package methodology

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
)

// A qualitative paper's vocabulary, and a quantitative one's. Synthetic rather
// than real PDFs: the six real papers are megabytes each and cannot live in
// testdata, so their measured numbers are recorded at the foot of this file and
// these fixtures exercise the logic.
const (
	qualitativeText = `We conducted an ethnography of the site over eighteen months.
Data came from in-depth interviewing and three focus groups, with participant
observation throughout. Analysis followed grounded theory, and we used thematic
analysis to develop the coding frame. Triangulation across sources supported the
qualitative findings. The case study design is described below, alongside the
content analysis procedure applied to the interview transcripts.`

	quantitativeText = `We estimated a regression model on survey responses measured
with a Likert scale. Each variable was standardized before analysis. Cronbach's
alpha exceeded 0.8 for every construct, and confirmatory factor analysis
supported discriminant validity. The coefficient on the treatment was significant
at conventional levels, with a p value below 0.01. Variance inflation indicated
no multicollinearity, and we report the standard error alongside the effect size.
Structural equation modeling produced comparable quantitative results.`
)

func TestClassify_Qualitative(t *testing.T) {
	got := Classify(qualitativeText)

	if got.Class != ClassQualitative {
		t.Errorf("class = %q, want %q (score %.2f, matches %v)", got.Class, ClassQualitative, got.Score, got.Matches)
	}
	if got.Status != StatusResolved {
		t.Errorf("status = %q, want %q", got.Status, StatusResolved)
	}
	if got.Method != MethodLexical {
		t.Errorf("method = %q, want %q", got.Method, MethodLexical)
	}
	if got.Score >= 0 {
		t.Errorf("score = %.2f, want negative", got.Score)
	}
	if got.MixedFlag {
		t.Error("mixed flag set on a single-method paper")
	}
}

func TestClassify_Quantitative(t *testing.T) {
	got := Classify(quantitativeText)

	if got.Class != ClassQuantitative {
		t.Errorf("class = %q, want %q (score %.2f)", got.Class, ClassQuantitative, got.Score)
	}
	if got.Status != StatusResolved {
		t.Errorf("status = %q, want %q", got.Status, StatusResolved)
	}
	if got.Score <= 0 {
		t.Errorf("score = %.2f, want positive", got.Score)
	}
}

// TestClassify_RefusesOnThinEvidence. A document that fired almost nothing must
// not produce a confident label just because what little fired was lopsided.
//
// One marker is not a finding, however one-sided it looks.
func TestClassify_RefusesOnThinEvidence(t *testing.T) {
	got := Classify("This paper presents a regression. Nothing else of note is said here at all.")

	if got.Status != StatusUnresolved {
		t.Errorf("status = %q, want %q — too few markers to lean either way (matches %v)",
			got.Status, StatusUnresolved, got.Matches)
	}
	if got.Class != "" {
		t.Errorf("class = %q, want empty on an unresolved determination", got.Class)
	}
}

// TestClassify_RefusesOnABalancedPaper is the other refusal, and a different
// one: plenty of evidence, pointing both ways.
func TestClassify_RefusesOnABalancedPaper(t *testing.T) {
	got := Classify(qualitativeText + "\n\n" + quantitativeText)

	if got.Status != StatusUnresolved {
		t.Errorf("status = %q, want %q — both vocabularies are present in force (score %.2f)",
			got.Status, StatusUnresolved, got.Score)
	}

	// The two refusals must stay distinguishable. This one has evidence.
	if got.DistinctTerms < minDistinctMarkers {
		t.Errorf("distinct terms = %d, want plenty — this is the balanced case, not the thin one", got.DistinctTerms)
	}
}

// TestClassify_MixedFlagIsSeparateFromClass.
//
// The published model is binary and has no mixed category, yet "Mixed Method" is
// one of its own 301 terms. The flag uses it, and stays out of the class: on the
// real papers one mixed submission still leans clearly qualitative, so folding
// the flag into the class would either lose that lean or invent a third value
// the evidence does not support.
func TestClassify_MixedFlagIsSeparateFromClass(t *testing.T) {
	got := Classify(qualitativeText + "\n\nWe adopt a mixed method design throughout.")

	if !got.MixedFlag {
		t.Error("mixed flag not set despite a mixed-methods term")
	}
	if got.Class != ClassQualitative {
		t.Errorf("class = %q, want %q — the flag must not overwrite the lean", got.Class, ClassQualitative)
	}
}

// TestClassify_EmptyDocument. Zero is a legitimate input and must not divide.
func TestClassify_EmptyDocument(t *testing.T) {
	got := Classify("")

	if got.Status != StatusUnresolved {
		t.Errorf("status = %q, want %q", got.Status, StatusUnresolved)
	}
	if got.Score != 0 || got.QualitativeRate != 0 || got.QuantitativeRate != 0 {
		t.Errorf("non-zero rates on an empty document: %+v", got)
	}
	if len(got.Matches) != 0 {
		t.Errorf("matches on an empty document: %v", got.Matches)
	}
}

