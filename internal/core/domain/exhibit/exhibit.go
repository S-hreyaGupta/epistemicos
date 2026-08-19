// Package exhibit extracts tables and figures from Step 2's markdown.
//
// # PARKED, 17 August 2026
//
// Complete and tested, and nothing consumes it. The decision was that the
// pipeline can operate without table data for now, so extraction stops at the
// `exhibits` CLI command: there is no persistence, no migration, and no store.
//
// That is a stopping point, not an unfinished job. docs/FUTURE_WORK.md records what
// exists, what does not, and the three findings that would otherwise have to be
// rediscovered — chiefly that the obvious detection rule fails SILENTLY, scoring
// zero of twenty tables on one real paper while raising no error.
//
// Left in the tree deliberately. Deleting a tested package to tidy up would mean
// rebuilding it and rediscovering ten papers' worth of edge cases.
//
// # Why this is not part of segment
//
// segment answers "what sections does this document have". This answers "what
// exhibits does it contain". Both read the same approved markdown and both
// produce byte offsets into it, which is exactly what lets a caller join them at
// read time without either depending on the other. Ordering them would make a
// table wait on section-level uncertainty for no gain.
//
// # Everything here was derived from ten real papers, not from one
//
// The rules below look fussy. Each clause is there because a paper broke a
// simpler version, and the simpler version failed SILENTLY — a paper with twenty
// tables came back with none, and nothing errored.
//
// Measured across the ten ingested papers, 902,867 characters:
//
//	88 pipe blocks, of which 14 were page-break continuations -> 74 tables
//	70 of 74 captioned (95%); the 4 misses are one survey questionnaire
//	26 images, of which 20 are figures and 6 are author photographs,
//	journal adverts and a scanned page
//
// The naive rule — "a line starting Table N whose next line is a table row" —
// scored 61 of 74, and zero of twenty on one paper.
package exhibit

import (
	"net/url"
	"regexp"
	"strconv"
	"strings"
)

// CaptionSource records how a caption was found, because the shapes are not
// equally trustworthy and a reader deserves to know which one applied.
type CaptionSource string

const (
	// CaptionAbove: an ordinary caption line preceding the table.
	CaptionAbove CaptionSource = "above"

	// CaptionInFirstCell: Mathpix absorbed the caption into the table's own
	// first cell, so there is nothing above the table to match.
	CaptionInFirstCell CaptionSource = "first_cell"

	// CaptionNone: no caption found. The table is still extracted — a table
	// without a caption is a table.
	CaptionNone CaptionSource = "none"
)

// Table is one extracted table.
type Table struct {
	// Label is the caption's identifier as printed: "1", "A1", "IV". Empty when
	// the caption is absent or carries no number.
	Label string

	// Kind is "table" or "appendix". Appendix tables are captioned "Appendix N"
	// rather than "Table N", and the distinction is worth keeping: an appendix
	// table is supporting material, which is a different claim about the content.
	Kind string

	// Caption is the full caption text without its label.
	Caption       string
	CaptionSource CaptionSource

	// Header is the first row when a separator row follows it, else nil. A table
	// whose header Mathpix did not mark is not an error; it is a table we should
	// not pretend to know the columns of.
	Header []string

	// Rows excludes the header and the separator.
	Rows [][]string

	// StartOffset and EndOffset span the caption (when above) through the last
	// row, half-open, into the same markdown segment indexes.
	StartOffset int
	EndOffset   int

	// ContinuationOffsets are the spans of blocks merged into this table because
	// a page break split it. Kept rather than discarded so the join back to the
	// document is complete: without them, bytes belonging to this table would
	// appear to belong to the surrounding prose.
	ContinuationOffsets [][2]int

	// HasLatex is set when any cell contains math. Those cells are not plain
	// strings and a numeric column needs the LaTeX stripped before it is numeric.
	HasLatex bool
}

// ColumnCount is the width of the widest row.
func (t Table) ColumnCount() int {
	n := len(t.Header)
	for _, r := range t.Rows {
		if len(r) > n {
			n = len(r)
		}
	}
	return n
}

