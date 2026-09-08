# Review evidence schema v1.0

Frozen structure for review-cycle evidence under
`specs/implementation-review-protocol-v1.0.md`.

MC-2 checks evidence against this schema. The schema must therefore be frozen
before any cycle is written, because a checker cannot validate a structure that
is still moving.

## Status of this document

```text
MC1_ENFORCEMENT   CONVENTION_ONLY
```

Decided before Run 1 rather than discovered during it. The implementing agent
and the review evidence share one effective write authority on the current
single-user Windows environment, so a technical immutability claim is not
supportable. Per MC-1, claims that Codex findings are immutable or that review
input is technically protected **must not be made** while this holds.

Upgrade to `TECHNICALLY_ENFORCED` only when authoritative review evidence sits
behind a write boundary the implementing agent does not have.

## Directory layout

```text
runs/
  A1E-001/
    run.json
    baseline/
    plan-review/
      cycle-01/
        target.json
        target.sha256
        codex-input.md
        codex-output-raw.md
        findings.json          written by the runner
        claude-response.md     written by the implementing agent
      cycle-02/
        ...
    plan-approval/
    implementation-review/
      cycle-01/
        ...
    code-approval/
    gold/
```

Cycle directories are `cycle-NN`, zero-padded, starting at `01`. The number is
the cycle identifier and must be unique within its review directory.

## `target.json`

The frozen artifact identity for one cycle. Hashed as a file; that hash is what
binds the cycle together.

Common fields, both review types:

```json
{
  "review_type": "plan" | "implementation",
  "run_id": "A1E-001",
  "cycle": 1,
  "protocol_commit": "ef0565b…",
  "protocol_sha256": "21d1b59a…",
  "spec_sha256": "…",
  "frozen_at": "2026-09-08T13:40:00Z"
}
```

Plan review adds:

```json
{
  "plan_files": [
    { "path": "runs/A1E-001/plan/01-PLAN.md", "sha256": "…" }
  ]
}
```

Implementation review adds — all five mandatory, per MC-2 check 9:

```json
{
  "commit": "…",
  "tree": "…",
  "approved_plan_sha256": "…",
  "diff":         { "path": "…", "sha256": "…" },
  "test_results": { "path": "…", "sha256": "…" }
}
```

## `target.sha256`

One line: the lowercase hex SHA-256 of `target.json`, nothing else.

## `codex-input.md`

Composed by the review runner, never by the implementing agent. Must contain the
`target.sha256` value verbatim somewhere in its text. That string is the binding
between what was frozen and what the reviewer was actually shown.

Freezing the target proves the artifact did not change. Only the embedded hash
ties that artifact to the input the reviewer received. This is the control whose
absence made the GSD pilot's criterion 1 unprovable.

## `codex-output-raw.md`

Exactly what Codex returned, captured before any parsing, summarisation or
response. No repair may occur before this file exists.

## Declared deviations from the protocol

The protocol's MC-2 specifies nine checks. `scripts/validate_cycle.py` implements
ten, and two of the nine more strictly than written. These were introduced while
building against the truncated source and are recorded here as deviations
awaiting a decision, not as settled design.

```text
D-1  a tenth check, not in the protocol
     codex-input.md must contain the target SHA-256 verbatim.
     Rationale: freezing the target proves the artifact did not change, but
     only the embedded hash ties that artifact to the input the reviewer
     received. Its absence is what made the GSD pilot's criterion 1
     unprovable. This is an addition to a frozen protocol and needs
     ratifying or removing.

D-2  check 9 made unconditional
     Protocol: "where target references additional hashed artifacts:
     recorded hashes match those artifacts" — a conditional. The checker
     requires plan_files for plan review, and commit, tree,
     approved_plan_sha256, diff and test_results for implementation review.
     A cycle omitting them fails rather than passing vacuously.
     Rationale: as written, an implementation review target carrying no
     artifacts at all satisfies check 9. That is a check that cannot come
     back false.

D-3  target named target.json
     Protocol says "target". The schema fixes the filename and the format.
     Cosmetic, but it is a choice the protocol did not make.
```

D-1 and D-2 both make the gate stricter, so no cycle that passes the protocol as
written would fail here for the wrong reason. That is not a justification for
making them silently. Until they are ratified, `MC2_CONFORMANCE: PASS` means
conformance to this schema, not to the protocol text.

## What MC-2 does not check

Stated so nobody reads a PASS as more than it is.

- That `codex-output-raw.md` came from the invocation `codex-input.md` describes.
  Nothing in the evidence proves that binding; it rests on the runner behaving.
- That the reviewer read the whole input.
- That findings in `findings.json` correspond to the raw output. A separate check
  could compare finding IDs against the raw text; it is not in the ten.
- Anything about content quality. MC-2 is an evidence-completeness gate.

Under `CONVENTION_ONLY` these gaps are procedural, not technical, and the
protocol's language must reflect that.

## Bootstrap exception

Per Alex Zamurko, 8 September. The runner and this checker necessarily precede
the automated protocol they enable, so artifacts produced before both exist and
have passed bootstrap review are:

```text
BOOTSTRAP / DEVELOPMENT EVIDENCE — NOT_A_PROTOCOL_CYCLE
```

They are not invalid cycles requiring retrospective interpretation. They are not
cycles. No `A1E-001` protocol cycle may be created until the evidence schema is
frozen and the MC-2 checker exists and has passed its own bootstrap review.
