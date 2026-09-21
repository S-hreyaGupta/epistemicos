---
document_id: citation_v3_4_conformance_matrix_freeze_checklist
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
status: review_candidate_supporting_evidence
---

# Citation v3.4 — Conformance Matrix / Freeze Checklist

This matrix binds to the exact rc2 candidate bytes above. `DEFINED` means an executable case is specified; it does not claim the case has run.

## 1. Evidence states

```text
DEFINED
PENDING_EXECUTION
PASS
FAIL
BLOCKED_DEPENDENCY
OUTSIDE_PILOT
```

## 2. Conformance matrix

| ID | Normative requirement | Scope | Evidence | Required assertion | Coverage | State |
|---|---|---|---|---|---|---|
| C-001 | invalid UTF-8 aborts before processing | pilot | golden bytes | invalid UTF-8 → exit5; exactly meta+error | DEFINED | PENDING_EXECUTION || C-002 | CRLF/lone CR→LF then NFC | pilot | byte golden | canonical bytes exactly pinned | DEFINED | PENDING_EXECUTION || C-003 | all manuscript coordinates are UTF-8 bytes | pilot | byte-offset golden | β, —, ’, ﬁ spans slice exact bytes | DEFINED | PENDING_EXECUTION || C-004 | only OSA/CORE/overlong use code-point counts | pilot | unit tests | multibyte boundary cases | DEFINED | PENDING_EXECUTION || C-005 | standalone heading contract | pilot | goldens | declared heading cases pass/fail deterministically | DEFINED | PENDING_EXECUTION || C-006 | references_source=detected | pilot | golden | explicit bibliography heading | DEFINED | PENDING_EXECUTION || C-007 | references_source=inferred | pilot | golden | plain References + threshold | DEFINED | PENDING_EXECUTION || C-008 | inferred threshold does not overtrigger | pilot | golden | 2 entry starts/prose mention do not infer | DEFINED | PENDING_EXECUTION || C-009 | references_source=not_available is supported | pilot | golden | extract, no identity/reconcile, one bibliography_absent | DEFINED | PENDING_EXECUTION || C-010 | in-envelope parenthetical candidate never silently drops | pilot | goldens | parse or unresolved_citation | DEFINED | PENDING_EXECUTION || C-011 | in-envelope narrative candidate never silently drops | pilot | goldens | parse or unresolved_citation | DEFINED | PENDING_EXECUTION || C-012 | six-token narrative cap absent | pilot | golden | long author phrase preserved | DEFINED | PENDING_EXECUTION || C-013 | arbitrary longest-suffix parsing forbidden | pilot | golden | World Bank never becomes Bank | DEFINED | PENDING_EXECUTION || C-014 | all-caps first author rejection | pilot | golden | OECD → all_caps_surname | DEFINED | PENDING_EXECUTION || C-015 | unsupported prefix uses no_grammar_match with verbatim span | pilot | golden | span/offsets preserved | DEFINED | PENDING_EXECUTION || C-016 | all closed PREFIX forms parse | pilot | synthetic suite | one case per prefix | DEFINED | PENDING_EXECUTION || C-017 | PREFIX longest-match precedence | pilot | golden | multiword prefix not decomposed | DEFINED | PENDING_EXECUTION || C-018 | every STOP token has deterministic behavior | pilot | synthetic suite | one case per STOP token | DEFINED | PENDING_EXECUTION || C-019 | STOP reduction is additive | pilot | golden | full phrase + reduced candidate retained | DEFINED | PENDING_EXECUTION || C-020 | author_phrase remains complete source surface | pilot | golden | STOP never rewrites source field | DEFINED | PENDING_EXECUTION || C-021 | possessive surname normalization affects person candidate only | pilot | golden | Fine's→fine candidate; surface unchanged | DEFINED | PENDING_EXECUTION || C-022 | surface key is JSON array | pilot | byte golden | ["smith",2020], not encoded string | DEFINED | PENDING_EXECUTION || C-023 | surface key lower+whitespace only | pilot | golden | punctuation and and/& remain surface-distinct | DEFINED | PENDING_EXECUTION || C-024 | surface key never enters identity/reconciliation | pilot | instrumentation assertion | resolver input excludes surface key | DEFINED | PENDING_EXECUTION || C-025 | distinct_surface_groups always emitted | pilot | summary golden | present with and without bibliography | DEFINED | PENDING_EXECUTION || C-026 | sentence_index continuity | pilot | golden | continuous across headings | DEFINED | PENDING_EXECUTION || C-027 | previous_sentence_end | pilot | golden | null first; exact prior end otherwise | DEFINED | PENDING_EXECUTION || C-028 | standalone positional flag | pilot | golden | citation-only sentence true | DEFINED | PENDING_EXECUTION || C-029 | reference assembly deterministic | pilot | golden | line join/source spans exact | DEFINED | PENDING_EXECUTION || C-030 | no-year entry emits unresolved_reference(no_year) | pilot | golden | no reference row/key | DEFINED | PENDING_EXECUTION || C-031 | unresolved_reference reasons closed | pilot | schema rejection | only entry_start_grammar|orphan_line|no_year | DEFINED | PENDING_EXECUTION || C-032 | reference suspect reasons ordered | pilot | golden | terminator, overlong, embedded_entry_pattern order | DEFINED | PENDING_EXECUTION || C-033 | person-list reference identity | pilot | golden | ordered authors and person key | DEFINED | PENDING_EXECUTION || C-034 | full-forename reference first-surname identity | pilot | golden | authors=null; no structure check | DEFINED | PENDING_EXECUTION || C-035 | non-person reference identity | pilot | golden | World Bank key | DEFINED | PENDING_EXECUTION || C-036 | unsupported comma-containing organization remains unresolved | pilot | golden | no guessed reference identity | DEFINED | PENDING_EXECUTION || C-037 | 3×3 no/no | pilot | golden/injection | not_resolved; null citation_key | DEFINED | PENDING_EXECUTION || C-038 | 3×3 unique/no | pilot | golden/injection | full_phrase authoritative identity | DEFINED | PENDING_EXECUTION || C-039 | 3×3 nonunique/no | pilot | golden/injection | full_phrase + ambiguous_citation | DEFINED | PENDING_EXECUTION || C-040 | 3×3 no/unique | pilot | golden/injection | stop_reduced authoritative identity | DEFINED | PENDING_EXECUTION || C-041 | 3×3 no/nonunique | pilot | golden/injection | stop_reduced + ambiguous_citation | DEFINED | PENDING_EXECUTION || C-042 | 3×3 unique/unique different keys | pilot | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION || C-043 | 3×3 unique/nonunique different keys | pilot | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION || C-044 | 3×3 nonunique/unique different keys | pilot | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION || C-045 | 3×3 nonunique/nonunique different keys | pilot | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION || C-046 | same candidate identity double resolution aborts | pilot | invariant injection | exit6 exact meta+error | DEFINED | PENDING_EXECUTION || C-047 | shared reference index across different candidate keys is allowed | pilot | injection | ambiguity, not exit6 | DEFINED | PENDING_EXECUTION || C-048 | ambiguous_author_resolution schema exact | pilot | byte golden | candidate states/keys/index arrays | DEFINED | PENDING_EXECUTION || C-049 | author-resolution ambiguity reserves references | pilot | golden | no mismatch/uncited compounding | DEFINED | PENDING_EXECUTION || C-050 | duplicate-key ambiguity reserves all duplicate refs | pilot | golden | duplicate+ambiguous; no false uncited | DEFINED | PENDING_EXECUTION || C-051 | reserved is not uniquely matched | pilot | summary assertion | counts +0 absent independent match | DEFINED | PENDING_EXECUTION || C-052 | identity partition is exact | pilot | summary invariant | resolved + author_ambiguous + not_resolved = extracted | DEFINED | PENDING_EXECUTION || C-053 | candidate-level missing_reference does not establish citation identity | pilot | golden | citation_key null; identity_authority=candidate | DEFINED | PENDING_EXECUTION || C-054 | candidate-level possible_mismatch does not establish citation identity | pilot | golden | citation_key null; identity_authority=candidate | DEFINED | PENDING_EXECUTION || C-055 | two unmatched identity candidates suppress missing/mismatch diagnostic | pilot | golden | identity_not_resolved only | DEFINED | PENDING_EXECUTION || C-056 | surname_edit_distance_1 precedence | pilot | golden | same kind/year; CORE bound | DEFINED | PENDING_EXECUTION || C-057 | year_adjacent precedence | pilot | golden | same identity phrase; ±1 year | DEFINED | PENDING_EXECUTION || C-058 | year_transposition precedence | pilot | golden | one adjacent digit swap | DEFINED | PENDING_EXECUTION || C-059 | candidate/reference author kind must agree for mismatch pairing | pilot | golden | cross-kind pair forbidden | DEFINED | PENDING_EXECUTION || C-060 | merge_suspected requires candidate author phrase + year | pilot | golden | targeted, not global | DEFINED | PENDING_EXECUTION || C-061 | uncited_reference excludes exact matches, reserved refs, mismatch-paired refs | pilot | golden | only true residual unique refs | DEFINED | PENDING_EXECUTION || C-062 | exact author-structure mismatch count | pilot | golden | count failure emits and exit1 | DEFINED | PENDING_EXECUTION || C-063 | exact author-structure mismatch order | pilot | golden | order failure emits and exit1 | DEFINED | PENDING_EXECUTION || C-064 | et_al structure threshold uses 3 | pilot | golden | <3 reports; threshold profile-pinned | DEFINED | PENDING_EXECUTION || C-065 | et_al mismatch alone does not force exit1 | pilot | golden | reported, exit unaffected absent other findings | DEFINED | PENDING_EXECUTION || C-066 | bibliography_absent uses not_evaluated identity state | pilot | byte golden | citation rows undetermined/not_evaluated | DEFINED | PENDING_EXECUTION || C-067 | bibliography_absent summary nullability | pilot | byte golden | identity/reconciliation counts null as specified | DEFINED | PENDING_EXECUTION || C-068 | canonical JSON serialization | pilot | byte comparison | key order, escapes, LF, raw non-ASCII | DEFINED | PENDING_EXECUTION || C-069 | every serialized block has total order | pilot | determinism golden | no tied distinct records | DEFINED | PENDING_EXECUTION || C-070 | multi-year citation ordering | pilot | byte golden | same segment 2020/2021 deterministic | DEFINED | PENDING_EXECUTION || C-071 | stdout/file bytes identical | pilot | file golden | --out exact stdout bytes | DEFINED | PENDING_EXECUTION || C-072 | directory output filename is canonical_sha256 | pilot | file golden | content-derived name | DEFINED | PENDING_EXECUTION || C-073 | atomic publication | pilot | fault injection | no partial authoritative file | DEFINED | PENDING_EXECUTION || C-074 | exit2 unsupported-style detector | pilot | golden | numeric/superscript dominance condition | DEFINED | PENDING_EXECUTION || C-075 | exit4 heading contract | pilot | golden | exact meta+error | DEFINED | PENDING_EXECUTION || C-076 | exit5 invalid UTF-8 | pilot | golden | exact meta+error | DEFINED | PENDING_EXECUTION || C-077 | exit6 invariant failure | pilot | injection | exact meta+error; no normal records | DEFINED | PENDING_EXECUTION || C-078 | normal exit1 findings closed | pilot | golden set | each defined finding forces/does not force per spec | DEFINED | PENDING_EXECUTION || C-079 | square-bracket author-year is out of envelope | pilot | golden | no citation identity record | DEFINED | PENDING_EXECUTION || C-080 | numeric citations never become identity records | pilot | golden | only style detector behavior | DEFINED | PENDING_EXECUTION || C-081 | 11-paper corpus has no unresolved blocking finding | pilot | corpus report | all unexpected findings dispositioned by B1-B10 | DEFINED | PENDING_EXECUTION || C-082 | bounded termination on corpus/synthetic stress | pilot | timed test | no hang | DEFINED | PENDING_EXECUTION || C-083 | same pilot inputs produce byte-identical output across two runs | pilot | byte comparison | determinism | DEFINED | PENDING_EXECUTION || C-084 | map-consuming standalone scope uses valid map and rejects invalid map | standalone_map | integration golden | separate scope; no fallback on invalid map | DEFINED | OUTSIDE_PILOT || C-085 | orchestrated scope requires current map/review state | pipeline | integration | separate scope | DEFINED | OUTSIDE_PILOT || C-086 | orchestrated mode fingerprint includes exact map bytes | pipeline | integration | determinism tuple | DEFINED | OUTSIDE_PILOT |

