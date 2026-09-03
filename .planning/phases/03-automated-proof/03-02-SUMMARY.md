---
phase: 03-automated-proof
plan: 02
subsystem: testing
tags: [go, testing, make, subprocess-harness, differential-control, ordering-check]

# Dependency graph
requires:
  - phase: 03-automated-proof
    plan: 01
    provides: "internal/platform/gateproof spine (unreachableDSN, lineContainsBoth, requireIntact, materializeTree, stripEscalationExport) and gate.RunOptions.Dir"
provides:
  - "TestPROOF02_GateNamesUnreachableHost (intact_tree + defeated_tree_control) proving PROOF-02 and its SC-5 differential control end-to-end through a real nested make gate"
  - "D-02b's effect-side observation that testenv, not store.RunMigrations, is the first voice on the unreachable-database path, obtained free from the same nested run"
  - "TestGateOrdersPreflightBeforeMigrate, the structural half of D-02/D-03's ordering claim, checked against make -n gate's dry-run expansion rather than the Makefile's raw text"
affects: [03-03-fixture-differential, 03-GOV-SWEEP]

# Actuals (#2632)
actuals:
  tokens: 3374
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Structural ordering check against `make -n <target>`'s dry-run expansion (variables resolved, $(MAKE) recursion shown) rather than the Makefile's raw text — a claim about recipe order, not output content, so D-07's non-uniform-weakness objection does not transfer"
    - "A deliberately absent assertion is documented in place, not omitted silently — the D-15 comment at the spot a reporter-identity assertion for a dependency's own prose would otherwise go"

key-files:
  created:
    - internal/platform/gateproof/ordering_test.go
  modified:
    - internal/platform/gateproof/proof02_test.go

key-decisions:
  - "PROOF-02's control asserts nothing about golang-migrate's own reporter text ('new migrator' wrapper) in the defeated tree — that text is a dependency's prose, and PROOF-01's control asserting config's own message does not transfer to a condition where the reporter is not this project's code (D-15)"
  - "The ordering check reads make -n gate's real dry-run expansion via gate.Run (not gate.Make, since -n must precede the target), performs no nested make gate, and is a strict index comparison (preflightIndex < migrateIndex) rather than a presence check for both tokens"
  - "GATE-10 is NOT marked complete in this plan despite appearing in this plan's requirements frontmatter — its own text requires the single-message guarantee proven 'on all three escalated paths', and PROOF-03 (the third path) has not yet been proven. Marking it here would assert a claim this plan does not establish; it is left Pending until 03-03 closes the third path."

requirements-completed: [PROOF-02]

coverage:
  - id: D1
    description: "TestPROOF02_GateNamesUnreachableHost/intact_tree shells out to a real nested make gate with EPISTEMIC_OS_DB_URL set to a closed-port DSN, and the escalation preamble + the literal host 127.0.0.1:1 land on one line of Combined (GATE-10, D-17)"
    requirement: "PROOF-02"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestPROOF02_GateNamesUnreachableHost -count=1 -v (against live compose Postgres)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The same nested gate run additionally shows testenv.RequireEnv present in Combined at all — D-02b's effect check on D-03's ordering claim, obtained at zero extra cost from a run that already happened"
    requirement: "PROOF-02"
    verification:
      - kind: integration
        ref: "internal/platform/gateproof/proof02_test.go intact_tree subtest, final assertion"
        status: pass
    human_judgment: false
  - id: D3
    description: "PROOF-02's SC-5 control (defeated_tree_control) runs the same invocation against a materializeTree copy with the escalation export stripped and observes NO escalation preamble there, while the intact side (captured, not re-run) produced one; the differential does not assert the defeated side's exit code, and does not assert golang-migrate's own reporter text (D-11, D-14, D-15)"
    requirement: "PROOF-02"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run 'TestPROOF02_GateNamesUnreachableHost' -count=1 -v — 3 PASS, 0 SKIP"
        status: pass
      - kind: other
        ref: "grep -c 'gate.Make(' proof02_test.go == 1; ! grep -nE 'defeated\\.ExitCode' proof02_test.go; grep -c 'D-15' proof02_test.go >= 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "The D-16 shared-result guard has a demonstrated failing path: running defeated_tree_control alone (proof filtered out) fails naming requireIntact rather than passing vacuously"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run 'TestPROOF02_GateNamesUnreachableHost/defeated_tree_control' -count=1 — exit non-zero, names requireIntact"
        status: pass
    human_judgment: false
  - id: D5
    description: "make -n gate's dry-run expansion contains a line invoking env-preflight strictly before the first line invoking migrate, asserted structurally (index comparison) rather than against the Makefile's raw text, and the check performs no nested make gate (D-02a)"
    requirement: "GATE-10 (D-03 ordering claim)"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -run TestGateOrdersPreflightBeforeMigrate -count=1 -v — PASS in 0.12s"
        status: pass
      - kind: other
        ref: "make -n gate — env-preflight line precedes migrate line in real output"
        status: pass
    human_judgment: false
  - id: D6
    description: "The ordering check is falsifiable: transposing the two $(MAKE) lines in a materializeTree copy's Makefile and running the same index-comparison logic against that copy produces a failing comparison (migrate's index precedes env-preflight's index)"
    verification:
      - kind: other
        ref: "Scratch demonstration (deleted after capture) — see Falsifiability Demonstration section below for real captured output"
        status: pass
    human_judgment: false
  - id: D7
    description: "The proof/control ordering does not depend on test execution order, across the whole package"
    verification:
      - kind: integration
        ref: "go test ./internal/platform/gateproof/ -count=1 -shuffle=on — all PASS, 0 SKIP, 0 FAIL"
        status: pass
    human_judgment: false
  - id: D8
    description: "The full gate is still green end-to-end with both new subtests wired in, and the compose PostgreSQL service was never stopped"
    requirement: "PROOF-02, GATE-10"
    verification:
      - kind: integration
        ref: "make gate (live compose Postgres, EPISTEMIC_OS_DB_URL set) — exit 0, includes internal/platform/gateproof's own nested proof run (38.2s)"
        status: pass
      - kind: other
        ref: "docker compose ps postgres — Up (healthy) before and after every run in this plan"
        status: pass
    human_judgment: false

