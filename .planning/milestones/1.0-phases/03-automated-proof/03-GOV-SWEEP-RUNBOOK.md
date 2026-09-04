---
phase: 03-automated-proof
plan: 05  # logical id — the sibling plans reference this sweep as 03-05
type: post-checkpoint
# NOT a wave plan, and deliberately not named `*-PLAN.md`.
#
# GOV-01 obligation 3 requires this sweep to run AFTER verification, UAT and
# security sign-off. As a wave plan it could not: `/gsd-execute-phase` runs every
# wave to completion BEFORE those checkpoints happen, so the precondition below
# could never be satisfied and the sweep would halt on every run — or an executor
# would quietly weaken it to proceed, which is GOV-01's own failure reproduced
# inside GOV-01's mechanism.
#
# `wave:` and `depends_on:` are omitted rather than adjusted, because adjusting
# them would not have helped: the effective wave is computed from the depends_on
# DAG and a declared `wave:` that disagrees is a warning, not an override. The only
# thing that actually removes a file from the wave graph is its NAME —
# `plan-scan.cjs:141` schedules every file ending `-PLAN.md`. Hence the rename.
#
# Position is the mechanism. A `checkpoint:decision` was considered and rejected in
# Phase 2 and the rejection stands: it would make the ordering depend on a human
# confirming the checkpoints ran, which is an assertion that can be given without
# checking. Being unreachable until the artifacts exist is structural; being asked
# is not.
#
# Run it explicitly, after verification, UAT and security sign-off:
#   /gsd-execute-plan .planning/phases/03-automated-proof/03-GOV-SWEEP-RUNBOOK.md
runs_after: [verification, uat, security-signoff]
files_modified:
  - .planning/phases/03-automated-proof/03-GOV-SWEEP.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/STATE.md
autonomous: true
requirements: [PROOF-01, PROOF-02, PROOF-03, GATE-10]

estimate:
  tokens: 50000
  raw_tokens: 50000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "The close sweep's artifact list is DERIVED mechanically rather than typed: every tracked file under `.planning/` that names this phase number or one of its four requirement IDs, produced by a command whose exact text and output are recorded in the sweep artifact (GOV-01 obligation 3)"
    - "The derivation is reproducible — run twice it produces the same sorted list, asserted by running it twice and comparing, not claimed (GOV-01 obligation 3)"
    - "The derivation's coverage bound is restated in the artifact: coverage is artifacts that explicitly name the phase or a requirement ID, and anything else is OUT OF SCOPE BY DESIGN, not assumed covered (GOV-01 obligation 4)"
    - "Evidence is a per-artifact table, one row per derived artifact, each carrying an explicit *confirmed current* or *corrected* verdict and, for a correction, the commit that made it"
    - "The confirmed-current rows are present and are the proof the sweep ran at all — a table containing only corrections cannot distinguish a thorough sweep from one that stopped after the first finding"
    - "A correction that changes only wording re-runs nothing; a correction that changes a requirement set, an anchor or a disposition re-arms the sweep, and passes repeat until one produces zero corrections"
    - "A pass that would ADD a requirement HALTS for a human rather than re-arming — correcting what a document says about the set is a sweep, changing the set is a decision. Phase 3 performed one of each and the artifact must keep them labelled"
    - "**This sweep writes NO `*-SUMMARY.md`.** It produces `03-GOV-SWEEP.md` and its own commit. GOV-01's requirement text never mentions a summary and ROADMAP's sweep entry does not either — the 'own commit and summary' wording is Phase 2's D-16, a CONTEXT decision — so this is a plan-shape choice, not a requirement change, and needs no GATE-10-style declaration (D-20)"
    - "The divergence from Phase 2 is STATED EXPLICITLY in `03-GOV-SWEEP.md`: 02's sweep wrote a SUMMARY, 03's does not, and a reader comparing the two phases must find the reason rather than infer an inconsistency (D-20)"
    - "After this sweep, phase 03's `verification.status` is NOT stale — the mechanism measured at `03-FINDING-01-phase-completion-diagnosis.md` is that a `*-VERIFICATION.md` is stale when a summary is newer than it, and with no summary written the comparison has nothing newer to find (D-20, D-21)"
    - "This plan writes no code — no file outside `.planning/` is modified"
  artifacts:
    - path: ".planning/phases/03-automated-proof/03-GOV-SWEEP.md"
      provides: "The recorded derivation command and its output, the per-artifact evidence table with verdicts, the re-arm log, the restated coverage bound, and the explicit statement of the divergence from Phase 2's sweep shape"
      contains: "confirmed current"
  key_links:
    - from: ".planning/phases/03-automated-proof/03-GOV-SWEEP.md"
      to: "every tracked .planning/ file naming phase 3 or one of its requirement IDs"
      via: "the recorded derivation command, whose output is the evidence table's row list"
      pattern: "PROOF-0|GATE-10"
    - from: "this runbook's filename"
      to: "the wave graph it must stay out of"
      via: "not ending in `-PLAN.md`, which is the only thing `plan-scan.cjs` looks at"
      pattern: "GOV-SWEEP-RUNBOOK"
    - "The derivation is both the scope and the evidence. If the command is not recorded verbatim, a later reader cannot tell an under-scoped sweep from a thorough one — which is GOV-01's own ambiguity one level up."
    - "The absence of a SUMMARY is load-bearing, not an omission. If a future executor adds one for consistency with Phase 2, phase 03's verification goes stale and `completed_phases` undercounts — the exact mechanism `03-FINDING-01` documents. That is why the artifact must state the divergence and its reason rather than leaving the absence to be read as a slip."
  prohibitions:
    - "The sweep must not add a requirement under the guise of a correction. Correcting what a document says about the requirement set is a sweep; changing the set is a decision. A pass that would add one halts for a human and does not re-arm."
    - "No confirmed-current verdict may be written for an artifact that was not actually re-read against this phase's final requirement set, evidence, anchors and dispositions. A row that says checked without being checked is the precise failure GOV-01 exists to remove, reproduced inside GOV-01's own mechanism."
    - "This sweep must not write a `*-SUMMARY.md`, and must not be renamed to end `-PLAN.md`. Both would put it back in the wave graph or back into the staleness comparison, and each undoes a measured decision rather than a stylistic one."
