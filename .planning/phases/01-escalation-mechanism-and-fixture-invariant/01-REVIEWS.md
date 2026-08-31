---
phase: 1
cycle: 3
reviewers: [codex]
reviewed_at: 2026-08-31T19:15:36+05:30
phase_base: 030521b1ec7c12df868445bf8d162527202d42f1
plan_set_head: ded50c21d713553a2b532743b069806bb9ee44bf
plans_reviewed: [01-01-PLAN.md, 01-02-PLAN.md, 01-03-PLAN.md]
models:
  codex: "gpt-5.6-sol (reasoning=low)"
model_sources:
  codex: "banner"
---

# Cross-AI Plan Review — Phase 1 (Cycle 3)

This is **cycle 3**, the final cycle of the plan-review-convergence loop.

- **Cycle 1** (recorded at `2041093`, run archived under `review-runs/20260831T173329/`)
  raised 4 HIGH concerns and 14 actionable non-HIGH findings against the plan set
  frozen at `940727c`/`d90b10d`. The plans were rewritten (`09a88c9`), re-frozen
  (`dd69e0e`), planning-complete recorded (`d61eac2`).
- **Cycle 2** (recorded at `aeb4a98`, run archived under `review-runs/20260831T184435/`)
  raised 1 HIGH and 2 actionable non-HIGH findings. The replan was **narrow** and
  touched only `01-03-PLAN.md` (`cdad611`, re-frozen at `d92a8c9`, planning-complete
  at `ded50c2`). `01-01-PLAN.md` and `01-02-PLAN.md` are byte-identical to the
  cycle-1 convergence freeze and carry no outstanding finding.
- The cycle-2 HIGH was that the fixture-restore path in `01-03` was not fail-closed:
  the explicit restore and the trap-clearing were `;`-separated
  (`mv "$TMP/demo.md" "$FIX"; trap - EXIT INT TERM`) under `set -o pipefail` but
  **without** `set -e`, so a failed restore fell straight through to the statement
  that disarmed the guard.

This cycle reviews the **current** plan set at `ded50c2` and reports only what
remains unresolved.

## Codex Review

## Summary

The plan set is substantially converged and matches the repository’s current structure. Plans 01-01 and 01-02 accurately identify the duplicated database helpers, all 38 call sites, the cross-package fixture skip, and the AC-14 content skips. The cycle-2 restore defect is mostly fixed: shell precedence now prevents `trap - EXIT INT TERM` from being reached after any guarded failure. Two execution-level issues remain in 01-03: the trap cannot actually recover from several post-restore failures despite claiming it can, and the final `printf | grep -q` pipeline can falsely fail under `pipefail`. Overall risk is MEDIUM.

## Strengths

- The source inventory is accurate. The two existing environment-decision helpers are at [segmentation_test.go:23](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:23) and [papers_test.go:24](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/approved/papers_test.go:24). The repository contains exactly the planned 38 `testPool(t)` call sites across six files.

- The fixture path is correctly identified as a separate environmental skip reached after acquiring the pool: the pool is obtained at [segmentation_test.go:272](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:272), the file is read at [segmentation_test.go:276](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:276), and read failure skips at [segmentation_test.go:278](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:278). This supports the planned database-before-fixture ordering.

- Plan 01-02 correctly preserves the distinction between fixture integrity and content-conditional acceptance behavior. AC-14 indexes the first heading at [acceptance_test.go:435](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:435), while its legitimate content declines remain at [acceptance_test.go:438](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:438) and [acceptance_test.go:451](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:451).

- The invariant is being added beside existing strong fixture pins: byte length and SHA-256 are enforced at [fixture_test.go:92](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:92) and [fixture_test.go:97](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:97). A pure-function negative proof is appropriate and avoids mutating tracked source.

- The phase boundary is correct. `make gate` currently performs vet, formatting, build, and tests without starting PostgreSQL or setting escalation at [Makefile:38](C:/EpistemicOS/epistemicos-gsd-pilot/Makefile:38). CI already provisions PostgreSQL and exports the DSN at [ci.yml:20](C:/EpistemicOS/epistemicos-gsd-pilot/.github/workflows/ci.yml:20) and [ci.yml:33](C:/EpistemicOS/epistemicos-gsd-pilot/.github/workflows/ci.yml:33).

