---
phase: 03-automated-proof
reviewed: 2026-09-03T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - internal/platform/gate/harness.go
  - internal/platform/gate/harness_waitdelay_test.go
  - internal/platform/gateproof/gateproof_test.go
  - internal/platform/gateproof/ordering_test.go
  - internal/platform/gateproof/proof01_test.go
  - internal/platform/gateproof/proof02_test.go
  - internal/platform/gateproof/proof03_test.go
  - internal/platform/gateproof/tree_drain_test.go
  - internal/platform/gateproof/tree_test.go
findings:
  critical: 0
  warning: 4
  info: 4
  total: 8
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-09-03T00:00:00Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

This review covers `internal/platform/gate/harness.go` (the shell-out harness) and eight files in `internal/platform/gateproof` that exercise it, with particular attention — at the dispatching agent's request — to two subprocess-lifecycle fixes committed today outside this phase's normal plan/SUMMARY flow: `harness.go`'s `cmd.WaitDelay` addition (meant to bound `gate.Run` when a grandchild process outlives a killed direct child and still holds the inherited stdout/stderr pipe open) and `materializeTree`'s drain-before-`Wait()` reordering in `tree_test.go` (meant to stop `git archive`'s tar-trailer padding from deadlocking `cmd.Wait()`).

To verify these two fixes precisely rather than accept the prose, I read the Go 1.24 `os/exec` stdlib source directly (`Cmd.Start`, `Cmd.Wait`, `watchCtx`, `awaitGoroutines`) to trace exactly when `WaitDelay`'s timer starts, what it protects, and what it does not. Two conclusions came out of that tracing that are not obvious from reading `harness.go`/`tree_test.go` alone:

1. In `harness.go`, `WaitDelay`'s pipe-closing/kill machinery can produce `exec.ErrWaitDelay` as `cmd.Run()`'s returned error in a scenario `Run()`'s classification logic does not account for (WR-01) — this is a real gap in the fix's completeness, not exercised by the current proof tests, but directly relevant to the exact code path the dispatch asked to be scrutinized.
2. In `tree_test.go`/`tree_drain_test.go`, `cmd.WaitDelay` is set on a `Cmd` that uses `StdoutPipe()` with a manual, synchronous drain — a shape under which `WaitDelay`'s pipe-forcing behavior never actually engages (it is gated on an internal `goroutineErr` channel that `StdoutPipe()` never populates). The real protection there comes entirely from the context deadline plus the default `Cancel` (`Process.Kill()`), which would behave identically with `WaitDelay` unset. The code is not wrong, but the comment claiming `WaitDelay` is "what stops … an undrained pipe … from holding Wait open" overstates what this specific line does (WR-02).

No BLOCKER-tier defect was found in the drain-then-`Wait()` ordering itself, in the zip-slip/path-traversal guard in `materializeTree`'s extraction loop (validate-then-act order is correct), or in the primary `WaitDelay`-bounds-a-grandchild-hang proof (`harness_waitdelay_test.go`), which is genuinely load-bearing because `harness.go`'s `Run()` uses `cmd.Stdout = &bytes.Buffer` (the internal-copy-goroutine shape, where `WaitDelay` *does* engage). The remaining findings are quality/robustness issues: an unanchored substring match in the ordering proof, a resource-cleanup gap on error paths in `materializeTree`, and a few informational notes (a look-alike hardcoded credential that is actually an intentionally-unreachable test DSN, an intentionally-orphaned helper subprocess, a narrow context-deadline race, and an implicit `bash` dependency).

## Warnings

### WR-01: `gate.Run` can misclassify a benign `WaitDelay`-forced completion as "could not be started"

**File:** `internal/platform/gate/harness.go:247-266`
**Issue:**
`Run`'s result classification is:
```go
if ctx.Err() == context.DeadlineExceeded {
    result.TimedOut = true
    result.ExitCode = -1
    return result
}
if runErr == nil { ... }
var exitErr *exec.ExitError
if errors.As(runErr, &exitErr) { ... }
t.Fatalf("gate.Run: %v %v could not be started: %v", argv[0], argv[1:], runErr)
```
This only special-cases `ctx.Err() == context.DeadlineExceeded`. But per the stdlib's own documented semantics (`os/exec` `Cmd.WaitDelay` doc; confirmed by reading `exec.go`'s `watchCtx`/`awaitGoroutines`), the `WaitDelay` timer "starts when either the associated Context is done **or a call to Wait observes that the child process has exited**, whichever occurs first" — i.e. `WaitDelay` can fire and force `cmd.Wait()` to return `exec.ErrWaitDelay` even when `ctx` never times out, if the *direct* child exits successfully (`state.Success() == true`, so `Cmd.Wait()`'s own `err` stays `nil` at that point) while a descendant it spawned and never waited for is still holding the inherited stdout/stderr pipe. In that case:
- `ctx.Err()` is `nil` (context never expired) → first branch is skipped.
- `runErr` is `exec.ErrWaitDelay`, not `nil` and not an `*exec.ExitError` → the `errors.As` branch is skipped.
- Execution falls through to `t.Fatalf("... could not be started: %v", runErr)` — an incorrect and misleading diagnosis for a process that started, ran, and even exited 0.

This is directly relevant to the fix under review: `exec.ErrWaitDelay` is a value `Run()` could not previously receive at all (before `cmd.WaitDelay` was set, `cmd.Wait()` would simply hang rather than return this sentinel), so this gap in the classification logic is a side effect of the very change being reviewed, and it contradicts `Run`'s own documented contract ("Run does not t.Fatal on a non-zero exit code … It does t.Fatal if the child could not be started at all"). None of the three current PROOF tests exercise this path (they all drive `make gate` to a non-zero exit), so it will not currently fail CI, but it is a real, reachable gap in exactly the mechanism this phase's incident fix introduced.

**Fix:**
```go
if errors.Is(runErr, exec.ErrWaitDelay) {
    result.TimedOut = true
    result.ExitCode = -1
    return result
}
```
placed alongside (or folded into) the `ctx.Err() == context.DeadlineExceeded` check, before the `errors.As(runErr, &exitErr)` branch. Add a regression test that starts a direct child which exits 0 while a grandchild it never waits for keeps the pipe open without the outer `ctx` timing out, asserting `Run` returns `TimedOut: true` (or a clearly-labeled result) rather than calling `t.Fatal`.

### WR-02: `cmd.WaitDelay` on `materializeTree`'s `git archive` command does not protect against what its comment claims

**File:** `internal/platform/gateproof/tree_test.go:74-79`, `internal/platform/gateproof/tree_drain_test.go:89`
**Issue:**
The comment says:
> "WaitDelay bounds how long Wait blocks for the child after the process exits or ctx is canceled. … WaitDelay is what stops a wedged child (or an undrained pipe, if the drain below is ever removed again) from holding Wait open past the context deadline."

Tracing `os/exec`'s `Cmd.Start`/`watchCtx`/`awaitGoroutines` (Go 1.24 stdlib): the forced-pipe-close behavior `WaitDelay` provides is gated on `c.goroutineErr != nil`, which is populated only when `cmd.Stdout`/`cmd.Stdin`/`cmd.Stderr` are given as a generic `io.Writer`/`io.Reader` (the internal-copy-goroutine shape `harness.go`'s `Run` uses, where the fix genuinely is load-bearing — verified separately, see Summary). `materializeTree` and the helper in `tree_drain_test.go` instead use `cmd.StdoutPipe()` with a manual, synchronous read loop; `StdoutPipe()` never appends to `c.goroutine`, so `c.goroutineErr` stays `nil` for the whole lifetime of this `Cmd`, and the entire `if c.goroutineErr != nil { … closeDescriptors(c.parentIOPipes) … }` block in `watchCtx` (the code that would force-close the pipe) is skipped unconditionally. `awaitGoroutines` likewise returns immediately (`if c.goroutineErr == nil { return nil }`) regardless of whether a timer was handed to it.

