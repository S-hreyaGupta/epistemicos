package segment

import (
	"strings"
	"testing"
)

// Acceptance criteria AC-01 through AC-14 from specification v2.1 §14.
//
// Each is named for its criterion so the done-condition can be read off a test
// run rather than reasoned about. Several overlap with tests elsewhere in this
// package, and the duplication is deliberate: those tests are named for the
// behaviour they guard and would be renamed or split as the code moves, whereas
// these are named for a contract that does not.
//
// AC-11, AC-12 and AC-13 are not here. They concern the pointer chain, Step 4's
// consumption and the hash gate, which live outside this package; see the notes
// at the bottom of the file.

// AC-01 — a standard paper produces a title node plus one node per detected
// H2-H4, with conventional headings resolved by rule and content_class
// populated from the table.
func TestAC01_StandardPaper(t *testing.T) {
	md := loadFixture(t)
	exp := loadExpected(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != len(exp.SectionNodes) {
		t.Fatalf("built %d nodes, want %d", len(doc.Nodes), len(exp.SectionNodes))
	}

	titles := 0
	for _, n := range doc.Nodes {
		if n.Kind == KindDocumentTitle {
			titles++
		}
		if n.HeadingLevel < 1 || n.HeadingLevel > 4 {
			t.Errorf("node %d has level %d, outside the structural contract", n.Ordinal, n.HeadingLevel)
		}
		// Every resolved node carries a class; every unresolved one carries
		// neither role nor class.
		if n.Classification.Status == StatusResolved && n.Classification.ContentClass == "" {
			t.Errorf("node %d (%q) resolved without a content class", n.Ordinal, n.HeadingRaw)
		}
		if n.Classification.Status == StatusUnresolved && n.Classification.Role != "" {
			t.Errorf("node %d (%q) is unresolved but carries role %q", n.Ordinal, n.HeadingRaw, n.Classification.Role)
		}
	}
	if titles != 1 {
		t.Errorf("%d title nodes, want exactly 1", titles)
	}
}

// AC-02 — #### Abstract becomes its own node with primary_role = abstract, by
// ordinary exact match. No promotion, no rescue, no special mechanism.
func TestAC02_AbstractResolvesByOrdinaryMatch(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	found := false
	for _, n := range doc.Nodes {
		if n.HeadingRaw != "Abstract" {
			continue
		}
		found = true

		if n.HeadingLevel != 4 {
			t.Errorf("Abstract level = %d, want 4", n.HeadingLevel)
		}
		if n.Classification.Role != RoleAbstract {
			t.Errorf("Abstract role = %q, want %q", n.Classification.Role, RoleAbstract)
		}
		if n.Classification.Method != MethodRule {
			t.Errorf("Abstract method = %q, want %q — it must resolve by ordinary keyword match, not by a special case", n.Classification.Method, MethodRule)
		}
	}
	if !found {
		t.Fatal("no Abstract node in the fixture")
	}
}

// AC-03 — a heading hitting two distinct roles is unresolved, with both
// candidates recorded and NO tie-break applied.
func TestAC03_MultiRoleMatchIsNotTieBroken(t *testing.T) {
	got := Classify("theoretical background and hypotheses derivation")

	if got.Status != StatusUnresolved {
		t.Fatalf("status = %q, want %q — a tie must not be resolved by preference order", got.Status, StatusUnresolved)
	}
	if got.Role != "" {
		t.Errorf("role = %q, want empty", got.Role)
	}

	want := []Role{RoleIntroduction, RoleTheory}
	if len(got.CandidateRoles) != len(want) {
		t.Fatalf("candidates = %v, want %v", got.CandidateRoles, want)
	}
	for i := range want {
		if got.CandidateRoles[i] != want[i] {
			t.Errorf("candidate %d = %q, want %q", i, got.CandidateRoles[i], want[i])
		}
	}
}

// AC-04 — several keywords from the SAME role resolve cleanly, with no review
// task. This is the distinct-role count, and it is the rule most easily got
// wrong by counting hits instead.
func TestAC04_SameRoleMultiKeywordResolves(t *testing.T) {
	got := Classify("prior research and extant literature")

	if got.Status != StatusResolved {
		t.Fatalf("status = %q, want %q — two keywords from one role is one role", got.Status, StatusResolved)
	}
	if got.Role != RoleLiteratureReview {
		t.Errorf("role = %q, want %q", got.Role, RoleLiteratureReview)
	}
	if got.Method != MethodRule {
		t.Errorf("method = %q, want %q", got.Method, MethodRule)
	}
	if len(got.MatchedKeywords) < 2 {
		t.Errorf("matched keywords = %v, want at least two, or this test proves nothing", got.MatchedKeywords)
	}
}

// AC-05 — all four identifier forms are stripped and the heading resolves
// normally afterwards.
func TestAC05_IdentifiersAreStripped(t *testing.T) {
	cases := []struct {
		heading string
		want    Role
	}{
		{"IV. Results", RoleResults},
		{"A. Methods", RoleMethodology},
		{"2.1 Methods", RoleMethodology},
		{"Section 4: Results", RoleResults},
	}

	for _, c := range cases {
		t.Run(c.heading, func(t *testing.T) {
			_, _, semantic := ParseContainer(StripIdentifiers(Normalize(c.heading)))
			got := Classify(semantic)

			if got.Status != StatusResolved {
				t.Fatalf("status = %q, want %q (semantic heading was %q)", got.Status, StatusResolved, semantic)
			}
			if got.Role != c.want {
				t.Errorf("role = %q, want %q", got.Role, c.want)
			}
		})
	}
}

// AC-06 — appendix containers. A labelled container with a semantic suffix
// classifies on the suffix; a bare one resolves to Unknown structurally with no
// task; and a child classifies independently of either.
func TestAC06_AppendixContainers(t *testing.T) {
	t.Run("labelled with suffix", func(t *testing.T) {
		container, label, semantic := ParseContainer(StripIdentifiers(Normalize("Appendix B: Robustness checks")))

		if container != ContainerAppendix {
			t.Errorf("container = %q, want %q", container, ContainerAppendix)
		}
		if label != "B" {
			t.Errorf("label = %q, want \"B\"", label)
		}

		if got := Classify(semantic); got.Role != RoleResults {
			t.Errorf("role = %q, want %q", got.Role, RoleResults)
		}
	})

	t.Run("bare container", func(t *testing.T) {
		container, label, semantic := ParseContainer(StripIdentifiers(Normalize("Appendix B")))

		if container != ContainerAppendix || label != "B" || semantic != "" {
			t.Errorf("parse = (%q, %q, %q), want (appendix, B, empty)", container, label, semantic)
		}

		got := Classify(semantic)
		if got.Role != RoleUnknown {
			t.Errorf("role = %q, want %q", got.Role, RoleUnknown)
		}
		if got.ContentClass != ClassAnalytical {
			t.Errorf("content class = %q, want %q", got.ContentClass, ClassAnalytical)
		}
		if got.Status != StatusResolved {
			t.Errorf("status = %q, want %q — a bare container is a complete answer", got.Status, StatusResolved)
		}
		if got.Method != MethodStructural {
			t.Errorf("method = %q, want %q", got.Method, MethodStructural)
		}
	})

	t.Run("child classifies independently", func(t *testing.T) {
		md := []byte("## Appendix B\n\nBody.\n\n### Robustness checks\n\nChild body.\n")

		doc, err := Build(md)
		if err != nil {
			t.Fatalf("Build: %v", err)
		}

		if doc.Nodes[1].Classification.Role != RoleResults {
			t.Errorf("child role = %q, want %q — classification is parent-independent", doc.Nodes[1].Classification.Role, RoleResults)
		}

		// Neither the container nor its child may raise a task: the container
		// is a complete structural answer, and the child resolved by rule.
		//
		// Counted per node rather than as a total. This snippet has no H1, so
		// §4 correctly raises a title_ambiguity task, and a total would fold
		// that unrelated rule into a criterion about containers — which is
		// what an earlier version of this test did, and it failed for the
		// right reason.
		run := NewRun(doc, "ac06", "hash")
		for _, task := range run.Tasks {
			if task.SectionOrdinal == 0 {
				t.Errorf("the bare container raised a %s task; it resolves structurally and has nothing to adjudicate", task.Reason)
			}
			if task.SectionOrdinal == 1 {
				t.Errorf("the child raised a %s task despite resolving to %s", task.Reason, RoleResults)
			}
		}
	})
}

// AC-07 — multiple H1s: the first becomes the title by structural_rule, a later
// matching H1 is an ordinary node, and a later unmatched H1 is an unresolved
// node rather than a title candidate.
func TestAC07_MultipleH1s(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"# Methodology\n\nMethod prose.\n\n" +
		"# Zorblatt Considerations\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleOrdinal != 0 || doc.TitleMethod != MethodStructuralRule {
		t.Fatalf("title ordinal = %d, method = %q; want 0 and %q", doc.TitleOrdinal, doc.TitleMethod, MethodStructuralRule)
	}

	if doc.Nodes[1].Kind != KindSection || doc.Nodes[1].Classification.Role != RoleMethodology {
		t.Errorf("second H1: kind %q role %q; want section/%s", doc.Nodes[1].Kind, doc.Nodes[1].Classification.Role, RoleMethodology)
	}

	third := doc.Nodes[2]
	if third.Kind != KindSection {
		t.Errorf("third H1 kind = %q, want %q — a later H1 is never a title candidate", third.Kind, KindSection)
	}
	if third.Classification.Status != StatusUnresolved {
		t.Errorf("third H1 status = %q, want %q", third.Classification.Status, StatusUnresolved)
	}
}

