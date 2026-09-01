---
phase: 01-escalation-mechanism-and-fixture-invariant
plan: 02
subsystem: testing
tags: [go, testing, fixture-invariant, gate-04, table-test]

# Dependency graph
requires: []
provides:
  - "preambleInvariant(src []byte, headings []Heading, declaredHasPreamble bool) string — pure decision function in fixture_test.go"
  - "fixtureHasPreamble — pinned declaration constant beside fixtureSHA256/fixtureBytes"
  - "TestFixtureIntegrity now asserts the preamble property against the pinned fixture"
  - "TestPreambleInvariant_Control — permanent, mutation-free negative proof (6 subtests)"
affects: [01-03-escalation-mechanism, phase-2-classification, phase-3-negative-tests]

actuals:
  tokens: 1712
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Pure-function invariant + synthetic-input table test as the mutation-free replacement for temporarily-edit-and-restore negative proofs"
    - "Declared pinned constant (fixtureHasPreamble) as the seam that admits a policy exception without silently waiving an assertion"

key-files:
  created: []
  modified:
    - internal/core/domain/segment/fixture_test.go

key-decisions:
  - "The preamble property is asserted once in TestFixtureIntegrity against the hash-pinned fixture, not re-derived per-run inside the acceptance test — this is what keeps AC-14's two content-conditional t.Skip calls green and silent instead of becoming a gate failure class."
  - "fixtureHasPreamble is a pinned constant (declared true), not a runtime skip, so a genuinely preamble-free fixture must be declared in the same diff that repins the hash and length."
  - "The negative proof (TestPreambleInvariant_Control) is a permanent table test against synthetic Heading values, not a temporary mutation of testdata/demo.md — this fully retires the mutate-and-restore pattern flagged as MEDIUM risk in cycle-1 review."
  - "No change was made to acceptance_test.go; Task 2 only verified byte-identity against the phase base and confirmed the two content-conditional skips still exist and do not fire for the pinned fixture."

requirements-completed: [GATE-04]

coverage:
  - id: D1
    description: "TestFixtureIntegrity fails, naming testdata/demo.md, if the pinned fixture ever has no preamble, a zero-offset first heading, a whitespace-only preamble, or no headings at all"
    requirement: "GATE-04"
    verification:
      - kind: unit
        ref: "internal/core/domain/segment/fixture_test.go#TestFixtureIntegrity"
        status: pass
      - kind: unit
        ref: "internal/core/domain/segment/fixture_test.go#TestPreambleInvariant_Control"
        status: pass
    human_judgment: false
  - id: D2
    description: "The declaration gate (fixtureHasPreamble) waives only the two preamble checks, never the no-headings check, and is proven in both directions with synthetic inputs"
    requirement: "GATE-04"
    verification:
      - kind: unit
        ref: "internal/core/domain/segment/fixture_test.go#TestPreambleInvariant_Control/declared_preamble-free"
        status: pass
      - kind: unit
        ref: "internal/core/domain/segment/fixture_test.go#TestPreambleInvariant_Control/declared_preamble-free,_but_no_headings"
        status: pass
    human_judgment: false
  - id: D3
    description: "The AC-14 content-conditional skips in acceptance_test.go survive byte-identical and remain unreachable (PASS, not SKIP) for the pinned fixture"
    requirement: "GATE-04"
    verification:
      - kind: unit
        ref: "internal/core/domain/segment/acceptance_test.go#TestAC14_PreHeadingContentHasNoNode"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-09-01
status: complete
---

# Phase 1 Plan 2: Fixture Preamble Invariant Summary

**`TestFixtureIntegrity` now proves `testdata/demo.md`'s preamble property once, against hash-pinned bytes, via a pure `preambleInvariant` function exercised by a permanent 6-case synthetic-input table test — with no mutation of tracked source and no change to the two content-conditional skips in `acceptance_test.go`.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-09-01T08:04:00Z (approx)
- **Completed:** 2026-09-01T08:19:05Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Added `fixtureHasPreamble`, a pinned `const` declared immediately after `fixtureBytes` (line 39, 10 lines after `fixtureBytes` at line 29), documenting that repinning the fixture to a preamble-free one requires flipping this constant in the same diff as the hash and length.
- Added `preambleInvariant(src []byte, headings []Heading, declaredHasPreamble bool) string`, a pure function checked in this order: no-headings (unconditional) → gate on `declaredHasPreamble` → zero-offset first heading → whitespace-only preamble.
- Extended `TestFixtureIntegrity` to call `detectHeadings` on the loaded fixture and pass the result, together with the `fixtureHasPreamble` constant (not an inlined literal), into `preambleInvariant`, `t.Fatal`-ing on a non-empty message.
- Added `TestPreambleInvariant_Control`, a 6-subtest table test that drives `preambleInvariant` directly with synthetic `Heading` values — no file in the working tree is read, mutated, or restored. This is the permanent replacement for the cycle-1 mutate-and-restore proposal.
- Verified (Task 2, no code change) that `acceptance_test.go` is byte-identical to the phase base and that `TestAC14_PreHeadingContentHasNoNode` reports PASS, not SKIP, against the pinned fixture.

## Task Commits

1. **Task 1: Assert the preamble as a fixture invariant, with a mutation-free negative proof** - `bdf7ddd` (feat)
2. **Task 2: Prove the AC-14 content skips are untouched, green and silent** - no commit (read-only verification task; made no file changes)

**Plan metadata:** pending (this SUMMARY commit)

## Files Created/Modified

- `internal/core/domain/segment/fixture_test.go` - Added `fixtureHasPreamble` const, `preambleInvariant` pure function, extended `TestFixtureIntegrity`, added `TestPreambleInvariant_Control` (133 lines added, 0 removed)

