package segment

import (
	"strings"
	"testing"
)

// doc joins lines with a newline and appends a trailing one, so a fixture reads
// like a file on disk. Fixtures are built with explicit lines rather than raw
// string literals because several of them contain backtick fences.
func doc(lines ...string) string {
	return strings.Join(lines, "\n") + "\n"
}

// levels extracts the heading levels in document order, for compact assertions.
func levels(hs []Heading) []int {
	out := make([]int, 0, len(hs))
	for _, h := range hs {
		out = append(out, h.Level)
	}
	return out
}

// headingText slices a heading's text range out of the document it came from.
func headingText(md string, h Heading) string {
	return md[h.TextStart:h.TextStop]
}

// assertPosIsHashByte verifies every heading's ByteStart from the RAW SOURCE
// BYTES alone, with no reference to goldmark's Lines(). That independence is
// the whole point: Lines() is empty for the three empty-heading shapes, so a
// Lines()-based cross-check would panic or silently mis-verify on exactly the
// malformed input it exists to catch. If goldmark ever regresses Pos(), this
// fails loudly instead of shifting every downstream span.
//
// Plan 01-06 calls this helper over every corpus fixture, so the name is fixed.
//
// Assertion 3 deliberately encodes the CORRECT rule rather than the tempting
// wrong one (md[ByteStart-1] must be a newline). CommonMark permits an ATX
// heading to be indented by up to three spaces, and under D-08 those leading
// spaces belong to the PRECEDING node — so a heading's ByteStart is legitimately
// not a line start.
func assertPosIsHashByte(t *testing.T, md string, hs []Heading) {
	t.Helper()

	for i, h := range hs {
		if h.ByteStart < 0 || h.ByteStart >= len(md) {
			t.Errorf("heading %d: ByteStart %d out of range for a %d-byte document", i, h.ByteStart, len(md))
			continue
		}

		// 1. The offset points at a hash.
		if md[h.ByteStart] != '#' {
			t.Errorf("heading %d: md[%d] = %q, want '#'", i, h.ByteStart, md[h.ByteStart])
			continue
		}

		// 2. The run of hashes is exactly Level long.
		run := 0
		for j := h.ByteStart; j < len(md) && md[j] == '#'; j++ {
			run++
		}
		if run != h.Level {
			t.Errorf("heading %d at byte %d: hash run is %d, want Level %d", i, h.ByteStart, run, h.Level)
		}

		// 3. Everything back to the line start is spaces or tabs, at most three.
		indent := 0
		for j := h.ByteStart - 1; j >= 0 && md[j] != '\n'; j-- {
			if md[j] != ' ' && md[j] != '\t' {
				t.Errorf("heading %d at byte %d: non-indent byte %q before the hash", i, h.ByteStart, md[j])
				break
			}
			indent++
		}
		if indent > 3 {
			t.Errorf("heading %d at byte %d: %d bytes of indent, CommonMark allows at most 3", i, h.ByteStart, indent)
		}
	}
}

// Every ATX level H1 through H6 is detected with its own level (SPLIT-01).
// This also closes RESEARCH.md assumption A2: a goldmark parser configured with
// ZERO inline parsers must parse without panic or hang. Nothing here was ever
// executed before this test existed — the claim was read from source only.
func TestDetectHeadings_AllLevelsH1ThroughH6(t *testing.T) {
	md := doc(
		"# One",
		"",
		"## Two",
		"",
		"### Three",
		"",
		"#### Four",
		"",
		"##### Five",
		"",
		"###### Six",
	)

	hs := detectHeadings([]byte(md))
	if len(hs) != 6 {
		t.Fatalf("want 6 headings, got %d: %+v", len(hs), hs)
	}

	for i, h := range hs {
		if h.Level != i+1 {
			t.Errorf("heading %d: Level %d, want %d", i, h.Level, i+1)
		}
	}
	if got := headingText(md, hs[0]); got != "One" {
		t.Errorf("heading 0 text: %q, want %q", got, "One")
	}
	if got := headingText(md, hs[5]); got != "Six" {
		t.Errorf("heading 5 text: %q, want %q", got, "Six")
	}
}

// CommonMark ATX edge cases: a hash with no following space is not a heading,
// a closing hash sequence is stripped from the text, and seven hashes exceed
// the maximum level and are not a heading at all.
func TestDetectHeadings_ATXEdgeCases(t *testing.T) {
	md := doc(
		"#Introduction",
		"",
		"## Methods ##",
		"",
		"####### Seven",
	)

	hs := detectHeadings([]byte(md))
	if len(hs) != 1 {
		t.Fatalf("want exactly 1 heading (Methods), got %d: %+v", len(hs), hs)
	}
	if hs[0].Level != 2 {
		t.Errorf("Level %d, want 2", hs[0].Level)
	}
	if got := headingText(md, hs[0]); got != "Methods" {
		t.Errorf("closing sequence should be stripped: text %q, want %q", got, "Methods")
	}
	assertPosIsHashByte(t, md, hs)
}