---

<objective>
Run GOV-01's close sweep for Phase 3: derive the artifact list mechanically,
revalidate every derived artifact against this phase's **final** requirement set,
evidence, anchors and dispositions, correct what has gone stale with the correction
recorded rather than made silently, and re-arm until a pass produces zero corrections.

Purpose: GOV-01's finding is that **checkpoint-derived state can invalidate previously
accurate governance artifacts without changing their files.** Phase 3 is a phase whose
own discussion changed its requirement set (GATE-10), corrected one of its success
criteria (SC-5), and corrected a recorded diagnosis (D-21) — so the assumption that
its governance artifacts are current *because nobody edited them* is exactly the
assumption GOV-01 forbids.

Output: `.planning/phases/03-automated-proof/03-GOV-SWEEP.md`, and its own commit.

## What is different about this sweep, and why (D-20)

**Phase 2's sweep wrote `02-05-SUMMARY.md`. This one writes no summary at all.**

That is not a style change and it is not an omission. `isPhaseComplete` is
`verification.status === 'passed'`, and the staleness rule is that a
`*-VERIFICATION.md` is stale when a summary is newer than it. GOV-01 mandates that the
close sweep run *after* verification and commit — so **any** phase whose sweep writes
a SUMMARY ends with stale verification and an undercounted phase. Measured live during
Phase 3's discussion: phase 01 read `passed`, phase 02 read **`stale`**, because
`02-05-SUMMARY.md` is newer than `02-VERIFICATION.md`. With no summary written, the
comparison has nothing newer to find.

**And the SUMMARY filename is not mandated.** Verified: GOV-01's requirement text never
mentions a summary, and ROADMAP's sweep entry does not either. The "own commit and
summary" wording is Phase 2's **D-16**, a CONTEXT decision. So this is a plan-shape
choice, it costs nothing, and it needs no GATE-10-style declaration.

**The divergence must be stated in `03-GOV-SWEEP.md` itself**, not only here: a reader
comparing the two phases must find the reason rather than infer an inconsistency, and
a future executor adding a summary "for consistency" would silently reintroduce the
undercount.
</objective>

<execution_context>
@C:/EpistemicOS/epistemicos-gsd-pilot/.claude/gsd-core/workflows/execute-plan.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/03-automated-proof/03-CONTEXT.md
@.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Derive the artifact list mechanically, and prove the derivation reproduces</name>

  <precondition>
**GOV-01 obligation 3 requires this sweep to run after the checkpoints, not before.**
Assert all four and HALT if any fails:

