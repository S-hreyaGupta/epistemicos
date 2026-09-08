# A.1-E Annotation & Validation Protocol v1.2 — EpistemicOS (Step 3)

**Status:** normative once the Protocol Freeze Check (29.16) passes. Final targeted revision of Protocol v1.1 before Step-3 freeze.
**Normative inputs (frozen):** `A1E_gap_extraction_contract_v1-2.md`; `A1E_gap_object_schema_v1-2.md`.
**Defines:** the measurement architecture for A.1-E. It does not define boundary semantics (Step 5), predicate mappings (Step 6), object rules (Step 8), merge rules (Step 9), the detection candidate envelope (Step 10), or verifier logic (Step 13).

**Revision record (v1.1 → v1.2):** (1) two explicit validation regimes — **component/oracle-input** evaluation (each component scored on the full gold population with gold upstream input) and **operational/pipeline** evaluation (full system, predictions flow normally); component gates use the oracle regime so a weak upstream stage can never shrink a downstream denominator; (2) acceptance-gate populations reworked accordingly, with gate classes COMPONENT_GATE / PIPELINE_GATE / STRUCTURAL_GATE; (3) Layer-1 proposition segmentation made independently annotatable via `boundary_annotation_attempt` proposals plus a mechanical alignment/adjudication stage; segmentation disagreement enters reliability reporting; (4) protocol pilot split from the **final annotation/calibration phase**; `TBD_BY_PILOT` → `TBD_BY_FINAL_CALIBRATION` wherever a value cannot legitimately be set under `interim-0`; (5) annotator requirements fixed per split — sealed cohorts 100% independently double-annotated and adjudicated on all epistemically material labels; development gold under a pre-registered QA/sampling design; (6) adjudication defect enum corrected (`annotation_error`; separate `confirmed_no_defect` outcome for non-disagreement records); (7) normalization gold elements made machine-unambiguous via a typed discriminated union; (8) root/cascade machinery confined to the operational regime.

---

## 29.1 Validation principles

1. **Three regimes of process, never collapsed.** Annotation, validation, acceptance — separate artefacts with separate outputs in every report.
2. **Two regimes of validation, both mandatory `[REV v1.2]`.** Component/oracle evaluation answers "does this component work given correct input?" on the **full gold population**; operational/pipeline evaluation answers "what does the assembled system do?". Component gates use the oracle regime; operational metrics are reported alongside and never substitute for them — and vice versa.
3. **Three populations, never conflated.** Annotation-unit census, detection candidates (Step-10 artefacts), and gap assertion instances are distinct; every metric names its population and its input regime.
4. **Gold mirrors the schema's semantics, not its ergonomics.** Gold payload maps 1:1 to Schema v1.2 meanings; annotation-only metadata lives in a separated envelope.
5. **What the contract excludes, annotation excludes.** No taxonomy, mode, construction, importance, novelty, validity, scope/context structure, citation-support judgment, or inferred/reconstructed label exists in gold.
6. **Layered and independent where judgment lives `[REV v1.2]`.** Layers freeze upward; boundary annotators never see system predictions; proposition segmentation itself is independently produced per annotator and only then aligned and adjudicated.
7. **Errors are counted where they arise — in the regime where they can arise `[REV v1.2]`.** In oracle evaluation the upstream input is gold, so upstream causes do not exist and components are scored directly. In operational evaluation, multiple independent roots may coexist and every cascade names a sufficient upstream cause.
8. **Numbers are earned in the right phase `[REV v1.2]`.** The only fixed threshold is zero Class-A contract violations. Every other threshold, floor, and the MATCH_CRITERION is `TBD_BY_FINAL_CALIBRATION`: set only in the final annotation/calibration phase (after Steps 5/6/8/9 freeze), documented, pre-registered, and frozen **before** any sealed cohort is exposed. Pilot observations inform calibration design; they never become thresholds by primacy. Human unreliability never automatically lowers a system requirement.
9. **An exposed test set is spent.** One acceptance attempt per sealed cohort; exposure makes it audit-only; any tuning informed by it requires a fresh sealed cohort; identical-build reproducibility reruns are the only exception. All thresholds and the MATCH_CRITERION are already frozen before exposure.
10. **Version-pinned meaning.** Every gold label carries the pinned versions; `interim-0` labels are protocol-pilot artefacts only and can never become final gold or ground final thresholds.