duration: ~50min (this continuation session; Task 1 was committed in a prior session)
completed: 2026-09-03
status: complete
---

# Phase 3 Plan 2: PROOF-02 and the Structural Ordering Check Summary

**`TestPROOF02_GateNamesUnreachableHost` proves the gate fails and names the unreachable host `127.0.0.1:1` on one line when the database is set but unreachable, with an SC-5 differential control that deliberately omits a reporter-identity assertion on golang-migrate's own prose (D-15); `TestGateOrdersPreflightBeforeMigrate` adds a cheap structural check over `make -n gate`'s dry-run expansion that carries D-03's ordering claim independently of the expensive proofs, demonstrated to fail when the two recipe lines are transposed.**

## Continuation Context

This plan's Task 1 was executed and committed (`c850f8f`) in a prior session. Tasks 2 and 3
existed as uncommitted work-in-progress on disk when this continuation began: an uncommitted
modification to `proof02_test.go` (the `defeated_tree_control` subtest, Task 2) and a complete,
untracked `ordering_test.go` (Task 3). This session's job was to independently verify that
work against the plan's `must_haves`, artifacts, key_links, and prohibitions — not accept it on
trust — then run the required falsifiability demonstration, commit, and close out the plan.

Two harness defects (`materializeTree`'s tar-drain deadlock and `gate.Run`'s unreachable
`TimedOut` branch) were fixed on `HEAD` immediately before this session began (see
`03-INCIDENT-02-harness-timeout-defects.md`). Neither fix touched `proof02_test.go` or
`ordering_test.go` — confirmed via `git log --oneline -- <both files>`, which shows no commit
between the harness fixes and this plan's own three commits.

## Verification of the Uncommitted Work

Both files were read in full and checked line-by-line against the plan's `must_haves` and
`acceptance_criteria` before anything was committed:

- **`defeated_tree_control` (Task 2):** reuses the intact-side `RunResult` from Task 1's
  `intact_tree` subtest via `requireIntact` (does not re-run the intact side — `grep -c
  'gate.Make(' proof02_test.go` == 1). Builds the defeated side with `materializeTree` +
  `stripEscalationExport`, then `gate.Run` with the same `Env`/`Unset` as the intact side.
  Asserts (1) the intact side's positive restated, (2) the defeated side's `Combined` does
  NOT contain `testenv.RequireEnv`, and does **not** assert the defeated side's exit code
  (`! grep -nE 'defeated\.ExitCode'` — confirmed empty) or golang-migrate's `new migrator`
  text as an assertion argument (confirmed: that phrase does not appear anywhere in the file,
  including the D-15 comment — the comment names the decision in prose without repeating the
  dependency's literal wrapper string). `grep -c 'D-15'` == 1, so the absent assertion is
  documented rather than invisible.
- **`ordering_test.go` (Task 3):** `gate.SkipIfNested(t)` first statement; invokes
  `gate.Run(t, []string{"make", "-n", "gate"}, gate.RunOptions{})` (not `gate.Make`, since `-n`
  must precede the target); vacuity guard on `TimedOut`/`ExitCode != 0` before any content
  assertion; splits `Combined` on newline, trims a trailing `\r`, finds the first line
  containing `env-preflight` and the first containing `migrate`, and asserts
  `preflightIndex < migrateIndex` — a strict index comparison, not a dual presence check. No
  nested `make gate` (`grep -c '"-n"'` == 1; the only `"gate"` literal is inside the `-n` argv
  itself). No Go parallel-test marker.

Both files matched the plan's intent; no defects were found that required a fix before
committing.

## Falsifiability Demonstration (Task 3, run once, not committed)

A scratch test file (`zzz_ordering_falsifiability_scratch_test.go`) was written, run once, and
deleted before finishing. It called `materializeTree(t)` to get a throwaway copy of `HEAD`,
transposed the `\t$(MAKE) env-preflight` and `\t$(MAKE) migrate` lines in that copy's
`Makefile` (the copy's line endings were CRLF, unlike the repo's LF — `git archive` applies
`.gitattributes`/`core.autocrlf` normalization on the way out; this is expected git behavior,
not a defect), then ran `make -n gate` against the copy via `gate.Run(t, ..., gate.RunOptions{
Dir: root})` and applied the identical index-comparison logic.

**Passing case (real ordering intact, from the actual `make -n gate` run against the
repository, captured earlier in this session):**

```
$ make -n gate
go vet ./...
unformatted=$(gofmt -l .); \
if [ -n "$unformatted" ]; then \
	echo "unformatted files:"; echo "$unformatted"; exit 1; \
fi
go build ./...
C:/Users/gupta/bin/make.exe env-preflight
make[1]: Entering directory 'C:/EpistemicOS/epistemicos-gsd-pilot'
go test ./internal/platform/testenv/ -count=1
make[1]: Leaving directory 'C:/EpistemicOS/epistemicos-gsd-pilot'
C:/Users/gupta/bin/make.exe migrate
...
```
`env-preflight` line index 6, `migrate` line index 10 — `6 < 10` holds, matches
`TestGateOrdersPreflightBeforeMigrate`'s real PASS.

**Failing case (transposed copy, real captured scratch-test output):**

```
=== RUN   TestZZZOrderingFalsifiabilityScratch
    zzz_ordering_falsifiability_scratch_test.go:64: SCRATCH DEMONSTRATION — transposed copy's `make -n gate` output:
        go vet ./...
        unformatted=$(gofmt -l .); \
        if [ -n "$unformatted" ]; then \
        	echo "unformatted files:"; echo "$unformatted"; exit 1; \
        fi
        go build ./...
        make migrate
        make[1]: Entering directory 'C:/Users/gupta/AppData/Local/Temp/gateproof-1864921556'
        go run ./cmd/epistemicos-cli migrate up
        make[1]: Leaving directory 'C:/Users/gupta/AppData/Local/Temp/gateproof-1864921556'
        make env-preflight
        make[1]: Entering directory 'C:/Users/gupta/AppData/Local/Temp/gateproof-1864921556'
        go test ./internal/platform/testenv/ -count=1
        make[1]: Leaving directory 'C:/Users/gupta/AppData/Local/Temp/gateproof-1864921556'
        make test
        make[1]: Entering directory 'C:/Users/gupta/AppData/Local/Temp/gateproof-1864921556'
        echo "make test is the lenient run: ..."
        go test ./... -count=1
        make[1]: Leaving directory 'C:/Users/gupta/AppData/Local/Temp/gateproof-1864921556'
    zzz_ordering_falsifiability_scratch_test.go:102: FALSIFIABILITY DEMONSTRATED: in the transposed copy, env-preflight is at line 10 ("make env-preflight\r") and migrate is at line 6 ("make migrate\r") — migrate now precedes env-preflight, exactly the ordering violation the real check exists to catch. The real check's assertion `preflightIndex < migrateIndex` would evaluate false here and fail with t.Fatalf.
--- PASS: TestZZZOrderingFalsifiabilityScratch (1.39s)
PASS
ok  	github.com/EpistemicOS/epistemicos/internal/platform/gateproof	85.206s
```

`env-preflight`'s index (10) is no longer less than `migrate`'s index (6) — the exact
transposition `TestGateOrdersPreflightBeforeMigrate`'s assertion is written to catch. The
scratch test's own outer assertion is a tautology reporting the demonstration succeeded
(PASS = falsifiability shown); the logged line states explicitly what the real check's
`preflightIndex < migrateIndex` comparison would evaluate to and that it would fail.

The scratch file has been deleted (`rm internal/platform/gateproof/zzz_ordering_falsifiability_scratch_test.go`), confirmed absent via `git status --porcelain` (clean of anything from this plan) and `go vet ./internal/platform/gateproof/` (clean, package compiles without it).

## Performance

- **Duration:** ~50 min (this continuation session)
- **Tasks:** 3 (Task 1 previously committed; Tasks 2 and 3 verified, demonstrated, and committed this session)
- **Files:** 2 (1 created, 1 modified)

## Task Commits

1. **Task 1: PROOF-02 intact_tree — gate names unreachable host** — `c850f8f` (feat, prior session)
2. **Task 2: PROOF-02's SC-5 differential control, with the assertion D-15 forbids left out** — `7e9fb82` (feat)
3. **Task 3: The structural half of D-03's ordering claim** — `81dc050` (feat)

_No TDD RED/GREEN/REFACTOR sequence: `type="auto" tdd="true"` where the deliverable IS the
test suite — each task's commit is its own verified, working slice, matching 03-01's pattern._

## Files Created/Modified

- `internal/platform/gateproof/proof02_test.go` — `TestPROOF02_GateNamesUnreachableHost` gains `defeated_tree_control` (Task 2), completing the proof/control pair started by Task 1's `intact_tree`
- `internal/platform/gateproof/ordering_test.go` — `TestGateOrdersPreflightBeforeMigrate` (Task 3), new file

## Plan-Level Verification

All items from the plan's `<verification>` section confirmed:

- `go test ./internal/platform/gateproof/ -run 'TestPROOF02_GateNamesUnreachableHost' -count=1 -v` — 2 `--- PASS` lines (parent + both subtests = 3 total counting the parent), 0 SKIP.
- `EPISTEMIC_OS_TEST_MAKE_DEPTH=1` reproduces SKIP for both `TestPROOF02_GateNamesUnreachableHost` and `TestGateOrdersPreflightBeforeMigrate`.
- `go test ./internal/platform/gateproof/ -count=1 -shuffle=on` — all tests PASS, 0 FAIL, 0 SKIP.
- `go build ./...`, `go vet ./...`, `gofmt -l .` all clean.
- `git diff --stat -- go.mod go.sum` — no output (byte-unchanged).
- `git diff --stat -- Makefile` — no output (byte-unchanged; the falsifiability demonstration's transposition happened only inside a `materializeTree` copy, never the working tree).
- **Real `make gate` run against live compose Postgres** (`EPISTEMIC_OS_DB_URL` exported to the compose DSN): **exit 0**, full run including `internal/platform/gateproof`'s own nested proof suite at depth 0 (38.2s of the 50s total), confirming the whole gate is green end-to-end with both new subtests wired into the suite they prove.
- `docker compose ps postgres` — `Up (healthy)` before, during, and after every run in this plan; the compose service was never stopped.
- `git status --porcelain` clean of anything belonging to this plan (only pre-existing, unrelated untracked files: `.gsd/`, `.planning/config.json`, `.planning/milestone.lock`).

## Deviations from Plan

None — plan executed exactly as written. The prior executor's uncommitted work matched the
plan's `must_haves`, artifacts, and prohibitions on independent review; no fix was required
before committing.

## Requirements Note

This plan's frontmatter lists `requirements: [PROOF-02, GATE-10]`. **PROOF-02 is marked
complete.** GATE-10 is intentionally left `Pending` in REQUIREMENTS.md: its own text requires
the single-message delivery guarantee to be proven "on all three escalated paths," and only two
of three (PROOF-01, PROOF-02) are proven after this plan. GATE-10 closes when 03-03 proves
PROOF-03, the third path.

## Issues Encountered

None. The prior executor's uncommitted work was sound; verification found no defects requiring
correction.

## User Setup Required

None. `EPISTEMIC_OS_DB_URL` was exported by this executor (to the documented compose DSN in
README.md) only for the plan-level `make gate` verification run in this shell session; no
change was made to any persisted environment or config file.

## Next Phase Readiness

- `internal/platform/gateproof` now proves 2 of 3 conditions (PROOF-01, PROOF-02) plus their
  SC-5 controls, and carries D-03's ordering claim on two independent legs (PROOF-02's D-02b
  in-run observation and this plan's structural `make -n gate` check).
- 03-03 (PROOF-03, the fixture-differential condition) is unblocked: no file this plan created
  or modified needs further changes, and the spine (`lineContainsBoth`, `requireIntact`,
  `materializeTree`, `stripEscalationExport`) is unchanged.
- GATE-10 remains the one requirement gating on 03-03's completion.
- No blockers. `go build ./...`, `go vet ./...`, `gofmt -l .` clean; `go.mod`/`go.sum`
  byte-unchanged; `git status --porcelain` carries no delta introduced by this plan.

---
*Phase: 03-automated-proof*
*Completed: 2026-09-03*

## Self-Check: PASSED

- Both files verified present on disk: `internal/platform/gateproof/proof02_test.go`,
  `internal/platform/gateproof/ordering_test.go`.
- All 3 commits (`c850f8f`, `7e9fb82`, `81dc050`) verified present via `git log --oneline --all`.
- Every task's acceptance criteria re-run and passing (grep/test output captured above).
- Plan-level `<verification>` re-run: `make gate` exit 0 against live compose Postgres;
  `git status --porcelain` carries no delta introduced by this plan; scratch falsifiability
  file confirmed deleted.
