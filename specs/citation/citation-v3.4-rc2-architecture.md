---
spec_id: citation_architecture
spec_version: "3.4"
candidate_revision: 2
quality_level: 3
content_state: review_candidate
frozen_at: null
supersedes: null
superseded_by: null
authoritative_source: docs/specs/citation_architecture_v3.4_rc2.md
validation_risk: null
selected_validation_rung: null
validation_rationale: null
conformance_scopes: []
dependencies: []
external_authorities: []
review_evidence: []
governance_basis:
  artifact: authoritative_technical_spec_standard_v0.1_rc3
  sha256: e5185b132ac22e3c373fff6358538d11d21e33ce572e800190c6078bb0c2a63b
pilot_context:
  artifact: PILOT_RUNBOOK_6
  sha256: df0a587c3d9d3289e57ab48f7e28e89d7edf7d5f45dc888fb1f179374d861876
decision_rationale_context:
  artifact: CITATIONS_STATE_18
  sha256: 2514ebcf335b5ad815992f802065cddb7c4844bbcc85e7e9faa9302efee0035a
  authority: non_normative_history
---

# Citation Architecture v3.4

**Status:** Level-3 review candidate. This document defines the architecture and authority boundaries for Citation v3.4. It is not implementation authority. The GSD pilot implementation target is the separate Level-5 standalone/no-map conformance scope.

## 1. Purpose

Citation v3.4 deterministically identifies supported author–year citation surfaces, extracts supported bibliography entries, resolves citation identity only when bibliography evidence establishes it, and reports structural citation ↔ bibliography coherence without making claims about evidential support, source credibility, or scientific quality.

## 2. Scope

### 2.1 In scope

- author–year citation occurrence extraction inside a declared candidate envelope;
- bibliography-entry extraction inside the supported reference envelope;
- extraction-layer surface grouping;
- bibliography-grounded author/work identity resolution;
- structural citation ↔ bibliography reconciliation;
- explicit ambiguity and non-resolution;
- deterministic structural diagnostics;
- standalone CLI execution;
- integration with a supplied structural map in a separate scope.

### 2.2 Out of scope

- claim ↔ citation linking;
- whether the cited source supports a claim;
- citation validity, quality, ethics, plagiarism, or source credibility;
- citation recommendation;
- numeric citation identity extraction;
- general citation-style detection/configuration;
- citation-specific human-review task creation;
- repair of text absent or corrupted upstream.

## 3. Three-layer architecture

```text
LAYER 1 — EXTRACTION
What citation-like surface is present in canonical manuscript bytes?

LAYER 2 — CITATION IDENTITY RESOLUTION
What authoritative author/work identity can bibliography evidence establish?

LAYER 3 — BIBLIOGRAPHY RECONCILIATION
What structural relation exists between resolved identities, unresolved candidates,
and bibliography entries?
```

The layers MUST remain distinct because they have different authority semantics.

### 3.1 Extraction authority

Extraction establishes only source-grounded surface facts:

- source span;
- author phrase;
- year;
- citation form;
- sentence/section position;
- non-authoritative surface grouping.

Extraction syntax MAY create internal identity candidates for deterministic lookup. A candidate is not an authoritative author/work identity.

### 3.2 Identity authority

Syntax alone MUST NOT establish:

- `author_kind`;
- authoritative `citation_key`;
- distinct cited-work identity.

Authoritative citation identity is established only when bibliography resolution supports one candidate identity. Bibliography-key multiplicity may make the bibliography mapping ambiguous while leaving the identity key itself established.

### 3.3 Reconciliation authority

Reconciliation consumes:

- authoritative citation identities when available;
- bibliography identities;
- explicitly non-authoritative unmatched citation candidates when identity was not established.

Candidate-level diagnostics such as a possible missing bibliography entry MUST remain marked as candidate-level evidence and MUST NOT be counted as resolved citation identity.

## 4. Canonical manuscript and coordinates

Citation v3.4 operates on canonical UTF-8 bytes defined by the Level-5 execution contract.

Every manuscript position/span is:

```text
0-based UTF-8 byte offset
half-open [start, end)
```

Code-point counts are permitted only for the three explicitly enumerated non-coordinate operations:

1. OSA edit distance;
2. `CORE` minimum character length;
3. reference `overlong` threshold.

## 5. Supported citation profile

Citation v3.4 supports exactly:

```text
apa7_like_v1
```

The profile is folded into `citation_rule_version`, including `ET_AL_MIN_AUTHORS = 3`. It is not a selectable runtime input.

Additional profiles require a versioned specification change.

## 6. Candidate-envelope principle

Inside the declared candidate envelope, citation-like input MUST NOT disappear silently. It either:

- produces one or more extracted citation occurrences; or
- emits an explicit unresolved-extraction record preserving the candidate span.

Outside the envelope, non-emission is by declared scope.

The Level-5 specification owns the exact recognizer and grammar.

## 7. Surface grouping is not identity

Every successfully extracted occurrence has:

```text
citation_surface_group_key
```

constructed from the complete author surface and year using only the Level-5 surface normalization.

It is an extraction/aggregation key only.

It MUST NOT determine or participate in:

- author kind;
- authoritative citation identity;
- reference pairing;
- missing-reference candidate generation;
- possible-mismatch candidate generation;
- ambiguity resolution;
- duplicate-reference identity;
- matched-work counts;
- author-structure validation.

