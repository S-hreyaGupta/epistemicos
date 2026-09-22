#!/usr/bin/env python3
"""Citation extraction, deterministic spec v3.3 — in version control this time.

    python scripts/citation_extract.py <paper.md>              v3.3 as specified
    python scripts/citation_extract.py <paper.md> --fix all    every rc3 fix

`--fix all` rather than a typed list: this line used to name four of the five
and had not gained `mathyear`, and it was not the only copy that drifted.

Exit 0/1 = ran; 1 means the manuscript has coherence problems, per §10.
Exit 2–5 = abort, and stdout is exactly two lines, per §10.

Why this exists
---------------
The implementation behind every citation figure quoted since August — 71.5
through 95.0 per cent, the 1502 of 1611, the 142-case residual — is gone. Not in
version control, not on the machine, never uploaded. Its hash was recorded and
the artifact was not kept, which leaves a digest naming something nobody has.

This is a fresh implementation of the same specification, `citation-spec` v3.3,
which is available and normative. It cannot reproduce the old numbers, because
the old code is gone and two implementations of one spec differ in their
silences. It can be run against the same inputs: `data/md_full` holds the
fourteen corpus papers from 29 August, byte-identical to `papers.markdown`
today. So a figure from here and a figure from then differ by the extractor and
nothing else, which is the comparison anyone would actually want.

What it is not
--------------
Not rc3. rc3 is frozen at `ddc6f1f8…` and lives only in Slack, so its grammar
amendments — the bounded SURNAME production, the non-person author path, the
compact year-suffix list — are not implemented and could not be. This is v3.3
plus the four corrections that were applied on top of it during the August runs,
each behind a flag so the baseline and the corrected run are both reachable:

    ampersand   Mathpix writes \\& for &; 810 occurrences corpus-wide. §6's
                grammar matches & and never sees them. Applied at source in
                August with sed, which is a transformation and not an
                exclusion, and belongs before canonicalisation.
    segments    A parenthetical group is atomic in §6.2, so one unparseable
                segment loses every citation beside it. Splits on top-level
                `;` and parses each independently.
    colon       `(Kunda, 1990: 480)` — house style in two journals, 28 cases,
                all from a paper absent from the original eleven. LOCATOR
                takes `, p. 480` only. Requires a digit after the colon,
                which is what separates `1990: 480` from `2024: Wezel et al.`
    cp          `cp.` as a PREFIX cue. Five occurrences, one paper, one token.

Run with no flags to get v3.3 as specified. The flags are named in the output's
meta record, so no figure can be quoted without saying which extractor produced
it — which is the whole reason the old one's absence matters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

SPEC_VERSION = "3.3"

# ------------------------------------------------- rc3 §A, the output contract
#
# rc3 A1, on what rc2 emitted and this implementation emitted until today:
#
#     rc2 emits every unresolved candidate as `unresolved_citation` with
#     `no_grammar_match`. A mathpix image URL and a genuinely missed citation
#     are byte-identical in the record.
#
# That was exactly true here. The corpus carried 247 unresolved spans and
# nothing in the output distinguished a span the parser MISSED from one it was
# RIGHT to refuse, so every accuracy figure computed over them was computed
# over a denominator containing known non-citations.
#
# A1 gives three terminal states and A4 gives one lifecycle for reaching them:
#
#     raw detection → candidate → exclusion classification
#                                     ├── excluded_candidate      terminal
#                                     └── eligible candidate
#                                             ├── parsed
#                                             └── unresolved_citation
#
# "Exclusion classifies a candidate; it does not prevent one." So an excluded
# span is EMITTED, with a reason, and is visible in the record. It is not
# dropped — §G's A4 case is "excluded span → excluded_candidate, NOT absent".
CANDIDATE_STATES = ("parsed", "unresolved_citation", "excluded_candidate")

# rc3 A2. The set is CLOSED, and the counts are rc3's own, over its nine
# in-profile papers. `bare_locator` is deliberately absent: rc3 puts
# `(Barbier, 2022; P.923)` in §C's diagnostic class, because a semicolon where
# APA wants a comma is an author error, not a correct refusal.
#
# WHAT IS IMPLEMENTED, AND WHAT IS NOT. Four of the six have a rule stated
# somewhere in rc3; two do not. Detectors exist only where a rule does, and the
# reason each of the others is absent was measured against the corpus rather
# than assumed — see `classify_exclusion` and EXCLUSION-COVERAGE.md.
EXCLUDED_REASONS = {
    "leading_gloss":       11,   # NO RULE ANYWHERE IN rc3 — not implemented
    "url_or_image":         8,   # B10 + §G case          — implemented
    "publisher_metadata":   4,   # §E, by section name    — implemented
    "math_expression":      3,   # B10, with D2 carve-out — implemented, 0 hits
    "conversion_artifact":  3,   # NO RULE ANYWHERE IN rc3 — not implemented
    "non_citation_year":    1,   # §F names ONE instance and no rule — see below
}

# ---------------------------------------------------------------- §4 grammar

NAMECHAR = r"[^\W\d_]|['’\-]"
CORE = r"[A-ZÀ-Þ][\w'’\-]+"
PARTICLES = ("de", "del", "della", "der", "den", "di", "da", "dos", "du",
             "la", "le", "van", "von", "ter", "ten", "zu", "zur")
# §4 lists the particles in lower case and says "single words, compared via
# lower()". Joining them into a case-sensitive alternation did not do that, so
# `van der Maas` parsed and `Van der Maas` did not — the same name, the second
# form being what you get at the start of a sentence. §12 names `van der Maas
# (2022)` as a conformance case and the suite tested exactly that spelling, so
# nothing caught it.
#
# Scoped flag rather than re.I on the whole pattern: CORE is `\p{Lu}NAMECHAR+`
# and must stay case-sensitive, or every lower-case word becomes a surname.
#
# Worth 15 citations across the nine in-profile papers, 10 fewer unresolved
# spans, and nothing lost on any paper.
PARTICLE = "(?i:" + "|".join(PARTICLES) + ")"
WS = r"[ \t\n]+"
# rc3 B1a, "SURNAME — personal, two cores. Worth 9", is NOT implemented, and
# the reason is worth keeping rather than rediscovering.
#
#     SURNAME = (PARTICLE WS)* CORE (WS (PARTICLE WS)? CORE)?
#
# It was implemented on 21 September and reverted the same day. It works —
# `Carrieri de Souza`, `Oliveira da Silva`, `El Akremi`, `Pircher Verdorfer`
# all key correctly, worth +0.011 recall on gold paper 1 and +0.040 on paper 2.
# It also breaks four §12 conformance requirements, because a second CORE lets
# SURNAME swallow the word in front of it:
#
#     In Smith (2020)            -> in smith|2020        §12: STOP discarded
#     Following Bartko's (1976)  -> following bartko|1976
#     World Bank (2024)          -> world bank|2024      §12: must NOT degrade
#     (Adam Smith, 1776)         -> adam smith|1776      §12: forename-first
#                                                        is unresolved
#
# rc3 says where the safety comes from, and it is not the grammar. B1b:
#
#     Under two-pass, Pass 1 assigns no identity, so the complete phrase
#     reaches reconciliation and NON_PERSON_AUTHOR classifies it there.
#
# v3.3 is single-pass and assigns identity at extraction, so nothing
# downstream catches these. B1a and B1b are a pair — B1b is itself blocked on
# rc2, which rc3 amends and which nobody has — and B1a alone trades four
# conformance requirements for recall. Implementing it needs either rc2 or
# v3.4's two-pass split, which is the architecture decision, not a grammar fix.
#
# rc3 B2, "Lowercase core after a particle. Worth 1":
#
#     Da silva  →  Da matches PARTICLE, silva fails CORE
#
#     Permit a lowercase core ONLY immediately after a matched PARTICLE.
#
# The restriction is the whole safety argument, in rc3's words: "Relaxing
# CORE's capital requirement generally would admit ordinary prose into the
# candidate run, which is the hazard §6.1's eligibility test exists to
# prevent." So this form appears only in the position a particle has already
# established, never as the first core of a surname.
CORE_AFTER_PARTICLE = r"[A-Za-zÀ-þ][\w'’\-]+"

# rc3 B1a is `(PARTICLE WS)* CORE (WS (PARTICLE WS)? CORE)?` — a run of leading
# particles, then one core, then optionally one more core with at most one
# particle ahead of it. A first draft here allowed a single leading particle
# and broke `van der maas`, which needs two. The `*` is load-bearing.
_LEAD = rf"(?:(?:{PARTICLE}){WS})+{CORE_AFTER_PARTICLE}|{CORE}"
SURNAME = rf"(?:{_LEAD})"
# rc3 B6 admits `2019a,b` here so the GROUP matches; the expansion into
# separate year tokens happens at record time via `expand_year`. The
# suffix on the base is required before any bare suffix may follow, which
# is what keeps `(Smith, 2020, 2021)` out of the production.
YEAR = r"(?:1[5-9]|20)\d{2}(?:[a-z](?:,[a-z])*)?|n\.d\."
INITIALS = r"[A-Z]\.(?:[- ]?[A-Z]\.)*"

# rc3 B7, "`and colleagues`. Worth 4":
#
#     Jost and colleagues (2003a)
#     Colquitt and colleagues (2012)
#     Dalal and colleagues (2009)
#
#     A closed two-token construction equivalent to `et al.`
#
# Closed, so it is spelled out rather than generalised to "and <noun>", which
# would make `Smith and Jones (2020)` ambiguous with a two-author list.
# The trailing possessive belongs to the whole author phrase, not to the last
# surname: rc3 B8 writes `Mackey et al.'s (2017)` and `Martinko et al.'s review
# (2013)`. Without the optional `'s` here, AUTHORS_NARR stops at `al.` and the
# possessive is left outside the match, so B8's lookbehind never fires.
ET_AL = rf"(?:et{WS}al\.['’]?s?|and{WS}colleagues['’]?s?)"

AUTHORS_PAREN = (rf"(?:{SURNAME}{WS}{ET_AL}"
                 rf"|{SURNAME}(?:,{WS}?{SURNAME})*(?:,?{WS}(?:&|and){WS}{SURNAME})?)")
AUTHORS_NARR = (rf"(?:{SURNAME}{WS}{ET_AL}"
                rf"|{SURNAME}(?:,{WS}{SURNAME})*,?{WS}(?:&|and){WS}{SURNAME}"
                rf"|{SURNAME})")

# §11 limitation, kept: LOCATOR takes `, p. 480` and not `: 480`. The `colon`
# flag adds the second form rather than replacing the first.
LOCATOR = r",[ \t\n]?(?:p\.|pp\.|para\.|chap\.)[ \t\n]?[^();]+"
LOCATOR_COLON = r"(?::[ \t]*\d[^();]*)"
PREFIX_CUES = ("e.g.", "i.e.", "cf.", "see also", "see", "but see")

# rc3 B5, "Bounded lead-in cue. Worth 17". The cue set is CLOSED and is listed
# in rc3 verbatim; it is not a pattern over "for a <noun>", because an open
# form would admit ordinary prose ahead of any parenthetical year.
#
#     LEAD_IN ","? CUE CITATION_LIST, with CUE a CLOSED set.
#
# Longest first, so `see also` is not consumed as `see` leaving `also` to fail
# the group.
LEAD_IN_CUES = (
    "for a recent review", "for comparative examples", "for a meta-analysis",
    "for an overview", "for a similar approach", "for a critique",
    "for critiques", "for a review", "for details", "see for example",
    "see also", "see",
)

PREFIX_CUES_CP = PREFIX_CUES + ("cp.",)

# rc3 B8. Named as the spec names it, so the number is findable from the text.
MAX_POSSESSIVE_YEAR_GAP_TOKENS = 3

NUMCITE = re.compile(r"\[\d{1,3}(?:[ \t]*[,–—-][ \t]*\d{1,3})*\]")
SUPCITE = re.compile(r"[¹²³⁰⁴-⁹]+")

STOP = {
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "jan.", "feb.", "mar.",
    "apr.", "jun.", "jul.", "aug.", "sep.", "sept.", "oct.", "nov.", "dec.",
    "in", "the", "a", "an", "see", "since", "during", "early", "late", "as",
    "at", "on", "after", "before", "table", "figure", "section", "chapter",
    "equation", "however", "moreover", "unlike", "although", "while",
    "whereas", "thus", "therefore", "furthermore", "additionally", "finally",
    "similarly", "likewise", "consequently", "meanwhile", "nevertheless",
    "nonetheless", "indeed", "overall", "importantly", "notably",
    "specifically", "together", "here", "there", "this", "these", "those",
    "using", "given", "despite", "beyond", "under", "over", "from", "with",
    "within", "without", "across", "toward", "towards", "per", "via",
    "following", "like", "first", "second", "third", "next", "then", "also",
    "yet", "still", "both", "when", "where", "because", "if", "unless",
    "until", "once",
}

GUARD = ("et al.", "e.g.", "i.e.", "cf.", "vs.", "Dr.", "Prof.", "Mr.",
         "Mrs.", "Ms.", "St.", "Jr.", "Sr.", "no.", "No.", "p.", "pp.",
         "Vol.", "vol.", "Eq.", "Fig.", "Figs.", "Tab.", "ca.", "ed.",
         "eds.", "approx.", "U.S.", "U.K.")

HEAD_MD = re.compile(r"^(#{1,6})[ \t]+(.*)$")
HEAD_HTML = re.compile(r"^[ \t]*<h([1-6])(?:[ \t][^>]*)?>(.*?)</h\1>[ \t]*$",
                       re.I)
REF_NAMES = {"references", "bibliography", "works cited"}

# §10 exit 2, the author-date style guard.
#
# The existing exit-2 test looks for numeric and superscript citations, and
# c22df19f has neither — yet it scores 30.5% because its style is comma-less
# author-date, `(Smith 2020)`, throughout. Nothing in the implementation
# detected that. It was classified as out of apa7_like_v1 in August by a person
# reading a report, which is a judgement rather than a rule, and it has been
# quoted as a result ever since.
#
# Alex Zamurko, 18 September: *add a deterministic author-date style check for
# that pattern; do not treat the existing numeric/superscript guard as
# sufficient.*
#
# The discriminator is the comma before the year. APA writes `(Smith, 2020)`;
# author-date styles write `(Smith 2020)`. Measured over all fourteen papers:
#
#     thirteen papers    0-2% comma-less
#     c22df19f           100% comma-less
#
# So the threshold is not fitted to the corpus. A majority sits twenty-five
# times above the highest in-profile paper, and any line between 3% and 99%
# would separate the same way — a majority is simply the least arbitrary of
# them. The minimum sample exists because a ratio over three parentheticals
# means nothing.
STYLE_MIN_SAMPLE = 10
STYLE_COMMA_LESS_MAX = 0.50

_APA_PAREN = re.compile(
    r"\([^()]*?[A-ZÀ-Þ][\w'’\-]+(?:[^()]*?),\s(?:1[5-9]|20)\d{2}[a-z]?\)")
_BARE_PAREN = re.compile(
    r"\([^()]*?[A-ZÀ-Þ][\w'’\-]+\s(?:1[5-9]|20)\d{2}[a-z]?(?:[;,][^()]*)?\)")


def comma_less_share(body: str) -> tuple[float, int]:
    """(share, total) of author-year parentheticals written without a comma."""
    apa = len(_APA_PAREN.findall(body))
    bare = len(_BARE_PAREN.findall(body))
    total = apa + bare
    return (bare / total if total else 0.0), total
ENTRY_START = re.compile(rf"^(?:(?:{PARTICLE})[ ])*{CORE},[ ]{INITIALS}",
                         re.I | re.U)
YEAR_RE = re.compile(YEAR)

ROLE_KEYWORDS = [
    ("introduction", ["introduction"]),
    ("literature_review", ["literature", "related work", "background"]),
    ("methodology", ["method", "methods", "methodology"]),
    ("results", ["result", "results", "finding", "findings"]),
    ("discussion", ["discussion"]),
    ("conclusion", ["conclusion", "conclusions"]),
]


class Abort(Exception):
    def __init__(self, code: int, reason: str):
        self.code, self.reason = code, reason


# ---------------------------------------------------------------- §2, §3

def normalise(raw: bytes) -> str:
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Abort(5, "invalid utf-8")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", s)


def clean_name(name: str) -> str:
    return re.sub(r"^\d+(\.\d+)*[.)]?[ \t]+", "", name)


def headings(text: str) -> list[tuple[int, int, str, int, int]]:
    """(line_index, level, cleaned name, line_start, line_end)."""
    out, pos = [], 0
    for i, line in enumerate(text.split("\n")):
        start, end = pos, pos + len(line)
        pos = end + 1
        m = HEAD_MD.match(line)
        if m:
            name = re.sub(r"(?:[ \t]+#+)?[ \t]*$", "", m.group(2))
            out.append((i, len(m.group(1)), clean_name(name), start, end))
            continue
        m = HEAD_HTML.match(line)
        if m:
            inner = re.sub(r"<[^>]*>", "", m.group(2))
            out.append((i, int(m.group(1)),
                        clean_name(re.sub(r"\s+", " ", inner).strip()),
                        start, end))
    return out


def split_body_and_references(text: str):
    heads = headings(text)
    # §3.2 — sectioning that lives in h1 is refused rather than remapped.
    if sum(1 for h in heads if h[1] == 1) >= 2 and \
            not any(h[1] == 2 for h in heads):
        raise Abort(4, "heading contract violated")

    ref = next((h for h in heads
                if 2 <= h[1] <= 4 and h[2].strip().lower() in REF_NAMES), None)
    source = "detected" if ref is not None else None

    if ref is None:
        # §3, unmarked-up label. Four of the fourteen corpus papers aborted
        # here from August to 19 September, recorded as "references section
        # not found". They all have one: 58 to 99 entries each, alphabetically
        # ordered, sitting where a bibliography sits, and the line immediately
        # above the first entry reads exactly
        #
        #     References
        #
        # as plain text. Mathpix wrote the word and did not mark it up, so
        # headings() never saw it and the whole document was refused. 582
        # citations, 27% of the corpus, behind two characters and a space.
        #
        # Alex Zamurko, 18 September: treat that standalone line as the
        # boundary when no marked-up heading exists, and use alphabetical
        # ordering only as confirmation. Narrower than the structural fallback
        # first proposed, which was over-engineered because the evidence
        # gathered asked what the last *heading* before the block was and
        # never what the last *line* was.
        ref = _unmarked_reference_label(text)
        if ref is not None:
            source = "inferred"

    if ref is None:
        # rc2 §10, bibliography-absent mode. This used to `raise Abort(3,
        # "references section not found")`, which is v3.3's behaviour and
        # which rc2 replaced: §14's abort list allocates exit 3 to "invalid
        # section map" and gives no exit at all for a missing bibliography.
        #
        #     If `references_source = not_available`:
        #         Pass 1 extraction          performed
        #         Pass 2 identity resolution not evaluated
        #
        # A manuscript with no reference list is a manuscript this tool can
        # still read. Refusing it threw away every citation in the document to
        # report one thing about the bibliography — which is the shape of the
        # defect that cost this corpus four papers and 582 citations until
        # 19 September, and is worth not repeating one rule over.
        return text, "", len(text), heads, "not_available"

    after = [h for h in heads if h[3] > ref[3] and h[1] <= ref[1]]
    ref_end = after[0][3] if after else len(text)
    body = text[:ref[3]]
    return body, text[ref[4] + 1:ref_end], ref[4] + 1, heads, source


# How much of the run after the label has to look like a bibliography, and how
# much of it has to be in order. Both are deliberately loose: the corpus runs
# 95-100% ascending and so do the papers that already work, so the check
# confirms rather than discriminates.
MIN_ENTRIES = 5
MIN_ASCENDING = 0.80


def _unmarked_reference_label(text: str):
    """A standalone `References` line acting as a section boundary.

    Returns a heading-shaped tuple so the caller cannot tell the difference,
    or None. The label alone is not enough — what follows it has to look like
    a reference list, or any paragraph ending in the word would split a paper.
    """
    lines = text.split("\n")
    offs, pos = [], 0
    for line in lines:
        offs.append(pos)
        pos += len(line) + 1

    for i, line in enumerate(lines):
        if line.strip().lower() not in REF_NAMES:
            continue

        # Confirmation, per the ruling: the run below is entry-shaped and in
        # near-alphabetical order by first surname.
        surnames = []
        for later in lines[i + 1:]:
            s = later.strip()
            if not s:
                continue
            m = ENTRY_START.match(s)
            if m:
                surnames.append(re.split(r",", m.group(0))[0].strip().lower())
        if len(surnames) < MIN_ENTRIES:
            continue
        ascending = sum(1 for a, b in zip(surnames, surnames[1:]) if a <= b)
        if ascending / max(1, len(surnames) - 1) < MIN_ASCENDING:
            continue

        start = offs[i]
        return (i, 2, clean_name(line.strip()), start, start + len(line))
    return None


def roles_of(name: str) -> list[str]:
    low = name.lower()
    hits = []
    for role, words in ROLE_KEYWORDS:
        best = None
        for w in words:
            m = re.search(rf"(?<![^\W_])\b{re.escape(w)}\b(?![^\W_])", low)
            if m and (best is None or m.start() < best):
                best = m.start()
        if best is not None:
            hits.append((best, role))
    return [r for _, r in sorted(hits, key=lambda x: x[0])]


def section_stack_at(heads, offset: int):
    stack = []
    for _, level, name, start, _ in heads:
        if start >= offset:
            break
        if 2 <= level <= 4:
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, name))
    if not stack:
        return "none", "front matter", "other", []
    level, name = stack[-1]
    for lv, nm in reversed(stack):
        rs = roles_of(nm)
        if rs:
            return f"h{level}", name, rs[0], rs
    return f"h{level}", name, "other", []


# ---------------------------------------------------------------- §5

def sentences(body: str) -> list[tuple[int, int, int]]:
    """(start, end, content_end) for each sentence in the body."""
    out = []
    for para_start, para in paragraphs(body):
        i, sent_start = 0, None
        while i < len(para):
            if sent_start is None and not para[i].isspace():
                sent_start = i
            ch = para[i]
            if ch in ".?!" and sent_start is not None:
                j = i + 1
                while j < len(para) and para[j] in "”\"’')]":
                    j += 1
                tail = para[j:]
                ends = (not tail.strip()) or re.match(r"\s+[A-ZÀ-Þ]", tail)
                if ends and not guarded(para, i):
                    out.append((para_start + sent_start, para_start + j,
                                para_start + i))
                    sent_start, i = None, j
                    continue
            i += 1
        if sent_start is not None:
            end = len(para.rstrip())
            out.append((para_start + sent_start, para_start + end,
                        para_start + end))

    # rc2 §5, the two sentence-relative quantities. Both are properties of a
    # sentence's PLACE IN THE BODY rather than of its text, so they are
    # attached here where the ordinal exists, not recomputed per citation.
    #
    #     sentence_index = 0-based ordinal among body sentences, CONTINUOUS
    #                      across sections
    #     previous_sentence_end = previous sentence content_end, or null for
    #                      the first body sentence
    #
    # "Continuous across sections" is the part worth stating: paragraphs and
    # headings break sentences, and the counter does not restart at either.
    # C-026 tests exactly that.
    return [(s, e, ce_, i, out[i - 1][2] if i else None)
            for i, (s, e, ce_) in enumerate(out)]


def paragraphs(body: str):
    pos = 0
    buf_start, buf = None, []
    for line in body.split("\n"):
        start, end = pos, pos + len(line)
        pos = end + 1
        if not line.strip() or HEAD_MD.match(line) or HEAD_HTML.match(line):
            if buf:
                yield buf_start, "\n".join(buf)
            buf_start, buf = None, []
            continue
        if buf_start is None:
            buf_start = start
        buf.append(line)
    if buf:
        yield buf_start, "\n".join(buf)


def guarded(para: str, t: int) -> bool:
    ctx = para[:t + 1]
    for g in GUARD:
        if ctx.endswith(g):
            before = ctx[:-len(g)]
            if not before or before[-1] in " \t\n([\"“'‘":
                return True
    m = re.search(r"[A-ZÀ-Þ]\.$", ctx)
    if m:
        before = ctx[:m.start()]
        if not before or before[-1] in " \t\n([\"“'‘":
            return True
    return False


# ---------------------------------------------------------------- §6

ELIGIBLE = re.compile(r"[A-ZÀ-Þ][\w'’.\-]*$", re.U)
# `colleagues` joins the eligible-lower set for rc3 B7. Without it the C2 run
# stops before the word, so `Jost and colleagues (2003a)` never reaches the
# grammar at all and B7's production is unreachable in narrative position —
# which is the only position the construction occurs in. The parenthetical
# form needs no run and worked without this.
ELIGIBLE_LOWER = {"et", "al.", "and", "&", "colleagues"} | set(PARTICLES)


def c1_spans(body: str) -> list[tuple[int, int]]:
    """§6.1 C1: maximal ( ... ) with no nesting, whose content holds a YEAR."""
    out = []
    for m in re.finditer(r"\([^()]*\)", body):
        if YEAR_RE.search(m.group(0)):
            out.append((m.start(), m.end()))
    return out


def sentence_of(sents, offset: int):
    for s in sents:
        if s[0] <= offset < s[1]:
            return s
    return None


def token_run(body: str, c1_start: int, sent_start: int):
    """§6.1 C2: walk left from C1 while tokens are eligible, never past the
    sentence start. Returns (run_start, [token strings]) innermost-last.

    rc3 B1, on the six-token cap v3.3 §6.1 specifies:

        Do not reintroduce a token cap. C2 removed the six-token cap for a
        reason and the corpus still contains the case that removed it:
        Van den Brink and Van der Woerd, 7 tokens, present twice.

    and later, of whichever production is doing the work:

        The span-length point stands unchanged: no global token cap.

    The cap is what produced EC-3 — four works in the corpus attributed to the
    wrong author, silently, because the run began partway through the author
    list and §6.2's longest-admissible-suffix rule then parsed the remainder as
    a shorter but well-formed list. `El Akremi, Gond, Swaen, De Roeck, and
    Igalens (2015)` came out as `gond|2015`.

    What still bounds the run, per rc3: eligibility and the sentence boundary,
    exactly as they were. Every collected token must be `\\p{Lu}`-initial or in
    the eligible-lower set, and none may start before sentence_start. Ordinary
    prose is stopped by the eligibility test rather than by counting.
    """
    i = c1_start
    toks, positions = [], []
    while True:
        j = i
        while j > sent_start and body[j - 1] in " \t\n":
            j -= 1
        if j <= sent_start:
            break
        k = j
        while k > sent_start and body[k - 1] not in " \t\n":
            k -= 1
        if k < sent_start:
            break
        tok = body[k:j]
        bare = tok[:-1] if tok.endswith(",") else tok
        # `al.'s` is `al.` wearing a possessive. Without stripping it the run
        # stops on the tail of `Mackey et al.'s (2017)` and B8 is unreachable
        # for every et-al. form, which is most of them.
        unpossessed = POSSESSIVE.sub("", bare)
        if not (ELIGIBLE.match(bare) or bare.lower() in ELIGIBLE_LOWER
                or unpossessed.lower() in ELIGIBLE_LOWER):
            # rc3 B8's gap is unreachable without this, and rc3 does not say
            # so. It specifies what the gap terminates at — sentence boundary,
            # comma, semicolon, parenthesis, another candidate — but not how
            # the §6.1 envelope reaches across it, and §6.1 eligibility stops
            # the walk at the first ordinary word. `Harter's definition of
            # authenticity (2002)` collected an empty run.
            #
            # So: on hitting an ineligible token, look further left for a
            # possessive within the bound. If one is there, the intervening
            # words are the gap and the run continues through them. If not,
            # stop exactly where eligibility said to. The exception cannot
            # widen anything that does not end in `'s`.
            gap = _possessive_gap(body, k, sent_start)
            if gap is None:
                break
            # The token that triggered the look-ahead is itself part of the
            # gap, and the loop walks leftward, so everything goes on in walk
            # order: this token first, then the words beyond it, ending at the
            # possessive. `positions` and `toks` are reversed together at the
            # end, so inserting in any other order scrambles both.
            toks.append(tok)
            positions.append(k)
            for g_tok, g_pos in gap:
                toks.append(g_tok)
                positions.append(g_pos)
            i = gap[-1][1]
            continue
        toks.append(tok)
        positions.append(k)
        i = k
    toks.reverse()
    positions.reverse()
    return (positions[0] if positions else c1_start), toks


def _possessive_gap(body: str, upto: int, sent_start: int):
    """The tokens of an rc3 B8 gap, or None.

    Walks left from `upto` collecting at most
    MAX_POSSESSIVE_YEAR_GAP_TOKENS words, and returns them only if the token
    immediately beyond them ends in a possessive. Returns the gap *including*
    that possessive token, in walk order — nearest first, possessive last —
    which is the order the caller's loop builds `toks` in. An earlier version
    reversed here and produced a run with tokens out of order and one of them
    duplicated.

    The terminators are rc3's: the gap does not cross a sentence boundary, a
    comma or semicolon, or a parenthesis. A token carrying any of those ends
    the attempt rather than being skipped over.
    """
    out, i = [], upto
    for _ in range(MAX_POSSESSIVE_YEAR_GAP_TOKENS + 1):
        j = i
        while j > sent_start and body[j - 1] in " \t\n":
            j -= 1
        if j <= sent_start:
            return None
        k = j
        while k > sent_start and body[k - 1] not in " \t\n":
            k -= 1
        if k < sent_start:
            return None
        tok = body[k:j]
        if any(ch in tok for ch in ",;()"):
            return None
        out.append((tok, k))
        if POSSESSIVE.search(tok):
            return out
        i = k
    return None


def build_patterns(fixes: set[str]):
    loc = LOCATOR + (f"|{LOCATOR_COLON}" if "colon" in fixes else "")
    cues = PREFIX_CUES_CP if "cp" in fixes else PREFIX_CUES
    # rc3 B5: LEAD_IN ","? CUE CITATION_LIST, CUE a closed set, plus a bounded
    # *trailing* form — `(see X, 2013, for a critique)`.
    #
    # The §4 PREFIX cues and B5's LEAD_IN cues are one optional element with an
    # internal alternation, not two optional groups in sequence. Written as
    # `(?:prefix)?(?:lead)?AUTHORS_PAREN…` the engine has to try every division
    # of the text between two optionals before the authors, and with SURNAME
    # now carrying its own alternations the segment pattern went exponential —
    # a corpus run that had taken seconds did not finish in three minutes.
    # Longest cue first inside the alternation, so `see also` is not consumed
    # as `see`.
    all_cues = tuple(sorted(set(cues) | set(LEAD_IN_CUES),
                            key=lambda c: (-len(c), c)))
    prefix = "(?:" + "|".join(re.escape(c) for c in all_cues) + r")[,]?[ \t\n]+"
    trail = r",[ \t\n]*(?:" + \
            "|".join(re.escape(c) for c in LEAD_IN_CUES) + ")"
    seg = (rf"(?:{prefix})?{AUTHORS_PAREN},{WS}(?:{YEAR})"
           rf"(?:,{WS}(?:{YEAR}))*(?:{loc})?(?:{trail})?")
    return {
        "seg": re.compile(seg, re.U),
        "cite_paren": re.compile(rf"\([ \t\n]?{seg}(?:;[ \t\n]?{seg})*[ \t\n]?\)",
                                 re.U),
        "cite_narr": re.compile(
            rf"{AUTHORS_NARR}{WS}\([ \t\n]?(?:{YEAR})(?:,{WS}(?:{YEAR}))*"
            rf"(?:{loc})?[ \t\n]?\)", re.U),
        # rc3 B8, "Possessive narrative, with a bounded gap. Worth 7". rc2
        # covers `Fine's (1998)`; new here is a noun between author and year:
        #
        #     Martinko et al.'s review (2013)
        #     Harter's definition of authenticity (2002)
        #
        #     NARRATIVE_POSSESSIVE_NORMALIZATION MUST tolerate at most
        #     MAX_POSSESSIVE_YEAR_GAP_TOKENS = 3 intervening tokens between
        #     the possessive author and (YEAR).
        #
        #     The gap TERMINATES at, and does not cross: a sentence boundary,
        #     a comma or semicolon, an opening or closing parenthesis, or any
        #     other citation candidate.
        #
        # The lookbehind is what keeps this from becoming a general "author,
        # some words, year" rule: without the possessive, `Smith review
        # (2020)` would match and is not a citation. rc3 is explicit that the
        # bound is legitimate here where B1's was not, because it limits a gap
        # between two anchored elements rather than the length of the author
        # expression.
        #
        # Three is the longest gap observed, so the bound sits at the measured
        # maximum — rc3 calls that "also the weak point: one unseen paper with
        # a four-token gap fails", and says the number should move only on
        # evidence.
        "cite_narr_poss": re.compile(
            rf"{AUTHORS_NARR}(?<=['’]s){WS}"
            rf"(?:[^\s,;().]+{WS}){{1,{MAX_POSSESSIVE_YEAR_GAP_TOKENS}}}"
            rf"\([ \t\n]?(?:{YEAR})(?:,{WS}(?:{YEAR}))*"
            rf"(?:{loc})?[ \t\n]?\)", re.U),
        "seg_anchored": re.compile(rf"\A{seg}\Z", re.U),
    }


POSSESSIVE = re.compile(r"['’]s\b")


def first_core(authors: str) -> str:
    """The first author's full SURNAME, particles included, single-spaced.

    A trailing possessive is not part of the surname. `Bartko's (1976)` and
    `Bartko (1976)` are one work, and carrying the `'s` into the derived
    identity split it into two: the gold set held `bartko 1976` and this
    produced `bartko's 1976`, so the same single cause scored as a miss *and*
    as a false positive. Six of gold paper 1's nine remaining discrepancies
    were three works counted that way.

    Worse than a miss, because the record is `parsed` with a well-formed key
    and is indistinguishable in the output from a correct one. In ea07e5f5 it
    produced the paper's only unmatched citation key, against a reference
    sitting in the same document.

    Recorded as EC-2, ruled by Alex Zamurko on 18 September as an extractor
    grammar error rather than an annotation error, so the gold sets keep the
    bare form and this is the side that moves.

    Stripped here, when deriving the identity, and *not* from `author_phrase`:
    rc3 §A requires author_phrase to record the complete source candidate
    phrase, and the possessive is part of what the manuscript wrote.
    """
    toks = authors.split()
    out: list[str] = []
    i = 0

    def bare(t: str) -> str:
        return t.rstrip(",")

    # Leading particles. A comma ends the surname, so a comma-terminated
    # particle is not one — it is the last token of a previous author.
    while i < len(toks) and bare(toks[i]).lower() in PARTICLES \
            and not toks[i].endswith(","):
        out.append(bare(toks[i]))
        i += 1

    if i >= len(toks):
        return POSSESSIVE.sub("", " ".join(out))

    first_ended_the_name = toks[i].endswith(",")
    out.append(bare(toks[i]))
    i += 1

    # rc3 B1a's optional second core: (WS (PARTICLE WS)? CORE)?
    #
    # Only reachable when the first core was not comma-terminated, because a
    # comma separates authors: `Smith, Jones, 2020` is two authors and
    # `Carrieri de Souza, 2023` is one. Without that guard the key for a
    # multi-author group would absorb the second author's surname.
    #
    # One repetition, not a loop — B1b is explicit that the production admits
    # at most two CORE elements and that institutional authors are a separate
    # path.
    if not first_ended_the_name and i < len(toks):
        j, extra = i, []
        if bare(toks[j]).lower() in PARTICLES and not toks[j].endswith(","):
            extra.append(bare(toks[j]))
            j += 1
        if j < len(toks):
            nxt = bare(toks[j])
            # A second CORE, and not a connective or the et-al. tail: those
            # end the author phrase rather than continuing a surname.
            if re.fullmatch(CORE, nxt) and nxt.lower() not in ("et", "al.", "and"):
                extra.append(nxt)
                out.extend(extra)

    return POSSESSIVE.sub("", " ".join(out))


def is_all_caps(core: str) -> bool:
    last = core.split()[-1] if core.split() else ""
    letters = [c for c in last if c.isalpha()]
    return len(letters) >= 2 and all(c.isupper() for c in letters)


def norm_year(y: str) -> str:
    return "nd" if y == "n.d." else y


# rc3 B6, worth 2, both in `ad1e3ff9` — which is gold paper 1, so this moves a
# measured figure rather than a projected one.
#
#     2019a,b   →   2019a + 2019b
#     BASE_YEAR SUFFIX ("," SUFFIX)+
#
# rc3 adds: "Deterministic expansion. Do not generalise to arbitrary year
# inference." So `2019a,b` expands and `2019,20` does not — the production
# requires a suffix on the base before any bare suffix can follow, which is
# what keeps `(Smith, 2020, 2021)` out of it.
COMPACT_YEAR = re.compile(r"\A((?:1[5-9]|20)\d{2})([a-z])((?:,[a-z])+)\Z")


def expand_year(tok: str) -> list[str]:
    """One year token in, one or more out. Only B6's shape expands."""
    m = COMPACT_YEAR.match(tok)
    if not m:
        return [norm_year(tok)]
    base, first, rest = m.groups()
    return [base + first] + [base + s for s in rest.split(",") if s]


