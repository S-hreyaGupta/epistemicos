package segment

// The run-level gate: the thing that decides whether Step 4 may run at all.
//
// Step 3 could already ask questions and store answers. What it could not do was
// END. There was no state meaning "every question is settled", so "Step 4 takes
// the human-reviewed version" was a convention rather than a rule, and a
// convention is not a gate. This file is that rule.
//
// # Why it is computed and not stored
//
// The same reason the effective classification is computed: it is derived
// entirely from rows that already exist. A stored review_state would be a second
// place for one fact to live, the two would eventually disagree, and nothing
// would say which was right. Reading it is cheap and always current.
//
// # Why closure is not an action
//
// There is no "submit review" step. The gate closes the moment the last open
// task receives a decision, because that IS the condition. An explicit close
// would introduce a fourth state — decided but not submitted — which nothing
// downstream can act on and which a reviewer can forget to leave.
//
// The cost of that is real and is handled elsewhere: since closure coincides
// with the final decision, freezing decisions AT closure would make that final
// decision uncorrectable the instant it is written. So decisions freeze on
// consumption instead — when Step 4 reads the run, or when the AuthorReturn is
// materialized. See Run.DecisionsFrozen and migration 0010.

// GateResult is the run's review state plus what it was computed from.
//
// The counts are returned rather than left for the caller to recount, because
// every consumer needs them for its message and three independent recounts is
// three chances to disagree with the verdict they accompany.
type GateResult struct {
	State ReviewState

	Total    int
	Open     int
	Resolved int
	Rejected int

	// RunRejected is a human objecting to the run as a whole rather than to any
	// one question.
	//
	// It exists because the gate could previously only be objected to where the
	// machine had already admitted doubt. A run whose every section resolved
	// cleanly raised no tasks, so it passed immediately and there was no action
	// a reviewer could take against it — which made the review a review of the
	// machine's own list of questions rather than of its answers.
	RunRejected bool

	// RejectedTaskIDs is in run task order, so a returned run's report lists the
	// rejections in document order rather than in whatever order the decisions
	// were written.
	RejectedTaskIDs []string
}

// Gate computes a run's review state from its tasks and their decisions.
//
// decisions is keyed by task id and may be missing entries; a task with no
// decision is open. Passing an empty map is the initial state of every run and
// is not an error.
//
// Note the deliberate ordering: rejection is only reported once EVERY task is
// decided. A run with one rejection and three still open is `open`, not
// `returned`. Returning early would send a manuscript back naming one problem
// while three unexamined questions remained, and the author would then fix one
// thing and receive the rest a round later.
func Gate(run Run, decisions map[string]*ReviewDecision) GateResult {
	return GateWith(run, decisions, false)
}

// GateWith computes the state including a run-level rejection.
//
// Kept as a second function rather than a field on Run because a rejection is
// not part of the segmentation — it is a later judgement about it, loaded
// separately, and threading it through Run would let a caller construct a run
// that carries its own verdict.
func GateWith(run Run, decisions map[string]*ReviewDecision, runRejected bool) GateResult {
	res := GateResult{Total: len(run.Tasks), RunRejected: runRejected}

	for i := range run.Tasks {
		if i >= len(run.TaskIDs) {
			// Identity is assigned by the service layer in parallel with the
			// tasks. A short TaskIDs means the run was assembled wrongly, and
			// the safe reading of a task whose id is unknown is that it is
			// unanswered — a gate that guesses "decided" would let Step 4 run.
			res.Open++
			continue
		}

		id := run.TaskIDs[i]
		d := decisions[id]

		switch {
		case d == nil:
			res.Open++
		case d.Rejected():
			res.Rejected++
			res.RejectedTaskIDs = append(res.RejectedTaskIDs, id)
		default:
			res.Resolved++
		}
	}

	// REJECTION TAKES PRECEDENCE, and this ordering was reversed on purpose.
	//
	// It previously read: open first, so a run with one rejection and three
	// unanswered questions was `open`. The argument was completeness — finish
	// the review and the author gets every problem at once rather than one per
	// round.
	//
	// The argument against is stronger. It produces a state that reads
	// "in progress" for a manuscript already known to be going back, so a
	// consumer checking the gate sees nothing wrong. An ambiguous state that
	// looks benign is worse than an incomplete report.
	//
	// The completeness concern is real and is handled where it belongs: the CLI
	// warns when a rejection leaves questions unanswered. That keeps the
	// information without putting it in the state machine.
	switch {
	case res.RunRejected || res.Rejected > 0:
		res.State = ReviewReturned
	case res.Open > 0:
		res.State = ReviewOpen
	default:
		// Includes Total == 0, which is the machine-only run: no questions were
		// raised, so there is nothing to wait for and the run passes
		// immediately. Its effective view is identical to its machine view.
		//
		// PASSED IS PROVISIONAL. It means currently accepted, not permanently
		// final — a run-level rejection can move it to returned later, which is
		// the only thing that makes a clean run challengeable at all.
		res.State = ReviewPassed
	}

	return res
}

