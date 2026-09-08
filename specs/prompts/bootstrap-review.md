# Bootstrap review prompt

Frozen for the `BOOTSTRAP_REVIEW` of the execution layer. Hand-written, per Alex
Zamurko, 8 September: a hand-written prompt is acceptable for the bootstrap and
the five production prompts are built and frozen before A1E-001.

This is **not** one of the five. It is used once, on the components that had to
exist before the protocol could run at all.

Revised 8 September, before use. The first version named three artifacts; the
ledger and loop controller were built after it was written, so it was frozen a
step too early and describing it as frozen was premature. Nothing was reviewed
against the earlier text.

---

## What you are reviewing

Five artifacts, hashed and listed in `target.json`:

```text
specs/evidence-schema-v1.0.md   the frozen evidence structure
scripts/validate_cycle.py       the MC-2 conformance gate, fifteen checks
scripts/run_review.py           the review runner
scripts/ledger.py               the finding and state ledger
scripts/loop_state.py           the loop-state controller
```

Their negative-control suites are supplied alongside as evidence that the checks
they contain are falsifiable:

```text
scripts/test_validate_cycle.py   24 controls
scripts/test_run_review.py       21 controls
scripts/test_ledger.py           25 controls, covering both of the last two
```

## What you are reviewing them against

The protocol at the commit and hash recorded in `target.json`. That file is
authoritative for this review. Where this prompt and the protocol disagree, the
protocol governs and the disagreement is itself a finding.

## The question

Do these five artifacts implement §2.2, §5, §6, §10.1, §10.2, MC-1 and MC-2 as
written, and do their controls actually establish what they claim?

Two failure modes matter more than the rest.

**A check that cannot come back false.** The v1.0 gate-hardening milestone found
thirteen of these. A check whose failure branch is unreachable reports success
while testing nothing. For every check in `validate_cycle.py` and every refusal
in `run_review.py`, ask whether the supplied controls demonstrate it firing, or
whether the control merely exercises the same code path under a different name.
Checks 1 to 4 are one mechanism, file existence, and only check 4 is
demonstrated; that specific weakness is already known and does not need
reporting, but comparable cases elsewhere do.

**A claim stronger than its evidence.** `MC1_ENFORCEMENT` is
`CONVENTION_ONLY` on this environment. Flag any language in the schema, the
scripts or their documentation that implies technical protection, immutability,
or a proven binding between reviewer input and reviewer output.

## Decisions already declared

The protocol underdetermines these, and each was resolved to build at all. They
are disclosed so you assess them rather than rediscover them. Undeclared
deviations you find are ordinary findings.

```text
A  target is instantiated on disk as target.json, and DIFF_HASH and
   TEST_RESULT_HASH are paired with diff_path and test_result_path so
   checks 14 and 15 have an artifact to hash. Ruled a schema-level
   concretisation, not a protocol change. See evidence-schema-v1.0.md.

B  candidate_tree_hash is derived by the runner from candidate_commit and
   never supplied by the operator. A hand-typed tree hash can be typed to
   match whatever was recorded.

C  Checks 11 to 15 report N/A on a plan cycle, never PASS. §10.2 scopes them
   to implementation review, and reporting PASS for a check that was never
   evaluated is the defect this gate exists to catch.

D  ACCEPT records a disposition and leaves the finding OPEN. §5 gives
   RESOLVED only "once the repair is demonstrated in the next review
   target", so ledger.py refuses to resolve in the same cycle as the
   acceptance. The protocol does not say who declares a repair demonstrated;
   `resolve` requires an evidence string rather than inventing an answer.

E  DISPUTED is terminal in the automated loop. §5 and §7.1 place adjudication
   at the human gate, so nothing here moves a finding out of it.

F  Check 13 compares approved_plan_hash against
   plan-approval/approval.json, where §7.3 freezes it. Absent that record the
   check fails rather than passing vacuously.

G  loop_state.py runs the MC-2 gate itself rather than reading a recorded
   verdict, so §6's n indexes VALID cycles and events recorded in an invalid
   cycle are ignored entirely, including resolutions. This is the
   conservative reading: it can delay an exit, never manufacture one.
```

D and G are the two most worth arguing with. D decides when a finding stops
being open, and G decides what counts as a cycle at all.

## Output format

Use only this closed vocabulary:

```text
MISSING REQUIREMENT
WRONG OWNERSHIP
NONDETERMINISTIC WHERE D POSSIBLE
SEMANTIC STEP TOO BROAD
UNTESTED RULE
CONTRADICTORY IMPLEMENTATION MAPPING
```

One block per finding, persistent identifier, cycle 01:

```text
Finding ID: B01-F01
Class:
Artifact:
Location:
Evidence:
Finding:
Required correction:
```

Quote the `TARGET_SHA256` from the top of this input in your first line, so the
response is bound to the exact artifacts you were shown.

If you find nothing in a category, say so explicitly rather than omitting it.
An empty review is a finding about the review, not about the code.

## Scope limits

Out of scope: style, performance, and anything in `specs/gap/`. Naming is out of
scope except where decision A is wrong.

Not yet built, so their absence is not a finding: the five production prompts,
the human review package generator (§7), and the Gold runner (§15). The
implementing agent has not written a plan or an implementation yet, so there is
no A1E-001 evidence to review; this is the tooling only.
