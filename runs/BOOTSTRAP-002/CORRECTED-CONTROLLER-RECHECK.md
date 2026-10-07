# BOOTSTRAP-002 under the corrected controller

Alex Zamurko, 7 October 2026, as the third of four next steps:

    Re-check BOOTSTRAP-002 with the corrected controller. The question is
    simply: does the corrected logic still produce the same final result?
    Why: BOOTSTRAP-002 does not automatically need reopening, but its previous
    closure should be shown not to depend on the defective logic.

## Why it could have changed

D01-F01, raised by BOOTSTRAP-003's first cycle, was that the stateless-finding
check replayed each finding's history over every valid cycle in the run, while
each boundary is computed over the cycles up to it. The repair narrows the
replay to the cycles that had reported the finding, and adds a refusal when an
entry's `cycle_raised` disagrees with its own RAISED event.

Both changes make the controller **stricter**. A ledger it previously accepted
can now be refused, so a run closed under the old logic is not automatically
still closed under the new. BOOTSTRAP-002 ended at `MAX_4_REACHED` with two
findings open, and that result is quoted in the evidence package Alex Zamurko
has, so whether it survives the repair is not a detail.

## The command

    python scripts/loop_state.py --review runs/BOOTSTRAP-002/plan-review --development

Run on 7 October 2026 against the repaired controller, after the three
D01-F01 controls were passing.

## The result

    LOOP_STATUS: MAX_4_REACHED  [DEVELOPMENT EVIDENCE — NOT A PROTOCOL OUTCOME]
    Budget exhausted with findings still open. Proceed to human plan review
    with the unresolved matters exposed.

    ledger at the stop boundary, n=4
      OPEN       2  C02-F08, C03-F02
      DISPUTED   0  -
      RESOLVED  19  C01-F01, C01-F02, C01-F03, C01-F04, C01-F05, C01-F06,
                    C01-F07, C01-F08, C02-F01, C02-F02, C02-F03, C02-F04,
                    C02-F05, C02-F06, C02-F07, C02-F09, C02-F10, C02-F11,
                    C03-F01

    exit code 0

Identical to the result recorded when the run closed: the same status, the same
two open findings, the same nineteen resolved, the same governing boundary at
n=4, and no refusal from either new rule.

## What this establishes, and what it does not

**Establishes:** BOOTSTRAP-002's closure does not depend on the defective
replay. Neither of the two new refusals fires anywhere in its ledger, so no
finding in it was relying on an event dated to a later cycle, and no entry
carries an origin that disagrees with its own history.

**Does not establish:** that BOOTSTRAP-002 was correct in any wider sense. It
ended with two findings open and a human decision outstanding, and this changes
none of that. It also does not re-examine the nineteen resolutions; it says
only that the arithmetic over them is unchanged.

The run stays closed as it ended rather than being reopened, which is the
outcome Alex Zamurko's instruction anticipated but did not assume.
