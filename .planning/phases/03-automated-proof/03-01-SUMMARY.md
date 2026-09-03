---
phase: 03-automated-proof
plan: 01
subsystem: testing
tags: [go, testing, make, subprocess-harness, tar, ci-verification]

# Dependency graph
requires:
  - phase: 02-enforcement-and-a-single-gate-definition
    provides: "internal/platform/gate shell-out-to-make harness (Run/Make/RunOptions/RunResult/SkipIfNested/RepoRoot/DepthEnv/DefaultTimeout), confirmed at a human checkpoint as this phase's contract"
provides:
  - "internal/platform/gateproof, a test-only package proving PROOF-01 and GATE-10 end-to-end through a real nested `make gate`, reaching only gate's exported surface"
  - "The same-line predicate (lineContainsBoth) and shared D-16 guard (requireIntact) every later proof in this phase reuses"
  - "Go tree materialisation (materializeTree, stripEscalationExport) from git archive HEAD via archive/tar — no external archiver, nothing registered in .git — shared by 03-02 and 03-03's controls"
  - "gate.RunOptions.Dir, additive with a zero-value fallback to RepoRoot(t)"
  - "DefaultTimeout's rationale corrected to the measured cold worst case (85s, margin 2.8x) and tagged PROOF-03"
affects: [03-02-closed-port-differential, 03-03-fixture-differential, 03-GOV-SWEEP]

# Actuals (#2632)
actuals:
  tokens: 42000
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Test-only package (_test.go files only) importing a sibling package's exported surface, so the compiler enforces a boundary a code review could only assert"
    - "Same-line predicate over subprocess Combined output, not whole-blob Contains, to rule out tokens that also appear in unrelated help/README/skip text"
    - "SC-5 differential controls as two subtests of one top-level test, sharing a captured RunResult across a *testing.T lineage rather than a package-level var"
    - "Go archive/tar tree materialisation from `git archive --format=tar HEAD`, replacing a bash `mktemp + tar -x` verification snippet with per-test infrastructure"

key-files:
  created:
    - internal/platform/gateproof/gateproof_test.go
    - internal/platform/gateproof/proof01_test.go
    - internal/platform/gateproof/tree_test.go
  modified:
    - internal/platform/gate/harness.go

key-decisions:
  - "Tree materialisation uses git archive --format=tar HEAD piped through Go's stdlib archive/tar, not git worktree add and not an external tar binary (CONTEXT.md D-07's 2026-09-03 correction) — no build-host dependency, nothing left in .git, and go.mod/go.sum stay byte-unchanged"
  - "A condition's proof and its SC-5 control are two subtests of one top-level test function, with the intact RunResult captured in the parent's scope, so ordering is guaranteed and -shuffle=on cannot break the control's dependency on the proof having run first"
  - "lineContainsBoth is deliberately not built on gate's extraLines, which solves a multiset-diff problem rather than a same-line-conjunction one"
  - "Both intact_tree and defeated_tree_control unset testenv.RequireEnv in addition to testenv.URLEnv (deviation from the plan's literal action text, applied identically to both sides to preserve 'the ONLY difference is the stripped export') — found running the real make gate, not the isolated go test"

requirements-completed: [PROOF-01, GATE-10]

