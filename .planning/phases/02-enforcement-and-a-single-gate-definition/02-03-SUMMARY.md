---
phase: 02-enforcement-and-a-single-gate-definition
plan: 03
subsystem: infra
tags: [docker-compose, github-actions, ci, security, golang, testing]

# Dependency graph
requires:
  - phase: 02-enforcement-and-a-single-gate-definition
    provides: "02-01's strict `make gate` (vet -> gofmt -> build -> env-preflight -> migrate -> test), the EPISTEMIC_OS_TEST_REQUIRE_ENV rename and its make-gate target-scoped value — the single definition this plan's CI collapse and README both bind to"
provides:
  - "docker-compose.yml postgres bound to 127.0.0.1 only, declared and live (SEC-01, closes AR-02/T-01-11)"
  - "ci.yml go job collapsed to a single `run: make gate` step, services: postgres and job-level EPISTEMIC_OS_DB_URL preserved (CI-02, preserves CI-01)"
  - "headingGuardMessage(headings, fixturePath) — repo-wide length guard for the one unguarded headings[0] index site (GATE-09)"
  - "README.md ## The gate section documenting the D-02 sequence, the database requirement, the migration warning, and EPISTEMIC_OS_TEST_REQUIRE_ENV's full presence-based semantics plus D-11's paths-not-precedence limit (GATE-08)"
affects: ["02-02-shell-out-harness", "02-04", "02-GOV-SWEEP-RUNBOOK", "03-01-automated-proof"]

# Actuals (#2632)
actuals:
  tokens: 2576
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Length guard as a value: headingGuardMessage(headings, fixturePath) string returns a fatal message or empty string, so the guard's branch can be driven by a control test with synthetic inputs rather than only located by line number"
    - "Negative-control proof via git archive HEAD + cp of the working-tree test file into a throwaway tree, then a targeted perl substitution that defeats the guard and requires the control test to fail — extends Phase 1's TestPreambleInvariant_Control pattern to GATE-09"

key-files:
  created: []
  modified:
    - docker-compose.yml
    - .github/workflows/ci.yml
    - internal/core/domain/segment/acceptance_test.go
    - README.md

key-decisions:
  - "Task 2 followed the plan's TDD structure literally: TestGATE09_HeadingGuard_Control was committed first in a state proven not to compile (RED — headingGuardMessage undefined), then headingGuardMessage plus the AC-14 wiring landed in the GREEN commit. No REFACTOR commit needed."
  - "Plan verify-script literal corrected: the fixtureHasPreamble declaration-count regex (`^[[:space:]]*fixtureHasPreamble[[:space:]]*=`) cannot match the actual `const fixtureHasPreamble = true` declaration, because the line starts with the `const` keyword, not the identifier. Corrected to `^[[:space:]]*(const|var)[[:space:]]+fixtureHasPreamble[[:space:]]*=` — see Deviations."

patterns-established:
  - "Pattern 3: a guard's decision is a pure value-returning function (headingGuardMessage), so a control test can prove the guard's branch actually executes against synthetic inputs, plus a negative control that mutates a throwaway copy of the guard and requires the control test to then fail — the same discipline Phase 1's TestPreambleInvariant_Control established for the declaration side of this same fixture invariant."

requirements-completed: [SEC-01, CI-02, GATE-09, GATE-08]

