package segment

// RunStatus is a segmentation run's terminal state.
type RunStatus string

const (
	RunProcessing RunStatus = "Processing"
	RunCompleted  RunStatus = "Completed"
	RunFailed     RunStatus = "Failed"
)

// ReviewReason says why a human is being asked.
type ReviewReason string

const (
	// ReasonZeroRoleMatch: no keyword matched. No candidates are offered — the
	// reviewer chooses from the full role set.
	ReasonZeroRoleMatch ReviewReason = "zero_role_match"

	// ReasonMultiRoleMatch: two or more distinct roles matched. The candidates
	// are offered as a shortlist.
	ReasonMultiRoleMatch ReviewReason = "multi_role_match"

	// ReasonTitleAmbiguity: §4 could not identify the document title. Nothing
	// is auto-promoted, so the question goes to a human.
	ReasonTitleAmbiguity ReviewReason = "title_ambiguity"
)

// TaskStatus is a review task's lifecycle state.
type TaskStatus string

const (
	TaskOpen     TaskStatus = "open"
	TaskResolved TaskStatus = "resolved"
)

// ReviewTask is one open question about one node.
//
// Heading and section text are deliberately absent. §8 retrieves them via the
// node instead, so there is exactly one authoritative copy and no possibility
// of a task quoting text that the node no longer has.
type ReviewTask struct {
	// ID is assigned by the service layer before persistence. The domain does
	// not generate identifiers: keeping uuid out of this package is what lets
	// the architecture guard hold the import set down to goldmark alone.
	ID string

	// SectionOrdinal is the node this concerns, or -1 for a title_ambiguity
	// task on a document with no H1 node at all.
	SectionOrdinal int

	Reason ReviewReason

	// CandidateRoles is populated only for ReasonMultiRoleMatch, sorted.
	CandidateRoles []Role

	// MatchedKeywords are the keywords that fired, sorted. Empty for a
	// zero-match.
	MatchedKeywords []string

	Status TaskStatus
}

// Run is one segmentation of one document: the §8 aggregate.
//
// The three ID fields are assigned by the service layer. The domain builds the
// structure and leaves identity to the caller.
type Run struct {
	ID string

	// ExtractionRunID is whatever reference the ApprovedMarkdownSource
	// supplied. Under the current adapter it is a paper id, not an
	// ExtractionRun id — see the adapter's comment for what that costs.
	ExtractionRunID string

	// ApprovedMarkdownHash is the hex SHA-256 of the exact markdown every
	// offset below indexes into. Without it the offsets are unverifiable, and
	// unverifiable offsets slice the wrong bytes silently.
	ApprovedMarkdownHash string

	// StructuralRuleVersion stays "2.0" through the 2.1 amendments: those were
	// clarifications and changed no behaviour, so a node set produced under
	// either is interpreted identically.
	StructuralRuleVersion string

	DocumentTitleLevel  int
	SupportedNodeLevels []int
	EmbeddedLevels      []int
	HeadingCounts       map[int]int

	// The §4 determination. Never overwritten by a human decision; the
	// effective title is computed at read time.
	DocumentTitleText        string
	DocumentTitleOrdinal     int
	DocumentTitleSourceLevel int
	DocumentTitleStatus      TitleStatus
	DocumentTitleMethod      TitleMethod

	Status        RunStatus
	FailureReason string

	Nodes []SectionNode
	Tasks []ReviewTask
}

// StructuralRuleVersion is the value persisted on every run produced by this
// implementation.
//
// It is "2.0" and not "2.1" on purpose. The 2.1 amendments clarified offset
// semantics, review context, title parentage and the input trust boundary;
// none of them changes what nodes come out or how they are classified, so a
// node set produced under 2.0 and one produced under 2.1 are the same node set
// and must not be distinguished by this field.
const StructuralRuleVersion = "2.0"

// NewRun assembles a persistable run from a segmented document, including one
// review task per unresolved node and one for an unidentified title.
//
// Task generation lives here rather than in the persistence layer because it is
// a rule, not a storage concern: §8 says one task per unresolved classification,
// and the two must not be able to drift apart. A store that could write nodes
// without their tasks would produce a run where questions had silently
// disappeared, which looks exactly like a run where none were needed.
//
// IDs are left empty for the service layer to assign.
func NewRun(doc Document, extractionRunID, markdownHash string) Run {
	run := Run{
		ExtractionRunID:       extractionRunID,
		ApprovedMarkdownHash:  markdownHash,
		StructuralRuleVersion: StructuralRuleVersion,
		DocumentTitleLevel:    1,
		SupportedNodeLevels:   []int{2, 3, 4},
		EmbeddedLevels:        []int{5, 6},
		HeadingCounts:         doc.HeadingCounts,
		DocumentTitleOrdinal:  doc.TitleOrdinal,
		DocumentTitleStatus:   doc.TitleStatus,
		DocumentTitleMethod:   doc.TitleMethod,
		Status:                RunCompleted,
		Nodes:                 doc.Nodes,
	}

	if title, ok := doc.Title(); ok {
		run.DocumentTitleText = title.HeadingRaw
		run.DocumentTitleSourceLevel = title.HeadingLevel
	}

	for _, n := range doc.Nodes {
		if n.Classification.Status != StatusUnresolved {
			continue
		}

		reason := ReasonZeroRoleMatch
		if len(n.Classification.CandidateRoles) > 0 {
			reason = ReasonMultiRoleMatch
		}

		run.Tasks = append(run.Tasks, ReviewTask{
			SectionOrdinal:  n.Ordinal,
			Reason:          reason,
			CandidateRoles:  n.Classification.CandidateRoles,
			MatchedKeywords: n.Classification.MatchedKeywords,
			Status:          TaskOpen,
		})
	}

	// An unidentified title is an open question too, and §4 is explicit that
	// nothing is auto-promoted. Raising the task is what stops "no title" from
	// quietly becoming "no title needed".
	if doc.TitleStatus == TitleUnresolved {
		run.Tasks = append(run.Tasks, ReviewTask{
			SectionOrdinal: -1,
			Reason:         ReasonTitleAmbiguity,
			Status:         TaskOpen,
		})
	}

	return run
}
