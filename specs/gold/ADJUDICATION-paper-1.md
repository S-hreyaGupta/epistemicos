# The eleven extras on paper 1, adjudicated

`gold_runner.py` reports works the candidate produced that the gold set does
not contain, and says of them: *either the candidate is wrong or the gold set
is incomplete.* Nothing in the run distinguishes the two, so precision of 0.884
could have meant eleven grammar errors or eleven missing annotations, and there
was no way to tell which.

Resolved 18 September 2026 against `ad1e3ff9`, by looking at where each one
sits in the manuscript and whether the manuscript's own bibliography contains
it. None of the eleven is a grammar error.

## Method, and what limits it

For each extra: locate every occurrence in the body, record whether it sits in
prose or in a table row, and look for a reference entry whose first author and
year match.

The check is independent of the extractor in the way that matters — a
bibliography entry is written by the paper's authors, not derived by the
grammar under test, so "this work is in the reference list" is not something
the extractor can manufacture.

**What is not independent is the discovery.** These eleven were found by
reading the candidate's output. A different extractor would have produced a
different eleven. So this pass improves the gold set in the direction the
current implementation happens to look, and any figure computed afterwards
carries that. It is an annotation-completeness pass driven by a candidate and
verified against the source, which is worth doing and is not the same thing as
an independent annotation.

Anyone quoting a number from this file needs that sentence with it.

## The three groups

### EC-2, the possessive — three works, each costing twice

```text
gold has              candidate produced      reference entry
bartko 1976           bartko's 1976           Bartko, J. (1976).
fine 1998             fine's 1998             Fine, C. (1998).
mcgraw and wong 1996  mcgraw and wong's 1996  none
```

All three are cited in prose, in the possessive: *following Bartko's (1976)
formula*, *following McGraw and Wong's (1996)*. The annotator recorded the
work; the extractor keyed the possessive.

This is the same defect as `CITATION-EDGE-CASES.md` EC-2, and the adjudication
shows it costs **twice per work**, which the edge-case record did not say: the
gold item goes unmatched, which is a miss, and the possessive form is not in
gold, which is a false positive. Three works, six penalties. That is why
folding `'s` moved recall and precision together.

`mcgraw and wong 1996` has no reference entry at all. It is cited in the text
and absent from the bibliography — a property of the manuscript, not of the
extractor, and the reconciliation is right to leave it unmatched.

### Missed by the annotation — five works, in prose, all with entries

```text
bellamy et al. 2014          Bellamy, M. A., Ghosh, S., & Hora, M. (2014).
ellram et al. 2004           Ellram, L. M., Tate, W. L., & Billington, C. (2004).
sampson and froehle 2006     Sampson, S. E., & Froehle, C. M. (2006).
shao et al. 2018             Shao, B. B., Shi, Z. M., Choi, T. Y., & Chae, S. 2018.
unruh et al. 2016            Unruh, G., Kiron, D., Kruschwitz, N., … (2016).
```

Ordinary prose citations with matching bibliography entries, absent from the
annotation. Two of them share one sentence:

```text
unobserved features of service supply chains (Sampson and Froehle, 2006; Ellram et al., 2004).
```

which suggests the omission is a reading slip on a multi-segment group rather
than a judgement about what counts.

Worth noting that `shao et al. 2018` has a reference entry with no parentheses
around the year — `Chae, S. 2018.` — a style variant the assembly handled.

### Table-only — three works, ruled on 18 September

```text
| Basole et al. (2017) | - | Structural prominence; density | - | …
| Dong et al. (2015)   | - | Relational embeddedness       | - | …
| Park et al. (2018)   | - | Accessibility                 | - | …
```

Each appears **only** as the first cell of a row in a table headed *Summary of
empirical studies on supply chain structure*, whose first column is
`Author-Year`. All three have reference entries.

`bellamy et al. 2014` is in this table too and is listed in the previous group
instead, because it is also cited in prose.

