package ports

import (
	"context"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/papertype"
)

// PaperTypeClassifier asks a language model to classify a manuscript.
//
// # Why the raw response comes back
//
// The adapter does not parse. It returns exactly what the model said, and
// internal/core/domain/papertype parses it. That split is deliberate: parsing,
// contract-checking and quote verification are deterministic, so they belong in
// the domain where they can be tested without a network and re-run years later
// against a stored response. If the adapter parsed, a stored response could never
// be re-examined by newer, stricter checks.
//
// The model name comes back for the same reason. It is not decoration: the same
// prompt on a different model is a different rule, and a verdict that cannot name
// the model that produced it cannot be compared with any other verdict.
type PaperTypeClassifier interface {
	// Classify sends the prompt and input, and returns the model's complete
	// response along with the model identifier that produced it.
	Classify(ctx context.Context, prompt, input string) (raw string, model string, err error)
}

// PaperTypeGate is the precondition Step 3 checks before it runs.
//
// # Why this is one method returning only an error
//
// Segmentation does not need to know what kind of paper it refused, only that it
// must not proceed. Handing it the whole verdict would invite it to make its own
// routing decision from the parts, and then two places would decide what
// "empirical" means.
//
// And why an ERROR rather than a bool: a bool is ignorable. A gate that can be
// dropped by accident is optional in practice while looking mandatory in the code,
// which is the failure this interface exists to prevent.
type PaperTypeGate interface {
	// Allow returns nil when the paper may proceed, and an error explaining why
	// not otherwise.
	Allow(ctx context.Context, paperID string) error
}

// PaperTypeStore persists verdicts.
//
// APPEND-ONLY. Re-classifying a paper writes a new verdict rather than replacing
// the old one, so a change of answer is visible as a change. This is the opposite
// of review_decisions, which corrects in place — and the difference is not
// inconsistency. There is exactly one authoritative human answer per question, and
// there are as many machine verdicts as times we asked.
type PaperTypeStore interface {
	// SaveVerdict appends a verdict for a paper.
	SaveVerdict(ctx context.Context, v *PaperTypeRecord) error

	// CurrentVerdict returns the newest verdict for a paper reached from the
	// given markdown hash, or ErrNotFound.
	//
	// Scoping by hash rather than by paper alone is what stops a re-ingested
	// paper inheriting a verdict reached from text that no longer exists.
	CurrentVerdict(ctx context.Context, paperID, markdownHash string) (*PaperTypeRecord, error)
}

// PaperTypeRecord is a verdict plus everything needed to interpret it later.
//
// It lives in ports rather than in the domain because half of it is provenance
// about a call the domain does not make. papertype.Verdict is the classification;
// this is the classification as stored.
type PaperTypeRecord struct {
	ID      string
	PaperID string

	// MarkdownHash ties the verdict to the exact text it was reached from.
	MarkdownHash string

	Verdict papertype.Verdict

	// QuotesExpected and QuotesVerified are the output of
	// papertype.VerifyQuotes. Unequal means the model paraphrased, and a verdict
	// resting on words that are not in the paper is not evidence.
	QuotesExpected int
	QuotesVerified int

	PromptVersion string
	Model         string
	InputForm     papertype.InputForm
	RawResponse   string
}
