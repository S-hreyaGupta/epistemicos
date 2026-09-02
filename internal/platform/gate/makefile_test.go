package gate

import (
	"strings"
	"testing"
)

// closedPortDSN is a PostgreSQL connection string pointing at a closed
// local port — no service has to be stopped to reproduce the
// unreachable-database condition, and nothing here disturbs the compose
// postgres service the rest of this suite (and 02-04) depends on.
const closedPortDSN = "postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable"

// composeDSN is the compose postgres service's connection string, bound to
// 127.0.0.1 rather than localhost — this host has no listener on ::1, which
// is what "localhost" resolves to first (D-11's carried-forward finding).
const composeDSN = "postgres://epistemicos:epistemicos@127.0.0.1:5432/epistemicos?sslmode=disable"

// TestEnvPreflightIsVoiceless asserts D-03: on the unreachable-database
// path, `make env-preflight` contributes no line of its own to either
// stream — every line testenv prints is the only voice a developer sees.
//
// This is a differential subprocess comparison, not a check of the
// Makefile's text, because D-07 rejected the text check on a
// non-uniform-weakness argument: the constraint is about output, and the
// likely decay is a tool inside the step starting to print, which a text
// assertion cannot see. So this test runs the real Make target and the real
// bare command it wraps, and reports any line present in the first and
// absent from the second — extraLines, proven able to report a violation by
// TestExtraLines_Control_DetectsAnAddedLine before this test relies on it.
func TestEnvPreflightIsVoiceless(t *testing.T) {
	SkipIfNested(t)

	env := []string{
		"EPISTEMIC_OS_DB_URL=" + closedPortDSN,
		"EPISTEMIC_OS_TEST_REQUIRE_ENV=TestEnvPreflightIsVoiceless",
	}
	unset := []string{"EPISTEMIC_OS_TEST_REQUIRE_DB"}

	makeSide := Make(t, "env-preflight", RunOptions{Silent: true, Env: env, Unset: unset})
	directSide := Run(t, []string{"go", "test", "./internal/platform/testenv/", "-count=1"}, RunOptions{Env: env, Unset: unset})

	// If the Make side passed, the unreachable-database condition was not
	// reproduced and every assertion below would be vacuous.
	if makeSide.ExitCode == 0 {
		t.Fatalf("make env-preflight exited 0 against a closed port — the unreachable-database condition was not reproduced; result=%+v", makeSide)
	}
	if makeSide.TimedOut {
		t.Fatalf("make env-preflight timed out instead of failing fast: %+v", makeSide)
	}

	if !strings.Contains(makeSide.Combined, "127.0.0.1:1") {
		t.Errorf("make env-preflight output does not name the unreachable host 127.0.0.1:1:\n%s", makeSide.Combined)
	}
	if !strings.Contains(makeSide.Combined, "EPISTEMIC_OS_TEST_REQUIRE_ENV") {
		t.Errorf("make env-preflight output does not carry testenv's escalation preamble (EPISTEMIC_OS_TEST_REQUIRE_ENV):\n%s", makeSide.Combined)
	}

	if extra := extraLines(makeSide.Stdout, directSide.Stdout); len(extra) != 0 {
		t.Errorf("make env-preflight's stdout said more than the direct go test command:\nextra lines: %v\nmake stdout:\n%s\ndirect stdout:\n%s", extra, makeSide.Stdout, directSide.Stdout)
	}
	if extra := extraLines(makeSide.Stderr, directSide.Stderr); len(extra) != 0 {
		t.Errorf("make env-preflight's stderr said more than the direct go test command:\nextra lines: %v\nmake stderr:\n%s\ndirect stderr:\n%s", extra, makeSide.Stderr, directSide.Stderr)
	}
}

// TestMakeTestPrintsLenientBanner asserts D-05: `make test` prints the
// lenient-run banner, so a tool inside that step starting to print — or the
// banner being quietly dropped in a Makefile tidy-up — is visible to an
// assertion rather than to nobody. A banner nobody checks is a claim that
// cannot come back false.
//
// This test invokes `make test`, which invokes `go test ./...`, which runs
// this package — the recursion path this package's doc comment names. The
// SkipIfNested call above is what terminates that loop at depth 1, and
// DefaultTimeout is what bounds it if something else goes wrong; this is
// the one call site in this plan where the loop is real, not hypothetical.
func TestMakeTestPrintsLenientBanner(t *testing.T) {
	SkipIfNested(t)

	result := Make(t, "test", RunOptions{
		Env:   []string{"EPISTEMIC_OS_DB_URL=" + composeDSN},
		Unset: []string{"EPISTEMIC_OS_TEST_REQUIRE_ENV", "EPISTEMIC_OS_TEST_REQUIRE_DB"},
	})

	// Two distinct clauses, asserted separately, so a half-deleted banner —
	// one clause dropped but not the other — is still caught.
	if !strings.Contains(result.Combined, "make test is the lenient run") {
		t.Errorf("make test's output does not carry the lenient-run clause of the banner:\n%s", result.Combined)
	}
	if !strings.Contains(result.Combined, "make gate is the run that proves anything") {
		t.Errorf("make test's output does not carry the make-gate clause of the banner:\n%s", result.Combined)
	}
}
