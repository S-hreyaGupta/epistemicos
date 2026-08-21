package store

import (
	"context"
	"errors"
	"testing"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/researchunit"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// These are integration tests because what can go wrong here is SQL: an UPSERT
// used for idempotence, a DELETE-and-rewrite of the child rows, and a
// three-column key. A fake store would accept all three however they behaved.

const testHash = "4ff6aa64ee8c4556e0d63d1de98f487c8a609cd81d16e638b459de91bafef147"

// savedPaper creates the papers row the verdict's foreign key needs.
func savedPaper(t *testing.T, pool *pgxpool.Pool) string {
	t.Helper()

	id := uuid.NewString()
	p := &paper.Paper{
		ID: paper.ID(id),
		// papers.hash is NOT NULL and UNIQUE, so it must differ per test. Two
		// fixtures sharing an empty hash would collide, and the second test to
		// run would fail for a reason that has nothing to do with its subject.
		Hash:         paper.Hash(id),
		Status:       paper.StatusReady,
		Markdown:     "# A Study Of Things\n",
		MarkdownHash: testHash,
	}
	if err := NewPostgresPaperStore(pool).Save(context.Background(), p); err != nil {
		t.Fatalf("save paper: %v", err)
	}
	t.Cleanup(func() {
		_, _ = pool.Exec(context.Background(), `DELETE FROM papers WHERE id = $1`, id)
	})
	return id
}

// frontiersGate is the real verdict from paper 43338825, three studies named in
// its headings. Using a measured example rather than an invented one keeps the
// evidence ordering honest: five labels, three groups.
func frontiersGate() researchunit.Gate {
	return researchunit.Gate{
		RuleVersion: researchunit.RuleVersion,
		Verdict:     researchunit.VerdictMulti,
		StudyCount:  3,
		Reason:      "3 studies named in the headings (1, 2, 3); the MVP handles one-study papers only",
		Evidence: []researchunit.Evidence{
			{Kind: "study", Label: "1", Group: "1", Text: "STUDY 1", Ordinal: 11},
			{Kind: "study", Label: "1", Group: "1", Text: "Discussion Study 1", Ordinal: 19},
			{Kind: "study", Label: "2", Group: "2", Text: "STUDY 2", Ordinal: 20},
			{Kind: "study", Label: "2", Group: "2", Text: "Discussion Study 2", Ordinal: 31},
			{Kind: "study", Label: "3", Group: "3", Text: "STUDY 3", Ordinal: 32},
		},
	}
}

func TestSaveAndGetResearchUnitGate(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresResearchUnitStore(pool)
	ctx := context.Background()

	paperID := savedPaper(t, pool)
	want := frontiersGate()

	if err := s.SaveGate(ctx, paperID, testHash, want); err != nil {
		t.Fatalf("SaveGate: %v", err)
	}

	got, err := s.CurrentGate(ctx, paperID, testHash, researchunit.RuleVersion)
	if err != nil {
		t.Fatalf("CurrentGate: %v", err)
	}

	if got.Verdict != want.Verdict || got.StudyCount != want.StudyCount {
		t.Errorf("verdict = %q/%d, want %q/%d", got.Verdict, got.StudyCount, want.Verdict, want.StudyCount)
	}
	if got.Reason != want.Reason {
		t.Errorf("reason = %q, want the gate's own sentence", got.Reason)
	}
	if got.RuleVersion != researchunit.RuleVersion {
		t.Errorf("rule version = %q, want %q", got.RuleVersion, researchunit.RuleVersion)
	}

	// Evidence order is meaningful: heading evidence can settle the verdict and
	// body evidence never can, so a reviewer must be able to tell them apart by
	// reading down the list.
	if len(got.Evidence) != len(want.Evidence) {
		t.Fatalf("got %d evidence rows, want %d", len(got.Evidence), len(want.Evidence))
	}
	for i := range want.Evidence {
		if got.Evidence[i] != want.Evidence[i] {
			t.Errorf("evidence[%d] = %+v, want %+v", i, got.Evidence[i], want.Evidence[i])
		}
	}
}

// TestSaveGate_IsIdempotent is the property that distinguishes this store from
// the paper-type one.
//
// That gate appends, because it asks a model and the same question can get a
// different answer next month. This gate is a computation: the same markdown
// under the same rule version cannot produce anything else. A second row would
// record a change that did not happen, and would double the evidence a reviewer
// is shown.
func TestSaveGate_IsIdempotent(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresResearchUnitStore(pool)
	ctx := context.Background()

	paperID := savedPaper(t, pool)
	gate := frontiersGate()

	for i := 0; i < 3; i++ {
		if err := s.SaveGate(ctx, paperID, testHash, gate); err != nil {
			t.Fatalf("SaveGate (run %d): %v", i+1, err)
		}
	}

	var verdicts, evidence int
	if err := pool.QueryRow(ctx,
		`SELECT count(*) FROM research_unit_verdicts WHERE paper_id = $1`, paperID).Scan(&verdicts); err != nil {
		t.Fatalf("count verdicts: %v", err)
	}
	if verdicts != 1 {
		t.Errorf("%d verdict rows after three identical runs, want 1", verdicts)
	}

	if err := pool.QueryRow(ctx, `
		SELECT count(*) FROM research_unit_evidence e
		  JOIN research_unit_verdicts v ON v.research_unit_verdict_id = e.research_unit_verdict_id
		 WHERE v.paper_id = $1`, paperID).Scan(&evidence); err != nil {
		t.Fatalf("count evidence: %v", err)
	}
	if evidence != 5 {
		t.Errorf("%d evidence rows after three identical runs, want 5 — evidence is replaced, not appended", evidence)
	}
}

// TestSaveGate_ADifferentRuleVersionIsADifferentRow.
//
// A rules change genuinely can change the answer, and that IS a second fact. It
// is the one case where two rows about one paper are correct, and it is why the
// version is part of the key rather than a column beside it.
func TestSaveGate_ADifferentRuleVersionIsADifferentRow(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresResearchUnitStore(pool)
	ctx := context.Background()

	paperID := savedPaper(t, pool)

	first := frontiersGate()
	if err := s.SaveGate(ctx, paperID, testHash, first); err != nil {
		t.Fatalf("SaveGate (1.0): %v", err)
	}

	// The same paper under hypothetical future rules that find the unnumbered
	// pre-study as well. This is FUTURE_WORK item K, and it is exactly the kind
	// of change that would move the version.
	second := frontiersGate()
	second.RuleVersion = "1.1"
	second.StudyCount = 4
	second.Reason = "4 studies, including one reported without a number"
	if err := s.SaveGate(ctx, paperID, testHash, second); err != nil {
		t.Fatalf("SaveGate (1.1): %v", err)
	}

	var n int
	if err := pool.QueryRow(ctx,
		`SELECT count(*) FROM research_unit_verdicts WHERE paper_id = $1`, paperID).Scan(&n); err != nil {
		t.Fatalf("count verdicts: %v", err)
	}
	if n != 2 {
		t.Errorf("%d verdict rows, want 2 — a rules change is a new answer, not an overwrite", n)
	}

	// And each version still reads back its own answer.
	old, err := s.CurrentGate(ctx, paperID, testHash, "1.0")
	if err != nil {
		t.Fatalf("CurrentGate (1.0): %v", err)
	}
	if old.StudyCount != 3 {
		t.Errorf("1.0 study count = %d, want 3 — the older verdict must not be rewritten by the newer", old.StudyCount)
	}
}

// TestCurrentGate_ScopedToTheMarkdown.
//
// A paper re-ingested into different markdown must not inherit a verdict reached
// from text that no longer exists. Same rule as paper-type, and the reason is
// the same: the evidence rows quote headings, and headings from a previous
// extraction may simply not be there any more.
func TestCurrentGate_ScopedToTheMarkdown(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresResearchUnitStore(pool)
	ctx := context.Background()

	paperID := savedPaper(t, pool)
	if err := s.SaveGate(ctx, paperID, testHash, frontiersGate()); err != nil {
		t.Fatalf("SaveGate: %v", err)
	}

	other := "0000000000000000000000000000000000000000000000000000000000000000"
	_, err := s.CurrentGate(ctx, paperID, other, researchunit.RuleVersion)
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ErrNotFound for a different markdown", err)
	}
}

