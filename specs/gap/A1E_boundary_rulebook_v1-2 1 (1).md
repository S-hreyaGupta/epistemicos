# A.1-E Boundary Rulebook v1.2 — EpistemicOS (Step 5)

**Status:** normative once the Freeze Check (§38.23) passes. Version string: `A1E-BR-1.2`.
**Document form:** **self-contained.** This document is the complete authoritative Boundary Rulebook. Every operative rule, definition, procedure step, precedence rule, registry entry, and test item appears in full; interpreting `A1E-BR-1.2` requires no earlier version. The change register (§38.21) records which clauses changed across versions; it is provenance, not operative content.
**Normative frozen inputs:** `A1E_gap_extraction_contract_v1-2.md` · `A1E_gap_object_schema_v1-2.md` · `A1E_annotation_validation_protocol_v1-2.md` · `A1E_state_machine_v1-3.md`.
**Defines:** classification of a proposition unit as `GAP` versus exactly one of `MOTIVATION · OWN_LIMITATION · FUTURE_RESEARCH · CONTRIBUTION · OTHER · UNCERTAIN` (the seven contract-frozen classes; none added or removed).
**Does not define:** relation/kind mapping (Step 6); affected-object extraction (Step 8); merge/identity (Step 9); detection (Step 10); structured extraction (Step 11); resolution (Step 12); verifier logic (Step 13); characterization (A.1-C); scientific gap analysis (A.1-A).
**Supersedes:** `A1E-BR-1.1`, `A1E-BR-1.0`, and the `interim-0` boundary asset (Contract §6 + legacy KB-3 cards). Pilot labels produced under any earlier boundary asset remain pilot-only (Protocol 29.12). Legacy KB-3's predicate→subject→marker test survives, re-derived, as BR-GAP-2/BR-GAP-3/BR-CROSS-5.

---

## 38.1 Boundary principles

1. **Assertion, not presupposition — including nominalized gap language.** A unit is classified by what it explicitly predicates. Pragmatic implication, presupposition, and deficiency-*denoting* noun phrases in argument position ("addressing **this gap**, we…") never classify; only asserted deficiency does.
2. **The target decides.** Every deficiency has a target: prior knowledge / knowledge structure — including the research–practice knowledge relationship — is the GAP path; the present study is OWN_LIMITATION; the external world, including practitioner capability, is the MOTIVATION/OTHER path. The target test runs before class competition.
3. **Context completes; context never creates — and failed completion never demotes.** Linguistic completion (anaphora, ellipsis, omitted arguments, referential dependency) may supply missing arguments of an asserted deficiency; it may never supply the deficiency predicate itself. When a deficiency predicate is asserted but completion fails, the unit's content is indeterminable → UNCERTAIN; it is never reconstructed into GAP and never quietly re-filed as OTHER.
4. **Function separates the prospective from the positional.** A prior-knowledge deficiency positioning the present research is GAP; work assigned beyond the present study is FUTURE_RESEARCH — and a prospective recommendation is FUTURE_RESEARCH whether or not any deficiency is asserted.
5. **Segment before classifying.** One proposition unit receives exactly one class; mixed sentences yield multiple units (Protocol 29.4-A owns the mechanics); no unit is forced into a class to cover a neighbor.
6. **Hedges signal, never decide.** "Little/few/limited/unclear/rarely/mixed" are cues; classification follows the subject and target of the predicate, not the lexeme (the cue registry itself is Step-7 property).
7. **Citation-independent.** An uncited explicit deficiency can be GAP; citation presence, absence, and support are irrelevant to boundary classification.
8. **Truth-independent.** Classification certifies that the manuscript *asserts* a gap — never that the gap exists, the literature is sparse, the claim is novel, the citation supports it, the gap matters, or the study fills it.
9. **Section is a tie-breaker between licensed readings, never evidence.** Section location can never satisfy positioning relevance (G5) and never overrides semantic function; it may only break a genuine tie between two readings each already licensed by semantic/discourse evidence.
10. **Abstain narrowly; abstain single-valuedly.** UNCERTAIN fires only on the three named triggers; combined labels ("MOTIVATION/OTHER") do not exist as outputs anywhere — including for capability/world-deficit statements. Coercion and dumping are both errors.

---

## 38.2 Closed class definitions

| Class | Definition | Deficiency target | Discourse function | Includes | Excludes |
|---|---|---|---|---|---|
| **GAP** | Explicit, source-grounded **assertion** of a deficiency in prior knowledge / understanding / evidence / theory / method-as-warrant / research–practice alignment, functioning as positioning for the present research | Prior knowledge or an existing knowledge structure (incl. its assumptions, internal conflicts, methodological warrant, and the research–practice knowledge relationship) | Positioning (incl. restatements of an earlier positioning gap) | Empirical, theoretical, methodological deficiencies; assumption challenges; conflicting-evidence assertions; alignment/disconnect assertions; uncited deficiencies | Reconstruction of any kind; presupposed/referenced deficiencies; world/practitioner-capability deficits; present-study limits; prospective assignments |
| **MOTIVATION** | Assertion of importance, urgency, problem-status, stakes, prevalence-as-problem, or need for world action | External world / practitioner capability (or none) | Establishes that the topic matters | Problem framing; costs, trends, stakes; capability deficits when problem-framed in the unit or its immediate discourse frame | Any asserted prior-knowledge deficiency; neutral description (→ OTHER) |
| **OWN_LIMITATION** | Deficiency attributed to the present study's data, design, measurement, sample, analysis, scope, or conclusions | The present study | Qualifies the present study | "Our design cannot…"; "This study is limited by…" | Deficiencies attributed to prior literature |
| **FUTURE_RESEARCH** | A research need, recommendation, invitation, next step, or question explicitly assigned to subsequent/future research beyond the present study — with or without any asserted deficiency | Prospective (post-study), or none | Opens work beyond the present study | "Future research should…"; "Subsequent studies could…"; needs newly raised by present findings | Restatements of an earlier positioning gap (→ GAP); the paper's own remaining sections |
| **CONTRIBUTION** | Assertion of what the present study adds, provides, develops, demonstrates, extends, addresses, or is first to do | None (an addition/action claim) | Claims the study's yield | First-study claims; novel-context claims; extensions; measures; typologies; gap-addressing claims ("we address this gap") | Any conversion into an implied or referenced gap |
| **OTHER** | Controlled residual: relevant material asserting no deficiency and carrying no other class's function — including neutral world-state description, bare capability/world-deficit statements without mattering function, and positioning-irrelevant knowledge deficiencies (BR-OTH-5) | None / descriptive | Background, description, report | Literature description; established facts; theory description; chronology; RQs and objectives as such; neutral prevalence statements; unlinked deficiencies | Parking ambiguity (that is UNCERTAIN misuse) |
| **UNCERTAIN** | The frozen rules genuinely underdetermine the class for this unit | — | — | Triggers T1/T2/T3 only (38.11) | Difficulty, rarity, hedging, missing citation, poor grammar; combined labels |

---

## 38.3 GAP necessary conditions (all required; jointly sufficient)

- **G1 — Unit.** An independently identified proposition unit exists (segmentation owned by Protocol 29.4-A / Step 11).
- **G2 — Asserted deficiency predicate.** The unit **asserts** a deficiency (absence, insufficiency, unclarity, untestedness, constraint, internal conflict, disconnection, challenge): the deficiency is what the unit predicates — existentially, copularly, or predicatively ("there is little evidence on X"; "evidence is lacking"; "prior findings conflict"). A deficiency-denoting noun phrase in argument position within a unit predicating something else ("by addressing **the lack of evidence on X**, we contribute…") does not satisfy G2 (BR-CROSS-13). Step 6 later maps deficiency families to relations; here only asserted presence matters.
- **G3 — Prior-knowledge target.** The target is prior knowledge or an existing knowledge structure — what is known, understood, evidenced, explained, tested, measured, connected, or assumed — **including the relationship/alignment between research knowledge and practice** (BR-GAP-12). Not the external world, **not practitioner/world capability as such** (BR-CROSS-14), not the present study. Method counts only as knowledge warrant ("prior methods leave X unknown/constrained"), never as mere practice difference.
- **G4 — Source grounding.** The assertion is grounded in manuscript wording: fully in the unit (`explicit`) or completable by pure linguistic completion (`context_supported`, 38.4). **An asserted deficiency whose completion fails does not satisfy G4 — and does not fall through to Route B: it is UNCERTAIN(T2b)** (38.4, 38.15 D3).
- **G5 — Positioning function.** Source-grounded evidence connects the deficiency to the present study's positioning: **(A)** explicit discourse linkage, or **(B) proposition-level alignment** — the proposition the unit asserts deficient corresponds, at the level of the question/relationship/phenomenon-aspect, to the manuscript's explicitly stated focus/purpose/RQ (38.14). **Topical overlap alone — a shared entity, term, or construct mention — never satisfies G5. Section location never satisfies G5.** Closing-section restatements of an earlier positioning gap satisfy G5 through that earlier gap's linkage, at proposition level (BR-FUT-2).
- **G6 — Not the present study.** The deficiency is not attributed to the present study (else OWN_LIMITATION).
- **G7 — Not a prospective assignment.** The unit is not a recommendation/next step assigned beyond the present study (else FUTURE_RESEARCH via BR-FUT-1/4).

Failure routing: G2 fails or is only referentially present → Route B (§38.15). G3 world/capability target → Route B mattering test. G4 completion failure → UNCERTAIN(T2b). G5 linkage clearly absent → OTHER (BR-OTH-5). Indeterminacy at G2/G3/G5 → UNCERTAIN (T2a/T1/T3).

---

## 38.4 Explicit vs context-supported boundary

