# Consolidation Step 1 — Inventory

Against Alex Zamurko's consolidation workflow v6, 21 September 2026.

> **Gate.** Every known relevant source is listed. Missing referenced material
> is recorded explicitly; affected items cannot be treated as resolved.

**GATE PASSED, 21 September 21:58.** All five rc2 files are in hand. Alex
Zamurko sent the three missing ones within minutes of being asked, and the two
already held came back byte-identical, so the package is internally consistent.

Thirteen sources, all hashed. Two artefacts remain unrecoverable and are
recorded in §4 as history rather than as blockers.

---

## 1. Where the search was performed

Recorded because the workflow asks for it, and because on 21 September the
answer turned out to matter more than the search did.

```text
this repository            specs/citation/, full tree
session uploads            1080 files
C:\ entire drive           *.md, *.txt, *.MD, by CONTENT not filename:
                           candidate_revision:\s*2 | NON_PERSON_AUTHOR
C:\Users\gupta\Downloads   every markdown file listed beside its real first
                           line, so a truncated filename could not hide a title
#citation Slack channel     Files and links tab
```

The first three searched the local disk and **all of them missed rc2**, which
had been posted to #citation on 28 August and never downloaded. The Downloads
title-listing found `CITATI_3.MD`, which the content searches also missed
because it carries no front matter and uses none of the search strings.

Two lessons worth carrying into any future search: a filename search finds
nothing here, and a local search cannot find what was never downloaded.

---

## 2. Sources present, with hashes

```text
sha256                                                            lines  file
239ee6bdd6cbdaf94f3e007d23fa47826ce2b11b60a03da0d9b667ba1a0a980e    456  citation-spec-v3.3.md
55fcc7b8ce610c85780737f7b13fab6e9a612160b74488fdf81b7c09c6411a71    274  citation-v3.4-pre-rc1-three-additions-first-draft.md
0c93ee9cf6c6784fb55aff24411886e9425e1c16a5325f3a5b27bcd4d64dd4ce    332  citation-v3.4-pre-rc1-three-additions.md
6a615c8136543ef492598196a918b2c1e4b62bb54fdbcca4bd12af28bac66cb0    435  citation-v3.4-rc1-architecture.md
11edbf8918224c0ee1ac85423db1f676fe49ca1feceecf1575c4a1daa2976695   1402  citation-v3.4-rc1-execution-conformance.md
73f4ba54cc045da9547202fbf48946b29a5e73981b402ae1554379cd60a42612    227  citation-v3.4-rc1-conformance-matrix.md
7d2414388cf019cca40361e42bdd6735b513c57a5fcce997ecbea9fc667db850    282  citation-v3.4-rc1-deferred-work-register.md
4a60b994845a323d5ee1170559d3f9017abf62aeaf4bc7fc0bc1992e335adb9e    377  citation-v3.4-rc2-architecture.md
4fa95af15755c569d5a5135321a22fdfab85464c4ee92c09a8808d73318aa466   1576  citation-v3.4-rc2-execution-conformance.md
f0f1aa37603e20be650159cf8b91896ea222ad2562f40d55c3a9e804640566b8    138  citation-v3.4-rc2-conformance-matrix.md
0bf1cc12e93ce1911916644d620d387f23ee0b14f41662b752846ba1858d5698    230  citation-v3.4-rc2-deferred-work-register.md
a35e2ded9197cf683686c1f1a2f793cbe0f61160ec64562351994d04dd9bbaf2    223  citation-v3.4-rc2-gsd-pilot-contract.md
c392982ef625aec03e8f52af51fc88138ea0e4e9c3bfb9795d62f9dfbf594d5b    735  citation-v3.4-rc3-amendments.md
```

Generated from the files, not transcribed. The first version of this table was
hand-split into groups of eight and one digest came out wrong — in a document
whose only job is to carry digests accurately. It is now produced by reading
the bytes.

## 3. Status and relationship

```text
file                          status            relationship
──────────────────────────────────────────────────────────────────────────────
citation-spec-v3.3            GOVERNS THE CODE  separate lineage. The running
                                                implementation is written from
                                                it clause by clause.
pre-rc1 first draft           SUPERSEDED        21 Aug, superseded 52 minutes
                                                later by the revision below
pre-rc1 three-additions       SUPERSEDED        21 Aug. rc1 absorbed every
                                                identifier in it; kept because
                                                it establishes rc1's scope
rc1 architecture              SUPERSEDED by rc2 same spec_id, revision 1
rc1 execution conformance     SUPERSEDED by rc2 same spec_id, revision 1
rc1 conformance matrix        SUPERSEDED by rc2 rc2's has 86 cases to rc1's set
rc1 deferred-work register    SUPERSEDED by rc2 X-01..X-14, same titles
rc2 architecture              CURRENT           candidate_revision: 2,
                                                content_state: review_candidate,
                                                frozen_at: null
rc2 execution conformance     CURRENT           as above
rc2 conformance matrix        CURRENT           binds to 4a60b994… and
                                                4fa95af1…, which are this
                                                repository's 01 and 02
rc2 deferred-work register    CURRENT           X-07 and X-08 are load-bearing
                                                for discrepancies 2 and 7
rc2 GSD pilot contract        CURRENT           pilot scope boundary
rc3 amendments                CURRENT           amendment set over rc2, frozen
                                                3 September per the records
```

