# rc3 A2's six reasons: which are implemented, and why the others are not

Written 21 September 2026, implementing rc3 §A against v3.3.

rc3 A2 closes the `excluded_reason` set at six members and gives each a count
over its nine in-profile papers. Four of the six have a rule stated somewhere
in rc3. Two do not. Detectors exist only where a rule does, and the reason each
of the others is absent was measured against the corpus rather than assumed.

```text
reason                 rc3   rule stated in rc3        implemented   corpus
                                                                     (14 papers)
leading_gloss           11   NOWHERE                   no                  —
url_or_image             8   B10 + §G case             yes                11
publisher_metadata       4   §E                        yes                 8
math_expression          3   B10, with a D2 carve-out  yes, 0 hits         0
conversion_artifact      3   NOWHERE                   no                  —
non_citation_year        1   §F names one instance     no                  —
                        ──                                                ──
                        30                                                19
```

The two columns of counts are over different corpora — rc3's nine in-profile
reconciling papers against all fourteen — so they are not expected to agree and
no claim is made that they do.

## The two with no rule anywhere

`leading_gloss` and `conversion_artifact` each appear **exactly once in the
whole specs tree**, in A2's own table:

```text
$ grep -rn "leading_gloss\|conversion_artifact" specs/
specs/citation/citation-v3.4-rc3-amendments.md:44:    leading_gloss,          11
specs/citation/citation-v3.4-rc3-amendments.md:48:    conversion_artifact,     3
```

They carry counts and no definition. Fourteen of the thirty spans rc3 counts as
correct refusals are therefore unreachable from rc3 alone. rc2 may define them;
rc2 is missing. Both names are kept in the closed set so the vocabulary is
right and a future detector has somewhere to land.

## `non_citation_year`: one instance is not a rule

§F gives the instance and no rule:

```text
non_citation_year   1   "three consecutive (2011, 2012, and 2013)"
```

It is in `849f8fc6`, it occurs once, and it is the only one. The obvious rule —
a parenthetical that is a pure year list with no reachable author run — was
written and run against the corpus before being adopted. It matches **nineteen
spans**, of which:

> **The table below is stale as of 24 September, and the rule that produced it
> was never written down.** Both halves matter. Six of the eight math-wrapped
> spans now parse, so the first row has moved. And the rule could not be
> recovered from the sentence above it: read as "the parenthetical is a pure
> year list" it matches 1145 C1 spans, and only some further reading of "no
> reachable author run" brings it to nineteen. The conclusion below survives
> either reading. The count does not, and a count whose method is a sentence
> can only be re-asserted. The replacement is `PURE_YEAR_LIST` in
> `scripts/corpus_dispositions.py`, which is a different and narrower rule,
> stated in code, re-run on every pass and pinned: 19 candidates, 8 already
> `publisher_metadata`, 11 live `no_grammar_match`, exactly 1 of them §F's.

```text
8   D2's math-wrapped citations     Baron ×2, Shepherd and Kay, Bicen and
                                    Johnson, Pichler, Hayes ×3
1   §C's malformed author form      Fremout et al (2022)
1   a real narrative citation       Boltužić and Šnajder (2014)
6   table source notes              "Source: SPSS multiple regression
                                    analysis (2015)" and similar
1   §F's own case                   three consecutive (2011, 2012, and 2013)
2   narrative boundary failures
```

§F is explicit that the boundary failures must not be removed:

> **These 15 MUST NOT be removed from the denominator as false positives.**
> They are missed extraction.

So the rule would take ten or more real citations off A5's denominator to
catch one non-citation. Nothing is excluded under this reason until rc2 or
Alex Zamurko supplies a rule that separates the case from the eighteen it
resembles.

Re-measured 24 September against the named spans, which are checkable even
though the count was not:

```text
Baron (2012,2016) ×2           now parsed, both years        rc3 §G, D2
Shepherd and Kay (2012,2014)   now parsed, both years
Hayes (2012,2017) ×3           now parsed, both years
Bicen and Johnson (2014,2015)  unresolved, stopword_surname  lead-in, B5
Pichler (2012,2019)            unresolved, no_grammar_match  lead-in, B5
Fremout et al (2022)           still §C's malformed form
(2011, 2012, and 2013)         still unresolved, §F's own
```

