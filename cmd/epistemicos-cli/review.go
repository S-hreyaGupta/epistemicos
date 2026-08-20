package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/approved"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/services/segmentation"
)

// The review commands are the write side of Step 3, and until they existed the
// pipeline could ask sixty-five questions about one manuscript and store not a
// single answer.
//
// They are a CLI rather than an HTTP surface deliberately. The interesting parts
// — validating an answer against its task, deriving the content class, verifying
// the markdown still hashes to what the offsets were computed against — all live
// in the domain and the service, so an HTTP handler added later is a thin
// translation of the same calls. Building the CLI first proves the seam is in the
// right place; building the UI first would have proved only that a form submits.

// buildSegmentation assembles Step 3 with its gate.
//
// The gate is passed even though none of the three review commands can trigger
// it: they read an existing run, and Segment is the only method that consults it.
// Constructing it anyway is deliberate — the constructor takes it positionally so
// that it cannot be forgotten, and a caller who supplied nil "because this command
// does not need it" would leave a Service that silently cannot segment.
func buildSegmentation() (*segmentation.Service, *store.PostgresSegmentationStore, func()) {
	pool, cleanup := openPool()

	segStore := store.NewPostgresSegmentationStore(pool)
	svc := segmentation.New(approved.NewPapersSource(pool), segStore, buildPaperType(pool))

	return svc, segStore, cleanup
}

// runReview lists a run's review tasks with the context needed to answer them.
func runReview(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "review: run id is required (the id printed by `segment`)")
		os.Exit(2)
	}
	runID := args[0]

	full := false
	for _, a := range args[1:] {
		if a == "--full" {
			full = true
		}
	}

	svc, _, cleanup := buildSegmentation()
	defer cleanup()

	run, items, err := svc.Review(context.Background(), runID)
	if err != nil {
		die(err)
	}

	open := 0
	for _, it := range items {
		if it.Decision == nil {
			open++
		}
	}

	// Recomputed from the same rows the gate uses rather than counted here, so
	// this header and `gate` can never disagree about the same run.
	_, gate, gerr := svc.GateState(context.Background(), runID)

	fmt.Printf("segmentation run %s\n", run.ID)
	fmt.Printf("  paper:         %s\n", run.ExtractionRunID)
	fmt.Printf("  rule version:  %s\n", run.StructuralRuleVersion)
	if gerr == nil {
		printGate(gate)
	}
	fmt.Println()

	if len(items) == 0 {
		fmt.Printf("No review tasks. Every section classified cleanly.\n")
		return
	}

	for _, it := range items {
		fmt.Printf("────────────────────────────────────────────────────────────────────\n")
		fmt.Printf("task %s\n", it.TaskID)
		fmt.Printf("  why:      %s\n", it.Task.Reason)

		if len(it.AncestorHeadings) > 0 {
			fmt.Printf("  under:    %s\n", strings.Join(trimAll(it.AncestorHeadings), "  ▸  "))
		}
		if it.Heading != "" {
			fmt.Printf("  heading:  %s\n", strings.TrimSpace(it.Heading))
		} else {
			fmt.Printf("  heading:  (no candidate node — the question is about the whole document)\n")
		}

		if len(it.Task.MatchedKeywords) > 0 {
			fmt.Printf("  matched:  %s\n", strings.Join(it.Task.MatchedKeywords, ", "))
		}
		if len(it.CandidateRoles) > 0 {
			fmt.Printf("  shortlist: %s   (advisory — any role is accepted)\n", joinRoles(it.CandidateRoles))
		}

		if it.Decision != nil {
			d := it.Decision
			fmt.Printf("\n  ANSWERED by %s\n", d.ReviewerID)
			if d.AssignedRole != "" {
				fmt.Printf("    role:    %s (%s)\n", d.AssignedRole, d.AssignedContentClass)
			}
			if d.AssignedDocumentTitleText != "" {
				fmt.Printf("    title:   %s\n", truncate(d.AssignedDocumentTitleText, 60))
			}
			if d.Comment != "" {
				fmt.Printf("    note:    %s\n", d.Comment)
			}
		}

		if text := strings.TrimSpace(it.Text); text != "" {
			shown := text
			if !full && len(shown) > 700 {
				shown = shown[:700] + "\n    […truncated — pass --full for all of it]"
			}
			fmt.Printf("\n  text:\n")
			for _, line := range strings.Split(shown, "\n") {
				fmt.Printf("    %s\n", line)
			}
		}
		fmt.Println()
	}

	fmt.Printf("────────────────────────────────────────────────────────────────────\n")

	if open == 0 {
		fmt.Printf("\nEvery question has an answer.\n")
		if gerr == nil {
			fmt.Println()
			printGate(gate)
			if gate.Returned() {
				fmt.Printf("\n  epistemicos-cli return-to-author %s --by <you>\n", runID)
			}
		}
		return
	}

	fmt.Printf("\nto answer one:\n")
	fmt.Printf("  epistemicos-cli resolve %s <task-id> --role <role> --by <you> [--note \"...\"]\n", runID)
	fmt.Printf("  epistemicos-cli resolve %s <task-id> --title \"...\" --by <you> [--node <section-id>]\n", runID)
	fmt.Printf("  epistemicos-cli resolve %s <task-id> --structure --by <you>\n\n", runID)
	fmt.Printf("or, if no answer is defensible:\n")
	fmt.Printf("  epistemicos-cli reject %s <task-id> --by <you> --comment \"why\"\n\n", runID)
	fmt.Printf("roles: %s\n", joinRoles(segment.AssignableRoles()))
	fmt.Printf("\nAn answer never overwrites the machine's. Its determination stays as\n")
	fmt.Printf("provenance and yours takes effect at read time, so \"the machine had no\n")
	fmt.Printf("answer and a human supplied one\" stays distinguishable from agreement.\n")
	fmt.Printf("\nA rejection is not an answer, it is the absence of one. It says a human\n")
	fmt.Printf("looked and could not decide, which is different from nobody having looked,\n")
	fmt.Printf("and it sends the whole manuscript back to its author.\n")
}