1. `.planning/phases/03-automated-proof/03-VERIFICATION.md` exists and its
   frontmatter `status` is `passed`.
2. `.planning/phases/03-automated-proof/03-UAT.md` exists and its frontmatter
   `status` is `complete`, with every raised issue dispositioned.
3. `.planning/phases/03-automated-proof/03-SECURITY.md` exists, is signed, and reports
   `threats_open: 0`.
4. `03-01-SUMMARY.md`, `03-02-SUMMARY.md`, `03-03-SUMMARY.md` and `03-04-SUMMARY.md`
   all exist — every wave plan has landed.

This precondition is the whole reason this file is not named `*-PLAN.md`. If any of
the four is missing, **HALT and report which**. Do not proceed on a partial set and do
not weaken the check to make progress: a sweep that runs before the checkpoints
inspects a requirement set the checkpoints have not finished changing, which is the
exact ordering failure GOV-01's four tabulated instances share.

Also run `make planning-parity PHASE=3` and require exit 0 before deriving anything. A
sweep over a requirement set the two documents disagree about would produce an evidence
table that is confidently wrong.
  </precondition>

  <files>.planning/phases/03-automated-proof/03-GOV-SWEEP.md</files>

  <read_first>
    - `.planning/REQUIREMENTS.md` GOV-01 — the finding, its four-row table of instances, and **obligations 3 and 4** verbatim: the derivation rule, its three properties (bounded, reproducible, self-extending), and the coverage bound with the `PROJECT.md` measurement that produced it
    - `.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP.md` — the derivation command verbatim (`git ls-files '.planning/*'` plus the ID/phase-number match), the per-artifact evidence table's exact shape, and the re-arm/halt rule. This is the format to reproduce, with Phase 3's IDs substituted
    - `.planning/phases/03-automated-proof/03-CONTEXT.md` — **D-20** for this sweep's shape, and `<deferred>` item 2 for why the derivation is NOT amended here
  </read_first>

  <behavior>
    - The derivation command is a single recorded shell pipeline over `git ls-files '.planning/*'`, matching this phase's number or any of `PROOF-01`, `PROOF-02`, `PROOF-03`, `GATE-10`.
    - Run twice, it emits byte-identical sorted output.
    - The derived list is non-empty — this phase's ROADMAP section, REQUIREMENTS entries, phase directory and STATE entries all name it, so a zero-row list is a defect in the derivation, not a clean sweep.
    - The list is deduplicated: an artifact naming both the phase number and a requirement ID appears exactly once.
    - `Phase 3` does not match `Phase 30` or a decimal phase such as `Phase 3.1`.
  </behavior>

  <action>
Create `.planning/phases/03-automated-proof/03-GOV-SWEEP.md`.

Run the derivation exactly as GOV-01 obligation 3 states it — every tracked file under
`.planning/` that names this phase number or one of its requirement IDs — reusing
`02-GOV-SWEEP.md`'s recorded command with Phase 3's four IDs substituted. **Record the
command verbatim in the artifact**, along with its full sorted output. The derivation is
both the scope and the evidence: scope and evidence are the same object, so an
under-scoped sweep cannot present itself as a thorough one.

Run it a second time and compare byte-for-byte. Record both the fact and the comparison
method — reproducibility is checkable in a way a judgement call is not, and it is one of
the three properties that made this the right rule.

Restate the **coverage bound** (obligation 4) in the artifact rather than assuming the
reader knows it: coverage is artifacts that explicitly name the phase or a requirement
ID, and **anything else is out of scope by design, not assumed covered**. Name the
bound's two demonstrated instances so the reader learns the mechanism has an edge from
the register rather than from the next escape: `.github/workflows/ci.yml`'s job name,
found by a human running Phase 2 UAT test 12; and `internal/platform/gate/harness.go`'s
timeout rationale, found by a cold-cache measurement during Phase 3's discussion.
**Neither was found by a sweep. Both were found by someone running something.**

Record explicitly that the derivation was **not amended** for this phase, and why: the
IDs-only repo-wide amendment is registered as deferred item 2, refused for Phase 3
deliberately because Phase 3's own close sweep would then run against a rule the phase
changed — a check validating its own amendment, the same self-reference that
disqualified VERIFICATION.md as GOV-01's home. Note the measurement that sizes it (5.3s
over 227 tracked files, derived set 51 to 54, one false positive) and that it is to be
decided at milestone close.

