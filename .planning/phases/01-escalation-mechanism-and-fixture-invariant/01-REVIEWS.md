---
phase: 1
cycle: 2
reviewers: [codex]
reviewed_at: 2026-08-31T18:43:42+05:30
phase_base: 030521b1ec7c12df868445bf8d162527202d42f1
plans_reviewed: [01-01-PLAN.md, 01-02-PLAN.md, 01-03-PLAN.md]
models:
  codex: "gpt-5.6-sol (reasoning=low)"
model_sources:
  codex: "banner"
---

# Cross-AI Plan Review — Phase 1 (Cycle 2)

This is **cycle 2** of the plan-review-convergence loop. Cycle 1 (recorded at
`2041093`, run archived under `review-runs/20260831T173329/`) raised 4 HIGH
concerns and 14 actionable non-HIGH findings against the plan set frozen at
`940727c`/`d90b10d`. The plans were rewritten from that feedback (`09a88c9`),
re-frozen (`dd69e0e`) and planning-complete recorded (`d61eac2`), against a new
phase base commit `030521b`. This cycle reviews the **current** plan set and
reports only what remains unresolved.

## Codex Review

# Cycle 2 Plan Review

## Summary

The current plan set is substantially stronger than cycle 1 and is well aligned with the actual repository. The plans correctly identify the two duplicated database helpers, all 38 database-backed call sites, the cross-package fixture skip, the two AC-14 content skips, and the existing CI/PostgreSQL arrangement. Most prior findings are now resolved.

Two verification defects remain: one materially weakens the promised unconditional fixture restoration, and one makes the zero-skip acceptance check incompatible with the required `pipefail` shell mode. Overall risk is **MEDIUM** pending those corrections.

## Plan 01 — Shared escalation helper

### Strengths

- The consolidation scope matches the repository. The two independent policy implementations are at `internal/adapters/secondary/store/segmentation_test.go:16-45` and `internal/adapters/secondary/approved/papers_test.go:19-46`.

- The claimed 38 call sites across six files is correct. Repository inspection found exactly 38 `testPool(t)` calls across six test files.

- The proposed decision ordering follows the real execution path. The fixture round-trip test obtains the pool before reading the fixture at `internal/adapters/secondary/store/segmentation_test.go:272-278`, so a database prerequisite necessarily wins over a fixture error.

- The plan correctly preserves the current classification of malformed configuration versus unreachability. `pgxpool.New` errors currently fail at `internal/adapters/secondary/store/segmentation_test.go:34-37`, while `Ping` errors skip at lines 38-41.

- Routing the fixture read into the shared helper addresses the only cross-package unreadable-fixture skip. The existing site is `internal/adapters/secondary/store/segmentation_test.go:276-279`.

- The dependency assumptions are accurate: pgx v5.7.2 is a direct dependency and no assertion library exists at `go.mod:5-10`.

### Concerns

No unresolved concern specific to Plan 01 was found.

The cycle-1 pipeline, anchor, disclosure-canary, and duplicated-decision findings appear resolved in the current plan. They should not be reopened.

### Suggestions

- Retain the proposed direct call-site conversion and pure unit tests.
- Keep the malformed-DSN fixed-message design; it provides a stable diagnostic without forwarding connection-string-derived data.

## Plan 02 — Fixture invariant

### Strengths

- The invariant is placed beside the existing fixture integrity pins, which is the correct ownership boundary. `loadFixture` reads `testdata/demo.md` at `internal/core/domain/segment/fixture_test.go:83-89`, and `TestFixtureIntegrity` begins at line 128.

- The plan accurately identifies the AC-14 behavior. It reads `headings[0].ByteStart` at `internal/core/domain/segment/acceptance_test.go:435`, then conditionally skips for zero-length and whitespace-only preambles at lines 438 and 451.

- The mutation-free negative proof is a material improvement. Exercising one pure function with synthetic violating and valid inputs proves both failure and success behavior without risking the pinned fixture.

- Leaving `acceptance_test.go` byte-identical correctly preserves GATE-04’s distinction between a fixture invariant and a generally legitimate content-conditional decline.

### Concerns

- **LOW — PARTIALLY RESOLVED, NOT ACTIONABLE:** AC-14 still indexes `headings[0]` without an empty check at `internal/core/domain/segment/acceptance_test.go:435`. Because Go does not order tests, `TestFixtureIntegrity` cannot be guaranteed to report its cleaner “no headings detected” failure before AC-14 panics. The plan explicitly acknowledges and defers this at `01-02-PLAN.md:90` and carries it into developer disposition in `01-03-PLAN.md:493-497`. Since the deferral is explicit and this phase intentionally requires the acceptance file to remain byte-identical, no additional cycle-2 task is required.

