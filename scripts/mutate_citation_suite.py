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
     "a plain-text References label with five ordered entries below it"),

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

    ("rc2 §8.2: every lookup reports a unique match",
     '        elif len(idx) == 1:\n            state = "unique"',
     '        elif True:\n            state = "unique"',
     "§8.2: two references sharing a key is nonunique"),

    ("rc2 §8.2: a no-match reports as resolved anyway",
     '        if not idx:\n            state = "no_match"',
     '        if False:\n            state = "no_match"',
     "§8.2: no keyed reference is no_match"),

    ("rc2 §8.2: reference indices are not sorted",
     '        idx = sorted(ref_index_by_key.get(cand, []))',
     '        idx = list(reversed(ref_index_by_key.get(cand, [])))',
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
     '                "candidate_key": cand_key, "occurrences": len(occs),',
     '                "candidate_key": None, "occurrences": len(occs),',
     "CIT-ARCH-01: the candidate is preserved in the diagnostic"),

    ("rc2 §11.2: the identity partition double-counts",
     '                          if c["identity_class"] == "identity_not_resolved"),',
     '                          if c["identity_class"] != "unique_reference_match"),',
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
     '                "merge_suspected": merge,\n                "citation_key": None, "author_kind": None,',
     '                "merge_suspected": merge,\n                "citation_key": cand_key, "author_kind": kind,',
     "§9.4: neither diagnostic establishes citation_key"),

    ("rc2 §9.4: nothing is ever paired",
     "            rule = repair_rule(kind, phrase, year, rk, rp, ry)",
     "            rule = None",
     "§9.4 surname_edit_distance_1: expected one possible_mismatch"),

    ("rc3 B1b: the parenthetical detection site is closed again",
     "        inner = body[c1s + 1:c1e - 1]\n        cut = YEAR_RE.search(inner)",
     "        inner = body[c1s + 1:c1e - 1]\n        cut = None",
     "§G: (International Monetary Fund, 2022) keys the complete label"),
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
