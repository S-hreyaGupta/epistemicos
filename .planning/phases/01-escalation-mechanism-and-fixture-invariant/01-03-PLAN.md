---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 03
type: execute
wave: 2
depends_on: ["01-01", "01-02"]
files_modified: []
autonomous: true
requirements: [GATE-04, GATE-05]

estimate:
  tokens: 36000
  raw_tokens: 36000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "`make gate` exits 0 with no database present, exactly as at the phase base commit — the mechanism built in 01-01 enforces nothing"
    - "`make gate` exits 0 with a reachable database and migrations applied"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and a reachable database, the store and approved packages report 0 skipped tests and 0 failures"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set, each of the three environment conditions produces a failure naming that specific cause: the variable, the host, the fixture path"
    - "No commit in this phase touches the Makefile or the CI workflow"
    - "The password component of a connection string appears in no output on any escalated failure path"
  artifacts:
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md
  key_links:
    - "The escalated-green run is the only check that proves the helper does not fail spuriously when the database IS present — without it, a helper that always failed would satisfy every other criterion in this phase"
    - "The unchanged-gate check is what makes this phase non-enforcing rather than merely intended to be; Phase 2 depends on inheriting a green tree"
  prohibitions:
    - "This phase must not wire enforcement. No change to the Makefile and no change to the CI workflow, even though both are one line away from turning the mechanism on — and the temptation is highest here, in the plan that measures the difference."
    - "The escalation flag must not default to on. With EPISTEMIC_OS_TEST_REQUIRE_DB unset, every test that skips at the phase base must still skip and the suite must still exit 0."
    - "The two content-conditional skips in the segment acceptance test must not be deleted, converted into failures, or made conditional on the escalation flag. A fixture that genuinely lacks a preamble is real signal, and turning that into a gate failure is the exact conflation this milestone exists to prevent."
    - "A failing check in this plan must not be resolved by weakening the check. If the escalated run does not reach 0 skips, the helper is wrong; the target is not."
---

<objective>
Measure that the escalation mechanism built in 01-01 works when the database is
present, that each escalated condition names its own cause, and — the hard
boundary of this phase — that `make gate` behaves exactly as it did before any of
it landed.

Purpose: this phase's whole claim is "the mechanism exists and enforces nothing".
Both halves need evidence. Without the escalated-green run, a helper that failed
unconditionally would satisfy every other criterion in the phase. Without the
unchanged-gate run, "non-enforcing" is an intention rather than a measurement, and
Phase 2 would inherit a red tree it did not cause.

Output: a SUMMARY recording the measured baseline that Phase 2 will be diffed
against and that Phase 3's proof tests will assert.

**This plan changes no source files.** `files_modified` is deliberately empty. If
a check fails, the fix belongs in 01-01 or 01-02 and this plan re-runs.
</objective>

## Artifacts this phase produces

This plan produces **no code symbols**. Its only artifact is its SUMMARY.

The new symbols this phase creates all belong to plan 01-01 — the
`internal/platform/testenv` package, its exported `URLEnv`, `RequireEnv`,
`Required`, `Pool` and `Fixture`, its unexported `hostFromURL`, and the
`EPISTEMIC_OS_TEST_REQUIRE_DB` environment variable. See that plan's artifacts
table. Plan 01-02 creates no symbols at all.

`EPISTEMIC_OS_DB_URL`, `make gate`, `make up`, `make migrate` and the CI workflow
are all pre-existing and are read, never written, by this plan.

## Flagged assumptions — spec-less edge probe

No SPEC exists for this phase. The deterministic edge probe over GATE-04 and
GATE-05 returned 4 applicable edges, **0 resolved**. All four are reproduced here
because this is the plan a human reviews, and none may be silently dropped:
4 surfaced == 0 authored into `must_haves.truths` + 4 flagged.

| # | Requirement | Category | Probe | Status |
|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (uncategorized — no probe question was generated; review manually) | **unresolved — flagged** |
| E2 | GATE-05 | adjacency | When two things are exactly equal or just touch, do they merge, collide, or separate? | **unresolved — flagged** |
| E3 | GATE-05 | empty | What is the result for empty, single-element, or null input? | **unresolved — flagged** |
| E4 | GATE-05 | ordering | When elements compare equal, is output order specified and stable? | **unresolved — flagged** |

