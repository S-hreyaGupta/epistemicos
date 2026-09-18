#!/usr/bin/env python3
"""Turn the hand-annotated citation spreadsheet into frozen gold sets.

    python scripts/build_citation_gold.py --xlsx <sheet.xlsx> --out specs/gold/

Exit 0 = gold sets written, with a stated count.
Exit 1 = refused; nothing written.

Provenance
----------
The annotation is Alex Zamurko's and Mohit's, 17 September 2026: the in-text
citations and reference list of two manuscripts, read and written out by hand.
That is what makes it a gold set. It was produced without reference to any
extractor output, which is the property the whole exercise depends on and the
one thing this script cannot verify — it sees a spreadsheet, not how it was made.

What these gold sets measure, and what they do not
--------------------------------------------------
**Distinct works, not occurrences.** The annotation lists each cited work once.
The extractor emits an occurrence every time a work is cited, and the corpus run
of 29 August put that at roughly 2.1 occurrences per source. So:

    recall here    = of the works the paper cites, how many did the extractor
                     find at least once
    NOT            = of the citation occurrences in the text, how many were
                     extracted

Both are worth knowing and they are not the same number. The second needs an
occurrence-level annotation, which this is not. Scoring occurrence output
against a work-level gold set without saying so would report a precision figure
that is mostly an artefact of repeated citations.

Identity
--------
`key_fields` is `author_phrase_normalised + year`, where the normalisation is
lowercase and collapsed whitespace and nothing else.

Deliberately not first-surname. Reducing "Carrieri de Souza et al., 2023" to a
surname requires deciding where the surname ends, and that decision is the
grammar under test — rc3 §B1a exists because the current one gets it wrong.
A gold set that applied the same rule would agree with the extractor by
construction on exactly the cases in dispute.

The cost is that the candidate must supply the author phrase it read, not the
key it derived. A candidate emitting only `person|souza|2023` cannot be scored
against this without a mapping, and building that mapping here would reintroduce
the problem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Which spreadsheet column holds what. Zero-based, from the sheet as received:
# an index column, then the values, twice per paper.
LAYOUT = {
    "paper-1": {"in_text": 1, "references": 4},
    "paper-2": {"in_text": 7, "references": 10},
}

# Identified by matching distinctive names against the 29 August corpus run.
# Paper 1 carries Kim and Davis 2016, Sharma et al. 2019a and Bloomberg;
# paper 2 carries Carrieri de Souza, Ellen MacArthur and Wezel.
CORPUS_ID = {"paper-1": "ad1e3ff9", "paper-2": "c1d56945"}

# The manuscripts the annotation was made from, by hash rather than by filename.
# Alex Zamurko sent them as `4_5861686162019590604.pdf` and
# `paper_2_review_input_manuscript_v1.pdf`; the first is byte-identical to the
# `paper_1_review_input_manuscript_v1` that has been through this pipeline four
# times, so the names travelled and the bytes did not.
#
# Recorded here so the gold set names the document it describes. It is NOT the
# `source` the runner checks: the extractor reads Mathpix markdown, not the PDF,
# and the two have different hashes by definition. Binding to the markdown needs
# papers.markdown for these rows, which is a database query, and until that is
# done the runner will say the score rests on an unverified assumption that gold
# and candidate describe the same text.
MANUSCRIPT_PDF = {
    "paper-1": "209af10a1a02c047b089d572a74dd99b48873a31c3d85701b8e98c77334b37f2",
    "paper-2": "c4d19c6fb53965655e60209dff785b05d5bfa1757f08f2c5aadf52ef0780e3b8",
}

# `papers.markdown` for those two rows: the bytes the extractor actually reads,
# and therefore what the gold set has to be bound to. The PDF hashes above are
# provenance for the annotation; these are the source of the comparison.
#
# They are not the same documents. The corpus rows were built from a different
# copy of each paper, established 17 September by comparing hashes, and the
# difference was then measured rather than assumed: 192 of the 193 annotated
# citations appear in these bytes. The one that does not is recorded in
# ABSENT_FROM_SOURCE below.
CORPUS_MARKDOWN = {
    "paper-1": "cff9bb85d74fbac8ffd69fd0c258812cb1d051b2963cbc8b8df8ebe447264615",
    "paper-2": "48b2b2f459e5cad88b7105048a0d7e0f852084764662a9e67155de52b52921d8",
}

# Annotated citations that are genuinely not in the bound source, with the
# reason. Scoring an extractor for missing a citation that is not in the text
# it was given would charge it for the corpus holding a different copy.
#
# `Wang et al., 2018` appears exactly once in the annotated PDF, inside a
# methods table listing sampling steps. That table is absent from the corpus
# copy entirely — `Step 4`, `Step 5`, `Isolate 245`, `NACE`, `CIE_DES` and
# `27,973` are all in the annotated PDF and none of them is in the corpus
# markdown. So the annotated copy is the fuller of the two, and the versions
# differ by one appendix table holding one citation.
#
# Kept in `items` rather than deleted. The annotation is what the annotator
# read, and deleting an entry would make the gold set describe a document
# nobody annotated. It is flagged, and the runner excludes flagged items from
# scoring and says how many it excluded.
ABSENT_FROM_SOURCE = {
    "paper-1": {
        "wang et al.|2018":
            "the paper's only occurrence is inside a methods table that the "
            "corpus copy of this paper does not contain. Verified by the "
            "absence of Step 4, Step 5, Isolate 245, NACE, CIE_DES and 27,973 "
            "from the corpus markdown, all of which are present in the "
            "annotated PDF.",
    },
    "paper-2": {},
}

YEAR = re.compile(r"\b((?:1[89]|20)\d{2}[a-z]?(?:,[a-z])*)\b")

# Written as a literal rather than with \b after the optional period. The
# obvious `\bet\s*al\.?\b` cannot match "et al." at all: after the "." the next
# character is a space, and two non-word characters give no boundary, so it
# strips "et al" and leaves a stray period behind. The first version of the
# verification below did that and reported 79 of 193 annotated citations
# missing from manuscripts that contained every one of them.
ET_AL = re.compile(r"\bet\s*al\b\.?")


def flatten(s: str) -> str:
    """Case, accents, dash variants and whitespace removed; nothing else.

    Manuscript text extracted from a PDF breaks names across lines and pages,
    so a search for an author has to be done against text whose line structure
    has been collapsed. `grep` on the raw extraction finds nothing for exactly
    this reason and would suggest the annotation was wrong.

    Dashes are folded because they differ between annotation and corpus without
    the name differing. `Brix‐Asala` carries U+2010 in the annotation and U+002D
    in the corpus markdown, and NFKD folds neither to the other, so the entry
    read as absent from a document containing it twice. That was the only one of
    191 bibliography entries to fail the check, and the fault was here.
    """
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # Every Unicode dash, and the minus sign, to an ASCII hyphen.
    s = "".join("-" if unicodedata.category(c) == "Pd" or c == "−" else c
                for c in s)
    return re.sub(r"\s+", " ", s).strip().lower()


def first_author(phrase: str) -> str:
    a = ET_AL.sub("", flatten(phrase))
    a = re.split(r"\band\b|&", a)[0]
    return a.strip().strip(".,;").strip()


# A trailing run of initials, for reference entries written "Surname A.B.,"
# with no comma after the surname. Five of the 191 are in that form.
TRAILING_INITIALS = re.compile(r"\s+(?:[A-Za-z]\.?){1,4}$")


def reference_key(entry: str) -> tuple[str, str] | None:
    """(author field, year) for one bibliography entry, positionally.

    No grammar. The year is located, the text before it is the author field,
    and the surname is what precedes the first comma inside that field — which
    works because a reference list puts the surname first.

    That last rule is why it is the first comma *before the year* and not the
    first comma in the entry. An institutional author has no forename, so no
    comma follows the name: `Bloomberg. (2011). Supply Chain on Bloomberg.
    Retrieved December 7, 2018` has its first comma deep in the retrieval date,
    and splitting there returned most of the entry as the author. Taking the
    pre-year text first bounds it, which is also what rc3's NON_PERSON_AUTHOR
    does: bounded by the start of the entry and the year.

    Deliberately positional. Deciding whether `Carrieri de Souza` is a
    multi-token surname or a surname plus a forename is the grammar under test,
    and a gold set that decided it would agree with the extractor by
    construction on the cases in dispute.
    """
    m = REF_YEAR.search(entry)
    if not m:
        return None
    year = m.group(1) or m.group(2)
    pre = entry[:m.start()]
    author = pre.split(",")[0] if "," in pre else pre
    author = author.strip().strip(".,;:").strip()
    author = TRAILING_INITIALS.sub("", author).strip()
    return (author, year) if author else None


# Parenthesised year first, because an entry may carry a date in its title or
# its retrieval note and the publication year is the parenthesised one when
# there is one.
REF_YEAR = re.compile(r"\((\d{4}[a-z]?)\)|\b((?:1[89]|20)\d{2}[a-z]?)\b")


class Refused(Exception):
    pass


def split_citation(raw: str) -> tuple[str, str] | None:
    """Author phrase and year, as written. None when there is no year.

    Nothing is repaired here. An entry the annotator wrote without a year is
    reported, not guessed at: "Speich (no year given)" is a fact about the
    manuscript and inventing a year would delete it.
    """
    s = raw.strip().strip("()").strip()
    m = YEAR.search(s)
    if not m:
        return None
    author = s[:m.start()].rstrip(" ,;:")
    return author, m.group(1)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="build_citation_gold.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--out", default="specs/gold")
    ap.add_argument("--annotator", default="Alex Zamurko and Mohit")
    ap.add_argument("--annotated", default="2026-09-17")
    ap.add_argument("--verify-against", action="append", default=[],
                    metavar="PAPER=TEXTFILE",
                    help="e.g. paper-1=/tmp/paper-1.txt — check every "
                         "annotated citation appears in the manuscript")
    a = ap.parse_args()

    verify: dict[str, Path] = {}
    for spec in a.verify_against:
        if "=" not in spec:
            raise Refused(f"--verify-against wants PAPER=TEXTFILE, got {spec!r}")
        k, v = spec.split("=", 1)
        if k not in LAYOUT:
            raise Refused(f"unknown paper {k!r}; expected one of {list(LAYOUT)}")
        p = Path(v).resolve()
        if not p.is_file():
            raise Refused(f"manuscript text not found: {p}")
        verify[k] = p

    try:
        import openpyxl
    except ImportError:
        raise Refused("openpyxl is not installed: pip install openpyxl")

    xlsx = Path(a.xlsx).resolve()
    if not xlsx.is_file():
        raise Refused(f"spreadsheet not found: {xlsx}")
    sheet_sha = hashlib.sha256(xlsx.read_bytes()).hexdigest()

    ws = openpyxl.load_workbook(xlsx, data_only=True).active
    rows = list(ws.iter_rows(values_only=True))

    out_dir = Path(a.out)
    if not out_dir.is_absolute():
        out_dir = REPO / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    summary: list[str] = []
    for paper, cols in LAYOUT.items():
        raw_in, raw_ref, no_year = [], [], []
        for r in rows[2:]:
            for kind, c in cols.items():
                v = r[c] if c < len(r) else None
                if not v or not str(v).strip():
                    continue
                (raw_in if kind == "in_text" else raw_ref).append(str(v).strip())

        items, seen = [], {}
        for s in raw_in:
            parsed = split_citation(s)
            if parsed is None:
                no_year.append(s)
                continue
            author, year = parsed
            k = (flatten(author), year)
            if k in seen:
                # The annotation is a list of distinct works; a repeat is the
                # annotator's, and collapsing it silently would understate the
                # denominator by an amount nobody could recover.
                seen[k] += 1
                continue
            seen[k] = 1
            item = {
                "author_phrase": flatten(author),
                "year": year,
                "as_annotated": s,
            }
            why = ABSENT_FROM_SOURCE.get(paper, {}).get(
                f"{flatten(author)}|{year}")
            if why:
                item["absent_from_source"] = why
            items.append(item)

        doc = {
            "gold_set": f"citation-{paper}-v0.1",
            "unit": "distinct cited work",
            "not_unit": "citation occurrence — see the module docstring",
            "corpus_paper": CORPUS_ID[paper],
            "key_fields": ["author_phrase", "year"],
            "provenance": {
                "annotator": a.annotator,
                "annotated": a.annotated,
                "method": "in-text citations and reference list read from the "
                          "manuscript and written out by hand",
                "independent_of_extractor_output": "asserted by the annotator; "
                                                   "not verifiable from the "
                                                   "spreadsheet",
                "spreadsheet_sha256": sheet_sha,
                "manuscript_pdf_sha256": MANUSCRIPT_PDF[paper],
            },
            "source": {
                "sha256": CORPUS_MARKDOWN[paper],
                "what": "papers.markdown for this row — the bytes the "
                        "extractor reads",
                "corpus_paper": CORPUS_ID[paper],
                "annotated_from_pdf_sha256": MANUSCRIPT_PDF[paper],
                "note": "the annotation was made from a different copy of this "
                        "paper than the corpus holds. 192 of the 193 annotated "
                        "citations across both papers are present in these "
                        "bytes; any that are not carry absent_from_source and "
                        "are excluded from scoring.",
            },
            "reference_list_entries": len(raw_ref),
            "items": items,
        }
        if paper in verify:
            text = flatten(verify[paper].read_text(encoding="utf-8",
                                                   errors="replace"))
            absent = [it["as_annotated"] for it in items
                      if not re.search(re.escape(first_author(it["author_phrase"]))
                                       + r".{0,140}?" + it["year"][:4],
                                       text, re.S)]
            doc["verified_against_manuscript"] = {
                "text_sha256": hashlib.sha256(
                    verify[paper].read_bytes()).hexdigest(),
                "checked": len(items),
                "not_found": absent,
                "means": "each annotated first author appears within 140 "
                         "characters of its year somewhere in the manuscript. "
                         "It establishes that the annotation was not invented. "
                         "It does not establish that the annotation is "
                         "complete — a citation nobody wrote down is invisible "
                         "to this check and is exactly what recall is for.",
            }
            summary.append(f"      verified against manuscript: "
                           f"{len(items) - len(absent)}/{len(items)} found"
                           + (f", MISSING {absent}" if absent else ""))

        if no_year:
            doc["excluded_no_year"] = no_year
        dupes = {f"{k[0]}|{k[1]}": n for k, n in seen.items() if n > 1}
        if dupes:
            doc["annotated_more_than_once"] = dupes

        # ---- the reference list, as its own gold set ----
        # The bibliography side was never measured against anything but the
        # extractor's own detections: #citation reported references at 92.5%,
        # counted from what it found. These 191 entries are what a human read.
        ref_items, ref_seen, ref_unkeyed = [], set(), []
        for s in raw_ref:
            k = reference_key(s)
            if k is None:
                ref_unkeyed.append(s[:80])
                continue
            author, year = k
            kk = (flatten(author), year)
            if kk in ref_seen:
                continue
            ref_seen.add(kk)
            ref_items.append({"author_field": flatten(author), "year": year,
                              "as_annotated": s})

        ref_doc = {
            "gold_set": f"citation-{paper}-references-v0.1",
            "unit": "bibliography entry",
            "corpus_paper": CORPUS_ID[paper],
            "key_fields": ["author_field", "year"],
            "identity_note":
                "author_field is positional: the text before the year, cut at "
                "the first comma within it, with a trailing run of initials "
                "removed. No grammar. Whether an author field is a person or "
                "an organisation is what rc3's C-series decides and is "
                "therefore not decided here.",
            "provenance": {
                "annotator": a.annotator,
                "annotated": a.annotated,
                "method": "reference list read from the manuscript and written "
                          "out by hand",
                "spreadsheet_sha256": sheet_sha,
                "annotated_from_pdf_sha256": MANUSCRIPT_PDF[paper],
            },
            "source": {
                "sha256": CORPUS_MARKDOWN[paper],
                "what": "papers.markdown for this row",
            },
            "items": ref_items,
        }
        if ref_unkeyed:
            ref_doc["unkeyable"] = ref_unkeyed
        ref_dest = out_dir / f"citation-{paper}-references-v0.1.json"
        with ref_dest.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(ref_doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        summary.append(
            f"  {ref_dest.relative_to(REPO).as_posix()}\n"
            f"      {len(ref_items)} bibliography entries"
            + (f"  ·  {len(raw_ref) - len(ref_items)} duplicate key(s) collapsed"
               if len(ref_items) != len(raw_ref) else "")
            + (f"\n      UNKEYABLE: {ref_unkeyed}" if ref_unkeyed else ""))

        dest = out_dir / f"citation-{paper}-v0.1.json"
        with dest.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        summary.append(
            f"  {dest.relative_to(REPO).as_posix()}\n"
            f"      {len(items)} distinct works  ·  {len(raw_ref)} reference "
            f"entries  ·  corpus {CORPUS_ID[paper]}\n"
            f"      sha256 {hashlib.sha256(dest.read_bytes()).hexdigest()}"
            + (f"\n      excluded, no year: {no_year}" if no_year else "")
            + (f"\n      annotated twice: {dupes}" if dupes else ""))

    print("built from " + xlsx.name)
    print(f"  spreadsheet sha256 {sheet_sha}")
    print()
    print("\n".join(summary))
    print()
    print("  Unit is the distinct cited work. Recall against these answers")
    print("  'of the works this paper cites, how many did the extractor find at")
    print("  least once'. It does not answer the occurrence question, which")
    print("  needs a different annotation.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
