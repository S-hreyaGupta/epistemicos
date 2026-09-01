---
status: testing
phase: 01-escalation-mechanism-and-fixture-invariant
source: [01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md]
started: 2026-09-01T16:00:00Z
updated: 2026-09-01T16:00:00Z
---

## Current Test

number: 4
name: Contract: documentation placement
expected: |
  The flag is documented ONLY in the package doc comment.
  README and Makefile documentation are deferred to Phase 2, where the flag actually becomes part of the gate.
  Confirm the deferral is acceptable.
awaiting: user response

## Tests

<!-- Tests 1-6 are human dispositions: the five contract decisions Phase 2 and
     Phase 3 bind to, plus the one unresolved probe edge. Source: 01-03-SUMMARY.md
     "Contract decisions awaiting developer disposition" and coverage entry D11
     (reason: human_judgment). None is pre-decided. -->

### 1. Contract: package path and exported API surface
expected: `internal/platform/testenv` with `URLEnv`, `RequireEnv`, `Required() bool`, `Pool(t) *pgxpool.Pool`, `Fixture(t, path) []byte` (plus unexported `hostFromURL`, `unparseableURLMsg`) is the permanent package path and API surface. Phase 2's Makefile change and Phase 3's proof tests will bind to these names.
result: pass
note: "Accepted 2026-09-01 by Alex. Provenance, so it is not re-raised: the name `internal/platform/dbtest` comes from a ~142-line `dbtest.go` GSD wrote BEFORE the plan existed, deleted before the plan ran and never committed. It appears in no plan version, no manifest, no review transcript, and `git log --all -S'dbtest'` returns nothing. `internal/platform/testenv` was specified from the first planning commit `940727c` and named in the review-of-record manifest `d90b10d`. There was no rename and there is no deviation."


### 2. Contract: flag name and presence-based semantics
expected: `EPISTEMIC_OS_TEST_REQUIRE_DB` is presence-based — ANY non-empty value enables escalation, including the string "0". Rationale: a typo in the value should err toward enforcing rather than toward a vacuously green gate. Confirm before Phase 2 wires it into the Makefile.
result: pass
note: "Accepted 2026-09-01 by Alex — presence-based is right, a typo should fail toward enforcing. Accepted WITH a new requirement, raised by Alex and registered as GATE-06 (Phase 2): when escalation causes a failure the message must name the flag AND print its value. Measured at Phase 1 close and confirmed as a real gap: testenv.go:93 says only `EPISTEMIC_OS_TEST_REQUIRE_DB is set` without the value, and :126 (unreachable) and :152 (fixture) never name the flag at all. Someone who set `0` meaning off currently sees a failure that looks like a bug in a variable they believe they disabled."


### 3. Contract: the flag's scope is wider than its name
expected: The flag also escalates the cross-package fixture prerequisite — a filesystem condition — not just database availability. A reader would reasonably assume it affects only database setup. Either the name widens in Phase 2 (reviewer suggested `EPISTEMIC_OS_TEST_REQUIRE_ENV`) or the package doc comment is deemed sufficient.
result: pass
disposition: "WIDEN. Alex 2026-09-01: the doc comment is not enough. Registered as GATE-07 (Phase 2) — rename to EPISTEMIC_OS_TEST_REQUIRE_ENV. Measured blast radius: 2 occurrences in Go (const value + doc comment), 0 in Makefile/ci.yml. The exported identifier RequireEnv is unchanged, so the API surface accepted in test 1 stands. GATE-06 was amended in the same commit to name the flag via testenv.RequireEnv rather than the literal old string, so it survives the rename."


### 4. Contract: documentation placement
expected: The flag is documented ONLY in the package doc comment. README and Makefile documentation are deferred to Phase 2, where the flag actually becomes part of the gate. Confirm the deferral is acceptable.
result: [pending]

### 5. Contract: the deferred AC-14 empty-heading guard
expected: `acceptance_test.go` indexes `headings[0]` with no emptiness guard, so a deliberately heading-free fixture would PANIC rather than skip cleanly. Not fixed in Phase 1 because GATE-04 requires that file to stay byte-identical to the phase base. Decide: backlog item, or a Phase 2 change?
result: [pending]

