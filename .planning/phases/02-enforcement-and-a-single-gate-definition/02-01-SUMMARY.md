---
phase: 02-enforcement-and-a-single-gate-definition
plan: 01
subsystem: testing
tags: [makefile, go-test, ci-gate, pgx, golang-migrate]

# Dependency graph
requires:
  - phase: 01-escalation-mechanism-and-fixture-invariant
    provides: "internal/platform/testenv (Pool, Fixture, Required, hostFromURL, unparseableURLMsg) — the single skip-or-fail decision point for every database-backed test, with escalation opt-in but unwired"
provides:
  - "testenv.RequireEnv renamed to EPISTEMIC_OS_TEST_REQUIRE_ENV, identifier unchanged"
  - "escalationPreamble(): one shared message builder used by all three escalated failure paths"
  - "renameTripwireMsg(): permanent guard against the stale EPISTEMIC_OS_TEST_REQUIRE_DB name"
  - "Makefile env-preflight target: reaches testenv.Pool's escalated path before migrate can run"
  - "Makefile gate target reshaped to a strict gate: vet -> gofmt -> build -> env-preflight -> migrate -> test, target-scoped EPISTEMIC_OS_TEST_REQUIRE_ENV=make-gate export, no database-starting path"
  - "make test lenient-run banner; make help corrected to no longer claim a static gate"
affects: [02-02-shell-out-harness, 02-03-ci-collapse-and-sec-01, 03-01-automated-proof]

# Actuals (#2632)
actuals:
  tokens: 4400
  tasks: 3
  commits: 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Argument-free / parameter-decides-branch-only message builders (escalationPreamble, renameTripwireMsg) — no fmt verbs, no interpolation of caller-controlled values, extending the unparseableURLMsg discipline from Phase 1"
    - "Target-scoped Make export (`gate: export VAR = value`) to inject a caller-identifying flag value into a recipe and its $(MAKE) sub-invocations, overriding any conflicting caller environment"
    - "$(MAKE) target reuse over recipe-body duplication (gate calls $(MAKE) migrate / $(MAKE) test rather than re-pasting their bodies)"

key-files:
  created: []
  modified:
    - internal/platform/testenv/testenv.go
    - internal/platform/testenv/testenv_test.go
    - Makefile

key-decisions:
  - "D-09's stale package-doc paragraph replaced in the same commit as the RequireEnv value rename, not a follow-up commit"
  - "Tripwire checked before every other branch in both Pool and Fixture (top of function), matching D-08's ordering requirement"
  - "Task 2 step 5a's verify-script literal corrected from EPISTEMIC_OS_TEST_REQUIRE_ENV=\"gate03\" to \"make-gate\" when running through `make gate` — D-11's own measured ground truth (target-scoped export overrides a conflicting caller value) makes the plan's original literal structurally unobservable; the substance of the check (both strings, proven by running it) is unchanged"

patterns-established:
  - "Pattern 1: every escalated t.Fatalf in testenv speaks through escalationPreamble() first, so a future fourth escalated path has an obvious, enforced place to plug into (GATE-06 message contract)"
  - "Pattern 2: rename tripwires are permanent and self-explaining in the failure text, not just a code comment, following internal/platform/config/config.go's precedent"

requirements-completed: [GATE-01, GATE-02, GATE-03, GATE-06, GATE-07]
# GATE-08 and GOV-01 are listed in this plan's own frontmatter `requirements:`
# field but are each only PARTIALLY satisfied here — see the "Requirements
# marked complete, then corrected" note under Deviations. Not included above
# because REQUIREMENTS.md's traceability table tracks them as still Pending.

