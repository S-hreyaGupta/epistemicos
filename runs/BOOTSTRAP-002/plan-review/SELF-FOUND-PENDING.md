# Self-found, pending cycle 01

Defects found by the implementing agent on 17 September, after the cycle-01
target was frozen at `813d780c…` and before any review has run.

Under Alex Zamurko's ruling of 16 September these are admissible to the ledger
with `SOURCE = IMPLEMENTER_SELF_FOUND`, persistent identifiers and ordinary
lifecycle state. They are held here rather than raised because BOOTSTRAP-002 has
no cycle on record yet, and a `C01-Fnn` identifier raised before cycle 01's
review would put the agent's own findings and the reviewer's under one cycle
with nothing separating them.

**Nothing below has been repaired, deliberately.** Every file named is in the
frozen target. Editing one now would put an unreviewed change into a file under
review, which is the condition this run exists to prevent.

---

## 1. A refusal with no control, found by naming a different one

`scripts/test_run_review.py` had a control called *a drifted spec is not embedded
under its old hash*, which read as a control over the snapshot comparison in
`cmd_freeze`. It asserted only that freeze refused. Made to assert *why*, it
turned out the run-pin check refuses first and the snapshot comparison is never
reached.

That comparison — `run_review.py:1012` — appears unreachable by any fixture. It
hashes the copy it has just written against a hash taken from the same file a
few lines earlier in the same call, so the two differ only if the file changes
on disk between those two reads.

The control has been renamed to what it demonstrates. The branch is untouched.

## 2. Refusals no control names — five of 107

Measured by taking every `raise Refused` / `raise FormatError` in the nine
covered modules and asking whether any 14-character run of its message appears
in any of the five suites. 102 of 107 are named by a control. These five are
not:

```text
run_review.py:219       cannot resolve git HEAD; the run must pin a commit
run_review.py:903       cannot resolve the tree of <commit>
ledger.py:569           <id> is already RESOLVED
bootstrap_gate.py:718   runner not found
bootstrap_gate.py:741   this exact runner is already approved
```

Three are plainly reachable and simply untested: resolving a finding twice,
approving a runner that does not exist, approving the same runner twice.

Two are defensive branches of the same family as item 1. `cannot resolve the
tree` fires only if a commit that `rev-parse` has already resolved has no tree.

**The measurement is crude and its first version was wrong.** It initially
reported 95 of 107 unmatched, because it extracted long fragments of each
message while the controls assert short needles. The number above is from the
corrected method and has not been checked by anyone else. A reviewer should
treat 102 as an estimate.

## 3. What this says about the resolved set

Both items are the shape cycle 04 named: a control that passes for a reason
other than the one it is named for. Item 1 was green for four review cycles.
Neither was found by a control failing; both came from asking a question no
control asks.

Twenty-five findings in BOOTSTRAP-001 are marked `RESOLVED` on controls written
the same way, and six of those were never re-verified.