// runResolve records one reviewer's answer.
func runResolve(args []string) {
	if len(args) < 2 {
		fmt.Fprintln(os.Stderr, "resolve: run id and task id are required")
		fmt.Fprintln(os.Stderr, "  epistemicos-cli resolve <run-id> <task-id> --role <role> --by <you>")
		os.Exit(2)
	}
	runID, taskID := args[0], args[1]

	var role, title, nodeID, reviewer, note string
	structure := false

	// Parsed by hand rather than with the flag package because the two
	// positional arguments come first, and flag.Parse stops at the first
	// non-flag. Kept as an explicit index walk with no closure over the loop
	// variable: a closure that advanced i would depend on Go 1.22's
	// per-iteration loop semantics, which is a subtle thing to rest an argument
	// parser on.
	rest := args[2:]
	for i := 0; i < len(rest); i++ {
		name := rest[i]

		// --structure takes no value: it names WHICH question is being answered,
		// not what the answer is. The optional --role beside it is the answer.
		if name == "--structure" {
			structure = true
			continue
		}

		if name == "--role" || name == "--title" || name == "--node" ||
			name == "--by" || name == "--note" || name == "--comment" {
			if i+1 >= len(rest) {
				fmt.Fprintf(os.Stderr, "resolve: %s needs a value\n", name)
				os.Exit(2)
			}
			i++
			switch name {
			case "--role":
				role = rest[i]
			case "--title":
				title = rest[i]
			case "--node":
				nodeID = rest[i]
			case "--by":
				reviewer = rest[i]
			case "--note", "--comment":
				note = rest[i]
			}
			continue
		}

		fmt.Fprintf(os.Stderr, "resolve: unknown flag %q\n", name)
		os.Exit(2)
	}

	// Three shapes of answer, exactly one of which must be chosen. --structure
	// may carry a --role, so it is checked first and excludes --title rather
	// than being folded into the role/title pair.
	switch {
	case structure && title != "":
		fmt.Fprintln(os.Stderr, "resolve: --structure answers whether a document with no headings may proceed; it cannot also name the title")
		os.Exit(2)
	case !structure && (role == "") == (title == ""):
		fmt.Fprintln(os.Stderr, "resolve: pass exactly one of:")
		fmt.Fprintln(os.Stderr, "  --role <role>   a section's role")
		fmt.Fprintln(os.Stderr, `  --title "..."   the document title`)
		fmt.Fprintln(os.Stderr, "  --structure     a document with no headings may proceed as one node")
		os.Exit(2)
	}

	svc, _, cleanup := buildSegmentation()
	defer cleanup()

	ctx := context.Background()

	var (
		decision *segment.ReviewDecision
		err      error
	)
	switch {
	case structure:
		decision, err = svc.AcceptStructure(ctx, runID, taskID, segment.Role(role), reviewer, note)
	case role != "":
		decision, err = svc.Resolve(ctx, runID, taskID, segment.Role(role), reviewer, note)
	default:
		decision, err = svc.ResolveTitle(ctx, runID, taskID, title, nodeID, reviewer, note)
	}
	if err != nil {
		die(err)
	}

	fmt.Printf("recorded decision %s\n", decision.ID)
	fmt.Printf("  task:     %s\n", decision.ReviewTaskID)
	fmt.Printf("  reviewer: %s\n", decision.ReviewerID)
	if decision.AssignedRole != "" {
		fmt.Printf("  role:     %s (%s)\n", decision.AssignedRole, decision.AssignedContentClass)
	}
	if decision.AssignedDocumentTitleText != "" {
		fmt.Printf("  title:    %s\n", decision.AssignedDocumentTitleText)
	}
	if decision.Comment != "" {
		fmt.Printf("  note:     %s\n", decision.Comment)
	}

	fmt.Printf("\nThe task is now resolved. The machine's determination on the node is\n")
	fmt.Printf("unchanged; this decision takes effect at read time.\n")

	// The run state, every time, because an answer is only interesting in
	// relation to whether it was the last one. A reviewer who has just closed the
	// final question should be told so here rather than discovering it by
	// checking separately.
	if _, gate, gerr := svc.GateState(ctx, runID); gerr == nil {
		fmt.Println()
		printGate(gate)
		if gate.Passed() {
			fmt.Printf("\nThat was the last one. Step 4 may now read this run.\n")
		}
	}
}

