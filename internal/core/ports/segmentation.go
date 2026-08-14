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
}
