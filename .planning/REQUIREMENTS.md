# Requirements: EpistemicOS

**Defined:** 2026-08-31
**Core Value:** `make gate` must be able to distinguish "tested and passed" from "tested nothing" — because every downstream verification claim is made through it, and a gate that passes vacuously makes all of them unfalsifiable.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

Derived from PROJECT.md ## Requirements ### Active, with one exception: GATE-05,
whose source is the agreed phase split and is documented under Traceability. The
single PROJECT.md line
"Automated negative tests prove the gate: each of the three environment conditions
is deliberately broken and the gate is asserted to fail *and* to name that cause"
is split into three atomic requirements (PROOF-01..03), one per condition, per the
atomicity rule in the requirements template. No requirement here is new scope.

### Gate Behavior

- [ ] **GATE-01**: `make gate` fails and names the cause when `EPISTEMIC_OS_DB_URL` is unset
- [ ] **GATE-02**: `make gate` fails and names the cause when the database is unreachable
- [ ] **GATE-03**: `make gate` fails and names the cause when a fixture is unreadable
- [x] **GATE-04**: Content-conditional skips stay green and silent — a fixture that genuinely lacks a preamble is legitimate signal, not a gate failure
- [x] **GATE-05**: With `EPISTEMIC_OS_TEST_REQUIRE_DB` set, a single shared test helper converts each environment skip — unset URL, unreachable database, unreadable fixture — into a failure naming that cause; with it unset, those skips remain
- [ ] **GATE-06**: When escalation causes a failure, the message names `EPISTEMIC_OS_TEST_REQUIRE_DB` **and prints its value**, on all three escalated paths. Presence-based semantics mean the string `0` enables escalation, so a reader who set `0` intending *off* must see `EPISTEMIC_OS_TEST_REQUIRE_DB="0"` in the failure itself. Measured at Phase 1 close: the unset-URL path says only "is set" and never prints the value, and the unreachable-database and unreadable-fixture paths do not name the flag at all — so neither reveals that escalation is why the run failed rather than skipped

### Continuous Integration

- [x] **CI-01**: CI provisions PostgreSQL and applies migrations so the database-backed tests actually execute on every push and pull request — **done at `868d45b`**
- [ ] **CI-02**: `ci.yml` calls `make gate` rather than re-implementing it, so the gate has exactly one definition

### Gate Proof

- [ ] **PROOF-01**: An automated test proves the gate fails and names `EPISTEMIC_OS_DB_URL` when that variable is unset
- [ ] **PROOF-02**: An automated test proves the gate fails and names the unreachable host when the database cannot be reached
- [ ] **PROOF-03**: An automated test proves the gate fails and names the fixture path when a fixture is unreadable

## v2 Requirements

None. This milestone is deliberately narrow; the next milestones are the specs
already in flight (ingest, section map, citation), which are verified *through*
this gate rather than alongside it.

## Out of Scope

Explicitly excluded. Carried forward from PROJECT.md ## Requirements ### Out of Scope.

| Feature | Reason |
|---------|--------|
| Ingest, section map, and citation specs | In flight, but they become their own milestones once the gate can be trusted to verify them |
| An opt-out target for running the gate without a database | Reintroduces exactly the ambiguity this milestone exists to remove |
| Failing the gate on content-conditional skips | A test declining because the fixture does not exercise a criterion is real signal, not an untested assertion — see GATE-04 |
| A drift check between `ci.yml` and `make gate` | Superseded by CI-02, which collapses the two to a single definition |
| Fixing failing tests | With Postgres up the suite is healthy; this milestone is about what the gate can prove, not about test correctness |

## Traceability

Which phases cover which requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-04 | Phase 1 | Complete |
| GATE-05 | Phase 1 | Complete |
| GATE-01 | Phase 2 | Pending |
| GATE-02 | Phase 2 | Pending |
| GATE-03 | Phase 2 | Pending |
| GATE-06 | Phase 2 | Pending |
| CI-01 | Delivered at `868d45b` (not planned) | Complete |
| CI-02 | Phase 2 | Pending |
| PROOF-01 | Phase 3 | Pending |
| PROOF-02 | Phase 3 | Pending |
| PROOF-03 | Phase 3 | Pending |

**Coverage:**

- v1 requirements: 10 total
- Already satisfied: 1 (CI-01)
- Mapped to phases: 9
- Unmapped: 0 ✓

**Note on CI-01:** satisfied before the roadmap existed, at commit `868d45b`,
which added a `services: postgres` block, `EPISTEMIC_OS_DB_URL`, and a `migrate`
step to `ci.yml`. Verified at the time: 38 database-backed tests pass, 0 skip,
and the full suite reports 0 skips. No phase plans it. Phase 2 must preserve this
behavior while collapsing the job to `make gate` — the inline `migrate` step
`868d45b` added is CI-only today, and removing that asymmetry is CI-02's job, not
a re-delivery of CI-01.

**Note on GATE-05's provenance.** Every other requirement here traces to a bullet
in PROJECT.md ## Requirements ### Active. GATE-05 does not, and that gap is worth
stating rather than leaving for a reader to notice.

Its source is the agreed non-enforcing/enforcing phase split: Phase 1 builds the
escalation mechanism, Phase 2 turns it on. PROJECT.md's Active bullets are all
written as claims about `make gate` ("`make gate` fails loudly and names the cause
when X"), which are enforcement claims and therefore land in Phase 2. PROJECT.md
was written before that split existed, so it has no bullet for the mechanism the
split puts in Phase 1 — even though GATE-01, GATE-02 and GATE-03 all depend on it.

Without GATE-05, Phase 1's success criteria exceed its requirement mapping: four
of its five criteria describe the helper and the flag, and only one (the fixture
invariant) maps to a requirement. That is a coverage gap in the requirements, not
a mis-titled phase.

This is not new scope — it is the mechanism the phase split already specifies —
but its traceability runs to that split, not to PROJECT.md. PROJECT.md's own
Evolution section is where it belongs: *"New requirements emerged? → Add to
Active"*, applied at the Phase 1 transition. Until then it is grounded here, in
this note, and nowhere else.

---
*Requirements defined: 2026-08-31*
*Last updated: 2026-08-31 after initial definition*
