// Package gate is the shell-out-to-`make` harness this phase needs and Phase
// 3 reuses: a test in this package can invoke a Make target as a subprocess,
// capture its stdout and stderr separately, capture its exit code, and
// impose a timeout.
//
// # The recursion hazard
//
// A test that shells out to a Make target, running inside the suite that
// target invokes, recurses:
//
//	make test → go test ./... → internal/platform/gate test → make test → go test ./... → …
//
// Each level costs a full suite run, and nothing in the design shows it
// until it happens — a 30-second test run becomes a hung machine.
// TestMakeTestPrintsLenientBanner (in this package) invokes `make test`
// directly, so this is not a hypothetical: it is the loop above, for real,
// at the one call site where it matters.
//
// The guard is a depth counter. Every child process Run spawns carries
// EPISTEMIC_OS_TEST_MAKE_DEPTH set to the parent's depth plus one, and every
// test in this package calls SkipIfNested(t) as its first statement: at
// depth 0 it runs, at depth ≥ 1 it declines, so the loop terminates at depth
// 1. A malformed marker value is neither treated as depth 0 (which would
// recurse) nor as nested (which would skip silently and pass vacuously) — it
// is a hard failure naming the variable and its value. See nestingDepth.
//
// # Placement constraint
//
// This package must not move under internal/platform/testenv. D-04's
// `env-preflight` Make target runs `go test ./internal/platform/testenv/`
// with no -run filter, so a make-invoking test placed there would be
// invoked by the preflight itself — a second, shorter recursion path that
// the depth marker's `make test` story above does not describe. Keeping the
// harness in its own package (internal/platform/gate) means env-preflight
// never reaches it at all.
package gate

import (
	"bytes"
	"context"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"testing"
	"time"
)

// The three fixed patterns extraLines and normalizeElapsed compare against:
// a per-test parenthesised elapsed such as "(0.01s)", a trailing
// tab-separated package elapsed such as "\t2.517s", and Make's own
// diagnostic voice ("make: ***" or "make[1]: ***"), which is never the
// recipe's own output and must be dropped before comparing.
var (
	perTestElapsedRe = regexp.MustCompile(`\([0-9]+\.[0-9]+s\)`)
	packageElapsedRe = regexp.MustCompile(`\t[0-9]+\.[0-9]+s`)
	makeDiagnosticRe = regexp.MustCompile(`^make(\[[0-9]+\])?: `)
)

// DepthEnv names the environment variable carrying the current recursion
// depth. Empty or absent means depth 0.
const DepthEnv = "EPISTEMIC_OS_TEST_MAKE_DEPTH"

// DefaultTimeout bounds every subprocess Run spawns unless RunOptions.Timeout
// overrides it. It sits below go test's 10-minute per-package default so a
// hung child is reported as a hung child rather than surfacing as a hung
// parent. [PROOF-03] Measured cold (fresh GOCACHE, no warm parent build): the
// worst observed child, PROOF-01's shape, took 85s — a margin of 2.8x, not
// the 6x a warm-cache measurement would suggest. Calibrate future changes
// against the cold case, not the warm one: on a cold CI runner the parent
// pays ~141s doing vet and build, and the children inherit that cache,
// running 11s / 9s / 21s — barely worse than warm.
//
// The [PROOF-03] tag's value is not getting this file into the close
// sweep's derived artifact set — measured, it is already in today via its
// "Phase 3" prose. Its value is keeping it in when someone rewords that
// prose. A durability property, not a coverage one.
const DefaultTimeout = 4 * time.Minute

// runWaitDelay bounds how long Run's cmd.Wait() blocks for I/O after the
// child process exits or ctx is canceled. exec.CommandContext's default
// cancellation (cmd.Process.Kill()) only reaches the direct child; on
// Windows a `make` -> `go test` -> test-binary chain hands its stdout/stderr
// pipe write ends down to grandchildren, so killing `make` alone can leave
// those handles open in a still-running grandchild. Without WaitDelay,
// cmd.Run() (which calls Wait() internally) then blocks forever waiting for
// the pipe copier goroutines to see EOF, and the ctx.Err() ==
// DeadlineExceeded / TimedOut branch below is never reached even though the
// context has already expired — see 03-INCIDENT-02.
//
// 5s is deliberately short relative to DefaultTimeout (4m): WaitDelay's job
// is only to bound the tail after the context is already done, not to give
// a well-behaved child extra running time. A normally-exiting child's
// copier goroutines see EOF within milliseconds of the process exiting, so
// 5s is pure margin for the ordinary case and a hard stop for the wedged
// one.
const runWaitDelay = 5 * time.Second

