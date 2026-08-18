package segment

import (
	"errors"
	"strings"
	"testing"
)

func roleTask() ReviewTask {
	return ReviewTask{SectionOrdinal: 3, Reason: ReasonZeroRoleMatch, Status: TaskOpen}
}

func titleTask() ReviewTask {
	return ReviewTask{SectionOrdinal: 0, Reason: ReasonTitleAmbiguity, Status: TaskOpen}
}

func TestNewRoleDecision(t *testing.T) {
	got, err := NewRoleDecision(roleTask(), "task-1", RoleMethodology, "shreya", "  the sample is described here  ")
	if err != nil {
		t.Fatalf("NewRoleDecision: %v", err)
	}

	if got.ReviewTaskID != "task-1" {
		t.Errorf("task id = %q, want %q", got.ReviewTaskID, "task-1")
	}
	if got.AssignedRole != RoleMethodology {
		t.Errorf("role = %q, want %q", got.AssignedRole, RoleMethodology)
	}
	if got.Comment != "the sample is described here" {
		t.Errorf("comment = %q, want it trimmed", got.Comment)
	}

	// The ID stays empty. The service assigns it, which is what keeps a UUID
	// generator out of this package's import set.
	if got.ID != "" {
		t.Errorf("id = %q, want empty — identity belongs to the service layer", got.ID)
	}
}

// TestNewRoleDecision_DerivesTheContentClass is the invariant that makes an
// impossible pair unrepresentable rather than merely discouraged.
func TestNewRoleDecision_DerivesTheContentClass(t *testing.T) {
	for _, role := range AssignableRoles() {
		got, err := NewRoleDecision(roleTask(), "task-1", role, "shreya", "")
		if err != nil {
			t.Fatalf("NewRoleDecision(%q): %v", role, err)
		}
		if want := ContentClassFor(role); got.AssignedContentClass != want {
			t.Errorf("role %q got class %q, want %q", role, got.AssignedContentClass, want)
		}
		if got.AssignedContentClass == "" {
			t.Errorf("role %q produced an empty content class", role)
		}
	}
}

// TestAssignableRoles_ExcludesUnknown. A task exists because a heading could not
// be classified. Unknown means "there was nothing to classify", so offering it
// would let a reviewer close a real question with the one value that denies the
// question existed.
func TestAssignableRoles_ExcludesUnknown(t *testing.T) {
	for _, r := range AssignableRoles() {
		if r == RoleUnknown {
			t.Fatal("AssignableRoles offers RoleUnknown")
		}
	}
	if IsAssignableRole(RoleUnknown) {
		t.Error("IsAssignableRole(RoleUnknown) = true")
	}

	// Every other role in the table is offered, so a reviewer is never blocked
	// from an answer the machine itself could have reached.
	if got, want := len(AssignableRoles()), len(roleContentClass)-1; got != want {
		t.Errorf("offers %d roles, want %d — the table has %d entries including Unknown", got, want, len(roleContentClass))
	}
}

func TestAssignableRoles_IsSorted(t *testing.T) {
	roles := AssignableRoles()
	for i := 1; i < len(roles); i++ {
		if roles[i-1] >= roles[i] {
			t.Fatalf("not sorted at %d: %q then %q", i, roles[i-1], roles[i])
		}
	}
}

func TestNewRoleDecision_RejectsBadInput(t *testing.T) {
	cases := []struct {
		name       string
		task       ReviewTask
		role       Role
		reviewer   string
		wantSubstr string
	}{
		{"unknown role", roleTask(), RoleUnknown, "shreya", "not a role a reviewer may assign"},
		{"empty role", roleTask(), "", "shreya", "not a role a reviewer may assign"},
		{"invented role", roleTask(), Role("methodolgy"), "shreya", "not a role a reviewer may assign"},
		{"no reviewer", roleTask(), RoleResults, "", "needs a reviewer"},
		{"whitespace reviewer", roleTask(), RoleResults, "   ", "needs a reviewer"},
		{"title task", titleTask(), RoleResults, "shreya", "use NewTitleDecision"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			_, err := NewRoleDecision(c.task, "task-1", c.role, c.reviewer, "")
			if err == nil {
				t.Fatal("accepted an invalid decision")
			}
			if !errors.Is(err, ErrDecisionInvalid) {
				t.Errorf("error does not wrap ErrDecisionInvalid: %v", err)
			}
			if !strings.Contains(err.Error(), c.wantSubstr) {
				t.Errorf("error = %q, want it to mention %q", err, c.wantSubstr)
			}
		})
	}
}

