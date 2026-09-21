# Citation v3.4 rc3 — amendment set over rc2

31 August 2026. Amends the four-file rc2 package. Every rule here was settled in
#citation between 29 and 31 August and, until now, existed only in that channel.

**Two of these are already measured, not projected.** The rest carry the corpus
count each is worth, so nothing in this document is an estimate dressed as a
requirement.

```text
corpus       9 in-profile reconciling papers, 14-paper export
baseline     1502 / 1611  =  93.2%   after \& + rc2-B4 segment splitting
                                     + rc3-B3 colon locator + rc3-B4 cp.
residual     109, fully classified, zero unclassified
```

---

## A. Output contract — the change that makes the rest measurable

### A1. `candidate_state` — three terminal states, not two

rc2 emits every unresolved candidate as `unresolved_citation` with
`no_grammar_match`. A mathpix image URL and a genuinely missed citation are
byte-identical in the record.

> **Every detected candidate MUST terminate in exactly one of:**
>
> ```text
> candidate_state ∈ {
>     parsed,
>     unresolved_citation,     a citation-like span the parser could not read
>     excluded_candidate       a span the parser CORRECTLY refused
> }
> ```

`excluded_candidate` is **not a failure**. It records that detection proposed a
span and the grammar was right to decline it.

### A2. `excluded_reason` — CLOSED

```text
excluded_reason ∈ {
    leading_gloss,          11
    url_or_image,            8
    publisher_metadata,      4
    math_expression,         3
    conversion_artifact,     3
    non_citation_year        1
}                           30
```

**`bare_locator` is NOT in this set.** `(Barbier, 2022; P.923)` is an author
error — a semicolon where APA wants a comma — and belongs to the diagnostic class
in §C, not to correct refusal. Including it would double-count those two.

### A3. The completeness invariant

> **Every detected candidate terminates as parsed, unresolved, or correctly
> excluded. Nothing disappears silently, and nothing is silently miscounted.**

The first half already held in rc2. The second did not, and is what A1 buys.

### A4. Candidate lifecycle — ONE model

An earlier draft described exclusion three different ways: as a terminal state in
§A, as preventing candidacy in §B10, and as "no candidate" in §E. Only one can be
true, and the 30-item accounting only reproduces under the first.

```text
raw detection
    │
    ▼
candidate                          every proposed span is a candidate
    │
    ▼
exclusion classification
    ├── excluded_candidate         terminal. Correct refusal.
    └── eligible citation candidate
            ├── parsed
            └── unresolved_citation
```

**Exclusion classifies a candidate; it does not prevent one.** Envelope rules
(§E) and exclusion-span rules (§B10) both terminate spans here, with the reason
recording which.

### A5. Denominator — normative

```text
detected_candidates      = parsed + unresolved + excluded
extraction_denominator   = parsed + unresolved        EXCLUDES excluded_candidate

candidate_parse_rate     = parsed / extraction_denominator
```

> **`candidate_parse_rate` is NOT accuracy.** It measures how much of what the
> detector proposed the parser could read. It says nothing about detection
> recall, and a parser can successfully parse an incorrect span.
>
> **Extraction accuracy, precision and recall MUST NOT be reported until a gold
> set exists.** Naming a parse rate "accuracy" is the same defect this whole
> milestone is about: a number that cannot come back false.

```text
CURRENTLY MEASURED — observed parser behaviour
all detected                     1502 / 1611  =  93.2%
excluding the classified 30      1502 / 1581  =  95.0%

COUNTED CONSEQUENCE — if B5 and B6 recover all 19 registered cases
with zero regressions. NOT MEASURED; neither is implemented.
                                 1521 / 1581  =  96.2%
```

An earlier draft put all three under one "Measured" heading. B5 and B6 are
unimplemented, and this document opens by promising not to dress projection as
measurement.

**A rate over all detected candidates measures detection granularity as much as
parser resolution.** rc2-B4's segment splitting demonstrated this: one failed parenthesis
becomes several failed segments, and `43338825` gained 5 citations while its rate
fell. Absolute counts are stable across such changes; rates are not.

