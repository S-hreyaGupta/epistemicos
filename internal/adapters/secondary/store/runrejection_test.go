package store

import (
	"context"
	"errors"
	"testing"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// Run-level rejection against a real database.
//
// These were missing when the feature was committed, and the gap is the same
// one that produced this week's NULL ancestor_headings bug: the domain logic was
// tested with doubles, the SQL was not tested at all, and the failure was a
// constraint nobody had exercised.

// cleanRunFixture is a run that raises NO review tasks.
//
// It is the whole point of this feature. `decisionFixture` deliberately produces
// a task so a decision can be written against it; this one deliberately produces
// none, because a run with nothing to answer is exactly the run that was
// unchallengeable before run-level rejection existed.
func cleanRunFixture(t *testing.T) segment.Run {
	t.Helper()

	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## Methodology\n\nMethod prose.\n\n" +
		"## Results\n\nResults prose.\n")

	doc, err := segment.Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := segment.NewRun(doc, "test-paper", "0000000000000000000000000000000000000000000000000000000000000000")
	if len(run.Tasks) != 0 {
		t.Fatalf("fixture raised %d tasks, want 0 — this test needs a run with nothing to answer", len(run.Tasks))
	}

	run.ID = uuid.NewString()
	run.NodeIDs = make([]string, len(run.Nodes))
	for i := range run.Nodes {
		run.NodeIDs[i] = uuid.NewString()
	}
	return run
}

func savedCleanRun(t *testing.T, s *PostgresSegmentationStore) segment.Run {
	t.Helper()

	run := cleanRunFixture(t)
	cleanup(t, s.pool, run.ID)

	if err := s.SaveRun(context.Background(), &run); err != nil {
		t.Fatalf("SaveRun: %v", err)
	}
	return run
}

// TestSaveRunRejection_RoundTripAndSupersede.
func TestSaveRunRejection_RoundTripAndSupersede(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := savedCleanRun(t, s)

	// Before: nothing to object through, and the gate passes.
	if r, err := s.GetRunRejection(ctx, run.ID); err != nil || r != nil {
		t.Fatalf("GetRunRejection on a fresh run = %v, %v; want nil, nil", r, err)
	}

	const why = "the bibliography was identified as a discussion section"
	if err := s.SaveRunRejection(ctx, run.ID, "shreya", why); err != nil {
		t.Fatalf("SaveRunRejection: %v", err)
	}

	got, err := s.GetRunRejection(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetRunRejection: %v", err)
	}
	if got == nil {
		t.Fatal("no rejection came back")
	}
	if got.Comment != why {
		t.Errorf("comment = %q, want the reviewer's own words", got.Comment)
	}
	if got.ReviewerID != "shreya" {
		t.Errorf("reviewer = %q", got.ReviewerID)
	}

	// And the run is superseded, so anything holding its section map hash can
	// tell that what it built on is no longer accepted.
	var supersededAt *string
	if err := pool.QueryRow(ctx,
		`SELECT superseded_at::text FROM segmentation_runs WHERE segmentation_run_id = $1`, run.ID).Scan(&supersededAt); err != nil {
		t.Fatalf("read superseded_at: %v", err)
	}
	if supersededAt == nil {
		t.Error("superseded_at is null after a rejection; downstream artefacts have no way to know they are stale")
	}
}

// TestSaveRunRejection_AllowedAfterConsumption is the design decision, and the
// one most likely to be "corrected" by someone who has read migration 0010 and
// not this.
//
// 0010 freezes review DECISIONS once a run is consumed, so a late edit cannot
// retroactively change what Step 4 read. A run-level rejection is not an edit.
// It does not change what Step 4 read; it records that what Step 4 read was
// wrong.
//
// Refusing it here would make a run unchallengeable from the moment anything
// downstream touched it — which is precisely when a structural error becomes
// likely to be noticed.
func TestSaveRunRejection_AllowedAfterConsumption(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := savedCleanRun(t, s)

	if err := s.MarkConsumed(ctx, run.ID, "step4"); err != nil {
		t.Fatalf("MarkConsumed: %v", err)
	}

	if err := s.SaveRunRejection(ctx, run.ID, "shreya", "step 4 acted on a bad segmentation"); err != nil {
		t.Fatalf("SaveRunRejection on a consumed run: %v — passed must mean currently accepted, not permanently final", err)
	}

	// The freeze on DECISIONS is unaffected and is covered separately by
	// TestSaveDecision_RefusedAfterConsumption. It cannot be asserted here
	// because this run has no tasks, which is the very property that makes it
	// the right fixture for run-level rejection.
}

