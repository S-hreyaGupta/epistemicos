#!/usr/bin/env python3
"""rc2 C-081: which corpus findings have a B1-B10 disposition, and which do not.

    python scripts/corpus_dispositions.py

Exit 0 = every finding the corpus produces carries a disposition.
Exit 1 = some do not, and they are named; or a guard below tripped.
Exit 2 = could not run.

What C-081 actually asks
------------------------
rc2's matrix:

    C-081 | 11-paper corpus has no unresolved blocking finding | pilot |
          | corpus report | all unexpected findings dispositioned by B1-B10

and the classification rule it leans on:

    A non-blocking disposition MUST cite the exact governing rule establishing
    the envelope boundary, accepted limitation, unsupported class, expected
    ambiguity/non-resolution, or explicit deferral. An undocumented
    expectation is not a waiver.

That last sentence is the whole case. "We looked and it seemed fine" is not a
disposition. So this file asks one mechanical question per finding group: does
a document state a disposition for it, and does that disposition cite a rule?

WHAT THIS FILE DOES NOT DO
--------------------------
It does not decide whether a disposition is CORRECT. Whether `orphan_line` on
a badly converted bibliography is an accepted limitation or a B3 defect is a
judgement about two specifications and one corpus, and it stays with the freeze
review. This file only separates the findings that have been ruled on from the
findings that have not, so the review can see what it is being asked to rule on
instead of inheriting it.

`corpus_report.py` counts findings. This file asks whether anyone has said what
they mean. The two are deliberately separate: a count that agrees with the
figures on record is not evidence that the findings behind it were dispositioned.
"""

from __future__ import annotations

import hashlib
import pathlib
import re as _re
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
CORPUS = REPO / "data" / "md_full"
sys.path.insert(0, str(REPO / "scripts"))

import citation_extract as ce  # noqa: E402

# The eleven papers rc2's C-081 names, read off
# `citation-v3.4-pre-rc1-three-additions.md`, which measures "the eleven
# ingested papers" and lists them one per row.
#
# `data/md_full` holds fourteen. The three extra are not in C-081's stated
# scope and nothing says whether they should be. Reported rather than resolved:
# widening a conformance case's corpus is a specification change.
ELEVEN = {
    "17bef7c6", "2af68a7f", "43338825", "5da73cf4", "849f8fc6", "ad1e3ff9",
    "bf2fdc4a", "c1d56945", "c22df19f", "ea07e5f5", "ed6a890a",
}

# The field that carries a finding's sub-reason, per record type. None means
# the type has no sub-reason and disposition is per type.
SUBKEY = {
    "unresolved_citation": "reason",
    "unresolved_reference": "reason",
    "excluded_candidate": "excluded_reason",
    "possible_mismatch": "evidence",
    "author_structure_mismatch": "failed",
    "uncited_reference": None,
    "missing_reference": None,
    "duplicate_reference_key": None,
    "ambiguous_citation": None,
}

# A disposition is (verdict, rule, document, expected count).
#
# The count is a tripwire, the same one `corpus_report.py` carries: a
# disposition written over eleven findings stops being a disposition over those
# eleven when the number moves, and the move has to be noticed rather than
# absorbed.
DISPOSED = {
    ("excluded_candidate", "url_or_image"): (
        "non-blocking", "rc3 B10 and its §G case",
        "specs/citation/EXCLUSION-COVERAGE.md", 11),
    ("excluded_candidate", "publisher_metadata"): (
        "non-blocking", "rc3 §E",
        "specs/citation/EXCLUSION-COVERAGE.md", 8),
}

