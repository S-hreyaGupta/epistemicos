package segment

import "testing"

// TestNested_IndependentOccurrenceSurvives is the case that corrected the rule.
//
// The first draft said "if a matched KEYWORD is contained inside another matched
// KEYWORD, discard the shorter one". That reasons about strings. This heading
// contains `background` twice — once standing alone, once inside `theoretical
// background` — and a string rule cannot tell the two apart, so it would discard
// both and resolve the heading to theory, silently destroying a real ambiguity.
//
// The heading genuinely says two things. It must stay a question.
func TestNested_IndependentOccurrenceSurvives(t *testing.T) {
	got := Classify("background and theoretical background")

	if got.Status != StatusUnresolved {
		t.Fatalf("status = %q, want %q — this heading really does say two things", got.Status, StatusUnresolved)
	}
	if len(got.CandidateRoles) != 2 {
		t.Fatalf("candidates = %v, want introduction and theory", got.CandidateRoles)
	}

	want := map[Role]bool{RoleIntroduction: true, RoleTheory: true}
	for _, r := range got.CandidateRoles {
		if !want[r] {
			t.Errorf("unexpected candidate %q", r)
		}
	}

	// Exactly one of the two `background` occurrences is suppressed: the nested
	// one. If both were suppressed the heading would resolve, and if neither
	// were, the rule would not be doing anything.
	var suppressed, live int
	for _, m := range got.Matches {
		if m.Keyword != "background" {
			continue
		}
		if m.SuppressedBy == "" {
			live++
		} else {
			suppressed++
			if m.SuppressedBy != "theoretical background" {
				t.Errorf("suppressed by %q, want %q", m.SuppressedBy, "theoretical background")
			}
		}
	}
	if live != 1 || suppressed != 1 {
		t.Errorf("background occurrences: %d live, %d suppressed; want 1 and 1", live, suppressed)
	}
}

// TestNested_SuppressionResolvesTheRealCase is the heading that started this.
//
// "Argumentation: Theoretical Background" from the arXiv paper. One occurrence
// of `background`, and it is inside `theoretical background`. Nothing
// independent survives to disagree, so it resolves.
func TestNested_SuppressionResolvesTheRealCase(t *testing.T) {
	got := Classify("argumentation: theoretical background")

	if got.Role != RoleTheory {
		t.Errorf("role = %q, want %q", got.Role, RoleTheory)
	}
	if got.Status != StatusResolved {
		t.Errorf("status = %q, want %q", got.Status, StatusResolved)
	}
	if got.Method != MethodRule {
		t.Errorf("method = %q, want %q", got.Method, MethodRule)
	}

	// MatchedKeywords carries what COUNTED. The suppressed hit is absent here
	// and present in Matches, which is what makes the decision explicable.
	for _, k := range got.MatchedKeywords {
		if k == "background" {
			t.Error("`background` counted; it was nested and must not have")
		}
	}

	var found bool
	for _, m := range got.Matches {
		if m.Keyword == "background" && m.SuppressedBy == "theoretical background" {
			found = true
		}
	}
	if !found {
		t.Error("the suppressed occurrence was discarded rather than recorded")
	}
}

// TestNested_ExactMatchIsUntouched. Exact match runs before the phrase scan and
// resolves outright, so a heading that IS a compound keyword never reaches
// suppression at all. This is why the whole problem stayed hidden: textbook
// headings are exact, and real papers add words.
func TestNested_ExactMatchIsUntouched(t *testing.T) {
	for _, c := range []struct {
		heading string
		want    Role
	}{
		{"theoretical background", RoleTheory},
		{"background literature", RoleLiteratureReview},
		{"discussion of results", RoleDiscussion},
		{"summary and conclusions", RoleConclusion},
		{"background", RoleIntroduction},
		{"summary", RoleAbstract},
	} {
		got := Classify(c.heading)
		if got.Role != c.want {
			t.Errorf("%q = %q, want %q", c.heading, got.Role, c.want)
		}
		if len(got.Matches) != 0 {
			t.Errorf("%q ran the phrase scan; exact match should have resolved it", c.heading)
		}
	}
}