def split_segments(inner: str) -> list[str]:
    """Top-level `;` split. Used only under the `segments` fix."""
    return [s for s in inner.split(";")]


# ------------------------------------------------------- rc3 §A4 exclusion
#
# Runs BEFORE the grammar, per A4: every proposed span is a candidate, and
# exclusion classifies it rather than stopping it from being one. rc3 is
# explicit about why the distinction matters, in B10:
#
#     An earlier draft said A3 "prevents spans becoming candidates". That
#     contradicted §A, where the same 11 instances are counted as
#     `excluded_candidate` removals — if they were never candidates the
#     accounting could not be reproduced from the output contract.

# §E. "Sections identified as `front matter` or `Citation information` are OUT
# of the in-text citation envelope." rc3 adds "No new detection is required —
# the section map already labels both by name."
#
# It labels ONE of them by name. `section_stack_at` returns the literal string
# "front matter" as its DEFAULT when no h2-h4 heading precedes the offset, so
# testing `name == "front matter"` would pass for a reason other than the one
# it is named for: not because a section was identified as front matter, but
# because no section had started yet. Those two coincide in this corpus and
# would stop coinciding the moment a paper carried an actual `## Front matter`
# heading, or the default string changed.
#
# So the front-matter half is tested STRUCTURALLY as well, on the level:
# "above every h2" is what a paper with an untitled preamble actually means,
# and it is checkable without depending on a default string. Measured over all
# fourteen papers before choosing it — six papers have exactly one C1 span
# above their first h2, every one of them the journal's own "To cite this
# article:" line, and the other eight have none. No abstract sits there: the
# first h2 is `## Abstract` in thirteen of the fourteen.
#
# "front matter" is deliberately NOT in the name set below, and the reason is
# a surviving mutation rather than a preference.
#
# §E's words are "sections identified as front matter", so listing the name
# looked right and was added. The mutation probe then removed the structural
# test and the suite stayed green: `section_stack_at` hands back the fabricated
# name "front matter", the name test caught the same span, and the control
# named for the structural rule had been passing through the other branch the
# whole time. The same defect the whole milestone is about, one level up.
#
# Two overlapping branches where one of them matches an invented value cannot
# both be held by a control, so the invented one goes. What remains: a paper
# with an untitled preamble is handled structurally, which is every paper in
# this corpus, and a paper carrying a real `## Front matter` heading is not
# handled at all. That is a miss rather than an over-exclusion — those spans
# stay unresolved and stay in A5's denominator, where they are visible — and it
# is the safe direction to be wrong in.
ENVELOPE_OUT_NAMES = {"citation information"}


