# Citation extraction & bibliographic coherence — deterministic spec v3.3

Capability: extraction of author–year in-text citations, extraction of
bibliography entries, and citation ↔ reference **structural** coherence
checking. Not in scope: claim–citation linking, citation validity, evidence
support.

Determinism claim: deterministic per versioned implementation — same input
bytes → identical output bytes. Cross-implementation byte identity requires
the pinned parameters in §1. Nothing is guessed: **citation-like input
within the supported candidate envelope (§6.1) is never silently dropped**
— it is parsed, or emitted as `unresolved_*`/`suspect`. Input outside the
envelope (§11) is out of scope **by declaration, not by accident**.

## 0. Conventions

- **All spans are half-open `[start, end)`**, in 0-based Unicode code point
  offsets into the normalized text (§2). Every `*_start`/`*_end` pair in
  this spec and the output uses this convention; no field is inclusive.
- `lower()` = Unicode simple lowercase (§1). `osa()` = OSA
  Damerau–Levenshtein (§1).
- Regexes: `\p{..}` classes per pinned Unicode version; matching is
  anchored exactly where written; nothing is a substring match unless
  stated.

## 1. Pinned runtime parameters

- Unicode 15.0.0 for NFC, `\p{Lu}`, `\p{L}`, `\p{M}`, `\p{N}`.
- Lowercasing = Unicode simple lowercase (1:1; unmapped code points pass
  through).
- Edit distance = optimal string alignment Damerau–Levenshtein, unit = code
  point after NFC.
- Invalid UTF-8 → exit 5, before any other processing.
- Output: UTF-8, no BOM, LF; every line (including the last) ends with
  exactly one LF.

## 2. Input normalization

1. Decode UTF-8 (failure → exit 5).
2. CRLF and lone CR → LF.
3. NFC.

"Verbatim" below always means verbatim after this normalization.

## 3. Document structure

### 3.1 Heading grammar

- Markdown ATX, per line: `HEAD_MD = ^(#{1,6})[ \t]+(.*)$`; level = number
  of `#`; name = group 2 with one trailing match of `(?:[ \t]+#+)?[ \t]*$`
  removed (closing hashes need preceding whitespace: `## C#` keeps its `#`,
  `## Intro ##` strips). Setext headings are NOT recognized.
- HTML, whole line only, tags case-insensitive:
  `HEAD_HTML = ^[ \t]*<h([1-6])(?:[ \t][^>]*)?>(.*?)</h\1>[ \t]*$`; name =
  inner text with remaining `<[^>]*>` removed and whitespace collapsed.
  Inline `<h2>…</h2>` inside a prose line is NOT a heading; multi-line HTML
  headings are NOT recognized.
- `clean(name)` = name with leading numbering `^\d+(\.\d+)*[.)]?[ \t]+`
  removed. All section names and comparisons use `clean(name)`.

### 3.2 Heading contract (exit 4)

h1 carries no structural meaning. If a document's sectioning apparently
lives in h1 — **≥ 2 h1 headings AND 0 h2 headings** — exit 4 rather than
guess a remapping. A stray extra h1 alongside h2 structure is tolerated and
ignored.

### 3.3 References section (exit 3)

Starts at the first h2–h4 heading with `lower(clean(name))` ∈
{ `references`, `bibliography`, `works cited` }; ends before the next
heading of level ≤ that heading's level, else EOF. Absent → exit 3.
Everything else is "body". Citations come from body only; references from
the section only.

### 3.4 Section stack and typing

Scan body headings in order; stack of (level, name) for h2–h4 only: on
level L pop entries with level ≥ L, push (L, clean(name)). h1/h5/h6 do not
change the stack but are structural lines for §5 and §7. A citation's
section = stack top at its `group_start`; empty stack → level `none`, name
`front matter`.

Role keywords, word-boundary matched (`(?<![\p{L}\p{N}_])` …
`(?![\p{L}\p{N}_])`) against `lower(section name)`:

