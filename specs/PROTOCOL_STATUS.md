# Protocol status

```text
AUTHORITATIVE   YES
confirmed by    Alex Zamurko, 8 September 2026
```

> "Other than that, it is the correct last complete version of the workflow,
> content-wise."

`PROTOCOL_COMMIT` and `PROTOCOL_HASH` below are therefore real values, and Step 0
can be completed rather than approximated for the first A.1-E run.

## Known defect, left uncorrected on instruction

V03's second cell reads `SPEC → CODE → TESTmapping`, with no space before
"mapping". Alex spotted it and ruled: *"I guess, we can leave it like it is."*

It is recorded here rather than fixed, for two reasons.

It is in the source. The docx carries `TESTmapping` in that table cell while both
prose occurrences elsewhere read `SPEC → CODE → TEST mapping`, and the conversion
reproduced the difference exactly. So this is not a conversion artifact, and the
fidelity check did its job: `TEST mapping` and `TESTmapping` are different word
sequences, so a converter that silently inserted the space would have failed.

And correcting it would change `PROTOCOL_HASH`. A one-character edit to an
authoritative governing document is a new version, a new commit and a new hash,
and every run pinning the old value would need re-pinning. Not worth it for a
missing space in a verification-table cell.

## The governing file

`specs/implementation-review-protocol-v1.0.md`

```text
PROTOCOL_HASH  74d7b56124a652525588fbb8548656aad2f7845d9cfea618c9d4136bf1f20a76
               25,177 bytes
source docx    0e0978269667ff9b2e906413b4efba05e2176c83d04b5cf4187d0e400faadee2
               posted in #gap, 8 September 2026
```

Three checks pass, and each has negative controls in
`scripts/test_convert_protocol.py`:

```text
fidelity      word sequence identical, 3,553 words
structure     one output line per source line, no invented headings
completeness  V01-V55 contiguous, 6 fields per row, terminal section present
```

Reproduce with:

```sh
python scripts/convert_protocol.py --docx <source> \
    --out specs/implementation-review-protocol-v1.0.md \
    --terminal "Preservation verdict"
```

## What the checks established, and what Alex's confirmation added

The mechanical checks establish that this file says what its source says. They
could not establish that the source was the document he meant to send, which is
why §0.1's authority needed a human line rather than a passing test. His
confirmation of 8 September supplies exactly that and nothing more.

## Lineage, recorded because it cost a day

Three documents were in play and only this one is right.

```text
(4)   929 paras   V01-V44   no §2.2, no §10.2    older draft, complete
(5)  1011 paras   V01-V21   §2.2 and §10.2       newer, truncated at export
(6)   byte-identical to (5), same sha256 47f7b9c0…
PDF   V01-V55, complete, but the table is positioned glyphs with no
      structure; reconstruction matched 0 of 21 known rows
(10)  879 paras   V01-V55   §2.2 and §10.2       newer AND complete  ← this one
```

The trap was that (4) looked complete and passed every completeness check, being
a tidy document that simply stopped earlier in its own development. Completeness
checking cannot distinguish "complete at V44" from "an older draft that ends at
V44". Only the author can.

The scripts were briefly derived from (5), which was the right lineage but
truncated. Its normative sections are identical to (10)'s, so no re-derivation
was needed when (10) arrived. That was luck rather than design: had (10) changed
a requirement, the scripts would have silently implemented a superseded one. The
51 differences between (5) and (10) in the overlapping region were all cosmetic —
quotation marks around identifiers, `---` separators, list numbering.

## Consistency with the execution layer

`scripts/validate_cycle.py`, `scripts/run_review.py` and
`specs/evidence-schema-v1.0.md` implement this file: fifteen MC-2 checks, and the
§10.1 field names `CANDIDATE_COMMIT`, `CANDIDATE_TREE_HASH`,
`APPROVED_PLAN_HASH`, `DIFF_HASH`, `TEST_RESULT_HASH`. Verified against §10.1,
§10.2 and MC-2 of this exact file.

## Next

```text
done  Alex confirms the markdown says what he wrote
done  PROTOCOL_COMMIT and PROTOCOL_HASH recorded as final
done  finding ledger and loop-state controller
next  bootstrap-review the schema, checker, runner, ledger and loop
      controller with Codex, using specs/prompts/bootstrap-review.md
then  the five production prompts, built and frozen before A1E-001
then  human review package generator, and the Gold runner
last  the first real cycle
```

The bootstrap prompt currently names three artifacts. It needs widening to five
before it is used, since the ledger and loop controller were built after it was
frozen.

Everything built so far is labelled
`BOOTSTRAP / DEVELOPMENT EVIDENCE — NOT_A_PROTOCOL_CYCLE`. No real-cycle
evidence exists and none is contaminated.
