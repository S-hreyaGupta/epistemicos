# The 46 residual — corrected

**Supersedes `CITATION_RESIDUAL_46.md`.** Four of its claims were wrong and the
arithmetic dropped 8 cases. Every correction below is Alex's, verified against
rc2 and the run output rather than accepted on assertion.

---

## What was wrong

```text
CLAIM                                          STATUS
4 institutional authors "already fixed"        WRONG — rc2 has non-person on the
                                               BIBLIOGRAPHY side only. Citation
                                               extraction still needs
                                               AUTHORS_PAREN, which is person
                                               grammar, so "International
                                               Monetary Fund" never becomes a
                                               candidate at all

2 compact 2019a,b "already specified"          WRONG — rc2 supports a single
                                               suffixed year (2020a). No rule
                                               expands 2019a,b. B6 is proposed,
                                               not incorporated

2 missing-comma "cheap and closed"             WRONG — SEG requires the comma
                                               before the year. Accepting
                                               (Lu and Shang 2017) is a grammar
                                               loosening, not a token addition

5 particle failures "a case issue"             PARTLY WRONG — see below

41 = 14 + 11 + 8                               ARITHMETIC ERROR — that is 33.
                                               The missing 8 are the classes
                                               outside the original 46
```

**The consequence: "27 of 68 recoverable without new grammar → 95.3%" does not
hold.** Corrected below.

---

## Particles — inspected individually, as asked

Six occurrences, and they are **two different defects**, not one.

```text
(Da silva et al., 2017)              Da  silva  et al.
                                     particle leads, core is lowercase
                                     → CASE issue

(da Silva et al., 2024: …)           da  Silva  et al.
                                     particle leads, core capitalised
                                     → shape is legal; fails on the ':' separator
                                       (class G), not on the particle

(Oliveira da Silva et al., 2024)     Oliveira  da  Silva
Carrieri de Souza et al. (2023)      Carrieri  de  Souza
Carrieri de Souza et al., 2023       Carrieri  de  Souza
Additionally, Oliviera da Silva …    Oliviera  da  Silva
                                     → CORE before particle
```

```text
SURNAME = (PARTICLE WS)* CORE
```

That is *particles preceding one core*. `Carrieri de Souza` is
**CORE + particle + CORE**, which the production cannot express at all. It is not
a case problem and case-folding would not touch it.

```text
1  genuine case issue          Da silva
4  compound surname            CORE particle CORE
1  miscounted — actually class G (': ' separator)
```

**So the fix is a bounded compound-surname rule, not case-folding**, and it would
recover 4 rather than 5. Alex was right to ask for the individual pass; the
aggregate label hid two unrelated problems and one miscount.

A candidate production, offered as a starting point rather than a proposal:

```text
SURNAME = (PARTICLE WS)* CORE (WS PARTICLE WS CORE)*
```

bounded to one internal particle-core repetition, which covers Lusophone and
Hispanic compounds without opening the run to arbitrary length.

---

## Corrected arithmetic

The residual is 68. Full accounting, nothing dropped:

```text
FROM THE 46
   6  D  narrative fragment, author split
   5  A  cp. cue not in PREFIX
   5  B  et-al punctuation variants
   5  G  wrong separator            (+1 reclassified from K = 6)
   5  K  particle                   (−1 reclassified to G  = 4 compound + 1 case)
   5  M  residual
   4  F  forename-first / in-line journal
   4  H  institutional author
   2  C  compact year-suffix
   2  E  bare locator
   2  J  missing comma
   1  I  multi-year, no author
  46

OUTSIDE THE 46
   9  B5 lead-in phrases
   5  A3 URL / image spans
   4     bare year
   2     math / LaTeX
   2     all-caps surname
  22

  46 + 22 = 68   ✓
```

### Recoverable, corrected

```text
SPECIFIED AND AGREED, NOT YET IMPLEMENTED
   9   B5 bounded lead-in
   5   A3 URL / image exclusion
  14

ONE TOKEN IN A CLOSED SET
   5   cp. added to PREFIX
   5

NEEDS NEW BUT BOUNDED GRAMMAR
   4   compound surname          CORE particle CORE
   4   institutional citation extraction path   ← NOT already fixed
   2   B6 compact year-suffix    ← NOT already specified
  10

────────────────────────────────────────────────
  29 of 68, and 10 of those require rc3 grammar work
```

