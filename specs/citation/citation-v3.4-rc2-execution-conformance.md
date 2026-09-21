---
spec_id: citation_execution_conformance
spec_version: "3.4"
candidate_revision: 2
quality_level: 5
content_state: review_candidate
frozen_at: null
supersedes: null
superseded_by: null
authoritative_source: docs/specs/citation_execution_conformance_v3.4_rc2.md
validation_risk: high
selected_validation_rung: high
validation_rationale: >-
  Citation extraction, identity resolution and reconciliation are deterministic,
  persistent and user-visible. False extraction, false identity, or false coherence
  diagnostics can contaminate downstream manuscript analysis. Baseline exact
  conformance, invariant injection, a focused deterministic-kernel implementation
  and the current regression corpus are proportionate before freeze.
conformance_scopes:
  - scope: citation_v3_4_standalone_cli_nomap_apa7_like_v1
    authority_state: not_yet_authoritative
    authority_reason: pending independent review, executable conformance evidence and freeze
  - scope: citation_v3_4_standalone_cli_with_map_apa7_like_v1
    authority_state: not_yet_authoritative
    authority_reason: pending frozen/current Section Map v1.1 binding plus review/evidence/freeze
  - scope: citation_v3_4_epistemicos_pipeline_apa7_like_v1
    authority_state: not_yet_authoritative
    authority_reason: pending Section Map and Orchestrator binding plus review/evidence/freeze
dependencies:
  - dependency_id: section_map
    required_version: "1.1"
    required_state: frozen_current_for_map_consuming_scopes
    scopes:
      - citation_v3_4_standalone_cli_with_map_apa7_like_v1
      - citation_v3_4_epistemicos_pipeline_apa7_like_v1
    required_sha256: null
    verified_at: null
  - dependency_id: orchestrator_build_spec
    required_version: "2.3"
    required_state: current_for_pipeline_scope
    scopes:
      - citation_v3_4_epistemicos_pipeline_apa7_like_v1
    required_sha256: null
    verified_at: null
external_authorities:
  - authority_id: unicode
    required_version: "15.0.0"
    verified_at: null
review_evidence: []
governance_basis:
  artifact: authoritative_technical_spec_standard_v0.1_rc3
  sha256: e5185b132ac22e3c373fff6358538d11d21e33ce572e800190c6078bb0c2a63b
pilot_context:
  artifact: PILOT_RUNBOOK_6
  sha256: df0a587c3d9d3289e57ab48f7e28e89d7edf7d5f45dc888fb1f179374d861876
---

# Citation Execution + Conformance Specification v3.4

**Status:** Level-5 review candidate prepared for the GSD pilot freeze path. The pilot target is the standalone/no-map conformance scope. This document is **not frozen** and has no current authority until independent review, pilot-scope conformance evidence and final freeze disposition pass.

## 0. Capability and scope

This specification defines the observable deterministic contract for:

1. supported author–year citation extraction;
2. bibliography-entry extraction;
3. citation identity resolution;
4. citation ↔ bibliography structural reconciliation;
5. canonical JSONL output on stdout and optional file output.

It declares three conformance scopes:

```text
citation_v3_4_standalone_cli_nomap_apa7_like_v1       # GSD pilot target
citation_v3_4_standalone_cli_with_map_apa7_like_v1
citation_v3_4_epistemicos_pipeline_apa7_like_v1
```

Only the first scope is the GSD pilot implementation target. Section Map and Orchestrator dependencies therefore do not block freeze/current authority for the no-map pilot scope.

It does not assess citation validity, claim support, source quality, source credibility, plagiarism, or claim ↔ citation attachment.

## 1. Pinned constants and canonical text

### 1.1 Rule identity

```text
spec_version          = "3.4"
citation_profile      = "apa7_like_v1"
citation_rule_version = "citation_v3.4_apa7_like_v1"
ET_AL_MIN_AUTHORS     = 3
Unicode               = 15.0.0
```

`citation_profile` and `ET_AL_MIN_AUTHORS` are properties of `citation_rule_version`; they are not independently selectable runtime inputs.

### 1.2 Canonical manuscript transform

Given source bytes:

1. validate UTF-8; invalid input → exit 5 before any other processing;
2. replace CRLF with LF;
3. replace any remaining lone CR with LF;
4. normalize Unicode to NFC using Unicode 15.0.0.

The resulting UTF-8 byte sequence is `canonical_manuscript_bytes`.

`canonical_sha256` is lowercase hexadecimal SHA-256 over exactly `canonical_manuscript_bytes`.

A pipeline may supply bytes already canonicalized upstream. This specification still defines the transform; reapplying it to conformant canonical input MUST be an identity transform.

### 1.3 Coordinates

Every manuscript coordinate is a half-open, zero-based UTF-8 byte offset into `canonical_manuscript_bytes`:

```text
[start, end)
```

All coordinate values MUST fall on UTF-8 code-point boundaries.

Code points are used only for these non-coordinate counts:

```text
OSA edit distance unit                 code point after NFC
CORE minimum length                    >= 2 code points
reference overlong threshold           > 1500 code points
```

### 1.4 Lowercase and edit distance

`lower(x)` = Unicode simple lowercase, one-to-one where defined; unmapped code points pass through.

`osa(a,b)` = optimal-string-alignment Damerau–Levenshtein distance over NFC code points.

## 2. Execution modes and material inputs

### 2.1 Standalone no-map mode — GSD pilot target

Required input:

```text
source_bytes : byte string
```

Forbidden material input for this scope:

```text
section_map_bytes
```

The implementation MUST execute the deterministic standalone structure fallback in §4.

This scope is:

```text
citation_v3_4_standalone_cli_nomap_apa7_like_v1
```

It has no Section Map or Orchestrator runtime dependency.

### 2.2 Standalone with supplied map

Required inputs:

```text
source_bytes      : byte string
section_map_bytes : exact Section Map v1.1 JSONL bytes
```

The supplied map MUST satisfy §4.1. This scope is separate from the pilot target.

### 2.3 EpistemicOS orchestrated mode

Required inputs:

```text
source_bytes      : byte string
section_map_bytes : exact Section Map v1.1 JSONL bytes
```

The Section Map MUST:

- have `map_version = "1.1"`;
- describe the same `canonical_sha256`;
- satisfy its own validity invariants;
- have the review state required by the current Orchestrator contract;
- be the structural source of truth for section/bibliography boundaries and metadata.

The no-map fallback in §4 is forbidden in orchestrated mode.

