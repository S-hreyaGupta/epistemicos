package store

import (
	"context"
	"errors"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// The two terminal acts of the review gate, and the only two things that freeze
// a run's decisions.
//
// Both live here rather than in segmentation.go because they share one rule that
// is easy to lose sight of: consuming a run and recording WHY it was consumed
// are the same transaction. A run frozen with no record of what froze it is a
// run nobody can explain later.

// SaveAuthorReturn materializes the report for a returned run and freezes it.
//
// Order inside the transaction is deliberate. The freeze goes FIRST and is
// conditional on the run not already being frozen, so two concurrent callers
// cannot both proceed to write items: the second finds zero rows affected and
// stops before it has written anything.
func (s *PostgresSegmentationStore) SaveAuthorReturn(ctx context.Context, runID, returnID, consumedBy string, items []segment.AuthorReturnItem) error {
	if runID == "" || returnID == "" {
		return errors.New("store: author return needs a run id and a return id")
	}
	if len(items) == 0 {
		// A returned run has at least one rejection by definition. Zero items
		// means the caller computed the gate wrongly, and writing an empty
		// report would send an author a message naming nothing.
		return errors.New("store: an author return with no items is not a return; the gate returns only when something was rejected")
	}
	for i, it := range items {
		if it.Comment == "" {
			return fmt.Errorf("store: author return item %d has no comment; it is the sentence the author reads", i)
		}
	}

	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return fmt.Errorf("begin: %w", err)
	}
	defer func() { _ = tx.Rollback(ctx) }()

	tag, err := tx.Exec(ctx, `
		UPDATE segmentation_runs
		   SET decisions_consumed_at = NOW(),
		       decisions_consumed_by = $2
		 WHERE segmentation_run_id = $1
		   AND decisions_consumed_at IS NULL`, runID, nullIfEmpty(consumedBy))
	if err != nil {
		return fmt.Errorf("freeze run %s: %w", runID, err)
	}
	if tag.RowsAffected() == 0 {
		// Either the run does not exist or it is already frozen. Told apart by
		// a second read, because reporting "not found" for a run that is simply
		// already returned would send someone looking for the wrong problem.
		var exists bool
		if err := tx.QueryRow(ctx,
			`SELECT true FROM segmentation_runs WHERE segmentation_run_id = $1`, runID).Scan(&exists); err != nil {
			if errors.Is(err, pgx.ErrNoRows) {
				return ports.ErrNotFound
			}
			return fmt.Errorf("check run %s: %w", runID, err)
		}
		return ports.ErrAlreadyReturned
	}

	if _, err := tx.Exec(ctx, `
		INSERT INTO author_returns (author_return_id, segmentation_run_id)
		VALUES ($1, $2)`, returnID, runID); err != nil {
		return fmt.Errorf("insert author return for run %s: %w", runID, err)
	}

	for i, it := range items {
		// A nil slice reaches Postgres as NULL, and the column's DEFAULT '{}'
		// does not apply to a value that was supplied — only to one omitted. So
		// nil must become an empty array here or the insert violates NOT NULL.
		//
		// Nil is the ORDINARY case, not a rare one. A top-level node has no
		// ancestors, which covers both of the tasks a headless document raises:
		// no_structure sits on the whole-document node, and title_ambiguity has
		// no node at all. Returning such a paper to its author is precisely the
		// path this would have broken.
		ancestors := it.AncestorHeadings
		if ancestors == nil {
			ancestors = []string{}
		}

		if _, err := tx.Exec(ctx, `
			INSERT INTO author_return_items (
				author_return_item_id, author_return_id, review_task_id,
				review_reason, heading_raw, ancestor_headings, human_review_comment
			) VALUES ($1,$2,$3,$4,$5,$6,$7)`,
			// nullIfEmpty on the task id: a run-level objection belongs to no
			// task, and "" would fail the foreign key rather than record the
			// absence.
			uuid.NewString(), returnID, nullIfEmpty(it.ReviewTaskID),
			string(it.Reason), it.HeadingRaw, ancestors, it.Comment,
		); err != nil {
			return fmt.Errorf("insert author return item %d (task %s): %w", i, it.ReviewTaskID, err)
		}
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("commit: %w", err)
	}
	return nil
}

// MarkConsumed freezes a run's decisions without producing a report.
//
// This is what Step 4 does on a passed run. Idempotent by the WHERE clause: a
// second call affects zero rows and returns nil, keeping the FIRST timestamp,
// which is the moment the decisions actually stopped being editable. Overwriting
// it on every read would make the freeze look later than it was and would let a
// correction slipped in between two reads appear legitimate.
func (s *PostgresSegmentationStore) MarkConsumed(ctx context.Context, runID, consumedBy string) error {
	if runID == "" {
		return errors.New("store: mark consumed needs a run id")
	}

	tag, err := s.pool.Exec(ctx, `
		UPDATE segmentation_runs
		   SET decisions_consumed_at = NOW(),
		       decisions_consumed_by = $2
		 WHERE segmentation_run_id = $1
		   AND decisions_consumed_at IS NULL`, runID, nullIfEmpty(consumedBy))
	if err != nil {
		return fmt.Errorf("mark run %s consumed: %w", runID, err)
	}
	if tag.RowsAffected() > 0 {
		return nil
	}

	// Zero rows means already consumed, or no such run. Only the second is an
	// error.
	var exists bool
	if err := s.pool.QueryRow(ctx,
		`SELECT true FROM segmentation_runs WHERE segmentation_run_id = $1`, runID).Scan(&exists); err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return ports.ErrNotFound
		}
		return fmt.Errorf("check run %s: %w", runID, err)
	}
	return nil
}