```text
19 recoverable with no new grammar   → 92.2% + 19  ≈ 94.4%
29 recoverable with rc3 grammar work → 92.2% + 29  ≈ 95.5%
```

**95% is not reachable without rc3 grammar work.** The earlier document said it
was, and that rested on the three false "already fixed" claims. Both figures
remain provisional until the gold denominator exists.

### The other 39

```text
REGISTERED LIMITATION CANDIDATES — malformed input or out of profile
   5  B  et-al punctuation typos       at al. / et al, / , et al.
   6  G  wrong separator               ':' and ',' for ';'
   4  F  forename-first / in-line journal   → already X-07
   2  J  missing comma before year     → register, do not loosen SEG
   2     all-caps surname              → already registered
  19

GENUINE GRAMMAR WORK, DEFERRED
   6  D  coordinated authors across the candidate boundary
   1  K  Da silva case-folding
   7

LONG TAIL / NEEDS INDIVIDUAL DECISION
   5  M  residual, each different
   4     bare year
   2     E bare locator
   1     I multi-year no author
   2     math / LaTeX
  14
  ────
  39 + 29 = 68   ✓
```

---

## Provenance — complete

Full 64-character SHA-256, and **both** the raw and the transformed inputs, since
run 2 read the transformed bytes.

```text
transform      sed 's/\\&/\&/g'      LaTeX-escaped ampersand → ampersand
rule version   ampersand_unescape_v1
               ad hoc for this run — NOT yet a versioned ingest rule, which is
               itself the open item from the \&-before-canonicalisation finding

implementation
  impl_v34.py            50077031db923e2b80eb86add2cf1967afc8222de569fd6258b99dc8c0846628
  spec33_reference_impl  952c6bd820b41722dfeee453b77ebc2d73dac0966fd857f4dfc0cafd304962be

runtime  python 3.10.12,  regex 2026.7.19
```

```text
paper      RAW input sha256                                                  TRANSFORMED input sha256
17bef7c6   5fd6328b341d6cc2f1da60833a0932bb06442020594f488ab9926e910267e275  096e5aabc3d39c6ca05c92d800b47f80cdf8994cac076dadd60cfbda992c00e3
2af68a7f   1ed96cb5189441114e7d2aa919a5066e7073d4b1e78461d7891cbf531e3081a9  d68b588e09f3d48e8d0e87bf008c55ac5acbbc4ef8841fd46c4eb3d96faef6bf
43338825   4ff6aa64ee8c4556e0d63d1de98f487c8a609cd81d16e638b459de91bafef147  4ff6aa64ee8c4556e0d63d1de98f487c8a609cd81d16e638b459de91bafef147
5da73cf4   1a62293ec8b5b31e0b0101055c780227a1663725d03965568b62b007bd8dd7c2  8cfd05945f8312b2fc07f5526780cf54ecf2c6dc2fb3d24abf9d6b3ae929792c
849f8fc6   5b1eda63829cf6585c896b011ba29f5529472bcb717ca0ee4da731720b072fc3  8e99746c12289e3fd6748fa04eed5fa8f00408e966c3b9da10b1612e5777d1ba
ad1e3ff9   cff9bb85d74fbac8ffd69fd0c258812cb1d051b2963cbc8b8df8ebe447264615  f802893fbf2f88fd33a8f861a23a786ff2ce0ddee4492888df18e6e4809299e7
bf2fdc4a   59f2a7337b97cf7b3641f10d62682f53693753512642f8e22f0ca5b6e77eeaec  4d65224a58d2514a89b5d7c78002cb699b355456116817f6ca4ad677f744c6fc
c1d56945   48b2b2f459e5cad88b7105048a0d7e0f852084764662a9e67155de52b52921d8  0e9b66c29d18992dfc156486ac37023d9ccc08358b7c95fe7218347c6de47f82
c22df19f   de75e3591a46663a295bd2fd70f0a10b41c8d32fec565f866c999e73ffdf626a  ba4b8763e85de848f68bb84524796b9f8aaf1b7e2afa61b8e73a19d27021009f
ea07e5f5   c43e5e1161ebccfda9b11f096a980d8c5d2dfea69f4599d7f92311bcf3edea1e  7684093bb4403e4a0bafb6da93da89395562ec2b3363a0f22d971be1c845d9f1
ed6a890a   0265812f086b6d4ce09348dd519c97fadb68b71084b6dfe636c41ae6961ba6d3  66b2d470cb70bf70bfb60ce30253599724045011829945dead43e5d3a0a105a2
```

