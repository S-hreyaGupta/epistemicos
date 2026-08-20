// Package researchunit decides how many studies a manuscript reports, and
// creates the object everything downstream will hang off.
//
// # Why this exists before anything uses it
//
// The MVP handles one-study papers. The danger is not that a multi-study paper is
// handled badly — it is that it is handled SILENTLY, with the method from Study 1
// attached to the results of Study 2 and the claims of Study 3. That output looks
// like a finding. Nothing about it looks like an error.
//
// So this is a gate first and a data structure second. Its job is to refuse.
//
// # Why it is deterministic
//
// Measured on the ten ingested papers: nine report one study, one reports three.
// The signal in that one is entirely in its headings — "4. Study 1", "7. Study 2",
// "8. Study 3" — and finding two different study numbers is a fact rather than a
// judgement. A model is not needed to read a heading.
//
// A model IS needed for the genuinely ambiguous case, where a paper has "Phase 1"
// and "Phase 2" and only reading tells you whether that is one study in two stages
// or two studies. That case occurs ZERO times in the ten papers, so this package
// routes it to a human and leaves the model call for when such a paper appears.
// Adding it now would be untested code on a path that has never fired.
//
// # The one thing this deliberately does not do
//
// It does not discover study structure. It counts labels. A paper that reports two
// studies without numbering them is a paper this cannot see, and the honest
// response to that is a review flag rather than a cleverer rule.
package researchunit

