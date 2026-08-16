package segment

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"testing"
)

// TestClassify_ExactMatch covers §6 step 4. A heading that IS a keyword resolves
// to that keyword's role without the phrase scan running at all.
func TestClassify_ExactMatch(t *testing.T) {
	cases := []struct {
		in   string
		want Role
	}{
		{"abstract", RoleAbstract},
		{"introduction", RoleIntroduction},
		{"literature review", RoleLiteratureReview},
		{"methodology", RoleMethodology},
		{"results", RoleResults},
		{"discussion", RoleDiscussion},
		{"conclusion", RoleConclusion},
		{"references", RoleReferences},
	}

	for _, c := range cases {
		t.Run(c.in, func(t *testing.T) {
			got := Classify(c.in)

			if got.Role != c.want {
				t.Errorf("role = %q, want %q", got.Role, c.want)
			}
			if got.Status != StatusResolved {
				t.Errorf("status = %q, want %q", got.Status, StatusResolved)
			}
			if got.Method != MethodRule {
				t.Errorf("method = %q, want %q", got.Method, MethodRule)
			}
			if got.ContentClass != ContentClassFor(c.want) {
				t.Errorf("content class = %q, want %q", got.ContentClass, ContentClassFor(c.want))
			}
		})
	}
}

// TestClassify_ExactMatchBeatsPhraseScan is the ordering assertion.
//
// "background" is an introduction keyword, and it also occurs inside theory
// keywords such as "theoretical background". Standing alone as an entire
// heading it must resolve to introduction — if the phrase scan ran first it
// would still resolve, but the ordering stops being load-bearing and a future
// keyword addition could silently turn this into a tie. Asserting the order
// here keeps §6 step 4's precedence real rather than incidental.
func TestClassify_ExactMatchBeatsPhraseScan(t *testing.T) {
	got := Classify("background")

	if got.Role != RoleIntroduction {
		t.Errorf("role = %q, want %q", got.Role, RoleIntroduction)
	}
	if got.Status != StatusResolved {
		t.Errorf("status = %q, want %q", got.Status, StatusResolved)
	}
	if len(got.MatchedKeywords) != 1 || got.MatchedKeywords[0] != "background" {
		t.Errorf("matched keywords = %v, want exactly [background]", got.MatchedKeywords)
	}
}

// TestClassify_DistinctRoleCounting is the single most consequential rule in §6
// and the one an implementation is most likely to get wrong.
//
// Several keywords from ONE role resolve cleanly. Counting keyword hits instead
// of distinct roles would read a verbose methodology heading as a tie and send
// it to a human for no reason.
func TestClassify_DistinctRoleCounting(t *testing.T) {
	// "data collection" and "sample" are both methodology keywords, so this
	// heading produces two hits but only one role.
	got := Classify("data collection and sample")

	if got.Status != StatusResolved {
		t.Fatalf("status = %q, want %q — multiple keywords from one role must resolve, not tie", got.Status, StatusResolved)
	}
	if got.Role != RoleMethodology {
		t.Errorf("role = %q, want %q", got.Role, RoleMethodology)
	}
	if len(got.MatchedKeywords) < 2 {
		t.Errorf("matched keywords = %v, want at least two — the test is meaningless if only one keyword fired", got.MatchedKeywords)
	}
}

// TestClassify_MultiRoleMatch covers the tie: two distinct roles, no winner,
// candidates offered for a human to choose between.
//
// The heading CHANGED at 2.7. "Theoretical background and hypotheses derivation"
// was the fixture's multi-role case and turned out never to have been a tie:
// `background` was hitting inside `theoretical background`, one span counted
// twice. Here `background` and `literature review` are separate spans, so the
// disagreement is real and must survive.
func TestClassify_MultiRoleMatch(t *testing.T) {
	got := Classify("background and literature review")

	if got.Status != StatusUnresolved {
		t.Fatalf("status = %q, want %q", got.Status, StatusUnresolved)
	}
	if got.Role != "" {
		t.Errorf("role = %q, want empty — an unresolved node must not carry a guess", got.Role)
	}
	if got.ContentClass != "" {
		t.Errorf("content class = %q, want empty", got.ContentClass)
	}
	if got.Method != "" {
		t.Errorf("method = %q, want empty — nothing was decided, so no method decided it", got.Method)
	}

	want := []Role{RoleIntroduction, RoleLiteratureReview}
	if len(got.CandidateRoles) != len(want) {
		t.Fatalf("candidate roles = %v, want %v", got.CandidateRoles, want)
	}
	for i := range want {
		if got.CandidateRoles[i] != want[i] {
			t.Errorf("candidate role %d = %q, want %q", i, got.CandidateRoles[i], want[i])
		}
	}
}

