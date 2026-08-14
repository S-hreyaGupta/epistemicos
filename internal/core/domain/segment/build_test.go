package segment

import (
	"strings"
	"testing"
)

// TestBuild_Fixture is phase 4's done-condition and the first test that checks
// byte offsets against expected.json.
//
// Every earlier phase compared strings. This one compares the numbers that
// Step 4 will slice somebody's paper with, so it is where the span rule either
// holds or does not.
func TestBuild_Fixture(t *testing.T) {
	md := loadFixture(t)
	exp := loadExpected(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != len(exp.SectionNodes) {
		t.Fatalf("built %d nodes, want %d", len(doc.Nodes), len(exp.SectionNodes))
	}

	id := map[int]string{}
	ordinal := map[string]int{}
	for i, n := range exp.SectionNodes {
		id[i] = n.SectionID
		ordinal[n.SectionID] = i
	}

	for i, want := range exp.SectionNodes {
		got := doc.Nodes[i]

		t.Run(want.SectionID, func(t *testing.T) {
			if got.StartOffset != want.StartOffset {
				t.Errorf("start_offset = %d, want %d", got.StartOffset, want.StartOffset)
			}
			if got.EndOffset != want.EndOffset {
				t.Errorf("end_offset = %d, want %d", got.EndOffset, want.EndOffset)
			}
			if got.HeadingLevel != want.HeadingLevel {
				t.Errorf("heading_level = %d, want %d", got.HeadingLevel, want.HeadingLevel)
			}
			if string(got.Kind) != want.NodeKind {
				t.Errorf("node_kind = %q, want %q", got.Kind, want.NodeKind)
			}
			if got.HeadingRaw != want.HeadingRaw {
				t.Errorf("heading_raw = %q, want %q", got.HeadingRaw, want.HeadingRaw)
			}

			// Parent linkage, compared by section id so a failure names the
			// heading rather than an index.
			gotParent := ""
			if got.ParentOrdinal >= 0 {
				gotParent = id[got.ParentOrdinal]
			}
			wantParent := ""
			if want.ParentSectionID != nil {
				wantParent = *want.ParentSectionID
			}
			if gotParent != wantParent {
				t.Errorf("parent = %q, want %q", gotParent, wantParent)
			}

			if string(got.Classification.Role) != derefOrEmpty(want.PrimaryRole) {
				t.Errorf("primary_role = %q, want %q", got.Classification.Role, derefOrEmpty(want.PrimaryRole))
			}
			if string(got.Classification.Status) != want.ClassificationStatus {
				t.Errorf("classification_status = %q, want %q", got.Classification.Status, want.ClassificationStatus)
			}
		})
	}
}

// TestBuild_TitleIdentification covers §4 on the fixture: one H1, not itself
// resolving to a role, therefore the title by the singleton_h1 rule.
func TestBuild_TitleIdentification(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleStatus != TitleIdentified {
		t.Fatalf("title status = %q, want %q", doc.TitleStatus, TitleIdentified)
	}
	if doc.TitleMethod != MethodSingletonH1 {
		t.Errorf("title method = %q, want %q", doc.TitleMethod, MethodSingletonH1)
	}

	title, ok := doc.Title()
	if !ok {
		t.Fatal("title status is identified but Title() reports none")
	}
	if title.Ordinal != 0 {
		t.Errorf("title ordinal = %d, want 0", title.Ordinal)
	}
	if title.Kind != KindDocumentTitle {
		t.Errorf("title node kind = %q, want %q", title.Kind, KindDocumentTitle)
	}

	// The title carries no section role, and that is not a failure to classify.
	if title.Classification.Role != "" {
		t.Errorf("title role = %q, want empty — document_title is a node kind, not a role", title.Classification.Role)
	}
	if title.Classification.Status != StatusResolved {
		t.Errorf("title status = %q, want %q", title.Classification.Status, StatusResolved)
	}
	if title.Classification.ContentClass != ClassAdministrative {
		t.Errorf("title content class = %q, want %q", title.Classification.ContentClass, ClassAdministrative)
	}
}

// TestBuild_HeadingCounts checks §15's per-level counts, including the zeroes.
func TestBuild_HeadingCounts(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	want := map[int]int{1: 1, 2: 8, 3: 12, 4: 1, 5: 0, 6: 0}
	for level, n := range want {
		if doc.HeadingCounts[level] != n {
			t.Errorf("H%d count = %d, want %d", level, doc.HeadingCounts[level], n)
		}
	}
}

// TestBuild_SpansExcludeHeadingText is the assertion that pins the span rule
// independently of the fixture's numbers.
//
// Comparing offsets proves this implementation agrees with expected.json.
// Checking that no span contains its own heading text proves the RULE, so that
// if the fixture were ever regenerated wrongly the property would still be
// under test.
//
// A span begins at the newline ending its heading line, so its first byte is
// that newline and its content starts on the following line.
func TestBuild_SpansExcludeHeadingText(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	for _, n := range doc.Nodes {
		if n.StartOffset >= n.EndOffset {
			continue // empty span, nothing to check
		}

		if md[n.StartOffset] != '\n' {
			t.Errorf("node %d (%q): span begins with %q, want a newline — the span must start at the newline ending its heading line", n.Ordinal, n.HeadingRaw, md[n.StartOffset])
		}

		firstLine := n.Text(md)
		if i := strings.IndexByte(firstLine[1:], '\n'); i >= 0 {
			firstLine = firstLine[1 : 1+i]
		}
		if strings.Contains(firstLine, n.HeadingRaw) {
			t.Errorf("node %d: span opens with its own heading text %q", n.Ordinal, n.HeadingRaw)
		}
	}
}

// TestBuild_UnownedBytesAreOnlyPreambleAndHeadings states the coverage property
// exactly, so the 1,945 unowned bytes cannot later be mistaken for loss.
//
// §3's non-overlap rule is about ownership collision, not coverage: no byte is
// claimed twice, and some bytes are claimed by nobody. The unowned bytes must
// be exactly two things — the preamble before the first heading, and the
// heading lines themselves. Any OTHER gap would be a real defect, and without
// this test it would look identical to the intended ones.
func TestBuild_UnownedBytesAreOnlyPreambleAndHeadings(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	owned := make([]bool, len(md))
	for _, n := range doc.Nodes {
		for i := n.StartOffset; i < n.EndOffset; i++ {
			if owned[i] {
				t.Fatalf("byte %d is owned by more than one node", i)
			}
			owned[i] = true
		}
	}

	headings := detectHeadings(md)
	if len(headings) == 0 {
		t.Fatal("no headings detected")
	}

	// Every unowned byte must fall before the first heading, or inside a
	// heading line — that is, between a '#' and the newline ending its line.
	preambleEnd := headings[0].ByteStart

	inHeadingLine := make([]bool, len(md))
	for _, h := range headings {
		end := h.TextStop
		for end < len(md) && md[end] != '\n' {
			end++
		}
		for i := h.ByteStart; i < end && i < len(md); i++ {
			inHeadingLine[i] = true
		}
	}

	for i := range md {
		if owned[i] {
			continue
		}
		if i < preambleEnd || inHeadingLine[i] {
			continue
		}
		t.Fatalf("byte %d is owned by no node and is neither preamble nor part of a heading line — this is real loss, not the intended gap", i)
	}
}

// TestBuild_NoHeadings covers §5's headless case: the one node in the system
// that exists without a detected heading.
func TestBuild_NoHeadings(t *testing.T) {
	md := []byte("This document has no headings at all.\n\nJust prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != 1 {
		t.Fatalf("built %d nodes, want exactly 1", len(doc.Nodes))
	}

	n := doc.Nodes[0]
	if n.StartOffset != 0 || n.EndOffset != len(md) {
		t.Errorf("span = [%d,%d), want [0,%d) — the node must cover the whole document", n.StartOffset, n.EndOffset, len(md))
	}
	if n.Classification.Role != RoleUnknown {
		t.Errorf("role = %q, want %q", n.Classification.Role, RoleUnknown)
	}
	if n.Classification.Status != StatusResolved {
		t.Errorf("status = %q, want %q — processing an unstructured document is a deliberate rule, not a failure", n.Classification.Status, StatusResolved)
	}
	if doc.TitleStatus != TitleUnresolved {
		t.Errorf("title status = %q, want %q", doc.TitleStatus, TitleUnresolved)
	}
}

// TestBuild_FirstH1ResolvingToARoleIsNotTheTitle covers §4 case 3.
//
// A document opening "# Introduction" has no title. §4 is explicit that nothing
// is auto-promoted and that a later H1 never becomes the title by elimination,
// so the honest answer is that the title is unresolved — which §8 turns into a
// review task rather than a guess.
func TestBuild_FirstH1ResolvingToARoleIsNotTheTitle(t *testing.T) {
	md := []byte("# Introduction\n\nOpening prose.\n\n## Methodology\n\nMethod prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleStatus != TitleUnresolved {
		t.Errorf("title status = %q, want %q — an H1 that classifies as a section is that section, not the title", doc.TitleStatus, TitleUnresolved)
	}
	if _, ok := doc.Title(); ok {
		t.Error("Title() returned a node for a document whose first H1 resolves to a role")
	}

	if doc.Nodes[0].Kind != KindSection {
		t.Errorf("first node kind = %q, want %q", doc.Nodes[0].Kind, KindSection)
	}
	if doc.Nodes[0].Classification.Role != RoleIntroduction {
		t.Errorf("first node role = %q, want %q", doc.Nodes[0].Classification.Role, RoleIntroduction)
	}
}

// TestBuild_MultipleH1s covers §4 case 2: only the first H1 is a candidate, and
// later ones are ordinary section nodes.
func TestBuild_MultipleH1s(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n# Methodology\n\nMethod prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleStatus != TitleIdentified {
		t.Fatalf("title status = %q, want %q", doc.TitleStatus, TitleIdentified)
	}
	if doc.TitleMethod != MethodStructuralRule {
		t.Errorf("title method = %q, want %q — two H1s means the first was taken by rule, not by being the only one", doc.TitleMethod, MethodStructuralRule)
	}
	if doc.TitleOrdinal != 0 {
		t.Errorf("title ordinal = %d, want 0", doc.TitleOrdinal)
	}

	// The second H1 classifies like anything else.
	if doc.Nodes[1].Kind != KindSection {
		t.Errorf("second H1 kind = %q, want %q", doc.Nodes[1].Kind, KindSection)
	}
	if doc.Nodes[1].Classification.Role != RoleMethodology {
		t.Errorf("second H1 role = %q, want %q", doc.Nodes[1].Classification.Role, RoleMethodology)
	}
	if doc.Nodes[1].HeadingLevel != 1 {
		t.Errorf("second H1 level = %d, want 1 — the level is recorded even though the node is anomalous", doc.Nodes[1].HeadingLevel)
	}
}

