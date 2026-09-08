# A.1-E Signal Library v1.1 — EpistemicOS (Step 7)

**Status:** normative once the Freeze Check (§40.45) passes. Version string: `A1E-SL-1.1`.
**Revision record (v1.0 → v1.1) — exactly these corrections:** 1. strength_tier vocabulary normalized. 2. local deficiency predication separated from manuscript adoption status. 3. frozen Step-6 detection coverage expanded for absent theory/model, absent method/measure, and support-predicate constructions. 4. contribution/reference "fill this gap" behavior made explicit. 5. temporal-resolution context signal added and tests reconciled. 6. false-friend examples expanded into explicit executable normative tests. 7. signal/test registry completeness re-audited. No unrelated signal semantics changed.
**Final-issuance corrections (7C; version unchanged):** 1. `ambiguous_semantics` removed from polarity values and retained as metadata. 2. support-predicate coverage corrected so "No empirical evidence supports X" maps only to SL-SUP-4 at Step 7. 3. SL-POS-2 surface coverage expanded to include "This gap motivates our/the present study." 4. MP-11 corrected to remove the undefined pseudo-signal `SL-WORLD-adjacent`; the right-hand world-state example now correctly has no Step-7 signal. **No other Step-7 semantics changed.**
**Document form:** complete and self-contained; independently interpretable without legacy KB files.
**Normative frozen inputs (pinned):** `A1E_gap_extraction_contract_v1-2.md` · `A1E_gap_object_schema_v1-2.md` · `A1E_annotation_validation_protocol_v1-2.md` · `A1E_state_machine_v1-3.md` · `A1E_boundary_rulebook_v1-2.md` (**A1E-BR-1.2**) · `A1E_deficiency_predicate_registry_v1-1.md` (**A1E-DPR-1.1**). Steps 1–6 are not reinterpreted or altered.

---

## 40.1 Purpose and ownership boundary

Step 7 answers exactly one question: **what observable textual/contextual signals may indicate that a proposition should be considered by the later A.1-E candidate detector?** It defines the **static signal knowledge base**: positive lexical/phrase/syntactic signals, semantic-deficiency cue families, discourse-positioning signals, contextual-support signals, anti-signals, boundary-adjacent signals, section priors, categorical signal-strength metadata, intrinsic signal interactions, detection-oriented examples/counterexamples, and stable machine-referenceable signal IDs.

**Frozen architecture:** Step 7 (Signal Library — "what features exist?") → Step 10 (Candidate Detection Spec — "how are features operationally combined to emit candidates?") → Step 11 (Extraction Spec). Step 7 MUST NOT become Step 10. Step 7 decides none of the following: whether any passage is a GAP; candidate emission, thresholds, scoring formulas, windows, ranking, deduplication, or merge; proposition segmentation; affected object (Step 8); relation or knowledge_kind (Step 6); scientific validity; gap characterization; runtime verification (Step 13). A signal entry may carry categorical metadata ("little is known" — strength STRONG — family limited-knowledge cue); it may never carry an emission rule ("IF strong_signal ≥ 1 THEN emit"). Categorical metadata is always preferred over runtime scoring; no numeric value in this document is an emission rule.

## 40.2 Frozen inputs and dependencies

The library is built against the frozen semantics of `A1E-BR-1.2` (boundary classes, assertion-vs-reference, positioning G5, practitioner-capability exclusion) and `A1E-DPR-1.1` (seven relations, five kinds, support≠testing, the four practice_alignment patterns, "fails to" residue OD-DPR-2). Links from signals to BR-* and DP-* rules are **informational crosswalks only** (§40.35–40.36); they never assign a class, relation, or kind. Nothing here adds fields to the frozen Gap Object Schema; the signal record (§40.4) is a Step-7 registry structure, not a production gap object.

## 40.3 Signal-library principles

**SIGNAL ≠ SEMANTIC VERDICT.** A signal means "this wording/context is worth presenting to the later candidate detector" — never "this is a gap." The library is **recall-supporting**: the detector should eventually over-generate safely because Step 5 provides the semantic boundary classifier. Consequences, frozen and repeated throughout: positive signal ≠ GAP · anti-signal ≠ automatic exclusion · high section prior ≠ GAP · low section prior ≠ automatic exclusion · lexical phrase ≠ semantic decision · "few studies" → strong deficiency signal ≠ automatically GAP · "future research should" → boundary signal ≠ automatic FUTURE_RESEARCH · "our study is limited" → anti-signal ≠ candidate deletion · "gap" ≠ GAP · "untested" ≠ relation assignment · "research and practice are disconnected" ≠ a Step-7 `(DISCONNECTED, practice_alignment)` output.

## 40.4 Signal object structure (Step-7 registry record)

Every signal is specified with: `signal_id` · `signal_family` · `signal_type` · `canonical_description` · `surface_forms` (incl. controlled variants) · `semantic_function` · `strength_tier` (exactly one of STRONG / MODERATE / WEAK / NOT_APPLICABLE) · `polarity` (one of positive / anti / context / boundary / reference / prior) · `required_context` (target/subject/syntax constraints) · `exclusions` · `nearest_confusions` · `section_modifiers` (if any) · `examples_positive` · `examples_negative` · `related_boundary_rules` (BR-*) · `related_predicate_rules` (DP-*) · `notes` (incl. `negation_scope_sensitive`, `coreference_dependent`, `attribution_sensitive`, `ambiguous_semantics`, `token_boundary_required`, `hyphen_variant_allowed`, `cross_sentence_context_possible` flags where applicable). Family sections (§40.7–40.27) are the normative cards; the registry table (§40.37) is the index.

## 40.5 Signal types

`LEXICAL` (single word) · `PHRASE` (multi-word) · `SYNTACTIC` (construction pattern) · `PREDICATE_PATTERN` (head predicate + target constraint) · `DISCOURSE` (positioning/consequence/contrast markers) · `COREFERENCE_CONTEXT` · `SECTION_PRIOR` · `ANTI_SIGNAL` · `BOUNDARY_ADJACENT`.

## 40.6 Signal strength and polarity

Closed strength tiers — exactly **STRONG / MODERATE / WEAK / NOT_APPLICABLE** — describing only *how directly the feature expresses deficiency-like semantics for candidate discovery*. Strength is NOT probability, confidence, scientific truth, severity, importance, relation strength, or annotation certainty; no probabilistic confidence exists anywhere. Polarity values — exactly `positive` (deficiency-cue), `anti` (deficiency-unlikely / adjacent-class cue), `context` (interpretation-modifying), `boundary` (adjacent-class cue), `reference` (reference-only form), `prior` (section).
**Hard separation rule (v1.1):** `strength_tier` encodes only detection-directness; `polarity` encodes semantic role/context. The axes are never fused: compound forms ("STRONG-anti", "STRONG-boundary", "MODERATE-boundary"), tier ranges ("WEAK/MODERATE", "MODERATE/WEAK"), and "—" are prohibited in any normative strength_tier field. **Every signal_id carries exactly one strength_tier value.** Pure context signals with no meaningful deficiency-directness (SL-ATTR-1/2, SL-REVERSAL-1, SL-COREF-1, SL-TEMP-1) carry `NOT_APPLICABLE` + polarity `context`; section-prior records carry `NOT_APPLICABLE` + polarity `prior`. SL-CITE-1 retains tier WEAK + polarity context, preserving the frozen "weak, never required" citation characterization. Examples: "No studies have examined X." → STRONG; bare "gap" → WEAK; "important" → not a deficiency signal at all. No numeric strength values exist.

---

## 40.7 Categorical-absence signals (family CATEGORICAL_ABSENCE; crosswalk DP-REL-1)

Canonical cue: categorical non-existence/non-occurrence of a prior-knowledge state. **Required context throughout: the grammatical target is a knowledge item or research activity** (studies, evidence, account, examination, understanding-as-established) — not a world state, procedure, or statistical result.

- **SL-ABS-1** · PREDICATE_PATTERN · STRONG · "no [studies|research|work|prior work] ha(s/ve) [examined|investigated|addressed|explored] …" · excl: own-study procedure ("No additional analyses were conducted."), participant reports ("No participants reported X."). `negation_scope_sensitive`.
- **SL-ABS-2** · PHRASE · STRONG · "no evidence [exists|is available] (on/about) …" / "there is no evidence …" · excl: support-predicate constructions ("no evidence supports X" → SL-SUP-4, not this signal, unless an existential absence predicate is independently present); search-result statements ("No evidence of fraud was found." — a finding about the world) and statistical results ("no significant difference", "no effect was found").
- **SL-ABS-3** · PHRASE · STRONG · "there is no [account|theory|theoretical account|data|research] (of/on) …".
- **SL-ABS-4** · PREDICATE_PATTERN · STRONG · "… has never been [studied|examined|investigated]" · `negation_scope_sensitive` ("has now been examined" must not fire).
- **SL-ABS-5** · PREDICATE_PATTERN · STRONG · "… remains [unexplored|unanswered|unknown]" / "remains an open question" · excl: attributive own-study exploration ("we explored the previously unexplored region" — the manuscript is removing, not asserting, the absence: reversal context §40.26); algorithmic/parameter-space use ("unexplored parameter space") is a false friend (FF-28). `token_boundary_required` (unexplored ≠ under-explored: that variant belongs to SL-LIM-4).
- **SL-ABS-6** · PREDICATE_PATTERN · STRONG · "nothing is known about …" / "… is not known" / "we (still) do not understand …" / "researchers do not understand …" · required context: knowledge-community subject ("we" as research community, "researchers", "the literature") — practitioner subjects route to SL-WORLD-1 (hard pair: "Managers do not understand X." → anti-signal). `attribution_sensitive`; "we" subject flagged `requires_subject_resolution`.
- **SL-ABS-7** · PHRASE · STRONG · "… has received no attention" · hedged variants ("virtually no", "almost no") stay in-family with flag `hedge_present` — the ABSENT-vs-LIMITED strength question is later Step-6 work (DP-PREC-1), never resolved here.

- **SL-ABS-8** · PREDICATE_PATTERN · STRONG · positive · categorical absence of an explanatory theoretical/model resource: "no [model|framework|theory|account] exists (for/of) …" / "no [model|framework|theory] [explains|accounts for] …" · required context: the absent subject/object is a research/theoretical knowledge resource · FF: "no model was fitted in specification 3" (FF-43 — present-study procedure) · crosswalk DP-REL-1 informational only; kind wording preserved for Step 6.
- **SL-ABS-9** · PREDICATE_PATTERN · STRONG · positive · categorical absence of a research-generating methodological resource: "no [validated] [method|measure|instrument|procedure|design] exists (for/to) …" / "no established procedure exists for …" · required context: method/measure/instrument/design/analytic resource as the absent research resource · FF: "No method was used in the robustness analysis." (FF-44 — present-study procedure); "No instrument was available in the room." (FF-45 — world/instrument state) · no `method` kind is assigned here; the resource wording is preserved for Step 6.

False friends affecting this family: FF-14–FF-17, FF-34–FF-36, FF-43–FF-45. Related rules: BR G1–G3 (informational); DP-REL-1.

## 40.8 Limited-knowledge signals (family LIMITED_KNOWLEDGE; crosswalk DP-REL-2)

Canonical cue: knowledge exists but is scarce/insufficient/underdeveloped.

