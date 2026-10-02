# Bootstrap review prompt — BOOTSTRAP-002, cycle 03

Third cycle of a second `BOOTSTRAP_REVIEW` of the execution layer. Hand-written,
per Alex Zamurko, 8 September: a hand-written prompt is acceptable for the
bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `C03-Fnn`.** The letter is the run and the digits
are the cycle this prompt is frozen at. Cycle 02's prompt said `C01-Fnn` while
being cycle 2's prompt, the ledger would have refused those identifiers, and the
reviewer raised the conflict rather than renaming anything. That was C02-F01 and
it is repaired; this line is the repair being used for the first time.

Use `C01-Fnn` and `C02-Fnn` only when referring to findings those cycles already
raised. `B01` and `B02` belong to BOOTSTRAP-001 and are quoted throughout for
cross-reference.

---

## Why there is a third cycle

Cycle 02 raised eleven findings and all eleven were accepted under §5. Every one
has since been repaired. None has been seen by a reviewer.

§5 gives `RESOLVED` only once a repair is demonstrated in the **next review
target**, so the eleven cannot close by my saying they are fixed, however
carefully they were fixed. That is what this cycle is for.

Cycle 02 also closed the eight findings cycle 01 raised. Those eight were the
first in either run to close on an independent demonstration rather than on the
implementer's assertion.

**This is development evidence, not a protocol outcome.** The gate still reports
no bootstrap review on record, so no real protocol cycle can run. `BOOTSTRAP-002`
is marked `NOT_A_PROTOCOL_CYCLE` and the controller refuses to state an
authoritative loop result for it.

**Nothing here is technically enforced.** `MC1_ENFORCEMENT` is
`CONVENTION_ONLY`. Every check in this layer is detection that holds while the
checks run faithfully and nobody edits the records they read. The same writable
code performs the checks on itself.

---

## What this cycle is for

**1. Are cycle 02's eleven repairs demonstrated?** For each C02 finding, does
the current code fix what that finding described, and do its controls establish
that it does. The accounts below are mine and are offered as claims to be
tested, not as a summary you can adopt.

**2. Do the eight cycle 01 repairs still hold?** They were demonstrated in cycle
02 against code that has since changed in nine of its ten files. A repair that
was demonstrated once and then edited is not thereby still demonstrated.

**3. Is anything else wrong?** The whole target is in scope, not only the parts
these notes discuss.

### What the two completed cycles suggest about where to spend the time

Cycle 01 raised eight findings, cycle 02 raised eleven. Seven of cycle 01's eight
and five of cycle 02's eleven were the same shape: one rule written in two or
more places, with one copy shorter than the others. Two more were the same
reading of absence as age. If there is a pattern worth testing first, it is
those two.

The rate has not fallen across four cycles of BOOTSTRAP-001 and two of this run.
That is offered as context, not as a quota.

---

## The account below is the implementing agent's own

I wrote the repairs and I wrote these notes about them. Cycle 02 said of the
previous version of this document that a count and an implementer description
cannot establish fixture validity, the intended refusal, absence of unintended
failing prerequisites, mutation sensitivity, or interruption behaviour. That was
C02-F10 and it was right.

What is different this time is listed under auxiliary evidence below. What is
not different is that everything in this section is still my account of my own
work.

---

## What you are reviewing

The artifacts hashed and listed in `target.json`, and the gate's covered set,
which are not the same list. Both are below, because the difference is itself
something to look at.

**The target pins ten**, the same ten cycle 02 pinned:

```text
scripts/authority.py              scripts/loop_state.py
scripts/bootstrap_gate.py         scripts/run_pins.py
scripts/cycle_projection.py       scripts/run_review.py
scripts/findings_format.py        scripts/validate_cycle.py
scripts/ledger.py                 specs/evidence-schema-v1.0.md
```

Seven of those ten changed since cycle 02, compared digest by digest against
the hashes cycle 02's target recorded. `authority.py`, `findings_format.py` and
the evidence schema are byte-identical to the versions cycle 02 reviewed.

