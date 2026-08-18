// Package papertype answers one question before Step 3 runs: is this paper
// empirical at all?
//
// # Why this is a gate and not a label
//
// Everything downstream assumes an empirical paper. Step 3's role table is built
// from the sections empirical papers have — methodology, results, discussion — and
// the methodology classifier counts a glossary of empirical method terms. Feed
// either a systematic review and both answer confidently and wrongly: a review of
// quantitative studies is saturated with quantitative vocabulary, because that
// vocabulary belongs to the corpus it reviews rather than to the paper itself.
//
// So a non-empirical paper is not a paper we classify badly. It is a paper we
// must refuse, and refusing is the feature.
//
// # What is deterministic here and what is not
//
// The classification comes from a language model, so it is NOT deterministic and
// this package does not pretend otherwise. What lives here is everything around
// that call which CAN be deterministic:
//
//   - the prompt, versioned as source rather than configuration
//   - parsing the response against its own output contract
//   - verifying every quote is genuinely in the manuscript
//   - the routing rule
//
// The model call itself is a port, satisfied by an adapter. That keeps this
// package free of network, and it means the parsing and verification of a stored
// response can be re-run years later without one.
//
// # Why quote verification is not optional
//
// The prompt tells the model its quotes are machine-verified. Until something
// verifies them that sentence is a promise rather than a control, and a model that
// paraphrases is indistinguishable from one that does not. Verification is what
// converts "the model said B" into "the model said B and here are the words in the
// paper that say so".
package papertype

import (
	"encoding/json"
	"fmt"
	"strings"
	"unicode"
)

// Type is the paper's primary knowledge-generation method.
type Type string

const (
	// TypeEmpirical is the only type that proceeds. The paper's own evidence
	// comes from observations of the world.
	TypeEmpirical Type = "A"

	// TypeSynthesis: a systematic aggregation of prior studies under a protocol.
	TypeSynthesis Type = "B"

	// TypeConceptual: definitions, frameworks and theory built by argumentation.
	TypeConceptual Type = "C"

	// TypeFormal: claims carried by derivation, theorems and proofs.
	TypeFormal Type = "D"

	// TypeUnclassified is a refusal, and a legitimate answer. The prompt is
	// explicit that a wrong "A" is costly and an honest refusal is cheap, so this
	// value must never be treated as a failure to be retried into an answer.
	TypeUnclassified Type = "UNCLASSIFIED"
)

// Subtype is the finer division required for B and D and absent elsewhere.
type Subtype string

const (
	SubtypeSystematicReview Subtype = "systematic_review"
	SubtypeMetaAnalysis     Subtype = "meta_analysis"
	SubtypeModelling        Subtype = "mathematical_modelling"
	SubtypeProof            Subtype = "mathematical_proof"
)

// InputForm records whether the model saw the whole document or a selection.
//
// Stored because it changes how much a verdict is worth. A "C" reached from a
// complete heading list plus an abstract is a weaker claim than one reached from
// the full text, and a reader who cannot tell them apart cannot weigh either.
type InputForm string

const (
	FormFull      InputForm = "FULL"
	FormSelection InputForm = "SELECTION"
)

// Evidence is one verbatim quote and what the model took it to show.
type Evidence struct {
	Quote   string `json:"quote"`
	Signals string `json:"signals"`

	// Verified is set by VerifyQuotes, not by the model. A quote the model
	// invented arrives here false, and the verdict is not trustworthy.
	Verified bool `json:"-"`
}

// CounterEvidence is the strongest quote AGAINST the verdict.
//
// Required by the prompt and kept because it is the cheapest calibration
// available: a model forced to state the best case against itself is much harder
// to read as confident when it is not.
type CounterEvidence struct {
	Quote    string `json:"quote"`
	PointsTo Type   `json:"points_to"`
	Verified bool   `json:"-"`
}