// Figure is one extracted figure.
//
// A figure is a caption and an image reference. It is NOT the data behind the
// chart, and no amount of parsing produces that.
type Figure struct {
	Label   string
	Caption string

	// URL is the image, which for Mathpix output is a link to THEIR CDN.
	URL string

	// Page, and the crop box within it, parsed out of the URL. This is the part
	// that matters: it means the figure can be re-cut from the PDF we already
	// hold, so nothing depends on that CDN staying up.
	//
	// Page is 1-based. Zero means the URL did not carry one.
	Page                  int
	CropX, CropY          int
	CropWidth, CropHeight int

	StartOffset int
	EndOffset   int
}

// MathpixRenderDPI is the resolution Mathpix rendered pages at when it computed
// the crop boxes above.
//
// Measured, not documented: rendering a paper's page at successive scales and
// choosing the one where the crop box stops clipping the figure gives 1980 pixels
// across a 595-point A4 page, which is 240 DPI. Verified by re-cutting a figure
// from our own PDF and comparing it against the Mathpix crop.
//
// It is a constant here rather than a literal at the call site because it is an
// empirical finding about somebody else's renderer, and if they change it, this
// is the one line to correct.
const MathpixRenderDPI = 240

var (
	// Five caption shapes, all observed. In order of how they read:
	//
	//	Table 1. Title
	//	**Table 1** Title
	//	[^6]Table 5. Title          a footnote marker Mathpix glued to the front
	//	Appendix 1. Title           appendix tables say Appendix, not Table
	//	Table 1                     label alone, caption on the NEXT line
	tableCaption = regexp.MustCompile(
		`^\s*(?:\[\^\d+\])?\s*(?:\*\*)?\s*(Table|TABLE|Tab\.|Appendix|APPENDIX)\s*\.?\s*([A-Z]?\d+|[IVXLC]+)\b\.?\s*(?:\*\*)?\s*(.*)$`)

	figureCaption = regexp.MustCompile(
		`^\s*(?:\[\^\d+\])?\s*(?:\*\*)?\s*(?:Figure|Fig|FIG)\s*\.?\s*([A-Z]?\d+|[IVXLC]+)\b\.?\s*(?:\*\*)?\s*(.*)$`)

	continued = regexp.MustCompile(`(?i)\(?\s*continued\s*\)?`)

	imageLine = regexp.MustCompile(`^\s*!\[[^\]]*\]\(([^)]+)\)`)

	heading = regexp.MustCompile(`^\s{0,3}#{1,6}\s`)

	// The page number is the numeric suffix on the cropped filename.
	cropPath = regexp.MustCompile(`-(\d+)\.[A-Za-z]+$`)
)

// captionLookback is how many non-blank lines above a table may be searched for
// its caption.
//
// Three, because one journal prints the label on its own line and the caption
// text on the next, and the paper that scored zero under a one-line rule was
// exactly that. More than three starts capturing the sentence before the table,
// which is prose about the table rather than its caption.
const captionLookback = 3

// Extract finds every table and figure in the markdown.
//
// Offsets index into md, which must be the same bytes segment was given, so the
// two results can be joined without re-reading anything.
func Extract(md []byte) ([]Table, []Figure) {
	text := string(md)
	lines := strings.Split(text, "\n")

	// Byte offset of each line's first character.
	offsets := make([]int, len(lines))
	at := 0
	for i, l := range lines {
		offsets[i] = at
		at += len(l) + 1
	}
	lineEnd := func(i int) int {
		if i+1 < len(offsets) {
			return offsets[i+1]
		}
		return len(text)
	}

	return extractTables(lines, offsets, lineEnd), extractFigures(lines, offsets, lineEnd)
}

