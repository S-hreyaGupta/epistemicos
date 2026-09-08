# A.1-E Deficiency Predicate Registry v1.1 — EpistemicOS (Step 6)

**Status:** normative once the Freeze Check (§39.27) passes. Version string: `A1E-DPR-1.1`. Targeted revision of `A1E-DPR-1.0`.
**Document form:** complete and self-contained; independently interpretable without legacy KB files or v1.0.
**Normative frozen inputs (pinned):** `A1E_gap_extraction_contract_v1-2.md` · `A1E_gap_object_schema_v1-2.md` · `A1E_annotation_validation_protocol_v1-2.md` · `A1E_state_machine_v1-3.md` · `A1E_boundary_rulebook_v1-2.md` (**boundary input pinned at `A1E-BR-1.2`**). Closed enums unaltered: `relation ∈ {ABSENT, LIMITED, CONFLICTING, UNTESTED, CONSTRAINED, DISCONNECTED, CHALLENGED}`; `knowledge_kind ∈ {evidence, theory, method, practice_alignment, unspecified}` — no aliases, no new values.

**Revision record (v1.0 → v1.1) — exactly these corrections:** 1. UNTESTED made evidence-only. 2. Testing absence separated from evidence-support absence. 3. practice_alignment decoupled from mandatory DISCONNECTED relation. 4. Compatibility matrix re-audited (new counts 12 C / 12 A / 11 P). 5. Invented `kind_commitment` field removed. 6. Positive test counts corrected (controls and review cases no longer counted toward relation minimums). 7. Adversarial suite expanded to 35 genuine one-comparison minimal pairs. **v1.1 final-issuance corrections (pre-freeze):** (a) a challenged model/theory keeps kind = theory even when challenged on empirical grounds — grounds adverbs never re-identify the deficient item (DP-KIND-9a); "The model is empirically wrong." → CHALLENGED+theory. (b) ABSENT×practice_alignment reassessed to ALLOWED_IF_EXPLICIT: a missing research→practice bridge ("no mechanism exists for translating…") → ABSENT+practice_alignment (DP-KIND-4a); unlinked-state wording → DISCONNECTED+practice_alignment (DP-PREC-15); missing research method/measure/design → ABSENT+method. Matrix recount 12 C / 13 A / 10 P. No other semantics changed.

---

## 39.1 Purpose and ownership boundary

Step 6 answers exactly one question: **given a proposition already classified GAP under `A1E-BR-1.2`, what deficiency pair does the manuscript assert?** Output: `(relation, knowledge_kind)`. The contract primitive is relation + knowledge_kind + affected_object; **Step 6 owns only relation and knowledge_kind; Step 8 owns affected_object.**

Step 6 certifies extraction fidelity only. It does not determine: whether the gap exists; whether the literature supports it; importance or novelty; any A.1-C gap type, rhetorical mode, or construction; scope/context classification; affected-object type; merge identity; detection signals; verification verdicts. Governing quality test (contract paraphrase/E-C criterion): the author could dispute a Step-6 output only by saying *"that is not what I asserted."*

---

## 39.2 Frozen input/output contract

**Input contract.** Applied only to Step-5 `GAP` outcomes; Step 6 never repairs or overrides Step 5; clearly non-GAP input → **DP-REVIEW-R1**, never a manufactured pair. Available input: the GAP proposition unit; complete source-grounded asserted wording; primary assertion span(s); licensed context-support spans where explicitness = `context_supported`; Step-5 rationale/rule IDs; section/discourse context only as already licensed by Step 5. Prohibited: external literature; citations as scientific evidence; downstream RQ/design/contribution information; inferred scope structures; registry knowledge about theories/methods; scientific world knowledge used to strengthen the assertion.

**Output contract.** Per classified GAP instance: exactly one relation and exactly one knowledge_kind, plus grounding rationale (rule IDs + traces, §39.17). Never emitted: disjunctions, ranked alternatives, competing final values, blended pairs. One deficiency proposition → one pair. Two independently asserted deficiencies in one unit → **DP-CROSS-3 (MULTIPLE_INDEPENDENT_DEFICIENCIES)**: no "primary," separation required, each resulting proposition receives its own pair (§39.13).

**Core axis separation (frozen).** `relation` = **HOW** prior knowledge is deficient; `knowledge_kind` = **WHAT KIND** of knowledge is deficient. Orthogonal, each independently source-grounded — which permits one predicate to ground both axes when it independently satisfies both axes' conditions (§39.8 DP-PAIR-2a): "untested" grounds relation UNTESTED (verification denied) *and* kind evidence (the missing knowledge state is empirical testing); alignment wording grounds DISCONNECTED *and* practice_alignment. What independence forbids is **enum-to-enum inference** — reading a kind off a relation value (or vice versa) rather than off the wording.

---

## 39.3 Closed relation definitions (semantic cards)

### DP-REL-1 — ABSENT
**Definition.** Categorical non-existence / non-occurrence of the relevant knowledge state is asserted: the study, evidence, account, answer, examination, or **supporting evidence** is asserted never to have existed or occurred.
**Necessary conditions.** A categorical-zero head: negated existentials over knowledge items ("no evidence exists", "there is no account", "**no empirical evidence supports X**", "X **lacks empirical support**" absent any separate testing denial); negated/never research-activity predicates ("no study has examined", "has never been studied"); categorical non-establishment ("remains unexplored/unanswered", "remains an open question", "is not known", "we do not understand why X persists").
**Exclusions.** Degree wording → LIMITED (DP-PREC-1); denial of the **verification act itself** over a named artifact → UNTESTED (DP-PREC-2/10); unlinked-**state** wording over the research↔practice relationship → DISCONNECTED (DP-PREC-7/15) — but categorical absence of the **bridge apparatus itself** ("no mechanism exists for translating…") stays ABSENT, with kind practice_alignment (DP-KIND-4a).
**Distinctions.** *unexplored* → ABSENT ‖ *underexplored* → LIMITED · *never examined* → ABSENT ‖ *rarely examined* → LIMITED · *no evidence* → ABSENT ‖ *little evidence* → LIMITED · *no support* → ABSENT ‖ *never tested* → UNTESTED (support ≠ testing, DP-PREC-10).
**Positive.** "No studies have examined X." → ABSENT+evidence · "There is no theoretical account of X." → ABSENT+theory · "Assumption X lacks empirical support." → ABSENT+evidence · "We still do not understand why X persists." → ABSENT+unspecified.
**Negative.** "Little is known about X." → LIMITED · "The model has never been tested." → UNTESTED.
**Grounding.** The categorical head span.

### DP-REL-2 — LIMITED
**Definition.** Relevant knowledge exists or may exist but is asserted scarce, incomplete, insufficient, weakly developed, partial, or poorly understood — including **limited evidential support** for a claim and **limited development of the research–practice connecting process** (translation/integration).
**Necessary conditions.** A degree/insufficiency head: "little", "few", "scarce", "scant", "limited", "insufficient", "sparse", "partial", "incomplete", "underexplored", "under-studied", "poorly/not well understood", "rarely examined", "inadequate", "underdeveloped", "thin", "weak support".
**Exclusions.** Categorical zero → ABSENT; capability/warrant restriction of an existing resource → CONSTRAINED (DP-PREC-3); **state-of-disrelation** predicates over the research↔practice relationship ("poorly aligned", "disconnected") → DISCONNECTED (DP-PREC-11). Never converted into a quantitative estimate.
**Positive (frozen anchors).** "Little is known about how X affects Y." → **LIMITED+evidence** (contract Case A) · "Collective adaptation remains poorly understood." → **LIMITED+unspecified** · "Empirical support for assumption X is limited." → LIMITED+evidence · "Translation of research findings into practice remains limited." → **LIMITED+practice_alignment** (insufficiency head over the connecting process; DP-PREC-11).
**Negative.** "No evidence exists on X." → ABSENT · "Research and practice remain poorly aligned." → DISCONNECTED.
**Grounding.** The degree head span.

### DP-REL-3 — CONFLICTING
**Definition.** Prior knowledge is asserted to contain disagreement, inconsistency, contradiction, mixed findings, or incompatible positions/results — **within prior knowledge**.
**Necessary conditions.** A plurality-of-prior-positions head: "mixed", "inconsistent", "contradictory", "conflicting", "do not agree", "disagree", "no consensus", "debate persists", "competing … remain unresolved", "evidence supporting X is mixed".
**Exclusions.** Authorial rejection → CHALLENGED (DP-PREC-4); **research-vs-practice prescription conflict is divergence of the relationship → DISCONNECTED** (DP-PREC-13); methodological diversity without asserted incompatibility is no deficiency.
**DP-REL-3a ("contested").** Prior parties contest → CONFLICTING; the authors contest → CHALLENGED; contester unrecoverable → R3.
**Positive.** "Prior findings on X are mixed." → CONFLICTING+evidence · "No consensus exists on X." → CONFLICTING+unspecified · "Competing theoretical explanations remain unresolved." → CONFLICTING+theory · "Evidence supporting assumption X is mixed." → CONFLICTING+evidence.
**Negative.** "The prevailing interpretation is mistaken." → CHALLENGED · "Research recommendations and managerial practice give conflicting prescriptions." → DISCONNECTED+practice_alignment (cross-pole; DP-PREC-13).
**Grounding.** The disagreement head span.

### DP-REL-4 — UNTESTED
**Definition.** An identifiable conceptual item that already exists (proposition, hypothesis, model, framework, measure, claim, assumption) is asserted to lack **the act of empirical testing / evaluation / validation / verification itself**.
**Necessary conditions.** (a) an identifiable existing artifact is the target; (b) the head denies the **verification act**: "remains untested", "has never been (empirically) tested/evaluated/validated/verified", "awaits empirical scrutiny/validation", "has yet to be tested".
**Exclusions (sharpened).** **Support-family wording never suffices**: "unsupported", "lacks (empirical) support", "no/weak/insufficient support" assert the non-existence or insufficiency of supporting **evidence**, not the absence of testing → ABSENT/LIMITED/CONFLICTING + evidence per the head (DP-PREC-10), unless the text separately denies testing itself. No artifact → ABSENT ("No model explains X." → ABSENT+theory). Asserted invalidity → CHALLENGED; asserted incapacity → CONSTRAINED.
**Kind consequence (frozen, DP-KIND-1a).** UNTESTED's definition itself fixes the missing knowledge state as empirical verification: **every valid UNTESTED proposition has knowledge_kind = evidence.** The adverb "empirically" is not required — "untested/unvalidated/unverified" are themselves verification-denial predicates whose wording grounds the evidence kind. This is dual grounding by one predicate (DP-PAIR-2a), not enum-to-enum inference. `UNTESTED × unspecified` and all other non-evidence UNTESTED cells are **PROHIBITED_BY_SEMANTICS** (§39.7).
**Positive (frozen anchor).** "The cascading-goals model remains empirically untested." → **UNTESTED+evidence** · "The model remains untested." → **UNTESTED+evidence** · "Measure X has not been validated." → UNTESTED+evidence · "This proposition has never been tested outside laboratory settings." → UNTESTED+evidence (wording preserved).
**Negative.** "Assumption X lacks empirical support." → ABSENT+evidence · "No validated method exists to measure X." → ABSENT+method.
**Grounding.** Verification-act-denial head + the artifact's in-text mention (existence condition); the same head wording grounds the evidence kind.

