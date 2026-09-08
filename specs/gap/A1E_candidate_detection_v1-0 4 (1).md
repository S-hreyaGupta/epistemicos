# A.1-E Candidate Detection Spec v1.0 — EpistemicOS (Step 10)

**Status:** presented for independent freeze audit once the internal check (§43.33) passes. Version string: `A1E-CD-1.0` (`candidate_detection_rules_version`).
**Freeze-closure correction record (10A, same version):** 1. restored categorical-absence coverage from SL-ABS-1..6 to SL-ABS-1..9; 2. Step-10 test signal firings synchronized with frozen Step-7 own-study exclusions (T-BND-11: `Our study is limited by its cross-sectional design.` fires SL-OWNLIM-1, not SL-CSTR-3); 3. formal protocol MATCH_CRITERION returned to TBD_BY_FINAL_CALIBRATION ownership; 4. deterministic CANDIDATE_MATCH_ALGORITHM_v1 separated from the formal MATCH_CRITERION; 5. compound overflow changed from first-N truncation to honest diagnostic / incomplete-attestation handling; 6. conditional test expectations removed; 7. CT-MATCH-04 mathematical inconsistency corrected; 8. no candidate architecture, context policy, dedup policy, ordering policy, or downstream ownership changed.

**Final closure correction record (10B, same version):** 1. synchronized the CD-EMIT-2 machine registry from SL-ABS-1..6 to SL-ABS-1..9; 2. removed stale Step-10 ownership/references to the formal protocol MATCH_CRITERION; 3. standardized development/calibration evaluation terminology on CANDIDATE_MATCH_ALGORITHM_v1; 4. restored SL-WORLD-2 to the complete Step-7 → Step-10 anti-signal interface; 5. added SL-WORLD-2 provenance/non-veto coverage (CT-BND-10/11, grounded in frozen T-BND-16); 6. synchronized test-count/editorial closure; 7. no candidate semantics, envelope, context, dedup, overlap, ordering, diagnostic, or downstream ownership architecture changed.

**Execution-closure correction record (10C, same version):** 1. completed the closed Step-7 → Step-10 reference/positioning interface (SL-REF-1/2, SL-POS-1..4); 2. made the SL-REF-1 + CD-EMIT-9 persistence construction executable in CD-PREC-1 (direct vs registered construction-qualified basis at CD-4); 3. clarified direct bases vs construction-qualified bases in CD-EMIT-13; 4. synchronized IN-2, CD-EMIT-9 prose, the machine registry, and the signal-interface summary (third branch removed; closed predicate list and closed deficiency-head class restored); 5. added positive/negative SL-REF-1 normative tests (CT-CTX-08/09); 6. synchronized the CD-EMIT-6 SL-WORLD-1/2 registry wording; 7. updated test counts; 8. no semantic ownership, candidate envelope, merge, resolution, or verification architecture changed.

**Final freeze-closure correction record (10D, same version):** 1. removed the Step-10 expansion of frozen SL-REF-1 surface semantics (the local deficiency-head lexicon gap/lack/limitation/void is deleted; "void" was never on the frozen card); 2. changed CD-EMIT-9 to consume already-valid Step-7 SL-REF-1 matches only; 3. rewrote CT-CTX-08/09 as oracle-input Step-10 construction tests rather than Step-7 surface-matching tests; 4. corrected normative test provenance so construction-qualified emissions carry licensing signals in xsig according to frozen polarity (TEST-PROVENANCE invariant); 5. synchronized CD-CORE-3, the CD-EMIT-9 registry wording, CD-PREC-1, the execution traces, and the freeze checks; 6. no candidate semantics, Step-7 semantics, envelope, merge, resolution, or verification architecture changed.

**Pinned frozen inputs:** contract v1.2 · schema `A1E-GS-1.3` · protocol v1.2 · state machine v1.3 · `A1E-BR-1.2` · `A1E-DPR-1.1` · `A1E-SL-1.1` · `A1E-OR-1.1` · `A1E-GI-1.0`. Steps 1–9 are never reinterpreted, repaired, simplified, or extended here.

## 43.1 Purpose and ownership

Step 10 answers exactly one question: **"Which source-grounded manuscript passages should enter the downstream A.1-E semantic pipeline as candidate gap passages?"** It does NOT answer "is this actually a GAP?" — that is Step 5. CANDIDATE ≠ GAP: a candidate is only a source-grounded passage admitted for downstream semantic evaluation. False-positive candidates are expected and lawful; a missed true GAP is a detection error.

Step 10 OWNS: runtime scanning; operational use of Step-7 signals; deterministic signal-combination rules; candidate emission rules; the candidate source-span envelope; permitted candidate context capture; exact-duplicate detector suppression; overlapping-candidate handling; candidate ordering; detector diagnostics; candidate-detection versioning; the deterministic candidate-to-gold matching algorithm used for development/calibration (`CANDIDATE_MATCH_ALGORITHM_v1`); candidate recall/precision/yield/review-load measurement.

Step 10 DOES NOT OWN and MUST NEVER OUTPUT: GAP vs MOTIVATION / OWN_LIMITATION / FUTURE_RESEARCH / CONTRIBUTION / OTHER / UNCERTAIN (Step 5); `relation` and `knowledge_kind` (Step 6); `affected_object` and coreference resolution (Step 8); canonical identity, same-gap verdicts, `possibly_same_claim`, `related_claim` (Step 9); final gap-record construction (Step 11); object/citation resolution (Step 12); semantic verification (Step 13); the formal protocol MATCH_CRITERION (Step-3 final calibration; `TBD_BY_FINAL_CALIBRATION`); scientific truth, novelty, citation validity, evidence support, or importance. A Step-10 output naming any of these is a specification violation, not a feature.

## 43.2 Frozen inputs and interface notes

The following delegations are frozen upstream and are the license for what this spec defines: `A1E-SL-1.1` §40.24 — "the parser/matcher is Step-10 property"; §40.33 — "No window size, sentence count, token radius, or paragraph radius is defined — Step-10 property"; §40.28 — priors "modify candidate-detection interpretation and never override proposition semantics"; §40.19 — anti-signals "cannot operate as hard global exclusion rules"; SL-POS-4 — "Steps 9/10+ own operational use"; protocol v1.2 §29.2 — `detection_candidate` is "the system-side interface" to the gold layers. SM v1.3 supplies the run condition (`candidate_universe: open/closed`, epoch-numbered) and requires a **Step-10 detection-completion attestation** as an input to `CANDIDATE_UNIVERSE_CLOSED`; this spec defines when that attestation may be produced (§43.20) and nothing else about lifecycle orchestration.

**Interface note IN-1 (evaluation-interface timing).** Frozen Protocol v1.2 (principle 8) reserves the formal MATCH_CRITERION for the final calibration phase: it is `TBD_BY_FINAL_CALIBRATION`, set and frozen only there, before any sealed-cohort exposure. Step 10 therefore freezes only the deterministic candidate-to-gold matching procedure used for development and calibration: **CANDIDATE_MATCH_ALGORITHM_v1** (§43.24) — machine-computable, threshold-free, span-grounded, deterministic, and used to generate calibration evidence. It does NOT supersede the protocol-level MATCH_CRITERION. During final calibration the protocol may adopt this algorithm unchanged as MATCH_CRITERION or amend it under the frozen calibration process; until that event, MATCH_CRITERION = `TBD_BY_FINAL_CALIBRATION`, and no sealed cohort may be evaluated before the formal MATCH_CRITERION is frozen.

**Interface note IN-2 (restatement constructions).** Step 10 does not determine what text qualifies for SL-REF-1; pinned `A1E-SL-1.1` supplies valid SL-REF-1 matches. Step 10 defines only the construction-qualified detector rule: (valid SL-GAPLEX-2 match OR valid SL-REF-1 match) + the registered CD-EMIT-9 continuation/persistence construction. Neither signal alone emits under this route. The construction establishes none of: GAP status; relation; knowledge_kind; affected_object; same-gap identity; restatement identity. SL-REF-2 remains non-emitting in v1.0 unless another registered Step-10 rule explicitly licenses it. Step-7 polarity labels are unchanged.

**Interface note IN-3 (unverified family IDs).** Where individual signal IDs were not verifiable in the pinned SL index at build time, this spec cites the frozen **family names** (FUTURE_RESEARCH_MODAL, CONTRIBUTION_YIELD, MATTERING_STAKES) rather than inventing IDs. All individually cited SL-* IDs in this document exist verbatim in `A1E-SL-1.1`.

## 43.3 Candidate definition

**CD-CORE-1 (frozen).** A **candidate** is: (a) a PRIMARY CANDIDATE SPAN — one detection unit (or a bounded compound, §43.15) containing at least one registered emission basis; (b) zero or more CONTEXT SUPPORT SPANS — bounded neighboring source spans captured only to enable downstream interpretation of anaphora, attribution, ellipsis, restatement, or reversal; (c) detection provenance (§43.10). CANDIDATE ≠ GAP; SIGNAL MATCH ≠ GAP VERDICT; context spans never become part of any asserted proposition merely by inclusion — Step 5/Step 11 own final proposition boundaries. **CD-CORE-2 (priority ordering, frozen).** 1. avoid missing legitimate explicit/context-supported GAP propositions; 2. retain deterministic source grounding; 3. keep candidates bounded for downstream processing; 4. only then improve precision. Conservative over-inclusion is preferred to silent omission — but never by emitting unbounded regions: the envelope (§43.7) is the recall discipline's counterweight.

## 43.4 Determinism

**CD-CORE-4 (frozen claim).** Same normalized manuscript + same segmentation/proposition units + same section-role inputs + same `A1E-SL-1.1` + same `A1E-CD-1.0` → identical candidate output: identical candidate set, primary spans, context refs, matched signal provenance, diagnostics, and ordering. Prohibited runtime inputs: temperature-dependent LLM judgement; embedding similarity; unfrozen thresholds; stochastic ranking; external web knowledge; journal prestige; manuscript quality; reviewer expectations; scientific plausibility. **The v1.0 normative emission path is a deterministic rule engine over frozen source structure + Step-7 signal matches; no LLM participates in the normative path.** LLM-assisted tooling may exist only outside the emission path (e.g., diagnostic triage) and never adds, removes, re-spans, or re-orders candidates (OD-CD-3).

## 43.5 Runtime input contract

**CD-INPUT-1 (closed input set).** (A) normalized manuscript text (the same normalization gold/annotation uses); (B) stable character-offset source spans; (C) the upstream proposition/clause segmentation where available, else sentence segmentation (Layer-1-compatible units); (D) paragraph and section boundaries; (E) section roles with SL-SECTION-* categorical priors (ELEVATED / NEUTRAL / REDUCED / BOUNDARY_SPECIAL; UNKNOWN_SECTION → NEUTRAL); (F) Step-7 positive signal matches with span offsets and signal_id; (G) Step-7 context/reference/positioning signal matches:
SL-ATTR-1/2,
SL-REVERSAL-1,
SL-COREF-1,
SL-TEMP-1,
SL-CITE-1,
SL-REF-1/2,
SL-POS-1/2/3/4;

(H) Step-7 anti-signal matches:
SL-OWNLIM-1/2,
SL-WORLD-1/2,
and boundary-family matches; (I) polarity/negation-scope metadata per SL §40.24 and temporal metadata per SL §40.26a; (J) neighboring unit references solely for context capture; (K) document_id, document_version, run_id, and current candidate-universe epoch (SM v1.3). **CD-INPUT-2.** All inputs are consumed under pinned versions; a signal match citing an ID absent from the pinned `A1E-SL-1.1` registry is a diagnostic condition (CD-DIAG-3), never silently accepted or repaired. No new canonical schema field is created anywhere in Step 10; all detector structures are internal/processing-envelope metadata (I-35/I-43 mutability side), and `A1E-GS-1.3` is unmodified.

## 43.6 Detection unit

**CD-INPUT-4 (unit hierarchy, frozen).** The smallest normal detection unit is the upstream **proposition/clause unit**; where clause segmentation is unavailable or structurally unsafe for a region, the **sentence** is the unit; a bounded **multi-unit compound** exists only under CD-EMIT-12 (segmentation cannot safely separate co-asserted deficiency clauses) and never exceeds MAX_COMPOUND (§43.7). Paragraph-level or section-level candidates do not exist. **CD-INPUT-3 (supported-region map, frozen).** Eligible detection regions: abstract and main body prose (including quoted prose inside main text, and appendix prose). Ineligible in v1.0 — headings, table cells, figure/table captions, footnotes/endnotes, the reference list, and non-prose artifacts: a positive signal match inside an ineligible region produces a **diagnostic record** (CD-DIAG-6: region, span, matched signals — reviewable, never silently dropped) and no candidate. This is a coverage boundary, not a semantic judgement; widening it is a candidate-envelope amendment.

