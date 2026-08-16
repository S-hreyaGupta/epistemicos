package store

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// testPool connects to the database named by PAPERLY_DB_URL, or skips.
//
// Skipping rather than failing is the right posture for a store test: a
// developer without Docker running should not see a red build for a reason
// unrelated to their change. CI sets the variable, so the tests do run where it
// matters — and a skip that is silent in CI would be worse than no test, which
// is why the skip message names the variable.
func testPool(t *testing.T) *pgxpool.Pool {
	t.Helper()

	url := os.Getenv("PAPERLY_DB_URL")
	if url == "" {
		t.Skip("PAPERLY_DB_URL is not set; start postgres and export it to run the store tests")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	pool, err := pgxpool.New(ctx, url)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		t.Skipf("cannot reach postgres at PAPERLY_DB_URL: %v", err)
	}

	t.Cleanup(pool.Close)
	return pool
}

// fixtureRun builds a small but structurally complete run: a title, a resolved
// section, an unresolved section with its task, and a parent-child link.
func fixtureRun(t *testing.T) segment.Run {
	t.Helper()

	md := []byte("# A Study Of Things\n\nAuthors.\n\n## Methodology\n\nMethod prose.\n\n### Structural model\n\nMore prose.\n")

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

func cleanup(t *testing.T, pool *pgxpool.Pool, runID string) {
	t.Helper()
	t.Cleanup(func() {
		// Nodes, tasks and decisions cascade from the run.
		_, _ = pool.Exec(context.Background(), `DELETE FROM segmentation_runs WHERE segmentation_run_id = $1`, runID)
	})
}

// TestSaveAndGetRun is the round trip: everything written must come back
// identical, including the nullable fields whose NULL-versus-empty distinction
// carries meaning.
func TestSaveAndGetRun(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	want := fixtureRun(t)
	cleanup(t, pool, want.ID)

	if err := s.SaveRun(ctx, &want); err != nil {
		t.Fatalf("SaveRun: %v", err)
	}

	got, err := s.GetRun(ctx, want.ID)
	if err != nil {
		t.Fatalf("GetRun: %v", err)
	}

	if got.ExtractionRunID != want.ExtractionRunID {
		t.Errorf("extraction_run_id = %q, want %q", got.ExtractionRunID, want.ExtractionRunID)
	}
	if got.ApprovedMarkdownHash != want.ApprovedMarkdownHash {
		t.Errorf("approved_markdown_hash = %q, want %q", got.ApprovedMarkdownHash, want.ApprovedMarkdownHash)
	}
	if got.StructuralRuleVersion != "2.7" {
		t.Errorf("structural_rule_version = %q, want \"2.7\"", got.StructuralRuleVersion)
	}
	if got.Status != segment.RunCompleted {
		t.Errorf("status = %q, want %q", got.Status, segment.RunCompleted)
	}
	if got.DocumentTitleStatus != want.DocumentTitleStatus {
		t.Errorf("title status = %q, want %q", got.DocumentTitleStatus, want.DocumentTitleStatus)
	}
	if got.DocumentTitleText != want.DocumentTitleText {
		t.Errorf("title text = %q, want %q", got.DocumentTitleText, want.DocumentTitleText)
	}
	if got.DocumentTitleOrdinal != want.DocumentTitleOrdinal {
		t.Errorf("title ordinal = %d, want %d", got.DocumentTitleOrdinal, want.DocumentTitleOrdinal)
	}

	// H5 and H6 must read back as explicit zeroes. A missing key and a zero
	// count are the same fact only until a reader treats absence as unknown,
	// and §10 depends on those counts being legible as deliberate exclusions.
	for level := 1; level <= 6; level++ {
		if got.HeadingCounts[level] != want.HeadingCounts[level] {
			t.Errorf("H%d count = %d, want %d", level, got.HeadingCounts[level], want.HeadingCounts[level])
		}
	}

	if len(got.Nodes) != len(want.Nodes) {
		t.Fatalf("read back %d nodes, want %d", len(got.Nodes), len(want.Nodes))
	}
	for i := range want.Nodes {
		w, g := want.Nodes[i], got.Nodes[i]

		if g.Ordinal != w.Ordinal {
			t.Errorf("node %d ordinal = %d, want %d", i, g.Ordinal, w.Ordinal)
		}
		if g.ParentOrdinal != w.ParentOrdinal {
			t.Errorf("node %d parent = %d, want %d", i, g.ParentOrdinal, w.ParentOrdinal)
		}
		if g.StartOffset != w.StartOffset || g.EndOffset != w.EndOffset {
			t.Errorf("node %d span = [%d,%d), want [%d,%d)", i, g.StartOffset, g.EndOffset, w.StartOffset, w.EndOffset)
		}
		if g.Kind != w.Kind {
			t.Errorf("node %d kind = %q, want %q", i, g.Kind, w.Kind)
		}
		if g.HeadingRaw != w.HeadingRaw {
			t.Errorf("node %d heading = %q, want %q", i, g.HeadingRaw, w.HeadingRaw)
		}
		if g.Classification.Role != w.Classification.Role {
			t.Errorf("node %d role = %q, want %q", i, g.Classification.Role, w.Classification.Role)
		}
		if g.Classification.Status != w.Classification.Status {
			t.Errorf("node %d status = %q, want %q", i, g.Classification.Status, w.Classification.Status)
		}
	}

	if len(got.Tasks) != len(want.Tasks) {
		t.Fatalf("read back %d tasks, want %d", len(got.Tasks), len(want.Tasks))
	}
	for i := range want.Tasks {
		if got.Tasks[i].Reason != want.Tasks[i].Reason {
			t.Errorf("task %d reason = %q, want %q", i, got.Tasks[i].Reason, want.Tasks[i].Reason)
		}
		if got.Tasks[i].SectionOrdinal != want.Tasks[i].SectionOrdinal {
			t.Errorf("task %d section ordinal = %d, want %d", i, got.Tasks[i].SectionOrdinal, want.Tasks[i].SectionOrdinal)
		}
	}
}

// TestGetRun_NotFound checks the sentinel, so callers can errors.Is rather than
// string-match.
func TestGetRun_NotFound(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)

	_, err := s.GetRun(context.Background(), uuid.NewString())
	if err == nil {
		t.Fatal("GetRun on an unknown id returned no error")
	}
	if err != ports.ErrNotFound {
		t.Errorf("error = %v, want ports.ErrNotFound", err)
	}
}