coverage:
  - id: D1
    description: "docker-compose.yml declares the loopback-only PostgreSQL publication (three-field 127.0.0.1:5432:5432), and the running container is recreated so the live binding matches — measured via docker compose ps, not assumed (SEC-01)"
    requirement: "SEC-01"
    verification:
      - kind: integration
        ref: "Task 1 verify (docker compose ps postgres PORTS cell == 127.0.0.1:5432->5432/tcp, absent from both 0.0.0.0 and [::])"
        status: pass
    human_judgment: false
  - id: D2
    description: "The api service's published port is byte-unchanged"
    requirement: "SEC-01"
    verification:
      - kind: unit
        ref: "Task 1 verify (git diff docker-compose.yml api service block unchanged, still \"9082:9082\")"
        status: pass
    human_judgment: false
  - id: D3
    description: "ci.yml's go job runs make gate as its single step; the five inline steps (vet, gofmt, build, migrate, test) are gone (CI-02)"
    requirement: "CI-02"
    verification:
      - kind: unit
        ref: "Task 1 verify (go job holds exactly 1 `- name:` line and exactly 2 `- uses:` lines, and a `run: make gate` line)"
        status: pass
    human_judgment: false
  - id: D4
    description: "CI-01 preserved: services: postgres block, job-level EPISTEMIC_OS_DB_URL and the docker smoke job are byte-unchanged"
    requirement: "CI-02"
    verification:
      - kind: unit
        ref: "Task 1 verify (grep for services:, postgres:16-alpine, pg_isready, the localhost DSN; git diff excludes Dockerfile.api)"
        status: pass
    human_judgment: false
  - id: D5
    description: "make gate is green against the rebound loopback-only postgres service"
    requirement: "CI-02"
    verification:
      - kind: integration
        ref: "Task 1 verify (EPISTEMIC_OS_DB_URL=127.0.0.1 make gate, exit 0; re-run at plan close, exit 0)"
        status: pass
    human_judgment: false
  - id: D6
    description: "A heading-free fixture produces a normal test failure naming testdata/demo.md and does not panic; the guard's branch is executed against synthetic inputs, not merely located (GATE-09)"
    requirement: "GATE-09"
    verification:
      - kind: unit
        ref: "internal/core/domain/segment/acceptance_test.go#TestGATE09_HeadingGuard_Control (11 passing subtests, including 5 does-not-panic subtests under recover())"
        status: pass
      - kind: unit
        ref: "Task 2 verify step 5 — negative control: guard defeated in a throwaway tree (git archive HEAD + cp of the working-tree file), TestGATE09_HeadingGuard_Control then fails"
        status: pass
    human_judgment: false
  - id: D7
    description: "The fix is a length guard only — fixtureHasPreamble remains the package's only declaration mechanism; the two already-guarded index sites are untouched"
    requirement: "GATE-09"
    verification:
      - kind: unit
        ref: "Task 2 verify steps 8 and 10 (exactly 1 fixtureHasPreamble declaration repo-wide; git diff excludes build_test.go and fixture_test.go)"
        status: pass
    human_judgment: false
  - id: D8
    description: "README.md documents the escalation flag's post-GATE-07 name, its presence-based semantics in both directions, what escalation changes, and D-11's paths-not-precedence limit, under the gate section rather than the Configuration table (GATE-08)"
    requirement: "GATE-08"
    verification:
      - kind: unit
        ref: "Task 3 verify (grep assertions on ## The gate section content and its absence from ## Configuration)"
        status: pass
    human_judgment: false
  - id: D9
    description: "README's gate command summary names the actual D-02 sequence, states the database requirement, and the quickstart points at the gate's dependence on make up (GATE-08)"
    requirement: "GATE-08"
    verification:
      - kind: unit
        ref: "Task 3 verify (## The gate section names env-preflight/migrate/make gate and the database requirement; ## Quickstart mentions the gate)"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-09-02
status: complete
---

# Phase 2 Plan 3: CI Collapse, Loopback Bind, Heading Guard, and Gate Documentation Summary

**Bound the compose PostgreSQL to loopback (declared and live), collapsed the CI `go` job onto `make gate`, added an executed (not merely located) length guard for the one unguarded `headings[0]` index, and rewrote README's gate section to describe the D-02 sequence and the escalation flag's full presence-based semantics.**

## Performance

- **Duration:** ~7 min (commit-to-commit; base `8a23cb6` to `4710c2e`)
- **Started:** 2026-09-02T07:01:19Z
- **Completed:** 2026-09-02T07:06:45Z
- **Tasks:** 3 completed
- **Files modified:** 4 (`docker-compose.yml`, `.github/workflows/ci.yml`, `internal/core/domain/segment/acceptance_test.go`, `README.md`)

## Accomplishments
- `docker-compose.yml`'s `postgres` service now publishes `"127.0.0.1:5432:5432"`; the running container was recreated (`pg_data` named volume survived) so the live binding matches the declared one, measured via `docker compose ps` rather than assumed — closes AR-02 and T-01-11
- `.github/workflows/ci.yml`'s `go` job collapsed from five inline steps to one `run: make gate` step; `services: postgres` and the job-level `EPISTEMIC_OS_DB_URL` (CI-01) survive byte-for-byte, and the `docker` smoke job is untouched
- `headingGuardMessage(headings, fixturePath) string` guards the one previously-unguarded `headings[0]` index in `TestAC14_PreHeadingContentHasNoNode`; a heading-free fixture now produces `t.Fatalf` naming `testdata/demo.md` instead of panicking
- `TestGATE09_HeadingGuard_Control` runs the guard against five heading-free synthetic inputs (empty document, prose with no `#`, whitespace only, `#` not at line start, a heading-like line inside a fenced code block), proving each first reaches `len == 0`, then runs the exact guarded sequence under `recover()`, plus a positive case — 11 passing subtests total, none vacuous, backed by a negative control that defeats the guard in a throwaway `git archive` copy and requires the control test to then fail
- README's `## The gate` section now names the real D-02 sequence, states the database requirement and the new migration behavior, and documents `EPISTEMIC_OS_TEST_REQUIRE_ENV`'s presence-based semantics in both directions plus D-11's paths-not-precedence limit; the flag is deliberately absent from the Configuration table

## Task Commits

1. **Task 1: Bind the compose PostgreSQL to loopback, and collapse the CI go job onto make gate**
   - `a527644` (feat) — docker-compose.yml loopback binding + container recreation; ci.yml go job collapsed to `make gate`
