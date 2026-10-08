# Bootstrap review prompt — BOOTSTRAP-003, cycle 03

Third cycle of the third `BOOTSTRAP_REVIEW` of the execution layer.
Hand-written, per Alex Zamurko, 8 September: a hand-written prompt is
acceptable for the bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `D03-Fnn`.** Each run has its own prefix letter:
`B` for BOOTSTRAP-001, `C` for BOOTSTRAP-002, `D` for this one. `D01-F01` and
`D02-F01` are this run's earlier findings; `C02-F08` and `C03-F02` are
BOOTSTRAP-002's.

**You may name those identifiers freely.** Until this cycle you could not: the
recorder treated any canonical identifier anywhere in a zero-finding reply as a
finding block it had failed to parse, so a review saying "the repair to D01-F01
is demonstrated, no new findings" could not be captured at all. That is
`D02-F01`, which cycle 02 raised, and it is repaired below. If this review
reports nothing new, say so in whatever words you like.

---

## What this cycle is for

**1. `D02-F01`.** Is the reference-versus-declaration distinction correct, and
does the signal net still catch a finding block the strict parser missed.

**2. `SELF-F01`, for the third time.** Cycle 01 found my first repair
incomplete. Cycle 02 found my second repair incomplete, in a different place.
Alex Zamurko, 8 October: "SELF-F01 is critical. The package can say 'none
unresolved' while the controller says OPEN / CONTINUE... The package must
derive finding state from the controller's reconstructed state, not stale
cached ledger state."

**3. Do the earlier repairs still hold?** `D01-F01` is `RESOLVED` on cycle 02's
assessment. Two covered files changed since that cycle.

**4. Is anything else wrong?** The whole target is in scope.

---

## The account below is the implementing agent's own

I wrote the repairs and I wrote these notes. Cycle 01 found two of three things
I called repaired were not; cycle 02 found one of those two still not repaired
after a second attempt. Treat what follows accordingly.

---

## What you are reviewing

**Eleven files**, the same set as cycle 02, and the same list the gate covers:

```text
specs/covered-components.json     scripts/ledger.py
specs/evidence-schema-v1.0.md     scripts/loop_state.py
scripts/authority.py              scripts/run_pins.py
scripts/bootstrap_gate.py         scripts/run_review.py
scripts/cycle_projection.py       scripts/validate_cycle.py
scripts/findings_format.py
```

**Two have changed since cycle 02's target**, compared digest by digest:
`scripts/findings_format.py` carries `D02-F01`'s repair, and
`scripts/loop_state.py` carries the half of `SELF-F01`'s repair that lives in
the controller. The other nine are byte-identical to what cycle 02 saw.

**`scripts/approval_package.py` also changed and is NOT in this target.** It is
not a covered component and nothing covered imports it. The other half of
`SELF-F01`'s repair is in that file, so assessing `SELF-F01` means reading a
file outside the review target; it is preserved beside the target with the
suites. Its state is a register assessment, not a finding about a covered
component.

### The control suites, preserved and run

```text
scripts/test_bootstrap_gate.py    53 controls
scripts/test_interfaces.py        29 controls, across eleven component seams
scripts/test_ledger.py           126 controls
scripts/test_run_review.py       160 controls
scripts/test_validate_cycle.py    54 controls
```

422 in total, up from 417 at cycle 02. The five new ones are `D02-F01`'s, in
`test_run_review.py`. They are produced by `scripts/refresh_counts.py` and
checked by `scripts/test_prompts.py` against the suites themselves.

**Two suites are not in that count and both are green.**
`scripts/test_approval_package.py`, which gained two controls for `SELF-F01`
this cycle, and `scripts/test_probe_recovery.py`. Neither file is a covered
component, so counting them would inflate a figure the frozen prompts state
about the review target.

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

### The mutation probe

`_probe/mutate_repairs.py` removes each repair from the real source one at a
time and requires its suite to go red, with a failure naming something specific
to that repair. **Its result is my assertion**: preserved so you can read it,
not run at freeze, and the last whole-set run predates this cycle's additions.

It earned its place again this cycle. My first `SELF-F01` mutation crashed the
package instead of reproducing the defect, and the probe reported it as the
wrong control rather than counting it: a crash is not the defect, and a control
that fires on one establishes nothing about the repair. The mutation now
restores the old behaviour exactly.

---

## `D02-F01`, and what was done about it

