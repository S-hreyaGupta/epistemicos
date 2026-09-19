# The citation specification lineage

Established 19 September 2026, after Alex Zamurko asked whether the next step
is to consolidate the three files. It is not three files, and consolidation is
blocked on a fifth.

## What exists, and what it is

```text
v3.3 — one document, a different lineage
  citation-spec-v3.3.md                        239ee6bd…  456 lines
  "deterministic spec v3.3". Numbered §1-§12. THIS IS WHAT RUNS.
  scripts/citation_extract.py implements it clause by clause and its
  70-control conformance suite is built from §12's own case list.

v3.4 rc1 — a FOUR-file package, all present
  citation-v3.4-rc1-architecture.md            6a615c81…  spec_id: citation_architecture
  citation-v3.4-rc1-execution-conformance.md   11edbf89…  spec_id: citation_execution_conformance
  citation-v3.4-rc1-conformance-matrix.md      73f4ba54…  conformance matrix / freeze checklist
  citation-v3.4-rc1-deferred-work-register.md  7d241438…  dependency + deferred-work register
  All four say content_state: review_candidate, frozen_at: null.
  Nothing implements any of them.

v3.4 rc2 — MISSING
  rc3 calls it "the four-file rc2 package" and cites rc2-A3 and rc2-B4, so
  rc2 carries its own A- and B-series: it is an amendment layer over rc1,
  not a fresh package.

v3.4 rc3 — one document, present
  citation-v3.4-rc3-amendments.md              c392982e…  735 lines
  "amendment set over rc2", 31 August. A- B- C- D-series amendments.
```

So the shape is:

```text
   v3.3                    a separate, earlier, self-contained specification
                           ── currently governing the code ──

   v3.4 rc1  (4 files)     base package
        ↓
   v3.4 rc2  (amendments)  MISSING
        ↓
   v3.4 rc3  (amendments)  present
```

**Six documents in two lineages, with one amendment layer absent.** Not three
files, and not three competing versions of one thing.

## Why consolidation is blocked

rc3 amends rc2. rc2 amends rc1. Consolidating rc1 and rc3 without rc2 would
silently drop whatever rc2 changed, and rc3 tells us rc2 changed real things:

```text
rc2-A3   an EXCLUSION, not a recovery — rc3 B10 says this is worth 11 off
         the denominator, so rc2-A3 moves a measured figure
rc2-B4   segment splitting, already in the baseline rc3 quotes:
         1502 / 1611 = 93.2% "after \& + rc2-B4 segment splitting"
```

A consolidation missing rc2 would produce a document that looks complete,
carries no marker of what is absent, and disagrees with rc3's own baseline
figure. That is worse than the current state, where at least the gap is
visible.

## The other thing consolidation has to decide

v3.3 and v3.4 are not the same document at different maturities. v3.4 rc1 §2 is
titled "Architectural split" and asserts things v3.3 does not:

```text
2.1  Extraction does not create work identity
2.2  Identity requires bibliography evidence
2.3  Reconciliation is downstream of identity
```

v3.3 has the extractor derive a `citation_key` at extraction time. v3.4 says
identity is not extraction's to create. That is a re-architecture, not an
increment, and the running implementation is built the v3.3 way.

So consolidation is not merging four documents into one. It is choosing
between two architectures and then rewriting the implementation to match
whichever wins. The size of that is not visible from the file count.

## What is available now without rc2

The conformance gap between the running implementation and rc3's amendments
can be measured today, because rc3's grammar amendments are self-contained
productions that do not depend on rc2 to be read:

```text
B1a   SURNAME = (PARTICLE WS)* CORE (WS (PARTICLE WS)? CORE)?      worth 9
B1b   NON_PERSON_AUTHOR, citation side                             worth 8
B8    NARRATIVE_POSSESSIVE_NORMALIZATION, 3-token gap              worth 7
B1    "do not reintroduce a token cap"                             —
B5    bounded lead-in cue                                          worth 17
B7    "and colleagues"                                             worth 4
```

Those six are implementable against v3.3 without resolving the architecture
question, and B1b is the institutional handling paper 2's recall is waiting on.

That is a better next step than consolidating, because it is not blocked, it
moves a number Alex is measuring, and it does not require choosing an
architecture first.

## What would unblock consolidation

```text
1  rc2, the four-file package or its amendment set
2  a decision on v3.3's architecture versus v3.4's §2 split
```

Neither is ours. Both are cheap to state and expensive to guess at.
