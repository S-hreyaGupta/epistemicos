#!/usr/bin/env python3
"""Assemble the §7 human review package for a run.

    python scripts/approval_package.py --run BOOTSTRAP-002 --type plan
    python scripts/approval_package.py --run BOOTSTRAP-002 --type plan --out PACKAGE.md

Exit 0 = a package was written, and it states which §7 items it could not fill.
Exit 1 = refused; nothing written.

Why this exists
---------------
§7 requires a human to review the plan after CONVERGED, HUMAN_ADJUDICATION_REQUIRED,
STALLED or MAX_4_REACHED, and lists ten things the package must contain. Nothing
built them. The consequence was not that approval was hard, it was that approval
had no defined subject: a human was being asked to approve a directory.

Every figure here is taken from the tool that owns it, by running that tool and
quoting what it said. None of it is recomputed locally. That is the whole design:
a package that recomputed loop status would be a second controller, and two
implementations of one rule is the defect this layer keeps finding in itself. If
a tool refuses, the refusal is what the package records — not a gap, and not a
guess at what the answer would have been.

What it does not do
-------------------
It does not decide anything, and it writes nothing into any ledger. The decision
is recorded by `bootstrap_gate.py record`, which is a separate act by a separate
person.

It cannot produce the SPEC → CODE → TEST mapping of §7 for a bootstrap run,
because that mapping is the output of a §1 plan audit and a bootstrap run has no
plan. It says so rather than leaving the heading out, because a reviewer who
cannot see what is missing cannot weigh it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

# The ten items §7 names, in its order. Presence is reported against this list
# rather than against whatever the package happened to manage, so an item that
# silently stopped being produced shows up as absent instead of disappearing.
SECTION_7_ITEMS = (
    "final plan",
    "final plan hash",
    "loop status",
    "valid iteration count",
    "SPEC -> CODE -> TEST mapping",
    "resolved findings",
    "disputes",
    "unresolved findings",
    "MC-1 enforcement status",
    "MC-2 conformance results for every valid cycle",
)


class Refused(Exception):
    """Exit 1, write nothing."""


def run_tool(*args: str) -> tuple[int, str]:
    """Run one of this repo's tools and return exactly what it said."""
    r = subprocess.run([sys.executable, *args], cwd=str(REPO),
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).rstrip()


def quote(text: str) -> str:
    return "```text\n" + (text if text.strip() else "(no output)") + "\n```"


