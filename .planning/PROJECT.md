# EpistemicOS

## What This Is

EpistemicOS is a manuscript pipeline for research papers. It ingests PDFs by URL or
upload, converts them to markdown via Mathpix, persists them in PostgreSQL with
integrity hashes, classifies paper type, and segments empirical papers into reviewable
runs with sections, exhibits, and research units. It is built as a Go hexagonal
architecture with an HTTP API and a CLI over the same core services.

This milestone is not about adding pipeline capability. It is about making the test
gate that verifies all of it mean something.

## Core Value

`make gate` must be able to distinguish "tested and passed" from "tested nothing" —
because every downstream verification claim is made through it, and a gate that passes
vacuously makes all of them unfalsifiable.

## Requirements

### Validated

<!-- Inferred from the existing codebase (.planning/codebase/, analyzed 2026-08-30). -->

- ✓ Ingest a paper from a URL or a multipart upload (50 MB cap) — existing
- ✓ Deduplicate by MD5 content hash before incurring Mathpix cost — existing
- ✓ Convert PDF to markdown via Mathpix three-phase async client — existing
- ✓ Store markdown and its SHA-256 hash atomically so offsets stay verifiable — existing
- ✓ Track paper lifecycle: pending → downloading → processing → ready \| failed — existing
- ✓ Classify paper type (empirical vs. systematic/conceptual) as a gate — existing
- ✓ Segment empirical papers into sections, exhibits, and research units — existing
- ✓ Persist segmentation runs with byte offsets verified against markdown hash — existing
- ✓ Review workflow: review, resolve, reject, return-to-author, decision freezing — existing
- ✓ Expose REST API (health, capabilities, papers, metrics) and an 18-command CLI — existing
- ✓ Apply schema migrations via golang-migrate — existing
- ✓ Operate with CORS, per-IP rate limiting, security headers, correlation IDs — existing

### Active

<!-- This milestone. Hypotheses until shipped and validated. -->

- [ ] `make gate` fails loudly and names the cause when `EPISTEMIC_OS_DB_URL` is unset (GATE-01)
- [ ] `make gate` fails loudly and names the cause when the database is unreachable (GATE-02)
- [ ] `make gate` fails loudly and names the cause when a fixture is unreadable (GATE-03)
- [ ] Content-conditional skips stay green and silent — a fixture that genuinely lacks
      a preamble is legitimate signal, not a gate failure (GATE-04)
- [ ] CI provisions PostgreSQL and applies migrations so the database-backed tests
      actually execute on every push and pull request (CI-01)
- [ ] `ci.yml` calls `make gate` rather than re-implementing it, so the gate has exactly
      one definition (CI-02)
- [ ] Automated negative tests prove the gate: each of the three environment conditions
      is deliberately broken and the gate is asserted to fail *and* to name that cause
      (PROOF-01, PROOF-02, PROOF-03 — REQUIREMENTS.md's header records that this single
      line was split into three atomic requirements under the template's atomicity rule)

### Out of Scope

- Ingest, section map, and citation specs — in flight, but they become their own
  milestones once the gate can be trusted to verify them
- An opt-out target for running the gate without a database — reintroduces exactly the
  ambiguity this milestone exists to remove
- Failing the gate on content-conditional skips — a test declining because the fixture
  does not exercise a criterion is real signal, not an untested assertion
- A drift check between `ci.yml` and `make gate` — superseded by collapsing the two to
  a single definition
- Fixing failing tests — with Postgres up the suite is healthy (46 PASS, 0 SKIP); this
  milestone is about what the gate can prove, not about test correctness

## Context

**The problem, concretely.** `make gate` is `vet` → `gofmt -l` → `go build ./...` →
`go test ./... -count=1`. Nothing in it starts PostgreSQL; `make up` is a separate
target. When no database is present the 38 database-backed tests call `t.Skip` and the
gate reports success.

**Skip sites fall into two families**, and only the first is a gate failure:

| Family | Sites |
|---|---|
| Environment — the assertion could not run | `internal/adapters/secondary/approved/papers_test.go:29,41`; `internal/adapters/secondary/store/segmentation_test.go:28,40,278` |
| Content — the fixture does not exercise the criterion | `internal/core/domain/segment/acceptance_test.go:438,451` |

**CI is green for the wrong reason.** `.github/workflows/ci.yml` has no `services:`
block and never sets `EPISTEMIC_OS_DB_URL`, so CI is passing precisely because every
database-backed test skips. Hard-failing the gate turns CI red until CI provisions a
database — which is why that work is inside this milestone rather than after it.

**The gate is defined twice.** `ci.yml` re-implements vet / gofmt / build / test as four
inline steps instead of calling `make gate`. The two agree today, but nothing enforces
it — a second definition of the gate is a second thing that can silently drift.

**Known tension for planning.** A negative test asserting "the gate fails when
`EPISTEMIC_OS_DB_URL` is unset" has to run inside the suite that the gate governs, in an
environment where that variable is set. How that is arranged is an open design question.

## Constraints

- **Tech stack**: Go 1.24, stdlib `net/http`, `pgx/v5`, `golang-migrate/v4`, `testify` —
  established; this milestone introduces no new runtime dependencies
- **Database**: PostgreSQL 16+ — the gate's meaning depends on it being genuinely present
- **CI**: GitHub Actions, `ubuntu-latest`, plus a Docker build smoke job
- **Formatting**: `gofmt` is already enforced and the tree is clean — keep it that way
- **Failure policy**: hard fail with no exception, locally and in CI; no sanctioned path
  to a green gate without a reachable database

## Key Decisions

| Decision | Rationale | Outcome | Requirements |
|----------|-----------|---------|--------------|
| Only environment skips fail the gate | A test declining because the fixture has no preamble is real signal; conflating it with "no database" would make the gate noisy and teach people to ignore it | **Done** (Phase 1, `TestFixtureIntegrity`) | GATE-04 |
| Hard fail with no exception | An opt-out target would recreate the ambiguity between "tested and passed" and "tested nothing" under a different name | **Done** (Phase 2 02-01, `a527644`) | GATE-01, GATE-02, GATE-03 |
| CI provisions Postgres in this milestone | A hard-failing gate turns CI red immediately; the change cannot land without it | **Done** (`868d45b`, preserved through Phase 2's collapse) | CI-01 |
| `ci.yml` calls `make gate` | One definition of the gate cannot drift from itself | **Done** (Phase 2 02-03, `a527644`) | CI-02 |
| Prove the gate with automated negative tests | A manual checklist decays as the code changes; the gate's own behavior should be covered by the suite | — Pending (Phase 3) | PROOF-01, PROOF-02, PROOF-03 |
| Scope limited to the gate | Ingest, section map, and citation are verified *through* the gate, so the gate has to be trustworthy first | — Pending (milestone-scope statement; closes with the milestone, not a phase) | no requirement — milestone-scope statement, not a requirement |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-30 after initialization*
