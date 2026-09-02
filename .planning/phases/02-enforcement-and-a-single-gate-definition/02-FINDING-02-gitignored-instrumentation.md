---
phase: 02-enforcement-and-a-single-gate-definition
type: finding
id: FINDING-02
title: Instrumentation that lives in gitignored .claude/ is unversioned and reverts silently
status: open — registered as a class; constrains every fix that touches .claude/
found: 2026-09-02
found_by: operator, while choosing a fix for FINDING-01
relates_to: [FINDING-01, GOV-01]
---

# FINDING-02 — Fragile gitignored instrumentation

## The finding

**`.gitignore:29` ignores `.claude/`.** Every behavioural modification we make to the
agent tooling therefore lives only on disk in one worktree. It is not in version
control, it is not reviewable, it does not survive recreating the worktree, and
**`/gsd-update` reverts it silently** — leaving no trace that it ever existed.

This is a **class, not three coincidences**. Three instances are known, all found by
walking into them rather than by any step that looks for them:

| # | Instrumentation | Where | How it is lost |
|---|---|---|---|
| 1 | The review-run archive block, hand-added before the `rm -rf` | `.claude/gsd-core/workflows/review.md` | `/gsd-update` restores the stock file; captures stop happening and say nothing |
| 2 | Any `state.cjs` guard (e.g. FINDING-01's withdrawn option 3) | `.claude/gsd-core/bin/lib/state.cjs` | Same — the guard disappears, the bug returns unannounced |
| 3 | The executor contract, incl. FINDING-01's landed `state.sync` call | `.claude/agents/gsd-executor.md` | Same — executors silently stop re-deriving frontmatter |

Instance 1 was already recorded in `STATE.md`'s Blockers/Concerns. Instances 2 and 3
were found on 2026-09-02 while choosing a fix for FINDING-01. Registering them as one
class is what makes the constraint visible **before** the next fix is designed rather
than after it vanishes.

## Why this belongs before a fix, not after

It **decides the shape of the fix**, not merely its durability. FINDING-01's
disposition turned on it twice:

- Option 3 (`state.cjs` guard) was already weak on the merits — it guarded a branch
  the trace showed is never taken. But even had it been correct, it would have been a
  fix for *"a mechanism that fails silently"* that **itself vanishes silently**. That
  is not a fix; it is a fix-shaped object with an undisclosed expiry.
- The cheap alternative — have the executor call `state.sync` — sidesteps `state.cjs`
  entirely. But the executor contract is **also** in `.claude/`, so it inherits the
  same fragility. **There is no fix for FINDING-01 that does not need a tracked
  counterpart.** That is a property of the constraint, discovered only because the
  constraint was named first.

A reader who meets this class only after choosing a fix has already chosen wrongly.

## The rule this imposes

**Any change to `.claude/` MUST ship with a durable instruction in the TRACKED
planning docs, in the same commit.** The tracked instruction is the artifact of
record; the `.claude/` edit is a convenience that may be reverted at any time by an
update nobody announces.

A conforming change therefore has two parts:

1. The edit itself, under `.claude/` — effective now, expendable.
2. A tracked counterpart stating **what** was changed, **where**, **why**, and
   **how to detect that it is gone** — so re-applying it is a step someone can take
   rather than a thing someone must remember.

Detection matters more than the instruction. An instruction with no detection is a
promise that the next reader will notice something invisible.

## Relationship to GOV-01

Adjacent, and instructive about GOV-01's bound.

GOV-01 covers artifacts that go stale **without being edited**. This class is the
mirror: instrumentation that is **removed** without anyone editing it, by a tool doing
its normal job. Both are "the file changed meaning while nobody touched it", and
neither is visible to a diff of the file.

But GOV-01's sweep cannot cover this one, for the same structural reason recorded in
its coverage bound: the derivation walks tracked files under `.planning/`, and by
construction **the instrumentation is neither tracked nor under `.planning/`.** It is
outside the sweep set permanently, not incidentally.

That is precisely why the rule above puts the record inside `.planning/`: the tracked
counterpart *is* in the sweep set even though the thing it describes never can be.

## Tracked counterparts register

The artifact of record for every live `.claude/` modification. Each row carries a
detection command that returns **0 when the modification is GONE**, so absence is
checkable rather than remembered. Run them after any `/gsd-update` or worktree
recreation.

### 1. Review-run archive block

- **File:** `.claude/gsd-core/workflows/review.md`
- **What:** a block archiving the review run directory before the `rm -rf`.
- **Why:** a capture that stops happening without saying so is the failure class the
  archive exists to catch.
- **Detect (0 = gone):**
  `grep -c 'review-runs' .claude/gsd-core/workflows/review.md`
- **Evidence it was working:** tracked output under
  `.planning/phases/*/review-runs/`, each with `_INSTRUMENTATION.txt` naming the GSD
  version that produced it. The output survives; the mechanism does not.

### 2. `state.sync` call in the executor contract  (FINDING-01's instance fix)

- **File:** `.claude/agents/gsd-executor.md`, in the post-SUMMARY STATE.md block,
  after `state.update-progress`.
- **What:** `gsd_run query state.sync`, with a comment explaining why.
- **Why:** STATE.md has two surfaces. Executors edit the body; without this call the
  machine-read frontmatter keeps whatever the previous writer left. Measured: `status:
  planning` survived three executed plans (`8a23cb6`, `9917290`, `2d52a1e`), none of
  which touched the frontmatter.
- **Detect (0 = gone):**
  `grep -c 'state.sync' .claude/agents/gsd-executor.md`
- **Re-apply:** add `gsd_run query state.sync` immediately after
  `gsd_run query state.update-progress` in that block.
- **Symptom if silently lost:** STATE.md frontmatter drifts from its body again —
  `status:` disagreeing with the body `Status:` line, `state_head` behind HEAD,
  `last_activity_desc` describing an earlier phase.

### 3. `state.cjs` guard — NOT PRESENT, deliberately

- **File:** `.claude/gsd-core/bin/lib/state.cjs`
- **Status:** FINDING-01's option 3 was implemented and then **reverted unapplied**.
  Recorded here so a later reader does not re-add it believing it was lost to an
  update. It was withdrawn on the merits: the branch it guarded is never taken.
- **Detect (1 = something re-added it):**
  `grep -c 'FINDING-01' .claude/gsd-core/bin/lib/state.cjs`

## Disposition

Registered as a class. Two things follow immediately, both landed with this finding:

- FINDING-01's `state.sync` executor fix ships with its tracked counterpart.
- A pointer to this finding is added to `.planning/codebase/CONCERNS.md` under
  Fragile Areas, which is where codebase orientation happens — so the next person
  meets the constraint before choosing, not after.

**Not decided here:** whether `.claude/` should be tracked at all, or whether these
modifications belong upstream in GSD rather than as local edits. Both are design
decisions for Alex, and either would dissolve the class rather than manage it.
