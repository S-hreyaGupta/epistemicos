---
spec_id: citation_execution_conformance
spec_version: "3.4"
candidate_revision: 1
quality_level: 5
content_state: review_candidate
frozen_at: null
supersedes: null
superseded_by: null
authoritative_source: docs/specs/citation_execution_conformance_v3.4_rc1.md
validation_risk: high
selected_validation_rung: high
validation_rationale: >-
  Citation extraction, identity resolution and reconciliation are deterministic,
  persistent and user-visible. False extraction or false coherence diagnostics can
  contaminate downstream manuscript analysis. Baseline byte-compared conformance,
  invariant injection, a focused deterministic-kernel implementation/prototype and
  the current 11-paper regression corpus are proportionate before freeze; the corpus
  is not a population-validity sample.
conformance_scopes:
  - scope: citation_v3_4_standalone_cli_apa7_like_v1
    authority_state: not_yet_authoritative
    authority_reason: pending dependency verification, independent review, executable conformance evidence and freeze
  - scope: citation_v3_4_epistemicos_pipeline_apa7_like_v1
    authority_state: not_yet_authoritative
    authority_reason: pending frozen/current Section Map v1.1 binding, Orchestrator compatibility, independent review, executable conformance evidence and freeze
dependencies:
  - dependency_id: section_map
    required_version: "1.1"
    required_state: frozen_current_before_citation_v3_4_freeze
    required_sha256: null
    verified_at: null
  - dependency_id: orchestrator_build_spec
    required_version: "2.3"
    required_state: current_for_epistemicos_pipeline_scope_before_freeze
    required_sha256: null
    verified_at: null
external_authorities:
  - authority_id: unicode
    required_version: "15.0.0"
    verified_at: null
review_evidence: []
---

# Citation Execution + Conformance Specification v3.4

**Status:** Level-5 freeze-ready review candidate. The behavioral contract is closed; this document is **not frozen** and has no current authority until the companion freeze checklist's external dependency, independent-review and executable-evidence gates pass.

## 0. Capability and scope

This specification defines the observable deterministic contract for:

1. supported author–year citation extraction;
2. bibliography-entry extraction;
3. citation identity resolution;
4. citation ↔ bibliography structural reconciliation;
5. canonical JSONL output on stdout and optional file output.

It governs two intended conformance scopes:

```text
citation_v3_4_standalone_cli_apa7_like_v1
citation_v3_4_epistemicos_pipeline_apa7_like_v1
```

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

### 2.1 Standalone mode

Required input:

```text
source_bytes : byte string
```

Optional input:

```text
section_map_bytes : null | exact Section Map v1.1 JSONL bytes
```

If no Section Map is supplied, standalone mode executes the deterministic structure fallback in §4.

### 2.2 EpistemicOS orchestrated mode

Required inputs:

```text
source_bytes       : byte string
section_map_bytes  : exact Section Map v1.1 JSONL bytes
```

The Section Map MUST:

- have `map_version = "1.1"`;
- describe the same `canonical_sha256`;
- satisfy its own validity invariants;
- have the review state required by the current Orchestrator contract; for Orchestrator v2.3 this is `review_state = passed`;
- be the structural source of truth for section/bibliography boundaries and section metadata.

The no-map fallback in §4 is forbidden in orchestrated mode.

`section_map_sha256` = lowercase SHA-256 over the exact supplied Section Map file bytes; it is `null` when no map is supplied.

### 2.3 Determinism tuple

Standalone without map:

```text
(canonical_manuscript_bytes, citation_rule_version)
```

With a supplied map, including orchestrated mode:

```text
(canonical_manuscript_bytes, section_map_bytes, citation_rule_version)
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

Syntax does not confer `author_kind`. Authority is acquired only through bibliography resolution.

### 8.1 Candidate construction

For each extracted occurrence create a full candidate:

- if `author_phrase` fully matches the applicable person citation grammar, full candidate key = `person|<normalized first visible surname>|<year>`;
- otherwise full candidate key = `non_person|<normalized complete author_phrase>|<year>`.

For narrative occurrences, if §6.3 produced `stop_reduced_phrase`, create a second candidate key:

```text
person|<normalized first surname of stop_reduced_phrase>|<year>
```

If no stop-reduced phrase exists, its match state is `no_match`, candidate key is `null`, and reference-index array is empty.

### 8.2 Candidate lookup result

Lookup considers keyed `reference` records only.

Each candidate independently yields:

```text
match_state ∈ {no_match, unique, nonunique}
candidate_key : string | null
reference_indices : ascending integer array
```

`no_match` → candidate_key MAY remain the deterministic proposed key for internal processing, but serialized diagnostic candidate_key is `null` when there is no bibliography match.

`unique` → exactly one reference index.

`nonunique` → at least two reference indices, all sharing that authoritative `reference_key`.

Both full and stop-reduced candidates MUST be evaluated before the occurrence outcome is chosen. No successful first lookup may short-circuit the second lookup.

### 8.3 Exhaustive 3 × 3 decision table

Let F = full candidate match state and S = stop-reduced candidate match state.

| F | S | occurrence identity result |
|---|---|---|
| no_match | no_match | `author_resolution=unresolved`; `author_kind=unresolved`; `resolved_author_phrase=null`; `citation_key=null` |
| unique | no_match | `author_resolution=full_phrase`; choose full key; author kind from key; resolved phrase = full phrase |
| nonunique | no_match | same as above; additionally emit `ambiguous_citation` for full key |
| no_match | unique | `author_resolution=stop_reduced`; choose stop key; author kind from key; resolved phrase = stop-reduced phrase |
| no_match | nonunique | same as above; additionally emit `ambiguous_citation` for stop key |
| unique | unique | if keys differ → `author_resolution=ambiguous`; if keys equal → exit 6 invariant failure |
| unique | nonunique | if keys differ → `author_resolution=ambiguous`; if keys equal → exit 6 invariant failure |
| nonunique | unique | if keys differ → `author_resolution=ambiguous`; if keys equal → exit 6 invariant failure |
| nonunique | nonunique | if keys differ → `author_resolution=ambiguous`; if keys equal → exit 6 invariant failure |

For `author_resolution=ambiguous`:

```text
author_kind = unresolved
resolved_author_phrase = null
citation_key = null
```

Emit exactly one `ambiguous_author_resolution` for the occurrence.

A shared reference index across the two **different** candidate identities is permitted and remains ordinary author-resolution ambiguity.

### 8.4 Ambiguity reservation

Before possible-mismatch or uncited-reference computation, reserve:

1. all reference indices named by an `ambiguous_author_resolution`;
2. all reference indices belonging to an authoritative citation key that resolves nonuniquely and therefore emits `ambiguous_citation`.

Reserved indices:

- are removed from the unmatched-reference pool;
- MUST NOT participate in `possible_mismatch`;
- MUST NOT emit `uncited_reference` solely because the ambiguous occurrence did not choose them;
- do not count as uniquely matched unless independently matched by another unambiguous citation occurrence.

`duplicate_reference_key` still emits for duplicate bibliography identities.

### 8.5 Internal invariant failure

If both full and stop-reduced candidate lookups are non-empty and serialize the same candidate key, the implementation has violated the candidate-construction invariant.

Abort with:

```text
exit = 6
reason = same_candidate_identity_double_resolution
```

This is system failure, not a manuscript diagnostic.

## 9. Reconciliation

This section runs only when bibliography reconciliation is performed.

### 9.1 Identity and duplicate index

Build `by_reference_key` over non-null `reference_key` values.

For each key with at least two entries emit one `duplicate_reference_key`, reference indices ascending.

### 9.2 Per-occurrence outcome classification

After §8 identity resolution:

- `author_resolution=ambiguous` → `author_resolution_ambiguous`;
- unresolved/null citation key → `unresolved`;
- citation key held by >=2 references → `bibliography_key_ambiguous`;
- citation key held by exactly one reference → `unique_reference_match` initially;
- citation key held by no reference → unresolved reconciliation candidate for §9.4.

### 9.3 Unique matches and author structure

A unique key match is retained as a unique match even if author structure later produces a mismatch diagnostic.

For person citations with non-null citation person-form data and a matched reference with non-null `authors`/`author_count`:

**exact** passes iff:

```text
reference.author_count == len(visible_authors)
AND reference.authors[i] == visible_authors[i] for every i
```

**et_al** passes iff:

```text
reference.author_count >= 3
AND reference.authors[i] == visible_authors[i] for every visible i
```

On failure emit `author_structure_mismatch`:

```text
failed = count  if count constraint fails
failed = order  otherwise
```

If both fail, `count` takes precedence.

An `exact` mismatch forces normal exit 1. An `et_al` mismatch is reported but does not by itself force exit 1 in v3.4.

A reference with `authors=null` takes no part in author-structure checking.

### 9.4 Missing versus possible mismatch

For each resolved citation key with no reference match, preserve first-occurrence key order.

Build the unmatched unique-reference pool in reference source order, excluding all ambiguity-reserved indices.

Scan missing citation keys in order; for each, scan unmatched unique references in source order and take the first matching rule, then remove both from their respective residual pools.

A pair MUST have the same `author_kind`.

Rules in precedence order:

1. `surname_edit_distance_1`: person kind only; years equal; `osa(identity_phrase_cite, identity_phrase_ref) <= 1`; citation person CORE length >=4 code points;
2. `year_adjacent`: identity phrases exactly equal; both years numeric; absolute year difference =1;
3. `year_transposition`: identity phrases exactly equal; both numeric; reference year equals citation year with exactly one adjacent digit pair swapped and years are not equal.

A consumed missing occurrence/key becomes outcome `possible_mismatch` for every occurrence of that citation key. A residual missing key becomes `reference_missing`.

### 9.5 Missing-reference merge qualification

For each residual `missing_reference`, `merge_suspected=true` iff at least one reference whose `suspect_reasons` contains `embedded_entry_pattern` has `assembled` text containing both:

- a surname/author phrase equal to the missing key's identity phrase under the applicable author-kind normalization; and
- a YEAR token equal to the missing key's normalized year.

Otherwise false.

This is a conservative suspicion flag only. The missing-reference record still emits and still contributes to exit 1.

### 9.6 Uncited references

After ambiguity reservation and mismatch pairing, emit `uncited_reference` for every remaining unique keyed reference not independently matched by any citation identity, in source order.

`unresolved_reference` records, including `no_year`, are not `uncited_reference` candidates because they have no authoritative key.

## 10. Bibliography-absent mode

If `references_source = not_available`:

```text
Pass 1                         performed
Pass 2 identity resolution     not performed
bibliography extraction        not performed
reconciliation                 not performed
```

Each successfully extracted citation MUST serialize:

```text
author_kind = unresolved
resolved_author_phrase = null
author_resolution = unresolved
citation_key = null
citation_surface_group_key = computed
```

Do not emit:

```text
reference
unresolved_reference
missing_reference
uncited_reference
duplicate_reference_key
ambiguous_citation
ambiguous_author_resolution
possible_mismatch
author_structure_mismatch
```

Emit exactly one:

```json
{"type":"bibliography_absent","references_source":"not_available"}
```

Its presence forces normal exit 1.

`distinct_surface_groups` remains computable. `distinct_works_cited` is `null`.

## 11. Summary invariants

### 11.1 Extraction invariant — always

```text
total_citation_occurrences
=
extracted_citation_occurrences
+ unresolved_extraction_occurrences
```

### 11.2 Reconciliation partition — only when performed

```text
total_citation_occurrences
=
unique_reference_match_occurrences
+ bibliography_key_ambiguous_occurrences
+ reference_missing_occurrences
+ possible_mismatch_occurrences
+ author_resolution_ambiguous_occurrences
+ unresolved_identity_occurrences
```

Counts are per citation occurrence, not per diagnostic record.

When `bibliography_reconciliation_performed=false`, every reconciliation outcome count is `null`; the reconciliation invariant is not evaluated.

### 11.3 Summary field semantics

```text
resolved_citation_occurrences
    occurrences with non-null authoritative citation_key;
    includes unique match, bibliography-key ambiguous, reference missing,
    and possible mismatch outcomes.