### 6. Probe edge E1 — disposition required
expected: E1 (GATE-04) came back from the deterministic edge probe with NO category, so it carries no probe question. Does it need a requirement of its own, or is it inapplicable to a test-harness refactor? Accounting: 4 edges surfaced == 3 authored into 01-01's must_haves (E2, E3, E4) + 1 flagged here (E1). It is NOT dismissed — a disposition is required.
result: [pending]

<!-- Tests 7+ are deterministically covered by passing automated verification
     (uat.classify-coverage mode: coverage, auto_passed). Recorded pre-resolved,
     NOT presented as checkpoints. All were additionally re-measured by the
     orchestrator and by gsd-verifier against the live tree. -->

### 7. [01-01 D1] With EPISTEMIC_OS_TEST_REQUIRE_DB unset and EPISTEMIC_OS_DB_URL unset, go test ./... -count=1 exits 0 and reports exactly 38 test-level skips, plain and -shuffle=on
expected: With EPISTEMIC_OS_TEST_REQUIRE_DB unset and EPISTEMIC_OS_DB_URL unset, go test ./... -count=1 exits 0 and reports exactly 38 test-level skips, plain and -shuffle=on
result: pass
source: automated
coverage_id: D1
verified_by: env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v | grep -c '^--- SKIP'; same command with -shuffle=on

### 8. [01-01 D2] With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL unset, the store and approved packages exit non-zero and name both env vars
expected: With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL unset, the store and approved packages exit non-zero and name both env vars
result: pass
source: automated
coverage_id: D2
verified_by: EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 (status + grep, asserted independently); EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/approved/... -count=1

### 9. [01-01 D3] With EPISTEMIC_OS_TEST_REQUIRE_DB set and a closed-port EPISTEMIC_OS_DB_URL, the run exits non-zero and names that host and port
expected: With EPISTEMIC_OS_TEST_REQUIRE_DB set and a closed-port EPISTEMIC_OS_DB_URL, the run exits non-zero and names that host and port
result: pass
source: automated
coverage_id: D3
verified_by: EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1

### 10. [01-01 D4] With the flag unset and the same closed-port URL, TestSaveRun_FixtureRoundTripsAllOffsets still reports SKIP and the package exits 0 â€” the phase-base branch is preserved
expected: With the flag unset and the same closed-port URL, TestSaveRun_FixtureRoundTripsAllOffsets still reports SKIP and the package exits 0 â€” the phase-base branch is preserved
result: pass
source: automated
coverage_id: D4
verified_by: env -u EPISTEMIC_OS_TEST_REQUIRE_DB ... go test -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 -v

### 11. [01-01 D5] The parse-failure branch emits unparseableURLMsg only â€” no component of the connection string, including a database-name leak token, reaches the output; measured to fail at the phase base and pass after this change
expected: The parse-failure branch emits unparseableURLMsg only â€” no component of the connection string, including a database-name leak token, reaches the output; measured to fail at the phase base and pass after this change
result: pass
source: automated
coverage_id: D5
verified_by: internal/platform/testenv/testenv_test.go#TestUnparseableURLMsg_Control_NoLeak; EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@ bad host/DSNLEAKCANARY' go test ./internal/adapters/secondary/store/... -count=1 (4 independent assertions); same with the keyword/value form host=x po

### 12. [01-01 D6] All 38 former call sites reach testenv.Pool(t) directly across 6 files; neither store nor approved defines its own pool helper
expected: All 38 former call sites reach testenv.Pool(t) directly across 6 files; neither store nor approved defines its own pool helper
result: pass
source: automated
coverage_id: D6
verified_by: grep -rno 'testenv.Pool(t)' --include=*_test.go internal | wc -l == 38, across 6 files

### 13. [01-01 D7] The cross-package fixture read in segmentation_test.go goes through testenv.Fixture; the in-package loadFixture in the segment domain is untouched and stays fatal
expected: The cross-package fixture read in segmentation_test.go goes through testenv.Fixture; the in-package loadFixture in the segment domain is untouched and stays fatal
result: pass
source: automated
coverage_id: D7
verified_by: grep -c 'testenv.Fixture(t' segmentation_test.go == 1; grep -c 'os.ReadFile' == 0; internal/platform/testenv/testenv_test.go#TestFixture_SuccessPath

