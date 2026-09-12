<execution_gap_HL_3>
# A.1-E Gap HLA — Execution-readiness analysis and implementation plan

# PART I — EXECUTION-READINESS ANALYSIS

Scope: what the high-level development architecture (`Gap_spec_HLA.docx`) still lacks before it can be executed (implemented, run, validated, frozen). Worked examples are excluded by instruction. Everything below is traced to the consolidation materials: the requirements register (R-*), the triage/adjudication outputs (memos M1–M5, blocker slugs), the recorded decisions (HD-*/SD-*), and the source specifications (D01–D13).

Readiness definition used throughout — a module is execution-ready when it has: (1) a typed interface schema; (2) its operative rules written out with an execution type (D/S/H/J); (3) closed vocabularies for every enum it emits; (4) every blocker it carries closed or explicitly parked with defined behaviour; (5) conformance tests and gold it can be scored against; (6) the platform guarantees it consumes contracted; and (7) the implementation artefacts needed to materialize and continuously enforce those contracts without introducing new scientific meaning.

## 0. Verdict

The HLA fixes module boundaries, data objects at type level, ordering, invariants and the switchable identity branch. It is **not execution-ready**: 37 items are explicitly "deferred to RECORDS", 17 blockers are open, no operative rule text has been carried into the spec (the semantic content still lives in D07/D08/D11/D12/D05/D10/D04), no execution-type classification exists, and the platform guarantees are named but not contracted.

A second, deduplicated implementation-readiness view is also required because several G-* gaps describe the same underlying engineering blocker at different abstraction levels. Section 7 records **18 unique implementation-readiness issues**: **5 Critical**, **11 High**, and **2 Medium/Low**. Critical means the implementation cannot faithfully encode A.1-E scientific meaning; High means initial coding may begin but reliable engineering, reproducibility, authoritative conformance, or integrated execution remains blocked; Medium/Low means a temporary substitute exists without changing the scientific architecture.

The G-* register remains the authoritative gap inventory by source/owner. The U-* register is a cross-cutting deduplicated engineering view and must not be added arithmetically to the G-* counts. Section 9 gives the decision procedure and the corrected path from adjudication through RECORDS/CLOSE, platform contracts, implementation, integration, validation and freeze. Part II binds every gap to the implementation chain (requirement → defect → change → owner → test → acceptance).

## 1. Decision gaps (must be signed by the owner; nothing else can close them)

| ID | Decision | Status | What is missing to decide it | Consequence if unsigned | Where it lands |
|---|---|---|---|---|---|
| G-D01 | M1 — governing status of D02, D03, D04, D05, D09, D10 | Memo drafted; unsigned | Choice among (a) audits+freeze, (b) drafts, (c) drafts + adoptions HD-21…HD-28 | Module 1 envelope/region/trigger rules (R-076/079/080), Module 7 independence (R-127), immutability (R-101), and the D03/D04/D05/D10 conformance suites have no normative status; `frozen-status` blocks freeze | HD-20 (+HD-21…28) |
| G-D02 | M2 — canonical identity in v1.0 | Memo drafted; unsigned | Choice in-scope / deferred; A3 facts already established (no v1 consumer; no identity gold) | Module 6, identity precondition, inter-gap links, `identity-gold` cannot be specified; RECORDS batch D12 cannot run | HD-29 |
| G-D03 | M3 — R-076/R-079/R-080 (MAX_COMPOUND, ineligible regions, trigger classes) | Conditional on M1 | A4 = CONTESTED_ONLY; needs M1(a) or HD-23/24/25 | Module 1 has no envelope bound, region rule or capture trigger — detection cannot be implemented deterministically | HD-30 |
| G-D04 | M4 — absent SM-1.3 / GS-1.3 | Memo drafted; unsigned | Search result for the two files; then re-author / consolidate without / defer | R-100 invariants, freeze prerequisites, lifecycle names, `rejected_illegal`, HUMAN_* transitions unavailable; HD-02 blocked | HD-31 |
| G-D05 | M5 — register status vocabulary | Memo drafted; unsigned | Normalise labels or add mapping | RECORDS cannot cite decision bases unambiguously | HD-32 |
| G-D06 | `positioning_context` input-contract amendment | HLA says "must be recorded"; not recorded | Amend D06 §9 input list; state producer, non-circularity, absence behaviour | Modules 2 and 5 have an input with no governing authority | new HD |
| G-D07 | `decision1-g5` — G5 as GAP-necessary vs positioning as role (HD-01 vs D07 §38.14) | DECISION_CONFLICT, open | Ruling on which module owns positioning function; treatment of REVIEW_FINDING (SD-02) under G5 | Module 2 cannot state its own GAP definition; Module 5 role assignment underdetermined | new HD or HD-01 amendment |
| G-D08 | `result-reported-gap` (G6), `agenda-positioning` (G1/DL-05), `we-lack-referent` (DL-03) | Open, SOURCE_SILENT/AMBIGUOUS | Adjudication under D01 with the probe cases | Boundary rules have no exit for three attested constructions → systematic UNCERTAIN or wrong class | new HDs (may fold into G-D07) |
| G-D09 | HD-10 — manuscript adoption, temporal currency, attribution-frame inclusion | UNRESOLVED (hole) | Author the rules (boundary semantics) and gold them; discriminating case absent (DL-02) | Attributed and historical deficiencies unclassifiable except by T2a fallback; identity outcome for embedded clauses undefined | new HDs; HD-19 remainder |
| G-D10 | HD-09 — segmentation interface / split ownership; `cardinality-authority` (G3/DL-04) | PARTIALLY RESOLVED | Formalize the layered chain (asset → Step-5 split → DP-CROSS-3 → extraction) and gold-vs-spec cardinality authority | Instance count is non-deterministic across layers; reason-clause loop and multi-proposition units have no reconciliation rule | new HD |
| G-D11 | `artifact-kind-method` (D06 six kinds vs GS/OR seven) | SOURCE_CONFLICT | Contract amendment adopting `method` or rejection | Module 4 `affected_object.artifact_kind` enum undefined | new HD |
| G-D12 | `normalization-grammar` (HD-12 remainder) | DECISION_REMAINDER | Author the grammar/templates for `A1E-EX-NORM-1.0` | Module 3 cannot produce `normalized_proposition` deterministically; identity P-EQ-1 and gold exact-string check impossible | new HD + spec artefact |
| G-D13 | `kb6-vocabulary` (KB-6 absent) | SOURCE_MISSING | Recover or re-author review-trigger, review-flag and reopening reason codes | UNCERTAIN trigger codes, review flags, reopening reasons have no closed vocabulary | new HD / artefact |
| G-D14 | HD-17 — owners of descriptor minting, corroborating role, diagnostic emission, object resolution | PARTIALLY RESOLVED | Assign owners within the recorded constraints | Evidence-role vocabulary and descriptor handling cannot be specified | new HD |
| G-D15 | HD-02 — lifecycle vocabulary (`boundary_passed`, `source_linked`) | UNRESOLVED (blocked by M4) | Alias table after SM-1.3 is read, or Contract reissue | Object-lifecycle interface names undefined | HD after G-D04 |

## 2. Interface / schema gaps (everything the HLA defers to RECORDS)

| ID | Module | Object / field | What must be specified | Derives from |
|---|---|---|---|---|
| G-S01 | Inputs | `structural_units`, `section_roles`, `source_span_registry` | Unit types, offsets, section-role enum incl. UNKNOWN, span-atom fields (doc id, version, section, paragraph, offsets, text) | D10 CD-INPUT-1/4, D09 D9/I-0, D13 §40.28 |
| G-S02 | Inputs | `positioning_context` | Objective/RQ object shape, spans, absence semantics | new (G-D06) |
| G-S03 | Inputs | `configuration`, run provenance record | Version-record schema (spec, SL, CD rules, KB, registry) | D09 gap_run, R-144 |
| G-S04 | 1 | `GapCandidate` | `detection_basis` (rule id + signal id), `context_span_refs` trigger class, lineage fields for reason-derived candidates, ordinal | D10 CD-CORE-3, CD-CONTEXT-1, CD-ORDER-1; R-068 |
| G-S05 | 2 | `BoundaryResult` + run-level boundary record | `rule_basis` (BR rule ids), `uncertainty{trigger, competing_classes}` vocabulary, diagnostics vocabulary, review-requirement type; BoundaryClassification must also emit/persist the candidate-level seven-class result into the run-level boundary record | D07 BR-UNC-3, §38.15; SD-04/05/06; KB-6 (G-D13); HLA run-record invariant |
| G-S06 | 3 | `GapOccurrenceDraft` | `affected_object` structure (object_kind, artifact_kind, mention, about, type traces), `evidence_refs` roles, `contrast_evidence` (status, entries, uncited referent), `citation_refs` stub, `explicitness` + `completion_support_refs` (dependency type), `preserved_context_refs`, `review_requirements` types, lineage | D09 §3/§4, D11 §41.4, D05 EX-CONTEXT/EX-CONTRAST/EX-CITE, D06 §8 traceability classes |
| G-S07 | 3 | `normalized_proposition` | Method id, grammar output, trace refs, unclassified restriction segments | D05 EX-NORM-1..3; G-D12 |
| G-S08 | Citation resolution | `citation_resolution_outcomes` | resolved/unresolved states, registry id, verbatim, confirmation status vocabulary | D09 citation_link, D03 RS-CITE, D04 VS-CITE-2 |
| G-S09 | Validation step | validation codes | Enum-closure, compatibility-matrix P/A-cell codes, structural invariant ids, re-derivation vs review routing | D08 §39.7, DP-PAIR-3; D09 invariants |
| G-S10 | 4 | `GapOccurrence` | Full field dictionary, traceability class per element, invariants (one primary span, context_support iff context_supported, no scope, no confidence) | D09 gap_record + I-* (R-100 pending M4) |
| G-S11 | 5 | `discourse_role`, `alignment_eligible` | Role assignment rule, evidence spans for role, eligibility derivation | HD-01, SD-01/02; G-D07 |
| G-S12 | 6 | `CanonicalGap`, links | identity_basis codes, representative selection record, `possibly_same_claim`/`related_claim`/`reason_of` link vocabularies and basis codes, cluster conflicts | D12 §42.28/§42.30/§42.44/§42.45, GI-REP-1 (only if M2 = in scope) |
| G-S13 | Identity precondition | closure record | What "closed" means for pending reviews; closure identity for invalidation | M4/lifecycle governance; D03 RS-EPOCH (contested) |
| G-S14 | 7 | `VerificationResult` | check families, basis codes, detail codes, fatal codes, review-requirement types, round identity | D04 §46.16–46.22 (contested; adoptable via HD-27) |
| G-S15 | 8 / run record | `GapResult`, `candidate_boundary_results`, `run_provenance` | Output contract to graph/alignment; persisted `A1ERunRecord` schema including closure/epoch identity, candidate boundary truth, invalidation history, pinned versions, and verification-round identity; if D04 VS-ROUND is not adopted under M1, round identity is re-authored as a platform contract rather than inherited from D04 | D06 §11; HLA run record; D04 VS-ROUND (contested) |
| G-S16 | Review interface | typed review requirement / resolution per class | Boundary, extraction, citation-confirmation, verification classes; permitted resolution semantics per class | R-143; D07 §38.15; D04 VS-REVIEW-3 |

### 2.1 RECORDS Section-1 module-interface template

Do **not** create a separate Module Interface Matrix artefact. The matrix is the RECORDS Section-1 output template itself, so every executable signature is bound to its governing requirement provenance and execution type.

For every executable stage where substitution is applicable, RECORDS must emit:

| Field | Required content |
|---|---|
| `operation_id` | Stable module / operation identifier |
| Typed inputs | Exact required and optional input object types |
| Typed outputs | Exact output object types; for `BoundaryClassification`, this includes both `BoundaryResult` and the run-level boundary-record emission |
| Review / failure outputs | Typed review requirement, refusal/failure semantics, and lawful empty-result behaviour where applicable |
| Governing provenance | R-* requirement ids, signed HD/SD decisions, operative rule ids, and source/spec version |
| Execution type | D / S / H / J for the retained rule or operation |
| Gold substitute type | Gold upstream object that may replace the runtime input in oracle/component evaluation |
| External guarantees consumed | Canonical text, segmentation, positioning context, Citation Registry, lifecycle, version registry, or other contracted provider guarantees |

The signature must be pure over its declared inputs: no hidden state from earlier stages may be required. Provider-side platform contracts in Section 5 define the guarantees; RECORDS defines the A.1-E consumer side. The two must co-evolve.

### 2.2 Engineering realization of typed interfaces

RECORDS remains the normative source. After CLOSE, the implementation must materialize each active RECORDS signature into **one canonical machine-readable interface representation** (for example JSON Schema or an equivalent typed IDL) and derive language-specific types such as Pydantic or TypeScript from it where useful.

Requirements:

