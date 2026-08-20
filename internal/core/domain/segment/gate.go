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
	res := GateResult{Total: len(run.Tasks)}

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

	switch {
	case res.Open > 0:
		res.State = ReviewOpen
	case res.Rejected > 0:
		res.State = ReviewReturned
	default:
		// Includes Total == 0, which is the machine-only run: no questions were
		// raised, so there is nothing to wait for and the run passes
		// immediately. Its effective view is identical to its machine view.
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
	g := Gate(run, decisions)
	if !g.Returned() {
		return nil
	}

	byID := map[string]int{}
	for i, id := range run.TaskIDs {
		byID[id] = i
	}

	items := make([]AuthorReturnItem, 0, len(g.RejectedTaskIDs))
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
