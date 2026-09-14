# Cycle 01 findings — eighteen, with current status

**This is a summary for reading, not the authoritative record.** The authoritative
finding set is `cycle-01/findings.json`, extracted from `cycle-01/codex-output-raw.md`;
state lives in `ledger.json`. Where this file and those disagree, they govern and
this is wrong. It is written by hand and can drift; they cannot.

Status as at commit `c2d5c4e`, after cycle 02 and after the repair work of
10 to 12 September.

The ten findings below that are not closed have all been worked on since cycle
02. None of that changes their state. §5 gives a finding `RESOLVED` only once
the repair is demonstrated in the next review target, and `ledger.py` refuses
to record it any earlier, so the ledger still reads `OPEN` for all ten and is
right to. What was done to each is set out in **Repairs claimed, awaiting
cycle 03** at the end of this file. That section is the implementing agent's
own account of its own work, which is exactly the kind of claim cycle 03
exists to test.

## What cycle 01 was

The first independent review of the execution layer, frozen 9 September against
the protocol at `296594a3…`. Six artifacts: the evidence schema, the MC-2 gate,
the runner, the ledger, the loop controller and the bootstrap gate.

It exists because the orchestrator constrains the implementing agent and the
implementing agent wrote it. Nothing here could pass through the process it
enables, because the process did not exist until it did.

Codex returned eighteen findings. All eighteen were accepted.

---

## Closed — eight

Confirmed by Codex in cycle 02 as repaired, not by the implementing agent.

**B01-F03** WRONG OWNERSHIP · MC-1
The schema assigned per-cycle `findings.json` to the runner; the runner never
wrote it, and the ledger wrote a review-level file with the same name instead.
An absent ledger read as a review that found nothing.

**B01-F06** MISSING REQUIREMENT · §10.2
Check 13 compared two recorded strings and never hashed the approved plan, so
the plan could change while both records still agreed.

**B01-F10** MISSING REQUIREMENT · MC-1
The review target carried six artifacts; the gate covered five. Editing
`evidence-schema-v1.0.md` did not invalidate its own approval.

**B01-F13** CONTRADICTORY IMPLEMENTATION MAPPING · V40
The duplicate-id refusal told the operator that a re-raised issue becomes a new
finding, contradicting persistent identifiers and defeating §6's re-raise
detection. The refusal was right; its guidance was wrong.

**B01-F15** CONTRADICTORY IMPLEMENTATION MAPPING · MC-1
The schema said freezing proves an artifact did not change, and the
implementing agent had told Alex Zamurko that self-hashing closed the
replace-and-evaluate hole. Neither holds under `CONVENTION_ONLY`: the same
writable code performs the check.

**B01-F16** UNTESTED RULE · MC-1
Dependency discovery matched filename strings, so a real import was invisible to
it, and the control inserted a string rather than an import. The closure claim
was stronger than its evidence.

**B01-F17** UNTESTED RULE · §10.1
Two of five implementation refusals were exercised while the suite printed that
every refusal was reachable.

**B01-F18** UNTESTED RULE · MC-2
Seam-1 probes sat outside a cycle layout, so check 13 failed on all of them for
the wrong reason. Deleting check 12's enforcement outright still reported 7/7
enforced and exited 0.

---

## Open, deferred — five

Alex Zamurko, 9 September: "Just the critical ones, we need to start producing
working code." These were scoped out of that round. They are open by ruling, not
by oversight, and cycle 02 was told not to re-report them.

**B01-F01** CONTRADICTORY IMPLEMENTATION MAPPING · MC-2
`next_cycle` counts cycle directories rather than valid cycles, so four invalid
cycles could exhaust a budget MC-2 says they cannot consume.

**B01-F04** MISSING REQUIREMENT · §2.2
The composed review input carries the protocol but not the pinned spec, and for
an implementation review omits the target identifiers entirely.

**B01-F05** NONDETERMINISTIC WHERE D POSSIBLE · §10.1
`candidate_commit` is stored verbatim, so `HEAD` is accepted and stays mutable
while checks 11 and 12 keep passing.

**B01-F07** MISSING REQUIREMENT · MC-2
`protocol_sha256` and `spec_sha256` are checked for presence only. No check ties
them to the pinned artifacts or to `run.json`.

*Constraint added 10 September: whoever repairs this must bind each cycle to the
pins in force at that cycle. Binding every cycle to the latest pin set would
retroactively invalidate cycle 01. See `pin-amendments.json`.*

**B01-F12** MISSING REQUIREMENT · §5
No event is checked against the finding's raising cycle, so a finding can be
accepted and resolved in cycles earlier than the one that raised it.

---

## Open, repair not demonstrated — five

Repaired in part. Cycle 02 examined each and found the other half of the
original finding undone. They keep their identifiers rather than becoming new
findings, and appear again in the cycle 02 list.