## 43.7 Candidate envelope

**CD-CONTEXT-2 (deterministic bounded envelope, frozen constants).**
- PRIMARY span = exactly one detection unit, or one compound of ≤ **MAX_COMPOUND = 3** contiguous units under CD-EMIT-12. One weak signal can never expand a primary beyond its unit.
- CONTEXT capture = at most **CONTEXT_MAX = 2** units, strictly preceding the primary, captured innermost-first (P−1, then P−2), only when a §43.16 trigger is present.
- Paragraph boundary: the window may cross at most ONE paragraph boundary, and only when the primary is paragraph-initial or the remaining window extends past the paragraph start; the crossed material is the final unit(s) of the immediately preceding paragraph, still within CONTEXT_MAX.
- Section boundary: never crossed, in either direction, for any purpose.
- Forward (cataphoric) capture = 0 in v1.0 (OD-CD-1).
- Expansion stops when: the trigger class is satisfied by captured units' mere presence (capture is form-driven, never resolution-driven — Step 10 does not test whether an antecedent "resolves"); or CONTEXT_MAX is reached; or a section boundary is reached.
Rationale for the constants: every frozen upstream context-supported example (schema V-series; GI/OR completion anchors; SL §40.33 patterns) locates its supporting material within two immediately preceding units; the SL explicitly delegates the radius to Step 10 (§43.2). The constants are amendable only via the context-window amendment class with impact analysis (§43.31). The envelope structurally prevents signal → paragraph → section → document inflation, and it is what constrains CANDIDATE_MATCH_ALGORITHM_v1 against oversized candidate primaries (§43.24).

## 43.8 Step-7 signal interface

**CD-CORE-6 (frozen).** Step 7 is a static feature vocabulary; Step 10 defines signal → detector-rule mappings and never signal → semantic-GAP meaning. Signal meanings, IDs, tiers, polarities, exclusions, false-friend non-firings, negation-scope non-firings (SL §40.24), and temporal-cancellation non-firings (SL §40.26a rules B/C) are consumed exactly as frozen: **where the SL says a form does not fire, no Step-10 emission basis exists** — that is the frozen detector-safe non-trigger layer, owned upstream. A signal match is detection evidence only: "little is known" (SL-LIM-1) may justify emission; it outputs neither GAP nor LIMITED nor evidence. **CD-EMIT-13 (tier-based basis rule, frozen).** An emission basis is: any STRONG- or MODERATE-tier positive-polarity match; a WEAK-tier positive match (SL-GAPLEX-2) constitutes a basis ONLY inside the registered restatement construction (CD-EMIT-9). Reference-polarity matches (SL-REF-1/2),
boundary-polarity matches (...),
anti-polarity matches (SL-OWNLIM-1/2, SL-WORLD-1/2),
context/positioning-polarity matches
(
  SL-ATTR-1/2,
  SL-REVERSAL-1,
  SL-COREF-1,
  SL-TEMP-1,
  SL-CITE-1,
  SL-POS-1/2/3/4
),
and prior records are NEVER emission bases alone.

These signals may participate in a separately registered Step-10
construction, such as CD-EMIT-9, but none is an emission basis by itself.

**Signal-coverage matrix (machine-auditable; every individually registered positive `A1E-SL-1.1` signal → its emission rule; semantics untouched).**
| SL positive signal(s) | tier(s) | Step-10 emission rule |
|---|---|---|
| SL-ABS-1, SL-ABS-2, SL-ABS-3, SL-ABS-4, SL-ABS-5, SL-ABS-6, SL-ABS-7, SL-ABS-8, SL-ABS-9 | STRONG | CD-EMIT-2 |
| SL-LIM-1, SL-LIM-2, SL-LIM-3, SL-LIM-4, SL-LIM-5, SL-LIM-7 | STRONG | CD-EMIT-1 |
| SL-LIM-6 | MODERATE | CD-EMIT-1 |
| SL-SUP-1, SL-SUP-3, SL-SUP-4 | STRONG | CD-EMIT-1 |
| SL-SUP-2 | MODERATE | CD-EMIT-1 |
| SL-GAPLEX-1, SL-GAPLEX-3, SL-GAPLEX-4 | MODERATE | CD-EMIT-1 |
| SL-GAPLEX-2 | WEAK | CD-EMIT-9 only — WEAK tier is not a standalone basis (CD-EMIT-13); lawful reason stated there |
| SL-CONF-1, SL-CONF-2, SL-CONF-3, SL-CONF-4, SL-CONF-6 | STRONG | CD-EMIT-4 |
| SL-CONF-5 | MODERATE | CD-EMIT-4 |
| SL-TEST-1, SL-TEST-2, SL-TEST-3 | STRONG | CD-EMIT-5 |
| SL-CSTR-1, SL-CSTR-2, SL-CSTR-3, SL-CSTR-6 | STRONG | CD-EMIT-3 |
| SL-CSTR-4, SL-CSTR-5 | MODERATE | CD-EMIT-3 |
| SL-CHAL-1, SL-CHAL-2, SL-CHAL-3, SL-CHAL-4, SL-CHAL-5 | STRONG | CD-EMIT-7 |
| SL-DISC-A1, SL-DISC-B1, SL-DISC-C1, SL-DISC-D1, SL-DISC-D2 | STRONG | CD-EMIT-6 |
No positive signal is unmapped. Reference/context/anti/boundary/prior signals are not DIRECT emission bases (CD-EMIT-13) and normally appear as provenance/context metadata; a signal may participate in a separately registered construction-qualified detector basis only where an explicit Step-10 rule licenses it — in v1.0, SL-REF-1 may participate in CD-EMIT-9, while SL-REF-2 participates in no emission construction and remains provenance / non-basis only. Step-7 polarity labels are unchanged.

## 43.9 Section priors and anti-signals

**CD-CORE-8 (priors non-determinative, frozen).** SL-SECTION-* priors are categorical metadata: they may shape diagnostics and review presentation; they may NEVER emit a candidate, veto a candidate, upgrade a match, or suppress a positive signal. A deficiency signal in Methods, Results, Discussion, or Conclusion emits exactly as in Introduction (CT-SECT suite); Introduction location without a registered basis emits nothing. **CD-CORE-9 (anti-signals non-veto, frozen).** positive signal + anti-signal → the candidate still emits, carrying the anti-signal in provenance. Anti-signals may attach metadata, trigger context capture (e.g., SL-OWNLIM co-presence marks a Step-5-relevant environment), and inform diagnostics; they may never remove a passage satisfying an emission rule — "This study is limited because few prior studies have examined X." emits on SL-LIM-2 with SL-OWNLIM-1 preserved (SL §40.19, INT-4). The rule is strictly one-directional: VALID positive signal + anti-signal → EMIT + preserve anti-signal metadata; an anti-signal alone is NEVER an emission basis, and Step 10 never invents a positive firing the frozen library withholds (T-BND-11 conformance). Step 5 owns every boundary decision this metadata serves.

## 43.10 Core emission architecture

**CD-CORE-3 (registered-basis emission, frozen).** Every emitted candidate cites ≥1 registered CD-EMIT-* rule AND ≥1 registered Step-7 signal match satisfying that rule; the satisfying signal need not be positive-polarity where the registered rule explicitly defines a construction-qualified basis (CD-EMIT-9 + valid SL-REF-1 + persistence construction). The Step-7 signal-provenance requirement is never weakened. No candidate exists because output "looked gap-like." Recorded provenance (Step-10 internal / processing-envelope only; no schema change): CD-EMIT-* rule ID(s); Step-7 signal ID(s) with match spans; primary unit ref(s) and char offsets; context unit refs with their trigger class; co-present context/anti/boundary signal IDs; section role + prior value; pinned versions; emitting-run epoch. **CD-CORE-5 (ownership guard).** The candidate record contains NO field named or valued as relation, knowledge_kind, affected_object, gap type, GAP verdict, identity verdict, possibly_same, related_claim, or quality score. **CD-CORE-7 (no hidden classifiers).** No Step-10 rule conditions on "is a limitation / is motivation / is future research / is a contribution / is a real gap / is the same gap" — only on registered signal presence, polarity, tier, structure, and position.

## 43.11 Direct signal candidates

**CD-EMIT-1** — LIMITED_KNOWLEDGE / EVIDENTIAL_SUPPORT / assertive GAP_LEXEME basis: any STRONG/MODERATE positive match from SL-LIM-1..7, SL-SUP-1..4, SL-GAPLEX-1/3/4 in an eligible unit → emit that unit as primary. Non-trigger: SL non-firing forms ("not limited"; FF entries); reference-polarity nominals. Prohibited inference: LIMITED/kind assignment.
**CD-EMIT-2** — CATEGORICAL_ABSENCE basis: SL-ABS-1..9 → emit, preserving every frozen required_context, non-firing, false-friend (incl. FF-43/44/45 present-study-procedure and instrument-state exclusions on SL-ABS-8/9), temporal-cancellation, and polarity condition exactly as supplied. Non-trigger: SL exclusions (own-study procedure; participant reports; temporal cancellation per SL §40.26a B/C). Prohibited: ABSENT assignment; no theory/method/object wording is interpreted.
**CD-EMIT-3** — CAPABILITY_CONSTRAINT basis: SL-CSTR-1..6 → emit. SL-CSTR-6/SL-CHAL-5 ambiguity metadata (`ambiguous_semantics`, OD-DPR-2) is carried, never resolved. Prohibited: CONSTRAINED/CHALLENGED assignment.
**CD-EMIT-4** — CONFLICT_INCONSISTENCY basis: SL-CONF-1..6 → emit. Prohibited: CONFLICTING assignment; contester resolution.
**CD-EMIT-5** — TESTING_ABSENCE basis: SL-TEST-1..3 → emit. Prohibited: UNTESTED assignment.
**CD-EMIT-6** — RESEARCH_PRACTICE basis: SL-DISC-A1/B1/C1/D1/D2 only (both poles named, per family required_context). Non-trigger:
SL-WORLD-1/2 environments without a registered research–practice
positive signal. ("Managers do not understand X." carries no positive basis). No generic practitioner-world detector exists. Prohibited: practice_alignment assignment.
**CD-EMIT-7** — CHALLENGE_INVALIDITY basis: SL-CHAL-1..5 → emit. Prohibited: CHALLENGED assignment; validity judgement.
Each rule's full row (structure, permitted context, test refs) is in §43.23.

## 43.12 Context-supported candidates

**CD-EMIT-8.** A positive basis (CD-EMIT-1..7) whose unit exhibits a backward-dependency form — demonstrative/anaphoric subject or argument ("this/these/that/those/such + N"; bare anaphoric pronoun subject; SL-COREF-1 match; `coreference_dependent` flag on the matched signal) → emit with MANDATORY context capture under §43.7/§43.16. "These mechanisms remain unexplored in distributed settings." emits on SL-ABS-5 with the preceding unit(s) as context; "This model remains untested." emits on SL-TEST-1 likewise. Step 10 does NOT resolve "These mechanisms" → coordination mechanisms or "This model" → Model A: no affected_object exists in the output; context capture only guarantees that Step 8's lawful completion inputs travel with the candidate. Missing context (window empty at document/section start) → emit + CD-DIAG-4.

## 43.13 Restatement candidates

**CD-EMIT-9 — RESTATEMENT-DEFICIENCY CONSTRUCTION.** Emit iff BOTH hold in one unit: (A) at least one of the following frozen Step-7 matches is ALREADY PRESENT in the unit's match set: (1) SL-GAPLEX-2; OR (2) a VALID SL-REF-1 match supplied by pinned `A1E-SL-1.1`; AND (B) the same referential expression participates in a registered continuation/persistence construction from the frozen CLOSED CD-EMIT-9 predicate list {persists, persist, remains, remain, continues, continue, endures, endure, remains unresolved, remains unaddressed, is still present}. Step 10 MUST NOT: decide whether arbitrary wording qualifies as SL-REF-1; expand SL-REF-1 to new heads; create a Step-10-specific SL-REF-1 lexical class; or infer a reference signal from semantic similarity — Step 7 owns surface matching, required context, exclusions, polarity, and signal identity; Step 10 consumes the already-valid match. Registered construction-qualified basis = (valid frozen SL-GAPLEX-2 match OR valid frozen SL-REF-1 match) + the registered continuation/persistence construction. Explicit non-bases: SL-GAPLEX-2 alone → NO_EMIT under this route; SL-REF-1 alone → NO_EMIT; SL-REF-2 alone → NO_EMIT; the continuation/persistence construction alone → NO_EMIT. No GAP verdict; no same-gap identity; no relation/kind/object extraction — Step 5 and Step 9 retain their frozen ownership.
No same-gap identity is inferred. Non-trigger (closed): response-verb constructions per SL-CONTRIB-3 ("we fill/close/address/bridge this gap"); forward-reference predicates {is addressed, will be addressed, is examined, is discussed, is resolved} + {below, next, in the next section, in Section N, here, in this paper/study} — "This gap is addressed in the next section." emits nothing; bare SL-REF-1 nominals without a listed continuation predicate. Prohibited inference: same-gap attachment (Step 9); restatement-role assignment (Step 9). Full deficiency assertions with restatement markers ("as noted above, little is known about X") emit under CD-EMIT-1 with the marker driving context capture — CD-EMIT-9 is only for the predicate-poor referential form.

