# The residual, decomposed over nine papers — and two fixes measured

Supersedes `CITATION_RESIDUAL_46_v2.md`, which decomposed six papers.
29 August 2026. Every number below is counted from run-3 output or produced by a
run performed for this document. Nothing is projected.

---

## First: 62 was never the residual

`CITATION_CORPUS_RUN_3.md` puts "gap to 95%" at 62 in a table beside run 2's 68.
Those are different quantities and should not sit in the same row.

```text
run 2   871 detected, 803 parsed    residual = 68     gap to 95% = 24
run 3  1611 detected, 1469 parsed   residual = 142    gap to 95% = 62
```

68 was a residual. 62 is a target distance. **The residual to decompose is 142**,
not 62 — a third larger than the previous decomposition, over three more papers.

The run-3 comparison table needs that row split in two before anything is frozen.

---

## The 142, classified

Twenty-two classes, zero unclassified. Classifier and its four explicit
judgement-call overrides are in `residual_classify.py`, so the counts are
re-derivable rather than asserted.

```text
  28   colon page-locator          (Kunda, 1990: 480)
  17   B5  lead-in cue             (for a review, see Sonnentag & Frese, 2003)
  16   bare year                   (2014)
  11   prose fragment              i.e., respect and dignity
   9   multi-token surname         Carrieri de Souza, El Akremi, Pircher Verdorfer
   8   A3  url / image span        mathpix cdn links
   8   et-al punctuation           Whiteman et al, 2013
   6   institutional author        (International Monetary Fund, 2022)
   6   coordinated narrative       and Pagell and Wu (2009)
   5   cp. cue                     (cp. Liu et al., 2012)
   4   forename-first / journal    Gisela Delfino, Cogent Business & Management (2023)
   4   wrong separator             (Bisht, 2019, Speich)
   3   math / LaTeX                \alpha=0.96
   3   artifact / non-citation     MBSR, McMindfulness, (ECP_150 03_08_2014_A2 OZL)
   3   possessive narrative        Robbins, Ford, and Tetrick's (2012: 250)
   2   missing comma before year   (Lu and Shang 2017)
   2   B6  compact year-suffix     (Sharma et al., 2019a,b)
   2   all-caps surname            (FAO, 2018)   ← reclassified, see correction 2
   2   bare locator                p.56
   1   prose-embedded citation     (conservation of resource theory, Hobfoll, 1989, …)
   1   particle case               (Da silva et al., 2017)
   1   non-numeric year            (Smith, Weed, & Ramsay, 2005-present)
 ─────
 142
```

### The largest class did not exist in the six-paper pass

**Colon page-locators are 28 of 142, and every one comes from a paper that was
not in the earlier corpus.**

```text
(Kunda, 1990: 480)
(Ambrose, Wo, & Griffith, 2015: 109)
(Sarchione, Cuttler, Muchinsky, & Nelson-Gray, 1998: 905)
```

These are ordinary, well-formed APA citations. The only thing the grammar cannot
read is `: 480` where it expects `, p. 480`:

```python
LOCATOR = r'(?:,' + WSO + r'(?:p\.|pp\.|para\.|chap\.)' + WSO + r'[^();]+)'
```

House style, two journals, entirely deterministic. This is the concrete cost of
having measured 11 files instead of 14 — the biggest single class in the residual
was invisible.

---

## Both cheap fixes, implemented and measured

Rather than project, I patched the implementation and re-ran all 14 papers.

```python
# colon locator — one alternative, digits required after the colon
LOCATOR = r'(?:(?:,' + WSO + r'(?:p\.|pp\.|para\.|chap\.)|:)' + WSO + r'\d[^();]*)'

# cp. — one token into the closed PREFIX set
PREFIX  = r'(?:(?:e\.g\.|i\.e\.|cf\.|cp\.|see also|see|but see)[, ]' + WSO + r')'
```

Nine in-profile reconciling papers:

```text
                    parsed / detected            residual   delta
run 3, \& + B4      1469 / 1611  =  91.2%          142        —
+ colon locator     1497 / 1611  =  92.9%          114       +28
+ cp.               1474 / 1611  =  91.5%          137        +5
+ both              1502 / 1611  =  93.2%          109       +33
```