### DP-REL-5 — CONSTRAINED
**Definition.** Knowledge generation, explanatory capability, measurement, inference, theoretical reach — **or the research→practice translation bridge** — is asserted restricted by an existing limitation: an existing knowledge resource, knowledge-generating approach, or explicitly named barrier has an asserted capability/warrant restriction.
**Necessary conditions.** A capability/warrant/restriction head over an existing resource or bridge: "cannot explain/predict/account for/capture", "unable to", "not designed to/for", "limited by [reliance/design/data practice]", "relies on X, leaving Y unexamined" (one predication, §39.13), "provide only partial insight", "ill-equipped to", "**[named barriers] constrain [the translation of research into practice]**".
**Exclusions.** Bare insufficiency → LIMITED (DP-PREC-3); falsity → CHALLENGED (DP-PREC-5); contextual restriction preserved-only (DP-CROSS-5); a causal persistence reason never converts the primary relation (DP-PREC-9); state-of-disrelation heads → DISCONNECTED (DP-PREC-12).
**Positive (frozen anchors).** "Existing diffusion theories cannot explain cross-boundary adoption." → **CONSTRAINED+theory** · "Existing measures cannot capture temporal variation." → **CONSTRAINED+method** · "Institutional barriers constrain the translation of research findings into practice." → **CONSTRAINED+practice_alignment** (the predication targets the bridge itself; DP-PREC-12).
**Negative.** "Evidence remains scarce because longitudinal data are difficult to obtain." → LIMITED+evidence · "The theory is wrong about X." → CHALLENGED.
**Grounding.** The capability/restriction head + the named resource/bridge wording.

### DP-REL-6 — DISCONNECTED
**Definition (frozen-narrow, unchanged).** An asserted research↔practice **state of disrelation**: disconnection, divergence, non-translation, misalignment.
**Necessary conditions.** A disrelation-state head whose poles are research knowledge and practice: "disconnected from practice", "has not translated into practice", "poorly aligned", "poorly integrated into practice", "diverges from what the evidence recommends", "does not address the problems practitioners face" (BR-GAP-12), "has yet to inform practice", "have drifted apart".
**Exclusions.** The lexeme "disconnect" alone decides nothing; literature-internal non-integration → ABSENT(+theory); practitioner capability deficits never arrive (R1). **The presence of both "research" and "practice" never forces DISCONNECTED**: insufficiency heads over the connecting *process* → LIMITED+practice_alignment (DP-PREC-11); explicit constraining factors over the bridge → CONSTRAINED+practice_alignment (DP-PREC-12).
**Implication (one-way, frozen).** DISCONNECTED → practice_alignment (the disrelation wording itself grounds the kind; DP-PAIR-2a). **The converse does not hold: practice_alignment ⇏ DISCONNECTED.**
**Positive (frozen anchors).** "Evidence on X is disconnected from current managerial practice." · "Academic understanding of X has not translated into practice." · "Research and practice remain poorly aligned on X." → all **DISCONNECTED+practice_alignment** (degree modifies within the disrelation family; DP-PREC-8).
**Negative.** "Research-practice integration remains limited." → LIMITED+practice_alignment · "Prior work has not connected findings on X with theories of Y." → ABSENT+theory.
**Grounding.** The two-pole disrelation head.

### DP-REL-7 — CHALLENGED
**Definition.** An existing prior view, assumption, interpretation, proposition, or theoretical position is asserted wrong, mistaken, misguided, invalid, or failing. The registry records the assertion of wrongness only.
**Necessary conditions.** An authorially asserted invalidity head: "is mistaken/wrong/flawed/misguided/invalid", "fails", "does not hold", "breaks down", "rests on a flawed premise", "we challenge/contest…", "are artifacts of…", "is empirically wrong".
**Exclusions.** Reported disagreement → CONFLICTING; incapacity without falsity → CONSTRAINED; verification-act denial → UNTESTED.
**Positive (frozen anchor).** "Previous theories assume stable boundaries, but this assumption is mistaken." → **CHALLENGED+theory** · "The model is empirically wrong." → CHALLENGED+theory (the challenged item is the **model** — a theoretical resource; "empirically" is a grounds adverb on the invalidity predicate and does not re-identify the deficient item, DP-KIND-9a) · "Established survey approaches, we argue, systematically misstate X." → CHALLENGED+method.
**Negative.** "Prior findings are mixed." → CONFLICTING · "The model remains untested." → UNTESTED+evidence.
**Grounding.** The invalidity head + the challenged item's mention.

---

## 39.4 Closed knowledge_kind definitions (semantic cards)

### DP-KIND-1 — evidence
**Definition.** The deficient item is empirical: studies, findings, evidence, data, observations, documentation, **empirical testing/verification**, **evidential support for a claim**, or what research has empirically established.
**Necessary textual evidence.** Empirical-item/activity/support wording as (or modifying) the deficient item: "evidence", "studies", "findings", "data", "empirical(ly)", "examined/studied/investigated/documented/observed", "tested/validated/verified" (verification acts), "support(s)/supporting" (evidential support), and — contract-frozen — the *known/established/documented* family ("little is known" → evidence, Case A).
**DP-KIND-1a (UNTESTED consequence).** Every valid UNTESTED proposition takes evidence: the verification-denial wording is itself the kind commitment (§39.3 DP-REL-4; DP-PAIR-2a).
**Exclusions.** kind = evidence never means the object is "evidence"; bare generics do not force evidence (DP-KIND-8).
**Positive.** "No studies have examined X." · "Little is known about X." · "The model remains untested." · "No empirical evidence supports assumption X." — all evidence.
**Negative.** "poorly understood" → unspecified · "no theoretical account" → theory.
**Trace.** The empirical-item/activity/support/verification wording (may coincide with the relation head).

### DP-KIND-2 — theory
**Definition.** The deficient item is a theoretical/conceptual resource: theories, theoretical accounts, explanations, frameworks, conceptual models, assumptions, interpretations, theoretical integration/understanding.
**Necessary textual evidence.** Theoretical-resource wording as (or modifying) the deficient item.
**Exclusions.** Kind never follows the object's category: an existing model lacking testing → **evidence** (DP-KIND-1a); "explain" inside a capability head names the theoretical resource ("theories cannot explain") but "no studies have examined the explanation of X" → evidence (deficient activity; DP-KIND-6).
**Positive.** "No theoretical account explains X." → ABSENT+theory · "Existing theories cannot explain X." → CONSTRAINED+theory · "This theoretical assumption is mistaken." → CHALLENGED+theory · "The model is empirically wrong." → CHALLENGED+theory (grounds adverb, DP-KIND-9a) · "Theoretical understanding of X remains limited." → LIMITED+theory.
**Negative.** "The cascading-goals model remains empirically untested." → evidence.
**Trace.** The theoretical-resource wording.

### DP-KIND-3 — method
**Definition.** The deficient item is a methodological resource or knowledge-generating technique itself: methods, designs, measures, instruments, analytic procedures, operationalizations.
**Necessary textual evidence.** Methodological-resource wording as the deficient item — asserted absent, insufficient, incapable, in dispute, or challenged *as a resource*.
**Exclusions.** Method-as-cause is not method-kind (DP-PREC-9): "Evidence is scarce because methods are weak/expensive." → LIMITED+evidence. A research→practice **translation mechanism** is bridge apparatus, not a knowledge-generating technique → practice_alignment, never method (DP-KIND-4a). The absent/unvalidated split: "No validated method exists to measure X." → the resource itself absent → **ABSENT+method**; "Measure X has not been validated." → the existing measure's verification act missing → **UNTESTED+evidence** (DP-PREC-10; DP-KIND-1a).
**Positive.** "Existing measures cannot capture temporal variation." → CONSTRAINED+method · "No validated method exists for X." → ABSENT+method · "Analytical approaches for multi-level X remain underdeveloped." → LIMITED+method · "Established survey approaches systematically misstate X." → CHALLENGED+method.
**Negative.** "Measure X has not been validated." → evidence · "scarce because methods are weak" → evidence.
**Trace.** The methodological-resource wording as deficient item (not as cause).

### DP-KIND-4 — practice_alignment
**Definition.** The deficient item is the relationship between research knowledge and practice: translation, alignment, integration, connection, the applicability bridge, research–practice divergence.
**Necessary textual evidence.** Wording naming the research↔practice relationship or its connecting process (translation/integration/uptake of research into practice) as the deficient item.
**Relation openness (corrected).** practice_alignment pairs with **any relation whose head semantics the wording independently satisfies**: DISCONNECTED (state of disrelation — canonical), LIMITED (insufficiency of the connecting process), CONSTRAINED (an explicit factor restricting the bridge), ABSENT (categorical absence of the bridge apparatus itself — "no mechanism/pathway exists for translating…"). It never *implies* DISCONNECTED. Remaining prohibited pairings (CONFLICTING, UNTESTED, CHALLENGED × practice_alignment) are justified cell-by-cell in §39.7.
**DP-KIND-4a (bridge-apparatus rule).** Mechanisms, pathways, channels, and infrastructures **for translating/moving research into practice** are bridge apparatus → practice_alignment kind; methods, measures, designs, and procedures **for generating research knowledge** are research resources → method kind. "Resource" wording alone never decides between them — what the resource is *for* does.
**Exclusions.** Practitioner ignorance never arrives (R1); a challenged claim *about* alignment challenges a view/finding → theory/evidence, not the relationship itself.
**Positive.** "Research and practice remain poorly aligned on X." → DISCONNECTED+pa · "Translation of research findings into practice remains limited." → LIMITED+pa · "Institutional barriers constrain the translation of research findings into practice." → CONSTRAINED+pa.
**Negative.** "Managers do not understand X." → R1 · "Findings on X have not been connected with theories of Y." → theory.
**Trace.** The relationship/connecting-process wording.