- generated / mechanically derived implementation types must preserve the RECORDS field names, enums, cardinalities and invariants;
- independently handwritten duplicate schemas are prohibited where a generated representation exists;
- every generated artefact records the governing RECORDS/spec version and hash;
- CI must fail on schema/type drift between the canonical machine-readable interface artefact and generated language types;
- oracle-substitution fixtures must validate against the same canonical interface artefact used by runtime code.

This is the engineering realization of the RECORDS Section-1 interface template; it is **not a second normative specification**.

## 3. Normative-rule gaps (rule text not yet carried into the spec)

| ID | Module | Rule set that must be transcribed | Source | Status of source |
|---|---|---|---|---|
| G-R01 | 1 | Emission rules CD-EMIT-1..13, context capture CD-CONTEXT-1..4, dedup/overlap, ordering, exhaustiveness, diagnostics CD-DIAG | D10 | contested (M1); HD-13 supports determinism and registered basis |
| G-R02 | 1 | Signal registry (74 ids), priors, false friends, non-firing cases | D13 | uncontested, but a versioned asset outside the spec |
| G-R03 | 2 | G1–G7, class definitions, pairwise distinctions, UNCERTAIN triggers, mixed-unit rule, decision procedure D0–D6, precedence PR-0..10 | D07 | uncontested; G5 form subject to G-D07 |
| G-R04 | 3 | Relation/kind cards, decision rules, compatibility matrix, precedence DP-PREC-1..15, review conditions R1–R5 | D08 | uncontested |
| G-R05 | 3 | Object rules OR-* (target, scope exclusion, carrier, artifact, relationship, about, coreference, normalization whitelist) | D11 | uncontested; `method` kind per G-D11 |
| G-R06 | 3 | Assertion-span rule (HD-19), explicitness/context-support, contrast capture, citation stubs, persistence-reason handling, silent-fallback ban, review routing | HD-19, HD-15, HD-07, HD-08; D05 EX-* | D05 contested (M1); decisions cover the core |
| G-R07 | 3 | Attribution adoption, temporal currency, frame inclusion | none | G-D09 |
| G-R08 | 5 | Role assignment rules for FOCAL_STUDY_POSITIONING / REVIEW_FINDING / RESTATEMENT | HD-01, SD-01, SD-02 (principles only) | G-D07 must fix the operational test |
| G-R09 | 6 | SAME_GAP conjuncts, OE-1..6, P-EQ tiers, wrappers/anti-erasure, clustering, representative precedence, link routing, reason reconciliation | D12 | uncontested; active only under M2 in-scope |
| G-R10 | 7 | Check families, verdict aggregation, narrow fatal policy, freeze prerequisites, human re-entry | D04 (contested), D06 §2/§13, HD-14 | policy fixed by HD-14; codes via M1(c) HD-27 |
| G-R11 | cross-cutting | No-confidence, no-reconstruction, no structured Scope/Context owned by A.1-E, diagnostics-never-gaps, determinism, three truth layers, and PASS-and-not-invalidated-only downstream publication | D06 §2/§11/§16; D09 verified/freeze semantics; R-140/R-026/R-098/R-141 | uncontested |
| G-R12 | 3 → 2 loop / closure | Persistence-reason derived-candidate loop: deduplicate only by span identity (same span = same candidate; identical text at another span remains distinct); semantic duplicate handling is reserved to identity; a derived candidate is grounded in a reason span inside the parent unit and cannot re-derive from its own reason clause; loop completes when no new eligible span-grounded reason candidate exists, which is a closure precondition rather than an iteration cap | D10 CD-DEDUP-1/2; D08 DP-PREC-9; D12 GI-REASON-1; R-081/R-116 | core constraints supported; exact runtime representation via RECORDS |

## 4. Execution-type and implementation gaps

| ID | Gap | Why it blocks execution | Owner |
|---|---|---|---|
| G-E01 | No D/S/H/J classification per retained rule | Implementers cannot tell which steps are code and which are bounded LLM inference; RECORDS is the pass that assigns it | RECORDS |
| G-E02 | No Semantic Execution Contract for S/H steps | Every S/H operation must have closed-vocabulary/schema output; output must cite governing rule ids in `rule_basis`; abstention/review is allowed only through rulebook triggers (Boundary UNCERTAIN T1–T3 and DPR R1–R5), never model confidence; numeric confidence is prohibited; same pinned inputs must yield the same output or the same review route. Detection is excluded from S/H by HD-13. Without this contract an LLM step can silently decide scientific meaning | RECORDS + semantic-runtime contract + implementation spec |
| G-E03 | No prompt/rule-pack versioning for semantic steps | Reproducibility (R-141/R-146) unmeasurable | implementation spec + Version registry |
| G-E04 | No error/failure semantics for structural failures vs semantic blockers (refusal vs review) | D05 EX-INPUT-2 distinction lost; runs can silently drop | RECORDS |
| G-E05 | No run identity / idempotence contract | Re-execution paths assume deterministic replay. Re-author this as an Object-lifecycle platform guarantee unless M1 explicitly adopts the contested orchestration text: stable run/execution identity, fingerprint = declared inputs + all pinned versions, retry/resume semantics, and idempotent replay rules | Platform (Object lifecycle) |
| G-E06 | No reason-derived loop termination / fixpoint contract | Runtime can recursively emit candidates unless the structural bound is explicit: same-span candidates are not re-emitted; identical wording at another span remains distinct; a derived candidate is grounded in a reason span within the parent unit and cannot re-derive from its own reason clause; termination occurs when no new eligible span-grounded reason candidate exists, not by an iteration cap | RECORDS + runtime orchestration |
| G-E07 | No explicit implementation / integration phase after specification | RECORDS and CLOSE produce the governed specification, not executable software. The implementation specification must be derived only from the CLOSE-completed RECORDS output plus any Semantic Execution Contracts; a spec-adequacy probe must run before implementation; then code/rule packs, component tests, integration, lifecycle/re-entry tests, calibration and validation follow | Engineering + validation |

## 5. Platform-guarantee gaps (named, not contracted)

These contracts should be authored **in parallel with RECORDS**, because they define the provider side of the same interfaces that RECORDS defines on the A.1-E consumer side. Each provider contract must state: input, success output, explicit absent/unavailable output where applicable, version/provenance token, deterministic guarantee, and failure semantics. **A.1-E must never infer a missing platform output.** Two contracts may remain partially open while their interfaces are fixed: segmentation split ownership remains open under HD-09, and positioning-context absence behaviour remains governed by G-D06 / `decision1-g5`.

| ID | Service | Guarantee A.1-E needs, not yet written |
|---|---|---|
| G-P01 | Canonical text artifact | Hashed, versioned text; offset coordinate system; gold offsets recomputed against it (`canonical-text-artifact`; findings §2) |
| G-P02 | Segmentation asset | Deterministic, prediction-independent units; version pinned; provider interface can be contracted now, while the disagreement/split-ownership rule between clause and sentence layers remains explicitly open under HD-09 / G-D10 until decided |
| G-P03 | Positioning-context producer | Independence from Gap output; availability; explicit absent token when Objective/RQ is unavailable. The provider contract does not decide what A.1-E does on absence: that behaviour remains G-D06 / `decision1-g5` |
| G-P04 | Citation Registry | Deterministic pinned lookup API; version pin; unresolved semantics |
| G-P05 | Object lifecycle / Invalidation | Universe closure signal; invalidation on identity-relevant change; review routing; conditional immutability (M1); stable run/execution identity and idempotence guarantees re-authored as platform semantics unless M1 adopts the contested orchestration texts; execution fingerprint = declared inputs + all pinned versions |
| G-P06 | Human review / re-entry | Typed requirement and resolution transport per review class |
| G-P07 | Version / spec registry | Pinning and provenance record schema |
| G-P08 | Test / gold corpus | Oracle-regime harness (gold substitution per stage), metrics ownership |
| G-P09 | Persistent A.1-E run / audit store | Persist `A1ERunRecord`: run id, manuscript/version, closure/epoch identity, candidate-level seven-class BoundaryResults, review/adjudication rounds, invalidations, verification results, all pinned execution assets, and final state. Verification-round identity comes from D04 only if M1 adopts it; otherwise re-author it as this platform contract |
| G-P10 | Downstream publication gate | Publish only a Gap object with verification `PASS` **and not invalidated**. If identity is enabled, the publication unit is the CanonicalGap; no occurrence publishes while its canonical Gap is `REVIEW_REQUIRED` or otherwise not PASS. The run-level boundary record never publishes to the Research Graph / Alignment feed |

## 6. Validation gaps (cannot claim validity without these)

| ID | Gap | Evidence | Needed |
|---|---|---|---|
| G-V01 | Gold Set v0.1 is single-annotator, six positives, two negatives, recall unmeasured | findings §3; D01 29.6-D requires double annotation | Independent second annotator; sealed cohorts; negatives for BR-CROSS-14 (`br-cross-14-coverage`) |
| G-V02 | MATCH_CRITERION, IAA floors, thresholds all `TBD_BY_FINAL_CALIBRATION` | D01 29.10 | Final calibration phase after G-D07…G-D10 close |
| G-V03 | No identity gold | A3 | Required if M2 = in scope (`identity-gold`) |
| G-V04 | Conformance suites of D03/D04/D05/D10 have no normative status | M1 | HD-26/27/28 or M1(a) |
| G-V05 | Gold offsets not tied to a canonical artifact | findings §2 | G-P01 |
| G-V06 | Discriminating cases for HD-10 absent (DL-02) | findings §4 | Construct with independent annotation |

## 7. Deduplicated implementation-readiness issues

The U-* register below consolidates overlapping specification and engineering gaps into unique implementation-readiness issues. It is a **cross-cutting view** over the G-* register, not an additional independent gap count.

### 7.1 Critical

These are critical because without them the implementation cannot faithfully encode A.1-E scientific meaning. Repository scaffolding can still be written, but not a trustworthy scientific capability.

| ID | Unique issue | Why it is unique | Why Critical |
|---|---|---|---|
| **U-01** | **Governing operative rules are not consolidated into the executable specification** | Different from schemas: this defines **what the system means and decides**, not what data looks like. G-R01–R12 currently identify rule sets and source locations rather than carrying the complete operative rule text into the governing executable specification. | Agents would otherwise have to reread source documents and reconstruct scientific semantics themselves, creating the silent-invention failure mode the architecture is designed to prevent. |
| **U-02** | **No D/S/H/J execution classification** | Different from rule content: even with a complete rule, implementation still needs to know **how the rule is executed**—deterministic code, bounded semantic inference, hybrid execution, or human judgment. | Engineering cannot determine which operations become pure code, constrained model calls, ordered hybrid operations, or human review. |
| **U-03** | **No executable typed module-interface source of truth** | Consolidates the G-S01–S16 prose-schema gap and the missing code-level interface artefact into one issue: the architecture does not yet provide machine-executable module contracts. | Modules cannot be independently implemented, composed, validated, or oracle-substituted reliably until RECORDS signatures are materialized into one canonical machine-readable interface representation. |
| **U-04** | **No Semantic Execution Contract for S/H operations** | Different from D/S/H/J: classification says **which** steps are semantic; this specifies **how semantic steps are constrained at runtime**. It includes closed outputs, `rule_basis`, lawful abstention/review, no confidence-based improvisation, failure behaviour, and model/prompt/rule-pack provenance. | Any unconstrained LLM-owned step can introduce scientific meaning absent from the governing specification. This issue becomes N/A only if no S/H operation survives classification. |
| **U-05** | **No canonical source-text and span-coordinate contract** | Different from fixtures: this is a **runtime evidence contract**, not merely test data. It defines the exact manuscript artefact and coordinate system against which every span is grounded. | A source-grounded extraction capability cannot reliably operate if the same span cannot always resolve to the same canonical text. |

### 7.2 High

These issues do not necessarily prevent initial module coding, but they prevent reliable engineering, reproducibility, authoritative conformance, or integrated execution.