Fail loudly on a zero-row list.
  </action>

  <verify>
    <automated>make planning-parity PHASE=3</automated>
    <automated>test -f .planning/phases/03-automated-proof/03-GOV-SWEEP.md &amp;&amp; grep -c 'git ls-files' .planning/phases/03-automated-proof/03-GOV-SWEEP.md</automated>
  </verify>

  <acceptance_criteria>
    - `03-GOV-SWEEP.md` contains the derivation command verbatim and its full sorted output, and the output has at least one row.
    - The artifact records that the derivation was run twice and that the two outputs were byte-identical, naming the comparison method.
    - The artifact restates the coverage bound and names both demonstrated instances (`ci.yml`, `harness.go`) with how each was found.
    - The artifact records that the derivation rule was not amended for this phase, with the self-reference reason and the deferred item's measurement.
    - The four preconditions were each checked and their verdicts recorded; `make planning-parity PHASE=3` exited 0 and its exact line is quoted.
    - No file outside `.planning/` was modified.
  </acceptance_criteria>

  <done>
The sweep's scope is a mechanically derived, reproducible, non-empty, deduplicated list
of tracked `.planning/` artifacts naming phase 3 or one of its four requirement IDs, and
the command that produced it is on the record. The coverage bound is restated with both
of its demonstrated escapes, and the decision not to amend the rule in this phase is
recorded with its reason.
  </done>
</task>

<task type="auto">
  <name>Task 2: Revalidate each derived artifact and write the per-artifact evidence table</name>

  <files>.planning/phases/03-automated-proof/03-GOV-SWEEP.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md, .planning/STATE.md</files>

  <read_first>
    - Every file in Task 1's derived list — actually read each one against this phase's final requirement set, evidence, anchors and dispositions. A verdict written without the read is the failure this mechanism exists to remove
    - `.planning/phases/03-automated-proof/03-VERIFICATION.md`, `03-UAT.md`, `03-SECURITY.md` — the checkpoint outputs whose dispositions may have invalidated earlier claims
    - `.planning/phases/03-automated-proof/03-CONTEXT.md` — the 21 decisions, so a document claiming something a decision contradicts is caught
    - `.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP.md` — the evidence table's exact column shape and verdict vocabulary
  </read_first>

  <behavior>
    - Every derived artifact has exactly one row, and every row carries a verdict of `confirmed current` or `corrected`.
    - Every `corrected` row names the commit that made the correction and restates what the artifact said before.
    - The table contains at least one `confirmed current` row — a table of only corrections cannot distinguish a thorough sweep from one that stopped at the first finding.
    - Rows for `ROADMAP.md`, `REQUIREMENTS.md` and `STATE.md` specifically check the three governance acts this phase performed: SC-5's correction, GATE-10's amendment, and D-21's diagnosis correction.
    - No correction adds, strengthens or rewords a requirement.
  </behavior>

  <action>
Revalidate each derived artifact against this phase's **final** state and write the
per-artifact evidence table into `03-GOV-SWEEP.md`, one row per derived artifact,
reproducing `02-GOV-SWEEP.md`'s column shape.

For each artifact, check the four things GOV-01 names — requirement set, evidence set,
commit and base anchors, recorded dispositions — and additionally check the three claims
this phase's own history makes most likely to have gone stale:

1. **Anything asserting Phase 3's requirement set is three IDs.** GATE-10 made it four.
   A document still saying three is stale even though nobody edited it, which is
   GOV-01's finding exactly.
2. **Anything quoting SC-5's original wording** — "Removing or bypassing the escalation
   mechanism makes these three tests fail." That wording was corrected; a quotation of it
   presented as current is stale.
3. **Anything repeating `13071ff`'s diagnosis** — that the phase-completion heuristic
   fails to recognise the runbook's SUMMARY. That is the corrected claim; see
   `03-FINDING-01-phase-completion-diagnosis.md`.

Each row gets `confirmed current` or `corrected`. A `corrected` row names the commit and
**restates what the artifact said before**, so the correction is legible as a correction
and not as a document that was always right.

