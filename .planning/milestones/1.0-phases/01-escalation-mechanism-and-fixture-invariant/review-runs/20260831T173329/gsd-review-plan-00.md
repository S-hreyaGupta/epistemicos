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
