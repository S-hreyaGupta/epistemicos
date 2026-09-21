# The citation specification lineage

Established 19 September 2026, after Alex Zamurko asked whether the next step
is to consolidate the three files. It is not three files.

Updated through 21 September, when rc2 arrived. The blocker this file recorded
for two days is gone; what remains is in "What consolidation now needs".

## What exists, and what it is

```text
pre-rc1 — the scoping note rc1 was written from, found 21 September
  citation-v3.4-pre-rc1-three-additions.md            0c93ee9c…  332 lines
  citation-v3.4-pre-rc1-three-additions-first-draft.md 55fcc7b8… 274 lines
  "Citation spec v3.3 → v3.4 — the three additions", 21 August, two revisions
  52 minutes apart. Superseded by rc1, which absorbed every identifier in it.
  Kept because it shows what rc1's scope actually is: four capabilities, not
  just §2's architecture split. See RC1-IS-BIGGER-THAN-THE-SPLIT.md.

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

v3.4 rc2 — FOUND 21 September, in #citation
  citation-v3.4-rc2-architecture.md            4a60b994…   377 lines
  citation-v3.4-rc2-execution-conformance.md   4fa95af1…  1576 lines
  Both declare candidate_revision: 2. Alex Zamurko posted the five-file
  package to #citation on 28 August at 12:58 AM; files 03, 04 and 05 are
  still to be downloaded.

  Every search recorded below was of the local disk, and the files had never
  been downloaded, so none of them could have found it. The guess this file
  recorded — "#citation between 27 and 31 August" — was where it was.

  What it settles: rc2 IS four files plus a GSD pilot contract, and it
  REVISES rc1 rather than amending it — 01 and 02 carry the same spec_ids as
  rc1's 01 and 02 at candidate_revision 2. So rc2 + rc3 is the live lineage
  and rc1 is superseded.

  Six places where rc3's description of rc2 does not match rc2 are recorded
  in RC2-RC3-DISCREPANCIES.md, every one found by implementing rather than
  reading.


v3.4 rc3 — one document, present
  citation-v3.4-rc3-amendments.md              c392982e…  735 lines
  "amendment set over rc2", 31 August. A- B- C- D-series amendments.
```

### Searched for rc2 by contents, 21 September

Alex Zamurko asked whether rc2 might simply have a different name, which is a
good hypothesis: it is exactly why rc3 went unfound for two weeks, and rc3 was
eventually located by searching file *contents* rather than names.

The same search was run for rc2, three independent ways. All three come back
empty across the uploads and this repository.

```text
1  BY DECLARED REVISION — name-independent, and the strongest of the three
   Every file in this house style carries `candidate_revision` in its front
   matter. Every citation-lineage file that carries one declares 1:

       candidate_revision: 1    citation_architecture            (rc1)
       candidate_revision: 1    citation_execution_conformance   (rc1)
       candidate_revision: 1    citation_v3.4_conformance_matrix (rc1)
       candidate_revision: 1    citation_v3.4_deferred_work      (rc1)

   The only `candidate_revision: 2` anywhere belongs to LDVI v0.3, a
   different specification.

2  BY rc2's OWN CONTENT
   rc3 says rc2 defines the bibliography-side NON_PERSON_AUTHOR production and
   B4's segment splitting. Both strings appear in exactly ONE file in the
   uploads, and that file is rc3 itself, referring to them. rc2's definitions
   are not present.

3  BY UPLOAD WINDOW
   rc1's four files arrived as a batch within 71 seconds:

       2026-08-27 18:17  citation_execution_conformance_v3.4_rc1
       2026-08-27 18:17  citation_v3.4_dependency_deferred_work_register
       2026-08-27 18:18  citation_architecture_v3.4_rc1
       2026-08-27 18:18  citation_v3.4_conformance_matrix_freeze_checklist

   rc3 arrived 31 August. Between those two dates there is no citation upload
   of any kind, and a four-file package would be visible as a batch.
```

One caveat worth stating: rc3 itself carries **no front matter**, so test 1
would miss an rc2 shaped like rc3 rather than like rc1. Tests 2 and 3 do not
depend on front matter and also come back empty, and rc3 calls rc2 "the
four-file rc2 package", which is rc1's shape rather than its own.

So rc2 was most likely never shared here. #citation between 27 and 31 August,
or Alex Zamurko's own machine, are where it would be.

**That caveat was not hypothetical.** A fourth search, listing every markdown
file in Downloads beside its actual first line so a mangled name could not hide
a title, turned up `CITATI_3.MD` — a citation v3.4 document with no front matter
that uses none of the search strings. It is not rc2; it predates rc1. But it
establishes that the first three tests can miss a citation-lineage document, and
that the only search which does not depend on what a file contains is the one
that reads every title. Recorded in `RC1-IS-BIGGER-THAN-THE-SPLIT.md`.

So the shape is:

```text
   v3.3                    a separate, earlier, self-contained specification
                           ── currently governing the code ──

   v3.4 rc1  (4 files)     base package
        ↓
   v3.4 rc2  (4 files)     REVISES rc1 — same spec_ids at revision 2
        ↓
   v3.4 rc3  (amendments)  present
```

**Eight documents in two lineages.** Not three files, and not three competing
versions of one thing.

## What consolidation now needs — updated 21 September

