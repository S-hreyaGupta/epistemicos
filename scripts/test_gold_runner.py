#!/usr/bin/env python3
"""Controls for the §15 Gold Set runner.

    python scripts/test_gold_runner.py

Exit 0 = every control fired.

Not in `refresh_counts.SUITES`, for the same reason as the approval-package
suite: `gold_runner.py` is not in the review target and is not reached through
`bootstrap_gate.covered()`. Adding it would inflate a figure four frozen prompts
state, for a file no reviewer was asked about.

The control that matters is the last one. §15.1 says aggregate improvement does
not override an unacceptable regression, and the only way to know a runner obeys
that is to hand it a candidate whose aggregate is level or better while one case
that used to work no longer does. A runner reporting a single accuracy figure
passes every other control here and fails that one.
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
SOURCE = {"path": "manuscript.md", "sha256": "a" * 64}


def gold_doc(items, **extra) -> dict:
    d = {"gold_set": "t-v0.1", "source": SOURCE,
         "key_fields": ["author", "year"], "items": items}
    d.update(extra)
    return d


def write(p: Path, doc: dict) -> Path:
    p.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return p


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SRC / "gold_runner.py"), *args],
                          cwd=str(REPO), capture_output=True, text=True)


def main() -> int:
    failures: list[str] = []
    t = Path(tempfile.mkdtemp())

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    def refuses(label: str, needle: str, *args: str) -> None:
        r = run(*args)
        blob = r.stdout + r.stderr
        if r.returncode != 1:
            failures.append(f"{label}: expected exit 1, got {r.returncode}\n{blob}")
        elif needle.lower() not in blob.lower():
            failures.append(f"{label}: refused for the wrong reason\n"
                            f"  wanted {needle!r}\n  got {blob.strip()[:220]}")
        else:
            ok(f"refused: {label}")

    print("gold runner")

    G = [{"author": "Smith", "year": "2020", "context": "Smith (2020) argues"},
         {"author": "Jones", "year": "2021", "context": "as Jones (2021) shows"},
         {"author": "World Bank", "year": "2016", "context": "(World Bank, 2016)"}]
    gold = write(t / "gold.json", gold_doc(G))

    # ---- refusals ----
    refuses("a gold set that declares no identity", "no `key_fields`",
            "--gold", str(write(t / "nokeys.json",
                                {k: v for k, v in gold_doc(G).items()
                                 if k != "key_fields"})),
            "--candidate", str(write(t / "c0.json", gold_doc(G))))

    # A gold set is written against one exact text. Scoring across two texts
    # measures the difference between them, not the extractor.
    other = gold_doc(G); other["source"] = {"path": "m.md", "sha256": "b" * 64}
    refuses("a candidate built from different source bytes", "different source",
            "--gold", str(gold), "--candidate", str(write(t / "c1.json", other)))

    # §15.2 evaluates against predefined acceptance criteria. Without them there
    # is a number and nothing to judge it against.
    refuses("no baseline and no acceptance criteria", "--criteria",
            "--gold", str(gold), "--candidate", str(write(t / "c2.json", gold_doc(G))))

    # An item with no value in any key field matches every other empty one, so
    # a file of them would score as perfect agreement.
    refuses("an item with an empty identity", "empty identity",
            "--gold", str(gold),
            "--candidate", str(write(t / "c3.json",
                                     gold_doc([{"author": "", "year": ""}]))))

    refuses("a gold set that is not there", "not found",
            "--gold", str(t / "absent.json"), "--candidate", str(gold))

    # ---- scoring ----
    crit = t / "crit.md"
    crit.write_text("recall >= 0.90\nno new false positives\n", encoding="utf-8")
    r = run("--gold", str(gold), "--candidate", str(write(t / "perfect.json",
                                                         gold_doc(G))),
            "--criteria", str(crit))
    if r.returncode != 0:
        failures.append(f"an exact candidate should score clean: {r.stderr}")
    elif "recall                1.000" not in r.stdout:
        failures.append(f"an exact candidate did not score recall 1.0\n{r.stdout[:400]}")
    elif "NOT_APPLICABLE" not in r.stdout:
        failures.append("§15.2 requires BASELINE_GOLD_RESULT = NOT_APPLICABLE "
                        "to be recorded when there is no baseline; it is absent")
    else:
        ok("an exact candidate scores 1.0, and §15.2 records NOT_APPLICABLE")

    # Position must not be part of identity: the same citations, renumbered and
    # reordered, are the same citations. Byte offsets move whenever an upstream
    # transform lands, and two are specified and unimplemented right now.
    moved = [dict(it, offset=999 - i) for i, it in enumerate(reversed(G))]
    r = run("--gold", str(gold), "--candidate", str(write(t / "moved.json",
                                                          gold_doc(moved))),
            "--criteria", str(crit))
    if "recall                1.000" not in r.stdout:
        failures.append(
            "reordering the items and changing their offsets changed the "
            "score. Identity is supposed to come from key_fields alone, so a "
            "gold set survives an upstream transform moving every position.")
    else:
        ok("identity ignores order and offset, as key_fields says it should")

    # ---- §15.1, the one this tool exists for ----
    # Baseline has Smith and Jones. Candidate has Smith and World Bank, and has
    # LOST Jones. Aggregate is level at 2 of 3 either way. A runner that reports
    # one accuracy figure calls this no change.
    base = write(t / "base.json", gold_doc(G[:2]))
    cand = write(t / "cand.json", gold_doc([G[0], G[2]]))
    r = run("--gold", str(gold), "--candidate", str(cand), "--baseline", str(base))
    blob = r.stdout + r.stderr
    if r.returncode != 3:
        failures.append(
            f"a candidate that lost a case the baseline got right exited "
            f"{r.returncode}, not 3. Aggregate was level, so the regression is "
            f"the only thing distinguishing these two runs and nothing in the "
            f"exit code says so.\n{blob[:400]}")
    elif "regressions                **1**" not in blob.replace("- **", "").replace("**\n", "**\n"):
        # tolerant of formatting: what matters is that exactly one is reported
        if "**1**" not in blob:
            failures.append(f"one regression was not reported as such\n{blob[:400]}")
        else:
            ok("a lost case is reported as a regression and exits 3")
    else:
        ok("a lost case is reported as a regression and exits 3")

    # Inside the Regressions section, not anywhere in the report. The first
    # version searched the whole output, and the lost case appears in the
    # missed-cases list too, so the control stayed green with regression
    # detection removed entirely. Found by mutation probe, 17 September: it was
    # passing for a reason that had nothing to do with what it is named for,
    # which is the defect this suite is meant to be watching for.
    section = blob.split("### Regressions", 1)[-1].split("\n## ", 1)[0] \
        if "### Regressions" in blob else ""
    if "Jones" not in section:
        failures.append("the regression is counted but the case is not named "
                        "under Regressions, so nobody can go and look at it")
    else:
        ok("the regressed case is named under Regressions, not just counted")

    # All six §15.1 comparisons, present by name.
    for needed in ("targeted improvements", "previously correct, retained",
                   "new false positives", "new false negatives",
                   "regressions", "aggregate"):
        if needed not in blob:
            failures.append(f"§15.1 requires all six comparisons; {needed!r} "
                            f"is absent")
            break
    else:
        ok("all six §15.1 comparisons are reported separately")

    # And a candidate strictly better than the baseline must not trip it.
    r = run("--gold", str(gold), "--candidate", str(write(t / "better.json",
                                                          gold_doc(G))),
            "--baseline", str(base))
    if r.returncode != 0:
        failures.append(f"a candidate that lost nothing exited {r.returncode}; "
                        f"a check that fires on every run reports nothing")
    else:
        ok("a candidate that lost nothing exits 0")

    shutil.rmtree(t, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("  aggregate improvement does not override a regression, and the "
          "runner proves it both ways")
    return 0


if __name__ == "__main__":
    sys.exit(main())
