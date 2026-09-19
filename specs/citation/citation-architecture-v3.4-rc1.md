---
spec_id: citation_architecture
spec_version: "3.4"
candidate_revision: 1
quality_level: 3
content_state: review_candidate
frozen_at: null
supersedes: null
superseded_by: null
authoritative_source: docs/specs/citation_architecture_v3.4_rc1.md
validation_risk: null
selected_validation_rung: null
validation_rationale: null
conformance_scopes: []
dependencies:
  - dependency_id: section_map
    required_version: "1.1"
    required_state: frozen_current_before_citation_v3_4_freeze
    required_sha256: null
    verified_at: null
  - dependency_id: orchestrator_build_spec
    required_version: "2.3"
    required_state: current_for_epistemicos_pipeline_scope_before_freeze
    required_sha256: null
    verified_at: null
external_authorities: []
review_evidence: []
---

# Citation Architecture v3.4

**Status:** content-complete Level-3 review candidate. It is **not frozen** and has no implementation authority. Actual Citation v3.4 freeze remains gated by the Level-5 execution specification, executable conformance evidence, independent review, and the dependency checks recorded in the companion dependency register.

## 1. Purpose

Citation v3.4 provides deterministic extraction of supported author–year citation occurrences, deterministic extraction of bibliography entries, authoritative citation/work identity resolution when bibliography evidence permits it, and structural citation ↔ bibliography coherence diagnostics.

The capability is deliberately narrower than citation quality assessment. It determines what citation surfaces are present, what identity can be established from the manuscript and bibliography under the supported profile, and whether the resulting citation/reference structure is coherent.

### 1.1 In scope

- author–year citation occurrence extraction inside the declared candidate envelope;
- bibliography-entry extraction inside the supported reference envelope;
- extraction-layer citation-surface grouping;
- bibliography-grounded author/work identity resolution;
- citation ↔ bibliography reconciliation;
- ambiguity representation;
- deterministic structural diagnostics, including missing, uncited, duplicate, possible mismatch, and author-structure mismatch states;
- standalone execution and EpistemicOS orchestrated execution through one shared semantic contract;
- deterministic provenance sufficient to bind output to canonical manuscript bytes and, when supplied, the exact Section Map artifact.

### 1.2 Out of scope

- claim ↔ citation linking;
- whether a cited source actually supports a manuscript claim;
- source credibility or scientific quality;
- plagiarism, provenance of ideas, or citation ethics;
- citation recommendation;
- general bibliography-format correction;
- numeric citation extraction;
- arbitrary citation-style detection/configuration;
- human-review-task creation for citation findings;
- recovery of text absent or corrupted in an upstream conversion artifact.

## 2. Architectural split

Citation v3.4 freezes the following three-layer model:

```text
1. EXTRACTION
   What citation-like occurrence did the canonical manuscript contain?

2. CITATION IDENTITY RESOLUTION
   What authoritative author/work identity does that occurrence assert?

3. BIBLIOGRAPHY RECONCILIATION
   How does that identity relate to bibliography entries?
```

These layers have different authority semantics and MUST remain distinct.

### 2.1 Extraction does not create work identity

Successful extraction establishes a source-grounded citation occurrence. It may normalize syntax for deterministic aggregation, but it does not establish an author identity or work identity merely because the surface resembles a person citation.

A syntactically clean surface such as `Smith (2020)` is not, by syntax alone, authoritative evidence that `Smith` is a person author or that one specific work has been identified.

### 2.2 Identity requires bibliography evidence

`author_kind`, authoritative `citation_key`, and distinct cited-work identity require bibliography-grounded resolution. The supported identity kinds are:

```text
person
non_person
unresolved
```

When the bibliography is unavailable, extracted occurrences remain useful, but authoritative identity is intentionally unavailable.

### 2.3 Reconciliation is downstream of identity

Missing-reference, duplicate-reference, mismatch, matched-work and related coherence states operate only on authoritative citation/reference identities. An extraction grouping key never substitutes for a work identity.

## 3. Canonical manuscript and coordinates

Citation v3.4 operates on canonical manuscript bytes defined by the execution specification. Canonicalization is deterministic and idempotent for already canonical input.

Every manuscript position or span emitted by the capability is:

```text
0-based UTF-8 BYTE offset
half-open [start, end)
```

Code-point counts are not manuscript coordinates.

Only explicitly declared character-count operations may remain code-point based. In v3.4 those are:

1. OSA edit distance;
2. minimum `CORE` character length;
3. the reference `overlong` character-count threshold.

This separation prevents structurally valid byte spans from drifting when the manuscript contains multibyte Unicode characters.

## 4. Supported profile

