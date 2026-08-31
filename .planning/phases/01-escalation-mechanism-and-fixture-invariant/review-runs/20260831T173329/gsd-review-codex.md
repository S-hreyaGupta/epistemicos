# Cross-AI Plan Review

## Overall assessment

The phase decomposition is sound: Plan 01 creates the mechanism, Plan 02 protects content-conditional behavior, and Plan 03 measures non-enforcement before Phase 2 activates it. The proposed implementation aligns closely with the current code. The main weaknesses are in verification rather than design: several negative checks can pass without proving the intended failure branch, temporary fixture/source mutations are not specified safely enough, and Plan 03 contradicts itself about producing no file changes while requiring a summary artifact.

Overall phase risk: **MEDIUM**. The implementation is relatively small and well scoped, but the milestone exists specifically to eliminate vacuous proof, so weaknesses in its own verification deserve more weight than they normally would.

---

# Plan 01 — Shared escalation helper

## Summary

Plan 01 correctly identifies and consolidates the two duplicated database-environment decision points and the separate cross-package fixture skip. The proposed `testenv` package is a reasonable location, and the security treatment of connection strings improves on the current implementation. The direct conversion of all 38 tests is mechanically clear. Its largest gap is that the helper’s most important behavior—skip versus fatal—is deliberately left without automated unit-level coverage until Phase 3, while some shell-based negative checks do not robustly prove which branch executed.

## Strengths

- The duplication claim is accurate. The store helper reads the URL, skips when unset, and skips when `Ping` fails at [segmentation_test.go:23](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:23). The approved package has an independent version at [papers_test.go:24](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/approved/papers_test.go:24). Centralizing these removes a real policy split.

- The plan correctly distinguishes lazy pool construction from reachability. Both current helpers call `pgxpool.New` and then explicitly call `Ping`, as seen at [segmentation_test.go:34](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:34) and [segmentation_test.go:38](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:38). Retaining both steps is necessary.

- The 38-site conversion is consistent with the repository. Representative sites include [authorreturn_test.go:31](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/authorreturn_test.go:31), [runrejection_test.go:66](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/runrejection_test.go:66), [researchunit_test.go:66](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/researchunit_test.go:66), and [papers_test.go:93](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/approved/papers_test.go:93).

- Routing the fixture read is justified. It is currently a third environment-dependent skip, separate from either database helper, at [segmentation_test.go:276](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:276).

- Credential handling is materially better than the current code. Both existing helpers interpolate the `pgxpool.New` error directly into test output at [segmentation_test.go:35](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:35) and [papers_test.go:36](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/approved/papers_test.go:36). Replacing that with fixed parse-error text removes a real logging risk.

- The plan does not add a dependency. `pgx/v5` is already direct and there is no assertion library in [go.mod:5](C:/EpistemicOS/epistemicos-gsd-pilot/go.mod:5).

- Keeping `context` and `pgxpool` in `segmentation_test.go` is necessary even after deleting `testPool`: cleanup and test logic still use them at [segmentation_test.go:73](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:73). The plan appropriately tells the executor to let the compiler determine unused imports.

## Concerns

- **MEDIUM — The central skip/fail behavior is not directly unit-tested.** The plan tests `Required` and `hostFromURL`, but not `Pool` or the failure branch of `Fixture`. Those branches are the actual implementation of GATE-05. Deferring all process-level testing to Phase 3 leaves Plan 01 dependent on manually interpreted shell output.

- **MEDIUM — The credential canary checks do not always prove the failure branch ran.** A command such as:

  ```sh
  go test ... 2>&1 | grep -c PWLEAKCANARY
  ```

  proves only that the canary was absent. It can also produce zero if the test command unexpectedly succeeds, skips, or fails before reaching `Pool`. The malformed-DSN case especially needs an independent assertion that `go test` exited nonzero and emitted the fixed parse-error message.

- **MEDIUM — Appending the raw `Ping` error remains an avoidable disclosure dependency.** The plan assumes pgx reachability errors never contain credentials. `hostFromURL` safely limits the explicitly derived display host, but the appended error is outside that control. Current code already prints it at [segmentation_test.go:40](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:40), but centralizing the helper is a good opportunity to avoid relying on undocumented error formatting.