// TestClassify_LengthNormalisation is why the rates exist.
//
// Doubling a document doubles its raw counts and must not change what it is.
// Without normalisation a long qualitative thesis would out-count a short
// quantitative paper on volume alone.
func TestClassify_LengthNormalisation(t *testing.T) {
	one := Classify(quantitativeText)
	two := Classify(quantitativeText + "\n\n" + quantitativeText)

	if one.Class != two.Class {
		t.Errorf("class changed on doubling: %q then %q", one.Class, two.Class)
	}
	if diff := one.QuantitativeRate - two.QuantitativeRate; diff > 0.5 || diff < -0.5 {
		t.Errorf("rate moved from %.2f to %.2f on doubling; it should be roughly stable",
			one.QuantitativeRate, two.QuantitativeRate)
	}
	if one.TotalOccurrences*2 != two.TotalOccurrences {
		t.Errorf("raw occurrences %d then %d, want exactly double", one.TotalOccurrences, two.TotalOccurrences)
	}
}

// TestCountWholeWord guards the boundary, which is the whole safety of matching
// a 301-term list against arbitrary prose.
func TestCountWholeWord(t *testing.T) {
	cases := []struct {
		s, keyword string
		want       int
	}{
		{"the sample was small", "sample", 1},
		{"two samples were drawn", "sample", 1},         // plural tolerated
		{"resampling is not sampling", "sampling", 1},   // must not fire inside "resampling"
		{"a variable and two variables", "variable", 2}, // both forms
		{"particular results", "art", 0},                // the case that bites
		{"mean, mean and mean again", "mean", 3},
		{"meaning is not mean", "mean", 1},
		{"análisis de la varianza", "varianza", 1}, // non-ASCII boundary
		{"", "sample", 0},
		{"anything", "", 0},
	}

	for _, c := range cases {
		if got := countWholeWord(c.s, c.keyword); got != c.want {
			t.Errorf("countWholeWord(%q, %q) = %d, want %d", c.s, c.keyword, got, c.want)
		}
	}
}

// TestCountWholeWord_PluralIsNotStemming records a deliberate limit.
//
// We tolerate a trailing "s" because the published method lemmatizes and we do
// not. We do NOT stem: "analysis"/"analyses" is not caught. That gap is visible
// and countable here rather than hidden inside a stemmer, and if accuracy ever
// depends on it the honest fix is lemmatization, not more suffixes.
func TestCountWholeWord_PluralIsNotStemming(t *testing.T) {
	if got := countWholeWord("post hoc analyses were run", "post hoc analysis"); got != 0 {
		t.Errorf("caught an irregular plural (%d); the limit is deliberate and this test records it", got)
	}
	if got := countWholeWord("post hoc analysis was run", "post hoc analysis"); got != 1 {
		t.Errorf("missed the exact form: %d", got)
	}
}

// TestMarkersAreDisjoint. A term in both lists would count for both sides and
// silently cancel itself, which is invisible in the output.
func TestMarkersAreDisjoint(t *testing.T) {
	qual := markerSet(qualitativeMarkers)
	for _, q := range quantitativeMarkers {
		if qual[strings.ToLower(q)] {
			t.Errorf("%q is in both marker lists", q)
		}
	}
}

// TestMarkersAreInTheGlossary. A marker outside the 301 would never be counted,
// so the list would silently shrink.
func TestMarkersAreInTheGlossary(t *testing.T) {
	in := map[string]bool{}
	for _, t := range glossaryTerms {
		in[strings.ToLower(t)] = true
	}
	for _, list := range [][]string{qualitativeMarkers, quantitativeMarkers, mixedMarkers} {
		for _, m := range list {
			if !in[strings.ToLower(m)] {
				t.Errorf("marker %q is not one of the glossary terms", m)
			}
		}
	}
}

// TestGlossaryHasNoDuplicates. The published table repeats eight terms; this
// package must not, because a duplicated column would count that term twice.
func TestGlossaryHasNoDuplicates(t *testing.T) {
	seen := map[string]bool{}
	for _, term := range glossaryTerms {
		k := strings.ToLower(term)
		if seen[k] {
			t.Errorf("duplicate glossary term %q", term)
		}
		seen[k] = true
	}
}

// TestGlossaryMatchesTestdata proves the Go list and the JSON have not drifted,
// the same way segment's role table is guarded.
func TestGlossaryMatchesTestdata(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("testdata", "glossary.json"))
	if err != nil {
		t.Fatalf("read glossary.json: %v", err)
	}

	var file struct {
		Terms        []string `json:"terms"`
		Qualitative  []string `json:"qualitative_markers"`
		Quantitative []string `json:"quantitative_markers"`
		Mixed        []string `json:"mixed_markers"`
	}
	if err := json.Unmarshal(raw, &file); err != nil {
		t.Fatalf("parse glossary.json: %v", err)
	}

	for _, c := range []struct {
		name      string
		got, want []string
	}{
		{"terms", glossaryTerms, file.Terms},
		{"qualitative markers", qualitativeMarkers, file.Qualitative},
		{"quantitative markers", quantitativeMarkers, file.Quantitative},
		{"mixed markers", mixedMarkers, file.Mixed},
	} {
		g, w := append([]string(nil), c.got...), append([]string(nil), c.want...)
		sort.Strings(g)
		sort.Strings(w)

		if len(g) != len(w) {
			t.Errorf("%s: Go has %d, glossary.json has %d", c.name, len(g), len(w))
			continue
		}
		for i := range g {
			if g[i] != w[i] {
				t.Errorf("%s: Go has %q where glossary.json has %q", c.name, g[i], w[i])
			}
		}
	}
}

