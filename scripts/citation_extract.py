#!/usr/bin/env python3
"""Citation extraction, deterministic spec v3.3 — in version control this time.

    python scripts/citation_extract.py <paper.md>
    python scripts/citation_extract.py <paper.md> --fix ampersand,segments,colon,cp

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
import json
import re
import sys
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
YEAR = r"(?:1[5-9]|20)\d{2}[a-z]?|n\.d\."
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

    if ref is None:
        raise Abort(3, "references section not found")

    after = [h for h in heads if h[3] > ref[3] and h[1] <= ref[1]]
    ref_end = after[0][3] if after else len(text)
    body = text[:ref[3]]
    return body, text[ref[4] + 1:ref_end], ref[4] + 1, heads


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
    return out


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


def extract_citations(body: str, sents, heads, fixes: set[str]):
    pat = build_patterns(fixes)
    cits, unres, excl = [], [], []
    maths = math_spans(body)

    for c1s, c1e in c1_spans(body):
        # A4: classification precedes the grammar, and terminates the
        # candidate when it fires.
        reason = classify_exclusion(body, c1s, c1e, heads, maths)
        if reason is not None:
            _excl(body, c1s, c1e, reason, sentence_of(sents, c1s), heads, excl)
            continue

        sent = sentence_of(sents, c1s)
        if sent is None:
            continue
        s_start, s_end, s_content_end = sent
        c1 = body[c1s:c1e]

        # 1. Parenthetical, full match over the whole C1 span.
        m = pat["cite_paren"].fullmatch(c1)
        if m:
            segs = _paren_segments(c1, pat)
            _emit_paren(body, c1s, c1e, segs, sent, heads, cits, unres)
            continue

        if "segments" in fixes:
            # One unparseable segment loses every citation beside it under
            # §6.2's atomic reading. Each segment is parsed on its own and a
            # failure is reported for that segment alone.
            done = _segmented_paren(body, c1s, c1e, pat, sent, heads,
                                    cits, unres)
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
                _emit_narr(body, span_start, c1e, sent, heads, cits, unres, pat)
                continue
            _unres(body, run_start, c1e, "no_grammar_match", sent, heads, unres)
            continue

        span = (run_start, c1e) if toks else (c1s, c1e)
        _unres(body, span[0], span[1], "no_grammar_match", sent, heads, unres)

    cits.sort(key=lambda r: (r["group_start"], r["segment_start"]))
    unres.sort(key=lambda r: r["start"])
    excl.sort(key=lambda r: r["start"])
    return cits, unres, excl


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


def _emit_paren(body, c1s, c1e, segs, sent, heads, cits, unres):
    inner_off = c1s + 1
    for seg_text in segs:
        pos = body.find(seg_text, inner_off, c1e)
        if pos < 0:
            continue
        _emit_segment(body, c1s, c1e, pos, pos + len(seg_text), seg_text,
                      "parenthetical", sent, heads, cits, unres)


def _segmented_paren(body, c1s, c1e, pat, sent, heads, cits, unres) -> bool:
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
                          "parenthetical", sent, heads, cits, unres)
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


def _emit_narr(body, span_start, c1e, sent, heads, cits, unres, pat):
    text = body[span_start:c1e]
    authors = text[:text.rindex("(")].rstrip()
    core = first_core(authors)
    if is_all_caps(core):
        _unres(body, span_start, c1e, "all_caps_surname", sent, heads, unres)
        return
    if core.lower() in STOP:
        _unres(body, span_start, c1e, "stopword_surname", sent, heads, unres)
        return
    years = YEAR_RE.findall(body[body.rindex("(", span_start, c1e):c1e])
    for y in years:
        _record(body, span_start, c1e, span_start, c1e, text, core, y,
                "narrative", sent, heads, cits, author_phrase=authors)


def _emit_segment(body, gs, ge, ss, se, seg_text, style, sent, heads, cits,
                  unres):
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
        _unres(body, ss, se, "all_caps_surname", sent, heads, unres)
        return
    for y in YEAR_RE.findall(rest[comma:] if comma > 0 else rest):
        _record(body, gs, ge, ss, se, seg_text, core, y, style, sent, heads,
                cits, author_phrase=authors)


def _record(body, gs, ge, ss, se, seg_text, core, year, style, sent, heads,
            cits, author_phrase=""):
    s_start, s_end, s_content_end = sent
    lv, nm, ty, rs = section_stack_at(heads, gs)
    surname = re.sub(r"\s+", " ", core).strip().lower()
    y = norm_year(year)
    cits.append({
        "type": "citation", "index": 0,
        # Not in v3.3's §9 contract. Emitted because a gold set annotated by
        # hand keys on the author phrase as written, and deriving a surname
        # from it is the grammar under test: scoring against a key this
        # extractor derived would have it agree with itself. rc3 §A makes
        # author_phrase mandatory for the same reason, so this is forward
        # compatible rather than an invention.
        "author_phrase": re.sub(r"\s+", " ", author_phrase).strip(),
        "candidate_state": "parsed",
        "citation_group": body[gs:ge], "citation_segment": seg_text,
        "citation_key": f"{surname}|{y}", "surname": surname, "year": y,
        "style": style,
        "group_start": gs, "group_end": ge,
        "segment_start": ss, "segment_end": se,
        "sentence": body[s_start:s_end], "sentence_start": s_start,
        "sentence_position": ("start" if gs == s_start else
                              "end" if ge == s_content_end else "middle"),
        "section_level": lv, "section_name": nm, "section_type": ty,
        "section_roles": rs,
    })


def _unres(body, start, end, reason, sent, heads, unres):
    s_start, s_end, _ = sent
    lv, nm, _, _ = section_stack_at(heads, start)
    unres.append({
        "type": "unresolved_citation", "index": 0,
        # rc3 A1. `type` already said this, but A1 makes the terminal state a
        # named field on every candidate so the three states can be counted
        # uniformly without knowing which record shapes exist.
        "candidate_state": "unresolved_citation",
        "text": body[start:end], "start": start, "end": end, "reason": reason,
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
        refs.append({
            "type": "reference", "index": 0, "assembled": assembled,
            "reference_key": f"{surname}|{year}" if (surname and year) else None,
            "surname": surname, "year": year, "start": start, "end": end,
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

FIXES = ("ampersand", "segments", "colon", "cp")


def run(path: Path, fixes: set[str]) -> tuple[list[dict], int]:
    text = normalise(path.read_bytes())
    body, section, sec_off, heads = split_body_and_references(text)
    if "ampersand" in fixes:
        body = body.replace("\\&", "&")
        section = section.replace("\\&", "&")
    sents = sentences(body)
    cits, unres, excl = extract_citations(body, sents, heads, fixes)

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

    refs, ref_unres = assemble_references(section, sec_off)

    lines = [{"type": "meta", "spec_version": SPEC_VERSION,
              "implementation": "scripts/citation_extract.py",
              "fixes_applied": sorted(fixes)}]
    for i, c in enumerate(cits):
        c["index"] = i
        lines.append(c)
    for i, u in enumerate(unres):
        u["index"] = i
        lines.append(u)
    for i, x in enumerate(excl):
        x["index"] = i
        lines.append(x)
    for i, r in enumerate(refs):
        r["index"] = i
        lines.append(r)
    for i, u in enumerate(ref_unres):
        u["index"] = i
        lines.append(u)

    keyed = {r["reference_key"] for r in refs if r["reference_key"]}
    cite_keys = []
    for c in cits:
        if c["citation_key"] not in cite_keys:
            cite_keys.append(c["citation_key"])
    matched = [c for c in cits if c["citation_key"] in keyed]

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
    n_parsed, n_unres, n_excl = len(cits), len(unres), len(excl)
    denom = n_parsed + n_unres
    lines.append({"type": "summary",
                  "matched_occurrences": len(matched),
                  "matched_works": len({c["citation_key"] for c in matched}),
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
                  "exit": 0 if len(matched) == len(cits) and not unres else 1})
    return lines, lines[-1]["exit"]


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="citation_extract.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper")
    ap.add_argument("--fix", default="",
                    help="comma-separated: " + ", ".join(FIXES) +
                         ". Default none, which is v3.3 as specified.")
    a = ap.parse_args()

    fixes = {f.strip() for f in a.fix.split(",") if f.strip()}
    unknown = fixes - set(FIXES)
    if unknown:
        print(f"unknown fix(es): {sorted(unknown)}; known: {list(FIXES)}",
              file=sys.stderr)
        return 1

    try:
        lines, code = run(Path(a.paper), fixes)
    except Abort as ab:
        print(json.dumps({"type": "meta", "spec_version": SPEC_VERSION},
                         separators=(",", ":"), ensure_ascii=False))
        print(json.dumps({"type": "error", "code": ab.code,
                          "reason": ab.reason},
                         separators=(",", ":"), ensure_ascii=False))
        return ab.code

    for rec in lines:
        print(json.dumps(rec, separators=(",", ":"), ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
