# A.1-E Gap Extraction Contract v1.2 — EpistemicOS

**Status:** revision of v1.1; normative once the Freeze Check (end of document) passes. Freezes the capability boundary of A.1-E before schema, knowledge-base, detection, extraction, resolution, verification, and validation design.
**Sources:** `A1_gap_statements_spec_v0-3.md` (*spec*), `A1_gap_rulebook_v0-1.md` (*rulebook*), `A1E_gap_extraction_contract_v1-0.md` (*v1.0*), `A1E_gap_extraction_contract_v1-1.md` (*v1.1*). Tags: `[SRC]` source-derived; `[NEW]` introduced in v1.0; `[REV v1.1]` / `[REV v1.2]` revised in that version.
**Architecture:** A.1-E (what the manuscript explicitly claims) → A.1-C (what kind of claimed gap) → A.1-A (is the claimed gap scientifically defensible). A.1-E is one extraction capability within the Research Structure, alongside — not above — Scope/Context, RQ, and Construct extraction (§11).

**Revision record (v1.1 → v1.2, narrow architectural correction):** research **scope/context is not owned by A.1-E**. It is a separate Research Structure object with its own extraction capability. Consequences: (1) the primitive becomes `relation + knowledge_kind + affected_object`; (2) all structured scope fields, identity-bearing scope, scope-type descriptive qualifiers, salience/head flags, and scope canonicalization are removed from A.1-E; (3) contextual wording is fully preserved through source grounding of the complete asserted deficiency proposition; (4) claim identity/merging is redefined on the primitive triple plus source-grounded proposition equivalence, conservatively; (5) the affected-object boundary is corrected (object ≠ scope container); (6) cross-object links (Gap ↔ Scope, Gap ↔ RQ) are produced downstream in the Research Object Graph. Everything not affected is preserved from v1.1.

---

## 1. Capability identity `[REV v1.1; v1.2 unit revised]`

| Field | Value |
|---|---|
| Capability ID | A.1-E |
| Name | Gap Extraction |
| Purpose | **A.1-E extracts explicit study-positioning gap claims: deficiencies in prior knowledge that form part of the manuscript's stated rationale or positioning for the present research.** |
| Core question | *What gap does the manuscript explicitly claim as positioning for the present research?* |
| Unit of extraction | One deficiency proposition — one asserted deficiency `(relation, knowledge_kind)` about one affected object — preserved with its **complete asserted wording**, including any contextual restrictions, which A.1-E preserves but does not structurally classify. `[REV v1.2]` |
| Authoritative output | The set of `extraction_verified` study-positioning gap objects for a manuscript, plus an UNCERTAIN queue and diagnostic notices. The empty set is a valid, meaningful output. |

A.1-E does **not** extract every knowledge deficiency appearing anywhere in the manuscript. Deficiencies that arise only after the study — the manuscript's own limitations, newly opened future-research needs — are not study-positioning claims and are not A.1-E records (§6). A.1-E also does **not** own research scope/context (§4, §5, §11). `[REV v1.2]`

---

## 2. Epistemic contract

Three truth layers, never conflated:

- **Manuscript truth** — the claim as the manuscript asserts it. May be scientifically false; A.1-E does not care.
- **Extraction truth** — the structured record faithfully represents that assertion. This, and only this, is what A.1-E certifies.
- **Scientific truth** — whether the claimed deficiency actually holds in the literature. Never touched by A.1-E (A.1-A; literature validation).

**`extraction_verified` means** `[REV v1.1; v1.2 addition in (iii)]`: EpistemicOS has verified that (i) a primary span lies in an eligible positioning context (§3) and explicitly asserts the deficiency — directly, or through the linguistic completion licensed in §7; (ii) the record's boundary class is GAP under the KB-3 tests; (iii) every element of the record satisfies the traceability classes of §8, **including that the complete asserted deficiency proposition is exactly reconstructable from its source spans** `[REV v1.2]`; (iv) the primitive structuring passes the **paraphrase test** (§3, Note); (v) every citation reference in the record has passed Citation Registry resolution — resolved, or flagged `unresolved` with verbatim preserved and reviewer confirmation recorded (§9); (vi) all extraction validators pass.

**`extraction_verified` must NOT be read as:** the claimed gap exists, matters, is novel, is correctly characterized under any taxonomy, is supported by the cited literature, or is addressed by the study; nor that the record set exhausts the manuscript's deficiency talk — A.1-E's coverage claim is scoped to study positioning; nor that any scope/context classification has occurred — none has. `[SRC: spec §1, §10 — strengthened; REV v1.2]`

---

## 3. In-scope operations

**Note — the paraphrase test (the E/C criterion) `[NEW]`.** An operation or label is extraction-grade iff its output is a faithful closed-vocabulary restatement of what the author asserted — disputable only as a *mis-reading*, never as a *mis-judgment*. "Little is known" ⇒ `(LIMITED, evidence)` restates the predicate; the author could dispute it only by saying "that is not what I wrote." A taxonomy label, a rhetorical-mode label, a scope classification, or a quality verdict imposes an analytic frame the author never asserted; those belong to other capabilities. `[REV v1.2: scope added to the exclusion list]`

