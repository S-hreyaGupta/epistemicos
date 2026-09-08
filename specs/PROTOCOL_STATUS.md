# Protocol status

Read this before treating anything in `specs/` as the governing protocol.

```text
AUTHORITATIVE   NO
```

## What is in git right now

`specs/implementation-review-protocol-v1.0.md`, committed at `8fcb181`, hash
`06285a4d74b9b86d9cafb1fd28ce8aa168720aa8d87618df66473fa884ee665e`.

It is a faithful, checked conversion of **Document (4)**. Fidelity, structure and
completeness all pass on it, and the checks are reproducible with:

```sh
python scripts/convert_protocol.py --docx <Document (4)> \
    --out <path> --terminal "Preservation verdict" --dry-run
```

## Why that file does not govern

Document (4) is the **older** draft. Measured against Document (5) — and (6),
which is byte-identical to (5), `47f7b9c0768c83fba5b7074fa6ed83d70edce3533bb02e2de18711d6b8188c8e`:

```text
41 regions differ; 457 of ~600 paragraphs identical
20 of the 21 overlapping V-rows are reworded in the newer draft

§2.2  Review runner composes the Codex input   newer only, ABSENT from (4)
§10.2 Implementation-specific MC-2 checks      newer only, ABSENT from (4)
      checks 11-15: candidate commit, tree hash, approved-plan hash,
      diff hash, test-result hash. Mandatory, not conditional.
```

So MC-2 has **fifteen** checks, not the nine Document (4) records.

## Why the newer draft is not in git either

Documents (5) and (6) are truncated at export. `word/document.xml` ends mid-word
at `V2` after V21; no V22 appears in any part of the container, so nothing
recovers it. The completeness check fails them and `convert_protocol.py`
therefore refuses to write them, which is the correct behaviour.

The missing portion is the last 23 of 631 paragraphs: the verification table from
V22 onward, the preservation verdict and the control chain. The entire normative
workflow survives — sections 0 to 16, MC-1, MC-2 with all fifteen checks, §2.2,
§10.2, and the summary chain through FINAL FREEZE / RELEASE.

That distinction is why work continued. The missing tail is an audit record
*about* the protocol, not a specification of behaviour. Nothing the checker needs
is absent.

## What the scripts are built against

`scripts/validate_cycle.py`, `scripts/run_review.py` and
`specs/evidence-schema-v1.0.md` are derived from the **newer** draft: fifteen
checks, and the §10.1 field names `CANDIDATE_COMMIT`, `CANDIDATE_TREE_HASH`,
`APPROVED_PLAN_HASH`, `DIFF_HASH`, `TEST_RESULT_HASH`.

They therefore implement a protocol version that is **not the file committed at
`8fcb181`**. That inconsistency is deliberate and recorded here rather than left
for someone to discover. It resolves when the complete newer source arrives.

## To clear this

1. Obtain the newer draft complete: V22 to the end, preservation verdict,
   control chain. Requested as pasted text rather than a re-export, since the
   export path is where the cut occurs.
2. Convert it. All three checks must pass with no `--dry-run`.
3. Commit, and record `PROTOCOL_COMMIT` and `PROTOCOL_HASH` here.
4. Re-verify the schema and scripts against that exact file.
5. Bootstrap-review all three with Codex, using
   `specs/prompts/bootstrap-review.md`.
6. Only then may a real cycle begin.

Everything produced so far is labelled
`BOOTSTRAP / DEVELOPMENT EVIDENCE — NOT_A_PROTOCOL_CYCLE`. No real-cycle
evidence exists and none is contaminated.
