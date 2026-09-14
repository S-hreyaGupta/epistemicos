# Bootstrap review prompt — cycle 03

Third cycle of the `BOOTSTRAP_REVIEW` of the execution layer. Hand-written, per
Alex Zamurko, 8 September: a hand-written prompt is acceptable for the bootstrap.
This is not one of the five production prompts.

Twenty findings are OPEN. Ten were raised in cycle 01 and ten in cycle 02. All
twenty are claimed repaired below, and none is RESOLVED, because §5 gives
RESOLVED only "once the repair is demonstrated in the next review target". This
is that target.

Two of four cycles are used. After cycle 04 the loop reaches `MAX_4_REACHED` and
goes to human review with whatever is still open, so a finding that survives
this cycle has one more chance to be closed by a reviewer rather than by a
person.

---

## What this cycle is for

Two questions, and the first is the one §5 turns on.

**1. Are the twenty repairs demonstrated?** For each finding claimed repaired
below, does the current code fix what the finding described, and do its controls
establish that it does? A finding whose repair does not hold stays OPEN, and
saying so is the most useful thing this review can do.

Cycle 02 examined thirteen repair claims and rejected five. That is the rate
this cycle's claims should be read against, not as a prediction, but because a
reviewer who expects every claim to hold will read past the ones that do not.

**2. Is anything new wrong?** The repairs changed every file in the target. New
defects introduced by the repairs are ordinary findings.

## The account below is the implementing agent's own

Everything in the next two sections is Claude's description of Claude's work. No
one else has checked it. It is supplied so you spend the cycle on verification
rather than rediscovery, and it should be treated as a claim, not as evidence.

A finding listed as repaired that is not repaired is a finding about this prompt
as much as about the code, and it is exactly what this cycle exists to catch.
Say so plainly if you find one.

## What you are reviewing

Ten artifacts, hashed and listed in `target.json`. The same ten as cycle 02.
Four of them were new to a reviewer in cycle 02 and have now been seen once.

```text
specs/evidence-schema-v1.0.md   the frozen evidence structure
scripts/validate_cycle.py       the MC-2 conformance gate, fifteen checks
scripts/run_review.py           the review runner
scripts/ledger.py               the finding and state ledger
scripts/loop_state.py           the loop-state controller
scripts/bootstrap_gate.py       the gate enforcing this review
scripts/findings_format.py      the single parser: raw reviewer output to
                                structured findings
scripts/cycle_projection.py     what counts as a cycle, for both the ledger and
                                the controller
scripts/authority.py            approvals that must come from outside the
                                implementing agent
scripts/run_pins.py             which artifacts govern a run, and which are
                                under review
```

The covered set was read from `bootstrap_gate.covered()` rather than asserted
from memory. It is ten. An earlier draft of this prompt said eleven, from
recollection rather than from the gate, which is the same error class as the
findings below and is recorded here rather than quietly corrected.

Their negative-control suites are supplied as evidence that the checks are
falsifiable:

```text
scripts/test_validate_cycle.py   24 controls
scripts/test_run_review.py       110 controls
scripts/test_ledger.py           73 controls, covering the ledger and controller
scripts/test_bootstrap_gate.py   42 controls
scripts/test_interfaces.py       29 controls, across eleven component seams
```

Those counts total 278. They are asserted here, produced by
`scripts/refresh_counts.py`, and checked by `scripts/test_prompts.py` against
the suites themselves.

**`refresh_counts.py` is not in the covered set and not in this target.** You
are therefore being given a number by a tool you cannot inspect. This is stated
rather than left for you to discover, because on 12 September that tool's
predecessor recorded 29 controls where there were 95: `test_run_review.py` died
part-way through with a `FileNotFoundError`, emitted no FAIL line, and a grep
for failures read clean. The count refresh wrote 29 into the prompt,
`test_prompts.py` compared 29 against 29, and the commit gate passed. Three
checks agreed and all three were measuring the same crash.

