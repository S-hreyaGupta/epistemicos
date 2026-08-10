package ports

import (
	"context"
	"errors"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
)

// ErrNotFound is returned by stores when a requested record doesn't
// exist. Callers should errors.Is against it rather than string-match.
var ErrNotFound = errors.New("not found")

// PaperStore persists Paper aggregates.
//
// This is the only store this system defines. The analysis-side stores
// (slots, flags, editor notes) belonged to the archetype pipeline and are
// deliberately absent — see the README on what this repository is and is not.
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