**Each fix recovered exactly its class count. No more, no less.** 28 and 5,
against 28 and 5 predicted. Nothing else moved.

**The denominator does not move here.** Unlike B4, neither change alters
detection, so 91.2% → 93.2% is a like-for-like comparison and the caveat that
attaches to the B4 figures does not attach to this one.

```text
paper      before          after
43338825   107/130 82.3%   112/130 86.2%   +5
50408397   227/242 93.8%   235/242 97.1%   +8
e1b418a4   176/215 81.9%   196/215 91.2%  +20
                                          ───
                                          +33
```

`e1b418a4` was the worst paper in the corpus at 81.9%. Two closed-set changes,
neither invented for it, take it to 91.2%.

### Checked for the failure mode that matters

The colon rule requires a **digit** immediately after the colon. That is what
separates a locator from the wrong-separator case:

```text
(Proudfoot & Kay, 2014: 176)              → locator, digit follows
(da Silva et al., 2024: Wezel et al.…)    → separator error, capital follows
```

Verified against output, not argued:

```text
citations lost                                     0
previously-parsed keys that changed                0
new keys of the bank|2024 shape                    0
new keys inspected      weiner|1986, gond|2008, kunda|1990, batson|2009,
                        ambrose|2015, jones|2013, ganster|2001, geisler|2015,
                        appelhans|2006 …           all correct author|year
references              724/783 = 92.5%            unchanged
```

---

## The 109 that remain

**Corrected 29 August, both corrections Alex's.** An earlier version of this
section counted A3 as a recovery and left the two `FAO` cases as an all-caps
limitation. Both were wrong; see the two notes below the table.

```text
RECOVERIES — specified and agreed, not yet implemented
  17   B5  bounded lead-in
   2   B6  compact year-suffix
  19        these add to the numerator

BOUNDED NEW GRAMMAR — needs an rc3 decision
   9   multi-token surname     El Akremi, Pircher Verdorfer, Carrieri de Souza
   8   institutional citation extraction path   ← was 6, +2 FAO
   6   coordinated narrative   author after "and"
   1   possessive narrative
   1   particle case           Da silva
  25

REGISTERED LIMITATION CANDIDATES — malformed input or out of profile
   8   et-al punctuation
   4   wrong separator
   4   forename-first / in-line journal      → already X-07
   2   missing comma before year
   1   non-numeric year
   1   prose-embedded citation
  20

NOT CITATIONS — candidate-detection false positives
  16   bare year
  11   prose fragment
   8   A3  url / image             ← exclusion, not recovery
   3   A3  math / LaTeX            ← exclusion, not recovery
   3   artifact / non-citation
   2   bare locator
   2   colon locator with trailing prose
  45        these come out of the denominator
 ─────
 109   ✓
```

### Correction 1 — A3 is an exclusion, not a recovery

A3 is an exclusion-span rule. A URL or a math span should never become a
candidate in the first place. It parses nothing, so it cannot add to the
numerator; it removes 11 false candidates from the denominator.

The earlier arithmetic put those 11 in the "not yet implemented" bucket and then
added them to the numerator alongside B5. Wrong mechanism, and it hid 11 false
positives inside a list of recoveries.

```text
after colon + cp.                          1502 / 1611
A3 excludes 11 false candidates            1502 / 1600  =  93.9%
B5 recovers 17 real citations              1519 / 1600  =  94.9%
B6 adds 2                                  1521 / 1600  =  95.1%
```

The figure lands in nearly the same place. The mechanism does not, and the
mechanism is what an implementer builds from.

### Correction 2 — the two FAO cases are institutional, not all-caps surnames

`(FAO, 2018)` and `(FAO, 2005)` carry `all_caps_surname` because that is the
reason the implementation emitted. `FAO` is not an uppercase personal surname
here — it is a group author, with matching bibliography entries.

I took the implementation's own reason label as the classification instead of
inspecting the case. Same error as the earlier "already fixed" claims: trusting a
label rather than reading the manuscript.

```text
institutional author    6 → 8
limitations            22 → 20
```

Which changes the argument, not just the count. Institutional authors are not an
exotic extension to cover three exceptions — they are 8 occurrences across three
papers in the target corpus. That is a much stronger case for the bounded
group-author extraction path in rc3.

### 45 of the 109 are not citations, and that is the denominator problem

