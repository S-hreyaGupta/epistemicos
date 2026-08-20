package segment

import (
	"bytes"
	"strings"
	"testing"
)

// A bibliography Mathpix left as plain text, in the shape all four affected
// papers share: the word alone on a line, then entries.
const plainTextBibliography = "# A Study Of Things\n\n" +
	"## 3 Methodology\n\nWe surveyed 200 firms.\n\n" +
	"## 4 Discussion\n\nThe findings suggest a relationship.\n\n" +
	"References\n" +
	"Alvord, S., Brown, L., & Letts, C. (2004). Social entrepreneurship and transformation.\n" +
	"Austin, J., Stevenson, H., & Wei-Skiller, J. (2006). Social and commercial entrepreneurship.\n" +
	"Avlonitis, G., & Salavou, H. (2007). Entrepreneurial orientation of SMEs.\n" +
	"Bacq, S., & Janssen, F. (2011). The multiple faces of social entrepreneurship.\n"

// TestBuild_RecoversAPlainTextReferencesHeading is the whole of 2.9.
//
// Four of the ten ingested papers look exactly like this. Before 2.9 the
// bibliography was absorbed by "4 Discussion", which on the real papers left
// sections that were 85% to 91% reference list.
func TestBuild_RecoversAPlainTextReferencesHeading(t *testing.T) {
	doc, err := Build([]byte(plainTextBibliography))
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	var refs *SectionNode
	for i := range doc.Nodes {
		if doc.Nodes[i].Classification.Role == RoleReferences {
			refs = &doc.Nodes[i]
		}
	}
	if refs == nil {
		t.Fatalf("no references node was recovered; nodes are %v", roles(doc.Nodes))
	}

	if refs.HeadingSource != HeadingInferred {
		t.Errorf("heading source = %q, want %q — nothing may pretend this was a real heading",
			refs.HeadingSource, HeadingInferred)
	}
	if refs.Classification.ContentClass != ClassCitationSource {
		t.Errorf("content class = %q, want %q", refs.Classification.ContentClass, ClassCitationSource)
	}
	if refs.HeadingLevel != 2 {
		t.Errorf("level = %d, want 2 — a bibliography is a section, not the document title", refs.HeadingLevel)
	}

	// The point of the exercise: Discussion must no longer own the bibliography.
	var discussion *SectionNode
	for i := range doc.Nodes {
		if doc.Nodes[i].Classification.Role == RoleDiscussion {
			discussion = &doc.Nodes[i]
		}
	}
	if discussion == nil {
		t.Fatal("the discussion section disappeared")
	}
	body := plainTextBibliography[discussion.StartOffset:discussion.EndOffset]
	if strings.Contains(body, "Alvord") {
		t.Errorf("discussion still contains the bibliography:\n%q", body)
	}
	if !strings.Contains(body, "findings suggest") {
		t.Errorf("discussion lost its own text:\n%q", body)
	}
}

// TestInferReferences_NotWhenARealHeadingExists. Six of the ten papers have a
// proper heading and must be untouched by 2.9.
func TestInferReferences_NotWhenARealHeadingExists(t *testing.T) {
	md := "## 4 Discussion\n\nProse.\n\n## References\n\nSmith, J. (2019). A paper.\n" +
		"Jones, B. (2020). Another paper.\nLee, C. (2021). A third paper.\n"

	doc, err := Build([]byte(md))
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	n := 0
	for _, node := range doc.Nodes {
		if node.Classification.Role == RoleReferences {
			n++
			if node.HeadingSource != HeadingDetected {
				t.Errorf("a real heading was marked %q", node.HeadingSource)
			}
		}
	}
	if n != 1 {
		t.Errorf("got %d references nodes, want exactly 1 — a second would be invented", n)
	}
}

// TestInferReferences_RefusesWithoutEntriesBelow.
//
// "References" in a sentence, or as a stray line with nothing bibliographic
// under it, must not split a section in half. A false positive here mislabels
// real content, which is worse than the problem 2.9 solves.
func TestInferReferences_RefusesWithoutEntriesBelow(t *testing.T) {
	cases := []struct {
		name, md string
	}{
		{"nothing below it", "## 4 Discussion\n\nProse.\n\nReferences\n"},
		{"only prose below", "## 4 Discussion\n\nProse.\n\nReferences\nWe discuss the implications at length here.\nAnd continue for a while.\nAnd a little more.\n"},
		{"the word inside a sentence", "## 4 Discussion\n\nThe author makes references to prior work (2019). And again (2020). And once more (2021).\n"},
		{"too few entries", "## 4 Discussion\n\nProse.\n\nReferences\nSmith, J. (2019). A paper.\nJones, B. (2020). Another.\n"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			doc, err := Build([]byte(c.md))
			if err != nil {
				t.Fatalf("Build: %v", err)
			}
			for _, n := range doc.Nodes {
				if n.HeadingSource == HeadingInferred {
					t.Errorf("invented a heading from %q", n.HeadingRaw)
				}
			}
		})
	}
}

