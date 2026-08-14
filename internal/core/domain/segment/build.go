package segment

import (
	"bytes"
	"fmt"
)

// TitleStatus records whether the document title was identified.
type TitleStatus string

const (
	TitleIdentified TitleStatus = "identified"
	TitleUnresolved TitleStatus = "unresolved"
)

// TitleMethod records which of §4's rules identified the title.
type TitleMethod string

const (
	// MethodSingletonH1: exactly one H1 in the document, and it did not itself
	// resolve to an ordinary role.
	MethodSingletonH1 TitleMethod = "singleton_h1"

	// MethodStructuralRule: two or more H1s, and the FIRST was taken as the
	// candidate. Later H1s are anomalous section nodes, never title candidates.
	MethodStructuralRule TitleMethod = "structural_rule"
)

// Document is the result of segmenting one markdown document.
type Document struct {
	Nodes []SectionNode

	// TitleOrdinal is the ordinal of the document-title node, or -1 when the
	// title is unresolved.
	TitleOrdinal int

	TitleStatus TitleStatus

	// TitleMethod is empty when the title is unresolved.
	TitleMethod TitleMethod

	// HeadingCounts is the number of detected headings per level, 1 to 6.
	// H5 and H6 are counted although they produce no node, because §10's
	// invariant is stated over DETECTED headings and the count is what makes
	// the exclusion auditable rather than invisible.
	HeadingCounts map[int]int
}

// Title returns the document-title node and whether one was identified.
func (d Document) Title() (SectionNode, bool) {
	if d.TitleOrdinal < 0 || d.TitleOrdinal >= len(d.Nodes) {
		return SectionNode{}, false
	}
	return d.Nodes[d.TitleOrdinal], true
}

// Build segments markdown into nodes: v2.1 §3, §4, §5 and §6, with §10's
// invariant checked on the way out.
//
// It returns an error only when the zero-silent-loss invariant fails. Every
// other outcome — an unresolved role, an unidentified title, a document with no
// headings — is a successful run carrying an honest result. §10 is explicit
// that classification failure is not segmentation failure: an unresolved node
// is acceptable, a MISSING node is not.
func Build(md []byte) (Document, error) {
	headings := detectHeadings(md)

	counts := map[int]int{}
	for _, h := range headings {
		counts[h.Level]++
	}

	// H5 and H6 are detected so they can be counted and excluded on purpose.
	// Their text stays inside the nearest enclosing H1-H4 span (§3).
	var structural []Heading
	for _, h := range headings {
		if h.Level >= 1 && h.Level <= 4 {
			structural = append(structural, h)
		}
	}

	if len(structural) == 0 {
		return buildHeadlessDocument(md, counts), nil
	}

	nodes := make([]SectionNode, 0, len(structural))
	for i, h := range structural {
		nodes = append(nodes, buildNode(md, i, h, spanEnd(md, structural, i)))
	}

	titleOrdinal, titleStatus, titleMethod := identifyTitle(nodes, counts[1])
	if titleOrdinal >= 0 {
		applyTitle(&nodes[titleOrdinal])
	}

	linkParents(nodes)
	inheritFromParents(nodes)

	doc := Document{
		Nodes:         nodes,
		TitleOrdinal:  titleOrdinal,
		TitleStatus:   titleStatus,
		TitleMethod:   titleMethod,
		HeadingCounts: counts,
	}

	if err := ValidateNoSilentLoss(doc, headings); err != nil {
		return Document{}, err
	}

	return doc, nil
}

// buildHeadlessDocument implements §5's no-headings case: one whole-document
// node with the synthetic Unknown role.
//
// This is the ONLY node in the system that exists without a detected heading,
// and it exists by explicit rule rather than by inference. The alternative —
// producing nothing — would silently skip an unstructured document, and a run
// that processes nothing while reporting success is worse than one that
// processes it badly.
func buildHeadlessDocument(md []byte, counts map[int]int) Document {
	node := SectionNode{
		Ordinal:       0,
		ParentOrdinal: -1,
		Kind:          KindSection,
		StartOffset:   0,
		EndOffset:     len(md),
		Classification: Classification{
			Role:         RoleUnknown,
			ContentClass: ContentClassFor(RoleUnknown),
			Status:       StatusResolved,
			Method:       MethodStructural,
		},
	}

	return Document{
		Nodes:         []SectionNode{node},
		TitleOrdinal:  -1,
		TitleStatus:   TitleUnresolved,
		HeadingCounts: counts,
	}
}

