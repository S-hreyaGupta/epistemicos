# A.1-E Object Rules v1.1 — EpistemicOS (Step 8)

**Status:** normative once the Freeze Check (§41.49) passes. Version string: `A1E-OR-1.1`.
**Pinned frozen inputs:** contract v1.2 · schema `A1E-GS-1.3` · protocol v1.2 · state machine v1.3 · `A1E-BR-1.2` · `A1E-DPR-1.1` · `A1E-SL-1.1`. Steps 1–7 are never reinterpreted here.

**Revision record (v1.0 → v1.1) — exactly these corrections:** 1. pinned schema updated from A1E-GS-1.2 to A1E-GS-1.3; 2. existing non-measure methodological artifacts now use artifact_kind = method; 3. SI-OR-1 unresolved routing removed; 4. scope ownership made invariant to pre-head/post-head realization; 5. population/context premodifiers no longer automatically enter object; 6. normative test schema normalized to legal enum/meta-values; 7. conditional tests split into deterministic cases; 8. mention.surface_form restored to strict verbatim source spans; 9. completion data separated from mention/normalized_text; 10. §41.40 made exhaustive for all normative OR-* IDs. No other Step-8 semantics changed.

**Final-issuance correction record (same version):** 1. coreference/completion aligned with frozen GS-1.3 I-44/I-45; 2. carrier/gap-reference anaphors now resolve to antecedent affected objects; 3. object-denoting anaphors remain local canonical mentions where licensed; 4. unresolved-object tests aligned with §41.4; 5. normative test schema closed to explicit legal/meta-values; 6. `pa` aliases replaced with `practice_alignment`; 7. compound/non-enum GIVEN values removed; 8. stale SI-OR-1 validation language removed; 9. registry-count evidence corrected to the actual row count; 10. no other Step-8 semantics changed.

**Final mechanical correction record (same version):** 1. OT-AMB-10 `given=` value normalized to the closed test schema; 2. stale `OR-COREF` shorthand in OT-COR-01 replaced by `OR-COREF-1 Branch A`; 3. obsolete `OR-COREF rule 6/7` in OT-COR-07 replaced by `OR-COREF-1 Branch D`; 4. OR-UNCERTAIN-3 examples restricted to genuine affected-object ambiguity; 5. OT-AMB-05 preserved as the counterexample where the affected object is resolved but a predicate-side complement is ambiguous; 6. no Step-8 semantics changed.

## 41.1 Purpose and ownership boundary

Step 8 answers exactly one question: **"What source-grounded thing is the manuscript asserting to be deficient?"** It owns the extraction and representation rules for `affected_object` within the frozen semantic primitive `(relation, knowledge_kind, affected_object)`. Step 5 owns the boundary class; Step 6 owns `relation` and `knowledge_kind` (both arrive here as GIVEN inputs); Step 9 owns merge and gap identity; Step 10 owns candidate emission.

Step 8 MAY determine: affected-object span; referent kind; source-grounded object wording; minimal normalized representation; explicit relationship arguments (internal metadata); licensed `about`; permitted linguistic completion; object-level traceability; extraction uncertainty. Step 8 MUST NOT determine: canonical gap identity; object equivalence; synonym resolution; object/gap merging; duplicate detection; proposition equivalence; scientific validity; novelty; scope/context classification; relation; knowledge_kind; candidate emission; Step-5 boundary class.

## 41.2 Frozen inputs and dependencies