MATH_SPAN = re.compile(r"\$[^$\n]{1,400}\$")


# rc3 D2, `math_wrapped_year_parenthetical_unwrap_v1`. Worth 3 in-profile,
# eight corpus-wide, and rc3 §J records it as normative and unimplemented.
#
#     MATCH      $ ( YEAR_LIST ) $
#                where YEAR_LIST satisfies the citation year-list grammar in
#                full, and the math span contains NOTHING else
#     CONTEXT    an eligible narrative author expression immediately precedes
#     ACTION     strip the enclosing $ delimiters. Nothing inside is altered.
#     NEGATIVE   $(2012,2016) + x$   → no match, span is not year-only
#                $\alpha=0.96$       → no match
#                standalone $(2014)$ with no preceding author → no match
#
# rc3 on why the restrictions are part of the rule rather than advice:
#
#     Without the year-only and author-context restrictions, "fix upstream"
#     leaves the implementer to decide which math spans are citations, which
#     is the discretion the rule exists to remove.
#
# Same family as `\&` — Mathpix wrapping an ordinary parenthetical in math
# mode — and applied at the same point, as a flag. rc3 §J requires both to run
# before canonicalisation in ingest; neither does here, and that is the same
# open item `\&` already carries rather than a new one.
#
# MEASURED: this recovers ZERO citations, and the reason is in D2 itself.
#
# The unwrap works — every corpus case is found and its `$` stripped. What it
# produces is `Baron (2012,2016)`, and that does not parse:
#
#     v3.3 §4    CITE_NARR = AUTHORS_NARR WS \( WS? YEAR (?:, WS YEAR)* ...
#     rc2 §6.2   prose only — "one or more YEAR_TOKEN values", separator
#                unspecified
#
# `WS` after the comma is required, and `2012,2016` has none. D2 asserts the
# span's contents "satisfy the citation year-list grammar in full" and then
# says "Nothing inside is altered". Both cannot hold: the form D2 hands to the
# parser is one the parser's own grammar refuses.
#
# So the transform is implemented faithfully and left worth 0, rather than
# widening `(?:, WS YEAR)*` to make §I's +3 appear. Widening it would change
# every citation in the corpus, not only the eight D2 touches, on the strength
# of a clause rc3 does not contain. Recorded in RC2-RC3-DISCREPANCIES.md as
# the sixth.
D2_MATH_YEARS = re.compile(
    r"\$\(\s*((?:1[5-9]|20)\d{2}(?:[a-z](?:,[a-z])*)?"
    r"(?:\s*[,;]\s*(?:1[5-9]|20)\d{2}(?:[a-z](?:,[a-z])*)?)*)\s*\)\$")
# "an eligible narrative author expression immediately precedes it" — the same
# eligibility §6.1 uses to build a token run, checked on the token to the left.
D2_AUTHOR_LEFT = re.compile(
    rf"(?:[A-ZÀ-Þ][\w'’\-]+|et{WS}al\.|and{WS}colleagues|&"
    rf"|(?:{PARTICLE}))[ \t]*\Z", re.U)


def unwrap_math_years(text: str) -> str:
    """rc3 D2. Strips the `$` around a year-only parenthetical with an author."""
    def repl(m):
        before = text[:m.start()]
        if not D2_AUTHOR_LEFT.search(before):
            return m.group(0)        # rc3's third negative: no author context
        return "(" + m.group(1) + ")"
    return D2_MATH_YEARS.sub(repl, text)


def math_spans(body: str) -> list[tuple[int, int]]:
    """Every `$...$` span in the body, computed ONCE per document.

    Scanning the body per candidate instead made the run quadratic — two
    thousand candidates over two hundred kilobytes — and a corpus pass stopped
    finishing. Worth recording, because the extractor's cost is normally
    linear in the body and this is the first thing in it that was not.
    """
    return [(m.start(), m.end()) for m in MATH_SPAN.finditer(body)]


def _in_math_span(spans, s: int, e: int):
    """The enclosing `$...$` span, if the candidate sits inside one."""
    for ms, me in spans:
        if ms <= s and e <= me:
            return ms, me
        if ms > e:
            break
    return None


# D2's MATCH clause, used here only to REFUSE to exclude. See below.
D2_YEAR_ONLY = re.compile(
    r"\A\$\(\s*(?:(?:1[5-9]|20)\d{2}[a-z]?|n\.d\.)"
    r"(?:\s*[,;]\s*(?:(?:1[5-9]|20)\d{2}[a-z]?|n\.d\.))*\s*\)\$\Z")


def classify_exclusion(body: str, s: int, e: int, heads, maths=None):
    """rc3 A2's reason, or None if the span stays an eligible candidate."""
    if maths is None:
        maths = math_spans(body)
    inner = body[s + 1:e - 1]

    # B10 / §G: "mathpix cdn URL → excluded_candidate/url_or_image".
    #
    # The span must BE the URL, not merely contain one. `(BIS, 2014,
    # https://www.gov.uk/...)` is a real citation with a link inside it, and it
    # is in this corpus. A containment test excludes it; an anchored test does
    # not. Eleven spans corpus-wide match anchored, all of them the URL of a
    # `![](https://cdn.mathpix.com/...)` image whose pixel dimensions happen to
    # parse as years.
    if re.match(r"\s*(?:https?://|www\.\w)", inner, re.I):
        return "url_or_image"

    # §E, envelope. Two disjoint tests: no section has started yet, or the
    # section we are in is named one of §E's two. Kept disjoint deliberately —
    # `section_stack_at` returns the literal string "front matter" as its
    # default name, so a single name test would swallow the structural case and
    # neither could then be probed on its own.
    level, name, _, _ = section_stack_at(heads, s)
    if level == "none":
        return "publisher_metadata"
    if name.strip().lower() in ENVELOPE_OUT_NAMES:
        return "publisher_metadata"

    # B10, math. rc3 warns by name that this rule collides with D2:
    #
    #     Blanket math-span exclusion would delete three real citations —
    #     `Baron $(2012,2016)$` and `Shepherd and Kay $(2012,2014)$`, where
    #     Mathpix wrapped an ordinary parenthetical in math mode.
    #
    # So D2's own MATCH clause is applied here as a carve-out: a math span that
    # is year-only is NOT excluded, because it is a citation awaiting D2's
    # unwrapping, and excluding it would take a real citation off the
    # denominator. Measured: every one of the eight math-wrapped candidates in
    # the corpus is year-only, which is D2's "eight corpus-wide" exactly. This
    # branch therefore fires zero times here, and that is the correct result
    # rather than a missing detector — the three rc3 counts under
    # `math_expression` are not among the candidates this detector produces.
    span = _in_math_span(maths, s, e)
    if span and not D2_YEAR_ONLY.match(body[span[0]:span[1]]):
        return "math_expression"

    # `non_citation_year` is NOT detected, and the reason is a measurement.
    #
    # rc3 §F gives one instance — "three consecutive (2011, 2012, and 2013)" —
    # and no rule. The obvious rule, a pure year list with no reachable author
    # run, was tried against the corpus first: it matches 19 spans, of which 8
    # are D2's math-wrapped citations, one is §C's `Fremout et al (2022)`, and
    # several more are narrative boundary failures that §F says in terms MUST
    # NOT be removed from the denominator as false positives. One instance in
    # nineteen is not a rule, so nothing is excluded under this reason until
    # rc2 or Alex Zamurko supplies one.
    #
    # `leading_gloss` (11) and `conversion_artifact` (3) appear exactly once
    # each in the whole specs tree — in A2's own table. They carry counts and
    # no definition, so there is nothing to implement. Together with the above
    # that is 18 of rc3's 30; see EXCLUSION-COVERAGE.md.
    return None


