#!/usr/bin/env python3
"""The machine-checkable half of the bootstrap exit criteria.

    python scripts/exit_criteria.py

Exit 0 = every check that ran, passed. 1 = at least one failed. 2 = at least
one could not be run, which is neither.

Three answers, not two
----------------------
PASS, FAIL and CANNOT_ESTABLISH. The third exists because this whole layer
keeps finding the same defect in itself: a check that passes for a reason other
than the one it is named for. A check that could not run has established
nothing, and reporting that as a pass is exactly how a review full of findings
reaches CONVERGED.

What this does not do
---------------------
It does not say whether the bootstrap phase can exit. Each condition in
specs/BOOTSTRAP-EXIT-CRITERIA.md has a judgement reserved to Alex Zamurko, and
those judgements are not derivable from anything here: which open defects are
critical, whether the mutation set covers what matters, whether a record is
true rather than merely present, and whether a reviewer's evidence is adequate.
This prints the mechanical half and says plainly that the other half is
missing. A tool that totalled these into a verdict would be making his
decisions quietly, which is the thing the whole protocol is built to prevent.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
SPECS = REPO / "specs"
PROBE = REPO / "_probe"

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "CANNOT_ESTABLISH"


def runs() -> list[Path]:
    base = REPO / "runs"
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir()
                  if (p / "plan-review").is_dir())


def tool(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, *args], cwd=str(REPO),
                       capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


class Condition:
    def __init__(self, cid: str, claim: str, judgement: str):
        self.cid = cid
        self.claim = claim
        self.judgement = judgement
        self.results: list[tuple[str, str, str]] = []

    def check(self, state: str, name: str, detail: str = "") -> None:
        self.results.append((state, name, detail))

    @property
    def verdict(self) -> str:
        states = {s for s, _, _ in self.results}
        if not self.results:
            return UNKNOWN
        if FAIL in states:
            return FAIL
        if UNKNOWN in states:
            return UNKNOWN
        return PASS

    def report(self) -> None:
        print(f"\n{self.cid}  {self.claim}")
        print(f"  machine checks: {self.verdict}")
        for state, name, detail in self.results:
            mark = {PASS: "ok  ", FAIL: "FAIL", UNKNOWN: "?   "}[state]
            print(f"    [{mark}] {name}")
            if detail:
                for line in detail.splitlines():
                    print(f"           {line}")
        print(f"  judgement reserved to Alex Zamurko: {self.judgement}")


# ---------------------------------------------------------------- EC-1
def ec1() -> Condition:
    c = Condition(
        "EC-1", "no critical open defect",
        "which open defects are critical")

    # A run that says CONVERGED while findings are open at its governing
    # boundary is the failure this condition exists for. A run that refuses to
    # compute a state is not a failure of this condition: refusing is the
    # correct behaviour and EC-3 is where an unreadable record is judged.
    for run in runs():
        rel = f"runs/{run.name}/plan-review"
        rc, out = tool(str(SCRIPTS / "loop_state.py"), "--review", rel,
                       "--development", "--json")
        if rc != 0:
            c.check(UNKNOWN, f"{run.name}: controller refuses, so convergence "
                             f"cannot be judged here",
                    out.strip().splitlines()[0] if out.strip() else "")
            continue
        try:
            proj = json.loads(out)
        except json.JSONDecodeError:
            c.check(UNKNOWN, f"{run.name}: the controller's JSON could not be "
                             f"read")
            continue
        if not proj.get("sets_established"):
            c.check(UNKNOWN, f"{run.name}: no finding sets were established")
            continue
        open_ids = proj.get("open", [])
        if proj.get("status") == "CONVERGED" and open_ids:
            c.check(FAIL, f"{run.name}: CONVERGED with findings open",
                    "open: " + ", ".join(open_ids))
        else:
            c.check(PASS, f"{run.name}: {proj.get('status')} with "
                          f"{len(open_ids)} open at n="
                          f"{proj.get('governing_boundary')}")

    # Every blocking item must be classified, and the classification file must
    # name the condition it blocks. An unclassified finding is not a pass and
    # not a failure: it is a judgement nobody has made yet.
    bf = SPECS / "blocking-defects.json"
    if not bf.is_file():
        c.check(UNKNOWN, "no blocking-defect classification exists",
                "EC-1 cannot be evaluated without it. See "
                "specs/BOOTSTRAP-EXIT-CRITERIA.md.")
    else:
        try:
            blocking = json.loads(bf.read_text(encoding="utf-8")).get(
                "blocking", {})
        except json.JSONDecodeError as e:
            c.check(UNKNOWN, f"the blocking-defect classification is not valid "
                             f"JSON: {e}")
            return c

        # The first version of this counted the blocking defects and called
        # that a pass. It reported EC-1 PASS on 10 October with all four of
        # them open, because counting a list is not asking whether anything on
        # it is closed. A condition named "no critical open defect" that never
        # looks at whether the critical defects are open is a check passing
        # for a reason other than the one it is named for, which is the defect
        # class this entire document exists to prevent, written into the
        # document itself.
        #
        # A defect is closed here when a reviewer has examined its repair,
        # which is EC-4's bar and Alex Zamurko's: "Behavioural claims require
        # independent execution." So EC-1 and EC-4 move together, and that is
        # correct rather than redundant: EC-4 asks whether the evidence
        # exists, EC-1 asks whether anything critical is still open. Today the
        # answer to both is no and they should not disagree.
        _open = sorted(k for k, v in blocking.items()
                       if not v.get("independently_examined_in_cycle"))
        if not blocking:
            c.check(UNKNOWN, "nothing is classified as blocking",
                    "An empty list is not the same as nothing being critical. "
                    "Either no\nfinding has been classified yet, or the file "
                    "is wrong.")
        elif _open:
            c.check(FAIL, f"{len(_open)} of {len(blocking)} blocking "
                          f"defect(s) are still open",
                    ", ".join(_open) + "\nEach has a repair that no reviewer "
                    "has examined. Until one has, this\ncondition is not met.")
        else:
            c.check(PASS, f"all {len(blocking)} blocking defect(s) closed")
    return c


# ---------------------------------------------------------------- EC-2
def ec2() -> Condition:
    c = Condition(
        "EC-2", "reliable verification",
        "whether the mutation set covers the repairs that matter")

    suites = sorted(SCRIPTS.glob("test_*.py"))
    red = []
    for s in suites:
        rc, _ = tool(str(s))
        if rc != 0:
            red.append(s.name)
    if red:
        c.check(FAIL, f"{len(red)} of {len(suites)} suite(s) red",
                ", ".join(red))
    else:
        c.check(PASS, f"all {len(suites)} suites pass")

    # The sweep is not run here: it takes hours and this script is meant to be
    # runnable on demand. Its recorded result is read instead, with the one
    # guard that makes a recorded result worth anything, which is that it must
    # be newer than the code it claims to cover. A sweep from before the last
    # change to scripts/ says nothing about what is there now.
    sweep = PROBE / "full-sweep.txt"
    if not sweep.is_file():
        c.check(UNKNOWN, "no recorded mutation sweep",
                "run `python _probe/mutate_repairs.py > _probe/full-sweep.txt`")
    else:
        r = subprocess.run(["git", "-C", str(REPO), "log", "-1",
                            "--format=%ct", "--", "scripts", "_probe"],
                           capture_output=True, text=True)
        try:
            newest_code = int(r.stdout.strip())
        except ValueError:
            newest_code = None
        text = sweep.read_text(encoding="utf-8", errors="replace")
        stale = (newest_code is not None
                 and sweep.stat().st_mtime < newest_code)
        if stale:
            c.check(UNKNOWN, "the recorded sweep predates the last change to "
                             "the code it covers",
                    "It is not evidence about the current source. Re-run it.")
        elif not text.strip():
            c.check(UNKNOWN, "the recorded sweep is empty")
        else:
            bad = [ln.strip() for ln in text.splitlines()
                   if any(k in ln for k in ("[BROKEN PROBE]", "[MISSED]",
                                            "[WRONG CONTROL]", "[CRASHED]",
                                            "[COULD NOT RUN]", "[ESCAPED]"))]
            if bad:
                c.check(FAIL, f"{len(bad)} repair(s) not demonstrably watched",
                        "\n".join(bad[:6]))
            elif "[caught]" not in text:
                c.check(UNKNOWN, "the recorded sweep reports nothing caught",
                        "An empty result is not a clean one.")
            else:
                n = text.count("[caught]")
                c.check(PASS, f"{n} repair(s) go red when removed, each in a "
                              f"control that names it")

    # The tool must leave the repository as it found it. Since 9 October the
    # probe works in a disposable checkout, so this is an assertion that the
    # isolation held rather than that a restore succeeded.
    r = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain",
                        "--", "scripts", "_probe"],
                       capture_output=True, text=True)
    dirty = [ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip()
             and not ln.strip().endswith("full-sweep.txt")]
    if dirty:
        # Said as what it is rather than as the worst thing it could be. The
        # first wording was "source differs from HEAD after testing", which
        # reads as the probe having escaped its sandbox, and on 10 October it
        # fired because the implementing agent had edited a file and not
        # committed it. Two causes, one message, and it named the alarming
        # one. The probe has its own check for escape and says both
        # possibilities out loud; this one is about something narrower.
        c.check(FAIL, "the source on disk is not the source any sweep "
                      "describes",
                ", ".join(dirty) +
                "\nThese differ from HEAD, and a recorded sweep describes a "
                "commit. Either\ncommit them and re-sweep, or discard them. "
                "This is not evidence of the probe\nreaching the real tree; "
                "the probe checks that itself and reports it separately.")
    else:
        c.check(PASS, "the working tree matches HEAD, so a sweep of HEAD "
                      "describes what is here")

    r = subprocess.run(["git", "-C", str(REPO), "worktree", "list",
                        "--porcelain"], capture_output=True, text=True)
    left = [ln[len("worktree "):].strip() for ln in r.stdout.splitlines()
            if ln.startswith("worktree ")
            and "epistemicos-probe-" in ln]
    if left:
        c.check(FAIL, f"{len(left)} disposable checkout(s) left behind",
                "\n".join(left) +
                "\n(Each path ends in the pid of the run that made it. If a "
                "sweep is running\nright now, this is that run's checkout and "
                "not a leftover: finish it and re-run.)")
    else:
        c.check(PASS, "no disposable checkout remains")
    return c


# ---------------------------------------------------------------- EC-3
def ec3() -> Condition:
    c = Condition(
        "EC-3", "complete audit records",
        "whether a record is true, as distinct from present")

    # The gate is run now rather than quoted. A recorded PASS is a claim about
    # the past; this asks the gate what it says today.
    cycles, failed = 0, []
    for run in runs():
        for cyc in sorted((run / "plan-review").glob("cycle-*")):
            if not cyc.is_dir():
                continue
            cycles += 1
            rc, out = tool(str(SCRIPTS / "validate_cycle.py"), str(cyc))
            if rc != 0 or "MC2_CONFORMANCE: PASS" not in out:
                failed.append(f"{run.name}/{cyc.name}")
    if not cycles:
        c.check(UNKNOWN, "no frozen cycles found to check")
    elif failed:
        c.check(FAIL, f"{len(failed)} of {cycles} frozen cycle(s) fail MC-2 "
                      f"today", ", ".join(failed))
    else:
        c.check(PASS, f"all {cycles} frozen cycle(s) pass MC-2 when run now")

    # Every superseded capture needs an approval bound by hash, and the
    # displaced capture must still be there. The recorder enforces this at the
    # moment of supersession; this asks whether it is still true afterwards.
    sup, bad = 0, []
    for run in runs():
        for cyc in sorted((run / "plan-review").glob("cycle-*")):
            log = cyc / "capture-log.json"
            if not log.is_file():
                continue
            try:
                d = json.loads(log.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                bad.append(f"{cyc.name}: capture log is not valid JSON")
                continue
            displaced = [a for a in d.get("invalidated", [])
                         if a.get("superseded_by")]
            if not displaced:
                continue
            sup += 1
            ap = cyc / "capture-supersession-approval.json"
            if not ap.is_file():
                bad.append(f"{cyc.name}: a capture was superseded with no "
                           f"approval record")
                continue
            try:
                rec = json.loads(ap.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                bad.append(f"{cyc.name}: the approval is not valid JSON")
                continue
            missing = [k for k in ("authorized_by", "reason", "at",
                                   "superseded_sha256", "superseding_sha256")
                       if not str(rec.get(k, "")).strip()]
            if missing:
                bad.append(f"{cyc.name}: approval missing "
                           f"{', '.join(missing)}")
            for a in displaced:
                kept = cyc / "captures" / f"attempt-{a.get('attempt'):02d}"
                if not (kept / "raw.md").is_file():
                    bad.append(f"{cyc.name}: the displaced capture "
                               f"attempt-{a.get('attempt')} was not kept")
    if bad:
        c.check(FAIL, "supersession records are incomplete", "\n".join(bad))
    elif sup:
        c.check(PASS, f"{sup} supersession(s), each approved and each keeping "
                      f"the capture it displaced")
    else:
        c.check(PASS, "no capture has been superseded")

    # The register's own obligation, checked rather than trusted.
    reg = REPO / "registers" / "implementer-disclosed.json"
    required = ("description", "discovery_source", "affected_component",
                "severity", "state", "proposed_repair", "evidence")
    if not reg.is_file():
        c.check(UNKNOWN, "the implementer-disclosed register is missing")
    else:
        try:
            rg = json.loads(reg.read_text(encoding="utf-8"))
            thin = [f"{k}.{f}" for k, v in rg.get("entries", {}).items()
                    for f in required if not v.get(f)]
            if thin:
                c.check(FAIL, "register entries missing required fields",
                        ", ".join(thin))
            else:
                c.check(PASS, f"{len(rg.get('entries', {}))} register "
                              f"entries, each complete")
        except json.JSONDecodeError as e:
            c.check(UNKNOWN, f"the register is not valid JSON: {e}")
    return c


# ---------------------------------------------------------------- EC-4
def ec4() -> Condition:
    c = Condition(
        "EC-4", "independent verification of blocking repairs",
        "whether each reviewer's evidence is adequate for a blocking item")

    bf = SPECS / "blocking-defects.json"
    if not bf.is_file():
        c.check(UNKNOWN, "no blocking-defect classification to check against")
        return c
    try:
        blocking = json.loads(bf.read_text(encoding="utf-8")).get("blocking", {})
    except json.JSONDecodeError as e:
        c.check(UNKNOWN, f"the classification is not valid JSON: {e}")
        return c

    for name, item in sorted(blocking.items()):
        cyc = item.get("independently_examined_in_cycle")
        if not cyc:
            c.check(UNKNOWN, f"{name}: no reviewer has examined its repair",
                    "Its repair landed on "
                    f"{item.get('repair_landed', 'an unrecorded date')}, after "
                    "the last frozen cycle.")
        else:
            c.check(PASS, f"{name}: examined in {cyc}")
    return c


def frozen_criteria() -> str | None:
    """Refuse everything if the criteria are not the ones that were frozen.

    A document that says "frozen" and is editable without consequence says
    nothing. This makes the word mean something: the digest recorded beside it
    is checked before any condition is reported, and a mismatch stops the run
    rather than producing a verdict against criteria nobody agreed to.

    It is not tamper-proofing. Anyone who can edit the document can edit the
    digest, which is AR-1 and is accepted for bootstrap. What it does is make
    a change to the bar a deliberate act with two files in the diff, rather
    than something that can drift under a decision while nobody is looking.
    """
    doc = SPECS / "BOOTSTRAP-EXIT-CRITERIA.md"
    rec = SPECS / "BOOTSTRAP-EXIT-CRITERIA.sha256"
    if not doc.is_file():
        return "the exit criteria document is missing"
    if not rec.is_file():
        return ("no recorded digest for the exit criteria, so there is "
                "nothing to say\n  which version this run is checking "
                "against")
    want = rec.read_text(encoding="utf-8").split()[0].strip()
    got = hashlib.sha256(doc.read_bytes()).hexdigest()
    if want != got:
        return ("the exit criteria have changed since they were frozen.\n"
                f"  frozen   {want}\n  on disk  {got}\n\n"
                "  Nothing is reported against criteria that are not the ones "
                "agreed. If the\n  change is intended, it takes a new version "
                "and a new digest, with the reason\n  recorded, rather than "
                "an edit. If it is not intended, find out what changed\n  "
                "before trusting anything else in this repository.")
    return None


def main() -> int:
    print("bootstrap exit criteria, machine-checkable half")
    print(f"  {REPO}")
    print("  specs/BOOTSTRAP-EXIT-CRITERIA.md holds the judgements this "
          "cannot make.")

    _bad = frozen_criteria()
    if _bad:
        print(f"\n  [CANNOT RUN] {_bad}")
        return 2
    print("  criteria digest matches the frozen record.")

    conditions = [ec1(), ec2(), ec3(), ec4()]
    for c in conditions:
        c.report()

    verdicts = [c.verdict for c in conditions]
    print("\n" + "-" * 68)
    for c in conditions:
        print(f"  {c.cid}  {c.verdict}")

    print("\n  NO OVERALL VERDICT IS PRINTED HERE, and that is deliberate.")
    print("  Each condition above has a judgement reserved to Alex Zamurko, "
          "and none of")
    print("  them is derivable from anything this script can read. Totalling "
          "the four")
    print("  into a yes would be this tool making his decision quietly, "
          "which is the")
    print("  behaviour the protocol exists to prevent.")

    if FAIL in verdicts:
        return 1
    if UNKNOWN in verdicts:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
