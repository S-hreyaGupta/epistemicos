// Package methodology answers one question about a whole paper: is its research
// quantitative or qualitative?
//
// # Why this is not part of segment
//
// It is a DOCUMENT-level attribute. segment produces a tree of sections and one
// answer per section; this produces one answer per paper. Neither is a step in
// the other, and ordering them would make a document-level label wait on
// section-level uncertainty for no gain — one real proposal raises 65 review
// tasks, and its methodology does not become unknowable while they are open.
//
// Both read Step 2's approved markdown. They run alongside each other.
//
// # What it does, and what it deliberately does not
//
// Kosztyán et al. (2025) count how often each of 307 glossary terms occurs in a
// paper's lemmatized full text, then feed those counts to a trained XGBoost
// model. Their feature space is only those columns — not TF-IDF, not the whole
// vocabulary — which is why the glossary is the substantive artifact and the
// model is not.
//
// This package implements the COUNTING and a lexical lean over it. It does not
// implement their model. That is a deliberate stopping point, not an
// incompleteness: on six test papers the counts alone separate quantitative from
// qualitative with no overlap, so the model's value is unmeasured rather than
// assumed. If counting proves insufficient, the model is the next step and it
// needs a licence the authors have not granted.
//
// Everything here is deterministic: same markdown, same answer, no network, no
// model file, no Python.
package methodology

import (
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"
)

// Status is whether a determination was reached.
type Status string

const (
	// StatusResolved: one side clearly dominates.
	StatusResolved Status = "resolved"

	// StatusUnresolved: too few terms fired to say anything, or the two sides
	// are close enough that the difference is not evidence.
	StatusUnresolved Status = "unresolved"
)

// Method records how a determination was reached, so a reader can tell a
// counted answer from a modelled one without inferring it.
type Method string

const (
	// MethodLexical: term counts only. The only method implemented today.
	MethodLexical Method = "lexical"
)

// Class is the determined methodology.
type Class string

const (
	ClassQuantitative Class = "quantitative"
	ClassQualitative  Class = "qualitative"
)

// TermMatch is one glossary term and how often it occurred.
//
// Every term that fired is kept, including ones in neither marker list. The
// lean uses the markers; the full set is what makes the lean explicable, and
// what a model would consume if one is ever added.
type TermMatch struct {
	Term  string
	Count int

	// Marker is "qualitative", "quantitative", "mixed", or empty when the term
	// counted toward nothing.
	Marker string
}

// Result is one paper's methodology determination.
type Result struct {
	Class  Class
	Status Status
	Method Method

	// Score runs from -1 (purely qualitative) to +1 (purely quantitative), and
	// is length-normalised so a 90-page thesis and a 12-page article are
	// comparable. Zero when nothing fired.
	Score float64

	// QualitativeRate and QuantitativeRate are marker occurrences per 10,000
	// characters. Kept alongside Score because the score alone cannot
	// distinguish "few terms, lopsided" from "many terms, lopsided", and the
	// first is much weaker evidence.
	QualitativeRate  float64
	QuantitativeRate float64

	// MixedFlag is set when a mixed-methods term occurs. It is deliberately
	// separate from Class: the paper's model has no mixed category, and a paper
	// that merely discusses mixed methods would trip this. It marks a paper as
	// worth a human's attention, and decides nothing.
	MixedFlag bool

	// Matches is every glossary term that occurred, ordered by count then
	// alphabetically. This is the evidence, and it is why a label from this
	// package can be argued with rather than only accepted.
	Matches []TermMatch

	// DistinctTerms and TotalOccurrences describe reach: how much of the
	// glossary this document touched at all. A paper matching four terms has
	// told us almost nothing however lopsided those four are.
	DistinctTerms    int
	TotalOccurrences int
}

// Thresholds. Both are judgement calls on six papers and should be revisited
// against a larger corpus; they are named constants rather than literals so
// that revisiting them is a one-line change with a visible diff.
const (
	// minDistinctMarkers is the floor below which a lean is not reported. It
	// exists to catch a near-empty document, not to discriminate.
	//
	// Set to 4, and the reason is worth recording. The six test papers hit 6, 7,
	// 12, 12, 18 and 24 distinct markers — so 6 is the OBSERVED MINIMUM, not a
	// comfortable distance below it. A floor placed exactly on the lowest thing
	// ever measured is one unremarkable paper away from rejecting a document it
	// should have answered. 4 sits below the evidence, which is where a floor
	// belongs.
	minDistinctMarkers = 4

	// decisionMargin is how far from zero the score must sit before a side is
	// called.
	//
	// Measured: the four single-method papers scored -0.92, -0.55, +0.98, +0.98,
	// so 0.20 separates them with room to spare. The two mixed-methods papers
	// scored -0.37 and +0.19 — one reads qualitative, the other falls inside the
	// band.
	//
	// So this constant does not separate mixed from single-method and is not
	// trying to. MixedFlag does that.
	//
	// 0.40 WOULD SCORE SIX OUT OF SIX, and was rejected. The only evidence for it
	// is that it fits these six papers, and it was found by looking at their
	// results. The marker lists above were chosen before anything was measured
	// precisely so they would not be fitted to a sample this small; moving the
	// threshold afterwards to make that sample come out clean would spend that
	// discipline on a number with no support outside it.
	//
	// If a larger corpus supports a wider band, widen it then. See
	// TestCalibrationAgainstRealPapers.
	decisionMargin = 0.20
)