// AC-08 — no H1, or a first H1 resolving to an ordinary role, leaves the title
// unresolved with a title_ambiguity task, while everything else classifies
// normally.
func TestAC08_TitleAmbiguity(t *testing.T) {
	cases := map[string][]byte{
		"first H1 resolves to a role": []byte("# Introduction\n\nProse.\n\n## Methodology\n\nMethod prose.\n"),
		"no H1 at all":                []byte("## Introduction\n\nProse.\n\n## Methodology\n\nMethod prose.\n"),
	}

	for name, md := range cases {
		t.Run(name, func(t *testing.T) {
			doc, err := Build(md)
			if err != nil {
				t.Fatalf("Build: %v", err)
			}

			if doc.TitleStatus != TitleUnresolved {
				t.Errorf("title status = %q, want %q", doc.TitleStatus, TitleUnresolved)
			}

			run := NewRun(doc, "ac08", "hash")

			found := false
			for _, task := range run.Tasks {
				if task.Reason == ReasonTitleAmbiguity {
					found = true
				}
			}
			if !found {
				t.Error("no title_ambiguity task was raised")
			}

			// Everything else still classifies.
			last := doc.Nodes[len(doc.Nodes)-1]
			if last.Classification.Role != RoleMethodology {
				t.Errorf("last node role = %q, want %q — a title problem must not block ordinary classification", last.Classification.Role, RoleMethodology)
			}
		})
	}
}

