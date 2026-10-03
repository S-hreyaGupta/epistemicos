# Bootstrap review prompt — BOOTSTRAP-002, cycle 04

Fourth and final cycle of a second `BOOTSTRAP_REVIEW` of the execution layer.
Hand-written, per Alex Zamurko, 8 September: a hand-written prompt is acceptable
for the bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `C04-Fnn`.** Use `C01-`, `C02-` and `C03-`
identifiers only when referring to findings those cycles raised. `B01` and `B02`
belong to BOOTSTRAP-001.

---

## Why there is a fourth cycle

Cycle 03 left six findings open: four cycle-02 repairs it refused to call
demonstrated, and two new defects. All six have since been repaired. None has
been seen by a reviewer.

§5 gives `RESOLVED` only once a repair is demonstrated in the **next review
target**, so none of them can close by my saying they are fixed. That is what
this cycle is for.

**This is the last cycle the protocol allows.** `MAX_VALID_CYCLES` is 4 and
three are spent. You should know that, and it should not change what you report.
If this review raises findings the run ends at `MAX_4_REACHED` with them open,
which is how BOOTSTRAP-001 ended and is a legitimate outcome of the loop rather
than a failure of it. A review that found less than was there in order to let a
run converge would be worth nothing, and the whole arrangement exists because
the implementing agent cannot be the judge of its own work.

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

**1. Are cycle 03's six findings repaired?** For each, does the current code fix
what the finding described, and do its controls establish that it does.

**2. Do the earlier repairs still hold?** Fifteen findings are `RESOLVED`. Seven
of the eleven covered files changed since cycle 03, so a repair demonstrated
then was demonstrated against code that has moved.

**3. Is anything else wrong?** The whole target is in scope.

---

## The account below is the implementing agent's own

I wrote the repairs and I wrote these notes. Everything in the finding-by-finding
section is my claim about my own work, offered to be tested rather than adopted.
What is not my claim is listed under auxiliary evidence: the control sources are
preserved and their run is recorded.

---

## What you are reviewing

**Eleven files.** For the first time the review target and the gate's covered set
are the same list, which is the repair for C03-F02:

```text
specs/covered-components.json     scripts/ledger.py
specs/evidence-schema-v1.0.md     scripts/loop_state.py
scripts/authority.py              scripts/run_pins.py
scripts/bootstrap_gate.py         scripts/run_review.py
scripts/cycle_projection.py       scripts/validate_cycle.py
scripts/findings_format.py
```

Cycle 03 found that the gate derived its covered set by scanning covered files
for anything that looked like a Python filename, which had grown the set from ten
to seventeen, including four control suites and a file named only inside a
comment. Alex Zamurko ruled on 2 October that the set must be explicit and
authoritative, that filename references must not expand it, and that test suites
are review evidence rather than approved components. `specs/covered-components.json`
is that list. It is itself covered, so changing the scope invalidates existing
approvals.

Seven of the ten files cycle 03 reviewed have changed since, compared digest by
digest against that cycle's target. `authority.py`, `ledger.py` and the evidence
schema are byte-identical to what cycle 03 saw.

### The control suites, preserved and run

```text
scripts/test_validate_cycle.py    54 controls
scripts/test_run_review.py       150 controls
scripts/test_ledger.py           122 controls
scripts/test_bootstrap_gate.py    49 controls
scripts/test_interfaces.py        29 controls, across eleven component seams
```

Those counts total 404, up from 383 at cycle 03. They are produced by
`scripts/refresh_counts.py` and checked by `scripts/test_prompts.py` against the
suites themselves.

Beside the target, not inside it:

```text
auxiliary/scripts/test_*.py      the exact suite bytes, digest-matched
auxiliary/observed-run.txt       every suite's exit code and output, from a
                                 run performed during this freeze
auxiliary/_probe/                the mutation probe's source, preserved and
                                 NOT run at freeze
auxiliary-evidence.json          the manifest tying all of it to this target
```

**Three kinds of evidence, and they are not interchangeable.** Source
inspection: the preserved suite bytes. Observed execution: `observed-run.txt`.
Implementer assertion: everything else in this document.

**`test_approval_package.py` does not pass**, and is named in this cycle's
record with its reason. An approval package for a run with frozen cycles and no
ledger stays silent, and silence reads as no findings rather than as nobody
having looked. That is a real defect, it predates this run, and it is still
there.