// buildNode runs one heading through §6 and §7 and gives it its span.
func buildNode(md []byte, ordinal int, h Heading, end int) SectionNode {
	raw := string(md[h.TextStart:h.TextStop])
	normalized := Normalize(raw)
	container, label, semantic := ParseContainer(StripIdentifiers(normalized))

	classification := Classify(semantic)

	// A container whose suffix classified as nothing is still a container.
	//
	// §7 already resolves a BARE container — "Appendix B", with no suffix — to
	// Unknown by structural assignment, raising no question, because the
	// heading carries no epistemic claim to adjudicate. But an appendix whose
	// suffix matched no keyword was becoming a question, which means ADDING
	// WORDS WE CANNOT PARSE turned a resolved answer into an unresolved one.
	// That is backwards: we know exactly as much as we did about the bare case.
	//
	// Nothing is lost by not asking. The suffix survives in SemanticHeading, so
	// this decides only what reaches the review queue, not what is recorded —
	// an appendix with an unclassified suffix remains findable at any time.
	if container != "" && classification.Status == StatusUnresolved {
		classification = Classification{
			Role:         RoleUnknown,
			ContentClass: ContentClassFor(RoleUnknown),
			Status:       StatusResolved,
			Method:       MethodStructural,
		}
	}

	return SectionNode{
		Ordinal:           ordinal,
		ParentOrdinal:     -1, // linkParents fills this in
		HeadingLevel:      h.Level,
		Kind:              KindSection,
		HeadingRaw:        raw,
		HeadingNormalized: normalized,
		SemanticHeading:   semantic,
		Container:         container,
		AppendixLabel:     label,
		StartOffset:       spanStart(md, h),
		EndOffset:         end,
		Classification:    classification,
	}
}

// spanStart returns the offset of the newline that terminates a heading line:
// §3's start_offset.
//
// THE SPAN BEGINS AT THAT NEWLINE, not after it. So every span's first byte is
// the '\n' ending its own heading line, and node n004 of the reference fixture
// spans "\n\n" — two bytes, not zero.
//
// This is worth stating because §3's prose says "immediately following the
// terminating newline", which is off by one against the fixture. The fixture is
// authoritative: it was generated by the reference implementation that verified
// the specification, and the ruling on this amendment was to keep it as it
// stands. Implementing the prose instead would shift all 22 offsets by one byte
// and fail every comparison in expected.json. The prose is being corrected.
//
// Nothing depends on which convention is chosen — the two differ by one
// newline, and no heading text is included either way — but the two
// implementations are not interchangeable, which is precisely the ambiguity
// this amendment existed to remove.
//
// Scanning forward from TextStop rather than computing from TextStart is
// deliberate. A heading may carry a closing marker run and trailing whitespace
// — "### Results ###   " — none of which goldmark includes in TextStop, so no
// arithmetic reaches the line end reliably. Finding the newline is exact.
//
// A heading on the final line with no trailing newline yields the document
// length, giving that node an empty span. §5 requires exactly that: a heading
// with an empty body is a node with an empty span, and it still classifies from
// its heading text.
func spanStart(md []byte, h Heading) int {
	if i := bytes.IndexByte(md[h.TextStop:], '\n'); i >= 0 {
		return h.TextStop + i
	}
	return len(md)
}

// spanEnd returns the byte offset of the '#' opening the next structural
// heading, or the document length for the final node: §3's end_offset.
func spanEnd(md []byte, structural []Heading, i int) int {
	if i+1 < len(structural) {
		return structural[i+1].ByteStart
	}
	return len(md)
}

