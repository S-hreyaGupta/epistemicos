---
phase: 03-automated-proof
type: finding
id: FINDING-01
title: 13071ff's diagnosis of the phase-completion undercount named a mechanism that does not operate
status: closed — mechanism identified and measured; D-20 is the structural answer
found: 2026-09-03
found_by: orchestrator, during Phase 3's discussion, reading the code path instead of the finding
relates_to: [D-20, D-21, GOV-01]
is_not: a claim that GATE-06/GOV-01 changed — this document changes no requirement
---

# FINDING-01 — the phase-completion undercount's real mechanism

## 1. The original claim, restated

Commit `13071ff` ("docs(02-05): correct state.update-progress's phase-completion
undercount") recorded this diagnosis, verbatim from its own commit message:

> `gsd-tools query state.update-progress` recalculated `completed_phases` and
> `percent` from disk, reverting the sweep's correct values (2/67%) to the
> pre-sweep values (1/33%) — **its phase-completion heuristic does not recognize
> the post-checkpoint runbook's SUMMARY (`02-05-SUMMARY.md`, associated with
> `02-GOV-SWEEP-RUNBOOK.md` rather than a `*-PLAN.md` file) as completing Phase 2.**

`.planning/STATE.md`'s own `### Blockers/Concerns — added 2026-09-03` section
registered the same claim as a finding before this document existed. Both name
**SUMMARY-to-PLAN pairing** as the cause: the tool cannot associate
`02-05-SUMMARY.md` with a plan file, because there is no `02-05-PLAN.md` — the
runbook is deliberately named `02-GOV-SWEEP-RUNBOOK.md` so it falls outside the
wave graph (`plan-scan.cjs:141` schedules every file ending `-PLAN.md`). The
diagnosis reads as though the undercount is a naming-convention gap: teach the
pairing logic to recognise a runbook's summary, and Phase 2 will read complete.

That is legible and it is wrong, restated here rather than left inferable only
from the immutable commit.

## 2. Why it is wrong, and inverted

**SUMMARY-to-PLAN pairing never enters the computation that decides phase
completion.** `scanPhasePlans`'s SUMMARY/PLAN counts feed `total_plans` and
`completed_plans` — a display of *how many plans finished*, a different pair of
fields entirely. Phase completion routes through a separate function that never
looks at plan/summary pairing at all:

```
isPhaseComplete(phaseDir, deps) — .claude/gsd-core/bin/lib/verification.cjs:565
  "complete" is exactly verification.status === 'passed'.
  A ROADMAP checkbox has no machine authority and is never consulted —
  this function never reads ROADMAP.md, and it never reads plan/summary counts.
```

`verification.status` becomes `'passed'` only when `readVerificationStatus`
reads a phase's `*-VERIFICATION.md` and confirms it is not stale. The staleness
rule, `#2348`, is: **a `*-VERIFICATION.md` is stale when a summary in that
phase's directory is newer than it.**

Measured live during this phase's discussion, against the actual repository
state at the time:

| Phase | `verification.status` |
|---|---|
| 01 | `passed` |
| 02 | **`stale`** |

Phase 02 read `stale` because `02-05-SUMMARY.md` — the close sweep's own
summary — is newer than `02-VERIFICATION.md`. `02-05-SUMMARY.md` is not
*unrecognised* by anything: it **is** seen, it **is** newer than the
verification artifact, and being seen by the staleness comparison is exactly
what marks the verification stale. The pairing logic `13071ff` blamed is not in
this path at all — it feeds a different pair of counters that were never wrong.

## 3. What the wrong diagnosis would have caused

This is the part worth keeping, not merely that the diagnosis was false. The
wrong mechanism implies a specific fix: **teach the SUMMARY/PLAN pairing to
recognise a runbook's summary as completing its phase.** Had that fix been
made, it would have changed nothing observable. `completed_phases` would still
read 1, because pairing is not a term in `isPhaseComplete`'s computation at
all — fixing a function the counter does not consult cannot move the counter.
A wrong mechanism yields a wrong fix that *appears* responsive, because the
symptom (phase undercounted) and the named cause (a runbook's summary going
unrecognised) both sound plausible together, and neither was checked against
the code path that actually runs.

## 4. The class, named

This is the **second instance this week** of a registered finding describing a
mechanism that was not the one operating. The first is
`02-FINDING-01-state-authority.md`'s own normalizer diagnosis (`state.md`
section "CORRECTED 2026-09-02: the mechanism first recorded here does not
exist" — a claimed `normalizeStateStatus` fallback that was never reached).
Both explanations fit the evidence, were asserted rather than measured, and
were falsified only when someone read the code path instead of the finding
that already existed about it. Neither wrong diagnosis was malicious or
careless in isolation — each named a real function in the right subsystem —
but neither was traced to confirm it was the function actually called.

## 5. The structural consequence, and Phase 3's answer

GOV-01 mandates that a phase's close sweep run *after* verification, UAT and
security sign-off, and commit its own artifact. Combine that ordering
requirement with the staleness rule above and the consequence is structural,
not incidental to Phase 2: **any phase whose GOV-01-mandated close sweep writes
a `*-SUMMARY.md` ends that phase with a stale verification and an undercounted
`completed_phases`**, regardless of what the sweep's content says, because the
sweep's own summary is — by construction — newer than the verification
artifact it runs after.

Phase 3's answer is `03-CONTEXT.md` **D-20**: Phase 3's close sweep produces
`03-GOV-SWEEP.md` and its own commit, and writes **no** `*-SUMMARY.md`. With no
summary written, the staleness comparison has nothing newer than
`03-VERIFICATION.md` to find, so `isPhaseComplete` is not defeated by the
sweep that closes the phase.

**The SUMMARY filename is not mandated by GOV-01.** Verified: GOV-01's
requirement text (`.planning/REQUIREMENTS.md`) never mentions a summary, and
ROADMAP's Phase 2 sweep entry does not either. The "own commit and summary"
wording that Phase 2's sweep followed is Phase 2's own **D-16**, a `CONTEXT.md`
decision for that phase — not a GOV-01 obligation. So Phase 3 writing no
summary for its sweep is a **plan-shape choice**, not a requirement change, and
needs no GATE-10-style declaration.

## 6. Citation

`13071ff` is immutable. This document is the correction; the commit is the
citation. No attempt is made to alter the commit message — the house rule this
project keeps applying is do not edit the historical record, write beside it.