| role | keywords |
|------|----------|
| introduction | introduction |
| literature_review | literature; related work; background |
| methodology | method; methods; methodology |
| results | result; results; finding; findings |
| discussion | discussion |
| conclusion | conclusion; conclusions |

`roles(name)` = all roles with ≥ 1 hit, ordered by leftmost hit (ties by
table order). For a citation: walk the stack innermost → outermost; the
first entry with non-empty roles supplies `section_roles`; `section_type` =
its first role; none → `[]` / `other`.

## 4. Grammar (normative)

`WS = [ \t\n]+` (a citation may wrap a soft line break; blank lines cannot
occur inside a sentence, §5).

```
NAMECHAR     = [\p{L}\p{M}'’-]
CORE         = \p{Lu}NAMECHAR+                    (≥ 2 code points)
PARTICLE     = de|del|della|der|den|di|da|dos|du|la|le|van|von|ter|ten|zu|zur
               (single words, compared via lower(); compounds by repetition)
SURNAME      = (?:PARTICLE WS)* CORE
YEAR         = (?:1[5-9]|20)\d{2}[a-z]? | n\.d\.
INITIALS     = \p{Lu}\.(?:[- ]?\p{Lu}\.)*
AUTHORS_PAREN= SURNAME WS et WS al\.
             | SURNAME(?:, WS? SURNAME)*(?:,? WS (?:&|and) WS SURNAME)?
AUTHORS_NARR = SURNAME WS et WS al\.
             | SURNAME(?:, WS SURNAME)* ,? WS (?:&|and) WS SURNAME
             | SURNAME
LOCATOR      = , WS? (?:p\.|pp\.|para\.|chap\.) WS? [^();]+
PREFIX       = (?:e\.g\.|i\.e\.|cf\.|see also|see|but see)[, ] WS?
SEG          = (?:PREFIX)? AUTHORS_PAREN , WS YEAR (?:, WS YEAR)* (?:LOCATOR)?
CITE_PAREN   = \( WS? SEG (?:; WS? SEG)* WS? \)
CITE_NARR    = AUTHORS_NARR WS \( WS? YEAR (?:, WS YEAR)* (?:LOCATOR)? WS? \)
ENTRY_START  = ^(?:PARTICLE[ ])* CORE , [ ] INITIALS
NUMCITE      = \[\d{1,3}(?:[ \t]*[,–—-][ \t]*\d{1,3})*\]
SUPCITE      = [\u00B9\u00B2\u00B3\u2070\u2074-\u2079]+
```

**Supported publication-year range: 1500–2099** (plus `n.d.`). This is the
envelope boundary for years, chosen to cover early-modern foundational
citations — (Machiavelli, 1532), (Hobbes, 1651), (Smith, 1776),
(Darwin, 1859) — while excluding antiquity-style years and the far future.
Years outside the range are not YEARs anywhere in this spec: not in
candidates, not in reference keys, not in the entry guard. The wider range
raises the §6.2 noise floor (e.g. `(1850 participants)` becomes an
unresolved candidate); that cost is accepted — visible noise over
invisible citations.

Notes. Comma before YEAR in SEG is mandatory. AUTHORS_NARR differs from
AUTHORS_PAREN: narrative comma lists must be `&`/`and`-terminated
(`Smith, Jones, and Brown (2020)` parses; `However, Smith` cannot parse as
two authors; parenthetical content is not prose, so AUTHORS_PAREN keeps
plain serial commas).

Narrative stoplist `STOP` (closed, via lower()): january…december, jan.,
feb., mar., apr., jun., jul., aug., sep., sept., oct., nov., dec., in, the,
a, an, see, since, during, early, late, as, at, on, after, before, table,
figure, section, chapter, equation, however, moreover, unlike, although,
while, whereas, thus, therefore, furthermore, additionally, finally,
similarly, likewise, consequently, meanwhile, nevertheless, nonetheless,
indeed, overall, importantly, notably, specifically, together, here, there,
this, these, those, using, given, despite, beyond, under, over, from, with,
within, without, across, toward, towards, per, via, following, like, first,
second, third, next, then, also, yet, still, both, when, where, because,
if, unless, until, once.