| ID | Unique issue | Why it is unique | Why High |
|---|---|---|---|
| **U-06** | **Validation gold and conformance authority are inadequate** | Different from the fixture harness: fixtures test software; gold and suite authority establish whether scientific behaviour is correct. | Implementation may begin provisionally, but neither freeze nor a defensible validity claim is possible until gold quality and conformance-suite authority are resolved. |
| **U-07** | **No engineering work-package decomposition** | Defines **what gets built, where, by whom, and in what dependency order**; it does not define scientific behaviour. | The 18-step path is programme governance, not an executable engineering backlog suitable for coding agents. |
| **U-08** | **No package-level Definition of Done** | Different from decomposition: decomposition says what work exists; DoD says **when a package is complete**. | Autonomous coding/review loops require deterministic stopping and acceptance conditions. |
| **U-09** | **No fixture corpus and oracle-substitution harness** | Different from the canonical source contract and scientific gold. This is engineering infrastructure for feeding valid typed inputs directly into individual modules. | Without it, downstream modules cannot be tested independently of upstream failures. |
| **U-10** | **No explicit rule-pack representation and versioning policy** | Different from rule semantics: rules may be scientifically fixed while their executable representation—code, tables, schemas, prompt/rule packs—remains undefined. | Uncontrolled representation creates rule drift, unnecessary code rewrites, and unreproducible behaviour. |
| **U-11** | **No complete semantic-call reproducibility mechanism** | Concrete runtime realization of part of U-04: provider/model/version, inference parameters, prompt hash, rule-pack hash, schema version, and per-call provenance. | Even a correctly constrained semantic operation cannot be reproduced or audited without the full invocation envelope. |
| **U-12** | **No rule → implementation → test traceability** | Different from provenance inside RECORDS: this links the governing scientific rule to actual implementation artefacts and executable tests. | A rule can otherwise exist in the specification yet be omitted, altered, or left untested in the implementation without detection. |
| **U-13** | **No typed runtime error/outcome taxonomy** | Different from scientific statuses such as `UNCERTAIN` or `REVIEW_REQUIRED`. It distinguishes execution failure, invalid input, infrastructure failure, lawful empty result, review routing, and scientific rejection. | Without it, implementation failures can be mistaken for scientific outcomes or silently dropped. |
| **U-14** | **No concrete persistence implementation for `A1ERunRecord` and versioned artefacts** | The architecture already specifies **what** must be persisted; this issue is **how persistence actually works**. | Audit, recovery, invalidation history, replay, and reproducibility require durable storage semantics before integrated execution. |
| **U-15** | **No CI enforcement of architectural invariants** | Different from traceability: traceability states the relationships; CI continuously **enforces** schemas, spans, enums, forbidden fields, hashes, and tests. | Without automated enforcement, implementation can drift from the governed specification immediately after review. |
| **U-16** | **No governed coding-agent review loop** | Different from an agent guardrail file: this controls iterative development cycles—inputs, hashes, findings, fixes/rejections, tests, and termination states. | In an agent-based implementation workflow, uncontrolled review cycles can accept unsupported changes or lose evidence of why a change was accepted. |

### 7.3 Medium / Low

These can be temporarily substituted without changing the scientific architecture itself. They remain required where the corresponding engineering workflow depends on them.

| ID | Unique issue | Why it is unique | Why Medium / Low |
|---|---|---|---|
| **U-17** | **No repository-level coding-agent guardrail file** | Different from the review-loop protocol: guardrails govern **what an agent may do during a coding task**; the review protocol governs the lifecycle across tasks/cycles. | **Medium.** RECORDS remains authoritative, so manual development can proceed without this file; agentic coding is materially safer with an explicit rule that spec silence means stop and emit a finding rather than inventing semantics. |
| **U-18** | **No provider test-double / stub policy** | Different from provider contracts: contracts define real semantics; stubs provide temporary implementations for testing those contracts. | **Medium.** Stable real providers may be used where available, so stubs are not intrinsically required. They become important when platform dependencies lag module development. |

### 7.4 Engineering artefacts required to close U-07…U-18

The implementation specification must produce, as applicable (bound to change records CHG-* in Part II §II.5):

- an engineering work-package map: `operation/module → repo/package path → dependencies → tasks → owner → acceptance tests`;
- executable Definition of Done per package;
- a canonical machine-readable interface artefact derived from RECORDS, with generated language types and CI drift checks;
- module-level fixtures plus at least one pinned end-to-end canonical manuscript fixture;
- an oracle-substitution runner at every applicable typed boundary;
- a rule-pack representation policy chosen per rule family after D/S/H/J classification, with stable rule IDs, version/hash, provenance, loader/validation rules and deterministic ordering;
- a semantic invocation envelope recording provider/model/version where available, all relevant inference parameters, prompt/system/rule-pack hashes, schema version and call provenance; no universal assumption that `temperature=0` guarantees determinism;
- rule → implementation → test traceability, with CI failing on active rules that lack required implementation or tests;
- a typed runtime outcome taxonomy before language-specific exception/result mappings are chosen;
- a concrete MVP persistence choice for `A1ERunRecord` and immutable/versioned artefacts, including identifier, serialization, atomic write/update and recovery guarantees;
- mandatory CI gates for schema/type drift, enum closure, canonical span integrity, prohibited fields, fixture hashes, deterministic validators, serialization round trips, traceability coverage and invariant suites;
- a version-pinned coding-agent review protocol with machine-readable stop states, exact target/input/output hashes, raw agent output, test evidence, and explicit fix-or-reject-with-evidence handling;
- a repository-level agent guardrail file derived from RECORDS/CLOSE and explicitly subordinate to it;
- deterministic, contract-valid test doubles only for providers that are unavailable or unsuitable for component tests.

None of these artefacts may become an independent source of scientific meaning. **RECORDS/CLOSE remains normative; implementation artefacts are derived and traceable.**


## 8. Coverage summary

| Category | Count | Blocks build | Blocks freeze | Blocks validity claim |
|---|---|---|---|---|
| Decisions | 15 | G-D01, D02, D03, D06, D07, D09, D10, D11, D12 | all | G-D07, D08, D09, D10 |
| Interface/schema | 16 | all executable-module signatures | all | schemas needed for scored interfaces |
| Normative rules | 12 | all active rule sets | all | active scientific rules must be fixed before validity claims |
| Execution-type / implementation | 7 | G-E01, E02, E04, E05, E06, E07 | G-E01, E03, E05, E06 | G-E02, E03 plus implementation/conformance evidence |
| Platform guarantees | 10 | G-P01…P07, P09, P10 | G-P05, P07, P09, P10 | G-P01, P08, P09 |
| Validation | 6 | — | G-V02 | all |

The U-* register is **not additive** to the G-* category counts above. It deduplicates overlapping blockers into an engineering-readiness lens:

| U-* severity | Count | Gate represented |
|---|---:|---|
| Critical | 5 | faithful encoding of scientific meaning |
| High | 11 | reliable engineering, reproducibility, conformance, integrated execution |
| Medium / Low | 2 | workflow hardening where temporary substitutes exist |

## 9. How to make the decisions

### 9.1 Procedure per decision
1. **Frame** the question exactly as its memo or blocker states it; do not widen scope.
2. **Gating facts first**: use only established facts (A-verdicts, source clauses, recorded decisions). Where a fact is missing (e.g. whether SM-1.3 exists), obtain it before deciding — several items are conditional, not judgmental.
3. **Options are fixed**: choose only among the options listed in the memo/blocker; adding an option requires a new memo.
4. **Test against the sources**: a chosen option must not contradict an uncontested frozen rule unless the decision explicitly supersedes it and says so.
5. **Record** as `HD-nn — Status: DECIDED — Scope — Text`, including any remainder as `DECIDED (partial: <remainder>)`. Drafts in the adjudication memos are ready to sign.
6. **Apply** via `PASS: APPLY` with `<signed_decisions>`; the ledger deltas are predefined, so no re-analysis is needed.
7. **Gold before rule**: for decisions that author new semantics (G-D07, G-D08, G-D09, G-D10), annotate the discriminating cases independently first; the decision cites the adjudication outcome.

### 9.2 Sequence (critical path)

The critical path must respect three dependencies introduced by the HLA: **M4 before or alongside M1**, **M2 before typed signatures / loop-run-publication semantics**, and **G-D06 before the BoundaryClassification signature**. Platform provider contracts and RECORDS consumer contracts then co-evolve.

| Order | Decision / phase | Why here | Unblocks |
|---|---|---|---|
| 1 | G-D04 (M4) — search for SM-1.3/GS-1.3, **before or alongside M1** | Cheap factual step; M1(a) cannot finish the D02 audit without it; R-100 invariants feed the `GapOccurrence` signature | G-D01 path (a), G-D15, parts of G-S10 |
| 2 | G-D01 (M1) | Determines normative status of contested orchestration/spec texts and whether their suites/rules may be adopted | G-D03 disposition, Module 1 rules, Module 7 independence, G-V04 |
| 3 | G-D03 (M3) — R-076/R-079/R-080 | Detection cannot be implemented or its gold denominator sealed without the envelope constants. Under M1(a) or explicit adoption, freeze them; under M1(b) without adoption, park them as **provisional configuration while retaining the ledger's UNRESOLVED status** | Module 1 implementation envelope and candidate-denominator stability |
| 4 | G-D02 (M2) | Must precede typed signatures and loop/run/publication semantics because identity changes `CanonicalGap`, closure, publication unit, run record and identity gold | G-S12, G-S13, G-R09, G-V03, identity-dependent provider contracts |
| 5 | G-D06 — `positioning_context` input-contract amendment | Must precede the `BoundaryClassification` signature because it is a declared input. Contract producer, non-circularity and an explicit absent token here; do **not** decide A.1-E absence behaviour in the provider contract | G-S02 and the Module 2/5 interface signature |
| 6 | G-D07 + G-D08 — positioning/G5 and attested boundary constructions | Fix scientific use of the positioning input. G-D07 may remain an explicit unresolved parameter while the interface is drafted, but it must close before the operative boundary/role rules are frozen | G-R03, G-R08, G-S11 |
| 7 | G-D10 — segmentation / cardinality authority | Stabilizes proposition instances and candidate counts before gold is sealed. Provider interface may already exist; split ownership remains open until this decision | G-S04, G-S06, G-P02 completion, G-V02 |
| 8 | G-D09 — adoption / temporal currency / attribution-frame semantics | Requires authored rules and discriminating gold | G-R07 |
| 9 | G-D11, G-D12, G-D13, G-D14, G-D15 + G-D05 | Close remaining vocabulary, normalization, ownership, lifecycle-name and decision-status ambiguities needed by signatures/rules | G-S06…S10, S14, RECORDS citations |
| 10 | **Platform provider contracts (G-P*) + RECORDS Section-1 interface template in parallel** | Provider side and A.1-E consumer side define one boundary and must co-evolve. Segmentation may retain the HD-09 open point; positioning contract depends on G-D06 | G-S* executable signatures; G-E05; G-P01…P10 |
| 11 | RECORDS rule/schema batches (D06, D07, D08, D11, D13, D01, D09, D10, D05, D04, D12 as active) | Carry operative rule text, bind every module signature to R-* provenance, assign D/S/H/J, close schemas, and encode G-R12 reason-loop closure | G-S*, G-R*, G-E01, G-E04, G-E06 |
| 12 | CLOSE + Semantic Execution Contracts for every surviving S/H operation | Reconcile the governing spec, then constrain semantic execution: closed output, `rule_basis`, rulebook-only abstention/review, no numeric confidence, and same input → same output or same review route | G-E02/G-E03; implementation specification |
| 13 | **Pre-implementation spec-adequacy probe** | Use the findings' spec-adequacy probe model to test whether an implementer can execute the CLOSE-completed RECORDS spec without inventing semantics or hidden inputs | GO/NO-GO for implementation |
| 14 | **Implementation specification + engineering package plan** | Must be derived only from the CLOSE-completed RECORDS output and the Semantic Execution Contracts; implementation convenience cannot add scientific semantics. Produce U-07/U-08 work packages + DoD, U-10 rule-pack representation policy, U-11 semantic invocation envelope, U-13 runtime outcome taxonomy, U-14 persistence decision, U-17 agent guardrails, U-18 test-double policy, and the dependency/build graph | Engineering work packages and executable acceptance criteria |
| 15 | **Machine-readable interfaces + fixtures/harness + code + component conformance + CI** | Materialize U-03 from RECORDS into one canonical machine-readable interface artefact; generate language types; build U-09 module/end-to-end fixtures and oracle-substitution harness; implement deterministic validators / semantic rule packs; establish U-12 rule→implementation→test traceability and U-15 CI gates | Independently testable, traceable component implementation |
| 16 | **Governed agent implementation loop + integration + lifecycle/re-entry tests** | Apply the U-16 version-pinned coding-agent review protocol during implementation/integration; test run identity/idempotence, reason-loop termination, human review, citation confirmation, invalidation, persistence/recovery, identity recomputation, provider substitutes where used, and PASS-only publication | Runtime readiness with auditable engineering evidence |
| 17 | Calibration and validation (G-V*) | Calibrate only after scientific rules, denominators, platform artifacts and executable behaviour are stable | Validity claim |
| 18 | Final freeze / release evidence | Pin hashes, versions, conformance/validation results and unresolved-but-explicitly-parked items; no execution-ready claim before these gates pass | Executable frozen release |

### 9.3 Decision criteria to apply (from the materials, not new)
- Prefer the option that keeps uncontested frozen rules intact and requires no reconstruction of absent sources.
- Prefer the option that leaves module topology unchanged (all M1–M5 options do; only rule content varies).
- Where two documents conflict and neither supersedes, the decision must name which text becomes operative and mark the other as provenance.
- A rule that cannot be validated with available gold may be decided but must carry a `VALIDATION_GAP` until gold exists; it must not be frozen as validated.
- Never resolve a scientific question by choosing the more convenient implementation.
- Engineering artefacts (generated schemas, rule packs, prompts, agent guardrails, stubs, persistence formats, tests) must remain derived from and subordinate to the governing RECORDS/CLOSE specification; they cannot create new scientific semantics.