**43338825 is the control.** Its raw and transformed hashes are identical because
it contains zero `\&`. That is the one paper the transform provably did not
touch, and its citation rate did not move.

### Output hashes — full, both runs

An earlier version pointed at `corpus_run_2/` and quoted only a truncated prefix.
A provenance manifest that refers elsewhere is not a complete evidence chain, so
both runs are recorded in full here.

```text
paper      RUN 1 output sha256                                               RUN 2 output sha256
17bef7c6   ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
2af68a7f   ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
43338825   a957ce1a97a74393fc6f28abc2d75a412fc5e113a6460121bf4ff99419ce028b  d223fc5bf44d45a8f7ce75e08babd0110078051848d6c976c516112c67fb61b2
5da73cf4   c9700b5725d641500200c82f0cfd57fa7fc5a81f50b2a2fe913de3908bdc7b9a  36ffd1922c189763cdcbde58f1428c01431b1e7d63a531bc15b14d4ce5f9b234
849f8fc6   fe07e089292bf60451d93959f002e517c0aa533edbcf9453ab1a24c62dd3a8cc  462dabbaf64b0ba6c43ed8f9b1b26895a1ec389b2a4e4d36a68bc9c691f3f363
ad1e3ff9   59b4cbff308b44706d71ddb9c76b6114e82d67bd0d5a62ca3958796e3ea192d7  a425d639fda64241cae90c85cef4b9555187affa7f1690fa061784d2778f48c8
bf2fdc4a   ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
c1d56945   d770879f6a21c582923ce5b018d7d25da7ed2fa977608849a1a695d4ac5cc2e1  8a9d9d5bcb8902ee4c6dde2cb08e43c56323c9436a2cc703bd8b1a549629d3b2
c22df19f   6d54241713f7a47d737040bfb9b6af0099ef1c08ffee3896a96d6a8521d03fd8  e090a8550482454a3f85dfdb9d649b954a5e1fd6632826912b71e69e9461cbc4
ea07e5f5   9966bca4dffcfba5881f676b0f5d7376b3a526c652b76ae7e1a8a8ab15806aa7  c2da4a8dec1a4e44e24ecf083d5af3d1df7f0e24cd2d6d3802a2a77e7a097729
ed6a890a   ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0  ced72346241f2815636597fffc2d8dee49ec7ebf8d154dc08ead2ac85ccd87b0
```

Two things the full table makes visible that the pointer did not:

**The four exit-3 papers share one hash across BOTH runs** —
`ced72346…87b0`. Identical bytes, four papers, two runs, two different
implementations. The tool produces the same two lines of nothing regardless of
input or version, which is the strongest possible statement of the
`bibliography_absent` gap.

**Every other paper's hash changed between runs**, including `43338825`, whose
*input* was byte-identical across runs because it contains no `\&`. Its output
still moved, which isolates the B4 segment-splitting change as the cause. That
is a clean control: same input, different output, one known code change.

---

## THIS CORPUS IS INCOMPLETE — established 29 August

Phase 0B against the development database returned **14 papers rows**, all with
markdown. `data/md` holds 11 files and is a stale export; the authoritative
markdown lives in `papers.markdown`.

```text
papers rows in the database   14
markdown files used by runs   11
never measured                 3   4918fd7d, 50408397, e1b418a4
```

**Every figure in this document and in both corpus runs is computed over 11 of
14 papers.** That includes 92.2%, the residual of 68, the distribution of the 46,
and the count of 5 for `cp.`.

The direction of the findings is unlikely to reverse, but **none of these numbers
should be frozen**. Re-run against markdown exported from the database, not from
`data/md`.
