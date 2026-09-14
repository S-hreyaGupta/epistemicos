#!/usr/bin/env python3
"""Refresh the control counts the bootstrap prompts assert.

    python scripts/refresh_counts.py

Exit 0 = every suite ran to completion and the prompts now match.
Exit 1 = a suite did not exit cleanly; nothing was written.

Why this is a script and not a paste
------------------------------------
It was a here-string pasted into PowerShell, and on 12 September it recorded a
count from a suite that had crashed. `test_run_review.py` raised
FileNotFoundError two thirds of the way through, emitted 29 `[ok]` lines instead
of 95, and produced no FAIL line — so a grep for failures read clean. The
refresh then wrote 29 into both prompts, `test_prompts.py` compared 29 against
29 and passed, and the commit gate let it through.

Three separate checks agreed, and all three were measuring the same crash.

So: a suite that exits non-zero is not a measurement. Its count is whatever it
managed before dying, and writing that number into a document whose stated
purpose is to tell a reviewer how well controlled these components are would
understate them by two thirds. The prompt says it itself — "an inflated one
would misrepresent how well controlled these components are to the reviewer
being asked to trust them" — and the same is true of a deflated one.

Nothing is written unless every suite exits 0.

Why SUITES is five and not eight
--------------------------------
There are eight `test_*.py` files. Three are deliberately outside this count,
and the omission is written here rather than left to be inferred.

`test_prompts.py` is excluded because it is the consumer of this number. It
reads the counts these five produce and compares them against the prompts. A
suite that checked its own count would agree with itself, which is the defect
this script exists to prevent.

`test_convert_protocol.py` and `test_protocol_pin.py` are excluded because they
control protocol document handling — conversion fidelity, version pinning,
reference consistency — and none of those files are in the review target. The
number the prompts assert is a count of controls over the execution layer being
reviewed, not over the repository. Both were run by hand on 14 September and
both were green; they simply are not what this number measures.

If either ever covers a file in the review target, it belongs in SUITES.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUITES = ("test_validate_cycle", "test_run_review", "test_ledger",
          "test_bootstrap_gate", "test_interfaces")


def main() -> int:
    counts: dict[str, int] = {}
    broken: list[str] = []

    for name in SUITES:
        out = subprocess.run([sys.executable, f"scripts/{name}.py"],
                             cwd=str(REPO), capture_output=True, text=True)
        text = out.stdout + out.stderr
        n = text.count("[ok]")
        counts[f"scripts/{name}.py"] = n
        if out.returncode != 0:
            tail = [l for l in text.splitlines() if l.strip()][-1:] or ["(no output)"]
            broken.append(f"{name}: exit {out.returncode}, {n} control(s) "
                          f"before stopping\n      {tail[0][:140]}")

    for rel, n in sorted(counts.items()):
        print(f"  {rel:<34}{n}")
    print(f"  {'total':<34}{sum(counts.values())}")

    if broken:
        print()
        print("NOT WRITING. A suite that did not exit cleanly is not a count:")
        for b in broken:
            print(f"    {b}")
        print()
        print("  Its total is whatever it reached before stopping. Recording "
              "that would understate")
        print("  the controls to the reviewer being asked to trust them, and a "
              "crash reports no")
        print("  failure, so nothing else would notice.")
        return 1

    changed = []
    for p in sorted((REPO / "specs" / "prompts").glob("bootstrap-review*.md")):
        original = p.read_text(encoding="utf-8")
        text = original
        for rel, n in counts.items():
            text = re.sub(rf"^({re.escape(rel)}\s+)\d+( controls)",
                          rf"\g<1>{n}\g<2>", text, flags=re.M)
        if text != original:
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            changed.append(p.name)

    print()
    print(f"updated: {', '.join(changed) if changed else 'nothing to change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
