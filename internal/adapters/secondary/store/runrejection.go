package store

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// Run-level rejection: the one route for objecting to a determination the
// machine made confidently.

// SaveRunRejection records an objection to a run as a whole and supersedes it.
//
// # Why this does not check the consumption freeze
//
// Migration 0010 freezes review DECISIONS once a run is consumed, so a late edit
// cannot retroactively change what Step 4 already read. That rule is untouched
// here and this is not an exception to it.
//
// A run-level rejection does not edit what Step 4 read. It records that what
// Step 4 read was wrong. History is preserved and superseded rather than
// rewritten — which is the only reading under which `passed` can mean "currently
// accepted" without also meaning "permanently final". Refusing a rejection on a
// consumed run would make every clean run unchallengeable the moment anything
// downstream touched it, which is precisely when discovering a structural error
// becomes likely.
func (s *PostgresSegmentationStore) SaveRunRejection(ctx context.Context, runID, reviewerID, comment string) error {
	if runID == "" {
		return errors.New("store: run rejection needs a run id")
	}
	if strings.TrimSpace(reviewerID) == "" {
		return errors.New("store: a run rejection needs a reviewer; an anonymous objection that returns a manuscript cannot be audited")
	}
	if strings.TrimSpace(comment) == "" {
		return errors.New("store: a run rejection needs a comment; it is the sentence the author reads")
	}

	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return fmt.Errorf("begin: %w", err)
	}
	defer func() { _ = tx.Rollback(ctx) }()

	var exists bool
	if err := tx.QueryRow(ctx,
		`SELECT true FROM segmentation_runs WHERE segmentation_run_id = $1`, runID).Scan(&exists); err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return ports.ErrNotFound
		}
		return fmt.Errorf("check run %s: %w", runID, err)
	}

	tag, err := tx.Exec(ctx, `
		INSERT INTO run_rejections (run_rejection_id, segmentation_run_id, human_review_comment, reviewer_id)
		VALUES ($1,$2,$3,$4)
		ON CONFLICT (segmentation_run_id) DO NOTHING`,
		uuid.NewString(), runID, strings.TrimSpace(comment), strings.TrimSpace(reviewerID))
	if err != nil {
		return fmt.Errorf("insert run rejection for %s: %w", runID, err)
	}
	if tag.RowsAffected() == 0 {
		// Already rejected. Not an error to be told twice, but the FIRST
		// objection stands: it is the one whose comment the author received, and
		// overwriting it would change a message already sent.
		return ports.ErrAlreadyRejected
	}

	if _, err := tx.Exec(ctx, `
		UPDATE segmentation_runs SET superseded_at = NOW()
		 WHERE segmentation_run_id = $1 AND superseded_at IS NULL`, runID); err != nil {
		return fmt.Errorf("supersede run %s: %w", runID, err)
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("commit: %w", err)
	}
	return nil
}

// GetRunRejection returns the objection against a run, or nil.
//
// nil rather than ErrNotFound: no rejection is the ordinary state of a run, and
// making the common case an error would have every caller unwrapping one.
func (s *PostgresSegmentationStore) GetRunRejection(ctx context.Context, runID string) (*segment.RunRejection, error) {
	var r segment.RunRejection

	err := s.pool.QueryRow(ctx, `
		SELECT human_review_comment, reviewer_id
		  FROM run_rejections
		 WHERE segmentation_run_id = $1`, runID).Scan(&r.Comment, &r.ReviewerID)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, nil
		}
		return nil, fmt.Errorf("select run rejection: %w", err)
	}
	return &r, nil
}
