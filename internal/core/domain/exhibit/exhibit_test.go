package exhibit

import (
	"strings"
	"testing"
)

// Every fixture below is a shape taken from the ten ingested papers, not one
// invented to make the code pass. The comment on each names the paper it came
// from, because that is the difference between a test and a restatement.

func one(t *testing.T, md string) Table {
	t.Helper()
	tables, _ := Extract([]byte(md))
	if len(tables) != 1 {
		t.Fatalf("got %d tables, want 1: %+v", len(tables), tables)
	}
	return tables[0]
}

// Shape 1, the ordinary case. Most papers.
func TestTable_CaptionAbove(t *testing.T) {
	got := one(t, "Some prose.\n\n"+
		"Table 1. Loadings, reliability, and convergent validity.\n"+
		"| Constructs | Items | AVE |\n"+
		"| :--- | :--- | :--- |\n"+
		"| BCT | BCT1 | 0.802 |\n"+
		"| SCI | SCI1 | 0.771 |\n\n"+
		"More prose.\n")

	if got.Label != "1" {
		t.Errorf("label = %q, want %q", got.Label, "1")
	}
	if got.Kind != "table" {
		t.Errorf("kind = %q", got.Kind)
	}
	if got.Caption != "Loadings, reliability, and convergent validity." {
		t.Errorf("caption = %q", got.Caption)
	}
	if got.CaptionSource != CaptionAbove {
		t.Errorf("source = %q, want %q", got.CaptionSource, CaptionAbove)
	}
	if len(got.Header) != 3 || got.Header[0] != "Constructs" {
		t.Errorf("header = %v", got.Header)
	}
	if len(got.Rows) != 2 {
		t.Fatalf("got %d rows, want 2: %v", len(got.Rows), got.Rows)
	}
	if got.Rows[1][2] != "0.771" {
		t.Errorf("last cell = %q", got.Rows[1][2])
	}
	if got.ColumnCount() != 3 {
		t.Errorf("columns = %d, want 3", got.ColumnCount())
	}
}

// Shape 5, and the one that mattered most.
//
// This is the layout of the paper that scored ZERO out of twenty under a rule
// requiring the table row to follow the caption immediately: the label sits
// alone, the caption text is on the next line, the table after that.
func TestTable_LabelAloneWithCaptionOnTheNextLine(t *testing.T) {
	got := one(t, "Peldszus and Stede (2015) created a small corpus.\n\n"+
		"Table 1\n"+
		"Existing corpora annotated with argumentation structures at the discourse-level\n"+
		"| Source | Genre | Granularity |\n"+
		"| :--- | :--- | :--- |\n"+
		"| Reed et al. | various | clause |\n")

	if got.Label != "1" {
		t.Errorf("label = %q", got.Label)
	}
	if !strings.HasPrefix(got.Caption, "Existing corpora annotated") {
		t.Errorf("caption = %q, want the text from the following line", got.Caption)
	}
	if len(got.Rows) != 1 {
		t.Errorf("rows = %v", got.Rows)
	}
}

func TestTable_CaptionShapes(t *testing.T) {
	cases := []struct {
		name, caption, wantLabel, wantKind string
	}{
		{"bold", "**Table 2** Discriminant validity", "2", "table"},
		{"footnote marker glued on", "[^6]Table 5. Regression results", "5", "table"},
		{"appendix", "Appendix 1. Measurement items", "1", "appendix"},
		{"lettered label", "Table A1. Summary of exploratory studies", "A1", "table"},
		{"no trailing period", "Table 3 Direct and moderation effect", "3", "table"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := one(t, c.caption+"\n| A | B |\n| :--- | :--- |\n| 1 | 2 |\n")
			if got.Label != c.wantLabel {
				t.Errorf("label = %q, want %q", got.Label, c.wantLabel)
			}
			if got.Kind != c.wantKind {
				t.Errorf("kind = %q, want %q", got.Kind, c.wantKind)
			}
			if got.CaptionSource != CaptionAbove {
				t.Errorf("source = %q", got.CaptionSource)
			}
		})
	}
}

// Shape 4. Mathpix sometimes pulls the caption INSIDE the table as its first
// cell, so there is nothing above the table to match.
func TestTable_CaptionInsideTheFirstCell(t *testing.T) {
	got := one(t, "Fulfilling the assumptions paves the way for a measurement model.\n\n"+
		"| Table 6. CFA and reliability and validity results: Study 3 |  |  |  |\n"+
		"| Construct | Loading | CR | AVE |\n"+
		"| BB1 | 0.650 | 0.9 | 0.7 |\n")

	if got.CaptionSource != CaptionInFirstCell {
		t.Fatalf("source = %q, want %q", got.CaptionSource, CaptionInFirstCell)
	}
	if got.Label != "6" {
		t.Errorf("label = %q", got.Label)
	}
	if got.Caption != "CFA and reliability and validity results: Study 3" {
		t.Errorf("caption = %q", got.Caption)
	}
	// The caption row is not data.
	if len(got.Rows) != 2 {
		t.Errorf("rows = %v, want the caption row excluded", got.Rows)
	}
}

