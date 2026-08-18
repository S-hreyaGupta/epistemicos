package segmentation

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
)

// ReviewItem is one review task with everything a person needs to answer it.
//
// The text is included rather than left to the caller to slice. Every consumer
// would otherwise repeat the same offset arithmetic against the same markdown,
// and one of them would eventually do it against markdown that had changed.
type ReviewItem struct {
	TaskID string
	Task   segment.ReviewTask

	// Heading is the node's own heading, or empty for a title task on a document
	// with no candidate node at all.
	Heading string

	// AncestorHeadings places the section in the document, outermost first.
	AncestorHeadings []string

	// Text is the node's span unioned with its descendants' — §8's review
	// context. A parent node owns only the bytes before its first child, which on
	// the reference fixture is two of them, so the node's own span alone would
	// show a reviewer nothing.
	Text string

	// Decision is the human answer already recorded, or nil.
	Decision *segment.ReviewDecision

	// CandidateRoles is the shortlist for a multi_role_match. Advisory: the
	// domain accepts an answer outside it.
	CandidateRoles []segment.Role

	// AssignableRoles is the full set a reviewer may choose from, so a caller can
	// render a complete list without importing the role table.
	AssignableRoles []segment.Role
}

// Review returns a run and its open questions, each with the context needed to
// answer it and any decision already made.
//
// The markdown hash is re-verified against the run's stored hash, and that check
// is the reason this lives in a service rather than in the CLI. Every offset in
// the run indexes into one exact text. Slicing today's markdown with yesterday's
// offsets does not fail — it returns plausible-looking prose from the wrong part
// of the paper, and a reviewer would answer a question about a section they were
// never shown.
func (s *Service) Review(ctx context.Context, runID string) (*segment.Run, []ReviewItem, error) {
	run, err := s.store.GetRun(ctx, runID)
	if err != nil {
		return nil, nil, fmt.Errorf("review: load run %s: %w", runID, err)
	}

	markdown, hash, err := s.source.Get(ctx, run.ExtractionRunID)
	if err != nil {
		return nil, nil, fmt.Errorf("review: fetch approved markdown for %s: %w", run.ExtractionRunID, err)
	}

	sum := sha256.Sum256([]byte(markdown))
	computed := hex.EncodeToString(sum[:])
	if computed != hash {
		return nil, nil, fmt.Errorf("review: markdown hashes to %s but the source reported %s", computed, hash)
	}
	if computed != run.ApprovedMarkdownHash {
		return nil, nil, fmt.Errorf(
			"review: run %s was segmented against markdown %s but the source now holds %s; its offsets would slice the wrong bytes and read as quotations rather than as errors",
			runID, run.ApprovedMarkdownHash, computed)
	}

	decisions, err := s.store.GetDecisions(ctx, runID)
	if err != nil {
		return nil, nil, fmt.Errorf("review: load decisions for %s: %w", runID, err)
	}

	md := []byte(markdown)
	assignable := segment.AssignableRoles()

	items := make([]ReviewItem, 0, len(run.Tasks))
	for i, task := range run.Tasks {
		taskID := ""
		if i < len(run.TaskIDs) {
			taskID = run.TaskIDs[i]
		}

		item := ReviewItem{
			TaskID:          taskID,
			Task:            task,
			Decision:        decisions[taskID],
			CandidateRoles:  task.CandidateRoles,
			AssignableRoles: assignable,
		}

		// A title task on a document with no candidate node carries -1, and there
		// is genuinely no context to show: the question is about the whole
		// document. Returning empty strings is the honest answer, and it is why
		// ContextFor's second return value is checked rather than ignored.
		if rc, ok := segment.ContextFor(run.Nodes, task.SectionOrdinal); ok {
			item.Heading = rc.Heading
			item.AncestorHeadings = rc.AncestorHeadings
			item.Text = rc.Text(md)
		}

		items = append(items, item)
	}

	return run, items, nil
}

// Resolve records a reviewer's role answer for one task.
//
// runID is required alongside taskID and is not redundant. A task id alone would
// let a mistyped id resolve a question on a different paper, which the overlay
// would then serve as a human-confirmed fact about a document nobody looked at.
// Requiring both means the task must belong to the run the caller thinks it does.
func (s *Service) Resolve(ctx context.Context, runID, taskID string, role segment.Role, reviewerID, comment string) (*segment.ReviewDecision, error) {
	_, task, err := s.findTask(ctx, runID, taskID)
	if err != nil {
		return nil, err
	}

	decision, err := segment.NewRoleDecision(task, taskID, role, reviewerID, comment)
	if err != nil {
		return nil, fmt.Errorf("resolve: %w", err)
	}

	return s.save(ctx, &decision)
}

// ResolveTitle records a reviewer's answer to a title_ambiguity task.
func (s *Service) ResolveTitle(ctx context.Context, runID, taskID, titleText, titleNodeID, reviewerID, comment string) (*segment.ReviewDecision, error) {
	run, task, err := s.findTask(ctx, runID, taskID)
	if err != nil {
		return nil, err
	}

	// A node id is optional, but a node id that is not part of this run is not.
	// The schema's foreign key would catch a nonexistent node; it would happily
	// accept a real node belonging to a different paper.
	if titleNodeID != "" {
		found := false
		for _, id := range run.NodeIDs {
			if id == titleNodeID {
				found = true
				break
			}
		}
		if !found {
			return nil, fmt.Errorf("resolve-title: node %s is not part of run %s", titleNodeID, runID)
		}
	}

	decision, err := segment.NewTitleDecision(task, taskID, titleText, titleNodeID, reviewerID, comment)
	if err != nil {
		return nil, fmt.Errorf("resolve-title: %w", err)
	}

	return s.save(ctx, &decision)
}

func (s *Service) findTask(ctx context.Context, runID, taskID string) (*segment.Run, segment.ReviewTask, error) {
	run, err := s.store.GetRun(ctx, runID)
	if err != nil {
		return nil, segment.ReviewTask{}, fmt.Errorf("load run %s: %w", runID, err)
	}

	for i, id := range run.TaskIDs {
		if id != taskID {
			continue
		}
		if i >= len(run.Tasks) {
			return nil, segment.ReviewTask{}, fmt.Errorf("run %s has %d task ids but %d tasks", runID, len(run.TaskIDs), len(run.Tasks))
		}
		return run, run.Tasks[i], nil
	}

	return nil, segment.ReviewTask{}, fmt.Errorf("run %s has no review task %s", runID, taskID)
}

// save assigns identity and persists. The ID is generated here for the same
// reason assignIDs exists: the domain has no UUID generator, and giving it one
// would weaken what the architecture guard is able to state.
func (s *Service) save(ctx context.Context, d *segment.ReviewDecision) (*segment.ReviewDecision, error) {
	d.ID = uuid.NewString()

	if err := s.store.SaveDecision(ctx, d); err != nil {
		return nil, fmt.Errorf("persist decision for task %s: %w", d.ReviewTaskID, err)
	}
	return d, nil
}