- The cycle-2 operator-precedence defect is resolved. In [01-03-PLAN.md:510](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:510), each of the restore, existence, re-hash, and comparison operations has an immediate `|| { ...; exit 1; }`. Because semicolons terminate each complete guarded command, `trap - EXIT INT TERM` cannot be reached through any of those failure paths.

- `$?` capture is correct: `st=$?` immediately follows the `out=$(go test ...)` assignment. Bash gives that assignment the command substitution’s exit status, so it captures `go test`, not a later command.

- The zero-skip and containment corrections are sound. [01-03-PLAN.md:504](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:504) separately checks the test status and filtered skip count, while [01-03-PLAN.md:507](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:507) accurately calls `comm -23` subset containment.

## Concerns

- **MEDIUM — PARTIALLY RESOLVED — ACTIONABLE:** The trap remains armed on all four abort paths, but it cannot “retry the restore” on all four as claimed.

  The trap condition at [01-03-PLAN.md:510](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:510) restores only when both conditions hold:

  ```sh
  [ -f "$TMP/demo.md" ] && [ ! -f "$FIX" ]
  ```

  Its behavior by failure point is:

  | Failure | Likely state | EXIT trap |
  |---|---|---|
  | Explicit restore `mv` fails before moving | temp exists, destination absent | Retries restore |
  | Destination existence check fails after `mv` reported success | temp may already be gone | Usually no-op |
  | Re-hash fails | destination exists, temp is gone | No-op |
  | Hash mismatch | destination exists, temp is gone | No-op |

  Thus [01-03-PLAN.md:513](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:513), which says any of the four guards causes the EXIT trap to retry restoration, is false. Likewise, [01-03-PLAN.md:515](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:515) says a restored-but-altered file aborts “with the guard still armed,” but the armed guard has no preserved good copy with which to repair it.

  The original cycle-2 defect—clearing the trap after a failed `mv`—is fixed. The remaining problem is the broader recovery guarantee. `/gsd-execute-phase` will inherit that incorrect guarantee unless the task is changed.

- **MEDIUM — NEWLY RAISED — ACTIONABLE:** The success-message check can falsely fail because it combines `pipefail` with `grep -q`.

  The command ends at [01-03-PLAN.md:510](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:510) with:

  ```sh
  test "$st" -ne 0 &&
    printf '%s' "$out" |
    grep -q 'core/domain/segment/testdata/demo.md' &&
    echo FIXTURE_FAIL_OK
  ```

  Under `set -o pipefail`, `grep -q` may exit as soon as it finds the path. If captured `go test` output continues beyond that match, the Bash `printf` builtin can encounter a closed pipe and return non-zero. `pipefail` then makes the pipeline non-zero even though the required text was found, suppressing `FIXTURE_FAIL_OK`.

  This is input-size and match-position dependent, so a stand-in with short output may not expose it. It is especially avoidable here because the output is already in a shell variable.

- **LOW — NEWLY RAISED — ACTIONABLE:** `mktemp -d` does not guarantee the temporary file remains on the workspace volume.

  [01-03-PLAN.md:510](C:/EpistemicOS/epistemicos-gsd-pilot/.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md:510) uses the default MSYS temporary directory. On the stated host it is probably on `C:`, but Git Bash honors temporary-directory configuration, so this is not guaranteed. If `$TMP` is on another Windows volume, `mv` becomes a copy-and-delete operation rather than a same-filesystem rename, enlarging the interruption window the trap is intended to control.

  The relative `$FIX` itself is safe because the command first changes to a fixed directory and never changes directory afterward. GNU `sha256sum | cut -d' ' -f1` is also valid for this filename. `INT`/`TERM` handlers can run before EXIT; the guard is sufficiently idempotent for the ordinary interruption path.

## Suggestions

- Preserve a recovery copy until verification succeeds. For example, create a temporary directory adjacent to the fixture and copy the fixture into it, or restore by copying rather than consuming the only temporary copy. Remove that backup only after existence and hash checks pass.

- Narrow the prose if full recovery is not required. State accurately that all four failures abort before trap clearing, but only a failed or interrupted move is automatically recoverable. Do not claim the EXIT handler repairs re-hash or hash-mismatch cases without a retained copy.

