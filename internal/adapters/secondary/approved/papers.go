// Package approved adapts this repository's papers table to the input
// specification Step 3 expects.
package approved

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// PapersSource satisfies ports.ApprovedMarkdownSource from the papers table.
//
// STEP 2 HAS NO APPROVAL GATE. papers.status = 'ready' means Mathpix finished
// converting the PDF. It does not mean a human approved the extraction — there
// has never been an Approved value anywhere in this codebase. This adapter maps
// 'ready' onto the specification's Approved as a deliberate, temporary
// simplification, permitted by v2.1 §12 G5. When ExtractionRun exists, this
// mapping is REPLACED rather than extended.
//
// The consequence, recorded rather than implied: until a real approval gate
// exists upstream, "approved" means "conversion completed", and no human has
// reviewed extraction quality. Every segmentation produced through this adapter
// inherits that. It is visible here, in one commented line somebody wrote on
// purpose, precisely so that it cannot become an assumption nobody remembers
// making.
//
// The runRef this accepts is a paper id, not an ExtractionRun id. §9's pointer
// chain cannot be advanced because ExtractionRun.current_segmentation_run_id
// does not exist; see the TODO below.
type PapersSource struct {
	pool *pgxpool.Pool
}

// NewPapersSource returns a source backed by the given pool.
func NewPapersSource(pool *pgxpool.Pool) *PapersSource {
	return &PapersSource{pool: pool}
}

// Get returns the markdown and hash for a paper id.
//
// The hash is VERIFIED against the markdown before returning, not merely read
// alongside it. papers.markdown and papers.markdown_hash are written in one
// statement so they cannot normally diverge, but "cannot normally" is not a
// property Step 3 can rely on: every byte offset it produces indexes into this
// exact text, and markdown that does not match its hash yields spans that slice
// the wrong bytes and read as plausible quotations rather than as errors.
//
// Recomputing costs one SHA-256 over a document that has just been read from
// the network anyway. The failure it prevents is a confidently wrong quote of
// somebody's paper.
func (s *PapersSource) Get(ctx context.Context, runRef string) (string, string, error) {
	var markdown, storedHash, status string

	err := s.pool.QueryRow(ctx, `
		SELECT markdown, markdown_hash, status
		  FROM papers
		 WHERE id = $1`, runRef,
	).Scan(&markdown, &storedHash, &status)

	if errors.Is(err, pgx.ErrNoRows) {
		return "", "", ports.ErrNotFound
	}
	if err != nil {
		return "", "", fmt.Errorf("approved: select paper %s: %w", runRef, err)
	}

	// The substitution for §2's `status = Approved` precondition. Stated as a
	// check rather than left implicit, so a paper still converting cannot be
	// segmented by accident.
	if status != "ready" {
		return "", "", fmt.Errorf("approved: paper %s has status %q, want \"ready\" (this repository's stand-in for the specification's Approved; see the type comment)", runRef, status)
	}

	if markdown == "" {
		return "", "", fmt.Errorf("approved: paper %s has status \"ready\" but no markdown", runRef)
	}

	sum := sha256.Sum256([]byte(markdown))
	computed := hex.EncodeToString(sum[:])
	if storedHash != "" && computed != storedHash {
		return "", "", fmt.Errorf("approved: paper %s has markdown_hash %s but its markdown hashes to %s; offsets derived from this text would be unverifiable", runRef, storedHash, computed)
	}

	// TODO(step9-pointer): §9 advances
	// ExtractionRun.current_segmentation_run_id after a successful run. That
	// column does not exist in this repository, so the advancement is recorded
	// here as a deferred obligation rather than silently skipped. Do not create
	// the column as part of Step 3 — it belongs to Step 2's schema.

	return markdown, computed, nil
}