// nestingDepth parses raw — the value of DepthEnv — into a recursion depth.
// The empty string is depth 0. A non-negative integer is that depth.
// Everything else is a hard failure: treating a malformed value as depth 0
// would let the recursion this package exists to bound continue unchecked,
// and treating it as "nested" would skip every test in this package
// silently, which is exactly the vacuous pass this milestone exists to
// remove, reintroduced inside its own guard. Neither convenient answer is
// right, so nestingDepth chooses neither.
func nestingDepth(raw string) (int, error) {
	if raw == "" {
		return 0, nil
	}
	n, err := strconv.Atoi(raw)
	if err != nil || n < 0 {
		return 0, errors.New(DepthEnv + " is set to an unparseable or negative value " + strconv.Quote(raw) + " — refusing to guess whether this is depth 0 or a nested run")
	}
	return n, nil
}

// SkipIfNested must be the first statement of every test in this package
// that spawns a subprocess. It reads DepthEnv, fails the test if the value
// is malformed, returns without effect at depth 0, and skips at depth ≥ 1 —
// the outer run at depth 0 already owns the assertion.
func SkipIfNested(t *testing.T) {
	t.Helper()

	depth, err := nestingDepth(os.Getenv(DepthEnv))
	if err != nil {
		t.Fatal(err)
	}
	if depth > 0 {
		t.Skipf("nested Make invocation at depth %d (%s=%q): the outer run owns this assertion", depth, DepthEnv, os.Getenv(DepthEnv))
	}
}

// RepoRoot returns the directory containing go.mod, walking up from the
// current working directory. It fails the test rather than returning an
// empty string if no such directory is found.
func RepoRoot(t *testing.T) string {
	t.Helper()

	dir, err := os.Getwd()
	if err != nil {
		t.Fatalf("gate.RepoRoot: os.Getwd: %v", err)
	}

	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			t.Fatalf("gate.RepoRoot: no go.mod found walking up from %s", dir)
		}
		dir = parent
	}
}

// RunOptions configures a single subprocess invocation.
type RunOptions struct {
	// Env holds KEY=VALUE entries layered onto the child's environment, on
	// top of the parent's os.Environ().
	Env []string
	// Unset names variables removed from the child's environment before Env
	// is applied.
	Unset []string
	// Timeout bounds the child process. Zero means DefaultTimeout.
	Timeout time.Duration
	// Silent adds -s on the Make path (see Make).
	Silent bool
	// Dir overrides the subprocess's working directory. Empty means
	// RepoRoot(t) — the historical default every existing caller relies on.
	Dir string
}

// RunResult is the observed outcome of a single subprocess invocation.
type RunResult struct {
	Stdout string
	Stderr string
	// Combined is Stdout + Stderr, not a third capture — a caller that
	// assumes interleaved ordering between the two streams would be wrong.
	Combined string
	ExitCode int
	TimedOut bool
}

// Run executes argv in the repository root with a child environment derived
// from the current process's environment: every name in opts.Unset is
// removed, every entry in opts.Env is applied on top, and DepthEnv is set to
// the current depth plus one so a child that itself shells out to Make
// inherits a depth this package's own guard will see.
//
// Run does not t.Fatal on a non-zero exit code — a non-zero exit is the
// expected outcome for most callers here and for all three of Phase 3's
// PROOF-01/02/03. It does t.Fatal if the child could not be started at all
// (a non-*exec.ExitError error), since that is a broken environment, not a
// test outcome.
func Run(t *testing.T, argv []string, opts RunOptions) RunResult {
	t.Helper()

	timeout := opts.Timeout
	if timeout == 0 {
		timeout = DefaultTimeout
	}

	currentDepth, err := nestingDepth(os.Getenv(DepthEnv))
	if err != nil {
		t.Fatal(err)
	}

	env := buildChildEnv(os.Environ(), opts.Unset, opts.Env, currentDepth+1)

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	dir := opts.Dir
	if dir == "" {
		dir = RepoRoot(t)
	}

	cmd := exec.CommandContext(ctx, argv[0], argv[1:]...)
	cmd.Dir = dir
	cmd.Env = env
	cmd.WaitDelay = runWaitDelay

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	runErr := cmd.Run()

	// With WaitDelay set, a timed-out run can return with PARTIAL captured
	// output: Wait forcibly closes the pipes once runWaitDelay elapses, so
	// whatever the copier goroutines had already read is preserved here,
	// but bytes a wedged grandchild wrote after that point are lost. This
	// is intentional — Stdout/Stderr/Combined below always report exactly
	// what was captured, timeout or not, so a proof's vacuity guard still
	// sees the escalation preamble whenever the timed-out child managed to
	// write it before the delay expired.
	result := RunResult{
		Stdout:   stdout.String(),
		Stderr:   stderr.String(),
		Combined: stdout.String() + stderr.String(),
	}

	if ctx.Err() == context.DeadlineExceeded {
		result.TimedOut = true
		result.ExitCode = -1
		return result
	}

	// WaitDelay (runWaitDelay, above) can force cmd.Wait() to return
	// exec.ErrWaitDelay even when ctx never expires: per the stdlib's own
	// doc comment on Cmd.WaitDelay, "If pipes are closed due to WaitDelay,
	// no Cancel call has occurred, and the command has otherwise exited
	// with a successful status, Wait and similar methods will return
	// ErrWaitDelay instead of nil." That happens whenever the direct child
	// exits (successfully or not) while a descendant it spawned and never
	// waited for is still holding the inherited stdout/stderr pipe open —
	// ctx.Err() stays nil in that case, so the branch above is skipped, and
	// without this branch runErr would fall through to the t.Fatalf below
	// as if the process "could not be started," which is false: it
	// started, ran, and (per WaitDelay's own doc wording) may have exited
	// 0. This gap was found by this phase's own code review (03-REVIEW.md
	// WR-01) and is a defect the WaitDelay fix itself introduced, not one
	// it exposed — see 03-INCIDENT-02-harness-timeout-defects.md's WR-01
	// addendum. Classified as TimedOut, matching the ctx.Err() branch
	// above: both describe "gate.Run's own bound was what ended this call,"
	// not the child's own outcome.
	if errors.Is(runErr, exec.ErrWaitDelay) {
		result.TimedOut = true
		result.ExitCode = -1
		return result
	}

	if runErr == nil {
		result.ExitCode = 0
		return result
	}

	var exitErr *exec.ExitError
	if errors.As(runErr, &exitErr) {
		result.ExitCode = exitErr.ExitCode()
		return result
	}

	t.Fatalf("gate.Run: %v %v could not be started: %v", argv[0], argv[1:], runErr)
	return RunResult{}
}