---

## 29.2 Evaluation units

Carried from v1.1 unchanged (annotation_unit census → gold_boundary_unit → gold_gap_instance → gold_canonical_gap; detection_candidate as the system-side interface; mixed units yield multiple boundary units; census ≠ detection inventory), with one addition `[REV v1.2]`: each gold layer's adjudicated output doubles as the **oracle input** for the next component's evaluation (29.8-O), which is why layer-wise adjudication and freezing is not only an annotation discipline but the enabling condition of component validation.

---

## 29.3 Gold annotation schema (machine-readable) `[REV v1.2 where noted]`

Conventions as v1.1. Changes: independent Layer-1 proposals; restructured `gold_boundary_unit`; typed `required_elements`; corrected adjudication enum. Unchanged entities (`gold_document`, `annotation_unit`, `gold_gap_instance` except the noted field, `gold_canonical_gap`, `gold_identity`) carry forward from v1.1.

```yaml
boundary_annotation_attempt:               # [REV v1.2] independent per-annotator Layer-1 product
  attempt_id: string
  annotator_id: string
  annotation_unit_id: string
  unit_census_vote: enum(no_proposition, has_proposals)
  proposed_units:                          # 0..n; the annotator independently decides HOW MANY
    - proposal_id: string                  #   proposition units exist, WHERE each begins/ends,
      segment_span_refs: [string]          #   and WHICH class each receives
      boundary: enum(GAP, MOTIVATION, OWN_LIMITATION, FUTURE_RESEARCH,
                     CONTRIBUTION, OTHER, UNCERTAIN)
      certainty: enum(confident, uncertain)          # annotation-only
      rationale_codes: [string]
      note: string                                   # opt; annotation-only

gold_boundary_unit:                        # [REV v1.2] the ADJUDICATED proposition unit
  boundary_unit_id: string
  annotation_unit_id: string
  adjudicated_segment_span_refs: [string]
  adjudicated_boundary: enum(...same 7...)
  source_proposal_refs: [string]           # the aligned proposals this unit was adjudicated from (0..n;
                                           #   0 permitted only via adjudicator-added unit, flagged)
  adjudication_ref: string
  flags: [enum(pragmatic_only, adjudicator_added)]
  gap_instance_id: string                  # req iff adjudicated_boundary = GAP

gold_gap_instance:
  # ... all fields as v1.1, with one change [REV v1.2]:
  gold_payload:
    proposition:
      normalized_reference:
        reference_text: string
        required_elements:                 # typed discriminated union — no interpretation guessing
          - element_kind: enum(relation_token, kind_token, object_reference,
                               preserved_context_segment, artifact_reference)
            source_type: enum(literal_value, span_ref)
            value: string                  # interpretation fixed by source_type:
                                           #   literal_value → controlled semantic value
                                           #   span_ref      → source-span identifier
          # per-kind constraints (I-N1): relation_token, kind_token MUST be literal_value drawn
          # from the frozen contract enums; preserved_context_segment MUST be span_ref;
          # object_reference, artifact_reference MUST be span_ref (mention spans)

adjudication_record:                       # [REV v1.2] corrected outcome model
  adjudication_id: string
  item_ref: {unit: enum(annotation_unit, boundary_segmentation, boundary_unit, instance,
                        span, field, contrast, reason, identity_pair), id: string, field: string}
  record_origin: enum(annotator_disagreement, escalation_flag, qa_sample)
  raw_a: string                            # req iff origin = annotator_disagreement
  raw_b: string                            # req iff origin = annotator_disagreement
  disagreement_type: string                # controlled per field; segmentation types include
                                           #   SEG-PRESENCE, SEG-COUNT, SEG-EXTENT, CLASS (29.4-A)
  rulebook_reference: {asset: string, version: string, clause: string}
  adjudicated_label: string
  adjudicator_id: string
  reason_code: string
  adjudication_outcome: enum(defect_classified, confirmed_no_defect)   # [REV v1.2]
  defect_class: enum(annotation_error, rulebook_ambiguity,
                     schema_insufficiency, genuine_epistemic_ambiguity)
                                           # req iff outcome = defect_classified; the four classes are
                                           #   mutually exclusive; disagreement-origin records normally
                                           #   resolve into one of them; confirmed_no_defect exists for
                                           #   non-disagreement origins (escalation/QA) found sound
  blind: boolean
```

