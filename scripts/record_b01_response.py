#!/usr/bin/env python3
"""Transcribe Codex's B01 findings into the ledger and record the responses.

    python scripts/record_b01_response.py

One-off, for BOOTSTRAP-001 plan-review cycle 01. Not part of the protocol
machinery.

Why this script exists, and why that is itself a finding
-------------------------------------------------------
B01-F03 says there is no runner-owned finding capture: the schema assigns
per-cycle findings.json to the review runner, the runner never writes it, and
nothing turns raw reviewer output into ledger entries. So the transcription falls
to whoever is holding the keyboard, which right now is the implementing agent
writing this file.

That is the defect being demonstrated rather than described. Under MC-1 the
implementing agent should not be the one deciding which findings entered the
authoritative record. It is doing so here because no other mechanism exists, and
this comment is the disclosure.

Every finding below is transcribed verbatim from codex-output-raw.md. The
disposition on all eighteen is ACCEPT: each was verified against the code before
responding, and none was found wrong.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REVIEW = REPO / "runs" / "BOOTSTRAP-001" / "plan-review"
LEDGER = REPO / "scripts" / "ledger.py"

# (id, class, requirement, one-line reason recorded with the ACCEPT)
FINDINGS = [
    ("C01-F01", "CONTRADICTORY IMPLEMENTATION MAPPING", "MC-2",
     "next_cycle counts directories, not valid cycles, so four invalid cycles "
     "exhaust a budget MC-2 says they cannot consume. Verified."),
    ("C01-F02", "CONTRADICTORY IMPLEMENTATION MAPPING", "S6",
     "The controller tests exits only at the latest boundary and the runner "
     "checks only that the previous cycle has output, so a terminal exit in an "
     "earlier cycle can be overridden by a later one. Verified."),
    ("C01-F03", "WRONG OWNERSHIP", "MC-1",
     "The schema assigns per-cycle findings.json to the runner; the runner never "
     "writes it and the ledger writes a review-level file instead. An absent "
     "ledger reads as a review that found nothing. Verified."),
    ("C01-F04", "MISSING REQUIREMENT", "S2.2",
     "compose_input carries the protocol but not the pinned spec, and for "
     "implementation review omits the target identifiers entirely. I fixed the "
     "protocol omission last night and stopped one step short. Verified."),
    ("C01-F05", "NONDETERMINISTIC WHERE D POSSIBLE", "S10.1",
     "candidate_commit is stored verbatim, so HEAD is accepted and stays "
     "mutable while checks 11 and 12 keep passing. Verified."),
    ("C01-F06", "MISSING REQUIREMENT", "S10.2",
     "Check 13 compares two recorded strings and never hashes the approved plan, "
     "so the plan can change while both records still agree. Verified."),
    ("C01-F07", "MISSING REQUIREMENT", "MC-2",
     "protocol_sha256 and spec_sha256 are checked for presence only; no check "
     "ties them to the pinned artifacts or to run.json. Verified."),
    ("C01-F08", "MISSING REQUIREMENT", "MC-2",
     "The bootstrap gate runs at init and never again, so components can change "
     "before freeze; and loop_state never reads the exempt label, so development "
     "evidence can reach authoritative loop state. Verified."),
    ("C01-F09", "MISSING REQUIREMENT", "MC-1",
     "cmd_record hashes whatever is on disk at decision time and never compares "
     "it to the frozen review target, so approval can cover code the review "
     "never saw. Verified."),
    ("C01-F10", "MISSING REQUIREMENT", "MC-1",
     "The review target carries six artifacts; the gate covers five. Editing "
     "evidence-schema-v1.0.md does not invalidate its own approval. Verified."),
    ("C01-F11", "CONTRADICTORY IMPLEMENTATION MAPPING", "S6",
     "The ledger authorises transitions from unfiltered history while the "
     "controller filters by valid cycle, so the two disagree about a finding's "
     "state and an invalid-cycle event can deadlock a valid one. Verified."),
    ("C01-F12", "MISSING REQUIREMENT", "S5",
     "No event is checked against the finding's raising cycle, so a finding can "
     "be accepted and resolved in cycles earlier than the one that raised it. "
     "Verified."),
    ("C01-F13", "CONTRADICTORY IMPLEMENTATION MAPPING", "V40",
     "The duplicate-id refusal instructs that a re-raised issue becomes a new "
     "finding, which contradicts V40 and defeats S6's re-raise detection. The "
     "refusal itself is right; its guidance is wrong. Verified."),
    ("C01-F14", "MISSING REQUIREMENT", "MC-1",
     "MC-1 requires each run to record MC1_ENFORCEMENT. run.json does not carry "
     "it; the status lives only in repository documentation. Verified."),
    ("C01-F15", "CONTRADICTORY IMPLEMENTATION MAPPING", "MC-1",
     "The schema says freezing proves the artifact did not change, and I told "
     "Alex self-hashing closed the replace-evaluate hole. Neither holds under "
     "CONVENTION_ONLY: the same writable code performs the check. Verified."),
    ("C01-F16", "UNTESTED RULE", "MC-1",
     "PY_REF matches filename strings, so a real import is invisible to the "
     "closure, and my control inserted a string rather than an import. The "
     "closure claim I gave Alex was stronger than its evidence. Verified."),
    ("C01-F17", "UNTESTED RULE", "S10.1",
     "Two of five implementation refusals are exercised while the suite prints "
     "that every refusal is reachable. Verified."),
    ("C01-F18", "UNTESTED RULE", "MC-2",
     "Seam-1 probes sit outside a cycle layout, so check 13 fails on all of "
     "them for the wrong reason. Demonstrated: deleting check 12's enforcement "
     "outright still reports 7/7 enforced and exits 0."),
]


def run(*args: str) -> int:
    r = subprocess.run([sys.executable, str(LEDGER), *args],
                       cwd=str(REPO), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  FAILED: {' '.join(args[:6])}\n    {r.stderr.strip()}")
    return r.returncode


def main() -> int:
    if not (REVIEW / "cycle-01" / "codex-output-raw.md").is_file():
        print("no recorded reviewer output; record the cycle first", file=sys.stderr)
        return 2

    bad = 0
    print(f"raising {len(FINDINGS)} findings from codex-output-raw.md")
    for fid, klass, req, _ in FINDINGS:
        bad += run("raise", "--review", str(REVIEW), "--cycle", "1",
                   "--id", fid, "--class", klass, "--requirement", req,
                   "--note", "transcribed verbatim from codex-output-raw.md, "
                             "B01 numbering")

    print()
    print("responding ACCEPT to each")
    for fid, _, _, reason in FINDINGS:
        bad += run("respond", "--review", str(REVIEW), "--cycle", "1",
                   "--id", fid, "--disposition", "ACCEPT", "--note", reason)

    print()
    if bad:
        print(f"{bad} command(s) failed")
        return 1
    print(f"{len(FINDINGS)} findings raised and accepted. All remain OPEN: §5 "
          "gives RESOLVED\nonly once each repair is demonstrated in the next "
          "review target.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