def extract_citations(body: str, sents, heads, fixes: set[str],
                      non_person_keys=frozenset()):
    """`non_person_keys` is rc2 §8's bibliography evidence, and without it the
    institutional path stays shut.

    rc2 §8, in terms this implementation had no way to honour until rc2
    arrived:

        Syntax does not confer authoritative `author_kind` or `citation_key`.
        Pass 1 syntax creates deterministic identity candidates only.
        Authority is acquired only through exact bibliography resolution.

    That is not pedantry here, it is the difference between right and wrong on
    real corpus text. `(Pircher Verdorfer, 2016)` and `(Population Pyramid,
    2022)` are the same shape — two capitalised words, no comma, a year — and
    one is a person with a compound surname while the other is an
    organisation. Nothing in the citation can separate them. The bibliography
    can: `Pircher Verdorfer, A. (2016)` takes rc2 §7.4's person path,
    `Population Pyramid. (2022)` takes the non-person one.

    So a non-person citation is emitted only when a non-person REFERENCE with
    the identical key exists. Where it does not, the span stays unresolved,
    which is what it is today and the safe direction to be wrong in.
    """
    pat = build_patterns(fixes)
    cits, unres, excl, errs = [], [], [], []
    maths = math_spans(body)

    for c1s, c1e in c1_spans(body):
        # A4: classification precedes the grammar, and terminates the
        # candidate when it fires.
        reason = classify_exclusion(body, c1s, c1e, heads, maths)
        if reason is not None:
            _excl(body, c1s, c1e, reason, sentence_of(sents, c1s), heads, excl)
            continue

        # rc3 §C. Emitted here, once per group, BEFORE the grammar runs and
        # regardless of what the grammar then does with it — the class is
        # orthogonal to `candidate_state`, so the same group can be parsed and
        # still carry an error. rc3 forbids only one combination: a malformed
        # group is never `excluded_candidate`, which is why this sits after
        # the exclusion check rather than before it.
        defects = citation_errors(body[c1s:c1e])
        if defects:
            lv, nm, _, _ = section_stack_at(heads, c1s)
            errs.append({
                "type": "citation_error", "index": 0,
                "diagnostic_class": "citation_error",
                "scope": "parenthetical_group",
                "text": body[c1s:c1e], "start": c1s, "end": c1e,
                "defects": defects,
                "section_level": lv, "section_name": nm,
            })

        sent = sentence_of(sents, c1s)
        if sent is None:
            continue
        s_start, s_end, s_content_end, s_index, s_prev_end = sent
        c1 = body[c1s:c1e]

        # 1. Parenthetical, full match over the whole C1 span.
        m = pat["cite_paren"].fullmatch(c1)
        if m:
            segs = _paren_segments(c1, pat)
            _emit_paren(body, c1s, c1e, segs, sent, heads, cits, unres,
                        non_person_keys)
            continue

        if "segments" in fixes:
            # One unparseable segment loses every citation beside it under
            # §6.2's atomic reading. Each segment is parsed on its own and a
            # failure is reported for that segment alone.
            done = _segmented_paren(body, c1s, c1e, pat, sent, heads,
                                    cits, unres, non_person_keys)
            if done:
                continue

        # 2. Narrative: longest admissible suffix of the token run.
        run_start, toks = token_run(body, c1s, s_start)
        parsed = None
        for L in range(len(toks), 0, -1):
            span_start = c1s
            # locate the start offset of token (len-L)
            off, count = c1s, 0
            k = len(toks) - L
            span_start = _offset_of_token(body, c1s, s_start, toks, k)
            cand = body[span_start:c1e]
            if pat["cite_narr"].fullmatch(cand) \
                    or pat["cite_narr_poss"].fullmatch(cand):
                parsed = (span_start, L)
                break
        if parsed:
            span_start, L = parsed
            discarded = toks[:len(toks) - L]
            if all(_discardable(t) for t in discarded):
                # §6.3's additive reduction. `run_start` is the complete C2
                # run and `span_start` is what parsed; passing both is what
                # lets author_phrase stay whole.
                _emit_narr(body, span_start, c1e, sent, heads, cits, unres, pat,
                           non_person_keys, full_start=run_start)
                continue
            # rc3 B1b reaches here too, and this is the branch that matters
            # most. `World Bank (2016)` DOES find a matching suffix — `Bank
            # (2016)` satisfies AUTHORS_NARR on its own — and is then refused
            # because `World` is not discardable. §6.2 doing its job: rc3 §G
            # requires `World Bank (2024)` MUST NOT yield `bank|2024`, and it
            # does not.
            #
            # But a refusal is not an identification, and until now that was
            # the end of it. The complete run is the institutional phrase, so
            # it is offered whole. `bank|2016` is never constructed; either
            # `non_person|world bank|2016` is confirmed by the bibliography or
            # the span stays unresolved exactly as before.
            narr = body[run_start:c1s].rstrip()
            if narr and _non_person_citation(
                    body, run_start, c1e, run_start, c1e, narr, "narrative",
                    sent, heads, cits, non_person_keys):
                continue
            _unres(body, run_start, c1e, "no_grammar_match", sent, heads, unres)
            continue

        # rc3 B1b's detection site. Everything the person grammar can express
        # has been tried and refused. Two shapes reach here and both are in
        # the corpus:
        #
        #   (International Monetary Fund, 2022)   parenthetical, phrase before
        #                                         the separator comma
        #   World Bank (2016)                     narrative, the run before
        #                                         the year paren
        #
        # Only the phrase is offered; `_non_person_citation` applies rc2
        # §7.4's test and refuses unless a non-person reference confirms it.
        inner = body[c1s + 1:c1e - 1]
        cut = YEAR_RE.search(inner)
        if cut:
            phrase = inner[:cut.start()].rstrip().rstrip(",;:").rstrip()
            if phrase and _non_person_citation(
                    body, c1s, c1e, c1s, c1e, phrase, "parenthetical",
                    sent, heads, cits, non_person_keys):
                continue

        # A narrative branch sat here and has been removed. It fired zero
        # times across all fourteen papers, because reaching it needs the last
        # token before the year paren to fail CORE — and any single
        # capitalised word satisfies CORE, so `International Monetary Fund
        # (2022)` matches on `Fund` and is handled in the `if parsed:` branch
        # above instead. A branch no control can reach is not coverage, and
        # the mutation probe reported exactly that by refusing to call it
        # caught. If a case turns up, it comes back with a control.
        span = (run_start, c1e) if toks else (c1s, c1e)
        _unres(body, span[0], span[1], "no_grammar_match", sent, heads, unres)

    cits.sort(key=lambda r: (r["group_start"], r["segment_start"]))
    unres.sort(key=lambda r: r["start"])
    excl.sort(key=lambda r: r["start"])
    errs.sort(key=lambda r: r["start"])
    return cits, unres, excl, errs


def _offset_of_token(body, c1_start, sent_start, toks, index):
    """Offset of toks[index], recomputed by walking left as token_run did."""
    i = c1_start
    offsets = []
    for _ in range(len(toks)):
        j = i
        while j > sent_start and body[j - 1] in " \t\n":
            j -= 1
        k = j
        while k > sent_start and body[k - 1] not in " \t\n":
            k -= 1
        offsets.append(k)
        i = k
    offsets.reverse()
    return offsets[index]


def _discardable(tok: str) -> bool:
    bare = tok.rstrip(",;:")
    return bare.lower() in STOP or tok[-1:] in ",;:"


def _paren_segments(c1: str, pat):
    inner = c1[1:-1]
    return [m.group(0) for m in pat["seg"].finditer(inner)]


def _emit_paren(body, c1s, c1e, segs, sent, heads, cits, unres,
                non_person_keys=frozenset()):
    inner_off = c1s + 1
    for seg_text in segs:
        pos = body.find(seg_text, inner_off, c1e)
        if pos < 0:
            continue
        _emit_segment(body, c1s, c1e, pos, pos + len(seg_text), seg_text,
                      "parenthetical", sent, heads, cits, unres,
                      non_person_keys)


def _segmented_paren(body, c1s, c1e, pat, sent, heads, cits, unres,
                     non_person_keys=frozenset()) -> bool:
    inner = body[c1s + 1:c1e - 1]
    pieces, off, any_ok = [], c1s + 1, False
    for piece in inner.split(";"):
        p_start = off
        p_end = off + len(piece)
        off = p_end + 1
        stripped = piece.strip()
        if not stripped:
            continue
        if pat["seg_anchored"].fullmatch(stripped):
            s = body.find(stripped, p_start, p_end + 1)
            _emit_segment(body, c1s, c1e, s, s + len(stripped), stripped,
                          "parenthetical", sent, heads, cits, unres,
                          non_person_keys)
            any_ok = True
        else:
            pieces.append((p_start, p_end, stripped))
    if not any_ok:
        return False
    for p_start, p_end, stripped in pieces:
        s = body.find(stripped, p_start, p_end + 1)
        _unres(body, s, s + len(stripped), "no_grammar_match", sent, heads,
               unres)
    return True


def _emit_narr(body, span_start, c1e, sent, heads, cits, unres, pat,
               non_person_keys=frozenset(), full_start=None):
    """rc2 §6.3. `span_start` begins the phrase that PARSED; `full_start`
    begins the complete collected C2 run.

    They differ exactly when leading tokens were removed, and §6.3 requires
    both to survive: `author_phrase` is the full run, `stop_reduced_phrase` is
    what parsed. The caller has already checked every removed token is
    discardable, which is §6.3's own condition for the reduction existing.
    """
    if full_start is None:
        full_start = span_start
    text = body[span_start:c1e]
    authors = text[:text.rindex("(")].rstrip()
    full_text = body[full_start:c1e]
    full_phrase = full_text[:full_text.rindex("(")].rstrip()
    reduced = authors if full_start != span_start else None
    core = first_core(authors)
    if is_all_caps(core):
        if _non_person_citation(body, span_start, c1e, span_start, c1e,
                                authors, "narrative", sent, heads, cits,
                                non_person_keys):
            return
        _unres(body, span_start, c1e, "all_caps_surname", sent, heads, unres)
        return
    if core.lower() in STOP:
        _unres(body, span_start, c1e, "stopword_surname", sent, heads, unres)
        return
    years = YEAR_RE.findall(body[body.rindex("(", span_start, c1e):c1e])
    for tok in years:
        for y in expand_year(tok):
            _record(body, span_start, c1e, span_start, c1e, text, core, y,
                    "narrative", sent, heads, cits, author_phrase=full_phrase,
                    stop_reduced_phrase=reduced)


def _emit_segment(body, gs, ge, ss, se, seg_text, style, sent, heads, cits,
                  unres, non_person_keys=frozenset()):
    # The cue is not part of the author phrase, and the segment text still
    # carries it. B5's LEAD_IN cues belong here alongside §4's PREFIX cues:
    # without them `(for a review, Smith, 2020)` fell through AUTHORS_PAREN to
    # the split-on-first-comma fallback and reported `for a review` as the
    # author, keying `for|2020`. Longest first so `see also` is not consumed
    # as `see`.
    _CUES = tuple(sorted(set(PREFIX_CUES_CP) | set(LEAD_IN_CUES),
                         key=lambda c: (-len(c), c)))
    m = re.match(rf"\A(?:(?:{'|'.join(re.escape(c) for c in _CUES)})[, ][ \t\n]?)?",
                 seg_text)
    rest = seg_text[m.end():] if m else seg_text
    # The whole AUTHORS_PAREN production, not the text up to the first comma.
    # A comma separates authors as well as authors from year, so cutting at the
    # first one turns "Duru, Therond, and Fares, 2015" into "Duru" — which
    # keys correctly and reports an author_phrase no annotator would write.
    # Scored against a hand-annotated gold set those read as misses, and they
    # were not: the citation was extracted and the phrase was truncated.
    am = re.match(rf"\A{AUTHORS_PAREN}", rest, re.U)
    authors = am.group(0) if am else (rest.split(",")[0] if "," in rest else rest)
    comma = len(authors)
    core = first_core(authors)
    if is_all_caps(core):
        # rc3 B1b. An all-caps head does not satisfy the person grammar, so
        # rc2 §8.1's "otherwise" branch applies and it is a non-person
        # candidate rather than a refusal. `(FAO, 2018)` is in this corpus
        # twice with a matching bibliography entry, and v3.3 refused both.
        if _non_person_citation(body, gs, ge, ss, se, authors.strip(),
                                style, sent, heads, cits, non_person_keys):
            return
        _unres(body, ss, se, "all_caps_surname", sent, heads, unres)
        return
    for tok in YEAR_RE.findall(rest[comma:] if comma > 0 else rest):
        for y in expand_year(tok):
            _record(body, gs, ge, ss, se, seg_text, core, y, style, sent,
                    heads, cits, author_phrase=authors)


ET_AL_CITE = re.compile(r"\bet\s+al\.?|\band\s+colleagues\b", re.I)
# A visible surname inside a citation's author phrase: particles, then a core,
# and NOT one of the joiners or `et al.` itself.
VISIBLE_UNIT = re.compile(
    rf"(?:(?:{PARTICLE}){WS})*[A-ZÀ-Þ][\w'’\-]+", re.U)


def person_form(phrase: str):
    """rc2 §6.7. Returns (author_form, visible_authors, constraint) or Nones.

    §6.7 applies "when the source citation author syntax fully matches the
    person grammar", so a non-person candidate gets three nulls — rc2 says so
    in terms, and a constraint on an organisation would be meaningless.

    Normalization is rc2's: lowercase, internal whitespace collapsed to one
    ASCII space, PARTICLES RETAINED. The last clause matters. `van der maas`
    and `maas` are different authors, and dropping the particle here while
    keeping it in the identity key would make the structure check disagree
    with the key built from the same phrase.
    """
    if not phrase:
        return None, None, None
    et_al = bool(ET_AL_CITE.search(phrase))
    stem = ET_AL_CITE.split(phrase)[0] if et_al else phrase
    # Comma, `&` and `and` all separate authors. Splitting on the joiners
    # alone read `Smith, Jones, and Brown` as two authors, which is worse than
    # useless: it would report a count mismatch against a correct three-author
    # reference.
    # The comma-then-joiner form has to be consumed as ONE separator, longest
    # alternative first. Splitting on the comma alone left `and Brown` as a
    # part, which failed to consume and turned every serial list into a null.
    parts = [p.strip() for p in re.split(
        r"\s*,\s*(?:and|&)\s+|\s*,\s*|\s*&\s*|\s+and\s+", stem, flags=re.I)]
    visible = []
    for part in parts:
        if not part or re.fullmatch(r"(?:[A-Z]\.\s*)+", part):
            continue          # a stray initial, not a surname
        m = VISIBLE_UNIT.fullmatch(part)
        if not m:
            # rc2's discipline from §7.4, applied on this side: a part that
            # does not fully consume as one surname means the list is not
            # confidently derivable, so there is NO structure rather than a
            # partial one. `El Akremi et al.` lands here — a compound surname
            # rc3 B1a would express and this implementation does not — and a
            # partial `['el']` would have produced a false mismatch against a
            # correct reference. rc2 is explicit that a false mismatch is
            # worse than no check, because it teaches a reviewer to ignore
            # the field.
            return None, None, None
        # rc2 §6.8 strips the possessive "only when deriving a person identity
        # candidate surname". `visible_authors` is §6.7 and is not named
        # there, so the literal reading leaves it attached — and that reading
        # produced nine false mismatches on this corpus, every one of the
        # shape `["tepper's"]` against a reference `['tepper']`. A citation
        # written `Tepper's (2000)` is the same author as `Tepper`, and a
        # check that cannot pass on a correct pair is the false mismatch rc2
        # says is worse than no check at all. These ARE surnames used for
        # identity comparison, so §6.8 applies to them.
        visible.append(POSSESSIVE.sub(
            "", re.sub(r"\s+", " ", m.group(0)).strip()).lower())
    if not visible:
        return None, None, None
    if et_al:
        return "et_al", visible, {"kind": "minimum",
                                  "value": ET_AL_MIN_AUTHORS}
    return "exact", visible, {"kind": "exact", "value": len(visible)}


# ----------------------------------------- rc2 §9.4, candidate-level repair
#
# The three rules rc2 gives, in its precedence order. They exist to tell an
# author "you probably meant this entry" without the record ever claiming the
# citation resolved — rc2 is explicit that "neither diagnostic establishes
# `citation_key`, `author_kind`, or `resolved_citation_occurrences`", and
# CIT-ARCH-01 says the same thing from the other direction.
#
# Each is narrow on purpose. A repair rule that fires easily turns a missing
# reference into a confident wrong pairing, which is the failure mode rc2
# guards against everywhere else in this document.

# --------------------------------------- rc2 §15, invariant-injection seam
#
#     The implementation MUST expose a substitutable resolver seam to the
#     conformance harness immediately before the §8.3 decision table.
#
#     The seam may inject, independently for full and STOP-reduced candidates:
#     match_state, candidate_key, reference_indices[].
#
# Why a module attribute and not an argument. §15 is emphatic:
#
#     It MUST NOT be reachable through CLI flags, environment variables,
#     config files, API parameters, or ordinary production dependency
#     injection.
#
# A parameter on `run()` is an API parameter; an env read is an environment
# variable. What is left is a name the harness rebinds after importing the
# module, which no production caller passes and no configuration can set.
#
# WHAT THIS SEAM IS FOR, and it was nearly missed. §8.3's rows 6 to 9 and the
# exit-6 case cannot be reached from a manuscript — the two candidates live in
# different namespaces, so their keys never collide. On 22 September that was
# written up as a defect in rc2: rules that are well formed and unexercisable.
#
# It is not. The conformance matrix marks C-042 through C-047 `injection` in
# its Evidence column, and §15 exists precisely because those states are not
# manuscript-reachable. rc2 anticipated this and supplied the mechanism; the
# cases were unexecuted because this seam was missing, not because rc2 was
# wrong. The Evidence column had the answer the whole time.
_RESOLVER_SEAM = None


