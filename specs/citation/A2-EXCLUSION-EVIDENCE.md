# rc3 §A2's thirty exclusions, against the case-level evidence

21 September 2026, from `CITATION_UNRESOLVED_109.md`, recovered the same day
and now at `specs/gold/recovered/`. Alex Zamurko had identified that file by
name as the missing piece and reported it could not be found.

It supplies both definitions A2 leaves out, and it does not reconcile with A2's
arithmetic.

---

## `conversion_artifact` — defined by its three cases

**CORRECTED 22 September. The first version of this section identified the
wrong three cases, and the correction matters because the wrong version was
sent to Alex Zamurko and used to confirm a guess of his.**

The residual has TWO groups of three that both mention conversion, in
different classes, and the first reading took the wrong one:

```text
class 4   UPSTREAM CONVERSION — fix before Citation sees the text     3
          Baron $(2012,2016)$ and two more like it. NOT part of the 30.
class 5   conversion artifact                                         3
          inside "NOT CITATIONS — come out of the denominator — 30"
```

A2's thirty is class 5. So `conversion_artifact` is class 5's three:

```text
102.  4918fd7d [15211:15215]   MBSR
103.  4918fd7d [50950:50977]   (ECP_150 03_08_2014_A2 OZL)
104.  4918fd7d [80801:80814]   McMindfulness
```

> Research has shown that mindfulness programs, such as MindfulnessBased
> Stress Reduction (**MBSR**; Kabat-Zinn, 1982), benefit mental and physical
> health [...]
>
> The study was approved by the local ethical review board
> **(ECP_150 03_08_2014_A2 OZL)**.

An acronym, an ethics approval code, and a coined term. Two of the three are
the gloss half of a `(GLOSS; Author, Year)` parenthetical — structurally the
same shape as `leading_gloss`, and distinguished from it, as far as the
evidence shows, by being a single opaque token rather than explanatory prose.

```text
candidate definition   a single opaque token inside a parenthetical that the
                       detector proposed and that names no author — an
                       acronym, an identifier code, a coinage
```

**The X-08 reading is NOT supported, and was confirmed here in error.** X-08
defers `ConversionArtifactAnnotations / conversion repair`. `MBSR` and
`McMindfulness` need no conversion repair; they are correctly converted words
that happen to sit where a citation sits. Only the ethics code looks like
conversion debris at all, and even that is a faithful rendering of what the
manuscript says.

Worth recording that the name is a poor fit for two of its three members,
which may be why it was never given a rule. Whatever `conversion_artifact`
was meant to mean, these three are what it counts.

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

## A2's thirty, reconciled

**Settled 22 September by running the extractor over exactly the nine papers
behind the 109 residual** — `43338825`, `4918fd7d`, `50408397`, `5da73cf4`,
`849f8fc6`, `ad1e3ff9`, `c1d56945`, `e1b418a4`, `ea07e5f5`, named in
`CITATION_CORPUS_RUN_3.md`.

```text
A2 reason             A2   ours, same nine papers
────────────────────────────────────────────────────────────────
url_or_image           8   8   exact
publisher_metadata     4   4   exact
leading_gloss         11   0   no rule exists
conversion_artifact    3   0   no rule exists
math_expression        3   0   rule exists, never fires
non_citation_year      1   0   rule exists, never fires
                      30   12
```

**`publisher_metadata` 4 is real and independent**, not a relabelling of the
four page locators it appears to displace. Both it and `url_or_image` reproduce
to the number on the same corpus, which is as close to confirmation as this
evidence gets.

So the total holds at 30 for a reason neither reading guessed: **four went out
and four came in.** The residual's four locators left the exclusion set — two
to §C's diagnostic class by A2's own note, two because the colon-locator fix
makes them parse — and four `publisher_metadata` spans came in. The counts
happen to match.

**Eighteen of the thirty do not reproduce here, in two distinct ways.**
Fourteen have no rule anywhere in the specification set. The other four are
different and more interesting: `math_expression` and `non_citation_year` ARE
implemented, with rules, and fire zero times across all thirteen in-profile
papers. For `non_citation_year` the extractor already records why — rc3 §F
gives one instance and no rule, and the obvious rule matches nineteen spans of
which one is right. One in nineteen is not a rule.

---

## What the two thirties are made of

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

So rc3 removes two cases from the set and the total stays at 30. Two readings
were offered when this was first written, and **both were wrong**:

```text
a)  publisher_metadata is separate and the total should read 28
b)  publisher_metadata is a relabelling of the four locators
```

The measurement above settles it. `publisher_metadata` is separate — four real
spans, reproduced exactly — so (b) is out. But the total is still 30 and
correctly so, because four locators left and four `publisher_metadata` came in,
which (a) did not consider. The arithmetic works; it is the composition that
changed.

Not resolvable from these files. Worth saying that `publisher_metadata` is a
real class independent of this question — this repository's implementation
emits eight of them across fourteen papers — so (a) is the more likely reading,
and the scope of rc3 §I may simply be wider than the nine papers behind the
109. That would make the count right and the total's provenance wrong, which
is still worth knowing before A2 is treated as arithmetic.

---

## What this changes

```text
conversion_artifact   definable now, and NOT the X-08 forward reference. The
                      first reading here took class 4's three cases instead of
                      class 5's, and confirmed a guess it should have refuted.
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
