package store

import (
	"context"
	"errors"
	"testing"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// The two terminal acts of the review gate, tested against a real database.
//
// These paths are worth integration tests rather than doubles because what can
// go wrong in them is SQL: a TEXT[] round trip, a CHECK constraint, and a
// conditional UPDATE used as a lock. None of those failures are visible from a
// fake store, and all three would surface for the first time on a manuscript
// being sent back to its author.

func rejectedDecision(taskID, comment string) segment.ReviewDecision {
	d, _ := segment.NewRejection(segment.ReviewTask{Reason: segment.ReasonZeroRoleMatch}, taskID, "shreya", comment)
	d.ID = uuid.NewString()
	return d
}

// TestSaveAuthorReturn_RoundTripAndFreeze is the whole path: reject, return,
// and find the run frozen afterwards.
func TestSaveAuthorReturn_RoundTripAndFreeze(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	d := rejectedDecision(taskID, "the heading is an OCR artifact; the section is unintelligible")
	if err := s.SaveDecision(ctx, &d); err != nil {
		t.Fatalf("SaveDecision (rejection): %v", err)
	}

	// The task must now read rejected, not resolved. This is the distinction the
	// whole gate rests on, and it is enforced by a CHECK that did not accept
	// 'rejected' before migration 0010.
	var status string
	if err := pool.QueryRow(ctx,
		`SELECT status FROM review_tasks WHERE review_task_id = $1`, taskID).Scan(&status); err != nil {
		t.Fatalf("read task status: %v", err)
	}
	if status != "rejected" {
		t.Errorf("task status = %q, want %q — a rejected task must not read as answered", status, "rejected")
	}

	items := []segment.AuthorReturnItem{{
		ReviewTaskID:     taskID,
		Reason:           segment.ReasonZeroRoleMatch,
		HeadingRaw:       "Zorblatt frobnication",
		AncestorHeadings: []string{"A Study Of Things"},
		Comment:          "the heading is an OCR artifact; the section is unintelligible",
	}}

	if err := s.SaveAuthorReturn(ctx, run.ID, uuid.NewString(), "shreya", items); err != nil {
		t.Fatalf("SaveAuthorReturn: %v", err)
	}

	// The TEXT[] round trip. Ancestors are what let an author FIND the section,
	// and an array that comes back empty would leave the report naming a heading
	// with no placement.
	var (
		heading  string
		ancestor []string
		comment  string
	)
	if err := pool.QueryRow(ctx, `
		SELECT i.heading_raw, i.ancestor_headings, i.human_review_comment
		  FROM author_return_items i
		  JOIN author_returns r ON r.author_return_id = i.author_return_id
		 WHERE r.segmentation_run_id = $1`, run.ID).Scan(&heading, &ancestor, &comment); err != nil {
		t.Fatalf("read author return item: %v", err)
	}
	if heading != "Zorblatt frobnication" {
		t.Errorf("heading = %q", heading)
	}
	if len(ancestor) != 1 || ancestor[0] != "A Study Of Things" {
		t.Errorf("ancestor_headings = %v, want the parent chain", ancestor)
	}
	if comment == "" {
		t.Error("comment came back empty; it is the sentence the author reads")
	}

	// And the run is frozen. Materializing the report IS the act of consuming
	// the decisions, so there is no window in which a report exists over
	// decisions that can still change.
	var consumedAt *string
	if err := pool.QueryRow(ctx,
		`SELECT decisions_consumed_at::text FROM segmentation_runs WHERE segmentation_run_id = $1`, run.ID).Scan(&consumedAt); err != nil {
		t.Fatalf("read consumption state: %v", err)
	}
	if consumedAt == nil {
		t.Fatal("run is not frozen after being returned; a correction could still change what the author was told")
	}
}

// TestSaveDecision_RefusedAfterConsumption.
//
// The freeze has to bite at the WRITE, not merely be recorded. A frozen run that
// still accepts decisions is a timestamp, not a rule.
func TestSaveDecision_RefusedAfterConsumption(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	if err := s.MarkConsumed(ctx, run.ID, "step4"); err != nil {
		t.Fatalf("MarkConsumed: %v", err)
	}

	d, err := segment.NewRoleDecision(
		segment.ReviewTask{Reason: segment.ReasonZeroRoleMatch},
		taskID, segment.RoleMethodology, "shreya", "",
	)
	if err != nil {
		t.Fatalf("NewRoleDecision: %v", err)
	}
	d.ID = uuid.NewString()

	err = s.SaveDecision(ctx, &d)
	if !errors.Is(err, ports.ErrDecisionsFrozen) {
		t.Fatalf("error = %v, want ErrDecisionsFrozen — a consumed run must not accept a late answer", err)
	}

	// Nothing was written. A rejected write that leaves a partial row behind is
	// worse than one that succeeds, because the run then disagrees with itself.
	var n int
	if err := pool.QueryRow(ctx,
		`SELECT count(*) FROM review_decisions WHERE review_task_id = $1`, taskID).Scan(&n); err != nil {
		t.Fatalf("count decisions: %v", err)
	}
	if n != 0 {
		t.Errorf("%d decisions written against a frozen run, want 0", n)
	}
}

// TestMarkConsumed_IsIdempotentAndKeepsTheFirstTimestamp.
//
// A consumer that legitimately re-reads a run must not be made to special-case
// the second read. But the FIRST timestamp is the one that matters: it is the
// moment the decisions stopped being editable, and refreshing it on every read
// would make a correction slipped between two reads look legitimate.
func TestMarkConsumed_IsIdempotentAndKeepsTheFirstTimestamp(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, _ := savedRunWithTask(t, s)

	if err := s.MarkConsumed(ctx, run.ID, "step4"); err != nil {
		t.Fatalf("MarkConsumed (first): %v", err)
	}

	var first string
	if err := pool.QueryRow(ctx,
		`SELECT decisions_consumed_at::text FROM segmentation_runs WHERE segmentation_run_id = $1`, run.ID).Scan(&first); err != nil {
		t.Fatalf("read first timestamp: %v", err)
	}

	if err := s.MarkConsumed(ctx, run.ID, "someone-else"); err != nil {
		t.Fatalf("MarkConsumed (second) returned an error; re-reading a run is not a fault: %v", err)
	}

	var second, by string
	if err := pool.QueryRow(ctx,
		`SELECT decisions_consumed_at::text, decisions_consumed_by
		   FROM segmentation_runs WHERE segmentation_run_id = $1`, run.ID).Scan(&second, &by); err != nil {
		t.Fatalf("read second timestamp: %v", err)
	}
	if second != first {
		t.Errorf("timestamp moved from %s to %s; the freeze happened once", first, second)
	}
	if by != "step4" {
		t.Errorf("consumed_by = %q, want %q — the first consumer is the one that froze it", by, "step4")
	}
}

// TestMarkConsumed_UnknownRun must say so rather than silently succeeding.
func TestMarkConsumed_UnknownRun(t *testing.T) {
	s := NewPostgresSegmentationStore(testPool(t))

	err := s.MarkConsumed(context.Background(), uuid.NewString(), "step4")
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ErrNotFound", err)
	}
}