- **LOW — “All three environment conditions are decided in one package” needs tighter wording.** In-package fixture reads intentionally remain fatal through `loadFixture` at [fixture_test.go:84](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:84). The intended invariant is therefore “all current environment skips,” not all unreadable-fixture decisions throughout the repository.

- **LOW — `EPISTEMIC_OS_TEST_REQUIRE_DB` is semantically narrower than its behavior.** It controls an unreadable filesystem fixture as well as database availability. This is workable for the milestone, but a future reader may reasonably assume it affects only DB setup.

- **LOW — Presence-based flag semantics are defensible but surprising.** Treating `0` and `false` as enabled is intentionally fail-closed, but it should be very prominent once Phase 2 exposes the flag through `make gate`.

## Suggestions

- Add a tiny subprocess test harness in `testenv_test.go` now, or at least in this phase, to run helper tests under controlled environment variables and assert exit status plus message. This would test `Pool` and `Fixture` without attempting to manufacture a `testing.T`.

- Capture command output and exit status separately for every negative scenario. Assert all three:

  1. the test process exits nonzero;
  2. the expected cause text is present;
  3. the credential canary is absent.

- Prefer emitting the sanitized host plus a stable error category for `Ping`, rather than appending the complete pgx error. If detailed error retention is required, add a test against more than one DSN form, including keyword/value DSNs.

- Rewrite the success criterion as: “One package owns every skip-or-fail decision that was an environment skip at the phase base.”

- Consider a broader name such as `EPISTEMIC_OS_TEST_REQUIRE_ENV`, or explicitly document that `REQUIRE_DB` also escalates the cross-package fixture prerequisite.

## Risk Assessment

**MEDIUM.** The source refactor is straightforward and well bounded, but the phase’s core behavior is validated mostly through shell scenarios whose exit status can be masked. The remaining credential dependency on pgx error rendering also merits attention.

---

# Plan 02 — Fixture invariant and AC-14 preservation

## Summary

Plan 02 correctly strengthens the existing hash-pinned fixture test rather than changing the content-conditional skips. This is the right separation of responsibility: the pinned project fixture must exercise AC-14, while the acceptance test retains the ability to decline for other legitimate inputs. The implementation is small and source-aligned. The main concerns are an unsafe negative-proof procedure and unnecessarily elaborate failure-message requirements.

## Strengths

- `TestFixtureIntegrity` is the correct home for the invariant. It already obtains the fixture through `loadFixture`, which verifies both byte length and SHA-256 at [fixture_test.go:87](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:87), [fixture_test.go:92](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:92), and [fixture_test.go:96](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:96).

- The plan correctly avoids relying on test ordering. The existing integrity test is independent at [fixture_test.go:128](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:128), and Go provides no guarantee that the heading-count test at [fixture_test.go:148](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:148) runs first.

- Checking for an empty heading slice before indexing is sound defensive handling. The AC-14 test currently indexes `headings[0]` directly at [acceptance_test.go:434](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:434).

- The invariant uses the same mechanism as AC-14. `detectHeadings` records `h.Pos()` as `ByteStart` at [headings.go:148](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/headings.go:148) and [headings.go:163](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/headings.go:163), while AC-14 uses the first detected `ByteStart` at [acceptance_test.go:435](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:435). The two checks therefore genuinely line up.

- Preserving the two skips is correct. They represent two separate content conditions at [acceptance_test.go:437](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:437) and [acceptance_test.go:449](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:449).

- The plan prevents the tempting but wrong change of converting the skips into failures. That directly supports GATE-04.

## Concerns

- **MEDIUM — The negative proof modifies the real source file without a precise restoration mechanism.** “Temporarily edit a working copy” and then “discard the edit” is underspecified when the same file already contains intended uncommitted changes. A blanket checkout could erase the implementation; an imprecise reverse edit could leave test code corrupted.

- **MEDIUM — `git diff --stat` cannot prove the temporary mutation was fully restored.** Since `fixture_test.go` is intentionally modified by the plan, a stat showing only that file does not distinguish the intended edit from a lingering negative-test mutation.