# ------------------------------------ rc2 §6.6, the surface grouping key
#
# rc2's architecture gives this its own section — "Surface grouping is not
# identity" — and the execution spec says it twice more: the key "is
# extraction/aggregation only and MUST NOT be consumed by identity resolution
# or reconciliation", and §6.8's possessive stripping "does not modify
# citation_surface_group_key".
#
# So the normalisation here is deliberately weaker than the identity path's,
# and the difference is the whole point:
#
#     Smith and Jones (2020)   ->  ["smith and jones", 2020]
#     Smith & Jones (2020)     ->  ["smith & jones", 2020]      DISTINCT
#     Fine's (1998)            ->  ["fine's", 1998]   identity: fine|1998
#
# Two surfaces that mean one work stay separate here on purpose. Anything
# that collapsed them would be doing identity work under an aggregation name,
# which is the confusion rc2 §7 exists to prevent.
def normalized_author_phrase(phrase: str) -> str:
    """§6.6: lower(), whitespace runs to one ASCII space, trimmed. Nothing
    else — no punctuation, possessive, particle or identity normalisation."""
    return re.sub(r"\s+", " ", phrase).strip().lower()


def surface_year_component(year: str):
    """§6.6. A bare year is a JSON INTEGER; a suffixed year or `nd` is a
    JSON string. The type carries meaning, so `2020` and `"2020"` are not
    interchangeable and the serializer must not quote the first."""
    return int(year) if year.isdigit() else year


def surface_group_key(phrase: str, year: str) -> list:
    """§6.6's JSON array, emitted as an array and never as a quoted string."""
    return [normalized_author_phrase(phrase), surface_year_component(year)]


def _osa(a: str, b: str) -> int:
    """Optimal string alignment distance. rc2 §1.4 names `osa` by that name."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    prev2, prev = None, list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            if (i > 1 and j > 1 and a[i - 1] == b[j - 2]
                    and a[i - 2] == b[j - 1]):
                cur[j] = min(cur[j], prev2[j - 2] + 1)
        prev2, prev = prev, cur
    return prev[lb]


def _year_transposed(a: str, b: str) -> bool:
    """One adjacent digit pair swapped, and nothing else."""
    if len(a) != len(b) or not (a.isdigit() and b.isdigit()) or a == b:
        return False
    for i in range(len(a) - 1):
        if a[:i] + a[i + 1] + a[i] + a[i + 2:] == b:
            return True
    return False


def _split_key(key: str):
    """A key back into (kind, phrase, year).

    v3.3 keys are `surname|year` and rc2's non-person keys are
    `non_person|label|year`. Both shapes are live at once while CIT-ARCH-01's
    key migration is outstanding, so this reads either rather than assuming
    the prefix is there.
    """
    parts = key.split("|")
    if len(parts) == 3 and parts[0] in ("person", "non_person"):
        return parts[0], parts[1], parts[2]
    return "person", parts[0], parts[-1]


def repair_rule(cand_kind, cand_phrase, cand_year,
                ref_kind, ref_phrase, ref_year):
    """rc2 §9.4: the rule qualifying this pair, or None.

    Alex Zamurko, 21 September 2026, amending §9.4. "Rules, in precedence
    order" and "take the first rule that matches" are replaced by:

        A candidate/reference pair qualifies when EXACTLY ONE of the following
        rules matches. [...] Take the first qualifying REFERENCE in source
        order.

    Precedence between rules is gone; ordering now lives entirely on the
    reference scan, which is where §9.4 always had it and where this file
    always implemented it.

    Written as a literal count rather than a short-circuit return. The
    short-circuit form is behaviourally identical here — see the suite for why
    two rules cannot both match — but it encodes "the first that matches",
    which is the sentence the amendment removed.
    """
    # "A pair MUST have the same candidate/reference author kind."
    if cand_kind != ref_kind:
        return None

    matched = []
    # 1. surname_edit_distance_1 — person only, same year, CORE >= 4.
    if (cand_kind == "person" and cand_year == ref_year
            and len(cand_phrase) >= 4
            and _osa(cand_phrase, ref_phrase) <= 1
            and cand_phrase != ref_phrase):
        matched.append("surname_edit_distance_1")
    if cand_phrase == ref_phrase:
        # 2. year_adjacent — both numeric, difference exactly one.
        if (cand_year.isdigit() and ref_year.isdigit()
                and abs(int(cand_year) - int(ref_year)) == 1):
            matched.append("year_adjacent")
        # 3. year_transposition — one adjacent digit pair swapped.
        if _year_transposed(cand_year, ref_year):
            matched.append("year_transposition")

    # "EXACTLY ONE". Zero is no pair, and two would be an ambiguous repair,
    # which under this wording is also no pair rather than a contest to settle.
    return matched[0] if len(matched) == 1 else None


def _record(body, gs, ge, ss, se, seg_text, core, year, style, sent, heads,
            cits, author_phrase="", author_kind="person",
            stop_reduced_phrase=None):
    s_start, s_end, s_content_end, s_index, s_prev_end = sent
    lv, nm, ty, rs = section_stack_at(heads, gs)
    surname = re.sub(r"\s+", " ", core).strip().lower()
    y = norm_year(year)
    # rc2 §7.5. The non-person key is the COMPLETE label, never its last token
    # — `world bank`, never `bank`. rc3 §G makes that a conformance case, and
    # it is the whole reason the institutional path is keyed separately rather
    # than fed through the surname grammar.
    key = f"non_person|{surname}|{y}" if author_kind == "non_person" \
        else f"{surname}|{y}"
    cits.append({
        "type": "citation", "index": 0,
        # Not in v3.3's §9 contract. Emitted because a gold set annotated by
        # hand keys on the author phrase as written, and deriving a surname
        # from it is the grammar under test: scoring against a key this
        # extractor derived would have it agree with itself. rc3 §A makes
        # author_phrase mandatory for the same reason, so this is forward
        # compatible rather than an invention.
        "author_phrase": re.sub(r"\s+", " ", author_phrase).strip(),
        # rc2 §6.3, C-019 and C-020. Reduction is ADDITIVE: `author_phrase`
        # above is `full_phrase`, the complete collected C2 text, and the
        # reduced form lives here rather than overwriting it.
        #
        # Until 22 September the reduced form WAS author_phrase and the lead-in
        # tokens were dropped, on 20 of 368 narrative occurrences. That
        # satisfied the gold set, which annotates author names only, and broke
        # rc3 §A, which says author_phrase "always records the complete source
        # candidate phrase before STOP reduction". Both fields exist now, and
        # `citation_candidate.py` selects the one gold actually annotates.
        #
        # 20, measured from this field. A first estimate said 129, counted by
        # looking for discardable text between `sentence_start` and
        # `group_start` — which finds prose the C2 walk never collected. The
        # loose probe overstated by six times, and the number reached two
        # docstrings before the real one was available. Fourth of its kind
        # this week; see UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md.
        "stop_reduced_phrase": (re.sub(r"\s+", " ", stop_reduced_phrase).strip()
                                if stop_reduced_phrase else None),
        # §6.6. Built from `author_phrase` and the normalized year, and from
        # nothing the identity path touches — see the note above the helper.
        "citation_surface_group_key": surface_group_key(author_phrase, y),
        # rc2 §6.7. Null for a non-person candidate, per the section's own
        # last line.
        **dict(zip(("author_form", "visible_authors", "author_count_constraint"),
                   person_form(author_phrase)
                   if author_kind == "person" else (None, None, None))),
        # rc2's citation schema declares this and never says what it holds
        # when identity IS resolved — §8.3 only ever sets it to null, for
        # not_resolved and for ambiguous. The reading taken here is the
        # phrase that established the identity, which the §8 block fills in
        # once resolution has run; null until then, and null for good in the
        # cases rc2 names.
        "resolved_author_phrase": None,
        "candidate_state": "parsed",
        "citation_group": body[gs:ge], "citation_segment": seg_text,
        "citation_key": key, "author_kind": author_kind,
        "surname": surname, "year": y,
        "style": style,
        "group_start": gs, "group_end": ge,
        "segment_start": ss, "segment_end": se,
        "sentence": body[s_start:s_end], "sentence_start": s_start,
        # rc2 §6, the sentence-relative fields. C-026 to C-028.
        "sentence_index": s_index,
        "previous_sentence_end": s_prev_end,
        # "standalone = true iff group_start == sentence_start AND
        # group_end == content_end", and §6 is emphatic about what it is not:
        # "`standalone` is positional only. It does not infer which claim the
        # citation supports." A sentence that is nothing but a citation.
        "standalone": gs == s_start and ge == s_content_end,
        "sentence_position": ("start" if gs == s_start else
                              "end" if ge == s_content_end else "middle"),
        "section_level": lv, "section_name": nm, "section_type": ty,
        "section_roles": rs,
    })


# ------------------------------------------------- rc3 §C, citation errors
#
# A diagnostic class, not a limitation. rc3:
#
#     `citation_error` is ORTHOGONAL to `candidate_state`. A malformed group
#     MAY be `parsed` or `unresolved_citation`, depending on whether a valid
#     citation was extracted from it. It MUST NOT be `excluded_candidate` —
#     malformed input is not correct refusal.
#
#     The grammar MUST NOT be loosened to accept these forms. The record names
#     what is wrong so an author can fix it.
#
# And C1, which rc3 calls "the part a naive implementation gets wrong":
#
#     One `citation_error` record per parenthetical group, carrying a list of
#     defects. NEVER one record per defect.
#
# The reason is the reader, not the schema. `(Gualandris, et al., 2024; p.56)`
# has two defects; as two records an author sees two unrelated problems and
# fixes neither.
CITATION_ERROR_DEFECTS = (
    "et_al_punctuation",           # 9   Whiteman et al, 2013 · Choi at al.
    "wrong_locator_separator",     # 2   (Barbier, 2022; P.923)
    "missing_comma_before_year",   # 2   (Lu and Shang 2017)
    "non_numeric_year",            # 1   (Smith, Weed, & Ramsay, 2005-present)
)

# Three shapes, all `et_al_punctuation`:
#   a missing period      Whiteman et al, 2013
#   the `at` typo         Choi at al., 2001
#   a comma before it     Gualandris, et al., 2024
#
# The third is rc3's own two-defect exemplar and was missed at first, because
# `(Gualandris, et al., 2024; p.56)` has its period and reads as correct. The
# defect is the comma between the surname and `et al.`, which APA does not
# take. rc3 lists that group as carrying et_al_punctuation AND
# wrong_locator_separator, and without this shape it carried only one — the
# case rc3 uses to distinguish a case count from a defect count would have
# been indistinguishable from the single-defect one.
ERR_ET_AL = re.compile(
    r"\bet[ \t]+al(?![.\w])|\bat[ \t]+al\.|,[ \t]*et[ \t]+al\.", re.I)
# C2: "`p.56` with no space matches, so the semicolon is the SOLE locator
# defect in both cases — one character." And: "`P.923` matches only because
# the pattern is applied case-insensitively. That dependency is load-bearing
# and should be explicit in the rule rather than inherited from a flag." So
# the case-insensitivity is written here rather than carried by re.I over the
# whole module.
ERR_LOCATOR_SEP = re.compile(r";[ \t]*(?:[Pp]{1,2}|[Pp]ara|[Cc]hap)\.[ \t]*\d")
# A year sitting directly after the author phrase with no comma. The word
# before it must be capital-initial and not a STOP word, or the rule fires on
# things that are not authors at all: `(running since 2005)` and the
# `(2011, 2012, and 2013)` §F names as a non-citation year were both reported
# before this narrowed, because `since` and `and` sit in the same position a
# surname does.
ERR_NO_COMMA_YEAR = re.compile(
    r"(?<![,;])\b([A-ZÀ-Þ][\w'’\-]+)\)?[ \t]+(?:1[5-9]|20)\d{2}[a-z]?[ \t]*[);,]")
# A year whose range end is not a year. rc3's instance is `2005-present`.
ERR_NON_NUMERIC_YEAR = re.compile(
    r"(?:1[5-9]|20)\d{2}[ \t]*[–—-][ \t]*(?!\d)[A-Za-z]")


def citation_errors(group: str) -> list[str]:
    """rc3 §C's defects for ONE parenthetical group, in declaration order.

    Order is fixed rather than discovery order so two implementations emit the
    same list for the same group, which §9's determinism claim needs.

    Four of rc3's seven defect classes are detected. `wrong separator` (4),
    `prose-embedded citation` (1) and `incomplete citation` (1) are named in
    the table with an example apiece and no rule, and the same discipline
    applies as to A2's undefined exclusion reasons: the vocabulary is kept and
    nothing is emitted under it. See RC2-RC3-DISCREPANCIES.md.
    """
    found = []
    if ERR_ET_AL.search(group):
        found.append("et_al_punctuation")
    if ERR_LOCATOR_SEP.search(group):
        found.append("wrong_locator_separator")
    m = ERR_NO_COMMA_YEAR.search(group)
    if m and m.group(1).lower() not in STOP:
        found.append("missing_comma_before_year")
    if ERR_NON_NUMERIC_YEAR.search(group):
        found.append("non_numeric_year")
    return [d for d in CITATION_ERROR_DEFECTS if d in found]


def _non_person_citation(body, gs, ge, ss, se, phrase, style, sent, heads,
                         cits, non_person_keys) -> bool:
    """rc3 B1b, the citation side. ONE production, reused from rc2 §7.4.

    rc2 §8.1:

        if `author_phrase` fully matches the applicable person citation
        grammar: `candidate_key = person|<first visible surname>|<year>`;
        otherwise: `candidate_key = non_person|<normalized complete
        author_phrase>|<year>`.

    rc3 B1b changes only where the detector is allowed to propose such a
    phrase. The test applied to the phrase is `non_person_head`, the same
    function the bibliography side calls, because rc3 says restating the rules
    here "would create a second definition that can disagree with the first".

    Returns True when a citation was emitted.
    """
    label = non_person_head(phrase)
    if not label:
        return False
    years = YEAR_RE.findall(body[ss:se])
    if not years:
        return False
    # rc2 §8: the bibliography, not the syntax, is what makes this a citation.
    if not all(f"non_person|{label}|{norm_year(y)}" in non_person_keys
               for y in years):
        return False
    for y in years:
        _record(body, gs, ge, ss, se, body[ss:se], label, norm_year(y),
                style, sent, heads, cits, author_phrase=phrase,
                author_kind="non_person")
    return True


def _unres(body, start, end, reason, sent, heads, unres):
    s_start, s_end = sent[:2]
    lv, nm, _, _ = section_stack_at(heads, start)
    unres.append({
        "type": "unresolved_citation", "index": 0,
        # rc3 A1. `type` already said this, but A1 makes the terminal state a
        # named field on every candidate so the three states can be counted
        # uniformly without knowing which record shapes exist.
        "candidate_state": "unresolved_citation",
        "text": body[start:end], "start": start, "end": end, "reason": reason,
        # §12's unresolved_citation shape carries the field as null. It has to
        # be PRESENT and null rather than absent: a consumer aggregating by
        # surface group needs the key on every extracted candidate record, and
        # an unresolved one has no author phrase to build it from.
        "citation_surface_group_key": None,
        "sentence": body[s_start:s_end], "sentence_start": s_start,
        "section_level": lv, "section_name": nm,
    })


def _excl(body, start, end, reason, sent, heads, excl):
    """rc3 A1's third terminal state. NOT a failure: it records that detection
    proposed a span and the grammar was right to decline it."""
    if reason not in EXCLUDED_REASONS:
        raise AssertionError(f"excluded_reason not in rc3 A2's closed set: "
                             f"{reason!r}")
    lv, nm, _, _ = section_stack_at(heads, start)
    rec = {
        "type": "excluded_candidate", "index": 0,
        "candidate_state": "excluded_candidate",
        "text": body[start:end], "start": start, "end": end,
        "excluded_reason": reason,
        "section_level": lv, "section_name": nm,
    }
    # A candidate above the first heading has no sentence under §5, which is
    # how the journal's "To cite this article:" line reaches here. The record
    # is emitted either way — A4's case is that it must not be absent.
    if sent is not None:
        rec["sentence"] = body[sent[0]:sent[1]]
        rec["sentence_start"] = sent[0]
    excl.append(rec)


# ---------------------------------------------------------------- §7

# --------------------------------------------- rc2 §7.4, non-person authors
#
# rc3 B1b is worth 8 citations and rc3 forbids writing it from rc3 alone:
#
#     The citation-side `NON_PERSON_AUTHOR` path MUST reuse the exact lexical
#     production and boundary rules rc2 defines for the bibliography-side
#     `NON_PERSON_AUTHOR`. rc3 changes the permitted DETECTION SITE only. It
#     does not introduce a second organisational-author grammar.
#
#     Two grammars for one object is how the boundaries drift.
#
# rc2 arrived 21 September. §7.4 is that production, and this is it:
#
#     `reference_author_head` is the trimmed text before the opening `(`
#     immediately containing the first YEAR token, with one trailing period
#     removed and trailing whitespace trimmed.
#
#     If neither person path applies, a non-person head is accepted only if:
#     it contains at least one Unicode letter; it contains no comma; after
#     trimming it is non-empty.
#
# The no-comma rule is the whole safeguard, and rc2 says why: "A
# comma-containing organization author that cannot be distinguished from an
# unsupported person-list form is therefore unresolved rather than guessed."
# Nothing here knows that the IMF is an institution. It knows the head has no
# comma and so cannot be a person list.
#
# ONE DISCREPANCY, recorded rather than resolved. rc3 says rc2's production
# "already carries the bound, the terminal-period handling and the maximum
# label length". §7.4 carries the first two. There is no maximum label length
# in rc2 at all, so none is implemented here, and a length bound is the kind
# of constant that must come from the spec rather than from whoever is typing.

def reference_author_head(assembled: str):
    """rc2 §7.4's head, or None when the entry has no usable year paren."""
    for m in re.finditer(r"\(", assembled):
        rest = assembled[m.start():]
        close_at = rest.find(")")
        if close_at < 0:
            continue
        if not YEAR_RE.search(rest[:close_at + 1]):
            continue
        head = assembled[:m.start()].rstrip()
        # rc2 §7.4: "with one trailing period removed". Taken literally that
        # rule defeats rc2's own primary path, and this was found by running
        # it rather than by reading it: only 1 of 1036 corpus references
        # produced an author list.
        #
        #     `Bartko, J. (1976).`  head -> `Bartko, J.`  -> strip -> `Bartko, J`
        #     rc2 §2: INITIALS = \p{Lu}\.(?:[- ]?\p{Lu}\.)*
        #
        # The period that was removed IS the initial, so the person unit
        # `SURNAME, WS INITIALS` can never match and every person reference
        # falls through to the non-person branch. rc2 §7.4 also says the list
        # must consume the head "after ordinary separator punctuation
        # normalization", which may be where the original intended to resolve
        # this, but that phrase is nowhere defined.
        #
        # So the period is removed only when it does not belong to an initial.
        # `World Bank.` still loses it, which is the case the rule exists for.
        if head.endswith(".") and not re.search(r"(?:^|[ \-])[A-ZÀ-Þ]\.$", head):
            head = head[:-1]
        return head.rstrip()
    return None


