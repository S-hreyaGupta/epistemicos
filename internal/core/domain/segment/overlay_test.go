package segment

import (
	"strings"
	"testing"
)

// TestEffectiveFor_NoDecision: the machine determination stands, unresolved
// included. §8 is explicit that an unresolved node without a decision stays
// unresolved and is never silently inferred into an answer.
func TestEffectiveFor_NoDecision(t *testing.T) {
	resolved := SectionNode{Classification: Classification{
		Role: RoleMethodology, ContentClass: ClassAnalytical,
		Status: StatusResolved, Method: MethodRule,
	}}

	got := EffectiveFor(resolved, nil)
	if got.Role != RoleMethodology || got.Status != EffectiveResolved || got.FromReview {
		t.Errorf("resolved node: %+v", got)
	}

	unresolved := SectionNode{Classification: Classification{Status: StatusUnresolved}}

	got = EffectiveFor(unresolved, nil)
	if got.Role != "" {
		t.Errorf("unresolved role = %q, want empty — an unresolved node must not acquire a role by being read", got.Role)
	}
	if got.Status != EffectiveUnresolved {
		t.Errorf("unresolved status = %q, want %q", got.Status, EffectiveUnresolved)
	}
}

// TestEffectiveFor_DecisionWins is the authority order: a human overrides the
// machine, and the machine's own record is untouched by the overlay.
func TestEffectiveFor_DecisionWins(t *testing.T) {
	node := SectionNode{Classification: Classification{
		Role: RoleMethodology, ContentClass: ClassAnalytical,
		Status: StatusResolved, Method: MethodRule,
	}}

	decision := &ReviewDecision{
		AssignedRole:         RoleResults,
		AssignedContentClass: ClassAnalytical,
	}

	got := EffectiveFor(node, decision)

	if got.Role != RoleResults {
		t.Errorf("effective role = %q, want %q — a human decision overrides the machine", got.Role, RoleResults)
	}
	if got.Status != EffectiveReviewerConfirmed {
		t.Errorf("effective status = %q, want %q", got.Status, EffectiveReviewerConfirmed)
	}
	if !got.FromReview {
		t.Error("FromReview is false on a decision-derived classification")
	}

	// The node itself is untouched. Provenance is the point: "the machine said
	// methodology and a human overrode it" and "the machine said results" are
	// different facts and must stay distinguishable.
	if node.Classification.Role != RoleMethodology {
		t.Errorf("the node's stored role changed to %q; the overlay must not write back", node.Classification.Role)
	}
}

// TestEffectiveTitleFor covers the same authority order on the title axis.
func TestEffectiveTitleFor(t *testing.T) {
	run := Run{
		DocumentTitleText:    "A Study Of Things",
		DocumentTitleOrdinal: 0,
		DocumentTitleStatus:  TitleIdentified,
		DocumentTitleMethod:  MethodSingletonH1,
		NodeIDs:              []string{"node-0"},
	}

	got := EffectiveTitleFor(run, nil)
	if got.Text != "A Study Of Things" || got.Status != EffectiveStatus(TitleIdentified) {
		t.Errorf("machine title: %+v", got)
	}
	if got.NodeID != "node-0" {
		t.Errorf("title node id = %q, want %q", got.NodeID, "node-0")
	}

	decision := &ReviewDecision{
		AssignedDocumentTitleText:   "The Real Title",
		AssignedDocumentTitleNodeID: "node-3",
	}

	got = EffectiveTitleFor(run, decision)
	if got.Text != "The Real Title" {
		t.Errorf("effective title = %q, want %q", got.Text, "The Real Title")
	}
	if got.Status != EffectiveReviewerConfirmed {
		t.Errorf("effective title status = %q, want %q", got.Status, EffectiveReviewerConfirmed)
	}
	if got.Method != "human" {
		t.Errorf("effective title method = %q, want %q", got.Method, "human")
	}
	if run.DocumentTitleText != "A Study Of Things" {
		t.Error("the run's stored title changed; the overlay must not write back")
	}
}

// TestContextFor_TheTwoByteNode is the amendment's whole reason for existing.
//
// n004 — "2 Theoretical background and hypotheses derivation" — is the fixture's
// sole multi_role_match, the one genuine judgement call, and its own span is two
// bytes. Under the unamended rule a reviewer would open it and see a heading and
// nothing else.
func TestContextFor_TheTwoByteNode(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	// Locate the multi-role node by its classification rather than by index, so
	// the test survives a fixture change.
	target := -1
	for i, n := range doc.Nodes {
		if len(n.Classification.CandidateRoles) > 1 {
			target = i
			break
		}
	}
	if target < 0 {
		t.Fatal("no multi-role node in the fixture")
	}

	own := doc.Nodes[target].EndOffset - doc.Nodes[target].StartOffset
	if own > 32 {
		t.Fatalf("the multi-role node owns %d bytes, so this test is no longer exercising the case it was written for", own)
	}

	ctx, ok := ContextFor(doc.Nodes, target)
	if !ok {
		t.Fatal("ContextFor returned false for a valid ordinal")
	}

	body := ctx.Text(md)
	if len(body) <= own {
		t.Fatalf("context is %d bytes, no wider than the node's own %d — the amendment is not being applied", len(body), own)
	}

	// The children's text must be present: that is where the evidence for
	// theory-versus-introduction actually lives.
	if !strings.Contains(body, "Theoretical basis") {
		t.Error("the context omits the node's first child heading")
	}
	if !strings.Contains(body, "The moderating role of environmental dynamism") {
		t.Error("the context omits the node's last child; it must run to the end of the subtree")
	}

	// One ancestor: the document title.
	if len(ctx.AncestorHeadings) != 1 {
		t.Fatalf("ancestor headings = %v, want exactly one (the document title)", ctx.AncestorHeadings)
	}
}

