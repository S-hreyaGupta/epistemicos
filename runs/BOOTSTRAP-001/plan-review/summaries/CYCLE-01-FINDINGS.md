# Cycle 01 findings — eighteen, with current status

**This is a summary for reading, not the authoritative record.** The authoritative
finding set is `cycle-01/findings.json`, extracted from `cycle-01/codex-output-raw.md`;
state lives in `ledger.json`. Where this file and those disagree, they govern and
this is wrong. It is written by hand and can drift; they cannot.

Status as at commit `2c2c17c`, after cycle 02.

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
