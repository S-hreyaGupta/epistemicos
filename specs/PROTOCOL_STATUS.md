# Protocol status

```text
VERSION         v1.1
AUTHORITATIVE   pending one confirmation from Alex Zamurko
```

v1.0 was confirmed authoritative on 8 September: *"it is the correct last
complete version of the workflow, content-wise."* v1.1 adds one exit and needs
the same one-line confirmation before it governs.

## The governing file

`specs/implementation-review-protocol-v1.1.md`

```text
PROTOCOL_HASH  296594a3c06cd2f9c66976c369b15804f39bbb2be37b5e62234d37fafd28d483
source docx    7cdb3a96666f254050a4173a0fdf56ae7972852eea348797315e378283fffd64
as converted   e6c42a1f918e304519977ece3a4c1b567423d2235c0be63b9ad0a8b4c3641c5f
               plus one declared amendment, below

superseded     specs/implementation-review-protocol-v1.0.md
               74d7b56124a652525588fbb8548656aad2f7845d9cfea618c9d4136bf1f20a76
               retained rather than overwritten; no run referenced it
```

Three checks pass, each with negative controls in
`scripts/test_convert_protocol.py`:

```text
fidelity      word sequence identical, 3,711 words
structure     one output line per source line, no invented headings
completeness  V01-V56 contiguous, 6 fields per row, terminal section present
```

Reproduce with:

```sh
python scripts/convert_protocol.py --docx <source> \
    --out specs/implementation-review-protocol-v1.1.md \
    --terminal "Preservation verdict"
```

Reconverting the v1.0 source with the current converter still yields
`74d7b561…`, so the soft-line-break fix below changed nothing about documents
that do not contain soft breaks.

## Amendment, and how it stays checkable

§0.1's "Recommended location" named `...-v1.0.md`, the superseded filename, so
the governing document pointed at a document it had replaced. Alex ruled on
8 September that this is operational metadata rather than an inert typo and must
be fixed rather than recorded: it creates exactly the which-copy-are-you-reading
ambiguity §0.1 exists to remove.

```diff
 Recommended location:
-specs/implementation-review-protocol-v1.0.md
+specs/implementation-review-protocol-v1.1.md
```

§0.1 makes the git artifact authoritative rather than the docx, so amending the
markdown is legitimate. It costs something though: the file is no longer a
byte-faithful conversion, so `convert_protocol.py` can no longer establish that
nothing *else* changed in the same edit, and "I only changed one line" becomes an
assertion.

`scripts/verify_amendment.py` restores the check. It reconverts the docx, applies
each declared amendment, and requires the result to be byte-identical to the
committed file:

```sh
python scripts/verify_amendment.py --docx <rev2 docx>
```

An undeclared edit fails it. Demonstrated by softening "Stop the automated plan
loop immediately" to "Stop the automated plan loop" in the STALLED text: the
verifier failed and named that line.

## What v1.1 changes

One exit, in both loops. V56 records it.

```text
Exit A  CONVERGED                     OPEN_n = 0 and DISPUTED_n = 0
Exit B  HUMAN_ADJUDICATION_REQUIRED   OPEN_n = 0 and DISPUTED_n != 0
Exit C  STALLED                       unchanged
Exit D  MAX_4_REACHED                 renumbered from C
```

The order is load-bearing, and both wrong answers were demonstrated on fixtures
before the rule was written. Under v1.0 the cycle a dispute landed in returned
CONTINUE, telling the implementing agent to repair a plan with nothing open to
repair and spending one of four cycles doing it. The cycle after returned
STALLED, which mislabels a loop that finished everything automation could do.

An invalid cycle cannot count toward `HUMAN_ADJUDICATION_REQUIRED` either;
v1.1 adds it to the MC-2 invalid-cycle list.

## Converter change made for this version

The v1.1 docx carries a soft line break inside one paragraph, in the preservation
verdict. `python-docx` returns those as `\n` within a single paragraph's text,
and the structure check counted one source line against several output lines.

A soft break is a line break the author typed, so `source_lines` now splits on
it and both sides count consistently. Verified by reconverting the v1.0 source to
its identical committed hash.

## Known defect, left uncorrected on instruction

V03's second cell reads `SPEC → CODE → TESTmapping`, no space before "mapping".
Alex ruled: *"I guess, we can leave it like it is."*

It is in the source rather than introduced by the conversion: the docx carries
`TESTmapping` in that cell while both prose occurrences elsewhere read
`SPEC → CODE → TEST mapping`, and the conversion reproduced the difference
exactly. The fidelity check would have failed a converter that silently inserted
the space, since those are different word sequences.

Correcting it would change `PROTOCOL_HASH`, which is a new version, a new commit
and a re-pin of every run referencing the old value. Not worth it for a missing
space in a table cell.

## Consistency with the execution layer

These implement this exact file:

```text
specs/evidence-schema-v1.0.md   fifteen MC-2 checks, §10.1 field names
scripts/validate_cycle.py       24 controls
scripts/run_review.py           21 controls
scripts/ledger.py               OPEN / RESOLVED / DISPUTED per §5, §6
scripts/loop_state.py           four exits, in the v1.1 order
scripts/test_ledger.py          29 controls across both
scripts/test_interfaces.py      six seams
specs/prompts/01..05            the five production prompts, §1 §4 §5 §8 §9 §11
scripts/test_prompts.py         vocabulary read from the protocol, not restated
```

## Lineage, recorded because it cost a day

```text
(4)   929 paras   V01-V44   no §2.2, no §10.2    older draft, complete
(5)  1011 paras   V01-V21   §2.2 and §10.2       newer, truncated at export
(6)   byte-identical to (5), sha256 47f7b9c0…
PDF   V01-V55 complete, but the table is positioned glyphs with no structure;
      reconstruction matched 0 of 21 known rows
(10)  V01-V55   newer AND complete                v1.0
rev2  V01-V56   adds HUMAN_ADJUDICATION_REQUIRED  v1.1
```

The trap was that (4) looked complete and passed every completeness check, being
a tidy document that simply stopped earlier in its own development. Completeness
checking cannot distinguish "complete at V44" from "an older draft that ends at
V44". Only the author can.

## Next

```text
done  v1.0 confirmed; v1.1 converted and checked
done  ledger, loop controller, interface tests, five production prompts
now   Alex confirms v1.1 says what he wrote
then  bootstrap-review the five components with Codex, using
      specs/prompts/bootstrap-review.md
then  human review package generator (§7), and the Gold runner (§15)
last  the first real cycle
```

Everything built so far is labelled
`BOOTSTRAP / DEVELOPMENT EVIDENCE — NOT_A_PROTOCOL_CYCLE`. No real-cycle
evidence exists and none is contaminated.