The classification behind the 30 is a heuristic pass, so even the parse rate
carries an unverified exclusion set. The gold set is the highest-value remaining
item and nothing above substitutes for it.

---

## B. Grammar amendments

### B1. Author phrase — bound the production, NEVER the span

**Split into two productions.** An earlier draft used one and claimed it covered
all 17 cases. It does not — see B1b.

**Do not reintroduce a token cap.** C2 removed the six-token cap for a reason and
the corpus still contains the case that removed it:

```text
Van den Brink and Van der Woerd        7 tokens   present twice
Dalal, Lam, Weiss, Welch, & Hulin      6 tokens   at the boundary
```

One more author on the second and a 6-token cap breaks it too. Meanwhile every
form the widening is *for* is short:

```text
International Monetary Fund     3
Carrieri de Souza               3
El Akremi                       2
Pircher Verdorfer               2
```

#### B1a. `SURNAME` — personal, two cores. Worth 9

> ```text
> SURNAME = (PARTICLE WS)* CORE (WS (PARTICLE WS)? CORE)?
> ```
>
> The candidate run stays bounded by §6.1 eligibility and the sentence boundary,
> exactly as C2 left it.

```text
Carrieri de Souza     CORE particle CORE      ✓
El Akremi             CORE CORE               ✓
Pircher Verdorfer     CORE CORE               ✓
Oliveira da Silva     CORE particle CORE      ✓
```

#### B1b. `NON_PERSON_AUTHOR` — citation side. Worth 8

**B1a cannot reach the institutional cases and an earlier draft claimed it
could.** The production admits at most two `CORE` elements:

```text
International Monetary Fund     3 cores   ✗
National Statistical Institute  3 cores   ✗
University of Pretoria          "of" is not in PARTICLES   ✗
```

Getting them from `SURNAME` would mean classifying ordinary nouns as particles,
which is wrong twice over — it corrupts the person grammar to reach organisations.

> **The citation-side `NON_PERSON_AUTHOR` path MUST reuse the exact lexical
> production and boundary rules rc2 defines for the bibliography-side
> `NON_PERSON_AUTHOR`. rc3 changes the permitted DETECTION SITE only. It does not
> introduce a second organisational-author grammar.**
>
> The candidate is emitted as `non_person_author_candidate`. Identity is settled
> in Pass 2 by reconciliation, exactly as rc2 specifies.

**Two grammars for one object is how the boundaries drift.** rc2's production
already carries the bound, the terminal-period handling and the maximum label
length; restating them here would create a second definition that can disagree
with the first. An earlier draft said "add a bounded path" without naming the
production, which two implementations could satisfy while producing different
candidate boundaries.

**Personal surnames and organisational authors are different grammatical
objects**, even where they share part of the detection path. Merging them was an
attempt at elegance that broke the coverage claim.

**Safety is rc2's argument, not a new one.** Widening previously risked
`World Bank → bank|2024`. Under two-pass, Pass 1 assigns no identity, so the
complete phrase reaches reconciliation and `NON_PERSON_AUTHOR` classifies it
there.

The span-length point stands unchanged: **no global token cap**, whichever
production is doing the work.

### B2. Lowercase core after a particle. Worth 1

**An earlier draft said "make particle matching case-insensitive". That is a
no-op** — the implementation already applies `(?i:…)` to `PARTICLE`, so `Da`
matches as a particle today. Verified against the source, not assumed.

The real blocker is `CORE`:

```text
CORE = \p{Lu} NAMECHAR+          requires an initial capital
Da silva  →  Da matches PARTICLE, silva fails CORE
```

> **Permit a lowercase core ONLY immediately after a matched `PARTICLE`.**

The restriction is what keeps it safe. Relaxing `CORE`'s capital requirement
generally would admit ordinary prose into the candidate run, which is the hazard
§6.1's eligibility test exists to prevent.

