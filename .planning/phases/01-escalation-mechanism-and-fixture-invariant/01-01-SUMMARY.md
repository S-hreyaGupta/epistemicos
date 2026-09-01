---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 01
subsystem: testing
tags: [go, testing, gate-05, environment-skip, pgx, escalation]

# Dependency graph
requires: []
provides:
  - "internal/platform/testenv package: URLEnv, RequireEnv, Required() bool, Pool(t *testing.T) *pgxpool.Pool, Fixture(t *testing.T, path string) []byte"
  - "EPISTEMIC_OS_TEST_REQUIRE_DB — the escalation flag, presence-based, unwired (Phase 2 turns it on in the Makefile/CI)"
  - "unparseableURLMsg — argument-free constant, the T-01-01 mitigation, pinned by a negative-control unit test"
  - "All 38 former testPool(t) call sites across 6 files now call testenv.Pool(t) directly; neither store nor approved defines its own pool helper"
affects: [01-03-escalation-mechanism, phase-2-classification, phase-3-negative-tests]

actuals:
  tokens: 15600
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "One package owns every skip-or-fail decision for an environment condition; every call site delegates rather than re-deciding"
    - "Argument-free message constant as the mitigation for a message that would otherwise interpolate untrusted/sensitive input (unparseableURLMsg)"
    - "Two-step negative control: assert the leak token is present in a naive/raw rendering (proving the check has teeth) before asserting it is absent from the real output"
    - "Documented decision order (unset URL -> unparseable URL -> unreachable host) so a reader can answer 'what happens when two conditions are unsatisfiable at once' without re-deriving it"

key-files:
  created:
    - internal/platform/testenv/testenv.go
    - internal/platform/testenv/testenv_test.go
  modified:
    - internal/adapters/secondary/store/segmentation_test.go
    - internal/adapters/secondary/store/authorreturn_test.go
    - internal/adapters/secondary/store/researchunit_test.go
    - internal/adapters/secondary/store/runrejection_test.go
    - internal/adapters/secondary/store/segmentation_decision_test.go
    - internal/adapters/secondary/approved/papers_test.go

key-decisions:
  - "Task 1 wired only segmentation_test.go's 5 call sites (the tracer slice) before Task 2 converted the remaining 33 across 5 files — this is the plan's own thin-slice sequencing, not a deviation."
  - "unparseableURLMsg is a plain string constant built by compile-time concatenation of URLEnv and a fixed sentence, not a format string — a later edit that wants to add detail must change its type, which is visible in review."
  - "hostFromURL never special-cases the keyword/value DSN form; net/url.Parse already returns an empty Host for a string with no '://' authority, which was verified empirically rather than assumed."
  - "The T-01-01 negative controls in testenv_test.go reuse the literal token DSNLEAKCANARY named in the plan's acceptance criteria for both the hostFromURL userinfo control and the unparseableURLMsg control, so the same token that proves the store-package acceptance criteria has teeth also proves the unit-level controls have teeth."

patterns-established:
  - "Environment-skip decisions (unset var, unreachable resource, unreadable file) live in exactly one platform package per class of condition, never duplicated per consumer package."

requirements-completed: [GATE-05]

