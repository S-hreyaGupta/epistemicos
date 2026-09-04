---
gsd_state_version: 1.0
status: Awaiting next milestone
stopped_at: Milestone complete — all three phases done, close sweep terminated, deferred item 2 decided
last_updated: "2026-09-04T06:51:49.736Z"
last_activity: 2026-09-04
last_activity_desc: Milestone 1.0 completed and archived
state_head: 99040c2eafde8857e3cd5539da80d303fee0dc69
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 11
  completed_plans: 11
  percent: 100
current_phase: 03
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-30)

**Core value:** `make gate` must be able to distinguish "tested and passed" from "tested nothing".
**Current focus:** v1.0 (Gate-Hardening) shipped 2026-09-04. Awaiting `/gsd-new-milestone`.

## Current Position

Phase: Milestone 1.0 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-09-04 — Milestone 1.0 completed and archived

## Performance Metrics

**Velocity:**

- Total plans completed: 9
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 3 | - | - |
| 03 | 6 | - | - |

**Recent Trend:**

- Last 5 plans: —
- Trend: —

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P02 | 15 min | 2 tasks | 1 files |
| Phase 01 P01 | 48min | 3 tasks | 8 files |
| Phase 01 P03 | 62min | 3 tasks | 1 files |
| Phase 02 P01 | 21 min | 3 tasks | 3 files |
| Phase 02 P03 | 7 min | 3 tasks | 4 files |
| Phase 02 P02 | 8min | 3 tasks | 4 files |
| Phase 03 P01 | 55 min | 3 tasks | 4 files |
| Phase 03 P02 | 50min | 3 tasks | 2 files |
| Phase 03 P03 | 55 min | 2 tasks | 1 files |
| Phase 03 P04 | 55 min | 3 tasks | 4 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Pre-phase: Only environment skips fail the gate; content-conditional skips stay green. The preamble property is proven as a fixture invariant in `TestFixtureIntegrity`, where `demo.md` is already hash-pinned — this satisfies both the requirement that the property hold and the requirement that content skips not be a gate failure class.
- Pre-phase: Three phases, not two. A gate that asserts it fails correctly, without a test proving it fails correctly, would be self-refuting.
- Pre-phase: CI provisions Postgres inside this milestone rather than after it, because a hard-failing gate turns CI red immediately.
- Phase 1 (2026-09-01): **GATE-04's byte-identical constraint on `acceptance_test.go` was Phase 1 scope only, not a standing requirement.** GATE-04 in REQUIREMENTS.md says only that content-conditional skips stay green and silent; the words "byte-identical" appear in no requirement, only in the Phase 1 plans, anchored to phase base `868d45b`. Confirmed at Alex's instruction during Phase 1 UAT rather than assumed. Phase 2 onward **may** add the AC-14 empty-heading guard, and doing so furthers GATE-04 rather than conflicting with it — a panic is neither green nor silent. Deferred to backlog with a hard gate: it must close before Phase 3.
- Phase 1 (2026-09-01): the test-env package is `internal/platform/testenv`, specified in the plan from `940727c` and named in the review-of-record `d90b10d`. Any memory of `internal/platform/dbtest` traces to a ~142-line `dbtest.go` written before the plan existed and deleted before it ran — never committed, absent from every artifact. No rename occurred; do not re-raise it as a deviation.
- Phase 1 (2026-09-01): the phase base is `868d45b`, approved by Alex Zamurko. It is the commit that modified `.github/workflows/ci.yml` and the last commit on this branch to touch either gate file, so the change sits *at* the anchor rather than behind it, and every commit after it is a `.planning/` commit from this phase's own planning loop. `030521b` — the base cycle-1 convergence substituted in without approval — was **rejected**: all four anchor properties hold at it and its source tree is byte-identical to `868d45b`'s, but it is a commit the review process wrote 23 seconds after the review that demanded the re-anchor, so anchoring the phase to it would be circular. The `fcebad1` → `030521b` substitution stays recorded as it happened: recorded, not halted, not approved.
- Phase 1: `d90b10d` (`01-PLAN-MANIFEST.json`, pinning the three plans at `940727c`) is the **review-of-record** — the exact byte state Alex reviewed, with findings written and recorded outside this repository. Convergence will rewrite the plans, superseding it. **Do not delete or edit it.** It is deliberately left unannotated: retroactively marking it would alter the artifact whose value is being an unaltered record of what was reviewed. The post-convergence manifest carries the supersession instead, via a `supersedes: d90b10d` field pointing back.
- [Phase 01]: The preamble property is asserted once in TestFixtureIntegrity against the hash-pinned fixture (via a pure preambleInvariant function), not re-derived per-run in acceptance_test.go, keeping AC-14's two content-conditional t.Skip calls green and silent instead of a gate failure class.
- [Phase 01]: fixtureHasPreamble is a pinned constant (declared true), not a runtime skip, so a genuinely preamble-free fixture must be declared in the same diff that repins the hash and length; the negative proof (TestPreambleInvariant_Control) drives the function with synthetic inputs, retiring the mutate-and-restore pattern flagged in cycle-1 review.
- [Phase 01]: 01-01: internal/platform/testenv replaces both duplicated pool helpers; all 38 call sites across 6 files now call testenv.Pool(t) directly, and the cross-package fixture read goes through testenv.Fixture(t, path). Escalation via EPISTEMIC_OS_TEST_REQUIRE_DB is opt-in and unwired in this plan; escalation off reproduces the phase-base baseline exactly (exit 0, 38 skips, unchanged under -shuffle=on).
- [Phase 01]: 01-01: unparseableURLMsg is an argument-free string constant (built by compile-time concatenation, not Sprintf), so no DSN-derived value can reach the parse-failure branch; verified against the phase base to fail (leak-token count 1) and after this change to pass (count 0) on both a URL-form and a keyword/value-form malformed DSN.
- [Phase 01]: Phase 1 (01-03): make gate is measured green with the compose database genuinely stopped and again with it running, database left running as declared; escalated run executes all 38 baseline-skipping tests by name (set containment) and skips zero (independent count); a DSN leak token measured present (count 1) at the phase base is absent (count 0) after the escalation mechanism. — This is the phase's central claim, measured rather than argued, and the baseline Phase 2 and Phase 3 will diff/assert against.
- [Phase 01]: 01-03: make was not installed on this host and the plan's own execution_shell.verified_present list never checked for it, despite 29+ commands depending on it. Execution halted; operator Alex approved and performed the install (GNU Make 4.4.1 / ezwinports.make); execution resumed with no plan/manifest edits. — Recorded for end-of-phase disposition as a planning-process gap, not fixed by editing the frozen plan.
- [Phase 2]: [Phase 02] 02-01: testenv.RequireEnv renamed to EPISTEMIC_OS_TEST_REQUIRE_ENV (identifier unchanged); escalationPreamble() is the one message builder all three escalated t.Fatalf sites use; renameTripwireMsg() permanently guards the old EPISTEMIC_OS_TEST_REQUIRE_DB name, checked first in both Pool and Fixture.
- [Phase 2]: [Phase 02] 02-01: make gate reshaped to vet -> gofmt -> build -> $(MAKE) env-preflight -> $(MAKE) migrate -> $(MAKE) test, target-scoped export EPISTEMIC_OS_TEST_REQUIRE_ENV=make-gate on the gate target (D-11) — measured to override a conflicting caller-set value, which corrected Task 2 step 5a's verify-script literal from gate03 to make-gate (see 02-01-SUMMARY.md Deviations).
- [Phase 2]: [Phase 02] 02-03: docker-compose.yml postgres bound to 127.0.0.1:5432:5432 (declared and live, container recreated) closing AR-02/T-01-11; ci.yml go job collapsed to a single make gate step, preserving services: postgres and job-level EPISTEMIC_OS_DB_URL (CI-01).
- [Phase 2]: [Phase 02] 02-03: headingGuardMessage(headings, fixturePath) added as GATE-09's length guard, wired at acceptance_test.go's one unguarded headings[0] index; TestGATE09_HeadingGuard_Control proves the branch executes (11 subtests) with a negative control that defeats the guard in a throwaway git-archive copy and requires the control to then fail. fixtureHasPreamble remains the package's only declaration mechanism.
- [Phase 2]: [Phase 02] 02-03: plan verify-script literal corrected — the fixtureHasPreamble declaration-count regex did not account for the const keyword prefix (const fixtureHasPreamble = true); corrected to ^[[:space:]]*(const|var)[[:space:]]+fixtureHasPreamble[[:space:]]*= , same substance, no code change.
- [Phase 2]: [Phase 2] 02-02: internal/platform/gate shell-out-to-make harness (Run/Make/RunOptions/RunResult/SkipIfNested/RepoRoot) built and confirmed at a human checkpoint (proceed) as Phase 3's PROOF-01/02/03 contract; depth marker recursion guard set last in buildChildEnv so Unset/Env cannot defeat it.
- [Phase 2]: [Phase 2] 02-02: TestEnvPreflightIsVoiceless (D-03) and TestMakeTestPrintsLenientBanner (D-05) assert against real subprocess output via extraLines' differential comparison, not Makefile text; ROADMAP.md Phase 3 gains a Note on the harness (D-07 binding condition 2) with Goal/Depends on/Requirements/Success Criteria byte-unchanged.
- [Phase 03]: 03-01: Tree materialisation uses git archive --format=tar HEAD piped through Go stdlib archive/tar, not git worktree add and not an external tar binary — no build-host dependency, nothing left in .git, go.mod/go.sum byte-unchanged.
- [Phase 03]: 03-01: Proof and SC-5 control are two subtests of one top-level test function sharing a captured RunResult in the parent scope, so ordering is guaranteed under -shuffle=on and the D-16 guard has a genuinely trippable failing path.
- [Phase 03]: 03-01: Both intact_tree and defeated_tree_control unset testenv.RequireEnv in addition to testenv.URLEnv (deviation from literal plan text, applied identically to both sides) — found running the real make gate, where the outer gate's own target-scoped export was leaking through ambient environment inheritance and defeating the SC-5 differential.
- [Phase 03]: [Phase 03]: 03-02: PROOF-02's SC-5 control deliberately asserts nothing about golang-migrate's own 'new migrator' reporter text — that is a dependency's prose, and PROOF-01's control asserting config's own message does not transfer to a condition where the reporter is not this project's code (D-15).
- [Phase 03]: [Phase 03]: 03-02: TestGateOrdersPreflightBeforeMigrate carries D-03's ordering claim structurally against make -n gate's dry-run expansion (not the Makefile's raw text), performs no nested make gate, and is demonstrated to fail when the two recipe lines are transposed in a materializeTree copy — the other independent leg is PROOF-02's D-02b in-run observation.
- [Phase 03]: /gsd-plan-phase 3: the planner's contributions were passed to the orchestrator as a file reference rather than inlined, an orchestrator-side deviation from the workflow's literal dispatch contract, declared in conversation only until now.
- [Phase 03]: /gsd-execute-phase 3: the execute-plan.md/summary.md/checkpoints.md/tdd.md/executor-examples.md protocol bundle (~103KB) was passed to each gsd-executor dispatch via a `<required_reading>` block with absolute paths rather than inlined verbatim as the workflow specifies, to keep orchestrator context near its ~15% budget across four dispatches; gsd-executor's own mandatory-initial-read rule still forces the Read before any other action, so the content reaches the executor through an enforced path rather than a silent `@`-include. Declared in conversation only until now.
- [Phase 03]: 2026-09-03: a real Anthropic incident affecting Opus 5 was confirmed at ~13:26 UTC (external status reports); the user set Sonnet 5 as their session default at 19:48 IST. No mid-session model switch for this orchestrator is asserted or verified — the `/model` output itself scopes the change to new sessions, and this session's own context was unchanged at the time of recording.
- [Phase 03]: [Phase 03]: 03-03: PROOF-03 and its SC-5 control both unset testenv.RequireEnv (deviation from literal plan text, carried forward from 03-01/03-02's identical finding) — the outer make gate's own target-scoped export leaks into the ambient environment of any nested gate.Run call that does not explicitly unset it, defeating the SC-5 differential for a reason unrelated to the stripped export. Found running the real make gate, not the isolated go test.
- [Phase 03]: [Phase 03]: 03-03: GATE-10 stays Pending after PROOF-03 lands — 03-04-PLAN.md also declares GATE-10 in its own requirements frontmatter and has not yet produced a SUMMARY, so the shared-ID gate (#2388) blocks marking it complete until the last declaring plan finishes, even though all three escalated paths (PROOF-01/02/03) are now proven.
- [Phase 03]: OPEN, not a finding — `harness.go`'s `DefaultTimeout` cold-case rationale (85s worst-observed child, 2.8x margin under the 4-minute bound) is unverified against current reality. Warm case measured 16.59s uncontended on 2026-09-03 (`TestPROOF01_GateNamesUnsetURL/intact_tree`, isolated, real repo root, go test's own per-test line, not shell wall-clock) and is consistent with the comment's own stated warm range (11s/9s/21s). Cold case (fresh GOCACHE) not re-tested — the user declined the GOCACHE flush needed to measure it, on the reasoning that nothing observed tonight contradicts the existing number and repopulating the cache afterward costs every subsequent build. Not disproven, not reconfirmed. Revisit if a genuine cold start (fresh CI runner, fresh clone) ever produces a number inconsistent with 85s/2.8x.
- [Phase 03]: Phase 3 (2026-09-03): GATE-10's checkbox and traceability row are marked Complete by 03-04, per the orchestrator's explicit instruction closing a scope gap between 03-03's deferral (which named 03-04 as the plan that would close it) and 03-04-PLAN.md's own narrower verification-only text -- confirmed safe by the shared-ID gate (requirements.ready-ids returning GATE-10 ready) and by re-running make gate green.
- [Phase 03]: Phase 3 (2026-09-03): No correction was needed to GATE-10's REQUIREMENTS.md entry or ROADMAP's SC-5 correction block on verification against D-19/D-12's stated obligations; both already carried everything required.
- [Phase 03]: Phase 3 (2026-09-03): D-21's correction of 13071ff's wrong phase-completion diagnosis was given a durable, single-writer home at 03-FINDING-01-phase-completion-diagnosis.md, with a pointer left in STATE.md, because STATE.md's own accuracy has a registered expiry (FINDING-01).

### Pending Todos

Added by the GOV-01 close sweep (`02-GOV-SWEEP.md` Task 3), so these travel rather
than living only inside a closed phase's plans:

- **Two still-open contract decisions from 01-03** (of the original five queued):
  the `internal/platform/testenv` package path/API, and
  `EPISTEMIC_OS_TEST_REQUIRE_DB`'s presence-based semantics — both **unchanged by
  Phase 2** and carried forward with no disposition needed beyond "still true as
  designed." (The other three — the flag's wider-than-its-name scope, the
  README/Makefile documentation deferral, and the AC-14 empty-heading guard — are
  RESOLVED, by GATE-07, GATE-08 and GATE-09 respectively; see `02-GOV-SWEEP.md`
  Task 3 for the full disposition.)

- **Three unclassified probe-edge rows**, none dismissed because no agent in this
  pipeline has authority to dismiss a probe row that returned no category:

  - **E1** (Phase 1, GATE-04) — queued in `01-03` Task 3, still open; covered by
    pointer per `01-UAT.md` test 5's disposition (six `TestPreambleInvariant_Control`
    subtests plus ten authored must-haves), not independently resolved.

  - **E11** (Phase 2, GATE-07) — unclassified; GATE-07's substance is covered by
    `02-01`'s authored must-haves and `02-VERIFICATION.md` Criterion 7.

  - **E12** (Phase 2, CI-02) — unclassified; CI-02's substance is covered by
    `02-03`'s authored must-haves and `02-VERIFICATION.md` Criteria 4/5.
  See `02-GOV-SWEEP.md` Task 3 for the full disposition record.

