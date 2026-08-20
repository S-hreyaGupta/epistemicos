package researchunit

import "fmt"

// UnitType is what kind of thing a research unit is. Only one value today; the
// type exists because the specification anticipates others and a string column
// with one legal value is cheaper to widen than a boolean is to replace.
type UnitType string

const UnitStudy UnitType = "study"

// Status records how a unit came to exist.
type Status string

const (
	// StatusAcceptedSingleStudy: the gate found one study and this was created
	// automatically. The only status the MVP produces.
	//
	// Named for how it was reached rather than as "active", because single-study
	// status is a SCOPE CONDITION we imposed, not a property of the paper we
	// discovered. A later reader must be able to tell that this unit exists
	// because we only handle one-study papers, not because somebody established
	// the paper has exactly one study.
	StatusAcceptedSingleStudy Status = "accepted_single_study"

	// StatusHumanConfirmed: a person resolved an uncertain gate in favour of one
	// study. Distinguished from the automatic case for the same reason a human
	// section role is distinguished from a machine one.
	StatusHumanConfirmed Status = "human_confirmed"
)

// Unit is one research unit: the parent object that methods, data, analyses,
// claims and evidence will later attach to.
type Unit struct {
	// ID is the database identity, assigned by the service layer. This package
	// generates no identifiers, which is what keeps its import set to the
	// standard library and the architecture guard meaningful.
	ID string

	PaperID string

	Type  UnitType
	Index int

	// Ref is the human-facing handle from the specification: "RU1".
	//
	// Kept ALONGSIDE the UUID rather than instead of it. "RU1" is unique within a
	// paper and not across the corpus, so it cannot be a primary key — but it is
	// what the specification's examples use and what a person reads in output,
	// and inventing a different name would make the two documents disagree.
	Ref string

	// Label is the study's name as a reader would say it: "Study 1".
	Label string

	Status Status
}

// NewSingleStudy builds the RU1 the specification asks for.
//
// It is created rather than inferred, and that is the point: the specification is
// explicit that single-study status is a scope condition, so there is nothing for
// a model to reconstruct. The gate has already refused everything else.
//
// The ID is left empty for the service to assign.
func NewSingleStudy(paperID string, status Status) Unit {
	return Unit{
		PaperID: paperID,
		Type:    UnitStudy,
		Index:   1,
		Ref:     "RU1",
		Label:   "Study 1",
		Status:  status,
	}
}

// Scope says whether a section belongs to the study, to the manuscript, or to
// both.
type Scope string

const (
	// ScopeManuscript: the section is about the paper, not the study. An abstract
	// describes the whole document; a reference list belongs to no study.
	ScopeManuscript Scope = "manuscript"

	// ScopeStudy: the section reports the study.
	ScopeStudy Scope = "study"

	// ScopeBoth: the section carries statements of both kinds.
	//
	// Introductions and discussions do this constantly — an introduction motivates
	// the paper AND states the study's question; a discussion interprets the
	// results AND makes claims about the literature. The split is real but it is a
	// PARAGRAPH-level split, and this layer works at section level.
	//
	// Recording "both" is therefore the accurate answer, not a hedge. Forcing one
	// side would produce a value indistinguishable from a confident one, and the
	// error would only surface when claim extraction started attributing a
	// literature claim to a study that never tested it.
	ScopeBoth Scope = "both"

	// ScopeUndetermined: an appendix, whose contents decide and whose heading does
	// not say. §7 already refuses to read a role off an appendix title for the same
	// reason.
	ScopeUndetermined Scope = "undetermined"
)

// scopeByRole maps Step 3's section roles onto the specification's split.
//
// The mapping is deliberately explicit rather than defaulted, so that a role added
// to the table later fails loudly here instead of quietly becoming study-level.
var scopeByRole = map[string]Scope{
	"abstract":             ScopeManuscript,
	"references":           ScopeManuscript,
	"acknowledgments":      ScopeManuscript,
	"funding":              ScopeManuscript,
	"author_contributions": ScopeManuscript,
	"data_availability":    ScopeManuscript,
	"ethics_statement":     ScopeManuscript,
	"conflict_of_interest": ScopeManuscript,

	"literature_review": ScopeManuscript,

	"theory":      ScopeStudy,
	"methodology": ScopeStudy,
	"results":     ScopeStudy,
	"limitations": ScopeStudy,

	"introduction": ScopeBoth,
	"discussion":   ScopeBoth,
	"conclusion":   ScopeBoth,

	// §7's synthetic role, carried by every appendix and by a document with no
	// headings at all.
	"Unknown": ScopeUndetermined,
}

// ScopeForRole returns where a section belongs, and whether the role was known.
//
// An unrecognised role returns false rather than a default. A silent fallback
// would make a typo look like a working assignment, and the caller could not tell
// the two apart afterwards — the same reasoning as ContentClassFor.
func ScopeForRole(role string) (Scope, bool) {
	s, ok := scopeByRole[role]
	return s, ok
}

// Assignment is one section's placement.
type Assignment struct {
	SectionOrdinal int
	Heading        string
	Role           string
	Scope          Scope

	// UnitRef is "RU1" when the section belongs to the study, empty otherwise.
	// Empty for manuscript-level sections is the correct value, not a missing one:
	// a reference list genuinely belongs to no study.
	UnitRef string
}

// Assign places every section relative to the unit.
//
// The document title is skipped: it carries no role by design (§4), and the
// two-axis model exists precisely so the title is not made to claim one.
func Assign(headings []Heading, unit Unit) []Assignment {
	out := make([]Assignment, 0, len(headings))

	for _, h := range headings {
		a := Assignment{
			SectionOrdinal: h.Ordinal,
			Heading:        h.Text,
			Role:           h.Role,
		}

		switch scope, known := ScopeForRole(h.Role); {
		case h.Role == "":
			// No role: either the document title, or a section Step 3 could not
			// classify and raised a question about. Neither is placeable, and
			// guessing here would answer a question a human is already being asked.
			a.Scope = ScopeUndetermined
		case !known:
			a.Scope = ScopeUndetermined
		default:
			a.Scope = scope
		}

		if a.Scope == ScopeStudy || a.Scope == ScopeBoth {
			a.UnitRef = unit.Ref
		}

		out = append(out, a)
	}

	return out
}

// Summary counts assignments by scope, for output that says how much of a paper
// was placed rather than only where.
func Summary(as []Assignment) map[Scope]int {
	counts := map[Scope]int{}
	for _, a := range as {
		counts[a.Scope]++
	}
	return counts
}

func (g Gate) String() string {
	return fmt.Sprintf("%s: %s", g.Verdict, g.Reason)
}