def load_run(run_id: str) -> dict:
    p = REPO / "runs" / run_id / "run.json"
    if not p.is_file():
        raise Refused(f"no run.json for {run_id}. A package describes a run; "
                      f"this one has no record.\n  expected {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise Refused(f"{p} is not valid JSON: {e}")


def cycles(review: Path) -> list[Path]:
    return sorted(d for d in review.glob("cycle-*") if d.is_dir())


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="approval_package.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--type", required=True, choices=("plan", "implementation"))
    ap.add_argument("--out", default="",
                    help="default: runs/<run>/<type>-review/APPROVAL-PACKAGE.md")
    a = ap.parse_args()

    run = load_run(a.run)
    review = REPO / "runs" / a.run / f"{a.type}-review"
    if not review.is_dir():
        raise Refused(f"no {a.type} review for {a.run}: {review} does not exist")

    cy = cycles(review)
    if not cy:
        raise Refused(f"{review} has no frozen cycles. There is nothing to "
                      "approve yet.")

    present: dict[str, bool] = {k: False for k in SECTION_7_ITEMS}
    out: list[str] = []
    W = out.append

    W(f"# Human review package — {a.run}, {a.type} review")
    W("")
    W("Assembled by `scripts/approval_package.py` from the run's own records. "
      "Every figure below is quoted from the tool that owns it; none is "
      "recomputed here.")
    W("")
    W("**This package decides nothing.** The decision is recorded separately, "
      "by a person, with `bootstrap_gate.py record`. §7.3 permits exactly three "
      "outcomes: `APPROVE`, `RETURN_FOR_REWORK`, `REJECT`.")
    W("")

    # ---- MC-1, §7 item 9. Read from the run, not assumed. ----
    W("## MC-1 enforcement status")
    W("")
    mc1 = run.get("mc1_enforcement")
    if mc1:
        present["MC-1 enforcement status"] = True
        W(f"`{mc1}`")
        if mc1 == "CONVENTION_ONLY":
            W("")
            W("Every check in this layer is detection that holds while the "
              "checks run faithfully and nobody edits the records they read. "
              "The same writable code performs the checks on itself. Nothing "
              "here is technically enforced.")
    else:
        W("**Absent from run.json.** The run does not record one, so this "
          "package cannot state it.")
    prov = run.get("mc1_enforcement_provenance")
    if prov:
        W("")
        W("Reconstructed rather than recorded at the time:")
        W("")
        W(quote(json.dumps(prov, indent=2)))
    W("")

    if run.get("bootstrap_review", "").startswith("EXEMPT"):
        W("> **Development evidence, not a protocol outcome.** This run is "
          "marked `NOT_A_PROTOCOL_CYCLE`. Nothing in this package may be cited "
          "as a protocol result.")
        W("")

    # ---- loop status + valid iteration count, §7 items 3 and 4 ----
    W("## Loop status and valid iteration count")
    W("")
    args_loop = [str(SCRIPTS / "loop_state.py"), "--review", str(review)]
    rc, text = run_tool(*args_loop)
    if rc != 0 and "--development" in text:
        W("The controller refuses to state an authoritative loop result for "
          "this run, and says why:")
        W("")
        W(quote(text))
        W("")
        W("Recomputed with `--development`. The result is labelled and is not "
          "a protocol outcome:")
        W("")
        rc, text = run_tool(*args_loop, "--development")
    if rc == 0:
        present["loop status"] = True
        present["valid iteration count"] = "-> n=" in text or "VALID" in text
    W(quote(text))
    W("")

    # ---- findings, §7 items 6, 7, 8. Presented separately, per §7.2. ----
    W("## Findings")
    W("")
    rc, led = run_tool(str(SCRIPTS / "ledger.py"), "show", "--review", str(review))
    ledger_json = review / "ledger.json"
    if rc != 0:
        W("The ledger could not be read, so this package states no finding "
          "counts:")
        W("")
        W(quote(led))
    elif not ledger_json.is_file():
        # `show` exits 0 on a review with no ledger, saying so. Taking exit 0 as
        # "the file is there" crashed this tool the first time it met a run that
        # had frozen a cycle and recorded nothing yet — which is the state every
        # run passes through, and the defect class this layer keeps finding in
        # itself: a zero exit read as an answer it was not giving.
        W(f"No `{ledger_json.name}` yet, so there are no findings to present.")
        W("")
        W(quote(led))
        W("")
        W("This is the ordinary state of a run whose cycles are frozen and "
          "whose review has not been recorded. It is not a defect, and it is "
          "not an absence of findings: no review has reported yet.")
    else:
        # Marked present only on the branch that actually produced them. The
        # coverage table is only worth reading if it cannot be satisfied by a
        # heading with nothing under it.
        present["resolved findings"] = True
        present["unresolved findings"] = True
        present["disputes"] = True
        W("§7.2 requires disputes and unresolved findings to be presented "
          "separately. They are separate headings below; the full ledger "
          "follows both.")
        W("")
        data = json.loads((review / "ledger.json").read_text(encoding="utf-8"))
        by_state: dict[str, list[str]] = {}
        for fid, f in sorted(data.get("findings", {}).items()):
            by_state.setdefault(f.get("state", "?"), []).append(fid)

        W("### Unresolved findings — the human decides each one")
        W("")
        W("§7.2: the human determines whether each requires correction, is "
          "explicitly waived or accepted, or causes rejection of the plan.")
        W("")
        openers = by_state.get("OPEN", [])
        if not openers:
            W("None.")
        for fid in openers:
            f = data["findings"][fid]
            line = f"- **{fid}** · {f.get('class','?')}"
            if f.get("requirement_id"):
                line += f" · {f['requirement_id']}"
            W(line)
            if f.get("repair_status"):
                extra = ", ".join(x for x in (f.get("external_verification_run"),
                                              f.get("human_closure_record")) if x)
                W(f"  - repair status: `{f['repair_status']}`"
                  + (f" ({extra})" if extra else "")
                  + " — descriptive, not a lifecycle state")
            W(f"  - found by: `{f.get('source', 'UNRECORDED')}`")
        W("")

        W("### Disputes — the human adjudicates")
        W("")
        W("§7.1: a dispute is a Codex finding plus a Claude "
          "`REJECT_WITH_REASON`.")
        W("")
        disputed = by_state.get("DISPUTED", [])
        W("None." if not disputed else "")
        for fid in disputed:
            f = data["findings"][fid]
            W(f"- **{fid}** · {f.get('class','?')}")
            for e in f.get("history", []):
                if e.get("event", "").startswith("REJECT"):
                    W(f"  - reason: {e.get('note','(none recorded)')}")
        W("")

        W("### Resolved findings")
        W("")
        res = by_state.get("RESOLVED", [])
        W(f"{len(res)} resolved." if res else "None.")
        if res:
            W("")
            W("`RESOLVED` under §5 means a repair was demonstrated in a later "
              "review target. It does not mean the repair was re-verified "
              "afterwards.")
        W("")
        W("<details><summary>Full ledger</summary>")
        W("")
        W(quote(led))
        W("")
        W("</details>")
    W("")

    # ---- MC-2 for every valid cycle, §7 item 10 ----
    W("## MC-2 conformance, every cycle")
    W("")
    W("The gate is run now, against the frozen evidence, rather than quoted "
      "from a stored result. A recorded PASS is a claim about the past; this "
      "is the gate's answer today.")
    W("")
    all_seen = True
    for c in cy:
        rc, text = run_tool(str(SCRIPTS / "validate_cycle.py"), str(c))
        verdict = next((l for l in text.splitlines()
                        if "MC2_CONFORMANCE" in l), "(no verdict line)")
        W(f"### {c.name} — `{verdict.strip()}`")
        W("")
        W("<details><summary>full gate output</summary>")
        W("")
        W(quote(text))
        W("")
        W("</details>")
        W("")
        if "PASS" not in verdict:
            all_seen = False
    present["MC-2 conformance results for every valid cycle"] = True
    if not all_seen:
        W("> At least one cycle does not currently pass. A package is still "
          "produced: whether that blocks approval is the human's decision, not "
          "this tool's.")
        W("")

    # ---- the reviewed artifacts, §7 items 1 and 2 ----
    W("## What is being approved")
    W("")
    latest = cy[-1]
    tj = latest / "target.json"
    ts = latest / "target.sha256"
    if tj.is_file() and ts.is_file():
        present["final plan"] = True
        present["final plan hash"] = True
        target = json.loads(tj.read_text(encoding="utf-8"))
        W(f"From `{latest.name}`, the most recent frozen cycle.")
        W("")
        W(f"Target digest: `{ts.read_text(encoding='utf-8').strip()}`")
        W("")
        files = target.get("plan_files") or target.get("artifacts") or []
        W(f"{len(files)} artifact(s):")
        W("")
        for f in files:
            W(f"- `{f.get('path','?')}` · `{f.get('sha256','?')}`")
        W("")
        W("The bytes reviewed are preserved under "
          f"`{latest.name}/artifacts/`. They are what the reviewer saw, and "
          "they do not change when the working tree does.")
    else:
        W(f"**`{latest.name}` has no target.json / target.sha256.** This "
          "package cannot say what was reviewed.")
    W("")

    # ---- what §7 asked for and what is here ----
    W("## §7 coverage")
    W("")
    W("Checked against §7's list rather than against what this package "
      "managed to produce, so an item that stopped being generated shows as "
      "absent instead of vanishing.")
    W("")
    for k in SECTION_7_ITEMS:
        W(f"- {'[x]' if present[k] else '[ ]'} {k}")
    W("")
    missing = [k for k in SECTION_7_ITEMS if not present[k]]
    if missing:
        W(f"**{len(missing)} of {len(SECTION_7_ITEMS)} not present.**")
        W("")
        # Each reason is keyed by the exact item string, so the text naming an
        # item and the table listing it cannot drift apart. They already had:
        # the table said "SPEC -> CODE -> TEST mapping" and the explanation
        # said "SPEC → CODE → TEST mapping", and a control looking for the
        # second under the first found nothing.
        WHY = {
            "SPEC -> CODE -> TEST mapping":
                "the output of a §1 plan audit. A bootstrap run reviews code "
                "directly and has no plan, so there is no mapping to produce. "
                "Named here rather than omitted, because a reviewer who cannot "
                "see what is missing cannot weigh it.",
            "resolved findings":
                "no review has been recorded for this run yet, so there is no "
                "ledger to read them from.",
            "unresolved findings":
                "no review has been recorded for this run yet. This is not the "
                "same as there being none.",
            "disputes":
                "no review has been recorded for this run yet, so no "
                "disposition has been rejected.",
        }
        for k in missing:
            W(f"- *{k}*: "
              + WHY.get(k, "not produced. See the section above for why."))
        W("")

    W("---")
    W("")
    W("## Recording the decision")
    W("")
    W("§7.3 permits `APPROVE`, `RETURN_FOR_REWORK`, `REJECT`. Nothing in this "
      "file records one.")
    W("")
    W(quote("python scripts/bootstrap_gate.py record \\\n"
            "    --decision APPROVE|RETURN_FOR_REWORK|REJECT \\\n"
            "    --decided-by \"<name>\" \\\n"
            "    --note \"<where the decision was made, and on what>\""))

    dest = Path(a.out).resolve() if a.out else (review / "APPROVAL-PACKAGE.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")

    print(f"wrote {dest.relative_to(REPO).as_posix()}")
    print(f"  §7 items present  {sum(present.values())}/{len(SECTION_7_ITEMS)}")
    for k in missing:
        print(f"  not present       {k}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
