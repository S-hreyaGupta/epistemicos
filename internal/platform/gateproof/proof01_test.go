package gateproof

import (
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
	"github.com/EpistemicOS/epistemicos/internal/platform/testenv"
)

// TestPROOF01_GateNamesUnsetURL proves PROOF-01: `make gate`, shelled out to
// from inside the suite it governs, in an environment where
// EPISTEMIC_OS_DB_URL IS set for the outer suite, fails and names
// EPISTEMIC_OS_DB_URL when that variable is unset for the nested gate.
//
// D-01: this shells out to `make gate`, not to `env-preflight` or any
// narrower target. SC-1 is worded "the gate fails", and every proof then
// exercises the real ordering (vet, gofmt, build, env-preflight, migrate,
// test), so a future reorder is caught by all three proofs rather than by
// none. The measurement removed the cheap option: `make env-preflight`
// against a closed-port DSN exited 0, because the escalation export is
// target-scoped to `gate` (D-11), so the narrower target would not have
// proven that the gate turns escalation on — it would have proven a weaker
// claim.
func TestPROOF01_GateNamesUnsetURL(t *testing.T) {
	gate.SkipIfNested(t)

	// intact holds the intact-tree result. Task 3's defeated_tree_control
	// subtest reads it from this enclosing scope rather than re-running the
	// intact side (D-16) — subtests inside one *testing.T lineage give
	// guaranteed ordering, so intact_tree always runs before
	// defeated_tree_control.
	var intact gate.RunResult

	t.Run("intact_tree", func(t *testing.T) {
		intact = gate.Make(t, "gate", gate.RunOptions{Unset: []string{testenv.URLEnv}})

		// Vacuity guard first, before any content assertion (the
		// makefile_test.go:44 shape): if the child timed out or exited 0,
		// the unset-URL condition was not reproduced and every assertion
		// below would be vacuous.
		if intact.TimedOut {
			t.Fatalf("make gate timed out instead of failing fast (measured cold worst case: 85s): %+v", intact)
		}
		if intact.ExitCode == 0 {
			t.Fatalf("make gate exited 0 with %s unset — the condition was not reproduced; result=%+v", testenv.URLEnv, intact)
		}

		// The single content assertion: the escalation preamble and the
		// named cause arriving on one line of Combined is GATE-10, and the
		// same-line form is what structurally rules out the lenient-skip
		// false positive — testenv.URLEnv also appears in the Makefile
		// help, in README, and in testenv's own lenient skip message, so a
		// whole-blob strings.Contains of the cause alone would pass on a
		// run that merely skipped.
		if !lineContainsBoth(intact.Combined, testenv.RequireEnv, testenv.URLEnv) {
			t.Fatalf("PROOF-01: no single line of make gate's output contains both %s and %s (GATE-10):\n%s", testenv.RequireEnv, testenv.URLEnv, intact.Combined)
		}
	})

	// defeated_tree_control is PROOF-01's SC-5 differential control (D-11,
	// D-13). It proves the intact side's assertion is non-vacuous: the
	// proofs assert the gate fails and names its cause; if the defeated
	// tree lacked the escalation preamble that the proofs bind to, the
	// proofs would fail. Proving the premise proves the consequent.
	t.Run("defeated_tree_control", func(t *testing.T) {
		// This is not checking that the proof passed — it is checking that
		// the proof RAN. A control comparing against a result that was
		// never produced is the vacuous-pass shape one indirection along,
		// and this guard exists to make that specific failure loud rather
		// than silent (D-16).
		requireIntact(t, intact)

		root := materializeTree(t)
		stripEscalationExport(t, root)

		// The same invocation and the same Unset as the intact side, with
		// Dir pointing at the defeated copy — the ONLY difference between
		// the two sides is the stripped export. gate.Run rather than
		// gate.Make because the working directory must be the copy, which
		// is what RunOptions.Dir (D-08) exists for. The intact side already
		// ran once above; this adds only the defeated run (D-16).
		defeated := gate.Run(t, []string{"make", "gate"}, gate.RunOptions{
			Dir:   root,
			Unset: []string{testenv.URLEnv},
		})

		// 1. Restate the intact side's positive from the captured result,
		// so both sides of the differential appear together at the
		// comparison.
		if !lineContainsBoth(intact.Combined, testenv.RequireEnv, testenv.URLEnv) {
			t.Fatalf("PROOF-01 control: the captured intact result no longer shows both %s and %s on one line:\n%s", testenv.RequireEnv, testenv.URLEnv, intact.Combined)
		}

		// 2. D-14: the differential binds to the escalation preamble, NOT
		// to the exit code — exit 2 was measured in all six cells of the
		// intact/defeated matrix (with escalation stripped, migrate becomes
		// the reporter and fails anyway), so an exit-code differential
		// could not come back false. The escalation preamble discriminates
		// cleanly in all six cells, and it is built from testenv.RequireEnv,
		// an exported constant this project owns. Do not assert on
		// defeated's exit code as a conjunct — it does no work.
		if strings.Contains(defeated.Combined, testenv.RequireEnv) {
			t.Errorf("PROOF-01 control: the defeated tree (escalation export stripped) still shows the escalation preamble — the differential does not discriminate:\n%s", defeated.Combined)
		}

		// 3. D-15: reporter identity is asserted only where the reporter's
		// text is ours — config's own required-variable message. This names
		// who spoke in the defeated tree; it deliberately does not assert
		// golang-migrate's own wrapper text, which is a foreign-prose
		// coupling PROOF-02's control must refuse.
		if !strings.Contains(defeated.Combined, "DB_URL is required") {
			t.Errorf("PROOF-01 control: the defeated tree's output does not carry config's own required-variable message (\"DB_URL is required\"):\n%s", defeated.Combined)
		}
	})
}
