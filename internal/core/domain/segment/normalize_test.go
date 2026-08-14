package segment

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// TestNormalize covers §6 step 1 on inputs OCR actually produces, rather than
// on tidy examples.
func TestNormalize(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"already normal", "introduction", "introduction"},
		{"case folded", "INTRODUCTION", "introduction"},
		{"surrounding space", "  Discussion  ", "discussion"},
		{"internal run collapsed", "Results   and    discussion", "results and discussion"},
		{"tab treated as space", "Data\tavailability", "data availability"},
		{"newline treated as space", "Conflict of\ninterest", "conflict of interest"},
		{"trailing colon", "Methodology:", "methodology"},
		{"trailing period", "Conclusion.", "conclusion"},
		{"trailing colon and space", "Abstract : ", "abstract"},

		// Identifier and trailing punctuation together. Normalize leaves the
		// identifier alone — that is step 2's job — and must not disturb the
		// interior while trimming the tail.
		{"identifier retained", "3. Methodology:", "3. methodology"},

		// Unicode case folding. A byte-wise fold would leave the accented
		// capital untouched and the string would never match the table.
		{"non-ascii folded", "RÉSULTATS", "résultats"},

		{"empty", "", ""},
		{"punctuation only", ":.", ""},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := Normalize(c.in); got != c.want {
				t.Errorf("Normalize(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}

// TestStripIdentifiers covers §6 step 2, including the cases where the rule
// must NOT fire. The negative cases carry the weight here: an over-eager
// stripper silently deletes the first word of a heading and the resulting
// misclassification looks like a keyword problem.
func TestStripIdentifiers(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"numeric single", "4 results", "results"},
		{"numeric dotted", "2.1 sample and procedure", "sample and procedure"},
		{"numeric dotted with period", "2.1. sample and procedure", "sample and procedure"},
		{"numeric deep", "4.2.1 measurement model", "measurement model"},
		{"numeric with colon", "3: methodology", "methodology"},
		{"section word", "section 4: results", "results"},
		{"section word with letter", "section 4a. results", "results"},
		{"roman lower", "iv. results", "results"},
		{"roman bracket", "iii) discussion", "discussion"},
		{"alphabetic", "a. methods", "methods"},
		{"alphabetic bracket", "b) results", "results"},
		{"nothing to strip", "introduction", "introduction"},

		// Parent independence, which is the property §6 exists to produce.
		// These two must reduce to the same string or a node's role would
		// depend on its position in the tree.
		{"identified child", "2.1 sample and procedure", "sample and procedure"},
		{"bare child", "sample and procedure", "sample and procedure"},

		// A separator is required. Without it, a heading that merely starts
		// with a letter or a Roman-numeral character would be truncated.
		{"letter without separator", "a priori power analysis", "a priori power analysis"},
		{"roman letters without separator", "ivory tower critiques", "ivory tower critiques"},
		{"digit without separator", "3d printing", "3d printing"},

		{"empty", "", ""},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := StripIdentifiers(c.in); got != c.want {
				t.Errorf("StripIdentifiers(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}

// TestStripIdentifiers_RomanOverMatch pins the known over-match documented in
// normalize.go rather than leaving it to be discovered.
//
// The Roman rule accepts any word spelled from i, v, x, l, c, d and m, so
// "civil. liberties" loses its first word. The reference implementation that
// generated expected.json behaves identically, and expected.json is the
// contract, so this is asserted as current behaviour — not endorsed. If §6 step
// 2 is ever narrowed to validate a well-formed numeral, this test is the one
// that should change first, and the fixture regenerated alongside it.
func TestStripIdentifiers_RomanOverMatch(t *testing.T) {
	const in = "civil. liberties"
	const want = "liberties"

	if got := StripIdentifiers(in); got != want {
		t.Errorf("StripIdentifiers(%q) = %q, want %q — if this changed deliberately, §6 step 2 and testdata/expected.json must change with it", in, got, want)
	}
}

// TestParseContainer covers §7.
func TestParseContainer(t *testing.T) {
	cases := []struct {
		name          string
		in            string
		wantContainer StructuralContainer
		wantLabel     string
		wantRemainder string
	}{
		{"not a container", "introduction", "", "", "introduction"},
		{"bare trigger", "appendix", ContainerAppendix, "", ""},
		{"bare plural trigger", "appendices", ContainerAppendix, "", ""},
		{"labelled", "appendix b", ContainerAppendix, "B", ""},
		{"labelled alphanumeric", "appendix a1", ContainerAppendix, "A1", ""},
		{"labelled with colon and text", "appendix b: robustness checks", ContainerAppendix, "B", "robustness checks"},
		{"labelled with period and text", "appendix c. measures", ContainerAppendix, "C", "measures"},
		{"alias", "supporting information", ContainerAppendix, "", ""},
		{"alias plural", "supplementary materials", ContainerAppendix, "", ""},
		{"alias online", "online appendix", ContainerAppendix, "", ""},

		// Aliases match the whole string only. A heading that merely begins
		// with an alias is ordinary text, and must still be classified — and
		// raise a review task if nothing matches — rather than being written
		// off as a bare container.
		{"alias as prefix is not an alias", "supporting information for reviewers", "", "", "supporting information for reviewers"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			gotContainer, gotLabel, gotRemainder := ParseContainer(c.in)
			if gotContainer != c.wantContainer {
				t.Errorf("ParseContainer(%q) container = %q, want %q", c.in, gotContainer, c.wantContainer)
			}
			if gotLabel != c.wantLabel {
				t.Errorf("ParseContainer(%q) label = %q, want %q", c.in, gotLabel, c.wantLabel)
			}
			if gotRemainder != c.wantRemainder {
				t.Errorf("ParseContainer(%q) remainder = %q, want %q", c.in, gotRemainder, c.wantRemainder)
			}
		})
	}
}

// roleTable is the subset of testdata/table.json this phase checks against.
type roleTable struct {
	StructuralContainers struct {
		Appendix struct {
			Triggers  []string `json:"triggers"`
			AliasesG2 []string `json:"aliases_g2"`
		} `json:"appendix"`
	} `json:"structural_containers"`
}

// TestContainerDataMatchesTable proves the trigger and alias lists in
// container.go still agree with the authoritative role table.
//
// The lists are held in Go rather than read from JSON at run time so that this
// package keeps no file dependency — it is pure domain logic and must stay
// callable without a working directory. The cost of that choice is that the two
// copies can drift, and drift here is invisible: a heading simply stops being
// recognised as an appendix and quietly acquires a role instead. This test is
// what makes the duplication safe.
func TestContainerDataMatchesTable(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("testdata", "table.json"))
	if err != nil {
		t.Fatalf("read table.json: %v", err)
	}

	var table roleTable
	if err := json.Unmarshal(raw, &table); err != nil {
		t.Fatalf("parse table.json: %v", err)
	}

	assertSameSet(t, "triggers", appendixTriggers, table.StructuralContainers.Appendix.Triggers)
	assertSameSet(t, "aliases", appendixAliases, table.StructuralContainers.Appendix.AliasesG2)
}

func assertSameSet(t *testing.T, what string, got, want []string) {
	t.Helper()

	if len(got) != len(want) {
		t.Errorf("%s: have %d in container.go, table.json has %d", what, len(got), len(want))
	}

	inGot := map[string]bool{}
	for _, s := range got {
		inGot[s] = true
	}
	for _, s := range want {
		if !inGot[s] {
			t.Errorf("%s: table.json has %q and container.go does not", what, s)
		}
	}

	inWant := map[string]bool{}
	for _, s := range want {
		inWant[s] = true
	}
	for _, s := range got {
		if !inWant[s] {
			t.Errorf("%s: container.go has %q and table.json does not", what, s)
		}
	}
}

// TestPipelineReproducesFixture runs §6 steps 1-2 and §7 over every heading in
// the fixture and compares against expected.json field by field.
//
// This is phase 2's done-condition. The unit tests above pin individual rules;
// this one proves they compose into the values the specification predicts for a
// real paper, which is the only claim §15 actually makes.
//
// The document title is skipped: §4 identifies it separately and expected.json
// records a null semantic heading for it, so it is not an input to this
// pipeline.
func TestPipelineReproducesFixture(t *testing.T) {
	exp := loadExpected(t)

	for _, want := range exp.SectionNodes {
		t.Run(want.SectionID, func(t *testing.T) {
			normalized := Normalize(want.HeadingRaw)
			if normalized != want.HeadingNormalized {
				t.Fatalf("heading_normalized = %q, want %q", normalized, want.HeadingNormalized)
			}

			if want.NodeKind == "document_title" {
				return
			}

			container, label, semantic := ParseContainer(StripIdentifiers(normalized))

			if got, want := string(container), derefOrEmpty(want.StructuralContainer); got != want {
				t.Errorf("structural_container = %q, want %q", got, want)
			}
			if got, want := label, derefOrEmpty(want.AppendixLabel); got != want {
				t.Errorf("appendix_label = %q, want %q", got, want)
			}
			if got, want := semantic, derefOrEmpty(want.SemanticHeading); got != want {
				t.Errorf("semantic_heading = %q, want %q", got, want)
			}
		})
	}
}

// derefOrEmpty maps expected.json's nullable strings onto Go's zero value.
//
// The two encodings differ and the difference is deliberate on both sides. JSON
// distinguishes null from "": a null semantic_heading means a bare container
// with nothing to classify, and an empty string would mean a heading that
// normalized away to nothing. Go collapses both to "". That is safe HERE only
// because §7 never produces the second case — ParseContainer returns the input
// unchanged when it recognises nothing — so the two states cannot both arise
// for one node.
func derefOrEmpty(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}
