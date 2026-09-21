# rc1 specifies four capabilities, and none of them are built

Found 21 September 2026, while searching for rc2. Shreya Gupta asked to see the
PowerShell output before a reply went out, and the listing carried a file nobody
here had read.

## What turned up

```text
CITATI_3.MD        21 Aug 16:29   274 lines   55fcc7b8…   first draft
CITATI_3 (2).MD    21 Aug 17:21   332 lines   0c93ee9c…   revision, 52 min later
```

Both titled `# Citation spec v3.3 → v3.4 — the three additions`. Another
Windows-truncated filename, the same reason rc3 went unfound for two weeks. It
did not appear in the content search run earlier the same day because it has no
front matter and never uses the string `NON_PERSON_AUTHOR`.

**It is not rc2.** It predates rc1 by six days and is one document, not four. It
is the scoping note that rc1 was written from: three requested additions plus a
blocker discovered while sizing them.

Both copies are kept. The revision corrects a real design decision and the
correction is worth having, since it is the same one this repository would have
had to make again.

## Why it matters anyway

rc1 has been discussed here as "the architecture split" — §2's three clauses
about identity not being extraction's to create. That is the part that conflicts
with v3.3, so it is the part that got attention.

It is not the whole of rc1. Checking every identifier this note introduces
against the four rc1 files:

```text
identifier                  rc1   v3.3   rc3   implemented
references_source            4      0      0        no
author_form                  1      0      1        no
visible_authors              1      0      0        no
ET_AL_MIN_AUTHORS            2      0      0        no
author_count_constraint      1      0      0        no
sentence_index               2      0      0        no
previous_sentence_end        2      0      0        no
author_structure_mismatch    1      0      0        no
```

**rc1 absorbed all of it.** So this note is superseded as a specification, and
what it establishes is scope: rc1 carries four capabilities beyond the
architecture split, and none of them exist in `scripts/citation_extract.py`.

```text
0  references-section fallback, with `references_source: heading | inferred`
1  sentence-relative positioning: sentence_index, previous_sentence_end,
   standalone
2  file output contract: --out, atomic write, content-derived default name,
   completeness marker, determinism extended to the file
3  author-structure agreement, which is the one with a live defect behind it
```

## Amendment 0 was solved here independently, and differently

The note's §0 names the blocker this repository rediscovered on 18 September:
four papers of eleven exit 3 because Mathpix wrote `References` as body text
rather than as a heading. It names the same four.

```text
17bef7c6   2af68a7f   bf2fdc4a   ed6a890a
```

The two solutions differ, and neither is obviously right:

```text
                        21 August note          implemented 18 September
confirmation            >= 3 of the next 10     >= 5 entries below the label
                        lines match ENTRY_START
ordering check          none                    >= 80% ascending by surname
records how it was      references_source       nothing
found                   ∈ {heading, inferred}
```

The implemented rule is stricter on count and adds an ordering test the note
does not have. The note carries something the implementation does not: a record
in `meta` of *which* rule found the section. That distinction is worth keeping
whichever threshold wins, because a bibliography located by fallback is a weaker
premise than one the document marked, and a downstream absence claim resting on
it should be able to say so.

## Amendment 3 has a live defect behind it, measured

This is the one that is not merely unbuilt. From the note:

> `Smith et al. (2020)` asserts a work with three or more authors. Its key is
> `smith|2020`. A reference reading `Smith, J. (2020). …` has the identical key
> and matches cleanly. Two different works, and nothing in the output says so.

That is exactly what this implementation does today. §8 reconciles on
`surname|year` and discards everything else the in-text form asserts.

Measured against the current corpus, 21 September:

```text
citations                                          2094
carrying `et al.` or `and colleagues`               790   37.7%
of those, matched to a reference declaring
    fewer than three authors                          6
```

The six, with the reference each matched:

```text
43338825  felfe|2006       Felfe et al.              Felfe, J., and Schyns, B.
4918fd7d  hülsheger|2015   Hülsheger et al.          Hülsheger, U. R.
ad1e3ff9  chen|2018   ×2   Chen et al.               Chen, S., Zhang, Q and Zhou, Y.
c1d56945  mamine|2020      Mamine et al.             Mamine, F., Farès, M.
e1b418a4  colquitt|2012    Colquitt and colleagues   Colquitt, J. A.
```

**Not yet adjudicated, and at least one is the measuring rule's own fault.**
`Chen, S., Zhang, Q and Zhou, Y.` is three authors; the probe counted two
because `Zhang, Q` has no period after the initial. That is the same defect
class as everything else this milestone has been about, and it appeared in the
throwaway script written to measure the defect.

So the honest statement is six candidates requiring eyes, not six confirmed
false matches. The point stands either way and does not depend on the number:
**the check that would catch them does not exist**, so a wrong match and a right
one are indistinguishable in the output. Six in two thousand is small; six
silent wrong matches is not the same as six visible ones.

The note is also explicit that counting alone is insufficient, and gives the
case that settles it:

```text
Smith & Jones (2020)   vs   Smith, J., & Brown, K. (2020)
```

Two authors each side. The count agrees and the works differ. So the citation
has to carry the visible surnames **in order**, which is what the 52-minute
revision changed: the first draft specified `author_count` only, and the
revision replaced it with `author_form` + `visible_authors` +
`author_count_constraint`, collapsed three author forms to two, and pinned
`ET_AL_MIN_AUTHORS = 3` in §1 rather than leaving it to the implementation.

## What this does and does not change

It does not change the rc2 position. rc2 is still missing, this is not it, and
the searches recorded in `LINEAGE.md` stand.

It changes what "consolidation" means. The question had been framed as choosing
between v3.3's architecture and v3.4 §2's split. That is still the hard part,
but rc1 also carries four unbuilt capabilities, one of which is a correctness
gap in what runs today. A consolidated specification that resolved the
architecture question and left these unlisted would look complete and would not
be.

## What is worth doing, in order

```text
3  author-structure agreement   a live defect, 37.7% of citations carry the
                                form, and 6 candidate false matches found
0  references_source in meta    small, and the fallback already exists here;
                                only the provenance field is missing
1  sentence-relative fields     three derived fields, nothing new parsed
2  file output contract         --out and atomic write
```

None of the four is blocked on rc2.