**B01-F02** CONTRADICTORY IMPLEMENTATION MAPPING · §6
*Was:* the controller tested exits only at the latest boundary and the runner
checked only that the previous cycle had output, so a terminal exit in an
earlier cycle could be overridden by a later one.
*Now:* the first uncleared exit is retained correctly, but an explicitly
authorised continuation does not work at the point the runner needs it.

**B01-F08** MISSING REQUIREMENT · MC-2
*Was:* the bootstrap gate ran at init and never again, and the loop controller
never read the exempt label, so development evidence could reach authoritative
loop state.
*Now:* the freeze-time half is repaired. The controller still cannot distinguish
a development run from a protocol run.

**B01-F09** MISSING REQUIREMENT · MC-1
*Was:* recording a decision hashed whatever was on disk and never compared it to
the frozen review target.
*Now:* component drift is detected. Approval still survives deletion of the
review evidence it is said to rest on.

**B01-F11** CONTRADICTORY IMPLEMENTATION MAPPING · §6
*Was:* the ledger authorised transitions from unfiltered history while the
controller filtered by valid cycle, so an invalid event could deadlock a valid
one or authorise a closure.
*Now:* the shared projection recomputes which events are members, but copies the
last retained state rather than replaying transitions. A resolution resting on
an invalid acceptance still survives.

**B01-F14** MISSING REQUIREMENT · MC-1
*Was:* MC-1 requires each run to record `MC1_ENFORCEMENT`; `run.json` did not
carry it.
*Now:* newly created runs record it. Nothing requires it, and `BOOTSTRAP-001`
itself still lacks it and was accepted for cycle 02.

---

## Repairs claimed, awaiting cycle 03 — ten

**Read this as a claim, not a status.** Every line below was written by the
implementing agent about its own work. Cycle 02 rejected five such claims out
of the thirteen it examined, which is the base rate this section should be
read against. The ledger records none of it, correctly: a finding moves to
`RESOLVED` on a `DEMONSTRATED` event, and only cycle 03 can raise one.

Each repair was checked by mutation, meaning the fix was deliberately broken
and the named control confirmed to fail. A control that passes both with and
without the repair is the defect class cycle 01 raised six times, so passing
is not on its own evidence of anything.

| ID | Commit | What changed | Control that fails without it |
|----|--------|--------------|-------------------------------|
| B01-F01 | `a9c0715` | the budget counts cycles that pass the gate rather than directories on disk | `test_run_review.py` · "the four-cycle budget counts valid cycles" |
| B01-F02 | `7c116cc` | a cleared exit at the latest boundary is read as permission to continue, and the runner acts on it | `test_interfaces.py` · seam 7 "runner <-> loop exit" and seam 10 "authorized continuation <-> the runner" |
| B01-F04 | `3c640ac` | the composed review input carries the pinned spec, and for an implementation review the target identifiers | `test_run_review.py` · "the review input carries the spec and the target identity" |
| B01-F05 | `6836060` | a mutable reference such as `HEAD` is resolved to an immutable SHA at freeze, and what was supplied is recorded alongside | `test_run_review.py` · "mutable candidate references" |
| B01-F07 | `ac61b95` | a cycle's recorded protocol and spec hashes are derived from the pin set governing that cycle | `test_run_review.py` · "recorded hashes follow the cycle's own pin set (B01-F07)" |
| B01-F08 | `8a3971b` | the controller distinguishes a development run from a protocol run, so exempt evidence cannot reach authoritative loop state | `test_interfaces.py` · seam 9 "run classification <-> loop outcome"; `test_run_review.py` · "--bootstrap-exempt labels the run NOT_A_PROTOCOL_CYCLE" |
| B01-F09 | `abb6383` | an approval is rechecked against the review evidence and the frozen target it was bound to | `test_bootstrap_gate.py` · "an approval is bound to the review it rests on (B01-F09)" |
| B01-F11 | `77f898b` | the shared projection replays transitions with their prerequisites instead of copying the last retained state, and refuses authority to cycles that do not exist | `test_ledger.py` · "invalid cycles neither authorize nor block (B01-F11)" |
| B01-F12 | `a9c0715` | no event may predate the cycle that raised the finding it acts on | `test_ledger.py` · "events cannot predate the finding they act on (B01-F12)" |
| B01-F14 | `46f11d1` | `MC1_ENFORCEMENT` is required and validated on every run, and `BOOTSTRAP-001`'s own value is recorded as reconstructed rather than quietly backfilled | `test_run_review.py` · "a new run records its enforcement status" |

**On B01-F07.** The constraint added 10 September was honoured: each cycle
binds to the pins in force at that cycle, not to the latest pin set, so
cycle 01 is not retroactively invalidated. `pin-amendments.json` carries the
history this depends on.

**On B01-F14.** `BOOTSTRAP-001` predates the requirement. Its enforcement
value is marked as reconstructed rather than presented as though it had been
recorded at the time, because the alternative is a record that claims more
than happened, which is B01-F15.