**29.3-N Normalized-proposition gold** — Option C staged, as v1.1, now over the typed `required_elements`: element-coverage and hallucination checks resolve each element by its `source_type` deterministically; once the normalization grammar freezes, the grammar applied to the typed elements yields the exact expected string.

---

## 29.4 Annotation workflow

Layers, upward freezing, blindness to system output, span mechanics (29.4-S), and Layers 2–5 carry forward from v1.1 unchanged, with Layer 1 replaced `[REV v1.2]`:

1. **L0 — Unit census.** Deterministic, prediction-independent segmentation into annotation units (pinned segmentation asset).
2. **L1a — Independent proposition proposals.** Each annotator independently produces a `boundary_annotation_attempt` per unit: a census vote and 0..n proposed proposition units, each with its own segment spans, class, certainty, rationale. Neither annotator sees the other's proposals or any system prediction.
3. **L1b — Alignment (mechanical) + adjudication.** Proposals are aligned by the protocol-level procedure 29.4-A; the adjudicator resolves count, extent, then class against the pinned rulebook, producing `gold_boundary_unit`s with `source_proposal_refs`. Segmentation disagreements are typed and logged; they feed reliability reporting (29.9). `pragmatic_only` flagging and the never-GAP/never-`context_supported` rule for pragmatically-inferable deficiencies apply as before. Adjudicated boundary units freeze.
4. **L2–L5 and close-out** as v1.1 (spans & explicitness → primitives with `object_scope_boundary` raised at L3 → supporting structures with spawn cycling → identity over instances → census audit).

**29.4-A Proposal alignment (protocol mechanics; no Step-5 semantics) `[REV v1.2]`.** Within an annotation unit, A's and B's proposals are grouped into alignment clusters by span overlap (any character overlap links two proposals; transitive closure forms the cluster). Cluster patterns and their recorded disagreement types:

| Pattern | Meaning | Disagreement type |
|---|---|---|
| 1 A-proposal ↔ 1 B-proposal | Aligned pair; compare extent and class | `SEG-EXTENT` if spans differ beyond tolerance; `CLASS` if classes differ; none if both agree |
| 1 ↔ many (or many ↔ many) | Proposition-**count** disagreement (A sees one, B sees two, …) | `SEG-COUNT` |
| 1 ↔ 0 | One annotator marks a proposition the other does not | `SEG-PRESENCE` |
| census votes differ (`no_proposition` vs `has_proposals`) | Unit-level presence disagreement | `SEG-PRESENCE` (unit level) |

Adjudication order inside a cluster: **count → extent → class**, each decided against the pinned rulebook and recorded with its own disagreement type and defect class. The adjudicator may, exceptionally, mint a unit neither annotator proposed (`adjudicator_added` flag; always `defect_classified` — it evidences a rulebook or instruction defect, never silent gold repair). Alignment is purely mechanical (overlap grouping); what counts as one proposition is decided in adjudication under the pinned rulebook — the substantive segmentation semantics remain Step-5 property.

---

## 29.5 Adjudication workflow

As v1.1, with the v1.2 record model: origins (`annotator_disagreement` / `escalation_flag` / `qa_sample`); disagreement-origin records normally resolve into one of the four defect classes (`annotation_error` · `rulebook_ambiguity` · `schema_insufficiency` · `genuine_epistemic_ambiguity` — mutually exclusive, never collapsed, routed to their owners); `confirmed_no_defect` is reserved for non-disagreement records found sound. Segmentation clusters adjudicate per 29.4-A. Identity disagreements at instance-pair level with the conservative pre-Step-9 default, unchanged.

---

