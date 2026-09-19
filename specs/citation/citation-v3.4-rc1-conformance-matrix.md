---
document_id: citation_v3_4_conformance_matrix_freeze_checklist
version: "1.0"
bound_architecture:
  spec_id: citation_architecture
  spec_version: "3.4"
  candidate_revision: 1
  sha256: 6a615c8136543ef492598196a918b2c1e4b62bb54fdbcca4bd12af28bac66cb0
bound_execution_spec:
  spec_id: citation_execution_conformance
  spec_version: "3.4"
  candidate_revision: 1
  sha256: 11edbf8918224c0ee1ac85423db1f676fe49ca1feceecf1575c4a1daa2976695
status: review_candidate_supporting_evidence
---

# Citation v3.4 — Conformance Matrix / Freeze Checklist

This matrix binds to the exact candidate bytes named in front matter. It distinguishes **specification coverage** from **executed evidence**. A row marked `DEFINED` means the freeze-ready candidate specifies an executable test; it does not claim the test has already passed.

## 1. Status vocabulary

```text
DEFINED             normative behavior + executable case are specified
PENDING_EXECUTION   test/prototype/corpus evidence has not yet been executed/attached
PASS                executable evidence has been run and accepted
FAIL                evidence contradicts the candidate
BLOCKED_DEPENDENCY  external freeze/current dependency is not yet established
```

At generation time, the candidate package is content-complete but not self-certified. Therefore evidence rows begin as `PENDING_EXECUTION` unless an external prerequisite is already demonstrably absent, in which case they are `BLOCKED_DEPENDENCY`.

## 2. Conformance matrix