func extractTables(lines []string, offsets []int, lineEnd func(int) int) []Table {
	var out []Table

	for i := 0; i < len(lines); {
		if !isPipeRow(lines[i]) {
			i++
			continue
		}

		start := i
		for i < len(lines) && isPipeRow(lines[i]) {
			i++
		}
		end := i

		// A continuation belongs to the table above rather than being one of its
		// own. Counting blocks instead of tables overcounts by a fifth.
		if isContinuation(lines, start) {
			if n := len(out); n > 0 {
				out[n-1].ContinuationOffsets = append(out[n-1].ContinuationOffsets,
					[2]int{offsets[start], lineEnd(end - 1)})
				out[n-1].Rows = append(out[n-1].Rows, parseRows(lines[start:end])...)
				out[n-1].EndOffset = lineEnd(end - 1)
			}
			continue
		}

		t := Table{
			Kind:          "table",
			CaptionSource: CaptionNone,
			StartOffset:   offsets[start],
			EndOffset:     lineEnd(end - 1),
		}

		body := lines[start:end]

		// Shape 4 first: the caption may be sitting inside the table's own first
		// cell, in which case there is nothing above to find and that row is not
		// data.
		if kind, label, cap, ok := captionFromFirstCell(body[0]); ok {
			t.Kind, t.Label, t.Caption, t.CaptionSource = kind, label, cap, CaptionInFirstCell
			body = body[1:]
		} else if kind, label, cap, capLine, ok := captionAbove(lines, start); ok {
			t.Kind, t.Label, t.Caption, t.CaptionSource = kind, label, cap, CaptionAbove
			t.StartOffset = offsets[capLine]
		}

		t.Header, t.Rows = splitHeader(body)
		t.HasLatex = containsLatex(body)

		out = append(out, t)
	}

	return out
}

// captionAbove searches upward for a caption, allowing the label and its text to
// sit on separate lines.
func captionAbove(lines []string, blockStart int) (kind, label, caption string, capLine int, ok bool) {
	seen := 0
	for k := blockStart - 1; k >= 0 && seen < captionLookback; k-- {
		l := lines[k]
		if strings.TrimSpace(l) == "" {
			continue
		}
		// A heading is a section boundary, never a caption. Stopping here is what
		// keeps a table from claiming the heading above it as its title.
		if heading.MatchString(l) {
			return "", "", "", 0, false
		}

		if m := tableCaption.FindStringSubmatch(l); m != nil {
			kind = "table"
			if strings.EqualFold(strings.TrimSuffix(m[1], "."), "appendix") {
				kind = "appendix"
			}
			caption = strings.TrimSpace(m[3])

			// The label-alone shape: caption text is on the following lines,
			// between the label and the table.
			if caption == "" {
				var parts []string
				for j := k + 1; j < blockStart; j++ {
					if s := strings.TrimSpace(lines[j]); s != "" {
						parts = append(parts, s)
					}
				}
				caption = strings.Join(parts, " ")
			}
			return kind, m[2], caption, k, true
		}

		seen++
	}
	return "", "", "", 0, false
}

// captionFromFirstCell reads a caption Mathpix absorbed into the table.
//
// It requires every OTHER cell in the row to be empty. A real header row has
// content in its other columns, and without that condition a table whose first
// column happens to be headed "Table" would lose its header row.
func captionFromFirstCell(row string) (kind, label, caption string, ok bool) {
	cells := splitRow(row)
	if len(cells) == 0 {
		return "", "", "", false
	}
	for _, c := range cells[1:] {
		if strings.TrimSpace(c) != "" {
			return "", "", "", false
		}
	}

	m := tableCaption.FindStringSubmatch(cells[0])
	if m == nil {
		return "", "", "", false
	}
	kind = "table"
	if strings.EqualFold(strings.TrimSuffix(m[1], "."), "appendix") {
		kind = "appendix"
	}
	return kind, m[2], strings.TrimSpace(m[3]), true
}

// isContinuation reports whether the block at start continues the one above.
//
// Three signals, all seen in the ten papers: the word "Continued" above the
// block, the word inside its first row, or a block that begins immediately after
// another with nothing between them.
func isContinuation(lines []string, start int) bool {
	if continued.MatchString(lines[start]) {
		return true
	}
	k := start - 1
	for k >= 0 && strings.TrimSpace(lines[k]) == "" {
		k--
	}
	if k < 0 {
		return false
	}
	return continued.MatchString(lines[k]) || isPipeRow(lines[k])
}

