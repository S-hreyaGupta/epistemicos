---
phase: 02-enforcement-and-a-single-gate-definition
type: finding
id: FINDING-01
title: STATE.md has many writers and no owner, so a correction to it cannot be durable
status: open — recorded, not fixed; disposition is a human decision
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

## The second half: a normalizer that cannot parse, and keeps the old value

`status:` in the frontmatter is **derived**, not authored.
`normalizeStateStatus` (`.claude/gsd-core/bin/lib/state-document.cjs:387`) maps the
body's `Status:` line onto an enum by substring. The body read:

> `Status: 02-03 (CI collapse, SEC-01 loopback bind, …) executed and committed — ready for the remaining wave-2 plans`

That contains none of the keywords the normalizer recognises — not `executing`, not
`in progress`, not `planning`, not `verif`. It therefore fell through to `unknown`,
and `state.cjs:2359-2361` **silently preserved the previous value**:

```js
// Preserve existing frontmatter status when body-derived status is 'unknown'.
if (derivedFm['status'] === 'unknown' && existingFm['status'] && existingFm['status'] !== 'unknown') {
    derivedFm['status'] = existingFm['status'];
}
```

So a `Status:` line the parser could not read produced no error, no warning, and a
frontmatter value that confidently asserted `planning` while three plans had run.

**This is the same shape as every other defect found this week**: a check that
cannot come back false. The vacuous negative control in 02-03, the `-eq 12` count
that could not hold on a correct tree, the `SHA-256` false positive, the guard
proven by placement rather than execution — and now a normalizer that answers
"unchanged" when it means "I could not tell". Preserving the old value is a
reasonable-looking fallback that makes an unparseable input indistinguishable from
a stable one.

## Disposition — a human decision, not taken here

Recorded, not fixed. GOV-01's own rule is that **a pass which would add a
requirement HALTS for a human**: correcting what a document says about the
requirement set is a sweep, changing the set is a decision. This finding would be a
new requirement, so it halts here.

Options, for whoever dispositions it:

1. **Give `STATE.md` a single writer.** Executors stop writing it; the orchestrator
   writes it once per wave from measured facts. Makes corrections durable by
   removing the overwrite path. Largest change.
2. **Make it derived rather than authored.** Anything reconstructible from disk and
   git — plan/summary pairs, HEAD, counts — is generated, not typed, so a partial
   writer cannot leave a stale field. Narrows what can drift to genuinely
   free-text fields.
3. **Make the normalizer loud.** An unparseable `Status:` line reports rather than
   silently inheriting. Cheapest, and closes only the second half — but the second
   half is the part that made the first half invisible.
4. **Accept it and re-check at close**, with the expiry stated plainly, so the next
   reader knows a hand-correction is good until the next executor runs.

These are not mutually exclusive: 3 is cheap and independent of the rest.

## What was done here

`STATE.md` was corrected again, to match the tree measured at 02-04's completion.
That correction carries the same expiry as the last one, which is the point of
recording this separately rather than fixing it a third time in silence.