- **SL-LIM-1** · PHRASE · STRONG · "little is known (about) …".
- **SL-LIM-2** · PHRASE · STRONG · "few studies [have] [examined|investigated|addressed] …" / "few researchers …".
- **SL-LIM-3** · PHRASE · STRONG · "[limited|scarce|scant|sparse] [evidence|research|attention|work] (on/exists)" · **exclusion:** "limited by …" never joins this family — capability construction → SL-CSTR-3 ("limited evidence exists" vs "evidence is limited by cross-sectional design" have different signal functions; the LIMITED-vs-CONSTRAINED decision is Step 6's, but the two surface constructions are kept apart here) · FF: limited liability/company/edition (FF-10–12), Methods "data were limited to …" (FF-13).
- **SL-LIM-4** · LEXICAL · STRONG · "underexplored / under-explored / under explored" · "understudied / under-studied / under studied" · "rarely examined" · `hyphen_variant_allowed`; contrast SL-ABS-5 ("unexplored" is categorical — separate signal).
- **SL-LIM-5** · PHRASE · STRONG · "poorly understood / not well understood / incomplete understanding (of)".
- **SL-LIM-6** · PHRASE · MODERATE · "thin literature / underdeveloped [research|literature] (on)".
- **SL-LIM-7** · PHRASE · STRONG · "limited [theoretical|empirical] understanding (of)" · note: the kind-marking modifier is preserved as surface metadata for later Step-6 use; no kind is assigned.

Related rules: BR G1–G3; DP-REL-2; DP-PREC-1/3 (informational).

## 40.9 Conflict/inconsistency signals (family CONFLICT_INCONSISTENCY; crosswalk DP-REL-3)

Canonical cue: incompatibility within prior knowledge. **Required context: the disagreeing items are prior-knowledge positions/results** — `requires_prior_knowledge_target = true` on every entry; world-state disagreement ("conflicting priorities among managers", FF-41) does not qualify. The actual semantic decision remains Step 5/6.

- **SL-CONF-1** · PHRASE · STRONG · "mixed [findings|evidence|results]" · FF: "mixed methods" (FF-08), "mixed sample" (FF-09).
- **SL-CONF-2** · PHRASE · STRONG · "[inconsistent|contradictory|conflicting] [findings|results|evidence|conclusions]".
- **SL-CONF-3** · PREDICATE_PATTERN · STRONG · "[studies|scholars|prior findings] disagree".
- **SL-CONF-4** · PHRASE · STRONG · "no consensus (exists) (on)" · FF: "consensus was not required" (FF-37).
- **SL-CONF-5** · PHRASE · MODERATE · "debate persists / remains contested" · `attribution_sensitive` — whether prior parties or the authors contest is later Step-6 work (DP-REL-3a); never resolved here.
- **SL-CONF-6** · PHRASE · STRONG · "competing [explanations|theories|accounts] (remain unresolved)".

## 40.10 Testing/validation signals (family TESTING_ABSENCE; crosswalk DP-REL-4)

Canonical cue: denial of the verification **act** over an existing artifact. **Hard inheritance from Step 6: testing-absence signals and support-absence signals are separate families and are never synonyms** (support family: §40.11). Useful required context: an identifiable artifact mention (model/proposition/measure/framework) as grammatical subject.

- **SL-TEST-1** · PREDICATE_PATTERN · STRONG · "(remains) untested / has not been tested / has never been tested / yet to be tested" · FF: "the test was not applicable" (FF-18), "test set" (FF-19); `token_boundary_required` ("test" ≠ "latest").
- **SL-TEST-2** · PREDICATE_PATTERN · STRONG · "has not been validated / remains unvalidated / awaits empirical validation" · FF: "validation dataset" (FF-20), "invalid input" (FF-21); `token_boundary_required` ("valid" ≠ "invalid"/"validated").
- **SL-TEST-3** · PREDICATE_PATTERN · STRONG · "has not been [verified|evaluated] / awaits empirical scrutiny".

Explicit false-friend pairs (metadata on all three): untested ↔ unsupported · unvalidated ↔ weakly supported · never examined ↔ tested-but-unsupported.

## 40.11 Evidential-support signals (family EVIDENTIAL_SUPPORT; crosswalk DP-REL-1/2/3 via support head)

Distinct family required because Step 6 freezes **testing absence ≠ evidential-support absence** (DP-PREC-10). These signals preserve the support-head surface so Steps 10/11 retain the distinction; no relation is assigned.

- **SL-SUP-1** · PREDICATE_PATTERN · STRONG · "lacks (empirical) support / unsupported / no (empirical) support (for)" · `negation_scope_sensitive`.
- **SL-SUP-2** · PHRASE · MODERATE · "[little|weak|limited|insufficient] support (for)".
- **SL-SUP-3** · PHRASE · STRONG · "support (for …) is mixed / evidence supporting … is mixed" · crosswalk note: support-conflict wording; later semantics decide among DP-REL-1/2/3 readings.
- **SL-SUP-4** · PREDICATE_PATTERN · STRONG · positive · support-predicate form: "no (empirical) evidence supports …" / "evidence does not support …" over a claim/proposition · required context: **prior/current knowledge-support target** — the manuscript's own result-reporting ("The results do not support H1.", FF-46) is excluded via context metadata, without solving the Step-5 boundary here · kept strictly separate from SL-TEST ("has not been tested") and from existential absence ("no evidence exists on X" → SL-ABS-2): existential evidence absence, support-predicate evidence absence, and testing-act absence are three distinct surface constructions, never collapsed.

## 40.12 Capability/constraint signals (family CAPABILITY_CONSTRAINT; crosswalk DP-REL-5)

Canonical cue: an existing knowledge resource's capability/warrant restriction. **Required context: the incapable subject is a knowledge resource** (theories, measures, methods, designs, evidence, models, the literature) — world/instrument subjects are false friends ("our camera cannot capture X", FF-38; "managers cannot explain X", FF-39).

- **SL-CSTR-1** · PREDICATE_PATTERN · STRONG · "cannot [explain|account for|capture|distinguish|identify|support (causal) inference]".
- **SL-CSTR-2** · PREDICATE_PATTERN · STRONG · "unable to [explain|capture] / ill-equipped to / not designed to/for".
- **SL-CSTR-3** · PREDICATE_PATTERN · STRONG · "[limited|constrained|restricted] by [reliance on …|its design|cross-sectional data|…]" · kept apart from SL-LIM-3 by construction ("limited by" vs "limited evidence").
- **SL-CSTR-4** · SYNTACTIC · MODERATE · "relies on X, leaving Y [unexamined|unmeasured|unaddressed]".
- **SL-CSTR-5** · PHRASE · MODERATE · "provide(s) only [partial insight|coarse estimates] / cannot separate X from Y".
- **SL-CSTR-6** · PREDICATE_PATTERN · STRONG · positive · "fails to [explain|capture|account for]" · **`ambiguous_semantics = true`:** per `A1E-DPR-1.1` OD-DPR-2, "fails to …" is semantically unresolved between constraint- and challenge-readings; this signal is detection-visible but MUST NOT be pre-classified as CONSTRAINED or CHALLENGED; the ambiguity is resolved (or routed to review R3) later. Listed in both this family and §40.14 by cross-reference; OD-DPR-2 is not resolved here.

FF for this family: FF-22 (optimization constraint), FF-23 (model constraint, technical).

## 40.13 Research-practice signals (family RESEARCH_PRACTICE; crosswalk DP-REL-1×pa / DP-REL-2×pa / DP-REL-5×pa / DP-REL-6 per subfamily)

The four-way distinction frozen in `A1E-DPR-1.1` (DP-KIND-4a, DP-PREC-11/12/15) is preserved as **four detection subfamilies** — never collapsed into a generic "practice gap" signal:

- **SL-DISC-A1** (absent bridge apparatus) · PHRASE · STRONG · "no [mechanism|pathway|channel|infrastructure] exists for translating [research|findings] into practice" · FF: "no mechanism exists in the machine" (FF-24-adjacent; engineering sense).
- **SL-DISC-B1** (limited bridge/process) · PHRASE · STRONG · "[translation|integration|uptake] of research into practice remains [limited|underdeveloped|partial]".
- **SL-DISC-C1** (constrained bridge) · PREDICATE_PATTERN · STRONG · "[barriers|factors|structures] [constrain|impede|restrict] (the) research-to-practice [translation|uptake]".
- **SL-DISC-D1** (disrelation state) · PREDICATE_PATTERN · STRONG · "[research|findings|evidence] ha(s/ve) not translated into practice / not reached practitioners / yet to inform practice".
- **SL-DISC-D2** (disrelation state) · PHRASE · STRONG · "research and practice [are disconnected|remain poorly aligned|have drifted apart|diverge]".

Anti-confusions (all `required_context`: both poles — research knowledge AND practice — must be named): "Managers do not understand X." → SL-WORLD-1, not this family · "Firms fail to implement X." → SL-WORLD-1 unless a research–practice relationship is asserted · "Research and theory are disconnected." → NOT this family (literature-internal; the wording may still carry SL-GAPLEX/SL-ABS-family cues). Orthographic variants: research-practice / research–practice / research practice (`hyphen_variant_allowed`).

## 40.14 Challenge/invalidity signals (family CHALLENGE_INVALIDITY; crosswalk DP-REL-7)

Canonical cue: authorially asserted wrongness of a prior position. **`attribution_sensitive` family-wide:** authors challenging a prior position is challenge-like; prior scholars disagreeing with each other is conflict-like (§40.9); neither relation is classified here.

- **SL-CHAL-1** · PREDICATE_PATTERN · STRONG · "[assumption|view|interpretation|model|theory] is [wrong|mistaken|flawed|misguided|invalid]" · FF: "the participant made a mistake" (FF-40), "invalid input" (FF-21).
- **SL-CHAL-2** · PREDICATE_PATTERN · STRONG · "does not hold (in) / breaks down / rests on a flawed premise".
- **SL-CHAL-3** · PHRASE · STRONG · "we [challenge|contest|dispute] (the [assumption|view|claim] that)" · FF: "challenging environment/problem" (FF-26/27).
- **SL-CHAL-4** · PHRASE · STRONG · "are artifacts of … / systematically misstate(s)".
- **SL-CHAL-5** · PREDICATE_PATTERN · STRONG · positive · "fails / fails to … / does not account for" · cross-reference of SL-CSTR-6: `ambiguous_semantics = true`; linked to later semantic adjudication (OD-DPR-2), never pre-classified.

## 40.15 Generic gap-lexeme signals (family GAP_LEXEME)

Generic deficiency lexemes are never automatically high-strength; the family's core job is separating **assertive deficiency use** from **nominal/reference-only use** (§40.16).

- **SL-GAPLEX-1** · PHRASE · MODERATE · "(there is) a gap in [knowledge|understanding|the literature|research] (about/on)" · assertive-existential frame elevates usefulness via INT-1; still ≠ GAP.
- **SL-GAPLEX-2** · LEXICAL · WEAK · bare "gap(s)" · `token_boundary_required`; FF: revenues–costs gap, wage/gender/generation/air gap, gap year, gap analysis (FF-01–07).
- **SL-GAPLEX-3** · LEXICAL/PHRASE · MODERATE · "lack of [evidence|research|understanding] / lacks / lacking" · required context: knowledge item as lacked object; FF: firms/managers/participants lack resources/expertise/information (FF-30–32) → SL-WORLD.
- **SL-GAPLEX-4** · LEXICAL · MODERATE · positive · "absence of [research|evidence]" · "missing / neglected / overlooked / unknown / unanswered / unresolved / underdeveloped / understudied" — the last two cross-listed with SL-LIM-4/6; assertive-vs-nominal use decides usefulness, not the lexeme.

Hard anti-shortcuts (frozen; also §40.45): "gap" ⇏ GAP · "lack" ⇏ GAP · "no" ⇏ ABSENT · "limited" ⇏ LIMITED · "mixed" ⇏ CONFLICTING · "untested" ⇏ candidate unless the grammatical target is relevant · "cannot" ⇏ CONSTRAINED · "wrong" ⇏ CHALLENGED · "practice" ⇏ practice_alignment · citation presence ⇏ GAP · Introduction ⇏ GAP · Future-Research section ⇏ FUTURE_RESEARCH · Methods section ⇏ exclusion. A signal is only an observable feature.

## 40.16 Assertion vs reference signals (family ASSERTION_REFERENCE)

Step 5 freezes assertion ≠ reference/presupposition (BR-CROSS-13); Step 7 provides the detection-oriented split without applying the boundary decision:

- **ASSERTIVE_DEFICIENCY_FORM** (class label, non-normative as an ID) — carried by the §40.7–40.15 families themselves ("Few studies examine X."; "No theory explains X."): a **local deficiency predication**, i.e., the clause itself contains a deficiency predicate satisfying a family's conditions. Locality is what fires the family — inside main clauses, complements of reporting verbs, quotations, rejected claims, and concessive constructions alike ("Smith argues that little is known about X." → the complement "little is known about X" is a local deficiency predication → SL-LIM-1 fires, plus SL-ATTR-1). **Frozen: local deficiency predication ≠ manuscript adoption.** Whether the manuscript adopts, endorses, rejects, or merely reports the predication is Step-5 semantic work; Step 7 detects the former and never decides the latter.
- **SL-REF-1** · BOUNDARY_ADJACENT · MODERATE · reference · REFERENTIAL_DEFICIENCY_FORM: "this gap / the aforementioned gap / this limitation (in prior research) / to fill this gap / addressing the lack of …" — nominal in argument position; reference-only; related BR-CROSS-13 (informational). Never itself an asserted deficiency.
- **SL-REF-2** · SYNTACTIC · MODERATE · reference · AMBIGUOUS_NOMINAL_FORM: "the limited evidence on X / the absence of research on X" — may be assertive or referential depending on syntax/context; flag `completion_required`; Step 7 marks, never resolves.

## 40.17 Positioning/discourse-link signals (family POSITIONING; DISCOURSE type)

Supporting signals only — **never sufficient to create a deficiency; objective/RQ/purpose wording cannot manufacture a gap** ("We investigate X." alone → no deficiency signal; "Little is known about X. We therefore investigate X." → deficiency signal + positioning link).

- **SL-POS-1** · DISCOURSE · WEAK · context · present-study action: "this study addresses / we [address|examine|investigate|test|develop] / the present study focuses on / our research responds to / we seek to understand / accordingly, we ask".
- **SL-POS-2** · DISCOURSE · MODERATE · context · explicit response-to-deficiency link: "to address this [gap|limitation in prior research]" / "motivated by this [gap|limitation]" / "in response to this [gap|limitation in prior research]" / active form "this [gap|limitation in prior research] motivates [our|the present] study" (incl. the same construction with "the gap motivates the present study") — anaphoric; `coreference_dependent` · **hard rule:** SL-POS-2 = explicit present-study response to a **referenced deficiency**; the anaphoric target must be a deficiency/gap-like proposition. Generic study motivation never qualifies: "This phenomenon motivates our study." → NOT SL-POS-2.
- **SL-POS-3** · DISCOURSE · WEAK · context · consequence markers joining deficiency and study: "therefore / accordingly / thus / consequently + we …" · `cross_sentence_context_possible`.
- **SL-POS-4** · COREFERENCE_CONTEXT · WEAK · context · proposition-alignment cues for later G5 work: repeated relationship proposition; same directional relationship/mechanism/question; explicit anaphors "this question / this issue / this gap / this limitation in prior research". **G5 is not implemented; no proposition equivalence, no similarity thresholds — Steps 9/10+ own operational use.**

## 40.18 Boundary-adjacent signal families (overview)

Adjacent rhetorical classes must remain detectable so Step 5 can classify them: PRESENT_STUDY_DEFICIENCY (§40.19) · FUTURE_RESEARCH_MODAL (§40.20) · CONTRIBUTION_YIELD (§40.21) · MATTERING_STAKES (§40.22) · WORLD_OR_PRACTITIONER_DEFICIT (§40.23) · REFERENCE_ONLY (§40.16). These are not noise: they help later detection distinguish likely GAP candidates from adjacent deficiency-like constructions. None assigns a Step-5 class.

## 40.19 Own-limitation anti-signals (anti_signal_family PRESENT_STUDY_DEFICIENCY)

- **SL-OWNLIM-1** · ANTI_SIGNAL · STRONG · anti · "our/this study is limited (by) / a limitation of [this study|our analysis|our design]".
- **SL-OWNLIM-2** · ANTI_SIGNAL · STRONG · anti · "we were unable to / we could not / our [design|sample|data] [cannot|does not|do not] …".

These indicate deficiency target = present study; Step 7 never outputs OWN_LIMITATION. **Anti-signal ≠ automatic candidate exclusion:** "This study is limited because few prior studies have examined X." contains an own-study limitation signal AND a prior-knowledge deficiency signal (SL-LIM-2); both propositions must remain preservable (§40.29 INT-4). **Anti-signal semantics (frozen):** an anti-signal (i) decreases the likelihood that deficiency wording represents a present-study prior-knowledge GAP, or (ii) marks a nearby Step-5 class, or (iii) indicates a common false-positive environment. An anti-signal never deletes text, never vetoes candidate creation, never decides a class, and never overrides a strong deficiency predicate — anti-signals cannot operate as hard global exclusion rules.

## 40.20 Future-research signals (family FUTURE_RESEARCH_MODAL; BOUNDARY_ADJACENT)

- **SL-FUT-1** · BOUNDARY_ADJACENT · STRONG · boundary · "future [research|studies|work] [should|could|might] …".
- **SL-FUT-2** · BOUNDARY_ADJACENT · STRONG · boundary · "(further) research is needed to … / we [call for|encourage] (future) research on …" — need-wording may co-occur with a genuine deficiency; deficiency signals are never suppressed by future-research co-occurrence.
- **SL-FUT-3** · BOUNDARY_ADJACENT · MODERATE · boundary · "remains for future [research|studies] / an avenue for future research / it would be useful to examine / future inquiry should".

Step 5 permits FUTURE_RESEARCH with or without a deficiency predicate; Step 7 captures prospective-assignment wording without assuming any class.

## 40.21 Contribution signals (family CONTRIBUTION_YIELD; BOUNDARY_ADJACENT)

- **SL-CONTRIB-1** · BOUNDARY_ADJACENT · STRONG · boundary · "we contribute (by) / this [study|research] contributes / our contribution is / this research adds".
- **SL-CONTRIB-2** · BOUNDARY_ADJACENT · MODERATE · boundary · "we [extend|develop|introduce|provide|offer|advance|demonstrate|show] / our findings show".

- **SL-CONTRIB-3** · PREDICATE_PATTERN · MODERATE · boundary · gap-directed contribution-response verbs over a deficiency nominal: "[fill|close|address|bridge] [this|the|that] [gap|lack|limitation|void]" (incl. participial "addressing this gap / the lack of …") · required context: deficiency **nominal** as object (referential form); the verb responds to, and never evidences, a deficiency · nearest confusions: SL-POS-2 — "to address this gap, we examine …" **co-fires** SL-POS-2 when the construction introduces the present-study response; SL-CONTRIB-3 marks the gap-response construction itself · related: BR-CROSS-13.

Contribution wording alone is never a gap signal; "fill/close/address this gap" is never evidence that a gap exists. Interaction note (INT-3): gap-reference nominal + fill/close/address/bridge contribution-response verb (SL-CONTRIB-3) → boundary/reference/contribution context, not an independent deficiency assertion ("We fill this gap by developing …").

## 40.22 Motivation/mattering signals (family MATTERING_STAKES; BOUNDARY_ADJACENT)

- **SL-MOT-1** · BOUNDARY_ADJACENT · WEAK · boundary · "[important|critical|pressing|significant|consequential] (for)".
- **SL-MOT-2** · BOUNDARY_ADJACENT · WEAK · boundary · "has major implications / is increasingly important / policy concern / managerial concern / matters because".
- **SL-MOT-3** · BOUNDARY_ADJACENT · WEAK · boundary · problem/stakes wording: "poses a challenge / creates difficulties / is costly / is widespread / affects many firms".

All three MOT entries carry tier WEAK: mattering wording has minimal deficiency-directness by definition, and importance language never elevates candidacy (INT-10) — the v1.0 tier ranges resolve downward accordingly. Not deficiency signals unless a knowledge deficiency is separately asserted: "SMEs account for most employment." → neutral world-state, **no signal at all**; "Understanding SME resilience is important." → motivation only; "Little is known about SME resilience." → deficiency signal (SL-LIM-1). Importance language never boosts a passage into GAP by itself (INT-10).

## 40.23 Practitioner/world-deficit anti-signals (anti_signal_family WORLD_OR_PRACTITIONER_DEFICIT)

- **SL-WORLD-1** · ANTI_SIGNAL · STRONG · anti · "[managers|firms|practitioners|employees|organizations|companies] [do not understand|lack|fail to|struggle to|are unable to|cannot] …" · subject-class constraint is the discriminator. Hard false-friend pair: "Managers do not understand X." → anti-signal ‖ "Researchers do not understand X." → potential prior-knowledge deficiency signal (SL-ABS-6) ‖ "Research knowledge has not translated to managers." → research-practice signal (SL-DISC-D1).
- **SL-WORLD-2** · ANTI_SIGNAL · MODERATE · anti · "implementation remains low / adoption is poor / capability is lacking".

The target matters: manager knowledge ≠ research knowledge. World-deficit wording may still be MOTIVATION- or OTHER-relevant later (§40.35); it never vetoes co-present deficiency signals (anti-signal semantics, §40.19).

## 40.24 Negation/polarity handling

Signal matching must be polarity-aware; the library specifies `negation_scope_sensitive = true` on all predicate-pattern signals whose semantics invert under negation. Frozen non-firing cases: "not limited" must not trigger SL-LIM-3 · "not inconsistent" must not trigger SL-CONF-2 · "no longer unexplored" must not trigger SL-ABS-5 as a current positive signal — explicit temporal cancellation fires SL-TEMP-1 (§40.26a) with negation context instead · "cannot be said to be limited" requires caution (`requires_negation_scope_analysis`). Step 7 defines the metadata requirement only; the parser/matcher is Step-10 property.

## 40.25 Attribution and reported-claim handling

Deficiency wording inside quotation, reported speech, citation paraphrase, or descriptions of another author's claim remains detectable, with attribution marked as context:

- **SL-ATTR-1** · COREFERENCE_CONTEXT · NOT_APPLICABLE · context · ATTRIBUTED_DEFICIENCY: "[Smith] [argues|claims|notes|suggests] that [deficiency wording]" — the deficiency-like signal is present; whether the manuscript adopts it is later semantic work.
- **SL-ATTR-2** · COREFERENCE_CONTEXT · NOT_APPLICABLE · context · REJECTED_DEFICIENCY: "Contrary to [Smith's] claim that [deficiency wording], … [extensive evidence exists]" — the quoted deficiency signal must not dominate; rejection context recorded.

Neither resolves into GAP; neither deletes the underlying signal. **Frozen (v1.1): local deficiency predication ≠ manuscript adoption** — positive family signals remain detectable inside reported speech, quotation, attributed claims, rejected claims, and concessive/contrast constructions whenever the local clause satisfies the family's conditions; adoption/endorsement is Step-5 work.

## 40.26 Contrast/reversal signals (family CONTRAST_REVERSAL; DISCOURSE)

- **SL-REVERSAL-1** · DISCOURSE · NOT_APPLICABLE · context · "however / but / although / despite / contrary to / rather than / yet / nevertheless" — may reverse the interpretation of nearby deficiency language ("Although prior authors argue that evidence is limited, recent studies provide extensive evidence."): the phrase "evidence is limited" remains detectable; the reversal must be visible to Steps 10/11. Signals are never deleted by reversal context. `cross_sentence_context_possible`. **Logical contrast/reversal (this family) and temporal resolution (§40.26a) are semantically distinct and never conflated; one sentence may carry both ("Although evidence was once limited, recent studies are extensive." → SL-REVERSAL-1 + SL-TEMP-1).**

## 40.26a Temporal-resolution signals (family TEMPORAL_RESOLUTION)

- **SL-TEMP-1** · DISCOURSE · NOT_APPLICABLE · context · marks that deficiency wording is explicitly located in a **closed or superseded past state** rather than asserted as current · surface patterns (only when the temporal construction modifies the deficiency state): "previously …", "formerly …", "was once …", "until recently", "no longer …", "historically …", "once considered …" · `negation_scope_sensitive` interplay for cancellation forms.

**Deterministic rule (frozen).** (A) *Historical/reported deficiency*: when a deficiency is genuinely predicated of a past state, the semantic family signal remains visible **and** SL-TEMP-1 fires — "X was poorly understood until recently." → SL-LIM-5 + SL-TEMP-1; whether the deficiency persists is later semantic work. (B) *Explicit cancellation*: constructions that cancel the current deficiency must NOT fire the positive current-deficiency signal — "X is no longer unexplored." → SL-TEMP-1 (+ negation context), NOT SL-ABS-5; the lexical cue may be recognized at matching level, but temporal/negation metadata prevents positive-signal status. (C) *Own-study resolution*: "We explored the previously unexplored region." → SL-TEMP-1 with RESOLVED_BY_PRESENT_STUDY context, NOT SL-ABS-5 (FF-42). Signal visibility for a historical/reported deficiency (A) is thereby precisely distinguished from positive current-deficiency firing, which (B) and (C) block.

## 40.27 Coreference-dependent signals (family COREFERENCE_DEPENDENT)

- **SL-COREF-1** · COREFERENCE_CONTEXT · NOT_APPLICABLE · context · anaphoric knowledge nominals: "this [issue|question|relationship|limitation|gap|disconnect] / these [mechanisms|findings] / such [evidence|research]" — not deficiency signals by themselves; a local deficiency predicate must supply the head ("These mechanisms remain unexplored." → SL-ABS-5 + SL-COREF-1; "These mechanisms are central to our model." → no deficiency signal). Step 7 marks that resolution may be required (`coreference_dependent = true`); it never performs resolution.

## 40.28 Section priors

Categorical priors only — **ELEVATED / NEUTRAL / REDUCED / BOUNDARY_SPECIAL**; no probabilities, no multipliers. Section location is NEVER sufficient to classify GAP; a prior modifies candidate-detection interpretation and never overrides proposition semantics. **UNKNOWN_SECTION → NEUTRAL**; uncertain section classification never suppresses detection; no new section classifier is invented. The full table is §40.38.

## 40.29 Signal interactions (family SIGNAL_INTERACTION; static, non-scoring)

Effects vocabulary: STRENGTHENS · WEAKENS · BOUNDARY_ADJACENT · REQUIRES_CONTEXT · CONFLICTING_CUES. No numeric scores; none of these is an emission rule.

| interaction_id | components | effect_on_signal_interpretation |
|---|---|---|
| INT-1 | deficiency head + prior-knowledge target | STRENGTHENS (stronger candidate evidence) |
| INT-2 | deficiency head + explicit positioning link (SL-POS-2/3) | STRENGTHENS |
| INT-3 | gap-reference nominal (SL-GAPLEX/SL-REF-1) + fill/close/address/bridge contribution-response verb (SL-CONTRIB-3; other SL-CONTRIB) | BOUNDARY_ADJACENT (referential/contribution construction; the verb never evidences the gap) |
| INT-4 | deficiency wording + own-study subject (SL-OWNLIM) | BOUNDARY_ADJACENT (own-limitation environment); co-present prior-knowledge signals preserved |
| INT-5 | deficiency wording + future-research modal (SL-FUT) | BOUNDARY_ADJACENT (future-research environment); deficiency signal not suppressed |
| INT-6 | world/practitioner subject + knowledge/capability verb | WEAKENS for GAP-candidacy (WORLD anti-environment) |
| INT-7 | deficiency signal + attribution frame (SL-ATTR-1) | REQUIRES_CONTEXT |
| INT-8 | deficiency signal + rejection/reversal (SL-ATTR-2 / SL-REVERSAL-1) | CONFLICTING_CUES (signal visible; interpretation contested) |
| INT-9 | coreference nominal (SL-COREF-1) + local deficiency head | REQUIRES_CONTEXT (completion needed) |
| INT-10 | mattering/stakes wording (SL-MOT) with no deficiency head | no elevation — explicitly inert for candidacy |
| INT-11 | hedge ("virtually", "almost") + categorical head (SL-ABS) | REQUIRES_CONTEXT (strength axis is later Step-6 work) |
| INT-12 | testing-absence (SL-TEST) + support wording (SL-SUP) co-present | REQUIRES_CONTEXT (two distinct cues; possible multi-deficiency separation later) |
| INT-13 | deficiency head + temporal-resolution marker (SL-TEMP-1) | REQUIRES_CONTEXT (current vs closed-past state; explicit cancellation blocks positive firing per §40.26a) |

## 40.30 False-friend registry (46 entries; each: surface · resembles → family · why insufficient). Registry entries are the semantic library; they are NOT executable tests — the executable false-friend tests are T-FF-01…T-FF-40 (§40.41).

FF-01 "the gap between revenues and costs" · gap → GAP_LEXEME · quantitative difference, no knowledge deficiency.
FF-02 "wage gap" · gap → GAP_LEXEME · social disparity phenomenon (may itself be a research topic, not a deficiency assertion).
FF-03 "gender gap" · gap → GAP_LEXEME · same as FF-02.
FF-04 "generation gap" · gap → GAP_LEXEME · cultural phenomenon.
FF-05 "air gap" · gap → GAP_LEXEME · technical artifact.
FF-06 "gap year" · gap → GAP_LEXEME · idiom; `token/collocation` guard.
FF-07 "gap analysis was performed" · gap → GAP_LEXEME · method name; procedural.
FF-08 "we use mixed methods" · mixed → CONFLICT · methodology descriptor, no incompatibility of prior knowledge.
FF-09 "a mixed sample of firms" · mixed → CONFLICT · sample composition.
FF-10 "limited liability" · limited → LIMITED_KNOWLEDGE · legal term.
FF-11 "limited company" · limited → LIMITED_KNOWLEDGE · legal form.
FF-12 "limited edition" · limited → LIMITED_KNOWLEDGE · product descriptor.
FF-13 "data were limited to the 2019 wave" (Methods) · limited → LIMITED_KNOWLEDGE · sample-scope statement about the present study.
FF-14 "no significant difference was found" · no → CATEGORICAL_ABSENCE · statistical result, not knowledge-state assertion.
FF-15 "no effect was observed" · no → CATEGORICAL_ABSENCE · result statement.
FF-16 "no evidence of misconduct was found" · no evidence → CATEGORICAL_ABSENCE · world-directed search result.
FF-17 "no missing data" · no/missing → CATEGORICAL_ABSENCE/GAP_LEXEME · data-quality statement.
FF-18 "the test was not applicable" · test → TESTING_ABSENCE · procedural applicability, not verification denial of an artifact.
FF-19 "test set" · test → TESTING_ABSENCE · ML data split.
FF-20 "validation dataset" · validat- → TESTING_ABSENCE · ML data split.
FF-21 "invalid input" · invalid → CHALLENGE/TESTING · technical error state.
FF-22 "subject to the budget constraint" · constrain → CAPABILITY_CONSTRAINT · optimization formalism.
FF-23 "model constraint" (technical) · constraint → CAPABILITY_CONSTRAINT · specification detail, not a knowledge-resource restriction.
FF-24 "practice session" · practice → RESEARCH_PRACTICE · rehearsal sense.
FF-25 "in clinical practice, dosing varies" (no research linkage asserted) · practice → RESEARCH_PRACTICE · world description; no research↔practice relation predicated.
FF-26 "a challenging environment" · challeng- → CHALLENGE · difficulty sense.
FF-27 "this is a challenging problem" · challeng- → CHALLENGE · task difficulty.
FF-28 "unexplored parameter space in the search algorithm" · unexplored → CATEGORICAL_ABSENCE · algorithmic search domain, not prior knowledge.
FF-29 "scarce resources in the empirical setting" · scarce → LIMITED_KNOWLEDGE · world-state scarcity.
FF-30 "firms lack resources" · lack → GAP_LEXEME · world/practitioner deficit (→ SL-WORLD-1).
FF-31 "managers lack expertise" · lack → GAP_LEXEME · practitioner deficit.
FF-32 "participants lack information" · lack → GAP_LEXEME · subject-population state.
FF-33 "the effect was not significant" (Results) · not → CATEGORICAL_ABSENCE · statistical result.
FF-34 "no additional analyses were conducted" · no → CATEGORICAL_ABSENCE · own-study procedure.
FF-35 "no participants reported X" · no → CATEGORICAL_ABSENCE · empirical observation about the sample.
FF-36 "little time was available" · little → LIMITED_KNOWLEDGE · resource statement.
FF-37 "consensus was not required" · consensus → CONFLICT · procedural rule.
FF-38 "our camera cannot capture low light" · cannot capture → CAPABILITY_CONSTRAINT · physical instrument, not a knowledge resource.
FF-39 "managers cannot explain X" · cannot explain → CAPABILITY_CONSTRAINT · practitioner capability (→ SL-WORLD-1).
FF-40 "the participant made a mistake" · mistake → CHALLENGE · behavioral event, no prior position challenged.
FF-41 "conflicting priorities among managers" · conflicting → CONFLICT · world-state disagreement, not prior-knowledge incompatibility.
FF-42 "we explored the previously unexplored region" · unexplored → CATEGORICAL_ABSENCE · attributive absence resolved by the present study; fires SL-TEMP-1 (own-study resolution) only — never SL-ABS-5 as a current positive signal.
FF-43 "no model was fitted in specification 3" · no model → CATEGORICAL_ABSENCE (SL-ABS-8) · present-study estimation procedure, not a prior-knowledge resource absence.
FF-44 "No method was used in the robustness analysis." · no method → CATEGORICAL_ABSENCE (SL-ABS-9) · present-study procedure description.
FF-45 "No instrument was available in the room." · no instrument → CATEGORICAL_ABSENCE (SL-ABS-9) · world/instrument availability, not a methodological knowledge resource.
FF-46 "The results do not support H1." · does not support → EVIDENTIAL_SUPPORT (SL-SUP-4) · the manuscript's own result-reporting statement, not a prior-knowledge support deficiency.

## 40.31 Morphological/orthographic variants (controlled; no unrestricted stemming)

underexplored / under-explored / under explored · understudied / under-studied / under studied · well-understood / well understood · research-practice / research–practice / research practice · evidence-based / evidence based. `hyphen_variant_allowed` marks entries where these apply. The text-normalization engine is not designed here.

## 40.32 Phrase-boundary/tokenization safety

Static metadata only (`token_boundary_required`, `case_sensitive` where needed, `hyphen_variant_allowed`): "gap" must not match arbitrary substrings · "limited" must distinguish adjectival ("limited evidence") from passive-verbal ("is limited by") constructions where needed · "test" must not match "latest" · "valid" must not match "invalid"/"validated". The runtime regex engine is Step-10 property.

## 40.33 Multi-sentence/context signals

`cross_sentence_context_possible = true` for: consequence-linked deficiency→study patterns ("Evidence remains mixed. We therefore examine whether X affects Y."), focus-then-residue patterns ("Prior studies focus on X. Consequently, Y remains poorly understood."), reversal spans (§40.26), and coreference chains (§40.27). **No window size, sentence count, token radius, or paragraph radius is defined — Step-10 property.**

## 40.34 Citation co-occurrence

Citation presence is neither necessary nor sufficient for anything: "Few studies examine X (Smith, 2020)." → the deficiency signal exists independently of the citation; "Smith (2020) examines X." → a citation alone is no deficiency signal. Where represented at all, citation co-occurrence is a **WEAK CONTEXT SIGNAL** (`SL-CITE-1`: strength_tier WEAK, polarity context — tier retained per the v1.1 preservation list), never required. No citation-reference resolution here; the Citation Registry remains separate.

## 40.35 Step-5 boundary crosswalk (informational only — Step 7 never assigns a Step-5 class)

PRESENT_STUDY_DEFICIENCY (SL-OWNLIM) → often relevant to OWN_LIMITATION · FUTURE_RESEARCH_MODAL (SL-FUT) → often FUTURE_RESEARCH · CONTRIBUTION_YIELD (SL-CONTRIB, incl. SL-CONTRIB-3 gap-response constructions) → often CONTRIBUTION · MATTERING_STAKES (SL-MOT) → often MOTIVATION · WORLD_OR_PRACTITIONER_DEFICIT (SL-WORLD) → often MOTIVATION / OTHER · REFERENCE_ONLY (SL-REF-1) → often OTHER / contribution-reference constructions · ASSERTIVE deficiency families (SL-ABS/LIM/CONF/TEST/SUP/CSTR/DISC/CHAL) → candidates for GAP evaluation under BR G1–G7. **Crosswalk = later classification hint only.**

## 40.36 Step-6 crosswalk (informational only — Step 7 never assigns relation or kind)

CATEGORICAL_ABSENCE (incl. SL-ABS-8/9 resource-absence forms) → may support DP-REL-1 · LIMITED_KNOWLEDGE → DP-REL-2 · CONFLICT_INCONSISTENCY → DP-REL-3 · TESTING_ABSENCE → DP-REL-4 · EVIDENTIAL_SUPPORT (incl. SL-SUP-4) → DP-REL-1/2/3 per support head · TEMPORAL_RESOLUTION (SL-TEMP-1) → context only, no relation mapping · CAPABILITY_CONSTRAINT → DP-REL-5 · RESEARCH_PRACTICE subfamilies → DP-REL-1×pa (A), DP-REL-2×pa (B), DP-REL-5×pa (C), DP-REL-6 (D) · CHALLENGE_INVALIDITY → DP-REL-7. Intentionally ambiguous mappings preserved unresolved: "fails to [verb]" → possible DP-REL-5 / DP-REL-7 (OD-DPR-2) · "lack" → multiple relations/kinds · "remains contested" → DP-REL-3/DP-REL-3a question. **Crosswalk ≠ relation assignment; ambiguity is not resolved here.**

## 40.36a Step-6 detection-coverage audit (informational; detection visibility only — no relation or knowledge_kind is assigned; one-to-many mapping allowed)

| DPR example family | Representative frozen wording | Step-7 signal(s) | Coverage |
|---|---|---|---|
| ABSENT + evidence (support-predicate form) | "No empirical evidence supports assumption X." | SL-SUP-4 | PASS |
| ABSENT + evidence (existential form) | "No evidence exists on X." | SL-ABS-2 | PASS |
| ABSENT + evidence (attention form) | "X has received no attention." | SL-ABS-7 | PASS |
| ABSENT + theory | "No theoretical account of X exists." | SL-ABS-3; SL-ABS-8 | PASS |
| ABSENT + theory (model form) | "No model explains X." | SL-ABS-8 | PASS |
| ABSENT + method | "No validated method exists to measure X." | SL-ABS-9 | PASS |
| ABSENT + practice_alignment | "No mechanism exists for translating research findings into practice." | SL-DISC-A1 | PASS |
| ABSENT + unspecified | "We do not understand why X persists." | SL-ABS-6 | PASS |
| LIMITED variants | "Little is known about X."; "Few studies have examined X."; "limited theoretical understanding of X" | SL-LIM-1 / SL-LIM-2 / SL-LIM-7 | PASS |
| LIMITED + practice_alignment | "Translation of research into practice remains limited." | SL-DISC-B1 | PASS |
| CONFLICTING variants | "Prior findings are mixed."; "X remains contested."; "No consensus exists on X." | SL-CONF-1 / SL-CONF-5 / SL-CONF-4 | PASS |
| UNTESTED | "The model remains untested."; "The framework has yet to be evaluated." | SL-TEST-1 / SL-TEST-3 | PASS |
| CONSTRAINED | "Existing theories cannot explain X."; "Prior work is limited by cross-sectional designs." | SL-CSTR-1 / SL-CSTR-3 | PASS |
| CONSTRAINED + practice_alignment | "Institutional barriers constrain the translation of research into practice." | SL-DISC-C1 | PASS |
| DISCONNECTED | "Research and practice remain poorly aligned."; "Research has not translated into practice." | SL-DISC-D2 / SL-DISC-D1 | PASS |
| CHALLENGED | "This assumption is mistaken."; "Prior findings are artifacts of measurement error." | SL-CHAL-1 / SL-CHAL-4 | PASS |
| CHALLENGED/CONSTRAINED residue | "Existing models fail to capture X." | SL-CSTR-6 + SL-CHAL-5 (ambiguous_semantics by design; OD-DPR-2) | PASS |

No unexplained coverage gaps: every frozen A1E-DPR-1.1 positive-example family above has at least one detection-visible Step-7 signal.

## 40.37 Machine-referenceable signal registry (index; family cards §40.7–40.27 remain normative)

| signal_id | family | type | tier | polarity | canonical_description / surface pattern | required_context | key exclusions | rel. Step-5 | rel. Step-6 |
|---|---|---|---|---|---|---|---|---|---|
| SL-ABS-1 | CATEGORICAL_ABSENCE | PREDICATE_PATTERN | STRONG | positive | no studies/research have examined … | knowledge-activity target | own-study procedure; participant reports | G1–G3 | DP-REL-1 |
| SL-ABS-2 | CATEGORICAL_ABSENCE | PHRASE | STRONG | positive | no evidence exists/available on … | knowledge item | search results; statistics | G1–G3 | DP-REL-1 |
| SL-ABS-3 | CATEGORICAL_ABSENCE | PHRASE | STRONG | positive | there is no account/theory/data on … | knowledge item | — | G1–G3 | DP-REL-1 |
| SL-ABS-4 | CATEGORICAL_ABSENCE | PREDICATE_PATTERN | STRONG | positive | has never been studied/examined | knowledge activity | negated-negation | G1–G3 | DP-REL-1 |
| SL-ABS-5 | CATEGORICAL_ABSENCE | PREDICATE_PATTERN | STRONG | positive | remains unexplored/unanswered/unknown/open question | knowledge target | attributive own-exploration; parameter-space | G1–G3 | DP-REL-1 |
| SL-ABS-6 | CATEGORICAL_ABSENCE | PREDICATE_PATTERN | STRONG | positive | nothing is known / we-researchers do not understand | research-community subject | practitioner subject → SL-WORLD-1 | G1–G3; BR-CROSS-14 | DP-REL-1 |
| SL-ABS-7 | CATEGORICAL_ABSENCE | PHRASE | STRONG | positive | has received no attention (hedge-flagged variants) | knowledge attention | — | G1–G3 | DP-REL-1; DP-PREC-1 |
| SL-ABS-8 | CATEGORICAL_ABSENCE | PREDICATE_PATTERN | STRONG | positive | no model/framework/theory/account exists or explains … | theoretical knowledge resource as absent item | fitted-model procedure (FF-43) | G1–G3 | DP-REL-1 |
| SL-ABS-9 | CATEGORICAL_ABSENCE | PREDICATE_PATTERN | STRONG | positive | no (validated) method/measure/instrument/procedure exists for … | research-generating methodological resource | present-study procedure (FF-44); world availability (FF-45) | G1–G3 | DP-REL-1 |
| SL-LIM-1 | LIMITED_KNOWLEDGE | PHRASE | STRONG | positive | little is known about … | — | — | G1–G3 | DP-REL-2 |
| SL-LIM-2 | LIMITED_KNOWLEDGE | PHRASE | STRONG | positive | few studies have examined … | — | — | G1–G3 | DP-REL-2 |
| SL-LIM-3 | LIMITED_KNOWLEDGE | PHRASE | STRONG | positive | limited/scarce/scant/sparse evidence-research-attention | adjectival construction | "limited by" → SL-CSTR-3; legal/product senses | G1–G3 | DP-REL-2 |
| SL-LIM-4 | LIMITED_KNOWLEDGE | LEXICAL | STRONG | positive | underexplored/understudied/rarely examined (variants) | — | "unexplored" → SL-ABS-5 | G1–G3 | DP-REL-2 |
| SL-LIM-5 | LIMITED_KNOWLEDGE | PHRASE | STRONG | positive | poorly / not well understood; incomplete understanding | — | — | G1–G3 | DP-REL-2 |
| SL-LIM-6 | LIMITED_KNOWLEDGE | PHRASE | MODERATE | positive | thin literature; underdeveloped research | — | — | G1–G3 | DP-REL-2 |
| SL-LIM-7 | LIMITED_KNOWLEDGE | PHRASE | STRONG | positive | limited theoretical/empirical understanding | — | — | G1–G3 | DP-REL-2 (kind surface preserved) |
| SL-CONF-1 | CONFLICT_INCONSISTENCY | PHRASE | STRONG | positive | mixed findings/evidence/results | prior-knowledge target | mixed methods/sample | G1–G3 | DP-REL-3 |
| SL-CONF-2 | CONFLICT_INCONSISTENCY | PHRASE | STRONG | positive | inconsistent/contradictory/conflicting findings | prior-knowledge target | world-state conflict | G1–G3 | DP-REL-3 |
| SL-CONF-3 | CONFLICT_INCONSISTENCY | PREDICATE_PATTERN | STRONG | positive | studies/scholars disagree | prior positions | — | G1–G3 | DP-REL-3 |
| SL-CONF-4 | CONFLICT_INCONSISTENCY | PHRASE | STRONG | positive | no consensus on … | prior positions | procedural consensus | G1–G3 | DP-REL-3 |
| SL-CONF-5 | CONFLICT_INCONSISTENCY | PHRASE | MODERATE | positive | debate persists; remains contested | contester unresolved | — | G1–G3 | DP-REL-3/3a |
| SL-CONF-6 | CONFLICT_INCONSISTENCY | PHRASE | STRONG | positive | competing explanations remain unresolved | prior positions | — | G1–G3 | DP-REL-3 |
| SL-TEST-1 | TESTING_ABSENCE | PREDICATE_PATTERN | STRONG | positive | (remains) untested; has not/never been tested | artifact subject | test-set/applicability senses | G1–G3 | DP-REL-4 |
| SL-TEST-2 | TESTING_ABSENCE | PREDICATE_PATTERN | STRONG | positive | not validated; unvalidated; awaits empirical validation | artifact subject | validation-dataset sense | G1–G3 | DP-REL-4 |
| SL-TEST-3 | TESTING_ABSENCE | PREDICATE_PATTERN | STRONG | positive | not verified/evaluated; awaits empirical scrutiny | artifact subject | — | G1–G3 | DP-REL-4 |
| SL-SUP-1 | EVIDENTIAL_SUPPORT | PREDICATE_PATTERN | STRONG | positive | lacks (empirical) support; unsupported; no support | claim/artifact target | testing-denial → SL-TEST | G1–G3 | DP-REL-1 (support head) |
| SL-SUP-2 | EVIDENTIAL_SUPPORT | PHRASE | MODERATE | positive | little/weak/limited/insufficient support | claim target | — | G1–G3 | DP-REL-2 (support head) |
| SL-SUP-3 | EVIDENTIAL_SUPPORT | PHRASE | STRONG | positive | support is mixed | claim target | — | G1–G3 | DP-REL-3 (support head) |
| SL-SUP-4 | EVIDENTIAL_SUPPORT | PREDICATE_PATTERN | STRONG | positive | no (empirical) evidence supports …; evidence does not support … | prior/current knowledge-support target | own result-reporting (FF-46); testing-denial → SL-TEST | G1–G3 | DP-REL-1 (support head) |
| SL-CSTR-1 | CAPABILITY_CONSTRAINT | PREDICATE_PATTERN | STRONG | positive | cannot explain/account for/capture/… | knowledge-resource subject | instrument/practitioner subjects | G1–G3 | DP-REL-5 |
| SL-CSTR-2 | CAPABILITY_CONSTRAINT | PREDICATE_PATTERN | STRONG | positive | unable to; ill-equipped to; not designed to | knowledge-resource subject | — | G1–G3 | DP-REL-5 |
| SL-CSTR-3 | CAPABILITY_CONSTRAINT | PREDICATE_PATTERN | STRONG | positive | limited/constrained/restricted by … | resource + restrictor | "limited evidence" → SL-LIM-3 | G1–G3 | DP-REL-5 |
| SL-CSTR-4 | CAPABILITY_CONSTRAINT | SYNTACTIC | MODERATE | positive | relies on X, leaving Y unexamined | resource subject | — | G1–G3 | DP-REL-5 |
| SL-CSTR-5 | CAPABILITY_CONSTRAINT | PHRASE | MODERATE | positive | only partial insight; coarse estimates; cannot separate | resource subject | — | G1–G3 | DP-REL-5 |
| SL-CSTR-6 | CAPABILITY_CONSTRAINT | PREDICATE_PATTERN | STRONG | positive | fails to explain/capture/account for | resource subject | never pre-classified; `ambiguous_semantics = true` (metadata) | G1–G3 | DP-REL-5/7 unresolved (OD-DPR-2) |
| SL-DISC-A1 | RESEARCH_PRACTICE (absent bridge) | PHRASE | STRONG | positive | no mechanism/pathway exists for translating research into practice | both poles named | machine-mechanism sense | G1–G3; BR-GAP-12 | DP-REL-1×pa (DP-KIND-4a) |
| SL-DISC-B1 | RESEARCH_PRACTICE (limited process) | PHRASE | STRONG | positive | translation/integration of research into practice remains limited/underdeveloped | both poles | — | G1–G3 | DP-REL-2×pa (DP-PREC-11) |
| SL-DISC-C1 | RESEARCH_PRACTICE (constrained bridge) | PREDICATE_PATTERN | STRONG | positive | barriers constrain research-to-practice translation | both poles + constrainer head | reason-only barriers | G1–G3 | DP-REL-5×pa (DP-PREC-12) |
| SL-DISC-D1 | RESEARCH_PRACTICE (disrelation) | PREDICATE_PATTERN | STRONG | positive | has not translated into practice; not reached practitioners | both poles | — | G1–G3 | DP-REL-6 |
| SL-DISC-D2 | RESEARCH_PRACTICE (disrelation) | PHRASE | STRONG | positive | research and practice disconnected/poorly aligned/drifted apart | both poles | research-and-theory | G1–G3 | DP-REL-6 |
| SL-CHAL-1 | CHALLENGE_INVALIDITY | PREDICATE_PATTERN | STRONG | positive | prior view is wrong/mistaken/flawed/invalid | prior-position target; authorial | behavioral "mistake"; technical "invalid" | G1–G3 | DP-REL-7 |
| SL-CHAL-2 | CHALLENGE_INVALIDITY | PREDICATE_PATTERN | STRONG | positive | does not hold; breaks down; flawed premise | prior-position target | — | G1–G3 | DP-REL-7 |
| SL-CHAL-3 | CHALLENGE_INVALIDITY | PHRASE | STRONG | positive | we challenge/contest/dispute … | authorial subject | difficulty senses | G1–G3 | DP-REL-7 |
| SL-CHAL-4 | CHALLENGE_INVALIDITY | PHRASE | STRONG | positive | artifacts of …; systematically misstates | prior findings/method target | — | G1–G3 | DP-REL-7 |
| SL-CHAL-5 | CHALLENGE_INVALIDITY | PREDICATE_PATTERN | STRONG | positive | fails; does not account for | prior-position/resource target | never pre-classified; `ambiguous_semantics = true` (metadata) | G1–G3 | DP-REL-5/7 unresolved |
| SL-GAPLEX-1 | GAP_LEXEME | PHRASE | MODERATE | positive | (there is) a gap in knowledge/literature about … | assertive-existential frame | domain gaps | G1–G3 | multiple |
| SL-GAPLEX-2 | GAP_LEXEME | LEXICAL | WEAK | positive | bare "gap(s)" | token boundary | FF-01…07 | — | multiple |
| SL-GAPLEX-3 | GAP_LEXEME | PHRASE | MODERATE | positive | lack of evidence/research; lacks; lacking | knowledge object | world-deficit lacks | G1–G3 | multiple |
| SL-GAPLEX-4 | GAP_LEXEME | LEXICAL | MODERATE | positive | absence of research; missing/neglected/overlooked/unresolved | assertive use | nominal-only use | G1–G3 | multiple |
| SL-REF-1 | ASSERTION_REFERENCE | BOUNDARY_ADJACENT | MODERATE | reference | this/the aforementioned gap; to fill this gap; addressing the lack of … | nominal-argument position | — | BR-CROSS-13; CONTRIBUTION | — |
| SL-REF-2 | ASSERTION_REFERENCE | SYNTACTIC | MODERATE | reference | the limited evidence on X; the absence of research on X | completion_required | — | BR-CROSS-13 | — |
| SL-POS-1 | POSITIONING | DISCOURSE | WEAK | context | we address/examine/investigate; the present study focuses on | present-study subject | never deficiency-creating | G5 | — |
| SL-POS-2 | POSITIONING | DISCOURSE | MODERATE | context | to address this gap/limitation; motivated by this gap/limitation; this gap/limitation motivates our/the present study; in response to this gap | anaphoric antecedent = deficiency/gap-like proposition | generic motivation ("this phenomenon motivates our study") never fires | G5(A) | — |
| SL-POS-3 | POSITIONING | DISCOURSE | WEAK | context | therefore/accordingly/thus + we … | consequence link | — | G5(A) | — |
| SL-POS-4 | POSITIONING | COREFERENCE_CONTEXT | WEAK | context | proposition-alignment cues; this question/issue anaphors | — | no G5 implementation | G5(B) | — |
| SL-OWNLIM-1 | PRESENT_STUDY_DEFICIENCY | ANTI_SIGNAL | STRONG | anti | our/this study is limited (by); a limitation of this study | own-study subject | never a veto | OWN_LIMITATION | — |
| SL-OWNLIM-2 | PRESENT_STUDY_DEFICIENCY | ANTI_SIGNAL | STRONG | anti | we were unable to; our data do not; our design cannot | own-study subject | never a veto | OWN_LIMITATION | — |
| SL-FUT-1 | FUTURE_RESEARCH_MODAL | BOUNDARY_ADJACENT | STRONG | boundary | future research/studies should/could | prospective assignment | no suppression of deficiency cues | FUTURE_RESEARCH (BR-FUT) | — |
| SL-FUT-2 | FUTURE_RESEARCH_MODAL | BOUNDARY_ADJACENT | STRONG | boundary | (further) research is needed to; we call for research on | prospective | — | FUTURE_RESEARCH | — |
| SL-FUT-3 | FUTURE_RESEARCH_MODAL | BOUNDARY_ADJACENT | MODERATE | boundary | remains for future research; avenue for future research | prospective | — | FUTURE_RESEARCH | — |
| SL-CONTRIB-1 | CONTRIBUTION_YIELD | BOUNDARY_ADJACENT | STRONG | boundary | we contribute; our contribution is; this research adds | present-study yield | never gap-creating | CONTRIBUTION | — |
| SL-CONTRIB-2 | CONTRIBUTION_YIELD | BOUNDARY_ADJACENT | MODERATE | boundary | we extend/develop/introduce/provide/demonstrate | present-study yield | — | CONTRIBUTION | — |
| SL-CONTRIB-3 | CONTRIBUTION_YIELD | PREDICATE_PATTERN | MODERATE | boundary | fill/close/address/bridge this gap/lack/limitation | deficiency nominal as object (referential) | never evidences a gap; co-fires SL-POS-2 when introducing study response | CONTRIBUTION; BR-CROSS-13 | — |
| SL-MOT-1 | MATTERING_STAKES | BOUNDARY_ADJACENT | WEAK | boundary | important/critical/pressing/significant | — | never gap-creating | MOTIVATION (BR-MOT-3) | — |
| SL-MOT-2 | MATTERING_STAKES | BOUNDARY_ADJACENT | WEAK | boundary | major implications; policy/managerial concern | — | — | MOTIVATION | — |
| SL-MOT-3 | MATTERING_STAKES | BOUNDARY_ADJACENT | WEAK | boundary | poses a challenge; is costly; is widespread | problem-framing | neutral prevalence = no signal | MOTIVATION/OTHER | — |
| SL-WORLD-1 | WORLD_OR_PRACTITIONER_DEFICIT | ANTI_SIGNAL | STRONG | anti | managers/firms/practitioners do not understand/lack/fail to/cannot | practitioner/world subject | researcher subject → SL-ABS-6 | BR-CROSS-14; MOTIVATION/OTHER | — |
| SL-WORLD-2 | WORLD_OR_PRACTITIONER_DEFICIT | ANTI_SIGNAL | MODERATE | anti | implementation remains low; adoption is poor | world state | — | MOTIVATION/OTHER | — |
| SL-COREF-1 | COREFERENCE_DEPENDENT | COREFERENCE_CONTEXT | NOT_APPLICABLE | context | this issue/question/gap; these mechanisms; such evidence | local predicate supplies head | no resolution performed | BR grounding (T2b adjacency) | DP-CROSS-4 |
| SL-ATTR-1 | ATTRIBUTION | COREFERENCE_CONTEXT | NOT_APPLICABLE | context | ATTRIBUTED_DEFICIENCY: X argues that [deficiency] | attribution frame | not resolved into GAP | — | — |
| SL-ATTR-2 | ATTRIBUTION | COREFERENCE_CONTEXT | NOT_APPLICABLE | context | REJECTED_DEFICIENCY: contrary to X's claim that … | rejection frame | quoted signal must not dominate | — | — |
| SL-REVERSAL-1 | CONTRAST_REVERSAL | DISCOURSE | NOT_APPLICABLE | context | however/but/although/despite/yet/nevertheless | proximity to deficiency wording | never deletes signals | — | — |
| SL-TEMP-1 | TEMPORAL_RESOLUTION | DISCOURSE | NOT_APPLICABLE | context | previously/formerly/was once/until recently/no longer/historically (modifying the deficiency state) | temporal construction over deficiency wording | cancellation blocks positive firing (§40.26a) | — | — |
| SL-CITE-1 | CITATION_CONTEXT | DISCOURSE | WEAK | context | citation co-occurring with deficiency wording | — | never necessary/sufficient | — | — |

## 40.38 Section-prior table (SL-SECTION-1…15; categorical, never determinative, never numeric)

| id | section_role | prior_tier | reason | common_signal_types | common_false_positives | special_handling_note |
|---|---|---|---|---|---|---|
| SL-SECTION-1 | Abstract | NEUTRAL | compressed positioning language, wording-dependent | ABS/LIM/GAPLEX/CONTRIB | contribution phrasing | prior modifies interpretation only |
| SL-SECTION-2 | Introduction | ELEVATED | prior-knowledge positioning concentrates here | ABS/LIM/CONF/GAPLEX/POS | motivation stakes | never sufficient for GAP |
| SL-SECTION-3 | Background | ELEVATED | literature positioning | ABS/LIM/CONF | attributed claims | attribution flags apply |
| SL-SECTION-4 | Literature Review | ELEVATED | densest deficiency assertions | all positive families | attributed/rejected deficiencies | — |
| SL-SECTION-5 | Theory / Theoretical Background | ELEVATED | theory-resource deficiencies | CSTR/CHAL/CONF/ABS | technical "model constraint" | — |
| SL-SECTION-6 | Hypotheses Development | ELEVATED | gap-to-hypothesis links | LIM/CONF/POS | contribution verbs | — |
| SL-SECTION-7 | Methods | REDUCED | procedural language dominates | few | FF-13/18/34; "data limited to" | reduced ≠ exclusion |
| SL-SECTION-8 | Data | REDUCED | dataset description | few | FF-17/19/20 | reduced ≠ exclusion |
| SL-SECTION-9 | Results | REDUCED | statistical reporting | few | FF-14/15/33 | reduced ≠ exclusion |
| SL-SECTION-10 | Discussion | NEUTRAL | mixes positioning, contribution, limitation | LIM/CONTRIB/OWNLIM | contribution/limitation blend | — |
| SL-SECTION-11 | Conclusion | NEUTRAL | summary + contribution | CONTRIB/GAPLEX | referential gap nominals | — |
| SL-SECTION-12 | Limitations | BOUNDARY_SPECIAL | deficiency wording common but often own-study | OWNLIM + genuine LIM/ABS | own-vs-prior conflation | affects prioritization/context, never exclusion |
| SL-SECTION-13 | Future Research | BOUNDARY_SPECIAL | prospective assignments dominate | FUT + genuine deficiency | future-modal blanket-classing | deficiency signals preserved |
| SL-SECTION-14 | Implications | BOUNDARY_SPECIAL | research-practice language frequent | DISC/WORLD/MOT | practitioner-deficit wording | pole test applies |
| SL-SECTION-15 | Appendix | REDUCED | supplementary material | few | technical senses | reduced ≠ exclusion |
| — | UNKNOWN_SECTION | NEUTRAL | classification uncertain upstream | all | — | detection never suppressed |

All section-prior records carry `strength_tier = NOT_APPLICABLE` and `polarity = prior`; the prior_tier column above is the section-prior tier vocabulary, not a strength tier.

## 40.39 Adjudication guidance (signal-level annotation/QA)

- **Fire positive-family signals on locally asserted deficiency predications within the clause, regardless of whether the manuscript ultimately adopts that proposition.** Attribution, rejection, quotation, and reversal are represented by separate context signals (SL-ATTR-1/2, SL-REVERSAL-1, SL-TEMP-1). Nominal reference-only forms remain SL-REF and do not independently fire an assertive deficiency family. The family's required target still applies (knowledge item/activity, resource, artifact, both practice poles). Local deficiency predication ≠ manuscript adoption: Step 7 detects the former; Step 5 later decides the latter.
- Check the **subject/target class first**: researcher/community/literature subjects → knowledge families; practitioner/firm/world subjects → SL-WORLD; instruments → false friend.
- Apply **negation scope** before firing any `negation_scope_sensitive` entry; "not limited", "no longer unexplored", "not inconsistent" never fire the positive family.
- Mark, never resolve: attribution (SL-ATTR-1/2), reversal (SL-REVERSAL-1), temporal resolution (SL-TEMP-1 — cancellation forms block positive firing per §40.26a), coreference (SL-COREF-1), hedges (INT-11), ambiguous "fails to" (SL-CSTR-6/SL-CHAL-5 — no CONSTRAINED/CHALLENGED pre-classification).
- **Support ≠ testing**: SL-SUP and SL-TEST never substitute for each other; both may fire in one passage (INT-12).
- Keep the four research-practice subfamilies distinct; both poles must be named; "research and theory" never fires SL-DISC.
- Section priors inform interpretation only; no fire/not-fire decision ever cites a section as its reason; UNKNOWN → NEUTRAL.
- Anti-signals mark environments; they never veto; dual-content sentences fire both sides (INT-4).
- Strength tiers record semantic directness only; disputes about tier are versioning matters (§40.43), not annotation matters.
- Expected outputs of any signal test are **signals and flags, never Step-5 classes, relations, or kinds**.

## 40.40 Step-3 error-analysis mapping (no new taxonomy; no thresholds)

| Later defect | Diagnosis route | Existing Step-3 class |
|---|---|---|
| Expected signal missing, no static entry covers the surface | signal-library **coverage defect** | rulebook_ambiguity / schema_insufficiency analogue (library layer) |
| Expected signal missing, entry exists | Step-10 **matching/implementation defect** | detector implementation (not a Step-7 defect) |
| False signal fired on a false friend, FF entry exists | Step-10 matching defect | detector implementation |
| False signal fired, no FF entry, wording genuinely resembles | signal-definition **ambiguity** → FF addition or exclusion amendment | rulebook_ambiguity analogue |
| Signal treated as semantic class downstream | Step-10/11 **architecture defect** | architecture, not Step-7 |
| Section prior used as veto/classifier | Step-10 **operational defect** (prior itself correctly defined here) | operational |
| Annotators disagree on fire/not-fire under this library | per Protocol: annotation_error vs rulebook_ambiguity vs genuine_epistemic_ambiguity | frozen Protocol classes |

Candidate-detection precision/yield definitions are Step-10 property; no evaluation thresholds are defined here.

## 40.41 Normative signal test suite (150 tests; uniform schema; expected outputs are signals/context flags only)

**Uniform test schema (machine-consumable).** Every test record carries: `test_id` · `source_text` · `section_role` (null where irrelevant) · `signals_must_fire` · `signals_must_not_fire` · `expected_strength_tiers` (one tier per must-fire signal, in order) · `context_flags` · `rationale` · `later_semantic_question` (unresolved item; "none" where no candidate question arises). Serialization used below: `ID · "source_text" · sec=<role|null> · fire=[…] · not=[…] · tiers=[…] · flags=[…] · <rationale> · unresolved=<…>`.

**Closed context-flag vocabulary (the only flags legal in test records; they mirror §40.4 metadata where applicable):** NEGATION_SCOPE · HEDGE_PRESENT · COREFERENCE_DEPENDENT · SUBJECT_RESOLUTION_REQUIRED · ATTRIBUTION_FRAME · REJECTION_FRAME · REVERSAL_MARKER · TEMPORAL_RESOLUTION · RESOLVED_BY_PRESENT_STUDY · CROSS_SENTENCE · OWN_STUDY_SUBJECT · PRACTITIONER_WORLD_SUBJECT · WORLD_STATE · INSTRUMENT_SUBJECT · PROCEDURAL_STATEMENT · STATISTICAL_RESULT · METHODOLOGY_DESCRIPTOR · ML_DATA_ARTIFACT · TECHNICAL_SENSE · DOMAIN_NON_KNOWLEDGE_GAP · LEGAL_PRODUCT_SENSE · IDIOM_COLLOCATION · REFERENTIAL_NOMINAL · PROSPECTIVE_ASSIGNMENT · AMBIGUOUS_SEMANTICS · PRIOR_KNOWLEDGE_TARGET · MATTERING_ONLY.

**Registry-completeness audit note.** Every SL-* ID invoked in §40.41/§40.42 is registered in §40.37 (section-prior IDs in §40.38); interaction IDs (INT-*) are registered in §40.29; false-friend IDs (FF-*) in §40.30; class labels (e.g., ASSERTIVE_DEFICIENCY_FORM) are explicitly non-normative and never appear in fire/not lists. FF registry entries are not executable tests; only T-FF records are.

**Positives (20).**
T-POS-01 · "No studies have examined X." · sec=null · fire=[SL-ABS-1] · not=[SL-OWNLIM-1, SL-WORLD-1] · tiers=[STRONG] · flags=[PRIOR_KNOWLEDGE_TARGET] · negated research activity · unresolved=BR G1–G7.
T-POS-02 · "There is no theoretical account of X." · sec=null · fire=[SL-ABS-3] · not=[] · tiers=[STRONG] · flags=[] · resource absence · unresolved=G-checks; later kind.
T-POS-03 · "X has never been examined." · sec=null · fire=[SL-ABS-4] · not=[SL-LIM-4] · tiers=[STRONG] · flags=[NEGATION_SCOPE] · categorical negation, scope verified · unresolved=G-checks.
T-POS-04 · "These mechanisms remain unexplored." · sec=null · fire=[SL-ABS-5, SL-COREF-1] · not=[] · tiers=[STRONG, NOT_APPLICABLE] · flags=[COREFERENCE_DEPENDENT] · deficiency head + anaphoric target · unresolved=completion; G-checks.
T-POS-05 · "Researchers do not understand X." · sec=null · fire=[SL-ABS-6] · not=[SL-WORLD-1] · tiers=[STRONG] · flags=[PRIOR_KNOWLEDGE_TARGET] · research-community subject · unresolved=G-checks.
T-POS-06 · "X has received virtually no attention." · sec=null · fire=[SL-ABS-7] · not=[] · tiers=[STRONG] · flags=[HEDGE_PRESENT] · hedged zero (INT-11) · unresolved=ABSENT-vs-LIMITED (DP-PREC-1).
T-POS-07 · "Little is known about how X affects Y." · sec=null · fire=[SL-LIM-1] · not=[] · tiers=[STRONG] · flags=[] · frozen-anchor wording · unresolved=G-checks.
T-POS-08 · "Few studies have examined X." · sec=null · fire=[SL-LIM-2] · not=[SL-OWNLIM-1] · tiers=[STRONG] · flags=[] · degree scarcity · unresolved=G-checks.
T-POS-09 · "Evidence on X remains scarce." · sec=null · fire=[SL-LIM-3] · not=[SL-CSTR-3] · tiers=[STRONG] · flags=[] · adjectival construction · unresolved=G-checks.
T-POS-10 · "X remains underexplored." · sec=null · fire=[SL-LIM-4] · not=[SL-ABS-5] · tiers=[STRONG] · flags=[] · degree morphology · unresolved=G-checks.
T-POS-11 · "Collective adaptation remains poorly understood." · sec=null · fire=[SL-LIM-5] · not=[] · tiers=[STRONG] · flags=[] · — · unresolved=G-checks; kind later.
T-POS-12 · "Prior findings on X are mixed." · sec=null · fire=[SL-CONF-1] · not=[] · tiers=[STRONG] · flags=[PRIOR_KNOWLEDGE_TARGET] · knowledge incompatibility · unresolved=G-checks.
T-POS-13 · "No consensus exists on X." · sec=null · fire=[SL-CONF-4] · not=[] · tiers=[STRONG] · flags=[PRIOR_KNOWLEDGE_TARGET] · — · unresolved=G-checks.
T-POS-14 · "The model remains untested." · sec=null · fire=[SL-TEST-1] · not=[SL-SUP-1] · tiers=[STRONG] · flags=[] · verification-act denial · unresolved=G-checks; DP-REL-4 conditions.
T-POS-15 · "Measure X has not been validated." · sec=null · fire=[SL-TEST-2] · not=[SL-SUP-1] · tiers=[STRONG] · flags=[] · artifact subject · unresolved=G-checks.
T-POS-16 · "Assumption X lacks empirical support." · sec=null · fire=[SL-SUP-1] · not=[SL-TEST-1, SL-TEST-2] · tiers=[STRONG] · flags=[] · support ≠ testing preserved · unresolved=G-checks; later relation.
T-POS-17 · "Existing theories cannot explain X." · sec=null · fire=[SL-CSTR-1] · not=[SL-WORLD-1] · tiers=[STRONG] · flags=[] · knowledge-resource subject · unresolved=G-checks.
T-POS-18 · "Existing studies rely on cross-sectional data, leaving temporal dynamics unexamined." · sec=null · fire=[SL-CSTR-4] · not=[] · tiers=[MODERATE] · flags=[] · one predication, one signal · unresolved=G-checks; single-instance ruling later.
T-POS-19 · "Research and practice remain poorly aligned on X." · sec=null · fire=[SL-DISC-D2] · not=[SL-LIM-3] · tiers=[STRONG] · flags=[] · both poles named; disrelation state · unresolved=G-checks.
T-POS-20 · "Previous theories assume stable boundaries, but this assumption is mistaken." · sec=null · fire=[SL-CHAL-1, SL-REVERSAL-1] · not=[SL-CONF-2] · tiers=[STRONG, NOT_APPLICABLE] · flags=[REVERSAL_MARKER] · authorial invalidity with contrast marker · unresolved=G-checks.

**Boundary-adjacent (20).**
T-BND-01 · "Future research should examine X." · sec=null · fire=[SL-FUT-1] · not=[SL-ABS-1, SL-LIM-1] · tiers=[STRONG] · flags=[PROSPECTIVE_ASSIGNMENT] · prospective assignment · unresolved=BR Route B.
T-BND-02 · "Research is needed to examine X." · sec=null · fire=[SL-FUT-2] · not=[] · tiers=[STRONG] · flags=[PROSPECTIVE_ASSIGNMENT] · need wording · unresolved=deficiency-anchored or not (BR-FUT).
T-BND-03 · "It would be useful to examine X." · sec=null · fire=[SL-FUT-3] · not=[] · tiers=[MODERATE] · flags=[PROSPECTIVE_ASSIGNMENT] · — · unresolved=BR class.
T-BND-04 · "We contribute by developing a model of X." · sec=null · fire=[SL-CONTRIB-1] · not=[SL-GAPLEX-1] · tiers=[STRONG] · flags=[] · yield wording · unresolved=BR class.
T-BND-05 · "We fill this gap by developing a taxonomy." · sec=null · fire=[SL-REF-1, SL-CONTRIB-3] · not=[SL-GAPLEX-1] · tiers=[MODERATE, MODERATE] · flags=[REFERENTIAL_NOMINAL] · gap-response construction (INT-3) · unresolved=BR-CROSS-13 handling upstream.
T-BND-06 · "To address this gap, we examine X." · sec=null · fire=[SL-REF-1, SL-POS-2, SL-CONTRIB-3] · not=[SL-GAPLEX-1] · tiers=[MODERATE, MODERATE, MODERATE] · flags=[REFERENTIAL_NOMINAL, COREFERENCE_DEPENDENT] · response construction; SL-POS-2 co-fires · unresolved=antecedent assertion.
T-BND-07 · "This gap motivates our study." · sec=null · fire=[SL-REF-1, SL-POS-2] · not=[] · tiers=[MODERATE, MODERATE] · flags=[REFERENTIAL_NOMINAL, COREFERENCE_DEPENDENT] · active response form licensed by the SL-POS-2 surface set · unresolved=antecedent assertion.
T-BND-08 · "Understanding SME resilience is important." · sec=null · fire=[SL-MOT-1] · not=[SL-LIM-1] · tiers=[WEAK] · flags=[MATTERING_ONLY] · mattering only · unresolved=BR MOTIVATION.
T-BND-09 · "Cyberattacks cost firms billions annually." · sec=null · fire=[SL-MOT-3] · not=[] · tiers=[WEAK] · flags=[MATTERING_ONLY, WORLD_STATE] · stakes framing · unresolved=BR class.
T-BND-10 · "SMEs account for most employment in Europe." · sec=null · fire=[] · not=[SL-MOT-1, SL-MOT-2, SL-MOT-3, SL-LIM-3] · tiers=[] · flags=[WORLD_STATE] · neutral prevalence — no signal by design · unresolved=none.
T-BND-11 · "Our study is limited by its cross-sectional design." · sec=null · fire=[SL-OWNLIM-1] · not=[SL-CSTR-3] · tiers=[STRONG] · flags=[OWN_STUDY_SUBJECT] · own-study subject · unresolved=BR OWN_LIMITATION.
T-BND-12 · "We were unable to observe long-term outcomes." · sec=null · fire=[SL-OWNLIM-2] · not=[SL-CSTR-1] · tiers=[STRONG] · flags=[OWN_STUDY_SUBJECT] · — · unresolved=BR class.
T-BND-13 · "A limitation of our analysis is the small sample." · sec=null · fire=[SL-OWNLIM-1] · not=[SL-LIM-3] · tiers=[STRONG] · flags=[OWN_STUDY_SUBJECT] · — · unresolved=BR class.
T-BND-14 · "Managers do not understand X." · sec=null · fire=[SL-WORLD-1] · not=[SL-ABS-6] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · hard subject pair · unresolved=BR MOTIVATION/OTHER.
T-BND-15 · "Firms fail to implement evidence-based practices." · sec=null · fire=[SL-WORLD-1] · not=[SL-DISC-D1, SL-DISC-D2] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · no research–practice relation asserted · unresolved=BR class.
T-BND-16 · "Implementation of X remains low." · sec=null · fire=[SL-WORLD-2] · not=[SL-LIM-3] · tiers=[MODERATE] · flags=[WORLD_STATE] · world state · unresolved=BR class.
T-BND-17 · "The aforementioned gap has attracted attention." · sec=null · fire=[SL-REF-1] · not=[SL-GAPLEX-1] · tiers=[MODERATE] · flags=[REFERENTIAL_NOMINAL] · nominal reference · unresolved=antecedent.
T-BND-18 · "We investigate X." · sec=null · fire=[SL-POS-1] · not=[SL-LIM-1, SL-ABS-1] · tiers=[WEAK] · flags=[] · objective wording cannot manufacture a gap · unresolved=none.
T-BND-19 · "Accordingly, we ask how X affects Y." · sec=null · fire=[SL-POS-1, SL-POS-3] · not=[] · tiers=[WEAK, WEAK] · flags=[] · consequence link only · unresolved=linkage to any asserted deficiency.
T-BND-20 · "Our research responds to calls for work on X." · sec=null · fire=[SL-POS-1] · not=[SL-ABS-1, SL-LIM-1, SL-FUT-1] · tiers=[WEAK] · flags=[PROSPECTIVE_ASSIGNMENT] · reported call; no local deficiency predication · unresolved=whether any deficiency is asserted elsewhere.

**Anti-signal / non-firing (20; FF numbers cited where the case instantiates a registry entry).**
T-ANTI-01 · "The evidence base is not limited; it is extensive." · sec=null · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[NEGATION_SCOPE] · negation scope · unresolved=none.
T-ANTI-02 · "Findings were not inconsistent across sites." · sec=null · fire=[] · not=[SL-CONF-2] · tiers=[] · flags=[NEGATION_SCOPE] · negation · unresolved=none.
T-ANTI-03 · "X is no longer unexplored." · sec=null · fire=[SL-TEMP-1] · not=[SL-ABS-5] · tiers=[NOT_APPLICABLE] · flags=[TEMPORAL_RESOLUTION, NEGATION_SCOPE] · explicit cancellation (§40.26a rule B) · unresolved=none.
T-ANTI-04 · "It cannot be said that evidence is limited." · sec=null · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[NEGATION_SCOPE] · scope analysis required before any firing · unresolved=none.
T-ANTI-05 · "No additional analyses were conducted." (FF-34) · sec=null · fire=[] · not=[SL-ABS-1] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · own-study procedure · unresolved=none.
T-ANTI-06 · "No participants reported side effects." (FF-35) · sec=null · fire=[] · not=[SL-ABS-1, SL-ABS-2] · tiers=[] · flags=[WORLD_STATE] · sample observation · unresolved=none.
T-ANTI-07 · "No significant difference was found." (FF-14) · sec=null · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[STATISTICAL_RESULT] · statistical result · unresolved=none.
T-ANTI-08 · "No evidence of misconduct was found." (FF-16) · sec=null · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[WORLD_STATE] · world-directed search result · unresolved=none.
T-ANTI-09 · "The test was not applicable to our sample." (FF-18) · sec=null · fire=[] · not=[SL-TEST-1] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · procedural applicability · unresolved=none.
T-ANTI-10 · "We used a validation dataset." (FF-20) · sec=null · fire=[] · not=[SL-TEST-2] · tiers=[] · flags=[ML_DATA_ARTIFACT] · ML split · unresolved=none.
T-ANTI-11 · "Our camera cannot capture low-light scenes." (FF-38) · sec=null · fire=[] · not=[SL-CSTR-1] · tiers=[] · flags=[INSTRUMENT_SUBJECT] · instrument subject · unresolved=none.
T-ANTI-12 · "Managers cannot explain the new policy to staff." (FF-39) · sec=null · fire=[SL-WORLD-1] · not=[SL-CSTR-1] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · practitioner capability · unresolved=BR class if retained.
T-ANTI-13 · "Participants lack information about the task." (FF-32) · sec=null · fire=[] · not=[SL-GAPLEX-3, SL-WORLD-1] · tiers=[] · flags=[WORLD_STATE] · study-population state; subject outside SL-WORLD-1 class · unresolved=none.
T-ANTI-14 · "Firms lack resources to adopt X." (FF-30) · sec=null · fire=[SL-WORLD-1] · not=[SL-GAPLEX-3] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · world deficit · unresolved=BR class if retained.
T-ANTI-15 · "Data were limited to the 2019 wave." (FF-13) · sec=Methods · fire=[] · not=[SL-LIM-3, SL-CSTR-3] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · sample-scope statement · unresolved=none.
T-ANTI-16 · "The market is challenging for entrants." (FF-26) · sec=null · fire=[] · not=[SL-CHAL-3] · tiers=[] · flags=[IDIOM_COLLOCATION] · difficulty sense · unresolved=none.
T-ANTI-17 · "Gap analysis was performed on service quality." (FF-07) · sec=null · fire=[] · not=[SL-GAPLEX-1, SL-GAPLEX-2] · tiers=[] · flags=[METHODOLOGY_DESCRIPTOR] · method name · unresolved=none.
T-ANTI-18 · "We adopted mixed methods." (FF-08) · sec=null · fire=[] · not=[SL-CONF-1] · tiers=[] · flags=[METHODOLOGY_DESCRIPTOR] · design descriptor · unresolved=none.
T-ANTI-19 · "Consensus was not required for inclusion." (FF-37) · sec=null · fire=[] · not=[SL-CONF-4] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · procedural rule · unresolved=none.
T-ANTI-20 · "The wage gap widened during the period." (FF-02) · sec=null · fire=[] · not=[SL-GAPLEX-1, SL-GAPLEX-2] · tiers=[] · flags=[DOMAIN_NON_KNOWLEDGE_GAP] · phenomenon sense · unresolved=none.

**False-friend tests (40; individually instantiated executable records; FF registry IDs cited in rationale only).**
T-FF-01 · "The gap between revenues and costs increased." · sec=null · fire=[] · not=[SL-GAPLEX-1, SL-GAPLEX-2] · tiers=[] · flags=[DOMAIN_NON_KNOWLEDGE_GAP] · FF-01: "gap" denotes a quantitative difference, not a knowledge deficiency · unresolved=none.
T-FF-02 · "The wage gap widened during the period." · sec=null · fire=[] · not=[SL-GAPLEX-1, SL-GAPLEX-2] · tiers=[] · flags=[DOMAIN_NON_KNOWLEDGE_GAP] · FF-02: social-phenomenon sense · unresolved=none.
T-FF-03 · "The gender gap in participation persists." · sec=null · fire=[] · not=[SL-GAPLEX-1, SL-GAPLEX-2] · tiers=[] · flags=[DOMAIN_NON_KNOWLEDGE_GAP] · FF-03: phenomenon under study, not a research deficiency · unresolved=none.
T-FF-04 · "A generation gap divides the two cohorts." · sec=null · fire=[] · not=[SL-GAPLEX-1] · tiers=[] · flags=[DOMAIN_NON_KNOWLEDGE_GAP] · FF-04: cultural-difference sense · unresolved=none.
T-FF-05 · "The system uses an air gap for security." · sec=null · fire=[] · not=[SL-GAPLEX-1] · tiers=[] · flags=[TECHNICAL_SENSE] · FF-05: engineering term · unresolved=none.
T-FF-06 · "She took a gap year before university." · sec=null · fire=[] · not=[SL-GAPLEX-1] · tiers=[] · flags=[IDIOM_COLLOCATION] · FF-06: fixed collocation · unresolved=none.
T-FF-07 · "Gap analysis was performed on service quality." · sec=null · fire=[] · not=[SL-GAPLEX-1, SL-GAPLEX-2] · tiers=[] · flags=[METHODOLOGY_DESCRIPTOR] · FF-07: named method · unresolved=none.
T-FF-08 · "We use mixed methods." · sec=null · fire=[] · not=[SL-CONF-1, SL-CONF-2] · tiers=[] · flags=[METHODOLOGY_DESCRIPTOR] · FF-08: "mixed" describes research design, not incompatible prior findings · unresolved=none.
T-FF-09 · "We recruited a mixed sample of firms." · sec=null · fire=[] · not=[SL-CONF-1] · tiers=[] · flags=[METHODOLOGY_DESCRIPTOR] · FF-09: sample composition · unresolved=none.
T-FF-10 · "The firm operates under limited liability." · sec=null · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[LEGAL_PRODUCT_SENSE] · FF-10: legal term · unresolved=none.
T-FF-11 · "The supplier is a limited company." · sec=null · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[LEGAL_PRODUCT_SENSE] · FF-11: legal form · unresolved=none.
T-FF-12 · "A limited edition was released." · sec=null · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[LEGAL_PRODUCT_SENSE] · FF-12: product sense · unresolved=none.
T-FF-13 · "Data were limited to the 2019 wave." · sec=Methods · fire=[] · not=[SL-LIM-3, SL-CSTR-3] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · FF-13: sample-scope description · unresolved=none.
T-FF-14 · "No significant difference was found." · sec=null · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[STATISTICAL_RESULT] · FF-14: statistical outcome, not evidence-base absence · unresolved=none.
T-FF-15 · "No effect was observed." · sec=null · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[STATISTICAL_RESULT] · FF-15: result statement · unresolved=none.
T-FF-16 · "No evidence of misconduct was found." · sec=null · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[WORLD_STATE] · FF-16: world-directed search result · unresolved=none.
T-FF-17 · "There were no missing data." · sec=null · fire=[] · not=[SL-ABS-2, SL-GAPLEX-4] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · FF-17: data-quality statement · unresolved=none.
T-FF-18 · "The test was not applicable to our sample." · sec=null · fire=[] · not=[SL-TEST-1] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · FF-18: procedural applicability · unresolved=none.
T-FF-19 · "The model was evaluated on the test set." · sec=null · fire=[] · not=[SL-TEST-1] · tiers=[] · flags=[ML_DATA_ARTIFACT] · FF-19: ML data split · unresolved=none.
T-FF-20 · "We used a validation dataset." · sec=null · fire=[] · not=[SL-TEST-2] · tiers=[] · flags=[ML_DATA_ARTIFACT] · FF-20: ML artifact · unresolved=none.
T-FF-21 · "The parser rejected invalid input." · sec=null · fire=[] · not=[SL-TEST-2, SL-CHAL-1] · tiers=[] · flags=[TECHNICAL_SENSE] · FF-21: technical validity · unresolved=none.
T-FF-22 · "Maximization is subject to the budget constraint." · sec=null · fire=[] · not=[SL-CSTR-3] · tiers=[] · flags=[TECHNICAL_SENSE] · FF-22: formal-model constraint · unresolved=none.
T-FF-23 · "We imposed a model constraint on the parameters." · sec=null · fire=[] · not=[SL-CSTR-3] · tiers=[] · flags=[TECHNICAL_SENSE] · FF-23: estimation constraint · unresolved=none.
T-FF-24 · "The team held a practice session." · sec=null · fire=[] · not=[SL-DISC-D1, SL-DISC-D2] · tiers=[] · flags=[IDIOM_COLLOCATION] · FF-24: rehearsal sense of "practice" · unresolved=none.
T-FF-25 · "In clinical practice, dosing varies." · sec=null · fire=[] · not=[SL-DISC-D1, SL-DISC-D2] · tiers=[] · flags=[WORLD_STATE] · FF-25: practice-world description; no research pole · unresolved=none.
T-FF-26 · "The market is a challenging environment." · sec=null · fire=[] · not=[SL-CHAL-3] · tiers=[] · flags=[IDIOM_COLLOCATION] · FF-26: difficulty sense · unresolved=none.
T-FF-27 · "This is a challenging problem." · sec=null · fire=[] · not=[SL-CHAL-3] · tiers=[] · flags=[IDIOM_COLLOCATION] · FF-27: difficulty sense · unresolved=none.
T-FF-28 · "The search covered unexplored parameter space in the algorithm." · sec=null · fire=[] · not=[SL-ABS-5] · tiers=[] · flags=[TECHNICAL_SENSE] · FF-28: computational-search sense · unresolved=none.
T-FF-29 · "Scarce resources in the empirical setting slowed data collection." · sec=null · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[WORLD_STATE] · FF-29: world resource scarcity · unresolved=none.
T-FF-30 · "Firms lack resources to adopt X." · sec=null · fire=[SL-WORLD-1] · not=[SL-GAPLEX-3] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · FF-30: world/practitioner deficit; lexical "lack" does not make a research-gap cue · unresolved=Step-5 boundary if candidate retained.
T-FF-31 · "Managers lack expertise in analytics." · sec=null · fire=[SL-WORLD-1] · not=[SL-GAPLEX-3] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · FF-31: practitioner capability deficit · unresolved=Step-5 boundary if candidate retained.
T-FF-32 · "Participants lack information about the task." · sec=null · fire=[] · not=[SL-GAPLEX-3, SL-WORLD-1] · tiers=[] · flags=[WORLD_STATE] · FF-32: study-population state; subject outside the SL-WORLD-1 class · unresolved=none.
T-FF-33 · "The effect was not significant." · sec=Results · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[STATISTICAL_RESULT] · FF-33: result reporting · unresolved=none.
T-FF-34 · "No additional analyses were conducted." · sec=null · fire=[] · not=[SL-ABS-1] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · FF-34: own-study procedure · unresolved=none.
T-FF-35 · "No participants reported X." · sec=null · fire=[] · not=[SL-ABS-1, SL-ABS-2] · tiers=[] · flags=[WORLD_STATE] · FF-35: sample observation · unresolved=none.
T-FF-36 · "Little time was available for follow-up." · sec=null · fire=[] · not=[SL-LIM-1] · tiers=[] · flags=[WORLD_STATE] · FF-36: resource scarcity, not knowledge scarcity · unresolved=none.
T-FF-37 · "Consensus was not required for inclusion." · sec=null · fire=[] · not=[SL-CONF-4] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · FF-37: procedural rule · unresolved=none.
T-FF-38 · "Our camera cannot capture low light." · sec=null · fire=[] · not=[SL-CSTR-1] · tiers=[] · flags=[INSTRUMENT_SUBJECT] · FF-38: instrument capability · unresolved=none.
T-FF-39 · "Managers cannot explain X to their staff." · sec=null · fire=[SL-WORLD-1] · not=[SL-CSTR-1] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · FF-39: practitioner capability, not knowledge-resource constraint · unresolved=Step-5 boundary if candidate retained.
T-FF-40 · "The participant made a mistake on the task." · sec=null · fire=[] · not=[SL-CHAL-1] · tiers=[] · flags=[WORLD_STATE] · FF-40: behavioral event, not claim invalidation · unresolved=none.

**Interactions (20; each rationale cites its §40.29 interaction ID).**
T-INT-01 · "Few studies have examined X." · sec=null · fire=[SL-LIM-2] · not=[] · tiers=[STRONG] · flags=[PRIOR_KNOWLEDGE_TARGET] · INT-1: prior-knowledge target present → STRENGTHENS · unresolved=G-checks.
T-INT-02 · "Little is known about X. We therefore investigate X." · sec=null · fire=[SL-LIM-1, SL-POS-3] · not=[] · tiers=[STRONG, WEAK] · flags=[CROSS_SENTENCE] · INT-2: deficiency + consequence link → STRENGTHENS · unresolved=G5.
T-INT-03 · "Motivated by this gap, we test Y." · sec=null · fire=[SL-REF-1, SL-POS-2] · not=[SL-GAPLEX-1] · tiers=[MODERATE, MODERATE] · flags=[REFERENTIAL_NOMINAL, COREFERENCE_DEPENDENT] · INT-2/INT-9: REQUIRES_CONTEXT (antecedent assertion) · unresolved=upstream gap.
T-INT-04 · "We fill this gap by developing a framework." · sec=null · fire=[SL-REF-1, SL-CONTRIB-3] · not=[SL-GAPLEX-1] · tiers=[MODERATE, MODERATE] · flags=[REFERENTIAL_NOMINAL] · INT-3: gap-response construction → BOUNDARY_ADJACENT · unresolved=BR-CROSS-13.
T-INT-05 · "Addressing the lack of evidence on X, we contribute a new dataset." · sec=null · fire=[SL-REF-1, SL-CONTRIB-3, SL-CONTRIB-1] · not=[SL-GAPLEX-3] · tiers=[MODERATE, MODERATE, STRONG] · flags=[REFERENTIAL_NOMINAL] · INT-3: participial gap-response + yield → BOUNDARY_ADJACENT · unresolved=BR-CON-4-type handling.
T-INT-06 · "This study is limited because few prior studies have examined X." · sec=null · fire=[SL-OWNLIM-1, SL-LIM-2] · not=[] · tiers=[STRONG, STRONG] · flags=[OWN_STUDY_SUBJECT] · INT-4: both fire; environment BOUNDARY_ADJACENT; deficiency preserved · unresolved=two propositions upstream.
T-INT-07 · "Our design cannot capture long-run effects." · sec=null · fire=[SL-OWNLIM-2] · not=[SL-CSTR-1] · tiers=[STRONG] · flags=[OWN_STUDY_SUBJECT] · INT-4: own-study environment → BOUNDARY_ADJACENT · unresolved=BR class.
T-INT-08 · "Little is known about X; future research should examine it." · sec=null · fire=[SL-LIM-1, SL-FUT-1] · not=[] · tiers=[STRONG, STRONG] · flags=[PROSPECTIVE_ASSIGNMENT] · INT-5: deficiency not suppressed by FUT · unresolved=BR classes per unit.
T-INT-09 · "Future studies could test the model, which remains untested." · sec=null · fire=[SL-FUT-1, SL-TEST-1] · not=[] · tiers=[STRONG, STRONG] · flags=[PROSPECTIVE_ASSIGNMENT] · INT-5: both visible · unresolved=BR/DPR per proposition.
T-INT-10 · "Managers do not understand X." · sec=null · fire=[SL-WORLD-1] · not=[SL-ABS-6] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · INT-6: WEAKENS for GAP-candidacy · unresolved=BR class.
T-INT-11 · "Organizations struggle to retain talent." · sec=null · fire=[SL-WORLD-1] · not=[] · tiers=[STRONG] · flags=[PRACTITIONER_WORLD_SUBJECT] · INT-6: WEAKENS · unresolved=BR class.
T-INT-12 · "Smith argues that little is known about X." · sec=null · fire=[SL-ATTR-1, SL-LIM-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[ATTRIBUTION_FRAME] · INT-7: REQUIRES_CONTEXT · unresolved=adoption by manuscript.
T-INT-13 · "Contrary to claims that little is known about X, extensive evidence exists." · sec=null · fire=[SL-ATTR-2, SL-LIM-1, SL-REVERSAL-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG, NOT_APPLICABLE] · flags=[REJECTION_FRAME, REVERSAL_MARKER] · INT-8: CONFLICTING_CUES · unresolved=manuscript stance.
T-INT-14 · "Although evidence was once limited, recent studies are extensive." · sec=null · fire=[SL-REVERSAL-1, SL-TEMP-1, SL-LIM-3] · not=[] · tiers=[NOT_APPLICABLE, NOT_APPLICABLE, STRONG] · flags=[REVERSAL_MARKER, TEMPORAL_RESOLUTION] · INT-8/INT-13: CONFLICTING_CUES; past-state predication visible · unresolved=temporal/adoption reading.
T-INT-15 · "These mechanisms remain unexplored." · sec=null · fire=[SL-COREF-1, SL-ABS-5] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[COREFERENCE_DEPENDENT] · INT-9: REQUIRES_CONTEXT · unresolved=completion.
T-INT-16 · "This question remains unanswered." · sec=null · fire=[SL-COREF-1, SL-ABS-5] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[COREFERENCE_DEPENDENT] · INT-9: REQUIRES_CONTEXT · unresolved=completion.
T-INT-17 · "X is increasingly important for policy." · sec=null · fire=[SL-MOT-2] · not=[SL-LIM-1] · tiers=[WEAK] · flags=[MATTERING_ONLY] · INT-10: mattering alone inert for candidacy · unresolved=none.
T-INT-18 · "X has received virtually no attention." · sec=null · fire=[SL-ABS-7] · not=[] · tiers=[STRONG] · flags=[HEDGE_PRESENT] · INT-11: hedge → REQUIRES_CONTEXT · unresolved=strength axis (Step 6).
T-INT-19 · "The model is untested and lacks empirical support." · sec=null · fire=[SL-TEST-1, SL-SUP-1] · not=[] · tiers=[STRONG, STRONG] · flags=[] · INT-12: REQUIRES_CONTEXT · unresolved=possible multi-deficiency separation.
T-INT-20 · "No mechanism exists in the machine." · sec=null · fire=[] · not=[SL-DISC-A1] · tiers=[] · flags=[TECHNICAL_SENSE] · INT-1 negative: target not a knowledge/bridge resource · unresolved=none.

**Section priors (15; section priors are categorical context, never suppression).**
T-SEC-01 · "Little is known about X." · sec=Introduction · fire=[SL-LIM-1] · not=[] · tiers=[STRONG] · flags=[] · prior ELEVATED; signal unchanged by section · unresolved=G-checks.
T-SEC-02 · "Little is known about X." · sec=Methods · fire=[SL-LIM-1] · not=[] · tiers=[STRONG] · flags=[] · prior REDUCED; reduced ≠ exclusion · unresolved=G-checks.
T-SEC-03 · "Little is known about X." · sec=Results · fire=[SL-LIM-1] · not=[] · tiers=[STRONG] · flags=[] · prior REDUCED · unresolved=G-checks.
T-SEC-04 · "Little is known about X." · sec=UNKNOWN · fire=[SL-LIM-1] · not=[] · tiers=[STRONG] · flags=[] · UNKNOWN_SECTION → NEUTRAL; never suppressed · unresolved=G-checks.
T-SEC-05 · "Our study is limited by X." · sec=Limitations · fire=[SL-OWNLIM-1] · not=[SL-LIM-3] · tiers=[STRONG] · flags=[OWN_STUDY_SUBJECT] · BOUNDARY_SPECIAL: own-study environment · unresolved=BR class.
T-SEC-06 · "Few prior studies have examined X." · sec=Limitations · fire=[SL-LIM-2] · not=[SL-OWNLIM-1] · tiers=[STRONG] · flags=[] · deficiency preserved inside Limitations · unresolved=G-checks.
T-SEC-07 · "Future research should examine X." · sec=FutureResearch · fire=[SL-FUT-1] · not=[] · tiers=[STRONG] · flags=[PROSPECTIVE_ASSIGNMENT] · BOUNDARY_SPECIAL; not auto-FUTURE_RESEARCH class · unresolved=BR Route B.
T-SEC-08 · "Little is known about X." · sec=FutureResearch · fire=[SL-LIM-1] · not=[] · tiers=[STRONG] · flags=[] · deficiency preserved · unresolved=G-checks.
T-SEC-09 · "Research has not translated into practice." · sec=Implications · fire=[SL-DISC-D1] · not=[] · tiers=[STRONG] · flags=[] · BOUNDARY_SPECIAL; pole test applies · unresolved=G-checks.
T-SEC-10 · "No evidence exists on X." · sec=LiteratureReview · fire=[SL-ABS-2] · not=[] · tiers=[STRONG] · flags=[] · prior ELEVATED · unresolved=G-checks.
T-SEC-11 · "Data were limited to the 2019 wave." · sec=Methods · fire=[] · not=[SL-LIM-3] · tiers=[] · flags=[PROCEDURAL_STATEMENT] · FF-13 case; prior REDUCED irrelevant to non-signal · unresolved=none.
T-SEC-12 · "The effect was not significant." · sec=Results · fire=[] · not=[SL-ABS-2] · tiers=[] · flags=[STATISTICAL_RESULT] · FF-33 case · unresolved=none.
T-SEC-13 · "There is a gap in knowledge about X." · sec=Abstract · fire=[SL-GAPLEX-1] · not=[] · tiers=[MODERATE] · flags=[] · prior NEUTRAL · unresolved=G-checks.
T-SEC-14 · "We contribute new evidence on X." · sec=Conclusion · fire=[SL-CONTRIB-1] · not=[] · tiers=[STRONG] · flags=[] · prior NEUTRAL · unresolved=BR class.
T-SEC-15 · "Existing theories cannot explain X." · sec=Theory · fire=[SL-CSTR-1] · not=[] · tiers=[STRONG] · flags=[] · prior ELEVATED · unresolved=G-checks.

**Attribution / contrast / coreference / temporal (15).**
T-CTX-01 · "Smith argues that little is known about X." · sec=null · fire=[SL-ATTR-1, SL-LIM-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[ATTRIBUTION_FRAME] · local deficiency predication inside the complement; adoption undecided · unresolved=manuscript adoption.
T-CTX-02 · "As Lee (2019) notes, evidence remains scarce." · sec=null · fire=[SL-ATTR-1, SL-LIM-3, SL-CITE-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG, WEAK] · flags=[ATTRIBUTION_FRAME] · attributed deficiency + citation context · unresolved=adoption.
T-CTX-03 · "Contrary to Smith's claim that little is known, extensive evidence exists." · sec=null · fire=[SL-ATTR-2, SL-LIM-1, SL-REVERSAL-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG, NOT_APPLICABLE] · flags=[REJECTION_FRAME, REVERSAL_MARKER] · rejected deficiency remains detection-visible, never dominant · unresolved=manuscript stance.
T-CTX-04 · "However, little is known about X." · sec=null · fire=[SL-REVERSAL-1, SL-LIM-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[REVERSAL_MARKER, CROSS_SENTENCE] · reversal of a preceding claim frames the deficiency · unresolved=contrast target.
T-CTX-05 · "Although X is well studied, little is known about Y." · sec=null · fire=[SL-REVERSAL-1, SL-LIM-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[REVERSAL_MARKER] · concessive frames the deficiency on Y · unresolved=G-checks on Y.
T-CTX-06 · "Despite extensive research, X remains poorly understood." · sec=null · fire=[SL-REVERSAL-1, SL-LIM-5] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[REVERSAL_MARKER] · concessive frame · unresolved=G-checks.
T-CTX-07 · "This issue remains unresolved." · sec=null · fire=[SL-COREF-1, SL-GAPLEX-4] · not=[] · tiers=[NOT_APPLICABLE, MODERATE] · flags=[COREFERENCE_DEPENDENT] · completion required · unresolved=antecedent.
T-CTX-08 · "Such evidence is lacking." · sec=null · fire=[SL-COREF-1, SL-GAPLEX-3] · not=[] · tiers=[NOT_APPLICABLE, MODERATE] · flags=[COREFERENCE_DEPENDENT] · completion required · unresolved=antecedent.
T-CTX-09 · "This disconnect persists." · sec=null · fire=[SL-COREF-1] · not=[SL-DISC-D2] · tiers=[NOT_APPLICABLE] · flags=[COREFERENCE_DEPENDENT] · anaphoric nominal; poles unverified locally, so no DISC family firing · unresolved=antecedent poles.
T-CTX-10 · "These findings are central to our model." · sec=null · fire=[SL-COREF-1] · not=[SL-LIM-1] · tiers=[NOT_APPLICABLE] · flags=[COREFERENCE_DEPENDENT] · no deficiency head · unresolved=none.
T-CTX-11 · "\"Little is known about X,\" Smith wrote." · sec=null · fire=[SL-ATTR-1, SL-LIM-1] · not=[] · tiers=[NOT_APPLICABLE, STRONG] · flags=[ATTRIBUTION_FRAME] · quoted deficiency remains detectable (local predication) · unresolved=adoption.
T-CTX-12 · "Prior studies focus on X. Consequently, Y remains poorly understood." · sec=null · fire=[SL-LIM-5, SL-POS-3] · not=[] · tiers=[STRONG, WEAK] · flags=[CROSS_SENTENCE] · consequence pattern across sentences · unresolved=G-checks on Y.
T-CTX-13 · "Evidence remains mixed. We therefore examine whether X affects Y." · sec=null · fire=[SL-CONF-1, SL-POS-3] · not=[] · tiers=[STRONG, WEAK] · flags=[CROSS_SENTENCE] · deficiency + response link · unresolved=G5.
T-CTX-14 · "Contrary to Smith, we find extensive evidence." · sec=null · fire=[SL-REVERSAL-1] · not=[SL-ATTR-2, SL-LIM-1] · tiers=[NOT_APPLICABLE] · flags=[REVERSAL_MARKER] · rejection of a cited position with no local deficiency predication; SL-ATTR-2 requires embedded deficiency wording · unresolved=none.
T-CTX-15 · "We explored the previously unexplored region." · sec=null · fire=[SL-TEMP-1] · not=[SL-ABS-5] · tiers=[NOT_APPLICABLE] · flags=[TEMPORAL_RESOLUTION, RESOLVED_BY_PRESENT_STUDY] · own-study resolution (§40.26a rule C; FF-42) · unresolved=none.

**Count audit.** Positives 20 · boundary-adjacent 20 · anti 20 · false-friend tests 40 (T-FF-01…T-FF-40, individually instantiated) · interactions 20 · section priors 15 · attribution/contrast/coreference/temporal 15 → **150 tests**, every record in the uniform schema; no test's expected output is a GAP class, relation, or kind; FF registry entries (§40.30, 46 items) are cited in rationales only and are not counted as tests.

## 40.42 Adversarial minimal-pair suite (40 comparisons; each: which signals differ · why · unresolved later question)

MP-01 · "No studies examine X." ‖ "No participants reported X." · SL-ABS-1 vs none · research activity vs sample observation · unresolved: G-checks (left only).
MP-02 · "Little is known about X." ‖ "Little time was available." · SL-LIM-1 vs none · knowledge vs resource · left G-checks.
MP-03 · "X remains unexplored." ‖ "We explored X." · SL-ABS-5 vs none · assertion vs own-study action · left G-checks.
MP-04 · "X remains underexplored." ‖ "X remains unexplored." · SL-LIM-4 vs SL-ABS-5 · degree vs categorical morphology · later ABSENT/LIMITED (Step 6).
MP-05 · "Prior findings are mixed." ‖ "We use mixed methods." · SL-CONF-1 vs none (FF-08) · knowledge incompatibility vs methodology · left G-checks.
MP-06 · "No consensus exists on X." ‖ "Consensus was not required." · SL-CONF-4 vs none (FF-37) · prior positions vs procedure · left G-checks.
MP-07 · "The model remains untested." ‖ "The test was not applicable." · SL-TEST-1 vs none (FF-18) · verification denial vs procedural applicability · left G-checks.
MP-08 · "The model lacks empirical support." ‖ "The model remains untested." · SL-SUP-1 vs SL-TEST-1 · support-absence vs testing-absence (families never merge) · later DP-PREC-10 relation split.
MP-09 · "Existing theories cannot explain X." ‖ "Managers cannot explain X." · SL-CSTR-1 vs SL-WORLD-1 · resource vs practitioner subject · left G-checks; right BR class.
MP-10 · "Existing measures cannot capture X." ‖ "Our camera cannot capture X." · SL-CSTR-1 vs none (FF-38) · knowledge resource vs instrument · left G-checks.
MP-11 · "Research and practice remain poorly aligned." ‖ "Managers are poorly aligned." · SL-DISC-D2 vs none · both research-practice poles vs world-state alignment · left G-checks; right no Step-7 signal.
MP-12 · "No mechanism exists for translating research into practice." ‖ "No mechanism exists in the machine." · SL-DISC-A1 vs none · bridge apparatus vs machinery · left G-checks.
MP-13 · "Research-practice translation remains limited." ‖ "Our study is limited." · SL-DISC-B1 vs SL-OWNLIM-1 · bridge process vs own study · left G-checks; right BR class.
MP-14 · "The prevailing theory is mistaken." ‖ "The participant made a mistake." · SL-CHAL-1 vs none (FF-40) · prior position vs behavior · left G-checks.
MP-15 · "We challenge the assumption that X." ‖ "X is a challenging problem." · SL-CHAL-3 vs none (FF-27) · authorial contest vs difficulty · left G-checks.
MP-16 · "This gap motivates our study." ‖ "There is a gap in knowledge about X." · SL-REF-1+SL-POS-2 (active form in the registered SL-POS-2 surface set) vs SL-GAPLEX-1 · reference vs assertive existential · right G-checks; left antecedent.
MP-17 · "We fill this gap." ‖ "Few studies have examined X." · SL-REF-1+SL-CONTRIB-3 vs SL-LIM-2 · referential gap-response construction vs asserted deficiency · right G-checks.
MP-18 · "Future research should examine X." ‖ "No research has examined X." · SL-FUT-1 vs SL-ABS-1 · prospective assignment vs asserted absence · right G-checks; left BR Route B.
MP-19 · "Our study is limited by X." ‖ "Prior research is limited by X." · SL-OWNLIM-1 vs SL-CSTR-3 · own vs prior target · right G-checks.
MP-20 · "Managers do not understand X." ‖ "Researchers do not understand X." · SL-WORLD-1 vs SL-ABS-6 · practitioner vs research-community subject · right G-checks; left BR class.
MP-21 · "X has rarely been examined." ‖ "X has never been examined." · SL-LIM-4 vs SL-ABS-4 · degree vs categorical · later strength axis.
MP-22 · "Limited evidence exists on X." ‖ "Evidence is limited by cross-sectional design." · SL-LIM-3 vs SL-CSTR-3 · adjectival scarcity vs restriction construction · later LIMITED/CONSTRAINED (Step 6).
MP-23 · "No consensus exists on X." ‖ "No consensus exists among managers about strategy." · SL-CONF-4 vs world-target non-fire · prior knowledge vs world state · left G-checks.
MP-24 · "X remains contested." ‖ "We contest the view that X." · SL-CONF-5 vs SL-CHAL-3 · contester unresolved vs authorial · later DP-REL-3a.
MP-25 · "Theories fail to explain X." ‖ "Theories cannot explain X." · SL-CSTR-6/SL-CHAL-5 (ambiguous) vs SL-CSTR-1 · "fails to" unresolved by A1E-DPR-1.1 · later OD-DPR-2 / R3.
MP-26 · "Translation of research into practice remains limited." ‖ "Research has not translated into practice." · SL-DISC-B1 vs SL-DISC-D1 · process insufficiency vs disrelation state · later DP-PREC-11.
MP-27 · "No mechanism exists for translating research into practice." ‖ "Research and practice are disconnected." · SL-DISC-A1 vs SL-DISC-D2 · absent bridge entity vs unlinked state · later DP-PREC-15.
MP-28 · "Barriers constrain research-to-practice translation." ‖ "Research-to-practice translation remains limited." · SL-DISC-C1 vs SL-DISC-B1 · constrainer head vs degree head · later DP-PREC-12.
MP-29 · "Smith argues little is known about X." ‖ "Little is known about X." · +SL-ATTR-1 vs plain · attribution frame · later adoption question.
MP-30 · "Contrary to claims that little is known, extensive evidence exists." ‖ "Little is known about X." · +SL-ATTR-2/REVERSAL vs plain · rejection frame · later stance.
MP-31 · "Although evidence was once limited, recent work is extensive." ‖ "Evidence remains limited." · +SL-REVERSAL-1 +SL-TEMP-1 (distinct context signals: concessive contrast; closed-past state) vs plain SL-LIM-3 · left past-state predication remains visible · later temporal/adoption reading.
MP-32 · "These mechanisms remain unexplored." ‖ "These mechanisms are central to our model." · SL-ABS-5+SL-COREF-1 vs SL-COREF-1 only · deficiency head present vs absent · left completion + G-checks.
MP-33 · "A lack of evidence on X persists." ‖ "Addressing the lack of evidence on X, we develop …" · SL-GAPLEX-3 assertive vs SL-REF-1 participial reference · assertion vs reference · right BR-CROSS-13.
MP-34 · "Research is needed to examine X." ‖ "Further research is needed because little is known about X." · SL-FUT-2 alone vs SL-FUT-2+SL-LIM-1 · bare need vs need + deficiency · right G-checks per unit.
MP-35 · "We investigate X." ‖ "Little is known about X; we therefore investigate X." · SL-POS-1 only vs SL-LIM-1+SL-POS-3 · objective wording cannot manufacture a gap · right G5.
MP-36 · "No evidence exists on X." ‖ "No evidence of an effect was found." · SL-ABS-2 vs none (FF-16-type) · knowledge-state vs result · left G-checks.
MP-37 · "X is understudied." ‖ "X is currently under study." · SL-LIM-4 vs none · deficiency vs ongoing-work statement · left G-checks.
MP-38 · "The model remains unvalidated." ‖ "The validation dataset contains 500 cases." · SL-TEST-2 vs none (FF-20) · verification denial vs ML split · left G-checks.
MP-39 · "Researchers do not understand X." ‖ "We do not understand X." · SL-ABS-6 vs SL-ABS-6 with `requires_subject_resolution` · explicit vs ambiguous community subject · right subject resolution then G-checks.
MP-40 · "X is poorly understood." ‖ "X was poorly understood until recently." · SL-LIM-5 vs SL-LIM-5+SL-TEMP-1 · present vs closed-past deficiency state (§40.26a rule A) · right temporal reading later.

## 40.43 Versioning

`signal_library_version = A1E-SL-1.1`, pinned by the Step-10 Candidate Detection Spec and by any detection-quality evaluation. Signal IDs are permanent; retired IDs never reused. Amendment classes: **new signal** (addition; detection tests extended) · **clarifying amendment** (wording, exemplars, orthographic variants without scope change — e.g., adding "under-explored" spacing variants) · **surface-form expansion** (new realizations under an unchanged canonical cue — clarifying unless scope shifts) · **false-friend addition** (clarifying) · **semantic amendment** (scope/tier/required-context change — e.g., changing what "X remains unexplored" covers) · **section-prior amendment** (tier change = semantic) · **signal retirement** (semantic for dependents). Every semantic amendment must name the affected §40.41/§40.42 tests and the Step-3 gold strata (via the frozen Protocol's versioning rules) requiring re-evaluation. No global invalidation mechanics are defined here. **v1.0 → v1.1 record:** exactly the seven corrections in the header revision record; all are correction-class amendments (tier normalization; adjudication-rule fix; coverage additions SL-ABS-8/9, SL-SUP-4, SL-CONTRIB-3, SL-TEMP-1; test-suite normalization); no unrelated signal semantics changed. **Final-issuance record (7C, same version):** `ambiguous_semantics` demoted from polarity to metadata (SL-CSTR-6, SL-CHAL-5); "No empirical evidence supports X" → SL-SUP-4 only; SL-POS-2 surface set extended with the active "this gap motivates our/the present study" construction; MP-11 corrected to remove the undefined pseudo-signal `SL-WORLD-adjacent` (right-hand world-state example fires no Step-7 signal). No Step-7 semantics changed.

## 40.44 Open decisions (all calibration-dependent; none blocks Step-7 freeze; Step 10 may proceed on all)

- **OD-SL-1 — weak-signal operational retention.** Whether WEAK entries (SL-GAPLEX-2, SL-MOT-1/2/3, SL-CITE-1) earn their detection cost. Unresolved because signal frequency/utility data do not yet exist. Evidence: Step-10 pilot yield analysis. Blocks freeze: no; Step 10 may proceed treating WEAK entries as optional context.
- **OD-SL-2 — section-prior utility.** Whether ELEVATED/REDUCED priors measurably improve candidate quality. Evidence: pilot recall/precision by section under Step-10's definitions. Blocks freeze: no; priors are already non-determinative.
- **OD-SL-3 — attribution-signal prioritization.** Whether ATTRIBUTED/REJECTED context should modify candidate prioritization (a Step-10 operational question; the signals themselves are settled). Evidence: pilot handling of attributed deficiencies. Blocks freeze: no.
- **OD-SL-4 — rare surface-form coverage.** Which rare orthographic/lexical variants deserve entries. Evidence: corpus frequency from pilots; handled via surface-form expansion. Blocks freeze: no.

No signal's meaning, exclusions, family membership, or false-friend status is left open.

## 40.45 Freeze check

| Check | PASS/FAIL | Evidence |
|---|---|---|
| Signal Library is static; no candidate emission implemented | PASS | §40.1/§40.3; no emission rule anywhere; interactions categorical (§40.29) |
| Step-10 candidate-generation ownership preserved | PASS | no thresholds, windows, scoring, ranking, dedup/merge; §40.32–40.33 defer runtime |
| Step-5 boundary semantics not duplicated | PASS | crosswalk-only (§40.35); no class assigned in any card or test |
| Step-6 relation/kind classification not duplicated | PASS | crosswalk-only (§40.36); "fails to"/"contested" left unresolved |
| No affected-object extraction introduced | PASS | no object output anywhere; Step-8 untouched |
| All seven deficiency-semantic families covered | PASS | §40.7–40.14 (ABS/LIM/CONF/TEST/CSTR/DISC/CHAL) + SUP family |
| Testing absence and evidential-support absence are separate families | PASS | §40.10 vs §40.11; MP-08; INT-12 |
| "fails to …" detection-visible but semantically unresolved | PASS | SL-CSTR-6/SL-CHAL-5 `ambiguous_semantics`; MP-25; OD-DPR-2 untouched |
| All four practice_alignment patterns separately represented | PASS | SL-DISC-A1/B1/C1/D1–D2; MP-26/27/28 |
| Practitioner/world deficits distinguishable from research-knowledge deficits | PASS | SL-WORLD vs SL-ABS-6; MP-09/20; subject-class constraints |
| Assertion vs reference-only gap wording distinguishable | PASS | §40.16; SL-REF-1/2; MP-16/17/33 |
| "gap" not sufficient | PASS | SL-GAPLEX-2 WEAK; anti-shortcuts (§40.15); FF-01…07 |
| "lack" not sufficient | PASS | SL-GAPLEX-3 constraints; FF-30…32 |
| Lexical signals are target-sensitive | PASS | required_context on every predicate-pattern entry |
| Negation scope represented | PASS | §40.24; T-ANTI-01…04 |
| Attribution/rejection context represented | PASS | §40.25; SL-ATTR-1/2; T-CTX block |
| Contrast/reversal context represented | PASS | §40.26; SL-REVERSAL-1; signals never deleted |
| Coreference-dependent signals represented without resolution | PASS | §40.27; SL-COREF-1; T-INT-15/16 |
| Section priors categorical and non-determinative | PASS | §40.28/§40.38; explicit non-override statements |
| Unknown section does not suppress detection | PASS | UNKNOWN → NEUTRAL; T-SEC-04 |
| Future Research treated as boundary-special, not excluded | PASS | SL-SECTION-13; T-SEC-07/08 |
| Limitations treated as boundary-special, not excluded | PASS | SL-SECTION-12; T-SEC-05/06 |
| Anti-signals are not hard vetoes | PASS | anti-signal semantics (§40.19); INT-4; T-INT-06 |
| Contribution wording cannot manufacture a deficiency | PASS | §40.21; T-BND-04/05 |
| Motivation wording cannot manufacture a deficiency | PASS | §40.22; INT-10; T-BND-08…10 |
| Objective/RQ/purpose wording cannot manufacture a deficiency | PASS | §40.17; T-BND-18; MP-35 |
| Citation presence neither necessary nor sufficient | PASS | §40.34; SL-CITE-1 WEAK context |
| At least 40 false friends included | PASS | FF-01…FF-46 (§40.30); executable tests T-FF-01…40 (§40.41) |
| At least 40 genuine minimal pairs included | PASS | MP-01…MP-40, one comparison each (§40.42) |
| Signal interactions define no runtime scoring | PASS | §40.29 categorical effects only |
| No numeric candidate-emission threshold appears | PASS | document-wide absence |
| No candidate window size appears | PASS | §40.33 explicit deferral |
| No candidate ranking algorithm appears | PASS | absent |
| No candidate dedup/merge algorithm appears | PASS | absent |
| No regex engine/runtime implementation specified | PASS | §40.32 metadata only |
| Step-7 signal IDs stable and machine-referenceable | PASS | §40.37; §40.43 stability rules |
| Test-suite expected outputs are signals, not final GAP classes | PASS | uniform schema + closed flag vocabulary (§40.41); count audit |
| Step-3 evaluation architecture not redesigned | PASS | §40.40 maps to frozen classes; no thresholds |
| Artifact complete and self-contained | PASS | §40.1–§40.45 in one document; no legacy dependency |
| Downstream Step 8/9/10/11/13 ownership intact | PASS | §40.1 exclusions; §40.17 (no G5); §40.29/§40.33 (no operationalization); §40.40 |
| strength_tier uses only STRONG, MODERATE, WEAK, NOT_APPLICABLE | PASS | §40.6 closed vocabulary; §40.37 tier column contains only these four values |
| polarity is never embedded inside strength_tier | PASS | compound tier forms eliminated document-wide; separate tier/polarity columns (§40.37) |
| every signal has exactly one strength_tier | PASS | §40.6 rule; one tier per §40.37 row |
| no WEAK/MODERATE or MODERATE/WEAK tier remains | PASS | SL-GAPLEX-4 → MODERATE; SL-MOT-2/3 → WEAK (in-card justification, §40.22) |
| attributed deficiency wording remains detectable | PASS | §40.16/§40.25; T-CTX-01/02/11; T-INT-12; MP-29 |
| rejected deficiency wording remains detectable | PASS | T-CTX-03; T-INT-13; MP-30 |
| local deficiency predication is distinct from manuscript adoption | PASS | frozen rule in §40.16, §40.25, §40.39 |
| nominal/reference-only wording still does not independently fire assertive deficiency signals | PASS | SL-REF-1/2; §40.39; T-BND-17; MP-33 |
| Step-5 adoption/assertion judgment has not moved into Step 7 | PASS | adoption always `unresolved` in tests (T-CTX-01…03); crosswalks informational |
| frozen DPR example "No model explains X" has detection coverage | PASS | SL-ABS-8; §40.36a |
| frozen DPR example "No validated method exists to measure X" has detection coverage | PASS | SL-ABS-9; §40.36a |
| frozen DPR example "No empirical evidence supports assumption X" has detection coverage | PASS | SL-SUP-4; §40.36a |
| Step-6 positive-example coverage audit contains no unexplained gaps | PASS | §40.36a — all rows PASS |
| support absence remains separate from testing absence | PASS | SL-SUP-4 exclusion metadata; MP-08; FF-46 |
| "fill this gap" behavior is represented by an actual registered signal | PASS | SL-CONTRIB-3 (§40.21, §40.37); T-BND-05; T-INT-04; MP-17 |
| temporal-resolution behavior is represented by an actual registered context signal | PASS | SL-TEMP-1 (§40.26a, §40.37) |
| logical reversal and temporal resolution are not conflated | PASS | §40.26 non-conflation note; MP-31; T-INT-14 |
| "X was poorly understood until recently" has defined signal behavior | PASS | §40.26a rule A; MP-40 |
| "X is no longer unexplored" does not fire a current positive absence signal | PASS | §40.26a rule B; T-ANTI-03 |
| "previously unexplored" in a resolved/own-study construction has defined signal behavior | PASS | §40.26a rule C; FF-42; T-CTX-15 |
| at least 40 false-friend tests are individually instantiated | PASS | T-FF-01…T-FF-40 (§40.41) |
| each false-friend test contains all required test-schema fields | PASS | uniform serialization; §40.41 schema preamble |
| false-friend registry examples are not counted as executable tests unless a T-FF record exists | PASS | §40.30 note; §40.41 count audit |
| every signal ID invoked by a normative test exists in §40.37 | PASS | registry-completeness audit note (§40.41); SL-SECTION-* registered in §40.38 |
| every normative signal appearing in prose is either registered or explicitly non-normative | PASS | class labels marked non-normative (§40.16; §40.41 audit note) |
| no undefined "context signal" is used in test expectations | PASS | closed context-flag vocabulary (§40.41); fire/not lists contain registered IDs only |
| test outputs remain signals/context flags, never GAP/relation/kind verdicts | PASS | §40.41 schema; count audit |
| no runtime candidate-emission logic has been added | PASS | all v1.1 corrections are static definitions; §40.1 prohibitions intact |
| Step 10 ownership remains intact | PASS | no thresholds, windows, scoring, ranking, dedup added anywhere in v1.1 |
| every polarity value is exactly one of positive, anti, context, boundary, reference, prior | PASS | §40.37 polarity-column scan: six legal values only; no compound entries |
| `ambiguous_semantics` appears only as metadata/notes and never as polarity | PASS | SL-CSTR-6/SL-CHAL-5 registry notes column; §40.12/§40.14 cards |
| SL-CSTR-6 has polarity = positive and ambiguous_semantics = true | PASS | §40.12 card; §40.37 row |
| SL-CHAL-5 has polarity = positive and ambiguous_semantics = true | PASS | §40.14 card; §40.37 row |
| "No evidence exists on X" is covered by SL-ABS-2 | PASS | SL-ABS-2 card (§40.7); T-SEC-10; §40.36a existential row |
| "No empirical evidence supports X" is covered by SL-SUP-4 | PASS | SL-SUP-4 card (§40.11); §40.36a support-predicate row |
| "No empirical evidence supports X" does not additionally require SL-ABS-2 | PASS | §40.36a corrected row; SL-ABS-2 exclusion (support-predicate → SL-SUP-4) |
| support-predicate absence and existential evidence absence remain separate surface constructions | PASS | mutual exclusions on SL-ABS-2 and SL-SUP-4 cards |
| testing absence remains separate from both | PASS | SL-TEST family; SL-SUP-4 three-way separation note; MP-08 |
| SL-POS-2 explicitly licenses "This gap motivates our study." | PASS | §40.17 card surface set; §40.37 row |
| T-BND-07 is consistent with the registered SL-POS-2 definition | PASS | T-BND-07 rationale cites the licensed active form |
| MP-16 is consistent with the registered SL-POS-2 definition | PASS | MP-16 wording; §40.17 surface set |
| generic motivation such as "This phenomenon motivates our study" does not automatically fire SL-POS-2 | PASS | §40.17 hard rule + counterexample; §40.37 exclusions column |
| every signal invoked in §40.36a, §40.41, and §40.42 is licensed by its registered definition | PASS | closure audit A–E: firings licensed by surface/context; non-firings match exclusions; no substring-driven expectation remains (§40.36a fix); no compound polarity/tier fields; ambiguity flags metadata-only |
| MP-11 left side fires SL-DISC-D2 | PASS | MP-11; SL-DISC-D2 card — both research-practice poles explicitly present |
| MP-11 right side fires no Step-7 signal | PASS | MP-11 "right no Step-7 signal"; no research pole, no research↔practice relation, no SL-WORLD-1 capability/knowledge predicate |
| MP-11 contains no undefined pseudo-signal | PASS | MP-11 expected outputs: SL-DISC-D2 vs none |
| `SL-WORLD-adjacent` appears nowhere in the normative artifact | PASS | zero occurrences in §40.36a/§40.41/§40.42 and all signal-bearing sections; the token survives only as quoted-prohibited text in this check row and the version record |
| every SL-* token in §40.36a, §40.41, and §40.42 is registered | PASS | broad-token closure scan: every SL-* token resolves to a §40.37 ID or a §40.38 SL-SECTION-* ID; no pseudo-labels |
| no new signal was introduced by the MP-11 correction | PASS | registry row count unchanged (74); no new IDs |
| no existing signal semantics changed by the MP-11 correction | PASS | edit confined to one §40.42 expectation line + version record |

**All checks PASS — the A.1-E Signal Library is declared FROZEN at v1.1 (`A1E-SL-1.1`), pinned to `A1E-BR-1.2` and `A1E-DPR-1.1`. `A1E-SL-1.0` is superseded.**
