package segmentation

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// In-memory doubles. These exist so the guard that matters — the markdown a
// reviewer is shown is the markdown the offsets were computed against — can be
// tested without Postgres. It is the one property in this file that fails
// silently in production: wrong offsets return plausible prose from the wrong
// part of the paper rather than an error.

type fakeSource struct {
	markdown string
	err      error
}

func (f *fakeSource) Get(_ context.Context, _ string) (string, string, error) {
	if f.err != nil {
		return "", "", f.err
	}
	sum := sha256.Sum256([]byte(f.markdown))
	return f.markdown, hex.EncodeToString(sum[:]), nil
}

type fakeStore struct {
	run       *segment.Run
	decisions map[string]*segment.ReviewDecision
	saved     []segment.ReviewDecision
	saveErr   error

	// consumedBy and returned record the two terminal acts, so a test can assert
	// that Consume and ReturnToAuthor actually froze the run rather than merely
	// reporting that they had.
	consumedBy string
	consumed   bool
	returned   []segment.AuthorReturnItem
	returnErr  error
}

func (f *fakeStore) SaveRun(_ context.Context, run *segment.Run) error {
	f.run = run
	return nil
}

func (f *fakeStore) GetRun(_ context.Context, runID string) (*segment.Run, error) {
	if f.run == nil || f.run.ID != runID {
		return nil, ports.ErrNotFound
	}
	return f.run, nil
}

func (f *fakeStore) SaveDecision(_ context.Context, d *segment.ReviewDecision) error {
	if f.saveErr != nil {
		return f.saveErr
	}
	f.saved = append(f.saved, *d)
	if f.decisions == nil {
		f.decisions = map[string]*segment.ReviewDecision{}
	}
	f.decisions[d.ReviewTaskID] = d
	return nil
}

func (f *fakeStore) GetDecisions(_ context.Context, _ string) (map[string]*segment.ReviewDecision, error) {
	if f.decisions == nil {
		return map[string]*segment.ReviewDecision{}, nil
	}
	return f.decisions, nil
}

func (f *fakeStore) SaveAuthorReturn(_ context.Context, _, _, consumedBy string, items []segment.AuthorReturnItem) error {
	if f.returnErr != nil {
		return f.returnErr
	}
	f.returned = items
	f.consumed = true
	f.consumedBy = consumedBy
	return nil
}

func (f *fakeStore) MarkConsumed(_ context.Context, _, consumedBy string) error {
	// Idempotent, matching the real store: the FIRST consumption is the one that
	// counts, because that is the moment the decisions stopped being editable.
	if f.consumed {
		return nil
	}
	f.consumed = true
	f.consumedBy = consumedBy
	return nil
}

// fakeGate stands in for the paper-type classifier. Review and Resolve never
// consult it — a run that already exists is reviewable whatever the paper turned
// out to be — so it exists here only to satisfy the constructor.
type fakeGate struct{ err error }

func (g *fakeGate) Allow(context.Context, string) error { return g.err }

// Compile-time proof the doubles are the real thing, so a port change breaks
// here rather than drifting.
var (
	_ ports.ApprovedMarkdownSource = (*fakeSource)(nil)
	_ ports.SegmentationStore      = (*fakeStore)(nil)
	_ ports.PaperTypeGate          = (*fakeGate)(nil)
)

// A document with an unresolvable section, so there is a question to answer.
//
// The nonsense heading is an H2 and not an H3, and that is load-bearing. As an
// H3 beneath "## Methodology" it would inherit methodology under 2.2 and resolve,
// leaving this file with nothing to review. As an H2 its parent is the document
// title, which has no role to give (§4), so it stays a zero_role_match — which
// is exactly the shape of question a reviewer exists to answer.
const reviewMarkdown = "# A Study Of Things\n\nAuthors.\n\n" +
	"## Methodology\n\nWe sampled two hundred firms.\n\n" +
	"## Zorblatt frobnication\n\nThe frobnication proceeded as described.\n"

func harness(t *testing.T, markdown string) (*Service, *fakeStore, *segment.Run) {
	t.Helper()

	doc, err := segment.Build([]byte(markdown))
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	sum := sha256.Sum256([]byte(markdown))
	run := segment.NewRun(doc, "paper-1", hex.EncodeToString(sum[:]))

	run.ID = "run-1"
	run.NodeIDs = make([]string, len(run.Nodes))
	for i := range run.Nodes {
		run.NodeIDs[i] = fmt.Sprintf("node-%d", i)
	}
	run.TaskIDs = make([]string, len(run.Tasks))
	for i := range run.Tasks {
		run.TaskIDs[i] = fmt.Sprintf("task-%d", i)
	}

	if len(run.Tasks) == 0 {
		t.Fatal("the fixture produced no review tasks; these tests need one")
	}

	store := &fakeStore{run: &run}
	return New(&fakeSource{markdown: markdown}, store, &fakeGate{}), store, &run
}