### DP-KIND-5 — unspecified
**Definition.** The manuscript is semantically noncommittal about kind: a GAP is clearly asserted, but the wording commits to none of the four specific kinds.
**Necessary textual evidence.** A deficiency head over kind-neutral wording: "understood/understanding" without a kind modifier (frozen: "poorly understood" → unspecified), bare "knowledge", bare "research/literature/attention/work", "no consensus on X" with no kind-marked positions.
**What unspecified is NOT.** Extractor uncertainty; low confidence; bad writing; missing object extraction; unresolved relation; system failure; a refuge for unresolved explicit-kind ambiguity (→ R2). If wording commits to a kind, unspecified is prohibited (DP-KIND-7). **No UNTESTED proposition can be unspecified** (DP-KIND-1a).
**Positive.** "Collective adaptation remains poorly understood." → LIMITED+unspecified · "Research on X remains limited." → LIMITED+unspecified.
**Negative.** "The model remains untested." → evidence · "Empirical evidence on X remains limited." → evidence.
**Trace (corrected, DP-TRACE-4 — no invented field).** `kind_trace_refs` reference the span of the **complete kind-neutral deficiency predication**; `rationale_codes` cite DP-KIND-5 and/or DP-KIND-8. The absence of a more specific commitment is represented by `knowledge_kind: unspecified` + that span + the rationale rule — nothing else. Example: "Collective adaptation remains poorly understood." → `relation_trace_refs`: span of "remains poorly understood"; `kind_trace_refs`: span of the full predication "Collective adaptation remains poorly understood"; rationale: DP-KIND-5/DP-KIND-8. **No `kind_commitment` field exists; the frozen Schema and Annotation Protocol are not modified.**

---

## 39.5 Relation decision rules

- **DP-REL-8 (head reading).** The relation is read from the semantic head of the asserted deficiency predication — never from subordinate reasons, contrasts, preserved context, or nearby nouns.
- **DP-REL-9 (family assignment).** Heads assign by meaning, not lexeme: categorical-zero → ABSENT; degree/insufficiency → LIMITED; within-knowledge plural incompatibility → CONFLICTING; artifact + verification-act denial → UNTESTED; capability/restriction of a resource or bridge → CONSTRAINED; research↔practice disrelation state → DISCONNECTED; authorial invalidity → CHALLENGED. Exemplars are semantic anchors, not a lexicon (§39.20-note).
- **DP-REL-10 (no scalar collapse).** Only ABSENT/LIMITED share a strength axis (§39.9); no other pair is resolved by "weaker/stronger."
- **DP-REL-11 (unlisted heads).** No family fits after all rules → R5; no nearest-value forcing.

## 39.6 Knowledge-kind decision rules

- **DP-KIND-6 (deficient-item test).** Kind = what the head predicates deficiency **of** — not nearby nouns, not the topic, not the object's category. "Little is known about the measurement of X." → evidence (what-is-known is deficient; the topic being measurement is irrelevant). "No mechanism exists for translating research findings into practice." → the deficient item is the **research→practice bridge apparatus** → **ABSENT+practice_alignment** (A-cell): a translation mechanism is not a knowledge-generating technique, so "resource" wording alone never yields method (DP-KIND-4a); contrast "No validated method exists for measuring X." → ABSENT+method (a research-generating resource) and "Research and practice are not linked on X." → DISCONNECTED+practice_alignment (unlinked **state**, not an absent bridge entity; DP-PREC-15).
- **DP-KIND-7 (commitment rule).** Explicit kind wording → that kind; none → unspecified; two explicit kinds unresolved in one predication → R2 (never unspecified, never a pick).
- **DP-KIND-8 (generic-word rule + frozen boundary).** Bare *research, literature, knowledge, understanding, attention, work* do not force evidence → unspecified absent a modifier. Contract-fixed poles: *known/established/documented* family → evidence (Case A); *understood/understanding* family → unspecified (Case I family) unless modified ("empirical understanding" → evidence; "theoretical understanding" → theory).
- **DP-KIND-9 (modifier precedence).** An explicit kind modifier beats the head's default ("no **theoretical** account exists" → theory).
- **DP-KIND-9a (grounds-adverb rule).** A kind modifier commits the kind only when it attaches to the **deficient-item nominal** ("empirical understanding", "theoretical account"). A manner/grounds adverb attached to the **deficiency predicate** states the grounds or mode of the deficiency and never re-identifies the deficient item: "The model is **empirically** wrong." → the challenged item is the model → CHALLENGED+theory; "The findings are **theoretically** implausible." → the challenged item is the findings → CHALLENGED+evidence. The what-is-challenged/deficient test (DP-KIND-6) decides; the adverb decides nothing.
- **DP-KIND-10 (resolved constructions).** "the literature is limited" → LIMITED+unspecified · "understanding remains poor" → LIMITED+unspecified · "research is scarce" → LIMITED+unspecified · "theoretical understanding is limited" → LIMITED+theory · "empirical understanding is limited" → LIMITED+evidence · "current methods provide only coarse estimates" → CONSTRAINED+method · "existing research has not translated into practice" → DISCONNECTED+practice_alignment · "research-practice integration remains underdeveloped" → LIMITED+practice_alignment.

## 39.7 Relation × kind compatibility matrix (35 cells; C = CANONICAL, A = ALLOWED_IF_EXPLICIT, P = PROHIBITED_BY_SEMANTICS)

**Role discipline (hard rule, DP-PAIR-3a).** The matrix is a **validator, never a classifier**: it never overrides an independently derived axis reading. If a correct reading lands on P, either an axis was mis-read (re-derive) or the cell is wrongly valued (registry-defect channel, R5 → §39.25); the relation is never forced to fit the matrix.

| relation \ kind | evidence | theory | method | practice_alignment | unspecified |
|---|---|---|---|---|---|
| ABSENT | **C** | **C** ("no theoretical account explains X") | **A** — explicit absence of a research-generating methodological resource ("no validated method exists for X") | **A** — explicit categorical absence of the **bridge apparatus itself** ("no mechanism exists for translating research findings into practice") → ABSENT+practice_alignment (DP-KIND-4a); unlinked-**state** wording ("research and practice are not linked/connected") stays DISCONNECTED (DP-PREC-15) | **C** ("we do not understand why X persists") |
| LIMITED | **C** (frozen "little is known") | **C** ("theoretical understanding … limited") | **A** — explicit insufficiency of methodological resources ("analytical approaches … underdeveloped") | **A** — explicit insufficiency/degree of the research→practice connecting process ("translation … remains limited"; "integration remains underdeveloped"); disrelation-state heads stay DISCONNECTED (DP-PREC-11) | **C** (frozen "poorly understood") |
| CONFLICTING | **C** ("findings are mixed"; "evidence supporting X is mixed") | **A** ("competing theoretical explanations remain unresolved") | **A** ("scholars disagree over the appropriate design for X") | **P** — CONFLICTING's frozen meaning is incompatibility *within prior knowledge*; research-vs-practice prescription conflict asserts the relationship diverges → DISCONNECTED (DP-PREC-13) | **A** ("no consensus on X") |
| UNTESTED | **C** — the only legal UNTESTED cell (DP-KIND-1a) | **P** — the frozen meaning fixes the missing item as *empirical* verification; "theoretically unexamined" is an ABSENT/LIMITED-theory assertion, not UNTESTED | **P** — an unvalidated measure lacks the verification act → evidence; a missing method → ABSENT+method | **P** — verification-denial over the relationship is not a licensed reading; disrelation wording → DISCONNECTED | **P** — "untested/unvalidated/unverified" is itself the evidence-kind commitment; a kind-silent verification denial cannot occur |
| CONSTRAINED | **A** ("existing evidence cannot support causal inference") | **C** (frozen "theories cannot explain") | **C** (frozen "measures cannot capture") | **A** — an explicit factor restricting the research→practice bridge itself ("institutional barriers constrain the translation of research findings into practice"); barrier wording as mere causal reason never overwrites another head (DP-PREC-9/12) | **A** ("existing knowledge cannot account for X") |
| DISCONNECTED | **P** | **P** | **P** | **C** (frozen anchors; the disrelation wording itself grounds the kind — one-way implication) | **P** — wording satisfying DISCONNECTED's conditions thereby commits practice_alignment; non-practice "disconnection" wording fails the relation's conditions and maps elsewhere (e.g., ABSENT+theory) |
| CHALLENGED | **A** ("reported effects are artifacts of measurement error" — the challenged item is findings; a challenged *model*, even "empirically wrong", is theory per DP-KIND-9a) | **C** (frozen "assumption … mistaken") | **A** ("survey approaches systematically misstate X") | **P** — a challenged *claim about* alignment is a challenged view/finding → theory/evidence; the relationship itself cannot be "wrong" | **A** ("the received view is mistaken", kind-silent; rare) |

**Counts: 12 C · 13 A · 10 P.** Every A-cell above is instantiated by genuine text in its cell; an A-cell pair is legal **only** when that explicit licensing wording is present and traced. The matrix is neither artificially permissive (10 justified prohibitions) nor artificially one-to-one (the practice_alignment column now spans four relations; only the DISCONNECTED **row** remains single-kind, by frozen one-way implication).

## 39.8 Pair-construction rules

- **DP-PAIR-1.** Exactly one pair per deficiency proposition; construction per §39.19; matrix-validated before output.
- **DP-PAIR-2 (independence / anti-shortcut).** No axis is inferred from the other's **enum value**: ABSENT ⇏ evidence ("no theoretical account" → theory); CONSTRAINED ⇏ method ("theories cannot explain" → theory); theory ⇏ CONSTRAINED; evidence ⇏ LIMITED; **practice_alignment ⇏ DISCONNECTED** ("integration remains limited" → LIMITED+pa).
- **DP-PAIR-2a (dual grounding ≠ enum inference — anti-confusion rule).** One asserted predicate may **independently ground both axes** when its semantics satisfy both axes' conditions: "untested" → relation UNTESTED (the verification act is denied) and kind evidence (the missing knowledge state is empirical testing); "disconnected [from practice]" → relation DISCONNECTED and kind practice_alignment. These are two semantic readings of the same wording, each traced to it (§39.17) — not a step from one enum to the other. What remains forbidden is deriving a value from the *other axis's label* rather than from wording.
- **DP-PAIR-3.** A P-cell after correct axis reading → re-derive one axis; doubly-correct P → R5 registry-defect channel. **DP-PAIR-3a** (validator-not-classifier) as stated in §39.7.

## 39.9 Weakest-supported-reading rule (contract-frozen; DP-PREC-1)

When the text supports LIMITED but does not safely support categorical ABSENT, record **LIMITED**. Scope: the ABSENT/LIMITED strength axis only — never a generic weakest-relation hierarchy: CHALLENGED is never downgraded to CONFLICTING, CONSTRAINED never to LIMITED, UNTESTED never to LIMITED. Hedge ladder: "no attention" → ABSENT · "virtually no attention" → LIMITED · "minimal attention" → LIMITED · "nothing is known" → ABSENT · "almost nothing is known" → LIMITED. Counter-examples for scope: "The theory arguably fails." → CHALLENGED (hedge preserved) · "Measures struggle to capture X." → CONSTRAINED if the capability head is asserted; genuinely unmappable → R5, not LIMITED.

