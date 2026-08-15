package segment

import "testing"

// TestConsensus_UnanimousChildrenResolveTheParent is the case that motivated the
// rule, reduced to its shape.
//
// A heading that means nothing to the role table, sitting too high in the
// document to inherit anything downward, with subsections that all say the same
// thing. The real one was "5 EMPIRICAL ANALYSIS" over "5.1 Regression results",
// "5.2 Robustness checks" and "5.3 Robustness checks".
func TestConsensus_UnanimousChildrenResolveTheParent(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 5 Zorblatt analysis\n\nProse.\n\n" +
		"### 5.1 Regression results\n\nProse.\n\n" +
		"### 5.2 Robustness checks\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	parent := doc.Nodes[1]

	if parent.Classification.Role != RoleResults {
		t.Errorf("parent role = %q, want %q", parent.Classification.Role, RoleResults)
	}
	if parent.Classification.Status != StatusResolved {
		t.Errorf("parent status = %q, want %q", parent.Classification.Status, StatusResolved)
	}
	if parent.Classification.Method != MethodChildConsensus {
		t.Errorf("parent method = %q, want %q — a role read off the children must stay distinguishable from one read off the heading", parent.Classification.Method, MethodChildConsensus)
	}
	if parent.Classification.ContentClass != ClassAnalytical {
		t.Errorf("parent class = %q, want %q", parent.Classification.ContentClass, ClassAnalytical)
	}

	// The point of the rule is to remove the question, not to answer it twice.
	run := NewRun(doc, "test", "hash")
	for _, task := range run.Tasks {
		if task.SectionOrdinal == 1 {
			t.Errorf("the parent still raised a %s task", task.Reason)
		}
	}
}

// TestConsensus_OneDissenterBlocksIt.
//
// Subsections that disagree are the strongest reason to involve a person, so
// they must not be the moment the machine decides for itself. A majority rule
// would silence exactly the disagreement that makes the section interesting.
func TestConsensus_OneDissenterBlocksIt(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 5 Zorblatt analysis\n\nProse.\n\n" +
		"### 5.1 Regression results\n\nProse.\n\n" +
		"### 5.2 Data collection\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.Nodes[2].Classification.Role != RoleResults {
		t.Fatalf("first child = %q, want results; this test needs children that disagree", doc.Nodes[2].Classification.Role)
	}
	if doc.Nodes[3].Classification.Role != RoleMethodology {
		t.Fatalf("second child = %q, want methodology; this test needs children that disagree", doc.Nodes[3].Classification.Role)
	}

	if doc.Nodes[1].Classification.Status != StatusUnresolved {
		t.Errorf("parent status = %q, want %q — its subsections disagree, which is a question, not an answer", doc.Nodes[1].Classification.Status, StatusUnresolved)
	}
}

// TestConsensus_OneChildIsNotAgreement.
//
// With a single subsection there is no agreement, only one data point that
// happens to be nested. A lone subsection is as likely to specialise its parent
// as to describe it, and calling that consensus would dress one weak signal in
// the language of several.
func TestConsensus_OneChildIsNotAgreement(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 5 Zorblatt analysis\n\nProse.\n\n" +
		"### 5.1 Regression results\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.Nodes[2].Classification.Role != RoleResults {
		t.Fatalf("the only child did not resolve; this test needs it to")
	}
	if doc.Nodes[1].Classification.Status != StatusUnresolved {
		t.Errorf("parent status = %q, want %q — one child is not a consensus", doc.Nodes[1].Classification.Status, StatusUnresolved)
	}
}

// TestConsensus_NeverOverridesAMatch is the limit that matters most, and it is
// the same limit the downward rule has.
//
// "4 Methodology" says what it is. Subsections reporting results underneath it
// are entirely ordinary — a methodology section can end by showing what the
// method produced — and letting them rewrite the parent would lose the one piece
// of direct evidence in favour of several pieces of indirect evidence.
func TestConsensus_NeverOverridesAMatch(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 4 Methodology\n\nProse.\n\n" +
		"### 4.1 Regression results\n\nProse.\n\n" +
		"### 4.2 Robustness checks\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	parent := doc.Nodes[1]

	if parent.Classification.Role != RoleMethodology {
		t.Errorf("parent role = %q, want %q — its own heading matched, so its children must not overrule it", parent.Classification.Role, RoleMethodology)
	}
	if parent.Classification.Method != MethodRule {
		t.Errorf("parent method = %q, want %q", parent.Classification.Method, MethodRule)
	}
}

// TestConsensus_NeverOverridesATie.
//
// A multi-role match carries a shortlist a reviewer can act on. Replacing it
// with the children's role would trade a good question for a plausible answer,
// and the shortlist is the most useful thing anyone has about that heading.
func TestConsensus_NeverOverridesATie(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 2 Theoretical background and hypotheses derivation\n\nProse.\n\n" +
		"### 2.1 Regression results\n\nProse.\n\n" +
		"### 2.2 Robustness checks\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	parent := doc.Nodes[1]

	if parent.Classification.Status != StatusUnresolved {
		t.Fatalf("parent status = %q, want %q — a tie must stay a question", parent.Classification.Status, StatusUnresolved)
	}
	if len(parent.Classification.CandidateRoles) != 2 {
		t.Errorf("candidates = %v, want the two that tied", parent.Classification.CandidateRoles)
	}
}