distinct_surface_groups
    count of unique citation_surface_group_key values among extracted citations.

distinct_works_cited
    count of unique non-null authoritative citation_key values when identity
    resolution was performed; null when it was not.

uniquely_matched_occurrences
    occurrences resolved unambiguously to exactly one reference entry.

uniquely_matched_works
    distinct reference indices with at least one unambiguous matched occurrence.
```

Ambiguity-reserved entries do not count as uniquely matched unless independently matched elsewhere.

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
4. `reference`
5. `unresolved_reference`
6. `ambiguous_author_resolution`
7. `missing_reference`
8. `uncited_reference`
9. `duplicate_reference_key`
10. `ambiguous_citation`
11. `possible_mismatch`
12. `author_structure_mismatch`
13. `bibliography_absent`
14. `summary`

### 12.3 Record schemas and key order

Normal `meta`:

```json
{"type":"meta","spec_version":"3.4","citation_rule_version":"citation_v3.4_apa7_like_v1","citation_profile":"apa7_like_v1","mode":"standalone","canonical_sha256":"…","section_map_sha256":null,"references_source":"detected"}
```

`mode ∈ {standalone,orchestrated}`.

`citation`:

```json
{"type":"citation","index":0,"citation_group":"…","citation_segment":"…","author_phrase":"…","resolved_author_phrase":null,"author_resolution":"unresolved","author_kind":"unresolved","citation_surface_group_key":["smith",2020],"citation_key":null,"year":"2020","style":"narrative","author_form":"exact","visible_authors":["smith"],"author_count_constraint":{"kind":"exact","value":1},"group_start":0,"group_end":0,"segment_start":0,"segment_end":0,"sentence":"…","sentence_start":0,"sentence_position":"middle","sentence_index":0,"previous_sentence_end":null,"standalone":false,"section_level":"h2","section_name":"Introduction","section_type":"introduction","section_roles":["introduction"]}
```

Enums:

```text
author_resolution ∈ {full_phrase,stop_reduced,unresolved,ambiguous}
author_kind ∈ {person,non_person,unresolved}
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

