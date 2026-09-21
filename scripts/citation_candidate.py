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

    works: dict[str, dict] = {}
    items: list[dict] = []
    counts = {s: 0 for s in STATES}
    unknown_state, no_phrase = 0, []

    # The three record types rc3 A1 gives a detected candidate, plus None for
    # the bare-record form. Filtering to `citation` alone — which is what this
    # did until A1 was implemented — meant the state counts below could only
    # ever report parsed, and the other two printed 0 on every run whatever the
    # extractor found. A count that cannot come back non-zero is not a
    # measurement, and this one was printed next to real ones.
    CANDIDATE_TYPES = (None, "citation", "unresolved_citation",
                       "excluded_candidate")

    for r in records(src):
        if r.get("type") not in CANDIDATE_TYPES:
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

        # Collapse to the WORK, not to the phrasing.
        #
        # This keyed on (author_phrase, year) until 19 September, while the
        # document it writes declared `"unit": "distinct cited work"` and a
        # field called `"distinct_works"`. It was counting distinct phrasings.
        # A manuscript writing `(Duru et al., 2015)` in one paragraph and
        # `Duru, Therond, and Fares (2015)` in another contributed two, one of
        # which matched the annotation and one of which scored as a false
        # positive — so the extractor was penalised for the manuscript varying
        # its own wording. Ten works in gold paper 2 are cited under more than
        # one phrase, `macfadyen` under three: eleven surplus entries, and
        # every one of that paper's extras.
        #
        # Alex Zamurko, 18 September: *If citation_candidate.py collapses by
        # author_phrase, it is not measuring distinct works correctly.*
        #
        # The identity used for grouping is the extractor's `citation_key`.
        # That is a considered reversal, and the reason for the original
        # decision still stands for *matching* — deriving a surname from a
        # phrase is the grammar under test — so matching stays on
        # author_phrase and every phrase observed for a work is carried in
        # `author_phrase_variants`. A gold item matches if it matches any of
        # them. Grouping a run's own occurrences by the extractor's own notion
        # of identity compares nothing; scoring still does not use it.
        key = r.get("citation_key") or f"?phrase:{flatten(phrase)}|{year}"
        if key in works:
            works[key]["variants"].add(flatten(phrase))
            works[key]["n"] += 1
            continue
        works[key] = {"variants": {flatten(phrase)}, "n": 1,
                      "year": year, "as_extracted": str(phrase)}

    # One item per work. `author_phrase` carries the longest variant seen,
    # which is the most complete form the manuscript used; the rest travel
    # alongside so a gold set keyed on any of them still matches.
    for key, w in works.items():
        # A possessive is not part of a name. rc3 §A keeps `Bartko's` in
        # author_phrase because that is what the manuscript wrote, and an
        # annotation records the work as `bartko`, so the comparable form has
        # to be offered here rather than by altering the record. Normalising
        # for comparison, not editing what was extracted.
        for v in list(w["variants"]):
            bare = re.sub(r"['’]s\b", "", v).strip()
            if bare and bare != v:
                w["variants"].add(bare)
        variants = sorted(w["variants"], key=lambda s: (-len(s), s))
        items.append({
            "author_phrase": variants[0],
            "year": w["year"],
            "as_extracted": w["as_extracted"],
            "author_phrase_variants": variants,
            "occurrences": w["n"],
        })

    if not items:
        raise Refused(
            "no parsed citation carried both an author_phrase and a year, so "
            "there is nothing to score.\n"
            f"  records by state: {counts}\n"
            "  rc3 §A requires author_phrase on every citation record. If this "
            "output predates that,\n  the extractor has to be re-run rather "
            "than the phrase reconstructed here.")

    occurrences = sum(w["n"] for w in works.values())
    multi = sum(1 for w in works.values() if len(w["variants"]) > 1)
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
            "works_cited_under_more_than_one_phrase": multi,
            "grouped_by": "citation_key",
            "matched_on": "author_phrase, any variant",
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