// Classify counts the glossary over a document and returns a determination.
//
// text is the approved markdown, whole. Passing a fragment is a category error:
// the counts are length-normalised and the thresholds were set against complete
// papers, so a single section would produce a number that looks like an answer
// and is not one.
func Classify(text string) Result {
	lowered := strings.ToLower(strings.ReplaceAll(text, "’", "'"))

	qual := markerSet(qualitativeMarkers)
	quan := markerSet(quantitativeMarkers)
	mixed := markerSet(mixedMarkers)

	var (
		res            Result
		qualHits       int
		quanHits       int
		distinctMarker int
	)
	res.Method = MethodLexical

	for _, term := range glossaryTerms {
		n := countWholeWord(lowered, strings.ToLower(strings.ReplaceAll(term, "’", "'")))
		if n == 0 {
			continue
		}

		m := TermMatch{Term: term, Count: n}

		// Normalise the apostrophe HERE TOO, not just when counting.
		//
		// markerSet stores its keys normalised, so looking up the raw term
		// missed every entry containing a typographic apostrophe. Exactly one
		// glossary term has one — "Cronbach's Alpha" — and it is a marker, so
		// the bug silently demoted an unambiguous quantitative signal to
		// counting toward nothing.
		//
		// It found itself: the term appeared in a real paper's evidence table
		// as "neither" when the marker list plainly contains it. Nothing about
		// the score looked wrong, which is the point — one missing marker out
		// of sixty-six moves a number slightly and never fails.
		key := strings.ToLower(strings.ReplaceAll(term, "’", "'"))
		switch {
		case mixed[key]:
			m.Marker = "mixed"
			res.MixedFlag = true
		case qual[key]:
			m.Marker = "qualitative"
			qualHits += n
			distinctMarker++
		case quan[key]:
			m.Marker = "quantitative"
			quanHits += n
			distinctMarker++
		}

		res.Matches = append(res.Matches, m)
		res.DistinctTerms++
		res.TotalOccurrences += n
	}

	sort.Slice(res.Matches, func(i, j int) bool {
		if res.Matches[i].Count != res.Matches[j].Count {
			return res.Matches[i].Count > res.Matches[j].Count
		}
		return res.Matches[i].Term < res.Matches[j].Term
	})

	// Per 10,000 characters. Without normalising, a long qualitative thesis
	// out-counts a short quantitative paper on sheer volume.
	if n := float64(len(text)); n > 0 {
		res.QualitativeRate = float64(qualHits) / n * 10000
		res.QuantitativeRate = float64(quanHits) / n * 10000
	}

	total := qualHits + quanHits
	if total > 0 {
		res.Score = float64(quanHits-qualHits) / float64(total)
	}

	// Refusing to answer is an answer. A document that fired almost nothing, or
	// one genuinely balanced between the two, gets no Class — and the caller can
	// tell those apart from Matches and the rates rather than guessing.
	switch {
	case distinctMarker < minDistinctMarkers || total == 0:
		res.Status = StatusUnresolved
	case res.Score > decisionMargin:
		res.Class, res.Status = ClassQuantitative, StatusResolved
	case res.Score < -decisionMargin:
		res.Class, res.Status = ClassQualitative, StatusResolved
	default:
		res.Status = StatusUnresolved
	}

	return res
}

func markerSet(xs []string) map[string]bool {
	m := make(map[string]bool, len(xs))
	for _, x := range xs {
		m[strings.ToLower(strings.ReplaceAll(x, "’", "'"))] = true
	}
	return m
}

// countWholeWord counts occurrences of keyword in s bounded by non-word
// characters, tolerating a trailing "s".
//
// # Why a hand-written matcher rather than a regexp
//
// The same reason segment has one: RE2 has no lookbehind, so the natural
// `(?<!\w)…(?!\w)` cannot be written, and this runs 301 times per document.
//
// # Why the trailing "s"
//
// The published method lemmatizes first, which would collapse "variables" to
// "variable" before counting. We do not lemmatize — it would mean a dictionary,
// a dependency, and a second source of non-determinism — so plural tolerance
// recovers most of what lemmatization was doing for a fixed glossary of nouns.
//
// It is deliberately NOT full stemming. "Analysis"/"analyses" is not caught, and
// that is visible and countable rather than hidden behind a stemmer's judgement.
// If accuracy ever depends on it, lemmatization is the honest fix, not a longer
// list of suffixes.
func countWholeWord(s, keyword string) int {
	if keyword == "" {
		return 0
	}

	count := 0
	for offset := 0; offset <= len(s)-len(keyword); {
		i := strings.Index(s[offset:], keyword)
		if i < 0 {
			break
		}
		start := offset + i
		end := start + len(keyword)

		// Accept a single trailing "s" as part of the match, so the word
		// boundary is tested after it rather than against it.
		if end < len(s) && s[end] == 's' {
			end++
		}

		if isBoundaryBefore(s, start) && isBoundaryAfter(s, end) {
			count++
		}
		offset = start + 1
	}
	return count
}

func isBoundaryBefore(s string, i int) bool {
	if i == 0 {
		return true
	}
	r, _ := utf8.DecodeLastRuneInString(s[:i])
	return !isWordRune(r)
}

func isBoundaryAfter(s string, i int) bool {
	if i >= len(s) {
		return true
	}
	r, _ := utf8.DecodeRuneInString(s[i:])
	return !isWordRune(r)
}

// isWordRune is Unicode-aware for the same reason segment's is: headings and
// body text reach this normalized but not transliterated, so "análisis" is a
// real input and treating the á as a separator would let a keyword match across
// it.
func isWordRune(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsDigit(r)
}

// GlossarySize is the number of distinct terms counted.
//
// Exported so a caller can print "N of M terms present" without importing the
// list, and so the 307-versus-301 discrepancy in the published table stays
// visible at the point anyone reads a number off this package.
func GlossarySize() int { return len(glossaryTerms) }