// runEffective prints a run as a consumer sees it, with the overlay applied.
//
// This exists because the overlay is the whole point and was, until now,
// unobservable: EffectiveFor was tested and correct and nothing ever called it
// against real data. A reviewer who answers a question deserves to see the
// answer take effect, and Step 4 deserves a reference for what it will read.
func runEffective(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "effective: run id is required")
		os.Exit(2)
	}
	runID := args[0]

	_, segStore, cleanup := buildSegmentation()
	defer cleanup()

	ctx := context.Background()

	run, err := segStore.GetRun(ctx, runID)
	if err != nil {
		die(err)
	}
	decisions, err := segStore.GetDecisions(ctx, runID)
	if err != nil {
		die(err)
	}

	// A node's decision is reached through its task, so index the other way.
	byOrdinal := map[int]*segment.ReviewDecision{}
	var titleDecision *segment.ReviewDecision
	for i, task := range run.Tasks {
		if i >= len(run.TaskIDs) {
			break
		}
		d := decisions[run.TaskIDs[i]]
		if d == nil {
			continue
		}
		if task.Reason == segment.ReasonTitleAmbiguity {
			titleDecision = d
			continue
		}
		byOrdinal[task.SectionOrdinal] = d
	}

	gate := segment.Gate(*run, decisions)

	title := segment.EffectiveTitleFor(*run, titleDecision)

	fmt.Printf("segmentation run %s — effective view\n", run.ID)
	fmt.Printf("  title:   %s\n", truncate(title.Text, 66))
	fmt.Printf("  status:  %s", title.Status)
	if title.FromReview {
		fmt.Printf("   (from review)")
	}
	fmt.Printf("\n  found by: %s\n\n", title.Method)

	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "#\tHEADING\tROLE\tCLASS\tSTATUS\tSOURCE")
	fmt.Fprintln(w, "-\t-------\t----\t-----\t------\t------")

	humans := 0
	for _, n := range run.Nodes {
		eff := segment.EffectiveFor(n, byOrdinal[n.Ordinal])

		role := string(eff.Role)
		switch {
		case n.Kind == segment.KindDocumentTitle:
			role = "(document title)"
		case eff.Status == segment.EffectiveReviewerRejected:
			// Not "still open". A human has been here and could not answer,
			// which is a different fact and the one the gate acts on.
			role = "— rejected"
		case role == "":
			role = "— still open"
		}

		source := string(n.Classification.Method)
		if eff.FromReview {
			source = "HUMAN"
			humans++
		}
		if source == "" {
			source = "—"
		}

		heading := strings.Repeat("  ", indentFor(n.HeadingLevel)) + truncate(n.HeadingRaw, 44)
		fmt.Fprintf(w, "%d\t%s\t%s\t%s\t%s\t%s\n",
			n.Ordinal, heading, role, eff.ContentClass, eff.Status, source)
	}
	_ = w.Flush()

	fmt.Printf("\n%d of %d sections carry a human decision.\n", humans, len(run.Nodes))
	fmt.Printf("Rows marked HUMAN read from review_decisions. The machine's own answer for\n")
	fmt.Printf("those rows is still stored on the node and is visible with `segment`.\n")

	// The gate goes at the END rather than the top, because this view is worth
	// reading either way. Printing "not passed" first would suggest the rows
	// below are not worth looking at, when inspecting them is exactly how a
	// reviewer decides what to do next.
	fmt.Println()
	printGate(gate)
	if !gate.Passed() {
		fmt.Printf("\nThis is what Step 4 WOULD read. It may not read it yet: the run is %s.\n", gate.State)
	}
}

func joinRoles(roles []segment.Role) string {
	parts := make([]string, 0, len(roles))
	for _, r := range roles {
		parts = append(parts, string(r))
	}
	return strings.Join(parts, ", ")
}

func trimAll(in []string) []string {
	out := make([]string, 0, len(in))
	for _, s := range in {
		out = append(out, strings.TrimSpace(s))
	}
	return out
}