## 5. Sentence segmentation (canonical spans, body only)

Hard boundaries: heading lines (h1–h6) and blank lines (`^[ \t]*$`)
terminate any open sentence; heading lines belong to no sentence.

Within a paragraph, `[.?!]` at offset t is a terminator iff followed by
`CLOSERS = [”"’')\]]*` and then (whitespace + `\p{Lu}`) or paragraph end,
**unless the guard holds**: let ctx = paragraph text up to and including t;
no split iff ctx ends with some G ∈ GUARD, or with `\p{Lu}.` (single
initial), where the code point immediately before the matched suffix is
paragraph start, whitespace, or one of `(`, `[`, `"`, `“`, `'`, `‘`.

GUARD (closed set): { et al., e.g., i.e., cf., vs., Dr., Prof., Mr., Mrs.,
Ms., St., Jr., Sr., no., No., p., pp., Vol., vol., Eq., Fig., Figs., Tab.,
ca., ed., eds., approx., U.S., U.K. }

Canonical span `[sentence_start, sentence_end)`: sentence_start = first
non-whitespace code point after the previous boundary; sentence_end = one
past the last CLOSER (terminated) or one past the last non-whitespace code
point (unterminated residue — still a sentence). `content_end` = offset of
the terminator character (terminated) or sentence_end (unterminated).
`sentence` = the span verbatim.

Known limitation: guards can wrongly join a true sentence end; unlisted
abbreviations can wrongly split.

## 6. Citation extraction

### 6.1 The candidate envelope

The envelope — the region within which nothing citation-like can be
silently dropped — is defined by C1 and C2. Scan body left to right.

- **C1**: every maximal `\([^()]*\)` span whose content contains a YEAR
  match (nested parentheses: innermost only). Round parentheses only;
  supported years only (§4 range).
- **C2 token run**: walking right-to-left from the C1 span, collect
  whitespace-separated tokens while each is *eligible*, at most 6, and
  never past the sentence boundary: every collected token must start at
  offset ≥ sentence_start of the sentence containing the C1 span (a
  trailing token of the previous sentence, e.g. `USA.`, can never enter
  the run). Eligibility (after stripping at most one trailing comma,
  retained in the span text): the token matches `\p{Lu}[\p{L}\p{M}'’.-]*`
  or lower(token) ∈ { et, al., and, & } ∪ PARTICLE. Candidate span = run +
  C1 if the run is non-empty, else C1.

Citation-like forms **outside** the envelope are invisible by declaration,
not flagged — see §11 for the list.

### 6.2 Parse or fail loud (full-match semantics)

1. **Parenthetical**: CITE_PAREN must consume the entire C1 span. If it
   parses but any SEG's first-author CORE is all-caps (≥ 2 code points,
   all `\p{Lu}`) → `unresolved_citation`, reason `all_caps_surname`
   (`(OECD, 2024)` is asserted for no one). Otherwise → parenthetical
   group.
2. **Narrative, longest admissible suffix**: with run tokens t₁…tₖ, let L*
   = the largest L such that tₖ₋L₊₁…tₖ plus the C1 span, as one contiguous
   span, is entirely consumed by CITE_NARR. If no L parses → step 3.
   **Discard constraint**: every discarded token t₁…tₖ₋L* must be
   *discardable* — lower(token minus one trailing `[,;:]`) ∈ STOP, or the
   token ends with `[,;:]`. Any non-discardable discarded token →
   `unresolved_citation`, reason `no_grammar_match`, over the **candidate
   span** — so `World Bank (2024)` does NOT degrade to `bank|2024`, and
   `European Commission (2023)` stays whole and unresolved, while
   `However, Smith (2020)`, `In Smith (2020)`, and `Curiously, Smith
   (2020)` discard legitimately and parse as `smith|2020` with
   `group_start` at "Smith". If the accepted parse's first CORE is
   all-caps → `all_caps_surname` (`OECD (2024)`, `UNESCO (2023)`); else if
   lower(first CORE) ∈ STOP → `stopword_surname` (`May (2020)`). For both
   post-parse rejections, `text`/`start`/`end` = the **accepted parse
   span** (`In May (2020)` → text `May (2020)`); for `no_grammar_match`,
   the **candidate span**. All-caps takes precedence over stopword.