**Honest note.** These are generic data-structure edges. GATE-04 and GATE-05
describe a test harness's skip-or-fail decision, not a collection with adjacency,
emptiness or sort order, so the poor fit is expected. That is a reason to put them
in front of a human to dismiss, not a reason for the planner to dismiss them.

Offered as context, **not** as resolutions — every row above remains unresolved:
E3 has a plausible referent in the empty-string value of the escalation flag and
the empty host returned for a keyword/value DSN, both handled and unit-tested in
01-01 Task 1. E1, E2 and E4 have no evident referent in this phase.

<execution_context>
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/workflows/execute-plan.md
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md
@.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md
</context>

## Verified ground truth

Measured in this repository at commit `fcebad1`, before any plan in this phase ran.
This is the baseline every check below is compared against.

- `go test ./... -count=1` with no database: **exit 0, 38 skipped tests.**
- `make gate` is `vet`, then a `gofmt -l .` check, then `go build ./...`, then
  `go test ./... -count=1`. Nothing in it starts PostgreSQL.
- The local DSN for the compose service is
  `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`.
  `make up` starts it and waits for readiness; `make migrate` applies migrations
  and requires `EPISTEMIC_OS_DB_URL` to be exported.
- The store package's cross-package fixture read resolves
  `../../../core/domain/segment/testdata/demo.md` and runs only after a pool is
  obtained, so exercising the unreadable-fixture path requires a live database.
- `.github/workflows/ci.yml` line 36 already sets `EPISTEMIC_OS_DB_URL` and the
  workflow already provisions PostgreSQL and applies migrations, delivered at
  `868d45b`. Neither that file nor the Makefile may be edited in this phase.

**Phase base commit: `fcebad1`.** Confirm it is an ancestor of HEAD before using it
in a diff; if other work landed first, substitute the actual commit this phase
branched from and record the substitution in the summary.

<tasks>

<task type="auto">
  <name>Task 1: Database-free behavioral matrix and non-enforcement audit</name>
  <files>none — verification only, no file is written by this task</files>

  <read_first>
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md (the exported signatures and the failure text 01-01 observed, so this task compares against a stated baseline rather than re-deriving one)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md (the fixture invariant result and the AC-14 baseline)
    - Makefile (lines 38-46 — the exact gate definition being held constant)
    - internal/platform/testenv/testenv.go (the helper as built, to confirm the observed messages come from the branches this plan believes they do)
  </read_first>

  <action>
Run the four scenarios that need no database, and the non-enforcement audit. Record
every observed exit status and message verbatim; the summary is the artifact.

Scenario A, the preserved default. With both `EPISTEMIC_OS_DB_URL` and
`EPISTEMIC_OS_TEST_REQUIRE_DB` explicitly removed from the environment, run the
full suite. It must exit 0 and report exactly 38 skipped tests — the count measured
at the phase base. Use `env -u` rather than assuming the variables are unset, since
a developer shell may export the local DSN.

Scenario B, escalated with no URL. With the flag set and the URL removed, run the
store package and then the approved package. Each must exit non-zero and name
`EPISTEMIC_OS_DB_URL` in its output.

Scenario C, escalated against a closed port. With the flag set and the URL
addressing `127.0.0.1` port 1, run the store package. It must exit non-zero and the
output must contain that host and port, proving the message names the specific
machine it could not reach rather than restating the variable.

Scenario D, the credential audit. Repeat scenario C with a distinctive password in
the DSN, and repeat it again with a DSN malformed enough that the pool constructor
itself rejects it — that constructor echoes its input verbatim, which is the leak
T-01-01 exists for. In both runs the password must not appear anywhere in the
output.

Then the non-enforcement audit. Confirm no commit in this phase touched the Makefile
or the CI workflow, by listing commits from the phase base to HEAD restricted to
those two paths. Confirm the full diff from the phase base touches nothing outside
`internal/` and `.planning/`. Confirm the gate itself still runs green with no
database.

