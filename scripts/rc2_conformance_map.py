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
    NOT           not implemented, with the reason named AND, where one
                  exists, an anti-needle that makes the verdict falsifiable
    NOT ASSESSED  no honest probe was written, or a probe went stale in
                  either direction. NEVER reported as met.

The distinction between MET and "it probably works" is the whole point. A case
is only MET when a control would go red if the behaviour were removed, which
this repository has learned twice is not the same as the behaviour appearing
to be present.

A NOT verdict needs the same treatment and did not have it. MET claims were
already falsifiable — remove the control and the needle stops matching — but
NOT claims were hand-maintained text that nothing could contradict. On
21 September, C-053 to C-060 kept reading "not implemented" for a full commit
after §9.4 landed, because implementing a behaviour gives this file no way to
notice. Each NOT now carries an anti-needle: the string that would appear if
the case WERE implemented. Its presence does not promote the case, it retires
the verdict. Seventeen cases have no honest anti-needle; they say so, and the
run counts them, because an unguarded claim that admits it is unguarded is a
different thing from one that does not.

WHAT AN ANTI-NEEDLE MUST BE, learned the hard way on 22 September
-----------------------------------------------------------------
The guard's first real outing produced both of its possible errors at once.

    FALSE POSITIVE   `exit 6` and `ambiguous_author_resolution` were the bare
                     concept names. Seven verdicts were retired by a COMMENT
                     explaining why those things are absent. Prose about a
                     missing feature is not the feature.

    FALSE NEGATIVE   `stop_reduced_candidate` was an identifier invented when
                     the case was written. The implementation calls it
                     `stop_reduced_phrase`, so the needle never matched and
                     five completed cases went on reading NOT — exactly the
                     failure the guard exists to prevent, surviving inside the
                     guard.

So an anti-needle must name an ARTIFACT a working implementation emits — a
serialized field, an emitted record type, a constant it must define — and it
must be read off the implementation rather than guessed. A word that could
appear in a sentence about the feature is not an anti-needle, and neither is
a name nobody has written yet.

A THIRD RULE, and it cost three verdicts on 23 September alone
--------------------------------------------------------------
A needle is searched for in SOURCE. So it must be a substring of the source,
not of what the source prints. Two ways that goes wrong, both hit today:

    f-strings     the control prints "all 109 tokens" and the file reads
                  `all {len(declared_stop)} tokens`. The needle matched
                  nothing. Same for `\\&`, which prints as `\&`.
    line breaks   a message wrapped across two string literals is two
                  substrings in the file and one in the output. A needle
                  spanning the break matches nothing.