`reference_key` is non-null for every `reference` record.

`unresolved_reference`:

```json
{"type":"unresolved_reference","index":0,"text":"…","start":0,"end":0,"reason":"entry_start_grammar"}
```

`ambiguous_author_resolution`:

```json
{"type":"ambiguous_author_resolution","citation_index":0,"author_phrase":"Panel Smith","full_match_state":"unique","full_candidate_key":"non_person|panel smith|2020","full_reference_indices":[4],"stop_reduced_phrase":"Smith","stop_reduced_match_state":"unique","stop_reduced_candidate_key":"person|smith|2020","stop_reduced_reference_indices":[7]}
```

`missing_reference`:

```json
{"type":"missing_reference","citation_key":"person|smith|2020","example":"Smith (2020)","occurrences":2,"merge_suspected":false}
```

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

`possible_mismatch`:

```json
{"type":"possible_mismatch","citation_key":"person|barko|2020","reference_index":6,"reference_key":"person|bartko|2020","evidence":"surname_edit_distance_1"}
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
{"type":"summary","bibliography_reconciliation_performed":true,"total_citation_occurrences":0,"extracted_citation_occurrences":0,"unresolved_extraction_occurrences":0,"resolved_citation_occurrences":0,"distinct_surface_groups":0,"distinct_works_cited":0,"uniquely_matched_occurrences":0,"uniquely_matched_works":0,"unique_reference_match_occurrences":0,"bibliography_key_ambiguous_occurrences":0,"reference_missing_occurrences":0,"possible_mismatch_occurrences":0,"author_resolution_ambiguous_occurrences":0,"unresolved_identity_occurrences":0,"canonical_sha256":"…","section_map_sha256":null,"references_source":"detected","exit":0}
```

When reconciliation is not performed, the fields specified as unavailable in §10–§11 are `null` rather than 0.

### 12.4 Total deterministic order

Every block MUST have a total deterministic ordering; two distinct records may not remain tied on every declared key.

Orders:

```text
citation                     (group_start, segment_start, year, canonical bytes of citation_surface_group_key)
unresolved_citation          (start, end, reason, text UTF-8 bytes)
reference                    (start, end, assembled UTF-8 bytes)
unresolved_reference         (start, end, reason, text UTF-8 bytes)
ambiguous_author_resolution  citation_index
missing_reference            first occurrence position of citation_key, then citation_key UTF-8 bytes
uncited_reference            reference_index
duplicate_reference_key      smallest member reference_index, then reference_key UTF-8 bytes
ambiguous_citation           first occurrence position of citation_key, then citation_key UTF-8 bytes
possible_mismatch            pairing order established in §9.4
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
- unresolved_citation;
- unresolved_reference;
- residual missing_reference;
- residual uncited_reference;
- possible_mismatch;
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
14. mismatch pairing precedence;
15. merge_suspected qualification;
16. author-structure exact and et_al cases;
17. bibliography-absent nullable summary;
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

## 19. Freeze gate

This specification may become frozen/current only after:

- the exact Section Map v1.1 dependency is frozen/current and bound by version + SHA-256 + freeze/disposition evidence;
- Orchestrator v2.3 (or its formally superseding current contract) is verified for the pipeline scope;
- every matrix case has executable evidence;
- the focused deterministic kernel has the selected HIGH-rung reference implementation/prototype evidence;
- the 11-paper corpus has no unresolved blocking finding under §18;
- an independent reviewer evaluates this exact spec_id/spec_version/candidate_revision/SHA-256;
- reviewer provenance and raw findings are retained;
- disagreements are resolved or recorded by the accountable human owner using the predeclared blocker taxonomy;
- no normative change after that review remains unevaluated;
- the final freeze review changes `content_state` to `frozen` and the approved scope authority states to `current`.

Until then, this document remains a freeze-ready **review candidate**, not an authoritative frozen spec.