// TestBuild_H5AndH6ProduceNoNode covers §3's exclusion. Their text must remain
// inside the enclosing node's span rather than vanishing.
func TestBuild_H5AndH6ProduceNoNode(t *testing.T) {
	md := []byte("## Methodology\n\nIntro prose.\n\n##### Deep detail\n\nDetail prose.\n\n## Results\n\nResults prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != 2 {
		t.Fatalf("built %d nodes, want 2 — H5 must not produce one", len(doc.Nodes))
	}
	if doc.HeadingCounts[5] != 1 {
		t.Errorf("H5 count = %d, want 1 — H5s are counted even though they produce no node", doc.HeadingCounts[5])
	}

	// The H5's heading and its text stay inside the methodology span.
	text := doc.Nodes[0].Text(md)
	if !strings.Contains(text, "Deep detail") {
		t.Error("the H5 heading is not inside its enclosing node's span; excluding it from node creation must not remove its text")
	}
	if !strings.Contains(text, "Detail prose.") {
		t.Error("the H5's body is not inside its enclosing node's span")
	}
}

// TestBuild_EmptySectionStillClassifies covers §5: a heading with no body is a
// node with an empty span, and classification is heading-based so the empty
// body is irrelevant to it.
//
// This is a change from 1.1, which marked empty sections unresolved.
func TestBuild_EmptySectionStillClassifies(t *testing.T) {
	md := []byte("## Methodology\n## Results\n\nResults prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != 2 {
		t.Fatalf("built %d nodes, want 2", len(doc.Nodes))
	}
	if doc.Nodes[0].Classification.Role != RoleMethodology {
		t.Errorf("empty section role = %q, want %q", doc.Nodes[0].Classification.Role, RoleMethodology)
	}
	if doc.Nodes[0].Classification.Status != StatusResolved {
		t.Errorf("empty section status = %q, want %q", doc.Nodes[0].Classification.Status, StatusResolved)
	}
}

