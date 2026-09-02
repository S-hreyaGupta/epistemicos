# Roadmap: EpistemicOS

## Overview

Three phases that take `make gate` from reporting ok on a suite that tested
nothing, to failing loudly and naming its cause, to proving it does so. The split
is deliberate and ordered: Phase 1 builds the mechanism but enforces nothing,
Phase 2 turns it on and collapses the gate to a single definition, Phase 3 proves
the enforcement is real. Each phase leaves the tree green on its own — reversing
the order would turn CI red for infrastructure reasons before the mechanism it is
enforcing exists.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Escalation Mechanism and Fixture Invariant** - One helper owns the skip/fail decision; an opt-in flag turns environment skips into named failures; the preamble property becomes a fixture invariant; nothing enforces yet (completed 2026-09-01)
- [ ] **Phase 2: Enforcement and a Single Gate Definition** - `make gate` turns strict and `ci.yml` calls it instead of re-implementing it
- [ ] **Phase 3: Automated Proof** - Negative tests break each condition and assert the gate fails and names that cause

## Phase Details

### Phase 1: Escalation Mechanism and Fixture Invariant

**Goal**: A single shared helper owns the decision to skip or fail for every database-backed test, an opt-in flag converts each environment skip into a failure that names its cause, and the preamble property is proven as a fixture invariant. `make gate` behavior is unchanged.
**Depends on**: Nothing (first phase)
**Requirements**: GATE-04, GATE-05
**Success Criteria** (what must be TRUE):

  1. One helper is the only place the `store` and `approved` tests decide to skip or fail — the duplicated `testPool` in `segmentation_test.go` and `papers_test.go` is gone
  2. With the escalation flag set, an unset URL, an unreachable database, and an unreadable fixture each fail with a message naming that specific cause
  3. With the flag unset, `go test ./...` skips exactly as it does today — a developer without Docker still gets a green run
  4. `TestFixtureIntegrity` asserts `demo.md` has a non-whitespace preamble, and `acceptance_test.go:438,451` stay green and silent
  5. `make gate` behaves exactly as before this phase — the tree is green with and without a database

**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Shared escalation helper: one package owns every skip-or-fail decision that was an environment skip at the phase base, and all 38 call sites across 6 test files reach it
- [x] 01-02-PLAN.md — Fixture invariant: TestFixtureIntegrity proves demo.md has a non-whitespace preamble via a pure function that is itself exercised against violating inputs, and the AC-14 content skips stay byte-identical, green and silent

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-03-PLAN.md — Non-enforcement audit: escalated run reaches 0 skips against a live database and passes every test that skipped without one, each condition names its cause with exit status asserted independently, all three unescalated branches still skip, and `make gate` is measured unchanged from the approved phase base `868d45b`

### Phase 2: Enforcement and a Single Gate Definition

**Goal**: `make gate` sets the escalation flag and fails on any environment skip in the database-backed packages, and `ci.yml` calls `make gate` instead of re-implementing vet / gofmt / build / test as inline steps — resolving the CI-only `migrate` step introduced at `868d45b`.
**Depends on**: Phase 1
**Requirements**: GATE-01, GATE-02, GATE-03, CI-02, GATE-06, GATE-07, GATE-08, GATE-09, SEC-01, GOV-01
**Requirements note**: six of these ten were added on 2026-09-01 at Phase 1 close, each from a disposition Alex gave at UAT or security sign-off. This line read only the original four until then, while REQUIREMENTS.md already carried all ten — the two disagreed, and a planner reading this line would have silently dropped six. Corrected 2026-09-01. This is the sixth instance of the GOV-01 finding and the first with real consequence.
**Preserves**: CI-01, already satisfied at `868d45b` — not re-delivered here, but the collapse to `make gate` must not regress it
**Success Criteria** (what must be TRUE):

  1. `make gate` with no `EPISTEMIC_OS_DB_URL` fails and the message names that variable
  2. `make gate` against an unreachable database fails and the message names the host it could not reach
  3. `make gate` with an unreadable fixture fails and the message names the fixture path
  4. The `go` job in `ci.yml` runs `make gate`; vet, gofmt, build and test are no longer separate inline steps
  5. Migrations are applied by one definition that CI and a local run share — no step exists in CI that `make gate` does not have
  6. When escalation causes a failure, the message names the escalation flag **and prints the value it is set to**, on all three escalated paths — so someone who set `0` intending *off* sees why the run failed (GATE-06)
  7. The escalation flag is named `EPISTEMIC_OS_TEST_REQUIRE_ENV`, not `..._REQUIRE_DB` — its scope includes the cross-package fixture prerequisite, which is a filesystem condition (GATE-07)
  8. `README.md` documents the flag and its presence-based semantics, and the `Makefile` `help` target describes `make gate` accurately — its current text, "Full static gate", becomes false once the gate requires a live database (GATE-08)
  9. A heading-free fixture produces a normal test failure and does not panic; no test indexes `headings[0]` before proving `len(headings) > 0` (GATE-09)
  10. `docker-compose.yml` binds PostgreSQL to loopback only — `"127.0.0.1:5432:5432"`, not `"5432:5432"` (SEC-01)
  11. Before this phase closes, a post-checkpoint stale-artifact sweep has revalidated ROADMAP, the adjudications, VERIFICATION and REQUIREMENTS against the phase's final requirement set, evidence, anchors and dispositions — each confirmed current or corrected on the record (GOV-01)

