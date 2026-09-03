---
gsd_state_version: 1.0
current_phase: 03
current_phase_name: Automated Proof
status: planning
stopped_at: Completed 03-03-PLAN.md
last_updated: "2026-09-03T15:34:39.108Z"
last_activity: 2026-09-03
state_head: 97fe596deb4741af2db837540641c08483644f7a
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 11
  completed_plans: 9
  percent: 33
last_activity_desc: Phase 03 execution started
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-30)

**Core value:** `make gate` must be able to distinguish "tested and passed" from "tested nothing".
**Current focus:** Phase 03 — Automated Proof

## Current Position

Phase: 03 (Automated Proof) — EXECUTING
requirements (GATE-01, GATE-02, GATE-03, CI-02, GATE-06, GATE-07, GATE-08, GATE-09,
SEC-01, GOV-01) closed in REQUIREMENTS.md. GOV-01 was the last: its close sweep
(`.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP.md`) ran
two passes and terminated on the second producing zero corrections — see that
document for the derivation, the per-artifact evidence table, and the re-arm log.
Plan: 4 of 4
(`2d52a1e`), 02-04 (`46d587e`) — plus the post-checkpoint GOV-01 close sweep
(logical id 02-05, `02-GOV-SWEEP-RUNBOOK.md`). All checkpoints landed: verification
`status: passed` (10/11, criterion 11 deferred-by-design until this sweep), UAT
`status: complete` (18 passed, 2 issues both dispositioned), security `status:
verified, threats_open: 0`.
Total Plans in Phase: 4
Phase base: `868d45b`, approved by Alex Zamurko 2026-09-01
Plan bytes: `8edae22` — freeze: `c96ecb2`
Last activity: 2026-09-03
`/gsd-execute-phase`, per its own structural design — see
`02-GOV-SWEEP-RUNBOOK.md`'s header). Compose postgres up and healthy, bound to
`127.0.0.1:5432` only.

**Next:** Phase 3 (Automated Proof) — **context gathered 2026-09-03** (`fc21341`),
not yet planned. Read
`.planning/phases/03-automated-proof/03-CONTEXT.md` before planning: 21 decisions, every
number in it measured on this host rather than estimated. Three things the planner must not
discover late:

1. **The requirement set has changed.** D-19 declares **GATE-10** as new scope — the
   single-message constraint GATE-06's design always had and never stated, which D-18's
   proofs depend on. ROADMAP §Phase 3's `**Requirements**:` line and REQUIREMENTS.md's
   traceability table both still read PROOF-01/02/03 only, so **they currently disagree**.
   GOV-01 obligation 2 requires `make planning-parity PHASE=3` as the first plan's
   precondition; it must be run, the two documents brought into agreement, and the check
   green before planning proceeds.

2. **SC-5 is corrected, not satisfied as worded** (D-10, D-12). Its literal form is
   unreachable through the harness: `buildChildEnv` sets `DepthEnv` last and skips any entry
   naming it, so a control spawning the proof package gets depth 1 and every proof
   `SkipIfNested`-skips. The correction is sequenced through the same start check.

3. **The close sweep writes no `*-SUMMARY.md`** (D-20) — see the corrected mechanism above.

Its Note on the harness (`internal/platform/gate`, built by 02-02) and the design-tension
entry below remain its starting context.