**The finding.** `SIGNALS` in `findings_format.py` held three patterns, and the
third was `\b[A-Z]{0,2}\d{2}-F\d{2,3}\b`: any canonical identifier, anywhere.
The net runs whenever nothing parsed, so a zero-finding review that mentioned an
earlier finding tripped it and zero could not be asserted. Cycle 02 supplied the
target hash and "The repair to D01-F01 is demonstrated. No new findings." and
both `extract()` and `capture_validity(..., zero_asserted=True)` refused it.

That the cycle 02 prompt instructed the reviewer to assess `D01-F01` explicitly
made the instruction and the recorder contradict each other, and had done since
the prompt was written.

**The repair.** The net is not dropped: it exists because a block with a
malformed header parses to nothing, and zero must not be assertable over a
review the parser may have failed to read. What distinguishes a declaration
from a reference is not the identifier but the `Class` or `Status` line a
finding block must carry. The identifier now counts only when one of those is
attached to it, on the same line or within the two lines below.

**Five controls.** Two positives that were impossible before, a zero-finding
review naming one demonstrated repair and another naming three. Three refusals
so the repair cannot become "an identifier in the text is always harmless": a
malformed header with a `Class` line below it, the same with a `Status` line,
and an identifier with its class on one line. The malformed-header fixtures
write `Finding-ID` and `Finding_ID` so the strict header misses them and only
the net can catch them, which is the case the net exists for.

**What this does not establish.** A finding block that carries neither a class
nor a status, and no recognisable header, still parses to nothing and no longer
trips the net. Such a block is not a valid finding under §4, but if you can
construct one a reviewer would plausibly write, it is a gap.

---

## `SELF-F01`, third attempt

**What cycle 02 found.** The package grouped findings by the `state` field
cached in the ledger. That field is written when an event is recorded and is
not recomputed when a cycle later becomes invalid. Cycle 02 invalidated the
cycle carrying a demonstration, left the stale `RESOLVED` in place, and the
controller reconstructed the finding as `OPEN` and reported `CONTINUE` while
the package exited 0, printed "None" under unresolved findings, and counted one
resolved.

**The repair, in two halves.** `loop_state.py` gained a `--json` flag that
prints the governing boundary and its §6 sets from the walk it already
performs. `approval_package.py` reads that instead of the cached fields, and
refuses with `FINDINGS_STATE: CANNOT_ESTABLISH` when the controller cannot
establish a state at all.

A flag rather than a second boundary walk in the package. The exit order is
load-bearing and a copy of it elsewhere would be free to disagree, which is the
defect class this layer keeps finding in itself. The package also now states,
in the document, that the states shown are reconstructed at the governing
boundary rather than read from the ledger.

**Two controls**, and the baseline matters as much as the case: with the
demonstration intact the finding really is resolved and the package must say
so, or a package that called everything unresolved would satisfy the other one.
The fixture is built from `test_ledger`'s own cycle builder rather than a
second one written for this suite.

**Both of my first attempts at those controls passed for the wrong reason.**
They searched the whole document after a heading, which reaches the full-ledger
dump at the foot of it, so a finding appeared "listed" under a heading it never
appeared beneath. That is the same defect in the control as the one the control
is about, and it was caught by the controls disagreeing with each other rather
than by me reading them.

**What this does not establish.** The package asks the controller for one
boundary's sets. If the controller's own boundary choice is wrong, the package
is wrong with it, and nothing here would show that.

---

## Where the other items stand

`D01-F01` is `RESOLVED` on cycle 02's assessment: boundary-limited replay, the
contradiction check, and delayed-origin reproductions refusing without emitting
`LOOP_STATUS`.

`SELF-F02` and `SELF-F03` were supported by cycle 02 and are unchanged since.
`SELF-F03` is `RESOLVED` in the register with cycle 01's two limits attached:
it does not validate the historical improvement figures and is not
frozen-component approval of `gold_runner.py`.

`C02-F08` and `C03-F02` were assessed as demonstrated in cycle 01, which is
external development evidence and does not change BOOTSTRAP-002's terminal
result. Nothing has been written into that run's ledger on the strength of it.

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

One block per finding, in the §4 format, with `Finding ID: D03-F01` and upward.

Where a repair named above is not demonstrated, report it in the recurrence
form against its existing identifier rather than as a new finding. The
implementer-disclosed entries have no cycle identifiers by Alex Zamurko's
ruling; report on them by their register names.

A repair you cannot verify should be reported as unverified rather than given
the benefit of the doubt.

State plainly at the end whether this review converged, and if it makes no such
claim, say that instead.