// AC-09 — zero silent loss, in both directions. N detected headings produce
// exactly N nodes, and a simulated dropped heading fails the run.
func TestAC09_ZeroSilentLoss(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	headings := detectHeadings(md)
	structural := 0
	for _, h := range headings {
		if h.Level >= 1 && h.Level <= 4 {
			structural++
		}
	}

	if len(doc.Nodes) != structural {
		t.Fatalf("%d detected H1-H4 headings produced %d nodes", structural, len(doc.Nodes))
	}

	t.Run("a dropped heading fails the run", func(t *testing.T) {
		damaged := doc
		damaged.Nodes = doc.Nodes[:len(doc.Nodes)-1]

		err := ValidateNoSilentLoss(damaged, headings)
		if err == nil {
			t.Fatal("dropping a node did not violate the invariant")
		}
		if !strings.Contains(err.Error(), "silent_loss_invariant") {
			t.Errorf("error = %q, want it to name silent_loss_invariant", err)
		}
	})
}

// AC-10 — the review overlay, on both axes. A decision supplies the effective
// value; the machine's stored fields are unchanged.
//
// The UNIQUE(review_task_id) half of AC-10 is enforced by the schema and
// belongs to the store's tests, not here.
func TestAC10_ReviewOverlay(t *testing.T) {
	t.Run("section role", func(t *testing.T) {
		node := SectionNode{Classification: Classification{Status: StatusUnresolved}}
		decision := &ReviewDecision{AssignedRole: RoleTheory, AssignedContentClass: ClassAnalytical}

		got := EffectiveFor(node, decision)

		if got.Role != RoleTheory {
			t.Errorf("effective role = %q, want %q", got.Role, RoleTheory)
		}
		if got.Status != EffectiveReviewerConfirmed {
			t.Errorf("effective status = %q, want %q", got.Status, EffectiveReviewerConfirmed)
		}
		if node.Classification.Role != "" || node.Classification.Status != StatusUnresolved {
			t.Error("the node's machine fields changed; they must remain as provenance")
		}
	})

	t.Run("document title", func(t *testing.T) {
		run := Run{
			DocumentTitleText:    "",
			DocumentTitleOrdinal: -1,
			DocumentTitleStatus:  TitleUnresolved,
		}
		decision := &ReviewDecision{
			AssignedDocumentTitleText:   "The Real Title",
			AssignedDocumentTitleNodeID: "node-2",
		}

		got := EffectiveTitleFor(run, decision)

		if got.Text != "The Real Title" || got.NodeID != "node-2" {
			t.Errorf("effective title = %+v", got)
		}
		if got.Status != EffectiveReviewerConfirmed || got.Method != "human" {
			t.Errorf("effective status/method = %q/%q, want %q/human", got.Status, got.Method, EffectiveReviewerConfirmed)
		}
		if run.DocumentTitleStatus != TitleUnresolved {
			t.Error("the run's stored title status changed")
		}
	})
}