# Groups with no disposition anywhere, carried explicitly so the list is a
# statement rather than a silence. Each names what a reviewer would have to
# settle. Moving one into DISPOSED needs a document, not an edit here.
UNDISPOSED_NOTE = {
    ("unresolved_reference", "orphan_line"):
        "a bibliography line that attached to no entry. Partitioned below: "
        "every one traces to rc2 §7.1 rule 1, a blank line closing the open "
        "entry, and 116 of the 196 are cascade rather than independent "
        "events. The question for the review is 80 wide, not 196",
    ("unresolved_reference", "entry_start_grammar"):
        "an entry-shaped line rc2 §7.1's guard refused",
    ("unresolved_reference", "no_year"):
        "rc2 §7.3 says emit this and no reference row. Expected by the rule, "
        "but no document says so over this corpus",
    ("unresolved_citation", "no_grammar_match"):
        "the largest citation-side class. C-010 and C-011 make it the correct "
        "outcome rather than a silent drop. Partitioned below by the first "
        "declared production that refuses each span: 25 of the 121 are the "
        "envelope catching prose with no author in it, and the rest are "
        "grammar questions rc3 already names",
    ("unresolved_citation", "stopword_surname"):
        "rc2 §6.3's named outcome",
    ("unresolved_citation", "all_caps_surname"):
        "rc2 §6.2's named outcome, and C-014 pins it",
    ("uncited_reference", None):
        "UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md identifies a large share of "
        "these as naming a reference the paper DOES cite, in a span the "
        "grammar could not read. A false reconciliation diagnostic is B3 on "
        "its face. The document states the number and stops short of "
        "classifying it. Re-derived below rather than quoted, because the "
        "figure moved",
    ("missing_reference", None):
        "candidate-level, so it establishes no identity. Partitioned below: "
        "only 9 of the 32 are a plausible author omission. Two are in a "
        "bibliography line the reference grammar refused, three are a "
        "surname the manuscript itself spells two ways, and 18 name a "
        "surname the references section does carry under a different year",
    ("possible_mismatch", "surname_edit_distance_1"):
        "rc2 §9.4's first repair rule",
    ("possible_mismatch", "year_adjacent"):
        "rc2 §9.4's second repair rule",
    ("duplicate_reference_key", None):
        "rc2 §9.1's record. Implemented 23 September, never dispositioned",
    ("ambiguous_citation", None):
        "rc2 §8.3 rows 3 and 5, and 15 of the 17 come from the three papers "
        "outside C-081's eleven. Reduced below to the 5 keys behind them: "
        "every pair is two genuinely different works, no manuscript uses a "
        "letter suffix, and the author list that does tell them apart is "
        "carried in the output but not in the key",
    # Two groups, not one. `author_structure_mismatch` carries a `failed`
    # field and rc2 §9.3 gives it two exact checks, so a single disposition
    # over the type would be covering two different findings with one
    # sentence. The guard below caught this on the first run, which is what
    # it is for.
    ("author_structure_mismatch", "count"):
        "rc2 §9.3's count check, pinned by C-062. "
        "RC1-IS-BIGGER-THAN-THE-SPLIT called author-structure agreement the "
        "amendment with a live defect behind it, and the check it said did "
        "not exist now does: two of the six candidates it named are caught. "
        "One of the remaining four that document already identified as its "
        "own measuring error, two sit on ambiguous keys where no identity "
        "was established, and the last cannot be checked at all. See the "
        "coverage block below for why",
    ("author_structure_mismatch", "order"):
        "rc2 §9.3's order check, pinned by C-063. Same open question as the "
        "count half",
}

# UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md, 22 September, as written.
#
# Its method, verbatim: "For each `uncited_reference`, check whether its
# surname and year both appear inside a single span the extractor emitted as
# `unresolved_citation`. Same span, not the same document."
#
# Pinned so the note above cannot go on quoting a figure the corpus stopped
# producing. It already had: 57 and 28 were both correct for the extractor at
# f6280de and both moved when §3.1's five missing PREFIX cues landed in
# e788440 the next day. Confirmed by re-running that extractor over this
# corpus rather than inferred — 57/28 before, 56/27 after.
RECALL_DOC = "specs/citation/UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md"
RECALL_PINNED = {"uncited": 56, "person_matched": 27, "non_person_matched": 3}