# PART II — IMPLEMENTATION PLAN

Part II binds every active requirement in Part I into the chain REQUIREMENT / FINDING → CURRENT DEFECT → EXACT CHANGE → OWNER / ARTIFACT → TEST → ACCEPTANCE CRITERION. It adds no scientific semantics. Where a fact is not in the supplied material it is typed as unresolved (`NOT YET AVAILABLE`, `DECISION_REQUIRED — G-Dxx`, `REPOSITORY_INSPECTION_REQUIRED`, `NOT APPLICABLE`).

## II.1 GOVERNING BASIS

| Item | Value |
|---|---|
| Protocol | A.1-E Annotation & Validation Protocol v1.2 (D01, `A1E_annotation_validation_protocol_v1-2.md`); hash: NOT YET AVAILABLE — must be pinned before implementation begins |
| Governing specification | A.1-E Minimal Governing Spec v1.0 — not yet drafted; the operative content still resides in D01–D13 plus signed decisions; name/version/hash: NOT YET AVAILABLE — must be pinned before implementation begins |
| Source specifications | D01–D13 (file names as listed in the Register §1); hashes: NOT YET AVAILABLE — must be pinned before implementation begins |
| RECORDS | not yet run; version/hash: NOT YET AVAILABLE — must be pinned before implementation begins |
| CLOSE | not yet run; version/hash: NOT YET AVAILABLE — must be pinned before implementation begins |
| Triage ledger / adjudication-prep | TRIAGE (146 lines), TRIAGE-REVISE, ADJUDICATION-PREP (memos M1–M5) exist as conversation artefacts; hashes: NOT YET AVAILABLE |
| R-* included | the 113 `S1` requirements of the reconciled ledger: R-001–R-006, R-008–R-021, R-023–R-069, R-071–R-081, R-083, R-084, R-089, R-093, R-094, R-098, R-100–R-111, R-123, R-126–R-128, R-130, R-133–R-138, R-140–R-145. `APP` requirements (R-007, R-022, R-070, R-082, R-085–R-088, R-090–R-092, R-095–R-097, R-099, R-112–R-122, R-124, R-125, R-129, R-131, R-132, R-139, R-146) enter only as platform-contract sources (Section 2 mechanisms), never as A.1-E rules |
| G-* repaired by this plan | G-S01–G-S16, G-R01–G-R12, G-E01–G-E07, G-P01–G-P10 (A.1-E consumer side), G-V04/G-V05 (prerequisite artefacts). G-V01/V02/V03/V06 are validation prerequisites, not repaired by implementation. G-D01–G-D15 are outside implementation authority |
| U-* repaired | U-01…U-18 (U-01/U-02 through RECORDS; U-04/U-11 through Semantic Execution Contracts; U-03/U-05–U-10, U-12–U-18 through implementation artefacts) |
| Finding IDs | `<findings>` carries no finding IDs; items are referenced by its section numbers (§1–§6) and decision-log items DL-02…DL-06. NOT YET AVAILABLE — findings must be assigned IDs before they can be cited as repaired |
| Signed decisions governing implementation | HD-01 (function-only GAP; roles), HD-19 (assertion span; remainder: attribution frame), HD-03, HD-04, HD-05, HD-06, HD-07, HD-08, HD-11, HD-12 (partial), HD-13, HD-14, HD-15, HD-16 (partial), HD-18 (partial), SD-01…SD-12. Status normalisation of these labels is itself G-D05 |
| Unresolved decisions outside implementation authority | G-D01–G-D15 (M1–M5 drafts HD-20…HD-32 unsigned; G-D06–G-D15 without drafts) and the blocker slugs decision1-g5, result-reported-gap, agenda-positioning, we-lack-referent, cardinality-authority, manuscript-adoption, attribution-frame, temporal-currency, artifact-kind-method, normalization-grammar, identity-scope, source-missing-sm13-gs13, frozen-status, segmentation-interface, lifecycle-vocabulary, unowned-operations, kb6-vocabulary, canonical-text-artifact, g5-focus-transfer, br-cross-14-coverage, hd10-discriminating-case, gold-independence, identity-gold |

Authority order (lower layers cannot override higher layers):

signed human decisions (HD-*/SD-*) → frozen RECORDS/CLOSE → Semantic Execution Contracts → implementation specification → generated implementation artefacts (interface artefact, rule packs, prompts, fixtures) → code/tests.

## II.2 OBJECTIVE

Capability implemented: A.1-E Gap extraction as decomposed in the HLA — candidate detection, boundary classification, assertion/deficiency extraction with the reason-derived loop, deterministic citation resolution, deterministic occurrence validation, occurrence representation, occurrence role, conditional identity/resolution, verification, verified output, run record, review/re-entry, invalidation/re-execution, publication gate.

Defects closed by this plan: G-S01–G-S16 (materialised as one machine-readable interface artefact), G-R01–G-R12 (rule packs bound to RECORDS text), G-E01–G-E07, G-P01–G-P10 consumer adapters, G-V04/G-V05 prerequisites; U-01–U-18 as listed in II.1.

Deferred (not closed here): G-D01–G-D15 and all listed blockers; A.1-C characterization; Scope/Context typing; identity when M2 = deferred; wider-literature support validation; scientific validation claims (Phase K).

Successful completion means, operationally: every active rule has an executable owner; every executable stage has a machine-readable typed interface derived from RECORDS; every S/H stage has a Semantic Execution Contract; every retained rule is traceable to implementation and tests; all required provider contracts are consumable; the runtime outcome taxonomy, run-record persistence, review/re-entry, invalidation/re-execution and PASS-and-not-invalidated publication pass integration tests; required conformance tests and CI gates pass; no unresolved scientific choice has been silently encoded (every open G-D is represented by a typed unresolved outcome, never a default).

## II.3 SCOPE

### II.3.A IN SCOPE
- Modules 1–8 of the HLA plus the deterministic citation-resolution and occurrence-validation steps, the reason-loop controller, review transport, invalidation/re-execution, run record, publication gate.
- Schemas/interfaces: one canonical machine-readable interface artefact per RECORDS signature (Part I §2.1/§2.2) with generated language types.
- Platform contracts (consumer side): G-P01–G-P10.
- Rule packs: G-R01–G-R12 in the representation chosen under U-10.
- Tests: conformance (II.7), oracle-substitution harness, integration/re-entry/invalidation tests, CI gates.
- Persistence: `A1ERunRecord` and immutable versioned artefacts (U-14, G-P09).
- CI: U-15 gates. Agent-review workflow: U-16/U-17. Fixtures: U-09.

### II.3.B OUT OF SCOPE
- Unrelated refactoring; downstream Research Graph redesign; A.1-C characterization; wider-literature truth validation (SD-12; A.1-A); new scientific rules not present in RECORDS/CLOSE; resolution of any G-D decision; platform redesign beyond the guarantees in G-P01–G-P10; structured Scope/Context objects (external capability, HLA "optional downstream context enrichment").

### II.3.C DEPENDENCIES AFFECTED
| Dependency | Direction | Contract |
|---|---|---|
| Canonical text / span registry | upstream | G-P01 |
| Segmentation asset | upstream | G-P02 (split ownership open, G-D10) |
| Positioning-context producer | upstream | G-P03 (absence behaviour open, G-D06/G-D07) |
| Citation Registry | upstream | G-P04 |
| Version / spec registry | cross-cutting | G-P07 |
| Object lifecycle / invalidation | cross-cutting | G-P05 |
| Human review / re-entry transport | cross-cutting | G-P06 |
| Test / gold infrastructure | cross-cutting | G-P08 |
| Run / audit store | cross-cutting | G-P09 |
| Research Graph / Alignment Engine | downstream | G-P10 (PASS-and-not-invalidated only) |
| Scope/Context capability | downstream, optional | consumes `preserved_context_refs` only |

Files / repository components: REPOSITORY_INSPECTION_REQUIRED — `<findings>` §6 states "No A.1-E code exists"; no repository was supplied with this task. Package-level planning cannot name files until inspection confirms the repository layout (or its absence).

## II.4 REQUIREMENT → IMPLEMENTATION MAPPING

Legend: Current implementation = `NONE` per `<findings>` §6 unless repository inspection shows otherwise (`UNKNOWN_PENDING_REPOSITORY_INSPECTION`). Execution type = proposed; normative only at RECORDS. Owner = logical component; repository path REPOSITORY_INSPECTION_REQUIRED for every row.