## 29.6 Corpus construction protocol

Carried from v1.1 (mandatory coverage cells; envelope-wide stratification with qualitative oversampling of rare constructions; sequential-calibration cell support with the stopping rule now `TBD_BY_FINAL_CALIBRATION` `[REV v1.2]`; mandatory-expansion triggers; splits `pilot` / `development` / `frozen_test_cohort` / `reserve`; intake-time stratified assignment).

**Split production constraints `[REV v1.2]`:** the pilot split may be produced under `interim-0`; the development split and every sealed cohort are produced **only** in the final annotation/calibration phase (29.13b), under frozen Steps 5/6/8/9 and the regenerated manual, and under the annotator requirements of 29.6-D.

**29.6-D Annotator requirements by split `[REV v1.2]`.**

- **Protocol pilot:** all epistemically material fields independently double-annotated (disagreement-mode discovery is the point).
- **Sealed acceptance cohorts:** every epistemically material label MUST be independently double-annotated and adjudicated **before sealing** — proposition segmentation (the L1a proposals themselves), boundary, assertion span, context-support evidence, explicitness, relation, knowledge_kind, affected object (surface, mentions, kinds, `about`), contrast, persistence and spawn where applicable, merge identity. Administrative metadata and deterministic registry outputs (e.g., Citation Registry resolution results) are exempt.
- **Development gold:** may use a calibrated QA/sampling design once annotators are qualified, provided the policy is **pre-registered** in the calibration phase; disputed/hard/flagged cases are always double-annotated; a continuing double-annotated subset monitors reliability; and **no single-annotated item ever enters IAA computation**. No sampling percentage is invented here — `TBD_BY_FINAL_CALIBRATION`.

**29.6-T One-exposure test policy** — carried verbatim from v1.1, with the clarification restated `[REV v1.2]`: all gate thresholds and the MATCH_CRITERION are frozen (29.10-P step 8) **before** any cohort is exposed; an exposed cohort is spent for any subsequently tuned build; fresh sealed cohorts come from reserve; identical-build reruns for technical reproducibility only.

---

## 29.7 Error taxonomy and error accounting `[REV v1.2]`

Codes, units, definitions, severities, owners, and the prerequisite/dependency table carry forward from v1.1, with the accounting now **regime-scoped**:

- **Component/oracle regime:** upstream input is gold, so upstream causes do not exist; every mismatch is a direct component error, scored plainly against the gold output. No cascade classification, no `caused_by` links, no suppression — the full gold population is the denominator.
- **Operational/pipeline regime:** the multi-root/cascade model applies exactly as in v1.1 — multiple independent roots may coexist; a mismatch is a cascade only when an already identified upstream error is *sufficient to explain it*, named in `caused_by_error_ids`; the prerequisite table aids classification; cascades are annexed, never deleted.

E-DETECT-* codes exist only in the operational regime (detection has no oracle). E-DETECT-FP\* remains reserved/diagnostic pending the Step-10 envelope.

---

## 29.8 Metric registry `[REV v1.2]`

**29.8-O Oracle inputs (exact, per component).**

| Component | Oracle input (adjudicated gold) | Oracle output compared against |
|---|---|---|
| Boundary | `gold_boundary_unit.adjudicated_segment_span_refs` (+ document co-text) — full population, all classes | `adjudicated_boundary` |
| Span & explicitness | GAP `gold_boundary_unit`s (adjudicated segment + GAP class) | Instance L2 payload: assertion spans, explicitness, dependency type/expression, support spans |
| Relation / Knowledge kind / Affected object | Gold assertion + context-support spans (adjudicated L2) | L3 payload per field (values + mentions), field-specific gold traces available for error analysis |
| Normalization | Gold spans + gold primitives | Typed `required_elements` coverage + hallucination check |
| Contrast | Gold gap instance (L2+L3 payload) + document co-text | L4 contrast (status, entries, attributed spans, referents) |
| Citation association / resolution | Gold citation-mention spans (+ Citation Registry, authoritative) | Association to entry/reason; resolution outcome |
| Persistence | Gold gap instance + co-text | Reason presence + spans |
| Spawn | Gold persistence-reason spans | `independent_assertion` verdict + spawned-instance link |
| Merge | Complete gold pre-merge instance set of the document (all L2–L4 payloads) | Gold partition + pair judgments (pairwise) |
| Verification storage | Gold record with gold-determinable flag conditions | Contract-required flag behavior |
| Routing | Adjudicated boundary per candidate-equivalent unit | Routing-outcome consistency |
| Detection | **No oracle** — input is the manuscript; evaluated operationally against gold GAP instances | — |