// TestSaveAuthorReturn_OncePerRun.
//
// A report is a thing that was sent. A second one would leave two documents and
// nothing to say which the author received, so the UNIQUE constraint is load
// bearing and this checks the error is legible rather than a raw SQLSTATE.
func TestSaveAuthorReturn_OncePerRun(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	d := rejectedDecision(taskID, "unintelligible")
	if err := s.SaveDecision(ctx, &d); err != nil {
		t.Fatalf("SaveDecision: %v", err)
	}

	items := []segment.AuthorReturnItem{{
		ReviewTaskID: taskID,
		Reason:       segment.ReasonZeroRoleMatch,
		HeadingRaw:   "Zorblatt frobnication",
		Comment:      "unintelligible",
	}}

	if err := s.SaveAuthorReturn(ctx, run.ID, uuid.NewString(), "shreya", items); err != nil {
		t.Fatalf("SaveAuthorReturn (first): %v", err)
	}

	err := s.SaveAuthorReturn(ctx, run.ID, uuid.NewString(), "shreya", items)
	if !errors.Is(err, ports.ErrAlreadyReturned) {
		t.Errorf("error = %v, want ErrAlreadyReturned", err)
	}
}

// TestSaveAuthorReturn_TopLevelNodeHasNoAncestors.
//
// Regression. A nil AncestorHeadings reaches Postgres as NULL, and the column's
// DEFAULT '{}' does not apply to a value that was supplied — only to one
// omitted. The first version of this store passed the slice through and the
// insert failed on NOT NULL.
//
// This is the ordinary case rather than an edge one. A top-level node has no
// ancestors, which covers BOTH tasks a headless document raises: no_structure
// sits on the whole-document node and title_ambiguity has no node at all. So the
// paper most in need of going back to its author was the one that could not.
func TestSaveAuthorReturn_TopLevelNodeHasNoAncestors(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	d := rejectedDecision(taskID, "no usable structure anywhere in this document")
	if err := s.SaveDecision(ctx, &d); err != nil {
		t.Fatalf("SaveDecision: %v", err)
	}

	items := []segment.AuthorReturnItem{{
		ReviewTaskID: taskID,
		Reason:       segment.ReasonNoStructure,
		Comment:      "no usable structure anywhere in this document",
		// HeadingRaw and AncestorHeadings deliberately left at their zero
		// values, which is what BuildAuthorReturn produces for a node with no
		// parent.
	}}

	if err := s.SaveAuthorReturn(ctx, run.ID, uuid.NewString(), "shreya", items); err != nil {
		t.Fatalf("SaveAuthorReturn with no ancestors: %v", err)
	}

	var ancestor []string
	if err := pool.QueryRow(ctx, `
		SELECT i.ancestor_headings
		  FROM author_return_items i
		  JOIN author_returns r ON r.author_return_id = i.author_return_id
		 WHERE r.segmentation_run_id = $1`, run.ID).Scan(&ancestor); err != nil {
		t.Fatalf("read author return item: %v", err)
	}
	if ancestor == nil {
		t.Error("ancestor_headings came back NULL; it must be an empty array so a reader need not special-case it")
	}
	if len(ancestor) != 0 {
		t.Errorf("ancestor_headings = %v, want empty", ancestor)
	}
}

