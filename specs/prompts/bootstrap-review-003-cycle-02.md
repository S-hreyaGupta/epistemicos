# Bootstrap review prompt — BOOTSTRAP-003, cycle 02

Second cycle of the third `BOOTSTRAP_REVIEW` of the execution layer.
Hand-written, per Alex Zamurko, 8 September: a hand-written prompt is
acceptable for the bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `D02-Fnn`.** Each run has its own prefix letter
so two runs cannot raise findings under one name: `B` for BOOTSTRAP-001, `C`
for BOOTSTRAP-002, `D` for this one. `D01-F01` is cycle 01's finding, and
`C02-F08` and `C03-F02` are BOOTSTRAP-002's.

---

## What this cycle is for

Cycle 01 raised one finding and sent two of three implementer-disclosed
repairs back as not demonstrated. All three have since been repaired, and
nobody independent has seen any of them.

Alex Zamurko set the terms on 7 October, after reading cycle 01:

    Send all three repaired findings to the independent reviewer again.
    Why: two repairs previously thought to be correct were not demonstrated.
    Developer confirmation is therefore insufficient evidence of closure.

So, in order of what matters:

**1. `D01-F01`, cycle 01's finding.** Is the boundary-accounting defect
repaired, and do its controls establish that rather than merely accompany it.

**2. The three implementer-disclosed defects, again.** `SELF-F01` and
`SELF-F02` were examined in cycle 01 and found not closed. `SELF-F03` was
found supported. All three are in `registers/implementer-disclosed.json` with
cycle 01's verdict recorded in each history.

**3. Does anything else in the target still hold?** The whole target is in
scope. One covered file changed; the other ten did not.

---

## The account below is the implementing agent's own

I wrote the repairs and I wrote these notes. Everything here is my claim about
my own work, offered to be tested rather than adopted. Cycle 01 is the reason
to treat it that way: two of the three things I described as repaired were not.

---

## What you are reviewing

**Eleven files**, the same set as cycle 01, and the same list the gate covers:

```text
specs/covered-components.json     scripts/ledger.py
specs/evidence-schema-v1.0.md     scripts/loop_state.py
scripts/authority.py              scripts/run_pins.py
scripts/bootstrap_gate.py         scripts/run_review.py
scripts/cycle_projection.py       scripts/validate_cycle.py
scripts/findings_format.py
```

**Exactly one has changed since cycle 01's target**, compared digest by digest:
`scripts/loop_state.py`. The other ten are byte-identical to what cycle 01 saw.
That one file carries the whole of `D01-F01`'s repair and nothing else.

### The control suites, preserved and run

```text
scripts/test_bootstrap_gate.py    53 controls
scripts/test_interfaces.py        29 controls, across eleven component seams
scripts/test_ledger.py           126 controls
scripts/test_run_review.py       155 controls
scripts/test_validate_cycle.py    54 controls
```

417 in total, up from 413 at cycle 01. The four new ones are `D01-F01`'s, in
`test_ledger.py`. They are produced by `scripts/refresh_counts.py` and checked
by `scripts/test_prompts.py` against the suites themselves.

**Two suites are not in that count and both are green.**
`scripts/test_approval_package.py` covers the package generator, and
`scripts/test_probe_recovery.py` is new in this cycle and covers the mutation
probe's crash recovery. Neither file is a covered component and nothing covered
imports them, so counting them would inflate a figure the frozen prompts state
about the review target. Both are preserved beside the target like the rest.

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

### The mutation probe, and what it did this round

`_probe/mutate_repairs.py` removes each repair from the real source one at a
time and requires its suite to go red, with a failure naming something specific
to that repair. **Its result is my assertion**: the source is preserved so you
can read it, it is not run at freeze, and the last whole-set run predates this
cycle's additions. Filtered runs establish nothing about the lines they skip.

What it did to `D01-F01` is worth stating, because it is the kind of thing a
green suite cannot show. The repair has two rules. With both in place, removing
the first changed nothing any control could see: the second rule refused the
same fixture first, so the first rule was unwatched while appearing tested. The
probe reported it, and the fixture that isolates each rule from the other was
written because of that report. It then reported the replacement line twice
more, once for pointing at the wrong fixture and once for matching a control's
success text instead of its failure text.

---

## `D01-F01`, and what was done about it

**The finding**, in cycle 01's words: the stateless-finding check replayed
history over `set(valid)`, every valid cycle in the run, while each boundary is
computed over `valid[:n]`. A finding reported by cycle 1's reviewer whose
`RAISED` event sits in cycle 2 therefore had a state when checked and none at
its own boundary, where it silently left `OPEN_1`. The reviewer built the
fixture and showed `STALLED` becoming `CONVERGED` by moving one event, with
`cycle_raised` and the reviewer evidence untouched.

**The repair, in two parts.** The replay is limited to the cycles through the
reporting boundary, which is the question actually being asked: does this
finding have a state established by the cycles that had reported it by then.
And an entry whose `cycle_raised` disagrees with its own `RAISED` event is
refused outright, which is cycle 01's "refuse contradictory originating-cycle
metadata and history".

