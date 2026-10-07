# Bootstrap review prompt — BOOTSTRAP-003, cycle 01

First cycle of a third `BOOTSTRAP_REVIEW` of the execution layer. Hand-written,
per Alex Zamurko, 8 September: a hand-written prompt is acceptable for the
bootstrap. This is not one of the five production prompts.

**Findings from this cycle are `D01-Fnn`.**

Each run has its own prefix letter so that two runs cannot raise findings under
one name: `B` for BOOTSTRAP-001, `C` for BOOTSTRAP-002, `D` for this one. The
ledger would accept a repeated identifier, since it checks only that the digits
match the cycle; the letters exist because identifiers are quoted in handovers
and messages where nothing carries the run beside them.

An earlier draft of this prompt said `C01-Fnn` and proposed writing the run in
front of every identifier instead. `test_prompts.py` refused it, correctly: the
convention already existed and I was about to invent a second one. Earlier
findings are referred to below by their own identifiers, `C02-F08` and
`C03-F02`, which are BOOTSTRAP-002's and are unambiguous because of the letter.

---

## Why there is a third run rather than a fifth cycle

BOOTSTRAP-002 ended at `MAX_4_REACHED` with two findings open: `C02-F08` and
`C03-F02`. That result is recorded and is not being revisited. §6's budget is
spent for that run, so the repairs made since cannot be demonstrated inside it,
and appending a fifth cycle to a loop that has already exited would rewrite a
terminal boundary after the fact.

Alex Zamurko, 6 October 2026: "Lets use the 5th one." A new run is how that is
done without disturbing the old record.

**This is development evidence, not a protocol outcome.** `BOOTSTRAP-003` is
marked `NOT_A_PROTOCOL_CYCLE`, the bootstrap gate still reports no approved
bootstrap review on record, and the controller refuses to state an authoritative
loop result for it.

**Nothing here is technically enforced.** `MC1_ENFORCEMENT` is
`CONVENTION_ONLY`. Every check in this layer is detection that holds while the
checks run faithfully and nobody edits the records they read. The same writable
code performs the checks on itself.

---

## What this cycle is for

**1. Are BOOTSTRAP-002's two open findings repaired?** `C02-F08` and `C03-F02`.
For each, does the current code fix what the finding described, and do its
controls establish that it does.

**2. Three defects I disclosed myself.** Alex Zamurko ruled on 6 October that
defects found by the implementing agent are tracked in a register of their own,
never given cycle-generated identifiers, and "require the next independent
review to assess it explicitly". That is this review. They are `SELF-F01`,
`SELF-F02` and `SELF-F03` in `registers/implementer-disclosed.json`.

**3. Do the earlier repairs still hold?** Nineteen findings are `RESOLVED` in
BOOTSTRAP-002. Three of the eleven covered files have changed since that run's
last target, so a repair demonstrated there was demonstrated against code that
has since moved.

**4. Is anything else wrong?** The whole target is in scope.

---

## The account below is the implementing agent's own

I wrote the repairs and I wrote these notes. Everything in the
finding-by-finding section is my claim about my own work, offered to be tested
rather than adopted. What is not my claim is listed under auxiliary evidence:
the control sources are preserved and their run is recorded.

---

## What you are reviewing

**Eleven files**, the same set BOOTSTRAP-002 cycle 04 reviewed, and the same
list the gate covers:

```text
specs/covered-components.json     scripts/ledger.py
specs/evidence-schema-v1.0.md     scripts/loop_state.py
scripts/authority.py              scripts/run_pins.py
scripts/bootstrap_gate.py         scripts/run_review.py
scripts/cycle_projection.py       scripts/validate_cycle.py
scripts/findings_format.py
```

Three have changed since cycle 04's target, compared digest by digest:
`bootstrap_gate.py`, `run_pins.py` and `validate_cycle.py`. The other eight are
byte-identical to what that cycle saw. The changed three are exactly the two
repairs below and nothing else.

### The control suites, preserved and run

```text
scripts/test_bootstrap_gate.py    53 controls
scripts/test_interfaces.py        29 controls, across eleven component seams
scripts/test_ledger.py           122 controls
scripts/test_run_review.py       155 controls
scripts/test_validate_cycle.py    54 controls
```

413 in total, up from 404 at cycle 04. They are produced by
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

**Every suite passes.** `test_approval_package.py` was named as known-red in all
four BOOTSTRAP-002 freezes; it is green now, for the reason set out under
`SELF-F01` below, and this is the first freeze in either run with no declared
exemption.

### The mutation probe, and what it does not establish

`_probe/mutate_repairs.py` removes each repair from the real source one at a
time and requires its suite to go red, with a failure naming something specific
to that repair.

**The probe's result is my assertion, and this time it is weaker than usual.**
Its source is preserved so you can read it; it is not run at freeze, because a
full run takes twenty-odd minutes. You have the instrument and not the run.