coverage:
  - id: D1
    description: "internal/platform/gateproof exists, is test-only, and compiles against internal/platform/gate's exported surface only — a proof needing extraLines, normalizeElapsed, nestingDepth, closedPortDSN, composeDSN or escalationPreamble fails to compile"
    requirement: "PROOF-01"
    verification:
      - kind: unit
        ref: "go build ./... && go vet ./... && gofmt -l ."
        status: pass
      - kind: other
        ref: "grep -nE '(extraLines|normalizeElapsed|nestingDepth|closedPortDSN|composeDSN|escalationPreamble)' internal/platform/gateproof/*_test.go — zero matches"
        status: pass
    human_judgment: false
  - id: D2
    description: "TestPROOF01_GateNamesUnsetURL/intact_tree shells out to a real nested make gate with EPISTEMIC_OS_DB_URL unset, and the escalation preamble + EPISTEMIC_OS_DB_URL land on one line of Combined (GATE-10)"
    requirement: "PROOF-01"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestPROOF01_GateNamesUnsetURL -count=1 -v (against live compose Postgres)"
        status: pass
    human_judgment: false
  - id: D3
    description: "lineContainsBoth is demonstrated able to return false on the adjacent-lines case (D-18), and TestGateproof_NoParallelMarker mechanically pins D-04 by scanning the package's own sources"
    requirement: "GATE-10"
    verification:
      - kind: unit
        ref: "tests/internal/platform/gateproof/gateproof_test.go#TestLineContainsBoth_Control"
        status: pass
      - kind: unit
        ref: "tests/internal/platform/gateproof/gateproof_test.go#TestGateproof_NoParallelMarker"
        status: pass
    human_judgment: false
  - id: D4
    description: "The nested make gate recursion terminates at depth 1 — every test in the package skips when EPISTEMIC_OS_TEST_MAKE_DEPTH is 1 or more"
    verification:
      - kind: integration
        ref: "EPISTEMIC_OS_TEST_MAKE_DEPTH=1 go test ./internal/platform/gateproof/ -count=1 -v — 3 SKIP, 0 FAIL, exit 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "gate.RunOptions gains an additive Dir field with a zero-value fallback to RepoRoot(t); every existing gate-package caller is behaviorally unchanged and buildChildEnv is byte-identical"
    requirement: "PROOF-01"
    verification:
      - kind: unit
        ref: "go test ./internal/platform/gate/ -count=1 -v — same test set, zero skips"
        status: pass
      - kind: other
        ref: "git diff HEAD~4..HEAD -- internal/platform/gate/harness.go shows no changed line inside buildChildEnv"
        status: pass
    human_judgment: false
  - id: D6
    description: "DefaultTimeout's rationale is corrected to the measured cold worst case (85s, margin 2.8x) and tagged PROOF-03, with the stale warm-figure claims removed"
    verification:
      - kind: other
        ref: "grep -c '85' / '2.8' / 'PROOF-03' harness.go all >=1; grep -c '13 seconds' / 'six times' both 0"
        status: pass
    human_judgment: false
  - id: D7
    description: "materializeTree builds a throwaway copy of HEAD from Go using only archive/tar, leaves nothing in .git, and go.mod/go.sum stay byte-unchanged; stripEscalationExport removes exactly one line or fails"
    verification:
      - kind: integration
        ref: "tests/internal/platform/gateproof/tree_test.go#TestMaterializeTree_Control"
        status: pass
      - kind: other
        ref: "git diff --stat -- go.mod go.sum prints nothing"
        status: pass
    human_judgment: false
  - id: D8
    description: "PROOF-01's SC-5 control (defeated_tree_control) runs the same make gate invocation against a copy with the escalation export stripped and observes no escalation preamble there, while the intact side produced one; the differential does not rest on exit code (measured 2 in all six cells)"
    requirement: "PROOF-01"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestPROOF01_GateNamesUnsetURL -count=1 -v — 3 PASS, 0 SKIP"
        status: pass
      - kind: other
        ref: "! grep -nE 'defeated\\.ExitCode' proof01_test.go"
        status: pass
    human_judgment: false
  - id: D9
    description: "The D-16 shared-result guard (requireIntact) has a demonstrated failing path: running the control subtest alone (proof filtered out) fails naming the guard rather than passing vacuously"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run 'TestPROOF01_GateNamesUnsetURL/defeated_tree_control' -count=1 — exit non-zero, names requireIntact"
        status: pass
    human_judgment: false
  - id: D10
    description: "The proof/control ordering does not depend on test execution order"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -count=1 -shuffle=on"
        status: pass
    human_judgment: false
  - id: D11
    description: "The full gate is still green end-to-end with the new package wired in, and the working tree is byte-unchanged by any assertion in this plan"
    requirement: "GATE-10"
    verification:
      - kind: integration
        ref: "make gate (live compose Postgres) — exit 0, includes internal/platform/gateproof's own nested proof run"
        status: pass
      - kind: other
        ref: "git status --porcelain shows only pre-existing, unrelated dirty state (delta-checked against a captured baseline) after every run in this plan"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-03
status: complete
---

# Phase 3 Plan 1: End-to-End PROOF-01 Summary