// TestTable_FirstCellCaptionNeedsAnEmptyRest is the limit on shape 4.
//
// Without it, a genuine header row whose first column happens to read "Table 1"
// would be swallowed as a caption and the table would lose its header.
func TestTable_FirstCellCaptionNeedsAnEmptyRest(t *testing.T) {
	got := one(t, "| Table 1 | Mean | SD |\n| :--- | :--- | :--- |\n| a | 1 | 2 |\n")

	if got.CaptionSource == CaptionInFirstCell {
		t.Error("took a populated header row as a caption")
	}
	if len(got.Header) != 3 {
		t.Errorf("header = %v, want three columns kept", got.Header)
	}
}

// A page break splits a table. Counting blocks instead of tables overcounts by
// a fifth across the ten papers.
func TestTable_ContinuationsMerge(t *testing.T) {
	md := "Table 4. Indirect effect\n" +
		"| Path | Beta |\n| :--- | :--- |\n| a | 1 |\n\n" +
		"(Continued)\n" +
		"| b | 2 |\n| c | 3 |\n"

	tables, _ := Extract([]byte(md))
	if len(tables) != 1 {
		t.Fatalf("got %d tables, want 1 — the second block continues the first", len(tables))
	}
	if len(tables[0].Rows) != 3 {
		t.Errorf("rows = %v, want all three merged", tables[0].Rows)
	}
	if len(tables[0].ContinuationOffsets) != 1 {
		t.Errorf("continuation spans = %v, want 1", tables[0].ContinuationOffsets)
	}
	if tables[0].EndOffset != len(md) {
		t.Errorf("end offset = %d, want the end of the continuation (%d)", tables[0].EndOffset, len(md))
	}
}

// An uncaptioned table is still a table. Refusing to extract it would lose data
// to a missing label.
func TestTable_NoCaption(t *testing.T) {
	got := one(t, "Ordinary prose that is not a caption.\n\n| A | B |\n| :--- | :--- |\n| 1 | 2 |\n")

	if got.CaptionSource != CaptionNone {
		t.Errorf("source = %q, want %q", got.CaptionSource, CaptionNone)
	}
	if len(got.Rows) != 1 {
		t.Errorf("rows = %v", got.Rows)
	}
}

// A heading is a section boundary and never a caption. Without this the table
// would claim the section title above it.
func TestTable_HeadingIsNotACaption(t *testing.T) {
	got := one(t, "## 4 Results\n\n| A | B |\n| :--- | :--- |\n| 1 | 2 |\n")

	if got.CaptionSource != CaptionNone {
		t.Errorf("source = %q — took the heading as a caption (%q)", got.CaptionSource, got.Caption)
	}
}

// TestTable_NoHeaderWithoutASeparator records a deliberate refusal to guess.
//
// Assuming the first row is a header would silently drop a data row from every
// table Mathpix did not mark, and the loss would look like a shorter table
// rather than an error.
func TestTable_NoHeaderWithoutASeparator(t *testing.T) {
	got := one(t, "Table 2. Something\n| a | 1 |\n| b | 2 |\n")

	if got.Header != nil {
		t.Errorf("header = %v, want none — nothing marked one", got.Header)
	}
	if len(got.Rows) != 2 {
		t.Errorf("rows = %v, want both kept", got.Rows)
	}
}

func TestTable_LatexIsFlagged(t *testing.T) {
	got := one(t, "Table 3. Effects\n| Path | $\\beta$ |\n| :--- | :--- |\n| A | 0.4 |\n")
	if !got.HasLatex {
		t.Error("LaTeX in a cell was not flagged; a numeric column needs it stripped first")
	}
}

func TestTable_OffsetsIndexTheMarkdown(t *testing.T) {
	md := "Preamble.\n\nTable 1. A caption\n| A |\n| :--- |\n| 1 |\n\nAfter.\n"
	got := one(t, md)

	span := md[got.StartOffset:got.EndOffset]
	if !strings.HasPrefix(span, "Table 1. A caption") {
		t.Errorf("span starts %q, want it to open at the caption", span[:min(24, len(span))])
	}
	if !strings.Contains(span, "| 1 |") {
		t.Errorf("span %q does not reach the last row", span)
	}
	if strings.Contains(span, "After.") {
		t.Error("span runs past the table into the prose below")
	}
}