## 39.10 Relation precedence / conflicts

- **DP-PREC-1 — ABSENT vs LIMITED.** Unhedged categorical zero → ABSENT; degree/hedged → LIMITED; underdetermined → LIMITED (§39.9).
- **DP-PREC-2 — ABSENT vs UNTESTED (artifact + act test).** Identifiable existing artifact **and** denial of the verification act → UNTESTED; no artifact, or the denial concerns existence of knowledge/evidence rather than the act → ABSENT. "No model explains X." → ABSENT+theory.
- **DP-PREC-10 — support vs testing (hard rule).** *Absence of SUPPORT ≠ absence of TESTING.* "unsupported / lacks support / no support / weak support / insufficient support" → ABSENT/LIMITED + evidence per the head (mixed support → CONFLICTING+evidence); UNTESTED only where the text denies the testing/evaluation/validation/verification **act** itself. Both asserted independently → §39.13 separation.
- **DP-PREC-3 — LIMITED vs CONSTRAINED.** Amount/development insufficiency → LIMITED; explicit capability/warrant restriction of an existing resource → CONSTRAINED.
- **DP-PREC-4 — CONFLICTING vs CHALLENGED.** Prior positions disagree → CONFLICTING; the manuscript asserts a prior view wrong → CHALLENGED; "contested" per DP-REL-3a.
- **DP-PREC-5 — CONSTRAINED vs CHALLENGED.** Incapacity → CONSTRAINED; falsity → CHALLENGED; fused single head with falsity asserted → CHALLENGED; independent predications → §39.13.
- **DP-PREC-6 — CONFLICTING vs CONSTRAINED.** Incompatibility among positions vs restricted capability of a resource.
- **DP-PREC-7 — DISCONNECTED vs ABSENT.** Two-pole research↔practice disrelation → DISCONNECTED; literature-internal non-connection → ABSENT.
- **DP-PREC-8 — family beats modifier.** Degree words inside non-scalar families never re-route: "poorly aligned" → DISCONNECTED; "largely untested" → UNTESTED; "somewhat inconsistent" → CONFLICTING.
- **DP-PREC-9 — head vs causal/persistence reason.** The head controls; reasons never overwrite (§39.12).
- **DP-PREC-11 — DISCONNECTED vs LIMITED (practice_alignment).** Disrelation-**state** predicates over the relationship (aligned/misaligned, connected/disconnected, integrated [as state: "poorly integrated"], translated [negated], diverges, drifted apart) → DISCONNECTED. Degree/development predicates over the connecting-**process** nominals (translation, integration, uptake … "remains limited/underdeveloped/partial") → LIMITED. The head's family controls; the mere co-presence of "research" and "practice" forces nothing.
- **DP-PREC-12 — DISCONNECTED vs CONSTRAINED (practice_alignment).** An explicit constraining factor asserted as the head **over the bridge itself** ("[barriers] constrain the translation…") → CONSTRAINED+pa. A disrelation-state head → DISCONNECTED. Barrier wording appearing only as a causal reason for another head never overwrites that head (DP-PREC-9): "Research has not translated into practice because of institutional barriers." → DISCONNECTED+pa, reason preserved.
- **DP-PREC-13 — DISCONNECTED vs CONFLICTING.** Disagreement **within prior research knowledge** → CONFLICTING. Research-vs-practice conflict of prescriptions/recommendations is divergence of the relationship → DISCONNECTED+pa ("Research recommendations and established managerial practice give conflicting prescriptions." → DISCONNECTED+pa). CONFLICTING×pa is therefore prohibited (§39.7).
- **DP-PREC-15 — ABSENT (practice_alignment) vs DISCONNECTED.** An existential predication asserting the categorical absence of a **bridge entity** (mechanism, pathway, channel, infrastructure for translating research into practice) → ABSENT+practice_alignment. A **state predication over the relationship itself** (not linked/connected/aligned/translated, diverges), even when existentially phrased about the relation ("no connection exists between research and practice"), → DISCONNECTED+practice_alignment. Entity-absence vs relation-state decides; a bridge can be absent while ad-hoc translation occurs, and poles can be unlinked despite mechanisms existing.
- **DP-PREC-14 (hard two-way principle).** Relation-family wording must not erase an explicitly asserted practice_alignment kind; equally, practice_alignment wording must not force DISCONNECTED. Each axis reads its own semantics.

## 39.11 Knowledge-kind precedence / under-commitment

DP-KIND-6/7/8/9 govern. Hard under-commitment rule: no kind is inferred from section location, the study's own method, the affected object's type, nearby citations, disciplinary convention, likely reviewer interpretation, or external knowledge. Minimal anchors: "X remains poorly understood." → unspecified · "Empirical evidence on X remains limited." → evidence · "Theoretical understanding of X remains limited." → theory · "Available measures of X remain inadequate." → method · "Research on X has not translated into practice." → practice_alignment (with relation DISCONNECTED from the disrelation head).

## 39.12 Predicate-head / causal-reason distinction (DP-PREC-9 in full)

- "Evidence on supplier adaptation remains scarce **because longitudinal data are difficult to obtain**." → **LIMITED+evidence**; never CONSTRAINED+method.
- "Prior findings are mixed **because studies use different methods**." → **CONFLICTING+evidence**; no remap.
- "Research has not translated into practice **because of institutional barriers**." → **DISCONNECTED+practice_alignment**; the barrier reason is preserved, not promoted (contrast the barrier-as-head case, DP-PREC-12).
- A reason clause that **independently asserts a second deficiency** requires a separate proposition instance (§39.13); the primary pair is unchanged; spawn mechanics remain downstream property.

## 39.13 Multiple-deficiency handling (DP-CROSS-3)

One deficiency + causal explanation → one pair. One deficiency + contrast → the deficiency unit alone. One predication with internal consequence ("relies on cross-sectional data, leaving dynamics unexamined") → **one** CONSTRAINED predication. Coordinated same-family heads over one item ("scarce and fragmented") → one pair. **Two independently asserted deficiency predicates** ("Evidence on X is scarce, and prior findings on Y conflict"; "the theory is untested and, we argue, mistaken about Z"; a theory-challenge plus a distinct evidence deficiency) → **MULTIPLE_INDEPENDENT_DEFICIENCIES** (R4): no primary, no blend; separation upstream/downstream; each resulting proposition receives its own pair. Segmentation/spawning mechanics are not defined here.

## 39.14 Context-supported handling (DP-CROSS-4)

Licensed completion only (anaphora, ellipsis, omitted argument, referential dependency, genuine linguistic dependency). Completion completes the proposition ("These mechanisms remain unexplored." + licensed antecedent → ABSENT+evidence); it never invents the predicate or a kind commitment. Broad paragraph inference prohibited. Completion failure cannot arrive here (BR T2b holds such units at UNCERTAIN); if one does → R1.

## 39.15 Scope/context non-ownership (DP-CROSS-5)

Population, geography, setting, level, temporal scope, and all contextual restrictions are preserved proposition content, never classified, never pair-altering: "No evidence exists about X among frontline workers." → ABSENT+evidence · "These mechanisms remain unexplored in distributed settings." → ABSENT+evidence · "Prior findings conflict in emerging markets." → CONFLICTING+evidence. No scope structure of any form.

## 39.16 Object-vs-kind separation (DP-CROSS-1)

Step 6 inspects the deficiency's target only to determine kind and (for UNTESTED) artifact existence; it outputs no `object_kind`, `artifact_kind`, object mention, participants, `about`, or scope. "The cascading-goals model remains empirically untested." → UNTESTED+evidence; the model's extraction is Step 8's. "Existing diffusion theories cannot explain cross-boundary adoption." → CONSTRAINED+theory; object Step 8's. No Step-8 rule appears here.

## 39.17 Traceability requirements (DP-TRACE-*)

Production Schema v1.2 stores `deficiency.source_trace_refs` (shared pair trace); the Annotation Protocol captures `relation_trace_refs` and `kind_trace_refs` separately in gold. Neither is altered; the gold field-specific traces are never collapsed.
- **DP-TRACE-1 (relation evidence).** The deficiency head span (+ the artifact mention for UNTESTED).
- **DP-TRACE-2 (kind evidence).** The kind-committing wording span. "**Empirical evidence** on X **remains scarce**." — relation trace "remains scarce"; kind trace "Empirical evidence".
- **DP-TRACE-3 (shared/overlapping spans — explicit).** One span may support both axes because the trace roles are conceptually distinct even when spans overlap or are identical: "The model **remains untested**." — relation trace "remains untested"; kind trace "untested" (or the containing predication span per the frozen span mechanics). Legal per DP-PAIR-2a.
- **DP-TRACE-4 (unspecified — corrected).** `kind_trace_refs` = the span of the complete kind-neutral deficiency predication; `rationale_codes` cite DP-KIND-5/DP-KIND-8. **No additional field exists**; `kind_commitment` and any equivalent are not part of any schema and are not stored.
- **DP-TRACE-5 (completion spans).** Licensed completing spans join the trace set; relation and kind may cite different spans where each is separately licensed.

## 39.18 Review / unresolved-classification rules (DP-REVIEW-*)

No `UNCERTAIN` relation or kind exists; `unspecified` is kind-only and manuscript-side; **unspecified never absorbs unresolved explicit-kind ambiguity, and no UNTESTED case can reach unspecified** (DP-KIND-1a). Review conditions (logical, Step-6-owned; runtime transitions and verification codes remain State-Machine/Step-13 property):
- **R1 — upstream_boundary_inconsistency.** Clearly non-GAP input (e.g., "Managers do not understand X."; "Managers struggle to understand X."). No pair.
- **R2 — kind_grounding_unresolved.** Two explicit kinds licensed; the predication's commitment unresolvable.
- **R3 — relation_nonscalar_unresolved.** Non-scalar relation ambiguity survives precedence (unrecoverable contester; incapacity-vs-invalidity residue).
- **R4 — multiple_independent_deficiencies.** §39.13 separation required.
- **R5 — head_unmappable / registry defect.** No family fits, or a doubly-correct reading lands on P (§39.8 DP-PAIR-3).

## 39.19 Deterministic decision procedure