| Requirement / finding | Normative requirement | Current status | Current implementation | Required implementation delta | Owning component / artefact | Execution type | Dependencies | Test reference | Acceptance criterion |
|---|---|---|---|---|---|---|---|---|---|
| G-R01 / R-076–R-084 / HD-13 | Deterministic registered-basis candidate emission; envelope; region rules; triggers; dedup by span; ordering; exhaustive evaluation | DECISION_REQUIRED (G-D01, G-D03) | NONE | Detection rule pack + engine (CHG-08); constants as pinned config with UNRESOLVED marker until G-D03 | Candidate detection engine | D | CHG-01, CHG-02, CHG-07, CHG-24 | T-05, T-06, T-15, T-22 | Every candidate cites rule id + signal id; identical run → identical candidate set; no LLM in path |
| G-R02 / R-069–R-075 | Signal library as versioned asset; signal ≠ verdict; priors never determinative | MISSING | NONE | Asset loader + integrity check (CHG-07) | Signal library asset + loader | D | CHG-05 | T-05, T-22 | Loader rejects unpinned or mutated asset; priors cannot veto |
| G-R03 / R-009–R-026 | Seven-class boundary truth; G1–G7; UNCERTAIN triggers; D0–D6; PR-0..10; no section gate | DECISION_REQUIRED (G-D07, G-D08, G-D09) for three exits; rest MISSING | NONE | Boundary rule pack + engine with explicit `UNRESOLVED → review` exits for G-D07/08/09 (CHG-09) | Boundary classification engine | H (S bounded by D0–D6, PR-*) | CHG-03, CHG-24, CHG-25 | T-07, T-08, T-11, T-23–T-27 | Every result carries rule_basis; UNCERTAIN carries trigger + ≥2 competing classes; open exits never yield a class |
| G-S05 / R-009 (Item 2) / SD-04 | Run-level seven-class record for every candidate | MISSING | NONE | Emit/persist candidate BoundaryResult (CHG-10) | Boundary record emitter → run store | D | CHG-23 | T-11 | 100% of evaluated candidates present with class, diagnostics, provenance |
| G-R04 / R-030–R-043 | Relation/kind assignment; weakest reading; matrix as validator; R1–R5 review | MISSING | NONE | DPR rule pack in extraction engine (CHG-11) + matrix in validator (CHG-14) | Extraction engine; validator | H → D | CHG-24, CHG-25 | T-02, T-09, T-23–T-27 | No pair outside the closed enums; P-cell never emitted; A-cell only with traced licensing |
| G-R05 / R-044–R-057 | Object rules OR-*; no scope in object; coreference branches; normalization whitelist | CONFLICT (G-D11 artifact_kind) / MISSING | NONE | OR rule pack in extraction engine (CHG-11); `method` behind G-D11 flag | Extraction engine | H | CHG-24, CHG-25 | T-03, T-09, T-23–T-27 | Object never contains scope tokens per OR-SCOPE tests; unresolved antecedent → review, never nearest noun |
| G-R06 / R-023, R-024, R-027, R-059–R-068, R-089 / HD-19, HD-15, HD-07, HD-08 | Minimal assertion span; explicitness/context support within envelope; contrast; citation stubs; reasons; silent-fallback ban | DECISION_REQUIRED (attribution-frame remainder); rest MISSING | NONE | Extraction engine (CHG-11); frame inclusion routed to review until HD-19 remainder closes | Extraction engine | H | CHG-24, CHG-25 | T-01, T-09, T-12, T-23–T-27 | Assertion span reconstructs proposition; no completion outside envelope; every ban-list coercion absent |
| G-R07 / R-028, R-029 | Attribution adoption; temporal currency; frame inclusion | DECISION_REQUIRED (G-D09) | NONE | Typed `UNRESOLVED_RULE` review exit in boundary/extraction engines (CHG-09, CHG-11) | Boundary/extraction engines | J (until rule authored) | G-D09 | T-08 | Attributed/historical constructions never receive a class or span decision by default |
| G-R08 / R-145 / HD-01, SD-01, SD-02 | Occurrence-level discourse role; alignment eligibility; RESTATEMENT ≠ SAME_GAP | DECISION_REQUIRED (G-D07 operational test) | NONE | Role assignment module with positioning-context input (CHG-16) | Occurrence role module | H | CHG-03 | T-10, T-17 | Role never written to CanonicalGap; eligibility = f(role) only |
| G-R09 / R-102–R-111, R-094, R-008 / HD-05 | SAME_GAP conjuncts; conservative default; contextual variants; clustering; representative; links | DECISION_REQUIRED (G-D02) | NONE | Identity module behind M2 switch (CHG-17) | Identity/resolution module | H (S equivalence bounded by OE/P-EQ registries → D clustering) | CHG-22, G-D02 | T-17, T-18, T-23–T-27 | Off when deferred; when on: no merge without established equivalence; payload from one representative |
| G-R10 / R-126–R-130, R-067 / HD-14 | Extraction-only verification; three verdicts; narrow REJECT; unresolved citation → review; no repair | DECISION_REQUIRED for R-127/R-101 (G-D01); rest MISSING | NONE | Verification engine (CHG-18); independence guarantee flagged CONDITIONAL | Verification engine | H → D (aggregation D) | CHG-13, CHG-21 | T-12, T-13, T-14, T-19 | REJECT only on the three fatal conditions; PASS blocked while unresolved citations unconfirmed |
| G-R11 / R-140, R-026, R-098, R-141, R-003, R-058 | No confidence; no reconstruction; no structured scope; diagnostics never gaps; determinism; traceability classes | MISSING | NONE | Enforced in validator (CHG-14), interface artefact (CHG-06), CI (CHG-26) | Validator; CI | D | CHG-06 | T-02, T-03, T-04, T-20, T-21 | Forbidden fields rejected at schema and CI level; diagnostics cannot alter class |
| G-R12 / G-E06 / R-068, R-081, R-116 | Reason-loop: span-identity dedup; derived candidate grounded in parent reason span; structural termination; closure precondition | MISSING | NONE | Loop controller (CHG-12) | Reason-loop controller | D | CHG-08, CHG-09, CHG-11 | T-06, T-15, T-16 | Same-span candidate never re-emitted; loop ends when no new span-grounded reason candidate exists |
| G-S01 / R-060, R-144 | Span atoms; units; section roles | MISSING | NONE | Interface artefact + adapters (CHG-01, CHG-02, CHG-06) | Interface artefact; input adapters | D | G-P01, G-P02 | T-01, T-20 | Every span resolves byte-identically to canonical text |
| G-S02 / G-D06 | Positioning-context object with explicit absent token | DECISION_REQUIRED (G-D06) | NONE | Adapter with `ABSENT` token; no inference (CHG-03) | Positioning-context adapter | D | G-P03 | T-19 | Absence surfaces as typed absent, never as empty objective list treated as evidence |
| G-S03 / R-144, R-146 | Version/provenance record | MISSING | NONE | Pinning and provenance record (CHG-05) | Config/provenance component | D | G-P07 | T-22 | Run cannot start without all pinned versions; record serialised in run record |
| G-S04 | GapCandidate with basis, trigger class, lineage, ordinal | MISSING | NONE | Interface artefact (CHG-06); engine (CHG-08) | Interface artefact | N/A | — | T-20 | Schema validates; drift CI passes |
| G-S06, G-S07, G-S10 / R-023, R-044, R-058–R-065 | Draft/occurrence field dictionaries; normalized proposition slot | DECISION_REQUIRED (G-D11, G-D12, G-D14) for three fields; rest MISSING | NONE | Interface artefact (CHG-06); representation (CHG-15) | Interface artefact; occurrence builder | N/A / D | RECORDS | T-20, T-03, T-04 | Fields governed by open decisions typed as optional-with-UNRESOLVED marker, never defaulted |
| G-S08 / R-066 | Citation resolution outcomes | MISSING | NONE | CHG-13 | Citation resolution step | D | G-P04 | T-12, T-13 | Every citation_ref has exactly one outcome; unresolved keeps verbatim |
| G-S09 / R-037 | Validation codes | MISSING | NONE | CHG-14 | Validator | D | RECORDS | T-02 | P-cell → return to owning rule or review; never substitution |
| G-S11 | Role fields | DECISION_REQUIRED (G-D07) | NONE | CHG-16 | Role module | N/A | — | T-10 | as G-R08 |
| G-S12, G-S13 / G-D02 | CanonicalGap, links, closure record | DECISION_REQUIRED | NONE | CHG-17, CHG-22 | Identity module; lifecycle adapter | N/A | G-D02, G-P05 | T-16, T-17, T-18 | Present only when identity enabled |
| G-S14 / HD-14 | VerificationResult codes | DECISION_REQUIRED for code registry (G-D01 / HD-27) | NONE | CHG-18 | Verification engine | N/A | — | T-13, T-14 | Three statuses only; codes closed |
| G-S15 / G-P09 | GapResult; A1ERunRecord | MISSING | NONE | CHG-23, CHG-19 | Run store; output contract | D | G-P09 | T-11, T-16, T-19 | Record round-trips; contains boundary truth, invalidations, versions |
| G-S16 / R-143, R-017, R-067 | Typed review requirement/resolution per class | MISSING | NONE | CHG-21 | Review transport adapter | D | G-P06 | T-19 | Each review class has a typed resolution; human input never mutates payload directly |
| G-E01 / U-02 | D/S/H/J per rule | MISSING | N/A | Assigned in RECORDS; enforced by traceability CI (CHG-26) | RECORDS; CI | N/A | RECORDS | T-21 | Every active rule has a type in the traceability index |
| G-E02 / U-04, U-11 | Semantic Execution Contract + invocation envelope | MISSING | NONE | CHG-25 | Semantic runtime layer | H | CLOSE | T-23–T-27 | Closed output; rule_basis mandatory; abstention only via triggers; envelope recorded per call |
| G-E03 / U-10, U-11 | Rule-pack and prompt versioning | MISSING | NONE | CHG-24, CHG-25 | Rule-pack registry | D | G-P07 | T-22 | Hash mismatch aborts run |
| G-E04 / U-13 / D05 EX-INPUT-2 | Runtime outcome taxonomy (refusal vs review vs failure vs empty) | MISSING | NONE | CHG-20 | Runtime outcome layer | D | — | T-13, T-14, T-19 | Infrastructure failure never appears as UNCERTAIN or REVIEW_REQUIRED |
| G-E05 / U-14 / G-P05 | Run identity, fingerprint, idempotent replay | MISSING | NONE | CHG-22 | Lifecycle adapter | D | G-P05 | T-16, T-22 | Replay with same fingerprint is a no-op or identical output |
| G-E07 / U-07, U-08 | Implementation phases, work packages, DoD | MISSING | N/A | II.6, II.10 | Programme | N/A | Phases A–D | — | Each package has executable DoD |
| G-P01 / U-05 / G-V05 | Canonical hashed text; offset coordinate system | MISSING | NONE | CHG-01 | Canonical source library | D | provider | T-01 | Gold/probe offsets recomputed against artefact; byte-identity holds |
| G-P02 | Segmentation guarantee | MISSING (interface fixable; ownership open) | NONE | CHG-02 | Segmentation adapter | D | G-D10 | T-01, T-06 | Units deterministic under pinned version |
| G-P03 | Positioning-context guarantee | DECISION_REQUIRED (G-D06) | NONE | CHG-03 | Adapter | D | G-D06 | T-19 | as G-S02 |
| G-P04 | Citation lookup guarantee | MISSING | NONE | CHG-04 | Citation adapter | D | provider | T-12 | Deterministic for pinned registry version |
| G-P05 | Closure, invalidation, immutability (conditional) | MISSING | NONE | CHG-22 | Lifecycle adapter | D | G-D01 (immutability), G-D02 | T-16, T-18 | Identity-relevant change triggers invalidate → recompute → reverify |
| G-P06 | Review transport | MISSING | NONE | CHG-21 | Review adapter | D | — | T-19 | as G-S16 |
| G-P07 | Version registry | MISSING | NONE | CHG-05 | Config/provenance | D | — | T-22 | as G-S03 |
| G-P08 / U-09 | Oracle harness | MISSING | NONE | CHG-27 | Test harness | D | CHG-06 | T-27 | Gold substitution at every applicable boundary |
| G-P09 / U-14 | Run/audit store | MISSING | NONE | CHG-23 | Persistence | D | — | T-11, T-16 | Atomic write; recovery; immutable versions |
| G-P10 / R-145 | Publication gate | MISSING | NONE | CHG-19 | Publication gate | D | CHG-18, CHG-22 | T-17, T-18 | Only PASS ∧ not invalidated publish; unit = CanonicalGap when identity on |
| G-V04 | Suites as conformance evidence | DECISION_REQUIRED (G-D01) | N/A | Import suites under HD-26/27/28 or M1(a) | Conformance suite | N/A | G-D01 | T-21 | Imported suite cases traceable to rules |
| G-V05 | Gold offsets tied to canonical artefact | MISSING | NONE | Recompute by quote-matching (II.9) | Fixture builder | D | CHG-01 | T-01 | Every gold span resolves |
| U-12 / U-15 | Traceability and CI enforcement | MISSING | NONE | CHG-26 | CI | D | CHG-06, CHG-24 | T-20, T-21 | CI fails on rule without code+test, on drift, on forbidden fields |
| U-16 / U-17 | Governed agent loop; guardrail file | MISSING | NONE | CHG-28 | Repo governance | N/A | RECORDS/CLOSE | — | Stop states machine-readable; spec silence → finding |
| U-18 | Provider test doubles | MISSING | NONE | CHG-29 | Test doubles | D | provider contracts | T-19 | Doubles validate against contract schemas |

## II.5 CONCRETE CHANGES

Common to all records: Repository artifact/path = `REPOSITORY_INSPECTION_REQUIRED — locate or confirm absence of the component; <findings> §6: no A.1-E code exists`; Current implementation = `UNKNOWN_PENDING_REPOSITORY_INSPECTION (expected: none)`; Behaviour owner = A.1-E engineering under RECORDS/CLOSE authority; Version/provenance impact = artefact records governing RECORDS/CLOSE version+hash (NOT YET AVAILABLE until pinned).

CHANGE-ID: CHG-01 — Canonical source & span library
Requirement(s): G-P01, G-S01, U-05, G-V05, R-060, R-058
Finding(s): `<findings>` §2 (pdftotext/soft-hyphen divergence; gold offsets non-authoritative)
Component: canonical source & span library (consumer of G-P01)
Current defect: no canonical hashed text; spans cannot be resolved byte-identically
Exact change: consume the provider's hashed canonical text + offset coordinate system; implement span minting/resolution that returns the verbatim slice and fails (typed) on hash or offset mismatch; store document id, version, hash on every span; provide quote-anchored recomputation for legacy offsets
Why required: every A.1-E element is span-grounded (D06 §8, §16 cl.12)
Interfaces affected: all modules (spans)
Schema affected: span atom
State/lifecycle: none
Tests required: T-01, T-20
Acceptance criterion: 100% of fixture/gold spans resolve byte-identically; mismatch produces typed failure, never a nearest match
Open dependency / blocker: canonical-text-artifact (provider delivery)

CHANGE-ID: CHG-02 — Segmentation adapter
Requirement(s): G-P02, G-S01, R-079, R-020, R-053
Finding(s): none
Component: segmentation adapter
Current defect: no consumer of units/boundaries/section roles
Exact change: consume proposition/clause units with sentence fallback, paragraph/section boundaries, section roles (UNKNOWN → neutral); expose unit hierarchy with stable ids; no local segmentation logic
Why required: detection unit and candidate cardinality depend on it (D10 CD-INPUT-1/4)
Interfaces affected: Module 1, 2, 3
Schema affected: structural unit, section role
State/lifecycle: none
Tests required: T-01, T-06
Acceptance criterion: deterministic units under pinned segmentation version; adapter never splits or merges units
Open dependency / blocker: segmentation-interface (G-D10) for split ownership

CHANGE-ID: CHG-03 — Positioning-context adapter
Requirement(s): G-P03, G-S02, G-D06, R-010 (g5-focus-transfer)
Finding(s): `<findings>` §4 (focus ~3,000 chars from candidates)
Component: positioning-context adapter
Current defect: no input path for objectives/RQs
Exact change: consume objective[]/research_question[] with spans and an explicit `ABSENT` token; forbid any inference of focus from candidate text when absent; pass the object unchanged to Modules 2 and 5
Why required: G5/focal positioning cannot execute from the envelope alone
Interfaces affected: Modules 2, 5
Schema affected: positioning_context
State/lifecycle: none
Tests required: T-19
Acceptance criterion: absence yields typed ABSENT surfaced to the owning module; no candidate-derived substitute
Open dependency / blocker: G-D06 (input-contract amendment), G-D07 (consumer assignment)

CHANGE-ID: CHG-04 — Citation Registry adapter
Requirement(s): G-P04, G-S08, R-066
Finding(s): none
Component: citation adapter
Current defect: no pinned lookup
Exact change: deterministic lookup against the pinned registry version; result = resolved(registry id) | unresolved(verbatim preserved); no fuzzy matching beyond the registry's own contract
Why required: D06 §9 hard dependency for resolution
Interfaces affected: citation resolution step
Schema affected: citation_resolution_outcome
State/lifecycle: none
Tests required: T-12
Acceptance criterion: same mention + same registry version → same outcome
Open dependency / blocker: provider contract

