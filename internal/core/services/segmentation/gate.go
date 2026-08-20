package segmentation

import (
	"context"
	"fmt"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
)

// The service side of the review gate: reject, read the state, and the two acts
// that end a run.

// Reject records that a reviewer looked at a task and no assignment is
// defensible.
//
// runID is required alongside taskID for the same reason Resolve requires it. A
// task id alone would let a mistyped id reject a question on a different paper,
// and unlike a wrong role — which is at least visible as a wrong role — a
// stray rejection sends someone else's manuscript back to its author.
func (s *Service) Reject(ctx context.Context, runID, taskID, reviewerID, comment string) (*segment.ReviewDecision, error) {
	_, task, err := s.findTask(ctx, runID, taskID)
	if err != nil {
		return nil, err
	}

	decision, err := segment.NewRejection(task, taskID, reviewerID, comment)
	if err != nil {
		return nil, fmt.Errorf("reject: %w", err)
	}

	return s.save(ctx, &decision)
}

// AcceptStructure answers the no_structure question: the document has no
// headings and may proceed as a single node.
func (s *Service) AcceptStructure(ctx context.Context, runID, taskID string, role segment.Role, reviewerID, comment string) (*segment.ReviewDecision, error) {
	_, task, err := s.findTask(ctx, runID, taskID)
	if err != nil {
		return nil, err
	}

	decision, err := segment.NewStructureDecision(task, taskID, role, reviewerID, comment)
	if err != nil {
		return nil, fmt.Errorf("accept-structure: %w", err)
	}

	return s.save(ctx, &decision)
}

// GateState computes a run's review state.
//
// Read-only and side-effect free, deliberately. Asking "may Step 4 run?" must
// not itself freeze the decisions — that would make merely LOOKING at the state
// change it, and a reviewer checking their own progress would lock themselves
// out.
func (s *Service) GateState(ctx context.Context, runID string) (*segment.Run, segment.GateResult, error) {
	run, err := s.store.GetRun(ctx, runID)
	if err != nil {
		return nil, segment.GateResult{}, fmt.Errorf("gate: load run %s: %w", runID, err)
	}

	decisions, err := s.store.GetDecisions(ctx, runID)
	if err != nil {
		return nil, segment.GateResult{}, fmt.Errorf("gate: load decisions for %s: %w", runID, err)
	}

	return run, segment.Gate(*run, decisions), nil
}

// Consume is the precondition Step 4 must satisfy before reading a run.
//
// It does two things in one call on purpose: it refuses a run that has not
// passed, and it freezes the decisions of one that has. Splitting them would let
// a caller check and then read without freezing, which is the arrangement the
// freeze exists to prevent.
//
// consumedBy is recorded so a frozen run can say what froze it. A run that
// cannot explain its own freeze is one nobody can reason about later.
func (s *Service) Consume(ctx context.Context, runID, consumedBy string) (*segment.Run, segment.GateResult, error) {
	run, gate, err := s.GateState(ctx, runID)
	if err != nil {
		return nil, segment.GateResult{}, err
	}

	if !gate.Passed() {
		return run, gate, fmt.Errorf("run %s is %s, not passed: %d of %d questions open, %d rejected; Step 4 reads only a passed run",
			runID, gate.State, gate.Open, gate.Total, gate.Rejected)
	}

	if err := s.store.MarkConsumed(ctx, runID, consumedBy); err != nil {
		return run, gate, fmt.Errorf("consume run %s: %w", runID, err)
	}

	return run, gate, nil
}

// ReturnToAuthor materializes the report for a returned run.
//
// The gate is recomputed here rather than taken from the caller. A caller who
// computed it a moment ago and passed the result would be acting on a state that
// may have changed, and the thing at stake is a manuscript being sent back.
func (s *Service) ReturnToAuthor(ctx context.Context, runID, returnedBy string) (segment.GateResult, []segment.AuthorReturnItem, error) {
	run, err := s.store.GetRun(ctx, runID)
	if err != nil {
		return segment.GateResult{}, nil, fmt.Errorf("return: load run %s: %w", runID, err)
	}

	decisions, err := s.store.GetDecisions(ctx, runID)
	if err != nil {
		return segment.GateResult{}, nil, fmt.Errorf("return: load decisions for %s: %w", runID, err)
	}

	gate := segment.Gate(*run, decisions)
	if !gate.Returned() {
		return gate, nil, fmt.Errorf("run %s is %s, not returned: %d of %d questions open, %d rejected; a manuscript goes back only when every question is answered and at least one was rejected",
			runID, gate.State, gate.Open, gate.Total, gate.Rejected)
	}

	items := segment.BuildAuthorReturn(*run, decisions)

	if err := s.store.SaveAuthorReturn(ctx, runID, uuid.NewString(), returnedBy, items); err != nil {
		return gate, items, fmt.Errorf("return run %s: %w", runID, err)
	}

	return gate, items, nil
}