**`internal/platform/gateproof` proves PROOF-01 and GATE-10 through a real nested `make gate`: the escalation preamble and `EPISTEMIC_OS_DB_URL` land on one line of subprocess output, the harness gains a `Dir` field for tree-scoped runs, and Go's `archive/tar` replaces a bash `git archive` snippet as reusable throwaway-tree infrastructure.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-03T09:37:00Z (approx.)
- **Completed:** 2026-09-03T10:32:27Z
- **Tasks:** 3
- **Files modified:** 4 (3 created, 1 modified)

## Accomplishments

- `internal/platform/gateproof` created as a test-only package that imports `internal/platform/gate` and reaches only its exported surface (`SkipIfNested`, `Run`, `Make`, `RunOptions`, `RunResult`, `RepoRoot`, `DepthEnv`, `DefaultTimeout`) — compiler-enforced, confirmed by grep for every relevant unexported identifier
- `lineContainsBoth` (the same-line predicate GATE-10 depends on) and `requireIntact` (the shared D-16 guard) built with demonstrated failing paths, not just passing ones
- `TestGateproof_NoParallelMarker` mechanically pins D-04 by scanning the package's own `_test.go` files at run time for the parallel-test marker
- `TestPROOF01_GateNamesUnsetURL/intact_tree` shells out to a real nested `make gate` with `EPISTEMIC_OS_DB_URL` unset and proves the escalation preamble and the variable land on one line of `RunResult.Combined`
- `gate.RunOptions` gained an additive `Dir` field (zero value falls back to `RepoRoot(t)`); `DefaultTimeout`'s rationale corrected from stale warm-cache figures to the measured cold worst case (85s, margin 2.8x), tagged `PROOF-03`
- `materializeTree`/`stripEscalationExport` — the first Go implementation of throwaway-tree materialisation via `git archive --format=tar HEAD` read through `archive/tar`, replacing a bash-only pattern from Phase 2's plan verification
- `TestPROOF01_GateNamesUnsetURL/defeated_tree_control` — PROOF-01's SC-5 differential control, reusing the intact side's captured result, discriminating on the escalation preamble (not exit code, measured 2 in all six cells), naming `config`'s own `DB_URL is required` message in the defeated tree
- Full `make gate` verified green end-to-end with the new package wired into the suite it proves

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end PROOF-01 — the proof package proves one condition through every layer** - `f2add33` (feat)
2. **Task 2: The harness gains `Dir`, an honest timeout rationale, and Go tree materialisation** - `e9a973f` (feat)
3. **Task 3: PROOF-01's SC-5 differential control** - `2aa1990` (feat)
4. **Deviation fix (Rule 1), found running the real `make gate`** - `2f6258e` (fix)

_No TDD RED/GREEN/REFACTOR sequence: this is `type="tracer" tdd="true"` and `type="auto" tdd="true"` where the deliverable IS the test suite — each task's commit is its own verified, working slice._

## Files Created/Modified

- `internal/platform/gateproof/gateproof_test.go` - Package spine: `unreachableDSN`, `fixturePathSuffix`, `lineContainsBoth`, `requireIntact`, `TestLineContainsBoth_Control`, `TestGateproof_NoParallelMarker`
- `internal/platform/gateproof/proof01_test.go` - `TestPROOF01_GateNamesUnsetURL` with `intact_tree` and `defeated_tree_control` subtests
- `internal/platform/gateproof/tree_test.go` - `materializeTree`, `stripEscalationExport`, `TestMaterializeTree_Control`
- `internal/platform/gate/harness.go` - `RunOptions.Dir` field (additive); `DefaultTimeout` rationale corrected and tagged `PROOF-03`

## Decisions Made