CHANGE-ID: CHG-05 — Configuration, version pinning and run provenance
Requirement(s): G-S03, G-P07, R-144, R-146, U-11 (part)
Finding(s): none
Component: config/provenance component
Current defect: no pinning; reproducibility unmeasurable
Exact change: require spec, RECORDS/CLOSE, signal-library, detection-rule, vocabulary, rule-pack, prompt, model and registry versions/hashes before a run starts; write them into the run record; abort on any unpinned asset
Why required: R-146; HLA reproducibility invariant
Interfaces affected: all
Schema affected: run_provenance
State/lifecycle: run start
Tests required: T-22
Acceptance criterion: run refuses to start with any unpinned or mismatched version
Open dependency / blocker: hashes NOT YET AVAILABLE

CHANGE-ID: CHG-06 — Canonical machine-readable interface artefact + codegen + drift check
Requirement(s): G-S01–G-S16, U-03, Part I §2.1/§2.2
Finding(s): none
Component: interface artefact and generated types
Current defect: schemas exist only as prose
Exact change: after CLOSE, materialise each RECORDS signature into one canonical machine-readable interface artefact preserving field names, enums, cardinalities, invariants and RECORDS version/hash; generate language types; forbid handwritten duplicates; CI drift check between artefact and generated types; fixtures validate against the same artefact
Why required: U-03; Part I §2.2
Interfaces affected: all
Schema affected: all
State/lifecycle: none
Tests required: T-20
Acceptance criterion: zero drift; every fixture validates; forbidden fields (`scope`, `confidence`, `same_claim`) rejected
Open dependency / blocker: RECORDS/CLOSE not run; open-decision fields typed as UNRESOLVED markers

CHANGE-ID: CHG-07 — Signal Library asset loader
Requirement(s): G-R02, R-069–R-075
Finding(s): none
Component: signal asset loader
Current defect: no loader; no integrity check
Exact change: load the 74-signal registry, priors, false friends and non-firing cases as a versioned data asset; verify hash; expose matches with tier/polarity only; no emission decisions in the loader
Why required: signal ≠ verdict (D13 §40.1)
Interfaces affected: Module 1
Schema affected: signal match
State/lifecycle: none
Tests required: T-05, T-22
Acceptance criterion: loader emits no class or verdict; mutated asset rejected
Open dependency / blocker: none

CHANGE-ID: CHG-08 — Candidate detection engine
Requirement(s): G-R01, R-076–R-084, HD-13, HD-07
Finding(s): none
Component: candidate detection engine
Current defect: none exists
Exact change: deterministic rule engine over units + signal matches; every candidate cites ≥1 emission rule and ≥1 signal; context capture per envelope constants; span-identity dedup; deterministic ordering; exhaustive evaluation of all eligible units; lawful empty set; envelope/region/trigger constants loaded from pinned config carrying an UNRESOLVED marker until G-D03 closes
Why required: HD-13; R-083; R-076–R-081
Interfaces affected: Module 1 → 2
Schema affected: GapCandidate
State/lifecycle: none
Tests required: T-05, T-06, T-15, T-22
Acceptance criterion: identical inputs → identical ordered candidate set; no LLM invocation in the path
Open dependency / blocker: G-D01, G-D03

CHANGE-ID: CHG-09 — Boundary classification engine
Requirement(s): G-R03, R-009–R-026, HD-01, HD-11, HD-15, SD-03, SD-04
Finding(s): `<findings>` §4 (G6 → OTHER; G1 → UNCERTAIN(T3))
Component: boundary classification engine
Current defect: none exists; three constructions have no rule exit
Exact change: implement D0–D6 and PR-0..10 as the bounded procedure; semantic reading confined to the tests the procedure names; output class + rule_basis + diagnostics + uncertainty block (trigger, ≥2 competing classes); typed `UNRESOLVED_RULE` exit for decision1-g5, result-reported-gap, agenda-positioning, we-lack-referent, manuscript-adoption, temporal-currency that routes to review without assigning a class
Why required: seven-class truth; no section gate; UNCERTAIN preserved
Interfaces affected: Module 2 → 3, run record
Schema affected: BoundaryResult
State/lifecycle: boundary review
Tests required: T-07, T-08, T-11, T-23–T-27
Acceptance criterion: no class emitted for an open construction; every class carries rule ids; no section-only decision
Open dependency / blocker: G-D07, G-D08, G-D09, G-D13 (trigger codes)

CHANGE-ID: CHG-10 — Run-level boundary record emission
Requirement(s): G-S05, R-009 (Item 2), SD-04
Finding(s): none
Component: boundary record emitter
Current defect: non-GAP truth would be discarded
Exact change: persist candidate ref + BoundaryResult + diagnostics + uncertainty + provenance for every evaluated candidate; update on re-review; never publish downstream
Why required: seven-class validation and non-GAP diagnostics retention
Interfaces affected: Module 2 → run store
Schema affected: candidate_boundary_results
State/lifecycle: re-review update
Tests required: T-11
Acceptance criterion: count(evaluated candidates) = count(records) after every run and re-review
Open dependency / blocker: CHG-23

CHANGE-ID: CHG-11 — Assertion / deficiency extraction engine
Requirement(s): G-R04, G-R05, G-R06, R-023–R-068, R-089, HD-19, HD-15, HD-07, HD-08, HD-06
Finding(s): `<findings>` §4 (G3 cardinality)
Component: extraction engine (semantic step under Semantic Execution Contract)
Current defect: none exists
Exact change: produce GapOccurrenceDraft: minimal assertion span (HD-19 include/exclude lists), explicitness + completion support within the Step-10 envelope only, relation/kind by DPR procedure, object by OR procedure, preserved_context_refs, contrast evidence, citation stubs, non-spawn reason spans in evidence_refs, review_requirements; ban list of silent fallbacks enforced; attribution-frame inclusion and `method` artifact kind routed to typed UNRESOLVED
Why required: G-R04–G-R06
Interfaces affected: Module 3 → resolution/validation; loop
Schema affected: GapOccurrenceDraft
State/lifecycle: extraction review
Tests required: T-01–T-04, T-09, T-12, T-23–T-27
Acceptance criterion: proposition exactly reconstructable from spans; no ban-list coercion observable; every semantic call carries rule_basis and envelope
Open dependency / blocker: G-D09, G-D10, G-D11, G-D12, G-D14

CHANGE-ID: CHG-12 — Reason-derived loop controller
Requirement(s): G-R12, G-E06, R-068, R-081, R-116
Finding(s): none
Component: reason-loop controller
Current defect: loop has no termination/dedup contract
Exact change: when extraction emits an independently asserted reason-clause deficiency, mint a candidate with lineage (parent occurrence, reason span); dedup by span identity only; forbid derivation from a derived candidate's own reason clause; route to boundary classification; declare loop complete when no new span-grounded reason candidate exists; report completion to lifecycle as closure precondition
Why required: R-068 (never silently demoted); Item 1
Interfaces affected: Module 3 → 2; lifecycle
Schema affected: GapCandidate lineage
State/lifecycle: closure precondition
Tests required: T-06, T-15, T-16
Acceptance criterion: no infinite recursion on adversarial fixtures; same-span never re-emitted; distinct-span identical text kept distinct
Open dependency / blocker: cardinality-authority (G-D10)

CHANGE-ID: CHG-13 — Deterministic citation resolution step
Requirement(s): R-066, R-067, G-S08
Finding(s): none
Component: citation resolution step
Current defect: none exists
Exact change: for each citation_ref call CHG-04; record outcome; unresolved → verbatim preserved + outcome + review requirement (class: citation confirmation); never drop; never treat as linked
Why required: D06 §2(v), §8/§9
Interfaces affected: between Module 3 and validation
Schema affected: citation_resolution_outcomes
State/lifecycle: citation confirmation review
Tests required: T-12, T-13
Acceptance criterion: every ref has one outcome; unresolved creates a blocking review requirement
Open dependency / blocker: none

CHANGE-ID: CHG-14 — Deterministic occurrence validator
Requirement(s): R-030, R-031, R-037, R-044, R-092, R-098, R-140, G-S09, G-R11
Finding(s): none
Component: validator
Current defect: none exists
Exact change: check closed relation/kind enums, relation×kind matrix (P-cell → return to owning rule for re-derivation or review; A-cell requires traced licensing), structural invariants, forbidden fields (scope, confidence), diagnostics-never-alter-class; never substitute a value
Why required: DP-PAIR-3; I-37; R-098
Interfaces affected: validation → representation
Schema affected: validation codes
State/lifecycle: review routing
Tests required: T-02, T-03, T-04, T-09
Acceptance criterion: invalid occurrence never reaches representation; validator output is a typed code, never a corrected value
Open dependency / blocker: G-S09 codes at RECORDS

CHANGE-ID: CHG-15 — Occurrence representation and normalization slot
Requirement(s): G-S10, G-S07, R-062, R-059, R-058, HD-12
Finding(s): none
Component: occurrence builder
Current defect: none exists; grammar undefined
Exact change: build GapOccurrence from validated draft; carry traceability class per element; `normalized_proposition` produced by method `A1E-EX-NORM-1.0` only once its grammar is recorded (G-D12); until then the field is typed UNRESOLVED and identity comparison on it is disabled
Why required: D06 §16 cl.3
Interfaces affected: Module 4 → 5
Schema affected: GapOccurrence
State/lifecycle: none
Tests required: T-03, T-04, T-20
Acceptance criterion: no field populated by default; unresolved fields carry the typed marker
Open dependency / blocker: G-D12

CHANGE-ID: CHG-16 — Occurrence role assignment
Requirement(s): G-R08, G-S11, HD-01, SD-01, SD-02
Finding(s): none
Component: occurrence role module
Current defect: none exists; operational test open
Exact change: assign FOCAL_STUDY_POSITIONING / REVIEW_FINDING / RESTATEMENT on the occurrence using positioning-context; derive alignment_eligible; never write role to CanonicalGap; RESTATEMENT carries no SAME_GAP claim; open positioning test → typed UNRESOLVED
Why required: HD-01; SD-01
Interfaces affected: Module 5 → 6/7, downstream
Schema affected: discourse_role, alignment_eligible
State/lifecycle: none
Tests required: T-10, T-17
Acceptance criterion: as G-R08 row
Open dependency / blocker: G-D07

CHANGE-ID: CHG-17 — Identity / resolution module (conditional)
Requirement(s): G-R09, G-S12, G-S13, R-102–R-111, R-094, HD-05
Finding(s): `<findings>` §3 (no identity gold)
Component: identity module behind M2 switch
Current defect: none exists; scope undecided
Exact change: if M2 = in scope: batch over the closed universe; SAME_GAP conjuncts with OE/P-EQ registries; conservative default; complete-linkage clustering; representative by precedence supplying whole payload; links with basis codes; if M2 = deferred: module inactive, occurrences flow directly to verification
Why required: D12; HD-05
Interfaces affected: Module 5 → 7
Schema affected: CanonicalGap, links
State/lifecycle: identity invalidation
Tests required: T-16, T-17, T-18, T-23–T-27
Acceptance criterion: switch state is explicit in run record; no merge without established equivalence
Open dependency / blocker: G-D02, identity-gold, attribution-frame, normalization-grammar

CHANGE-ID: CHG-18 — Verification engine
Requirement(s): G-R10, G-S14, R-126–R-130, R-067, HD-14
Finding(s): none
Component: verification engine
Current defect: none exists
Exact change: fresh invocation over the occurrence/identity representation; check families incl. prohibited content; three statuses; REJECT only for deterministic NON-GAP, prohibited reconstruction, fabricated assertion; correctable defects → REVIEW_REQUIRED; unresolved citations block PASS until human-confirmed; never modify payload; independence guarantee implemented but flagged CONDITIONAL (R-127) in provenance
Why required: HD-14; D06 §2
Interfaces affected: Module 7 → 8
Schema affected: VerificationResult
State/lifecycle: verification review
Tests required: T-12, T-13, T-14, T-19
Acceptance criterion: fatal codes limited to the three; no payload mutation detectable by diff
Open dependency / blocker: G-D01 (R-127, R-101, code registry)

CHANGE-ID: CHG-19 — Downstream publication gate
Requirement(s): G-P10, R-145, D06 §2/§11
Finding(s): none
Component: publication gate
Current defect: none exists
Exact change: publish only objects with status PASS and not invalidated; when identity enabled the unit is CanonicalGap and no occurrence publishes while its canonical Gap is not PASS; run-level boundary record never publishes
Why required: G-P10
Interfaces affected: Module 8 → Research Graph
Schema affected: GapResult
State/lifecycle: publish
Tests required: T-17, T-18
Acceptance criterion: gate rejects REVIEW_REQUIRED, REJECT, UNCERTAIN, invalidated
Open dependency / blocker: G-D02

