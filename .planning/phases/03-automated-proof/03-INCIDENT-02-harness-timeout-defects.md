---
type: incident
phase: 03-automated-proof
raised_by: execute-phase orchestrator
raised_at: 2026-09-03T00:00:00Z
severity: timeout-defeating
status: fixed
affects: [internal/platform/gateproof/tree_test.go, internal/platform/gate/harness.go]
---

# INCIDENT-02: Two timeout-defeating defects in the gate harness

Confirms and resolves the open item [[03-INCIDENT-01-orchestrator-self-contamination]]
left tracked separately: "The affected run was found deadlocked, not slow ... That is a
defect in its own right and is tracked separately ... See also: [[03-INCIDENT-02]] if the
`materializeTree` deadlock is confirmed." It is confirmed. This document also covers a
second, independent defect in the same harness family, found while fixing the first:
`gate.Run`'s `TimedOut` branch was unreachable in exactly the case it exists for.

Both defects share a shape: a timeout mechanism exists, and a downstream `cmd.Wait()`
call defeats it by blocking on I/O the timeout was never able to bound. Both were fixed
by draining or bounding that I/O explicitly, and both fixes carry a deterministic
regression test that does not depend on the underlying race that made the original
defect intermittent.

## Defect 1: `materializeTree` deadlocks non-deterministically

### What INCIDENT-01 measured

A 30-minute goroutine dump of `go test -run TestPROOF01` showed:

```
goroutine 18 [syscall, 29 min]: syscall.WaitForSingleObject -> os/exec.(*Cmd).Wait(exec.go:922)
  -> gateproof.materializeTree(tree_test.go:118)      <-- line 118 IS `cmd.Wait()`
goroutine 19 [syscall, 29 min]: os/exec.(*Cmd).writerDescriptor.func1 blocked in syscall.readFile
  (this is the stderr copier; it is CORRECT and proves stderr IS drained)
```

The extraction loop had already completed. `git.exe` was alive with 0.203s CPU, flat
across a 10s resample — a wedge, not slow work.

### Root cause, measured

`archive/tar` returns `io.EOF` at the archive's own end-of-archive marker (two 512-byte
zero blocks), but `git archive` pads its output to a full tar record boundary beyond
that marker. Measured against this repository:

| Quantity | Value |
|---|---|
| Total `git archive --format=tar HEAD` output | 4,587,520 bytes |
| Bytes remaining on the pipe after `tar.Reader` returns `io.EOF` | **4,608 bytes** |

`materializeTree` called `cmd.Wait()` without draining those 4,608 bytes. `git` blocks
writing them into a pipe nobody is reading; `cmd.Wait()` blocks on a process that cannot
exit. This races the pipe buffer — sometimes the whole tail already fits inside it,
which is why 03-01's own run of this exact test passed before a later run hung for 30
minutes. It is exactly the hazard `StdoutPipe`'s own doc names: *"it is incorrect to call
Wait before all reads from the pipe have completed."*

A second, independent problem in the same function: `materializeTree` used a bare
`exec.Command`, not `exec.CommandContext`, so `gate.DefaultTimeout` never applied to it —
it ran unbounded, on every gate, on two platforms, in CI.

### Fix

`internal/platform/gateproof/tree_test.go`, `materializeTree`:

1. **Drain to true EOF before `Wait()`**: `io.Copy(io.Discard, stdout)` after the
   extraction loop, before `cmd.Wait()`, erroring via `t.Fatalf` on failure like every
   other step in the function.
2. **Bound the call**: `exec.Command` → `exec.CommandContext` with an explicit
   `materializeTreeTimeout = 30 * time.Second` (justified inline: `git archive` on this
   repo produces 4.5 MB in well under a second uncontended, so 30s is roughly two orders
   of magnitude of margin — deliberately not reusing `gate.DefaultTimeout`, whose
   cold-CI rationale is calibrated against `make gate` children, not a bare `git archive`
   call this function makes directly). `cmd.WaitDelay = 5 * time.Second` bounds how long
   `Wait()` can block for I/O after the context fires, as a second line of defense if the
   drain is ever removed again.
3. Extraction semantics are otherwise byte-identical: the `pax_global_header` skip, the
   absolute-path and path-escape guards, the `entryCount == 0` guard, and `t.Cleanup` are
   all unchanged.

Verified: `TestMaterializeTree_Control` (the existing control) passes in 0.49s after the
fix, confirming the extraction still produces the same tree.

Commits: `60bb107` (fix), `5f3d639` (regression test).

### Falsifiability demonstration (Task 2)

Depending on the real `git archive` race to demonstrate this would be exactly the
intermittency that let it through the first time. Instead,
`internal/platform/gateproof/tree_drain_test.go` drives a **synthetic** child process (the
`TestHelperProcess_TarWithTrailer` self-exec pattern, the same one `os/exec`'s own tests
use) that emits a valid one-entry tar stream followed by a hardcoded 1 MiB trailer — far
larger than any plausible OS pipe buffer — so a reader that stops at `tar.Reader`'s
`io.EOF` blocks the writer **every run**, not intermittently.

