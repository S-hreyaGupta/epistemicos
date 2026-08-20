package store

import (
	"context"
	"errors"
	"testing"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// decisionFixture is deliberately NOT fixtureRun.
//
// fixtureRun's unresolvable node is "### Structural model" beneath "##
// Methodology", which since 2.2 inherits methodology from its parent and
// resolves. That fixture now produces ZERO review tasks, which the round-trip
// test above does not notice because it compares counts rather than requiring
// one — and a decision test built on it would skip its own subject.
//
// Here the nonsense heading is an H2, so its parent is the document title, which
// has no role to give. It stays a zero_role_match.
func decisionFixture(t *testing.T) segment.Run {
	t.Helper()

	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## Methodology\n\nMethod prose.\n\n" +
		"## Zorblatt frobnication\n\nMore prose.\n")

	doc, err := segment.Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := segment.NewRun(doc, "test-paper", "0000000000000000000000000000000000000000000000000000000000000000")
	run.ID = uuid.NewString()
	run.NodeIDs = make([]string, len(run.Nodes))
	for i := range run.Nodes {
		run.NodeIDs[i] = uuid.NewString()
	}
	run.TaskIDs = make([]string, len(run.Tasks))
	for i := range run.Tasks {
		run.TaskIDs[i] = uuid.NewString()
	}

	return run
}

// savedRunWithTask persists the fixture and returns it with the id of a task a
// role decision may be written against.
func savedRunWithTask(t *testing.T, s *PostgresSegmentationStore) (segment.Run, string) {
	t.Helper()

	run := decisionFixture(t)
	cleanup(t, s.pool, run.ID)

	if err := s.SaveRun(context.Background(), &run); err != nil {
		t.Fatalf("SaveRun: %v", err)
	}

	for i, task := range run.Tasks {
		if task.Reason != segment.ReasonTitleAmbiguity {
			return run, run.TaskIDs[i]
		}
	}
	t.Fatal("the fixture produced no role task; this test needs one")
	return run, ""
}

// TestSaveAndGetDecision is the round trip. Until this passed, Step 3 could ask
// sixty-five questions about one manuscript and store no answers at all.
func TestSaveAndGetDecision(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	decision, err := segment.NewRoleDecision(
		segment.ReviewTask{Reason: segment.ReasonZeroRoleMatch},
		taskID, segment.RoleMethodology, "shreya", "the sample is described here",
	)
	if err != nil {
		t.Fatalf("NewRoleDecision: %v", err)
	}
	decision.ID = uuid.NewString()

	if err := s.SaveDecision(ctx, &decision); err != nil {
		t.Fatalf("SaveDecision: %v", err)
	}

	got, err := s.GetDecisions(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetDecisions: %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("got %d decisions, want 1", len(got))
	}

	d := got[taskID]
	if d == nil {
		t.Fatalf("no decision keyed by task %s; keys are %v", taskID, keysOf(got))
	}
	if d.ID != decision.ID {
		t.Errorf("id = %q, want %q", d.ID, decision.ID)
	}
	if d.AssignedRole != segment.RoleMethodology {
		t.Errorf("role = %q, want %q", d.AssignedRole, segment.RoleMethodology)
	}
	if d.AssignedContentClass != segment.ClassAnalytical {
		t.Errorf("class = %q, want %q", d.AssignedContentClass, segment.ClassAnalytical)
	}
	if d.ReviewerID != "shreya" {
		t.Errorf("reviewer = %q, want %q", d.ReviewerID, "shreya")
	}
	if d.Comment != "the sample is described here" {
		t.Errorf("comment = %q", d.Comment)
	}
}

// TestSaveDecision_ResolvesItsTask. A decision stored against a task still marked
// open is a question that has been answered and will be asked again.
func TestSaveDecision_ResolvesItsTask(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	decision := segment.ReviewDecision{
		ID:                   uuid.NewString(),
		ReviewTaskID:         taskID,
		Decision:             segment.DecisionResolve,
		AssignedRole:         segment.RoleResults,
		AssignedContentClass: segment.ClassAnalytical,
		ReviewerID:           "shreya",
	}
	if err := s.SaveDecision(ctx, &decision); err != nil {
		t.Fatalf("SaveDecision: %v", err)
	}

	reread, err := s.GetRun(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetRun: %v", err)
	}

	for i, id := range reread.TaskIDs {
		if id != taskID {
			continue
		}
		if reread.Tasks[i].Status != segment.TaskResolved {
			t.Errorf("task status = %q, want %q", reread.Tasks[i].Status, segment.TaskResolved)
		}
		return
	}
	t.Fatalf("task %s vanished from the run", taskID)
}

