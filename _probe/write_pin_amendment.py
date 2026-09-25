#!/usr/bin/env python3
"""Amendment 1 to BOOTSTRAP-002's pin set, written and then verified.

    python _probe\\write_pin_amendment.py            # show what it would write
    python _probe\\write_pin_amendment.py --write     # write it

Why this exists as a script rather than a hand-written JSON file: it stamps
`at` with the real UTC time of writing instead of a time I typed, and it
re-reads the result through run_pins.governing_pins afterwards, so the file is
proved to parse and validate rather than assumed to.

The amendment itself removes `specs/evidence-schema-v1.0.md` from the run's
governing pins so it can be a REVIEW TARGET instead. It is currently both,
which run_review.py refuses at freeze, and that refusal is what stopped
BOOTSTRAP-002 cycle-01 from covering all ten components the bootstrap gate
requires.

Authorised by Alex Zamurko in Slack, 25 September 2026 15:40, replying to the
workflow-readiness report: "Yes, approved. Amend the BOOTSTRAP-002 pin set
using the documented run_pins.py mechanism so that specs/evidence-schema-v1.0.md
can be included in the frozen review target."
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN_DIR = REPO / "runs" / "BOOTSTRAP-002"
AMEND = RUN_DIR / "pin-amendments.json"

PRIOR = [
    "specs/evidence-schema-v1.0.md",
    "specs/implementation-review-protocol-v1.1.md",
]
NEW = [
    "specs/implementation-review-protocol-v1.1.md",
]

REASON = (
    "specs/evidence-schema-v1.0.md is pinned as run-governing and is also one "
    "of the ten components the bootstrap gate requires to be covered by the "
    "review target. An artifact cannot hold both roles: it would have to stay "
    "byte-identical for the run while also being changeable to resolve a "
    "finding raised about it. The gate added it to COMPONENTS deliberately, "
    "because MC-2 checks evidence against it and covering the checker but not "
    "the document it reads its expectations from leaves a seam through the "
    "middle of what the review claims to cover. Removing it from the pin set "
    "resolves the collision in the direction the gate requires, leaving the "
    "protocol as the sole governing pin. Authorised by Alex Zamurko, Slack, "
    "25 September 2026 15:40."
)


def _gov():
    spec = importlib.util.spec_from_file_location(
        "_run_pins", REPO / "scripts" / "run_pins.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    doc = {
        "schema": "run-pin-amendments/1",
        "amendments": [
            {
                "reason": REASON,
                "affected_artifacts": ["specs/evidence-schema-v1.0.md"],
                "prior_pin_set": PRIOR,
                "new_pin_set": NEW,
                "effective_cycle": 2,
                "authorized_by": "Alex Zamurko",
                "at": _dt.datetime.now(_dt.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        ],
    }
    blob = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    if AMEND.exists():
        print(f"  {AMEND.relative_to(REPO).as_posix()} already exists.")
        print("  Amendments are appended, never rewritten. Stopping so this "
              "cannot silently\n  replace a prior one.")
        return 1

    if not a.write:
        print("  would write "
              f"{AMEND.relative_to(REPO).as_posix()}\n")
        print(blob)
        print("  re-run with --write to create it")
        return 0

    AMEND.write_text(blob, encoding="utf-8", newline="")
    print(f"  wrote {AMEND.relative_to(REPO).as_posix()}")

    # Verified, not assumed. If this raises, the amendment is malformed and the
    # freeze would have failed later with less context.
    rp = _gov()
    for cycle in (1, 2):
        try:
            pins = rp.governing_pins(
                json.loads((RUN_DIR / "run.json").read_text(encoding="utf-8")),
                RUN_DIR, cycle)
            print(f"    governing pins at cycle {cycle}: {sorted(pins)}")
        except Exception as e:
            print(f"    cycle {cycle}: REFUSED — {e}")
            return 1

    print("\n  Cycle 1 keeps the pin set it was frozen under. Cycle 2 onward")
    print("  drops the evidence schema, which is what lets it be a review")
    print("  target. Historical cycles are never revalidated against a later")
    print("  pin set, which is the whole reason amendments are a history.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