- Tree materialisation via `git archive --format=tar HEAD` + stdlib `archive/tar`, not `git worktree add` and not an external `tar` binary (CONTEXT.md discretion note 1) — no build-host dependency, nothing registered in `.git`, `go.mod`/`go.sum` byte-unchanged
- Proof and SC-5 control as two subtests of one top-level test, sharing a captured `RunResult` in the parent's scope (discretion note 2) — guaranteed ordering under `-shuffle=on`, and the D-16 guard has a genuinely trippable failing path
- `lineContainsBoth` built as its own function rather than reusing `gate.extraLines`, which solves multiset-diff, not same-line-conjunction (discretion note 3)
- Each control materialises its own tree copy rather than sharing across tests (discretion note 4) — the sharing cheap-path this phase's `Claude's Discretion` section allowed does not apply once the copy is also mutated per condition

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `archive/tar` reader surfaces git's pax global header as an unsupported entry**
- **Found during:** Task 2 (`TestMaterializeTree_Control`)
- **Issue:** `git archive --format=tar HEAD` always emits one `pax_global_header` entry ahead of the 230 tracked files, carrying commit metadata as an archive-format artifact rather than tracked content. `archive/tar`'s `Reader.Next()` does not fold a *global* pax header (`tar.TypeXGlobalHeader`) into the following entry the way it does a per-entry pax header, so it surfaced as an "unsupported type flag" hard failure.
- **Fix:** Added an explicit `case tar.TypeXGlobalHeader: continue` in the extraction loop's switch, with a comment recording why this is not a weakening of the entry-kind guard — it is an archive-format artifact, not tracked content, and the guard's strictness against genuinely unexpected entry kinds (symlinks, devices, etc.) is unchanged.
- **Files modified:** `internal/platform/gateproof/tree_test.go`
- **Verification:** `TestMaterializeTree_Control` passes; the resulting tree still contains exactly the same 230 tracked files.
- **Committed in:** `e9a973f` (Task 2 commit)

**2. [Rule 1 - Bug] The SC-5 differential leaked escalation from the calling process's ambient environment**
- **Found during:** Task 3, running the real `make gate` (not the isolated `go test` invocation the plan's action text was verified against)
- **Issue:** The outer `make gate`'s own target-scoped `EPISTEMIC_OS_TEST_REQUIRE_ENV=make-gate` export lands in the ambient environment of the `go test ./...` process that runs `internal/platform/gateproof`'s tests at depth 0. `gate.RunOptions.Unset` (as authored per the plan's action text, `[]string{testenv.URLEnv}` only) did not remove that variable, and `buildChildEnv` passes any name not in `Unset`/`Env` straight through from `os.Environ()`. The defeated-tree control's nested `gate.Run` therefore inherited escalation from the calling context rather than from the (correctly stripped) copy's own Makefile, defeating the differential for a reason unrelated to the stripped export — the exact "reword/coupling breaks silently" defect class this milestone exists to catch, caught here by actually running the real gate rather than only the isolated test.
- **Fix:** Both `intact_tree` and `defeated_tree_control` now also unset `testenv.RequireEnv`, so each nested `make gate`'s escalation state is decided solely by that copy's own Makefile. Applied identically to both sides to preserve the plan's stated invariant that Unset is the same on both sides and the stripped export is the only difference. Harmless for `intact_tree`: D-11 measured the copy's own `gate:` target-scoped export to override a conflicting caller-set value regardless.
- **Files modified:** `internal/platform/gateproof/proof01_test.go`
- **Verification:** Standalone `go test ./internal/platform/gateproof/ -count=1 -shuffle=on` still passes; a full `make gate` run (vet, gofmt, build, env-preflight, migrate, test — including this package's own nested proof) is green end-to-end.
- **Committed in:** `2f6258e` (separate fix commit, after Task 3's own commit, since the discrepancy only surfaced running the full gate afterward)

---

**Total deviations:** 2 auto-fixed (2 bugs, both Rule 1)
**Impact on plan:** Both fixes were necessary for the proof to hold under its own stated success criterion ("make gate is still green with the compose database up"). No scope creep — no must-have, artifact, or prohibition was weakened; the second fix strengthens the differential's hermeticity, which is exactly what D-11/D-14/D-16 exist to protect.

## Issues Encountered

None beyond the two deviations above, both found and resolved during this plan's own execution.

## User Setup Required

None - no external service configuration required. The plan's precondition (`make planning-parity PHASE=3`) was verified green before any task began, and the compose PostgreSQL was already up and healthy.

## Next Phase Readiness

- `internal/platform/gateproof`'s shared spine (`lineContainsBoth`, `requireIntact`, tree materialisation) is in place for 03-02 (PROOF-02) and 03-03 (PROOF-03) to add new files to, touching no file this plan created, per this plan's own success criterion.
- `gate.RunOptions.Dir` and the corrected `DefaultTimeout` rationale are available to both follow-on plans without further harness changes.
- No blockers. `go build ./...`, `go vet ./...`, `gofmt -l .` are clean, exactly four files changed against the phase base, `go.mod`/`go.sum` are byte-unchanged, and `git status --porcelain` carries no delta introduced by this plan.

---
*Phase: 03-automated-proof*
*Completed: 2026-09-03*