## 43.14 Attribution / negation / reversal

**CD-CONTEXT-4 (frozen).** (A) Attribution: per SL §40.16, local deficiency predication fires inside complements and quotations — "Smith argues that little is known about X." emits on SL-LIM-1 with SL-ATTR-1 preserved and the attribution frame inside the primary span; Step 10 never strips attribution and never decides adoption (Step 5). (B) Negation/reversal: where the SL's frozen non-firing rules block the positive signal ("Evidence is not limited."; "X is no longer unexplored." → SL-TEMP-1 cancellation), no basis exists → no emission. Where the positive form fires inside a negated/reversed/rejected embedding not blocked by SL ("It is not true that little is known about X." — the complement "little is known about X" is a local predication), the candidate emits WITH the negation/reversal context signal retained (SL-REVERSAL-1 / negation metadata / SL-ATTR-2); reversal spans may trigger context capture (`cross_sentence_context_possible`). The detector never strips negation and never performs Step-5 exclusion. (C) Historical deficiency (SL §40.26a rule A): positive signal + SL-TEMP-1 → emit with temporal metadata.

## 43.15 Multiple signals / compound propositions

**CD-EMIT-11 (frozen).** One unit + multiple positive matches supporting the same envelope → ONE candidate with the union of signal provenance ("Little empirical evidence exists and findings remain inconsistent regarding X." → one candidate; SL-GAPLEX-4/SL-LIM-3-family + SL-CONF-2 provenance; whether it is one gap, two gaps, LIMITED, or CONFLICTING is downstream). One candidate per lexical match is prohibited. **CD-EMIT-12 (frozen).** Two deficiency predications in one sentence: if upstream segmentation yields two units ("Evidence on X is limited," | "while findings on Y remain inconsistent.") → two candidates, one per unit. If segmentation cannot safely separate them → ONE compound candidate (≤ MAX_COMPOUND contiguous units) with each internal signal span preserved; Step 10 never invents two canonical gaps and never merges two segmented units into one candidate for convenience. **CD-EMIT-10 (persistence-reason clause).** A subordinate reason clause carrying its own positive basis ("…because existing theories cannot explain Y.") → its own candidate when segmentation supplies the clause unit, else part of the host compound with the clause-internal signal span preserved. Whether it spawns a gap (I-16) is upstream/downstream semantics, never Step 10's.

## 43.16 Context capture

**CD-CONTEXT-1 (closed trigger classes).** Context capture occurs only when the primary unit exhibits: T1 anaphoric/demonstrative dependency form (CD-EMIT-8); T2 restatement construction or restatement marker ("as noted above", "as discussed", SL-POS-4 anaphors); T3 attribution frame extending beyond the unit or SL-ATTR-1/2 with `cross_sentence_context_possible`; T4 reversal/concession span (SL-REVERSAL-1) crossing into the preceding unit; T5 ellipsis/comparative dependency form ("Such evidence remains limited."). Capture is form-triggered and bounded (§43.7); Step 10 never verifies that the captured material actually resolves the dependency — resolution is Step 8 (objects) and the frozen proposition representation (propositions). **CD-CONTEXT-3 (frozen).** Context spans are metadata: excluded from the primary span, excluded from CANDIDATE_MATCH_ALGORITHM_v1 containment, never part of any asserted proposition, never evidence of any semantic verdict.

## 43.17 Duplicate emission handling

**CD-DEDUP-1 (exact detector-event identity, frozen).** Two detector events are the SAME candidate iff: same document_id + document_version + run_id + identical primary-span boundaries + identical envelope (context-ref set). Then: one candidate, union of rule/signal provenance — this covers the same signal firing twice, two rules on one span, and duplicated event delivery (idempotence). **CD-DEDUP-2 (frozen).** Identical TEXT at different manuscript positions → DISTINCT candidates, always ("Little is known about X." in Introduction and again in Discussion → two candidates); cross-position text dedup is semantic identity and belongs to Step 9. No similarity measure of any kind participates in dedup.

## 43.18 Overlap handling

