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

	// ReasonRunRejected labels the run-level objection in an author return.
	//
	// It is NOT a review_reason in the schema sense and never appears on a
	// ReviewTask — no task raises it, because its whole purpose is to exist
	// where no task does. It exists so that an AuthorReturnItem can say which
	// kind of objection it carries without a second enum that would have to be
	// kept in step with this one.
	ReasonRunRejected ReviewReason = "run_rejected"

	// ReasonNoStructure: the document has no headings at all, so §5 produced a
	// single synthetic whole-document node.
	//
	// This is a SEPARATE question from the title one, and the separation is the
	// whole point. Such a document also has no H1, so it already raises a
	// title_ambiguity task and could never pass the gate unlooked-at. But that
	// task asks what the paper is CALLED. A reviewer can answer it perfectly
	// well while the document still has no structural signal of any kind, and
	// the run would pass.
	//
	// One decision per task means the two cannot be merged: "the paper is
	// called X" and "this document is unusable" are different answers, and a
	// reviewer may reasonably want to give the first and reject on the second.
	//
	// The node's own classification is untouched. It stays resolved Unknown and
	// the run stays Completed, exactly as title_ambiguity leaves the title
	// fields alone. This is a gate requirement, not a classification failure.
	ReasonNoStructure ReviewReason = "no_structure"
)

// TaskStatus is a review task's lifecycle state.
//
// TaskRejected is the third state and the reason Step 3R exists. Without it,
// "nobody has looked at this" and "somebody looked and could not answer" are
// the same row, and a run has no way to tell an unfinished review from a
// finished one that failed.
type TaskStatus string

const (
	TaskOpen     TaskStatus = "open"
	TaskResolved TaskStatus = "resolved"
	TaskRejected TaskStatus = "rejected"
)

// ReviewState is a run's gate state, computed from its tasks and never stored.
//
// Not stored for the same reason the effective classification is not stored: it
// is derived from rows that already exist, and a stored copy is a second place
// for one fact to live. The two would eventually disagree, and nothing would say
// which was right.
type ReviewState string

const (
	// ReviewOpen: at least one task has no decision. Step 4 must not run.
	ReviewOpen ReviewState = "open"

	// ReviewPassed: every task decided, none rejected. Step 4 consumes the
	// effective classification. A run that raised no tasks at all is passed
	// immediately, which is the ordinary machine-only case.
	ReviewPassed ReviewState = "passed"

	// ReviewReturned: every task decided, at least one rejected. The manuscript
	// goes back to the author with the rejection comments.
	//
	// One rejection returns the WHOLE manuscript. Partial consumption of a
	// half-good segmentation is not defined, and inventing it here would mean
	// Step 4 acting on a document a reviewer said was defective.
	ReviewReturned ReviewState = "returned"
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

	// NodeIDs and TaskIDs are parallel to Nodes and Tasks, assigned by the
	// service layer before persistence.
	//
	// Identity is kept alongside the values rather than inside them so this
	// package never needs a UUID generator. That is what holds the import set
	// down to goldmark and keeps the architecture guard meaningful: with no
	// generator and no ports, there is nothing in here that could be made
	// non-deterministic by a wiring change.
	NodeIDs []string
	TaskIDs []string
}

