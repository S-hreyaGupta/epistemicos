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
- [ ] 01-01-PLAN.md — Shared escalation helper: one package owns the skip-or-fail decision for all three environment conditions, and all 38 call sites across 6 test files reach it
- [ ] 01-02-PLAN.md — Fixture invariant: TestFixtureIntegrity proves demo.md has a non-whitespace preamble, and the AC-14 content skips stay untouched, green and silent
- [ ] 01-03-PLAN.md — Non-enforcement audit: escalated run reaches 0 skips against a live database, each condition names its cause, and `make gate` is measured unchanged


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
  tokens: 55000
  raw_tokens: 55000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB unset and EPISTEMIC_OS_DB_URL unset, `go test ./... -count=1` exits 0 and reports exactly 38 skipped tests — the measured count at HEAD"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL unset, the store and approved packages fail, and the failure text names EPISTEMIC_OS_DB_URL"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and EPISTEMIC_OS_DB_URL addressing a closed port, the failure text names that host and port"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and the cross-package fixture unreadable, the failing test names the fixture path it could not read"
    - "No test file in the store or approved packages holds its own skip-or-fail decision for the database — all 38 former call sites reach one helper"
    - "No message the helper emits contains the password component of EPISTEMIC_OS_DB_URL, on any of its three failure paths"
  artifacts:
    - internal/platform/testenv/testenv.go
    - internal/platform/testenv/testenv_test.go
  key_links:
    - "All 38 former call sites resolve to the shared helper — one missed file leaves a second decision site and silently defeats success criterion 1"
    - "Required() is the only reader of EPISTEMIC_OS_TEST_REQUIRE_DB; Phase 2's Makefile change and Phase 3's proof tests bind to this exact name"
    - "hostFromURL is the only source of host text in failure messages — it is what keeps the raw DSN out of CI logs"
  prohibitions:
    - "The escalation flag must not default to on. With EPISTEMIC_OS_TEST_REQUIRE_DB unset, every test that skips at HEAD must still skip and the suite must still exit 0 — a mechanism that enforces on arrival is Phase 2's change smuggled into Phase 1."
    - "This phase must not wire enforcement. No change to the Makefile and no change to the CI workflow, even though both are one line away from turning the mechanism on."
---

<objective>
Replace the two duplicated `testPool` helpers in the `store` and `approved` test
packages with a single shared helper that owns every skip-or-fail decision for
the database-backed tests, and give that helper an opt-in escalation flag that
converts each environment skip into a failure naming its specific cause.

Purpose: today the decision to skip lives in two near-identical copies, and
neither can be escalated without editing both. GATE-01 through GATE-03 in Phase 2
and the proof tests in Phase 3 all bind to this helper, so it has to exist and be
the only decision site before either of those phases can be written.

Output: a new `internal/platform/testenv` package, its unit test, and six test
files converted to call it.

**The escalation is built here and turned on in Phase 2.** After this plan,
`make gate` must behave exactly as it does at HEAD. Nothing in this plan sets
`EPISTEMIC_OS_TEST_REQUIRE_DB` anywhere it would be read by a default run.

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
</objective>

## Artifacts this phase produces

New symbols introduced by this plan. Nothing below exists at HEAD; treat every
entry as created here rather than as drift against the existing codebase.

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
| Environment variable | `EPISTEMIC_OS_TEST_REQUIRE_DB` (new) |

Pre-existing, not produced here: `EPISTEMIC_OS_DB_URL`, `pgxpool`, the six test
files, `make gate`.

## Flagged assumptions — spec-less edge probe

No SPEC exists for this phase, so the deterministic edge probe ran over GATE-04
and GATE-05 and returned 4 applicable edges, **0 resolved**. Per the no-silent-drop
rule, all 4 are carried here as explicit flagged assumptions: 4 surfaced == 0
authored into `must_haves.truths` + 4 flagged.

| # | Requirement | Category | Probe | Status |
|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (uncategorized — review manually) | **unresolved — flagged** |
| E2 | GATE-05 | adjacency | When two things are exactly equal or just touch, do they merge, collide, or separate? | **unresolved — flagged** |
| E3 | GATE-05 | empty | What is the result for empty, single-element, or null input? | **unresolved — flagged** |
| E4 | GATE-05 | ordering | When elements compare equal, is output order specified and stable? | **unresolved — flagged** |

**Honest note on applicability.** These four are generic data-structure edges.
GATE-04 and GATE-05 describe a test harness's skip-or-fail decision, not a
collection with adjacency, emptiness or sort order, so the categories map poorly
onto this phase. That is a reason to flag them for a human to dismiss, not a
reason for the planner to dismiss them silently.

Two observations a reviewer may find useful, offered as context and **not** as
resolutions — none of these rows is resolved:

- E3 (empty) has a plausible landing site: `EPISTEMIC_OS_TEST_REQUIRE_DB` set to
  the empty string, and `hostFromURL` returning an empty host for a
  keyword/value DSN. Both are handled in Task 1 and pinned by unit tests. Whether
  that is what the probe meant is a judgment call left to the reviewer.
- E2 and E4 have no evident referent in this phase.

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

Measured in this repository before planning. Do not re-derive; do not assume
anything beyond these.

- `go test ./... -count=1` at HEAD exits 0 with **38 skipped tests** and no
  database present. Call sites per file: `authorreturn_test.go` 9,
  `runrejection_test.go` 7, `researchunit_test.go` 6,
  `segmentation_decision_test.go` 6, `segmentation_test.go` 5,
  `papers_test.go` 5.
- `pgxpool.New` is lazy. With `postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable`
  it returns a nil error; the failure surfaces at `Ping`.
- The `Ping` error names the host and omits the password. Observed:
  ``failed to connect to `user=probeuser database=nodb`: 127.0.0.1:1 (127.0.0.1): dial error: ...``
- **`pgxpool.New`'s parse error echoes the connection string verbatim.**
  Observed for a malformed DSN: ``cannot parse `://not a url`: failed to parse
  as keyword/value``. Today's code passes that error to `t.Fatalf`, so a
  malformed DSN carrying a password would publish it. See T-01-01.
- A non-test Go package that imports `testing` builds, vets and formats clean,
  and `t.Skip` called from it correctly skips the calling test. Verified with a
  probe module on Go 1.24.
- `go.mod` requires `golang-migrate/v4`, `google/uuid`, `pgx/v5`, `godotenv`,
  `goldmark`. **There is no testify dependency**, contrary to PROJECT.md's
  Constraints line. Use stdlib `testing` only; adding a dependency is out of
  scope for this plan.
- Local DSN for the compose service:
  `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`

<tasks>