- **Three items carried from `03-CONTEXT.md`'s `<deferred>` section (items 3, 4, 5), none
  resolved by Phase 3, each with a pointer so they travel if the phase is rescoped:**

  - **(3) The class of measured/descriptive claims in code files outside `.planning/` that
    go stale and are invisible to GOV-01's derivation.** Two demonstrated instances:
    `.github/workflows/ci.yml`'s job name `vet + test + fmt`, stale after CI-02 collapsed it
    to one `make gate` step, found by a human running Phase 2 UAT test 12; and
    `internal/platform/gate/harness.go`'s `DefaultTimeout` rationale, warm-figure claims
    stale against the measured cold worst case (85s, 2.8x margin), found by a cold-cache
    measurement during Phase 3's discussion. **Neither was found by a sweep; both were found
    by someone running something.** Pointer: `03-CONTEXT.md` `<deferred>` item 3.

  - **(4) SC-5's literal wording is unreachable through the harness, by design.**
    `buildChildEnv` sets `DepthEnv` last and skips any entry naming it, so a control
    spawning the proof package hands it depth 1 and every proof `SkipIfNested`-skips — three
    skips and a green run, a vacuous pass inside the mechanism built to remove vacuous
    passes. D-12 corrects the ROADMAP criterion and D-11 supplies what is provable instead;
    this item preserves *why* the original wording could not stand, so the correction is not
    later mistaken for a weakening. Pointer: `03-CONTEXT.md` `<deferred>` item 4.

  - **(5) D-21's scope** — the registered finding that named SUMMARY-to-PLAN pairing as the
    (wrong) cause of the phase-completion undercount; the operating mechanism is
    `verification.cjs`'s `#2348` staleness rule plus `isPhaseComplete`'s
    `status === 'passed'` check. **Closed by this phase**, not merely carried: see
    `03-FINDING-01-phase-completion-diagnosis.md` for the full correction. Pointer:
    `03-CONTEXT.md` `<deferred>` item 5.

