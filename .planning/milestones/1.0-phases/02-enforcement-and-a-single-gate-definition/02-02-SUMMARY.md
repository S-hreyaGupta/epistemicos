---
phase: 02-enforcement-and-a-single-gate-definition
plan: 02
subsystem: testing
tags: [go-test, exec, make, subprocess-harness, ci-gate]

# Dependency graph
requires:
  - phase: 02-enforcement-and-a-single-gate-definition
    provides: "02-01: env-preflight and gate Make targets, testenv.RequireEnv/escalationPreamble; 02-03: docker-compose.yml postgres bound to 127.0.0.1:5432 (live, healthy) that Task 3's TestMakeTestPrintsLenientBanner and the final make gate check depend on at runtime"
provides:
  - "internal/platform/gate package: Run/Make/RunOptions/RunResult, SkipIfNested, RepoRoot, DepthEnv, DefaultTimeout — Phase 3's PROOF-01/02/03 contract, confirmed at the Task 1 checkpoint (human decision: proceed)"
  - "The recursion guard (EPISTEMIC_OS_TEST_MAKE_DEPTH, incremented last in buildChildEnv so Unset/Env cannot defeat it; SkipIfNested declining at depth >= 1; a malformed marker a hard failure rather than depth 0 or a silent skip)"
  - "TestEnvPreflightIsVoiceless: D-03's voiceless-preflight constraint as a differential subprocess assertion, not a Makefile-text check"
  - "TestMakeTestPrintsLenientBanner: D-05's lenient-run banner asserted from real make test output, both clauses checked separately"
  - "ROADMAP.md Phase 3 'Note on the harness', recording the slice taken (D-07 binding condition 2) without narrowing Phase 3's success criteria"
affects: [03-01-automated-proof]

# Actuals (#2632)
actuals:
  tokens: 6583
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Depth-marker recursion guard for shell-out-to-make tests: DepthEnv incremented last in child-env construction (after Unset/Env are applied), SkipIfNested(t) as the first statement of every test that spawns a Make subprocess, malformed marker is a hard failure rather than either convenient wrong answer (treat-as-0 recurses, treat-as-nested skips vacuously)"
    - "Differential subprocess comparison (extraLines, normalizeElapsed) over static Makefile-text assertions, for constraints about a recipe's own output rather than its source text"
    - "Two-step negative control demonstrating a comparison CAN fail before a later test relies on it (TestExtraLines_Control_DetectsAnAddedLine), matching testenv's TestHostFromURL_Control_NeverReturnsUserinfo / TestUnparseableURLMsg_Control_NoLeak shape"

key-files:
  created:
    - internal/platform/gate/harness.go
    - internal/platform/gate/harness_test.go
    - internal/platform/gate/makefile_test.go
  modified:
    - .planning/ROADMAP.md

key-decisions:
  - "Task 1 checkpoint (type=checkpoint:decision, gate=blocking-human) was answered 'proceed' by the human operator before this executor was dispatched — not auto-approved, not inferred. Recorded here per the dispatch instructions rather than re-litigated. The locked API (Run/Make/RunOptions/RunResult/SkipIfNested/RepoRoot/DepthEnv/DefaultTimeout) is now Phase 3's contract; PROOF-01/02/03 bind to it as Make(t, \"gate\", {Unset:[EPISTEMIC_OS_DB_URL]}), Make(t, \"gate\", {Env:[closed-port DSN]}), and the same with fixture setup."
  - "Task 2 (tdd=true) executed as a genuine RED/GREEN pair rather than writing both files together: harness_test.go was committed first, and RED was demonstrated for real (not merely asserted) by temporarily moving the just-authored harness.go aside and running go vet, confirming 'undefined: nestingDepth', before restoring it and committing harness.go as GREEN."
  - "TestRunIncrementsDepth observes the depth increment via a real child process (bash -c 'printf %s \"$EPISTEMIC_OS_TEST_MAKE_DEPTH\"') rather than a comment-only assertion or an exported test seam, per the plan's stated preference for 'the simplest form that genuinely observes the increment'."
  - "TestRunTimesOut uses a 100ms per-call Timeout against a 5s bash sleep, asserting TimedOut, a non-zero ExitCode, and that the whole call returned well under DefaultTimeout (4m) — proving the per-call override is honored, not merely that the const exists (T-02-07's threat mitigation was previously unexercised in this direction)."
  - "Both closed-port and compose DSNs use 127.0.0.1, not localhost, per the carried-forward finding that this host has no ::1 listener since 02-03's loopback rebind."