**Three controls**, each exercising a rule no other rule can answer for: cycle
01's own fixture, which the contradiction rule refuses; the same defect with
the origin made consistent, which only the boundary rule can refuse; and a
contradictory origin that no cycle reports, which only the contradiction rule
can refuse. Each requires a refusal, and the first requires that no
`LOOP_STATUS:` line is emitted, since an undeterminable state must not be
reported as a state.

**What this does not establish.** The repair makes the controller stricter, so
it can now refuse ledgers it used to accept. Whether anything beyond the two
cases named is affected is not something these controls show.

---

## BOOTSTRAP-002 under the corrected controller

Alex Zamurko asked whether BOOTSTRAP-002's closure depended on the defective
logic. Re-run under the repaired controller it produces the same result:
`MAX_4_REACHED`, the same two open findings, the same nineteen resolved, exit
0, and neither new refusal fires anywhere in its ledger.

The command and its full output are recorded in
`runs/BOOTSTRAP-002/CORRECTED-CONTROLLER-RECHECK.md` so this can be re-run
rather than taken on my word. That run stays closed as it ended.

---

## The three implementer-disclosed defects

Not reviewer findings, no cycle identifiers, tracked in
`registers/implementer-disclosed.json` by Alex Zamurko's ruling of 6 October.
Cycle 01's verdict on each is recorded in its history, in cycle 01's words.

**`SELF-F01` · an approval package could present silence as no findings.**
Cycle 01: "a readable ledger containing `{"findings": {}}` beside a valid
review reporting a finding still produces an approval package with exit 0...
the unresolved-findings section says 'None' and its coverage item is marked
present."

My first repair handled the two ways a ledger can fail to be **read**, missing
and unparseable. It did not handle the way it can fail to be **true**. The
findings each frozen cycle reported are now reconciled against the ledger
before any category is asserted empty, and a disagreement is
`CANNOT_ESTABLISH`. The recorded findings are read through `loop_state`'s own
reader rather than a second one written in the package generator. One control,
whose ledger is valid and parses and simply holds none of what the cycle beside
it reported.

**`SELF-F02` · a killed probe left a disabled check in tracked source.**
Cycle 01: the recovery ran `git checkout -- <path>`, which restores from the
index, while the message said HEAD; with different bytes staged it wrote those
and reported restoration from HEAD.

That was exactly right and the claim in my output was false. The bytes are now
read with `git show HEAD:<path>`, which names its source in the command, cannot
be satisfied from the index, and leaves the index alone. The restored file is
then verified against HEAD's bytes rather than the command's exit code being
trusted. The probe had **no controls at all** before this cycle, which is why a
wrong repair to it could pass; `scripts/test_probe_recovery.py` now holds five,
including cycle 01's staged-bytes fixture.

Writing those controls found a second defect cycle 01 had not reported:
recovery ran **after** the argument filter, so a run whose filter matched
nothing exited with the mutation still applied. Recovery now runs before
anything else.

**`SELF-F03` · the gold runner scored its two sides by different rules.**
Cycle 01 found the repair supported, and was explicit about two limits: it does
not validate the historical improvement figures, and it is not frozen-component
approval of `gold_runner.py`, which is in no review target. The register records
it as `RESOLVED` with both limits attached.

**A claim of mine that cycle 01 refused**, and I have not reinstated it: that
none of these three could produce a false green. `SELF-F02` concerns suites
passing while a check is disabled, and `SELF-F01` could still present an empty
findings category as a finished one. The register now says so.

---

## What cycle 01 established about BOOTSTRAP-002's two findings

`C02-F08` and `C03-F02` were assessed as demonstrated for the defects reported.
Cycle 01 is explicit that this is external development evidence and does not
change BOOTSTRAP-002's terminal result or its ledger states, and nothing has
been written into that run's ledger on the strength of it.

---

## What you are reviewing them against

The protocol and the evidence schema named in `run.json`, and nothing else.
Both are pinned at freeze and their digests are in `target.json`.

The six finding classes of §4 are closed. `OUT OF VOCABULARY` remains available
as a human-visible diagnostic: no Finding ID, never written to `findings.json`,
never in a lifecycle state, no effect on loop state. The ledger refuses it by
name.

**This is development evidence, not a protocol outcome.** `BOOTSTRAP-003` is
marked `NOT_A_PROTOCOL_CYCLE` and the controller refuses to state an
authoritative loop result for it. `MC1_ENFORCEMENT` is `CONVENTION_ONLY`: every
check here is detection that holds while the checks run faithfully and nobody
edits the records they read.

---

## Reporting

One block per finding, in the §4 format, with `Finding ID: D02-F01` and upward.

Where a repair named above is not demonstrated, report it in the recurrence
form against its existing identifier, `D01-F01`, rather than as a new finding,
so it reopens instead of acquiring a second name. The implementer-disclosed
entries have no cycle identifiers by Alex Zamurko's ruling; report on them by
their register names.

A repair you cannot verify should be reported as unverified rather than given
the benefit of the doubt. The preserved suites are there so that "unverified"
can be narrowed to a specific thing you looked at and could not establish.

State plainly at the end whether this review converged, and if it makes no such
claim, say that instead.
