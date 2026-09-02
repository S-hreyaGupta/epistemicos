---
status: testing
phase: 02-enforcement-and-a-single-gate-definition
source: [02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md]
started: 2026-09-02T00:00:00Z
updated: 2026-09-02T00:00:00Z
---

## Current Test

number: 14
name: DISPOSITION — the documented happy path does not work
awaiting: user response

## Tests

<!-- Tests 1-13 are behavioural. Tests 14-20 are human dispositions.
     Tests 2-13 were run by the orchestrator at the operator's instruction,
     EXACTLY as each procedure is written, from a clean shell, supplying
     nothing a procedure does not state. Where something had to be supplied,
     it is recorded as a procedure gap, not as a setup step. -->

### 1. Cold Start Smoke Test
expected: **In Git Bash (POSIX shell).** `docker compose down -v`, then `make up`, then **export the compose DSN**, then `make gate` — the database comes up from nothing, migrations apply, the gate exits 0.
result: issue
reported: "(1) In PowerShell both fail on shell incompatibility: make up 'The system cannot find the path specified'; make gate 'unformatted' is not recognized. Make defaults to cmd on Windows unless SHELL is set. (2) In Git Bash, following the procedure literally, make gate FAILED on EPISTEMIC_OS_DB_URL not set. The failure is the test's procedure, not the gate — make up starts the database, make gate demands one, and nothing joins them."
severity: major
gap_ref: [G-02-1a, G-02-1b, G-02-1c]
orchestrator_correction: |
  CORRECTION. I earlier recorded this re-run as "passed". It did not pass the
  procedure as written — it passed because I prefixed EPISTEMIC_OS_DB_URL=... ,
  silently supplying the step the procedure omits. I confirmed a test by running
  something other than what the test says, while recording a finding about that
  exact defect class. The operator caught it by running what was written.

  What the operator's failure output demonstrates is the phase's central claim,
  reached by accident: GATE-01 names the variable, GATE-06 names the flag AND its
  value, remediation rides in the same sentence, and it FAILS rather than skipping.
  At the phase base this same condition exited 0 and printed ok.

  Verified separately, with the DSN exported: docker compose down -v removed the
  pg_data volume, make up exited 0, make gate exited 0 against an empty database
  with migrations applying from nothing. The freshly CREATED container reported
  127.0.0.1:5432->5432/tcp, so SEC-01 holds on a from-scratch create and not only
  on the recreate 02-03 performed.

### 2. The gate is green with the database up
expected: `make gate` exits 0 with compose postgres running.
result: issue
reported: "Run exactly as written from a clean shell: exit=2, failing on GATE-01 (EPISTEMIC_OS_DB_URL is not set). The procedure omits the export."
severity: major
gap_ref: G-02-1c
orchestrator_note: "The gate's behaviour is correct — it names the variable and fails rather than skipping. The defect is the procedure. With the export supplied, the gate exits 0 (measured repeatedly this session)."

### 3. GATE-01 — unset database URL
expected: `env -u EPISTEMIC_OS_DB_URL make gate` exits non-zero, the message names `EPISTEMIC_OS_DB_URL`, and `new migrator` does NOT appear — the preflight speaks before migrate can.
result: pass
measured: "exit=2; names EPISTEMIC_OS_DB_URL; 'new migrator' absent (0 occurrences) — the preflight reported before migrate could run."

### 4. GATE-02 — unreachable database
expected: `make gate` with a closed-port DSN exits non-zero and names the host (`127.0.0.1:1`) plus the remedy `make up`.
result: pass
measured: "exit=2; 'cannot reach postgres at 127.0.0.1:1 (from EPISTEMIC_OS_DB_URL) — run make up: ... target machine actively refused it'; 'new migrator' absent (0)."

### 5. GATE-03 — unreadable fixture
expected: With `internal/core/domain/segment/testdata/demo.md` moved aside and the database up, `make gate` exits non-zero and the message names the fixture path.
result: issue
reported: "Run exactly as written (fixture moved aside, container up, no export stated): exit=2 but the fixture path is NEVER NAMED — it fails on GATE-01 instead."
severity: major
gap_ref: G-02-5
orchestrator_note: "With the omitted export supplied, GATE-03 is correct: exit=2, 'fixture not readable at ../../../core/domain/segment/testdata/demo.md', carrying the escalation preamble, from segmentation_test.go:244 — the escalated Fixture branch. Fixture restored byte-identical after both runs."

### 6. `make test` alone stays lenient
expected: `make test` with no escalation flag exits 0 and reports skips rather than failures.
result: pass
measured: "exit=0, lenient-run banner printed in full, 0 failures. PROCEDURE GAP: 'reports skips' is unobservable from the stated command — the test target runs `go test ./... -count=1` with no -v, and Go prints '--- SKIP' only under -v. Skips DO occur: 6 across testenv + approved when re-run with -v."
gap_ref: G-02-6