# ------------------------------------- rc2 §6.7 / §7.4 / §9.3, author structure
#
# The defect this closes, in rc2's own framing and measured here on 21
# September: §8 reconciles on `surname|year` and discards everything else the
# in-text form asserts. `Smith et al. (2020)` asserts a work with three or more
# authors; a reference reading `Smith, J. (2020).` has the identical key and
# matches cleanly. Two different works, and nothing in the output says so.
#
# 790 of this corpus's 2094 citations carry `et al.` or `and colleagues`, so
# the form is not rare. The check is what is missing, not the cases.
#
# rc2 §1.1 pins the constant rather than leaving it to the implementation,
# because older APA and several other styles begin `et al.` at a different
# author and an implementation that picks its own value produces different
# output from the same bytes.
ET_AL_MIN_AUTHORS = 3

# rc2 §7.4's person unit: SURNAME, WS INITIALS, separated by comma, `&` or
# `and`, and it must consume the entire head. Anything less is not a
# confidently derivable list, and rc2 says a null "takes no part in the check"
# — a false mismatch against a pair that genuinely matched is worse than no
# check at all, because it teaches a reviewer to ignore the field.
_PERSON_UNIT = rf"(?:(?:{PARTICLE})[ ])*{CORE},[ ]{INITIALS}"
PERSON_LIST_UNIT = re.compile(_PERSON_UNIT, re.I | re.U)
# `and` MUST be followed by whitespace. Written first as `(?:&|and)\s*`, which
# let the joiner glue onto the next name: `Faems, D., De Visser, M., Andries,
# P.` split as `... and` + `ries, P.` and reported `ries` as an author. It then
# disagreed with the citation's `andries` and emitted a mismatch that was
# entirely this regex's doing. `&` needs no such guard.
PERSON_LIST_SEP = re.compile(
    r"\A\s*(?:,\s*&\s*|,\s*and\s+|,\s*|\s*&\s*|\s+and\s+)", re.I)


def reference_authors(head: str):
    """rc2 §7.4's ordered surname list, or None when not confidently derivable.

    None is a deliberate output, not a failure to try. rc2 reaches it for a
    full-forename reference such as `Smith, John. (2020).` and for any entry
    whose author field contains `et al.` itself, and in both cases the entry
    takes no part in author-structure validation.
    """
    if head is None or re.search(r"\bet\s+al", head, re.I):
        return None
    out, pos = [], 0
    while pos < len(head):
        m = PERSON_LIST_UNIT.match(head, pos)
        if not m:
            return None
        got = m.group(0)
        out.append(re.sub(r"\s+", " ", got[:got.index(",")]).strip().lower())
        pos = m.end()
        if pos >= len(head):
            break
        sep = PERSON_LIST_SEP.match(head[pos:])
        if not sep:
            return None
        pos += sep.end()
    # "it must consume the entire reference_author_head"
    return out or None


def non_person_head(head: str):
    """rc2 §7.4's three conditions. Returns the normalised label, or None."""
    if head is None:
        return None
    if "," in head:
        return None
    if not any(c.isalpha() for c in head):
        return None
    label = re.sub(r"\s+", " ", head).strip().lower()
    return label or None


def assemble_references(section: str, base: int):
    refs, unres = [], []
    open_entry = None

    def close():
        nonlocal open_entry
        if open_entry is None:
            return
        start, end, parts = open_entry
        assembled = " ".join(parts)
        m = ENTRY_START.match(assembled)
        surname = ""
        if m:
            got = m.group(0)
            surname = re.sub(r"\s+", " ", got[:got.index(",")]).strip().lower()
        ym = YEAR_RE.search(assembled)
        year = norm_year(ym.group(0)) if ym else None

        # rc2 §7.4, the person path first and only then the non-person one.
        # The order is rc2's and it is load-bearing: `Van Den Brink, T. W., &
        # van Der Woerd, F. (2004)` satisfies the person grammar and must
        # never be read as an organisation merely because its author field
        # holds several words.
        author_kind = "person" if surname else None
        label = None
        head = reference_author_head(assembled)
        # rc2 §7.4: the ordered list where it is derivable, null otherwise. It
        # is what §9.3 compares the in-text form against, and a null is not a
        # gap — it is the entry declining to take part.
        authors = reference_authors(head) if surname else None
        if not surname:
            label = non_person_head(head)
            if label and year:
                author_kind = "non_person"

        reasons = []
        if not ym:
            reasons.append("no_year")
        if not re.search(r"(?:\.|\?|\d+[–—-]\d+\.?|(?:doi:|https?://)\S+)$",
                         assembled):
            reasons.append("terminator")
        if len(assembled) > 1500:
            reasons.append("overlong")
        em = re.search(rf"\. (?:(?:{PARTICLE}) )*{CORE}, (?:[A-Z]\. ?)+", assembled)
        if em and em.start() > 10:
            reasons.append("embedded_entry_pattern")
        # rc2 §7.5 keys non-person entries `non_person|<label>|<year>`. Person
        # entries keep v3.3's bare `surname|year` rather than gaining rc2's
        # `person|` prefix: the prefixed form changes every existing key, every
        # gold set and every conformance case asserting one, and that is the
        # consolidation's decision rather than this change's. The namespaces
        # cannot collide — a v3.3 surname never contains `|`, and rc2 §7.5's
        # escaping exists for exactly that reason — so this is additive.
        if author_kind == "non_person":
            ref_key = f"non_person|{label}|{year}"
        elif surname and year:
            ref_key = f"{surname}|{year}"
        else:
            ref_key = None

        # C-030, and §7.3's closed list. An entry with no year is an
        # `unresolved_reference`, not a keyless `reference` — the case says
        # "no reference row/key" in as many words, and §7.3's `suspect_reasons`
        # list for EMITTED references is closed at three: terminator,
        # overlong, embedded_entry_pattern. `no_year` is not among them; it
        # belongs to §6.4's unresolved-reference reasons.
        #
        # This emitted a reference row carrying `no_year` in its
        # suspect_reasons and a null key. One entry corpus-wide reaches it —
        # `Bhattacharjee, A., Dana, J., & Baron, J. In press.` — which is
        # exactly the shape the rule is for: a real reference whose year does
        # not exist yet.
        if not ym:
            unres.append({
                "type": "unresolved_reference", "index": 0,
                "reason": "no_year", "text": assembled,
                "start": start, "end": end,
            })
            open_entry = None
            return

        refs.append({
            "type": "reference", "index": 0, "assembled": assembled,
            "reference_key": ref_key,
            "author_kind": author_kind,
            "authors": authors,
            "author_count": len(authors) if authors else None,
            # rc2 §7.4 names this `identity_author_phrase`: "authors[0]" for
            # a person entry, "normalized leading SURNAME" otherwise. It was
            # called `surname` here, which is the same value under a name
            # that stops being accurate the moment the entry is
            # institutional. Nothing downstream read it.
            "identity_author_phrase": surname,
            "year": year, "start": start, "end": end,
            "validation_state": "suspect" if reasons else "ok",
            "suspect_reasons": reasons,
        })
        open_entry = None

    pos = 0
    for line in section.split("\n"):
        lstart, lend = pos, pos + len(line)
        pos = lend + 1
        stripped = line.strip(" \t")
        if not stripped:
            close()
            continue
        off = lstart + (len(line) - len(line.lstrip(" \t")))
        span = (base + off, base + off + len(stripped))
        if HEAD_MD.match(line) or HEAD_HTML.match(line):
            close()
            continue
        if ENTRY_START.match(stripped):
            close()
            open_entry = (span[0], span[1], [stripped])
            continue
        # §7.4 entry-candidate guard: stops out-of-grammar entry starts from
        # wrap-joining into the entry above them.
        head = re.sub(rf"^(?:(?:{PARTICLE})[ ])*", "", stripped, flags=re.I)
        if head[:1].isupper() and (
                re.search(r"\((?:(?:1[5-9]|20)\d{2}|n\.d\.)", stripped[:100])
                or re.match(r"^[^.\n]{2,60}\.[ \t]+\(?(?:(?:1[5-9]|20)\d{2}|n\.d\.)",
                            stripped)):
            close()
            # rc2 §7.4: before refusing, try the non-person path. Four corpus
            # entries land here and every one is an institution the person
            # grammar cannot express — International Monetary Fund, Population
            # Pyramid, National Statistical Institute, World Bank. They were
            # `unresolved_reference` with `entry_start_grammar`, which is the
            # reason rc2 keeps for a head that satisfies NO path; these satisfy
            # one.
            if non_person_head(reference_author_head(stripped)):
                open_entry = (span[0], span[1], [stripped])
                continue
            unres.append({"type": "unresolved_reference", "index": 0,
                          "text": stripped, "start": span[0], "end": span[1],
                          "reason": "entry_start_grammar"})
            continue
        if open_entry is None:
            unres.append({"type": "unresolved_reference", "index": 0,
                          "text": stripped, "start": span[0], "end": span[1],
                          "reason": "orphan_line"})
            continue
        s, _, parts = open_entry
        open_entry = (s, span[1], parts + [stripped])
    close()
    return refs, unres


# ---------------------------------------------------------------- cli

FIXES = ("ampersand", "segments", "colon", "cp", "mathyear")


