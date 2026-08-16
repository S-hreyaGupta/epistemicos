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

	// TitleCandidateOrdinal is the node §4 could not confirm as the title but
	// could not dismiss either, or -1 when there is no such node. See
	// suppressTitleCandidate.
	//
	// It is NOT a title. It is the question "is this one?", pointed at something
	// specific so a reviewer has a candidate rather than a blank prompt.
	TitleCandidateOrdinal int

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

	// Runs BEFORE the two inheritance rules, so the suppressed candidate cannot
	// pick a role back up from its neighbours. It has no parent (it is the
	// shallowest node), and its children must not decide what it is either: a
	// paper whose sections all report results does not make the paper "results",
	// which is the same reason §4 leaves a confirmed title's role null.
	candidate := -1
	if titleStatus == TitleUnresolved {
		candidate = suppressTitleCandidate(nodes, counts)
	}

	linkParents(nodes)
	inheritFromParents(nodes)
	inheritFromChildren(nodes, candidate)

	doc := Document{
		Nodes:                 nodes,
		TitleOrdinal:          titleOrdinal,
		TitleStatus:           titleStatus,
		TitleMethod:           titleMethod,
		TitleCandidateOrdinal: candidate,
		HeadingCounts:         counts,
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
		Nodes:        []SectionNode{node},
		TitleOrdinal: -1,
		TitleStatus:  TitleUnresolved,
		// No candidate. A document with no headings has nothing that could be
		// its title, so the task stays addressed to the whole document.
		TitleCandidateOrdinal: -1,
		HeadingCounts:         counts,
	}
}

