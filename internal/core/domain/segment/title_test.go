package segment

import "testing"

// TestTitleCandidate_SuppressedWhenNoH1 is the case that motivated the rule.
//
// Mathpix emits an H1 or not depending on the PDF's typography, not on whether
// the document has a title. A systematic review arrived with no H1 at all, so
// its title came through as an H2 and classified as THEORY with a three-byte
// span. Step 4 would have read the paper's own title as analytical content.
func TestTitleCandidate_SuppressedWhenNoH1(t *testing.T) {
	md := []byte("## A systematic review on regenerative supply chains\n\n" +
		"#### Abstract\n\nAbstract prose.\n\n" +
		"## 1 Introduction\n\nOpening prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.HeadingCounts[1] != 0 {
		t.Fatalf("this test needs a document with no H1")
	}
	if doc.TitleStatus != TitleUnresolved {
		t.Fatalf("title status = %q, want %q", doc.TitleStatus, TitleUnresolved)
	}
	if doc.TitleCandidateOrdinal != 0 {
		t.Fatalf("candidate ordinal = %d, want 0", doc.TitleCandidateOrdinal)
	}

	n := doc.Nodes[0]

	if n.Classification.Role != "" {
		t.Errorf("candidate role = %q, want empty — nothing established that this is a section", n.Classification.Role)
	}
	if n.Classification.Status != StatusUnresolved {
		t.Errorf("candidate status = %q, want %q", n.Classification.Status, StatusUnresolved)
	}
	if n.Classification.ContentClass != "" {
		t.Errorf("candidate class = %q, want empty", n.Classification.ContentClass)
	}

	// The text, the span and the tree position all survive. This suppresses a
	// claim, not a node.
	if n.HeadingRaw == "" || n.EndOffset <= n.StartOffset {
		t.Errorf("the node lost its text or its span: %+v", n)
	}

	// The sections after it must be unaffected.
	if doc.Nodes[1].Classification.Role != RoleAbstract {
		t.Errorf("Abstract = %q, want %q", doc.Nodes[1].Classification.Role, RoleAbstract)
	}
	if doc.Nodes[2].Classification.Role != RoleIntroduction {
		t.Errorf("Introduction = %q, want %q", doc.Nodes[2].Classification.Role, RoleIntroduction)
	}
}

// TestTitleCandidate_RaisesExactlyOneTask.
//
// The candidate is unresolved, so the ordinary loop would raise a
// zero_role_match on it as well as the title_ambiguity task. That would put one
// section in the queue twice and ask a reviewer to answer one question in two
// places.
func TestTitleCandidate_RaisesExactlyOneTask(t *testing.T) {
	md := []byte("## A systematic review on regenerative supply chains\n\n" +
		"#### Abstract\n\nAbstract prose.\n\n" +
		"## 1 Introduction\n\nOpening prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	run := NewRun(doc, "test", "hash")

	var forCandidate []ReviewReason
	for _, task := range run.Tasks {
		if task.SectionOrdinal == 0 {
			forCandidate = append(forCandidate, task.Reason)
		}
	}

	if len(forCandidate) != 1 {
		t.Fatalf("candidate raised %d tasks (%v), want exactly 1", len(forCandidate), forCandidate)
	}
	if forCandidate[0] != ReasonTitleAmbiguity {
		t.Errorf("reason = %q, want %q", forCandidate[0], ReasonTitleAmbiguity)
	}
}

// TestTitleCandidate_NotSuppressedWhenFirstNodeIsDeeper is the limit that keeps
// the rule from breaking the other no-H1 paper.
//
// That DBA proposal's first node is "Abstract" at H4, with H2s beneath it. Being
// first is not enough to be a title; a title also has nothing above it. Without
// this condition, a correctly classified Abstract would be un-classified to fix
// a problem it does not have.
func TestTitleCandidate_NotSuppressedWhenFirstNodeIsDeeper(t *testing.T) {
	md := []byte("#### Abstract\n\nAbstract prose.\n\n" +
		"## 1. INTRODUCTION AND MOTIVATION\n\nOpening prose.\n\n" +
		"### 1.1 MACRO CONTEXT\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.HeadingCounts[1] != 0 {
		t.Fatalf("this test needs a document with no H1")
	}
	if doc.TitleCandidateOrdinal != -1 {
		t.Errorf("candidate ordinal = %d, want -1 — the first node sits below the shallowest level", doc.TitleCandidateOrdinal)
	}
	if doc.Nodes[0].Classification.Role != RoleAbstract {
		t.Errorf("Abstract = %q, want %q — a real section must keep its role", doc.Nodes[0].Classification.Role, RoleAbstract)
	}
}

// TestTitleCandidate_NotSuppressedWhenTitleIsIdentified. A document with a
// working H1 has nothing to ask about.
func TestTitleCandidate_NotSuppressedWhenTitleIsIdentified(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n## Methodology\n\nMethod prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleStatus != TitleIdentified {
		t.Fatalf("title status = %q, want %q", doc.TitleStatus, TitleIdentified)
	}
	if doc.TitleCandidateOrdinal != -1 {
		t.Errorf("candidate ordinal = %d, want -1", doc.TitleCandidateOrdinal)
	}

	run := NewRun(doc, "test", "hash")
	if len(run.Tasks) != 0 {
		t.Errorf("generated %d tasks, want 0: %+v", len(run.Tasks), run.Tasks)
	}
}

