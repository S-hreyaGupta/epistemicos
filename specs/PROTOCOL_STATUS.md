# Protocol status

```text
AUTHORITATIVE   pending one confirmation from Alex Zamurko
```

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

## What is still outstanding

§0.1 makes the git artifact authoritative, but a conversion nobody confirmed is
the "which copy are you reading" problem inside the document written to prevent
it. The mechanical checks establish that this file says what its source says.
They cannot establish that the source is the document Alex meant to send.

One line from him closes it, and then `PROTOCOL_COMMIT` and `PROTOCOL_HASH` are
real values for the first A.1-E run.

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

1. Alex confirms the markdown says what he wrote.
2. Record `PROTOCOL_COMMIT` and `PROTOCOL_HASH` above as final.
3. Bootstrap-review the schema, checker and runner with Codex, using
   `specs/prompts/bootstrap-review.md`.
4. Build the ledger, loop controller and five production prompts.
5. Only then may a real cycle begin.

Everything built so far is labelled
`BOOTSTRAP / DEVELOPMENT EVIDENCE — NOT_A_PROTOCOL_CYCLE`. No real-cycle
evidence exists and none is contaminated.
