package ports

import (
	"context"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
)

// ApprovedMarkdownSource supplies the input Step 3 segments.
//
// This interface is the whole of the fork ruling. Specification §2 reads from
// an ExtractionRun with status = Approved, and §9 walks a three-level pointer
// chain through Manuscript and ManuscriptVersion. None of those entities exist
// in this repository: there is a flat papers table and no approval workflow.
//
// Rather than fork the specification or bend Step 3 around entities that are
// not there, Step 3 declares the three things it actually consumes — the
// markdown, its hash, and a reference identifying the run — and takes them
// through this port. An adapter satisfies it from papers today; a different
// adapter satisfies it from ExtractionRun when that exists, and nothing in the
// domain changes. Swapping them is one line in the composition root.
//
// The alternative considered and rejected was to read papers directly from the
// service. Under that arrangement someone maps status = ready onto the
// specification's Approved because it is convenient, and the review gate
// disappears without anyone deciding to remove it. Behind this port the mapping
// is one visible, commented line that somebody wrote on purpose.
type ApprovedMarkdownSource interface {
	// Get returns the approved markdown and its hex-encoded SHA-256 for the
	// given run reference.
	//
	// Implementations MUST return ErrNotFound when the reference is unknown,
	// and MUST NOT return markdown whose hash they have not verified. Every
	// byte offset Step 3 produces indexes into this exact text; supplying
	// markdown that does not match the hash yields spans that slice the wrong
	// bytes and read as plausible quotations rather than as errors.
	Get(ctx context.Context, runRef string) (markdown string, markdownHash string, err error)
}

// SegmentationStore persists the four entities of §8.
type SegmentationStore interface {
	// SaveRun writes a run and all of its nodes and review tasks in a single
	// transaction.
	//
	// Atomicity is required rather than convenient. A partially written run is
	// indistinguishable from a document that genuinely has fewer sections, and
	// §10's zero-silent-loss invariant — checked in the domain before this is
	// ever called — would be defeated by a store that could persist half a node
	// set and report success.
	SaveRun(ctx context.Context, run *segment.Run) error

	// GetRun fetches a run with its nodes and tasks, ordered by ordinal.
	// Returns ErrNotFound if the run does not exist.
	GetRun(ctx context.Context, runID string) (*segment.Run, error)

	// SaveDecision writes the single authoritative human decision for one review
	// task and closes that task, in one transaction.
	//
	// The task's new status MIRRORS the decision — resolved for a resolve,
	// rejected for a reject. Collapsing both onto resolved would make a finished
	// review that failed look identical to one that succeeded, which is exactly
	// what the run gate has to tell apart.
	//
	// Implementations MUST refuse with ErrDecisionsFrozen when the run has been
	// consumed, and MUST make that check inside the same transaction as the
	// write. A run consumed between a check and a write is the one case a
	// separate read cannot cover.
	//
	// A correction UPDATES the existing decision in place rather than appending,
	// which is the one deliberate exception to the pipeline's append-only
	// discipline: there is never more than one competing human resolution per
	// task, and 0005 enforces that with UNIQUE(review_task_id). Implementations
	// MUST set decision.ID to the id of the row actually stored, which on a
	// correction is the ORIGINAL id and not the one supplied — otherwise a caller
	// holds an identifier for a row that does not exist.
	//
	// The task update belongs in the same transaction as the decision. A decision
	// stored against a task still marked open is a question that has been
	// answered and will be asked again; a task marked resolved with no decision is
	// an answer that has been lost. Both are worse than failing.
	//
	// Returns ErrNotFound if the task does not exist.
	SaveDecision(ctx context.Context, decision *segment.ReviewDecision) error

	// GetDecisions returns every decision recorded against a run's tasks, keyed
	// by review task id. An absent key means no human has answered that task.
	//
	// Keyed rather than ordered because that is how the overlay consumes it: one
	// lookup per node, no scan. Returns an empty map, not an error, for a run
	// nobody has reviewed.
	GetDecisions(ctx context.Context, runID string) (map[string]*segment.ReviewDecision, error)

	// SaveAuthorReturn materializes the report for a returned run and freezes the
	// run's decisions in the same transaction.
	//
	// One per run, enforced by a UNIQUE constraint rather than by the caller
	// checking first: two reports for one decision set would leave nothing to say
	// which was sent. A second attempt returns ErrAlreadyReturned.
	//
	// The items are a SNAPSHOT of the rejections. Storing them rather than
	// joining at render time is what makes the sent report and the stored report
	// the same document, even after a later correction or a re-segmentation.
	//
	// Freezing here is not a side effect: materializing the report IS the act of
	// consuming the decisions, and separating the two would leave a window in
	// which a report had been produced from decisions that could still change.
	SaveAuthorReturn(ctx context.Context, runID, returnID, consumedBy string, items []segment.AuthorReturnItem) error

	// MarkConsumed freezes a run's decisions without producing a report, which is
	// what Step 4 does when it reads a passed run.
	//
	// Idempotent: consuming an already-consumed run is not an error, because a
	// consumer that legitimately re-reads a run must not be made to special-case
	// the second read. The FIRST consumption timestamp is kept — it is the moment
	// the decisions actually stopped being editable.
	MarkConsumed(ctx context.Context, runID, consumedBy string) error
}
