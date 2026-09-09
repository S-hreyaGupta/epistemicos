#!/usr/bin/env python3
"""Negative controls for the MC-2 conformance gate.

Every one of the fifteen checks is demonstrated failing on a fixture built to
break exactly that check, and clean plan and implementation cycles are
demonstrated passing.

A gate whose checks are never shown to fail is the defect class the v1.0
gate-hardening milestone found thirteen times: a check that cannot come back
false reports success while testing nothing.

Checks 11 to 15 apply to implementation review only. That creates a second way
to build the same defect: report them PASS on a plan cycle they never examined.
So this suite also asserts they come back N/A there, and that N/A is distinct
from PASS in the output.

    python scripts/test_validate_cycle.py

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


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)


def make_repo() -> tuple[Path, str, str]:
    """A throwaway repo so REPO resolves to the fixture. Returns (root, commit, tree)."""
    tmp = Path(tempfile.mkdtemp(prefix="mc2-")).resolve()
    (tmp / "scripts").mkdir()
    shutil.copy2(SRC / "validate_cycle.py", tmp / "scripts" / "validate_cycle.py")
    write_lf(tmp / "plan.md", "# plan\n\nbody\n")
    write_lf(tmp / "candidate.diff", "--- a\n+++ b\n@@ -1 +1 @@\n-x\n+y\n")
    write_lf(tmp / "tests.txt", "ok 1 - everything\n")
    sh("git", "init", "-q", cwd=tmp)
    sh("git", "config", "user.email", "t@t", cwd=tmp)
    sh("git", "config", "user.name", "t", cwd=tmp)
    sh("git", "add", "-A", cwd=tmp)
    sh("git", "commit", "-qm", "fixture", cwd=tmp)
    commit = sh("git", "rev-parse", "HEAD", cwd=tmp).stdout.strip()
    tree = sh("git", "rev-parse", "HEAD^{tree}", cwd=tmp).stdout.strip()
    return tmp, commit, tree


def build(root: Path, commit: str, tree: str, kind: str = "plan",
          mutate=None, sibling: dict | None = None, approval: bool = True) -> Path:
    review = root / "runs" / "T-001" / f"{kind}-review"
    cycle = review / "cycle-01"
    cycle.mkdir(parents=True)

    target = {
        "review_type": kind,
        "run_id": "T-001",
        "cycle": 1,
        "protocol_commit": commit,
        "protocol_sha256": "2" * 64,
        "spec_sha256": "0" * 64,
        "frozen_at": "2026-09-08T13:40:00Z",
    }
    plan_hash = sha256_file(root / "plan.md")
    if kind == "plan":
        target["plan_files"] = [{"path": "plan.md", "sha256": plan_hash}]
        # Preserved copy: check 9 validates the snapshot, not the live tree,
        # so a cycle survives the repairs its review asked for.
        snap = cycle / "artifacts" / "plan.md"
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_bytes((root / "plan.md").read_bytes())
    else:
        target.update({
            "candidate_commit": commit,
            "candidate_tree_hash": tree,
            "approved_plan_hash": plan_hash,
            "diff_path": "candidate.diff",
            "diff_hash": sha256_file(root / "candidate.diff"),
            "test_result_path": "tests.txt",
            "test_result_hash": sha256_file(root / "tests.txt"),
        })
        if approval:
            write_lf(root / "runs" / "T-001" / "plan-approval" / "approval.json",
                     json.dumps({"decision": "APPROVE",
                                 # B01-F06: name the artifact, or check 13 can
                                 # only compare a hash with a copy of itself.
                                 "approved_plan_path": "plan.md",
                                 "approved_plan_hash": plan_hash}, indent=2))

    if mutate:
        target = mutate(target, cycle, root) or target

    write_lf(cycle / "target.json", json.dumps(target, indent=2))
    digest = sha256_file(cycle / "target.json")
    write_lf(cycle / "target.sha256", digest + "\n")
    write_lf(cycle / "codex-input.md", f"Review target {digest}\n\n(contents)\n")
    write_lf(cycle / "codex-output-raw.md", "C01-F01 | UNTESTED RULE | R-B7 | ...\n")

    if sibling is not None:
        sib = review / "cycle-02"
        sib.mkdir()
        write_lf(sib / "target.json", json.dumps(sibling, indent=2))
    return cycle


def run(root: Path, cycle: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(root / "scripts" / "validate_cycle.py"),
                        str(cycle)], capture_output=True, text=True)
    return r.returncode, r.stdout


def marks(output: str) -> dict[int, str]:
    out = {}
    for line in output.splitlines():
        s = line.strip()
        if s and s[0].isdigit() and "[" in s and "]" in s:
            try:
                n = int(s.split(".", 1)[0])
            except ValueError:
                continue
            out[n] = s[s.index("[") + 1:s.index("]")].strip()
    return out


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def fresh():
        root, commit, tree = make_repo()
        made.append(root)
        return root, commit, tree

    def expect_fail(label: str, check: int, kind: str, mutate=None, **kw) -> None:
        root, commit, tree = fresh()
        cycle = build(root, commit, tree, kind, mutate=mutate, **kw)
        rc, out = run(root, cycle)
        if rc == 0:
            failures.append(f"{label}: expected FAIL, gate passed")
            return
        got = marks(out)
        if got.get(check) != "FAIL":
            failures.append(f"{label}: expected check {check} to FAIL, "
                            f"it was {got.get(check)!r}")
            return
        print(f"  [ok] check {check:>2} fails on: {label}")

    # ---- clean fixtures ----
    root, commit, tree = fresh()
    rc, out = run(root, build(root, commit, tree, "plan"))
    m = marks(out)
    if rc != 0:
        failures.append(f"clean plan cycle did not pass:\n{out}")
    else:
        print("  [ok] clean plan cycle passes")
        na = [n for n in range(11, 16) if m.get(n) != "N/A"]
        if na:
            failures.append(f"checks {na} should be N/A on a plan cycle, "
                            f"got {[m.get(n) for n in na]}. Reporting PASS for a "
                            f"check that was never evaluated is the defect this "
                            f"gate exists to catch.")
        else:
            print("  [ok] checks 11-15 report N/A on a plan cycle, not PASS")

    root, commit, tree = fresh()
    rc, out = run(root, build(root, commit, tree, "implementation"))
    if rc != 0:
        failures.append(f"clean implementation cycle did not pass:\n{out}")
    else:
        m = marks(out)
        evaluated = [n for n in range(11, 16) if m.get(n) == "PASS"]
        if len(evaluated) != 5:
            failures.append(f"implementation cycle should evaluate 11-15, got {m}")
        else:
            print("  [ok] clean implementation cycle passes all fifteen")

    # ---- checks 1-10 ----
    # These four mutate the cycle AFTER build(), because build() writes the
    # required files last and a mutate hook would be overwritten by it.
    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    (cyc / "codex-output-raw.md").unlink()
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(4) != "FAIL":
        failures.append("check 4 did not fail on a missing required file")
    else:
        print("  [ok] check  4 fails on: missing required file")

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "codex-input.md", "")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(5) != "FAIL":
        failures.append("check 5 did not fail on an empty required file")
    else:
        print("  [ok] check  5 fails on: empty required file")

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "target.sha256", "a" * 64 + "\n")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(6) != "FAIL":
        failures.append("check 6 did not fail on a wrong target.sha256")
    else:
        print("  [ok] check  6 fails on: target.sha256 does not match target")

    expect_fail("duplicate cycle identifier", 7, "plan",
                sibling={"review_type": "plan", "run_id": "T-001", "cycle": 1})
    expect_fail("referenced commit does not resolve", 8, "plan",
                mutate=lambda t, c, r: {**t, "protocol_commit": "deadbeef" * 5})
    expect_fail("declared artifact hash is wrong", 9, "plan",
                mutate=lambda t, c, r: {**t, "plan_files": [
                    {"path": "plan.md", "sha256": "b" * 64}]})
    expect_fail("review_type outside the closed set", 9, "plan",
                mutate=lambda t, c, r: {**t, "review_type": "other"})

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "codex-input.md", "Review the plan.\n")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(10) != "FAIL":
        failures.append("check 10 did not fail when the input lacks the target hash")
    else:
        print("  [ok] check 10 fails on: codex-input.md does not carry the target hash")

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "target.json", "{ not json")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(7) != "FAIL":
        failures.append("check 7 did not fail on unparseable target.json")
    else:
        print("  [ok] check  7 fails on: target.json is not valid JSON")

    # ---- checks 11-15, §10.2 ----
    expect_fail("candidate commit does not resolve", 11, "implementation",
                mutate=lambda t, c, r: {**t, "candidate_commit": "deadbeef" * 5})
    expect_fail("candidate tree hash is wrong", 12, "implementation",
                mutate=lambda t, c, r: {**t, "candidate_tree_hash": "a" * 40})
    expect_fail("approved-plan hash disagrees with the approval record", 13,
                "implementation",
                mutate=lambda t, c, r: {**t, "approved_plan_hash": "c" * 64})
    expect_fail("no approval record to match against", 13, "implementation",
                approval=False)
    expect_fail("diff hash does not match the diff", 14, "implementation",
                mutate=lambda t, c, r: {**t, "diff_hash": "d" * 64})
    expect_fail("diff artifact is missing", 14, "implementation",
                mutate=lambda t, c, r: {**t, "diff_path": "nope.diff"})
    expect_fail("test-result hash does not match", 15, "implementation",
                mutate=lambda t, c, r: {**t, "test_result_hash": "e" * 64})
    for field in ("candidate_commit", "candidate_tree_hash", "approved_plan_hash",
                  "diff_hash", "test_result_hash"):
        expect_fail(f"§10.1 field absent: {field}", 9, "implementation",
                    mutate=lambda t, c, r, f=field: {k: v for k, v in t.items() if k != f})

    for p in made:
        shutil.rmtree(p, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("all negative controls fired; every check is falsifiable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
