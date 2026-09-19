---
document_id: citation_v3_4_dependency_deferred_work_register
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
status: current_candidate_register
---

# Citation v3.4 — Dependency + Deferred-Work Register

This register is the explicit scope boundary for the Citation v3.4 candidate package. Items listed as deferred are **not hidden missing requirements** for v3.4. Items listed as hard dependencies remain freeze gates and cannot be silently substituted.

## 1. Dependency classes

```text
HARD_FREEZE_DEPENDENCY
    must be verified before Citation v3.4 can be frozen/current for the affected scope

RUNTIME_EXTERNAL_AUTHORITY
    external deterministic authority pinned by version and tested for conformance

INTERNAL_RULE
    defined inside the Level-5 Citation contract; no separate mutable authority

NON_AUTHORITATIVE_CONTEXT
    useful provenance/context; cannot change a conformance outcome
```

## 2. Active dependencies

| ID | Dependency | Class | Required contract | Scope affected | Candidate status | Freeze action |
|---|---|---|---|---|---|---|
| D-01 | Section Map | HARD_FREEZE_DEPENDENCY | exact v1.1 artifact; frozen/current; exact SHA-256; freeze/disposition record | whole Citation v3.4 package by operator decision G3; runtime-required specifically for pipeline | **not yet bound** | obtain exact artifact identity; verify version/hash/freeze record; record in both candidate metadata before actual freeze |
| D-02 | Orchestrator | HARD_FREEZE_DEPENDENCY for pipeline | v2.3 or formally superseding current contract; citation eligibility includes segmentation complete + required reviewed map state; citation execution input fingerprint includes canonical manuscript + section map + citation rule version | EpistemicOS pipeline | version known; exact freeze/current hash still to be attached | verify current/supersession state and exact artifact SHA before pipeline authority |
| D-03 | Unicode | RUNTIME_EXTERNAL_AUTHORITY | Unicode 15.0.0 NFC, simple lowercase, Unicode properties | both | version pinned in Level5 | demonstrate runtime/library behavior in conformance evidence |
| D-04 | Canonical citation text transform | INTERNAL_RULE | invalid UTF-8 reject → CRLF/lone CR to LF → NFC; folded into citation_rule_version | both | closed in Level5 | conformance C-001/C-002; pipeline upstream bytes must be compatible/idempotent |
| D-05 | Citation profile | INTERNAL_RULE | `apa7_like_v1`; `ET_AL_MIN_AUTHORS=3`; folded into citation_rule_version | both | closed | profile change requires versioned spec change |
| D-06 | Citation Architecture v3.4 rc1 | NON_AUTHORITATIVE_CONTEXT | Level-3 architecture baseline; SHA `6a615c8136543ef492598196a918b2c1e4b62bb54fdbcca4bd12af28bac66cb0` | both | generated | Level5 is self-contained; architecture cannot change execution conformance by itself |
| D-07 | Authoritative Technical Specification Standard rc3 | NON_AUTHORITATIVE governance context | candidate-revision, scope-authority, review/freeze process | governance only | current project governance basis, itself a review candidate | do not treat it as product behavioral input; apply project governance procedure |

## 3. Dependency rule for Section Map

Filename presence is insufficient.

Before Citation v3.4 actual freeze, D-01 MUST contain all of:

```text
spec/artifact id
version = 1.1
exact content SHA-256
content_state = frozen (or project-equivalent immutable freeze state)
authority_state = current for the required structural scope
freeze/disposition evidence identifier
superseded_by = null or equivalent current-source proof
verification date
```

If any field cannot be established, Citation v3.4 remains `not_yet_authoritative`. The generator/reviewer MUST NOT infer authority from recency, filename, or prose such as “final”.

## 4. Normalization authority disposition

Citation v3.4 does **not** depend on a mutable GSD implementation plan to define canonical bytes.

The normative canonicalization algorithm is closed directly inside the Level-5 specification and folded into `citation_rule_version`:

```text
validate UTF-8
CRLF → LF
lone CR → LF
NFC under Unicode 15.0.0
```

The pipeline may canonicalize earlier, but that earlier transform must be observationally identical/idempotent under conformance. A GSD may describe how to implement this rule; it does not own the rule.

## 5. L–T backlog disposition