**29.8-M Metric table.** Metric definitions (confusion matrices, exact/overlap span measures per MATCH_CRITERION_TBD, per-field accuracies, pairwise merge P/R with directional counts, element-coverage/hallucination, abstention handling, gold-UNCERTAIN exclusion-with-reporting) carry forward from v1.1; each now runs in one or both regimes:

| Component | Oracle/component metric | Operational metric | Gold input | System input |
|---|---|---|---|---|
| Detection | — (none by nature) | Recall over gold GAP instances (availability per MATCH_CRITERION); precision RESERVED_STEP10 | Gold GAP instances as targets | Manuscript |
| Boundary | 7-class confusion; GAP P/R/F1; abstention — on the **full** adjudicated boundary-unit population | Same metrics on detection-reached units; GAP-FN decomposition (undetected vs misclassified) | Adjudicated segments | System candidates/segments |
| Span | Exact rate; overlap F1; boundary distance; truncation/over-extension — on **all** gold GAP instances | Same on operationally reached instances | Gold GAP boundary units | System GAP-classified items |
| Explicitness | Accuracy + direction; dependency-type accuracy — on all gold GAP instances (gold spans given) | Same on span-assessable operational instances | Gold L2 evidence | System spans |
| Relation | Accuracy, per-value F1, confusion — full gold-instance population | Same on operational assessable population | Gold spans | System spans |
| Knowledge kind | Accuracy; forced-kind rate on gold-`unspecified` — full population | Same, operational | Gold spans | System spans |
| Affected object | Mention IoU; surface match; object_kind / artifact_kind accuracy; `about` grounding; E-OBJECT-SCOPE rate — full population | Same, operational | Gold spans | System spans |
| Normalization | Element coverage; hallucination rate; [post-grammar exact-string] — full population | Same, operational | Gold spans + primitives | System spans + primitives |
| Contrast | Status accuracy; entry alignment P/R; referent capture — full population | Same, operational | Gold instances | System records |
| Citation association | Mention detection P/R; resolution accuracy; association accuracy | Same, operational | Gold mention spans + Registry | System mentions |
| Persistence | Presence P/R; span overlap — full population | Same, operational | Gold instances | System records |
| Spawn | Spawn precision and recall separately — over all gold reasons | Same, operational | Gold reason spans | System reasons |
| Merge | Pairwise P/R/F1; over-/under-merge counts; unresolved-handling — over the **complete** gold pre-merge partition | Same over operationally surviving instances; propagation analysis | Full gold instance set | System instance set |
| Verification | Flag-behavior accuracy — gold-determinable conditions | Same, operational | Gold records | System records |
| Routing | Routing consistency — adjudicated boundaries | Same, operational | Adjudicated boundaries | System boundaries |
| End-to-end | — | Strict-record rate; cumulative propagation; review load; abstention economics; root/cascade graph | — | Full pipeline |

Reporting requirement: wherever both columns are meaningful, both are reported and labeled — e.g. *Relation accuracy — oracle input* vs *Relation accuracy — operational matched population*. The former evaluates the extractor; the latter, the user experience after upstream error. Neither substitutes for the other.

---

## 29.9 Inter-annotator agreement `[REV v1.2 additions]`