- Replace the final pipeline with a non-SIGPIPE-prone check, such as:

  ```sh
  grep 'core/domain/segment/testdata/demo.md' >/dev/null <<<"$out"
  ```

  or a Bash pattern test. This avoids `printf | grep -q` under `pipefail`.

- Create the temporary directory on the same filesystem, preferably adjacent to `demo.md`, and remove it after successful verification.

- Add a small shell-level stand-in covering all four named failure states, not only the inbound `mv` failure. Assert both exit status and resulting filesystem state.

## Risk Assessment

**MEDIUM.** The implementation design and requirement coverage are strong, and the cycle-2 trap-disarming bug is genuinely fixed. The remaining issues are concentrated in the destructive verification harness rather than production code. However, that harness moves a hash-pinned fixture and currently overstates its recovery guarantees; its final `pipefail` pipeline can also report a false failure. These should be corrected in Plan 01-03 before execution.


---

## Consensus Summary

Only one external reviewer ran this cycle (`--codex`), so there is no second
opinion to converge with. To keep the cycle from resting on a single unverified
voice, the orchestrator independently re-derived the shell claims against Git Bash
stand-ins on this host; those results are recorded under **Verification coverage**
below and are treated as a second source where they agree or disagree with Codex.

**Headline: the cycle-2 HIGH is resolved.** Both Codex and the orchestrator's own
stand-in confirm that in the reworked command at `01-03-PLAN.md:510`, each of the
four inbound steps — the restore `mv`, the `test -f` existence re-check, the
re-hash, and the `$BEFORE`/`$AFTER` comparison — terminates in an
`|| { …; exit 1; }` whose braces close before the next `;`. `trap - EXIT INT TERM`
is therefore unreachable from any of those failure paths. Executed with `mv`
shadowed so only the inbound direction fails, the command exits `1`, prints
`RESTORE_FAILED_TRAP_ARMED`, and the still-armed EXIT trap fires and restores the
file. The specific fail-open shape cycle 2 rejected is gone.

**No HIGH concerns remain.** Three actionable non-HIGH findings do.

### Agreed Strengths

Single grounded reviewer plus orchestrator verification; the following were
confirmed from source by both:

- The repository inventory the plans rest on is accurate: the two duplicated
  environment-decision helpers at `internal/adapters/secondary/store/segmentation_test.go:23`
  and `internal/adapters/secondary/approved/papers_test.go:24`, and exactly **38**
  `testPool(t)` call sites across **6** test files (re-counted this cycle).
- The cross-package fixture path is correctly modelled as a *separate* environment
  skip reached only after the pool is obtained: pool at `segmentation_test.go:272`,
  read at `:276`, skip at `:278`. The database-before-fixture ordering the plans
  claim is the ordering the code actually has.
- `st=$?` reads the status the plan thinks it reads — it immediately follows the
  `out=$(go test …)` assignment, whose status is the substitution's.
- The zero-skip counting form is correct under `pipefail`: command substitution
  discards the pipeline status, so `test "$(… | grep -c …)" = "0"` succeeds on the
  zero case even though the inner `grep` exits `1`. Verified directly.
- Plan 01-02 preserves the AC-14 content skips at `acceptance_test.go:438,451`
  rather than converting them, which is the distinction this milestone exists to
  protect.

### Agreed Concerns

With one reviewer, "agreed" means Codex raised it and the orchestrator independently
reproduced or confirmed it from source.

