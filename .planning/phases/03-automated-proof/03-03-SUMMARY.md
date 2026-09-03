---
phase: 03-automated-proof
plan: 03
subsystem: testing
tags: [go, testing, make, subprocess-harness, differential-control, fixture-defeat]

# Dependency graph
requires:
  - phase: 03-automated-proof
    plan: 01
    provides: "internal/platform/gateproof spine (materializeTree, stripEscalationExport, lineContainsBoth, requireIntact) and gate.RunOptions.Dir"
  - phase: 03-automated-proof
    plan: 02
    provides: "PROOF-02's proof/control shape and D-15's reporter-identity discipline (do not bind to a dependency's or a co-failure's prose)"
provides:
  - "TestPROOF03_GateNamesUnreadableFixture (intact_tree + defeated_tree_control), proving PROOF-03 end-to-end through a real nested make gate"
  - "breakFixture, the condition-specific defeat: replaces demo.md with a directory inside a materializeTree copy, refusing the real repo root and a non-regular-file target"
  - "All three SC-5 differential controls now exist (PROOF-01, PROOF-02, PROOF-03), completing the phase's proof of GATE-10 on all three escalated paths"
affects: [03-04-governance, 03-GOV-SWEEP]

# Actuals (#2632)
actuals:
  tokens: 2991
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The intact side of a proof can itself be a copy when the condition cannot be reproduced in the real tree without mutating it — PROOF-03 is the only one of the three conditions where this applies, because the fixture read is a filesystem condition rather than an environment-variable one"
    - "A condition-specific defeat helper (breakFixture) mirrors stripEscalationExport's shape: refuse the real repo root, refuse a target that would make the defeat a silent no-op, fail loudly otherwise"

key-files:
  created:
    - internal/platform/gateproof/proof03_test.go
  modified: []

key-decisions:
  - "PROOF-03 and its SC-5 control both unset testenv.RequireEnv (deviation from this plan's literal action text, carried forward from 03-01's Task 3 finding and 03-02's identical carry-forward) — the outer make gate's own target-scoped export leaks into the ambient environment of any nested gate.Run call that does not explicitly unset it, defeating the SC-5 differential for a reason unrelated to the stripped export. Found running the real make gate, not the isolated go test — the exact same defect class 03-01 found in the same spot."
  - "GATE-10 stays Pending after PROOF-03 lands. 03-04-PLAN.md also declares GATE-10 in its own requirements frontmatter and has not yet produced a SUMMARY, so the shared-ID gate (#2388) blocks marking it complete until the last declaring plan finishes — even though all three escalated paths (PROOF-01/02/03) are now individually proven. See 'GATE-10 Evaluation' below for the full reasoning."

requirements-completed: [PROOF-03]