| Operation | Why required for extraction |
|---|---|
| Positioning-scope restriction `[REV v1.1]`: eligible contexts are the abstract, introduction, literature review, and theory / conceptual-development sections in their positioning role. Section roles act as **extraction priors and routing evidence**, not as a mechanical "introduction only" rule. | Confines extraction to the manuscript's stated rationale for the present research `[SRC: spec R-GAP-SCOPE, re-scoped]` |
| Candidate detection (lexical + model sweep over eligible contexts) | Claims must be found before they can be represented `[SRC: spec §5 St.1]` |
| Boundary classification (GAP / MOTIVATION / OWN_LIMITATION / FUTURE_RESEARCH / CONTRIBUTION / OTHER / UNCERTAIN) | Only knowledge-deficiency assertions may become gap objects `[SRC: KB-3]` |
| Span capture with roles (primary / restatement / corroborating); later restatements of an established positioning gap attach as `restatement` spans wherever they occur `[REV v1.1]` | Source grounding of the claim and its repetitions `[SRC: spec §3 [Δ]]` |
| **Full-proposition preservation** `[REV v1.2]`: capture of the minimum span set from which the complete asserted deficiency proposition — including any contextual restrictions (population, setting, geography, level of analysis, temporal, or other research-context wording) — is exactly reconstructable. Such restrictions are preserved as **source content only**, never structurally classified by A.1-E. | No manuscript information is lost while scope ownership stays with the Scope/Context capability |
| Explicitness assignment (explicit / context_supported per §7) | Distinguishes linguistic completion from inference; caps the interpretation license `[REV v1.1]` |
| Primitive structuring: relation, knowledge_kind, affected object (surface form) `[REV v1.2: scope removed]` | Minimal semantic content of the asserted deficiency (§5); passes the paraphrase test |
| Proposition normalization (controlled restatement, every content element span-traceable; contextual restrictions retained **unclassified** as span-traced segments `[REV v1.2]`) | One canonical, faithful sentence per claim for downstream identity and alignment `[SRC: spec §3]` |
| Within-manuscript same-claim resolution `[REV v1.2]`: merge only on the primitive triple **plus clear source-grounded proposition equivalence**; contextual differences A.1-E cannot resolve without scope classification → no merge, `possibly_same_claim` link | One claim stated three times is one claim; but contextually distinct claims must never be collapsed by a scope-blind key `[SRC: KB-5, redefined]` |
| Contrast capture: cited works + the proposition the manuscript attributes to them | The explicit contrast is part of the claim as made `[SRC: spec R-GAP-CONTRAST]` |
| Persistence-reason capture (span-anchored, only-if-stated); spawn links **only where the reason itself asserts a prior-knowledge deficiency** `[REV v1.1]` | Explicit claims *about* the gap; assertion-triggered spawn prevents silent loss without manufacturing claims `[SRC: R-GAP-REASON, tightened]` |
| Provisional object descriptor minting + provisional registry linking | Faithful representation must not block on Construct/Phenomenon Registry maturity `[SRC: spec R-GAP-OBJ]` |
| Diagnostic notices (e.g., `presupposed_gap_without_antecedent`) | Coverage metadata carrying no deficiency content `[SRC: rulebook B4]` |
| UNCERTAIN emission / escalation | Undecidable boundaries are surfaced, never coerced `[SRC: KB-6]` |
| Record validation (extraction validators only) | Certifies extraction truth (§2), nothing more |

---

## 4. Out-of-scope operations

| Operation | Destination capability | Why excluded from extraction |
|---|---|---|
| **Structured extraction, classification, canonicalization, or registry linking of research scope/context** — population, setting/context, geography, level of analysis, temporal scope, other research-scope dimensions `[REV v1.2]` | Scope / Context Extraction (Research Structure) | Separately owned Research Structure object; duplicate ownership would fork scope representation. A.1-E preserves the wording, never the structure. |
| Gap ↔ Scope, Gap ↔ RQ, RQ ↔ Scope linking `[REV v1.2]` | Research Object Graph (downstream) | Cross-object links are produced from the separately extracted objects, not inside any single extractor |
| Assigning gap-type labels (the eight-value enum) | A.1-C Characterization | Derived classification over primitives; fails the paraphrase test |
| Assigning mode (incomplete/inadequate/incommensurate) | A.1-C | Rhetorical-stance interpretation, not assertion content |
| Assigning construction (spotting/problematization) | A.1-C | Analytic frame about question construction |
| Primary-type selection, tie-breaks over taxonomy | A.1-C | Presupposes the taxonomy |
| Judging whether the gap exists | A.1-A Analysis | Scientific truth; Müller-Bloch & Kranz-style gap verification `[SRC: spec §1 boundary note]` |
| Judging importance / novelty of the gap | A.1-A | Merit judgment about the world of research |
| Checking whether cited literature supports the gap claim | Citation / literature validation | Requires retrieval and assessment beyond the manuscript |
| Gap ↔ design alignment; gap ↔ objective alignment analysis | Macro Alignment | Cross-object analysis |
| Gap ↔ contribution correspondence; whether the study fills the gap | Contribution Analysis | Outcome judgment over the study's results |
| Canonical construct identity (final registry resolution) | Construct / Phenomenon Registry capability | Shared identity service; A.1-E holds provisional links only |
| Extraction of post-study deficiencies (own limitations; newly opened future-research needs) `[REV v1.1]` | Limitations / Future-Research capability | Not study-positioning claims |
| Cross-manuscript gap comparison / corpus analytics | Corpus-level capabilities | A.1-E is strictly per-manuscript |
| Gap reconstruction from objectives, RQs, contributions, methods | **Nowhere in v1.2** (see §7) | Manufactures claims the manuscript did not make |

---

## 5. Primitive semantic representation `[REV v1.2]`

Basis: `relation + knowledge_kind + affected_object`, together with the separately preserved, complete, source-grounded deficiency proposition.

**Verdict: sufficient, with three amendments** (relation-vocabulary unification; `unspecified` knowledge kind; knowledge-artifact object referents). Scope is no longer a primitive of this capability: contextual restrictions are preserved as source content and structurally owned by Scope/Context Extraction.

| Field | Role | Disposition |
|---|---|---|
| `relation` | The deficiency predicate class asserted of prior knowledge. Provisional closed vocabulary `[SRC: rulebook §5]`: `ABSENT, LIMITED, CONFLICTING, UNTESTED, CONSTRAINED, DISCONNECTED, CHALLENGED`. Single-vocabulary rule: this list supersedes the spec template's divergent labels (§14 C-1). Convention: when the text underdetermines strength, record the weakest supported reading (LIMITED over ABSENT). | ACCEPT + unify |
| `knowledge_kind` | What kind of knowledge is deficient: `evidence, theory, method, practice_alignment` `[SRC: rulebook §5]` **+ `unspecified` `[NEW]`** — "poorly understood" commits to no kind; forcing one would be inference, violating §2. | MODIFY |
| `affected_object` | **What the deficient knowledge is about — not the research scope within which the deficiency applies.** `[REV v1.2]` Referent kinds `[NEW]`: construct/phenomenon; relationship(X,Y); knowledge artifact (named proposition, theory, model, framework, assumption, measure), with an optional `about` link from artifact to subject matter. Surface form + mention span are mandatory; registry link provisional. The object MUST NOT be used as a disguised scope container: "evidence about employee engagement is limited among frontline workers" → object = `employee engagement`, with "among frontline workers" preserved in the proposition, unclassified. **Boundary caution:** wording that names the phenomenon itself may legitimately remain in the object — "network-level effects remain poorly understood" may have object = `network-level effects` if that is the claimed unknown. The operative distinction: *part of what is unknown* (object) vs *restriction on where/for whom/under what context the deficiency applies* (preserved-only). Full operationalization is deferred to coordinated boundary rules between A.1-E and Scope/Context (OD-3). | MODIFY |