- **LOW — Failure-message requirements are over-specified.** Requiring both constants to be named, the discovered offset to be printed, the filename to be named, and regeneration rationale to appear in every branch adds noise without materially improving diagnosis. The hash and length failures already name exact mismatches at [fixture_test.go:92](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:92).

- **LOW — The empty-heading guard protects only `TestFixtureIntegrity`.** AC-14 itself still assumes at least one heading at [acceptance_test.go:435](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/acceptance_test.go:435). Hash pinning makes this safe for the current fixture, but if the fixture and pins are deliberately updated together, AC-14 could panic rather than skip or fail clearly.

- **LOW — “Green and silent” is interpreted as PASS for the current fixture.** That is appropriate for the pinned fixture, but the plan should distinguish it from the more general GATE-04 behavior, under which a genuinely preamble-free fixture would produce SKIP rather than PASS.

## Suggestions

- Implement the negative proof using a generated temporary test file or a temporary copy of the package, rather than editing tracked source in place.

- If tracked-source mutation is unavoidable, save the exact pre-mutation file hash and restore through a narrowly targeted reverse patch; assert that the final hash equals the pre-mutation hash.

- Simplify invariant failures to stable, actionable messages, for example:

  - `testdata/demo.md: no headings detected`
  - `testdata/demo.md: first heading starts at byte 0; AC-14 requires a non-whitespace preamble`
  - `testdata/demo.md: bytes [0,N) are whitespace only`

- Consider adding an empty-heading guard to AC-14 itself. It could fail clearly because a fixture with no headings cannot exercise the criterion at all.

## Risk Assessment

**LOW to MEDIUM.** The actual code change is small and correctly located. Risk comes primarily from the executor’s proposed mutation-based negative proof, not from the invariant itself.

---

# Plan 03 — Non-enforcement audit

## Summary

Plan 03 asks the right behavioral questions: default green without PostgreSQL, escalated green with PostgreSQL, named failures for all three broken prerequisites, credential non-disclosure, and an unchanged gate. This is exactly the matrix needed before enforcement lands. However, its verification mechanics contain several contradictions and opportunities for false positives. Because this is the phase’s evidence-producing plan, those issues should be fixed before execution.

## Strengths

- The two-environment gate comparison is appropriate. The current gate only vets, formats, builds, and tests at [Makefile:38](C:/EpistemicOS/epistemicos-gsd-pilot/Makefile:38); it neither starts PostgreSQL nor sets enforcement.

- The live-database precondition is grounded in actual targets. `make up` starts PostgreSQL and waits for readiness at [Makefile:18](C:/EpistemicOS/epistemicos-gsd-pilot/Makefile:18), while `make migrate` invokes the CLI migration path at [Makefile:47](C:/EpistemicOS/epistemicos-gsd-pilot/Makefile:47).

- The migration assumption is correct. Store migrations are embedded and applied through `RunMigrations` at [migrate.go:14](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/migrate.go:14) and [migrate.go:24](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/migrate.go:24).

- The CI baseline is accurately described. CI provisions PostgreSQL at [ci.yml:18](C:/EpistemicOS/epistemicos-gsd-pilot/.github/workflows/ci.yml:18), exports the URL at [ci.yml:33](C:/EpistemicOS/epistemicos-gsd-pilot/.github/workflows/ci.yml:33), and applies migrations at [ci.yml:67](C:/EpistemicOS/epistemicos-gsd-pilot/.github/workflows/ci.yml:67).

- The escalated-green scenario is essential and well motivated. Negative-only testing could be satisfied by a helper that always fails; requiring the packages to pass with zero skips closes that loophole.

- The fixture failure must be tested after obtaining a live pool because the fixture read occurs after `testPool(t)` at [segmentation_test.go:272](C:/EpistemicOS/epistemicos-gsd-pilot/internal/adapters/secondary/store/segmentation_test.go:272). The plan correctly recognizes this dependency.

- The recorded base commit exists and is an ancestor of the current repository state, so the proposed audit range is presently valid.

## Concerns

