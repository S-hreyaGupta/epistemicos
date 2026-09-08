#!/usr/bin/env python3
"""Negative controls for the MC-2 conformance gate.

Every one of the ten checks is demonstrated failing on a fixture built to break
exactly that check, and a clean fixture is demonstrated passing.

A gate whose checks are never shown to fail is the defect class the v1.0
gate-hardening milestone found thirteen times: a check that cannot come back
false reports success while testing nothing. These are the negative controls.

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

REPO = Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "scripts" / "validate_cycle.py"
# A commit that exists in this repository; check 8 resolves against it.
KNOWN_COMMIT = "ef0565b5d6715dded817d47a8abba99ff514f3f5"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_cycle(root: Path, mutate=None, extra_sibling: dict | None = None) -> Path:
    """A conformant plan-review cycle, optionally mutated to break one check."""
    review = root / "plan-review"
    cycle = review / "cycle-01"
    cycle.mkdir(parents=True)

    plan = root / "plan.md"
    plan.write_text("# plan\n\nbody\n", encoding="utf-8")

    target = {
        "review_type": "plan",
        "run_id": "A1E-001",
        "cycle": 1,
        "protocol_commit": KNOWN_COMMIT,
        "protocol_sha256": "2" * 64,
        "spec_sha256": "0" * 64,
        "frozen_at": "2026-09-08T13:40:00Z",
        "plan_files": [{"path": str(plan), "sha256": sha256_file(plan)}],
    }
    if mutate:
        target = mutate(target, cycle) or target

    (cycle / "target.json").write_text(json.dumps(target, indent=2), encoding="utf-8")
    digest = sha256_file(cycle / "target.json")
    (cycle / "target.sha256").write_text(digest + "\n", encoding="utf-8")
    (cycle / "codex-input.md").write_text(
        f"Review target {digest}\n\n(plan contents)\n", encoding="utf-8")
    (cycle / "codex-output-raw.md").write_text(
        "C01-F01 | UNTESTED RULE | R-B7 | ...\n", encoding="utf-8")

    if extra_sibling is not None:
        sib = review / "cycle-02"
        sib.mkdir()
        (sib / "target.json").write_text(json.dumps(extra_sibling, indent=2), encoding="utf-8")

    return cycle


def run(cycle: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(VALIDATOR), str(cycle)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


def failed_checks(output: str) -> set[int]:
    out = set()
    for line in output.splitlines():
        line = line.strip()
        if "[FAIL]" in line:
            out.add(int(line.split(".", 1)[0]))
    return out


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="mc2-"))
    failures: list[str] = []

    try:
        # Clean fixture must pass, or every negative below is meaningless.
        cycle = build_cycle(tmp / "clean")
        rc, out = run(cycle)
        if rc != 0:
            failures.append(f"clean fixture did not pass:\n{out}")
        else:
            print("  [ok] clean fixture passes")

        def expect_fail(label: str, check: int, setup) -> None:
            d = tmp / label.replace(" ", "_")
            cycle = setup(d)
            rc, out = run(cycle)
            if rc == 0:
                failures.append(f"{label}: expected FAIL, gate passed")
                return
            got = failed_checks(out)
            if check not in got:
                failures.append(f"{label}: expected check {check} to fail, failed {sorted(got)}")
                return
            print(f"  [ok] check {check:>2} fails on: {label}")

        expect_fail("missing required file", 4, lambda d: (
            lambda c: ((c / "codex-output-raw.md").unlink(), c)[1])(build_cycle(d)))

        expect_fail("empty required file", 5, lambda d: (
            lambda c: ((c / "codex-input.md").write_text("", encoding="utf-8"), c)[1])(build_cycle(d)))

        expect_fail("target.sha256 does not match target.json", 6, lambda d: (
            lambda c: ((c / "target.sha256").write_text("a" * 64 + "\n", encoding="utf-8"), c)[1]
        )(build_cycle(d)))

        expect_fail("duplicate cycle identifier", 7, lambda d: build_cycle(
            d, extra_sibling={"review_type": "plan", "run_id": "A1E-001", "cycle": 1}))

        expect_fail("referenced commit does not resolve", 8, lambda d: build_cycle(
            d, mutate=lambda t, c: {**t, "protocol_commit": "deadbeef" * 5}))

        expect_fail("declared artifact hash is wrong", 9, lambda d: build_cycle(
            d, mutate=lambda t, c: {**t, "plan_files": [
                {**t["plan_files"][0], "sha256": "b" * 64}]}))

        expect_fail("review_type outside the closed set", 9, lambda d: build_cycle(
            d, mutate=lambda t, c: {**t, "review_type": "other"}))

        expect_fail("implementation review missing mandatory hashes", 9, lambda d: build_cycle(
            d, mutate=lambda t, c: {k: v for k, v in
                                    {**t, "review_type": "implementation"}.items()
                                    if k != "plan_files"}))

        expect_fail("codex-input.md does not carry the target hash", 10, lambda d: (
            lambda c: ((c / "codex-input.md").write_text(
                "Review the plan.\n", encoding="utf-8"), c)[1])(build_cycle(d)))

        expect_fail("target.json is not valid JSON", 7, lambda d: (
            lambda c: ((c / "target.json").write_text("{ not json", encoding="utf-8"), c)[1]
        )(build_cycle(d)))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("all negative controls fired; every check is falsifiable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