| ID | Normative requirement | Scope | Required evidence | Mandatory vector / assertion | Spec coverage | Evidence state |
|---|---|---|---|---|---|---|
| C-001 | invalid UTF-8 aborts before processing | both | golden bytes | malformed UTF-8 → exit 5, exactly meta+error | DEFINED | PENDING_EXECUTION |
| C-002 | CRLF/lone CR→LF then NFC | both | byte golden | decomposed Unicode + CRLF canonicalizes to pinned bytes | DEFINED | PENDING_EXECUTION |
| C-003 | manuscript coordinates are UTF-8 bytes | both | byte-offset golden | text containing β, —, ’, ﬁ; all spans slice exact source bytes | DEFINED | PENDING_EXECUTION |
| C-004 | only OSA/CORE/overlong use code-point counts | both | unit tests | multibyte cases preserve code-point semantics for the three exceptions | DEFINED | PENDING_EXECUTION |
| C-005 | standalone heading contract | standalone | golden | ≥2 h1 +0 h2 → exit4; h2 structure passes | DEFINED | PENDING_EXECUTION |
| C-006 | references_source=detected | standalone | golden | explicit References heading | DEFINED | PENDING_EXECUTION |
| C-007 | references_source=inferred | standalone | golden | plain References + ≥3 of next 10 entry-start lines | DEFINED | PENDING_EXECUTION |
| C-008 | inferred threshold does not overtrigger | standalone | golden | only 2 entry-start lines; prose mention “references” | DEFINED | PENDING_EXECUTION |
| C-009 | references_source=not_available is supported | standalone | golden | no recoverable bibliography → extraction continues, one bibliography_absent | DEFINED | PENDING_EXECUTION |
| C-010 | valid Section Map supplies structure | pipeline | integration golden | map hash/manuscript hash align; map fields used | DEFINED | BLOCKED_DEPENDENCY |
| C-011 | invalid supplied map never falls back | both with map | failure golden | hash mismatch/invariant violation → exit3 | DEFINED | BLOCKED_DEPENDENCY |
| C-012 | orchestrated mode requires map + passed review state | pipeline | integration | no map/open map cannot run citation stage | DEFINED | BLOCKED_DEPENDENCY |
| C-013 | candidate envelope never silently drops in-envelope input | both | golden set | every C1/C2 candidate parses or unresolved_citation | DEFINED | PENDING_EXECUTION |
| C-014 | six-token cap removed | both | golden | legitimate long multi-token narrative author survives | DEFINED | PENDING_EXECUTION |
| C-015 | arbitrary longest-suffix parsing forbidden | both | golden | World Bank (2024) never becomes bank identity | DEFINED | PENDING_EXECUTION |
| C-016 | all-caps rejection | both | golden | OECD (2024) / (OECD, 2024) → all_caps_surname | DEFINED | PENDING_EXECUTION |
| C-017 | unsupported prefix remains no_grammar_match with complete span | both | golden | unsupported lead-in candidate preserves text/start/end | DEFINED | PENDING_EXECUTION |
| C-018 | every closed PREFIX parses | both | synthetic set | one vector per 11 prefix forms | DEFINED | PENDING_EXECUTION |
| C-019 | PREFIX longest-match precedence | both | golden | `see also` and each multiword `…, see` form cannot decompose to `see` | DEFINED | PENDING_EXECUTION |
| C-020 | PREFIX attestation corpus form | both | regression golden | `for a similar approach, see ...` parses full group | DEFINED | PENDING_EXECUTION |
| C-021 | every STOP token has deterministic reduction behavior | both | generated synthetic suite | each closed STOP token before `Smith (2020)` | DEFINED | PENDING_EXECUTION |
| C-022 | structural STOP additions work | both | golden | Panel/Column/Row/Appendix/Exhibit Smith → person candidate after bibliography resolution | DEFINED | PENDING_EXECUTION |
| C-023 | STOP reduction is additive | both | golden | Panel Smith with both full and reduced reference identities retains both candidates | DEFINED | PENDING_EXECUTION |
| C-024 | author_phrase remains complete source phrase | both | golden | reduction never rewrites author_phrase | DEFINED | PENDING_EXECUTION |
| C-025 | possessive person identity stripping | both | golden | Fine's (1998) resolves to person|fine|1998 when bibliography supports | DEFINED | PENDING_EXECUTION |
| C-026 | surface key is extraction-only | both | golden + instrumentation assertion | surface key emitted but resolver never receives it as identity key | DEFINED | PENDING_EXECUTION |
| C-027 | surface key normalization | both | golden | whitespace/lower normalization; punctuation otherwise preserved | DEFINED | PENDING_EXECUTION |
| C-028 | surface key type is JSON array | both | byte golden | `["smith",2020]`, not quoted JSON text | DEFINED | PENDING_EXECUTION |
| C-029 | unresolved extraction surface key null | both | golden | no_grammar_match record includes null key | DEFINED | PENDING_EXECUTION |
| C-030 | sentence_index continuous | both | golden | continuous across section/heading boundary | DEFINED | PENDING_EXECUTION |
| C-031 | previous_sentence_end | both | golden | null first sentence; exact previous content_end otherwise | DEFINED | PENDING_EXECUTION |
| C-032 | standalone positional flag | both | golden | citation-only sentence true; preceding word false | DEFINED | PENDING_EXECUTION |
| C-033 | reference person-list parsing | both | golden | Smith, J., & Jones, K. -> ordered authors, person key | DEFINED | PENDING_EXECUTION |
| C-034 | non-person reference identity | both | golden | World Bank. (2024). -> non_person|world bank|2024 | DEFINED | PENDING_EXECUTION |
| C-035 | full-forename ref preserves person identity without inventing complete author structure | both | golden | Smith, John. (2020). -> person|smith|2020, authors=null, no author-structure mismatch | DEFINED | PENDING_EXECUTION |
| C-036 | no-year bibliography entry remains visible without identity laundering | both | golden | emits unresolved_reference reason=no_year; no reference record/key | DEFINED | PENDING_EXECUTION |
| C-037 | unresolved_reference reason enum closed | both | schema rejection | any reason outside entry_start_grammar/orphan_line/no_year rejected | DEFINED | PENDING_EXECUTION |
| C-038 | reference suspect reason ordering | both | golden | multi-reason record follows fixed order | DEFINED | PENDING_EXECUTION |
| C-039 | 3×3 F/S table: no/no | both | golden or injection | unresolved identity | DEFINED | PENDING_EXECUTION |
| C-040 | 3×3: unique/no | both | golden/injection | full_phrase chosen | DEFINED | PENDING_EXECUTION |
| C-041 | 3×3: nonunique/no | both | golden/injection | full_phrase + ambiguous_citation | DEFINED | PENDING_EXECUTION |
| C-042 | 3×3: no/unique | both | golden/injection | stop_reduced chosen | DEFINED | PENDING_EXECUTION |
| C-043 | 3×3: no/nonunique | both | golden/injection | stop_reduced + ambiguous_citation | DEFINED | PENDING_EXECUTION |
| C-044 | 3×3: unique/unique different keys | both | golden/injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION |
| C-045 | 3×3: unique/nonunique different keys | both | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION |
| C-046 | 3×3: nonunique/unique different keys | both | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION |
| C-047 | 3×3: nonunique/nonunique different keys | both | injection | ambiguous_author_resolution | DEFINED | PENDING_EXECUTION |
| C-048 | same candidate key in both nonempty candidates is invariant failure | both | invariant injection | exit6 meta+error only | DEFINED | PENDING_EXECUTION |
| C-049 | shared reference index across different candidate keys is permitted | both | injection | ambiguity, not exit6 | DEFINED | PENDING_EXECUTION |
| C-050 | ambiguous_author_resolution output schema | both | byte golden | both candidate states/keys/index arrays, arrays ascending | DEFINED | PENDING_EXECUTION |
| C-051 | ambiguous author refs are reserved | both | golden | Panel Smith dual identities → neither ref uncited nor mismatch-paired | DEFINED | PENDING_EXECUTION |
| C-052 | duplicate-key ambiguity reserves all duplicate refs | both | golden | Smith key with two refs → duplicate + ambiguous, no uncited/mismatch | DEFINED | PENDING_EXECUTION |
| C-053 | ambiguity reserved != uniquely matched | both | summary assertion | unique-match counts +0 absent independent match | DEFINED | PENDING_EXECUTION |
| C-054 | mismatch pairing same author kind | both | golden | cross-kind candidates never pair | DEFINED | PENDING_EXECUTION |
| C-055 | surname_edit_distance_1 | both | golden | Barko/Bartko same year, min CORE bound | DEFINED | PENDING_EXECUTION |
| C-056 | year_adjacent | both | golden | 2020↔2021 pair | DEFINED | PENDING_EXECUTION |
| C-057 | year_transposition | both | golden | 2012↔2021 and 1859↔1895 pair; nonpairs excluded | DEFINED | PENDING_EXECUTION |
| C-058 | mismatch pairing consumes each side once | both | golden | deterministic first-rule/first-reference pairing | DEFINED | PENDING_EXECUTION |
| C-059 | merge_suspected requires same phrase + year | both | golden | surname-only or year-only does not qualify; both does | DEFINED | PENDING_EXECUTION |
| C-060 | merge_suspected doesn't suppress missing | both | golden | record remains, exit1 | DEFINED | PENDING_EXECUTION |
| C-061 | exact author structure order mismatch | both | golden | Smith & Jones vs Smith+Brown -> failed=order + exit1 | DEFINED | PENDING_EXECUTION |
| C-062 | exact author structure count mismatch | both | golden | two visible vs three reference authors -> failed=count + exit1 | DEFINED | PENDING_EXECUTION |
| C-063 | et_al valid minimum | both | golden | Smith et al. vs 3 authors -> no mismatch | DEFINED | PENDING_EXECUTION |
| C-064 | et_al mismatch reports without alone forcing exit1 | both | golden | Smith et al. vs 1/2 authors | DEFINED | PENDING_EXECUTION |
| C-065 | null reference author list skips structure check | both | golden | unsupported person-list author structure -> no false mismatch | DEFINED | PENDING_EXECUTION |
| C-066 | multi-year total order | both | byte golden | Smith et al. (2020,2021) stable citation order/index | DEFINED | PENDING_EXECUTION |
| C-067 | every block ordering total | both | property test | no distinct records tie on all declared keys | DEFINED | PENDING_EXECUTION |
| C-068 | bibliography absence surface grouping | standalone | byte golden | Smith×2 + Jones×1 -> 3 extracted, 2 groups, no identities | DEFINED | PENDING_EXECUTION |
| C-069 | bibliography absence null semantics | standalone | summary golden | resolved=0, works=null, all reconciliation counts=null | DEFINED | PENDING_EXECUTION |
| C-070 | extraction invariant | both | property test | total = extracted + unresolved extraction | DEFINED | PENDING_EXECUTION |
| C-071 | conditional reconciliation invariant | both | property test | six outcome counts sum to total iff reconciliation performed | DEFINED | PENDING_EXECUTION |
| C-072 | counts are per occurrence, not diagnostic | both | golden | one missing key cited 7 times contributes 7 to outcome count | DEFINED | PENDING_EXECUTION |
| C-073 | distinct_surface_groups always computed | both | summary golden | same meaning with/without bibliography | DEFINED | PENDING_EXECUTION |
| C-074 | distinct_works_cited depends on identity | both | summary golden | null no-bib; distinct non-null citation keys with bib | DEFINED | PENDING_EXECUTION |
| C-075 | stdout canonical JSONL | both | byte golden | key order, escapes, non-ASCII raw, final LF, empty blocks | DEFINED | PENDING_EXECUTION |
| C-076 | file bytes == stdout bytes | standalone | byte compare | `--out` exact stream equality | DEFINED | PENDING_EXECUTION |
| C-077 | deterministic default filename | standalone | filesystem test | canonical_sha256 filename | DEFINED | PENDING_EXECUTION |
| C-078 | atomic normal publication | standalone | fault injection | crash before rename leaves no partial authoritative file | DEFINED | PENDING_EXECUTION |
| C-079 | abort file is two-line error artifact | standalone | golden | exits2–6 file ends error | DEFINED | PENDING_EXECUTION |
| C-080 | no normal output before exit6 assessment | both | invariant injection | same-key double resolution emits no partial normal stream | DEFINED | PENDING_EXECUTION |
| C-081 | exit2 ratio boundary | both | golden | N=40,P=1 abort; N=3,P=60 does not | DEFINED | PENDING_EXECUTION |
| C-082 | numeric author-year form stays out of identity envelope | both | golden | `[Smith, 2020]` no citation record | DEFINED | PENDING_EXECUTION |
| C-083 | numeric/superscript dominance detector only | both | golden | numeric markers can trigger exit2 but never become citation identities | DEFINED | PENDING_EXECUTION |
| C-084 | deterministic termination | both | bounded test | all synthetic/corpus inputs terminate within harness bound | DEFINED | PENDING_EXECUTION |
| C-085 | 11-paper regression corpus | both as applicable | corpus run | every unexpected finding classified under blocker taxonomy | DEFINED | PENDING_EXECUTION |
| C-086 | corpus non-blocker requires rule citation | both | review audit | every waiver points to exact envelope/limitation/deferral rule | DEFINED | PENDING_EXECUTION |
| C-087 | no accuracy claim from 11 papers | governance | artifact review | corpus report labels itself regression/conformance only | DEFINED | PENDING_EXECUTION |

