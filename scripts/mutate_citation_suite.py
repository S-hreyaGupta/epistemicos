#!/usr/bin/env python3
"""Does the conformance suite actually hold the extractor down?

    python scripts/mutate_citation_suite.py

Exit 0 = every mutation was caught.

`test_citation_extract.py` passes. That is not evidence on its own, and this
session has produced the counter-example three separate times: a check that
passes for a reason other than the one it is named for, found by probing and
never by a control going red. So each mutation below breaks one rule the
extractor is supposed to follow, and the suite is expected to notice. A
mutation that survives means the control naming that rule is not testing it.

The mutations are textual substitutions on a copy of the source. If a
substitution does not apply — because the line it targets was rewritten — that
is reported as a broken probe rather than a pass, since a probe that silently
mutated nothing would be the same defect one level up.

The fourth column is the control that MUST go red, and it is checked
------------------------------------------------------------------
Until 21 September this file asked only whether the suite went red at all. It
did not check *which* control did, so the fourth column was a human-readable
note that nothing verified. When the check was finally applied, 21 of 34
mutations turned out to name a control that does not catch them — every one
reported as caught, for years, on the strength of some other control failing.

The same defect this file exists to find, one level up: "something failed" is
not evidence that the named rule is held.

Most were naming drift and are corrected. One was not, and was chased rather
than renamed away:

    "particles are dropped from the key" does NOT take
    `van der Maas particle surname` red.

INVESTIGATED AND CLOSED, 21 September. It is not a defect, and the answer is
worth more than the question was.

`first_core` reaches a leading-particle surname two ways: the leading-particle
`while` loop, and rc3 B1a's optional second-core block below it. They overlap.
Disabling the loop and comparing seventeen particle surnames, only three come
out differently, and `van der Maas` is not among them — the second-core block
produces it identically. So the control passes whether or not the rule it names
is implemented, because another mechanism silently covers that exact input.

Of the three shapes that DO distinguish the loop:

    Da silva           reachable, and `a lower-case core after a particle is
                       a surname` already pins it
    da Silva Costa     NOT reachable — SURNAME is (PARTICLE WS)* CORE and the
                       second core needs rc3 B1a, which is reverted, so the
                       span never reaches first_core
    van der van Maas   three particles, not a name anyone writes

So the mutation is correctly caught by the B2 control, and no new control is
added: the only input that would pin the loop on its own cannot be built. What
the finding leaves behind is narrower and still true — `van der Maas particle
surname` tests the outcome, not the mechanism, and reads like it tests both.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent
EXTRACT = SRC / "citation_extract.py"
SUITE = SRC / "test_citation_extract.py"

# (label, old, new, the control that should go red)
MUTATIONS = [
    ("year envelope opens a century early",
     r'YEAR = r"(?:1[5-9]|20)\d{2}',
     r'YEAR = r"(?:1[4-9]|20)\d{2}',
     "1499 is invisible"),

    ("all-caps surnames are accepted as authors",
     "    return len(letters) >= 2 and all(c.isupper() for c in letters)",
     "    return False",
     "OECD (2024) is all_caps_surname"),

    ("the stop list is empty, so In and See become surnames",
     "STOP = {",
     "STOP = set() or {",  # keeps the literal, drops nothing — see below
     "(intentionally inert, replaced below)"),

    ("particles are dropped from the key",
     "    while i < len(toks) and bare(toks[i]).lower() in PARTICLES \\",
     "    while False and bare(toks[i]).lower() in PARTICLES \\",
     "a lower-case core after a particle is a surname"),

    ("the author phrase is cut at the first comma",
     "    am = re.match(rf\"\\A{AUTHORS_PAREN}\", rest, re.U)",
     "    am = None",
     "comma-separated authors are not cut at the first comma"),

    ("particles are matched case-sensitively again",
     'PARTICLE = "(?i:" + "|".join(PARTICLES) + ")"',
     'PARTICLE = "|".join(PARTICLES)',
     "the same particle surname, sentence-initial"),

    ("the unmarked-up References label is not recognised",
     "        ref = _unmarked_reference_label(text)",
     "        ref = None",
     "the plain-text label was found but the section below it did not"),

    ("the entry-count confirmation is removed",
     "        if len(surnames) < MIN_ENTRIES:",
     "        if False:",
     "too few entries below it was accepted as a boundary"),

    ("the ordering confirmation is removed",
     "        if ascending / max(1, len(surnames) - 1) < MIN_ASCENDING:",
     "        if False:",
     "a reverse-alphabetical run was accepted"),

    ("the author-date style guard never fires",
     "    if total >= STYLE_MIN_SAMPLE and share > STYLE_COMMA_LESS_MAX:",
     "    if False:",
     "a wholly comma-less author-date document was accepted"),

    ("the style guard has no sample floor",
     "STYLE_MIN_SAMPLE = 10",
     "STYLE_MIN_SAMPLE = 0",
     "two comma-less parentheticals aborted 2"),

    ("the possessive is carried into the identity again",
     '                out.extend(extra)\n\n    return POSSESSIVE.sub("", " ".join(out))',
     '                out.extend(extra)\n\n    return " ".join(out)',
     "a possessive surname keys to the bare name"),

    ("rc3 B1: the six-token cap comes back",
     "    while True:\n        j = i",
     "    while len(toks) < 6:\n        j = i",
     "a seven-token author list is reached in full"),

    ("rc3 B2: a lower-case core after a particle is refused again",
     'CORE_AFTER_PARTICLE = r"[A-Za-zÀ-þ][\\w\'’\\-]+"',
     "CORE_AFTER_PARTICLE = CORE",
     "a lower-case core after a particle is a surname"),

    ("rc3 B7: `and colleagues` is not equivalent to et al.",
     'ET_AL = rf"(?:et{WS}al\\.[\'’]?s?|and{WS}colleagues[\'’]?s?)"',
     'ET_AL = rf"(?:et{WS}al\\.[\'’]?s?)"',
     "Jost and colleagues, narrative"),

    ("rc3 B8: the possessive gap is not reachable",
     "            gap = _possessive_gap(body, k, sent_start)",
     "            gap = None",
     "three intervening tokens, the measured maximum"),

    ("rc3 B8: the gap has no bound",
     "\nMAX_POSSESSIVE_YEAR_GAP_TOKENS = 3\n",
     "\nMAX_POSSESSIVE_YEAR_GAP_TOKENS = 9\n",
     "four intervening tokens is too many"),

    ("rc3 B5: the lead-in cue set is empty",
     'LEAD_IN_CUES = (\n    "for a recent review"',
     'LEAD_IN_CUES = (\n    "zzz-not-a-cue"  # "for a recent review"',
     "cue 'for a recent review'"),

    # ------------------------------------------------ rc3 §A, output contract
    #
    # A1 gives a candidate three terminal states and A5 makes the denominator
    # normative, so these mutations are aimed at the accounting rather than the
    # grammar. The failure they model is the one rc3 A1 opens with: a mathpix
    # image URL and a genuinely missed citation being byte-identical in the
    # record. Each mutation puts that back a different way.

    ("rc3 B10: nothing is ever excluded",
     "        reason = classify_exclusion(body, c1s, c1e, heads, maths)",
     "        reason = None",
     "a mathpix image URL should be excluded as url_or_image"),

    ("rc3 B10: the URL test is containment, not anchored",
     'if re.match(r"\\s*(?:https?://|www\\.\\w)", inner, re.I):',
     'if re.search(r"(?:https?://|www\\.\\w)", inner, re.I):',
     "a group that merely CONTAINS a URL was excluded"),

    ("rc3 §E: the structural front-matter test is gone",
     '    if level == "none":\n        return "publisher_metadata"',
     '    if False:\n        return "publisher_metadata"',
     "above the first h2 should be excluded_candidate/publisher_metadata"),

    ("rc3 §E: the named sections are back in the envelope",
     "    if name.strip().lower() in ENVELOPE_OUT_NAMES:",
     "    if False and name.strip().lower() in ENVELOPE_OUT_NAMES:",
     "a candidate under `## Citation information` should be publisher_metadata"),

    ("rc3 B10: math exclusion is blanket, deleting D2's real citations",
     "    if span and not D2_YEAR_ONLY.match(body[span[0]:span[1]]):",
     "    if span:",
     "a year-only math span is D2's unwrap case and MUST NOT be excluded"),

    ("rc3 B10: math spans are never excluded, so the branch is vacuous",
     "    span = _in_math_span(maths, s, e)",
     "    span = None",
     "a math span that is not year-only should be math_expression"),

    ("rc3 A2: the reason set stops being closed",
     "    if reason not in EXCLUDED_REASONS:\n        raise AssertionError",
     "    if False:\n        raise AssertionError",
     "_excl accepted a reason outside rc3 A2's closed set"),

    ("rc3 A4: an excluded span is dropped instead of recorded",
     "    excl.append(rec)",
     "    return  # excl.append(rec)",
     "an excluded span left no record"),

    ("rc3 A5: the denominator counts the excluded candidates again",
     "    n_parsed, n_unres, n_excl = len(cits), len(unres), len(excl)\n"
     "    denom = n_parsed + n_unres",
     "    n_parsed, n_unres, n_excl = len(cits), len(unres), len(excl)\n"
     "    denom = n_parsed + n_unres + n_excl",
     "A5: extraction_denominator must be parsed + unresolved"),

    ("rc3 A5: the summary calls its parse rate an accuracy",
     '                  "candidate_parse_rate": (round(n_parsed / denom, 4)',
     '                  "extraction_accuracy": (round(n_parsed / denom, 4)',
     "A5 forbids the summary reporting accuracy, precision or recall"),

    # ------------------------------------- rc2 §7.4 / rc3 B1b, non-person
    #
    # The institutional path is the one rc3 forbids inventing, so its controls
    # are the ones most worth probing: a second organisational grammar that
    # disagreed with rc2's would be invisible in a green suite.

    ("rc2 §7.4: the no-comma rule is dropped, so person lists become orgs",
     '    if "," in head:\n        return None',
     "    if False:\n        return None",
     "rc2 §7.4: no comma, at least one letter, non-empty"),

    ("rc2 §7.4: the head never drops its trailing period",
     "            head = head[:-1]",
     "            pass",
     "rc2 §7.4: the head stops at the year paren, one period removed"),

    ("rc2 §7.4: the reference side never takes the non-person path",
     "            label = non_person_head(head)",
     "            label = None",
     "rc2 §7.4: an institutional reference entry is keyed, not refused"),

    ("rc2 §8: syntax confers identity, with no bibliography evidence",
     '    if not all(f"non_person|{label}|{norm_year(y)}" in non_person_keys\n'
     "               for y in years):\n        return False",
     "    if False:\n        return False",
     "rc2 §8: with no reference entry, the institution stays unresolved"),

    ("rc3 §G: the non-person key degrades to its last token",
     '    key = f"non_person|{surname}|{y}" if author_kind == "non_person" \\\n'
     '        else f"{surname}|{y}"',
     '    key = f"non_person|{surname.split()[-1]}|{y}" '
     'if author_kind == "non_person" \\\n        else f"{surname}|{y}"',
     "§G: World Bank (2024) keys the whole label, never bank|2024"),

    # A second narrative site was probed here and the probe killed it. It
    # could not be reached by any control, fired zero times across the corpus,
    # and was removed from the extractor rather than left as a branch nothing
    # tests. The probe earning a deletion is the point of it.

    # ------------------------- rc2 §6.7 / §9.3, author-structure coherence
    #
    # Two of these model defects that were actually present and found by
    # running the check rather than reading the spec: the trailing period that
    # is an initial, and the `and` separator gluing onto a surname. Both
    # produced silently wrong output, and one of them produced a confident
    # wrong mismatch, which is the failure rc2 says is worse than no check.

    ("rc2 §9.3: the structure check never runs",
     "        if ref is None or not vis or c.get(\"author_kind\") != \"person\":\n"
     "            continue",
     "        if True:\n            continue",
     "§9.3: exact fails on count"),

    # The defect this modelled was real until 23 September: `visible_authors`
    # read `author_phrase`, which §6.3 guarantees is the phrase that did NOT
    # match the grammar whenever reduction happened. Four corpus mismatches,
    # one `exact` and so exit-1 forcing, every one of them against a reference
    # the citation agreed with.
    ("rc2 §6.7: visible_authors is read from the phrase that did not parse",
     "person_form(stop_reduced_phrase or author_phrase)",
     "person_form(author_phrase)",
     "§6.7 exact: visible_authors comes from the phrase that matched"),

    # Paired with it, the opposite error: always reducing would drop a leading
    # surname that never was a lead-in. Nothing in the corpus distinguishes
    # these two, so the negative is here rather than left to a measurement.
    ("rc2 §6.6: reduction rewrites the surface phrase as well",
     '        "author_phrase": re.sub(r"\\s+", " ", author_phrase).strip(),',
     '        "author_phrase": re.sub(r"\\s+", " ", '
     'stop_reduced_phrase or author_phrase).strip(),',
     "C-020: author_phrase is still the complete run"),

    ("rc2 §9.3: et al. is compared as a count, not a minimum",
     "            count_ok = rn >= ET_AL_MIN_AUTHORS",
     "            count_ok = rn == len(vis)",
     "§9.3: et_al passes against three authors"),

    ("rc2 §9.3: order is never checked",
     "        order_ok = all(i < len(ra) and ra[i] == v for i, v in enumerate(vis))",
     "        order_ok = True",
     "§9.3: exact fails on order"),

    ("rc2 §9.3: order wins over count when both fail",
     '            "failed": "count" if not count_ok else "order",',
     '            "failed": "order" if not order_ok else "count",',
     "§9.3: exact fails on count — got ['order']"),

    ("rc2 §1.1: ET_AL_MIN_AUTHORS is chosen by the implementation",
     "\nET_AL_MIN_AUTHORS = 3\n",
     "\nET_AL_MIN_AUTHORS = 2\n",
     "§9.3: et_al fails below ET_AL_MIN_AUTHORS"),

    ("rc2 §7.4: the trailing period is stripped even from an initial",
     '        if head.endswith(".") and not re.search(r"(?:^|[ \\-])[A-ZÀ-Þ]\\.$", head):',
     '        if head.endswith("."):',
     "rc2 §7.4: a trailing period that IS an initial must survive"),

    ("rc2 §7.4: the `and` separator glues onto the next surname",
     r'    r"\A\s*(?:,\s*&\s*|,\s*and\s+|,\s*|\s*&\s*|\s+and\s+)", re.I)',
     r'    r"\A\s*(?:,\s*(?:&|and)\s*|,\s*|\s*&\s*|\s+and\s+)", re.I)',
     "the `and` separator consumed the start of a surname"),

    ("rc2 §6.8: the possessive is compared against the bare surname",
     "        visible.append(POSSESSIVE.sub(\n"
     '            "", re.sub(r"\\s+", " ", m.group(0)).strip()).lower())',
     '        visible.append(re.sub(r"\\s+", " ", m.group(0)).strip().lower())',
     "§6.8: the possessive is stripped before comparison"),

    ("rc2 §7.4: a reference list is guessed rather than refused",
     "        m = PERSON_LIST_UNIT.match(head, pos)\n        if not m:\n"
     "            return None",
     "        m = PERSON_LIST_UNIT.match(head, pos)\n        if not m:\n"
     "            break",
     "a list that parses partway must yield nothing, not a partial list"),

    ("Alex Zamurko: a mismatched occurrence still counts as matched",
     "    uniquely_matched = [c for c in matched\n"
     '                        if c["citation_key"] not in mismatched_keys]',
     "    uniquely_matched = list(matched)",
     "an author_structure_mismatch occurrence must not count as matched"),

    # --------------------------------------------------- rc3 B6 and D2

    ("rc3 B6: the compact suffix list is out of the grammar again",
     'YEAR = r"(?:1[5-9]|20)\\d{2}(?:[a-z](?:,[a-z])*)?|n\\.d\\."',
     'YEAR = r"(?:1[5-9]|20)\\d{2}[a-z]?|n\\.d\\."',
     "B6: 2019a,b expands to two occurrences"),

    ("rc3 B6: the compact list matches but never expands",
     "    m = COMPACT_YEAR.match(tok)\n    if not m:\n        return [norm_year(tok)]",
     "    m = None\n    if not m:\n        return [norm_year(tok)]",
     "B6: 2019a,b expands to two occurrences"),

    ("rc3 B6: a bare year may take a suffix, so 2020,21 expands",
     r'COMPACT_YEAR = re.compile(r"\A((?:1[5-9]|20)\d{2})([a-z])((?:,[a-z])+)\Z")',
     r'COMPACT_YEAR = re.compile(r"\A((?:1[5-9]|20)\d{2})([a-z]?)((?:,[a-z])+)\Z")',
     "B6: a base year with no suffix of its own is not a compact list"),

    ("rc3 D2: the author-context restriction is dropped",
     "        if not D2_AUTHOR_LEFT.search(before):\n            return m.group(0)",
     "        if False:\n            return m.group(0)",
     "D2 negative — no preceding author"),

    ("rc3 D2: nothing is ever unwrapped",
     "    return D2_MATH_YEARS.sub(repl, text)",
     "    return text",
     "D2: a year-only math span with an author before it is unwrapped"),

    # ------------------------------------------------ rc3 §C, citation errors

    ("rc3 §C1: one record per DEFECT instead of per group",
     '        if defects:\n            lv, nm, _, _ = section_stack_at(heads, c1s)',
     '        for defects in [[d] for d in defects]:\n            lv, nm, _, _ = section_stack_at(heads, c1s)',
     "§C1: ONE record per parenthetical group"),

    ("rc3 §C: the comma-before-et-al shape is not a defect",
     '    r"\\bet[ \\t]+al(?![.\\w])|\\bat[ \\t]+al\\.|,[ \\t]*et[ \\t]+al\\.", re.I)',
     '    r"\\bet[ \\t]+al(?![.\\w])|\\bat[ \\t]+al\\.", re.I)',
     "§C1: the Gualandris group carries two defects"),

    ("rc3 §C2: the locator separator is matched case-sensitively",
     r'ERR_LOCATOR_SEP = re.compile(r";[ \t]*(?:[Pp]{1,2}|[Pp]ara|[Cc]hap)\.[ \t]*\d")',
     r'ERR_LOCATOR_SEP = re.compile(r";[ \t]*(?:p{1,2}|para|chap)\.[ \t]*\d")',
     "§C2: the uppercase `P.` must be recognised"),

    ("rc3 §C: nothing is ever reported as a citation error",
     "    found = []\n    if ERR_ET_AL.search(group):",
     "    found = []\n    if False and ERR_ET_AL.search(group):",
     "§C1: the Gualandris group carries two defects"),

    ("rc3 §C: the STOP guard is dropped, so `(See 2020)` is a defect",
     '    if m and m.group(1).lower() not in STOP:',
     '    if m:',
     "§C: (See 2020) is not a citation error"),

    # ---------------------------- rc2 §8.2 / §8.3, identity — CIT-ARCH-01

    # Re-aimed 22 September. §8.2's state derivation moved into `_lookup` when
    # the second candidate arrived, and all three of these went stale at once.
    # Reported as broken probes rather than passes, which is the whole point of
    # this file checking itself.

    ("rc2 §8.2: every lookup reports a unique match",
     '                "unique" if len(idx) == 1 else "nonunique"), idx',
     '                "unique" if True else "nonunique"), idx',
     "§8.2: two references sharing a key is nonunique"),

    # Aimed at the branch selection, not at `_lookup`. Mutating `_lookup` makes
    # EVERY lookup non-no_match, which means both candidates match, which trips
    # §8.3's exit-6 abort — and an abort is a crash, not a control going red.
    # This file has now made that mistake three times; the rule is that a
    # mutation must leave the program runnable so a control can judge it.
    ("rc2 §8.2: a no-match reports as resolved anyway",
     '            cand, state, idx, res = (reduced_key or full_key), "no_match", [], \\\n                                    "not_resolved"',
     '            cand, state, idx, res = (reduced_key or full_key), "unique", [], \\\n                                    "full_phrase"',
     "§8.2: no keyed reference is no_match"),

    ("rc2 §8.2: reference indices are not sorted",
     '        idx = sorted(ref_index_by_key.get(key, []))',
     '        idx = list(reversed(ref_index_by_key.get(key, [])))',
     "§8.2: reference_indices are ascending"),

    ("rc2 §8.3: a nonunique match emits no ambiguous_citation",
     '        if state == "nonunique":\n            ambiguous_citations.append',
     '        if False:\n            ambiguous_citations.append',
     "§8.3: nonunique emits exactly one ambiguous_citation"),

    # Aimed at the DIAGNOSTIC rather than the citation record. Pointed at
    # `c["candidate_key"] = cand` it took _split_key down with a TypeError,
    # and a crash is not a control going red — the same distinction this file
    # had to learn about extraction_accuracy earlier tonight.
    ("CIT-ARCH-01: the diagnostic drops the candidate it must preserve",
     '                "candidate_key": cand_key,\n'
     '                "identity_authority": "candidate",',
     '                "candidate_key": None,\n'
     '                "identity_authority": "candidate",',
     "CIT-ARCH-01: the candidate is preserved in the diagnostic"),

    ("rc2 §11.2: the identity partition double-counts",
     '                      sum(1 for c in cits\n                          if c["identity_class"] == "identity_not_resolved")),',
     '                      sum(1 for c in cits\n                          if True)),',
     "§11.2: the identity classes must partition"),

    # ------------------------------- rc2 §9.4, candidate-level diagnostics

    ("rc2 §9.4: the CORE length floor is removed",
     "            and len(cand_phrase) >= 4",
     "            and len(cand_phrase) >= 0",
     "§9.4: a candidate CORE shorter than 4 code points"),

    ("rc2 §9.4: a pair need not share author kind",
     "    if cand_kind != ref_kind:\n        return None",
     "    if False:\n        return None",
     "§9.4: a pair must share author kind"),

    ("rc2 §9.4: a paired reference stays in the pool",
     "            pool.pop(pi)",
     "            pass",
     "§9.4: a paired reference is removed from the pool"),

    ("CIT-ARCH-01: missing_reference establishes identity",
     '                "identity_authority": "candidate",\n'
     '                "example": occs[0].get("citation_group"),',
     '                "identity_authority": "authoritative",\n'
     '                "example": occs[0].get("citation_group"),',
     "identity_authority is the literal 'candidate'"),

    ("CIT-ARCH-01: possible_mismatch establishes identity",
     '                "identity_authority": "candidate",\n'
     '                "reference_index": ri,',
     '                "identity_authority": "authoritative",\n'
     '                "reference_index": ri,',
     "identity_authority is the literal 'candidate' on possible_mismatch"),

    ("rc2 §9.5: merge_suspected is set globally",
     "            merge = any(",
     "            merge = True or any(",
     "§9.5: merge_suspected is targeted, not global"),

    ("rc2 §9.5: merge_suspected never fires",
     "            merge = any(",
     "            merge = False and any(",
     "§9.5: a candidate whose phrase and year sit inside"),

    ("rc2 §9.4: nothing is ever paired",
     "            rule = repair_rule(kind, phrase, year, rk, rp, ry)",
     "            rule = None",
     "§9.4 surname_edit_distance_1: expected one possible_mismatch"),

    ("--fix all quietly drops one fix",
     '        fixes = (fixes - {"all"}) | set(FIXES)',
     '        fixes = (fixes - {"all"}) | (set(FIXES) - {"mathyear"})',
     "--fix all applied"),

    # ------------------------------- rc2 §6.3 / §8.1 / §8.4, the second
    # candidate. Unreachable before 22 September; these are its first probes.

    ("rc2 §6.3: reduction goes back to destroying the source phrase",
     "    reduced = authors if full_start != span_start else None",
     "    reduced = None\n    authors = authors",
     "§6.3: both phrases survive reduction"),

    ("rc2 §6.3: the reduced phrase is set even when nothing was removed",
     "    reduced = authors if full_start != span_start else None",
     "    reduced = authors",
     "§6.3: no reduction means no reduced phrase"),

    ("C-020: author_phrase is rewritten by the reduction after all",
     '"narrative", sent, heads, cits, author_phrase=full_phrase,',
     '"narrative", sent, heads, cits, author_phrase=authors,',
     "C-020: the source surface is not rewritten"),

    ("rc2 §8.3: the stop-reduced candidate is never looked up",
     "        s_state, s_idx = _lookup(reduced_key)",
     "        s_state, s_idx = _lookup(None)",
     "§8.3 row 4: F=no_match, S=unique is stop_reduced"),

    ("rc2 §8.3: a stop_reduced result is labelled full_phrase",
     '            cand, state, idx, res = reduced_key, s_state, s_idx, "stop_reduced"',
     '            cand, state, idx, res = reduced_key, s_state, s_idx, "full_phrase"',
     "§8.3 row 4: F=no_match, S=unique is stop_reduced"),

    ("rc2 §8.4: two candidates no longer suppress the diagnostic",
     '        and not c.get("stop_reduced_phrase")]',
     "                       ]",
     "§8.4: two candidates suppress candidate-level diagnostics"),

    # ------------------------------- rc2 §6.6, the surface grouping key

    ("rc2 §6.6: the surface key is a quoted string, not an array",
     '    return [normalized_author_phrase(phrase), surface_year_component(year)]',
     '    return f"{normalized_author_phrase(phrase)}|{surface_year_component(year)}"',
     "C-022: the key serializes as a JSON array with an integer year"),

    ("rc2 §6.6: a bare year is emitted as a string",
     "    return int(year) if year.isdigit() else year",
     "    return year",
     "C-022: the key serializes as a JSON array with an integer year"),

    ("rc2 §6.6: surface normalization reaches for identity normalization",
     '    return re.sub(r"\\s+", " ", phrase).strip().lower()\n\n\ndef surface_year_component',
     '    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\\s+", " ", phrase).strip().lower())\n\n\ndef surface_year_component',
     "C-023: `and` and `&` remain surface-distinct"),

    # Counts OCCURRENCES rather than distinct groups, by making the set a
    # list. The previous form was `len(cits) and len({...})`, which returns
    # the same value whenever `cits` is non-empty and the same 0 when it is —
    # a mutation that could never change anything, reported as caught for
    # however long, off some other control. The probe surfaced it on
    # 22 September once the controls around it stopped failing for other
    # reasons.
    ("rc2 §11: distinct_surface_groups counts occurrences, not groups",
     '                  "distinct_surface_groups": len({\n                      json.dumps(c["citation_surface_group_key"],\n                                 separators=(",", ":"), ensure_ascii=False)\n                      for c in cits}),',
     '                  "distinct_surface_groups": len([\n                      json.dumps(c["citation_surface_group_key"],\n                                 separators=(",", ":"), ensure_ascii=False)\n                      for c in cits]),',
     "C-023: two occurrences of ONE surface is one group"),

    # ------------------------------- rc2 §12.3 / §7.4, key order and naming

    ("rc2 §12.3: the declared key order is not applied",
     "    order = KEY_ORDER.get(rec.get(\"type\"))",
     "    order = None",
     "§12.3: declared key order"),

    ("rc2 §12.3: two keys swap in the citation record",
     '        "author_phrase", "resolved_author_phrase", "author_resolution",',
     '        "resolved_author_phrase", "author_phrase", "author_resolution",',
     "§12.3: declared key order"),

    ("rc2 §7.4: the reference identity field keeps its old name",
     '            "identity_author_phrase": surname,',
     '            "surname": surname,',
     "§7.4: the reference's identity field is named"),

    # ------------------------------- rc2 §5 / §6, sentence-relative fields

    ("rc2 §5: sentence_index restarts at each paragraph",
     "    return [(s, e, ce_, i, out[i - 1][2] if i else None)\n            for i, (s, e, ce_) in enumerate(out)]",
     "    return [(s, e, ce_, 0, out[i - 1][2] if i else None)\n            for i, (s, e, ce_) in enumerate(out)]",
     "C-026: sentence_index is continuous across headings"),

    ("rc2 §5: previous_sentence_end points at the sentence's own end",
     "out[i - 1][2] if i else None)",
     "out[i][2] if i else None)",
     "C-027: previous_sentence_end is the PRIOR sentence"),

    ("rc2 §6: standalone ignores where the citation ends",
     '        "standalone": gs == s_start and ge == s_content_end,',
     '        "standalone": gs == s_start,',
     "C-028: standalone needs BOTH ends"),

    # ------------------------------- rc2 §12.4, §7.3, C-030

    ("rc2 §12.4: multi-year citations keep source order",
     "    cits.sort(key=lambda c: (",
     "    [].sort(key=lambda c: (",
     "C-070: two years in one segment order by year"),

    ("rc2 C-030: a no-year entry is a keyless reference again",
     '        if not ym:\n            unres.append({',
     '        if False:\n            unres.append({',
     "§7.3: suspect_reasons is closed at terminator"),

    ("rc2 §7.3: suspect_reasons gains a fourth member",
     '        if not ym:\n            reasons.append("no_year")',
     '        if True:\n            reasons.append("no_year")',
     "C-032: suspect_reasons are the closed three"),

    # ------------------------------- rc2 §13 / §12.1, bytes on disk

    ("rc2 §12.2: the two §9.4 diagnostics share one block again",
     "    for block in (cits,                 # 2",
     "    missing_refs = missing_refs + possible_mismatches\n    possible_mismatches = []\n    for block in (cits,                 # 2",
     "§12.2: block order"),

    # Duplicating a block makes it REOPEN, which the interleave branch
    # catches. The order branch needs a pure swap, so it gets its own.
    ("rc2 §12.2: author_structure_mismatch comes back to the top",
     "                  ambiguous_authors,    # 7",
     "                  mismatches, ambiguous_authors,    # 7",
     "§12.2: blocks never interleave"),

    ("rc2 §12.2: two blocks swap places",
     "                  missing_refs,         # 8\n                  uncited,              # 9",
     "                  uncited,              # 9\n                  missing_refs,         # 8",
     "§12.2: block order"),

    ("rc2 §12.1: the stream goes back through text-mode print()",
     '                   ensure_ascii=False).encode("utf-8") + b"\\n"',
     '                   ensure_ascii=False).encode("utf-8") + b"\\r\\n"',
     "§12.1: LF line ending only"),

    ("rc2 §12.1: non-ASCII is escaped rather than emitted raw",
     '        json.dumps(canonical_order(r), separators=(",", ":"),\n                   ensure_ascii=False)',
     '        json.dumps(canonical_order(r), separators=(",", ":"),\n                   ensure_ascii=True)',
     "§12.1: non-ASCII is emitted raw, not escaped"),

    ("rc2 §13: --out writes something other than the stdout bytes",
     "    sys.stdout.buffer.write(payload)",
     "    sys.stdout.buffer.write(payload + b'\\n')",
     "C-071: --out bytes differ from stdout bytes"),

    ("rc2 §13: the directory filename is not content-derived",
     '        target = target / f"{digest}.citations.jsonl"',
     '        target = target / "citations.jsonl"',
     "C-072: a directory target names the file"),

    ("rc2 §2: canonical_sha256 hashes the OUTPUT, not the manuscript",
     '              "canonical_sha256": hashlib.sha256(\n                  text.encode("utf-8")).hexdigest(),',
     '              "canonical_sha256": hashlib.sha256(\n                  body.encode("utf-8")).hexdigest(),',
     "§2: canonical_sha256 is over the normalised INPUT bytes"),

    ("rc2 §13: publication is not atomic — the target is written in place",
     "        os.replace(tmp, target)",
     "        target.write_bytes(payload)",
     "C-073: publication left scratch files behind"),

    ("rc2 §13: an abort leaves the previous artifact in place",
     "    if a.out:\n        try:\n            publish(Path(a.out), payload, digest)",
     "    if a.out and digest is not None:\n        try:\n            publish(Path(a.out), payload, digest)",
     "§13: an abort left the previous normal artifact in place"),

    # ------------------------------- rc2 §10 / §11.3, bibliography absent

    ("rc2 §10: a missing bibliography aborts again, as v3.3 did",
     '        return text, "", len(text), heads, "not_available"',
     '        raise Abort(3, "references section not found")',
     "§10: a manuscript with no bibliography is still READ"),

    ("rc2 §10: identity is evaluated anyway, so absence reads as no-match",
     '            c["author_resolution"] = "not_evaluated"',
     '            c["author_resolution"] = "not_resolved"',
     "C-066: author_resolution is not_evaluated, which is NOT not_resolved"),

    # Aimed at `refs = []`, not at the enumerate guard. Un-guarding the
    # enumerate alone changes nothing, because `refs` is already emptied
    # upstream — so the first version of this mutation was a no-op that the
    # probe reported as SURVIVED. Two dud mutations found in one run.
    # No mutation for §10's nine-type suppression. Every guard in that path
    # is REDUNDANT: with no bibliography there is no reference section, so
    # `assemble_references` returns nothing, every lookup is no_match, and not
    # one of the nine can be constructed whatever the guards say. Disabling
    # any of them changes no output, so a probe would report "caught" off some
    # other control and establish nothing.
    #
    # The guards are kept because they state the rule where a reader looks for
    # it, and because they would matter the day the absent path returns
    # something other than an empty section. But the control that passes is
    # passing structurally, and this file will not pretend otherwise.

    ("rc2 §11.3: not-evaluated quantities report 0 instead of null",
     "        return None if absent else value",
     "        return value",
     "C-067: not-evaluated quantities are null, never 0"),

    ("rc2 §10: the surface key is nulled along with the identity",
     '            c["citation_key"] = None\n            # C-066:',
     '            c["citation_key"] = None\n            c["citation_surface_group_key"] = None\n            # C-066:',
     "C-025: citation_surface_group_key stays COMPUTED"),

    # ------------------------------- rc2 §8.3 rows 6-9, §8.5, §8.6

    # §8.6's abort IS probeable, now that §15's seam exists. The note that
    # stood here said otherwise — that the branch was unreachable and a probe
    # for it would establish nothing. True of manuscripts, false of the spec:
    # the matrix marks these cases `injection`, and §15 supplies the seam.
    # Corrected 22 September, the same afternoon the wrong version was written.

    ("rc2 §8.6: double resolution no longer aborts",
     '            if full_key == reduced_key:\n                raise Abort(6, "same_candidate_identity_double_resolution")',
     '            if False:\n                raise Abort(6, "same_candidate_identity_double_resolution")',
     "§8.6: two non-empty lookups with the SAME candidate_key must abort"),

    ("rc2 §8.6: the guard fires on overlapping INDICES, not equal keys",
     "            if full_key == reduced_key:",
     "            if set(f_idx) & set(s_idx):",
     "C-047: a shared reference index across different candidate keys"),

    ("rc2 §15: the seam is ignored",
     "        if _RESOLVER_SEAM is not None:",
     "        if False:",
     "§8.3 rows 6-9 by injection:"),

    ("rc2 §8.3: an ambiguous occurrence keeps its citation_key",
     '            c["citation_key"] = None\n            # "Emit exactly one',
     '            # "Emit exactly one',
     "§8.3: an ambiguous occurrence establishes no citation_key"),

    # Aimed to DROP the record rather than duplicate it. The duplicate form
    # appended a bare `{}`, which §8.5's reservation loop then indexed — a
    # crash, not a control going red, and the probe refused it on those
    # grounds. Fourth time this file has had to relearn that distinction.
    ("rc2 §8.3: the ambiguity record is never emitted",
     '            ambiguous_authors.append({',
     '            [].append({',
     "§8.3: EXACTLY ONE ambiguous_author_resolution per occurrence"),

    # Retargeted 23 September: the record went flat, into rc2 §12.3's declared
    # key order, so the nested `candidates` array this probe reached into is
    # gone. Reported as "probe did not apply", which is the right answer and
    # the reason that state exists — a probe that silently mutated nothing
    # would have read as a pass.
    ("rc2 §8.5: ambiguity reserves nothing",
     "    for a in ambiguous_authors:",
     "    for a in []:",
     "§8.5: reserved indices must not emit uncited_reference"),

    ("rc2 §8.5: reserved indices stay in the pool",
     "            and i not in reserved]",
     "            and True]",
     "§8.5: reserved indices must not emit uncited_reference"),

    # ------------------------------- rc2 §9.6, the residual

    ("rc2 §9.6: nothing is ever reported uncited",
     '    uncited = [{"type": "uncited_reference", "index": i,',
     '    uncited = [{"type": "uncited_reference_OFF", "index": i,',
     "§9.6: every remaining keyed reference is uncited"),

    ("rc2 §9.6: the unique-key filter is removed, so duplicates qualify",
     "    unique_keys = {k for k, idx in ref_index_by_key.items() if len(idx) == 1}",
     "    unique_keys = {k for k, idx in ref_index_by_key.items() if len(idx) >= 1}",
     "§9.6: a duplicated key is not a UNIQUE keyed reference"),

    ("rc2 §9.6: exactly matched references stay in the residual",
     "            and r[\"reference_key\"] not in authoritative\n",
     "            and r[\"reference_key\"] not in set()\n",
     "§9.6: an exactly matched reference is not uncited"),

    ("rc3 B1b: the parenthetical detection site is closed again",
     "        inner = body[c1s + 1:c1e - 1]\n        cut = YEAR_RE.search(inner)",
     "        inner = body[c1s + 1:c1e - 1]\n        cut = None",
     "§G: (International Monetary Fund, 2022) keys the complete label"),

    # rc2 §2. The state this file was in until 22 September: coordinates
    # emitted as code-point indices. It passed every control in the suite,
    # and on the corpus 95.3% of offsets pointed at unrelated text.
    ("rc2 §2: coordinates go back to being code-point indices",
     "    to_byte_coordinates(lines, text)\n",
     "    pass  # to_byte_coordinates(lines, text)\n",
     "spans do not slice their own text out of the manuscript bytes"),

    # The subtler shape, and the one worth probing separately: an
    # implementation that converts only SOME fields. `group_start` and
    # `group_end` are the obvious pair; `segment_start` is the one a partial
    # patch forgets, and every count and sort still comes out identical.
    ("rc2 §2: segment coordinates are left unconverted",
     'OFFSET_FIELDS = frozenset({\n'
     '    "group_start", "group_end", "segment_start", "segment_end",',
     'OFFSET_FIELDS = frozenset({\n'
     '    "group_start", "group_end",',
     "spans do not slice their own text out of the manuscript bytes"),

    # rc3 D1. The transforms go back after canonicalisation, which is where
    # they were. Under `--fix all` every offset past the first substitution
    # shifts, and nothing errors.
    ("rc3 D1: the ampersand substitution moves back after canonicalisation",
     '    if "ampersand" in fixes:\n        text = text.replace("\\\\&", "&")\n',
     "",
     "The substitution is running after canonicalisation"),

    # And the half-move: `ampersand` ahead of the hash but `mathyear` left
    # behind. Passes the D1 control above and must fail the §J one.
    ("rc3 §J: mathyear alone is left after canonicalisation",
     '    if "mathyear" in fixes:\n        # rc3 §J pins the order',
     '    if False:\n        # rc3 §J pins the order',
     "with both byte-changing fixes on"),

    # rc2 §2 binds canonical_sha256 to the bytes the offsets index. Hashing
    # before the transform breaks that binding and nothing downstream notices,
    # because the digest is only ever compared to itself.
    ("rc2 §2: canonical_sha256 is taken before the ingest transform",
     '              "canonical_sha256": hashlib.sha256(\n'
     '                  text.encode("utf-8")).hexdigest(),',
     '              "canonical_sha256": hashlib.sha256(\n'
     '                  normalise(path.read_bytes()).encode("utf-8")).hexdigest(),',
     "canonical_sha256 is unchanged by a byte-changing fix"),

    # The other half of the same control, and it needs its own mutation or the
    # binding branch is unreachable. Hashing the BODY moves with the fixes, so
    # it passes the movement test above, and is still not the manuscript the
    # coordinates index — the reference section is missing from it.
    ("rc2 §2: canonical_sha256 covers the body instead of the manuscript",
     '              "canonical_sha256": hashlib.sha256(\n'
     '                  text.encode("utf-8")).hexdigest(),',
     '              "canonical_sha256": hashlib.sha256(\n'
     '                  body.encode("utf-8")).hexdigest(),',
     "canonical_sha256 is not the digest of the bytes the offsets index"),

    # The strictness of the guard, not the conversion. Skipping an
    # unconvertible coordinate leaves a code-point value in a byte field with
    # nothing to distinguish it — the exact silent-wrongness this change
    # exists to remove.
    # rc2 §11. The state this file was in until 23 September: nine of rc2's
    # twenty-one summary fields. Every one of §11.1 and §11.2's invariants was
    # unevaluable, and the conformance map could only say PARTIAL.
    ("rc2 §11: the twelve added summary fields go away again",
     '                  "bibliography_reconciliation_performed": not absent,',
     "",
     "rc2 declares summary fields this file does not emit"),

    # §12.3 for the summary. Removing its KEY_ORDER row leaves insertion
    # order, which is v3.3's order and passes every arithmetic check above.
    ("rc2 §12.3: the summary's declared key order is dropped",
     '    "summary": [\n        "type", "identity_resolution_performed",',
     '    "_summary_disabled": [\n        "type", "identity_resolution_performed",',
     "§12.3: declared key order"),

    # §11.4's authority distinction, and the defect this actually was. Counting
    # every non-null key instead of every authoritative one is silent: the
    # number is plausible, it is larger than the truth by exactly the citations
    # with no reference behind them, and only §11.2's partition catches it.
    ("rc2 §11.4: resolved counts any key, not an authoritative one",
     '    resolved_occ = sum(1 for c in cits if c["citation_key"] in ref_index_by_key)',
     '    resolved_occ = sum(1 for c in cits if c["citation_key"] is not None)',
     "a key with no bibliography entry behind it is not resolved"),

    # The same error one field over. `distinct_works_cited` has no invariant
    # over it in rc2, so nothing but its own control can catch this.
    ("rc2 §11.4: works cited counts syntax-derived keys",
     '                      c["citation_key"] for c in cits\n'
     '                      if c["citation_key"] in ref_index_by_key})),',
     '                      c["citation_key"] for c in cits\n'
     '                      if c["citation_key"] is not None})),',
     "a key with no reference is not a work cited"),

    # §11.2's subset bound. Counting diagnostic RECORDS rather than the
    # occurrences they represent undercounts whenever one candidate key covers
    # several occurrences — the opposite direction from double-counting, and
    # equally invisible.
    ("rc2 §11.4: the diagnostics count records, not occurrences",
     '    ref_missing_occ = sum(d["occurrences"] for d in missing_refs)\n'
     '    mismatch_occ = sum(d["occurrences"] for d in possible_mismatches)',
     "    ref_missing_occ = len(missing_refs) * 9\n"
     "    mismatch_occ = len(possible_mismatches)",
     "the diagnostics count occurrences twice"),

    # §11.1. The extraction invariant is the one rc2 marks "always", so it has
    # to hold in bibliography-absent mode too.
    ("rc2 §11.1: total stops counting the unresolved occurrences",
     '                  "total_citation_occurrences": denom,',
     '                  "total_citation_occurrences": n_parsed,',
     "total must equal extracted + unresolved"),

    # rc2 §14's reason table, C-077. The defect this golden found the moment
    # it existed: exit 2 emitted rc2's string plus a diagnostic tail, and the
    # two exit-2 sites disagreed with each other.
    ("rc2 §14: the style guard's reason grows a tail again",
     '        raise Abort(2, "unsupported citation style",\n'
     '                    f"{share:.0%} of {total} author-year parentheticals omit "',
     '        raise Abort(2, f"unsupported citation style: {share:.0%} of "\n'
     '                    f"XX{total} author-year parentheticals omit "',
     "the abort stream does not match rc2's declared bytes"),

    # §12.1's byte properties reach the error stream too. `print` would
    # translate LF to CRLF on Windows, which is how the normal stream was
    # broken until 22 September.
    ("rc2 §12.1: the error stream goes through the text layer",
     "    sys.stdout.buffer.write(payload)\n    sys.stdout.buffer.flush()",
     "    print(payload.decode(), end='')",
     "the abort stream does not match rc2's declared bytes"),

    # §13: for exits 2-5 the requested file IS the error artifact.
    # Surgical: only the ABORT path stops publishing. Widening it to every
    # run made C-071 and C-072 fail first, which told us the mutation broke
    # something rather than which rule it broke.
    ("rc2 §13: an abort writes no artifact to --out",
     "        if ab.detail:\n"
     "            print(f\"{ab.reason}: {ab.detail}\", file=sys.stderr)",
     "        if ab.detail:\n"
     "            print(f\"{ab.reason}: {ab.detail}\", file=sys.stderr)\n"
     "        a.out = None",
     "the error stream is written to the requested file"),

    # rc2 §1.1, adopted 23 September. `meta` said v3.3 while every rule the
    # extractor runs is rc2's or rc3's, so the label was wrong rather than
    # undecided.
    ("rc2 §1.1: meta declares v3.3 again",
     'SPEC_VERSION = "3.4"',
     'SPEC_VERSION = "3.3"',
     "rule identity must match rc2's pinned constants"),

    ("rc2 §1.1: the profile drifts from the rule version it belongs to",
     'CITATION_PROFILE = "apa7_like_v1"',
     'CITATION_PROFILE = "apa7"',
     "rule identity must match rc2's pinned constants"),

    # §12.3's declared meta. Dropping `mode` leaves the other seven in order,
    # so only the declared-FIELDS half of the §12.3 control can see it.
    ("rc2 §12.3: meta stops naming its execution mode",
     '              "mode": MODE,\n',
     "",
     "rc2 declares fields this file does not emit"),

    # §14's error stream has its own two-field meta, and the second field is
    # the ruleset that refused the document.
    ("rc2 §14: the error stream's meta loses its rule version",
     '            {"type": "meta", "spec_version": SPEC_VERSION,\n'
     '             "citation_rule_version": CITATION_RULE_VERSION},',
     '            {"type": "meta", "spec_version": SPEC_VERSION},',
     "the error stream's meta is exactly type, spec_version"),

    # C-031, generalised: every closed value enum rc2 declares. The sweep found
    # zero violations, so these mutations check the guard rather than a defect —
    # each puts a value outside the set rc2 closes.
    ("rc2 §7: an unresolved_reference gains a fourth reason",
     '                          "reason": "orphan_line"})',
     '                          "reason": "orphan_line_v2"})',
     "values emitted outside a set rc2 closes"),

    ("rc2 §9.3: `failed` gains a third value",
     '            "failed": "count" if not count_ok else "order",',
     '            "failed": "count" if not count_ok else "order_or_count",',
     "values emitted outside a set rc2 closes"),

    # The other direction, and the one that matters more: a declared value
    # stops being reachable. That is the shape §3.1 and §3.2 both had.
    ("rc2 §9.4: year_transposition can no longer fire",
     "        if _year_transposed(cand_year, ref_year):",
     "        if False:",
     "declared values were never reached"),

    # rc2 §3.1, C-016/017. Six of eleven members until 23 September, and
    # unlike §3.2's gap this one was NOT latent: two corpus groups parsed while
    # silently dropping the citation behind the prefix.
    ("rc2 §3.1: the five multiword PREFIX forms go missing again",
     '               "for example, see", "for instance, see",\n'
     '               "for a similar approach, see", "for discussion, see",\n'
     '               "for a review, see")',
     "               )",
     "the PREFIX set must equal rc2's closed list"),

    # C-016 asks for one case per prefix, and the cue must not leak into
    # author_phrase. Dropping the cue group entirely leaves every member
    # unparseable, which the per-cue control catches and the set-equality one
    # does not.
    ("rc2 §3.1/C-016: the cue is no longer stripped before the authors",
     '    prefix = "(?:" + "|".join(re.escape(c) for c in all_cues) + r")[,]?[ \\t\\n]+"',
     '    prefix = "(?:zzz-not-a-cue)[,]?[ \\t\\n]+"',
     "every closed PREFIX form must parse with the cue excluded"),

    # C-017's longest-first ordering. Sorting the cues shortest-first puts
    # `see` ahead of `see also` and every multiword form ending in `see`.
    ("rc2 §3.1/C-017: cues are offered shortest first",
     "    all_cues = tuple(sorted(set(cues) | set(LEAD_IN_CUES),\n"
     "                            key=lambda c: (-len(c), c)))",
     "    all_cues = tuple(sorted(set(cues) | set(LEAD_IN_CUES),\n"
     "                            key=lambda c: (len(c), c)))",
     "a longer form must be offered before the shorter one it contains"),

    # rc2 §3.2, C-018. The state this file was in until 23 September: five of
    # rc2's 109 STOP tokens missing, zero corpus occurrences of any of them, so
    # nothing but an exhaustive check over the closed set could see it.
    ("rc2 §3.2: rc2's last STOP line goes missing again",
     '    "panel", "column", "row", "appendix", "exhibit",',
     "",
     "the STOP set must equal rc2's closed list"),

    # The two behaviours a STOP token has, each broken on its own. Removing a
    # token from the middle of the set is the same defect as the five, and the
    # set-equality control catches it — so these aim at the RULES instead.
    ("rc2 §6: a STOP first CORE is no longer rejected",
     '    if core.lower() in STOP:',
     "    if False:",
     "STOP token leading a candidate must never become a citation"),

    # rc2 §9.1, implemented 23 September. The groups were computed and never
    # emitted — five across four papers, zero records.
    ("rc2 §9.1: duplicate groups are computed and not emitted again",
     '        for k, idx in ref_index_by_key.items() if len(idx) >= 2]',
     "        for k, idx in ref_index_by_key.items() if len(idx) >= 3]",
     "one record per key holding two or more entries"),

    # `cited` hardcoded true passes on the whole corpus: all five real groups
    # ARE cited. Only the fixture with an uncited duplicate can catch it.
    ("rc2 §9.1: cited is always true",
     '         "cited": k in cited_keys}',
     '         "cited": True}',
     "a duplicate key no occurrence cites is cited=false"),

    # NO MUTATION for §9.1's `identity_class` restriction on `cited_keys`.
    # Written, probed, and removed on 23 September because it SURVIVED — and
    # survived for a reason worth keeping rather than a gap worth filling.
    #
    # §8.2 gives `identity_not_resolved` only to keys matching zero references;
    # a duplicate key matches two or more; so the only class a duplicate key
    # can reach is `bibliography_key_ambiguous`, which is inside the
    # restriction. Narrow and wide `cited_keys` are equal for duplicate keys.
    # Measured: all 17 corpus citations carrying a duplicate key are that
    # class, and zero candidate-level keys are duplicate keys.
    #
    # The restriction stays in the implementation because rc2 states the rule
    # rather than the coincidence. It gets no mutation here because a mutation
    # nothing can catch would sit in this file reading as an untested rule,
    # which is the exact failure this file exists to find.

    # §12.4's order for the block.
    ("rc2 §12.4: the duplicate block loses its deterministic order",
     '    duplicates.sort(key=lambda d: (min(d["reference_indices"]),\n'
     '                                   d["reference_key"].encode("utf-8")))',
     "    duplicates.reverse()",
     "orders by smallest member reference_index, not by key"),

    # rc2 §14, C-078. The three conditions that do not coincide with "not every
    # citation uniquely matched", each removed on its own. All three are facts
    # about the bibliography, and the old proxy could not see any of them.
    ("rc2 §14: a reference nobody cited stops forcing exit 1",
     '    ("residual uncited_reference", lambda ls: _has(ls, "uncited_reference")),',
     "",
     "residual uncited_reference forces exit 1"),

    ("rc2 §14: a malformed bibliography entry stops forcing exit 1",
     '    ("unresolved_reference", lambda ls: _has(ls, "unresolved_reference")),',
     "",
     "named condition 'unresolved_reference'"),

    ("rc2 §14: a suspect reference stops forcing exit 1",
     '    ("any suspect reference",\n'
     '     lambda ls: any(r.get("type") == "reference" and r.get("suspect_reasons")\n'
     '                    for r in ls)),',
     "",
     "named condition 'any suspect reference'"),

    # §9.3's split. An `et_al` mismatch must NOT force exit 1 on its own, so
    # widening the predicate to every mismatch breaks the rule in the other
    # direction — and the control that catches it is the clean-document one,
    # because a widened condition makes exit 0 unreachable.
    ("rc2 §9.3: an et_al mismatch forces exit 1 too",
     '    ("exact author_structure_mismatch",\n'
     '     lambda ls: any(r.get("type") == "author_structure_mismatch"\n'
     '                    and r.get("citation_author_form") == "exact"\n'
     '                    for r in ls)),',
     '    ("exact author_structure_mismatch",\n'
     '     lambda ls: _has(ls, "author_structure_mismatch") or len(ls) > 0),',
     "a clean document must exit 0"),

    # The count itself. If rc2's twelve and this file's tuple drift apart, the
    # first control in the block says so — it reads rc2's list, not this one.
    ("rc2 §14: one finding condition is dropped from the closed set",
     '    ("ambiguous_citation", lambda ls: _has(ls, "ambiguous_citation")),',
     "",
     "finding conditions, this file evaluates"),

    # C-051 and rc2 §11.4. The state this file was in until 23 September: a key
    # held by two references counted as a unique match, so an occurrence that
    # was `bibliography_key_ambiguous` by every other field in the output was
    # `uniquely_matched` by this one. Worth 11 occurrences and 3 works on the
    # corpus, and invisible without a control that builds a duplicate key.
    ("rc2 §11.4: a key in the bibliography at all counts as uniquely matched",
     "    keyed_once = {k for k, n in counts.items() if n == 1}",
     "    keyed_once = {k for k, n in counts.items() if n >= 1}",
     "counts +0 toward uniquely matched, and the unambiguous"),

    # rc2 §12.3's declared FIELDS, as against their order. Twelve were absent
    # across five record types until 23 September and §12.3's control passed on
    # all of it: it filtered rc2's declared keys down to the ones the record
    # had, then checked those were in order. A field that was never emitted was
    # never compared.
    ("rc2 §12.3: identity_authority goes away again",
     '                "identity_authority": "candidate",\n'
     '                "example": occs[0].get("citation_group"),',
     '                "example": occs[0].get("citation_group"),',
     "rc2 declares fields this file does not emit"),

    ("rc2 §12.3: possible_mismatch calls its evidence `rule` again",
     '                "evidence": rule,',
     '                "rule": rule,',
     "rc2 declares fields this file does not emit"),

    ("rc2 §12.3: ambiguous_citation reverts to rc1's candidate_key",
     '                "citation_key": cand,\n'
     '                # rc2\'s declared shape:',
     '                "candidate_key": cand,\n'
     '                # rc2\'s declared shape:',
     "rc2 declares fields this file does not emit"),

    # §12.4 needs this one, not just §12.3: without `reference_index` two
    # mismatches on one citation can stay tied on every key the block is
    # ordered by, which §12.4 forbids in as many words.
    ("rc2 §12.3: the mismatch stops naming its reference",
     '            "reference_index": ri,\n'
     '            "citation_author_form": c["author_form"],',
     '            "citation_author_form": c["author_form"],',
     "rc2 declares fields this file does not emit"),

    # The rule those two records carry. rc2 replaces `citation_key: null,
    # author_kind: null` with the literal, so re-adding the nulls is the
    # regression to catch.
    ("rc2 §12.3: the candidate diagnostics carry null identity fields again",
     '                "merge_suspected": merge,\n            })',
     '                "merge_suspected": merge,\n'
     '                "citation_key": None, "author_kind": None,\n            })',
     "must not carry citation_key or author_kind at all"),

    # C-002. Dropping NFC leaves a decomposed `e` + U+0301 in the manuscript:
    # two code points where one is meant, so every coordinate after it is
    # one out and the canonical hash names a different document.
    ("rc2 §2/C-002: NFC normalisation is dropped",
     '    return unicodedata.normalize("NFC", s)',
     "    return s",
     "normalisation is not CRLF/CR→LF then NFC"),

    # C-004, the converse. Each of rc2 §1.3's three code-point counts is
    # switched to bytes; all three are silent, and each has its own control.
    ("rc2 §1.3/C-004: osa measures bytes instead of code points",
     "def _osa(a: str, b: str) -> int:",
     "def _osa(a: str, b: str) -> int:\n"
     "    a, b = a.encode('utf-8').decode('latin-1'), "
     "b.encode('utf-8').decode('latin-1')",
     "osa counts code points, not bytes"),

    ("rc2 §1.3/C-004: the overlong threshold counts bytes",
     "        if len(assembled) > 1500:",
     '        if len(assembled.encode("utf-8")) > 1500:',
     "the 1500 threshold is counting bytes"),

    ("rc2 §2: an out-of-range coordinate is skipped instead of aborting",
     "            if not isinstance(v, int) or not 0 <= v < len(table):",
     "            if not isinstance(v, int) or not 0 <= v < len(table):\n"
     "                continue\n            if False:",
     "an out-of-range coordinate was accepted"),

    # ---------------------------------------------------------------- C-005.
    # §4.2 is the contract every later section stands on, and all four of
    # these are silent: the document still parses, the bibliography boundary
    # just moves.
    ("rc2 §4.2/C-005: a hash run no longer needs whitespace after it",
     'HEAD_MD = re.compile(r"^(#{1,6})[ \\t]+(.*)$")',
     'HEAD_MD = re.compile(r"^(#{1,6})[ \\t]*(.*)$")',
     "a hash run needs a space or tab"),

    ("rc2 §4.2/C-005: the HTML heading no longer has to close its own level",
     'r"^[ \\t]*<h([1-6])(?:[ \\t][^>]*)?>(.*?)</h\\1>[ \\t]*$"',
     'r"^[ \\t]*<h([1-6])(?:[ \\t][^>]*)?>(.*?)</h[1-6]>[ \\t]*$"',
     "the HTML level must close itself"),

    ("rc2 §4.2/C-005: the h1 refusal needs three h1 headings, not two",
     "    if sum(1 for h in heads if h[1] == 1) >= 2 and \\",
     "    if sum(1 for h in heads if h[1] == 1) >= 3 and \\",
     "two h1 and no h2 is refused"),

    ("rc2 §4.2/C-005: closing hashes stay in the heading name",
     '            name = CLOSING_HASHES.sub("", m.group(2), count=1)',
     "            name = m.group(2)",
     "one trailing hash run comes off"),

    # ---------------------------------------------------------------- C-015.
    # Surgical on purpose. Removing `start`/`end` from OFFSET_FIELDS would take
    # a dozen controls red and prove nothing about which one was watching the
    # unresolved records; skipping exactly that record type leaves C-015 as the
    # only thing standing between this and a silent unit change.
    ("rc2 §6.4/C-015: unresolved candidates keep code point offsets",
     "    table = byte_offsets(text)\n    for rec in records:",
     "    table = byte_offsets(text)\n    for rec in records:\n"
     '        if rec.get("type") == "unresolved_citation":\n            continue',
     "the candidate begins at byte"),

    # `"reason": reason` on the end is what makes this the unresolved builder
    # rather than the excluded-candidate one four lines below it, which opens
    # with the same six keys.
    ("rc2 §6.4/C-015: the unresolved span stops one short of its own text",
     '        "text": body[start:end], "start": start, "end": end, '
     '"reason": reason,',
     '        "text": body[start:end - 1], "start": start, "end": end, '
     '"reason": reason,',
     "does not slice its own text"),

    # ---------------------------------------------------------------- C-029.
    ("rc2 §7.2/C-029: wrapped lines join on two spaces",
     '        assembled = " ".join(parts)',
     '        assembled = "  ".join(parts)',
     "the join is not one ASCII space per line"),

    ("rc2 §7.2/C-029: the entry span keeps the line's own indentation",
     "        span = (base + off, base + off + len(stripped))",
     "        span = (base + lstart, base + lend)",
     "starts or ends on horizontal whitespace"),

    # ---------------------------------------------------------------- C-080.
    # One conceptual change — numeric brackets enter the C1 envelope — and it
    # takes both halves of `c1_spans`, because square brackets carry a
    # reference NUMBER where the envelope asks for a year. An implementation
    # that widened only the delimiter would still find nothing, which is the
    # reason this mutation is a single substitution over both lines.
    # ---------------------------------------------------------------- C-048.
    # The two index arrays are swapped. §12.3's control sees key NAMES and
    # ORDER, so it stays green; only a byte golden notices that `full` names
    # the reduced candidate's reference and the reduced candidate names
    # `full`'s. That difference is the reason rc2 asks for a byte golden here
    # and the reason the old control, which asked only whether both candidates
    # were named, could not have caught the nested shape it was written
    # against.
    ("rc2 §12.3/C-048: the two reference-index arrays are swapped",
     '                "full_match_state": f_state,\n'
     '                "full_candidate_key": full_key,\n'
     '                "full_reference_indices": f_idx,\n'
     '                "stop_reduced_phrase": c.get("stop_reduced_phrase"),\n'
     '                "stop_reduced_match_state": s_state,\n'
     '                "stop_reduced_candidate_key": reduced_key,\n'
     '                "stop_reduced_reference_indices": s_idx,\n',
     '                "full_match_state": f_state,\n'
     '                "full_candidate_key": full_key,\n'
     '                "full_reference_indices": s_idx,\n'
     '                "stop_reduced_phrase": c.get("stop_reduced_phrase"),\n'
     '                "stop_reduced_match_state": s_state,\n'
     '                "stop_reduced_candidate_key": reduced_key,\n'
     '                "stop_reduced_reference_indices": f_idx,\n',
     "byte for byte"),

    # The §12.3 control read ONE fixture's output and skipped every declared
    # type that fixture did not emit — ten of fifteen. This mutation drops a
    # declared field from a record type that was in the missing five, so it
    # survives against the old control by construction.
    ("rc2 §12.3: ambiguous_author_resolution drops a declared field",
     '                "stop_reduced_phrase": c.get("stop_reduced_phrase"),\n',
     "",
     "rc2 declares fields this file does not emit"),

    # ------------------------------------------------------- §8.5, C-051's twin.
    # Restores the ordering defect exactly: the ambiguous occurrence's own
    # `citation_key` is null by §8.3, and falling back to the candidate key it
    # held BEFORE resolution is what building `matched` too early did.
    ("rc2 §8.5: an ambiguous occurrence is matched on its pre-resolution key",
     '    matched = [c for c in cits if c["citation_key"] in keyed_once]',
     '    matched = [c for c in cits\n'
     '               if (c["citation_key"] or c.get("candidate_key_stop_reduced"))\n'
     "               in keyed_once]",
     "counts +0 — got"),

    # ---------------------------------------------------------------- C-061.
    # Aimed at 2a, not 2b. A duplicate key is excluded from the pool
    # structurally — it is not in `unique_keys` — so removing the reservation
    # of `ambiguous_citations` changes nothing observable and a control built
    # on that fixture alone survives it. Author-resolution ambiguity is where
    # reservation is the only thing holding the rows out.
    ("rc2 §9.6: author-resolution ambiguity reserves only its full candidate",
     '        reserved.update(a["full_reference_indices"])\n'
     '        reserved.update(a["stop_reduced_reference_indices"])',
     '        reserved.update(a["full_reference_indices"])',
     "both reserved rows must leave the pool"),

    ("rc2 §9.6: a mismatch-paired reference stays in the pool",
     '            pool.pop(pi)                          # "remove from the pool"',
     '            pool.count(pi)                        # "remove from the pool"',
     "must leave the pool and nothing else with it"),

    ("rc2 C-080: numeric brackets enter the C1 envelope",
     '    for m in re.finditer(r"\\([^()]*\\)", body):\n'
     "        if YEAR_RE.search(m.group(0)):",
     '    for m in re.finditer(r"[(\\[][^()\\[\\]]*[)\\]]", body):\n'
     "        if YEAR_RE.search(m.group(0)) or "
     'm.group(0).startswith("["):',
     "overlaps a numeric bracket span"),
]

# The STOP mutation needs to empty the set rather than edit its opening line.
MUTATIONS[2] = (
    "the stop list is empty, so In and See become surnames",
    "    return bare.lower() in STOP or tok[-1:] in \",;:\"",
    "    return tok[-1:] in \",;:\"",
    "In Smith (2020) parses as smith|2020",
)


def run_suite(scripts_dir: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(scripts_dir / "test_citation_extract.py")],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    baseline_code, baseline_out = run_suite(SRC)
    if baseline_code != 0:
        print("the suite does not pass unmutated; fix that before probing it")
        print(baseline_out[-2000:])
        return 1
    print("baseline: the suite passes on the real implementation\n")

    survivors, broken = [], []

    for label, old, new, expected in MUTATIONS:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            shutil.copy(SUITE, d / "test_citation_extract.py")
            src = EXTRACT.read_text(encoding="utf-8")
            if old not in src:
                broken.append(f"{label}\n      target text not found: {old!r}")
                print(f"  [??] {label}  — probe did not apply")
                continue
            if src.count(old) > 1:
                broken.append(f"{label}\n      target text is not unique "
                              f"({src.count(old)} occurrences)")
                print(f"  [??] {label}  — target ambiguous")
                continue
            (d / "citation_extract.py").write_text(
                src.replace(old, new), encoding="utf-8")

            code, out = run_suite(d)
            fails = [l for l in out.splitlines() if l.startswith("FAIL:")]
            if code == 0:
                survivors.append(f"{label}\n      expected to break: {expected}")
                print(f"  [SURVIVED] {label}")
            elif not any(expected in l for l in fails):
                # The suite went red, but not on the control this mutation is
                # aimed at. That is the defect this file exists to find, one
                # level up: "some control failed" is not evidence that the
                # NAMED rule is held. It was reached honestly — removing rc2
                # §8's evidence check took twenty controls red and the probe
                # printed only the first, which read as a pass for a rule it
                # had not tested.
                mis = "; ".join(f[:70] for f in fails[:3]) or "(no FAIL line)"
                broken.append(f"{label}\n      expected: {expected}"
                              f"\n      actually failed: {mis}")
                print(f"  [WRONG CONTROL] {label}")
                print(f"           expected {expected[:80]}")
            else:
                hit = next(l for l in fails if expected in l)
                print(f"  [caught] {label}")
                print(f"           {hit[:110]}")

    print()
    if broken:
        print("probes that did not apply — these establish nothing:\n")
        for b in broken:
            print("  ", b)
    if survivors:
        print("mutations the suite did not notice:\n")
        for s in survivors:
            print("  ", s)
        print("\nEach one names a rule with no control actually testing it.")
        return 1
    if broken:
        return 1
    print(f"  all {len(MUTATIONS)} mutations were caught; the controls bite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
