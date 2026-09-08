# A.1-E Gap Object Schema v1.4 — EpistemicOS

**Status:** normative logical data model once the Schema Freeze Check (§11) passes. Current normative version: `A1E-GS-1.4` — a narrow multi-instance-routing amendment of the frozen `A1E-GS-1.3`.
**Implements:** `A1E_gap_extraction_contract_v1-2.md` (frozen, normative). The capability boundary is not modified or reinterpreted.
**Excludes by design:** detection logic, prompts, KB rules, object-vs-scope linguistic rules, merge algorithms, verifier logic, state-promotion logic, characterization, analysis, database implementation.

**Revision record (v1.3 → v1.4):** A1E-GS-1.4 adds canonical candidate-side representation for the frozen Step-11 extraction-instance routing set required by A1E-SM-1.4. Exactly these schema changes are made: 1. GAP candidates may carry one frozen `routing_set` bound to the Step-11 extraction bundle. 2. `routing_set` contains exactly one routing entry per `extraction_instance_id`. 3. each routing entry has exactly one routing status from: UNROUTED, ROUTING_REVIEW_OPEN, CREATED, ATTACHED. 4. CREATED and ATTACHED carry exactly one `target_gap_id`. 5. UNROUTED and ROUTING_REVIEW_OPEN carry no `target_gap_id`. 6. the former singular GAP routing representation `routing_outcome=promoted|attached_as_restatement` plus `promoted_gap_id` / `attached_to_gap_id` is superseded. 7. `rejected_non_gap` and `uncertain_queued` remain candidate-level outcomes. 8. one compound candidate remains one candidate regardless of N routing entries. 9. no gap_record semantic fields, extraction semantics, identity rules, lifecycle transitions, candidate-universe semantics, or verification semantics are changed.