1. **The trap's recovery guarantee is narrower than the plan claims** (MEDIUM,
   PARTIALLY RESOLVED, ACTIONABLE). Confirmed independently. The trap body guards on
   `[ -f "$TMP/demo.md" ] && [ ! -f "$FIX" ]`. That is true only when the temp copy
   still exists *and* the fixture is absent — i.e. the failed-inbound-`mv` case. On
   the re-hash-failed and hash-mismatch paths the fixture is present, so the trap is
   a **no-op**; on the `RESTORE_MISSING` path the temp copy has already been
   consumed, so it is a no-op too. `01-03-PLAN.md:513` ("If any of the four guards
   fires … the EXIT trap runs and retries the restore") and `:515` ("aborts with the
   guard still armed") therefore overstate the control. The tree is not left
   *corrupt* on those paths — the file is present — but an executor reading the
   criterion will believe a repair happened that did not.

2. **`mktemp -d` does not guarantee the same volume as the workspace** (LOW, NEWLY
   RAISED, ACTIONABLE). On this host `$TMPDIR` resolves under `C:`, so `mv` is a
   rename, but Git Bash honours `TMPDIR`/`TEMP` configuration. If the temp dir lands
   on another volume, both `mv` calls become copy-then-delete, widening the window
   the trap exists to cover. The plan asserts the trap "outlives every statement
   that could fail" without pinning the volume that assumption depends on.

### Divergent Views

3. **`printf | grep -q` under `pipefail`** (Codex: MEDIUM, NEWLY RAISED, ACTIONABLE;
   orchestrator: **could not reproduce**). Codex argues that `grep -q` exits on first
   match, `printf` then hits a closed pipe, and `pipefail` propagates the failure,
   suppressing `FIXTURE_FAIL_OK` even though the text was found. The orchestrator
   tested exactly this shape under Git Bash 5.3.15 with the match placed at offset 0
   and payloads of 100 KB, 1 MB and 5 MB: `rc=0`, `PIPESTATUS=0 0` in every case —
   bash's **builtin** `printf` does not surface a broken pipe here, and the plan's
   criterion is run under Git Bash where `printf` is the builtin. The hazard is real
   in principle (an external `/usr/bin/printf`, or a different bash SIGPIPE
   disposition, would expose it) but does not materialise for the command as written
   on the host the plan names.

   It is still counted as actionable: the plan's own **Pipeline rule** section
   (`01-03-PLAN.md:160-165`) does not cover this shape, `$out` is already in a shell
   variable so the pipeline is avoidable, and the fix — a here-string
   (`grep -q '…' <<<"$out"`) or `case "$out" in *…*)` — is one token of work.

## Verification coverage

Source-grounded evidence checked this cycle, beyond the reviewer's own citations.

| Claim under test | Method | Result |
|---|---|---|
| `trap - EXIT INT TERM` unreachable from a failed inbound `mv` | Stand-in of `01-03-PLAN.md:510` with a shell function shadowing only the inbound `mv` direction, Git Bash 5.3.15(1) x86_64-pc-cygwin | Exits `1`, prints `RESTORE_FAILED_TRAP_ARMED`, trap fires, file restored. **Fail-closed confirmed.** |
| Trap recovers on all four guard paths | Read of the trap's guard condition against each abort state | **False** — no-op on re-hash-failed, hash-mismatch and `RESTORE_MISSING`. Finding 1. |
| `printf \| grep -q` fails under `pipefail` | Direct execution at 100 KB / 1 MB / 5 MB with the match at offset 0 | `rc=0`, `PIPESTATUS=0 0` at every size. **Not reproduced.** Finding 3 downgraded. |
| `grep -c` zero-match inside `$( )` yields `"0"` | Direct execution under `pipefail` | Prints `0`, substitution text `0`, assertion passes. Plan's reasoning at `:505` is correct. |
| `wc -l < file` is unpadded on this host | Direct execution | `[3]` — no padding, so `test "$(wc -l < …)" = "38"` is safe. |
| `demo.md` is not `//go:embed`-ed | `grep -rn "go:embed" internal/` | Only `store/migrate.go:14` (`migrations/*.sql`). Moving the fixture cannot break compilation, so scoping the run to the store package is sound. |
| Only `segmentation_test.go:276` reads the fixture cross-package | `grep -rn "demo.md" internal/ --include=*.go` | Confirmed; the other hits are `fixture_test.go:87` (in-package) and comments. |
| Escalated fixture message will match the plan's `grep` pattern | Read of `segmentation_test.go:278` (`t.Skipf("fixture not readable from here: %v", err)`) and 01-01's `Fixture` spec | The relative path is passed through verbatim, so forward slashes survive on Windows and `grep -q 'core/domain/segment/testdata/demo.md'` matches. Not a finding. |
| The fixture criterion needs a live DB (pool is acquired first) | Read of `01-03-PLAN.md:409` `<precondition>` | Already covered — the precondition requires `make up`, an exported `EPISTEMIC_OS_DB_URL` and `make migrate`. **Not actionable.** |
| 38 `testPool(t)` sites across 6 files | `grep -rn "testPool(t)" internal/ --include=*_test.go` | 38 across 6 files. Confirmed. |
