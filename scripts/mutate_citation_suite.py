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
     "        if t.lower().rstrip(\",\") in PARTICLES:",
     "        if False:",
     "van der Maas particle surname"),

    ("the C2 run has no six-token cap",
     "    while len(toks) < 6:",
     "    while len(toks) < 60:",
     "World Bank must not degrade / C2 boundary"),

    ("the author phrase is cut at the first comma",
     "    am = re.match(rf\"\\A{AUTHORS_PAREN}\", rest, re.U)",
     "    am = None",
     "multi-author parenthetical"),
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