Therefore:

```text
distinct_surface_groups != distinct_works_cited
```

A surface group MUST NOT be called a work.

## 8. Complete phrase preservation and additive STOP reduction

Narrative extraction preserves the complete source `author_phrase`.

When permitted by the closed execution grammar, one STOP-reduced alternative MAY be constructed for identity lookup. The reduction is additive:

```text
complete phrase remains
+
optional reduced candidate
```

Arbitrary longest-valid-suffix parsing is prohibited.

## 9. Identity states

When bibliography identity resolution is performed, an extracted occurrence has one of four identity states:

```text
resolved_unique_reference
resolved_bibliography_key_ambiguous
author_resolution_ambiguous
identity_not_resolved
```

When bibliography identity resolution is not performed, identity state is `not_evaluated`.

Identity-state counts are separate from reconciliation diagnostics.

### 9.1 Resolved identity

An authoritative `citation_key` exists when exactly one candidate identity is supported by bibliography evidence, including the case where that same key is represented by multiple bibliography rows.

### 9.2 Author-resolution ambiguity

If full and STOP-reduced candidates receive bibliography support for different identities, the system MUST represent ambiguity and MUST NOT choose.

### 9.3 Identity not resolved

If no candidate identity receives exact bibliography support, `citation_key` remains null.

The system MAY still issue candidate-level structural diagnostics under the Level-5 contract when exactly one deterministic unmatched candidate exists. Such a diagnostic does not acquire identity authority.

## 10. Ambiguity reservation

Reference entries implicated by either:

- bibliography-key ambiguity; or
- author-resolution ambiguity

are reserved before mismatch pairing and uncited-reference computation.

Reservation means:

```text
not eligible for mismatch pairing
not emitted as uncited solely because ambiguity prevented selection
not counted as uniquely matched solely because reserved
```

The underlying bibliography defect remains reportable.

## 11. Bibliography absence

`references_source` uses exactly:

```text
detected
inferred
not_available
```

When `references_source = not_available`:

- extraction runs;
- surface grouping runs;
- identity resolution is not evaluated;
- bibliography reconciliation is not evaluated;
- authoritative work counts are unavailable;
- one bibliography-absence finding emits;
- per-citation missing-reference diagnostics MUST NOT be manufactured.

## 12. Structural diagnostics

Citation v3.4 supports:

- unresolved extraction;
- unresolved bibliography entry;
- duplicate bibliography identity;
- bibliography-key ambiguity;
- author-resolution ambiguity;
- candidate-level missing-reference evidence;
- candidate-level possible mismatch evidence;
- uncited authoritative bibliography entries;
- author-structure mismatch;
- merged-entry suspicion qualification.

Candidate-level missing/mismatch diagnostics MUST explicitly remain non-authoritative.

## 13. Author-structure coherence

For bibliography-confirmed person identities, v3.4 compares visible in-text author structure against the matched bibliography structure when the bibliography author list is confidently derivable.

Forms:

```text
exact
et_al
```

An author-structure mismatch does not erase an established identity match.

## 14. Execution scopes

### 14.1 GSD-pilot target scope

The pilot targets only:

```text
citation_v3_4_standalone_cli_nomap_apa7_like_v1
```

This scope:

- receives manuscript bytes;
- receives no Section Map;
- uses the deterministic standalone structural fallback;
- includes extraction, bibliography extraction, identity resolution, reconciliation,
  canonical JSONL output and file-output behavior.

It has no runtime dependency on Section Map or Orchestrator.

### 14.2 Standalone with supplied map

A separate conformance scope may consume a valid Section Map. That scope is not part of the GSD pilot target and remains dependency-gated.

### 14.3 EpistemicOS orchestrated pipeline

The pipeline scope requires a current/frozen Section Map contract and compatible Orchestrator contract. It is outside the GSD pilot target.

## 15. Determinism

For the pilot target scope:

```text
(canonical_manuscript_bytes, citation_rule_version)
→ byte-identical canonical output
```

For map-consuming scopes:

```text
(canonical_manuscript_bytes, exact section_map_bytes, citation_rule_version)
→ byte-identical canonical output
```

No clock, filesystem, machine, reviewer, or hidden configuration state may alter canonical output.

## 16. Failure principle

The Level-5 contract MUST distinguish:

- invalid input;
- unsupported input;
- extraction failure;
- identity not evaluated;
- identity not resolved;
- bibliography ambiguity;
- author-resolution ambiguity;
- candidate-level missing/mismatch evidence;
- system invariant failure.

Ambiguity is represented, not guessed away.

## 17. Validation boundary

The current manuscript corpus is regression/conformance discovery evidence. It is not a population-validity sample and MUST NOT support generalized accuracy claims.

## 18. Pilot/governance boundary

This architecture is non-authoritative Level 3.

The GSD pilot may plan or execute product implementation only against a Level-5 specification that is frozen/current for the pilot's declared conformance scope. The pilot runbook remains a process-governance artifact and MUST NOT create or modify citation behavior.

## 19. Architecture readiness

This architecture is content-ready for independent review when:

- every behavior delegated to Level 5 is closed there;
- the pilot target scope is explicitly separated from map/pipeline scopes;
- no architecture statement requires a mutable GSD document to establish product behavior;
- the dependency/deferred-work register contains every external or intentionally deferred item.

It remains a review candidate until independently reviewed and dispositioned.
