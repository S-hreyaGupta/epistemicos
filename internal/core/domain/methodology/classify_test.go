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
// than real PDFs: the six papers Alex supplied are megabytes each and cannot
// live in testdata, so their measured numbers are recorded in
// TestCalibrationAgainstRealPapers is documentation with an assertion attached.
//
// The six papers cannot live in testdata — they are PDFs, megabytes each — so
// what they measured is recorded here. Re-derive with
// `epistemicos-cli methodology <paper-id>`.
//
// Measured 17 August 2026 on MATHPIX MARKDOWN, which is what the pipeline
// actually feeds this package. An earlier version of this table held numbers
// taken from a different PDF text extractor and was quietly wrong by a few
// hundredths; the source of a calibration number is part of the number.
//
//	paper                        expected  got            score   qual/10k  quan/10k  terms  mixed
//	wedding vendors, pandemic    qual      qualitative    -0.92     7.11      0.28      20    no
//	people management, COVID     qual      qualitative    -0.55     4.37      1.29      22    no
//	leader-member exchange       quan      quantitative   +0.98     0.12     12.17      51    no
//	open innovation in SMEs      quan      quantitative   +0.98     0.15     13.82      30    no
//	TPB questionnaire validation mix       qualitative    -0.37    10.05      4.59      52    YES
//	social mission, mixed-method mix       needs review   +0.19     3.99      5.88      35    YES
//
// FOUR OF FOUR single-method papers correct, with a wide gap and no overlap.
// Both mixed papers flagged.
//
// # The tuning that was available and not taken
//
// A decisionMargin of 0.40 rather than 0.20 would score six out of six: the TPB
// paper at -0.37 would fall inside the band and read "needs review" like the
// other mixed one, instead of being called qualitative.
//
// It was not taken, and the reason is the point. The only evidence for 0.40 is
// that it fits these six papers, and it was found by looking at their results.
// The marker lists in this package were deliberately chosen from the methods
// literature BEFORE anything was measured, precisely so that they would not be
// fitted to a sample of six; moving the threshold afterwards to make the sample
// come out clean would give that up for a number with no support outside it.
//
// There is a genuine argument for a wider band — a score near zero means both
// vocabularies are comparably present, which is close to what mixed methods
// means, and 0.20 is a narrow reading of "balanced". If a larger corpus supports
// it, widen it then. The flag already catches both mixed papers without it.
func TestCalibrationAgainstRealPapers(t *testing.T) {
	// The floor must sit BELOW the evidence, not on it. The thinnest real paper
	// touched 20 distinct glossary terms; marker counts run lower than that, and
	// 4 is a guard against a near-empty document rather than a discriminator.
	if minDistinctMarkers >= 6 {
		t.Errorf("minDistinctMarkers = %d; a floor at or above the thinnest observed paper rejects the next ordinary document", minDistinctMarkers)
	}

	// Below 0.37 the TPB paper is called rather than left open; at or above 0.55
	// the second qualitative paper stops being called at all. Any value in
	// between is defensible, and this asserts only that the constant sits in the
	// range the evidence actually permits.
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