// buildNode runs one heading through §6 and §7 and gives it its span.
func buildNode(md []byte, ordinal int, h Heading, end int) SectionNode {
	raw := string(md[h.TextStart:h.TextStop])
	normalized := Normalize(raw)
	container, label, semantic := ParseContainer(StripIdentifiers(normalized))

	// EVERY appendix resolves structurally. Its suffix is never classified.
	//
	// Through 2.4 an appendix suffix ran the ordinary pipeline, so
	// "Appendix B: Robustness checks" became RESULTS and "Appendix B" alone
	// became Unknown. 2.5 removes that split: an appendix is an appendix, its
	// class is analytical, and it carries no role.
	//
	// The reason is that an appendix title says what the appendix is ABOUT, not
	// what epistemic work it does. "Detailed Results of Model Selection" sounds
	// like results and may equally be methodology a reviewer moved out of the
	// body; "Class Distributions" could support either. Appendices exist to hold
	// material that did not fit, and which part of the paper they support is not
	// recoverable from the title. Reading a role off it was reading confidence
	// into a coincidence of vocabulary.
	//
	// Nothing is lost. The suffix survives in SemanticHeading, so an appendix
	// stays searchable by what it is about; the two-axis model already keeps
	// WHERE content sits separate from WHAT it does, and this makes the appendix
	// answer only the first question, which is the only one its title answers.
	//
	// No ReviewTask either. A human cannot recover the role from the title
	// either, so routing it to review would be asking someone to guess with
	// exactly the information the machine had.
	classification := Classify(semantic)
	if container != "" {
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

// suppressTitleCandidate un-classifies the first node when a document has no H1
// at all, and returns its ordinal, or -1 when the rule does not apply.
//
// # The problem
//
// §4 admits only the first H1 as a title candidate. Two of the first four real
// papers had no H1: Mathpix emits one or not depending on the PDF's typography,
// not on whether the document has a title. So the paper's title arrived as an H2,
// classified through the ordinary pipeline, and acquired a role. On a systematic
// review, "A systematic review on regenerative supply chains…" came out as
// THEORY, with a three-byte span, and Step 4 would have read it as content.
//
// # Why this suppresses rather than promotes
//
// The obvious alternative is to promote the first H2 to title when no H1 exists.
// The heuristic that would gate it — "a title matches no keyword" — fails on the
// exact paper that raised the problem, whose title matched `theory`. There is no
// reliable signal here, so the honest move is to stop asserting one. The node
// keeps its text, its offsets and its place in the tree; it simply carries no
// role, and a human is asked.
//
// # Why the shallowest-level condition
//
// Without it this breaks the other no-H1 paper. That DBA proposal's first node is
// "Abstract" at H4, with H2s beneath it — a real section that resolves correctly
// and should keep its role. Being first is not enough; a title also has nothing
// above it. Requiring the node to sit at the shallowest level present separates
// the two cases exactly.
//
// # Scope
//
// Only the no-H1 case. §4's other unresolved-title case is a first H1 that
// classified as an ordinary section, and there the heading matched a keyword on
// its own terms — suppressing it would discard a good answer to fix a different
// problem.
func suppressTitleCandidate(nodes []SectionNode, counts map[int]int) int {
	if counts[1] != 0 || len(nodes) == 0 {
		return -1
	}

	shallowest := nodes[0].HeadingLevel
	for _, n := range nodes {
		if n.HeadingLevel < shallowest {
			shallowest = n.HeadingLevel
		}
	}
	if nodes[0].HeadingLevel != shallowest {
		return -1
	}

	// A STRUCTURAL CONTAINER IS NEVER A TITLE (2.8). "Appendix B" is not what a
	// paper is called, whatever level it arrives at. §7 already resolved it, and
	// un-resolving it to ask a question nobody needs asked is worse than the
	// problem this rule exists to fix.
	if nodes[0].Container != "" {
		return -1
	}

	// A HEADING THAT *IS* A ROLE KEYWORD IS THAT ROLE, NOT A TITLE (2.8).
	// A paper is never called "Methodology".
	//
	// The test is EXACT match, not "resolved by rule", and the difference is the
	// entire reason this rule suppresses rather than promotes. §4's existing
	// wording for H1s says a first heading "deterministically resolving to an
	// ordinary role" is that section — but the systematic review's title
	// resolved to `theory`, because the title itself reads "…A theoretical
	// framework of supply chain adaptations…". Applying §4's looser test here
	// would let that paper's title keep a role it should never have had.
	//
	// Containing a role keyword is something titles do. BEING one is not.
	if _, exact := keywordToRole[nodes[0].SemanticHeading]; exact {
		return -1
	}

	nodes[0].Classification = Classification{
		Status: StatusUnresolved,
	}
	return 0
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

// inheritFromChildren gives an unresolved node the role its subsections agree on.
//
// # Why this exists
//
// A real paper's "5 EMPIRICAL ANALYSIS" matched nothing, sat directly beneath
// the document title so there was nothing to inherit downward, and was the last
// open question in a 46-page document. Its three subsections were "5.1
// Regression results", "5.2 Robustness checks" and "5.3 Robustness checks", all
// three of which matched RESULTS from their own headings, unanimously.
//
// The answer was in the document. Asking a person for it, or paying an LLM for
// it, was asking for something already written down.
//
// # Why unanimity among MATCHED children, and not something looser
//
// Consensus is evidence only because each child reached its role independently,
// from its own heading, without consulting the parent or its siblings. Three
// independent readings agreeing is a fact about the section. Three readings that
// all descend from one earlier guess are that guess repeated, and treating
// repetition as corroboration is how a system talks itself into confidence it
// has not earned.
//
// So only MethodRule children count. A child that inherited downward is not a
// second opinion; a child resolved by its OWN children's consensus is a guess
// two hops from evidence. Both are excluded, which also makes the rule
// self-limiting: it fires at most once per node and never chains.
//
// # The limits, and the specific failure each one prevents
//
// ONLY WHEN NOTHING MATCHED. Same first limit as inheritFromParents, for the
// same reason: a heading that spoke for itself is not improved by its children.
// A multi-role tie is likewise left alone — it carries a shortlist a reviewer
// can act on, and overwriting it would replace a good question with a plausible
// answer.
//
// UNANIMOUS, NOT MAJORITY. One dissenting child and the node stays a question.
// A parent whose subsections disagree is exactly the case where a human should
// look, and a majority rule would silence the disagreement that makes it
// interesting.
//
// AT LEAST TWO CHILDREN. With one child there is no agreement, only a single
// data point that happens to be nested. A lone subsection is as likely to
// specialise its parent as to describe it, and calling that "consensus" would
// be dressing one weak signal in the language of several.
//
// UNKNOWN NEVER COUNTS. §7's Unknown is a placeholder meaning "this heading
// carries no semantic content", not a role. A parent of two bare appendices has
// learned nothing about itself.
//
// NEVER THE DOCUMENT TITLE. §4 leaves the title's role null deliberately. A
// paper whose sections were all methodology would not make the paper
// methodology, and the two-axis model exists precisely so the title does not
// have to pretend to a role.
//
// # Ordering
//
// Runs after inheritFromParents, and iterates in reverse so deeper nodes settle
// before shallower ones. The two rules cannot collide: downward reads a RESOLVED
// parent, upward writes an UNRESOLVED one. And a child of an unresolved node can
// never carry MethodInherited, since the only node it could have inherited from
// is the unresolved node itself.
// titleCandidate is the ordinal suppressTitleCandidate un-classified, or -1.
// It is excluded for the same reason the document title is: a paper whose
// sections all report results is not itself "results", and the node this points
// at is a title candidate rather than a section.
func inheritFromChildren(nodes []SectionNode, titleCandidate int) {
	children := make([][]int, len(nodes))
	for i := range nodes {
		if p := nodes[i].ParentOrdinal; p >= 0 && p < len(nodes) {
			children[p] = append(children[p], i)
		}
	}

	for i := len(nodes) - 1; i >= 0; i-- {
		c := nodes[i].Classification

		if c.Status != StatusUnresolved {
			continue // it has an answer; leave it alone
		}
		if len(c.CandidateRoles) > 0 {
			continue // a tie is a real question with a real shortlist
		}
		// Redundant today: applyTitle marks the title StatusResolved, so the
		// check above already skipped it. Kept because it states the actual
		// reason. §4 could reasonably leave the title unresolved instead, and on
		// the day someone makes that change this line is the only thing standing
		// between a paper's sections and a title that claims to be methodology.
		if nodes[i].Kind == KindDocumentTitle {
			continue
		}
		if i == titleCandidate {
			continue
		}

		kids := children[i]
		if len(kids) < 2 {
			continue // one child is a data point, not an agreement
		}

		role := Role("")
		unanimous := true
		for _, k := range kids {
			kc := nodes[k].Classification

			// Only a role the child read off its OWN heading is independent
			// evidence. Anything else is this same rule, or the downward one,
			// looking at itself.
			if kc.Method != MethodRule || kc.Status != StatusResolved {
				unanimous = false
				break
			}
			if kc.Role == "" || kc.Role == RoleUnknown {
				unanimous = false
				break
			}
			if role == "" {
				role = kc.Role
				continue
			}
			if kc.Role != role {
				unanimous = false
				break
			}
		}

		if !unanimous || role == "" {
			continue
		}

		nodes[i].Classification = Classification{
			Role:         role,
			ContentClass: ContentClassFor(role),
			Status:       StatusResolved,
			Method:       MethodChildConsensus,
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