// identifyTitle applies §4's position-constrained rule.
//
// Only the FIRST H1 is ever a candidate, and it must not itself resolve to an
// ordinary role. A document opening "# Introduction" has no title: the H1 is an
// introduction section, and §4 is explicit that nothing is auto-promoted and
// that a later H1 never becomes the title by elimination. Returning "no title"
// here is a real answer, and §8 turns it into a title_ambiguity review task
// rather than a guess.
//
// The method distinguishes the two identifying paths so a reader can tell how
// confident the determination was: singleton_h1 means the document had exactly
// one H1, structural_rule means it had several and the first was taken.
func identifyTitle(nodes []SectionNode, h1Count int) (ordinal int, status TitleStatus, method TitleMethod) {
	first := -1
	for i, n := range nodes {
		if n.HeadingLevel == 1 {
			first = i
			break
		}
	}

	if first < 0 {
		return -1, TitleUnresolved, ""
	}

	// A first H1 that classifies as an ordinary section is that section, not
	// the title.
	if nodes[first].Classification.Status == StatusResolved &&
		nodes[first].Classification.Method == MethodRule {
		return -1, TitleUnresolved, ""
	}

	if h1Count == 1 {
		return first, TitleIdentified, MethodSingletonH1
	}
	return first, TitleIdentified, MethodStructuralRule
}

// applyTitle converts a node into the document-title node: §4.
//
// The title is not classified. Its role is null — deliberately not a value in
// the role taxonomy, because "title" answers what document this is, while roles
// answer what function a section performs. Its class is administrative and its
// status resolved, because the determination succeeded; there is simply no
// section role to report.
func applyTitle(n *SectionNode) {
	n.Kind = KindDocumentTitle
	n.Classification = Classification{
		Role:         "",
		ContentClass: ClassAdministrative,
		Status:       StatusResolved,
		Method:       MethodStructural,
	}
}

// linkParents sets ParentOrdinal for every node from heading levels alone.
//
// A node's parent is the nearest preceding node at a shallower level. The
// document-title node participates as an ordinary H1 ancestor — v2.1 §8 makes
// it explicitly eligible — so an H2, or an H4 with no H2 or H3 above it, hangs
// off the title.
//
// The stack holds one ordinal per level rather than a growing list, so a
// document that skips a level (H2 straight to H4, as the fixture does for the
// Abstract) still finds the nearest real ancestor rather than failing to link.
func linkParents(nodes []SectionNode) {
	// byLevel[l] is the ordinal of the most recent node at level l, or -1.
	byLevel := [5]int{-1, -1, -1, -1, -1}

	for i := range nodes {
		level := nodes[i].HeadingLevel

		parent := -1
		for l := level - 1; l >= 1; l-- {
			if byLevel[l] >= 0 {
				parent = byLevel[l]
				break
			}
		}
		nodes[i].ParentOrdinal = parent

		byLevel[level] = i

		// Deeper levels are no longer in scope once a shallower heading opens.
		// Without this, an H3 following a later H2 would still see the H3 that
		// preceded that H2 and could parent to a node outside its subtree.
		for l := level + 1; l <= 4; l++ {
			byLevel[l] = -1
		}
	}
}

