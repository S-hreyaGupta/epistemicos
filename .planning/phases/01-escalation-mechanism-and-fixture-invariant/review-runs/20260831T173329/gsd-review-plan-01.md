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