Each time, the guard did its job and reported NOT ASSESSED rather than
passing — which is the guard working, not failing. But three in one day is a
habit rather than an accident, so the rule is written here: before adding a
needle, grep the source for it. `grep -c -- "<needle>" scripts/<file>.py`
must print 1.
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
    # rc2 §2 and §1.3, implemented 22 September. These three were NOT for as
    # long as this file has existed, and carried `None` for an anti-needle on
    # the stated ground that "a byte-offset contract leaves no distinctive
    # identifier behind". That was true of the implementation and false of the
    # controls: what a byte contract leaves behind is a control that slices
    # the manuscript by a record's own coordinates, and those name themselves.
    #
    # The implementation needle is `to_byte_coordinates` rather than anything
    # in §2's prose, and the suite needles are the three controls' own
    # sentences. C-003's characters are rc2's — β, —, ’, ﬁ — not chosen here.
    "C-002": (("unicodedata.normalize(\"NFC\"",),
              ("§2/C-002: CRLF and lone CR become LF",), "MET",
              "CRLF and lone CR to LF, then NFC, canonical bytes pinned"),
    "C-003": (("def to_byte_coordinates",),
              # Not the whole sentence: the suite writes the ampersand inside
              # an f-string, so its SOURCE carries `\\&` where its output
              # carries `\&`. A needle copied from the printed line would
              # never match the file it is searched in — the same shape as the
              # `stop_reduced_candidate` false negative recorded above.
              ("spans still slice their own text",
               "substitutions precede canonicalisation"),
              "MET",
              "every span slices its own text, with the fixes on and off"),
    # C-004 is the converse case and needs its own evidence: three counts
    # rc2 §1.3 keeps in code points. Converting THOSE to bytes would be just
    # as silent as leaving the coordinates unconverted, so each is exercised
    # on input where the two units disagree.
    "C-004": (("if len(assembled) > 1500:",),
              ("§1.3/C-004: osa is one substitution apart",
               "§1.3/C-004: CORE's floor is 2 code points"),
              "MET",
              "osa, CORE's floor and the overlong threshold stay code points"),
    # rc2 §13 and §12.1, implemented 22 September. Every control here compares
    # BYTES: §12.1's clauses are byte properties, and a test that parses the
    # lines back cannot see a single one of them.
    "C-071": ((), ("C-071: --out and stdout are byte-identical",), "MET",
              "the file is the stdout stream, exactly"),
    "C-072": ((), ("C-072: a directory target is named for canonical_sha256",),
              "MET", "content-derived name, over the INPUT bytes"),
    "C-073": ((), ("C-073: atomic publication leaves no scratch file",), "MET",
              "temp in the destination dir, rename after completion"),
    # §12.1's byte properties and §12.3's key order, the latter checked
    # against rc2's OWN declared records rather than against this file's
    # table — comparing output to the table it was built from can only show
    # the table was not applied, never that it is wrong.
    #
    # `summary` closed on 23 September: all twenty-one of rc2's fields, in
    # rc2's order, checked against rc2's own bytes.
    #
    # Still PARTIAL, for two divergences that are named rather than hidden:
    #
    #   1. records carry fields beyond rc2's declared set — rc3's
    #      `candidate_state`, §6.3's `stop_reduced_phrase`, §8.1's two
    #      candidate keys. rc3 requires them, so a byte golden against rc2
    #      differs on the tail by design and this will not close while both
    #      documents are in force.
    #   2. `meta` CLOSED on 23 September. rc2 §1.1's four rule-identity
    #      fields are emitted and the question that held them back turned out
    #      not to need asking: every rule the extractor runs is rc2's or
    #      rc3's, so `3.3` was a wrong label rather than an undecided one.
    #
    # So C-068 is PARTIAL on (1) alone now, and (1) will not close while both
    # rc2 and rc3 are in force — rc3 REQUIRES the extra fields.
    "C-068": (("CITATION_RULE_VERSION = ",),
              ("record types lead with the key ",
               "rule version and ET_AL_MIN_AUTHORS"),
              "PARTIAL",
              "meta and summary closed; rc3's extra fields keep it open"),
    # rc2 §11.1's extraction invariant, executable for the first time on
    # 23 September — `total_citation_occurrences` was among the twelve fields
    # this file did not emit, so the equation had no left-hand side.
    #
    # Not one of rc2's 86 cases. Recorded here anyway, with C-052's entry
    # extended below to the second control, because the map's job is to say
    # what is pinned and §11.1 now is.
    "C-083": ((), ("C-083: the same input produces byte-identical output",),
              "MET", "two runs, same bytes"),
    # §12.2's two halves. "Blocks never interleave" was being broken: the two
    # §9.4 diagnostics shared one list, so missing_reference reopened seven
    # times on paper ad1e3ff9.
    "C-069": ((), ("§12.2: blocks are in order and never interleave",), "MET",
              "block order stated once, and no block reopens"),
    # PARTIAL until 22 September for one reason — "references_source not
    # emitted" — which §10's work fixed as a side effect of needing the third
    # value, `not_available`.
    "C-006": (("REF_NAMES",), ("C-006: a marked-up References heading",),
              "MET", "detected, from a marked-up heading"),
    "C-007": (("_unmarked_reference_label",),
              ("a standalone `References` line is a section boundary",),
              "MET", "inferred, from a bare label with the confirmation"),
    # rc2 §10 and §11.3, implemented 22 September. The abort these replace
    # was v3.3's: rc2 §14 allocates exit 3 to "invalid section map" and gives
    # a missing bibliography no exit at all.
    "C-009": ((), ("§10: no bibliography is processed, not refused",), "MET",
              "extract, no identity, one bibliography_absent"),
    "C-066": ((), ("C-066: not_evaluated is a different state",), "MET",
              "undetermined kind, not_evaluated state, null key"),
    "C-067": ((), ("C-067: identity counts null, extraction counts real",),
              "MET", "null is not-evaluated; 0 would be a measurement"),
    # rc2 §5 and §6, implemented 22 September. Additive fields on the
    # citation record; nothing renamed, so the gold path is untouched.
    "C-026": ((), ("C-026: sentence_index continues across a heading",),
              "MET", "0-based, continuous across sections"),
    "C-027": ((), ("C-027: previous_sentence_end carries the prior",), "MET",
              "prior content_end, null for the first body sentence"),
    "C-028": ((), ("C-028: standalone marks the citation-only sentence",),
              "MET", "both ends, positional only"),
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
    # "one case per prefix", over rc2's closed list rather than this file's.
    # The same exhaustiveness that found five missing STOP tokens found five
    # missing PREFIX cues an hour later — rc2's own "five newly added
    # multiword forms", which arrived with rc2 and were never picked up here.
    # Unlike the STOP gap this one was NOT latent: two corpus groups parsed
    # while silently dropping the citation sitting behind the prefix.
    "C-016": (('"for a similar approach, see", "for discussion, see",',),
              ("the PREFIX set must equal rc2's closed list",
               "every closed PREFIX form must parse"),
              "MET",
              "all eleven parse, and no cue leaks into author_phrase"),
    # STRUCTURAL, and the note says so. On every input that can be built the
    # two orders agree — a short match leaves a lowercase remainder, CORE
    # needs a capital, the branch fails and the alternation backtracks. What
    # is checkable is that the compiled alternation offers the long form
    # first, which is what rc2's "before considering a shorter member" asks.
    "C-017": (("key=lambda c: (-len(c), c)",),
              ("a longer form must be offered before",),
              "MET",
              "longest-first in the compiled alternation; structural"),
    # "one case per token", and rc2 §3.2 calls the list "closed and versioned"
    # — which is the one situation where testing a sample proves nothing about
    # the rest. The exhaustive control found five tokens missing from this
    # file: rc2's last line, panel / column / row / appendix / exhibit, with
    # zero occurrences anywhere in the corpus. `Panel (2020)` was keying
    # `panel|2020`, and `As Panel Smith (2020)` was losing a real citation.
    "C-018": (('"panel", "column", "row", "appendix", "exhibit",',),
              ("tokens, and no others — this file's",
               "STOP token leading a candidate must never"),
              "MET",
              "one case per token, over rc2's list rather than this file's"),
    "C-021": ((), ("a possessive surname keys to the bare name",), "MET",
              "person candidate only, surface unchanged"),
    # These four were implemented and controlled BEFORE the anti-needle guard
    # existed, and the map went on reporting them NOT. Caught 22 September by
    # the guard, which is the case it was built for — and a reminder that the
    # stale NOTs it finds are not always recent work.
    "C-022": ((), ("C-022: the surface key is a JSON array",), "MET",
              "JSON array, bare year an integer, suffixed year a string"),
    "C-023": ((), ("C-023: punctuation and `and`/`&` remain",), "MET",
              "lower and whitespace only; surfaces stay distinct"),
    "C-024": ((), ("C-024: two surface groups, one identity",), "MET",
              "the surface key never reaches identity"),
    "C-025": ((), ("C-025: the summary count and the null",), "MET",
              "emitted with a bibliography and without; C-009 landed"),
    # C-030 said "emitted" and was PARTIAL. It WAS emitted — as a keyless
    # `reference` row carrying no_year in suspect_reasons, where the case says
    # "no reference row/key" and §7.3 closes that list at three. Corrected
    # 22 September; one corpus entry reached it, an "In press." reference.
    "C-030": ((), ("C-030: a no-year entry is unresolved",), "MET",
              "unresolved_reference(no_year), no row and no key"),
    "C-032": ((), ("C-032: suspect_reasons are closed and ordered",), "MET",
              "the closed three, in §7.3's order"),
    "C-070": ((), ("C-070: multi-year citations order by year",), "MET",
              "§12.4's year key breaks the position tie"),
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
    # Two controls, and the second is the one that earned its place. §11.2's
    # partition was pinned in the extractor's own vocabulary; the new control
    # checks rc2's equation over rc2's field names, with a resolved and an
    # unresolved occurrence both present so neither side can be empty.
    # rc2 §8.5's fourth bullet and §11.4 together: a key mapped to more than
    # one reference row is not a unique match, and reserved indices count +0
    # "unless independently matched by another unambiguous occurrence". The
    # control asserts both halves, because excluding everything would satisfy
    # the first alone.
    # rc2 §14's twelve finding conditions, implemented 23 September. C-078's
    # NOT reason was "the exit-1 finding set is not closed" — wrong about rc2,
    # which closes it in as many words, and right about this file, which tested
    # three proxies. Eight of the twelve coincided with "not every citation
    # uniquely matched" and so were never consulted; three did not coincide at
    # all and each exited 0 where rc2 requires 1.
    #
    # The suite needle is the COUNT control, which reads rc2's list rather
    # than this file's tuple, so the verdict goes stale if either moves.
    "C-078": (("FINDINGS_FORCING_EXIT1 = (",),
              # NOT the printed line: the control builds the count with an
              # f-string, so its SOURCE reads `all {len(spec14)} of rc2's`.
              # A needle copied from the output would never match the file it
              # is searched in — the third time that shape has appeared.
              # A needle must also fit on ONE source line. The first attempt
              # here spanned the control's line break and matched nothing,
              # which is the same mistake in a third guise.
              ("of rc2's finding conditions are",),
              "MET", "twelve conditions, counted against rc2's own list"),
    "C-051": (("keyed_once = {k for k, n in counts.items() if n == 1}",),
              ("C-051: reserved indices",), "MET",
              "a duplicated key counts +0; the unambiguous match still counts"),
    "C-052": ((), ("§11.2: the identity classes partition",
                   "§11.2/C-052: resolved + ambiguous + not_resolved"),
              "MET",
              "identity partition exact, in rc2's names, both sides non-empty"),
    # rc2 §6.3 / §8.1 / §8.4, implemented 22 September. The guard did NOT
    # flag these, because their anti-needle was `stop_reduced_candidate` —
    # a name guessed when the case was written, and the implementation calls
    # it `stop_reduced_phrase`. A guessed identifier cannot go stale because
    # it was never true.
    "C-019": ((), ("§6.3: author_phrase is the full run",), "MET",
              "reduction is additive, both phrases survive"),
    "C-020": ((), ("C-020: the full surface is kept",), "MET",
              "STOP reduction never rewrites author_phrase"),
    "C-040": ((), ("§8.3 row 4: no_match/unique → stop_reduced",), "MET",
              "F=no_match, S=unique"),
    "C-041": ((), ("§8.3 row 5: no_match/nonunique → stop_reduced",), "MET",
              "F=no_match, S=nonunique, plus ambiguous_citation"),
    "C-055": ((), ("§8.4: two internal candidates suppress",), "MET",
              "the corpus reaches none; the control builds the input"),
    # §8.3 rows 6-9, §8.5, §8.6 — implemented 22 September. The anti-needle
    # named the emission this time and fired correctly on all eleven.
    # All four state pairs are now injected individually through §15's seam,
    # which is how the matrix says to evidence them. They were PARTIAL for
    # half an hour on the reasoning that one `if` serves all four — true, and
    # not what the case asks: rc2 wants each pair exercised, and injection is
    # how.
    **{c: ((), ("§15: all four different-key state pairs",), "MET",
           "injected per rc2 §15, its own state pair")
       for c in ("C-042", "C-043", "C-044", "C-045")},
    "C-046": ((), ("§15/§8.6: same candidate_key on both lookups",), "MET",
              "§15's mandatory case: exit 6, reason named"),
    "C-047": ((), ("C-047: a shared reference index is ambiguity",), "MET",
              "guards on equal keys, not overlapping indices"),
    "C-048": ((), ("C-048: the record carries both candidates",), "PARTIAL",
              "both candidates named; rc2 asks for a byte golden"),
    "C-049": ((), ("§8.5: ambiguity-reserved references leave the pool",),
              "MET", "reserved indices emit no uncited_reference"),
    # §9.1's record, implemented 23 September. The groups were computed here
    # from the start — `unique_keys` is their complement and §8.5, §9.4 and
    # §9.6 all depend on it — and never emitted, so the one thing a reader
    # needed in order to see why those references were held back was the one
    # thing missing from the output. Five groups across four papers.
    #
    # `cited` gets both branches: every real corpus group is cited, so a field
    # hardcoded `true` passes the entire corpus and only a fixture catches it.
    "C-050": ((), ("§9.6: a duplicated reference key is not a uncited",
                   "§9.1: one record for"),
              "MET",
              "the record is emitted, and cited has both branches"),
    # rc2 §9.4 / §9.5, implemented 21 September. These eight sat in
    # NOT_IMPLEMENTED for a full commit after the behaviour landed, which is
    # what the anti-needle guard below now exists to prevent.
    # PARTIAL until 23 September on "identity_authority not emitted", which
    # rc2 §12.3 declares as the literal `"candidate"`. Emitting it closes both,
    # and it is a stronger statement than the two nulls it replaced: an absent
    # `citation_key` cannot be misread as an unestablished one, and the literal
    # says positively what authority the record carries. The controls now
    # require the fields to be ABSENT rather than null.
    "C-053": (('"identity_authority": "candidate",',),
              ("§9.4: missing_reference preserves the candidate",),
              "MET", "no citation_key at all, and identity_authority=candidate"),
    "C-054": (('"identity_authority": "candidate",\n'
               '                "reference_index": ri,',),
              ("§9.4: a possible_mismatch establishes no citation_key",),
              "MET", "same rule on the other diagnostic, same evidence"),
    # These three were PARTIAL on 21 September because each case is named for
    # a "precedence" that could not be exercised. Alex Zamurko amended §9.4
    # that evening, replacing the precedence list with "a pair qualifies when
    # EXACTLY ONE rule matches" and leaving ordering to the reference scan.
    # The unexercisable thing is gone from the normative text, so what remains
    # in each case is its acceptance column, and that is pinned.
    #
    # The case TITLES in rc2 file 03 still read "precedence"; the amendment
    # arrived in Slack and file 03 has not been reissued. Same standing as the
    # 20 September §9.3 amendment this implementation already follows.
    "C-056": ((), ("§9.4: the CORE length floor stops short surnames",),
              "MET", "kind/year/CORE bound pinned; precedence withdrawn"),
    "C-057": ((), ("§9.4: EXACTLY ONE rule can match",), "MET",
              "phrase equality and ±1 year pinned"),
    "C-058": ((), ("§9.4: all three repair rules pair their reference",),
              "MET", "adjacent digit swap pinned"),
    "C-059": ((), ("§9.4: a person candidate never pairs with a non-person",),
              "MET", "cross-kind pairing refused"),
    # rc2 §9.6, implemented 22 September. The anti-needle added the night
    # before caught this entry going stale on its first real occasion: the
    # NOT verdict was still standing while the behaviour was in the file.
    #
    # PARTIAL rather than MET, and for one reason only. The case names three
    # exclusions; exact matches and mismatch-paired references are pinned,
    # and so are two more the case implies (unique keys, keyless rows). The
    # third, ambiguity-reserved references, cannot be exercised because
    # nothing reserves any yet — C-049 and C-050 are NOT. Claiming MET would
    # mean claiming a control for an exclusion with no input.
    "C-061": ((), ("§9.6: a mismatch-paired reference does not reappear",),
              "PARTIAL",
              "exact and paired pinned; no reserved refs exist to exclude"),
    "C-060": ((), ("§9.5: merge_suspected is targeted at the candidate",),
              "MET", "both halves pinned: targeted, and it does fire"),
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

