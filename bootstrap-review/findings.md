# BOOTSTRAP-002 — findings and their final states

Run `BOOTSTRAP-002`, plan review, four valid cycles. `LOOP_STATUS: MAX_4_REACHED`.
Twenty one findings raised, nineteen resolved, two open, none disputed.

This file is a reading of `runs/BOOTSTRAP-002/plan-review/ledger.json`. The
ledger is authoritative; where this disagrees with it, it is wrong.

---

## The two that are still open

Both were reported by cycle 04 as recurrences, meaning the reviewer examined the
repair and did not find it demonstrated. Both are defects in code the bootstrap
decision would be approving. Neither is disputed: I accept both.

### C02-F08 — the preserved patch need not match its own headers

The reviewed diff is derived from the base and candidate commits, and check 14
compares the blob identities named in the patch's `index` lines with the ones in
the change set. That establishes the headers name the right objects. It does not
establish that the rest of the patch describes what those headers point at.

Cycle 04: "Retain its original `index <old>..<new>` lines, alter the displayed
paths or added/removed lines, and update the patch hash and target binding...
The derived raw digest remains correct and both blob-pair sets remain equal. No
check connects the altered text to the objects those headers name."

Two further holes it names, both mine and both plain. Comparing sets loses
repeated changes that share a blob pair. And an empty change set skips the
comparison entirely, because the guard reads `if _want and _got != _want`, so a
cycle whose change set is empty accepts any patch at all.

**What it would take.** Validate the patch's actual transformation against the
base and candidate objects, including paths, modes and repeated entries. Compare
empty change sets explicitly rather than skipping them. Controls for: correct
headers with altered hunks or paths, an omitted entry among several sharing a
blob pair, and a nonempty patch against an empty change set.

### C03-F02 — the scope approval need not be committed

The ruling of 2 October requires a scope change to be both committed and
separately authorised. The manifest's committed state is checked properly. The
approval record's is not.

Cycle 04: "lines 483–485 only run `git status --porcelain -- <approval-path>`
and refuse when the command succeeds with nonempty output. No committed approval
blob is resolved or compared with the approval bytes."

So an approval file that is untracked and ignored produces empty status output
and passes. And if the git call fails, the condition `rc == 0 and
appr_dirty.strip()` is false and execution continues, which treats a failure to
establish provenance as permission. That is the same defect class this run has
been repairing throughout, in code I wrote three days ago to close it.

**What it would take.** Resolve the committed approval blob and compare its bytes
with the approval being consumed. Refuse a failed repository query rather than
proceeding. Controls for: an ignored untracked approval, an approval present only
in the index, a failed provenance query, and a committed matching approval.

---

## The nineteen resolved

Each closed because a later cycle's reviewer examined the repair and said so.
None closed on my assertion.

| ID | closed in | what it was |
|---|---|---|
| C01-F01 | cycle 02 | three copies of the transition rules, which disagreed |
| C01-F02 | cycle 02 | the four-cycle ceiling bound only at the last boundary |
| C01-F03 | cycle 02 | check 9 compared records with records, never artifacts |
| C01-F04 | cycle 02 | the gate replayed a pin history it never validated |
| C01-F05 | cycle 02 | a run with no classification got the stronger one |
| C01-F06 | cycle 02 | a reported finding could exist without a state |
| C01-F07 | cycle 02 | cycle uniqueness was checked, cycle identity was not |
| C01-F08 | cycle 02 | the commit and the hash described different bytes |
| C02-F01 | cycle 03 | a prompt numbered its findings from the wrong cycle |
| C02-F05 | cycle 03 | two cycle-directory grammars that disagreed |
| C02-F06 | cycle 03 | an interrupted capture designation could be taken |
| C02-F07 | cycle 03 | the gate's evidence need not name its target |
| C02-F09 | cycle 03 | a missing snapshot was filled from a live file |
| C02-F10 | cycle 03 | the controls were asserted rather than supplied |
| C02-F11 | cycle 03 | a bare status escaped through an early return |
| C02-F02 | cycle 04 | a chronological guard that lived only in the commands |
| C02-F03 | cycle 04 | the age exemption claimed by evidence that is not old |
| C02-F04 | cycle 04 | the classification taken from the transcription |
| C03-F01 | cycle 04 | a finished review read with today's schema |

---

## How the run moved

```text
boundary        open   resolved   exit
n=1 cycle 01       8          0   CONTINUE
n=2 cycle 02      11          8   CONTINUE
n=3 cycle 03       6         15   CONTINUE
n=4 cycle 04       2         19   MAX_4_REACHED
```

The open count rose once, when cycle 02 raised eleven against eight repairs, and
fell at every boundary after. The run ends on the budget rather than on a stall:
four findings closed in the final cycle, so the loop was still converging when it
ran out of cycles.

---

## What is not established

**The mutation probe's results are my assertion.** `_probe/mutate_repairs.py`
removes each repair and requires its control to fail; thirty nine mutations hold.
Its source is preserved in each cycle's `auxiliary/`, but it is not run at freeze
and no cycle carries its output. Cycle 04 said so: "the mutation probe's results
remain unverified implementer assertions."

**`test_approval_package.py` does not pass.** An approval package for a run with
frozen cycles and no ledger stays silent, and silence reads as no findings rather
than as nobody having looked. It is named in every freeze record with that
reason. It is a real defect and it is still there.

**No cycle certified every earlier repair.** Each reviewed what its prompt put in
front of it. Cycle 04 was explicit: its support for four repairs "does not
establish probe execution or certify every earlier repair."
