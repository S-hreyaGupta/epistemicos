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

The one thing they do not have is a heading. Mathpix emitted none. §3 locates
the reference section by heading, finds nothing matching, and refuses the whole
document.

For comparison, the heading immediately before each block:

```text
17bef7c6   ## 10. Conclusion, limitations, and scope for future research
2af68a7f   ## 6. Implications and recommendations of the study
bf2fdc4a   ## 6. Further developments
ed6a890a   ### 5.3. Future Directions

ad1e3ff9   ## REFERENCES          <- the working control
```

One line of markdown is the whole difference.

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

The change belongs in §3: when no heading matches, is a structural fallback
permitted, and what is it. The signal is available and strong:

```text
a contiguous run of >= N lines matching ENTRY_START
in near-alphabetical order by first surname
in the last third of the document
```

The ordering is what makes it safe. The four papers run 95-100% ascending, and
so do the two papers that already work (99% and 94%) — so the test does not
distinguish "has a heading" from "does not", which is what you want from a
fallback. Body text does not do this.

**This needs a decision, not a repair.** Nothing has been changed.

## What this does not establish

That 582 is the right number. It is what the current extractor produces given a
boundary placed at the first entry-shaped line, and that boundary is a guess
which has not been checked against the PDFs. A few trailing body lines may have
been swept into the reference side, or the last paragraph of the conclusion may
have been.

Nor does it say the four papers are in profile. `c22df19f` reaches extraction
and still scores 30.5% because its style is ACL rather than APA, and nothing
here checks whether these four are APA beyond the shape of their reference
entries.

What it does establish is that the refusal is about a missing heading and not
about a missing bibliography, which is the thing three weeks of "four papers
exit 3" did not say.