// All three zero-Lines paths in atxHeadingParser.Open must yield an empty text
// range rather than an index-out-of-range panic.
func TestDetectHeadings_EmptyHeadingHasNoText(t *testing.T) {
	// Path 2: "## " followed only by whitespace.
	// Path 3: "### ###", where the line is nothing but markers.
	// Path 1: a bare "#" at EOF with NO trailing newline — hence no doc() here.
	cases := []string{
		"## \n",
		"### ###\n",
		"#",
	}

	for _, md := range cases {
		hs := detectHeadings([]byte(md))
		if len(hs) != 1 {
			t.Fatalf("%q: want 1 heading, got %d: %+v", md, len(hs), hs)
		}
		h := hs[0]
		if h.TextStart != h.TextStop {
			t.Errorf("%q: TextStart %d != TextStop %d, want an empty range", md, h.TextStart, h.TextStop)
		}
		if got := headingText(md, h); got != "" {
			t.Errorf("%q: heading text %q, want empty", md, got)
		}
		assertPosIsHashByte(t, md, hs)
	}
}

// A paragraph underlined by --- or === produces NO heading (SPLIT-07).
//
// This passes because NewSetextHeadingParser is absent from the block-parser
// set in headings.go — the grammar has no Setext production at all. It is not a
// filter applied to a parser's output, which is why it cannot be defeated by an
// input shape nobody thought of.
func TestDetectHeadings_SetextIsNotAHeading(t *testing.T) {
	dashes := doc(
		"Introduction",
		"---",
		"",
		"Body text.",
	)
	if hs := detectHeadings([]byte(dashes)); len(hs) != 0 {
		t.Errorf("--- underline: want 0 headings, got %d: %+v", len(hs), hs)
	}

	equals := doc(
		"Introduction",
		"===",
		"",
		"Body text.",
	)
	if hs := detectHeadings([]byte(equals)); len(hs) != 0 {
		t.Errorf("=== underline: want 0 headings, got %d: %+v", len(hs), hs)
	}
}

// A line-leading hash inside a fenced code block is code, not a heading
// (SPLIT-08). Both fence characters are exercised.
func TestDetectHeadings_HashInFencedCode(t *testing.T) {
	md := doc(
		"# Real One",
		"",
		"```python",
		"# not a heading",
		"x = 1",
		"```",
		"",
		"~~~",
		"# also not a heading",
		"~~~",
		"",
		"## Real Two",
	)

	hs := detectHeadings([]byte(md))
	if len(hs) != 2 {
		t.Fatalf("want 2 headings, got %d: %+v", len(hs), hs)
	}
	if got := levels(hs); got[0] != 1 || got[1] != 2 {
		t.Errorf("levels %v, want [1 2]", got)
	}
	if got := headingText(md, hs[0]); got != "Real One" {
		t.Errorf("heading 0 text %q, want %q", got, "Real One")
	}
	if got := headingText(md, hs[1]); got != "Real Two" {
		t.Errorf("heading 1 text %q, want %q", got, "Real Two")
	}
	assertPosIsHashByte(t, md, hs)
}

// A line-leading hash inside a display-math block is LaTeX, not a heading
// (SPLIT-08). goldmark has no math support, so this is the one SPLIT-08 clause
// that the bespoke parser in mathblock.go — not goldmark — is responsible for.
//
// The second case pins the UNTERMINATED behaviour: an unclosed block swallows
// the remainder of the document, so headings after it disappear. That is
// documented behaviour, not a defect. The alternative is emitting confident
// headings from inside broken LaTeX and splitting the equation across two
// sections, which is strictly worse in a phase whose product is byte-exactness.
func TestDetectHeadings_HashInDisplayMath(t *testing.T) {
	md := doc(
		"## Results",
		"",
		"$$",
		"\\begin{aligned}",
		"# this is not a heading",
		"x &= 1",
		"\\end{aligned}",
		"$$",
		"",
		"## Discussion",
	)

	hs := detectHeadings([]byte(md))
	if len(hs) != 2 {
		t.Fatalf("want exactly 2 headings, got %d: %+v", len(hs), hs)
	}
	if got := headingText(md, hs[0]); got != "Results" {
		t.Errorf("heading 0 text %q, want %q", got, "Results")
	}
	if got := headingText(md, hs[1]); got != "Discussion" {
		t.Errorf("heading 1 text %q, want %q", got, "Discussion")
	}
	assertPosIsHashByte(t, md, hs)

	// The single-line form closes on its opening line, so the block must not
	// swallow anything after it.
	inline := doc(
		"## Before",
		"",
		"$$ x = 1 $$",
		"",
		"## After",
	)
	if hs := detectHeadings([]byte(inline)); len(hs) != 2 {
		t.Errorf("single-line display math: want 2 headings, got %d: %+v", len(hs), hs)
	}

	// Unterminated: everything from the opening delimiter to EOF is swallowed.
	unterminated := doc(
		"## Results",
		"",
		"$$",
		"x = 1",
		"",
		"## Discussion",
	)
	hs = detectHeadings([]byte(unterminated))
	if len(hs) != 1 {
		t.Fatalf("unterminated display math: want 1 heading (the one before the block), got %d: %+v", len(hs), hs)
	}
	if got := headingText(unterminated, hs[0]); got != "Results" {
		t.Errorf("unterminated display math: surviving heading %q, want %q", got, "Results")
	}
}

