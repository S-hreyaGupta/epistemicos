#!/usr/bin/env python3
"""rc2 C-082: bounded termination on corpus and synthetic stress.

    python scripts/termination_bound.py

Exit 0 = everything terminated inside its bound.
Exit 1 = something did not, or grew super-linearly.
Exit 2 = could not run.

Why this exists
---------------
rc2's C-082 asks for a "timed test | no hang", and it is not an abstract worry.
This file has already had the failure once, and `build_patterns` records it:

    with SURNAME now carrying its own alternations the segment pattern went
    exponential — a corpus run that had taken seconds did not finish in three
    minutes.

That is the shape catastrophic backtracking always has. Nothing errors, no
output is wrong, the run simply stops finishing, and the change that caused it
looks like a tidy-up. It returns silently unless something watches for it.

WHAT IS AND IS NOT ESTABLISHED HERE
-----------------------------------
The GROWTH CHECK is validated against a regex known to be catastrophic,
`(a+)+$`, which it sees at 4x per two added characters. So the check works.

The PATTERNS are a different claim. Seven adversarial shapes were tried
against the live patterns — long comma lists, particle runs, et-al runs,
and-chains, semicolon segments, nested parens, and a variant with the
whitespace quantifier deliberately widened to create nested-quantifier
ambiguity. Every one came out linear. So no input that makes the current
patterns super-linear could be constructed.

That is evidence the fix recorded at `build_patterns` is robust. It is NOT
proof that none exists, and this file does not claim otherwise. What it gives
is a regression guard: if a future change reintroduces the shape, these
timings move and this run fails.
"""

from __future__ import annotations

import pathlib
import re
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
CORPUS = REPO / "data" / "md_full"
sys.path.insert(0, str(REPO / "scripts"))

import citation_extract as ce  # noqa: E402

# Generous by design. A normal corpus run is about a second; a hang is
# unbounded. Anything between is not a thing this check needs to distinguish,
# and a tight bound on shared hardware fails for reasons that are not defects.
CORPUS_CEILING_SECONDS = 60.0

# 4x the input should cost about 4x the time. 16 tolerates quadratic and still
# catches exponential by orders of magnitude. A ratio, so it does not depend on
# how fast the machine is.
GROWTH_CEILING = 16.0

SHAPES = {
    "comma author list": lambda n: "(" + ", ".join(["Smith"] * n) + " NOYEAR)",
    "particle run": lambda n: "(" + "van der " * n + "X NOYEAR)",
    "et-al run": lambda n: "(" + "Smith et al. " * n + "NOYEAR)",
    "and-chain": lambda n: "(" + " and ".join(["Smith"] * n) + " NOYEAR)",
    "semicolon segments": lambda n: "(" + "; ".join(["Smith, 2020"] * n) + ")",
    "nested parens": lambda n: "(" * n + "Smith, 2020",
    "narrative run": lambda n: " ".join(["Smith (2020) reports."] * n),
}


def timed(fn, *a):
    t0 = time.perf_counter()
    fn(*a)
    return time.perf_counter() - t0


def main() -> int:
    failures = []

    # 1. The growth check itself, against a regex known to be catastrophic.
    #    Without this the check below could be measuring nothing.
    # 18 -> 26 rather than 18 -> 22. `(a+)+$` roughly quadruples every two
    # characters, so a four-character gap gives about 16x — the SAME order as
    # the ceiling it is meant to validate, and the first run landed at 15.5x
    # and failed. A validation that close to the threshold it validates is not
    # a validation. Eight characters gives four doublings and separates the
    # two by more than an order of magnitude.
    catastrophic = re.compile(r"(a+)+$")
    lo = timed(catastrophic.search, "a" * 18 + "!")
    hi = timed(catastrophic.search, "a" * 26 + "!")
    seen = hi / lo if lo > 0 else 0
    print("  growth check, validated against `(a+)+$`")
    print(f"    18 -> 26 characters costs {seen:.0f}x more time, against a "
          f"{GROWTH_CEILING:.0f}x ceiling")
    if seen < GROWTH_CEILING:
        failures.append(
            f"the growth check cannot see a regex that IS catastrophic "
            f"({seen:.1f}x < {GROWTH_CEILING}); everything below is vacuous")
        print(f"    FAILED — the check is not sensitive enough to be evidence\n")
    else:
        print(f"    the check is sensitive enough to be evidence\n")

    # 2. The live patterns, on adversarial input, at a scale where timing is
    #    signal rather than noise.
    pats = ce.build_patterns({"ampersand"})
    print(f"  synthetic stress, {len(SHAPES)} shapes, n and 4n")
    print(f"    {'shape':20s} {'n=800 ms':>10s} {'n=3200 ms':>11s} {'growth':>8s}")
    for name, mk in SHAPES.items():
        a = timed(pats["cite_paren"].search, mk(800))
        b = timed(pats["cite_paren"].search, mk(3200))
        ratio = b / a if a > 0 else 0
        flag = "" if ratio <= GROWTH_CEILING else "   SUPER-LINEAR"
        print(f"    {name:20s} {a * 1000:10.3f} {b * 1000:11.3f} "
              f"{ratio:7.1f}x{flag}")
        if ratio > GROWTH_CEILING:
            failures.append(f"{name}: 4x the input cost {ratio:.0f}x the time, "
                            f"ceiling is {GROWTH_CEILING:.0f}x")

    # 3. The corpus, end to end, under a wall-clock ceiling. "No hang" is what
    #    C-082 asks for, and this is the only part of it that exercises the
    #    whole pipeline rather than one compiled pattern.
    if not CORPUS.is_dir():
        print(f"\n  corpus not found at {CORPUS}")
        return 2
    papers = sorted(CORPUS.glob("*.md"))
    print(f"\n  corpus, {len(papers)} papers, ceiling "
          f"{CORPUS_CEILING_SECONDS:.0f}s")
    total, slowest = 0.0, ("", 0.0)
    for f in papers:
        t0 = time.perf_counter()
        try:
            ce.run(f, set(ce.FIXES))
        except ce.Abort:
            pass
        dt = time.perf_counter() - t0
        total += dt
        if dt > slowest[1]:
            slowest = (f.name[:8], dt)
    print(f"    total {total:.2f}s, slowest {slowest[0]} at {slowest[1]:.2f}s")
    if total > CORPUS_CEILING_SECONDS:
        failures.append(f"the corpus took {total:.1f}s against a "
                        f"{CORPUS_CEILING_SECONDS:.0f}s ceiling")

    print()
    if failures:
        print("  bounded termination NOT established:\n")
        for f in failures:
            print("   ", f)
        return 1
    print("  C-082: every shape linear, corpus inside its ceiling.")
    print("  The growth check is validated; the patterns are guarded rather")
    print("  than proven — see this file's header for the difference.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