Every Step-8 decision presupposes: a proposition unit (Step-1 contract), its Step-5 class, and its Step-6 `(relation, knowledge_kind)` result. The Gap Object Schema `A1E-GS-1.3` is the canonical field authority: its names are `object_kind` and `artifact_kind` (this document's normative names), while the build-prompt aliases `referent_type`/`artifact_subtype` are treated as synonyms for those canonical fields and never added to the schema. Schema invariants binding Step 8: mention is required, verbatim, source-grounded or completion-recoverable (I-9b), and never a scope container (I-9); `artifact_kind` is required iff `object_kind = knowledge_artifact` and absent otherwise (I-10) — no null subtype exists, and the enum now includes `method` (GS-1.3); `type_trace_refs` ≥1 (I-40); generated descriptors can never ground an object (I-41); `about` is optional, knowledge_artifact-only, verbatim + refs (I-28, I-42); object-denoting vs carrier/reference anaphor completion is schema-frozen (I-44) and mention-span coherence is schema-frozen (I-45) — Step 8 implements both exactly and never reinterprets them.

## 41.3 Affected-object ontology (frozen)

`object_kind ∈ { construct, phenomenon, relationship, knowledge_artifact }`.
`artifact_kind ∈ { proposition, theory, model, framework, assumption, measure, method }` — required iff `object_kind = knowledge_artifact` (GS-1.3).

No additional top-level kinds are introduced. The following are NEVER independent affected-object kinds: population, context, setting, geography, sample, industry, country, time period, methodology, practice. A methodology is representable through `measure` where it genuinely is a measurement resource (§41.19), or through `method` where it is an existing non-measure methodological artifact bearing the deficiency (§41.20); categorical absences of a method class never fabricate an artifact object (OR-ART-7a). Practice appears only inside practice-alignment objects as a relational pole or process participant (§41.32), never as its own object kind.

## 41.4 Object record

Canonical production fields (schema-owned; Step 8 populates, never modifies): `affected_object.object_kind` · `artifact_kind` (iff knowledge_artifact) · `type_trace_refs` · `mention` (`surface_form`, `mention_span_refs`, optional `generated_descriptor` — label only, never a referent substitute) · `about` (`surface_form`, `mention_span_refs`).

Step-8 INTERNAL extraction metadata (class B; never silently added to the canonical record): `head` (grammatical head lexeme) · `modifiers` (object-internal only) · `relationship_arguments` (`argument_1`, `argument_2`, `predicate`, `direction ∈ {directed_a1_to_a2, undirected}`, `relational_qualifier`, `args_complete ∈ {complete, partial}`) · `completion_status ∈ {local, context_completed, unresolved}` · `completion_trace_refs` · `coordination_present ∈ {true, false}` · `normalized_text`.

Nullability: `about` absent unless licensed (§41.21); `relationship_arguments` present iff `object_kind = relationship`; `completion_trace_refs` present iff `completion_status = context_completed`; `artifact_kind` per I-10; `relational_qualifier` present only when explicit higher-order wording exists (§41.12). `completion_status = unresolved` routes per §41.25/§41.48 and produces no canonical object.

## 41.5 Source-groundedness

Every affected object is grounded in manuscript wording. Prohibited grounds: research objective, RQ, hypothesis, contribution statements, methods sections, later discussion, scientific background knowledge, ontology/registry knowledge, likely author intent. Permitted: linguistic completion from frozen permitted context (schema `context_support` dependency types: anaphora, ellipsis, omitted_argument, referential_dependency, other_linguistic_dependency) — only to resolve an argument already asserted in the deficiency proposition. **Hard rule (OR-TRACE-1): context may complete the referent; context may not create the referent.** Semantic invention is prohibited everywhere. *Clarification (I-44):* source-grounded completion may take the canonical mention wording from a permitted antecedent/support span — this does not violate source-groundedness. The canonical mention may therefore originate from (A) the local deficiency span or (B) a permitted antecedent span, as I-44 directs per anaphor class; in both cases `mention.surface_form` is verbatim manuscript wording, and no generated paraphrase may ever become the canonical mention.

## 41.6 Minimal-sufficient-object rule

**OR-TARGET-2.** The affected object is the smallest source-grounded expression that still identifies what is asserted to be deficient. Deterministic tests: (a) *removal test* — a candidate token belongs to the object iff removing it changes which referent bears the deficiency (not merely where/when/for-whom it holds); (b) *carrier test* — knowledge-kind carrier wording never enters the object (§41.22); (c) *scope test* — post-head adjuncts failing the removal test are scope (§41.7, §41.31). Over-extraction (carrier or scope inside mention) and under-extraction (dropping constitutive modifiers or relationship arguments, §41.30) are both errors (E-OVEREXTRACTION / E-UNDEREXTRACTION, §41.46). Example: "Little is known about how digital surveillance affects employee trust in remote teams." → object = relationship(digital surveillance, employee trust); "in remote teams" is scope; "Little is known about" is carrier.

## 41.7 Scope/context exclusion

A.1-E does not own structured scope/context. NEVER extracted into `affected_object` (and never emitted as structured fields anywhere in A.1-E): population, participant group, organizational context, industry, setting, geography, temporal context, level of analysis, sample characteristics. Such wording remains linguistically present in the preserved complete proposition (schema `proposition` block), owned by the separate Research Structure Scope/Context capability. Step 8 distinguishes object-internal content from external qualification; it does not classify scope itself.

**FROZEN PRINCIPLE — scope ownership is invariant to syntactic position.** A population/context modifier remains scope whether realized post-head ("engagement among nurses") or pre-head ("nurse engagement"). Surface position alone never converts scope into object identity.

- **OR-SCOPE-1 (post-head adjunct test).** A post-head adjunct PP headed by among / in / across / within / during / over / at + a population, setting, industry, geography, or time NP is external scope and is excluded from mention.
- **OR-SCOPE-2 (constitutive-only rule; replaces the retired pre-head-position rule).** A modifier/complement is object-internal ONLY when it is constitutive of the deficient referent — removing it changes WHAT construct/phenomenon is denoted, not merely where/when/for-whom it occurs. Pre-head position is NEVER sufficient evidence of constitutiveness.
- **OR-SCOPE-3 (position invariance).** Population, bearer group, organizational setting, industry, geography, temporal setting, and level of analysis are external scope in every syntactic realization — prenominal, genitive ("Spanish firms' trust" → object "trust"), compound, or adjunct.
- **OR-SCOPE-PRE-1 (premodifier paraphrase/removal test).** For modifier M on head H: if M can be interpreted solely as "H among/in/within/across/during/at M" AND removing M leaves the same core construct/phenomenon being studied, M is external scope: "nurse engagement" ≈ engagement among nurses → object "engagement", nurse = population scope; "SME leadership" ≈ leadership in SMEs → object "leadership"; "multinational-firm trust" → object "trust". *Sense-fixing carve-out:* a generic-bearer premodifier that fixes WHICH construct sense is denoted (bare head polysemous) is constitutive, not scope — "employee engagement" (bare "engagement" is sense-ambiguous; "employee" fixes the work-attitude construct) and "employee trust" are retained whole; a proper-subgroup premodifier within an already-fixed sense (nurse, SME, Spanish-firm) is scope. Lexicalization as a distinct construct is never assumed from the phrase alone; it requires explicit source-grounded evidence (e.g., the manuscript defines "nurse engagement" as a distinct construct).
- **OR-SCOPE-4 (ambiguity safety rule).** When linguistic evidence cannot distinguish constitutive content from scope/context without interpretive invention: use the minimal core object; preserve the complete proposition; flag unresolved scope attachment for review; never add the disputed material to affected_object. No structured scope field is ever emitted.

Example: "Evidence about employee engagement is limited among frontline workers." → relation LIMITED · kind evidence · mention "employee engagement" · proposition preserved in full · no population field exists.

## 41.8 Construct

**OR-CONSTRUCT-1.** A construct is a named or clearly delimited conceptual variable/category — a property, attitude, capacity, state-quality, or classificatory concept attributable to entities — whose deficiency concerns knowledge about that conceptual entity itself: "employee engagement", "organizational resilience", "absorptive capacity", "trust", "ethical climate", "commitment", "job satisfaction". "Little is known about organizational resilience." → construct("organizational resilience"). No Research Structure registry membership is required; theoretical legitimacy is never validated; synonymous constructs are never merged (Step 9 territory).

**OR-TYPE-2 (construct vs phenomenon head rule).** Classify by the grammatical head's reading in the proposition: a *stative attribute/variable* head (trust, engagement, commitment, capacity, climate, quality, intention, satisfaction, resilience-as-capacity) → construct; an *eventive/process/pattern* head (adaptation, integration, transformation, responses, hiding, diffusion, emergence, dynamics, differences-as-pattern) → phenomenon. Deverbal morphology (-tion/-ing/-ment) signals phenomenon only under an occurrence/process reading; stative-attitude readings (engagement, commitment) remain constructs. If both readings are genuinely live in the local proposition and nothing in it disambiguates → `E-OBJECT-TYPE` risk; route per §41.25 only if extraction itself is blocked, otherwise prefer the reading selected by the deficiency predicate's own complement structure and record the alternative in review notes.

## 41.9 Phenomenon

**OR-PHEN-1.** A phenomenon is a process, event, behavior, condition, pattern, or empirical/theoretical occurrence not better represented as a single construct, an explicit relationship, or a named knowledge artifact: "collective adaptation", "post-merger integration", "digital transformation", "knowledge hiding", "organizational responses to disruption". **OR-PHEN-2 (nominalized-relationship guard).** "X responses to Y" and similar nominal compounds are phenomena by default; they become relationships only when relational semantics are actually asserted by the proposition's structure (§41.10): "Little is known about employee responses to algorithmic monitoring." → phenomenon("employee responses to algorithmic monitoring"); "Little is known about how employees respond to algorithmic monitoring." → relationship(algorithmic monitoring, employee responses) — the wh-complement over a relational predicate asserts the relation.

## 41.10 Relationship

**OR-REL-1 (activation).** `object_kind = relationship` iff the deficient content is knowledge about an asserted relation between two or more entities, activated by exactly one of: (i) a wh-/whether-complement over a relational predicate ("how X affects Y", "whether X predicts Y"); (ii) an explicit relational nominal with both arguments ("the relationship/association/link/effect/impact/interaction between/of X and/on Y"); (iii) an explicit two-argument relational clause under the knowledge carrier ("few studies examine whether X shapes Y"). Canonical payload: `mention.surface_form` = the minimal verbatim source span expressing the relational content (the wh/whether-clause, the relational nominal phrase, or — when the disrelation is predicate-expressed, as in practice-alignment pattern D — the verbatim relational clause; this clause-span license is the single consistent representation used by §41.32); internal metadata: relationship_arguments per §41.4. No relational activation → §41.8/41.9 kinds apply. Relational semantics are never invented from co-mention: "Little is known about X and Y." is coordination (§41.28), not relationship.

## 41.11 Relationship arguments and direction

**OR-REL-2 (arguments).** argument_1/argument_2 are the source-grounded argument phrases, each with spans; internal only (the canonical record carries the mention phrase + trace). **OR-REL-3 (direction).** Direction is represented only when linguistically asserted: "effect of X on Y" / "X affects|predicts|influences|drives|shapes|causes Y" → directed X→Y; "association/relationship/link/interaction between X and Y" → undirected; "correlates with" → undirected. Direction is NEVER inferred from RQ order, hypothesis order, theory, or common knowledge; "relationship between X and Y" never normalizes to X→Y. Step 8 records asserted directionality; whether any causal claim is warranted is downstream.

## 41.12 Higher-order relationships

**OR-REL-4 (arity).** Binary explicit relationships are represented directly (args_complete = complete). Mediation/moderation/conditioning wording that is semantically necessary to identify the object ("how X affects Y through M", "the effect of X on Y under Z") is preserved: mention keeps the full phrase; internal metadata sets `relational_qualifier` ("through M" / "under Z") and args_complete = complete when both core arguments plus the qualifier are explicit. Higher-order structures whose full semantics cannot be represented without inventing a richer graph (chained mediations, nested conditionals) keep the complete source-grounded phrase as mention and mark args_complete = partial. **OR-REL-5.** "how X affects Y through M" is never silently flattened to relationship(X,Y). Step 8 is not a conceptual-model parser; anything beyond one explicit qualifier is partial, never reconstructed.

## 41.13 Knowledge artifacts

**OR-ART-1 (existent-artifact rule).** When a definite, specific, or existing epistemic artifact — determined by determiner/naming ("this/the/that/prevailing/existing/established" or a proper designation "Assumption X", "Model M") plus an artifact head from the licensed set — itself bears the deficiency predicate (untested, unvalidated, unsupported, mistaken, wrong, cannot explain/capture/distinguish, is flawed, breaks down), the artifact is the affected object: `object_kind = knowledge_artifact`, `artifact_kind` per the explicit head (§41.15–41.19), mention = the artifact phrase. The deficient knowledge is about that artifact (its validity, support, or capability), satisfying the schema's mention semantics.

**OR-ART-2 (existential-absence rule).** When the predicate asserts the *nonexistence* of an artifact/resource class for or about a target T ("No theory of X exists", "No model explains X", "No validated method exists to measure X", "No validated measure exists for X", "No analytical procedure can recover X"), no existing artifact referent exists to point at (the frozen DP-PREC-2 logic: "no artifact"); the deficient knowledge is about T. Therefore mention = T, `object_kind` per T's own kind (§41.8–41.10), and the absent artifact/resource class is carried entirely by `knowledge_kind` (theory / method) plus the preserved proposition. `about` is never used here (no artifact object exists to be about anything).

**OR-ART-3 (support/testing target rule).** Support-absence and testing-absence predicates ("lacks empirical support", "no empirical evidence supports —", "remains untested", "has not been validated/evaluated") target the artifact or relational content named as their subject/object; that named item is the affected object even though `knowledge_kind` is typically evidence (frozen DP-PREC-10): "Assumption X lacks empirical support." → assumption artifact; "No empirical evidence supports assumption X." → assumption artifact; "The relationship between X and Y has weak support." → relationship(X,Y).

**OR-ART-4 (challenged-findings rule).** When empirical findings/effects/results are themselves challenged ("Reported effects are artifacts of measurement error." — frozen CHALLENGED+evidence, the challenged item is the findings), the affected object is the challenged empirical claims: `object_kind = knowledge_artifact`, `artifact_kind = proposition`, mention = "reported effects" (the claims that the effects obtain). Rationale: the challenged item is epistemic output, not a worldly occurrence; proposition is the licensed artifact kind for claims. The phenomenon reading is rejected because the manuscript disputes the claims' validity, not the world's behavior.

## 41.14 Proposition

**OR-ART-5.** `artifact_kind = proposition` when the grammatical head is proposition / claim / hypothesis / prediction / assertion / finding-as-claim: "The proposition that X causes Y remains untested." → knowledge_artifact · proposition · mention "the proposition that X causes Y" · about = "X causes Y" (the that-clause explicitly supplies the artifact's content; §41.21). The object is NEVER automatically decomposed into relationship(X,Y): the deficiency is explicitly about the proposition artifact. Contrast (head rule, §41.24): "Whether X causes Y remains untested." → the whether-clause is relational content → relationship(X,Y). Step-8 object kinds never alter the given Step-6 relation.

## 41.15 Theory

**OR-ART-6a.** Explicit label "theory/theories" (or "theoretical account(s)" as head) → `artifact_kind = theory` under OR-ART-1. "Existing theories cannot explain X." → knowledge_artifact · theory · mention "existing theories"; X is the capability target (predicate complement) and never becomes `about` (§41.21). "Existing theories of organizational resilience cannot explain rapid adaptation." → same, with about = "organizational resilience" (artifact-attached of-complement). No reinterpretation by scientific judgment: model is never relabeled theory, framework never model, theory never proposition.

## 41.16 Model

**OR-ART-6b.** Explicit label "model(s)" → `artifact_kind = model`. "The model remains untested." → knowledge_artifact · model · mention "the model". Generic expressions ("this approach") receive no artifact kind unless permitted local context resolves the label (§41.26); otherwise the case falls under §41.20/§41.25 handling.

## 41.17 Framework

**OR-ART-6c.** Explicit label "framework(s)" → `artifact_kind = framework`. "The framework has yet to be evaluated." → knowledge_artifact · framework.

## 41.18 Assumption

**OR-ART-6d.** Explicit label "assumption(s)" or a named assumption → `artifact_kind = assumption`. "This assumption is mistaken." → knowledge_artifact · assumption · mention "this assumption". Anaphoric assumption heads keep the surface phrase and complete via §41.26: "Prior research assumes stable preferences, but this assumption is empirically unsupported." → mention.surface_form = "this assumption"; completion_status = context_completed; completion_trace_refs → span of "stable preferences"; surface referent and completed referent are both recorded; the manuscript text is never rewritten.

## 41.19 Measure

**OR-ART-6e.** A measure is a research measurement resource: measures, scales, instruments, indices, operationalizations, and measurement methods/procedures whose function is measuring. "Existing measures cannot capture temporal volatility." → knowledge_artifact · measure · mention "existing measures" (OR-ART-1). "No validated measure exists for X." → existential absence → OR-ART-2 → mention = X, kind carries the absence class. False friends (never measure artifacts): physical measurement events ("temperature was measured daily"), numeric metrics/values ("the measure rose to 0.7"), dependent-variable values, policy "measures" ("austerity measures").

## 41.20 Method-like objects

Step 6 permits `knowledge_kind = method`; GS-1.3 now licenses `artifact_kind = method` for existing non-measure methodological artifacts. The deterministic family, exhaustive and frozen:

- **OR-ART-7a (absent methodological resource).** "No validated method exists to measure X." / "No analytical procedure can recover X." — no existing artifact referent exists; OR-ART-2 applies: affected_object = the target (object_kind per the target); `knowledge_kind = method` is GIVEN from Step 6. A nonexistent `method` artifact is NEVER fabricated.
- **OR-ART-7b (existing measurement artifact).** "Existing measures cannot capture X." / "Scale M is unreliable." → `object_kind = knowledge_artifact`, `artifact_kind = measure` (§41.19).
- **OR-ART-7c (existing non-measure methodological artifact).** "Existing methods cannot distinguish X from Y." / "Cross-sectional designs cannot identify temporal ordering." / "Established survey approaches systematically misstate X." → `object_kind = knowledge_artifact`, `artifact_kind = method`, mention = the exact methodological artifact phrase ("Existing methods", "Cross-sectional designs", "Established survey approaches"). Canonical, local, no unresolved routing, no schema insufficiency.

**Hard distinction (frozen): ABSENCE of a method class ≠ EXISTING method artifact bearing deficiency.** The former yields the subject-matter target (7a); the latter yields a `method` artifact (7c). `method` never absorbs `measure` (7b). The former schema-insufficiency routing (SI-OR-1) is removed — it survives only as history in the revision record.

## 41.21 Optional `about`

**OR-ABOUT-1 (license).** `about` is permitted only when ALL hold: (1) `object_kind = knowledge_artifact`; (2) the manuscript explicitly supplies the artifact's subject matter *attached to the artifact head* — an of/on/about complement ("theories **of organizational resilience**", "measures **of trust**") or a content that-clause ("the proposition **that X causes Y**", "the assumption **that preferences are stable**"); (3) extraction requires no scientific inference; (4) the content usefully distinguishes the artifact's source-grounded referent. **OR-ABOUT-2 (prohibition).** The deficiency predicate's complement is NEVER `about`: in "Existing theories of organizational resilience cannot explain rapid adaptation.", about = "organizational resilience", never "rapid adaptation" — the artifact's subject matter is distinct from its deficient capability target. **OR-ABOUT-3.** about carries surface_form + mention_span_refs (I-42); it is never registry-inferred, never abbreviation-expanded, never created by completion beyond the schema's permitted linguistic completion.

## 41.22 Knowledge carrier vs affected object

**OR-CARRIER-1 (carrier-absorption rule; frozen).** A knowledge-kind carrier phrase — wording naming the knowledge itself: "evidence / empirical evidence / studies / research / literature / data / findings (as knowledge state) / knowledge / (theoretical) understanding / what is known" — is consumed by Step 6's `knowledge_kind` and NEVER becomes the affected object. The affected object is the carrier's complement: the subject matter the deficient knowledge is about. "Evidence about X is limited." → kind = evidence (given) · mention = X. "Theoretical understanding of X is limited." → kind = theory (given) · mention = X. "Little is known about X." → kind = evidence (frozen Case A) · mention = X. **OR-CARRIER-2 (carrier vs artifact test).** Carrier wording differs from an artifact bearing deficiency: carriers name knowledge coverage (mass/generic: evidence, understanding, literature); artifacts are determinate epistemic items (this/the/existing + proposition|theory|model|framework|assumption|measure, or named). "Theory about X is limited." → carrier reading (theory-type knowledge coverage) → object X; "The theory remains untested." → artifact reading → object = the theory. **OR-CARRIER-3.** When the carrier's complement is itself an artifact class as topic ("Little is known about models of X.", "Knowledge about the model is limited."), the object is that topic: knowledge_artifact · model · mention "models of X" / "the model" · about = X where explicitly attached — knowledge ABOUT artifacts is still knowledge about a referent.

## 41.23 Artifact vs subject matter

**OR-PREC-2.** "Little is known about Theory X." → Theory X is subject matter of deficient knowledge → object = knowledge_artifact · theory · mention "Theory X" (OR-CARRIER-3). "Theory X cannot explain Y." → Theory X is the deficient artifact (OR-ART-1). "Little theoretical understanding exists of Y." → carrier → object Y. "The theory remains untested." → artifact object. The rule is grammatical, never scientific: what the deficiency predicate targets (frozen DP-KIND-6 logic, applied to objects) decides; nearby salience decides nothing.

## 41.24 Relationship vs proposition artifact

**OR-PREC-3 (head rule).** The grammatical head of the deficiency target decides: head = proposition/claim/hypothesis/prediction ("the proposition that X affects Y") → knowledge_artifact · proposition; head = wh/whether-clause or relational nominal ("whether X affects Y", "the relationship between X and Y") → relationship(X,Y). Mandatory pairs: "Little is known about whether X affects Y." → relationship(X,Y) ‖ "The proposition that X affects Y remains untested." → proposition artifact. "Few studies examine the relationship between X and Y." → relationship(X,Y) ‖ "The model linking X and Y remains untested." → model artifact (mention "the model linking X and Y"; the linked content stays inside the mention, not decomposed). "Evidence about whether X predicts Y is limited." → relationship(X,Y), directed ‖ "The prediction that X predicts Y lacks empirical support." → proposition artifact (head "prediction"). Outside Step 8 in every pair: whether the two sides denote the same gap (Step 9) and every boundary/relation question (Steps 5–6).

## 41.25 Generic / unresolved objects

**OR-UNCERTAIN-1.** "little is known" (bare), "much remains unknown", "this remains unclear", "the issue remains unresolved", "the literature is limited" — no object is fabricated. If frozen grounding rules recover the referent from permitted context (§41.26) → completion_status = context_completed, with the canonical mention taken from the antecedent referent span where I-44 requires it (carrier/gap/reference expressions never stand as canonical objects). Otherwise → completion_status = unresolved; no canonical `affected_object` is produced; the case routes through the frozen lifecycle/review architecture (state machine v1.3 review path; protocol defect classes). `affected_object = "unspecified"` does not exist in `A1E-GS-1.3` and is never emitted. **OR-UNCERTAIN-2.** `knowledge_kind = unspecified` (a frozen enum value) NEVER implies an unspecified object: the axes are independent — "We do not understand why X persists." → kind = unspecified · mention = "why X persists" (a fully resolved object).

## 41.26 Coreference completion

**OR-COREF-1 (four-branch completion protocol; frozen; implements GS-1.3 I-44/I-45 exactly).**

- **Branch A — object-denoting anaphor.** The local anaphoric NP itself denotes a licensed affected object ("this theory", "this model", "this assumption", "this relationship"): the local surface form MAY remain the canonical mention; the antecedent supplies completion/identity support only (completion_status = context_completed when resolution is needed; completion_trace_refs identify the antecedent). The local mention is never rewritten: "Model M predicts X. This model remains untested." → knowledge_artifact · model · mention.surface_form = "This model" · context_completed — never rewritten to "Model M".
- **Branch B — carrier/gap/reference anaphor.** The local expression denotes a gap state, knowledge carrier, generic reference, or issue/reference wrapper rather than the affected referent itself ("this gap", "such evidence", "this issue", and analogous expressions under I-44): the canonical object resolves to the source-grounded antecedent referent; the local anaphor is NOT the canonical object and remains represented through the frozen schema's `context_support.dependency_expression`. "Little is known about employee turnover. This gap persists." → mention.surface_form = "employee turnover".
- **Branch C — frozen-example completion.** Where GS-1.3 itself specifies antecedent wording as canonical (its V3: "These mechanisms remain unexplored…" with antecedent "coordination mechanisms" → canonical mention "coordination mechanisms"), Step 8 follows GS-1.3 exactly. Step 8 never invents a representation competing with the frozen schema's own worked examples.
- **Branch D — unresolved.** Antecedent not unique → unresolved; no canonical affected_object; review route.

Operational constraints carried over: prefer the local explicit noun phrase; use the smallest preceding context sufficient to identify the antecedent; record completion traces (schema `context_support`: anaphora / referential_dependency); never rewrite manuscript text; never use distant inference when multiple plausible antecedents exist. Completion recovers only already-asserted referents (OR-TRACE-1). No runtime context-window size is defined here.

## 41.27 Ellipsis

**OR-ELLIPSIS-1.** Grammatically omitted but linguistically recoverable objects may be completed only under the frozen segmentation/extraction contract (schema context_support: ellipsis / omitted_argument). "Prior studies explain adoption but not retention." → the elided predication "prior studies do not explain retention" licenses object = "retention" (construct/phenomenon per head) with completion_status = context_completed and trace to the shared head "explain". Covered forms: coordination ellipsis (shared verb), shared heads ("measures of trust and of commitment"), contrastive ellipsis ("but not Y"). **OR-ELLIPSIS-2.** Completion is grammatical only — no scientific meaning is reconstructed; if the elided predicate is not uniquely recoverable, → unresolved.

## 41.28 Conjoined objects

**OR-CONJ-1 (frozen).** `A1E-GS-1.3` defines exactly one `affected_object` per gap_record. Step 8 therefore emits ONE object per proposition, preserving coordinated source wording in the mention ("trust and commitment"), with internal `coordination_present = true`. Splitting into sibling objects is licensed only when upstream proposition segmentation (Step-1 contract; Step-11 runtime) has already produced separate proposition units — in which case each unit passes through Step 8 independently. Step 8 itself never splits, because splitting presupposes that each coordinated referent independently bears the same predicate without semantic distortion — a segmentation judgment owned upstream — and never merges (Step 9). "Theories cannot explain acquisition timing or integration speed." → one artifact object (existing theories) with the coordinated capability targets preserved in the proposition; the coordination lives in the predicate complement, not the object.

## 41.29 Nested objects

**OR-PREC-4 (HEAD-TARGET rule; frozen).** Determine the grammatical head of the deficiency target first; the head controls object selection: "No measure of trust captures temporal change." → head = measure → measure artifact (mention "measure of trust", about = "trust"), NOT trust. "Little is known about trust." → head = trust → construct. "the assumption underlying model M" → head = assumption → assumption artifact (about only if a content clause is attached; "model M" is a structural attachment, recorded in mention wording). "evidence about relationship Y" → carrier evidence absorbed; head of complement = relationship → relationship object. The target of the deficiency predicate controls; salience never does.

## 41.30 Object-internal modifiers

**OR-MOD-1.** Modifiers constitutive of referent identity stay in the object: "causal mechanisms", "informal coordination", "digital platform governance", and sense-fixing generic-bearer premodifiers such as "employee trust" / "employee engagement" (OR-SCOPE-PRE-1 carve-out) — removing them changes WHICH referent is deficient (removal test, §41.6). Subgroup premodifiers (nurse, SME, Spanish-firm) are population/setting scope under OR-SCOPE-3 regardless of position. **OR-MOD-2.** External scope modifiers never enter the object (§41.7, §41.31): "employee trust among frontline workers" → mention "employee trust"; "organizational adaptation during crises" → mention "organizational adaptation" ("during crises" = temporal scope). The complete proposition preserves all wording either way.

## 41.31 Scope/context modifiers

Descriptor ownership is decided by the §41.7 family (OR-SCOPE-2/3/PRE-1/4), never by position or intuition: "digital transformation", "post-merger integration", "knowledge hiding", "causal mechanism" → constitutive (removal changes WHAT is denoted). "recent research on transformation" → "recent" modifies the carrier state, never the object. "cross-national differences in trust" → object-internal iff the object is the difference pattern across national units (it is, when the differences themselves are the deficient topic); "trust across countries" → construct trust + geographic scope. "crisis adaptation" → retained whole ONLY when local wording makes crisis the semantic content of the adaptation (adaptation-to-crisis); when it can equally mean adaptation observed during a crisis, OR-SCOPE-4 applies: minimal object "adaptation" + review flag. Residual ambiguity always resolves to the minimal object + `E-SCOPE-LEAKAGE`-guarded review; no structured scope output ever exists.

## 41.32 Practice-alignment objects

The four frozen Step-6 patterns receive distinct source-grounded objects; relation and kind are GIVEN and untouched; no generic "practice gap" object exists; practitioners are never converted to scope.

- **OR-PA-1** — "No mechanism exists for translating research findings into practice." (ABSENT + practice_alignment): existential absence of the bridge apparatus → OR-ART-2 → mention = "translating research findings into practice" (the process the absent bridge is for) · object_kind = phenomenon. The bridge-entity wording stays in the preserved proposition and kind.
- **OR-PA-2** — "Translation of research into practice remains limited." (LIMITED + practice_alignment): mention = "translation of research into practice" · phenomenon.
- **OR-PA-3** — "Barriers constrain the translation of research into practice." (CONSTRAINED + practice_alignment): mention = "the translation of research into practice" · phenomenon (the constrained process; "barriers" are the constraining cause, never the object).
- **OR-PA-4** — "Research and practice remain poorly aligned." (DISCONNECTED + practice_alignment): object_kind = relationship · mention.surface_form = "Research and practice remain poorly aligned" (verbatim clause span, licensed by §41.10 for predicate-expressed disrelations) · internal arguments (research; alignment; undirected; practice).

Distinctness is source-grounded (four different mentions/kinds); whether OR-PA-2 and OR-PA-3 objects are identity-equivalent is exactly the Step-9 question and is NOT decided here.

## 41.33 Support objects

Per OR-ART-3 with frozen DP-PREC-10 (support wording → evidence kind): "Assumption X lacks empirical support." → assumption artifact (about = X if named content attaches). "No empirical evidence supports assumption X." → assumption artifact — evidence is the kind carrier; the supported item bears the deficiency. "The proposition that X causes Y lacks support." → proposition artifact (about = "X causes Y"). "The relationship between X and Y has weak support." → relationship(X,Y), undirected. The evidence carrier NEVER becomes the object; the claim/proposition/relationship being (un)supported always does.

## 41.34 Testing objects

"The model remains untested." → model artifact. "The proposition that X causes Y has not been tested." → proposition artifact. "Measure X has not been validated." → measure artifact (frozen UNTESTED+evidence: existing artifact + denied verification act — the artifact is the object). "The framework has yet to be evaluated." → framework artifact. The artifact is never collapsed into its subject matter; its validity is never inferred.

## 41.35 Challenged/constrained objects

"The prevailing assumption is mistaken." → assumption artifact (OR-ART-1). "Existing theories cannot explain X." → theory artifact per frozen CONSTRAINED+theory — the theories are the deficient resource; X is capability target only. "Reported effects are artifacts of measurement error." → OR-ART-4 → knowledge_artifact · proposition · mention "reported effects" (the challenged findings-claims; frozen CHALLENGED+evidence untouched). CHALLENGED/CONSTRAINED semantics are consumed, never modified.

## 41.36 Attribution and temporal context

**OR-TRACE-2.** Attribution never changes object identity: "Smith argues that little is known about X." → if the local deficiency proposition is processed, mention = X; adoption/rejection is Step-5 work. "Contrary to Smith's claim that little is known about X…" → object of the quoted proposition = X; rejection status handled elsewhere. **OR-TRACE-3.** Temporal status is never encoded into affected_object: "X was poorly understood until recently." → mention = X; whether the deficiency is current is owned upstream/downstream (SL-TEMP-1 context; Step-5/6 semantics). Step 8 does not recreate Step-7 signal rules.

## 41.37 Source traceability

Captured per object: mention_span_refs (≥1); type_trace_refs (≥1; artifact naming covered when artifact_kind present — I-40); completion_trace_refs iff context_completed; internal argument spans iff relationship; about spans iff about. The gap-level trace machinery is the schema's; Step 8 references it, never duplicates it. **Hard rule (OR-TRACE-4):** normalized object content is always reconstructable from manuscript text plus explicitly recorded permitted completion — nothing else. *I-45 alignment:* every mention_span_ref used for a canonical mention must contain/correspond to the declared surface_form; surface_form "coordination mechanisms" is never combined with a span containing only "These mechanisms" — the latter belongs to completion/context traceability, never to mention_span_refs.

**Source vs normalized (OR-TRACE-5).** `source_text` (= mention.surface_form) is exact manuscript wording. `normalized_text` (internal) permits ONLY: trimming surrounding punctuation; whitespace normalization; deterministic case handling where frozen upstream; removal of purely syntactic determiners ("the organization's absorptive capacity" → "organization's absorptive capacity"); controlled recovery of an omitted argument via permitted completion. PROHIBITED in normalization: synonym replacement; ontology mapping; external abbreviation expansion; latent-variable inference; translation; collapsing semantically similar expressions; any Step-9 identity resolution. "organization's absorptive capacity" is never rewritten "knowledge assimilation capability" unless the manuscript itself explicitly equates them and a frozen rule licenses it. Preservation is always preferred over normalization.

## 41.38 Object extraction procedure

O1. Receive proposition + GIVEN Step-6 (relation, knowledge_kind). O2. Identify the grammatical deficiency predicate. O3. Identify the referent that bears / is targeted by the deficiency (OR-TARGET-1). O4. Separate knowledge carrier from affected subject matter (OR-CARRIER-1, OR-CARRIER-2, OR-CARRIER-3). O5. Determine object_kind (OR-TYPE-2; OR-REL-1; OR-ART-1; OR-ART-2). O6. Determine artifact_kind iff knowledge_artifact (OR-ART-5; OR-ART-6a–6e; OR-ART-7a–7c). O7. If relationship: extract explicit arguments, predicate, direction — no inference (OR-REL-2, OR-REL-3, OR-REL-4, OR-REL-5). O8. Remove only external scope/context from the structured object; the complete proposition preserves all wording (OR-SCOPE-1, OR-SCOPE-2, OR-SCOPE-3, OR-SCOPE-PRE-1, OR-SCOPE-4). O9. Apply permitted local completion if needed (OR-COREF-1; OR-ELLIPSIS-1, OR-ELLIPSIS-2). O10. Produce source-grounded representation + trace refs (OR-TRACE-1, OR-TRACE-2, OR-TRACE-3, OR-TRACE-4, OR-TRACE-5). O11. Multiple readings remain → unresolved / review (OR-UNCERTAIN-3). Excluded by construction: merge, identity, candidate emission, scientific evaluation.

## 41.39 Precedence rules

**OR-PREC-1 (object-kind precedence; frozen).** Apply in order, stopping at the first match: (1) a named/definite knowledge artifact is itself the grammatical deficiency target → knowledge_artifact; (2) explicit relational content is the deficient object → relationship; (3) a delimited conceptual variable/entity → construct; (4) a broader event/process/pattern/state → phenomenon; (5) otherwise unresolved. Existential absences enter at step (2)–(4) via OR-ART-2 and OR-ART-7a (the absent class never reaches step 1 — no artifact exists). **OR-PREC-5 (completion precedence; frozen).** 1. fully explicit local affected object → 2. object-denoting local anaphor with unique antecedent (OR-COREF-1 Branch A) → 3. carrier/reference anaphor resolved to a unique antecedent referent (Branch B/C) → 4. locally recoverable grammatical ellipsis (OR-ELLIPSIS-1) → 5. unresolved. PROHIBITED continuations: infer from RQ; from objective; from contribution; from abstract; from later method; from domain knowledge. **OR-UNCERTAIN-3 (multiple plausible affected objects).** Two or more linguistically plausible AFFECTED-OBJECT readings unresolved by frozen rules are never resolved by scientific plausibility; mark the affected object unresolved and route to review. Examples: "This remains poorly understood." with multiple candidate antecedents → affected object unresolved; "This model remains untested." with two plausible model antecedents → affected object unresolved; "The literature is limited." with no identifiable subject matter → affected object unresolved. A predicate-side complement may be ambiguous while the affected object itself remains resolved; such cases do NOT trigger object-level unresolved status (e.g. OT-AMB-05). No forced extraction, ever.

## 41.40 Machine-referenceable rule registry

Every normative OR-* ID in this artifact has exactly one row below (hard closure; no pseudo-ranges).

| rule_id | rule_family | normative_rule | input_condition | output_effect | prohibited_inference | related_frozen_rule | test_refs |
|---|---|---|---|---|---|---|---|
| OR-TARGET-1 | TARGET | object = referent bearing the deficiency predicate | any proposition | selects deficiency target | salience-based choice | DP-KIND-6 (kind analogue) | OT-CAR suite, MP-01 |
| OR-TARGET-2 | TARGET | minimal sufficient object; removal/carrier/scope tests | any object | smallest identifying span | padding with scope/carrier | schema I-9 | OT-SCP suite, MP-06, MP-08 |
| OR-CONSTRUCT-1 | CONSTRUCT | construct = delimited conceptual variable/category | conceptual NP | construct object | registry validation; synonym merge | — | OT-CP-01..05, OT-CP-12 |
| OR-TYPE-2 | TYPE | stative-attribute head → construct; eventive/process head → phenomenon | non-relational, non-artifact NP | object_kind | lexicon-external guesses | — | OT-CP suite |
| OR-PHEN-1 | PHEN | phenomenon = process/event/behavior/condition/pattern | eventive NP | phenomenon object | forced construct/artifact | — | OT-CP-06..11 |
| OR-PHEN-2 | PHEN | nominal "X responses to Y" = phenomenon unless relation asserted | nominalized compound | phenomenon default | forced relationship | — | OT-CP-11, OT-CP-15, MP-25 |
| OR-REL-1 | REL | relationship iff wh/whether-relational, relational nominal with both args, or relational clause | activation forms | relationship object | relation from co-mention | — | OT-REL-01..08 |
| OR-REL-2 | REL | arguments = source-grounded phrases with spans (internal metadata) | relationship object | argument metadata | argument invention | — | OT-REL suite |
| OR-REL-3 | REL | direction only when lexically asserted; between/association/link/interaction undirected | relational phrase | direction metadata | direction from RQ/theory/order | §41.11 lexeme list | OT-REL-03, OT-REL-07, MP-22, MP-23 |
| OR-REL-4 | REL | one explicit qualifier preserved as relational_qualifier; beyond that args_complete = partial | higher-order wording | qualifier / partial | graph invention | — | OT-REL-11, OT-REL-12, OT-REL-14 |
| OR-REL-5 | REL | qualified relationships never silently flattened | "through M" forms | full-phrase mention | flattening | — | OT-REL-11, MP-24 |
| OR-ART-1 | ART | existent definite artifact bearing deficiency → artifact object | definite artifact + deficiency | knowledge_artifact + kind | subject-matter substitution | DPR artifact anchors | OT-ART-01..08 |
| OR-ART-2 | ART | existential absence → mention = target T; kind carries the absent class | "no ARTIFACT … exists/explains" | object per T | nonexistent-artifact referent | DP-PREC-2 | OT-ART-09..12, MP-14, MP-21 |
| OR-ART-3 | ART | support/testing predicates → named artifact/relation is object | support/testing wording | artifact/relationship object | evidence-as-object | DP-PREC-10 | OT-ST suite |
| OR-ART-4 | ART | challenged findings → proposition-kind artifact | challenged effects/findings | proposition artifact | phenomenon reading | CHALLENGED+evidence cell | OT-ART-17, MP-18 |
| OR-ART-5 | ART | head proposition/claim/hypothesis/prediction → proposition; that-clause = about | content-clause head | proposition + about | auto-decomposition | — | OT-ART-13..15, OT-ST-10 |
| OR-ART-6a | ART | explicit "theory/theoretical account" head → theory | labeled theory | artifact_kind = theory | scientific relabeling | §41.15 | OT-ART-04, OT-ART-05 |
| OR-ART-6b | ART | explicit "model" head → model | labeled model | artifact_kind = model | relabeling | §41.16 | OT-ART-01, OT-ART-08 |
| OR-ART-6c | ART | explicit "framework" head → framework | labeled framework | artifact_kind = framework | relabeling | §41.17 | OT-ART-06, OT-ST-08 |
| OR-ART-6d | ART | explicit "assumption" head → assumption; anaphors complete per OR-COREF-1 | labeled assumption | artifact_kind = assumption | silent rewriting | §41.18 | OT-ART-03, OT-ART-07, OT-COR-01 |
| OR-ART-6e | ART | measurement resources → measure; false friends excluded | measurement wording | artifact_kind = measure | metric/event confusion | §41.19 | OT-ART-02, OT-ST-07 |
| OR-ART-7a | ART | absent methodological resource → OR-ART-2 target object; no fabricated method artifact | existential method absence | object per target | artifact fabrication | DP-KIND-3; DP-PREC-2 | OT-ART-11, OT-ART-12, MP-34 |
| OR-ART-7b | ART | existing measurement artifact → measure | existing measure + deficiency | measure artifact | method mislabel | GS-1.3 §4a | OT-ART-02, MP-13 |
| OR-ART-7c | ART | existing non-measure methodological artifact → method (GS-1.3) | existing method/design/approach + deficiency | method artifact, verbatim mention | measure absorption; unresolved routing | GS-1.3 §4a | OT-ART-18..20, MP-34 |
| OR-ABOUT-1 | ABOUT | about iff artifact + explicitly attached subject matter (of/on/that) | attachment present | about populated | predicate-complement about | I-28/I-42 | OT-ART-05, OT-ART-13, MP-36, MP-37 |
| OR-ABOUT-2 | ABOUT | capability target never = about | predicate complement | about withheld | inference from failure target | I-42 | OT-ART-04, MP-36 |
| OR-ABOUT-3 | ABOUT | about verbatim + refs; never registry/abbreviation/completion-invented | about block | grounded about | external enrichment | I-42 | OT-ART-05 |
| OR-CARRIER-1 | CARRIER | carrier phrase absorbed by kind; object = the carrier's complement | carrier + complement | mention = complement | carrier-as-object | DP-KIND-6; frozen Case A | OT-CAR-01..08, OT-CAR-14 |
| OR-CARRIER-2 | CARRIER | carrier (mass/generic knowledge) vs artifact (determinate item) | knowledge wording | reading selection | scientific relabeling | DP-PREC-2 | OT-CAR-09, OT-CAR-10, MP-03 |
| OR-CARRIER-3 | CARRIER | artifact-class-as-topic under a carrier stays the object (+ about where attached) | carrier + artifact topic | knowledge_artifact object | topic deletion | — | OT-CAR-11..13, MP-09, MP-14 |
| OR-SCOPE-1 | SCOPE | post-head among/in/across/within/during/over/at + pop/setting/geo/time NP → external scope | adjunct PP | excluded from mention | structured scope output | I-9 | OT-SCP-01..08 |
| OR-SCOPE-2 | SCOPE | object-internal ONLY when constitutive; pre-head position never sufficient | any modifier | constitutive decision | position-based inclusion | 8B §11 | OT-SCP-03, OT-SCP-09, MP-06 |
| OR-SCOPE-3 | SCOPE | population/context ownership invariant to syntactic realization | any realization | scope stays scope | prenominal conversion | 8B §8 | OT-SCP-03, MP-06, MP-08 |
| OR-SCOPE-PRE-1 | SCOPE | paraphrase/removal test for premodifiers; sense-fixing carve-out; lexicalization needs explicit evidence | premodifier M on head H | scope vs constitutive | assumed lexicalization | 8B §9 | OT-SCP-03, OT-SCP-09, OT-CP-18 |
| OR-SCOPE-4 | SCOPE | irreducible ambiguity → minimal object + review flag; never forced inclusion | ambiguous attachment | minimal object + flag | interpretive invention | 8B §11 | OT-SCP-07, OT-SCP-14 |
| OR-COREF-1 | COREF | four-branch completion protocol (A object-denoting local mention · B carrier/reference resolves to antecedent · C frozen GS-example completion · D unresolved); implements I-44/I-45 | anaphoric head | canonical mention per branch; context_completed or unresolved | distant inference; rewriting local object-denoting mentions; carrier anaphors as canonical objects | GS-1.3 I-44/I-45; schema context_support | OT-COR-01..07, OT-AMB-05, OT-AMB-11 |
| OR-ELLIPSIS-1 | ELLIPSIS | grammatical recovery only, under frozen contract | ellipsis forms | completed object + trace | semantic reconstruction | context_support: ellipsis | OT-COR-08..10, MP-27, MP-28 |
| OR-ELLIPSIS-2 | ELLIPSIS | non-unique elided predicate → unresolved | ambiguous ellipsis | review routing | forced recovery | — | OT-COR-08 rationale |
| OR-CONJ-1 | CONJ | one object per record; coordination preserved; splitting is upstream segmentation | coordinated referents | single mention + flag | Step-8 splitting/merging | schema: single affected_object | OT-CP-19, OT-CP-20, MP-26 |
| OR-MOD-1 | MOD | constitutive modifiers preserved (removal test; sense-fixing carve-out) | modifiers | identity-preserving mention | modifier stripping | §41.6 | OT-CP-08, OT-SCP-05 |
| OR-MOD-2 | MOD | external scope modifiers never enter object | scope modifiers | clean mention | scope inclusion | §41.7 family | OT-SCP-01, OT-SCP-02 |
| OR-PREC-1 | PREC | kind precedence: artifact → relationship → construct → phenomenon → unresolved | typed candidates | deterministic kind | forcing on tie | — | all suites |
| OR-PREC-2 | PREC | artifact-as-subject-matter vs artifact-as-deficient-resource by deficiency target | artifact wording | reading selection | scientific judgment | DP-KIND-6 | OT-CAR-10..13, MP-09, MP-17 |
| OR-PREC-3 | PREC | proposition vs relationship by grammatical head | content clause vs wh-clause | kind decision | scientific equivalence | — | MP-04, MP-05, MP-35 |
| OR-PREC-4 | PREC | HEAD-TARGET: nested objects resolved by deficiency-target head | nested NP | head-selected object | salience selection | — | OT-ART-16, MP-13 |
| OR-PREC-5 | PREC | completion precedence: explicit local → object-denoting anaphor (A) → carrier/reference resolution (B/C) → grammatical ellipsis → unresolved; RQ/objective/contribution/abstract/later-method/domain prohibited | incomplete object | ordered completion | prohibited sources | §41.39; I-44 | OT-COR suite, OT-AMB suite |
| OR-UNCERTAIN-1 | UNCERTAIN | generic expressions: complete (to antecedent referent per I-44) or unresolved; no fabrication; no "unspecified" object value | bare deficiency wording | context_completed / unresolved | fabricated objects; carrier wording as object | schema (no such value); I-44 | OT-AMB-01..04, MP-40 |
| OR-UNCERTAIN-2 | UNCERTAIN | knowledge_kind = unspecified never implies unresolved object | unspecified kind | independent axes | axis conflation | contract enums | OT-CAR-15, MP-39 |
| OR-UNCERTAIN-3 | UNCERTAIN | multiple plausible affected-object readings → unresolved/review | ≥2 plausible affected-object readings | no canonical affected_object; review routing | scientific/plausibility tie-breaking | protocol classes | OT-AMB-03, OT-AMB-06, OT-COR-07 |
| OR-TRACE-1 | TRACE | context completes, never creates | any completion | grounded object | referent creation | I-9b | OT-COR suite |
| OR-TRACE-2 | TRACE | attribution never changes object identity | attributed proposition | invariant object | adoption inference | Step-5 ownership | OT-AMB-10, MP-29 |
| OR-TRACE-3 | TRACE | temporal status never enters object | temporal wording | clean mention | temporal encoding | SL-TEMP-1 boundary | OT-AMB-09, MP-30 |
| OR-TRACE-4 | TRACE | normalized object reconstructable from source + recorded completion | any object | reconstructability | untraceable content | I-41 | all suites |
| OR-TRACE-5 | TRACE | normalization whitelist only; never holds completed referents; preservation preferred | normalization | safe normalized_text | synonym/ontology mapping; antecedent substitution | 8B §21 | OT-ART-02, OT-CP-13, MP-32 |
| OR-PA-1 | PA | absent bridge apparatus → phenomenon object = the translation process (OR-ART-2 pattern) | practice-alignment pattern A | phenomenon, verbatim process span | mechanism-as-object; generic practice-gap | DP-KIND-4a | OT-PA-01, OT-PA-10, MP-15 |
| OR-PA-2 | PA | limited translation process → phenomenon | practice-alignment pattern B | phenomenon object | collapse into A/C/D | DP-KIND-4 | OT-PA-02, MP-16 |
| OR-PA-3 | PA | constrained translation process → phenomenon; constrainer never the object | practice-alignment pattern C | phenomenon object | barrier-as-object | DP-KIND-4 | OT-PA-03, OT-PA-09, MP-16 |
| OR-PA-4 | PA | alignment/disrelation state → relationship(research, practice), verbatim clause mention | practice-alignment pattern D | relationship object | phenomenon collapse; forced direction | DP-PREC-15 | OT-PA-04..07, MP-15 |

## 41.41 Knowledge-carrier vs affected-object table (normative)

| Sentence pattern | Knowledge carrier | knowledge_kind (GIVEN) | Affected object | Reason |
|---|---|---|---|---|
| Little is known about X. | "known" | evidence | X (per X's kind) | OR-CARRIER-1; frozen Case A |
| Evidence about X is limited. | evidence | evidence | X | OR-CARRIER-1 |
| Empirical evidence on X is scarce. | empirical evidence | evidence | X | OR-CARRIER-1 |
| Theoretical understanding of X is limited. | theoretical understanding | theory | X | OR-CARRIER-1 |
| No theory of X exists. | — (existential) | theory | X | OR-ART-2: no artifact exists; kind carries class |
| Existing theories cannot explain X. | — | theory | knowledge_artifact · theory ("existing theories") | OR-ART-1; X = capability target, not about |
| No model explains X. | — (existential) | theory | X | OR-ART-2; DP-PREC-2 "no artifact" |
| The model remains untested. | — | evidence | knowledge_artifact · model ("the model") | OR-ART-1/OR-ART-3 |
| Assumption X lacks empirical support. | empirical support | evidence | knowledge_artifact · assumption ("Assumption X") | OR-ART-3; DP-PREC-10 |
| No empirical evidence supports assumption X. | empirical evidence | evidence | knowledge_artifact · assumption | OR-ART-3; supported item bears deficiency |
| Existing measures cannot capture X. | — | method | knowledge_artifact · measure ("existing measures") | OR-ART-1/7b |
| No validated measure exists for X. | — (existential) | method | X | OR-ART-2/7a |
| No validated method exists to measure X. | — (existential) | method | X | OR-ART-2/7a; DP-KIND-3 absent resource |
| Existing methods cannot distinguish X from Y. | — | method | knowledge_artifact · method ("Existing methods") | OR-ART-7c (GS-1.3) |
| Cross-sectional designs cannot identify temporal ordering. | — | method | knowledge_artifact · method ("Cross-sectional designs") | OR-ART-7c |
| Research and practice remain poorly aligned. | — | practice_alignment | relationship(research, practice), undirected | OR-PA-4 |
| No mechanism exists for translating research into practice. | — (existential) | practice_alignment | phenomenon "translating research (findings) into practice" | OR-PA-1; OR-ART-2 |
| Translation of research into practice remains limited. | — | practice_alignment | phenomenon "translation of research into practice" | OR-PA-2 |

**Explanatory rule:** an EXISTING artifact bearing the deficiency → artifact object (rows: existing theories, the model, existing measures, existing methods, cross-sectional designs); CATEGORICAL ABSENCE of an artifact class → subject-matter target object (rows: no theory of X, no model explains X, no validated measure/method for X). This is OR-ART-1 vs OR-ART-2, applied uniformly across theory, measure, and method.

## 41.42 Step-6 coverage audit (objects for the frozen DPR anchors; relation/kind GIVEN, untouched)

| DPR anchor | Given (relation, kind) | Step-8 object | Rule | PASS |
|---|---|---|---|---|
| "No studies have examined X." | ABSENT, evidence | X | OR-CARRIER-1 (studies = carrier) | PASS |
| "Little is known about X." | LIMITED, evidence | X | OR-CARRIER-1 | PASS |
| "X has received no attention." | ABSENT, evidence | X | OR-CARRIER-1 (attention = carrier) | PASS |
| "No theoretical account explains X." | ABSENT, theory | X | OR-ART-2 | PASS |
| "Existing theories cannot explain X." | CONSTRAINED, theory | theory artifact "existing theories" | OR-ART-1 | PASS |
| "This theoretical assumption is mistaken." | CHALLENGED, theory | assumption artifact | OR-ART-1/6d | PASS |
| "The model is empirically wrong." | CHALLENGED, theory | model artifact | OR-ART-1; grounds adverb irrelevant to object | PASS |
| "Theoretical understanding of X remains limited." | LIMITED, theory | X | OR-CARRIER-1 | PASS |
| "No validated method exists to measure X." | ABSENT, method | X | OR-ART-2/7a | PASS |
| "Existing measures cannot capture temporal variation." | CONSTRAINED, method | measure artifact "existing measures" | OR-ART-7b | PASS |
| "Analytical approaches for multi-level X remain underdeveloped." | LIMITED, method | method artifact "Analytical approaches for multi-level X" | OR-ART-7c (GS-1.3) | PASS |
| "Established survey approaches systematically misstate X." | CHALLENGED, method | method artifact "Established survey approaches" | OR-ART-7c | PASS |
| "The model remains untested." | UNTESTED, evidence | model artifact | OR-ART-3 | PASS |
| "Measure X has not been validated." | UNTESTED, evidence | measure artifact "Measure X" | OR-ART-3 | PASS |
| "No empirical evidence supports assumption X." | ABSENT, evidence | assumption artifact | OR-ART-3 | PASS |
| "Prior findings on X are mixed." | CONFLICTING, evidence | X (findings = carrier of conflicting knowledge about X) | OR-CARRIER-1 | PASS |
| "Reported effects are artifacts of measurement error." | CHALLENGED, evidence | proposition artifact "reported effects" | OR-ART-4 | PASS |
| Four practice-alignment anchors (§41.32) | per frozen DPR | four non-collapsed objects | OR-PA-1, OR-PA-2, OR-PA-3, OR-PA-4 | PASS |
| "We do not understand why X persists." | LIMITED, unspecified | "why X persists" | OR-UNCERTAIN-2 | PASS |

## 41.43 Normative object test suite (131 tests)

**Serialization contract (one deterministic machine-readable interpretation per test).** Fields: `test_id · "source_text" · given=GIVEN_RELATION/GIVEN_KNOWLEDGE_KIND · type=expected_object_type · art=expected_artifact_kind · obj=expected_source_text (mention.surface_form) · norm=expected_normalized_text (shown only when ≠ obj) · args=expected_relationship_arguments (arg1; predicate; direction; arg2[; qualifier]) · about=expected_about · comp=completion_status · object_type_assertion (optional metadata) · not=[must_not_extract] · short_rationale · open=later_question_unresolved`. Closed values — expected_object_type ∈ {construct, phenomenon, relationship, knowledge_artifact, NO_CANONICAL_OBJECT, NOT_TESTED}; expected_artifact_kind ∈ {proposition, theory, model, framework, assumption, measure, method, NOT_APPLICABLE, NOT_TESTED}; completion_status ∈ {local, context_completed, unresolved}, always spelled in full; GIVEN_RELATION ∈ {ABSENT, LIMITED, CONFLICTING, UNTESTED, CONSTRAINED, DISCONNECTED, CHALLENGED} or NOT_TESTED; GIVEN_KNOWLEDGE_KIND ∈ {evidence, theory, method, practice_alignment, unspecified} or NOT_TESTED — the "/" in `given=` is the relation/kind separator, never an alternative marker, and no compound alternatives exist anywhere. Meta-value semantics: `NO_CANONICAL_OBJECT` means the production object is absent because extraction is unresolved (it is NEVER serialized into `affected_object.object_kind`) and pairs with `art=NOT_APPLICABLE` (explicit or by the omission convention) and `obj=ABSENT`; `NOT_APPLICABLE` marks artifact_kind for non-artifact objects; an omitted `art=` field serializes NOT_APPLICABLE; "—" in any other field = inapplicable/absent; `object_type_assertion=NOT_TESTED` marks tests asserting target selection or completion mechanics without asserting object typing — every test carries either an explicit legal `type=` value or this declaration. `comp` describes AFFECTED-OBJECT completion only; unresolved predicate-side complements never mark the object unresolved. Prohibited everywhere: per-X · pa · compound slash alternatives (e.g. two relations in one GIVEN) · UNREPRESENTABLE · SI-OR-1 route · ctx · unres. Verbatim rule: every `obj=` value is an exact manuscript substring — local or antecedent span as licensed by I-44/I-45; generated labels, ellipsis substitutions, and bracketed reconstructions are prohibited. Relation/kind are GIVEN Step-6 inputs; their accuracy is never tested here. Completion never rewrites an object-denoting local mention; recovered antecedents live in completion metadata, never in `norm` (OR-TRACE-5).

**Construct / phenomenon (20).**
OT-CP-01 · "Little is known about organizational resilience." · given=LIMITED/evidence · type=construct · obj="organizational resilience" · comp=local · not=[carrier "known"] · stative capacity head · open=G-checks upstream.
OT-CP-02 · "Little is known about employee engagement." · given=LIMITED/evidence · type=construct · obj="employee engagement" · comp=local · not=[] · stative attitude (-ment, stative) · open=—.
OT-CP-03 · "Evidence about absorptive capacity is scarce." · given=LIMITED/evidence · type=construct · obj="absorptive capacity" · comp=local · not=[evidence] · OR-CARRIER-1 · open=—.
OT-CP-04 · "Trust remains poorly understood." · given=LIMITED/unspecified · type=construct · obj="trust" · comp=local · not=[] · bare construct subject · open=—.
OT-CP-05 · "Few studies examine ethical climate." · given=LIMITED/evidence · type=construct · obj="ethical climate" · comp=local · not=[studies] · carrier absorbed · open=—.
OT-CP-06 · "Little is known about collective adaptation." · given=LIMITED/evidence · type=phenomenon · obj="collective adaptation" · comp=local · not=[] · eventive process head · open=—.
OT-CP-07 · "Post-merger integration remains underexplored." · given=LIMITED/evidence · type=phenomenon · obj="post-merger integration" · comp=local · not=[] · process nominal · open=—.
OT-CP-08 · "Digital transformation is poorly understood." · given=LIMITED/unspecified · type=phenomenon · obj="digital transformation" · comp=local · not=["digital" removal] · "digital" constitutive (OR-MOD-1) · open=—.
OT-CP-09 · "Knowledge hiding has received little attention." · given=LIMITED/evidence · type=phenomenon · obj="knowledge hiding" · comp=local · not=[attention] · behavior head · open=—.
OT-CP-10 · "Organizational responses to disruption remain unexplored." · given=ABSENT/evidence · type=phenomenon · obj="organizational responses to disruption" · comp=local · not=[relationship reading] · OR-PHEN-2 nominal default · open=—.
OT-CP-11 · "Little is known about employee responses to algorithmic monitoring." · given=LIMITED/evidence · type=phenomenon · obj="employee responses to algorithmic monitoring" · comp=local · not=[args split] · no asserted relational predicate · open=—.
OT-CP-12 · "Job satisfaction is understudied." · given=LIMITED/evidence · type=construct · obj="job satisfaction" · comp=local · not=[] · stative -tion attitude · open=—.
OT-CP-13 · "The emergence of platform ecosystems is not well understood." · given=LIMITED/unspecified · type=phenomenon · obj="the emergence of platform ecosystems" · norm="emergence of platform ecosystems" · comp=local · not=[] · occurrence head; determiner trimmed · open=—.
OT-CP-14 · "Cross-national differences in trust remain unexplained." · given=ABSENT/theory · type=phenomenon · obj="cross-national differences in trust" · comp=local · not=[scope split of "cross-national"] · differences-pattern is the object (OR-SCOPE-3) · open=—.
OT-CP-15 · "Little is known about how employees respond to algorithmic monitoring." · given=LIMITED/evidence · type=relationship · obj="how employees respond to algorithmic monitoring" · args=(employees; respond_to; undirected; algorithmic monitoring) · comp=local · not=[phenomenon reading; forced direction] · wh-complement over relational predicate (OR-REL-1, clause i); "respond to" is non-directional per OR-REL-3, so no direction is recorded · open=Step-9 identity vs OT-CP-11.
OT-CP-16 · "Few studies examine knowledge hiding in teams." · given=LIMITED/evidence · type=phenomenon · obj="knowledge hiding" · comp=local · not=["in teams"] · post-head in-PP = setting scope · open=—.
OT-CP-17 · "Organizational resilience during crises is poorly understood." · given=LIMITED/unspecified · type=construct · obj="organizational resilience" · comp=local · not=["during crises"] · temporal scope excluded · open=—.
OT-CP-18 · "Crisis adaptation remains poorly understood." (standalone; no constitutive evidence) · given=LIMITED/unspecified · type=phenomenon · obj="adaptation" · comp=local · not=[position-based inclusion of "Crisis"] · OR-SCOPE-4 minimal object + review flag; parallel to OT-SCP-07 · open=constitutive evidence.
OT-CP-19 · "Little is known about trust and commitment." · given=LIMITED/evidence · type=construct · obj="trust and commitment" · comp=local · not=[two records] · OR-CONJ-1: one object, coordination_present=true · open=upstream segmentation may split.
OT-CP-20 · "Few studies examine trust and commitment." · given=LIMITED/evidence · type=construct · obj="trust and commitment" · comp=local · not=[Step-8 split] · same rule · open=segmentation.

**Relationship (20).**
OT-REL-01 · "Little is known about how digital surveillance affects employee trust in remote teams." · given=LIMITED/evidence · type=relationship · obj="how digital surveillance affects employee trust" · args=(digital surveillance; affects; directed_a1_to_a2; employee trust) · comp=local · not=["in remote teams"] · scope excluded; direction asserted · open=—.
OT-REL-02 · "Whether X predicts Y remains unexamined." · given=ABSENT/evidence · type=relationship · obj="whether X predicts Y" · args=(X; predicts; directed_a1_to_a2; Y) · comp=local · not=[] · whether-complement · open=—.
OT-REL-03 · "The relationship between X and Y is poorly understood." · given=LIMITED/unspecified · type=relationship · obj="the relationship between X and Y" · norm="relationship between X and Y" · args=(X; relationship_between; undirected; Y) · comp=local · not=[X→Y] · undirected nominal (OR-REL-3) · open=—.
OT-REL-04 · "Evidence on the association between X and Y is limited." · given=LIMITED/evidence · type=relationship · obj="the association between X and Y" · args=(X; associated_with; undirected; Y) · comp=local · not=[evidence] · carrier absorbed · open=—.
OT-REL-05 · "The effect of X on Y has not been examined." · given=ABSENT/evidence · type=relationship · obj="the effect of X on Y" · args=(X; effect_on; directed_a1_to_a2; Y) · comp=local · not=[] · directional lexeme · open=—.
OT-REL-06 · "Few studies examine whether X shapes Y." · given=LIMITED/evidence · type=relationship · obj="whether X shapes Y" · args=(X; shapes; directed_a1_to_a2; Y) · comp=local · not=[studies] · relational clause under carrier · open=—.
OT-REL-07 · "The interaction between leadership style and team autonomy remains unexplored." · given=ABSENT/evidence · type=relationship · obj="the interaction between leadership style and team autonomy" · args=(leadership style; interaction; undirected; team autonomy) · comp=local · not=[forced direction] · OR-REL-3 · open=—.
OT-REL-08 · "How X influences Y is unknown." · given=ABSENT/evidence · type=relationship · obj="how X influences Y" · args=(X; influences; directed_a1_to_a2; Y) · comp=local · not=[] · — · open=—.
OT-REL-09 · "X's link to Y is understudied." · given=LIMITED/evidence · type=relationship · obj="X's link to Y" · args=(X; link_to; undirected; Y) · comp=local · not=[direction] · link = non-directional · open=—.
OT-REL-10 · "Little is known about whether X is associated with Y." · given=LIMITED/evidence · type=relationship · obj="whether X is associated with Y" · args=(X; associated_with; undirected; Y) · comp=local · not=[] · — · open=—.
OT-REL-11 · "How X affects Y through M remains unclear." · given=LIMITED/unspecified · type=relationship · obj="how X affects Y through M" · args=(X; affects; directed_a1_to_a2; Y; qualifier="through M") · comp=local · not=[flattening to (X,Y)] · OR-REL-4/5 · open=—.
OT-REL-12 · "The effect of X on Y under high uncertainty is unexamined." · given=ABSENT/evidence · type=relationship · obj="the effect of X on Y under high uncertainty" · args=(X; effect_on; directed_a1_to_a2; Y; qualifier="under high uncertainty") · comp=local · not=[qualifier-as-scope deletion] · conditioning qualifier semantically identifying · open=qualifier-vs-scope pilot check.
OT-REL-13 · "Whether X causes Y remains untested." · given=UNTESTED/evidence · type=relationship · obj="whether X causes Y" · args=(X; causes; directed_a1_to_a2; Y) · comp=local · not=[proposition artifact] · wh-head (OR-PREC-3) · open=—.
OT-REL-14 · "The pathway from X to Y via M and then N is not understood." · given=LIMITED/unspecified · type=relationship · obj="the pathway from X to Y via M and then N" · args=(X; pathway_to; directed_a1_to_a2; Y) args_complete=partial · comp=local · not=[graph invention] · chained mediation → partial · open=Step-11 richer capture.
OT-REL-15 · "Few studies examine the relationship between X and Y." · given=LIMITED/evidence · type=relationship · obj="the relationship between X and Y" · args=(X; relationship_between; undirected; Y) · comp=local · not=[] · mandated anchor · open=—.
OT-REL-16 · "X predicts Y, but this relationship remains untested." · given=UNTESTED/evidence · type=relationship · obj="this relationship" · args=(X; predicts; directed_a1_to_a2; Y) · comp=context_completed · not=[mention rewritten to the antecedent clause] · OR-COREF-1 Branch A: "this relationship" is object-denoting, so the local mention stays canonical; arguments recovered internally · open=—.
OT-REL-17 · "The impact of AI adoption on job design is rarely examined." · given=LIMITED/evidence · type=relationship · obj="the impact of AI adoption on job design" · args=(AI adoption; impact_on; directed_a1_to_a2; job design) · comp=local · not=[] · — · open=—.
OT-REL-18 · "Why X correlates with Y remains unknown." · given=ABSENT/theory · type=relationship · obj="Why X correlates with Y" · args=(X; correlates_with; undirected; Y) · comp=local · not=[direction; bracketed reconstruction as mention] · explanatory wh-span is verbatim · open=—.
OT-REL-19 · "Little is known about X and its effect on Y." · given=LIMITED/evidence · type=relationship · obj="X and its effect on Y" · args=(X; effect_on; directed_a1_to_a2; Y) · comp=local · not=[splitting] · coordination inside relational nominal preserved · open=segmentation.
OT-REL-20 · "The mechanisms linking X to Y remain unexplored." · given=ABSENT/theory · type=relationship · obj="the mechanisms linking X to Y" · args=(X; linking; directed_a1_to_a2; Y) · comp=local · not=[phenomenon "mechanisms"] · relational participle supplies both args · open=—.

**Knowledge artifacts (20).**
OT-ART-01 · "The model remains untested." · given=UNTESTED/evidence · type=knowledge_artifact · art=model · obj="the model" · norm="model" · comp=local · not=[subject matter substitute] · OR-ART-1/3 · open=—.
OT-ART-02 · "The organization's absorptive-capacity model has not been validated." · given=UNTESTED/evidence · type=knowledge_artifact · art=model · obj="the organization's absorptive-capacity model" · norm="organization's absorptive-capacity model" · comp=local · not=[synonym rewrite] · OR-TRACE-5 whitelist only · open=—.
OT-ART-03 · "This assumption is mistaken." (unique explicit antecedent: "Prior work assumes stable preferences.") · given=CHALLENGED/theory · type=knowledge_artifact · art=assumption · obj="This assumption" · comp=context_completed (trace→"stable preferences") · not=[rewritten mention; fabricated content] · anaphor completed per OR-COREF-1 · open=—.
OT-ART-04 · "Existing theories cannot explain X." · given=CONSTRAINED/theory · type=knowledge_artifact · art=theory · obj="existing theories" · about=— · comp=local · not=[about="X"] · X = capability target (OR-ABOUT-2) · open=—.
OT-ART-05 · "Existing theories of organizational resilience cannot explain rapid adaptation." · given=CONSTRAINED/theory · type=knowledge_artifact · art=theory · obj="Existing theories of organizational resilience" · about="organizational resilience" · comp=local · not=[about="rapid adaptation"] · OR-ABOUT-1 vs -2 anchor · open=—.
OT-ART-06 · "The framework has yet to be evaluated." · given=UNTESTED/evidence · type=knowledge_artifact · art=framework · obj="the framework" · comp=local · not=[] · label-driven kind · open=—.
OT-ART-07 · "The prevailing assumption of stable preferences is empirically unsupported." · given=ABSENT/evidence · type=knowledge_artifact · art=assumption · obj="the prevailing assumption of stable preferences" · about="stable preferences" · comp=local · not=[] · of-complement about · open=—.
OT-ART-08 · "Model M breaks down under scarcity." · given=CHALLENGED/theory · type=knowledge_artifact · art=model · obj="Model M" · comp=local · not=["under scarcity" in object] · condition = predicate context, not object · open=—.
OT-ART-09 · "No theory of knowledge hiding exists." · given=ABSENT/theory · type=phenomenon · obj="knowledge hiding" · comp=local · not=[theory artifact object] · OR-ART-2 existential · open=—.
OT-ART-10 · "No model explains employee turnover." · given=ABSENT/theory · type=phenomenon · obj="employee turnover" · comp=local · not=[model artifact] · OR-ART-2; DP-PREC-2 · open=—.
OT-ART-11 · "No validated measure exists for psychological safety." · given=ABSENT/method · type=construct · obj="psychological safety" · comp=local · not=[measure artifact] · OR-ART-7a · open=—.
OT-ART-12 · "No validated method exists to measure employee engagement." · given=ABSENT/method · type=construct · obj="employee engagement" · comp=local · not=[fabricated method artifact] · OR-ART-7a; mandated 8B §23 anchor · open=—.
OT-ART-13 · "The proposition that X causes Y remains untested." · given=UNTESTED/evidence · type=knowledge_artifact · art=proposition · obj="the proposition that X causes Y" · about="X causes Y" · comp=local · not=[relationship(X,Y) decomposition] · OR-ART-5 · open=Step-9 identity vs relationship objects.
OT-ART-14 · "The prediction that X predicts Y lacks empirical support." · given=ABSENT/evidence · type=knowledge_artifact · art=proposition · obj="the prediction that X predicts Y" · about="X predicts Y" · comp=local · not=[] · head=prediction · open=—.
OT-ART-15 · "This hypothesis has never been examined." (unique antecedent: "H1: monitoring increases stress.") · given=ABSENT/evidence · type=knowledge_artifact · art=proposition · obj="This hypothesis" · comp=context_completed · not=[content invention] · anaphor completed per OR-COREF-1 · open=—.
OT-ART-16 · "No measure of trust captures temporal change." · given=CONSTRAINED/method · type=knowledge_artifact · art=measure · obj="measure of trust" · about="trust" · comp=local · not=[object=trust] · OR-PREC-4 head=measure; existing-class capability reading (plural-generic "no measure … captures" predicates incapacity of the measure class, not nonexistence) · open=existential-vs-capability reading pilot.
OT-ART-17 · "Reported effects are artifacts of measurement error." · given=CHALLENGED/evidence · type=knowledge_artifact · art=proposition · obj="reported effects" · comp=local · not=[phenomenon reading] · OR-ART-4 · open=—.
OT-ART-18 · "Existing methods cannot distinguish X from Y." · given=CONSTRAINED/method · type=knowledge_artifact · art=method · obj="Existing methods" · comp=local · not=[measure mislabel; X or Y as object] · OR-ART-7c (GS-1.3) · open=—.
OT-ART-19 · "Cross-sectional designs cannot identify temporal ordering." · given=CONSTRAINED/method · type=knowledge_artifact · art=method · obj="Cross-sectional designs" · comp=local · not=[phenomenon "designs"; "temporal ordering" as object] · OR-ART-7c · open=—.
OT-ART-20 · "Established survey approaches systematically misstate X." · given=CHALLENGED/method · type=knowledge_artifact · art=method · obj="Established survey approaches" · comp=local · not=[measure mislabel] · OR-ART-7c; frozen DPR anchor · open=—.

**Carrier vs object (15).**
OT-CAR-01 · "Evidence about X is limited." · given=LIMITED/evidence · obj="X" · comp=local · object_type_assertion=NOT_TESTED · not=[evidence] · OR-CARRIER-1: carrier absorption is the tested mechanic · open=—.
OT-CAR-02 · "Empirical evidence on X is scarce." · given=LIMITED/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[empirical evidence] · — · open=—.
OT-CAR-03 · "Little is known about X." · given=LIMITED/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[known] · Case A carrier · open=—.
OT-CAR-04 · "Theoretical understanding of X is limited." · given=LIMITED/theory · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[theoretical understanding] · — · open=—.
OT-CAR-05 · "Research on X remains sparse." · given=LIMITED/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[research] · — · open=—.
OT-CAR-06 · "The literature on X is thin." · given=LIMITED/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[literature] · — · open=—.
OT-CAR-07 · "Data about X are lacking." · given=ABSENT/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[data] · — · open=—.
OT-CAR-08 · "What is known about X is fragmentary." · given=LIMITED/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[what-is-known] · free-relative carrier · open=—.
OT-CAR-09 · "Theory about X is limited." · given=LIMITED/theory · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[theory artifact] · mass-carrier reading (OR-CARRIER-2) · open=—.
OT-CAR-10 · "The theory remains untested." · given=UNTESTED/evidence · type=knowledge_artifact · art=theory · obj="the theory" · comp=local · not=[carrier reading] · determinate artifact · open=—.
OT-CAR-11 · "Knowledge about the model is limited." · given=LIMITED/evidence · type=knowledge_artifact · art=model · obj="the model" · comp=local · not=[knowledge] · OR-CARRIER-3 topic-artifact · open=—.
OT-CAR-12 · "Little is known about models of X." · given=LIMITED/evidence · type=knowledge_artifact · art=model · obj="models of X" · about="X" · comp=local · not=[obj=X] · OR-CARRIER-3 · open=—.
OT-CAR-13 · "Little is known about Theory X." · given=LIMITED/evidence · type=knowledge_artifact · art=theory · obj="Theory X" · comp=local · not=[Theory X as deficient artifact reading] · subject-matter reading (§41.23) · open=—.
OT-CAR-14 · "Findings on X remain scarce." · given=LIMITED/evidence · obj="X" · object_type_assertion=NOT_TESTED · comp=local · not=[findings] · findings-as-knowledge-state carrier · open=—.
OT-CAR-15 · "Understanding of why X persists is limited." · given=LIMITED/unspecified · obj="why X persists" · object_type_assertion=NOT_TESTED · comp=local · not=[understanding] · unspecified kind ≠ unresolved object · open=—.

**Scope vs object (15).**
OT-SCP-01 · "Evidence about employee engagement is limited among frontline workers." · given=LIMITED/evidence · type=construct · obj="employee engagement" · comp=local · not=["among frontline workers"; population field] · OR-SCOPE-1 · open=—.
OT-SCP-02 · "Little is known about employee engagement among nurses." · given=LIMITED/evidence · type=construct · obj="employee engagement" · comp=local · not=[among-PP] · population scope · open=—.
OT-SCP-03 · "Little is known about nurse engagement." · given=LIMITED/evidence · type=construct · obj="engagement" · comp=local · not=["nurse" in object absent explicit lexicalization evidence] · OR-SCOPE-PRE-1/OR-SCOPE-3: nurse = population scope in prenominal position · open=lexicalization evidence would retain the compound.
OT-SCP-04 · "Evidence about trust is limited in multinational firms." · given=LIMITED/evidence · type=construct · obj="trust" · comp=local · not=[in-PP] · setting scope · open=—.
OT-SCP-05 · "Evidence about cross-national trust differences is limited." · given=LIMITED/evidence · type=phenomenon · obj="cross-national trust differences" · comp=local · not=[splitting descriptor] · constitutive pattern · open=—.
OT-SCP-06 · "Little is known about adaptation during crises." · given=LIMITED/evidence · type=phenomenon · obj="adaptation" · comp=local · not=["during crises"] · temporal scope · open=—.
OT-SCP-07 · "Little is known about crisis adaptation." (no local wording fixing crisis as semantic content) · given=LIMITED/evidence · type=phenomenon · obj="adaptation" · comp=local · not=[forced inclusion of "crisis"] · OR-SCOPE-4: constitutive vs temporal reading irreducible → minimal object + review flag · open=constitutive evidence would retain "crisis adaptation".
OT-SCP-08 · "Few studies examine leadership in SMEs." · given=LIMITED/evidence · type=construct · obj="leadership" · comp=local · not=["in SMEs"] · industry scope · open=—.
OT-SCP-09 · "Few studies examine SME leadership practices." · given=LIMITED/evidence · type=phenomenon · obj="leadership practices" · comp=local · not=["SME" in object absent lexicalization evidence] · OR-SCOPE-PRE-1: SME = industry scope prenominally realized · open=lexicalization evidence.
OT-SCP-10 · "Trust across countries is understudied." · given=LIMITED/evidence · type=construct · obj="trust" · comp=local · not=["across countries"] · geographic scope · open=—.
OT-SCP-11 · "Little is known about digital surveillance in remote teams." · given=LIMITED/evidence · type=phenomenon · obj="digital surveillance" · comp=local · not=["in remote teams"] · setting scope · open=—.
OT-SCP-12 · "Adoption of AI is poorly understood at the team level." · given=LIMITED/unspecified · type=phenomenon · obj="adoption of AI" · comp=local · not=["at the team level"] · level-of-analysis scope · open=—.
OT-SCP-13 · "Recent research on transformation is limited." · given=LIMITED/evidence · type=phenomenon · obj="transformation" · comp=local · not=["recent" in object] · "recent" modifies carrier state · open=—.
OT-SCP-14 · "Long-term adaptation dynamics remain unexplored." · given=ABSENT/evidence · type=phenomenon · obj="adaptation dynamics" · comp=local · not=[forced inclusion of "long-term"] · OR-SCOPE-4: temporal-constitutive vs temporal-scope reading irreducible → minimal object + review flag · open=constitutive evidence retains the full phrase.
OT-SCP-15 · "Engagement is understudied over the past decade." · given=LIMITED/evidence · type=construct · obj="engagement" · comp=local · not=["over the past decade"] · temporal adjunct on carrier state · open=—.

**Coreference / completion (10).**
OT-COR-01 · "Prior research assumes stable preferences, but this assumption is empirically unsupported." · given=ABSENT/evidence · type=knowledge_artifact · art=assumption · obj="this assumption" · comp=context_completed (trace→"stable preferences") · not=[rewritten mention] · OR-COREF-1 Branch A · open=—.
OT-COR-02 · "Prior work has documented several coordination mechanisms in co-located teams. These mechanisms remain unexplored in distributed settings." · given=ABSENT/evidence · type=phenomenon · obj="coordination mechanisms" · comp=context_completed (antecedent span) · not=["These mechanisms" as canonical mention; mixed mention spans] · OR-COREF-1 Branch C: the frozen GS-1.3 V3 pattern — canonical mention = antecedent referent wording; local anaphor stays in context_support (I-44/I-45) · open=—.
OT-COR-03 · "This issue remains unresolved." (unique antecedent: "whether X causes Y") · given=ABSENT/unspecified · type=relationship · obj="whether X causes Y" · args=(X; causes; directed_a1_to_a2; Y) · comp=context_completed · not=["This issue" as canonical affected_object] · OR-COREF-1 Branch B: issue/reference wrapper resolves to the antecedent relational phrase (I-44) · open=—.
OT-COR-04 · "Prior work provides evidence on supplier adaptation. Such evidence remains limited." · given=LIMITED/evidence · type=phenomenon · obj="supplier adaptation" · comp=context_completed (antecedent span containing "supplier adaptation") · not=["Such evidence" as canonical affected_object] · OR-COREF-1 Branch B: carrier anaphor resolves to antecedent subject matter (I-44); local phrase remains context/dependency evidence · open=—.
OT-COR-05 · "Little is known about employee turnover. This gap persists." · given=LIMITED/evidence · type=phenomenon · obj="employee turnover" · comp=context_completed · not=["This gap" as canonical affected_object] · OR-COREF-1 Branch B: gap-reference expression stays in context-support traceability; canonical object = antecedent referent (I-44; GS-1.3 invalid ex. 35) · open=—.
OT-COR-06 · "This theory cannot account for Y." (unique antecedent: "Theory T") · given=CONSTRAINED/theory · type=knowledge_artifact · art=theory · obj="This theory" · comp=context_completed · not=[mention rewritten to "Theory T"; about=Y] · OR-COREF-1 Branch A: object-denoting anaphor keeps the local mention · open=—.
OT-COR-07 · "It remains untested." (two candidate antecedents: the model; the assumption) · given=UNTESTED/evidence · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[forced choice] · OR-COREF-1 Branch D · open=review.
OT-COR-08 · "Prior studies explain adoption but not retention." · given=ABSENT/evidence · type=phenomenon · obj="retention" · comp=context_completed (ellipsis trace→"explain") · not=[semantic reconstruction beyond gap of predicate] · OR-ELLIPSIS-1 · open=—.
OT-COR-09 · "Measures exist for trust but not for commitment." · given=ABSENT/method · type=construct · obj="commitment" · comp=context_completed (shared head "measures … for") · not=[measure-artifact object] · existential ellipsis → OR-ART-2 target · open=—.
OT-COR-10 · "Theories explain onset, though not persistence." · given=ABSENT/theory · type=phenomenon · obj="persistence" · comp=context_completed · not=[] · contrastive ellipsis · open=—.

**Ambiguous / unresolved (11).**
OT-AMB-01 · "Much remains unknown." · given=LIMITED/evidence · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[fabrication; "unspecified" value] · OR-UNCERTAIN-1 · open=review routing.
OT-AMB-02 · "The literature is limited." · given=LIMITED/evidence · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[literature-as-object] · no subject matter · open=review.
OT-AMB-03 · "This remains poorly understood." (no unique antecedent) · given=LIMITED/unspecified · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[distant inference] · — · open=review.
OT-AMB-04 · "The issue remains unresolved." (no antecedent) · given=LIMITED/unspecified · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[] · — · open=review.
OT-AMB-05 · "Two competing turnover models have been proposed. These models fail to explain it." ("it" has multiple candidate antecedents) · given=CONSTRAINED/theory · type=knowledge_artifact · art=model · obj="These models" · comp=context_completed (unique antecedent for "These models") · not=[choosing "it" scientifically; marking the object unresolved] · completion_status describes affected-object completion ONLY — the object is resolved (Branch A); the predicate-complement ambiguity ("it") is a NON-OBJECT unresolved item flagged for review · open=predicate-target adjudication.
OT-AMB-06 · "Little is known about it."  (ambiguous "it") · given=LIMITED/evidence · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[forced] · — · open=review.
OT-AMB-07 · "This approach has limitations." (no recoverable antecedent) · given=CONSTRAINED/unspecified · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[invented artifact_kind] · §41.16 generic label; no licensed artifact label locally resolvable · open=review.
OT-AMB-08 · "Understanding remains incomplete." · given=LIMITED/unspecified · type=NO_CANONICAL_OBJECT · obj=ABSENT · comp=unresolved · not=[carrier-as-object] · bare carrier · open=review.
OT-AMB-09 · "X was poorly understood until recently." · given=LIMITED/unspecified · obj="X" · comp=local · object_type_assertion=NOT_TESTED · not=[temporal status in object] · OR-TRACE-3 · open=currency decided upstream/downstream.
OT-AMB-10 · "Smith argues that little is known about X." · given=LIMITED/evidence · obj="X" · comp=local · object_type_assertion=NOT_TESTED · not=[attribution altering object] · OR-TRACE-2; GIVEN applies to the local attributed deficiency proposition · open=Step-5 adoption.
OT-AMB-11 · "This assumption is mistaken." (no recoverable antecedent) · given=CHALLENGED/theory · type=NO_CANONICAL_OBJECT · art=NOT_APPLICABLE · obj=ABSENT · comp=unresolved · not=["This assumption" as canonical affected_object; fabricated assumption content] · although "assumption" supplies an apparent artifact head, the frozen schema requires an identifiable source-grounded affected referent before a canonical gap_record can be finalized (§41.4; I-44); the item remains in review/candidate handling · open=antecedent supply.

**Practice alignment (10).**
OT-PA-01 · "No mechanism exists for translating research findings into practice." · given=ABSENT/practice_alignment · type=phenomenon · obj="translating research findings into practice" · comp=local · not=[mechanism-as-object; generic practice-gap] · OR-PA-1 · open=Step-9 identity.
OT-PA-02 · "Translation of research into practice remains limited." · given=LIMITED/practice_alignment · type=phenomenon · obj="Translation of research into practice" · norm="translation of research into practice" · comp=local · not=[] · OR-PA-2 · open=—.
OT-PA-03 · "Barriers constrain the translation of research into practice." · given=CONSTRAINED/practice_alignment · type=phenomenon · obj="the translation of research into practice" · comp=local · not=[barriers-as-object] · OR-PA-3 · open=B/C identity → Step 9.
OT-PA-04 · "Research and practice remain poorly aligned." · given=DISCONNECTED/practice_alignment · type=relationship · obj="Research and practice remain poorly aligned" (alignment-state phrase) · args=(research; alignment; undirected; practice) · comp=local · not=[phenomenon collapse; forced direction] · OR-PA-4: the deficient content is the research–practice alignment state · open=—.
OT-PA-05 · "Research has not translated into practice." · given=DISCONNECTED/practice_alignment · type=relationship · obj="Research has not translated into practice" · args=(Research; translated into; directed_a1_to_a2; practice) · comp=local · not=[ellipsis characters in mention] · verbatim clause span (§41.10 license); disrelation with directional lexeme · open=—.
OT-PA-06 · "Research and practice are not linked on X." · given=DISCONNECTED/practice_alignment · type=relationship · obj="Research and practice are not linked on X" · args=(Research; linked; undirected; practice; qualifier="on X") · comp=local · not=[X as sole object; ellipsis in mention] · verbatim clause span; unlinked state (DP-PREC-15) · open=—.
OT-PA-07 · "The research-practice divide persists in healthcare." · given=DISCONNECTED/practice_alignment · type=relationship · obj="the research-practice divide" · args=(research; divide; undirected; practice) · comp=local · not=["in healthcare"] · setting scope excluded · open=—.
OT-PA-08 · "Uptake of research findings by practitioners remains limited." · given=LIMITED/practice_alignment · type=phenomenon · obj="Uptake of research findings by practitioners" · comp=local · not=[practitioners→scope] · practitioners are process participants, object-internal · open=—.
OT-PA-09 · "Institutional barriers constrain research-to-practice translation." · given=CONSTRAINED/practice_alignment · type=phenomenon · obj="research-to-practice translation" · comp=local · not=[institutional barriers] · OR-PA-3 · open=—.
OT-PA-10 · "No pathway exists for moving evidence into managerial practice." · given=ABSENT/practice_alignment · type=phenomenon · obj="moving evidence into managerial practice" · comp=local · not=[pathway-as-object] · OR-PA-1 pattern · open=—.

**Support / testing (10).**
OT-ST-01 · "Assumption X lacks empirical support." · given=ABSENT/evidence · type=knowledge_artifact · art=assumption · obj="Assumption X" · comp=local · not=[evidence-as-object] · OR-ART-3 · open=—.
OT-ST-02 · "No empirical evidence supports assumption X." · given=ABSENT/evidence · type=knowledge_artifact · art=assumption · obj="assumption X" · comp=local · not=[evidence] · supported item bears deficiency · open=—.
OT-ST-03 · "The proposition that X causes Y lacks support." · given=ABSENT/evidence · type=knowledge_artifact · art=proposition · obj="the proposition that X causes Y" · about="X causes Y" · comp=local · not=[relationship decomposition] · — · open=Step-9.
OT-ST-04 · "The relationship between X and Y has weak support." · given=LIMITED/evidence · type=relationship · obj="the relationship between X and Y" · args=(X; relationship_between; undirected; Y) · comp=local · not=[proposition artifact] · relational head · open=—.
OT-ST-05 · "The model remains untested." · given=UNTESTED/evidence · type=knowledge_artifact · art=model · obj="the model" · comp=local · not=[] · — · open=—.
OT-ST-06 · "The proposition that X causes Y has not been tested." · given=UNTESTED/evidence · type=knowledge_artifact · art=proposition · obj="the proposition that X causes Y" · about="X causes Y" · comp=local · not=[] · — · open=—.
OT-ST-07 · "Measure X has not been validated." · given=UNTESTED/evidence · type=knowledge_artifact · art=measure · obj="Measure X" · comp=local · not=[X-as-object] · artifact + denied act · open=—.
OT-ST-08 · "The framework has yet to be evaluated." · given=UNTESTED/evidence · type=knowledge_artifact · art=framework · obj="the framework" · comp=local · not=[] · — · open=—.
OT-ST-09 · "Support for the stable-preferences assumption is mixed." · given=CONFLICTING/evidence · type=knowledge_artifact · art=assumption · obj="the stable-preferences assumption" · comp=local · not=[support-as-object] · carrier "support" absorbed · open=—.
OT-ST-10 · "Hypothesis H1 remains unverified." · given=UNTESTED/evidence · type=knowledge_artifact · art=proposition · obj="Hypothesis H1" · comp=local · not=[] · hypothesis head → proposition · open=—.

## 41.44 Adversarial minimal-pair suite (40 comparisons; left object ‖ right object · deciding rule · outside Step 8)

MP-01 · "Little is known about X." ‖ "Existing theories cannot explain X." · X ‖ theory artifact "existing theories" · OR-CARRIER-1 vs OR-ART-1 · relation/kind upstream.
MP-02 · "Evidence about X is limited." ‖ "Evidence itself is unreliable." · X ‖ unresolved (bare carrier challenged; no subject matter) · OR-CARRIER-1 vs OR-UNCERTAIN-1 · Step-5/6 status of right.
MP-03 · "Theoretical understanding of X is limited." ‖ "The existing theory cannot explain X." · X ‖ theory artifact · OR-CARRIER-2 · —.
MP-04 · "Little is known about whether X affects Y." ‖ "The proposition that X affects Y remains untested." · relationship(X,Y) ‖ proposition artifact · OR-PREC-3 head rule · Step-9 identity.
MP-05 · "Few studies examine the relationship between X and Y." ‖ "The model linking X and Y remains untested." · relationship(X,Y) ‖ model artifact · head rule · Step-9.
MP-06 · "Little is known about employee trust among nurses." ‖ "Little is known about nurse trust." · "employee trust" (+ population scope) ‖ "trust" (+ population scope; "nurse" prenominal) · OR-SCOPE-1 and OR-SCOPE-3/OR-SCOPE-PRE-1: identical scope ownership across positions; "employee" retained only as sense-fixing carve-out · lexicalization evidence; Step-9 identity.
MP-07 · "Evidence about trust is limited in multinational firms." ‖ "Evidence about cross-national trust differences is limited." · trust ‖ phenomenon "cross-national trust differences" · OR-SCOPE-1/3 · —.
MP-08 · "Little is known about adaptation during crises." ‖ "Little is known about crisis adaptation." · "adaptation" (+ temporal scope) ‖ "adaptation" (+ review flag per OR-SCOPE-4; constitutive reading requires evidence) · OR-SCOPE-3 position invariance: word order alone never differentiates · constitutive evidence; Step-9.
MP-09 · "The model remains untested." ‖ "Knowledge about the model is limited." · model artifact (deficiency-bearer) ‖ model artifact (topic; OR-CARRIER-3) · target vs topic route · relation upstream.
MP-10 · "Assumption X lacks empirical support." ‖ "Evidence about assumption X is limited." · assumption artifact ‖ assumption artifact as topic · OR-ART-3 vs OR-CARRIER-3 · kind upstream.
MP-11 · "No empirical evidence supports assumption X." ‖ "No evidence exists about assumption X." · assumption artifact ‖ assumption artifact as topic (existential carrier absence) · OR-ART-3 vs OR-CARRIER-1/3 · Step-9.
MP-12 · "No validated measure exists for X." ‖ "X has not been measured." · X (OR-ART-2) ‖ X (act denial; measurement-of-X target) · both object X; relation/kind differ upstream · —.
MP-13 · "Existing measures cannot capture X." ‖ "Measurement of X is rare." · measure artifact (never method — OR-ART-7b) ‖ phenomenon "measurement of X" · artifact-bearer vs scarce-activity · —.
MP-14 · "No model explains X." ‖ "Little is known about models of X." · X ‖ knowledge_artifact·model "models of X" (about=X) · OR-ART-2 vs OR-CARRIER-3 · Step-9.
MP-15 · "No mechanism exists for translating research into practice." ‖ "Research and practice remain disconnected." · phenomenon "translating research into practice" ‖ relationship(research, practice) · OR-PA-1 vs OR-PA-4 · Step-9 identity.
MP-16 · "Translation of research into practice remains limited." ‖ "Barriers constrain research-to-practice translation." · phenomenon (same process, distinct mentions) ‖ phenomenon · OR-PA-2 vs OR-PA-3 · identity → Step 9 only.
MP-17 · "The assumption is mistaken." ‖ "The assumption is poorly understood." · assumption artifact ‖ assumption artifact as topic of limited knowledge · OR-ART-1 vs OR-CARRIER-3 · relation upstream.
MP-18 · "Reported effects are artifacts of measurement error." ‖ "Evidence about the reported effects is limited." · proposition artifact "reported effects" ‖ proposition-as-topic · OR-ART-4 vs OR-CARRIER-3 · —.
MP-19 · "These mechanisms remain unexplored." ‖ "These mechanisms remain central to the model." · canonical object = antecedent referent wording (e.g., "coordination mechanisms"; Branch C, I-44) ‖ no deficiency proposition (no Step-8 input) · deficiency predicate presence; GS-1.3 V3 completion · Step-5 upstream.
MP-20 · "This theory remains untested." ‖ "This relationship remains untested." · theory artifact, mention "This theory" ‖ relationship, mention "This relationship" — both object-denoting (Branch A), both local mentions canonical when uniquely resolved · head lexeme decides kind; I-44 licenses both local mentions · completion antecedents.
MP-21 · "No theory of X exists." ‖ "The theory of X remains untested." · X ‖ theory artifact "the theory of X" (about=X) · OR-ART-2 vs OR-ART-1 · —.
MP-22 · "How X affects Y is unknown." ‖ "Whether X and Y are related is unknown." · directed relationship ‖ undirected relationship · OR-REL-3 · —.
MP-23 · "The relationship between X and Y is unexamined." ‖ "The effect of X on Y is unexamined." · undirected ‖ directed X→Y · lexeme-driven direction · —.
MP-24 · "How X affects Y through M remains unclear." ‖ "How X affects Y remains unclear." · qualified relationship (through M) ‖ plain relationship · OR-REL-4/5 no flattening · Step-9 identity.
MP-25 · "Little is known about employee responses to algorithmic monitoring." ‖ "Little is known about how employees respond to algorithmic monitoring." · phenomenon ‖ relationship · OR-PHEN-2 vs OR-REL-1 · Step-9.
MP-26 · "Few studies examine trust and commitment." ‖ "Few studies examine trust." · one coordinated object ‖ single construct · OR-CONJ-1 · segmentation/Step-9.
MP-27 · "Prior studies explain adoption but not retention." ‖ "Prior studies do not explain retention." · retention (ellipsis-completed) ‖ retention (explicit) · OR-ELLIPSIS-1 · —.
MP-28 · "Measures exist for trust but not for commitment." ‖ "No validated measure exists for commitment." · commitment (ellipsis) ‖ commitment (explicit existential) · completion parity · —.
MP-29 · "Smith argues that little is known about X." ‖ "Little is known about X." · X ‖ X · OR-TRACE-2 attribution-invariance · Step-5 adoption.
MP-30 · "X was poorly understood until recently." ‖ "X is poorly understood." · X ‖ X · OR-TRACE-3 temporal-invariance · currency upstream.
MP-31 · "This gap motivates our study." ‖ "Little is known about X." · left is a Step-5 boundary/reference matter — Step 8 assigns NO affected_object unless Step 5 has routed a local GAP proposition, and then only via Branch B to a unique antecedent referent, never "This gap" ‖ X · I-44 + Step-5 ownership; Step 8 never overrides Step 5 · Step-5 routing of left.
MP-32 · "The organization's absorptive capacity is poorly understood." ‖ "Knowledge assimilation capability is poorly understood." · distinct mentions; never equated · OR-TRACE-5 no synonym mapping · Step-9 identity.
MP-33 · "Trust in leaders is understudied." ‖ "Trust is understudied among leaders." · "Trust in leaders" (the in-complement names the attitude's target — removal changes WHAT attitude, so constitutive under OR-SCOPE-2) ‖ "Trust" + population scope (bearers) · constitutive-complement vs bearer-population, decided semantically not positionally · —.
MP-34 · "No analytical procedure can recover X." ‖ "Existing analytical procedures cannot recover X." · X (existential; no fabricated artifact) ‖ method artifact "Existing analytical procedures" · OR-ART-7a vs OR-ART-7c — the mandated NO-METHOD-EXISTS vs EXISTING-METHOD-DEFICIENT pair · Step-9 identity.
MP-35 · "Hypothesis H1 remains untested." ‖ "Whether X causes Y remains untested." · proposition artifact ‖ relationship · head rule · Step-9.
MP-36 · "Existing theories of resilience cannot explain rapid adaptation." ‖ "Existing theories cannot explain rapid adaptation." · theory artifact + about=resilience ‖ theory artifact, no about · OR-ABOUT-1/2 · —.
MP-37 · "The assumption that preferences are stable is untested." ‖ "This assumption is untested." · assumption artifact + about = "preferences are stable" ‖ assumption artifact, mention "This assumption" (Branch A) when a unique antecedent exists; with no recoverable antecedent → NO_CANONICAL_OBJECT (OT-AMB-11) · about machinery vs object-denoting completion · antecedent presence.
MP-38 · "Uptake of research by practitioners is limited." ‖ "Practitioners lack knowledge of research." · phenomenon (pa process; practitioners internal) ‖ no A.1-E object (world-deficit; Step-5 OTHER) · pa-participant vs practitioner-subject · Step-5 upstream.
MP-39 · "Why X persists is not understood." ‖ "X persists." · "why X persists" object ‖ no deficiency proposition · deficiency predicate requirement · Step-5.
MP-40 · "The literature is limited." ‖ "The literature on X is limited." · unresolved ‖ X · OR-UNCERTAIN-1 vs OR-CARRIER-1 · review routing.

## 41.45 Validation / Step-3 mapping

Step-8 evaluation dimensions (protocol-compatible; no numeric thresholds frozen here): affected-object span correctness · object_kind correctness · artifact_kind correctness · relationship-argument correctness · direction correctness · about correctness · scope-leakage rate · carrier/object confusion rate · forced-object rate · coreference-completion correctness. All defects map onto the frozen Step-3 classes: annotation_error · rulebook_ambiguity · schema_insufficiency (the former Step-8-specific defect SI-OR-1 was resolved by GS-1.3 and is retired; the general class remains) · genuine_epistemic_ambiguity. Nothing in Step 3 is redesigned.

## 41.46 Error labels (component-level only; never replacing Step-3 classes)

E-OBJECT-SPAN · E-OBJECT-TYPE · E-ARTIFACT-SUBTYPE · E-REL-ARGUMENT · E-REL-DIRECTION · E-ABOUT · E-SCOPE-LEAKAGE · E-CARRIER-OBJECT · E-COREF · E-FORCED-OBJECT · E-OVEREXTRACTION · E-UNDEREXTRACTION.

## 41.47 Versioning

`object_rules_version = A1E-OR-1.1`, pinned by downstream Steps 9/11/13; pins `A1E-GS-1.3`. Rule IDs are permanent; retired IDs are never reused. Amendment classes: clarifying (wording, no semantic scope change) · semantic (rule meaning changes; names affected rule IDs, tests, gold objects) · test-only · ontology (any object_kind/artifact_kind change — requires: affected rule IDs; affected test cases; affected gold objects; impact on Step-9 identity rules; impact on Step-11 extraction) · normalization (whitelist changes). No global invalidation mechanics are defined here.

## 41.48 Open decisions

- **OD-OR-2 (type cue-list calibration; test-only).** The stative/eventive head cue lists under OR-TYPE-2 are frozen as a rule; their lexeme inventories may be extended by clarifying amendment after pilot annotation. Alters no ordinary object representation. Blocks freeze: no. Depends: protocol pilot.
- **OD-OR-3 (coordination splitting).** Whether upstream segmentation will emit sibling propositions for coordinated referents (activating per-unit objects) is a Step-1/11 runtime matter; OR-CONJ-1 is complete either way. Blocks freeze: no. Depends: Steps 9, 11.

OD-OR-1 / SI-OR-1 is REMOVED: resolved by `A1E-GS-1.3` (artifact_kind = method) and OR-ART-7c. No must-resolve Step-8 item remains open: construct-vs-phenomenon (OR-TYPE-2), relationship (OR-REL-1, OR-REL-2, OR-REL-3, OR-REL-4, OR-REL-5), artifact (OR-ART-1, OR-ART-2, OR-ART-3, OR-ART-4, OR-ART-5, OR-ART-6a–6e, OR-ART-7a–7c), carrier-vs-object (OR-CARRIER-1, OR-CARRIER-2, OR-CARRIER-3), scope-vs-object (OR-SCOPE-1, OR-SCOPE-2, OR-SCOPE-3, OR-SCOPE-PRE-1, OR-SCOPE-4), method-like representation (OR-ART-7a–7c under GS-1.3), `about` (OR-ABOUT-1, OR-ABOUT-2, OR-ABOUT-3), coreference completion precedence (OR-COREF-1; OR-PREC-5), unresolved-object routing (OR-UNCERTAIN-1, OR-UNCERTAIN-2, OR-UNCERTAIN-3) — all frozen above.

## 41.49 Freeze check

| Check | PASS/FAIL | Evidence |
|---|---|---|
| **DEPENDENCY** | | |
| pins A1E-GS-1.3 | PASS | header; §41.2; §41.47 |
| conforms to I-44 | PASS | OR-COREF-1 Branches A–D implement it verbatim; §41.5 clarification; OT-COR-02..06; OT-AMB-11 |
| conforms to I-45 | PASS | §41.37 alignment note; OT-COR-02 must_not (mixed mention spans) |
| does not reinterpret frozen Step 2 | PASS | §41.26 Branch C hard rule: Step 8 never invents a representation competing with GS-1.3 |
| **COMPLETION** | | |
| object-denoting anaphor rule explicit | PASS | OR-COREF-1 Branch A with the frozen "This model" example |
| carrier/reference anaphor rule explicit | PASS | Branch B with the frozen "This gap" example |
| "This assumption" may remain canonical when object-denoting and resolved | PASS | OT-ART-03; MP-37 right |
| "This relationship" may remain canonical when object-denoting and resolved | PASS | OT-REL-16; MP-20 |
| "This gap" cannot be canonical affected_object when merely gap reference | PASS | Branch B; OT-COR-05; MP-31 |
| "Such evidence" cannot be canonical affected_object when merely carrier | PASS | Branch B; OT-COR-04 |
| "This issue" resolves to antecedent affected referent where applicable | PASS | OT-COR-03: mention = "whether X causes Y" |
| GS V3 pattern "These mechanisms" → antecedent "coordination mechanisms" respected | PASS | Branch C; OT-COR-02; MP-19 |
| unresolved antecedent cannot produce a canonical object | PASS | Branch D; OT-COR-07; OT-AMB-11 |
| completion never rewrites a local object-denoting mention | PASS | Branch A "never rewritten"; OT-COR-06 must_not |
| completion may use a verbatim antecedent mention where I-44 requires it | PASS | §41.5 clarification; OT-COR-04/05 |
| **UNRESOLVED** | | |
| completion_status=unresolved consistent with §41.4 | PASS | §41.4 sentence unchanged; OT-AMB-11 reshaped to match |
| unresolved affected object → NO_CANONICAL_OBJECT | PASS | OT-COR-07; OT-AMB-01..04/06/07/08/11 (obj=ABSENT) |
| OT-AMB-11 follows this rule | PASS | NO_CANONICAL_OBJECT · NOT_APPLICABLE · ABSENT · unresolved |
| predicate-complement ambiguity distinguished from object ambiguity | PASS | OT-AMB-05: object context_completed; "it" flagged as non-object unresolved |
| **TEST SCHEMA** | | |
| every test has explicit legal expected type or NOT_TESTED | PASS | complete 131-test audit: every row carries an explicit `type=` or `object_type_assertion=NOT_TESTED` (mechanical scan returns zero rows lacking both) |
| every artifact expectation legal/NOT_APPLICABLE/NOT_TESTED | PASS | 7-value enum + omission convention; OT-AMB-11 explicit NOT_APPLICABLE |
| every completion_status local/context_completed/unresolved | PASS | full-spelling scan clean |
| every GIVEN relation one legal value or NOT_TESTED | PASS | 7-relation scan; no compound values |
| every GIVEN knowledge_kind one legal value or NOT_TESTED | PASS | 5-kind scan; practice_alignment everywhere |
| no `pa` | PASS | alias scan of §41.41–41.44 clean outside the serialization contract's own prohibition list; full value used throughout (the bare token is named only there and in this check row) |
| no `per-X` | PASS | token absent from §41.40–41.44 outside the contract's prohibition list (named only there and in this check row) |
| no `LIMITED/ABSENT` | PASS | §41.42 row corrected to LIMITED, unspecified; compound scan clean |
| no compound conditional enum values | PASS | contract prohibition + scan |
| no `UNREPRESENTABLE` | PASS | token absent from §41.40–41.44 outside the contract's prohibition list (named only there and in this check row) |
| no active `SI-OR-1 route` | PASS | §41.45 retirement wording; token appears only in the contract's prohibition list, the revision-record history, and this row |
| conditional tests are split | PASS | OT-ART-03 ‖ OT-AMB-11; OT-AMB-05 context made explicit |
| **METHOD** | | |
| artifact_kind=method preserved | PASS | OR-ART-7c unchanged; OT-ART-18/19/20 |
| artifact_kind=measure preserved separately | PASS | OR-ART-7b; OT-ART-02; MP-13 |
| absent method class does not fabricate method artifact | PASS | OR-ART-7a; OT-ART-12; MP-34 left |
| existing method artifact canonically representable | PASS | OT-ART-18 "Existing methods" · method · local |
| **SCOPE** | | |
| corrected position-invariant scope rules preserved | PASS | §41.7 family untouched; OT-SCP-03/07/09/14 |
| no regression to pre-head = object | PASS | OR-SCOPE-2 "never sufficient" retained |
| no structured scope field introduced | PASS | document-wide absence |
| **VERBATIM** | | |
| every canonical mention source-grounded/verbatim | PASS | obj= audit: local or antecedent manuscript substrings only |
| antecedent canonical mention is a verbatim antecedent span | PASS | OT-COR-02 "coordination mechanisms"; OT-COR-04 "supplier adaptation"; OT-COR-05 "employee turnover" |
| no mixed surface-form mention refs | PASS | §41.37 I-45 note; OT-COR-02 must_not |
| I-45 operationally reflected in tests | PASS | OT-COR-02 must_not; §41.43 verbatim rule |
| no generated reconstruction in obj fields | PASS | bracket/ellipsis scan of obj= fields clean; OT-REL-18 verbatim wh-span |
| **REGISTRY** | | |
| every normative OR-* ID resolves to exactly one §41.40 row | PASS | token-grammar scan: zero undefined |
| no undefined OR-* IDs | PASS | same scan |
| no duplicate normative rule IDs | PASS | duplicate scan: zero |
| actual registry row count reported correctly | PASS | §41.40 contains 58 atomic rule rows; exhaustive token-to-registry scan returns zero undefined and zero duplicate normative IDs |
| **VALIDATION** | | |
| Step-3 general schema_insufficiency class remains | PASS | §41.45 lists all four frozen classes |
| specific SI-OR-1 retired/resolved | PASS | §41.45 retirement wording; §41.48 (no OD-OR-1); revision record item 3 |
| no Step-3 redesign | PASS | §41.45/41.46 map onto frozen classes only |
| **OWNERSHIP** | | |
| Step 5 boundary ownership preserved | PASS | OR-TRACE-2; MP-31 left defers to Step 5; MP-38 |
| Step 6 relation/kind ownership preserved | PASS | relation/kind everywhere GIVEN |
| Step 9 merge/identity ownership preserved | PASS | OR-CONJ-1; §41.32 note; MP "outside Step 8" column |
| Step 10 detection ownership preserved | PASS | no emission/threshold/scoring/window |
| no scientific validity/novelty judgment added | PASS | prohibited-inference column; OR-UNCERTAIN-3 |
| **CORE SEMANTICS** | | |
| carrier ≠ affected object | PASS | OR-CARRIER-1..3; §41.41 |
| artifact ≠ subject matter | PASS | OR-PREC-2; OT-CAR-10..13 |
| relationship ≠ proposition artifact | PASS | OR-PREC-3; MP-04/35 |
| method ≠ measure | PASS | OR-ART-7b/7c; GS-1.3 §4a |
| scope ≠ object | PASS | §41.7 family; OT-SCP suite |
| source completion ≠ reconstruction | PASS | OR-TRACE-1; §41.5 clarification |
| object extraction ≠ identity | PASS | Step-9 deferrals throughout |
| **FINAL MECHANICAL CORRECTION** | | |
| OT-AMB-10 given value = LIMITED/evidence exactly | PASS | corrected line; whole-field scan |
| no commentary inside any machine `given=` value | PASS | whole-field audit: every `given=` segment matches RELATION/kind exactly |
| OT-COR-01 references OR-COREF-1 Branch A | PASS | corrected line |
| OT-COR-07 references OR-COREF-1 Branch D | PASS | corrected line |
| no undefined `OR-COREF` shorthand remains | PASS | broad family-token scan clean outside the mandated correction record and this check block (the bare token is named only in those two quoting sites) |
| no obsolete "rule 6/7" language remains | PASS | phrase scan: zero occurrences outside the mandated correction record and this row |
| OR-UNCERTAIN-3 examples concern affected-object ambiguity only | PASS | §41.39 rewrite; "These models fail to explain it." removed from its examples |
| OT-AMB-05 not treated as an unresolved affected-object case | PASS | OR-UNCERTAIN-3 registry test_refs = OT-AMB-03/06, OT-COR-07; OT-AMB-05 cited only as the resolved counterexample |
| object ambiguity and predicate-side ambiguity explicitly distinguished | PASS | §41.39 caveat sentence; OT-AMB-05; UNRESOLVED block rows above |
| every normative OR-* token resolves to exactly one registry row | PASS | narrow-grammar scan zero undefined; broad-grammar family sweep zero bare tokens outside sanctioned quoting |
| registry count evidence matches the actual registry | PASS | 58 atomic rule rows counted mechanically; evidence cell unchanged and re-verified |
| no semantic rule changed | PASS | diff surface = two test rationale tokens, one given field, OR-UNCERTAIN-3 examples/registry wording, records, this block |

**All checks PASS — the A.1-E Object Rules are declared FROZEN at v1.1 (`A1E-OR-1.1`), pinned to `A1E-GS-1.3`, `A1E-BR-1.2`, `A1E-DPR-1.1`, and `A1E-SL-1.1`.**

**Proceed next to Step 9 — Merge & Gap Identity Rules.**
