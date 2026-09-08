# Bootstrap review prompt

Frozen for the `BOOTSTRAP_REVIEW` of the execution layer. Hand-written, per Alex
Zamurko, 8 September: a hand-written prompt is acceptable for the bootstrap and
the five production prompts are built and frozen before A1E-001.

This is **not** one of the five. It is used once, on the three components that
had to exist before the protocol could run at all.

---

## What you are reviewing

Three artifacts, hashed and listed in `target.json`:

```text
specs/evidence-schema-v1.0.md   the frozen evidence structure
scripts/validate_cycle.py       the MC-2 conformance gate
scripts/run_review.py           the review runner
```

Their negative-control suites are supplied alongside as evidence that the checks
they contain are falsifiable:

```text
scripts/test_validate_cycle.py
scripts/test_run_review.py
```

## What you are reviewing them against

The protocol at the commit and hash recorded in `target.json`. That file is
authoritative for this review. Where this prompt and the protocol disagree, the
protocol governs and the disagreement is itself a finding.

## The question

Do these three artifacts implement the protocol's Step 2.2, MC-1 and MC-2 as
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

## Deviations already declared

Three are recorded in `specs/evidence-schema-v1.0.md` under "Declared
deviations". They are disclosed here so you assess them rather than rediscover
them:

```text
D-1  a tenth MC-2 check the protocol does not specify: codex-input.md must
     contain the target SHA-256 verbatim
D-2  protocol check 9 is conditional; the implementation makes it
     unconditional
D-3  protocol says "target"; the schema fixes the filename as target.json
```

Assess whether each is sound, whether it is correctly scoped, and whether
declaring it is sufficient or it should be removed. Undeclared deviations you
find are ordinary findings.

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

Out of scope: style, naming beyond D-3, performance, and anything in
`specs/gap/`. The ledger, loop-state controller and the five production prompts
do not exist yet and their absence is not a finding.