I first wrote nine here and checked afterwards. Twice now in this document a
number I was confident about was wrong, and both times the check was something I
chose to run rather than something that would have caught me. Treat the
unchecked claims below with that in mind; they are the same kind of writing.

**The gate covers seventeen:**

```text
declared                          reached through the import closure
scripts/authority.py              scripts/convert_protocol.py
scripts/bootstrap_gate.py         scripts/refresh_counts.py
scripts/cycle_projection.py       scripts/verify_amendment.py
scripts/findings_format.py        scripts/test_convert_protocol.py
scripts/ledger.py                 scripts/test_prompts.py
scripts/loop_state.py             scripts/test_protocol_pin.py
scripts/run_pins.py               scripts/test_run_review.py
scripts/run_review.py
scripts/validate_cycle.py
specs/evidence-schema-v1.0.md
```

**Seven reached coverage through the import closure rather than by being
declared.** The gate treats any `name.py` token appearing in a covered file as a
dependency and pulls it in. So a reviewer is never asked about those seven while
the gate treats them as reviewed, which is the shape of B01-F09 and of C02-F07.

**Four of the seven are control suites, and one is `refresh_counts.py`.** Two
consequences, both stated rather than argued away.

Everything else in this document says control suites belong beside the target
and not inside it, because putting them in means every control edit invalidates
the bootstrap approval of the production code. Four are inside it anyway, by
accident of a token-matching rule rather than by anyone's decision, and
`test_run_review.py` is among them. That is the file nearly every new control in
this run was written into, including the ones for the eleven repairs below.

And cycle 02's prompt told its reviewer, in terms, that `refresh_counts.py` is
not in the covered set and not in that target. It is in this one. Whether it was
in that one I have not established, and I am not going to assert either way
here.

I am not repairing any of this in this cycle. Changing the gate's covered set is
Alex Zamurko's to decide, and all of it reached me while writing this prompt
rather than through a review, which is the wrong order for a change to what
counts as reviewed.

The schema's current bytes have still been reviewed by nobody. It has been
amended twice since BOOTSTRAP-001 last looked at it.

### The control suites are auxiliary evidence, and this time they are here

`target_drift` refuses extra target artifacts, and widening the gate's covered
set is a change Alex Zamurko has not made. Cycle 02 accepted that and asked for
something else: "keeping tests auxiliary is compatible with supplying and
preserving their exact contents for examination."

So this cycle's evidence directory carries, beside the target rather than inside
it:

```text
auxiliary/scripts/test_*.py      the exact suite bytes, digest-matched
auxiliary/observed-run.txt       every suite's exit code and output, from a
                                 run performed during this freeze
auxiliary-evidence.json          the manifest, which now records where each
                                 preserved copy is and what its run returned
```

`target.json` records the manifest digest and `target.sha256` covers that, so a
change to any of it is detectable by anyone who compares the two. No MC-2 check
performs that comparison. This is a record, not an enforced binding, and the
distinction is the one cycle 02 asked to be made explicit.

```text
scripts/test_validate_cycle.py    50 controls
scripts/test_run_review.py       147 controls
scripts/test_ledger.py           113 controls, covering the ledger and controller
scripts/test_bootstrap_gate.py    44 controls
scripts/test_interfaces.py        29 controls, across eleven component seams
```

Those counts total 383, up from 319 at cycle 02. They are produced by
`scripts/refresh_counts.py` and checked by `scripts/test_prompts.py` against the
suites themselves.

**Three kinds of evidence, and they are not interchangeable.** Source
inspection: the preserved suite bytes, which you can read. Observed execution:
`observed-run.txt`, which is what happened when they ran on one machine at one
moment. Implementer assertion: everything else in this document. Cycle 02 was
given only the third.

**What the preserved suites still do not establish.** That a fixture is valid.
That a passing control is checking the thing it is named for. That the results
reproduce anywhere else. If a count or a single observed run is not evidence you
can use for a particular claim, say so as a finding.