What actually unblocks a wedged `git archive`/helper process here is `ctx`'s own deadline plus the *default* `Cancel` function `exec.CommandContext` installs (`cmd.Process.Kill()`), which fires as soon as `ctx.Done()` — independent of `WaitDelay` being set at all. Setting `WaitDelay` to a nonzero value changes nothing observable for this exact usage shape: the same protection (and the same 30s/5s upper bound) would exist with `cmd.WaitDelay` left at its zero value. This is not a live bug — nothing hangs, nothing behaves incorrectly — but the comment materially overstates what this line does, and a future reader relying on it (e.g. porting this pattern to a call site where a grandchild genuinely does inherit the `StdoutPipe`'s write end, such as if `git` ever forked a helper that inherited fd 1) would wrongly believe `WaitDelay` already covers that case.

**Fix:** Either drop the `WaitDelay` field here (it is dead configuration for this code shape) or correct the comment to state plainly that protection against a wedged `git archive` comes from `ctx`'s deadline plus the default `Kill`-on-cancel, not from `WaitDelay`'s pipe-closing path, and that `WaitDelay` would need `cmd.Stdout` to be a plain `io.Writer` (not `StdoutPipe()`) to actually engage that mechanism.

### WR-03: `TestGateOrdersPreflightBeforeMigrate`'s substring match for "migrate" is unanchored

