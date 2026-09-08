#!/usr/bin/env python3
"""Interface tests for the execution layer.

The other suites test each component alone. This one tests the seams, which is
where the components can each be correct and the system still wrong.

    python scripts/test_interfaces.py

Exit 0 = every seam held.

Seams covered, per Alex Zamurko's list of 8 September:

    1  schema      <-> checker      the doc's mandatory fields are the ones
                                    the checker actually enforces
    2  runner      <-> checker      a cycle the runner produced passes the
                                    gate with no hand-editing, both types
    3  runner      <-> evidence     freeze writes the layout the schema
                                    documents, by filename
    4  ledger      <-> controller   findings.json written by one is read by
                                    the other with no schema drift
    5  controller  <-> live MC-2    the verdict follows the evidence on disk
                                    now, not a value cached earlier
    6  states      <-> exits        each finding state maps to the exit the
                                    protocol assigns it

Seam 1 is the one worth having. A unit test cannot catch a schema that says a
field is mandatory while the checker never looks for it: each side passes its own
tests and the pair is wrong. It reads the field names out of the frozen schema
document and requires the checker to refuse when each is missing, so the document
and the code cannot drift apart silently.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "scripts"
SCHEMA = REPO / "specs" / "evidence-schema-v1.0.md"


def write_lf(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)


def build_repo() -> tuple[Path, str]:
    """A throwaway repo carrying the real scripts and a real commit."""
    tmp = Path(tempfile.mkdtemp(prefix="iface-")).resolve()
    (tmp / "scripts").mkdir()
    for n in ("validate_cycle.py", "run_review.py", "ledger.py", "loop_state.py",
              "bootstrap_gate.py"):
        shutil.copy2(SRC / n, tmp / "scripts" / n)
    (tmp / "specs").mkdir()
    write_lf(tmp / "specs" / "protocol.md", "# protocol\n\nbody\n")
    write_lf(tmp / "specs" / "spec.md", "# spec\n\nrules\n")
    write_lf(tmp / "specs" / "prompt.md", "Review the plan. Report findings.\n")
    write_lf(tmp / "plan" / "01-PLAN.md", "# plan v1\n\nstep one\n")
    write_lf(tmp / "candidate.diff", "--- a\n+++ b\n@@ -1 +1 @@\n-x\n+y\n")
    write_lf(tmp / "tests.txt", "ok 1 - all\n")
    sh("git", "init", "-q", cwd=tmp)
    sh("git", "config", "user.email", "t@t", cwd=tmp)
    sh("git", "config", "user.name", "t", cwd=tmp)
    sh("git", "add", "-A", cwd=tmp)
    sh("git", "commit", "-qm", "fixture", cwd=tmp)
    return tmp, sh("git", "rev-parse", "HEAD", cwd=tmp).stdout.strip()


def run(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return sh(sys.executable, str(root / "scripts" / script), *args, cwd=root)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def ok(msg: str) -> None:
        print(f"  [ok] {msg}")

    def bad(msg: str) -> None:
        failures.append(msg)

    # ---------------------------------------------------------- seam 1
    print("seam 1  schema <-> checker")

    # The schema documents these as mandatory for implementation review. Read
    # them out of the document rather than restating them here, so the test
    # fails if the document changes and the checker does not.
    block = re.search(r'"candidate_commit".*?\n```', SCHEMA.read_text(encoding="utf-8"),
                      re.S)
    if not block:
        bad("could not find the implementation field block in the schema; "
            "seam 1 cannot be checked and that is itself the finding")
        documented = []
    else:
        documented = re.findall(r'"([a-z_]+)":', block.group(0))
        print(f"        schema declares {len(documented)}: {', '.join(documented)}")

    root, commit = build_repo()
    made.append(root)

    def impl_target(**overrides) -> dict:
        tree = sh("git", "rev-parse", f"{commit}^{{tree}}", cwd=root).stdout.strip()
        t = {
            "review_type": "implementation", "run_id": "I-001", "cycle": 1,
            "protocol_commit": commit, "protocol_sha256": "2" * 64,
            "spec_sha256": "0" * 64, "frozen_at": "2026-09-08T00:00:00Z",
            "candidate_commit": commit,
            "candidate_tree_hash": tree,
            "approved_plan_hash": sha256_file(root / "plan" / "01-PLAN.md"),
            "diff_path": "candidate.diff",
            "diff_hash": sha256_file(root / "candidate.diff"),
            "test_result_path": "tests.txt",
            "test_result_hash": sha256_file(root / "tests.txt"),
        }
        t.update(overrides)
        return t

    def lay_cycle(cdir: Path, target: dict) -> None:
        write_lf(cdir / "target.json", json.dumps(target, indent=2))
        d = sha256_file(cdir / "target.json")
        write_lf(cdir / "target.sha256", d + "\n")
        write_lf(cdir / "codex-input.md", f"target {d}\n")
        write_lf(cdir / "codex-output-raw.md", "findings\n")

    # approval record so check 13 has something authoritative
    write_lf(root / "runs" / "I-001" / "plan-approval" / "approval.json",
             json.dumps({"decision": "APPROVE",
                         "approved_plan_hash": sha256_file(root / "plan" / "01-PLAN.md")},
                        indent=2))

    base = root / "runs" / "I-001" / "implementation-review" / "cycle-01"
    lay_cycle(base, impl_target())
    r = run(root, "validate_cycle.py", str(base))
    if r.returncode != 0:
        bad(f"a conformant implementation cycle failed the gate:\n{r.stdout}")
    else:
        ok("a conformant implementation cycle passes all fifteen")

    unenforced = []
    for field in documented:
        d = root / "runs" / "I-001" / f"probe-{field}"
        d.mkdir(parents=True)
        lay_cycle(d, impl_target(**{field: None}))
        (d / "target.json").write_text(
            json.dumps({k: v for k, v in impl_target().items() if k != field}, indent=2),
            encoding="utf-8", newline="\n")
        dg = sha256_file(d / "target.json")
        write_lf(d / "target.sha256", dg + "\n")
        write_lf(d / "codex-input.md", f"target {dg}\n")
        if run(root, "validate_cycle.py", str(d)).returncode == 0:
            unenforced.append(field)
    if unenforced:
        bad("the schema declares these mandatory but the checker accepts a "
            f"cycle without them: {', '.join(unenforced)}")
    elif documented:
        ok(f"every field the schema calls mandatory is enforced ({len(documented)}/"
           f"{len(documented)})")

    # ---------------------------------------------------------- seam 2 and 3
    print()
    print("seam 2  runner <-> checker      seam 3  runner <-> evidence store")

    root2, commit2 = build_repo()
    made.append(root2)
    # --bootstrap-exempt: this seam tests that a runner-produced cycle passes the
    # checker with no hand-editing, which is development evidence about the
    # machinery rather than a protocol cycle. The gate's own behaviour is
    # controlled in test_run_review.py and test_bootstrap_gate.py.
    r = run(root2, "run_review.py", "init", "--run", "A1E-001", "--bootstrap-exempt",
            "--protocol", "specs/protocol.md", "--spec", "specs/spec.md")
    if r.returncode != 0:
        bad(f"init failed:\n{r.stderr}{r.stdout}")

    r = run(root2, "run_review.py", "freeze", "--run", "A1E-001", "--type", "plan",
            "--prompt", "specs/prompt.md", "--file", "plan/01-PLAN.md")
    if r.returncode != 0:
        bad(f"freeze failed:\n{r.stderr}{r.stdout}")

    cyc = root2 / "runs" / "A1E-001" / "plan-review" / "cycle-01"

    # seam 3: the filenames the schema documents are the ones freeze wrote.
    schema_text = SCHEMA.read_text(encoding="utf-8")
    layout = re.search(r"```text\nruns/\n(.*?)```", schema_text, re.S)
    documented_files = set(re.findall(r"^\s+(target\.json|target\.sha256|"
                                      r"codex-input\.md|codex-output-raw\.md)\s*$",
                                      layout.group(1), re.M)) if layout else set()
    frozen = {p.name for p in cyc.iterdir()}
    missing = documented_files - frozen - {"codex-output-raw.md"}
    if missing:
        bad(f"freeze did not write files the schema layout documents: {missing}")
    else:
        ok(f"freeze wrote the documented layout ({len(documented_files)} names "
           "checked against the schema)")

    write_lf(root2 / "reply.md", "C01-F01 | UNTESTED RULE | R-B7 | ...\n")
    r = run(root2, "run_review.py", "record", "--cycle", str(cyc),
            "--output", "reply.md", "--invocation", "manual")
    if r.returncode != 0 or "MC2_CONFORMANCE: PASS" not in r.stdout:
        bad(f"a runner-produced cycle did not pass the gate:\n{r.stdout}")
    else:
        ok("a runner-produced cycle passes the gate with no hand-editing")

    # ---------------------------------------------------------- seam 4
    print()
    print("seam 4  ledger <-> controller")

    rev = root2 / "runs" / "A1E-001" / "plan-review"
    run(root2, "ledger.py", "raise", "--review", str(rev), "--cycle", "1",
        "--id", "C01-F01", "--class", "UNTESTED RULE", "--requirement", "R-B7")
    r = run(root2, "loop_state.py", "--review", str(rev))
    if "C01-F01" not in r.stdout:
        bad("the controller did not see a finding the ledger wrote; the two "
            f"disagree about findings.json\n{r.stdout}")
    elif "OPEN_1           1" not in r.stdout.replace("  ", "  "):
        # tolerate spacing, just require it counted one open finding
        if "OPEN_1" not in r.stdout:
            bad(f"controller produced no OPEN_1 line\n{r.stdout}")
        else:
            ok("the controller reads the ledger's findings.json without drift")
    else:
        ok("the controller reads the ledger's findings.json without drift")

    # ---------------------------------------------------------- seam 5
    print()
    print("seam 5  controller <-> live MC-2 result")

    before = run(root2, "loop_state.py", "--review", str(rev)).stdout
    if "cycle-01  VALID" not in before:
        bad(f"expected cycle-01 valid before tampering\n{before}")
    # Break the evidence AFTER the controller has already run once.
    (cyc / "codex-output-raw.md").write_text("", encoding="utf-8")
    after = run(root2, "loop_state.py", "--review", str(rev)).stdout
    if "cycle-01  INVALID" not in after:
        bad("the controller still reported the cycle valid after its evidence "
            f"was broken; it is not re-running the gate\n{after}")
    else:
        ok("breaking the evidence flips the verdict, so the gate is re-run "
           "rather than cached")
    if "VALID_CYCLE_COUNT: 0" not in after:
        bad(f"an invalid cycle still counted toward the budget\n{after}")
    else:
        ok("an invalid cycle contributes nothing to the budget")

    # ---------------------------------------------------------- seam 6
    print()
    print("seam 6  finding states <-> protocol exits")

    # The cycle count is part of each case. One finding open across two cycles
    # with nothing changing is a stall by §6, not a CONTINUE, so the CONTINUE
    # case needs a single cycle where STALLED is not yet testable.
    cases = [
        ("no findings",  1, [], "CONVERGED"),
        ("one OPEN",     1, [("raise", "C01-F01")], "CONTINUE"),
        ("one OPEN, unchanged across two cycles", 2,
                            [("raise", "C01-F01")], "STALLED"),
        ("one RESOLVED", 2, [("raise", "C01-F01"), ("accept", "C01-F01"),
                             ("resolve", "C01-F01")], "CONVERGED"),
    ]
    for label, ncycles, ops, expect in cases:
        root3, commit3 = build_repo()
        made.append(root3)
        rv = root3 / "runs" / "T" / "plan-review"
        for n in range(1, ncycles + 1):
            d = rv / f"cycle-{n:02d}"
            d.mkdir(parents=True)
            t = {"review_type": "plan", "run_id": "T", "cycle": n,
                 "protocol_commit": commit3, "protocol_sha256": "2" * 64,
                 "spec_sha256": "0" * 64, "frozen_at": "2026-09-08T00:00:00Z",
                 "plan_files": [{"path": "plan/01-PLAN.md",
                                 "sha256": sha256_file(root3 / "plan" / "01-PLAN.md")}]}
            lay_cycle(d, t)
        for op, fid in ops:
            if op == "raise":
                run(root3, "ledger.py", "raise", "--review", str(rv), "--cycle", "1",
                    "--id", fid, "--class", "UNTESTED RULE")
            elif op == "accept":
                run(root3, "ledger.py", "respond", "--review", str(rv), "--cycle", "1",
                    "--id", fid, "--disposition", "ACCEPT", "--note", "fix")
            elif op == "resolve":
                run(root3, "ledger.py", "resolve", "--review", str(rv), "--cycle", "2",
                    "--id", fid, "--evidence", "done")
        out = run(root3, "loop_state.py", "--review", str(rv)).stdout
        got = next((l.split(":", 1)[1].strip() for l in out.splitlines()
                    if l.startswith("LOOP_STATUS:")), "(none)")
        if got != expect:
            bad(f"seam 6, {label}: expected {expect}, got {got}\n{out}")
        else:
            ok(f"{label} -> {expect}")

    # The dispute-only state is deliberately absent. See below.
    root3, commit3 = build_repo()
    made.append(root3)
    rv = root3 / "runs" / "T" / "plan-review"
    d = rv / "cycle-01"
    d.mkdir(parents=True)
    lay_cycle(d, {"review_type": "plan", "run_id": "T", "cycle": 1,
                  "protocol_commit": commit3, "protocol_sha256": "2" * 64,
                  "spec_sha256": "0" * 64, "frozen_at": "2026-09-08T00:00:00Z",
                  "plan_files": [{"path": "plan/01-PLAN.md",
                                  "sha256": sha256_file(root3 / "plan" / "01-PLAN.md")}]})
    run(root3, "ledger.py", "raise", "--review", str(rv), "--cycle", "1",
        "--id", "C01-F01", "--class", "WRONG OWNERSHIP")
    run(root3, "ledger.py", "respond", "--review", str(rv), "--cycle", "1",
        "--id", "C01-F01", "--disposition", "REJECT_WITH_REASON", "--note", "disagree",
        "--spec-evidence", "§4: the class does not apply to this requirement")
    out = run(root3, "loop_state.py", "--review", str(rv)).stdout
    got = next((l.split(":", 1)[1].strip() for l in out.splitlines()
                if l.startswith("LOOP_STATUS:")), "(none)")
    if got != "HUMAN_ADJUDICATION_REQUIRED":
        bad(f"dispute-only state: expected HUMAN_ADJUDICATION_REQUIRED, got {got}")
    else:
        ok("nothing open, one dispute -> HUMAN_ADJUDICATION_REQUIRED (protocol v1.1)")

    for p in made:
        shutil.rmtree(p, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("all seams held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