// TestNested_AllFivePairs walks every nested pair in the table in its expanded
// form, where the trap actually springs.
func TestNested_AllFivePairs(t *testing.T) {
	for _, c := range []struct {
		heading string
		want    Role
	}{
		{"argumentation: theoretical background", RoleTheory},
		{"theoretical background and hypotheses derivation", RoleTheory},
		{"a review of the background literature", RoleLiteratureReview},
		{"discussion of results and implications", RoleDiscussion},
		{"chapter summary and conclusions", RoleConclusion},
	} {
		got := Classify(c.heading)
		if got.Role != c.want {
			t.Errorf("%q = %q (status %q, candidates %v), want %q",
				c.heading, got.Role, got.Status, got.CandidateRoles, c.want)
		}
	}
}

// TestNested_DoesNotTouchGenuineTies is the limit.
//
// Suppression removes a hit that was never independent. It must not remove one
// that was. Neither keyword here sits inside the other, so both survive and the
// heading stays the question it is.
func TestNested_DoesNotTouchGenuineTies(t *testing.T) {
	got := Classify("background and literature review")

	if got.Status != StatusUnresolved {
		t.Fatalf("status = %q, want %q — two independent keywords disagree here", got.Status, StatusUnresolved)
	}
	if len(got.CandidateRoles) != 2 {
		t.Errorf("candidates = %v, want two", got.CandidateRoles)
	}
	for _, m := range got.Matches {
		if m.SuppressedBy != "" {
			t.Errorf("%q was suppressed by %q; neither keyword contains the other", m.Keyword, m.SuppressedBy)
		}
	}
}

// TestNested_SameRoleNestingStillResolves. Nesting within one role was never a
// problem — distinct-role counting already handled it — but the suppression must
// not break it either.
func TestNested_SameRoleNestingStillResolves(t *testing.T) {
	// "measurement model" (methodology) contains "measurement" (methodology).
	got := Classify("the measurement model and its fit")

	if got.Role != RoleMethodology {
		t.Errorf("role = %q, want %q", got.Role, RoleMethodology)
	}
	if got.Status != StatusResolved {
		t.Errorf("status = %q, want %q", got.Status, StatusResolved)
	}
}

// TestNested_ScanIsDeterministic.
//
// scanKeywords iterates keywordToRole, which is a map, and Go randomises map
// iteration. Without the sort, two runs over the same heading could name
// different suppressors and store different provenance for identical input.
// Determinism is the product here, so it is asserted rather than assumed.
func TestNested_ScanIsDeterministic(t *testing.T) {
	const heading = "background and theoretical background"

	first := Classify(heading)
	for i := 0; i < 50; i++ {
		got := Classify(heading)

		if len(got.Matches) != len(first.Matches) {
			t.Fatalf("run %d found %d matches, first run found %d", i, len(got.Matches), len(first.Matches))
		}
		for j := range got.Matches {
			if got.Matches[j] != first.Matches[j] {
				t.Fatalf("run %d match %d = %+v, first run = %+v", i, j, got.Matches[j], first.Matches[j])
			}
		}
	}
}

// TestWholeWordSpans_OverlappingOccurrences guards the scan loop's one subtlety.
//
// It advances one byte past each candidate START rather than past its end,
// because occurrences can overlap. Skipping to the end would find one "art" in
// "art art" and miss the other, which would then be invisible to suppression.
func TestWholeWordSpans_OverlappingOccurrences(t *testing.T) {
	got := wholeWordSpans("results and more results", "results")

	if len(got) != 2 {
		t.Fatalf("found %d occurrences, want 2: %v", len(got), got)
	}
	if got[0] != [2]int{0, 7} {
		t.Errorf("first span = %v, want [0 7]", got[0])
	}
	if got[1] != [2]int{17, 24} {
		t.Errorf("second span = %v, want [17 24]", got[1])
	}

	// A boundary failure must produce no span at all, not a shortened one.
	if spans := wholeWordSpans("resultset", "results"); len(spans) != 0 {
		t.Errorf("matched inside a word: %v", spans)
	}
}
