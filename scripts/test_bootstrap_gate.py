#!/usr/bin/env python3
"""Negative controls for the bootstrap gate.

    python scripts/test_bootstrap_gate.py

Exit 0 = every refusal fired on a fixture built to produce it.

The gate is one boolean standing between development evidence and a real
protocol cycle, so the only thing that makes it worth having is that it can say
no. Each refusal below is demonstrated, and the approval path is demonstrated
too, because a gate that refuses everything is as useless as one that refuses
nothing.

The control that matters most is `approval does not survive editing a reviewed
component`. Without it the gate would answer "was there a review" rather than
"was this code reviewed", and it would keep saying yes about files nobody has
looked at since. That is the superseded-protocol-pin defect one level up.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "scripts"

EVIDENCE = ("codex-input.md", "codex-output-raw.md", "findings.md",
            "claude-response.md")


def write_lf(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build(with_evidence: bool = True) -> Path:
    """A throwaway repo carrying the real gate and the real components."""
    tmp = Path(tempfile.mkdtemp(prefix="bgate-")).resolve()
    (tmp / "scripts").mkdir()
    for n in ("bootstrap_gate.py", "validate_cycle.py", "run_review.py"):
        shutil.copy2(SRC / n, tmp / "scripts" / n)
    if with_evidence:
        for n in EVIDENCE:
            write_lf(tmp / "bootstrap-review" / n, f"contents of {n}\n")
    return tmp


def gate(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "scripts" / "bootstrap_gate.py"),
                           *args], cwd=str(root), capture_output=True, text=True)


def approve(root: Path, who: str = "Alex Zamurko") -> subprocess.CompletedProcess:
    return gate(root, "record", "--decision", "APPROVE", "--decided-by", who,
                "--note", "reviewed by Codex, bootstrap exception")


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def expect_refused(label: str, needle: str, r: subprocess.CompletedProcess) -> None:
        if r.returncode == 0:
            failures.append(f"{label}: expected a refusal, got exit 0\n{r.stdout}")
            return
        blob = (r.stdout + r.stderr).lower()
        if needle.lower() not in blob:
            failures.append(f"{label}: refused for the wrong reason\n"
                            f"  wanted {needle!r}\n  got {blob.strip()[:240]}")
            return
        print(f"  [ok] refused: {label}")

    print("the gate refuses")

    # ---- nothing recorded ----
    root = build(); made.append(root)
    expect_refused("check with no bootstrap review at all",
                   "no bootstrap review on record", gate(root, "check"))

    # ---- evidence incomplete ----
    root = build(with_evidence=False); made.append(root)
    expect_refused("record a decision with no evidence preserved",
                   "incomplete", approve(root))

    root = build(); made.append(root)
    (root / "bootstrap-review" / "codex-output-raw.md").write_text("", encoding="utf-8")
    expect_refused("record a decision with the raw output empty",
                   "codex-output-raw.md (empty)", approve(root))

    # ---- no human named ----
    root = build(); made.append(root)
    expect_refused("record a decision with no human named", "decided-by",
                   gate(root, "record", "--decision", "APPROVE", "--decided-by", "  "))

    # ---- a decision that is not an approval ----
    root = build(); made.append(root)
    r = gate(root, "record", "--decision", "RETURN_FOR_REWORK",
             "--decided-by", "Alex Zamurko")
    if r.returncode != 0:
        failures.append(f"recording RETURN_FOR_REWORK should succeed:\n{r.stderr}{r.stdout}")
    else:
        expect_refused("check after RETURN_FOR_REWORK", "not approve",
                       gate(root, "check"))

    print()
    print("the gate approves")

    root = build(); made.append(root)
    r = approve(root)
    if r.returncode != 0:
        failures.append(f"a complete bootstrap review should record:\n{r.stderr}{r.stdout}")
    elif gate(root, "check").returncode != 0:
        failures.append("check refused immediately after a valid APPROVE; the "
                        "gate would then block every run forever, which is as "
                        "useless as approving everything")
    else:
        print("  [ok] a complete review records, and check passes")

    # ---- one-time by design ----
    expect_refused("record a second decision without --supersede",
                   "already exists", approve(root, "Someone Else"))

    r = gate(root, "record", "--decision", "APPROVE", "--decided-by", "Alex Zamurko",
             "--supersede")
    if r.returncode != 0:
        failures.append(f"--supersede should be permitted:\n{r.stderr}{r.stdout}")
    else:
        d = json.loads((root / "bootstrap-review" / "decision.json")
                       .read_text(encoding="utf-8"))
        if "supersedes" not in d:
            failures.append("--supersede replaced the decision without preserving "
                            "the prior one; the record must not lose it")
        else:
            print("  [ok] --supersede preserves the decision it replaces")

    print()
    print("approval covers bytes, not filenames")

    # ---- THE control: editing a reviewed component invalidates the review ----
    for target in ("validate_cycle.py", "run_review.py"):
        root = build(); made.append(root)
        if approve(root).returncode != 0 or gate(root, "check").returncode != 0:
            failures.append(f"fixture for {target} did not reach an approved state")
            continue
        p = root / "scripts" / target
        p.write_text(p.read_text(encoding="utf-8") + "\n# a later edit\n",
                     encoding="utf-8")
        expect_refused(f"approval surviving an edit to {target}",
                       "has changed since it was reviewed", gate(root, "check"))

    # ---- a reviewed component deleted ----
    root = build(); made.append(root)
    approve(root)
    (root / "scripts" / "validate_cycle.py").unlink()
    expect_refused("approval surviving deletion of a reviewed component",
                   "no longer exists", gate(root, "check"))

    # ---- a decision that covers fewer components than required ----
    root = build(); made.append(root)
    approve(root)
    rec = root / "bootstrap-review" / "decision.json"
    d = json.loads(rec.read_text(encoding="utf-8"))
    d["components"].pop("scripts/run_review.py")
    write_lf(rec, json.dumps(d, indent=2) + "\n")
    expect_refused("a decision covering only some of the components",
                   "does not cover every component", gate(root, "check"))

    # ---- a corrupt record is a refusal, not a crash ----
    root = build(); made.append(root)
    approve(root)
    write_lf(root / "bootstrap-review" / "decision.json", "{not json\n")
    expect_refused("a decision record that is not valid JSON",
                   "not valid json", gate(root, "check"))

    print()
    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("every refusal fired, and approval does not outlive the code it covered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