**Preserved deficiency proposition (not a primitive; mandatory record content) `[REV v1.2]`:** the minimum span set whose text exactly reconstructs the complete asserted proposition, plus a normalized-with-trace restatement in which contextual restrictions are retained as unclassified, span-traced segments. Qualifiers of the missing knowledge itself (e.g., "large-scale", "fine-grained") likewise remain proposition content, unstructured at A.1-E; the v1.1 descriptive-qualifier structure is removed.

**Additional primitives (must be primitive, not derived):** span set with roles; explicitness class (§7); boundary class; contrast structure (cited-work refs + attributed propositions); persistence-reason attachments with assertion-triggered spawn links `[REV v1.1]`; within-manuscript claim-identity links (`possibly_same_claim`, `related_claim`, `reason_of`); per-field traceability tags (§8). Everything else — taxonomy labels, modes, construction, scope classification, quality judgments — is determined by other capabilities under their own contracts.

**Claim identity `[REV v1.2; replaces the v1.1 rule]`:**

> A.1-E may merge records only when equivalence of the **complete asserted deficiency proposition** is clear from the manuscript without independently classifying scope/context.

Identity test = `(affected_object, relation, knowledge_kind)` **+ source-grounded proposition equivalence**, applied conservatively. The bare triple is insufficient: "No evidence exists about X among frontline workers" and "No evidence exists about X among senior managers" share the triple and MUST NOT merge. Where contextual differences may affect claim identity and A.1-E cannot resolve them without performing scope extraction: **DO NOT MERGE → `possibly_same_claim`**. Final contextual identity MAY later be resolved through the Research Object Graph after Scope/Context extraction; that resolution algorithm is not designed here.

The complete JSON/YAML schema is deliberately **not** defined here.

---

## 6. Statement boundaries (conceptual freeze; full rules remain in KB-3) `[REV v1.1]`

- **GAP** — asserts a deficiency in the *state of prior knowledge* (predicate scoped over knowledge, per the B1 predicate→subject→marker test) **as part of the manuscript's positioning of the present research**.
- **MOTIVATION** — asserts importance, prevalence, or stakes of a *world state*. Contrast markers never convert motivation into gap.
- **OWN_LIMITATION** — deficiency attributed to the manuscript's own study.
- **FUTURE_RESEARCH** — a deficiency or agenda proposal that arises only after the study and does not restate an established study-positioning gap. Restatements of a positioning gap, wherever they occur, attach as `restatement` spans to the existing record (closes spec OI-5). Genuinely new post-study deficiencies route to the Limitations / Future-Research capability, never to A.1-E.
- **CONTRIBUTION** — asserts what the study does or adds; any deficiency is at most presupposed, not asserted.
- **OTHER** — statements about prior literature that assert no deficiency (descriptions of prior methods, findings, or coverage) and all remaining material.
- **UNCERTAIN** — boundary undecidable under KB-3 at extraction time; emitted to review; never silently coerced into any other class.

Assumption-challenge claims ("prior views are wrong") are **GAP** — deficiency relation `CHALLENGED` — with no dependence on downstream mode labels `[SRC: rulebook B5, relocated]`.

---

## 7. Explicitness contract `[REV v1.1]`

| Class | Definition | A.1-E emission |
|---|---|---|
| **explicit** | The deficiency is assertable from the primary span alone. | YES |
| **context_supported explicit** | May be used **only** when immediate co-text resolves referential dependence, ellipsis, omitted arguments, or another linguistic dependency required to recover a deficiency proposition **that the manuscript still explicitly asserts**. Examples: "*These mechanisms* remain unexplored" (antecedent resolution); "Formal ties have been mapped extensively; informal ties have not" (elided predicate recovered). | YES, flagged |
| **inferred** | Deficiency derived from what the manuscript investigates, needs, implies, or subsequently does — but nowhere states. | NEVER |
| **reconstructed** | Deficiency manufactured to fill a missing gap statement, e.g. converting an objective, RQ, or contribution claim into a gap. | NEVER |

**Rule: context may complete an assertion; it may not create one.**

Immediate context MUST NOT: (a) manufacture a deficiency predicate; (b) turn a descriptive statement into a deficiency merely through pragmatic implication; (c) infer theoretical inadequacy from the fact that a theory was developed for another context; (d) infer a gap from what the study subsequently does.

Operational locality (the co-text window) remains an implementation question (OD-1); the completion requirement — linguistic dependency resolution of a still-asserted deficiency, never pragmatic creation — is mandatory regardless of window size.

**Reconstruction decision.** OFF, everywhere in v1.2. Objectives, RQs, contribution claims, and methods MUST NOT be converted into gaps; downstream reasoning MUST NOT manufacture missing gap statements. A manuscript with no explicit positioning-gap claim yields an empty A.1-E set — and that emptiness is itself analytically valuable to A.1-A and Macro Alignment (a positioning finding), an additional architectural reason not to paper over it. If a future need for inferred positioning arises, it belongs in a **separate capability outside A.1-E** (e.g., "positioning inference" feeding A.1-A), whose outputs are typed as system inferences and never enter the A.1-E record space. Consequence: the spec's `status: explicit | reconstructed` field is replaced by the explicitness class above (§14 C-4).

---

## 8. Source-grounding contract `[REV v1.2 additions]`

Every record element carries exactly one traceability class:

- **Verbatim** — exact manuscript spans (claim spans, attributed-proposition spans, persistence-reason spans). Never edited.
- **Normalized-with-trace** — controlled restatements (the deficiency proposition) in which every content element is traceable to verbatim spans; templated to prevent free generation. Contextual restrictions appear in the normalized proposition as unclassified, span-traced segments — never as typed scope. `[REV v1.2]`
- **Referenced** `[REV v1.1]` — citation references MUST be resolved through the Citation Registry before the citation-link portion of the record counts as verified. An unresolvable citation is preserved verbatim and flagged `unresolved` with a review flag; it is never silently treated as linked.
- **Linked-provisional** — affected-object registry links; provisional until the Construct/Phenomenon Registry capability canonicalizes; the surface mention span always retained alongside.
- **Generated-flagged** — descriptors EpistemicOS writes (provisional object descriptors), explicitly marked as generated and grounded in the mention spans that motivated them.

**Proposition reconstructability principle `[REV v1.2]`:** the complete asserted deficiency proposition MUST be exactly reconstructable from its source spans. Contextual wording is never trimmed when its removal would alter the proposition as asserted — "No evidence exists about X among frontline workers" preserves "among frontline workers" in full, even though A.1-E assigns it no scope structure.

Principle: generated text never masquerades as source text; per-field traceability tags are mandatory `[SRC: spec §3 [Δ] per-field method]`. Offset mechanics are implementation, not contract.

---

## 9. Capability inputs `[REV v1.1]`

| Input | Class | Why |
|---|---|---|
| Document segmentation + section roles | **Hard dependency** | Positioning-scope routing is undefined without them; roles serve as priors and evidence (§3) |
| KB assets: KB-2 signals, KB-3 boundary cards, retained R-GAP rules, KB-5 identity rules (versioned) | **Hard configuration** | The extraction rules *are* these assets; version hash recorded in provenance |
| Citation Registry | **Hard dependency for citation-reference resolution** | Every citation reference used in an A.1-E record must resolve through the Registry, or be preserved verbatim with an `unresolved` review flag. A gap claim need not contain citations: absent citations, the `not_reported` / uncited-contrast state is valid and the Registry is simply not invoked for that record. |
| Construct / Phenomenon Registry | **Optional enrichment** | Provisional-object protocol exists by design; canonicalization is never a hard dependency and never gates extraction |
| Manuscript metadata (date, venue) | **Optional enrichment** | Time-indexes deficiency claims for downstream use |

**Scope / Context Extraction is neither an input nor a dependency of A.1-E** `[REV v1.2]`: the two capabilities run independently over the same segmentation and are joined only in the Research Object Graph.

**Coherence with the state model:** `source_linked` means every citation reference in the record has been through Registry resolution with a recorded per-reference outcome — `resolved`, or `unresolved` (verbatim preserved, review flag). `extraction_verified` additionally requires that unresolved references carry reviewer confirmation that the verbatim capture is faithful (§2.v). Records with no citations satisfy `source_linked` vacuously with `not_reported` where a contrast is absent.

---

## 10. Capability output (conceptual) `[REV v1.2]`

A per-manuscript set of study-positioning gap objects, each containing: spans with roles; boundary class GAP; explicitness class; the primitive triple `(relation, knowledge_kind, affected_object)`; the **preserved complete deficiency proposition** (minimum span set + normalized-with-trace restatement, contextual restrictions retained unclassified); contrast structure (cited works + attributed propositions, or `not_reported` + flag); persistence-reason attachments with assertion-triggered spawn links; claim-identity links; provisional object descriptors/links; per-field traceability tags; **observable status** — extraction state (`candidate → boundary_passed → structured → source_linked → extraction_verified`), verifier verdicts, verification basis, review flags, human-confirmation status where applicable; and provenance (detectors, model and rule versions).

Plus: the UNCERTAIN queue and diagnostic notices. Contains **no** taxonomy labels, no mode, no construction, **no structured scope/context fields of any kind** `[REV v1.2]`, no quality judgments, no numeric scores, and no mandatory confidence field. Calibrated confidence MAY later be added as operational review-prioritization metadata if validation data justifies it; it is not part of the v1.2 normative extraction object.

---

## 11. Downstream consumers and position within Research Structure `[REV v1.2]`

**Research Structure siblings and the Research Object Graph:**

```text
A.1-E Gap Extraction ─────────┐
                              │
Scope / Context Extraction ───┼──→ Research Object Graph
                              │
RQ Extraction ────────────────┤
                              │
Construct Extraction ─────────┘
```

A.1-E does not own Scope/Context. Links such as `Gap ↔ Scope`, `Gap ↔ RQ`, `RQ ↔ Scope` are produced downstream in the Research Object Graph from the separately extracted objects; no single extractor emits them.

**Consumers of the verified gap object `[REV v1.1]`:**

```text
                 A.1-E
          Verified Gap Object
            /       |       \
           ↓        ↓        ↓
        A.1-C     A.1-A    Macro Alignment
          |         |
          |         └── may consume A.1-C enrichment where useful
          |
          └── derived characterization
```

Principles:

- **A.1-E is the canonical source-grounded representation.** All consumers may read it directly.
- **A.1-C** derives characterization from the A.1-E object without modifying it; it receives the primitive A.1-E representation (with the preserved proposition and, once available in the graph, the linked Scope/Context object) and determines higher-order gap characterization under its own future contract. Whether that characterization is deterministic, rule-based, or model-based is not prejudged here.
- **A.1-A** may consume A.1-E directly and MAY additionally consume A.1-C outputs where the analysis requires them.
- **Macro Alignment** may consume A.1-E directly.
- **Contribution Analysis** may consume A.1-E directly.
- **Citation / literature validation** consumes A.1-E directly (contrast structure: refs + attributed propositions).

No consumer is required to access gaps "through A.1-C." Everything relocated to other capabilities remains reachable from the A.1-E object through provenance-preserving links.

---

## 12. Field disposition table `[REV v1.2 where noted]`

Decision legend: ACCEPT_EXISTING · MODIFY_EXISTING · MOVE_DOWNSTREAM · **MOVE_EXTERNAL** (relocation to a sibling Research Structure capability, joined later in the Research Object Graph) `[REV v1.2]`.

