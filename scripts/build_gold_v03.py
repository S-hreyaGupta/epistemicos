#!/usr/bin/env python3
"""Build gold paper 1 v0.3 from v0.2 plus the three table-only works.

    python scripts/build_gold_v03.py            # check only, writes nothing
    python scripts/build_gold_v03.py --write

Exit 0 = the set was built (or would be). Exit 1 = refused.

The ruling
----------
Alex Zamurko, 18 September 2026, on the three works appearing only inside
Table 1, "Summary of empirical studies on supply chain structure", whose first
column is headed `Author-Year`:

    Count the three table-only works as citations. A table titled "Summary of
    empirical studies" with an Author-Year column is part of the manuscript's
    scholarly content, and Basole 2017, Dong 2015 and Park 2018 are explicitly
    identified there and all appear in the reference list. Unless the
    annotation protocol explicitly excluded tables, excluding them would
    create an undocumented prose-only rule.

And prospectively:

    Citations appearing in manuscript tables count when the table identifies
    scholarly works by author/year or equivalent citation information, unless
    the annotation protocol explicitly excludes that table type.

That rule is recorded in the output under `provenance.table_scope_rule` so it
travels with the data rather than living only in Slack.

What is *not* changed
---------------------
The three possessive cases — bartko 1976, fine 1998, mcgraw and wong 1996 —
stay exactly as v0.1 recorded them. Per the same ruling they are extractor
grammar errors rather than annotation errors, so the gold set is already right
and EC-2 is the extractor's to fix.

How the resulting score must be labelled
----------------------------------------
Not independent holdout performance. The five prose omissions in v0.2 and the
three table works here were both found through extractor-led adjudication, so
any figure computed against v0.3 is *post-adjudication performance on an
amended gold set*. `ADJUDICATION-paper-1.md` records exactly what changed and
why. The output carries the same statement in `provenance.additions`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
V02 = REPO / "specs" / "gold" / "citation-paper-1-v0.2.json"
V03 = REPO / "specs" / "gold" / "citation-paper-1-v0.3.json"
SOURCE = REPO / "data" / "md_full"

TABLE_NAME = "Summary of empirical studies on supply chain structure"

# author_phrase, year, the table row as it stands, first-author surname.
ADDITIONS = [
    ("basole et al.", "2017", "| Basole et al. (2017) |", "Basole"),
    ("dong et al.", "2015", "| Dong et al. (2015) |", "Dong"),
    ("park et al.", "2018", "| Park et al. (2018) |", "Park"),
]


def refuse(msg: str) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write the file; without it, verify and report only")
    a = ap.parse_args()

    gold = json.loads(V02.read_text(encoding="utf-8"))
    items = gold["items"]

    paper = gold["corpus_paper"]
    src = next(SOURCE.glob(paper + "*.md"), None)
    if src is None:
        refuse(f"no source for {paper} in {SOURCE}")

    got = hashlib.sha256(src.read_bytes()).hexdigest()
    want = gold["source"]["sha256"]
    if got != want:
        refuse(f"source bytes differ from the ones v0.2 records\n"
               f"  file   {got}\n  v0.2   {want}")
    print(f"source matches v0.2's recorded sha256 ({want[:16]}…)")

    sys.path.insert(0, str(REPO / "scripts"))
    import citation_extract as ce  # noqa: E402
    body, refs, _, _ = ce.split_body_and_references(ce.normalise(src.read_bytes()))
    body = body.replace("\\&", "&")
    entries = [" ".join(l.split()) for l in refs.splitlines() if l.strip()]

    # The ruling is conditional on the table identifying works by author-year.
    # Check that rather than assume it, since it is the rule's own predicate.
    if "Author-Year" not in body:
        refuse("no Author-Year column found; the ruling's condition is that "
               "the table identifies works by author/year, and this does not")
    print("table identifies works by Author-Year: the ruling's condition holds")

    existing = {(i["author_phrase"], i["year"]) for i in items}
    added = []
    print()
    for phrase, year, row_marker, surname in ADDITIONS:
        if (phrase, year) in existing:
            refuse(f"{phrase} {year} is already in v0.2; this would duplicate it")

        row = next((l for l in body.splitlines()
                    if l.lstrip().startswith("|") and row_marker in l), None)
        if row is None:
            refuse(f"{row_marker!r} is not a table row in {paper}")

        # and it must appear ONLY in a table — if it is also cited in prose it
        # belongs in the v0.2 group, not this one.
        prose = [l for l in body.splitlines()
                 if f"{surname} et al." in l and not l.lstrip().startswith("|")]
        if prose:
            refuse(f"{surname} {year} is also cited in prose; it is not a "
                   f"table-only work and this rule does not cover it")

        entry = next((e for e in entries
                      if re.match(rf"^{re.escape(surname)}\s*,", e) and year in e), None)
        if entry is None:
            refuse(f"no reference entry for {surname} {year}")

        print(f"  {phrase} {year}")
        print(f"      table row  {row.strip()[:78]}")
        print(f"      reference  {entry[:78]}")
        added.append({
            "author_phrase": phrase,
            "year": year,
            "as_annotated": row.strip(),
            "added_in": "v0.3",
            "found_by": "candidate_adjudication",
            "source_location": "table",
            "table": TABLE_NAME,
            "found_by_note": (
                "table-only: identified in the Author-Year column of a table "
                "of empirical studies, not cited in prose, present in the "
                "reference list. Admitted under the table-scope rule recorded "
                "in provenance. Found by reading the candidate's output; the "
                "verification against the reference list is independent of the "
                "extractor, the discovery is not."),
            "reference_entry": entry,
            "adjudicated_in": "specs/gold/ADJUDICATION-paper-1.md",
            "ruling": "Alex Zamurko, 2026-09-18",
        })

    out = dict(gold)
    out["gold_set"] = "citation-paper-1-v0.3"
    out["items"] = items + added
    out["provenance"] = dict(gold["provenance"])
    out["provenance"]["table_scope_rule"] = {
        "ruled": "2026-09-18",
        "by": "Alex Zamurko",
        "rule": ("Citations appearing in manuscript tables count when the "
                 "table identifies scholarly works by author/year or "
                 "equivalent citation information, unless the annotation "
                 "protocol explicitly excludes that table type."),
        "prospective": True,
        "why": ("excluding them would create an undocumented prose-only rule; "
                "a table of empirical studies with an Author-Year column is "
                "part of the manuscript's scholarly content"),
    }
    additions = dict(out["provenance"].get("additions", {}))
    additions["v0.3"] = {
        "added": "2026-09-18",
        "count": len(added),
        "method": ("works appearing only in a table with an Author-Year "
                   "column, each checked for the table row, for absence from "
                   "prose, and for a matching reference entry"),
        "independent_of_extractor_output": False,
        "why_not": ("found by reading the candidate's output, as with v0.2. "
                    "The verification is independent; the discovery is not."),
        "score_label": ("post-adjudication performance on an amended gold "
                        "set. Not independent holdout performance, and must "
                        "not be presented as such."),
        "unchanged": {
            "possessives": ["bartko 1976", "fine 1998", "mcgraw and wong 1996"],
            "why": ("extractor grammar errors rather than annotation errors, "
                    "so the gold set is already correct and EC-2 is the "
                    "extractor's to fix"),
        },
    }
    out["provenance"]["additions"] = additions

    print(f"\nv0.2 {len(items)} items -> v0.3 {len(out['items'])} items "
          f"({len(added)} added under the table-scope rule)")
    print("  possessives left unchanged: they are extractor errors, not "
          "annotation errors")

    if not a.write:
        print("\ncheck only; pass --write to create the file")
        return 0

    V03.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"wrote {V03.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
