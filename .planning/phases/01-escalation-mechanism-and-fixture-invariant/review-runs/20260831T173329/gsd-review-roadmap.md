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