**File:** `internal/platform/gateproof/ordering_test.go:63-69`
**Issue:**
```go
if preflightIndex == -1 && strings.Contains(line, "env-preflight") {
    preflightIndex = i
}
if migrateIndex == -1 && strings.Contains(line, "migrate") {
    migrateIndex = i
}
```
`preflightIndex`/`migrateIndex` are set to the *first* line in `make -n gate`'s dry-run expansion containing these substrings. `"migrate"` in particular is a common word that other target names, comment text, or variable names introduced later (e.g. a future `migrate-status`, `migrate-down`, or `unmigrated-*` target invoked earlier in the recipe, or a `$(MIGRATE_BIN)` reference) could contain, silently shifting `migrateIndex` to an unrelated, earlier line and either producing a false failure (a correctly-ordered gate now fails this test) or, worse, a false pass (if the coincidental earlier "migrate" match happens to still sort after the real `env-preflight` line). Because `make -n`'s expansion is largely under this project's own control today the risk is currently low, but the check does not verify it is matching the actual `migrate` *target invocation* line as opposed to any line merely containing the substring.

**Fix:** Anchor the match to the actual invocation shape, e.g. require the line to look like a `$(MAKE) …` or direct recipe invocation of the named target:
```go
migrateInvocationRe := regexp.MustCompile(`(^|\s)migrate(\s|$)`)
```
or, more robustly, assert on the specific recipe command line captured in a fixture once and treat any deviation as a hard failure (consistent with this package's general "hard failure over silent divergence" convention used elsewhere, e.g. `materializeTree`'s `default:` case).

### WR-04: `materializeTree` can leave the `git archive` child unreaped on error paths

**File:** `internal/platform/gateproof/tree_test.go:94-141`
**Issue:** Every `t.Fatalf` call inside the tar-extraction loop (lines 100, 105, 109, 124, 128, 132, 134, 138) aborts the goroutine via `runtime.Goexit()` without draining the remaining pipe, calling `cmd.Wait()`, or explicitly killing `cmd.Process`. The deferred `cancel()` (line 70) still runs, and `exec.CommandContext`'s default `Cancel` will eventually `Kill()` the process once `ctx` is done, but because `cmd.Wait()` (the only call in this file that reaps `os.Process`) is never reached on these paths, the killed process is not waited on. On POSIX this can leave a zombie process; more generally, the pipe reader owned by this `Cmd` is not closed until the process is reaped, so this is unmanaged cleanup on every early-fatal branch in a loop with eight separate exit points. This is a test-only, failure-path concern that will not cause a passing suite to misbehave, but it is a real gap in the cleanup contract this file otherwise tries hard to be careful about (see the deliberate `t.Cleanup`-not-`defer` comment two lines above for `os.RemoveAll(root)`, which was itself hardened for exactly this reason).