patterns-established:
  - "Pattern 3 (this plan): the recursion guard's own failure modes are closed both directions and proven by a synthetic-input table test (TestNestingDepth), matching the discipline nestingDepth's own doc comment states — neither convenient wrong answer is chosen for a malformed marker."

requirements-completed: [GATE-01, GATE-02]

coverage:
  - id: D1
    description: "A Go test can invoke a Make target as a subprocess from the repository root, capturing stdout/stderr separately, exit code, and a timeout (D-07)"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "internal/platform/gate/harness_test.go#TestRunIncrementsDepth, #TestRunTimesOut, #TestRepoRootFindsGoMod"
        status: pass
      - kind: integration
        ref: "internal/platform/gate/makefile_test.go#TestEnvPreflightIsVoiceless, #TestMakeTestPrintsLenientBanner (both invoke real make subprocesses)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The recursion guard cannot recurse without bound: every child carries an incremented depth marker set last (so Unset/Env cannot defeat it), every test declines at depth >= 1, and a malformed marker hard-fails naming the variable and value rather than choosing either convenient wrong answer"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "internal/platform/gate/harness_test.go#TestNestingDepth (8 synthetic cases)"
        status: pass
      - kind: integration
        ref: "Task 2 verify steps 3-4 (EPISTEMIC_OS_TEST_MAKE_DEPTH=1 declines with --- SKIP; =abc hard-fails naming the variable)"
        status: pass
    human_judgment: false
  - id: D3
    description: "make env-preflight on the unreachable-database path contributes no line of its own to either stream, asserted differentially against the bare go test command it wraps (D-03); the comparison is proven able to report a violation before this test relies on it"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "internal/platform/gate/harness_test.go#TestExtraLines_Control_DetectsAnAddedLine"
        status: pass
      - kind: integration
        ref: "internal/platform/gate/makefile_test.go#TestEnvPreflightIsVoiceless"
        status: pass
    human_judgment: false
  - id: D4
    description: "make test prints the lenient-run banner, asserted from real subprocess output rather than Makefile text, both load-bearing clauses checked separately (D-05)"
    verification:
      - kind: integration
        ref: "internal/platform/gate/makefile_test.go#TestMakeTestPrintsLenientBanner"
        status: pass
    human_judgment: false
  - id: D5
    description: "ROADMAP.md Phase 3 records that Phase 2 took a slice of PROOF-01/02/03's design question (naming the harness package, PROJECT.md lines 91-93, the recursion guard, and the three RunOptions shapes), without narrowing Phase 3's Goal/Depends on/Requirements/Success Criteria (D-07 binding condition 2)"
    verification:
      - kind: unit
        ref: "Task 3 verify steps 4-5 (grep checks against the Phase 3 section; git diff shows only added lines)"
        status: pass
    human_judgment: false
  - id: D6
    description: "make gate remains green end-to-end after this package lands, with the compose database up"
    verification:
      - kind: integration
        ref: "Task 3 verify step 6 (full make gate run)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-02
status: complete
---

# Phase 2 Plan 2: The Shell-Out-to-Make Harness Summary

**Built `internal/platform/gate` — a depth-guarded shell-out-to-`make` subprocess harness (`Run`/`Make`/`RunOptions`/`RunResult`/`SkipIfNested`) confirmed at a human checkpoint as Phase 3's PROOF-01/02/03 contract, then used it to turn D-03's voiceless-preflight constraint and D-05's lenient-run banner into differential subprocess assertions instead of Makefile-text checks.**