Then write the **divergence statement** D-20 requires, as its own section of
`03-GOV-SWEEP.md`: Phase 2's sweep wrote `02-05-SUMMARY.md`; this sweep writes none;
the reason is that `isPhaseComplete` is `verification.status === 'passed'` and a
`*-VERIFICATION.md` is stale when a summary is newer than it, so any phase whose
GOV-01-mandated post-checkpoint sweep writes a summary ends with stale verification and
an undercounted phase — measured live as phase 01 `passed` and phase 02 `stale`. Record
that GOV-01's text never mentions a summary and that the "own commit and summary"
wording is Phase 2's own D-16, so this is a plan-shape choice rather than a requirement
change. State plainly that a future executor adding a summary here for consistency would
reintroduce the undercount.

Apply corrections with scoped edits. Never rewrite `ROADMAP.md`, `REQUIREMENTS.md` or
`STATE.md` wholesale — a whole-file write destroys every entry outside the diff window.
  </action>

  <verify>
    <automated>grep -c 'confirmed current' .planning/phases/03-automated-proof/03-GOV-SWEEP.md</automated>
    <automated>make planning-parity PHASE=3 &amp;&amp; make gate</automated>
  </verify>

  <acceptance_criteria>
    - The evidence table has exactly one row per file in Task 1's derived list, and the row count equals the derived list's line count.
    - At least one row reads `confirmed current`, and every `corrected` row names a commit and restates the prior text.
    - The artifact contains a section stating the divergence from Phase 2's sweep shape, naming `isPhaseComplete`, the staleness rule, the measured `passed`/`stale` pair, and the fact that GOV-01's text never mentions a summary.
    - Every row's verdict corresponds to a read that actually happened — the SUMMARY of this sweep names, for each row, the specific claim checked.
    - `make planning-parity PHASE=3` still exits 0 and `make gate` is green.
    - No file outside `.planning/` was modified.
  </acceptance_criteria>

  <done>
Every derived artifact carries an explicit verdict backed by a read, every correction
restates what it replaced, and the confirmed-current rows prove the sweep was thorough
rather than truncated. `03-GOV-SWEEP.md` states why this sweep writes no summary, in
terms a reader comparing the two phases can act on.
  </done>
</task>

<task type="auto">
  <name>Task 3: Re-arm until a pass produces zero corrections, halt on a scope change, and close</name>

  <files>.planning/phases/03-automated-proof/03-GOV-SWEEP.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md, .planning/STATE.md</files>

  <read_first>
    - `.planning/phases/03-automated-proof/03-GOV-SWEEP.md` (Tasks 1 and 2 — the derivation, the evidence table, the divergence statement)
    - `.planning/REQUIREMENTS.md` GOV-01 — the re-arm rule and the halt case, and the sentence separating a correction from a decision
    - `.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP.md` — the re-arm log's shape, and the record of its two passes terminating on the second with zero corrections
    - `.planning/STATE.md` `### Pending Todos` — the carried flagged assumptions and unclassified probe rows that need a disposition recorded here rather than left open
  </read_first>

  <behavior>
    - A pass that produced only wording corrections terminates the sweep.
    - A pass that changed a requirement set, an anchor or a disposition re-arms it, and passes repeat until one produces zero corrections.
    - A pass that would ADD a requirement halts for a human and does not re-arm.
    - Each pass's classification is recorded per correction, not applied silently.
    - The final commit contains `03-GOV-SWEEP.md` and any corrected `.planning/` files, and **no `*-SUMMARY.md`**.
  </behavior>

  <action>
Classify every correction Task 2 made into exactly one of three kinds, and record the
classification **per correction** rather than applying it silently — a correction
classified wrongly either terminates the sweep early or spins it forever:

- **Wording only** — re-runs nothing.
- **Requirement set, anchor or disposition changed** — re-arms the sweep. Run another
  pass from Task 1's derivation, because the derived list itself may have changed.
- **Would ADD a requirement** — **HALT for a human.** Correcting what a document says
  about the requirement set is a sweep; changing the set is a decision. Phase 3 already
  performed one of each and kept them labelled; this sweep does not get to blur them
  because blurring is convenient.

Repeat until a pass produces zero corrections. Record the re-arm log — one entry per
pass, with the pass number, the corrections it produced, their classifications, and the
termination reason.

Then dispose of the carried items so they do not silently outlive the phase:

- The unclassified probe rows and open contract decisions carried in STATE.md's
  `### Pending Todos` — record for each whether Phase 3 resolved it, whether it is
  covered by pointer, or whether it carries forward. No agent in this pipeline has
  authority to dismiss a probe row that returned no category, so "carries forward" is a
  legitimate outcome and silence is not.
