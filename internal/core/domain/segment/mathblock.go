// File: mathblock.go — a goldmark block parser that masks display-math blocks
// so their interior can never produce a heading (SPLIT-08).
//
// WHY THIS EXISTS. This codebase asks Mathpix for its plain-markdown conversion
// format, not Mathpix Markdown: internal/adapters/secondary/mathpix/client.go
// sends conversion_formats {"md": true}. That format emits dollar delimiters
// rather than LaTeX bracket delimiters, so display math arrives as $$ ... $$.
// goldmark has no math support of any kind, which means a $$ block is an
// ordinary paragraph to it — and atxHeadingParser.CanInterruptParagraph()
// returns true. A line-leading "# " inside a $$ block WILL therefore become a
// heading, and the damage is worse than a spurious node: the math block is then
// split across two sections, so both carry syntactically broken LaTeX.
//
// KNOWN BEHAVIOUR, documented rather than worked around. An UNTERMINATED $$
// swallows every remaining line to EOF, so every heading after it disappears
// from the output. That is the honest consequence of a masking block parser and
// it is the preferable failure: the alternative is emitting confident headings
// from inside broken LaTeX, in a phase whose whole product is byte-exactness.
// It is asserted explicitly in headings_test.go so it cannot be discovered
// later as a surprise, and plan 01-06's corpus diagnostic reports unpaired $$
// counts across real fixtures so the real-world exposure is measured rather
// than assumed.

package segment

import (
	"bytes"

	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/text"
)

// displayMathFence is the delimiter that opens and closes a display-math block.
var displayMathFence = []byte("$$")

// kindDisplayMath identifies the node type below. The kind is registered only
// because ast.Node requires a Kind; nothing ever renders one of these nodes and
// detectHeadings walks for *ast.Heading and ignores everything else.
var kindDisplayMath = ast.NewNodeKind("EpistemicOSDisplayMath")

// displayMath is an unexported block node whose only job is to SWALLOW LINES.
// It holds no content of interest and is never rendered or inspected.
type displayMath struct {
	ast.BaseBlock
}

// Kind implements ast.Node.
func (n *displayMath) Kind() ast.NodeKind { return kindDisplayMath }

// Dump implements ast.Node. It exists to satisfy the interface; goldmark calls
// it only from its own debugging helpers, which this package never uses.
func (n *displayMath) Dump(source []byte, level int) {
	ast.DumpHelper(n, source, level, nil, nil)
}

// displayMathData tracks one open block. The done flag carries the single-line
// "$$ x $$" case across from Open to the first Continue, since Open must not
// parse beyond the current line and cannot itself return Close.
type displayMathData struct {
	node ast.Node
	done bool
}

// displayMathKey is this parser's slot in the parse context, mirroring
// fencedCodeBlockParser's use of a context key for its own fence state.
var displayMathKey = parser.NewContextKey()

// displayMathParser implements parser.BlockParser for $$ ... $$ blocks.
type displayMathParser struct{}

// newDisplayMathParser returns the display-math block parser.
//
// It is registered at priority 550 in headings.go — BEFORE the ATX heading
// parser at 600 — which is what makes an open $$ block claim every subsequent
// line, so a line-leading '#' inside the block is never offered to the ATX
// parser at all. Returning NoChildren from Open and Continue|NoChildren from
// Continue is exactly the contract fencedCodeBlockParser uses to make its own
// interior opaque to every other block parser; copying it is what makes the
// masking total rather than partial.
func newDisplayMathParser() parser.BlockParser {
	return &displayMathParser{}
}

// Trigger reports the byte that offers a line to this parser. goldmark consults
// Trigger against the first non-space byte of the line, so a $$ indented by up
// to three spaces still reaches Open.
func (p *displayMathParser) Trigger() []byte { return []byte{'$'} }

// CanInterruptParagraph is true because display math routinely follows a prose
// line with no blank line between them in OCR output. If this returned false, a
// $$ block in that position would stay paragraph text and its interior would be
// offered to the ATX parser — the exact failure this file exists to prevent.
func (p *displayMathParser) CanInterruptParagraph() bool { return true }

// CanAcceptIndentedLine is false: a line indented four or more spaces is an
// indented code block, which the code-block parser at priority 500 already
// masks.
func (p *displayMathParser) CanAcceptIndentedLine() bool { return false }

// Open starts a block when the line begins with $$ at the block offset. The
// single-line form is recorded as already done, so the first Continue closes
// the block without consuming the following line.
func (p *displayMathParser) Open(_ ast.Node, reader text.Reader, pc parser.Context) (ast.Node, parser.State) {
	line, _ := reader.PeekLine()
	pos := pc.BlockOffset()
	if pos < 0 || !bytes.HasPrefix(line[pos:], displayMathFence) {
		return nil, parser.NoChildren
	}

	node := &displayMath{}
	// A closing $$ on the same line ends the block here; anything after the
	// opening delimiter is searched for it.
	done := bytes.Contains(line[pos+len(displayMathFence):], displayMathFence)
	pc.Set(displayMathKey, &displayMathData{node: node, done: done})

	reader.AdvanceToEOL()
	return node, parser.NoChildren
}

// Continue consumes lines until one containing the closing $$ has been
// consumed, then closes. Returning Continue|NoChildren keeps the interior
// opaque: while this block is open, parseBlocks never offers its lines to any
// other block parser, so a line-leading '#' inside it cannot become a heading.
//
// An unterminated block therefore consumes the rest of the document. See the
// file comment: that is documented behaviour, not a defect.
func (p *displayMathParser) Continue(node ast.Node, reader text.Reader, pc parser.Context) parser.State {
	d, ok := pc.Get(displayMathKey).(*displayMathData)
	if !ok || d == nil || d.node != node || d.done {
		return parser.Close
	}

	line, _ := reader.PeekLine()
	if line == nil {
		return parser.Close
	}
	if bytes.Contains(line, displayMathFence) {
		d.done = true
		reader.AdvanceToEOL()
		return parser.Close
	}

	reader.AdvanceToEOL()
	return parser.Continue | parser.NoChildren
}

// Close clears this parser's context slot so a later block starts clean. There
// is nothing else to finalise — the node carries no content anyone reads.
func (p *displayMathParser) Close(node ast.Node, _ text.Reader, pc parser.Context) {
	if d, ok := pc.Get(displayMathKey).(*displayMathData); ok && d != nil && d.node == node {
		pc.Set(displayMathKey, nil)
	}
}