## Performance

- **Duration:** 8 min (commit-to-commit; base `ed043e2` to `bf4e0c3`)
- **Started:** 2026-09-02T07:35:51Z
- **Completed:** 2026-09-02T07:43:00Z
- **Tasks:** 3 (1 checkpoint + 2 auto)
- **Files modified:** 4 (`internal/platform/gate/harness.go`, `internal/platform/gate/harness_test.go`, `internal/platform/gate/makefile_test.go`, `.planning/ROADMAP.md`)

## Checkpoint: Task 1

**Type:** `checkpoint:decision`, `gate="blocking-human"`
**Decision:** Confirm that Phase 2 builds the shell-out-to-make harness, and that its API shape becomes Phase 3's contract.
**Answer:** `proceed` — decided by the human operator before this executor was dispatched. This is recorded as an explicit human decision, not auto-approved and not inferred by this executor, per the dispatch instructions.

The locked API, verbatim as approved:

```
gate.Run(t, argv []string, opts RunOptions) RunResult
gate.Make(t, target string, opts RunOptions) RunResult
gate.SkipIfNested(t)
gate.RepoRoot(t) string
gate.DepthEnv, gate.DefaultTimeout

RunOptions{Env, Unset []string; Timeout time.Duration; Silent bool}
RunResult{Stdout, Stderr, Combined string; ExitCode int; TimedOut bool}
```

Alternatives declined, and why (recorded so a later reader sees reasoning, not just an outcome):
- **`narrow`** (drop exported `Run`) — D-03's voicelessness assertion has to run the bare `go test` command that `env-preflight` wraps and compare the two; without an exported `Run` that half would live outside the harness, unguarded by `SkipIfNested`, exactly where it would decay.
- **`defer`** (no harness in Phase 2) — D-07 already rejected its only alternative, static Makefile-text assertions, because the likely decay mode is a tool that starts printing, which text assertions cannot see. Deferring would leave D-03 and D-05 as intentions rather than testable constraints.

## Accomplishments
- `internal/platform/gate/harness.go`: `Run`/`Make` shell out to a Make target (or any argv) from the repository root, capturing stdout and stderr in separate buffers, an exit code, and a `TimedOut` flag under `exec.CommandContext` with a per-call `Timeout` (default `DefaultTimeout`, 4 minutes, below `go test`'s 10-minute package default)
- The recursion guard: every child carries `EPISTEMIC_OS_TEST_MAKE_DEPTH` set to the parent's depth plus one, applied **last** in `buildChildEnv` (after `Unset` and `Env`) so a caller cannot defeat it by naming the variable in either; `SkipIfNested(t)` declines at depth ≥ 1; `nestingDepth` hard-fails on a malformed value naming the variable and its value, choosing neither of the two convenient wrong answers
- `extraLines`/`normalizeElapsed`: the differential-comparison helpers, proven able to report a violation (`TestExtraLines_Control_DetectsAnAddedLine`) before `TestEnvPreflightIsVoiceless` relies on them
- `TestEnvPreflightIsVoiceless` (D-03): runs the real `make env-preflight` against a closed-port DSN and the bare `go test ./internal/platform/testenv/` command it wraps, and asserts nothing on either stream is present in the Make side that the direct side did not also say
- `TestMakeTestPrintsLenientBanner` (D-05): runs the real `make test` and asserts both load-bearing clauses of the banner separately, so a half-deleted banner is caught; this is the one call site where the recursion loop this plan is built around is real, terminated at depth 1 by `SkipIfNested`
- `ROADMAP.md` §Phase 3 gains a "Note on the harness" line recording the slice taken, without altering Phase 3's Goal, Depends on, Requirements, or Success Criteria

## Task Commits

1. **Task 1: Checkpoint decision** — no commit (decision recorded above; already answered `proceed` before dispatch)
2. **Task 2: The harness and its recursion guard** (`tdd="true"`) — RED/GREEN pair:
   - `e79998c` (test) — add failing `harness_test.go`; RED demonstrated for real by moving the just-authored `harness.go` aside and confirming `go vet` reports `undefined: nestingDepth`, then restoring it
   - `9aa0b95` (feat) — add `harness.go` (GREEN: full package test suite passes)
3. **Task 3: Assert the voiceless preflight and the lenient-run banner, record the roadmap slice** — `bf4e0c3` (feat) — `makefile_test.go` + `ROADMAP.md` note

**Plan metadata:** this commit (docs: complete plan)

## Files Created/Modified
- `internal/platform/gate/harness.go` — the harness: `DepthEnv`, `DefaultTimeout`, `nestingDepth`, `SkipIfNested`, `RepoRoot`, `RunOptions`, `RunResult`, `Run`, `Make`, `buildChildEnv`, `normalizeElapsed`, `extraLines`
- `internal/platform/gate/harness_test.go` — table-driven tests for the pure functions (`TestNestingDepth`, `TestNormalizeElapsed`, `TestExtraLines`, `TestExtraLines_Control_DetectsAnAddedLine`, `TestRepoRootFindsGoMod`) plus the two subprocess-spawning tests (`TestRunIncrementsDepth`, `TestRunTimesOut`)
- `internal/platform/gate/makefile_test.go` — `TestEnvPreflightIsVoiceless`, `TestMakeTestPrintsLenientBanner`
- `.planning/ROADMAP.md` — Phase 3 "Note on the harness" line (added, nothing removed)

## Decisions Made
See `key-decisions` in frontmatter. Notably: Task 2's TDD gate was demonstrated with a real compile failure (not merely asserted), and `TestRunIncrementsDepth`/`TestRunTimesOut` were written to genuinely observe their targets (a real child process's inherited environment; a real timeout-vs-elapsed measurement) rather than describing them.

