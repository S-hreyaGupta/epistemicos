# `uncited_reference` measures our parser, not the bibliography

22 September 2026, found while implementing rc2 §9.6.

```text
                                  22 Sep    23 Sep
uncited_reference emitted            57        56
of those, the reference IS cited     28        27
                                     ──        ──
plausible residual                   29        29
```

**Both headline figures moved on 23 September and the residual did not.** rc2
§3.1's closed PREFIX set turned out to be five cues short, and the five missing
are the multiword forms — `for a review, see` among them, which this document
lists below as one of its own examples. Restoring them let one of those spans
parse, which resolved its reference and removed the row from both columns at
once. Measured rather than reasoned: the extractor at `f6280de` produces 57 and
28 over this corpus, the one at `e788440` produces 56 and 27.

The figures are re-derived by `scripts/corpus_dispositions.py`, by this
document's own method, so the next move is noticed rather than absorbed.

```text
by the failed span's own reason      22 Sep    23 Sep
no_grammar_match                        24        23
stopword_surname                         4         4
```

## The method does not reach non-person references

"Its surname and year" is person-shaped, and three `non_person|` reference
keys satisfy the same test:

```text
17bef7c6   non_person|citizenship report p&g india subcontinent|2022
ad1e3ff9   non_person|bloomberg|2011
ad1e3ff9   non_person|bloomberg|2013
```

All three were present on 22 September too, so this is a gap in the method
rather than drift. Counting them takes the residual from 29 to 26. They are
reported separately rather than folded in, because this document's breakdown
below is over the person-shaped population and mixing the two would make the
28 and the 27 stop being comparable.

Just under half the rows are wrong. Each of the 27 names a reference the paper
does cite, in a span the grammar could not read. The breakdown that follows was
written over the 28 and one of its lead-in-cue cases has since parsed, so it
describes the shapes rather than the current count.

The implementation is faithful to §9.6. That is the problem: the section is
correctly implemented and the number it produces still does not mean what its
name says.

> **These figures replace an earlier version of this document that reported 72
> and 39.** Those came from a corpus run with only two of the five canonical
> fixes enabled. The correction is at the bottom, under "How this document was
> wrong first", because it is the more useful half.

---

## How the 28 were identified

For each `uncited_reference`, check whether its surname and year both appear
inside a single span the extractor emitted as `unresolved_citation`. Same span,
not the same document — a first attempt matched surname and year independently
across all failed spans and returned a higher number, inflated by `kim`
appearing once and three different years appearing elsewhere. The loose test
looked like corroboration and was counting coincidence.

The reason field is the extractor's own, not a hand label.

```text
no_grammar_match    24
stopword_surname     4
```

---

## What the 28 actually are

```text
(M. Kim, 2020)                               forename initial first     4
Y. J. Kim et al. (2013)

However, Dahlander and Gann (2010)           lead-in cue, rc3 B5        9
Additionally, Bacq, Hartog, and Hoogendoorn (2016)
(for a review, see Sonnentag & Frese, 2003)
(for an overview, see, e.g., Iszatt-White & Kempster, 2018)

and Ohly, Sonnentag, Niessen, and Zapf (2010)    conjunction lead-in    5
and Sauer and Seuring (2023)

(Van Quaquebeke 2016)                        multi-token surname, B1a   3
Saeed & Binti Abdul Ghani Azmi, 2019
Pérez-Luño, Wiklund, & Valle Cabrera, 2011

Hayes (2012,2017)                            multi-year parenthetical   4
Similarly, Bicen and Johnson (2014,2015)

(conservation of resource theory, Hobfoll, 1989, and ego-depletion,
 Baumeister et al., 1998)                    gloss-prefixed group       2

(Smith, Weed, & Ramsay, 2005-present)        one-off                    1
```

Almost every shape is already-specified work: rc3 **B5** bounded lead-in cue,
**B1a** surname production, and the forename-first limitation rc3 §C3
discusses.

The multi-year group is worth separate attention. `Hayes (2012,2017)` is the
same shape as `conversion_artifact`'s `Baron $(2012,2016)$` with no math
wrapping, so unwrapping alone cannot recover it. That is discrepancy 6 in
`RC2-RC3-DISCREPANCIES.md` — "rc3 D2 unwraps into a form the grammar refuses"
— now visible end-to-end rather than only at the transform.

---

## The finding, stated plainly

**One unread citation is counted twice, under two names, in two places.**

```text
the citation   → unresolved_citation, and stays in A5's denominator
its reference  → uncited_reference, a false residual
```

`uncited_reference` is parse recall, inverted and relabelled. It reads as a
property of the author's bibliography — "they listed something they never
cited" — and is substantially a property of our grammar. Anyone reading the
number without this document would draw a conclusion about the corpus from a
measurement of the extractor.

---

## What was NOT done about it

No filter, no threshold, no confidence field. rc2 §9.6 says emit
`uncited_reference` for every remaining unique keyed reference, and that is
what the implementation does. Suppressing rows whose surname turns up in a
failed span would be inventing a rule rc2 does not have, and would hide the
recall problem inside the diagnostic that reveals it.

The rule is implemented as written. The number is recorded as unreliable.

---

## How this document was wrong first

The original version reported 57 as 72 and 28 as 39, and named a
fourteen-row colon-locator group as its largest open question — spans like
`(Gilliland, 2008: 271)` failing against records that describe colon locators
as handled.

They are handled. `LOCATOR_COLON` is applied when `"colon"` is in the fix set,
the canonical set is `("ampersand", "segments", "colon", "cp", "mathyear")`,
and every corpus measurement behind the first version passed
`{"ampersand", "segments"}`. With the canonical set, **zero** colon-locator
rows remain.

The reduced set is correct inside `test_citation_extract.py`, where a control
isolates one behaviour deliberately. It was carried into corpus measurement by
habit, where it is simply wrong.

```text
                     two fixes      canonical five
parsed                    2069                2102
unresolved                 166                 133
uncited_reference           72                  57
   of those, false          39                  28
```

The right-hand column reproduces the corpus figures already on record, which
is the check that should have been run first: a new measurement that disagrees
with the established one is reporting on itself until that disagreement is
explained.

**This is the third measurement error of the same shape in two days**, and the
other two are recorded in `GSD-FOLDER-RECOVERY.md`: a search whose negative
result described the search rather than the world, and a surname/year test that
matched across spans instead of within one. Each produced a number that looked
like a finding. Each was caught by re-deriving rather than by anything going
red.

The defect class the conformance suite exists to catch does not stop at the
suite. A measurement is a check, and a check that passes for a reason other
than the one it names is the same failure wherever it happens.
