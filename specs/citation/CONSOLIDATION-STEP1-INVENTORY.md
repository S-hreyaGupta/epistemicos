# Consolidation Step 1 — Inventory

Against Alex Zamurko's consolidation workflow v6, 21 September 2026.

> **Gate.** Every known relevant source is listed. Missing referenced material
> is recorded explicitly; affected items cannot be treated as resolved.

**The gate is not passed.** Three sources are known to exist, are named by an
artefact already in hand, and are not here. Step 2 can begin on what is
present; the rows those three govern stay `UNRESOLVED / blocked` per rule 4.

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
SHA-256                                                           lines  file
239ee6bd d6cbdaf9 4f3e007d 23fa4782 6ce2b11b 60a03da0 d9b667ba 1a0a980e   456
    citation-spec-v3.3.md
55fcc7b8 ce610c85 780737f7 b13fab6e 9a612160 b74488fd f81b7c09 c6411a71   274
    citation-v3.4-pre-rc1-three-additions-first-draft.md
0c93ee9c f6c6784f b55aff24 411886e9 425e1c16 a5325f3a 5b27bcd4 d64dd4ce   332
    citation-v3.4-pre-rc1-three-additions.md
6a615c81 36543ef2 98196a91 8b5e4c1b 62bb54fd b28fac68 2b4dc66c bb32b8e1   435
    citation-v3.4-rc1-architecture.md
11edbf89 18224c0e e1ac8542 3db1f676 fe49ca1f eceecf15 75c4a1da a2976695  1402
    citation-v3.4-rc1-execution-conformance.md
73f4ba54 cc045da9 547202fb f48946b2 9a5e7398 1b402ae1 554379cd 60a42612   227
    citation-v3.4-rc1-conformance-matrix.md
7d241438 8cf019cc a40361e4 2bdd6735 b513c57a 5fcce997 ecbea9fc 667db850   282
    citation-v3.4-rc1-deferred-work-register.md
4a60b994 845a323d 5ee11705 59d3f901 7abf62ae af4bc7fc 0bc1992e 335adb9e   377
    citation-v3.4-rc2-architecture.md
4fa95af1 5755c569 d5a51353 21a22fdf ab85464c 4ee92c09 a8808d73 318aa466  1576
    citation-v3.4-rc2-execution-conformance.md
c392982e f625aec0 3e8f52af 51fc8813 8ea0e4e9 c3bfb979 5d62f9df bf594d5b   735
    citation-v3.4-rc3-amendments.md
```

Full single-line digests are in the repository; they are split here only to fit
the page.

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
rc1 conformance matrix        SUPERSEDED?       no rc2 counterpart IN HAND
rc1 deferred-work register    SUPERSEDED?       no rc2 counterpart IN HAND
rc2 architecture              CURRENT           candidate_revision: 2,
                                                content_state: review_candidate,
                                                frozen_at: null
rc2 execution conformance     CURRENT           as above
rc3 amendments                CURRENT           amendment set over rc2, frozen
                                                3 September per the records
```

`rc2 REVISES rc1` is established rather than inferred: rc2's two files carry
rc1's own `spec_id` values at `candidate_revision: 2`. That answers the question
`LINEAGE.md` carried open for two days.

## 4. Missing referenced material — the gate

```text
03_citation_v3.4_conformance_matrix_freeze_checklist_rc2.md   NOT IN HAND
04_citation_v3.4_dependency_deferred_work_register_rc2.md     NOT IN HAND
05_citation_v3.4_gsd_pilot_task_contract_and_manual_comparator.md  NOT IN HAND
```

**Known to exist**, not merely suspected: Alex Zamurko posted all five files to
#citation on 28 August at 12:58 AM and they are listed in that channel's Files
and links tab today. Two were downloaded on 21 September; three were not.

What they govern, and therefore what cannot be resolved without them:

```text
03  the freeze checklist and conformance matrix. Any row whose disposition
    depends on "is this conformance requirement still binding" is blocked.
04  the dependency and deferred-work register. rc1's version carries the
    limitation register including X-07, which rc3 §C3 says has lost its
    evidence. Whether rc2 already moved it cannot be checked.
05  the GSD pilot task contract and manual comparator, frozen at c27e647f
    before onboarding. Governs the pilot scope boundary.
```

Also unrecoverable, and recorded rather than resolved:

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
v3.3           vs  rc1        two architectures, not two maturities
rc1            vs  rc2        01 and 02 only; 03 and 04 blocked
rc2            vs  rc3        amendment layer, and SIX places where rc3's
                              description of rc2 does not match rc2 —
                              RC2-RC3-DISCREPANCIES.md
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
