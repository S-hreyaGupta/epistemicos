---
phase: 02-enforcement-and-a-single-gate-definition
type: finding
id: FINDING-01
title: STATE.md has many writers and no owner, so a correction to it cannot be durable
status: open — instance fixed, class open; option 2 escalated to Alex. Mechanism CORRECTED 2026-09-02.
found: 2026-09-02
found_by: orchestrator, while correcting STATE.md for the second time in one session
relates_to: [GOV-01]
is_not: an instance of GOV-01
---

# FINDING-01 — STATE.md's authority

## The finding

**Executors write `STATE.md` mid-phase. A hand-correction to it survives only until
the next executor writes it.** So `STATE.md` cannot be durably fixed by any
end-of-phase mechanism, GOV-01's close sweep included: the sweep produces a
correction at close, and the next phase's first executor overwrites it.

This is a statement about **where `STATE.md`'s authority sits**, not about any
particular stale value.

## Evidence, measured this session

`STATE.md` was corrected by hand at `20bd4ce` — the three contradictions that had
already misled a fresh session that morning. Three executor commits then rewrote
it:

| Commit | Writer | |
|---|---|---|
| `20bd4ce` | orchestrator (hand correction) | the three contradictions fixed |
| `8a23cb6` | 02-01 executor | rewrote STATE |
| `9917290` | 02-03 executor | rewrote STATE |
| `2d52a1e` | 02-02 executor | rewrote STATE |

State at `2d52a1e`, before the correction that follows this finding:

- `status: planning` — three plans had executed.
- `last_activity_desc: Phase 01 complete, transitioned to Phase 2` — from Phase 1,
  survived every rewrite.
- `state_head: bf4e0c3` — not HEAD, and not even 02-02's final commit.
- Body: *"3 of 4 wave plans complete (02-01, 02-03 done; 02-02, 02-04 remaining)"* —
  the count and the list contradict each other. 02-02 **was** complete.
- Body `Status:` still described 02-03 as the most recent work, written by the
  02-02 executor, which did not update the line it inherited.

The last writer left the body describing someone else's plan as the latest event.
That is the shape of the problem: each writer updates the fields it knows about and
inherits the rest without reading them.

## Why this is NOT an instance of GOV-01

GOV-01's instances are documents **nobody edited**, which were accurate when
written and were falsified by a decision taken afterwards. Its framing, Alex's:
*checkpoint-derived state can invalidate previously accurate governance artifacts
without changing their files.*

`STATE.md` is the opposite case. It is a document that **is** edited, constantly, by
many writers, none of whom owns it. It does not go stale because nobody touched it;
it goes stale **because several agents touch it and each one only partially.**

The distinction matters because it determines what fixes it. GOV-01's mechanism is
a periodic re-read of files assumed stable between edits. That mechanism cannot
help here — re-reading a file that is about to be overwritten by the next executor
produces a correction with a known expiry. Registering this under GOV-01 would put
it under a mechanism structurally unable to close it.

## CORRECTED 2026-09-02: the mechanism first recorded here does not exist

**This section previously claimed a normalizer bug. That claim was false, and it was
asserted rather than measured. It is corrected in place, and the original claim is
restated below so the correction is legible rather than silent.**

**What this file originally said.** That `status:` is derived; that
`normalizeStateStatus` (`state-document.cjs:387`) matched the body `Status:` line by
substring; that a line matching none of its keywords yielded `unknown`; and that
`state.cjs:2359-2361` then silently preserved the previous value — producing
`status: planning` while three plans had executed.

**Both halves are wrong.**

1. `normalizeStateStatus` opens with `let normalizedStatus = status || 'unknown'`.
   An unrecognised **non-empty** line is returned VERBATIM, not mapped to `unknown`.
   Measured directly:

   ```
   "02-03 (CI collapse) executed and committed"  ->  "02-03 (CI collapse) executed and committed"
   ""                                            ->  "unknown"
   undefined                                     ->  "unknown"
   "Ready to execute"                            ->  "executing"
   ```

   `unknown` requires a **missing** `Status:` line, which never occurred.