CHANGE-ID: CHG-20 — Runtime outcome taxonomy
Requirement(s): G-E04, U-13, D05 EX-INPUT-2, R-089
Finding(s): none
Component: runtime outcome layer
Current defect: infrastructure failure indistinguishable from scientific outcome
Exact change: introduce the typed runtime result union for successful output, lawful empty result, REVIEW_REQUIRED, structural REFUSAL (invalid input), provider failure/absence, and terminal REJECT; prevent infrastructure errors from being represented as UNCERTAIN or REVIEW_REQUIRED; language-specific exception mapping chosen after the taxonomy
Why required: silent drop prevention
Interfaces affected: all modules
Schema affected: runtime result union
State/lifecycle: none
Tests required: T-13, T-14, T-19
Acceptance criterion: no path maps an exception to a scientific status
Open dependency / blocker: none

CHANGE-ID: CHG-21 — Review transport and re-entry
Requirement(s): G-P06, G-S16, R-143, R-017, R-067
Finding(s): none
Component: review adapter
Current defect: none exists
Exact change: emit typed review requirements per class (boundary UNCERTAIN, extraction, citation confirmation, verification); receive typed human resolution; re-execute the owning operation with the resolution as class-specific input (boundary: review context per D07 §38.15; citation: confirmation evidence; verification: correction then fresh round); no direct payload mutation
Why required: R-143; HLA review interface
Interfaces affected: Modules 2, 3, 7; lifecycle
Schema affected: review requirement/resolution
State/lifecycle: review, re-execution
Tests required: T-19
Acceptance criterion: human resolution never writes a semantic field directly
Open dependency / blocker: G-D13 (codes)

CHANGE-ID: CHG-22 — Lifecycle adapter: closure, invalidation, run identity, conditional immutability
Requirement(s): G-P05, G-E05, R-109, R-083, R-101 (conditional), Item 1
Finding(s): none
Component: lifecycle adapter
Current defect: none exists
Exact change: compute execution fingerprint = declared inputs + all pinned versions; idempotent replay; universe-closure signal (treatment of pending reviews typed UNRESOLVED until decided); on identity-relevant change: invalidate CanonicalGap and links → recompute over complete universe → fresh verification; immutability of verified payload enforced only if M1(a)/HD-21, otherwise recorded as inactive
Why required: Item 1; HLA re-execution
Interfaces affected: Modules 6, 7, 8
Schema affected: closure record, invalidation record
State/lifecycle: all
Tests required: T-16, T-18, T-22
Acceptance criterion: replay = no-op; invalidation cascades to links and verification
Open dependency / blocker: G-D01, G-D02, G-D04, G-D15

CHANGE-ID: CHG-23 — A1ERunRecord persistence
Requirement(s): G-P09, G-S15, U-14
Finding(s): none
Component: run/audit store
Current defect: none exists
Exact change: persist run id, manuscript/version/hash, closure/epoch identity, candidate boundary results, review rounds, invalidations, verification results, pinned assets, final state; atomic write/update; recovery; immutable versioned artefacts; MVP storage technology = DECISION_REQUIRED (engineering, non-scientific)
Why required: U-14
Interfaces affected: run record
Schema affected: A1ERunRecord
State/lifecycle: all
Tests required: T-11, T-16
Acceptance criterion: round-trip and recovery tests pass
Open dependency / blocker: storage choice (engineering)

CHANGE-ID: CHG-24 — Rule-pack representation and versioning
Requirement(s): U-10, G-E03, G-R01–G-R12
Finding(s): none
Component: rule-pack registry
Current defect: no representation policy
Exact change: after D/S/H/J, choose per rule family whether rules are data tables or code; stable rule ids; version/hash; loader validation; deterministic ordering; provenance to RECORDS clause
Why required: prevents rule drift; R-146
Interfaces affected: all engines
Schema affected: rule pack
State/lifecycle: none
Tests required: T-21, T-22
Acceptance criterion: every active rule id resolvable to pack entry + RECORDS clause
Open dependency / blocker: RECORDS

CHANGE-ID: CHG-25 — Semantic Execution Contract runtime and invocation envelope
Requirement(s): G-E02, U-04, U-11, R-089, R-140, D07 principle 10
Finding(s): none
Component: semantic runtime layer
Current defect: none exists
Exact change: for every S/H operation: closed output schema, mandatory rule_basis, abstention only via rulebook triggers, no confidence, envelope recorded per call (provider/model/version, parameters, prompt/system/rule-pack hashes, schema version, call provenance); unsupported case → typed review; same pinned inputs → same output or same review route
Why required: prevents silent scientific decisions
Interfaces affected: Modules 2, 3, 6, 7 (if S/H)
Schema affected: semantic call record
State/lifecycle: none
Tests required: T-23–T-27
Acceptance criterion: any output lacking rule_basis or containing a non-closed value is rejected before use
Open dependency / blocker: CLOSE (D/S/H/J)

CHANGE-ID: CHG-26 — Traceability index and CI gates
Requirement(s): U-12, U-15, G-E01, R-141
Finding(s): none
Component: CI
Current defect: none exists
Exact change: traceability index rule id → implementation unit → tests; CI fails on active rule lacking either; gates for schema drift, enum closure, canonical span integrity, prohibited fields, fixture hashes, deterministic validator determinism, serialization round trips, invariant suite
Why required: U-12/U-15
Interfaces affected: repo
Schema affected: traceability index
State/lifecycle: none
Tests required: T-20, T-21
Acceptance criterion: CI green iff all gates pass
Open dependency / blocker: none

CHANGE-ID: CHG-27 — Fixtures and oracle-substitution harness
Requirement(s): U-09, G-P08, D01 29.8, HLA validation-interface invariant
Finding(s): `<findings>` §3 (Gold v0.1 limits)
Component: test harness
Current defect: none exists
Exact change: at least one pinned canonical manuscript fixture; per-module typed fixtures; runner that substitutes gold objects at every applicable boundary; strict separation of development fixtures, adjudication cases, conformance tests, calibration corpus, held-out gold
Why required: component/oracle evaluation
Interfaces affected: all
Schema affected: fixtures validate against CHG-06 artefact
State/lifecycle: none
Tests required: T-27
Acceptance criterion: every applicable boundary substitutable; fixture classes labelled
Open dependency / blocker: G-V01, G-V05

CHANGE-ID: CHG-28 — Agent guardrail file and governed review loop
Requirement(s): U-16, U-17, Part I §7.4
Finding(s): `<findings>` §5 (review-loop amendments)
Component: repository governance
Current defect: none exists
Exact change: guardrail file derived from RECORDS/CLOSE (prohibitions; spec silence → stop and emit finding); review protocol with stop states converged/stalled/cap_reached, per-cycle target hash/exact input/raw output, fix-or-reject-with-evidence, rejected findings counted as unresolved for convergence, gold baseline before/after
Why required: U-16/U-17
Interfaces affected: development workflow
Schema affected: finding record
State/lifecycle: none
Tests required: —
Acceptance criterion: protocol machine-readable; no cycle accepted without evidence
Open dependency / blocker: none

CHANGE-ID: CHG-29 — Provider test doubles
Requirement(s): U-18
Finding(s): none
Component: test doubles
Current defect: none exists
Exact change: deterministic, contract-valid doubles only for unavailable providers; validate against provider contract schemas; never used for validity claims
Why required: U-18
Interfaces affected: adapters
Schema affected: none
State/lifecycle: none
Tests required: T-19
Acceptance criterion: double outputs validate against the contract; flagged in run provenance
Open dependency / blocker: none

## II.6 EXECUTION ORDER

The 18-step critical path of Part I §9.2 is preserved; phases below map onto it and add change-level sequencing.

| Phase | Part I steps | Changes | Prerequisites | Must be frozen before next phase |
|---|---|---|---|---|
| A — GOVERNING DECISIONS | 1–9 | none (decisions only) | G-D04 → G-D01 → G-D03 → G-D02 → G-D06 → G-D07/08 → G-D10 → G-D09 → G-D11–15, G-D05 | signed HD entries or lawful parking with defined behaviour |
| B — RECORDS / PLATFORM CONTRACTS | 10–11 | provider contracts G-P01–P10 (provider side); RECORDS batches | Phase A | RECORDS Section 1 signatures; provider contracts |
| C — CLOSE / SEMANTIC EXECUTION CONTRACTS | 12 | SEC per S/H operation (CHG-25 spec) | Phase B | CLOSE pinned; D/S/H/J final |
| D — PRE-IMPLEMENTATION ADEQUACY GATE | 13 | spec-adequacy probe | Phase C | GO/NO-GO |
| E — IMPLEMENTATION PLANNING | 14 | repository inspection; package map; DoD (II.10.A); CHG-24 policy; CHG-20 taxonomy; storage choice for CHG-23; CHG-28 | Phase D | package plan approved |
| F — INTERFACE / RULE-PACK / PERSISTENCE | 15 | CHG-05, CHG-06, CHG-07, CHG-24, CHG-23, CHG-26 (gates), CHG-01, CHG-02, CHG-03, CHG-04, CHG-29 | Phase E | interface artefact hash; rule-pack hashes |
| G — MODULE IMPLEMENTATION | 15 | CHG-08, CHG-09, CHG-10, CHG-11, CHG-12, CHG-13, CHG-14, CHG-15, CHG-16, CHG-17 (if M2), CHG-18, CHG-19, CHG-20, CHG-21, CHG-22, CHG-25 | Phase F | none until H |
| H — COMPONENT CONFORMANCE | 15 | CHG-27 harness; tests T-01–T-27 per module | Phase G | component DoD per package |
| I — INTEGRATION / RE-ENTRY / INVALIDATION | 16 | end-to-end runs; review re-entry; invalidation; replay; publication gate | Phase H | IMPLEMENTATION_COMPLETE |
| J — CALIBRATION | 17 | thresholds, MATCH_CRITERION per D01 | Phase I; G-V01/V02 | calibration record |
| K — HELD-OUT VALIDATION | 17 | sealed cohorts; one exposure | Phase J | SCIENTIFICALLY_VALIDATED |
| L — FREEZE / RELEASE | 18 | pin hashes, versions, evidence | Phase K | FROZEN_RELEASE |

Change-level dependencies (prerequisites → change → dependants): CHG-01 → CHG-02, CHG-06, CHG-27 → all modules; CHG-05 → CHG-07, CHG-24, CHG-25; CHG-06 → CHG-08…CHG-19, CHG-26; CHG-07 → CHG-08; CHG-08 → CHG-09 → CHG-10, CHG-11 → CHG-12 → (loop) CHG-09; CHG-11 → CHG-13 → CHG-14 → CHG-15 → CHG-16 → CHG-17 (M2) → CHG-18 → CHG-19; CHG-20, CHG-21, CHG-22, CHG-23 are cross-cutting prerequisites of Phase I; CHG-25 precedes any S/H module test; CHG-26/27/28/29 precede Phase H. Scientific decisions are never reordered for engineering convenience: CHG-09/CHG-11/CHG-16/CHG-17 remain gated by Phase A items even if scaffolding exists.

## II.7 DETERMINISTIC / CONFORMANCE TESTS

Fixture classes are strictly separated: development fixtures (DF), adjudication cases (AC), conformance tests (CT), calibration corpus (CC), held-out gold (HG). Cases used to author a rule (AC) are never counted as HG for that rule.

