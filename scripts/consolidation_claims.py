#!/usr/bin/env python3
"""Do the consolidation documents still describe the running extractor?

    python scripts/consolidation_claims.py

Exit 0 = every checked claim still holds.
Exit 1 = a document says something the extractor no longer does.

Why this exists
---------------
The five Step 2 documents make claims about the implementation, and a document
cannot notice when the thing it describes changes underneath it. On
23 September three of them went stale within hours of being written:

    "§9.1 ... and it is NOT IMPLEMENTED"        implemented four hours later
    "meta is the one record this implementation  emitted the same afternoon
     still does not emit in rc2's shape"
    "one open implementation item ... no         five records now emitted
     records emitted"

Nothing was wrong with the documents when they were written. The defect is that
they had no way to stop being right, which is the same shape as a NOT verdict in
`rc2_conformance_map.py` that cannot notice the behaviour has landed. That file
solved it with anti-needles. This does the same for prose.

WHAT THIS CAN AND CANNOT CHECK
------------------------------
It checks CLAIMS ABOUT THE IMPLEMENTATION that are mechanically decidable:
a record type is emitted or it is not, a field is present or it is not, a
number matches or it does not.

It cannot check a disposition. Whether §11.2 should be REPLACE rather than KEEP
is a judgement about two specifications, and no script settles it. Those rows
are the documents' real content and they stay reviewed by people.

So this is a staleness guard, not a correctness one. It answers "has the ground
moved since this was written", never "was this right in the first place".
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SPECS = REPO / "specs" / "citation"
sys.path.insert(0, str(REPO / "scripts"))

import citation_extract as ce  # noqa: E402

CORPUS = REPO / "data" / "md_full"


def corpus_records() -> dict:
    """Every record type the corpus produces, and how many of each."""
    counts: dict[str, int] = {}
    for f in sorted(CORPUS.glob("*.md")):
        try:
            lines, _ = ce.run(f, set(ce.FIXES))
        except ce.Abort:
            continue
        for r in lines:
            counts[r["type"]] = counts.get(r["type"], 0) + 1
    return counts


def main() -> int:
    if not CORPUS.is_dir():
        print(f"corpus not found at {CORPUS}")
        return 2

    counts = corpus_records()
    meta_fields = []
    for f in sorted(CORPUS.glob("*.md")):
        try:
            lines, _ = ce.run(f, set(ce.FIXES))
        except ce.Abort:
            continue
        meta_fields = list(ce.canonical_order(lines[0]))
        break

    docs = {p.name: p.read_text(encoding="utf-8")
            for p in sorted(SPECS.glob("CONSOLIDATION-STEP2-*.md"))}
    if not docs:
        print("no Step 2 documents found")
        return 2

    # (phrase that must NOT appear anywhere in the Step 2 documents,
    #  why it would be stale, the evidence that settles it)
    #
    # Each phrase is a claim that WAS true and is not any more. A document is
    # free to say the claim was true once — "it WAS NOT IMPLEMENTED", "this
    # said eight" — so the phrases are the present-tense forms only.
    STALE = [
        ("and it is NOT IMPLEMENTED",
         "§9.1's duplicate_reference_key is implemented",
         f"{counts.get('duplicate_reference_key', 0)} records emitted"),
        ("no records emitted",
         "§9.1's duplicate_reference_key is implemented",
         f"{counts.get('duplicate_reference_key', 0)} records emitted"),
        ("meta is the one record this implementation still does not",
         "meta carries rc2 §1.1's rule identity",
         f"meta fields: {meta_fields[:5]}"),
        ("the one record this implementation still does not\nemit",
         "meta carries rc2 §1.1's rule identity",
         f"meta fields: {meta_fields[:5]}"),
    ]

    failures = []
    for phrase, why, evidence in STALE:
        for name, text in docs.items():
            if phrase in text:
                failures.append(f"{name}\n      says {phrase!r}\n"
                                f"      but {why} — {evidence}")

    # Positive claims: a number in a document that must still be the number.
    #
    # Written as (document, literal string, live value) so a drift shows the
    # document's figure beside the run's rather than just failing.
    FIGURES = [
        ("CONSOLIDATION-STEP2-IDENTITY-AND-RECONCILIATION.md",
         "duplicate_reference_key records emitted      0       5",
         counts.get("duplicate_reference_key", 0), 5),
        ("CONSOLIDATION-STEP2-SUMMARY-AND-OUTPUT.md",
         "CORPUS           2235       2104",
         counts.get("citation", 0), 2104),
    ]
    for name, literal, live, expected in FIGURES:
        text = docs.get(name, "")
        if literal not in text:
            failures.append(f"{name}\n      the figure block {literal!r} is "
                            f"gone, so this check no longer guards anything")
        elif live != expected:
            failures.append(f"{name}\n      states {expected}, the run "
                            f"produces {live}")

    print(f"{len(docs)} Step 2 document(s), "
          f"{len(STALE)} staleness phrase(s), {len(FIGURES)} figure(s)\n")
    if failures:
        print("claims that no longer hold:\n")
        for f in failures:
            print("  ", f)
        return 1
    for name in docs:
        print(f"  ok  {name}")
    print("\n  every mechanically checkable claim still describes the run.")
    print("  Dispositions are NOT checked here and never will be; whether a")
    print("  row is REPLACE rather than KEEP is a judgement about two")
    print("  specifications, and it stays reviewed by people.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
