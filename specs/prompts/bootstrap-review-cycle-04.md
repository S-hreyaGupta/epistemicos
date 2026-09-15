# Bootstrap review prompt — cycle 04

Fourth cycle of the `BOOTSTRAP_REVIEW` of the execution layer. Hand-written, per
Alex Zamurko, 8 September: a hand-written prompt is acceptable for the bootstrap.
This is not one of the five production prompts.

**This is the last cycle.** Three of four are used. When this one closes the loop
reaches `MAX_4_REACHED`, and since Alex Zamurko's ruling of 15 September that
outcome is terminal: no recorded authorisation clears it, and there is no fifth
cycle to appeal to. Whatever is still open afterwards goes to a human reviewer.

That changes what is useful from you. In earlier cycles a finding you were unsure
about could be raised and settled next time. There is no next time. A defect you
suspect but cannot demonstrate is still worth stating, labelled as what it is,
because a human will read it. A repair you cannot verify should be reported as
unverified rather than given the benefit of the doubt.

---

## What this cycle is for

Two questions, and the first is the one §5 turns on.

**1. Are the eleven repairs demonstrated?** For each finding claimed repaired
below, does the current code fix what the finding described, and do its controls
establish that it does? A finding whose repair does not hold stays OPEN, and
saying so is the most useful thing this review can do.

Cycle 02 examined thirteen repair claims and rejected five. Cycle 03 examined
twenty and rejected nine. The rate did not improve between them. It is offered
not as a prediction but because a reviewer who expects every claim to hold reads
past the ones that do not.

The pattern in those fourteen rejections was consistent enough to be worth naming:
**the ordinary path was repaired and the adversarial one was left standing.**
The check worked when called; it was not called from the second place. The
refusal fired on the tested input; a neighbouring input reached the same state by
another route. If you have limited time, spend it there.

**2. Is anything new wrong?** The repairs changed every file in the target. New
defects introduced by the repairs are ordinary findings, reported as `B04-Fnn`.

## The account below is the implementing agent's own

Everything in the repair sections is Claude's description of Claude's work. No
one else has checked it. It is supplied so you spend the cycle on verification
rather than rediscovery, and it should be treated as a claim, not as evidence.

A finding listed as repaired that is not repaired is a finding about this prompt
as much as about the code. Cycle 03 raised exactly that as B03-F02, about this
prompt's predecessor, and it was right to.

---

## What you are reviewing

Ten artifacts, hashed and listed in `target.json`. The same ten as cycles 02
and 03.

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

The covered set is read from `bootstrap_gate.covered()` rather than asserted from
memory. It is ten.

### The control suites are not in this target, and this prompt does not pretend they are

Cycle 03's prompt said "the suites are in the target." They were not, and B03-F02
recorded the over-claim. The repair does not move them into the target —
`target_drift` refuses extra target artifacts, and widening the gate's covered
set is a change Alex Zamurko has not made.

Instead the five suites are hashed into a **manifest recorded beside the target
at freeze**, and `target.json` records the manifest digest, which `target.sha256`
in turn covers. So their exact versions are identifiable from this cycle's
evidence, and a later edit to a suite does not alter what was frozen — but they
are auxiliary evidence, not members of the reviewed set, and the target hash you
are asked to quote does not bind their contents directly.

```text
scripts/test_validate_cycle.py   30 controls
scripts/test_run_review.py       120 controls
scripts/test_ledger.py           76 controls, covering the ledger and controller
scripts/test_bootstrap_gate.py   43 controls
scripts/test_interfaces.py       29 controls, across eleven component seams
```

Those counts total 298, produced by `scripts/refresh_counts.py` and checked by
`scripts/test_prompts.py` against the suites themselves.

**`refresh_counts.py` is not in the covered set and not in this target.** You are
being given a number by a tool you cannot inspect, and the tool has now been
wrong twice. Its predecessor recorded 29 controls where there were 95, because a
suite crashed part-way and emitted no failure. On 15 September it was found
rewriting the prompts of cycles that were already frozen, so cycle 03's prompt
came to assert 298 controls for a review conducted against 263 — and the check
that should have caught that compared the rewritten document against the same
suites that had just been written into it. Both are described under *Found
without a reviewer*, below.