- **HIGH — Several pipelines can mask the `go test` exit status.** Commands of the form:

  ```sh
  go test ... 2>&1 | grep -c ...
  ```

  report the status of `grep`, not necessarily the test process, unless `pipefail` is enabled. A test crash, setup failure, unexpected success, or zero-test run can therefore satisfy parts of the matrix.

- **HIGH — The unreadable-fixture procedure does not specify an actually unconditional restore.** The plan says restoration must happen regardless of test result, but gives no concrete `trap`/`finally` mechanism. This is material because the target file is the hash-pinned fixture read at [fixture_test.go:87](C:/EpistemicOS/epistemicos-gsd-pilot/internal/core/domain/segment/fixture_test.go:87).

- **MEDIUM — The plan claims `files_modified: []` but requires creating `01-03-SUMMARY.md`.** It also lists that summary as an artifact. Either `.planning/.../01-03-SUMMARY.md` must appear in `files_modified`, or the plan should explicitly distinguish source files from generated planning artifacts.

- **MEDIUM — The final clean-status criterion conflicts with creating the summary.** Once `01-03-SUMMARY.md` is written, `git status --porcelain` cannot show only the pre-existing `.planning/config.json` unless the workflow commits the summary before running that check. The ordering needs to be explicit.

- **MEDIUM — The malformed-DSN canary again checks only absence of the password.** It does not require a nonzero test exit or the stable parse-error text. That permits a vacuous pass—the exact class of problem this milestone is intended to eliminate.

- **MEDIUM — The verification commands are POSIX-specific in a Windows workspace.** They use `env -u`, `export`, `test`, `grep`, and `&&`, while the active repository environment is PowerShell. This may be fine if the execution workflow explicitly launches Git Bash or WSL, but the plan does not say so. The commands are not directly runnable in the current shell.

- **LOW — Counting at least 38 `PASS` lines is only an indirect execution proof.** It does not establish a one-to-one correspondence with the former database call sites, particularly if packages contain subtests. Explicit test-name enumeration or JSON output would be stronger.

- **LOW — Stopping the shared compose database is a local side effect.** It is within the verification scope, but the plan should state the final desired service state. Task 3 currently brings it back up, leaving a running service even if it was originally stopped.

- **LOW — The generic E1–E4 probe edges add noise.** Adjacency and ordering have no meaningful mapping to this test-harness change. Carrying them through every plan consumes review attention without improving coverage.

## Suggestions

- Capture each test run once:

  ```sh
  set +e
  output=$(go test ... 2>&1)
  status=$?
  set -e
  ```

  Then independently assert `status != 0`, expected cause text is present, and password text is absent. Enable `set -o pipefail` where pipelines remain.

- For unreadable-fixture verification, use an explicit `trap` in POSIX shell or `try/finally` in PowerShell. Record the original file hash before moving and verify the same hash after restoration.

- Add `.planning/phases/.../01-03-SUMMARY.md` to `files_modified`, and define whether summaries are committed between plans.

- Move the clean-status check before summary creation, or allow the new summary path in the expected status result.

- Use `go test -json` to count database test starts, skips, and failures reliably. This avoids fragile matching against human-formatted `-v` output.

- State the required shell explicitly. If execution occurs in PowerShell, translate the commands; if it requires Bash, invoke Bash explicitly.

- Replace the four irrelevant generic probe edges with a short disposition now: E1, E2, and E4 are inapplicable; E3 maps to empty flag/empty host and is already covered.

## Risk Assessment

**MEDIUM to HIGH.** The intended behavioral matrix is excellent, but its evidence collection can currently pass vacuously or leave the fixture displaced after an interruption. Those are serious defects for a plan whose sole purpose is to establish trustworthy proof.

---

# Final recommendations

Before executing the phase:

1. Make every negative scenario assert process status, expected cause, and credential absence independently.
2. Add an unconditional, hash-verified restoration mechanism for all temporary file mutations.
3. Resolve Plan 03’s summary/status and `files_modified` contradictions.
4. Specify the execution shell.
5. Prefer `go test -json` over parsing verbose display text.
6. Add process-level helper coverage earlier if practical, so Plan 01 itself proves the skip/fail mechanism it introduces.

With those changes, the phase should achieve its stated goal without expanding scope or altering `make gate` prematurely.