func TestNewTitleDecision(t *testing.T) {
	got, err := NewTitleDecision(titleTask(), "task-9", "  A systematic review on regenerative supply chains  ", "node-4", "alex", "confirmed from the PDF")
	if err != nil {
		t.Fatalf("NewTitleDecision: %v", err)
	}

	if got.AssignedDocumentTitleText != "A systematic review on regenerative supply chains" {
		t.Errorf("title = %q, want it trimmed", got.AssignedDocumentTitleText)
	}
	if got.AssignedDocumentTitleNodeID != "node-4" {
		t.Errorf("node id = %q, want %q", got.AssignedDocumentTitleNodeID, "node-4")
	}

	// A title decision carries no role. Writing one would make the overlay
	// report a section role for the document title, which is precisely the
	// two-axis confusion v2.0 exists to prevent.
	if got.AssignedRole != "" || got.AssignedContentClass != "" {
		t.Errorf("title decision carries a role: %+v", got)
	}
}

// TestNewTitleDecision_NodeIDIsOptional records the harder no-H1 case: Mathpix
// emitted no title node at all, so there is nothing to point at, and the text
// alone is a complete answer. Requiring the node would make that unanswerable.
func TestNewTitleDecision_NodeIDIsOptional(t *testing.T) {
	got, err := NewTitleDecision(titleTask(), "task-9", "A Study Of Things", "", "alex", "")
	if err != nil {
		t.Fatalf("NewTitleDecision: %v", err)
	}
	if got.AssignedDocumentTitleNodeID != "" {
		t.Errorf("node id = %q, want empty", got.AssignedDocumentTitleNodeID)
	}
}

func TestNewTitleDecision_RejectsBadInput(t *testing.T) {
	cases := []struct {
		name       string
		task       ReviewTask
		text       string
		reviewer   string
		wantSubstr string
	}{
		{"role task", roleTask(), "A Study", "alex", "needs a section role, not a title"},
		{"no text", titleTask(), "", "alex", "needs the title text"},
		{"whitespace text", titleTask(), "   \n ", "alex", "needs the title text"},
		{"no reviewer", titleTask(), "A Study", "", "needs a reviewer"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			_, err := NewTitleDecision(c.task, "task-9", c.text, "", c.reviewer, "")
			if err == nil {
				t.Fatal("accepted an invalid decision")
			}
			if !errors.Is(err, ErrDecisionInvalid) {
				t.Errorf("error does not wrap ErrDecisionInvalid: %v", err)
			}
			if !strings.Contains(err.Error(), c.wantSubstr) {
				t.Errorf("error = %q, want it to mention %q", err, c.wantSubstr)
			}
		})
	}
}

// TestNewRoleDecision_AcceptsARoleOutsideTheShortlist.
//
// A multi_role_match offers the roles that matched. They are a shortlist, not a
// constraint: a reviewer reading the section may correctly conclude that none of
// the matched keywords describe it. Rejecting that would be the tool overruling
// the human it just asked.
func TestNewRoleDecision_AcceptsARoleOutsideTheShortlist(t *testing.T) {
	task := ReviewTask{
		SectionOrdinal: 2,
		Reason:         ReasonMultiRoleMatch,
		CandidateRoles: []Role{RoleIntroduction, RoleTheory},
		Status:         TaskOpen,
	}

	got, err := NewRoleDecision(task, "task-1", RoleLiteratureReview, "shreya", "neither candidate fits")
	if err != nil {
		t.Fatalf("rejected a role outside the shortlist: %v", err)
	}
	if got.AssignedRole != RoleLiteratureReview {
		t.Errorf("role = %q, want %q", got.AssignedRole, RoleLiteratureReview)
	}
}

// TestDecisionFeedsTheOverlay ties the two halves together: a decision built
// here must be usable by EffectiveFor, and must win.
func TestDecisionFeedsTheOverlay(t *testing.T) {
	node := SectionNode{
		Ordinal:    3,
		HeadingRaw: "## 2.1 Sample and procedure",
		Classification: Classification{
			Status: StatusUnresolved,
		},
	}

	decision, err := NewRoleDecision(roleTask(), "task-1", RoleMethodology, "shreya", "")
	if err != nil {
		t.Fatalf("NewRoleDecision: %v", err)
	}

	eff := EffectiveFor(node, &decision)

	if eff.Role != RoleMethodology {
		t.Errorf("effective role = %q, want %q", eff.Role, RoleMethodology)
	}
	if eff.ContentClass != ClassAnalytical {
		t.Errorf("effective class = %q, want %q", eff.ContentClass, ClassAnalytical)
	}
	if eff.Status != EffectiveReviewerConfirmed {
		t.Errorf("effective status = %q, want %q", eff.Status, EffectiveReviewerConfirmed)
	}
	if !eff.FromReview {
		t.Error("FromReview is false on a human decision")
	}

	// And the node itself is untouched. The machine's honest "I did not know"
	// survives as provenance.
	if node.Classification.Status != StatusUnresolved || node.Classification.Role != "" {
		t.Errorf("the overlay mutated the node: %+v", node.Classification)
	}
}