### Blockers/Concerns

- Phase 3 carries an open design question, recorded at PROJECT.md lines 91-93: a negative test asserting "the gate fails when `EPISTEMIC_OS_DB_URL` is unset" has to run inside the suite the gate governs, in an environment where that variable is set. **Amended by the GOV-01 close sweep, 2026-09-02 (not deleted — Phase 3's success criterion 4 still requires the tension to be solved *in Phase 3's plan*):** Phase 2's 02-02 supplied a slice of the answer rather than the whole one. It built `internal/platform/gate` (`Run`/`Make`/`RunOptions`/`RunResult`/`SkipIfNested`/`RepoRoot`/`DepthEnv`/`DefaultTimeout`) as a shell-out-to-`make` harness, confirmed at a human checkpoint as Phase 3's PROOF-01/02/03 contract, with a bounded recursion guard (`EPISTEMIC_OS_TEST_MAKE_DEPTH`, incremented last so `Unset`/`Env` cannot defeat it) so a proof that shells out to `make gate` from inside the suite `make gate` governs does not loop. ROADMAP.md §Phase 3 carries a "Note on the harness" recording this slice and pointing at the three `RunOptions` shapes PROOF-01/02/03 map onto. **What Phase 3 still has to solve:** the harness makes the recursive shell-out *safe*; it does not by itself decide how each proof arranges an environment where `EPISTEMIC_OS_DB_URL` IS set for the outer suite while being unset/unreachable/fixture-broken for the inner `make gate` call — that composition is Phase 3's own plan's job, per its Note on the harness and success criterion 4. **RESOLVED, 2026-09-04, Phase 3 close:** each proof composed its own environment via `gate.RunOptions.Unset`/`Env` per the three shapes the harness Note specified — `Unset: [EPISTEMIC_OS_DB_URL]` for PROOF-01, a closed-port DSN in `Env` for PROOF-02, a broken fixture inside a `materializeTree` copy for PROOF-03 — while the outer suite kept `EPISTEMIC_OS_DB_URL` set throughout. Verified live: all three proofs run inside `make gate`'s own governed suite (`03-VERIFICATION.md`, criterion 4). No longer a blocker.
- `.planning/config.json` is untracked. `cmdConfigNewProject` refuses to overwrite an existing config, so it is protected from regeneration only while the file stays in place.
- **After any `/gsd-update`, re-check that `.claude/gsd-core/workflows/review.md` still contains the run-directory archive block before the `rm -rf`.** The block is hand-added instrumentation in a GSD-managed file, so an update reverts it silently — and a capture that stops happening without saying so is the same failure class the archive exists to catch. Added under GSD 1.11.0; each archive records the version that produced it in `_INSTRUMENTATION.txt`.
- **The instrumentation itself is not in version control.** `.gitignore:29` ignores `.claude/`, so the archive block lives only on disk in this worktree. Its *output* under `.planning/phases/*/review-runs/` is tracked and survives, but the mechanism does not: recreating this worktree, or the runbook removing it, takes the block with it and later reviews would then discard their run dirs silently. Re-applying it is a manual step with no reminder attached.
- 01-02's whole-tree git-diff acceptance criteria (unrestricted 'git diff --name-only 868d45b --') print 47 files, not the expected single fixture_test.go, because ~29 pre-existing .planning/-only commits (base re-anchor, plan re-freeze, review-run archives) already sit between the phase base and execution start. The internal/-scoped form of the same check still confirms exactly one source file changed. Likely affects 01-01 and 01-03's identical whole-tree-diff criteria too — flag before running them.
- 01-03: five contract decisions (testenv package path/API, EPISTEMIC_OS_TEST_REQUIRE_DB semantics, the flag's wider-than-its-name scope, README/Makefile documentation deferral, the deferred AC-14 empty-heading guard) plus unresolved probe edge E1 are queued for the developer's end-of-phase disposition. The preamble policy (option C) is already RESOLVED 2026-09-01 by Alex and is not among these five.

### Blockers/Concerns — added 2026-09-04

- **Third same-night reproduction of the frontmatter-corruption class, this time mid-`transition.md`.** Between two `Read`s of this file during `transition.md`'s post-processing (evolve_project → the STATE.md steps), an automated write reverted `completed_phases` 3→2 and `percent` 100→67 again — the identical regression already corrected once at `d7619ca` — and additionally introduced a brand-new field, `current_phase_name: "**COMPLETE**. All three milestone phases   are now"`, a garbled fragment that reads as markdown bold syntax and a partial sentence lifted from this file's own "Current Position" body text, not a value any writer should have derived. `state_head` was the one field correctly advanced (to `ca1cf08`, the true current HEAD) — confirming *something* ran `state.sync`-shaped logic in the background, partially correctly, while corrupting the rest. Caught only because the `Edit` tool itself warned "the file had been modified on disk since you last read it" immediately after a routine edit; `git diff` against the last commit was checked before any further blind edit was made, per this session's own standing rule not to trust a STATE.md write without verifying it. Corrected by hand in the same pass: `completed_phases: 3`, `percent: 100`, `current_phase_name` removed entirely (it was never part of this file's schema before this write introduced it), `stopped_at`/Session Continuity's stale "context exhaustion" text replaced with the actual completed state. **No further `gsd_run query state.*` calls were made for the remainder of this task after this was found**, to stop feeding whatever background writer is doing this. Not diagnosed to a specific call site — unlike the prior two instances (`13071ff`'s wrong diagnosis, then `phase.complete`'s confirmed gap), this one's trigger is unknown; recorded as a third occurrence of FINDING-01's named class rather than as a fourth wrong-mechanism guess.

