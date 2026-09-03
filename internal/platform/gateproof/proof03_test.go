package gateproof

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
	"github.com/EpistemicOS/epistemicos/internal/platform/testenv"
)

// breakFixture replaces
// <root>/internal/core/domain/segment/testdata/demo.md with a directory of
// the same name, inside a materializeTree copy. It fails unless a regular
// file was present there beforehand, so a defeat that silently no-ops
// because the path moved cannot make PROOF-03 pass against an intact tree —
// the vacuous-pass shape this phase exists to remove.
//
// D-09: the fixture is replaced by a DIRECTORY, not deleted. os.ReadFile on
// a directory fails on both Windows and Linux — a genuine READ FAILURE,
// which is what GATE-03 and PROOF-03 actually say. Deleting would prove the
// ABSENT case instead, and absence is not unreadability — letting an
// adjacent proof stand in for the stated one is the habit this milestone
// keeps breaking. "Both, as two subtests" was rejected: it buys something
// the requirement does not ask for, at roughly 18-21s per extra nested
// gate, and the absence case is a cheap addition later if it is ever
// wanted.
func breakFixture(t *testing.T, root string) {
	t.Helper()

	if root == gate.RepoRoot(t) {
		t.Fatalf("breakFixture: refusing to break the fixture in the real repository root — this must operate on a materializeTree copy only")
	}

	path := filepath.Join(root, "internal", "core", "domain", "segment", "testdata", "demo.md")

	info, err := os.Stat(path)
	if err != nil {
		t.Fatalf("breakFixture: stat %s: %v — expected a regular file here before defeating it", path, err)
	}
	if !info.Mode().IsRegular() {
		t.Fatalf("breakFixture: %s is not a regular file (mode %v) — the defeat would silently no-op against an already-broken fixture", path, info.Mode())
	}

	if err := os.Remove(path); err != nil {
		t.Fatalf("breakFixture: os.Remove %s: %v", path, err)
	}
	if err := os.Mkdir(path, 0o755); err != nil {
		t.Fatalf("breakFixture: os.Mkdir %s: %v", path, err)
	}
}

// TestPROOF03_GateNamesUnreadableFixture proves PROOF-03 and GATE-10: `make
// gate`, shelled out to from inside the suite it governs, fails and names
// the fixture path on one line of Combined when
// internal/core/domain/segment/testdata/demo.md is unreadable.
//
// D-01: this shells out to `make gate`, not to any narrower target — SC-3 is
// worded "the gate fails", and every proof exercises the real ordering (vet,
// gofmt, build, env-preflight, migrate, test), so a future reorder is caught
// by all three proofs rather than by none.
func TestPROOF03_GateNamesUnreadableFixture(t *testing.T) {
	gate.SkipIfNested(t)

	// intact holds the intact-tree result. defeated_tree_control (Task 2)
	// reads it from this enclosing scope rather than re-running the intact
	// side (D-16) — subtests inside one *testing.T lineage give guaranteed
	// ordering, so intact_tree always runs before defeated_tree_control.
	var intact gate.RunResult

	t.Run("intact_tree", func(t *testing.T) {
		// PROOF-03 is the one proof whose intact side is itself a copy —
		// the condition it names cannot be reproduced in the real tree
		// without mutating it. D-07's measurement is why: segment ran
		// 3.34s-5.28s while gate ran 4.46s-25.70s, so they overlap, and
		// mutating the real demo.md would corrupt a file another package
		// is concurrently reading, landing the failure somewhere unrelated
		// to PROOF-03. A defer restore would not have rescued it either —
		// a defer does not survive the timeout kill DefaultTimeout exists
		// for. "Intact" here means the ESCALATION MECHANISM is intact,
		// which is the axis the SC-5 differential (Task 2) varies; the
		// fixture itself is broken on both sides of this test.
		root := materializeTree(t)
		breakFixture(t, root)

		// This condition requires the database to be fine, so that Pool
		// returns and Fixture is the branch that speaks — no Env/Unset for
		// the database here, the ambient compose DSN reaches the child.
		// testenv.Fixture's own doc comment records that Fixture runs only
		// after Pool has already returned, which is what makes the fixture
		// condition observable rather than masked by a database condition.
		//
		// Unset does carry testenv.RequireEnv (deviation from this
		// package's literal action text, carried forward from 03-01's
		// Task 3 finding and 03-02's identical carry-forward, applied
		// identically here): when this test itself runs under a real
		// depth-0 `make gate`, that outer gate's own target-scoped export
		// (gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate) lands
		// in this process's ambient environment, and buildChildEnv would
		// otherwise pass it straight through to the nested child. Harmless
		// here — D-11 measured this copy's own gate: target-scoped export
		// to override a conflicting caller-set value regardless — but
		// unsetting it makes this side control exactly the environment the
		// assertion is about, rather than depending on ambient state, and
		// matches the defeated side below where it is load-bearing.
		intact = gate.Run(t, []string{"make", "gate"}, gate.RunOptions{
			Dir:   root,
			Unset: []string{testenv.RequireEnv},
		})

		// Vacuity guard first, before any content assertion (the
		// makefile_test.go:44 shape): if the child timed out or exited 0,
		// the unreadable-fixture condition was not reproduced and every
		// assertion below would be vacuous.
		if intact.TimedOut {
			t.Fatalf("make gate timed out instead of failing fast (measured cold worst case: 85s): %+v", intact)
		}
		if intact.ExitCode == 0 {
			t.Fatalf("make gate exited 0 with the fixture replaced by a directory — the unreadable-fixture condition was not reproduced; result=%+v", intact)
		}

		// The single content assertion: the escalation preamble and the
		// fixture path arriving on one line of Combined is GATE-10.
		//
		// D-17: the path has two spellings — the on-disk path
		// internal/core/domain/segment/testdata/demo.md, and the relative
		// literal at the call site (segmentation_test.go:244), which
		// climbs three directories up from
		// internal/adapters/secondary/store before rejoining the same
		// suffix. The common suffix fixturePathSuffix is the actual
		// invariant: move the fixture and both spellings change, so this
		// assertion fails — correctly, the requirement's subject moved.
		// Change only the call site's relative depth and the suffix
		// survives — also correctly, because the file did not move.
		//
		// D-09's measured known consequence is why the preamble must be
		// part of this assertion rather than "the gate merely failed":
		// replacing demo.md also breaks more than the one testenv.Fixture
		// call site — segment's own hash-pinned direct reads in
		// fixture_test.go fail hard regardless of escalation. So "the gate
		// failed" alone is not evidence that the fixture condition, and
		// not that co-failure, was the reporter. The preamble is what
		// shows testenv spoke.
		//
		// No assertion here binds to the operating system's own errno
		// text for reading a directory as a file — that text differs
		// between Windows and Linux, and binding to it would make the
		// proof pass on one platform and fail on the other for a reason
		// unrelated to the requirement. The assertion binds to the path.
		if !lineContainsBoth(intact.Combined, testenv.RequireEnv, fixturePathSuffix) {
			t.Fatalf("PROOF-03: no single line of make gate's output contains both %s and %s (GATE-10):\n%s", testenv.RequireEnv, fixturePathSuffix, intact.Combined)
		}
	})
}
