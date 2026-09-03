package gateproof

import (
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
	"github.com/EpistemicOS/epistemicos/internal/platform/testenv"
)

// TestPROOF02_GateNamesUnreachableHost proves PROOF-02: `make gate`, shelled
// out to from inside the suite it governs, in an environment where
// EPISTEMIC_OS_DB_URL IS set for the outer suite, fails and names the
// unreachable host when that variable is set but unreachable for the nested
// gate.
//
// D-01: this shells out to `make gate`, not to `env-preflight` or any
// narrower target. SC-2 is worded "the gate fails", and every proof then
// exercises the real ordering (vet, gofmt, build, env-preflight, migrate,
// test), so a future reorder is caught by all three proofs rather than by
// none. Measured (warm cache, live compose Postgres): `make gate` against a
// closed-port DSN exited 2 in 6.4s, while `make env-preflight` against the
// same DSN exited 0 in 5.6s, because the escalation export is target-scoped
// to `gate` (D-11). The cheaper target did not prove the same claim more
// cheaply; it proved a weaker one — a proof calling it would have had to set
// the flag itself, and would then no longer prove that the gate turns
// escalation on.
func TestPROOF02_GateNamesUnreachableHost(t *testing.T) {
	gate.SkipIfNested(t)

	// intact holds the intact-tree result. The defeated_tree_control subtest
	// (Task 2) reads it from this enclosing scope rather than re-running the
	// intact side (D-16) — subtests inside one *testing.T lineage give
	// guaranteed ordering, so intact_tree always runs before
	// defeated_tree_control.
	var intact gate.RunResult

	t.Run("intact_tree", func(t *testing.T) {
		// Env, not Unset: the condition PROOF-02 names is a database that IS
		// set but unreachable, so unreachableDSN is layered on top via Env.
		// Unsetting testenv.URLEnv here would reproduce PROOF-01's condition
		// instead.
		//
		// Unset also carries testenv.RequireEnv (deviation from this
		// package's literal, carried forward from 03-01's Task 3 finding,
		// applied identically here): the outer gate's own target-scoped
		// export (gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate)
		// lands in this test process's ambient environment when it is itself
		// run under a real depth-0 `make gate`, and buildChildEnv would
		// otherwise pass that straight through to the nested child.
		// Harmless here — D-11 measured this copy's own `gate:` target-scoped
		// export to override a conflicting caller-set value regardless — but
		// unsetting it makes this side control exactly the environment the
		// assertion is about, rather than depending on ambient state, and
		// matches the defeated side (Task 2) where it is load-bearing.
		intact = gate.Make(t, "gate", gate.RunOptions{
			Env:   []string{testenv.URLEnv + "=" + unreachableDSN},
			Unset: []string{testenv.RequireEnv},
		})

		// Vacuity guard first, before any content assertion (the
		// makefile_test.go:44 shape): if the child timed out or exited 0,
		// the unreachable-database condition was not reproduced and every
		// assertion below would be vacuous.
		if intact.TimedOut {
			t.Fatalf("make gate timed out instead of failing fast (measured cold worst case: 85s): %+v", intact)
		}
		if intact.ExitCode == 0 {
			t.Fatalf("make gate exited 0 against a closed-port DSN — the unreachable-database condition was not reproduced; result=%+v", intact)
		}

		// The single content assertion: the escalation preamble and the
		// unreachable host arriving on one line of Combined is GATE-10.
		// D-17: the host is the value this test itself supplied
		// (127.0.0.1:1), so this couples to nothing — not to testenv's
		// prose, which testenv could reword, and not to pgx's dial
		// diagnosis, which pgx could reword. D-18: a whole-blob
		// strings.Contains of the host alone would pass on a run that merely
		// skipped, since the same token appears in testenv's own lenient
		// skip message; a non-zero exit code adds nothing as a conjunct
		// either, since exit 2 was measured in all six cells of the
		// intact/defeated matrix.
		if !lineContainsBoth(intact.Combined, testenv.RequireEnv, "127.0.0.1:1") {
			t.Fatalf("PROOF-02: no single line of make gate's output contains both %s and the unreachable host 127.0.0.1:1 (GATE-10):\n%s", testenv.RequireEnv, intact.Combined)
		}

		// D-02b: the effect half of D-03's ordering claim, obtained from a
		// nested gate that was going to run anyway, at zero extra cost —
		// testenv.RequireEnv appearing in Combined at all means testenv, not
		// store.RunMigrations, was the first voice on this path. The
		// structural half is TestGateOrdersPreflightBeforeMigrate
		// (ordering_test.go, Task 3), and the two are deliberately
		// independent: each has a single reason to fail, so a reword of one
		// does not silently take both, and if either is ever deleted the
		// claim quietly drops to one leg with nothing at the deletion site
		// saying so.
		if !strings.Contains(intact.Combined, testenv.RequireEnv) {
			t.Fatalf("PROOF-02 (D-02b): make gate's output does not carry testenv.RequireEnv at all — testenv was not a voice on the unreachable-database path:\n%s", intact.Combined)
		}
	})

	// defeated_tree_control is PROOF-02's SC-5 differential control (D-11,
	// D-13). It proves the intact side's assertion is non-vacuous: the
	// proofs assert the gate fails and names its cause; if the defeated tree
	// lacked the escalation preamble that the proofs bind to, the proofs
	// would fail. Proving the premise proves the consequent.
	t.Run("defeated_tree_control", func(t *testing.T) {
		// Not checking that the proof passed — checking that the proof RAN.
		// A control comparing against a result that was never produced is
		// the vacuous-pass shape one indirection along, and this guard
		// exists to make that specific failure loud rather than silent
		// (D-16).
		requireIntact(t, intact)

		root := materializeTree(t)
		stripEscalationExport(t, root)

		// The same DSN and the same Unset as the intact side, with Dir
		// pointing at the defeated copy — the ONLY difference between the
		// two sides is the stripped export. gate.Run rather than gate.Make
		// because the working directory must be the copy (RunOptions.Dir,
		// D-08). The intact side already ran once above; this adds only the
		// defeated run (D-16).
		//
		// Unsetting testenv.RequireEnv here is load-bearing, not symmetry
		// for its own sake: with the export stripped from this copy's
		// Makefile, nothing in the copy re-declares escalation, so an
		// ambient EPISTEMIC_OS_TEST_REQUIRE_ENV inherited from whatever
		// process is running this test (a real outer `make gate`, in
		// particular) would otherwise leak through and make the defeated
		// tree escalate anyway — defeating the differential for a reason
		// unrelated to the stripped export.
		defeated := gate.Run(t, []string{"make", "gate"}, gate.RunOptions{
			Dir:   root,
			Env:   []string{testenv.URLEnv + "=" + unreachableDSN},
			Unset: []string{testenv.RequireEnv},
		})

		// 1. Restate the intact side's positive from the captured result, so
		// both sides of the differential appear together at the comparison.
		if !lineContainsBoth(intact.Combined, testenv.RequireEnv, "127.0.0.1:1") {
			t.Fatalf("PROOF-02 control: the captured intact result no longer shows both %s and 127.0.0.1:1 on one line:\n%s", testenv.RequireEnv, intact.Combined)
		}

		// 2. D-11: the differential binds to the escalation preamble, NOT to
		// the exit code — exit 2 was measured in all six cells of the
		// intact/defeated matrix. With the export stripped, migrate becomes
		// the reporter and fails anyway (D-03's ordering point, measured
		// from the other side), so an exit-code differential could not come
		// back false. The escalation preamble discriminates cleanly in all
		// six cells, and it is built from testenv.RequireEnv, an exported
		// constant this project owns. Do not assert on defeated's exit code
		// as a conjunct — it does no work.
		if strings.Contains(defeated.Combined, testenv.RequireEnv) {
			t.Errorf("PROOF-02 control: the defeated tree (escalation export stripped) still shows the escalation preamble — the differential does not discriminate:\n%s", defeated.Combined)
		}

		// 3. The third assertion is deliberately absent, and this comment is
		// why (D-15): PROOF-01's control additionally asserts config's own
		// message text in its defeated tree, because config is ours.
		// PROOF-02's own defeated tree reports through golang-migrate's
		// wrapper instead — a phrase this comment does not repeat as an
		// assertion argument, only names in prose — and that text is a
		// dependency's prose. Pinning to it is Phase 2's carried warning 2
		// done on purpose. Naming what a dependency says is a coupling whose
		// breakage would read as a proof defect rather than as the
		// dependency change it actually is. The "who spoke" signal is
		// obtained above, from the escalation preamble alone, without
		// reintroducing a defect already paid for. This comment exists
		// because an absent assertion is invisible, and a later reader
		// adding a reporter-identity assertion here for symmetry with
		// PROOF-01's control would be reintroducing exactly what was
		// removed.
	})
}
