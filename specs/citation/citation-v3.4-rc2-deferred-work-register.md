---
document_id: citation_v3_4_dependency_deferred_work_register
version: "2.0"
bound_architecture:
  spec_id: citation_architecture
  spec_version: "3.4"
  candidate_revision: 2
  sha256: 4a60b994845a323d5ee1170559d3f9017abf62aeaf4bc7fc0bc1992e335adb9e
bound_execution_spec:
  spec_id: citation_execution_conformance
  spec_version: "3.4"
  candidate_revision: 2
  sha256: 4fa95af15755c569d5a5135321a22fdfab85464c4ee92c09a8808d73318aa466
pilot_target_scope: citation_v3_4_standalone_cli_nomap_apa7_like_v1
status: current_candidate_register
---

# Citation v3.4 — Dependency + Deferred-Work Register

This register closes the implementation boundary for the GSD pilot target and separately records map/pipeline dependencies that do not affect the no-map standalone scope.

## 1. Dependency classes

```text
PILOT_HARD_DEPENDENCY
    required before the GSD pilot may Execute/Verify the Citation product task

SCOPE_HARD_DEPENDENCY
    required only for the named non-pilot conformance scope

RUNTIME_EXTERNAL_AUTHORITY
    deterministic external behavior pinned by version and demonstrated by conformance

INTERNAL_RULE
    defined completely in the Level-5 Citation contract

NON_AUTHORITATIVE_CONTEXT
    process/history context; cannot change Citation output
```

## 2. Active dependencies

| ID | Dependency | Class | Scope | Required state |
|---|---|---|---|---|
| D-01 | Citation Execution + Conformance v3.4 rc2 | PILOT_HARD_DEPENDENCY | pilot | exact rc2 bytes must complete independent review/conformance and become frozen/current before GSD Execute/Verify |
| D-02 | Unicode 15.0.0 behavior | RUNTIME_EXTERNAL_AUTHORITY | pilot + other scopes | NFC/simple-lowercase behavior required by Level5 demonstrated in execution environment |
| D-03 | Section Map v1.1 | SCOPE_HARD_DEPENDENCY | standalone-with-map + pipeline | exact frozen/current artifact + SHA + disposition |
| D-04 | Orchestrator v2.3 or formal successor | SCOPE_HARD_DEPENDENCY | pipeline only | current compatible contract + exact identity |
| D-05 | canonical Citation transform | INTERNAL_RULE | all | invalid UTF-8 reject → CRLF/CR→LF → NFC; owned by Level5, not by GSD |
| D-06 | `apa7_like_v1` | INTERNAL_RULE | all | folded into `citation_rule_version`; ET_AL_MIN_AUTHORS=3 |
| D-07 | Authoritative Technical Specification Standard rc3 | NON_AUTHORITATIVE_CONTEXT | governance | process basis only; SHA `e5185b132ac22e3c373fff6358538d11d21e33ce572e800190c6078bb0c2a63b` |
| D-08 | PILOT_RUNBOOK (6) | NON_AUTHORITATIVE_CONTEXT | pilot process | process contract only; SHA `df0a587c3d9d3289e57ab48f7e28e89d7edf7d5f45dc888fb1f179374d861876` |
| D-09 | Citation Architecture v3.4 rc2 | NON_AUTHORITATIVE_CONTEXT | all | architecture context; Level5 is self-contained for implementation |

## 3. Pilot dependency rule

The pilot target is:

```text
citation_v3_4_standalone_cli_nomap_apa7_like_v1
```

Therefore:

```text
Section Map is NOT a pilot dependency.
Orchestrator is NOT a pilot dependency.
```

The GSD pilot preflight MUST instead verify the exact frozen/current Level-5 Citation artifact and the pilot manual comparator hash.

A filename, branch name, or prose statement such as “final” is insufficient authority evidence.

## 4. rc1 → rc2 normative correction

rc2 resolves a contradiction in rc1 between:

```text
syntax does not confer authoritative author_kind/citation_key
```

and rc1 reconciliation text that attempted to classify a `reference_missing` / `possible_mismatch` using a supposedly resolved citation key even when no exact bibliography identity existed.

Final rc2 rule:

```text
exact bibliography support
    → may establish authoritative citation_key

no exact bibliography support
    → citation_key remains null
    → identity_class = identity_not_resolved

exactly one deterministic unmatched internal candidate
    → candidate-level missing_reference / possible_mismatch MAY emit
    → identity_authority = "candidate"
    → diagnostic MUST NOT increase resolved_citation_occurrences

two distinct unmatched candidates
    → no missing/mismatch diagnostic
    → identity remains not resolved
```

This change is normative and is the reason the Level-5 candidate is `candidate_revision: 2`.

## 5. Final terminology dispositions