```text
P0  INPUT: Step-5 outcome = GAP under A1E-BR-1.2?  NO → R1.
P1  HEAD: identify the asserted deficiency predication head (DP-REL-8);
      none locatable → R1.
P2  SEPARATION: two+ independent deficiency predicates → R4 (no primary, no blend);
      consequence-pattern / same-family coordination / causal reason → one predication.
P3 RELATION: family by head semantics (DP-REL-9); precedence DP-PREC-2..13 and DP-PREC-15;
      support≠testing (DP-PREC-10); ABSENT/LIMITED underdetermination → LIMITED (39.9);
      unmappable → R5; non-scalar residue → R3.
P4  KIND: deficient-item test (DP-KIND-6); explicit commitment → that kind
      (DP-KIND-9); generic-word rule + frozen known/understood boundary (DP-KIND-8);
      UNTESTED → evidence by DP-KIND-1a (wording-grounded, DP-PAIR-2a);
      no commitment → unspecified (DP-KIND-7); two-explicit unresolved → R2.
P5  MATRIX (validator only, DP-PAIR-3a): C → proceed; A → confirm the cell's licensing
      wording is in the trace set, else re-derive; P → re-derive one axis;
      doubly-correct P → R5. The matrix never forces a value.
P6  TRACES: relation and kind each grounded (39.17); shared/overlapping spans legal
      (DP-TRACE-3); unspecified per DP-TRACE-4 (existing fields only).
P7  OUTPUT: exactly one (relation, knowledge_kind) + rule IDs + traces;
      or exactly one review condition R1–R5.
```

## 39.20 Machine-referenceable rule registry

| rule_id | rule_statement (operative core) | positive_conditions | exclusions | ex (+) | ex (−) | nearest_confusions | related |
|---|---|---|---|---|---|---|---|
| DP-REL-1 | ABSENT ⟺ categorical non-existence head, incl. support-nonexistence | §39.3 card | degree; verification-act denial; disrelation | "No studies have examined X."; "lacks empirical support" | "Little is known…"; "remains untested" | LIMITED, UNTESTED | DP-PREC-1/2/10 |
| DP-REL-2 | LIMITED ⟺ insufficiency/degree head, incl. limited support and limited connecting process | card | zero; capability; disrelation state | "support … is limited"; "translation … remains limited" | "no support"; "poorly aligned" | ABSENT, CONSTRAINED, DISCONNECTED | DP-PREC-1/3/11 |
| DP-REL-3 | CONFLICTING ⟺ within-knowledge plural incompatibility | card | authorial rejection; cross-pole divergence | "findings are mixed" | "prescriptions conflict [research vs practice]" → DISCONNECTED | CHALLENGED, DISCONNECTED | DP-PREC-4/13 |
| DP-REL-3a | "contested": prior parties → CONFLICTING; authors → CHALLENGED; unrecoverable → R3 | — | guessing | — | — | — | R3 |
| DP-REL-4 | UNTESTED ⟺ existing artifact + denial of the verification act; kind = evidence always | card | support-family wording; no artifact; invalidity; incapacity | "remains untested"; "has not been validated" | "lacks empirical support" → ABSENT | ABSENT, CHALLENGED | DP-PREC-2/10; DP-KIND-1a |
| DP-REL-5 | CONSTRAINED ⟺ capability/restriction head over resource or bridge | card | bare scarcity; falsity; reason-only barriers | "cannot explain"; "barriers constrain the translation…" | "scarce because…" | LIMITED, CHALLENGED, DISCONNECTED | DP-PREC-3/5/9/12 |
| DP-REL-6 | DISCONNECTED ⟺ research↔practice disrelation state (frozen-narrow); one-way ⇒ practice_alignment | two-pole disrelation head | co-presence of "research"+"practice"; process-insufficiency; bridge-constraint | "poorly aligned"; "not translated" | "integration remains limited" → LIMITED+pa | LIMITED, CONSTRAINED, CONFLICTING | DP-PREC-7/8/11/12/13 |
| DP-REL-7 | CHALLENGED ⟺ authorially asserted invalidity | card | disagreement; incapacity; verification denial | "assumption … mistaken"; "empirically wrong" | "findings are mixed"; "remains untested" | CONFLICTING, CONSTRAINED, UNTESTED | DP-PREC-4/5 |
| DP-REL-8..11 | head reading; family-by-meaning; no scalar collapse; unmappable → R5 | — | — | — | — | — | — |
| DP-KIND-1 | evidence ⟺ empirical item/activity/support/verification wording; "known" family contract-anchored | card | object-category inference; bare generics | "no studies"; "lacks support"; "little is known" | "poorly understood" | unspecified, theory | DP-KIND-8; DP-KIND-1a |
| DP-KIND-1a | Every valid UNTESTED proposition → evidence; the verification-denial wording is the kind commitment | — | UNTESTED×any-other-kind | "The model remains untested." → evidence | — | — | DP-PAIR-2a; §39.7 |
| DP-KIND-2 | theory ⟺ theoretical/conceptual resource wording | card | object=model shortcut | "no theoretical account" | untested model → evidence | evidence, method | DP-CROSS-1 |
| DP-KIND-3 | method ⟺ methodological resource as deficient item; absent-resource vs unvalidated-artifact split | card | method-as-cause | "no validated method exists" → ABSENT+method | "measure … not validated" → UNTESTED+evidence | evidence | DP-PREC-9/10 |
| DP-KIND-4 | practice_alignment ⟺ research↔practice relationship / connecting process / bridge apparatus as deficient item; relation-open (DISC/LIM/CONSTR/ABSENT) | card | practitioner ignorance; challenged claims about alignment | four pa anchors (§39.4) | "Managers do not understand X." | — | DP-PREC-11/12/14/15 |
| DP-KIND-4a | Bridge apparatus (translation mechanisms/pathways) → practice_alignment; research-generating resources → method; purpose decides, not "resource" wording | — | resource-wording shortcut | "no mechanism … for translating" → ABSENT+pa | "no validated method … for measuring" → ABSENT+method | method | DP-KIND-6; DP-PREC-15 |
| DP-KIND-9a | Item-attached modifiers commit kind; predicate-attached grounds adverbs never re-identify the deficient item | — | adverb-driven kind | "empirically wrong" model → theory | "empirical understanding limited" → evidence (item-attached) | — | DP-KIND-6/9 |
| DP-KIND-5 | unspecified ⟺ manuscript kind-silence; never system uncertainty; never UNTESTED | card | explicit commitment; R2 refuge | "poorly understood" | "remains untested" | all | DP-KIND-7; DP-TRACE-4 |
| DP-KIND-6..10 | deficient-item test; commitment; generic-word + frozen boundary; modifier precedence; resolved constructions | §39.6 | — | — | — | — | — |
| DP-PAIR-1 | One matrix-validated pair per proposition | — | disjunctions, blends | — | — | — | §39.7 |
| DP-PAIR-2 | No enum-to-enum inference; incl. pa ⇏ DISCONNECTED | each axis own wording | axis shortcuts | "integration limited" → LIMITED+pa | — | — | DP-PREC-14 |
| DP-PAIR-2a | Dual grounding of both axes by one predicate is legal; distinct from enum inference | both conditions satisfied by the wording | label-derived values | "untested" → UNTESTED & evidence | — | — | DP-TRACE-3 |
| DP-PAIR-3 / 3a | P-cell → re-derive / R5; matrix = validator, never classifier | — | forcing to fit | — | — | — | §39.25 |
| DP-PREC-1..15 | Precedence set per §39.10 (incl. support≠testing; all practice-alignment distinctions; two-way non-erasure) | — | — | — | — | — | — |
| DP-CROSS-1 | Object never substitutes for kind; no object output | — | — | — | — | — | §39.16 |
| DP-CROSS-3 | MULTIPLE_INDEPENDENT_DEFICIENCIES → separation, own pairs | — | primary-picking, blending | — | — | — | R4 |
| DP-CROSS-4 | Licensed completion only | — | paragraph inference | — | — | — | §39.14 |
| DP-CROSS-5 | Context preserved, never classified, never pair-altering | — | scope structures | — | — | — | §39.15 |
| DP-TRACE-1..5 | Trace sufficiency; shared/overlapping spans legal; unspecified via existing fields only | — | invented fields; gold collapse | — | — | — | Schema/Protocol |
| DP-REVIEW-R1..R5 | Review conditions per §39.18 | — | new enums; runtime design | — | — | — | SM/Step-13 |

**§39.20-note (Step-7 boundary, hard statement).** Every exemplar here is a semantic exemplar for interpretation, not a detection signal: no regexes, triggers, weights, priors, strengths, seeds, or scanning features. Semantic exemplar ≠ detection signal; detection is Step-7 property.

---

## 39.21 Adjudication guidance

| Value | Clear positive | Clear negative | Nearest boundary | Review condition |
|---|---|---|---|---|
| ABSENT | "No studies have examined X."; "lacks empirical support" | "Little is known." | hedged zero ("virtually no") → LIMITED | R5 head unmappable |
| LIMITED | "Evidence remains scarce."; "translation … remains limited" | "cannot capture" | resource-internal restriction → CONSTRAINED | — |
| CONFLICTING | "Findings are mixed." | "assumption is mistaken" | "contested" (DP-REL-3a); cross-pole conflict → DISCONNECTED | R3 |
| UNTESTED | "remains untested"; "has not been validated" | "lacks empirical support" → ABSENT | verification act vs supporting evidence (DP-PREC-10) | — |
| CONSTRAINED | "theories cannot explain"; "barriers constrain the translation…" | "scarce because…" | bridge-constraint vs disrelation state (DP-PREC-12) | R3 |
| DISCONNECTED | "poorly aligned"; "not translated into practice" | "integration remains limited" → LIMITED+pa | state vs process-development head (DP-PREC-11) | R1 for capability inputs |
| CHALLENGED | "assumption … mistaken"; "empirically wrong" (kind from the challenged item: model → theory, DP-KIND-9a) | "remains untested" | fused incapacity+falsity → CHALLENGED | R3 |
| evidence | "no studies…"; "little is known"; "remains untested" | "poorly understood" | support-family always evidence-kind | — |
| theory | "no theoretical account" | untested model → evidence | explanatory resource vs examined activity | R2 |
| method | "measures cannot capture"; "no validated method exists" | "measure … not validated" → evidence | absent resource vs unvalidated artifact | R2 |
| practice_alignment | four-relation anchors (§39.4) | "managers do not understand" | relation per its own head (DP-PREC-11/12/13/15) | R1 |
| unspecified | "poorly understood" | "empirical evidence limited"; any UNTESTED case | bare generics → unspecified (DP-KIND-8) | never for R2 |

