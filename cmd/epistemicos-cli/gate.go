package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
)

// The write side of the review GATE, as opposed to the write side of a single
// answer. Three commands: reject one task, read the run's state, send the
// manuscript back.
//
// `gate` is deliberately read-only. Asking whether Step 4 may run must not itself
// freeze the decisions, or a reviewer checking their own progress would lock
// themselves out of correcting the answer they just gave.

// parseGateFlags reads --by and --comment, in the same hand-rolled style as
// resolve: two positional arguments come first and flag.Parse stops at the first
// non-flag.
func parseGateFlags(cmd string, rest []string) (reviewer, comment, role string) {
	for i := 0; i < len(rest); i++ {
		name := rest[i]

		switch name {
		case "--by", "--comment", "--note", "--reason", "--role":
			if i+1 >= len(rest) {
				fmt.Fprintf(os.Stderr, "%s: %s needs a value\n", cmd, name)
				os.Exit(2)
			}
			i++
			switch name {
			case "--by":
				reviewer = rest[i]
			case "--comment", "--note", "--reason":
				comment = rest[i]
			case "--role":
				role = rest[i]
			}
		default:
			fmt.Fprintf(os.Stderr, "%s: unknown flag %q\n", cmd, name)
			os.Exit(2)
		}
	}
	return reviewer, comment, role
}

// runReject records a rejection against one task, or against the whole run.
//
// The --run form exists because the gate could previously be objected to only
// where the machine had already admitted doubt. A run whose sections all
// resolved raised no tasks, passed immediately, and offered a reviewer no action
// at all — which made this a review of the machine's questions rather than of
// its answers.
func runReject(args []string) {
	if len(args) < 1 {
		fmt.Fprintln(os.Stderr, "reject: a run id is required")
		fmt.Fprintln(os.Stderr, `  epistemicos-cli reject <run-id> <task-id> --by <you> --comment "why"`)
		fmt.Fprintln(os.Stderr, `  epistemicos-cli reject <run-id> --run --by <you> --comment "why"`)
		os.Exit(2)
	}
	runID := args[0]

	// --run may appear anywhere after the run id, so the task id is whatever
	// second positional argument is not a flag.
	wholeRun := false
	taskID := ""
	rest := args[1:]
	for i := 0; i < len(rest); i++ {
		if rest[i] == "--run" {
			wholeRun = true
			rest = append(append([]string{}, rest[:i]...), rest[i+1:]...)
			i--
			continue
		}
		if taskID == "" && !strings.HasPrefix(rest[i], "--") {
			taskID = rest[i]
			rest = append(append([]string{}, rest[:i]...), rest[i+1:]...)
			i--
		}
	}

	if wholeRun == (taskID != "") {
		fmt.Fprintln(os.Stderr, "reject: pass either a task id, or --run to reject the whole run")
		os.Exit(2)
	}

	reviewer, comment, _ := parseGateFlags("reject", rest)

	// Checked here as well as in the domain so the message names the flag the
	// operator has to add, rather than describing the rule abstractly.
	if strings.TrimSpace(comment) == "" {
		fmt.Fprintln(os.Stderr, "reject: --comment is required")
		fmt.Fprintln(os.Stderr, "  It is the sentence the author reads when the manuscript goes back.")
		fmt.Fprintln(os.Stderr, `  "unclear" is not something they can act on; name what is wrong with this section.`)
		os.Exit(2)
	}

	svc, _, cleanup := buildSegmentation()
	defer cleanup()

	ctx := context.Background()

	if wholeRun {
		// The state BEFORE, so the message can say what is being overturned. A
		// reviewer rejecting a run that already passed is doing something
		// different from rejecting one still under review, and should be told so.
		_, before, err := svc.GateState(ctx, runID)
		if err != nil {
			die(err)
		}

		gate, err := svc.RejectRun(ctx, runID, reviewer, comment)
		if err != nil {
			die(err)
		}

		fmt.Printf("rejected run %s\n", runID)
		fmt.Printf("  reviewer: %s\n", reviewer)
		fmt.Printf("  reason:   %s\n\n", comment)
		printGate(gate)

		if before.Passed() {
			fmt.Printf("\nThis run had PASSED. It is now returned.\n")
			fmt.Printf("Passed means currently accepted rather than permanently final, which is\n")
			fmt.Printf("the only reading under which a clean run can be challenged at all.\n")
			fmt.Printf("\nAnything already derived from this run is stale. The run is marked\n")
			fmt.Printf("superseded, so a consumer holding its section map hash can tell.\n")
		}
		fmt.Printf("\n  epistemicos-cli return-to-author %s --by %s\n", runID, orPlaceholder(reviewer))
		return
	}

	decision, err := svc.Reject(ctx, runID, taskID, reviewer, comment)
	if err != nil {
		die(err)
	}

	fmt.Printf("recorded rejection %s\n", decision.ID)
	fmt.Printf("  task:     %s\n", decision.ReviewTaskID)
	fmt.Printf("  reviewer: %s\n", decision.ReviewerID)
	fmt.Printf("  reason:   %s\n", decision.Comment)

	// The consequence is printed immediately, because it is not local to this
	// task. A reviewer rejecting one heading is deciding the fate of the whole
	// manuscript, and finding that out later is finding it out too late.
	_, gate, err := svc.GateState(ctx, runID)
	if err != nil {
		die(err)
	}

	fmt.Println()
	printGate(gate)

	if gate.Returned() {
		fmt.Printf("\nThis manuscript now goes back to its author. Step 4 will not run on it.\n")

		// A rejection now returns the run immediately, even with questions
		// outstanding. That is the right state — "open" would read as nothing
		// being wrong — but the author then receives one problem rather than
		// all of them, so the reviewer is told here rather than discovering it
		// when the paper comes back a second time.
		if gate.Open > 0 {
			fmt.Printf("\n%d question", gate.Open)
			if gate.Open != 1 {
				fmt.Printf("s")
			}
			fmt.Printf(" remain unanswered. The author will be told about the\n")
			fmt.Printf("rejection only. Answering the rest first means they receive every\n")
			fmt.Printf("problem in one round instead of one per round.\n")
		}

		fmt.Printf("\n  epistemicos-cli return-to-author %s --by %s\n", runID, orPlaceholder(reviewer))
	}
}