The question this section asked for two days, "is rc2 an amendment over rc1 or
a revision of it", is answered. rc2's 01 and 02 carry rc1's own `spec_id`s at
`candidate_revision: 2`, so rc2 REVISES rc1. **rc2 + rc3 is the live lineage
and rc1 is superseded**, which is the lighter of the two outcomes this file
described.

What is still outstanding is narrower:

```text
1  rc2 files 03, 04 and 05, in #citation and not yet downloaded
2  the six places rc3's description of rc2 does not match rc2
   — RC2-RC3-DISCREPANCIES.md
```

Neither blocks consolidation the way the missing package did.

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

## rc3's amendments, checked one by one

Headed "what is available without rc2" until 21 September, when rc2 arrived.

An earlier version of this file said rc3's grammar amendments are all
self-contained. **One of them is not, and it is the one that matters most.**

Implementable against v3.3 today — rc3 states the rule in full:

```text
B1    no global token cap                                          —    = EC-3
B1a   SURNAME = (PARTICLE WS)* CORE (WS (PARTICLE WS)? CORE)?      9    = EC-4
B2    lowercase CORE, but only immediately after a matched PARTICLE 1
B5    LEAD_IN ","? CUE CITATION_LIST, CUE a closed set given here  17
B7    `and colleagues`, a closed two-token form equivalent to et al. 4
B8    possessive with MAX_POSSESSIVE_YEAR_GAP_TOKENS = 3            7
                                                                   ──
                                                                   38
```

Blocked on rc2:

```text
B1b   NON_PERSON_AUTHOR, citation side                              8
```

rc3 is explicit that this one cannot be written from rc3 alone:

> The citation-side `NON_PERSON_AUTHOR` path MUST reuse the exact lexical
> production and boundary rules rc2 defines for the bibliography-side
> `NON_PERSON_AUTHOR`. rc3 changes the permitted DETECTION SITE only. It does
> not introduce a second organisational-author grammar.

And says why, in terms that rule out working around it:

> Two grammars for one object is how the boundaries drift. rc2's production
> already carries the bound, the terminal-period handling and the maximum
> label length; restating them here would create a second definition that can
> disagree with the first.

**So the institutional handling was genuinely gated on rc2**, and inventing a
production to fill the gap was the one thing rc3 forbids by name.

**UNGATED 21 September.** rc2 §7.4 is that production and it is implemented,
called from both sides so there is one definition rather than two. It is
simpler than rc3's description of it: the head is the text before the year
paren with one trailing period removed, and it is non-person if it holds a
letter, holds no comma, and is non-empty. The no-comma rule is the whole
safeguard, and rc2 gives its reason — an organisation name with a comma cannot
be told apart from an unsupported person list, so it is unresolved rather than
guessed.

rc2 §8 is the half rc3 never mentions and it is what makes the change safe.
Syntax does not confer identity: `(Pircher Verdorfer, 2016)` and `(Population
Pyramid, 2022)` are the same shape and one is a person, so a non-person
citation is emitted only when a non-person reference confirms it.

The other six are not gated, do not require resolving the architecture
question, and are worth 38 between them.

### Implemented as of 21 September

```text
B2    lowercase CORE after a matched PARTICLE                       1   done
B5    LEAD_IN ","? CUE CITATION_LIST, closed cue set               17   done
B7    `and colleagues`                                              4   done
B8    possessive, MAX_POSSESSIVE_YEAR_GAP_TOKENS = 3                7   done
B1    no global token cap                                           —   done
B1a   SURNAME, personal, two cores                                  9   REVERTED
B1b   NON_PERSON_AUTHOR, citation side, from rc2 §7.4               8   done
B6    compact year-suffix, 2019a,b                                  2   done
D2    math-wrapped year parentheticals                              3   done, 0
§6.7  author_form / visible_authors / constraint       rc2              done
§7.4  reference authors, author_count                  rc2              done
§9.3  author_structure_mismatch                        rc2              done
A1    candidate_state, three terminal states                            done
A2    excluded_reason, closed set                                       done, 4 of 6
A4    one candidate lifecycle                                           done
A5    denominator normative, parse rate is not accuracy                 done
```

B1a was written and reverted: the production swallowed the word before the
surname, turning `In Smith (2020)` into `in smith|2020` and `World Bank (2024)`
into `world bank|2024`. The reasoning is kept in `citation_extract.py` rather
than rediscovered.

D2 is implemented faithfully and recovers nothing: the form it unwraps to is
refused by the grammar D2 says it satisfies. Sixth entry in
`RC2-RC3-DISCREPANCIES.md`, which also records that rc3's "worth" column counts
occurrences while the gold sets score works — B6 is worth 4 occurrences here
and moved recall by zero.

A2 reaches four of its six reasons. `leading_gloss` and `conversion_artifact`
appear exactly once each in the whole specs tree — in A2's own table, with a
count and no definition — and `non_citation_year` has one instance and no rule
that separates it from the eighteen corpus spans sharing its shape. See
`EXCLUSION-COVERAGE.md`.

### A note on B2

B2 records, of the August implementation, that it "already applies `(?i:…)` to
`PARTICLE` … verified against the source, not assumed." The reconstruction did
not, and that was added on 18 September as a deviation worth 35 citations. So
the deviation was in the reconstruction rather than the original. Recorded in
`PROVENANCE-GAP.md`, since it is a verified property of an artifact nobody can
run.

## What would unblock consolidation

```text
1  rc2, the four-file package or its amendment set
2  a decision on v3.3's architecture versus v3.4's §2 split
```

Neither is ours. Both are cheap to state and expensive to guess at.