**CD-OVERLAP-1** — exact duplicate envelope → suppression per CD-DEDUP-1. **CD-OVERLAP-2** — same primary unit, different signal matches or different emitting rules → one candidate, union provenance (equivalent to CD-EMIT-11 at the event level). **CD-OVERLAP-3** — nested envelopes caused only by differing context-window capture over the same primary unit → one canonical candidate under deterministic precedence: the envelope produced by evaluating the union of present trigger classes under §43.7 (i.e., the maximal lawful window; windows are never unioned beyond CONTEXT_MAX). **CD-OVERLAP-4** — genuinely distinct primary units with overlapping sentence or shared context coverage → SEPARATE candidates, always (two clause units of one sentence; a unit that is context for another candidate's primary). Semantic similarity never collapses an overlap.

## 43.19 Candidate IDs / ordering

**CD-ORDER-1 (frozen).** Step 10 assigns only an internal detector ordinal; canonical `gap_id` assignment timing is owned by SM v1.3 + Step 9/Step 12 machinery (D10) and is untouched. Candidate output order: 1. primary-span start offset (ascending); 2. primary-span end offset (ascending); 3. stable segmentation unit ID (lexicographic); 4. lowest emitting CD-EMIT-* rule ID — final deterministic tie-break only. **CD-ORDER-2 (frozen).** Signal-match enumeration order, unit processing order, worker/thread scheduling, batch partitioning, and event arrival order never affect the candidate set, spans, provenance, or ordering; parallel evaluation of independent units is lawful only because outputs are merged under CD-ORDER-1 and CD-DEDUP-1 idempotence.

## 43.20 Candidate-universe closure

**CD-CORE-10 (completion rule, frozen).** The Step-10 **detection-completion attestation** (the input SM v1.3 requires for `CANDIDATE_UNIVERSE_CLOSED`) may be produced ONLY when every eligible detection unit in the supported manuscript envelope (§43.6) has been evaluated under the pinned `A1E-CD-1.0` + `A1E-SL-1.1` versions for the run. Completion never depends on: how many candidates were found; early stopping; ranking cutoffs; any judgement that "enough gaps have been found." **CD-CORE-11 (frozen prohibitions).** No top-k detection; no per-manuscript candidate cap; no section-only scanning; no sampling or subsampling; no early stop after N candidates; no ranking cutoff. Deterministic optimizations (indexed lookup, precompiled rules, parallel unit evaluation) are lawful only when provably output-invariant. If an operational resource limit interrupts evaluation: emit CD-DIAG-8-family diagnostics identifying the unevaluated region and DO NOT produce the completion attestation — completeness is never falsely declared. Emission attempts under a closed or stale epoch are rejected by SM legality; Step 10 records the diagnostic (late detection is a Step-4 reopening reason, not a Step-10 override).

## 43.21 Diagnostics / failure routes

**CD-DIAG-1** invalid/missing source span → diagnostic record with unit ref; no silent drop. **CD-DIAG-2** malformed segmentation unit → sentence-level fallback per CD-INPUT-4 + diagnostic. **CD-DIAG-3** signal ID unknown to pinned `A1E-SL-1.1` → diagnostic; the match is quarantined, never an emission basis, never silently repaired. **CD-DIAG-4** context window unconstructible (document/section start; missing units) → emit the candidate WITHOUT the unavailable context + diagnostic (reviewable; never suppresses emission). **CD-DIAG-5 (compound-envelope overflow).** Applies ONLY to a genuinely unsplittable structure whose lawful primary would exceed MAX_COMPOUND (if upstream segmentation provides separate units, each is evaluated independently and this rule never applies): emit a diagnostic identifying the over-envelope structure; preserve every matched signal span and source trace in the diagnostic; emit NO truncated candidate; mark the affected unit/region unevaluated for completion-attestation purposes; produce no detection-completion attestation for the run until the condition is resolved/reprocessed. Prohibited inference: first MAX_COMPOUND units = sufficient representation of the whole signal-bearing structure. **CD-DIAG-6** positive signal in an unsupported region → diagnostic record (region, span, signals); no candidate; reviewable (§43.6). **CD-DIAG-7** conflicting source offsets (span map disagreement) → diagnostic; affected unit excluded from the completion attestation's "evaluated" set unless re-supplied. **CD-DIAG-8** stale/closed epoch at emission time; interrupted evaluation → diagnostics + no completion attestation (§43.20). All diagnostics preserve reviewability; none deletes a signal-bearing passage; no new lifecycle state is invented — diagnostics are records, and lifecycle behavior stays SM v1.3's.

## 43.22 Deterministic decision procedure

**CD-PREC-1.** CD-1 Verify pinned versions + epoch (CD-INPUT-2; CD-DIAG-8). CD-2 Enumerate eligible detection units over the supported-region map (CD-INPUT-3/4). CD-3 For each unit, collect Step-7 matches with polarity/tier/negation/temporal metadata; quarantine unknown IDs (CD-DIAG-3). CD-4 Determine whether the unit has at least one LAWFUL DETECTOR BASIS of either type: (A) DIRECT BASIS — a direct emission basis under CD-EMIT-13; OR (B) REGISTERED CONSTRUCTION-QUALIFIED BASIS — all requirements of a registered construction rule are satisfied; for v1.0 this is exactly CD-EMIT-9: (already-valid SL-GAPLEX-2 match OR already-valid SL-REF-1 match) + registered continuation/persistence construction. No new Step-7 lexical matching occurs at CD-4: the licensing signal must already exist in the Step-7 match set. If neither A nor B is satisfied → no candidate (SL-REF-1 alone, SL-REF-2 alone, a persistence predicate alone, and boundary/anti/context/prior matches alone all emit nothing). CD-5 Apply the corresponding registered CD-EMIT-* rule(s); form compounds only per CD-EMIT-12. CD-6 Apply context triggers (CD-CONTEXT-1) and capture under the §43.7 envelope; attach CD-DIAG-4 where unconstructible. CD-7 Deduplicate exact events (CD-DEDUP-1) and resolve overlaps (CD-OVERLAP-1..4). CD-8 Record provenance (CD-CORE-3). CD-9 Order output (CD-ORDER-1). CD-10 After every eligible unit is evaluated, produce the detection-completion attestation (CD-CORE-10); otherwise emit diagnostics and stop short of attestation. No step consults semantics, similarity, or downstream verdicts.
**Execution traces (frozen proof; oracle Step-7 input).** GIVEN a unit U2 whose Step-7 match set already contains a valid SL-REF-1 match on its referential expression, with a registered persistence predicate governing that expression, and antecedent unit U1: CD-4 finds no direct CD-EMIT-13 basis BUT a construction-qualified basis (valid SL-REF-1 + registered construction) → CD-5: CD-EMIT-9 → emit candidate on U2, capture U1 as bounded context → no semantic classification (CT-CTX-08). GIVEN the same valid SL-REF-1 match where the governing predicate is a forward-reference non-trigger: CD-4 finds neither basis type → NO_EMIT (CT-CTX-09). Step 10 performs no surface matching in either trace.

## 43.23 Machine-referenceable rule registry

Every normative CD-* ID has exactly one row; no pseudo-ranges; retired IDs never reused.

| rule_id | rule_family | normative_rule | input_condition | candidate_effect | required_signal_or_structure | permitted_context | non_trigger | prohibited_inference | upstream_dependency | test_refs |
|---|---|---|---|---|---|---|---|---|---|---|
| CD-CORE-1 | CORE | candidate = primary span + bounded context + provenance; CANDIDATE ≠ GAP | any emission | defines output object | registered basis | §43.7 envelope | — | GAP verdict | contract; Step-5 ownership | CT-DIR-01, CT-BND-01 |
| CD-CORE-2 | CORE | recall-first priority ordering; bounded envelope as counterweight | design-level | over-inclusion preferred to omission | — | — | unbounded emission | recall via whole sections | protocol | CT-BND suite |
| CD-CORE-3 | CORE | every candidate cites registered rule + signal; full provenance recorded | emission | provenance attached | ≥1 CD-EMIT-* + ≥1 SL match | — | basisless emission | "looked gap-like" | SL registry | CT-DIR suite |
| CD-CORE-4 | CORE | determinism claim; no stochastic/LLM/external inputs in normative path | runtime | identical output for identical input | — | — | — | plausibility-driven detection | — | CT-ORD suite |
| CD-CORE-5 | CORE | output contains no downstream semantic fields | emission | ownership guard | — | — | — | relation/kind/object/identity output | Steps 5/6/8/9 | CT-BND suite |
| CD-CORE-6 | CORE | signal match ≠ GAP verdict; SL non-firing = no basis | any match | detection evidence only | SL semantics as frozen | — | SL-blocked forms | signal → semantic meaning | SL §40.24/§40.26a | MP-CD-01/02 |
| CD-CORE-7 | CORE | no hidden Step-5/6/8/9 classifier anywhere | all rules | structure-only conditions | presence/polarity/tier/position | — | — | class-conditioned emission | Steps 5/6/8/9 | CT-BND suite |
| CD-CORE-8 | CORE | section priors never emit, veto, upgrade, or suppress | prior present | metadata only | SL-SECTION-* categorical | — | — | prior-driven decisions | SL §40.28 | CT-SECT-01..06 |
| CD-CORE-9 | CORE | anti-signals never veto a positive basis; anti-signals alone are never bases | anti co-present | emit + preserve anti provenance | — | — | — | anti-driven suppression; anti-as-basis | SL §40.19 | CT-BND-03, CT-BND-10, CT-BND-11, MP-CD-07 |
| CD-CORE-10 | CORE | completion attestation only after all eligible units evaluated | run end | attestation gating | full-universe evaluation | — | resource-limited runs | count-based completeness | SM v1.3 closure | CT-ORD-06 |
| CD-CORE-11 | CORE | no top-k / caps / sampling / early stop / section-only scanning; optimizations output-invariant | runtime | universe integrity | — | — | — | ranking-based recall loss | SM closure | CT-ORD suite |
| CD-INPUT-1 | INPUT | closed runtime input set (A)–(K) | run start | inputs fixed | — | — | — | external knowledge input | schema; SM; SL | CT-DIR-01 |
| CD-INPUT-2 | INPUT | pinned-version consumption; unknown refs quarantined | any input | version safety | — | — | — | silent repair | all pins | CT-ORD-01 |
| CD-INPUT-3 | INPUT | supported-region map; ineligible regions → diagnostic, no candidate | region check | coverage boundary | — | — | main-prose signals | region-based semantic judgement | — | CT-BND-09 |
| CD-INPUT-4 | INPUT | unit hierarchy: proposition/clause → sentence fallback; no paragraph default | segmentation | unit selection | upstream segmentation | — | — | paragraph candidates | protocol Layer-1 | CT-MULT-02 |
| CD-EMIT-1 | EMIT | limited-knowledge / evidential-support / assertive gap-lexeme basis | eligible unit | emit unit | SL-LIM-1..7; SL-SUP-1..4; SL-GAPLEX-1/3/4 | §43.16 | SL non-firing; reference nominals | LIMITED/kind assignment | SL §40.8/40.11/40.15 | CT-DIR-01/02/07, MP-CD-01 |
| CD-EMIT-2 | EMIT | categorical-absence basis | eligible unit | emit unit | SL-ABS-1..9 | §43.16 | SL exclusions; temporal cancellation | ABSENT assignment | SL §40.7/§40.26a | CT-DIR-03, CT-DIR-11, CT-DIR-12, CT-DIR-13, MP-CD-03 |
| CD-EMIT-3 | EMIT | capability/constraint basis; ambiguity metadata carried | eligible unit | emit unit | SL-CSTR-1..6 | §43.16 | SL FF entries | CONSTRAINED/CHALLENGED assignment | SL §40.12; OD-DPR-2 | CT-DIR-04, MP-CD-02 |
| CD-EMIT-4 | EMIT | conflict/inconsistency basis | eligible unit | emit unit | SL-CONF-2, SL-CONF-5, family positives per pinned registry | §43.16 | "not inconsistent" (SL non-firing) | CONFLICTING assignment | SL §40.9 | CT-DIR-05, MP-CD-08 |
| CD-EMIT-5 | EMIT | testing-absence basis | eligible unit | emit unit | SL-TEST-1..3 | §43.16 | SL FF (test set etc.) | UNTESTED assignment | SL §40.10 | CT-DIR-06, MP-CD-05 |
| CD-EMIT-6 | EMIT | research-practice basis; both poles required; no generic practitioner detector | eligible unit | emit unit | SL-DISC-A1/B1/C1/D1/D2 | §43.16 | SL-WORLD-1/2 environments without a registered research–practice positive signal | practice_alignment assignment | SL §40.13/§40.23 | CT-DIR-08, MP-CD-04 |
| CD-EMIT-7 | EMIT | challenge/invalidity basis | eligible unit | emit unit | SL-CHAL-1..5 | §43.16 | FF (challenging environment) | CHALLENGED assignment; validity judgement | SL §40.14 | CT-DIR-09 |
| CD-EMIT-8 | EMIT | context-supported form → mandatory bounded context | basis + dependency form | emit + context | CD-EMIT-1..7 basis + T1/T5 form | §43.7 mandatory | independent-referential units | object resolution | SL §40.27; OR ownership | CT-CTX-01..04, MP-CD-09 |
| CD-EMIT-9 | EMIT | restatement-deficiency construction; construction-qualified basis, reached via CD-PREC-1 CD-4(B); consumes already-valid Step-7 matches only | referential unit | emit + mandatory context | (valid frozen SL-GAPLEX-2 match OR valid frozen SL-REF-1 match) + closed CD-EMIT-9 continuation/persistence predicate list | §43.7 mandatory | SL-GAPLEX-2 without registered construction; SL-REF-1 without registered construction; SL-REF-2; forward-reference predicates; SL-CONTRIB-3 response-verb constructions | same-gap attachment; restatement role; GAP-status inference; Step-10 surface classification | SL §40.15/40.16/40.21; IN-2 | CT-CTX-05/06/08/09, MP-CD-06, MP-CD-25 |
| CD-EMIT-10 | EMIT | persistence-reason clause with own basis → own candidate (or preserved compound span) | subordinate clause | emit clause unit | clause-internal CD-EMIT-1..7 basis | §43.16 | reason clauses without basis | spawn decision (I-16) | GI-REASON ownership | CT-MULT-05, MP-CD-13 |
| CD-EMIT-11 | EMIT | multiple signals, one unit → one candidate, union provenance | multi-match unit | single emission | ≥2 bases one unit | §43.16 | — | per-signal candidate inflation | — | CT-MULT-01 |
| CD-EMIT-12 | EMIT | two predications: two units → two candidates; unsplittable → one bounded compound | multi-predication sentence | split or compound | segmentation | §43.16 | — | canonical gap segmentation | protocol Layer-1 | CT-MULT-02/03 |
| CD-EMIT-13 | EMIT | governs DIRECT emission bases: STRONG/MODERATE positive = direct basis; WEAK and non-positive polarities never direct bases alone; a non-direct signal may participate only in a separately registered construction-qualified basis (v1.0: SL-REF-1 in CD-EMIT-9) | any match | direct-basis gating | tier + polarity metadata | — | boundary/anti/context/reference/prior alone | semantic weighting; polarity relabeling | SL §40.6 | CT-BND-04..08, CT-CTX-08, CT-CTX-09, MP-CD-10 |
| CD-CONTEXT-1 | CONTEXT | closed trigger classes T1–T5; form-triggered, never resolution-tested | primary emitted | capture gating | dependency forms; SL context flags | §43.7 | trigger-free units | resolution verification | SL §40.27/§40.33 | CT-CTX suite |
| CD-CONTEXT-2 | CONTEXT | envelope constants: primary ≤ MAX_COMPOUND=3; context ≤ CONTEXT_MAX=2 preceding; ≤1 paragraph crossing; no section crossing; no forward capture | capture | bounded envelope | — | — | — | unbounded expansion | SL §40.33 delegation | CT-CTX-03/07, CT-MATCH-04 |
| CD-CONTEXT-3 | CONTEXT | context spans are metadata: never proposition content, never match-eligible | any capture | separation | — | — | — | context-as-assertion | GI/OR ownership | CT-MATCH-03 |
| CD-CONTEXT-4 | CONTEXT | attribution and negation/reversal preserved; SL non-firing respected; historical deficiency emits with SL-TEMP-1 | frame present | emit + preserve frames | SL-ATTR-1/2; SL-REVERSAL-1; SL-TEMP-1; §40.24 metadata | §43.7 | SL-blocked cancellations | frame stripping; adoption/exclusion decisions | SL §40.16/40.24/40.26/40.26a | CT-BND-05/06, MP-CD-01/11/12 |
| CD-DEDUP-1 | DEDUP | exact event identity: doc+version+run+primary+envelope → one candidate, union provenance; idempotent | duplicate events | suppression | identical envelope | — | different positions | — | — | CT-DUP-01/02/05 |
| CD-DEDUP-2 | DEDUP | identical text at different positions → distinct candidates; no semantic dedup | repeated wording | both survive | — | — | — | text-based cross-position dedup | GI ownership | CT-DUP-03, MP-CD-14 |
| CD-OVERLAP-1 | OVERLAP | exact duplicate envelope → suppress | overlap A | one candidate | — | — | — | — | — | CT-DUP-01 |
| CD-OVERLAP-2 | OVERLAP | same primary, different matches/rules → one candidate, union | overlap B | union provenance | — | — | — | — | — | CT-DUP-02 |
| CD-OVERLAP-3 | OVERLAP | nested context-only variants → one canonical maximal-lawful envelope | overlap C | canonical envelope | trigger-class union under §43.7 | §43.7 | — | window unioning past CONTEXT_MAX | — | CT-DUP-04 |
| CD-OVERLAP-4 | OVERLAP | distinct primary units with shared coverage → separate candidates | overlap D | both survive | — | — | — | similarity-based collapse | — | CT-DUP-06, CT-MULT-03 |
| CD-ORDER-1 | ORDER | output order: primary start → primary end → unit ID → rule ID | output | deterministic order | — | — | — | arrival-order effects | D10 (id timing untouched) | CT-ORD-02/03 |
| CD-ORDER-2 | ORDER | enumeration/concurrency/batch/event-order invariance | runtime | identical set + order | — | — | — | scheduling effects | — | CT-ORD-01..05 |
| CD-DIAG-1 | DIAG | invalid/missing span → diagnostic, no silent drop | bad span | diagnostic | — | — | — | silent deletion | — | CT-ORD-04 |
| CD-DIAG-2 | DIAG | malformed unit → sentence fallback + diagnostic | bad unit | fallback | CD-INPUT-4 | — | — | unit invention | protocol Layer-1 | CT-MULT-02 |
| CD-DIAG-3 | DIAG | unknown signal ID vs pinned SL → quarantine + diagnostic | version drift | no basis from unknowns | — | — | — | silent repair | SL pin | CT-ORD-01 |
| CD-DIAG-4 | DIAG | context unconstructible → emit without it + diagnostic | empty window | emission preserved | — | — | — | context-failure suppression | — | CT-CTX-04 |
| CD-DIAG-5 | DIAG | compound-envelope overflow: unsplittable over-envelope structure → diagnostic with all signal spans preserved; no truncated candidate; region unevaluated; completion attestation blocked | oversize unsplittable structure | honest incompleteness | MAX_COMPOUND | — | independently segmented units (evaluated per unit) | first-N truncation as sufficient representation | CD-CORE-10 | CT-MULT-06B, CT-MATCH-04 |
| CD-DIAG-6 | DIAG | unsupported region signal → diagnostic record, no candidate, reviewable | ineligible region | reviewability | CD-INPUT-3 | — | — | silent drop | — | CT-BND-09 |
| CD-DIAG-7 | DIAG | offset conflict → diagnostic; unit outside evaluated set until re-supplied | span disagreement | integrity | — | — | — | guessing offsets | — | CT-ORD-04 |
| CD-DIAG-8 | DIAG | stale/closed epoch or interrupted run → diagnostics; no completion attestation | epoch/limit | honest incompleteness | SM epoch | — | — | false completeness | SM v1.3 | CT-ORD-06 |
| CD-EVAL-1 | EVAL | CANDIDATE_MATCH_ALGORITHM_v1 per §43.24 (threshold-free containment + one-to-one assignment); development/calibration algorithm, not the protocol MATCH_CRITERION | evaluation | match verdicts for calibration evidence | gold layers | — | — | context-overlap credit; similarity matching; protocol-freeze claims | protocol §29.2; IN-1 | CT-MATCH-01..08 |
| CD-EVAL-2 | EVAL | candidate recall = matched gold GAP propositions / all gold GAP propositions (oracle regime, full gold population) | evaluation | metric | CD-EVAL-1 | — | — | — | protocol regimes | CT-MATCH-01 |
| CD-EVAL-3 | EVAL | candidate precision = matching candidates / all emitted candidates | evaluation | metric | CD-EVAL-1 | — | — | — | protocol | CT-MATCH-02 |
| CD-EVAL-4 | EVAL | candidate yield = candidates per manuscript | evaluation | metric | — | — | — | yield-driven suppression | — | — |
| CD-EVAL-5 | EVAL | candidate density = primary-span coverage / manuscript size | evaluation | metric | — | — | — | — | — | — |
| CD-EVAL-6 | EVAL | review load = candidate passages reaching Step 5 | evaluation | metric | — | — | — | — | — | — |
| CD-EVAL-7 | EVAL | miss taxonomy by rule/signal family | evaluation | diagnostics | — | — | — | — | — | — |
| CD-EVAL-8 | EVAL | span inflation = primary coverage beyond gold assertion span (context excluded) | evaluation | anti-gaming monitor | — | — | — | — | — | CT-MATCH-04 |
| CD-EVAL-9 | EVAL | numeric thresholds AND the formal protocol MATCH_CRITERION remain TBD_BY_FINAL_CALIBRATION; Step 10 freezes CANDIDATE_MATCH_ALGORITHM_v1 for development/calibration use; final calibration may adopt or amend it | evaluation | evaluation-timing policy | — | — | — | primacy-based thresholds; any claim that MATCH_CRITERION is frozen in Step 10 | protocol principle 8; IN-1 | — |
| CD-PREC-1 | CORE | deterministic decision procedure CD-1..CD-10 with the CD-4 direct / construction-qualified basis gate | any run | end-to-end detector pipeline | — | — | — | semantic consultation at any step | all pins | CT-ORD suite, CT-CTX-08, CT-CTX-09 |

## 43.24 Candidate-to-gold matching algorithm

**CD-EVAL-1 — CANDIDATE_MATCH_ALGORITHM_v1 (frozen for Step-10 development/calibration use; threshold-free; machine-computable). This is the Step-10 development/calibration matching algorithm, NOT the final protocol MATCH_CRITERION, which remains `TBD_BY_FINAL_CALIBRATION` (IN-1).** Evaluated against adjudicated gold (`gold_boundary_unit` → `gold_gap_instance`, protocol v1.2 §29.2/§29.3) on the shared normalized text and shared Layer-1 segmentation. A predicted candidate `c` MATCHES a gold GAP proposition `g` iff ALL hold:
1. **Same document identity:** c.document_id = g.document_id AND c.document_version = g.document_version.
2. **Primary containment:** g's deficiency-bearing assertion span (char offsets) ⊆ c.primary_span, where c.primary_span = the union of c's primary unit spans and NEVER includes context spans; equivalently satisfied by **unit correspondence**: c's primary unit set ⊇ g's adjudicated boundary unit(s) under the shared segmentation. No partial-overlap percentage exists anywhere.
3. **Context exclusion:** containment of g's span solely within c's context-support spans is NOT a match — context-only overlap never counts as detection.
4. **One-to-one assignment:** matching is a deterministic assignment computed as: for each gold proposition in document order, select among not-yet-assigned candidates satisfying (1)–(3) the candidate with maximum |primary_span ∩ gold assertion span|; ties → shortest primary span; ties → earliest primary start offset; ties → lowest CD-ORDER-1 ordinal. Each candidate is assigned to at most one gold proposition, UNLESS the gold record itself is a protocol-marked compound (one mixed unit yielding multiple gold instances), in which case each gold instance is assigned independently and one compound candidate may lawfully match each of them.
5. **Anti-gaming (structural):** CANDIDATE_MATCH_ALGORITHM_v1 cannot reward arbitrary whole-document spans because it operates ONLY over lawfully emitted candidates, whose primaries are bounded by the candidate envelope (§43.7); an over-envelope attempt is a detector diagnostic (CD-DIAG-5), not a lawful candidate, and residual looseness within the envelope is monitored by CD-EVAL-8 span inflation. Context expansion never affects matching (context is excluded). No claim is made here about the final calibrated MATCH_CRITERION beyond frozen Step-3 ownership.
A gold assertion span crossing unit boundaries that the detector emitted as a single narrower unit fails (2) and scores as a miss (E-CD-SPAN-UNDER) — under-spanning is a detection error, never excused by the algorithm.
**Ownership interface (frozen).** Step 10 owns and freezes `CANDIDATE_MATCH_ALGORITHM_v1` solely for development/calibration evaluation. Step 10 does NOT set, freeze, or own the formal protocol MATCH_CRITERION, which remains `TBD_BY_FINAL_CALIBRATION` under Protocol v1.2 and is frozen only during final calibration before sealed-cohort exposure.

## 43.25 Detection metrics

All Step-10 component metrics are computed in the protocol's **component/oracle regime** on the full gold population (gold segmentation, gold section roles), with operational/pipeline figures reported alongside and never substituted (protocol v1.2 principle 2). Metrics: **candidate recall** (CD-EVAL-2); **candidate precision** (CD-EVAL-3) — expected to be modest by design (recall-first; Step 5 is the precision stage); **candidate yield** (CD-EVAL-4); **candidate density** (CD-EVAL-5); **review load** (CD-EVAL-6); **miss taxonomy** by rule/signal family (CD-EVAL-7); **candidate-span inflation** (CD-EVAL-8), computed over primary spans only. No numeric acceptance thresholds are frozen here, and neither is the formal protocol MATCH_CRITERION: both remain `TBD_BY_FINAL_CALIBRATION` under Protocol v1.2 (CD-EVAL-9); all Step-10 metrics are computed with CANDIDATE_MATCH_ALGORITHM_v1 (IN-1), which final calibration may adopt or amend.

## 43.26 Normative test suite (60 rows: 52 emission tests + 8 matching-algorithm tests)

**Serialization contract** (glossary uses spaced " = " so documentation never matches a serialized `tag=value`): `test_id · text = the source passage (units separated by " | " when segmented) · sec = section role · sig = bracketed matched Step-7 IDs · xsig = bracketed context/anti/boundary IDs or [] · emit = expected detector result · n = expected candidate count · prim = primary unit index list · ctx = context unit index list or [] · rule = emitting CD rule list · why · down = what remains for Steps 5/6/8/9`. Closed emit vocabulary: {EMIT, EMIT_COMPOUND, NO_EMIT, SUPPRESS_DUPLICATE, DIAGNOSTIC_ONLY}. Units are numbered U1, U2, … in source order; where one row expects several candidates, per-candidate values in prim/ctx/rule are separated by ";" in candidate order; relations, kinds, objects, and verdicts appear NOWHERE. **Provenance:** every EMIT row records (1) at least one registered emitting CD-* rule, AND (2) every Step-7 signal participating in the licensing basis, in the field matching its frozen polarity — positive signals in `sig`; reference/context/anti/boundary signals in `xsig`. A lawful construction-qualified EMIT may therefore have sig=[] provided its licensing non-positive signal appears in xsig, the named CD rule explicitly licenses that signal + structural construction, and the row carries complete provenance; no EMIT row has neither sig nor xsig licensing provenance. **TEST-PROVENANCE invariant:** for every normative EMIT test, rule ≠ [] AND (sig ≠ [] OR xsig contains a signal explicitly licensed by the named construction-qualified CD rule); DIRECT emissions carry the positive basis in sig; CONSTRUCTION-QUALIFIED emissions may carry the participating signal in xsig per frozen Step-7 polarity. This is a serialization/testing distinction only and modifies no runtime polarity.

**Direct positive detection (13).**
CT-DIR-01 · text="Little is known about X." · sec=Introduction · sig=[SL-LIM-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · frozen example 1 · down=Step-5 boundary; Step-6 relation/kind.
CT-DIR-02 · text="Evidence about X is limited among frontline workers." · sec=Introduction · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · frozen example 2; restriction wording travels inside the unit untouched · down=all semantics.
CT-DIR-03 · text="No research has examined X." · sec=Literature Review · sig=[SL-ABS-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-2] · categorical absence · down=Step-6.
CT-DIR-04 · text="Existing methods cannot distinguish X from Y." · sec=Methods · sig=[SL-CSTR-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-3] · frozen example 4; Methods location irrelevant (CD-CORE-8) · down=Step-6.
CT-DIR-05 · text="Prior findings are inconsistent." · sec=Introduction · sig=[SL-CONF-2] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-4] · frozen example 6 · down=Step-6; contester resolution.
CT-DIR-06 · text="The model remains empirically untested." · sec=Discussion · sig=[SL-TEST-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-5] · frozen example 3 · down=Step-6; Step-8 object.
CT-DIR-07 · text="There is a gap in knowledge about X." · sec=Introduction · sig=[SL-GAPLEX-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · MODERATE assertive-existential frame is a basis · down=Step-5.
CT-DIR-08 · text="Research and practice remain poorly aligned." · sec=Discussion · sig=[SL-DISC-D2] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-6] · frozen example 5; both poles named · down=Step-6.
CT-DIR-09 · text="This assumption is mistaken." · sec=Introduction · sig=[SL-CHAL-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-7] · challenge basis; anaphoric subject also triggers T1 context where preceding unit exists · down=Step-6/8.
CT-DIR-10 · text="X lacks empirical support." · sec=Literature Review · sig=[SL-SUP-1] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · support-predicate basis · down=Step-6.
CT-DIR-11 · text="X has received no attention." · sec=Introduction · sig=[SL-ABS-7] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-2] · restored ABS-7 coverage; emission only — no downstream field output · down=Step-5/6.
CT-DIR-12 · text="No model explains X." · sec=Introduction · sig=[SL-ABS-8] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-2] · restored ABS-8 coverage; the theoretical-resource wording is preserved, never interpreted · down=Step-6.
CT-DIR-13 · text="No validated method exists to measure X." · sec=Methods · sig=[SL-ABS-9] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-2] · restored ABS-9 coverage; Methods location irrelevant (CD-CORE-8); FF-44 own-procedure forms remain non-triggers upstream · down=Step-6.