// TestSaveRun_UnresolvedNodeCannotCarryARole is the CHECK constraint under
// test, not the Go code.
//
// §8's overlay model depends on an unresolved node storing no role: the
// effective value prefers a human decision when one exists and falls back to
// the machine determination otherwise, so a placeholder role would be
// indistinguishable from a real answer. Enforcing it in the schema means a
// future writer cannot forget, which a code path cannot promise.
func TestSaveRun_UnresolvedNodeCannotCarryARole(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := fixtureRun(t)
	cleanup(t, pool, run.ID)

	// Corrupt one node the way a careless caller might: unresolved, but
	// carrying a role anyway.
	//
	// The invalid state is constructed OUTRIGHT rather than found by searching
	// for an existing unresolved node. An earlier version did search, and under
	// rule version 2.2 it silently stopped testing anything: parent inheritance
	// resolved the only unresolved node in this fixture, the loop found nothing
	// to corrupt, and the save succeeded — so a test about a database constraint
	// was quietly passing on a row that was never invalid.
	run.Nodes[len(run.Nodes)-1].Classification = segment.Classification{
		Role:   segment.RoleMethodology,
		Status: segment.StatusUnresolved,
	}

	if err := s.SaveRun(ctx, &run); err == nil {
		t.Fatal("saved an unresolved node carrying a role; the section_nodes_unresolved_is_empty constraint is not enforcing §8")
	}
}