| # | Item | A.1-E | A.1-C | Other | Decision | Reason |
|---|---|:--:|:--:|:--:|---|---|
| 1 | verbatim gap span | ● | | | ACCEPT_EXISTING | Source grounding of the claim |
| 2 | restatement spans | ● | | | ACCEPT_EXISTING | Same claim, repeated; faithful counting |
| 3 | corroborating spans | ● | | | ACCEPT_EXISTING | Elaboration of one assertion |
| 4 | deficiency relation | ● | | | MODIFY_EXISTING | Paraphrase-faithful predicate class; vocabulary unified (C-1) |
| 5 | knowledge kind | ● | | | MODIFY_EXISTING | Same; `unspecified` added (§5) |
| 6 | affected object | ● | | | MODIFY_EXISTING | Referent of the assertion; artifact kinds added; **not a scope container (§5)** `[REV v1.2]`; canonical ID stays with Registry capability |
| 7 | scope (population, setting, geography, level, temporal) | | | Scope/Context Extraction | **MOVE_EXTERNAL** `[REV v1.2]` | Separately owned Research Structure object; A.1-E preserves the wording in the proposition, never the structure |
| 8 | contrasted prior knowledge | ● | | | ACCEPT_EXISTING | The explicit contrast is part of the claim |
| 9 | citation references | ● | | | MODIFY_EXISTING | Hard Registry resolution; unresolved → verbatim + flag (§8, §9) `[REV v1.1]` |
| 10 | proposition attributed to cited work | ● | | | ACCEPT_EXISTING | The manuscript's assertion about the cited work |
| 11 | persistence reasons | ● | | | MODIFY_EXISTING | Explicit claims about the gap; spawn only on asserted deficiency `[REV v1.1]` |
| 12 | provisional object identity | ● | | | ACCEPT_EXISTING | R-GAP-OBJ; extraction must not block on registry maturity |
| 13 | gap merge identity (within manuscript) | ● | | | MODIFY_EXISTING | Triple + proposition equivalence, conservative; contextual ambiguity → `possibly_same_claim` `[REV v1.2]` |
| 14 | facets / descriptive qualifiers | ● | | | MODIFY_EXISTING | **Structure removed** `[REV v1.2]`: wording preserved in proposition spans; research-scope qualifiers owned by Scope/Context |
| 15 | `knowledge_void` | | ● | | MOVE_DOWNSTREAM | Classification over primitives; A.1-C's contract |
| 16 | `contradictory_evidence` | | ● | | MOVE_DOWNSTREAM | Same |
| 17 | `evaluation_void` | | ● | | MOVE_DOWNSTREAM | Same |
| 18 | `theory_application_void` | | ● | | MOVE_DOWNSTREAM | Same |
| 19 | `methodological_gap` | | ● | | MOVE_DOWNSTREAM | Same |
| 20 | `action_knowledge_conflict` | | ● | | MOVE_DOWNSTREAM | Same |
| 21 | `population_context_gap` | | ● | | MOVE_DOWNSTREAM | Same; population content reaches A.1-C via the preserved proposition and the Scope/Context object, not via A.1-E structure `[REV v1.2]` |
| 22 | `level_of_analysis_gap` | | ● | | MOVE_DOWNSTREAM | Same; level/context information is owned by Scope/Context; A.1-E preserves wording only `[REV v1.2]` |
| 23 | `mode: incomplete` | | ● | | MOVE_DOWNSTREAM | Rhetorical stance, not assertion content |
| 24 | `mode: inadequate` | | ● | | MOVE_DOWNSTREAM | Same |
| 25 | `mode: incommensurate` | | ● | | MOVE_DOWNSTREAM | Same; extraction covers it via relation `CHALLENGED` |
| 26 | `construction: confusion_spotting` | | ● | | MOVE_DOWNSTREAM | Question-construction analytics |
| 27 | `construction: neglect_spotting` | | ● | | MOVE_DOWNSTREAM | Same |
| 28 | `construction: application_spotting` | | ● | | MOVE_DOWNSTREAM | Same |
| 29 | `construction: problematization` | | ● | | MOVE_DOWNSTREAM | Same |
| 30 | whether the gap actually exists | | | A.1-A | MOVE_DOWNSTREAM | Scientific truth |
| 31 | whether the gap is important | | | A.1-A | MOVE_DOWNSTREAM | Merit judgment |
| 32 | whether the gap is novel | | | A.1-A | MOVE_DOWNSTREAM | Merit judgment |
| 33 | whether cited literature supports the gap | | | Literature/Citation validation | MOVE_DOWNSTREAM | Retrieval + assessment beyond the manuscript |
| 34 | whether the RQ follows from the gap | | | Macro Alignment | MOVE_DOWNSTREAM | Cross-object alignment (link objects live in the Research Object Graph) |
| 35 | whether the design addresses the gap | | | Macro Alignment | MOVE_DOWNSTREAM | Cross-object alignment |
| 36 | whether the contribution corresponds to the gap | | | Contribution Analysis | MOVE_DOWNSTREAM | Cross-object alignment |
| 37 | whether the study fills the gap | | | Contribution Analysis | MOVE_DOWNSTREAM | Outcome judgment |

One primary destination per item. Items relocated elsewhere remain reachable from the A.1-E object through provenance-preserving links; consumers read A.1-E directly (§11).

---

## 13. Existing artefacts retained `[REV v1.2 where noted]`