// Verdict is one parsed, contract-checked classification.
type Verdict struct {
	PrimaryType   Type    `json:"primary_type"`
	Subtype       Subtype `json:"subtype"`
	SecondaryType Type    `json:"secondary_type"`
	DecisionRule  int     `json:"decision_rule"`
	Confidence    string  `json:"confidence"`

	Evidence        []Evidence       `json:"evidence"`
	CounterEvidence *CounterEvidence `json:"counter_evidence"`

	BoundaryCase        string `json:"boundary_case"`
	LimitsFromSelection string `json:"limits_from_selection"`
	Rationale           string `json:"rationale"`
	UnclassifiedReason  string `json:"unclassified_reason"`
}

// Empirical reports whether this paper proceeds into Step 3.
//
// A synthesis paper carrying its own substantial empirical study is typed B with
// a secondary of A, and it proceeds. The prompt says so and this is the code that
// makes it true: without reading the secondary, a paper with real data of its own
// would be parked for having also reviewed the literature systematically.
func (v Verdict) Empirical() bool {
	return v.PrimaryType == TypeEmpirical || v.SecondaryType == TypeEmpirical
}

// AllQuotesVerified reports whether every quote was found in the manuscript.
//
// Call VerifyQuotes first. Before that this returns false for any verdict, which
// is the safe direction: an unverified verdict must never read as a verified one.
func (v Verdict) AllQuotesVerified() bool {
	if len(v.Evidence) == 0 {
		return false
	}
	for _, e := range v.Evidence {
		if !e.Verified {
			return false
		}
	}
	if v.CounterEvidence != nil && !v.CounterEvidence.Verified {
		return false
	}
	return true
}

// Reason renders why a paper was refused, for a person to read.
func (v Verdict) Reason() string {
	switch v.PrimaryType {
	case TypeEmpirical:
		return "empirical"
	case TypeSynthesis:
		s := "evidence synthesis of prior studies rather than the paper's own data"
		if v.Subtype != "" {
			s = string(v.Subtype) + ": " + s
		}
		return s
	case TypeConceptual:
		return "conceptual or theoretical: builds concepts by argumentation, with no data of its own"
	case TypeFormal:
		s := "formal or mathematical: claims carried by derivation rather than observation"
		if v.Subtype != "" {
			s = string(v.Subtype) + ": " + s
		}
		return s
	case TypeUnclassified:
		if v.UnclassifiedReason != "" {
			return "unclassified: " + v.UnclassifiedReason
		}
		return "unclassified"
	}
	return "unrecognised type " + string(v.PrimaryType)
}

// ContractError says a response did not satisfy its own output contract.
//
// Nothing in this package retries one. A response that breaks its contract is
// evidence about the model or the prompt, and quietly asking again would hide the
// one signal that says the prompt needs work.
type ContractError struct {
	Problem string
	Raw     string
}

func (e *ContractError) Error() string {
	return fmt.Sprintf("papertype: response breaks the output contract: %s", e.Problem)
}

// Parse extracts and validates a verdict from a raw model response.
//
// The response carries the answer TWICE by design: once as primary_type inside
// the JSON and once in a trailing <verdict> tag. Parse requires them to agree.
// That redundancy is the cheapest possible check on a truncated or garbled
// response — a reply cut off mid-JSON has no verdict tag at all, and one whose tag
// disagrees with its own JSON was not produced by a model following the contract,
// whatever else it says.
func Parse(raw string) (Verdict, error) {
	answer, err := between(raw, "<answer>", "</answer>")
	if err != nil {
		return Verdict{}, &ContractError{Problem: "no <answer> block", Raw: raw}
	}

	tag, err := between(raw, "<verdict>", "</verdict>")
	if err != nil {
		return Verdict{}, &ContractError{Problem: "no <verdict> block; the response may have been truncated", Raw: raw}
	}

	// Fenced JSON despite instructions not to. Trimming is cheaper than a retry
	// and hides nothing: if what remains is not JSON the decode still says so.
	answer = strings.TrimSpace(answer)
	answer = strings.TrimPrefix(answer, "```json")
	answer = strings.TrimPrefix(answer, "```")
	answer = strings.TrimSuffix(answer, "```")
	answer = strings.TrimSpace(answer)

	var v Verdict
	if err := json.Unmarshal([]byte(answer), &v); err != nil {
		return Verdict{}, &ContractError{Problem: fmt.Sprintf("the <answer> block is not valid JSON: %v", err), Raw: raw}
	}

	if got := Type(strings.TrimSpace(tag)); got != v.PrimaryType {
		return Verdict{}, &ContractError{
			Problem: fmt.Sprintf("<verdict> says %q but primary_type says %q", got, v.PrimaryType),
			Raw:     raw,
		}
	}

	if err := v.validate(); err != nil {
		return Verdict{}, &ContractError{Problem: err.Error(), Raw: raw}
	}

	return v, nil
}