// TestSaveRunRejection_FirstObjectionStands.
//
// The comment is what the author received. A second rejection overwriting it
// would change a message already sent.
func TestSaveRunRejection_FirstObjectionStands(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := savedCleanRun(t, s)

	if err := s.SaveRunRejection(ctx, run.ID, "shreya", "first reason"); err != nil {
		t.Fatalf("SaveRunRejection (first): %v", err)
	}

	err := s.SaveRunRejection(ctx, run.ID, "alex", "second reason")
	if !errors.Is(err, ports.ErrAlreadyRejected) {
		t.Fatalf("error = %v, want ErrAlreadyRejected", err)
	}

	got, err := s.GetRunRejection(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetRunRejection: %v", err)
	}
	if got.Comment != "first reason" || got.ReviewerID != "shreya" {
		t.Errorf("got %+v; the first objection is the one the author was given", got)
	}
}

func TestSaveRunRejection_UnknownRun(t *testing.T) {
	s := NewPostgresSegmentationStore(testPool(t))

	err := s.SaveRunRejection(context.Background(), uuid.NewString(), "shreya", "why")
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ErrNotFound", err)
	}
}

// TestSaveRunRejection_RequiresReviewerAndComment at the store boundary. The
// service constructs these, but an import script can bypass the service and the
// database cannot be bypassed.
func TestSaveRunRejection_RequiresReviewerAndComment(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := savedCleanRun(t, s)

	if err := s.SaveRunRejection(ctx, run.ID, "shreya", "   "); err == nil {
		t.Error("accepted a rejection with a whitespace-only comment; the author would be told nothing")
	}
	if err := s.SaveRunRejection(ctx, run.ID, "", "a real reason"); err == nil {
		t.Error("accepted an anonymous rejection; an objection that returns a manuscript cannot be unattributable")
	}
}

// TestSaveAuthorReturn_RunLevelItemHasNoTask.
//
// Migration 0010 made author_return_items.review_task_id NOT NULL, which was
// right while every rejection came from a task. A run-level objection has none.
//
// This is the same shape as the NULL ancestor_headings bug earlier this week: a
// column constraint that only fires on a path the fixtures happened not to
// cover. The run-level path is not an edge case — it is the whole reason the
// feature exists.
func TestSaveAuthorReturn_RunLevelItemHasNoTask(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := savedCleanRun(t, s)

	const why = "no review task exists; the machine was confident and wrong"
	if err := s.SaveRunRejection(ctx, run.ID, "shreya", why); err != nil {
		t.Fatalf("SaveRunRejection: %v", err)
	}

	items := segment.BuildAuthorReturnWith(run, nil, &segment.RunRejection{
		Comment: why, ReviewerID: "shreya",
	})
	if len(items) != 1 {
		t.Fatalf("built %d items for a run-level rejection with no tasks, want 1", len(items))
	}
	if items[0].ReviewTaskID != "" {
		t.Errorf("run-level item carries task id %q, want empty", items[0].ReviewTaskID)
	}
	if items[0].Reason != segment.ReasonRunRejected {
		t.Errorf("reason = %q, want %q", items[0].Reason, segment.ReasonRunRejected)
	}

	if err := s.SaveAuthorReturn(ctx, run.ID, uuid.NewString(), "shreya", items); err != nil {
		t.Fatalf("SaveAuthorReturn with a task-less item: %v", err)
	}

	var taskID *string
	var comment string
	if err := pool.QueryRow(ctx, `
		SELECT i.review_task_id::text, i.human_review_comment
		  FROM author_return_items i
		  JOIN author_returns r ON r.author_return_id = i.author_return_id
		 WHERE r.segmentation_run_id = $1`, run.ID).Scan(&taskID, &comment); err != nil {
		t.Fatalf("read author return item: %v", err)
	}
	if taskID != nil {
		t.Errorf("review_task_id = %v, want NULL", *taskID)
	}
	if comment != why {
		t.Errorf("comment = %q, want the reviewer's words", comment)
	}
}

// TestBuildAuthorReturn_RunRejectionComesFirst.
//
// A run-level objection concerns the document as a whole and frames whatever
// follows. A reader who meets it after four heading complaints has already
// formed the wrong idea of what is wrong with their paper.
func TestBuildAuthorReturn_RunRejectionComesFirst(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	d := rejectedDecision(taskID, "this heading is an OCR artifact")
	if err := s.SaveDecision(ctx, &d); err != nil {
		t.Fatalf("SaveDecision: %v", err)
	}
	decisions, err := s.GetDecisions(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetDecisions: %v", err)
	}

	items := segment.BuildAuthorReturnWith(run, decisions, &segment.RunRejection{
		Comment: "the whole segmentation is wrong", ReviewerID: "shreya",
	})

	if len(items) < 2 {
		t.Fatalf("built %d items, want the run objection plus the task rejection", len(items))
	}
	if items[0].Reason != segment.ReasonRunRejected {
		t.Errorf("first item is %q; the run-level objection must lead", items[0].Reason)
	}
}