### B3. `LOCATOR` — colon branch. MEASURED, +28

House style in two journals, and the largest single class in the residual.

```python
LOCATOR = r'(?:(?:,' + WSO + r'(?:p\.|pp\.|para\.|chap\.)|:)' + WSO + r'\d[^();]*)'
```

**The digit is load-bearing.** It is the whole discriminator between a locator
and the wrong-separator error:

```text
(Proudfoot & Kay, 2014: 176)              locator      digit follows
(da Silva et al., 2024: Wezel et al.…)    separator    capital follows
```

Measured on the nine papers: **+28, zero regressions, zero previously-parsed keys
changed, denominator unmoved.** All 28 came from papers absent from the 11-file
corpus, which is why no earlier pass saw the class at all.

### B4. `PREFIX` — add `cp.`. MEASURED, +5

```python
PREFIX = r'(?:(?:e\.g\.|i\.e\.|cf\.|cp\.|see also|see|but see)[, ]' + WSO + r')'
```

One token in a closed set. All five occurrences are in one paper, and all five
recovered, including the bare non-parenthesised `cp. Weiner, 1986`.

House-style rather than general APA, which is an argument for expecting further
cues like it on unseen papers — not for opening the set.

### B5. Bounded lead-in cue. Worth 17

Already specified in rc2 and unimplemented. The observed cues cluster tightly:

```text
see · see also · see for example · for an overview · for a review ·
for a recent review · for a meta-analysis · for a critique · for critiques ·
for a similar approach · for comparative examples · for details
```

> **`LEAD_IN ","? CUE CITATION_LIST` with `CUE` a CLOSED set.** A bounded
> *trailing* form is also required — `(see X, 2013, for a critique)` — where the
> cue follows the citation.

### B6. Compact year-suffix. Worth 2

```text
2019a,b   →   2019a + 2019b
BASE_YEAR SUFFIX ("," SUFFIX)+
```

Deterministic expansion. **Do not generalise to arbitrary year inference.**

### B7. `and colleagues`. Worth 4

```text
Jost and colleagues (2003a)
Colquitt and colleagues (2012)
Dalal and colleagues (2009)
```

A closed two-token construction equivalent to `et al.` The cheapest change in
this document after `cp.`

### B8. Possessive narrative, with a bounded gap. Worth 7

rc2 specifies the simple form. New here is a noun between author and year:

```text
Fine's (1998)                          simple, rc2 covers it
Mackey et al.'s (2017) meta-analysis   simple
Martinko et al.'s review (2013)        intervening noun
Harter's definition of authenticity (2002)   intervening noun phrase
```

> **`NARRATIVE_POSSESSIVE_NORMALIZATION` MUST tolerate at most
> `MAX_POSSESSIVE_YEAR_GAP_TOKENS = 3` intervening tokens between the possessive
> author and `(YEAR)`.**
>
> **The gap TERMINATES at**, and does not cross: a sentence boundary, a comma or
> semicolon, an opening or closing parenthesis, or any other citation candidate.

Three is the longest gap observed — `Harter's definition of authenticity (2002)`
— so the bound sits exactly at the measured maximum. That is deliberate and it is
also the weak point: one unseen paper with a four-token gap fails. Raising it
trades that against overcapture, and the number should move only on evidence.

**This bound is legitimate where B1's was not.** It limits a *gap* between two
anchored elements, not the length of the author expression. The C2 argument does
not apply.

### B9. Segment-split orphan. Worth 1

```text
Brees et al. (2016; see also Martinko et al., 2013)
```

An ordinary narrative citation broken apart by rc2-B4's own splitting.

An earlier draft said "implement only if regression-safe", which is a development
instruction, not something conformance can test.

> **The B9 branch MUST recover the registered orphan case, and MUST produce zero
> change to the parsed citation-key multiset across every other conformance and
> corpus case.**

If that invariant cannot be met, B9 is **registered and deferred**, not
normative. It is our own change causing the defect, and the repair must not
reopen what rc2-B4 closed.