## 3. Prefix attestation coverage

| Prefix | Introduction basis | Required evidence before freeze |
|---|---|---|
| `for a similar approach, see` | corpus-observed form | retain corpus example + golden |
| `for example, see` | attested standard scholarly formula; moderate-confidence design judgment | synthetic golden + attestation record |
| `for instance, see` | attested standard scholarly formula; moderate-confidence design judgment | synthetic golden + attestation record |
| `for discussion, see` | attested standard scholarly formula; moderate-confidence design judgment | synthetic golden + attestation record |
| `for a review, see` | attested standard scholarly formula; moderate-confidence design judgment | synthetic golden + attestation record |

The original six prefix forms remain inherited from v3.3 and still require regression goldens.

## 4. Corpus finding classification

A corpus finding is **blocking** if it meets any category B1–B10:

| Code | Blocking category |
|---|---|
| B1 | output contradicts normative rule |
| B2 | in-envelope candidate silently dropped |
| B3 | false extracted citation/reference content, identity, or reconciliation diagnostic caused by spec or implementation defect |
| B4 | invariant/partition/cardinality/closed-enum violation |
| B5 | deterministic ordering/canonical-byte failure |
| B6 | exit/abort/atomic-publication failure |
| B7 | bounded-termination failure or hang |
| B8 | standalone/orchestrated scope behavior violation |
| B9 | supported input has undefined behavior |
| B10 | pinned dependency contract incompatible |

