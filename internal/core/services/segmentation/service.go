// Package segmentation orchestrates Step 3: fetch approved markdown, segment
// and classify it, then persist the result.
//
// The orchestration is thin on purpose. Every rule lives in
// internal/core/domain/segment, which imports no ports and no adapters, so
// there is no interface through which segmentation could be made
// non-deterministic by a wiring change. This package supplies I/O and
// identifiers and nothing else.
package segmentation

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// Service runs Step 3.
type Service struct {
	source ports.ApprovedMarkdownSource
	store  ports.SegmentationStore

	// gate is the paper-type precondition. Step 3's role table is built from the
	// sections empirical papers have, so a systematic review or a conceptual
	// paper does not classify badly here — it classifies plausibly and wrongly.
	gate ports.PaperTypeGate
}

// New returns a Service over the given port implementations.
//
// The gate is a REQUIRED argument rather than an optional setter, and that is the
// whole design of it. An optional gate is one that can be omitted by accident,
// and the omission looks exactly like a deliberate decision afterwards — which is
// the failure mode the ApprovedMarkdownSource comment describes for the review
// gate. Making it positional means a caller who does not want it has to say so.
func New(source ports.ApprovedMarkdownSource, store ports.SegmentationStore, gate ports.PaperTypeGate) *Service {
	return &Service{source: source, store: store, gate: gate}
}

// Segment fetches the approved markdown for runRef, segments it, and persists
// the run. It returns the run id.
//
// The hash is re-verified here even though the source is expected to have done
// so. The two checks guard different things: the adapter proves the row is
// internally consistent, and this proves the bytes this service segmented are
// the bytes whose hash it is about to persist beside 22 byte offsets. A source
// that transformed the text between reading and returning it — a future
// caching layer normalising line endings, say — would pass the first check and
// fail this one.
func (s *Service) Segment(ctx context.Context, runRef string) (string, error) {
	// The gate runs FIRST, before the markdown is even fetched for segmenting.
	//
	// Not for speed. A paper that must not be segmented must not produce a
	// partial run either, and the cheapest way to guarantee that is to refuse
	// before anything is built. A gate applied after Build would leave a node set
	// in memory that only a discipline of not-persisting keeps out of the
	// database.
	if s.gate == nil {
		return "", fmt.Errorf("segment: no paper-type gate configured; Step 3 must not run on an unclassified paper")
	}
	if err := s.gate.Allow(ctx, runRef); err != nil {
		return "", fmt.Errorf("segment: %w", err)
	}

	markdown, hash, err := s.source.Get(ctx, runRef)
	if err != nil {
		return "", fmt.Errorf("segment: fetch approved markdown: %w", err)
	}

	sum := sha256.Sum256([]byte(markdown))
	if computed := hex.EncodeToString(sum[:]); computed != hash {
		return "", fmt.Errorf("segment: markdown hashes to %s but the source reported %s; offsets computed from it would be unverifiable", computed, hash)
	}

	doc, err := segment.Build([]byte(markdown))
	if err != nil {
		// §10 failed. The run is not persisted: a Failed run carrying a node
		// set that violates the invariant is worse than no run, because the
		// nodes look usable.
		return "", fmt.Errorf("segment: %w", err)
	}

	run := segment.NewRun(doc, runRef, hash)
	assignIDs(&run)

	if err := s.store.SaveRun(ctx, &run); err != nil {
		return "", fmt.Errorf("segment: persist run: %w", err)
	}

	return run.ID, nil
}

// assignIDs gives the run, its nodes and its tasks identifiers.
//
// This is the only reason uuid appears anywhere near segmentation. Keeping it
// out of the domain is what lets the architecture guard state something
// meaningful: that package's entire transitive import set is goldmark, so
// nothing in it can reach a network, a clock or a random source.
func assignIDs(run *segment.Run) {
	run.ID = uuid.NewString()

	run.NodeIDs = make([]string, len(run.Nodes))
	for i := range run.Nodes {
		run.NodeIDs[i] = uuid.NewString()
	}

	run.TaskIDs = make([]string, len(run.Tasks))
	for i := range run.Tasks {
		run.TaskIDs[i] = uuid.NewString()
	}
}
