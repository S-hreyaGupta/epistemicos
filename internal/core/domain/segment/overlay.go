package segment

// ReviewDecision is one authoritative human resolution of one review task.
//
// A correction updates the same decision in place. That is a deliberate and
// confined exception to the pipeline's append-only discipline, limited to human
// decisions, because there is never more than one competing human resolution
// per task — the database enforces it with UNIQUE(review_task_id).
//
// The machine's determination on the node is NEVER overwritten. It stays as
// provenance, and the effective value is computed at read time by preferring
// this decision when one exists. That is what makes the two distinguishable
// afterwards: "the machine said methodology and a human agreed" and "the machine
// had no answer and a human supplied methodology" are different facts, and
// overwriting would destroy the difference.
type ReviewDecision struct {
	ID           string
	ReviewTaskID string

	// Decision is which of the two things this is. It is not derivable from the
	// other fields: a rejection assigns nothing, and so does a decision whose
	// assignment failed to save, and those must not read the same.
	Decision Decision

	AssignedRole         Role
	AssignedContentClass ContentClass

	// Used only by title_ambiguity decisions.
	AssignedDocumentTitleText   string
	AssignedDocumentTitleNodeID string

	// Comment is optional on a resolve and MANDATORY on a reject, because on a
	// rejection it is the sentence the author reads. Enforced by the
	// constructors and again by a CHECK in migration 0010: the constructor can
	// be bypassed by an import script and the database cannot.
	Comment    string
	ReviewerID string
}

// Decision is what a reviewer did with a task.
type Decision string

const (
	// DecisionResolve: the reviewer supplied an answer — a role, or the title.
	DecisionResolve Decision = "resolve"

	// DecisionReject: the reviewer looked and no assignment is defensible. The
	// heading is unintelligible, the structure is defective, or the document has
	// no identifiable title and needs one.
	//
	// This means "send it back", not "the machine should not have asked". The
	// second thing may turn out to be worth having, but it is a different verb
	// with a different consequence — a task that closes and goes nowhere — and
	// conflating them would make the run state unreadable.
	DecisionReject Decision = "reject"
)

// Rejected is a nil-safe test used by the overlay and the gate.
func (d *ReviewDecision) Rejected() bool {
	return d != nil && d.Decision == DecisionReject
}

// EffectiveStatus is a classification status after the review overlay is
// applied. It extends ClassificationStatus with the one value only a human can
// produce.
type EffectiveStatus string

const (
	EffectiveResolved   EffectiveStatus = "resolved"
	EffectiveUnresolved EffectiveStatus = "unresolved"

	// EffectiveReviewerConfirmed is never stored on a node. It exists only as a
	// read-time value, and its absence from the section_nodes CHECK constraints
	// is deliberate: a node row that claimed it would mean a human decision had
	// been written over the machine's, which the overlay exists to prevent.
	EffectiveReviewerConfirmed EffectiveStatus = "reviewer_confirmed"

	// EffectiveReviewerRejected is a human looking and finding no answer.
	//
	// Deliberately NOT unresolved. Unresolved means the machine had no answer
	// and nobody has looked yet; this means somebody looked and the question
	// cannot be answered. Collapsing the two would make a finished review
	// indistinguishable from an abandoned one, which is precisely what the run
	// gate has to tell apart.
	EffectiveReviewerRejected EffectiveStatus = "reviewer_rejected"
)

// EffectiveClassification is what a consumer should act on: the machine's
// determination, or a human's decision where one exists.
type EffectiveClassification struct {
	Role         Role
	ContentClass ContentClass
	Status       EffectiveStatus

	// FromReview says whether a human supplied this. Consumers that need to
	// distinguish machine confidence from human judgement — a quality report,
	// say — read this rather than inferring it from Status.
	FromReview bool
}

// EffectiveFor computes §8's read-time overlay for one node.
//
// Authority order is fixed and the same on both axes: a human decision
// overrides the machine determination, for section roles and for the document
// title alike. A node with no decision keeps whatever the machine concluded,
// including an honest "unresolved" — which is never silently inferred into an
// answer.
//
// decision may be nil, which is the ordinary case.
func EffectiveFor(n SectionNode, decision *ReviewDecision) EffectiveClassification {
	// A rejection carries no assignment, so there is nothing to overlay. What it
	// contributes is the status: a reader must not see this node as merely
	// unresolved, because a human has already been here.
	if decision.Rejected() {
		return EffectiveClassification{
			Role:         "",
			ContentClass: "",
			Status:       EffectiveReviewerRejected,
			FromReview:   true,
		}
	}

	if decision != nil {
		return EffectiveClassification{
			Role:         decision.AssignedRole,
			ContentClass: decision.AssignedContentClass,
			Status:       EffectiveReviewerConfirmed,
			FromReview:   true,
		}
	}

	return EffectiveClassification{
		Role:         n.Classification.Role,
		ContentClass: n.Classification.ContentClass,
		Status:       EffectiveStatus(n.Classification.Status),
	}
}

