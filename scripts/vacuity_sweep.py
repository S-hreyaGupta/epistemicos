#!/usr/bin/env python3
"""Which controls in the citation suite still pass when the extractor emits nothing?

    python scripts/vacuity_sweep.py

Exit 0 = the survivor set is exactly the pinned one.
Exit 1 = it is not, and the difference is named.
Exit 2 = could not run.

The question this asks
----------------------
`mutate_citation_suite.py` asks whether a control notices when the RULE it
names is broken. This asks the complementary question, which no mutation can
reach: does a control pass because the behaviour is right, or because its
fixture produced nothing for it to judge?

A control asserting an absence is satisfied by an empty document. "No mismatch
was emitted", "nothing was excluded", "this span produces no record" are all
true of a run that produced no records at all. Four such controls were found by
hand on 23 September, each after a different investigation, and each time by
accident. This finds them on purpose.

Where the question comes from
-----------------------------
BOOTSTRAP-001 cycle 04, reviewing the execution layer:

    each control tested the case its repair was designed for, and the case one
    step sideways went untested

and Alex Zamurko's ruling of 16 September on the fixture-validity audit:

    each negative control should first establish that its fixture satisfies all
    prerequisites except the single condition it intends to violate

That review was of the review machinery, not of this suite. The finding is
about how controls get written here, and this suite is written by the same
hand, so it applies. `CITATION-WORK-IS-OUTSIDE-THE-REVIEW-PROTOCOL.md` records
why the citation work never went through that protocol.

How it works
------------
Each of the three citation-side record emitters is disabled in turn, by
replacing the `append` that publishes the record with a discard. The suite is
then run and its `[ok]` lines collected. A control that still passes with an
emitter disabled is not testing anything that emitter produces.

Most survivors are legitimate: a heading-detection control does not care that
citations stopped being emitted, and a reference-side control does not either.
So the survivor set is PINNED rather than required to be empty, and the sweep
fails when it changes in either direction. A new vacuous control makes the set
grow; repairing one makes it shrink. Both have to be looked at, and shrinking
without updating the pin would otherwise pass silently, which is the defect
this file exists to find.

Why the pin is a set and not a count
------------------------------------
A count lets one control become vacuous while another is repaired. The names
are what the review needs anyway.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
EXTRACTOR = REPO / "scripts" / "citation_extract.py"
SUITE = REPO / "scripts" / "test_citation_extract.py"

# (label, the exact source text that publishes the record, its replacement)
#
# Each targets the `append` itself rather than the function around it, so the
# record is still built and simply not published. Disabling the function would
# change control flow and produce failures that have nothing to do with the
# question.
EMITTERS = [
    ("citation",
     '    cits.append({\n        "type": "citation", "index": 0,',
     '    _ = ({\n        "type": "citation", "index": 0,'),
    ("unresolved_citation",
     '    unres.append({\n        "type": "unresolved_citation", "index": 0,',
     '    _ = ({\n        "type": "unresolved_citation", "index": 0,'),
]

# Controls that legitimately survive with BOTH citation-side emitters off.
#
# Every one was read before it was listed. They fall into five groups, none of
# which consumes a citation record:
#
#   heading and section detection      the `References` line rules, h1/h2
#   the style guard                    §10, which runs on raw text pre-extraction
#   excluded_candidate                 a third emitter, not disabled here
#   aborts                             exit 2, 4, 5, which stop before extraction
#   summary schema                     fields that must be absent, not counts
#
# Two entries are here for a weaker reason and are marked. They assert an
# absence and are guarded by a neighbouring positive on the same fixture rather
# than by anything inside themselves, so they would survive a total extractor
# failure while their partner failed. That is sound as a pair and invisible as
# a line, which is why they are named here instead of being quietly allowed.
PINNED_SURVIVORS = {
    # heading and section boundary
    "a standalone `References` line is a section boundary",
    "a marked-up heading still takes priority over a stray line",
    "a stray second h1 alongside h2 structure is tolerated",
    "refused: a `References` line with nothing below it",
    "refused: a `References` line with prose below it, not entries",
    "refused: a `References` line with too few entries below it",
    "refused: entries below the label are not in order",
    # the style guard, pre-extraction
    "an APA document passes the style guard",
    "a stray comma-less citation among APA ones does not trip it",
    "comma_less_share counts both forms and reports the ratio",
    "too few parentheticals to judge a style: not refused",
    # excluded_candidate, a third emitter this sweep does not disable
    "A2: a reason outside the closed set is refused, incl. bare_locator",
    "A2: excluded_reason is rc3's closed six-member set",
    "A4: an excluded span is emitted, not silently dropped",
    "a mathpix cdn image URL is excluded_candidate/url_or_image",
    "§E: a candidate above the first h2 is publisher_metadata",
    "§E: a candidate under `## Citation information` is excluded",
    "B10/D2: a year-only math span is not math_expression",
    "B10: a math span that is not year-only is math_expression",
    # aborts, which stop before extraction runs
    "exit 2: a comma-less author-date document is refused",
    "exit 4: sectioning lives in h1: two h1, no h2",
    "exit 5: invalid utf-8",
    # summary schema: an assertion that a field is absent
    "A5: the summary reports a parse rate and no accuracy figure",
    # PAIRED ONLY. Guarded by a positive on the same fixture immediately
    # beside it, not by anything internal.
    "1499 is invisible, not unresolved",          # paired: "1500 is inside"
    "square brackets produce no record at all",   # paired: §10/C-080
    "a damaged group loses everything without the segments flag",  # paired:
                                                  # "with it, the good
                                                  # segments survive"
}


def ok_labels(text: str) -> list:
    return [m.group(1) for m in re.finditer(r"^\s*\[ok\] (.+)$", text, re.M)]


def duplicates(labels: list) -> list:
    seen, dup = set(), set()
    for x in labels:
        (dup if x in seen else seen).add(x)
    return sorted(dup)


def run_suite(source: str) -> set:
    """Run the suite against a temporary extractor built from `source`."""
    original = EXTRACTOR.read_text(encoding="utf-8")
    EXTRACTOR.write_text(source, encoding="utf-8")
    try:
        r = subprocess.run([sys.executable, str(SUITE)],
                           capture_output=True, text=True, timeout=600)
        return ok_labels(r.stdout)
    finally:
        # Restored in a finally so an interrupted sweep cannot leave a
        # disabled emitter in the working tree. A sweep that breaks the thing
        # it measures and does not put it back is worse than no sweep.
        EXTRACTOR.write_text(original, encoding="utf-8")


def main() -> int:
    if not EXTRACTOR.is_file() or not SUITE.is_file():
        print("  extractor or suite not found")
        return 2

    source = EXTRACTOR.read_text(encoding="utf-8")
    disabled = source
    for label, old, new in EMITTERS:
        if disabled.count(old) != 1:
            print(f"  the {label} emitter is not where this file expects it "
                  f"({disabled.count(old)} matches). The probe cannot run, "
                  f"which is reported rather than passed.")
            return 2
        disabled = disabled.replace(old, new, 1)

    print("  baseline: the suite as it stands")
    base_labels = run_suite(source)
    if not base_labels:
        print("  the suite produced no [ok] lines at all; nothing to compare")
        return 2
    print(f"    {len(base_labels)} controls pass\n")

    # Labels have to be unique, and this is where it gets noticed because this
    # is the only place that compares the count with the distinct count.
    #
    # `mutate_citation_suite.py` names the control each mutation must take red
    # and matches it as a substring of the failure text. Two controls sharing a
    # label make that match ambiguous: the mutation reports caught while the
    # control it names may never have run. No mutation names a duplicated label
    # today, which is luck rather than design, and three pairs were duplicated
    # until 23 September.
    dup = duplicates(base_labels)
    if dup:
        print("  two or more controls share a label:\n")
        for d in dup:
            print(f"    {d}")
        print("\n  A mutation naming one of these cannot say which control")
        print("  went red, so `caught` would stop meaning what it says.\n")
        return 1

    base = set(base_labels)
    print("  with the citation and unresolved_citation emitters disabled")
    survivors = set(run_suite(disabled))
    print(f"    {len(survivors)} of {len(base)} still pass\n")

    # A control that stops passing is not interesting here; that is the
    # expected outcome. Only the survivors are the question.
    survivors &= base
    new = sorted(survivors - PINNED_SURVIVORS)
    gone = sorted(PINNED_SURVIVORS - survivors)

    if new:
        print("  NOT PINNED, and passing with nothing emitted:\n")
        for n in new:
            print(f"    {n}")
        print("\n  Each of these is satisfied by a run that produced no")
        print("  records at all. Either add a live-fixture guard, or read it")
        print("  and pin it with the reason it does not need one.\n")

    if gone:
        print("  pinned and no longer surviving:\n")
        for g in gone:
            print(f"    {g}")
        print("\n  A control that used to pass with nothing emitted and now")
        print("  does not has been repaired or removed. Good either way, and")
        print("  the pin has to move deliberately rather than quietly.\n")

    if new or gone:
        return 1

    print(f"  the survivor set is exactly the pinned {len(PINNED_SURVIVORS)}.")
    print("  Every one was read before it was listed, and three of them are")
    print("  marked PAIRED ONLY: sound because of a positive beside them on")
    print("  the same fixture, and not because of anything inside themselves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