**This file's accuracy has a known expiry — see `02-FINDING-01-state-authority.md`.** It has many writers and no owner: it was hand-corrected at `20bd4ce`, then rewritten by the 02-01, 02-03 and 02-02 executors, and was stale again by `2d52a1e` (`status: planning` with three plans executed; a body whose count and list contradicted each other). It was stale a further time after this correction: `stopped_at`/`Current Position` narrated all three checkpoints as outstanding after all three had already landed and been committed — found and corrected by this sweep (`02-GOV-SWEEP.md`, evidence row 4). This correction carries the same expiry. FINDING-01's own mechanism fix (the executor's `state.sync` call) closes the frontmatter-vs-body desync path; it does not close the class this file's own edit history keeps demonstrating.

Progress: [███░░░░░░░] 33%

## Performance Metrics

**Velocity:**

- Total plans completed: 3
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 3 | - | - |

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

### Blockers/Concerns

- Phase 3 carries an open design question, recorded at PROJECT.md lines 91-93: a negative test asserting "the gate fails when `EPISTEMIC_OS_DB_URL` is unset" has to run inside the suite the gate governs, in an environment where that variable is set. **Amended by the GOV-01 close sweep, 2026-09-02 (not deleted — Phase 3's success criterion 4 still requires the tension to be solved *in Phase 3's plan*):** Phase 2's 02-02 supplied a slice of the answer rather than the whole one. It built `internal/platform/gate` (`Run`/`Make`/`RunOptions`/`RunResult`/`SkipIfNested`/`RepoRoot`/`DepthEnv`/`DefaultTimeout`) as a shell-out-to-`make` harness, confirmed at a human checkpoint as Phase 3's PROOF-01/02/03 contract, with a bounded recursion guard (`EPISTEMIC_OS_TEST_MAKE_DEPTH`, incremented last so `Unset`/`Env` cannot defeat it) so a proof that shells out to `make gate` from inside the suite `make gate` governs does not loop. ROADMAP.md §Phase 3 carries a "Note on the harness" recording this slice and pointing at the three `RunOptions` shapes PROOF-01/02/03 map onto. **What Phase 3 still has to solve:** the harness makes the recursive shell-out *safe*; it does not by itself decide how each proof arranges an environment where `EPISTEMIC_OS_DB_URL` IS set for the outer suite while being unset/unreachable/fixture-broken for the inner `make gate` call — that composition is Phase 3's own plan's job, per its Note on the harness and success criterion 4.
- `.planning/config.json` is untracked. `cmdConfigNewProject` refuses to overwrite an existing config, so it is protected from regeneration only while the file stays in place.
- **After any `/gsd-update`, re-check that `.claude/gsd-core/workflows/review.md` still contains the run-directory archive block before the `rm -rf`.** The block is hand-added instrumentation in a GSD-managed file, so an update reverts it silently — and a capture that stops happening without saying so is the same failure class the archive exists to catch. Added under GSD 1.11.0; each archive records the version that produced it in `_INSTRUMENTATION.txt`.
- **The instrumentation itself is not in version control.** `.gitignore:29` ignores `.claude/`, so the archive block lives only on disk in this worktree. Its *output* under `.planning/phases/*/review-runs/` is tracked and survives, but the mechanism does not: recreating this worktree, or the runbook removing it, takes the block with it and later reviews would then discard their run dirs silently. Re-applying it is a manual step with no reminder attached.
- 01-02's whole-tree git-diff acceptance criteria (unrestricted 'git diff --name-only 868d45b --') print 47 files, not the expected single fixture_test.go, because ~29 pre-existing .planning/-only commits (base re-anchor, plan re-freeze, review-run archives) already sit between the phase base and execution start. The internal/-scoped form of the same check still confirms exactly one source file changed. Likely affects 01-01 and 01-03's identical whole-tree-diff criteria too — flag before running them.
- 01-03: five contract decisions (testenv package path/API, EPISTEMIC_OS_TEST_REQUIRE_DB semantics, the flag's wider-than-its-name scope, README/Makefile documentation deferral, the deferred AC-14 empty-heading guard) plus unresolved probe edge E1 are queued for the developer's end-of-phase disposition. The preamble policy (option C) is already RESOLVED 2026-09-01 by Alex and is not among these five.

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

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
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

Last session: 2026-09-03T15:34:38.864Z
Stopped at: Completed 03-03-PLAN.md

What changed, and the evidence that closed it:

1. **GATE-03 (was: no executable acceptance)** — 02-01 T2 step 5 moves the fixture aside against a live database and observes the failure. Reachability confirmed: `segmentation_test.go:240` calls `Pool(t)`, `:244` calls `Fixture(...)` — the repo's only `testenv.Fixture` call — so with a live DB the Pool branch cannot mask it.
2. **GATE-06 third path (was: grep-proven)** — the same step asserts the flag+value in the real failure output; the three-`escalationPreamble` grep is now explicitly demoted to a structural check that does not on its own satisfy GATE-06.
3. **GATE-02 at the gate (was: package-only)** — step 3b runs `make gate` against the closed-port DSN and asserts the absence of `new migrator`.
4. **Requirement count (was: 12 vs an actual 16)** — all three count sites now assert entry-count == traceability-row-count before the pinned 16.
5. **GOV-01 sweep (was: unachievable as scheduled)** — see below.
6. **Criterion 9** — the guard is now run, not located; negative control confirmed sound (`git archive HEAD` + `cp` of the one declared file makes the throwaway tree byte-equivalent for that package).

**The sweep is out of the wave graph — structurally, not procedurally.** `02-05-PLAN.md` is now `02-GOV-SWEEP-RUNBOOK.md`. The rename is the mechanism: `plan-scan.cjs:141` schedules every file ending `-PLAN.md`, and `phase.cjs:797-801` computes the effective wave from the `depends_on` DAG while downgrading a disagreeing `wave:` to a warning — so clearing the frontmatter would have changed nothing. Measured: waves went from `{1,2,3}` to `{1:[02-01], 2:[02-02,02-03,02-04]}`, 0 warnings. Its logical id stays `02-05`; the sibling plans' references remain valid.

**Invoke it explicitly, after verification + UAT + security sign-off:**
`/gsd-execute-plan .planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP-RUNBOOK.md`

Its precondition proves the checkpoints COMPLETED rather than asking: each artifact's own frontmatter verdict (`passed` / `complete` / `verified` + `threats_open: 0`), each committed, and each one's latest commit a descendant of the final plan SUMMARY's commit. Checker confirmed no assertion can pass vacuously (all four expectations are non-empty, so a missing key fails) and that the `LAST_SUMMARY` loop lands on the latest of the four on linear history.

**5 warnings carried, none blocking:**

- Criterion 3 is executed but at package level, never through `make gate` as the criterion is worded. (The asymmetry with the GATE-02 fix is defensible — migrate cannot be first reporter for a filesystem condition against a live DB — but it is an asymmetry.)
- `grep -q 'new migrator'` pins the D-03 ordering to a message string this phase does not own; a reword makes it silently vacuous.
- Undeclared runtime coupling: 02-03 T1 recreates the shared compose container; 02-02 T3 and 02-04 read it via `make gate`. Same wave, no declared edge — safe only because `parallelization: false`.
- `localhost` DSNs survive the loopback rebind in 02-02, 02-03 T1 and the runbook; 02-01 T2 already switched to `127.0.0.1` and the others did not follow.
- 02-02: verify step 3 is still a bare `echo` in an assertion slot, and `DefaultTimeout`'s kill path is never exercised despite being a control on a high-rated threat.

Resume with: `/gsd-execute-phase 2` — the plan gate has passed. It will run the 4 wave plans and CANNOT reach the GOV-01 sweep; run that separately by path after verification, UAT and security sign-off. Optionally clear the 5 warnings first (none blocks execution).
Resume file: None