// AC-14 — pre-heading content produces no node, and no node's span reaches back
// into it.
func TestAC14_PreHeadingContentHasNoNode(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	headings := detectHeadings(md)
	firstHeading := headings[0].ByteStart

	if firstHeading == 0 {
		t.Skip("the fixture has no preamble, so this criterion is not exercised")
	}

	for _, n := range doc.Nodes {
		if n.StartOffset < firstHeading {
			t.Errorf("node %d (%q) starts at %d, before the first heading at %d — preamble must belong to no node",
				n.Ordinal, n.HeadingRaw, n.StartOffset, firstHeading)
		}
	}

	// And the preamble text really is absent from every span.
	preamble := string(md[:firstHeading])
	if len(strings.TrimSpace(preamble)) == 0 {
		t.Skip("preamble is whitespace only")
	}
	for _, n := range doc.Nodes {
		if strings.Contains(n.Text(md), strings.TrimSpace(preamble)) {
			t.Errorf("node %d contains the preamble text", n.Ordinal)
		}
	}
}

// AC-11, AC-12 and AC-13 are recorded here rather than implemented, because
// each is a claim about something outside this package.
//
// AC-11 (reprocessing advances current_segmentation_run_id only on Completed)
// requires the §9 pointer chain. ExtractionRun does not exist in this
// repository, so the advancement is a deferred obligation under §12 G5 — see
// TODO(step9-pointer) in internal/adapters/secondary/approved. Testing it here
// would mean testing a column that was invented for the test.
//
// AC-12 (funding never reaches Step 4; references and data_availability are
// available to their consumers) is a claim about Step 4's behaviour. What this
// package owes it is that the content_class is present and correct on every
// node, which TestAC01_StandardPaper and TestRoleTableMatchesTable together
// establish. The consumption rule itself belongs to Step 4's tests.
//
// AC-13 (hash mismatch fails the run and writes nothing) is enforced in two
// places outside the domain: the adapter re-verifies the stored hash before
// returning markdown, and the service re-verifies again after fetching. Both
// are in internal/adapters/secondary/approved and
// internal/core/services/segmentation respectively, and neither is reachable
// from a package that takes []byte and returns nodes.