// Passed is the precondition Step 4 must check.
//
// Written as a method on the result rather than left as a comparison at each
// call site, so that adding a state later cannot silently widen what counts as
// permission. A new state is not passed unless this function says so.
func (g GateResult) Passed() bool { return g.State == ReviewPassed }

// Returned reports whether the manuscript goes back to the author.
func (g GateResult) Returned() bool { return g.State == ReviewReturned }

// AuthorReturnItem is one rejection, rendered for the author.
//
// The fields are a SNAPSHOT rather than references. A report is a thing that was
// sent, and it must keep saying what it said even if the underlying decision is
// later corrected or the paper re-segmented under new rules.
type AuthorReturnItem struct {
	ReviewTaskID string
	Reason       ReviewReason

	// HeadingRaw and AncestorHeadings locate the section for the author. The
	// ancestors are outermost-first, matching ReviewContext, because "5.3" alone
	// is not a location and "Discussion → 5.3 Future Directions" is.
	HeadingRaw       string
	AncestorHeadings []string

	// Comment is the reviewer's own words, and is never empty. A rejection with
	// no reason gives the author nothing to act on, which is why both the
	// constructor and the schema refuse one.
	Comment string
}

// BuildAuthorReturn assembles the items for a returned run.
//
// It returns nil when the run is not returned, so a caller cannot accidentally
// materialize a report for a run that passed. That check lives here rather than
// at the call site because there will be more than one call site — a CLI today,
// an HTTP handler later — and a precondition enforced in one of them is not
// enforced.
func BuildAuthorReturn(run Run, decisions map[string]*ReviewDecision) []AuthorReturnItem {
	return BuildAuthorReturnWith(run, decisions, nil)
}

// RunRejection is a human objecting to a run as a whole.
//
// Separate from ReviewDecision because it answers no question: there is no task,
// no assignment and nothing to overlay. Modelling it as a decision with a null
// task would put a foreign key with no target in the one table whose whole
// premise is one authoritative answer per question.
type RunRejection struct {
	Comment    string
	ReviewerID string
}

// BuildAuthorReturnWith assembles the report, including a run-level rejection.
//
// A run rejected at run level with no tasks would otherwise produce an EMPTY
// report — the run is returned, `Gate` agrees, and there are no rejected tasks
// to iterate. The author would receive a manuscript back with nothing said about
// it, which is the exact failure the mandatory-comment rule exists to prevent,
// arriving by a different route.
func BuildAuthorReturnWith(run Run, decisions map[string]*ReviewDecision, rejection *RunRejection) []AuthorReturnItem {
	g := GateWith(run, decisions, rejection != nil)
	if !g.Returned() {
		return nil
	}

	var items []AuthorReturnItem

	// The run-level objection goes FIRST. It concerns the document as a whole
	// and frames whatever follows; a reader who meets it after four heading
	// complaints has already formed the wrong idea of what is wrong.
	if rejection != nil {
		items = append(items, AuthorReturnItem{
			Reason:  ReasonRunRejected,
			Comment: rejection.Comment,
		})
	}

	byID := map[string]int{}
	for i, id := range run.TaskIDs {
		byID[id] = i
	}

	for _, id := range g.RejectedTaskIDs {
		i, ok := byID[id]
		if !ok || i >= len(run.Tasks) {
			continue
		}
		task := run.Tasks[i]

		item := AuthorReturnItem{
			ReviewTaskID: id,
			Reason:       task.Reason,
			Comment:      decisions[id].Comment,
		}

		// A title_ambiguity task on a document with no H1 has no node, so there
		// is no heading to name. The comment carries the whole message there,
		// which is the case the mandatory-comment rule was written for.
		//
		// ContextFor is reused rather than reimplemented: the author needs the
		// same placement a reviewer was shown, and two walks of the parent chain
		// would be two chances to disagree about where a section sits.
		if task.SectionOrdinal >= 0 {
			if ctx, ok := ContextFor(run.Nodes, task.SectionOrdinal); ok {
				item.HeadingRaw = ctx.Heading
				item.AncestorHeadings = ctx.AncestorHeadings
			}
		}

		items = append(items, item)
	}

	return items
}
