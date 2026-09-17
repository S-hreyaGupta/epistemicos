#!/usr/bin/env python3
"""Controls for the §7 human review package generator.

    python scripts/test_approval_package.py

Exit 0 = every control fired.

Deliberately not in `refresh_counts.SUITES`. That number counts controls over
the execution layer under review, and `approval_package.py` is not in the review
target: it is not a declared component and nothing covered imports it, so it is
not in `bootstrap_gate.covered()`. Adding it to SUITES would inflate a figure
that four frozen prompts state, for a file no reviewer was asked about.

The thing most worth controlling here is what this tool must NOT do. It assembles
a package for a human to decide from; if it could decide anything itself, or
recompute a figure the owning tool refused to give, the package would be a second
implementation of the rule and the human would be reading it rather than the
record.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent
REPO = SRC.parent


def run(*args: str, cwd: Path, script: Path | None = None) -> subprocess.CompletedProcess:
    """Run the generator. `script` names which copy, which is not cosmetic.

    approval_package.py resolves the repository from its own location, not from
    the working directory, so running the real script with cwd set to a fixture
    reads the real repository. The first version of the temp-directory control
    below did exactly that and reported a refusal about the wrong run.
    """
    return subprocess.run(
        [sys.executable, str(script or (SRC / "approval_package.py")), *args],
        cwd=str(cwd), capture_output=True, text=True)


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    print("approval package")

    # ---- refusals: a package about nothing is worse than no package ----
    r = run("--run", "NO-SUCH-RUN", "--type", "plan", cwd=REPO)
    if r.returncode == 0:
        failures.append("a package was produced for a run that does not exist")
    elif "no run.json" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the missing run\n{r.stderr}")
    else:
        ok("refused: a run with no run.json")

    r = run("--run", "BOOTSTRAP-001", "--type", "implementation", cwd=REPO)
    if r.returncode == 0:
        failures.append("a package was produced for a review type that has no "
                        "directory")
    elif "no implementation review" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the absent review\n{r.stderr}")
    else:
        ok("refused: a review type this run never held")

    # A run initialised but never frozen. There is nothing to approve, and
    # saying so beats producing a package with empty headings that reads like
    # an approval-ready document.
    t = Path(tempfile.mkdtemp()); made.append(t)
    (t / "runs" / "T-001" / "plan-review").mkdir(parents=True)
    (t / "scripts").mkdir()
    for f in ("approval_package.py", "loop_state.py", "ledger.py",
              "validate_cycle.py", "cycle_projection.py", "authority.py",
              "run_pins.py", "findings_format.py"):
        shutil.copy(SRC / f, t / "scripts" / f)
    (t / "runs" / "T-001" / "run.json").write_text(json.dumps({
        "run_id": "T-001", "mc1_enforcement": "CONVENTION_ONLY",
        "max_cycles": 4}), encoding="utf-8")
    r = run("--run", "T-001", "--type", "plan", cwd=t,
            script=t / "scripts" / "approval_package.py")
    if r.returncode == 0:
        failures.append("a package was produced for a review with no frozen "
                        "cycles; there is nothing to approve")
    elif "no frozen cycles" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the absent cycles\n{r.stderr}")
    else:
        ok("refused: a review with no frozen cycle")

    # ---- the real run ----
    out = REPO / "runs" / "BOOTSTRAP-001" / "plan-review" / "APPROVAL-PACKAGE.md"
    ledger = REPO / "runs" / "BOOTSTRAP-001" / "plan-review" / "ledger.json"
    before = ledger.read_bytes()
    r = run("--run", "BOOTSTRAP-001", "--type", "plan", cwd=REPO)
    if r.returncode != 0:
        failures.append(f"could not build a package for BOOTSTRAP-001:\n"
                        f"{r.stdout}{r.stderr}")
        text = ""
    else:
        text = out.read_text(encoding="utf-8")
        ok("a package is produced for a run with frozen cycles")

    # The one thing it must never do.
    if ledger.read_bytes() != before:
        failures.append(
            "building a package altered the ledger. It assembles a record for "
            "a human to decide from and must write nothing into the record it "
            "describes.")
    else:
        ok("building a package writes nothing into the ledger")

    if text and "decides nothing" not in text:
        failures.append("the package does not say that it decides nothing, so "
                        "a reader could take it for the decision")
    elif text:
        ok("the package states that it decides nothing")

    # §7.2, in the protocol's own words: "Disputes and unresolved findings must
    # be presented separately." One heading holding both satisfies a reader
    # skimming for the word and defeats the requirement.
    if text:
        if "### Unresolved findings" not in text or "### Disputes" not in text:
            failures.append("§7.2 requires disputes and unresolved findings "
                            "presented separately; they are not two headings")
        elif text.index("### Unresolved findings") == text.index("### Disputes"):
            failures.append("disputes and unresolved findings share a heading")
        else:
            ok("§7.2: disputes and unresolved findings are separate headings")

    # It must quote the owning tool, including when that tool refuses. A package
    # that recomputed a refused figure would be a second controller, and the
    # human would be reading this file instead of the record.
    if text:
        if "REFUSED" not in text or "development" not in text.lower():
            failures.append(
                "the controller refuses an authoritative loop result for this "
                "run, and the package does not carry the refusal. Either it "
                "recomputed the figure or it dropped it; both are worse than "
                "quoting the refusal.")
        else:
            ok("a refusal by the owning tool is quoted, not worked around")

    # The coverage table is checked against §7's list, so an item that stops
    # being produced shows as absent. Verified by reading the list out of the
    # generator rather than restating it here: a second copy would be free to
    # disagree, which is the defect this whole layer keeps finding.
    if text:
        import importlib.util as il
        spec = il.spec_from_file_location("_ap", SRC / "approval_package.py")
        mod = il.module_from_spec(spec); spec.loader.exec_module(mod)
        absent = [k for k in mod.SECTION_7_ITEMS if f"- [ ] {k}" in text]
        listed = [k for k in mod.SECTION_7_ITEMS
                  if f"- [x] {k}" in text or f"- [ ] {k}" in text]
        if len(listed) != len(mod.SECTION_7_ITEMS):
            failures.append(
                f"the coverage table lists {len(listed)} of "
                f"{len(mod.SECTION_7_ITEMS)} §7 items. An item missing from "
                "the table cannot be seen to be missing from the package.")
        elif not absent:
            failures.append(
                "every §7 item reports present. BOOTSTRAP-001 has no plan and "
                "therefore no SPEC -> CODE -> TEST mapping, so a table with "
                "nothing absent is not reporting, it is agreeing.")
        else:
            ok(f"all {len(listed)} §7 items appear in the coverage table, "
               f"{len(absent)} marked absent")

        for k in absent:
            if f"*{k}*" not in text:
                failures.append(f"§7 item {k!r} is marked absent and the "
                                "package never says why")
                break
        else:
            if absent:
                ok("each absent §7 item carries a stated reason")

    # ---- a frozen run with no recorded review ----
    # Every run passes through this state, and it is where the first version of
    # this tool crashed: `ledger show` exits 0 on a review with no ledger, and
    # exit 0 was read as "the file is there".
    r = run("--run", "BOOTSTRAP-002", "--type", "plan", cwd=REPO)
    p2 = REPO / "runs" / "BOOTSTRAP-002" / "plan-review" / "APPROVAL-PACKAGE.md"
    if r.returncode != 0:
        failures.append(f"a frozen run with no recorded review should still "
                        f"produce a package:\n{r.stdout}{r.stderr}")
    else:
        t2 = p2.read_text(encoding="utf-8")
        if "no review has reported yet" not in t2:
            failures.append(
                "a run with frozen cycles and no ledger does not say so. "
                "Silence there reads as 'no findings', which is the opposite "
                "of 'nobody has looked'.")
        elif "- [x] unresolved findings" in t2:
            failures.append(
                "a run with no ledger reports unresolved findings as present. "
                "An empty heading satisfied the coverage table.")
        else:
            ok("a frozen run with no recorded review says so, and claims no "
               "findings")

    for p in made:
        shutil.rmtree(p, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("  the package generator assembles, refuses, and decides nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