// --- figures ---

func TestFigure(t *testing.T) {
	md := "Prose.\n\n" +
		"![](https://cdn.mathpix.com/cropped/7fa57a38-abc-19.jpg?height=943&width=1067&top_left_y=354&top_left_x=468)\n" +
		"Fig 3. Large network of 189 supply chains.\n"

	_, figs := Extract([]byte(md))
	if len(figs) != 1 {
		t.Fatalf("got %d figures, want 1", len(figs))
	}
	f := figs[0]

	if f.Label != "3" {
		t.Errorf("label = %q", f.Label)
	}
	if f.Caption != "Large network of 189 supply chains." {
		t.Errorf("caption = %q", f.Caption)
	}
	// The crop box is the whole point: it is what lets the figure be re-cut from
	// the PDF we already hold, instead of depending on Mathpix's CDN.
	if f.Page != 19 {
		t.Errorf("page = %d, want 19", f.Page)
	}
	if f.CropX != 468 || f.CropY != 354 || f.CropWidth != 1067 || f.CropHeight != 943 {
		t.Errorf("crop box = %dx%d at (%d,%d)", f.CropWidth, f.CropHeight, f.CropX, f.CropY)
	}
}

// TestFigure_AnImageWithNoCaptionIsNotAFigure.
//
// Six of the 26 images across the ten papers have no caption: three author
// photographs, two journal adverts and one scanned page of body text. The line
// under an author photo is the author's name.
func TestFigure_AnImageWithNoCaptionIsNotAFigure(t *testing.T) {
	cases := []struct{ name, md string }{
		{"author photograph",
			"#### Abstract\n\n![](https://cdn.mathpix.com/cropped/x-02.jpg?width=368&height=368)\nGisela Delfino\n"},
		{"journal advert",
			"Submit your manuscript to a Cogent OA journal at www.CogentOA.com\n![](https://cdn.mathpix.com/cropped/x-16.jpg?width=530&height=452)\n\n"},
		{"scanned page of prose",
			"The focus of the current study was to evaluate.\n![](https://cdn.mathpix.com/cropped/x-06.jpg?width=1318&height=543)\nschools located in each division were available.\n"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if _, figs := Extract([]byte(c.md)); len(figs) != 0 {
				t.Errorf("extracted %d figures from %s: %+v", len(figs), c.name, figs)
			}
		})
	}
}

// Some papers put the caption above the image rather than below.
func TestFigure_CaptionAboveTheImage(t *testing.T) {
	md := "Figure 2. Measurement model.\n![](https://cdn.mathpix.com/cropped/x-09.jpg?width=1296&height=760&top_left_x=624&top_left_y=351)\n"

	_, figs := Extract([]byte(md))
	if len(figs) != 1 {
		t.Fatalf("got %d figures, want 1", len(figs))
	}
	if figs[0].Label != "2" || figs[0].Page != 9 {
		t.Errorf("label = %q page = %d", figs[0].Label, figs[0].Page)
	}
}

func TestFigure_AppendixLabels(t *testing.T) {
	md := "![](https://cdn.mathpix.com/cropped/x-39.jpg?width=1472&height=837&top_left_x=298&top_left_y=832)\n" +
		"Fig A1. Simplified illustration of the extended supply chain.\n"

	_, figs := Extract([]byte(md))
	if len(figs) != 1 || figs[0].Label != "A1" {
		t.Fatalf("figures = %+v, want one labelled A1", figs)
	}
}

// A URL with no crop information must not invent one.
func TestFigure_UrlWithoutACropBox(t *testing.T) {
	md := "![](figures/local-image.png)\nFig 1. A local figure.\n"

	_, figs := Extract([]byte(md))
	if len(figs) != 1 {
		t.Fatalf("got %d figures, want 1", len(figs))
	}
	if figs[0].Page != 0 || figs[0].CropWidth != 0 {
		t.Errorf("invented a page or crop box: %+v", figs[0])
	}
}

// TestExtract_EmptyAndPlainDocuments. A qualitative paper in the set has one
// table and no figures at all; that is the paper, not a failure.
func TestExtract_EmptyAndPlainDocuments(t *testing.T) {
	for _, md := range []string{"", "# A Paper\n\nJust prose, no exhibits.\n"} {
		tables, figs := Extract([]byte(md))
		if len(tables) != 0 || len(figs) != 0 {
			t.Errorf("got %d tables and %d figures from %q", len(tables), len(figs), md)
		}
	}
}