**Boundary-adjacent (11).**
CT-BND-01 · text="Future research should examine X." · sec=Conclusion · sig=[] · xsig=[FUTURE_RESEARCH_MODAL] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · no positive basis; boundary polarity never a basis (CD-EMIT-13) · down=nothing reaches Step 5 from this unit.
CT-BND-02 · text="Our study is limited by its cross-sectional design." · sec=Discussion · sig=[] · xsig=[SL-OWNLIM-1] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · frozen T-BND-11: OWN_STUDY_SUBJECT fires SL-OWNLIM-1 and NOT SL-CSTR-3; an anti-signal alone is never an emission basis — non-emission follows from the frozen Step-7 inventory, not from Step-10 boundary classification · down=nothing reaches Step 5 from this unit.
CT-BND-03 · text="This study is limited because few prior studies have examined X." · sec=Discussion · sig=[SL-LIM-2] · xsig=[SL-OWNLIM-1] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · SL §40.19 anchor: both propositions preservable · down=Step-5 splits own vs prior deficiency.
CT-BND-04 · text="We contribute by examining X for the first time." · sec=Introduction · sig=[] · xsig=[CONTRIBUTION_YIELD] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · contribution wording alone is never a gap signal (SL §40.21) · down=—.
CT-BND-05 · text="It is not true that little is known about X." · sec=Introduction · sig=[SL-LIM-1] · xsig=[negation_scope metadata] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · local predication fires inside embedding; negation retained, never stripped (CD-CONTEXT-4B) · down=Step-5 exclusion decision.
CT-BND-06 · text="Smith argues that little is known about X." · sec=Introduction · sig=[SL-LIM-1] · xsig=[SL-ATTR-1] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · frozen example 10; attribution inside primary, preserved · down=Step-5 adoption.
CT-BND-07 · text="Managers do not understand X." · sec=Introduction · sig=[] · xsig=[SL-WORLD-1] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · practitioner subject → no positive basis (SL-ABS-6 required_context unmet) · down=—.
CT-BND-08 · text="X is no longer unexplored." · sec=Introduction · sig=[] · xsig=[SL-TEMP-1, negation context] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · SL §40.26a rule B cancellation: positive signal does not fire → no basis · down=—.
CT-BND-09 · text="Table 3 caption: little is known about X." · sec=Results · sig=[SL-LIM-1] · xsig=[] · emit=DIAGNOSTIC_ONLY · n=0 · prim=[] · ctx=[] · rule=[CD-DIAG-6] · unsupported region; reviewable diagnostic, no silent drop · down=review.
CT-BND-10 · text="Implementation remains low, while evidence about its causes is limited." (GIVEN: one segmentation unit; frozen Step-7 matches sig=[SL-LIM-3], xsig=[SL-WORLD-2]) · sec=Discussion · sig=[SL-LIM-3] · xsig=[SL-WORLD-2] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · emission licensed by SL-LIM-3 alone; SL-WORLD-2 preserved as anti-signal provenance, never a veto and never itself a basis; no boundary verdict made · down=Step-5 MOTIVATION/OTHER vs GAP work.
CT-BND-11 · text="Implementation of X remains low." · sec=Discussion · sig=[] · xsig=[SL-WORLD-2] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · frozen T-BND-16: fires SL-WORLD-2 and NOT SL-LIM-3; an anti-signal alone is never an emission basis · down=nothing reaches Step 5 from this unit.

