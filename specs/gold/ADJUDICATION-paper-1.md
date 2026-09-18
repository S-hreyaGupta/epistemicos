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

### Table-only — three works, and a scope question, not a defect

```text
| Basole et al. (2017) | - | Structural prominence; density | - | …
| Dong et al. (2015)   | - | Relational embeddedness       | - | …
| Park et al. (2018)   | - | Accessibility                 | - | …
```

Each appears **only** as the first cell of a row in a table headed *Summary of
empirical studies on supply chain structure*, whose first column is
`Author-Year`. All three have reference entries.

Whether a table of works counts as citing them is a question about what the
gold set is for, and it has not been asked. The annotator may well have
excluded table contents deliberately, and this file does not overrule that.
`bellamy et al. 2014` is in this table too and is listed in the previous group
instead, because it is also cited in prose.

**This one needs a decision rather than a repair.**

## What the groups are worth

```text
                                            recall   precision
as scored today                              0.933       0.884
+ EC-2 repaired                              0.967       0.916
+ the five prose omissions annotated         0.968       0.968
```

Against Alex Zamurko's threshold of 0.95 on both, set 28 August. The bottom row
meets it.

It is a projection and not a score. It assumes the five are accepted into the
gold set and that EC-2 is repaired, and neither has happened. The table group
is excluded from it entirely, since that is undecided.

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