// TestSaveDecision_CorrectionUpdatesInPlace.
//
// A reviewer changing their mind is ordinary, and 0005's UNIQUE means a plain
// insert would fail on it. The row must be updated, and it must KEEP ITS
// IDENTITY: the second call's id is discarded and the original returned, so a
// caller is never left holding an id for a row that does not exist.
func TestSaveDecision_CorrectionUpdatesInPlace(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, taskID := savedRunWithTask(t, s)

	first := segment.ReviewDecision{
		ID:                   uuid.NewString(),
		ReviewTaskID:         taskID,
		Decision:             segment.DecisionResolve,
		AssignedRole:         segment.RoleResults,
		AssignedContentClass: segment.ClassAnalytical,
		ReviewerID:           "shreya",
		Comment:              "first thought",
	}
	if err := s.SaveDecision(ctx, &first); err != nil {
		t.Fatalf("SaveDecision (first): %v", err)
	}
	originalID := first.ID

	second := segment.ReviewDecision{
		ID:                   uuid.NewString(),
		ReviewTaskID:         taskID,
		Decision:             segment.DecisionResolve,
		AssignedRole:         segment.RoleDiscussion,
		AssignedContentClass: segment.ClassAnalytical,
		ReviewerID:           "alex",
		Comment:              "on reflection, discussion",
	}
	if err := s.SaveDecision(ctx, &second); err != nil {
		t.Fatalf("SaveDecision (correction): %v", err)
	}

	if second.ID != originalID {
		t.Errorf("correction reported id %q, want the original %q", second.ID, originalID)
	}

	got, err := s.GetDecisions(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetDecisions: %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("got %d decisions after a correction, want 1", len(got))
	}

	d := got[taskID]
	if d.AssignedRole != segment.RoleDiscussion {
		t.Errorf("role = %q, want %q", d.AssignedRole, segment.RoleDiscussion)
	}
	if d.ReviewerID != "alex" {
		t.Errorf("reviewer = %q, want %q", d.ReviewerID, "alex")
	}
	if d.Comment != "on reflection, discussion" {
		t.Errorf("comment = %q, want the corrected one", d.Comment)
	}
	if d.ID != originalID {
		t.Errorf("stored id = %q, want %q", d.ID, originalID)
	}
}

// TestSaveDecision_UnknownTask must not create anything.
func TestSaveDecision_UnknownTask(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	decision := segment.ReviewDecision{
		ID:                   uuid.NewString(),
		ReviewTaskID:         uuid.NewString(),
		Decision:             segment.DecisionResolve,
		AssignedRole:         segment.RoleResults,
		AssignedContentClass: segment.ClassAnalytical,
		ReviewerID:           "shreya",
	}

	err := s.SaveDecision(ctx, &decision)
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ports.ErrNotFound", err)
	}
}

// TestGetDecisions_NoneYet returns an empty map rather than an error. A run
// nobody has reviewed is the ordinary case, not a failure.
func TestGetDecisions_NoneYet(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run, _ := savedRunWithTask(t, s)

	got, err := s.GetDecisions(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetDecisions: %v", err)
	}
	if len(got) != 0 {
		t.Errorf("got %d decisions on an unreviewed run, want 0", len(got))
	}
}

// TestGetDecisions_ScopedToTheRun. The join runs through review_tasks, and a
// decision on another paper's task must not leak into this run's overlay.
func TestGetDecisions_ScopedToTheRun(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	runA, taskA := savedRunWithTask(t, s)
	runB, _ := savedRunWithTask(t, s)

	decision := segment.ReviewDecision{
		ID:                   uuid.NewString(),
		ReviewTaskID:         taskA,
		Decision:             segment.DecisionResolve,
		AssignedRole:         segment.RoleResults,
		AssignedContentClass: segment.ClassAnalytical,
		ReviewerID:           "shreya",
	}
	if err := s.SaveDecision(ctx, &decision); err != nil {
		t.Fatalf("SaveDecision: %v", err)
	}

	inB, err := s.GetDecisions(ctx, runB.ID)
	if err != nil {
		t.Fatalf("GetDecisions(B): %v", err)
	}
	if len(inB) != 0 {
		t.Errorf("run B sees %d of run A's decisions", len(inB))
	}

	inA, err := s.GetDecisions(ctx, runA.ID)
	if err != nil {
		t.Fatalf("GetDecisions(A): %v", err)
	}
	if len(inA) != 1 {
		t.Errorf("run A sees %d decisions, want 1", len(inA))
	}
}

func keysOf(m map[string]*segment.ReviewDecision) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