`section_map_sha256` = lowercase SHA-256 over exact supplied Section Map bytes; it is `null` in the pilot target scope.

### 2.4 Determinism tuple

Pilot standalone/no-map scope:

```text
(canonical_manuscript_bytes, citation_rule_version)
```

Map-consuming scopes:

```text
(canonical_manuscript_bytes, exact section_map_bytes, citation_rule_version)
```

Identical tuple → byte-identical canonical JSONL output.

## 3. Closed lexical and grammar primitives

`WS = [ \t\n]+`.

```text
NAMECHAR      = [\p{L}\p{M}'’-]
CORE          = \p{Lu}NAMECHAR+                     # >= 2 code points
PARTICLE      = de|del|della|der|den|di|da|dos|du|la|le|van|von|ter|ten|zu|zur
SURNAME       = (?:PARTICLE WS)* CORE
YEAR_TOKEN    = (?:1[5-9]|20)\d{2}[a-z]? | n\.d\.
INITIALS      = \p{Lu}\.(?:[- ]?\p{Lu}\.)*
AUTHORS_PAREN = SURNAME WS et WS al\.
              | SURNAME(?:, WS? SURNAME)*(?:,? WS (?:&|and) WS SURNAME)?
AUTHORS_NARR  = SURNAME WS et WS al\.
              | SURNAME(?:, WS SURNAME)* ,? WS (?:&|and) WS SURNAME
              | SURNAME
LOCATOR       = , WS? (?:p\.|pp\.|para\.|chap\.) WS? [^();]+
ENTRY_START   = ^(?:PARTICLE[ ])* CORE , [ ] INITIALS
NUMCITE       = \[\d{1,3}(?:[ \t]*[,–—-][ \t]*\d{1,3})*\]
SUPCITE       = [\u00B9\u00B2\u00B3\u2070\u2074-\u2079]+
```

Supported numeric publication years are 1500–2099 inclusive. `n.d.` is supported. A suffixed year such as `2020a` is supported.

`normalized_year` is:

```text
plain numeric token  -> decimal string, e.g. "2020"
suffixed token       -> lowercase string, e.g. "2020a"
n.d.                  -> "nd"
```

### 3.1 Closed parenthetical PREFIX set

A parenthetical segment MAY begin with exactly one prefix from this closed set:

```text
e.g.
i.e.
cf.
see also
see
but see
for example, see
for instance, see
for a similar approach, see
for discussion, see
for a review, see
```

Matching is case-insensitive through `lower()` and anchored at the beginning of the segment after optional `WS`.

The matcher MUST choose the **longest matching member** before considering a shorter member. Therefore `see also` cannot decompose to `see`, and a multiword form ending in `see` cannot decompose to the standalone `see` prefix.

For `e.g.`, `i.e.`, `cf.`, `see`, `see also`, and `but see`, one comma immediately after the listed phrase is permitted. The five newly added multiword forms contain their internal comma exactly as listed and do not require an additional comma after `see`.

After the prefix, at least one grammar whitespace character MUST separate the prefix from `AUTHORS_PAREN` unless the accepted trailing comma itself is followed immediately by whitespace.

Adding a prefix is a versioned rule change and requires a recorded attestation basis.

### 3.2 Closed STOP set

STOP is compared by `lower()` after removal of at most one trailing `,`, `;`, or `:`:

```text
january february march april may june july august september october november december
jan. feb. mar. apr. jun. jul. aug. sep. sept. oct. nov. dec.
in the a an see since during early late as at on after before table figure section chapter equation
however moreover unlike although while whereas thus therefore furthermore additionally finally similarly likewise consequently meanwhile nevertheless nonetheless indeed overall importantly notably specifically together here there this these those using given despite beyond under over from with within without across toward towards per via following like first second third next then also yet still both when where because if unless until once
panel column row appendix exhibit
```

This list is closed and versioned. It is structural vocabulary only; runtime inference MUST NOT add tokens.

## 4. Document structure

### 4.1 Supplied Section Map

If a Section Map is supplied, the extractor MUST use it for:

- section boundaries;
- section names/levels/roles;
- bibliography presence/source;
- references-section ordinal and span.

It MUST NOT independently derive a conflicting bibliography boundary.

A supplied map is invalid for this execution if any of the following holds:

- malformed JSONL;
- unsupported map major/version other than 1.1;
- `canonical_sha256` mismatch;
- invalid Section Map invariant;
- record/count contradiction;
- impossible references invariant;
- required review state not satisfied in orchestrated mode.

Invalid supplied map → exit 3 with reason `invalid section map`; MUST NOT fall back.

### 4.2 Standalone heading fallback

When no map is supplied:

Markdown ATX heading:

```text
HEAD_MD = ^(#{1,6})[ \t]+(.*)$
```

Remove one trailing closing-hash match `(?:[ \t]+#+)?[ \t]*$` from group 2.

Whole-line HTML heading, case-insensitive:

```text
HEAD_HTML = ^[ \t]*<h([1-6])(?:[ \t][^>]*)?>(.*?)</h\1>[ \t]*$
```

Remove residual tags from inner text and collapse whitespace.

`clean(name)` removes leading numbering matching:

```text
^\d+(\.\d+)*[.)]?[ \t]+
```

Setext headings are not recognized.

If the apparent section structure uses at least two h1 headings and zero h2 headings, exit 4 `heading contract violated` rather than remapping.

### 4.3 Standalone bibliography detection

First, find the first h2–h4 heading whose `lower(clean(name))` is one of:

```text
references
bibliography
works cited
```

If found:

```text
references_source = detected
```

The section ends before the next heading of level <= the references heading, else EOF.

If not found, scan for a line whose entire trimmed lowercased content is one of the three names. It starts an inferred bibliography iff at least 3 of the following 10 non-blank trimmed lines satisfy the reference `ENTRY_START` guard.

If this fallback succeeds:

```text
references_source = inferred
```

The inferred section ends at the next h1–h6 heading, else EOF.

If both methods fail:

```text
references_source = not_available
```

This is a supported run state; it is not exit 3.

### 4.4 Section metadata in standalone mode

For body headings h2–h4, maintain a level/name stack. On heading level `L`, pop stack entries with level >= L, then push `(L, clean(name))`. h1/h5/h6 do not enter the stack.

Role keyword matching is word-boundary based over `lower(section_name)`:

```text
introduction       -> introduction
literature_review  -> literature | related work | background
methodology        -> method | methods | methodology
results            -> result | results | finding | findings
discussion         -> discussion
conclusion         -> conclusion | conclusions
```