## Deviations from Plan

None — plan executed exactly as written. The plan's own `<action>` text left the exact form of `TestRunIncrementsDepth` and `TestRunTimesOut` to the executor's judgment ("prefer the simplest form that genuinely observes...", "use a portable slow argv"); the choices made (a `bash -c` child reading back its own env; a `bash -c 'sleep 5'` against a 100ms timeout) are within that latitude, not departures from it.

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required. The compose `postgres` service was already up and healthy from 02-03; this plan's Task 3 reads it via `make gate` and `make test` but does not start, stop, or reconfigure it.

## Next Phase Readiness
- `internal/platform/gate` is Phase 3's confirmed contract: `Run`, `Make`, `RunOptions`, `RunResult`, `SkipIfNested`, `RepoRoot`, `DepthEnv`, `DefaultTimeout` are all present and exercised by real subprocess invocations in this plan, not just declared
- `ROADMAP.md` §Phase 3 now points Phase 3's plan at `gate.Make`/`gate.RunOptions` and the three `RunOptions` shapes PROOF-01/02/03 map onto, rather than leaving Phase 3 to rediscover the tension at `PROJECT.md` lines 91-93
- The compose `postgres` service is left up and healthy, bound to `127.0.0.1:5432` only — unchanged by this plan, available for 02-04
- `make gate` is green end-to-end (verified after this plan's commits); `go build ./...`, `go vet ./...`, `gofmt -l .` clean across the whole repository; `go.mod`/`go.sum` byte-unchanged (harness uses stdlib only)
- No blockers for 02-04 or the GOV-01 closure sweep runbook

---
*Phase: 02-enforcement-and-a-single-gate-definition*
*Completed: 2026-09-02*

## Self-Check: PASSED

All four declared files (`internal/platform/gate/harness.go`,
`internal/platform/gate/harness_test.go`, `internal/platform/gate/makefile_test.go`,
`.planning/ROADMAP.md`) and this SUMMARY.md exist on disk. All three commit
hashes (`e79998c`, `9aa0b95`, `bf4e0c3`) are present in `git log --oneline --all`.
