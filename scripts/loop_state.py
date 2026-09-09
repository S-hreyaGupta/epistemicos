#!/usr/bin/env python3
"""Loop-state controller.

Computes CONVERGED / HUMAN_ADJUDICATION_REQUIRED / STALLED / MAX_4_REACHED /
CONTINUE for one review loop, per §6 and §13 of the protocol, and shows the
working.

    python scripts/loop_state.py --review runs/A1E-001/plan-review

Exit 0 = a state was determined, 2 = could not run.
The state itself is on stdout as LOOP_STATUS; it is not an exit code, because
CONTINUE is not a failure and STALLED is not an error.

Validity is computed, not trusted
---------------------------------
§2 : "Only cycles that pass the MC-2 conformance gate count toward this maximum."
§3 : an invalid cycle "cannot support an authoritative Codex finding" and
     "cannot consume one of the four valid review cycles".

So this runs scripts/validate_cycle.py on every cycle directory rather than
reading a recorded verdict. A loop controller that accepted an asserted PASS
would let an invalid cycle consume the budget, which is the exact defect the
"MAX 4 counts valid cycles" note exists to prevent.

Two consequences, both deliberate and both worth disagreeing with if you see it
differently:

1. §6's n indexes VALID cycles, not directory numbers. If cycle-02 fails the
   gate, then cycle-03 is n=2. Otherwise |OPEN_n| would be compared against a
   cycle whose evidence is not authoritative.

2. Events recorded in an invalid cycle are ignored entirely, including
   resolutions. A finding accepted in valid cycle 1 and marked demonstrated in
   invalid cycle 2 stays OPEN, because the cycle that would demonstrate it
   cannot support an authoritative anything. This is the conservative reading
   and it can only ever delay an exit, never manufacture one.

What this does not do
---------------------
It does not decide whether a repair was demonstrated; the ledger records that
assertion and this reads it. It does not adjudicate disputes. And CONVERGED
here means the finding sets are empty, not that the plan is good.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
VALIDATOR = REPO / "scripts" / "validate_cycle.py"
MAX_VALID_CYCLES = 4

OPEN, RESOLVED, DISPUTED = "OPEN", "RESOLVED", "DISPUTED"


def cycle_dirs(review: Path) -> list[tuple[int, Path]]:
    out = []
    for d in sorted(review.iterdir()) if review.is_dir() else []:
        m = re.fullmatch(r"cycle-(\d{2})", d.name)
        if m and d.is_dir():
            out.append((int(m.group(1)), d))
    return sorted(out)


def gate(cycle_dir: Path) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, str(VALIDATOR), str(cycle_dir)],
                       capture_output=True, text=True)
    if r.returncode == 2:
        return False, "checker could not run"
    reason = ""
    if r.returncode != 0:
        fails = [l.strip() for l in r.stdout.splitlines() if "[FAIL]" in l]
        reason = fails[0] if fails else "MC-2 FAIL"
    return r.returncode == 0, reason


class CannotCalculate(Exception):
    """Loop state is not determinable from the evidence present. Exit 2."""


def load_ledger(review: Path) -> dict:
    """State history. Absent means no findings have been responded to yet.

    Distinct from the per-cycle authoritative findings, which are checked
    separately below and whose absence is a refusal rather than a zero.
    """
    p = review / "ledger.json"
    if not p.is_file():
        return {"findings": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise CannotCalculate(f"ledger.json is not valid JSON: {e}")


def authoritative_findings(cycle_dir: Path) -> list[str]:
    """The finding IDs the runner extracted for this cycle.

    Alex Zamurko, issue 4: "Controller refuses to calculate loop state if
    findings.json is missing or invalid."

    Absence used to mean zero. That is the path by which a review full of
    findings produces CONVERGED: nobody transcribes them, the ledger is empty,
    and empty reads as clean. So a valid cycle without an authoritative findings
    record is not a cycle with no findings; it is a cycle whose result nobody
    can determine, and the controller says so rather than guessing.
    """
    # Requirements 3 and 4: the structured result must still account for the
    # raw review, and identifiers must be unchanged along the whole chain
    #
    #     codex-output-raw.md -> findings.json -> ledger.json
    #
    # Checked here rather than only at record time, because findings.json is an
    # ordinary file afterwards. A finding quietly dropped from it, or renamed,
    # would otherwise never be noticed again.
    raw = cycle_dir / "codex-output-raw.md"
    p = cycle_dir / "findings.json"
    if raw.is_file() and p.is_file():
        try:
            import findings_format
            parsed, problems = findings_format.extract(
                raw.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            raise CannotCalculate(
                f"{cycle_dir.name}: the raw review cannot be reparsed, so the "
                f"structured result cannot be checked against it: {e}")
        if problems:
            raise CannotCalculate(
                f"{cycle_dir.name}: the raw review no longer parses "
                "deterministically:\n  " + "\n  ".join(problems))
        try:
            structured = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise CannotCalculate(f"{cycle_dir.name}/findings.json is not valid "
                                  f"JSON: {e}")
        raw_ids = [f["id"] for f in parsed]
        got_ids = [f.get("id") for f in structured.get("findings", [])]
        if raw_ids != got_ids:
            raise CannotCalculate(
                f"{cycle_dir.name}: findings.json does not match the raw review "
                "it was extracted from.\n"
                f"  raw        {raw_ids}\n"
                f"  structured {got_ids}\n"
                "  A finding dropped or renamed here is a finding the loop will "
                "never see.")

    if not p.is_file():
        raise CannotCalculate(
            f"{p.parent.name} passed MC-2 but has no findings.json.\n"
            "  Absence is not zero. Either the runner did not record this cycle "
            "or the file\n  was removed; both make the loop state "
            "undeterminable. Re-record the cycle.")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise CannotCalculate(f"{p.parent.name}/findings.json is not valid "
                              f"JSON: {e}")
    if d.get("schema") != "cycle-findings/1":
        raise CannotCalculate(
            f"{p.parent.name}/findings.json declares schema "
            f"{d.get('schema')!r}, expected 'cycle-findings/1'")
    items = d.get("findings")
    if not isinstance(items, list) or "count" not in d:
        raise CannotCalculate(f"{p.parent.name}/findings.json is malformed: "
                              "needs a findings list and a count")
    if d["count"] != len(items):
        raise CannotCalculate(
            f"{p.parent.name}/findings.json says count={d['count']} but carries "
            f"{len(items)} findings")
    if not items and not d.get("zero_findings_asserted"):
        raise CannotCalculate(
            f"{p.parent.name}/findings.json records zero findings without "
            "zero_findings_asserted.\n  Zero has to be asserted, never inferred.")
    return [f["id"] for f in items if isinstance(f, dict) and "id" in f]


def state_after(f: dict, valid_upto: set[int]) -> str | None:
    """State as at the end of the valid cycles in `valid_upto`.

    Events in cycles outside the set are skipped, per consequence 2 above.
    """
    state = None
    for e in f["history"]:
        if e["cycle"] in valid_upto:
            state = e["state"]
    return state


def sets_at(ledger: dict, valid_upto: set[int]) -> dict[str, set[str]]:
    out = {OPEN: set(), RESOLVED: set(), DISPUTED: set()}
    for fid, f in ledger["findings"].items():
        s = state_after(f, valid_upto)
        if s in out:
            out[s].add(fid)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", required=True)
    ap.add_argument("--quiet", action="store_true", help="print LOOP_STATUS only")
    a = ap.parse_args(argv[1:])
    try:
        return _run(a)
    except CannotCalculate as e:
        print(f"CANNOT CALCULATE LOOP STATE: {e}", file=sys.stderr)
        print()
        print("No LOOP_STATUS is emitted. An undeterminable state is not "
              "CONTINUE, and it is\nnot CONVERGED; treating it as either is the "
              "failure this refusal exists to stop.", file=sys.stderr)
        return 2


def _run(a) -> int:
    review = Path(a.review).resolve()
    if not review.is_dir():
        print(f"not a directory: {review}", file=sys.stderr)
        return 2

    dirs = cycle_dirs(review)
    if not dirs:
        print(f"no cycle directories in {review}", file=sys.stderr)
        return 2

    lines: list[str] = [f"loop state — {review}", "", "cycles"]
    valid: list[int] = []
    for num, d in dirs:
        ok, why = gate(d)
        if ok:
            valid.append(num)
            lines.append(f"  cycle-{num:02d}  VALID    -> n={len(valid)}")
        else:
            lines.append(f"  cycle-{num:02d}  INVALID  {why}")
            lines.append("            does not count toward the budget and its "
                         "events are ignored")
    lines += ["", f"VALID_CYCLE_COUNT: {len(valid)}"]

    if not valid:
        lines += ["", "LOOP_STATUS: CONTINUE",
                  "No valid cycle has been completed, so §6 has nothing to measure. "
                  "Repair the evidence and rerun."]
        print("\n".join(lines) if not a.quiet else "LOOP_STATUS: CONTINUE")
        return 0

    # Every valid cycle must carry an authoritative findings record, and the
    # ledger must account for everything in it. Without this the controller
    # measures only what someone remembered to transcribe, and silence reads as
    # a clean review.
    ledger = load_ledger(review)
    lines += ["", "authoritative findings"]
    unaccounted: list[str] = []
    for num, d in dirs:
        if num not in valid:
            continue
        ids = authoritative_findings(d)
        missing = [i for i in ids if i not in ledger["findings"]]
        lines.append(f"  cycle-{num:02d}  {len(ids)} finding(s)"
                     + (f": {', '.join(ids)}" if ids else ", explicitly zero"))
        unaccounted += [f"cycle-{num:02d}: {i}" for i in missing]
    if unaccounted:
        raise CannotCalculate(
            "findings the reviewer recorded are absent from the ledger:\n  "
            + "\n  ".join(unaccounted) +
            "\n\n  The loop state would be computed over a smaller finding set "
            "than the review\n  produced, which is how a review full of findings "
            "reaches CONVERGED.")
    lines.append("  every recorded finding is accounted for in the ledger")

    n = len(valid)
    upto_n = set(valid)
    upto_prev = set(valid[:-1])

    cur = sets_at(ledger, upto_n)
    prev = sets_at(ledger, upto_prev) if n > 1 else None

    # §6: the _NEW_n sets are findings that were OPEN after n-1 and changed during n.
    resolved_new: set[str] = set()
    disputed_new: set[str] = set()
    if prev is not None:
        for fid in prev[OPEN]:
            s = state_after(ledger["findings"][fid], upto_n)
            if s == RESOLVED:
                resolved_new.add(fid)
            elif s == DISPUTED:
                disputed_new.add(fid)

    def fmt(ids: set[str]) -> str:
        return ", ".join(sorted(ids)) if ids else "-"

    lines += ["", "§6 sets"]
    lines.append(f"  OPEN_{n}          {len(cur[OPEN]):>2}  {fmt(cur[OPEN])}")
    lines.append(f"  DISPUTED_{n}      {len(cur[DISPUTED]):>2}  {fmt(cur[DISPUTED])}")
    lines.append(f"  RESOLVED_{n}      {len(cur[RESOLVED]):>2}  {fmt(cur[RESOLVED])}")
    if prev is not None:
        lines.append(f"  OPEN_{n-1}          {len(prev[OPEN]):>2}  {fmt(prev[OPEN])}")
        lines.append(f"  RESOLVED_NEW_{n}  {len(resolved_new):>2}  {fmt(resolved_new)}")
        lines.append(f"  DISPUTED_NEW_{n}  {len(disputed_new):>2}  {fmt(disputed_new)}")

    # Exits are tested in the protocol's order, and the order is load-bearing.
    # HUMAN_ADJUDICATION_REQUIRED sits between CONVERGED and STALLED because a
    # loop with nothing open and a dispute outstanding is not stalled: it
    # finished everything automation can do. Test STALLED first and it swallows
    # the case a cycle later, which is what v1.0 did.
    lines += ["", "exits"]
    status = None
    detail = ""

    converged = not cur[OPEN] and not cur[DISPUTED]
    lines.append(f"  A CONVERGED                    OPEN_{n} = 0 and DISPUTED_{n} = 0"
                 f"        {'yes' if converged else 'no'}")
    if converged:
        status = "CONVERGED"
        detail = "Nothing open and nothing disputed. Proceed to human plan review."

    if status is None:
        adjudicate = not cur[OPEN] and cur[DISPUTED]
        lines.append(f"  B HUMAN_ADJUDICATION_REQUIRED  OPEN_{n} = 0 and "
                     f"DISPUTED_{n} != 0     {'yes' if adjudicate else 'no'}")
        if adjudicate:
            status = "HUMAN_ADJUDICATION_REQUIRED"
            detail = ("Everything actionable is resolved or disputed, and no further "
                      "automated repair is available. Stop now rather than spending a "
                      "cycle on a plan with nothing open to repair. Proceed to human "
                      "plan review.")

    if status is None:
        if prev is None:
            lines.append("  C STALLED                      not testable at n=1 "
                         "(§6 requires n > 1)")
        else:
            stalled = (len(cur[OPEN]) >= len(prev[OPEN])
                       and not resolved_new and not disputed_new)
            lines.append(
                f"  C STALLED                      |OPEN_{n}| >= |OPEN_{n-1}|"
                f" ({len(cur[OPEN])} >= {len(prev[OPEN])})"
                f" and no new resolved/disputed   {'yes' if stalled else 'no'}")
            if stalled:
                status = "STALLED"
                detail = ("The last valid cycle reduced nothing, resolved nothing and "
                          "disputed nothing. Stop now rather than spending the "
                          "remaining budget. Proceed to human plan review.")

    if status is None:
        maxed = len(valid) >= MAX_VALID_CYCLES
        lines.append(f"  D MAX_4_REACHED                VALID_CYCLE_COUNT = {len(valid)}"
                     f"                  {'yes' if maxed else 'no'}")
        if maxed:
            status = "MAX_4_REACHED"
            detail = ("Budget exhausted with findings still open. Proceed to human "
                      "plan review with the unresolved matters exposed.")

    if status is None:
        status = "CONTINUE"
        detail = (f"Repair the plan, produce a new version, and open cycle "
                  f"{dirs[-1][0] + 1:02d} with a new frozen target.")

    lines += ["", f"LOOP_STATUS: {status}", detail]
    if status != "CONTINUE" and cur[DISPUTED]:
        lines.append("")
        lines.append(f"Disputes for adjudication ({len(cur[DISPUTED])}): "
                     f"{fmt(cur[DISPUTED])}")
        lines.append("§7 requires disputes and unresolved findings to reach the human "
                     "as separate lists.")

    print(f"LOOP_STATUS: {status}" if a.quiet else "\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