def canonical_text(path: pathlib.Path, fixes: set, meta: dict) -> str | None:
    """The exact string every coordinate in the output indexes, or None.

    Reproduces `run`'s three lines — normalise, then rc3 D1's two
    byte-changing transforms in rc3 §J's pinned order — and then CHECKS the
    result against the run's own `canonical_sha256` rather than trusting it.
    A first attempt skipped the transforms and read a string 106 characters
    from the one the offsets belong to; every line lookup below was quietly
    off, and 55 of 196 orphans failed to map at all. The hash is what turns
    that from a silent wrong answer into a refusal.
    """
    text = ce.normalise(path.read_bytes())
    if "ampersand" in fixes:
        text = text.replace("\\&", "&")
    if "mathyear" in fixes:
        text = ce.unwrap_math_years(text)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta.get(
            "canonical_sha256"):
        return None
    return text


def orphan_causes(lines: list, text: str) -> Counter:
    """Why no entry was open, per rc2 §7.1's own five rules.

    §7.1 emits `orphan_line` in exactly one situation: a non-blank,
    non-heading line that is neither an ENTRY_START nor an entry candidate,
    arriving when nothing is open. So the question is never what the text is.
    It is which of rules 1, 2 and 3 last closed the entry, and that is
    readable off the line above without re-implementing the walk.
    """
    out: Counter = Counter()
    starts, off = [], 0
    for ln in text.split("\n"):
        starts.append(off)
        off += len(ln.encode("utf-8")) + 1
    src = text.split("\n")
    idx = {}
    for i, s in enumerate(starts):
        idx[s] = i
    orphan_rows = []
    for r in lines:
        if r.get("type") != "unresolved_reference" or \
                r.get("reason") != "orphan_line":
            continue
        # The record's start is the first non-whitespace byte of its line, so
        # walk back to the line start rather than assuming they coincide.
        i = max((j for j, s in enumerate(starts) if s <= r["start"]),
                default=None)
        if i is None:
            out["could not be located in the manuscript"] += 1
            continue
        orphan_rows.append(i)
    seen = set(orphan_rows)
    for i in orphan_rows:
        prev = src[i - 1] if i else ""
        if (i - 1) in seen:
            out["continuing a run the line above started"] += 1
        elif not prev.strip(" \t"):
            out["after a BLANK line, rule 1 closed the entry"] += 1
        elif ce.HEAD_MD.match(prev) or ce.HEAD_HTML.match(prev):
            out["after a heading, rule 2 closed the entry"] += 1
        else:
            out["after a line that was consumed into an entry"] += 1
    return out


def grammar_refusals(lines: list) -> Counter:
    """Which declared production refuses each `no_grammar_match` span.

    Same method as the orphan partition: ask rc2's own machinery why, rather
    than sorting the text by eye into categories this file invented. Every
    test below is a production the specification declares — YEAR, INITIALS,
    CORE, the closed STOP set, §7.4's non-person head — and the order is
    first-failure, so a span is reported against the earliest thing that
    refuses it.

    ONE GROUP IS NAMED FOR AN ASYMMETRY, NOT A CAUSE
    ------------------------------------------------
    `non_person_head` accepts `BIS` and `Citizenship report P&G India
    subcontinent`, which are organisations. It also accepts
    `Ulker Demirel & Ciftci` and `Saeed & Binti Abdul Ghani Azmi`, which are
    people with multi-token surnames. Both land in one group because §7.4's
    reference-side path is what admits both, and that asymmetry — the
    reference side accepts the head, the citation side refuses it — is the
    true statement available here.

    Calling the group "non-person" would have been the day's recurring
    defect in miniature: a label that is accurate about the test and wrong
    about the finding. Separating the organisations from the multi-token
    surnames needs rc3 B1a's surname production, which this file does not
    implement and must not invent.
    """
    init_re = _re.compile(rf"^{ce.INITIALS}")
    year_only = _re.compile(rf"^[\(\s]*{ce.YEAR}[\)\s,.]*$")
    out: Counter = Counter()
    for r in lines:
        if r.get("type") != "unresolved_citation" or \
                r.get("reason") != "no_grammar_match":
            continue
        t = r["text"]
        inner = t[1:-1] if t.startswith("(") and t.endswith(")") else t
        head = _re.split(rf"[,(]?\s*{ce.YEAR}", inner)[0].strip(" ,;(")
        first = _re.split(r"[\s,;:]+", head)[0].lower().rstrip(",;:") if head \
            else ""
        if year_only.match(t.strip()) or not head:
            k = "a year with no author region at all"
        elif init_re.match(head):
            k = "opens with INITIALS — rc3 §C3's forename-first limitation"
        elif not _re.search(ce.CORE, head):
            k = "no CORE anywhere in the author region"
        elif first in ce.STOP:
            k = "opens with a STOP token — §6.3 reduced and the rest refused"
        elif ce.non_person_head(head):
            k = "§7.4 accepts this head, §6 refuses it (see the docstring)"
        else:
            k = "CORE-opening, not STOP, not §7.4-acceptable, still refused"
        out[k] += 1
    return out