def run(path: Path, fixes: set[str]) -> tuple[list[dict], int]:
    text = normalise(path.read_bytes())
    body, section, sec_off, heads, ref_source = split_body_and_references(text)
    if "ampersand" in fixes:
        body = body.replace("\\&", "&")
        section = section.replace("\\&", "&")
    if "mathyear" in fixes:
        # rc3 §J fixes the order: ampersand first, then this. The two are
        # independent — a year-only span contains no ampersand — but rc3 pins
        # it anyway, "because two orders that happen to agree today are still
        # two orders".
        body = unwrap_math_years(body)
    sents = sentences(body)

    # rc2 §8 runs citation identity AFTER the bibliography, because authority
    # comes from the reference list rather than from citation syntax. v3.3
    # assembled references last, which was fine while every key was
    # `surname|year` derived at extraction; the non-person path cannot work
    # that way and rc2 says so in terms. The references are assembled here and
    # reused below, so nothing is parsed twice.
    refs, ref_unres = assemble_references(section, sec_off)
    non_person_keys = frozenset(
        r["reference_key"] for r in refs
        if r.get("author_kind") == "non_person" and r["reference_key"])

    cits, unres, excl, errs = extract_citations(body, sents, heads, fixes,
                                                non_person_keys)

    # §10 exit 2, computed on the body and the parse count.
    n = len(NUMCITE.findall(body)) + len(SUPCITE.findall(body))
    if n >= 3 and n > 10 * len(cits):
        raise Abort(2, "unsupported citation style")

    share, total = comma_less_share(body)
    if total >= STYLE_MIN_SAMPLE and share > STYLE_COMMA_LESS_MAX:
        raise Abort(2, f"unsupported citation style: {share:.0%} of "
                       f"{total} author-year parentheticals omit the comma "
                       f"before the year, which is author-date rather than "
                       f"APA")

    lines = [{"type": "meta", "spec_version": SPEC_VERSION,
              "implementation": "scripts/citation_extract.py",
              "fixes_applied": sorted(fixes),
              # rc2 §2: "canonical_sha256 is lowercase hexadecimal SHA-256
              # over exactly canonical_manuscript_bytes" — the INPUT after
              # newline and NFC normalisation, not the output. No circularity,
              # which is what lets §13 name an output file after it.
              "canonical_sha256": hashlib.sha256(
                  text.encode("utf-8")).hexdigest(),
              # rc2 §6.2, C-006 and C-007. Whether the bibliography was found
              # by a marked-up heading, inferred from a bare `References`
              # line, or absent entirely is a property of the run, and a
              # reader cannot otherwise tell an inferred boundary from a
              # declared one.
              "references_source": ref_source}]
    absent = ref_source == "not_available"

    # rc2 §12.4, total deterministic order:
    #
    #     citation  (group_start, segment_start, year,
    #                canonical bytes of citation_surface_group_key)
    #
    # Sorted HERE, before `index` is assigned, because §12.4 also says "index
    # is 0-based per record type in serialized order" and several later record
    # types carry a `citation_index` pointing back at it. Sorting after
    # indexing would leave those pointing at the wrong rows.
    #
    # Only multi-year groups move. Extraction already walks the body left to
    # right, so `(group_start, segment_start)` is ascending by construction —
    # but `(Smith, 2021, 2020)` emitted 2021 first, tied on both positions,
    # with the `year` key that breaks the tie never applied. §12.4's whole
    # point is that "two distinct records may not remain tied on every
    # declared key", and those two were.
    cits.sort(key=lambda c: (
        c["group_start"], c["segment_start"], c["year"],
        json.dumps(c["citation_surface_group_key"],
                   separators=(",", ":"), ensure_ascii=False).encode("utf-8")))

    for i, c in enumerate(cits):
        c["index"] = i
        if absent:
            # §10, verbatim. Identity was not evaluated, so nothing may claim
            # it was — and `not_evaluated` is a different statement from
            # `not_resolved`, which is why rc2 gives it its own value.
            c["author_kind"] = "undetermined"
            c["resolved_author_phrase"] = None
            c["author_resolution"] = "not_evaluated"
            c["citation_key"] = None
            # C-066: "bibliography_absent uses not_evaluated identity state".
            # A fourth value beside the three §9.2 assigns, and it has to be
            # distinct from `identity_not_resolved` — that one means the
            # lookup ran and matched nothing.
            c["identity_class"] = "not_evaluated"
            c["candidate_key"] = None
            c["match_state"] = None
            c["reference_indices"] = []
            # "citation_surface_group_key = computed" — the one identity-ish
            # field that survives, because it is a surface property and never
            # needed the bibliography. C-025's "always emitted" is this half.
    for i, u in enumerate(unres):
        u["index"] = i
    for i, x in enumerate(excl):
        x["index"] = i
    for i, e in enumerate(errs):
        e["index"] = i
    # §10's suppression list. Nine types must not be emitted when the
    # bibliography is absent; `reference` and `unresolved_reference` are the
    # two that could otherwise come from an empty section, and the remaining
    # seven are guarded where they are built.
    refs_out = [] if absent else refs
    ref_unres_out = [] if absent else ref_unres
    for i, r in enumerate(refs_out):
        r["index"] = i
    for i, u in enumerate(ref_unres_out):
        u["index"] = i
    # "one bibliography_absent" — C-009. The record says the manuscript was
    # read and the bibliography was not there, which is a different claim from
    # the run having failed.
    bib_absent = [{"type": "bibliography_absent", "index": 0,
                   "references_source": "not_available",
                   "identity_resolution_performed": False}] if absent else []

    # §10: "Pass 2 identity resolution — not evaluated". With no references,
    # every lookup would be `no_match` and every occurrence would come out
    # `identity_not_resolved` — which reads as "we looked and found nothing"
    # when the truth is that we never looked. rc2 separates those two states
    # deliberately, so the whole block is skipped rather than allowed to
    # produce a confident-looking wrong answer.
    if absent:
        refs = []
    keyed = {r["reference_key"] for r in refs if r["reference_key"]}
    cite_keys = []
    for c in cits:
        if c["citation_key"] not in cite_keys:
            cite_keys.append(c["citation_key"])
    matched = [c for c in cits if c["citation_key"] in keyed]

    # ------------------------------------------- rc2 §8.2 and §8.3, identity
    #
    # Alex Zamurko, 21 September, Decision CIT-ARCH-01:
    #
    #     In-text citation evidence may generate and narrow candidate
    #     reference identities, but it may not independently confirm reference
    #     identity. A citation is CONFIRMED only when it matches a compatible
    #     reference-list entry. If no compatible entry exists, classify it as
    #     MISSING_REFERENCE while preserving the citation-derived candidate.
    #     If multiple compatible entries remain, classify it as AMBIGUOUS; do
    #     not guess.
    #
    # §8.2 gives the lookup result and §8.3 the exhaustive 3×3 table over the
    # full candidate's match state F and the STOP-reduced candidate's S.
    #
    # ONLY THE FIRST COLUMN IS REACHABLE HERE, and saying so matters more than
    # implementing the rest would. rc2 §6.3's additive STOP reduction is
    # C-019 and is not implemented, so no STOP-reduced candidate is ever
    # produced and §8.3's own rule applies: "If no STOP-reduced candidate
    # exists, S is no_match." Six of the nine rows need S to be something
    # else. Writing them would be writing code no input can reach, which this
    # session has already deleted once tonight.
    #
    #     F=no_match   S=no_match   not_resolved, citation_key null
    #     F=unique     S=no_match   full_phrase, the key is authoritative
    #     F=nonunique  S=no_match   same key, and emit ambiguous_citation
    #
    # ADDITIVE. `citation_key` keeps v3.3's meaning for now and the new fields
    # sit beside it, because retiring it changes both gold sets, the candidate
    # adapter and every control asserting a key. What the record must not do
    # is claim both things silently, so `identity_class` says plainly whether
    # that key has been confirmed by a reference.
    ref_index_by_key: dict[str, list[int]] = {}
    for i, r in enumerate(refs):
        if r["reference_key"]:
            ref_index_by_key.setdefault(r["reference_key"], []).append(i)

    def _lookup(key):
        """§8.2. One candidate's match state and its ascending index array."""
        if key is None:
            return "no_match", []
        idx = sorted(ref_index_by_key.get(key, []))
        return ("no_match" if not idx else
                "unique" if len(idx) == 1 else "nonunique"), idx

    ambiguous_citations = []
    ambiguous_authors = []
    for c in (cits if not absent else []):
        # §8.1. Two candidates now, where there was one.
        #
        # `citation_key` has always been derived from the phrase that PARSED,
        # which after §6.3 is the reduced one. So the key this file has been
        # carrying is rc2's SECOND candidate, and the full-phrase candidate —
        # the one §8.1 names first — was never built at all. That is why every
        # reduced occurrence reported `author_resolution = full_phrase`: the
        # only candidate present was labelled with the only label implemented.
        reduced_key = c["citation_key"] if c.get("stop_reduced_phrase") else None
        if reduced_key:
            # §8.1's full candidate, built from author_phrase. A lead-in makes
            # the complete phrase fail the person grammar, so it keys
            # non-person over the whole surface and finds nothing — which is
            # the correct answer, not a failure.
            surface = re.sub(r"\s+", " ", c["author_phrase"]).strip().lower()
            full_key = f"non_person|{surface}|{c['year']}"
        else:
            full_key, reduced_key = c["citation_key"], None

        # rc2 §15's seam sits exactly here: "immediately before the §8.3
        # decision table". Production leaves `_RESOLVER_SEAM` None and binds
        # the deterministic real resolver below.
        f_state, f_idx = _lookup(full_key)
        s_state, s_idx = _lookup(reduced_key)
        if _RESOLVER_SEAM is not None:
            (full_key, f_state, f_idx), (reduced_key, s_state, s_idx) = \
                _RESOLVER_SEAM((full_key, f_state, f_idx),
                               (reduced_key, s_state, s_idx))

        # §8.3's table. Rows 6 to 9 are the ones where BOTH candidates match,
        # and rc2 splits them on whether the two keys are the same string.
        #
        # No corpus input reaches either, but one can be BUILT — a
        # bibliography carrying both `From Tether (2018). A report.` and
        # `Tether, B. (2018).` gets there. That is why these are implemented
        # rather than left as an abort: reachable-in-principle code that
        # refuses where the spec says carry on is a defect waiting for the
        # manuscript that triggers it, not a safe simplification.
        if f_state != "no_match" and s_state != "no_match":
            # §8.6, verbatim: "If both full and STOP-reduced lookups are
            # non-empty and serialize the same candidate key, abort." The
            # section is explicit that this is "a system failure, not a
            # manuscript diagnostic" — one occurrence resolved twice to one
            # identity means the two-candidate construction itself is broken.
            if full_key == reduced_key:
                raise Abort(6, "same_candidate_identity_double_resolution")

            # Different keys: ambiguous. §8.3 lists exactly what is NOT
            # established, and CIT-ARCH-01 says why — two compatible entries
            # remain and the rule is "do not guess".
            c["candidate_key"] = None
            c["candidate_key_full"] = full_key
            c["candidate_key_stop_reduced"] = reduced_key
            c["match_state"] = "ambiguous"
            c["match_state_full"] = f_state
            c["match_state_stop_reduced"] = s_state
            c["reference_indices"] = []
            c["author_resolution"] = "ambiguous"
            c["identity_class"] = "author_resolution_ambiguous"
            c["author_kind"] = "undetermined"
            c["resolved_author_phrase"] = None
            c["citation_key"] = None
            # "Emit exactly one `ambiguous_author_resolution`." One per
            # occurrence, carrying both candidates — never one per candidate,
            # which is the shape rc3 §C1 calls the naive mistake elsewhere.
            ambiguous_authors.append({
                "type": "ambiguous_author_resolution", "index": 0,
                "citation_index": c["index"],
                "candidates": [
                    {"candidate": "full", "candidate_key": full_key,
                     "match_state": f_state, "reference_indices": f_idx},
                    {"candidate": "stop_reduced", "candidate_key": reduced_key,
                     "match_state": s_state, "reference_indices": s_idx},
                ],
            })
            continue

        if f_state != "no_match":
            cand, state, idx, res = full_key, f_state, f_idx, "full_phrase"
        elif s_state != "no_match":
            cand, state, idx, res = reduced_key, s_state, s_idx, "stop_reduced"
        else:
            # Both no_match. The candidate retained for §9.4 is the reduced one
            # where it exists, per §8.4 — it is the narrower of the two and the
            # only one a repair rule can work with.
            cand, state, idx, res = (reduced_key or full_key), "no_match", [], \
                                    "not_resolved"

        c["candidate_key"] = cand
        c["candidate_key_full"] = full_key
        c["candidate_key_stop_reduced"] = reduced_key
        c["match_state"] = state
        c["match_state_full"] = f_state
        c["match_state_stop_reduced"] = s_state
        c["reference_indices"] = idx
        c["author_resolution"] = res
        # The phrase that established the identity. Null where §8.3 says so.
        c["resolved_author_phrase"] = (
            c["author_phrase"] if res == "full_phrase" else
            c.get("stop_reduced_phrase") if res == "stop_reduced" else None)
        if state == "no_match":
            c["identity_class"] = "identity_not_resolved"
        else:
            c["identity_class"] = ("bibliography_key_ambiguous"
                                   if state == "nonunique"
                                   else "unique_reference_match")
        if state == "nonunique":
            ambiguous_citations.append({
                "type": "ambiguous_citation", "index": 0,
                "citation_index": c["index"],
                "candidate_key": cand,
                "reference_indices": idx,
            })

    # rc2 §9.3. The check that was missing, and the reason `Smith et al.
    # (2020)` and a one-author `Smith, J. (2020).` have been matching cleanly.
    #
    #     exact  passes iff reference.author_count == len(visible_authors)
    #            AND reference.authors[i] == visible_authors[i] for every i
    #     et_al  passes iff reference.author_count >= ET_AL_MIN_AUTHORS
    #            AND reference.authors[i] == visible_authors[i] for every
    #            visible i
    #
    # The et_al rule compares every visible author, not only the first, so
    # `Smith, Jones, et al. (2020)` is checked on both.
    by_key = {}
    for r in refs:
        if r["reference_key"] and r.get("authors"):
            by_key.setdefault(r["reference_key"], r)

    mismatches = []
    for c in (cits if not absent else []):
        ref = by_key.get(c["citation_key"])
        vis = c.get("visible_authors")
        # "For person citations with NON-NULL person-form data and a matched
        # reference with NON-NULL authors/author_count." A null on either side
        # takes no part, which is rc2's protection against a confident wrong
        # answer from a fragile parse.
        if ref is None or not vis or c.get("author_kind") != "person":
            continue
        ra, rn = ref["authors"], ref["author_count"]
        if c["author_form"] == "exact":
            count_ok = rn == len(vis)
        else:
            count_ok = rn >= ET_AL_MIN_AUTHORS
        order_ok = all(i < len(ra) and ra[i] == v for i, v in enumerate(vis))
        if count_ok and order_ok:
            continue
        # rc2: "If count and order both fail, failed=count." Which half failed
        # is the whole point of the field — `Smith & Jones` against
        # Smith-and-Brown and `Smith & Jones` against three authors are
        # different faults with different repairs.
        mismatches.append({
            "type": "author_structure_mismatch", "index": 0,
            "citation_index": c["index"] if "index" in c else None,
            "citation_key": c["citation_key"],
            "citation_author_form": c["author_form"],
            "visible_authors": vis,
            "author_count_constraint": c["author_count_constraint"],
            "reference_authors": ra, "reference_author_count": rn,
            "failed": "count" if not count_ok else "order",
        })

    # rc3 A5, normative:
    #
    #     detected_candidates    = parsed + unresolved + excluded
    #     extraction_denominator = parsed + unresolved
    #                              EXCLUDES excluded_candidate
    #     candidate_parse_rate   = parsed / extraction_denominator
    #
    # and, in terms this summary is required to obey:
    #
    #     `candidate_parse_rate` is NOT accuracy. It measures how much of what
    #     the detector proposed the parser could read. It says nothing about
    #     detection recall, and a parser can successfully parse an incorrect
    #     span. Extraction accuracy, precision and recall MUST NOT be reported
    #     until a gold set exists. Naming a parse rate "accuracy" is the same
    #     defect this whole milestone is about: a number that cannot come back
    #     false.
    #
    # So this record carries a parse rate under its own name and no accuracy
    # field of any kind. Precision and recall are computed in
    # `scripts/gold_runner.py`, against the hand-annotated sets, and nowhere
    # else. rc3 also warns that the rate is the less stable of the two figures
    # — segment splitting turns one failed parenthesis into several failed
    # segments, so absolute counts survive detection changes and rates do not.
    # Both are emitted; the counts are the ones to compare across runs.
    # Collected, not emitted. §12.2's order is applied in one place below.

    # ---------------------------------------------------- rc2 §9.4 and §9.5
    #
    # CIT-ARCH-01: "If no compatible entry exists, classify it as
    # MISSING_REFERENCE while preserving the citation-derived candidate."
    # This is that classification, and rc2 §9.4 is its rules.
    #
    # §8.4's two-candidate suppression is LIVE as of 22 September, which is
    # the day C-019 landed. The note that used to sit here said this loop
    # would need the check on exactly that day, and it does.
    #
    # §9.4's own precondition:
    #
    #     identity_class = identity_not_resolved
    #     AND exactly one deterministic internal candidate exists
    #
    # An occurrence carrying a reduced phrase has TWO: the full-phrase
    # candidate and the STOP-reduced one, always distinct because the first
    # keys non-person over the whole surface and the second keys a surname.
    # Identity is underdetermined for those before fuzzy repair even begins,
    # so emitting a candidate-level diagnostic would name one of two — the
    # guess CIT-ARCH-01 exists to prevent.
    # §10 again: `missing_reference`, `possible_mismatch` and
    # `uncited_reference` are all built from here down, and all three are on
    # the suppression list. Empty in absent mode rather than guarded record by
    # record, so a later addition to this block cannot forget.
    unresolved_cits = [] if absent else [
        c for c in cits
        if c["identity_class"] == "identity_not_resolved"
        and not c.get("stop_reduced_phrase")]

    # "Group such occurrences by that candidate key in FIRST-OCCURRENCE order."
    grouped: dict[str, list[dict]] = {}
    for c in unresolved_cits:
        grouped.setdefault(c["candidate_key"], []).append(c)

    # "Build the unmatched unique-reference pool in reference SOURCE order,
    # excluding ... references already exactly matched by an authoritative
    # citation identity." Ambiguity-reserved indices would be excluded too;
    # nothing reserves any yet, so the set is empty rather than ignored.
    #
    # "UNIQUE-reference pool" is load-bearing and was missed when §9.4 first
    # landed on 21 September. §9.1 builds `by_reference_key` and emits one
    # `duplicate_reference_key` per key holding two or more entries; a
    # reference inside such a group has no unambiguous identity, so it can be
    # neither a repair target here nor an `uncited_reference` under §9.6.
    #
    # This corpus has five such groups across four papers, and every one is
    # two genuinely different works by the same first author in the same year
    # — `Felfe & Schyns (2006)` beside `Felfe, Schmook & Six (2006)`. APA
    # disambiguates those with 2006a/2006b and these bibliographies do not, so
    # `surname|year` really is ambiguous for them rather than defective.
    authoritative = {c["candidate_key"] for c in cits
                     if c["identity_class"] == "unique_reference_match"}
    unique_keys = {k for k, idx in ref_index_by_key.items() if len(idx) == 1}

    # rc2 §8.5, ambiguity reservation. Two sources, and they behave
    # differently here:
    #
    #   1. indices named by `ambiguous_author_resolution` — live since rows
    #      6-9 landed, and the only reason this set is ever non-empty
    #   2. indices belonging to a key that resolves nonuniquely and emits
    #      `ambiguous_citation` — already excluded structurally, because a
    #      nonunique key is by definition not in `unique_keys`
    #
    # The second is computed anyway rather than argued away. The argument is
    # currently sound and it is one refactor away from not being, and this
    # file has already watched a structural guarantee stop holding quietly.
    reserved: set[int] = set()
    for a in ambiguous_authors:
        for cand in a["candidates"]:
            reserved.update(cand["reference_indices"])
    for a in ambiguous_citations:
        reserved.update(a["reference_indices"])

    # "Reserved indices are removed from the unmatched-reference pool", so
    # they can neither pair in `possible_mismatch` nor surface as
    # `uncited_reference` — §8.5 names both prohibitions, and both are served
    # by the one exclusion because §9.6 emits what the pool has left.
    pool = [i for i, r in enumerate(refs)
            if r["reference_key"] in unique_keys
            and r["reference_key"] not in authoritative
            and i not in reserved]

    # §9.5's merge qualification needs the suspect entries.
    embedded = [r for r in refs
                if "embedded_entry_pattern" in r.get("suspect_reasons", [])]

    diagnostics = []
    for cand_key, occs in grouped.items():
        kind, phrase, year = _split_key(cand_key)
        paired = None
        for pi, ri in enumerate(pool):            # source order
            r = refs[ri]
            rk, rp, ry = _split_key(r["reference_key"])
            rule = repair_rule(kind, phrase, year, rk, rp, ry)
            if rule:
                paired = (pi, ri, rule)
                break                             # "the FIRST rule that matches"
        if paired:
            pi, ri, rule = paired
            pool.pop(pi)                          # "remove from the pool"
            diagnostics.append({
                "type": "possible_mismatch", "index": 0,
                "candidate_key": cand_key, "reference_index": ri,
                "reference_key": refs[ri]["reference_key"],
                "rule": rule, "occurrences": len(occs),
                # rc2, twice over and in CIT-ARCH-01: this establishes nothing.
                "citation_key": None, "author_kind": None,
            })
        else:
            merge = any(
                phrase in re.sub(r"\s+", " ", r["assembled"]).lower()
                and year in r["assembled"] for r in embedded)
            diagnostics.append({
                "type": "missing_reference", "index": 0,
                "candidate_key": cand_key, "occurrences": len(occs),
                "merge_suspected": merge,
                "citation_key": None, "author_kind": None,
            })

    # §12.2: "Blocks never interleave." `diagnostics` holds both kinds in
    # pairing order, so emitting it as one run reopened the missing_reference
    # block seven times on paper ad1e3ff9 — interleaved with possible_mismatch
    # exactly as the section forbids. Split here; ordered below.
    missing_refs = [d for d in diagnostics if d["type"] == "missing_reference"]
    possible_mismatches = [d for d in diagnostics
                           if d["type"] == "possible_mismatch"]

    # ---------------------------------------------------------- rc2 §9.6
    #
    #     After exact authoritative matches, ambiguity reservation, and
    #     candidate-level possible-mismatch pairing, emit `uncited_reference`
    #     for every remaining unique keyed reference.
    #
    # `pool` is already that set. It was built unique-keyed and not
    # authoritatively matched, and §9.4's loop popped every reference it
    # paired, so what survives is the residual the section asks for. Nothing
    # is recomputed here, deliberately: a second derivation of "remaining"
    # could disagree with the first, and then one of them would be wrong
    # without anything saying which.
    #
    # The section's second sentence needs no code. "`unresolved_reference`
    # rows are never uncited-reference candidates because they have no
    # authoritative reference identity" — those rows carry no
    # `reference_key`, so they never entered `ref_index_by_key`, never
    # appeared in `unique_keys`, and cannot reach the pool. Stated because a
    # reader should not have to rediscover that the guard is structural.
    uncited = [{"type": "uncited_reference", "index": i,
                "reference_index": ri,
                "reference_key": refs[ri]["reference_key"]}
               for i, ri in enumerate(pool)]

    # ------------------------------------------------ rc2 §12.2, block order
    #
    #     Empty blocks emit nothing. Blocks never interleave.
    #
    # Stated once, here, rather than emerging from the order in which each
    # block happens to be computed. It emerged that way until 22 September and
    # the result was wrong in two ways at once: `author_structure_mismatch`
    # came out fourth from the top instead of last, and the two §9.4
    # diagnostics shared one list, so `missing_reference` reopened seven times
    # on paper ad1e3ff9 — interleaved, which the section forbids in as many
    # words.
    #
    # rc3's two additional record types are not in §12.2's list, which was
    # written before them. They sit with the other Pass-1 candidate outcomes,
    # immediately after `unresolved_citation`, and that placement is this
    # implementation's choice rather than rc2's.
    for i, m in enumerate(mismatches):
        m["index"] = i
    for i, a in enumerate(ambiguous_citations):
        a["index"] = i
    for i, a in enumerate(ambiguous_authors):
        a["index"] = i
    for i, d in enumerate(missing_refs):
        d["index"] = i
    for i, d in enumerate(possible_mismatches):
        d["index"] = i

    for block in (cits,                 # 2
                  unres,                # 3
                  excl, errs,           # rc3, placed here
                  bib_absent,           # 4
                  refs_out,             # 5
                  ref_unres_out,        # 6
                  ambiguous_authors,    # 7
                  missing_refs,         # 8
                  uncited,              # 9
                  # 10 duplicate_reference_key — §9.1, not implemented
                  ambiguous_citations,  # 11
                  possible_mismatches,  # 12
                  mismatches):          # 13
        lines.extend(block)

    # Alex Zamurko, 20 September, amending rc2:
    #
    #     A citation is `unique_reference_match` only when exactly one
    #     bibliography entry matches the citation identity AND all applicable
    #     author-structure checks pass. [...] `author_structure_mismatch`
    #     occurrences MUST NOT contribute to `uniquely_matched_occurrences`
    #     or `uniquely_matched_works`.
    #
    # rc2 §9.3 says the opposite about identity — "a unique exact key match
    # remains an established identity even if author-structure validation
    # emits a mismatch" — and the two are compatible. The identity stands; the
    # match does not count as unique. So the key is kept and the occurrence is
    # subtracted from the matched counts rather than erased.
    mismatched_keys = {m["citation_key"] for m in mismatches}
    uniquely_matched = [c for c in matched
                        if c["citation_key"] not in mismatched_keys]

    n_parsed, n_unres, n_excl = len(cits), len(unres), len(excl)
    denom = n_parsed + n_unres
    # rc2 §11.3. When identity resolution did not run, ten fields go `null`
    # rather than `0`, and the section says why in one line: "null means the
    # corresponding resolution/reconciliation quantity was not evaluated."
    #
    # `0` would be a measurement — we looked, and found none. `null` is the
    # absence of a measurement. A downstream reader averaging match rates over
    # a corpus has to be able to tell those apart, and a zero that means "not
    # asked" is the same defect class as a green control that never ran.
    #
    # `resolved_citation_occurrences = 0` is the one exception §11.3 makes,
    # and it is not an oversight: zero citations were resolved, and that IS a
    # measurement.
    def _n(value):
        """§11.3: null in bibliography-absent mode, the count otherwise."""
        return None if absent else value

    lines.append({"type": "summary",
                  "identity_resolution_performed": not absent,
                  "references_source": ref_source,
                  # v3.3's fields keep v3.3's meaning. rc2 renames them
                  # `uniquely_matched_*`, which is the consolidation's change
                  # to make, not this one's.
                  "matched_occurrences": _n(len(uniquely_matched)),
                  "matched_works": _n(len({c["citation_key"]
                                           for c in uniquely_matched})),
                  "author_structure_mismatches": _n(len(mismatches)),
                  # rc3 §C partitions CASES, not defects: one record per
                  # group, however many defects that group carries.
                  # rc2 §11.2, over the three reachable identity
                  # classes. The partition is exact by construction:
                  # every parsed citation gets exactly one.
                  "unique_reference_match_occurrences": _n(
                      sum(1 for c in cits
                          if c["identity_class"] == "unique_reference_match")),
                  "bibliography_key_ambiguous_occurrences": _n(
                      sum(1 for c in cits
                          if c["identity_class"] == "bibliography_key_ambiguous")),
                  "identity_not_resolved_occurrences": _n(
                      sum(1 for c in cits
                          if c["identity_class"] == "identity_not_resolved")),
                  # rc2 §9.2's fourth identity class, live since §8.3 rows 6-9
                  # landed. Counted even though this corpus produces none:
                  # a partition over three names when the code can emit four
                  # is an invariant that holds only while the fourth stays
                  # empty, which is not what an invariant is for.
                  "author_resolution_ambiguous_occurrences": _n(
                      sum(1 for c in cits
                          if c["identity_class"] == "author_resolution_ambiguous")),
                  # §11: "unique citation_surface_group_key values among
                  # extracted citations; ALWAYS emitted" — including in
                  # bibliography-absent mode, where §10 keeps it computed
                  # while nulling the identity counts. Aggregation survives
                  # the absence of a bibliography because it never needed one.
                  #
                  # Keyed on the JSON bytes so ["smith", 2020] and
                  # ["smith", "2020"] count as two, which is what §6.6's
                  # integer-versus-string distinction is for.
                  "distinct_surface_groups": len({
                      json.dumps(c["citation_surface_group_key"],
                                 separators=(",", ":"), ensure_ascii=False)
                      for c in cits}),
                  "citation_error_cases": len(errs),
                  "citation_error_defects": sum(len(e["defects"]) for e in errs),
                  "parsed": n_parsed,
                  "unresolved": n_unres,
                  "excluded": n_excl,
                  "detected_candidates": denom + n_excl,
                  "extraction_denominator": denom,
                  "candidate_parse_rate": (round(n_parsed / denom, 4)
                                           if denom else None),
                  "excluded_by_reason": {
                      r: sum(1 for x in excl if x["excluded_reason"] == r)
                      for r in EXCLUDED_REASONS
                      if any(x["excluded_reason"] == r for x in excl)},
                  # rc2 §9.3: "An `exact` mismatch forces exit 1. An `et_al`
                  # mismatch is reported but does not by itself force exit 1
                  # in v3.4." The split is deliberate — an exact mismatch is
                  # wrong in every style, while et_al depends on
                  # ET_AL_MIN_AUTHORS and is style-dependent.
                  #
                  # Bibliography-absent mode is stated rather than inherited.
                  # The test below asks whether every citation was uniquely
                  # matched; under §10 none can be, because identity was never
                  # evaluated. So absent mode would reach exit 1 through a
                  # condition that is vacuous there — the right answer for a
                  # reason that does not survive reading.
                  #
                  # It is exit 1 because a manuscript with no reference list
                  # is a reportable condition about the document, and exit 0
                  # would assert there is nothing to report. Recorded as this
                  # implementation's reading, not as rc2's: §14 gives exit 1
                  # to "one or more defined finding conditions" and never
                  # closes that set, which is C-078 and unimplemented.
                  "exit": 1 if absent else
                          (0 if (len(uniquely_matched) == len(cits)
                                 and not unres
                                 and not any(m["citation_author_form"] == "exact"
                                             for m in mismatches)) else 1)})
    return lines, lines[-1]["exit"]