// TestClassify_ZeroMatch covers the other unresolved case. It differs from a
// tie in offering no candidates: nothing matched, so there is no shortlist and
// the reviewer chooses from the whole role set.
func TestClassify_ZeroMatch(t *testing.T) {
	got := Classify("structural model")

	if got.Status != StatusUnresolved {
		t.Fatalf("status = %q, want %q", got.Status, StatusUnresolved)
	}
	if got.Role != "" {
		t.Errorf("role = %q, want empty", got.Role)
	}
	if len(got.CandidateRoles) != 0 {
		t.Errorf("candidate roles = %v, want none — a zero-match has no shortlist to offer", got.CandidateRoles)
	}
	if len(got.MatchedKeywords) != 0 {
		t.Errorf("matched keywords = %v, want none", got.MatchedKeywords)
	}
}

// TestClassify_BareContainer covers §7's hand-off into §6: an empty semantic
// heading is a structural assignment, not a classification failure.
//
// The distinction is the reason RoleUnknown exists separately from the empty
// role. It must resolve, so that no review task is raised — a heading reading
// only "Appendix B" has nothing for a human to adjudicate, and routing it to
// review would bury the genuine questions.
func TestClassify_BareContainer(t *testing.T) {
	got := Classify("")

	if got.Role != RoleUnknown {
		t.Errorf("role = %q, want %q", got.Role, RoleUnknown)
	}
	if got.Status != StatusResolved {
		t.Errorf("status = %q, want %q — a bare container is a complete answer, not a failure to find one", got.Status, StatusResolved)
	}
	if got.Method != MethodStructural {
		t.Errorf("method = %q, want %q", got.Method, MethodStructural)
	}
	if got.ContentClass != ClassAnalytical {
		t.Errorf("content class = %q, want %q", got.ContentClass, ClassAnalytical)
	}
}

// TestContainsWholeWord guards the substring boundary directly.
//
// Without the boundary test, "art" — from the literature_review keyword "state
// of the art" — fires on "particular", and "results" fires on "resultset". Both
// produce a confident wrong role rather than a visible failure.
func TestContainsWholeWord(t *testing.T) {
	cases := []struct {
		s, keyword string
		want       bool
	}{
		{"results", "results", true},
		{"the results section", "results", true},
		{"results and discussion", "results", true},
		{"resultset handling", "results", false},
		{"preresults", "results", false},
		{"in particular", "art", false},
		{"state of the art", "art", true},
		{"art", "art", true},
		{"art.", "art", true},
		{"the art, restated", "art", true},

		// Non-ASCII neighbours must count as word characters, or a keyword
		// could match across an accented letter.
		{"análisis", "lisis", false},
		{"datos análisis", "análisis", true},

		{"anything", "", false},
	}

	for _, c := range cases {
		t.Run(c.s+"/"+c.keyword, func(t *testing.T) {
			if got := containsWholeWord(c.s, c.keyword); got != c.want {
				t.Errorf("containsWholeWord(%q, %q) = %v, want %v", c.s, c.keyword, got, c.want)
			}
		})
	}
}

// fullRoleTable is the whole section_roles block, for the drift check below.
type fullRoleTable struct {
	SectionRoles map[string]struct {
		Keywords     []string `json:"keywords"`
		ContentClass string   `json:"content_class"`
	} `json:"section_roles"`
}