| Legacy item | Final disposition in v3.4 | Governing location |
|---|---|---|
| L — two-author narrative mis-key | closed as already fixed by v3.3 grammar; obsolete exposure figure must not be reused | Level5 person grammar regression cases |
| M — code-point offsets | incorporated | Architecture §3; Level5 §1.3; C-003/C-004 |
| N — bibliography may not be heading | absorbed into references fallback / `references_source` model | Level5 §4.3 |
| O — merged entry creates false certainty | incorporated as targeted `merge_suspected` qualification; record retained | Level5 §9.5; C-059/C-060 |
| P — partial references need review | not a Citation CLI/execution-spec requirement; underlying human-review capability retained as deferred X below | Deferred X-01 |
| Q — record ordering collision | incorporated as universal total-order invariant and multi-year golden | Level5 §12.4; C-066/C-067 |
| R — determinism/review contradiction | superseded by explicit standalone/map determinism tuples | Level5 §2.3 |
| S — numeric range orphan spray | impossible by construction because numeric citations are not identity records | Level5 §16; C-082/C-083 |
| T — enumerations not closed | incorporated; unresolved-reference enum closed; later non-null reference-key decision adds the mechanically required `no_year` unresolved state | Level5 §7.1–§7.4; C-036/C-037 |

No L–T item remains an untracked implementation choice.

## 6. New v3.4 decision dispositions

| Decision | Disposition |
|---|---|
| three-layer extraction → identity → reconciliation | incorporated |
| syntax does not confer author_kind | incorporated |
| `citation_surface_group_key` | incorporated as non-authoritative extraction key |
| bibliography absence uses null reconciliation counts | incorporated |
| distinct surface groups != distinct works | incorporated |
| author-resolution 3×3 table | incorporated |
| ambiguity reservation before repair/unmatched | incorporated |
| exit6 invariant failure | incorporated |
| test-only resolver seam | incorporated |
| possessive person surname stripping | incorporated |
| PREFIX expansion | incorporated as closed list + longest-match rule |
| unsupported prefix failure class | remains existing `no_grammar_match`; candidate span preserved |
| current 11-paper corpus | regression/conformance discovery only; not validation sample |
| independent review | provider/model provenance + sealed context + human taxonomy adjudication required |

## 7. Prefix attestation register

| Prefix introduced in v3.4 | Basis | Status |
|---|---|---|
| `for a similar approach, see` | observed in current manuscript corpus | accepted into closed v3.4 profile |
| `for example, see` | standard scholarly formula attestation; design judgment, moderate confidence | accepted into closed v3.4 profile; golden required |
| `for instance, see` | standard scholarly formula attestation; design judgment, moderate confidence | accepted into closed v3.4 profile; golden required |
| `for discussion, see` | standard scholarly formula attestation; design judgment, moderate confidence | accepted into closed v3.4 profile; golden required |
| `for a review, see` | standard scholarly formula attestation; design judgment, moderate confidence | accepted into closed v3.4 profile; golden required |

Future prefix additions require a version change and an attestation record based on corpus evidence or an approved citation-style authority. Runtime discovery is forbidden.

## 8. Explicit deferred work

### X-01 — Citation → human review integration

**Status:** deferred, outside v3.4 execution authority.

Future scope:

- transform citation `suspect`, unresolved-reference, bibliography-absence and related findings into reviewable tasks on the shared review surface;
- define task identity, review contracts, carry/re-review behavior and orchestration;
- preserve deterministic citation output as the source diagnostic rather than embedding human workflow in the parser.

**Trigger:** shared review surface supports citation-scoped task contracts and a separate reviewed specification is commissioned.

### X-02 — Additional citation profiles / selectable style configuration

**Status:** deferred.

v3.4 supports only `apa7_like_v1`. Future selectable profiles require:

- `citation_profile_id` as a pinned runtime input;
- profile-specific thresholds/rules;
- fingerprint inclusion;
- profile-specific conformance suites;
- versioned authority and provenance.

### X-03 — Numeric citation identity extraction

**Status:** deferred/out of envelope.

Includes `[1]`, `[1–4]`, numeric ranges and reference-number reconciliation. The current numeric recognizer is only an unsupported-style dominance detector.

### X-04 — Square-bracket author–year forms

**Status:** deferred/out of envelope.

Example: `[Smith, 2020]`.

### X-05 — Parenthesis-free author–year citation forms

**Status:** deferred/out of envelope.

Example: `as Smith 2020 argued`.

### X-06 — Footnote/superscript citation extraction