**Captured BEFORE (drain line temporarily removed, deadlock reproduced):**

```
=== RUN   TestHelperProcess_TarWithTrailer
--- PASS: TestHelperProcess_TarWithTrailer (0.00s)
=== RUN   TestMaterializeTree_DrainsPastTarEOF
    tree_drain_test.go:129: TestMaterializeTree_DrainsPastTarEOF: cmd.Wait() did not return within the test's 5s bound — deadlock reproduced (see 03-INCIDENT-02)
--- FAIL: TestMaterializeTree_DrainsPastTarEOF (5.00s)
FAIL
FAIL	github.com/EpistemicOS/epistemicos/internal/platform/gateproof	5.948s
FAIL
```

**Captured AFTER (drain line restored):**

```
=== RUN   TestHelperProcess_TarWithTrailer
--- PASS: TestHelperProcess_TarWithTrailer (0.00s)
=== RUN   TestMaterializeTree_DrainsPastTarEOF
--- PASS: TestMaterializeTree_DrainsPastTarEOF (0.50s)
PASS
ok  	github.com/EpistemicOS/epistemicos/internal/platform/gateproof	1.500s
```

The committed test file (`tree_drain_test.go`) always contains the passing (drained)
version — the failure above was captured by temporarily commenting out the
`io.Copy(io.Discard, stdout)` call, running `go test -run
TestMaterializeTree_DrainsPastTarEOF`, capturing this output, then restoring the drain
and reconfirming the pass shown above, before either state was committed. No `zzz_*`
scratch file was left behind.

## Defect 2: `gate.Run`'s `TimedOut` branch is unreachable

### Root cause, measured

`gate.Run` uses `exec.CommandContext` with `cmd.Stdout`/`cmd.Stderr` set to `*bytes.Buffer`
(not `*os.File`), so `os/exec` allocates OS pipes plus copier goroutines internally, and
`cmd.Run()` (which calls `Wait()` internally) blocks until those copiers see EOF.
`CommandContext`'s default cancellation is `cmd.Process.Kill()` — the **direct child
only**: no process group, no job object. On Windows, a `make` → `go test` →
test-binary chain hands its stdout/stderr pipe write handles down to grandchildren, so
killing `make` on timeout leaves the pipe open in a still-running grandchild. The copier
goroutine never sees EOF, `cmd.Run()` never returns, and the

```go
if ctx.Err() == context.DeadlineExceeded {
    result.TimedOut = true
    ...
}
```

check immediately below it is never reached — `TimedOut` can never be set in exactly the
case it exists for.

### Fix

`internal/platform/gate/harness.go`, `Run`:

```go
cmd.WaitDelay = runWaitDelay   // runWaitDelay = 5 * time.Second
```

`WaitDelay` (Go 1.20+) bounds how long `Wait()` blocks for the copier goroutines after
the process has exited or the context has been canceled, closing the pipes and returning
once that delay elapses regardless of whether a grandchild still holds them open. This is
simpler and more portable than a Windows job object, and is exactly what the Go
documentation recommends for "any command that produces its own subprocesses."

5s is deliberately short relative to `DefaultTimeout` (4m): it only bounds the tail after
the context is already done, not extra running time for a well-behaved child. All
non-timeout paths — `Stdout`/`Stderr`/`Combined`, `ExitCode`, the `t.Fatalf`-on-start-failure
path — are unchanged. A timed-out run can now return **partial** captured output (`Wait`
forcibly stops the copy once `runWaitDelay` elapses), which is documented at the call
site so a proof's vacuity guard still sees the escalation preamble whenever the
timed-out child managed to write it before the delay expired.

Commits: `fe052fb` (fix), `d47f70f` (regression test).

### Falsifiability demonstration (Task 4)