coverage:
  - id: D1
    description: "With EPISTEMIC_OS_TEST_REQUIRE_DB unset and EPISTEMIC_OS_DB_URL unset, go test ./... -count=1 exits 0 and reports exactly 38 test-level skips, plain and -shuffle=on"
    requirement: "GATE-05"
    verification:
      - kind: integration
        ref: "env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v | grep -c '^--- SKIP'"
        status: pass
      - kind: integration
        ref: "same command with -shuffle=on"
        status: pass
    human_judgment: false
  - id: D2
    description: "With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL unset, the store and approved packages exit non-zero and name both env vars"
    requirement: "GATE-05"
    verification:
      - kind: integration
        ref: "EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 (status + grep, asserted independently)"
        status: pass
      - kind: integration
        ref: "EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/approved/... -count=1"
        status: pass
    human_judgment: false
  - id: D3
    description: "With EPISTEMIC_OS_TEST_REQUIRE_DB set and a closed-port EPISTEMIC_OS_DB_URL, the run exits non-zero and names that host and port"
    requirement: "GATE-05"
    verification:
      - kind: integration
        ref: "EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1"
        status: pass
    human_judgment: false
  - id: D4
    description: "With the flag unset and the same closed-port URL, TestSaveRun_FixtureRoundTripsAllOffsets still reports SKIP and the package exits 0 — the phase-base branch is preserved"
    requirement: "GATE-05"
    verification:
      - kind: integration
        ref: "env -u EPISTEMIC_OS_TEST_REQUIRE_DB ... go test -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 -v"
        status: pass
    human_judgment: false
  - id: D5
    description: "The parse-failure branch emits unparseableURLMsg only — no component of the connection string, including a database-name leak token, reaches the output; measured to fail at the phase base and pass after this change"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "internal/platform/testenv/testenv_test.go#TestUnparseableURLMsg_Control_NoLeak"
        status: pass
      - kind: integration
        ref: "EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@ bad host/DSNLEAKCANARY' go test ./internal/adapters/secondary/store/... -count=1 (4 independent assertions)"
        status: pass
      - kind: integration
        ref: "same with the keyword/value form host=x port=notanumber password=pw dbname=DSNLEAKCANARY"
        status: pass
    human_judgment: false
  - id: D6
    description: "All 38 former call sites reach testenv.Pool(t) directly across 6 files; neither store nor approved defines its own pool helper"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "grep -rno 'testenv.Pool(t)' --include=*_test.go internal | wc -l == 38, across 6 files"
        status: pass
    human_judgment: false
  - id: D7
    description: "The cross-package fixture read in segmentation_test.go goes through testenv.Fixture; the in-package loadFixture in the segment domain is untouched and stays fatal"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "grep -c 'testenv.Fixture(t' segmentation_test.go == 1; grep -c 'os.ReadFile' == 0"
        status: pass
      - kind: unit
        ref: "internal/platform/testenv/testenv_test.go#TestFixture_SuccessPath"
        status: pass
    human_judgment: false
  - id: D8
    description: "Nothing outside internal/ and .planning/ changed relative to the approved phase base 868d45b; the mechanism exists and enforces nothing by default"
    requirement: "GATE-05"
    verification:
      - kind: other
        ref: "git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3 -- | grep -v '^internal/' | grep -v '^\\.planning/' (empty after each task)"
        status: pass
    human_judgment: false

duration: 48min
completed: 2026-09-01
status: complete
---

# Phase 1 Plan 1: Escalation Mechanism and Fixture Invariant Summary

**New `internal/platform/testenv` package (`Pool`, `Fixture`, `Required`, `hostFromURL`, `unparseableURLMsg`) replaces two duplicated package-local pool helpers, routes all 38 former call sites across 6 files through one decision point, and gives that decision point an opt-in `EPISTEMIC_OS_TEST_REQUIRE_DB` escalation flag — verified inert with escalation off (38 skips, exit 0, unchanged) and verified to fail with a named cause on each of the three environment conditions with escalation on, including a database-name DSN leak that is measured to fail at the phase base and pass only after this change.**

## Performance

- **Duration:** 48 min
- **Started:** 2026-09-01T08:23:00Z (approx)
- **Completed:** 2026-09-01T09:11:00Z (approx)
- **Tasks:** 3
- **Files modified:** 8 (2 created, 6 modified)

## Accomplishments

