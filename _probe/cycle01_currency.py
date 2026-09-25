#!/usr/bin/env python3
"""Is BOOTSTRAP-002 cycle-01 still a review of the code that exists?

    python _probe\\cycle01_currency.py

Read-only. Nothing is written and nothing is decided here.

Cycle-01 was frozen on 17 September and never run. Giving its 340 KB input to
a reviewer is a real cost, so the question worth answering first is what that
reviewer would be reading.

`validate_cycle.py` cannot answer it: that gate requires `codex-output-raw.md`
and so can only speak after the round trip, not before it. And the freeze
itself says nothing either, which is the finding this run already produced
once in a different form. A frozen `target.json` states intent. It is not
evidence that anyone read the bytes, and it is not evidence that the bytes are
still the ones in the working tree.

So this compares three things per artifact:

    frozen      the sha256 recorded in target.json
    snapshot    the copy kept under <cycle>/artifacts/, which is what the
                reviewer's input was composed from
    live        the file in the working tree today

    CURRENT     live matches frozen. A finding lands on real code.
    DRIFTED     live has moved since the freeze. The review is still coherent,
                because the snapshot is a fixed object and the reviewer reads
                that, but some findings may name code that no longer exists.
    SNAPSHOT-MISMATCH
                the snapshot does not match its own recorded hash. That is a
                broken cycle rather than a stale one, and it is the one result
                here that should stop the round trip.

DRIFTED is not by itself a reason not to run. It is a reason to know, before
spending the round trip, how much of the answer will be about the past.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CYCLE = REPO / "runs" / "BOOTSTRAP-002" / "plan-review" / "cycle-01"


def sha(p: Path) -> str | None:
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    target = json.loads((CYCLE / "target.json").read_text(encoding="utf-8"))

    rows, current, drifted, broken = [], 0, 0, 0
    for entry in target["plan_files"]:
        rel, frozen = entry["path"], entry["sha256"]
        live = sha(REPO / rel)
        snap = sha(CYCLE / "artifacts" / rel)

        if snap is None:
            state, broken = "SNAPSHOT MISSING", broken + 1
        elif snap != frozen:
            state, broken = "SNAPSHOT-MISMATCH", broken + 1
        elif live is None:
            state, drifted = "DELETED FROM TREE", drifted + 1
        elif live == frozen:
            state, current = "current", current + 1
        else:
            state, drifted = "DRIFTED", drifted + 1
        rows.append((rel, state))

    print("  the nine plan files under review\n")
    for rel, state in rows:
        print(f"    {rel:34}  {state}")
    print(f"\n    {current} current, {drifted} drifted, {broken} broken\n")

    print("  governing pins\n")
    for rel, want in target["governing_pin_hashes"].items():
        got = sha(REPO / rel)
        print(f"    {rel:44}  "
              f"{'current' if got == want else 'DRIFTED' if got else 'MISSING'}")

    aux = sha(CYCLE / "auxiliary-evidence.json")
    want_aux = target.get("auxiliary_evidence_sha256")
    print(f"\n  auxiliary-evidence.json                       "
          f"{'intact' if aux == want_aux else 'MISMATCH'}")

    inp = CYCLE / "codex-input.md"
    print(f"  codex-input.md                                "
          f"{inp.stat().st_size if inp.is_file() else 0} bytes")

    out = CYCLE / "codex-output-raw.md"
    print(f"  codex-output-raw.md                           "
          f"{'present' if out.is_file() else 'absent, never run'}")

    print()
    if broken:
        print("  A snapshot that does not match its own recorded hash is a")
        print("  broken cycle, not a stale one. Fix that before the round")
        print("  trip; a review of it would be evidence about nothing.")
        return 2
    if drifted:
        print("  The cycle is intact and the reviewer would read a coherent")
        print("  object. Some of what it reads is no longer what runs, so")
        print("  expect findings that name code already changed. Whether that")
        print("  is worth the round trip, or whether cycle-01 should be")
        print("  re-frozen at today's bytes first, is a judgement and not")
        print("  this file's to make.")
        return 1
    print("  Every artifact under review is the file that exists today. A")
    print("  finding from this cycle lands on running code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
