package segment

import "testing"

// The gate's whole job is to say when Step 4 may run, so these tests are written
// as the state table rather than as scenarios. Every combination of open,
// resolved and rejected has exactly one right answer, and the ones that are easy
// to get wrong are called out individually below.

func runWithTasks(n int) Run {
	run := Run{}
	for i := 0; i < n; i++ {
		run.Tasks = append(run.Tasks, ReviewTask{SectionOrdinal: i, Reason: ReasonZeroRoleMatch, Status: TaskOpen})
		run.TaskIDs = append(run.TaskIDs, string(rune('a'+i)))
	}
	return run
}

func resolveD(task string) *ReviewDecision {
	return &ReviewDecision{ReviewTaskID: task, Decision: DecisionResolve, AssignedRole: RoleMethodology, ReviewerID: "shreya"}
}

func rejectD(task string) *ReviewDecision {
	return &ReviewDecision{ReviewTaskID: task, Decision: DecisionReject, Comment: "the heading is an OCR artifact", ReviewerID: "shreya"}
}

func TestGate_StateTable(t *testing.T) {
	cases := []struct {
		name      string
		tasks     int
		decisions map[string]*ReviewDecision
		want      ReviewState
	}{
		{
			// The ordinary machine-only run. It passes IMMEDIATELY: there is
			// nothing to wait for, and making it wait would block every clean
			// paper behind a review nobody needs to do.
			name: "no tasks at all", tasks: 0, decisions: nil, want: ReviewPassed,
		},
		{name: "every task open", tasks: 3, decisions: nil, want: ReviewOpen},
		{
			name: "some answered, one still open", tasks: 3,
			decisions: map[string]*ReviewDecision{"a": resolveD("a"), "b": resolveD("b")},
			want:      ReviewOpen,
		},
		{
			name: "all resolved", tasks: 3,
			decisions: map[string]*ReviewDecision{"a": resolveD("a"), "b": resolveD("b"), "c": resolveD("c")},
			want:      ReviewPassed,
		},
		{
			name: "all decided, one rejected", tasks: 3,
			decisions: map[string]*ReviewDecision{"a": resolveD("a"), "b": rejectD("b"), "c": resolveD("c")},
			want:      ReviewReturned,
		},
		{
			name: "all rejected", tasks: 3,
			decisions: map[string]*ReviewDecision{"a": rejectD("a"), "b": rejectD("b"), "c": rejectD("c")},
			want:      ReviewReturned,
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := Gate(runWithTasks(c.tasks), c.decisions)
			if got.State != c.want {
				t.Errorf("state = %q, want %q (open=%d resolved=%d rejected=%d)",
					got.State, c.want, got.Open, got.Resolved, got.Rejected)
			}
		})
	}
}

// TestGate_RejectionDoesNotReturnWhileQuestionsRemain is the ordering rule, and
// the one most likely to be "simplified" away later.
//
// A run with one rejection and two open questions is OPEN, not returned.
// Returning early would send the manuscript back naming one problem while two
// unexamined questions remained, and the author would fix that one thing and
// receive the rest a round later. The gate closes only when every question has
// been answered, which is what makes a returned run's report complete.
func TestGate_RejectionDoesNotReturnWhileQuestionsRemain(t *testing.T) {
	g := Gate(runWithTasks(3), map[string]*ReviewDecision{"b": rejectD("b")})

	if g.State != ReviewOpen {
		t.Errorf("state = %q, want %q — a rejection with questions still open must not return the paper", g.State, ReviewOpen)
	}
	if g.Rejected != 1 || g.Open != 2 {
		t.Errorf("counts = %d rejected, %d open; want 1 and 2", g.Rejected, g.Open)
	}
	if g.Passed() {
		t.Error("Passed() is true on an open run; Step 4 would run on a half-reviewed paper")
	}
}

// TestGate_MissingTaskIDCountsAsOpen.
//
// TaskIDs is assigned in parallel with Tasks by the service layer. If the two
// ever fall out of step, the safe reading of a task whose id is unknown is that
// it is UNANSWERED. Guessing the other way would let Step 4 run on a paper with
// questions nobody could look up.
func TestGate_MissingTaskIDCountsAsOpen(t *testing.T) {
	run := runWithTasks(3)
	run.TaskIDs = run.TaskIDs[:1]

	g := Gate(run, map[string]*ReviewDecision{"a": resolveD("a")})

	if g.State != ReviewOpen {
		t.Errorf("state = %q, want %q — a task with no id must never read as decided", g.State, ReviewOpen)
	}
	if g.Open != 2 {
		t.Errorf("open = %d, want 2", g.Open)
	}
}

