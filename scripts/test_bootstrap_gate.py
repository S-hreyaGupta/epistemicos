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
import re
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


def sha256_file(p: Path) -> str:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(with_evidence: bool = True) -> Path:
    """A throwaway repo carrying the real gate, components and a review target."""
    tmp = Path(tempfile.mkdtemp(prefix="bgate-")).resolve()
    (tmp / "scripts").mkdir()
    (tmp / "specs").mkdir()
    for n in ("bootstrap_gate.py", "validate_cycle.py", "run_review.py",
              "ledger.py", "loop_state.py", "findings_format.py",
              "cycle_projection.py", "authority.py"):
        shutil.copy2(SRC / n, tmp / "scripts" / n)
    shutil.copy2(REPO / "specs" / "evidence-schema-v1.0.md",
                 tmp / "specs" / "evidence-schema-v1.0.md")
    if with_evidence:
        for n in EVIDENCE:
            write_lf(tmp / "bootstrap-review" / n, f"contents of {n}\n")
    freeze_target(tmp)
    return tmp


def freeze_target(root: Path) -> Path:
    """A target.json covering exactly the files the gate covers.

    B01-F09 requires the decision to be bound to what was reviewed, so a fixture
    that wants to approve needs a target to bind to. Built from the gate's own
    covered set, so the two agree by construction here and any disagreement in a
    control below is one the control deliberately introduced.
    """
    import importlib.util
    spec_ = importlib.util.spec_from_file_location(
        "_bg_fixture", root / "scripts" / "bootstrap_gate.py")
    mod = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(mod)

    tgt = root / "runs" / "B-001" / "plan-review" / "cycle-01" / "target.json"
    write_lf(tgt, json.dumps({
        "review_type": "plan", "run_id": "B-001", "cycle": 1,
        "plan_files": [{"path": rel, "sha256": digest}
                       for rel, digest in mod.covered(root).items()],
    }, indent=2) + "\n")
    return tgt


TARGET = "runs/B-001/plan-review/cycle-01/target.json"


def gate(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "scripts" / "bootstrap_gate.py"),
                           *args], cwd=str(root), capture_output=True, text=True)