Six of the eight math-wrapped spans left this list by parsing, which is the
outcome §F's warning was protecting: they were real citations all along. The
two that remain fail on a lead-in rather than on the year list, so they belong
to B5 and not here. **The verdict is unchanged and is now better supported** —
a `non_citation_year` rule built on this shape would have excluded six real
citations that the corpus has since recovered.

## `math_expression`: implemented, and correctly fires zero times

B10 lists math exclusion and then warns about it by name:

> Blanket math-span exclusion would delete three real citations — `Baron
> $(2012,2016)$` and `Shepherd and Kay $(2012,2014)$`, where Mathpix wrapped an
> ordinary parenthetical in math mode. Those require D2's pre-canonicalisation
> unwrapping, not exclusion.

Every `$…$`-enclosed candidate in the corpus was listed before writing the
detector. There are eight, which is D2's own count — "Eight corpus-wide, three
in the nine in-profile papers" — and every one of them is the shape
`$(YYYY,YYYY)$`:

```text
4918fd7d   $(2012,2016)$ ×2      Baron
50408397   $(2012,2014)$         Shepherd and Kay
bf2fdc4a   $(2014,2015)$         Bicen and Johnson
ed6a890a   $(2012,2019)$, $(2012,2017)$ ×3
```

So the detector carries D2's MATCH clause as a carve-out and refuses to exclude
a year-only math span. It fires zero times on this corpus, and that is the
correct result rather than a missing detector: the three spans rc3 counts under
`math_expression` are not among the candidates this detector sees. Removing the
carve-out is a mutation in `mutate_citation_suite.py`, and it takes the Baron
control red.

## `url_or_image`: anchored, not containment

The span must **be** a URL, not contain one. `2af68a7f` carries

```text
(BIS, 2014, https://www.gov.uk/government/organisations/…)
```

a real citation with its source link inside the group. A containment test
excludes it; an anchored test does not. Both shapes are conformance cases.

The eleven that match are all the URL of a `![](https://cdn.mathpix.com/…)`
image, whose `height=1895&width=1318` query parameters parse as years. That is
why an image is a citation candidate at all.

## `publisher_metadata`: structural, not by name

§E says "No new detection is required — the section map already labels both by
name." It labels one of them. `section_stack_at` returns the **fabricated**
name `"front matter"` whenever no h2–h4 heading precedes the offset, so a name
test would match not because a section was identified as front matter but
because no section had started.

Both tests were written at first, name and structural. The mutation probe then
removed the structural one and the suite stayed green — the fabricated name
caught the same span through the other branch, and the control named for the
structural rule had been passing through the name path all along. Two
overlapping branches, one of them matching an invented value, cannot both be
held by a control. The invented one was removed.

What the structural test rests on, measured over all fourteen papers before it
was chosen:

```text
6 papers    exactly one candidate above the first h2, every one of them the
            journal's own "To cite this article:" line
8 papers    none at all
13 of 14    first h2 is `## Abstract`, so no abstract sits above it
2 papers    carry a `## Citation information` h2 — 849f8fc6 and ea07e5f5,
            exactly the two §E names
```

A paper carrying a real `## Front matter` heading is not handled. Those spans
stay unresolved and stay in the denominator, where they are visible, which is
the safe direction to be wrong in.

## What this changed, measured

Same corpus, same fixes, before and after §A:

```text
              parsed   unresolved   excluded   denominator   parse rate
before          2094          158          —          2252       0.9299
after           2094          139         19          2233       0.9378
delta             +0          -19        +19           -19      +0.0079
```

**No paper lost a parsed citation.** The nineteen moved from unresolved to
excluded and conserved exactly, which is A3's completeness invariant holding by
construction rather than by hope. The rate moves because the denominator is
corrected, not because anything new was read.

Gold scores are unchanged, which is the expected result — these amendments
classify refusals, not citations:

```text
paper 1   recall 0.969   precision 1.000
paper 2   recall 0.882   precision 0.989
```

## What would close the rest

```text
1  rc2, which may define leading_gloss and conversion_artifact
2  a rule for non_citation_year that separates §F's one case from the
   eighteen spans that share its shape
```

Both are cheap to state and, as the nineteen-span measurement shows, expensive
to guess at.