### The mutation probe, and what it does not establish

`_probe/mutate_repairs.py` removes each repair from the real source one at a
time and requires its suite to go red, with a failure naming something specific
to that repair. Thirty nine mutations, covering every repair in both runs.

It has now found four of my own controls passing for reasons other than the ones
they named. The most recent is worth stating because it is a failure mode a
green suite cannot show: C02-F08's second repair added a stronger check, which
made the first repair's control pass for the new reason instead of the old one.
Removing the original rule changed nothing anyone could see. Both rules now have
their own control.

**The probe's result is my assertion.** Its source is preserved so you can read
it; it is not run at freeze, because a full run takes twenty-odd minutes. You
have the instrument and not the run, which is weaker than the suites' position
and is stated rather than glossed.

---

## Cycle 03's six findings, and what was done about each

**C02-F02 · a chronological guard that lived only in the commands.** The shared
evaluator did not retain the cycle a finding was raised in, so the history
`RAISED(3), ACCEPT(1), DEMONSTRATED(4)` replayed as `RESOLVED` while the write
commands refused every part of it. `Walk` now carries `raised_at` and refuses an
acceptance or a rejection dated before it. Controls: the three forged histories
cycle 03 named, plus the legal pair that keeps them honest.

**C02-F03 · the exemption for old evidence, claimed by new evidence.** Dating a
target by the fields it happens to carry meant the list had to grow with the
freezer, and a modern target stripped back to the bone read as historical. A
target now declares `evidence_format`, and only a record declaring none is dated
by inference. An unrecognised format is refused rather than read as newer.

**C02-F04 · the classification taken from the transcription.** The controller
read `kind` from `findings.json` and never asked whether it matched the review it
came from, so a recurrence recorded as a new finding skipped the reopening
guard. The classification now comes from the reparse, and a structured copy that
disagrees is refused rather than overruled quietly. Entries written before the
field existed are filled from the reparse.

**C02-F08 · a patch that need not describe its own change.** The first repair
derived the patch and recorded a digest of the change set, and check 14 compared
each against its own record without relating them. The preserved patch must now
name the same objects the change does, compared on blob identities rather than
patch text so that context width, rename detection and whitespace cannot move
the answer.

**C03-F01 · a completed review read with today's schema.** The parser read the
live evidence schema every time, including when re-reading a review from weeks
ago, so amending the grammar changed what a finished cycle meant. Each cycle is
now reparsed with the grammar it recorded. A cycle that recorded none falls back
to the live schema, which is the bounded compatibility path.

**C03-F02 · the covered set and the reviewed target disagreed by construction.**
Described above. Three rounds of correction from Alex Zamurko shaped it: one
list rather than two, the manifest's own history is descriptive rather than
proof, and a commit evidences that a change happened rather than that it was
authorised. A scope change now requires the manifest to be committed and an
approval record naming a human, bound to that version's exact bytes, committed
as well.

---

## What changed since cycle 03 and has been reviewed by nobody

Seven of the eleven covered files. `bootstrap_gate.py` lost its derivation
entirely and gained the manifest, its provenance and its authorisation checks.
`cycle_projection.py` gained the raising-cycle guard. `findings_format.py` and
`loop_state.py` gained the per-cycle grammar binding. `run_pins.py` gained the
evidence-format vocabulary and the blob-pair helpers. `run_review.py` and
`validate_cycle.py` carry the rest.

`specs/covered-components.json` and `approvals/covered-scope/v1.json` are new.
The second is not a covered component and is not in this target; it is the
record that authorises the first.

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

One block per finding, in the §4 format, with `Finding ID: C04-F01` and upward.

Where a repair named above is not demonstrated, report it in the recurrence form
against its existing identifier rather than as a new finding, so the ledger
reopens it instead of recording two names for one defect.

A repair you cannot verify should be reported as unverified rather than given
the benefit of the doubt. The preserved suites are there so that "unverified"
can be narrowed to a specific thing you looked at and could not establish.

State plainly at the end whether this review converged, and if it makes no such
claim, say that instead. Every cycle of BOOTSTRAP-001 ended by saying it made no
claim of convergence, and each time that was the accurate thing to say.