// TestCalibrationAgainstRealPapers is documentation with an assertion attached.
//
// Six papers, measured 17 August 2026 on MATHPIX MARKDOWN — which is what the
// pipeline actually feeds this package. An earlier version of this table held
// numbers from a different PDF text extractor and was quietly wrong by a few
// hundredths; the source of a calibration number is part of the number.
//
// They cannot live in testdata, being PDFs of a megabyte or more each.
// Re-derive with `epistemicos-cli methodology <paper-id>`.
//
//	paper                          expected  got            score  qual/10k  quan/10k  terms  mixed
//	wedding vendors, pandemic      qual      qualitative    -0.92    7.11      0.28      20    no
//	people management, COVID       qual      qualitative    -0.55    4.37      1.29      22    no
//	leader-member exchange         quan      quantitative   +0.98    0.12     12.17      51    no
//	open innovation in SMEs        quan      quantitative   +0.98    0.15     13.82      30    no
//	TPB questionnaire validation   mix       qualitative    -0.37   10.05      4.59      52    YES
//	social mission, mixed-method   mix       needs review   +0.19    3.99      5.88      35    YES
//
// Four of four single-method papers correct, wide gap, no overlap. Both
// mixed-methods papers flagged.
//
// # The tuning that was available and not taken
//
// decisionMargin of 0.40 rather than 0.20 scores six out of six: the TPB paper
// at -0.37 would fall inside the band and read "needs review" like the other
// mixed one, instead of being called qualitative.
//
// It was not taken, and the reason is the point. The only evidence for 0.40 is
// that it fits these six papers, and it was found by looking at their results.
// The marker lists were chosen from the methods literature BEFORE anything was
// measured, precisely so they would not be fitted to a sample this small; moving
// the threshold afterwards to make that sample come out clean spends the
// discipline and buys a number with no support outside it.
//
// The argument for a wider band is real — a score near zero means both
// vocabularies are comparably present, which is close to what mixed methods
// means. If a larger corpus supports it, widen it then. The flag already catches
// both mixed papers without it.
func TestCalibrationAgainstRealPapers(t *testing.T) {
	// A floor belongs BELOW its evidence, not on it. The thinnest real paper
	// touched 20 distinct glossary terms, with a marker count lower again; 4
	// guards against a near-empty document rather than discriminating.
	if minDistinctMarkers >= 6 {
		t.Errorf("minDistinctMarkers = %d; a floor at or above the thinnest observed paper refuses the next ordinary document", minDistinctMarkers)
	}

	// Below 0.37 the TPB paper gets called rather than left open; at 0.55 or
	// above the second qualitative paper stops resolving at all. This asserts
	// only that the constant sits inside the range the evidence permits.
	if decisionMargin <= 0 || decisionMargin >= 0.55 {
		t.Errorf("decisionMargin = %.2f; at or above 0.55 the -0.55 qualitative paper would no longer resolve", decisionMargin)
	}
}

// TestEveryMarkerIsReachable is the test that would have caught a real bug, and
// did not exist until the bug found itself.
//
// markerSet normalises typographic apostrophes into straight ones. The lookup
// that classified each term did not, so "Cronbach’s Alpha" — the one glossary
// entry with a curly apostrophe, and a quantitative marker — never matched its
// own list. It counted toward nothing.
//
// Nothing failed. One missing marker out of sixty-six shifts a score slightly
// and produces no error, which is why it survived unit tests and was only
// visible when a real paper printed its evidence and the term read "neither"
// beside a list that plainly contains it.
//
// This asserts the property directly: every marker, fed to Classify inside a
// sentence, must come back attributed to the side it belongs to.
func TestEveryMarkerIsReachable(t *testing.T) {
	check := func(markers []string, want string) {
		t.Helper()
		for _, marker := range markers {
			got := Classify("The study reports " + marker + " in detail here.")

			var found bool
			for _, m := range got.Matches {
				if strings.EqualFold(m.Term, marker) {
					found = true
					if m.Marker != want {
						t.Errorf("%q counted toward %q, want %q", marker, m.Marker, want)
					}
				}
			}
			if !found {
				t.Errorf("%q did not match itself; it can never contribute", marker)
			}
		}
	}

	check(qualitativeMarkers, "qualitative")
	check(quantitativeMarkers, "quantitative")
	check(mixedMarkers, "mixed")
}