### B10. `rc2-A3` is an EXCLUSION, not a recovery. Worth 11 off the denominator

A3 **does not recover a citation.** A detected span matching an exclusion rule
terminates as `excluded_candidate`; it never becomes an eligible citation
candidate, and it cannot add to the numerator.

An earlier draft said A3 "prevents spans becoming candidates". That contradicted
§A, where the same 11 instances are counted as `excluded_candidate` removals — if
they were never candidates the accounting could not be reproduced from the output
contract. One lifecycle, stated in §A4.

```text
url_or_image        8
math_expression     3
```

An earlier residual counted these as pending recoveries and added them to the
numerator. Wrong mechanism, and it hid 11 false positives inside a list of fixes.

**One collision to avoid.** Blanket math-span exclusion would delete three real
citations — `Baron $(2012,2016)$` and `Shepherd and Kay $(2012,2014)$`, where
Mathpix wrapped an ordinary parenthetical in math mode. Those require D2's pre-canonicalisation unwrapping, not exclusion. They belong
to the same upstream transformation class as `\&`, but are governed by a
different rule.

---

## C. Citation errors — a diagnostic class, not a limitation

**19 cases, 20 defect instances.** One case carries two defects; the counts are
not interchangeable and an earlier draft used them as though they were.

```text
DEFECT INSTANCES
et-al punctuation           9    Whiteman et al, 2013 · Choi at al., 2001
wrong separator             4    (Bisht, 2019, Speich) · ':' for ';'
missing comma before year   2    (Lu and Shang 2017)
bare locator                2    (Barbier, 2022; P.923)
non-numeric year            1    (Smith, Weed, & Ramsay, 2005-present)
prose-embedded citation     1
incomplete citation         1    Carrieri Souza — no year in the sentence
                           20

CASES                      19    one case, (Gualandris, et al., 2024; p.56),
                                 carries two of the above
```

§I counts **19**, because it partitions cases.

> **`citation_error` is ORTHOGONAL to `candidate_state`.** A malformed group MAY
> be `parsed` or `unresolved_citation`, depending on whether a valid citation was
> extracted from it. It MUST NOT be `excluded_candidate` — malformed input is not
> correct refusal. All such cases remain in `extraction_denominator`.
>
> **The grammar MUST NOT be loosened to accept these forms.** The record names
> what is wrong so an author can fix it.

```text
(Gualandris, et al., 2024; p.56)
    candidate_state   = unresolved_citation
    diagnostic_class  = citation_error
    defects           = [ et_al_punctuation, wrong_locator_separator ]

(Barbier, 2022; P.923)
    candidate_state   = parsed
    diagnostic_class  = citation_error
    defects           = [ wrong_locator_separator ]
```

An earlier draft said these "remain unparsed", which contradicted C1's own
Barbier case. Two axes, not one.

### C1. Errors attach to the PARENTHESIS, not the segment

This is the part a naive implementation gets wrong.

```text
(Gualandris, et al., 2024; p.56)
```

Two defects in one malformed citation. Emitted as two records, the author sees
two unrelated problems and fixes neither.

> **One `citation_error` record per parenthetical group, carrying a list of
> defects. NEVER one record per defect.**
>
> ```text
> candidate_state   = unresolved_citation
> diagnostic_class  = citation_error
> scope             = parenthetical_group
> defects           = [ et_al_punctuation, wrong_locator_separator ]
> ```

Contrast `(Barbier, 2022; P.923)`, where the citation parsed and only the locator
orphaned — one group, one defect, one record. Both shapes need a conformance
case, and the pair is what distinguishes a case count from a defect count.

### C2. `LOCATOR` already tolerates the spacing

`p.56` with no space matches, so the semicolon is the **sole locator defect** in
both cases — one character. In `(Gualandris, et al., 2024; p.56)` it is not the
sole defect: the et-al punctuation is independent of it.

`P.923` matches only because the pattern is applied case-insensitively. That
dependency is load-bearing and should be explicit in the rule rather than
inherited from a flag.