### 14. [01-01 D8] Nothing outside internal/ and .planning/ changed relative to the approved phase base 868d45b; the mechanism exists and enforces nothing by default
expected: Nothing outside internal/ and .planning/ changed relative to the approved phase base 868d45b; the mechanism exists and enforces nothing by default
result: pass
source: automated
coverage_id: D8
verified_by: git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3 -- | grep -v '^internal/' | grep -v '^\\.planning/' (empty after each task)

### 15. [01-02 D1] TestFixtureIntegrity fails, naming testdata/demo.md, if the pinned fixture ever has no preamble, a zero-offset first heading, a whitespace-only preamble, or no headings at all
expected: TestFixtureIntegrity fails, naming testdata/demo.md, if the pinned fixture ever has no preamble, a zero-offset first heading, a whitespace-only preamble, or no headings at all
result: pass
source: automated
coverage_id: D1
verified_by: internal/core/domain/segment/fixture_test.go#TestFixtureIntegrity; internal/core/domain/segment/fixture_test.go#TestPreambleInvariant_Control

### 16. [01-02 D2] The declaration gate (fixtureHasPreamble) waives only the two preamble checks, never the no-headings check, and is proven in both directions with synthetic inputs
expected: The declaration gate (fixtureHasPreamble) waives only the two preamble checks, never the no-headings check, and is proven in both directions with synthetic inputs
result: pass
source: automated
coverage_id: D2
verified_by: internal/core/domain/segment/fixture_test.go#TestPreambleInvariant_Control/declared_preamble-free; internal/core/domain/segment/fixture_test.go#TestPreambleInvariant_Control/declared_preamble-free,_but_no_headings

### 17. [01-02 D3] The AC-14 content-conditional skips in acceptance_test.go survive byte-identical and remain unreachable (PASS, not SKIP) for the pinned fixture
expected: The AC-14 content-conditional skips in acceptance_test.go survive byte-identical and remain unreachable (PASS, not SKIP) for the pinned fixture
result: pass
source: automated
coverage_id: D3
verified_by: internal/core/domain/segment/acceptance_test.go#TestAC14_PreHeadingContentHasNoNode

### 18. [01-03 D1] Default run (no DB, no flag) reproduces the phase base exactly: exit 0, 38 test-level skips by two independent counting methods, unchanged under -shuffle=on
expected: Default run (no DB, no flag) reproduces the phase base exactly: exit 0, 38 test-level skips by two independent counting methods, unchanged under -shuffle=on
result: pass
source: automated
coverage_id: D1
verified_by: env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate; go test ./... -count=1 -v | grep -c '^--- SKIP' == 38; -json filtered by \"Test\": also 38; -shuffle=on -json also 38

### 19. [01-03 D2] Non-escalated unreachable database still SKIPs (Scenario A2) â€” the branch measured at the phase base, half of ROADMAP criterion 3, uncovered by cycle 1
expected: Non-escalated unreachable database still SKIPs (Scenario A2) â€” the branch measured at the phase base, half of ROADMAP criterion 3, uncovered by cycle 1
result: pass
source: automated
coverage_id: D2
verified_by: env -u EPISTEMIC_OS_TEST_REQUIRE_DB EPISTEMIC_OS_DB_URL=postgres://u:pw@127.0.0.1:1/nodb go test -run TestSaveRun_FixtureRoundTripsAllOffsets -v

### 20. [01-03 D3] Escalated with URL unset (Scenario B): store and approved packages both exit non-zero and name both EPISTEMIC_OS_DB_URL and EPISTEMIC_OS_TEST_REQUIRE_DB; the fixture branch is not reached (edge E2)
expected: Escalated with URL unset (Scenario B): store and approved packages both exit non-zero and name both EPISTEMIC_OS_DB_URL and EPISTEMIC_OS_TEST_REQUIRE_DB; the fixture branch is not reached (edge E2)
result: pass
source: automated
coverage_id: D3
verified_by: EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 (33 name-hits each var, 0 testdata/demo.md hits); same against ./internal/adapters/secondary/approved/... (5 name-hits each var)

### 21. [01-03 D4] Escalated against a closed port (Scenario C): non-zero exit, output names the specific host:port
expected: Escalated against a closed port (Scenario C): non-zero exit, output names the specific host:port
result: pass
source: automated
coverage_id: D4
verified_by: EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL=postgres://u:pw@127.0.0.1:1/nodb go test ./internal/adapters/secondary/store/... (status 1, 127.0.0.1:1 count 33)

