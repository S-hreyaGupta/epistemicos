#!/usr/bin/env python3
"""Which controls in the citation suite still pass when the extractor emits nothing?

    python scripts/vacuity_sweep.py
    python scripts/vacuity_sweep.py --census

Exit 0 = no surviving control reads citation-side output.
Exit 1 = one does, and it is named along with the line that read.
Exit 2 = could not run.

Two questions, not one
----------------------
The default run asks whether a CONTROL is asleep: does it pass because the
behaviour is right, or because its fixture produced nothing to judge?

`--census` asks the complement, about the extractor rather than the suite:
is each RECORD TYPE watched by anything at all? It disables one emitter at a
time and counts the controls that go red. Zero would mean nothing in the
suite notices that record vanishing. Thirteen suite runs, so it is a
deliberate check rather than part of the default path.

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
All three citation-side record emitters — `citation`, `unresolved_citation`
and `excluded_candidate` — are disabled TOGETHER, by replacing the `append`
that publishes each record with a discard. The suite is then run and its
`[ok]` lines collected. A control that still passes with all three disabled is
not testing anything the extractor emits.

Together rather than one at a time, because the question worth asking is the
strongest one: does this control read any citation-side output at all? Which
emitter a given control depends on is recorded in the pin below instead.

That question is now measured rather than reasoned about. The disabled build
returns read-logging lists, so each survivor is reported as one of two kinds:

    read nothing the three emitters produce
        testing a constant, the reference side, the output bytes or an abort.
        Sound, and the reason belongs to its section rather than to it.

    read the empty output and passed anyway
        asked the citation side a question, got nothing back, and reported
        success. This is the defect, and the marker names the line that read.

The split matters because the first kind is the large majority and the second
is the finding. Reading 109 labels by hand to separate them is work nobody
completes; the interpreter already knows the answer.

What this file got wrong about itself
-------------------------------------
The first version said "each of the three citation-side record emitters is
disabled in turn" while disabling two, together. Wrong twice in five words, in
the file whose entire purpose is catching claims that overstate what was
checked. Corrected on 23 September to say two and together, which then made
the gap obvious: six survivors were pinned only because `excluded_candidate`
kept running, so they were untested rather than cleared.

The third emitter was added on 24 September. Five of those six stopped
surviving, which is the answer. The sixth, `B10/D2: a year-only math span is
not math_expression`, was a real vacuous control: it asserted that a span was
not excluded, and a span that was never a candidate is not excluded either.
It now has to show the span present before the absence means anything.

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

import os
import pathlib
import re
import subprocess
import sys

# `→` in this file's output, and cp1252 cannot encode it, so a Windows console
# kills the run mid-print. See `test_citation_extract.py` for what that cost on
# 25 September — this file was the one that turned the crash into a finding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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
    # Added 24 September, which is what the docstring correction below asked
    # for. Six survivors were pinned only because this emitter kept running,
    # so they were untested rather than cleared. They are measured now.
    ("excluded_candidate",
     '    excl.append(rec)',
     '    _ = (rec)'),
]

# A fourth patch, applied only to the disabled build, answering the question
# the docstring above states and the survivor list by itself cannot: does this
# control READ any citation-side output at all?
#
# Grouping the survivors by the suite's own headings showed every one of the
# twenty-three groups is all-or-nothing. Not one section has some controls
# surviving and some going red. That is what a suite organised by subject looks
# like, and it means the survivors are twenty-three group judgements rather
# than 109 separate ones. What it does not do is separate the two kinds of
# survivor, and only one kind is a finding:
#
#     a control that never touches `cits`, `unres` or `excl` survives because
#     it is testing something else — a constant, the reference side, the
#     output bytes, an abort — and is sound
#
#     a control that DOES touch them and still passes with all three empty is
#     asserting over nothing, which is exactly what this file exists to find
#
# The compound-surname control was the second kind, and it was found by hand
# after a separate investigation. This finds that shape on purpose.
#
# So the disabled build returns read-logging lists and prints a marker at each
# read made from OUTSIDE the extractor. The module check is the whole trick:
# `run()` consumes all three lists itself while building the summary, so a flag
# set by any read at all would fire for every end-to-end control regardless of
# what that control actually asserts.
#
# Cost is nil: with the emitters disabled all three lists are empty, so every
# read is one call over zero elements.
READ_PROBE = '''\
class _VacSeen(list):
    """A list that reports reads made from outside this module.

    Injected by `vacuity_sweep.py` into the disabled build only. Never part of
    the extractor as committed.
    """

    def _touch(self):
        # By FILE, not by module name. Several controls run this file as a
        # script and compare its stdout byte for byte; in that subprocess the
        # module is `__main__`, a name check would not exclude it, and a
        # marker would land inside the artifact being compared. The file is
        # the same either way.
        #
        # And the frame reported is the caller's `main`, not the innermost
        # one. `keys(cits)` is a two-line helper at the top of the suite, so
        # the innermost frame says line 78 for every control that calls it,
        # which names the helper instead of the control. Walking out to `main`
        # gives the line in the suite body that is executing, which is the
        # control itself.
        me = os.path.basename(__file__)
        f = sys._getframe(2)
        # The IMMEDIATE caller decides whether this read counts. Walking past
        # extractor frames to find `main` instead made every internal read
        # `run()` performs look like a suite read, and the marker then landed
        # in stdout that a control was about to parse as JSON.
        if os.path.basename(f.f_code.co_filename) == me:
            return
        best = f
        while f is not None:
            if (f.f_code.co_name == "main"
                    and os.path.basename(f.f_code.co_filename) != me):
                best = f
                break
            f = f.f_back
        # Straight to fd 2, not to `sys.stdout` or even `sys.stderr`. Controls
        # capture stdout to compare it byte for byte or to json.loads it, and
        # a diagnostic that corrupts the artifact under test is worse than no
        # diagnostic. Attribution is by source line, so nothing here needs to
        # interleave with the suite's own output.
        os.write(2, f"[vacr] {os.path.basename(best.f_code.co_filename)}:"
                    f"{best.f_lineno}\\n".encode())

    def __iter__(self):
        self._touch()
        return list.__iter__(self)

    def __len__(self):
        self._touch()
        return list.__len__(self)

    def __getitem__(self, i):
        self._touch()
        return list.__getitem__(self, i)

    def __contains__(self, x):
        self._touch()
        return list.__contains__(self, x)

    def __bool__(self):
        self._touch()
        return list.__len__(self) != 0

    def __eq__(self, other):
        self._touch()
        return list.__eq__(self, other)

    __hash__ = None


'''

_EC_DEF = "def extract_citations(body: str, sents, heads, fixes: set[str],"

# (label, exact source text, replacement). Applied after the emitter patches
# and only to the disabled build.
READ_PATCHES = [
    ("the read probe", _EC_DEF, READ_PROBE + _EC_DEF),
    ("the instrumented return",
     "    return cits, unres, excl, errs",
     "    return _VacSeen(cits), _VacSeen(unres), _VacSeen(excl), errs"),
]

# The other nine record types the extractor emits, for `--census` only.
#
# These are NOT part of the survivor sweep above, and the reason is worth
# stating because the obvious extension does not work. The sweep's signal
# comes from nearly every control in the suite passing through citation
# extraction, so a survivor is unusual and therefore interesting. Disable
# `possible_mismatch` instead and 309 of 317 controls survive, because almost
# none of them was ever about possible_mismatch. Pinning 309 names would be
# noise wearing the shape of a result.
#
# So the narrow emitters get the complementary question instead, which needs
# no pin: does ANY control go red when this record stops being emitted? Zero
# would mean nothing in the suite watches that record type at all.
NARROW_EMITTERS = [
    ("reference",
     '        refs.append({\n            "type": "reference", "index": 0,',
     '        _ = ({\n            "type": "reference", "index": 0,'),
    # THREE sites, not one. This entry named a record type and disabled a
    # third of it until 25 September: the pattern below requires the type to
    # sit on the line after `unres.append({`, which is true only where
    # `no_year` is built. `entry_start_grammar` and `orphan_line` are written
    # on one line and went on emitting throughout. The census row read
    # `unresolved_reference  2  thin` and meant `no_year  2`.
    #
    # The uniqueness guard could not catch it. The pattern really does match
    # exactly once, so `count(old) == 1` confirms a site was found and says
    # nothing about whether it is the only one. That is why the completeness
    # check in `census` counts emission sites in the source instead.
    ("unresolved_reference",
     ('            unres.append({\n                "type": "unresolved_reference", "index": 0,',
      '            unres.append({"type": "unresolved_reference", "index": 0,\n'
      '                          "text": stripped, "start": span[0], "end": span[1],\n'
      '                          "reason": "entry_start_grammar"})',
      '            unres.append({"type": "unresolved_reference", "index": 0,\n'
      '                          "text": stripped, "start": span[0], "end": span[1],\n'
      '                          "reason": "orphan_line"})'),
     ('            _ = ({\n                "type": "unresolved_reference", "index": 0,',
      '            _ = ({"type": "unresolved_reference", "index": 0,\n'
      '                          "text": stripped, "start": span[0], "end": span[1],\n'
      '                          "reason": "entry_start_grammar"})',
      '            _ = ({"type": "unresolved_reference", "index": 0,\n'
      '                          "text": stripped, "start": span[0], "end": span[1],\n'
      '                          "reason": "orphan_line"})')),
    ("author_structure_mismatch",
     '        mismatches.append({\n            "type": "author_structure_mismatch", "index": 0,',
     '        _ = ({\n            "type": "author_structure_mismatch", "index": 0,'),
    ("possible_mismatch",
     '            diagnostics.append({\n                "type": "possible_mismatch", "index": 0,',
     '            _ = ({\n                "type": "possible_mismatch", "index": 0,'),
    ("missing_reference",
     '            diagnostics.append({\n                "type": "missing_reference", "index": 0,',
     '            _ = ({\n                "type": "missing_reference", "index": 0,'),
    ("ambiguous_citation",
     '            ambiguous_citations.append({\n                "type": "ambiguous_citation", "index": 0,',
     '            _ = ({\n                "type": "ambiguous_citation", "index": 0,'),
    ("ambiguous_author_resolution",
     '            ambiguous_authors.append({\n                "type": "ambiguous_author_resolution", "index": 0,',
     '            _ = ({\n                "type": "ambiguous_author_resolution", "index": 0,'),
    # These two are built by comprehension rather than appended, so the
    # disable guards the comprehension instead of a publish.
    ("uncited_reference",
     '    uncited = [{"type": "uncited_reference", "index": i,',
     '    uncited = []\n    _ = [{"type": "uncited_reference", "index": i,'),
    ("duplicate_reference_key",
     '    duplicates = [] if absent else [',
     '    duplicates = [] if True else ['),
]

# A record type no control notices the absence of is unwatched, whatever else
# the suite says about it. Measured 24 September: every one of the twelve has
# at least one, and the census prints the counts so the thin ones are visible.
#
# `unresolved_reference` read two and was the thinnest, which is what sent
# anyone looking at it. What was actually thin was the probe: two of its three
# emission sites were never disabled, so the row was about `no_year` alone.
# The real figure is whatever the fixed probe prints, and the lesson is that a
# suspiciously thin row is worth reading as a claim about the PROBE first.
CENSUS_FLOOR = 1
CENSUS_THIN = 2

# The suite's own control count, as a floor rather than an equality so that
# adding a control does not fail this file. It exists because a truncated
# baseline is indistinguishable from a real one by size alone, and on
# 25 September a run that died at 179 of 323 was used as the denominator for
# a twelve-emitter census. Raise it when the suite grows; never lower it to
# make a run pass.
BASELINE_FLOOR = 320

# KNOWN STALE as of 25 September, and left stale on purpose. This file now
# REFUSES rather than passing, and that refusal is the honest state.
#
# These twenty were read before they were listed, and they are still twenty
# controls that survive. What they are not is the ANSWER, because the run they
# came from never finished. The first empty run hit a `ZeroDivisionError`
# inside the suite after about twenty `[ok]` lines had printed, `run_suite`
# could not tell a crash from a control failing, and the truncated output was
# scored as a completed sweep. Every control after the crash looked like a
# non-survivor because it never printed, not because it went red.
#
# With the crash sites fixed, the empty run completes for the first time and
# the real figure is 134 of 323. Those 114 additional survivors have NOT been
# read. Re-pinning to 134 to make this file green would assert twenty times
# over the thing this file exists to catch: a number that passes because
# nobody looked at it.
#
# RESOLVED 25 September, and not by reading 130 labels.
#
# The twenty below are no longer the pass condition. Grouping the survivors by
# the suite's own headings showed all twenty-three groups are all-or-nothing —
# not one section has some controls surviving and some going red — which is
# what a suite organised by subject looks like and is also a hint that
# survival is a property of the SUBJECT rather than of the control. Measuring
# it directly confirmed that: 106 of the 109 unpinned survivors read no
# citation-side output at all, so an empty citation stream tells them nothing
# either way and there is nothing in them to read.
#
# Three did read it and passed anyway, and those three were the whole finding.
# They are repaired. The list below is kept as history and as a cross-check:
# a label that was read by hand and called sound, but measures as reading the
# empty output, means the hand reading and the measurement disagree.
#
# The first pass also found the shape to look for.
#
#     `any(...)` over an empty sequence is False.
#     `all(...)` over an empty sequence is True.
#
# So a control written as "fail if anything is wrong, otherwise ok" reports
# success when there is nothing to be wrong. C-027 did exactly that: two
# `any()` branches over the citations of its fixture, an `else: ok()`, and no
# check that the fixture produced any. C-026 sits directly above it on the same
# fixture and does NOT have the defect, because it compares a list against
# [1, 2, 3] rather than asking whether anything is wrong. One survived the
# empty run and the other did not, four lines apart.
#
# `not any(...)` and `not all(...)` are the safe direction: empty makes them
# fire rather than pass. The suite has 23 of these constructs and about
# thirteen are the unsafe shape. Each needs reading for a preceding emptiness
# guard; C-027 is the one confirmed so far and is fixed.
#
# The general discriminator, for whoever continues this: a survivor is
# legitimate when its fixture produces no citation record even in the baseline
# run, and vacuous when its fixture produces them normally and the assertion
# simply stops having anything to range over.
#
# Controls that legitimately survive with all three emitters off.
#
# Every one was read before it was listed. They fall into five groups, none of
# which reads a record the extractor emits:
#
#   heading and section detection      the `References` line rules, h1/h2
#   the style guard                    §10, which runs on raw text pre-extraction
#   direct calls                       a constant read, or an emitter called
#                                      straight and required to raise
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
    # excluded_candidate, and these two do not consume a record at all:
    # one reads EXCLUDED_REASONS as a constant, the other calls the
    # emitter directly and requires it to raise before anything is built
    "A2: a reason outside the closed set is refused, incl. bare_locator",
    "A2: excluded_reason is rc3's closed six-member set",
    # aborts, which stop before extraction runs
    "exit 2: a comma-less author-date document is refused",
    "exit 4: sectioning lives in h1: two h1, no h2",
    "exit 5: invalid utf-8",
    # summary schema: an assertion that a field is absent
    "A5: the summary reports a parse rate and no accuracy figure",
    # PAIRED ONLY, and REPAIRED 25 September. These three were pinned with
    # the honest note that each was sound only because of a positive sitting
    # beside it in the file, not because of anything inside itself. The read
    # probe then measured exactly these three, and no others, reading the
    # empty output — the measurement and the hand reading agreeing to the
    # label. Each now names its companion fixture itself, via `case(alive=)`
    # or an inline `elif`, so the pairing is structure rather than adjacency
    # and all three go red on an empty run. They are kept here as the record
    # of that agreement.
    "1499 is invisible, not unresolved",          # paired: "1500 is inside"
    "square brackets produce no record at all",   # paired: §10/C-080
    "a damaged group loses everything without the segments flag",  # paired:
                                                  # "with it, the good
                                                  # segments survive"
}


def ok_labels(text: str) -> list:
    return [m.group(1) for m in re.finditer(r"^\s*\[ok\] (.+)$", text, re.M)]


def labels_by_section(text: str) -> dict[str, list[str]]:
    """Passing controls, grouped by the suite heading they printed under.

    The survivor list is 130 long and reading it one control at a time is the
    wrong unit. The original twenty were accepted as five groups with one
    reason each — heading detection, the style guard, direct calls, aborts,
    summary schema — because a reason that holds for a group is checked once
    and applies to all of it.

    The suite already prints its own section headings. Attributing each `[ok]`
    to the last heading above it costs nothing and turns an undifferentiated
    list into the shape the reasons are actually written in.

    A group whose members all survive for the same reason is one judgement. A
    group where some survive and some go red is the interesting case, because
    the difference between them is the thing worth reading.
    """
    out: dict[str, list[str]] = {}
    section = "(before any heading)"
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^\s*\[ok\] (.+)$", line)
        if m:
            out.setdefault(section, []).append(m.group(1))
        elif not s.startswith(("[ok]", "FAIL:", "[")) and not line.startswith(" "):
            # A heading is a non-indented, non-record line. The suite writes
            # them as `rc2 §11 — summary fields and the invariants over them`.
            section = s
    return out


def ok_sites(src: str) -> list:
    """(line number, the literal text a label starts with) for each control.

    Used to turn a read's suite line number into the control that made it.
    Labels built with an f-string are keyed on the run of literal text before
    the first `{`, which is enough to match them by prefix.

    `case(...)` counts as a site as well as `ok(...)`, because `case` is the
    suite's own helper and calls `ok(label)` from inside itself, at line 227,
    on behalf of a control written hundreds of lines away. Without it every
    `case` call's reads pile onto the next literal `ok(` in the file: that is
    what put `B6: expand_year leaves an ordinary year and n.d. alone` on the
    finding list with five reads at lines 1642 to 1656, none of them its own.
    It calls `ce.expand_year` and reads no record at all.

    Line 227 is the only `ok()` in the suite that names another control; every
    other non-literal call sits at its own control's position.
    """
    out = []
    # Anywhere on the line, not just at its start: the suite writes
    # `else: ok(...)` in several places, and a site this misses widens the
    # span of its neighbour rather than simply being absent.
    for m in re.finditer(r"(?<![\w.])(?:ok|case)\(\s*f?(['\"])(.*?)\1", src):
        out.append((src.count("\n", 0, m.start()) + 1, m.group(2).split("{")[0]))
    return out


def reads_by_label(text: str, err: str, suite_src: str) -> tuple:
    """For each control, the citation-side reads made by its own source lines.

    Attribution is by POSITION IN THE SOURCE, not position in the output
    stream, and the difference is the whole correctness of this function.

    The obvious reading — every `[vacr]` marker printed since the previous
    `[ok]` belongs to the control that just passed — is wrong here, and wrong
    in the direction that manufactures findings. The suite collects its
    failures and prints them on the way out, so a control that goes red prints
    NOTHING at its own position. In the disabled run 193 of 323 go red, and
    every read all 193 made is credited to whichever survivor happens to print
    next. The first version of this said 8 survivors read the empty output,
    with clusters of twenty-two and thirty reads attached to single controls,
    which is what that leak looks like from the outside.

    Source position has no such failure mode. Each read reports the suite line
    that made it, each control owns the lines between the previous `ok()` call
    and its own, and a control that never ran contributes nothing to anyone.

    Returns (reads per label, labels whose `ok()` could not be located).
    """
    lines = [int(m.group(1)) for m in
             re.finditer(r"^\[vacr\] [^:]+:(\d+)$", err, re.M)]
    sites = ok_sites(suite_src)
    labels = ok_labels(text)

    # label -> (start, end] of the source lines that control owns
    span: dict[str, tuple] = {}
    unlocated: list[str] = []
    for lab in labels:
        # Longest matching literal, not the first. Several labels in this
        # suite share an opening run such as `§9.4: `, and taking the first
        # match would file a read against a control several hundred lines away.
        hit, best = None, -1
        for i, (line, lit) in enumerate(sites):
            if lit and lab.startswith(lit) and len(lit) > best:
                hit, best = i, len(lit)
        if hit is None:
            unlocated.append(lab)
            continue
        span[lab] = (sites[hit - 1][0] if hit else 0, sites[hit][0])

    out: dict[str, list[str]] = {}
    for lab, (lo, hi) in span.items():
        out[lab] = [f"{SUITE.name}:{n}" for n in sorted({
            n for n in lines if lo < n <= hi})]
    return out, unlocated


def duplicates(labels: list) -> list:
    seen, dup = set(), set()
    for x in labels:
        (dup if x in seen else seen).add(x)
    return sorted(dup)


def run_suite(source: str) -> set:
    """Run the suite against a temporary extractor built from `source`.

    A non-zero exit is EXPECTED here and is not an error: disabling an emitter
    is supposed to take controls red. So the return code cannot be the test of
    whether the run happened. A crash has to be told from a control failure
    some other way, and a Python traceback is the one signal a failing control
    never produces.

    That distinction was missing and it produced a false finding. Run on a
    Windows console on 25 September, the suite died on a `→` it could not
    encode partway through printing, and this function read the truncated
    output as a completed run: the census reported a baseline of 179 controls
    where the real number is 323, and then announced NOTHING WATCHES THIS
    RECORD TYPE for seven record types. Every one of those seven is watched.
    The exit code was 1, so the tool was not silent, but the sentence it
    printed was false and read like a finding.

    Two guards, because the encoding fix alone would only close this instance.
    The child is given UTF-8 explicitly, and a crash is refused rather than
    counted.
    """
    original = EXTRACTOR.read_text(encoding="utf-8")
    # newline="" so a run on Windows does not rewrite the extractor's line
    # endings on its way past. `write_text` translates \n to \r\n by default,
    # and the file it writes back is the working tree's own extractor.
    EXTRACTOR.write_text(source, encoding="utf-8", newline="")
    try:
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, str(SUITE)], env=env,
                           capture_output=True, text=True, timeout=600)
        if "Traceback (most recent call last)" in (r.stderr or ""):
            raise RuntimeError(
                "the suite crashed rather than failing controls, so its "
                "output says nothing about which controls hold:\n"
                + "\n".join((r.stderr or "").strip().splitlines()[-3:]))
        # The raw text is kept because grouping survivors by the suite's own
        # headings needs the lines between the `[ok]`s, and a list of labels
        # has thrown those away.
        run_suite.last_stdout = r.stdout
        # The read markers arrive here rather than on stdout, for the reason
        # given in READ_PROBE.
        run_suite.last_stderr = r.stderr
        return ok_labels(r.stdout)
    finally:
        # Restored in a finally so an interrupted sweep cannot leave a
        # disabled emitter in the working tree. A sweep that breaks the thing
        # it measures and does not put it back is worse than no sweep.
        #
        # newline="" on the RESTORE as well as the write, which the first
        # version of this fix missed. `read_text` collapses CRLF to \n and the
        # default `write_text` expands it again, so on Windows every sweep
        # rewrote all 3670 lines of the extractor's endings. Put back means put
        # back byte for byte.
        EXTRACTOR.write_text(original, encoding="utf-8", newline="")


def census(source: str, base: set) -> int:
    """Per emitter, how many controls notice when it stops emitting.

    The complement of the survivor sweep. That one asks whether a control is
    asleep; this asks whether a record type is watched. One emitter at a
    time, because the question is per record type and a combined disable
    could not attribute the reds.

    Thirteen suite runs, so this is not on the default path.
    """
    print("  census: controls that go red when one emitter is disabled\n")
    problems = 0
    for label, old_text, new_text in EMITTERS + NARROW_EMITTERS:
        pairs = (list(zip(old_text, new_text))
                 if isinstance(old_text, tuple) else [(old_text, new_text)])

        # How many places in the extractor build this record, counted in the
        # source rather than assumed. A census row is only about a RECORD TYPE
        # if every site that produces it is disabled; patch two of three and
        # the row silently becomes about one code path, still printing the
        # record type's name. `unresolved_reference` was in exactly that state
        # and read `2  thin`.
        #
        # This counts sites against patches. It does not verify that each
        # patch lands on a site, which a patch like `duplicates = [] if True`
        # makes awkward, but it is what catches the defect that occurred and
        # it fails loudly when a new emission site is added later.
        sites = source.count(f'"type": "{label}"')
        if sites != len(pairs):
            print(f"    {label:30}  PROBE INCOMPLETE, {len(pairs)} patch(es) "
                  f"for {sites} emission site(s); reported rather than passed")
            problems += 1
            continue

        patched, broken = source, None
        for old, new in pairs:
            if patched.count(old) != 1:
                broken = patched.count(old)
                break
            patched = patched.replace(old, new, 1)
        if broken is not None:
            print(f"    {label:30}  PROBE BROKEN, a patch matched {broken} "
                  f"times; reported rather than passed")
            problems += 1
            continue
        survivors = set(run_suite(patched)) & base
        red = len(base) - len(survivors)
        note = ""
        if red < CENSUS_FLOOR:
            note = "   NOTHING WATCHES THIS RECORD TYPE"
            problems += 1
        elif red <= CENSUS_THIN:
            note = "   thin"
        print(f"    {label:30}  {red:4d}{note}")
    print()
    if problems:
        print("  A record type no control notices the absence of is unwatched,")
        print("  whatever else the suite says about it.")
        return 1
    print(f"  every emitter has at least {CENSUS_FLOOR} control watching it.")
    return 0


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

    # The read probe is applied to the disabled build only, and a missing
    # anchor is reported rather than skipped: a sweep that silently ran
    # without it would print "reads nothing" for all 109 survivors, which is
    # the most convincing wrong answer this file could give.
    for label, old, new in READ_PATCHES:
        if disabled.count(old) != 1:
            print(f"  {label} has no unique anchor ({disabled.count(old)} "
                  f"matches). Without it every survivor would be reported as "
                  f"reading nothing, so this refuses rather than running.")
            return 2
        disabled = disabled.replace(old, new, 1)

    # The patched build is compiled before it is ever written over the working
    # tree's extractor. `READ_PROBE` is injected Python held in an ordinary
    # string, so an escape that the sweep expands on its way in produces a
    # build that does not parse — and the symptom is the suite dying, which
    # reads like a finding about the suite. Compiling here names the real
    # cause, and does it before the extractor has been touched.
    try:
        compile(disabled, str(EXTRACTOR), "exec")
    except SyntaxError as e:
        print(f"  the patched extractor does not parse: {e.msg} at line "
              f"{e.lineno}. The patch is wrong, not the suite, and nothing "
              f"has been written to the working tree.")
        return 2

    print("  baseline: the suite as it stands")
    base_labels = run_suite(source)
    if not base_labels:
        print("  the suite produced no [ok] lines at all; nothing to compare")
        return 2
    # A baseline is the denominator for every number below it, so a baseline
    # that is merely PLAUSIBLE is worse than none. "no [ok] lines at all" was
    # the only check here, and a run that died two thirds of the way through
    # sails past it: on 25 September this printed 179 and went on to compute a
    # whole census against it. The floor is the count the suite reports for
    # itself, which it prints and this can read.
    if len(base_labels) < BASELINE_FLOOR:
        print(f"    {len(base_labels)} controls pass, but the suite has at "
              f"least {BASELINE_FLOOR}. A short baseline means the run ended "
              f"early, and every count below it would be measured against a "
              f"denominator that is not the suite.")
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

    if "--census" in sys.argv:
        return census(source, base)
    print("  with all three citation-side emitters disabled")
    survivors = set(run_suite(disabled))
    print(f"    {len(survivors)} of {len(base)} still pass\n")

    # A control that stops passing is not interesting here; that is the
    # expected outcome. Only the survivors are the question.
    #
    # Every survivor is examined, not only the ones outside the pinned list.
    # The pin was a list of twenty labels read by hand, and this file spent a
    # week refusing because the real figure is 130 and re-pinning to 130 would
    # have asserted, twenty times over, the thing it exists to catch. The way
    # out was not to read 130 labels. It was to find the property that makes
    # reading them unnecessary and check THAT:
    #
    #     no surviving control reads citation-side output
    #
    # A survivor that reads nothing the three emitters produce is testing a
    # constant, the reference side, the output bytes or an abort, and an empty
    # citation stream tells it nothing either way. A survivor that DOES read
    # is the defect. So the pass condition is a measured invariant over all of
    # them rather than a list, and it cannot go stale as the suite grows.
    survivors &= base
    new = sorted(survivors)

    # Grouped by the suite's own headings rather than listed flat. A reason
    # that holds for a group is one judgement covering all of it, which is how
    # the original twenty were accepted; 130 read singly is the wrong unit and
    # does not get done.
    out = getattr(run_suite, "last_stdout", "")
    sections = labels_by_section(out)
    where = {lab: sec for sec, labs in sections.items() for lab in labs}
    reads, unlocated = reads_by_label(
        out, getattr(run_suite, "last_stderr", ""),
        SUITE.read_text(encoding="utf-8"))

    # The survivors split in three, and only one part is a finding. This is a
    # measurement, not a heuristic over the labels: a control either read
    # `cits`, `unres` or `excl` on its own source lines or it did not.
    unk = [n for n in new if n in unlocated]
    reading = [n for n in new if n not in unlocated and reads.get(n)]
    blind = [n for n in new if n not in unlocated and not reads.get(n)]

    if new:
        print("  Passing with nothing emitted.\n")
        print(f"  {len(reading)} of the {len(new)} READ citation-side output "
              f"and passed anyway.")
        print(f"  {len(blind)} never touched it, so they are testing "
              f"something else.")
        if unk:
            print(f"  {len(unk)} could not be located in the suite source, so "
                  f"they are neither.")
        print()

        if reading:
            print("  READ THE EMPTY OUTPUT AND STILL PASSED. This is the whole")
            print("  finding; everything below it is context. Each of these")
            print("  asked the citation side a question, got nothing, and")
            print("  reported success:\n")
            for lab in reading:
                print(f"    {lab}")
                print(f"      {where.get(lab, '(no heading found)')}")
                for site in reads[lab]:
                    print(f"      read at {site}")
                print()
            print("  A control here is either asserting an absence, which an")
            print("  empty run satisfies for free, or counting over a sequence")
            print("  that is empty. Read the line named above, then either add")
            print("  a live-fixture guard or record what it is really for.\n")

        if blind:
            print("  Read nothing the three emitters produce. Grouped by the")
            print("  suite's own headings, because the reason is the group's")
            print("  rather than the control's:\n")
            grouped: dict[str, list[str]] = {}
            for n in blind:
                grouped.setdefault(
                    where.get(n, "(no heading found)"), []).append(n)
            for sec in sorted(grouped, key=lambda s: (-len(grouped[s]), s)):
                labs = grouped[sec]
                total = len(sections.get(sec, labs))
                print(f"    {sec}")
                print(f"      {len(labs)} of this section's {total} survive, "
                      f"none reading citation output")
            print()
            print("  A whole section reading nothing is the expected shape: it")
            print("  is testing a constant, the reference side, the output")
            print("  bytes or an abort. One reason covers the section. What")
            print("  would NOT be expected, and is worth looking for, is a")
            print("  section whose subject IS the citation side appearing in")
            print("  this list at all.\n")

        if unk:
            print("  Could not be matched to an `ok()` call in the suite")
            print("  source, so nothing is claimed about them either way:\n")
            for lab in unk:
                print(f"    {lab}")
            print("\n  A label built at run time from values this file cannot")
            print("  see. Reported rather than silently filed as clean.\n")

    # The twenty were read by hand before the read probe existed and judged
    # sound. Any of them turning up in `reading` is the hand reading and the
    # measurement disagreeing about the same control, which is worth saying
    # out loud rather than letting the measurement quietly win.
    contradicted = sorted(set(reading) & PINNED_SURVIVORS)
    if contradicted:
        print("  Read by hand and recorded as sound, but measured reading the")
        print("  empty output. One of the two is wrong:\n")
        for lab in contradicted:
            print(f"    {lab}")
        print()

    if reading or unk:
        return 1

    print(f"  no surviving control reads citation-side output.")
    print(f"  {len(blind)} controls pass with all three emitters disabled and")
    print("  not one of them asks the citation side anything, so an empty")
    print("  citation stream tells them nothing either way. That is the")
    print("  property worth holding, and unlike a list of labels it does not")
    print("  go stale when the suite grows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
