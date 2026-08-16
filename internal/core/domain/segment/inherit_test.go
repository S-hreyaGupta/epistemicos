package segment

import "testing"

// TestInherit_UnmatchedChildTakesParentRole is the case that motivated the
// change: a subsection whose heading means nothing on its own, sitting under a
// parent that says exactly what it is.
func TestInherit_UnmatchedChildTakesParentRole(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 2 Literature review\n\nProse.\n\n" +
		"### 2.1 Zorblatt disclosure in supply chains\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	child := doc.Nodes[2]

	if child.Classification.Role != RoleLiteratureReview {
		t.Errorf("child role = %q, want %q", child.Classification.Role, RoleLiteratureReview)
	}
	if child.Classification.Status != StatusResolved {
		t.Errorf("child status = %q, want %q", child.Classification.Status, StatusResolved)
	}
	if child.Classification.Method != MethodInherited {
		t.Errorf("child method = %q, want %q — an inherited role must stay distinguishable from a matched one", child.Classification.Method, MethodInherited)
	}
	if child.Classification.ContentClass != ClassAnalytical {
		t.Errorf("child class = %q, want %q", child.Classification.ContentClass, ClassAnalytical)
	}
}

// TestInherit_NeverOverridesAMatch is the limit that matters most.
//
// "4.1 Regression results" under a methodology section is results, because its
// own heading says so. If position could overrule a keyword, the one piece of
// direct evidence about the section would lose to the one piece of indirect
// evidence.
func TestInherit_NeverOverridesAMatch(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 4 Methodology\n\nProse.\n\n" +
		"### 4.1 Regression results\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	child := doc.Nodes[2]

	if child.Classification.Role != RoleResults {
		t.Errorf("child role = %q, want %q — its own heading matched, so the parent must not overrule it", child.Classification.Role, RoleResults)
	}
	if child.Classification.Method != MethodRule {
		t.Errorf("child method = %q, want %q", child.Classification.Method, MethodRule)
	}
}

// TestInherit_NeverOverridesATie: a multi-role match is a real question with a
// real shortlist. Burying it under the parent's role would throw away the best
// information the reviewer has.
func TestInherit_NeverOverridesATie(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 4 Methodology\n\nProse.\n\n" +
		"### 4.1 Theoretical background and hypotheses derivation\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	child := doc.Nodes[2]

	if child.Classification.Status != StatusUnresolved {
		t.Fatalf("child status = %q, want %q — a tie must stay a question", child.Classification.Status, StatusUnresolved)
	}
	if len(child.Classification.CandidateRoles) != 2 {
		t.Errorf("candidates = %v, want the two that tied", child.Classification.CandidateRoles)
	}
}

// TestInherit_NotFromAnUnresolvedParent stops guesses inheriting from guesses.
func TestInherit_NotFromAnUnresolvedParent(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 2 Zorblatt considerations\n\nProse.\n\n" +
		"### 2.1 Quixotic frobnication\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.Nodes[1].Classification.Status != StatusUnresolved {
		t.Fatalf("the parent resolved unexpectedly; this test needs an unresolved parent")
	}
	if doc.Nodes[2].Classification.Status != StatusUnresolved {
		t.Errorf("child status = %q, want %q — nothing to inherit from an unresolved parent", doc.Nodes[2].Classification.Status, StatusUnresolved)
	}
}

// TestInherit_NotFromTheDocumentTitle is why "5 Empirical analysis" and
// "Appendix A" stayed questions on the real paper.
//
// The title has no role by design, so there is nothing to pass down — and that
// is the right answer, because sitting directly beneath the title tells a
// reviewer nothing about what a section does.
func TestInherit_NotFromTheDocumentTitle(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 5 Zorblatt analysis\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.Nodes[0].Kind != KindDocumentTitle {
		t.Fatalf("first node is not the title; this test needs one")
	}
	if doc.Nodes[1].Classification.Status != StatusUnresolved {
		t.Errorf("status = %q, want %q — the title has no role to inherit", doc.Nodes[1].Classification.Status, StatusUnresolved)
	}
}

// TestAppendix_UnmatchedSuffixResolvesStructurally.
//
// A bare "Appendix B" already resolved to Unknown with no question raised.
// Before this change, "Appendix B - <words we cannot parse>" became a question
// — so adding unparseable words turned a resolved answer into an unresolved
// one, which is backwards.
func TestAppendix_UnmatchedSuffixResolvesStructurally(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## Appendix A - Isolating extended supply chains\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	n := doc.Nodes[1]

	if n.Container != ContainerAppendix {
		t.Errorf("container = %q, want %q", n.Container, ContainerAppendix)
	}
	if n.AppendixLabel != "A" {
		t.Errorf("label = %q, want \"A\"", n.AppendixLabel)
	}
	if n.Classification.Role != RoleUnknown {
		t.Errorf("role = %q, want %q", n.Classification.Role, RoleUnknown)
	}
	if n.Classification.Status != StatusResolved {
		t.Errorf("status = %q, want %q", n.Classification.Status, StatusResolved)
	}
	if n.Classification.Method != MethodStructural {
		t.Errorf("method = %q, want %q", n.Classification.Method, MethodStructural)
	}

	// The suffix must still be recorded. This is what makes the change a
	// decision about the review queue rather than about what is kept — an
	// appendix with an unclassified suffix stays findable.
	if n.SemanticHeading == "" {
		t.Error("the suffix was discarded; it must remain in SemanticHeading so nothing is lost by not asking")
	}

	run := NewRun(doc, "test", "hash")
	for _, task := range run.Tasks {
		if task.SectionOrdinal == 1 {
			t.Errorf("the appendix raised a %s task", task.Reason)
		}
	}
}

// TestAppendix_MatchedSuffixIsStillNotClassified is the 2.5 reversal.
//
// Through 2.4 this heading resolved to RESULTS, because "robustness checks" is
// a results keyword. It no longer does, and the reason is that an appendix title
// says what the appendix is ABOUT rather than what it does. "Detailed Results of
// Model Selection" sounds like results and may equally be methodology that a
// reviewer asked to be moved out of the body. Which part of the paper an
// appendix supports is not recoverable from its title, so reading a role off it
// was reading confidence into a coincidence of vocabulary.
//
// This test exists in its inverted form on purpose. Deleting it would leave no
// record that the old behaviour was considered and rejected, and someone would
// eventually re-add suffix classification as an improvement.
func TestAppendix_MatchedSuffixIsStillNotClassified(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## Appendix B - Robustness checks\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	n := doc.Nodes[1]

	if n.Container != ContainerAppendix || n.AppendixLabel != "B" {
		t.Errorf("container/label = %q/%q, want appendix/B", n.Container, n.AppendixLabel)
	}
	if n.Classification.Role != RoleUnknown {
		t.Errorf("role = %q, want %q — the suffix matched a results keyword and must not be read as one", n.Classification.Role, RoleUnknown)
	}
	if n.Classification.Method != MethodStructural {
		t.Errorf("method = %q, want %q", n.Classification.Method, MethodStructural)
	}
	if n.Classification.ContentClass != ClassAnalytical {
		t.Errorf("class = %q, want %q", n.Classification.ContentClass, ClassAnalytical)
	}
	if n.SemanticHeading != "robustness checks" {
		t.Errorf("semantic heading = %q, want it retained — the suffix is not classified, but it is kept", n.SemanticHeading)
	}
}
