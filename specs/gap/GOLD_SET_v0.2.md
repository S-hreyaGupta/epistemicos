# Gold Set v0.2 — A.1-E gap extraction

```text
SET_STATUS   SINGLE_ANNOTATOR_BASELINE
```

Per Alex Zamurko, 8 September. Not gold under `A1E-AVP-1.2` (D01): the positive
annotation was produced by the author of the specifications, so scoring a system
built from those specifications against it is not independent. D01's regime would
have to be applied for that.

Supersedes `GOLD_SET_v0.1.md` and `GOLD_SET_v0.1_NEGATIVES_DRAFT.md`.

## Source manuscript

Rodríguez, Amaya-Rivas, Samaniego, Luzzini, Merino-Gaibor, "From agroecology to
regenerative supply chain design: A systematic literature review", Journal of
Purchasing and Supply Management, S1478-4092(26)00063-4.

## The pinned text artifact

Every offset below indexes this file and nothing else:

```text
specs/gap/probe/manuscript_gold_v0.2.txt
sha256  dae57720157dd54e420f214f07070da9eebd4dddb42cfc3d57f2aeb3cd54be35
chars   104,761
```

It is produced from `manuscript_normalised.txt` by three rules, in order:

```python
t = re.sub(r"­\s*", "", raw)    # 1. soft hyphen U+00AD and the whitespace after it
t = re.sub(r"-\n\s*", "", t)         # 2. hard hyphen at a line break
t = re.sub(r"\s+", " ", t).strip()   # 3. collapse all whitespace runs
```

Rule 3 is new in v0.2 and it is not cosmetic. Six of the ten spans below,
including four of the six positives, do **not** match verbatim in
`manuscript_normalised.txt` as stored, because the PDF wraps lines inside
sentences and inside table cells. v0.1 recorded offsets into a collapsed text
that was never itself committed, so the artifact in git and the offsets indexing
it were in different spaces. Pinning the collapsed text by hash removes that.

## Correction carried forward from the v0.1 negatives draft

All four negative offsets in that draft were wrong, by 128 to 238 characters:

```text
      draft   correct   drift
N3    27063     26917    -146
N4    52468     52260    -208
N5    74472     74234    -238
N6    33622     33494    -128
```

They were computed against a differently normalised copy and never re-verified
against the committed file. The failure mode is the one this project keeps
meeting: each wrong offset still lands in plausible text. N3's pointed at the
tail of its own sentence, so an inspection would have read as correct.

The six positive offsets were verified against the committed text and are
unchanged.

All ten spans below were confirmed present, exactly once, on 8 September 2026.

## Positives — six tagged gaps

```text
id   §      p   offset   relation / type
G1   §1     1     3246   constrained / unable to capture
G2   §1     1     3488   limited / insufficient
G3   §1     1     3641   missing / absent
G4   §1     2     5623   disconnected / not integrated
G5   §2.1   2    10869   limited / insufficient
G6   §4.5   9    52791   limited / insufficient
```

Quotes and per-case reasoning are unchanged from v0.1 §"Positive cases".

## Negatives

`N1` and `N2` are unchanged from v0.1: attributed future-research gaps in
Table 1, and the §6 future-research paragraph.

`N3` to `N6` are added per Alex Zamurko's ruling of 8 September. They exist
because `BR-CROSS-14` — the deficiency targets the external world or
practitioner capability rather than prior knowledge — carried **zero** coverage
in v0.1. Five of the eight negatives surfaced by the spec-adequacy probe died at
D2 on that rule, and none of them was in the set. An implementation that deleted
`BR-CROSS-14` entirely would have scored 6 of 6.

```text
id   §      offset   expected   discriminating because
N3   §4.1    26917   OTHER      deficiency lexis identical to a real gap
                                ("lack …"); only the target test separates them
N4   §4.5    52260   OTHER      sits 469 chars before G6 in the same subsection,
                                so a detector emitting on proximity trips here
N5   §6      74234   OTHER      "remain nascent" also appears in Table 1 applied
                                to a concept, where the target IS knowledge.
                                Same words, opposite side of D2
N6   §4.3    33494   OTHER      see the HD-09 note below
```

### N3 — §4.1

> The reviewed studies describe this configuration in settings where farmer
> organizations lack consolidation infrastructure or formal market access and
> where intermediaries provide the coordination interface.

```text
D1   deficiency predicated?          yes — "lack consolidation infrastructure"
D2   target                          farmer organizations = practitioner
                                     capability, not prior knowledge → D6m
D6m  importance / urgency asserted?  no — descriptive of reviewed settings
expected                             OTHER
```

### N4 — §4.5

> This approach is more common in developing economies, in which farmers lack
> the consolidation infrastructure, the formalization or organizational forms
> to connect with the market