All four rc1 files are superseded. rc1 is history, not a source for the
consolidation, and the only reason to open it now is to check what rc2
changed.

`rc2 REVISES rc1` is established rather than inferred: rc2's two files carry
rc1's own `spec_id` values at `candidate_revision: 2`. That answers the question
`LINEAGE.md` carried open for two days.

## 4. The rc2 package, now complete

All five arrived 21 September. What they turned out to contain:

```text
03  conformance matrix and freeze checklist. EIGHTY-SIX conformance cases,
    C-001 to C-086, every one DEFINED / PENDING_EXECUTION. Its front matter
    binds to `4a60b994…` and `4fa95af1…`, which are exactly the 01 and 02 in
    this repository, so the package hashes check against each other.
04  dependency and deferred-work register. Fourteen deferred items X-01 to
    X-14, identical in title to rc1's.
05  GSD pilot task contract and manual comparator.
```

Two things this settles immediately, both of which had been open:

```text
leading_gloss          ZERO occurrences across all five rc2 files
conversion_artifact    ZERO occurrences across all five rc2 files
```

So rc3 A2's two undefined exclusion reasons are undefined in rc1, rc2 AND rc3.
They appear exactly once each in the entire specification set, in rc3's own A2
table, carrying a count and no rule. That is 14 of rc3's 30 exclusions, and it
is now an `UNRESOLVED` row needing a normative decision rather than more
evidence.

`conversion_artifact` may be a forward reference: rc2 X-08 defers
`ConversionArtifactAnnotations / conversion repair` entirely. If so the reason
name was written against work that does not exist yet, which is worth Alex
Zamurko confirming rather than my assuming.

And one thing it confirms. rc2 X-07 defers "comma-containing organization
authors" by name, and C-036 makes it a conformance case: "unsupported
comma-containing organization remains unresolved / no guessed reference
identity". That is exactly the FAO decision recorded as discrepancy 2. FAO is
not an oversight in rc2; it is explicitly deferred work, and the implementation
already satisfies C-036.

Still unrecoverable, and recorded rather than resolved:

```text
the August implementation    impl_v34.py and the corpus_run_2 outputs. The
                             hash is recorded and the artefact is gone;
                             PROVENANCE-GAP.md has the detail. rc3 §I is
                             frozen on figures produced by it.
rc3's recorded hash          the records quote ddc6f1f8… since 3 September;
                             the file in hand is c392982e…. No file anywhere
                             hashes to the recorded value.
```

## 5. What Step 2 can proceed on now

```text
architecture   rc1 vs rc2     DONE — CONSOLIDATION-STEP2-ARCHITECTURE.md
               no DROP, no UNRESOLVED. rc2's text replaces throughout.
execution      rc1 vs rc2     not started, 1402 -> 1576 lines, carries the
conformance                   grammar. The largest remaining piece.
matrix         rc1 vs rc2     not started
register       rc1 vs rc2     not started, X-01..X-14 same titles
rc2            vs  rc3        SEVEN discrepancies recorded —
                              RC2-RC3-DISCREPANCIES.md
v3.3           vs  v3.4       a normative decision, not a comparison.
                              Decision CIT-ARCH-01, pending.
```

The six are already in the shape the workflow's consolidation table wants: each
records the source text, the conflict, what was chosen, why, and what the
consolidation should decide. They are candidate `UNRESOLVED` rows requiring a
normative decision rather than more evidence, except number 2, which rc2 itself
settles.

## 6. One thing to settle before Step 3

The workflow says a disposition resolves "only items that require a normative
decision". The largest item in this consolidation is not a rule but an
architecture:

```text
v3.3     the extractor derives citation_key at extraction time
rc2 §8   "Syntax does not confer authoritative author_kind or citation_key.
          Authority is acquired only through exact bibliography resolution."
```

Those cannot both hold. The running implementation is v3.3's way except on the
non-person path, where rc2's two-pass model is implemented because rc3 B1b
cannot work without it. So the code currently sits across both.

This is one decision, it governs a large share of the rows, and taking it first
would stop those rows being decided twice.

---

## Gate result

```text
Step 1   NOT PASSED — three known sources absent
Step 2   may begin on v3.3 / rc1 / rc2 / rc3 as listed in §5
Step 3   blocked for any row governed by 03, 04 or 05
```

Per rule 4, those rows wait for the artefact, not for a human decision. The
three files are two clicks away in #citation.