# rc2 §12.3, the declared key order per record type.
#
#     keys in the exact order declared for each record below
#
# Applied in `serialize` rather than by reordering thirteen dict literals,
# for the reason §12.2's block order is stated in one place: a rule spread
# across thirteen constructors is a rule nobody can read, and the next field
# added goes wherever the author happened to be typing.
#
# Two things this table does NOT do, both recorded rather than silently
# handled:
#
#   1. It does not drop fields. This implementation carries more than rc2
#      declares — `candidate_state` and `excluded_reason` from rc3 §A,
#      `stop_reduced_phrase` from §6.3, the two candidate keys from §8.1.
#      rc2's keys come first in rc2's order; ours follow. A byte golden
#      against rc2 would still differ on the tail, which is why C-068 is not
#      claimed as fully met.
#   2. It does not rename the summary's counts. rc2 calls them
#      `uniquely_matched_occurrences` and `uniquely_matched_works`; this file
#      keeps v3.3's `matched_occurrences` and `matched_works`, as it has
#      since before the consolidation, and that rename is the consolidation's
#      to make.
KEY_ORDER = {
    "citation": [
        "type", "index", "citation_group", "citation_segment",
        "author_phrase", "resolved_author_phrase", "author_resolution",
        "author_kind", "citation_surface_group_key", "citation_key", "year",
        "style", "author_form", "visible_authors", "author_count_constraint",
        "group_start", "group_end", "segment_start", "segment_end",
        "sentence", "sentence_start", "sentence_position", "sentence_index",
        "previous_sentence_end", "standalone", "section_level",
        "section_name", "section_type", "section_roles"],
    "unresolved_citation": [
        "type", "index", "text", "start", "end", "reason",
        "citation_surface_group_key", "sentence", "sentence_start",
        "section_level", "section_name"],
    "reference": [
        "type", "index", "assembled", "author_kind",
        "identity_author_phrase", "reference_key", "authors", "author_count",
        "year", "start", "end", "validation_state", "suspect_reasons"],
    "unresolved_reference": [
        "type", "index", "text", "start", "end", "reason"],
    "ambiguous_author_resolution": [
        "type", "citation_index", "author_phrase", "full_match_state",
        "full_candidate_key", "full_reference_indices", "stop_reduced_phrase",
        "stop_reduced_match_state", "stop_reduced_candidate_key",
        "stop_reduced_reference_indices"],
    "missing_reference": [
        "type", "candidate_key", "identity_authority", "example",
        "occurrences", "merge_suspected"],
    "uncited_reference": ["type", "reference_index", "reference_key"],
    "duplicate_reference_key": [
        "type", "reference_key", "reference_indices", "cited"],
    "ambiguous_citation": [
        "type", "citation_key", "example", "reference_indices"],
    "possible_mismatch": [
        "type", "candidate_key", "identity_authority", "reference_index",
        "reference_key", "evidence"],
    "author_structure_mismatch": [
        "type", "citation_key", "reference_index", "citation_author_form",
        "visible_authors", "author_count_constraint", "reference_authors",
        "reference_author_count", "failed", "example"],
    "bibliography_absent": ["type", "references_source"],
    "error": ["type", "code", "reason"],
}


def canonical_order(rec: dict) -> dict:
    """rc2's declared keys in rc2's order, then anything else this file adds."""
    order = KEY_ORDER.get(rec.get("type"))
    if not order:
        return rec
    out = {k: rec[k] for k in order if k in rec}
    out.update({k: v for k, v in rec.items() if k not in out})
    return out


def serialize(records: list[dict]) -> bytes:
    """rc2 §12.1's canonical stream, as BYTES.

    Bytes rather than a string because three of §12.1's clauses are byte
    properties and cannot be asserted on a `str`:

        UTF-8, no BOM
        LF line ending only
        every line, including the final line, ends with exactly one LF

    And because `print()` would break the second of those on Windows, where
    text-mode stdout translates `\\n` to `\\r\\n`. The extractor emitted its
    stream through `print()` until 22 September, so every run on this machine
    was producing CRLF output that §12.1 forbids — invisible on Linux, and
    invisible in any test that parsed the lines back rather than reading them.
    """
    return b"".join(
        json.dumps(canonical_order(r), separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8") + b"\n"
        for r in records)


def publish(target: Path, payload: bytes, digest: str | None) -> Path:
    """rc2 §13's atomic publication.

        1. build complete bytes in a temporary file in the destination
           directory;
        2. evaluate all abort-class conditions, including exit 6;
        3. fsync/close as needed for safe rename;
        4. atomically rename over the target only after complete output is
           known.

    Step 2 has already happened: `payload` exists, so either the run completed
    or it aborted and this is the two-line error stream. That ordering is the
    point of the section — a reader must never find a half-written normal
    artifact, so nothing is placed at the target path until the whole of it is
    known.

    The temp file goes in the DESTINATION directory rather than /tmp, because
    `os.replace` is only atomic within a filesystem.
    """
    if target.is_dir():
        if digest is None:
            # Exit 5: the manuscript has no canonical form, so it has no
            # canonical_sha256 and no derived filename. rc2 does not cover
            # this pairing; refusing to invent a name is the conservative
            # reading.
            raise Abort(5, "invalid utf-8: no canonical name for a directory "
                           "target")
        target = target / f"{digest}.citations.jsonl"
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=".citations-",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, target)
    except BaseException:
        # A failed publish leaves the target untouched and takes its scratch
        # file with it.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return target


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="citation_extract.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper")
    ap.add_argument("--fix", default="",
                    help="comma-separated: " + ", ".join(FIXES) +
                         "; or `all` for every one of them. Default none, "
                         "which is v3.3 as specified.")
    ap.add_argument("--out", metavar="PATH",
                    help="write the same canonical bytes here as well as to "
                         "stdout, published atomically. A directory names the "
                         "file <canonical_sha256>.citations.jsonl.")
    a = ap.parse_args()

    fixes = {f.strip() for f in a.fix.split(",") if f.strip()}
    # `all` exists so the canonical set never has to be retyped. Two scripts
    # had retyped it and both had drifted: one lost `mathyear` entirely, and
    # one corpus measurement used two of the five and reported 72 uncited
    # references where the figure is 57. A list a caller must keep in sync by
    # hand is a list that goes stale.
    if "all" in fixes:
        fixes = (fixes - {"all"}) | set(FIXES)
    unknown = fixes - set(FIXES)
    if unknown:
        print(f"unknown fix(es): {sorted(unknown)}; known: {list(FIXES)}",
              file=sys.stderr)
        return 1

    digest = None
    try:
        lines, code = run(Path(a.paper), fixes)
        digest = lines[0]["canonical_sha256"]
        payload = serialize(lines)
    except Abort as ab:
        # §13: "For exits 2-5, the two-line error stream is written to the
        # requested file as the authoritative error artifact." The same bytes
        # go to stdout, so the two destinations never disagree.
        code = ab.code
        payload = serialize([
            {"type": "meta", "spec_version": SPEC_VERSION},
            {"type": "error", "code": ab.code, "reason": ab.reason}])

    # §12.1: UTF-8, LF only. Written through the binary buffer so the
    # platform's text layer cannot translate the line endings.
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()

    if a.out:
        try:
            publish(Path(a.out), payload, digest)
        except Abort as ab:
            print(f"--out: {ab.reason}", file=sys.stderr)
            return ab.code
        except OSError as e:
            print(f"--out: {e}", file=sys.stderr)
            return 1
    return code


if __name__ == "__main__":
    sys.exit(main())
