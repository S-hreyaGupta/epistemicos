# Gold Set v0.1 — proposed world/capability negatives

**Draft for Alex's review. Not part of the frozen gold set until adjudicated.**

## Why these

The spec-adequacy probe surfaced fourteen candidate units. Eight were negatives,
and **five of those eight died at D2 on `BR-CROSS-14`** — the deficiency targets
the external world or practitioner capability rather than prior knowledge.

None of the five appears in Gold Set v0.1, because the annotation never treated
them as candidates. So the rule carrying most of A.1-E's precision on this
manuscript has zero gold coverage, and an implementation that dropped
`BR-CROSS-14` entirely would still score 6/6 on the current set.

These are proposed as negatives to close that.

---

## N3 — §4.1, char 27063 — CLEAN

> The reviewed studies describe this configuration in settings where farmer
> organizations lack consolidation infrastructure or formal market access and
> where intermediaries provide the coordination interface.

```text
D1  deficiency predicated?        yes — "lack consolidation infrastructure"
D2  target                         farmer organizations = practitioner
                                   capability, not prior knowledge
                                   → D6m mattering test
D6m importance / urgency asserted? no — descriptive of reviewed settings
expected                           OTHER
```

Discriminating because the deficiency lexis is identical to a real gap
("lack …"), and only the target test separates them.

## N4 — §4.5, char 52468 — CLEAN

> This approach is more common in developing economies, in which farmers lack
> the consolidation infrastructure, the formalization or organizational forms to
> connect with the market

```text
D2  target    farmers = practitioner capability   → D6m
D6m           neutral description                 → OTHER
expected      OTHER
```

Sits 469 characters before G6 in the same subsection, so a detector that emits on
proximity to a real gap will trip here.

## N5 — §6, char 74472 — CLEAN

> Policy makers can act as market makers when local organizations remain
> nascent.

```text
D1  deficiency predicated?  "remain nascent" — of organizations, not knowledge
D2  target                   world → D6m
D6m                          the unit's function is a recommendation to policy
                             makers; not research-assigned, so not
                             FUTURE_RESEARCH under BR-FUT-4
expected                     OTHER
```

Useful because "nascent" also appears in Table 1 applied to a *concept*
("Regeneration remains a nascent concept in business"), where the target is a
knowledge structure. Same word, opposite side of D2.

---

## Two I would not add as-is, and why

### N6 candidate — §4.3, char 33622 — inside a table

> Public embeddedness alone may be insufficient to drive deep territorial
> transformation.

Reads as a clean world-target negative, but it sits inside Table 3's cells. The
surrounding extraction is:

> … PNAE (Brazil) Farmers remain dependent on external public coordination.
> Public embeddedness alone may be insufficient to drive deep territorial
> transformation. B – Scaffolded Boissière et al. (2020) …

Whether a table cell is a proposition unit is **HD-09**, segmentation ownership,
which the register records as assigned in a circle and never resolved. Adding
this case would silently answer HD-09 in the gold set rather than in the spec.

Worth adding **after** HD-09 is settled, and it is a good test case for whichever
way it goes.

### N7 candidate — §5.1, char 69241 — corrupted by page furniture

Extraction yields:

> Our first contribution bridges agroecology—traditionally rooted in **11 J.A.
> Rodríguez et al. Journal of Purchasing and Supply Management xxx (xxxx) xxx**
> coordination infrastructure where producer organizations lack market access,
> consolidation assets, or formal governance capacity.

A running header and page number injected mid-sentence, joining two fragments
across a page boundary. The sentence as extracted is not a sentence.

**This is a third extraction defect**, beyond the two recorded in
`GOLD_SET_v0.1.md`:

```text
1  two-column reading order      pdftotext -layout interleaves columns
2  soft hyphens U+00AD           strip character AND following whitespace
3  page furniture                running headers, page numbers, journal
                                 strapline injected between sentence fragments
```

All three are the same class as the ampersand problem in ingest: the rules are
fine, the bytes are wrong, and nothing errors. Any exact-span requirement
evaluated against text carrying (3) will fail on units that straddle a page
break, and will fail *silently* — the quote appears absent rather than corrupted.

---

## What this changes

Adding N3–N5 gives `BR-CROSS-14` three discriminating cases where it currently
has none.

N6 and N7 are held: one waits on HD-09, the other on the extraction path.

And N7 argues the point already made in `GOLD_SET_v0.1.md` more strongly. Gold
cannot be scored against a local PDF extraction. It needs the canonical stored
text from the conversion path, where page furniture is handled upstream rather
than by whoever writes the gold runner.