<task type="tracer">
  <name>Task 1: End-to-end escalation for the database path — store package only</name>
  <files>internal/platform/testenv/testenv.go, internal/platform/testenv/testenv_test.go, internal/adapters/secondary/store/segmentation_test.go</files>

  <read_first>
    - internal/adapters/secondary/store/segmentation_test.go (lines 1-46 — the helper being replaced, its doc comment, and the import block)
    - internal/adapters/secondary/approved/papers_test.go (lines 1-46 — the second copy; its message wording differs and both are being unified)
    - internal/platform/security (any file — for the house style of a platform package: doc comments that explain why, not what)
    - go.mod (confirm pgx/v5 is a direct requirement and no assertion library exists)
  </read_first>

  <reversibility rating="costly">
    Phase 2's Makefile change and Phase 3's proof tests bind to the package path,
    the two exported function names, and the literal `EPISTEMIC_OS_TEST_REQUIRE_DB`.
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
errs toward enforcing rather than toward a vacuous pass.

Declare `URLEnv` as the string `EPISTEMIC_OS_DB_URL` and `RequireEnv` as the
string `EPISTEMIC_OS_TEST_REQUIRE_DB`.

Add `Required() bool`, returning true when the value of `RequireEnv` is non-empty.

Add unexported `hostFromURL(raw string) string`. Parse with `net/url.Parse` and
return the `Host` field. Return the empty string on a parse error, and also for a
keyword/value DSN such as one beginning `host=`, which parses without producing a
host. This function is the only thing permitted to derive display text from the
connection string, and it must never return anything drawn from the userinfo
component.

Add `Pool(t *testing.T) *pgxpool.Pool`, calling `t.Helper()` first, then deciding
in this order:

1. Read `URLEnv`. When it is empty and `Required()` is true, `t.Fatalf` with a
   message naming both `EPISTEMIC_OS_DB_URL` and `EPISTEMIC_OS_TEST_REQUIRE_DB`
   and stating that escalation is on so the test cannot be skipped. When it is
   empty and `Required()` is false, `t.Skip` with a message naming
   `EPISTEMIC_OS_DB_URL` and telling the developer to start postgres and export
   it — preserving today's behavior.
2. Build a context with a five second timeout, matching the existing helpers, and
   call `pgxpool.New`. On error, `t.Fatalf` in both modes — matching today's
   classification, where a malformed URL already fails rather than skips. The
   message names `EPISTEMIC_OS_DB_URL` and states that its value could not be
   parsed as a connection string. It must not interpolate the variable's value
   and must not interpolate the returned error: that error embeds the connection
   string verbatim, so echoing it publishes any password in it to the CI log.
   Record that reason in a comment on this branch.
3. Call `Ping`. On error, close the pool, then take `hostFromURL` of the URL and
   substitute a fixed placeholder naming the variable when it comes back empty.
   When `Required()` is true, `t.Fatalf` naming that host and appending the Ping
   error. Otherwise `t.Skipf` with the same text. The Ping error is verified to
   omit the password and is kept for diagnosis; the connection string still is
   not interpolated.
4. Register `t.Cleanup` to close the pool and return it.

Note in a comment that the two packages' skip messages differ at HEAD, so unifying
them is unavoidable when the duplication is removed; what is preserved is the
skip-or-fail classification of every site, not the message bytes.

Then wire one path end to end. In `segmentation_test.go`, keep the existing local
helper's name and signature — it takes a `*testing.T` and returns a
`*pgxpool.Pool` — but replace its body with a call to the new shared helper, and
delete the doc comment above it that describes the skip policy, since that policy
now lives in one place. Add the import. Remove any import the file no longer uses;
let `go build ./...` name them. This routes all 33 store call sites through the
shared helper in one move, which is the thinnest slice that proves the mechanism
against real tests. Task 2 removes the local wrapper entirely.

Write `internal/platform/testenv/testenv_test.go` in package `testenv` covering
the two pure pieces only. For `hostFromURL`: a full DSN with userinfo, port and
query returns host and port; a DSN pointing at a closed port returns that host
and port; a keyword/value DSN returns empty; the empty string returns empty; a
malformed string returns empty; and for a DSN carrying a password, the returned
value does not contain that password. For `Required`, drive the variable with
`t.Setenv`: unset is false, empty is false, the string one is true, and the string
zero is true — the last case pins the presence-based rule deliberately.

Do not test `Pool`'s skip-or-fail decision here. Asserting that a helper skips or
fails requires driving a `testing.T` from outside, which is the gate proof, and
that belongs to Phase 3.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; go test ./internal/platform/testenv/... -count=1 &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 &amp;&amp; env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1 2>&amp;1 | grep -q 'EPISTEMIC_OS_DB_URL' &amp;&amp; echo TRACER_OK</automated>
  </verify>

  <acceptance_criteria>
    - `go build ./...`, `go vet ./...` all succeed and `gofmt -l .` prints nothing.
    - `go test ./internal/platform/testenv/... -count=1` passes and the package no longer reports no test files.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` exits 0.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `38`, matching the measured HEAD baseline.
    - `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1` exits non-zero and its combined output contains `EPISTEMIC_OS_DB_URL`.
    - `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:PWLEAKCANARY@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1 2>&1` exits non-zero, contains `127.0.0.1:1`, and `grep -c PWLEAKCANARY` over that output prints `0`.
    - `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:PWLEAKCANARY@ host with spaces/db' go test ./internal/adapters/secondary/store/... -count=1 2>&1 | grep -c PWLEAKCANARY` prints `0`.
    - `git diff --name-only` lists no path outside `internal/`.
  </acceptance_criteria>

  <done>
The shared helper exists, its pure parts are unit-tested, and the store package
reaches it through one delegate. Escalation off reproduces the HEAD baseline
exactly at 38 skips; escalation on converts the unset-URL and unreachable-host
conditions into failures that name their cause and leak no credential.
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
Remove the package-local pool helper from both packages so exactly one skip-or-fail
decision remains in the repository.

In `segmentation_test.go`, delete the delegate Task 1 left in place. In
`papers_test.go`, delete the second copy — the definition at lines 24-46 as of HEAD
together with its doc comment at lines 19-23, which describes a policy that now
lives in the shared package.

In all six files, replace every call of the deleted local helper with a call to
the shared package's pool function, passing the same `t`. The expected counts,
measured at HEAD, are 9 in `authorreturn_test.go`, 7 in `runrejection_test.go`,
6 in `researchunit_test.go`, 6 in `segmentation_decision_test.go`, 5 in
`segmentation_test.go` and 5 in `papers_test.go` — 38 in total. Confirm each file's
count after editing rather than trusting a single pass.

Add the import of `github.com/EpistemicOS/epistemicos/internal/platform/testenv`
to each of the six files, in the project-local import group that already holds the
other `github.com/EpistemicOS/epistemicos` paths.