### The mutation probe, and its own limits

`_probe/mutate_repairs.py` removes each repair from the real source one at a
time and requires its suite to go red, and requires the failure text to name
something specific to that repair rather than any failure at all. Twenty five
mutations, covering the eight cycle 01 repairs, the eleven of cycle 02, and
three exit-condition rules.

It found three of my own controls passing for reasons other than the ones they
named: a mutation aimed at a rule the control was not exercising, a control
whose fixture was being refused by check 10 over a stale digest and had never
reached check 14 at all, and a needle matched against the wrong side of the
test. Each was corrected and recorded in the probe's own source.

**The probe is not in the covered set and not in this target.** Its source is
preserved under `auxiliary/` so that it can at least be read, and
`auxiliary-evidence.json` records it as an instrument: preserved, deliberately
not run at freeze, and carrying no recorded result. A full run takes twenty-odd
minutes because it runs a whole suite per mutation, so a freeze that waited for
it would be a freeze nobody performs.

That leaves its reported outcome as my assertion. You have the source and not
the run, which is a weaker position than the suites are in, and it is stated
rather than glossed. `refresh_counts.py` put cycle 02 in the position of being
given a number by a tool it could not inspect, and that tool was wrong three
times.

Mutation sensitivity is not claimed by `auxiliary-evidence.json`, deliberately.
It is a separate instrument and conflating the two would overstate both.

---

## Cycle 02's eleven findings, and what was done about each

All eleven were repaired between 30 September and 2 October. Each account is
mine. The named controls are in the preserved suites.

**C02-F01 · a prompt numbered its findings from the wrong cycle.** Following
cycle 02's prompt would have given a new defect an existing finding's identity,
or given new cycle-02 issues cycle-01 digits the ledger refuses at cycle 2.
`specs/review/PROMPT-NUMBERS-FINDINGS-BY-CYCLE.md` states the rule;
`test_prompts.py` binds the frozen prompt's exemption to a finding that is
actually recorded in the ledger, in both directions, so the exemption cannot
quietly become a list of things we have stopped checking.

**C02-F02 · command-only chronological guards had no replay equivalent.** C01-F01
moved the six-event reproduction into the shared evaluator and stopped there.
Three ordering rules still lived only in the ledger commands, so an invalid
pre-existing history could reconstruct an authoritative resolution during replay.
`Walk` now carries `accepted_at` and `demonstrated_at` and enforces all three,
and `ledger.py` asks `cycle_projection.would_apply` rather than keeping its own
copy. Controls: three forged histories plus a positive pair.

**C02-F03 · the age exemption was granted on absence alone.** Check 9 skipped
the governing checker whenever both governing fields were absent, which a modern
target achieves by deleting them. `MODERN_MARKERS` names the fields only a later
freeze emits, and a record carrying one of them cannot claim to predate what it
omits. The matching positive is kept beside the refusal, because refusing both
would retroactively invalidate BOOTSTRAP-001's first two cycles, which is the
thing the exemption exists to prevent.

**C02-F04 · a recurrence could stand against a RESOLVED entry.** The controller
reparsed the reviewer's output but discarded the recurrence kind before checking
accounting, so a valid review reporting an unresolved defect could be measured
against an older resolution. `authoritative_items` now returns full entries and
the controller refuses a recurrence standing against a RESOLVED entry without a
reopening.

**C02-F05 · two cycle-directory grammars.** The checker read `cycle-(\d+)` and
the controller `cycle-(\d{2})`, so `cycle-1` was an accepted cycle to
conformance and not a cycle at all to the projection that counts them toward the
budget. One grammar now, in `run_pins`, read by both, because the checker cannot
import the controller that runs it.

**C02-F06 · an interrupted designation could be taken by a later capture.** An
interruption after an attempt's `findings.json` was written and before the
designation was recorded left a complete valid first capture and a log naming
nobody; the next `record` could then supply different output and have it
designated with no supersession approval. Recovery now finishes that designation
before any new candidate is considered, so the recovered capture is defended by
the same refusal every designated capture has.

