package ports

import (
	"context"
	"errors"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
)

// ErrNotFound is returned by stores when a requested record doesn't
// exist. Callers should errors.Is against it rather than string-match.
var ErrNotFound = errors.New("not found")

// ErrDecisionsFrozen is returned when a review decision is written against a run
// that has already been consumed.
//
// A distinct error rather than a generic failure because the two responses are
// different: a caller seeing this should tell the reviewer that the run has moved
// on and their change needs a re-run, not offer a retry.
var ErrDecisionsFrozen = errors.New("review decisions are frozen: the run has been consumed")

// ErrAlreadyReturned is returned when a run already has an AuthorReturn.
//
// A report is a thing that was sent. Producing a second one for the same run
// would leave two documents and nothing to say which the author received.
var ErrAlreadyReturned = errors.New("this run has already been returned to the author")

// ErrAlreadyRejected is returned when a run already carries a run-level
// objection. The first one stands: its comment is what the author received, and
// replacing it would change a message already sent.
var ErrAlreadyRejected = errors.New("this run has already been rejected")

// PaperStore persists Paper aggregates.
//
// This is the only store this system defines.
type PaperStore interface {
	// Save inserts or updates a paper. Idempotent on ID.
	Save(ctx context.Context, p *paper.Paper) error

	// GetByID fetches a paper by its persistent ID.
	GetByID(ctx context.Context, id paper.ID) (*paper.Paper, error)

	// GetByHash fetches a paper by content hash. Used for dedupe on ingest.
	GetByHash(ctx context.Context, h paper.Hash) (*paper.Paper, error)

	// List returns papers in reverse-chronological order.
	List(ctx context.Context) ([]*paper.Paper, error)

	// UpdateStatus mutates only the status + error fields.
	UpdateStatus(ctx context.Context, id paper.ID, status paper.Status, errMsg string) error

	// UpdateMarkdown stores the Mathpix output and transitions status to ready.
	//
	// markdownHash is the hex-encoded SHA-256 of markdown, computed by the
	// ingest service. It is written in the same statement as the markdown so
	// the two cannot diverge: any consumer holding offsets into this text can
	// check them against the hash before trusting them.
	UpdateMarkdown(ctx context.Context, id paper.ID, title, markdown, markdownHash string) error
}
