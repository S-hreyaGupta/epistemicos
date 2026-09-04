---
phase: 02-enforcement-and-a-single-gate-definition
plan: 04
status: complete
executed: 2026-09-02
executed_by: orchestrator (inline)
tasks: 3
tasks_complete: 3
commits: [a44b040, 18c94f6, 18453ce]
base: 2d52a1e
requirements-touched: [GOV-01]
requirements-completed: []
---

# 02-04 Summary — GOV-01's mechanism

GOV-01's **mechanism** only. The close sweep is not run here; it lives in
`02-GOV-SWEEP-RUNBOOK.md` and is deliberately outside the wave graph. GOV-01 is
left **Pending** — its closure is the runbook's job.

## Execution note: this plan was executed inline, not by a subagent

Two executor subagents dispatched for this plan were killed by the stall watchdog
(no progress for 600s). The first left nothing. The second wrote
`scripts/planning-parity.sh` and died before ever running it, leaving the file
untracked in the working tree with no commit and no record. The orchestrator
finished the plan inline, where command pacing is controlled.

This matters for the record: **the script was authored by a subagent that never
executed it.** Every check below was run for the first time by the orchestrator,
and two of them failed on first run.

## Tasks

| Task | Commit | What landed |
|---|---|---|
| 1. Parity check + Make target | `a44b040` | `scripts/planning-parity.sh`, `make planning-parity PHASE=n` |
| 2. PROJECT.md requirement-ID tags | `18c94f6` | 9 distinct IDs where there were 0 |
| 3. GOV-01's obligations in GOV-01's text | `18453ce` | Four obligations moved out of CONTEXT.md |

## Defects found by RUNNING the checks

Three, none of which reading would have caught.

**1. `SHA-256` parsed as a requirement ID.** The script's pattern
`[A-Z]{2,}-[0-9]+` matched `SHA-256` in PROJECT.md, so every phase reported a hash
algorithm as an unknown requirement and the check failed on a correct tree.
Requirement IDs are two digits — the convention every other parser in this phase
already uses, and one all 16 current IDs obey. Narrowed to `[A-Z]{2,}-[0-9]{2}`.

**2. Literal backspace bytes in the fix.** The two-digit width needs a word
boundary, or `SHA-256` still matches as `SHA-25`. The patch that applied `\b` wrote
byte `0x08` into the script instead of the two characters `\b`, and the script then
matched nothing at all — `SET_A` came back empty and all ten Phase 2 IDs were
reported as missing from ROADMAP. Replaced with `grep -w`, which needs no escaping
and cannot be corrupted the same way. **This defect was introduced by the
orchestrator's own repair of defect 1**, and found only because the check was
re-run rather than assumed fixed.

**3. Task 2 verify step 4 counts the table header as a data row.** Its pattern
`^\| [^-|].*\|.*\|.*\|$` excludes the separator row (which begins `|-`) but not the
header (`| Decision | Rationale | …`). It reports 7 rows against 6 taggable ones,
so it can never pass — the header would have to contain a requirement ID.
Re-run excluding the header: `ROWS=6, TAGGED=6`. Recorded as a Rule-1 deviation in
`18c94f6`; no content was altered to suit the check.

## Verification — all of Task 1's nine steps, run

- Phases 1, 2, 3 all agree: 2, 10, 3 IDs compared, exit 0.
- **CONTROL:** with `GOV-01` removed from ROADMAP's Phase 2 line in a scratch copy,
  the check exits non-zero **and names `GOV-01`**. That second assertion is what
  separates "failed for the intended reason" from "never ran" — the property
  02-03's negative control lacked.
- A PROJECT.md tag absent from the traceability table exits non-zero naming `GATE-99`.
- No argument → non-zero, names the phase argument. Phase 97 → non-zero (an absent
  section is a failure, not a vacuously agreeing empty set). `Phase 2` does not
  match `Phase 21`.
- Two runs byte-identical — D-14's reproducibility property, first exercised here.
- `make planning-parity PHASE=2` exits 0; `make planning-parity` exits non-zero
  naming `PHASE`. No default, for the same reason the script has none.
- **Prohibition:** the `gate` recipe contains no occurrence of `planning-parity`
  and no `gate:` line lists it as a prerequisite. `make gate` exits 0.
- No `jq` invocation — the only occurrence is a comment recording its absence.
- Task 2: 9 distinct IDs (0 before); parity passes after tagging, so every ID
  written exists; all six Key Decisions data rows tagged, including
  "Scope limited to the gate" tagged explicitly as corresponding to no requirement;
  six `— Pending` cells intact; the recorded tension at lines 91-93 shows no diff.
- Task 3: finding, four-instance table, Alex's framing, GOV-01's unchecked checkbox
  and the `Phase 2 (closure gate)` traceability cell all preserved; 16 entries and
  16 traceability rows, asserted equal before the pinned count.

## Deliberately not done

- **GOV-01 not marked complete.** The mechanism exists; the sweep has not run.
- **The six `— Pending` outcome cells in PROJECT.md not corrected.** Four are
  already false. Tagging is what makes the close sweep *see* them; correcting them
  here would be the sweep running before the events it exists to catch, which is
  how all four of GOV-01's instances were missed.
- **No stale artifact corrected anywhere.** Same reason.
