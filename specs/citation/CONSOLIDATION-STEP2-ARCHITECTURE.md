# Consolidation Step 2 — the architecture document, rc1 against rc2

Against Alex Zamurko's consolidation workflow v6, 21 September 2026.

> **Gate.** Every substantive change is represented in the consolidation table.
> No wording change is hidden inside a formatting-only group.

This covers **one document pair only**:

```text
citation-v3.4-rc1-architecture.md   6a615c81…  435 lines   SUPERSEDED
citation-v3.4-rc2-architecture.md   4a60b994…  377 lines   CURRENT
```

Taken first because it carries the decision that governs roughly a third of
rc2's conformance matrix. The remaining pairs — execution conformance,
conformance matrix, deferred-work register — are not covered here and Step 2 is
not complete until they are.

---

## Structural map

rc1's twenty sections against rc2's nineteen. Renames are recorded even where
the rule did not change, because a reader following rc3's section references
into rc2 will otherwise land in the wrong place.

```text
rc1                                        rc2                                   disposition
──────────────────────────────────────────────────────────────────────────────────────────
1.  Purpose                                1.  Purpose                           KEEP
1.1 In scope                               2.1 In scope                          MOVE
1.2 Out of scope                           2.2 Out of scope                      MOVE
2.  Architectural split                    3.  Three-layer architecture          REPLACE
2.1 Extraction does not create identity    3.1 Extraction authority              REPLACE
2.2 Identity requires bibliography         3.2 Identity authority                REPLACE
2.3 Reconciliation is downstream           3.3 Reconciliation authority          REPLACE
3.  Canonical manuscript / coordinates     4.  same                              MOVE
4.  Supported profile                      5.  Supported citation profile        MOVE
5.  Candidate-envelope principle           6.  same                              MOVE
6.  Citation surface vs citation identity  7.  Surface grouping is not identity  REPLACE
7.  Complete phrase preservation           8.  + additive STOP reduction         REPLACE
8.  Bibliography-grounded author kind      —                                     MOVE → 3.2
9.  Ambiguity is reserved, not repaired    10. Ambiguity reservation             MOVE
10. Bibliography absence                   11. same                              MOVE
11. Reconciliation outcome model           9.  Identity states                   REPLACE
12. Author-structure coherence             13. same                              MOVE
13. Structural coherence diagnostics       12. Structural diagnostics            MOVE
14. Execution modes                        14. Execution scopes                  REPLACE
14.1 Standalone                            14.2 Standalone with supplied map     REPLACE
—                                          14.1 GSD-pilot target scope           NEW
14.2 orchestrated pipeline                 14.3 same                             MOVE
15. Determinism                            15. same                              KEEP
16. Failure classes                        16. Failure principle                 REPLACE
17. Atomic publication                     —                                     MOVE → 02
18. Validation vs scientific accuracy      17. Validation boundary                REPLACE
19. Authority boundary                     18. Pilot/governance boundary         REPLACE
20. Architecture freeze-readiness          19. Architecture readiness            REPLACE
```

Two sections have no rc2 heading, and they are different cases. Neither is a
`DROP`.

---

## The two disappearances, checked rather than assumed

### rc1 §8 → rc2 §3.2. MOVE.

rc1's verbatim text:

> The bibliography may establish either a person-author identity or a
> non-person author identity. Citation syntax may propose a resolution
> candidate, but bibliography confirmation is the authority event.

rc2 §3.2's verbatim text:

> Syntax alone MUST NOT establish: `author_kind`; authoritative
> `citation_key`; distinct cited-work identity.
>
> Authoritative citation identity is established only when bibliography
> resolution supports one candidate identity.

Same rule, promoted from a standalone section into the three-layer split and
restated as a prohibition rather than a description. `MOVE`, and the wording
change is substantive enough to record: rc1 says what the bibliography *may*
establish, rc2 says what syntax *must not*.

### rc1 §17 → the execution conformance document. MOVE.

rc1's verbatim text:

> Normal authoritative output MUST NOT become externally authoritative before
> abort-class conditions, including reconciliation-time invariant checks, have
> completed.
>
> File output is published atomically.

`atomic` appears **0 times** in rc2's architecture and **4 times** in rc2's
execution conformance. The rule is intact and has crossed a document boundary.

That boundary is deliberate — the workflow says "preserve intentional document
boundaries" — so this is the right place for it. An implementation rule sat in
the architecture document and now sits in the execution one.

---

## The one substantive rewrite

`rc1 §11 Reconciliation outcome model` → `rc2 §9 Identity states` is a
`REPLACE`, not a rename. rc1 frames the model around **reconciliation
outcomes**; rc2 frames it around **identity states**, with resolved,
author-resolution-ambiguous and not-resolved as the three. That reframing is
what rc2's 3×3 decision table and `ambiguous_author_resolution` rest on, and it
is ten of the sixty unimplemented conformance cases.

---

## What this pair decides, and what it leaves open

The consolidated architecture document is essentially rc2's, because rc2
revises rc1 rather than amending it and every rc1 section is `KEEP`, `MOVE` or
`REPLACE` with rc2's text as the replacement. **No `DROP` and no `UNRESOLVED`
in this pair.**

That is a cleaner result than expected and it narrows the job: for this
document, consolidation is "take rc2, apply rc3's amendments", not a merge.

What it does **not** settle is the item flagged in Step 1:

```text
rc2 §3.2   Syntax alone MUST NOT establish author_kind or citation_key
v3.3 §6.3  the extractor derives citation_key at extraction time
```

That is not an rc1-versus-rc2 question — rc1 and rc2 agree. It is a
**v3.3-versus-v3.4** question, and v3.3 is a separate lineage that the running
implementation follows. It cannot be settled by comparing these two files, and
it requires a normative decision.

```text
Decision ID   CIT-ARCH-01
Issue         v3.3 derives citation_key at extraction; rc1 and rc2 both
              forbid syntax from establishing identity
Affected      ~10 conformance cases directly (C-037..C-045, C-052), and the
              implementation's whole identity path
Remainder     the implementation currently follows v3.3 for person authors
              and rc2 for non-person authors, because rc3 B1b cannot work
              the v3.3 way. So the code already sits across both.
Decision      PENDING — Alex Zamurko
```

Per the workflow's rule 6, an incomplete decision cannot change a row's
disposition, so nothing above is contingent on it. It governs the *next*
document pair, not this one.

---

## Step 2 status

```text
architecture              rc1 → rc2   COMPLETE, this document
execution conformance     rc1 → rc2   NOT STARTED, 1402 → 1576 lines
conformance matrix        rc1 → rc2   NOT STARTED
deferred-work register    rc1 → rc2   NOT STARTED, X-01..X-14 same titles
rc2 → rc3                             seven discrepancies already recorded in
                                      RC2-RC3-DISCREPANCIES.md
```

The execution conformance pair is the largest and carries the grammar. It is
the natural next piece.
