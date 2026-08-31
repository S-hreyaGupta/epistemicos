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
