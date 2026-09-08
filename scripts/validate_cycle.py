#!/usr/bin/env python3
"""MC-2 conformance gate.

Checks one review cycle against specs/evidence-schema-v1.0.md and the ten checks
in specs/implementation-review-protocol-v1.0.md MC-2.

    python scripts/validate_cycle.py runs/A1E-001/plan-review/cycle-01

Exit 0 = PASS, exit 1 = FAIL, exit 2 = the checker could not run.

A FAIL means REVIEW_CYCLE_STATUS = INVALID: the cycle cannot support a finding
and cannot count toward CONVERGED, STALLED, MAX_4_REACHED, or the four-cycle
budget. It is repaired and rerun, not interpreted.

Written under the anti-whitelist rule: every check derives its expectation from
the schema, and nothing passes because a previous run accepted it.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = ("target.json", "target.sha256", "codex-input.md", "codex-output-raw.md")
HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")

COMMON_FIELDS = ("review_type", "run_id", "cycle", "protocol_commit",
                 "protocol_sha256", "spec_sha256", "frozen_at")


class Result:
    def __init__(self) -> None:
        self.checks: list[tuple[int, str, bool, str]] = []

    def add(self, n: int, name: str, ok: bool, detail: str = "") -> bool:
        self.checks.append((n, name, ok, detail))
        return ok

    @property
    def passed(self) -> bool:
        return all(ok for _, _, ok, _ in self.checks)

    def report(self, cycle_dir: Path) -> str:
        lines = [f"MC-2 conformance — {cycle_dir}", ""]
        for n, name, ok, detail in self.checks:
            mark = "PASS" if ok else "FAIL"
            lines.append(f"  {n:>2}. [{mark}] {name}")
            if detail:
                lines.append(f"          {detail}")
        lines += ["", f"MC2_CONFORMANCE: {'PASS' if self.passed else 'FAIL'}"]
        if not self.passed:
            lines.append("REVIEW_CYCLE_STATUS: INVALID")
            lines.append("This cycle does not count toward the four-cycle budget "
                         "or any loop state. Repair the evidence and rerun.")
        return "\n".join(lines)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit_exists(repo_root: Path, commit: str) -> bool:
    try:
        r = subprocess.run(["git", "-C", str(repo_root), "cat-file", "-e", f"{commit}^{{commit}}"],
                           capture_output=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def validate(cycle_dir: Path, repo_root: Path) -> Result:
    r = Result()

    # 1-4. required files exist
    missing = [n for n in REQUIRED_FILES if not (cycle_dir / n).is_file()]
    for i, name in enumerate(REQUIRED_FILES, start=1):
        r.add(i, f"{name} exists", (cycle_dir / name).is_file(),
              "" if (cycle_dir / name).is_file() else "not found")
    if missing:
        r.add(5, "all required files non-empty", False, f"skipped, missing: {', '.join(missing)}")
        for n in range(6, 11):
            r.add(n, "(not reached)", False, "earlier checks failed")
        return r

    # 5. non-empty
    empty = [n for n in REQUIRED_FILES if (cycle_dir / n).stat().st_size == 0]
    r.add(5, "all required files non-empty", not empty,
          f"empty: {', '.join(empty)}" if empty else "")

    # 6. SHA256(target.json) == target.sha256
    recorded = (cycle_dir / "target.sha256").read_text(encoding="utf-8").strip()
    actual = sha256_file(cycle_dir / "target.json")
    if not HEX64.match(recorded):
        r.add(6, "target.sha256 matches target.json", False,
              f"target.sha256 is not a lowercase 64-char hex digest: {recorded[:80]!r}")
    else:
        r.add(6, "target.sha256 matches target.json", recorded == actual,
              "" if recorded == actual else f"recorded {recorded}\n          actual   {actual}")

    # target.json must parse before checks 7-9 mean anything
    try:
        target = json.loads((cycle_dir / "target.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        r.add(7, "cycle identifier unique", False, f"target.json is not valid JSON: {e}")
        r.add(8, "referenced git commit exists", False, "target.json unreadable")
        r.add(9, "mandatory hashed artifacts present and matching", False, "target.json unreadable")
        target = None
    else:
        missing_fields = [f for f in COMMON_FIELDS if f not in target]
        if missing_fields:
            r.add(7, "cycle identifier unique", False,
                  f"target.json missing required fields: {', '.join(missing_fields)}")
        else:
            # 7. cycle identifier unique within this review directory
            siblings = [d for d in cycle_dir.parent.iterdir()
                        if d.is_dir() and d != cycle_dir and (d / "target.json").is_file()]
            clashes = []
            for s in siblings:
                try:
                    other = json.loads((s / "target.json").read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                if other.get("cycle") == target.get("cycle"):
                    clashes.append(s.name)
            r.add(7, "cycle identifier unique", not clashes,
                  f"cycle {target.get('cycle')} also declared by: {', '.join(clashes)}"
                  if clashes else f"cycle {target.get('cycle')} in {cycle_dir.parent.name}")

        # 8. referenced git commit exists
        commits = [v for k, v in (target or {}).items() if k in ("commit", "protocol_commit")]
        if not commits:
            r.add(8, "referenced git commit exists", True, "no commit referenced")
        else:
            bad = [c for c in commits if not git_commit_exists(repo_root, str(c))]
            r.add(8, "referenced git commit exists", not bad,
                  f"unresolvable: {', '.join(bad)}" if bad else f"resolved: {', '.join(map(str, commits))}")

        # 9. mandatory hashed artifacts, per review type. Unconditional.
        rtype = (target or {}).get("review_type")
        problems: list[str] = []
        if rtype == "plan":
            files = target.get("plan_files")
            if not files:
                problems.append("plan review requires a non-empty plan_files list")
            else:
                for entry in files:
                    problems += _check_hashed_ref(entry, repo_root, "plan_files entry")
        elif rtype == "implementation":
            for field in ("commit", "tree", "approved_plan_sha256"):
                if not target.get(field):
                    problems.append(f"implementation review requires {field}")
            for field in ("diff", "test_results"):
                entry = target.get(field)
                if not entry:
                    problems.append(f"implementation review requires {field}")
                else:
                    problems += _check_hashed_ref(entry, repo_root, field)
        else:
            problems.append(f"review_type must be 'plan' or 'implementation', got {rtype!r}")
        r.add(9, "mandatory hashed artifacts present and matching", not problems,
              "; ".join(problems))

    # 10. codex-input.md contains the target hash verbatim
    ci = (cycle_dir / "codex-input.md").read_text(encoding="utf-8", errors="replace")
    bound = HEX64.match(recorded) is not None and recorded in ci
    r.add(10, "codex-input.md contains target SHA-256 verbatim", bound,
          "" if bound else
          "the input does not carry the frozen target hash, so nothing ties the "
          "reviewed artifact to what the reviewer was shown")

    return r


def _check_hashed_ref(entry, repo_root: Path, label: str) -> list[str]:
    if not isinstance(entry, dict) or "path" not in entry or "sha256" not in entry:
        return [f"{label} must be an object with path and sha256"]
    p = (repo_root / entry["path"])
    if not p.is_file():
        return [f"{label} path not found: {entry['path']}"]
    actual = sha256_file(p)
    if actual != entry["sha256"]:
        return [f"{label} hash mismatch for {entry['path']}: "
                f"recorded {entry['sha256']}, actual {actual}"]
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    cycle_dir = Path(argv[1]).resolve()
    if not cycle_dir.is_dir():
        print(f"not a directory: {cycle_dir}", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parent.parent
    result = validate(cycle_dir, repo_root)
    print(result.report(cycle_dir))
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