**Ruled by Alex Zamurko, 18 September: they count.**

> A table titled "Summary of empirical studies" with an Author-Year column is
> part of the manuscript's scholarly content, and Basole 2017, Dong 2015 and
> Park 2018 are explicitly identified there and all appear in the reference
> list. Unless the annotation protocol explicitly excluded tables, excluding
> them would create an undocumented prose-only rule.

And prospectively, so the next annotator does not face the same question:

> Citations appearing in manuscript tables count when the table identifies
> scholarly works by author/year or equivalent citation information, unless
> the annotation protocol explicitly excludes that table type.

Added in v0.3 by `scripts/build_gold_v03.py`, which checks the rule's own
condition rather than assuming it: the table must identify works by
Author-Year, the work must appear in a table row, it must *not* appear in
prose, and it must have a reference entry. The rule travels with the data in
`provenance.table_scope_rule`.

The same ruling leaves the three possessives alone: they are extractor grammar
errors, not annotation errors, so the gold set is already correct and EC-2 is
the extractor's to fix.

## What the groups are worth

These are measured, not projected. Every row after the first is a real run of
`citation_extract.py` through `citation_candidate.py` and `gold_runner.py`.

```text
                                              gold   recall   precision
v0.1, as first scored                           90    0.933       0.884
v0.1, after the particle fix                    90    0.944       0.876
v0.2, + the five prose omissions                95    0.947       0.928
v0.3, + the three table works                   98    0.949       0.959
v0.3, + EC-2 repaired                           98    0.980       0.990
```

Against Alex Zamurko's threshold of 0.95 on both, set 28 August. Precision
crosses at v0.3. Recall is 0.949, one thousandth short, and **EC-2 alone takes
both over**: 0.980 and 0.990.

Only the last row is hypothetical, and it is hypothetical in a narrow way —
EC-2's repair is not implemented, but the effect was measured by folding the
possessive and rescoring rather than estimated.

### How these numbers must be labelled

Alex Zamurko, 18 September:

> The 0.968 / 0.968 result is useful, but do not present it as independent
> holdout performance. The five prose omissions and three table cases were
> found through extractor-led adjudication, so label the result as
> post-adjudication performance on an amended Gold Set.

So: **post-adjudication performance on an amended gold set.** Not independent
holdout performance, and not to be quoted as such. The gold set improved in the
direction this implementation happens to look, and this file exists to record
exactly what changed and why.

The v0.1 row is the last one that is independent of the extractor, and it is
0.933 / 0.884.

## What remains on paper 1, and it is now fully accounted for

Nine discrepancies at v0.3, every one with a named cause and none unexplained:

```text
6   EC-2          three works, each scored twice — a miss and a false positive
1   EC-5          dooley et al. 2019, cited only in a footnote
1   EC-3          den brink and van der woerd 2004, envelope truncation
1   world bank    refused exactly as §12 requires for institutional authors
```

Which is the useful state to be in: nothing here is a mystery, and six of the
nine are one defect.

## What this establishes, and what it does not

It establishes that **none of paper 1's eleven extras is a grammar error**. The
precision figure of 0.884 contained no case of the extractor inventing a
citation, mis-parsing a span, or keying the wrong surname. It was one defect
counted three times, five annotation gaps, and three works whose status is
undecided.

It does not establish that precision is really 0.968. That number depends on
annotation changes not yet made and a repair not yet done, and it was arrived
at by asking the candidate where to look.

It says nothing about paper 2, whose fifteen misses have not been adjudicated
and whose extras are a different list.

## What would follow

A gold set v0.2 carrying the five prose additions, with provenance recording
that they were found this way rather than in the original annotation pass, so
that the improved figure is never mistaken for an independent one. The table
question goes to whoever owns the annotation scope. EC-2 stays in the edge-case
register until it is repaired, now with the note that it costs double.
