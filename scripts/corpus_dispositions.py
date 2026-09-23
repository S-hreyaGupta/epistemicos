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

import pathlib
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
        "a bibliography line that attached to no entry. Three visibly "
        "different kinds are mixed in here: continuation lines of a real "
        "entry, journal boilerplate inside the bibliography span, and entries "
        "whose year is not parenthesised. Only the second is obviously "
        "non-blocking",
    ("unresolved_reference", "entry_start_grammar"):
        "an entry-shaped line rc2 §7.1's guard refused",
    ("unresolved_reference", "no_year"):
        "rc2 §7.3 says emit this and no reference row. Expected by the rule, "
        "but no document says so over this corpus",
    ("unresolved_citation", "no_grammar_match"):
        "the largest citation-side class. C-010 and C-011 make it the correct "
        "outcome rather than a silent drop; whether 121 of them is an "
        "accepted limitation is the open question",
    ("unresolved_citation", "stopword_surname"):
        "rc2 §6.3's named outcome",
    ("unresolved_citation", "all_caps_surname"):
        "rc2 §6.2's named outcome, and C-014 pins it",
    ("uncited_reference", None):
        "UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md identifies 28 of these as "
        "naming a reference the paper DOES cite, in a span the grammar could "
        "not read. A false reconciliation diagnostic is B3 on its face. The "
        "document states the number and stops short of classifying it",
    ("missing_reference", None):
        "candidate-level, so it establishes no identity. Whether the "
        "occurrences behind it are real gaps is unexamined",
    ("possible_mismatch", "surname_edit_distance_1"):
        "rc2 §9.4's first repair rule",
    ("possible_mismatch", "year_adjacent"):
        "rc2 §9.4's second repair rule",
    ("duplicate_reference_key", None):
        "rc2 §9.1's record. Implemented 23 September, never dispositioned",
    ("ambiguous_citation", None):
        "rc2 §8.3 rows 3 and 5. 15 of the 17 come from the three papers "
        "outside C-081's eleven",
    # Two groups, not one. `author_structure_mismatch` carries a `failed`
    # field and rc2 §9.3 gives it two exact checks, so a single disposition
    # over the type would be covering two different findings with one
    # sentence. The guard below caught this on the first run, which is what
    # it is for.
    ("author_structure_mismatch", "count"):
        "rc2 §9.3's count check, pinned by C-062. "
        "RC1-IS-BIGGER-THAN-THE-SPLIT names author-structure agreement as "
        "the amendment with a live defect behind it",
    ("author_structure_mismatch", "order"):
        "rc2 §9.3's order check, pinned by C-063. Same open question as the "
        "count half",
}


def main() -> int:
    if not CORPUS.is_dir():
        print(f"  corpus not found at {CORPUS}")
        return 2

    groups: Counter = Counter()
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
    print("\n  where the orphan lines are, and why this is not yet a cause")
    for src in sorted(orphan_by_source):
        r, o = orphan_by_source[src]
        if r + o:
            print(f"    {src:10s} {r:4d} references {o:4d} orphan   "
                  f"{o / (r + o):5.1%} of lines orphaned")
    print("    The papers needing §4.3's inferred fallback are the same "
          "papers whose")
    print("    conversion lost the heading, so the fallback's cost and the "
          "papers'")
    print("    condition are confounded. Both readings fit; neither is "
          "established here.")

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