**Mandated drills (verbatim discipline):**
- **UNTESTED vs unsupported.** Ask: does the text deny the testing/evaluation/validation/verification **act**, or the existence/sufficiency of supporting **evidence**? Act → UNTESTED; support → ABSENT/LIMITED/CONFLICTING + evidence per the head. "Unsupported" never yields UNTESTED by itself.
- **UNTESTED vs ABSENT.** Artifact + act test (DP-PREC-2): an existing named artifact whose testing is denied → UNTESTED; absence of research/knowledge/evidence on a phenomenon → ABSENT.
- **UNTESTED is always evidence-kind.** DP-KIND-1a; recording any other kind on UNTESTED is an error, not a judgment call; "empirically" need not appear.
- **LIMITED×pa vs DISCONNECTED.** Head family: development/amount over the connecting process ("translation/integration remains limited/underdeveloped") → LIMITED+pa; disrelation state ("disconnected", "poorly aligned", "not translated", "poorly integrated") → DISCONNECTED+pa.
- **CONSTRAINED×pa vs DISCONNECTED.** Constraining factor asserted as the head over the bridge → CONSTRAINED+pa; disrelation state → DISCONNECTED+pa; barrier wording as a mere reason never overwrites (DP-PREC-9/12) — quote the head in the rationale.
- **Absent bridge vs unlinked state vs absent research method.** "No mechanism exists for translating research findings into practice." → ABSENT+practice_alignment (bridge entity absent, DP-KIND-4a); "Research and practice are not linked on X." → DISCONNECTED+practice_alignment (relation-state, DP-PREC-15); "No validated method exists for measuring X." → ABSENT+method (research-generating resource). Ask what the absent thing is *for* and whether an entity or a state is predicated.
- **practice_alignment vs practitioner capability.** Who/what is deficient: the research↔practice relationship (pa) vs practitioners' own knowledge ("managers struggle/do not understand") → not GAP, R1.
- **unspecified tracing without a new field.** `kind_trace_refs` → the full kind-neutral predication span; rationale cites DP-KIND-5/DP-KIND-8; write nothing else — no `kind_commitment`, no invented annotation.
- **Matrix = validator, not classifier.** Never adjust an axis to satisfy a cell; a doubly-correct P-cell reading is a registry defect (R5), not an annotation instruction.

No confidence scores exist anywhere.

## 39.22 Step-3 error mapping

| Failure | Step-3 treatment |
|---|---|
| Wrong relation (span-matched instance) | `E-RELATION` (per-value confusion reporting) |
| Wrong knowledge_kind | `E-KNOWLEDGE-KIND` |
| Forced specific kind where gold = unspecified; or unspecified where kind committed | `E-KNOWLEDGE-KIND` + direction reporting |
| **"The model remains untested." predicted UNTESTED+unspecified, gold UNTESTED+evidence** | `E-KNOWLEDGE-KIND` (relation correct; kind wrong per DP-KIND-1a) |
| **"Research-practice integration remains limited." predicted DISCONNECTED+practice_alignment, gold LIMITED+practice_alignment** | `E-RELATION` (kind correct; relation wrong per DP-PREC-11) |
| Scope/context wrongly influencing the pair | routed to the existing primitive/object-scope analysis of the frozen Protocol taxonomy |
| Pair emitted for non-GAP material | upstream `E-BOUNDARY` (Class-A where applicable) / cascade per Protocol prerequisite accounting |
| Root vs cascade | Step-6 root errors counted on gold-upstream (oracle-input) evaluation; wrong-boundary/wrong-span inputs → cascades attributed upstream |
| Enum violation / missing trace | Schema structural violation (validator territory) |

No new taxonomy; **no schema field such as `kind_commitment` is required for evaluation** — gold `kind_trace_refs` + rationale codes suffice.

## 39.23 Normative semantic test suite

Format: `ID · "text" → RELATION + kind · [relation rule; kind rule] · rationale · review N/Y`. Positive minimums count only same-relation positives; negative controls (…C-suffixed) and review cases are additional and never counted.

**ABSENT — 12 positives.**
A1 · "No studies have examined X." → ABSENT+evidence · [DP-REL-1; DP-KIND-1] · negated activity · N
A2 · "There is no evidence on the long-term effects of X." → ABSENT+evidence · [DP-REL-1; DP-KIND-1] · negated existential · N
A3 · "These mechanisms remain unexplored in distributed settings." [licensed antecedent supplied] → ABSENT+evidence · [DP-REL-1; DP-KIND-1] · completion per DP-CROSS-4; restriction preserved · N
A4 · "X has never been studied." → ABSENT+evidence · [DP-REL-1; DP-KIND-1] · never-quantified activity · N
A5 · "We still do not understand why X persists." → ABSENT+unspecified · [DP-REL-1; DP-KIND-5/8] · categorical; kind-neutral · N
A6 · "There is no theoretical account of X." → ABSENT+theory · [DP-REL-1; DP-KIND-2] · theory-resource absence · N
A7 · "No model explains X." → ABSENT+theory · [DP-REL-1/DP-PREC-2; DP-KIND-2] · no artifact exists → not UNTESTED · N
A8 · "No validated method exists to measure X." → ABSENT+method · [DP-REL-1; DP-KIND-3] · A-cell: the resource itself absent · N
A9 · "X remains unanswered in this literature." → ABSENT+unspecified · [DP-REL-1; DP-KIND-5] · non-establishment · N
A10 · "Nothing is known about X." → ABSENT+evidence · [DP-REL-1/DP-PREC-1; DP-KIND-1/8] · unhedged zero; "known" → evidence · N
A11 · "Assumption X lacks empirical support." → ABSENT+evidence · [DP-REL-1/DP-PREC-10; DP-KIND-1] · support-nonexistence, not testing-denial · N
A12 · "No mechanism exists for translating research findings on X into practice." → ABSENT+practice_alignment · [DP-REL-1/DP-PREC-15; DP-KIND-4a] · A-cell: bridge apparatus categorically absent; not method, not DISCONNECTED · N

**LIMITED — 13 positives.**
B1 · "Little is known about how X affects Y." → LIMITED+evidence · [DP-REL-2; DP-KIND-1/8] · frozen anchor (contract Case A) · N
B2 · "Collective adaptation remains poorly understood." → LIMITED+unspecified · [DP-REL-2; DP-KIND-5/8] · frozen anchor · N
B3 · "Evidence on X remains scarce." → LIMITED+evidence · [DP-REL-2; DP-KIND-1] · · N
B4 · "X has rarely been examined." → LIMITED+evidence · [DP-REL-2/DP-PREC-1; DP-KIND-1] · degree, not zero · N
B5 · "Theoretical understanding of X remains limited." → LIMITED+theory · [DP-REL-2; DP-KIND-2/9] · modifier commits · N
B6 · "Analytical approaches for multi-level X remain underdeveloped." → LIMITED+method · [DP-REL-2; DP-KIND-3] · A-cell: resource insufficiency · N
B7 · "Research on X remains limited." → LIMITED+unspecified · [DP-REL-2; DP-KIND-8] · bare generic never forces evidence · N
B8 · "Available measures of X remain inadequate." → LIMITED+method · [DP-REL-2; DP-KIND-3] · insufficiency head; capability wording would be CONSTRAINED · N
B9 · "Evidence on X remains scarce because longitudinal data are difficult to obtain." → LIMITED+evidence · [DP-REL-2/DP-PREC-9; DP-KIND-1] · reason never overwrites; NOT CONSTRAINED+method · N
B10 · "Scholarly attention to X has been minimal." → LIMITED+unspecified · [DP-REL-2/§39.9; DP-KIND-8] · weakest-supported; generic · N
B11 · "Translation of research findings into practice remains limited." → LIMITED+practice_alignment · [DP-REL-2/DP-PREC-11; DP-KIND-4] · A-cell: insufficiency of the connecting process · N
B12 · "Research-practice integration remains underdeveloped." → LIMITED+practice_alignment · [DP-REL-2/DP-PREC-11; DP-KIND-4] · A-cell; not forced to DISCONNECTED · N
B13 · "The broader literature on X remains thin." → LIMITED+unspecified · [DP-REL-2; DP-KIND-8] · bare generic · N

**CONFLICTING — 9 positives.**
C1 · "Prior findings on X are mixed." → CONFLICTING+evidence · [DP-REL-3; DP-KIND-1] · frozen anchor · N
C2 · "There is no consensus on whether X improves Y." → CONFLICTING+unspecified · [DP-REL-3; DP-KIND-5] · A-cell kind-silent · N
C3 · "Competing theoretical explanations remain unresolved." → CONFLICTING+theory · [DP-REL-3; DP-KIND-2] · plural theoretical positions; A-cell · N
C4 · "Empirical results on X are contradictory." → CONFLICTING+evidence · [DP-REL-3; DP-KIND-1] · · N
C5 · "Scholars disagree over the appropriate design for studying X." → CONFLICTING+method · [DP-REL-3; DP-KIND-3] · A-cell methodological disagreement · N
C6 · "X remains contested among researchers." → CONFLICTING+unspecified · [DP-REL-3a; DP-KIND-5] · prior parties contest · N
C7 · "Prior findings are mixed because studies use different methods." → CONFLICTING+evidence · [DP-REL-3/DP-PREC-9; DP-KIND-1] · head-vs-reason · N
C8 · "The debate over X's mechanism persists." → CONFLICTING+theory · [DP-REL-3; DP-KIND-2] · · N
C9 · "Evidence supporting assumption X is mixed." → CONFLICTING+evidence · [DP-REL-3/DP-PREC-10; DP-KIND-1] · mixed-support family · N

**UNTESTED — 8 positives (all evidence by DP-KIND-1a).**
D1 · "The cascading-goals model remains empirically untested." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · frozen anchor · N
D2 · "This proposition has never been tested outside laboratory settings." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · restriction preserved · N
D3 · "The framework awaits empirical validation." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · · N
D4 · "Measure X has not been validated." → UNTESTED+evidence · [DP-REL-4/DP-PREC-10; DP-KIND-1a] · verification act denied; NOT method-kind · N
D5 · "The moderating role proposed by Smith has not been empirically verified." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · named proposition · N
D6 · "The model remains untested." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · corrected mandatory case; "empirically" not required · N
D7 · "The hypothesized moderation effect has yet to be tested." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · · N
D8 · "The scale has not been evaluated in field settings." → UNTESTED+evidence · [DP-REL-4; DP-KIND-1a] · evaluation act denied; context preserved · N
DC1 · [control] "The assumption of Y, though widely adopted, lacks empirical support." → ABSENT+evidence · [DP-PREC-10; DP-KIND-1] · support ≠ testing — the v1.0 mis-mapping corrected · N
DC2 · [control] "Whether the mechanism generalizes has not been examined." → ABSENT+evidence · [DP-PREC-2; DP-KIND-1] · no named artifact · N