### 22. [01-03 D5] Connection-string disclosure control (Scenario D): a database-name leak token measured present (count 1) at the phase base is absent (count 0) after this phase's mechanism, on both URL-form and keyword/value-form malformed DSNs, alongside a passing negative control proving the detector has teeth
expected: Connection-string disclosure control (Scenario D): a database-name leak token measured present (count 1) at the phase base is absent (count 0) after this phase's mechanism, on both URL-form and keyword/value-form malformed DSNs, alongside a passing negative control proving the detector has teeth
result: pass
source: automated
coverage_id: D5
verified_by: EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@ bad host/DSNLEAKCANARY' go test ./internal/adapters/secondary/store/... (status 1, EPISTEMIC_OS_DB_URL present, DSNLEAKCANARY count 0, 'cannot parse' count 0); same with host=x port=notanumber password=pw dbname=DSNLEAKCANARY (iden

### 23. [01-03 D6] Non-enforcement audit: no commit from the approved phase base to HEAD touches the Makefile or CI workflow; the full diff touches nothing outside internal/ and .planning/; both gate-file git blob hashes are unchanged
expected: Non-enforcement audit: no commit from the approved phase base to HEAD touches the Makefile or CI workflow; the full diff touches nothing outside internal/ and .planning/; both gate-file git blob hashes are unchanged
result: pass
source: automated
coverage_id: D6
verified_by: git log --format=%H 868d45b..HEAD -- Makefile .github/workflows/ci.yml (empty); git diff --name-only 868d45b..HEAD | grep -v '^internal/' | grep -v '^\\.planning/' (empty); git rev-parse HEAD:Makefile == 63d55631...; git rev-parse HEAD:.github/workflows/ci.yml == fdbf98f4...

### 24. [01-03 D7] Escalated-green: with a live database, the store and approved packages execute every test that skipped without one (name-set containment, 38-of-38) and skip none (independent zero-skip count), with the plain run also exiting 0
expected: Escalated-green: with a live database, the store and approved packages execute every test that skipped without one (name-set containment, 38-of-38) and skip none (independent zero-skip count), with the plain run also exiting 0
result: pass
source: automated
coverage_id: D7
verified_by: comm -23 base_skips.txt esc_pass.txt == empty (38 baseline skip names, all present among 42 escalated pass names); capture-form: st==0 AND escalated -json skip count carrying \"Test\": == 0; plain escalated run also exits 0

### 25. [01-03 D8] Preserved fixture skip with a live database (flag unset): moving the fixture under the fail-closed trap and running the round-trip test by name exits 0 and reports SKIP â€” closing the second half of ROADMAP criterion 3
expected: Preserved fixture skip with a live database (flag unset): moving the fixture under the fail-closed trap and running the round-trip test by name exits 0 and reports SKIP â€” closing the second half of ROADMAP criterion 3
result: pass
source: automated
coverage_id: D8
verified_by: trap-guarded move + env -u EPISTEMIC_OS_TEST_REQUIRE_DB go test -run TestSaveRun_FixtureRoundTripsAllOffsets -v (status 0, '--- SKIP: TestSaveRun_FixtureRoundTripsAllOffsets' present)

### 26. [01-03 D9] Escalated fixture failure: same move, flag set, exits non-zero and names the fixture path; the fixture is restored byte-identical (SHA-256 equal before and after) with the trap cleared only after the restore and hash comparison both succeeded
expected: Escalated fixture failure: same move, flag set, exits non-zero and names the fixture path; the fixture is restored byte-identical (SHA-256 equal before and after) with the trap cleared only after the restore and hash comparison both succeeded
result: pass
source: automated
coverage_id: D9
verified_by: the exact fail-closed trap command from Task 2's acceptance criteria, printing FIXTURE_FAIL_OK with no *_TRAP_ARMED marker; go test ./internal/core/domain/segment/... -run TestFixtureIntegrity -count=1 (post-restore integrity, PASS)

### 27. [01-03 D10] make gate is measured green with the compose database genuinely stopped and again with it running, and the database is left running as the plan's declared end state
expected: make gate is measured green with the compose database genuinely stopped and again with it running, and the database is left running as the plan's declared end state
result: pass
source: automated
coverage_id: D10
verified_by: docker compose stop postgres && make gate (exit 0) && make up && make gate (exit 0) && docker compose ps --services --filter status=running includes postgres

## Summary

total: 27
passed: 24
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

[none yet]