Worse than that here: the last run covering the whole set was on 6 October and
caught every line it then held. A line was added after it, for the hunk-body
half of `C02-F08`, and that line has only been exercised in a filtered run of
its own finding. A filtered run establishes nothing about the lines it skipped.
A full run was started before this freeze and was abandoned unfinished, so
nothing from it is claimed either.

Two things it has caught are worth naming, because neither is visible to a green
suite. It has repeatedly found controls of mine passing for a reason other than
the one they are named for, most often where a stronger check had silently taken
over answering for a weaker one. And it has twice found its own lines too weak
to reopen the hole they claimed to test, so a line was reporting a catch it had
not made. Both kinds are recorded in the source at the point they happened,
rather than counted here.

---

## BOOTSTRAP-002's two open findings, and what was done about each

**`C02-F08` · the preserved patch need not describe its own change.** Cycle 04 found three ways past the previous repair: correct `index`
headers over altered hunks or paths, a set comparison hiding an omitted entry
when another entry shares the same blob pair, and an empty expected change set
bypassing comparison entirely.

Alex Zamurko ruled on 5 October: generate the patch from the recorded base and
candidate, compare it with the preserved patch byte for byte, reject on paths,
modes, hunks, file entries or repeated changes, and do not skip validation when
the change set is empty.

Check 14 now regenerates the patch with the same pinned diff flags the freeze
used and requires the preserved bytes to equal it. The header comparison
remains, demoted from a rule to an explanation: it says whether a difference is
a different change or the same files with different contents, and it never
refuses on its own. Five controls: a substituted patch, a wrong path with
correct `index` lines, an omitted file among two sharing a blob pair, a nonempty
patch against an empty change set, and an altered hunk body under correct
headers.

What this does not establish: that the hunks apply. Byte equality with a
regenerated patch is as far as a gate without a working tree can go, and a
different git version formatting a patch differently would refuse a cycle that
is otherwise sound. The refusal message says so.

**`C03-F02` · a failed provenance query read as permission.**
Cycle 04 found that an ignored, untracked approval file satisfied
`authority.require_approval` while producing empty porcelain status output, and
that failure to establish provenance was treated as permission.

The gate now reads the approval's bytes out of the committed tree and compares
them with the file it is about to consume, and a git query that fails refuses
rather than returning. Four controls: an approval that is untracked and ignored,
one staged but never committed, a repository whose record cannot be read at all,
and the positive case of a committed approval for a committed scope.

---

## The three implementer-disclosed defects

Not reviewer findings, no cycle identifiers, and in the register rather than the
ledger. Alex Zamurko's instruction is that this review assess them explicitly,
so each is stated with what I claim and where to check it.

**`SELF-F01` · an approval package could present silence as no findings.** With
frozen cycles and no ledger, the package was produced with empty findings
headings. The generator now refuses with `FINDINGS_STATE: CANNOT_ESTABLISH` when
frozen cycles exist and the ledger is missing, unreadable or unparseable.
`approval_package.py` is not a covered component and is not in this target; the
entry is here because the ruling says it must be assessed, not because the file
is under review.

**`SELF-F02` · a killed probe left a disabled check in tracked source.** The
restore runs in a `finally`, which does not survive the process being killed,
and closing a terminal window on 5 October left `if False:` in `loop_state.py`
until the next run refused to start. The probe now records the mutation on disk
before applying it and the next run restores it from HEAD, refusing instead if
HEAD or the file has moved.

**`SELF-F03` · the gold runner scored its two sides by different rules.** A
candidate work may match a gold item under any phrasing the manuscript used for
it, and that remapping ran over the candidate only; the baseline never received
it. Every before-and-after figure it produced therefore favoured the candidate.
Found because one file scored 93/98 as a baseline and 96/98 as a candidate in
the same run. `gold_runner.py` belongs to the citation product and is not in
this target either.

The register's own claim is worth testing: that none of the three can produce a
false green in this layer. `SELF-F03` in particular means figures quoted in
`citation_extract.py` for earlier work were measured with the defect. They have
not been restated.

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

One block per finding, in the §4 format, with `Finding ID: D01-F01` and upward.

Where a repair named above is not demonstrated, report it in the recurrence form
against its existing identifier, `C02-F08` or `C03-F02`, rather than as a new
finding, so it reopens instead of acquiring a second name.

A repair you cannot verify should be reported as unverified rather than given
the benefit of the doubt. The preserved suites are there so that "unverified"
can be narrowed to a specific thing you looked at and could not establish.

State plainly at the end whether this review converged, and if it makes no such
claim, say that instead. Every cycle of BOOTSTRAP-001 ended by saying it made no
claim of convergence, and each time that was the accurate thing to say.