**CONSTRAINED — 11 positives.**
E1 · "Existing diffusion theories cannot explain cross-boundary adoption." → CONSTRAINED+theory · [DP-REL-5; DP-KIND-2] · frozen anchor · N
E2 · "Existing measures cannot capture temporal variation." → CONSTRAINED+method · [DP-REL-5; DP-KIND-3] · frozen anchor · N
E3 · "Existing studies rely on cross-sectional data, leaving temporal dynamics unexamined." → CONSTRAINED+method · [DP-REL-5/§39.13; DP-KIND-3] · one predication with consequence · N
E4 · "Prior instruments were not designed to capture team-level variation." → CONSTRAINED+method · [DP-REL-5; DP-KIND-3] · · N
E5 · "Current methods provide only coarse estimates of X." → CONSTRAINED+method · [DP-REL-5; DP-KIND-3] · partial capability · N
E6 · "Institutional theory is unable to account for rapid collapse." → CONSTRAINED+theory · [DP-REL-5; DP-KIND-2] · · N
E7 · "Existing evidence cannot support causal inference about X." → CONSTRAINED+evidence · [DP-REL-5; DP-KIND-1] · A-cell · N
E8 · "Existing knowledge cannot account for the observed heterogeneity." → CONSTRAINED+unspecified · [DP-REL-5; DP-KIND-5/8] · A-cell · N
E9 · "Current designs cannot separate selection from treatment effects." → CONSTRAINED+method · [DP-REL-5; DP-KIND-3] · · N
E10 · "Existing frameworks are ill-equipped to capture platform dynamics." → CONSTRAINED+theory · [DP-REL-5; DP-KIND-2] · · N
E11 · "Institutional barriers constrain the translation of research findings into practice." → CONSTRAINED+practice_alignment · [DP-REL-5/DP-PREC-12; DP-KIND-4] · A-cell: constraint head over the bridge itself · N
EC1 · [control] "Little evidence exists among frontline workers." → LIMITED+evidence · [DP-CROSS-5; DP-KIND-1] · population restriction never becomes CONSTRAINED · N
EC2 · [control] "Prior theory constrains our view of X." → review · [DP-REL-11] · metaphorical head unmappable · Y (R5)

**DISCONNECTED — 8 positives.**
F1 · "Evidence on X is disconnected from current managerial practice." → DISCONNECTED+practice_alignment · [DP-REL-6; DP-KIND-4] · frozen anchor · N
F2 · "Academic understanding of X has not translated into practice." → DISCONNECTED+practice_alignment · [DP-REL-6; DP-KIND-4] · frozen anchor · N
F3 · "Research and practice remain poorly aligned on X." → DISCONNECTED+practice_alignment · [DP-REL-6/DP-PREC-8; DP-KIND-4] · degree within family · N
F4 · "Existing research does not address the problems practitioners face." → DISCONNECTED+practice_alignment · [DP-REL-6; DP-KIND-4] · BR-GAP-12 wording · N
F5 · "Managerial practice diverges from what the evidence recommends." → DISCONNECTED+practice_alignment · [DP-REL-6/DP-PREC-13; DP-KIND-4] · cross-pole divergence · N
F6 · "Research knowledge about X has not reached practitioners." → DISCONNECTED+practice_alignment · [DP-REL-6; DP-KIND-4] · non-translation · N
F7 · "Scholarly evidence on X has yet to inform practice." → DISCONNECTED+practice_alignment · [DP-REL-6; DP-KIND-4] · non-translation · N
F8 · "The findings of this literature and everyday clinical practice have drifted apart." → DISCONNECTED+practice_alignment · [DP-REL-6; DP-KIND-4] · divergence state · N
FC1 · [control] "Prior work has not connected findings on X with theories of Y." → ABSENT+theory · [DP-PREC-7; DP-KIND-2] · literature-internal · N
FC2 · [control] "Managers do not understand X." → no pair · [DP-REVIEW-R1] · practitioner capability; upstream-boundary inconsistency · Y (R1)

**CHALLENGED — 8 positives.**
G1 · "Previous theories assume stable boundaries, but this assumption is mistaken." → CHALLENGED+theory · [DP-REL-7; DP-KIND-2] · frozen anchor · N
G2 · "The standard model does not hold in multi-sided markets." → CHALLENGED+theory · [DP-REL-7; DP-KIND-2] · restriction preserved · N
G3 · "The prevailing interpretation of X is mistaken." → CHALLENGED+theory · [DP-REL-7; DP-KIND-2] · · N
G4 · "Reported effects of X are, we contend, artifacts of measurement error." → CHALLENGED+evidence · [DP-REL-7; DP-KIND-1] · A-cell: findings challenged · N
G5 · "Established survey approaches, we argue, systematically misstate X." → CHALLENGED+method · [DP-REL-7; DP-KIND-3] · A-cell: method's warrant challenged · N
G6 · "The dominant view rests on a flawed premise." → CHALLENGED+theory · [DP-REL-7; DP-KIND-2] · · N
G7 · "We challenge the assumption that X drives Y." → CHALLENGED+theory · [DP-REL-7/DP-REL-3a; DP-KIND-2] · authors contest · N
G8 · "The received view is mistaken." → CHALLENGED+unspecified · [DP-REL-7; DP-KIND-5] · A-cell kind-silent (rare) · N

**Count audit.** Relation positives: ABSENT 12 ✓ · LIMITED 13 ✓ · CONFLICTING 9 ✓ · UNTESTED 8 ✓ · CONSTRAINED 11 ✓ · DISCONNECTED 8 ✓ · CHALLENGED 8 ✓ — controls (DC1, DC2, EC1, EC2, FC1, FC2) and review cases counted toward no minimum. Kind counts across all pair-bearing items: evidence 27 ✓(≥15) · theory 14 ✓(≥12) · method 10 ✓(≥10) · practice_alignment 12 ✓(≥8; four beyond-DISCONNECTED: B11, B12, E11, A12) · unspecified 10 ✓(≥10).

## 39.24 Adversarial minimal-pair suite (35 comparisons; one left-vs-right comparison per MP ID; each states what changed and why)