| Artefact | Disposition | Note |
|---|---|---|
| KB-1 typology cards | MOVE_DOWNSTREAM (→ A.1-C) | Cards' detection-useful signals migrate into KB-2 first; distinguish-from notes are characterization material |
| KB-2 signal lexicon | RETAIN | A.1-E detection asset |
| KB-3 boundary cards (B1–B5) | RETAIN_WITH_MODIFICATION | B1–B4 unchanged in role; B5 keeps the boundary rule (assumption-challenge = GAP, relation `CHALLENGED`) and sheds its mode-label tail |
| KB-4 R-GAP rules | RETAIN_WITH_MODIFICATION | Stay in A.1-E: VS-MOTIVATION; SCOPE (re-scoped to positioning contexts `[REV v1.1]`); LIM; CONTRAST (as integrity flag); MULTI (redefined on triple + proposition equivalence `[REV v1.2]`); REASON (spawn condition tightened `[REV v1.1]`); OBJ; RECONSTRUCT (as prohibition); ESCALATE. Move to A.1-C: CLOSED-SET (enum enforcement) |
| KB-5 merge rules + predicate classes | RETAIN_WITH_MODIFICATION | Predicate-class pair retained as primitive; identity rule replaced by the conservative proposition-equivalence test `[REV v1.2]`; the head test leaves A.1-E — its subject matter (object vs scope) is now the OD-3 coordination boundary; worked pairs involving scope facets require re-derivation |
| KB-6 escalation | RETAIN | UNCERTAIN pathway |
| KB-7 / KB-7b | RETAIN_WITH_MODIFICATION | Correction error taxonomy must be split per capability: boundary/span/primitive/merge errors test A.1-E; type/mode errors test A.1-C; scope errors test Scope/Context `[REV v1.2]` |
| Object schema (spec §3) | RETAIN_WITH_MODIFICATION | Strip `types` axes, `primary_content`, `type_proposal` (→ A.1-C); replace `status` with explicitness class; extend object referents per §5; **no structured scope/context or qualifier fields** `[REV v1.2]`; remove mandatory confidence field `[REV v1.1]` |
| State machine | RETAIN_WITH_MODIFICATION | `filtered` → `boundary_passed`; terminal state → `extraction_verified`; `source_linked` semantics defined in §9 `[REV v1.1]` |
| Verification section (spec §7) | RETAIN_WITH_MODIFICATION | Span, positioning-context, template, citation-resolution, objective-distinctness (as CONTRIBUTION-leak flag), completeness validators stay; **proposition-reconstructability validator added** `[REV v1.2]`; enum-compliance validator moves to A.1-C; acceptance criteria split per capability |
| Confidence semantics (spec §8) | REMOVE_FROM_A1-E (as a mandatory record field) `[REV v1.1]` | Numeric-score prohibition retained as constraint; observable status replaces bands; calibrated confidence MAY return later as operational review-prioritization metadata |

---

## 14. Architectural conflicts discovered

**C-1** — Relation vocabulary drift: spec §3 template `ASSUMPTION_CHALLENGED`, `PRACTICE_DISCONNECTED` vs rulebook §5 `CHALLENGED`, `DISCONNECTED` inside the pair. *Resolution:* rulebook vocabulary; spec template rewritten. **MODIFY_EXISTING.**

**C-2** — Flat predicate-class list (spec) vs composite pair (rulebook, logged as [Δ-spec] but never applied back). *Why:* flat `ABSENT` wrongly merges evidence-absence with theory-absence. *Resolution:* composite pair as primitive. **MODIFY_EXISTING.**

**C-3** — Tie-break rule: spec "most specific" vs rulebook head-of-claim. *Resolution:* head-of-claim; the taxonomy-primary decision is A.1-C's; under v1.2 the head test's remaining subject matter (object vs scope) moves to the OD-3 coordination boundary. **MODIFY_EXISTING `[REV v1.2 note]`.**

**C-4** — Spec schema advertises `status: reconstructed` while its rules disable reconstruction. *Resolution:* explicitness class; reconstruction removed from the record space. **MODIFY_EXISTING.**

**C-5** — Both files restrict `affected_object` to registry/phenomenon referents, yet evaluation-void and assumption-challenge claims require knowledge-artifact referents. *Resolution:* extend referent kinds with `about` links. **MODIFY_EXISTING.**

**C-6** — Both files place taxonomy, mode, and construction inside the "extraction-safe" module vs the E/C/A separation. *Resolution:* wholesale relocation (items 15–29). **MOVE_DOWNSTREAM.**

**C-7** — KB-7b's error taxonomy mixes capability layers. *Resolution:* partition per capability; one review pass, routed codes. **MODIFY_EXISTING.**

**C-8** — Spec OI-5: front-end anchoring vs later restatements. *Resolution:* primary span in a positioning context; restatement/corroborating spans anywhere; validator checks the primary only. **ACCEPT_EXISTING (formalized).**

**C-9 `[REV v1.1]`** — v1.0's `context_supported` admitted causal/consequence readings — pragmatic implication — while banning inference; Case F's spawned record instantiated the contradiction. *Resolution:* completion-not-creation rule; Case F rehandled; spawn tightened. **MODIFY_EXISTING.**

**C-10 `[REV v1.1]`** — v1.0 mandated uncalibrated confidence bands while the project's own principle conditions confidence semantics on calibration. *Resolution:* observable status replaces mandatory confidence. **MODIFY_EXISTING.**

**C-11 `[REV v1.1]`** — v1.0 routed analysis capabilities "through A.1-C" while declaring A.1-E canonical. *Resolution:* direct consumption for all; A.1-C optional enrichment. **MODIFY_EXISTING.**

**C-12 `[REV v1.1]`** — v1.0 claimed "every deficiency claim" while zoning to front-end contexts. *Resolution:* study-positioning definition; zoning becomes derivative. **MODIFY_EXISTING.**

**C-13 `[REV v1.2]`**
Conflict: v1.1 made A.1-E extract, type, and canonicalize identity-bearing scope (population, setting, geography, level, temporal) — including salience flags and scope-based merge identity — while the Research Structure defines Scope/Context as a separately owned object with its own extraction capability.
Source: v1.1 §5/§10/§16 vs the Research Structure architecture (document 6).
Why it matters: duplicate ownership forks scope representation — A.1-E would classify research scope under its own ad-hoc rules, diverging from the Scope/Context capability's, and the Research Object Graph would inherit two incompatible scope models; scope-based merge keys would also bake A.1-E's scope judgments into claim identity.
Recommended resolution: scope removed from A.1-E primitives, object, qualifiers, salience, and identity; contextual wording preserved via full-proposition source grounding; identity redefined as triple + conservative proposition equivalence with `possibly_same_claim` fallback; Gap ↔ Scope produced in the Research Object Graph after independent Scope/Context extraction. The former OD-3 (salience flag) is withdrawn as moot and replaced by the object-vs-scope boundary (new OD-3).
Status: **MODIFY_EXISTING.**