### 7. GATE-07 — the rename tripwire
expected: With the OLD flag name set and the new one unset, the run fails and names BOTH flags.
result: pass
measured: "Through a bare `go test`: exit=1, names both flags, message explains the rename and that the old name is not honored. Through `make gate`: the tripwire does NOT fire — the gate's own target-scoped export sets the new name, so there is no silent downgrade to catch. Correct by design. PROCEDURE GAP: the test says 'the run' without naming a command, and the answer differs by path."
gap_ref: G-02-7

### 8. GATE-08 — `make help` is accurate
expected: `make help` no longer claims "Full static gate"; it states the gate requires a running database and will not start one.
result: pass
measured: "'Full static gate' absent (0). Now reads 'REQUIRES a running database and will not start one'. Minor: em-dashes render as mojibake in the Windows console (2 lines)."

### 9. GATE-08 — README documents the flag
expected: README's gate section states the flag name, its presence-based semantics, and what it changes.
result: pass
measured: "Flag named 5 times. README:300-304 state 'The semantics are presence-based, in both directions' and that any non-empty value, including the string 0, enables escalation."

### 10. GATE-09 — heading-free fixture does not panic
expected: A heading-free fixture produces a normal test failure naming the fixture, and does not panic.
result: pass
measured: "TestGATE09_HeadingGuard_Control PASS with 6 subtests: empty document, prose with no hash, whitespace only, hash not at line start, fenced code block with a hash, positive case."

### 11. SEC-01 — PostgreSQL is loopback-only
expected: `docker compose ps postgres` shows `127.0.0.1:5432->5432/tcp` and no any-address mapping.
result: pass
measured: "Ports = 127.0.0.1:5432->5432/tcp; any-address mappings = 0."

### 12. CI-02 — one definition of the gate
expected: `ci.yml`'s `go` job runs `make gate` as its only run step; vet, gofmt, build and test are no longer separate inline steps.
result: pass
measured: "Exactly one run step: 'name: make gate' / 'run: make gate'. Separate inline run lines for vet/gofmt/build/test/migrate = 0. services: postgres and the job-level DSN preserved. Minor: the job's name: is still 'vet + test + fmt'."
gap_ref: G-02-12

### 13. GOV-01 mechanism — the parity check
expected: `make planning-parity PHASE=2` exits 0 and reports how many IDs it compared; with no PHASE it exits non-zero naming PHASE.
result: pass
measured: "PHASE=2 -> exit 0, 'OK: phase 2 — 10 requirement IDs compared ... and they agree'. No PHASE -> exit 2, names PHASE, prints the usage line."