**Context-supported (9).**
CT-CTX-01 · text="Prior work has documented several coordination mechanisms. | These mechanisms remain unexplored in distributed settings." · sec=Introduction · sig=[SL-ABS-5] · xsig=[SL-COREF-1] · emit=EMIT · n=1 · prim=[U2] · ctx=[U1] · rule=[CD-EMIT-8] · frozen example 7; no object resolution occurs · down=Step-8 completion.
CT-CTX-02 · text="Model A predicts X. | This model remains untested." · sec=Introduction · sig=[SL-TEST-1] · xsig=[SL-COREF-1] · emit=EMIT · n=1 · prim=[U2] · ctx=[U1] · rule=[CD-EMIT-8] · frozen example 8 · down=Step-8 antecedent.
CT-CTX-03 · text="Several models exist. | Extensive work validates them. | Such evidence remains limited for SMEs." · sec=Literature Review · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U3] · ctx=[U2, U1] · rule=[CD-EMIT-8] · T5 ellipsis form; CONTEXT_MAX=2 captured innermost-first · down=Step-8/proposition completion.
CT-CTX-04 · text="This model remains untested." (document-initial unit) · sec=Abstract · sig=[SL-TEST-1] · xsig=[SL-COREF-1] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-8, CD-DIAG-4] · window unconstructible → emit + diagnostic, never suppression · down=Step-8 handles unresolved antecedent.
CT-CTX-05 · text="Little is known about X. | This gap persists." · sec=Discussion · sig=[SL-LIM-1, SL-GAPLEX-2] · xsig=[] · emit=EMIT · n=2 · prim=[U1; U2] · ctx=[— ; U1] · rule=[CD-EMIT-1; CD-EMIT-9] · frozen example 9: two candidates; restatement construction with mandatory backward context; no same-gap attachment · down=Step-9 identity.
CT-CTX-06 · text="This gap is addressed in the next section." · sec=Introduction · sig=[SL-GAPLEX-2] · xsig=[SL-REF-1] (frozen card surface "this gap" — upstream fact, not a Step-10 classification) · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · forward-reference predicate = CD-EMIT-9 non-trigger; WEAK match alone is no basis (CD-EMIT-13) · down=—.
CT-CTX-07 · text="[paragraph P1 ends] Several mechanisms were proposed. || [P2 begins] These mechanisms remain unexplored." · sec=Introduction · sig=[SL-ABS-5] · xsig=[SL-COREF-1] · emit=EMIT · n=1 · prim=[P2-U1] · ctx=[P1-Ulast] · rule=[CD-EMIT-8] · one lawful paragraph crossing at paragraph-initial primary (CD-CONTEXT-2) · down=Step-8.
CT-CTX-08 · text=U1 = preceding antecedent/context unit | U2 = referential unit containing a registered persistence construction (GIVEN frozen Step-7 output: a valid SL-REF-1 match already present on the referential expression in U2) · sec=Discussion · sig=[] · xsig=[SL-REF-1] · emit=EMIT · n=1 · prim=[U2] · ctx=[U1] · rule=[CD-EMIT-9] · Step 10 does not determine whether the source wording qualifies for SL-REF-1; given the already-valid frozen match, the co-located registered persistence construction forms a construction-qualified basis; backward context captured under the bounded envelope · down=Step-5 boundary; Step-9 identity/restatement handling.
CT-CTX-09 · text=referential unit with a forward-reference / non-persistence predicate (GIVEN frozen Step-7 output: a valid SL-REF-1 match already present on the referential expression) · sec=Discussion · sig=[] · xsig=[SL-REF-1] · emit=NO_EMIT · n=0 · prim=[] · ctx=[] · rule=[] · SL-REF-1 is present but no registered CD-EMIT-9 persistence/continuation construction is satisfied; no semantic judgement is made · down=nothing reaches Step 5 from this unit.

**Multiple signals / compounds (7).**
CT-MULT-01 · text="Little empirical evidence exists and findings remain inconsistent regarding X." (one unit) · sec=Introduction · sig=[SL-GAPLEX-4, SL-CONF-2] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-11] · one unit, one candidate, union provenance; one-vs-two-gaps is downstream · down=Steps 5/6/11.
CT-MULT-02 · text="Evidence on X is limited, while findings on Y remain inconsistent." · segmentation=[U1 | U2] · sec=Introduction · sig=[SL-LIM-3 in U1; SL-CONF-2 in U2] · xsig=[] · emit=EMIT · n=2 · prim=[U1; U2] · ctx=[] · rule=[CD-EMIT-12] · two clause units → two candidates · down=downstream segmentation semantics.
CT-MULT-03 · text=same sentence, segmentation cannot split · sec=Introduction · sig=[SL-LIM-3, SL-CONF-2] · xsig=[] · emit=EMIT_COMPOUND · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-12] · one bounded compound, internal signal spans preserved · down=Step-11 proposition boundaries.
CT-MULT-04 · text="Evidence on X is limited. | Evidence on X is limited." (adjacent repetition) · sec=Introduction · sig=[SL-LIM-3; SL-LIM-3] · xsig=[] · emit=EMIT · n=2 · prim=[U1; U2] · ctx=[] · rule=[CD-EMIT-1] · distinct positions, distinct candidates (CD-DEDUP-2) · down=Step-9 identity.
CT-MULT-05 · text="Evidence on X is limited | because existing theories cannot explain Y." · sec=Introduction · sig=[SL-LIM-3 in U1; SL-CSTR-1 in U2] · xsig=[] · emit=EMIT · n=2 · prim=[U1; U2] · ctx=[] · rule=[CD-EMIT-1; CD-EMIT-10] · reason clause carries its own basis; spawn decision not made here · down=I-16 upstream; Step-9 persistence links.
CT-MULT-06A · text=four segmented units U1 | U2 | U3 | U4, each carrying a valid positive basis · sec=Discussion · sig=[one family match per unit] · xsig=[] · emit=EMIT · n=4 · prim=[U1; U2; U3; U4] · ctx=[] · rule=[CD-EMIT-1 per unit] · MAX_COMPOUND never caps the number of independently segmented candidates; no overflow diagnostic · down=Steps 5/6 per candidate.
CT-MULT-06B · text=one structurally unsplittable region whose lawful representation would require a primary compound of more than MAX_COMPOUND units · sec=Discussion · sig=[all matched family signals, preserved in the diagnostic] · xsig=[] · emit=DIAGNOSTIC_ONLY · n=0 · prim=[] · ctx=[] · rule=[CD-DIAG-5] · no truncated candidate; region marked unevaluated; no detection-completion attestation for the run until resolved · down=reprocessing/review; no semantic gap count is interpreted.

**Duplication / overlap (6).**
CT-DUP-01 · event stream: same detector event delivered twice (identical doc/version/run/primary/envelope) · emit=SUPPRESS_DUPLICATE · n=1 · rule=[CD-DEDUP-1] · idempotence; union provenance unchanged · down=—.
CT-DUP-02 · two direct bases (SL-LIM-3 and SL-GAPLEX-3) match the same primary unit · sig=[SL-LIM-3, SL-GAPLEX-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1, CD-OVERLAP-2] · direct emission is licensed by the registered positive signals; overlap handling collapses the duplicate detector events on the same primary into one candidate with union provenance · down=—.
CT-DUP-03 · text="Evidence remains limited." at two distinct manuscript positions (Introduction; Discussion) · sig=[SL-LIM-3; SL-LIM-3] · xsig=[] · emit=EMIT · n=2 · prim=[U1; U2] · ctx=[] · rule=[CD-EMIT-1, CD-DEDUP-2] · each occurrence is independently licensed by SL-LIM-3; distinct source positions survive as two candidates; Step 9 owns SAME_GAP · down=Step-9.
CT-DUP-04 · primary U3 has a valid positive basis and two lawful context-trigger paths: T1 yields ctx=[U2], while T4 yields ctx=[U2,U1] · sig=[SL-TEST-1] · xsig=[SL-COREF-1, SL-REVERSAL-1] · emit=EMIT · n=1 · prim=[U3] · ctx=[U2,U1] · rule=[CD-EMIT-8, CD-OVERLAP-3] · SL-TEST-1 licenses emission; the context-trigger variants resolve to one canonical maximal-lawful envelope under trigger-class union · down=Step-8 interprets context; no semantic merge occurs.
CT-DUP-05 · concurrent workers each emit the same candidate · emit=SUPPRESS_DUPLICATE · n=1 · rule=[CD-DEDUP-1, CD-ORDER-2] · merge under idempotence · down=—.
CT-DUP-06 · text="Model A predicts X. | This model remains untested." where U1 also carries its own basis (SL-CHAL-1 on "Model A rests on a flawed premise" variant reading is absent — here U1 additionally contains "predictions remain unvalidated") · sig=[SL-TEST-2 in U1; SL-TEST-1 in U2] · emit=EMIT · n=2 · prim=[U1; U2] · ctx=[— ; U1] · rule=[CD-EMIT-5; CD-EMIT-8] · U1 is simultaneously a primary (own candidate) and context for U2's candidate — both survive separately (CD-OVERLAP-4) · down=Step-8/9.

**Section invariance (6).** Each row independently serializes the same proposition, "Evidence about X remains limited.", with sig=[SL-LIM-3], xsig=[], and rule=[CD-EMIT-1]; expected emission is identical across sections and only the frozen section-prior metadata differs.
CT-SECT-01 · text="Evidence about X remains limited." · sec=Introduction · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · prior=ELEVATED · section prior does not alter emission.
CT-SECT-02 · text="Evidence about X remains limited." · sec=Literature Review · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · prior=ELEVATED · section prior does not alter emission.
CT-SECT-03 · text="Evidence about X remains limited." · sec=Methods · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · prior=REDUCED · no veto (CD-CORE-8).
CT-SECT-04 · text="Evidence about X remains limited." · sec=Results · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · prior=REDUCED · no veto.
CT-SECT-05 · text="Evidence about X remains limited." · sec=Discussion · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · prior=NEUTRAL (SL-SECTION-10) · no veto.
CT-SECT-06 · text="Evidence about X remains limited." · sec=UNKNOWN_SECTION · sig=[SL-LIM-3] · xsig=[] · emit=EMIT · n=1 · prim=[U1] · ctx=[] · rule=[CD-EMIT-1] · prior=NEUTRAL (SL §40.28) · uncertain section never suppresses.

**Candidate-to-gold matching algorithm suite (8; mini-contract: `test_id · gold = gold assertion span(s) as [start,end) offsets or unit refs · cand = candidate primary span + ctx spans · m = MATCH | NO_MATCH · why`; offsets on the shared normalized text).**
CT-MATCH-01 · gold=[100,140) "Little is known about X." · cand: prim=[100,140), ctx=[] · m=MATCH · exact containment; clause 2.
CT-MATCH-02 · gold=[100,140) · cand: prim=[80,180) two-unit lawful compound containing the gold span · m=MATCH · candidate wider than gold but envelope-lawful; containment holds.
CT-MATCH-03 · gold=[60,95) (the antecedent sentence) · cand: prim=[100,140), ctx=[60,95) · m=NO_MATCH · gold region present only in context spans; clause 3.
CT-MATCH-04 · gold=[100,140) · attempted primary requires >MAX_COMPOUND contiguous units (unsplittable) · candidate=NONE · diagnostic=CD-DIAG-5 · m=NO_MATCH · the over-envelope structure produces no lawful candidate (no truncated candidate exists), the region is marked unevaluated, and the run's completion attestation is blocked — evaluation operates only over lawful emitted candidates.
CT-MATCH-05 · gold G1=[100,140), G2=[150,190) (two separate gold propositions) · cand: prim=[95,195) lawful three-unit compound · m=MATCH for exactly one (G1, max overlap; then candidate is assigned) · clause 4 one-to-one: G2 unmatched → E-CD-MISS unless another candidate covers it.
CT-MATCH-06 · gold = protocol-marked compound (one mixed unit, two gold instances) · cand: prim = the compound unit · m=MATCH for each gold instance · clause 4 compound exception.
CT-MATCH-07 · gold=[100,140) · two candidates: cand-A prim=[100,140); cand-B prim=[90,160) — equal containment, overlap |40| each · m=MATCH via cand-A · tie → shortest primary span.
CT-MATCH-08 · gold=[100,140) · two candidates with identical span [100,140) from different rules · m=MATCH via the earlier CD-ORDER-1 ordinal · final deterministic tie-break.

## 43.27 Order / concurrency suite (6)

