# Cycle 02 findings — fifteen

**This is a summary for reading, not the authoritative record.** The authoritative
finding set is `cycle-02/findings.json`, extracted from `cycle-02/codex-output-raw.md`;
state lives in `ledger.json`. Where this file and those disagree, they govern and
this is wrong.

Status as at commit `2c2c17c`. `LOOP_STATUS: CONTINUE`, two of four cycles used.

## What cycle 02 was, and how it differs from cycle 01

Cycle 01 asked one question: is this code correct against the protocol. Cycle 02
asks two.

1. **Do the claimed repairs hold?** §5 gives a finding `RESOLVED` only "once the
   repair is demonstrated in the next review target". Cycle 02 is that target,
   so it is the cycle that closes cycle 01's findings, or declines to.
2. **Is anything new wrong?** The repairs added three files and changed five,
   and a fourth file had been load-bearing since before cycle 01 without ever
   appearing in a reviewer's list.

The target grew from six artifacts to ten: `findings_format.py`,
`cycle_projection.py`, `authority.py` and `run_pins.py` had never been reviewed
by anyone. They entered the reviewed set through the gate's own import
discovery rather than by being declared.

The prompt was written by the implementing agent describing its own repairs, and
says so. It names the commits as the evidence and tells the reviewer that a
repair listed as done but not done is exactly what the cycle exists to catch.
Five such listings were found.

**Where the two lists apply.** Cycle 01's list is the historical record of what
was wrong on 9 September, and eight of its eighteen entries are now closed.
Cycle 02's list is the live work queue. The five entries that appear in both are
not duplicates: they are cycle 01 findings whose repair cycle 02 rejected, and
they keep their original identifiers because §6's re-raise detection needs the
identity to persist.

---

## Repairs rejected — five

Full text in the cycle 01 summary. Listed here because they are part of cycle
02's authoritative finding set.

| ID | What remains undone |
|----|---------------------|
| B01-F02 | authorised continuation fails at the point the runner needs it |
| B01-F08 | the controller cannot tell development evidence from protocol evidence |
| B01-F09 | approval survives deletion of the review evidence it rests on |
| B01-F11 | a resolution resting on an invalid acceptance still survives |
| B01-F14 | enforcement status is written but never required, and this run lacks it |

---

## New — ten

**B02-F01** MISSING REQUIREMENT · `findings_format.py`, `run_review.py`, `loop_state.py`
A finding block indented by one space is invisible to the strict parser, and the
safeguard that would have caught it only ran when nothing parsed at all. One
successful block switched off the protection for the rest. Both extraction and
the controller's reconciliation use the same parser, so both agree on the same
incomplete list. **Fixed 10 September.**

**B02-F02** CONTRADICTORY IMPLEMENTATION MAPPING · `cycle-02/codex-input.md`, `findings_format.py`
The cycle 02 prompt specified a recurrence block with no `Class:` line, and the
parser requires one on every block. Following the review instructions exactly
produced a response the capture runner refused. Codex reported the
incompatibility as the finding rather than reformatting to make it pass.
**Fixed 10 September:** the parser accepts the recurrence form and resolves the
class from the ledger, so the reviewer never re-asserts a classification it is
not making.

**B02-F03** CONTRADICTORY IMPLEMENTATION MAPPING · schema, `findings_format.py`, `ledger.py`
The schema permits zero to two capital letters at the start of a finding
identifier; the ledger's independently written expression permits at most one.
`AB02-F01` parses cleanly and the ledger then refuses it. A valid captured
finding cannot be entered unchanged, which is the divergence the single-grammar
ruling was meant to end.

**B02-F04** CONTRADICTORY IMPLEMENTATION MAPPING · `run_review.py`
Superseding a capture deletes `codex-output-raw.md` and `findings.json` before
the zero-findings consistency check runs. With a conflicting flag combination
the command deletes the working authoritative evidence, then refuses and reports
"Nothing written." The preserved attempt bytes survive, but the authoritative
cycle is broken.

**B02-F05** MISSING REQUIREMENT · `run_pins.py`, `run_review.py`
A structurally valid amendment can remove the governing protocol from the pin
set entirely, or add a path that is never checked because the pin check iterates
only what `run.json` originally recorded. Role separation is implemented as
unrestricted set editing.

**B02-F06** MISSING REQUIREMENT · `run_pins.py`
Amendments are compared only against the preceding amendment, not against cycles
that already exist. An amendment appended after a review can retroactively change
what governed a completed cycle, which defeats the historical reconstruction the
mechanism was built for.

**B02-F07** CONTRADICTORY IMPLEMENTATION MAPPING · `run_review.py`, `validate_cycle.py`
For implementation review, checks 14 and 15 still hash the live diff and test
results rather than the preserved copies, and the approved plan is not
snapshotted at all. Ordinary later repairs invalidate earlier evidence and
remove its events from the loop calculation.

**B02-F08** CONTRADICTORY IMPLEMENTATION MAPPING · `run_review.py`, `bootstrap_gate.py`
The expiry check runs only when `init` receives `--bootstrap-exempt`, so a run
that is already exempt keeps working after a runner has been approved. Separately,
the deletion protection depends on the approval being committed, and the control
suite demonstrates that an uncommitted approval can be deleted — a bypass the
prompt presented as enforcement.

**B02-F09** CONTRADICTORY IMPLEMENTATION MAPPING · `authority.py`
The module states that the approval hashes are "not knowable until the action
has been attempted and refused once". They are computable in advance from the
capture log and the replacement file, and no prior-refusal state is checked. The
separate-artifact and byte-binding checks work; the claimed forced out-of-band
step does not exist. This is an over-claim inside the module written to avoid
over-claims.

**B02-F10** UNTESTED RULE · `test_bootstrap_gate.py`, `test_run_review.py`
The no-over-claim scanner reads a hard-coded list of six files and omits all four
newly reviewed modules, including the one containing B02-F09. Two of the
authority refusals, malformed JSON and absent timestamp, have no control at all.
The review scope was broadened; its prose control was not.

---

## Codex on the declared decisions

A, B, C and E remain defensible within their stated limits. D holds in the
ordinary path but does not cure the invalid-prerequisite defect. F is materially
improved. G's filtering is observable, but the claim that filtering can only
delay an exit is not justified when invalidation can remove actionable findings.
H requires the authority/staging separation above. I retains the first exit
correctly but fails authorised resumption. J provides a useful conventional
record, not its claimed forced external step. K is not fully enforced at its
stated boundary. L solves the specific deadlock but its amendment mechanism is
insufficiently constrained.
