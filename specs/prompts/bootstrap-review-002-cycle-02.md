# Bootstrap review prompt — BOOTSTRAP-002, cycle 02

First cycle of a second `BOOTSTRAP_REVIEW` of the execution layer. Hand-written,
per Alex Zamurko, 8 September: a hand-written prompt is acceptable for the
bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `C01-Fnn`.** The letter is the run, not the
cycle. `B` belongs to BOOTSTRAP-001 and its identifiers are quoted throughout
this document; raising a `B01-Fnn` here would give one name to two defects in
two ledgers.

---

## Why there is a second run at all

BOOTSTRAP-001 closed on 16 September at `MAX_4_REACHED` with five findings
`OPEN`. All five have since been repaired. None has been seen by a reviewer.

§5 gives `RESOLVED` only once a repair is demonstrated in the **next review
target**, and that loop has no next target. So those five cannot close in their
own ledger however thoroughly they are fixed. Alex Zamurko, 16 September:

> Do not close them by human assertion and do not create cycle 05. Start a
> separate, bounded bootstrap-verification run whose purpose is to independently
> demonstrate those five repairs. Cross-reference the original IDs.

That is this run. It is also why nothing here may write into BOOTSTRAP-001's
ledger: this run has its own, and a demonstration recorded here is descriptive
metadata there, never a §5 transition.

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

**1. Are the five repairs demonstrated?** For each, does the current code fix
what the original finding described, and do its controls establish that it does?

**2. Is anything else wrong?** Every file in the target changed after cycle 04
froze, and a good deal changed again on 17 September. None of it has been
reviewed. New defects are ordinary findings.

### What the first run's record suggests about how to spend the time

Across BOOTSTRAP-001, repair claims were examined and rejected at roughly two in
five, in every cycle including the last: 5 of 13, then 9 of 20, then 5 of 11.
**The rate never fell.** That is offered not as a prediction but because a
reviewer expecting claims to hold reads past the ones that do not.

Cycle 04's closing observation was that all five remaining findings shared one
shape: **the control tested the case its repair was built for and missed the
adjacent one.** The check worked when called and was not called from the second
place. The refusal fired on the tested input and a neighbouring input reached
the same state by another route. Mutation testing did not catch it, because
breaking the fix does make those controls fail; they were not asking a wide
enough question.

Six of the twenty-five findings BOOTSTRAP-001 marked `RESOLVED` were never
re-verified. The honest reading is that the resolved set likely contains defects
of this shape too, and it is in scope here.

## The account below is the implementing agent's own

Everything in the repair sections is Claude's description of Claude's work. No
one else has checked it. It is supplied so the cycle is spent on verification
rather than rediscovery, and it should be treated as a claim, not as evidence.

A finding listed as repaired that is not repaired is a finding about this prompt
as much as about the code. BOOTSTRAP-001's cycle 03 raised exactly that, as
B03-F02, about that run's cycle-02 prompt, and was right to.

---

## What you are reviewing

**Ten artifacts**, hashed and listed in `target.json`. That is the gate's whole
covered set, read from `bootstrap_gate.covered()` rather than asserted, and it
is the first time any single frozen target has carried all ten.

`run_pins.py` opens with the rule: *which artifacts govern a run, and which are
under review. Never both.* That is Alex Zamurko's Run-Pin and Review-Target
Separation Specification of 10 September, whose governing invariant is that no
review process may require an artifact to remain byte-invariant for the duration
of a run while simultaneously requiring that same version to change in order to
resolve findings. It was written because BOOTSTRAP-001 required exactly that of
the schema.

Cycle 01 pinned `specs/evidence-schema-v1.0.md` as this run's governing spec and
so could not review it. Its prompt said the remedy in terms: *"Cycle 02 will,
under a pin amendment that moves it between roles, which is what
`pin-amendments.json` and `pins_for_cycle` exist for."* That amendment is now
recorded at `runs/BOOTSTRAP-002/pin-amendments.json`, effective this cycle,
authorised by Alex Zamurko on 25 September. The protocol is now the sole
governing pin and the schema is a review target.

**The schema's current bytes have still been reviewed by nobody.** BOOTSTRAP-001
pinned `98a5920d…`; this run pins `4203ba64…`. It was amended after the first run
froze, and until this cycle no reviewer had seen the version in the tree. Cycle
01 said so, and it is still true, which is why the schema is in this target.

### Cycle 01 was frozen and never run

Its `target.json` and `codex-input.md` were written on 17 September and no
capture was ever taken. It is left in place rather than deleted, because a
frozen cycle with no reviewer output is itself a record of where this stopped.

Nothing in it has been carried forward as evidence. This prompt reproduces its
substance because the material is still the material, not because cycle 01
established any of it. If you see a claim here that cycle 01 is supposed to have
settled, treat it as unestablished: no reviewer has read any of this before you.