- **Explicit (BR-GAP-5).** The unit's own wording contains the deficiency predicate and its arguments sufficiently to assert the deficiency. "Little is known about X." → explicit.
- **Context-supported (BR-GAP-6).** The deficiency predicate is in the unit; local co-text is needed only to resolve *anaphora* ("These mechanisms remain unexplored" — the antecedent supplies the referent), *ellipsis*, *omitted arguments*, or *referential dependency*. The completion set is contract-fixed; nothing pragmatic is in it.
- **Failure branch (procedural).** When the deficiency predicate is asserted but its arguments cannot be recovered by permitted completion (no antecedent anywhere; unresolvable ellipsis — "Questions remain." with no recoverable question set), the unit is **UNCERTAIN(T2b)**: the assertion is real, its content indeterminable. This is distinct from the *pragmatic* case, where no deficiency predicate exists in the text at all — that case, and only that case, routes to Route B, and any GAP emitted from it is a Class-A critical error.
- **Hard line (BR-CROSS-2).** Context may never supply the deficiency predicate. "Prior work documented X. We examine X in SMEs." — no unit asserts a deficiency; nothing here is GAP, whatever the paragraph implies.
- Resolving what a nominal like "this gap" **refers to** is completion; it establishes reference, never assertion — the referential unit still classifies by its own predication (BR-CROSS-13).
- No third explicitness form exists; `inferred`/`reconstructed` are contract-prohibited.

---

## 38.5 Prohibited reconstruction (BR-CROSS-1)

None of the following creates a GAP, alone or combined, absent a separately **asserted** prior-knowledge deficiency:

| Source | Example | Class |
|---|---|---|
| Objective | "We examine X in SMEs." | OTHER |
| RQ | "How does X influence Y?" | OTHER |
| New method | "We use longitudinal data." | OTHER |
| Contribution claim | "We provide the first causal evidence on X." | CONTRIBUTION |
| Untested-by-us | "We test a previously untested mechanism." | CONTRIBUTION |
| New context | "We are the first to study X in Spain." | CONTRIBUTION |
| Imported theory | "We draw on theory developed in sociology." | OTHER |
| Discussion adds-knowledge | "Our results add to knowledge on X." | CONTRIBUTION |
| Gap reference | "We address this gap." | CONTRIBUTION |
| Future-research recommendation | "Future research should examine X." | FUTURE_RESEARCH |
| Practitioner knowledge deficit | "Managers do not understand X." (bare, no mattering frame) | **OTHER** — frozen default; problem-framed variants ("…, which undermines adoption efforts") → MOTIVATION (BR-CROSS-14/BR-MOT-3); indeterminate → UNCERTAIN(T3) |

Worked pair (frozen): "We examine X in SMEs." → not GAP. "Little is known about X in SMEs. We therefore examine…" → first unit GAP (G1–G7), second unit OTHER/objective. Emitting a GAP from any left-column source — including a bare gap-reference nominal — is a Step-3 **Class-A critical error** (invented gap / pragmatic-inference emission), not an ordinary misclassification.

---

## 38.6 GAP vs MOTIVATION

**BR-MOT-1.** MOTIVATION asserts that a phenomenon matters (importance, prevalence-as-problem, cost, urgency, stakes) or that the *world* needs action. GAP asserts what is deficient in *knowledge about* it. Test: does the deficiency/mattering attach to knowledge/research/evidence/understanding, or to the phenomenon itself?

- "Employee burnout is a growing organizational problem." → MOTIVATION.
- "Despite its importance, little is known about how burnout affects turnover." → GAP (the concessive importance wording is preserved in the proposition; it does not split off unless it is a separate unit).
- Mixed sentence — "Burnout is increasing, yet little is known about its effect on retention." → two units: MOTIVATION + GAP (38.13).
- World-deficit statements resolve **single-valuedly**: with problem/urgency/stakes function asserted in the unit or its immediate discourse frame → MOTIVATION; as neutral description → OTHER; genuinely indeterminate → UNCERTAIN(T3). "Few firms implement X, a persistent implementation problem." → MOTIVATION; "Few firms implement X." in neutral background → OTHER (BR-MOT-3, BR-CROSS-5/6).

---

## 38.7 GAP vs OWN_LIMITATION

**BR-LIM-1.** Target decides: a deficiency attributed to the present study → OWN_LIMITATION, even when it verbatim-echoes a literature-wide gap. **BR-LIM-2.** A deficiency attributed to prior research/literature/existing studies → GAP path (G3), including "A limitation of existing research is its reliance on self-reports, leaving actual behavior unmeasured" — limitation-lexis does not decide (38.12-L).

- "Our cross-sectional design does not establish causality." → OWN_LIMITATION.
- "Existing cross-sectional studies cannot establish whether X causes Y." → GAP (methodological warrant deficiency).
- **BR-LIM-3.** Ambiguous referents ("this study is limited…", "this work…", "these studies…") resolve by ordinary anaphora against local co-text — linguistic completion, permitted. If the referent (present paper vs reviewed stream) is genuinely unresolvable → UNCERTAIN(T1), never a default.

---

## 38.8 GAP vs FUTURE_RESEARCH

**Two ways into FUTURE_RESEARCH — frozen:**

- **BR-FUT-1 (deficiency-anchored, Route A).** A deficiency/new question explicitly **opened by the present study** ("Whether these effects persist over time remains for future studies"; "a question our findings newly raise") → FUTURE_RESEARCH. The epistemic anchor — pre-study knowledge state vs post-study opening — decides against GAP.
- **BR-FUT-4 (prospective assignment, Route B).** An explicit prospective recommendation, invitation, next-step statement, or question **assigned to subsequent/future research beyond the present study** is FUTURE_RESEARCH **even when it asserts no current deficiency**. "Future research should examine X." → FUTURE_RESEARCH. "Subsequent studies could test X." → FUTURE_RESEARCH. "An important next step is to examine X." → FUTURE_RESEARCH when the step is explicitly assigned beyond the present study; the paper's own remaining sections ("In the next section, we examine X.") are not FUTURE_RESEARCH. No GAP is inferred from any of these.
- **BR-FUT-2 (restatement carve-out, proposition-level).** A closing-section unit that (i) asserts a prior-knowledge deficiency and (ii) restates, at proposition level, an earlier positioning gap — presenting it as the deficiency the study addressed or that persists — → boundary class **GAP** (a restatement candidate; whether it merges with the earlier gap is Step-9's decision, not made here). A topic-only echo is not a restatement candidate. A genuinely new post-study need → FUTURE_RESEARCH.
- **BR-FUT-3 (need-for-research).** "There is a need for research on X…" — with an asserted deficiency and positioning linkage → GAP; as a prospective assignment (incl. post-study anchor) → FUTURE_RESEARCH; bare, unlinked, unanchored → UNCERTAIN(T3). The word "need" never decides.

Section titles never decide alone (principle 9); anchor, assignment, and proposition-level co-reference do.

---

## 38.9 GAP vs CONTRIBUTION

**BR-CON-1.** CONTRIBUTION asserts the study's yield. **BR-CON-5 (hard rule).** A contribution may presuppose a gap; it never *creates* one. No implication path exists from any contribution claim to a GAP.

- "We extend theory X to remote work." → CONTRIBUTION. Do NOT derive "Theory X has not been applied to remote work."
- "Theory X has rarely been applied to remote work." → GAP; "We therefore extend theory X to remote work." → CONTRIBUTION. Two units.
- **BR-CON-2 (frozen).** "This is the first study to examine X." → CONTRIBUTION; the pragmatic paraphrase "no prior study examined X" is prohibited reconstruction. **BR-CON-3 (frozen).** Novel-context claims ("first to study X in Spain"; "we introduce X to context Y") → CONTRIBUTION; no contextual-knowledge-absence gap is inferred.
- **BR-CON-4 (presupposition rule).** Contribution language containing a deficiency-**denoting nominal** does **not** spawn a GAP unit: "By addressing the lack of evidence on X, we contribute…" → **CONTRIBUTION only**; the nominal is a source-grounded reference/presupposition inside the contribution proposition, not an assertion (BR-CROSS-13). A GAP unit exists only where the deficiency is independently **asserted**: "There is a lack of evidence on X. We address this gap." → GAP (first unit) + CONTRIBUTION (second unit; "this gap" refers back — whether that reference is a restatement/identity link of the first GAP is Step-9 property, not a new GAP). "We address this gap." standing alone → CONTRIBUTION; if an earlier explicit GAP exists, it remains the GAP object.

---

## 38.10 GAP vs OTHER

**BR-OTH-1.** OTHER is a controlled residual: positioning-adjacent material asserting no deficiency and carrying no other class's function. It is not an ambiguity bin.

- **BR-OTH-2.** Literature description without deficiency: "Prior studies have examined X using surveys." → OTHER.
- **BR-OTH-3.** Established facts and theory description: "X is associated with Y."; "Agency theory assumes managers act opportunistically." → OTHER — unless a separate unit challenges the assumption (38.12-A).
- **BR-OTH-4.** Chronology/background: "Research on X emerged in the 1980s." → OTHER. RQ and objective units as such → OTHER (38.12-Q/O).
- **BR-OTH-5 (positioning-irrelevant deficiency).** A genuine prior-knowledge deficiency whose positioning linkage is **clearly absent** under 38.14-A/B — unrelated literature stream, disjoint proposition, no discourse link — is **OTHER**, *in any section, including Introduction, Literature Review, and Theory*, and **including when it shares a topic word with the study** (proposition-level non-alignment, 38.14-B). "Prior research has not examined pricing in healthcare. This study investigates employee motivation." → first unit OTHER. Linkage merely *indeterminate* (not clearly absent) → UNCERTAIN(T3), never a silent OTHER.
- Neutral world-state description without mattering function → OTHER; problem-framed → MOTIVATION; one class always (BR-MOT-3).

---

## 38.11 UNCERTAIN rules

**BR-UNC-1 (the only three triggers, legal exactly when, after applying every rule in this book):**
- **T1 — Target-indeterminate:** whether the deficiency targets prior knowledge, the present study, or the world/practitioner capability cannot be established (e.g., unresolvable "this work"; "attention" with unrecoverable agent).
- **T2 — Assertion-or-content-indeterminate:** either **(a)** whether the unit asserts a deficiency at all (vs pure description, presupposition, or mere reference) cannot be established, or **(b)** a deficiency is asserted but its propositional content cannot be established because permitted linguistic completion fails (unrecoverable antecedent; unresolvable ellipsis). Case (b) is the grounding-failure exit of D3.
- **T3 — Function-indeterminate:** the unit's discourse function among its surviving candidate classes — positioning vs prospective vs mattering vs neutral description (any competing subset of GAP / FUTURE_RESEARCH / MOTIVATION / OTHER) — cannot be established, and PR-4's constrained tie-break does not lawfully apply.

**BR-UNC-2.** UNCERTAIN is NOT: low confidence, hard wording, poor grammar, unusual phrasing, rare construction, missing citation, or annotator disagreement (disagreement is adjudicated, not classified). Annotator `confident/uncertain` metadata lives in Step-3 annotation records; the class stays one of the seven.
**BR-UNC-3.** Every UNCERTAIN outcome records its trigger (T1/T2/T3) and the unit's **actual surviving competing classes** (≥2) — these populate the Schema `uncertainty` block (`competing_boundary_states`, `review_trigger_code`), which the State Machine routes to boundary review. Competitor sets are **item-specific**: they are whichever classes remain live for that unit given its content and context after all rules; **no trigger has a canonical competitor set** (the {GAP, OTHER} pairs recorded on U07/A11/A12 follow from those items' stipulated contexts, not from T2b itself — a grounding-failure unit elsewhere may survive with a different set). No score or probability exists anywhere; no combined labels exist.

