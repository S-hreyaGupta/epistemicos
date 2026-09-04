---
phase: 03-automated-proof
plan: review-fix
subsystem: testing
tags: [go, os-exec, waitdelay, code-review, gate-run, materializetree]

# Dependency graph
requires:
  - phase: 03-automated-proof
    plan: review
    provides: "03-REVIEW.md's WR-01 and WR-02 findings against tonight's harness-timeout-defect fixes"
provides:
  - "gate.Run correctly classifies exec.ErrWaitDelay as TimedOut instead of falling through to a misleading 'could not be started' t.Fatalf"
  - "TestGateRun_ErrWaitDelayMisclassification: deterministic regression test for WR-01, self-exec'd helper pattern, no ctx-expiry dependency"
  - "materializeTree's WaitDelay comment corrected to name the actual protection mechanism (ctx deadline + default Cancel), not WaitDelay's inert-here pipe-forcing path"
  - "03-INCIDENT-02-harness-timeout-defects.md addendum distinguishing 'fix introduced this' (WR-01) from 'fix exposed/carried this pre-existing class'"
affects: [gate, gateproof]

# Actuals (#2632)
actuals:
  tokens: 4819
  tasks: 5
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Self-exec'd helper-process regression test that reproduces a stdlib error sentinel (exec.ErrWaitDelay) via an independent marker-file side effect, proving the subprocess ran before asserting on the caller's classification of the outcome — avoids relying on *testing.T from a background goroutine after the main test goroutine may have Fatal'd."
    - "Falsifiability demonstration by temporary revert: comment out the fix, run the targeted test, capture the real failing output verbatim, restore, capture the real passing output verbatim — both pasted into the SUMMARY/INCIDENT doc rather than described."

key-files:
  created:
    - internal/platform/gate/harness_errwaitdelay_test.go
  modified:
    - internal/platform/gate/harness.go
    - internal/platform/gateproof/tree_test.go
    - .planning/phases/03-automated-proof/03-INCIDENT-02-harness-timeout-defects.md

key-decisions:
  - "Task 1 (WR-01 fix) and Task 2 (its regression test) were committed together in one commit rather than split, because the test is the only thing proving the fix's correctness — an isolated fix commit with no accompanying proof would be exactly the 'untested prose' this phase's own convention rejects."
  - "Task 3 (WR-02 comment fix) was committed separately from Task 1, since it touches a different package (gateproof, not gate) and is a pure comment correction with no code/behavior change — bundling it with WR-01's fix would have mixed a behavioral fix with a documentation-only correction in one commit."
  - "The WR-01 regression test drives RunOptions.Timeout at 30s (far larger than the ~5s WaitDelay bound it expects) specifically so ctx.Err() never becomes context.DeadlineExceeded — this isolates WR-01's scenario from Defect 2's already-covered ctx-expiry path (TestGateRun_WaitDelayBoundsGrandchildHang) and is the detail that makes 'ctx never expires' a measured property of the test, not an assumption."
  - "The diagnostic goroutine that polls for the marker file in TestGateRun_ErrWaitDelayMisclassification communicates via plain fmt.Fprintf to os.Stderr, never via *testing.T — 03-INCIDENT-02 already documents a 'Log in goroutine after Test has completed' hazard from a similar driving-goroutine pattern in a sibling test, and calling t.Fatalf inside gate.Run's own call (which happens on the main test goroutine) Goexits before any post-Run assertion could run, so the marker's own proof had to be independent of the test's control flow."
  - "WR-03 and WR-04 (both flagged by the same review) are explicitly out of scope for this fix pass and are left untouched, per the dispatch's prohibitions — both are already registered in STATE.md's Deferred Items table (see below) rather than re-derived here."

requirements-completed: []

coverage:
  - id: D1
    description: "gate.Run classifies exec.ErrWaitDelay as TimedOut instead of falling through to a misleading t.Fatalf, for a process that started, ran, and exited successfully"
    verification:
      - kind: unit
        ref: "internal/platform/gate/harness_errwaitdelay_test.go#TestGateRun_ErrWaitDelayMisclassification"
        status: pass
    human_judgment: false
  - id: D2
    description: "WR-01's fix is falsifiable: removing it reproduces the real misleading Fatalf (captured), restoring it reproduces the real pass (captured)"
    verification:
      - kind: unit
        ref: "internal/platform/gate/harness_errwaitdelay_test.go#TestGateRun_ErrWaitDelayMisclassification (run twice: fix removed, fix restored)"
        status: pass
    human_judgment: false
  - id: D3
    description: "materializeTree's WaitDelay comment (tree_test.go) accurately states what protects the git archive child (ctx deadline + default Cancel), not WaitDelay's inert pipe-forcing path"
    verification:
      - kind: unit
        ref: "internal/platform/gateproof/tree_test.go#TestMaterializeTree_Control"
        status: pass
      - kind: unit
        ref: "internal/platform/gateproof/tree_drain_test.go#TestMaterializeTree_DrainsPastTarEOF"
        status: pass
    human_judgment: false
  - id: D4
    description: "03-INCIDENT-02 addendum records WR-01 as a defect the WaitDelay fix introduced (not a pre-existing/exposed defect), the exact ErrWaitDelay mechanism, both captured before/after outputs, and WR-02's correction — cross-referenced to 03-REVIEW.md"
    verification: []
    human_judgment: true
    rationale: "Documentation completeness and accuracy of a narrative addendum is a judgment call about clarity and correct categorization, not something a test asserts."

