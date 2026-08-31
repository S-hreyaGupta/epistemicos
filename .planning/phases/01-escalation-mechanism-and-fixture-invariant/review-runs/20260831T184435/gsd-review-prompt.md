# Cross-AI Plan Review Request

You are reviewing implementation plans for a software project phase.
Provide structured feedback on plan quality, completeness, and risks.

## Project Context

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

- [ ] `make gate` fails loudly and names the cause when `EPISTEMIC_OS_DB_URL` is unset
- [ ] `make gate` fails loudly and names the cause when the database is unreachable
- [ ] `make gate` fails loudly and names the cause when a fixture is unreadable
- [ ] Content-conditional skips stay green and silent — a fixture that genuinely lacks
      a preamble is legitimate signal, not a gate failure
- [ ] CI provisions PostgreSQL and applies migrations so the database-backed tests
      actually execute on every push and pull request
- [ ] `ci.yml` calls `make gate` rather than re-implementing it, so the gate has exactly
      one definition
- [ ] Automated negative tests prove the gate: each of the three environment conditions
      is deliberately broken and the gate is asserted to fail *and* to name that cause

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

## Phase 1: Escalation Mechanism and Fixture Invariant
### Roadmap Section

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
**Wave 1**

- [ ] 01-01-PLAN.md — Shared escalation helper: one package owns every skip-or-fail decision that was an environment skip at the phase base, and all 38 call sites across 6 test files reach it
- [ ] 01-02-PLAN.md — Fixture invariant: TestFixtureIntegrity proves demo.md has a non-whitespace preamble via a pure function that is itself exercised against violating inputs, and the AC-14 content skips stay byte-identical, green and silent

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 01-03-PLAN.md — Non-enforcement audit: escalated run reaches 0 skips against a live database and passes every test that skipped without one, each condition names its cause with exit status asserted independently, all three unescalated branches still skip, and `make gate` is measured unchanged from the verified phase base `030521b`


### Requirements Addressed

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
- [ ] **GATE-04**: Content-conditional skips stay green and silent — a fixture that genuinely lacks a preamble is legitimate signal, not a gate failure
- [ ] **GATE-05**: With `EPISTEMIC_OS_TEST_REQUIRE_DB` set, a single shared test helper converts each environment skip — unset URL, unreachable database, unreadable fixture — into a failure naming that cause; with it unset, those skips remain

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
| GATE-04 | Phase 1 | Pending |
| GATE-05 | Phase 1 | Pending |
| GATE-01 | Phase 2 | Pending |
| GATE-02 | Phase 2 | Pending |
| GATE-03 | Phase 2 | Pending |
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

### Plans to Review

#### gsd-review-plan-00.md

---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - internal/platform/testenv/testenv.go
  - internal/platform/testenv/testenv_test.go
  - internal/adapters/secondary/store/segmentation_test.go
  - internal/adapters/secondary/store/authorreturn_test.go
  - internal/adapters/secondary/store/researchunit_test.go
  - internal/adapters/secondary/store/runrejection_test.go
  - internal/adapters/secondary/store/segmentation_decision_test.go
  - internal/adapters/secondary/approved/papers_test.go
autonomous: true
requirements: [GATE-05]

estimate:
  tokens: 62000
  raw_tokens: 62000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB unset and EPISTEMIC_OS_DB_URL unset, `go test ./... -count=1` exits 0 and reports exactly 38 test-level skips — the count measured at the phase base"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL unset, the store and approved packages exit non-zero, and the failure text names both EPISTEMIC_OS_DB_URL and EPISTEMIC_OS_TEST_REQUIRE_DB"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL addressing a closed port, the run exits non-zero and the failure text names that host and port"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and the cross-package fixture unreadable, the run exits non-zero and the failing test names the fixture path it could not read"
    - "No test file in the store or approved packages holds its own skip-or-fail decision for the database — all 38 former call sites reach one helper"
    - "The unparseable-URL branch emits a fixed message built from zero connection-string-derived arguments, so no component of EPISTEMIC_OS_DB_URL — not the user, host, database name or query — reaches the output on that path"
    - "E3 (empty): Required() returns false for an unset flag and for an empty-string flag value; hostFromURL returns the empty string for empty input, for a malformed string and for a keyword/value DSN; and the unreachable-host branch substitutes a fixed placeholder naming EPISTEMIC_OS_DB_URL rather than emitting an empty host"
    - "E2 (adjacency): when more than one environment condition is unsatisfiable at once, exactly one cause is named, in Pool's documented order — unset URL, then unparseable URL, then unreachable host. Fixture runs only after Pool has returned, so an unreadable fixture can never mask a database condition"
    - "E4 (ordering): the skip-or-fail outcome is independent of test execution order. Pool and Fixture read the environment on every call and hold no package-level state, so `go test ./... -count=1 -shuffle=on` yields the same 38 test-level skips as the unshuffled run — measured at the phase base"
  artifacts:
    - internal/platform/testenv/testenv.go
    - internal/platform/testenv/testenv_test.go
  key_links:
    - "All 38 former call sites resolve to the shared helper — one missed file leaves a second decision site and silently defeats success criterion 1"
    - "Required() is the only reader of EPISTEMIC_OS_TEST_REQUIRE_DB; Phase 2's Makefile change and Phase 3's proof tests bind to this exact name"
    - "hostFromURL is the only source of host text in failure messages — it is what keeps the raw DSN out of CI logs"
    - "The negative control in testenv_test.go is what makes T-01-01 and T-01-02 falsifiable rather than decorative — without it, an assertion that a string is absent proves nothing about whether the assertion could ever see it"
  prohibitions:
    - "The escalation flag must not default to on. With EPISTEMIC_OS_TEST_REQUIRE_DB unset, every test that skips at the phase base must still skip and the suite must still exit 0 — a mechanism that enforces on arrival is Phase 2's change smuggled into Phase 1."
    - "This phase must not wire enforcement. No change to the Makefile and no change to the CI workflow, even though both are one line away from turning the mechanism on."
    - "No acceptance criterion in this plan may take the form of a bare pipeline from `go test` into `grep`. Such a criterion reports grep's exit status, not the test process's, and is satisfied by a build failure, a crash, an unexpected success or a zero-test run."
---

<objective>
Replace the two duplicated package-local pool helpers in the `store` and
`approved` test packages with a single shared helper that owns every skip-or-fail
decision for the database-backed tests, and give that helper an opt-in escalation
flag that converts each environment skip into a failure naming its specific cause.

Purpose: today the decision to skip lives in two near-identical copies, and
neither can be escalated without editing both. GATE-01 through GATE-03 in Phase 2
and the proof tests in Phase 3 all bind to this helper, so it has to exist and be
the only decision site before either of those phases can be written.

Output: a new `internal/platform/testenv` package, its unit test, and six test
files converted to call it.

**The escalation is built here and turned on in Phase 2.** After this plan,
`make gate` must behave exactly as it does at the phase base. Nothing in this plan
sets `EPISTEMIC_OS_TEST_REQUIRE_DB` anywhere it would be read by a default run.

## Decisions this plan makes (flagged for review)

These were the planner's discretion, not user-locked. They are surfaced because
Phase 2 and Phase 3 bind to them.

1. **Package location: `internal/platform/testenv`.** Keeps the existing
   three-way `internal/` split (adapters / core / platform) intact rather than
   adding a fourth top-level directory. Rated `costly`, not one-way — a move is a
   mechanical rename, but by Phase 2 the Makefile and CI reference it.
2. **Flag semantics: any non-empty value enables escalation.** So
   `EPISTEMIC_OS_TEST_REQUIRE_DB=0` escalates. Presence-based was chosen over
   value-parsing because a typo in the value then errs toward enforcing rather
   than toward a silently vacuous pass — which is the failure direction this
   whole milestone exists to remove. Pinned by a unit test so it is deliberate
   rather than accidental.
3. **The flag is documented in the package doc comment only.** Not in README.md,
   whose environment table is for runtime configuration. README and Makefile
   documentation land in Phase 2, when the flag actually becomes part of the gate.
4. **The flag's name is narrower than its behavior.** It also escalates the
   cross-package fixture prerequisite, which is a filesystem condition, not a
   database one. Accepted for this milestone and queued for the developer's
   disposition in 01-03 Task 3 rather than renamed here, because Phase 2 and
   Phase 3 both bind to the literal name and renaming after they are written is
   no longer local to this package.
</objective>

## Review response — cycle 1

`01-REVIEWS.md` returned 4 unresolved HIGH concerns and 14 actionable non-HIGH
findings across the plan set. Those belonging to this plan are resolved as follows.
Nothing below is merely acknowledged; each names the place in this file where the
change landed.

| Finding | Severity | Resolution in this plan |
|---|---|---|
| Pipelines mask `go test` exit status | HIGH | The tracer `<automated>` block and every acceptance criterion in Tasks 1-3 now capture output and status separately, or run under `set -o pipefail`. A frontmatter prohibition forbids the bare-pipeline form outright. See **Execution shell** below. |
| T-01-01's "verified ground truth" is false | HIGH | The false premise is deleted from **Verified ground truth** and replaced with what was actually measured on four DSN shapes. T-01-01 is restated as a control that fails at the phase base, and downgraded from `high` to `medium` with the measurement that disproves the original rating. See **Verified ground truth** and `<threat_model>`. |
| Canary criteria assert only absence | MEDIUM | Every canary criterion now asserts non-zero exit, the fixed message text present, and the leak token absent — three independent assertions, plus a unit-level negative control proving the containment assertion can see a leak at all. Task 1 acceptance criteria. |
| `git diff --name-only` with no revision range is vacuous | LOW | Anchored to the phase base commit `030521b`, which is recorded in **Verified ground truth** and asserted by Task 1's `<precondition>`. |
| "All three environment conditions are decided in one package" is imprecise | LOW | Reworded throughout to "every skip that was an environment skip at the phase base". The in-package `loadFixture` in the segment domain stays fatal by design and is explicitly out of scope. See `<success_criteria>`. |
| `EPISTEMIC_OS_TEST_REQUIRE_DB` is semantically narrower than its behavior | LOW | Recorded as decision 4 above and added to the contract decisions queued for the developer's disposition in 01-03 Task 3. Not renamed here — rationale in decision 4. |
| Phase base `fcebad1` is mis-anchored | HIGH | Re-anchored to `030521b`. Owned by 01-03, but this plan carries the guard: Task 1's `<precondition>` asserts the base is valid **before any Phase 1 code lands**, so a wrong base fails at phase start rather than at audit time. |

**Rejected, with rationale:**

| Finding | Severity | Why not adopted |
|---|---|---|
| "The central skip/fail behavior is not directly unit-tested — add a subprocess harness now" | MEDIUM | Proving that the helper skips or fails at process level *is* PROOF-01, PROOF-02 and PROOF-03, which REQUIREMENTS.md maps to Phase 3. Building it here would leave Phase 3 with nothing to deliver and would make its own success criterion 5 — "removing the escalation mechanism makes these three tests fail" — untestable, because the tests would already exist. The reviewer's underlying worry, that Plan 01 rests on manually interpreted shell output, is addressed instead: every escalated scenario in this plan and in 01-03 now asserts process exit status independently of message content, and the message-construction half is covered by a real unit test with a negative control. |
| "Prefer emitting a stable error category for `Ping` rather than appending the complete pgx error" | MEDIUM | The Ping error is measured to render as ``failed to connect to `user=u database=nodb`: 127.0.0.1:1 (127.0.0.1): dial error: …`` — it is constructed by pgx from the parsed config, never from the raw DSN, and carries the dial diagnosis Phase 3's PROOF-02 needs to assert against. Dropping it would replace real diagnosis with a category name. The disclosure it does carry (user, database name) is covered by T-01-02 at `medium`, whose mitigation — `hostFromURL` never returning userinfo — is pinned by a unit test with a negative control. |

## Execution shell

Every command in this plan is POSIX shell and MUST be run under Git Bash.
Verified present on this host: `/usr/bin/bash` (Windows path
`C:\Program Files\Git\usr\bin\bash.exe`), GNU bash 5.3.15(1)-release,
x86_64-pc-cygwin. Also verified on PATH: `env`, `grep`, `sort`, `comm`,
`sha256sum`, `mktemp`, `wc`, `git`, `docker`, and `go` (go1.24.13
windows/amd64). Verified **absent**: `jq` — no command in this phase may depend
on it. PowerShell is this workspace's interactive default and will fail on
`env -u`, on `test -z`, and on `$(...)` capture semantics; do not run these
commands there.

**Pipeline rule.** A bare `go test … 2>&1 | grep -c X` reports grep's exit
status, not the test process's, so a build failure, a panic, an unexpected
success and a zero-test run all satisfy it. Every check in this plan therefore
either runs under `set -o pipefail` or uses the capture form: assign the combined
output to a variable, capture `$?` on the next statement, and assert status and
content as separate conditions.

**Skip-counting rule.** `go test -json` emits `"Action":"skip"` for packages with
no test files as well as for skipped tests. Measured at the phase base over
`./...`: 49 skip events, of which **38 carry a `"Test"` field** and 11 are
package-level. Every skip count in this phase must filter for `"Test":"`, or use
`-v` and count lines matching `^--- SKIP`, which was independently measured at 38.

## Artifacts this phase produces

New symbols introduced by this plan. Nothing below exists at the phase base; treat
every entry as created here rather than as drift against the existing codebase.

| Kind | Name |
|---|---|
| Package | `github.com/EpistemicOS/epistemicos/internal/platform/testenv` |
| File | `internal/platform/testenv/testenv.go` |
| File | `internal/platform/testenv/testenv_test.go` |
| Exported const | `testenv.URLEnv` |
| Exported const | `testenv.RequireEnv` |
| Exported func | `testenv.Required() bool` |
| Exported func | `testenv.Pool(t *testing.T) *pgxpool.Pool` |
| Exported func | `testenv.Fixture(t *testing.T, path string) []byte` |
| Unexported func | `hostFromURL(raw string) string` |
| Unexported const | `unparseableURLMsg` — the fixed, argument-free message for the parse-failure branch |
| Environment variable | `EPISTEMIC_OS_TEST_REQUIRE_DB` (new) |

Pre-existing, not produced here: `EPISTEMIC_OS_DB_URL`, `pgxpool`, the six test
files, `make gate`, `loadFixture` in `internal/core/domain/segment`.

## Flagged assumptions — spec-less edge probe

No SPEC exists for this phase, so the deterministic edge probe ran over GATE-04
and GATE-05 and returned 4 applicable edges. Cycle 1's plan set carried all four
as unresolved. The reviewer's LOW finding — that four generic data-structure
edges add noise to every plan — is answered not by dismissing them (the
spec-less fallback protocol forbids planner-side dismissal) but by finding the
referent each one actually has in this phase and writing it as a checkable
criterion.

| # | Requirement | Category | Probe | Status |
|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (no category was assigned, so there is no probe question to answer) | **unresolved — flagged** |
| E2 | GATE-05 | adjacency | When two things are exactly equal or just touch, do they merge, collide, or separate? | **resolved — explicit** |
| E3 | GATE-05 | empty | What is the result for empty, single-element, or null input? | **resolved — explicit** |
| E4 | GATE-05 | ordering | When elements compare equal, is output order specified and stable? | **resolved — explicit** |