---

## 38.12 Special constructions

- **A — Assumption challenge (BR-GAP-10).** "Previous theories assume X, but this assumption is mistaken." → GAP (a challenge to an existing knowledge artifact). "Theory X assumes bounded rationality." → OTHER (description). "The assumption of bounded rationality fails in this setting." → GAP. No relation/kind assigned here.
- **M — Prior-method weakness (BR-GAP-9).** GAP only when prior methodological practice is asserted to leave something unknown/untested/constrained: "Existing studies rely on cross-sectional data, leaving temporal dynamics unexamined." → GAP. "We use longitudinal data." → OTHER. "Most studies use cross-sectional surveys; we instead employ panel data." → OTHER + CONTRIBUTION — method *difference* is never a gap.
- **C — Conflicting evidence (BR-GAP-11).** "Prior findings on X are inconsistent/mixed/do not agree." → GAP (internal conflict of the knowledge base is a knowledge deficiency).
- **F — First-study (BR-CON-2).** → CONTRIBUTION; frozen; no implication path.
- **N — Novel context (BR-CON-3).** → CONTRIBUTION; frozen.
- **Q — Research questions (BR-CROSS-8).** "How does X influence Y?" → OTHER. "It remains unclear how X influences Y." → GAP (given G5). "We therefore ask: how does X influence Y?" → the RQ stays OTHER; any preceding explicit deficiency is its own GAP unit.
- **O — Objectives (BR-CROSS-8).** "This study aims to examine X." → OTHER. "Because little is known about X, this study examines X." → GAP unit + OTHER unit (segmented).
- **K — Contribution-with-deficiency (BR-CON-4).** Asserted deficiency → separate GAP unit; nominal reference → CONTRIBUTION only.
- **P — Deficiency nominals (BR-CROSS-13).** "the gap", "this gap", "the lack of evidence", "the limited literature", "the unanswered question", "the underexplored issue": deficiency-denoting NPs classify **nothing by themselves**. Assertion test: is the deficiency the unit's predication (existential "there is…", copular "evidence is scarce/lacking", predicative "X remains unexplored") — or an argument inside another predication ("addressing…", "motivated by…", "given…")? Only the former satisfies G2. Reference to an earlier explicit GAP leaves that GAP as the object; the reference's identity status is Step-9 property. General parsing mechanics are not defined here — only this semantic boundary.
- **L — Limitation lexis (BR-LIM-1/2).** "limitation/shortcoming/weakness/constraint" classify by *target*, never by lexeme: of our study → OWN_LIMITATION; of existing research, framed as a deficiency in knowledge or its warrant → GAP.
- **R — Future-research language (BR-FUT-1/2/4).** Two routes per 38.8; prospective assignments need no deficiency; restatements are proposition-level.
- **D — "Need" (BR-FUT-3 / BR-MOT-2).** "There is a need for stronger cybersecurity regulation." → **MOTIVATION** (world-action need is mattering function). "Regulation differs across jurisdictions." → OTHER. Need-for-research per BR-FUT-3.
- **X — "Lack" (BR-CROSS-6).** Target test: "The literature lacks evidence on X." → GAP path. "Firms lack the resources to absorb such shocks, leaving supply chains exposed." → MOTIVATION. "There is a lack of coordination between departments." (bare, neutral) → **OTHER**; with asserted stakes ("…, a costly failure mode") → MOTIVATION. One class always.
- **H — "Little/few/limited…" (BR-CROSS-5).** Subject test: knowledge-referring subject (studies, research, evidence, understanding, attention-by-scholars) → GAP-relevant; world-referring subject (firms, people, cases) → not. "Few studies examine blockchain adoption." → GAP path. "Only 12% of firms use X." [neutral] → OTHER; "Only 12% of firms use X, creating an urgent implementation problem." → MOTIVATION.
- **G — Negation (BR-CROSS-7).** Negated research/knowledge state → GAP-relevant: "No studies have examined X." → GAP (given G5). Negated empirical claim → OTHER: "X does not affect Y." Negated agreement → GAP: "Prior studies do not agree on X."
- **W — Practitioner/world knowledge (BR-CROSS-14 / BR-GAP-12).** Capability deficits ("Managers do not understand X"; "Practitioners lack knowledge of X"; "Firms do not know how to implement X") are never GAP, whatever knowledge-lexis they contain. Single-class resolution: **bare/neutral → OTHER** (frozen default); **problem-framed → MOTIVATION** — where the mattering function is asserted in the unit *or established by its immediate discourse frame* (a function reading over existing text; no propositional content is added); **indeterminate → UNCERTAIN(T3)**. By contrast: "Existing research does not address the problems managers face." / "Evidence on X is disconnected from current managerial practice." / "Academic understanding of X has not translated into practice." / "Research and practice remain poorly aligned on X." → **GAP path** (BR-GAP-12): the asserted deficiency targets the relationship/alignment between research knowledge and practice — a knowledge-structure target. What Step 6 later maps such a GAP to is not decided here.

---

## 38.13 Mixed / multi-proposition treatment (BR-CROSS-3/4/12)

One sentence may hold multiple boundary units; each unit gets exactly one class; classes coexist at sentence level, never within one unit. Contrastive connectives (*although, despite, however, yet, while, whereas, but*) typically join a known/important state with a deficiency: classify each side by its own assertion — "Although X is well studied, little is known about Y." → OTHER + GAP. "Although X is important, few firms implement it." → unit 1 MOTIVATION; unit 2 **MOTIVATION** — the concessive frame problem-frames the implementation deficit (discourse-frame mattering per 38.12-W); the same second unit in isolated neutral prose → OTHER. No GAP either way; no combined label anywhere. Segmentation mechanics are owned by Protocol 29.4-A / Step 11; this rulebook only requires that classification respect the delivered units and never force one class across heterogeneous content. If a truly unsegmentable unit carries two live classes after all rules → UNCERTAIN with both competitors listed (BR-UNC-3), except that an asserted deficiency predicate inside the unit outranks co-present importance wording (PR-3).

---

## 38.14 Positioning relevance (BR-GAP-4)

G5 is satisfied **only** by source-grounded evidence connecting the deficiency to the present study's positioning:

- **A — Explicit discourse linkage:** *therefore, to address this gap, accordingly, this motivates our study, we therefore examine…*, or semantically equivalent explicit discourse structure between the deficiency unit and the study's stated focus/purpose/RQ/objective. No specific lexical cue is required.
- **B — Proposition-level alignment:** the proposition asserted deficient and the study's explicitly stated focus/purpose/RQ concern the **same question, relationship, or phenomenon-aspect** — established by surface co-reference of the *propositional content*, not merely of an entity. **Shared mention of a construct, term, or topic is insufficient:** "Little is known about the historical development of engagement measurement" does not align with a stated focus of "how engagement affects retention," despite the shared construct. Containment counts: a deficiency proposition that is a directly constitutive part of the stated focus's proposition (or vice versa, stated as such) aligns.

**Section location is not evidence.** A deficiency in an Introduction, Literature Review, or Theory section with neither A nor B is **OTHER** when non-alignment is clear (BR-OTH-5) and **UNCERTAIN(T3)** when alignment is indeterminate. Prohibited as always: deriving relevance from methods, contributions, study design, plausible reviewer reasoning, or any downstream inference. Restatements inherit G5 from the earlier gap's linkage, at proposition level (BR-FUT-2).

---

## 38.15 Decision procedure (deterministic; every branch terminates in exactly one of the seven classes)