**Status:** deferred/out of envelope except for current unsupported-style detection.

### X-07 — Broader bibliography author grammars

**Status:** deferred.

Includes:

- complete ordered author-structure extraction for full-forename person references;
- non-person author names containing commas;
- other author-list conventions outside `apa7_like_v1`.

Current behavior is explicitly unresolved/reference-limited rather than guessed.

### X-08 — ConversionArtifactAnnotations / conversion repair

**Status:** deferred to LDVI/lifecycle architecture; not a citation stage and not part of immutable source conversion.

Citation v3.4 consumes canonical text actually present. Recovery of malformed footnotes, columns or conversion omissions is upstream scope.

### X-09 — Claim ↔ citation linking

**Status:** deferred/outside capability.

Sentence-relative `standalone` is positional metadata only and MUST NOT be promoted into attachment semantics without a separate claim-linking specification.

### X-10 — Citation validity / evidential support / source credibility

**Status:** deferred/outside structural coherence.

Citation v3.4 establishes structural identity/coherence only.

### X-11 — Population-level validation study

**Status:** deferred but required before generalized accuracy claims.

Required future study:

- powered or otherwise defensibly sampled manuscript corpus;
- predeclared error taxonomy;
- extraction/identity/reconciliation metrics separated by layer;
- stratification by citation/reference form where relevant;
- human adjudication protocol;
- no reuse of the 11-paper regression corpus as if it were population validation.

**Trigger:** before external accuracy claims or before a product decision that requires validated error rates.

### X-12 — Prefix vocabulary expansion

**Status:** deferred unless new evidence appears.

Any new formula requires a versioned change, attestation basis, longest-match interaction audit and goldens.

### X-13 — Fuzzy citation/work identity

**Status:** deferred.

v3.4 allows deterministic `possible_mismatch` diagnostics but does not let fuzzy similarity acquire authoritative identity. Future fuzzy identity would require a separate authority model and validation.

### X-14 — Upstream column-interleaving / malformed PDF repair

**Status:** deferred upstream.

`embedded_entry_pattern` remains a tripwire. Citation does not reconstruct missing/merged layout.

## 9. Known limitations permitted at freeze

The following are permitted because their behavior and scope are explicit rather than unresolved:

| Limitation | Governing disposition |
|---|---|
| standalone no-bibliography has no authoritative work identity | intentional authority trade-off; Level5 §10 |
| all-caps citation author cores unresolved | Level5 §6.2/§6.3 |
| full-forename references retain first-surname person identity but do not expose a complete ordered author list for structure checking | Level5 §7.4, deferred X-07 |
| organization author heads with commas unsupported | Level5 §7.4, deferred X-07 |
| sentence splitter is closed-guard approximation | Level5 §16.2 |
| conversion corruption not repaired | Level5 §16.2, deferred X-08/X-14 |
| et_al mismatch does not alone force exit1 | profile-dependent diagnostic policy, Level5 §9.3 |
| numeric/footnote/superscript citation identities unsupported | Level5 §16.1, deferred X-03/X-06 |

A limitation not listed here or in the Level-5 specification cannot be invented after a corpus failure merely to reclassify a blocker.

## 10. Freeze-time register updates required

Before actual freeze, update this register with:

1. D-01 exact Section Map v1.1 identity, SHA-256, authority state and freeze/disposition evidence;
2. D-02 exact current Orchestrator identity/SHA and supersession check;
3. Unicode runtime conformance evidence identifier;
4. exact conformance-suite evidence artifact(s);
5. 11-paper corpus report identifier and all finding dispositions;
6. focused HIGH-rung deterministic-kernel evidence artifact;
7. independent review artifact, reviewer/model provenance, exact candidate hashes;
8. human adjudication records for any disagreements;
9. final freeze/disposition record.

Any normative change to either bound candidate before freeze increments that candidate's `candidate_revision`, changes its SHA-256, and requires this register and the matrix to be rebound.

## 11. Current register verdict

```text
DEFERRED-WORK BOUNDARY: CLOSED
HIDDEN CITATION V3.4 WORK: NONE IDENTIFIED
HARD DEPENDENCY STILL UNBOUND: Section Map v1.1 frozen/current exact artifact
PIPELINE DEPENDENCY TO VERIFY: Orchestrator v2.3 current exact artifact
PROCESS EVIDENCE STILL REQUIRED: conformance execution + HIGH-rung kernel evidence + corpus + independent review
```
