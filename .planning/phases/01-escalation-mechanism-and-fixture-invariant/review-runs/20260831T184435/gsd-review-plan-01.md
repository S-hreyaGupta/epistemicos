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
