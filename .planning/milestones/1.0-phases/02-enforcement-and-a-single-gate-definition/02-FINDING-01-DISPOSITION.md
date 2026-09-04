---
phase: 02-enforcement-and-a-single-gate-definition
type: disposition
id: FINDING-01-DISPOSITION
title: Option 2 accepted — derived operational state, not authored
status: accepted — not yet implemented
decided_by: Alex Zamurko
decided: 2026-09-03
registered: 2026-09-04
registered_by: orchestrator, verbatim per Alex's 2026-09-03 instruction to record the class fix verbatim rather than paraphrase it
relates_to: [FINDING-01]
is_not: an implementation — this document registers the decision only
---

# FINDING-01 — Disposition (Option 2, accepted)

This is Alex Zamurko's disposition of the option escalated to him at
[[02-FINDING-01-state-authority]]'s Disposition section — the paragraph beginning
"Escalated to Alex — option 2, the real fix, as a design decision and not a
disposition." Registered here as its own document, separate from the finding
itself, because this is the disposition and not the finding.

**This document registers the decision. It does not implement it.** No code change
accompanies this file — no edit to `state.cjs`, `agents/gsd-executor.md`, or any
other mechanism, and no STATE.md derivation exists yet as a result of this file.
Implementing option 2 remains open work, tracked via `FINDING-01` staying open
until it lands.

## Alex's disposition, verbatim

He was told on 2026-09-03 this would be recorded verbatim rather than paraphrased.
It is reproduced exactly as sent, with no rewording:

> Option 2 — ACCEPT
>
> Class fix:
> Derived operational state MUST NOT be persisted as independently mutable
> project state when it can be deterministically reconstructed from authoritative
> planning artifacts and repository history.
>
> STATE.md may retain non-derivable decisions/context, but generated phase,
> status, progress and next-action fields become derived views.

**Sent by:** Alex Zamurko
**Date:** 2026-09-03

## What this changes and does not change

`FINDING-01`'s own core claim — STATE.md has many writers and no owner, and a
hand-correction to it survives only until the next writer overwrites it — is
unaffected by this disposition; the class fix above is the answer to it, not a
restatement of it. The three prior paraphrases of this decision in the repository
(`.planning/STATE.md`'s "ESCALATED TO ALEX — FINDING-01 option 2" entry,
`02-FINDING-01-state-authority.md`'s own Disposition section, and
`.planning/GSD-PILOT-REPORT.md`'s Finding 1) all describe the *shape* of option 2
accurately, but none of them carries Alex's actual wording — this file is now that
source, and the paraphrases should be read as summaries of it rather than as
independent statements of the rule.

## Cross-reference

Answers the escalation at [[02-FINDING-01-state-authority]] (Disposition section):
"Escalated to Alex — option 2, the real fix, as a design decision and not a
disposition." That escalation is the finding's open question; the text above is
Alex's answer to it, verbatim.