func (v Verdict) validate() error {
	switch v.PrimaryType {
	case TypeEmpirical, TypeSynthesis, TypeConceptual, TypeFormal, TypeUnclassified:
	default:
		return fmt.Errorf("primary_type %q is not one of A, B, C, D, UNCLASSIFIED", v.PrimaryType)
	}

	if v.DecisionRule < 1 || v.DecisionRule > 5 {
		return fmt.Errorf("decision_rule is %d, want 1 to 5", v.DecisionRule)
	}

	switch v.Confidence {
	case "high", "medium", "low":
	default:
		return fmt.Errorf("confidence %q is not high, medium or low", v.Confidence)
	}

	// A subtype is required exactly where the taxonomy divides, and forbidden
	// elsewhere. "B with no subtype" leaves a meta-analysis and a narrative
	// systematic review indistinguishable; "A with a subtype" means the model
	// invented a division the downstream system does not have.
	needsSubtype := v.PrimaryType == TypeSynthesis || v.PrimaryType == TypeFormal
	switch {
	case needsSubtype && v.Subtype == "":
		return fmt.Errorf("primary_type %s requires a subtype", v.PrimaryType)
	case !needsSubtype && v.Subtype != "":
		return fmt.Errorf("primary_type %s must not carry a subtype, got %q", v.PrimaryType, v.Subtype)
	}
	if v.Subtype != "" {
		switch v.Subtype {
		case SubtypeSystematicReview, SubtypeMetaAnalysis:
			if v.PrimaryType != TypeSynthesis {
				return fmt.Errorf("subtype %q belongs to B, not %s", v.Subtype, v.PrimaryType)
			}
		case SubtypeModelling, SubtypeProof:
			if v.PrimaryType != TypeFormal {
				return fmt.Errorf("subtype %q belongs to D, not %s", v.Subtype, v.PrimaryType)
			}
		default:
			return fmt.Errorf("subtype %q is not in the contract", v.Subtype)
		}
	}

	if v.SecondaryType != "" {
		switch v.SecondaryType {
		case TypeEmpirical, TypeSynthesis, TypeConceptual, TypeFormal:
		default:
			return fmt.Errorf("secondary_type %q is not one of A, B, C, D", v.SecondaryType)
		}
		// A secondary equal to the primary is how a model hedges without saying
		// so, and it would make Empirical() read "A" twice as though a second
		// contribution existed.
		if v.SecondaryType == v.PrimaryType {
			return fmt.Errorf("secondary_type equals primary_type (%s); a secondary must be a different contribution", v.PrimaryType)
		}
	}

	// UNCLASSIFIED is a real answer and must say why. Without the reason it is
	// indistinguishable from a model that gave up, and the whole point of making
	// refusal cheap is that a refusal teaches us something.
	if v.PrimaryType == TypeUnclassified && strings.TrimSpace(v.UnclassifiedReason) == "" {
		return fmt.Errorf("UNCLASSIFIED without an unclassified_reason")
	}
	if v.PrimaryType != TypeUnclassified && strings.TrimSpace(v.UnclassifiedReason) != "" {
		return fmt.Errorf("unclassified_reason set on a %s verdict", v.PrimaryType)
	}

	if n := len(v.Evidence); n < 2 || n > 4 {
		return fmt.Errorf("evidence holds %d items, want 2 to 4", n)
	}
	for i, e := range v.Evidence {
		if strings.TrimSpace(e.Quote) == "" {
			return fmt.Errorf("evidence %d has an empty quote", i)
		}
		if n := len(strings.Fields(e.Quote)); n > 25 {
			return fmt.Errorf("evidence %d quote is %d words, over the 25-word limit", i, n)
		}
	}

	if v.CounterEvidence != nil {
		if strings.TrimSpace(v.CounterEvidence.Quote) == "" {
			return fmt.Errorf("counter_evidence has an empty quote; use null instead")
		}
		switch v.CounterEvidence.PointsTo {
		case TypeEmpirical, TypeSynthesis, TypeConceptual, TypeFormal:
		default:
			return fmt.Errorf("counter_evidence points_to %q is not one of A, B, C, D", v.CounterEvidence.PointsTo)
		}
	}

	return nil
}