// TestInferReferences_AcceptedTitles walks EVERY title the role table knows,
// rather than a list written here.
//
// The hard-coded version of this list is what caught the original bug: it
// contained "literature cited", the role table did not, and the rule happily
// recovered a heading that then could not be classified — an unresolved node and
// a review task asking a human about a bibliography. Deriving both from
// keywordToRole is what makes that impossible; this test is what proves they are
// still derived from it.
func TestInferReferences_AcceptedTitles(t *testing.T) {
	entries := "\nSmith, J. (2019). A paper.\nJones, B. (2020). Another paper.\nLee, C. (2021). A third paper.\n"

	var titles []string
	for keyword, role := range keywordToRole {
		if role == RoleReferences {
			titles = append(titles, keyword)
		}
	}
	if len(titles) == 0 {
		t.Fatal("the role table has no references keywords; this test is checking nothing")
	}
	// Decorations the rule tolerates, checked against a real keyword.
	titles = append(titles, "References:", "7. References", "REFERENCES")

	for _, title := range titles {
		t.Run(title, func(t *testing.T) {
			doc, err := Build([]byte("## 4 Discussion\n\nProse.\n\n" + title + entries))
			if err != nil {
				t.Fatalf("Build: %v", err)
			}
			for _, n := range doc.Nodes {
				if n.HeadingSource == HeadingInferred && n.Classification.Role == RoleReferences {
					return
				}
			}
			t.Errorf("%q was not recovered; roles are %v", title, roles(doc.Nodes))
		})
	}
}

// TestInferReferences_TakesTheLastCandidate. A paper may say "References" in its
// methods section; the bibliography is the one at the end.
func TestInferReferences_TakesTheLastCandidate(t *testing.T) {
	md := "## 3 Method\n\nProse.\n\nReferences\nWe list our sources below in 2019 style.\n" +
		"Following the 2020 convention.\nAnd the 2021 update.\n\n" +
		"## 4 Discussion\n\nMore prose.\n\nReferences\n" +
		"Smith, J. (2019). A paper.\nJones, B. (2020). Another.\nLee, C. (2021). A third.\n"

	doc, err := Build([]byte(md))
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	n := 0
	for _, node := range doc.Nodes {
		if node.HeadingSource == HeadingInferred {
			n++
			if node.StartOffset < len(md)/2 {
				t.Errorf("took the earlier candidate at offset %d", node.StartOffset)
			}
		}
	}
	if n != 1 {
		t.Errorf("inferred %d headings, want exactly 1 per document", n)
	}
}

// TestInferReferences_SurvivesTheLossInvariant. §10 counts detected headings
// against nodes, so an inferred heading must be part of the same set or the run
// fails.
func TestInferReferences_SurvivesTheLossInvariant(t *testing.T) {
	doc, err := Build([]byte(plainTextBibliography))
	if err != nil {
		t.Fatalf("Build failed the loss invariant: %v", err)
	}
	// title + methodology + discussion + references
	if len(doc.Nodes) != 4 {
		t.Errorf("got %d nodes, want 4: %v", len(doc.Nodes), roles(doc.Nodes))
	}
}

// TestInferReferences_DoesNotDisturbTheTitle.
//
// The inferred heading is H2, never H1. An H1 would create a second
// document-title-level heading, flipping the title from singleton_h1 to
// structural_rule and asserting that a bibliography sits at the same level as
// the paper's name.
func TestInferReferences_DoesNotDisturbTheTitle(t *testing.T) {
	doc, err := Build([]byte(plainTextBibliography))
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if doc.TitleStatus != TitleIdentified {
		t.Errorf("title status = %q, want %q", doc.TitleStatus, TitleIdentified)
	}
	if doc.TitleMethod != MethodSingletonH1 {
		t.Errorf("title method = %q, want %q — the inferred heading added a second H1",
			doc.TitleMethod, MethodSingletonH1)
	}
	if doc.HeadingCounts[1] != 1 {
		t.Errorf("H1 count = %d, want 1", doc.HeadingCounts[1])
	}
}

// TestValidateOffsetsOnRuneBoundaries is the price of choosing byte offsets.
//
// Bytes are the right choice — the hash is over bytes, Go slices by bytes, and
// the offsets only ever index the document they came from. The one thing bytes
// can do that code points cannot is split a character, so the run checks.
func TestValidateOffsetsOnRuneBoundaries(t *testing.T) {
	md := []byte("# Título\n\nProse with café and naïve.\n\n## Método\n\nMore prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build rejected a document with accented headings: %v", err)
	}
	if err := ValidateOffsetsOnRuneBoundaries(doc, md); err != nil {
		t.Errorf("real spans failed the boundary check: %v", err)
	}

	// A span deliberately moved into the middle of "í" must be caught.
	i := bytes.IndexRune(md, 'í')
	if i < 0 {
		t.Fatal("this test needs a multi-byte character in the document")
	}
	damaged := doc
	damaged.Nodes = append([]SectionNode(nil), doc.Nodes...)
	damaged.Nodes[0].StartOffset = i + 1

	err = ValidateOffsetsOnRuneBoundaries(damaged, md)
	if err == nil {
		t.Fatal("a span starting inside a multi-byte character was accepted")
	}
	if !strings.Contains(err.Error(), "multi-byte") {
		t.Errorf("error = %q, want it to name the problem", err)
	}
}

func roles(nodes []SectionNode) []string {
	out := make([]string, 0, len(nodes))
	for _, n := range nodes {
		r := string(n.Classification.Role)
		if r == "" {
			r = "-"
		}
		if n.HeadingSource == HeadingInferred {
			r += "*"
		}
		out = append(out, r)
	}
	return out
}