// StructuralRuleVersion is the value persisted on every run produced by this
// implementation.
//
// It stayed "2.0" through the whole of 2.1, because those amendments clarified
// offset semantics, review context, title parentage and the input trust
// boundary without changing what came out. A node set produced under 2.0 and
// one produced under 2.1 were the same node set, and distinguishing them would
// have been a lie.
//
// 2.2 is the first version that changes classifications, so it is the first
// that earns a new number. Two rules were added:
//
//   - A section whose heading matched nothing takes its parent's role, recorded
//     as MethodInherited. This relaxes §3's parent-independence, which ruled out
//     rescue mechanisms by name.
//   - An appendix whose suffix matched nothing resolves to Unknown structurally
//     rather than raising a question, matching what a bare "Appendix B" already
//     did.
//
// On the reference fixture the visible effect is one node: "4.2 Structural
// model" now inherits results from "4 Data analysis and results", and §15's
// review-task count goes from six to five.
//
// 2.3 adds the rule that runs the other way. A section that matched nothing, and
// has no parent to inherit from, takes the role every one of its subsections
// independently matched. It requires unanimity among at least two children, each
// of which resolved by MethodRule — a child that inherited its role is an echo,
// not a second opinion, which also means the rule never chains.
//
// The reference fixture is UNCHANGED by 2.3, and deliberately so: its one
// multi-role heading is the parent of its four zero-match ones, so a rule that
// respects both limits has nothing to do there. TestConsensus_DoesNotDisturbThe
// Fixture asserts that rather than leaving it to be noticed later.
//
// 2.4 removes one keyword: "boundary conditions" from results. No rule changed.
//
// A keyword change earns a number by the same test 2.2 set. This field exists so
// a reader of stored data knows which rules produced it, and the keyword set is
// part of those rules — two runs under different keyword sets can classify the
// same heading differently, which is exactly what the version is for.
//
// 2.5 stops classifying appendix suffixes. Every appendix now resolves to
// Unknown / analytical / structural, whatever its title says.
//
// Through 2.4, "Appendix B: Robustness checks" was RESULTS and "Appendix B" was
// Unknown, so the same container answered differently depending on how much its
// author wrote in the heading. The ruling is that an appendix title says what
// the appendix is ABOUT, not what epistemic work it does: "Detailed Results of
// Model Selection" reads like results and may equally be methodology moved out
// of the body, and which part of a paper an appendix supports is not
// recoverable from its title. The suffix is still parsed and retained in
// SemanticHeading; it is simply no longer read as a role.
//
// 2.6 stops classifying the first node of a document that has NO H1 at all, when
// that node sits at the shallowest heading level present.
//
// Mathpix emits an H1 or not depending on a PDF's typography, not on whether the
// document has a title, and two of the first four real papers had none. Their
// titles came through as H2s and ran the ordinary pipeline: one resolved to
// THEORY with a three-byte span, which Step 4 would have read as content.
//
// It SUPPRESSES rather than promotes. The heuristic that would gate promotion —
// a title matches no keyword — fails on the very paper that raised the problem.
// With no reliable signal, the honest move is to stop asserting one: the node
// keeps its text, its span and its place in the tree, carries no role, and the
// title_ambiguity task points at it so a reviewer has a candidate to confirm
// rather than a blank question about the whole document.
//
// 2.7 suppresses a keyword occurrence whose span lies strictly inside another
// occurrence's span, before distinct roles are counted.
//
// Five keywords sit inside a longer keyword of a different role — `background`
// inside `theoretical background`, `results` inside `discussion of results`, and
// three more. Whenever the longer fires the shorter fires too, and the pair looks
// like two roles disagreeing when it is one span read twice.
//
// The rule is stated over SPANS rather than keywords, and that distinction is the
// whole of it. An earlier draft said "discard the shorter KEYWORD", which would
// have resolved "Background and theoretical background" to theory by discarding
// both occurrences of `background` — including the standalone one that was real
// evidence. GPT caught it; the counter-example reproduces exactly.
//
// FIRST VERSION TO CHANGE THE REFERENCE FIXTURE. demo.md's sole multi_role_match
// was this same illusion, so it resolves to theory, its four subsections inherit,
// and §15 goes from five review tasks to NONE.
//
// 2.8 closes two gaps in 2.6's title-candidate rule, found by tests that 2.7
// forced a proper re-run of. A structural container is never a title candidate,
// and neither is a heading that IS a role keyword.
//
// "Appendix B" is not what a paper is called. Neither is "Methodology". 2.6
// tested only whether a node was first and shallowest, so on a short document
// beginning with either, it un-resolved a perfectly good answer to ask a
// question nobody needed asked.
//
// The second test is EXACT match, not "resolved by rule", and that is the whole
// care in it. §4's existing wording for H1s says a first heading "resolving to
// an ordinary role" is that section — but the systematic review's title resolved
// to `theory`, because the title reads "…A theoretical framework of supply chain
// adaptations…". Reusing §4's looser test would have let that paper's title keep
// a role it should never have had, which is the case 2.6 exists for. Containing
// a role keyword is something titles do; BEING one is not.
// 2.9 recovers a references heading that Mathpix left as plain text.
//
// FOUND BY MEASUREMENT, not by reasoning. Four of the ten ingested papers carry
// the word "References" on its own line with no heading markers. Step 3 is
// heading-driven, so no citation_source node was created and the bibliography
// was absorbed by whatever section preceded it:
//
//	"5.3. Future Directions"                     91% reference list
//	"6. Further developments"                    88% reference list
//	"10. Conclusion, limitations, and scope…"    85% reference list
//	"6. Implications and recommendations…"       85% reference list
//
// Anything reading those sections was reading somebody else's bibliography, and
// nothing failed to say so. That is wrong for every consumer, not only for the
// citation work that exposed it.
//
// THE REPAIR CANNOT BE MADE TO THE TEXT. approved_markdown is fingerprinted and
// every offset in the system indexes into it, so editing the markdown to insert
// a heading would invalidate every stored span in every prior run. This version
// changes only how the same bytes are read.
//
// Nodes now carry HeadingSource, so an inferred heading is never mistaken for
// one the document actually had. On the six papers with a real references
// heading, 2.9 changes nothing at all.
const StructuralRuleVersion = "2.9"

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

		// The suppressed title candidate is unresolved on purpose, and the
		// title_ambiguity task below already points at it. Raising a
		// zero_role_match here as well would put the same section in the queue
		// twice, asking a reviewer to answer one question in two places.
		if n.Ordinal == doc.TitleCandidateOrdinal {
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

	// A document with no headings at all raises its own question (3R §2).
	//
	// Detected by the shape §5 produces for that case and nothing else: exactly
	// one node, which is the whole document, resolved structurally. Testing the
	// shape rather than re-deriving "were there headings" keeps this true for
	// any future path that legitimately produces a single synthetic node.
	//
	// This is NOT the same question as the title task below, and merging them
	// was considered and rejected. There is one decision per task, so a merged
	// task would force a reviewer who can name the paper but considers it
	// structurally unusable to answer only one of those.
	//
	// The node's classification is untouched. It stays resolved Unknown and the
	// run stays Completed. The task is a gate requirement, exactly as
	// title_ambiguity is, not a report of a classification failure.
	if len(doc.Nodes) == 1 &&
		doc.Nodes[0].ParentOrdinal == -1 &&
		doc.Nodes[0].HeadingLevel == 0 &&
		doc.Nodes[0].Classification.Method == MethodStructural {
		run.Tasks = append(run.Tasks, ReviewTask{
			SectionOrdinal: doc.Nodes[0].Ordinal,
			Reason:         ReasonNoStructure,
			Status:         TaskOpen,
		})
	}

	// An unidentified title is an open question too, and §4 is explicit that
	// nothing is auto-promoted. Raising the task is what stops "no title" from
	// quietly becoming "no title needed".
	if doc.TitleStatus == TitleUnresolved {
		// Point at the candidate when there is one (2.6). A task carrying -1
		// asks "what is this paper called?" against a whole document; one
		// carrying an ordinal asks "is this it?" against a specific heading,
		// which is a question a reviewer can answer by looking.
		run.Tasks = append(run.Tasks, ReviewTask{
			SectionOrdinal: doc.TitleCandidateOrdinal,
			Reason:         ReasonTitleAmbiguity,
			Status:         TaskOpen,
		})
	}

	return run
}