def _flat(s: str) -> str:
    return _re.sub(r"[^0-9a-zà-ÿ]", "", s.lower())


def missing_gaps(lines: list, section: str) -> Counter:
    """Is the work a `missing_reference` names actually absent?

    `missing_reference` says a citation's candidate key matched no reference.
    It does not say the paper failed to list the work, and the difference is
    the whole question for the review: an author's omission is the paper's
    problem, a reference the extractor could not read is ours.

    Mirrors UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md's method in the other
    direction, and orders the tests so the narrowest explanation wins.

    THE THIRD GROUP IS NOT A DEFECT, AND IT LOOKS EXACTLY LIKE ONE
    -------------------------------------------------------------
    Three keys differ from a real reference key only by punctuation:
    `kabatzinn|2003` against `kabat-zinn|2003`, and the same for
    `donaldson-feilder`. That reads as the two sides normalising hyphens
    differently, which would be a reconciliation defect on both sides at
    once.

    It is not. The manuscript itself carries both spellings — `Kabat-Zinn,
    2003` in four places and `KabatZinn, 2003` in one — so the conversion
    dropped the hyphen in a single occurrence and the extractor is reporting
    that occurrence accurately. Checked in the canonical bytes before the
    conclusion was written, because every field in the output agrees with the
    defect reading and only the manuscript disagrees.
    """
    out: Counter = Counter()
    secflat = _flat(section)
    refkeys = {r["reference_key"] for r in lines
               if r.get("type") == "reference" and r.get("reference_key")}
    flatrefs = {_flat(k) for k in refkeys}
    refused = [r["text"].lower() for r in lines
               if r.get("type") == "unresolved_reference"]
    for r in lines:
        if r.get("type") != "missing_reference":
            continue
        ck = r["candidate_key"]
        _kind, phrase, year = ce._split_key(ck)
        if _flat(ck) in flatrefs:
            k = "same work, the two sides spell the surname differently"
        elif any(phrase in t and year in t for t in refused):
            k = "in a bibliography line the reference grammar refused"
        elif _flat(phrase) in secflat:
            k = "surname IS in the references section, this year is not"
        else:
            k = "surname appears nowhere in the references section"
        out[k] += 1
    return out


def ambiguity_sources(lines: list) -> tuple[Counter, list]:
    """How many keys are behind the `ambiguous_citation` records, and can the
    source tell the works apart when the key cannot?

    §8.3 rows 3 and 5 emit this when a candidate key maps to more than one
    reference row. Seventeen records is not seventeen questions: several
    occurrences can hit the same duplicated key, and the review's unit is the
    key.

    The second question is the interesting one. rc2 builds identity from the
    FIRST surname and the year, and checks author structure separately in
    §9.3. So a paper citing two 2015 works by the same first author produces
    a nonunique key even when its own text distinguishes them, and on this
    corpus that is what happens in every case: not one of the five pairs is a
    duplicated reference, and not one manuscript uses a letter suffix. They
    disambiguate by author list, which `visible_authors` already carries.

    Reported, not judged. rc2 separating identity from author structure looks
    deliberate rather than overlooked, so whether identity should read the
    author list is a specification question and not this file's.
    """
    out: Counter = Counter()
    detail: list = []
    refs = {r["index"]: r for r in lines if r.get("type") == "reference"}
    dup = {r["reference_key"] for r in lines
           if r.get("type") == "duplicate_reference_key"}
    seen_keys = set()
    for r in lines:
        if r.get("type") != "ambiguous_citation":
            continue
        out["records"] += 1
        k = r["citation_key"]
        if k not in seen_keys:
            seen_keys.add(k)
            out["distinct keys behind them"] += 1
            out["...also a duplicate_reference_key" if k in dup
                else "...NOT a duplicate_reference_key"] += 1
            rows = [refs[i]["assembled"] for i in r.get("reference_indices", [])
                    if i in refs]
            # Same work twice would be a reference-side defect. Different
            # works is the paper citing two things the key cannot separate.
            same = len(rows) == 2 and rows[0][:40] == rows[1][:40]
            out["...the rows are the same work" if same
                else "...the rows are different works"] += 1
            detail.append((k, rows))
    for r in lines:
        if r.get("type") != "citation":
            continue
        if r.get("citation_key") in seen_keys:
            va = r.get("visible_authors") or []
            out["occurrences on an ambiguous key, one visible author"
                if len(va) < 2 else
                "occurrences on an ambiguous key, author list visible"] += 1
    return out, detail