// TestRoleTableMatchesTable proves keywords.go and role.go still agree with the
// authoritative table, and that no keyword belongs to two roles.
//
// The second property is not cosmetic. keywordToRole inverts the table into a
// map, so a keyword owned by two roles would silently keep whichever role was
// built last, and the loss would be invisible at every later stage: the heading
// would classify confidently, to one of the two, with nothing to indicate a
// choice had been made. Asserting the property is what makes the inversion
// legitimate.
func TestRoleTableMatchesTable(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("testdata", "table.json"))
	if err != nil {
		t.Fatalf("read table.json: %v", err)
	}

	var table fullRoleTable
	if err := json.Unmarshal(raw, &table); err != nil {
		t.Fatalf("parse table.json: %v", err)
	}

	if len(table.SectionRoles) != len(roleKeywords) {
		t.Errorf("table.json defines %d roles, keywords.go defines %d", len(table.SectionRoles), len(roleKeywords))
	}

	seen := map[string]string{}
	for roleName, entry := range table.SectionRoles {
		role := Role(roleName)

		got, ok := roleKeywords[role]
		if !ok {
			t.Errorf("table.json defines role %q and keywords.go does not", roleName)
			continue
		}
		assertSameSet(t, "keywords for "+roleName, got, entry.Keywords)

		if class := ContentClassFor(role); string(class) != entry.ContentClass {
			t.Errorf("role %q: content class is %q in role.go, %q in table.json", roleName, class, entry.ContentClass)
		}

		for _, keyword := range entry.Keywords {
			if other, dup := seen[keyword]; dup {
				t.Errorf("keyword %q belongs to both %q and %q; keywordToRole inverts the table and would silently keep one", keyword, other, roleName)
			}
			seen[keyword] = roleName
		}
	}

	for role := range roleKeywords {
		if _, ok := table.SectionRoles[string(role)]; !ok {
			t.Errorf("keywords.go defines role %q and table.json does not", role)
		}
	}
}

// TestClassifyReproducesFixture is phase 3's done-condition: run §6 and §7 over
// every fixture heading and compare all four classification fields against
// expected.json, then check the review-task count and content §15 predicts.
//
// The document title is skipped. §4 assigns it separately — null role,
// administrative class — and it is not an input to the classification pipeline.
func TestClassifyReproducesFixture(t *testing.T) {
	exp := loadExpected(t)

	var unresolved []string

	for _, want := range exp.SectionNodes {
		if want.NodeKind == "document_title" {
			continue
		}
		// This test verifies §6 ALONE, so it must skip nodes whose stored role
		// did not come from §6. Two 2.2 rules produce such nodes: a section that
		// inherited its parent's role, and an appendix whose suffix matched
		// nothing and fell back to Unknown. Both are covered by their own tests
		// in inherit_test.go; comparing them here would be comparing the output
		// of one rule against the expectations of another.
		if derefOrEmpty(want.ClassificationMethod) == string(MethodInherited) {
			continue
		}
		if want.StructuralContainer != nil && derefOrEmpty(want.PrimaryRole) == string(RoleUnknown) {
			continue
		}

		t.Run(want.SectionID, func(t *testing.T) {
			_, _, semantic := ParseContainer(StripIdentifiers(Normalize(want.HeadingRaw)))
			got := Classify(semantic)

			if string(got.Role) != derefOrEmpty(want.PrimaryRole) {
				t.Errorf("primary_role = %q, want %q", got.Role, derefOrEmpty(want.PrimaryRole))
			}
			if string(got.ContentClass) != derefOrEmpty(want.ContentClass) {
				t.Errorf("content_class = %q, want %q", got.ContentClass, derefOrEmpty(want.ContentClass))
			}
			if string(got.Status) != want.ClassificationStatus {
				t.Errorf("classification_status = %q, want %q", got.Status, want.ClassificationStatus)
			}
			if string(got.Method) != derefOrEmpty(want.ClassificationMethod) {
				t.Errorf("classification_method = %q, want %q", got.Method, derefOrEmpty(want.ClassificationMethod))
			}
		})

		// Count from the STORED status, not from a fresh Classify call: after
		// 2.2 the two legitimately differ for inherited and fallback nodes, and
		// the review tasks follow what was stored.
		if want.ClassificationStatus == string(StatusUnresolved) {
			unresolved = append(unresolved, want.SectionID)
		}
	}

	if len(unresolved) != len(exp.ReviewTasks) {
		t.Fatalf("%d nodes classify as unresolved, expected.json has %d ReviewTasks: %v", len(unresolved), len(exp.ReviewTasks), unresolved)
	}

	wantSections := make([]string, 0, len(exp.ReviewTasks))
	for _, task := range exp.ReviewTasks {
		wantSections = append(wantSections, task.SectionID)
	}
	sort.Strings(wantSections)
	sort.Strings(unresolved)

	for i := range wantSections {
		if unresolved[i] != wantSections[i] {
			t.Errorf("unresolved node %d is %s, expected.json raises a task for %s", i, unresolved[i], wantSections[i])
		}
	}
}