If any scenario fails, do not adjust the scenario. Report it and stop — the defect
belongs to 01-01 or 01-02, and this plan re-runs after that fix.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate &amp;&amp; test "$(env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&amp;1 | grep -c '^--- SKIP')" = "38" &amp;&amp; test -z "$(git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml)" &amp;&amp; echo NONENFORCING_OK</automated>
  </verify>

  <acceptance_criteria>
    - Scenario A: `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - Scenario A: `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `38`.
    - Scenario B: `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1` exits non-zero and its output contains `EPISTEMIC_OS_DB_URL`.
    - Scenario B: the same command against `./internal/adapters/secondary/approved/...` exits non-zero and its output contains `EPISTEMIC_OS_DB_URL`.
    - Scenario C: `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1 2>&1` exits non-zero and contains `127.0.0.1:1`.
    - Scenario D: `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:PWLEAKCANARY@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1 2>&1 | grep -c PWLEAKCANARY` prints `0`.
    - Scenario D: `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:PWLEAKCANARY@ bad host/db' go test ./internal/adapters/secondary/store/... -count=1 2>&1 | grep -c PWLEAKCANARY` prints `0`.
    - Audit: `git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml` prints nothing.
    - Audit: `git diff --name-only fcebad1..HEAD | grep -vc '^\(internal/\|.planning/\)'` prints `0`.
    - Audit: `git rev-parse --verify fcebad1` succeeds and `git merge-base --is-ancestor fcebad1 HEAD` exits 0, confirming the recorded phase base is valid.
  </acceptance_criteria>

  <done>
Every database-free claim in this phase is measured and recorded: the default run
is bit-for-bit the same outcome as the phase base at 38 skips and exit 0, two of the
three escalated conditions name their own cause, no credential reaches the output,
and neither the Makefile nor the CI workflow was touched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Escalated-green and unreadable-fixture proof against a live database</name>
  <files>none — verification only; the fixture is moved and restored within the task and must end byte-identical</files>

  <precondition>PostgreSQL is running and migrated: `make up` succeeds, `EPISTEMIC_OS_DB_URL` is exported as `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`, and `make migrate` exits 0 — without a live database neither claim in this task is decidable and execution must halt rather than record an unverified pass.</precondition>

  <read_first>
    - Makefile (lines 18-23 and 47-48 — the up and migrate targets and the readiness wait, so the precondition is satisfied the same way CI does it)
    - internal/adapters/secondary/store/segmentation_test.go (the fixture-round-trip test — the only test that exercises the unreadable-fixture path, and the relative path it resolves)
    - internal/platform/testenv/testenv.go (the fixture branch, to confirm the observed message comes from the escalated path)
  </read_first>

  <action>
Prove the two claims that require a real database.

First, escalated green. With the database up, migrations applied, the DSN exported
and the escalation flag set, run the store and approved packages. Every test must
run: zero skipped and zero failed. This is the check that distinguishes a working
mechanism from one that simply always fails — without it, a helper hard-coded to
fail would satisfy every other criterion in this phase.

Second, the unreadable fixture. With the same environment, move
`internal/core/domain/segment/testdata/demo.md` aside, run only the store package's
fixture round-trip test by name, and confirm it fails with a message naming that
fixture path. Restore the file unconditionally — sequence the restore so it runs
whether the test command succeeded or failed, never conditionally on success. Scope
the run to the store package alone so the segment domain package, which owns that
fixture, is not compiled against a missing file during the window.

After restoring, confirm the working tree is clean and the fixture's hash still
matches by running the segment package's integrity test, which pins it. Do not
proceed to Task 3 until both are confirmed.

Record the exact escalated failure message for the fixture path in the summary.
Phase 3's proof test for GATE-03 asserts against this text, so an approximation is
not good enough.

If the escalated run reports any skip or any failure, stop and report. Do not
narrow the package selection, do not add a skip exclusion, and do not lower the
target — the target is the requirement.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; export EPISTEMIC_OS_DB_URL='postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable' &amp;&amp; make migrate &amp;&amp; test "$(EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -v 2>&amp;1 | grep -c '^--- SKIP')" = "0" &amp;&amp; EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 &amp;&amp; echo ESCALATED_GREEN_OK</automated>
  </verify>

  <acceptance_criteria>
    - `make up` exits 0 and `make migrate` exits 0 with the DSN exported.
    - `EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `0`.
    - The same command filtered for `^--- FAIL` prints `0`, and the plain (non-`-v`) run exits 0.
    - The same command filtered for `^--- PASS` prints at least `38` — every former call site actually ran.
    - With the fixture moved aside, `EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 2>&1` exits non-zero and its output contains `core/domain/segment/testdata/demo.md`.
    - After restoring, `git status --porcelain` prints nothing except the pre-existing untracked `.planning/config.json`.
    - After restoring, `go test ./internal/core/domain/segment/... -run TestFixtureIntegrity -count=1` exits 0 — the fixture's pinned hash and length still match, proving the move-and-restore was lossless.
    - `env -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0 with the database still up — the gate is green in the database-present case too.
  </acceptance_criteria>

  <done>