2. **Task 2: Guard the unguarded heading index** — TDD pair
   - `fa74fae` (test) — add `TestGATE09_HeadingGuard_Control` (RED: `headingGuardMessage` undefined, package does not compile)
   - `919efec` (feat) — add `headingGuardMessage`, wire it into `TestAC14_PreHeadingContentHasNoNode` (GREEN)
3. **Task 3: Document the gate's new shape and the escalation flag**
   - `4710c2e` (docs) — README `## The gate` section rewritten, Quickstart gains one pointer line

**Plan metadata:** this commit (docs: complete plan)

_Task 2 carried `tdd="true"`: RED (compile failure) then GREEN, no REFACTOR needed._

## Files Created/Modified
- `docker-compose.yml` — `postgres` service `ports` entry changed to the three-field `"127.0.0.1:5432:5432"` form with a comment naming AR-02/T-01-11; `api` service unchanged
- `.github/workflows/ci.yml` — `go` job's five inline steps replaced by one `run: make gate` step with a comment explaining the collapse; `services: postgres`, job-level `EPISTEMIC_OS_DB_URL`, and the `docker` job unchanged
- `internal/core/domain/segment/acceptance_test.go` — added `headingGuardMessage` (pure length guard) and `TestGATE09_HeadingGuard_Control`; `TestAC14_PreHeadingContentHasNoNode` now calls the guard between `detectHeadings(md)` and the first `headings[0]` index
- `README.md` — `## The gate` section rewritten (real command sequence, database requirement, migration warning, escalation flag semantics, D-11 limit, rename note); one line added to `## Quickstart` pointing at the gate section

## Decisions Made
- Followed the plan's TDD structure literally for Task 2: the control test was committed first in a state that fails to compile (RED), then the guard implementation and AC-14 wiring landed together in the GREEN commit.
- The negative control's `cp` of the working-tree `acceptance_test.go` into the `git archive HEAD` copy was essential, not incidental: at the point Task 2's GREEN commit had not yet landed, `git archive HEAD` alone would have materialized the RED (non-compiling) state. Confirmed this is exactly what the plan's provenance note called out.
- See Deviations below for the corrected `fixtureHasPreamble` declaration-count regex.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — plan verify-script defect, not a code defect] Corrected the `fixtureHasPreamble` declaration-count regex in Task 2's verify step 8**
- **Found during:** Task 2, verify step 8 (length-guard-only constraint)
- **Issue:** The plan's verify script asserted `grep -rE '^[[:space:]]*fixtureHasPreamble[[:space:]]*=' internal/core/domain/segment/ | wc -l` equals 1. The actual declaration, landed in Phase 1 and untouched by this plan, is `const fixtureHasPreamble = true` — the line begins with the `const` keyword, not with the identifier, so the plan's regex structurally cannot match it and returned 0.
- **Fix:** Ran the check with a corrected pattern, `^[[:space:]]*(const|var)[[:space:]]+fixtureHasPreamble[[:space:]]*=`, which returned exactly 1 — confirming the substance of the check (no second declaration mechanism was added) without weakening it. No code change; `fixtureHasPreamble` was not touched by this plan.
- **Files modified:** none (verification-only)
- **Verification:** `grep -rE '^[[:space:]]*(const|var)[[:space:]]+fixtureHasPreamble[[:space:]]*=' internal/core/domain/segment/` returns exactly the one Phase 1 declaration in `fixture_test.go`
- **Committed in:** documented here; no separate commit needed since no file changed

---

**Total deviations:** 1 auto-fixed (1 plan verify-script literal correction — Rule 1)
**Impact on plan:** No production or test code changed as a result. The corrected regex measures the same substance the plan intended (exactly one `fixtureHasPreamble` declaration, no second declaration mechanism) and is required only because Go's `const` syntax puts a keyword before the identifier, which the plan's original pattern did not anticipate.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None — no external service configuration required. `make up` was already running; Task 1 recreated the `postgres` container in place using the existing compose project.

## Next Phase Readiness
- SEC-01, CI-02, GATE-09 and GATE-08 are now complete; ROADMAP §Phase 2 success criteria 4, 5, 8, 9 and 10 hold
- The compose `postgres` service is left running and healthy on `127.0.0.1:5432`, as the plan's declared end state — 02-02 and 02-04 (same wave) depend on this runtime resource and will find it already rebound
- `make gate` is green end-to-end against the rebound service, confirmed both immediately after Task 1 and again at plan close
- `go.mod` and `go.sum` are untouched; `go build ./...`, `go vet ./...` and `gofmt -l .` are clean across the whole repository
- No blockers for 02-02, 02-04, or the GOV-01 closure sweep runbook

---
*Phase: 02-enforcement-and-a-single-gate-definition*
*Completed: 2026-09-02*