coverage:
  - id: D1
    description: "make gate fails with EPISTEMIC_OS_DB_URL unset and names that variable (GATE-01)"
    requirement: "GATE-01"
    verification:
      - kind: integration
        ref: "env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate (Task 1 verify step 4)"
        status: pass
    human_judgment: false
  - id: D2
    description: "make gate fails against an unreachable database, naming the host and carrying the remedy in the same sentence (GATE-02)"
    requirement: "GATE-02"
    verification:
      - kind: integration
        ref: "EPISTEMIC_OS_TEST_REQUIRE_ENV=make-gate EPISTEMIC_OS_DB_URL=postgres://u:pw@127.0.0.1:1/nodb make gate (Task 2 verify step 3b)"
        status: pass
    human_judgment: false
  - id: D3
    description: "make gate fails with a fixture unreadable, naming the fixture path (GATE-03), proven by moving internal/core/domain/segment/testdata/demo.md aside against a live database"
    requirement: "GATE-03"
    verification:
      - kind: integration
        ref: "Task 2 verify step 5a (literal corrected to EPISTEMIC_OS_TEST_REQUIRE_ENV=\"make-gate\" per D-11 — see Deviations)"
        status: pass
    human_judgment: false
  - id: D4
    description: "All three escalated failures share one preamble naming EPISTEMIC_OS_TEST_REQUIRE_ENV and printing its value, quoted (GATE-06)"
    requirement: "GATE-06"
    verification:
      - kind: unit
        ref: "internal/platform/testenv/testenv_test.go#TestEscalationPreamble"
        status: pass
      - kind: integration
        ref: "Task 1 step 4 + Task 2 steps 2/3/5 (all three paths run, not grepped)"
        status: pass
    human_judgment: false
  - id: D5
    description: "testenv.RequireEnv's value is EPISTEMIC_OS_TEST_REQUIRE_ENV; exported identifier RequireEnv unchanged (GATE-07)"
    requirement: "GATE-07"
    verification:
      - kind: unit
        ref: "internal/platform/testenv/testenv_test.go#TestRequired (unedited, still passes against renamed constant)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Rename tripwire: EPISTEMIC_OS_TEST_REQUIRE_DB set while EPISTEMIC_OS_TEST_REQUIRE_ENV is unset fails naming the rename and stating why the check is permanent (D-08, D-10)"
    verification:
      - kind: unit
        ref: "internal/platform/testenv/testenv_test.go#TestRenameTripwireMsg, #TestRenameTripwireMsg_Control_DetectsTheTripwireCase"
        status: pass
      - kind: integration
        ref: "Task 2 verify step 2 (EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/approved/)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Makefile help target no longer claims a static gate; states the database requirement and describes make test as lenient (GATE-08, Makefile half only — README half is 02-03, not this plan)"
    requirement: "GATE-08"
    verification:
      - kind: integration
        ref: "Task 3 verify steps 1-3 (make test banner, make help text)"
        status: pass
    human_judgment: true
    rationale: "GATE-08 is a single two-part requirement ((a) README, (b) Makefile help). This plan delivers only (b); REQUIREMENTS.md keeps GATE-08 Pending until 02-03 lands (a). Not auto-passable as a requirement-level deliverable even though the Makefile half is itself fully proven."
  - id: D8
    description: "make gate never starts a database and demands one; migrate/test invoked via $(MAKE), not by re-pasting bodies (D-01, D-02, D-06)"
    verification:
      - kind: unit
        ref: "awk '/^gate:/,/^$/' Makefile | grep -c 'docker compose' == 0; grep -c '^gate: up' Makefile == 0"
        status: pass
    human_judgment: false
  - id: D9
    description: "env-preflight strictly before $(MAKE) migrate in the gate recipe, so testenv (not store.RunMigrations) is the first reporter for an unreachable database (D-03)"
    verification:
      - kind: unit
        ref: "structural awk-based line-number ordering check, Task 1 verify step 5 + Task 2 verify step 3b"
        status: pass
    human_judgment: false
  - id: D10
    description: "GOV-01 phase-start check (one of two required runs, D-12): ROADMAP.md Phase 2 requirement set equals REQUIREMENTS.md's Phase 2 traceability table"
    requirement: "GOV-01"
    verification:
      - kind: manual_procedural
        ref: "Task 1 precondition — both sets read and diffed: 10 IDs, identical in both directions"
        status: pass
    human_judgment: true
    rationale: "GOV-01's own requirement text states Phase 2 does not close until the post-checkpoint stale-artifact sweep (02-GOV-SWEEP-RUNBOOK.md) runs, after every plan, UAT and security sign-off. This plan satisfies only the phase-start half of D-12's two required runs. REQUIREMENTS.md keeps GOV-01 Pending until the closure sweep lands."

duration: 21min
completed: 2026-09-02
status: complete
---

# Phase 2 Plan 1: Enforcement Core Summary

**Renamed the escalation flag to EPISTEMIC_OS_TEST_REQUIRE_ENV, gave all three escalated `testenv` failure paths one shared preamble naming the flag and its value, armed a permanent rename tripwire, and reshaped `make gate` into a strict gate whose voiceless preflight reports before `migrate` can.**

## Performance

- **Duration:** 21 min (commit-to-commit; base `dfd1db6` to `faad2ef`)
- **Started:** 2026-09-02T06:26:00Z
- **Completed:** 2026-09-02T06:47:07Z
- **Tasks:** 3 completed
- **Files modified:** 3 (`internal/platform/testenv/testenv.go`, `internal/platform/testenv/testenv_test.go`, `Makefile`)