// inheritFromParents gives an unresolved node its parent's role.
//
// # This is a rescue mechanism, and the specification rules one out
//
// §3 says every node "runs the same parent-independent classification pipeline"
// and that "no promotion or rescue mechanism exists or is needed." This is
// exactly such a mechanism, added deliberately after a real paper showed that
// seven of its nine open questions were answered by the parent heading alone:
// "2.1 ESG disclosure in supply chains" is uninterpretable by itself and
// obvious beneath "2 Literature Review".
//
// Parent-independence remains true where it matters. A heading that MATCHED
// keeps its own answer; position never overrules evidence. What changes is only
// what happens when there is no evidence at all.
//
// # Three limits, each preventing a specific failure
//
// ONLY WHEN NOTHING MATCHED. A resolved node is left alone, and so is a
// multi-role tie — a tie is a real question with a real shortlist, and burying
// it under the parent's role would silently discard the reviewer's best
// information. Without this limit, "4.1 Preliminary results" under a methodology
// section would become methodology, overruling the keyword that got it right.
//
// ONLY FROM A RESOLVED PARENT. If the parent is itself unresolved the child
// stays unresolved. Otherwise guesses inherit from guesses and nothing records
// how far any given answer is from actual evidence.
//
// NEVER FROM THE DOCUMENT TITLE. The title has no role by design (§4), so there
// is nothing to inherit. This is why "5 EMPIRICAL ANALYSIS" and "Appendix A",
// which sit directly beneath the title, remain questions — correctly, since
// their placement tells a reviewer nothing.
//
// The result is marked MethodInherited rather than MethodRule, so an inherited
// role stays distinguishable from a matched one for as long as it is stored.
func inheritFromParents(nodes []SectionNode) {
	for i := range nodes {
		c := nodes[i].Classification

		if c.Status != StatusUnresolved {
			continue // it has an answer; leave it alone
		}
		if len(c.CandidateRoles) > 0 {
			continue // a tie is a real question with a real shortlist
		}

		p := nodes[i].ParentOrdinal
		if p < 0 || p >= i {
			continue
		}

		parent := nodes[p]
		if parent.Kind == KindDocumentTitle {
			continue // the title has no role to give
		}
		if parent.Classification.Status != StatusResolved || parent.Classification.Role == "" {
			continue // no guesses inheriting from guesses
		}

		nodes[i].Classification = Classification{
			Role:         parent.Classification.Role,
			ContentClass: parent.Classification.ContentClass,
			Status:       StatusResolved,
			Method:       MethodInherited,
		}
	}
}

// ValidateNoSilentLoss enforces §10's hard runtime invariant: every detected
// H1-H4 heading survives as exactly one node.
//
// # Why this fails closed
//
// A missing node does not throw. It produces a section tree that looks complete
// and quietly omits part of somebody's paper, and Step 4 then reports on a
// document it never fully saw. Byte-exactness and completeness are this phase's
// entire product; a tree missing a section is not a smaller answer, it is a
// wrong one. The cost of failing is bounded and visible — one paper does not
// segment, and someone reads an error that names the counts.
//
// Build calls this on its own output rather than trusting its construction, so
// a later refactor's bug becomes a hard failure where it happens instead of a
// wrong quote three phases downstream.
//
// The invariant is stated over DETECTED headings only. H5 and H6 headings, and
// the unheaded preamble, remaining inside their enclosing spans is an explicit
// scope boundary (§12, G1) and not loss.
func ValidateNoSilentLoss(doc Document, detected []Heading) error {
	structural := 0
	for _, h := range detected {
		if h.Level >= 1 && h.Level <= 4 {
			structural++
		}
	}

	// §5's sole exception: no headings at all yields exactly one node by rule.
	if structural == 0 {
		if len(doc.Nodes) != 1 {
			return fmt.Errorf("segment: silent_loss_invariant: a document with no detected headings must produce exactly one node, produced %d", len(doc.Nodes))
		}
		return nil
	}

	if len(doc.Nodes) != structural {
		return fmt.Errorf("segment: silent_loss_invariant: %d detected H1-H4 headings produced %d nodes", structural, len(doc.Nodes))
	}

	for i, n := range doc.Nodes {
		if n.Ordinal != i {
			return fmt.Errorf("segment: silent_loss_invariant: node at index %d carries ordinal %d, so parent links in this slice address the wrong nodes", i, n.Ordinal)
		}
		if n.HeadingLevel < 1 || n.HeadingLevel > 4 {
			return fmt.Errorf("segment: silent_loss_invariant: node %d has heading level %d, outside the supported range", i, n.HeadingLevel)
		}
		if n.StartOffset > n.EndOffset {
			return fmt.Errorf("segment: silent_loss_invariant: node %d has inverted span [%d,%d)", i, n.StartOffset, n.EndOffset)
		}
		if n.ParentOrdinal >= i {
			return fmt.Errorf("segment: silent_loss_invariant: node %d has parent ordinal %d, which is not an earlier node", i, n.ParentOrdinal)
		}
	}

	return nil
}