Citation v3.4 supports exactly one citation profile:

```text
apa7_like_v1
```

The profile is folded into `citation_rule_version`; it is not an independently selectable runtime input.

The profile includes the author-structure rule that `et al.` implies a minimum work-author count of 3. Applying that diagnostic to a manuscript governed by a materially different citation convention is outside v3.4's conformance claim.

Supporting additional profiles requires a versioned specification change.

## 5. Candidate-envelope principle

Citation-like material is divided into two classes:

```text
inside the declared candidate envelope
outside the declared candidate envelope
```

Inside the envelope, a citation-like candidate MUST NOT disappear silently. It either:

- becomes one or more extracted citation occurrences; or
- becomes an explicit unresolved-extraction record.

Outside the envelope, absence of a record is by declared scope rather than accidental parser omission.

The Level-5 execution specification owns the exact recognizer and grammar.

## 6. Citation surface versus citation identity

Every successfully extracted occurrence carries a non-authoritative surface grouping key:

```text
citation_surface_group_key
```

Conceptually it is based only on:

```text
normalized complete author phrase
+ year
```

It is an extraction/aggregation key only.

It is **not**:

- an author identity;
- a citation identity;
- a work identity;
- a reconciliation key.

It MUST NOT determine or participate in:

- `author_kind`;
- authoritative `citation_key`;
- reference pairing;
- missing-reference findings;
- possible mismatch findings;
- ambiguity findings;
- duplicate-reference identity;
- matched-work counts;
- author-structure validation.

Therefore:

```text
distinct_surface_groups  = extraction-level quantity
distinct_works_cited     = identity-level quantity
```

A surface group MUST NOT be described as a distinct cited work.

## 7. Complete phrase preservation and additive reduction

Narrative citation extraction preserves the complete source author candidate.

`author_phrase` always represents the complete extracted author surface before structural STOP reduction. Reduction does not rewrite the source phrase.

When the complete narrative phrase does not support the person-form candidate, the execution layer may construct one deterministic alternative through the closed structural STOP/discard mechanism. This alternative is **additive**, not destructive:

```text
full phrase remains available
+
optional stop-reduced person candidate
```

The system does not use arbitrary longest-suffix parsing. That prohibition prevents an institutional surface such as `World Bank (2024)` from silently collapsing into `Bank (2024)`.

## 8. Bibliography-grounded author kind

The bibliography may establish either a person-author identity or a non-person author identity. Citation syntax may propose a resolution candidate, but bibliography confirmation is the authority event.

Consequences:

- `World Bank (2024)` may resolve as `non_person` when the bibliography supports that identity;
- `Panel Smith (2020)` may produce both a full-phrase candidate and a STOP-reduced person candidate;
- when distinct candidates resolve to distinct bibliography identities, the occurrence is author-resolution ambiguous rather than guessed;
- when no bibliography exists, all extracted occurrences retain `author_kind = unresolved`.

## 9. Ambiguity is reserved, not repaired away

Ambiguity is an explicit state.

Two different ambiguity classes are architecturally distinct:

1. **bibliography-key ambiguity** — one authoritative citation identity maps to multiple bibliography entries;
2. **author-resolution ambiguity** — the complete phrase and STOP-reduced alternative both have bibliography support for different identities.

Reference entries named by either ambiguity are **ambiguity-reserved** before mismatch repair and uncited-reference computation.

Reservation means:

```text
not available to mismatch pairing
not emitted as uncited merely because this ambiguous occurrence did not choose them
not counted as uniquely matched solely because they were reserved
```

The bibliography defect itself, such as duplicate keys, remains reportable.

## 10. Bibliography absence

`references_source` has one vocabulary across Citation v3.4:

```text
detected
inferred
not_available
```

When `references_source = not_available`:

- extraction still runs;
- surface grouping still runs;
- citation identity resolution does not run;
- bibliography reconciliation does not run;
- authoritative citation/work counts are unavailable rather than zero;
- one run-level bibliography-absence finding is emitted;
- synthetic per-citation missing-reference findings are forbidden.

This is intentionally weaker than a one-pass design that manufactures `surname|year` identities from citation syntax. The loss of standalone identity is accepted in exchange for preserving epistemic authority boundaries.

## 11. Reconciliation outcome model

When bibliography reconciliation is performed, every citation occurrence belongs to exactly one final outcome class:

```text
unique_reference_match
bibliography_key_ambiguous
reference_missing
possible_mismatch
author_resolution_ambiguous
unresolved
```

The partition is conditional on reconciliation being performed. Bibliography absence is a run-level condition, not a seventh occurrence state.

Counts that were not evaluated are `null`, not `0`.

## 12. Author-structure coherence

