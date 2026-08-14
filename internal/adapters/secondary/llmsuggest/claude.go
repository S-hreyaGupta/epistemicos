// Package llmsuggest asks an LLM which role an unresolved section should have.
//
// # This is ADVISORY and sits OUTSIDE the pipeline
//
// Specification §13 defers every LLM mechanism from the MVP, with review volume
// named as the trigger for reconsidering. Nothing in this package is reachable
// from internal/core/domain/segment, from the segmentation service, or from any
// code path that writes to the database. It reads a completed run and prints
// suggestions.
//
// That separation is the whole point. Segmentation stays deterministic: the same
// markdown produces the same 28 sections and the same 9 questions, today and in
// a year, with no network call in the path. What this package adds is a way to
// answer those questions faster — a first draft for a human, not a decision.
//
// If the suggestions ever become good enough to trust unattended, that is a
// specification change to §6 and §13, made deliberately. It must not arrive by
// this package quietly gaining a write.
package llmsuggest

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// Suggestion is one proposed role for one unresolved section.
type Suggestion struct {
	Heading    string
	Role       string
	Confidence string // high | medium | low
	Reasoning  string
}

// Section is what the suggester needs to know about a node.
type Section struct {
	Heading   string
	Ancestors []string // outermost first
	Excerpt   string   // the opening of the section's own text
}

// Client asks Claude for role suggestions.
type Client struct {
	apiKey string
	http   *http.Client
}

// New returns a client. An empty key is a usable value: Suggest then returns a
// clear error rather than panicking, so a caller can report the missing
// credential rather than crash.
func New(apiKey string) *Client {
	return &Client{
		apiKey: apiKey,
		http:   &http.Client{Timeout: 90 * time.Second},
	}
}

const model = "claude-sonnet-4-5-20250929"

// prompt is deliberately explicit about three things, because each one has an
// obvious wrong answer the model would otherwise give.
//
// The ROLE LIST is closed. Without stating that, a model invents plausible
// roles — "hypotheses", "analysis", "background" — none of which exist in the
// taxonomy, and every one of which would then have to be mapped by hand.
//
// The ANCESTORS are supplied because they usually contain the answer. A heading
// like "2.1 ESG disclosure in supply chains" is uninterpretable alone and
// obvious beneath "2 Literature Review". Withholding them would make the model
// guess at exactly the thing a human reviewer would use.
//
// LOW CONFIDENCE MUST BE AVAILABLE. A suggester that is always confident is
// worse than none, because the reviewer stops reading. The instruction to say
// "low" when genuinely unsure is what keeps the confidence field informative.
const prompt = `You are helping classify sections of an academic paper.

The role must be exactly one of these sixteen, with no others invented:

abstract, introduction, literature_review, theory, methodology, results,
discussion, limitations, conclusion, acknowledgments, funding,
author_contributions, data_availability, ethics_statement,
conflict_of_interest, references

For each section below you are given its heading, the headings it sits beneath
(outermost first), and the opening of its text.

The parent headings are often decisive: "2.1 Sample and procedure" beneath
"2 Methodology" is methodology. Use them.

Reply with JSON only — an array, one object per section, in the same order:

[{"role": "...", "confidence": "high|medium|low", "reasoning": "one short sentence"}]

Say "low" when you are genuinely unsure. A suggestion that is always confident
is useless to the person reading it.

Sections:

%s`

type apiRequest struct {
	Model     string       `json:"model"`
	MaxTokens int          `json:"max_tokens"`
	Messages  []apiMessage `json:"messages"`
}

type apiMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type apiResponse struct {
	Content []struct {
		Text string `json:"text"`
	} `json:"content"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error"`
}

// Suggest asks for a role per section, in order.
//
// All sections go in ONE request rather than one each. That is not only cheaper:
// seeing the whole set lets the model be consistent across siblings, so 3.1
// through 3.4 do not come back as four different roles when they are plainly
// the same kind of section.
func (c *Client) Suggest(ctx context.Context, sections []Section) ([]Suggestion, error) {
	if c.apiKey == "" {
		return nil, fmt.Errorf("llmsuggest: no API key; set ANTHROPIC_API_KEY in .env")
	}
	if len(sections) == 0 {
		return nil, nil
	}

	var b strings.Builder
	for i, s := range sections {
		fmt.Fprintf(&b, "%d. Heading: %s\n", i+1, s.Heading)
		if len(s.Ancestors) > 0 {
			fmt.Fprintf(&b, "   Sits beneath: %s\n", strings.Join(s.Ancestors, " > "))
		}
		if s.Excerpt != "" {
			fmt.Fprintf(&b, "   Text begins: %s\n", s.Excerpt)
		}
		b.WriteString("\n")
	}

	body, err := json.Marshal(apiRequest{
		Model:     model,
		MaxTokens: 2048,
		Messages: []apiMessage{{
			Role:    "user",
			Content: fmt.Sprintf(prompt, b.String()),
		}},
	})
	if err != nil {
		return nil, fmt.Errorf("llmsuggest: encode request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost,
		"https://api.anthropic.com/v1/messages", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("llmsuggest: build request: %w", err)
	}
	req.Header.Set("content-type", "application/json")
	req.Header.Set("x-api-key", c.apiKey)
	req.Header.Set("anthropic-version", "2023-06-01")

	resp, err := c.http.Do(req)
	if err != nil {
		return nil, fmt.Errorf("llmsuggest: call: %w", err)
	}
	defer resp.Body.Close()

	var parsed apiResponse
	if err := json.NewDecoder(resp.Body).Decode(&parsed); err != nil {
		return nil, fmt.Errorf("llmsuggest: decode response: %w", err)
	}
	if parsed.Error != nil {
		return nil, fmt.Errorf("llmsuggest: api error: %s", parsed.Error.Message)
	}
	if len(parsed.Content) == 0 {
		return nil, fmt.Errorf("llmsuggest: empty response")
	}

	text := strings.TrimSpace(parsed.Content[0].Text)

	// Models sometimes wrap JSON in a fenced block despite being asked not to.
	// Trimming it is cheaper than a retry and does not hide a real failure: if
	// what remains is not JSON, the decode below still reports it.
	text = strings.TrimPrefix(text, "```json")
	text = strings.TrimPrefix(text, "```")
	text = strings.TrimSuffix(text, "```")
	text = strings.TrimSpace(text)

	var raw []struct {
		Role       string `json:"role"`
		Confidence string `json:"confidence"`
		Reasoning  string `json:"reasoning"`
	}
	if err := json.Unmarshal([]byte(text), &raw); err != nil {
		return nil, fmt.Errorf("llmsuggest: response was not the expected JSON: %w\n%s", err, text)
	}

	// A short reply would silently misalign every suggestion with the wrong
	// heading, which is worse than no reply at all.
	if len(raw) != len(sections) {
		return nil, fmt.Errorf("llmsuggest: asked about %d sections, got %d answers; suggestions would not line up", len(sections), len(raw))
	}

	out := make([]Suggestion, len(raw))
	for i := range raw {
		out[i] = Suggestion{
			Heading:    sections[i].Heading,
			Role:       raw[i].Role,
			Confidence: raw[i].Confidence,
			Reasoning:  raw[i].Reasoning,
		}
	}
	return out, nil
}