### C3. `X-07` has lost its evidence

X-07 registers forename-first as a limitation. All four corpus instances turn out
to be publisher metadata (§E), not manuscript prose. The limitation may still be
right in principle; it now has **zero supporting occurrences** and the register
should say so rather than implying observation.

---

## D. Upstream conversion — before Citation sees the text

### D1. `\& → &` MUST precede canonicalisation

810 occurrences. Measured worth: **+621 citations** across nine papers, the
single largest defect in the pipeline.

```text
exclusion      does not change bytes    safe at any stage
substitution   changes bytes            every downstream offset shifts
```

810 substitutions, each one byte shorter. Applied after canonical bytes are
fixed, every citation offset is wrong and **nothing errors**.

> **A deterministic ingest transform before canonical bytes, hash and offsets
> exist. Rule id `ampersand_unescape_v1`.** Currently ad hoc; not yet a versioned
> ingest rule.

### D2. Math-wrapped year parentheticals. Worth 3

```text
Baron $(2012,2016)$          author is right there, the $ blocks it
Shepherd and Kay $(2012,2014)$
```

Same family as `\&` — Mathpix wrapping an ordinary parenthetical in math mode.
Eight corpus-wide, three in the nine in-profile papers, four in `exit 3` papers
that will surface once `bibliography_absent` exists.

**Fix upstream, not by exclusion.** §B10's math exclusion would delete these.
They need D2's pre-canonicalisation unwrapping — the same upstream transformation
*class* as `\&`, not the same rule.

> **Rule id `math_wrapped_year_parenthetical_unwrap_v1`. Ingest transform order
> is FIXED:**
>
> ```text
> 1  ampersand_unescape_v1
> 2  math_wrapped_year_parenthetical_unwrap_v1
> 3  canonicalisation
> 4  canonical hash
> 5  offset assignment
> ```
>
> The two transforms are independent — a year-only span contains no ampersand, so
> neither changes whether the other matches. The order is fixed anyway, because
> two orders that happen to agree today are still two orders.
>
> ```text
> MATCH      $ ( YEAR_LIST ) $
>            where YEAR_LIST satisfies the citation year-list grammar in full,
>            and the math span contains NOTHING else
> CONTEXT    an eligible narrative author expression immediately precedes it
> ACTION     strip the enclosing $ delimiters. Nothing inside is altered.
> NEGATIVE   $(2012,2016) + x$      → no match, span is not year-only
>            $\alpha=0.96$          → no match
>            standalone $(2014)$ with no preceding author  → no match
> ```

Without the year-only and author-context restrictions, "fix upstream" leaves the
implementer to decide which math spans are citations, which is the discretion the
rule exists to remove.

---

## E. Envelope — publisher metadata is out

```text
849f8fc6   front matter           "To cite this article: …"
849f8fc6   Citation information   "Cogent Business & Management (2023), 10: 2275370"
ea07e5f5   front matter
ea07e5f5   Citation information
```

Not manuscript in-text citations. Publisher-generated metadata.

> **Sections identified as `front matter` or `Citation information` are OUT of
> the in-text citation envelope.**

**No new detection is required** — the section map already labels both by name.
This is an envelope decision, not a recognition problem. Worth 4, and it empties
the forename-first class entirely.

Spans in those sections terminate as `excluded_candidate / publisher_metadata`
per §A4. An earlier draft said "no candidate", which contradicted the accounting
that counts these four among the 30.

---

## F. Failure taxonomy — replaces `bare_year`

Sixteen cases were classified `bare_year`. **Fifteen are real citations** whose
author expression sits in the surrounding sentence; the detector saw the year and
failed to associate it.