2. The preserve branch was never reached anyway, because **the executor path never
   re-derives frontmatter at all.** `grep` for `state sync` / `syncStateFrontmatter`
   across `execute-plan.md` and `agents/gsd-executor.md` returns nothing.

**The actual mechanism, traced from git rather than inferred from code.**
`status: planning` was written by the ORCHESTRATOR at `20bd4ce` — the "fix the three
contradictions" commit. The three executor commits that followed changed only the
body `Status:` line and never touched the frontmatter. `git show` confirms not one of
them carries a `±status:` pair:

| Commit | Writer | Frontmatter `status:` |
|---|---|---|
| `20bd4ce` | orchestrator | `executing` -> **`planning`** |
| `8a23cb6` | 02-01 executor | untouched (body `Status:` only) |
| `9917290` | 02-03 executor | untouched (body `Status:` only) |
| `2d52a1e` | 02-02 executor | untouched (body `Status:` only) |
| `d17051a` | orchestrator | corrected back to `executing` |

So the stale value was the orchestrator's own, left in place while the body moved on
beneath it. No fallback fired. No normalizer was involved.

**How the false claim got written.** The orchestrator read the fallback at
`state.cjs:2359-2361`, saw a mechanism that would produce the observed symptom, and
recorded it as traced — in this file and in `d17051a`'s commit message — without
checking whether that code ran. An explanation that fits the evidence, asserted
rather than measured. It was falsified only when the operator asked for the actual
writer. That is the same defect class this milestone exists to remove, committed
while documenting it.

**What this does to the finding.** The core claim is unchanged and now BETTER
evidenced: STATE.md has many writers and no owner. It is also sharper than first
stated — the file has **two independently hand-edited surfaces**, frontmatter and
body, and the machine-read one is updated by **nobody** in the normal execution path.
The executor contract tells executors to "update STATE.md"; they update the body.

## Disposition

**Option 3 (make the normalizer loud) is WITHDRAWN — it has no target.** It was
selected by the operator on 2026-09-02 on the strength of the false mechanism above,
implemented, and then reverted unapplied when the trace showed the guarded branch is
never taken. It would have guarded a missing `Status:` line, which is not the bug.

**Option 1 (single writer)** remains the heaviest and is not proposed.

**Landed now — the instance fix.** The executor path calls `state.sync` after its
STATE.md write, so the frontmatter is re-derived by the writer that just changed the
body. This closes THIS instance. It does not remove the class: STATE.md still has
many writers, and a writer that forgets the call still leaves the frontmatter stale.

**Escalated to Alex — option 2, the real fix, as a design decision and not a
disposition.** Anything reconstructible from disk and git (plan/summary pairs, HEAD,
counts, phase position) is DERIVED rather than authored, so a partial writer cannot
leave a stale field at all. The reason this is the right fix is now sharper than when
it was first proposed: the frontmatter is **already meant to be derived** — the
executor path simply never invokes the derivation. Option 2 makes that intent true
rather than aspirational.

**Stated plainly, because it must not be misread:** neither the withdrawn option 3
nor the landed sync-call fix makes STATE.md stop going stale. STATE.md still has many
writers and no owner. The sync call removes one path to staleness; it does not remove
the class. **FINDING-01 stays OPEN** until option 2 is decided.

**Shape constraint — see FINDING-02.** Every candidate fix here lives in gitignored
`.claude/`: `state.cjs` for option 3, `agents/gsd-executor.md` for the sync call. All
are reverted silently by `/gsd-update`. So each must ship with a durable instruction
in the TRACKED planning docs, or the guard vanishes and nothing records that it ever
existed. That constraint shaped this decision and is registered as its own class in
`02-FINDING-02-gitignored-instrumentation.md`.

## What was done here

- STATE.md corrected to the measured tree (`d17051a`), with its expiry stated.
- The normalizer claim CORRECTED above rather than deleted, so the false diagnosis and
  its falsification are both on the record.
- Option 3 implemented, then reverted unapplied once the trace falsified its premise.
- The sync-call instance fix landed, with a tracked counterpart per FINDING-02.
- Option 2 escalated to Alex as a design decision.

This file's own history is the finding in miniature: an artifact that was accurate
when written, falsified by a later measurement, and corrected only because someone
asked for the evidence behind it.