Nothing was lost in those 45. They are text the detector proposed and the grammar
correctly refused — `(2014)`, `i.e., respect and dignity`, `MBSR`, mathpix image
links. Most of the bare-year cases are B4's second-order effect: splitting a
group leaves orphan year segments behind, each counting as a detected occurrence.

```text
on all detected occurrences        1502 / 1611  =  93.2%
excluding the 45 non-citations     1502 / 1566  =  95.9%
    plus B5 and B6                 1521 / 1566  =  97.1%
```

**That crosses 95% by correcting the denominator, not by improving the parser.**
Which is why the gold set comes before any more grammar work — the target is
currently measuring detection granularity as much as accuracy, and 45 is the size
of the distortion.

Treat these as indicative. The classification is a heuristic pass and the 45 are
subject to gold adjudication; it is evidence that the gold set is the highest-value
remaining item, not a substitute for one.

### The path to target runs through decided work

```text
raw denominator, + B5 and B6           1521 / 1611  =  94.4%
A3 exclusion applied                   1521 / 1600  =  95.1%
```

B5, B6 and A3 are all already specified and agreed. So the target is reachable
through work that is decided plus a denominator definition, not through new
grammar. The 25 bounded-grammar cases can then be judged on merit rather than
under target pressure.

---

## What changed from the six-paper decomposition

```text
                          six papers    nine papers
residual                      68            142
largest class            other, 46     colon locator, 28
cp.                            5              5    unchanged
institutional                  4              6
compound / multi-token         4              9
B5 lead-in                     9             17
A3 url / image                 5              8
```

`cp.` is the one figure that survives intact — still exactly 5, still all in
`43338825`. Everything else grew, and the class that now leads the residual was
absent from the earlier set entirely.

**The old "other, 46" bucket is gone.** It was 67.6% of the six-paper residual
and read as an unanalysable long tail. Over nine papers with a fuller class
scheme there is no residual bucket at all: 22 named classes, zero unclassified.
Most of what sat in "other" was colon locators and bare years.

---

## Provenance

One consistent run. Full 64-character SHA-256 throughout, raw and transformed
inputs both, because the run reads the transformed bytes.

```text
transform      sed 's/\\&/\&/g'     rule id ampersand_unescape_v1
               still ad hoc, not a versioned ingest rule — the open item from
               the \&-before-canonicalisation finding is unchanged
runtime        python 3.10.12, regex 2026.7.19
corpus         development database `paperly`, 14 rows, exported base64
```

```text
implementation                    sha256
impl_v34.py            50077031db923e2b80eb86add2cf1967afc8222de569fd6258b99dc8c0846628
impl_v35_locator.py    afb635ee7593019e1aa8769cdbc3833a8ea19c992fbd332afff0223d82263fb2
impl_v35_cp.py         e2337195ef3c1e8c57bf531db1101206200c83d3818e0dce0976fa8a7fed6de1
impl_v35_both.py       03927c0ac4be04b0251adc991ac02d430f8fad46d8c09db5d3bda2a351bc685f
spec33_reference_impl  952c6bd820b41722dfeee453b77ebc2d73dac0966fd857f4dfc0cafd304962be
residual_classify.py   see alongside — classifier for the 142 and the 109
```