```text
narrative_citation_boundary_failure                                 15
├─ possessive_author                         4   Mackey et al.'s (2017)
│                                                El Akremi et al.'s (2015) scale
│                                                Scott et al.'s (2014) ×2
├─ possessive_author_with_intervening_noun   2   Martinko et al.'s review (2013)
│                                                Harter's definition of … (2002)
├─ author_and_colleagues                     4   Jost ×2, Colquitt, Dalal
├─ math_wrapped_year                         3   Baron ×2, Shepherd and Kay
├─ segment_split_orphan                      1   Brees et al. (2016; see also …)
└─ malformed_author_form                     1   Fremout et al (2022)   → §C

non_citation_year                            1   "three consecutive
                                                  (2011, 2012, and 2013)"
                                            ───
former bare_year total                       16   ✓
```

**These counts are of the original 16 only**, which is where an earlier draft
became unverifiable. §I's totals differ because they carry cases from elsewhere
in the residual:

```text
B8 possessive        7  =  6 here  +  1 pre-existing (and Fotiadis's (2018))
B7 and colleagues    4  =  4 here
D2 math wrapped      3  =  3 here
B9 segment orphan    1  =  1 here
§C malformed et-al   1 of the 20 defect instances
```

So the subtype table partitions the 16, and §I partitions the 109. Both are
mechanically checkable, and neither is a subset of the other.

**These 15 MUST NOT be removed from the denominator as false positives.** They
are missed extraction. The umbrella is for reporting; the six subtypes have three
different causes and three different fixes — grammar, upstream, and our own B4.

---

## G. Conformance

One case per changed behaviour. Two already have measured results rather than
expectations.

```text
B1a  Carrieri de Souza et al. (2023)      → person, compound surname
B1a  Van den Brink and Van der Woerd (2004) → MUST still parse, 7 tokens
B1b  International Monetary Fund, 2022    → non_person via reconciliation
B1b  National Statistical Institute, 2022 → 3 cores, MUST reach a candidate
B1b  World Bank (2024)                    → MUST NOT yield bank|2024
B2   (Da silva et al., 2017)              → parses
B2   ordinary lowercase prose             → MUST NOT enter the candidate run
B3   (Kunda, 1990: 480)                   → locator      MEASURED +28
B3   (da Silva et al., 2024: Wezel…)      → wrong separator, NOT locator
B4   (cp. Liu et al., 2012)               → parses       MEASURED +5
B4   cp. Weiner, 1986                     → bare form parses
B5   (see X, 2013, for a critique)        → trailing cue
B6   (Sharma et al., 2019a,b)             → 2019a + 2019b
B7   Jost and colleagues (2003a)          → jost|2003a
B8   Martinko et al.'s review (2013)      → martinko|2013
B10  mathpix cdn URL                      → excluded_candidate/url_or_image
C1   (Gualandris, et al., 2024; p.56)     → ONE error, two defects listed
C1   (Barbier, 2022; P.923)               → citation parses, one error
E    "To cite this article: …"            → excluded_candidate/publisher_metadata
F    three consecutive (2011, 2012, 2013) → excluded/non_citation_year
B8   possessive gap of 4 tokens           → MUST NOT parse, bound is 3
B9   registered orphan case               → recovered, key multiset otherwise
                                             UNCHANGED
D2   Baron $(2012,2016)$                  → unwrap → baron|2012 + baron|2016
D2   $(2012,2016) + x$                    → no unwrap, span not year-only
D2   standalone $(2014)$, no author       → no unwrap, no author context
A1   every corpus candidate               → exactly one terminal state
A4   excluded span                        → excluded_candidate, NOT absent
A5   summary                              → denominator excludes excluded_candidate
A5   summary                              → candidate_parse_rate only; MUST NOT
                                             report accuracy/precision/recall
```

---

## H. NOT in rc3

```text
coordinated "and"           6    "and" is already an author joiner inside
                                 AUTHORS_NARR, so the parser cannot separate
                                 two authors of one work from two citations.
                                 REGISTER, do not solve.
bibliography_absent         4 papers exit 3 and produce byte-identical
                                 nothing. Specified in rc2, unimplemented.
gold denominator            the highest-value remaining item, and the reason
                                 every rate above is indicative
no_grammar_match split      deferred. 192 citations were recovered without
                                 touching the reason enum.
annotation framework        deferred. Two fixes needed one substitution and
                                 one parser branch.
c22df19f                    ACL bracketed-key style, 0/121 references. A
                                 CORRECT refusal, out of apa7_like_v1. Name it
                                 in register §9 so it reads as a limitation
                                 rather than a catastrophe.
```

