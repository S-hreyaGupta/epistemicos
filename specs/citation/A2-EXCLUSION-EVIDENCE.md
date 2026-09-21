# rc3 §A2's thirty exclusions, against the case-level evidence

21 September 2026, from `CITATION_UNRESOLVED_109.md`, recovered the same day
and now at `specs/gold/recovered/`. Alex Zamurko had identified that file by
name as the missing piece and reported it could not be found.

It supplies both definitions A2 leaves out, and it does not reconcile with A2's
arithmetic.

---

## `conversion_artifact` — defined by its three cases

All three are one shape. The residual files them under a section headed
**"UPSTREAM CONVERSION — fix before Citation sees the text"**.

```text
77.  4918fd7d [19437:19448]   (2012,2016)
78.  4918fd7d [38239:38250]   (2012,2016)
79.  50408397 [27081:27092]   (2012,2014)
```

> Additional work by Baron `$(2012,2016)$`, which focused on the effects of
> extensive leader action learning programs, showed that [...]

The PDF-to-Markdown conversion wrapped the year parenthetical in LaTeX math
delimiters. The span is a real citation that the converter damaged, not a
grammar failure and not something the grammar should learn to read.

```text
definition   a candidate span whose detected form exists only because of an
             upstream conversion defect; here, a year parenthetical wrapped in
             $...$ by the PDF converter
disposition  repair upstream, before the extractor sees the text
```

**This confirms the X-08 reading.** Alex Zamurko's guess on 21 September, that
`conversion_artifact` forward-references rc2 X-08's deferred conversion repair,
is right: the residual's own section header says the fix belongs upstream.

---

## `leading_gloss` — defined by its eleven cases, and not by a marker

```text
external and unstable attributions: e.g., leader stress, time or task pressure
e.g., goal setting or intellectual stimulation
e.g., using images and metaphors in a speech
cognitive decentering
psychological capital, leader self-knowledge and self-consistency
e.g., from the Minnesota Satisfaction Questionnaire
e.g., emotional stability, conscientiousness, psychological capital, ...
what organizational scholars would call interpersonal justice or fairness
i.e., distributive, procedural, informational, and interpersonal
i.e., respect and dignity
as past research on average justice has shown
```

Each is a segment of a split parenthetical. The full parenthetical does contain
citations — `(e.g., goal setting or intellectual stimulation; Barling, Weber, &
Kelloway, 1996; …)` — and splitting on `;` leaves the leading explanatory text
as its own detected occurrence with no author-year in it.

**A reconstruction offered earlier in this repository was wrong, and the way it
was wrong is the point.** Before the file was recovered, `leading_gloss` was
guessed from four examples as "a segment opening with a gloss marker (e.g.,
i.e., viz., namely)". Filtering on that rule returns six of these eleven. Four
of the eleven carry no marker at all:

```text
cognitive decentering
psychological capital, leader self-knowledge and self-consistency
what organizational scholars would call interpersonal justice or fairness
as past research on average justice has shown
```

A marker-based rule would leave those four in the denominator. The class is
defined by what the segment *is* — explanatory prose glossing the preceding
term — not by how it opens.

```text
definition   a segment produced by group splitting whose text glosses the
             preceding term rather than citing, and which contains no YEAR
```

The separation this must preserve, because it cuts the other way: rc3 **B5**,
"bounded lead-in cue", is worth **+17** and *recovers* `(e.g., Tepper, 2000)` —
a real citation behind the same marker. Same cue, opposite disposition. What
separates them is whether an author-year survives in the span, not the cue.
A marker rule that excluded on the cue alone would delete seventeen real
citations to save eleven non-citations.

---

## A2's thirty does not reconcile with the thirty it came from

The residual's class 5, **"NOT CITATIONS — come out of the denominator — 30"**,
has seven subsections. A2 has six members. Five map one-to-one with identical
counts:

```text
residual class 5                    rc3 §A2                    count
──────────────────────────────────────────────────────────────────────
leading gloss segment          →    leading_gloss                 11
A3 url / image span            →    url_or_image                   8
math / LaTeX                   →    math_expression                3
conversion artifact            →    conversion_artifact            3
non-citation year              →    non_citation_year              1
                                                                  26

colon locator, trailing prose        2  ┐
bare locator                         2  ┘ →  publisher_metadata     4
                                                                  30
```

Those two remaining classes are page locators:

```text
(El Akremi et al., 2015: 2)
Indeed, Lind and van den Bos (2002: 196)
p.56
P.923
```

`publisher_metadata` is not what those are. And A2 itself says so about half
of them:

> **`bare_locator` is NOT in this set.** `(Barbier, 2022; P.923)` is an author
> error — a semicolon where APA wants a comma — and belongs to the diagnostic
> class in §C, not to correct refusal. Including it would double-count those
> two.

So rc3 removes two cases from the set and the total stays at 30. Either:

```text
a)  publisher_metadata is a genuinely separate class that happens to number 4,
    the two bare locators were dropped as the note says, and the total should
    read 28
b)  publisher_metadata is a relabelling of the four locators, in which case it
    contains the two the note excludes and the note contradicts the table
```

Not resolvable from these files. Worth saying that `publisher_metadata` is a
real class independent of this question — this repository's implementation
emits eight of them across fourteen papers — so (a) is the more likely reading,
and the scope of rc3 §I may simply be wider than the nine papers behind the
109. That would make the count right and the total's provenance wrong, which
is still worth knowing before A2 is treated as arithmetic.

---

## What this changes

```text
conversion_artifact   definable now. Confirms the X-08 forward reference.
leading_gloss         definable now, and NOT by the marker rule this
                      repository had reconstructed.
A2's total            needs re-deriving, or a note saying which scope each
                      count is over.
CIT-EXCL-01           unaffected. Both names stay in the set, deferred. The
                      decision was about status, and this is about meaning.
```

`GSD-FOLDER-RECOVERY.md` records the separate and larger point, that
`impl_v34.py` has no candidate-exclusion machinery at all, so none of A2's
thirty came from the extractor. The classification was a heuristic pass its own
author labelled indicative. This document is what that pass actually contains.