// runGate prints a run's review state without changing it.
func runGate(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "gate: run id is required")
		os.Exit(2)
	}
	runID := args[0]

	svc, _, cleanup := buildSegmentation()
	defer cleanup()

	run, gate, err := svc.GateState(context.Background(), runID)
	if err != nil {
		die(err)
	}

	fmt.Printf("segmentation run %s\n", run.ID)
	fmt.Printf("  paper:        %s\n", run.ExtractionRunID)
	fmt.Printf("  rule version: %s\n\n", run.StructuralRuleVersion)

	printGate(gate)

	switch gate.State {
	case segment.ReviewOpen:
		fmt.Printf("\nStep 4 must not run. %d question", gate.Open)
		if gate.Open != 1 {
			fmt.Printf("s")
		}
		fmt.Printf(" still ha")
		if gate.Open == 1 {
			fmt.Printf("s")
		} else {
			fmt.Printf("ve")
		}
		fmt.Printf(" no answer.\n")
		fmt.Printf("\n  epistemicos-cli review %s\n", runID)

	case segment.ReviewPassed:
		if gate.Total == 0 {
			fmt.Printf("\nNo questions were raised, so there was nothing to wait for. The\n")
			fmt.Printf("effective view is identical to the machine's.\n")
		} else {
			fmt.Printf("\nEvery question is answered and none was rejected. Step 4 may read\n")
			fmt.Printf("the effective classification.\n")
		}
		fmt.Printf("\n  epistemicos-cli effective %s\n", runID)

	case segment.ReviewReturned:
		fmt.Printf("\nThis manuscript goes back to its author. Step 4 will not run on it.\n")
		fmt.Printf("A rejection anywhere returns the whole paper: partial consumption of a\n")
		fmt.Printf("half-good segmentation is not defined.\n")
		fmt.Printf("\n  epistemicos-cli return-to-author %s --by <you>\n", runID)
	}
}

// runReturnToAuthor materializes the report and freezes the run.
func runReturnToAuthor(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "return-to-author: run id is required")
		os.Exit(2)
	}
	runID := args[0]
	reviewer, _, _ := parseGateFlags("return-to-author", args[1:])

	svc, _, cleanup := buildSegmentation()
	defer cleanup()

	gate, items, err := svc.ReturnToAuthor(context.Background(), runID, reviewer)
	if err != nil {
		die(err)
	}

	fmt.Printf("returned run %s to its author\n", runID)
	fmt.Printf("  %d of %d questions rejected\n\n", gate.Rejected, gate.Total)

	for i, it := range items {
		fmt.Printf("%d. ", i+1)
		if len(it.AncestorHeadings) > 0 {
			fmt.Printf("%s → ", strings.Join(trimAll(it.AncestorHeadings), " → "))
		}
		if it.HeadingRaw != "" {
			fmt.Printf("%s\n", strings.TrimSpace(it.HeadingRaw))
		} else {
			fmt.Printf("(the document as a whole)\n")
		}
		fmt.Printf("   why:  %s\n", it.Reason)
		fmt.Printf("   note: %s\n\n", it.Comment)
	}

	fmt.Printf("The decisions on this run are now frozen. Correcting one would change an\n")
	fmt.Printf("outcome the author has already been given, so a revised manuscript comes\n")
	fmt.Printf("back as a new document with a fresh run and a fresh queue.\n")
}

// printGate renders the counts and the verdict in one block, so that no command
// prints a state without the numbers behind it.
func printGate(g segment.GateResult) {
	fmt.Printf("  REVIEW STATE: %s\n", strings.ToUpper(string(g.State)))
	fmt.Printf("  questions:    %d total — %d open, %d resolved, %d rejected\n",
		g.Total, g.Open, g.Resolved, g.Rejected)

	// Printed separately from the counts because it is not one of them. A run
	// rejection concerns no question, and adding it to "rejected" would make a
	// run with zero tasks report one rejection out of none.
	if g.RunRejected {
		fmt.Printf("  the run itself was rejected\n")
	}
}

func orPlaceholder(s string) string {
	if strings.TrimSpace(s) == "" {
		return "<you>"
	}
	return s
}
