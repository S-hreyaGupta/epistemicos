package segment

// Role is a section's semantic function — what epistemic work the section does,
// independent of where in the document it sits.
//
// The empty Role is a valid and meaningful value: v2.0 §6 assigns it to a node
// whose heading matched no keyword or matched several, and pairs it with an
// unresolved status and a ReviewTask. That is a change from 1.1, which reached
// for a placeholder role instead. The distinction matters because a placeholder
// is indistinguishable from a confident answer once it is persisted, whereas an
// empty role with an unresolved status states plainly that the machine did not
// decide.
//
// RoleUnknown is different again and must not be confused with either. It is a
// deliberate structural assignment, never a failure — see its own comment.
type Role string

// The sixteen section roles of v2.0. This set is closed: §6 classifies against
// these and nothing else, and an implementation that invents a seventeenth is
// not conforming.
const (
	RoleAbstract            Role = "abstract"
	RoleIntroduction        Role = "introduction"
	RoleLiteratureReview    Role = "literature_review"
	RoleTheory              Role = "theory"
	RoleMethodology         Role = "methodology"
	RoleResults             Role = "results"
	RoleDiscussion          Role = "discussion"
	RoleLimitations         Role = "limitations"
	RoleConclusion          Role = "conclusion"
	RoleAcknowledgments     Role = "acknowledgments"
	RoleFunding             Role = "funding"
	RoleAuthorContributions Role = "author_contributions"
	RoleDataAvailability    Role = "data_availability"
	RoleEthicsStatement     Role = "ethics_statement"
	RoleConflictOfInterest  Role = "conflict_of_interest"
	RoleReferences          Role = "references"
)

// RoleUnknown is the synthetic role from the table's synthetic_roles block.
//
// It is assigned in exactly two situations, both of them deliberate: a document
// with no headings at all, and a structural container carrying no semantic
// suffix — a bare "Appendix B", or an alias like "Supporting information".
//
// It is NOT what an unclassifiable heading receives. That distinction is the
// whole reason the value exists separately. "Appendix B" has no epistemic claim
// to classify, so calling it Unknown is a complete and correct answer and no
// human should ever be asked about it. A heading like "2.1 Sample and
// procedure" that matched nothing is an open question, and it gets an empty
// role, an unresolved status and a ReviewTask. Collapsing the two would bury
// every genuine question in a pile of appendix headings.
const RoleUnknown Role = "Unknown"

// ContentClass is the handling category a role implies — what Step 4 should do
// with the section, as distinct from what the section is.
//
// It is derived from the role and never assigned independently, which is what
// keeps the two axes from drifting: a role's class is a property of the role.
type ContentClass string

const (
	ClassAnalytical           ContentClass = "analytical"
	ClassAdministrative       ContentClass = "administrative"
	ClassComplianceDisclosure ContentClass = "compliance_disclosure"
	ClassCitationSource       ContentClass = "citation_source"
)

// ClassificationStatus records whether the machine reached an answer.
type ClassificationStatus string

const (
	// StatusResolved means a role was determined, by keyword or by structure.
	StatusResolved ClassificationStatus = "resolved"

	// StatusUnresolved means it was not, and a ReviewTask exists. The role is
	// empty and MUST NOT be filled with a guess: §8's overlay model lets a
	// human decision take effect at read time without ever overwriting the
	// machine's stored determination, and that only works if the stored value
	// honestly records having no answer.
	StatusUnresolved ClassificationStatus = "unresolved"
)

// ClassificationMethod records how a resolved role was reached, so a reader can
// tell a keyword match from a structural assignment without inferring it.
type ClassificationMethod string

const (
	// MethodRule: matched the role table.
	MethodRule ClassificationMethod = "rule"

	// MethodStructural: assigned by §7's container rule, not by any keyword.
	MethodStructural ClassificationMethod = "structural"

	// MethodInherited: no keyword matched, so the node took its parent's role.
	//
	// This is deliberately its OWN method rather than being folded into
	// MethodRule. An inherited role is a weaker claim than a matched one — it
	// says "this sits under a methodology section" rather than "this heading
	// says methodology" — and the two must stay distinguishable in the stored
	// data. Merging them would make it impossible to ask afterwards how many
	// roles were guessed from position, or to check whether the guess was right.
	//
	// Same principle as never overwriting the machine's answer with a human's:
	// keep the provenance, and let a reader decide how much to trust it.
	MethodInherited ClassificationMethod = "inherited"

	// MethodChildConsensus: no keyword matched, so the node took the role that
	// every one of its subsections independently matched.
	//
	// The evidence here runs the opposite way to MethodInherited, and it is a
	// different kind of claim, so it gets a different value rather than being
	// folded in. "This sits under a methodology section" and "everything
	// underneath this says results" are not interchangeable, and a reader who
	// cannot tell them apart cannot audit either.
	//
	// The word INDEPENDENTLY is doing the work. Consensus is only evidence
	// because each subsection reached its role from its own heading, without
	// consulting the parent or each other. That is why only MethodRule children
	// count: a child that inherited its role is not a second opinion, it is an
	// echo, and counting echoes as agreement would manufacture confidence out of
	// a single fact.
	MethodChildConsensus ClassificationMethod = "child_consensus"
)

// NodeKind separates a node's structural position from its semantic role, which
// is the axis separation v2.0 introduced and 1.1 lacked.
//
// Under 1.1 the document root was a ROLE value, which meant asking "what is
// this section about" and "where does this sit in the tree" returned answers
// from the same enum, and the title could not be given a role without lying
// about one or the other. v2.0 puts the title on this axis instead and leaves
// its primary_role null.
type NodeKind string

const (
	// KindDocumentTitle is the paper's title. At most one node per run carries
	// it, and only the first H1 is ever a candidate (§4).
	KindDocumentTitle NodeKind = "document_title"

	// KindSection is every other node, including any H1 after the first. A
	// second H1 is anomalous but not special-cased: it classifies through the
	// ordinary pipeline like anything else.
	KindSection NodeKind = "section"
)

// roleContentClass maps each role to its handling category. Mirrors the
// content_class of each entry in the table's section_roles block;
// TestRoleTableMatchesTable proves it has not drifted.
var roleContentClass = map[Role]ContentClass{
	RoleAbstract:            ClassAnalytical,
	RoleIntroduction:        ClassAnalytical,
	RoleLiteratureReview:    ClassAnalytical,
	RoleTheory:              ClassAnalytical,
	RoleMethodology:         ClassAnalytical,
	RoleResults:             ClassAnalytical,
	RoleDiscussion:          ClassAnalytical,
	RoleLimitations:         ClassAnalytical,
	RoleConclusion:          ClassAnalytical,
	RoleAcknowledgments:     ClassAdministrative,
	RoleFunding:             ClassAdministrative,
	RoleAuthorContributions: ClassAdministrative,
	RoleDataAvailability:    ClassComplianceDisclosure,
	RoleEthicsStatement:     ClassComplianceDisclosure,
	RoleConflictOfInterest:  ClassAdministrative,
	RoleReferences:          ClassCitationSource,

	// The synthetic role is analytical by the table's synthetic_roles block.
	// An appendix usually holds analytical content, so this is the least
	// misleading default for a container whose contents are not yet known.
	RoleUnknown: ClassAnalytical,
}

// ContentClassFor returns the handling category a role implies.
//
// An unrecognised role yields the empty class rather than a default. A silent
// fallback to analytical would make a typo in a role constant look like a
// working classification, and the caller cannot tell the two apart afterwards.
func ContentClassFor(r Role) ContentClass {
	return roleContentClass[r]
}