`section_roles` contains all matched roles ordered by leftmost hit, ties by the table order above. Walking stack innermost → outermost, the first non-empty role set provides `section_roles` and `section_type`; none gives `[]` and `other`.

## 5. Sentence segmentation

Sentence processing is over body text only.

Hard boundaries:

- blank line;
- structural heading line in standalone mode;
- supplied Section Map heading boundary when a map is used.

Within a paragraph, `[.?!]` at byte position `t` terminates a sentence iff followed by:

```text
CLOSERS = [”"’')\]]*
```

and then either paragraph end or whitespace followed by `\p{Lu}`, unless the guard holds.

GUARD is closed:

```text
et al. e.g. i.e. cf. vs. Dr. Prof. Mr. Mrs. Ms. St. Jr. Sr. no. No. p. pp. Vol. vol. Eq. Fig. Figs. Tab. ca. ed. eds. approx. U.S. U.K.
```

A single initial `\p{Lu}.` is also guarded when preceded by paragraph start, whitespace, or one of `(` `[` `"` `“` `'` `‘`.

For each sentence:

```text
sentence_start = first non-whitespace byte after previous boundary
sentence_end   = one past final closer for terminated sentence,
                 else one past final non-whitespace byte
content_end    = byte offset of terminator for terminated sentence,
                 else sentence_end
sentence       = canonical bytes [sentence_start, sentence_end) decoded as UTF-8
sentence_index = 0-based ordinal among body sentences, continuous across sections
```

`previous_sentence_end` = previous sentence `content_end`, or `null` for the first body sentence.

## 6. Pass 1 — citation occurrence extraction

Pass 1 performs **no bibliography lookup**.

### 6.1 Candidate envelope

Scan body left to right.

**C1 parenthetical anchor:** every maximal `\([^()]*\)` span whose content contains at least one supported `YEAR_TOKEN`; nested parentheses contribute the innermost maximal spans only.

**C2 narrative run:** immediately before each C1 span, walk right-to-left over whitespace-separated tokens until the containing sentence boundary or until the next token is ineligible. There is **no token-count cap** in v3.4.

A C2 token is eligible, after retaining its original bytes and ignoring at most one trailing comma for eligibility, iff it:

- matches `\p{Lu}[\p{L}\p{M}'’.-]*`; or
- lowercases to one of `et`, `al.`, `and`, `&`; or
- is a declared `PARTICLE`.

Candidate span = collected run + C1 when the run is non-empty, otherwise C1.

Citation-like forms outside this envelope are invisible by declaration and are listed in §16.

### 6.2 Parenthetical parsing

A C1 span parses only if the entire parenthetical content is consumed as one or more semicolon-separated segments.

For each segment:

```text
SEG = optional PREFIX
      + AUTHORS_PAREN
      + comma
      + one or more YEAR_TOKEN values
      + optional LOCATOR
```

A supported PREFIX is syntactically separate from `author_phrase`.

If full consumption fails, emit one `unresolved_citation` for the C1 candidate with:

```text
reason = no_grammar_match
text/start/end = verbatim candidate span and byte coordinates
citation_surface_group_key = null
```

If the parsed first-author CORE is all-caps with at least 2 code points, emit `all_caps_surname` instead of a citation occurrence. All-caps rejection precedes stopword-surname rejection.

### 6.3 Narrative parsing and complete-phrase preservation

For narrative C2+C1 candidates, the complete collected C2 text is the `author_phrase` source candidate after trimming leading/trailing grammar whitespace and one trailing comma immediately before C1.

The implementation MUST NOT use arbitrary longest-valid-suffix parsing.

Pass 1 creates:

```text
full_phrase = author_phrase
```

If `full_phrase` fully satisfies `AUTHORS_NARR`, it is a syntactic person-form candidate.

If it does not, Pass 1 MAY create one `stop_reduced_phrase` by repeatedly removing leading C2 tokens only while each removed token is either:

- in the closed STOP set after the comparison normalization above; or
- ends in `,`, `;`, or `:` in the source token.

Reduction stops at the first non-removable leading token. A reduced phrase exists only if the remaining phrase fully matches `AUTHORS_NARR`.

Reduction is additive:

```text
author_phrase remains full_phrase
stop_reduced_phrase is separate
```

If neither the complete phrase nor an allowed reduced phrase can create an identity candidate, emit `unresolved_citation`, reason `no_grammar_match`, over the complete candidate span.

A parsed first CORE that is all-caps → `all_caps_surname`; a parsed first CORE whose lowercase value is STOP → `stopword_surname`.

### 6.4 Unresolved-citation reasons

Closed enum:

```text
no_grammar_match
stopword_surname
all_caps_surname
```

Unsupported prefatory prose inside the candidate envelope remains `no_grammar_match`; no separate `unsupported_prefix` reason exists in v3.4.

Every unresolved record preserves verbatim candidate text and byte offsets.

### 6.5 Extracted occurrence cardinality

One citation occurrence is emitted per parsed segment per normalized year.

Example:

```text
Smith et al. (2020, 2021)
→ 2 occurrences
```

### 6.6 Pass-1 author surface fields

For each extracted occurrence:

`author_phrase` = complete source author candidate, excluding a supported parenthetical PREFIX and excluding year/locator syntax; STOP reduction never rewrites it.

`normalized_author_phrase` = `lower()` after replacing each maximal run of citation grammar whitespace with one ASCII space and trimming leading/trailing whitespace. No punctuation, possessive, particle, or identity normalization is performed for this field.

`surface_year_component`:

```text
"2020"  -> JSON integer 2020
"2020a" -> JSON string "2020a"
"nd"    -> JSON string "nd"
```

`citation_surface_group_key` = the JSON array:

```text
[normalized_author_phrase, surface_year_component]
```

This field is emitted as an actual JSON array, not as a quoted serialized string.

It is extraction/aggregation only and MUST NOT be consumed by identity resolution or reconciliation.

### 6.7 Person-form extraction fields

When the source citation author syntax fully matches the person grammar:

```text
author_form = exact | et_al
visible_authors = ordered normalized surnames
```

Normalization = lowercase, internal whitespace collapsed to one ASCII space, particles retained.

For `exact`:

```json
{"kind":"exact","value":2}
```

where value = number of visible authors.

For `et_al`:

```json
{"kind":"minimum","value":3}
```

`author_count_constraint` uses key order `kind`, then `value`.

For a non-person full-phrase candidate, `author_form`, `visible_authors`, and `author_count_constraint` are `null`.