| Test ID | Requirement | Component | Positive case | Negative case | Mutation / refusal case | Expected result | Fixture / oracle source |
|---|---|---|---|---|---|---|---|
| T-01 | R-060, G-P01, G-V05 | CHG-01 | span resolves byte-identically | offset shifted by 1 | hash mismatch | typed failure, no nearest match | DF: pinned canonical manuscript |
| T-02 | R-030, R-031, R-037 | CHG-14 | canonical pair accepted | P-cell pair | value outside enum | P-cell → re-derive/review; enum breach rejected | CT: matrix table from D08 §39.7 |
| T-03 | R-047, R-092, G-R11 | CHG-14, CHG-06 | object without scope token | object containing "among nurses" | field `scope` present | rejected at validator and schema | CT: OR-SCOPE cases from D11 |
| T-04 | R-140 | CHG-06, CHG-25 | output without confidence | numeric confidence field | model returns probability | rejected before use | CT |
| T-05 | R-069, R-077, HD-13 | CHG-07, CHG-08 | STRONG signal → candidate with basis | prior-only unit | LLM call attempted | no candidate without registered basis; call forbidden | DF + CT |
| T-06 | R-081, G-R12 | CHG-08, CHG-12 | same-span derived candidate | identical text at distinct span | re-derivation from own reason clause | not re-emitted; kept distinct; forbidden | CT adversarial |
| T-07 | R-009, R-017 | CHG-09 | seven classes reachable | UNCERTAIN with one competitor | section-only evidence | ≥2 competitors required; section never sufficient | CT from D07 suites (status per M1) |
| T-08 | G-R07, G-D07–09 | CHG-09 | attested construction | — | rule absent | typed UNRESOLVED_RULE, no class | AC |
| T-09 | HD-19, R-059 | CHG-11 | minimal span reconstructs proposition | motivation clause included | completion outside envelope | over-extension flagged; outside-envelope → review | CT + AC |
| T-10 | HD-01, SD-01 | CHG-16 | FOCAL role on occurrence | role on CanonicalGap | RESTATEMENT used as SAME_GAP | rejected | CT |
| T-11 | G-S05 | CHG-10, CHG-23 | all candidates persisted | non-GAP dropped | re-review not updated | counts equal; update recorded | DF end-to-end |
| T-12 | R-066 | CHG-13, CHG-04 | resolved ref | unresolved ref | ref dropped | unresolved kept verbatim + review | CT |
| T-13 | R-067 | CHG-18, CHG-20 | confirmed capture → PASS possible | unconfirmed → REVIEW_REQUIRED | confirmation treated as support | PASS blocked; support never asserted | CT |
| T-14 | HD-14, R-130 | CHG-18, CHG-20 | fatal condition → REJECT | correctable defect → REVIEW_REQUIRED | infrastructure error | never REJECT/REVIEW for infra; typed failure | CT |
| T-15 | G-R12 | CHG-12 | loop ends | nested reason clauses | cyclic derivation fixture | structural termination, no cap | CT adversarial |
| T-16 | Item 1, R-109, G-P05 | CHG-22, CHG-17 | change → invalidate → recompute → reverify | stale identity reused | replay same fingerprint | cascade occurs; replay no-op | DF + CT |
| T-17 | G-P10 | CHG-19 | PASS ∧ not invalidated publishes | REVIEW_REQUIRED | invalidated PASS | only first publishes; canonical unit when identity on | CT |
| T-18 | R-102, HD-05 | CHG-17 | equivalence established → merge | contextual variant | triple-only match | no merge; link recorded | CT from D12 (if M2) |
| T-19 | G-S16, G-P03, U-13 | CHG-21, CHG-03, CHG-20, CHG-29 | typed resolution re-executes owner | direct field edit | provider absent | edit rejected; ABSENT token surfaced; not inferred | CT + doubles |
| T-20 | U-03, §2.2 | CHG-06, CHG-26 | artefact = generated types | drifted type | forbidden field | CI fails | CI |
| T-21 | U-12 | CHG-26 | rule → code → test present | rule without test | test deleted | CI fails | CI |
| T-22 | R-146, G-S03 | CHG-05, CHG-24 | pinned run | unpinned asset | mutated rule pack | run refuses to start | CI/DF |
| T-23 | SEC | CHG-25 | supported semantic case | — | — | closed output + rule_basis | CT |
| T-24 | SEC | CHG-25 | rulebook-authorized abstention | — | — | UNCERTAIN/review via trigger | CT |
| T-25 | SEC | CHG-25 | — | confidence-driven decision | model rationale used | rejected | CT |
| T-26 | SEC | CHG-25 | — | invalid enum/output | schema breach | rejected before use | CT |
| T-27 | SEC, D01 29.8 | CHG-25, CHG-27 | same-input replay | — | — | identical output or identical review route; oracle substitution at every applicable boundary | CT/harness |
| T-28 | R-006 | CHG-08, CHG-19 | manuscript with no gaps | — | — | lawful empty run, record written | DF |

Mapping: requirement → change → test → expected result is given row-wise above and in II.4.

## II.8 INVARIANTS THAT MUST REMAIN TRUE

1. Scientific meaning comes only from RECORDS/CLOSE plus signed decisions; implementation artefacts never become normative.
2. No unresolved scientific choice may be silently implemented; every open G-D is a typed unresolved outcome.
3. Candidate detection remains deterministic under HD-13; no LLM in the normative path.
4. No numeric confidence anywhere (R-140).
5. No source-unlicensed reconstruction (R-026; D06 §7).
6. No structured Scope/Context object owned by A.1-E; contextual restrictions remain source-linked and unclassified (R-047; D06 §16 cl.4).
7. Diagnostics never create, reclassify or supply content for a Gap (R-098).
8. Same-span derived candidate is not re-emitted; identical text at different spans remains distinct at candidate level; semantic duplicate resolution belongs to identity (R-081, G-R12).
9. Run-level seven-class truth is retained for every evaluated candidate (R-009, Item 2).
10. Human review returns typed resolution, never direct semantic mutation (R-143).
11. Verified payload changes only through invalidation/re-execution (conditional immutability per M1).
12. Only PASS-and-not-invalidated objects publish; run-level boundary record never publishes (G-P10).
13. Provider absence is explicit and never inferred over (G-P03; no reconstruction).
14. Code/test refactoring cannot change rule semantics; tests are not weakened to fit implementation.
15. Generated schemas cannot drift from the canonical interface artefact (§2.2).
16. Every span resolves byte-identically to the pinned canonical text (R-060).
17. Signals never determine a verdict; priors never veto (R-069, R-074).
18. Extraction never reclassifies a boundary (R-142; D05 EX-REVIEW-3).
19. REJECT only for the three fatal conditions; verification never repairs (HD-14; R-126).
20. Empty result is lawful (R-006).
21. RESTATEMENT does not establish SAME_GAP; role belongs to the occurrence (HD-01, SD-01).
22. Every run is fully version-pinned (R-146).

## II.9 HISTORICAL / MIGRATION HANDLING

| Artefact | Status | Basis |
|---|---|---|
| Existing A1ERunRecord data | N/A — no production/runtime artefact exists to migrate | `<findings>` §6 |
| Prior candidate/Gap records | N/A — none exist | `<findings>` §6 |
| Prior verification results | N/A — none exist | `<findings>` §6 |
| Old schemas (GS-1.1…1.4 in D09; contract §12) | UNCHANGED as sources; not runtime data; superseded content handled by RECORDS/CLOSE per HD-18 | Register V-04 |
| Old fixtures / Gold Set v0.1 | REGENERATE offsets by quote-matching against the pinned canonical artefact (reconstruction of offsets allowed; annotations unchanged); reclassify as development fixture / adjudication cases, not held-out gold | `<findings>` §2–§3; D01 29.6-D |
| Probe outputs (spec-adequacy probe) | UNCHANGED as evidence; never gold | `<findings>` §4 |
| Old hashes | N/A — none recorded | — |
| Old semantic-call records | N/A — none exist | — |
| Prior conformance evidence (D03/D04/D05/D10 test suites) | DECISION_REQUIRED — G-D01 (HD-26/27/28 or M1(a)); until then evidence only | Part I G-V04 |
| Absent SM-1.3 / GS-1.3 | DECISION_REQUIRED — G-D04; reconstruction from citations is not allowed | Register §2.5 |

No historical evidence is rewritten; regeneration of offsets is recorded with the method and hash of the canonical artefact.

## II.10 ACCEPTANCE CRITERIA

### II.10.A Package-level Definition of Done
A package (one CHG record) is DONE iff: its owning component exists at an inspected repository path; its interface validates against the canonical interface artefact; every rule it implements is in the traceability index with tests; its tests in II.7 pass; its CI gates pass; every open decision it touches is represented by a typed unresolved outcome (never a default); its provenance records governing RECORDS/CLOSE version+hash; no deviation finding is open against it.

### II.10.B Whole-capability acceptance gate
- IMPLEMENTATION_COMPLETE PASS iff: all required governing decisions for active functionality are signed or lawfully parked with defined behaviour; RECORDS/CLOSE pinned; active rule text consolidated; every active rule has D/S/H/J; every executable module has machine-readable typed interfaces; every S/H operation has a Semantic Execution Contract; required provider contracts exist; canonical manuscript/span contract exists; rule→implementation→test traceability complete; fixtures and oracle harness exist; conformance tests T-01–T-28 pass; CI gates pass; runtime outcome taxonomy implemented; A1ERunRecord persistence operational; invalidation/re-execution integration tests pass; PASS-only publication passes; no unapproved deviation exists; required versions/hashes pinned.
- SCIENTIFICALLY_VALIDATED PASS iff IMPLEMENTATION_COMPLETE and: G-V01–G-V06 satisfied for every validity claim made; calibration recorded (D01 29.10); held-out cohorts sealed and exposed once; component (oracle) and pipeline regimes both reported (D01 29.8); any rule lacking gold carries VALIDATION_GAP and is not claimed validated.
- FROZEN_RELEASE PASS iff SCIENTIFICALLY_VALIDATED and: all hashes/versions pinned; unresolved-but-parked items listed with defined behaviour; `frozen-status` and `source-missing-sm13-gs13` closed or lawfully parked by signed decision.
These three statuses are distinct and never collapsed.

## II.11 KNOWN UNCERTAINTIES / DECISIONS REQUIRED

An unresolved decision cannot be turned into a hidden implementation default; temporary behaviour is always a typed unresolved outcome routed to review or a flagged inactive path.

| Decision | Affected implementation | May work proceed? | Temporary behaviour | Latest closure point |
|---|---|---|---|---|
| G-D01 (M1) | CHG-08 constants, CHG-18 independence/immutability, suites | Scaffolding yes; rule content no | constants marked UNRESOLVED; independence flagged CONDITIONAL | before Phase B freeze |
| G-D02 (M2) | CHG-17, CHG-19 unit, CHG-22 closure, CHG-23 record | Adapters yes; identity code no | switch inactive; occurrences flow to verification | before Phase B |
| G-D03 (M3) | CHG-08 | Engine yes | provisional config flagged UNRESOLVED; denominators not sealed | before Phase F |
| G-D04 (M4) | CHG-22, CHG-15 invariants | Yes | SM-1.3-dependent rules absent, not reconstructed | before Phase B |
| G-D05 (M5) | RECORDS citations | Yes | mapping applied by convention | before Phase B |
| G-D06 | CHG-03 | Adapter yes | ABSENT token; no absence behaviour decided | before BoundaryClassification signature (Phase B) |
| G-D07 | CHG-09, CHG-16 | Engines yes | UNRESOLVED_RULE exit → review | before Phase C |
| G-D08 | CHG-09 | Yes | UNRESOLVED_RULE exit → review | before Phase C |
| G-D09 | CHG-09, CHG-11, CHG-17 | Yes | T2a fallback only where genuinely indeterminate; frame inclusion → review | before Phase C |
| G-D10 | CHG-02, CHG-12 | Interface yes | separation only where governing rule requires; owner marked open | before Phase F |
| G-D11 | CHG-11, CHG-06 | Yes | `method` behind flag; artifact_kind enum typed with UNRESOLVED marker | before Phase F |
| G-D12 | CHG-15, CHG-17 | Yes | normalized_proposition UNRESOLVED; identity P-EQ-1 disabled | before Phase C |
| G-D13 | CHG-09, CHG-21 | Yes | trigger/flag codes provisional, non-normative | before Phase F |
| G-D14 | CHG-11, CHG-15 | Yes | descriptors not minted; corroborating role unused | before Phase F |
| G-D15 | CHG-22 | Yes | SM state names external; no alias table | before Phase F |

## II.12 PLAN-DEVIATION BOUNDARY

A MATERIAL DEVIATION is any proposed change that: changes scientific semantics; changes a closed enum; changes rule precedence; changes a rule's D/S/H/J type; adds a semantic fallback; changes source-span semantics; introduces reconstruction; introduces confidence; creates structured Scope/Context inside A.1-E; changes candidate identity/deduplication semantics; changes reason-loop termination; changes lifecycle or invalidation semantics; changes PASS/REVIEW_REQUIRED/REJECT semantics; changes publication eligibility; changes identity topology; resolves an open G-D; changes a provider contract so that scientific behaviour changes; introduces an unrelated architectural refactor; changes tests because implementation fails rather than because the governing rule changed.

For any such deviation: STOP → emit deviation finding → cite affected requirement/decision → explain proposed change → obtain human approval → update governing specification if approved → only then resume. Non-material details may proceed only where RECORDS/CLOSE leaves genuine engineering discretion and scientific behaviour is unchanged.

## II.13 PROHIBITED PLAN CONTENT

Prohibited: speculative improvements unrelated to active requirements; convenience refactors; architecture additions unsupported by RECORDS/CLOSE; hidden defaults for unresolved decisions; inferred scientific semantics; tests weakened to fit implementation; generated implementation artefacts becoming normative; silent history rewriting; silent dropping of failed or unsupported cases; confidence-based semantic routing.

## II.14 TRACEABILITY COMPLETENESS CHECK

For every active requirement in II.4: governing source (R-*/HD/SD/D-doc) — present; implementation owner (logical component) — present; implementation artefact or planned artefact (CHG-*) — present; test (T-*) — present; expected result — present; acceptance criterion — present. Repository paths are typed REPOSITORY_INSPECTION_REQUIRED, which the plan permits as a planned artefact.

IMPLEMENTATION PLAN STATUS = READY FOR REPOSITORY INSPECTION AND PHASE-A DECISIONS; NOT READY FOR IMPLEMENTATION until Phases A–D complete (governing versions/hashes NOT YET AVAILABLE; 15 decisions unsigned).

</execution_gap_HL_3>
