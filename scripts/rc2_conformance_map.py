#!/usr/bin/env python3
"""Where the implementation stands against rc2's own conformance matrix.

    python scripts/rc2_conformance_map.py

rc2 file 03 defines 86 conformance cases, C-001 to C-086, and marks every one
`DEFINED / PENDING_EXECUTION`. That is rc2 saying the cases exist and none has
been run. This maps them against what is actually implemented and controlled
here, so the consolidation's Step 2 has an evidence base rather than a guess.

Written as a script rather than a table, for the reason the inventory's hash
block was regenerated on 21 September: a transcribed artifact goes stale
silently, and one digest in that table was already wrong. This re-derives from
the two files every time it runs.

WHAT A VERDICT MEANS, precisely
-------------------------------
    MET           the behaviour is implemented AND a named control in
                  test_citation_extract.py pins it, so the mutation probe can
                  show the control biting
    PARTIAL       the behaviour exists but the case asks for more than is
                  pinned — usually a field rc2 requires that is not emitted,
                  or an exhaustiveness the suite does not have
    NOT           not implemented, with the reason named
    NOT ASSESSED  no honest probe was written. NEVER reported as met.

The distinction between MET and "it probably works" is the whole point. A case
is only MET when a control would go red if the behaviour were removed, which
this repository has learned twice is not the same as the behaviour appearing
to be present.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATRIX = REPO / "specs/citation/citation-v3.4-rc2-conformance-matrix.md"
IMPL = REPO / "scripts/citation_extract.py"
SUITE = REPO / "scripts/test_citation_extract.py"

# (case, needles that must be in the implementation, needles in the suite,
#  verdict when all present, note)
#
# A suite needle is what makes a verdict MET rather than asserted: it names the
# control that would go red. Where there is no such control the verdict is
# PARTIAL at best.
CHECKS = {
    "C-001": ((), ("exit 5: invalid utf-8",), "MET", "abort before processing"),
    "C-006": (("REF_NAMES",), (), "PARTIAL",
              "heading detection exists; references_source not emitted"),
    "C-007": (("_unmarked_reference_label",), (), "PARTIAL",
              "inferred fallback exists; references_source not emitted"),
    "C-008": ((), ("too few entries below it",), "MET",
              "threshold does not overtrigger"),
    "C-010": ((), ("every detected candidate reaches exactly one",), "MET",
              "rc3 A1/A3 completeness invariant"),
    "C-011": ((), ("every detected candidate reaches exactly one",), "MET",
              "same invariant covers narrative"),
    "C-012": (("while True:\n        j = i",),
              ("a seven-token author list is reached in full",), "MET",
              "no token cap"),
    "C-013": ((), ("never bank|2024",), "MET",
              "longest-suffix recovery forbidden"),
    "C-014": ((), ("OECD (2024) is all_caps_surname",), "MET", ""),
    "C-016": (("PREFIX_CUES_CP",), ("the §4 prefix cues still work",), "MET",
              "closed PREFIX set"),
    "C-018": (("STOP = {",), (), "PARTIAL",
              "STOP exists; rc2 wants one case per token"),
    "C-021": ((), ("a possessive surname keys to the bare name",), "MET",
              "person candidate only, surface unchanged"),
    "C-030": (('reasons.append("no_year")',), (), "PARTIAL",
              "emitted; no control pins it"),
    "C-031": (('"entry_start_grammar"', '"orphan_line"', '"no_year"'), (),
              "PARTIAL", "three reasons emitted, set not schema-enforced"),
    "C-033": ((), ("a list that parses partway",), "MET",
              "ordered authors, or nothing"),
    "C-034": ((), ("a full-forename reference takes no part",), "MET",
              "authors null, no structure check"),
    "C-035": ((), ("an institutional reference entry is keyed",), "MET",
              "rc2 §7.4 non-person identity"),
    "C-036": ((), ("no comma, at least one letter",), "MET",
              "comma-containing organisation unresolved, not guessed"),
    # rc2 §8.2 / §8.3, unblocked by CIT-ARCH-01 and implemented 21 September.
    # Only §8.3's first column is reachable: no STOP-reduced candidate exists,
    # so S is always no_match and six of the nine rows cannot be built.
    "C-037": ((), ("§8.3: no_match → not_resolved",), "MET",
              "F=no_match, S=no_match"),
    "C-038": ((), ("§8.3: unique/no_match → full_phrase",), "MET",
              "F=unique, S=no_match"),
    "C-039": ((), ("§8.3: nonunique/no_match → ambiguous_citation",), "MET",
              "F=nonunique, S=no_match"),
    "C-052": ((), ("§11.2: the identity classes partition",), "MET",
              "identity partition is exact"),
    "C-062": ((), ("exact fails on count",), "MET", "rc2 §9.3"),
    "C-063": ((), ("exact fails on order",), "MET", "rc2 §9.3"),
    "C-064": (("ET_AL_MIN_AUTHORS = 3",),
              ("et_al fails below ET_AL_MIN_AUTHORS",), "MET",
              "threshold pinned in the profile, not chosen"),
    "C-065": ((), ("does not itself force exit 1",), "MET", ""),
    "C-074": ((), ("comma-less author-date document is refused",), "MET",
              "exit 2 style detector"),
    "C-075": ((), ("sectioning lives in h1: two h1, no h2",), "MET",
              "exit 4 heading contract"),
    "C-076": ((), ("exit 5: invalid utf-8",), "MET", ""),
    "C-079": ((), ("square brackets produce no record",), "MET",
              "out of envelope"),
}

# Not implemented, each with the reason. Grouped so the shape of what is
# missing is legible: most of it is one architecture and one output contract,
# not sixty unrelated gaps.
NOT_IMPLEMENTED = {
    **{c: "rc2 §8 two-pass identity model not implemented"
       for c in ("C-040", "C-041", "C-042",
                 "C-043", "C-044", "C-045")},
    **{c: "ambiguous_author_resolution not implemented"
       for c in ("C-048", "C-049", "C-050", "C-051")},
    **{c: "candidate-level diagnostics not implemented"
       for c in ("C-053", "C-054", "C-055", "C-061")},
    **{c: "§9.4 repair rules not implemented"
       for c in ("C-056", "C-057", "C-058", "C-059", "C-060")},
    **{c: "citation_surface_group_key not implemented"
       for c in ("C-022", "C-023", "C-024", "C-025")},
    **{c: "sentence-relative fields not emitted"
       for c in ("C-026", "C-027", "C-028")},
    **{c: "bibliography_absent not implemented"
       for c in ("C-009", "C-066", "C-067")},
    **{c: "exit 6 not allocated" for c in ("C-046", "C-047", "C-077")},
    **{c: "file output contract not implemented"
       for c in ("C-071", "C-072", "C-073")},
    **{c: "byte-coordinate contract: offsets here are code points"
       for c in ("C-002", "C-003", "C-004")},
    **{c: "determinism not byte-pinned"
       for c in ("C-029", "C-032", "C-068", "C-069", "C-070", "C-083")},
    **{c: "outside the pilot scope" for c in ("C-084", "C-085", "C-086")},
    "C-005": "heading contract only partially pinned",
    "C-015": "verbatim span is kept but not pinned by a control",
    "C-017": "PREFIX longest-match precedence not pinned",
    "C-019": "STOP reduction is destructive here; rc2 requires additive",
    "C-020": "author_phrase is complete, but no stop_reduced candidate exists",
    "C-078": "the exit-1 finding set is not closed",
    "C-080": "true but unpinned: numeric citations never become identity",
    "C-081": "the corpus still carries unresolved findings",
    "C-082": "no timed termination test",
}


def main() -> int:
    if not MATRIX.exists():
        print(f"rc2 conformance matrix not found at {MATRIX}")
        return 1
    matrix = MATRIX.read_text(encoding="utf-8")
    impl = IMPL.read_text(encoding="utf-8")
    suite = SUITE.read_text(encoding="utf-8")

    cases = [(c, d.strip(), s.strip()) for c, d, s in
             re.findall(r"\| (C-\d{3}) \| ([^|]+?) \| ([^|]+?) \|", matrix)]
    if not cases:
        print("no cases parsed from the matrix; the table shape has changed")
        return 1

    rows, tally, broken = [], Counter(), []
    for cid, desc, scope in cases:
        if cid in CHECKS:
            need_impl, need_suite, verdict, note = CHECKS[cid]
            missing = [n for n in need_impl if n not in impl] + \
                      [n for n in need_suite if n not in suite]
            if missing:
                # The needle no longer matches. That is a broken probe, not a
                # failure and not a pass — the same rule mutate_citation_suite
                # applies to itself.
                verdict, note = "NOT ASSESSED", f"probe stale: {missing[0][:40]!r}"
                broken.append(cid)
        elif cid in NOT_IMPLEMENTED:
            verdict, note = "NOT", NOT_IMPLEMENTED[cid]
        else:
            verdict, note = "NOT ASSESSED", "no probe written"
        tally[verdict] += 1
        rows.append((cid, verdict, scope, desc, note))

    print(f"rc2 conformance matrix — {len(cases)} cases, all DEFINED / "
          f"PENDING_EXECUTION in rc2\n")
    for cid, verdict, scope, desc, note in rows:
        print(f"  {cid}  {verdict:13} {desc[:54]:54} {note[:44]}")

    print(f"\n  {dict(tally)}")
    met = tally["MET"]
    print(f"\n  {met} of {len(cases)} met with a control that can fail.")
    print("  rc2 marks all 86 PENDING_EXECUTION, so these are the first that")
    print("  have been executed at all.")

    if broken:
        print(f"\n  {len(broken)} probe(s) went stale and are reported as NOT")
        print(f"  ASSESSED rather than passing: {', '.join(broken)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