// TestGate_RejectedIDsAreInRunOrder so a returned run's report lists its
// rejections in document order rather than in whatever order they were written.
func TestGate_RejectedIDsAreInRunOrder(t *testing.T) {
	g := Gate(runWithTasks(3), map[string]*ReviewDecision{
		"c": rejectD("c"), "a": rejectD("a"), "b": resolveD("b"),
	})

	if len(g.RejectedTaskIDs) != 2 || g.RejectedTaskIDs[0] != "a" || g.RejectedTaskIDs[1] != "c" {
		t.Errorf("rejected ids = %v, want [a c]", g.RejectedTaskIDs)
	}
}

// TestEffectiveFor_RejectedIsNotUnresolved is the distinction the whole gate
// rests on.
//
// "Nobody has looked at this" and "somebody looked and could not answer" must
// not read the same. Collapsing them would make an abandoned review
// indistinguishable from a finished one that failed.
func TestEffectiveFor_RejectedIsNotUnresolved(t *testing.T) {
	n := SectionNode{Classification: Classification{Status: StatusUnresolved}}

	eff := EffectiveFor(n, rejectD("a"))

	if eff.Status != EffectiveReviewerRejected {
		t.Errorf("status = %q, want %q", eff.Status, EffectiveReviewerRejected)
	}
	if eff.Status == EffectiveUnresolved {
		t.Error("a rejected node reads as merely unresolved; a human has already been here")
	}
	if eff.Role != "" {
		t.Errorf("role = %q, want empty — a rejection assigns nothing", eff.Role)
	}
	if !eff.FromReview {
		t.Error("FromReview is false on a rejection; a human produced this")
	}
}

// TestEffectiveFor_NoDecisionKeepsTheMachineAnswer guards the nil-safety of the
// new branch. Rejected() is called on a possibly-nil pointer before the existing
// nil check, so this is the case a careless refactor breaks.
func TestEffectiveFor_NoDecisionKeepsTheMachineAnswer(t *testing.T) {
	n := SectionNode{Classification: Classification{
		Role: RoleResults, ContentClass: ClassAnalytical, Status: StatusResolved,
	}}

	eff := EffectiveFor(n, nil)

	if eff.Role != RoleResults || eff.Status != EffectiveResolved || eff.FromReview {
		t.Errorf("got %+v; a node with no decision must keep exactly what the machine said", eff)
	}
}

// TestBuildAuthorReturn_OnlyForAReturnedRun.
//
// The precondition lives in the domain rather than at the call site because
// there will be more than one call site, and a precondition enforced in one of
// them is not enforced.
func TestBuildAuthorReturn_OnlyForAReturnedRun(t *testing.T) {
	passed := Gate(runWithTasks(1), map[string]*ReviewDecision{"a": resolveD("a")})
	if !passed.Passed() {
		t.Fatal("fixture is wrong: expected a passed run")
	}

	if items := BuildAuthorReturn(runWithTasks(1), map[string]*ReviewDecision{"a": resolveD("a")}); items != nil {
		t.Errorf("built %d items for a passed run, want none — nothing was rejected, so there is nothing to tell the author", len(items))
	}
}

// TestBuildAuthorReturn_CarriesTheReviewersWords.
//
// The comment is the message. An item that lost it would name a heading and give
// no reason, which is the thing the mandatory-comment rule exists to prevent.
func TestBuildAuthorReturn_CarriesTheReviewersWords(t *testing.T) {
	run := runWithTasks(2)
	run.Nodes = []SectionNode{
		{Ordinal: 0, ParentOrdinal: -1, HeadingLevel: 1, HeadingRaw: "A Study Of Things"},
		{Ordinal: 1, ParentOrdinal: 0, HeadingLevel: 2, HeadingRaw: "5.3 Future Directions"},
	}
	run.Tasks[1].SectionOrdinal = 1

	items := BuildAuthorReturn(run, map[string]*ReviewDecision{
		"a": resolveD("a"), "b": rejectD("b"),
	})

	if len(items) != 1 {
		t.Fatalf("built %d items, want 1", len(items))
	}
	if items[0].Comment != "the heading is an OCR artifact" {
		t.Errorf("comment = %q, want the reviewer's own words", items[0].Comment)
	}
	if items[0].HeadingRaw != "5.3 Future Directions" {
		t.Errorf("heading = %q, want the rejected node's", items[0].HeadingRaw)
	}
	// Placement, not just the heading. "5.3" alone is not a location.
	if len(items[0].AncestorHeadings) != 1 || items[0].AncestorHeadings[0] != "A Study Of Things" {
		t.Errorf("ancestors = %v, want the parent chain so the author can find the section", items[0].AncestorHeadings)
	}
}
