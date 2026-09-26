#!/usr/bin/env python3
"""What does the controller actually print for C01-F01's history?

    python _probe\\c01f01_controller.py

Read-only with respect to the repository; builds and discards a temp fixture.

The repair for C01-F01 fixed the ledger and the diagnostics and left the
controller reporting CONVERGED, and a note was written saying the cycles run
after that exit "are not reported as anything at all". Then
`UNAUTHORIZED CONTINUATION` turned up in `loop_state.py`, firing on exactly
the condition this case meets: a terminal status at boundary n with valid
cycles beyond it.

So the note may be wrong about the part that matters. Reading the code says it
should fire. Reading the code is what produced the wrong census row yesterday,
so this runs it instead.

    the continuation IS named    the gap is only that LOOP_STATUS says
                                 CONVERGED while the ledger says OPEN, which
                                 is narrower than the note claims and makes
                                 one of its three positions the current
                                 behaviour already

    nothing is named             the note stands as written
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import test_ledger as tl  # noqa: E402


def main() -> int:
    root, commit = tl.make_repo()
    rev = root / "runs" / "T-001" / "plan-review"
    for n in (1, 2, 3, 4):
        tl.make_cycle(root, rev, n, commit)

    def led(*args):
        return tl.ledger(root, *args)

    led("raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
        "--class", "UNTESTED RULE", "--source", "CODEX_REVIEW")
    led("respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
        "--disposition", "ACCEPT", "--note", "will fix")
    led("resolve", "--review", str(rev), "--cycle", "2", "--id", "C01-F01",
        "--evidence", "repaired")
    led("reopen", "--review", str(rev), "--cycle", "3", "--id", "C01-F01",
        "--evidence", "it came back")

    lp = rev / "ledger.json"
    doc = json.loads(lp.read_text(encoding="utf-8"))
    hist = doc["findings"]["C01-F01"]["history"]
    hist.append({"cycle": 2, "event": "ACCEPT", "state": "OPEN",
                 "at": "2026-09-16T00:00:00Z", "note": "backdated"})
    hist.append({"cycle": 4, "event": "DEMONSTRATED", "state": "RESOLVED",
                 "at": "2026-09-16T00:00:01Z", "evidence": "the closure"})
    doc["findings"]["C01-F01"]["state"] = "RESOLVED"
    tl.write_lf(lp, json.dumps(doc, indent=2) + "\n")

    show = tl.ledger(root, "show", "--review", str(rev))
    print("  ledger show, state line(s)")
    for line in show.stdout.splitlines():
        if "C01-F01" in line:
            print(f"    {line.strip()}")

    r = tl.loop(root, rev)
    print(f"\n  controller exit {r.returncode}, "
          f"LOOP_STATUS {tl.status_of(r.stdout)}\n")
    print("  full controller output")
    for line in r.stdout.splitlines():
        print(f"    {line}")
    if r.stderr.strip():
        print("\n  stderr")
        for line in r.stderr.splitlines():
            print(f"    {line}")

    named = "UNAUTHORIZED CONTINUATION" in r.stdout
    print("\n  what this settles")
    if named:
        print("    The continuation IS named. The note overstates the gap:")
        print("    the later cycles are reported, and what remains is only")
        print("    that LOOP_STATUS reads CONVERGED while the ledger holds")
        print("    the finding OPEN. Correct the note to say that.")
        return 1
    print("    Nothing names the later cycles. The note stands as written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
