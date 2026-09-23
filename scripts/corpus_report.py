#!/usr/bin/env python3
"""The corpus figures, derived one way, in one place.

    python scripts/corpus_report.py

Exit 0 = the run completed and the figures printed.
Exit 1 = a paper failed for a reason other than a declared refusal.

Why this exists
---------------
On 22 September a corpus measurement reported 72 uncited references where the
true figure is 57, and 2069 parsed candidates where the figure already on
record is 2102. Nothing was wrong with the extractor. The probe had called
`ce.run(p, {"ampersand", "segments"})`, which is correct inside
`test_citation_extract.py` — a control isolates one behaviour deliberately —
and simply wrong for a corpus measurement, where the canonical set is all five
fixes.

That was the third measurement error of the same shape in two days. The first
two are recorded in `GSD-FOLDER-RECOVERY.md`. Writing the fourth ad-hoc probe
and hoping to remember is not a control, so the derivation lives here instead:

    ONE fix set, taken from ce.FIXES rather than retyped
    ONE corpus directory
    ONE definition of each figure

Anything quoting a corpus number in a spec, a Slack message or a commit should
be able to point at this script's output. A number that cannot be reproduced
from here is a number nobody can check.

The self-check
--------------
The figures on record from the August corpus runs are pinned below. If this
script disagrees with them, that disagreement is reported rather than printed
past. A new measurement that quietly contradicts an established one is
reporting on itself, and this repository has now watched that happen three
times.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import citation_extract as ce  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "data/md_full"

# The candidate-state figures this corpus is known to produce under ce.FIXES.
# Not a target and not an assertion about quality — a tripwire, so a change in
# the numbers has to be noticed and explained rather than absorbed.
PINNED = {"parsed": 2102, "unresolved_citation": 133, "excluded_candidate": 19}


def main() -> int:
    if not CORPUS.is_dir():
        print(f"corpus not found at {CORPUS}")
        return 1

    fixes = set(ce.FIXES)
    state, types, refused, unexpected = Counter(), Counter(), [], []

    for p in sorted(CORPUS.glob("*.md")):
        try:
            lines, _code = ce.run(p, fixes)
        except ce.Abort as e:
            # A DECLARED refusal: exit 2 unsupported style, 3 no references,
            # 4 heading contract, 5 bad UTF-8. The extractor working, not
            # failing. Recorded by name and exit code, never silently skipped.
            code = e.args[0] if e.args else "?"
            refused.append((p.name[:12], f"exit {code}: "
                                         f"{str(e.args[1])[:62] if len(e.args) > 1 else e}"))
            continue
        except Exception as e:                       # noqa: BLE001
            # Anything else is a build break wearing a refusal's clothes, and
            # the distinction is one this repository has already had to learn
            # twice in the mutation probe.
            unexpected.append((p.name[:12], f"{type(e).__name__}: {e}"))
            continue
        for ln in lines:
            types[ln.get("type")] += 1
            if ln.get("candidate_state"):
                state[ln["candidate_state"]] += 1

    parsed = state["parsed"]
    unres = state["unresolved_citation"]
    excl = state["excluded_candidate"]
    denom = parsed + unres

    print(f"corpus   {CORPUS.relative_to(REPO)}")
    print(f"fixes    {','.join(sorted(fixes))}   (from ce.FIXES)")
    print(f"papers   {len(list(CORPUS.glob('*.md')))} seen, "
          f"{len(refused)} refused\n")

    print("rc3 A1 candidate states")
    print(f"  parsed                  {parsed}")
    print(f"  unresolved_citation     {unres}")
    print(f"  excluded_candidate      {excl}")

    print("\nrc3 A5, named as A5 names them")
    print(f"  detected_candidates     {denom + excl}")
    print(f"  extraction_denominator  {denom}")
    print(f"  candidate_parse_rate    "
          f"{parsed / denom:.4f}" if denom else "  candidate_parse_rate    n/a")

    print("\nreconciliation records")
    # rc2 §12.2's block order, so the report reads the way the output does.
    # `duplicate_reference_key` was absent from this list while §9.1 was
    # unimplemented, which meant the report agreed with the extractor about a
    # record neither of them produced.
    for t in ("reference", "unresolved_reference", "uncited_reference",
              "missing_reference", "possible_mismatch",
              "duplicate_reference_key", "ambiguous_citation",
              "author_structure_mismatch"):
        print(f"  {t:26} {types[t]}")

    if refused:
        print("\nrefused by the extractor, deliberately")
        for name, why in refused:
            print(f"  {name}  {why}")

    if unexpected:
        print("\n  CRASHED. Not a refusal; these figures are incomplete:")
        for name, why in unexpected:
            print(f"    {name}  {why}")
        return 1

    drift = {k: (v, state[k]) for k, v in PINNED.items() if state[k] != v}
    if drift:
        print("\n  FIGURES MOVED since they were pinned. Explain before "
              "quoting either set:")
        for k, (was, now) in drift.items():
            print(f"    {k:24} pinned {was}  →  now {now}")
        return 1

    print("\n  agrees with the figures on record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