A non-blocking classification MUST cite an exact governing rule establishing out-of-envelope status, expected ambiguity/unresolved behavior, accepted limitation, unsupported status, or explicit deferral. An undocumented expectation is not a waiver.

## 5. Freeze checklist

### 5.1 Candidate identity

- [x] Architecture `spec_id = citation_architecture`.
- [x] Architecture `spec_version = 3.4`.
- [x] Architecture `candidate_revision = 1`.
- [x] Architecture SHA-256 bound in this file: `6a615c8136543ef492598196a918b2c1e4b62bb54fdbcca4bd12af28bac66cb0`.
- [x] Execution `spec_id = citation_execution_conformance`.
- [x] Execution `spec_version = 3.4`.
- [x] Execution `candidate_revision = 1`.
- [x] Execution SHA-256 bound in this file: `11edbf8918224c0ee1ac85423db1f676fe49ca1feceecf1575c4a1daa2976695`.
- [x] Level 3 / Level 5 authority split explicit.

### 5.2 Static specification completeness

- [x] Three-layer architecture closed.
- [x] Candidate envelope closed.
- [x] Byte coordinate system closed.
- [x] Canonicalization closed.
- [x] Prefix set + longest-match rule closed.
- [x] STOP vocabulary and additive reduction closed.
- [x] Surface grouping defined and prohibited from identity authority.
- [x] Bibliography-grounded author kind defined.
- [x] 3×3 identity table closed.
- [x] Ambiguity reservation closed.
- [x] Reconciliation outcome partition closed and conditional.
- [x] Bibliography-absent behavior closed.
- [x] Author-structure behavior closed.
- [x] JSONL serialization and total order closed.
- [x] File atomicity and exit6 publication behavior closed.
- [x] No unresolved behavioral choice is intentionally left to implementation.

