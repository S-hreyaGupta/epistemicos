package gateproof

import (
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
}