```text
paper      RAW input sha256                                                  TRANSFORMED input sha256                                          OUTPUT sha256 (impl_v35_both)
17bef7c6   5fd6328b341d6cc2f1da60833a0932bb06442020594f488ab9926e910267e275  096e5aabc3d39c6ca05c92d800b47f80cdf8994cac076dadd60cfbda992c00e3  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
2af68a7f   1ed96cb5189441114e7d2aa919a5066e7073d4b1e78461d7891cbf531e3081a9  d68b588e09f3d48e8d0e87bf008c55ac5acbbc4ef8841fd46c4eb3d96faef6bf  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
43338825   4ff6aa64ee8c4556e0d63d1de98f487c8a609cd81d16e638b459de91bafef147  4ff6aa64ee8c4556e0d63d1de98f487c8a609cd81d16e638b459de91bafef147  57a36260c0645c58dba96aade2a57175ce45be4da39cd66a53ad1d2e23e11685
4918fd7d   815f21f63a036245c5f1903853dc76eb0c6e249d2c34279694c35058eb82acaa  c76da39265641f05cab363e00d6b6b8662183dbd0390b3b4ca4cb5996f389815  6e4ed01a1e73b5419c2b09d9d04547ef7348f6c281652d387a06f920a5d6981f
50408397   30a6cecc1c52a69329304a4e6956eb20558c6c0b0970fcaa3daa74bb20791509  41828229665ff0b02683ca1e013476773cdfc199f027f5fcb1b78d9d59871515  0fc180d4ee0b9a625028125f8163ea27d0e5335541f5ed594e9e3db2fe9e6d6d
5da73cf4   1a62293ec8b5b31e0b0101055c780227a1663725d03965568b62b007bd8dd7c2  8cfd05945f8312b2fc07f5526780cf54ecf2c6dc2fb3d24abf9d6b3ae929792c  36ffd1922c189763cdcbde58f1428c01431b1e7d63a531bc15b14d4ce5f9b234
849f8fc6   5b1eda63829cf6585c896b011ba29f5529472bcb717ca0ee4da731720b072fc3  8e99746c12289e3fd6748fa04eed5fa8f00408e966c3b9da10b1612e5777d1ba  462dabbaf64b0ba6c43ed8f9b1b26895a1ec389b2a4e4d36a68bc9c691f3f363
ad1e3ff9   cff9bb85d74fbac8ffd69fd0c258812cb1d051b2963cbc8b8df8ebe447264615  f802893fbf2f88fd33a8f861a23a786ff2ce0ddee4492888df18e6e4809299e7  a425d639fda64241cae90c85cef4b9555187affa7f1690fa061784d2778f48c8
bf2fdc4a   59f2a7337b97cf7b3641f10d62682f53693753512642f8e22f0ca5b6e77eeaec  4d65224a58d2514a89b5d7c78002cb699b355456116817f6ca4ad677f744c6fc  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
c1d56945   48b2b2f459e5cad88b7105048a0d7e0f852084764662a9e67155de52b52921d8  0e9b66c29d18992dfc156486ac37023d9ccc08358b7c95fe7218347c6de47f82  8a9d9d5bcb8902ee4c6dde2cb08e43c56323c9436a2cc703bd8b1a549629d3b2
c22df19f   de75e3591a46663a295bd2fd70f0a10b41c8d32fec565f866c999e73ffdf626a  ba4b8763e85de848f68bb84524796b9f8aaf1b7e2afa61b8e73a19d27021009f  e090a8550482454a3f85dfdb9d649b954a5e1fd6632826912b71e69e9461cbc4
e1b418a4   60bdf44f97ae996b65da3bdc8ac89d36c6330e3cc772ebd6769dab81a7a95090  a01786ee7c206ffa49c75e8c005933788c4d8a9e54bff8b3aa4722909d256446  92e831acbce16a225067d959e408cd8f7c7221c378f2c1a2d400c5e673a3046d
ea07e5f5   c43e5e1161ebccfda9b11f096a980d8c5d2dfea69f4599d7f92311bcf3edea1e  7684093bb4403e4a0bafb6da93da89395562ec2b3363a0f22d971be1c845d9f1  c2da4a8dec1a4e44e24ecf083d5af3d1df7f0e24cd2d6d3802a2a77e7a097729
ed6a890a   0265812f086b6d4ce09348dd519c97fadb68b71084b6dfe636c41ae6961ba6d3  66b2d470cb70bf70bfb60ce30253599724045011829945dead43e5d3a0a105a2  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
```

`43338825` is the control: raw and transformed hashes identical, because it
contains zero `\&`. Its rate still moved this time — `+5` from `cp.`, which is
the right behaviour, since that fix is unrelated to the transform.

The four `exit 3` papers share output hash `ced72346…` across run 3 and this run,
across both implementations. Byte-identical nothing, four times, unchanged by two
grammar fixes — which is what `bibliography_absent` is for and remains unbuilt.

---

## Open, unchanged by this run

```text
[ ] gold denominator over the 10 in-profile papers        now the top item
[ ] the four exit-3 papers under bibliography_absent      impl does not have it
[ ] \& → & placed before canonicalisation in ingest       still ad hoc
[ ] c22df19f named in register §9 as out-of-profile       0/121 is correct refusal
```