## Accomplishments
- `make gate` now demands a running PostgreSQL and fails loudly — naming the unset variable, the unreachable host with remedy, or the unreadable fixture path — instead of silently reporting ok on a suite that skipped everything
- All three escalated failures speak with one voice: `escalationPreamble()` is the single builder every `t.Fatalf` in `testenv` calls, printing the flag name and its `%q`-quoted value
- `EPISTEMIC_OS_TEST_REQUIRE_DB` is permanently guarded: a stale export of the old name with the new one unset fails loudly, naming the rename and explaining why the check never retires
- `env-preflight` inserts a voiceless, unfiltered reachability check ahead of `migrate`, so `testenv` — not `golang-migrate`'s unaudited `new migrator: %w` — is the first thing a developer reads when the database is unreachable
- `make test` now announces it is the lenient run; `make help` no longer claims "Full static gate"

## Task Commits

Each task was committed with a RED/GREEN TDD pair (tasks carried `tdd="true"`):

1. **Task 1: End-to-end strict gate for the unset-URL path**
   - `18624fc` (test) — add `TestPoolReachesDatabase`, `TestEscalationPreamble` (RED: `escalationPreamble` undefined)
   - `65fb8c0` (feat) — rename `RequireEnv`'s value, add `legacyRequireEnv`/`escalationPreamble`, correct package doc comment, add `env-preflight` target, reshape `gate` (GREEN)
2. **Task 2: Expand the shared preamble, arm the rename tripwire**
   - `e8faa6a` (test) — add `TestRenameTripwireMsg`, `TestRenameTripwireMsg_Control_DetectsTheTripwireCase` (RED: `renameTripwireMsg` undefined)
   - `190c125` (feat) — add `renameTripwireMsg`, wire it at the top of `Pool`/`Fixture`, apply `escalationPreamble()` to the remaining two escalated sites, extend `Pool`'s doc comment (GREEN)
3. **Task 3: Lenient-run banner and corrected help text**
   - `faad2ef` (feat) — `make test` banner, `make help` correction

**Plan metadata:** this commit (docs: complete plan)

_All five task commits carry the RED-then-GREEN TDD gate. No REFACTOR commit was needed — both GREEN commits landed clean._

## Files Created/Modified
- `internal/platform/testenv/testenv.go` — `RequireEnv` renamed, `legacyRequireEnv` and `escalationPreamble()` added, `renameTripwireMsg()` added and wired at the top of `Pool`/`Fixture`, all three escalated `t.Fatalf` sites now speak through `escalationPreamble()`, package doc comment corrected
- `internal/platform/testenv/testenv_test.go` — `TestPoolReachesDatabase`, `TestEscalationPreamble`, `TestRenameTripwireMsg`, `TestRenameTripwireMsg_Control_DetectsTheTripwireCase` added; file-level doc comment recording D-04's accepted cost
- `Makefile` — new `env-preflight` target; `gate` reshaped to `vet -> gofmt -> build -> $(MAKE) env-preflight -> $(MAKE) migrate -> $(MAKE) test` with target-scoped `export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate`; `test` gains the lenient-run banner; `help` corrected

## Decisions Made
- Followed the plan's TDD structure literally: for each `tdd="true"` task, tests were committed first in a state proven to fail to compile (RED — `escalationPreamble`/`renameTripwireMsg` undefined), then the implementation commit made them pass (GREEN). No REFACTOR commit was needed.
- `renameTripwireMsg`'s message text extends `internal/platform/config/config.go`'s "name the rename, not the absence" shape per D-10, carrying its own reasoning (why the rename happened, that the old name is not honored, why the check is permanent, what to do) directly in the failure text rather than only in a comment.
- Correction plan gap: see Deviations below for Task 2 step 5a's literal fix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — plan verify-script defect, not a code defect] Corrected the expected flag value in Task 2 step 5a's `make gate` assertion**
- **Found during:** Task 2, verify step 5a (GATE-03 proven at the gate)
- **Issue:** The plan's verify script sets `EPISTEMIC_OS_TEST_REQUIRE_ENV=gate03` in the invoking shell and then asserts that `make gate`'s output contains `EPISTEMIC_OS_TEST_REQUIRE_ENV="gate03"`. But `gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate` (D-11, added in Task 1, exactly as specified) is a target-scoped export, and the plan's own "Verified ground truth" section had already measured that such an export "overrides a conflicting value already exported in the caller's environment." Running the check confirmed this empirically: the message inside `make gate`'s output read `EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"`, never `"gate03"` — the literal the verify script named can never appear in that position given the implementation the same plan specifies in D-11.
- **Fix:** Confirmed the assertion's *substance* — `make gate` fails, and the failure carries both `fixture not readable at` (with the fixture path) and the shared escalation preamble naming the flag and its value — by running it with the corrected expected literal `EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"`. No code change; no weakening of what the check proves (both strings, proven by genuinely moving the fixture aside against a live database, not grepped). Step 5 (the package-level check, run directly with `go test`, not through `make gate`) is unaffected — `gate03` correctly appears there since no target-scoped export intervenes.
- **Files modified:** none (verification-only; no production or test code changed for this deviation)
- **Verification:** Task 2's full step 5/5a/5b/5c sequence run end-to-end in one shell session (required for the fixture-restoration trap to survive across the whole sequence); tree confirmed byte-identical to HEAD afterward via `git diff --quiet`
- **Committed in:** documented in `190c125`'s commit message; no separate commit needed since no file changed