## 3. Blocking-finding taxonomy for the regression corpus

A corpus finding is blocking if it reveals:

```text
B1  output contradicts a normative rule
B2  in-envelope candidate silently dropped
B3  false extracted citation/reference content, false identity, or false diagnostic
B4  invariant/partition/cardinality/closed-enum violation
B5  deterministic ordering/canonical-byte failure
B6  exit/abort/atomic-publication failure
B7  bounded-termination failure or hang
B8  declared scope behavior violation
B9  supported input has undefined behavior
B10 pinned dependency/authority incompatibility
```

A non-blocking disposition MUST cite the exact governing rule establishing the envelope boundary, accepted limitation, unsupported class, expected ambiguity/non-resolution, or explicit deferral.

## 4. GSD-pilot freeze checklist

### 4.1 Candidate identity

- [x] Architecture v3.4 rc2 bound by SHA.
- [x] Level-5 execution v3.4 rc2 bound by SHA.
- [x] Pilot target scope is `citation_v3_4_standalone_cli_nomap_apa7_like_v1`.
- [x] Pilot target has no Section Map or Orchestrator runtime dependency.
- [x] Map/pipeline scopes remain separately declared and non-authoritative.

### 4.2 Static closure

- [x] Candidate envelope closed.
- [x] Byte-coordinate invariant closed with exactly three code-point-count exceptions.
- [x] PREFIX and STOP vocabularies closed.
- [x] Surface grouping separated from identity.
- [x] `unresolved_citation` is extraction failure; identity uses `not_resolved`/`not_evaluated`.
- [x] Bibliography-grounded identity authority closed.
- [x] Candidate-level missing/mismatch diagnostics cannot establish `citation_key`.
- [x] 3×3 identity table closed.
- [x] Ambiguity reservation closed.
- [x] No-year reference behavior closed.
- [x] Summary partitions and nullability closed.
- [x] JSONL serialization, total ordering, exits and atomicity closed.
- [x] Test-only invariant-injection seam closed.