- The five deferred entries 03-04 registered — confirm each is present in STATE.md with
  its measurement intact after this sweep's edits.

Update ROADMAP.md's Progress table row for Phase 3 and STATE.md's position, with scoped
edits only.

**Then close, and note what closing does NOT include.** Commit `03-GOV-SWEEP.md`
together with any `.planning/` files this sweep corrected, in its own commit.

**Write no `*-SUMMARY.md`.** Not `03-05-SUMMARY.md`, not any other. This is D-20 and it
is the operative instruction of this task: with no summary written, the staleness
comparison has nothing newer than `03-VERIFICATION.md` to find, so phase 03's
`verification.status` stays `passed` and `completed_phases` counts it. Verify after
committing that the phase reads complete rather than assuming it does.
  </action>

  <verify>
    <automated>ls .planning/phases/03-automated-proof/ | grep -c 'SUMMARY'</automated>
    <automated>make planning-parity PHASE=3 &amp;&amp; make gate &amp;&amp; git status --porcelain</automated>
  </verify>

  <acceptance_criteria>
    - The re-arm log in `03-GOV-SWEEP.md` has one entry per pass, each recording its corrections, their per-correction classifications, and the termination reason; the final pass produced zero corrections.
    - `ls .planning/phases/03-automated-proof/ | grep 'SUMMARY'` lists exactly the four wave-plan summaries `03-01-SUMMARY.md` through `03-04-SUMMARY.md` — **no fifth summary exists**, and none was created by this sweep.
    - No file in `.planning/phases/03-automated-proof/` other than the four wave plans ends `-PLAN.md`; this runbook does not.
    - Phase 03's `verification.status` reads `passed` after the sweep's commit, verified by inspection rather than asserted.
    - Every carried pending todo and unclassified probe row has a recorded disposition — resolved, covered by pointer, or carries forward. None is dropped and none is dismissed.
    - `make planning-parity PHASE=3` exits 0, `make gate` is green, and `git status --porcelain` is empty after the commit.
    - No file outside `.planning/` was modified by this runbook.
  </acceptance_criteria>

  <done>
The sweep terminated on a pass producing zero corrections, with every correction
classified on the record and every carried item dispositioned. `03-GOV-SWEEP.md` and the
corrected `.planning/` files are committed together, and **no summary was written** — so
phase 03's verification is not marked stale by its own close sweep, which is the whole
point of D-20 and the practical repair of the mechanism `03-FINDING-01` documents.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Checkpoint outputs → the sweep's scope | Verification, UAT and security sign-off can change the requirement set, anchors and dispositions the sweep validates against; running before them inspects an unfinished set |
| Derivation command → the evidence table's rows | The command's output IS the scope, so a narrowed command narrows the evidence without looking narrowed |
| Sweep corrections → the requirement set | A correction that crosses from wording into scope changes what future phases plan against |
| Sweep artifacts → the phase-completion computation | Writing a summary here marks verification stale and undercounts the phase — a documentation act with a mechanical consequence |

## STRIDE Threat Register

ASVS L1; `security_block_on: high`. Severity is impact x likelihood.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-03-13 | Elevation of Privilege | a sweep silently adding or strengthening a requirement | **high** | mitigate | GOV-01's own rule, applied to GOV-01's own mechanism: a pass that would add a requirement HALTS for a human and does not re-arm. Task 3 classifies every correction into wording / set-anchor-disposition / would-add, records the classification per correction, and the acceptance criteria require the log rather than the conclusion |
| T-03-14 | Repudiation | a `confirmed current` verdict written without the read | **high** | mitigate | The precise failure GOV-01 exists to remove, reproduced inside GOV-01's mechanism. Bounded by requiring the SUMMARY of this sweep to name, per row, the specific claim checked — so a row asserting a verdict without a checkable claim behind it is visible |
| T-03-15 | Tampering | an under-scoped derivation presenting as thorough | **high** | mitigate | Scope and evidence are the same object: the derivation command is recorded verbatim, its output is the row list, it is run twice and compared byte-for-byte, and a zero-row list fails loudly. A narrowed command therefore produces a visibly narrowed table rather than a confidently short one |
| T-03-16 | Denial of Service | this runbook re-entering the wave graph | medium | mitigate | Its filename does not end `-PLAN.md`, which is the only property the scheduler inspects, and `wave:`/`depends_on:` are omitted rather than adjusted because a declared wave that disagrees with the DAG is a warning, not an override. An acceptance criterion asserts no file other than the four wave plans in this directory ends `-PLAN.md` |
| T-03-17 | Repudiation | a future executor adding a summary for consistency | medium | mitigate | The absence is load-bearing and the artifact says so. `03-GOV-SWEEP.md` carries the divergence statement with the measured mechanism, and an acceptance criterion counts the summaries in the phase directory and requires exactly four |
| T-03-SC | Tampering | dependency installation | low | accept | No code, no package-manager install, no dependency change. This runbook modifies only files under `.planning/` |
</threat_model>