```text
D2   target   farmers = practitioner capability   → D6m
D6m           neutral description                 → OTHER
```

### N5 — §6

> Policy makers can act as market makers when local organizations remain
> nascent.

```text
D1   deficiency predicated?  "remain nascent", of organizations, not knowledge
D2   target                  world → D6m
D6m                          function is a recommendation to policy makers; not
                             research-assigned, so not FUTURE_RESEARCH under
                             BR-FUT-4
expected                     OTHER
```

### N6 — §4.3, inside Table 3

> Public embeddedness alone may be insufficient to drive deep territorial
> transformation.

Held in v0.1 pending HD-09. HD-09 is now frozen, so it is added.

```text
D1   deficiency predicated?  "may be insufficient"
D2   target                  territorial transformation = world capability → D6m
D6m                          neutral                                       → OTHER
```

## HD-09 — resolved

Frozen by Alex Zamurko, 8 September:

> A table cell is a structural source container, not a semantic class. Text
> within a table cell is eligible to yield zero, one, or multiple proposition
> units under the same proposition-segmentation rules as prose. Table location
> alone neither creates nor excludes a proposition unit. Row/column headers and
> adjacent cells may provide source-grounded context, but must not be silently
> concatenated into the proposition.

Ownership follows:

```text
structural segmentation   pinned segmentation asset
                          paragraphs / list items / table cells
proposition semantics     Step 5
final extraction boundary Step 11, within an already lawful GAP candidate
```

### What N6 does and does not test

N6 is a sound `BR-CROSS-14` negative and belongs in the set on that basis. Its
expected class does not depend on knowing it is in a table: it fails at D2
because the target is world capability.

**It does not currently test HD-09.** The pinned artifact carries no cell
structure. In `manuscript_normalised.txt` a blank line separates table cells and
also separates prose paragraphs, with nothing marking which is which, and rule 3
removes even that. So nothing in the text tells a system it is inside a cell,
which means the rule's operative clauses — row/column headers as context,
adjacent cells not silently concatenated — cannot be exercised against it.

The cell also contains two sentences:

> Farmers remain dependent on external public coordination. Public embeddedness
> alone may be insufficient to drive deep territorial transformation.

Under the frozen rule that is one container yielding two candidate propositions.
N6 quotes the second. A test of HD-09 would have to assert that segmentation,
and it cannot be asserted against a representation with no cells in it.

Testing HD-09 needs the canonical stored text from the conversion path, where a
table survives as a table. That is the same dependency v0.1 recorded for a
different reason, now with a second, independent motivation.

## N7 — held

§5.1. Extraction is corrupted by page furniture injected mid-sentence:

> Our first contribution bridges agroecology—traditionally rooted in **11 J.A.
> Rodríguez et al. Journal of Purchasing and Supply Management xxx (xxxx) xxx**
> coordination infrastructure where producer organizations lack market access

A running header and page number joining two fragments across a page boundary.
The sentence as extracted is not a sentence. Held until the conversion path
supplies text where page furniture is removed upstream.

## Extraction defects, cumulative

```text
1  two-column reading order   pdftotext -layout interleaves columns
2  soft hyphens U+00AD        strip the character AND the whitespace after it
3  page furniture             running headers and page numbers injected between
                              sentence fragments                        (N7)
4  intra-cell line wrapping   sentences inside table cells broken at every
                              wrap; six of ten spans need rule 3        (new)
5  lost table structure       cells and paragraphs share one separator; no
                              row/column headers recoverable            (new)
```

All five are the same shape as the ampersand problem in ingest: the rules are
fine, the bytes reaching them are wrong, and nothing errors.

Defects 3, 4 and 5 are why gold cannot be scored against a local PDF extraction.
`manuscript_gold_v0.2.txt` is a pinned stopgap that makes the offsets
reproducible; it is not a substitute for the conversion path.

## Open dependency

This manuscript is not among the fourteen rows in the corpus and the ingest path
is mid-migration under Stage 1 v9. Either it is ingested first, or the gold
runner takes this pinned artifact by hash and the divergence from what
`papers.markdown` would hold is recorded. Defect 5 means that divergence is
material for HD-09 specifically.

## Not established here

- Whether the six positives are complete. One annotator's sweep, not measured
  recall.
- Whether G1 is a gap this paper fills or only positioning. The annotation says
  positioning; A.1-E has no rule distinguishing them, and the spec-adequacy
  probe reached UNCERTAIN(T3) on it.
- G5 as a restatement of G2/G3 is the annotator's reading, not an
  `A1E-GI-1.0` rule application.
- HD-10 remains unowned. Agreement on the Table 1 items between annotation and
  probe is coincidental: excluded on attribution grounds by one and on G5
  grounds by the other.