### Suggestions

- At phase sign-off, turn the empty-heading guard into a concrete backlog item or assign it to Phase 2. Avoid leaving it as an indefinitely recurring review note.

## Plan 03 — Behavioral audit

### Strengths

- The plan verifies both halves of “mechanism exists but does not enforce”: `make gate` with PostgreSQL absent and present. This is consistent with the current gate at `Makefile:38-45`, which neither starts PostgreSQL nor sets the escalation flag.

- The database precondition matches the real project targets. `make up` starts and waits for PostgreSQL at `Makefile:18-22`; migrations run through the CLI at lines 47-48.

- The CI baseline is accurately described. PostgreSQL is provisioned at `.github/workflows/ci.yml:18-31`, the DSN is exported at lines 33-36, migrations run at lines 64-68, and tests run at lines 70-71.

- Name-set containment is much stronger than counting PASS lines. It verifies that every test skipped without a database appears among the tests passing with one.

- The worktree assumptions currently match the repository: `git status --porcelain` shows only `?? .planning/config.json`, and the corrected base `030521b1ec7c12df868445bf8d162527202d42f1` exists.

### Concerns

- **HIGH — PARTIALLY RESOLVED:** The fixture restoration is not actually guaranteed by the exact command. The plan correctly installs a trap before moving the hash-pinned fixture, but the explicit restoration uses:

  ```sh
  mv "$TMP/demo.md" "$FIX"; trap - EXIT INT TERM
  ```

  at `01-03-PLAN.md:416`. Because these commands are separated by `;`, a failed `mv` does not prevent the trap from being cleared. The script can therefore strand `demo.md` in the temporary directory—the exact high-severity failure the mitigation claims to prevent. This concerns the real pinned file read at `internal/core/domain/segment/fixture_test.go:87` and used by AC-14 at `internal/core/domain/segment/acceptance_test.go:427-435`.

  **ACTIONABLE:** Yes. `/gsd-execute-phase` will run the exact command unless it is corrected in the plan.

- **MEDIUM — NEWLY RAISED:** The escalated zero-skip acceptance criterion conflicts with mandatory `set -o pipefail`. At `01-03-PLAN.md:412`, the plan requires a filtered pipeline to “print `0`” when there are no skip events. A final `grep -c` prints `0` but exits status 1 when it finds no matches; under `pipefail`, that makes the pipeline fail even though zero skips is the desired result. The automated block at line 407 avoids this particular check, so the acceptance criterion remains unrunnable as written.

  **ACTIONABLE:** Yes. The zero-skip mechanism must be specified in the plan so execution does not mistake success for failure.

- **LOW — NEWLY RAISED:** The plan repeatedly calls the skipped/pass comparison “set equality,” but the implemented command is containment: `comm -23 base_skips esc_pass` at `01-03-PLAN.md:407,413`. Containment is the correct property—there will naturally be additional passing tests—but the terminology is inaccurate.

  **ACTIONABLE:** Yes, but documentation-only. Rename the claim to “set containment” in `must_haves.truths` and related prose so the executor and summary do not record a stronger property than was tested.

### Suggestions

- Make explicit restoration conditional and leave the trap active if restoration fails:

  ```sh
  mv "$TMP/demo.md" "$FIX" || exit 1
  trap - EXIT INT TERM
  ```

  Preferably also remove the temporary directory after successful restoration.

- Test zero skips without a failing no-match pipeline. For example, capture JSON output and count matches with a construct whose status remains successful:

  ```sh
  out=$(EPISTEMIC_OS_TEST_REQUIRE_DB=1 go test ... -json 2>&1)
  st=$?
  test "$st" -eq 0
  skips=$(printf '%s\n' "$out" | awk '/"Action":"skip"/ && /"Test":/ {n++} END {print n+0}')
  test "$skips" -eq 0
  ```

- Change “set equality” to “the baseline skip set is a subset of the escalated pass set.”

## Risk Assessment

**Overall risk: MEDIUM.**

The architecture, requirement mapping, dependency ordering, negative controls, and repository facts are sound. The plans should achieve the phase goal once the two verification mechanics are corrected. The remaining HIGH issue is localized but important: the plan currently claims an unconditional recovery guarantee that its exact shell command does not provide. The zero-skip check is less dangerous but would create a false failure during execution. After those edits, residual implementation risk should be LOW.

---

## Consensus Summary

Only one reviewer ran this cycle (`--codex`), so there is no cross-reviewer
consensus to synthesize. The findings below are Codex's, filtered through
orchestrator verification against the repository — every `file:line` citation in
the Codex section was independently re-checked before this file was written (see
**Verification coverage**).