One consequence worth stating plainly. A tool in this repository reported cycle
01 as review evidence on 25 September, because it checked that a target had been
frozen and never that a reviewer had been shown it. Freezing a target is a
statement of intent; only the capture is evidence. That mistake was made about
this very cycle, by the implementing agent, hours before this prompt was written.

```text
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
specs/evidence-schema-v1.0.md   what MC-2 checks evidence against. Not code,
                                and covered anyway: a gate that covers the
                                checker but not the document the checker reads
                                its expectations from leaves a seam through the
                                middle of what it claims to cover
```

The gate's covered set is read from `bootstrap_gate.covered()` rather than
asserted from memory. It is ten, all ten are named in this document, and all ten
are in this cycle's target. Six of the ten are declared roots; four —
`authority.py`, `cycle_projection.py`, `findings_format.py` and `run_pins.py` —
are reached through the dependency closure rather than declared, which is why
editing any of them invalidates an approval that never named them directly.

### The control suites are auxiliary evidence, not members of the target

`target_drift` refuses extra target artifacts, and widening the gate's covered
set is a change Alex Zamurko has not made. The five suites are hashed into a
manifest recorded beside the target at freeze; `target.json` records the manifest
digest and `target.sha256` covers that. Their exact versions are identifiable
from this cycle's evidence, but the target hash does not bind their contents
directly.

```text
scripts/test_validate_cycle.py   33 controls
scripts/test_run_review.py       127 controls
scripts/test_ledger.py           87 controls, covering the ledger and controller
scripts/test_bootstrap_gate.py   43 controls
scripts/test_interfaces.py       29 controls, across eleven component seams
```

Those counts total 319, produced by `scripts/refresh_counts.py` and checked by
`scripts/test_prompts.py` against the suites themselves.

**`refresh_counts.py` is not in the covered set and not in this target.** You are
being given a number by a tool you cannot inspect, and the tool has been wrong
three times. It once recorded 29 controls where there were 95, because a suite
crashed part-way and emitted no failure. On 15 September it was found rewriting
the prompts of already-frozen cycles, so one prompt asserted 298 controls for a
review conducted against 263 — and the check that should have caught it compared
the rewritten document against the same suites just written into it. On 17
September it was found resolving a prompt's frozen input by globbing every run,
so a prompt for this run's first cycle would have been declared frozen by
BOOTSTRAP-001's first cycle and never updated.

A count cannot show that the intended refusal is what made a test pass. If a
count supplied from outside the target is not evidence you can use, say so as a
finding.

---

## The five repairs, to verify

Each names its BOOTSTRAP-001 identifier. Those findings remain `OPEN` in that
run's ledger and will stay `OPEN` permanently; what this cycle can establish is
whether the repair holds.

**B01-F02 · the budget could still be extended.** `MAX_4_REACHED` was made
unclearable, and that was not enough: §6 evaluates `STALLED` before the budget,
so a fourth boundary that genuinely stalls never met the unclearable list, and
clearing it returned `CONTINUE` with the ceiling never consulted. The controller
told the operator to open cycle five while the runner refused it. *Repair: the
ceiling is checked on the way out rather than trusting the shape of whichever
exit was cleared.* Commit `76e102b`.

**B01-F07 · the gate checked that fields agreed, not that they were true.** A
target was built whose governing pin named a file that does not exist, with
`"not-a-hash"` as its digest, consistent across both fields. Check 9 passed and
MC-2 returned PASS. *Repair: check 9 replays the run's own pin history for the
cycle and requires the recorded governing set to be the one that history
produced; which pin counts as the protocol comes from what the run declares
rather than from whichever entry matched the field under test.* Commit
`c584e66`. The control that matters is the one where the governing set is well
formed, names the real protocol with its real digest, and is internally
consistent throughout — its only defect is a spec the run never pinned, which
nothing but the run's history can see.

**B01-F11 · a backdated acceptance revived a reopened finding.** Accept at cycle
1, demonstrate at 2, reopen at 3, then append an acceptance dated cycle 2 and
demonstrate at 4. The ledger stored `RESOLVED`. No acceptance ever belonged to
the reopening cycle or later. *Repair: two guards, because refusing to write one
is not refusing to use one. The ledger will not record a disposition dated
before the reopening it answers, and replay will not honour one already in the
history.* Commit `4b36083`.

**B01-F14 · deleting the whole file bypassed the check for the missing field.**
Removing `mc1_enforcement` from `run.json` was refused, exit 2. Removing
`run.json` entirely exited 0 with an unqualified `CONVERGED`, because
classification returned UNKNOWN before the shared metadata check ran. *Repair:
authoritative calculation is refused when run metadata cannot be established at
all, with no labelled fallback, since calling an unreadable run "development
evidence" would be a claim about it.* Commit `c617333`.