Delete imports that the edits make unused. Measured at HEAD, the `os` package is
referenced only at line 26 of `segmentation_test.go` and line 27 of
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
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 &amp;&amp; echo DEDUP_OK</automated>
  </verify>

  <acceptance_criteria>
    - `grep -v '^\s*//' internal/adapters/secondary/store/segmentation_test.go | grep -c 'testPool'` prints `0`.
    - `grep -v '^\s*//' internal/adapters/secondary/approved/papers_test.go | grep -c 'testPool'` prints `0`.
    - `grep -rn 'testenv.Pool(t)' --include=*_test.go internal | wc -l` prints `38`.
    - `grep -rlc 'testenv.Pool(t)' --include=*_test.go internal | wc -l` prints `6` — every one of the six files was converted.
    - `go build ./...`, `go vet ./...` succeed and `gofmt -l .` prints nothing.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` exits 0 and `-v` output still yields `38` lines matching `^--- SKIP`.
    - `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/approved/... -count=1` exits non-zero and its output contains `EPISTEMIC_OS_DB_URL` — proving the approved package now escalates too, which it could not before.
  </acceptance_criteria>

  <done>
Neither package defines a pool helper. All 38 call sites name the shared package
directly, the suite is unchanged with escalation off, and the approved package
escalates identically to the store package.
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
today's behavior. On success return the bytes. Give it a doc comment saying this is
for fixtures read across package boundaries, where a relative path is a real
environment risk, and pointing at the in-package `loadFixture` in the segment domain
as the stricter idiom for a fixture the package owns.

In `segmentation_test.go`, replace the read of
`../../../core/domain/segment/testdata/demo.md` inside
`TestSaveRun_FixtureRoundTripsAllOffsets` — the read at line 276 and the skip at
line 278 as of HEAD — with a single call to the new function, keeping the same
relative path. Remove the `os` import if nothing else in the file uses it.

Add unit coverage for the non-escalated success path only: reading a file that
exists returns its exact bytes. As in Task 1, do not attempt to assert the skip or
fail branches from inside a test — that is Phase 3's job.

Do not change the in-package `loadFixture` in the segment domain. It already hard
fails on a read error, which is the correct behavior and needs no escalation flag.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; go test ./internal/platform/testenv/... -count=1 &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 &amp;&amp; echo FIXTURE_ROUTE_OK</automated>
  </verify>

  <acceptance_criteria>
    - `grep -c 'testenv.Fixture(t' internal/adapters/secondary/store/segmentation_test.go` prints `1`.
    - `grep -v '^\s*//' internal/adapters/secondary/store/segmentation_test.go | grep -c 'os.ReadFile'` prints `0`.
    - `go build ./...`, `go vet ./...` succeed and `gofmt -l .` prints nothing.
    - `go test ./internal/platform/testenv/... -count=1 -v 2>&1 | grep -c '^--- FAIL'` prints `0`.
    - `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` exits 0 with `38` lines matching `^--- SKIP` under `-v`.
    - `git diff --name-only` lists no path outside `internal/`.
  </acceptance_criteria>

  <done>
All three environment conditions GATE-05 names — unset URL, unreachable database,
unreadable fixture — are decided in one package, and the store package's
cross-package fixture read goes through it.
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
| T-01-01 | Information Disclosure | `testenv.Pool`, the `pgxpool.New` error branch | high | mitigate | Verified in this repository: `pgxpool.New` echoes the connection string verbatim on a parse failure, and the existing helpers pass that error straight to `t.Fatalf`. Task 1 forbids interpolating either the variable's value or that error; the branch emits a fixed message naming only `EPISTEMIC_OS_DB_URL`. Enforced by the canary criteria in Tasks 1 and by the plan 01-03 audit. Severity high meets `security_block_on: high`, so this is blocking. |
| T-01-02 | Information Disclosure | `testenv.Pool`, the `Ping` error branch | medium | mitigate | Host text is derived only through `hostFromURL`, which returns `net/url`'s Host and therefore never the userinfo component. The `Ping` error is verified to render as `user=… database=…` with no password and is retained for diagnosis. Pinned by a `hostFromURL` unit test asserting a DSN password is absent from the return value. |
| T-01-03 | Tampering | `EPISTEMIC_OS_TEST_REQUIRE_DB` | low | accept | Anyone able to set environment variables in the test process already controls the build. The flag can only weaken behavior toward today's skip, never toward a false pass that today would fail. Out of scope at ASVS L1. |
| T-01-04 | Denial of Service | the five second connect timeout in `testenv.Pool` | low | accept | Carried forward unchanged from both existing helpers. A hung database bounds each call at five seconds rather than hanging the suite. |
| T-01-05 | Tampering | the `path` parameter of `testenv.Fixture` | low | accept | Every argument is a compile-time string literal in a test file. No external or user-controlled input reaches this parameter, so path traversal has no source. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan adds no dependency. `go.mod` is unchanged; `testing`, `os`, `net/url`, `context` and `time` are stdlib and `pgx/v5` is already a direct requirement. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
Run from the repository root with no database present. Every check here is
database-free by design; the database-dependent half of the phase is verified in
plan 01-03.

1. `go build ./... && go vet ./... && gofmt -l .` — builds, vets, prints no files.
2. `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1` — exits 0.
3. The same command with `-v`, counting lines matching `^--- SKIP`, prints 38.
4. `grep -rn 'testenv.Pool(t)' --include=*_test.go internal | wc -l` prints 38.
5. Escalated with no URL: the store and approved packages fail, output names `EPISTEMIC_OS_DB_URL`.
6. Escalated with a closed port: failure output names the host and port.
7. Credential canary: neither the closed-port DSN nor a malformed DSN puts the password in the output.
8. `git diff --name-only` lists nothing outside `internal/` — the Makefile and the CI workflow are untouched.
</verification>

<success_criteria>
- One package owns the skip-or-fail decision for all three environment conditions, and neither test package defines its own.
- All 38 former call sites reach it; the six-file conversion is complete.
- With the escalation flag unset, the suite is byte-for-byte equivalent in outcome to HEAD: exit 0, 38 skips.
- With the flag set, each of the three conditions produces a failure naming that specific cause.
- No failure path emits the password component of the connection string.
- Nothing outside `internal/` changed — the mechanism exists and enforces nothing.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md` when done.

Record in it: the final exported signatures, the exact skip count observed with
escalation off, the observed failure text for each of the three escalated
conditions (with the password redacted), and confirmation that `git diff --name-only`
listed nothing outside `internal/`. Phase 2 will read those signatures and Phase 3
will assert against that failure text.
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
  tokens: 24000
  raw_tokens: 24000
  tasks: 2
  confidence: low

must_haves:
  truths:
    - "TestFixtureIntegrity fails, naming testdata/demo.md, if the pinned fixture ever stops beginning with pre-heading content"
    - "TestFixtureIntegrity fails, naming testdata/demo.md, if that pre-heading content is ever whitespace only"
    - "TestAC14_PreHeadingContentHasNoNode reports PASS, not SKIP — its two content-conditional skips remain in the file and remain unreachable for the pinned fixture"
    - "`go test ./internal/core/domain/segment/... -count=1` passes with no database present, exactly as at HEAD"
  artifacts:
    - internal/core/domain/segment/fixture_test.go
  key_links:
    - "The preamble assertion lives in the same test that already pins demo.md by SHA-256 and byte length, so the property is decidable from bytes that cannot change without that test failing first"
    - "acceptance_test.go lines 438 and 451 stay untouched — the invariant makes them unreachable rather than making them illegal, which is what keeps a genuinely preamble-free fixture legitimate signal instead of a gate failure"
  prohibitions:
    - "The two content-conditional skips in the segment acceptance test must not be deleted, converted into failures, or made conditional on the escalation flag. They are unreachable for the pinned fixture, not wrong — a fixture that genuinely lacks a preamble is real signal, and turning that into a gate failure is the exact conflation this milestone exists to prevent."
    - "The fixture's pinned SHA-256 and byte-length constants must not be edited, and testdata/demo.md must not be regenerated, to make the new assertion pass. If the assertion fails, the fixture is wrong, not the assertion."
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