**C02-F07 · the gate's evidence need not name the target.** Stale review
evidence for target A could be approved against a newly frozen target B, with
both independently hashed and the decision recording only their coexistence.
`cmd_record` now refuses unless the preserved input carries the target's digest.
Two test fixtures could previously only be built by exploiting this, which is
itself evidence the finding was real; they are fixed at source.

**C02-F08 · the reviewed diff was supplied beside the candidate.** The freeze
resolved a real candidate commit and then read whatever file `--diff` named, so
a cycle could pin commit B and show a diff of A with every hash well formed. The
diff is now derived by the runner from `--base` to `--candidate-commit`, and
check 14 re-derives the change set from the two commits the target names and
refuses a diff that is not the change between them. The binding is checked on
`git diff --raw` rather than on patch text, because patch text varies with
configuration and git version while the change itself does not.

**C02-F09 · a missing snapshot was filled from a live file.** Deleting an
implementation cycle's preserved diff, test results, approved plan or approval
record did not necessarily invalidate it, because each absent snapshot fell back
to today's matching file. The fallback is now conditional on the record carrying
no marker of a freeze that preserves. Controls delete one snapshot at a time
with the live file left in place, which is the hard case: the bytes agree and
nothing looks wrong.

**C02-F10 · the controls were asserted, not supplied.** Addressed in two parts:
the mutation probe described above, and the preserved sources and observed run
described above. Neither existed when cycle 02 reviewed this.

**C02-F11 · a bare status escaped through an early return.** A recognised exempt
run containing only invalid cycles could emit an unqualified `LOOP_STATUS:
CONTINUE` through `--development --quiet`, bypassing the labelling added so a
caller cannot mistake development analysis for a protocol outcome. One formatter
now, defined before the early return and used by both paths.

### One thing found and deliberately not repaired

The evidence schema's historical parsing still reads a mutable document to
decide what an old record meant. Repairing it off the draft would put a change
into the target that no review has seen. It enters through this review instead.

---

## What changed since cycle 02 and has been reviewed by nobody

Seven of the ten pinned artifacts changed. `run_pins.py` gained the shared cycle
grammar and the shared git invocations. `validate_cycle.py` gained the modern
marker rule, the derived-diff comparison in check 14, and the snapshot
requirements in checks 13 to 15. `run_review.py` gained designation recovery,
diff derivation, and the auxiliary preservation and observed run. `ledger.py`
and `cycle_projection.py` were rewired so the ordering rules live in one place.

The freeze now runs every control suite before it will create a cycle, and
refuses if any suite fails unless that suite is named with `--aux-known-red` and
explained. `test_approval_package.py` is named in this cycle's record with its
reason: an approval package for a run with frozen cycles and no ledger stays
silent, and silence reads as no findings rather than as nobody having looked.
That is a known defect, not a passing test.

---

## What you are reviewing them against

The protocol and the evidence schema named in `run.json`, and nothing else. Both
are pinned at freeze and their digests are in `target.json`.

The six finding classes of §4 are closed. `OUT OF VOCABULARY` remains available
as a human-visible diagnostic: no Finding ID, never written to `findings.json`,
never in a lifecycle state, no effect on loop state. The ledger refuses it by
name.

---

## Reporting

One block per finding, in the §4 format, with `Finding ID: C03-F01` and upward.

Where a finding concerns one of the eleven repairs above, name the C02
identifier in the evidence so the two records can be joined. Where a repair you
examined is not demonstrated, report it in the recurrence form against its
existing identifier rather than as a new finding, so the ledger reopens it
instead of recording two names for one defect.

A repair you cannot verify should be reported as unverified rather than given
the benefit of the doubt. The preserved suites are there so that "unverified"
can be narrowed to a specific thing you looked at and could not establish.

State plainly at the end whether this review converged, and if it makes no such
claim, say that instead. Every cycle of BOOTSTRAP-001 ended by saying it made no
claim of convergence, and each time that was the accurate thing to say.