// TestConsensus_UnknownChildrenDoNotCount.
//
// §7's Unknown is a placeholder meaning "this heading carries no semantic
// content", not a role. A parent of two bare appendices has learned nothing
// about itself, and a rule that counted them would report that ignorance as
// agreement.
func TestConsensus_UnknownChildrenDoNotCount(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 5 Zorblatt analysis\n\nProse.\n\n" +
		"### Appendix A\n\nProse.\n\n" +
		"### Appendix B\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	for _, i := range []int{2, 3} {
		if doc.Nodes[i].Classification.Role != RoleUnknown {
			t.Fatalf("node %d = %q, want Unknown; this test needs bare containers", i, doc.Nodes[i].Classification.Role)
		}
	}

	if doc.Nodes[1].Classification.Status != StatusUnresolved {
		t.Errorf("parent status = %q, want %q — two Unknowns agreeing is not evidence", doc.Nodes[1].Classification.Status, StatusUnresolved)
	}
}

// TestConsensus_DoesNotChain is the property that keeps the rule honest.
//
// Consensus is evidence only because each child reached its role independently,
// from its own heading. A child that was ITSELF resolved by consensus is a guess
// one hop further from the document, and letting it vote would turn a single
// original fact into apparent corroboration at every level above it.
//
// Here 2.1 and 2.2 both resolve by consensus from their own subsections. Their
// parent must not then resolve from them.
func TestConsensus_DoesNotChain(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n" +
		"## 2 Zorblattery\n\nProse.\n\n" +
		"### 2.1 Frobnication\n\nProse.\n\n" +
		"#### 2.1.1 Regression results\n\nProse.\n\n" +
		"#### 2.1.2 Robustness checks\n\nProse.\n\n" +
		"### 2.2 Quixotics\n\nProse.\n\n" +
		"#### 2.2.1 Empirical results\n\nProse.\n\n" +
		"#### 2.2.2 Qualitative results\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	for _, i := range []int{2, 5} {
		if doc.Nodes[i].Classification.Method != MethodChildConsensus {
			t.Fatalf("node %d (%q) method = %q, want %q; this test needs both middle nodes resolved by consensus",
				i, doc.Nodes[i].HeadingRaw, doc.Nodes[i].Classification.Method, MethodChildConsensus)
		}
	}

	if doc.Nodes[1].Classification.Status != StatusUnresolved {
		t.Errorf("grandparent status = %q, want %q — its children are guesses, and guesses do not corroborate each other",
			doc.Nodes[1].Classification.Status, StatusUnresolved)
	}
}

// TestConsensus_NeverTheDocumentTitle.
//
// A paper whose every section reported results would not make the paper
// "results". §4 leaves the title's role null on purpose, and the two-axis model
// exists so the title never has to pretend to a role it does not have.
func TestConsensus_NeverTheDocumentTitle(t *testing.T) {
	md := []byte("# Zorblatt frobnication in quixotic systems\n\nAuthors.\n\n" +
		"## Regression results\n\nProse.\n\n" +
		"## Robustness checks\n\nProse.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	title := doc.Nodes[0]

	if title.Kind != KindDocumentTitle {
		t.Fatalf("first node is not the title; this test needs one")
	}
	if title.ParentOrdinal != -1 {
		t.Fatalf("the title has a parent; this test assumes it is the root")
	}
	if doc.Nodes[1].Classification.Role != RoleResults || doc.Nodes[2].Classification.Role != RoleResults {
		t.Fatalf("the two sections did not both resolve to results; this test needs them to")
	}

	if title.Classification.Role != "" {
		t.Errorf("title role = %q, want empty — the title takes no role, however unanimous its sections are", title.Classification.Role)
	}
	if title.Classification.Method != MethodStructural {
		t.Errorf("title method = %q, want %q", title.Classification.Method, MethodStructural)
	}
}

// TestConsensus_DoesNotDisturbTheFixture.
//
// The reference fixture must be unchanged by this rule, and for a reason worth
// asserting rather than assuming: its one multi-role heading is the parent of
// its four zero-match ones, so both of the first two limits are engaged at once.
// If either weakens, this test notices before the fixture is quietly rewritten
// to match.
func TestConsensus_DoesNotDisturbTheFixture(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := NewRun(doc, "test", fixtureSHA256)

	if len(run.Tasks) != 5 {
		t.Errorf("fixture produced %d tasks, want 5 — the consensus rule must not touch it", len(run.Tasks))
	}
	for _, n := range doc.Nodes {
		if n.Classification.Method == MethodChildConsensus {
			t.Errorf("fixture node %q resolved by consensus; nothing in it should", n.HeadingRaw)
		}
	}
}
