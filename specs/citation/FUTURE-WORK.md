# Citation work deferred, by instruction

Everything here is work Alex Zamurko has ruled on and explicitly deferred. It
is collected in one file so that "later" has an address, rather than living in
three chat windows and a comment.

Nothing in this file is implemented. Each item records his words, what exists
today, and what it would take, so that picking one up does not start with
rediscovering the rule.

---

## 1. Reference-list confirmation

Deferred 6 October 2026: "Let's keep the reference list confirmation as a
future work. So, we can continue with other parts." Reaffirmed 7 October in the
`and` taxonomy, where it is the second-stage mechanism for every case surface
syntax cannot settle.

**What it is for**, in his words: ambiguous surname boundaries such as `Pircher
Verdorfer`; contaminated spans where the intended citation may still be
recoverable; institutional authors containing `and`; names and institutions
with identical surface structure; and malformed structures where direct parsing
cannot establish the full author span.

**What exists today.** The reference section is already assembled and parsed:
`assemble_references`, `reference_authors`, `reference_author_head`. The
citation side and the reference side are reconciled for identity, which is what
produces `missing_reference` and `uncited_reference`. What does not exist is
using the reference list to *decide a parse* rather than to check one.

**Explicitly not required** for ordinary cases: he is clear that `Smith and
Jones (2020)` must not be made to depend on downstream evidence.

---

## 2. The `and` cases he classed Low

From the taxonomy of 7 October 2026, with his instruction to resolve the High
and Medium cases and record the Low ones here. Measured against the code on
7 October, not assumed:

    case 8    `??? Seuring and Müller (2008)` produces `seuring|2008`
              where he requires unresolved. The serial-author grammar
              accepts `Seuring and Müller` as a two-author list, so the
              contamination to its left is never consulted.

    case 11   `Johnson and Johnson (2020)` parses as two authors where he
              wants reference-list confirmation of person versus institution.

    cases 9   and 10 land on unresolved, which is his stated fallback when
              reference-list confirmation is unavailable. They become correct
              rather than merely safe once item 1 exists.

---

## 3. Non-year publication-status values

Alex Zamurko, 7 October 2026, asked for as future work. Quoted in full:

    Rule: Non-year publication-status values

    Where the citation grammar normally expects a publication year, it may also
    accept an explicitly defined non-year publication-status value.

    Supported values should be handled through a controlled allow-list rather
    than by accepting arbitrary text inside parentheses.

    Initial supported set:

    - "forthcoming"
    - "in press"
    - "n.d." / "n.d" — no publication date available
    - "in preparation"
    - "under review"
    - "submitted"
    - "unpublished" / "unpublished manuscript"

    Matching should be case-insensitive while preserving the original source
    text.

    Examples:

    "Hattiangadi and Schoubye (forthcoming)"
    → two authors, one work, publication status = "forthcoming"

    "Smith (in press)"
    → one author, one work, publication status = "in press"

    "Jones (n.d.)"
    → one author, one work, publication date status = "no date"

    "Smith and Jones (under review)"
    → two authors, one work, publication status = "under review"

    Boundary

    A recognised status value may occupy the same structural position as a
    year, but it must not be converted into a year or interpreted more strongly
    than the text supports.

    For example:

    - "forthcoming" → preserve as "forthcoming"; do not infer an expected year.
    - "in press" → preserve as "in press"; do not infer publication date.
    - "under review" → preserve as "under review"; do not infer acceptance.
    - "n.d." → preserve as no-date status; do not infer unpublished status.

    Unknown textual values in the year position must not automatically become
    valid publication statuses. They should remain unresolved until explicitly
    supported.

    Invariant

    A recognised non-year value may replace the year syntactically, but it does
    not change author parsing and must not generate an inferred publication
    year or editorial state beyond what is explicitly stated.

### What exists today

One member of his set is already in the grammar. `YEAR` in
`citation_extract.py` reads:

    (?:1[5-9]|20)\d{2}(?:[a-z](?:,[a-z])*)?|n\.d\.

so `n.d.` already occupies the year position, and `norm_year` maps it to `nd`.
That is from reading the source; whether `Jones (n.d.)` resolves end to end has
not been run, and should be the first thing checked rather than the first thing
assumed. His other seven values are not in the pattern and will not parse.

### What it would take

The allow-list belongs beside `YEAR` and inside it, not in a second pattern:
the structural position is the same one, and two patterns describing one
position is how this layer has produced most of its defects. The multi-word
values mean whitespace inside the alternative, as the particle sequences
already do.

The part that is not pattern work is his invariant. A status is not a year, so
it cannot flow into anything that treats the year as a date: the identity key,
the year-adjacent mismatch evidence, `expand_year`, and the gold set's
`author_phrase + year` identity all assume a year today. Each needs to carry
the status as a status, and the gold sets would need entries to score it
against. That, rather than the alternation, is the work.

A control that `(probably 2019)` and other unlisted text in the year position
stay unresolved is the other half, and by his own wording the more important
one: the allow-list exists so that arbitrary text does not become a status.
