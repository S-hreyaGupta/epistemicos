package researchunit

import (
	"strings"
	"testing"
)

func headings(pairs ...string) []Heading {
	out := make([]Heading, 0, len(pairs))
	for i, p := range pairs {
		out = append(out, Heading{Ordinal: i, Level: 2, Text: p})
	}
	return out
}

// The real multi-study paper's heading list, abridged but verbatim.
//
// This is the whole reason the gate exists. Note where "3. Research methodology"
// sits: BEFORE all three studies, and on its own. A gate that looked only at the
// methodology section would see no studies at all and let a three-study paper
// through as one.
func TestDetect_TheRealMultiStudyPaper(t *testing.T) {
	got := Detect(headings(
		"2. Theoretical framework, review of literature, and hypotheses development",
		"3. Research methodology",
		"4. Study 1: Elicitation study of belief constructs",
		"4.1. Study 1A: Focus group discussions",
		"4.2. Study 1B: Administering an open-ended questionnaire",
		"5. Content analysis",
		"6. Results",
		"7. Study 2: Development and validation of indirect and direct measures",
		"7.2. Study 2A: Content validity",
		"7.3. Study 2B: Face validity",
		"8. Study 3: Validation study",
		"9. Discussions and implications",
	), "")

	if got.Verdict != VerdictMulti {
		t.Fatalf("verdict = %q, want %q (%s)", got.Verdict, VerdictMulti, got.Reason)
	}

	// Three studies, not seven. 1A and 1B are parts of Study 1.
	if got.StudyCount != 3 {
		t.Errorf("study count = %d, want 3 — 1A and 1B belong to Study 1, 2A and 2B to Study 2", got.StudyCount)
	}
	if !strings.Contains(got.Reason, "1, 2, 3") {
		t.Errorf("reason = %q, want it to name the three studies", got.Reason)
	}
}

// TestDetect_SubLabelsAreNotSeparateStudies is the correction the specification
// needed. A paper that splits its one study into halves is still one study.
func TestDetect_SubLabelsAreNotSeparateStudies(t *testing.T) {
	got := Detect(headings(
		"3. Method",
		"3.1. Study 1A: Focus group discussions",
		"3.2. Study 1B: Open-ended questionnaire",
		"4. Results",
	), "")

	if got.Verdict != VerdictSingle {
		t.Fatalf("verdict = %q, want %q — 1A and 1B are one study (%s)", got.Verdict, VerdictSingle, got.Reason)
	}
	if got.StudyCount != 1 {
		t.Errorf("study count = %d, want 1", got.StudyCount)
	}
}

func TestDetect_SingleStudyPapers(t *testing.T) {
	cases := [][]string{
		{"1 INTRODUCTION", "2 LITERATURE REVIEW", "3 THEORETICAL FRAMEWORK", "4 METHODOLOGY", "5 EMPIRICAL ANALYSIS", "6 DISCUSSION"},
		{"Abstract", "Introduction", "Method", "Results", "Discussion", "References"},
		{},
	}

	for i, hs := range cases {
		got := Detect(headings(hs...), "")
		if got.Verdict != VerdictSingle {
			t.Errorf("case %d: verdict = %q, want %q (%s)", i, got.Verdict, VerdictSingle, got.Reason)
		}
	}
}

func TestDetect_ExperimentsAndRomanNumerals(t *testing.T) {
	cases := []struct {
		name string
		hs   []string
	}{
		{"experiments", []string{"Experiment 1: Pilot", "Experiment 2: Replication"}},
		{"roman numerals", []string{"Study I", "Study II"}},
		{"mixed kinds", []string{"Study 1: Survey", "Experiment 2: Lab"}},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := Detect(headings(c.hs...), ""); got.Verdict != VerdictMulti {
				t.Errorf("verdict = %q, want %q (%s)", got.Verdict, VerdictMulti, got.Reason)
			}
		})
	}
}

// TestDetect_AmbiguousHeadingsGoToAHuman. Phases and samples are usually stages
// of one study and occasionally not, and only reading them settles it. This is
// the case a model would earn its place on; it fires on none of the ten papers.
func TestDetect_AmbiguousHeadingsGoToAHuman(t *testing.T) {
	for _, hs := range [][]string{
		{"Phase 1: Recruitment", "Phase 2: Follow-up"},
		{"Sample 1", "Sample 2"},
		{"Dataset 1: Training", "Dataset 2: Holdout"},
	} {
		got := Detect(headings(hs...), "")
		if got.Verdict != VerdictUncertain {
			t.Errorf("%v: verdict = %q, want %q (%s)", hs, got.Verdict, VerdictUncertain, got.Reason)
		}
	}
}

