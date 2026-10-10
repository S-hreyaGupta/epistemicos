# Bootstrap review prompt — BOOTSTRAP-003, cycle 04

Fourth and final cycle of the third `BOOTSTRAP_REVIEW` of the execution layer.
Hand-written, per Alex Zamurko, 8 September: a hand-written prompt is
acceptable for the bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `D04-Fnn`.** Each run has its own prefix letter:
`B` for BOOTSTRAP-001, `C` for BOOTSTRAP-002, `D` for this one. `D01-F01` and
`D02-F01` are this run's earlier findings. You may name any of them freely; the
recorder distinguishes a reference from a declaration, which is `D02-F01`'s
repair and one of the things this cycle is asked to test.

**This cycle exists by an authorised exception.** Cycle 03 ended `STALLED`: the
§6 test found `|OPEN_3| >= |OPEN_2|` with nothing newly resolved or disputed,
and the protocol says stop rather than spend the remaining budget. Alex Zamurko
cleared that exit and authorised one further review. The authorisation is
recorded at `runs/BOOTSTRAP-003/plan-review/loop-authorizations.json`, naming
the boundary and the outcome it clears. `MAX_4_REACHED` is not clearable and
this is the fourth valid cycle, so there is no fifth.

---

## What this cycle is for

Alex Zamurko, 9 October 2026, setting the question:

    "The next independent review should answer whether the system is
    sufficiently reliable to proceed to the next development stage, not whether
    every conceivable defect has been eliminated."

That is the question. The items below are the evidence for it, not a
replacement for it. If you conclude the layer is not yet reliable enough,
saying so plainly is more useful than a list of further defects.

**1. Four repairs, none of which any reviewer has seen.** Each was classified
as blocking by Alex on 9 October and each landed after cycle 03 was frozen, so
this is their first examination. They are listed with their evidence further
down.

**2. `D02-F01`, which you reported as `REPAIR NOT DEMONSTRATED`.** Your words:
"the signal net runs only when `found` is empty. The new malformed declarations
covered by this repair remain invisible when another finding parses
successfully." That is now repaired, and the repair is the reconciliation you
asked for.

**3. `SELF-F01`, and this time by running it.** Cycle 03 supported the third
repair but said: "I could not independently execute the Python controls: the
available Python commands failed to launch, and WSL access was denied." Alex
has asked specifically for the execution check. If your environment still
cannot run them, say so again rather than inferring, and say what you were able
to establish instead.

**4. The exit criteria themselves.** `specs/BOOTSTRAP-EXIT-CRITERIA.md` states
four conditions with a check behind each. Are the checks the right ones for the
claims they sit under, and does anything in them pass for a reason other than
the one it is named for? That defect class is most of what this run has found,
and it would be a poor joke to leave it in the criteria.

**5. Is anything else wrong?** The whole target is in scope.

---

## The account below is the implementing agent's own

I wrote the repairs and I wrote these notes. The record of how that has gone:
cycle 01 found two of three things I called repaired were not. Cycle 02 found
one of those still not repaired after a second attempt. Cycle 03 found a third
attempt supported, and raised a new defect in the half of it that was inside
the target. Treat what follows accordingly.

Two things from the last two days that bear on how much weight to give my
account.

On 8 October the mutation probe emptied `scripts/loop_state.py`, a covered
component, to zero bytes, and the repository stayed that way for about thirteen
hours. Nothing reached the history. It surfaced because a person read a status
line, not because any check reported it.

On 9 October a killed run left a mutation in that same file disabling the
four-cycle ceiling, and the recovery restored a different file while never
learning about this one. Again nothing reached the history, and again the thing
that caught it was a guard refusing to start rather than a check reporting a
problem.

Both are recorded as `SELF-F05` and in `SELF-F02`'s history. Both are why the
probe no longer writes to this repository at all.

---

## What you are reviewing

**Eleven files**, the same covered set as cycles 02 and 03:

```text
specs/covered-components.json     scripts/ledger.py
specs/evidence-schema-v1.0.md     scripts/loop_state.py
scripts/authority.py              scripts/run_pins.py
scripts/bootstrap_gate.py         scripts/run_review.py
scripts/cycle_projection.py       scripts/validate_cycle.py
scripts/findings_format.py
```

<!-- FREEZE: replace this block with the digest-by-digest comparison from
     `python _tmp/changed_since.py runs/BOOTSTRAP-003/plan-review/cycle-03/target.json`
     before freezing. State which files changed and why, and say explicitly
     that the rest are byte-identical to what cycle 03 saw. -->

