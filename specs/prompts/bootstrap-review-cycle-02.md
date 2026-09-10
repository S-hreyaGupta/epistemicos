# Bootstrap review prompt — cycle 02

Second cycle of the `BOOTSTRAP_REVIEW` of the execution layer. Hand-written, per
Alex Zamurko, 8 September: a hand-written prompt is acceptable for the bootstrap.
This is not one of the five production prompts.

Cycle 01 produced eighteen findings. All eighteen were accepted and none is
RESOLVED, because §5 gives RESOLVED only "once the repair is demonstrated in the
next review target". This is that target.

---

## What this cycle is for

Two questions, and the first is the one §5 turns on.

**1. Are the repairs demonstrated?** For each cycle-01 finding claimed repaired
below, does the current code actually fix what the finding described, and do its
controls establish that it does? A finding whose repair does not hold stays OPEN,
and saying so is the most useful thing this review can do.

**2. Is anything new wrong?** The repairs added three files and changed five,
and a fourth file has been in the covered set since before cycle 01 without ever
appearing in a reviewer's list. New defects introduced by the repairs are
ordinary findings.

## The account below is the implementing agent's own

Everything in the next two sections is Claude's description of Claude's work. No
one else has checked it. It is supplied so you spend the cycle on verification
rather than rediscovery, and it should be treated as a claim, not as evidence.

The evidence is the code and these commits:

```text
1ce74b7  F02 and F11
ecdcf1c  ruling 3, capture supersession authority
e704aac  rulings 1 and 2, the bounded bootstrap exception
b43fc46  issue 7 recurrence, and F06
```

A finding listed as repaired that is not repaired is a finding about this
prompt as much as about the code, and it is exactly what cycle 02 exists to
catch. Say so plainly if you find one.

## What you are reviewing

Ten artifacts, hashed and listed in `target.json`. Six were reviewed in cycle
01. Four have **never been seen by any reviewer**:

```text
specs/evidence-schema-v1.0.md   the frozen evidence structure
scripts/validate_cycle.py       the MC-2 conformance gate, fifteen checks
scripts/run_review.py           the review runner
scripts/ledger.py               the finding and state ledger
scripts/loop_state.py           the loop-state controller
scripts/bootstrap_gate.py       the gate enforcing this review

scripts/findings_format.py      UNREVIEWED. the single parser: raw reviewer
                                output to structured findings
scripts/cycle_projection.py     UNREVIEWED. what counts as a cycle, for both
                                the ledger and the controller
scripts/authority.py            UNREVIEWED. approvals that must come from
                                outside the implementing agent
scripts/run_pins.py             UNREVIEWED. which artifacts govern a run, and
                                which are under review
```

All four are load-bearing. `findings_format.py` decides what the reviewer said;
`cycle_projection.py` decides whether a recorded event may authorise a state
transition; `authority.py` decides whether a supersession may proceed;
`run_pins.py` decides what a cycle is measured against. An error in any of them
produces a false process outcome from evidence that passes MC-2 cleanly, which
is the reason Alex Zamurko gave for widening the review scope on 9 September.

None of them was declared as a component. All four entered the gate's covered
set through its import discovery, which is the B01-F16 repair behaving as
intended. Worth checking that it did so correctly rather than by luck, and worth
noting that until 10 September nothing checked that a covered file was named in
the prompt at all: three of these were covered, treated as reviewed, and absent
from the reviewer's list at the same time.

Their negative-control suites are supplied as evidence that the checks are
falsifiable:

```text
scripts/test_validate_cycle.py   24 controls
scripts/test_run_review.py       62 controls
scripts/test_ledger.py           56 controls, covering the ledger and controller
scripts/test_bootstrap_gate.py   36 controls
scripts/test_interfaces.py       19 controls, across seven component seams
```

Those counts are asserted here and checked by `scripts/test_prompts.py` against
the suites themselves.

## What you are reviewing them against

The protocol at the commit and hash recorded in `target.json`, unchanged since
cycle 01. Where this prompt and the protocol disagree, the protocol governs and
the disagreement is itself a finding.

Alex Zamurko's section mapping, carried forward, with the four unreviewed files
added:

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

## Claimed repairs, to verify

```text
B01-F02  loop_state.py evaluates every valid boundary in order and retains the
         first terminal outcome; run_review refuses to open a cycle after one.
         Continuing past an exit needs a record in loop-authorizations.json
         naming the boundary and the exit it clears.
B01-F03  cmd_record writes per-cycle findings.json; absence never means zero.
B01-F06  check 13 hashes the approved plan itself and requires the approval to
         name the artifact and to be an APPROVE.
B01-F08  the bootstrap gate is checked at freeze as well as init.
B01-F09  recording a decision refuses if the components drifted from the frozen
         review target.
B01-F10  evidence-schema-v1.0.md is in the gate's covered set.
B01-F11  ledger and controller share cycle_projection.py. An event in a cycle
         that fails MC-2 neither authorises a transition nor blocks one.
B01-F13  recurrence has its own transition, RESOLVED -> OPEN, keeping the
         identifier. The duplicate-id refusal no longer tells the operator to
         rename.
B01-F14  run.json records MC1_ENFORCEMENT.
B01-F15  the immutability and proof language is gone from the covered files, and
         a control scans for its return.
B01-F16  the closure discovers real imports by parsing, not only filename
         strings.
B01-F17  all five implementation refusals are exercised.
B01-F18  the seam-1 probes sit inside a cycle layout, so check 13 no longer
         fails on all of them for the wrong reason.
```

