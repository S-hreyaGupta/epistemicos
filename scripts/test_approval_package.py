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
    #
    # --out, to a temp path. Without it the generator writes to its default,
    # which is the committed APPROVAL-PACKAGE.md of a finished review, so
    # running this suite silently rewrote a real artifact — in CI invisibly,
    # because the checkout is thrown away, and locally as a dirty working tree
    # someone could commit without noticing. Found 18 September, by `git status`
    # after a routine local CI run, not by anything here.
    review_dir = REPO / "runs" / "BOOTSTRAP-001" / "plan-review"
    canonical = review_dir / "APPROVAL-PACKAGE.md"
    ledger = review_dir / "ledger.json"

    # Everything the run owns, watched as a whole rather than one file of it.
    def snapshot() -> dict[Path, bytes]:
        return {p: p.read_bytes() for p in sorted(review_dir.rglob("*"))
                if p.is_file()}

    before = snapshot()
    tmp_out = Path(tempfile.mkdtemp()) / "APPROVAL-PACKAGE.md"
    r = run("--run", "BOOTSTRAP-001", "--type", "plan",
            "--out", str(tmp_out), cwd=REPO)
    if r.returncode != 0:
        failures.append(f"could not build a package for BOOTSTRAP-001:\n"
                        f"{r.stdout}{r.stderr}")
        text = ""
    else:
        text = tmp_out.read_text(encoding="utf-8")
        ok("a package is produced for a run with frozen cycles")

    # The one thing it must never do.
    #
    # This control used to compare ledger.json alone and pass, while the same
    # call overwrote APPROVAL-PACKAGE.md in the directory next to it. The
    # package is part of the record it describes, so the control was named for
    # the right rule and watching one file of it. Comparing the whole review
    # directory is what the sentence below actually claims.
    after = snapshot()
    changed = sorted({p for p in set(before) | set(after)
                      if before.get(p) != after.get(p)})
    if changed:
        failures.append(
            "building a package altered the review it describes: "
            + ", ".join(p.relative_to(REPO).as_posix() for p in changed) +
            "\n      It assembles a record for a human to decide from and must "
            "write nothing\n      into that record. Pass --out.")
    else:
        ok("building a package writes nothing into the review it describes")

    if canonical.read_bytes() != before.get(canonical):
        failures.append("the committed APPROVAL-PACKAGE.md was modified by "
                        "this suite")

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

    # ---- SELF-F01: frozen cycles and no ledger is not zero findings ----
    # Alex Zamurko, 5 October: "Require the ledger whenever frozen review cycles
    # exist... Never translate missing evidence into zero findings", because
    # "absence of evidence must not become evidence of absence."
    #
    # This is where the tool used to explain, inside a produced package, that no
    # review had reported yet. The explanation was true and the package was
    # still a package: headings with nothing under them, in a document titled
    # for an approval decision. Now it refuses and names the state.
    #
    # Two fixtures, because missing and unreadable are two states, and one
    # control covering both would pass while either of them went unwatched.
    def _frozen_no_ledger(ledger_text, cycle_findings=None):
        f = Path(tempfile.mkdtemp()); made.append(f)
        (f / "runs" / "T-001" / "plan-review" / "cycle-01").mkdir(parents=True)
        if cycle_findings is not None:
            (f / "runs" / "T-001" / "plan-review" / "cycle-01"
             / "findings.json").write_text(cycle_findings, encoding="utf-8")
        (f / "scripts").mkdir()
        for name in ("approval_package.py", "loop_state.py", "ledger.py",
                     "validate_cycle.py", "cycle_projection.py", "authority.py",
                     "run_pins.py", "findings_format.py"):
            shutil.copy(SRC / name, f / "scripts" / name)
        (f / "runs" / "T-001" / "run.json").write_text(json.dumps({
            "run_id": "T-001", "mc1_enforcement": "CONVENTION_ONLY",
            "max_cycles": 4}), encoding="utf-8")
        if ledger_text is not None:
            (f / "runs" / "T-001" / "plan-review" / "ledger.json").write_text(
                ledger_text, encoding="utf-8")
        return run("--run", "T-001", "--type", "plan", cwd=f,
                   script=f / "scripts" / "approval_package.py")

    # BOOTSTRAP-003's reviewer on SELF-F01: "a readable ledger containing
    # `{"findings": {}}` beside a valid review reporting a finding still
    # produces an approval package with exit 0... the unresolved-findings
    # section says 'None' and its coverage item is marked present."
    #
    # The first repair handled the two ways a ledger can fail to be READ. This
    # is the third way it can fail to be TRUE, and it is the one that produces
    # a confident answer rather than an error. The ledger below is valid and
    # parses; it simply holds none of what the cycle beside it reported.
    _reported = json.dumps({
        "schema": "cycle-findings/1",
        "count": 1,
        "findings": [{"id": "D01-F01", "class": "MISSING REQUIREMENT",
                      "kind": "finding"}],
    }, indent=2)
    rr = _frozen_no_ledger(json.dumps({"review": "plan-review",
                                       "findings": {}}, indent=2),
                           cycle_findings=_reported)
    _o = rr.stdout + rr.stderr
    if rr.returncode == 0:
        failures.append(
            "a package was produced from a ledger that holds none of what the "
            "review beside it reported. The findings section would say None, "
            "which is a confident wrong answer rather than a missing one.")
    elif "CANNOT_ESTABLISH" not in _o or "reported" not in _o:
        failures.append(f"refused for a ledger disagreeing with its own "
                        f"review, but not for that reason:\n{_o[-400:]}")
    else:
        ok("refused: a readable ledger that holds none of what the review "
           "reported")

    for _label, _text in (("missing", None), ("unreadable", "{ not json")):
        rr = _frozen_no_ledger(_text)
        _o = rr.stdout + rr.stderr
        if rr.returncode == 0:
            failures.append(
                f"a package was produced for a run with a frozen cycle and a "
                f"{_label} ledger. Nothing in that run says what any reviewer "
                f"found, and the package presented the silence under its own "
                f"findings headings.")
        elif "CANNOT_ESTABLISH" not in _o:
            failures.append(f"refused for a {_label} ledger, but without the "
                            f"explicit state:\n{_o[-400:]}")
        else:
            ok(f"refused: frozen cycles and a {_label} ledger, "
               f"CANNOT_ESTABLISH")

    # SELF-F01, third pass. BOOTSTRAP-003 cycle 02: the package grouped
    # findings by the `state` field cached in the ledger rather than by the
    # state the controller reconstructs. Invalidate the cycle carrying a
    # demonstration and the cached RESOLVED survives, so the controller says
    # OPEN and CONTINUE while the package says "None" under unresolved and
    # counts one resolved. Alex Zamurko called it critical, because the
    # reporting layer was presenting a cleaner state than the authoritative
    # reconstruction.
    #
    # The fixture needs cycles that actually pass MC-2, which test_ledger
    # already knows how to build. Imported rather than copied: a second
    # cycle-builder here would be free to drift from the one the controller's
    # own suite uses, and this file would then be testing a shape no real run
    # has.
    import test_ledger as _TL

    def _section(text: str, heading: str) -> str:
        """Just that section, not everything after its heading.

        The package ends with the full ledger inside a <details> block, so
        `split(heading)[-1]` reaches a JSON dump naming every finding. The
        first version of the resolved-section check did exactly that and
        reported a finding as listed under a heading it never appeared beneath.
        """
        rest = text.split(heading, 1)[-1]
        for stop in ("\n<details", "\n## ", "\n### "):
            rest = rest.split(stop, 1)[0]
        return rest

    _lr, _commit = _TL.make_repo()
    made.append(_lr)
    shutil.copy2(SRC / "approval_package.py", _lr / "scripts")
    shutil.copy2(SRC / "authority.py", _lr / "scripts")
    _rev = _lr / "runs" / "T-001" / "plan-review"
    _TL.make_cycle(_lr, _rev, 1, _commit)
    _TL.make_cycle(_lr, _rev, 2, _commit)
    # Cycle 1 reports the finding; cycle 2 demonstrates the repair.
    for _n, _body, _entry in (
            (1, "Finding ID: C01-F01\nClass: UNTESTED RULE\n",
             {"id": "C01-F01", "class": "UNTESTED RULE"}),):
        _c = _rev / f"cycle-{_n:02d}"
        (_c / "codex-output-raw.md").write_text(_body, encoding="utf-8")
        (_c / "findings.json").write_text(json.dumps({
            "schema": "cycle-findings/1", "cycle": _n, "count": 1,
            "findings": [_entry]}, indent=2), encoding="utf-8")
    _TL.ledger(_lr, "raise", "--review", str(_rev), "--cycle", "1",
               "--id", "C01-F01", "--class", "UNTESTED RULE",
               "--source", "CODEX_REVIEW")
    _TL.ledger(_lr, "respond", "--review", str(_rev), "--cycle", "1",
               "--id", "C01-F01", "--disposition", "ACCEPT", "--note", "fix")
    _TL.ledger(_lr, "resolve", "--review", str(_rev), "--cycle", "2",
               "--id", "C01-F01", "--evidence", "demonstrated")

    # The baseline: with both cycles valid the finding really is resolved, and
    # the package should say so. Without this the control below would pass on a
    # package that calls everything unresolved.
    _pb = Path(tempfile.mkdtemp()) / "base.md"
    _rb = run("--run", "T-001", "--type", "plan", "--out", str(_pb), cwd=_lr,
              script=_lr / "scripts" / "approval_package.py")
    if _rb.returncode != 0:
        failures.append(f"a run whose demonstration is intact could not "
                        f"produce a package:\n{_rb.stdout}{_rb.stderr}")
    # The resolved section reports a COUNT, not identifiers, so this asserts on
    # the count and on the unresolved section being empty. Checking for the
    # identifier here passed for a while against the full-ledger dump at the
    # foot of the document, which names every finding regardless of state.
    elif ("1 resolved." not in _section(_pb.read_text(encoding="utf-8"),
                                        "### Resolved findings")
          or "None." not in _section(_pb.read_text(encoding="utf-8"),
                                     "### Unresolved findings")):
        failures.append(
            "a genuinely resolved finding is not reported as resolved with "
            "nothing unresolved, so the control below proves nothing")
    else:
        ok("a demonstrated repair is reported as resolved")

    # Now invalidate only the cycle that carried the demonstration. The ledger
    # is untouched and still caches RESOLVED.
    (_rev / "cycle-02" / "codex-output-raw.md").write_text("", encoding="utf-8")
    _cached = json.loads((_rev / "ledger.json").read_text(encoding="utf-8"))
    if _cached["findings"]["C01-F01"].get("state") != "RESOLVED":
        failures.append("the fixture's ledger does not cache RESOLVED, so "
                        "nothing stale is being tested")
    _pi = Path(tempfile.mkdtemp()) / "invalid.md"
    _ri = run("--run", "T-001", "--type", "plan", "--out", str(_pi), cwd=_lr,
              script=_lr / "scripts" / "approval_package.py")
    _itext = _pi.read_text(encoding="utf-8") if _pi.exists() else ""
    _unres = _section(_itext, "### Unresolved findings")
    if _ri.returncode != 0:
        # Refusing is also correct: his instruction was to derive the state
        # from the controller or refuse when it cannot be established.
        if "CANNOT_ESTABLISH" in (_ri.stdout + _ri.stderr):
            ok("an invalidated demonstration makes the package refuse rather "
               "than report the stale state")
        else:
            failures.append(f"the package failed for some other reason\n"
                            f"{(_ri.stdout + _ri.stderr)[-400:]}")
    elif "C01-F01" not in _unres:
        failures.append(
            "the cycle carrying the demonstration was invalidated, the "
            "controller reconstructs the finding as OPEN, and the package "
            "still does not list it as unresolved. The reporting layer is "
            "presenting a cleaner state than the authoritative one.")
    elif "None." not in _section(_itext, "### Resolved findings"):
        failures.append(
            "the finding is listed as unresolved and the resolved section "
            "still counts one, so the two sections disagree about the same "
            "finding")
    else:
        ok("an invalidated demonstration is reported as unresolved, not from "
           "the ledger's cached RESOLVED")

    # The positive, so the two refusals above cannot be "refuse everything".
    # BOOTSTRAP-002 has four frozen cycles and a recorded ledger.
    # --out again, because its package is tracked too.
    b2_dir = REPO / "runs" / "BOOTSTRAP-002" / "plan-review"
    b2_before = {p: p.read_bytes() for p in sorted(b2_dir.rglob("*"))
                 if p.is_file()}
    p2 = Path(tempfile.mkdtemp()) / "APPROVAL-PACKAGE.md"
    r = run("--run", "BOOTSTRAP-002", "--type", "plan",
            "--out", str(p2), cwd=REPO)
    if any(p.read_bytes() != b for p, b in b2_before.items()):
        failures.append("building BOOTSTRAP-002's package altered its review "
                        "directory")
    if r.returncode != 0:
        failures.append(f"a run with frozen cycles and a recorded ledger "
                        f"should produce a package:\n{r.stdout}{r.stderr}")
    else:
        t2 = p2.read_text(encoding="utf-8")
        if "### Unresolved findings" not in t2:
            failures.append(
                "the package for a run with a ledger does not present "
                "unresolved findings under their own heading")
        else:
            ok("a run with frozen cycles and a recorded ledger produces a "
               "package")

        # SELF-F01's own ruling: implementer-disclosed defects appear in the
        # package, under their own heading, separately from reviewer findings.
        # Read out of the register rather than restated here, so an entry that
        # stops being shown shows up as missing instead of being agreed with.
        reg = json.loads(
            (REPO / "registers" / "implementer-disclosed.json")
            .read_text(encoding="utf-8"))
        live = [k for k, v in reg.get("entries", {}).items()
                if v.get("state") != "RESOLVED"]
        required = ("description", "discovery_source", "affected_component",
                    "severity", "state", "proposed_repair", "evidence")
        thin = [f"{k}.{f}" for k, v in reg.get("entries", {}).items()
                for f in required if not v.get(f)]
        if thin:
            failures.append(
                "the register is missing fields the ruling names: "
                + ", ".join(thin[:6]))
        elif "## Implementer-disclosed defects" not in t2:
            failures.append(
                "the package has no implementer-disclosed section. A defect "
                "disclosed outside the ledger and then absent from the package "
                "is disclosed to nobody who matters.")
        elif t2.index("## Implementer-disclosed defects") < t2.index("## Findings"):
            failures.append("implementer-disclosed defects are presented above "
                            "the reviewer findings; they must be separate and "
                            "subordinate, not first")
        elif [k for k in live if k not in t2]:
            failures.append(
                "the register holds unresolved entries the package does not "
                "name: " + ", ".join(k for k in live if k not in t2))
        else:
            ok(f"{len(live)} implementer-disclosed defect(s) appear under "
               f"their own heading, after the reviewer findings")

        # The section as the package actually laid it out, split per entry, so
        # the two controls below assert about one entry's own block rather
        # than about the whole document. My earlier controls in this file
        # passed by matching text that belonged to a different part of the
        # page, which is the same defect as the one they were watching for.
        _sec = t2.split("## Implementer-disclosed defects", 1)[-1]
        _sec = _sec.split("## MC-2 conformance", 1)[0]
        _blocks = {}
        for _chunk in _sec.split("\n### ")[1:]:
            _blocks[_chunk.split("\n", 1)[0].split(" ")[0].strip("*` ")] = _chunk

        # The glossary paragraph under each entry must describe that entry's
        # state. It used to print the REPAIRED_UNREVIEWED text unconditionally,
        # so an OPEN defect with no repair carried a line reading "a repair has
        # landed with controls behind it".
        wrong_gloss = []
        for k, v in reg.get("entries", {}).items():
            st = v.get("state")
            if st == "RESOLVED" or k not in _blocks:
                continue
            for other in reg.get("states", {}):
                if other != st and f"`{other}` means" in _blocks[k]:
                    wrong_gloss.append(f"{k} is {st} but its block explains {other}")
        if wrong_gloss:
            failures.append("an entry is glossed with a state it is not in: "
                            + "; ".join(wrong_gloss))
        elif not _blocks:
            failures.append("no implementer-disclosed entry blocks were found "
                            "to check, so this control proves nothing")
        else:
            ok("each disclosed defect is glossed with its own state, not with "
               "REPAIRED_UNREVIEWED regardless")

        # A resolved entry must still be named. Dropping it entirely leaves a
        # reader following one disclosure across packages unable to tell
        # resolution from deletion.
        done = [k for k, v in reg.get("entries", {}).items()
                if v.get("state") == "RESOLVED"]
        if not done:
            failures.append(
                "the register currently holds no RESOLVED entry, so the "
                "control for naming resolved entries did not exercise "
                "anything. It is reported rather than passed.")
        elif "### Resolved and no longer outstanding" not in _sec:
            failures.append(
                "resolved implementer-disclosed entries are dropped from the "
                "package with no trace: " + ", ".join(sorted(done)))
        elif [k for k in done if k not in _sec]:
            failures.append(
                "the resolved summary omits: "
                + ", ".join(k for k in done if k not in _sec))
        else:
            ok(f"{len(done)} resolved disclosure(s) are still named, so "
               f"resolution is distinguishable from deletion")

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
