# Cycle 02 findings — fifteen

**This is a summary for reading, not the authoritative record.** The authoritative
finding set is `cycle-02/findings.json`, extracted from `cycle-02/codex-output-raw.md`;
state lives in `ledger.json`. Where this file and those disagree, they govern and
this is wrong.

Status as at commit `c2d5c4e`. `LOOP_STATUS: CONTINUE`, two of four cycles used.

All fifteen have been worked on since the cycle 02 capture: the ten new
findings below, and the five rejected repairs whose work is recorded in the
cycle 01 summary. None of them has changed state. §5 gives `RESOLVED` only on
demonstration in the next review target, so the ledger still reads `OPEN` for
every one. See **Repairs claimed, awaiting cycle 03** at the end of this file.

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
incomplete list. *Repair claimed 10 September, not yet demonstrated.*

**B02-F02** CONTRADICTORY IMPLEMENTATION MAPPING · `cycle-02/codex-input.md`, `findings_format.py`
The cycle 02 prompt specified a recurrence block with no `Class:` line, and the
parser requires one on every block. Following the review instructions exactly
produced a response the capture runner refused. Codex reported the
incompatibility as the finding rather than reformatting to make it pass.
*Repair claimed 10 September, not yet demonstrated:* the parser accepts the
recurrence form and resolves the class from the ledger, so the reviewer never
re-asserts a classification it is not making.

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

## Repairs claimed, awaiting cycle 03 — ten

**Read this as a claim, not a status.** Written by the implementing agent
about its own work. Cycle 02 rejected five of the thirteen repair claims it
examined; that is the rate this section should be read against. Each repair
was checked by mutation, meaning the fix was deliberately broken and the named
control confirmed to fail.

| ID | Commit | What changed | Control that fails without it |
|----|--------|--------------|-------------------------------|
| B02-F01 | `0743baa` | the strict parser sees an indented block, and the safeguard runs on every block rather than only when nothing parsed | `test_run_review.py` · "recurrence blocks, and blocks the strict parser cannot see" |
| B02-F02 | `0743baa` | the parser accepts the recurrence form with no `Class:` line and resolves the class from the ledger | `test_run_review.py` · "a recurrence takes its class from the ledger, not the review" |
| B02-F03 | `b6ea13a` | the ledger consumes the canonical Finding ID grammar instead of carrying a second copy of it | `test_ledger.py` · "one Finding ID grammar, parser and ledger (B02-F03)" |
| B02-F04 | `f6e9016`, then `a0b9893` and `f95ada5` | every refusal a supersession can trigger runs before anything is deleted; then the records are staged and swapped rather than unlinked | `test_run_review.py` · "a refused supersession leaves the authoritative capture, findings and designation intact" and "no staging files are left behind in the cycle" |
| B02-F05 | `6871d65` | amendments are constrained by role, and added pins are hash-bound and actually checked rather than iterated from what `run.json` first recorded | `test_run_review.py` · "refused: an artifact added by amendment is checked like any other governing pin" |
| B02-F06 | `6871d65` | a frozen cycle records what governed it, so a later amendment cannot retroactively change a completed cycle | `test_run_review.py` · "a frozen cycle records its governing pin set" and "refused: an amendment that would change what a completed cycle ran under" |
| B02-F07 | `604467d` | the whole implementation evidence set is snapshotted at freeze, and checks 13, 14 and 15 read the preserved copies | `test_interfaces.py` · seam 11 "implementation evidence <-> later work (B02-F07)" |
| B02-F08 | `da0f833` | the bootstrap exception expires at every operation rather than only at `init`, and `approve-runner` commits its own record | `test_bootstrap_gate.py` · "the bootstrap exception ends at the first approved runner" |
| B02-F09 | `870912a` | `authority.py` states its control at its real strength: the separate-artifact and byte-binding checks, with no claim of a forced out-of-band step | `test_bootstrap_gate.py` · "no claim stronger than CONVENTION_ONLY" |
| B02-F10 | `870912a` | the over-claim scan derives its file list from the gate's actual covered set instead of a hard-coded six, and the two uncontrolled authority refusals gained controls | `test_bootstrap_gate.py` · "no claim stronger than CONVENTION_ONLY"; `test_run_review.py` · "refused: an approval record that is not valid JSON" |

**On B02-F09 and B02-F10 sharing a commit.** F10 is the reason F09 was
invisible: the scanner that should have caught the over-claim did not read the
file containing it. Repairing the scan without repairing what it now sees
would leave a control that fires on the next commit rather than this one.

**On B02-F04's three commits.** `f6e9016` moved the refusals ahead of the
deletions. That was not enough, because a refusal between the two writes still
left one record replaced and one not, so `a0b9893` and `f95ada5` replaced
deletion with staging and an atomic swap.

---

## Raised here, not by a reviewer — one

**B02-F11** A refused capture attempt was recorded on disk but not in the
capture log, so the log and the directory disagreed about what had been
attempted. Addressed in `0629bbd`. This was found by the implementing agent
rather than by Codex, so it carries no cycle 02 identifier from the reviewer
and is not in the authoritative finding set. It is listed here so the record
is complete. **Awaiting a decision from Alex Zamurko** on whether it should be
entered into the ledger as a finding or left as a repair with no finding
attached.

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