### 5.3 External dependency gates

- [ ] **Section Map v1.1 exact artifact is frozen/current, with version + SHA-256 + freeze/disposition evidence.** `BLOCKED_DEPENDENCY` until populated.
- [ ] Orchestrator v2.3 or its current superseding contract is verified, hashed and compatible for the pipeline scope.
- [ ] Unicode 15.0.0 runtime/library conformance is demonstrated in the execution environment.

### 5.4 Executable conformance

- [ ] C-001 through C-087 have executed evidence attached.
- [ ] Every closed STOP token is covered synthetically.
- [ ] Every prefix is covered.
- [ ] All nine 3×3 cells are covered.
- [ ] Invariant-injection exit6 case passes.
- [ ] Focused HIGH-rung deterministic-kernel prototype/reference implementation evidence is accepted.
- [ ] 11-paper corpus run completes with every unexpected finding dispositioned.
- [ ] No blocking corpus finding remains.

### 5.5 Independent review / authority

- [ ] Independent reviewer received sealed candidate bytes and evidence without shared generation context.
- [ ] Reviewer model/provider identity and version are logged where applicable.
- [ ] Raw findings are durably retained.
- [ ] Review binds exact `spec_id`, `spec_version`, `candidate_revision`, and SHA-256.
- [ ] No normative post-review change remains unevaluated.
- [ ] Reviewer disagreement is resolved or adjudicated by the accountable human owner using the predeclared taxonomy, with rationale recorded.
- [ ] Final freeze/disposition record exists.
- [ ] `content_state` changed to `frozen` only after all applicable gates pass.
- [ ] approved Level-5 conformance scopes changed to `authority_state=current` only after freeze.

## 6. Current verdict

```text
STATIC CONTENT READINESS: PASS
ACTUAL FREEZE AUTHORITY:  NOT YET ESTABLISHED
PRIMARY EXTERNAL BLOCKER: Section Map v1.1 frozen/current artifact binding
OTHER REQUIRED EVIDENCE: executable suite + HIGH-rung kernel evidence + 11-paper corpus + independent review
```

The package is therefore **ready to enter the freeze process** but is not self-certified as frozen.