// buildChildEnv derives a child environment from base by removing every name
// in unset, applying every entry in overlay, and setting DepthEnv to the
// given depth. DepthEnv is set last, after unset and overlay are applied, so
// a caller cannot defeat the recursion guard by naming DepthEnv in either.
func buildChildEnv(base, unset, overlay []string, depth int) []string {
	unsetSet := make(map[string]bool, len(unset))
	for _, name := range unset {
		unsetSet[name] = true
	}

	overlayKeys := make(map[string]bool, len(overlay))
	for _, kv := range overlay {
		if k, _, ok := strings.Cut(kv, "="); ok {
			overlayKeys[k] = true
		}
	}

	env := make([]string, 0, len(base)+len(overlay)+1)
	for _, kv := range base {
		k, _, ok := strings.Cut(kv, "=")
		if !ok {
			continue
		}
		if unsetSet[k] || overlayKeys[k] || k == DepthEnv {
			continue
		}
		env = append(env, kv)
	}

	env = append(env, overlay...)
	env = append(env, DepthEnv+"="+strconv.Itoa(depth))

	return env
}

// Make runs `make target` (or `make -s target` when opts.Silent) in the
// repository root; it is Run with argv built for the Make CLI.
func Make(t *testing.T, target string, opts RunOptions) RunResult {
	t.Helper()

	argv := []string{"make"}
	if opts.Silent {
		argv = append(argv, "-s")
	}
	argv = append(argv, target)

	return Run(t, argv, opts)
}

// normalizeElapsed rewrites the two elapsed-time shapes go test emits —
// a parenthesised per-test elapsed such as "(0.01s)", and a tab-separated
// trailing package elapsed such as "\t2.517s" — to a fixed placeholder, so
// two runs of the same command compare equal modulo timing. Every other
// character is left untouched.
func normalizeElapsed(s string) string {
	s = perTestElapsedRe.ReplaceAllString(s, "(ELAPSED)")
	s = packageElapsedRe.ReplaceAllString(s, "\tELAPSED")
	return s
}

// extraLines splits got and want on newlines, normalizes each line with
// normalizeElapsed, drops lines from got matching Make's own diagnostic
// prefix ("make:" or "make[N]:" — Make's voice, not the recipe's), and
// returns the lines of got not accounted for by want, compared as
// multisets so a line printed twice is reported once as extra. An empty
// result means got said nothing want did not.
func extraLines(got, want string) []string {
	wantCounts := lineCounts(splitLines(want))

	gotLines := splitLines(got)
	gotCounts := make(map[string]int, len(gotLines))

	var extra []string
	for _, line := range gotLines {
		if makeDiagnosticRe.MatchString(line) {
			continue
		}
		gotCounts[line]++
		if gotCounts[line] > wantCounts[line] {
			extra = append(extra, line)
		}
	}
	return extra
}

func splitLines(s string) []string {
	var out []string
	for _, line := range strings.Split(s, "\n") {
		out = append(out, normalizeElapsed(line))
	}
	return out
}

func lineCounts(lines []string) map[string]int {
	counts := make(map[string]int, len(lines))
	for _, l := range lines {
		counts[l]++
	}
	return counts
}