**Fix:** Register a single `t.Cleanup` right after `cmd.Start()` that guarantees the process is killed and reaped regardless of which exit path is taken:
```go
if err := cmd.Start(); err != nil {
    t.Fatalf("materializeTree: git archive: Start: %v", err)
}
t.Cleanup(func() {
    if cmd.ProcessState == nil {
        _ = cmd.Process.Kill()
        _ = cmd.Wait()
    }
})
```
so every `t.Fatalf` in the loop below is covered without having to thread cleanup logic through each branch.

## Info

### IN-01: `unreachableDSN` contains a placeholder credential that looks like a hardcoded secret

**File:** `internal/platform/gateproof/gateproof_test.go:31`
**Issue:** `const unreachableDSN = "postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable"` will trip a naive `password\s*[=:]` / hardcoded-credential scanner. It is not a real secret — `u:pw` are throwaway literal strings against a deliberately-unreachable port (`:1`) that the test itself controls, and no real system uses these credentials.
**Fix:** No functional change needed; consider a comment noting explicitly that `u`/`pw` are inert placeholders (the surrounding doc comment already explains the unreachable-port choice but not the credential choice), to pre-empt future scanner false positives or reviewer confusion.

### IN-02: `TestHelperProcess_WaitDelaySpawner` deliberately leaves an orphaned subprocess running after the test returns

**File:** `internal/platform/gate/harness_waitdelay_test.go:64-81`
**Issue:** The grandchild (`bash -c "…sleep 12"`) is started and never `Wait()`-ed for, and the parent helper process is killed by `gate.Run`'s context timeout at ~2s — well before the grandchild's own 12s sleep completes. This is precisely the scenario the test needs to reproduce and is well-documented, but it means every run of `TestGateRun_WaitDelayBoundsGrandchildHang` leaves a detached `bash`/`sleep` process running for up to ~10 more seconds after the Go test itself has already reported pass/fail.
**Fix:** No change required for correctness. Worth a one-line comment acknowledging the residual process is expected and self-terminating, so a future reader investigating leftover `sleep` processes during local debugging doesn't mistake it for a leak from unrelated code.

### IN-03: `gate.Run`'s deadline check has a narrow inherent boundary race

**File:** `internal/platform/gate/harness.go:231-251`
**Issue:** `cmd.Run()` and the subsequent `ctx.Err() == context.DeadlineExceeded` check are two sequential, independently-timed observations. In the extremely narrow window where the child process exits (successfully or not) at almost exactly the configured deadline, it is possible for `cmd.Run()` to return based on the process's real exit while `ctx.Err()` — checked microseconds later — already reports `DeadlineExceeded`, causing a run that actually completed in time to be reported as `TimedOut: true` with its real exit code discarded. This is inherent to any code that checks `ctx.Err()` after the fact rather than atomically with the operation's own completion, and is not specific to this fix.
**Fix:** No action needed for `DefaultTimeout` (4 minutes) callers. Callers that pass a `Timeout` close to the operation's expected runtime (as `TestGateRun_WaitDelayBoundsGrandchildHang` intentionally does, though not in a way this race would affect since it wants `TimedOut: true` anyway) should be aware a "just barely finished" result could be misreported as timed out; not worth guarding against given the class of callers in this codebase.

### IN-04: `WaitDelay`-related tests implicitly require `bash` on the host

**File:** `internal/platform/gate/harness_waitdelay_test.go:65`
**Issue:** `TestHelperProcess_WaitDelaySpawner` shells out to `bash -c "…"` for its grandchild. On a Windows host without Git Bash/WSL on `PATH`, `grandchild.Start()` fails and the helper `os.Exit(1)`s almost immediately, which would correctly fail `TestGateRun_WaitDelayBoundsGrandchildHang` via its `!result.TimedOut` check (a loud failure, not a silent false pass) — but the failure message would read as a `WaitDelay` regression rather than "bash is missing," which could mislead whoever triages it on an unusual environment.
**Fix:** No change required; this mirrors an existing convention in this package (`TestRunTimesOut` already depends on an external shell command). If this pattern spreads further, consider a documented environment precondition or a `bash`-presence check that skips with a clear message rather than failing with a `WaitDelay`-shaped error.

---

_Reviewed: 2026-09-03T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