CT-ORD-01 · reversed signal-match enumeration order · expected: identical candidate set, spans, provenance, order · CD-ORDER-2; unknown-ID quarantine (CD-DIAG-3) unaffected by order.
CT-ORD-02 · reversed unit processing order · identical output; ordering restored by CD-ORDER-1.
CT-ORD-03 · candidates with identical primary start (nested clause/sentence units) · order resolved by end offset, then unit ID, then rule ID — deterministic.
CT-ORD-04 · one unit carries an invalid span (CD-DIAG-1/7) · diagnostics identical across orders; no silent drop in any order.
CT-ORD-05 · concurrent evaluation, randomized batch partitions, duplicated event delivery · identical candidate universe (CD-ORDER-2 + CD-DEDUP-1).
CT-ORD-06 · resource limit interrupts evaluation before final unit · no completion attestation in any order; CD-DIAG-8 names the unevaluated region; completeness never falsely declared (CD-CORE-10).

## 43.28 Adversarial minimal pairs (32; emit L ‖ emit R · rule/sig · ctx · why · remains downstream)

MP-CD-01 · "Little is known about X." ‖ "It is not true that little is known about X." · EMIT ‖ EMIT · CD-EMIT-1/SL-LIM-1 both; right adds negation metadata · no ctx · local predication fires in the embedding; negation preserved, never stripped · Step-5 owns exclusion of the right.
MP-CD-02 · "Existing methods cannot identify X." ‖ "Our method does not identify X." · EMIT ‖ NO_EMIT · CD-EMIT-3/SL-CSTR-1 ‖ [] · none · right: own-study subject with "does not" — no registered STRONG/MODERATE positive surface fires (SL-CSTR-1 requires "cannot"; SL-OWNLIM-2's bracket covers design/sample/data, not method) — non-emission from frozen inventory, not classification · Step-5 never sees right.
MP-CD-03 · "No prior study has examined X." ‖ "We did not examine X." · EMIT ‖ NO_EMIT · CD-EMIT-2/SL-ABS-1 ‖ [] (sig=[], xsig=[], rule=[]) · none · right: SL-ABS-1's frozen own-study-procedure exclusion removes the basis, and no registered own-study anti-surface literally covers "we did not examine" — a single deterministic expected result; the removal is Step 7's, never Step 10's judgement · Step-5 unreachable for right.
MP-CD-04 · "Research and practice remain poorly aligned." ‖ "Managers remain poorly aligned." · EMIT ‖ NO_EMIT · CD-EMIT-6/SL-DISC-D2 ‖ [] (SL-WORLD-1 only) · none · both poles required; practitioner-only deficit carries no positive basis · Step-5 never sees right.
MP-CD-05 · "This model remains untested." ‖ "This model is tested here." · EMIT ‖ NO_EMIT · CD-EMIT-8/SL-TEST-1 + ctx ‖ [] · left ctx=preceding unit · right contains no deficiency signal; own-study testing assertion · Step-8 resolves left's antecedent.
MP-CD-06 · "This gap persists." ‖ "This gap is addressed below." · EMIT ‖ NO_EMIT · CD-EMIT-9/SL-GAPLEX-2 + construction ‖ non-trigger (forward-reference predicate) · left ctx mandatory · closed predicate lists decide, not semantics · Step-9 identity for left.
MP-CD-07 · "Evidence remains limited." ‖ "Our evidence is limited." · EMIT ‖ EMIT · CD-EMIT-1/SL-LIM-3 ‖ CD-EMIT-1/SL-LIM-3 · none · SL-LIM-3's adjectival-scarcity surface fires on both (no "limited by" construction; no registered own-study exclusion on the LIM-3 card, and SL-OWNLIM-1's bracket covers study/analysis/design, not evidence) · Step-5 owns the own-vs-prior evidence boundary for the right side.
MP-CD-08 · "Findings are inconsistent." ‖ "Our estimate is imprecise." · EMIT ‖ NO_EMIT · CD-EMIT-4/SL-CONF-2 ‖ [] · none · imprecision wording matches no registered family; no basis, no invention · —.
MP-CD-09 · "These mechanisms remain unexplored." ‖ "Coordination mechanisms remain unexplored." · EMIT+ctx ‖ EMIT · CD-EMIT-8 ‖ CD-EMIT-1-family basis (SL-ABS-5) without T1 form · left ctx=[preceding]; right ctx=[] · context capture is form-triggered only · Step-8 objects.
MP-CD-10 · "There is a gap in the literature on X." ‖ "The pay gap between groups widened." · EMIT ‖ NO_EMIT · CD-EMIT-1/SL-GAPLEX-1 ‖ [] (FF-01–07 non-firing) · none · SL false-friend exclusions remove the match upstream · —.
MP-CD-11 · "X was poorly understood until recently." ‖ "X is no longer poorly understood." · EMIT ‖ NO_EMIT · CD-EMIT-1/SL-LIM-5 + SL-TEMP-1 (rule A) ‖ cancellation (rule B) · none · historical deficiency emits with temporal metadata; cancellation removes the basis · Step-5/6 temporal semantics.
MP-CD-12 · "Although evidence is limited, recent work is promising." ‖ "Evidence was once limited; extensive studies now exist." · EMIT ‖ EMIT · SL-LIM-3 + SL-REVERSAL-1 ‖ SL-LIM-3 + SL-TEMP-1 + SL-REVERSAL-1 · T4 ctx where spans cross units · reversal marks, never deletes (SL §40.26) · Step-5 interpretation.
MP-CD-13 · "…because existing theories cannot explain Y." ‖ "…because such studies are expensive." · EMIT ‖ NO_EMIT · CD-EMIT-10/SL-CSTR-1 ‖ [] · none · reason clause emits only on its own basis; cost claims match nothing · I-16 spawn decision upstream.
MP-CD-14 · same deficiency sentence, Introduction ‖ Discussion · EMIT ‖ EMIT · CD-EMIT-1 both; CD-DEDUP-2 keeps both · none · positions differ → two candidates; identity is Step-9's · Step-9 SAME_GAP.
MP-CD-15 · "Few studies have examined X." ‖ "Few participants completed X." · EMIT ‖ NO_EMIT · SL-LIM-2 ‖ [] (knowledge-activity context unmet) · none · SL required_context decides · —.
MP-CD-16 · "The literature lacks evidence on X." ‖ "Firms lack resources for X." · EMIT ‖ NO_EMIT · SL-GAPLEX-3 ‖ [] (FF-30–32 → SL-WORLD) · none · lacked-object class decides upstream · —.
MP-CD-17 · "Support for the model is mixed." ‖ "The results do not support H1." · EMIT ‖ NO_EMIT · SL-SUP-3 ‖ [] (FF-46 own-result exclusion) · none · SL context metadata removes the basis · —.
MP-CD-18 · "X remains an open question." ‖ "We opened the questionnaire with X." · EMIT ‖ NO_EMIT · SL-ABS-5 ‖ [] · none · token-boundary and construction constraints · —.
MP-CD-19 · "Debate persists about X." ‖ "This gap persists." · EMIT ‖ EMIT · CD-EMIT-4/SL-CONF-5 ‖ CD-EMIT-9 construction · right ctx mandatory · two different registered routes to emission · Step-6 vs Step-9 downstream work.
MP-CD-20 · "We challenge the assumption that X." ‖ "X is a challenging problem." · EMIT ‖ NO_EMIT · SL-CHAL-3 ‖ [] (FF-26/27) · none · false-friend exclusion upstream · —.
MP-CD-21 · "No mechanism exists for translating research into practice." ‖ "No mechanism exists in the device." · EMIT ‖ NO_EMIT · SL-DISC-A1 ‖ [] (engineering sense FF) · none · family required_context · —.
MP-CD-22 · "Prior work is limited by small samples." ‖ "Access was limited to employees." · EMIT ‖ NO_EMIT · SL-CSTR-3 ‖ [] (FF-13-adjacent) · none · construction class decides · Step-6 for left.
MP-CD-23 · "The framework has yet to be evaluated." ‖ "The evaluation framework is described below." · EMIT ‖ NO_EMIT · SL-TEST-3 ‖ [] · none · predicate-pattern vs nominal compound · Step-6 for left.
MP-CD-24 · "Such evidence remains limited." ‖ "Such firms remain profitable." · EMIT+ctx ‖ NO_EMIT · CD-EMIT-8/SL-LIM-3 + T5 ‖ [] · left ctx=[preceding ≤2] · deficiency signal decides; "such" alone never does · Step-8/proposition completion.
MP-CD-25 · "To fill this gap, we conduct three studies." ‖ "This gap in knowledge about X remains." · NO_EMIT ‖ EMIT · [] (SL-CONTRIB-3 + SL-REF-1; INT-3) ‖ CD-EMIT-9/SL-GAPLEX-2 + continuation predicate · right ctx mandatory · response construction vs continuation construction · Step-9 for right.
MP-CD-26 · "Smith (2020) argues evidence is limited." ‖ "As Smith showed, evidence is now extensive." · EMIT ‖ NO_EMIT · SL-LIM-3 + SL-ATTR-1 ‖ [] (no deficiency predication of current state) · none · local predication test · Step-5 adoption for left.
MP-CD-27 · "Little is known about X (see Table 2)." ‖ table cell: "little is known" · EMIT ‖ DIAGNOSTIC_ONLY · CD-EMIT-1 ‖ CD-DIAG-6 · none · region map, not semantics · review for right.
MP-CD-28 · "Evidence is limited." + duplicate event delivery ‖ same sentence twice in text · SUPPRESS_DUPLICATE (n=1) ‖ EMIT (n=2) · CD-DEDUP-1 ‖ CD-DEDUP-2 · none · event identity vs source identity · Step-9 for right pair.
MP-CD-29 · "Findings remain contested." ‖ "The election remains contested." · EMIT ‖ NO_EMIT · SL-CONF-5 ‖ [] (knowledge-domain context) · none · required_context decides · —.
MP-CD-30 · "Understanding of X is incomplete." ‖ "The form was incomplete." · EMIT ‖ NO_EMIT · SL-LIM-5 ‖ [] · none · construction class · —.
MP-CD-31 · "Research has not reached practitioners." ‖ "The shipment has not reached customers." · EMIT ‖ NO_EMIT · SL-DISC-D1 ‖ [] · none · research-practice poles required · —.
MP-CD-32 · "A limitation of prior work is its reliance on X." ‖ "A limitation of our work is its reliance on X." · NO_EMIT ‖ NO_EMIT · [] ‖ [] · none · neither nominal-limitation construction matches a registered positive surface (SL-CSTR-3 is the predicate form "limited by …"; SL-OWNLIM-1's nominal bracket covers this study/our analysis/our design, not "our work") — absence of a registered surface, never boundary classification; the prior-vs-own distinction therefore never reaches Step 10 for this construction · miss-taxonomy visibility (CD-EVAL-7).

## 43.29 Step-3 validation mapping

Step-10 evaluation runs under protocol v1.2 unchanged: component/oracle regime for the candidate-detection COMPONENT_GATE population (full gold, gold upstream inputs); operational regime for pipeline reporting; defects map onto the four frozen classes (annotation_error · rulebook_ambiguity · schema_insufficiency · genuine_epistemic_ambiguity) — a detector rule whose non-trigger wording proves ambiguous in pilot is rulebook_ambiguity against THIS document, never a reinterpretation of the SL. Nothing in Step 3 is redesigned; `detection_candidate` remains the system-side interface object.

## 43.30 Error labels (component-level; never replacing Step-3 classes)

E-CD-MISS · E-CD-SPURIOUS · E-CD-SPAN-UNDER · E-CD-SPAN-OVER · E-CD-CONTEXT-MISSING · E-CD-CONTEXT-OVEREXPANSION · E-CD-DUPLICATE-EMISSION · E-CD-OVERLAP-COLLAPSE · E-CD-SIGNAL-MISAPPLICATION · E-CD-ANTI-SIGNAL-VETO · E-CD-SECTION-VETO · E-CD-ORDER-NONDETERMINISM · E-CD-UNSUPPORTED-REGION · E-CD-TRACE-LOSS.

## 43.31 Versioning

`candidate_detection_rules_version = A1E-CD-1.0`; rule IDs permanent; retired IDs never reused. Amendment classes: clarification · signal-application amendment · emission-rule amendment · candidate-envelope amendment · context-window amendment · dedup/overlap amendment · matching-algorithm amendment (protocol MATCH_CRITERION adoption is Step-3 final-calibration business, never amended here) · test-only amendment. Any semantic detector amendment states expected impact on: candidate recall; candidate precision; candidate yield; Step-5 review load; downstream extracted gaps; gold detection results. No global invalidation mechanics are built here.

## 43.32 Open decisions

- **OD-CD-1 (forward/cataphoric context).** v1.0 captures no forward context; cataphoric dependencies ("The following remains unknown: …") rely on unit segmentation keeping the material in-unit. Extension is a context-window amendment after pilot evidence. Blocks freeze: no.
- **OD-CD-2 (envelope-constant calibration).** MAX_COMPOUND=3 / CONTEXT_MAX=2 are frozen v1.0 values with recorded rationale; pilot may motivate a context-window amendment. Blocks freeze: no.
- **OD-CD-3 (non-normative LLM tooling).** Any LLM assistance is confined outside the emission path (triage/diagnostics presentation) and may never add, remove, re-span, or re-order candidates. Blocks freeze: no.
- **OD-CD-4 (formal MATCH_CRITERION).** CANDIDATE_MATCH_ALGORITHM_v1 is frozen for Step-10 development/calibration use. The formal protocol MATCH_CRITERION remains `TBD_BY_FINAL_CALIBRATION` and will be frozen only in the final calibration phase before sealed-cohort exposure. Blocks Step-10 freeze: NO — Step 10 has a deterministic evaluation algorithm and can be implemented and tested; formal protocol adoption remains correctly owned by Step-3 final calibration.
None of the must-freeze items (candidate definition; detection unit; envelope; emission logic; context capture; duplicate handling; overlap handling; ordering; the deterministic matching algorithm; universe-completion rule; ownership) is open.

## 43.33 Freeze check

| Check | PASS/FAIL | Evidence |
|---|---|---|
| **OWNERSHIP** | | |
| Step 10 emits candidates only | PASS | CD-CORE-1/5; no semantic field anywhere in output |
| Step 5 owns GAP boundary | PASS | CD-CORE-7; CT-BND suite; MP-CD-01/02/07/26/32 |
| Step 6 owns relation/kind | PASS | prohibited-inference column of every CD-EMIT-* row |
| Step 8 owns affected_object | PASS | CD-EMIT-8; CT-CTX-01/02; no object output |
| Step 9 owns identity/merge | PASS | CD-DEDUP-2; CT-DUP-03; MP-CD-14/28 |
| Steps 11–13 not implemented | PASS | no extraction/resolution/verification content |
| **DETECTION** | | |
| every candidate has a registered emission basis | PASS | CD-CORE-3; CD-EMIT-13; every EMIT row records a registered emitting rule plus complete licensing Step-7 provenance across sig/xsig according to frozen polarity |
| signal match never equals GAP verdict | PASS | CD-CORE-6; §43.8 |
| section prior never vetoes | PASS | CD-CORE-8; CT-SECT-01..06 |
| anti-signal never vetoes a positive candidate | PASS | CD-CORE-9; CT-BND-03; CT-BND-10; MP-CD-07 |
| context capture bounded | PASS | CD-CONTEXT-2 constants; CT-CTX-03/07 |
| no whole-section fallback | PASS | CD-INPUT-4; envelope §43.7 |
| no top-k / early stop | PASS | CD-CORE-11; CT-ORD-06 |
| attribution preserved | PASS | CD-CONTEXT-4A; CT-BND-06 |
| negation preserved | PASS | CD-CONTEXT-4B; CT-BND-05; MP-CD-01 |
| **DEDUP / OVERLAP** | | |
| exact source-event duplicates suppressed lawfully | PASS | CD-DEDUP-1; CT-DUP-01/05 |
| repeated assertions at different positions survive | PASS | CD-DEDUP-2; CT-DUP-03; CT-MULT-04 |
| overlapping distinct proposition candidates survive | PASS | CD-OVERLAP-4; CT-DUP-06 note: covered by CT-MULT-02/03 distinct units |
| no semantic deduplication | PASS | CD-DEDUP-2; CD-OVERLAP-4 |
| **DETERMINISM** | | |
| input-order invariant | PASS | CD-ORDER-2; CT-ORD-01/02 |
| concurrency invariant | PASS | CD-ORDER-2; CT-ORD-05 |
| candidate ordering deterministic | PASS | CD-ORDER-1; CT-ORD-03 |
| same input/version → same candidate universe | PASS | CD-CORE-4; CT-ORD suite |
| **EVALUATION** | | |
| Step 10 owns CANDIDATE_MATCH_ALGORITHM_v1 | PASS | §43.1 ownership list; §43.24 ownership interface |
| Step 10 does NOT own the formal MATCH_CRITERION | PASS | §43.1 non-owned list; §43.24 ownership interface; CD-EVAL-9 |
| CANDIDATE_MATCH_ALGORITHM_v1 deterministic and fully specified | PASS | CD-EVAL-1: containment + deterministic one-to-one assignment; no thresholds |
| formal MATCH_CRITERION remains explicitly TBD_BY_FINAL_CALIBRATION | PASS | IN-1; CD-EVAL-9; OD-CD-4; declaration |
| no Step-10 wording claims protocol-level MATCH_CRITERION freeze | PASS | terminology sweep: freeze claims attach only to the algorithm |
| no sealed-cohort evaluation before final calibration freezes MATCH_CRITERION | PASS | IN-1 final sentence; protocol principle 9 |
| context-only overlap never counts | PASS | CD-EVAL-1 clause 3; CT-MATCH-03 |
| recall / precision / yield / review load defined | PASS | CD-EVAL-2..6 |
| algorithm cannot reward oversized passages | PASS | operates only over lawful emitted candidates; envelope bound; CD-DIAG-5; CD-EVAL-8 |
| **SIGNAL COVERAGE (10A)** | | |
| every STRONG/MODERATE positive SL signal mapped to an emission rule | PASS | §43.8 matrix: 49 positive IDs, zero orphans |
| SL-ABS-7 covered | PASS | CD-EMIT-2; CT-DIR-11 |
| SL-ABS-8 covered | PASS | CD-EMIT-2; CT-DIR-12 |
| SL-ABS-9 covered | PASS | CD-EMIT-2; CT-DIR-13 |
| no test invents a positive firing the frozen SL withholds | PASS | own-study audit vs T-BND-11 and family cards; CT-BND-02, MP-CD-02/03/32 corrected |
| own-study non-triggers remain non-triggers absent an independent positive | PASS | CT-BND-02 NO_EMIT; CT-BND-03 EMIT on SL-LIM-2 |
| CD-EMIT-2 prose, registry, coverage matrix, and tests all agree on SL-ABS-1..9 | PASS | §43.11; §43.23 row; §43.8 matrix; CT-DIR-03/11/12/13 |
| SL-WORLD-1/2 both survive the Step-7 → Step-10 anti-signal interface | PASS | CD-INPUT-1 (H); CD-EMIT-13 enumeration |
| SL-WORLD-2 alone never emits | PASS | CT-BND-11 (frozen T-BND-16) |
| SL-WORLD-2 never vetoes an independently valid positive basis | PASS | CT-BND-10: EMIT on SL-LIM-3 with SL-WORLD-2 preserved |
| **COMPOUND OVERFLOW (10A)** | | |
| segmented signal-bearing units never discarded by MAX_COMPOUND | PASS | CD-DIAG-5 scope clause; CT-MULT-06A n=4 |
| over-envelope unsplittable structures are diagnostic-only | PASS | CD-DIAG-5; CT-MULT-06B |
| over-envelope diagnostics block detection-completion attestation | PASS | CD-DIAG-5 + CD-CORE-10; CT-MULT-06B |
| no first-N truncation silently removes positive material | PASS | truncation removed from CD-DIAG-5; prohibited-inference cell |
| **EXECUTION CLOSURE (10C)** | | |
| SL-REF-1 exists in the closed Step-10 input contract | PASS | CD-INPUT-1 (G) |
| SL-REF-1 alone does not emit | PASS | CD-EMIT-9 non-bases; CT-CTX-09 |
| SL-REF-2 alone does not emit | PASS | CD-EMIT-9 non-bases; IN-2; interface summary |
| CD-EMIT-9 construction alone does not emit | PASS | persistence predicate alone → NO_EMIT (CD-EMIT-9; CD-4) |
| valid frozen SL-REF-1 match + registered persistence construction emits | PASS | CT-CTX-08 |
| CD-PREC-1 reaches CD-EMIT-9 for a construction-qualified basis | PASS | CD-4(B); execution trace |
| CT-CTX-08 proves the positive SL-REF-1 route | PASS | deterministic EMIT, n=1, ctx=[U1] |
| CT-CTX-09 proves the forward-reference non-trigger | PASS | deterministic NO_EMIT |
| CD-EMIT-9 prose and machine registry are identical | PASS | basis formula and non-trigger sets aligned verbatim |
| no direct Step-7 polarity has been changed | PASS | polarity labels untouched; participation ≠ relabeling |
| **UPSTREAM OWNERSHIP (10D)** | | |
| Step 10 does not define or expand SL-REF-1 surface forms | PASS | deficiency-head lexicon removed; §14 surface-claim audit clean |
| all SL-REF-1 matches consumed as frozen Step-7 outputs | PASS | CD-EMIT-9 (A)(2); CD-4(B); traces GIVEN-style |
| CD-EMIT-9 adds only an operational construction, never a Step-7 signal | PASS | construction defined over already-valid matches |
| **TEST PROVENANCE (10D)** | | |
| every EMIT row has a registered CD rule | PASS | TEST-PROVENANCE invariant; row scan |
| every EMIT row has complete licensing Step-7 provenance across sig/xsig | PASS | contract §43.26; row scan |
| direct emissions use sig | PASS | CT-DIR/BND/MULT EMIT rows |
| construction-qualified emissions may use xsig | PASS | CT-CTX-08 sig=[] + xsig=[SL-REF-1] lawful |
| no runtime polarity changed by test serialization | PASS | serialization/testing distinction stated in contract |
| **REGISTRY** | | |
| every normative CD-* ID registered exactly once | PASS | §43.23; dual-grammar scan zero undefined, zero duplicates |
| no pseudo-ranges | PASS | row-per-ID |
| every test deterministic | PASS | closed emit vocabulary; single expected outcome per row |
| every emission names registered provenance | PASS | rule plus complete licensing signal provenance across sig/xsig per frozen Step-7 polarity; direct EMIT tests have non-empty sig; construction-qualified EMIT tests may have sig=[] only with the licensing signal in xsig — CT-CTX-08 is the normative example |
| every cited SL-* ID exists in pinned `A1E-SL-1.1` | PASS | ID audit against verified registry; families cited by name where IDs unverified (IN-3) |
| human-readable CD-EMIT-2 and machine registry identical | PASS | prose/registry/matrix three-way scan |
| every complete Step-7 signal-set enumeration synchronized with the pinned SL | PASS | REFERENCE SL-REF-1/2; POSITIONING SL-POS-1/2/3/4; CONTEXT SL-ATTR-1/2, SL-REVERSAL-1, SL-COREF-1, SL-TEMP-1, SL-CITE-1; ANTI SL-OWNLIM-1/2, SL-WORLD-1/2; boundary families FUTURE_RESEARCH_MODAL / CONTRIBUTION_YIELD / MATTERING_STAKES; frozen Step-7 categories preserved; positives per matrix |
| **BOUNDARY** | | |
| no hidden Step-5 classifier | PASS | §32 audit: every non-emission traces to SL non-firing or CD-EMIT-13 polarity/tier |
| no hidden Step-6 classifier | PASS | no CD rule named or behaving as a relation; §33 audit |
| no hidden Step-8 extraction | PASS | no object output; context = spans only |
| no hidden Step-9 merge | PASS | CD-DEDUP-2; no similarity anywhere |
| no Step-11/12/13 implementation | PASS | §44 respected |
| **MATCHING ALGORITHM SUITE (CT-MATCH-01..08)** | | |
| exact match scores | PASS | CT-MATCH-01: gold span = primary span → MATCH |
| lawful wider candidate scores | PASS | CT-MATCH-02: compound primary ⊇ gold span → MATCH |
| context-only overlap fails | PASS | CT-MATCH-03: gold span inside ctx only → NO_MATCH |
| oversize passage cannot score | PASS | CT-MATCH-04: over-envelope attempt → no candidate, CD-DIAG-5 diagnostic, NO_MATCH |
| one candidate, two golds | PASS | CT-MATCH-05: assignment gives the max-overlap gold; second gold unmatched unless compound-marked (CT-MATCH-06: protocol compound → both match) |
| deterministic ties | PASS | CT-MATCH-07: equal overlap → shortest primary; CT-MATCH-08: full tie → earliest start, then ordinal |

**All internal Step-10 checks PASS — Candidate Detection Spec v1.0 (`A1E-CD-1.0`) is presented as READY FOR INDEPENDENT FREEZE AUDIT, pinned to `A1E-GS-1.3`, `A1E-BR-1.2`, `A1E-DPR-1.1`, `A1E-SL-1.1`, `A1E-OR-1.1`, and `A1E-GI-1.0`.**

**The formal protocol MATCH_CRITERION remains TBD_BY_FINAL_CALIBRATION; Step 10 freezes only CANDIDATE_MATCH_ALGORITHM_v1 for deterministic development/calibration use.**