With a live database the escalated run executes all 38 database-backed tests and
skips none, and the third environment condition — an unreadable fixture — produces
a failure naming that path. The fixture is restored and still matches its pin.
  </done>
</task>

<task type="auto">
  <name>Task 3: Consolidate the phase baseline and surface the contract decisions for sign-off</name>
  <files>none — verification and summary only, no source file is written</files>

  <read_first>
    - .planning/ROADMAP.md (Phase 1 success criteria, all five — the consolidation is a judgment against these, not against the plan)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md (the exported names and flag semantics Phase 2 and Phase 3 bind to)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md (the fixture invariant result and the AC-14 baseline)
    - Makefile (the gate target, to confirm by reading that nothing was wired)
  </read_first>

  <action>
Run the final both-environments confirmation and assemble the baseline. Run every
command here directly — do not ask the developer to run anything.

First, `make gate` with no database reachable and no escalation flag. This is the
developer-without-Docker case the whole skip policy exists to protect. Stop the
compose database first if Task 2 left it running, so the case is real rather than
assumed, then bring it back up afterward.

Second, `make gate` with the database up and the DSN exported, still with no
escalation flag. Both must exit 0, and that pair is the phase's central claim: the
mechanism exists and the gate is unmoved.

Then assemble the summary. Collect from Tasks 1 and 2 every exit status, the skip
counts, and the verbatim escalated failure message for each of the three
conditions, redacting passwords. Phase 3 asserts against that text, so record it
exactly rather than paraphrasing.

Finally, write into the summary — for the developer to accept or amend at
end-of-phase review — the three contracts Phase 2 and Phase 3 will bind to, since
changing any of them later is mechanical but no longer local to one package:

- The package path `internal/platform/testenv` and the exported function names.
- The flag name `EPISTEMIC_OS_TEST_REQUIRE_DB`, and that any non-empty value
  enables it, so the string zero enables it too. State the rationale: a typo in the
  value then errs toward enforcing rather than toward a vacuously green gate.
- That the flag is documented in the package doc comment only, with README and
  Makefile documentation deferred to Phase 2, where the flag actually becomes part
  of the gate.

Also carry forward the four unresolved probe edges E1 through E4 verbatim, as open
items awaiting disposition. Do not dismiss any of them; the planner did not, and
neither should the executor.

If either gate run exits non-zero, stop and report. The defect belongs to 01-01 or
01-02 and this plan re-runs after it is fixed.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; docker compose stop postgres &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate &amp;&amp; make up &amp;&amp; env -u EPISTEMIC_OS_TEST_REQUIRE_DB EPISTEMIC_OS_DB_URL='postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable' make gate &amp;&amp; echo GATE_UNCHANGED_BOTH_WAYS</automated>
    <human-check>Review the recorded baseline and accept or amend three contracts Phase 2 and Phase 3 bind to: (1) the package path `internal/platform/testenv` and its exported function names; (2) the flag name `EPISTEMIC_OS_TEST_REQUIRE_DB` and its presence-based semantics, under which the string zero enables escalation because a typo in the value should err toward enforcing rather than toward a vacuously green gate; (3) documenting the flag in the package doc comment only, deferring README and Makefile documentation to Phase 2. Then give a disposition for each of the four unresolved probe edges E1 through E4 — whether each becomes a requirement or is dismissed as inapplicable to a test-harness refactor.</human-check>
  </verify>

  <acceptance_criteria>
    - With the compose database stopped, `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - With the database up and the DSN exported, `env -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - `git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml` still prints nothing after all three plans have run.
    - The summary records an exit status and a skip count for every scenario in Tasks 1 and 2.
    - The summary contains the verbatim escalated failure text for all three conditions — unset variable, unreachable host, unreadable fixture — with passwords redacted.
    - The summary lists all three contract decisions and all four probe edges E1 through E4 as items awaiting the developer's disposition, none pre-dismissed.
    - `git status --porcelain` prints nothing except the pre-existing untracked `.planning/config.json`.
  </acceptance_criteria>

  <done>
