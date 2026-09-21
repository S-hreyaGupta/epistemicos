# The 46 "other" — decomposed

Alex's point 5: *investigate the 46 first, they are ~68% of the remaining
failures.* Here they are, every one, classified and counted. 28 August 2026.

**Nothing here is projected.** These are the actual unresolved citation texts
from run 2, on the six in-profile reconciling papers.

---

## Distribution

```text
 6   13.0%   D  narrative fragment, author split across the candidate boundary
 5   10.9%   A  cp. cue not in PREFIX
 5   10.9%   B  et-al punctuation variants
 5   10.9%   G  wrong segment separator
 5   10.9%   K  particle capitalisation
 5   10.9%   M  residual, genuinely different from each other
 4    8.7%   F  forename-first / journal name in line
 4    8.7%   H  institutional author
 2    4.3%   C  compact year-suffix 2019a,b
 2    4.3%   E  bare locator
 2    4.3%   J  missing comma before year
 1    2.2%   I  multi-year, no author
 46          TOTAL
```

**No single class is more than 13%.** The 46 are a long tail, not one missing
rule. That matters for the plan: there is no single fix in here that moves 92.2%
materially, and the sum of the four cheapest is 14 of 46.

---

## A — `cp.` — **exactly 5 occurrences**, answering the count question

```text
(cp. Skogstad et al., 2014)
(cp. Schyns and Schilling, 2013)
(cp. Liu et al., 2012)
(cp. Martinko et al., 2013)
cp. Weiner, 1986
```

All five are real citations in one paper's prose, all APA-shaped, all failing only
because `cp.` is absent from the closed PREFIX set (`e.g. / i.e. / cf. / see also
/ see / but see`).

**Worth 5 citations for one token in a closed set plus one golden.** That is the
cheapest fix on the board and it is measured, not projected.

Note all five come from a single paper. It is a house-style cue rather than a
general APA one, which is an argument for adding it and for expecting more cues
like it on unseen papers.

---

## The classes that are cheap and closed

**C — compact year-suffix, 2** — `(Sharma et al., 2019a,b)`. Already specified as
B6. Deterministic expansion to `2019a` + `2019b`.

**B — et-al punctuation, 5** — `(Choi at al., 2001)`, `Whiteman et al, 2013`,
`Slawinski, et al., 2021`, `Garrett et al, 2017`, `Esquivel, et al 2021`. Three
distinct deviations: `at al.` for `et al.`, missing full stop, comma before
`et al.` These are author typos and OCR noise, not grammar gaps. Tolerating them
means loosening a closed grammar to accept malformed input, which is a
**registered-limitation candidate rather than an MVP fix**.

**E — bare locator, 2** — `p.56`, `P.923`. Detached page references picked up as
candidates. Belongs with A3's exclusion work, not the author grammar.

**J — missing comma before year, 2** — `(Lu and Shang 2017)`,
`(University of Pretoria 2021a)`. One-character author omission.

**I — multi-year no author, 1** — `(2011, 2012, and 2013)`. A continuation of a
narrative citation whose author sits outside the candidate.

---

## The classes that are *not* cheap

**D — narrative fragment, 6, the largest class.** The author is split across the
candidate boundary:

```text
and Sauer and Seuring (2023)
and Pagell and Wu (2009)
and Müller (2008)
Additionally, Oliviera da Silva et al. (2023)
and Fotiadis's (2018)
Carrieri Souza
```

These are the *second* author of a coordinated pair — "X (2020) and Y (2021)" —
where the run stops at `and`. Fixing it means the candidate walk crossing a
coordinating conjunction, which is exactly the overcapture territory the
six-token cap used to guard. **Not an MVP fix**, and it interacts with B4.

**K — particle capitalisation, 5.** `Carrieri de Souza et al., 2023`,
`(Da silva et al., 2017)`, `(Oliveira da Silva et al., 2024)`. Portuguese and
Spanish surnames with internal particles. §4's `PARTICLE` list has `da`, `de`,
`di` — so these should parse. The failures are **case**: `Da silva` capitalises
the particle and lowercases the core, inverting what `SURNAME` expects. Worth
investigating properly; it may be a small fix to particle case-folding rather
than a limitation, and 5 occurrences in one paper suggests a whole corpus of
Lusophone author names would fare badly.