// TestDetect_ProseCannotEstablishMulti is the asymmetry that keeps this honest.
//
// A heading is the document's structural claim about ITSELF. A sentence is not:
// a related-work section discussing "Study 1 of Peldszus and Stede" is describing
// somebody else's research. So prose raises a question and never settles one.
func TestDetect_ProseCannotEstablishMulti(t *testing.T) {
	md := "## 2 Related work\n\nAs shown in Study 1 of Smith et al. and later in Study 2 of Jones,\n" +
		"the effect is well documented.\n\n## 3 Method\n\nWe surveyed 200 firms.\n"

	got := Detect(headings("2 Related work", "3 Method"), md)

	if got.Verdict != VerdictUncertain {
		t.Fatalf("verdict = %q, want %q — prose mentions must raise a question, not settle one (%s)",
			got.Verdict, VerdictUncertain, got.Reason)
	}
	if got.StudyCount != 0 {
		t.Errorf("study count = %d, want 0 — nothing was found in the headings", got.StudyCount)
	}
	if !strings.Contains(got.Reason, "other authors") {
		t.Errorf("reason = %q, want it to explain why this is a question rather than a verdict", got.Reason)
	}
}

// TestDetect_SurvivesMathpixFlatteningTheHeadings.
//
// Not hypothetical. In four of the ten ingested papers Mathpix emitted
// "References" as PLAIN TEXT rather than a heading — the word is there, the
// heading is not. If it can do that to a reference list it can do it to
// "Study 2", and this gate reads headings.
//
// So the safety net has to hold: with every study heading flattened, the paper
// must NOT come back single. It comes back uncertain, because the prose still
// names three studies — rule 2, where prose raises a question and never settles
// one. Verified against the real multi-study paper: flattening its Study
// headings turns "multi" into "uncertain", never into "single".
func TestDetect_SurvivesMathpixFlatteningTheHeadings(t *testing.T) {
	// The same paper, with its "Study N" headings demoted to body text.
	md := "## 3. Research methodology\n\nWe describe the three studies below.\n\n" +
		"4. Study 1: Elicitation study of belief constructs\n\n" +
		"Focus groups were run with 24 participants.\n\n" +
		"7. Study 2: Development and validation of measures\n\n" +
		"Scale items were drafted and reviewed.\n\n" +
		"8. Study 3: Validation study\n\n" +
		"A confirmatory factor analysis was conducted.\n"

	got := Detect(headings("3. Research methodology"), md)

	if got.Verdict == VerdictSingle {
		t.Fatalf("a three-study paper passed as single once its headings were flattened (%s)", got.Reason)
	}
	if got.Verdict != VerdictUncertain {
		t.Errorf("verdict = %q, want %q", got.Verdict, VerdictUncertain)
	}
	// Nothing was found in the headings, which is exactly the point.
	if got.StudyCount != 0 {
		t.Errorf("study count = %d, want 0 — the headings carry nothing", got.StudyCount)
	}
}

// One study named in prose is not a signal at all.
func TestDetect_OneProseMentionIsFine(t *testing.T) {
	md := "## 3 Method\n\nFollowing the design of Study 1 in earlier work, we surveyed 200 firms.\n"

	if got := Detect(headings("3 Method"), md); got.Verdict != VerdictSingle {
		t.Errorf("verdict = %q, want %q (%s)", got.Verdict, VerdictSingle, got.Reason)
	}
}

// Headings win. When the document structures itself into studies, prose adds
// nothing and must not downgrade a clear answer to uncertain.
func TestDetect_HeadingsOutrankProse(t *testing.T) {
	md := "Some prose mentioning Study 1 and Study 2 and Study 3.\n"

	got := Detect(headings("4. Study 1: Elicitation", "7. Study 2: Validation"), md)
	if got.Verdict != VerdictMulti {
		t.Errorf("verdict = %q, want %q (%s)", got.Verdict, VerdictMulti, got.Reason)
	}
}

func TestDetect_EvidenceIsRecorded(t *testing.T) {
	got := Detect(headings("4. Study 1: Elicitation", "8. Study 3: Validation"), "")

	if len(got.Evidence) != 2 {
		t.Fatalf("evidence = %+v, want two items", got.Evidence)
	}
	for _, e := range got.Evidence {
		if e.Kind != "study" {
			t.Errorf("kind = %q, want %q", e.Kind, "study")
		}
		if e.Ordinal < 0 {
			t.Errorf("ordinal = %d, want the heading's ordinal", e.Ordinal)
		}
		if !strings.Contains(e.Text, "Study") {
			t.Errorf("text = %q, want the heading verbatim", e.Text)
		}
	}
}