**Deferred by Alex Zamurko, 9 September, and still OPEN by his ruling, not by
oversight**: B01-F01, B01-F04, B01-F05, B01-F07, B01-F12. He scoped this round
to the critical set. They do not need re-reporting as new findings. If a repair
above interacts badly with one of them, that interaction is a finding.

## Declared decisions

Cycle 01's decisions A to G stand and are in `bootstrap-review.md`. Assess them
again if the repairs changed what they mean. Five are new.

```text
H  cycle_projection distinguishes three states, not two: VALID, INVALID and
   UNJUDGED. Only INVALID strips authority. A cycle with no directory yet is
   the one being assembled, and a ledger that refused to record into it would
   be unusable. Authority is recomputed on every read rather than frozen at
   write time, so an event loses authority the moment its cycle is judged and
   fails. The ledger's stored `state` field is a cache of that projection and
   nothing reads it to decide anything.

I  The first terminal loop outcome governs, and later cycles do not override
   it. An authorisation to continue must name both the boundary and the exit
   it clears; a blanket authorisation would restore B01-F02 under a different
   spelling. Cycles run after an unauthorised exit are reported, not absorbed.

J  authority.py claims only what CONVENTION_ONLY supports. It does not prove
   who wrote an approval. What it enforces is that the approval exists as a
   separate artifact, names a person and a reason, and binds by hash to the
   exact bytes it approves, so it cannot be recycled. The hashes are printed
   only by the refusal, so obtaining an approval is a step outside the command.
   The intended change is that unilateral supersession becomes a deliberate
   forgery naming a person rather than a flag. Argue with this if the claim is
   still stronger than the mechanism.

K  The bootstrap exception ends at the first runner approval, and the check
   consults git history as well as the working tree so that deleting the
   approval does not reopen it. This rests on an asymmetry: writing an approval
   only makes the rules stricter, so the direction worth closing is removal. A
   history rewrite still defeats it.
```

L  A run-level pin and a review target are disjoint roles, per Alex Zamurko's
   Run-Pin and Review-Target Separation Specification of 10 September. run.json
   is not edited when the pin set changes; it stays the record of what was
   pinned at init, and amendments are appended to pin-amendments.json with
   reason, affected artifacts, prior set, new set and effective cycle. The set
   governing a cycle is replayed from that history, so cycle 01 keeps the pins
   it was conducted under and cycle 02 gets the amended set.

   This was found by the loop deadlocking on it: evidence-schema-v1.0.md was
   both BOOTSTRAP-001's only run-level pin and cycle 01's first review target,
   so repairing findings about it broke the run's own pin and blocked the cycle
   meant to demonstrate the repairs. Assess whether the amendment mechanism can
   itself be used to make an inconvenient pin disappear.

H and J are the two most worth arguing with. H decides which recorded events
carry authority, and J decides whether a control the implementing agent cannot
operate has actually been built or merely described.

## Known, and not needing a finding

**Checks 1 to 4 are one mechanism**, file existence, and only check 4 is
demonstrated. Known from cycle 01. Comparable cases elsewhere still count.

## The two failure modes that matter most

**A check that cannot come back false.** For every check in `validate_cycle.py`,
every refusal in `run_review.py` and `authority.py`, and every rule in
`cycle_projection.py`, ask whether the supplied controls demonstrate it firing,
or whether the control merely exercises the same path under another name.

The implementing agent claims every control added in this round was verified by
mutating the repaired logic and confirming the control went red, and that three
controls came back alive on the first attempt and were rewritten. That claim is
not evidence. The suites are in the target; check whether the controls could
actually fail.

**A claim stronger than its evidence.** `MC1_ENFORCEMENT` is `CONVENTION_ONLY`.
Flag any language in the schema, the scripts or their documentation implying
technical protection, immutability, prevention, or a proven binding between
reviewer input and reviewer output. `authority.py` and `cycle_projection.py` are
new prose and have never been read by a reviewer.

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

One block per finding, persistent identifier, cycle 02:

```text
Finding ID: B02-F01
Class:
Artifact:
Location:
Evidence:
Finding:
Required correction:
```

For a cycle-01 finding whose repair does not hold, keep the original identifier
and say so explicitly, in this form, so the ledger can record the recurrence
against the persistent identifier rather than opening a new one:

```text
Finding ID: B01-F11
Status: REPAIR NOT DEMONSTRATED
Evidence:
Finding:
Required correction:
```

Quote the `TARGET_SHA256` from the top of this input in your first line.

State explicitly which claimed repairs you checked and found to hold. Silence
about a repair reads as a verdict nobody gave, which is the defect class this
whole review exists to catch. If you find nothing in a category, say so rather
than omitting it.

## Scope limits

Out of scope: style, performance, and anything in `specs/gap/`. Naming is out of
scope except where decision A is wrong.

Not yet built, so their absence is not a finding: the human review package
generator (§7) and the Gold runner (§15). There is still no A1E-001 plan or
implementation; this is the tooling only.

The five production prompts `specs/prompts/01`–`05` exist and are not in this
target. Their absence is a scoping decision, not a claim that they are unwritten.
