// Package papertype orchestrates the classification gate that runs before
// Step 3.
//
// The orchestration is thin, as segmentation's is. Every rule lives in
// internal/core/domain/papertype: the prompt, the response contract, the quote
// verification and the routing decision. This package supplies the model call, the
// identifiers and the persistence.
package papertype

import (
	"context"
	"errors"
	"fmt"

	"github.com/google/uuid"

	domain "github.com/EpistemicOS/epistemicos/internal/core/domain/papertype"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// ErrNotEmpirical is returned when a paper is classified out of scope.
//
// A distinct error rather than a boolean, because every caller must handle it and
// a boolean is ignorable. Step 3 refusing to run is the entire point of this
// service, and a return value that could be dropped by accident would make the
// gate optional in practice while looking mandatory in the code.
var ErrNotEmpirical = errors.New("paper is not empirical and is out of scope")

// ErrUnverifiedQuotes is returned when the model's quotes are not in the paper.
//
// Separate from ErrNotEmpirical because it says something different: not "this
// paper is the wrong kind" but "this answer is not evidence". A verdict resting on
// words that are not in the manuscript should not route anything, whichever way it
// points.
var ErrUnverifiedQuotes = errors.New("the model quoted text that is not in the manuscript")

// Service classifies papers and gates Step 3.
type Service struct {
	source     ports.ApprovedMarkdownSource
	classifier ports.PaperTypeClassifier
	store      ports.PaperTypeStore
}

// New returns a Service.
func New(source ports.ApprovedMarkdownSource, classifier ports.PaperTypeClassifier, store ports.PaperTypeStore) *Service {
	return &Service{source: source, classifier: classifier, store: store}
}

// This Service is what Step 3 holds as its gate. Asserting it here means a change
// to either side breaks in one of the two files that define the relationship,
// rather than in the command that happens to wire them together.
var _ ports.PaperTypeGate = (*Service)(nil)

// Result is one classification, freshly made or read back.
type Result struct {
	Record *ports.PaperTypeRecord

	// Cached says the verdict was read from storage rather than newly asked for.
	// Surfaced so a caller can tell "the model answered B" from "we already knew
	// B" — the second costs nothing and the first costs a call.
	Cached bool
}

// Classify asks the model about a paper and stores the verdict.
//
// It does NOT return an error for a non-empirical paper. Classifying is a
// question; refusing is a routing decision, and they are separate methods so that
// asking about a conceptual paper on purpose is not an error condition. Gate is
// where the refusal lives.
func (s *Service) Classify(ctx context.Context, paperID string) (*Result, error) {
	markdown, hash, err := s.source.Get(ctx, paperID)
	if err != nil {
		return nil, fmt.Errorf("classify: fetch approved markdown for %s: %w", paperID, err)
	}

	// FULL for now. BuildInput and the prompt both handle SELECTION, and the
	// intent is to switch once we are sending only the headings plus the abstract
	// and methods — which needs the heading scan to run first. The prompt's
	// selection rules are in place so that switch is a change of two arguments
	// rather than a change of rules.
	input, err := domain.BuildInput(domain.FormFull, nil, markdown)
	if err != nil {
		return nil, fmt.Errorf("classify: %w", err)
	}

	raw, model, err := s.classifier.Classify(ctx, domain.Prompt(), input)
	if err != nil {
		return nil, fmt.Errorf("classify: %w", err)
	}

	verdict, err := domain.Parse(raw)
	if err != nil {
		// The raw response is attached because a contract failure is a fact about
		// the prompt, and diagnosing it without seeing what came back is guesswork.
		return nil, fmt.Errorf("classify: %w\n\n--- raw response ---\n%s", err, raw)
	}

	expected := len(verdict.Evidence)
	if verdict.CounterEvidence != nil {
		expected++
	}
	verified := domain.VerifyQuotes(markdown, &verdict)
	if verdict.CounterEvidence != nil && verdict.CounterEvidence.Verified {
		verified++
	}

	record := &ports.PaperTypeRecord{
		ID:             uuid.NewString(),
		PaperID:        paperID,
		MarkdownHash:   hash,
		Verdict:        verdict,
		QuotesExpected: expected,
		QuotesVerified: verified,
		PromptVersion:  domain.PromptVersion,
		Model:          model,
		InputForm:      domain.FormFull,
		RawResponse:    raw,
	}

	// Stored BEFORE the quote check rejects anything. A verdict whose quotes do
	// not check out is exactly the verdict worth keeping: it is the evidence that
	// the prompt or the model needs work, and discarding it would leave us
	// arguing from memory about how often this happens.
	if err := s.store.SaveVerdict(ctx, record); err != nil {
		return nil, fmt.Errorf("classify: persist verdict: %w", err)
	}

	return &Result{Record: record}, nil
}

// Verdict returns the stored verdict for a paper, classifying it if there is none.
//
// The cache is keyed on the markdown hash, so a re-ingested paper is re-classified
// rather than inheriting an answer reached from text that no longer exists.
func (s *Service) Verdict(ctx context.Context, paperID string) (*Result, error) {
	_, hash, err := s.source.Get(ctx, paperID)
	if err != nil {
		return nil, fmt.Errorf("verdict: fetch approved markdown for %s: %w", paperID, err)
	}

	record, err := s.store.CurrentVerdict(ctx, paperID, hash)
	switch {
	case err == nil:
		return &Result{Record: record, Cached: true}, nil
	case errors.Is(err, ports.ErrNotFound):
		return s.Classify(ctx, paperID)
	default:
		return nil, fmt.Errorf("verdict: %w", err)
	}
}

// Gate is the routing decision, and the method Step 3 calls.
//
// It returns ErrNotEmpirical for a paper out of scope and ErrUnverifiedQuotes for
// a verdict that is not evidence. Both errors carry the reason in their text, so a
// person reading the failure learns what the paper was taken to be rather than
// only that it was rejected.
//
// A refusal is not a failure of this system. It is this system working.
func (s *Service) Gate(ctx context.Context, paperID string) (*Result, error) {
	result, err := s.Verdict(ctx, paperID)
	if err != nil {
		return nil, err
	}

	v := result.Record.Verdict

	// Checked before the type, deliberately. An unverified verdict should not
	// route a paper EITHER way: letting an unverified "A" through would use an
	// answer we have just shown to be unsupported, simply because we liked it.
	if result.Record.QuotesVerified != result.Record.QuotesExpected {
		return result, fmt.Errorf("%w: %d of %d quotes were not found in the paper (verdict %s, prompt %s, model %s)",
			ErrUnverifiedQuotes,
			result.Record.QuotesExpected-result.Record.QuotesVerified,
			result.Record.QuotesExpected,
			v.PrimaryType, result.Record.PromptVersion, result.Record.Model)
	}

	if !v.Empirical() {
		return result, fmt.Errorf("%w: classified %s — %s", ErrNotEmpirical, v.PrimaryType, v.Reason())
	}

	return result, nil
}

// Allow satisfies ports.PaperTypeGate: nil to proceed, an explanatory error to
// stop.
//
// It exists so segmentation can depend on a one-method interface rather than on
// this package. Handing Step 3 the whole verdict would invite it to decide for
// itself what counts as empirical, and then two places would define it.
func (s *Service) Allow(ctx context.Context, paperID string) error {
	_, err := s.Gate(ctx, paperID)
	return err
}
