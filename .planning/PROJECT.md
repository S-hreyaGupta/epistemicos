# EpistemicOS — Trustworthy Test Gate

## What This Is

EpistemicOS is a Go research-paper ingestion and processing system: PDFs come in by URL or upload, Mathpix converts them to markdown, PostgreSQL persists them, and core services classify paper type and segment the markdown into role-tagged sections. This milestone is not about that pipeline. It is about `make gate` — the command every downstream verification claim is settled by — and making its verdict mean something.

Today the gate reports success whether the 38 database-backed tests execute or silently skip. With Postgres up all 46 pass, so the suite itself is sound. The gate simply cannot distinguish "tested and passed" from "tested nothing."

## Core Value

A passing gate must be falsifiable: green means the database-backed tests actually ran and actually passed.

## Requirements

### Validated

<!-- Inferred from the existing codebase via .planning/codebase/. These work and are relied upon. -->

- ✓ Paper ingestion by URL or multipart upload — existing
- ✓ Mathpix three-phase async PDF→markdown conversion — existing
- ✓ PostgreSQL persistence with paper status tracking — existing
- ✓ Content deduplication via MD5 hashing — existing
- ✓ Paper type classification (empirical / systematic / conceptual) — existing
- ✓ Markdown segmentation with section-role classification, persisted as runs — existing
- ✓ Multi-study gate verdict and evidence persistence — existing
- ✓ Run-level rejection — existing
- ✓ REST API: health, capabilities, papers, metrics — existing
- ✓ CLI: ingest, classify, segment, review, migrate — existing
- ✓ Static gate: `go vet` + `gofmt` + `go build` + `go test` — existing, and the subject of this milestone

### Active

- [ ] `make gate` fails when `EPISTEMIC_OS_DB_URL` is unset
- [ ] `make gate` fails when Postgres is unreachable
- [ ] `make gate` fails when a required test fixture is unreadable
- [ ] Gate failure output names which cause fired and what went untested as a result
- [ ] A separate unit-only target exists that announces loudly what it did not verify
- [ ] `.github/workflows/ci.yml` provisions Postgres and enforces the same gate

### Out of Scope

- **Coverage or count pinning** — the gate will not assert that an expected number of DB-backed tests ran. A deleted or silently-unhooked test is review's job; a manifest that must be kept current costs more than it catches.
- **Re-verification of already-shipped phases** — prior verification claims stand on other evidence. See Context for the consequence.
- **The two content-conditional skips in `internal/core/domain/segment/acceptance_test.go`** (lines 438, 451) — these skip on fixture content, not infrastructure. They are deterministic and would skip identically with Postgres up, so they are not "tested nothing."
- **Rewriting the test suite** — all 46 tests pass with a database present. The suite is not the problem.

## Context

**Current state of the gate.** `make gate` runs `go vet`, a `gofmt -l` check, `go build ./...`, and `go test ./... -count=1`. Go exits 0 when tests skip, so the DB-backed tests skipping is indistinguishable from them passing.

**CI is worse than the local case.** `.github/workflows/ci.yml` runs on a bare `ubuntu-latest` with no `services:` block and no `EPISTEMIC_OS_DB_URL`. Every push and pull request to `main` has run with all 38 database-backed tests skipping, and has been green throughout. The vacuous pass is not a latent risk — it is the steady state of branch protection.

**The gate is defined twice.** `ci.yml` does not invoke `make gate`; it re-implements the same four steps inline. The two agree today by coincidence, not construction. Changing only the Makefile would leave `main` merging on vacuous passes.

**Skip inventory** (`grep -rn "t.Skip"`):

| Site | Cause | Treatment |
|---|---|---|
| `internal/adapters/secondary/approved/papers_test.go:29` | `EPISTEMIC_OS_DB_URL` unset | must fail |
| `internal/adapters/secondary/approved/papers_test.go:41` | Postgres unreachable | must fail |
| `internal/adapters/secondary/store/segmentation_test.go:28` | `EPISTEMIC_OS_DB_URL` unset | must fail |
| `internal/adapters/secondary/store/segmentation_test.go:40` | Postgres unreachable | must fail |
| `internal/adapters/secondary/store/segmentation_test.go:278` | fixture not readable | must fail |
| `internal/core/domain/segment/acceptance_test.go:438` | fixture has no preamble | stays legal |
| `internal/core/domain/segment/acceptance_test.go:451` | preamble is whitespace only | stays legal |

**Known consequence of deferring re-verification.** Because prior phases were verified through a gate that could pass vacuously, the first trustworthy gate run may surface failures in already-shipped work. This is expected, not a defect in this milestone, and deliberately not scoped as a task here.

## Constraints

- **Tech stack**: Go 1.24, PostgreSQL 16, `make`, Docker Compose — the gate must work within these, no new toolchain
- **Compatibility**: CI runs on GitHub Actions `ubuntu-latest`; whatever the gate requires must be provisionable there
- **Duplication**: the gate exists in both `Makefile` and `ci.yml` — both must change together or they drift apart again
- **Developer ergonomics**: contributors must retain a way to run tests without Docker, but it must never be mistakable for a full verification

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Infra skips fail; content-conditional skips stay legal | The two `acceptance_test.go` skips are deterministic and would skip with the database up — they are a test declining a case the fixture lacks, not untested infrastructure | — Pending |
| Unit-only path announces itself rather than running silently | Preserves offline development without letting a quiet pass masquerade as verification | — Pending |
| Milestone covers `Makefile` and `ci.yml` together | CI does not call `make gate`; fixing only the Makefile leaves `main` merging on vacuous passes | — Pending |
| No coverage or count pinning | A manifest must be kept current to be worth anything; the deleted-test case it would catch is within review's reach | — Pending |
| No re-verification of already-shipped phases | Prior claims stand on other evidence; widening scope now would delay the gate that makes future claims checkable | — Pending |

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