coverage:
  - id: D1
    description: "breakFixture(t, root) replaces demo.md with a directory inside a materializeTree copy, refusing a root equal to the real repository and refusing a target that is not a pre-existing regular file, so the defeat cannot silently no-op against an already-broken or moved fixture"
    requirement: "PROOF-03"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestPROOF03_GateNamesUnreadableFixture -count=1 -v (against live compose Postgres)"
        status: pass
      - kind: other
        ref: "falsifiability demonstration — breakFixture temporarily no-op'd, vacuity guard fired naming the exact condition (captured below), reverted before commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "TestPROOF03_GateNamesUnreadableFixture/intact_tree shells out to a real nested make gate against a copy with the fixture broken and the escalation export intact, and the escalation preamble plus the fixture path's common suffix land on one line of Combined (GATE-10)"
    requirement: "PROOF-03"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestPROOF03_GateNamesUnreadableFixture/intact_tree -count=1 -v"
        status: pass
    human_judgment: false
  - id: D3
    description: "The assertion binds to the common path suffix (core/domain/segment/testdata/demo.md), never to either full spelling and never to the platform's errno text for reading a directory as a file (D-17, prohibitions)"
    requirement: "PROOF-03"
    verification:
      - kind: other
        ref: "grep -c 'fixturePathSuffix' proof03_test.go >= 1; ! grep -n the call-site literal; ! grep -nEi '(is a directory|incorrect function|EISDIR)' proof03_test.go"
        status: pass
    human_judgment: false
  - id: D4
    description: "PROOF-03's SC-5 control (defeated_tree_control) runs the same make gate invocation against a copy defeated twice — escalation export stripped AND fixture broken — and observes no escalation preamble there, while the intact side (captured, not re-run) produced one; no assertion on the defeated side's exit code or on segment's own hash-pin reporter text (D-11, D-13, D-14)"
    requirement: "PROOF-03"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestPROOF03_GateNamesUnreadableFixture -count=1 -v — 3 PASS, 0 SKIP"
        status: pass
      - kind: other
        ref: "grep -c 'materializeTree(' == 2; grep -c 'breakFixture(' == 3; grep -c 'stripEscalationExport(' == 1; ! grep -nE 'defeated\\.ExitCode'; grep -c 'D-13' >= 1"
        status: pass
    human_judgment: false
  - id: D5
    description: "The D-16 shared-result guard (requireIntact) has a demonstrated failing path: running defeated_tree_control alone (proof filtered out) fails naming requireIntact rather than passing vacuously"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run 'TestPROOF03_GateNamesUnreadableFixture/defeated_tree_control' -count=1 — exit non-zero, names requireIntact"
        status: pass
    human_judgment: false
  - id: D6
    description: "The proof/control ordering does not depend on test execution order, and all three proofs plus all three SC-5 controls pass together"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -count=1 -shuffle=on -v — all PASS, 0 SKIP, 0 FAIL (117.55s)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The real working-tree demo.md is never touched — byte-identical before and after every run — and no bypass was added to internal/platform/testenv"
    requirement: "PROOF-03"
    verification:
      - kind: other
        ref: "git status --porcelain empty; git diff --stat -- internal/core/domain/segment/testdata/demo.md, go.mod, go.sum, Makefile, internal/platform/testenv/ all print nothing, checked after every run in this plan including the failing one"
        status: pass
    human_judgment: false
  - id: D8
    description: "The full gate is still green end-to-end with PROOF-03 and its control wired in, and the compose PostgreSQL service was never stopped"
    requirement: "PROOF-03"
    verification:
      - kind: integration
        ref: "make gate (live compose Postgres) — exit 0, includes internal/platform/gateproof's own nested proof run (143.4s of the run)"
        status: pass
      - kind: other
        ref: "docker compose ps postgres — Up (healthy) before and after every run in this plan"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-03
status: complete
---

# Phase 3 Plan 3: PROOF-03 and Its SC-5 Differential Control Summary

**`TestPROOF03_GateNamesUnreadableFixture` proves the gate fails and names the fixture path on one line when `internal/core/domain/segment/testdata/demo.md` is unreadable — defeated as a directory (never a deletion) inside a throwaway copy so the real working tree is never touched — with an SC-5 differential control against a copy defeated twice (escalation export stripped AND fixture broken), completing all three of GATE-10's escalated paths.**

## Performance

- **Duration:** 55 min
- **Started:** ~2026-09-03T14:38:32Z (continuation from 03-02's completion)
- **Completed:** 2026-09-03T15:33:52Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- `breakFixture(t, root)` replaces `demo.md` with a directory inside a `materializeTree` copy, refusing a root equal to the real repository and refusing a target that is not a pre-existing regular file — a defeat that could otherwise silently no-op and pass PROOF-03 against an intact tree
- `TestPROOF03_GateNamesUnreadableFixture/intact_tree` shells out to a real nested `make gate` with the fixture broken and the escalation export intact, and proves the escalation preamble and the fixture path's common suffix (`core/domain/segment/testdata/demo.md`) land on one line of `RunResult.Combined` (GATE-10)
- `TestPROOF03_GateNamesUnreadableFixture/defeated_tree_control` — PROOF-03's SC-5 differential control, against a copy defeated on **both** axes (escalation export stripped and fixture broken), discriminating on the escalation preamble rather than the exit code (D-14 measured exit 2 in all six cells of the intact/defeated matrix across the phase, including this one, because `segment`'s own hash-pinned reads fail hard regardless of escalation)
- The assertion binds to the path suffix, never to either full spelling of the fixture path and never to the operating system's errno text for reading a directory — verified by grep and by reading the file
- The real working-tree `demo.md` was never opened for writing, removed, or renamed — `git status --porcelain` and a targeted `git diff --stat` on the fixture stayed empty through every run in this plan, including the one that failed
- All three proofs (PROOF-01, PROOF-02, PROOF-03) and all three SC-5 controls pass together under `go test ./internal/platform/gateproof/ -count=1 -shuffle=on` (117.55s), and `make gate` is green end-to-end against the live compose database

## Task Commits

Each task was committed atomically:

