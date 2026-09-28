#!/usr/bin/env python3
"""Break each repair in turn. Does its control notice?

    python _probe\\mutate_repairs.py

Exit 0 = every repair has a control that goes red when the repair is removed.
Exit 1 = one does not, and it is named.
Exit 2 = could not run.

Why
---
Eight findings were repaired on 26 September and each commit claims a control
that holds it. A control written beside a repair, by the same hand, on the
same afternoon, is exactly the kind that passes because the repair happens to
be there rather than because it is checking for it. That is the defect class
this whole run keeps finding, and asserting it about my own work without
testing it would be the same mistake with a different subject.

So each repair is removed, one at a time, from the real file, and its suite is
run. The repair's control must go red, and the failure must mention something
specific to that repair rather than any failure at all: a suite that goes red
for an unrelated reason establishes nothing about the control named.

`mutate_citation_suite.py` does this for the extractor and has done since
September; the review layer, which is the more consequential of the two, has
had no equivalent. This is a start on that rather than the whole of it: one
mutation per repair as each is made, not a general mutation probe. A repair
that arrives without a line here has not been shown to be watched.

A crashed suite is refused rather than counted, for the reason
`vacuity_sweep.py` records at length: a traceback is the one signal a failing
control never produces, and reading a crash as a catch means the control was
never consulted.

The tree is checked before the first mutation and again after the last. An
earlier run of this probe left `run_review.py` mutated over a weekend, its
protocol-integrity check replaced with `if False:`. The restore runs in a
`finally`, which does not survive the process being killed, and nothing else
in the repository would have noticed a check that had been switched off.
Every suite run in that window passed for a reason other than the one it
names, which is precisely the defect this probe was written to find, arriving
by way of the probe. So a run refuses to start against a tree that is already
dirty, and says so loudly if it fails to leave one clean.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

# (finding, file, exact source to replace, replacement, suite, needle)
#
# The needle is matched against the suite's own failure text and has to be
# specific to the control the repair is supposed to have. "expected FAIL" or a
# bare non-zero exit would be satisfied by any breakage at all.
MUTATIONS = [
    ("C01-F01  the reopening guard in the shared evaluator",
     "cycle_projection.py",
     "if self.reopened_at is not None and c < self.reopened_at:",
     "if False:",
     "test_ledger.py",
     # "backdated" appears in the [ok] text and in comments, not in any
     # FAILURE message, so the first version of this needle reported WRONG
     # CONTROL about a control that was working. The failures say "predates
     # the reopening" and "dated before the reopening"; this matches both.
     "the reopening"),

    ("C01-F02  the ceiling binding at every boundary",
     "loop_state.py",
     "        if n >= MAX_VALID_CYCLES:\n"
     "            lines.append(f\"        {status} at n={n} was cleared, and the \"",
     "        if False:\n"
     "            lines.append(f\"        {status} at n={n} was cleared, and the \"",
     "test_ledger.py",
     "fifth cycle"),

    ("C01-F03  check 9 reading the governing artifacts",
     "validate_cycle.py",
     "    if bad:\n"
     "        return [\"the governing artifacts",
     "    if False:\n"
     "        return [\"the governing artifacts",
     "test_validate_cycle.py",
     "governing"),

    ("C01-F04  MC-2 validating the pin history before replaying it",
     "validate_cycle.py",
     "        expect = run_pins.governing_pin_hashes(run, run_dir,\n"
     "                                               int(target[\"cycle\"]))",
     "        expect = run_pins.pin_hashes_for_cycle(\n"
     "            run, run_pins.load_amendments(run_dir), int(target[\"cycle\"]))",
     "test_validate_cycle.py",
     "amendment history"),

    ("C01-F05  no default classification for a run",
     "loop_state.py",
     "    kind, problem = run_pins.run_kind(run)\n"
     "    if problem:",
     "    kind, problem = run_pins.run_kind(run)\n"
     "    problem = None\n"
     "    kind = kind or run_pins.PROTOCOL\n"
     "    if problem:",
     "test_ledger.py",
     "bootstrap_review"),

    ("C01-F06  a reported finding must have a state",
     "loop_state.py",
     "    if _stateless:\n"
     "        raise CannotCalculate(",
     "    if False:\n"
     "        raise CannotCalculate(",
     "test_ledger.py",
     "authoritative state"),

    ("C01-F07  cycle identity, not only uniqueness",
     "validate_cycle.py",
     "        ok7 = not clashes and not mismatch",
     "        ok7 = not clashes",
     "test_validate_cycle.py",
     "check 7"),

    ("C01-F08  the commit and the hash describing one document",
     "run_review.py",
     "    if _committed != sha256_file(protocol):",
     "    if False:",
     "test_run_review.py",
     "protocol"),

    ("C02-F03  the age exemption refused to evidence that is not old",
     "validate_cycle.py",
     "    if _gph is None and _gp is None:\n"
     "        if _modern:",
     "    if _gph is None and _gp is None:\n"
     "        if False:",
     "test_validate_cycle.py",
     "artifacts were preserved"),

    # Not repairs. The §6 exit order, which Alex Zamurko asked on 28 September
    # to be tested at cycle 4 specifically, because every other exit was only
    # ever exercised where the ceiling was not competing with it. Disabling
    # either branch sends its scenario to MAX_4_REACHED, which is the exact
    # failure the new controls exist to refuse, so these two mutations are what
    # make them evidence rather than decoration.
    ("exit A  converging at the ceiling is CONVERGED, not MAX_4",
     "loop_state.py",
     "    if not cur[OPEN] and not cur[DISPUTED]:",
     "    if False:",
     "test_ledger.py",
     "a fourth cycle that converges"),

    ("exit B  a dispute at the ceiling needs a human, not MAX_4",
     "loop_state.py",
     "    if not cur[OPEN] and cur[DISPUTED]:",
     "    if False:",
     "test_ledger.py",
     "only a dispute left"),
]


def run_suite(name: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, str(SCRIPTS / name)],
                          env=env, capture_output=True, text=True, timeout=900)


def modified(rel_paths: list[str]) -> list[str]:
    """Which of these repo-relative paths git reports as changed."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain", "--"] + rel_paths,
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git status failed:\n{r.stderr.strip()}")
    return sorted({ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip()})