func TestGroupOf(t *testing.T) {
	cases := map[string]string{
		"1": "1", "2": "2", "1A": "1", "1B": "1", "2A": "2", "10": "10", "I": "I", "II": "II",
	}
	for label, want := range cases {
		if got := groupOf(label); got != want {
			t.Errorf("groupOf(%q) = %q, want %q", label, got, want)
		}
	}
}

// --- the unit and its scope ---

func TestNewSingleStudy(t *testing.T) {
	u := NewSingleStudy("paper-1", StatusAcceptedSingleStudy)

	if u.Ref != "RU1" || u.Label != "Study 1" || u.Index != 1 {
		t.Errorf("unit = %+v, want RU1 / Study 1 / index 1", u)
	}
	if u.Type != UnitStudy {
		t.Errorf("type = %q", u.Type)
	}
	if u.Status != StatusAcceptedSingleStudy {
		t.Errorf("status = %q", u.Status)
	}
	// Identity belongs to the service, as it does for runs, nodes and tasks.
	if u.ID != "" {
		t.Errorf("id = %q, want empty", u.ID)
	}
}

func TestScopeForRole(t *testing.T) {
	cases := map[string]Scope{
		"abstract":          ScopeManuscript,
		"references":        ScopeManuscript,
		"ethics_statement":  ScopeManuscript,
		"literature_review": ScopeManuscript,
		"methodology":       ScopeStudy,
		"results":           ScopeStudy,
		"theory":            ScopeStudy,
		"limitations":       ScopeStudy,
		"introduction":      ScopeBoth,
		"discussion":        ScopeBoth,
		"conclusion":        ScopeBoth,
		"Unknown":           ScopeUndetermined,
	}

	for role, want := range cases {
		got, ok := ScopeForRole(role)
		if !ok {
			t.Errorf("role %q not in the map", role)
			continue
		}
		if got != want {
			t.Errorf("ScopeForRole(%q) = %q, want %q", role, got, want)
		}
	}

	// An unrecognised role must say so rather than default. A silent fallback
	// would make a typo look like a working assignment.
	if _, ok := ScopeForRole("methodolgy"); ok {
		t.Error("an unrecognised role was accepted")
	}
}

func TestAssign(t *testing.T) {
	unit := NewSingleStudy("paper-1", StatusAcceptedSingleStudy)

	hs := []Heading{
		{Ordinal: 0, Text: "A Study Of Things", Role: ""},
		{Ordinal: 1, Text: "Abstract", Role: "abstract"},
		{Ordinal: 2, Text: "1 Introduction", Role: "introduction"},
		{Ordinal: 3, Text: "4 Methodology", Role: "methodology"},
		{Ordinal: 4, Text: "5 Results", Role: "results"},
		{Ordinal: 5, Text: "6 Discussion", Role: "discussion"},
		{Ordinal: 6, Text: "References", Role: "references"},
		{Ordinal: 7, Text: "Appendix A", Role: "Unknown"},
	}

	got := Assign(hs, unit)
	if len(got) != len(hs) {
		t.Fatalf("got %d assignments, want %d", len(got), len(hs))
	}

	want := []Scope{
		ScopeUndetermined, // the title carries no role by design
		ScopeManuscript,
		ScopeBoth,
		ScopeStudy,
		ScopeStudy,
		ScopeBoth,
		ScopeManuscript,
		ScopeUndetermined,
	}
	for i := range want {
		if got[i].Scope != want[i] {
			t.Errorf("%q: scope = %q, want %q", hs[i].Text, got[i].Scope, want[i])
		}
	}

	// A reference list belongs to no study, and empty is the correct value there
	// rather than a missing one.
	if got[6].UnitRef != "" {
		t.Errorf("references carry unit ref %q", got[6].UnitRef)
	}
	if got[3].UnitRef != "RU1" {
		t.Errorf("methodology unit ref = %q, want RU1", got[3].UnitRef)
	}
	// "Both" still belongs to the study; the section simply also says things about
	// the manuscript.
	if got[2].UnitRef != "RU1" {
		t.Errorf("introduction unit ref = %q, want RU1", got[2].UnitRef)
	}
}

func TestSummary(t *testing.T) {
	unit := NewSingleStudy("paper-1", StatusAcceptedSingleStudy)
	got := Summary(Assign([]Heading{
		{Ordinal: 0, Text: "Abstract", Role: "abstract"},
		{Ordinal: 1, Text: "Method", Role: "methodology"},
		{Ordinal: 2, Text: "Results", Role: "results"},
		{Ordinal: 3, Text: "Discussion", Role: "discussion"},
	}, unit))

	if got[ScopeManuscript] != 1 || got[ScopeStudy] != 2 || got[ScopeBoth] != 1 {
		t.Errorf("summary = %v", got)
	}
}
