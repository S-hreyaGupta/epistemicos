package ports

import (
	"context"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/researchunit"
)

// ResearchUnitStore persists the multi-study gate's verdicts.
//
// # Why this port looks unlike PaperTypeStore
//
// PaperTypeStore is APPEND-ONLY, because that gate asks a language model and the
// same question can get a different answer next month. Every verdict is a
// separate event and a change of answer must be visible as a change.
//
// This gate is deterministic. The same markdown under the same rule version
// always produces the same verdict, so a second run is not a second opinion —
// it is the same computation repeated. Storing it twice would record a change
// that did not happen.
//
// So this store is IDEMPOTENT rather than append-only, keyed on
// (paper, markdown hash, rule version). A rules change produces a new row
// because the version differs; a re-run under unchanged rules produces the same
// row. Both properties come free from the gate being a computation rather than a
// judgement, and the schema is where that difference is made explicit.
type ResearchUnitStore interface {
	// SaveGate writes a verdict and its evidence in one transaction.
	//
	// Atomicity matters here for the same reason it does for a run: a verdict
	// stored without its evidence is a conclusion with no visible basis, and the
	// whole reason this is persisted at all is so a reviewer can see what the
	// machine saw.
	//
	// Re-saving an identical (paper, hash, rule version) REPLACES the evidence
	// rather than appending to it. The verdict is a pure function of those three
	// things, so the second write can only be the same evidence; replacing keeps
	// that true even if the gate's evidence ordering later changes.
	SaveGate(ctx context.Context, paperID, markdownHash string, gate researchunit.Gate) error

	// CurrentGate returns the verdict for a paper reached from the given
	// markdown under the given rule version, or ErrNotFound.
	//
	// All three are required. Scoping by paper alone would let a re-ingested
	// paper inherit a verdict reached from text that no longer exists, and
	// scoping without the rule version would serve an answer computed by rules
	// that are no longer in force — which for a deterministic gate is the one
	// mistake that makes a stored answer worse than no answer.
	CurrentGate(ctx context.Context, paperID, markdownHash, ruleVersion string) (*researchunit.Gate, error)
}
