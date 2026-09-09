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
    for n in ("bootstrap_gate.py", "validate_cycle.py", "run_review.py",
              "ledger.py", "loop_state.py"):
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
    # All four roots, plus the gate itself. bootstrap_gate.py is the one that was
    # missing: it did not hash itself, so editing `evaluate` to return (True, [])
    # would have defeated every other pin while check still said APPROVED.
    for target in ("validate_cycle.py", "run_review.py", "ledger.py",
                   "loop_state.py", "bootstrap_gate.py"):
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
    # Refuses in covered(), before the per-file comparison, because a root that
    # is gone cannot be hashed at all. Both refusals are correct; this asserts
    # the one that actually fires rather than the one written first.
    root = build(); made.append(root)
    approve(root)
    (root / "scripts" / "validate_cycle.py").unlink()
    expect_refused("approval surviving deletion of a reviewed root",
                   "component under bootstrap review is missing",
                   gate(root, "check"))

    # A deleted *dependency* takes the other path: the closure no longer reaches
    # it, so it is not required, but the decision still pins it. Without this the
    # "was reviewed but no longer exists" branch would be dead code.
    root = build(); made.append(root)
    write_lf(root / "scripts" / "helper_two.py", "VALUE = 1\n")
    lg = root / "scripts" / "ledger.py"
    lg.write_text(lg.read_text(encoding="utf-8") + '\n_H = "helper_two.py"\n',
                  encoding="utf-8")
    approve(root)
    (root / "scripts" / "helper_two.py").unlink()
    expect_refused("approval surviving deletion of a pinned dependency",
                   "no longer exists", gate(root, "check"))

    # ---- a decision that covers fewer components than required ----
    # This is also what an old decision looks like after the root list is
    # widened, which happened on 9 September when ledger.py and loop_state.py
    # were added. A decision predating a widening is not a decision about the
    # current system.
    for dropped in ("scripts/run_review.py", "scripts/ledger.py",
                    "scripts/loop_state.py"):
        root = build(); made.append(root)
        approve(root)
        rec = root / "bootstrap-review" / "decision.json"
        d = json.loads(rec.read_text(encoding="utf-8"))
        d["components"].pop(dropped)
        write_lf(rec, json.dumps(d, indent=2) + "\n")
        expect_refused(f"a decision that never covered {Path(dropped).name}",
                       "does not cover every component", gate(root, "check"))

    print()
    print("executable dependencies are derived, not listed")

    # The closure is empty on the real repository, because the four roots plus
    # the gate happen to cover everything they reference. An empty result from a
    # scanner that cannot find anything looks identical, so this builds a
    # dependency that does not exist in the real tree and requires it to be
    # found, pinned, and to invalidate the approval when edited.
    root = build(); made.append(root)
    write_lf(root / "scripts" / "helper_module.py", "VALUE = 1\n")
    vc = root / "scripts" / "validate_cycle.py"
    vc.write_text(
        vc.read_text(encoding="utf-8").replace(
            "import hashlib",
            'import hashlib\n_HELPER = "helper_module.py"  # loaded at runtime',
            1),
        encoding="utf-8")

    r = approve(root)
    if r.returncode != 0:
        failures.append(f"could not approve the dependency fixture:\n{r.stdout}{r.stderr}")
    else:
        d = json.loads((root / "bootstrap-review" / "decision.json")
                       .read_text(encoding="utf-8"))
        if "scripts/helper_module.py" not in d.get("components", {}):
            failures.append(
                "a module referenced by validate_cycle.py was not pulled into "
                "the pinned set. The closure is empty on the real repo, so "
                "without this control an inert scanner would look correct.")
        elif "scripts/helper_module.py" not in d.get("dependencies", {}):
            failures.append("the dependency was pinned but not recorded as a "
                            "dependency, so the record does not say why it is "
                            "covered")
        else:
            print("  [ok] a referenced local module is discovered and pinned")

            h = root / "scripts" / "helper_module.py"
            h.write_text("VALUE = 2\n", encoding="utf-8")
            expect_refused("approval surviving an edit to a dependency",
                           "has changed since it was reviewed", gate(root, "check"))

    # A dependency appearing after the decision must also block: the reviewed
    # bytes did not change, but what they reach did.
    root = build(); made.append(root)
    approve(root)
    if gate(root, "check").returncode != 0:
        failures.append("fixture did not reach an approved state")
    else:
        write_lf(root / "scripts" / "late_helper.py", "VALUE = 1\n")
        lp = root / "scripts" / "loop_state.py"
        lp.write_text(lp.read_text(encoding="utf-8") +
                      '\n_LATE = "late_helper.py"\n', encoding="utf-8")
        # loop_state.py itself changed too, so accept either reason; the point
        # is that it no longer passes.
        r = gate(root, "check")
        blob = (r.stdout + r.stderr).lower()
        if r.returncode == 0:
            failures.append("a component that started reaching new code still "
                            "passed on an old approval")
        elif "has changed" not in blob and "does not cover" not in blob:
            failures.append(f"blocked for an unexpected reason:\n{blob[:240]}")
        else:
            print("  [ok] refused: a component reaching code the decision never saw")

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
