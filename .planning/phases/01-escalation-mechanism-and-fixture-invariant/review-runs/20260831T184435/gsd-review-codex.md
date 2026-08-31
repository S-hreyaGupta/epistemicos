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