For bibliography-confirmed person identities, v3.4 may compare the in-text visible author structure with the ordered author structure extracted from the matched bibliography entry.

The in-text forms are conceptually:

```text
exact
et_al
```

`exact` requires the visible authors to equal the complete work-author list in count and order.

`et_al` requires the visible authors to match the corresponding ordered prefix and the work to satisfy the profile's minimum-author rule.

A structural mismatch does not erase the identity match. It is a diagnostic about the matched pair.

Exact-form mismatches are conformance-significant run findings. `et_al` mismatch is reported but does not itself fail the run in v3.4 because its threshold is profile-dependent and has not yet been independently calibrated across styles.

## 13. Structural coherence diagnostics

The architecture supports deterministic diagnostics for:

- missing references;
- uncited references;
- duplicate bibliography identity keys;
- bibliography-key ambiguity;
- possible deterministic mismatch repair candidates;
- author-resolution ambiguity;
- author-structure mismatch;
- suspect merged bibliography entries.

A merge suspicion qualifies a missing-reference diagnostic; it does not suppress the record or assert that the hidden work definitely exists.

## 14. Execution modes

### 14.1 Standalone

The standalone tool may run without a Section Map. In that mode it uses the deterministic structural fallback defined by the Level-5 contract.

If no recoverable bibliography exists, the run continues in bibliography-absent mode.

### 14.2 EpistemicOS orchestrated pipeline

The orchestrated path has one structural source of truth:

```text
reviewed Section Map
```

For orchestrated execution:

- a compatible Section Map MUST be supplied;
- it MUST represent the same canonical manuscript bytes;
- the required review state MUST satisfy the Orchestrator prerequisite;
- the no-map structural fallback is not an orchestrated execution path.

The citation step does not independently re-derive a competing bibliography boundary when an authoritative map has been supplied.

## 15. Determinism

The Level-5 contract closes all output-affecting variables.

Conceptually:

```text
standalone:
    canonical manuscript bytes
    + citation_rule_version
    → identical output bytes

orchestrated:
    canonical manuscript bytes
    + exact Section Map bytes
    + citation_rule_version
    → identical output bytes
```

The execution contract therefore pins:

- normalization;
- Unicode version;
- candidate envelope;
- grammar;
- profile;
- closed vocabularies;
- identity construction;
- ambiguity rules;
- reconciliation order;
- sorting and tie-breaking;
- serialization;
- failure semantics.

No timestamp, random identifier, machine state, filesystem state or mutable external configuration may affect canonical output bytes.

## 16. Failure classes

The architecture distinguishes:

- normal success with no findings;
- normal success with deterministic findings;
- unsupported citation-style dominance;
- invalid structural input;
- standalone heading-contract failure;
- invalid UTF-8;
- internal invariant failure.

Internal invariant failure is a system failure, not a manuscript-quality finding.

## 17. Atomic publication

Normal authoritative output MUST NOT become externally authoritative before abort-class conditions, including reconciliation-time invariant checks, have completed.

File output is published atomically. An invariant failure cannot leave a partial authoritative artifact that looks like a shorter valid JSONL run.

## 18. Validation versus scientific accuracy

Freezing this contract establishes that the implementation is tested against the declared deterministic specification. It does **not** establish population-level extraction accuracy.

The current 11-paper corpus is a regression/conformance discovery corpus only. It MUST NOT be used to make generalized accuracy or prevalence claims.

A powered validation study with a defined error taxonomy is deferred separately.

## 19. Authority boundary

This Level-3 document is the non-authoritative architecture baseline for Citation v3.4. It describes the stable architecture and authority model.

Implementation authority, once independently reviewed and frozen/current, belongs to the separate Level-5 Citation Execution + Conformance Specification v3.4.

The Level-5 specification is intentionally self-contained for observable behavior and MUST NOT rely on mutable Level-3 prose to determine a conformance result.

## 20. Architecture freeze-readiness conditions

This candidate is content-complete when all of the following remain true under independent review:

- three-layer split remains explicit;
- surface grouping cannot acquire identity authority;
- bibliography confirmation remains required for authoritative author/work identity;
- byte-coordinate model is internally consistent;
- standalone/orchestrated structural-source boundary is unambiguous;
- ambiguity reservation precedes repair/unmatched logic;
- bibliography absence is run-level and nullable-summary semantics are preserved;
- architecture contains no implementation-only grammar/schema detail that conflicts with the Level-5 contract;
- every external dependency required for actual Citation v3.4 freeze is pinned in the companion dependency register;
- no unresolved architecture-level behavioral choice remains.

Passing these content checks makes this a **freeze-ready review candidate**, not a frozen specification.