// EffectiveTitle is the document title after the overlay.
type EffectiveTitle struct {
	Text       string
	NodeID     string
	Status     EffectiveStatus
	Method     string
	FromReview bool
}

// EffectiveTitleFor computes the overlay for a run's title.
//
// The single-decision rule applies unchanged here: one authoritative decision
// per title_ambiguity task, corrected in place, and the run's stored title
// fields never overwritten.
func EffectiveTitleFor(run Run, decision *ReviewDecision) EffectiveTitle {
	// A rejected title task means the reviewer could not name the paper either.
	// The run's own determination stays visible as provenance; the status is
	// what changes, for the same reason it does on a node.
	if decision.Rejected() {
		return EffectiveTitle{
			Text:       run.DocumentTitleText,
			Status:     EffectiveReviewerRejected,
			Method:     string(run.DocumentTitleMethod),
			FromReview: true,
		}
	}

	if decision != nil {
		return EffectiveTitle{
			Text:       decision.AssignedDocumentTitleText,
			NodeID:     decision.AssignedDocumentTitleNodeID,
			Status:     EffectiveReviewerConfirmed,
			Method:     "human",
			FromReview: true,
		}
	}

	nodeID := ""
	if run.DocumentTitleOrdinal >= 0 && run.DocumentTitleOrdinal < len(run.NodeIDs) {
		nodeID = run.NodeIDs[run.DocumentTitleOrdinal]
	}

	return EffectiveTitle{
		Text:   run.DocumentTitleText,
		NodeID: nodeID,
		Status: EffectiveStatus(run.DocumentTitleStatus),
		Method: string(run.DocumentTitleMethod),
	}
}

// ReviewContext is what a review surface must show for one task: v2.1 §8.
type ReviewContext struct {
	// AncestorHeadings are the heading_raw of every ancestor, outermost first.
	// HEADINGS ONLY — ancestor body text is excluded.
	AncestorHeadings []string

	// Heading is the node's own heading_raw.
	Heading string

	// StartOffset and EndOffset span the node AND all of its descendants: from
	// the node's own start to the end of its last descendant.
	StartOffset int
	EndOffset   int
}

// Text returns the context body — the node's span unioned with its
// descendants'.
func (c ReviewContext) Text(md []byte) string {
	if c.StartOffset < 0 || c.EndOffset > len(md) || c.StartOffset > c.EndOffset {
		panic("segment: review context span is outside the document")
	}
	return string(md[c.StartOffset:c.EndOffset])
}

// ContextFor builds the review context for the node at the given ordinal.
//
// # Why this exists
//
// §3 gives a parent node only the text between its own heading and its first
// child's. On the reference fixture that leaves the sole multi_role_match node
// — "2 Theoretical background and hypotheses derivation", the one case genuinely
// needing a human to choose between theory and introduction — owning two bytes.
// A reviewer opening it would see the heading and nothing else.
//
// So the context widens in two directions:
//
// DOWNWARD, through the descendants, which is where the content actually is.
//
// UPWARD, through the ancestor HEADINGS, which is where the placement is.
// "2.1 Sample and procedure" is uninterpretable alone and unambiguous beneath
// "2 Theoretical background and hypotheses derivation". Ancestor BODY text is
// excluded deliberately: it is unbounded in length and rarely bears on the
// decision.
//
// Ancestors are whichever exist. A node whose only ancestor is the document
// title contributes one heading — the fixture's sole H4, "#### Abstract", is
// exactly this case, sitting directly beneath the title with no intervening H2
// or H3. The rule is stated by ancestry rather than by enumerated heading level
// because an enumeration over H2/H3/H4 does not cover it.
//
// This is a read-time computation over fields that already exist: no schema
// change, no additional persistence, no effect on classification. The stored
// text_span remains the node's own authoritative span.
func ContextFor(nodes []SectionNode, ordinal int) (ReviewContext, bool) {
	if ordinal < 0 || ordinal >= len(nodes) {
		return ReviewContext{}, false
	}

	n := nodes[ordinal]

	// Walk up the parent chain, collecting headings, then reverse so the
	// outermost comes first.
	var ancestors []string
	for p := n.ParentOrdinal; p >= 0 && p < len(nodes); p = nodes[p].ParentOrdinal {
		ancestors = append(ancestors, nodes[p].HeadingRaw)
	}
	for i, j := 0, len(ancestors)-1; i < j; i, j = i+1, j-1 {
		ancestors[i], ancestors[j] = ancestors[j], ancestors[i]
	}

	// The subtree ends at the first following node that is not a descendant —
	// that is, the first at the same level or shallower. Scanning by level
	// rather than by following parent links keeps this correct when a level is
	// skipped, as it is for the fixture's Abstract.
	end := n.EndOffset
	for i := ordinal + 1; i < len(nodes); i++ {
		if nodes[i].HeadingLevel <= n.HeadingLevel {
			break
		}
		end = nodes[i].EndOffset
	}

	return ReviewContext{
		AncestorHeadings: ancestors,
		Heading:          n.HeadingRaw,
		StartOffset:      n.StartOffset,
		EndOffset:        end,
	}, true
}