**F — forename-first with journal in line, 4.** `César Martínez Morán & Gisela
Delfino (2023)`, `Gisela Delfino, Cogent Business & Management (2023)`. Already a
registered limitation under X-07. Confirms the registration was right.

**H — institutional author, 4.** `(International Monetary Fund, 2022)`,
`(Population Pyramid, 2022)`, `(National Statistical Institute, 2022)`,
`(Ellen MacArthur, 2024)`. **These are the C-series non-person author case, which
v3.4 already specifies and the v3.3 reference implementation does not have.** So
4 of the 46 are already fixed by work that is agreed but unimplemented — they
should not be counted as an open gap.

**G — wrong separator, 5.** `(da Silva et al., 2024: Wezel et al., 2016)` uses a
colon where APA wants a semicolon; `Resque et al., 2019, Sam, 2018` uses a comma.
Author error. Registered-limitation candidate.

---

## What this changes about the path to 95%

```text
already fixed by agreed v3.4 work, not yet implemented
    H  institutional authors        4
    C  compact year-suffix          2
                                    6

cheap and closed
    A  cp.                          5
    J  missing comma                2
                                    7

with the other agreed fixes
    B5 lead-in                      9
    A3 URL / image                  5
                                   14

────────────────────────────────────────
recoverable without new grammar work    27 of 68
```

**27 of 68 clears to roughly 95.3% on the six-paper set.** That is the first
version of this number that rests on counted cases rather than projection —
though it still uses the unstable denominator, so it is indicative until the gold
set exists.

**The remaining 41 divide cleanly:**

```text
registered limitations   B (5) + G (5) + F (4)  = 14   author error / out of profile
genuine grammar work     D (6) + K (5)          = 11   coordinated authors, particles
long tail                M (5) + E (2) + I (1)  =  8
```

**So the honest reading is that 95% is reachable without new grammar**, if the
14 registered-limitation cases are accepted as limitations rather than counted as
failures — which is precisely the decision §9 of the register exists to make, and
this run is the evidence that lets it be made before freeze.

---

## Provenance

```text
implementation
  impl_v34.py            50077031db923e2b80eb86add2cf1967afc8222de569fd6258b99dc8c0846628
  spec33_reference_impl  952c6bd820b41722dfeee453b77ebc2d73dac0966fd857f4dfc0cafd304962be

runtime
  python 3.10.12, regex 2026.7.19

corpus inputs (raw markdown, before the \& transform), sha256 first 32:
  17bef7c6  5fd6328b341d6cc2f1da60833a0932bb
  2af68a7f  1ed96cb5189441114e7d2aa919a5066e
  43338825  4ff6aa64ee8c4556e0d63d1de98f487c
  5da73cf4  1a62293ec8b5b31e0b0101055c780227
  849f8fc6  5b1eda63829cf6585c896b011ba29f55
  ad1e3ff9  cff9bb85d74fbac8ffd69fd0c258812c
  bf2fdc4a  59f2a7337b97cf7b3641f10d62682f53
  c1d56945  48b2b2f459e5cad88b7105048a0d7e0f
  c22df19f  de75e3591a46663a295bd2fd70f0a10b
  ea07e5f5  c43e5e1161ebccfda9b11f096a980d8c
  ed6a890a  0265812f086b6d4ce09348dd519c97fa

run-2 outputs, sha256 first 32:
  43338825  d223fc5bf44d45a8f7ce75e08babd011
  5da73cf4  36ffd1922c189763cdcbde58f1428c01
  849f8fc6  462dabbaf64b0ba6c43ed8f9b1b26895
  ad1e3ff9  a425d639fda64241cae90c85cef4b955
  c1d56945  8a9d9d5bcb8902ee4c6dde2cb08e43c5
  c22df19f  e090a8550482454a3f85dfdb9d649b95
  ea07e5f5  c2da4a8dec1a4e44e24ecf083d5af3d1

  17bef7c6 · 2af68a7f · bf2fdc4a · ed6a890a
            ced72346241f2815636597fffc2d8dee   ← identical: all four are the
                                                 same two-line exit-3 output
```

**The four exit-3 papers share one output hash**, which is itself the finding: the
tool produces byte-identical nothing for 4 of 11 papers. Those four must be re-run
under v3.4's `bibliography_absent` behaviour before the corpus evidence is
complete, and the reference implementation does not have it yet.
