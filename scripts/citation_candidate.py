#!/usr/bin/env python3
"""Turn citation extractor output into a candidate the §15 gold runner can score.

    python scripts/citation_candidate.py --output <extractor.jsonl> \
        --paper paper-1 --out /tmp/candidate-1.json

Exit 0 = candidate written.
Exit 1 = refused; nothing written.

Why this is a separate step
--------------------------
The gold set keys on `author_phrase` plus year. rc3 §A already requires the
extractor to emit exactly that: *`author_phrase` always records the complete
source candidate phrase before STOP reduction, and STOP reduction MUST never
alter it.* So the two meet without either bending toward the other, which is
the property that makes the comparison worth anything.

What it deliberately does not use is `citation_key`. That is the extractor's
resolved identity — `person|smith|2020`, `non_person|world bank|2016` — and
deriving a surname from a phrase is the grammar under test. Scoring against a
gold set built from the same derivation would agree by construction on exactly
the cases rc3 exists to fix.

Occurrences to works
--------------------
The extractor emits one record per occurrence. The gold set lists each cited
work once. This collapses occurrences to distinct works and reports how many
were collapsed, because the alternative — scoring occurrence output against a
work-level gold set — produces a precision figure that is mostly an artefact of
how often a paper repeats itself.

The collapse is stated in the output. Anyone reading the score can see how many
occurrences stood behind it, and a later occurrence-level gold set will not
have to guess what this run measured.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The terminal states rc3 §A gives a detected candidate. Only `parsed` is a
# claim that a citation was read; the other two are the extractor declining, and
# counting a declined candidate as an extraction would score a refusal as a
# success.
PARSED = "parsed"
STATES = (PARSED, "unresolved_citation", "excluded_candidate")


class Refused(Exception):
    pass


def flatten(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def records(path: Path):
    """One JSON object per line, or a single JSON array. Both are seen."""
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("["):
        try:
            for r in json.loads(text):
                yield r
            return
        except json.JSONDecodeError as e:
            raise Refused(f"{path.name} starts as a JSON array and does not "
                          f"parse: {e}")
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            raise Refused(f"{path.name} line {n} is not valid JSON: {e}\n"
                          f"  {line[:120]}")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="citation_candidate.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True,
                    help="the extractor's records, JSONL or a JSON array")
    ap.add_argument("--paper", required=True,
                    help="which gold set this is for, e.g. paper-1")
    ap.add_argument("--out", required=True)
    ap.add_argument("--source-sha256", default="",
                    help="papers.markdown hash the extractor ran against; "
                         "without it the runner cannot establish that "
                         "candidate and gold describe the same text")
    a = ap.parse_args()

    src = Path(a.output).resolve()
    if not src.is_file():
        raise Refused(f"extractor output not found: {src}")

    gold_p = REPO / "specs" / "gold" / f"citation-{a.paper}-v0.1.json"
    if not gold_p.is_file():
        raise Refused(f"no gold set for {a.paper!r}: {gold_p}")
    gold = json.loads(gold_p.read_text(encoding="utf-8"))

    seen: dict[tuple, int] = {}
    items: list[dict] = []
    counts = {s: 0 for s in STATES}
    unknown_state, no_phrase = 0, []

    for r in records(src):
        if r.get("type") not in (None, "citation"):
            continue
        state = r.get("candidate_state")
        if state is None:
            # Pre-rc3 output has no candidate_state. Treat a record carrying a
            # citation_key as parsed and say so, rather than silently assuming.
            state = PARSED if r.get("citation_key") or r.get("author_phrase") \
                else "unresolved_citation"
        if state in counts:
            counts[state] += 1
        else:
            unknown_state += 1
            continue
        if state != PARSED:
            continue

        phrase = r.get("author_phrase")
        if not phrase:
            # rc3 §A requires it on every citation record. A parsed citation
            # without one cannot be scored against this gold set, and guessing
            # from citation_key would reintroduce the derivation under test.
            no_phrase.append(r.get("citation_index", "?"))
            continue
        year = str(r.get("year") or "").strip()
        if not year:
            no_phrase.append(r.get("citation_index", "?"))
            continue

        k = (flatten(phrase), year)
        if k in seen:
            seen[k] += 1
            continue
        seen[k] = 1
        items.append({"author_phrase": flatten(phrase), "year": year,
                      "as_extracted": str(phrase)})

    if not items:
        raise Refused(
            "no parsed citation carried both an author_phrase and a year, so "
            "there is nothing to score.\n"
            f"  records by state: {counts}\n"
            "  rc3 §A requires author_phrase on every citation record. If this "
            "output predates that,\n  the extractor has to be re-run rather "
            "than the phrase reconstructed here.")

    occurrences = sum(seen.values())
    doc = {
        "candidate": f"citation-{a.paper}",
        "unit": "distinct cited work",
        "key_fields": gold["key_fields"],
        "produced_from": {
            "extractor_output": src.name,
            "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        },
        "collapsed": {
            "parsed_occurrences": occurrences,
            "distinct_works": len(items),
            "note": "the extractor emits one record per occurrence; the gold "
                    "set lists each work once. Scoring is at the work level "
                    "and this is the ratio behind it.",
        },
        "candidate_states": counts,
        "items": items,
    }
    if a.source_sha256:
        doc["source"] = {"sha256": a.source_sha256}
    if no_phrase:
        doc["parsed_without_author_phrase"] = no_phrase
    if unknown_state:
        doc["records_with_unrecognised_state"] = unknown_state

    dest = Path(a.out).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"wrote {dest}")
    print(f"  {occurrences} parsed occurrence(s) -> {len(items)} distinct work(s)")
    print(f"  states: {counts}")
    if no_phrase:
        print(f"  parsed with no author_phrase or year: {len(no_phrase)} "
              f"(not scored, rc3 §A requires them)")
    if not a.source_sha256:
        print("  no --source-sha256: the runner will say the score rests on an")
        print("  unverified assumption that candidate and gold describe the "
              "same text")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