def structure_coverage(lines: list) -> Counter:
    """How much of the corpus rc2 §9.3's author-structure check can reach.

    §7.4 anchors `reference_author_head` on "the text before the opening `(`
    immediately containing the first YEAR token". A reference written
    `Agle, B. R., Mitchell, R. K., & Sonnenfeld, J. A. 1999.` has no such
    parenthesis, so the closed person-list parser never runs on it, and §7.4's
    own fallback then says what follows:

        Because `authors` and `author_count` are null, the entry takes no
        part in author-structure validation.

    So this is specified behaviour and the extractor is faithful to it. What
    rc2 does not state, and what C-062 and C-063 being MET does not state
    either, is how much of a corpus falls into that path. MET means the rule
    holds where it runs. It has never meant the rule runs everywhere, and on
    this corpus a third of the person references are outside it.

    That gap is why this block exists rather than a defect claim. Whether a
    check that cannot see a third of the bibliography is sufficient for freeze
    is the review's call; the number is not.
    """
    out: Counter = Counter()
    for r in lines:
        if r.get("type") != "reference" or not r.get("reference_key"):
            continue
        if r.get("author_kind") != "person":
            continue
        out["person references carrying a key"] += 1
        if r.get("authors") is not None:
            out["  ...§9.3 can check them"] += 1
            continue
        out["  ...authors is null, so §9.3 takes no part"] += 1
        # Which of §7.4's two null paths. The parenthesis is the anchor, so
        # its absence is the one that takes a whole citation style out.
        head = r["assembled"][:120]
        if _re.search(r"\((?:1[5-9]|20)\d{2}", head):
            out["      parenthesised year, so the list itself was unparsed"] += 1
        else:
            out["      BARE year, so §7.4 never located an author head"] += 1
    return out