Ordering rationale: the assertion test runs first (kills nominal-reference GAPs at the door); the target test precedes class competition (kills OWN_LIMITATION leakage — a present-study limitation echoing a literature gap must never reach the positioning test); grounding precedes function (kills pragmatic GAPs, and gives asserted-but-ungroundable units their UNCERTAIN exit before any function reading); the prospective-assignment branch is first in the no-deficiency route (FUTURE_RESEARCH must not require a deficiency, and prospective wording must not leak into CONTRIBUTION); yield precedes mattering (contribution claims with importance flavor stay CONTRIBUTION).

```text
D0  A proposition unit exists (delivered by segmentation). If none → no decision.

D1  ASSERTION TEST (BR-GAP-2 + BR-CROSS-13): is a deficiency the unit's own predication?
    (Deficiency-denoting NPs in argument position do NOT count; they are references.)
      YES → ROUTE A (D2) · NO → ROUTE B (D6) · indeterminable → UNCERTAIN (T2a)

ROUTE A — DEFICIENCY ASSERTED
D2  TARGET (BR-GAP-3 / BR-GAP-12 / BR-CROSS-14 / BR-LIM-1):
      present study                                   → OWN_LIMITATION
      prior knowledge / knowledge structure /
        research–practice relationship                → D3
      external world / practitioner capability        → D6m (mattering test)
      indeterminable                                  → UNCERTAIN (T1)
D3  GROUNDING (BR-GAP-5/6, BR-CROSS-2) — four exits:
      explicit                                  → D4 (form: explicit)
      completion-only, completion SUCCEEDS      → D4 (form: context_supported)
      predicate asserted, completion FAILS      → UNCERTAIN (T2b) — never Route B,
                                                  never OTHER, never a reconstructed GAP
      re-analysis: no predicate in the text —
        deficiency only pragmatically available → ROUTE B (D6); emitting GAP here is Class-A
D4  FUNCTION (BR-GAP-4; BR-FUT-1/2; BR-OTH-5):
      positioning for present study (G5 via 38.14 A/B)        → GAP
      restatement of an earlier positioning gap
        (proposition-level, BR-FUT-2)                          → GAP (restatement candidate;
                                                                 identity = Step 9)
      newly opened post-study need (anchor test, BR-FUT-1)     → FUTURE_RESEARCH
      linkage clearly absent                                   → OTHER
      indeterminate after PR-4 tie-break                       → UNCERTAIN (T3)

ROUTE B — NO DEFICIENCY ASSERTED
D6  LITERAL FUNCTION, tested in order:
      explicit prospective recommendation/invitation/next step/question
        assigned to subsequent research beyond the present study (BR-FUT-4)  → FUTURE_RESEARCH
      present-study yield/addition/first/introduces/addresses
        ("we address this gap") (BR-CON-1..5)                                → CONTRIBUTION
      D6m: mattering function — importance/urgency/problem-status/stakes/
        need-for-world-action asserted in-unit or by immediate discourse
        frame (BR-MOT-1/2/3)                                                 → MOTIVATION
      otherwise relevant description/background/RQ/objective                 → OTHER
      function genuinely indeterminate among survivors                       → UNCERTAIN (T3)
```

The State Machine consumes the result directly: `BOUNDARY_RESULT(class, boundary_rulebook_version = A1E-BR-1.2, uncertainty block iff UNCERTAIN)`; the same procedure governs re-classification after `boundary_reopened` (State Machine v1.3), with the review findings as additional co-text.

---

## 38.16 Rule registry (complete; machine-referenceable; rationale codes cite these IDs)

| rule_id | Statement (operative core) | Positive conditions | Exclusions | Ex (+) | Ex (−) | Related |
|---|---|---|---|---|---|---|
| BR-GAP-1 | GAP ⟺ G1–G7 all hold | 38.3 | any G fails | G01 | P01-left | all BR-GAP-* |
| BR-GAP-2 | A deficiency must be **asserted** — the unit's own predication (existential/copular/predicative) | deficiency is what the unit predicates | nominal reference; implication; presupposition | "There is little evidence on X." | "addressing the lack of evidence, we…" | BR-CROSS-13 |
| BR-GAP-3 | Target = prior knowledge/structure, incl. warrant, assumptions, internal agreement, and the research–practice relationship | knowledge-referring target | world/practitioner capability; present study | G09 | "Managers lack knowledge of X." | BR-GAP-12, BR-CROSS-14, BR-LIM-1 |
| BR-GAP-4 | G5 by explicit discourse linkage (A) or **proposition-level alignment** (B) only; topical overlap alone and section location never suffice | 38.14-A/B | section presumption; entity-only overlap; downstream inference | G01, A13 | N01, N06 | BR-OTH-5, BR-CROSS-9, BR-FUT-2 |
| BR-GAP-5 | Explicit form | predicate + arguments in unit | — | "No studies examined X." | — | BR-GAP-6 |
| BR-GAP-6 | Context-supported form: completion of anaphora/ellipsis/omitted args/referential dependency only; **completion failure → UNCERTAIN(T2b)**, never Route B, never OTHER | recoverable antecedent | pragmatic supply of the predicate | G07 | A11 (no antecedent → UNCERTAIN) | BR-CROSS-2, BR-UNC-1 |
| BR-GAP-7 | Citation not required; support never judged | — | requiring/assessing citations | uncited G01 | — | principles 7/8 |
| BR-GAP-8 | Closing restatement of a positioning gap = GAP | BR-FUT-2 conditions | newly opened needs | "the evidence gap on X we addressed…" | "future work should test Z (new)" | BR-FUT-1/2 |
| BR-GAP-9 | Prior-method deficiency = GAP only via knowledge consequence | "…leaving X unexamined/constrained" | mere method difference | G05 | "We use panel data." | BR-CON-*, 38.12-M |
| BR-GAP-10 | Assumption challenge = GAP; description = OTHER | challenge predicate over artifact | bare description | "assumption fails" | "theory assumes X" | BR-OTH-3 |
| BR-GAP-11 | Asserted conflict in prior findings = GAP | "inconsistent/mixed/do not agree" over prior findings | conflicting world events | G04 | "markets are volatile" | — |
| BR-GAP-12 | Research–practice relationship/alignment deficiency = GAP-path target | disconnect/non-translation/misalignment between research knowledge and practice asserted | practitioner capability deficits | G15, A07 | "Managers do not understand X." | BR-CROSS-14 |
| BR-MOT-1 | Importance/prevalence-as-problem/urgency/stakes = MOTIVATION | world-facing mattering claims | any knowledge-deficiency predicate | M01 | G01 | BR-GAP-3 |
| BR-MOT-2 | Need-for-world-action = MOTIVATION (single class) | mattering function asserted | need-for-research (→ BR-FUT-3) | M04 | P15-right | BR-MOT-3 |
| BR-MOT-3 | MOTIVATION vs OTHER is single-valued: mattering function asserted in-unit **or established by the immediate discourse frame** (a function reading; no content added) → MOTIVATION; neutral → OTHER; indeterminate → UNCERTAIN(T3). Exactly one class, always | — | combined labels | A05, A08 | A06, O12, O13 | BR-CROSS-14, PR-10, BR-UNC-1(T3) |
| BR-LIM-1 | Present-study target ⇒ OWN_LIMITATION | attribution to our study/data/design | literature targets | L01 | G05 | BR-GAP-3, PR-1 |
| BR-LIM-2 | Literature-limitation with knowledge framing ⇒ GAP path | deficiency in prior knowledge/warrant | present-study attribution | G14 | L06 | BR-GAP-9 |
| BR-LIM-3 | Ambiguous referent → resolve by anaphora; unresolvable → UNCERTAIN(T1) | recoverable antecedent | defaulting either way | "this study" resolved | U01 | BR-UNC-1 |
| BR-FUT-1 | Post-study opened need = FUTURE_RESEARCH (Route A) | post-study anchor | pre-study positioning deficiency | F05 | G01 | BR-GAP-8 |
| BR-FUT-2 | Restatement carve-out at **proposition level**: the closing unit restates the earlier gap's proposition | proposition-level co-reference + persisting/addressed framing | new needs; topic-only echoes | 38.8 case | F05 | BR-GAP-8, BR-GAP-4 |
| BR-FUT-3 | "Need for research": asserted deficiency + G5 → GAP; prospective assignment → FUTURE_RESEARCH; bare/unanchored → UNCERTAIN(T3) | — | word-based classing | P15-right | U02 | BR-FUT-4, BR-MOT-2 |
| BR-FUT-4 | Explicit prospective recommendation/invitation/next-step/question assigned beyond the present study = FUTURE_RESEARCH, **with or without any asserted deficiency**; no GAP is inferred | prospective assignment explicit | the paper's own remaining sections; restatements (BR-FUT-2) | F01, F02, A01, A09-left | "We will examine X in Section 5." | BR-FUT-1/2 |
| BR-CON-1 | Study-yield assertions = CONTRIBUTION | adds/provides/develops/demonstrates/extends/first/introduces/addresses | conversion to GAP | C02 | — | BR-CON-5 |
| BR-CON-2 | First-study ⇒ CONTRIBUTION (frozen) | — | implied prior absence | C01 | P06-right | BR-CROSS-1 |
| BR-CON-3 | Novel-context ⇒ CONTRIBUTION (frozen) | — | implied contextual gap | C07 | P19-right | BR-CROSS-1 |
| BR-CON-4 | Deficiency **nominals** inside contribution language do not spawn GAP; only an independently asserted deficiency does | asserted deficiency → separate unit | presupposed nominal → CONTRIBUTION only | A04 (GAP + CONTRIBUTION) | A03 (CONTRIBUTION only) | BR-CROSS-13, BR-CROSS-3 |
| BR-CON-5 | No implication path contribution → GAP, ever | — | — | — | — | BR-CROSS-1 |
| BR-OTH-1 | OTHER = controlled residual, never an ambiguity bin | no deficiency, no other function | parking hard cases | O01 | U-cases | BR-UNC-2 |
| BR-OTH-2 | Literature description w/o deficiency = OTHER | — | asserted deficiency | O01 | G01 | — |
| BR-OTH-3 | Fact/theory description = OTHER | — | separate challenge unit | O03 | 38.12-A(+) | BR-GAP-10 |
| BR-OTH-4 | Chronology/background = OTHER | — | — | O04 | — | — |
| BR-OTH-5 | Unlinked knowledge deficiency = OTHER **in any section**, incl. entity-shared but proposition-non-aligned cases; indeterminate linkage = UNCERTAIN(T3) | G2–G4 hold; 38.14-A/B clearly fail | inventing relevance; section presumption | N01–N07, O09 | G01, A13 | BR-GAP-4 |
| BR-UNC-1 | UNCERTAIN ⟺ trigger T1 / T2 (assertion **or content** indeterminate) / T3 (function indeterminate among surviving classes), after all rules | 38.11 | any convenience use; combined labels | U01–U10, A11, A12 | hard-but-decidable cases | BR-MOT-3, principle 10 |
| BR-UNC-2 | UNCERTAIN ≠ difficulty/confidence/rarity | — | — | — | — | principle 10 |
| BR-UNC-3 | Record trigger + the unit's actual surviving competing classes (≥2; item-specific — no trigger has a canonical set) into the Schema uncertainty block | — | scores/probabilities; fixed per-trigger competitor sets | — | — | SM routing |
| BR-CROSS-1 | Reconstruction prohibited from the **eleven** sources (38.5) | — | — | 38.5 table | — | Class-A mapping |
| BR-CROSS-2 | Context completes, never creates; failed completion → UNCERTAIN(T2b) | completion set only | pragmatic predicate supply; demotion to OTHER | G07 | P01-left; A11 | BR-GAP-6 |
| BR-CROSS-3 | Segment-sensitive classification; one class per unit | — | forcing sentence-level class | P18-right | — | BR-CROSS-12 |
| BR-CROSS-4 | Contrastives: classify each side by its own assertion | — | whole-sentence GAP | 38.13 examples | — | BR-CROSS-3 |
| BR-CROSS-5 | Hedges: subject test decides, lexeme never | knowledge-referring subject | word-triggered classing | P02-right | P02-left | 38.12-H |
| BR-CROSS-6 | "Lack": target test | knowledge target | world target | P03-right | P03-left | BR-GAP-3 |
| BR-CROSS-7 | Negation: negated research/knowledge state vs negated empirical claim | — | — | P17-right | P17-left | BR-GAP-11 |
| BR-CROSS-8 | RQs and objectives are OTHER as such | — | RQ/objective-derived gaps | O-units in P04/P05 | — | BR-CROSS-1 |
| BR-CROSS-9 | Section = constrained tie-breaker between semantically **licensed** readings only (PR-4); never G5 evidence, never an override | exactly-two licensed survivors | section-as-evidence | PR-4 | N01 | BR-GAP-4 |
| BR-CROSS-10 | Contextual wording preserved in the proposition; never a scope structure, never an inference source | — | population/geo fields; context-derived gaps | G03 | "Research has focused on Europe" → GAP | Contract OD-3 |
| BR-CROSS-11 | Scientific truth/novelty/importance/support never assessed | — | — | — | — | principle 8 |
| BR-CROSS-12 | Exactly one class per proposition unit | — | multi-class units (→ segmentation or UNCERTAIN) | — | — | BR-CROSS-3 |
| BR-CROSS-13 | Deficiency-denoting NP ≠ deficiency assertion unless assertive force is independently established; references to an earlier GAP leave that GAP as the object (identity = Step 9) | assertion test 38.12-P | argument-position nominals as GAP | "There is a lack of evidence on X." | "We address this gap." | BR-GAP-2, BR-CON-4 |
| BR-CROSS-14 | Practitioner/world capability deficits are never GAP; resolve to exactly one of OTHER (bare default) / MOTIVATION (problem-framed, per BR-MOT-3) / UNCERTAIN(T3) | capability predication | alignment/disconnect assertions (→ BR-GAP-12) | O13 → OTHER; A05 → MOTIVATION | "poorly aligned on X" → GAP path | BR-GAP-12, BR-MOT-3, PR-9 |

