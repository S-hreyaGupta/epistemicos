// Package gateproof proves PROOF-01, PROOF-02, PROOF-03 and GATE-10: it
// imports github.com/EpistemicOS/epistemicos/internal/platform/gate and
// reaches only that package's exported surface — SkipIfNested, Run, Make,
// RunOptions, RunResult, RepoRoot, DepthEnv, DefaultTimeout. A proof that
// needed an unexported helper from gate would fail to build, and the API
// would be wrong, not the compiler — which is what makes Phase 2's binding
// condition that gate was built as this phase's harness compiler-enforced
// instead of a claim nobody could falsify.
//
// Every test in this package calls gate.SkipIfNested(t) as its first
// statement, so a nested `make gate` invoked from inside the suite `make
// gate` governs declines at depth 1 rather than recursing.
package gateproof

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
)

// unreachableDSN reproduces the unreachable-database condition without
// stopping the compose service. The equivalent constant in
// internal/platform/gate is unexported and this package may not reach it
// (D-03), so it is redeclared here rather than imported. The host token is
// test-supplied, so this couples to nothing this project does not own.
// 127.0.0.1 is used rather than the loopback hostname because this host has
// no IPv6 loopback listener and the hostname resolves there first.
const unreachableDSN = "postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable"

// fixturePathSuffix is the common suffix shared by the fixture's two
// spellings — the on-disk path and the relative literal at the one
// cross-package testenv.Fixture call site
// (internal/adapters/secondary/store/segmentation_test.go:244). The suffix
// is the actual invariant: move the fixture and both spellings change, so an
// assertion against the suffix fails — correctly; change only the call
// site's relative depth and the suffix survives — also correctly, because
// the file did not move.
const fixturePathSuffix = "core/domain/segment/testdata/demo.md"

// lineContainsBoth splits combined on the newline byte, trims a single
// trailing carriage return from each line, and reports whether any one line
// contains both a and b. It exists because a whole-blob strings.Contains of
// the cause alone is weaker than it looks: the cause token also appears in
// the Makefile help, in README, in config's own required-variable error, and
// in testenv's own lenient skip message — so the weak form passes on a run
// that only skipped. A non-zero exit code cannot rescue that weakness
// either, since exit 2 was measured in every cell of the intact/defeated
// matrix. Same-line is what discriminates.
func lineContainsBoth(combined, a, b string) bool {
	for _, line := range strings.Split(combined, "\n") {
		line = strings.TrimSuffix(line, "\r")
		if strings.Contains(line, a) && strings.Contains(line, b) {
			return true
		}
	}
	return false
}

// requireIntact is the shared guard every SC-5 differential control opens
// with. It fails the test when res is the zero value, when res.TimedOut is
// true, or when res.ExitCode is 0.
//
// It is NOT checking that the proof passed — it is checking that the proof
// RAN. A control comparing against a result that was never produced is the
// vacuous-pass shape one indirection along, and this guard exists to make
// that specific failure loud rather than silent.
func requireIntact(t *testing.T, res gate.RunResult) {
	t.Helper()

	if res == (gate.RunResult{}) {
		t.Fatalf("requireIntact: the captured intact-tree result is the zero value — the proof subtest this control depends on never ran")
	}
	if res.TimedOut {
		t.Fatalf("requireIntact: the captured intact-tree result timed out — the proof did not run to completion: %+v", res)
	}
	if res.ExitCode == 0 {
		t.Fatalf("requireIntact: the captured intact-tree result exited 0 — the proof's condition was not reproduced: %+v", res)
	}
}

// TestLineContainsBoth_Control drives lineContainsBoth against synthetic
// inputs, including the case D-18 exists to rule out: the two substrings on
// two adjacent lines. This is Phase 1's preambleInvariant shape — a pure
// decision function exercised against inputs that make it say no — so the
// predicate every proof rests on is demonstrated able to return false before
// any proof relies on it.
func TestLineContainsBoth_Control(t *testing.T) {
	gate.SkipIfNested(t)

	cases := []struct {
		name     string
		combined string
		a, b     string
		want     bool
	}{
		{
			name:     "same line",
			combined: "alpha beta\ngamma",
			a:        "alpha", b: "beta",
			want: true,
		},
		{
			name:     "adjacent lines — the case D-18 exists to rule out",
			combined: "alpha\nbeta",
			a:        "alpha", b: "beta",
			want: false,
		},
		{
			name:     "CRLF — one trailing carriage return is trimmed",
			combined: "alpha beta\r\ngamma",
			a:        "alpha", b: "beta",
			want: true,
		},
		{
			name:     "empty combined",
			combined: "",
			a:        "alpha", b: "beta",
			want: false,
		},
		{
			name:     "same-line, no word boundary — same-line, not adjacency-of-characters",
			combined: "alphabeta",
			a:        "alpha", b: "beta",
			want: true,
		},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			got := lineContainsBoth(tc.combined, tc.a, tc.b)
			if got != tc.want {
				t.Errorf("lineContainsBoth(%q, %q, %q) = %v, want %v", tc.combined, tc.a, tc.b, got, tc.want)
			}
		})
	}
}

// TestGateproof_NoParallelMarker is the mechanical pin for D-04: three
// proofs each shelling out to a full `make gate` against one shared compose
// database, made safe by a default nobody stated, is Phase 2's carried
// warning 3 with more at stake, and adding the marker later is a one-line
// change with no visible consequence until CI goes flaky. The searched token
// is assembled from parts at run time, not written as one literal, so this
// guard's own source does not trip the pattern it searches for.
func TestGateproof_NoParallelMarker(t *testing.T) {
	gate.SkipIfNested(t)

	dir := filepath.Join(gate.RepoRoot(t), "internal", "platform", "gateproof")
	entries, err := os.ReadDir(dir)
	if err != nil {
		t.Fatalf("TestGateproof_NoParallelMarker: reading %s: %v", dir, err)
	}

	dot := "."
	method := "Parallel"
	openParen := "("
	token := dot + method + openParen

	for _, entry := range entries {
		name := entry.Name()
		if entry.IsDir() || !strings.HasSuffix(name, "_test.go") {
			continue
		}
		path := filepath.Join(dir, name)
		data, err := os.ReadFile(path)
		if err != nil {
			t.Fatalf("TestGateproof_NoParallelMarker: reading %s: %v", path, err)
		}
		for i, line := range strings.Split(string(data), "\n") {
			if strings.Contains(line, token) {
				t.Errorf("%s:%d: found the Go parallel-test marker — no test in this package may run in parallel (D-04)", path, i+1)
			}
		}
	}
}