The tool was rewritten to refuse a suite that does not exit 0. Whether it should
be inside the reviewed set is an open question for Alex Zamurko, not a decision
taken here. If you think a count supplied from outside the target is not
evidence you can use, say so as a finding.

Three further test suites exist and are deliberately outside that 278:
`test_prompts.py`, which consumes the number and would otherwise be agreeing
with itself; and `test_convert_protocol.py` and `test_protocol_pin.py`, which
control protocol document handling rather than the execution layer. The reason
is recorded in `refresh_counts.py`.

## What you are reviewing them against

The protocol at the commit and hash recorded in `target.json`, unchanged since
cycle 01. Where this prompt and the protocol disagree, the protocol governs and
the disagreement is itself a finding.

Alex Zamurko's section mapping, carried forward unchanged:

```text
scripts/validate_cycle.py    MC-2, and §10.2 for implementation review
scripts/run_review.py        §2.2 input composition, §10.1 target fields
scripts/ledger.py            §§5 and 12
scripts/loop_state.py        §§6 and 13
scripts/bootstrap_gate.py    no protocol section; his 8 September ruling
scripts/findings_format.py   §4 finding structure, and the schema's
                             FINDING_ID_GRAMMAR
scripts/cycle_projection.py  §§2, 3 and 6: what counts as a valid cycle
scripts/authority.py         no protocol section; his 9 September ruling 3
scripts/run_pins.py          no protocol section; his 10 September Run-Pin and
                             Review-Target Separation Specification
```

## Claimed repairs, to verify — twenty

Each line gives the finding, the commit, and the control that is claimed to fail
if the repair is removed. Every repair was checked by mutating the fixed logic
and confirming the named control went red. **That claim is not evidence.** The
suites are in the target; check whether the controls could actually fail.

### From cycle 01 — ten

Five of these were deferred by Alex Zamurko on 9 September and were never
re-reported by cycle 02 on his instruction. Five are repairs cycle 02 examined
and rejected. They keep their original identifiers.

```text
B01-F01  a9c0715  the four-cycle budget counts cycles that pass the gate, not
         directories on disk.
         control: test_run_review.py "the four-cycle budget counts valid cycles"

B01-F02  7c116cc  a cleared exit at the latest boundary is permission to
         continue, and the runner acts on it. Cycle 02 found the first half
         repaired and this half undone.
         control: test_interfaces.py seams 7 and 10

B01-F04  3c640ac  the composed review input carries the pinned spec, and for an
         implementation review the target identifiers.
         control: test_run_review.py "the review input carries the spec and the
         target identity"

B01-F05  6836060  a mutable reference such as HEAD is resolved to an immutable
         SHA at freeze, with what was supplied recorded alongside.
         control: test_run_review.py "mutable candidate references"

B01-F07  ac61b95  a cycle's recorded protocol and spec hashes derive from the
         pin set governing that cycle. Each cycle binds to the pins in force at
         that cycle, so cycle 01 is not retroactively invalidated.
         control: test_run_review.py "recorded hashes follow the cycle's own pin
         set (B01-F07)"

B01-F08  8a3971b  the controller distinguishes a development run from a protocol
         run, so exempt evidence cannot reach authoritative loop state. Cycle 02
         found the freeze-time half repaired and this half undone.
         control: test_interfaces.py seam 9; test_run_review.py
         "--bootstrap-exempt labels the run NOT_A_PROTOCOL_CYCLE"

B01-F09  abb6383  an approval is rechecked against the review evidence and the
         frozen target it was bound to. Cycle 02 found component drift detected
         and the evidence half undone.
         control: test_bootstrap_gate.py "an approval is bound to the review it
         rests on (B01-F09)"

B01-F11  77f898b  the shared projection replays transitions with their
         prerequisites rather than copying the last retained state, and refuses
         authority to cycles that do not exist. Cycle 02 found membership
         recomputed and replay absent.
         control: test_ledger.py "invalid cycles neither authorize nor block
         (B01-F11)"

B01-F12  a9c0715  no event may predate the cycle that raised the finding it acts
         on.
         control: test_ledger.py "events cannot predate the finding they act on
         (B01-F12)"

B01-F14  46f11d1  MC1_ENFORCEMENT is required and validated on every run.
         BOOTSTRAP-001 predates the requirement and its value is recorded as
         reconstructed rather than backfilled as though it had been written at
         the time. Cycle 02 found new runs recording it and nothing requiring it.
         control: test_run_review.py "a new run records its enforcement status"
```