def main() -> int:
    targets = sorted({f"scripts/{m[1]}" for m in MUTATIONS})
    try:
        dirty = modified(targets)
    except RuntimeError as exc:
        print(f"  [CANNOT RUN] {exc}")
        return 2
    if dirty:
        print("  [CANNOT RUN] this probe writes to tracked source and restores "
              "it afterwards,\n  so it can only run against a clean tree. These "
              "already differ from HEAD:\n")
        for p in dirty:
            print(f"      {p}")
        print("\n  Commit or discard them first. Started from here, each restore "
              "would put the\n  file back to whatever it held at the start, which "
              "is not the same as putting\n  it back to the repaired source, and "
              "the result would say nothing about the\n  repairs.")
        return 2

    bad = 0
    for finding, fname, old, new, suite, needle in MUTATIONS:
        path = SCRIPTS / fname
        original = path.read_text(encoding="utf-8")
        found = original.count(old)
        if found != 1:
            hint = ""
            if found == 0 and new in original:
                hint = ("\n      The replacement text is there instead, so the "
                        "mutation is already applied:\n      an earlier run "
                        "wrote it and did not restore it.")
            print(f"  [BROKEN PROBE] {finding}\n"
                  f"      the source this mutation replaces appears {found} "
                  f"times in {fname}, not\n      once, so the mutation cannot "
                  f"be applied. That is reported rather than\n      counted as "
                  f"a catch.{hint}")
            bad += 1
            continue

        # newline="" so a run on Windows does not rewrite the file's endings
        # on its way past, and on the restore as well as the write.
        path.write_text(original.replace(old, new, 1), encoding="utf-8",
                        newline="")
        try:
            r = run_suite(suite)
        finally:
            path.write_text(original, encoding="utf-8", newline="")

        blob = (r.stdout or "") + (r.stderr or "")
        if "Traceback (most recent call last)" in (r.stderr or ""):
            print(f"  [CRASHED] {finding}\n"
                  f"      {suite} crashed rather than failing controls, so "
                  f"its output says nothing about which controls hold.")
            bad += 1
        elif r.returncode == 0:
            print(f"  [MISSED] {finding}\n"
                  f"      the repair was removed and {suite} still passed. "
                  f"Nothing in that suite is checking for it.")
            bad += 1
        elif needle.lower() not in blob.lower():
            print(f"  [WRONG CONTROL] {finding}\n"
                  f"      {suite} went red, and not for anything mentioning "
                  f"{needle!r}. Something failed; it is not shown to be the "
                  f"control this repair is supposed to have.")
            bad += 1
        else:
            print(f"  [caught] {finding}")

    left = modified(targets)
    if left:
        print(f"\n  [LEFT MODIFIED] the probe did not restore everything it "
              f"wrote to:\n")
        for p in left:
            print(f"      {p}")
        print("\n  Restore them with `git checkout --` before running anything "
              "else. Until then\n  every suite in the repository is reading "
              "source this probe broke on purpose.")
        bad += 1

    print()
    if bad:
        print(f"  {bad} of {len(MUTATIONS)} repairs are not demonstrably held "
              f"by a control.")
        return 1
    print(f"  all {len(MUTATIONS)} repairs go red when removed, each in a "
          f"control that names what it is about.")
    print("  That is not proof the repairs are correct. It is proof they are")
    print("  watched, which is the claim each commit made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