- **`/gsd-execute-plan <path>` — the command this project's own tooling instructs an operator to run at the last step of every milestone — does not exist.** Found trying to invoke it exactly as directed: `03-GOV-SWEEP-RUNBOOK.md`'s own frontmatter comment says *"Run it explicitly, after verification, UAT and security sign-off: `/gsd-execute-plan .planning/phases/03-automated-proof/03-GOV-SWEEP-RUNBOOK.md`"*, and this file's own since-corrected Session Continuity section carried the identical invocation for `02-GOV-SWEEP-RUNBOOK.md` at Phase 2's close. Checked `.claude/commands/` (every real slash command GSD installs) and `.claude/gsd-core/workflows/` directly: no `gsd-execute-plan.md` exists in either. The only command referencing the underlying `execute-plan.md` workflow file at all is `gsd-execute-phase.md`, which loads it internally per-wave-plan — it is not a user-invokable "run one plan by path" command, and no such command exists anywhere in this installation. **This is a documented invocation that has never worked, sitting at the single most load-bearing step of every milestone's close** — the sweep this project's own GOV-01 requirement depends on to catch exactly this class of drift. Confirmed how Phase 2's sweep actually ran despite the broken instruction: `git log f2794e4` (Task 1 of that same runbook shape) shows per-task atomic commits in the executor's own commit style, with no slash-command trace — meaning it was run the same way every numbered `03-0X-PLAN.md` in this phase was run tonight: a `gsd-executor` agent dispatched directly against the file path, following `execute-plan.md`'s workflow, bypassing wave scheduling because the runbook's own filename (not ending `-PLAN.md`) already keeps `plan-scan.cjs` from touching it. The real mechanism has always been direct executor dispatch, not a documented command — and nothing in either runbook's own text, or this file's prior Session Continuity sections, ever named that mechanism; both pointed an operator at a command that 404s. Not filed as a new FINDING document — recorded here as the measurement, in this file, at the moment it was caught, so the next milestone's close doesn't rediscover it the same way.

- **`phase.complete`'s automated STATE.md write produced a contradictory, partially-spliced
  frontmatter and body at the milestone's final phase transition.** Measured directly, not
  described: frontmatter read `completed_phases: 2` while `phase.complete`'s own JSON output for
  this same call reported `"is_last_phase": true` — meaning all three phases (01, 02, 03) were now
  complete and the field should have read 3. The same write set `percent: 67` in frontmatter while
  the body's own rendered `Progress: [███░░░░░░░] 33%` bar disagreed with it internally, and both
  were wrong regardless (should have been 100% by either the phase-fraction or plan-fraction
  formula). The `status:` field was left at `planning` — untouched by the write entirely, even
  though the phase it names as current had just been marked complete. Most seriously, the "Current
  Position" body section was not regenerated to reflect the new state: it still read "Plan: Not
  started" and a "**Next:** Phase 3 (Automated Proof) — ... not yet planned" block instructing a
  future planner on pre-planning context for a phase that had been fully executed, reviewed,
  secured, and verified hours earlier — and mid-paragraph, that stale Phase-3-pre-planning text was
  spliced directly against an unrelated fragment of PHASE 2's own plan-list prose ("Plan: Not
  started\n(`2d52a1e`), 02-04 (`46d587e`) — plus the post-checkpoint GOV-01 close sweep..."),
  producing an incoherent sentence that read as neither phase's actual content.

  **This is the same defect class FINDING-01 and the 2026-09-03 corrections already document — "a
  normalizer that cannot parse keeps the previous value, silently" and "many writers, no owner" —
  firing again, this time in the orchestrator-driven `phase.complete` path rather than an executor
  write.** The executor-side fix (`state.sync`) does not cover this call path. Corrected by hand:
  frontmatter (`completed_phases: 3`, `percent: 100`, `status: verified`), the "Current Position"
  body section rewritten to reflect actual current state and point to the close sweep by path, and
  the progress bar. Not filed as a new FINDING document — FINDING-01 already names the class and
  covers this instance without needing a fourth restatement; this entry is the measurement FINDING-01
  itself asks every future instance to carry.

- **Phase 2's `verification_status` reads `stale` in `init.manager`, surfaced during the v1.0
  milestone audit's readiness check (`ALL_PHASES_VERIFIED` computed `false` on Phase 2 alone;
  Phase 1 and Phase 3 both `passed`).** Root cause is the same `#2348` staleness rule already
  measured in the 2026-09-03 correction above: `02-GOV-SWEEP.md`'s own close sweep wrote
  `02-05-SUMMARY.md`, which postdates `02-VERIFICATION.md`, so `isPhaseComplete`'s
  `status === 'passed'` check reads stale forever — not because Phase 2's verified content is
  wrong (re-read in full during this audit: `status: passed`, 10/11 criteria verified live,
  criterion 11 correctly deferred-by-design pending the sweep that has since run and closed with
  zero corrections), but because a summary newer than the verification report is, by this rule's
  own design, indistinguishable from a summary that invalidated it.

  **This is the same defect `13071ff` was believed to fix, on its fourth observed occurrence.**
  `13071ff` diagnosed the cause as SUMMARY-to-PLAN pairing and was itself corrected as WRONG by
  the 2026-09-03 entry above, which measured the real mechanism (`isPhaseComplete` +
  the `#2348` staleness rule) and called that correction the "third live reproduction" as of
  2026-09-03 — this audit's `init.manager` read is the fourth: same trigger (a post-verification
  sweep commit landing a `*-SUMMARY.md`), same symptom (a genuinely-passed phase reporting as
  incomplete/stale), still unpatched at the mechanism level. Every occurrence so far has been
  corrected by hand at the point of discovery (frontmatter edits, or here an override during
  milestone close) rather than by a fix to `isPhaseComplete` or the staleness rule itself.

  **Phase 3's D-20 (its own close sweep deliberately writes no `*-SUMMARY.md`) is a workaround for
  Phase 3, not a fix for the class.** It prevents Phase 3 from re-triggering the rule, which is why
  Phase 3 reads `passed` here and Phase 2 does not — but it does so by avoiding the trigger
  shape for one phase, not by changing what the staleness rule does when a legitimate
  post-verification artifact (a sweep's own summary, a GOV-01 record, anything dated after
  `*-VERIFICATION.md`) lands on disk. Phase 2 carries the defect permanently: `02-05-SUMMARY.md`
  already exists and will always postdate `02-VERIFICATION.md`, so this phase will read `stale`
  in every future `init.manager`/`isPhaseComplete` call for the life of this repository unless the
  rule itself is changed. Milestone close proceeded past this with an explicit override (see the
  v1.0 milestone-close override record) rather than waiting on a fix that was already known, before
  this audit, not to be in scope for this milestone.