---

## 38.17 Precedence / conflict rules (deterministic)

- **PR-0 (master).** The unit's **asserted semantic function** beats lexical cues, nominalized gap language, section titles, and pragmatic implication. All other precedence rules instantiate this.
- **PR-1 (target precedence).** Present-study attribution beats everything: a deficiency attributed to the present study is OWN_LIMITATION even when it verbatim-echoes a literature gap.
- **PR-2 (assertion over implication).** CONTRIBUTION / first-study / novel-context / RQ / objective units never convert into GAP; only a separately asserted deficiency unit can be GAP.
- **PR-3 (deficiency over importance).** Within one genuinely unsegmentable unit containing both a mattering claim and an asserted knowledge-deficiency predicate, the deficiency predicate controls → GAP, with the importance wording preserved in the proposition. MOTIVATION requires the absence of any knowledge-deficiency predicate.
- **PR-4 (function over section; section as constrained tie-breaker).** Semantic function markers (anchor, proposition-level co-reference, discourse links) always beat section location. Section may decide only when, after every rule, exactly two readings survive, **each independently licensed by semantic/discourse evidence**, and the section is function-strong for one of them: an explicitly titled Future-Research subsection → FUTURE_RESEARCH; an explicitly titled Limitations subsection → OWN_LIMITATION for present-study-referent ambiguity. Introduction/Literature Review/Theory carry **no** G5-conferring power; Discussion/Conclusion carry no prior. Tie-break conditions unmet → UNCERTAIN(T3).
- **PR-5 (OTHER vs UNCERTAIN).** OTHER requires a confident non-deficiency (or BR-OTH-5) reading; UNCERTAIN requires a named trigger. Neither absorbs the other's cases.
- **PR-6 (one class per unit).** Two live classes after all rules and PR-1..5 → first re-examine segmentation; if genuinely one unit → UNCERTAIN with competitors recorded. No blended or dual labels exist.
- **PR-7 (assertion over reference).** An asserted deficiency outranks any co-present nominal reference; a nominal reference alone never outranks the unit's own predication — "we address this gap" is a CONTRIBUTION predication regardless of the nominal.
- **PR-8 (prospective assignment).** An explicit assignment to subsequent research is FUTURE_RESEARCH and is never converted to GAP; a unit can be GAP only through its **own** asserted pre-study deficiency (Route A), never through prospective wording.
- **PR-9 (capability vs alignment).** What the deficiency **predicate targets** controls: capability of practitioners/world → non-GAP path; the research–practice knowledge relationship → GAP path. Lexical presence of "knowledge/understanding" decides nothing.
- **PR-10 (mattering vs description).** MOTIVATION requires an asserted mattering function, evaluated per BR-MOT-3 (in-unit or immediate discourse frame); its absence yields OTHER; genuine indeterminacy yields UNCERTAIN(T3). The default is frozen; no disjunctive residue can re-enter through this rule.

---

## 38.18 Adjudication guidance

| Class | Clear positive | Clear negative | Boundary case | UNCERTAIN trigger |
|---|---|---|---|---|
| GAP | "Little is known about X." (+G5) | "We examine X." | Literature-limitation phrasing (BR-LIM-2 vs L06) | T1/T2/T3 per 38.11 |
| MOTIVATION | "X is a growing problem." | "Little is known about X." | Need/prevalence statements — resolve by mattering function (BR-MOT-3) | T3 when mattering undecidable |
| OWN_LIMITATION | "Our design cannot…" | "Existing studies cannot…" | "This work is limited…" referent | T1 when referent unresolvable |
| FUTURE_RESEARCH | "Future research should test Z." | Intro-positioning gap | Closing restatement (BR-FUT-2) | T3 when anchor undecidable |
| CONTRIBUTION | "We provide the first causal evidence." | "No prior study examined X." | Deficiency nominal inside contribution syntax (BR-CON-4) | — (apply the assertion test) |
| OTHER | "Prior studies used surveys." | Any asserted, linked deficiency | Positioning-irrelevant deficiency (BR-OTH-5) | T2 description-vs-deficiency |
| UNCERTAIN | U01–U10, A11–A12 patterns | Hard-but-decidable wording | — | Named triggers only |