---

## I. What this is worth, counted

```text
ALREADY MEASURED
  B3  colon locator            +28
  B4  cp.                       +5
                               +33   →  93.2%

SPECIFIED AND AGREED
  B5  lead-in                  +17
  B6  compact year-suffix       +2
                               +19   →  96.2% on the corrected denominator

BOUNDED NEW GRAMMAR
  B1a surname production        +9
  B1b non_person citation path  +8
  B8  possessive                +7
  B7  and colleagues            +4
  B2  lowercase core after particle  +1
  B9  segment-split orphan      +1
                               +30

EXCLUSIONS — denominator, not numerator
  B10 url / image                8
  B10 math                       3
  E   publisher metadata         4
  F   non-citation year          1
  §A  leading gloss             11
  §A  conversion artifact        3
                                30

DIAGNOSTIC, NOT FIXED
  §C  citation errors           19   cases, 20 defect instances

UPSTREAM RECOVERY
  D2  math-wrapped year         +3

REGISTERED
  H   coordinated "and"          6
```

```text
19 + 30 + 19 + 30 + 6 + 3   =   107
long tail                         2
                              -----
                                109   ✓
```

An earlier draft omitted D2 and called 5 cases long tail. Three of those were
already classified as `math_wrapped_year`, so they could not also be unclassified
residue. §F's claim that §I partitions the 109 is now true.

---

## J. Provenance

```text
corpus        development database `paperly`, 14 rows, base64 export
runtime       python 3.10.12, regex 2026.7.19

MEASURED RUN TRANSFORM — what actually produced the figures above
  ampersand_unescape_v1        sed 's/\\&/\&/g'   ad hoc, not yet a
                               versioned ingest rule

RC3 REQUIRED INGEST TRANSFORMS — normative, and NOT yet implemented
  1  ampersand_unescape_v1
  2  math_wrapped_year_parenthetical_unwrap_v1

D2 has no measured result and no hash, because it has not been run.

impl_v34.py         50077031db923e2b80eb86add2cf1967afc8222de569fd6258b99dc8c0846628
impl_v35_both.py    03927c0ac4be04b0251adc991ac02d430f8fad46d8c09db5d3bda2a351bc685f
impl_v35_locator.py afb635ee7593019e1aa8769cdbc3833a8ea19c992fbd332afff0223d82263fb2
impl_v35_cp.py      e2337195ef3c1e8c57bf531db1101206200c83d3818e0dce0976fa8a7fed6de1
```

Per-paper raw, transformed and output hashes: `CITATION_RESIDUAL_142.md`.
Per-case listing of all 109 with sentence context: `CITATION_UNRESOLVED_109.md`.

---

**Governing-spec note — resolved 4 September 2026.**

> **This document is the governing amendment set for Citation v3.4 rc3. It
> amends the four-file rc2 package, and nothing else amends rc2. Freezing this
> document satisfies the specification dependency for the rc3 implementation
> work queued behind it: §I's SPECIFIED AND AGREED tier (B5, B6) and its
> BOUNDED NEW GRAMMAR tier (B1a, B1b, B2, B7, B8, B9).**

Recorded because Ingest Stage 1 hit the inverse problem. An earlier draft left
it ambiguous whether the artifact planning waited on was that file or a separate
unnamed one, which meant the document blocked its own freeze — the dependency
could not be satisfied because nobody could say what would satisfy it. Naming
the dependency here means the same question cannot be asked of rc3.

The frozen stamp is recorded in `CITATION_v3.4_rc3_FREEZE.md`. Any change to
this document requires a new revision and a new stamp. The frozen text is not
edited in place.