import (
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// Heading is one of the document's headings. Deliberately not segment's
// SectionNode: this package needs four fields, and taking the whole type would
// couple two domains that have no reason to know about each other.
type Heading struct {
	Ordinal int
	Level   int
	Text    string

	// Role is the section role from Step 3, used only for scope assignment.
	// A string rather than segment.Role for the same decoupling reason.
	Role string
}

// Verdict is the gate's decision.
type Verdict string

const (
	// VerdictSingle: one study. A research unit is created and the paper proceeds.
	VerdictSingle Verdict = "single"

	// VerdictMulti: two or more studies. Out of scope for the MVP.
	VerdictMulti Verdict = "multi"

	// VerdictUncertain: signals that could mean either. A human decides.
	//
	// This is a real answer, not a failure. A wrong "single" silently corrupts
	// every downstream link in the paper; a human spending two minutes is cheap
	// by comparison.
	VerdictUncertain Verdict = "uncertain"
)

// Evidence is one label found in the document.
type Evidence struct {
	// Kind is "study", "experiment", "phase", "sample", "dataset" or "wave".
	Kind string

	// Label is as printed: "1", "2", "1A", "II".
	Label string

	// Group is the top-level number Label belongs to. "1A" and "1B" both group
	// under "1", which is the whole reason this field exists — they are parts of
	// Study 1, not Studies 1A and 1B.
	Group string

	// Text is the heading or line it was found in, verbatim.
	Text string

	// Ordinal is the heading's ordinal, or -1 when found in body prose.
	Ordinal int
}

// Gate is the decision plus everything it was based on.
type Gate struct {
	Verdict Verdict

	// StudyCount is the number of distinct study groups found in headings. Zero
	// when nothing was labelled, which is the ordinary single-study case.
	StudyCount int

	// Evidence is every label found, headings first.
	Evidence []Evidence

	// Reason is one sentence a person can read.
	Reason string
}

var (
	// Two vocabularies, and the split IS the rule. A numbered study or experiment
	// is a study; a numbered phase, sample, dataset, wave or round might be
	// anything, so those are everything the regexp matches which is not listed
	// here. Only the strong list is enumerated, so that adding a weak word to the
	// pattern cannot accidentally make it decisive.
	strongKinds = []string{"study", "experiment"}

	labelled = regexp.MustCompile(
		`(?i)\b(stud(?:y|ies)|experiments?|phases?|samples?|datasets?|data sets?|waves?|rounds?)\s+([0-9]{1,2}[A-Za-z]?|[IVX]{1,4})\b`)
)

// Detect runs the gate.
//
// It reads headings and body separately, and treats them differently on purpose.
// A heading is the document's own structural claim about itself. A sentence is
// not: "as in Study 1 of Peldszus and Stede" is a reference to somebody else's
// study, and a paper's related-work section is full of them. So body evidence can
// raise a question and never settles one.
func Detect(headings []Heading, markdown string) Gate {
	g := Gate{}

	headingGroups := map[string]bool{}
	weakGroups := map[string]bool{}

	for _, h := range headings {
		for _, e := range scan(h.Text, h.Ordinal) {
			g.Evidence = append(g.Evidence, e)
			if isStrong(e.Kind) {
				headingGroups[e.Group] = true
			} else {
				weakGroups[e.Group] = true
			}
		}
	}

	g.StudyCount = len(headingGroups)

	// RULE 1. Two or more study numbers in the headings. This is the case the ten
	// papers actually contain, and it is not a close call.
	if len(headingGroups) >= 2 {
		g.Verdict = VerdictMulti
		g.Reason = fmt.Sprintf("%d studies named in the headings (%s); the MVP handles one-study papers only",
			len(headingGroups), strings.Join(sortedKeys(headingGroups), ", "))
		return g
	}

	// Body evidence, gathered only now: it cannot establish MULTI, so there is no
	// point collecting it when the headings already have.
	bodyGroups := map[string]bool{}
	for _, line := range strings.Split(markdown, "\n") {
		if isHeadingLine(line) {
			continue
		}
		for _, e := range scan(line, -1) {
			if !isStrong(e.Kind) {
				continue
			}
			if !bodyGroups[e.Group] {
				bodyGroups[e.Group] = true
				g.Evidence = append(g.Evidence, e)
			}
		}
	}

	// RULE 2. The headings say one study, but the prose keeps naming several.
	//
	// NOT multi. A related-work section discussing "Study 1 of Smith et al." would
	// trip this, and refusing a perfectly good paper on that basis is worse than
	// asking. But a paper that genuinely runs two studies without heading them is
	// exactly the silent failure this gate exists for, so it must not pass either.
	if len(bodyGroups) >= 2 {
		g.Verdict = VerdictUncertain
		g.Reason = fmt.Sprintf("the headings name at most one study, but the text refers to %d (%s); those may be other authors' studies or unlabelled studies of its own",
			len(bodyGroups), strings.Join(sortedKeys(bodyGroups), ", "))
		return g
	}

	// RULE 3. Numbered phases, samples or waves in the headings.
	//
	// Usually one study in stages. Occasionally not. Only reading settles it, so
	// this is the case a model would earn its place on — and it fires on none of
	// the ten papers, which is why there is no model call here yet.
	if len(weakGroups) >= 2 {
		g.Verdict = VerdictUncertain
		g.Reason = fmt.Sprintf("headings numbered %s: usually stages of one study, occasionally separate studies, and only reading them settles it",
			strings.Join(sortedKeys(weakGroups), ", "))
		return g
	}

	// RULE 4. Nothing numbered.
	g.Verdict = VerdictSingle
	g.Reason = "no numbered studies, experiments, phases or samples in the headings"
	return g
}

// scan finds every label in one line.
func scan(text string, ordinal int) []Evidence {
	var out []Evidence
	for _, m := range labelled.FindAllStringSubmatch(text, -1) {
		kind := normaliseKind(m[1])
		label := strings.ToUpper(m[2])
		out = append(out, Evidence{
			Kind:    kind,
			Label:   label,
			Group:   groupOf(label),
			Text:    strings.TrimSpace(text),
			Ordinal: ordinal,
		})
	}
	return out
}

// groupOf reduces a label to the study it belongs to.
//
// "1A" and "1B" both return "1". This is the correction the specification needed:
// the real multi-study paper carries Study 1, 1A, 1B, 2, 2A, 2B and 3, which is
// three studies with sub-parts, not seven studies. Counting labels rather than
// groups would report seven and would report two for a paper that merely split
// Study 1 into halves.
func groupOf(label string) string {
	i := 0
	for i < len(label) && label[i] >= '0' && label[i] <= '9' {
		i++
	}
	if i > 0 {
		return label[:i]
	}
	// A roman numeral has no digits; it is its own group.
	return label
}

func normaliseKind(s string) string {
	s = strings.ToLower(s)
	switch {
	case strings.HasPrefix(s, "stud"):
		return "study"
	case strings.HasPrefix(s, "experiment"):
		return "experiment"
	case strings.HasPrefix(s, "phase"):
		return "phase"
	case strings.HasPrefix(s, "sample"):
		return "sample"
	case strings.HasPrefix(s, "dataset"), strings.HasPrefix(s, "data set"):
		return "dataset"
	case strings.HasPrefix(s, "wave"):
		return "wave"
	case strings.HasPrefix(s, "round"):
		return "round"
	}
	return s
}

func isStrong(kind string) bool {
	for _, k := range strongKinds {
		if kind == k {
			return true
		}
	}
	return false
}

func isHeadingLine(l string) bool {
	t := strings.TrimLeft(l, " ")
	return strings.HasPrefix(t, "#")
}

// sortedKeys returns group labels in a stable, human order: numbers numerically,
// anything else alphabetically after them.
func sortedKeys(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Slice(out, func(i, j int) bool {
		a, errA := strconv.Atoi(out[i])
		b, errB := strconv.Atoi(out[j])
		if errA == nil && errB == nil {
			return a < b
		}
		if errA == nil {
			return true
		}
		if errB == nil {
			return false
		}
		return out[i] < out[j]
	})
	return out
}