`internal/platform/gate/harness_waitdelay_test.go` drives a synthetic spawner
(`TestHelperProcess_WaitDelaySpawner`, self-exec'd) that starts a grandchild — deliberately
`bash -c "... sleep 12"`, not another copy of the test binary — inheriting the spawner's
own `os.Stdout`/`os.Stderr` `*os.File` directly (the same handle `gate.Run`'s internal
pipe gave the spawner), then outlives a short `RunOptions.Timeout` so `ctx` cancellation
kills the spawner while the grandchild survives underneath it, still holding the pipe.

**Captured BEFORE (`cmd.WaitDelay = runWaitDelay` temporarily removed):**

```
=== RUN   TestHelperProcess_WaitDelaySpawner
--- PASS: TestHelperProcess_WaitDelaySpawner (0.00s)
=== RUN   TestGateRun_WaitDelayBoundsGrandchildHang
    harness_waitdelay_test.go:135: gate.Run: took 12.4292768s, at or past waitDelayBoundThreshold (9s) — WaitDelay did not bound the wait (see 03-INCIDENT-02); result={Stdout:grandchild-alive
         Stderr: Combined:grandchild-alive
         ExitCode:-1 TimedOut:true}
--- FAIL: TestGateRun_WaitDelayBoundsGrandchildHang (12.43s)
FAIL
FAIL	github.com/EpistemicOS/epistemicos/internal/platform/gate	13.219s
FAIL
```

Note `TimedOut:true` is present even in this failing run — `ctx.Err()` had indeed become
`context.DeadlineExceeded` well before this point (the spawner was killed at ~2s). The
failure is not that `TimedOut` was never set; it is that `cmd.Run()` did not *return* until
the grandchild's own 12s sleep ended, ~10s after the timeout that was supposed to bound
it — precisely "TimedOut can never be set in exactly the case it exists for," restated as
"can never be *observed in time to matter*."

**Captured AFTER (`cmd.WaitDelay = runWaitDelay` restored):**

```
=== RUN   TestHelperProcess_WaitDelaySpawner
--- PASS: TestHelperProcess_WaitDelaySpawner (0.00s)
=== RUN   TestGateRun_WaitDelayBoundsGrandchildHang
--- PASS: TestGateRun_WaitDelayBoundsGrandchildHang (7.00s)
PASS
ok  	github.com/EpistemicOS/epistemicos/internal/platform/gate	7.788s
```

7.00s matches `waitDelayDrivingTimeout` (2s) + `runWaitDelay` (5s) exactly.

### Two pitfalls found and worked around while building this reproduction

Recorded because both cost real debugging time and would silently reappear if someone
"simplified" this test later:

1. **A too-tight driving `Timeout` (200ms) produced a false pass.** The spawner's own
   process-start latency (loading the Go runtime for a fresh test-binary invocation)
   sometimes exceeds 200ms, so `ctx` killed the spawner before it finished starting its
   grandchild at all — the test observed a fast, empty return (`TimedOut:true`, empty
   `Stdout`) that looked like a pass but reproduced nothing. Measured directly with an
   external driver program isolating `gate.Run`'s exact shape: 300ms was too tight (empty
   capture, near-instant return); 2s was reliably sufficient (full capture, correct
   ~7-8s bound). `waitDelayDrivingTimeout` is set to 2s for this reason, with the
   measurement recorded in the test's own doc comment so a future "let's make this
   faster" edit does not reintroduce the false pass.

2. **A self-exec'd grandchild broke the test suite's own exit code even though every
   test passed.** The first version of the grandchild helper was a second self-exec of
   the same compiled test binary, sleeping past this test's own ~7s completion. On
   Windows, a still-running process holding that binary's executable file open prevents
   `go test`'s own post-run cleanup from removing/replacing the temp binary, producing
   `go: remove ...\gate.test.exe: Access is denied.` and a **non-zero exit code from the
   `go test` process despite `PASS` / `ok` being printed for every test** — exactly the
   kind of gate-defeating failure this whole phase exists to prevent, reintroduced by the
   very test proving a related fix. Switching the grandchild to `bash -c "... sleep N"` —
   an external binary `go test` does not manage — removed the conflict entirely, using
   the same external-command approach `TestRunTimesOut` (this package, pre-existing)
   already relies on.

   A related design consequence: the driving test also does **not** use a driving
   goroutine + `select` to bound its own observation. An earlier version did, and hit a
   reproducible multi-minute stall (one run took 204s against a 30s `-timeout` before
   `go test`'s own watchdog force-killed the process) that traced to a background
   goroutine still calling `*testing.T` methods after the goroutine running the select
   had already returned via `t.Fatalf`. Because the synthetic grandchild's sleep is
   itself finite (12s, a constant this test controls), there is no unbounded-hang case
   to guard against with an outer `select` — the worst possible runtime is bounded by
   that constant either way, so calling `Run` directly on the test's own goroutine and
   asserting on elapsed time is both simpler and avoids that hazard. This is recorded in
   the test's own doc comment.

## Summary

| | Defect 1: `materializeTree` | Defect 2: `gate.Run` |
|---|---|---|
| Symptom | 30-minute hang, confirmed via goroutine dump | `TimedOut` never observably set |
| Root cause | `cmd.Wait()` before draining 4,608 bytes past tar's `io.EOF` | Grandchild holds pipe after direct child is killed; no `WaitDelay` |
| Fix | `io.Copy(io.Discard, stdout)` before `Wait()`; bound with `exec.CommandContext` (30s) + `WaitDelay` (5s) | `cmd.WaitDelay = 5s` |
| Regression test | `tree_drain_test.go`: synthetic tar + 1 MiB trailer, deterministic every run | `harness_waitdelay_test.go`: synthetic spawner + bash-sleep grandchild, deterministic every run |
| Fix commit | `60bb107` | `fe052fb` |
| Test commit | `5f3d639` | `d47f70f` |

Both fixes were verified end-to-end with the demonstration technique this task required:
capture the real failure by temporarily reverting the fix and running the test, capture
the real pass by restoring it and running again. No claim in this document rests on
untested prose.

See also: [[03-INCIDENT-01-orchestrator-self-contamination]] for the contaminated-timing
half of this investigation, which is unaffected by either defect above and remains void
for `DefaultTimeout` calibration purposes.