### 4.3 Pilot-scope executable evidence

Before the pilot target may become `current`:

- [ ] C-001 through C-083 have accepted evidence.
- [ ] Every PREFIX is covered.
- [ ] Every STOP token is covered.
- [ ] All nine 3×3 cells are covered.
- [ ] Exit6 invariant injection passes.
- [ ] HIGH-rung focused deterministic-kernel evidence is accepted.
- [ ] 11-paper regression corpus has no unresolved B1–B10 finding.
- [ ] Unicode 15.0.0 behavior required by the spec is demonstrated in the implementation environment.

### 4.4 Independent review / freeze

- [ ] Independent reviewer receives sealed exact rc2 bytes.
- [ ] Raw findings and reviewer/model provenance are retained.
- [ ] Review binds spec id, version, candidate revision and SHA.
- [ ] No blocking finding remains open/rebuttal_pending/escalated.
- [ ] Any normative post-review change increments candidate revision and is re-reviewed.
- [ ] Final freeze/disposition exists.
- [ ] `content_state=frozen`.
- [ ] `citation_v3_4_standalone_cli_nomap_apa7_like_v1 → authority_state=current`.

### 4.5 GSD-pilot preflight

The pilot runbook may proceed through **Execute/Verify** only if all of:

```text
exact Level-5 spec artifact is frozen
pilot target scope authority_state = current
manual comparator artifact is frozen/hashed in the pilot baseline
installed GSD preflight conditions in PILOT_RUNBOOK (6) pass
```

If the spec is still `review_candidate`, the Citation product task is **not eligible for Execute/Verify** under the technical-spec standard. Do not let GSD planning or code establish missing normative behavior.

## 5. Non-pilot scope gates

C-084 requires a frozen/current Section Map v1.1 artifact.

C-085/C-086 additionally require the current compatible Orchestrator contract.

These do not block pilot-scope freeze or pilot-scope GSD execution.

## 6. Current verdict

```text
STATIC PILOT-SCOPE CONTENT: CLOSED
EXECUTABLE EVIDENCE:       PENDING
INDEPENDENT REVIEW:        PENDING
FROZEN/CURRENT AUTHORITY:  NOT YET ESTABLISHED
SECTION MAP:               NOT A PILOT-SCOPE BLOCKER
GSD EXECUTE/VERIFY:        ELIGIBLE ONLY AFTER PILOT SCOPE FREEZE
```
