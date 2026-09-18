# Paper 2's missed works, adjudicated

Paper 1's problem was precision, and `ADJUDICATION-paper-1.md` found that none
of its eleven extras was a grammar error. Paper 2's problem is the other side:
recall 0.873 against Alex Zamurko's 0.95, and fifteen works in the gold set that
the candidate did not produce.

Adjudicated 18 September 2026 against `c1d56945`. Two of the fifteen were
repaired the same day by the particle fix, so thirteen remain, and every one has
been located verbatim in the manuscript before being classified.

The question this answers is the one the count cannot: is the extractor failing,
or is it refusing things it was told to refuse.

## The thirteen, by cause

### Refused as the specification requires — 3

```text
FAO, 2005                       all_caps_surname
FAO, 2018                       all_caps_surname
(Ellen MacArthur, 2024)         forename-first, so not a SURNAME YEAR form
```

§12 states both refusals as expected behaviour: `(OECD, 2024)` is
`all_caps_surname` because it "is asserted for no one", and forename-first is
unresolved rather than a citation. All three are institutional authors, which is
the class rc3 exists for, and the reference list confirms it —
`Ellen MacArthur Foundation (EMF)., 2024.`

So these are not extractor failures. They are the specification working, against
a gold set that annotated the works anyway. Which of the two should change is a
question for rc3 and not for this file.

### EC-4, a particle inside the surname — 3

```text
(Carrieri de Souza et al., 2023)
(Oliveira da Silva et al., 2024)
Oliviera da Silva et al. (2023)
```

`SURNAME = (PARTICLE WS)* CORE` puts particles ahead of a single CORE. These are
CORE PARTICLE CORE, outside the production's shape. Recorded as EC-4 in
`CITATION-EDGE-CASES.md`; it needs a grammar amendment, not a repair.

The third also carries a source typo, `Oliviera` for `Oliveira`, so the gold set
holds both spellings as separate works. That is faithful annotation of what the
manuscript says and worth leaving alone.

### EC-1, the coordinated "and" — 1

```text
... Durach et al. (2017) and Sauer and Seuring (2023), further aligned ...
```

Both occurrences of this work are coordinated, so the work is lost entirely.
This is the single instance behind EC-1's "1 of 15" cost, and the arithmetic
there still holds.

### The manuscript is malformed — 4

```text
(Bisht, 2019, Speich)                            a bare word inside the group
(Da silva et al., 2017)                          lower-case core
(da Silva et al., 2024: Wezel et al., 2016)      colon where a semicolon belongs
(Levidow, 2023; Resque et al., 2019, Sam, 2018)  comma where a semicolon belongs
```

Each is a departure from the style the grammar implements, in the source rather
than in the extractor. The fourth is the clearest: two of its three works are
separated by `;` and parse, and the third is separated by `,` and does not.

The colon case is worth noting because the extractor gets it right for the right
reason. The colon correction admits `(Kunda, 1990: 480)` by requiring a digit
after the colon, so it declines to fire before `Wezel` — and
`test_citation_extract.py` carries exactly that control, "colon flag does not
swallow a following author". The group then fails as a whole, which §6.2 says it
should.

### `et al` without the period — 2

```text
(Garrett et al, 2017; Macfadyen et al., 2015)
(Guthey et al., 2014; Whiteman et al, 2013)
```

Both occurrences sit beside a correctly punctuated `et al.` in the same group,
so the manuscript is inconsistent with itself rather than following another
convention. §4 spells the production `et WS al\.` and the period is load-bearing.

Two works, one paper. Whether to widen the grammar for a typo this common is a
judgement, and the pairing above is the argument on both sides: the neighbouring
segment parses, so a reader has no trouble, and neither would a looser rule.

## What the misses come to

```text
3    specification working as written, against institutional authors
3    EC-4, grammar shape
1    EC-1, known
4    malformed source
2    missing period in et al.
```

**None of the thirteen is an implementation defect.** Nothing here mis-parses a
well-formed citation, invents one, or keys the wrong surname. That is the same
finding as paper 1 arrived at from the opposite direction, and two papers
agreeing is the reason it is worth writing down.

What it does not mean is that recall of 0.873 is acceptable. Six of the thirteen
— the institutional three and EC-4's three — are works a reader would expect a
citation extractor to find, and the fact that they are refused by rule rather
than missed by accident does not put them in the output.

## The eleven extras: one cause, and it is in the measuring apparatus

Adjudicated after the misses, and the result is not like paper 1's.