**2. [Rule 2 — governance-record correctness] Reverted premature GATE-08/GOV-01 completion marks in REQUIREMENTS.md**
- **Found during:** post-execution `requirements mark-complete` step
- **Issue:** This plan's own frontmatter `requirements:` field lists `GATE-08` and `GOV-01` alongside the five requirements it fully satisfies. Mechanically extracting and marking all seven complete (as the standard state-update step instructs) would have marked GATE-08 and GOV-01 "Complete" in `REQUIREMENTS.md`, but neither is actually done: GATE-08 is a two-part requirement ((a) README documentation, (b) Makefile help text) and this plan delivers only (b) — the plan's own `<verification>` section says so explicitly ("GATE-08, Makefile half — the README half is 02-03"). GOV-01's requirement text states outright that "Phase 2 does not close until a post-checkpoint stale-artifact sweep" runs (D-12's second required run, `02-GOV-SWEEP-RUNBOOK.md`) — this plan satisfies only D-12's phase-*start* check via its precondition.
- **Fix:** Ran `requirements mark-complete` for all seven IDs (as instructed), observed both surfaces (checkbox + traceability row) flip to Complete for all seven, then manually reverted the checkbox and traceability row for `GATE-08` and `GOV-01` back to Pending, with an inline note on each traceability row recording what this plan did complete (`GATE-08`: "Makefile half complete at 02-01; README half is 02-03"; `GOV-01`: "start check passed at 02-01 precondition; closure sweep is 02-GOV-SWEEP-RUNBOOK.md"). SUMMARY.md's `requirements-completed` frontmatter list and the `D7`/`D10` coverage entries were corrected to match — both retained with `human_judgment: true` and a `rationale` explaining the partial completion, rather than silently dropped from coverage.
- **Files modified:** `.planning/REQUIREMENTS.md`, `.planning/phases/02-enforcement-and-a-single-gate-definition/02-01-SUMMARY.md`
- **Verification:** `grep -n 'GATE-08\|GOV-01' .planning/REQUIREMENTS.md` confirms both checkboxes are `[ ]` and both traceability rows read `Pending` with the disposition note
- **Committed in:** separate `docs(02)` commit alongside the metadata commit

---

**Total deviations:** 2 auto-fixed (1 plan verify-script literal correction — Rule 1; 1 governance-record correction — Rule 2)
**Impact on plan:** No production or test code changed as a result of either. The verify-script literal is required by D-11, which this same plan authored and measured empirically before planning. The GATE-08/GOV-01 reversion keeps REQUIREMENTS.md honest about what 02-01 actually delivered versus what 02-03 and the closure sweep still owe — both are documented as partially satisfied in this SUMMARY's coverage block rather than silently marked done.

## Issues Encountered
- Bash tool calls are separate shell processes, so a `trap ... EXIT` set in one call does not survive into a subsequent call — an early attempt to run Task 2 step 5's fixture-move and step 5a's `make gate` check as separate tool calls silently let the trap restore the fixture between them, making step 5a appear to pass against a *readable* fixture. Resolved by running the entire fixture-move-verify-restore sequence (steps 5, 5a, 5b, 5c) in a single Bash invocation, matching the plan's intended one-script design.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `make gate` is now strict and green with the compose database up; `EPISTEMIC_OS_TEST_REQUIRE_ENV` is the flag name 02-02's shell-out harness and Phase 3's proofs must bind to
- 02-02 (shell-out-to-make harness) can now assert the `env-preflight` voicelessness constraint and the `make test` banner text, both landed unchanged from what this plan committed
- 02-03 (CI collapse, SEC-01, GATE-09, README) is unblocked — nothing in this plan touched `.github/workflows/ci.yml`, `docker-compose.yml`, or `README.md`
- No blockers. The Task 2 step 5a literal-correction deviation above is paper-only and does not affect any downstream plan's binding to the flag name, the message shapes, or D-11 itself

---
*Phase: 02-enforcement-and-a-single-gate-definition*
*Completed: 2026-09-02*

## Self-Check: PASSED

All three declared files (`internal/platform/testenv/testenv.go`,
`internal/platform/testenv/testenv_test.go`, `Makefile`) and this SUMMARY.md
exist on disk. All six commit hashes (`18624fc`, `65fb8c0`, `e8faa6a`,
`190c125`, `faad2ef`, `54924bc`) are present in `git log --oneline --all`.