---

## 15. Open decisions

**OD-1 — Co-text window for `context_supported`.** The completion-not-creation rule is frozen and window-independent (§7); the operational window is an implementation parameter best set from KB-7b correction data. Default in force: same paragraph.

**OD-2 — Reported calls for research.** "Scholars have called for more research on X" is currently a GAP candidate (rulebook B1, an authored choice the sources do not settle). Default in force: GAP with the calling works as contrast; explicitly subject to reversal by KB-7b elicitation evidence.

**OD-3 `[REV v1.2]` — Object vs scope boundary.** Whether wording like "network-level effects" belongs to the affected object (it names the claimed unknown) or is a contextual restriction (preserved-only) cannot be fully operationalized inside A.1-E alone; it requires coordinated boundary rules between A.1-E and Scope/Context Extraction. Defaults in force: wording that names the phenomenon itself (compound head noun phrase) stays in `affected_object`; wording that restricts an otherwise-named object ("about X *among Y*", "*in remote teams*") is preserved-only; genuinely uncertain cases take the narrower object reading plus review flag `object_scope_boundary`. The full object-vs-scope rulebook is deliberately not created here. (The v1.1 OD-3 — scope salience flag — is withdrawn as moot under C-13.)

(Not open: spec OI-1 on `level_of_analysis_gap`. Under v1.2, A.1-E never structurally extracts level at all; whether A.1-C retains a level-related enum value is a question for A.1-C in coordination with Scope/Context.)

---

## 16. Frozen A.1-E contract `[REV v1.2]`

1. A.1-E MUST extract every explicit or context-supported **study-positioning** gap claim — deficiencies in prior knowledge forming part of the manuscript's stated rationale or positioning for the present research — from the eligible positioning contexts (abstract, introduction, literature review, theory / conceptual development), and MUST attach later restatements of those claims as restatement spans wherever they occur.
2. A.1-E MUST NOT be read or implemented as extracting every knowledge deficiency appearing anywhere in the manuscript; deficiencies arising only after the study (own limitations, new future-research needs) MUST be routed to the Limitations / Future-Research capability.
3. A.1-E MUST represent each claim with: spans (roles), boundary class GAP, explicitness class, relation, knowledge_kind, affected object (surface form mandatory; registry link provisional), the preserved complete deficiency proposition (minimum span set plus normalized-with-trace restatement with contextual restrictions retained unclassified), contrast structure, persistence-reason attachments, claim links, per-field traceability tags, observable status (extraction state, verifier verdicts, verification basis, review flags, human-confirmation status), and provenance.
4. A.1-E MUST NOT structurally extract, classify, canonicalize, registry-link, or otherwise own research scope/context — population, setting/context, geography, level of analysis, temporal scope, or other research-scope dimensions; these belong to Scope/Context Extraction. A.1-E MUST preserve all such wording within the proposition's source spans and MUST NOT trim contextual wording whose removal would alter the proposition as asserted.
5. A.1-E MUST NOT emit taxonomy labels, mode labels, construction labels, scope classifications, or any judgment of gap existence, importance, novelty, literature support, alignment, or fulfilment.
6. A.1-E MUST NOT convert objectives, research questions, contribution claims, or methods into gap records, and MUST NOT manufacture missing gap statements. Emission classes are limited to `explicit` and `context_supported`.
7. Context MAY complete an assertion (referential dependence, ellipsis, omitted arguments, other linguistic dependency) and MUST NOT create one: no manufactured deficiency predicates, no pragmatic-implication conversion of descriptive statements, no inferring theoretical inadequacy from a theory's origin context, no inferring gaps from what the study subsequently does.
8. A.1-E MUST emit the empty set when a manuscript makes no explicit positioning-gap claim, and MUST NOT compensate for that emptiness.
9. A.1-E MUST spawn a linked candidate claim from a persistence reason **only when the reason itself asserts a prior-knowledge deficiency** (directly, or via clause-7 linguistic completion); causal implication alone MUST NOT spawn; asserted-deficiency reasons MUST NOT be silently demoted.
10. A.1-E MUST merge records only when equivalence of the complete asserted deficiency proposition is clear from the manuscript without performing scope/context classification — identity test: `(affected_object, relation, knowledge_kind)` plus source-grounded proposition equivalence, applied conservatively. Where contextual differences may affect claim identity and cannot be resolved without scope extraction, A.1-E MUST NOT merge and MUST link `possibly_same_claim`; final contextual identity MAY be resolved downstream in the Research Object Graph.
11. `affected_object` MUST identify what the deficient knowledge is about and MUST NOT be used as a container for research scope/context wording; uncertain object-vs-scope cases take the narrower object reading with review flag `object_scope_boundary` (OD-3).
12. A.1-E MUST ground every record element in exactly one traceability class (§8); generated descriptors MUST be flagged as generated; normalized text MUST be fully span-traceable; the complete asserted deficiency proposition MUST be exactly reconstructable from its source spans.
13. A.1-E MUST resolve every citation reference through the Citation Registry; unresolvable citations MUST be preserved verbatim and flagged `unresolved` for review, never silently treated as linked; records without citations MUST use the `not_reported` / uncited-contrast state where appropriate.
14. A.1-E MUST emit UNCERTAIN for boundary-undecidable candidates and MUST NOT coerce them.
15. A.1-E MAY mint provisional object descriptors and MAY link provisionally to the Construct/Phenomenon Registry; it MUST NOT block on that registry's maturity and MUST NOT finalize canonical identity.
16. A.1-E MAY attach diagnostic notices (e.g., presupposed-gap-without-antecedent) carrying no deficiency content.
17. A.1-E MUST NOT emit numeric confidence scores or performance thresholds, and MUST NOT require any confidence field on the extraction object; calibrated confidence MAY later be introduced as operational review-prioritization metadata if validation data justifies it, outside the normative object.
18. `extraction_verified` MUST certify only faithful representation of an explicit study-positioning manuscript claim (§2) and MUST NOT be interpreted as any scientific verdict about the claim.
19. A.1-E is the canonical source-grounded representation: A.1-C, A.1-A, Macro Alignment, Contribution Analysis, and Citation/literature validation MAY each consume it directly; no consumer is required to route through A.1-C; cross-object links (Gap ↔ Scope, Gap ↔ RQ, RQ ↔ Scope) are produced downstream in the Research Object Graph from separately extracted objects and MUST NOT be emitted by A.1-E; everything relocated elsewhere MUST remain reachable through provenance-preserving links.