Accounting: **4 surfaced == 3 authored into `must_haves.truths` + 1 flagged.**

- **E2** maps to simultaneous conditions. When the URL is unset *and* the fixture
  is unreadable, or the URL is unparseable *and* the host unreachable, the
  question "do they merge or collide" has a real answer: `Pool` decides in a
  documented order and names exactly one cause, and `Fixture` runs only after
  `Pool` has returned. Authored as a truth; pinned by the ordering of the
  branches in Task 1 and by 01-03 Scenario B, where both conditions hold at once.
- **E3** maps to the empty-string flag value and to the empty host `hostFromURL`
  returns for a keyword/value DSN. Authored as a truth; pinned by unit tests in
  Task 1.
- **E4** maps to test execution order. Authored as a truth; pinned by a
  `-shuffle=on` criterion, measured at the phase base to yield the same 38.
- **E1** came back with no category at all. It stays unresolved and is carried to
  01-03 Task 3 for the developer's disposition. It is not dismissed here.

<execution_context>
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/workflows/execute-plan.md
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
</context>

## Verified ground truth

Measured in this repository at commit `030521b` before planning, by running the
commands. Do not re-derive; do not assume anything beyond these.

- **Phase base commit: `030521b1ec7c12df868445bf8d162527202d42f1`.** Verified at
  planning time: `git rev-parse --verify` succeeds,
  `git merge-base --is-ancestor 030521b HEAD` exits 0,
  `git log --format=%H 030521b..HEAD -- Makefile .github/workflows/ci.yml` prints
  nothing, and `git diff --name-only 030521b..HEAD` filtered against `^internal/`
  and `^\.planning/` prints nothing. The cycle-1 base `fcebad1` failed both of the
  last two checks, because `868d45b` landed after it and modified
  `.github/workflows/ci.yml`. Ancestry alone is not a sufficient guard, which is
  why Task 1 carries a `<precondition>` asserting all four properties.
- `go test ./... -count=1` at the phase base exits 0 with **38 test-level skips**
  and no database present. `-shuffle=on` yields the same 38. Call sites per file:
  `authorreturn_test.go` 9, `runrejection_test.go` 7, `researchunit_test.go` 6,
  `segmentation_decision_test.go` 6, `segmentation_test.go` 5, `papers_test.go` 5
  — 38 total, re-measured at `030521b`.
- `pgxpool.New` is lazy. With `postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable`
  it returns a nil error; the failure surfaces at `Ping`.
- The `Ping` error names the host and omits the password, and is constructed by
  pgx from the parsed config rather than from the raw DSN. Observed on both DSN
  forms: ``failed to connect to `user=u database=nodb`: 127.0.0.1:1 (127.0.0.1):
  dial error: …``. It does disclose the user and database name.
- **Correction to cycle 1 — pgx v5.7.2 redacts the password in its parse error.**
  Cycle 1 recorded that the parse error "echoes the connection string verbatim…
  so a malformed DSN carrying a password would publish it". That is false for the
  pinned version. Measured on four shapes, all with a distinctive token in the
  password position, all against the **unmodified** helper: URL form renders
  `u:xxxxxx`; keyword/value form renders `password=xxxxx`; a `?password=` query
  parameter renders `password=xxxxx`; a `?sslpassword=` query parameter renders
  `sslpassword=xxxxx`. The token count in the output was `0` every time. Any
  acceptance criterion asserting "the password does not appear" therefore passes
  with zero code written and proves nothing.
- **What pgx does echo verbatim is everything else in the DSN.** Measured with a
  distinctive token in the *database-name* position: the parse error printed
  ``cannot parse `postgres://u:xxxxxx@ bad host/<token>``` and
  ``cannot parse `host=x port=notanumber password=xxxxx dbname=<token>``` — token
  count `1` in both cases, at the phase base, unmodified. That is the falsifiable
  control this plan uses: a criterion that **fails today** and can only pass once
  the branch stops interpolating the DSN and the pgx error. See T-01-01.
- The existing helper classifies a parse error as fatal (`t.Fatalf`) and an
  unreachable host as a skip (`t.Skipf`). With the flag unset and a closed-port
  DSN, `TestSaveRun_FixtureRoundTripsAllOffsets` reports `--- SKIP` and the
  package exits 0 — verified. That branch must survive unchanged.
- A non-test Go package that imports `testing` builds, vets and formats clean, and
  `t.Skip` called from it correctly skips the calling test. Verified with a probe
  module on Go 1.24.
- `go.mod` requires `golang-migrate/v4`, `google/uuid`, `pgx/v5 v5.7.2`,
  `godotenv`, `goldmark`. **There is no testify dependency**, contrary to
  PROJECT.md's Constraints line. Use stdlib `testing` only; adding a dependency is
  out of scope for this plan.
- Local DSN for the compose service:
  `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`

<tasks>

<task type="tracer">
  <name>Task 1: End-to-end escalation for the database path — store package only</name>
  <files>internal/platform/testenv/testenv.go, internal/platform/testenv/testenv_test.go, internal/adapters/secondary/store/segmentation_test.go</files>

  <precondition>
The phase base commit `030521b1ec7c12df868445bf8d162527202d42f1` is valid as an
audit anchor. Assert all four before writing any code, and halt if any fails:
`git rev-parse --verify 030521b1ec7c12df868445bf8d162527202d42f1` succeeds;
`git merge-base --is-ancestor 030521b1ec7c12df868445bf8d162527202d42f1 HEAD` exits 0;
`git log --format=%H 030521b1ec7c12df868445bf8d162527202d42f1..HEAD -- Makefile .github/workflows/ci.yml`
prints nothing; and `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1..HEAD`
piped through `grep -v '^internal/' | grep -v '^\.planning/'` prints nothing.
Ancestry alone is not sufficient — the cycle-1 base satisfied ancestry while
failing the last two, which is exactly the failure this precondition exists to
catch, and it must be caught here, before any Phase 1 code makes the tree
indistinguishable from a genuine violation. If any assertion fails, halt and
report; the correct anchor is the tip of the branch at the moment this phase
starts, and the manifest must be re-frozen with it rather than the plan patched
around it.
  </precondition>

  <read_first>
    - internal/adapters/secondary/store/segmentation_test.go (lines 1-46 — the helper being replaced, its doc comment, and the import block)
    - internal/adapters/secondary/approved/papers_test.go (lines 1-46 — the second copy; its message wording differs and both are being unified)
    - internal/platform/security (any file — for the house style of a platform package: doc comments that explain why, not what)
    - go.mod (confirm pgx/v5 is a direct requirement at v5.7.2 and no assertion library exists)
  </read_first>

  <reversibility rating="costly">
    Phase 2's Makefile change and Phase 3's proof tests bind to the package path,
    the exported function names, and the literal `EPISTEMIC_OS_TEST_REQUIRE_DB`.
    Renaming any of them later means touching the Makefile, the CI workflow and
    every call site — mechanical, but no longer local to one package.
  </reversibility>

  <action>
Create package `testenv` at `internal/platform/testenv/testenv.go`, import path
`github.com/EpistemicOS/epistemicos/internal/platform/testenv`.

Give the package a doc comment that states the contract a reader needs: this is
the one place the database-backed tests decide to skip or fail; setting
`EPISTEMIC_OS_TEST_REQUIRE_DB` to any non-empty value turns each environment skip
into a failure that names its cause; leaving it unset preserves the skip so a
developer without Docker still gets a green run. Say explicitly that any non-empty
value enables it, including the string zero, and why: a typo in the value then
errs toward enforcing rather than toward a vacuous pass. Say also that the flag's
name is narrower than its reach — it escalates the cross-package fixture
prerequisite too, which is a filesystem condition, not a database one — and that
this asymmetry is deliberate for this milestone and queued for review.

Declare `URLEnv` as the string `EPISTEMIC_OS_DB_URL` and `RequireEnv` as the
string `EPISTEMIC_OS_TEST_REQUIRE_DB`.

Add `Required() bool`, returning true when the value of `RequireEnv` is non-empty.

Add unexported `hostFromURL(raw string) string`. Parse with `net/url.Parse` and
return the `Host` field. Return the empty string on a parse error, and also for a
keyword/value DSN such as one beginning `host=`, which parses without producing a
host. This function is the only thing permitted to derive display text from the
connection string, and it must never return anything drawn from the userinfo
component.

Declare an unexported constant `unparseableURLMsg` holding the entire message the
parse-failure branch emits. It takes **no arguments and no format verbs**: it
names `EPISTEMIC_OS_DB_URL`, states that the variable is set but its value is not
a usable PostgreSQL connection string, and states that the value and the
underlying library error are deliberately withheld because both carry the
connection string. Making it an argument-free constant, rather than a format
string that happens not to be given the DSN today, is the point: a later edit that
wants to add detail has to change the constant's type, which is visible in review,
instead of adding one more verb to an existing `Fatalf`.

Add `Pool(t *testing.T) *pgxpool.Pool`, calling `t.Helper()` first, then deciding
in this documented order — the order matters and belongs in a comment, because it
is what makes the answer well-defined when more than one condition is
unsatisfiable at once:

1. Read `URLEnv`. When it is empty and `Required()` is true, `t.Fatalf` with a
   message naming both `EPISTEMIC_OS_DB_URL` and `EPISTEMIC_OS_TEST_REQUIRE_DB`
   and stating that escalation is on so the test cannot be skipped. When it is
   empty and `Required()` is false, `t.Skip` with a message naming
   `EPISTEMIC_OS_DB_URL` and telling the developer to start postgres and export
   it — preserving the phase-base behavior.
2. Build a context with a five second timeout, matching the existing helpers, and
   call `pgxpool.New`. On error, emit `unparseableURLMsg` through `t.Fatal` in
   both modes — matching the phase-base classification, where a malformed URL
   already fails rather than skips. Pass the constant and nothing else: not the
   variable's value, not the returned error, not a wrapped form of either. Record
   the measured reason in a comment on this branch: the library redacts only the
   password and echoes the rest of the connection string — user, host, database
   name and query — into that error, so forwarding it publishes the whole DSN
   minus one field to the CI log.
3. Call `Ping`. On error, close the pool, then take `hostFromURL` of the URL and
   substitute a fixed placeholder naming the variable when it comes back empty.
   When `Required()` is true, `t.Fatalf` naming that host and appending the Ping
   error. Otherwise `t.Skipf` with the same text. The Ping error is measured to be
   built by the library from the parsed config rather than from the raw DSN, and
   is kept because Phase 3's proof for the unreachable-host condition asserts
   against it; the connection string itself still is not interpolated.
4. Register `t.Cleanup` to close the pool and return it.

Note in a comment that the two packages' skip messages differ at the phase base,
so unifying them is unavoidable when the duplication is removed; what is preserved
is the skip-or-fail classification of every site, not the message bytes.

Then wire one path end to end. In `segmentation_test.go`, keep the existing local
helper's name and signature — it takes a `*testing.T` and returns a
`*pgxpool.Pool` — but replace its body with a call to the new shared helper, and
delete the doc comment above it that describes the skip policy, since that policy
now lives in one place. Add the import. Remove any import the file no longer uses;
let `go build ./...` name them. This routes all 33 store call sites through the
shared helper in one move, which is the thinnest slice that proves the mechanism
against real tests. Task 2 removes the local wrapper entirely.

Write `internal/platform/testenv/testenv_test.go` in package `testenv`. Cover the
pure pieces, and cover them with negative controls where the assertion is that
something is *absent* — an absence assertion that has never been shown to detect a
presence is not evidence.

For `hostFromURL`: a full DSN with userinfo, port and query returns host and port;
a DSN pointing at a closed port returns that host and port; a keyword/value DSN
returns empty; the empty string returns empty; a malformed string returns empty.
Then the credential case, written as a two-step control using the token named in
this task's acceptance criteria as the secret: first assert that the token really
is present in the raw input DSN, failing with a message saying the negative
control itself is broken if it is not; then assert the token is absent from what
`hostFromURL` returned. The first step is what proves the second step could fail.

For `unparseableURLMsg`, the same shape against the database-name leak token named
in the acceptance criteria: assert the token is present in the naive rendering a
careless implementation would produce — the DSN interpolated into a message —
failing with an explicit "negative control broken" message if it is not; then
assert the constant contains neither that token nor any part of the DSN; then
assert the constant does contain `EPISTEMIC_OS_DB_URL`, since a message that leaks
nothing and says nothing is not an improvement.

For `Required`, drive the variable with `t.Setenv`: unset is false, empty is
false, the string one is true, and the string zero is true — the last case pins
the presence-based rule deliberately.

Do not test `Pool`'s skip-or-fail decision here. Asserting that a helper skips or
fails requires driving a `testing.T` from outside, which is the gate proof, and
that is PROOF-01 through PROOF-03 in Phase 3. Building it here would leave that
phase with nothing to deliver and make its own success criterion — that removing
the mechanism makes those tests fail — untestable.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; go test ./internal/platform/testenv/... -count=1 &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 || exit 1; out=$(env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 2>&amp;1); st=$?; test "$st" -ne 0 &amp;&amp; printf '%s' "$out" | grep -q EPISTEMIC_OS_DB_URL &amp;&amp; printf '%s' "$out" | grep -q EPISTEMIC_OS_TEST_REQUIRE_DB &amp;&amp; echo TRACER_OK</automated>
  </verify>

  <acceptance_criteria>
    - Precondition satisfied: all four phase-base assertions above pass before any file is written.
    - `go build ./...` and `go vet ./...` succeed, and `gofmt -l .` prints nothing.
    - `go test ./internal/platform/testenv/... -count=1` exits 0 and the package no longer reports `[no test files]`.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` exits 0.
    - Under `set -o pipefail`, `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `38`, matching the phase-base baseline. Without `pipefail` this check is void.
    - The same run with `-shuffle=on` also yields `38` — the outcome does not depend on execution order (edge E4).
    - **Escalated, URL unset.** Capture once: assign the combined output of `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 2>&1` to a variable and capture `$?` on the following statement. Then assert three conditions independently: the status is non-zero; the output contains `EPISTEMIC_OS_DB_URL`; the output contains `EPISTEMIC_OS_TEST_REQUIRE_DB`. A single pipeline into `grep -c` does not satisfy this criterion.
    - **Escalated, unreachable host.** Capture once, with `EPISTEMIC_OS_TEST_REQUIRE_DB=1` and `EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable'`, running the store package. Assert independently: status non-zero; output contains `127.0.0.1:1`.
    - **Non-escalated, unreachable host — the preserved skip.** Same DSN with the flag removed via `env -u EPISTEMIC_OS_TEST_REQUIRE_DB`, running `-run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 -v`. Assert independently: status is `0`; output contains a line matching `^--- SKIP: TestSaveRun_FixtureRoundTripsAllOffsets`. This is the branch measured at the phase base and it must survive; ROADMAP success criterion 3 is otherwise only half-verified.
    - **T-01-01 falsifiable leak control.** With `EPISTEMIC_OS_TEST_REQUIRE_DB=1` and `EPISTEMIC_OS_DB_URL='postgres://u:pw@ bad host/DSNLEAKCANARY'`, capture the store package run once. Assert four conditions independently: status non-zero; output contains `EPISTEMIC_OS_DB_URL`; `printf '%s' "$out" | grep -c DSNLEAKCANARY` prints `0`; `printf '%s' "$out" | grep -c 'cannot parse'` prints `0`. **This criterion fails at the phase base** — both counts are `1` there, measured — so it can only pass once the branch stops forwarding the library error. That is what makes it a control rather than a decoration.
    - **T-01-01, keyword/value form.** Repeat with `EPISTEMIC_OS_DB_URL='host=x port=notanumber password=pw dbname=DSNLEAKCANARY'` and assert the same four conditions. Measured at the phase base: both counts are `1`.
    - **Negative controls are present and wired.** `go test ./internal/platform/testenv/... -count=1 -run 'Control' -v` runs at least two tests, and both pass. Their bodies assert the leak token is present in the raw or naive form before asserting it is absent from the sanitised form.
    - `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1 -- | grep -v '^internal/' | grep -v '^\.planning/'` prints nothing — the diff is anchored to the phase base, not to an empty range.
  </acceptance_criteria>

  <done>