// A hash inside a pipe-table cell produces no heading (SPLIT-08).
//
// This is essentially free in the md conversion format this codebase requests:
// a pipe-table row's first non-space byte is a pipe, so the ATX trigger never
// fires. The LaTeX tabular hazard described in the older project research is a
// property of the mmd format, which internal/adapters/secondary/mathpix does
// NOT request. The test is written anyway because the requirement is stated
// unconditionally and it costs three lines.
func TestDetectHeadings_HashInTableCell(t *testing.T) {
	md := doc(
		"## Sample",
		"",
		"| Metric | Value |",
		"| --- | --- |",
		"| # of firms | 412 |",
		"",
		"## Next",
	)

	hs := detectHeadings([]byte(md))
	if len(hs) != 2 {
		t.Fatalf("want 2 headings, got %d: %+v", len(hs), hs)
	}
	for _, h := range hs {
		if txt := headingText(md, h); strings.Contains(txt, "firms") {
			t.Errorf("table cell became a heading: %q", txt)
		}
	}
	assertPosIsHashByte(t, md, hs)
}

// A line-leading hash inside a four-space-indented code block or inside an HTML
// block produces no heading (SPLIT-08). Both are handled by goldmark's own
// CommonMark parsers rather than by hand-rolled state machines.
func TestDetectHeadings_HashInIndentedAndHTMLBlocks(t *testing.T) {
	indented := doc(
		"# Real One",
		"",
		"    # not a heading",
		"",
		"## Real Two",
	)
	hs := detectHeadings([]byte(indented))
	if len(hs) != 2 {
		t.Fatalf("indented code: want 2 headings, got %d: %+v", len(hs), hs)
	}
	assertPosIsHashByte(t, indented, hs)

	html := doc(
		"# Real One",
		"",
		"<div>",
		"# not a heading",
		"</div>",
		"",
		"## Real Two",
	)
	hs = detectHeadings([]byte(html))
	if len(hs) != 2 {
		t.Fatalf("html block: want 2 headings, got %d: %+v", len(hs), hs)
	}
	for _, h := range hs {
		if txt := headingText(html, h); strings.Contains(txt, "not a heading") {
			t.Errorf("html block interior became a heading: %q", txt)
		}
	}
	assertPosIsHashByte(t, html, hs)
}

// ByteStart is the offset of the hash character itself (D-07, SPLIT-09),
// verified against the raw source bytes with no reference to goldmark's
// Lines(). The indented case is included on purpose: it is the shape that
// breaks the naive rule "the byte before a heading is a newline".
func TestDetectHeadings_PosIsTheHashByte(t *testing.T) {
	md := doc(
		"# Title",
		"",
		"Some prose before a heading.",
		"",
		"   ## Methods",
		"",
		"Body with a β and an em dash — to keep the offsets multi-byte.",
		"",
		"#### Abstract",
	)

	hs := detectHeadings([]byte(md))
	if len(hs) != 3 {
		t.Fatalf("want 3 headings, got %d: %+v", len(hs), hs)
	}
	assertPosIsHashByte(t, md, hs)

	// The indented heading is the load-bearing case: its ByteStart must be the
	// hash, three bytes after the line start.
	indented := hs[1]
	if indented.Level != 2 {
		t.Fatalf("heading 1: Level %d, want 2", indented.Level)
	}
	if md[indented.ByteStart-1] != ' ' {
		t.Errorf("indented heading: byte before ByteStart is %q, want a space — ByteStart must be the hash, not the line start", md[indented.ByteStart-1])
	}
	if got := headingText(md, indented); got != "Methods" {
		t.Errorf("indented heading text %q, want %q", got, "Methods")
	}
}