`make gate` is measured green in both environments, the phase baseline is recorded
in a form Phase 2 can diff against and Phase 3 can assert against, and the three
contract decisions plus the four probe edges are queued for the developer's
end-of-phase disposition rather than settled on their behalf.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| verification process → CI log and terminal | Every scenario in this plan deliberately constructs failing connection strings; their text is printed |
| verification process → working tree | Task 2 moves a hash-pinned fixture aside and must restore it exactly |
| verification process → local PostgreSQL | The exported DSN carries credentials for the compose service |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01-09 | Information Disclosure | the DSNs constructed in Scenarios C and D | high | mitigate | This plan is where a real password would leak if T-01-01's mitigation regressed, so Scenario D is the standing audit for it: two runs with a distinctive password, one through the connect path and one through the parse path that is known to echo its input, each asserting the password count in the output is zero. Severity high meets `security_block_on: high`, so a non-zero count blocks the phase. The DSNs used here carry a throwaway credential, never a real one. |
| T-01-10 | Tampering | `testdata/demo.md` during the Task 2 move | high | mitigate | Moving a hash-pinned fixture risks leaving the tree corrupt if the run aborts. Mitigated by sequencing the restore so it executes regardless of the test's exit status, by scoping the test run to the store package so the owning package is never compiled against the gap, and by two post-conditions: a clean `git status --porcelain` and a passing integrity test that re-checks the pinned hash and byte length. |
| T-01-11 | Elevation of Privilege | the local compose PostgreSQL instance | low | accept | Credentials are the published compose defaults on a loopback port, used only for tests. No production data is reachable. Out of scope at ASVS L1. |
| T-01-12 | Repudiation | the escalated-green measurement | medium | mitigate | A recorded "0 skips" that was never actually run against a database would make the phase's central claim unfalsifiable — the exact failure mode this milestone exists to remove. Mitigated by the task precondition, which halts rather than recording an unverified pass, and by the PASS-count criterion requiring at least 38 tests to have actually executed. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan installs nothing and writes no source. `go.mod` is unchanged across the whole phase. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
The phase is verified when all five ROADMAP success criteria are measured, not
argued:

1. One helper owns the decision — 01-01 Task 2 criteria: 38 call sites, 6 files,
   0 remaining local definitions.
2. Escalated, each of the three conditions names its cause — Scenarios B and C here
   for the variable and the host, Task 2 here for the fixture path.
3. Flag unset, skips exactly as today — Scenario A: exit 0 and 38 skips, matching
   the count measured at the phase base.
4. The fixture invariant holds and the AC-14 declines stay green and silent — 01-02
   Tasks 1 and 2.
5. `make gate` behaves exactly as before — Task 3 runs it with the compose database
   genuinely stopped and again with it up, and both must exit 0.

Plus the standing non-enforcement audit: no commit in this phase touches the
Makefile or the CI workflow, and no path outside `internal/` and `.planning/`
appears in the phase diff.
</verification>

<success_criteria>
- The default run reproduces the phase base exactly: exit 0, 38 skips.
- The escalated run against a live database executes all 38 and skips none.
- Each of the three environment conditions produces a failure naming that specific cause, with the fixture message recorded verbatim for Phase 3.
- No password appears in any output, through either the connect path or the parse path.
- The Makefile and the CI workflow are untouched, and `make gate` is measured green with the database genuinely stopped and again with it up.
- The three contracts Phase 2 and Phase 3 bind to, and the four unresolved probe edges, are queued for the developer's end-of-phase disposition rather than settled on their behalf.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md` when done.

Record in it, as the baseline Phase 2 will be diffed against and Phase 3 will assert
against: the exit status and skip count for every scenario; the verbatim escalated
failure message for each of the three conditions, with passwords redacted; the
confirmed phase base commit; the three contract decisions awaiting the developer's
acceptance or amendment; and the four unresolved probe edges awaiting disposition.

The two sign-off blocks are harvested from Task 3's `<verify><human-check>` into the
phase UAT at end-of-phase review, so they reach the developer in one batch rather
than halting execution mid-flight.
</output>