The shared helper exists, its pure parts are unit-tested with negative controls
that prove the absence assertions can detect a presence, and the store package
reaches it through one delegate. Escalation off reproduces the phase-base baseline
exactly at 38 skips, shuffled or not, and still skips for an unreachable host.
Escalation on converts the unset-URL and unreachable-host conditions into failures
that name their cause, and the parse-failure branch no longer puts any part of the
connection string into the output — a claim that was false at the phase base and is
true now.
  </done>
</task>

<task type="auto">
  <name>Task 2: Delete both duplicated helpers and route all 38 call sites directly</name>
  <files>internal/adapters/secondary/store/segmentation_test.go, internal/adapters/secondary/store/authorreturn_test.go, internal/adapters/secondary/store/researchunit_test.go, internal/adapters/secondary/store/runrejection_test.go, internal/adapters/secondary/store/segmentation_decision_test.go, internal/adapters/secondary/approved/papers_test.go</files>

  <read_first>
    - internal/adapters/secondary/store/segmentation_test.go (the delegate left by Task 1, and the import block)
    - internal/adapters/secondary/approved/papers_test.go (lines 1-46 — the second duplicate and its import block, which also carries crypto/sha256, encoding/hex, errors and strings used elsewhere in the file)
    - internal/adapters/secondary/store/authorreturn_test.go (import block and one call site, to see the local conventions)
    - internal/platform/testenv/testenv.go (the helper's exported signatures)
  </read_first>

  <reversibility rating="reversible">
    A mechanical call-site rewrite across six test files, restorable by reverting
    one commit. No production code and no external contract changes.
  </reversibility>

  <action>
Remove the package-local pool helper from both packages so exactly one
skip-or-fail decision remains in the repository.

In `segmentation_test.go`, delete the delegate Task 1 left in place. In
`papers_test.go`, delete the second copy — the definition at lines 24-46 as of the
phase base together with its doc comment at lines 19-23, which describes a policy
that now lives in the shared package.

In all six files, replace every call of the deleted local helper with a call to
the shared package's pool function, passing the same `t`. The expected counts,
re-measured at the phase base, are 9 in `authorreturn_test.go`, 7 in
`runrejection_test.go`, 6 in `researchunit_test.go`, 6 in
`segmentation_decision_test.go`, 5 in `segmentation_test.go` and 5 in
`papers_test.go` — 38 in total. Confirm each file's count after editing rather
than trusting a single pass.

Add the import of `github.com/EpistemicOS/epistemicos/internal/platform/testenv`
to each of the six files, in the project-local import group that already holds the
other `github.com/EpistemicOS/epistemicos` paths.

Delete imports that the edits make unused. Measured at the phase base, the `os`
package is referenced only at line 26 of `segmentation_test.go` and line 27 of
`papers_test.go` — both inside the deleted definitions — plus one file read at
line 276 of `segmentation_test.go` that Task 3 removes. So `os` becomes unused in
`papers_test.go` in this task and in `segmentation_test.go` only after Task 3.
`time` becomes unused in both. Whether `context` and `pgxpool` survive depends on
the rest of each file, so do not guess: run `go build ./...`, let the compiler name
each unused import, and remove exactly those.

Do not leave a wrapper of any kind behind in either package, and do not add one
elsewhere. Success criterion 1 is that these two definitions are gone, not that
they delegate.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 &amp;&amp; test "$(grep -rno 'testenv.Pool(t)' --include=*_test.go internal | wc -l)" = "38" &amp;&amp; echo DEDUP_OK</automated>
  </verify>

  <acceptance_criteria>
    - `grep -v '^\s*//' internal/adapters/secondary/store/segmentation_test.go | grep -c 'testPool'` prints `0`.
    - `grep -v '^\s*//' internal/adapters/secondary/approved/papers_test.go | grep -c 'testPool'` prints `0`.
    - `grep -rno 'testenv.Pool(t)' --include=*_test.go internal | wc -l` prints `38`.
    - `grep -rl 'testenv.Pool(t)' --include=*_test.go internal | wc -l` prints `6` — every one of the six files was converted.
    - `go build ./...` and `go vet ./...` succeed, and `gofmt -l .` prints nothing.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` exits 0, and under `set -o pipefail` the `-v` output still yields `38` lines matching `^--- SKIP`.
    - **Escalated, approved package.** Capture once: the combined output of `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/approved/... -count=1 2>&1`, with `$?` captured on the following statement. Assert independently: status non-zero; output contains `EPISTEMIC_OS_DB_URL`. A bare pipeline into `grep -c` does not satisfy this criterion — that form would also be satisfied by a build failure in a package that no longer compiles, which is precisely the risk of a six-file mechanical rewrite.
    - `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1 -- | grep -v '^internal/' | grep -v '^\.planning/'` prints nothing.
  </acceptance_criteria>

  <done>
Neither package defines a pool helper. All 38 call sites name the shared package
directly, the suite is unchanged with escalation off, and the approved package
escalates identically to the store package — proven by a status assertion, not by
a grep count that a build failure would also satisfy.
  </done>
</task>

<task type="auto">
  <name>Task 3: Route the cross-package fixture read through the same helper</name>
  <files>internal/platform/testenv/testenv.go, internal/platform/testenv/testenv_test.go, internal/adapters/secondary/store/segmentation_test.go</files>

  <read_first>
    - internal/adapters/secondary/store/segmentation_test.go (lines 265-300 — the fixture read and the skip it currently performs)
    - internal/core/domain/segment/fixture_test.go (lines 81-102 — loadFixture, the established idiom: a read failure is fatal and the message names the file)
    - internal/platform/testenv/testenv.go (the helper written in Task 1, for message style and the Required branch shape)
  </read_first>

  <reversibility rating="reversible">
    One new function and one call site.
  </reversibility>

  <action>
Add `Fixture(t *testing.T, path string) []byte` to the shared package, so the third
environment condition GATE-05 names — an unreadable fixture — is decided in the same
place as the other two.

Call `t.Helper()`, then read the file. On a read error, take the escalation branch:
when `Required()` is true, `t.Fatalf` with a message naming the path that could not
be read and the underlying error; otherwise `t.Skipf` with the same text, preserving
the phase-base behavior. On success return the bytes. Give it a doc comment saying
this is for fixtures read across package boundaries, where a relative path is a real
environment risk, and pointing at the in-package `loadFixture` in the segment domain
as the stricter idiom for a fixture the package owns.

State in that doc comment that this function is reached only after the pool helper
has returned, so a fixture condition can never mask a database condition — the
ordering answer edge E2 asks for, recorded where a reader will find it.

In `segmentation_test.go`, replace the direct read of
`../../../core/domain/segment/testdata/demo.md` inside
`TestSaveRun_FixtureRoundTripsAllOffsets` — the read at line 276 and the skip at
line 278 as of the phase base — with a single call to the new function, keeping the
same relative path. Remove the `os` import if nothing else in the file uses it.

Add unit coverage for the non-escalated success path only: reading a file that
exists returns its exact bytes. As in Task 1, do not attempt to assert the skip or
fail branches from inside a test — that is Phase 3's job under PROOF-03.

Do not change the in-package `loadFixture` in the segment domain. It already hard
fails on a read error, which is the correct behavior for a fixture its own package
owns and pins, and it is deliberately outside this phase's "every environment skip"
scope: it was never a skip.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; go test ./internal/platform/testenv/... -count=1 &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 &amp;&amp; test "$(env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&amp;1 | grep -c '^--- SKIP')" = "38" &amp;&amp; echo FIXTURE_ROUTE_OK</automated>
  </verify>

  <acceptance_criteria>
    - `grep -c 'testenv.Fixture(t' internal/adapters/secondary/store/segmentation_test.go` prints `1`.
    - `grep -v '^\s*//' internal/adapters/secondary/store/segmentation_test.go | grep -c 'os.ReadFile'` prints `0`.
    - `go build ./...` and `go vet ./...` succeed, and `gofmt -l .` prints nothing.
    - `go test ./internal/platform/testenv/... -count=1` exits 0. Assert the status directly; do not infer it from a `grep -c '^--- FAIL'` of `0`, which a build failure also produces.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` exits 0, and under `set -o pipefail` the `-v` run yields `38` lines matching `^--- SKIP`.
    - The whole-suite `-json` run, filtered to skip events that carry a `"Test"` field, also yields `38` — the two counting methods agree, and the 11 package-level skip events are not miscounted as test skips.
    - `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1 -- | grep -v '^internal/' | grep -v '^\.planning/'` prints nothing.
  </acceptance_criteria>

  <done>
Every skip that was an environment skip at the phase base — unset URL, unreachable
database, unreadable cross-package fixture — is decided in one package, and the
store package's cross-package fixture read goes through it. The segment domain's
in-package `loadFixture` is untouched and remains fatal by design.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| test process → PostgreSQL | The DSN, including its password, crosses here and is held in process memory and in an environment variable |
| test process → CI log | Anything the helper writes to a failure or skip message becomes a build-log artifact; this repository's workflow logs are readable by anyone who can read the repository |
| test process → filesystem | A relative fixture path is resolved and read across a package boundary |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01-01 | Information Disclosure | `testenv.Pool`, the `pgxpool.New` parse-error branch | medium | mitigate | **Restated after cycle-1 review; severity corrected from `high` down.** The original rating rested on the claim that the library echoes the connection string verbatim including its password. Measured against pgx v5.7.2 on four DSN shapes, that is false: the password is redacted on every one, so the original canary passed at the phase base with zero code written and could not fail. What the library does echo verbatim is the rest of the DSN — scheme, user, host, database name and query parameters — and it reaches `t.Fatalf` unfiltered today. Impact is therefore DSN-metadata disclosure at the pinned version, not credential disclosure, which is `medium`. The residual credential risk is a version bump silently dropping the redaction, which the same mitigation covers. Mitigation: the branch emits `unparseableURLMsg`, an argument-free constant, so no DSN-derived value can reach it without a type change. Falsifiable by the DSNLEAKCANARY criteria in Task 1, which are **measured to fail at the phase base** (token count 1, `cannot parse` count 1) and can only pass once the branch is rewritten, and by a unit-level negative control that first proves the containment assertion detects the token in a naive rendering. Below `security_block_on: high`, so no longer phase-blocking — recorded as a correction in the manifest rather than carried forward on a false premise. |
| T-01-02 | Information Disclosure | `testenv.Pool`, the `Ping` error branch | medium | mitigate | Host text is derived only through `hostFromURL`, which returns `net/url`'s Host and therefore never the userinfo component. The `Ping` error is measured to be constructed by the library from the parsed config, rendering as `user=… database=…` with no password, and is retained because PROOF-02 asserts against it. It does disclose the user and database name; accepted at `medium` for a test-only helper against a loopback compose service. Pinned by a `hostFromURL` unit test with a negative control that first asserts the secret is present in the raw DSN, so the absence assertion is proven able to detect a leak. |
| T-01-03 | Tampering | `EPISTEMIC_OS_TEST_REQUIRE_DB` | low | accept | Anyone able to set environment variables in the test process already controls the build. The flag can only weaken behavior toward the phase-base skip, never toward a false pass that would otherwise fail. Out of scope at ASVS L1. |
| T-01-04 | Denial of Service | the five second connect timeout in `testenv.Pool` | low | accept | Carried forward unchanged from both existing helpers. A hung database bounds each call at five seconds rather than hanging the suite. |
| T-01-05 | Tampering | the `path` parameter of `testenv.Fixture` | low | accept | Every argument is a compile-time string literal in a test file. No external or user-controlled input reaches this parameter, so path traversal has no source. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan adds no dependency. `go.mod` is unchanged; `testing`, `os`, `net/url`, `strings`, `context` and `time` are stdlib and `pgx/v5 v5.7.2` is already a direct requirement. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
Run from the repository root under Git Bash, with no database present. Every check
here is database-free by design; the database-dependent half of the phase is
verified in plan 01-03.

1. `go build ./... && go vet ./... && gofmt -l .` — builds, vets, prints no files.
2. `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` — exits 0.
3. The same command with `-v` under `set -o pipefail`, counting `^--- SKIP`, prints 38. The same with `-shuffle=on` prints 38.
4. `grep -rno 'testenv.Pool(t)' --include=*_test.go internal | wc -l` prints 38, across 6 files.
5. Escalated with no URL: the store and approved packages exit non-zero, and their captured output names `EPISTEMIC_OS_DB_URL` — status and content asserted separately.
6. Escalated with a closed port: exits non-zero, and the captured output names the host and port.
7. Non-escalated with a closed port: exits 0, and the fixture round-trip test reports SKIP — the preserved branch.
8. Parse-failure leak control: with a distinctive token in the database-name position, the run exits non-zero, the token count in the output is 0, and the library's parse-error text is absent. Both counts are 1 at the phase base, so this check has teeth.
9. Unit-level negative controls pass, having first proved they can detect the token they later assert absent.
10. `git diff --name-only 030521b -- ` lists nothing outside `internal/` and `.planning/` — the Makefile and the CI workflow are untouched.
</verification>

<success_criteria>
- One package owns every skip-or-fail decision that was an environment skip at the phase base, and neither test package defines its own. The segment domain's in-package `loadFixture` is explicitly out of scope: it was fatal at the phase base, not a skip, and stays fatal.
- All 38 former call sites reach it; the six-file conversion is complete.
- With the escalation flag unset, the suite reproduces the phase base: exit 0, 38 test-level skips, shuffled or not, including the unreachable-host case which still skips.
- With the flag set, each of the three conditions produces a failure naming that specific cause, with process exit status asserted independently of message content.
- The parse-failure branch emits no component of the connection string — a claim that is false at the phase base and true after this plan, so the criterion proving it can actually fail.
- Nothing outside `internal/` changed relative to the phase base — the mechanism exists and enforces nothing.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md` when done.

Record in it: the final exported signatures; the exact skip count observed with
escalation off, plain and shuffled; the observed failure text for each of the three
escalated conditions; the observed exit status for each scenario, stated separately
from the message content; the phase base commit used and the result of its
four-part precondition; the measured leak-token counts before and after the change,
so the control's teeth are recorded rather than asserted; and confirmation that the
diff from the phase base listed nothing outside `internal/`. Phase 2 will read those
signatures and Phase 3 will assert against that failure text.
</output>

#### gsd-review-plan-01.md

---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - internal/core/domain/segment/fixture_test.go
autonomous: true
requirements: [GATE-04]

estimate:
  tokens: 30000
  raw_tokens: 30000
  tasks: 2
  confidence: low

must_haves:
  truths:
    - "TestFixtureIntegrity fails, naming testdata/demo.md, if the pinned fixture ever stops beginning with pre-heading content"
    - "TestFixtureIntegrity fails, naming testdata/demo.md, if that pre-heading content is ever whitespace only"
    - "TestFixtureIntegrity fails, naming testdata/demo.md, if the pinned fixture contains no headings at all — asserted without depending on TestDetectHeadings_Fixture having run first, since Go guarantees no ordering between tests"
    - "The invariant is decided by one pure function that is itself exercised against synthetic inputs which violate it, so the assertion is proven able to fail without any file in the working tree being mutated"
    - "TestAC14_PreHeadingContentHasNoNode reports PASS, not SKIP, for the pinned fixture — its two content-conditional skips remain in the file, unmodified, and remain unreachable for these bytes"
    - "`go test ./internal/core/domain/segment/... -count=1` exits 0 with no database present, exactly as at the phase base"
  artifacts:
    - internal/core/domain/segment/fixture_test.go
  key_links:
    - "The preamble assertion lives in the same test that already pins demo.md by SHA-256 and byte length, so the property is decidable from bytes that cannot change without that test failing first"
    - "acceptance_test.go lines 438 and 451 stay untouched — the invariant makes them unreachable rather than making them illegal, which is what keeps a genuinely preamble-free fixture legitimate signal instead of a gate failure"
    - "The pure invariant function is the seam that makes the negative proof possible without mutating tracked source; if the integrity test reimplements the check inline instead of calling it, the negative proof tests a copy and proves nothing about the real assertion"
  prohibitions:
    - "The two content-conditional skips in the segment acceptance test must not be deleted, converted into failures, or made conditional on the escalation flag. They are unreachable for the pinned fixture, not wrong — a fixture that genuinely lacks a preamble is real signal, and turning that into a gate failure is the exact conflation this milestone exists to prevent."
    - "The fixture's pinned SHA-256 and byte-length constants must not be edited, and testdata/demo.md must not be regenerated, to make the new assertion pass. If the assertion fails, the fixture is wrong, not the assertion."
    - "The negative proof must not be performed by temporarily editing tracked source. No task in this plan may mutate a file and rely on restoring it; the proof is a permanent test against synthetic inputs."
    - "This phase must not wire enforcement. No change to the Makefile and no change to the CI workflow."
---

<objective>
Assert in `TestFixtureIntegrity` that `testdata/demo.md` begins with non-whitespace
pre-heading content, so the preamble property AC-14 depends on is proven once
against the hash-pinned fixture instead of being re-derived, and skipped, inside
the acceptance test.

Purpose: GATE-04 says content-conditional skips stay green and silent. The two
skips in `TestAC14_PreHeadingContentHasNoNode` are exactly that kind of skip and
must not become a gate failure class. But the property still has to hold, or AC-14
is a test that can quietly stop asserting anything. Moving the property to the
fixture invariant satisfies both: the skips stay, and they become unreachable for
the fixture the suite actually runs against.

Output: a strengthened `TestFixtureIntegrity`, one new unexported helper that
decides the invariant, and a permanent test that exercises that helper against
inputs which violate it. No change to `acceptance_test.go`.

**This plan enforces nothing.** It adds assertions to a test that already runs and
already passes. `make gate` behavior is unchanged.

## What "green and silent" means here, precisely

For the pinned fixture, PASS is the requirement: the AC-14 test's real assertions
about node spans must actually execute, so a SKIP would be a regression. That is
a statement about *these bytes*, not about the criterion.

The general GATE-04 behavior is the opposite and stays legal: a fixture that
genuinely lacks a preamble should make AC-14 **SKIP**, not fail. That is the
"green and silent" the requirement names. The invariant added here does not make
the preamble-free case illegal — it makes it impossible for the one fixture whose
bytes are pinned, and it fails loudly if those bytes ever change. Conflating the
two readings is the mistake this plan is shaped to avoid.
</objective>

## Review response — cycle 1

Findings from `01-REVIEWS.md` belonging to this plan, and where each landed.

| Finding | Severity | Resolution in this plan |
|---|---|---|
| The negative proof modifies real source with no precise restoration mechanism | MEDIUM | **The mutation is removed entirely.** The invariant is factored into a pure unexported function, and the negative proof becomes a permanent table test driving that function with synthetic violating inputs. Nothing in this plan writes and then restores a file. A frontmatter prohibition now forbids the mutate-and-restore pattern outright. Task 1. |
| `git diff --stat` cannot prove the temporary mutation was fully restored | MEDIUM | Moot by construction — there is no temporary mutation to restore, so no pre/post hash comparison is needed here. The equivalent requirement is **not** dropped: it is enforced in 01-03 Task 2, where a real file move is unavoidable, as a `trap`-based unconditional restore plus a pre/post SHA-256 comparison. |
| Failure-message requirements are over-specified | LOW | Reduced to three stable one-line messages, given verbatim in Task 1's action. The requirements to name both constants, print the offset in every branch, and repeat the regeneration rationale are dropped; the hash and length failures already name exact mismatches. |
| "Green and silent" is being read as PASS when GATE-04's general case is SKIP | LOW | Answered explicitly in the objective section above, and carried into Task 2's action so the executor cannot collapse the two readings. |
| Pipelines mask `go test` exit status | HIGH | Every criterion that inspects test output now runs under `set -o pipefail` or captures status and output separately. See **Execution shell**. |
| `git diff --name-only` with no revision range is vacuous | LOW | Anchored to the phase base commit `030521b`. |

**Deferred, with rationale:**

| Finding | Severity | Why deferred |
|---|---|---|
| "Consider adding an empty-heading guard to AC-14 itself — it indexes `headings[0]` directly" | LOW | The finding is correct: if the fixture and its pins were deliberately updated together to a heading-free document, AC-14 would panic rather than skip. But GATE-04's contract in this phase is that `acceptance_test.go` stays byte-identical, and Task 2 asserts exactly that; adding a guard there would violate the plan's own central claim. The risk is bounded in the meantime: the invariant added in Task 1 runs against the same pinned bytes and fails first with a message naming the file. Recorded here and carried into 01-03 Task 3's disposition list so the developer decides whether it becomes a backlog item or a Phase 2 change. |

## Execution shell

Every command in this plan is POSIX shell and MUST be run under Git Bash —
verified present on this host at `/usr/bin/bash` (`C:\Program Files\Git\usr\bin\bash.exe`),
GNU bash 5.3.15(1)-release, x86_64-pc-cygwin. `jq` is verified **absent**; no
command may depend on it. PowerShell is this workspace's interactive default and
will fail on `test -z` and on the capture forms used below.

**Pipeline rule.** A bare `go test … 2>&1 | grep -c X` reports grep's exit status,
not the test process's, so a build failure, a panic or a zero-test run all satisfy
it. Every check here either runs under `set -o pipefail` or captures the combined
output and `$?` separately and asserts them as independent conditions.

## Artifacts this phase produces

This plan introduces **one new unexported symbol** and modifies one existing test
function in place.

| Kind | Name | Status |
|---|---|---|
| Unexported func | `preambleInvariant(src []byte, headings []Heading) string` | **new** — created by this plan in `fixture_test.go` |
| Test function | `TestPreambleInvariant_Control` | **new** — created by this plan |
| Test function | `TestFixtureIntegrity` | pre-existing at `internal/core/domain/segment/fixture_test.go:128` — extended here, not created |
| Const | `fixtureSHA256`, `fixtureBytes` | pre-existing — read, never edited |
| Func | `loadFixture`, `detectHeadings` | pre-existing — called, never changed |
| Type | `Heading`, field `ByteStart` | pre-existing at `internal/core/domain/segment/headings.go:148` and `:163` — constructed in the control test, never changed |
| Import | `strings` | added to an existing import block |

The other new symbols this phase creates all belong to plan 01-01: the
`internal/platform/testenv` package, its exported `URLEnv`, `RequireEnv`,
`Required`, `Pool` and `Fixture`, its unexported `hostFromURL` and
`unparseableURLMsg`, and the `EPISTEMIC_OS_TEST_REQUIRE_DB` environment variable.
See that plan's artifacts table.

## Flagged assumption — spec-less edge probe

The deterministic edge probe returned 4 applicable edges across GATE-04 and
GATE-05. Three of them (E2 adjacency, E3 empty, E4 ordering — all GATE-05) are
resolved as explicit criteria in `01-01-PLAN.md`, where the full table and the
no-silent-drop accounting live: **4 surfaced == 3 authored into `must_haves.truths`
+ 1 flagged.** The row belonging to this plan's requirement is repeated here so it
is visible where it applies:

| # | Requirement | Category | Probe | Status |
|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (no category was assigned, so there is no probe question to answer) | **unresolved — flagged** |

E1 came back with no category at all, so there is no probe question to answer. It
is carried as an open item for the developer's disposition in 01-03 Task 3 rather
than dismissed here. The probe's categories are generic data-structure edges and
GATE-04 is a statement about which skips are legitimate signal, so a poor fit is
expected — that is a reason to flag, not to drop.

<execution_context>
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/workflows/execute-plan.md
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
</context>

## Verified ground truth

Measured in this repository at commit `030521b` before planning.

- **Phase base commit: `030521b1ec7c12df868445bf8d162527202d42f1`.** The cycle-1
  base `fcebad1` was mis-anchored; see `01-01-PLAN.md` and `01-03-PLAN.md` for the
  measurement. Every `git diff` in this plan is anchored to `030521b`.
- `go test ./internal/core/domain/segment/... -run 'TestAC14_PreHeadingContentHasNoNode|TestFixtureIntegrity' -v`
  reports **PASS for both**. The AC-14 test does not skip today, which means the
  fixture's first heading is not at byte 0 and the preamble is not whitespace only.
  The invariant this plan adds is therefore already true and must pass on first run
  — if it fails, something else is wrong and the fixture is the suspect.
- `fixture_test.go` pins `demo.md` at SHA-256
  `a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e` and
  `fixtureBytes = 81492`, and `loadFixture` hard-fails on a read error. Re-measured:
  `sha256sum internal/core/domain/segment/testdata/demo.md` matches that constant
  exactly. That is the house idiom this plan follows.
- The two content-conditional skips are at `acceptance_test.go:438` (first heading
  at offset 0) and `:451` (whitespace-only preamble). AC-14 indexes `headings[0]`
  at `:434` without an emptiness guard — see the deferred finding above.
- `detectHeadings(src []byte) []Heading` is declared at `headings.go:148` and
  records `h.Pos()` into `ByteStart` at `:163`, which is the same field AC-14 reads.
  `Heading` is an exported struct in the same package, so the control test can
  construct instances directly without calling the parser.
- `TestDetectHeadings_Fixture` asserts the fixture contains 22 headings, so a
  non-empty result from `detectHeadings` is established elsewhere — but this test
  must not depend on that, since Go guarantees no ordering between tests.
- `fixture_test.go` imports `crypto/sha256`, `encoding/hex`, `encoding/json`, `os`,
  `path/filepath`, `testing`. `strings` is not yet imported.
- The whole segment domain package runs without a database. Measured: `go test
  ./internal/core/domain/segment/... -count=1 -v` reports zero lines matching
  `^--- SKIP`. Every check in this plan is database-free.

<tasks>

<task type="auto">
  <name>Task 1: Assert the preamble as a fixture invariant, with a mutation-free negative proof</name>
  <files>internal/core/domain/segment/fixture_test.go</files>

  <read_first>
    - internal/core/domain/segment/fixture_test.go (whole file — the pinning constants, loadFixture, and TestFixtureIntegrity's existing carriage-return scan, whose message style the new failures must match)
    - internal/core/domain/segment/headings.go (lines 145-172 — detectHeadings' signature, the Heading struct and the ByteStart field the control test constructs directly)
    - internal/core/domain/segment/acceptance_test.go (lines 424-458 — the AC-14 test, to see exactly which two conditions are being lifted and to confirm neither is being altered)
  </read_first>

  <reversibility rating="reversible">
    One new unexported function, one new test, and three assertions added to an
    existing test. Reverting restores the phase base exactly.
  </reversibility>

  <action>
Add an unexported function `preambleInvariant(src []byte, headings []Heading) string`
to `fixture_test.go`. It returns the empty string when the invariant holds, and a
one-line failure message otherwise. Factoring the decision out of the test body is
what makes the negative proof possible without touching a single byte of tracked
source at run time — the alternative, mutating the file and restoring it, is
forbidden by this plan's prohibitions.

It decides three cases, in this order, and returns exactly one of these messages,
each on one line and each naming the fixture file:

- When `headings` is empty:
  `testdata/demo.md: no headings detected`
- When the first heading's `ByteStart` is zero:
  `testdata/demo.md: first heading starts at byte 0; AC-14 requires a non-whitespace preamble`
- When `strings.TrimSpace` of `src` up to that offset is empty, with N the offset:
  `testdata/demo.md: bytes [0,N) are whitespace only`

Keep them at that length. Do not name the pinning constants, do not restate the
regeneration rationale in each branch, and do not append the offset to the first
two — the hash and length failures already name exact mismatches, and the
comment described below carries the rationale once instead of three times.

Extend `TestFixtureIntegrity`, after the existing carriage-return scan, to call
`detectHeadings` on the bytes `loadFixture` returned, pass both to
`preambleInvariant`, and `t.Fatal` the returned message when it is non-empty. The
integrity test must call the function, not reimplement the checks inline — if it
reimplements them, the control test below exercises a copy and proves nothing
about the assertion that actually runs.

Do not rely on `TestDetectHeadings_Fixture` having run first. Go gives no ordering
guarantee across tests, and this test exists precisely to be the one that fails
first.

Add `TestPreambleInvariant_Control`, a table test that drives `preambleInvariant`
directly with synthetic inputs and is the permanent replacement for the
mutation-based negative proof cycle 1 proposed. Four cases:

- No headings at all: an empty slice with any source. Expect a non-empty message
  containing the fixture filename.
- First heading at byte 0. Expect a non-empty message containing the fixture
  filename.
- A whitespace-only preamble: a source whose leading bytes up to the first
  heading's offset are spaces, tabs and newlines. Expect a non-empty message
  containing the fixture filename.
- A valid preamble: real non-whitespace text before an offset greater than zero.
  Expect the empty string.

Construct `Heading` values directly rather than parsing markdown; only `ByteStart`
matters here and the parser is covered elsewhere. Each violating case must assert
the message is non-empty and mentions the file, and the holding case must assert
the message is exactly empty — that fourth case is what proves the function is not
simply returning a message unconditionally.

Add `strings` to the import block, in stdlib order.

Write one comment above the new block explaining the division of responsibility
this change establishes: the property is asserted here, where the fixture is
already pinned by hash and length and the answer is therefore decidable from bytes
that cannot change without a louder failure firing first; and it is deliberately
NOT asserted in the acceptance test, where the same question has to be answered per
run and a fixture that legitimately lacked a preamble would have to decline rather
than fail. State that this is what keeps the acceptance test's two
content-conditional declines green and silent instead of turning them into a gate
failure class. State also that a failure here means the fixture was replaced or
regenerated, not that the assertion drifted, and that the constants at the top of
this file are where to look.

Change nothing else in the file. Do not touch `loadFixture`, do not touch the two
pinning constants, and do not open the acceptance test for editing.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; go test ./internal/core/domain/segment/... -count=1 &amp;&amp; go test ./internal/core/domain/segment/... -count=1 -run 'TestFixtureIntegrity|TestPreambleInvariant_Control' -v 2>&amp;1 | grep -c '^--- PASS' | grep -qx 2 &amp;&amp; echo INVARIANT_OK</automated>
  </verify>

  <acceptance_criteria>
    - `go build ./...` and `go vet ./...` succeed, and `gofmt -l .` prints nothing.
    - `go test ./internal/core/domain/segment/... -count=1` exits 0. Assert the status directly, not via a grep of the output.
    - Under `set -o pipefail`, `go test ./internal/core/domain/segment/... -count=1 -run TestFixtureIntegrity -v 2>&1 | grep -c '^--- PASS: TestFixtureIntegrity'` prints `1`.
    - Under `set -o pipefail`, the same for `TestPreambleInvariant_Control` prints `1`.
    - `grep -c 'preambleInvariant' internal/core/domain/segment/fixture_test.go` prints at least `4` — the declaration, the call from the integrity test, and at least two references from the control test.
    - `grep -v '^\s*//' internal/core/domain/segment/fixture_test.go | grep -c 'strings.TrimSpace'` prints at least `1`.
    - `grep -c 'detectHeadings' internal/core/domain/segment/fixture_test.go` is strictly greater than `git show 030521b1ec7c12df868445bf8d162527202d42f1:internal/core/domain/segment/fixture_test.go | grep -c detectHeadings`.
    - **The negative proof is mutation-free.** `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1 --` prints exactly `internal/core/domain/segment/fixture_test.go` and nothing else, at every point during and after this task. No command in this task moves, renames, or temporarily rewrites any file.
    - **The control test has teeth.** Running only the three violating cases must produce three non-empty messages: `go test ./internal/core/domain/segment/... -count=1 -run 'TestPreambleInvariant_Control' -v` and confirm the subtest names for the no-headings, zero-offset and whitespace-only cases each report PASS. Each of those subtests asserts a non-empty return, so a `preambleInvariant` that always returned the empty string would fail all three.
    - **The control test cannot pass vacuously.** The fourth subtest, the valid-preamble case, asserts the return is exactly empty, so a `preambleInvariant` that always returned a message would fail it. Confirm that subtest reports PASS too.
    - `sha256sum internal/core/domain/segment/testdata/demo.md` still prints `a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e` — the fixture was not regenerated to accommodate the assertion.
  </acceptance_criteria>

  <done>
`TestFixtureIntegrity` proves the pinned fixture has a non-whitespace preamble by
calling one pure function, and that same function is exercised against three inputs
that violate the invariant and one that satisfies it — so the assertion is proven
able to both fail and pass, without any file in the working tree having been
mutated and restored. The segment package still passes with no database present.
  </done>
</task>

<task type="auto">
  <name>Task 2: Prove the AC-14 content skips are untouched, green and silent</name>
  <files>internal/core/domain/segment/acceptance_test.go (read-only — must remain byte-identical to the phase base)</files>

  <read_first>
    - internal/core/domain/segment/acceptance_test.go (lines 424-458 — both content-conditional declines and the assertions between them)
    - internal/core/domain/segment/fixture_test.go (the invariant added in Task 1, to confirm the two conditions now line up)
  </read_first>

  <action>
Verify, do not modify. This task exists because the tempting next move after Task 1
is to delete the two content-conditional declines in the AC-14 test as dead code —
and that would convert legitimate signal into a gate failure class, which is
precisely what GATE-04 forbids.

Confirm the AC-14 test still contains both declines, at the same two conditions:
one guarding a first-heading offset of zero at line 438 of the phase base, one
guarding a whitespace-only preamble at line 451. Confirm the assertions between and
after them are unchanged.

Confirm the file is byte-identical to the phase base by diffing it against that
commit. It must appear in no diff produced by this plan.

Run the segment package and confirm the AC-14 test reports PASS, not SKIP, and
record both facts in the summary with the distinction spelled out rather than
collapsed: PASS is the requirement **for these pinned bytes**, because it means the
declines did not fire and the test's real assertions about node spans actually ran.
It is not a claim that a decline would be wrong in general — under GATE-04 a
genuinely preamble-free fixture must produce SKIP, and that remains the correct and
legal outcome for such a fixture. A SKIP here, against the pinned fixture, would
mean the fixture lost its preamble, which Task 1's invariant should have caught
first; if both happen, Task 1's assertion is not wired to the same bytes and must
be fixed before this plan closes.

Record the observed result line in the summary, so Phase 2 and Phase 3 inherit a
stated baseline rather than an assumption.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; git diff --quiet 030521b1ec7c12df868445bf8d162527202d42f1 -- internal/core/domain/segment/acceptance_test.go &amp;&amp; go test ./internal/core/domain/segment/... -count=1 -run TestAC14_PreHeadingContentHasNoNode -v 2>&amp;1 | grep -q '^--- PASS: TestAC14_PreHeadingContentHasNoNode' &amp;&amp; echo AC14_INTACT</automated>
  </verify>

  <acceptance_criteria>
    - `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1 -- internal/core/domain/segment/acceptance_test.go` prints nothing — the file is byte-identical to the phase base.
    - `grep -c 't.Skip' internal/core/domain/segment/acceptance_test.go` prints the same number as `git show 030521b1ec7c12df868445bf8d162527202d42f1:internal/core/domain/segment/acceptance_test.go | grep -c 't.Skip'`.
    - `go test ./internal/core/domain/segment/... -count=1 -run TestAC14_PreHeadingContentHasNoNode` exits 0 — asserted from the status, before any output inspection.
    - Under `set -o pipefail`, `go test ./internal/core/domain/segment/... -count=1 -run TestAC14_PreHeadingContentHasNoNode -v 2>&1 | grep -c '^--- PASS: TestAC14_PreHeadingContentHasNoNode'` prints `1`.
    - The same command filtered for `^--- SKIP` prints `0`.
    - Under `set -o pipefail`, `go test ./internal/core/domain/segment/... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `0` — the whole segment package skips nothing, matching the phase base.
    - `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1 --` lists exactly `internal/core/domain/segment/fixture_test.go` for this plan's work, and no other path.
  </acceptance_criteria>

  <done>
Both content-conditional declines survive in the acceptance test, byte-identical to
the phase base, and the AC-14 test passes with its real assertions executing rather
than declining — with the summary recording that PASS is required for the pinned
fixture while SKIP remains the correct outcome for a genuinely preamble-free one.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repository → test process | `testdata/demo.md` is read from the working tree; its bytes determine whether 22 span assertions across the package mean anything |
| version control → working tree | Git's line-ending machinery can rewrite the fixture on checkout, which is why `.gitattributes` marks it `-text` and why the hash is pinned |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01-06 | Tampering | `testdata/demo.md` and the two pinning constants in `fixture_test.go` | medium | mitigate | A fixture edit, or a constant edit to accommodate one, would silently invalidate every byte offset in `expected.json` and could be used to make an assertion pass vacuously. Mitigated by the existing SHA-256 and byte-length pins, which fail before any offset assertion runs; by the plan prohibition forbidding edits to either; and by a Task 1 acceptance criterion that re-runs `sha256sum` on the fixture and compares it against the pinned constant after the change. |
| T-01-07 | Repudiation | the AC-14 content-conditional declines | medium | mitigate | Deleting the two declines would remove the record that a preamble-free fixture is a legitimate outcome rather than a failure, making a future maintainer unable to tell signal from breakage. Mitigated by Task 2, which asserts the file is byte-identical to the phase base commit rather than to an unanchored `HEAD`. |
| T-01-08 | Tampering | line-ending conversion on checkout | low | accept | Already mitigated at the phase base by `.gitattributes` marking the fixture `-text` and by the carriage-return scan in `TestFixtureIntegrity`. This plan changes neither and adds no new exposure. |
| T-01-13 | Tampering | the negative proof procedure | low | accept | **Newly retired, recorded rather than dropped.** Cycle 1 proposed proving the assertion has teeth by temporarily editing tracked source and restoring it, which risked leaving test code corrupt if the run aborted between edit and restore. This plan removes the mutation entirely in favour of a pure function driven by synthetic inputs, so the threat has no surface left. Retained in the register so a future reader can see the design was chosen against a known alternative rather than by default. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan adds no dependency. `strings` is stdlib; `go.mod` is unchanged. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
Run from the repository root under Git Bash. No database is needed for any check in
this plan.

1. `go build ./... && go vet ./... && gofmt -l .` — builds, vets, prints no files.
2. `go test ./internal/core/domain/segment/... -count=1` — exits 0, asserted from status.
3. The same with `-v` under `set -o pipefail`, counting `^--- SKIP` lines, prints 0.
4. The AC-14 test reports PASS, not SKIP, for the pinned fixture.
5. `git diff --name-only 030521b -- internal/core/domain/segment/acceptance_test.go` prints nothing.
6. `TestPreambleInvariant_Control` passes all four subtests: three violating inputs return non-empty messages naming the fixture, one valid input returns exactly empty. This is the negative proof, and it is permanent rather than a temporary mutation.
7. `sha256sum internal/core/domain/segment/testdata/demo.md` still matches the pinned constant.
8. `git diff --name-only 030521b --` for this plan lists exactly one file.
</verification>

<success_criteria>
- The preamble property is asserted where the fixture is already hash-pinned, so it is decidable rather than re-derived.
- A future fixture that loses its preamble fails one test with a one-line message naming the file, instead of silently downgrading AC-14 to a skip.
- The assertion is proven able to fail, by a permanent test against synthetic violating inputs rather than by a temporary mutation of tracked source.
- The two content-conditional declines survive byte-identical — GATE-04's "green and silent" holds literally, and the summary records that PASS is required for the pinned fixture while SKIP stays correct for a genuinely preamble-free one.
- The segment package skips nothing and passes, exactly as at the phase base.
- Exactly one file changed, and it is not the acceptance test, the Makefile, or the CI workflow.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md` when done.

Record in it: the observed result lines for `TestFixtureIntegrity`,
`TestPreambleInvariant_Control` (all four subtests) and the AC-14 test; the three
invariant failure messages verbatim, since Phase 3 may assert against them; the
re-measured fixture SHA-256; confirmation that the acceptance test is byte-identical
to the phase base commit `030521b`; and the deferred AC-14 empty-heading guard, so
it reaches 01-03 Task 3's disposition list rather than evaporating.
</output>

#### gsd-review-plan-02.md

---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 03
type: execute
wave: 2
depends_on: ["01-01", "01-02"]
files_modified:
  - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md
autonomous: true
requirements: [GATE-04, GATE-05]

estimate:
  tokens: 48000
  raw_tokens: 48000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "`make gate` exits 0 with no database present, exactly as at the phase base commit — the mechanism built in 01-01 enforces nothing"
    - "`make gate` exits 0 with a reachable database and migrations applied"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and a reachable database, the store and approved packages report 0 skipped tests and 0 failures, and the set of tests that PASS contains every test that SKIPPED in the unescalated baseline — set equality, not a count"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set, each of the three environment conditions produces a non-zero exit AND a message naming that specific cause: the variable, the host, the fixture path — status and content asserted as independent conditions"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB unset and the database unreachable, the suite exits 0 and the database-backed tests SKIP — the branch measured at the phase base, and half of ROADMAP success criterion 3"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB unset and the cross-package fixture unreadable, the fixture round-trip test SKIPs and the package exits 0 — the other half of ROADMAP success criterion 3"
    - "No commit in this phase touches the Makefile or the CI workflow, measured from the corrected phase base commit 030521b"
    - "On the unparseable-URL path, no component of the connection string reaches the output — a claim measured to be FALSE at the phase base, so the criterion proving it can actually fail"
    - "The hash-pinned fixture is byte-identical before and after the unreadable-fixture proof, verified by SHA-256 comparison, with restoration guaranteed by a shell trap rather than by statement ordering"
  artifacts:
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md
  key_links:
    - "The escalated-green run is the only check that proves the helper does not fail spuriously when the database IS present — without it, a helper that always failed would satisfy every other criterion in this phase"
    - "The unchanged-gate check is what makes this phase non-enforcing rather than merely intended to be; Phase 2 depends on inheriting a green tree"
    - "The DSN leak control is the only criterion in the phase that is measured to fail at the phase base; if it is weakened back to a password canary it becomes unfalsifiable and the phase's security claim becomes decorative"
  prohibitions:
    - "This phase must not wire enforcement. No change to the Makefile and no change to the CI workflow, even though both are one line away from turning the mechanism on — and the temptation is highest here, in the plan that measures the difference."
    - "The escalation flag must not default to on. With EPISTEMIC_OS_TEST_REQUIRE_DB unset, every test that skips at the phase base must still skip and the suite must still exit 0."
    - "The two content-conditional skips in the segment acceptance test must not be deleted, converted into failures, or made conditional on the escalation flag. A fixture that genuinely lacks a preamble is real signal, and turning that into a gate failure is the exact conflation this milestone exists to prevent."
    - "A failing check in this plan must not be resolved by weakening the check. If the escalated run does not reach 0 skips, the helper is wrong; the target is not."
    - "No check in this plan may take the form of a bare pipeline from `go test` into `grep`. Such a check reports grep's exit status, not the test process's, and is satisfied by a build failure, a crash, an unexpected success or a zero-test run — the exact vacuity this milestone exists to remove."
    - "The unreadable-fixture proof must not rely on statement ordering to restore the fixture. Restoration must be installed as a shell trap before the file is moved, and proven by a SHA-256 comparison taken before the move and after the restore."
---

<objective>
Measure that the escalation mechanism built in 01-01 works when the database is
present, that each escalated condition names its own cause, that each unescalated
condition still skips, and — the hard boundary of this phase — that `make gate`
behaves exactly as it did before any of it landed.

Purpose: this phase's whole claim is "the mechanism exists and enforces nothing".
Both halves need evidence. Without the escalated-green run, a helper that failed
unconditionally would satisfy every other criterion in the phase. Without the
unchanged-gate run, "non-enforcing" is an intention rather than a measurement, and
Phase 2 would inherit a red tree it did not cause.

Output: a SUMMARY recording the measured baseline that Phase 2 will be diffed
against and that Phase 3's proof tests will assert.

**This plan writes no source file.** `files_modified` lists exactly one path, its
own SUMMARY, which is a planning artifact rather than source. That distinction is
stated here because cycle 1 declared `files_modified: []` while requiring the
summary as an artifact, which was a contradiction the executor had to resolve on
its own. If a check fails, the fix belongs in 01-01 or 01-02 and this plan re-runs.
</objective>

## Review response — cycle 1

`01-REVIEWS.md` concentrated its heaviest findings on this plan, correctly: it is
the phase's evidence-producing plan, so a weakness in its verification mechanics
is a weakness in every claim the phase makes. Each finding and where it landed.

| Finding | Severity | Resolution in this plan |
|---|---|---|
| Several pipelines can mask the `go test` exit status | HIGH | Every scenario now uses the capture form — combined output into a variable, `$?` on the following statement, then status and content asserted as independent conditions — or runs under `set -o pipefail`. A frontmatter prohibition forbids the bare-pipeline form. See **Execution shell**. |
| The unreadable-fixture procedure specifies no actually unconditional restore | HIGH | Task 2 now installs a `trap … EXIT INT TERM` **before** the move, captures the fixture's SHA-256 before the move, restores explicitly after the run, clears the trap, re-hashes, and asserts the two hashes are equal. The full command is given verbatim as an acceptance criterion, not described. |
| Phase base `fcebad1` is mis-anchored; the audit fails before any Phase 1 code exists | HIGH | Re-anchored to `030521b1ec7c12df868445bf8d162527202d42f1`, and the anchor was verified by running the two audit commands: both now return empty. `fcebad1` was measured to fail both — `868d45b` landed after it and modified `.github/workflows/ci.yml`. The guard is no longer "is it an ancestor" (which `fcebad1` satisfied while the audit failed) but the full four-part check, and it has been **moved to 01-01 Task 1's `<precondition>`** so a wrong anchor fails at phase start rather than at audit time. `01-PLAN-MANIFEST.json` is re-frozen with the corrected value. |
| T-01-01's ground truth is false; the phase's only blocking control is unfalsifiable | HIGH | Scenario D is rebuilt. The password canary is retired — pgx v5.7.2 redacts the password on all four DSN shapes measured, so that canary passes at the phase base with zero code written. It is replaced by a **database-name** leak token, measured to appear in the phase-base output (count 1), plus an assertion that the library's parse-error text is absent, plus non-zero exit, plus the fixed message present. T-01-09 is restated and downgraded from `high` to `medium` accordingly; see `<threat_model>`. |
| `files_modified: []` contradicts the required `01-03-SUMMARY.md` artifact | MEDIUM | The summary is now listed in `files_modified`, and the source/planning-artifact distinction is stated in the objective. |
| The clean `git status --porcelain` criterion conflicts with writing the summary | MEDIUM | Task 3 now specifies the ordering explicitly and states both expected states — before the summary is written, and after. |
| Scenario D's malformed-DSN canary lacks positive assertions | MEDIUM | Scenario D now asserts non-zero exit and the fixed parse-failure message text, alongside the two absence assertions. |
| Verification commands are POSIX-only and the shell is unspecified on a Windows workspace | MEDIUM | **Execution shell** below states Git Bash explicitly, with the verified path, version, and the tool inventory — including that `jq` is absent, so no command may use it. The reviewer's runnability claim was partly overstated (every command re-ran correctly under Git Bash during review); the documentation gap was real and is now closed. |
| No scenario covers the non-escalated skip path for an unreachable database or an unreadable fixture | MEDIUM | Added as Scenario A2 (Task 1, database-free) and Scenario A3 (Task 2, needs a live pool). ROADMAP success criterion 3 is now fully covered rather than half. |
| "At least 38 `--- PASS` lines" is an indirect execution proof | LOW | Replaced with a `go test -json` set comparison: the set of test names that SKIP in the unescalated baseline must be a subset of the set that PASS in the escalated run, checked with `comm`. This is set equality on names, not a count, and is immune to subtest inflation. |
| The compose database's final state is unstated | LOW | Declared: **the compose database is left running** at the end of this plan. Task 3's last database action is `make up`, and the end state is now an explicit acceptance criterion. |
| `EPISTEMIC_OS_TEST_REQUIRE_DB` also gates the cross-package fixture, not just the DB | LOW | Added to the contract decisions queued for the developer's disposition in Task 3. |
| `git diff --name-only` with no revision range is vacuous | LOW | All diffs anchored to `030521b`. |
| The four generic probe edges add noise; dismiss E1/E2/E4 and mark E3 covered | LOW | **Rejected as stated, addressed in substance.** The spec-less fallback protocol forbids planner-side dismissal of a probe edge, so they cannot simply be struck. Instead each was given the referent it actually has in this phase: E2 → the order in which simultaneous conditions are decided, E3 → the empty flag value and the empty host, E4 → independence from test execution order (pinned by `-shuffle=on`). Three are now explicit criteria in 01-01's `must_haves.truths`. Only E1, which the probe returned with no category at all, remains unresolved, and it is queued for the developer in Task 3. Accounting: 4 surfaced == 3 authored + 1 flagged. |

## Execution shell

Every command in this plan is POSIX shell and MUST be run under Git Bash.
Verified present on this host: `/usr/bin/bash` (Windows path
`C:\Program Files\Git\usr\bin\bash.exe`), GNU bash 5.3.15(1)-release,
x86_64-pc-cygwin. Also verified on PATH and used below: `env`, `grep`, `sort`,
`comm`, `sha256sum`, `cut`, `mktemp`, `wc`, `git`, `docker`, and `go` (go1.24.13
windows/amd64). Verified **absent**: `jq` — no command in this plan may depend on
it, which is why the `-json` checks below use `grep` rather than a JSON parser.
PowerShell is this workspace's interactive default; `env -u`, `test -z`, `trap`
and `$(…)` capture will not behave there. Launch Git Bash explicitly.

**Pipeline rule.** A bare `go test … 2>&1 | grep -c X` reports grep's exit status,
not the test process's. A build failure, a panic, an unexpected success and a
zero-test run all satisfy such a check. Every scenario below therefore uses the
capture form: assign the combined output to a variable, capture `$?` on the *next*
statement, and assert status and content as separate conditions. Where a pipeline
is genuinely more readable, `set -o pipefail` must be in effect first.

**Skip-counting rule.** `go test -json` emits `"Action":"skip"` for packages with
no test files as well as for skipped tests. Measured at the phase base over
`./...`: 49 skip events, of which **38 carry a `"Test"` field** and 11 are
package-level. Every `-json` skip count in this plan filters for `"Test":"`. The
`-v` method — counting lines matching `^--- SKIP` — was independently measured at
38 and the two must agree.

## Artifacts this phase produces

This plan produces **no code symbols**. Its only artifact is its SUMMARY, which is
listed in `files_modified`.

The new symbols this phase creates belong to plans 01-01 and 01-02 — the
`internal/platform/testenv` package with its exported `URLEnv`, `RequireEnv`,
`Required`, `Pool` and `Fixture` and its unexported `hostFromURL` and
`unparseableURLMsg`; the `EPISTEMIC_OS_TEST_REQUIRE_DB` environment variable; and
in the segment domain the unexported `preambleInvariant` and the new
`TestPreambleInvariant_Control`. See those plans' artifacts tables.

`EPISTEMIC_OS_DB_URL`, `make gate`, `make up`, `make migrate`,
`TestSaveRun_FixtureRoundTripsAllOffsets`, `TestFixtureIntegrity` and the CI
workflow are all pre-existing and are read, never written, by this plan.

## Flagged assumptions — spec-less edge probe

No SPEC exists for this phase. The deterministic edge probe over GATE-04 and
GATE-05 returned 4 applicable edges. After cycle 1, three have been given the
referent they actually have in this phase and authored as explicit criteria in
`01-01-PLAN.md`'s `must_haves.truths`. One remains unresolved and is reproduced
here because this is the plan a human reviews, and it may not be silently dropped.

| # | Requirement | Category | Probe | Status | Where |
|---|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (no category was assigned, so there is no probe question to answer) | **unresolved — flagged** | queued for disposition in Task 3 |
| E2 | GATE-05 | adjacency | When two things are exactly equal or just touch, do they merge, collide, or separate? | **resolved — explicit** | `01-01` truth: `Pool` decides in a documented order and names exactly one cause; `Fixture` runs only after `Pool` returns |
| E3 | GATE-05 | empty | What is the result for empty, single-element, or null input? | **resolved — explicit** | `01-01` truth: empty flag value is false; empty and keyword/value DSNs yield an empty host and a fixed placeholder |
| E4 | GATE-05 | ordering | When elements compare equal, is output order specified and stable? | **resolved — explicit** | `01-01` truth: outcome is independent of execution order; `-shuffle=on` yields the same 38 |

Accounting: **4 surfaced == 3 authored into `must_haves.truths` + 1 flagged.**
E1 is not dismissed by the planner; the executor must not dismiss it either.

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

Measured in this repository at commit `030521b`, by running the commands, before
any plan in this phase ran. This is the baseline every check below is compared
against.

- **Phase base commit: `030521b1ec7c12df868445bf8d162527202d42f1`.** Verified at
  planning time, all four properties: `git rev-parse --verify` succeeds;
  `git merge-base --is-ancestor 030521b HEAD` exits 0;
  `git log --format=%H 030521b..HEAD -- Makefile .github/workflows/ci.yml` prints
  nothing; `git diff --name-only 030521b..HEAD` filtered against `^internal/` and
  `^\.planning/` prints nothing.
- **Why not `fcebad1`.** Cycle 1 anchored here and the anchor was wrong.
  `868d45b` ("Run the store and approved tests against a real Postgres in CI")
  landed after `fcebad1` and changed `.github/workflows/ci.yml`. Measured:
  `git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml` returns
  1 commit where the plan required 0, and the outside-paths filter returns 1 where
  it required 0. `git merge-base --is-ancestor fcebad1 HEAD` exits 0, so the
  ancestry guard passed while the audit it guarded failed. Ancestry is necessary
  and not sufficient; the four-part check above is the guard, and it runs as
  01-01 Task 1's `<precondition>`, before any Phase 1 code can make a real
  violation indistinguishable from a mis-anchor.
- `go test ./... -count=1` with no database: **exit 0, 38 test-level skips.**
  Identical with `-shuffle=on`. Under `-json`, 49 skip events of which 38 carry a
  `"Test"` field.
- `make gate` is `vet`, then a `gofmt -l .` check, then `go build ./...`, then
  `go test ./... -count=1`, defined at `Makefile:39-45`. Nothing in it starts
  PostgreSQL and nothing in it sets the escalation flag.
- The local DSN for the compose service is
  `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`.
  `make up` starts it and waits for readiness; `make migrate` applies migrations
  and requires `EPISTEMIC_OS_DB_URL` to be exported.
- The store package's cross-package fixture read resolves
  `../../../core/domain/segment/testdata/demo.md` at `segmentation_test.go:276`
  and runs only after a pool is obtained at `:272`, so exercising either fixture
  path — escalated failure or unescalated skip — requires a live database.
- **Non-escalated, unreachable database: SKIP.** Measured with
  `EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable'` and the
  flag unset: `TestSaveRun_FixtureRoundTripsAllOffsets` reports `--- SKIP` and the
  package exits 0. This branch must survive; it is half of ROADMAP criterion 3.
- **pgx v5.7.2 redacts the password and echoes everything else.** Measured on four
  DSN shapes against the unmodified helper — URL form, keyword/value form,
  `?password=` query, `?sslpassword=` query — the password renders as `xxxxxx` or
  `xxxxx` every time and a distinctive token placed in the password position was
  never present in the output. A token placed in the **database-name** position
  *was* present, count 1, on both the URL and keyword/value forms, alongside the
  library's parse-error text. Scenario D is built on the database-name token for
  exactly that reason: it is measured to fail at the phase base.
- The `Ping` error is built by the library from the parsed config, not the raw DSN:
  ``failed to connect to `user=u database=nodb`: 127.0.0.1:1 (127.0.0.1): dial
  error: …``. It names the host, omits the password, and discloses the user and
  database name.
- `.github/workflows/ci.yml` line 36 already sets `EPISTEMIC_OS_DB_URL` and the
  workflow already provisions PostgreSQL and applies migrations, delivered at
  `868d45b`. Neither that file nor the Makefile may be edited in this phase.
- `sha256sum internal/core/domain/segment/testdata/demo.md` prints
  `a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e`, matching the
  constant pinned in `fixture_test.go`. This is the value Task 2 compares against.

## Compose database end state

Declared, because cycle 1 left it unstated: **the compose PostgreSQL service is
left running when this plan finishes.** Task 3 deliberately stops it to make the
developer-without-Docker case real rather than assumed, then brings it back up as
its last database action, and asserts the running state as an acceptance criterion.
If the developer wants it down, `make down` after the phase; this plan does not
guess.

<tasks>

<task type="auto">
  <name>Task 1: Database-free behavioral matrix and non-enforcement audit</name>
  <files>none — verification only, no file is written by this task</files>

  <read_first>
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md (the exported signatures, the observed failure text and the measured leak-token counts, so this task compares against a stated baseline rather than re-deriving one)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md (the fixture invariant result and the AC-14 baseline)
    - Makefile (lines 39-45 — the exact gate definition being held constant)
    - internal/platform/testenv/testenv.go (the helper as built, to confirm the observed messages come from the branches this plan believes they do, and to read `unparseableURLMsg` so Scenario D can assert its text)
  </read_first>

  <action>
Run the five scenarios that need no database, and the non-enforcement audit. Record
every observed exit status and message verbatim; the summary is the artifact.

Run every scenario with the capture form. Assign the combined output of the test
command to a shell variable, capture the exit status on the following statement,
and then assert status and content as separate conditions. Do not pipe a test
command into `grep` and read the pipeline's status — that reports grep's status,
so a build failure or a zero-test run satisfies it, and this whole milestone exists
because a check that cannot fail proves nothing.

Scenario A, the preserved default. With both `EPISTEMIC_OS_DB_URL` and
`EPISTEMIC_OS_TEST_REQUIRE_DB` explicitly removed from the environment, run the
full suite. It must exit 0 and report exactly 38 test-level skips — the count
measured at the phase base. Use `env -u` rather than assuming the variables are
unset, since a developer shell may export the local DSN. Run it once more with
`-shuffle=on` and confirm the same 38, which is the ordering edge E4's criterion.

Scenario A2, the preserved skip for an unreachable database. With the flag removed
and the URL addressing `127.0.0.1` port 1, run the store package's fixture
round-trip test by name with `-v`. It must exit 0 and report SKIP for that test.
This is the branch measured at the phase base and it is half of ROADMAP success
criterion 3, which cycle 1 left unverified. A failure here means the helper
escalated without being asked to, which is Phase 2's change arriving early.

Scenario B, escalated with no URL. With the flag set and the URL removed, run the
store package and then the approved package. Each must exit non-zero, and each
output must name both `EPISTEMIC_OS_DB_URL` and `EPISTEMIC_OS_TEST_REQUIRE_DB` —
the second because a message that names only the missing variable does not tell the
developer why it was fatal rather than skipped. This scenario also exercises edge
E2: the fixture is unreachable in this configuration too, and exactly one cause must
be named, the database one, because the fixture branch is only reached after the
pool helper has returned.

Scenario C, escalated against a closed port. With the flag set and the URL
addressing `127.0.0.1` port 1, run the store package. It must exit non-zero and the
output must contain that host and port, proving the message names the specific
machine it could not reach rather than restating the variable.

Scenario D, the connection-string disclosure audit. This is the phase's one
security control and cycle 1's version of it could not fail. Run the store package
twice with the flag set: once with a URL-form DSN and once with a keyword/value
DSN, each malformed so the pool constructor rejects it, and each carrying the
distinctive token named in this task's acceptance criteria in its **database-name**
position — not its password position. Assert four conditions independently on each
run: the exit status is non-zero; the output contains the fixed parse-failure text
the helper emits; the token count in the output is zero; and the library's own
parse-error phrasing is absent. Both token counts were measured as 1 at the phase
base, so this check has teeth, whereas a password-position token is redacted by the
library and would have passed with no code written.

Then the non-enforcement audit, anchored at `030521b`. Confirm no commit in this
phase touched the Makefile or the CI workflow, by listing commits from the phase
base to HEAD restricted to those two paths. Confirm the full diff from the phase
base touches nothing outside `internal/` and `.planning/`. Confirm the gate itself
still runs green with no database.

If any scenario fails, do not adjust the scenario. Report it and stop — the defect
belongs to 01-01 or 01-02, and this plan re-runs after that fix.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate &amp;&amp; test "$(env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&amp;1 | grep -c '^--- SKIP')" = "38" &amp;&amp; test "$(env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -shuffle=on -json 2>&amp;1 | grep '\"Action\":\"skip\"' | grep -c '\"Test\":\"')" = "38" &amp;&amp; test -z "$(git log --format=%H 030521b1ec7c12df868445bf8d162527202d42f1..HEAD -- Makefile .github/workflows/ci.yml)" &amp;&amp; test -z "$(git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1..HEAD | grep -v '^internal/' | grep -v '^\.planning/')" &amp;&amp; echo NONENFORCING_OK</automated>
  </verify>

  <acceptance_criteria>
    - **Scenario A.** `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0, asserted from its status.
    - **Scenario A.** Under `set -o pipefail`, `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `38`; and the `-json` form, filtered to skip events carrying a `"Test"` field, also prints `38`. The two counting methods must agree — a bare `grep -c '"Action":"skip"'` prints 49 and is wrong.
    - **Scenario A, edge E4.** The same `-json` count with `-shuffle=on` also prints `38`.
    - **Scenario A2, the preserved unreachable-database skip.** Capture once: the combined output of `env -u EPISTEMIC_OS_TEST_REQUIRE_DB EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 -v 2>&1`, with `$?` captured on the next statement. Assert independently: the status is `0`; the output contains a line matching `^--- SKIP: TestSaveRun_FixtureRoundTripsAllOffsets`. Measured at the phase base as SKIP/exit 0.
    - **Scenario B, store.** Capture once: `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 2>&1`. Assert independently: status non-zero; output contains `EPISTEMIC_OS_DB_URL`; output contains `EPISTEMIC_OS_TEST_REQUIRE_DB`.
    - **Scenario B, approved.** The same three assertions against `./internal/adapters/secondary/approved/...`.
    - **Scenario B, edge E2.** In the same captured output, exactly one cause is named: the output does **not** contain `testdata/demo.md`. The fixture is equally unavailable in this configuration, and the fixture branch must not have been reached, because it runs only after the pool helper returns.
    - **Scenario C.** Capture once with `EPISTEMIC_OS_TEST_REQUIRE_DB=1` and `EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable'` against the store package. Assert independently: status non-zero; output contains `127.0.0.1:1`.
    - **Scenario D, URL form.** Capture once with `EPISTEMIC_OS_TEST_REQUIRE_DB=1` and `EPISTEMIC_OS_DB_URL='postgres://u:pw@ bad host/DSNLEAKCANARY'` against the store package. Assert four conditions independently: status is non-zero; the output contains `EPISTEMIC_OS_DB_URL`; `printf '%s' "$out" | grep -c DSNLEAKCANARY` prints `0`; `printf '%s' "$out" | grep -c 'cannot parse'` prints `0`. **Both counts were measured as `1` at the phase base**, so this criterion is falsifiable — record the post-change counts in the summary next to the phase-base counts.
    - **Scenario D, keyword/value form.** The same four assertions with `EPISTEMIC_OS_DB_URL='host=x port=notanumber password=pw dbname=DSNLEAKCANARY'`. Also measured as `1`/`1` at the phase base.
    - **Scenario D, negative control on the audit itself.** Before or after the two runs above, confirm the leak detector can see a leak: `printf '%s' 'cannot parse `postgres://u:xxxxxx@ bad host/DSNLEAKCANARY`' | grep -c DSNLEAKCANARY` prints `1`. An absence assertion whose detector has never been shown to detect a presence is not evidence.
    - **Audit.** `git log --format=%H 030521b1ec7c12df868445bf8d162527202d42f1..HEAD -- Makefile .github/workflows/ci.yml` prints nothing.
    - **Audit.** `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1..HEAD | grep -v '^internal/' | grep -v '^\.planning/'` prints nothing. Note the anchored escaping — an unescaped `.planning` would match any character in that position.
    - **Audit.** `git rev-parse --verify 030521b1ec7c12df868445bf8d162527202d42f1` succeeds and `git merge-base --is-ancestor 030521b1ec7c12df868445bf8d162527202d42f1 HEAD` exits 0. Both are necessary and neither is sufficient; the two audit commands above are the actual guard, which is why 01-01 Task 1 asserted all four before writing any code.
  </acceptance_criteria>

  <done>
Every database-free claim in this phase is measured and recorded: the default run
reproduces the phase base at 38 skips and exit 0, shuffled or not; an unreachable
database still skips when the flag is unset; two of the three escalated conditions
name their own cause with exit status asserted independently of message content;
the connection string no longer reaches the output on the parse path, a claim that
was false at the phase base; and neither the Makefile nor the CI workflow was
touched, measured from a phase base that has itself been verified rather than
assumed.
  </done>
</task>

<task type="auto">
  <name>Task 2: Escalated-green, preserved fixture skip, and the unreadable-fixture failure proof</name>
  <files>none — verification only; the fixture is moved and restored within the task under a trap, and must end byte-identical</files>

  <precondition>PostgreSQL is running and migrated: `make up` succeeds, `EPISTEMIC_OS_DB_URL` is exported as `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`, and `make migrate` exits 0 — without a live database none of the three claims in this task is decidable and execution must halt rather than record an unverified pass.</precondition>

  <read_first>
    - Makefile (lines 18-23 and 47-48 — the up and migrate targets and the readiness wait, so the precondition is satisfied the same way CI does it)
    - internal/adapters/secondary/store/segmentation_test.go (the fixture-round-trip test — the only test that exercises either fixture path, the relative path it resolves, and the fact that the read happens after the pool is obtained)
    - internal/platform/testenv/testenv.go (the fixture branch, to confirm the observed message comes from the escalated path and to read the unescalated skip text)
    - internal/core/domain/segment/fixture_test.go (the pinned SHA-256 and byte-length constants, which are what the post-restore integrity check re-verifies)
  </read_first>

  <action>
Prove the three claims that require a real database.

First, escalated green. With the database up, migrations applied, the DSN exported
and the escalation flag set, run the store and approved packages. Every test must
run: zero skipped and zero failed. This is the check that distinguishes a working
mechanism from one that simply always fails — without it, a helper hard-coded to
fail would satisfy every other criterion in this phase.

Prove it by name rather than by count. Run the same two packages twice under
`-json`: once unescalated with the URL removed, collecting the sorted set of test
names whose action is `skip` and which carry a `Test` field; once escalated against
the live database, collecting the sorted set of test names whose action is `pass`.
Every name in the first set must appear in the second. A count of PASS lines is an
indirect proof that subtests inflate and that says nothing about which tests ran;
set containment says exactly the right thing, which is that each test that declined
without a database now executes with one.

Second, the preserved fixture skip. Still with the database up but with the
escalation flag removed, move the fixture aside under the trap procedure described
below and run the fixture round-trip test by name. It must exit 0 and report SKIP.
This is the second half of ROADMAP success criterion 3 and cycle 1 did not cover it:
the unescalated fixture branch is a distinct branch of the new helper from the
unescalated database branch, and only the latter was verified.

Third, the escalated fixture failure. Same move, flag set: the test must exit
non-zero with a message naming the fixture path.

For both fixture scenarios, restoration is not a step to be sequenced — it is a
trap installed before the move. Capture the fixture's SHA-256 first. Create a
temporary directory. Install a trap on EXIT, INT and TERM that restores the file
from that directory if the file is missing, so an interruption at any point between
the move and the explicit restore still leaves the tree intact. Only then move the
file. Run the test with the capture form. Restore explicitly, clear the trap,
re-hash, and assert the two hashes are equal. The full command is given verbatim in
this task's acceptance criteria; use it rather than reconstructing it, because the
file being moved is the one whose corruption invalidates all 22 offsets in
`expected.json` and every span assertion in the segment package.

Scope each run to the store package alone so the segment domain package, which owns
that fixture, is never compiled against a missing file during the window.

After restoring, confirm the working tree is clean and the fixture's hash still
matches by running the segment package's integrity test, which pins it. Do not
proceed to Task 3 until both are confirmed.

Record the exact escalated failure message for the fixture path in the summary, and
the exact unescalated skip message alongside it. Phase 3's proof test for GATE-03
asserts against the first, so an approximation is not good enough.

If the escalated run reports any skip or any failure, stop and report. Do not
narrow the package selection, do not add a skip exclusion, and do not lower the
target — the target is the requirement.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; export EPISTEMIC_OS_DB_URL='postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable' &amp;&amp; make migrate &amp;&amp; env -u EPISTEMIC_OS_DB_URL go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -json 2>&amp;1 | grep '"Action":"skip"' | grep -o '"Test":"[^"]*"' | sort -u &gt; /tmp/base_skips.txt &amp;&amp; test "$(wc -l &lt; /tmp/base_skips.txt)" = "38" &amp;&amp; EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -json 2>&amp;1 | grep '"Action":"pass"' | grep -o '"Test":"[^"]*"' | sort -u &gt; /tmp/esc_pass.txt &amp;&amp; test -z "$(comm -23 /tmp/base_skips.txt /tmp/esc_pass.txt)" &amp;&amp; EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 &amp;&amp; echo ESCALATED_GREEN_OK</automated>
  </verify>

  <acceptance_criteria>
    - `make up` exits 0 and `make migrate` exits 0 with the DSN exported. Both asserted from status.
    - **Escalated green, zero skips.** Under `set -o pipefail`, the escalated `-json` run over both packages, filtered to skip events carrying a `"Test"` field, prints `0`. The plain (non-`-json`) escalated run exits 0, asserted from its own status.
    - **Escalated green, set containment.** `/tmp/base_skips.txt` — the sorted unique `"Test":"…"` names from the unescalated `-json` run — has exactly `38` lines. `comm -23 /tmp/base_skips.txt /tmp/esc_pass.txt` prints nothing: every test that skipped without a database passes with one. This replaces the cycle-1 criterion "at least 38 `--- PASS` lines", which subtests inflate and which names no test.
    - **Preserved fixture skip, flag unset.** Using the trap procedure below with `env -u EPISTEMIC_OS_TEST_REQUIRE_DB`, running `go test ./internal/adapters/secondary/store/... -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 -v`: assert independently that the status is `0` and that the output contains a line matching `^--- SKIP: TestSaveRun_FixtureRoundTripsAllOffsets`.
    - **Escalated fixture failure, with the unconditional restore.** Run exactly this, under Git Bash, and assert it prints `FIXTURE_FAIL_OK`:
      `cd C:/EpistemicOS/epistemicos-gsd-pilot && set -o pipefail && FIX=internal/core/domain/segment/testdata/demo.md && BEFORE=$(sha256sum "$FIX" | cut -d' ' -f1) && TMP=$(mktemp -d) && trap 'if [ -f "$TMP/demo.md" ] && [ ! -f "$FIX" ]; then mv "$TMP/demo.md" "$FIX"; fi' EXIT INT TERM && mv "$FIX" "$TMP/demo.md" || exit 1; out=$(EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 2>&1); st=$?; mv "$TMP/demo.md" "$FIX"; trap - EXIT INT TERM; AFTER=$(sha256sum "$FIX" | cut -d' ' -f1); test "$BEFORE" = "$AFTER" && test "$st" -ne 0 && printf '%s' "$out" | grep -q 'core/domain/segment/testdata/demo.md' && echo FIXTURE_FAIL_OK`
    - **Pre/post hash equality is asserted, not assumed.** `$BEFORE` and `$AFTER` above must both equal `a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e`, the value pinned in `fixture_test.go` and re-measured at the phase base. Record both in the summary.
    - **The trap is installed before the move.** In the command above, `trap … EXIT INT TERM` precedes `mv "$FIX" "$TMP/demo.md"`. A restore that is merely the next statement is not sufficient: an interruption between the two would leave the tree corrupt in the one file whose corruption invalidates every offset in `expected.json`.
    - **Post-restore integrity.** `go test ./internal/core/domain/segment/... -run 'TestFixtureIntegrity' -count=1` exits 0 — the pinned hash and byte length still match, proving the move-and-restore was lossless. Run it after the trap is cleared.
    - **Working tree clean after the fixture work, before any summary is written.** `git status --porcelain` prints exactly one line, `?? .planning/config.json`, the pre-existing untracked file. See Task 3 for the expected state once the summary exists.
    - **Gate green with the database up.** `env -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0 with the database still running.
  </acceptance_criteria>

  <done>
With a live database the escalated run executes every test that skipped without
one — proven by name-set containment, not by a PASS count — and skips none. The
unescalated fixture branch still skips, completing ROADMAP criterion 3. The
escalated fixture branch fails with a message naming the path. The fixture is
restored under a trap installed before the move and its SHA-256 is proven equal
before and after.
  </done>
</task>

<task type="auto">
  <name>Task 3: Consolidate the phase baseline and surface the contract decisions for sign-off</name>
  <files>.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md</files>

  <read_first>
    - .planning/ROADMAP.md (Phase 1 success criteria, all five — the consolidation is a judgment against these, not against the plan)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md (the exported names, flag semantics, and measured leak-token counts Phase 2 and Phase 3 bind to)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md (the fixture invariant result, the AC-14 baseline, and the deferred AC-14 empty-heading guard)
    - Makefile (the gate target, to confirm by reading that nothing was wired)
  </read_first>

  <action>
Run the final both-environments confirmation and assemble the baseline. Run every
command here directly — do not ask the developer to run anything.

First, `make gate` with no database reachable and no escalation flag. This is the
developer-without-Docker case the whole skip policy exists to protect. Stop the
compose database first, so the case is real rather than assumed.

Second, bring the compose database back up, export the DSN, and run `make gate`
again, still with no escalation flag. Both must exit 0, and that pair is the
phase's central claim: the mechanism exists and the gate is unmoved.

**Leave the compose database running.** That is this plan's declared end state and
an acceptance criterion below; do not stop it again as a tidy-up.

Then the ordering that cycle 1 left ambiguous. Run the clean-status check
**before** writing the summary: at that point `git status --porcelain` must print
exactly one line, the pre-existing untracked `.planning/config.json`. Only then
write the summary. After writing it, the expected status is two lines — that one
plus the untracked summary path — and it stays two until the summary is committed,
at which point it returns to one. Record which of those two states was observed
rather than asserting a clean tree that the plan's own artifact makes impossible.

Then assemble the summary. Collect from Tasks 1 and 2 every exit status, the skip
counts by both counting methods, and the verbatim escalated failure message for each
of the three conditions. Record the unescalated skip messages too, since ROADMAP
criterion 3 is about them. Record the phase-base and post-change leak-token counts
side by side, so a later reader can see the control had teeth rather than taking it
on trust. Phase 3 asserts against this text, so record it exactly rather than
paraphrasing.

Finally, write into the summary — for the developer to accept or amend at
end-of-phase review — the contracts Phase 2 and Phase 3 will bind to, since
changing any of them later is mechanical but no longer local to one package:

- The package path `internal/platform/testenv` and the exported function names.
- The flag name `EPISTEMIC_OS_TEST_REQUIRE_DB`, and that any non-empty value
  enables it, so the string zero enables it too. State the rationale: a typo in the
  value then errs toward enforcing rather than toward a vacuously green gate.
- **The flag's scope is wider than its name.** It escalates the cross-package
  fixture prerequisite, a filesystem condition, as well as database availability.
  A reader will reasonably assume it affects only database setup. Ask whether the
  name should widen in Phase 2 — `EPISTEMIC_OS_TEST_REQUIRE_ENV` was the reviewer's
  suggestion — or whether the doc comment is sufficient. Not decided here, because
  Phase 2's Makefile change and Phase 3's proof tests both bind to the literal.
- That the flag is documented in the package doc comment only, with README and
  Makefile documentation deferred to Phase 2, where the flag actually becomes part
  of the gate.
- **The deferred AC-14 empty-heading guard**, carried from 01-02: `acceptance_test.go`
  indexes the first heading without an emptiness guard, so a deliberately
  heading-free fixture would panic rather than skip. Not fixed in this phase because
  GATE-04's contract is that the file stays byte-identical. Ask whether it becomes a
  backlog item or a Phase 2 change.

Also carry forward the unresolved probe edge E1 as an open item awaiting
disposition, and record that E2, E3 and E4 were resolved into explicit criteria in
01-01 rather than dismissed — with the accounting, so the no-silent-drop rule is
auditable: 4 surfaced, 3 authored, 1 flagged. Do not dismiss E1; the planner did
not, and neither should the executor.

If either gate run exits non-zero, stop and report. The defect belongs to 01-01 or
01-02 and this plan re-runs after it is fixed.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; set -o pipefail &amp;&amp; docker compose stop postgres &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate &amp;&amp; make up &amp;&amp; env -u EPISTEMIC_OS_TEST_REQUIRE_DB EPISTEMIC_OS_DB_URL='postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable' make gate &amp;&amp; test -n "$(docker compose ps --services --filter status=running | grep -x postgres)" &amp;&amp; echo GATE_UNCHANGED_BOTH_WAYS</automated>
    <human-check>Review the recorded baseline and accept or amend the contracts Phase 2 and Phase 3 bind to: (1) the package path `internal/platform/testenv` and its exported function names; (2) the flag name `EPISTEMIC_OS_TEST_REQUIRE_DB` and its presence-based semantics, under which the string zero enables escalation because a typo in the value should err toward enforcing rather than toward a vacuously green gate; (3) the flag's scope being wider than its name — it also escalates the cross-package fixture prerequisite, a filesystem condition — and whether the name should widen in Phase 2 or the doc comment suffices; (4) documenting the flag in the package doc comment only, deferring README and Makefile documentation to Phase 2; (5) the deferred AC-14 empty-heading guard, which `acceptance_test.go` still lacks and which this phase could not add without breaking its own byte-identical guarantee. Then give a disposition for the one unresolved probe edge E1, which the probe returned with no category — whether it becomes a requirement or is dismissed as inapplicable to a test-harness refactor. E2, E3 and E4 were resolved into explicit criteria in 01-01 and need no disposition, only confirmation that the referents chosen for them are the right ones.</human-check>
  </verify>

  <acceptance_criteria>
    - With the compose database stopped, `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - With the database up and the DSN exported, `env -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - **Declared end state.** `docker compose ps --services --filter status=running` includes `postgres` when this task finishes. The database is left running deliberately; this is the plan's stated end state, not an oversight.
    - `git log --format=%H 030521b1ec7c12df868445bf8d162527202d42f1..HEAD -- Makefile .github/workflows/ci.yml` still prints nothing after all three plans have run.
    - `git diff --name-only 030521b1ec7c12df868445bf8d162527202d42f1..HEAD | grep -v '^internal/' | grep -v '^\.planning/'` still prints nothing.
    - **Status ordering, before the summary.** Run `git status --porcelain` before writing the summary: it prints exactly one line, `?? .planning/config.json`. Record that it was run at this point.
    - **Status ordering, after the summary.** After the summary is written and before it is committed, `git status --porcelain` prints exactly two lines: `?? .planning/config.json` and the untracked `01-03-SUMMARY.md` path. After it is committed, it prints one. Record which state was observed. Cycle 1 required a one-line status after creating the summary, which is unsatisfiable.
    - The summary records an exit status and a skip count for every scenario in Tasks 1 and 2, with the skip counts stated under both the `-v` and the filtered `-json` methods.
    - The summary contains the verbatim escalated failure text for all three conditions — unset variable, unreachable host, unreadable fixture — and the verbatim unescalated skip text for the unreachable-host and unreadable-fixture cases.
    - The summary records the leak-token counts at the phase base (`1` and `1`) beside the post-change counts (`0` and `0`), so the control's falsifiability is on the record rather than asserted.
    - The summary lists all five contract decisions and the unresolved probe edge E1 as items awaiting the developer's disposition, none pre-dismissed, together with the 4-surfaced/3-authored/1-flagged accounting for E1 through E4.
    - The summary records the confirmed phase base commit `030521b1ec7c12df868445bf8d162527202d42f1` and states that the cycle-1 base `fcebad1` was measured invalid, so a later reader does not re-adopt it.
  </acceptance_criteria>

  <done>
`make gate` is measured green in both environments with the compose database
genuinely stopped for the first and running for the second, the database is left
running as declared, the phase baseline is recorded in a form Phase 2 can diff
against and Phase 3 can assert against, and the five contract decisions plus the one
unresolved probe edge are queued for the developer's end-of-phase disposition rather
than settled on their behalf.
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
| T-01-09 | Information Disclosure | the DSNs constructed in Scenarios C and D | medium | mitigate | **Restated after cycle-1 review; severity corrected from `high` down, for the same reason as T-01-01.** Cycle 1's audit asserted that a password placed in the DSN did not appear in the output. Measured against pgx v5.7.2 on four DSN shapes, the library redacts the password itself, so that assertion passed at the phase base with zero code written and could not fail — an unfalsifiable control standing in for the phase's security claim. Scenario D is rebuilt on a token placed in the **database-name** position, which the library echoes verbatim: measured count `1` at the phase base on both DSN forms, and required to be `0` after the change, alongside a non-zero exit assertion, the fixed message text present, and the library's parse-error phrasing absent. The audit also carries its own negative control, proving the detector sees the token in a naive rendering. Impact at the pinned version is DSN-metadata disclosure rather than credential disclosure, which is `medium`; below `security_block_on: high`, so no longer phase-blocking. The DSNs used here carry throwaway values, never real credentials. |
| T-01-10 | Tampering | `testdata/demo.md` during the Task 2 move | high | mitigate | Moving a hash-pinned fixture risks leaving the tree corrupt if the run aborts, in the one file whose corruption invalidates all 22 offsets in `expected.json` and every span assertion in the segment package. Cycle 1 required the restore to run "regardless of exit status" but named no mechanism, which is a statement of intent, not a control. Mitigated by a concrete `trap … EXIT INT TERM` installed **before** the move and given verbatim as an acceptance criterion; by a SHA-256 captured before the move and compared after the restore, with both required to equal the constant pinned in `fixture_test.go`; by scoping the test run to the store package so the owning package is never compiled against the gap; and by two post-conditions — a `git status --porcelain` showing only the pre-existing untracked config, and a passing integrity test that re-checks the pinned hash and byte length. Remains `high` and phase-blocking. |
| T-01-11 | Elevation of Privilege | the local compose PostgreSQL instance | low | accept | Credentials are the published compose defaults on a loopback port, used only for tests. No production data is reachable. Out of scope at ASVS L1. |
| T-01-12 | Repudiation | the escalated-green measurement | medium | mitigate | A recorded "0 skips" that was never actually run against a database would make the phase's central claim unfalsifiable — the exact failure mode this milestone exists to remove. Mitigated by the task precondition, which halts rather than recording an unverified pass; and by the name-set containment criterion, which requires every test that skipped without a database to appear by name among the passing tests with one. Cycle 1's PASS-line count is retired: subtests inflate it and it names no test. |
| T-01-14 | Repudiation | the phase base commit recorded in the manifest | medium | mitigate | **New after cycle-1 review.** A mis-anchored base makes the non-enforcement audit report a violation that does not exist, or — worse in the other direction — a base chosen after a real change would hide one. Cycle 1 anchored at `fcebad1` and both audit criteria failed before any Phase 1 code existed, while the ancestry guard passed. Mitigated by re-anchoring to `030521b`, by verifying all four properties at planning time rather than asserting them, by running the same four as 01-01 Task 1's `<precondition>` so a wrong anchor halts at phase start, and by recording the corrected value in a re-frozen `01-PLAN-MANIFEST.json` carrying `supersedes: d90b10d`. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan installs nothing and writes no source. `go.mod` is unchanged across the whole phase. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
The phase is verified when all five ROADMAP success criteria are measured, not
argued. Every command runs under Git Bash.

1. One helper owns the decision — 01-01 Task 2 criteria: 38 call sites, 6 files,
   0 remaining local definitions.
2. Escalated, each of the three conditions names its cause — Scenarios B and C here
   for the variable and the host, Task 2 here for the fixture path, each with a
   non-zero exit status asserted independently of the message content.
3. Flag unset, skips exactly as today — Scenario A for the unset URL (exit 0, 38
   skips by two independent counting methods, shuffled and not), Scenario A2 for an
   unreachable database, and Task 2 for an unreadable fixture. All three branches,
   not one.
4. The fixture invariant holds and the AC-14 declines stay green and silent — 01-02
   Tasks 1 and 2, with PASS required for the pinned fixture and SKIP still legal for
   a genuinely preamble-free one.
5. `make gate` behaves exactly as before — Task 3 runs it with the compose database
   genuinely stopped and again with it up, and both must exit 0.

Plus the standing non-enforcement audit, anchored at `030521b`: no commit in this
phase touches the Makefile or the CI workflow, and no path outside `internal/` and
`.planning/` appears in the phase diff.

Plus the disclosure control: the connection string does not reach the output on the
parse path, proven by a token measured present at the phase base and required absent
after — the one criterion in this phase that is known to be able to fail.
</verification>

<success_criteria>
- The default run reproduces the phase base exactly: exit 0, 38 test-level skips, by two counting methods, shuffled and unshuffled.
- All three unescalated branches still skip: unset URL, unreachable database, unreadable fixture.
- The escalated run against a live database executes, by name, every test that skipped without one, and skips none.
- Each of the three environment conditions produces a non-zero exit and a failure naming that specific cause, with the fixture message recorded verbatim for Phase 3.
- No component of the connection string appears in the output on the parse path — a claim measured false at the phase base, so the criterion proving it can fail.
- The hash-pinned fixture is byte-identical before and after the move, restored under a trap installed before the move rather than by statement ordering.
- The Makefile and the CI workflow are untouched relative to a phase base that has itself been verified, and `make gate` is measured green with the database genuinely stopped and again with it up.
- The compose database is left running, as declared.
- The five contracts Phase 2 and Phase 3 bind to, and the one unresolved probe edge, are queued for the developer's end-of-phase disposition rather than settled on their behalf.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md` when done.

Record in it, as the baseline Phase 2 will be diffed against and Phase 3 will assert
against: the exit status and skip count for every scenario, with skip counts stated
under both the `-v` and the filtered `-json` methods; the verbatim escalated failure
message for each of the three conditions and the verbatim unescalated skip message
for the two that have one; the phase-base and post-change leak-token counts side by
side; the before-and-after SHA-256 of the fixture; the confirmed phase base commit
`030521b` together with the note that `fcebad1` was measured invalid; the two
observed `git status --porcelain` states and the point in the sequence each was
taken; the five contract decisions awaiting the developer's acceptance or amendment;
and the unresolved probe edge E1 with the 4-surfaced/3-authored/1-flagged accounting.

The sign-off block is harvested from Task 3's `<verify><human-check>` into the phase
UAT at end-of-phase review, so it reaches the developer in one batch rather than
halting execution mid-flight.
</output>


## Review Instructions

**Verify against source — do not review the plan text in isolation.** The plans reference real files, migrations, routes, and tests in this repo (repo root is the current working directory).
1. Open the referenced files and check each claim against the actual code.
2. For every strength or concern, cite concrete `path/to/file:line` evidence plus the mechanism.
3. When a plan asserts a mechanism works (a guard, a query filter, a test that exercises a path), trace whether it actually does what is claimed — do not take the plan's word for it.
4. If you cannot read the repo (no file access), say so and downgrade that finding to an open question rather than asserting it.

Findings citing `file:line` evidence are weighted far more heavily than impressionistic ones; a review that only restates the plan's own claims has low value.

### IMPORTANT — this is CYCLE 2 of a plan-review-convergence loop

Cycle 1 of review raised 4 HIGH concerns and 14 actionable non-HIGH findings against an EARLIER version of these plans. The plans were then rewritten to incorporate that feedback (commits 09a88c9, dd69e0e, d61eac2) and re-frozen at a new phase base commit `030521b`.

**You are reviewing the CURRENT plan set.** Report what remains UNRESOLVED NOW. Do not re-report cycle-1 findings that the replan already addressed. For each concern you raise, state explicitly whether it is:
- NEWLY RAISED in this cycle, or
- PARTIALLY RESOLVED (acknowledged in the plan, mitigation described but not verifiable/complete), or
- STILL UNRESOLVED from a prior cycle.

For every MEDIUM/LOW concern, state whether it is ACTIONABLE — i.e. whether it would be invisible to `/gsd-execute-phase` unless incorporated into a PLAN.md task, action, acceptance_criteria, verify command, must_haves item, threat model, artifact list, or an explicit deferral/rejection rationale. If the concern is ALREADY covered by some element of the current PLAN.md files, say so and mark it NOT ACTIONABLE, citing the plan line that covers it.

Analyze each plan and provide:

1. **Summary** — One-paragraph assessment
2. **Strengths** — What's well-designed (bullet points)
3. **Concerns** — Potential issues, gaps, risks (bullet points with severity: HIGH/MEDIUM/LOW, and the resolution status label above)
4. **Suggestions** — Specific improvements (bullet points)
5. **Risk Assessment** — Overall risk level (LOW/MEDIUM/HIGH) with justification

Focus on:
- Missing edge cases or error handling
- Dependency ordering issues
- Scope creep or over-engineering
- Security considerations
- Performance implications
- Whether the plans actually achieve the phase goals

Output your review in markdown format.