duration: 35min
completed: 2026-09-03
status: complete
---

# Phase 3 Code-Review-Fix Pass: WR-01 fix + WR-02 correction Summary

**Fixed a real correctness gap in `gate.Run`'s subprocess-result classification (misses `exec.ErrWaitDelay`, falls through to a false "could not be started" diagnosis) and corrected an overstated comment about what `WaitDelay` protects in `materializeTree` — both found by this phase's own code review of tonight's harness-timeout-defect fixes.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 5 (WR-01 fix, WR-01 regression test + falsifiability demonstration, WR-02 comment correction, INCIDENT-02 addendum, this SUMMARY)
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- **WR-01 fixed:** `internal/platform/gate/harness.go`'s `Run` now checks `errors.Is(runErr, exec.ErrWaitDelay)` — placed before the `errors.As(runErr, &exitErr)` branch, alongside the existing `ctx.Err() == context.DeadlineExceeded` check — and classifies that outcome as `TimedOut: true`, `ExitCode: -1`, instead of falling through to `t.Fatalf("... could not be started: %v", runErr)`. The added comment cites the exact stdlib doc wording and names this phase's own review (WR-01) so a future reader knows the gap was found, not speculated.
- **Regression test added and proven falsifiable:** `internal/platform/gate/harness_errwaitdelay_test.go` reproduces WR-01's exact scenario deterministically — a self-exec'd helper process that writes a marker file (independent proof it started and ran), spawns a `bash`/`sleep` grandchild inheriting its stdout handle, and exits successfully almost immediately, with a driving `Timeout` (30s) far larger than the ~5s `WaitDelay` bound so `ctx.Err()` stays `nil` throughout. Verified by temporarily removing the fix, running the test, and capturing the real misleading `t.Fatalf` firing ~5s after the marker was already observed present; then restoring the fix and capturing the real pass. Both captures are pasted verbatim below and in the INCIDENT-02 addendum.
- **WR-02 corrected:** the comment on `materializeTree`'s `cmd.WaitDelay = 5 * time.Second` assignment (`internal/platform/gateproof/tree_test.go`) no longer claims WaitDelay "is what stops a wedged child... from holding Wait open." It now states plainly that this specific usage shape (`cmd.StdoutPipe()` with a manual synchronous drain) never populates the internal `goroutineErr` channel WaitDelay's pipe-forcing path is gated on, so the real protection is `ctx`'s own deadline plus `exec.CommandContext`'s default `Cancel` (`cmd.Process.Kill()`) — and that WaitDelay would need `cmd.Stdout` to be a plain `io.Writer` (mirroring `gate.Run`'s own shape) to actually engage. One-line-scope comment change; no code or behavior change; `WaitDelay` field itself left in place per the dispatch's instruction. `tree_drain_test.go`'s `cmd.WaitDelay = 2 * time.Second` assignment carries no comment claiming this mechanism, so it required no correction.
- **03-INCIDENT-02 addendum:** appended (not edited in place, per this project's "corrections go beside the original claim" convention) a clearly-marked section stating WR-01 is a defect the WaitDelay fix (`fe052fb`) **introduced**, not one it exposed or that pre-existed — a distinct category from "another instance of the same pre-existing defect class" — with the exact mechanism cited against Go's own doc comment, both captured before/after outputs, and WR-02's correction, cross-referenced to `03-REVIEW.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1 + Task 2: WR-01 fix + regression test** - `1caa410` (fix)
2. **Task 3: WR-02 comment correction** - `f329265` (docs)
3. **Task 4: 03-INCIDENT-02 addendum** - `b9d8a1b` (docs)
4. **Task 5: this SUMMARY** - committed separately below

_Tasks 1 and 2 were combined into a single commit — see "Decisions Made" below for why._

## Files Created/Modified

- `internal/platform/gate/harness.go` - Added the `errors.Is(runErr, exec.ErrWaitDelay)` classification branch (WR-01 fix)
- `internal/platform/gate/harness_errwaitdelay_test.go` - New: `TestHelperProcess_ErrWaitDelaySpawner` + `TestGateRun_ErrWaitDelayMisclassification` (WR-01 regression test)
- `internal/platform/gateproof/tree_test.go` - Corrected the `cmd.WaitDelay` comment in `materializeTree` (WR-02 correction, comment-only)
- `.planning/phases/03-automated-proof/03-INCIDENT-02-harness-timeout-defects.md` - Appended the WR-01/WR-02 addendum

## Decisions Made

- Tasks 1 and 2 (fix + test) were combined into one commit — the fix without its proof is exactly the kind of untested claim this project's own convention (see `03-INCIDENT-02`'s own "no claim in this document rests on untested prose") rejects. Splitting them would create an intermediate commit with an unverified fix.
- Task 3 (WR-02) was committed separately — different package, comment-only, no behavioral coupling to WR-01's fix.
- See frontmatter `key-decisions` for the full list (regression test design choices, scope boundary on WR-03/WR-04).

## Falsifiability Demonstration (verbatim captures)

**WR-01 fix temporarily removed (`errors.Is(runErr, exec.ErrWaitDelay)` branch commented out), test run fresh:**

```
=== RUN   TestGateRun_ErrWaitDelayMisclassification
MARKER OBSERVED at 2026-09-03T23:34:05.1587586+05:30: spawner process started, wrote its marker, and exited — independent of whatever gate.Run later classifies this call as
    harness_errwaitdelay_test.go:148: gate.Run: C:\Users\gupta\AppData\Local\Temp\go-build3588986029\b001\gate.test.exe [-test.run=TestHelperProcess_ErrWaitDelaySpawner] could not be started: exec: WaitDelay expired before I/O complete
--- FAIL: TestGateRun_ErrWaitDelayMisclassification (5.39s)
FAIL
FAIL	github.com/EpistemicOS/epistemicos/internal/platform/gate	6.236s
FAIL
```

**WR-01 fix restored, test run fresh (`-count=1`):**

```
=== RUN   TestGateRun_ErrWaitDelayMisclassification
MARKER OBSERVED at 2026-09-03T23:34:44.5853754+05:30: spawner process started, wrote its marker, and exited — independent of whatever gate.Run later classifies this call as
--- PASS: TestGateRun_ErrWaitDelayMisclassification (5.43s)
PASS
ok  	github.com/EpistemicOS/epistemicos/internal/platform/gate	6.262s
```

The full `internal/platform/gate` package suite (all pre-existing tests plus the new one) was also re-run after restoring the fix — all pass, 35.96s total, no regressions.

The comment-only WR-02 correction was verified by re-running `TestMaterializeTree_Control` and `TestMaterializeTree_DrainsPastTarEOF` (`internal/platform/gateproof`) unchanged — both pass, confirming zero behavior change.

## Deferred (not this pass's scope)

Per the dispatch's explicit prohibitions, WR-03 and WR-04 were left untouched. Both are already registered in `.planning/STATE.md`'s Deferred Items table — cited here rather than re-derived:

- **WR-03** (`ordering_test.go:63-69`, unanchored `"migrate"` substring match) — registered under "Test-harness robustness" in STATE.md's Deferred Items table, 2026-09-03, Phase 3 code review. Not currently reachable (today's `make -n gate` expansion has exactly one line containing "migrate"); deferred as low-urgency hardening.
- **WR-04** (`materializeTree`'s tar-extraction loop can leave the `git archive` child unreaped on error paths) — registered under "Process lifecycle" in STATE.md's Deferred Items table alongside `gate.Run`'s own analogous grandchild-reaping gap, as one shared defect class (a process-group/Job-Object fix would close both) rather than two independent patches. Not taken now because it is new process-management machinery, not a fix scoped to either call site.

No other files in `gateproof` (`proof01_test.go`, `proof02_test.go`, `proof03_test.go`, `ordering_test.go`, `gateproof_test.go`) were touched.

## Issues Encountered

None. All targeted tests passed on first attempt after each change; no auto-fix deviations beyond the plan's own explicit instructions were needed.

## Next Phase Readiness

`gate.Run`'s subprocess-result classification now covers every documented `exec.CommandContext` + `WaitDelay` outcome relevant to this codebase (success, non-zero exit, context-deadline timeout, WaitDelay-forced completion). `materializeTree`'s comment now accurately describes its own protection mechanism. No blockers for Phase 3's remaining governance work; WR-03/WR-04 remain tracked in STATE.md for future disposition (see "Deferred" above).

---
*Phase: 03-automated-proof (code-review-fix pass, not a numbered plan)*
*Completed: 2026-09-03*