As v1.1 (Krippendorff's α + raw agreement for nominal fields; overlap-based agreement for spans; pairwise identity agreement over instance pairs; IAA = gold reliability, never system quality; floors via 29.10-P; single-annotated items never enter IAA), plus **segmentation reliability**: (i) unit-level census agreement (`no_proposition` vs `has_proposals`); (ii) proposition-count agreement per annotation unit; (iii) proposal alignment F1 (overlap-based pairing of A's and B's proposals); (iv) class agreement (α) computed **on aligned pairs only**, co-reported with the alignment rate so segmentation mismatch is visible rather than silently deflating class agreement. SEG-PRESENCE / SEG-COUNT / SEG-EXTENT rates from 29.4-A are part of the reliability report.

---

## 29.10 Acceptance-gate registry `[REV v1.2]`

**29.10-P Common threshold-setting procedure** — carried from v1.1 verbatim (eight steps; human reliability as evidence, never an automatic discount; documentation; **freeze before sealed exposure**), with the phase correction: the procedure executes **only in the final annotation/calibration phase** (29.13b). All non-structural values are `TBD_BY_FINAL_CALIBRATION`.

Gate classes: `COMPONENT_GATE` (oracle regime, full gold population) · `PIPELINE_GATE` (operational regime) · `STRUCTURAL_GATE` (contract-violation counts / structural preconditions).

| Gate | Class | Metric | Population / input regime | Threshold source | Threshold | Failure consequence |
|---|---|---|---|---|---|---|
| G-0a Gold reliability (per field, incl. segmentation) | STRUCTURAL (gold precondition) | Field IAA incl. 29.9 segmentation measures | Double-annotated gold for the split in use | empirically-calibrated (29.10-P) | TBD_BY_FINAL_CALIBRATION | Gold unusable for that field; re-annotation / rulebook escalation |
| G-0b Census completeness | STRUCTURAL | 100% units closed | Cohort documents | risk-derived | 100% | Document excluded; replaced from reserve |
| G-1 Detection recall | PIPELINE_GATE | Recall over gold GAP instances | Operational; frozen cohort | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block; detection rework |
| G-1r Detection precision | (reserved) | Pending Step-10 envelope | — | — | RESERVED_STEP10 | Not a gate until defined |
| G-2/G-3 Boundary (GAP precision / GAP recall) | COMPONENT_GATE | GAP P and R + confusion | **Full adjudicated boundary-unit population, oracle segments** — not detector-reached items | empirically-calibrated (joint, direction-costed) | TBD_BY_FINAL_CALIBRATION | Block; boundary rework |
| G-4 Span | COMPONENT_GATE | Overlap measure + truncation ceiling (frozen MATCH_CRITERION) | **All gold GAP instances, gold GAP input** | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block |
| G-4b Explicitness | COMPONENT_GATE | Accuracy + direction ceiling | All gold GAP instances, gold L2 evidence | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block |
| G-5 Relation | COMPONENT_GATE | Accuracy | Full gold-instance population, gold spans | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block |
| G-6 Knowledge kind | COMPONENT_GATE | Accuracy + forced-kind ceiling | Full population, gold spans | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block |
| G-7 Affected object | COMPONENT_GATE | Mention IoU + kind accuracies + E-OBJECT-SCOPE ceiling | Full population, gold spans | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block |
| G-8 Merge | COMPONENT_GATE | Pairwise over-merge ceiling + F1 floor | **Complete gold pre-merge partition**, gold instance set | empirically-calibrated (risk-weighted ceiling) | TBD_BY_FINAL_CALIBRATION | Block; identity rework |
| G-9 Critical errors | STRUCTURAL_GATE | Class-A count (29.11) | All system records, both regimes; frozen cohort for acceptance | **risk-derived — fixed now** | **0** | Block absolutely; incident review |
| G-10 Class-B budget | STRUCTURAL_GATE (budgeted) | Class-B counts | Frozen cohort | empirically-calibrated | TBD_BY_FINAL_CALIBRATION | Block until under budget |
| End-to-end strict-record rate | Reporting / optional PIPELINE_GATE | Composite | Operational, frozen cohort | empirically-calibrated if adopted | TBD_BY_FINAL_CALIBRATION (optional) | Never substitutes for component gates |

Component failures cannot be hidden by upstream selection: every COMPONENT_GATE denominator is the full gold population under oracle input, by construction. All mandatory gates must pass on the named fresh cohort; thresholds and MATCH_CRITERION are frozen before that cohort's exposure.

---

## 29.11 Critical-error policy

Carried from v1.1 unchanged: **Class A** zero-tolerance contract violations (invented/reconstructed gap; fabricated object; scope structure; A.1-C/A.1-A judgment fields; citation-support judgment; pragmatic-inference emission) — measured in both regimes, gated structurally; **Class B** budgeted severe semantic errors (materially-distinct over-merge at instance-pair level; proposition-altering truncation; spawn false positive; unsupported-element normalization); **Class C** ordinary component errors under gates; severity not exaggerated.

---

## 29.12 Versioning / re-annotation policy

Carried from v1.1 (pinned versions on every gold item; `interim-0` definitions; re-annotation triggers via rationale-code indexing; quarantine-and-replace for sealed cohorts), with the phase structure sharpened `[REV v1.2]`: `interim-0` supports the **protocol pilot only** (29.13a); final development gold, sealed cohorts, and every calibrated value are products of the **final annotation/calibration phase** (29.13b) and of nothing earlier.

---

## 29.13 Pilot and final calibration `[REV v1.2]`

### 29.13a Protocol pilot (before Steps 5/6/8/9 freeze; `interim-0` permitted)

**Purpose — only:** test annotation tooling; test the layered workflow incl. L1a/L1b proposal-and-alignment mechanics; test adjudication mechanics and the defect-class routing; discover missing schema/protocol states; estimate workload; identify semantic questions for the later rulebooks; gather preliminary information for **designing** the calibration phase (candidate matching-distribution shapes, prevalence sketches, throughput).

**Outputs are exploratory.** The pilot MUST NOT produce final development gold, sealed acceptance gold, final thresholds, or the final MATCH_CRITERION.

**Exit criteria (structural):** consecutive waves add no new `rulebook_ambiguity` / `schema_insufficiency` findings in any layer; every mandatory coverage cell exercised through all layers, including the segmentation-disagreement patterns of 29.4-A; each defect class and each `record_origin` has a worked precedent; adjudication queue empty; the calibration-phase design document is complete (what will be calibrated, from what data, by whom); the manual regenerates cleanly from the pinned-asset manifest. Pilot exit authorizes nothing beyond readiness for 29.13b.

### 29.13b Final annotation / calibration phase (only after Steps 5/6/8/9 freeze)

```text
regenerate final annotation manual (versioned build manifest)
        ↓
annotate + adjudicate development gold  (29.6-D requirements)
        ↓
calibrate: MATCH_CRITERION · IAA floors · acceptance thresholds ·
           corpus-support / sequential stopping rules   (all via 29.10-P)
        ↓
document every derivation
        ↓
pre-register + freeze all gates and the MATCH_CRITERION
        ↓
construct / retain sealed acceptance cohort(s) (29.6-D sealed requirements; 29.6-T)
```

Only this phase may produce final values. Pilot estimates inform calibration design; they never become thresholds by having been observed first.

**Guideline generation** — carried: the manual is mechanically assembled from the pinned assets via a versioned build manifest; handwritten content is tooling mechanics only, non-normative; a non-regenerable manual is invalid for annotation.

---

## 29.14 Reporting template `[REV v1.2 additions]`

As v1.1 (header with cohort id + exposure ledger; gold-validity block; component tables; critical register; gate outcomes; abstention economics; deltas; defect feed), with: (3′) every component table labeled by **regime** — oracle metrics on full gold populations and operational metrics side by side wherever both are meaningful; (4′) the multi-root/cascade error-accounting block appears **only** in the operational section; the oracle section reports plain component scores; (2′) the gold-validity block includes the 29.9 segmentation-reliability measures and confirms sealed-cohort double-annotation compliance (29.6-D).

---

## 29.15 Open issues

- **OI-P1** MATCH_CRITERION — family and parameters set in 29.13b from calibration data + Step-10 candidate semantics; frozen pre-exposure. `[REV: phase corrected]`
- **OI-P2** Sequential stopping-rule parameterization — 29.13b. `[REV]`
- **OI-P3** UNCERTAIN/abstention economics — operational-regime question; calibration-phase data required.
- **OI-P4** Shared vs field-specific production traces — the declared empirical test; comparison data now spans pilot (exploratory) and 29.13b (decisive); outcome routes to schema governance.
- **OI-P5** Tooling ownership for the normalization element-coverage checker (now simplified by the typed union).
- **OI-P6** Reserve-cohort pipeline sizing under the one-exposure consumption rate — 29.13b resourcing.
- **OI-P7** Detection-evaluation interface pending Step 10 (envelope; availability semantics; precision denominator) — G-1r reserved.
- **OI-P8 `[NEW]`** Development-gold QA/sampling design parameters (sampling rates, qualification criteria, reliability-monitoring subset size) — pre-registered in 29.13b; deliberately not invented here.

---

## 29.16 Protocol freeze check

### Carried forward (v1.0 + v1.1 checks, re-audited under v1.2)

All thirty-one prior checks re-audited: **PASS**, with evidence updated where affected — component/span/primitive separation is now regime-explicit (29.8); candidate-recall measurability unchanged (operational, gold GAP instances); merge separability now additionally gate-anchored to the complete gold partition (G-8); disagreement machinery extended to segmentation without weakening any prior property (29.4-A, 29.9); leakage control unchanged and restated (29.6-T); no fabricated numbers remain (all `TBD_BY_FINAL_CALIBRATION`; only G-9 = 0 fixed); interim-0 restriction and final-gold sequencing strengthened into the two-phase structure (29.13); pinning, critical-error reporting, and Steps-5–9 survivability intact.

### New v1.2 checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| Component performance can be measured with oracle upstream input | PASS | 29.8-O defines the exact oracle input per component; principle 2; COMPONENT_GATE populations (29.10) |
| Operational pipeline performance is separately measured | PASS | 29.8-M operational column; end-to-end row; 29.14 regime-labeled reporting; detection and propagation remain operational |
| A bad upstream component cannot improve a downstream component's gate by shrinking its denominator | PASS | Every COMPONENT_GATE runs on the full gold population with gold input (29.10 table; revision rationale); operational conditional populations are reporting-only for those components |
| Proposition segmentation is independently annotated | PASS | `boundary_annotation_attempt` with per-annotator `proposed_units` (29.3); L1a blindness (29.4); sealed-cohort double-annotation includes segmentation (29.6-D) |
| Proposition-count disagreements can be adjudicated | PASS | 29.4-A cluster patterns SEG-PRESENCE / SEG-COUNT / SEG-EXTENT / CLASS; count→extent→class order; `source_proposal_refs` + `adjudicator_added` flag; disagreement types in `adjudication_record` |
| Final thresholds cannot come from interim-0 pilot labels | PASS | 29.13a prohibition list; principle 8; TBD_BY_FINAL_CALIBRATION terminology throughout (29.10, 29.6) |
| Final calibration occurs after Steps 5/6/8/9 | PASS | 29.13b timing condition and sequence diagram; 29.12 phase statement |
| Sealed acceptance gold is independently double-annotated | PASS | 29.6-D sealed-cohort requirement enumerating all epistemically material labels incl. segmentation; sealing gated on adjudication; 29.14.2′ compliance reporting |
| Development QA policy does not contaminate IAA | PASS | 29.6-D development rules: pre-registered policy; hard cases double; monitoring subset; single-annotated items never enter IAA (also 29.9) |
| Adjudication defect classes are mutually clear | PASS | 29.3 `adjudication_outcome` + four mutually exclusive defect classes; `annotation_error` renamed; `confirmed_no_defect` defined separately for non-disagreement origins (29.5) |
| Normalization gold elements are machine-unambiguous | PASS | Typed discriminated union with `source_type` and per-kind constraints (29.3, I-N1); no string ever requires interpretation guessing |
| Root/cascade logic is confined to where causal upstream errors actually exist | PASS | 29.7 regime scoping: oracle = plain scoring, no cascade machinery; operational = multi-root/cascade with named sufficient causes; 29.14.4′ places the graph in the operational section only |

**All checks PASS — the A.1-E Annotation & Validation Protocol is declared FROZEN at v1.2.**