MP-01 · "No evidence exists on X." → ABSENT+evidence ‖ "Little evidence exists on X." → LIMITED+evidence · **relation changed** (zero vs degree, DP-PREC-1).
MP-02 · "X has never been examined." → ABSENT+evidence ‖ "X has rarely been examined." → LIMITED+evidence · **relation changed** (never vs rarely).
MP-03 · "X remains unexplored." → ABSENT+evidence ‖ "X remains underexplored." → LIMITED+evidence · **relation changed** (categorical vs degree morphology).
MP-04 · "No theoretical model explains X." → ABSENT+theory ‖ "The existing model remains empirically untested." → UNTESTED+evidence · **both changed** (artifact existence flips relation, DP-PREC-2; missing account vs missing verification flips kind).
MP-05 · "Existing theory cannot explain X." → CONSTRAINED+theory ‖ "Existing theory is wrong about X." → CHALLENGED+theory · **relation changed** (incapacity vs falsity, DP-PREC-5).
MP-06 · "Prior findings disagree." → CONFLICTING+evidence ‖ "The prevailing interpretation is mistaken." → CHALLENGED+theory · **both changed** (who rejects, DP-PREC-4; findings vs interpretation).
MP-07 · "Evidence is scarce because methods are weak." → LIMITED+evidence ‖ "Existing methods cannot capture X." → CONSTRAINED+method · **both changed** (head vs reason, DP-PREC-9; deficient item shifts to the method resource).
MP-08 · "Measure X has not been validated." → UNTESTED+evidence ‖ "Measure X cannot capture Y." → CONSTRAINED+method · **both changed** (verification-act denial vs capability restriction; missing validation vs deficient resource).
MP-09 · "Managers do not understand X." → no pair (R1) ‖ "Research knowledge about X has not translated to managers." → DISCONNECTED+practice_alignment · **entry status changed** (practitioner capability never enters; two-pole non-translation does).
MP-10 · "X is poorly understood." → LIMITED+unspecified ‖ "Empirical evidence on X is limited." → LIMITED+evidence · **kind changed** (frozen understood-anchor vs explicit empirical commitment).
MP-11 · "X is poorly understood." → LIMITED+unspecified ‖ "Theoretical understanding of X is limited." → LIMITED+theory · **kind changed** (modifier commits, DP-KIND-9).
MP-12 · "Research on X is limited." → LIMITED+unspecified ‖ "Existing methods for researching X are limited." → LIMITED+method · **kind changed** (bare generic vs explicit methodological resource).
MP-13 · "Findings on X have not been connected with theories of Y." → ABSENT+theory ‖ "Findings on X have not been connected with practice." → DISCONNECTED+practice_alignment · **both changed** (pole test, DP-PREC-7).
MP-14 · "Evidence on X is scarce." → LIMITED+evidence ‖ "Evidence on X is scarce, and prior findings on Y conflict." → R4 · **review status changed** (two independent predicates; separation, then each instance pairs on its own).
MP-15 · "The theory remains untested." → UNTESTED+evidence ‖ "The theory is untested and, we argue, mistaken about Z." → R4 · **review status changed** (verification denial + invalidity as independent predications; never blended, no primary).
MP-16 · "Little is known about X." → LIMITED+evidence ‖ "Little is known about the measurement of X." → LIMITED+evidence · **neither changed** (DP-KIND-6: topic ≠ kind; the deficient item is what-is-known in both).
MP-17 · "No consensus exists on X." → CONFLICTING+unspecified ‖ "No evidence exists on X." → ABSENT+evidence · **both changed** (disagreement vs nonexistence; kind-silence vs explicit evidence).
MP-18 · "The assumption fails in digital markets." → CHALLENGED+theory ‖ "The assumption has never been tested in digital markets." → UNTESTED+evidence · **both changed** (invalidity vs verification denial; context preserved in each).
MP-19 · "These mechanisms remain unexplored." [antecedent supplied] → ABSENT+evidence ‖ same sentence, no recoverable antecedent → held at Step 5 (BR T2b); if presented → R1 · **entry status changed** (grounding, not pair semantics).
MP-20 · "Practice and research disagree on X." → DISCONNECTED+practice_alignment ‖ "Researchers disagree on X." → CONFLICTING+unspecified · **both changed** (cross-pole divergence vs within-research disagreement, DP-PREC-13).
MP-21 · "The model has never been tested." → UNTESTED+evidence ‖ "No evidence supports the model." → ABSENT+evidence · **relation changed** (testing-act denial vs support-nonexistence, DP-PREC-10); kind evidence in both.
MP-22 · "The model has never been tested." → UNTESTED+evidence ‖ "Evidence supporting the model remains limited." → LIMITED+evidence · **relation changed** (act denial vs support insufficiency).
MP-23 · "The model remains untested." → UNTESTED+evidence ‖ "The model is empirically wrong." → CHALLENGED+theory · **both changed** (verification denial vs asserted invalidity; missing verification [evidence] vs the challenged model itself [theory]) — "empirically" is a grounds adverb on "wrong" and does not make the kind evidence (DP-KIND-9a); the kind reads off the challenged item.
MP-24 · "No empirical evidence supports the assumption." → ABSENT+evidence ‖ "Empirical support for the assumption is limited." → LIMITED+evidence · **relation changed** (support zero vs support degree).
MP-25 · "Empirical support for the assumption is limited." → LIMITED+evidence ‖ "Evidence supporting the assumption is mixed." → CONFLICTING+evidence · **relation changed** (insufficiency vs incompatibility of support).
MP-26 · "The assumption has never been empirically tested." → UNTESTED+evidence ‖ "The assumption lacks empirical support." → ABSENT+evidence · **relation changed** — the dedicated support≠testing family pair (the v1.0 mis-mapping's exact contrast).
MP-27 · "Research-practice integration remains limited." → LIMITED+practice_alignment ‖ "Research and practice are disconnected." → DISCONNECTED+practice_alignment · **relation changed** (process-development insufficiency vs disrelation state, DP-PREC-11); kind pa in both.
MP-28 · "Institutional barriers constrain research-to-practice translation." → CONSTRAINED+practice_alignment ‖ "Research has not translated into practice." → DISCONNECTED+practice_alignment · **relation changed** (constraint head over the bridge vs disrelation state, DP-PREC-12); kind pa in both.
MP-29 · "Managers struggle to understand X." → no pair (R1) ‖ "Research knowledge about X is poorly integrated into managerial practice." → DISCONNECTED+practice_alignment · **entry status changed**; right side's head is a disrelation-state participle ("poorly integrated") → DISCONNECTED per DP-PREC-11.
MP-30 · "X remains poorly understood." → LIMITED+unspecified ‖ "Empirical understanding of X remains limited." → LIMITED+evidence · **kind changed** (frozen boundary; the modifier converts the understanding-family wording).
MP-31 · "Theoretical explanation of X is limited." → LIMITED+theory ‖ "Empirical evidence for model X is limited." → LIMITED+evidence · **kind changed** (theoretical resource vs empirical support around the same model; the model's category decides nothing, DP-CROSS-1).
MP-32 · "No validated method exists for X." → ABSENT+method ‖ "Method X exists but has not been validated." → UNTESTED+evidence · **both changed** (resource absent vs existing artifact's verification act denied; DP-KIND-3 split).
MP-33 · "Evidence is scarce because available methods are expensive." → LIMITED+evidence ‖ "Available methods cannot capture X." → CONSTRAINED+method · **both changed** (causal reason preserved vs capability head; DP-PREC-9).
MP-34 · "No mechanism exists for translating research findings into practice." → ABSENT+practice_alignment ‖ "Research findings have not translated into practice." → DISCONNECTED+practice_alignment · **relation changed** (categorical absence of the bridge entity vs disrelation state, DP-PREC-15); kind pa in both.
MP-35 · "No validated method exists for measuring X." → ABSENT+method ‖ "No mechanism exists for translating research findings on X into practice." → ABSENT+practice_alignment · **kind changed** (research-generating resource vs bridge apparatus, DP-KIND-4a); relation ABSENT in both.

## 39.25 Versioning / re-annotation

- **Version:** `A1E-DPR-1.1`, pinned as Step-3's `predicate_registry_version` in every gold record, rationale context, and extraction/verification diagnostic. rule_id stability: DP-* IDs permanent; retired IDs never reused; rules revised in this version (DP-REL-4, DP-REL-6, DP-KIND-3, DP-KIND-4, DP-KIND-5, DP-TRACE-3, DP-TRACE-4) keep their IDs with revised text; new IDs appended (DP-KIND-1a, DP-KIND-4a, DP-KIND-9a, DP-PAIR-2a, DP-PAIR-3a, DP-PREC-10..15).
- **Amendment classes → consequences** (via the Protocol's rationale-code index): *clarifying amendment* (wording, exemplars): selective re-adjudication of items citing the entry; *semantic amendment* (criterion/mapping change): re-adjudication of items citing the entry plus affected relation/kind strata and review-pool items with the affected value among competitors; *compatibility-matrix change*: re-adjudication of affected cells plus touched A-cell items; *rule retirement*: as semantic amendment of the dependency closure. Sealed cohorts are never silently relabeled. Platform-wide manuscript versioning out of scope.
- **v1.0 → v1.1 consequence note.** No final gold exists; no sealed cohorts exist; any pilot material labeled under `A1E-DPR-1.0` is re-adjudicated against v1.1 before informing calibration — the affected strata are the UNTESTED row (kind), the support-family items, and every practice_alignment item.

## 39.26 Open decisions

- **OD-DPR-1 — A-cell exemplar libraries (calibration-only; does not block final gold).** All A-cell licensing criteria are decided; exemplar libraries for the rarer cells — CONFLICTING×theory/method/unspecified, CONSTRAINED×evidence/unspecified, CHALLENGED×evidence/method/unspecified, and the new LIMITED×practice_alignment, CONSTRAINED×practice_alignment, and ABSENT×practice_alignment — grow from pilot adjudications as clarifying amendments. (UNTESTED×unspecified no longer exists and is removed from this list.) Resolving evidence: pilot adjudication records. Blocks final gold: no.
- **OD-DPR-2 — "fails to [verb]" residue (bounded; does not block final gold).** The frozen inputs settle "fails" as invalidity (CHALLENGED) and "cannot" as incapacity (CONSTRAINED) but genuinely underdetermine hybrids ("fails to capture/account for") where neither reading is textually recoverable → review R3, never a legislated default. Resolving evidence: pilot frequency + adjudication outcomes → clarifying exemplars, or a contract-governance proposal if a default proves necessary. Blocks final gold: no.

## 39.27 Freeze check

### Carried forward (all 38 v1.0 checks, re-audited under v1.1)

All thirty-eight v1.0 checks re-audited: **PASS** — with corrected evidence where the revision touched them: "UNTESTED respects its frozen empirical-verification meaning" now holds *more strongly* (evidence-only row; support-family excluded); "compatibility matrix covers all 35 combinations" holds at the recomputed 12 C / 13 A / 10 P; "prohibited combinations are semantically justified" holds for the new P-set (incl. the corrected ABSENT/CONFLICTING/CHALLENGED × practice_alignment justifications); "normative tests are internally consistent with the decision procedure" now holds with honest positive counts; the v1.0 evidence for `unspecified` tracing is replaced by the corrected DP-TRACE-4 (existing fields only). One v1.0 check — "production shared traces and gold field-specific traces remain compatible" — is now passed *without* the invented field it previously leaned on.

### New v1.1 checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| Every valid UNTESTED proposition maps to knowledge_kind = evidence | PASS | DP-KIND-1a; DP-REL-4 kind consequence; D1–D8 |
| UNTESTED × unspecified is prohibited | PASS | §39.7 UNTESTED row (C,P,P,P,P); cell justification |
| "The model remains untested" maps to UNTESTED + evidence | PASS | D6; MP-23 left; "empirically" not required (DP-REL-4) |
| Absence of empirical support is not automatically UNTESTED | PASS | DP-PREC-10 hard rule; A11/DC1; MP-21/26 |
| "No empirical evidence supports X" maps independently from "X has never been empirically tested" | PASS | ABSENT+evidence vs UNTESTED+evidence; MP-21/26; DP-REL-1 vs DP-REL-4 conditions |
| LIMITED practice_alignment and DISCONNECTED practice_alignment are semantically distinguishable | PASS | DP-PREC-11 (process-development vs disrelation state); B11/B12 vs F1–F3; MP-27 |
| CONSTRAINED practice_alignment and DISCONNECTED practice_alignment are distinguishable where explicit wording supports both | PASS | DP-PREC-12; E11 vs F2; MP-28; reason-only barriers excluded (DP-PREC-9) |
| practice_alignment does not automatically imply DISCONNECTED | PASS | DP-PAIR-2 extension; DP-PREC-14; B11/B12/E11; MP-27/28 |
| DISCONNECTED still implies practice_alignment under its frozen narrow meaning | PASS | DP-REL-6 one-way implication; §39.7 DISCONNECTED row |
| The practice_alignment column has been fully re-audited | PASS | §39.7: DISC C · LIM A · CONSTR A · ABSENT A · CONFLICTING P · UNTESTED P · CHALLENGED P, each with cell-level justification and (for A) instantiating text |
| Matrix validation does not override independently derived axis semantics | PASS | DP-PAIR-3a validator-not-classifier; P5 in §39.19; adjudication drill |
| No invented annotation field exists | PASS | DP-TRACE-4 corrected; unspecified card; §39.22 note |
| `kind_commitment: none_in_span` does not appear as a required schema field | PASS | Removed everywhere; document-wide absence |
| unspecified is grounded using existing kind_trace_refs + rationale_codes | PASS | DP-TRACE-4; the "Collective adaptation" worked example (§39.4) |
| At least 10 positive ABSENT cases exist | PASS | A1–A12 (12) |
| At least 10 positive LIMITED cases exist | PASS | B1–B13 (13) |
| At least 8 positive CONFLICTING cases exist | PASS | C1–C9 (9) |
| At least 8 positive UNTESTED cases exist | PASS | D1–D8 (8) |
| At least 10 positive CONSTRAINED cases exist | PASS | E1–E11 (11) |
| At least 8 positive DISCONNECTED cases exist | PASS | F1–F8 (8) |
| At least 8 positive CHALLENGED cases exist | PASS | G1–G8 (8) |
| Negative controls are not counted as positive cases | PASS | DC/EC/FC items marked [control], excluded from the count audit |
| Review/no-pair cases are not counted as positive cases | PASS | EC2, FC2 excluded; count audit (§39.23) |
| Knowledge-kind minimum counts are independently satisfied | PASS | evidence 27 / theory 14 / method 10 / practice_alignment 12 (4 beyond DISCONNECTED) / unspecified 10 |
| At least 30 genuine minimal-pair comparisons exist | PASS | MP-01…MP-35 |
| Each MP ID represents one actual left-vs-right comparison | PASS | §39.24 format; no b-variant counting; change-type stated per pair |
| The test suite and 35-cell matrix are mutually consistent | PASS | Every suite pair occupies a C or A cell with its licensing wording present; no suite item lands on P; review items emit conditions, not pairs |
| A challenged model/theory keeps kind = theory despite empirical grounds of the challenge | PASS | DP-KIND-9a; DP-REL-7 positive; MP-23; the challenged-item test (findings → evidence remains via G4) |
| Absent bridge, unlinked state, and absent research method are three distinct classifications | PASS | DP-KIND-4a; DP-PREC-15; A12 vs F2 vs A8; MP-34/MP-35; adjudication drill |
| No Step-7/8/9/11/13 ownership leakage was introduced | PASS | §39.16 (Step 8), §39.20-note (Step 7), §39.13 (spawn/merge mechanics excluded), §39.18 (runtime/verification codes excluded), §39.22 (Step-3 architecture untouched) |

**All checks PASS — the A.1-E Deficiency Predicate Registry is declared FROZEN at v1.1 (`A1E-DPR-1.1`), pinned to `A1E-BR-1.2`.**