// TestBuild_ParentsSkipMissingLevels covers the linkage case the fixture itself
// exercises: an H4 with no H2 or H3 above it hangs off the H1.
//
// v2.1 §8 makes the document-title node explicitly eligible as a parent, and
// this is that rule in action. Parentage is structural position only and
// implies nothing semantic.
func TestBuild_ParentsSkipMissingLevels(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n#### Abstract\n\nAbstract prose.\n\n## Introduction\n\nIntro prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != 3 {
		t.Fatalf("built %d nodes, want 3", len(doc.Nodes))
	}
	if doc.Nodes[1].ParentOrdinal != 0 {
		t.Errorf("H4 parent = %d, want 0 — with no H2 or H3 above it, the nearest ancestor is the title node", doc.Nodes[1].ParentOrdinal)
	}
	if doc.Nodes[2].ParentOrdinal != 0 {
		t.Errorf("H2 parent = %d, want 0", doc.Nodes[2].ParentOrdinal)
	}
}

// TestBuild_SiblingSubtreesDoNotCross guards the scope reset in linkParents.
//
// Without clearing deeper levels when a shallower heading opens, the second H3
// would find the first H3's slot still populated and could parent outside its
// own subtree — producing a tree that looks plausible and is wrong.
func TestBuild_SiblingSubtreesDoNotCross(t *testing.T) {
	md := []byte("## Methodology\n\nA.\n\n### Measures\n\nB.\n\n## Results\n\nC.\n\n### Descriptives\n\nD.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if len(doc.Nodes) != 4 {
		t.Fatalf("built %d nodes, want 4", len(doc.Nodes))
	}
	if doc.Nodes[1].ParentOrdinal != 0 {
		t.Errorf("first H3 parent = %d, want 0", doc.Nodes[1].ParentOrdinal)
	}
	if doc.Nodes[3].ParentOrdinal != 2 {
		t.Errorf("second H3 parent = %d, want 2 — it must belong to the second H2, not the first", doc.Nodes[3].ParentOrdinal)
	}
}

// TestValidateNoSilentLoss_DetectsAMissingNode is §10's negative test, required
// by AC-09.
//
// Every other test proves the invariant passes when nothing is wrong, which
// says nothing about whether it would notice if something were. This drops a
// node and asserts the check fires.
func TestValidateNoSilentLoss_DetectsAMissingNode(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	headings := detectHeadings(md)

	damaged := doc
	damaged.Nodes = doc.Nodes[:len(doc.Nodes)-1]

	err = ValidateNoSilentLoss(damaged, headings)
	if err == nil {
		t.Fatal("dropping a node did not violate the invariant; a segmentation that silently loses a section would be reported as complete")
	}
	if !strings.Contains(err.Error(), "silent_loss_invariant") {
		t.Errorf("error = %q, want it to name silent_loss_invariant", err)
	}
}