**Files that changed and are NOT in this target.** `scripts/approval_package.py`
and `_probe/mutate_repairs.py` are not covered components and nothing covered
imports them. Parts of `SELF-F01`, `SELF-F04` and the whole of `SELF-F02`'s
third repair live in those two files. They are preserved beside the target with
the suites, as auxiliary evidence. Their state is a register assessment, not a
finding about a covered component, and saying so is not an invitation to go
easy on them.

### The control suites, preserved and run

<!-- FREEZE: `python scripts/refresh_counts.py` fills these and
     `scripts/test_prompts.py` checks them against the suites themselves. -->

---

## The four blocking repairs

### `D02-F01` — a named finding is a reference, not a declaration

**What you found.** A canonical identifier anywhere in a zero-finding reply was
read as a finding block the parser had failed to see, so a review saying "the
repair is demonstrated, nothing new" could not be captured. Cycle 03 then found
the first repair incomplete: the signal net ran only when nothing had parsed,
so a malformed declaration beside a finding that parsed stayed invisible.

**What changed.** Three rules, each with its own control and its own mutation.
Declarations are reconciled against the blocks that actually parsed, whether or
not something parsed. Fenced text is masked before scanning, because a code
fence is quoted material and your own example of a malformed declaration was
being read as a real one. And the declaration pattern requires the `Class` or
`Status` on the identifier's own line, or the line immediately below with no
other identifier on it.

**What to attack.** The masking is the riskiest part: it changes what the
parser can see at all. A finding block that happens to be indented, or inside a
fence the reviewer intended as real content, is the obvious shape of a miss.

### `SELF-F04` — the machine interface answered on a path it never computed

**What you found,** outside the finding format, which is why it has no cycle
identifier: "`loop_state.py:592` returns prose with exit 0 when every cycle is
invalid, even with `--json`."

**What changed.** The early return now emits JSON, and it omits the finding-set
keys rather than sending them empty, because an empty list reads as "nothing is
open" and that is indistinguishable from a genuine clean boundary. A
`sets_established` field says which it is, on both branches. The sole caller
refuses when it is false.

**What to attack.** The package's guard for that flag is deliberately
uncontrolled, and the test file says why: nothing today can reach it, because a
run with no valid cycle is refused earlier and a run with one always
establishes sets. Judge whether writing an unreachable guard and declaring it
unreachable is the right call or a dressed-up excuse.

### `SELF-F02`, reopened, with `SELF-F05` under it

**What happened.** The probe wrote mutations into the live controller and
restored them afterwards, so every way a run could die was a way to leave a
disabled check in the repository. Three separate gaps in that design, each
found after the previous one was called repaired.

**What changed.** The probe no longer writes to this repository. It creates a
git worktree of `HEAD` in a temporary directory, mutates that, runs the suite
there, and deletes it. A killed run costs a directory that was going to be
thrown away. Abandoned checkouts are swept by the next run and reported.

**What to attack.** Two things. First, the claim that the real tree cannot be
touched: `scripts/test_probe_recovery.py` tests it by cloning the repository,
killing a run, and checking the clone, and a test that kills a process is a
test with timing in it. Second, the trade recorded as `AR-6`: the probe now
tests committed source, so an uncommitted edit is not what gets tested, and the
refusal to run against a dirty tree is the only thing keeping that honest.

---

## What is asked of you, specifically

1. For each of the four above: is the repair demonstrated in this target, or
   not. Use `REPAIR NOT DEMONSTRATED` where it is not.
2. For `SELF-F01`: execute the controls if you can, and say plainly if you
   cannot.
3. On the exit criteria: do the four checks establish what their conditions
   claim, and is each judgement correctly left to a human rather than quietly
   decided by the script.
4. Anything else in the target.
5. The reliability question above, answered in your own words.

A reply reporting no new findings is now capturable. If that is your
conclusion, say it.

---

## Reporting

One block per finding, in the §4 format, with `Finding ID: D04-F01` and upward.

Where a repair named above is not demonstrated, report it in the recurrence
form against its existing identifier rather than as a new finding. The
implementer-disclosed entries have no cycle identifiers, by Alex Zamurko's
ruling of 5 October and his confirmation on 9 October that the rule stands;
report on them by their register names.

A repair you cannot verify should be reported as unverified rather than given
the benefit of the doubt. That distinction is load-bearing this cycle: Alex has
ruled that a behavioural claim needs independent execution, and that source
inspection alone does not establish runtime behaviour. If you can only read,
say so and say what reading established.

**This is development evidence, not a protocol outcome.** `BOOTSTRAP-003` is
marked `NOT_A_PROTOCOL_CYCLE` and the controller refuses to state an
authoritative loop result for it. `MC1_ENFORCEMENT` is `CONVENTION_ONLY`: every
check here is detection that holds while the checks run faithfully and nobody
edits the records they read.

State plainly at the end whether the layer is reliable enough to proceed, which
is the question this cycle exists to answer, and say if it makes no such claim.