func TestReview(t *testing.T) {
	svc, _, want := harness(t, reviewMarkdown)

	run, items, err := svc.Review(context.Background(), "run-1")
	if err != nil {
		t.Fatalf("Review: %v", err)
	}

	if run.ID != "run-1" {
		t.Errorf("run id = %q", run.ID)
	}
	if len(items) != len(want.Tasks) {
		t.Fatalf("got %d items, want %d", len(items), len(want.Tasks))
	}

	it := items[0]
	if it.TaskID == "" {
		t.Error("item has no task id; nothing could be resolved against it")
	}
	if it.Decision != nil {
		t.Errorf("unreviewed task carries a decision: %+v", it.Decision)
	}
	if len(it.AssignableRoles) == 0 {
		t.Error("no assignable roles offered; a reviewer would have nothing to choose from")
	}

	// The context text is the whole point. A parent node owns only the bytes
	// before its first child, so the node's own span alone can be almost empty.
	if !strings.Contains(it.Text, "frobnication") {
		t.Errorf("context text does not contain the section's prose: %q", it.Text)
	}
}

// TestReview_RefusesWhenTheMarkdownChanged is the guard that justifies this
// service existing rather than the CLI slicing offsets itself.
//
// Every offset in a run indexes into one exact text. Against different bytes the
// spans do not fail — they return real prose from the wrong part of the paper,
// and a reviewer answers a question about a section they were never shown.
func TestReview_RefusesWhenTheMarkdownChanged(t *testing.T) {
	svc, _, _ := harness(t, reviewMarkdown)

	// Same service, but the source now holds a different document.
	svc.source = &fakeSource{markdown: reviewMarkdown + "\n## An Appended Section\n\nMore prose.\n"}

	_, _, err := svc.Review(context.Background(), "run-1")
	if err == nil {
		t.Fatal("Review accepted markdown that no longer matches the run's hash")
	}
	if !strings.Contains(err.Error(), "slice the wrong bytes") {
		t.Errorf("error = %q, want it to explain the offset problem", err)
	}
}

func TestReview_UnknownRun(t *testing.T) {
	svc, _, _ := harness(t, reviewMarkdown)

	_, _, err := svc.Review(context.Background(), "no-such-run")
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ports.ErrNotFound", err)
	}
}

func TestResolve(t *testing.T) {
	svc, store, run := harness(t, reviewMarkdown)

	taskID := roleTaskID(t, run)

	got, err := svc.Resolve(context.Background(), "run-1", taskID, segment.RoleMethodology, "shreya", "a subsection of methodology")
	if err != nil {
		t.Fatalf("Resolve: %v", err)
	}

	if got.ID == "" {
		t.Error("decision has no id; the service assigns identity")
	}
	if got.AssignedRole != segment.RoleMethodology {
		t.Errorf("role = %q", got.AssignedRole)
	}
	if got.AssignedContentClass != segment.ClassAnalytical {
		t.Errorf("class = %q, want it derived from the role", got.AssignedContentClass)
	}
	if len(store.saved) != 1 {
		t.Fatalf("store received %d decisions, want 1", len(store.saved))
	}
	if store.saved[0].ReviewTaskID != taskID {
		t.Errorf("saved against task %q, want %q", store.saved[0].ReviewTaskID, taskID)
	}
}

// TestResolve_RejectsBadRoleWithoutTouchingTheStore. A malformed decision must
// not reach persistence: once stored it outranks the machine's answer and no
// re-run corrects it.
func TestResolve_RejectsBadRoleWithoutTouchingTheStore(t *testing.T) {
	svc, store, run := harness(t, reviewMarkdown)

	_, err := svc.Resolve(context.Background(), "run-1", roleTaskID(t, run), segment.Role("methodolgy"), "shreya", "")
	if err == nil {
		t.Fatal("accepted a misspelled role")
	}
	if !errors.Is(err, segment.ErrDecisionInvalid) {
		t.Errorf("error does not wrap segment.ErrDecisionInvalid: %v", err)
	}
	if len(store.saved) != 0 {
		t.Errorf("store received %d decisions after a rejection", len(store.saved))
	}
}

