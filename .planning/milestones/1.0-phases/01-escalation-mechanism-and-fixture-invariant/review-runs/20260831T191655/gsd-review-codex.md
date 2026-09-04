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