func extractFigures(lines []string, offsets []int, lineEnd func(int) int) []Figure {
	var out []Figure

	for i, l := range lines {
		m := imageLine.FindStringSubmatch(l)
		if m == nil {
			continue
		}

		// An image with no caption near it is NOT a figure, and this is the whole
		// filter. Of 26 images across the ten papers, 6 had no caption: three
		// author photographs, two journal adverts and one scanned page of body
		// text. Every one of the other 20 was a real figure.
		label, caption, capLine, ok := figureCaptionNear(lines, i)
		if !ok {
			continue
		}

		f := Figure{
			Label:       label,
			Caption:     caption,
			URL:         strings.TrimSpace(m[1]),
			StartOffset: offsets[min(i, capLine)],
			EndOffset:   lineEnd(max(i, capLine)),
		}
		f.Page, f.CropX, f.CropY, f.CropWidth, f.CropHeight = parseCrop(f.URL)

		out = append(out, f)
	}

	return out
}

// figureCaptionNear looks two lines either side. Mathpix puts the caption below
// the image in most papers and above it in some, and a blank line may sit
// between.
func figureCaptionNear(lines []string, img int) (label, caption string, at int, ok bool) {
	for _, k := range []int{img + 1, img + 2, img - 1, img - 2} {
		if k < 0 || k >= len(lines) {
			continue
		}
		if heading.MatchString(lines[k]) {
			continue
		}
		if m := figureCaption.FindStringSubmatch(lines[k]); m != nil {
			return m[1], strings.TrimSpace(m[2]), k, true
		}
	}
	return "", "", 0, false
}

// parseCrop pulls the page number and crop box out of a Mathpix CDN URL.
//
// This is the answer to "can we keep the figures?". The URL carries where on
// which page the image was cut from, so a figure can be re-cut from the PDF we
// already store at ingest, at MathpixRenderDPI. Nothing has to depend on their
// CDN continuing to serve the file.
func parseCrop(raw string) (page, x, y, w, h int) {
	u, err := url.Parse(raw)
	if err != nil {
		return 0, 0, 0, 0, 0
	}
	if m := cropPath.FindStringSubmatch(u.Path); m != nil {
		page, _ = strconv.Atoi(m[1])
	}
	q := u.Query()
	atoi := func(k string) int {
		n, _ := strconv.Atoi(q.Get(k))
		return n
	}
	return page, atoi("top_left_x"), atoi("top_left_y"), atoi("width"), atoi("height")
}

func isPipeRow(l string) bool {
	s := strings.TrimSpace(l)
	return len(s) > 2 && strings.HasPrefix(s, "|") && strings.HasSuffix(s, "|")
}

// isSeparatorRow matches Mathpix's | :--- | header rule.
func isSeparatorRow(l string) bool {
	if !isPipeRow(l) {
		return false
	}
	for _, c := range splitRow(l) {
		c = strings.TrimSpace(c)
		if c == "" {
			continue
		}
		if strings.Trim(c, ":- ") != "" {
			return false
		}
	}
	return true
}

func splitRow(l string) []string {
	s := strings.TrimSpace(l)
	s = strings.TrimPrefix(s, "|")
	s = strings.TrimSuffix(s, "|")
	parts := strings.Split(s, "|")
	for i := range parts {
		parts[i] = strings.TrimSpace(parts[i])
	}
	return parts
}

// splitHeader separates a header row from the data, but only when Mathpix marked
// one with a separator. Guessing that the first row is a header would silently
// drop a data row from any table that has no header.
func splitHeader(body []string) (header []string, rows [][]string) {
	if len(body) >= 2 && isSeparatorRow(body[1]) {
		return splitRow(body[0]), parseRows(body[2:])
	}
	return nil, parseRows(body)
}

func parseRows(body []string) [][]string {
	var rows [][]string
	for _, l := range body {
		if isSeparatorRow(l) {
			continue
		}
		rows = append(rows, splitRow(l))
	}
	return rows
}

func containsLatex(body []string) bool {
	for _, l := range body {
		if strings.Contains(l, "$") || strings.Contains(l, `\mathrm`) {
			return true
		}
	}
	return false
}