// VerifyQuotes checks every quote against the manuscript and records the result
// on the verdict. It returns how many evidence quotes were found.
//
// # Why not strings.Contains on the raw text
//
// The manuscript is machine-converted from PDF, and a model asked to copy
// verbatim will still normalise typography: a curly apostrophe becomes straight,
// an em dash becomes a hyphen, a line break inside a sentence becomes a space.
// Every one of those is a faithful quote that a byte comparison rejects.
//
// This exact mismatch already cost us a silent bug elsewhere in this repository.
// One glossary term contained a typographic apostrophe; the counting normalised it
// and the attribution did not, and an unambiguous signal counted toward nothing
// for days with fifteen tests passing. Normalising ONE side is the bug. Normalising
// both is the fix.
//
// Case and word content are deliberately NOT folded. A quote that differs in a
// word is a paraphrase, and catching paraphrase is the entire purpose.
func VerifyQuotes(markdown string, v *Verdict) int {
	haystack := normaliseForQuote(markdown)

	verified := 0
	for i := range v.Evidence {
		if quoteFound(haystack, v.Evidence[i].Quote) {
			v.Evidence[i].Verified = true
			verified++
		}
	}
	if v.CounterEvidence != nil {
		v.CounterEvidence.Verified = quoteFound(haystack, v.CounterEvidence.Quote)
	}
	return verified
}

func quoteFound(normalisedHaystack, quote string) bool {
	q := normaliseForQuote(quote)
	if q == "" {
		return false
	}
	return strings.Contains(normalisedHaystack, q)
}

// normaliseForQuote folds the typographic differences a faithful quote may still
// carry, and nothing else.
//
// The cases are written as \u escapes rather than literal glyphs on purpose.
// Several are visually identical in an editor — U+2010 through U+2015 all look
// like a dash — and a duplicated case is a compile error that reads as a mystery.
// Whitespace is handled by unicode.IsSpace below rather than enumerated here,
// which covers NBSP and the en and em spaces without listing them.
func normaliseForQuote(s string) string {
	var b strings.Builder
	b.Grow(len(s))

	space := false
	for _, r := range s {
		switch r {
		case '\u2018', '\u2019', '\u02bc', '\u00b4', '`':
			r = '\''
		case '\u201c', '\u201d', '\u201e':
			r = '"'
		case '\u2010', '\u2011', '\u2012', '\u2013', '\u2014', '\u2015', '\u2212':
			r = '-'
		case '\u200b', '\u200c', '\u200d', '\ufeff':
			continue // zero-width; never part of a quote
		case '\u2026':
			// An ellipsis is how a model elides. Expanding it lets a quote that
			// used three literal dots match the same span.
			b.WriteString("...")
			space = false
			continue
		}

		if unicode.IsSpace(r) {
			if !space {
				b.WriteRune(' ')
				space = true
			}
			continue
		}
		space = false
		b.WriteRune(r)
	}

	return strings.TrimSpace(b.String())
}

func between(s, openTag, closeTag string) (string, error) {
	i := strings.Index(s, openTag)
	if i < 0 {
		return "", fmt.Errorf("missing %s", openTag)
	}
	rest := s[i+len(openTag):]
	j := strings.Index(rest, closeTag)
	if j < 0 {
		return "", fmt.Errorf("missing %s", closeTag)
	}
	return rest[:j], nil
}