func TestResolve_RejectsAnonymousReviewer(t *testing.T) {
	svc, store, run := harness(t, reviewMarkdown)

	_, err := svc.Resolve(context.Background(), "run-1", roleTaskID(t, run), segment.RoleResults, "  ", "")
	if err == nil {
		t.Fatal("accepted a decision with no reviewer")
	}
	if len(store.saved) != 0 {
		t.Error("store received an anonymous decision")
	}
}

// TestResolve_RejectsATaskFromAnotherRun. A task id alone would let a mistyped
// id answer a question about a different paper, and the overlay would then serve
// that as a human-confirmed fact about a document nobody looked at.
func TestResolve_RejectsATaskFromAnotherRun(t *testing.T) {
	svc, store, _ := harness(t, reviewMarkdown)

	_, err := svc.Resolve(context.Background(), "run-1", "task-from-somewhere-else", segment.RoleResults, "shreya", "")
	if err == nil {
		t.Fatal("resolved a task that is not part of the run")
	}
	if !strings.Contains(err.Error(), "no review task") {
		t.Errorf("error = %q", err)
	}
	if len(store.saved) != 0 {
		t.Error("store received a decision for a foreign task")
	}
}

// TestResolveTitle_RejectsAForeignNode. The schema's foreign key catches a
// nonexistent node; it happily accepts a real node belonging to another paper.
func TestResolveTitle_RejectsAForeignNode(t *testing.T) {
	// A document with no H1 raises a title_ambiguity task.
	md := "## A systematic review on regenerative supply chains\n\n" +
		"#### Abstract\n\nAbstract prose.\n\n" +
		"## 1 Introduction\n\nOpening prose.\n"

	svc, store, run := harness(t, md)

	taskID := ""
	for i, task := range run.Tasks {
		if task.Reason == segment.ReasonTitleAmbiguity {
			taskID = run.TaskIDs[i]
		}
	}
	if taskID == "" {
		t.Fatal("this test needs a title_ambiguity task")
	}

	_, err := svc.ResolveTitle(context.Background(), "run-1", taskID, "A Study", "node-from-another-paper", "alex", "")
	if err == nil {
		t.Fatal("accepted a node id from outside the run")
	}
	if !strings.Contains(err.Error(), "is not part of run") {
		t.Errorf("error = %q", err)
	}
	if len(store.saved) != 0 {
		t.Error("store received the decision anyway")
	}

	// The same call without the foreign node must succeed: a title with no node
	// is a complete answer for a document Mathpix gave no H1.
	got, err := svc.ResolveTitle(context.Background(), "run-1", taskID, "A Study", "", "alex", "")
	if err != nil {
		t.Fatalf("ResolveTitle without a node: %v", err)
	}
	if got.AssignedDocumentTitleText != "A Study" {
		t.Errorf("title = %q", got.AssignedDocumentTitleText)
	}
	if got.AssignedRole != "" {
		t.Errorf("title decision carries role %q", got.AssignedRole)
	}
}

// TestReview_ShowsAnExistingDecision closes the loop: an answer must be visible
// to the next person who opens the queue, or it will be answered twice.
func TestReview_ShowsAnExistingDecision(t *testing.T) {
	svc, _, run := harness(t, reviewMarkdown)
	taskID := roleTaskID(t, run)

	if _, err := svc.Resolve(context.Background(), "run-1", taskID, segment.RoleMethodology, "shreya", "noted"); err != nil {
		t.Fatalf("Resolve: %v", err)
	}

	_, items, err := svc.Review(context.Background(), "run-1")
	if err != nil {
		t.Fatalf("Review: %v", err)
	}

	for _, it := range items {
		if it.TaskID != taskID {
			continue
		}
		if it.Decision == nil {
			t.Fatal("the answered task shows no decision")
		}
		if it.Decision.AssignedRole != segment.RoleMethodology {
			t.Errorf("decision role = %q", it.Decision.AssignedRole)
		}
		return
	}
	t.Fatalf("task %s missing from the review items", taskID)
}

func roleTaskID(t *testing.T, run *segment.Run) string {
	t.Helper()
	for i, task := range run.Tasks {
		if task.Reason != segment.ReasonTitleAmbiguity {
			return run.TaskIDs[i]
		}
	}
	t.Fatal("the fixture produced no role task")
	return ""
}
