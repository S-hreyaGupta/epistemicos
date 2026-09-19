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
SURNAME = rf"(?:(?:{PARTICLE}){WS})*{CORE}"
YEAR = r"(?:1[5-9]|20)\d{2}[a-z]?|n\.d\."
INITIALS = r"[A-Z]\.(?:[- ]?[A-Z]\.)*"

AUTHORS_PAREN = (rf"(?:{SURNAME}{WS}et{WS}al\."
                 rf"|{SURNAME}(?:,{WS}?{SURNAME})*(?:,?{WS}(?:&|and){WS}{SURNAME})?)")
AUTHORS_NARR = (rf"(?:{SURNAME}{WS}et{WS}al\."
                rf"|{SURNAME}(?:,{WS}{SURNAME})*,?{WS}(?:&|and){WS}{SURNAME}"
                rf"|{SURNAME})")

# §11 limitation, kept: LOCATOR takes `, p. 480` and not `: 480`. The `colon`
# flag adds the second form rather than replacing the first.
LOCATOR = r",[ \t\n]?(?:p\.|pp\.|para\.|chap\.)[ \t\n]?[^();]+"
LOCATOR_COLON = r"(?::[ \t]*\d[^();]*)"
PREFIX_CUES = ("e.g.", "i.e.", "cf.", "see also", "see", "but see")
PREFIX_CUES_CP = PREFIX_CUES + ("cp.",)

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
ELIGIBLE_LOWER = {"et", "al.", "and", "&"} | set(PARTICLES)


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
    """§6.1 C2: walk left from C1, at most 6 eligible tokens, never past the
    sentence start. Returns (run_start, [token strings]) innermost-last."""
    i = c1_start
    toks, positions = [], []
    while len(toks) < 6:
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
        if not (ELIGIBLE.match(bare) or bare.lower() in ELIGIBLE_LOWER):
            break
        toks.append(tok)
        positions.append(k)
        i = k
    toks.reverse()
    positions.reverse()
    return (positions[0] if positions else c1_start), toks


def build_patterns(fixes: set[str]):
    loc = LOCATOR + (f"|{LOCATOR_COLON}" if "colon" in fixes else "")
    cues = PREFIX_CUES_CP if "cp" in fixes else PREFIX_CUES
    prefix = "(?:" + "|".join(re.escape(c) for c in cues) + r")[, ][ \t\n]?"
    seg = (rf"(?:{prefix})?{AUTHORS_PAREN},{WS}(?:{YEAR})"
           rf"(?:,{WS}(?:{YEAR}))*(?:{loc})?")
    return {
        "seg": re.compile(seg, re.U),
        "cite_paren": re.compile(rf"\([ \t\n]?{seg}(?:;[ \t\n]?{seg})*[ \t\n]?\)",
                                 re.U),
        "cite_narr": re.compile(
            rf"{AUTHORS_NARR}{WS}\([ \t\n]?(?:{YEAR})(?:,{WS}(?:{YEAR}))*"
            rf"(?:{loc})?[ \t\n]?\)", re.U),
        "seg_anchored": re.compile(rf"\A{seg}\Z", re.U),
    }


def first_core(authors: str) -> str:
    """The first author's full SURNAME, particles included, single-spaced."""
    toks = authors.split()
    out = []
    for t in toks:
        if t.lower().rstrip(",") in PARTICLES:
            out.append(t.rstrip(","))
            continue
        out.append(t.rstrip(","))
        break
    return " ".join(out)


def is_all_caps(core: str) -> bool:
    last = core.split()[-1] if core.split() else ""
    letters = [c for c in last if c.isalpha()]
    return len(letters) >= 2 and all(c.isupper() for c in letters)


def norm_year(y: str) -> str:
    return "nd" if y == "n.d." else y


def split_segments(inner: str) -> list[str]:
    """Top-level `;` split. Used only under the `segments` fix."""
    return [s for s in inner.split(";")]


def extract_citations(body: str, sents, heads, fixes: set[str]):
    pat = build_patterns(fixes)
    cits, unres = [], []

    for c1s, c1e in c1_spans(body):
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
            if pat["cite_narr"].fullmatch(cand):
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
    return cits, unres


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
    m = re.match(rf"\A(?:(?:{'|'.join(re.escape(c) for c in PREFIX_CUES_CP)})[, ][ \t\n]?)?",
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
        "text": body[start:end], "start": start, "end": end, "reason": reason,
        "sentence": body[s_start:s_end], "sentence_start": s_start,
        "section_level": lv, "section_name": nm,
    })


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
    cits, unres = extract_citations(body, sents, heads, fixes)

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
    lines.append({"type": "summary",
                  "matched_occurrences": len(matched),
                  "matched_works": len({c["citation_key"] for c in matched}),
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
