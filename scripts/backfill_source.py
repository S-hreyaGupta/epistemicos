#!/usr/bin/env python3
"""Backfill `source` on findings raised before the field existed.

    python scripts/backfill_source.py --review runs/BOOTSTRAP-001/plan-review
    python scripts/backfill_source.py --review <dir> --apply

Exit 0 = reported, or written with `--apply`.
Exit 1 = refused; nothing written.

Alex Zamurko, 18 September 2026:

    Backfill SOURCE as reconstructed provenance. The historical Codex origin is
    provable, so UNRECORDED unnecessarily loses information; mark the backfill
    explicitly as reconstructed.

Evidenced, not asserted
-----------------------
"Provable" is doing real work in that ruling, so this proves it rather than
taking it. A finding is backfilled only if its identifier appears verbatim in
`codex-output-raw.md` for the cycle that raised it — the frozen, hashed capture
of what the reviewer actually said. Any finding whose identifier is not there is
left `UNRECORDED` and reported, because for that one the claim would be exactly
the assertion the ruling was careful to avoid.

What the record then says
-------------------------
`source` is set, and `source_provenance` beside it says the value was
reconstructed, when, on whose authority, and from what. That is the shape used
for `mc1_enforcement` in `run.json` on 11 September, for the same reason: a
value recovered later and a value recorded at the time are different claims, and
a file that cannot tell them apart is worth less than one that can.

This does not make the enforcement stronger. Under `CONVENTION_ONLY` the raw
captures are detection that holds while nobody edits them, and a backfill read
from them inherits exactly that and no more.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

AUTHORITY = ("Alex Zamurko, 18 September 2026: \"Backfill SOURCE as "
             "reconstructed provenance. The historical Codex origin is "
             "provable, so UNRECORDED unnecessarily loses information; mark "
             "the backfill explicitly as reconstructed.\"")


class Refused(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="backfill_source.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", required=True)
    ap.add_argument("--apply", action="store_true",
                    help="without this, report and change nothing")
    a = ap.parse_args()

    review = Path(a.review).resolve()
    led_p = review / "ledger.json"
    if not led_p.is_file():
        raise Refused(f"no ledger at {led_p}")
    led = json.loads(led_p.read_text(encoding="utf-8"))

    raw: dict[int, tuple[Path, str]] = {}
    for c in sorted(review.glob("cycle-*")):
        p = c / "codex-output-raw.md"
        if p.is_file():
            raw[int(c.name.split("-")[1])] = (
                p, p.read_text(encoding="utf-8", errors="replace"))
    if not raw:
        raise Refused(
            f"no codex-output-raw.md under {review}. The backfill reads the "
            "reviewer's own\n  frozen capture; without it there is nothing to "
            "reconstruct from and the value would\n  be an assertion.")

    evidenced, unevidenced, already = [], [], 0
    for fid, f in sorted(led["findings"].items()):
        if f.get("source"):
            already += 1
            continue
        cyc = f.get("cycle_raised")
        hit = cyc in raw and re.search(re.escape(fid), raw[cyc][1])
        (evidenced if hit else unevidenced).append((fid, cyc))

    print(f"ledger {led_p.relative_to(REPO).as_posix()}")
    print(f"  already carry a source          {already}")
    print(f"  identifier found in its cycle's raw capture   {len(evidenced)}")
    print(f"  not found, left UNRECORDED      {len(unevidenced)}")
    for fid, cyc in unevidenced:
        print(f"      {fid}  raised cycle {cyc}")

    if not a.apply:
        print()
        print("  reported only. Pass --apply to write.")
        return 0

    for fid, cyc in evidenced:
        f = led["findings"][fid]
        p, _ = raw[cyc]
        f["source"] = "CODEX_REVIEW"
        f["source_provenance"] = {
            "reconstructed": True,
            "added": "2026-09-18",
            "why": "this finding was raised before the source field existed. "
                   "The field was introduced on 16 September closing B02-F11.",
            "basis": f"the identifier {fid} appears verbatim in "
                     f"{p.relative_to(review).as_posix()}, the frozen capture "
                     f"of what the reviewer said in the cycle that raised it.",
            "authority": AUTHORITY,
            "limit": "under CONVENTION_ONLY the raw captures are detection "
                     "that holds while nobody edits them. A value read from "
                     "them inherits that and no more.",
        }

    led_p.write_text(json.dumps(led, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8", newline="\n")
    print()
    print(f"  wrote {len(evidenced)} source field(s), each with its basis")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
