#!/usr/bin/env python3
"""Count each known citation edge case across the whole corpus.

    python scripts/edge_case_census.py
    python scripts/edge_case_census.py --detail EC-5

Exit 0 always; this measures, it does not judge.

Why
---
`CITATION-EDGE-CASES.md` describes five edge cases and `ADJUDICATION-paper-*.md`
two more findings, and every one of them ends "needs a decision, not a repair".
Those decisions are sitting with one person, and most of them arrived with a
count from one or two papers — the two that have gold sets, which are also the
two that have been read closely. That is a biased sample by construction: they
are the papers someone looked at.

This runs the same detectors over all fourteen, so a decision about whether to
amend §6.1 or §3 can be made against what the corpus contains rather than
against what two papers happened to show.

What each detector is worth
---------------------------
Stated per row in the output, because they are not equally solid. Three are
exact — they read the extractor's own output for a structural property. Three
are pattern matches over unresolved spans and will drift from the true count in
both directions. The distinction is printed, not buried here, since a census
whose rows look alike but are not is the failure mode this repository keeps
finding.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "scripts" / "citation_extract.py"
CORPUS = REPO / "data" / "md_full"
FIXES = {"ampersand", "segments", "colon", "cp"}

EXACT, PATTERN = "exact", "pattern"


def load(name: str, text: str):
    d = Path(tempfile.mkdtemp())
    (d / "m.py").write_text(text, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, d / "m.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(mod, raw: bytes):
    """The CLI's pipeline, not extract_citations on its own.

    citation_extract.run() applies the ampersand correction to the body and the
    reference section *before* extraction, because \\& is a property of the
    markdown rather than of the grammar. Calling extract_citations directly and
    passing "ampersand" in the fix set looks like it applies the correction and
    does not — the flag is read inside extract_citations for other purposes, so
    nothing errors and the count just comes out low.

    Every ad-hoc corpus measurement made on 18 September took that shortcut and
    understated its numbers. This mirrors the CLI instead.
    """
    text = mod.normalise(raw)
    body, section, off, heads = mod.split_body_and_references(text)
    if "ampersand" in FIXES:
        body = body.replace("\\&", "&")
        section = section.replace("\\&", "&")
    cits, unres = mod.extract_citations(body, mod.sentences(body), heads, set(FIXES))
    return body, section, cits, unres


PARTICLES = ("de|del|della|der|den|di|da|dos|du|la|le|van|von|ter|ten|zu|zur")
INTERNAL_PARTICLE = re.compile(
    rf"\b[A-ZÀ-Þ][\w'’-]+\s+(?:{PARTICLES})\s+[A-ZÀ-Þ][\w'’-]+", re.I)
ET_AL_NO_DOT = re.compile(r"\bet\s+al\s*,", re.I)
LEADING_CONJ = re.compile(r"^(?:and|&)\s")
FOOTNOTE_BLOCK = re.compile(r"^\[\^[^\]]+\]:.*(?:\n(?!\[\^).*)*", re.M)

HEAD = "# P\n\n## Introduction\n\n"
TAIL = "\n\n## References\n\nSmith, J. (2020). A paper. Journal, 1(1), 1-10.\n"


def census(real, cap8, path: Path) -> dict | None:
    raw = path.read_bytes()
    try:
        body, refs, cits, unres = run(real, raw)
    except real.Abort as a:
        return {"abort": a.code}

    row: dict = {"abort": None, "parsed": len(cits), "unresolved": len(unres)}

    # EC-2 — exact: the possessive survives into the key.
    row["EC-2"] = sum(1 for c in cits if "'s|" in c["citation_key"]
                      or "’s|" in c["citation_key"])

    # EC-3 — exact: records that change when the envelope is widened to 8.
    try:
        _, _, c8, _ = run(cap8, raw)
        row["EC-3"] = len({(c["citation_key"], c["group_start"]) for c in cits}
                          - {(c["citation_key"], c["group_start"]) for c in c8})
    except cap8.Abort:
        row["EC-3"] = None

    # EC-5 — exact: citations that parse when a footnote body is read as body.
    n5 = 0
    for blk in FOOTNOTE_BLOCK.findall(refs):
        clean = re.sub(r"^\[\^[^\]]+\]:\s*", "", blk).replace("\n", " ")
        try:
            _, _, fc, _ = run(real, (HEAD + clean + TAIL).encode())
            n5 += len(fc)
        except real.Abort:
            pass
    row["EC-5"] = n5

    # The rest read unresolved spans, so they are patterns and can miss or
    # over-count. A span is counted once even if it carries two of these.
    texts = [u["text"] for u in unres]
    row["EC-1"] = sum(1 for t in texts if LEADING_CONJ.match(t))
    row["EC-4"] = sum(1 for t in texts if INTERNAL_PARTICLE.search(t))
    row["et al"] = sum(1 for t in texts if ET_AL_NO_DOT.search(t))
    row["instit."] = sum(1 for u in unres if u["reason"] == "all_caps_surname")
    return row


COLS = [("EC-1", PATTERN, "coordinated \"and\""),
        ("EC-2", EXACT, "possessive kept in the key"),
        ("EC-3", EXACT, "envelope truncates the author list"),
        ("EC-4", PATTERN, "particle inside the surname"),
        ("EC-5", EXACT, "citation inside a footnote"),
        ("et al", PATTERN, "\"et al\" with no period"),
        ("instit.", EXACT, "all-caps institutional author")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail", help="print the spans behind one column")
    a = ap.parse_args()

    src = SRC.read_text(encoding="utf-8")
    real = load("real", src)
    cap8 = load("cap8", src.replace("    while len(toks) < 6:",
                                    "    while len(toks) < 8:"))

    papers = sorted(CORPUS.glob("*.md"))
    rows = {p.stem[:8]: census(real, cap8, p) for p in papers}

    if a.detail:
        return detail(real, cap8, papers, a.detail)

    hdr = f"{'paper':10s} {'parsed':>7s} {'unres':>6s}" + \
          "".join(f"{c:>9s}" for c, _, _ in COLS)
    print(hdr)
    print("-" * len(hdr))
    tot = {c: 0 for c, _, _ in COLS}
    inprofile = 0
    for stem, r in rows.items():
        if r["abort"] is not None:
            print(f"{stem:10s} {'exit ' + str(r['abort']):>7s}"
                  f"{'  — not in profile, no references section found':>0s}")
            continue
        inprofile += 1
        line = f"{stem:10s} {r['parsed']:>7d} {r['unresolved']:>6d}"
        for c, _, _ in COLS:
            v = r[c]
            line += f"{'?' if v is None else v:>9}"
            if v: tot[c] += v
        print(line)
    print("-" * len(hdr))
    print(f"{'TOTAL':10s} {'':>7s} {'':>6s}" +
          "".join(f"{tot[c]:>9d}" for c, _, _ in COLS))
    print(f"\n{inprofile} in-profile papers of {len(papers)}.\n")

    print("how each column is counted:")
    for c, kind, what in COLS:
        mark = "exact  " if kind == EXACT else "pattern"
        print(f"  {c:<8} {mark}  {what}")
    print()
    print("  exact    read from the extractor's own output, or from rerunning it")
    print("           with one rule changed. The number is what it says.")
    print("  pattern  matched against the text of unresolved spans. These will")
    print("           miss forms nobody has seen yet and can count one span")
    print("           twice under different columns. Treat as a floor, not a")
    print("           measurement.")
    return 0


def detail(real, cap8, papers, which: str) -> int:
    print(f"spans behind {which}\n")
    for p in papers:
        try:
            body, refs, cits, unres = run(real, p.read_bytes())
        except real.Abort:
            continue
        hits = []
        if which == "EC-2":
            hits = [f"{c['citation_key']:<24} {c['author_phrase']}"
                    for c in cits if "'s|" in c["citation_key"]]
        elif which == "EC-3":
            _, _, c8, _ = run(cap8, p.read_bytes())
            keyed = {(c["citation_key"], c["group_start"]) for c in c8}
            hits = [f"{c['citation_key']:<24} {c['author_phrase']}"
                    for c in cits if (c["citation_key"], c["group_start"]) not in keyed]
        elif which == "EC-5":
            for blk in FOOTNOTE_BLOCK.findall(refs):
                clean = re.sub(r"^\[\^[^\]]+\]:\s*", "", blk).replace("\n", " ")
                try:
                    _, _, fc, _ = run(real, (HEAD + clean + TAIL).encode())
                except real.Abort:
                    continue
                hits += [f"{c['author_phrase']} ({c['year']})" for c in fc]
        else:
            pat = {"EC-1": LEADING_CONJ, "EC-4": INTERNAL_PARTICLE,
                   "et al": ET_AL_NO_DOT}.get(which)
            if pat is None:
                print(f"no detail available for {which!r}")
                return 0
            hits = [u["text"] for u in unres
                    if (pat.match(u["text"]) if which == "EC-1"
                        else pat.search(u["text"]))]
        if hits:
            print(f"  {p.stem[:8]}")
            for h in hits:
                print(f"      {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
