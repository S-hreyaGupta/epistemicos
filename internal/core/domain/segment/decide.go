package segment

import (
	"errors"
	"fmt"
	"sort"
	"strings"
)

// A reviewer's answer is constructed and validated HERE, in the domain, rather
// than at whatever edge happens to collect it.
//
// The overlay in overlay.go is the reason. A stored decision OUTRANKS the
// machine's determination at read time and can never be overwritten by a later
// run, so a malformed one is not a bad row that a re-run corrects — it is a
// permanent, authoritative wrong answer sitting on top of a correct one. Every
// route in (a CLI today, an HTTP handler tomorrow, an import script after that)
// must therefore pass the same gate, and the only way to guarantee that is for
// the gate to be the sole way to build the value.
//
// Hence no exported literal construction path: NewRoleDecision and
// NewTitleDecision are the constructors, and both return an error rather than a
// best effort.

// ErrDecisionInvalid wraps every rejection below so a caller can distinguish a
// reviewer's mistake, which deserves a message, from a storage failure, which
// deserves a retry.
var ErrDecisionInvalid = errors.New("review decision is not valid for its task")

// AssignableRoles is what a reviewer may choose from, sorted for a stable
// display order.
//
// RoleUnknown is DELIBERATELY EXCLUDED. It is a structural assignment for a node
// with no epistemic claim to classify — a bare "Appendix B" — and role.go is
// explicit that it "is NOT what an unclassifiable heading receives". A task only
// exists because a heading could not be classified, so offering Unknown would
// invite a reviewer to close a genuine question with the one value that means
// "there was no question". A reviewer who truly cannot decide should leave the
// task open, which is information; recording Unknown would destroy it.
func AssignableRoles() []Role {
	out := make([]Role, 0, len(roleContentClass))
	for r := range roleContentClass {
		if r == RoleUnknown {
			continue
		}
		out = append(out, r)
	}
	sort.Slice(out, func(i, j int) bool { return out[i] < out[j] })
	return out
}

// IsAssignableRole reports whether a reviewer may assign r.
func IsAssignableRole(r Role) bool {
	if r == RoleUnknown || r == "" {
		return false
	}
	_, ok := roleContentClass[r]
	return ok
}

// NewRoleDecision builds a validated role resolution for one review task.
//
// The ID is left empty. Identity is the service layer's job, exactly as it is
// for runs, nodes and tasks, and for the same reason: this package's whole
// transitive import set is goldmark, and adding a UUID generator to it would
// make the architecture guard in deps_test.go a weaker statement.
//
// # Why the content class is derived and not a parameter
//
// A role's class is a property of the role (role.go), so accepting both would
// let a caller store a pair that cannot occur — methodology as
// compliance_disclosure — and the overlay would then serve that pair to Step 4
// as a human-confirmed fact. Deriving it makes the impossible pair
// unrepresentable rather than merely discouraged.
//
// # Why the candidate shortlist is not a constraint
//
// A multi_role_match task carries the roles that matched. Those are offered to
// the reviewer, and 0005's schema comment calls them a shortlist. A reviewer
// looking at the section text may correctly conclude that NONE of the matched
// keywords describe it, and rejecting that answer would be the tool overruling
// the human it just asked. So a role outside the shortlist is accepted. It is
// visible afterwards by comparing the decision against the task.
func NewRoleDecision(task ReviewTask, taskID string, role Role, reviewerID, comment string) (ReviewDecision, error) {
	if task.Reason == ReasonTitleAmbiguity {
		return ReviewDecision{}, fmt.Errorf("%w: task %s asks what the paper is called, which a section role cannot answer; use NewTitleDecision", ErrDecisionInvalid, taskID)
	}
	if !IsAssignableRole(role) {
		return ReviewDecision{}, fmt.Errorf("%w: %q is not a role a reviewer may assign; choose one of %s", ErrDecisionInvalid, role, joinRoles(AssignableRoles()))
	}

	reviewerID = strings.TrimSpace(reviewerID)
	if reviewerID == "" {
		return ReviewDecision{}, fmt.Errorf("%w: a decision needs a reviewer; an anonymous answer that outranks the machine cannot be audited", ErrDecisionInvalid)
	}

	return ReviewDecision{
		ReviewTaskID:         taskID,
		AssignedRole:         role,
		AssignedContentClass: ContentClassFor(role),
		Comment:              strings.TrimSpace(comment),
		ReviewerID:           reviewerID,
	}, nil
}

// NewTitleDecision builds a validated title resolution for one title_ambiguity
// task.
//
// titleNodeID may be empty. §4's unresolved-title case includes documents where
// no node is the title — Mathpix emitted no H1 and nothing beneath it is a
// plausible candidate — and a reviewer supplying the text alone is a complete
// answer there. Pointing at a node when one fits is better, because it ties the
// title to a span, but requiring it would make the harder case unanswerable.
func NewTitleDecision(task ReviewTask, taskID, titleText, titleNodeID, reviewerID, comment string) (ReviewDecision, error) {
	if task.Reason != ReasonTitleAmbiguity {
		return ReviewDecision{}, fmt.Errorf("%w: task %s is a %s and needs a section role, not a title", ErrDecisionInvalid, taskID, task.Reason)
	}

	titleText = strings.TrimSpace(titleText)
	if titleText == "" {
		return ReviewDecision{}, fmt.Errorf("%w: a title decision needs the title text", ErrDecisionInvalid)
	}

	reviewerID = strings.TrimSpace(reviewerID)
	if reviewerID == "" {
		return ReviewDecision{}, fmt.Errorf("%w: a decision needs a reviewer; an anonymous answer that outranks the machine cannot be audited", ErrDecisionInvalid)
	}

	return ReviewDecision{
		ReviewTaskID:                taskID,
		AssignedDocumentTitleText:   titleText,
		AssignedDocumentTitleNodeID: strings.TrimSpace(titleNodeID),
		Comment:                     strings.TrimSpace(comment),
		ReviewerID:                  reviewerID,
	}, nil
}

func joinRoles(roles []Role) string {
	parts := make([]string, 0, len(roles))
	for _, r := range roles {
		parts = append(parts, string(r))
	}
	return strings.Join(parts, ", ")
}