# Not implemented: (reason, anti-needle). Grouped so the shape of what is
# missing is legible — most of it is one architecture and one output contract,
# not sixty unrelated gaps.
#
# THE ANTI-NEEDLE, and why it exists
# ----------------------------------
# A CHECKS verdict degrades to NOT ASSESSED when its needle stops matching, so
# a MET claim cannot outlive the control behind it. A NOT verdict had no such
# guard, and on 21 September eight of them — C-053 to C-060 — went on reading
# "not implemented" for a full commit after §9.4 landed. Nothing was wrong
# except that a hand-maintained claim had no way to notice it had become false.
#
# The anti-needle is the string that would appear in the source IF the case
# were implemented. Its presence does not mean the case is met; it means this
# verdict can no longer be trusted, and the run says NOT ASSESSED and exits 1.
#
# Some cases have no honest anti-needle — a byte-offset contract or a
# determinism golden leaves no distinctive identifier behind. Those carry None
# and are COUNTED in the output, so the size of the unguarded set is visible
# rather than silent. Inventing a needle for them would put this file back in
# the business of green-for-the-wrong-reason.
NOT_IMPLEMENTED = {
    # Rows 6 to 9 of §8.3, and everything they need. All blocked on the same
    # thing: an occurrence whose BOTH candidates match needs
    # `ambiguous_author_resolution` for the different-key case and exit 6 for
    # the same-key case, and neither exists. The extractor raises Abort(6) for
    # both rather than guessing, which refuses correctly and implements
    # neither.
    #
    # The anti-needle names the EMISSION, not the concept. An earlier version
    # used the bare words `ambiguous_author_resolution` and `exit 6`, and both
    # matched the prose explaining why those things are missing — so seven
    # verdicts were retired on 22 September by a comment rather than by code.
    # Two of the eleven turned out to be unreachable rather than unbuilt, and
    # they are different kinds of unreachable. Both are NOT, with the reason
    # naming which.
    # C-051 moved out of here on 23 September. Its NOT reason had gone stale
    # in the worse of the two directions: not "implemented and still reading
    # NOT", but "the stated obstacle was removed and the rule underneath was
    # broken". The summary gained `uniquely_matched_works` that morning; a key
    # held by two references was still counted as a unique match. See CHECKS.
    "C-077": ("the exit-6 CONDITION is executed under §15 (see C-046); what "
              "is unpinned is the two-line error stream's exact bytes, which "
              "needs a byte golden this repository does not have",
              '"code": 6, "reason"'),

    # No honest anti-needle. Each says why.
    **{c: ("determinism not byte-pinned; 'byte-identical' already appears in "
           "prose, so it cannot serve as a needle", None)
       for c in ("C-029", )},
    **{c: ("outside the pilot scope — rc2 itself marks these OUTSIDE_PILOT, "
           "so no local change can make the verdict stale", None)
       for c in ("C-084", "C-085", "C-086")},
    "C-005": ("heading contract only partially pinned; 'heading contract' "
              "already names an existing exit-4 control", None),
    "C-015": ("verbatim span is kept but not pinned by a control", None),
    "C-080": ("true but unpinned: numeric citations never become identity",
              None),
    "C-081": ("the corpus still carries unresolved findings", None),
    "C-082": ("no timed termination test", None),
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

    both = impl + suite
    rows, tally, broken, unguarded = [], Counter(), [], []
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
            reason, anti = NOT_IMPLEMENTED[cid]
            if anti is None:
                verdict, note = "NOT", reason
                unguarded.append(cid)
            elif anti in both:
                # The thing this case said was missing is now present. The
                # verdict is not wrong-and-failing, it is no longer evidence.
                verdict, note = "NOT ASSESSED", f"NOT may be stale: {anti!r}"
                broken.append(cid)
            else:
                verdict, note = "NOT", reason
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

    if unguarded:
        print(f"\n  {len(unguarded)} NOT verdict(s) carry no anti-needle and")
        print("  so cannot notice if the behaviour is implemented. Each says")
        print(f"  why: {', '.join(unguarded)}")

    if broken:
        print(f"\n  {len(broken)} verdict(s) went stale and are reported as NOT")
        print(f"  ASSESSED rather than passing: {', '.join(broken)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
