package segment

import (
	"bytes"
	"regexp"
	"sort"
	"strings"
)

// HeadingSource records whether a node came from a real markdown heading or was
// inferred from a line Mathpix left as ordinary text.
//
// It is a THIRD axis, alongside node_kind and primary_role, and it is separate
// from ClassificationMethod on purpose. Method answers "how was the role
// decided". This answers "was there a heading here at all". A node inferred from
// plain text whose role then matched a keyword is MethodRule and
// HeadingInferred: the role is as well-founded as any other, and the heading is
// not.
type HeadingSource string

const (
	// HeadingDetected: goldmark found an ATX heading. Every node before rule
	// version 2.9 was this, and almost every node still is.
	HeadingDetected HeadingSource = "detected"

	// HeadingInferred: no heading existed; §3.1 recovered one from plain text.
	HeadingInferred HeadingSource = "inferred"
)

// referencesLine matches a line that is nothing but a bibliography title.
//
// Anchored at both ends deliberately. "References" alone on a line is a section
// title Mathpix failed to mark; "references to prior work" inside a sentence is
// prose, and the difference is the entire safety of this rule. An optional
// trailing colon and an optional leading section number are the only decorations
// allowed.
//
// # Built FROM the role table, not written alongside it
//
// The first version of this hard-coded its own list of titles, and it included
// "literature cited", which the role table does not. The result was a heading
// recovered and then unclassifiable: an inferred node with no role, an
// unresolved status, and a review task asking a human about a bibliography.
// Strictly worse than not inferring at all.
//
// Deriving the pattern from keywordToRole makes that failure unrepresentable.
// The two lists cannot drift because there is only one list, and adding a title
// to the role table extends this rule automatically and correctly.
var referencesLine = buildReferencesLinePattern()

func buildReferencesLinePattern() *regexp.Regexp {
	var titles []string
	for keyword, role := range keywordToRole {
		if role == RoleReferences {
			titles = append(titles, regexp.QuoteMeta(keyword))
		}
	}
	// Sorted for a stable pattern: map iteration order is random in Go, and a
	// regexp that differs between processes is a reproducibility bug waiting to
	// be blamed on something else. Longest first so "reference list" is tried
	// before "references" would otherwise shadow it.
	sort.Slice(titles, func(i, j int) bool {
		if len(titles[i]) != len(titles[j]) {
			return len(titles[i]) > len(titles[j])
		}
		return titles[i] < titles[j]
	})

	return regexp.MustCompile(`(?i)^\s*(?:\d+\.?\s*)?(` + strings.Join(titles, "|") + `)\s*:?\s*$`)
}

// referenceEntry is a weak test for a line that looks like a bibliography entry:
// it carries a plausible publication year.
var referenceEntry = regexp.MustCompile(`\((?:19|20)\d{2}[a-z]?\)|\b(?:19|20)\d{2}[a-z]?\.`)

// Detection thresholds. Both are deliberately conservative: this rule invents a
// section that the document did not mark, so it must be much more willing to do
// nothing than to be wrong.
const (
	// minReferenceEntries is how many entry-like lines must follow the candidate
	// before it is believed. Three is enough to distinguish a bibliography from a
	// sentence that happens to mention a year.
	minReferenceEntries = 3

	// entryScanLimit is how far below the candidate to look for them. A real
	// bibliography starts immediately; a prose mention of "References" followed
	// twenty lines later by three dated sentences is not one.
	entryScanLimit = 25
)