## Observed Results (verbatim, for Phase 3 to build on)

**`TestFixtureIntegrity`:**
```
--- PASS: TestFixtureIntegrity (0.00s)
```

**`TestPreambleInvariant_Control` (all 6 subtests):**
```
--- PASS: TestPreambleInvariant_Control (0.00s)
    --- PASS: TestPreambleInvariant_Control/no_headings_at_all (0.00s)
    --- PASS: TestPreambleInvariant_Control/first_heading_at_byte_0 (0.00s)
    --- PASS: TestPreambleInvariant_Control/whitespace-only_preamble (0.00s)
    --- PASS: TestPreambleInvariant_Control/valid_preamble (0.00s)
    --- PASS: TestPreambleInvariant_Control/declared_preamble-free (0.00s)
    --- PASS: TestPreambleInvariant_Control/declared_preamble-free,_but_no_headings (0.00s)
```

**`TestAC14_PreHeadingContentHasNoNode`:**
```
--- PASS: TestAC14_PreHeadingContentHasNoNode (0.00s)
```
PASS is the requirement **for these pinned bytes** — it means both content-conditional declines (offset-zero at phase-base line 438, whitespace-only at line 451) did not fire, so the test's real node-span assertions actually executed. This is not a claim that a decline would be wrong in general: under GATE-04 a genuinely preamble-free fixture must produce SKIP, and that remains the correct and legal outcome for such a fixture. A SKIP against the pinned fixture would mean the fixture lost its preamble — which Task 1's invariant would have caught first in `TestFixtureIntegrity`.

**The three invariant failure messages, verbatim** (for Phase 3's negative-test authors):
- `testdata/demo.md: no headings detected`
- `testdata/demo.md: first heading starts at byte 0; AC-14 requires a non-whitespace preamble`
- `testdata/demo.md: bytes [0,N) are whitespace only`

**Re-measured fixture SHA-256:**
```
a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e *internal/core/domain/segment/testdata/demo.md
```
Matches the pinned constant exactly — the fixture was not regenerated to accommodate this assertion.

**`acceptance_test.go` byte-identity to phase base `868d45b`:** confirmed. `git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3 -- internal/core/domain/segment/acceptance_test.go` printed nothing. `grep -c 't.Skip'` on that file is `2`, identical to the phase-base count.

## Decisions Made

- The preamble property is decided by one pure function (`preambleInvariant`), called from `TestFixtureIntegrity` rather than reimplemented inline, so the negative-proof table test exercises the exact assertion that runs in production, not a copy.
- `fixtureHasPreamble` is read via the constant at the call site (`preambleInvariant(src, detectHeadings(src), fixtureHasPreamble)`), never inlined as a literal `true`, so a repin that flips the constant actually changes behavior.
- No guard/`if` wraps the call to `preambleInvariant` in `TestFixtureIntegrity` — the gate lives inside the function, reachable by the control test, and no `t.Skip` was introduced at the call site.

## Deviations from Plan

None - plan executed exactly as written. No Rule 1-4 auto-fixes were needed; the implementation matched the plan's action section directly and all task-level acceptance criteria that could pass in this repository state did pass.

## Issues Encountered

**Discrepancy in two whole-tree-diff acceptance criteria (Task 1 and Task 2), not caused by this plan's execution:**

Both tasks include an acceptance criterion of the form `git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3 --` (no path restriction) "prints exactly `internal/core/domain/segment/fixture_test.go` and nothing else." Run verbatim, this command actually prints 47 files, because the working branch already carries ~29 `.planning/`-only commits made after the approved phase base `868d45b` — the base-approval re-anchor (`8edae22`), the plan-set re-freeze (`c96ecb2`), review-run archives, and the STATE.md base-decision record (`fc46f1c`), none of which this plan authored or could have avoided (editing any of them is explicitly prohibited by this plan's scope). These are legitimate planning-process artifacts committed to git history between the chosen base and the start of execution.

The narrower, source-scoped form of the same check — `git diff --name-only 868d45bf873c9e147f18a099171b99afa348f4a3 -- internal/` — does print exactly one file, `internal/core/domain/segment/fixture_test.go`, both after Task 1 and after Task 2, confirming the substantive claim the criterion exists to protect (no other source file changed, `acceptance_test.go` untouched, no Makefile/CI change). Recorded here per the "run verbatim, report don't paraphrase" instruction rather than silently treated as passing or silently reworded.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The fixture invariant is in place and proven both to fail (three synthetic violating cases) and to pass (valid case), with the declaration gate proven both to open (`declared preamble-free`) and to stay narrow (`declared preamble-free, but no headings`).
- `acceptance_test.go` is confirmed byte-identical to the phase base; AC-14's two content-conditional skips remain in place, unreachable for the pinned fixture, and reachable (legal) for a genuinely preamble-free one.
- The three verbatim invariant failure messages are recorded above for Phase 3's negative-test authors to assert against.
- The deferred AC-14 empty-heading guard (no emptiness check before `headings[0]` indexing in `acceptance_test.go`) is **not** addressed here per this plan's own prohibition against editing `acceptance_test.go`; it is explicitly carried forward to 01-03 Task 3's disposition list, as the plan's review-response table specifies.
- No enforcement was wired in this plan (no Makefile or CI change) — `make gate` behavior is unchanged, as intended.
- The whole-tree-diff acceptance-criterion discrepancy above (pre-existing `.planning/` commits since the phase base) should be noted by whoever runs 01-01 and 01-03's own whole-tree-diff criteria, since the same base drift affects them identically.

---
*Phase: 01-escalation-mechanism-and-fixture-invariant*
*Completed: 2026-09-01*
