# Citation v3.3 — eleven-paper corpus run

**Method:** the v3.3 reference implementation, run offline against every converted
paper in `data/md`. No database, no Mathpix, no network. 28 August 2026.

**What this answers:** "is most of it working, and what can we accept as a known
limitation?" — with measurements instead of estimates.

---

## Headline

```text
                citations parsed        references parsed
as-is             658 / 920  71.5%        354 / 504  70.2%
one-char fix      829 / 998  83.1%        354 / 504  70.2%
```

**The single largest defect in the citation pipeline is not in the citation
specification.** It is that Mathpix emits `\&` where the manuscript has `&`, and
the grammar matches `&`. Replacing that one escape recovers **171 citations**
across three papers.

It is a conversion artifact, exactly the class Alex specified as
`ConversionArtifactAnnotations` for the glued footnote marker — and it is roughly
two orders of magnitude more consequential than the case that motivated it.

---

## Per paper

```text
paper       exit   citations parsed              references parsed
─────────────────────────────────────────────────────────────────────
43338825      1    102/123   82.9%                56/63    88.9%
5da73cf4      1     13/62    21.0%  → 100.0%      24/26    92.3%
849f8fc6      1     40/61    65.6%  →  91.5%      60/64    93.8%
ad1e3ff9      1    177/186   95.2%                92/106   86.8%
c1d56945      1    205/230   89.1%                84/85    98.8%
c22df19f      1     47/151   31.1%                 0/121    0.0%
ea07e5f5      1     74/107   69.2%  →  96.4%      38/39    97.4%

17bef7c6      3    references section not found — no output
2af68a7f      3    references section not found — no output
bf2fdc4a      3    references section not found — no output
ed6a890a      3    references section not found — no output
```

`→` is the figure after replacing `\&` with `&`.

**Four of eleven papers produce nothing at all.** This confirms the figure that
has been quoted from a 21 August estimate ever since; it is now measured. §3.3's
`Absent → exit 3` is the single biggest coverage gap, and addition 0 /
`bibliography_absent` is the fix already specified for it.

---

## Finding 1 — `\&` is the dominant citation failure

Mathpix LaTeX-escapes ampersands. 810 occurrences across the eleven papers.

```text
(Lawrence \& Lorsch, 1967; Galbraith, 1974, 1977; Tushman \& Nadler, 1978)
(Simon, 1947; March \& Simon, 1958)
(Aghion \& Tirole, 1997; Dobrajska et al., 2015)
```

`AUTHORS_PAREN` matches `(?:&|and)`. A backslash before the ampersand fails the
whole segment, and because a parenthetical group is currently atomic, **one
escaped ampersand destroys every citation in that parenthesis**, including the
ones that would have parsed.

That interaction is why 5da73cf4 sat at 21%: it is not that most of its citations
are unusual, it is that most of its parentheses contain at least one `\&`.

```text
95 of 262 unresolved citations (36.3%) contain \&
+171 citations recovered by  sed 's/\\&/\&/g'
5da73cf4 reaches 100.0%
```

**Where the fix belongs.** Not in the citation grammar. Adding `\\&` as an
alternative would put a converter's escaping convention inside a citation-style
specification, and the next converter escapes something else. It belongs in the
conversion-artifact annotation layer, alongside `glued_footnote_marker`.

Note the interaction with the segment-splitting change already agreed (B4,
parse `;`-separated segments independently). That change alone would also recover
much of this, because a single bad segment would stop destroying its neighbours.
The two fixes are complementary and neither is a substitute for the other.

---

## Finding 2 — c22df19f is out of profile, and that is correct behaviour

Zero of 121 references parsed. Not a defect:

```text
[Afantenos and Asher2014]Afantenos, Stergos and Nicholas Asher. 2014. ...
[Aharoni et al.2014]Aharoni, Ehud, Anatoly Polnarov, Tamar Lavee, ...
[Beardsley1950]Beardsley, Monroe C. 1950. Practical Logic. Prentice-Hall.
```

Bracketed author-year keys, forename-first author lists, year after the author
block rather than in parentheses. This is ACL/computational-linguistics style,
not APA. `apa7_like_v1` does not cover it and should not pretend to.

**This is a registered limitation, not a bug**, and it is the clearest possible
argument for the profile mechanism. It should be named in register §9 explicitly,
because "0 of 121" in a corpus report otherwise reads as a catastrophic failure
rather than a correct out-of-profile refusal.

It also means the corpus is 10 papers for APA purposes, not 11 — worth stating
wherever corpus-wide percentages are quoted.

---

## Finding 3 — failure classes, measured

```text
unresolved_citation  reasons          unresolved_reference reasons
──────────────────────────────        ───────────────────────────────
260   99.2%  no_grammar_match         140   93.3%  orphan_line
  2    0.8%  all_caps_surname          10    6.7%  entry_start_grammar
```

`no_grammar_match` carrying 99% of citation failures means the reason enum is
not currently diagnostic. Breaking the 260 down by inspection:

```text
146   56.2%  other  (dominated by \& — see finding 1)
 96   36.9%  math / LaTeX spans
 10    3.8%  lead-in phrases outside PREFIX
  5    1.9%  markdown image / URL spans
  3    1.2%  bare (YEAR) with the narrative author not captured
```

Three of these five already have agreed fixes: A3 excludes URL and image spans,
B5 adds the bounded lead-in with a closed CUE set, and the `\&` case belongs to
the annotation layer.

**The math/LaTeX group is the one with no agreed fix.** 96 occurrences —
inline `$...$` and `\alpha=0.96` spans producing year-like tokens. A3's
exclusion-span rule should cover code and math spans as well as URLs; as written
it names markdown link and image destinations only.

**And `no_grammar_match` should be split.** A single reason covering 99% of
failures cannot support the limitation register, because you cannot pre-register
a limitation you cannot name. Minimum useful split: excluded-structure,
unsupported-lead-in, conversion-artifact, out-of-profile-form, genuine-no-match.

---

## What this means for the freeze

**Working, and better than the record suggested.** On the seven papers that
reconcile, citation parsing is 71.5% as-is and 83.1% once one converter escape is
handled. Four of the remaining failure classes already have specified fixes.

**Acceptable as registered limitations:**

```text
c22df19f-style bracketed-key bibliographies   → out of apa7_like_v1
all-caps surnames                              → already registered, 2 occurrences
orphan_line reference fragments                → 140, mostly wrapped-line artifacts
```

**Not acceptable as limitations, because they are specified fixes not yet
applied:**

```text
references section absent          4 of 11 papers  → addition 0
\& conversion escape               171 citations   → annotation layer
math/LaTeX spans                    96 citations   → A3, needs widening
lead-in phrases                     10 citations   → B5
```

**The register consequence.** §9 forbids inventing a limitation after a corpus
run to reclassify a blocker. This run is the corpus evidence, and it was produced
before freeze — so everything above is registrable now. That is the window
closing, not a hypothetical.

---

## Reproducing

```bash
python3 spec33_reference_impl.py data/md/<paper>.md > out.jsonl
```

Offline. Eleven papers, no database, no provider call. Raw output for every
paper retained alongside this document.
