#!/usr/bin/env python3
"""Turn a citation extractor run into a candidate the gold runner can score.

    python scripts/citation_candidate.py --jsonl <run>/<paper>.jsonl \
        --out /tmp/candidate.json

Exit 0 = written. Exit 1 = refused.

Why this is a separate script
----------------------------
The extractor emits occurrences with a derived key (`sodhi|2019`). The gold set
is a list of distinct works identified by the author phrase a human read
(`sodhi and tang` + `2019`). Scoring one against the other needs a stated
conversion, and putting that conversion inside either side would let it quietly
decide the result.

Two things it does, both declared
---------------------------------
**Reads the phrase, not the key.** `citation_segment` holds the text as it
appeared; `citation_key` holds what the grammar made of it. Using the key would
compare the extractor's surname rule against a gold set that deliberately avoids
having one, so every multi-token surname would score as a miss for a reason that
has nothing to do with whether the citation was found. The phrase is split by
the same rule the gold set used: everything before the year is the author.

**Collapses occurrences to works.** The gold set lists each work once and the
extractor emits one record per mention. ad1e3ff9 has 180 citation records for
91 annotated works. Comparing those directly would report a precision of about
0.5 that measures nothing but repetition. The occurrence count is preserved on
each item so nothing is lost, and an occurrence-level score needs an
occurrence-level annotation, which does not exist.

What it does not do
-------------------
It does not repair. A record whose segment carries no year is reported as
unparseable rather than guessed at, and the count appears in the output so the
denominator is visible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

# The same rule both sides are split by. Imported rather than restated: a second
# copy is free to disagree, and the whole point is that gold and candidate are
# reduced to comparable form by one rule.
from build_citation_gold import YEAR, flatten  # noqa: E402


class Refused(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="citation_candidate.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    src = Path(a.jsonl).resolve()
    if not src.is_file():
        raise Refused(f"extractor output not found: {src}")

    works: dict[tuple, dict] = {}
    occurrences = 0
    unparseable: list[str] = []

    for line in src.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("type") != "citation":
            continue
        occurrences += 1
        seg = rec.get("citation_segment") or rec.get("citation_group") or ""
        m = YEAR.search(seg)
        if not m:
            unparseable.append(seg[:60])
            continue
        author = flatten(seg[:m.start()].rstrip(" ,;:").strip("("))
        year = m.group(1)
        k = (author, year)
        if k in works:
            works[k]["occurrences"] += 1
            continue
        works[k] = {
            "author_phrase": author,
            "year": year,
            "occurrences": 1,
            "citation_key_emitted": rec.get("citation_key"),
            "first_seen_in": rec.get("section_name"),
        }

    doc = {
        "candidate": a.label or src.stem,
        "unit": "distinct cited work",
        "from": {
            "path": str(src),
            "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        },
        "citation_records_read": occurrences,
        "distinct_works": len(works),
        "unparseable_segments": unparseable,
        "items": sorted(works.values(),
                        key=lambda x: (x["author_phrase"], x["year"])),
    }

    dest = Path(a.out).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"{dest}")
    print(f"  {occurrences} citation records -> {len(works)} distinct works"
          + (f"  ({occurrences / len(works):.1f} per work)" if works else ""))
    if unparseable:
        print(f"  {len(unparseable)} segment(s) with no year, not guessed at:")
        for s in unparseable[:5]:
            print(f"      {s!r}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