| Concept | Final term |
|---|---|
| extraction failure record | `unresolved_citation` |
| identity lookup ran but established no identity | `author_resolution=not_resolved` |
| identity lookup did not run | `author_resolution=not_evaluated` |
| unknown author kind | `author_kind=undetermined` |
| identity-level unresolved count | `identity_not_resolved_occurrences` |
| extraction-level group | `citation_surface_group_key` |
| non-authoritative missing diagnostic key | `candidate_key` |
| authoritative citation identity | `citation_key` |

## 6. L–T and run-finding disposition

| Item | Final v3.4 disposition |
|---|---|
| L | already fixed by v3.3 person grammar; obsolete exposure claim not carried |
| M | UTF-8 byte-coordinate invariant + exactly three code-point exceptions |
| N | absorbed by standalone bibliography detection and `references_source` |
| O | targeted `merge_suspected`; diagnostic retained and explicitly candidate-level where identity unresolved |
| P | citation→human review deferred outside Citation v3.4 |
| Q | universal total deterministic ordering |
| R | resolved by explicit determinism tuples |
| S | numeric citation identities out of envelope |
| T | `unresolved_reference.reason` closed, including `no_year` |
| R1 | possessive `'s`/`’s` stripped only when deriving person identity candidate |
| R2 | closed PREFIX set + longest-match precedence + no silent in-envelope drop |

## 7. Prefix attestation register

v3.4 closed PREFIX additions:

| Prefix | Basis |
|---|---|
| `for a similar approach, see` | observed in current corpus |
| `for example, see` | approved scholarly-formula attestation |
| `for instance, see` | approved scholarly-formula attestation |
| `for discussion, see` | approved scholarly-formula attestation |
| `for a review, see` | approved scholarly-formula attestation |

All require executable golden coverage. Runtime prefix discovery is forbidden.

## 8. Explicit deferred work

### X-01 — Citation → human review integration
Deferred. Requires a separate lifecycle/review-surface contract.

### X-02 — Additional citation profiles
Deferred. Multi-profile runtime selection is outside v3.4.

### X-03 — Numeric citation identity extraction
Deferred/out of envelope.

### X-04 — Square-bracket author–year forms
Deferred/out of envelope.

### X-05 — Parenthesis-free author–year forms
Deferred/out of envelope.

### X-06 — Footnote/superscript citation identity extraction
Deferred/out of envelope except unsupported-style detection.

### X-07 — Broader bibliography author grammars
Deferred. Includes comma-containing organization authors and richer full-forename list parsing.

### X-08 — ConversionArtifactAnnotations / conversion repair
Deferred upstream. Citation consumes canonical bytes actually present.

### X-09 — Claim ↔ citation linking
Deferred.

### X-10 — Citation validity / evidential support / source credibility
Deferred.

### X-11 — Population-level validation study
Deferred but required before generalized accuracy claims.

### X-12 — Prefix vocabulary expansion
Deferred; requires versioned change + attestation + interaction goldens.

### X-13 — Fuzzy identity acquisition
Deferred. v3.4 candidate-level `possible_mismatch` MUST NOT acquire identity authority.

### X-14 — Column-interleaving / malformed PDF repair
Deferred upstream.

## 9. Known limitations permitted for the pilot scope

- standalone no-bibliography mode cannot establish cited-work identity;
- all-caps author cores are unresolved extraction;
- comma-containing organization bibliography heads may remain unresolved;
- full-forename references may establish first-surname identity without a complete author list;
- the sentence splitter is a deterministic approximation;
- upstream conversion corruption is not repaired;
- `et_al` author-structure mismatch does not alone force exit1;
- numeric, footnote and superscript citation identities are unsupported.

No new “expected limitation” may be invented after a failing pilot/corpus result without a versioned specification disposition.

## 10. GSD-pilot entry conditions

Before the pilot reaches GSD **Execute**:

1. exact Level-5 rc2 candidate has completed independent review;
2. pilot-scope conformance evidence is accepted;
3. HIGH-rung focused kernel evidence is accepted;
4. final freeze/disposition makes the Level-5 document frozen;
5. pilot target scope is current;
6. the manual comparator is frozen and hashed in the pilot baseline;
7. the installed GSD preflight in `PILOT_RUNBOOK (6)` passes.

A planning finding that reveals a missing normative behavior is a **spec finding**, not permission for GSD/Claude/Codex to choose behavior.

## 11. Current register verdict

```text
PILOT SCOPE BOUNDARY:              CLOSED
SECTION MAP PILOT DEPENDENCY:      NONE
ORCHESTRATOR PILOT DEPENDENCY:     NONE
HIDDEN PILOT PRODUCT WORK:         NONE IDENTIFIED
EXECUTION SPEC INDEPENDENT REVIEW: PENDING
EXECUTABLE PILOT CONFORMANCE:      PENDING
PILOT SCOPE FROZEN/CURRENT:        NOT YET
```