### 6.8 Possessive person surname normalization

Only when deriving a **person identity candidate surname**, strip one trailing ASCII `'s` or typographic `’s`, case-insensitive on `s`, after source extraction and before identity-key construction.

This does not modify:

- `citation_group`;
- `citation_segment`;
- `author_phrase`;
- `citation_surface_group_key`.

Thus `Fine's (1998)` may form person candidate surname `fine` while preserving the source surface verbatim.

### 6.9 Sentence-relative fields

For each citation group:

```text
sentence_position = start  iff group_start == sentence_start
                    end    iff group_end == content_end
                    middle otherwise

sentence_index = containing sentence ordinal
previous_sentence_end = prior sentence content_end | null
standalone = true iff group_start == sentence_start AND group_end == content_end
```

`standalone` is positional only. It does not infer which claim the citation supports.

## 7. Bibliography assembly and reference identity

This section is skipped entirely when `references_source = not_available`.

### 7.1 Line assembly

Trim leading/trailing `[ \t]` from each bibliography line before tests and joins.

At most one entry is open:

1. blank line → close entry;
2. heading line → close entry; heading excluded;
3. line matching `ENTRY_START` → close prior entry; open new;
4. otherwise, if line satisfies the entry-candidate guard below → close prior entry; emit `unresolved_reference` with reason `entry_start_grammar`;
5. otherwise append to open entry with one ASCII space; if none open emit `unresolved_reference`, reason `orphan_line`.

Entry-candidate guard: after leading particles, first code point is uppercase and either:

- `(` + supported numeric year or `n.d.` occurs within first 100 code points; or
- line matches a short pre-year pattern `^[^.\n]{2,60}\.[ \t]+\(?(YEAR)`.

Section end closes the open entry.

Closed `unresolved_reference.reason` enum:

```text
entry_start_grammar
orphan_line
no_year
```

### 7.2 Reference source span

`assembled` = joined entry text and is not verbatim because joins insert one space.

`start`/`end` cover the canonical-byte region from first non-horizontal-whitespace byte of the first source line through one past the last non-horizontal-whitespace byte of the final source line.

### 7.3 Reference year and plausibility

`year` = first supported YEAR token in `assembled`, normalized as in §3.

If no year exists, do **not** emit a `reference` record. Emit one `unresolved_reference` over the assembled entry source span with:

```text
reason = no_year
```

This preserves the year-less entry as an explicit, actionable bibliography defect without manufacturing an identity key.

Every emitted `reference` record therefore has a **non-null** `reference_key`. An unresolvable year-bearing author head is likewise diverted to `unresolved_reference`; a null authoritative reference identity is never serialized as a `reference`.

`validation_state = ok | suspect`.

`suspect_reasons` for emitted `reference` records is a closed ordered list:

1. `terminator`;
2. `overlong`;
3. `embedded_entry_pattern`.

Tests:

- `terminator`: assembled fails end-anchored `(?:\.|\?|\d+[–—-]\d+\.?|(?:doi:|https?://)\S+)$`;
- `overlong`: assembled length >1500 Unicode code points;
- `embedded_entry_pattern`: matches `. (?:PARTICLE )*CORE, (?:INITIALS ?)+` at offset >10.

A suspect reference with a non-null key still participates in reconciliation.

### 7.4 Reference author head

For a reference with a supported year, `reference_author_head` is the trimmed text before the opening `(` immediately containing the first YEAR token, with one trailing period removed and trailing whitespace trimmed.

Attempt the closed person-list parser first.

A person list is one or more units:

```text
SURNAME, WS INITIALS
```

separated by comma, `&`, or `and`, and it must consume the entire `reference_author_head` after ordinary separator punctuation normalization.

If full person-list parsing succeeds:

```text
author_kind = person
authors = ordered normalized surnames
author_count = len(authors)
identity_author_phrase = authors[0]
reference_key = person|<escaped identity_author_phrase>|<normalized_year>
```

If the complete ordered list is not confidently derivable but `reference_author_head` begins with a full `SURNAME` followed by a comma, the first surname is still sufficient for the bibliography identity used by this profile. Emit:

```text
author_kind = person
authors = null
author_count = null
identity_author_phrase = normalized leading SURNAME
reference_key = person|<escaped identity_author_phrase>|<normalized_year>
```

This covers full-forename references such as `Smith, John. (2020).` without pretending that the complete author list was parsed. Because `authors` and `author_count` are null, the entry takes no part in author-structure validation.

If neither person path applies, a non-person head is accepted only if:

- it contains at least one Unicode letter;
- it contains no comma;
- after trimming it is non-empty.

Then:

```text
author_kind = non_person
authors = null
author_count = null
identity_author_phrase = lower(canonical-whitespace-normalized reference_author_head)
reference_key = non_person|<escaped identity_author_phrase>|<normalized_year>
```

A year-bearing author head satisfying none of these paths → `unresolved_reference`, reason `entry_start_grammar`; no `reference` record is emitted for that entry.

A comma-containing organization author that cannot be distinguished from an unsupported person-list form is therefore unresolved rather than guessed.

### 7.5 Identity-key escaping

In identity-key middle components, escape in this order:

```text
\  -> \\
|  -> \|
```

Keys are:

```text
person|<escaped first-surname>|<year>
non_person|<escaped full-author-phrase>|<year>
```

Normal examples remain:

```text
person|smith|2020
non_person|world bank|2024
```

## 8. Pass 2 — bibliography-grounded citation identity resolution

Pass 2 runs only when `references_source ∈ {detected,inferred}`.

Syntax does not confer authoritative `author_kind` or `citation_key`. Pass 1 syntax creates deterministic **identity candidates** only. Authority is acquired only through exact bibliography resolution.

### 8.1 Candidate construction

For each extracted occurrence create a full internal candidate:

- if `author_phrase` fully matches the applicable person citation grammar:
  `candidate_key = person|<normalized first visible surname>|<year>`;
- otherwise:
  `candidate_key = non_person|<normalized complete author_phrase>|<year>`.

For narrative occurrences, if §6.3 produced `stop_reduced_phrase`, create a second candidate:

```text
person|<normalized first surname of stop_reduced_phrase>|<year>
```

Every internal candidate records:

```text
candidate_phrase
candidate_kind ∈ {person,non_person}
candidate_key
```

These are lookup candidates, not serialized authoritative citation identity.

### 8.2 Candidate lookup result

Lookup considers keyed `reference` records only.

Each candidate independently yields:

```text
match_state ∈ {no_match, unique, nonunique}
candidate_key : deterministic string
reference_indices : ascending integer array
```

`no_match` → zero reference indices.

`unique` → exactly one reference index.

`nonunique` → at least two reference indices, all sharing that authoritative `reference_key`.

Both full and STOP-reduced candidates MUST be evaluated before the occurrence identity result is chosen.

### 8.3 Exhaustive 3 × 3 decision table

Let F = full candidate match state and S = STOP-reduced candidate match state. If no STOP-reduced candidate exists, S is `no_match`.

| F | S | authoritative identity result |
|---|---|---|
| no_match | no_match | `author_resolution=not_resolved`; `author_kind=undetermined`; `resolved_author_phrase=null`; `citation_key=null` |
| unique | no_match | `author_resolution=full_phrase`; full key is authoritative; author kind from key |
| nonunique | no_match | same authoritative full key; additionally emit `ambiguous_citation` |
| no_match | unique | `author_resolution=stop_reduced`; STOP key is authoritative; author kind from key |
| no_match | nonunique | same authoritative STOP key; additionally emit `ambiguous_citation` |
| unique | unique | different keys → `ambiguous`; same key → exit 6 |
| unique | nonunique | different keys → `ambiguous`; same key → exit 6 |
| nonunique | unique | different keys → `ambiguous`; same key → exit 6 |
| nonunique | nonunique | different keys → `ambiguous`; same key → exit 6 |

For `author_resolution=ambiguous`:

```text
author_kind = undetermined
resolved_author_phrase = null
citation_key = null
```

Emit exactly one `ambiguous_author_resolution`.

A shared reference index across two different candidate identities is permitted and remains ordinary author-resolution ambiguity.

### 8.4 Unmatched candidate set

For `author_resolution=not_resolved`, retain the deterministic internal candidate set for §9.4.

```text
one internal candidate
    → candidate-level missing/mismatch diagnostics MAY run

two distinct internal candidates
    → identity is underdetermined even before fuzzy repair
    → missing_reference and possible_mismatch MUST NOT emit for that occurrence
```

This rule prevents a candidate-level diagnostic from pretending that syntax selected one authoritative identity.

### 8.5 Ambiguity reservation

Before candidate mismatch or uncited-reference computation, reserve:

1. all reference indices named by `ambiguous_author_resolution`;
2. all reference indices belonging to a citation key that resolves nonuniquely and therefore emits `ambiguous_citation`.

Reserved indices:

- are removed from the unmatched-reference pool;
- MUST NOT participate in `possible_mismatch`;
- MUST NOT emit `uncited_reference` solely because ambiguity prevented selection;
- do not count as uniquely matched unless independently matched by another unambiguous occurrence.

`duplicate_reference_key` still emits.

### 8.6 Internal invariant failure

If both full and STOP-reduced lookups are non-empty and serialize the same candidate key, abort:

```text
exit = 6
reason = same_candidate_identity_double_resolution
```

This is a system failure, not a manuscript diagnostic.

## 9. Reconciliation

This section runs only when `bibliography_reconciliation_performed = true`.

### 9.1 Bibliography identity and duplicate index

Build `by_reference_key` over all emitted `reference` rows.

For each key with at least two entries emit one `duplicate_reference_key`, indices ascending. `cited=true` iff at least one extracted occurrence has an authoritative non-null `citation_key` equal to that duplicate key; candidate-level missing/mismatch keys do not set `cited=true`.

### 9.2 Identity classification

After §8:

```text
author_resolution=full_phrase|stop_reduced
    + exactly one bibliography row for citation_key
    → identity_class = resolved_unique_reference

author_resolution=full_phrase|stop_reduced
    + >=2 bibliography rows for citation_key
    → identity_class = resolved_bibliography_key_ambiguous

author_resolution=ambiguous
    → identity_class = author_resolution_ambiguous

author_resolution=not_resolved
    → identity_class = identity_not_resolved
```

Only the first two classes have non-null authoritative `citation_key`.

### 9.3 Unique exact matches and author structure

A unique exact key match remains an established identity even if author-structure validation emits a mismatch.

For person citations with non-null person-form data and a matched reference with non-null `authors`/`author_count`:

**exact** passes iff:

```text
reference.author_count == len(visible_authors)
AND reference.authors[i] == visible_authors[i] for every i
```

**et_al** passes iff:

```text
reference.author_count >= ET_AL_MIN_AUTHORS
AND reference.authors[i] == visible_authors[i] for every visible i
```

On failure emit `author_structure_mismatch`.

If count and order both fail, `failed=count`.

An `exact` mismatch forces exit 1. An `et_al` mismatch is reported but does not by itself force exit 1 in v3.4.

### 9.4 Candidate-level possible mismatch and missing reference

This subsection applies only to occurrences where:

```text
identity_class = identity_not_resolved
AND exactly one deterministic internal candidate exists
```

The diagnostic candidate key remains **non-authoritative**.

Group such occurrences by that candidate key in first-occurrence order.

Build the unmatched unique-reference pool in reference source order, excluding all ambiguity-reserved indices and references already exactly matched by an authoritative citation identity.

For each unmatched candidate key, scan unmatched references in source order and take the first rule that matches. A pair MUST have the same candidate/reference author kind.

Rules, in precedence order:

1. `surname_edit_distance_1`:
   person kind only; years equal; `osa(candidate_identity_phrase, reference_identity_phrase) <= 1`;
   candidate CORE length >=4 code points;
2. `year_adjacent`:
   identity phrases exactly equal; both years numeric; absolute year difference =1;
3. `year_transposition`:
   identity phrases exactly equal; both numeric; one adjacent digit pair transposed.

If paired:

- emit `possible_mismatch`;
- remove the reference from the unmatched pool;
- all occurrences of that candidate contribute to `possible_mismatch_occurrences`.

If not paired:

- emit `missing_reference`;
- all occurrences of that candidate contribute to `reference_missing_occurrences`.

Neither diagnostic establishes `citation_key`, `author_kind`, or `resolved_citation_occurrences`.

### 9.5 Missing-reference merge qualification

For each candidate-level `missing_reference`, `merge_suspected=true` iff a reference whose `suspect_reasons` contains `embedded_entry_pattern` has `assembled` text containing both:

- an author phrase/surname equal to the diagnostic candidate identity phrase under that candidate kind; and
- a YEAR token equal to the candidate year.

This is conservative suspicion only.

### 9.6 Uncited references

After:

- exact authoritative matches;
- ambiguity reservation; and
- candidate-level possible-mismatch pairing