### 14. DISPOSITION — the documented happy path does not work (raised by tests 1, 2, 5)
expected: `make gate` in PowerShell errors with 'unformatted' is not recognized, naming neither the gate nor the cause; and README instructs "Run make up first" but never gives the DSN or the export step (postgres:// appears nowhere in README). Orchestrator's scope call, for approval or override — (a) IN SCOPE as a GATE-08 documentation gap covering both, since GATE-08 requires the gate documented "where a developer will meet it"; (b) NEW SCOPE, backlog: pinning SHELL := /bin/sh or adding a cmd.exe guard changes Makefile semantics on every target and platform, and GOV-01's rule is that adding a requirement halts for a human.
result: [pending]

### 15. DISPOSITION — GATE-03 proven at the gate, not just at package level
expected: You directed this as an explicit decision rather than inheriting the checker's defence of the asymmetry. Confirm it stands: GATE-01, GATE-02 and GATE-03 are each proven through `make gate`, so the family has one rule.
result: [pending]

### 16. DISPOSITION — the GATE-09 negative control passed vacuously
expected: The guard IS load-bearing (defeating it fails all five heading-free subtests), but the control that claimed to prove it never ran — TMP reassigns an exported Windows env var, Go ignored the go.mod, and a module error was read as success. Recorded as an appended correction to 02-03-SUMMARY.md; the frozen plan was NOT edited. Confirm, or direct that the plan be corrected.
result: [pending]

### 17. DISPOSITION — verify-expression defects found only by running
expected: Four now — the -eq 12 count that could not hold on a correct tree; the SHA-256 false positive; 02-04 Task 2's header row counted as data (7 vs 6, could never pass); and T-02-09's plan text claiming the banner test prints no subprocess output when makefile_test.go:89,92 do. All recorded as deviations with no content bent to suit them. Confirm.
result: [pending]

### 18. DISPOSITION — FINDING-01, where STATE.md's authority sits
expected: STATE.md has many writers and no owner, so a hand-correction survives only until the next executor. Recorded with four options and NO disposition taken, because it would be a new requirement. Your call, or defer.
result: [pending]

### 19. DISPOSITION — two executor stalls, and 02-04 finished inline
expected: 02-02's first dispatch and both 02-04 dispatches were killed by the stall watchdog. 02-04 was completed inline by the orchestrator rather than by a subagent — a deviation from how every other plan in this phase ran. Confirm, or direct a re-run.
result: [pending]

### 20. DISPOSITION — the `new migrator` absence assertion
expected: The D-03 ordering is asserted by the ABSENCE of `new migrator`, a string owned by store/migrate.go and by no plan. Now guarded — each site first asserts the wrap still exists, plus a structural check on the gate recipe's ordering. Confirm sufficient, or direct a stronger pin.
result: [pending]

## Summary

total: 20
passed: 10
issues: 3
pending: 7
skipped: 0
blocked: 0

## Gaps

- gap_id: G-02-1a
  truth: "A UAT acceptance test produces the same result regardless of which terminal the reader opens"
  status: failed
  reason: "User reported: the test's procedure doesn't name a shell, so it passes or fails depending on which terminal the reader opens"
  severity: major
  test: 1
  owner: orchestrator (test-authoring defect)
  resolution: "Corrected in place — test 1 now names Git Bash."

- gap_id: G-02-1b
  truth: "A developer running `make gate` is told what failed and why"
  status: failed
  reason: "A Windows developer running make gate in PowerShell gets an error naming neither the gate nor the cause"
  severity: major
  test: 1
  evidence: "Makefile has no SHELL assignment, so GNU Make defaults to cmd.exe on Windows; the gate recipe at Makefile:74-75 uses shell substitution and test brackets. The planning-parity target added in 02-04 at Makefile:95 has the same dependency — the orchestrator extended the problem while building GOV-01's mechanism."
  disposition_proposed: "GATE-08 documentation gap (in scope) + a new requirement for the Makefile SHELL pin (backlog). Test 14."
  missing:
    - "State the POSIX-shell requirement where a developer meets the gate"
    - "DECISION NEEDED: pin SHELL, or fail loudly naming the cause under cmd.exe"

- gap_id: G-02-1c
  truth: "A developer who follows README's own instructions can run the gate"
  status: failed
  reason: "make up starts the database, make gate demands one, and nothing joins them. README says 'Run make up first' but never gives the export step, so the documented sequence fails as written — on every platform, not just Windows."
  severity: major
  test: 1
  also_reproduced_by: [2, 5]
  evidence: "grep for postgres:// in README.md returns NOTHING. EPISTEMIC_OS_DB_URL is named three times but never with a value or an export line. make up ends at 'Postgres ready'; make help never mentions the export."
  missing:
    - "Give the compose DSN and the export line in README's gate section, adjacent to 'Run make up first'"
    - "Consider having make up print the export line it just made valid"

- gap_id: G-02-5
  truth: "The GATE-03 acceptance test can distinguish GATE-03 working from GATE-03 broken"
  status: failed
  reason: "Run exactly as written, test 5 exits non-zero WITHOUT naming the fixture — it fails on GATE-01 because the procedure omits the export. Both a working and a broken GATE-03 exit non-zero."
  severity: major
  test: 5
  owner: orchestrator (test-authoring defect)
  note: "The most dangerous of the procedure gaps. Tests 1, 2 and 6 fail visibly; this one PASSES visibly while measuring the wrong thing."
  missing:
    - "State the export, and assert the fixture path is NAMED — not merely that the exit code is non-zero"

- gap_id: G-02-6
  truth: "The lenient-run test can observe the skips it claims to check"
  status: failed
  reason: "'reports skips' is unobservable from the stated command: make test runs go test with no -v, and Go prints '--- SKIP' only under -v. The skips do occur (6 under -v); the procedure cannot see them."
  severity: minor
  test: 6
  owner: orchestrator (test-authoring defect)

- gap_id: G-02-7
  truth: "The rename-tripwire test names the command it is run through"
  status: failed
  reason: "The procedure says 'the run' without naming a command, and the answer differs by path: through a bare go test the tripwire fires and names both flags; through make gate it does not fire at all. A reader running it through make gate would conclude the tripwire is broken."
  severity: minor
  test: 7
  owner: orchestrator (test-authoring defect)
  note: "The non-firing through make gate is correct design — the gate sets the new name itself, so there is no silent downgrade to catch. Recorded so it is not later mistaken for a defect."

- gap_id: G-02-12
  truth: "CI job names describe what the job does"
  status: failed
  reason: "The go job's name: is still 'vet + test + fmt' after CI-02 collapsed it onto make gate. Accurate before this phase, false now — nobody edited it, a decision falsified it."
  severity: cosmetic
  test: 12
  note: "GOV-01-shaped staleness in a file GOV-01's derivation does not cover, since ci.yml is not under .planning/. Relevant to GOV-01's coverage-bound clause."