// TestContextFor_AncestorHeadingsAreOutermostFirst checks the ordering and that
// ancestor BODY text is excluded.
//
// The exclusion is the part worth guarding. Ancestor bodies are unbounded — an
// introduction can run for pages — and including them would bury the section
// under review in text that rarely bears on the decision.
func TestContextFor_AncestorHeadingsAreOutermostFirst(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors and affiliations.\n\n" +
		"## Methodology\n\nParent body text that must not appear.\n\n" +
		"### Measures\n\nChild body.\n\n" +
		"#### Construct validity\n\nGrandchild body.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	// The H4 is the last node; its ancestors are H3, H2, H1.
	ctx, ok := ContextFor(doc.Nodes, len(doc.Nodes)-1)
	if !ok {
		t.Fatal("ContextFor returned false")
	}

	want := []string{"A Study Of Things", "Methodology", "Measures"}
	if len(ctx.AncestorHeadings) != len(want) {
		t.Fatalf("ancestor headings = %v, want %v", ctx.AncestorHeadings, want)
	}
	for i := range want {
		if ctx.AncestorHeadings[i] != want[i] {
			t.Errorf("ancestor %d = %q, want %q (outermost first)", i, ctx.AncestorHeadings[i], want[i])
		}
	}

	body := ctx.Text(md)
	if strings.Contains(body, "Parent body text that must not appear") {
		t.Error("the context includes ancestor body text; §8 says headings only")
	}
	if strings.Contains(body, "Authors and affiliations") {
		t.Error("the context includes the title node's body text")
	}
	if !strings.Contains(body, "Grandchild body") {
		t.Error("the context omits the node's own body")
	}
}

// TestContextFor_SkippedLevel is the case Alex's three-case formulation did not
// cover, and the reason the rule is stated by ancestry instead.
//
// The fixture's only H4 is the Abstract, which sits directly beneath the title
// with no H2 or H3 above it. A rule enumerated over heading levels — "for an
// H4, show the H2 heading and the H3 heading" — has nothing to show here.
func TestContextFor_SkippedLevel(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n#### Abstract\n\nAbstract body.\n\n## Introduction\n\nIntro body.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	ctx, ok := ContextFor(doc.Nodes, 1) // the H4
	if !ok {
		t.Fatal("ContextFor returned false")
	}

	if len(ctx.AncestorHeadings) != 1 {
		t.Fatalf("ancestor headings = %v, want exactly one — the H4's only ancestor is the title", ctx.AncestorHeadings)
	}
	if ctx.AncestorHeadings[0] != "A Study Of Things" {
		t.Errorf("ancestor = %q, want the document title", ctx.AncestorHeadings[0])
	}

	// The Abstract has no descendants, so its context must not run on into the
	// sibling H2 that follows it.
	if strings.Contains(ctx.Text(md), "Intro body") {
		t.Error("the context ran past the node's subtree into a sibling")
	}
}

// TestContextFor_LeafNodeIsItsOwnSpan: a node with no descendants gets no
// widening downward, only the ancestor headings.
func TestContextFor_LeafNodeIsItsOwnSpan(t *testing.T) {
	md := []byte("## Methodology\n\nMethod body.\n\n## Results\n\nResults body.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	ctx, ok := ContextFor(doc.Nodes, 0)
	if !ok {
		t.Fatal("ContextFor returned false")
	}

	if ctx.EndOffset != doc.Nodes[0].EndOffset {
		t.Errorf("context end = %d, want %d — a leaf must not extend past its own span", ctx.EndOffset, doc.Nodes[0].EndOffset)
	}
	if len(ctx.AncestorHeadings) != 0 {
		t.Errorf("ancestor headings = %v, want none for a top-level node", ctx.AncestorHeadings)
	}
}

// TestContextFor_EveryFixtureTaskHasUsableContext is the property that matters
// in practice: after the amendment, no review task presents an empty body.
//
// Before it, one of the six did.
func TestContextFor_EveryFixtureTaskHasUsableContext(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := NewRun(doc, "fixture", fixtureSHA256)

	for _, task := range run.Tasks {
		if task.SectionOrdinal < 0 {
			continue // title ambiguity, no section
		}

		ctx, ok := ContextFor(doc.Nodes, task.SectionOrdinal)
		if !ok {
			t.Fatalf("no context for task on node %d", task.SectionOrdinal)
		}

		body := strings.TrimSpace(ctx.Text(md))
		if len(body) < 64 {
			t.Errorf("task on node %d (%q) has only %d bytes of context; a reviewer cannot judge from that",
				task.SectionOrdinal, doc.Nodes[task.SectionOrdinal].HeadingRaw, len(body))
		}
	}
}

// TestContextFor_OutOfRange guards the boundary rather than panicking.
func TestContextFor_OutOfRange(t *testing.T) {
	nodes := []SectionNode{{Ordinal: 0}}

	if _, ok := ContextFor(nodes, -1); ok {
		t.Error("ContextFor accepted a negative ordinal")
	}
	if _, ok := ContextFor(nodes, 1); ok {
		t.Error("ContextFor accepted an ordinal past the end")
	}
}