### From cycle 02 — ten

```text
B02-F01  0743baa  the strict parser sees a block indented by one space, and the
         safeguard runs on every block rather than only when nothing parsed.
         control: test_run_review.py "recurrence blocks, and blocks the strict
         parser cannot see"

B02-F02  0743baa  the parser accepts the recurrence form with no Class line and
         resolves the class from the ledger, so the reviewer never re-asserts a
         classification it is not making.
         control: test_run_review.py "a recurrence takes its class from the
         ledger, not the review"

B02-F03  b6ea13a  the ledger consumes the canonical Finding ID grammar instead
         of carrying a second copy that disagreed with it.
         control: test_ledger.py "one Finding ID grammar, parser and ledger
         (B02-F03)"

B02-F04  f6e9016, then a0b9893 and f95ada5  every refusal a supersession can
         trigger runs before anything is deleted; then deletion was replaced by
         staging and an atomic swap, because a refusal between two writes still
         left one record replaced and one not.
         control: test_run_review.py "a refused supersession leaves the
         authoritative capture, findings and designation intact" and "no staging
         files are left behind in the cycle"

B02-F05  6871d65  amendments are constrained by role, and an added pin is
         hash-bound and actually checked rather than iterated from what run.json
         first recorded.
         control: test_run_review.py "refused: an artifact added by amendment is
         checked like any other governing pin"

B02-F06  6871d65  a frozen cycle records what governed it, so a later amendment
         cannot retroactively change a completed cycle.
         control: test_run_review.py "a frozen cycle records its governing pin
         set" and "refused: an amendment that would change what a completed
         cycle ran under"

B02-F07  604467d  the whole implementation evidence set is snapshotted at
         freeze, and checks 13, 14 and 15 read the preserved copies rather than
         the live files.
         control: test_interfaces.py seam 11

B02-F08  da0f833  the bootstrap exception expires at every operation rather than
         only at init, and approve-runner commits its own record. The deletion
         protection consults git history, which is the only place in this system
         where a tool writes to git history; assess whether that is the right
         mechanism.
         control: test_bootstrap_gate.py "the bootstrap exception ends at the
         first approved runner"

B02-F09  870912a  authority.py states its control at its real strength: the
         separate-artifact and byte-binding checks, with no claim of a forced
         out-of-band step. The claim that approval hashes are "not knowable
         until the action has been attempted and refused once" is removed,
         because they are computable in advance.
         control: test_bootstrap_gate.py "no claim stronger than
         CONVENTION_ONLY"

B02-F10  870912a  the over-claim scan derives its file list from the gate's
         actual covered set instead of a hard-coded six, and the two
         uncontrolled authority refusals gained controls.
         control: test_bootstrap_gate.py "no claim stronger than
         CONVENTION_ONLY"; test_run_review.py negative controls
```

**On B02-F09 and B02-F10 sharing a commit.** F10 is the reason F09 was
invisible: the scanner that should have caught the over-claim did not read the
file containing it. Repairing the scan without repairing what it then sees would
leave a control that fires on the next commit rather than this one. Assess
whether that reasoning holds or whether it conceals a second defect.

## Declared decisions

Decisions A to L stand and are in `bootstrap-review.md` and
`bootstrap-review-cycle-02.md`. Cycle 02's assessment of them is recorded in
`CYCLE-02-FINDINGS.md` and is reproduced here because several were qualified
rather than accepted:

```text
A, B, C, E  defensible within their stated limits.
D           holds in the ordinary path; does not cure the invalid-prerequisite
            defect.
F           materially improved.
G           filtering is observable, but the claim that filtering can only
            delay an exit is not justified when invalidation can remove
            actionable findings.
H           requires the authority/staging separation; addressed by B02-F04's
            repair.
I           retains the first exit correctly but failed authorised resumption;
            addressed by B01-F02's repair.
J           provided a conventional record, not its claimed forced external
            step; addressed by B02-F09's repair.
K           not fully enforced at its stated boundary; addressed by B02-F08's
            repair.
L           solved the specific deadlock, but its amendment mechanism was
            insufficiently constrained; addressed by B02-F05 and B02-F06.
```

Six of those qualifications were treated as the substance of a finding and
repaired. Assess whether the repair addresses the qualification or merely the
narrower finding text. G is the one with no repair attached; it is still
qualified and no work has been done on it.

## Known, and not needing a finding

**Checks 1 to 4 are one mechanism**, file existence, and only check 4 is
demonstrated. Known from cycle 01 and unchanged. Comparable cases elsewhere
still count.

## The two failure modes that matter most

**A check that cannot come back false.** For every check in `validate_cycle.py`,
every refusal in `run_review.py` and `authority.py`, and every rule in
`cycle_projection.py`, ask whether the supplied controls demonstrate it firing,
or whether the control merely exercises the same path under another name.

This cycle has a specific variant worth naming. On 12 September a suite crashed
part-way through and produced no FAIL line, so a grep for failures read clean
and the reduced control count was recorded as though it were a measurement. A
control that never runs is indistinguishable from a control that passes unless
something counts what was expected. Ask, for each suite, what would reveal a
control that silently stopped running.

**A claim stronger than its evidence.** `MC1_ENFORCEMENT` is `CONVENTION_ONLY`.
Flag any language in the schema, the scripts or their documentation implying
technical protection, immutability, prevention, or a proven binding between
reviewer input and reviewer output. `authority.py` was corrected for exactly
this in B02-F09; check whether the correction is complete or whether the
remaining language still claims more than the mechanism delivers.

## Output format

Use only this closed vocabulary:

```text
MISSING REQUIREMENT
WRONG OWNERSHIP
NONDETERMINISTIC WHERE D POSSIBLE
SEMANTIC STEP TOO BROAD
UNTESTED RULE
CONTRADICTORY IMPLEMENTATION MAPPING
```

One block per new finding, persistent identifier, cycle 03:

```text
Finding ID: B03-F01
Class:
Artifact:
Location:
Evidence:
Finding:
Required correction:
```

For an earlier finding whose repair does not hold, keep the original identifier
and say so explicitly, in this form, so the ledger records the recurrence
against the persistent identifier rather than opening a new one:

```text
Finding ID: B01-F11
Status: REPAIR NOT DEMONSTRATED
Evidence:
Finding:
Required correction:
```

The recurrence form takes no `Class:` line. The class is resolved from the
ledger, so you are not asked to re-assert a classification you are not making.

Quote the `TARGET_SHA256` from the top of this input in your first line.

State explicitly which of the twenty claimed repairs you checked and found to
hold. Silence about a repair reads as a verdict nobody gave, which is the defect
class this whole review exists to catch. If you find nothing in a category, say
so rather than omitting it.

## Scope limits

Out of scope: style, performance, and anything in `specs/gap/`. Naming is out of
scope except where decision A is wrong.

Not yet built, so their absence is not a finding: the human review package
generator (§7) and the Gold runner (§15). There is still no A1E-001 plan or
implementation; this is the tooling only.

The five production prompts `specs/prompts/01`–`05` exist and are not in this
target. Their absence is a scoping decision, not a claim that they are unwritten.