// TestTitleCandidate_NotSuppressedWhenFirstH1Matched covers §4's other
// unresolved-title case, which this rule deliberately does not touch.
//
// "# Introduction" is not the title, and §4 already says so. But it matched a
// keyword on its own terms, and suppressing it would discard a good answer to
// fix a different problem. The rule is scoped to documents with NO H1.
func TestTitleCandidate_NotSuppressedWhenFirstH1Matched(t *testing.T) {
	md := []byte("# Introduction\n\nOpening prose.\n\n## Methodology\n\nMethod prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleStatus != TitleUnresolved {
		t.Fatalf("title status = %q, want %q", doc.TitleStatus, TitleUnresolved)
	}
	if doc.TitleCandidateOrdinal != -1 {
		t.Errorf("candidate ordinal = %d, want -1 — an H1 exists, so this is not the no-H1 case", doc.TitleCandidateOrdinal)
	}
	if doc.Nodes[0].Classification.Role != RoleIntroduction {
		t.Errorf("first H1 = %q, want %q — its heading matched, so it keeps its answer", doc.Nodes[0].Classification.Role, RoleIntroduction)
	}
}

// TestTitleCandidate_NeverResolvedByChildren.
//
// The candidate is unresolved with no parent, which makes it exactly the shape
// the 2.3 consensus rule looks for. It must be excluded, for the same reason §4
// leaves a confirmed title's role null: a paper whose sections all report
// results is not itself "results". Without the guard this node would silently
// become results and the question would disappear.
func TestTitleCandidate_NeverResolvedByChildren(t *testing.T) {
	md := []byte("## Zorblatt frobnication in quixotic systems\n\nPreamble.\n\n" +
		"### Regression results\n\nProse.\n\n" +
		"### Robustness checks\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleCandidateOrdinal != 0 {
		t.Fatalf("candidate ordinal = %d, want 0", doc.TitleCandidateOrdinal)
	}
	if doc.Nodes[1].ParentOrdinal != 0 || doc.Nodes[2].ParentOrdinal != 0 {
		t.Fatalf("this test needs both sections parented to the candidate")
	}
	if doc.Nodes[1].Classification.Method != MethodRule || doc.Nodes[2].Classification.Method != MethodRule {
		t.Fatalf("this test needs both children resolved by rule")
	}

	if doc.Nodes[0].Classification.Status != StatusUnresolved {
		t.Errorf("candidate status = %q, want %q — its sections must not decide what the paper is",
			doc.Nodes[0].Classification.Status, StatusUnresolved)
	}
	if doc.Nodes[0].Classification.Role != "" {
		t.Errorf("candidate role = %q, want empty", doc.Nodes[0].Classification.Role)
	}
}