Cycle 03 said, and it still holds: a count cannot show that the intended refusal
is what made a test pass. If you think a count supplied from outside the target
is not evidence you can use, say so as a finding.

---

## The ledger says seventeen are open. Eleven are live work.

This is the one place where the authoritative record and this prompt appear to
disagree, so it is set out here rather than left for you to find and report.

`ledger.json` currently reads `OPEN` for seventeen findings. Eleven of those are
the live work listed below. The other six — B02-F01, B02-F02, B02-F03, B02-F07,
B02-F09 and B02-F10 — are repairs **cycle 03 explicitly demonstrated**, and they
are still `OPEN` because of a collision between two of our own rules:

- Alex Zamurko ruled on 14 September that the cycle-02 findings be marked
  accepted on the day he accepted them rather than backdated, so their `ACCEPT`
  events sit at cycle 3.
- `ledger.py` refuses to resolve a finding in the same cycle it was accepted in,
  because §5 puts the demonstration in the *next* review target after the
  acceptance.

So six findings that were demonstrated could not be recorded as resolved, and no
later cycle re-examines a repair it has already judged. He ruled on 15 September
that they be recorded at cycle 4, each carrying a note naming cycle 03 as what
demonstrated them. That entry will be made when this cycle's ledger step runs.

**You are not asked to re-verify those six.** If you think the resolution is
wrong — that recording a cycle-03 demonstration under cycle 4 makes the ledger's
cycle field mean "when it was written down" rather than "when it happened" — that
is a finding, and a fair one. Cycle 03 made us define the effective-cycle
coordinate for pin amendments in B02-F06; the same ambiguity is arguably now in
the ledger.

---

## Found without a reviewer — two

Both were found by the implementing agent in its own work. Neither carries a
reviewer's identifier and neither is in any authoritative finding set. They are
disclosed because a review told only about the defects someone else caught is
being told a flattering subset.

**A capture attempt recorded on disk but not in the capture log** (10 September,
addressed in `0629bbd`). The log and the directory disagreed about what had been
attempted.

**The count refresh rewrote finished cycles' prompts** (15 September, addressed
in `c3a4020`). Described above. `c2d5c4e` had restored those numbers by hand
once already and the tool put them straight back, which is why the repair is to
the tool.

**The open question both raise:** does a defect the implementing agent finds in
its own work enter the ledger as a finding, or stay a repair with no finding
attached? Entering it means the agent raises findings against itself, which is
the thing this review exists so as not to rely on. Not entering it means the
ledger undercounts what was wrong, and this prompt is the only place either
appears. It has been open since 10 September and is Alex Zamurko's to settle, not
yours — but if you think the current arrangement makes the ledger an unreliable
census of known defects, that is worth stating.

---

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

---

## Claimed repairs, to verify — eleven

Each line gives the finding, the commit, and the control claimed to fail if the
repair is removed. Every repair was checked by mutating the fixed logic and
confirming the named control went red **for its own reason**, with the other
controls staying green.

**That claim is not evidence, and the qualifier is there because cycle 03 caught
its absence.** B01-F11's control in cycle 03 went red under mutation for an
unrelated reason and was recorded as proof anyway; Codex removed the purported
fix and watched the control pass. Two of this cycle's controls were rewritten
after the same test: B02-F04's took four attempts before it discriminated, and
B02-F06's version control first went red for pin drift rather than for the thing
it names. Check whether these controls could actually fail, and fail for the
stated reason.

### Recurrences from cycles 01 and 02 — nine