// inferReferencesHeading recovers a bibliography heading that Mathpix emitted as
// ordinary text, and reports whether it found one.
//
// # Why this exists
//
// Measured on the ten ingested papers: FOUR of them contain the word
// "References" on its own line with no heading markers. Step 3 is heading-driven,
// so no citation_source node is created, and the bibliography is absorbed into
// whatever section precedes it. The damage is not hypothetical:
//
//	"5.3. Future Directions"                       91% reference list
//	"6. Further developments"                      88% reference list
//	"10. Conclusion, limitations, and scope..."    85% reference list
//	"6. Implications and recommendations..."       85% reference list
//
// So a consumer reading "Future Directions" gets twenty kilobytes of somebody
// else's bibliography. That is wrong today, for every consumer, and it is wrong
// before any citation work begins.
//
// # Why the fix belongs HERE and not in Step 2
//
// The obvious repair is to make Mathpix emit the heading, or to patch the
// markdown afterwards. The second is not available: approved_markdown is
// fingerprinted, every offset in the system indexes into it, and editing it
// would invalidate every stored span in every prior run. We cannot repair the
// text. We can only improve how we read it.
//
// # Why it is this conservative
//
// It fires at most once per document, never when a real references heading
// exists, only on a line that is nothing but the title, and only when the lines
// below it actually look like a bibliography. A false positive here splits a
// genuine section in half and mislabels the remainder, which is worse than the
// problem it solves. Doing nothing is always the safe answer.
//
// src is the markdown; detected is the headings goldmark found. The returned
// Heading carries the same byte-offset contract as a real one, with ByteStart
// equal to TextStart because there are no '#' markers to skip.
func inferReferencesHeading(src []byte, detected []Heading) (Heading, bool) {
	// Never when the document already says so. A paper with a real references
	// heading has nothing to recover, and a second one would be an invention.
	for _, h := range detected {
		if h.TextStart < 0 || h.TextStop > len(src) {
			continue
		}
		text := StripIdentifiers(Normalize(string(src[h.TextStart:h.TextStop])))
		if _, _, semantic := ParseContainer(text); keywordToRole[semantic] == RoleReferences {
			return Heading{}, false
		}
	}

	// The level to give it: the shallowest SECTION level the document uses, so it
	// becomes a sibling of the paper's main sections rather than a child of the
	// one it is ending.
	//
	// H1 is excluded, and that exclusion is load-bearing. §4 treats H1 as the
	// document-title level, and a paper with one H1 has its title identified by
	// the singleton rule. Inferring an H1 here would silently create a SECOND
	// one, flip the title from singleton_h1 to structural_rule, and assert that a
	// bibliography sits at the same level as the paper's name. It is a section.
	//
	// All four affected papers number their sections at H2, which is what this
	// yields for them.
	level := 4
	found := false
	for _, h := range detected {
		if h.Level >= 2 && h.Level <= 4 && h.Level < level {
			level, found = h.Level, true
		}
	}
	if !found {
		level = 2
	}

	lines, starts := splitLines(src)

	// The LAST qualifying candidate wins. A bibliography sits at the end, and a
	// paper that discusses "Works cited" in its methods section would otherwise
	// hand the title to the wrong line.
	best := -1
	for i, line := range lines {
		if !referencesLine.MatchString(line) {
			continue
		}
		if isInsideHeading(starts[i], detected) {
			continue
		}
		if countEntriesBelow(lines, i) < minReferenceEntries {
			continue
		}
		best = i
	}
	if best < 0 {
		return Heading{}, false
	}

	line := lines[best]
	lead := len(line) - len(strings.TrimLeft(line, " \t"))
	textStart := starts[best] + lead
	textStop := starts[best] + len(strings.TrimRight(line, " \t\r"))

	return Heading{
		Level:     level,
		ByteStart: textStart,
		TextStart: textStart,
		TextStop:  textStop,
		Inferred:  true,
	}, true
}

// countEntriesBelow counts bibliography-looking lines just under a candidate.
func countEntriesBelow(lines []string, from int) int {
	n, seen := 0, 0
	for i := from + 1; i < len(lines) && seen < entryScanLimit; i++ {
		if strings.TrimSpace(lines[i]) == "" {
			continue
		}
		seen++
		if referenceEntry.MatchString(lines[i]) {
			n++
		}
	}
	return n
}

// isInsideHeading guards against promoting a line that goldmark already claimed.
// "## References" matches the pattern too once the markers are stripped, and
// promoting it would produce two nodes for one heading — a §10 violation.
func isInsideHeading(offset int, detected []Heading) bool {
	for _, h := range detected {
		if offset >= h.ByteStart && offset < h.TextStop {
			return true
		}
	}
	return false
}

// splitLines returns each line and its byte offset, without allocating a copy of
// the document.
func splitLines(src []byte) ([]string, []int) {
	var lines []string
	var starts []int

	at := 0
	for at <= len(src) {
		i := bytes.IndexByte(src[at:], '\n')
		if i < 0 {
			lines = append(lines, string(src[at:]))
			starts = append(starts, at)
			break
		}
		lines = append(lines, string(src[at:at+i]))
		starts = append(starts, at)
		at += i + 1
	}

	return lines, starts
}

// insertHeading places h into a document-ordered heading slice.
func insertHeading(hs []Heading, h Heading) []Heading {
	out := make([]Heading, 0, len(hs)+1)
	placed := false
	for _, existing := range hs {
		if !placed && h.ByteStart < existing.ByteStart {
			out = append(out, h)
			placed = true
		}
		out = append(out, existing)
	}
	if !placed {
		out = append(out, h)
	}
	return out
}