**Revision record (v1.2 → v1.3):** A1E-GS-1.3 adds `method` to `artifact_kind` so existing non-measure methodological artifacts can be represented canonically. No other schema semantics changed. (`A1E-GS-1.2` is superseded only for downstream artifacts that depend on the artifact_kind ontology; the change is the single authorized ontology amendment identified by Step 8's SI-OR-1.) **Final-issuance correction (same version):** 1. canonical completion semantics clarified for object-denoting vs carrier/reference anaphors (I-44, I-45); 2. V3 mention/span references corrected; 3. V5 no longer infers `about` from a model name; 4. V11 repaired to validate as a complete GS-1.3 gap_record. No other schema semantics changed.

**Revision record (v1.1 → v1.2):** (1) external object resolution separated from the canonical semantic payload — `object_link` removed from `affected_object` / `about` / `uncited_referent`; mutable `object_resolution_link` entries live in the processing envelope; `surface_only` becomes the *absence* of a resolution; external canonicalization may now change after semantic freeze without touching the record; (2) candidate routing outcome (`disposition` → `routing_outcome`) made optional until routing occurs — no `pending` value invented; `boundary_state` likewise optional until boundary classification runs (same principle, directly entailed); `gap_id` timing un-fixed: created at record instantiation, ordering owned by Steps 4/9; (3) field-level traceability completed for semantic primitives — `deficiency.source_trace_refs` and `affected_object.type_trace_refs` added as `normalized_with_trace` classifications; generated descriptors structurally cannot ground them; (4) `about` made extraction-safe — when present it MUST be source-grounded (surface form + mention refs); registry-known artifact↔phenomenon relations belong to the Research Object Graph, never to the canonical record; (5) semantic-freeze boundary enumerated (may-change vs must-not-change after `extraction_verified`); (6) step ownership re-audited (Steps 3, 4, 5, 6, 8, 9, 13) — including the note that the predicate→relation lexicon is Step-6 material, while the relation/kind enums themselves remain contract-frozen.

---

## 1. Design principles

1. **Contract-bound.** Every structure implements v1.2; no field exists that the contract does not require or permit.
2. **Semantic/workflow separation with staged freeze.** A canonical `gap_record` carries meaning and may be assembled and amended during extraction and resolution; at the State-Machine-designated verified condition (`extraction_verified`) its semantic content freezes (enumerated in §2) except through explicit versioning/correction procedures defined later. The mutable `gap_processing_envelope` carries state, verification, review, and **external object resolution** at all times. Verifier execution never rewrites semantic content.
3. **Triple + preserved proposition, payload-pure.** The owned semantics are `(relation, knowledge_kind, affected_object)` plus the source-grounded proposition. No scope structure and **no external-resolution state** exists in the canonical payload.
4. **Traceability by construction, down to the primitives.** Every substantive extracted element — including `relation`, `knowledge_kind`, `object_kind`, `artifact_kind` — carries source evidence; generated content is structurally distinguishable from manuscript wording and can never be the sole ground for any primitive or object.
5. **Spans are defined once.** Each top-level artefact holds one authoritative `source_spans` collection; every other structure references spans by ID. No two copies of a span can diverge.
6. **Absence over ambiguous null.** Conditional fields are absent when
inapplicable; null appears only where null itself has defined meaning.

Absence also means things: no resolution entry = surface-only.

For non-GAP / UNCERTAIN candidates, absence of `routing_outcome` means no
candidate-level routing outcome has yet been recorded.

For GAP candidates, `routing_outcome` is always absent; routing progress
and completion are represented exclusively by `routing_set`.
7. **Conservative identity, stored not computed.** The schema stores merge *outcomes*; algorithms live in the Merge & Gap Identity Rules Spec.
8. **No interpretation fields.** Only paraphrase-faithful labels persist; taxonomy, mode, stance, scope, judgments, and externally inferred relations are structurally impossible.
9. **Non-gap material never contaminates the canonical record.** Candidates, UNCERTAIN items, and diagnostics are separate artefacts; `gap_record.boundary_class` is the literal `GAP`.
10. **Frozen where the contract froze; owned slots elsewhere.** Contract-fixed enums are closed here; lifecycle, verification, escalation, merge-basis, and predicate-lexicon vocabularies belong to their owning specs, with only contract-reserved codes registered.

---

## 2. Top-level architecture

**Architecture: Option B (canonical record + processing envelope), staged freeze, resolution in the envelope.**

```text
gap_run  (1 per manuscript execution: shared version provenance)
  │
  ├── gap_candidate (0..n)  — every detected candidate; outcomes populate when
  │       │                   their operations run (Step 4 owns transitions)
  │       ├── non-GAP / UNCERTAIN candidate-level outcome (routing_outcome):
  │       │     ├── rejected_non_gap ──────  (terminal; retained for audit/eval)
  │       │     └── uncertain_queued ──────  (the UNCERTAIN queue)
  │       └── GAP → routing_set (one frozen entry per extraction_instance_id):
  │             ├── extraction_instance I1 ── CREATED ───► G1 (new gap_record)
  │             ├── extraction_instance I2 ── ATTACHED ──► G7 (existing gap_record)
  │             └── extraction_instance I3 ── CREATED ───► G2 (new gap_record)
  │
  │       One gap_candidate remains one candidate even when routing_set contains N
  │       entries. routing_set cardinality does not alter candidate-universe cardinality.
  │       ▼
  ├── gap_record (canonical; semantics freeze at verified state)
  │        ▲ 1:1
  │        └── gap_processing_envelope
  │              • lifecycle / verifier history / review / human review
  │              • object_resolutions[]  ← external object identity lives HERE, never in the record
  │
  └── diagnostic_notice (0..n; never gap objects)
```

**Semantic freeze boundary (correction 5).** After `extraction_verified`:

| MAY change (envelope & beyond) | MUST NOT change silently (canonical record) |
|---|---|
| Verifier history; human-review metadata | `source_spans` |
| **External object-resolution links** (`object_resolutions`) | `explicitness`; `context_support` |
| Downstream Research Object Graph links | `deficiency` (relation, kind, traces) |
| Operational metadata; lifecycle codes; review flags | `affected_object` source representation (kinds, traces, mention, `about`) |
| | Complete asserted proposition (assertion refs + normalized) |
| | `contrast` as extracted; `persistence_reasons` as extracted; `claim_links` as resolved at freeze |

The later correction/versioning mechanism is deliberately not designed here (OI-S7).

**Entity decisions (carried and revised):**

- `gap_run`, `gap_candidate`, `gap_record`+envelope (1:1), `diagnostic_notice` — retained. `uncertain_candidate` remains folded into `gap_candidate`.
- **D12 (new) — object resolution placed in the envelope.** Chosen over a third top-level entity: the envelope is already the mutable 1:1 companion of the record, so resolution history gains mutability, lineage, and timestamps for free, and the entity count stays stable. A dedicated `object_resolution_link` structure inside the envelope keeps resolution audit-clean without touching frozen semantics.

**Assessed design decisions (revised set):**

- **D1 — `object_kind` + conditional `artifact_kind`.** Contract-fixed kinds; two orthogonal enums condition artifact-only fields cleanly.
- **D2 — Relationship decomposition deferred.** No `participants`; Step-8 Object Rules material.
- **D3 (revised) — External identity is enrichment, never payload.** Resolution states (`provisional_link`, `externally_canonicalized`) exist only in envelope `object_resolutions`; `surface_only` is now the *absence* of a resolution entry — one fewer stored state, with absence carrying the meaning (principle 6). A.1-E never derives an external canonical ID; `externally_canonicalized` records an ID issued by the external owner.
- **D4 — No `same_claim` link.** Confirmed identity = one canonical record with multiple spans.
- **D5 — `related_claim` retained narrowly**; basis vocabulary owned by Step 9.
- **D6 — Legacy contrast `stance` excluded** (interpretive; MOVE_TO_A1-C).
- **D7 (extended) — Traceability by construction, now covering primitives.** `deficiency.source_trace_refs` and `affected_object.type_trace_refs` treat the classifications as `normalized_with_trace`; one shared trace list per structure avoids duplication. Because all trace refs resolve only to `source_spans` entries and generated descriptors have no `span_id`, descriptors structurally cannot ground primitives (I-41).
- **D8 — Per-reference citation review as an owned code** on the citation link (Verification Spec owner).
- **D9 — Span pool** (one definition per artefact; refs elsewhere).
- **D10 (revised) — `spawned_claim_ref`** supports pre-promotion candidates; **gap_id timing is not fixed here**: `gap_id` is created when a canonical `gap_record` is instantiated; the lifecycle event and its ordering relative to merge/resolution are owned by the State Machine (Step 4) and the Merge & Gap Identity Rules (Step 9).
- **D11 — Owned-code strategy** (slots + owners + contract-reserved codes only). Step-6 note: the mapping from manuscript predicates to `relation` values (the predicate lexicon) is owned by the Deficiency Predicate Registry; this schema stores only the contract-frozen enum values.

---

## 3. Complete normative YAML schema

Types: `string`, `int`, `timestamp` (ISO-8601 string), `enum(...)` (closed), `code(OWNER)` (controlled string; vocabulary owned by OWNER; contract-reserved codes in §5B), `[T]` list, `object`. `req` = required; `opt` = optional and **absent when inapplicable**; explicit null semantics stated wherever null is permitted.

```yaml
# ─────────────────────────────────────────────
# Reusable structures
# ─────────────────────────────────────────────

source_span:                     # defined ONLY inside a top-level artefact's source_spans collection
  span_id: string                # req; unique within the containing top-level artefact (D9)
  document_id: string            # req
  document_version: string       # req; exact text snapshot the offsets index
  section_id: string             # req
  section_role: code(SEGMENTATION)   # req
  paragraph_id: string           # req
  char_start: int                # req; >= 0
  char_end: int                  # req; > char_start
  text: string                   # req; verbatim copy of the span

trace:                           # only where class membership needs evidence (D7)
  traceability_type: enum(verbatim, normalized_with_trace, referenced,
                          linked_provisional, generated_flagged)   # req
  evidence_refs: [string]        # req; >=1; span_ids (or link ids) within the same artefact

object_mention:                  # NO external link lives here (D3): resolution is envelope enrichment
  surface_form: string           # req; manuscript wording (verbatim; consistent with referenced span text)
  mention_span_refs: [string]    # req; >=1; span_ids in the containing artefact's source_spans
  generated_descriptor:          # opt; a system-written LABEL for a grounded referent — never a substitute
    text: string                 #   for an absent object (I-9b), never sole ground for any primitive (I-41)
    trace: trace                 # req within block; traceability_type must be generated_flagged;
                                 #   evidence_refs = motivating span_ids

affected_object:
  object_kind: enum(phenomenon, construct, relationship, knowledge_artifact)  # req (D1)
  artifact_kind: enum(proposition, theory, model, framework, assumption, measure, method)  # `method` added [v1.3]
                                 # req iff object_kind = knowledge_artifact; absent otherwise (I-10)
  type_trace_refs: [string]      # req; >=1; span_ids evidencing the kind classification(s); shared trace
                                 #   for object_kind and (when present) artifact_kind — treated as
                                 #   normalized_with_trace (correction 3; I-40, I-41)
  mention: object_mention        # req; identifies WHAT the deficient knowledge is about; source-grounded
                                 #   or completion-recoverable (I-9b); never a scope container (I-9);
                                 #   anaphor rule I-44; span coherence I-45
  about:                         # opt; only when object_kind = knowledge_artifact; the artifact's subject
                                 #   matter AS ASSERTED IN THE MANUSCRIPT (correction 4; I-42). External
                                 #   registry knowledge never creates this relation.
    surface_form: string         # req within block; verbatim
    mention_span_refs: [string]  # req within block; >=1

deficiency:
  relation: enum(ABSENT, LIMITED, CONFLICTING, UNTESTED,
                 CONSTRAINED, DISCONNECTED, CHALLENGED)             # req; contract-frozen; no aliases
  knowledge_kind: enum(evidence, theory, method,
                       practice_alignment, unspecified)             # req; contract-frozen; no aliases
  source_trace_refs: [string]    # req; >=1; span_ids evidencing the relation and kind classifications;
                                 #   one shared trace for the pair — normalized_with_trace (I-39, I-41)

context_support:                 # present iff explicitness = context_supported (I-26)
  dependency_type: enum(anaphora, ellipsis, omitted_argument,
                        referential_dependency, other_linguistic_dependency)  # req
  dependency_expression: string  # req; verbatim expression in the primary span requiring completion
  support_span_refs: [string]    # req; >=1
  note: string                   # opt; req iff dependency_type = other_linguistic_dependency

normalized_proposition:          # normalized_with_trace
  text: string                   # req; completed controlled restatement; contextual wording only as
                                 #   unclassified content
  source_trace_refs: [string]    # req; >=1; ⊆ assertion refs ∪ permitted support refs (I-2)
  normalization_method: code(NORMALIZATION_SPEC)   # req

citation_link:                   # referenced
  link_id: string                # req; unique within artefact
  resolution_status: enum(resolved, unresolved)                     # req
  registry_citation_id: string   # req iff resolved; ABSENT iff unresolved (I-11)
  citation_span_ref: string      # req; both states
  verbatim_citation_text: string # req iff unresolved (durable verbatim copy); opt iff resolved
  unresolved_review_status_code: code(VERIFICATION_SPEC)
                                 # req iff unresolved; ABSENT iff resolved (D8)
                                 # NOTE: no field, in any state, judges citation support (I-13)

contrast_entry:
  entry_id: string               # req; unique within record
  attributed_span_refs: [string] # req; >=1
  normalized_attributed_proposition: normalized_proposition   # opt
  citation_links: [citation_link]        # req; 0..n; empty = uncited entry
  uncited_referent: object_mention       # opt; generalized referent when uncited (linkless by D3)
                                         # I-36: citation_links >=1 OR uncited_referent present

contrast:
  status: enum(reported, not_reported)   # req
  entries: [contrast_entry]              # req; >=1 iff reported; [] iff not_reported (I-30a)

persistence_reason:
  reason_id: string              # req; unique within record
  reason_span_refs: [string]     # req; >=1
  normalized_descriptor: normalized_proposition   # opt
  citation_links: [citation_link]                 # req; 0..n
  spawned_claim_ref:             # opt; ABSENT = the reason asserts no independent deficiency (I-16)
    target_type: enum(candidate, gap_record)      # req within block (D10)
    target_id: string            # req within block; existing artefact (I-17); reciprocity per I-29

claim_link:
  link_type: enum(possibly_same_claim, related_claim, reason_of)    # req (D4)
  target_gap_id: string          # req; existing gap_record; != own gap_id (I-31)
  unmerged_basis_code: code(MERGE_RULES_SPEC)     # req iff possibly_same_claim; absent otherwise (I-32)
  relation_basis_code: code(MERGE_RULES_SPEC)     # req iff related_claim; absent otherwise
  source_persistence_reason_id: string            # req iff reason_of; absent otherwise (I-29)

# ─────────────────────────────────────────────
# Canonical semantic object
# ─────────────────────────────────────────────

gap_record:                      # amendable during extraction/resolution; semantic content frozen at the
                                 # verified condition per §2 table (I-38); gap_id itself immutable
  gap_id: string                 # req; opaque; globally unique within the EpistemicOS instance; immutable;
                                 #   created when a canonical gap_record is instantiated. The lifecycle
                                 #   event and its ordering relative to merge/resolution are owned by the
                                 #   State Machine Spec (Step 4) and Merge & Gap Identity Rules (Step 9);
                                 #   never reassigned by later Research Object Graph resolution
  schema_version: string         # req
  document_id: string            # req
  document_version: string       # req; all contained spans must match (I-33a)
  boundary_class: enum(GAP)      # req; literal GAP only (I-30)
  explicitness: enum(explicit, context_supported)                   # req (I-20)
  source_spans: [source_span]    # req; >=1; single authoritative span collection (D9; I-0; I-3a)
  gap_evidence:                  # req; >=1; exactly one primary (I-1)
    - role: enum(primary, restatement, corroborating)               # req
      span_ref: string                                              # req
  context_support: context_support   # req iff context_supported; ABSENT iff explicit (I-26)
  deficiency: deficiency         # req; includes source_trace_refs (I-39)
  affected_object: affected_object   # req; includes type_trace_refs (I-40); NO resolution state (I-35)
  proposition:
    assertion_span_refs: [string]    # req; >=1; includes primary (I-27); full wording preserved here
    normalized: normalized_proposition                              # req (I-2)
  contrast: contrast             # req
  persistence_reasons: [persistence_reason]                         # req; 0..n
  claim_links: [claim_link]      # req; 0..n

# ─────────────────────────────────────────────
# Processing envelope (mutable at all times; 1:1 with gap_record)
# ─────────────────────────────────────────────

object_resolution_link:          # external object identity — enrichment, never payload (D3, D12)
  resolution_id: string          # req; unique within envelope
  subject:                       # req; WHICH grounded referent of the record this enriches
    target_kind: enum(affected_object, about, uncited_referent)     # req
    contrast_entry_id: string    # req iff target_kind = uncited_referent; absent otherwise
  link_status: enum(provisional_link, externally_canonicalized)     # req; absence of any resolution
                                 #   entry = surface-only (former state removed; principle 6)
  target_capability: code(RESEARCH_STRUCTURE)                       # req
  target_object_id: string       # req; externally_canonicalized IDs are issued by the external owner —
                                 #   A.1-E records them, never derives them (D3; I-35)
  updated_at: timestamp          # req

gap_processing_envelope:
  envelope_id: string            # req; unique
  gap_id: string                 # req; exactly one envelope per record (I-33)
  run_id: string                 # req
  lifecycle_state_code: code(STATE_MACHINE_SPEC)                    # req; reserved code: extraction_verified
                                 #   (semantic-freeze trigger, I-38)
  object_resolutions: [object_resolution_link]                      # req; 0..n; MAY change after freeze
  verifier_results:              # req; 0..n
    - verifier_id: string        # req
      verdict_code: code(VERIFICATION_SPEC)                         # req
      detail_code: code(VERIFICATION_SPEC)                          # opt
      at: timestamp              # req
  verification_basis_codes: [code(VERIFICATION_SPEC)]               # req; 0..n
  review_flags:                  # req; 0..n
    - review_flag_code: code(VERIFICATION_SPEC / KB-6)              # req; reserved: object_scope_boundary,
                                 #   citation_unresolved, contrast_not_reported
      detail: string             # opt
      status: enum(open, resolved)                                  # req
  human_review_status_code: code(VERIFICATION_SPEC)                 # opt; ABSENT when not applicable
  detector_ids: [string]         # req; >=1
  promoted_from_candidate_ids: [string]   # req; >=1; lineage
  updated_at: timestamp          # req

# ─────────────────────────────────────────────
# Run-level provenance
# ─────────────────────────────────────────────

gap_run:
  run_id: string                 # req; unique
  document_id: string            # req
  document_version: string       # req
  schema_version: string         # req
  extractor_model: string        # req
  extraction_prompt_version: string      # req
  detector_versions:             # req; >=1
    - {detector_id: string, version: string}
  kb_versions:                   # req; >=1
    - {kb_id: string, version: string}
  started_at: timestamp          # req

# ─────────────────────────────────────────────
# Candidate artefact (includes the UNCERTAIN queue)
# ─────────────────────────────────────────────

candidate_instance_routing:
  extraction_instance_id: string
                                 # req; unique within the containing
                                 # candidate.routing_set (I-47)
  routing_status: enum(UNROUTED, ROUTING_REVIEW_OPEN, CREATED, ATTACHED)
                                 # req; CREATED/ATTACHED terminal;
                                 # UNROUTED/ROUTING_REVIEW_OPEN nonterminal
  target_gap_id: string          # req iff routing_status ∈ {CREATED, ATTACHED};
                                 # ABSENT iff routing_status ∈ {UNROUTED, ROUTING_REVIEW_OPEN} (I-48)

gap_candidate:
  candidate_id: string           # req; unique within run
  run_id: string                 # req
  source_spans: [source_span]    # req; >=1 (D9)
  evidence_span_refs: [string]   # req; >=1
  context_window_span_ref: string        # opt
  detector_ids: [string]         # req; >=1
  boundary_state: enum(GAP, MOTIVATION, OWN_LIMITATION, FUTURE_RESEARCH,
                       CONTRIBUTION, OTHER, UNCERTAIN)
                                 # opt; ABSENT until boundary classification runs (correction 2 principle:
                                 #   outcomes populate when their operations occur; no pending value)
  routing_outcome: enum(rejected_non_gap, uncertain_queued)
                                 # opt; candidate-level outcome only for non-GAP / UNCERTAIN
                                 #   routing; ABSENT for GAP candidates (I-34) [v1.4]
  routing_set:                   # opt; GAP candidates only; ABSENT until the Step-11
                                 #   extraction-instance set has been frozen by EXTRACTION_COMPLETE [v1.4]
    extraction_bundle_id: string # req within block
    structured_output_digest: string
                                 # req within block; binds the exact frozen Step-11 extraction bundle (I-46)
    instances: [candidate_instance_routing]
                                 # req within block; >=1; exactly one entry per frozen extraction_instance_id
  lifecycle_state_code: code(STATE_MACHINE_SPEC)                    # opt
  uncertainty:                   # req iff boundary_state = UNCERTAIN; absent otherwise
    competing_boundary_states: [enum(GAP, MOTIVATION, OWN_LIMITATION, FUTURE_RESEARCH,
                                     CONTRIBUTION, OTHER)]          # req; >=2
    review_trigger_code: code(KB-6)                                 # req

# ─────────────────────────────────────────────
# Diagnostic notices (never gap objects)
# ─────────────────────────────────────────────

diagnostic_notice:
  notice_id: string              # req; unique within run
  notice_code: enum(presupposed_gap_without_antecedent)             # req; extension only by contract amendment
  source_span: source_span       # req; single embedded definition (D9 note)
  related_gap_id: string         # opt; ABSENT = no related record exists
  review_status: enum(open, reviewed)                               # req
  run_id: string                 # req
```

---

## 4. Field dictionary

Version tags identify the schema revision in which a row was introduced
or materially changed. Untagged rows carry forward unchanged from the
preceding schema versions.

| Field path | Type | Required | Meaning | Source/derivation | Validation invariant |
|---|---|---:|---|---|---|
| source_span.* | — | req | Span atoms (unchanged) | verbatim / segmentation | I-0; I-3a; I-33a |
| trace.* | — | req | Class + grounding (unchanged) | contract §8 | refs resolve |
| object_mention.surface_form | string | req | Manuscript wording of the referent | **verbatim** | consistent with span text |
| object_mention.mention_span_refs | [string] | req ≥1 | Where the referent is mentioned | verbatim refs | resolve (I-3a) |
| object_mention.generated_descriptor | object | opt | System label for a grounded referent | **generated_flagged** | I-14; never sole ground (I-9b, I-41) |
| ~~object_mention.object_link~~ | — | — | **Removed [v1.2]** — resolution is envelope enrichment | — | I-35/I-37: presence in record is invalid |
| affected_object.object_kind / artifact_kind | enum | req/cond | Kind of referent / artifact subtype (`method` added [v1.3]) | **normalized_with_trace [v1.2]** | closed enums; I-10 |
| affected_object.type_trace_refs `[v1.2]` | [string] | req ≥1 | Source evidence for the kind classification(s); shared trace | normalized_with_trace | resolve to source_spans (I-40, I-41) |
| affected_object.mention | object_mention | req | What the deficient knowledge is about | verbatim | I-9; I-9b |
| affected_object.about `[v1.2]` | object | opt | Artifact's subject matter **as asserted in the manuscript** | **verbatim** (surface + refs, both req) | only if knowledge_artifact (I-28); grounded (I-42); never registry-inferred |
| deficiency.relation / knowledge_kind | enum | req | Asserted predicate class / kind | **normalized_with_trace [v1.2]** | frozen enums (I-6, I-7) |
| deficiency.source_trace_refs `[v1.2]` | [string] | req ≥1 | Source evidence for relation and kind; shared trace | normalized_with_trace | resolve to source_spans (I-39, I-41) |
| gap_record.gap_id | string | req | Canonical ID; immutable; **created at record instantiation — event ordering owned by Steps 4/9 [v1.2]** | system | unique; never reassigned |
| gap_record.affected_object | affected_object | req | Object payload — **no resolution state [v1.2]** | — | I-35 |
| envelope.object_resolutions `[v1.2]` | [object_resolution_link] | req 0..n | External object identity; mutable after freeze | **linked_provisional** (envelope-side) | I-35; subject resolves to a grounded referent of the record |
| object_resolution_link.subject `[v1.2]` | object | req | Which grounded referent is enriched | system | target_kind enum; contrast_entry_id iff uncited_referent |
| object_resolution_link.link_status `[v1.2]` | enum | req | provisional_link \| externally_canonicalized | external outcome | absence of entry = surface-only |
| object_resolution_link.target_capability / target_object_id `[v1.2]` | code / string | req | External owner + ID | external | externally_canonicalized IDs issued externally (I-35) |
| gap_candidate.boundary_state `[v1.2]` | enum | **opt** | Contract §6 class; absent until classification runs | boundary stage | I-34 |
| gap_candidate.routing_outcome `[v1.4]` | enum | **opt** | Candidate-level non-GAP / UNCERTAIN outcome only: `rejected_non_gap` \| `uncertain_queued`; ABSENT for GAP candidates | routing fact | revised I-34 |
| gap_candidate.routing_set `[v1.4]` | object | **opt** | GAP candidates only; canonical representation of the frozen Step-11 routing obligations | routing facts | I-34; I-46 |
| gap_candidate.routing_set.extraction_bundle_id `[v1.4]` | string | req within routing_set | Identifies the Step-11 extraction bundle | system | I-46 |
| gap_candidate.routing_set.structured_output_digest `[v1.4]` | string | req within routing_set | Binds the immutable extraction-instance set | system | I-46 |
| gap_candidate.routing_set.instances `[v1.4]` | [candidate_instance_routing] | req ≥1 within routing_set | Exactly one entry per frozen extraction_instance_id | routing facts | I-46/I-47 |
| candidate_instance_routing.extraction_instance_id `[v1.4]` | string | req | Frozen Step-11 instance identity; unique within routing_set | system | I-47 |
| candidate_instance_routing.routing_status `[v1.4]` | enum | req | UNROUTED \| ROUTING_REVIEW_OPEN \| CREATED \| ATTACHED | routing fact | I-48/I-49 |
| candidate_instance_routing.target_gap_id `[v1.4]` | string | cond | Required iff CREATED or ATTACHED; absent otherwise | routing fact | I-48/I-49 |
| gap_candidate.uncertainty | object | cond | Unresolved boundary decision | boundary stage | present iff boundary_state = UNCERTAIN (I-34) |
| (all remaining rows) | — | — | As in Schema v1.1 §4 | — | unchanged |

---

### 4a — `artifact_kind = method` [v1.3]

**Definition.** `method` = an explicitly mentioned research-generating methodological artifact that is not better classified as `measure`. It applies only when the methodological artifact itself bears the deficiency predicate.

Includes (when they themselves bear the deficiency, used as epistemic/research-methodological artifacts): method · methodological approach · research design · study design · analytical procedure · analytic approach · estimation approach · survey approach · experimental design · cross-sectional design · longitudinal design · identification strategy · analysis procedure.

Excludes: physical procedures; organizational procedures; business processes; intervention procedures unrelated to knowledge generation; generic "approach" without recoverable methodological meaning; measurement resources already represented by `measure`.

**Hard distinction (frozen):** measurement resource → `artifact_kind = measure`; non-measure methodological resource → `artifact_kind = method`. `method` never replaces `measure`. All other invariants are untouched: `artifact_kind` remains required iff `object_kind = knowledge_artifact` (I-10); no null `artifact_kind`; `object_kind` remains exactly {construct, phenomenon, relationship, knowledge_artifact}.

## 5. Enum / code registry

### 5A — Contract-frozen enums (closed in this schema)

Changes from v1.1 only; all other rows carry forward:

| Enum | Value(s) | Exact meaning | Prohibited interpretation |
|---|---|---|---|
| object-resolution status `[v1.2]` | provisional_link / externally_canonicalized | Envelope-side external-identity states; **absence of a resolution entry = surface-only** | Canonical identity performed by A.1-E; any state inside the record payload |
| resolution subject kind `[v1.2]` | affected_object / about / uncited_referent | Which grounded referent an envelope resolution enriches | A license to add referents the record does not contain |
| candidate-level routing outcome `[v1.4]` | rejected_non_gap / uncertain_queued | Candidate-level structural outcome for non-GAP / UNCERTAIN cases; field ABSENT for GAP candidates. `rejected_non_gap` is terminal. `uncertain_queued` is provisional/nonterminal; subsequent lifecycle handling is owned by the State Machine (Step 4). | A transition system; treating `uncertain_queued` as terminal; any GAP-side use |
| instance routing status `[v1.4]` | UNROUTED / ROUTING_REVIEW_OPEN / CREATED / ATTACHED | UNROUTED = no Step-12 terminal routing decision yet · ROUTING_REVIEW_OPEN = unresolved via the existing routing-review pathway, NONTERMINAL · CREATED = this extraction instance created exactly one canonical gap_record, TERMINAL · ATTACHED = this instance attached as a restatement to exactly one canonical gap_record, TERMINAL | State Machine transitions; routing review as terminal; a status implying a new candidate; PROMOTED as a replacement for CREATED |
| artifact_kind `[v1.3]` | proposition / theory / model / framework / assumption / measure / method | Artifact subtype; required iff object_kind = knowledge_artifact (I-10) | A null value; a free-text slot; a replacement for `measure` |
| (relation, knowledge_kind, explicitness, span roles, linguistic dependency, object_kind, citation resolution, traceability, claim-link type, boundary state, contrast status, flag status, review status, notice code, spawned target type) | — | As in v1.1 §5A | unchanged |

Note (Step-6 ownership): the relation and knowledge_kind **values** are contract-frozen; the lexicon mapping manuscript predicates to these values is owned by the Deficiency Predicate Registry (Step 6) and is not part of this schema.

### 5B — Owned code slots

As in v1.1 §5B, unchanged: lifecycle_state_code (Step 4; reserved `extraction_verified`); verdict/detail/basis codes and review_flag_code (Step 13 / KB-6; reserved `object_scope_boundary`, `citation_unresolved`, `contrast_not_reported`); human_review_status_code; unresolved_review_status_code; unmerged/relation basis codes (Step 9); review_trigger_code (KB-6); section_role (segmentation); normalization_method (normalization spec); target_capability (Research Structure).

---

## 6. Cross-field invariants

Carried invariants I-0 through I-38 hold except where explicitly revised
below. I-39 through I-43 were introduced in v1.2; I-44 and I-45 were added
in the v1.3 final issuance; I-46 through I-51 are introduced by v1.4.
Existing invariant IDs are preserved.

- **I-34 (v1.4) — Candidate routing consistency.** `boundary_state` is absent until boundary classification runs. For `boundary_state = GAP`: candidate-level `routing_outcome` MUST be absent; `routing_set` MAY be absent before Step-11 EXTRACTION_COMPLETE; once the frozen Step-11 extraction-instance set is represented, `routing_set` contains all GAP routing obligations; singular promoted/attached candidate-level target fields do not exist. For a present non-GAP, non-UNCERTAIN `boundary_state`: `routing_outcome` MAY equal `rejected_non_gap`; `routing_set` MUST be absent. For `boundary_state = UNCERTAIN`: the uncertainty block MUST be present; `routing_outcome` MAY equal `uncertain_queued`; `routing_set` MUST be absent. `routing_outcome` present ⇒ `boundary_state` present. No pending candidate-level routing outcome exists: pending GAP routing is represented structurally by the statuses inside `routing_set`, never by a candidate-level pending enum.
- **I-35 (revised)** External-resolution state exists **only** in `envelope.object_resolutions`; the canonical record contains no link, status, or external ID for any referent. Every resolution entry has `target_capability` and `target_object_id`; its `subject` must resolve to a grounded referent actually present in the record (`affected_object.mention`, a grounded `about`, or a named `uncited_referent`); `externally_canonicalized` IDs are issued by the external owner, never derived by A.1-E. Absence of an entry = surface-only.
- **I-37 (revised; v1.4 additions)** Closed schema: artefacts contain only fields defined here; removed fields — `participants`, `scope`, `confidence`, `spawned_gap_id`, `disposition` (legacy name), `promoted_gap_id` [v1.4], `attached_to_gap_id` [v1.4], and any `object_link` inside a gap_record — are violations. Candidate-level routing_outcome values `promoted` and `attached_as_restatement` are no longer valid under GS-1.4 [v1.4].
- **I-38 (revised)** Semantic freeze per the §2 table: after the reserved verified condition, the record's `source_spans`, `explicitness`, `context_support`, `deficiency` (including traces), `affected_object` source representation (kinds, traces, mention, `about`), proposition, contrast, persistence reasons, and claim links change only through the later versioning/correction procedure; envelope content — including `object_resolutions` — may change at any time; verifier execution never modifies semantic content at any state.
- **I-39 (new)** Every `deficiency` carries `source_trace_refs` (≥1) resolving to the record's `source_spans` (assertion spans or, for `context_supported` records, permitted support spans).
- **I-40 (new)** Every `affected_object` carries `type_trace_refs` (≥1) resolving likewise; when `artifact_kind` is present, the trace evidence covers the artifact naming.
- **I-41 (new)** Generated descriptors cannot ground primitives or objects: all trace and evidence references resolve only to `source_spans` entries; generated descriptor text possesses no `span_id` and is therefore structurally incapable of serving as evidence for `relation`, `knowledge_kind`, `object_kind`, `artifact_kind`, or the existence of the affected object (with I-9b).
- **I-42 (new)** `about`, when present, is source-grounded: `surface_form` and `mention_span_refs` (≥1) are required; an `about` relation is never created from external registry knowledge — manuscript assertion (or permitted linguistic completion) only. External enrichment of a grounded `about` occurs solely via envelope `object_resolutions`. *Clarification (v1.3 final issuance):* `about` is licensed only when manuscript wording explicitly asserts the artifact's subject/content relationship — licensed: "the theory of organizational resilience" → about "organizational resilience"; "the model of supplier adaptation" → about "supplier adaptation"; "the proposition that X causes Y" → about "X causes Y"; "the assumption that preferences are stable" → about "preferences are stable". NOT licensed merely from a compound/name: "cascading-goals model", "ABC model", "resilience framework" carry no automatic `about` unless the manuscript construction explicitly establishes the subject matter under the Step-8 Object Rules. The schema stores grounded `about`; Step 8 owns the linguistic qualification decision.
- **I-43 (new)** Payload purity: no structure inside `gap_record` stores external-resolution state, graph links, or any field whose value an external capability may later change.
- **I-44 (v1.3 final issuance) — object-denoting vs carrier/reference anaphors.** An anaphoric expression may stand as the canonical `affected_object.mention` ONLY when it itself denotes the affected object ("This theory", "This assumption", "This relationship"); its resolution then lives in `context_support` (`dependency_expression` = the exact local anaphor; `support_span_refs` = the antecedent evidence), and the antecedent supports resolution without rewriting the local surface form. An anaphoric expression that instead refers to a deficiency state, knowledge carrier, or gap reference ("this gap", "such evidence", "this issue" pointing to an antecedent) must NOT become the canonical affected object: the canonical `affected_object` resolves to the source-grounded antecedent referent (e.g., "Little is known about employee turnover. This gap persists." → mention.surface_form = "employee turnover"), while the local anaphor remains represented in `context_support.dependency_expression` and proposition traceability. If the antecedent cannot be uniquely resolved, no canonical gap_record may be finalized with a fabricated affected_object — the case routes through the existing candidate/review lifecycle semantics; no new field exists for it.
- **I-45 (v1.3 final issuance) — mention-span coherence.** `affected_object.mention.mention_span_refs` reference only spans whose text contains/corresponds to the declared `surface_form`; one canonical `surface_form` never cites mutually different surface forms as if they were identical mentions. A local anaphor whose text does not match the surface form is never inserted into `mention_span_refs`; it is carried by `context_support.dependency_expression` and its own span in the proposition/context trace structure.

- **I-46 (new v1.4) — Frozen routing-set identity.** For a GAP candidate with `routing_set` present: `routing_set.extraction_bundle_id` and `routing_set.structured_output_digest` identify the exact Step-11 bundle accepted by EXTRACTION_COMPLETE. The set of `extraction_instance_id` values in `routing_set` is the complete frozen instance set I(C). Routing must not add, delete, replace, merge, or duplicate entries.
- **I-47 (new v1.4) — Routing-instance uniqueness.** Within one `routing_set` every `extraction_instance_id` occurs exactly once.
- **I-48 (new v1.4) — Routing-status target consistency.** `routing_status ∈ {CREATED, ATTACHED}` ⇔ `target_gap_id` present; `routing_status ∈ {UNROUTED, ROUTING_REVIEW_OPEN}` ⇔ `target_gap_id` absent.
- **I-49 (new v1.4) — One terminal routing representation per instance.** One `extraction_instance_id` may not be represented as both CREATED and ATTACHED and may not have multiple terminal `target_gap_id`s.
- **I-50 (new v1.4) — Candidate routing-completion representability.** A GAP candidate is fully routed exactly when every `routing_set` entry has `routing_status ∈ {CREATED, ATTACHED}`. The schema stores the facts required for `A1E-SM-1.4` to evaluate CANDIDATE_ROUTING_COMPLETE(C); the schema does NOT itself perform lifecycle transitions.
- **I-51 (new v1.4) — Candidate cardinality unchanged.** A `routing_set` containing N extraction instances remains attached to ONE `gap_candidate`. No child candidates, synthetic candidates, or candidate fission are introduced by the schema.

---

## 7. Invalid-state examples

Items 1–31 carry forward from the prior schema history with their existing
numbers preserved. Item 32 is revised for GS-1.4 compatibility; items 33–37
carry forward from the v1.3 final issuance; items 38–47 are added by v1.4.

26. **Resolution state inside the record** — `affected_object.mention.object_link: {link_status: provisional_link, …}` or any link/status/external-ID field within `gap_record` → **I-35/I-37/I-43**.
27. **Removed/legacy field present** — `participants`, `spawned_gap_id`, or `disposition` in any artefact → **I-37**.
28. **Relation without evidence** — `deficiency` lacking `source_trace_refs`, or refs that do not resolve → **I-39**.
29. **Kind classification without evidence** — `affected_object` lacking `type_trace_refs`; or `artifact_kind: model` with traces evidencing no artifact naming → **I-40**.
30. **Descriptor-grounded primitive** — `type_trace_refs` empty while only a `generated_descriptor` "supports" the object kind (or any attempt to reference descriptor text as evidence) → **I-41** (structurally: descriptor has no span_id).
31. **Ungrounded / registry-inferred `about`** — `about` present with no `mention_span_refs` (e.g., populated because a registry knows the model concerns adoption) → **I-42**.
32. **Candidate-level routing before classification** — candidate with
`routing_outcome: rejected_non_gap` or `routing_outcome: uncertain_queued`
while `boundary_state` is absent → **I-34**.
33. **Resolution subject without referent** — envelope resolution `subject: {target_kind: about}` while the record has no `about` → **I-35**.
34. **Mixed mention spans** — `mention: {surface_form: "coordination mechanisms", mention_span_refs: [span("coordination mechanisms"), span("These mechanisms")]}` where the second span's text does not contain the declared surface form → **I-45**.
35. **Gap-reference anaphor as canonical object** — `affected_object.mention.surface_form = "This gap"` where "This gap" merely refers to an antecedent deficiency about X → **I-44** (the canonical object is X; "This gap" belongs in `context_support`).
36. **Name-derived `about`** — `about: {surface_form: "cascading-goals"}` populated solely because the artifact is named "The cascading-goals model" → **I-42** (ungrounded about; naming ≠ subject-matter assertion).
37. **Incomplete "full record"** — a worked gap_record presented as complete while missing `contrast`, `persistence_reasons`, or `claim_links` → violates the required-field set of the normative `gap_record` block.
38. **GAP candidate with candidate-level outcome** — `boundary_state: GAP` with `routing_outcome: rejected_non_gap` or `uncertain_queued` → **I-34**.
39. **routing_set on the wrong side** — a non-GAP or UNCERTAIN candidate carrying `routing_set` → **I-34**.
40. **Duplicate instance** — duplicate `extraction_instance_id` inside one `routing_set` → **I-47**.
41. **CREATED without target** — `routing_status: CREATED` without `target_gap_id` → **I-48**.
42. **ATTACHED without target** — `routing_status: ATTACHED` without `target_gap_id` → **I-48**.
43. **UNROUTED with target** — `routing_status: UNROUTED` with `target_gap_id` → **I-48**.
44. **Review with target** — `routing_status: ROUTING_REVIEW_OPEN` with `target_gap_id` → **I-48**.
45. **Double representation** — one `extraction_instance_id` represented twice with different routing statuses or targets → **I-47/I-49**.
46. **Set/digest mismatch** — `routing_set` instance set inconsistent with its frozen bundle/digest → **I-46**.
47. **Legacy routing artifacts** — `promoted_gap_id`, `attached_to_gap_id`, `routing_outcome: promoted`, or `routing_outcome: attached_as_restatement` in a GS-1.4 candidate → **I-37**.

---

## 8. Valid worked examples (synthetic)

Conventions as in v1.1 (`schema_version: A1E-GS-1.4`; per-span `document_id: DOC-1, document_version: v1` elided on the page for readability only; owned-code values illustrative). Changes from v1.1: `object_link` removed everywhere; `deficiency.source_trace_refs` and `affected_object.type_trace_refs` added everywhere; V4 shows envelope-side object resolution.

### V1 — Simple explicit gap (with envelope, verified)

```yaml
gap_record:
  gap_id: G-001
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p3,
       char_start: 1200, char_end: 1241, text: "Little is known about how X affects Y."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p3,
       char_start: 1222, char_end: 1240, text: "how X affects Y"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: LIMITED, knowledge_kind: evidence, source_trace_refs: [S1]}
  affected_object:
    object_kind: relationship
    type_trace_refs: [S2]
    mention: {surface_form: "how X affects Y", mention_span_refs: [S2]}
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "LIMITED evidence about the relationship(X, Y).",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons: []
  claim_links: []

gap_processing_envelope:
  envelope_id: E-001
  gap_id: G-001
  run_id: R-001
  lifecycle_state_code: extraction_verified
  object_resolutions: []            # none = affected object remains surface-only (D3)
  verifier_results:
    - {verifier_id: vfy-span-01, verdict_code: pass, at: "2026-08-22T10:00:00Z"}
  verification_basis_codes: [validators_passed]
  review_flags:
    - {review_flag_code: contrast_not_reported, status: resolved}
  detector_ids: [lex-01, llm-sweep-01]
  promoted_from_candidate_ids: [C-014]
  updated_at: "2026-08-22T10:05:00Z"
```

### V2 — `knowledge_kind: unspecified`

```yaml
gap_record:
  gap_id: G-002
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p2,
       char_start: 810, char_end: 858, text: "Collective adaptation remains poorly understood."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p2,
       char_start: 810, char_end: 831, text: "Collective adaptation"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: LIMITED, knowledge_kind: unspecified, source_trace_refs: [S1]}
  affected_object:
    object_kind: phenomenon
    type_trace_refs: [S2]
    mention: {surface_form: "Collective adaptation", mention_span_refs: [S2]}
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "LIMITED knowledge (kind unspecified) about collective adaptation.",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons: []
  claim_links: []
```

### V3 — Context-supported through anaphora

```yaml
gap_record:
  gap_id: G-003
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: context_supported
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p4,
       char_start: 2110, char_end: 2170, text: "These mechanisms remain unexplored in distributed settings."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p4,
       char_start: 2030, char_end: 2109, text: "Prior work has documented several coordination mechanisms in co-located teams."}
    - {span_id: S3, section_id: sec-intro, section_role: introduction, paragraph_id: p4,
       char_start: 2061, char_end: 2084, text: "coordination mechanisms"}
    - {span_id: S4, section_id: sec-intro, section_role: introduction, paragraph_id: p4,
       char_start: 2110, char_end: 2126, text: "These mechanisms"}   # local anaphor site — referenced via context_support, never via mention_span_refs (I-45)
  gap_evidence: [{role: primary, span_ref: S1}]
  context_support:
    dependency_type: anaphora
    dependency_expression: "These mechanisms"
    support_span_refs: [S2]
  deficiency: {relation: ABSENT, knowledge_kind: evidence, source_trace_refs: [S1]}
  affected_object:
    object_kind: phenomenon
    type_trace_refs: [S3]              # classification evidenced via completion co-text (I-40 with I-2 scope)
    mention: {surface_form: "coordination mechanisms", mention_span_refs: [S3]}   # S4 text ≠ surface_form → never a mention span (I-45); the anaphor lives in context_support
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "ABSENT evidence about coordination mechanisms, as asserted 'in distributed settings'.",
                 source_trace_refs: [S1, S2], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons: []
  claim_links: []
```

*V3 illustrates the completion rule (I-44/I-45): the local clause "These mechanisms remain unexplored…" is anaphoric; the antecedent "coordination mechanisms" supplies the actual source-grounded referent, so the canonical mention is "coordination mechanisms" with mention_span_refs = [S3] only, while "These mechanisms" is carried by `context_support.dependency_expression` with `support_span_refs = [S2]`. Nothing is rewritten or synthesized.*

### V4 — Context wording preserved; envelope-side object resolution

```yaml
gap_record:
  gap_id: G-004
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p5,
       char_start: 3001, char_end: 3071, text: "Evidence about employee engagement is limited among frontline workers."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p5,
       char_start: 3016, char_end: 3035, text: "employee engagement"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: LIMITED, knowledge_kind: evidence, source_trace_refs: [S1]}
  affected_object:
    object_kind: construct
    type_trace_refs: [S2]
    mention: {surface_form: "employee engagement", mention_span_refs: [S2]}
    # NO link, status, or external ID here — payload purity (I-43)
  proposition:
    assertion_span_refs: [S1]          # "among frontline workers" fully preserved; no scope field anywhere
    normalized: {text: "LIMITED evidence about employee engagement, as asserted 'among frontline workers'.",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons: []
  claim_links: []

gap_processing_envelope:
  envelope_id: E-004
  gap_id: G-004
  run_id: R-001
  lifecycle_state_code: extraction_verified
  object_resolutions:
    - resolution_id: OR-1
      subject: {target_kind: affected_object}
      link_status: provisional_link
      target_capability: construct_registry
      target_object_id: PROV-ENG-01
      updated_at: "2026-08-22T10:20:00Z"
      # May later become externally_canonicalized with the registry's canonical ID —
      # WITHOUT any change to the frozen gap_record above (correction 1 property)
  verifier_results: []
  verification_basis_codes: [validators_passed]
  review_flags: []
  detector_ids: [lex-01]
  promoted_from_candidate_ids: [C-021]
  updated_at: "2026-08-22T10:20:00Z"
```

### V5 — Knowledge artifact (model, untested); `about` absent

```yaml
gap_record:
  gap_id: G-005
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-theory, section_role: theory, paragraph_id: p2,
       char_start: 5210, char_end: 5266, text: "The cascading-goals model remains empirically untested."}
    - {span_id: S2, section_id: sec-theory, section_role: theory, paragraph_id: p2,
       char_start: 5210, char_end: 5235, text: "The cascading-goals model"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: UNTESTED, knowledge_kind: evidence, source_trace_refs: [S1]}
  affected_object:
    object_kind: knowledge_artifact
    artifact_kind: model
    type_trace_refs: [S2]              # "model" evidenced by the manuscript's own naming
    mention: {surface_form: "The cascading-goals model", mention_span_refs: [S2]}
    # about: ABSENT — a model NAME does not assert subject matter; naming alone never grounds `about` (I-42 clarification)
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "UNTESTED (empirical) status asserted for the cascading-goals model.",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons: []
  claim_links: []
```

### V6 — Assumption challenge

```yaml
gap_record:
  gap_id: G-006
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p6,
       char_start: 4100, char_end: 4177, text: "Previous theories assume stable boundaries, but this assumption is mistaken."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p6,
       char_start: 4126, char_end: 4143, text: "stable boundaries"}
    - {span_id: S3, section_id: sec-intro, section_role: introduction, paragraph_id: p6,
       char_start: 4100, char_end: 4143, text: "Previous theories assume stable boundaries"}
    - {span_id: S4, section_id: sec-intro, section_role: introduction, paragraph_id: p6,
       char_start: 4100, char_end: 4117, text: "Previous theories"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: CHALLENGED, knowledge_kind: theory, source_trace_refs: [S1]}
  affected_object:
    object_kind: knowledge_artifact
    artifact_kind: assumption
    type_trace_refs: [S1]              # "assumption … mistaken" evidences both kind and artifact type
    mention: {surface_form: "stable boundaries", mention_span_refs: [S2]}
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "CHALLENGED status asserted for the prior-theory assumption of stable boundaries.",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast:
    status: reported
    entries:
      - entry_id: CE-1
        attributed_span_refs: [S3]
        citation_links: []
        uncited_referent: {surface_form: "Previous theories", mention_span_refs: [S4]}
  persistence_reasons: []
  claim_links: []
```

### V7 — Cited contrast

```yaml
gap_record:
  gap_id: G-007
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p7,
       char_start: 6000, char_end: 6041, text: "Little is known about supplier collusion."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p7,
       char_start: 6022, char_end: 6040, text: "supplier collusion"}
    - {span_id: S3, section_id: sec-intro, section_role: introduction, paragraph_id: p7,
       char_start: 6042, char_end: 6101, text: "Prior studies focus on dyadic relationships (Smith, 2022)."}
    - {span_id: S4, section_id: sec-intro, section_role: introduction, paragraph_id: p7,
       char_start: 6088, char_end: 6099, text: "Smith, 2022"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: LIMITED, knowledge_kind: evidence, source_trace_refs: [S1]}
  affected_object:
    object_kind: phenomenon
    type_trace_refs: [S2]
    mention: {surface_form: "supplier collusion", mention_span_refs: [S2]}
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "LIMITED evidence about supplier collusion.",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast:
    status: reported
    entries:
      - entry_id: CE-1
        attributed_span_refs: [S3]
        citation_links:
          - link_id: CL-1
            resolution_status: resolved
            registry_citation_id: CIT-00042
            citation_span_ref: S4
            verbatim_citation_text: "Smith, 2022"
  persistence_reasons: []
  claim_links: []
```

### V8 — Persistence reason without spawned gap

```yaml
gap_record:
  gap_id: G-008
  schema_version: A1E-GS-1.4
  document_id: DOC-1
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p8,
       char_start: 7000, char_end: 7047, text: "Evidence on supplier adaptation remains scarce"}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p8,
       char_start: 7012, char_end: 7031, text: "supplier adaptation"}
    - {span_id: S3, section_id: sec-intro, section_role: introduction, paragraph_id: p8,
       char_start: 7048, char_end: 7098, text: "because longitudinal data are difficult to obtain."}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: LIMITED, knowledge_kind: evidence, source_trace_refs: [S1]}
  affected_object:
    object_kind: phenomenon
    type_trace_refs: [S2]
    mention: {surface_form: "supplier adaptation", mention_span_refs: [S2]}
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "LIMITED evidence about supplier adaptation.",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons:
    - reason_id: PR-1
      reason_span_refs: [S3]
      citation_links: []
      # spawned_claim_ref ABSENT: causal reason, no independent deficiency (I-16)
  claim_links: []
```

### V9 — Persistence reason with a separately asserted deficiency (spawn)

As in v1.1 V9 with the v1.2 adjustments applied to both records: `object_link` blocks removed; `deficiency.source_trace_refs: [S1]` and `affected_object.type_trace_refs: [S2]` added to G-009 and G-010; `uncited_referent` on G-010 linkless (`{surface_form: "existing diffusion theories", mention_span_refs: [S3]}`); the spawn remains `spawned_claim_ref: {target_type: gap_record, target_id: G-010}` with the pre-promotion candidate note, and G-010 keeps `claim_link{reason_of, target_gap_id: G-009, source_persistence_reason_id: PR-1}`.

### V10 — Contextually different gaps, not merged

As in v1.1 V10 with the v1.2 adjustments applied to both records: no `object_link`; `deficiency.source_trace_refs: [S1]`; `affected_object.type_trace_refs: [S2]`; reciprocal `possibly_same_claim` links with `unmerged_basis_code: contextual_wording_difference` (illustrative) unchanged; "among frontline workers" / "among senior managers" preserved solely in spans and normalized text.

---

### V11 — Method artifacts vs measure `[v1.3]` (normative)

Full record for the first case; compact field mappings for the rest.

```yaml
gap_record:
  gap_id: G-011
  schema_version: A1E-GS-1.4
  document_id: DOC-2
  document_version: v1
  boundary_class: GAP
  explicitness: explicit
  source_spans:
    - {span_id: S1, section_id: sec-intro, section_role: introduction, paragraph_id: p4,
       char_start: 2100, char_end: 2146, text: "Existing methods cannot distinguish X from Y."}
    - {span_id: S2, section_id: sec-intro, section_role: introduction, paragraph_id: p4,
       char_start: 2100, char_end: 2116, text: "Existing methods"}
  gap_evidence: [{role: primary, span_ref: S1}]
  deficiency: {relation: CONSTRAINED, knowledge_kind: method, source_trace_refs: [S1]}
  affected_object:
    object_kind: knowledge_artifact
    artifact_kind: method
    type_trace_refs: [S2]
    mention: {surface_form: "Existing methods", mention_span_refs: [S2]}
  proposition:
    assertion_span_refs: [S1]
    normalized: {text: "CONSTRAINED method capability asserted for existing methods (cannot distinguish X from Y).",
                 source_trace_refs: [S1], normalization_method: norm-proc-0.1}
  contrast: {status: not_reported, entries: []}
  persistence_reasons: []
  claim_links: []
```

*V11 re-audited field-by-field against the normative `gap_record` block: gap_id · schema_version · document_id · document_version · boundary_class · explicitness (explicit → `context_support` correctly ABSENT, I-26) · source_spans · gap_evidence · deficiency · affected_object (object_kind, artifact_kind = method, type_trace_refs, mention) · proposition (assertion_span_refs + normalized in the V1–V10 format) · contrast · persistence_reasons · claim_links — complete.*

Compact mandated mappings (all validate under GS-1.4):

| Sentence | object_kind | artifact_kind | mention.surface_form |
|---|---|---|---|
| "Existing methods cannot distinguish X from Y." | knowledge_artifact | method | "Existing methods" |
| "Cross-sectional designs cannot identify temporal ordering." | knowledge_artifact | method | "Cross-sectional designs" |
| "Established survey approaches systematically misstate X." | knowledge_artifact | method | "Established survey approaches" |
| "Existing measures cannot capture X." | knowledge_artifact | measure | "Existing measures" |

The fourth row is normative proof that `method` ≠ `measure`: measurement resources keep `measure`; only non-measure methodological artifacts take `method`.

### V12 — Mixed multi-instance GAP routing [v1.4]

```yaml
gap_candidate:
  candidate_id: C-100
  run_id: R-001
  source_spans: [...]
  evidence_span_refs: [...]
  detector_ids: [...]
  boundary_state: GAP
  routing_set:
    extraction_bundle_id: B-100
    structured_output_digest: DIGEST-100
    instances:
      - extraction_instance_id: I1
        routing_status: CREATED
        target_gap_id: G-201
      - extraction_instance_id: I2
        routing_status: ATTACHED
        target_gap_id: G-055
      - extraction_instance_id: I3
        routing_status: CREATED
        target_gap_id: G-202
```

Candidate-level `routing_outcome` is ABSENT (I-34). One candidate; three frozen routing obligations; mixed terminal outcomes (I-46..I-49, I-51).

### V13 — Partially routed GAP candidate [v1.4]

```yaml
gap_candidate:
  candidate_id: C-101
  run_id: R-001
  source_spans: [...]
  evidence_span_refs: [...]
  detector_ids: [...]
  boundary_state: GAP
  routing_set:
    extraction_bundle_id: B-101
    structured_output_digest: DIGEST-101
    instances:
      - extraction_instance_id: I1
        routing_status: CREATED
        target_gap_id: G-203
      - extraction_instance_id: I2
        routing_status: ROUTING_REVIEW_OPEN
      - extraction_instance_id: I3
        routing_status: UNROUTED
```

This example proves the schema represents the facts `A1E-SM-1.4` needs to keep the parent candidate unresolved (I-48/I-50); the schema itself assigns no lifecycle_state transitions.

## 9. Legacy compatibility mapping

### 9a — Spec v0.3 → schema (unchanged from v1.1 except one row)

All rows as in v1.1 §9, with:

| Legacy field | Disposition | Target / rationale |
|---|---|---|
| `affected_object` | SPLIT | `affected_object.{object_kind, artifact_kind, type_trace_refs, mention, about}`; scope content → preserved proposition; scope structure → Scope/Context; relationship decomposition → Object Rules (Step 8); **registry linkage → envelope `object_resolutions` [v1.2]** |

### 9b — Schema v1.1 → v1.2 migration notes

| v1.1 element | v1.2 disposition |
|---|---|
| `object_mention.object_link` (record-side) | REMOVED from payload; `provisional_link`/`externally_canonicalized` states migrate to `envelope.object_resolutions[]`; `surface_only` migrates to *absence of an entry* |
| `about.object_link` | REMOVED; `about` now requires `surface_form` + `mention_span_refs`; enrichment via `object_resolutions{subject.target_kind: about}` |
| `gap_candidate.disposition` (req) | RENAMED `routing_outcome`, now OPTIONAL (absent until routing); `boundary_state` likewise optional until classification (same principle) |
| `gap_id` "assigned at promotion after merge resolution" | RE-WORDED: created at record instantiation; event ordering owned by Steps 4/9 |
| `deficiency` (untraced) | `source_trace_refs` added (backfill required for existing records) |
| `affected_object` kinds (untraced) | `type_trace_refs` added (backfill required) |

### 9c — Schema v1.3 → v1.4 migration notes

| v1.3 element | v1.4 disposition |
|---|---|
| routing_outcome = promoted | REMOVED for GAP candidates; migrate to routing_set.instances[].routing_status = CREATED |
| promoted_gap_id | REMOVED; migrate to corresponding instance.target_gap_id |
| routing_outcome = attached_as_restatement | REMOVED for GAP candidates; migrate to routing_set.instances[].routing_status = ATTACHED |
| attached_to_gap_id | REMOVED; migrate to corresponding instance.target_gap_id |
| routing_outcome = rejected_non_gap | retained candidate-level |
| routing_outcome = uncertain_queued | retained candidate-level |
| single GAP routing outcome | replaced by routing_set with one entry for N=1 or N entries for compound candidates |

Migration from singular v1.3 GAP routing to v1.4 requires the corresponding `extraction_instance_id`. If a legacy record lacks enough provenance to map the old singular outcome to an extraction instance deterministically, migration must not fabricate the mapping; route through the applicable correction/migration procedure. That procedure is not invented in this schema.

---

## 10. Open issues (schema-level only)

- **OI-S1 — Owned vocabularies pending** (Steps 4, 13, 9, KB-6). Unchanged.
- **OI-S2 — `target_capability` vocabulary** (Research Structure). Unchanged; now consumed only by envelope resolutions.
- **OI-S3 — `document_version` semantics** (segmentation). Unchanged.
- **OI-S4 — `related_claim` utility.** Unchanged.
- **OI-S5 — `normalization_method` values.** Unchanged.
- **OI-S6 (revised) — `about` final coordination.** Grounding is now settled (I-42); remaining coordination with Step-8 Object Rules concerns only whether/how grounded `about` relations decompose further and how the Research Object Graph consumes them.
- **OI-S7 — Post-freeze versioning/correction procedure.** Required eventually; deliberately not designed here.

OD-1/OD-2/OD-3 referenced where they touch the schema (I-9, `object_scope_boundary`); not re-decided.

---

## 11. Schema Freeze Check

### Carried forward (v1.0 + v1.1 checks, re-audited under v1.2)

All thirty-one prior checks re-audited: **PASS**, with evidence updated where affected — notably: *Canonical gap separated from workflow metadata* now also covers external identity (I-35/I-43; V4); *All semantic fields source-traceable* now includes the primitives (I-39/I-40/I-41); *Knowledge artifacts representable* now with grounded `about` (I-42; V5); *Conditional fields use coherent absence/null semantics* extended to `boundary_state`/`routing_outcome` and resolution-entry absence (I-34; D3). No prior check regresses: span pooling, staged freeze, owned-code slots, spawn references, grounding rule, grounded objects, deferred decomposition, scope purity, A.1-C/A.1-A exclusion, and no-confidence all hold unchanged (I-0–I-38; §3).

### Final v1.2 checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| External object resolution can change without mutating frozen gap semantics | PASS | Resolution lives only in `envelope.object_resolutions` (I-35/I-43); §2 freeze table lists it as may-change; V4 demonstrates the property explicitly |
| A newly detected candidate can exist without a routing outcome | PASS | `routing_outcome` optional; `boundary_state` optional; no `pending` value invented (I-34; §3 candidate); invalid ex. 32 guards misuse |
| Gap-ID creation timing is not prematurely fixed | PASS | `gap_id` comment + D10: created at record instantiation; ordering owned by Steps 4/9; no invariant references promotion timing |
| Relation is source-traceable | PASS | `deficiency.source_trace_refs` req ≥1 (I-39); every valid example carries it; invalid ex. 28 |
| Knowledge kind is source-traceable | PASS | Shared `deficiency.source_trace_refs` covers the pair (I-39; D7) |
| Object kind/artifact kind are source-traceable | PASS | `affected_object.type_trace_refs` req ≥1 (I-40); invalid ex. 29; V5/V6 show artifact-kind evidence |
| Generated descriptors cannot ground primitives by themselves | PASS | I-41 — refs resolve only to `source_spans`; descriptor text has no `span_id`; invalid ex. 30 |
| `about` cannot introduce externally inferred content | PASS | I-42 — surface + mention refs required; registry-known relations excluded; invalid ex. 31; V5 grounded |
| Semantic freeze boundary is internally consistent | PASS | §2 may/must-not table; I-38 enumerates the frozen set; mutable set = envelope (incl. resolutions) + graph + operational metadata; no frozen field is externally writable (I-43) |
| Step 2 does not preempt State Machine/Merge/Verification specs | PASS | Lifecycle, routing transitions, merge bases, verifier vocabularies remain owned slots (§5B; I-34 note; D10/D11); Step-6 predicate-lexicon ownership noted; only contract-reserved codes registered |

*(v1.2 issuance declaration — superseded by the v1.3 check below.)*

### Final v1.3 checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| object_kind enum unchanged | PASS | §3 YAML: enum(phenomenon, construct, relationship, knowledge_artifact) untouched |
| artifact_kind adds exactly one value: method | PASS | §3 enum line `[v1.3]`; §4a; §5A row — six prior values + `method`, nothing else |
| measure remains distinct from method | PASS | §4a hard distinction; V11 fourth row keeps `measure` |
| artifact_kind mandatory iff object_kind = knowledge_artifact | PASS | I-10 untouched; §3 comment unchanged |
| no null artifact_kind introduced | PASS | §4a; §5A anti-column ("a null value") |
| existing methodological artifacts representable | PASS | V11 rows 1–3 validate: object_kind=knowledge_artifact, artifact_kind=method, verbatim mentions |
| absent methodological artifact classes not fabricated as objects | PASS | §4a applies only when the artifact itself bears the deficiency; absence cases carry no artifact referent (Step-8 OR-ART-7a consumes this) |
| no unrelated schema field changed | PASS | Diff surface = title, revision record, enum line, §4a, §5A/§4 rows, example version strings, V11, this check |
| no Step-5/6/9/10 ownership moved into schema | PASS | §5B owned slots untouched; no lifecycle/merge/detection content added |
| all schema examples validate under GS-1.3 | PASS | V1–V10 re-audited (version strings + enum widening backward-compatible); V3 mention spans corrected (I-45); V5 unlicensed `about` removed; V11 completed field-by-field |

### Final-issuance correction checks (same version)

| Check | PASS/FAIL | Evidence |
|---|---|---|
| object-denoting anaphor behavior defined | PASS | I-44 first clause; "This theory/assumption/relationship" may stand as mention |
| carrier/reference-anaphor behavior defined | PASS | I-44 second clause; resolution to antecedent referent |
| "this gap" cannot become canonical affected_object merely by referring to a gap | PASS | I-44; invalid ex. 35 |
| "such evidence" cannot become canonical affected_object merely by referring to deficient evidence | PASS | I-44 (carrier anaphor class; "such evidence" named) |
| canonical affected_object may resolve to a source-grounded antecedent | PASS | I-44 employee-turnover example; V3 |
| completion does not invent source wording | PASS | I-44 "supports resolution without rewriting"; I-9b unchanged |
| mention.surface_form is verbatim | PASS | object_mention block unchanged; I-45 coherence |
| every mention_span_ref contains/supports the declared surface_form | PASS | I-45; V3 mention_span_refs = [S3] |
| context_support retains the local dependency expression separately | PASS | context_support.dependency_expression (existing field); V3 block |
| V3 uses a single coherent canonical surface form | PASS | corrected V3 yaml + explanatory note |
| V3 no longer mixes "coordination mechanisms" and "These mechanisms" as equivalent mention spans | PASS | S4 excluded from mention_span_refs; annotated in-line |
| `about` requires explicit source-grounded artifact-subject content | PASS | I-42 + v1.3 clarification with licensed/not-licensed lists |
| artifact naming alone does not create `about` | PASS | I-42 clarification; invalid ex. 36 |
| V5 contains no unlicensed about field | PASS | about removed; ABSENT comment in V5 |
| V11 validates against the normative gap_record schema | PASS | field-by-field audit note under V11 |
| V11 normalized proposition uses text + source_trace_refs + normalization_method | PASS | corrected block, norm-proc-0.1 as in V1–V10 |
| V11 contains contrast | PASS | {status: not_reported, entries: []} |
| V11 contains persistence_reasons | PASS | [] |
| V11 contains claim_links | PASS | [] |
| artifact_kind = method remains valid | PASS | §3 enum; §4a; V11 unchanged in purpose |
| measure remains distinct from method | PASS | §4a hard distinction; V11 compact table fourth row |
| no unrelated schema field changed | PASS | diff surface = revision record, mention comment, I-42 note, I-44/I-45, V3, V5, V11, invalid ex. 34–37, this table |
| Step 8 ownership remains outside the schema | PASS | I-42 clarification defers qualification to Step 8; no extraction rulebook added |
| Step 9 ownership remains outside the schema | PASS | no merge/identity logic anywhere |
| Step 10 ownership remains outside the schema | PASS | no detection logic anywhere |

*(v1.3 freeze declaration — historical; superseded by the v1.4 check and declaration below.)*

### Final v1.4 checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| one GAP candidate can represent N extraction instances | PASS | routing_set + I-46/I-47 |
| every extraction_instance_id occurs exactly once | PASS | I-47; invalid ex. 40/45 |
| mixed CREATED/ATTACHED outcomes are representable | PASS | V12 |
| partially routed candidates are representable | PASS | V13 |
| ROUTING_REVIEW_OPEN is nonterminal and has no target_gap_id | PASS | §5A meaning + I-48; invalid ex. 44 |
| UNROUTED has no target_gap_id | PASS | I-48; invalid ex. 43 |
| CREATED has exactly one target_gap_id | PASS | I-48/I-49; invalid ex. 41/45 |
| ATTACHED has exactly one target_gap_id | PASS | I-48/I-49; invalid ex. 42/45 |
| frozen Step-11 bundle identity is represented | PASS | extraction_bundle_id + structured_output_digest + I-46; invalid ex. 46 |
| routing entries cannot be added/deleted/duplicated by routing | PASS | I-46/I-47 |
| one compound candidate remains one candidate | PASS | I-51; §2 sentence |
| no child candidate / fission structure introduced | PASS | I-51 |
| singular promoted_gap_id removed | PASS | §3 + I-37; invalid ex. 47 |
| singular attached_to_gap_id removed | PASS | §3 + I-37; invalid ex. 47 |
| promoted removed from candidate routing_outcome | PASS | §3/§5A; invalid ex. 47 |
| attached_as_restatement removed from candidate routing_outcome | PASS | §3/§5A; invalid ex. 47 |
| rejected_non_gap remains candidate-level | PASS | §3/§5A/I-34 |
| uncertain_queued remains candidate-level | PASS | §3/§5A/I-34 |
| schema contains every fact required by A1E-SM-1.4 MI-19 | PASS | routing_set representation; I-48/I-50; V13 |
| schema does not implement State Machine transitions | PASS | I-50 ownership fence; V13 note |
| no gap_record semantic field changed | PASS | normative diff surface = candidate routing only |
| no Step-9 identity logic moved into schema | PASS | ownership audit; statuses are structural facts |
| no Step-11 extraction semantics moved into schema | PASS | bundle referenced by id/digest only |
| no Step-12 decision logic moved into schema | PASS | statuses record outcomes, never decide them |

**All internal schema checks PASS — A.1-E Gap Object Schema v1.4 (`A1E-GS-1.4`) is presented as READY FOR INDEPENDENT AMENDMENT AUDIT. `A1E-GS-1.3` remains the preceding frozen version until this amendment passes independent freeze audit.**
