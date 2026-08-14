package segment

import (
	"regexp"
	"strings"
)

// Normalize folds a raw heading into the form the role table is keyed on:
// specification v2.1 §6, step 1.
//
// Three operations, in this order and no other:
//
//	trim surrounding whitespace
//	lower-case
//	collapse every internal whitespace run to a single space
//	trim trailing colons and full stops
//
// The trailing-punctuation trim runs LAST because OCR output routinely emits
// "3. Methodology:" — a heading carrying both a leading identifier and trailing
// punctuation. Trimming before the collapse would leave the identifier stripper
// in §6 step 2 matching against a string whose tail it cannot predict.
//
// Case folding is strings.ToLower, which is Unicode-aware. That matters because
// Mathpix emits real non-ASCII text; a byte-wise fold would leave "Résultats"
// and "résultats" distinct and neither would match the table.
//
// The result is what expected.json records as heading_normalized, and it is the
// input to StripIdentifiers.
func Normalize(raw string) string {
	s := strings.ToLower(strings.TrimSpace(raw))
	s = whitespaceRun.ReplaceAllString(s, " ")
	return strings.TrimRight(s, ":. ")
}

var whitespaceRun = regexp.MustCompile(`\s+`)

// The four identifier forms §6 step 2 strips. They are applied in sequence, and
// the sequence is load-bearing: "section 4: results" must lose the section word
// before the numeric rule would otherwise see "4: results" and consume the "4".
//
// Each pattern requires a SEPARATOR — a space, a dot, a colon or a hyphen —
// between the identifier and the text that follows. Without that requirement
// the alphabetic rule would eat the "a" from "a priori power analysis" and the
// Roman rule would eat "i" from "i and ii compared". Requiring the separator is
// what keeps a heading that merely begins with a letter intact.
var (
	// "section 4: results", "section 4a. results"
	identSectionWord = regexp.MustCompile(`^section\s+\d+[a-z]?\s*[:.\-]\s*`)

	// "2.1 methods", "2.1. methods", "4 results"
	identNumeric = regexp.MustCompile(`^\d+(\.\d+)*\s*[.:\-]?\s+`)

	// "iv. results", "iii) discussion"
	//
	// KNOWN OVER-MATCH, reproduced deliberately. The character class accepts any
	// word spelled from i, v, x, l, c, d and m — "civil", "mid", "dill" all
	// qualify — so "civil. liberties" strips to "liberties". The trailing
	// `[.)]\s+` is the only guard, and it is a weak one.
	//
	// This is not an oversight being carried forward silently. The reference
	// implementation that generated testdata/expected.json has the identical
	// behaviour, and expected.json is the contract this package is measured
	// against, so narrowing the rule here would break the fixture rather than
	// fix a defect. The reference used a lookahead, `(?=[ivxlcdm]+[.)\s])`,
	// which RE2 does not support; it is omitted rather than emulated because it
	// changed nothing — every string the lookahead admits, the body already
	// admits, including the over-match above.
	//
	// Narrowing it — validating the run as a well-formed Roman numeral — is a
	// specification change, not an implementation change, and belongs in a
	// revision of §6 step 2 with the fixture regenerated alongside.
	identRoman = regexp.MustCompile(`^[ivxlcdm]+\s*[.)]\s+`)

	// "a. methods", "b) results"
	identAlpha = regexp.MustCompile(`^[a-z]\s*[.)]\s+`)
)

// StripIdentifiers removes a leading section identifier from a normalized
// heading: v2.1 §6, step 2.
//
// The input must already have passed through Normalize. Every pattern here
// assumes lower case and single-spaced input, so calling this on a raw heading
// silently under-matches rather than failing.
//
// This is what makes classification PARENT-INDEPENDENT, which is the property
// §6 is built around. "2.1 Sample and procedure" and "Sample and procedure"
// reduce to the same string and therefore classify identically, no matter where
// either sits in the tree. Nothing downstream needs to know a node's depth to
// decide its role.
//
// Returns the semantic heading: the heading with its identifier and any
// surrounding punctuation removed.
func StripIdentifiers(s string) string {
	s = identSectionWord.ReplaceAllString(s, "")
	s = identNumeric.ReplaceAllString(s, "")
	s = identRoman.ReplaceAllString(s, "")
	s = identAlpha.ReplaceAllString(s, "")
	return strings.TrimSpace(strings.Trim(s, ":. "))
}
