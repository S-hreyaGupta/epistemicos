package segment

// SectionNode is one segmented section of a document.
//
// # The byte-offset contract
//
// StartOffset and EndOffset are 0-based BYTE offsets into the UTF-8 encoding of
// the exact markdown the node was derived from. They are not rune offsets and
// they are not UTF-16 code units, and on real Mathpix output the three disagree
// — it carries β, —, ’ and ﬁ. Go string indexing is byte-based; keep it that
// way. Any conversion a browser front end needs happens in the HTTP DTO layer,
// never here.
//
// The range is half-open, so markdown[StartOffset:EndOffset] is the node's text
// and EndOffset-StartOffset is its length in bytes.
//
// # What a span covers, and what it does not
//
// A span begins immediately AFTER the newline terminating its own heading line,
// and ends at the '#' opening the next detected H1-H4 heading, or at the end of
// the document for the final node (v2.1 §3).
//
// Heading lines therefore belong to NO span. On the reference fixture that
// leaves 659 bytes across 21 heading lines owned by nobody, and this is correct
// rather than a defect: the heading is preserved verbatim in HeadingRaw, so
// nothing is lost. §3's non-overlap rule is about ownership collision, not
// coverage — no byte is claimed twice, and some bytes are claimed by no one.
//
// Text before the first detected heading is likewise unowned and produces no
// node at all (§5). In journal PDFs that region is citation metadata, dates and
// copyright. It survives in the stored approved_markdown; it is simply not part
// of any section. This is the difference between v2.0's 22 nodes for the
// fixture and 1.1's 23 — 1.1 created a front_matter node here.
//
// Nodes at H5 and H6 do not exist. Their headings and text stay inside the span
// of the nearest enclosing H1-H4 node.
//
// The offsets are valid ONLY against markdown whose SHA-256 matches the hash
// recorded alongside them. Nothing in this package can enforce that; the
// persistence layer must.
type SectionNode struct {
	// Ordinal is the node's position in document order, 0-based and dense. It
	// is the node's identity within a run and ParentOrdinal refers to it, so a
	// gap or a reorder invalidates every parent link in the slice.
	Ordinal int

	// ParentOrdinal is the ordinal of the nearest enclosing node, or -1 for a
	// node with no ancestor.
	//
	// The document-title node IS eligible as a parent (v2.1 §8). It is the H1
	// ancestor of the H2-H4 hierarchy, so the first H2 — or an H4 preceding it,
	// as in the reference fixture, where #### Abstract sits directly beneath
	// the title — carries the title node's ordinal.
	//
	// Parentage is structural position only. It confers no role relationship
	// whatever: classification is parent-independent by §6, and a node's role
	// never depends on its parent's.
	ParentOrdinal int

	// HeadingLevel is the markdown level, 1 to 4. H5 and H6 produce no node.
	HeadingLevel int

	// HeadingSource says whether a markdown heading existed here at all, or
	// whether 2.9 recovered one from plain text. Empty on runs stored before
	// 2.9, which is honest: those runs did not record the distinction because
	// every node was detected.
	HeadingSource HeadingSource

	// Kind separates structural position from semantic role. At most one node
	// per run is KindDocumentTitle.
	Kind NodeKind

	// HeadingRaw is the heading text verbatim, markers already stripped. It is
	// what makes excluding heading lines from spans lossless.
	HeadingRaw string

	// HeadingNormalized is HeadingRaw after §6 step 1.
	HeadingNormalized string

	// SemanticHeading is what survives identifier stripping and container
	// parsing, and is the input to classification. Empty means a bare
	// structural container with nothing to classify.
	SemanticHeading string

	// Container is the structural container this heading opens, if any.
	Container StructuralContainer

	// AppendixLabel is the short token following an appendix trigger — the "B"
	// of "Appendix B". Empty when there is none.
	AppendixLabel string

	// StartOffset is the first byte of the node's text: immediately after the
	// newline ending its heading line.
	StartOffset int

	// EndOffset is exclusive.
	EndOffset int

	// Classification is the §6 outcome. On an unresolved node its Role is
	// empty and must stay that way.
	Classification Classification
}

// Text returns the node's span of md.
//
// It panics on an out-of-range span rather than returning a truncated string.
// A span that does not fit its document means the markdown is not the markdown
// the offsets were computed against, and quietly returning a shorter string
// would surface three phases downstream as a plausible, confidently wrong quote
// of somebody's paper — which is the failure mode this whole phase exists to
// prevent.
func (n SectionNode) Text(md []byte) string {
	if n.StartOffset < 0 || n.EndOffset > len(md) || n.StartOffset > n.EndOffset {
		panic("segment: node span is outside the document; the markdown does not match the offsets")
	}
	return string(md[n.StartOffset:n.EndOffset])
}