**B02-F04 · the atomic commit point was preceded by a destructive write.**
Publication turned on one atomic rename, but recording wrote `capture-log.json`
non-atomically twice during preparation. Truncating it there left the previous
generation on disk with nothing able to say which attempt it was. *Repair: every
write to that file is atomic.* Commit `5201396`.

**The control for B02-F04 is weaker than the others and is marked so.** It reads
the source and requires every write to that file to use the atomic path, rather
than injecting a crash, which a suite driving the runner as a subprocess cannot
do. Alex Zamurko accepted it on 16 September as *structural evidence, not
behavioural fault-injection evidence*, conditional on the atomic primitive
itself having behavioural tests. It had none. Three were added on 17 September,
and within the hour they found that a failed write left its staging file behind.
That is fixed, and the sequence is worth knowing: the structural control said
every write goes through the primitive, which was true and said nothing about
what the primitive does on the way down.

---

## What changed on 16 and 17 September, none of it reviewed

**`SOURCE` on every finding.** Closing B02-F11, open since 10 September: does a
defect the implementing agent finds in its own work enter the ledger? Ruled yes,
with provenance — `CODEX_REVIEW`, `IMPLEMENTER_SELF_FOUND`, `HUMAN_REVIEW` —
persistent identifiers and ordinary lifecycle state, distinguished from reviewer
findings and requiring independent verification before closure like any other.
Required with no default: a default of `CODEX_REVIEW` would mean a defect
recorded without the flag silently claims reviewer provenance. The thirty
BOOTSTRAP-001 findings predate the field and report as `UNRECORDED` rather than
being backfilled.

**`REPAIR_STATUS` beside the state.** `OPEN` currently means two things in
BOOTSTRAP-001's ledger — not repaired, and repaired but undemonstrable there.
This records the difference without touching the three-state vocabulary. Alex
Zamurko's constraint, 17 September: *external demonstration may update
descriptive repair/closure metadata, but must never masquerade as a §5
`RESOLVED` transition in the original ledger*, and neither field may affect
`OPEN_n`, convergence, stall, or cycle counting.

That constraint is under a control which captures the controller's output and
the per-cycle snapshot, writes every non-authoritative field onto the findings,
recomputes both, and fails if either moved by a byte. Another tries
`--status RESOLVED` and requires a refusal. **Whether those two are sufficient
is a fair question for this cycle.**

**The fixture-validity audit**, Alex Zamurko's item C of 16 September: each
negative control should first establish that its fixture satisfies all
prerequisites except the single condition it intends to violate. Two suites had
real gaps.

In the ledger suite, scenarios built fixtures by calling the ledger and ignoring
the result, so a fixture that failed to build was asserted over rather than
reported. All four scenario helpers now require every setup call to succeed.
`scenario_absent` needed it most: it asserts an absence, and an empty fixture
satisfies an absence perfectly, so it was a check that could not come back
false.

In the cycle-validation suite, `expect_fail` asserted the intended check went red
and never asked what else did. It now requires that check to be the only failure
unless the cascade is declared.

**The audit was not exhaustive and this prompt does not claim it was.** The
runner suite is 127 controls and was sampled, not audited. The gate and interface
suites were found already conformant. If the sampling is not good enough to rest
an approval on, that is a finding.

### One pattern found three times in a day, and probably not three times in total

Creating a second run broke three rules that had been correct for as long as
there was exactly one. None of them errored; each quietly answered a different
question from the one it appeared to answer.

```text
refresh_counts.frozen_input   resolved a prompt's frozen input by globbing every
                              run, so a prompt for this cycle would have been
                              declared frozen by BOOTSTRAP-001's cycle 01 and
                              never given today's counts

test_prompts, finding-ID      hardcoded the prefix letter as B, so a prompt using
                              the letter its own run raises under would have
                              failed a check meant to confirm it used the right
                              one

test_prompts, covered set     took "current prompt" to be the highest cycle
                              number, so this prompt was written, the check ran
                              green, and what it had graded was a prompt frozen
                              the day before
```

The third was found by reading the output of a green run rather than by any
control failing, which is the only reason it is in this list instead of still
being true.

These are all in tooling outside the target, so they are not findings against the
reviewed set. They are offered because the same substitution — one run, one
cycle numbering, one ledger — is made in places that *are* in the target, and
three for three is a poor rate to stop looking at.

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

One block per finding, in the §4 format, with `Finding ID: C01-F01` and upward.

Where a finding concerns one of the five repairs above, name the BOOTSTRAP-001
identifier in the evidence so the two records can be joined. A repair you cannot
verify should be reported as unverified rather than given the benefit of the
doubt.

State plainly at the end whether this review converged, and if it makes no such
claim, say that instead. Every cycle of BOOTSTRAP-001 ended by saying it made no
claim of convergence, and each time that was the accurate thing to say.