// TestSaveGate_RefusesAVerdictWithNoRuleVersion.
//
// Defaulting to the current constant would stamp today's version onto a verdict
// computed by rules we cannot identify. A row that misreports its own provenance
// is worse than a missing one: the first is trusted and wrong, the second is
// merely absent.
func TestSaveGate_RefusesAVerdictWithNoRuleVersion(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresResearchUnitStore(pool)
	ctx := context.Background()

	paperID := savedPaper(t, pool)

	gate := frontiersGate()
	gate.RuleVersion = ""

	if err := s.SaveGate(ctx, paperID, testHash, gate); err == nil {
		t.Error("stored a verdict with no rule version; it could not say which rules produced it")
	}
}

// TestSaveGate_SingleStudyPaperIsStoredToo.
//
// The refusals are the interesting rows, but a `single` verdict is the record
// that the gate was consulted and let the paper through. Storing only refusals
// would make "this paper was never checked" and "this paper passed" the same
// absence.
func TestSaveGate_SingleStudyPaperIsStoredToo(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresResearchUnitStore(pool)
	ctx := context.Background()

	paperID := savedPaper(t, pool)

	gate := researchunit.Gate{
		RuleVersion: researchunit.RuleVersion,
		Verdict:     researchunit.VerdictSingle,
		StudyCount:  0,
		Reason:      "no numbered studies, experiments, phases or samples in the headings",
	}
	if err := s.SaveGate(ctx, paperID, testHash, gate); err != nil {
		t.Fatalf("SaveGate: %v", err)
	}

	got, err := s.CurrentGate(ctx, paperID, testHash, researchunit.RuleVersion)
	if err != nil {
		t.Fatalf("CurrentGate: %v", err)
	}
	if got.Verdict != researchunit.VerdictSingle {
		t.Errorf("verdict = %q, want %q", got.Verdict, researchunit.VerdictSingle)
	}
	if len(got.Evidence) != 0 {
		t.Errorf("got %d evidence rows for a paper that matched nothing, want 0", len(got.Evidence))
	}
}