- **Sixth occurrence of the FINDING-01 frontmatter-regression class, this time via
  `gsd_run query milestone.complete`'s own state write.** Its JSON result reported
  `state_updated: true` and `preservation_warnings` for exactly two fields
  (`stopped_at`, `current_phase` — both correctly preserved over a disagreeing derived
  value, per its own self-report). `completed_phases` (3→2) and `percent` (100→67)
  regressed to the identical wrong values seen in every prior instance, with no
  preservation warning for either — the same silent-regression shape, now confirmed at
  a fifth distinct call site (`state.record-session`, `phase.complete`, the
  unidentified mid-`transition.md` writer, and now `milestone.complete`, in addition to
  `13071ff`'s original mis-diagnosed instance). Corrected by hand in the same pass:
  `completed_phases: 3`, `percent: 100`. Not filed as a new FINDING document — same
  reasoning as every prior instance this session: FINDING-01 already names the class,
  and each occurrence's own measurement is what the finding asks to be carried forward.

### Blockers/Concerns — added 2026-09-03

- **`state.record-session` reverted `completed_phases` 2→1 and `percent` 67→33 again; restored
  by hand.** Third live reproduction. **The mechanism recorded at `13071ff` is WRONG and is
  corrected here.** That commit blamed the phase-completion heuristic for not recognising the
  post-checkpoint runbook's SUMMARY (`02-05-SUMMARY.md`, paired with `02-GOV-SWEEP-RUNBOOK.md`
  rather than a `*-PLAN.md`). Measured: SUMMARY-to-PLAN pairing never enters the computation —
  `scanPhasePlans`'s counts feed `total_plans`/`completed_plans`, different fields. Phase
  completion routes through `isPhaseComplete` (`.claude/gsd-core/bin/lib/verification.cjs:565`)
  = `verification.status === 'passed'`, and the `#2348` staleness rule is *a `*-VERIFICATION.md`
  is stale when a summary is newer than it*. Measured live: phase 01 → `passed`, phase 02 →
  **`stale`**. `02-05-SUMMARY.md` is not *unrecognised*; it **is** seen, it **is** newer than
  `02-VERIFICATION.md`, and being seen is what marks verification stale.

  **What the wrong diagnosis would have caused, which is the part worth keeping:** teaching the
  SUMMARY/PLAN pairing to recognise runbooks — the fix the recorded mechanism implies — would
  have changed nothing. `completed_phases` would still read 1, because pairing is not what the
  counter consults. A wrong mechanism yields a wrong fix that *appears* responsive.

  **Second instance this week of a registered finding naming a mechanism that was not the one
  operating** (FINDING-01's normalizer diagnosis was the first). Both were explanations that fit
  the evidence, asserted rather than measured, and both were falsified by someone reading the
  code path instead of the finding. Commits are immutable, so this entry is the correction and
  cites `13071ff`.

  **Structural, not incidental:** GOV-01 requires the close sweep to run *after* verification and
  to commit, so any phase whose sweep writes a SUMMARY ends with stale verification and an
  undercounted phase. Phase 3's answer is `03-CONTEXT.md` **D-20** — its sweep writes
  `03-GOV-SWEEP.md` and **no `*-SUMMARY.md`**, so the staleness comparison has nothing newer to
  find. Verified during discussion: the SUMMARY filename is **not** mandated by GOV-01 (its text
  never mentions one); the "own commit and summary" wording is Phase 2's D-16, a CONTEXT
  decision — so this is a plan-shape choice, not a requirement change.

  **Durable home:** this correction's full audit trail — the original claim restated, the
  operating mechanism named and measured, what the wrong diagnosis would have caused, and
  the connection to D-20 — now lives at `03-FINDING-01-phase-completion-diagnosis.md`,
  because this file's accuracy has a registered expiry (see below) and a correction living
  only here is one executor run from disappearing.

- **`state.planned-phase` recomputed `percent` to 33 while leaving `completed_phases: 2`
  intact — a SECOND field falling to the mechanism corrected above, and the reason a
  `completed_phases`-only hand-fix is not sufficient.** `computeProgressPercent`
  (`state-document.cjs:424`) returns `min(planFraction, phaseFraction)`. It takes
  `phaseFraction` from the **disk-derived** phase count — which reads 1, because Phase 2's
  verification is `stale` — not from the frontmatter value a human just corrected. So the
  write left the file internally contradictory: `completed_phases: 2` beside `percent: 33`,
  which is 1/3.

  **Corrected to 64, computed rather than assumed.** With four Phase 3 plans added,
  `planFraction` = 7/11 = 63.6% is now the binding constraint, below `phaseFraction` = 2/3 =
  66.7%. The intuitive "restore it to 67" would have been wrong — 67 was correct only while
  `total_plans` was 7.

  **Why this is worth recording rather than just fixing:** `13071ff` and the 2026-09-03
  correction above both restored `completed_phases` and stopped there. Neither noticed
  `percent` because at the time `planFraction` was 1.0 and the two happened to agree. The
  moment plans were added they diverged, and the same root cause produced a wrong field that
  reads like an unrelated bug. A partial hand-correction of a derived block is not a
  correction — it moves the staleness to whichever field nobody checked.

- **A third field found wrong by the same root cause, this time in `state.sync`'s body
  write: `Total Plans in Phase` regressed 4 -> 3 during 03-04's own execution.** Running
  `gsd-tools query state.sync` (the standard `execute-plan.md` state-update step) on a
  disk state where every phase's plan count equals its summary count — Phase 1 (3/3),
  Phase 2 (4 plans/5 summaries), Phase 3 (4/4, this plan's own `03-04-SUMMARY.md` just
  landed on disk) — walked phase directories in sorted order and set `highestIncompletePhase`
  to the FIRST phase encountered whose `summaries < plans` is false (Phase 1, `planCount: 3`),
  then never updated it for Phase 2 or Phase 3 because `highestIncompletePhase` was already
  truthy: `cmdStateSync`'s loop only replaces `highestIncompletePhase` inside its
  `summaries < plans` branch (a genuinely incomplete phase) OR inside an `else if
  (!highestIncompletePhase)` branch that only fires while it is still null. **Once every
  phase on disk is fully summarized, no phase can ever re-trigger either branch after the
  first one runs, so the field silently freezes on whichever phase sorts first alphabetically
  — Phase 1's plan count, reported as "the current phase's total," regardless of which phase
  is actually current.** Corrected by hand here (4, matching `find-phase 3`'s
  `plan_count: 4`); not a fix to `state.cjs` — that file is gitignored `.claude/` tooling,
  outside this plan's `files_modified`, and a code fix belongs to whoever owns that class
  (see FINDING-02, gitignored instrumentation). Logged here so the instance is not silently
  overwritten again the next time `state.sync` runs against an all-summarized disk state.

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| Governance | **Untagged code written outside any plan escapes every derivation-based coverage mechanism, including the just-decided GOV-01 amendment above.** Distinct from that amendment, deliberately not solved by it: the amendment fixes the derivation RULE (IDs-only, repo-wide); this item is a TAGGING-DISCIPLINE gap — a file with no requirement-ID tag at all is invisible to any ID-keyed derivation no matter how wide its scope. Confirmed concretely: `internal/platform/gateproof/tree_drain_test.go`, `internal/platform/gate/harness_waitdelay_test.go`, and the `migrate.go` T-03-14 fix — three of six files committed outside any Phase 3 plan tonight — carry no requirement-ID tag (only `tree_drain_test.go` carries a bare document reference, "see 03-INCIDENT-02", which is not an ID). Phase 3's close sweep caught these six commits' `.planning/`-side documentation (tagged, in-scope) but not their code (untagged, structurally out of scope regardless of the amendment just taken). Not taken now — the fix is a process discipline (every commit outside a plan gets a requirement-ID comment at the point of writing) or a CI-side check (a diff touching source with no adjacent ID-tagged doc fails loudly), neither of which is scoped work for tonight. | **Registered** — not planned | 2026-09-04, found auditing the GOV-01 amendment's own coverage | Milestone close |
| Process lifecycle | **Grandchild processes are left unreaped after a Go subprocess-lifecycle timeout, in two instances of the same defect class.** (1) `gate.Run` (`harness.go`, fixed at `fe052fb`): `exec.CommandContext`'s default `Cancel` kills only the direct child; a grandchild that survives it and holds an inherited I/O handle keeps `cmd.Wait()`'s underlying process unreaped even after `WaitDelay` forces the pipe closed and returns to the caller — confirmed by reading `os/exec`'s `exec.go` directly, with dump evidence in `03-INCIDENT-02-harness-timeout-defects.md`. (2) `materializeTree` (`tree_test.go`, 03-REVIEW.md WR-04): every `t.Fatalf` in the tar-extraction loop aborts via `runtime.Goexit()` without draining, waiting on, or killing the `git archive` child — inconsistent with this same file's own deliberate `t.Cleanup`-not-`defer` convention two lines above, hardened for exactly this reason. **One fix closes both:** a process group (POSIX) or Job Object (Windows) that reaps every descendant on timeout/cancel, rather than patching each call site's cleanup individually. Not taken now — it is new process-management machinery, not a fix scoped to either call site. **This deferral itself existed only in conversation for roughly five hours before being written down here.** It was agreed around 18:00 on 2026-09-03 when the `gate.Run` fix was scoped ("make the timeout path return; defer reaping" — the fix landed at `fe052fb`, the deferral did not), and was recovered only because a search for a *different*, unrelated STATE.md entry ("orphan-reaping deferred item," sought to fold in WR-04) turned up nothing and forced the gap into view. Third conversation-only item tonight that nearly did not make the record, after the planner-contributions-as-file and required-reading-bundle deviations above. | **Registered** — not planned | 2026-09-03 (agreed ~18:00 IST during gate.Run fix scoping; recorded 23:28 IST after WR-04 surfaced it) | Gate milestone |
| Process lifecycle | **`materializeTree` copies are orphaned on disk, a distinct instance of the grandchild-reaping defect class above — disk space, not zombie processes.** `t.Cleanup(func() { os.RemoveAll(root) })` (`tree_test.go`) never ran for 8 copies found accumulated in `%TEMP%` (38MB total, timestamped across the whole 2026-09-03/04 session, the most recent 17 minutes before discovery). Mechanism: Go's own `-timeout` watchdog panics from `testing.(*M).startAlarm`'s alarm goroutine, not the stalled test's own goroutine, so the process exits before that test's registered `t.Cleanup` ever runs — every stall tonight killed by Go's internal timeout (not an external kill) orphaned its copy this way. Would recur on every CI timeout, not just this session. Cleaned up (deleted) 2026-09-04 after registration; not fixed at the source — same process-group/Job-Object mitigation as the sibling entry above would also bound this, since a reaped process tree could be made to also unlink its own temp root, but that is scope creep on top of an already-deferred fix, not a new one. | **Registered** — not planned | 2026-09-04, discovered auditing the T-03-14/control-drift fix's out-of-scope observation | Gate milestone |
| Test isolation | **PROOF-03 has hit a 12+ minute `go test` timeout twice, confirmed, post-drain-fix (`60bb107`) — the D-06/deferred-item-1 contention prediction, observed rather than modelled.** (1) 03-03's own executor, 828.9s, `go test ./internal/platform/gateproof/ -shuffle=on`, not reproduced on retry (116-118s clean twice after). (2) The T-03-14 security-fix agent's isolated `TestPROOF03_GateNamesUnreadableFixture` run, over 12 minutes, goroutine dump. **A user-reported third occurrence could not be independently corroborated** — searched every phase-3 SUMMARY/INCIDENT/REVIEW doc for a third timeout/goroutine-dump mention and found none; if a third instance exists outside those artifacts, its source is not yet identified. **Contention vs. a second wedge — partially checked, not conclusively resolved:** postgres's own logs (`docker logs`) show real, unrelated-domain activity (two `section_nodes` constraint-violation errors, the segmentation/structural-model pipeline, nothing to do with `gateproof`/`migrate`) landing 29 seconds after occurrence (2)'s orphaned temp-dir creation timestamp — consistent with genuine external load on the shared compose database at the same moment, matching D-06's own measured prediction of cross-package contention (`gate`×`store` +2.11s, `gate`×`approved` +0.80s), just far more severe here (minutes, not seconds). At the time of both occurrences, `log_lock_waits` was `off` and `log_min_duration_statement` was `-1` (disabled) on this database, so postgres would not have logged an actual blocking lock even if one occurred — its logs could show correlated activity but could not rule a lock wait in or out. No goroutine dump text was captured to a file for either occurrence (03-03's own SUMMARY calls its event "not currently understood"; the security-fix agent's report is prose-only), so the frame-identity question — same `materializeTree` frame both times, or different — could not be checked retroactively. **Fixed forward rather than reproduced live tonight:** `log_lock_waits = on` and `log_min_duration_statement = 1000` were set via `ALTER SYSTEM` + `pg_reload_conf()` on 2026-09-04 and confirmed persisted to `postgresql.auto.conf` in the `pg_data` named volume (survives container restarts). The next occurrence, whenever it happens, will be diagnosable from postgres's own logs without needing a live reproduction. **Update, 2026-09-04, same session: a named contributing source found, but the mechanism is not D-06's.** With the `api` compose service running (started ~04:28 UTC, cause not investigated), `TestPROOF03_GateNamesUnreadableFixture`'s `defeated_tree_control` took 161.18s; a full `make test` regression run immediately after (exit 0, no failures) showed `gateproof` at 150.656s, both consistent with the same elevated state. `docker compose stop api` followed by an immediate re-run dropped `defeated_tree_control` to 26.13s (6.2x) and `intact_tree` to 26.42s — both back near the plan's original 18-21s measurement. **But postgres's own logs, checked with `log_lock_waits`/`log_min_duration_statement` now enabled, showed zero lock-wait or slow-statement entries during the contended run** — meaning the mechanism is NOT the classic postgres-side query/lock contention D-06 measured and modeled (`gate`×`store`/`approved`, concurrent Go test packages issuing real queries). `max_connections` is 100, ruling out connection-limit exhaustion too. The `api` container's effect is real and reproduced, but its mechanism is more likely host-level (CPU/network) resource contention from a live application container than database contention proper — a different mechanism that happens to produce a similar symptom, not a confirmation of D-06's specific model. `api` was restarted after this test (only stopped for the comparison). **Left open, linked to D-06 deferred item 1 as a related-but-distinct observation, not closed as either verdict** — this phase does not block on it: all three proofs pass, no requirement fails, and PROOF-01/02/03 are independently `[x]`/Complete in REQUIREMENTS.md regardless of this timing anomaly's cause. — this phase does not block on it: all three proofs pass, no requirement fails, and PROOF-01/02/03 are independently `[x]`/Complete in REQUIREMENTS.md regardless of this timing anomaly's cause. | **Registered** — not planned; diagnosability fixed forward via postgres logging, resolution deferred to next occurrence | 2026-09-04 | Gate milestone |
| Test-harness robustness | **`TestGateOrdersPreflightBeforeMigrate`'s ordering check matches on the unanchored substring `"migrate"` (03-REVIEW.md WR-03, `ordering_test.go:63-69`).** It records the index of the *first* line in `make -n gate`'s dry-run expansion containing that substring, which a future target name, comment, or variable reference (e.g. `migrate-status`, `unmigrated-*`, `$(MIGRATE_BIN)`) could match earlier than the real invocation line, producing either a false failure or — if the coincidental match still sorts after `env-preflight` — a false pass. Not currently reachable: today's `make -n gate` expansion has exactly one line containing "migrate". Deferred rather than fixed immediately because the fix (anchor to the actual invocation shape, e.g. a `(^|\s)migrate(\s|$)` regex, or pin to a captured fixture line) is a real but low-urgency hardening, not a live defect. | **Registered** — not planned | 2026-09-03, Phase 3 code review | Gate milestone |
| Test isolation | **Isolate PROOF-03's nested run on its own database or schema (D-06, deferred item 1).** Measured interference, present *today* before Phase 3, from per-package intervals in `go test ./... -json`: `store` 2.42s to 6.57s, `approved` 2.32s to 5.26s, `gate` 4.46s to 25.70s — giving `gate` x `store` **+2.11s concurrent** and `gate` x `approved` **+0.80s concurrent**. Phase 2's nested `make test` already runs `store` tests against the compose database while the outer `store` package is running; Phase 3 adds `migrate` to that concurrently-running set via PROOF-03's full nested gate. **Not taken because it is arguably its own requirement** — new isolation machinery in a phase scoped to three proofs, not a fix to any of them. | **Registered** — not planned | 2026-09-03, Phase 3 discussion | Gate milestone |
| Governance | **Amend GOV-01's close-sweep derivation to IDs-only, repo-wide (deferred item 2).** The current rule is path-scoped — `git ls-files '.planning/*'` — so a requirement-ID tag in a file outside `.planning/` buys nothing; `ci.yml` and `harness.go` would each stay invisible to the derivation **fully tagged**. Measured: widening to `git ls-files` (repo-wide) costs **5.3s over 227 tracked files** and takes the derived set from **51 to 54**, correctly adding `harness.go` and `testenv_test.go`, and incorrectly adding `classify_test.go` as a **false positive** — it matches on "phase 3's done-condition," the *segmentation pipeline's* phase 3, not this milestone's. So any amendment must be **IDs-only outside `.planning/`, with no phase-number term**: requirement IDs are globally unambiguous, phase numbers are not, and the phase-number term is the sole noise source. **Refused for Phase 3 deliberately**: Phase 3's own close sweep would then run against a rule the phase itself changed — a check validating its own amendment, the same self-reference that disqualified `*-VERIFICATION.md` as GOV-01's own durable home. **Decide at milestone close.** Nothing is lost by waiting: `harness.go` is already in the derived set today via its "Phase 3" prose. The argument for the amendment, preserved in the form D-06 found better than the one first given: the tag's value is **not** getting `harness.go` into the set — it is already in, unprompted — it is **keeping it in when someone rewords the prose**. A durability property, not a coverage one. **DECIDED 2026-09-04, at milestone close, per the terms above**: amendment taken as specified — IDs-only, repo-wide, no phase-number term. The self-reference objection expired when Phase 3's close sweep terminated (`03-GOV-SWEEP.md`, `0b7f6a7`). Recorded in REQUIREMENTS.md's GOV-01 entry, beside obligation 3's original text (unedited), not in place of it — see "Amendment to obligation 3, 2026-09-04." **This decision does NOT close the tagging-discipline gap found the same night** (untagged code committed outside any plan, e.g. `tree_drain_test.go`) — that is a separate item, registered below. | **Decided** — amendment taken, recorded in REQUIREMENTS.md | 2026-09-03 registered, 2026-09-04 decided | Milestone close |
| Build portability | **Pin `SHELL` in the Makefile, or fail loudly naming the cause under `cmd.exe`.** GNU Make executes recipes through `cmd.exe` on Windows unless `SHELL` is set, and the gate recipe (`Makefile:74-75`) plus the `planning-parity` target (`Makefile:95`, added by 02-04) use POSIX constructs. A Windows developer running `make gate` in PowerShell gets `'unformatted' is not recognized as an internal or external command` — an error naming neither the gate nor the cause, which is adjacent to what GATE-01..03 exist to fix. It fails LOUDLY with a non-zero exit, so there is no false green: the milestone's core value is not violated in the dangerous direction, which is why this is deferred rather than blocking. **Deferred as NEW SCOPE, not as a defect** — pinning `SHELL` changes recipe execution semantics for every target on every platform, which is a requirement decision, and GOV-01's own rule is that a pass which would add a requirement HALTS for a human. The documentation half WAS taken in scope and is closed at `b877d9b`: README and `make help` now state the POSIX-shell requirement and README records the PowerShell symptom. | **Deferred** — registered, not planned | 2026-09-02 (operator, Phase 2 UAT test 14, disposition (a)) | Gate milestone |
| Test-harness robustness | **AC-14 empty-heading guard — CLOSED 2026-09-01 by Alex.** The entry covered two halves of the heading-free-fixture edge and both now have homes, so it is closed as a backlog item rather than carried. **Half 1, the preamble declaration — closed in Phase 1:** Alex proposed the declaration fix (option C); it landed in 01-02 as the pinned `fixtureHasPreamble` constant, covered by control subtests 1 ("no headings at all") and 6 ("declared preamble-free, but no headings"). **Half 2, the unguarded index — specified as GATE-09 (Phase 2):** `acceptance_test.go:435` indexes `headings[0]` with no emptiness check and panics on a heading-free fixture, aborting the test binary. Alex's acceptance text: *a heading-free fixture MUST produce a normal test failure and MUST NOT panic; no test may index `headings[0]` before proving `len(headings) > 0`.* Length guard only, no second declaration mechanism. **The former "blocks Phase 3" gate is discharged, not dropped:** GATE-09 is a Phase 2 requirement and Phase 2 precedes Phase 3, so the ordering that gate enforced is now structural. GATE-09 is a newly discovered Phase 2 hardening requirement, NOT a retroactive modification of Phase 1's frozen acceptance basis — Phase 1 was contractually forbidden from touching `acceptance_test.go`. | **Closed** — superseded by GATE-09 (Phase 2) | 2026-09-01 (Alex, Phase 1 UAT test 5; closed same day) | Gate milestone |

### Blockers/Concerns — added 2026-09-02

- **ESCALATED TO ALEX — FINDING-01 option 2, a design decision, not a disposition.**
  Make STATE.md's frontmatter DERIVED rather than authored: anything reconstructible
  from disk and git (plan/summary pairs, HEAD, counts, phase position) is generated,
  so a partial writer cannot leave a stale field. The case is sharper than when first
  proposed — the frontmatter is **already meant to be derived**; the executor path
  simply never invoked the derivation. Option 2 makes that intent true rather than
  aspirational. An instance fix landed 2026-09-02 (the executor now calls
  `state.sync`), but it closes one path, not the class: STATE.md still has many
  writers, and a writer that forgets the call still leaves the frontmatter stale.
  **FINDING-01 stays OPEN until this is decided.**

- **FINDING-02 — instrumentation in gitignored `.claude/` is unversioned and reverts
  silently.** A class with three known instances (the review-run archive block, any
  `state.cjs` guard, the executor contract). It CONSTRAINS every fix that touches
  `.claude/` and must be read before choosing one, not after — see
  `02-FINDING-02-gitignored-instrumentation.md` and the pointer under Fragile Areas in
  `.planning/codebase/CONCERNS.md`. The tracked-counterparts register in that finding
  carries a detection command per instance; run them after any `/gsd-update`.
  **This supersedes the standalone review.md note below**, which is instance 1.

- **CORRECTION 2026-09-02:** FINDING-01 originally recorded a normalizer bug as the
  cause of the stale `status:` field. That was false and asserted rather than measured
  — traced to the orchestrator's own value at `20bd4ce`, left untouched by three
  executor commits. The false claim also went into `d17051a`'s commit message.
  Corrected in place in the finding, with the original claim restated so the
  correction is legible.

- **FINDING-01: `STATE.md` has many writers and no owner.** Recorded in
  `.planning/phases/02-enforcement-and-a-single-gate-definition/02-FINDING-01-state-authority.md`.
  Executors write this file mid-phase, so a hand-correction survives only until the
  next executor runs. It is NOT an instance of GOV-01 — GOV-01's instances are
  documents nobody edited that a later decision falsified; this is a document
  several agents edit and each one only partially. Registering it under GOV-01
  would put it under a mechanism structurally unable to close it. **Disposition is
  a human decision and has not been taken** — it would be a new requirement, and
  GOV-01's own rule is that a pass which would add a requirement halts for a human.

- **A normalizer that cannot parse keeps the previous value, silently.**
  `normalizeStateStatus` (`state-document.cjs:387`) maps the body `Status:` line by
  substring; a line matching none of its keywords yields `unknown`, and
  `state.cjs:2359-2361` then preserves the old frontmatter value with no warning.
  That is how `status: planning` survived three executed plans. Same shape as the
  other defects this week: a check that cannot come back false.

- **Two executor subagents were killed by the stall watchdog during this phase**
  (02-02's first dispatch, and 02-04 twice). 02-04 was finished inline. If this
  recurs, the likely cause is a long output-silent command — the nested-suite tests
  legitimately take minutes.

## Session Continuity

Last session: 2026-09-04T06:51:49.736Z
Stopped at: v1.0 (Gate-Hardening) shipped and archived — awaiting /gsd-new-milestone

**Note: this section previously carried Phase 2's own closure narrative (GATE-03/06/02, requirement
count, GOV-01 sweep mechanics for `02-GOV-SWEEP-RUNBOOK.md`) verbatim, unchanged since 2026-09-02,
because whatever wrote this file at Phase 3's close did not regenerate it either — the same
`phase.complete` gap recorded in Blockers/Concerns 2026-09-04. That content is preserved in this
file's git history (see `02-VERIFICATION.md` and `02-GOV-SWEEP.md` for Phase 2's own record); it is
replaced below with Phase 3's actual closure content, not appended beside stale content the way a
correction normally would be, because it described a different phase's mechanics entirely and left
in place would mislead about which phase is current.**

What Phase 3 delivered, and the evidence that closed it:

1. **PROOF-01/02/03** — `internal/platform/gateproof` proves all three environment conditions
   (unset DSN, unreachable host, unreadable fixture) fail `make gate` and name the cause, each with
   an SC-5 differential control. Independently re-run live during phase verification against the
   real compose database (`03-VERIFICATION.md`).

2. **GATE-10** — the escalation preamble and named cause arrive in one `t.Fatalf` call at all three
   sites in `testenv.go`; confirmed directly in source, not by grep count.

3. **Two harness defects found and fixed mid-phase** (not part of the planned scope): a
   `materializeTree` pipe-drain deadlock and `gate.Run`'s unreachable `TimedOut` branch on
   `WaitDelay` — `03-INCIDENT-01`, `03-INCIDENT-02`.

4. **Code review**: 4 warnings found, 2 fixed (a real `errors.Is(exec.ErrWaitDelay)` gap the
   `WaitDelay` fix itself introduced, and a misleading comment), 2 deferred with measurements
   (`03-REVIEW.md`, `03-REVIEW-FIX-SUMMARY.md`).

5. **Security audit**: 29 threats registered (including 3 test files committed outside any plan,
   which no plan's threat model could have covered), 28 closed on first pass, 1 real live password
   leak found (`store.RunMigrations`, T-01-01's un-remediated twin, amplified by PROOF-03's design)
   and fixed same night (`03-SECURITY.md`, `03-SECURITY-FIX-SUMMARY.md`).

6. **Regression gate**: full `make test` (all packages) passed clean, no cross-phase regressions.
7. **PROOF-03 timing anomaly**: an intermittent 12+ minute timeout (vs. 18-30s normal), the `api`
   compose service confirmed as a contributing factor via live A/B test, mechanism not fully
   understood (not postgres lock/query contention per enabled logging showing nothing) — registered
   open, non-blocking, linked to D-06.

**The close sweep is out of the wave graph, same mechanism as Phase 2's:** `03-GOV-SWEEP-RUNBOOK.md`
does not end `-PLAN.md`, so `plan-scan.cjs` never schedules it as a wave plan. Its logical id is
`03-05`; ROADMAP.md's Phase 3 plan list already references it as the post-checkpoint step.

**Correction, 2026-09-04 (03-GOV-SWEEP.md Task 2):** this section originally instructed invoking the
sweep via `/gsd-execute-plan .planning/phases/03-automated-proof/03-GOV-SWEEP-RUNBOOK.md` and stated
"**UAT status is the one precondition not independently confirmed**: `03-VERIFICATION.md` found zero
human-verification items needed, so no `03-UAT.md` was created — whether the sweep's own precondition
checker accepts that as satisfying `uat`, or requires a literal UAT artifact regardless of content,
was not checked before this entry was written. If the sweep halts on that precondition, run
`/gsd-verify-work 3` first (should close near-instantly, nothing to test) and re-invoke." Both claims
are now stale: (1) `/gsd-execute-plan` does not exist as a command (see "Blockers/Concerns — added
2026-09-04" below — this was already caught and recorded separately); the sweep actually ran via a
`gsd-executor` agent dispatched directly against the runbook's path. (2) `/gsd-verify-work 3` WAS run
(after this entry was written), produced a real `03-UAT.md` (`status: complete`, 4/4 passed, 0
issues, 35/35 deliverables auto-covered, committed `367761d`), and the sweep's four preconditions —
verification, UAT, security, all four wave SUMMARYs — were all independently re-checked by the sweep
itself and confirmed satisfied before it derived anything. See `03-GOV-SWEEP.md` for the sweep's own
record.

Resume with: none — the close sweep (`03-GOV-SWEEP.md`) has run and terminated. Phase 3's 4/4 wave
plans are complete and the milestone's three phases are all complete.
Resume file: None

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