def main() -> int:
    if not CORPUS.is_dir():
        print(f"  corpus not found at {CORPUS}")
        return 2

    groups: Counter = Counter()
    recall: Counter = Counter()
    causes: Counter = Counter()
    refusals: Counter = Counter()
    gaps: Counter = Counter()
    amb: Counter = Counter()
    cover: Counter = Counter()
    unreadable: list = []
    by_scope: dict[str, Counter] = {"eleven": Counter(), "extra": Counter()}
    orphan_by_source: dict[str, list[int]] = {}
    refused = []
    papers = sorted(CORPUS.glob("*.md"))

    for p in papers:
        stem = p.name[:8]
        scope = "eleven" if stem in ELEVEN else "extra"
        try:
            lines, _code = ce.run(p, set(ce.FIXES))
        except ce.Abort as e:
            refused.append((stem, scope, f"exit {e.args[0]}"))
            continue
        # The recall re-derivation, per paper. "Same span, not the same
        # document" is the whole method: an earlier attempt matched surname
        # and year independently across all failed spans and counted
        # coincidence, so the containment test stays inside one span.
        failed = [r["text"].lower() for r in lines
                  if r.get("type") == "unresolved_citation"]
        for r in lines:
            if r.get("type") != "uncited_reference":
                continue
            _kind, phrase, year = ce._split_key(r["reference_key"])
            if any(phrase in span and year in span for span in failed):
                if r["reference_key"].startswith("non_person|"):
                    recall["non_person_matched"] += 1
                else:
                    recall["person_matched"] += 1
            recall["uncited"] += 1

        ctext = canonical_text(p, set(ce.FIXES), lines[0])
        if ctext is None:
            unreadable.append(stem)
        else:
            causes.update(orphan_causes(lines, ctext))
            _b, _sec, *_rest = ce.split_body_and_references(ctext)
            gaps.update(missing_gaps(lines, _sec))
        refusals.update(grammar_refusals(lines))
        _a, _d = ambiguity_sources(lines)
        amb.update(_a)
        cover.update(structure_coverage(lines))

        source = lines[0].get("references_source")
        refs = orph = 0
        for r in lines:
            t = r.get("type")
            if t == "reference":
                refs += 1
            if t not in SUBKEY:
                continue
            field = SUBKEY[t]
            key = (t, r.get(field) if field else None)
            groups[key] += 1
            by_scope[scope][key] += 1
            if key == ("unresolved_reference", "orphan_line"):
                orph += 1
        d = orphan_by_source.setdefault(source, [0, 0])
        d[0] += refs
        d[1] += orph

    total = sum(groups.values())
    print(f"  corpus {CORPUS.relative_to(REPO)}, {len(papers)} papers, "
          f"{total} findings\n")

    # ---- the scope question C-081 leaves open --------------------------
    seen_extra = {p.name[:8] for p in papers} - ELEVEN
    n_eleven = sum(by_scope["eleven"].values())
    n_extra = sum(by_scope["extra"].values())
    print(f"  C-081 names an ELEVEN-paper corpus. This one holds "
          f"{len(papers)}.")
    print(f"    the eleven          {n_eleven:5d} findings")
    print(f"    {len(seen_extra)} outside the eleven {n_extra:5d} findings   "
          f"{', '.join(sorted(seen_extra))}")
    print(f"    {n_extra / total:.0%} of the findings come from papers the "
          f"case does not name.\n")

    # ---- dispositioned against not --------------------------------------
    disposed_n = sum(n for k, n in groups.items() if k in DISPOSED)
    print(f"  dispositioned  {disposed_n:5d}")
    for key in sorted(DISPOSED, key=str):
        verdict, rule, doc, want = DISPOSED[key]
        got = groups.get(key, 0)
        t, sub = key
        label = f"{t}/{sub}" if sub else t
        print(f"    {label:44s} {got:5d}  {verdict}, {rule}")
        print(f"      {doc}")

    residue = {k: n for k, n in groups.items() if k not in DISPOSED}
    print(f"\n  NOT dispositioned  {sum(residue.values()):5d}")
    for key, n in sorted(residue.items(), key=lambda kv: -kv[1]):
        t, sub = key
        label = f"{t}/{sub}" if sub else t
        note = UNDISPOSED_NOTE.get(key, "")
        print(f"    {label:44s} {n:5d}")
        if note:
            for chunk in _wrap(note, 68):
                print(f"        {chunk}")

    # ---- one pattern inside the residue, with its confound --------------
    #
    # 196 orphan lines is the single largest group, and it is not spread
    # evenly. Stated as a correlation, because the two readings cannot be
    # separated from this corpus: the four papers that reach their
    # bibliography through §4.3's inferred fallback are EXACTLY the four
    # Mathpix converted badly enough to lose the heading, so "the fallback
    # costs this" and "these papers are in worse shape" predict the same
    # numbers.
    print("\n  where the orphan lines are")
    for src in sorted(orphan_by_source):
        r, o = orphan_by_source[src]
        if r + o:
            print(f"    {src:10s} {r:4d} references {o:4d} orphan   "
                  f"{o / (r + o):5.1%} of lines orphaned")

    print("\n  why no entry was open, per rc2 §7.1's own five rules")
    runs = causes["after a BLANK line, rule 1 closed the entry"]
    if unreadable:
        # The conclusion below is drawn over whatever loaded. Printing it
        # above the caveat is how a partial run reads as a whole one, so the
        # caveat replaces it instead of following it. Found by removing one
        # of rc3 D1's transforms from the reproduction: twelve of thirteen
        # papers refused, and the paragraph still said "one rule accounts
        # for all of them" over the seven that were left.
        print(f"    NOT ANALYSED. The canonical bytes could not be "
              f"reproduced for")
        print(f"    {len(unreadable)} paper(s): {', '.join(unreadable)}.")
        print(f"    Every line lookup indexes that string, so a partial "
              f"answer here would")
        print(f"    be a wrong one rather than a smaller one.")
    else:
        for k, n in causes.most_common():
            print(f"    {n:5d}  {k}")
    if runs and not unreadable:
        print(f"\n    One rule accounts for all of them. Rule 1 — a blank "
              f"line closes the")
        print(f"    open entry — fires inside bibliographies whose conversion "
              f"put a blank")
        print(f"    line in the middle of an entry, and the entry's remaining "
              f"lines have")
        print(f"    nothing to attach to. Rule 2 causes none of these and no "
              f"section opens")
        print(f"    with one.")
        print(f"\n    So the review has {runs} decisions, not "
              f"{sum(causes.values())}. The rest are the")
        print(f"    cascade: once a line fails to attach, every line after it "
              f"fails too,")
        print(f"    until the next ENTRY_START.")
        print(f"\n    This also dissolves the inferred/detected gap above "
              f"rather than")
        print(f"    explaining it away. Both are downstream of the same "
              f"conversion damage:")
        print(f"    the papers that lost their heading are the papers with "
              f"blank lines")
        print(f"    inside entries. §4.3's fallback is what let them run at "
              f"all, not what")
        print(f"    costs them their tails.")

    print("\n  no_grammar_match, by the first declared production that "
          "refuses the span")
    for k, n in refusals.most_common():
        print(f"    {n:5d}  {k}")
    print("    Six groups, and only the last two are open questions about "
          "the grammar.")
    print("    A year with no author and a span with no CORE are the "
          "envelope catching")
    print("    prose, which C-010 and C-011 make the correct outcome rather "
          "than a drop.")

    if cover:
        print("\n  how much of the bibliography rc2 §9.3 can actually check")
        for k in ("person references carrying a key",
                  "  ...§9.3 can check them",
                  "  ...authors is null, so §9.3 takes no part",
                  "      BARE year, so §7.4 never located an author head",
                  "      parenthesised year, so the list itself was unparsed"):
            if cover.get(k):
                print(f"    {cover[k]:5d}  {k}")
        tot = cover["person references carrying a key"]
        null = cover["  ...authors is null, so §9.3 takes no part"]
        if tot:
            print(f"    {null / tot:.0%} of person references take no part in "
                  f"author-structure validation.")
        print("    Specified, not a defect: §7.4 says so in terms. But C-062 "
              "and C-063 read")
        print("    MET, and MET means the rule holds where it runs, never "
              "that it runs")
        print("    everywhere. Nothing before today stated the coverage.")

    if amb:
        print("\n  ambiguous_citation, what is really ambiguous")
        for k in ("records", "distinct keys behind them",
                  "...also a duplicate_reference_key",
                  "...NOT a duplicate_reference_key",
                  "...the rows are different works",
                  "...the rows are the same work",
                  "occurrences on an ambiguous key, author list visible",
                  "occurrences on an ambiguous key, one visible author"):
            if amb.get(k):
                print(f"    {amb[k]:5d}  {k}")
        print("    Not one pair is a duplicated reference and not one "
              "manuscript uses a")
        print("    letter suffix. They tell the works apart by author list, "
              "which the")
        print("    output already carries in visible_authors and the key does "
              "not use.")
        print("    rc2 checks author structure separately in §9.3, so that "
              "reads as a")
        print("    deliberate split rather than an oversight. A specification "
              "question.")

    if gaps:
        print("\n  missing_reference, is the work really absent?")
        for k, n in gaps.most_common():
            print(f"    {n:5d}  {k}")
        print("    Only the last group is a plausible author omission. The "
              "other three are")
        print("    the extractor or the conversion, and each is a narrower "
              "question than")
        print("    \"are these 32 real\".")

    # ---- the one figure the residue notes lean on, re-derived ------------
    pm, npm, unc = (recall["person_matched"], recall["non_person_matched"],
                    recall["uncited"])
    print(f"\n  uncited_reference, re-derived by {RECALL_DOC}'s own method")
    print(f"    emitted                              {unc:4d}")
    print(f"    the reference IS cited, person key   {pm:4d}   "
          f"the document's population")
    print(f"    the reference IS cited, non_person   {npm:4d}   "
          f"its method does not reach these")
    print(f"    plausible residual, person only      {unc - pm:4d}")
    print(f"    plausible residual, both shapes      {unc - pm - npm:4d}")
    print("    A reference the paper cites, reported as uncited, is a false")
    print("    reconciliation diagnostic. Classifying it is the review's.")

    if refused:
        print("\n  refused by the extractor, deliberately")
        for stem, scope, why in refused:
            where = "in the eleven" if scope == "eleven" else "outside"
            print(f"    {stem}  {why}  ({where})")

    # ---- guards ---------------------------------------------------------
    #
    # A disposition table drifts in two directions and both are silent. A
    # group the corpus produces that the table has never heard of reads as
    # "nothing to disposition". A table entry with no findings behind it
    # reads as coverage that is not covering anything.
    problems = []
    unknown = [k for k in groups
               if k not in DISPOSED and k not in UNDISPOSED_NOTE]
    if unknown:
        problems.append(f"finding groups this file has never heard of, so "
                        f"they were counted as neither: {sorted(map(str, unknown))}")
    for key, (_v, _r, _d, want) in DISPOSED.items():
        got = groups.get(key, 0)
        if got == 0:
            problems.append(f"{key} is dispositioned and the corpus produces "
                            f"none of it; the disposition covers nothing")
        elif got != want:
            problems.append(f"{key} was dispositioned over {want} findings "
                            f"and the corpus now produces {got}. The "
                            f"disposition was written about a different set")
    for key in UNDISPOSED_NOTE:
        if key not in groups and key not in DISPOSED:
            problems.append(f"{key} is listed as undispositioned and the "
                            f"corpus produces none of it")
    if unreadable:
        problems.append(
            f"the canonical bytes could not be reproduced for "
            f"{', '.join(unreadable)}, so the orphan analysis ran over part "
            f"of the corpus and was suppressed rather than reported small")
    if causes and sum(causes.values()) != groups.get(
            ("unresolved_reference", "orphan_line"), 0):
        problems.append(
            f"the orphan analysis accounted for {sum(causes.values())} lines "
            f"and the corpus emitted "
            f"{groups.get(('unresolved_reference', 'orphan_line'), 0)}. A "
            f"partition that does not add up is not a partition")
    drift = {k: (RECALL_PINNED[k], recall[k]) for k in RECALL_PINNED
             if RECALL_PINNED[k] != recall[k]}
    if drift:
        problems.append(
            f"the recall figures moved: "
            f"{', '.join(f'{k} {a} -> {b}' for k, (a, b) in drift.items())}. "
            f"{RECALL_DOC} quotes these, so the document is now wrong and the "
            f"move has to be explained before the pin is touched")

    print()
    if problems:
        print("  this file could not do its job:\n")
        for p_ in problems:
            for chunk in _wrap(p_, 70):
                print(f"    {chunk}")
        return 1

    if residue:
        print(f"  C-081 is NOT met. {sum(residue.values())} of {total} "
              f"findings carry no disposition,")
        print(f"  across {len(residue)} groups. rc2's classification rule is "
              f"explicit that an")
        print(f"  undocumented expectation is not a waiver, so these cannot "
              f"be counted")
        print(f"  as non-blocking by default.")
        print()
        print(f"  Whether each is blocking is a freeze-review judgement and "
              f"not this")
        print(f"  script's. What this run establishes is the size and shape "
              f"of what")
        print(f"  the review has to rule on.")
        return 1

    print(f"  every one of the {total} findings carries a disposition citing "
          f"a rule.")
    return 0


def _wrap(s: str, width: int) -> list[str]:
    out, line = [], ""
    for word in s.split():
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


if __name__ == "__main__":
    sys.exit(main())
