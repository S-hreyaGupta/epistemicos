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
     "OECD / all_caps_surname"),

    ("the stop list is empty, so In and See become surnames",
     "STOP = {",
     "STOP = set() or {",  # keeps the literal, drops nothing — see below
     "(intentionally inert, replaced below)"),

    ("particles are dropped from the key",
     "    while i < len(toks) and bare(toks[i]).lower() in PARTICLES \\",
     "    while False and bare(toks[i]).lower() in PARTICLES \\",
     "van der Maas particle surname"),

    ("the author phrase is cut at the first comma",
     "    am = re.match(rf\"\\A{AUTHORS_PAREN}\", rest, re.U)",
     "    am = None",
     "multi-author parenthetical"),

    ("particles are matched case-sensitively again",
     'PARTICLE = "(?i:" + "|".join(PARTICLES) + ")"',
     'PARTICLE = "|".join(PARTICLES)',
     "sentence-initial particle surnames"),

    ("the unmarked-up References label is not recognised",
     "        ref = _unmarked_reference_label(text)",
     "        ref = None",
     "a standalone `References` line is a section boundary"),

    ("the entry-count confirmation is removed",
     "        if len(surnames) < MIN_ENTRIES:",
     "        if False:",
     "a `References` line with too few entries below it is refused"),

    ("the ordering confirmation is removed",
     "        if ascending / max(1, len(surnames) - 1) < MIN_ASCENDING:",
     "        if False:",
     "entries below the label are not in order"),

    ("the author-date style guard never fires",
     "    if total >= STYLE_MIN_SAMPLE and share > STYLE_COMMA_LESS_MAX:",
     "    if False:",
     "a comma-less author-date document is refused"),

    ("the style guard has no sample floor",
     "STYLE_MIN_SAMPLE = 10",
     "STYLE_MIN_SAMPLE = 0",
     "too few parentheticals to judge a style"),

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
     "cue 'for a review'"),

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
     "a mathpix cdn image URL is excluded_candidate/url_or_image"),

    ("rc3 B10: the URL test is containment, not anchored",
     'if re.match(r"\\s*(?:https?://|www\\.\\w)", inner, re.I):',
     'if re.search(r"(?:https?://|www\\.\\w)", inner, re.I):',
     "a citation beside a URL parses and is not url_or_image"),

    ("rc3 §E: the structural front-matter test is gone",
     '    if level == "none":\n        return "publisher_metadata"',
     '    if False:\n        return "publisher_metadata"',
     "§E: a candidate above the first h2 is publisher_metadata"),

    ("rc3 §E: the named sections are back in the envelope",
     "    if name.strip().lower() in ENVELOPE_OUT_NAMES:",
     "    if False and name.strip().lower() in ENVELOPE_OUT_NAMES:",
     "§E: a candidate under `## Citation information` is excluded"),

    ("rc3 B10: math exclusion is blanket, deleting D2's real citations",
     "    if span and not D2_YEAR_ONLY.match(body[span[0]:span[1]]):",
     "    if span:",
     "B10/D2: a year-only math span is not math_expression"),

    ("rc3 B10: math spans are never excluded, so the branch is vacuous",
     "    span = _in_math_span(maths, s, e)",
     "    span = None",
     "B10: a math span that is not year-only is math_expression"),

    ("rc3 A2: the reason set stops being closed",
     "    if reason not in EXCLUDED_REASONS:\n        raise AssertionError",
     "    if False:\n        raise AssertionError",
     "A2: a reason outside the closed set is refused, incl. bare_locator"),

    ("rc3 A4: an excluded span is dropped instead of recorded",
     "    excl.append(rec)",
     "    return  # excl.append(rec)",
     "A4: an excluded span is emitted, not silently dropped"),

    ("rc3 A5: the denominator counts the excluded candidates again",
     "    n_parsed, n_unres, n_excl = len(cits), len(unres), len(excl)\n"
     "    denom = n_parsed + n_unres",
     "    n_parsed, n_unres, n_excl = len(cits), len(unres), len(excl)\n"
     "    denom = n_parsed + n_unres + n_excl",
     "A5: the denominator excludes excluded_candidate"),

    ("rc3 A5: the summary calls its parse rate an accuracy",
     '                  "candidate_parse_rate": (round(n_parsed / denom, 4)',
     '                  "extraction_accuracy": (round(n_parsed / denom, 4)',
     "A5: the summary reports a parse rate and no accuracy figure"),
]

# The STOP mutation needs to empty the set rather than edit its opening line.
MUTATIONS[2] = (
    "the stop list is empty, so In and See become surnames",
    "    return bare.lower() in STOP or tok[-1:] in \",;:\"",
    "    return tok[-1:] in \",;:\"",
    "adversarial narrative leads / stopword_surname",
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
            if code == 0:
                survivors.append(f"{label}\n      expected to break: {expected}")
                print(f"  [SURVIVED] {label}")
            else:
                first = next((l for l in out.splitlines()
                              if l.startswith("FAIL:")), "")
                print(f"  [caught] {label}")
                print(f"           {first[:110]}")

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