Output: a strengthened `TestFixtureIntegrity`. No new files, no new symbols, and
no change to `acceptance_test.go`.

**This plan enforces nothing.** It adds assertions to a test that already runs and
already passes. `make gate` behavior is unchanged.
</objective>

## Artifacts this phase produces

This plan introduces **no new symbols**. It modifies one existing test function in
place.

| Kind | Name | Status |
|---|---|---|
| Test function | `TestFixtureIntegrity` | pre-existing at `internal/core/domain/segment/fixture_test.go:128` — extended here, not created |
| Const | `fixtureSHA256`, `fixtureBytes` | pre-existing — read, never edited |
| Func | `loadFixture`, `detectHeadings` | pre-existing — called, never changed |
| Import | `strings` | added to an existing import block |

The new symbols this phase creates all belong to plan 01-01: the
`internal/platform/testenv` package, its exported `URLEnv`, `RequireEnv`,
`Required`, `Pool` and `Fixture`, and the `EPISTEMIC_OS_TEST_REQUIRE_DB`
environment variable. See that plan's artifacts table.

## Flagged assumption — spec-less edge probe

The deterministic edge probe returned 4 applicable edges across GATE-04 and
GATE-05, **0 resolved**. The full table and the no-silent-drop accounting
(4 surfaced == 0 authored into truths + 4 flagged) live in `01-01-PLAN.md`. The
row belonging to this plan's requirement is repeated here so it is visible where
it applies:

| # | Requirement | Category | Probe | Status |
|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (uncategorized — review manually) | **unresolved — flagged** |

E1 came back with no category at all, so there is no probe question to answer. It
is carried as an open item for human review rather than dismissed. Note honestly
that the probe's categories are generic data-structure edges and GATE-04 is a
statement about which skips are legitimate signal, so a poor fit is expected —
that is a reason to flag, not to drop.

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

Measured in this repository before planning.

- `go test ./internal/core/domain/segment/... -run 'TestAC14_PreHeadingContentHasNoNode|TestFixtureIntegrity' -v` reports
  **PASS for both**. The AC-14 test does not skip today, which means the fixture's
  first heading is not at byte 0 and the preamble is not whitespace only. The
  invariant this plan adds is therefore already true and must pass on first run —
  if it fails, something else is wrong and the fixture is the suspect.
- `fixture_test.go` pins `demo.md` at SHA-256
  `a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e` and
  `fixtureBytes = 81492`, and `loadFixture` hard-fails on a read error. That is the
  house idiom this plan follows.
- `TestDetectHeadings_Fixture` asserts the fixture contains 22 headings, so a
  non-empty result from `detectHeadings` is established elsewhere — but this test
  must not depend on that, since Go guarantees no ordering between tests.
- `fixture_test.go` imports `crypto/sha256`, `encoding/hex`, `encoding/json`, `os`,
  `path/filepath`, `testing`. `strings` is not yet imported.
- The whole segment domain package runs without a database, so every check in this
  plan is database-free.

<tasks>