## Artifacts this phase produces

For this runbook's purposes the code surface is what the evidence table must be checked
against; it is listed in full so a sweep executor does not have to reconstruct it.

**New package — `internal/platform/gateproof`** (test-only): `unreachableDSN`,
`fixturePathSuffix`, `lineContainsBoth`, `requireIntact`, `TestLineContainsBoth_Control`,
`TestGateproof_NoParallelMarker` (`gateproof_test.go`); `materializeTree`,
`stripEscalationExport`, `TestMaterializeTree_Control` (`tree_test.go`);
`TestPROOF01_GateNamesUnsetURL` (`proof01_test.go`);
`TestPROOF02_GateNamesUnreachableHost` (`proof02_test.go`);
`TestGateOrdersPreflightBeforeMigrate` (`ordering_test.go`); `breakFixture` and
`TestPROOF03_GateNamesUnreadableFixture` (`proof03_test.go`). Each of the three
`TestPROOF0N_*` functions carries two subtests, `intact_tree` and
`defeated_tree_control`.

**Modified — `internal/platform/gate`**: the new exported struct field `RunOptions.Dir`,
and `DefaultTimeout`'s corrected, requirement-tagged rationale comment (value unchanged).

**Governance artifacts**: `03-FINDING-01-phase-completion-diagnosis.md` (03-04), this
runbook, and `03-GOV-SWEEP.md` — with **no `*-SUMMARY.md`** accompanying the sweep.

## Probe-row accounting (spec-less fallback)

The phase's 10 probe rows were authored into `must_haves.truths` by the three code plans
(9 resolved explicit, 1 resolved backstop, 0 unresolved, 0 dismissed, 0 dropped). This
runbook authors none of its own — it changes no behavior. Task 3 disposes of the
**carried** unclassified probe rows E1, E11 and E12 from Phases 1 and 2, which are open
in STATE.md's Pending Todos and which no agent in this pipeline has authority to dismiss.

<verification>
- The sweep ran after verification, UAT and security sign-off, and the precondition that enforces that was checked rather than assumed.
- The artifact list was derived mechanically, recorded verbatim, and proven reproducible by a second run.
- The coverage bound is restated with both of its demonstrated escapes, neither of which a sweep found.
- Every derived artifact carries a verdict backed by a read; corrections restate what they replaced.
- The sweep re-armed on any set/anchor/disposition change and terminated on a pass with zero corrections.
- A pass that would have added a requirement would have halted; none did, and that is recorded rather than implied.
- **No `*-SUMMARY.md` was written**, the divergence from Phase 2 is stated with its measured mechanism, and phase 03's verification is confirmed not stale afterwards.
- `make planning-parity PHASE=3` is green and `make gate` is green.
</verification>

<success_criteria>
- ROADMAP §Phase 2's criterion 11 shape is honoured for Phase 3: a post-checkpoint stale-artifact sweep revalidated the governance artifacts against the phase's final requirement set, evidence, anchors and dispositions, with every result confirmed or corrected on the record.
- Phase 3's requirement set — PROOF-01, PROOF-02, PROOF-03, GATE-10 — is closed in REQUIREMENTS.md.
- Phase 03 reads complete, and its verification is not marked stale by its own close sweep.
- No file outside `.planning/` was modified by this runbook.
</success_criteria>

<output>
Create `.planning/phases/03-automated-proof/03-GOV-SWEEP.md` when done.

**Do NOT create any `*-SUMMARY.md` for this sweep.** That is D-20, and it is the
mechanism rather than a preference: a summary newer than `03-VERIFICATION.md` marks the
verification stale, `isPhaseComplete` then returns false, and `completed_phases`
undercounts the phase. The sweep's record is `03-GOV-SWEEP.md` and its own commit.
</output>
