---
phase: 01-escalation-mechanism-and-fixture-invariant
verified: 2026-09-01T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 1: Escalation Mechanism and Fixture Invariant Verification Report

**Phase Goal:** A single shared helper owns the decision to skip or fail for every
database-backed test, an opt-in flag converts each environment skip into a failure
that names its cause, and the preamble property is proven as a fixture invariant.
`make gate` behavior is unchanged.

**Verified:** 2026-09-01 (commands re-run independently by the verifier, in Git Bash,
against the working tree at the time of verification — not inferred from SUMMARY.md)
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

All five ROADMAP success criteria were independently re-measured (not read from a
SUMMARY) by running the commands below from the repository root.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | One helper is the only place `store`/`approved` tests decide to skip or fail — duplicated `testPool` gone | VERIFIED | `grep -v '^\s*//' segmentation_test.go \| grep -c testPool` → `0`; same for `papers_test.go` → `0`; `grep -rno 'testenv.Pool(t)' --include=*_test.go internal \| wc -l` → `38` across `grep -rl ... \| wc -l` → `6` files. Read `internal/platform/testenv/testenv.go` directly — one `Pool` function is the sole decision point. |
| 2 | With escalation flag set, unset URL / unreachable DB / unreadable fixture each fail naming that specific cause | VERIFIED | Unset URL (store): status `1`, output contains `EPISTEMIC_OS_DB_URL` (33×) and `EPISTEMIC_OS_TEST_REQUIRE_DB` (33×); same for `approved` package (5×/5×). Closed port: status `1`, output contains `127.0.0.1:1` (33×). Unreadable fixture (live DB, fixture moved aside under a trap): status `1`, output names `core/domain/segment/testdata/demo.md`, fixture restored byte-identical (SHA-256 `a5f1feb0...` before and after). |
| 3 | With flag unset, `go test ./...` skips exactly as today — green run without Docker | VERIFIED | `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v` → exit `0`, `grep -c '^--- SKIP'` → `38`; `-shuffle=on` → same `38`. Unreachable-DB case: `TestSaveRun_FixtureRoundTripsAllOffsets` → exit `0`, `--- SKIP`. Unreadable-fixture case (DB up, flag unset, fixture moved aside): exit `0`, `--- SKIP`, fixture restored byte-identical. |
| 4 | `TestFixtureIntegrity` asserts `demo.md`'s non-whitespace preamble; `acceptance_test.go:438,451` stay green and silent | VERIFIED | `const fixtureHasPreamble = true` present beside `fixtureSHA256`/`fixtureBytes` (`fixture_test.go:24,29,39`). `go test ./internal/core/domain/segment/... -run 'TestFixtureIntegrity\|TestPreambleInvariant_Control\|TestAC14_PreHeadingContentHasNoNode' -v` → all PASS, 6/6 control subtests PASS. `git diff --name-only 868d45b -- acceptance_test.go` → empty (byte-identical); `grep -c 't.Skip' acceptance_test.go` → `2` (unchanged; AC-14's two content-conditional skips remain, unreached — PASS not SKIP, for the pinned fixture). |
| 5 | `make gate` behaves exactly as before — green with and without a database | VERIFIED | `docker compose stop postgres` then `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` → exit `0` (all packages `ok`/`[no test files]`). `make up` then `env -u EPISTEMIC_OS_TEST_REQUIRE_DB EPISTEMIC_OS_DB_URL=... make gate` → exit `0`. `git rev-parse HEAD:Makefile` → `63d55631...` and `HEAD:.github/workflows/ci.yml` → `fdbf98f4...`, both matching the pinned phase-base blob hashes exactly (content-level proof, immune to base-window games). `git log 868d45b..HEAD -- Makefile .github/workflows/ci.yml` → empty. Postgres left running (declared end state, confirmed). |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `internal/platform/testenv/testenv.go` | Shared skip/fail decision package: `URLEnv`, `RequireEnv`, `Required()`, `hostFromURL`, `unparseableURLMsg`, `Pool()`, `Fixture()` | VERIFIED | Read in full. All 7 symbols present with the exact signatures the SUMMARY claims. Decision order documented in comments (unset URL → unparseable URL → unreachable host), matching edge E2's must-have. |
| `internal/platform/testenv/testenv_test.go` | Unit tests + negative controls | VERIFIED | `go test ./internal/platform/testenv/... -v` → 9 tests/subtests, all PASS, including `TestHostFromURL_Control_NeverReturnsUserinfo` and `TestUnparseableURLMsg_Control_NoLeak` (both negative controls, run independently by the verifier). |
| `internal/core/domain/segment/fixture_test.go` | `fixtureHasPreamble` const, `preambleInvariant` pure function, extended `TestFixtureIntegrity`, `TestPreambleInvariant_Control` | VERIFIED | Const declared and read (not inlined) at the call site; 6/6 control subtests PASS; `TestFixtureIntegrity` PASS. |
| Six converted test files (`segmentation_test.go`, `authorreturn_test.go`, `researchunit_test.go`, `runrejection_test.go`, `segmentation_decision_test.go`, `papers_test.go`) | All former `testPool` call sites → `testenv.Pool(t)` | VERIFIED | 38 call sites across exactly 6 files, 0 remaining `testPool` references. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| 6 store/approved test files | `internal/platform/testenv` | `testenv.Pool(t)` calls | WIRED | 38 call-site grep hits, `go build`/`go vet`/`gofmt` all clean, package compiles and all tests exercise the real helper (escalated-green run below proves it is not a stub). |
| `segmentation_test.go`'s fixture read | `testenv.Fixture(t, path)` | direct call | WIRED | `grep -c 'testenv.Fixture(t' segmentation_test.go` → `1`; `grep -c 'os.ReadFile'` (non-comment) → `0`; exercised live via the trap-guarded move-and-restore proof (both escalated-fail and unescalated-skip paths observed). |
| Escalation flag `EPISTEMIC_OS_TEST_REQUIRE_DB` | Makefile / CI workflow | (deliberately absent) | CORRECTLY UNWIRED | `git log 868d45b..HEAD -- Makefile .github/workflows/ci.yml` empty; gate-file git blob hashes unchanged from phase base — confirms the mechanism is built but not yet turned on, as this phase requires. |

### Data-Flow Trace (Level 4)

Not applicable in the UI-rendering sense — this phase's "data" is the pass/fail/skip
decision of a test-execution helper. The escalated-green run (below) is the
equivalent proof: it confirms the helper is not a stub that always fails or always
skips regardless of environment.

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| Escalated run with a live DB actually executes and passes the tests that skip without one | capture-form `EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -json`, `comm -23` set containment against the 38 unescalated skip names | status `0`; escalated skip count `0`; escalated pass set (42 names) is a superset of the 38 baseline skip names, `comm -23` empty | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Flag unset reproduces phase-base skip count | `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v \| grep -c '^--- SKIP'` | `38`, exit `0` | PASS |
| Same, shuffled | same with `-shuffle=on` | `38` | PASS |
| Escalated, unset URL (store) | `EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/...` | status `1`, both var names present | PASS |
| Escalated, unset URL (approved) | same against `.../approved/...` | status `1`, both var names present | PASS |
| Escalated, closed port | `EPISTEMIC_OS_DB_URL=postgres://u:pw@127.0.0.1:1/nodb ... go test .../store/...` | status `1`, `127.0.0.1:1` present | PASS |
| DSN leak control, URL form | `EPISTEMIC_OS_DB_URL='postgres://u:pw@ bad host/DSNLEAKCANARY' EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test .../store/...` | status `1`; `EPISTEMIC_OS_DB_URL` present; `DSNLEAKCANARY` count `0`; `cannot parse` count `0` | PASS |
| Fixture invariant + control table + AC-14 | `go test ./internal/core/domain/segment/... -run '...' -v` | all PASS, 6/6 subtests | PASS |
| `make gate`, DB genuinely stopped | `docker compose stop postgres && make gate` | exit `0` | PASS |
| `make gate`, DB up | `make up && make gate` | exit `0` | PASS |
| Escalated-green, live DB | capture-form run, `comm -23` containment | status `0`, 0 skips, containment holds | PASS |
| Unreadable-fixture, escalated | trap-guarded move + `EPISTEMIC_OS_TEST_REQUIRE_DB=1` run | status `1`, names fixture path, restored byte-identical | PASS |
| Unreadable-fixture, unescalated | trap-guarded move + flag unset | status `0`, `--- SKIP`, restored byte-identical | PASS |

No SKIP results in this table — every spot-check was runnable without starting new
external services (Postgres was already running per the task brief, and was
deliberately stopped/restarted only where the scenario required it, per 01-03's
declared end state).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| GATE-04 | 01-02, 01-03 | Content-conditional skips stay green and silent | SATISFIED | `fixtureHasPreamble` declaration + `preambleInvariant`, AC-14 byte-identical and PASS for pinned fixture, `make gate` unmoved in both DB states |
| GATE-05 | 01-01, 01-03 | Shared helper converts each environment skip into a named failure when escalated; skips remain when unset | SATISFIED | `testenv.Pool`/`testenv.Fixture` as sole decision point; all 3 escalated conditions verified to fail-with-cause; all 3 unescalated branches verified to still skip |

REQUIREMENTS.md's traceability table maps only GATE-04 and GATE-05 to Phase 1
(GATE-01/02/03 → Phase 2, CI-01 → delivered pre-phase, CI-02 → Phase 2, PROOF-01+ →
Phase 3). No requirement mapped to Phase 1 is absent from the plan set — **no
orphaned requirements**.

### Anti-Patterns Found

`grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` across all 9 files this phase
created or modified (`testenv.go`, `testenv_test.go`, the 6 converted test files,
`fixture_test.go`) → no matches. No debt markers.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `internal/platform/testenv/testenv.go` | 126, 128 | `Pool`'s `Ping`-failure branch interpolates the pgx error (`%v`) into `Fatalf`/`Skipf`, and pgx v5.7.2's `ConnectError.Error()` embeds `user=` and `database=` from the parsed config | WARNING (non-blocking) | Independently confirmed by direct code read: the message text observed in this verifier's own Scenario-C run contains `` failed to connect to `user=u database=nodb`: ... ``. This is CR-01 from `01-REVIEW.md`, filed as a code-review BLOCKER and adjudicated to MEDIUM in `01-REVIEW-ADJUDICATION.md`. I independently re-derive the same conclusion: this exact disclosure is pre-existing in the phase's own threat model (T-01-01, T-01-09), measured before any code was written, graded `medium` (below the phase's `security_block_on: high`), and explicitly accepted with rationale ("a test-only helper against a loopback compose service"). No must-have truth in any of the three plans' frontmatter requires the *Ping-failure* branch specifically to withhold the error — the sealed truth ("no component of `EPISTEMIC_OS_DB_URL` reaches the output") is scoped explicitly to "the unparseable-URL branch," which I verified is sealed (DSNLEAKCANARY count `0`). The remediation is sound and cheap (drop `err`, matching the `unparseableURLMsg` pattern) and is correctly queued for Phase 2, not fabricated as already-done. **I concur with the orchestrator's adjudication: this does not block Phase 1's goal**, because none of the phase's own stated success criteria or must-have truths cover this specific branch, and the risk was pre-assessed and accepted at design time rather than discovered as an oversight. It should not be forgotten going into Phase 2. |

### Known Process Discrepancies (documented, non-blocking)

These three items were flagged by the executor in the SUMMARYs and are called out in
the task brief. I re-ran each independently rather than trusting the SUMMARY's framing:

1. **Unfiltered `git diff --name-only 868d45b --` lists ~48 files, not 1.** Confirmed:
   this is due to ~32 pre-existing `.planning/`-only commits (base re-anchor, plan
   freezes, review-run archives, STATE.md updates) sitting between the approved base
   and phase execution — none authored by this phase's code work. The **filtered**
   forms every actual acceptance criterion specifies (`grep -v '^internal/' | grep -v
   '^\.planning/'`) print empty, which I re-verified directly above. Not a gap: the
   literal unfiltered form in the plans' prose `<verification>` narrative sections was
   never the operative acceptance criterion.
2. **`git status --porcelain` prints 3 lines (`.gsd/`, `.planning/config.json`,
   `.planning/milestone.lock`), not the 1-2 lines some acceptance criteria specify.**
   Confirmed via direct `git status --porcelain` run above. `.gsd/` and
   `.planning/milestone.lock` are GSD-tooling execution-machinery byproducts that did
   not exist when the plans were authored; adding them to `.gitignore` would itself
   violate the phase's own "nothing outside `internal/` and `.planning/`" audit scope
   in a different way. No tracked file is dirty. Not a gap in the phase's actual
   deliverable.
3. **`execution_shell.verified_present` never listed `make`,** which 29+ commands in
   01-03 depended on. Confirmed in the SUMMARY and consistent with the manifest;
   `make` is now installed (GNU Make 4.4.1, confirmed via `make --version` during this
   verification) and every `make gate`/`make up` invocation in this verification
   succeeded. This was a planning-process gap, not a code defect, and has already
   manifested and been resolved with human sign-off (recorded in the 01-03-SUMMARY).

None of these three items affect any must-have truth, artifact, or key link. They are
recorded per the task brief's instruction to judge them independently rather than
silently accept the executor's framing — my independent judgment agrees that none is
blocking.

### Human Verification Required

None. Every must-have truth, artifact, and key link was independently exercised with
a command this verifier ran itself (not inferred from SUMMARY.md), including the two
scenarios requiring a live database (Postgres was already running per the task brief;
it was stopped and restarted only for the `make gate`-without-a-database and
fixture-restore proofs, and left running afterward per 01-03's declared end state).

### Gaps Summary

No gaps. All five ROADMAP success criteria for Phase 1 are independently verified
against the live codebase:

1. Single shared helper (`internal/platform/testenv.Pool`/`.Fixture`) — confirmed sole
   decision point, 38/38 call sites converted, 0 duplicated `testPool` definitions.
2. Escalation flag converts each of the three environment conditions into a
   cause-naming failure — confirmed for unset URL, closed port, and unreadable
   fixture, independently, with status and message content asserted separately.
3. Flag unset preserves the phase-base skip behavior — confirmed at 38/38 skips
   (plain and shuffled), and for both the unreachable-database and unreadable-fixture
   branches individually.
4. `TestFixtureIntegrity` proves the preamble invariant; `acceptance_test.go` is
   byte-identical to the phase base and its two content-conditional skips remain
   unreached (PASS) for the pinned fixture.
5. `make gate` is green with the database genuinely stopped and again with it
   running; the Makefile and CI workflow are unchanged by git blob hash, not merely
   by commit-count; Postgres was left running as declared.

One code-review finding (CR-01, Ping-error metadata disclosure) remains open as a
documented, pre-assessed, and explicitly accepted `medium`-severity residual risk,
correctly queued for Phase 2 rather than silently dropped. It does not fail any
must-have truth stated for this phase and does not block phase completion.

---

_Verified: 2026-09-01_
_Verifier: Claude (gsd-verifier)_

---

## Orchestrator addendum — 2026-09-01

Appended by the orchestrator after the verifier returned. **It changes no finding, no
score and no status.** `status: passed`, 5/5 must-haves, stands exactly as verified.
Only one supporting citation above is stale, and this records why.

**What happened.** The verifier ran for ~11 minutes. During that window the
orchestrator amended `01-REVIEW-ADJUDICATION.md` twice — at `a555ead` (unrelated: the
ROADMAP base reference) and at `27fbd43` (the CR-01 adjudication itself). The verifier
read the pre-`27fbd43` version. That is an orchestrator sequencing error, not a
verifier error: the file moved under a running agent.

**What is therefore stale above.**

1. The CR-01 paragraph cites T-01-01 and T-01-09 as the covering threat entries. The
   on-point entry is **T-01-02** — *"`testenv.Pool`, the `Ping` error branch"* — which
   names this exact code path and states the disclosure outright. The verifier never
   reaches it, because the adjudication it read did not name it either. The conclusion
   (non-blocking) is **unchanged and better supported** by T-01-02 than by the two
   entries actually cited.

2. *"correctly queued for Phase 2 rather than silently dropped"* is **incorrect**. The
   remediation CR-01 proposes — dropping the pgx error from the message — was already
   raised during cross-AI planning review and **rejected with rationale**, recorded in
   `01-01-PLAN.md` under *Rejected, with rationale*: it carries the dial diagnosis
   Phase 3's PROOF-02 asserts against, and dropping it would replace real diagnosis
   with a category name. It is not a queued action item. It is a declined proposal,
   and re-queueing it without engaging that rationale is what `27fbd43` corrected.

**What this does NOT do.** It does not weaken the verdict. CR-01 is non-blocking on
stronger grounds than those cited. But it also must not be read as independent
corroboration of the orchestrator's adjudication: the verifier was reading that
adjudication, so on this one point the two artifacts are not independent sources.

**Live question, unresolved and owned by Phase 3.** T-01-02's acceptance is scoped to
*"a test-only helper against a loopback compose service"* and T-01-09's to throwaway
scenario DSNs. Both scopes hold for how this repository runs today. Neither is enforced
by `testenv.Pool` itself. Phase 2 turns this helper into the thing that decides whether
CI goes red.

Current disposition of CR-01 is in `01-REVIEW-ADJUDICATION.md` as amended at `27fbd43`.
The verifier's findings above are otherwise untouched.