---

## Quality test report `[REV v1.2 additions]`

- **Case A** — "Little is known about how X affects Y." → GAP, `explicit`, `(LIMITED, evidence)` about `relationship(X,Y)`; full proposition preserved. Clean.
- **Case B** — "X has become increasingly important to organizations." → MOTIVATION (world-state predicate); no record. Clean.
- **Case C** — "Existing studies rely almost exclusively on cross-sectional designs." → Alone: **OTHER**. Becomes GAP `(CONSTRAINED, method)` only when the passage explicitly asserts a knowledge deficiency (in-span consequence predicate or adjacent asserted-deficiency sentence); implication never suffices. Clean.
- **Case D** — "This study extends research on X." → CONTRIBUTION; no record; no reconstruction. Clean.
- **Case E** — "Previous theories assume X, but this assumption is fundamentally mistaken." → GAP, `explicit`, `(CHALLENGED, theory)` about `assumption(X)` [knowledge-artifact referent]; contrast = uncited "previous theories" (descriptor, flag). Clean.
- **Case F** — "No evidence exists for X, because existing theories were developed for Y." → One record: `(ABSENT, evidence)` about X; because-clause = persistence reason (provenance, no spawn). Spawn only on additionally asserted inadequacy ("not built for X", "cannot account for X"). Clean.
- **Case G `[REV v1.2]`** — "Evidence about employee engagement is limited among frontline workers." → GAP, `explicit`, `(LIMITED, evidence)`, `affected_object = employee engagement`. **No population field is created**; "among frontline workers" is preserved intact in the proposition spans and normalized restatement (unclassified). Scope/Context Extraction owns its structuring. Clean.
- **Case H `[REV v1.2]`** — "The relationship between autonomy and performance remains unexamined in remote teams." → GAP, `explicit`, `(ABSENT, evidence)`, `affected_object = relationship(autonomy, performance)`; "in remote teams" preserved-only. Clean.
- **Case I `[REV v1.2]`** — "Network-level effects remain poorly understood." → GAP, `explicit`, `(LIMITED, unspecified)`; here the level wording names the claimed unknown itself, so `affected_object = network-level effects` — it is not mechanically stripped. Uncertain object-vs-scope cases take the narrower reading + `object_scope_boundary` flag (OD-3). Clean under the stated boundary.
- **Case J (merge) `[REV v1.2]`** — "No evidence exists about X among frontline workers" vs "No evidence exists about X among senior managers." → Identical triple `(ABSENT, evidence, X)`; propositions clearly non-equivalent in asserted wording → **no merge**, two records, `possibly_same_claim` link; contextual identity resolvable only after Scope/Context extraction, in the Research Object Graph. Clean — and demonstrates why the bare triple was rejected as an identity key.

**Unresolved cases: none**, conditional on the §5 amendments, the §7 completion-not-creation rule, and the §5/OD-3 object-vs-scope boundary defaults being adopted as part of this contract.

---

## v1.2 Freeze Check

**Carried forward from v1.1 (re-audited):**

| Check | PASS/FAIL | Evidence |
|---|---|---|
| Capability scope internally consistent | PASS | §1 positioning definition; §3 positioning-scope operation; §6 FUTURE_RESEARCH routing; §16 clauses 1–2; no "every deficiency anywhere" wording |
| Extraction vs characterization separated | PASS | §4; §12 items 15–29 → A.1-C; §16 clause 5; only primitive relation values remain |
| Extraction vs scientific analysis separated | PASS | §2 three-truth definition; §4; §12 items 30–37; §16 clauses 5, 18 |
| Explicitness rule prevents reconstruction | PASS | §7 `inferred`/`reconstructed` = NEVER; C-4; §16 clauses 6, 8; empty set valid |
| Context-supported rule prevents inferred gaps | PASS | §7 completion-not-creation + four MUST NOTs; §16 clause 7; Cases C and F |
| Dependencies consistent with state model | PASS | §9 Citation Registry hard for resolution; per-reference `source_linked` semantics; §2.v |
| A.1-E remains canonical downstream source | PASS | §11 consumer diagram; C-11 resolved; §16 clause 19 |
| No uncalibrated confidence required | PASS | §10 observable status; §13 confidence row; §16 clause 17 |

**New in v1.2:**

| Check | PASS/FAIL | Evidence |
|---|---|---|
| A.1-E does not own research scope/context | PASS | §4 first row; §5 primitive = triple; §16 clause 4; C-13 |
| No population/geography/level/time scope fields remain in A.1-E | PASS | §5 scope row removed; §10 "no structured scope/context fields of any kind"; §12 item 7 MOVE_EXTERNAL; §13 object-schema row; qualifier structure removed (item 14) |
| Full contextual wording remains source-grounded | PASS | §3 full-proposition preservation operation; §8 proposition-reconstructability principle; §2(iii); §16 clauses 4, 12; Cases G, H |
| Affected object is not used as a disguised scope container | PASS | §5 object row (Examples A/B pattern); §16 clause 11; Cases G, H vs Case I boundary; OD-3 defaults + `object_scope_boundary` flag |
| Merge cannot collapse contextually distinct gap claims | PASS | §5 identity rule (triple explicitly rejected as sufficient); §16 clause 10; Case J two-record outcome |
| Scope / Context has one clear owner in Research Structure | PASS | §11 Research Structure diagram; §9 independence note; §4 MOVE_EXTERNAL row; C-13 resolution |
| Research Object Graph can link Gap ↔ Scope later | PASS | §11 graph diagram and link statement; §16 clauses 10, 19 (`possibly_same_claim` defers contextual identity to the graph) |

**All checks PASS — the A.1-E Gap Extraction Contract is declared FROZEN at v1.2.**