// TestSaveAuthorReturn_RefusesAnEmptyReport.
//
// The gate returns only when something was rejected, so zero items means the
// caller computed the state wrongly. Writing it anyway would send an author a
// message naming nothing at all.
func TestSaveAuthorReturn_RefusesAnEmptyReport(t *testing.T) {
	s := NewPostgresSegmentationStore(testPool(t))

	if err := s.SaveAuthorReturn(context.Background(), uuid.NewString(), uuid.NewString(), "shreya", nil); err == nil {
		t.Error("accepted an author return with no items")
	}
}

// TestSaveDecision_RejectionNeedsAComment at the store boundary, not only in the
// domain constructor. The constructor can be bypassed by an import script; this
// cannot.
func TestSaveDecision_RejectionNeedsAComment(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	_, taskID := savedRunWithTask(t, s)

	// Built by hand precisely because NewRejection refuses this.
	d := segment.ReviewDecision{
		ID:           uuid.NewString(),
		ReviewTaskID: taskID,
		Decision:     segment.DecisionReject,
		ReviewerID:   "shreya",
	}

	if err := s.SaveDecision(ctx, &d); err == nil {
		t.Error("stored a rejection with no comment; the author would be told nothing")
	}
}

// TestSaveDecision_RefusesADecisionWithNoVerb.
//
// Defaulting an empty verb to resolve would be convenient and wrong: a rejection
// that lost its verb between the constructor and the store would arrive as an
// empty resolve, the task would close as answered, and the run would pass
// instead of going back to its author.
func TestSaveDecision_RefusesADecisionWithNoVerb(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	_, taskID := savedRunWithTask(t, s)

	d := segment.ReviewDecision{
		ID:                   uuid.NewString(),
		ReviewTaskID:         taskID,
		AssignedRole:         segment.RoleMethodology,
		AssignedContentClass: segment.ClassAnalytical,
		ReviewerID:           "shreya",
	}

	if err := s.SaveDecision(ctx, &d); err == nil {
		t.Error("stored a decision with no verb; a lost rejection would read as an answer")
	}
}