1. **Task 1: PROOF-03 — the gate names the fixture path when the fixture is unreadable** - `bd45410` (feat)
2. **Task 2: PROOF-03's SC-5 differential control — a copy defeated twice** - `97fe596` (feat)

_No TDD RED/GREEN/REFACTOR sequence: `type="auto" tdd="true"` where the deliverable IS the test suite — each task's commit is its own verified, working slice, matching 03-01's and 03-02's pattern. The Rule 1 fix below (the `Unset` deviation) was applied and verified before either commit, so both commits already carry the corrected code — there is no separate fix commit._

## Files Created/Modified

- `internal/platform/gateproof/proof03_test.go` — `breakFixture` and `TestPROOF03_GateNamesUnreadableFixture` with `intact_tree` and `defeated_tree_control` subtests

## Decisions Made

- Tree materialisation and the escalation-strip helper were reused unchanged from `internal/platform/gateproof/tree_test.go` (03-01) — no file this plan created or modified touches any file 03-01 or 03-02 authored, per this plan's own success criterion.
- The control materialises its own copy rather than sharing the proof's copy (03-01's discretion note 4) — a control needing a *differently* defeated tree gets its own, since a copy with only the escalation strip would fail for a different reason entirely (`segment`'s own hash-pinned read) and would not be a control for PROOF-03's condition.
- No reporter-identity assertion was added to the control (matching D-15's discipline from 03-02): the reporter in the doubly-defeated cell is `segment`'s own hash pin, which is this project's text but is **not** the condition PROOF-03 names, so asserting it would couple the control to an incidental co-failure rather than to the requirement.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The SC-5 differential leaked escalation from the calling process's ambient environment**
- **Found during:** Running the real `make gate` end-to-end after both tasks were implemented and verified in isolation (not during the isolated `go test ./internal/platform/gateproof/` runs, which never exercise this path because they are not themselves invoked from inside a real depth-0 `make gate`)
- **Issue:** This plan's action text specified no `Env`/`Unset` overrides for the database on either subtest (correct, since the fixture condition requires the database to be fine). But when `TestPROOF03_GateNamesUnreadableFixture` itself runs under a real outer `make gate`, that outer gate's own target-scoped export (`gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate`) lands in the ambient environment of the `go test ./...` process running `gateproof`'s tests at depth 0, and `gate.RunOptions.Unset` — left empty on both subtests as literally specified — did not remove it. `buildChildEnv` passes any name not in `Unset`/`Env` straight through, so the defeated-tree control's nested `gate.Run` inherited escalation from the calling context rather than from the (correctly stripped) copy's own Makefile, defeating the differential for a reason unrelated to the stripped export. Captured directly from a real `make gate` run: `defeated_tree_control` failed because the escalation preamble was still present in the doubly-defeated copy's output, alongside 16 real test failures inside that copy's own nested suite (`segment`'s hash-pinned reads and `store`'s cross-package fixture read, both hitting the directory-fixture as expected) — this is exactly 03-01's Task 3 finding, in the same spot, in a different plan.
- **Fix:** Both `intact_tree` and `defeated_tree_control` now unset `testenv.RequireEnv` in addition to leaving the database untouched, so each nested `make gate`'s escalation state is decided solely by that copy's own Makefile. Applied identically to both sides to preserve the invariant that the stripped export is the *only* difference between the two copies. Harmless for `intact_tree` — D-11 measured this copy's own `gate:` target-scoped export to override a conflicting caller-set value regardless — but it makes the intact side control its own environment rather than depend on ambient state, matching the defeated side where it is load-bearing.
- **Files modified:** `internal/platform/gateproof/proof03_test.go` (both `gate.Run` calls)
- **Verification:** Re-ran the isolated test (`-run TestPROOF03_GateNamesUnreadableFixture -count=1 -v`, PASS, 62.7s), the `-shuffle=on` full-package run (PASS, 117.6s), and a full `make gate` against the live compose database (exit 0, `internal/platform/gateproof` at 143.4s within it) — all green after the fix, with `git status --porcelain` and a targeted diff on `demo.md` staying empty throughout.
- **Committed in:** `bd45410` and `97fe596` — the fix was found and applied before either task's first commit, so both commits already carry the corrected `Unset` calls; there is no separate fix commit (unlike 03-01, where the fix landed after Task 3's own commit).

---

**Total deviations:** 1 auto-fixed (1 bug, Rule 1)
**Impact on plan:** The fix was necessary for the control to hold under its own stated success criterion ("`make gate` is green end to end") — without it, a real depth-0 `make gate` run would fail this package's own tests, which is a gate that fails for a reason unrelated to any of the three conditions it exists to prove. No must-have, artifact, or prohibition was weakened; this is the third instance of the exact same defect class (03-01 found it first, 03-02 carried the fix forward, this plan found it again in a new call site and carried it forward the same way).

## Issues Encountered

One anomalous timing event, not reproduced on retry and not treated as a defect: an early `go test ./internal/platform/gateproof/ -count=1 -shuffle=on` run (before the `Unset` fix, run without an explicit `-timeout`) printed a goroutine dump and exited non-zero at 828.9s — consistent with `go test`'s own default 10-minute-per-package watchdog, not with a deadlock in this package's own code (all subtests up to that point had themselves completed and printed `PASS`). Re-run twice after the fix, the same command completed cleanly in 116–118s both times, well inside the default timeout. Recorded here rather than silently discarded, in case the pattern recurs — it is not currently understood, and no fix was attempted because the reproducible runs are all green. Not filed as a Rule 1/3 fix because it never reproduced against the corrected code and touches no file this plan is scoped to change.

## GATE-10 Evaluation

**All three escalated paths are now proven** (PROOF-01, PROOF-02, PROOF-03), which is the substantive condition GATE-10's text names: "The escalation preamble and the named cause MUST be delivered in a single message ... on all three escalated paths." Measured directly in this plan's own runs: all three proofs' single content assertions bind to `lineContainsBoth`, requiring the preamble and the cause on one line, and all three now pass.

**GATE-10 is nonetheless left `Pending` in REQUIREMENTS.md**, not marked complete by this plan. The mechanical reason: `03-04-PLAN.md` also declares `GATE-10` in its own `requirements` frontmatter field and has not yet produced a `*-SUMMARY.md`. The shared-ID gate (issue #2388, `requirements.ready-ids`) exists precisely to stop the first of several plans declaring the same requirement ID from flipping it `Complete` while a sibling plan is still outstanding — closing it here, before 03-04 has run its own verification of "the already-landed SC-5 correction and GATE-10 amendment" (ROADMAP's own words for what 03-04 does), would let a governance-verification step run against an already-closed requirement, which is the reviewability the gate exists to preserve. Run mechanically: `gsd-tools query requirements.ready-ids` returned `PROOF-03` ready and `GATE-10` blocked, and only `PROOF-03` was marked complete.

This is not a claim that GATE-10's substance is unproven — it is proven, by this plan's own tests, right now. It is a claim that the requirement's formal closure correctly waits for the plan whose stated job is to verify that closure.

## User Setup Required

None - no external service configuration required. The compose PostgreSQL was already up and healthy throughout this plan, and was never stopped.

## Next Phase Readiness

- All three of Phase 3's conditions (PROOF-01, PROOF-02, PROOF-03) and all three SC-5 differential controls now exist and pass together, in any top-level order, under `-shuffle=on`.
- `internal/platform/gateproof` is otherwise unchanged from 03-01/03-02's contributions — no file either of those plans created or modified was touched by this plan.
- `go build ./...`, `go vet ./...`, `gofmt -l .` are all clean; `go.mod`, `go.sum`, `Makefile`, `internal/platform/testenv/`, and the real `internal/core/domain/segment/testdata/demo.md` are all byte-unchanged.
- 03-04 (Governance) is unblocked: its job is to verify the already-landed SC-5 correction and the GATE-10 amendment, and to close GATE-10 once its own verification lands — this plan's proofs are the substantive evidence that verification will confirm.
- No blockers.

---
*Phase: 03-automated-proof*
*Completed: 2026-09-03*

## Self-Check: PASSED

- `internal/platform/gateproof/proof03_test.go` verified present on disk with `[ -f ]`.
- Both commits (`bd45410`, `97fe596`) verified present via `git log --oneline --all`.
- Every task's acceptance criteria re-run and passing against the final committed content (byte-identical to what was fully tested: 233 lines, confirmed via line count and hash before and after the two-commit split).
- Plan-level `<verification>` re-run at the final committed HEAD (`97fe596`): `go test ./internal/platform/gateproof/ -count=1 -shuffle=on -v` — all PASS, 0 SKIP, 0 FAIL (117.55s); `make gate` — exit 0 against live compose Postgres, includes `gateproof`'s own nested proof run; `git status --porcelain` and a targeted `demo.md`/`go.mod`/`go.sum`/`Makefile`/`internal/platform/testenv/` diff both empty.
