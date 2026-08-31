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

- [ ] **Phase 1: Escalation Mechanism and Fixture Invariant** - One helper owns the skip/fail decision; an opt-in flag turns environment skips into named failures; the preamble property becomes a fixture invariant; nothing enforces yet
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
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Shared escalation helper: one package owns the skip-or-fail decision for all three environment conditions, and all 38 call sites across 6 test files reach it
- [ ] 01-02-PLAN.md — Fixture invariant: TestFixtureIntegrity proves demo.md has a non-whitespace preamble, and the AC-14 content skips stay untouched, green and silent
- [ ] 01-03-PLAN.md — Non-enforcement audit: escalated run reaches 0 skips against a live database, each condition names its cause, and `make gate` is measured unchanged

### Phase 2: Enforcement and a Single Gate Definition
**Goal**: `make gate` sets the escalation flag and fails on any environment skip in the database-backed packages, and `ci.yml` calls `make gate` instead of re-implementing vet / gofmt / build / test as inline steps — resolving the CI-only `migrate` step introduced at `868d45b`.
**Depends on**: Phase 1
**Requirements**: GATE-01, GATE-02, GATE-03, CI-02
**Preserves**: CI-01, already satisfied at `868d45b` — not re-delivered here, but the collapse to `make gate` must not regress it
**Success Criteria** (what must be TRUE):
  1. `make gate` with no `EPISTEMIC_OS_DB_URL` fails and the message names that variable
  2. `make gate` against an unreachable database fails and the message names the host it could not reach
  3. `make gate` with an unreadable fixture fails and the message names the fixture path
  4. The `go` job in `ci.yml` runs `make gate`; vet, gofmt, build and test are no longer separate inline steps
  5. Migrations are applied by one definition that CI and a local run share — no step exists in CI that `make gate` does not have
**Plans**: TBD

Plans:
- [ ] 02-01: TBD at planning

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
| 1. Escalation Mechanism and Fixture Invariant | 0/3 | Planned | - |
| 2. Enforcement and a Single Gate Definition | 0/TBD | Not started | - |
| 3. Automated Proof | 0/TBD | Not started | - |