def approve(root: Path, who: str = "Alex Zamurko") -> subprocess.CompletedProcess:
    return gate(root, "record", "--decision", "APPROVE", "--decided-by", who,
                "--note", "#gap, 9 Sep 2026 00:03, Alex Zamurko: reviewed and "
                          "approved for the bootstrap exception",
                "--target", TARGET)


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def ok(msg: str) -> None:
        print(f"  [ok] {msg}")

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
                   gate(root, "record", "--decision", "APPROVE", "--decided-by", "  ",
                        "--note", "#gap, 9 Sep 2026, some attribution text here",
                        "--target", TARGET))

    # A name in --decided-by is typed by whoever ran the command. Without an
    # attribution the record cannot distinguish a relayed approval from an
    # invented one.
    expect_refused("record an approval with no attribution", "--note is required",
                   gate(root, "record", "--decision", "APPROVE",
                        "--decided-by", "Alex Zamurko", "--target", TARGET))

    expect_refused("attribution too thin to identify anything", "--note is required",
                   gate(root, "record", "--decision", "APPROVE",
                        "--decided-by", "Alex Zamurko", "--note", "ok",
                        "--target", TARGET))

    # ---- a decision that is not an approval ----
    root = build(); made.append(root)
    r = gate(root, "record", "--decision", "RETURN_FOR_REWORK",
             "--decided-by", "Alex Zamurko",
             "--note", "#gap, 9 Sep 2026, Alex Zamurko: rework required",
             "--target", TARGET)
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
             "--note", "#gap, 9 Sep 2026, Alex Zamurko: re-approved after rework",
             "--target", TARGET, "--supersede")
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
    freeze_target(root)
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
    # B01-F16: the first version of this control inserted
    #     _HELPER = "helper_module.py"
    # which is a string, so it exercised filename discovery — the route that
    # already worked — and said nothing about imports, the route that did not.
    # This uses a real import whose value the component actually reads, so the
    # dependency genuinely affects behaviour rather than merely being named.
    # The module name must appear nowhere in any covered file, including in
    # comments. An earlier attempt used `helper_module`, which bootstrap_gate.py
    # mentions in the docstring explaining this very finding — so the
    # filename scan pulled it in from the documentation and the control passed
    # with import discovery entirely removed. Same defect, one layer out.
    HELPER = "zqx_probe_dep"
    root = build(); made.append(root)
    write_lf(root / "scripts" / f"{HELPER}.py", "THRESHOLD = 64\n")
    vc = root / "scripts" / "validate_cycle.py"
    vc.write_text(
        vc.read_text(encoding="utf-8").replace(
            "import hashlib",
            f"import hashlib\nimport {HELPER}\n_T = {HELPER}.THRESHOLD",
            1),
        encoding="utf-8")
    # Re-freeze: the edited component is what a reviewer would have seen in this
    # scenario, and B01-F09 now binds the decision to the frozen target.
    freeze_target(root)

    r = approve(root)
    if r.returncode != 0:
        failures.append(f"could not approve the dependency fixture:\n{r.stdout}{r.stderr}")
    else:
        d = json.loads((root / "bootstrap-review" / "decision.json")
                       .read_text(encoding="utf-8"))
        if f"scripts/{HELPER}.py" not in d.get("components", {}):
            failures.append(
                "a module referenced by validate_cycle.py was not pulled into "
                "the pinned set. The closure is empty on the real repo, so "
                "without this control an inert scanner would look correct.")
        elif f"scripts/{HELPER}.py" not in d.get("dependencies", {}):
            failures.append("the dependency was pinned but not recorded as a "
                            "dependency, so the record does not say why it is "
                            "covered")
        else:
            print("  [ok] a referenced local module is discovered and pinned")

            h = root / "scripts" / f"{HELPER}.py"
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
        write_lf(root / "scripts" / "zqx_late_dep.py", "LIMIT = 4\n")
        lp = root / "scripts" / "loop_state.py"
        lp.write_text(lp.read_text(encoding="utf-8") +
                      "\nimport zqx_late_dep\n_L = zqx_late_dep.LIMIT\n",
                      encoding="utf-8")
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

    # ---- B01-F15: no claim stronger than CONVENTION_ONLY supports ----
    # MC-1: while enforcement is CONVENTION_ONLY, claims that findings are
    # immutable or that review input is technically protected "must not be
    # made". Two such claims had grown back by the time Codex read the code:
    # the schema said freezing "proves the artifact did not change", and the
    # comment here said self-hashing closed the replace-evaluate hole.
    #
    # Prose drifts in the flattering direction on its own. A hash check reads
    # like a guarantee to whoever writes about it next, so this refuses the
    # phrasings rather than trusting everyone to remember the distinction.
    print()
    print("the decision is bound to what was reviewed")

    # ---- B01-F09 ----
    # Approval must be about the artifacts a reviewer saw, not about whatever is
    # on disk when someone gets round to recording the decision. Without this,
    # approve-then-edit-then-record produces an approval covering code nobody
    # reviewed, under evidence describing code that no longer exists — and
    # `check` then verifies the decision against itself and passes forever.
    root = build(); made.append(root)
    expect_refused("record a decision with no --target at all",
                   "--target is required",
                   gate(root, "record", "--decision", "APPROVE",
                        "--decided-by", "Alex Zamurko",
                        "--note", "#gap, 9 Sep 2026, approved after review"))

    root = build(); made.append(root)
    vc = root / "scripts" / "validate_cycle.py"
    vc.write_text(vc.read_text(encoding="utf-8") + "\n# edited after the freeze\n",
                  encoding="utf-8")
    expect_refused("record a decision after a component changed post-freeze",
                   "changed after the freeze", approve(root))

    # ---- B01-F10 ----
    # The target carried six artifacts and the covered set held five, so editing
    # the evidence schema did not invalidate its own approval. Both directions
    # of that mismatch are refusals now.
    root = build(); made.append(root)
    tgt = root / TARGET
    d = json.loads(tgt.read_text(encoding="utf-8"))
    d["plan_files"] = [e for e in d["plan_files"]
                       if e["path"] != "specs/evidence-schema-v1.0.md"]
    write_lf(tgt, json.dumps(d, indent=2) + "\n")
    expect_refused("a covered file the review target never contained",
                   "was not in the review target", approve(root))

    root = build(); made.append(root)
    tgt = root / TARGET
    d = json.loads(tgt.read_text(encoding="utf-8"))
    d["plan_files"].append({"path": "specs/unreviewed-extra.md",
                            "sha256": "f" * 64})
    write_lf(tgt, json.dumps(d, indent=2) + "\n")
    expect_refused("a reviewed artifact the gate does not cover",
                   "not in the covered set", approve(root))

    # And the schema must actually be in the covered set, or F10 is only
    # half-repaired: the mismatch check would pass while nothing pinned it.
    root = build(); made.append(root)
    if approve(root).returncode != 0 or gate(root, "check").returncode != 0:
        failures.append("the six-artifact fixture did not reach an approved state")
    else:
        sch = root / "specs" / "evidence-schema-v1.0.md"
        sch.write_text(sch.read_text(encoding="utf-8") + "\n<!-- later edit -->\n",
                       encoding="utf-8")
        expect_refused("approval surviving an edit to the evidence schema",
                       "has changed since it was reviewed", gate(root, "check"))

    print()
    print("no claim stronger than CONVENTION_ONLY")

    # Word-boundary on both sides: an earlier version used r"prove[sd]?\b" and
    # matched the "prove" inside "approved", flagging every mention of the
    # approved-plan hash. And "prevents" was a trigger until it flagged "the
    # defect this gate exists to prevent", which is a claim about a logic
    # property rather than about enforcement. Both were noise, and a check that
    # cries wolf gets silenced rather than heeded.
    OVERCLAIM = (
        (r"\bprove[sd]?\b|\bproof\b", "proof"),
        (r"\bimmutab", "immutability"),
        (r"technically protected", "technical protection"),
        (r"cannot be (?:changed|edited|modified|overwritten|rewritten)",
         "prevention of modification"),
        (r"\bguarantee[sd]?\b", "guarantee"),
    )
    # Denying the claim is the point, not a violation of it. Checked over a
    # two-line window because these are wrapped paragraphs and the negation
    # frequently lands on the following line.
    DENIAL = re.compile(
        r"\b(?:not|never|no|nothing|cannot|rather than|instead of|without|"
        r"neither|nor|unsupportable|forbid)", re.I)

    scanned = [REPO / "specs" / "evidence-schema-v1.0.md"]
    scanned += [REPO / c for c in
                ("scripts/validate_cycle.py", "scripts/run_review.py",
                 "scripts/ledger.py", "scripts/loop_state.py",
                 "scripts/bootstrap_gate.py")]

    def sentences(text: str):
        """(sentence, first line number). Prose here wraps, so a sentence is the
        unit that carries the claim; a line is not."""
        line_of, pos = [], 0
        for n, ln in enumerate(text.splitlines(keepends=True), 1):
            line_of.append((pos, n))
            pos += len(ln)
        # Strip comment markers before flattening. Left in, a bare "#" between
        # two comment paragraphs stops the sentence splitter, so the claim in
        # the second paragraph merges with a sentence from the first — and if
        # that one contains a negation, the claim is silently excused. That is
        # how "Self-hashing guarantees tamper evidence" went unflagged.
        stripped = []
        for ln in text.splitlines():
            body = re.sub(r"^\s*#\s?", "", ln)
            stripped.append("" if not body.strip() else body)
        flat = re.sub(r"\s*\n\s*", " ", "\n".join(stripped))
        flat = re.sub(r"\n\s*\n", ".\n", flat)
        # Offsets shift once newlines collapse, so locate each sentence by
        # searching the original for its opening words instead.
        for s in re.split(r"(?<=[.:])\s+(?=[A-Z`\"'(])", flat):
            s = s.strip()
            if not s:
                continue
            head = re.escape(s[:40].strip())
            m = re.search(head.replace(r"\ ", r"\s+"), text)
            n = 1
            if m:
                n = next((ln for off, ln in reversed(line_of)
                          if off <= m.start()), 1)
            yield s, n

    offenders = []
    for f in scanned:
        if not f.is_file():
            continue
        for sentence, n in sentences(f.read_text(encoding="utf-8")):
            # The denial has to be in the same sentence as the claim. An earlier
            # version looked at a window of neighbouring lines, which in prose
            # discussing what things do and do not establish suppressed almost
            # every real over-claim — including all three Codex had flagged.
            if DENIAL.search(sentence):
                continue
            for pat, label in OVERCLAIM:
                if re.search(pat, sentence, re.I):
                    offenders.append(
                        f"{f.relative_to(REPO).as_posix()}:{n} claims {label}\n"
                        f"        {sentence[:88]}")
                    break
    if offenders:
        failures.append(
            "language asserting more than CONVENTION_ONLY supports:\n      "
            + "\n      ".join(offenders) +
            "\n      MC-1 forbids these claims while enforcement is by "
            "convention. Restate as\n      detection that holds when the checks "
            "run faithfully, or negate the claim explicitly.")
    else:
        ok(f"{len(scanned)} covered files carry no unqualified proof, "
           "immutability or prevention claim")

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