- Created `internal/platform/testenv` with `URLEnv`, `RequireEnv`, `Required() bool`, unexported `hostFromURL(raw string) string`, unexported constant `unparseableURLMsg`, `Pool(t *testing.T) *pgxpool.Pool`, and `Fixture(t *testing.T, path string) []byte` — the single place every skip-or-fail decision for the database-backed tests and the cross-package fixture is made.
- Wired all 38 former `testPool(t)` call sites across 6 files (`segmentation_test.go` 5, `authorreturn_test.go` 9, `researchunit_test.go` 6, `runrejection_test.go` 7, `segmentation_decision_test.go` 6, `papers_test.go` 5) to call `testenv.Pool(t)` directly; deleted both package-local pool helper definitions entirely.
- Routed `TestSaveRun_FixtureRoundTripsAllOffsets`'s cross-package fixture read through `testenv.Fixture(t, path)`, closing GATE-05's third environment condition (unreadable fixture) in the same package as the other two.
- Wrote `testenv_test.go` covering the pure pieces (`hostFromURL`, `Required`, `unparseableURLMsg`, `Fixture`'s success path) with two negative controls that each first prove a leak token would be detected in a naive/raw rendering before asserting it is absent from the real output.
- Confirmed escalation off reproduces the phase-base baseline exactly (exit 0, 38 test-level skips, unchanged under `-shuffle=on`), and escalation on converts each of the three environment conditions into a named failure without wiring any enforcement into the Makefile or CI.

## Task Commits

1. **Task 1: End-to-end escalation for the database path — store package only** - `3f5c373` (feat)
2. **Task 2: Delete both duplicated helpers and route all 38 call sites directly** - `7699ea8` (refactor)
3. **Task 3: Route the cross-package fixture read through the same helper** - `d811f0f` (feat)

**Plan metadata:** pending (this SUMMARY commit)

## Files Created/Modified

- `internal/platform/testenv/testenv.go` - New package: URLEnv, RequireEnv, Required, hostFromURL, unparseableURLMsg, Pool, Fixture
- `internal/platform/testenv/testenv_test.go` - Unit tests with negative controls for the pure pieces
- `internal/adapters/secondary/store/segmentation_test.go` - testPool deleted; 5 call sites -> testenv.Pool(t); fixture read -> testenv.Fixture(t, ...); os import removed
- `internal/adapters/secondary/store/authorreturn_test.go` - 9 call sites -> testenv.Pool(t); testenv import added
- `internal/adapters/secondary/store/researchunit_test.go` - 6 call sites -> testenv.Pool(t); testenv import added
- `internal/adapters/secondary/store/runrejection_test.go` - 7 call sites -> testenv.Pool(t); testenv import added
- `internal/adapters/secondary/store/segmentation_decision_test.go` - 6 call sites -> testenv.Pool(t); testenv import added
- `internal/adapters/secondary/approved/papers_test.go` - testPool deleted; 5 call sites -> testenv.Pool(t); os and time imports removed

## Final Exported Signatures

```go
package testenv // github.com/EpistemicOS/epistemicos/internal/platform/testenv

const URLEnv = "EPISTEMIC_OS_DB_URL"
const RequireEnv = "EPISTEMIC_OS_TEST_REQUIRE_DB"

func Required() bool
func Pool(t *testing.T) *pgxpool.Pool
func Fixture(t *testing.T, path string) []byte
```
(`hostFromURL(raw string) string` and `unparseableURLMsg` are unexported, per plan.)

## Observed Results (verbatim, for Phase 2 and Phase 3 to build on)

**Phase base precondition (Task 1), all five assertions run before any file was written:**
1. `git rev-parse --verify 868d45bf873c9e147f18a099171b99afa348f4a3` — succeeded (prints the SHA).
2. `git merge-base --is-ancestor 868d45bf873c9e147f18a099171b99afa348f4a3 HEAD` — exit 0.
3. `git log --format=%H 868d45bf873c9e147f18a099171b99afa348f4a3..HEAD -- Makefile .github/workflows/ci.yml` — empty.
4. `git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3..HEAD | grep -v '^internal/' | grep -v '^\.planning/'` — empty.
5. Manifest `phase_base_approval.commit` == `868d45bf873c9e147f18a099171b99afa348f4a3` and `phase_base_approval.status` == `approved` — both confirmed by direct read of `01-PLAN-MANIFEST.json`.

All five passed. No re-anchoring occurred.

**Escalation off — exact skip count, plain and shuffled:**
```
env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1
-> exit 0 (measured after every task, and again after Task 3 as the final state)

... -v | grep -c '^--- SKIP'   -> 38
... -v -shuffle=on | grep -c '^--- SKIP' -> 38

-json run, skip events carrying a "Test" field -> 38
-json run, total skip events (incl. 11 package-level) -> 49
```
Matches the phase-base baseline recorded in the manifest (`test_level_skips_no_db: 38`, `test_level_skips_no_db_shuffled: 38`) exactly.

**Escalated, URL unset (store package):**
- Status: non-zero (measured `1`)
- Text (verbatim, `authorreturn_test.go:31` and identical at every other of the 33 store-package sites):
  `EPISTEMIC_OS_DB_URL is not set, and EPISTEMIC_OS_TEST_REQUIRE_DB is set: escalation is on, so this test cannot be skipped for a missing database URL`

**Escalated, URL unset (approved package):**
- Status: non-zero (measured `1`)
- Text (verbatim, `papers_test.go:63`): same message as above.

**Escalated, unreachable host (`postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable`):**
- Status: non-zero (measured `1`)
- Text (verbatim, `authorreturn_test.go:31`):
  `cannot reach postgres at 127.0.0.1:1 (from EPISTEMIC_OS_DB_URL): failed to connect to `user=u database=nodb`: 127.0.0.1:1 (127.0.0.1): dial error: dial tcp 127.0.0.1:1: connectex: No connection could be made because the target machine actively refused it.`

**Non-escalated, unreachable host — the preserved skip (`TestSaveRun_FixtureRoundTripsAllOffsets`):**
- Status: `0`
- Output: `--- SKIP: TestSaveRun_FixtureRoundTripsAllOffsets (0.01s)` with body `segmentation_test.go:246: cannot reach postgres at 127.0.0.1:1 (from EPISTEMIC_OS_DB_URL): failed to connect to ...`

**Escalated, unparseable URL — the T-01-01 falsifiable leak control:**
- URL form (`postgres://u:pw@ bad host/DSNLEAKCANARY`): status non-zero (`1`); output contains `EPISTEMIC_OS_DB_URL`; `DSNLEAKCANARY` count `0`; `cannot parse` count `0`. Message (verbatim, `authorreturn_test.go:31`):
  `EPISTEMIC_OS_DB_URL is set, but its value is not a usable PostgreSQL connection string; the value and the underlying library error are deliberately withheld here, since both carry the connection string`
- Keyword/value form (`host=x port=notanumber password=pw dbname=DSNLEAKCANARY`): identical four results (status non-zero, `EPISTEMIC_OS_DB_URL` present, both leak counts `0`).

**Measured leak-token counts, before and after this change (the control's teeth):**
| Scenario | Before (phase base, unmodified helper) | After (this plan) |
|---|---|---|
| DSNLEAKCANARY count, URL form | 1 (manifest `dsn_leak_token_count_at_phase_base_url_form`) | 0 (measured above) |
| DSNLEAKCANARY count, keyword/value form | 1 (manifest `dsn_leak_token_count_at_phase_base_kv_form`) | 0 (measured above) |
| `cannot parse` phrase present | yes (both forms, phase base) | no (both forms, this plan) |

**Negative controls, wired and passing:**
```
go test ./internal/platform/testenv/... -count=1 -run 'Control' -v
--- PASS: TestHostFromURL_Control_NeverReturnsUserinfo (0.00s)
--- PASS: TestUnparseableURLMsg_Control_NoLeak (0.00s)
PASS
```
Both bodies assert the leak token is present in the raw or naive form before asserting it is absent from the sanitised form.

**Diff from phase base, filtered form (asserted after each of the 3 tasks):**
`git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3 -- | grep -v '^internal/' | grep -v '^\.planning/'` printed nothing every time. Note (carried forward from 01-02's SUMMARY): the *unfiltered* form of this command, as literally spelled in this plan's own `<verification>` step 10 (`git diff --name-only 868d45b -- ` with no path filter), lists roughly 48 paths — not because this plan touched anything outside `internal/`, but because ~32 pre-existing `.planning/`-only commits (the base re-anchor, the plan re-freeze, review-run archives, STATE.md records) already sit between the approved phase base and the start of this plan's execution, none of which this plan authored or could avoid, and editing any of which is out of scope. This plan ran the filtered form the acceptance criteria specify, exactly as instructed, and that form is empty at every checkpoint.

## Decisions Made

- Task 1's tracer slice wired only `segmentation_test.go` (5 call sites) end-to-end before Task 2 converted the remaining 33; this is the plan's designed sequencing (prove the mechanism against real tests before the mechanical six-file rewrite), not a scope deviation.
- `unparseableURLMsg` was written as `URLEnv + " is set, but ..."`, a compile-time string constant concatenation — not a `Sprintf` — so it satisfies "no arguments and no format verbs" literally while still naming `EPISTEMIC_OS_DB_URL` via the constant rather than a repeated literal.
- The malformed-string `hostFromURL` test case (`postgres://u:pw@ bad host/db`, a bare space in the host) was verified empirically to trigger a `net/url.Parse` error rather than assumed; the plan's own ground-truth measurements did not specify the exact string, and this shape reuses the same construction as the T-01-01 acceptance criteria for consistency.
- Both negative controls (`TestHostFromURL_Control_NeverReturnsUserinfo`, `TestUnparseableURLMsg_Control_NoLeak`) reuse the literal token `DSNLEAKCANARY` from the plan's own acceptance criteria, so the token that proves the process-level store-package criteria have teeth is the same token proving the unit-level controls have teeth.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' actions, acceptance criteria, and verify blocks were followed as specified; no Rule 1-4 auto-fixes were needed.

## Issues Encountered

None beyond the pre-existing whole-tree-diff discrepancy already flagged by 01-02's SUMMARY and by this plan's own `<known_plan_defect>` context (verification step 10's unfiltered `git diff` form lists ~48 paths due to pre-existing `.planning/`-only commits since the phase base; the filtered form the acceptance criteria specify is empty). Recorded above under Observed Results rather than silently treated as passing or reworded.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `internal/platform/testenv` exists with the exact exported signatures Phase 2's Makefile change and Phase 3's proof tests bind to: `Pool(t *testing.T) *pgxpool.Pool`, `Fixture(t *testing.T, path string) []byte`, `Required() bool`, `URLEnv`, `RequireEnv`.
- The three verbatim failure messages (unset-URL, unreachable-host, unparseable-URL) are recorded above for Phase 3's PROOF-01/PROOF-02/PROOF-03 to assert against.
- `make gate` behavior is unchanged: escalation is opt-in via `EPISTEMIC_OS_TEST_REQUIRE_DB`, which nothing in this plan sets in a default run. No Makefile or CI change was made.
- The `awaiting_disposition.contract_decisions` items in `01-PLAN-MANIFEST.json` (flag name scope, README/Makefile documentation, the deferred AC-14 empty-heading guard) remain open for 01-03 Task 3's disposition, as designed.
- 01-03 (wave 2, depends on 01-01 and 01-02) can now proceed: both of its dependencies have SUMMARY.md files.

---
*Phase: 01-escalation-mechanism-and-fixture-invariant*
*Completed: 2026-09-01*