<task type="auto">
  <name>Task 1: Assert the preamble as a fixture invariant</name>
  <files>internal/core/domain/segment/fixture_test.go</files>

  <read_first>
    - internal/core/domain/segment/fixture_test.go (whole file — the pinning constants, loadFixture, and TestFixtureIntegrity's existing carriage-return scan, whose message style the new failures must match)
    - internal/core/domain/segment/acceptance_test.go (lines 424-458 — the AC-14 test, to see exactly which two conditions are being lifted and to confirm neither is being altered)
  </read_first>

  <reversibility rating="reversible">
    Three assertions added to an existing test. Reverting restores HEAD exactly.
  </reversibility>

  <action>
Extend `TestFixtureIntegrity`, after the existing carriage-return scan, with the
preamble invariant.

Call `detectHeadings` on the bytes `loadFixture` returned. Fail with `t.Fatalf`
when it returns an empty slice, stating that the pinned fixture contains no
headings at all, so no offset in `expected.json` can mean anything. Do not rely on
`TestDetectHeadings_Fixture` having run first — Go gives no ordering guarantee
across tests, and this test exists precisely to be the one that fails first.

Take the `ByteStart` of the first heading. Fail with `t.Fatalf` when it is zero,
stating that the fixture must begin with pre-heading content, because the AC-14
criterion about pre-heading content producing no node is only exercised when such
content exists.

Take the bytes before that offset, and fail with `t.Fatalf` when
`strings.TrimSpace` of them is empty, stating that the preamble must contain
non-whitespace text for the same reason.

Both messages must name `testdata/demo.md`, must report the offset that was found,
and must say that the constants at the top of this file pin the fixture's exact
bytes — so a failure here means the fixture was replaced or regenerated, not that
the assertion drifted. Name those two constants in the message so the reader knows
where to look.

Add `strings` to the import block, in stdlib order.

Write a comment above the new block explaining the division of responsibility this
change establishes: the property is asserted here, where the fixture is already
pinned by hash and length and the answer is therefore decidable from bytes that
cannot change without a louder failure firing first; and it is deliberately NOT
asserted in the acceptance test, where the same question has to be answered per run
and a fixture that legitimately lacked a preamble would have to decline rather than
fail. State that this is what keeps the acceptance test's two content-conditional
declines green and silent instead of turning them into a gate failure class.

Change nothing else in the file. Do not touch `loadFixture`, do not touch the two
pinning constants, and do not open the acceptance test for editing.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; go build ./... &amp;&amp; go vet ./... &amp;&amp; test -z "$(gofmt -l .)" &amp;&amp; go test ./internal/core/domain/segment/... -count=1</automated>
  </verify>

  <acceptance_criteria>
    - `go build ./...`, `go vet ./...` succeed and `gofmt -l .` prints nothing.
    - `go test ./internal/core/domain/segment/... -count=1` exits 0.
    - `go test ./internal/core/domain/segment/... -count=1 -run TestFixtureIntegrity -v 2>&1 | grep -c '^--- PASS: TestFixtureIntegrity'` prints `1`.
    - `grep -c 'strings' internal/core/domain/segment/fixture_test.go` is at least `2` — the import plus at least one use.
    - `grep -c 'detectHeadings' internal/core/domain/segment/fixture_test.go` increases by at least 1 relative to HEAD (`git show HEAD:internal/core/domain/segment/fixture_test.go | grep -c detectHeadings`).
    - Negative proof that the assertion has teeth: temporarily edit a working copy so the first-heading offset compared against is a value the fixture cannot satisfy, run `go test ./internal/core/domain/segment/... -run TestFixtureIntegrity -count=1`, confirm it exits non-zero with output containing `demo.md`, then discard the edit and confirm `git diff --stat internal/core/domain/segment/fixture_test.go` shows only the intended addition.
    - `git diff --name-only` lists exactly `internal/core/domain/segment/fixture_test.go` and nothing else.
  </acceptance_criteria>

  <done>
`TestFixtureIntegrity` proves the pinned fixture has a non-whitespace preamble, and
fails with a message naming `demo.md` if that ever stops being true. The segment
package still passes with no database present.
  </done>
</task>

<task type="auto">
  <name>Task 2: Prove the AC-14 content skips are untouched, green and silent</name>
  <files>internal/core/domain/segment/acceptance_test.go (read-only — must remain byte-identical to HEAD)</files>

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
one guarding a first-heading offset of zero, one guarding a whitespace-only
preamble. Confirm the assertions between and after them are unchanged.

Confirm the file is byte-identical to HEAD by diffing it against the committed
version. It must appear in no diff produced by this plan.

Run the segment package and confirm the AC-14 test reports PASS, not SKIP. PASS is
the requirement: it means the declines did not fire, so the test's real assertions
about node spans actually ran. A SKIP here would mean the fixture lost its preamble,
which Task 1's invariant should have caught first — if both happen, Task 1's
assertion is not wired to the same bytes and must be fixed before this plan closes.

Record the observed result line in the summary, so Phase 2 and Phase 3 inherit a
stated baseline rather than an assumption.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; git diff --quiet HEAD -- internal/core/domain/segment/acceptance_test.go &amp;&amp; go test ./internal/core/domain/segment/... -count=1 -run TestAC14_PreHeadingContentHasNoNode -v 2>&amp;1 | grep -q '^--- PASS: TestAC14_PreHeadingContentHasNoNode' &amp;&amp; echo AC14_INTACT</automated>
  </verify>

  <acceptance_criteria>
    - `git diff --name-only HEAD -- internal/core/domain/segment/acceptance_test.go` prints nothing — the file is untouched.
    - `grep -c 't.Skip' internal/core/domain/segment/acceptance_test.go` prints the same number as `git show HEAD:internal/core/domain/segment/acceptance_test.go | grep -c 't.Skip'`.
    - `go test ./internal/core/domain/segment/... -count=1 -run TestAC14_PreHeadingContentHasNoNode -v 2>&1 | grep -c '^--- PASS: TestAC14_PreHeadingContentHasNoNode'` prints `1`.
    - The same command filtered for `^--- SKIP` prints `0`.
    - `go test ./internal/core/domain/segment/... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `0` — the whole segment package skips nothing, matching HEAD.
  </acceptance_criteria>

  <done>
Both content-conditional declines survive in the acceptance test, unmodified, and
the AC-14 test passes with its real assertions executing rather than declining.
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
| T-01-06 | Tampering | `testdata/demo.md` and the two pinning constants in `fixture_test.go` | medium | mitigate | A fixture edit, or a constant edit to accommodate one, would silently invalidate every byte offset in `expected.json` and could be used to make an assertion pass vacuously. Mitigated by the existing SHA-256 and byte-length pins, which fail before any offset assertion runs, and by the plan prohibition forbidding edits to either. Task 1 acceptance requires `git diff --name-only` to list only `fixture_test.go`. |
| T-01-07 | Repudiation | the AC-14 content-conditional declines | medium | mitigate | Deleting the two declines would remove the record that a preamble-free fixture is a legitimate outcome rather than a failure, making a future maintainer unable to tell signal from breakage. Mitigated by Task 2, which asserts the file is byte-identical to HEAD. |
| T-01-08 | Tampering | line-ending conversion on checkout | low | accept | Already mitigated at HEAD by `.gitattributes` marking the fixture `-text` and by the carriage-return scan in `TestFixtureIntegrity`. This plan changes neither and adds no new exposure. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan adds no dependency. `strings` is stdlib; `go.mod` is unchanged. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
Run from the repository root. No database is needed for any check in this plan.

1. `go build ./... && go vet ./... && gofmt -l .` — builds, vets, prints no files.
2. `go test ./internal/core/domain/segment/... -count=1` — exits 0.
3. The same with `-v`, counting `^--- SKIP` lines, prints 0.
4. The AC-14 test reports PASS, not SKIP.
5. `git diff --name-only HEAD -- internal/core/domain/segment/acceptance_test.go` prints nothing.
6. The negative proof in Task 1 confirmed the new assertion fails when the property is violated, and the working tree was restored afterward.
7. `git diff --name-only` for this plan lists exactly one file.
</verification>

<success_criteria>
- The preamble property is asserted where the fixture is already hash-pinned, so it is decidable rather than re-derived.
- A future fixture that loses its preamble fails one test with a message naming the file, instead of silently downgrading AC-14 to a skip.
- The two content-conditional declines survive untouched — GATE-04's "green and silent" holds literally.
- The segment package skips nothing and passes, exactly as at HEAD.
- Exactly one file changed, and it is not the acceptance test, the Makefile, or the CI workflow.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md` when done.

Record in it: the observed result lines for `TestFixtureIntegrity` and the AC-14
test, the outcome of the negative proof in Task 1 acceptance including the failure
message text, and confirmation that the acceptance test is byte-identical to HEAD.
</output>

#### gsd-review-plan-02.md

---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 03
type: execute
wave: 2
depends_on: ["01-01", "01-02"]
files_modified: []
autonomous: true
requirements: [GATE-04, GATE-05]

estimate:
  tokens: 36000
  raw_tokens: 36000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "`make gate` exits 0 with no database present, exactly as at the phase base commit — the mechanism built in 01-01 enforces nothing"
    - "`make gate` exits 0 with a reachable database and migrations applied"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set and a reachable database, the store and approved packages report 0 skipped tests and 0 failures"
    - "With EPISTEMIC_OS_TEST_REQUIRE_DB set, each of the three environment conditions produces a failure naming that specific cause: the variable, the host, the fixture path"
    - "No commit in this phase touches the Makefile or the CI workflow"
    - "The password component of a connection string appears in no output on any escalated failure path"
  artifacts:
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md
  key_links:
    - "The escalated-green run is the only check that proves the helper does not fail spuriously when the database IS present — without it, a helper that always failed would satisfy every other criterion in this phase"
    - "The unchanged-gate check is what makes this phase non-enforcing rather than merely intended to be; Phase 2 depends on inheriting a green tree"
  prohibitions:
    - "This phase must not wire enforcement. No change to the Makefile and no change to the CI workflow, even though both are one line away from turning the mechanism on — and the temptation is highest here, in the plan that measures the difference."
    - "The escalation flag must not default to on. With EPISTEMIC_OS_TEST_REQUIRE_DB unset, every test that skips at the phase base must still skip and the suite must still exit 0."
    - "The two content-conditional skips in the segment acceptance test must not be deleted, converted into failures, or made conditional on the escalation flag. A fixture that genuinely lacks a preamble is real signal, and turning that into a gate failure is the exact conflation this milestone exists to prevent."
    - "A failing check in this plan must not be resolved by weakening the check. If the escalated run does not reach 0 skips, the helper is wrong; the target is not."
---

<objective>
Measure that the escalation mechanism built in 01-01 works when the database is
present, that each escalated condition names its own cause, and — the hard
boundary of this phase — that `make gate` behaves exactly as it did before any of
it landed.

Purpose: this phase's whole claim is "the mechanism exists and enforces nothing".
Both halves need evidence. Without the escalated-green run, a helper that failed
unconditionally would satisfy every other criterion in the phase. Without the
unchanged-gate run, "non-enforcing" is an intention rather than a measurement, and
Phase 2 would inherit a red tree it did not cause.

Output: a SUMMARY recording the measured baseline that Phase 2 will be diffed
against and that Phase 3's proof tests will assert.

**This plan changes no source files.** `files_modified` is deliberately empty. If
a check fails, the fix belongs in 01-01 or 01-02 and this plan re-runs.
</objective>

## Artifacts this phase produces

This plan produces **no code symbols**. Its only artifact is its SUMMARY.

The new symbols this phase creates all belong to plan 01-01 — the
`internal/platform/testenv` package, its exported `URLEnv`, `RequireEnv`,
`Required`, `Pool` and `Fixture`, its unexported `hostFromURL`, and the
`EPISTEMIC_OS_TEST_REQUIRE_DB` environment variable. See that plan's artifacts
table. Plan 01-02 creates no symbols at all.

`EPISTEMIC_OS_DB_URL`, `make gate`, `make up`, `make migrate` and the CI workflow
are all pre-existing and are read, never written, by this plan.

## Flagged assumptions — spec-less edge probe

No SPEC exists for this phase. The deterministic edge probe over GATE-04 and
GATE-05 returned 4 applicable edges, **0 resolved**. All four are reproduced here
because this is the plan a human reviews, and none may be silently dropped:
4 surfaced == 0 authored into `must_haves.truths` + 4 flagged.

| # | Requirement | Category | Probe | Status |
|---|---|---|---|---|
| E1 | GATE-04 | unclassified | (uncategorized — no probe question was generated; review manually) | **unresolved — flagged** |
| E2 | GATE-05 | adjacency | When two things are exactly equal or just touch, do they merge, collide, or separate? | **unresolved — flagged** |
| E3 | GATE-05 | empty | What is the result for empty, single-element, or null input? | **unresolved — flagged** |
| E4 | GATE-05 | ordering | When elements compare equal, is output order specified and stable? | **unresolved — flagged** |

**Honest note.** These are generic data-structure edges. GATE-04 and GATE-05
describe a test harness's skip-or-fail decision, not a collection with adjacency,
emptiness or sort order, so the poor fit is expected. That is a reason to put them
in front of a human to dismiss, not a reason for the planner to dismiss them.

Offered as context, **not** as resolutions — every row above remains unresolved:
E3 has a plausible referent in the empty-string value of the escalation flag and
the empty host returned for a keyword/value DSN, both handled and unit-tested in
01-01 Task 1. E1, E2 and E4 have no evident referent in this phase.

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

Measured in this repository at commit `fcebad1`, before any plan in this phase ran.
This is the baseline every check below is compared against.

- `go test ./... -count=1` with no database: **exit 0, 38 skipped tests.**
- `make gate` is `vet`, then a `gofmt -l .` check, then `go build ./...`, then
  `go test ./... -count=1`. Nothing in it starts PostgreSQL.
- The local DSN for the compose service is
  `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`.
  `make up` starts it and waits for readiness; `make migrate` applies migrations
  and requires `EPISTEMIC_OS_DB_URL` to be exported.
- The store package's cross-package fixture read resolves
  `../../../core/domain/segment/testdata/demo.md` and runs only after a pool is
  obtained, so exercising the unreadable-fixture path requires a live database.
- `.github/workflows/ci.yml` line 36 already sets `EPISTEMIC_OS_DB_URL` and the
  workflow already provisions PostgreSQL and applies migrations, delivered at
  `868d45b`. Neither that file nor the Makefile may be edited in this phase.

**Phase base commit: `fcebad1`.** Confirm it is an ancestor of HEAD before using it
in a diff; if other work landed first, substitute the actual commit this phase
branched from and record the substitution in the summary.

<tasks>

<task type="auto">
  <name>Task 1: Database-free behavioral matrix and non-enforcement audit</name>
  <files>none — verification only, no file is written by this task</files>

  <read_first>
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md (the exported signatures and the failure text 01-01 observed, so this task compares against a stated baseline rather than re-deriving one)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md (the fixture invariant result and the AC-14 baseline)
    - Makefile (lines 38-46 — the exact gate definition being held constant)
    - internal/platform/testenv/testenv.go (the helper as built, to confirm the observed messages come from the branches this plan believes they do)
  </read_first>

  <action>
Run the four scenarios that need no database, and the non-enforcement audit. Record
every observed exit status and message verbatim; the summary is the artifact.

Scenario A, the preserved default. With both `EPISTEMIC_OS_DB_URL` and
`EPISTEMIC_OS_TEST_REQUIRE_DB` explicitly removed from the environment, run the
full suite. It must exit 0 and report exactly 38 skipped tests — the count measured
at the phase base. Use `env -u` rather than assuming the variables are unset, since
a developer shell may export the local DSN.

Scenario B, escalated with no URL. With the flag set and the URL removed, run the
store package and then the approved package. Each must exit non-zero and name
`EPISTEMIC_OS_DB_URL` in its output.

Scenario C, escalated against a closed port. With the flag set and the URL
addressing `127.0.0.1` port 1, run the store package. It must exit non-zero and the
output must contain that host and port, proving the message names the specific
machine it could not reach rather than restating the variable.

Scenario D, the credential audit. Repeat scenario C with a distinctive password in
the DSN, and repeat it again with a DSN malformed enough that the pool constructor
itself rejects it — that constructor echoes its input verbatim, which is the leak
T-01-01 exists for. In both runs the password must not appear anywhere in the
output.

Then the non-enforcement audit. Confirm no commit in this phase touched the Makefile
or the CI workflow, by listing commits from the phase base to HEAD restricted to
those two paths. Confirm the full diff from the phase base touches nothing outside
`internal/` and `.planning/`. Confirm the gate itself still runs green with no
database.

If any scenario fails, do not adjust the scenario. Report it and stop — the defect
belongs to 01-01 or 01-02, and this plan re-runs after that fix.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate &amp;&amp; test "$(env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&amp;1 | grep -c '^--- SKIP')" = "38" &amp;&amp; test -z "$(git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml)" &amp;&amp; echo NONENFORCING_OK</automated>
  </verify>

  <acceptance_criteria>
    - Scenario A: `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - Scenario A: `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB go test ./... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `38`.
    - Scenario B: `env -u EPISTEMIC_OS_DB_URL EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -count=1` exits non-zero and its output contains `EPISTEMIC_OS_DB_URL`.
    - Scenario B: the same command against `./internal/adapters/secondary/approved/...` exits non-zero and its output contains `EPISTEMIC_OS_DB_URL`.
    - Scenario C: `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1 2>&1` exits non-zero and contains `127.0.0.1:1`.
    - Scenario D: `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:PWLEAKCANARY@127.0.0.1:1/nodb?sslmode=disable' go test ./internal/adapters/secondary/store/... -count=1 2>&1 | grep -c PWLEAKCANARY` prints `0`.
    - Scenario D: `EPISTEMIC_OS_TEST_REQUIRE_DB=1 EPISTEMIC_OS_DB_URL='postgres://u:PWLEAKCANARY@ bad host/db' go test ./internal/adapters/secondary/store/... -count=1 2>&1 | grep -c PWLEAKCANARY` prints `0`.
    - Audit: `git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml` prints nothing.
    - Audit: `git diff --name-only fcebad1..HEAD | grep -vc '^\(internal/\|.planning/\)'` prints `0`.
    - Audit: `git rev-parse --verify fcebad1` succeeds and `git merge-base --is-ancestor fcebad1 HEAD` exits 0, confirming the recorded phase base is valid.
  </acceptance_criteria>

  <done>
Every database-free claim in this phase is measured and recorded: the default run
is bit-for-bit the same outcome as the phase base at 38 skips and exit 0, two of the
three escalated conditions name their own cause, no credential reaches the output,
and neither the Makefile nor the CI workflow was touched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Escalated-green and unreadable-fixture proof against a live database</name>
  <files>none — verification only; the fixture is moved and restored within the task and must end byte-identical</files>

  <precondition>PostgreSQL is running and migrated: `make up` succeeds, `EPISTEMIC_OS_DB_URL` is exported as `postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable`, and `make migrate` exits 0 — without a live database neither claim in this task is decidable and execution must halt rather than record an unverified pass.</precondition>

  <read_first>
    - Makefile (lines 18-23 and 47-48 — the up and migrate targets and the readiness wait, so the precondition is satisfied the same way CI does it)
    - internal/adapters/secondary/store/segmentation_test.go (the fixture-round-trip test — the only test that exercises the unreadable-fixture path, and the relative path it resolves)
    - internal/platform/testenv/testenv.go (the fixture branch, to confirm the observed message comes from the escalated path)
  </read_first>

  <action>
Prove the two claims that require a real database.

First, escalated green. With the database up, migrations applied, the DSN exported
and the escalation flag set, run the store and approved packages. Every test must
run: zero skipped and zero failed. This is the check that distinguishes a working
mechanism from one that simply always fails — without it, a helper hard-coded to
fail would satisfy every other criterion in this phase.

Second, the unreadable fixture. With the same environment, move
`internal/core/domain/segment/testdata/demo.md` aside, run only the store package's
fixture round-trip test by name, and confirm it fails with a message naming that
fixture path. Restore the file unconditionally — sequence the restore so it runs
whether the test command succeeded or failed, never conditionally on success. Scope
the run to the store package alone so the segment domain package, which owns that
fixture, is not compiled against a missing file during the window.

After restoring, confirm the working tree is clean and the fixture's hash still
matches by running the segment package's integrity test, which pins it. Do not
proceed to Task 3 until both are confirmed.

Record the exact escalated failure message for the fixture path in the summary.
Phase 3's proof test for GATE-03 asserts against this text, so an approximation is
not good enough.

If the escalated run reports any skip or any failure, stop and report. Do not
narrow the package selection, do not add a skip exclusion, and do not lower the
target — the target is the requirement.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; export EPISTEMIC_OS_DB_URL='postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable' &amp;&amp; make migrate &amp;&amp; test "$(EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -v 2>&amp;1 | grep -c '^--- SKIP')" = "0" &amp;&amp; EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 &amp;&amp; echo ESCALATED_GREEN_OK</automated>
  </verify>

  <acceptance_criteria>
    - `make up` exits 0 and `make migrate` exits 0 with the DSN exported.
    - `EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... ./internal/adapters/secondary/approved/... -count=1 -v 2>&1 | grep -c '^--- SKIP'` prints `0`.
    - The same command filtered for `^--- FAIL` prints `0`, and the plain (non-`-v`) run exits 0.
    - The same command filtered for `^--- PASS` prints at least `38` — every former call site actually ran.
    - With the fixture moved aside, `EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ./internal/adapters/secondary/store/... -run TestSaveRun_FixtureRoundTripsAllOffsets -count=1 2>&1` exits non-zero and its output contains `core/domain/segment/testdata/demo.md`.
    - After restoring, `git status --porcelain` prints nothing except the pre-existing untracked `.planning/config.json`.
    - After restoring, `go test ./internal/core/domain/segment/... -run TestFixtureIntegrity -count=1` exits 0 — the fixture's pinned hash and length still match, proving the move-and-restore was lossless.
    - `env -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0 with the database still up — the gate is green in the database-present case too.
  </acceptance_criteria>

  <done>
With a live database the escalated run executes all 38 database-backed tests and
skips none, and the third environment condition — an unreadable fixture — produces
a failure naming that path. The fixture is restored and still matches its pin.
  </done>
</task>

<task type="auto">
  <name>Task 3: Consolidate the phase baseline and surface the contract decisions for sign-off</name>
  <files>none — verification and summary only, no source file is written</files>

  <read_first>
    - .planning/ROADMAP.md (Phase 1 success criteria, all five — the consolidation is a judgment against these, not against the plan)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md (the exported names and flag semantics Phase 2 and Phase 3 bind to)
    - .planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-SUMMARY.md (the fixture invariant result and the AC-14 baseline)
    - Makefile (the gate target, to confirm by reading that nothing was wired)
  </read_first>

  <action>
Run the final both-environments confirmation and assemble the baseline. Run every
command here directly — do not ask the developer to run anything.

First, `make gate` with no database reachable and no escalation flag. This is the
developer-without-Docker case the whole skip policy exists to protect. Stop the
compose database first if Task 2 left it running, so the case is real rather than
assumed, then bring it back up afterward.

Second, `make gate` with the database up and the DSN exported, still with no
escalation flag. Both must exit 0, and that pair is the phase's central claim: the
mechanism exists and the gate is unmoved.

Then assemble the summary. Collect from Tasks 1 and 2 every exit status, the skip
counts, and the verbatim escalated failure message for each of the three
conditions, redacting passwords. Phase 3 asserts against that text, so record it
exactly rather than paraphrasing.

Finally, write into the summary — for the developer to accept or amend at
end-of-phase review — the three contracts Phase 2 and Phase 3 will bind to, since
changing any of them later is mechanical but no longer local to one package:

- The package path `internal/platform/testenv` and the exported function names.
- The flag name `EPISTEMIC_OS_TEST_REQUIRE_DB`, and that any non-empty value
  enables it, so the string zero enables it too. State the rationale: a typo in the
  value then errs toward enforcing rather than toward a vacuously green gate.
- That the flag is documented in the package doc comment only, with README and
  Makefile documentation deferred to Phase 2, where the flag actually becomes part
  of the gate.

Also carry forward the four unresolved probe edges E1 through E4 verbatim, as open
items awaiting disposition. Do not dismiss any of them; the planner did not, and
neither should the executor.

If either gate run exits non-zero, stop and report. The defect belongs to 01-01 or
01-02 and this plan re-runs after it is fixed.
  </action>

  <verify>
    <automated>cd C:/EpistemicOS/epistemicos-gsd-pilot &amp;&amp; docker compose stop postgres &amp;&amp; env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate &amp;&amp; make up &amp;&amp; env -u EPISTEMIC_OS_TEST_REQUIRE_DB EPISTEMIC_OS_DB_URL='postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable' make gate &amp;&amp; echo GATE_UNCHANGED_BOTH_WAYS</automated>
    <human-check>Review the recorded baseline and accept or amend three contracts Phase 2 and Phase 3 bind to: (1) the package path `internal/platform/testenv` and its exported function names; (2) the flag name `EPISTEMIC_OS_TEST_REQUIRE_DB` and its presence-based semantics, under which the string zero enables escalation because a typo in the value should err toward enforcing rather than toward a vacuously green gate; (3) documenting the flag in the package doc comment only, deferring README and Makefile documentation to Phase 2. Then give a disposition for each of the four unresolved probe edges E1 through E4 — whether each becomes a requirement or is dismissed as inapplicable to a test-harness refactor.</human-check>
  </verify>

  <acceptance_criteria>
    - With the compose database stopped, `env -u EPISTEMIC_OS_DB_URL -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - With the database up and the DSN exported, `env -u EPISTEMIC_OS_TEST_REQUIRE_DB make gate` exits 0.
    - `git log --format=%H fcebad1..HEAD -- Makefile .github/workflows/ci.yml` still prints nothing after all three plans have run.
    - The summary records an exit status and a skip count for every scenario in Tasks 1 and 2.
    - The summary contains the verbatim escalated failure text for all three conditions — unset variable, unreachable host, unreadable fixture — with passwords redacted.
    - The summary lists all three contract decisions and all four probe edges E1 through E4 as items awaiting the developer's disposition, none pre-dismissed.
    - `git status --porcelain` prints nothing except the pre-existing untracked `.planning/config.json`.
  </acceptance_criteria>

  <done>
`make gate` is measured green in both environments, the phase baseline is recorded
in a form Phase 2 can diff against and Phase 3 can assert against, and the three
contract decisions plus the four probe edges are queued for the developer's
end-of-phase disposition rather than settled on their behalf.
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
| T-01-09 | Information Disclosure | the DSNs constructed in Scenarios C and D | high | mitigate | This plan is where a real password would leak if T-01-01's mitigation regressed, so Scenario D is the standing audit for it: two runs with a distinctive password, one through the connect path and one through the parse path that is known to echo its input, each asserting the password count in the output is zero. Severity high meets `security_block_on: high`, so a non-zero count blocks the phase. The DSNs used here carry a throwaway credential, never a real one. |
| T-01-10 | Tampering | `testdata/demo.md` during the Task 2 move | high | mitigate | Moving a hash-pinned fixture risks leaving the tree corrupt if the run aborts. Mitigated by sequencing the restore so it executes regardless of the test's exit status, by scoping the test run to the store package so the owning package is never compiled against the gap, and by two post-conditions: a clean `git status --porcelain` and a passing integrity test that re-checks the pinned hash and byte length. |
| T-01-11 | Elevation of Privilege | the local compose PostgreSQL instance | low | accept | Credentials are the published compose defaults on a loopback port, used only for tests. No production data is reachable. Out of scope at ASVS L1. |
| T-01-12 | Repudiation | the escalated-green measurement | medium | mitigate | A recorded "0 skips" that was never actually run against a database would make the phase's central claim unfalsifiable — the exact failure mode this milestone exists to remove. Mitigated by the task precondition, which halts rather than recording an unverified pass, and by the PASS-count criterion requiring at least 38 tests to have actually executed. |
| T-01-SC | Tampering | dependency installation | low | accept | This plan installs nothing and writes no source. `go.mod` is unchanged across the whole phase. No package-manager install task exists, so no package-legitimacy audit table and no legitimacy checkpoint is required. |
</threat_model>

<verification>
The phase is verified when all five ROADMAP success criteria are measured, not
argued:

1. One helper owns the decision — 01-01 Task 2 criteria: 38 call sites, 6 files,
   0 remaining local definitions.
2. Escalated, each of the three conditions names its cause — Scenarios B and C here
   for the variable and the host, Task 2 here for the fixture path.
3. Flag unset, skips exactly as today — Scenario A: exit 0 and 38 skips, matching
   the count measured at the phase base.
4. The fixture invariant holds and the AC-14 declines stay green and silent — 01-02
   Tasks 1 and 2.
5. `make gate` behaves exactly as before — Task 3 runs it with the compose database
   genuinely stopped and again with it up, and both must exit 0.

Plus the standing non-enforcement audit: no commit in this phase touches the
Makefile or the CI workflow, and no path outside `internal/` and `.planning/`
appears in the phase diff.
</verification>

<success_criteria>
- The default run reproduces the phase base exactly: exit 0, 38 skips.
- The escalated run against a live database executes all 38 and skips none.
- Each of the three environment conditions produces a failure naming that specific cause, with the fixture message recorded verbatim for Phase 3.
- No password appears in any output, through either the connect path or the parse path.
- The Makefile and the CI workflow are untouched, and `make gate` is measured green with the database genuinely stopped and again with it up.
- The three contracts Phase 2 and Phase 3 bind to, and the four unresolved probe edges, are queued for the developer's end-of-phase disposition rather than settled on their behalf.
</success_criteria>

<output>
Create `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md` when done.

Record in it, as the baseline Phase 2 will be diffed against and Phase 3 will assert
against: the exit status and skip count for every scenario; the verbatim escalated
failure message for each of the three conditions, with passwords redacted; the
confirmed phase base commit; the three contract decisions awaiting the developer's
acceptance or amendment; and the four unresolved probe edges awaiting disposition.

The two sign-off blocks are harvested from Task 3's `<verify><human-check>` into the
phase UAT at end-of-phase review, so they reach the developer in one batch rather
than halting execution mid-flight.
</output>


## Review Instructions

**Verify against source — do not review the plan text in isolation.** The plans reference real files, migrations, routes, and tests in this repo.
1. Open the referenced files and check each claim against the actual code.
2. For every strength or concern, cite concrete `path/to/file:line` evidence plus the mechanism.
3. When a plan asserts a mechanism works (a guard, a query filter, a test that exercises a path), trace whether it actually does what is claimed — do not take the plan's word for it.
4. If you cannot read the repo (no file access), say so and downgrade that finding to an open question rather than asserting it.

Findings citing `file:line` evidence are weighted far more heavily than impressionistic ones; a review that only restates the plan's own claims has low value.

Analyze each plan and provide:

1. **Summary** — One-paragraph assessment
2. **Strengths** — What's well-designed (bullet points)
3. **Concerns** — Potential issues, gaps, risks (bullet points with severity: HIGH/MEDIUM/LOW)
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