// TestSaveRun_IsAtomic proves a failed write leaves nothing behind.
//
// A partially written run is indistinguishable from a document with fewer
// sections, which is exactly the silent loss §10 exists to prevent — and §10
// runs in the domain, before the store, so it cannot catch this.
func TestSaveRun_IsAtomic(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	run := fixtureRun(t)
	cleanup(t, pool, run.ID)

	// A heading level outside 1-4 violates section_nodes_level_valid, so the
	// insert fails partway through the node loop.
	run.Nodes[len(run.Nodes)-1].HeadingLevel = 7

	if err := s.SaveRun(ctx, &run); err == nil {
		t.Fatal("SaveRun accepted an invalid heading level")
	}

	var count int
	if err := pool.QueryRow(ctx,
		`SELECT count(*) FROM segmentation_runs WHERE segmentation_run_id = $1`, run.ID,
	).Scan(&count); err != nil {
		t.Fatalf("count runs: %v", err)
	}
	if count != 0 {
		t.Errorf("a failed SaveRun left %d run rows behind; the write is not atomic", count)
	}

	if err := pool.QueryRow(ctx,
		`SELECT count(*) FROM section_nodes WHERE segmentation_run_id = $1`, run.ID,
	).Scan(&count); err != nil {
		t.Fatalf("count nodes: %v", err)
	}
	if count != 0 {
		t.Errorf("a failed SaveRun left %d node rows behind", count)
	}
}

// TestSaveRun_FixtureRoundTripsAllOffsets persists the real reference document
// and reads back all 22 spans.
//
// The domain tests already prove Build produces the right offsets. This proves
// they survive a round trip through Postgres — that nothing is truncated by a
// column type, and that parent links reconstruct from ids back into ordinals.
func TestSaveRun_FixtureRoundTripsAllOffsets(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	md, err := os.ReadFile("../../../core/domain/segment/testdata/demo.md")
	if err != nil {
		t.Skipf("fixture not readable from here: %v", err)
	}

	doc, err := segment.Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := segment.NewRun(doc, "fixture-paper", "a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e")
	run.ID = uuid.NewString()
	run.NodeIDs = make([]string, len(run.Nodes))
	for i := range run.Nodes {
		run.NodeIDs[i] = uuid.NewString()
	}
	run.TaskIDs = make([]string, len(run.Tasks))
	for i := range run.Tasks {
		run.TaskIDs[i] = uuid.NewString()
	}
	cleanup(t, pool, run.ID)

	if err := s.SaveRun(ctx, &run); err != nil {
		t.Fatalf("SaveRun: %v", err)
	}

	got, err := s.GetRun(ctx, run.ID)
	if err != nil {
		t.Fatalf("GetRun: %v", err)
	}

	if len(got.Nodes) != 22 {
		t.Fatalf("read back %d nodes, want 22", len(got.Nodes))
	}
	// NONE under rule version 2.7. Six at 2.1, five at 2.2 once "4.2 Structural
	// model" inherited results, and zero at 2.7 once nested-occurrence
	// suppression resolved "2 Theoretical background and hypotheses derivation"
	// and its four subsections inherited theory.
	//
	// The count is asserted rather than derived, deliberately. This is a
	// PERSISTENCE test: a run with no tasks must still round-trip, and a store
	// that silently dropped every task would pass any assertion computed from
	// the run it was just handed.
	if len(got.Tasks) != 0 {
		t.Errorf("read back %d tasks, want 0", len(got.Tasks))
	}

	for i := range run.Nodes {
		if got.Nodes[i].StartOffset != run.Nodes[i].StartOffset ||
			got.Nodes[i].EndOffset != run.Nodes[i].EndOffset {
			t.Errorf("node %d span = [%d,%d), want [%d,%d)",
				i, got.Nodes[i].StartOffset, got.Nodes[i].EndOffset,
				run.Nodes[i].StartOffset, run.Nodes[i].EndOffset)
		}
		if got.Nodes[i].ParentOrdinal != run.Nodes[i].ParentOrdinal {
			t.Errorf("node %d parent = %d, want %d", i, got.Nodes[i].ParentOrdinal, run.Nodes[i].ParentOrdinal)
		}
	}
}
