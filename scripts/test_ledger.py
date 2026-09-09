#!/usr/bin/env python3
"""Negative controls for the finding ledger and the loop-state controller.

Every refusal in ledger.py and every exit in loop_state.py is demonstrated on a
fixture built to produce exactly that outcome.

The loop controller is the piece where a bug is invisible. A controller that can
never return STALLED simply burns all four cycles every time and nothing looks
wrong, so each exit is shown firing AND shown not firing when it should not.

    python scripts/test_ledger.py

Exit 0 = every expectation held.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent


def write_lf(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)


def make_repo() -> tuple[Path, str]:
    tmp = Path(tempfile.mkdtemp(prefix="ledger-")).resolve()
    (tmp / "scripts").mkdir()
    for n in ("ledger.py", "loop_state.py", "validate_cycle.py"):
        shutil.copy2(SRC / n, tmp / "scripts" / n)
    write_lf(tmp / "plan.md", "# plan\n\nbody\n")
    sh("git", "init", "-q", cwd=tmp)
    sh("git", "config", "user.email", "t@t", cwd=tmp)
    sh("git", "config", "user.name", "t", cwd=tmp)
    sh("git", "add", "-A", cwd=tmp)
    sh("git", "commit", "-qm", "fixture", cwd=tmp)
    return tmp, sh("git", "rev-parse", "HEAD", cwd=tmp).stdout.strip()


def make_cycle(root: Path, review: Path, n: int, commit: str, valid: bool = True) -> None:
    """A cycle directory that passes MC-2, or one deliberately broken."""
    c = review / f"cycle-{n:02d}"
    c.mkdir(parents=True)
    target = {
        "review_type": "plan", "run_id": "T-001", "cycle": n,
        "protocol_commit": commit, "protocol_sha256": "2" * 64,
        "spec_sha256": "0" * 64, "frozen_at": "2026-09-08T00:00:00Z",
        "plan_files": [{"path": "plan.md",
                        "sha256": hashlib.sha256((root / "plan.md").read_bytes()).hexdigest()}],
    }
    snap = c / "artifacts" / "plan.md"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_bytes((root / "plan.md").read_bytes())
    write_lf(c / "target.json", json.dumps(target, indent=2))
    digest = hashlib.sha256((c / "target.json").read_bytes()).hexdigest()
    write_lf(c / "target.sha256", digest + "\n")
    write_lf(c / "codex-input.md", f"target {digest}\n")
    write_lf(c / "codex-output-raw.md", "findings\n")
    write_lf(c / "findings.json", json.dumps({
        "schema": "cycle-findings/1", "cycle": n, "count": 0,
        "zero_findings_asserted": True, "findings": [],
    }, indent=2))
    if not valid:
        # Break check 5: a required file is empty.
        write_lf(c / "codex-output-raw.md", "")


def ledger(root: Path, *args: str) -> subprocess.CompletedProcess:
    return sh(sys.executable, str(root / "scripts" / "ledger.py"), *args, cwd=root)


def loop(root: Path, review: Path) -> subprocess.CompletedProcess:
    return sh(sys.executable, str(root / "scripts" / "loop_state.py"),
              "--review", str(review), cwd=root)


def status_of(out: str) -> str:
    for line in out.splitlines():
        if line.startswith("LOOP_STATUS:"):
            return line.split(":", 1)[1].strip()
    return "(none)"


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def fresh():
        root, commit = make_repo()
        made.append(root)
        return root, commit, root / "runs" / "T-001" / "plan-review"

    def expect_refused(label: str, needle: str, run) -> None:
        r = run()
        if r.returncode == 0:
            failures.append(f"{label}: expected refusal, exit 0\n{r.stdout}")
            return
        text = (r.stderr + r.stdout).lower()
        if needle.lower() not in text:
            failures.append(f"{label}: refused for the wrong reason\n"
                            f"  wanted {needle!r}\n  got {text.strip()[:240]}")
            return
        print(f"  [ok] refused: {label}")

    print("ledger")

    # ---- happy path ----
    root, commit, rev = fresh()
    rev.mkdir(parents=True)
    r = ledger(root, "raise", "--review", str(rev), "--cycle", "1",
               "--id", "C01-F01", "--class", "UNTESTED RULE", "--requirement", "R-B7")
    if r.returncode != 0:
        failures.append(f"raise failed:\n{r.stderr}{r.stdout}")
    else:
        print("  [ok] raise records a finding as OPEN")

    r = ledger(root, "respond", "--review", str(rev), "--cycle", "1",
               "--id", "C01-F01", "--disposition", "ACCEPT", "--note", "will fix")
    data = json.loads((rev / "ledger.json").read_text(encoding="utf-8"))
    if data["findings"]["C01-F01"]["state"] != "OPEN":
        failures.append("ACCEPT changed the state; §5 resolves only once the repair "
                        "is demonstrated in the next review target")
    else:
        print("  [ok] ACCEPT records a disposition and leaves the state OPEN")

    r = ledger(root, "resolve", "--review", str(rev), "--cycle", "2",
               "--id", "C01-F01", "--evidence", "repaired in 02-PLAN.md")
    data = json.loads((rev / "ledger.json").read_text(encoding="utf-8"))
    if r.returncode != 0 or data["findings"]["C01-F01"]["state"] != "RESOLVED":
        failures.append(f"resolve from a later cycle should work:\n{r.stderr}{r.stdout}")
    else:
        print("  [ok] resolve from a later cycle moves OPEN -> RESOLVED")

    # ---- refusals ----
    expect_refused("duplicate finding id", "already exists", lambda: ledger(
        root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
        "--class", "UNTESTED RULE"))

    expect_refused("id declares a different cycle", "persistent", lambda: ledger(
        root, "raise", "--review", str(rev), "--cycle", "2", "--id", "C09-F01",
        "--class", "UNTESTED RULE"))

    expect_refused("respond to a finding never raised", "no such finding", lambda: ledger(
        root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F99",
        "--disposition", "ACCEPT"))

    expect_refused("respond to a RESOLVED finding", "resolved", lambda: ledger(
        root, "respond", "--review", str(rev), "--cycle", "3", "--id", "C01-F01",
        "--disposition", "ACCEPT"))

    root2, commit2, rev2 = fresh()
    rev2.mkdir(parents=True)
    ledger(root2, "raise", "--review", str(rev2), "--cycle", "1", "--id", "C01-F01",
           "--class", "UNTESTED RULE")

    expect_refused("REJECT_WITH_REASON with no reason", "requires --note", lambda: ledger(
        root2, "respond", "--review", str(rev2), "--cycle", "1", "--id", "C01-F01",
        "--disposition", "REJECT_WITH_REASON"))

    # §5 names Reason and Spec evidence as two fields. A rejection carrying only
    # a reason rests on the implementing agent's reading of the spec rather than
    # on the spec, and the human adjudicating the dispute gets half of what the
    # protocol says they should have.
    expect_refused("REJECT_WITH_REASON with a reason but no spec evidence",
                   "requires --spec-evidence", lambda: ledger(
        root2, "respond", "--review", str(rev2), "--cycle", "1", "--id", "C01-F01",
        "--disposition", "REJECT_WITH_REASON", "--note", "I disagree"))

    # Whitespace is not evidence.
    expect_refused("spec evidence that is only whitespace",
                   "requires --spec-evidence", lambda: ledger(
        root2, "respond", "--review", str(rev2), "--cycle", "1", "--id", "C01-F01",
        "--disposition", "REJECT_WITH_REASON", "--note", "I disagree",
        "--spec-evidence", "   "))

    expect_refused("resolve with no prior ACCEPT", "no accept", lambda: ledger(
        root2, "resolve", "--review", str(rev2), "--cycle", "2", "--id", "C01-F01",
        "--evidence", "x"))

    ledger(root2, "respond", "--review", str(rev2), "--cycle", "1", "--id", "C01-F01",
           "--disposition", "ACCEPT", "--note", "will fix")

    expect_refused("resolve in the same cycle as the ACCEPT", "next review target",
                   lambda: ledger(root2, "resolve", "--review", str(rev2), "--cycle", "1",
                                  "--id", "C01-F01", "--evidence", "x"))

    expect_refused("resolve with no evidence", "--evidence is required", lambda: ledger(
        root2, "resolve", "--review", str(rev2), "--cycle", "2", "--id", "C01-F01"))

    expect_refused("two dispositions in one cycle", "exactly one", lambda: ledger(
        root2, "respond", "--review", str(rev2), "--cycle", "1", "--id", "C01-F01",
        "--disposition", "REJECT_WITH_REASON", "--note", "actually no"))

    root3, commit3, rev3 = fresh()
    rev3.mkdir(parents=True)
    ledger(root3, "raise", "--review", str(rev3), "--cycle", "1", "--id", "C01-F01",
           "--class", "WRONG OWNERSHIP")
    ledger(root3, "respond", "--review", str(rev3), "--cycle", "1", "--id", "C01-F01",
           "--disposition", "REJECT_WITH_REASON", "--note", "spec says otherwise",
           "--spec-evidence", "§5: ACCEPT does not resolve")
    data = json.loads((rev3 / "ledger.json").read_text(encoding="utf-8"))
    if data["findings"]["C01-F01"]["state"] != "DISPUTED":
        failures.append("REJECT_WITH_REASON did not produce DISPUTED")
    else:
        print("  [ok] REJECT_WITH_REASON moves OPEN -> DISPUTED")

    expect_refused("respond to a DISPUTED finding", "human adjudication", lambda: ledger(
        root3, "respond", "--review", str(rev3), "--cycle", "2", "--id", "C01-F01",
        "--disposition", "ACCEPT"))

    # ---- OUT OF VOCABULARY is a diagnostic, not a finding ----
    # Ruled 8 September 2026: kept in the review prompts, but with no Finding ID,
    # never in findings.json, never in a state, no effect on loop state. The
    # prompts say so; these show the ledger enforces it, which is the difference
    # between a rule and a request.
    root4, commit4, rev4 = fresh()
    rev4.mkdir(parents=True)

    expect_refused("raise OUT OF VOCABULARY as a finding", "not a finding",
                   lambda: ledger(root4, "raise", "--review", str(rev4),
                                  "--cycle", "1", "--id", "C01-F01",
                                  "--class", "OUT OF VOCABULARY"))

    # Case and spacing must not be a way around it. A refusal that a different
    # capitalisation defeats is a refusal in appearance only.
    expect_refused("raise it in lower case", "not a finding",
                   lambda: ledger(root4, "raise", "--review", str(rev4),
                                  "--cycle", "1", "--id", "C01-F02",
                                  "--class", "out of vocabulary"))

    expect_refused("raise it with surrounding whitespace", "not a finding",
                   lambda: ledger(root4, "raise", "--review", str(rev4),
                                  "--cycle", "1", "--id", "C01-F03",
                                  "--class", "  OUT OF VOCABULARY  "))

    # And nothing was written on the way to being refused.
    if (rev4 / "findings.json").is_file():
        data = json.loads((rev4 / "ledger.json").read_text(encoding="utf-8"))
        if data.get("findings"):
            failures.append("a refused OUT OF VOCABULARY class still left findings "
                            f"in the ledger: {sorted(data['findings'])}")
        else:
            print("  [ok] three refusals left findings.json empty")
    else:
        print("  [ok] three refusals wrote no findings.json at all")

    # The six must still be accepted, or the check above is just a broken raise.
    for i, klass in enumerate(("MISSING REQUIREMENT", "WRONG OWNERSHIP",
                               "NONDETERMINISTIC WHERE D POSSIBLE",
                               "SEMANTIC STEP TOO BROAD", "UNTESTED RULE",
                               "CONTRADICTORY IMPLEMENTATION MAPPING"), start=10):
        r = ledger(root4, "raise", "--review", str(rev4), "--cycle", "1",
                   "--id", f"C01-F{i}", "--class", klass)
        if r.returncode != 0:
            failures.append(f"the ledger refused a legitimate class {klass!r}:\n"
                            f"{r.stderr}{r.stdout}")
            break
    else:
        print("  [ok] all six legitimate classes still accepted")

    # An unknown class still refuses, with the general message rather than the
    # OUT OF VOCABULARY one. Removing argparse's `choices` moved this check into
    # the code, so it needs its own control.
    expect_refused("an invented seventh class", "one of the six",
                   lambda: ledger(root4, "raise", "--review", str(rev4),
                                  "--cycle", "1", "--id", "C01-F20",
                                  "--class", "STYLE NIT"))

    expect_refused("resolve a DISPUTED finding", "human adjudication", lambda: ledger(
        root3, "resolve", "--review", str(rev3), "--cycle", "2", "--id", "C01-F01",
        "--evidence", "x"))

    # ---------------------------------------------------------------- loop
    print()
    print("loop controller")

    def scenario(label: str, n_cycles: int, script, expect: str,
                 invalid: set[int] | None = None) -> None:
        root, commit, rev = fresh()
        rev.mkdir(parents=True)
        for i in range(1, n_cycles + 1):
            make_cycle(root, rev, i, commit, valid=(i not in (invalid or set())))
        script(root, rev)
        r = loop(root, rev)
        got = status_of(r.stdout)
        if got != expect:
            failures.append(f"{label}: expected {expect}, got {got}\n{r.stdout}")
            return
        print(f"  [ok] {expect:<14} {label}")

    def nothing(root, rev):
        pass

    def one_open(root, rev):
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "UNTESTED RULE")

    scenario("no findings at all", 1, nothing, "CONVERGED")

    scenario("one finding still open after cycle 1", 1, one_open, "CONTINUE")

    def resolved_by_2(root, rev):
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "UNTESTED RULE")
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--disposition", "ACCEPT", "--note", "fix")
        ledger(root, "resolve", "--review", str(rev), "--cycle", "2", "--id", "C01-F01",
               "--evidence", "done")
    scenario("everything resolved by cycle 2", 2, resolved_by_2, "CONVERGED")

    def stalled(root, rev):
        # Raised in 1, accepted in 1, nothing demonstrated in 2, nothing new.
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "UNTESTED RULE")
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--disposition", "ACCEPT", "--note", "fix")
    scenario("no reduction, nothing resolved, nothing disputed", 2, stalled, "STALLED")

    def new_dispute(root, rev):
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "UNTESTED RULE")
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F02",
               "--class", "WRONG OWNERSHIP")
        # A NEW dispute in cycle 2 is progress under §6, so this must NOT stall.
        ledger(root, "respond", "--review", str(rev), "--cycle", "2", "--id", "C01-F02",
               "--disposition", "REJECT_WITH_REASON", "--note", "spec disagrees",
               "--spec-evidence", "§4 closed vocabulary")
    scenario("a new dispute counts as progress, so not stalled", 2, new_dispute,
             "CONTINUE")

    # Four cycles that each show progress, so STALLED never fires and the
    # budget is genuinely exhausted. My first attempt at this fixture added one
    # new finding per cycle, which is a stall by §6 and rightly came back
    # STALLED. The fixture was wrong, not the controller.
    def four_with_progress(root, rev, cycles=(1, 2, 3, 4)):
        c1 = cycles[0]
        for i in range(1, 5):
            ledger(root, "raise", "--review", str(rev), "--cycle", str(c1),
                   "--id", f"C{c1:02d}-F{i:02d}", "--class", "UNTESTED RULE")
        # Accept one per cycle and demonstrate it in the next valid cycle.
        for k, cyc in enumerate(cycles[:-1], start=1):
            ledger(root, "respond", "--review", str(rev), "--cycle", str(cyc),
                   "--id", f"C{c1:02d}-F{k:02d}", "--disposition", "ACCEPT",
                   "--note", "fix")
            ledger(root, "resolve", "--review", str(rev), "--cycle", str(cycles[k]),
                   "--id", f"C{c1:02d}-F{k:02d}", "--evidence", "done")

    scenario("budget exhausted, progress every cycle", 4, four_with_progress,
             "MAX_4_REACHED")

    # Exit ordering: STALLED is exit B and MAX 4 is exit C, so a loop that
    # stalls on its fourth valid cycle reports STALLED, not MAX_4_REACHED.
    def four_no_progress(root, rev):
        for c in range(1, 5):
            ledger(root, "raise", "--review", str(rev), "--cycle", str(c),
                   "--id", f"C{c:02d}-F01", "--class", "UNTESTED RULE")
    scenario("STALLED is tested before MAX_4", 4, four_no_progress, "STALLED")

    def four_then_resolved(root, rev):
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "UNTESTED RULE")
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--disposition", "ACCEPT", "--note", "fix")
        ledger(root, "resolve", "--review", str(rev), "--cycle", "4", "--id", "C01-F01",
               "--evidence", "done")
    scenario("CONVERGED takes precedence over MAX_4", 4, four_then_resolved, "CONVERGED")

    # The one that would have bitten: cycle-02 fails the gate, so the four valid
    # cycles are 1, 3, 4, 5 and the budget is reached at directory cycle 5.
    scenario("an invalid cycle does not consume the budget", 5,
             lambda root, rev: four_with_progress(root, rev, cycles=(1, 3, 4, 5)),
             "MAX_4_REACHED", invalid={2})

    # ---- HUMAN_ADJUDICATION_REQUIRED, added in protocol v1.1 ----
    # v1.0 had no exit here: the cycle the dispute landed in returned CONTINUE,
    # telling Claude to repair a plan with nothing open, and the next returned
    # STALLED, which mislabels a loop that finished everything automation could.
    def only_a_dispute(root, rev):
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "WRONG OWNERSHIP")
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--disposition", "REJECT_WITH_REASON", "--note", "spec disagrees",
               "--spec-evidence", "§4 closed vocabulary")
    scenario("nothing open, one dispute outstanding", 1, only_a_dispute,
             "HUMAN_ADJUDICATION_REQUIRED")

    # The exit order is load-bearing: this same fixture returned STALLED under
    # v1.0 because STALLED was tested first.
    scenario("precedes STALLED, which would otherwise swallow it", 2,
             only_a_dispute, "HUMAN_ADJUDICATION_REQUIRED")

    def resolved_and_disputed(root, rev):
        for fid, cls in (("C01-F01", "UNTESTED RULE"), ("C01-F02", "WRONG OWNERSHIP")):
            ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", fid,
                   "--class", cls)
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--disposition", "ACCEPT", "--note", "fix")
        ledger(root, "resolve", "--review", str(rev), "--cycle", "2", "--id", "C01-F01",
               "--evidence", "done")
        ledger(root, "respond", "--review", str(rev), "--cycle", "2", "--id", "C01-F02",
               "--disposition", "REJECT_WITH_REASON", "--note", "spec disagrees",
               "--spec-evidence", "§4 closed vocabulary")
    scenario("everything resolved or disputed", 2, resolved_and_disputed,
             "HUMAN_ADJUDICATION_REQUIRED")

    # It must NOT fire while anything is still open. A dispute alongside an open
    # finding leaves automated repair available, so the loop continues.
    def dispute_plus_open(root, rev):
        for fid, cls in (("C01-F01", "UNTESTED RULE"), ("C01-F02", "WRONG OWNERSHIP")):
            ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", fid,
                   "--class", cls)
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F02",
               "--disposition", "REJECT_WITH_REASON", "--note", "spec disagrees",
               "--spec-evidence", "§4 closed vocabulary")
    scenario("a dispute alongside an open finding does not trigger it", 1,
             dispute_plus_open, "CONTINUE")

    def resolved_in_invalid_cycle(root, rev):
        ledger(root, "raise", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--class", "UNTESTED RULE")
        ledger(root, "respond", "--review", str(rev), "--cycle", "1", "--id", "C01-F01",
               "--disposition", "ACCEPT", "--note", "fix")
        # Demonstrated in cycle 2, which fails the gate. It must not count.
        ledger(root, "resolve", "--review", str(rev), "--cycle", "2", "--id", "C01-F01",
               "--evidence", "done")
    scenario("a resolution recorded in an invalid cycle is ignored", 2,
             resolved_in_invalid_cycle, "CONTINUE", invalid={2})

    for p in made:
        shutil.rmtree(p, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("all controls fired; every refusal is reachable and every exit is "
          "shown firing and not firing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