emit `uncited_reference` for every remaining unique keyed reference.

`unresolved_reference` rows are never uncited-reference candidates because they have no authoritative reference identity.

## 10. Bibliography-absent mode

If `references_source = not_available`:

```text
Pass 1 extraction               performed
Pass 2 identity resolution      not evaluated
bibliography extraction         not performed
reconciliation                  not evaluated
```

Each successfully extracted `citation` MUST serialize:

```text
author_kind = undetermined
resolved_author_phrase = null
author_resolution = not_evaluated
citation_key = null
citation_surface_group_key = computed
```

Do not emit:

```text
reference
unresolved_reference
ambiguous_author_resolution
missing_reference
uncited_reference
duplicate_reference_key
ambiguous_citation
possible_mismatch
author_structure_mismatch
```

Emit exactly one:

```json
{"type":"bibliography_absent","references_source":"not_available"}
```

`bibliography_absent` has exactly two fields, no index, and appears iff `references_source=not_available`.

Its presence forces normal exit 1.

`identity_resolution_performed = false`.
`bibliography_reconciliation_performed = false`.
`distinct_surface_groups` remains computed.
`distinct_works_cited` is `null`.
Identity-resolution and reconciliation outcome counts that were not evaluated are `null`.

## 11. Summary invariants

### 11.1 Extraction invariant — always

```text
total_citation_occurrences
=
extracted_citation_occurrences
+
unresolved_extraction_occurrences
```

### 11.2 Identity-resolution invariant — conditional

When `references_source ∈ {detected,inferred}`:

```text
identity_resolution_performed = true
bibliography_reconciliation_performed = true
```

If `identity_resolution_performed = true`:

```text
extracted_citation_occurrences
=
resolved_citation_occurrences
+
author_resolution_ambiguous_occurrences
+
identity_not_resolved_occurrences
```

where:

```text
resolved_citation_occurrences
=
unique_reference_match_occurrences
+
bibliography_key_ambiguous_occurrences
```

Candidate-level `reference_missing_occurrences` and `possible_mismatch_occurrences` are diagnostics over a subset of `identity_not_resolved_occurrences`; they are **not** additional identity-partition states.

### 11.3 Bibliography absence

If `identity_resolution_performed = false`:

```text
resolved_citation_occurrences = 0
author_resolution_ambiguous_occurrences = null
identity_not_resolved_occurrences = null
unique_reference_match_occurrences = null
bibliography_key_ambiguous_occurrences = null
reference_missing_occurrences = null
possible_mismatch_occurrences = null
uniquely_matched_occurrences = null
uniquely_matched_works = null
distinct_works_cited = null
```

`null` means the corresponding resolution/reconciliation quantity was not evaluated.

### 11.4 Summary field semantics

```text
identity_resolution_performed
    true iff Pass 2 was evaluated against an extracted bibliography.

bibliography_reconciliation_performed
    true iff bibliography reconciliation was evaluated; in v3.4 this equals
    identity_resolution_performed.

total_citation_occurrences
    all candidate occurrences that reached either citation or unresolved_citation output.

extracted_citation_occurrences
    serialized citation rows.

unresolved_extraction_occurrences
    serialized unresolved_citation rows.

resolved_citation_occurrences
    extracted occurrences with a non-null authoritative citation_key.

distinct_surface_groups
    unique citation_surface_group_key values among extracted citations; always emitted.

distinct_works_cited
    unique non-null authoritative citation_key values when identity resolution ran;
    null when identity resolution did not run.

uniquely_matched_occurrences
    occurrences with an authoritative citation_key mapped to exactly one reference row.

uniquely_matched_works
    distinct authoritative citation keys mapped to exactly one reference row.

reference_missing_occurrences
    occurrences represented by candidate-level missing_reference diagnostics.

possible_mismatch_occurrences
    occurrences represented by candidate-level possible_mismatch diagnostics.
```

## 12. Canonical JSONL output

### 12.1 Serialization

Canonical output is:

- UTF-8;
- no BOM;
- exactly one JSON object per line;
- LF line ending only;
- every line, including the final line, ends with exactly one LF;
- no blank lines;
- keys in the exact order declared for each record below;
- separators `,` and `:` with no insignificant spaces;
- non-ASCII characters emitted raw;
- mandatory JSON escapes only: `\"`, `\\`, `\n`, `\r`, `\t`; other C0 controls as lowercase `\u00xx`;
- booleans as `true`/`false`;
- integers as base-10 with no leading zero except `0`;
- null as `null`;
- arrays preserve their declared order;
- object-valued `author_count_constraint` key order is `kind`, then `value`.

No timestamp, random id, hostname, process id, filesystem path, run id or machine-specific datum may enter canonical records.

### 12.2 Normal-output block order

Empty blocks emit nothing. Blocks never interleave.

1. `meta`
2. `citation`
3. `unresolved_citation`
4. `bibliography_absent` (singleton only when `references_source=not_available`)
5. `reference`
6. `unresolved_reference`
7. `ambiguous_author_resolution`
8. `missing_reference`
9. `uncited_reference`
10. `duplicate_reference_key`
11. `ambiguous_citation`
12. `possible_mismatch`
13. `author_structure_mismatch`
14. `summary`

### 12.3 Record schemas and key order

Normal `meta`:

```json
{"type":"meta","spec_version":"3.4","citation_rule_version":"citation_v3.4_apa7_like_v1","citation_profile":"apa7_like_v1","mode":"standalone_nomap","canonical_sha256":"…","section_map_sha256":null,"references_source":"detected"}
```

`mode ∈ {standalone_nomap,standalone_map,orchestrated}`.

`citation`:

```json
{"type":"citation","index":0,"citation_group":"…","citation_segment":"…","author_phrase":"…","resolved_author_phrase":null,"author_resolution":"not_resolved","author_kind":"undetermined","citation_surface_group_key":["smith",2020],"citation_key":null,"year":"2020","style":"narrative","author_form":"exact","visible_authors":["smith"],"author_count_constraint":{"kind":"exact","value":1},"group_start":0,"group_end":0,"segment_start":0,"segment_end":0,"sentence":"…","sentence_start":0,"sentence_position":"middle","sentence_index":0,"previous_sentence_end":null,"standalone":false,"section_level":"h2","section_name":"Introduction","section_type":"introduction","section_roles":["introduction"]}
```

Enums:

```text
author_resolution ∈ {full_phrase,stop_reduced,not_resolved,ambiguous,not_evaluated}
author_kind ∈ {person,non_person,undetermined}
style ∈ {parenthetical,narrative}
author_form ∈ {exact,et_al} | null
section_level ∈ {h2,h3,h4,none}
```

`unresolved_citation`:

```json
{"type":"unresolved_citation","index":0,"text":"…","start":0,"end":0,"reason":"no_grammar_match","citation_surface_group_key":null,"sentence":"…","sentence_start":0,"section_level":"h2","section_name":"Introduction"}
```

`reference`:

```json
{"type":"reference","index":0,"assembled":"…","author_kind":"person","identity_author_phrase":"smith","reference_key":"person|smith|2020","authors":["smith","jones"],"author_count":2,"year":"2020","start":0,"end":0,"validation_state":"ok","suspect_reasons":[]}
```

Every emitted `reference` has non-null `reference_key`.

`unresolved_reference`:

```json
{"type":"unresolved_reference","index":0,"text":"…","start":0,"end":0,"reason":"entry_start_grammar"}
```

Closed reasons:

```text
entry_start_grammar
orphan_line
no_year
```

`ambiguous_author_resolution`:

```json
{"type":"ambiguous_author_resolution","citation_index":0,"author_phrase":"Panel Smith","full_match_state":"unique","full_candidate_key":"non_person|panel smith|2020","full_reference_indices":[4],"stop_reduced_phrase":"Smith","stop_reduced_match_state":"unique","stop_reduced_candidate_key":"person|smith|2020","stop_reduced_reference_indices":[7]}
```

`missing_reference` — candidate-level, non-authoritative:

```json
{"type":"missing_reference","candidate_key":"person|smith|2020","identity_authority":"candidate","example":"Smith (2020)","occurrences":2,"merge_suspected":false}
```

`identity_authority` is the literal `"candidate"`.

`uncited_reference`:

```json
{"type":"uncited_reference","reference_index":0,"reference_key":"person|smith|2020"}
```

`duplicate_reference_key`:

```json
{"type":"duplicate_reference_key","reference_key":"person|smith|2020","reference_indices":[2,5],"cited":true}
```

`ambiguous_citation`:

```json
{"type":"ambiguous_citation","citation_key":"person|smith|2020","example":"Smith (2020)","reference_indices":[2,5]}
```

`possible_mismatch` — candidate-level, non-authoritative:

```json
{"type":"possible_mismatch","candidate_key":"person|barko|2020","identity_authority":"candidate","reference_index":6,"reference_key":"person|bartko|2020","evidence":"surname_edit_distance_1"}
```

`evidence ∈ {surname_edit_distance_1,year_adjacent,year_transposition}`.

`author_structure_mismatch`:

```json
{"type":"author_structure_mismatch","citation_key":"person|smith|2020","reference_index":0,"citation_author_form":"exact","visible_authors":["smith","jones"],"author_count_constraint":{"kind":"exact","value":2},"reference_authors":["smith","brown"],"reference_author_count":2,"failed":"order","example":"Smith & Jones (2020)"}
```

`failed ∈ {count,order}`.

`bibliography_absent`:

```json
{"type":"bibliography_absent","references_source":"not_available"}
```

`summary`:

```json
{"type":"summary","identity_resolution_performed":true,"bibliography_reconciliation_performed":true,"total_citation_occurrences":0,"extracted_citation_occurrences":0,"unresolved_extraction_occurrences":0,"resolved_citation_occurrences":0,"distinct_surface_groups":0,"distinct_works_cited":0,"uniquely_matched_occurrences":0,"uniquely_matched_works":0,"unique_reference_match_occurrences":0,"bibliography_key_ambiguous_occurrences":0,"reference_missing_occurrences":0,"possible_mismatch_occurrences":0,"author_resolution_ambiguous_occurrences":0,"identity_not_resolved_occurrences":0,"canonical_sha256":"…","section_map_sha256":null,"references_source":"detected","exit":0}
```

When identity resolution/reconciliation is not performed, §10–§11 define which fields are `null`.

### 12.4 Total deterministic order

Every block MUST have a total deterministic ordering; two distinct records may not remain tied on every declared key.

Orders:

```text
citation                     (group_start, segment_start, year, canonical bytes of citation_surface_group_key)
unresolved_citation          (start, end, reason, text UTF-8 bytes)
reference                    (start, end, assembled UTF-8 bytes)
unresolved_reference         (start, end, reason, text UTF-8 bytes)
ambiguous_author_resolution  citation_index
missing_reference            first occurrence position of candidate_key, then candidate_key UTF-8 bytes
uncited_reference            reference_index
duplicate_reference_key      smallest member reference_index, then reference_key UTF-8 bytes
ambiguous_citation           first occurrence position of citation_key, then citation_key UTF-8 bytes
possible_mismatch            candidate pairing order established in §9.4
author_structure_mismatch    (citation index of first corresponding occurrence, reference_index, failed)
bibliography_absent          singleton
summary                      singleton, always last
```

`index` is 0-based per record type in serialized order. All `reference_index` values refer to the serialized `reference.index`.

## 13. File output and atomicity

`--out <path>` writes the byte-identical canonical stream that would be written to stdout.

If `<path>` names a directory, the target filename is:

```text
<canonical_sha256>.citations.jsonl
```

No output field depends on target path.

File publication:

1. build complete bytes in a temporary file in the destination directory;
2. evaluate all abort-class conditions, including exit 6;
3. fsync/close according to platform implementation as needed for safe rename;
4. atomically rename over the target only after complete output is known.

A normal file whose final record is not `summary` is incomplete. An abort file whose final record is not `error` is incomplete.

For exits 2–5, the two-line error stream is written to the requested file as the authoritative error artifact.

For exit 6, no partial normal artifact may be published; if `--out` was requested, the authoritative file contains only the two-line error stream after the invariant failure has been established.

## 14. Exit and abort semantics

Normal exits:

```text
0  completed; no exit-1 finding condition
1  completed; one or more defined finding conditions
```

Abort/system exits:

```text
2  unsupported citation style
3  invalid section map
4  heading contract violated
5  invalid utf-8
6  internal invariant violation
```

Exit 2 detector, after body identification and extraction attempt:

```text
N = NUMCITE matches + SUPCITE runs in body
P = successfully extracted citation occurrences
abort iff N >= 3 AND N > 10 * P
```

Exit 1 is forced by any of:

- bibliography_absent;
- any extracted citation with `author_resolution=not_resolved`;
- unresolved_citation;
- unresolved_reference;
- candidate-level missing_reference;
- residual uncited_reference;
- candidate-level possible_mismatch;
- duplicate_reference_key;
- ambiguous_citation;
- ambiguous_author_resolution;
- any suspect reference;
- any `exact` author_structure_mismatch.

An `et_al` author_structure_mismatch alone does not force exit 1.

### 14.1 Abort serialization

On exit 2–6 stdout is exactly two lines:

```json
{"type":"meta","spec_version":"3.4","citation_rule_version":"citation_v3.4_apa7_like_v1"}
{"type":"error","code":6,"reason":"same_candidate_identity_double_resolution"}
```

The `code` and `reason` vary by exit:

```text
2 -> unsupported citation style
3 -> invalid section map
4 -> heading contract violated
5 -> invalid utf-8
6 -> same_candidate_identity_double_resolution
```

stderr is non-normative.

No normal record may precede the error stream.

## 15. Test-only invariant-injection seam

The implementation MUST expose a substitutable resolver seam to the conformance harness immediately before the §8.3 decision table.

The seam may inject, independently for full and STOP-reduced candidates:

```text
match_state
candidate_key
reference_indices[]
```

It MUST NOT alter:

- Pass-1 parsing;
- candidate spans;
- source bibliography bytes;
- reference extraction;
- production runtime behavior.

It MUST NOT be reachable through CLI flags, environment variables, config files, API parameters, or ordinary production dependency injection.

Production binds the deterministic real resolver.

The mandatory invariant-injection case sets both candidates to non-empty results with the same `candidate_key`; expected result = exit 6, exact two-line error stream, no partial normal authoritative artifact.

## 16. Out of envelope and accepted limitations

### 16.1 Out of envelope

No citation record is required for:

- square-bracket author–year forms such as `[Smith, 2020]`;
- author–year without parentheses, e.g. `as Smith 2020 argued`;
- years outside 1500–2099;
- footnote citation styles outside the candidate recognizer;
- superscript citation styles outside the exit-2 dominance detector;
- numeric citations as citation identities.

Extending the envelope is a versioned specification change.

### 16.2 In-envelope limitations with defined behavior

- comma-less parentheticals surface as `no_grammar_match`;
- forename-first parentheticals surface as `no_grammar_match`;
- all-caps first-author cores surface as `all_caps_surname`;
- unsupported prefatory prose inside a candidate surfaces as `no_grammar_match` preserving the complete candidate span;
- full-forename bibliography author lists may establish first-surname person identity, but their complete ordered `authors` list remains null and therefore receives no author-structure check;
- organization names containing commas that cannot be distinguished from unsupported person-list syntax remain unresolved;
- the sentence splitter is a closed-guard approximation;
- `embedded_entry_pattern` is a merge suspicion tripwire, not a repair;
- column-interleaved PDF conversion corruption is upstream conversion scope, not repaired here.

## 17. Mandatory conformance classes

The companion matrix enumerates exact cases. At minimum the executable suite MUST cover:

1. canonicalization + invalid UTF-8;
2. multibyte byte offsets and the three code-point-count exceptions;
3. standalone heading/ref detection including detected/inferred/not_available;
4. supplied valid/invalid Section Map behavior and no fallback on invalid map;
5. parenthetical grammar and every supported PREFIX;
6. longest PREFIX match;
7. every STOP token in synthetic narrative coverage;
8. World Bank / structural-word institutional cases;
9. possessive person citations;
10. multi-year total ordering;
11. surface grouping and authority prohibition;
12. all nine cells of the 3×3 identity-resolution table;
13. ambiguity reservation for author-resolution ambiguity and duplicate-key ambiguity;
14. candidate-level mismatch pairing precedence and proof that it does not establish citation identity;
15. merge_suspected qualification;
16. author-structure exact and et_al cases;
17. bibliography-absent `not_evaluated` identity state and nullable summary;
18. summary invariants;
19. canonical JSONL byte serialization;
20. atomic file/error publication;
21. invariant injection / exit 6;
22. current 11-paper regression/conformance corpus.

## 18. Corpus blocking taxonomy

The 11-paper corpus is a regression/conformance discovery corpus, not a validation sample.

A corpus finding is BLOCKING if it reveals any of:

1. output contradicts a normative rule;
2. an in-envelope candidate is silently dropped;
3. false extracted citation/reference content, false identity, or false reconciliation diagnostic, whether caused by specification or implementation defect;
4. an invariant, partition, cardinality, or closed-enum violation;
5. deterministic ordering or canonical-byte failure;
6. exit, abort, or atomic-publication failure;
7. bounded-termination failure or hang;
8. standalone/orchestrated scope behavior violation;
9. an input claimed as supported has undefined behavior;
10. a pinned dependency contract is incompatible.

A finding is non-blocking only when its disposition cites the exact governing artifact/rule that establishes one of:

- declared out-of-envelope input;
- expected unresolved/ambiguous behavior;
- explicitly accepted known limitation;
- correctly classified unsupported input;
- explicit deferral outside v3.4 scope.

An undocumented “expected” failure is not a non-blocking category. It remains a specification gap/blocker until formally dispositioned.

## 19. Freeze and GSD-pilot gate

This document is eligible for document-wide freeze only after the applicable governance gates pass.

For the **GSD pilot target scope**:

```text
citation_v3_4_standalone_cli_nomap_apa7_like_v1
```

the following are required before product implementation planning/execution begins:

- exact rc2 candidate SHA is computed and retained;
- independent static review is bound to exact spec id/version/revision/SHA;
- no unresolved blocking finding remains;
- pilot-scope executable conformance cases have accepted evidence;
- the focused HIGH-rung deterministic kernel evidence is accepted;
- Unicode 15.0.0 behavior required by this contract is demonstrated in the execution environment;
- final freeze/disposition sets `content_state=frozen`;
- the pilot target conformance scope is explicitly established as `authority_state=current`.

Section Map and Orchestrator are **not** freeze dependencies for the standalone/no-map pilot scope.

The map-consuming standalone scope remains `not_yet_authoritative` until Section Map v1.1 is bound by exact frozen/current artifact identity.

The EpistemicOS pipeline scope remains `not_yet_authoritative` until both Section Map and Orchestrator dependencies are verified.

The GSD pilot runbook MUST treat any attempt to Execute product code before the pilot target scope is frozen/current as a preflight failure. GSD planning, convergence, or code MUST NOT create new citation behavior; any discovered normative gap routes back to the specification lifecycle.

Until these gates pass, this file is a Level-5 review candidate, not an authoritative implementation contract.
