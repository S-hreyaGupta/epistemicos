#!/usr/bin/env python3
"""Build gold paper 1 v0.2 from v0.1 plus the five adjudicated omissions.

    python scripts/build_gold_v02.py            # check only, writes nothing
    python scripts/build_gold_v02.py --write

Exit 0 = the set was built (or would be). Exit 1 = refused.

Why a script and not an edited file
-----------------------------------
A gold set is evidence. Editing one by hand leaves no account of what changed
or on what grounds, and the thing being added here is exactly the kind of thing
that needs an account: five works the annotation missed, found by reading the
candidate's output.

`ADJUDICATION-paper-1.md` establishes each of the five — cited in prose, with a
matching entry in the manuscript's own bibliography. That verification is
independent of the extractor, because the authors wrote the bibliography. The
*discovery* is not, and v0.1's provenance block asserts
`independent_of_extractor_output` for its own items, so the additions must not
inherit that claim silently.

So each added item carries its own provenance, the same per-item form Alex
Zamurko approved for the ledger's SOURCE backfill on 18 September: the claim is
attached to the item it is about, rather than to the file as a whole.

Deliberately not added
----------------------
The three table-only works — Basole 2017, Dong 2015, Park et al. 2018 — appear
solely as rows in a "Summary of empirical studies" table. Whether a table of
works counts as citing them is a scope question for the annotation and has not
been answered. They stay out until it is.

The possessives — Bartko 1976, Fine 1998, McGraw and Wong 1996 — are already in
v0.1 and correctly so. The candidate produces `bartko's`; that is EC-2 and is
the extractor's to fix, not the gold set's.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
V01 = REPO / "specs" / "gold" / "citation-paper-1-v0.1.json"
V02 = REPO / "specs" / "gold" / "citation-paper-1-v0.2.json"
SOURCE = REPO / "data" / "md_full"

# author_phrase, year, the text as it actually stands in the manuscript, and
# the first-author surname to look for in the reference list.
#
# `as_annotated` is the whole group, not the segment, because three of these
# five are one work inside a multi-work group and the group is what a reader
# sees. The first draft of this list wrote `(Ellram et al., 2004)`, which
# appears nowhere — Ellram is cited inside
# `(Sampson and Froehle, 2006; Ellram et al., 2004)`. The refusal below caught
# it, which is the reason these are checked against the source rather than
# transcribed from the adjudication.
ADDITIONS = [
    ("bellamy et al.", "2014", "Bellamy et al. (2014)", "Bellamy"),
    ("ellram et al.", "2004",
     "(Sampson and Froehle, 2006; Ellram et al., 2004)", "Ellram"),
    ("sampson and froehle", "2006",
     "(Sampson and Froehle, 2006; Ellram et al., 2004)", "Sampson"),
    ("shao et al.", "2018", "Shao et al. (2018)", "Shao"),
    ("unruh et al.", "2016", "(Unruh et al., 2016; Marquis et al., 2018)",
     "Unruh"),
]


def refuse(msg: str) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write the file; without it, verify and report only")
    a = ap.parse_args()

    gold = json.loads(V01.read_text(encoding="utf-8"))
    items = gold["items"]

    paper = gold["corpus_paper"]
    src = next(SOURCE.glob(paper + "*.md"), None)
    if src is None:
        refuse(f"no source for {paper} in {SOURCE}")
    text = src.read_bytes().decode("utf-8")

    # The source has to be the one v0.1 was annotated against, or the
    # verification below is against different bytes than the gold set is.
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    want = gold["source"]["sha256"]
    if got != want:
        refuse(f"source bytes differ from the ones v0.1 records\n"
               f"  file   {got}\n  v0.1   {want}")
    print(f"source matches v0.1's recorded sha256 ({want[:16]}…)")

    # Split body from references the way the extractor does, so "in the
    # bibliography" means the bibliography and not a mention in the text.
    sys.path.insert(0, str(REPO / "scripts"))
    import citation_extract as ce  # noqa: E402
    body, refs, _, _ = ce.split_body_and_references(ce.normalise(src.read_bytes()))
    entries = [" ".join(l.split()) for l in refs.splitlines() if l.strip()]

    existing = {(i["author_phrase"], i["year"]) for i in items}
    added = []
    print()
    for phrase, year, as_annotated, surname in ADDITIONS:
        if (phrase, year) in existing:
            refuse(f"{phrase} {year} is already in v0.1; this would duplicate it")

        # cited in the body, in prose
        if as_annotated not in body:
            refuse(f"{as_annotated!r} does not appear in the body of {paper}")

        # and present in the manuscript's own reference list
        entry = next((e for e in entries
                      if re.match(rf"^{re.escape(surname)}\s*,", e) and year in e), None)
        if entry is None:
            refuse(f"no reference entry for {surname} {year}; "
                   f"the adjudication says there is one")

        print(f"  {phrase} {year}")
        print(f"      cited      {as_annotated}")
        print(f"      reference  {entry[:88]}")
        added.append({
            "author_phrase": phrase,
            "year": year,
            "as_annotated": as_annotated,
            "added_in": "v0.2",
            "found_by": "candidate_adjudication",
            "found_by_note": (
                "present in the candidate and absent from v0.1; verified here "
                "against the manuscript's own reference list, which the paper's "
                "authors wrote and the extractor cannot produce. The "
                "verification is independent of the extractor; the discovery is "
                "not."),
            "reference_entry": entry,
            "adjudicated_in": "specs/gold/ADJUDICATION-paper-1.md",
        })

    out = dict(gold)
    out["gold_set"] = "citation-paper-1-v0.2"
    out["items"] = items + added
    out["provenance"] = dict(gold["provenance"])
    out["provenance"]["additions"] = {
        "v0.2": {
            "added": "2026-09-18",
            "count": len(added),
            "method": ("works the candidate produced and v0.1 lacked, each "
                       "checked for a prose citation in the body and a matching "
                       "entry in the manuscript's reference list"),
            "independent_of_extractor_output": False,
            "why_not": ("these five were found by reading the candidate's "
                        "output. A different extractor would have surfaced a "
                        "different five, so the set improves in the direction "
                        "this implementation looks. Any score computed against "
                        "v0.2 carries that and is not an independent result."),
            "not_added": {
                "table_only": ["basole et al. 2017", "dong et al. 2015",
                               "park et al. 2018"],
                "why": ("each appears solely as a row in a Summary of empirical "
                        "studies table whose first column is Author-Year, and "
                        "whether that counts as citing them is an open question "
                        "about annotation scope"),
            },
        }
    }

    print(f"\nv0.1 {len(items)} items -> v0.2 {len(out['items'])} items "
          f"({len(added)} added, 3 held back pending the table question)")

    if not a.write:
        print("\ncheck only; pass --write to create the file")
        return 0

    V02.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"wrote {V02.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