// TestClassifyReproducesFixtureTaskDetail checks the reason and candidates of
// every expected review task, not merely that the right nodes are unresolved.
// The two reasons demand different things of a reviewer, since only one of them
// comes with a shortlist.
//
// AT 2.7 THIS TEST GOES QUIET, AND THAT IS WORTH SAYING OUT LOUD.
//
// The fixture now raises no tasks at all, so the loop below runs zero times and
// checks nothing. It was passing an assertion of "1 multi and 4 zero" hardcoded
// from 2.2, which is how the emptiness got noticed: the numbers stopped matching
// rather than the test quietly succeeding.
//
// It is kept, and its assertion rewritten to guard the OPPOSITE property: that
// the fixture still has none. If a future change reintroduces a review task on
// demo.md, this fails and the detail checks come back to life with it. A test
// that verifies nothing today but fails the moment there is something to verify
// is worth more than a deleted one.
func TestClassifyReproducesFixtureTaskDetail(t *testing.T) {
	exp := loadExpected(t)

	bySection := map[string]expectedNode{}
	for _, n := range exp.SectionNodes {
		bySection[n.SectionID] = n
	}

	multi, zero := 0, 0

	for _, task := range exp.ReviewTasks {
		t.Run(task.ReviewTaskID, func(t *testing.T) {
			node, ok := bySection[task.SectionID]
			if !ok {
				t.Fatalf("task references section %s, which is not in SectionNodes", task.SectionID)
			}

			_, _, semantic := ParseContainer(StripIdentifiers(Normalize(node.HeadingRaw)))
			got := Classify(semantic)

			if got.Status != StatusUnresolved {
				t.Fatalf("section %s classified %q, but expected.json raises a task for it", task.SectionID, got.Status)
			}

			switch task.ReviewReason {
			case "multi_role_match":
				multi++

				if len(got.CandidateRoles) != len(task.CandidateRoles) {
					t.Fatalf("candidate roles = %v, want %v", got.CandidateRoles, task.CandidateRoles)
				}
				for i, want := range task.CandidateRoles {
					if string(got.CandidateRoles[i]) != want {
						t.Errorf("candidate role %d = %q, want %q", i, got.CandidateRoles[i], want)
					}
				}

				assertSameSet(t, "matched keywords", got.MatchedKeywords, task.MatchedKeywords)

			case "zero_role_match":
				zero++

				if len(got.CandidateRoles) != 0 {
					t.Errorf("candidate roles = %v, want none for a zero-match", got.CandidateRoles)
				}

			default:
				t.Fatalf("unrecognised review reason %q", task.ReviewReason)
			}
		})
	}

	// The count over time: 1 multi and 5 zero at 2.1; 1 and 4 at 2.2, once "4.2
	// Structural model" inherited results from its parent; 0 and 0 at 2.7, once
	// nested-occurrence suppression resolved the multi and its four subsections
	// inherited from it.
	//
	// Asserting zero is asserting that the loop above SHOULD have been vacuous.
	// If either count moves, demo.md has an open question again and the detail
	// checks start running — which is the state this test was written for.
	if multi != 0 || zero != 0 {
		t.Errorf("review reasons: %d multi_role_match and %d zero_role_match, want 0 and 0 — demo.md classifies cleanly at 2.7", multi, zero)
	}
}