Annotator protocol notes: segment first (accept delivered units; propose splits via the Protocol's proposal mechanism, never by dual-labeling); run the target test before anything else; never reconstruct; record rule_ids as rationale codes on every non-obvious decision (they are the re-annotation index); mark `confident/uncertain` as metadata — it never changes the class; when tempted to write a note explaining an inference, the classification is probably wrong (PR-0).

Specific instructions:
- **A — Gap references.** "This gap" / "the lack of evidence" as nominals: run the assertion test (38.12-P). Argument position → no GAP unit; classify the unit's own predication (usually CONTRIBUTION). If it plausibly refers to an earlier explicit GAP, note the reference in the rationale — the identity question is Step-9's.
- **B — Prospective recommendations without deficiency.** Classify FUTURE_RESEARCH under BR-FUT-4; do not hunt for an implicit gap; do not mark UNCERTAIN merely because no deficiency exists.
- **C — Unlinked deficiencies in any section.** Apply 38.14-A/B strictly at the *proposition* level; a shared construct name is not linkage; the section confers nothing. Clearly non-aligned → OTHER (cite BR-OTH-5/BR-GAP-4); indeterminate → UNCERTAIN(T3) with {GAP, OTHER} recorded.
- **D — Practitioner vs alignment.** Ask what the predicate targets: who lacks the knowledge (managers/firms → capability → non-GAP path) versus what fails to connect (research↔practice → GAP path). Quote the predicate in the rationale.
- **E — MOTIVATION vs neutral OTHER.** Ask whether mattering/problem/urgency is *asserted* (in-unit or by the immediate discourse frame) or merely inferable from topic salience. Asserted → MOTIVATION; neutral description → OTHER; genuinely undecidable → UNCERTAIN(T3), never a slash label.
- **F — Grounding failure.** When a deficiency predicate is asserted but its referent set cannot be recovered ("Questions remain."; document-initial "These mechanisms…"), record UNCERTAIN(T2b) with the unit's **actual surviving competing classes**, determined per BR-UNC-3 — item-specific, never a fixed set ({GAP, OTHER} happens to be the surviving pair for U07/A11/A12 under their stipulated contexts; the same construction in, e.g., a Limitations paragraph may survive with a different set). Do not classify the unit by its residual surface function.

---

## 38.19 Step-3 error mapping

| Boundary mistake | Step-3 treatment |
|---|---|
| GAP↔MOTIVATION, GAP↔CONTRIBUTION, GAP↔FUTURE_RESEARCH, GAP↔OWN_LIMITATION, GAP↔OTHER confusions (both directions) | `E-BOUNDARY` (7-class confusion matrix; GAP-FP and GAP-FN reported separately) |
| Non-GAP reconstructed as GAP (objective/RQ/contribution/first-study/novel-context/gap-reference/prospective-recommendation/practitioner-deficit sources) | **Class-A critical** — invented gap (Protocol 29.11 A-1) + `E-BOUNDARY` |
| Pragmatic implication emitted as GAP / as `context_supported` | **Class-A critical** — pragmatic-inference emission (29.11 A-6) |
| UNCERTAIN used for difficulty; or coercion where a trigger held; or a grounding-failure unit forced into OTHER/GAP | `E-BOUNDARY` + abstention accounting (Protocol OI-P3); adjudication defect channel decides annotation-error vs rulebook-ambiguity |
| Context restriction absorbed while classifying (pre-empting object work) | flagged forward to `E-OBJECT-SCOPE` territory (Protocol taxonomy); boundary class itself per this book |
| Wrong class traceable to an ambiguous rule here | adjudication `defect_class: rulebook_ambiguity` citing the rule_id → this book's versioning queue (38.21) |

No replacement taxonomy is created; all counting, populations, and gates remain Protocol v1.2 property.

---

## 38.20 Semantic test suite (NORMATIVE for boundary class; no Step-6 relation/kind is assigned anywhere)

**G5 marking convention:** every GAP item establishes positioning relevance explicitly, in one of three forms: **(A)** a `Context:` line stating the present study's focus, with the deficiency proposition aligned to it; **(B)** inline discourse linkage, with segmentation shown; **(C)** the marker `[+POS]` = "stipulated: the manuscript's stated focus addresses, at proposition level, the same question/relationship/aspect the unit asserts deficient (BR-GAP-4-B)". No GAP label rests on topic sharing, section location, or on G2+G3 alone.

**GAP (15).**
G01 Context: "The present study investigates how X affects Y." · Unit: "Little is known about how X affects Y." → GAP (form A) · G02 "No studies have examined the adoption of X in supply chains." [+POS] · G03 "Evidence on X remains limited among frontline employees." [+POS] (context wording preserved; no scope field) · G04 "Prior findings on the X–Y link are inconsistent." [+POS] · G05 "Existing studies rely on cross-sectional data, leaving temporal dynamics unexamined." [+POS] · G06 "The assumption of stable preferences fails in digital markets." [+POS] · G07 "These mechanisms remain unexplored in distributed settings." [+POS] (antecedent present in co-text; context_supported) · G08 "It remains unclear how regulation shapes SME innovation; we therefore examine this question." → GAP + OTHER, segmented (form B) · G09 "The literature lacks evidence on long-term effects of X." [+POS] · G10 "Theories of institutional change cannot explain rapid platform collapse." [+POS] · G11 "Research has yet to test whether the model holds outside laboratory settings." [+POS] · G12 "How X influences Y has received scant scholarly attention." [+POS] · G13 "Despite two decades of work, we still do not understand why X persists." [+POS] · G14 "A key limitation of existing research is its reliance on self-reported outcomes, which leaves actual behavior unmeasured." [+POS] · G15 "Existing research on X is disconnected from current managerial practice." [+POS] (BR-GAP-12). (All uncited — BR-GAP-7.)

**G5 negative controls (7)** — asserted knowledge deficiency, linkage failed → **OTHER** (BR-OTH-5):
N01 [Introduction] "Little is known about healthcare pricing." — paper explicitly studies employee motivation; no link · N02 "Research on marine ecosystems has not addressed X." — paper studies executive compensation · N03 "Little is known about consumer trust in cryptocurrencies." — paper studies hospital staffing · N04 "The determinants of teacher attrition remain poorly understood." — paper studies semiconductor supply chains · N05 "Evidence on microplastic toxicity is scarce." — paper studies B2B branding · N06 Context: "The present study investigates how employee engagement affects retention." · Unit: "Little is known about the historical development of engagement measurement." → OTHER (shared construct, disjoint proposition) · N07 Context: "This study examines the effect of X on Y." · Unit: "Evidence on the antecedents of X is scarce." → OTHER (entity shared; proposition non-aligned). (With O09, eight controls exercise G2+G3 with failed G5.)

**MOTIVATION (10).**
M01 "Employee burnout is a growing organizational problem." · M02 "Cyberattacks cost firms billions annually." · M03 "SMEs account for most employment in Europe, making their resilience a first-order policy concern." (mattering asserted in-unit; the bare prevalence fact is O14) · M04 "There is a need for stronger cybersecurity regulation." (BR-MOT-2) · M05 "Understanding X is critical for managers." · M06 "Digital transformation is reshaping every industry." · M07 "Few firms implement circular-economy practices, a persistent implementation problem." · M08 "Firms lack the resources to absorb such shocks, leaving supply chains exposed." · M09 "The pandemic exposed the fragility of global supply chains." · M10 "Turnover among nurses has reached record levels."

**OWN_LIMITATION (10).**
L01 "Our cross-sectional design does not establish causality." · L02 "This study is limited by its single-country sample." · L03 "We did not measure long-term outcomes." · L04 "The self-report measures used here may inflate associations." · L05 "Our findings may not generalize beyond the studied platform." · L06 "A limitation of our study is reliance on archival data." · L07 "The small sample limits statistical power." · L08 "We could not rule out selection effects." · L09 "Our data end in 2023, preceding the policy change." · L10 "The present analysis does not distinguish subtypes of X."

**FUTURE_RESEARCH (10).**
F01 "Future research should examine whether X holds in Asia." · F02 "Subsequent studies could test the model with longitudinal data." · F03 "We encourage scholars to explore boundary conditions of this effect." · F04 "An important next step is to replicate these findings in field settings." · F05 "Research is needed on how the mechanism operates under scarcity, a question our findings newly raise." · F06 "Scholars might extend this framework to nonprofit contexts." · F07 "Further work should develop measures for the construct introduced here." · F08 "Whether these effects persist over time remains for future studies." · F09 "We invite research on the unintended consequences identified above." · F10 "Follow-up studies should test alternative explanations we could not exclude."
Reachability: F01–F04, F06, F07, F09, F10 via Route B / BR-FUT-4 (no deficiency required — F09's "we invite research" is a prospective invitation, not a deficiency assertion); F05, F08 via Route A / post-study anchor (BR-FUT-1: an unresolved question/need asserted as opened by the present study).

**CONTRIBUTION (10).**
C01 "This is the first study to examine X." (BR-CON-2) · C02 "We extend theory X to remote work." · C03 "Our study provides causal evidence on the X–Y relationship." · C04 "This research introduces the concept of Z." · C05 "We contribute a validated measure of X." · C06 "The study demonstrates that A moderates B." · C07 "We are the first to study X in Spain." (BR-CON-3) · C08 "Our findings advance understanding of X." · C09 "This paper develops a typology of X." · C10 "We test a previously untested mechanism." (BR-CROSS-1)

**OTHER (14).**
O01 "Prior studies have examined X using surveys." · O02 "X is positively associated with Y." · O03 "Agency theory assumes that managers act opportunistically." (BR-OTH-3) · O04 "Research on X emerged in the 1980s." · O05 "Smith (2020) found that X increases Y." · O06 "The construct X comprises three dimensions." · O07 "Several reviews have synthesized this literature." · O08 "Our sample consists of 214 firms." · O09 "Prior research has not examined pricing in healthcare." [paper on employee motivation; no discourse link] (BR-OTH-5) · O10 "X theory has been applied across many industries." · O11 "Regulation differs across jurisdictions." (neutral description; BR-MOT-3) · O12 "Only 12% of firms use X." [neutral descriptive context] · O13 "Managers do not understand X." [bare, isolated] → OTHER (frozen default; contrast A05) · O14 "SMEs account for most employment in Europe." [bare, neutral prevalence fact] → OTHER (BR-MOT-3; contrast M03).

**UNCERTAIN (10; trigger noted).**
U01 "This work is limited by its reliance on Western samples." [lit-review paragraph; referent unresolvable] — T1 {OWN_LIMITATION, GAP} · U02 "More research attention to X would be valuable." [mid-intro; no link, no anchor] — T3 {GAP, FUTURE_RESEARCH, MOTIVATION} · U03 "The field has not matured enough to answer such questions." — T2a {GAP, OTHER} · U04 "Our understanding of X is shaped mainly by case studies." — T2a {GAP, OTHER} · U05 "Little attention has been paid to implementation." [agent — scholars or firms — unrecoverable] — T1 {GAP, MOTIVATION} · U06 "It is time to revisit the foundations of X theory." — T3 {GAP, FUTURE_RESEARCH} · U07 "Questions remain." [no recoverable antecedent; completion fails; stipulated mid-manuscript positioning discourse] — **T2b** {GAP, OTHER} (item-specific survivors) · U08 "Existing approaches struggle with scalability." [approaches: literature methods vs deployed systems] — T1 {GAP, OTHER} · U09 "The evidence base is thin, though growing rapidly." [discussion opening; anchor indeterminate] — T3 {GAP, FUTURE_RESEARCH} · U10 "Whether X matters remains an open question in practice." [which knowledge the predicate targets is unrecoverable] — T1 {GAP, MOTIVATION}.

**Additional normative items (A-set).**
A01 "Future research should test X." → FUTURE_RESEARCH (BR-FUT-4; no deficiency) · A02 "We address this gap." → CONTRIBUTION (BR-CROSS-13; no new GAP; reference to any earlier GAP is Step-9 material) · A03 "By addressing the lack of evidence on X, we contribute a longitudinal analysis." → CONTRIBUTION only (BR-CON-4) · A04 "There is a lack of evidence on X. We address this gap." → GAP + CONTRIBUTION (two units; first asserts, second refers) · A05 "Managers do not understand X, which undermines adoption efforts." → MOTIVATION (capability deficit, problem-framed; BR-CROSS-14) · A06 "Managers' familiarity with X varies across sectors." → OTHER (neutral capability description) · A07 "Academic understanding of X has not translated into practice." [+POS] → GAP (BR-GAP-12) · A08 "Only 12% of firms use X, creating an urgent implementation problem." → MOTIVATION ‖ contrast O12 → OTHER · A09 "An important next step is to examine X." [assigned to future research in a Future-Research subsection] → FUTURE_RESEARCH ‖ "In the next section, we examine X." → OTHER (the paper's own plan) · A10 [Introduction] "Little is known about healthcare pricing. This study investigates employee motivation." → OTHER + OTHER (the disconnect shown in-text) · A11 "These mechanisms remain unexplored in distributed settings." [document-initial; **no antecedent anywhere**] → UNCERTAIN(T2b) {GAP, OTHER} (item-specific survivors) — contrast G07 · A12 "Several issues remain unresolved." [no recoverable issue set; stipulated mid-manuscript positioning discourse] → UNCERTAIN(T2b) {GAP, OTHER} (item-specific survivors) · A13 Context: "The present study investigates how employee engagement affects retention." · Unit: "Little is known about how employee engagement affects retention." → GAP (the proposition-level positive standard; contrast N06).

**Minimal pairs (20).**
P01 "We examine X in SMEs." → OTHER ‖ "Little is known about X in SMEs." [+POS] → GAP · P02 "Few firms use blockchain." → OTHER (neutral) ‖ "Few studies examine blockchain adoption." [+POS] → GAP · P03 "Firms lack resources." → OTHER (neutral; problem-framed variants → MOTIVATION) ‖ "The literature lacks evidence on X." [+POS] → GAP · P04 "How does X influence Y?" → OTHER ‖ "It remains unclear how X influences Y." [+POS] → GAP · P05 "This study aims to examine X." → OTHER ‖ "Because little is known about X, this study examines X." → GAP + OTHER (segmented) · P06 "This is the first study to examine X." → CONTRIBUTION ‖ "No prior study has examined X." [+POS] → GAP · P07 "We extend theory X to remote work." → CONTRIBUTION ‖ "Theory X has rarely been applied to remote work." [+POS] → GAP · P08 "Our cross-sectional design cannot establish causality." → OWN_LIMITATION ‖ "Existing cross-sectional studies cannot establish whether X causes Y." [+POS] → GAP · P09 "A limitation of our study is self-report reliance." → OWN_LIMITATION ‖ "A limitation of existing research is its reliance on self-reports, leaving behavior unmeasured." [+POS] → GAP · P10 "Future research should examine X in Asia." → FUTURE_RESEARCH ‖ "Little is known about whether these findings generalize to Asian firms." [intro, +POS] → GAP · P11 "Research has focused on Europe." → OTHER ‖ "Little is known about whether these effects hold beyond Europe." [+POS] → GAP · P12 "We study frontline employees." → OTHER ‖ "Evidence remains limited among frontline employees." [+POS] → GAP · P13 "Agency theory assumes opportunism." → OTHER ‖ "The assumption of opportunism fails in family firms." [+POS] → GAP · P14 "We use longitudinal data." → OTHER ‖ "Existing studies rely on cross-sectional data, leaving dynamics unexamined." [+POS] → GAP · P15 "There is a need for stronger regulation." → MOTIVATION ‖ "There is a need for research on how regulation affects SMEs, which prior work has not addressed." [+POS] → GAP · P16 "By addressing the lack of evidence on X, we contribute…" → CONTRIBUTION only ‖ "There is a lack of evidence on X. We address this gap." → GAP + CONTRIBUTION · P17 "X does not affect Y." → OTHER ‖ "Prior studies do not agree on whether X affects Y." [+POS] → GAP · P18 "Burnout is increasing." → MOTIVATION ‖ "Burnout is increasing, yet little is known about its effect on retention." [+POS] → MOTIVATION + GAP (segmented) · P19 "This research introduces X to context Y." → CONTRIBUTION ‖ "Knowledge of X in context Y is absent." [+POS] → GAP · P20 "Prior studies focus on large firms, and we extend this work to SMEs." → OTHER + CONTRIBUTION ‖ "Prior studies focus on large firms and say little about SMEs; we extend this work." → GAP + CONTRIBUTION.

**Coverage:** empirical (G01…), theoretical (G10, G06), methodological (G05, G14, P14), assumption challenge (G06, P13), conflicting evidence (G04, P17), population/context wording (G03, P11, P12), no-citation (all G), first-study (C01, P06), novel-context (C07, P19), RQ (P04), objectives (P05, O08-adjacent), future-research language (F-set, P10, A01, A09), contribution language (C-set, P16), prior-method limits (G05, G14), mixed sentences (P18, P20), anaphora (G07), ellipsis/failed completion (U07, A11, A12), pragmatic-only inference (C10, P01/P06 left sides), nominal reference (A02–A04, P16), section false positives (N01–N07, A10), practitioner vs alignment (A05–A07, G15, O13, U10), mattering vs neutral (A08/O12, O11, M03/O14, M07/M08), proposition-level alignment (A13 vs N06/N07).
**Consistency audit:** every expected class above is derivable from §38.15 as written; in particular, every F-item is reachable, every grounding-failure item has the T2b path, and no label rests on topic-sharing or section location.

---

## 38.21 Versioning / re-annotation policy

- **Version string:** `A1E-BR-1.2`, pinned in every `BOUNDARY_RESULT`, every gold record, and every rationale-code context (Protocol 29.12).
- **rule_id stability:** IDs are permanent; retired IDs are never reused; amendments version the rule text under the same ID; the change register below records lineage.
- **Change classes → re-annotation consequences** (executed through Protocol 29.12's rationale-code index): *clarifying amendment* (wording, added exemplars): selective re-adjudication of items citing the rule; *semantic narrowing/broadening of one rule:* re-adjudication of all items citing the rule plus the UNCERTAIN pool whose competing classes include the affected class; *class-boundary shift:* full boundary re-annotation of the affected strata; *new rule:* re-adjudication of the UNCERTAIN pool and of items carrying related defect findings; *rule retirement:* as semantic change of every dependent rule. Sealed cohorts are never relabeled in place (quarantine-and-replace, Protocol 29.6-T).
- **Version status:** no final gold exists (Protocol 29.13b has not run); pilot material annotated under any earlier boundary asset is re-adjudicated against `A1E-BR-1.2` before informing calibration design; sealed cohorts are unaffected because none exist.
- **Change register (provenance, non-operative).** v1.0→v1.1: FUTURE_RESEARCH made reachable without an asserted deficiency (BR-FUT-4; two-route procedure); asserted-vs-presupposed deficiency distinction (BR-CROSS-13; BR-CON-4 reversed; P16 reworked); section presumption deleted from G5; practitioner boundary closed (BR-CROSS-14/BR-GAP-12); single-valued outputs (BR-MOT-3; T3 generalized); G5-exercising suite with negative controls. v1.1→v1.2: D3 gained the grounding-failure exit → UNCERTAIN(T2b) (BR-GAP-6, BR-UNC-1, principle 3); G5-B tightened to proposition-level alignment (BR-GAP-4; BR-FUT-2; [+POS] re-anchored; N06/N07/A13 added); residual disjunctive outputs removed with frozen defaults (38.5 practitioner row; 38.12-W/X/H; 38.13 example; O13 added). v1.2 consolidation: the document was issued self-contained; no operative rule changed in consolidation. v1.2 final-issuance corrections (pre-freeze): F09 route attribution corrected to Route B/BR-FUT-4 (an invitation is not a deficiency assertion); M03 given explicit in-unit mattering framing, with the bare prevalence fact added as O14 — the M-set was re-audited under BR-MOT-3 and M03 was the only neutral-prevalence residue (M02/M05/M09/M10 assert stakes, criticality, exposure, or extremity in-unit); the fixed {GAP, OTHER} competitor set removed from T2b guidance — competitor sets are item-specific per BR-UNC-3 (instruction F, registry row, and U07/A11/A12 annotations updated).
- **Downstream dependency note.** Step 6 and subsequent components MUST pin the frozen Boundary Rulebook version they consume. Because Step 6 has not been frozen, no compatibility assertion about Step-6 rule content is made here. When Step 6 is produced, it must use `A1E-BR-1.2` as its normative Step-5 input.

---

## 38.22 Open decisions

- **OD-BR-2 (calibration-only).** The exemplar library for **proposition-level alignment** (what still counts as the "same question" under paraphrase; containment edge cases) is appended from pilot adjudications as clarifying amendments. The criterion itself is fixed; only its exemplar set grows.

Nothing else is deferred: the grounding-failure routing, the section rule, the practitioner boundary, the need/lack/first-study/novel-context defaults, the restatement carve-out, and the single-class defaults are all decided above. No Step-6/8/9 material was pulled forward to fill them. (The formerly open practitioner-knowledge decision is closed by BR-CROSS-14/BR-GAP-12.)

---

## 38.23 Freeze check

### Part A — Core checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| All seven boundary classes have exact definitions | PASS | 38.2; 38.6–38.11 |
| GAP requires an explicit prior-knowledge deficiency | PASS | G2+G3; BR-GAP-2/3; D1–D2 |
| GAP requires positioning relevance to the present study | PASS | G5; 38.14; BR-GAP-4; BR-OTH-5 |
| Context may complete but never create a gap | PASS | 38.4; BR-GAP-6/BR-CROSS-2; D3; A11/U07 route to UNCERTAIN, not GAP |
| Pragmatic reconstruction is prohibited | PASS | 38.5 (eleven sources); BR-CROSS-1; D3 pragmatic branch; Class-A mapping (38.19) |
| Objectives cannot create gaps | PASS | 38.5; BR-CROSS-8; P05 |
| RQs cannot create gaps | PASS | 38.5; BR-CROSS-8; P04 |
| Contributions cannot create gaps by implication or by nominal reference | PASS | BR-CON-4/5; BR-CROSS-13; PR-2/PR-7; P07/P16/A02–A04 |
| "First study" claims default to CONTRIBUTION | PASS | BR-CON-2; C01; P06 |
| Novel-context claims do not imply a gap | PASS | BR-CON-3; C07; P19 |
| Motivation is separated from knowledge deficiency | PASS | BR-MOT-1; PR-3; P02/P03/P18 |
| Present-study limitations are separated from prior-knowledge deficiencies | PASS | BR-LIM-1/2; PR-1; P08/P09; D2 ordering |
| Future research is separated from present-study positioning | PASS | BR-FUT-1/4; D4/D6; P10; A01/A09 |
| Restated prior gaps are not automatically FUTURE_RESEARCH | PASS | BR-FUT-2 (proposition-level); identity deferred to Step 9 |
| Prior literature description without deficiency is OTHER | PASS | BR-OTH-2; O01; P11/P12/P14 left sides |
| UNCERTAIN is genuine ambiguity, not low confidence | PASS | BR-UNC-1/2; three named triggers; U-set with triggers |
| Lack of citation does not prevent GAP classification | PASS | BR-GAP-7; all G-items uncited |
| Citation support is not judged | PASS | BR-GAP-7; principle 8; BR-CROSS-11 |
| Scope/context is not structurally extracted | PASS | BR-CROSS-10; G03/P11/P12; no scope inference path |
| Multiple proposition classes may coexist in one sentence | PASS | 38.13; BR-CROSS-3/4/12; P05/P16/P18/P20 |
| Rule precedence is deterministic | PASS | PR-0…PR-10; ties route to UNCERTAIN by rule |
| Rule IDs support annotation/adjudication version pinning | PASS | 38.16 complete registry; rationale codes = rule_ids; 38.21 change-class mapping |
| Step-6 relation/kind rules are not defined | PASS | G2 names deficiency families without mapping; suite carries no relation/kind labels |
| Step-8 object rules are not defined | PASS | No object extraction anywhere; scope flag routed via Protocol taxonomy (38.19) |
| Step-9 identity rules are not defined | PASS | BR-FUT-2/BR-CON-4 set boundary conditions only; identity explicitly deferred |
| Detection/signals are not defined | PASS | Cue lexemes never decide (BR-CROSS-5; principle 6); signal library = Step-7 property |
| Scientific truth/novelty/importance is not assessed | PASS | Principle 8; BR-CROSS-11; 38.2 exclusion columns |
| The State Machine can consume the boundary outcome directly | PASS | §38.15 output = one of seven + version + BR-UNC-3 uncertainty block = `BOUNDARY_RESULT` payload; `boundary_reopened` covered; every class producible (F-suite reachability shown) |
| Step-3 can evaluate the rulebook without conceptual redesign | PASS | Classes, triggers, rule_ids align with Protocol gold units, defect classes, rationale codes, E-BOUNDARY/Class-A mapping (38.19); suite usable as oracle material |

### Part B — Boundary-refinement checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| FUTURE_RESEARCH is reachable without an asserted deficiency | PASS | Route B first branch; BR-FUT-4; 38.2; A01/A09 |
| Every FUTURE_RESEARCH test case is reachable under the procedure | PASS | 38.20 reachability note (Route B vs Route A anchors) |
| Deficiency reference/presupposition is distinguished from assertion | PASS | BR-CROSS-13; BR-GAP-2; 38.12-P; D1 |
| "this gap" cannot instantiate a new GAP by itself | PASS | A02; 38.5 gap-reference row; PR-7; Class-A mapping |
| Nominalized "lack/gap" language cannot create GAP without assertive force | PASS | BR-CON-4; A03 vs A04; P16 |
| Section location cannot independently satisfy positioning relevance | PASS | 38.14 (no presumption); BR-CROSS-9; PR-4 |
| A positioning-irrelevant knowledge deficiency remains non-GAP in any section | PASS | BR-OTH-5; N01–N07; A10 |
| Practitioner capability deficits are separated from alignment deficiencies | PASS | BR-CROSS-14 vs BR-GAP-12; 38.12-W; A05–A07; PR-9 |
| The practitioner-knowledge boundary is closed (no open decision) | PASS | 38.22; normative rules in place |
| Every rule returns exactly one of the seven classes | PASS | §38.15 termination; BR-MOT-3; PR-10; registry audit — no disjunctive outputs |
| No operative combined-label output exists anywhere | PASS | 38.5 row, 38.12-W/X/H, 38.13 all single-valued; remaining "/" occurrences are pairwise-boundary headers, never labels |
| GAP normative tests explicitly satisfy G5 | PASS | 38.20 convention (forms A/B/C) applied to every G-item |
| Negative controls test knowledge deficiency with failed G5 | PASS | N01–N07 (+O09) |
| Decision procedure and normative test suite are mutually consistent | PASS | 38.20 consistency audit; every label derivable from §38.15 |
| An asserted deficiency with failed completion routes to UNCERTAIN, never Route B | PASS | D3 fourth exit; BR-GAP-6; principle 3; A11/A12/U07 |
| Failed completion cannot silently re-file an asserted deficiency as OTHER | PASS | T2b exit precedes any Route-B function reading; instruction F |
| Pragmatic-only and asserted-ungroundable are distinct branches | PASS | D3: pragmatic → Route B (Class-A if GAP emitted) vs completion-failure → UNCERTAIN(T2b); 38.4 |
| Content indeterminacy is covered without a fourth trigger | PASS | BR-UNC-1 T2 = assertion-or-content; trigger count unchanged |
| Topical overlap alone can never satisfy G5 | PASS | BR-GAP-4-B proposition-level standard; 38.14 insufficiency clause; N06/N07 |
| The [+POS] stipulation matches the proposition-level standard | PASS | 38.20 convention definition; A13 positive twin |
| Restatement co-reference is proposition-level | PASS | BR-FUT-2; topic-only echoes excluded |
| Bare capability/world-deficit statements have a frozen single default | PASS | OTHER default; MOTIVATION when problem-framed; UNCERTAIN(T3) when indeterminate (38.12-W/X; O13 vs A05) |
| The mattering-function reading adds no propositional content | PASS | BR-MOT-3: discourse-frame function judgment over existing text; completion/creation line untouched (principle 3) |
| F-suite route attribution is consistent with the decision procedure | PASS | F09 → Route B/BR-FUT-4 ("we invite research" asserts no deficiency); reachability note (38.20); F05/F08 remain the only Route-A anchors |
| No neutral prevalence fact is labeled MOTIVATION | PASS | M-set re-audited under BR-MOT-3; M03 mattering-framed in-unit; bare variant = O14 → OTHER; change register records the audit |
| T2b competitor sets are item-specific, never prescribed | PASS | BR-UNC-3 (no canonical per-trigger set); instruction F reworded; registry row updated; U07/A11/A12 annotated with stipulated contexts |

### Part C — Form and layering checks

| Check | PASS/FAIL | Evidence |
|---|---|---|
| The document is self-contained: every operative rule appears in full | PASS | Complete class table, G-conditions, procedure, 49-row registry, PR-0…PR-10, full guidance, full suite; no "carried from v1.1" references remain in operative text |
| Interpretation requires no earlier version | PASS | Change register is provenance-only (38.21); all normative content is present in this document |
| No forward references to unfrozen downstream artifacts | PASS | No Step-6 artifact identifiers, rule IDs, or compatibility assertions appear anywhere; dependency direction is one-way |
| Downstream pinning is specified without asserting downstream content | PASS | §38.21 downstream dependency note: Step 6 must pin `A1E-BR-1.2`; nothing more is claimed |
| Consolidation introduced no semantic change | PASS | Change register v1.2 line; operative rules identical in content to the three recorded corrections applied to the v1.1 base; diffable against the recorded revision history |

**All checks PASS — the A.1-E Boundary Rulebook is declared FROZEN at v1.2 (`A1E-BR-1.2`), as a complete, self-contained normative specification.**
