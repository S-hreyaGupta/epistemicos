package segmentation

import (
	"context"
	"errors"
	"strings"
	"testing"
)

// TestSegment_RefusesWhenTheGateSaysNo is the whole reason the gate is a
// constructor argument rather than a setter.
//
// A non-empirical paper does not segment badly. It segments plausibly: the role
// table finds "Methods" and "Results" in a systematic review's own reporting of
// other people's studies, and every downstream consumer then treats a review as
// though it held its own data.
func TestSegment_RefusesWhenTheGateSaysNo(t *testing.T) {
	svc, store, _ := harness(t, reviewMarkdown)

	refusal := errors.New("paper is not empirical and is out of scope: classified B")
	svc.gate = &fakeGate{err: refusal}

	// The store already holds the harness's run, so count what Segment adds.
	before := store.run

	_, err := svc.Segment(context.Background(), "paper-1")
	if err == nil {
		t.Fatal("Segment ran on a paper the gate refused")
	}
	if !errors.Is(err, refusal) {
		t.Errorf("error = %v, want it to wrap the gate's refusal", err)
	}
	if !strings.Contains(err.Error(), "not empirical") {
		t.Errorf("error = %q, want it to carry the reason through", err)
	}
	if store.run != before {
		t.Error("Segment persisted a run for a refused paper")
	}
}

// TestSegment_RefusesWithNoGateAtAll. A nil gate must fail closed.
//
// The constructor takes the gate positionally so it cannot be forgotten, but a
// caller can still pass nil, and "no gate configured" must never mean "no gate
// needed". This is the same reasoning as the review gate the
// ApprovedMarkdownSource comment describes: the dangerous version is the one that
// disappears without anyone deciding to remove it.
func TestSegment_RefusesWithNoGateAtAll(t *testing.T) {
	svc, _, _ := harness(t, reviewMarkdown)
	svc.gate = nil

	_, err := svc.Segment(context.Background(), "paper-1")
	if err == nil {
		t.Fatal("Segment ran with no gate configured")
	}
	if !strings.Contains(err.Error(), "gate") {
		t.Errorf("error = %q, want it to name the missing gate", err)
	}
}

// TestSegment_ProceedsWhenAllowed. The gate must not be so strict that nothing
// gets through, which is the failure a refusal-only test would miss.
func TestSegment_ProceedsWhenAllowed(t *testing.T) {
	svc, store, _ := harness(t, reviewMarkdown)
	svc.gate = &fakeGate{}

	runID, err := svc.Segment(context.Background(), "paper-1")
	if err != nil {
		t.Fatalf("Segment: %v", err)
	}
	if runID == "" {
		t.Error("Segment returned an empty run id")
	}
	if store.run == nil || store.run.ID != runID {
		t.Error("the run was not persisted")
	}
	if len(store.run.Tasks) == 0 {
		t.Error("the fixture's open question did not survive into the saved run")
	}
}

// TestReviewIsNotGated. A run that exists is reviewable whatever the paper turned
// out to be. Gating the review of work already done would mean a reclassification
// could lock a reviewer out of answers they had part-written.
func TestReviewIsNotGated(t *testing.T) {
	svc, _, _ := harness(t, reviewMarkdown)
	svc.gate = &fakeGate{err: errors.New("out of scope")}

	if _, _, err := svc.Review(context.Background(), "run-1"); err != nil {
		t.Errorf("Review consulted the gate: %v", err)
	}
}