```text
B01-F02  e1e3c04  MAX_4_REACHED is not clearable by authorisation; the budget
         number lives once, in cycle_projection, instead of one copy per
         component. Rests on Alex Zamurko's ruling, not on code alone.
         control: test_run_review.py "an authorization naming MAX_4_REACHED is
         read, refused, and said out loud"

B01-F04  2e8b1b4  the embedded specs come from the cycle's effective pin set, so
         a spec added by amendment reaches the reviewer.
         control: test_run_review.py "a spec added by amendment appears in the
         composed input"

B01-F07  c85eeee, then 04572f9  the input header quotes the cycle's own digests
         rather than the run's; and check 9 validates the governing digests a
         target records. Two defects under one identifier.
         control: test_run_review.py "the input header quotes the cycle's own
         digests, not the run's"; test_validate_cycle.py "a spec digest that
         does not describe the governing set"

B01-F11  4bac2b6  authority rests on cycle membership, and a REOPENED withdraws
         the acceptance it rested on.
         control: test_ledger.py "an acceptance in a gap between real cycles
         authorizes nothing" and "a reopened finding needs a new acceptance, not
         the spent one"

B01-F14  a576489  the controller and the runner share one run-metadata rule.
         control: test_run_review.py "a protocol run recording its enforcement
         status is concluded normally"

B02-F04  2ad9ccd  one commit point instead of two renames; the attempt directory
         holds its own raw bytes and findings and is never edited again;
         publication repeats before any new recording.
         control: test_run_review.py "a half-published cycle is recovered even by
         a command that is then refused" and "the working copies match the
         designated generation"

B02-F05  a8922fa  added_pin_hashes binds the bytes of newly added pins only.
         control: test_run_review.py "refused: an amendment that rewrites a
         retained pin's hash"

B02-F06  61d6c6f  the frozen check covers every review directory in the run;
         records keep which loop they came from; recorded hashes are compared as
         well as paths.
         control: test_run_review.py "refused: one loop freezing against history
         that contradicts the other loop's completed cycle" and "refused: same
         governing paths under a completed cycle, different versions"

B02-F08  674a394  an unreadable git history is reported as unreadable, not as
         evidence that no approval exists.
         control: test_bootstrap_gate.py "the exception is withheld when the
         history cannot be read"
```

### From cycle 03 — two

```text
B03-F01  004ee0a  only a completed controller run reporting exactly one
         recognised CONTINUE is permission to open a cycle. Nonzero exits,
         missing, unrecognised and conflicting statuses are all refused, and
         replay errors are translated rather than escaping as tracebacks.
         control: test_run_review.py "refused: a controller that says CONTINUE
         and then fails", "refused: a controller that exits 0 and reports no
         status", "refused: a status this runner does not recognise", "refused:
         two statuses in one run"

B03-F02  89e3e3e  the control suites are recorded in a hash-bound manifest
         beside the target rather than described as members of it; the covered
         set is not widened.
         control: test_run_review.py "the manifest records every suite at
         freeze", "target.json records the manifest digest, and target.sha256
         covers target.json", "no control suite appears in the review target",
         "a later suite edit leaves the frozen record unchanged"
```

### Two over-claims corrected without a finding number

Cycle 03 named four claims stronger than their evidence. Two were repaired as
B01-F11 and B03-F02. The other two were prose, and are corrected here:

- `loop_state.py` claimed that ignoring invalid-cycle events "can only ever delay
  an exit, never manufacture one". Cycle 03: ignoring an invalid `RAISED` or
  `REOPENED` removes an actionable finding. The claim is withdrawn.
- `run_review.py`'s opening said `codex-output-raw.md` is never overwritten and
  that `record` refuses whenever raw output is present. That has not described
  the capture-log behaviour for some time. Restated.

Both are in the target. If either restatement still claims more than
`CONVENTION_ONLY` supports, that is a finding.

---

## Reporting

Use the finding block the schema defines. New findings take this cycle's
identifiers:

```text
Finding ID: B04-F01
Class: MISSING REQUIREMENT
Artifact: scripts/example.py
Location: example.py:120
Evidence:
...
Finding:
...
Required correction:
...
```

A finding recurring from an earlier cycle keeps its original identifier —
`B01-Fnn`, `B02-Fnn`, `B03-Fnn` — and its block does not reassert `Class`,
because the ledger already holds the classification and a reviewer restating it
is asserting something it is not judging.

Quote the `TARGET_SHA256` from this cycle's `target.sha256` at the top of your
reply. A capture that does not quote it is not demonstrably a capture of this
target and the runner will refuse it.

If the review has not converged, say so. Cycle 03 ended with "I make no claim
that the review has converged", and that sentence was worth more than a
reassurance would have been.