**Every one of paper 2's eleven extras is the same work as a gold item, under a
different author phrase.** Not one is a citation the extractor invented.

```text
candidate                 gold                              why they differ
de freitas et al. 2017    de freitas 2017                   et al. present in one
de santana 2023           de santana et al. 2023            et al. present in one
duru et al. 2015          duru, therond, and fares 2015     et al. vs the full list
garrett 2017              garrett et al 2017                et al. present in one
lanka 2017                lanka et al. 2017                 et al. present in one
levidow 2023              levidow et al. 2023               et al. present in one
macfadyen 2015            macfadyen et al. 2015             et al., and MacFadyen vs Macfadyen
resque 2019               resque et al. 2019                et al. present in one
roth and zeng 2021        roth and zheng 2021               Zeng/Zheng, a source typo
sancha et al. 2015        sancha, longoni and giménez 2015  et al. vs the full list
sanz-cañada 2023          sanz-cañada et al. 2023           et al. present in one
```

Ten works in this paper are cited under more than one phrase, and `macfadyen`
under three. Ten works, eleven surplus entries.

### Why that produces extras

`citation_candidate.py` collapses the extractor's per-occurrence output to
works before scoring, and the key it collapses on is `(author_phrase, year)`.
The document it writes declares `"unit": "distinct cited work"` and a field
called `"distinct_works"`.

It is not counting distinct works. It is counting distinct phrasings, and a
manuscript that writes `(Duru et al., 2015)` in one paragraph and
`Duru, Therond, and Fares (2015)` in another contributes two. One matches the
annotation and the other is a false positive, so the extractor is penalised for
the manuscript varying its own wording.

The label and the number disagree, which is the defect this layer keeps finding
in itself, here in the instrument rather than in what it measures.

### What collapsing by work is worth, measured

Grouping occurrences by the work and accepting a match on any phrase observed
for it:

```text
                       items   matched   precision
paper 2  by phrase      100       89       0.890
paper 2  by work         90       89       0.989

paper 1  by phrase       97       90       0.928
paper 1  by work         96       89       0.927
```

Paper 2's precision is almost entirely this. Recall does not move on either
paper, which is the expected shape: nothing new is found, duplicate entries
stop being counted against it.

### Paper 1's single lost match is a gold-set duplicate

Collapsing costs paper 1 one match, and that one is worth following.
`ostrom|2003` is cited two ways, and **gold holds both as separate works**:

```text
(Gould, 1993; Ostrom and Walker, 2003)   the work as the bibliography gives it
(Ostrom, 1990, 2003)                     a multi-year group, where the
                                         manuscript attributes the 2003 work
                                         to Ostrom alone
```

Both quoted as whole groups, because a segment is not a string you can find in
the source. Writing `(Ostrom and Walker, 2003)` here would have been the third
time today that a segment got quoted as though it stood alone — the gold
builder refused its own input over the same mistake an hour earlier, which is
why these were checked rather than transcribed.

The bibliography has one 2003 Ostrom entry —
`Ostrom, E., & Walker, J. (Eds.). (2003)` — so there is one work, recorded
twice. The annotation was faithful to what the manuscript says, and
`author_phrase + year` cannot express that two spellings are one work.

Across both gold sets this happens once: paper 1 has 96 items and 95 distinct
first-surname-and-year pairs, paper 2 has 102 and 102. So the annotation is
nearly free of it, and the splitting is on the candidate's side, because the
candidate sees every occurrence and the annotator wrote one line per work.

### Why this is recorded and not repaired

Collapsing by work means collapsing on `citation_key`, and
`citation_candidate.py` avoids that deliberately and says so: *deriving a
surname from a phrase is the grammar under test, and scoring against a gold set
built from the same derivation would agree by construction on exactly the cases
rc3 exists to fix.*

That objection is about scoring rather than grouping, and matching would stay on
`author_phrase`. But it is not empty: EC-3 shows the key can be wrong, and a
wrong key groups wrongly. Reversing a considered decision in the instrument that
produces the numbers everyone is arguing about is a decision for whoever owns
the criteria.

**Needs a decision, not a repair.** Nothing has been changed.

## What this does not establish

The classification is of causes, not of correctness. Saying a refusal is
specification-conformant is not saying the specification is right; three of the
thirteen are institutional authors that rc3 was written to handle, and that work
is not done here.

And the same limit applies as in paper 1: these thirteen are the works the gold
annotation happened to contain. A work neither annotated nor extracted appears
in neither list and is invisible to this exercise.
