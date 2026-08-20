package segment

import (
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/text"
	"github.com/yuin/goldmark/util"
)

// Heading is one ATX heading found in a markdown document.
//
// Every field is a 0-based BYTE offset into the src buffer passed to
// detectHeadings, never a rune offset and never a UTF-16 code unit. The offsets
// are meaningless against any other buffer; slice the same src that produced
// them.
type Heading struct {
	// Level is the markdown heading level, 1..6, taken from ast.Heading.Level.
	// goldmark rejects a run of seven or more '#' outright, so no value outside
	// that range can reach this field.
	Level int

	// ByteStart is the offset of the heading's '#' character (D-07).
	ByteStart int

	// TextStart is the offset at which the heading text begins, with the '#'
	// markers, the whitespace following them, and any closing '###' sequence
	// already removed.
	TextStart int

	// TextStop is exclusive. TextStart == TextStop for an empty heading.
	TextStop int

	// Inferred marks a heading this package recovered from plain text because
	// Mathpix did not emit one (§3.1, rule version 2.9). goldmark never sets it;
	// only inferReferencesHeading does.
	Inferred bool
}

// mdParser is the block-only markdown parser this package detects headings
// with. It is built from an EXPLICIT parser set, and the set below is
// exhaustive.
//
// Verified against goldmark v1.8.5 parser/parser.go:462-470, 673-681:
// parser.NewConfig initialises BlockParsers to an empty util.PrioritizedSlice
// and WithBlockParsers APPENDS to it. DefaultBlockParsers is a separate free
// function that NewParser never calls. So a parser built this way contains
// exactly the parsers named here and nothing else.
//
// Three properties of this configuration are decisions, not accidents:
//
//   - NewSetextHeadingParser is deliberately ABSENT. Because the set is
//     exhaustive, omitting it genuinely excludes Setext headings from the
//     grammar. SPLIT-07 is therefore satisfied BY CONSTRUCTION rather than by
//     filtering the output of a parser that ran. With Setext gone and
//     ThematicBreak present, a --- line under a paragraph becomes a thematic
//     break and a === line becomes ordinary paragraph continuation text;
//     neither yields a heading.
//
//   - NewParagraphParser is NOT optional, and omitting it is catastrophic
//     rather than degraded. parseBlocks reads
//     "if p.openBlocks(...) != newBlocksOpened { return }"
//     (parser/parser.go:1085-1087), so with no paragraph parser the first
//     ordinary prose line opens no block, openBlocks returns noBlocksOpened,
//     and parsing STOPS at that line. Every heading after the first paragraph
//     would silently disappear with no error of any kind.
//
//   - NewListParser, NewListItemParser and NewBlockquoteParser are deliberately
//     omitted, and dropping them is strictly SAFER for false headings, not
//     riskier. Without them a blockquoted or list-item heading line becomes a
//     paragraph line whose first byte is '>' or '-', so the ATX trigger (which
//     fires on the first non-space byte) never sees a '#'.
//
// Do NOT generalise that last point into "any parser can be dropped safely".
// Measured on this configuration during plan 01-04: dropping NewCodeBlockParser
// does not merely re-expose an indented '#' as a false heading — it makes the
// four-space-indented line open no block at all, which ends parseBlocks early
// and LOSES every heading after it (3 headings become 1 on the fixture in
// TestDetectHeadings_HashInIndentedAndHTMLBlocks). Each of the seven entries
// above earns its place; removing one is a behavioural change, not a cleanup.
//
// No inline parsers, no paragraph transformers, no AST transformers and no
// renderer are configured: this package needs block structure and byte offsets
// only, and never looks inside a heading's inline content.
var mdParser = parser.NewParser(
	parser.WithBlockParsers(
		util.Prioritized(parser.NewThematicBreakParser(), 200), // --- is a rule, never an H2
		util.Prioritized(parser.NewCodeBlockParser(), 500),     // 4-space indented code
		util.Prioritized(newDisplayMathParser(), 550),          // $$ ... $$ masking (SPLIT-08)
		util.Prioritized(parser.NewATXHeadingParser(), 600),
		util.Prioritized(parser.NewFencedCodeBlockParser(), 700),
		util.Prioritized(parser.NewHTMLBlockParser(), 900),
		util.Prioritized(parser.NewParagraphParser(), 1000), // MANDATORY, see above
	),
)

// headingTextRange returns the byte range of a heading's text.
//
// The zero-Lines guard is unconditional on purpose. Three distinct return paths
// in atxHeadingParser.Open produce an *ast.Heading carrying ZERO Lines
// segments:
//
//  1. a bare '#' at EOF with no trailing newline;
//  2. "## " followed only by whitespace;
//  3. "### ###", where the whole line is markers.
//
// All three are reachable from OCR output, and on any of them a bare
// h.Lines().At(0) is an index-out-of-range panic. An empty heading is reported
// as the empty range [Pos, Pos), which keeps TextStart == TextStop true exactly
// when the heading has no text.
func headingTextRange(h *ast.Heading) (start, stop int) {
	if h.Lines().Len() == 0 {
		p := h.Pos()
		return p, p
	}
	seg := h.Lines().At(0)
	return seg.Start, seg.Stop
}

// detectHeadings returns every ATX heading in src, in document order.
//
// ByteStart is ast.Node.Pos(), which goldmark sets generically at
// parser/parser.go:997 as blockPos.Start + max(pc.BlockOffset(), 0) — the
// absolute byte offset of the first non-space byte on the block's opening line.
// For an ATX heading that byte is the '#'. ast.Heading does not override Pos(),
// so it inherits BaseNode.Pos() and that value reaches this function unchanged.
//
// ANTI-PATTERN, stated because it is tempting and wrong: Pos() and
// Lines().At(0) are different things BY DESIGN and neither may be derived from
// the other. Pos() is the '#' byte. Lines().At(0) is the heading TEXT, with the
// markers, the whitespace after them, and any closing '###' sequence already
// stripped and the remainder right-space-trimmed. That trimming is why this is
// strictly better than a regex splitter: a `^(#{1,6})\\s+(.*)$` capture group
// keeps a trailing carriage return on CRLF input, because goldmark's space set
// includes 0x0d but a regex `.` does not.
// A cross-check that back-scans from Lines().At(0).Start is unsafe for the
// three empty-heading cases above; verify Pos() against the raw source bytes
// instead, as assertPosIsHashByte does.
//
// INDENTATION SUBTLETY, worth knowing before Phase 4: CommonMark permits an ATX
// heading to be indented by up to three spaces. For such a heading Pos() points
// at the '#' and NOT at the line start, so under D-08 those leading spaces
// belong to the PRECEDING node. Tiling still holds exactly — the preceding
// node ends where this one begins — but md[ByteStart:] does not begin at a line
// start for that node.
//
// No sorting happens here and none is needed: goldmark walks the AST in
// document order, so the natural collection order already matches the source.
func detectHeadings(src []byte) []Heading {
	doc := mdParser.Parse(text.NewReader(src))

	var out []Heading
	_ = ast.Walk(doc, func(n ast.Node, entering bool) (ast.WalkStatus, error) {
		if !entering {
			return ast.WalkContinue, nil
		}
		h, ok := n.(*ast.Heading)
		if !ok {
			return ast.WalkContinue, nil
		}
		start, stop := headingTextRange(h)
		out = append(out, Heading{
			Level:     h.Level,
			ByteStart: h.Pos(),
			TextStart: start,
			TextStop:  stop,
		})
		return ast.WalkContinue, nil
	})

	return out
}
