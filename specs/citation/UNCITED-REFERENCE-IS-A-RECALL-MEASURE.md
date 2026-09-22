# `uncited_reference` measures our parser, not the bibliography

22 September 2026, found while implementing rc2 §9.6.

```text
uncited_reference emitted            72
of those, the reference IS cited     39
                                     ──
plausible residual                   33
```

Fifty-four percent of the rows are wrong. Each of the 39 names a reference the
paper does cite, in a span the grammar could not read.

The implementation is faithful to §9.6. That is the problem: the section is
correctly implemented and the number it produces still does not mean what its
name says.

---

## How the 39 were identified

For each `uncited_reference`, check whether its surname and year both appear
inside a single span the extractor emitted as `unresolved_citation`. Same span,
not the same document — a first attempt matched surname and year independently
across all failed spans and returned 41, inflated by `kim` appearing once and
three different years appearing elsewhere. The loose test looked like
corroboration and was counting coincidence.

Reproducible; the reason field is the extractor's own, not a hand label.

```text
no_grammar_match    35
stopword_surname     4
```

---

## What the 39 actually are

```text
(M. Kim, 2020)                              forename initial first
Y. J. Kim et al. (2013)
However, Dahlander and Gann (2010)          lead-in cue, rc3 B5
Additionally, Bacq, Hartog, and Hoogendoorn (2016)
(for a review, see Sonnentag & Frese, 2003)
and Ohly, Sonnentag, Niessen, and Zapf (2010)   conjunction lead-in
(Van Quaquebeke 2016)                       multi-token surname, rc3 B1a
Saeed & Binti Abdul Ghani Azmi, 2019
(Gilliland, 2008: 271)                      colon locator
(Colquitt, Scott, Judge, & Shaw, 2006: 114)
Robbins, Ford, and Tetrick's (2012: 250)    possessive + colon locator
(conservation of resource theory, Hobfoll, 1989, and ego-depletion,
 Baumeister et al., 1998)                   gloss-prefixed group
```

Almost every shape is already specified work: rc3 **B5** bounded lead-in cue,
**B1a** surname production, **B8** possessive, and the forename-first
limitation rc3 §C3 discusses. The colon-locator group is the largest single
shape and is worth its own look, since the records describe colon locators as
already handled and fourteen of these carry one.

---

## The finding, stated plainly

**One unread citation is counted twice, under two names, in two places.**

```text
the citation   → unresolved_citation, and stays in A5's denominator
its reference  → uncited_reference, a false residual
```

`uncited_reference` is parse recall, inverted and relabelled. It reads as a
property of the author's bibliography — "they listed something they never cited"
— and is substantially a property of our grammar. Anyone reading the number
without this document would draw a conclusion about the corpus from a
measurement of the extractor.

That is the defect shape this repository keeps meeting. A green suite that is
green for another reason. A search result recorded as a fact about the world.
A control that passes whether or not its rule holds. Here: a diagnostic whose
name points at the manuscript while its value tracks our own failures.

---

## What was NOT done about it

No filter, no threshold, no confidence field. rc2 §9.6 says emit
`uncited_reference` for every remaining unique keyed reference, and that is
what the implementation does. Suppressing rows whose surname turns up in a
failed span would be inventing a rule rc2 does not have, and would hide the
recall problem inside the diagnostic that reveals it.

The rule is implemented as written. The number is recorded as unreliable.
Those are different jobs and both are done.

---

## What follows

```text
now        do not report 72 as an uncited-reference count, in a corpus
           report or anywhere else, without this caveat attached
on B5/B1a  re-measure after each lands. The 39 should shrink, and by how
           much is a better recall signal than the parse rate, because it
           is end-to-end rather than per-span
for rc2    §9.6 may warrant a note that the residual is only as good as
           Pass 1 recall. Alex Zamurko's call, not this implementation's.
open       the colon-locator group, fourteen rows, against records that
           describe colon locators as handled
```

The 33 that survive the check are the plausible residual. They are not
verified as genuinely uncited — nothing here establishes that — they are
simply the rows this test cannot show to be wrong.
