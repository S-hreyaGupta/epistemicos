# Four papers produce nothing, and their reference lists are right there

27% of the corpus has never been read. Diagnosed 18 September 2026.

Four of the fourteen papers abort at exit 3, "references section not found".
The August corpus runs recorded this and `PROVENANCE-GAP.md` lists it among the
findings independently reproduced on 18 September — *four papers exit 3, the
same four* — so it has been known for three weeks, reproduced twice, and never
once asked about.

It is not that these papers lack bibliographies.

## What they actually contain

```text
paper       reference entries   alphabetically ordered
17bef7c6           76                  75/75   100%
2af68a7f           58                  54/57    95%
bf2fdc4a           99                  98/98   100%
ed6a890a           70                  68/69    99%
```

Each is a single contiguous block of 11,000 to 21,000 characters, running
`Aggarwal, V.` to `Zhang, A.`, `Alvord, S.` to `Zahra, S.`, sitting where a
bibliography sits. They are complete, well-formed, and in APA order.

The one thing they do not have is a *heading*. The line immediately above the
first entry, in all four, is this:

```text
References
```

Plain text. No `#`, no `<h2>`, nothing `headings()` recognises. Mathpix wrote
the word and did not mark it up. §3 locates the section by heading, finds none
matching anywhere in the document, and refuses the whole paper.

```text
17bef7c6   'References'   HEAD_MD matches: False
2af68a7f   'References'   HEAD_MD matches: False
bf2fdc4a   'References'   HEAD_MD matches: False
ed6a890a   'References'   HEAD_MD matches: False

ad1e3ff9   '## REFERENCES'   matches                <- the working control
```

Two characters and a space is the whole difference.

**The first version of this file said the section was unlabelled and proposed a
structural fallback — a contiguous run of entry-shaped lines in near
alphabetical order.** That was over-engineered, and it was over-engineered
because of how the evidence was gathered: the check asked what the last
*heading* before the block was, and got "10. Conclusion, limitations, and scope
for future research". It never asked what the last *line* was. Looking at the
headings and not at the text is the same move that produced every other
correction recorded in this directory today.

## What is behind it

Inserting `## References` at the start of the block and running the real
splitter and extractor, everything else unchanged:

```text
paper       entries   parsed   unresolved
17bef7c6       76       101        19
2af68a7f       58       134        19
bf2fdc4a       99       161        10
ed6a890a       70       186        12
TOTAL                   582        60
```

```text
corpus today              1548 parsed, 10 of 14 papers
with these four read      2130 parsed, 14 of 14
locked behind a heading    582 citations, 27% of the total
```

They are not marginal papers. **They parse better than the corpus average** —
90.7% of candidates resolve against 87.9% across the ten that currently work.
The corpus has been measured, argued over and frozen into rc3's §I for six
weeks on 73% of itself, and the missing quarter is the easy quarter.

## Why this is not a repair

Adding a heading to the data would edit the corpus, and the corpus is evidence.
`PROVENANCE-GAP.md` establishes `data/md_full/` as byte-identical to what the
August runs read and to `papers.markdown` today, which is the only reason any
figure from August can be compared with any figure from now. Writing into it
would spend that.

The change belongs in §3, and it is smaller than the first version of this file
proposed: whether a standalone line whose entire content is a reference-section
name counts as a section boundary when no marked-up heading does.

That is a narrower rule than a structural fallback, and it is testable against
the thing it would change — four documents where such a line exists and is
followed immediately by 58 to 99 reference entries.

The alphabetical-ordering signal is still worth recording as a second check,
because it is what distinguishes this line from the word "References" appearing
anywhere else:

```text
17bef7c6   76 entries   75/75 ascending   100%
2af68a7f   58 entries   54/57 ascending    95%
bf2fdc4a   99 entries   98/98 ascending   100%
ed6a890a   70 entries   68/69 ascending    99%

ad1e3ff9   89 entries   87/88 ascending    99%   <- already works
c1d56945   84 entries   78/83 ascending    94%   <- already works
```

The papers that already work score the same, so the test does not distinguish
"has a heading" from "does not", which is what a confirmation check needs.

**This needs a decision, not a repair.** Nothing has been changed.

## Two caveats this file carried, both since closed

**Was the boundary a guess?** It was described as one. It is not: the cut lands
directly after a line reading `References` and directly before the first
entry, in all four. Checked by reading the lines on either side.

**Are the four in the APA profile, or out of it like `c22df19f`?** In it, and
the discriminator is mechanical rather than a judgement. APA writes a comma
before the year and ACL author-date does not:

```text
paper       (Smith, 2020)   (Smith 2020)   comma-less share
17bef7c6         75              0                0%
2af68a7f         48              1                2%
bf2fdc4a         73              0                0%
ed6a890a         99              0                0%

c22df19f          0             73              100%   <- the out-of-profile one
ad1e3ff9        104              2                2%   <- gold paper
c1d56945        145              1                1%   <- gold paper
```

Complete separation. The four sit with the gold papers; `c22df19f` is alone.

Worth noting that §10's exit 2, the style guard, does **not** catch
`c22df19f` — it tests for numeric and superscript citations, and that paper has
none of either. Its 30.5% score is comma-less author-date, which nothing in the
implementation currently detects. The August classification of it as "out of
`apa7_like_v1`" was a human reading the report, not a check. The table above is
the first mechanical version of that judgement, and it is a by-product of this
investigation rather than its object.

## What this still does not establish

That 582 is the right number in detail. It is what the current extractor
produces on these four, and no gold set exists for any of them, so the figure
has the same standing as the corpus counts did before the two gold sets: a
parse count, not an accuracy.

What it does establish is that the refusal is about markup and not about a
missing bibliography, which is the thing three weeks of "four papers exit 3"
did not say.
