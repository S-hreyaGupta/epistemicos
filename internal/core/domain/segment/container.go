package segment

import (
	"regexp"
	"strings"
)

// StructuralContainer names a heading that describes WHERE content sits rather
// than what epistemic function it performs. v2.1 §7 recognises exactly one.
//
// The distinction is the whole point of the type. "Appendix C: Measures" is an
// appendix AND it is methodology; those are answers to different questions, so
// the container never competes for primary_role. Collapsing them — making
// "appendix" a role — would mean a reader asking "where is the method
// described" gets no answer for any paper that put it in an appendix.
type StructuralContainer string

// ContainerAppendix is the only structural container in v2.0.
const ContainerAppendix StructuralContainer = "appendix"

// appendixTriggers open an appendix container when a normalized heading begins
// with one. Mirrors structural_containers.appendix.triggers in the role table;
// TestContainerDataMatchesTable proves they have not drifted apart.
//
// Ordering is not significant here — neither trigger is a prefix of the other
// ("appendix" and "appendices" diverge at the eighth character) — but the loop
// below takes the first match, so a future trigger that IS a prefix of another
// would need the longer one listed first.
var appendixTriggers = []string{
	"appendix",
	"appendices",
}

// appendixAliases are headings that ARE an appendix without saying so. Mirrors
// structural_containers.appendix.aliases_g2.
//
// These match EXACTLY, never as a prefix, which is what separates them from
// triggers. "Supporting information" is an appendix; "Supporting information
// for the reader" is a sentence that happens to begin with those words, and
// treating it as a bare container would suppress a review task that ought to
// be raised.
var appendixAliases = []string{
	"supporting information",
	"supplementary material",
	"supplementary materials",
	"supplementary information",
	"online appendix",
	"electronic supplementary material",
}

// appendixLabel captures the short token that follows a trigger — the "B" of
// "appendix b: robustness checks", the "A1" of "appendix a1".
//
// One to three alphanumerics, then a word boundary. The boundary is what stops
// the rule from biting a word: given "appendixation", no prefix of "ation"
// ending at a boundary exists, the match fails, and the remainder is treated as
// semantic text instead of as a label. That is the intended fallback, not an
// accident of the pattern.
var appendixLabel = regexp.MustCompile(`^([A-Za-z0-9]{1,3})\b\s*([:.\-]\s*)?(.*)$`)

// ParseContainer applies §7's appendix rule to a semantic heading — that is, to
// a heading that Normalize and StripIdentifiers have already reduced.
//
// It returns the structural container, an optional appendix label, and the
// semantic heading that survives for role classification. An empty semantic
// heading means there is nothing left to classify: §7 calls this a bare
// container, and it resolves to Unknown by structural assignment with no review
// task, because a heading reading only "Appendix B" genuinely carries no
// epistemic claim. That is a deliberate assignment and not a classification
// failure, which is why it does not reach a human.
//
// The three outcomes:
//
//	"supporting information"          -> appendix, no label,  no semantic heading
//	"appendix b"                      -> appendix, label "B", no semantic heading
//	"appendix b: robustness checks"   -> appendix, label "B", "robustness checks"
//
// and anything not matching a trigger or alias passes through untouched, with
// no container and the heading returned as given.
//
// The label is upper-cased so "appendix b" and "Appendix B" produce one value.
// Everything else here operates on already-normalized input and assumes it;
// calling this with a raw heading under-matches silently rather than failing.
func ParseContainer(semanticHeading string) (container StructuralContainer, label string, remainder string) {
	s := strings.TrimSpace(semanticHeading)

	// Aliases resolve first and match whole-string only.
	for _, alias := range appendixAliases {
		if s == alias {
			return ContainerAppendix, "", ""
		}
	}

	for _, trigger := range appendixTriggers {
		if !strings.HasPrefix(s, trigger) {
			continue
		}

		rest := strings.TrimSpace(strings.TrimPrefix(s, trigger))
		if rest == "" {
			// The heading is the bare trigger: "appendix", "appendices".
			return ContainerAppendix, "", ""
		}

		m := appendixLabel.FindStringSubmatch(rest)
		if m == nil {
			// No label-shaped token. Whatever follows is semantic text.
			return ContainerAppendix, "", strings.Trim(rest, " :.-")
		}

		return ContainerAppendix, strings.ToUpper(m[1]), strings.Trim(m[3], " :.-")
	}

	return "", "", s
}
