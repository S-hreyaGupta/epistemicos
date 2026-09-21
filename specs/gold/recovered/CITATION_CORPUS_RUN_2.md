# Citation corpus run 2 — after `\&` and segment splitting

**Method:** the v3.3 reference implementation with two changes applied — `\&` → `&`
at source, and B4 independent semicolon-segment parsing inside parentheses.
Re-run against every converted paper. Offline. 28 August 2026.

**This is Alex's point 4:** measure before building anything else.

---

## Result

**Six papers**, the in-profile ones that actually reconcile:

```text
                          citations                 references
baseline           611/769  =  79.5%         354/383  =  92.4%
\& + B4 segments   803/871  =  92.2%         354/383  =  92.4%
```

```text
absolute citations parsed   611 → 803   (+192)
```

**92.2% against a 95% target. The remaining gap is 68 citations.**

### Per paper

```text
paper       citations            references
──────────────────────────────────────────────────────
43338825    102/123 → 107/130     56/63    88.9%
5da73cf4     13/62  → 125/125     24/26    92.3%
849f8fc6     40/61  →  65/71      60/64    93.8%
ad1e3ff9    177/186 → 180/189     92/106   86.8%
c1d56945    205/230 → 218/244     84/85    98.8%
ea07e5f5     74/107 → 108/112     38/39    97.4%

c22df19f     47/151 →  47/179      0/121   ← out of profile, excluded
17bef7c6 · 2af68a7f · bf2fdc4a · ed6a890a  → exit 3, no output
```

---

## Methodological warning — B4 moves the denominator

**Percentages before and after B4 are not directly comparable.**

```text
denominator   769 → 871   (+102)
```

Splitting one failed parenthetical group into three failed segments turns one
`unresolved_citation` into three. So the count of failures rises even where
nothing got worse, and **a percentage can fall while parsed citations rise**:

```text
43338825    102/123  82.9%   →   107/130  82.3%
                     +5 parsed, and the rate went DOWN
c22df19f     47/151  31.1%   →    47/179  26.3%
                     nothing gained, denominator grew
```

Both are improvements in information — a group that failed for one reason now
reports which of its segments failed — but neither is an accuracy regression.

> **Whatever accuracy target is set, fix the denominator definition first.**
> "Citations parsed / citation-like occurrences detected" changes meaning the
> moment detection granularity changes, and B4 changes it. Absolute parsed count
> is the stable measure across this change; the rate is not.

---

## The remaining 68, ranked

Alex's plan: rank the residual by frequency, fix only what crosses the threshold.
Here it is.

```text
 46   67.6%  other
  9   13.2%  lead-in phrases          → B5, already specified
  5    7.4%  URL / image spans        → A3, already specified
  4    5.9%  bare year                → narrative author not captured
  2    2.9%  math / LaTeX spans       → A3 widened
  2    2.9%  all_caps_surname         → already a registered limitation
```

**The math/LaTeX group collapsed from 96 to 2.** Most of those 96 were not
independent failures at all — they were whole parentheses destroyed by one bad
element, and B4 dissolved them. That is a real finding about the first corpus
report: **failure-class counts taken before segment splitting overstate every
class**, because one bad token was inflating its neighbours into the same bucket.

So A3's widening to cover math and code spans is worth doing, and it is worth
roughly 2 citations rather than 96. The measurement had to come first, which is
exactly Alex's argument.

**B5 and A3 together are 14 of the 68.** Applying both takes the six papers from
92.2% to roughly 93.8%. **Neither reaches 95% on its own or together.**

### The 46 in "other" are where the target lives

Two shapes dominate, and both are real citations the profile could reasonably
claim:

```text
(conservation of resource theory, Hobfoll, 1989, and ego-depletion, Baumeister…)
    → prose-with-embedded-citation. The segment carries a theory name before
      the author. Not a lead-in cue, so B5 does not cover it.

(cp. Skogstad et al., 2014)
    → `cp.` is a citation cue that PREFIX does not contain.
      PREFIX has e.g. / i.e. / cf. / see also / see / but see.
```

The second is a one-token fix to a closed set and it is the cheapest remaining
win. The first is a genuine grammar question and should probably be a registered
limitation rather than an MVP fix.

---

## What this changes about the plan

**Points 1, 2 and 3 are done and measured.** 79.5% → 92.2%, and the denominator
caveat above is the only asterisk.

**Point 5 is smaller than it looked.** Math and code exclusion is worth 2
citations post-B4, not 96. Still worth doing, no longer urgent.

**The deferral calls are right, and now provably so.** The `no_grammar_match`
split does not recover citations — this run recovered 192 without touching it.
And no annotation framework was needed for either fix: one substitution and one
parser change.

**One thing the deferral does not cover.** `\&` → `&` is a *transformation*, not
an *exclusion*, and the two behave differently under M's byte-offset invariant:

```text
exclusion    does not change bytes    → safe at any stage
substitution changes bytes            → every downstream offset shifts
```

810 occurrences, one byte shorter each. Applied after canonical bytes are fixed,
every citation offset in the document is wrong and nothing errors. So the `\&`
fix MUST happen **before canonicalisation**, in ingest, producing the canonical
bytes — or be an annotation the parser honours without rewriting.

"Normalize/annotate before Citation sees the text" covers both, and only one of
them is safe.

---

## Reproducing

```bash
sed 's/\\&/\&/g' data/md/<paper>.md > /tmp/in.md
python3 impl_v34.py /tmp/in.md > out.jsonl
```

`impl_v34.py` is the v3.3 reference implementation plus the B4 segment-splitting
branch. Raw output for all eleven papers retained.