3. Else → `unresolved_citation`, reason `no_grammar_match`, text = the
   candidate span verbatim.

Reasons enum (closed): `no_grammar_match` | `stopword_surname` |
`all_caps_surname`. Unresolved-citation records carry `sentence`,
`sentence_start`, and section fields. Expected noise (by design): bare
`(2019)` or `(1859)`, `(May 2020)`, `(Smith 2020)` comma-less, forename-
first forms `(Adam Smith, 1776)`, dual original/reprint dates
`(Marx, 1867/1990)`, quantity parentheticals admitted by the wider year
range `(1850 participants)`, multi-word and all-caps institutional
authors. Residual risk (documented): a single-token, mixed-case
institutional name (`Eurostat (2024)`) is deterministically
indistinguishable from a surname and will parse.

### 6.3 Occurrences

One occurrence per SEG per YEAR (`(Ahnert & Fink, 2008; Bartko, 1976)` →
2; `Smith et al. (2020, 2021)` → 2). Fields:

- `citation_group` verbatim, `[group_start, group_end)`; narrative groups
  include the accepted token suffix.
- `citation_segment` verbatim, `[segment_start, segment_end)` (narrative:
  = group).
- `surname` = lower(full SURNAME of the segment's first author, whitespace
  collapsed to one space), particles included (`van der maas`).
- `year` = YEAR token normalized (`n.d.` → `nd`; suffix kept).
- `citation_key` = `surname + "|" + year`.
- `style` = parenthetical | narrative.
- `sentence`, `sentence_start`, `sentence_position` from the **group**
  span: `start` iff group_start = sentence_start; `end` iff group_end =
  content_end; else `middle`. Positional only.
- section fields per §3.4.

## 7. Reference assembly

Each section line is trimmed of leading/trailing `[ \t]` before all tests
and joins. Entry span: start = offset of the first non-`[ \t]` code point
of its first line; end = one past the last non-`[ \t]` code point of its
last line (covers the verbatim region, interior breaks included). At most
one entry is open:

1. Blank line → close the open entry.
2. Heading line (h1–h6) → close; excluded from assembly (`### Books` can
   never be joined into an entry).
