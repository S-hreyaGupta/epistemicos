# rc3 was in the uploads all along, and it already decides the edge cases

Found 19 September 2026, after Alex Zamurko said he did not have the file
either and asked whether it was anywhere in the records.

It is. `specs/citation/citation-v3.4-rc3-amendments.md`, committed here
byte-identical to the copy it came from.

## Why nobody found it

The filename.

```text
66128c8e-a5a0-4898-86bf-d856d098e289-1788200487226_CI2D25~1 (2).MD
```

A Windows 8.3-truncated name. Searching for `rc3` in filenames returns four
files, all for *other* specifications — `LDVI_v0.3_minimum_v1_rc3`,
`authoritative_technical_spec_standard_v0.1_rc3` — because rc3 is a general
release-candidate convention here, not a citation-specific label. The citation
one is the single file whose name contains none of the words anyone searched
for.

It was found by searching for its **contents** instead: the repository cites
`NON_PERSON_AUTHOR` and `B1a` in comments, and exactly one file in the uploads
contains either.

## What it is

```text
title      Citation v3.4 rc3 — amendment set over rc2
dated      31 August 2026
735 lines
sha256     c392982ef625aec03e8f52af51fc88138ea0e4e9c3bfb9795d62f9dfbf594d5b
```

Not a standalone specification. **An amendment set over rc2**, which is
described in it as a four-file package. So the lineage is:

```text
v3.3          the deterministic spec — what scripts/citation_extract.py implements
v3.4 rc1      freeze candidate, content_state: review_candidate, frozen_at: null
v3.4 rc2      a four-file package — NOT in the repository, not in the uploads
v3.4 rc3      this: an amendment set over rc2
```

rc1, rc2 and rc3 are candidate revisions of **one document**, v3.4. They are
not three competing specifications, which is how the records had been reading
them.

**rc2 is still missing**, and rc3 amends it rather than replacing it, so rc3
alone is not a complete specification either.

## The recorded hash is right. This copy is truncated.

```text
recorded in the records   ddc6f1f80c93d12d6268cda03fffb6720adac3b4bb9bc5da351f8c5a28a108e2
this file                 c392982ef625aec03e8f52af51fc88138ea0e4e9c3bfb9795d62f9dfbf594d5b
```

**Resolved 21 September.** The `ddc6f1f8…` file was found in the assistant's
own outputs directory, under `gsd/`, and is now in this repository as
`citation-v3.4-rc3-amendments-frozen.md`. It hashes exactly.

The copy here is a second download — the filename ends `(2)` — and it stops
twenty lines early. The frozen file appends a governing-spec note and a pointer
to its freeze record; the diff is append-only and **§A2 is byte-identical**, so
nothing implemented from this copy needs revisiting.

What this document got wrong is worth keeping. It read the mismatch as a
recorded hash naming an artifact nobody has, the same shape as
`PROVENANCE-GAP.md`. Both were wrong the same way, and for the same reason:
neither search covered the directory the assistant writes into.
`GSD-FOLDER-RECOVERY.md` has the full account.

## What it already decides

This is the part that matters. Every edge case recorded in
`CITATION-EDGE-CASES.md` as needing a decision is **already decided in rc3**,
with a measured value attached.

```text
ours    rc3          what rc3 says                                  worth
────────────────────────────────────────────────────────────────────────────
EC-3    B1           "Do not reintroduce a token cap. C2 removed
                     the six-token cap for a reason and the corpus
                     still contains the case that removed it:
                     Van den Brink and Van der Woerd, 7 tokens,
                     present twice."                                  —

EC-4    B1a          SURNAME = (PARTICLE WS)* CORE
                                (WS (PARTICLE WS)? CORE)?
                     names Carrieri de Souza, El Akremi,
                     Pircher Verdorfer, Oliveira da Silva             9

instit. B1b          NON_PERSON_AUTHOR, citation side                 8

EC-2    B8           NARRATIVE_POSSESSIVE_NORMALIZATION, with
                     MAX_POSSESSIVE_YEAR_GAP_TOKENS = 3               7
```

**EC-3 is not an open question.** rc3 names the exact case this repository
rediscovered independently on 18 September — `Van den Brink and Van der Woerd`,
seven tokens — and says the cap must not be reintroduced. v3.3's §6.1 caps the
envelope at six. So the implementation is conformant to v3.3 and in violation
of rc3 on the same clause.

**EC-4's grammar is written out.** The production that admits
`Carrieri de Souza` and `Oliveira da Silva` exists, and so does the statement
that it cannot reach the institutional cases, which is why B1b is separate.

**EC-2 was repaired on 19 September** and rc3 goes further: rc2 covers the
simple form, and B8 adds an intervening-noun gap of up to three tokens —
`Martinko et al.'s review (2013)`, `Harter's definition of authenticity
(2002)`. The repair here handles the simple form only.

Also already specified: `\& → &` ordering (D1), the colon locator (B3,
measured +28), `cp.` (B4, measured +5), segment-split orphans (B9) — all four
of the corrections currently carried as flags.

## What this changes

The edge-case register was written as a list of open questions for Alex. Four
of its entries were answered on 31 August in a document that was in the
uploads the whole time.

That is not wasted work: the register measured each one against the current
corpus, and rc3's own figures are from the August run whose implementation is
gone. The two now corroborate each other from different directions, which is
worth more than either alone.

But the framing has to change. These are not decisions awaiting a ruling. They
are **a conformance gap between the running v3.3 implementation and an rc3
that has never been read here** — which is exactly what
`CITATION_SPEC_STATUS.md` said could not be measured, and now can be.

## What is still open

```text
rc2               missing. rc3 amends it; without it rc3 is not complete.
the recorded hash does not identify this file, and nothing explains why.
which governs    rc3 is an amendment set over a package nobody has, so
                 "rc3 governs" is not yet an executable statement.
```