**Plans**: 4 wave plans + 1 post-checkpoint runbook

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — Enforcement core: rename the escalation flag to `EPISTEMIC_OS_TEST_REQUIRE_ENV`, give all three escalated paths one shared preamble naming the flag and printing its value, arm the permanent rename tripwire, and reshape `make gate` into a strict gate whose voiceless preflight reports before migrate can

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-03-PLAN.md — Collapse the CI `go` job onto `make gate`, bind the compose PostgreSQL to loopback in the file and in the running container, guard the one unguarded heading index, and document the gate and the flag in README

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 02-02-PLAN.md — The shell-out-to-make harness, built as Phase 3's harness: a bounded-recursion subprocess runner that asserts the preflight is voiceless and `make test` prints the lenient-run banner, plus the roadmap note recording the slice taken from PROOF-01/02/03's design question
- [ ] 02-04-PLAN.md — GOV-01 mechanism: a standalone phase-argument-taking parity check with a Make target, requirement-ID tags on PROJECT.md, and GOV-01's own obligations written into GOV-01's text

  **Why 02-02 and 02-04 moved out of Wave 2.** 02-03 Task 1 destroys and recreates the shared compose `postgres` container; 02-02 Task 3 and 02-04 both run `make gate` against it. No `files_modified` overlap, so the coupling was invisible to both the dependency DAG and the wave guard — it was safe only because `parallelization: false`, which is a trap for whoever flips that flag later. Declaring `depends_on: 02-03` makes the ordering enforced rather than incidental.

**Post-checkpoint** *(NOT a wave — runs after verification, UAT and security sign-off)*

- [ ] 02-GOV-SWEEP-RUNBOOK.md (logical id 02-05) — GOV-01 close sweep, code-free and last: derive the artifact list mechanically, revalidate every derived artifact with a per-artifact confirmed-current or corrected verdict, re-arm until a pass produces zero corrections, and halt rather than add a requirement

  **Why it is not Wave 3.** GOV-01 requires the sweep to run *after* UAT and security sign-off, but `/gsd-execute-phase` runs every wave to completion *before* those checkpoints happen — so as a Wave 3 plan its precondition could never be satisfied, and it would halt on every run or be quietly weakened to proceed. The second outcome is GOV-01's own failure reproduced inside GOV-01's mechanism. Removing `wave:`/`depends_on:` would not have helped: the effective wave is computed from the `depends_on` DAG and a disagreeing `wave:` is only a warning. What actually removes a file from the wave graph is its **name** — every file ending `-PLAN.md` is scheduled — hence the rename. Measured after the change: the phase's wave graph is `{1: [02-01], 2: [02-02, 02-03, 02-04]}`, with no warnings.

  **Invoke explicitly** once the checkpoints have landed:
  `/gsd-execute-plan .planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP-RUNBOOK.md`
  Its precondition verifies the checkpoints **completed** mechanically — each artifact's own frontmatter verdict (`verification: passed`, `uat: complete`, `security: verified` with `threats_open: 0`) plus git ancestry proving each was written after the final plan SUMMARY. It never asks whether they ran.

### Phase 3: Automated Proof

**Goal**: Automated negative tests deliberately break each of the three environment conditions and assert that the gate fails and names that cause, so the gate's own behavior is covered by the suite rather than by a manual checklist that decays.
**Depends on**: Phase 2
**Requirements**: PROOF-01, PROOF-02, PROOF-03
**Success Criteria** (what must be TRUE):

  1. A test proves the gate fails and names `EPISTEMIC_OS_DB_URL` when that variable is unset
  2. A test proves the gate fails and names the host when the database is unreachable
  3. A test proves the gate fails and names the path when a fixture is unreadable
  4. These tests run inside the suite the gate governs, in an environment where `EPISTEMIC_OS_DB_URL` IS set — the tension recorded at PROJECT.md lines 91-93 is solved in this phase's plan, not deferred out of it
  5. Removing or bypassing the escalation mechanism makes these three tests fail

**Plans**: TBD

Plans:

- [ ] 03-01: TBD at planning

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Escalation Mechanism and Fixture Invariant | 3/3 | Complete    | 2026-09-01 |
| 2. Enforcement and a Single Gate Definition | 2/4 | In Progress|  |
| 3. Automated Proof | 0/TBD | Not started | - |