3. Trimmed line matches ENTRY_START → close; open a new entry.
4. Else **entry-candidate**: after skipping leading particles the first
   code point is `\p{Lu}`, AND ( `\((?:(?:1[5-9]|20)\d{2}|n\.d\.)` occurs
   in the first 100 code points OR the trimmed line matches
   `^[^.\n]{2,60}\.[ \t]+\(?(?:(?:1[5-9]|20)\d{2}|n\.d\.)` ) → close the
   open entry; whole line → `unresolved_reference`, reason
   `entry_start_grammar`. Stops out-of-grammar forms — `World Bank.
   (2024).`, `Smith, John. (2020).`, `World Health Organization. (n.d.).`,
   `Royal Society. (1887).` — from wrap-joining into the preceding valid
   entry (the guard's year pattern uses the same 1500–2099 range as §4). A
   legitimate journal-name wrap line may occasionally divert: visible,
   chosen over silent corruption.
5. Else non-blank → append to the open entry, joined with one space; none
   open → `unresolved_reference`, reason `orphan_line`.

Section end closes the open entry. For both `unresolved_reference`
reasons, `text` = the **trimmed** line and `[start, end)` = the trimmed
region of that line.

Per entry: `assembled` = the joined text — explicitly NOT verbatim (joins
insert one space); the verbatim region is recoverable from the entry span.
`surname` = lower(particles + CORE from ENTRY_START, single-spaced).
`year` = first YEAR in `assembled` (`n.d.` → `nd`) — under the §4 range,
`Darwin, C. (1859). …` keys `darwin|1859` instead of degrading to a
`no_year` null key; if no YEAR, `year` and `reference_key` are `null` and
the entry takes no part in §8. Else `reference_key` =
`surname + "|" + year`.

`validation_state` = `ok` | `suspect`; reasons, in **this fixed order**
when several apply (structural plausibility, not validity; all tests on
`assembled`):

1. `no_year` — no YEAR token.
2. `terminator` — fails the end-anchored test
   `(?:\.|\?|\d+[–—-]\d+\.?|(?:doi:|https?://)\S+)$`.
3. `overlong` — length > 1500 code points.
4. `embedded_entry_pattern` — matches
   `\. (?:PARTICLE )*\p{Lu}[\p{L}\p{M}'’-]+, (?:\p{Lu}\. ?)+` at offset >
   10 (tripwire for merges and column-interleaved input).

Suspect entries with a key are still reconciled.

## 8. Reconciliation (normative order; keyed references only)

1. `cite_keys` = unique occurrence keys, first-occurrence order.
2. `dup_keys` = keys held by ≥ 2 keyed references → one
   `duplicate_reference_key` record per key (member indices ascending,
   `cited` = whether any citation key equals it). These entries take no
   part in steps 3–7.
3. `matched_work_keys` = keys in cite_keys held by exactly one reference;
   `matched_occurrences` = count of occurrences with key ∈
   matched_work_keys; `matched_works` = |matched_work_keys|.
4. `ambiguous_citation` = cite_keys ∩ dup_keys. Neither matched nor
   missing.
5. `missing_reference` = remaining cite_keys, first-occurrence order.
6. `uncited_reference` = unique-key references with key ∉ cite_keys,
   source order.
7. `possible_mismatch` over leftovers only (missing × uncited): scan
   missing keys in order; per key scan uncited entries in source order;
   pair on the first rule hit, removing both from their buckets (each item
   pairs at most once):
   - `surname_edit_distance_1`: years equal AND osa(surnames) ≤ 1 AND
     citation CORE length ≥ 4.
   - `year_adjacent`: surnames equal, both years numeric, |y₁ − y₂| = 1.
   - `year_transposition`: surnames equal, both numeric, y₂ = y₁ with one
     adjacent digit pair swapped, y₁ ≠ y₂ (2012↔2021, 1989↔1998,
     1859↔1895; excludes 2020↔2029, 1997↔2024). Rules apply uniformly
     across the full 1500–2099 range.
8. Exit 0 iff missing_reference, uncited_reference, possible_mismatch,
   duplicate_reference_key, ambiguous_citation, unresolved_citation,
   unresolved_reference are all empty AND every reference is `ok`; else 1.

## 9. Output contract (JSONL on stdout, nothing else)

Canonical serialization: one JSON object per line; keys exactly in the
order shown; separators `,` and `:` with no spaces; non-ASCII raw;
mandatory escapes only (`\"` `\\` `\n` `\r` `\t`, other C0 as `\u00xx`
lowercase); integers only; `null` literal for null keys.

`index` is per record type, 0-based, in emission order, and is the stable
id for that type; `reference_index`/`reference_indices` always refer to
`index` values of the `reference` block.

Blocks in this order, homogeneous, no interleaving; empty blocks emit
nothing:

```
 1 {"type":"meta","spec_version":"3.3"}
 2 {"type":"citation","index":0,"citation_group":"…","citation_segment":"…","citation_key":"…","surname":"…","year":"…","style":"…","group_start":0,"group_end":0,"segment_start":0,"segment_end":0,"sentence":"…","sentence_start":0,"sentence_position":"…","section_level":"…","section_name":"…","section_type":"…","section_roles":[]}
 3 {"type":"unresolved_citation","index":0,"text":"…","start":0,"end":0,"reason":"…","sentence":"…","sentence_start":0,"section_level":"…","section_name":"…"}
 4 {"type":"reference","index":0,"assembled":"…","reference_key":null,"surname":"…","year":null,"start":0,"end":0,"validation_state":"…","suspect_reasons":[]}
 5 {"type":"unresolved_reference","index":0,"text":"…","start":0,"end":0,"reason":"…"}
 6 {"type":"missing_reference","citation_key":"…","example":"…","occurrences":0}
 7 {"type":"uncited_reference","reference_index":0,"reference_key":"…"}
 8 {"type":"duplicate_reference_key","reference_key":"…","reference_indices":[],"cited":false}
 9 {"type":"ambiguous_citation","citation_key":"…","example":"…","reference_indices":[]}
10 {"type":"possible_mismatch","citation_key":"…","reference_index":0,"reference_key":"…","evidence":"…"}
11 {"type":"summary","matched_occurrences":0,"matched_works":0,"exit":0}
```

Field semantics (normative):

- `section_level` ∈ { `"h2"`, `"h3"`, `"h4"`, `"none"` } — the only
  permitted serialized values, in blocks 2 and 3 alike.
- `example` (blocks 6 and 9) = the `citation_segment` of the **first**
  occurrence bearing that `citation_key`.
- `occurrences` (block 6) = the number of block-2 `citation` records with
  that `citation_key`.
- Blocks 6 and 7 contain the **post-pairing residuals** of §8 step 7;
  every item consumed by `possible_mismatch` appears only in block 10.
- `suspect_reasons` (block 4) in the fixed §7 order.
- Block orders: 2 by (group_start, segment_start); 3 by start; 4 and 5 by
  source position; 6 first-occurrence order; 7 source order; 8 ascending
  by smallest member `reference_index` (indices ascending within); 9
  first-occurrence order of the citation key; 10 pairing order; 11 always
  last.

## 10. Aborts and exit codes

Sequence: 5 (UTF-8) → 4 (heading contract) → 3 (references section) →
extraction → 2 (style) → assembly → reconciliation → 0/1.

Exit 2 (unsupported citation style): N = NUMCITE matches + SUPCITE runs in
body, P = parsed citation occurrences; abort iff **N ≥ 3 AND N > 10 × P**.

On exit 2–5, stdout is exactly two lines:

```
{"type":"meta","spec_version":"3.3"}
{"type":"error","code":2,"reason":"unsupported citation style"}
```

Reasons: 2 `unsupported citation style`, 3 `references section not found`,
4 `heading contract violated`, 5 `invalid utf-8`. stderr non-normative.

## 11. Out of envelope and documented limitations

**Out of envelope — invisible by declaration** (not flagged, not counted):
square-bracket author–year forms (`[Smith, 2020]`); author–year without
parentheses ("as Smith 2020 argued"); years outside 1500–2099 (`(Cicero,
44 BC)`, `(Smith, 1499)`); footnote- and superscript-marker citation
styles beyond the exit-2 detector's reach. Extending the envelope is a
versioned spec change, never an implementation choice.

**In envelope, limited by design**: multi-word and all-caps institutional
authors, comma-less citations, forename-first parentheticals, and
full-first-name reference styles surface as unresolved, not parsed. A
single-token mixed-case institutional name (`Eurostat (2024)`) is
deterministically indistinguishable from a surname and will parse — the
one knowing false-positive class in the grammar. A capitalized non-name
word outside STOP directly before `(YEAR)` can yield a false narrative
parse only when no token must be discarded; §12 adversarial goldens police
STOP. Setext and multi-line or inline HTML headings are plain text.
Column-interleaved PDF extraction is out of scope — fix upstream;
`embedded_entry_pattern` is a tripwire, not a repair. The sentence
splitter is a closed-guard approximation. Bare-year and quantity
parentheticals produce unresolved noise. The entry-candidate guard may
divert an occasional legitimate wrap line.

## 12. Conformance suite (golden files, byte-compared)

| class | must cover |
|-------|-----------|
| headings | h2→h3→h4 stack, siblings, ignored h1/h5/h6, exit 4 boundary (2×h1+0×h2 aborts; 2×h1+1×h2 passes), numbering strip, `## C#` keeps `#`, inline `<h2>…</h2>` not a heading |
| typing | inherited Methods, "Results and Discussion" roles, "Resulting…" non-match, unknown → other |
| parenthetical | 1 author, 2 authors, serial list, et al., multi-segment, multi-year, prefix `e.g.,`, locator `p. 14`, full-span consumption (trailing junk → unresolved) |
| narrative | 1 author, `&`/`and`, and-terminated serial list, et al., multi-year, particle surnames (`van der Maas (2022)` → `van der maas\|2022`) |
| historical & envelope | `(Darwin, 1859)` → `darwin\|1859`; `Smith (1890)` → `smith\|1890`; `(Machiavelli, 1532)` parses; boundary pair `(Smith, 1500)` parses vs `(Smith, 1499)` invisible (out of envelope); `(Adam Smith, 1776)` → unresolved no_grammar_match (in envelope, forename-first); `(Marx, 1867/1990)` → unresolved; `[Smith, 2020]` produces no record of any kind; Darwin 1859 reference keys `darwin\|1859` (not `no_year`) and matches |
| adversarial narrative | `However, Smith (2020)` / `In Smith (2020)` / `See Smith (2020)` / `Unlike Smith (2020)` / `Curiously, Smith (2020)` → `smith\|2020`, group at "Smith"; `Following (2019)` → stopword_surname; non-STOP capitalized word + `(YEAR)` documented-risk case |
| institutional | `World Bank (2024)` → no_grammar_match over the full candidate (NOT `bank\|2024`); `European Commission (2023)` → no_grammar_match; `OECD (2024)`, `UNESCO (2023)` → all_caps_surname; `(OECD, 2024)` → all_caps_surname; `Eurostat (2024)` documented false-positive golden |
| C2 boundary | previous sentence ending `…USA.` directly before `Smith (2020)` → run bounded at sentence_start, parses `smith\|2020` |
| unicode | García, Müller, de Vries in citations AND entries |
| unresolved_citation | `(May 2020)`, `(Smith 2020)`, bare `(2019)`, `(1850 participants)` noise golden; span goldens: `In May (2020)` → stopword_surname with text exactly `May (2020)` vs `World Bank (2024)` text = candidate span; records carry sentence + section |
| sentences | start/middle/end, group-based position, `.” Next` split, `et al.` guard mid-sentence, heading and blank-line boundaries |
| offsets | half-open goldens: terminated sentence (content_end = terminator offset; final citation's group_end = content_end) vs unterminated residue (content_end = sentence_end) |
| assembly | single line, wrapped Abadie, `### Books` exclusion, blank-line closure, orphan preamble (trimmed text + trimmed-span offsets), particle ENTRY_START, line-trim before tests |
| entry guard | `World Bank. (2024).` diverted; `World Health Organization. (n.d.).` immediately after an open valid entry → diverted, prior entry intact; `Royal Society. (1887).` diverted under the widened year range; legitimate journal-name wrap divert (documented cost) |
| plausibility | DOI ending ok (end-anchored), `(n.d.)` ok, overlong, embedded_entry_pattern; multi-reason entry → suspect_reasons in §7 order; no-year entry → `reference_key:null`, absent from §8, two year-less entries produce no duplicate diagnostics |
| reconciliation | occurrence vs works counts (3 occurrences, 1 work), repeated citations 1× vs 10×, missing, uncited; blocks 6/7 verified as post-pairing residuals |
| collisions | two `Smith 2020` refs → duplicate_reference_key + ambiguous_citation (record orders per §9); 2020a/2020b resolving cleanly |
| possible_mismatch | Barko/Bartko, 2020↔2021, 2012↔2021, 1859↔1895 transposition, 2020↔2029 and 1997↔2024 non-pairs, Kim/Kin exclusion |
| aborts | numeric `[1,2]`/`[1–4]`, superscripts, ratio boundary (N=40,P=1 aborts; N=3,P=60 does not), missing References, invalid UTF-8 |
| serialization | quotes/pipes/newlines in sentences, non-ASCII passthrough, `null` keys, per-type index stability, section_level enum, block 8/9 ordering, final LF, empty blocks |