### Agreed Strengths

Single reviewer; strengths are recorded as reported and verified:

- The consolidation scope matches reality: exactly 38 `testPool(t)` call sites
  across exactly the six files 01-01 names.
- The skip/fail split the helper must preserve is correctly read from the
  existing code — `pgxpool.New` errors are fatal, `Ping` errors skip.
- The fixture invariant is placed beside the existing hash pin rather than by
  mutating the pinned fixture, and `acceptance_test.go` stays byte-identical,
  which is what GATE-04 actually requires.
- Name-set containment replaces cycle 1's `--- PASS` line count, which subtests
  inflate and which names no test.
- Cycle 1's pipeline-status, anchor, DSN-disclosure-canary and
  duplicated-decision findings are resolved in the current plans and are not
  reopened.

### Agreed Concerns

Carried forward as this cycle's unresolved set:

1. **HIGH — restore-then-clear-trap ordering in 01-03.** The unconditional
   fixture restoration is not unconditional.
2. **MEDIUM — the "zero skips" acceptance criterion has no automated command**
   and its natural pipeline form is fragile under the plan's own mandatory
   `set -o pipefail`.
3. **LOW — "set equality" vs "set containment"** mislabel in
   `must_haves.truths` and the deferral table.

### Divergent Views

None — single reviewer.

---

## Verification coverage

Every claim in the Codex section that cites repository source was re-checked by
the orchestrator against the working tree at `030521b` + planning commits. All
sampled citations verified:

| Claim | Citation | Verified |
|---|---|---|
| 38 call sites across 6 files | `grep -rn "testPool(t)" internal/` | ✓ 38 matches, 6 files, exactly those named in 01-01 |
| Duplicated policy helper #1 | `internal/adapters/secondary/store/segmentation_test.go:16-45` | ✓ `testPool` with `t.Skip` on unset URL, `t.Fatalf` on `pgxpool.New`, `t.Skipf` on `Ping` |
| Duplicated policy helper #2 | `internal/adapters/secondary/approved/papers_test.go:19-46` | ✓ present |
| Cross-package fixture skip | `internal/adapters/secondary/store/segmentation_test.go:272-279` | ✓ `pool := testPool(t)` at 272 precedes `os.ReadFile(...)`/`t.Skipf` at 276-279 — so a database condition necessarily wins over a fixture condition |
| AC-14 unguarded index | `internal/core/domain/segment/acceptance_test.go:435` | ✓ `firstHeading := headings[0].ByteStart` with no length check |
| AC-14 content skips | `internal/core/domain/segment/acceptance_test.go:438,451` | ✓ both `t.Skip` sites present and are content-conditional |
| Gate definition | `Makefile:38-45` | ✓ `gate: vet` → `gofmt -l` → `go build` → `go test`; no Postgres, no escalation flag |
| Restore/trap defect | `01-03-PLAN.md:416` | ✓ `mv "$TMP/demo.md" "$FIX"; trap - EXIT INT TERM` — `;`-separated, so the trap is cleared even when the restore fails |
| Zero-skip criterion has no automated command | `01-03-PLAN.md:407` (verify) vs `:412` (criterion) | ✓ the `<automated>` block asserts containment and exit status but never counts escalated skips |
| Terminology mismatch | `01-03-PLAN.md:22,83` say "set equality"; `:413` says "set containment"; `comm -23` implements containment | ✓ internally inconsistent |

Reviewer evidence class: **source-grounded** (Codex had repo access and cited
`file:line` throughout; no `[reviewed-without-repo-access]` or
`[reviewed-without-source-citations]` marker).

## Orchestrator adjudication

One Codex finding is recorded here with a narrowed mechanism:

- On the MEDIUM zero-skip finding, Codex's stated mechanism — that `grep -c`
  exiting 1 on no matches breaks the check under `pipefail` — is only true for
  some spellings. In the capture form the plan mandates at `01-03-PLAN.md:101-106`
  (`test "$(… | grep -c …)" = "0"`), command substitution swallows the pipeline
  status and the check is safe. The finding **still stands**, on the narrower
  and verified ground that the criterion at `:412` has **no corresponding command
  in the `<automated>` verify block at `:407`**, leaving the executor to improvise
  a spelling that the plan's own pipeline rule makes easy to get wrong. The
  containment check covers the 38 baseline skips but would not catch a *newly
  introduced* skip in the escalated run, which is what "zero skips" asserts.

## Next step

To incorporate this feedback into planning:

    /gsd-plan-phase 1 --reviews
