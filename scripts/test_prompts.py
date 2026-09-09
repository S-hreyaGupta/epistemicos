#!/usr/bin/env python3
"""Conformance checks for the five production prompts.

A prompt is a specification the model is asked to follow, so it can drift from
the protocol exactly the way code can, and more quietly: nothing errors when a
prompt quietly permits a seventh finding class or drops a required field.

    python scripts/test_prompts.py

Exit 0 = the prompts agree with the protocol.

Everything below is read out of the authoritative protocol rather than restated
here. If the protocol changes and a prompt does not, this fails. That is the
whole point: a hand-copied vocabulary is a vocabulary that will eventually differ
from its source and nobody will notice.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# The governing protocol, not a superseded one. This pin was left at v1.0 when
# v1.1 landed, which is precisely the drift this file exists to catch: it kept
# passing because the vocabulary happened not to change between versions.
PROTOCOL = REPO / "specs" / "implementation-review-protocol-v1.1.md"
PROMPTS = REPO / "specs" / "prompts"

FIVE = {
    "01-claude-audit-plan.md":        "1",
    "02-codex-plan-review.md":        "4",
    "03-claude-findings-response.md": "5",
    "04-claude-implement.md":         "8",
    "05-codex-code-review.md":        "11",
}

# The prompts that hand Codex the finding vocabulary.
REVIEW_PROMPTS = ("02-codex-plan-review.md", "05-codex-code-review.md")


def main() -> int:
    failures: list[str] = []
    proto = PROTOCOL.read_text(encoding="utf-8")

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    # ---- all five present and non-trivial ----
    print("presence")
    for name in FIVE:
        p = PROMPTS / name
        if not p.is_file():
            failures.append(f"missing prompt: {name}")
        elif p.stat().st_size < 500:
            failures.append(f"{name} is suspiciously short ({p.stat().st_size} bytes); "
                            "the runner accepts any non-empty file, so a stub would "
                            "freeze a cycle with no review criteria in it")
    if not failures:
        ok("all five prompts present, none a stub")
    before = len(failures)

    # ---- the closed vocabulary, read from the protocol ----
    print()
    print("closed finding vocabulary")
    block = re.search(r"Codex uses the following closed finding vocabulary:\n(.*?)\n\n"
                      r"Every finding receives", proto, re.S)
    if not block:
        failures.append("could not locate the vocabulary in the protocol; this check "
                        "cannot run and that is itself the finding")
        vocab = []
    else:
        vocab = [l.strip() for l in block.group(1).splitlines() if l.strip()]
        print(f"        protocol declares {len(vocab)}")
        for v in vocab:
            print(f"          {v}")

    for name in REVIEW_PROMPTS:
        text = (PROMPTS / name).read_text(encoding="utf-8")
        missing = [v for v in vocab if v not in text]
        if missing:
            failures.append(f"{name} omits finding classes the protocol defines: "
                            f"{', '.join(missing)}")
        # A seventh class would let the reviewer widen its own scope, which is
        # what the closed vocabulary exists to prevent.
        # A class name is all-caps words separated by single spaces. Runs of
        # two or more spaces mean column alignment in an inputs block, not a
        # vocabulary term, and matching those was a bug in this check.
        allcaps = {m.strip() for m in
                   re.findall(r"^\s{0,4}([A-Z]+(?: [A-Z]+)+)\s*$", text, re.M)
                   if "  " not in m.strip()}
        extra = allcaps - set(vocab) - {"OUT OF VOCABULARY", "REJECT WITH REASON"}
        if extra:
            failures.append(f"{name} appears to introduce classes outside the "
                            f"closed vocabulary: {', '.join(sorted(extra))}")
    if len(failures) == before:
        ok("both review prompts carry all six classes verbatim, and no seventh")
    before = len(failures)

    # ---- the finding block fields, read from the protocol ----
    print()
    print("finding block")
    fields = re.search(r"Finding ID: C02-F03\nClass:(.*?)Required correction:", proto, re.S)
    required = ["Finding ID", "Class", "Requirement ID", "Evidence", "Finding",
                "Required correction"] if fields else []
    for name in REVIEW_PROMPTS:
        text = (PROMPTS / name).read_text(encoding="utf-8")
        absent = [f for f in required if f + ":" not in text]
        if absent:
            failures.append(f"{name} drops required finding fields: {', '.join(absent)}")
    if required and len(failures) == before:
        ok(f"both review prompts require all {len(required)} finding fields")
    before = len(failures)

    # ---- OUT OF VOCABULARY is a diagnostic, not a finding ----
    # Ruled 8 September 2026: kept, but with no Finding ID, never written to
    # findings.json, never in a state, no effect on loop state. ledger.py refuses
    # it, so the enforcement is real; this checks the prompts still tell the
    # reviewer why, because a reviewer that is refused without being told will
    # reach for one of the six instead, which is worse than the hole.
    print()
    print("OUT OF VOCABULARY")
    ruled = {
        "no Finding ID":        (r"no Finding ID", ),
        "not in findings.json": (r"findings\.json", ),
        "not a lifecycle state": (r"OPEN, RESOLVED or DISPUTED",
                                  r"OPEN / RESOLVED / DISPUTED"),
        "no effect on loop state": (r"loop.state", ),
    }
    for name in REVIEW_PROMPTS:
        text = (PROMPTS / name).read_text(encoding="utf-8")
        if "OUT OF VOCABULARY" not in text:
            continue  # removing it entirely is a different decision, not drift
        absent = [label for label, pats in ruled.items()
                  if not any(re.search(p, text, re.I) for p in pats)]
        if absent:
            failures.append(f"{name} keeps OUT OF VOCABULARY but no longer states "
                            f"what makes it a non-finding: {', '.join(absent)}. "
                            "ledger.py refuses it either way, so the prompt and "
                            "the code would disagree about why.")
    if len(failures) == before:
        ok("both review prompts state all four non-finding constraints")
    before = len(failures)

    # ---- dispositions, §5 ----
    print()
    print("dispositions")
    resp = (PROMPTS / "03-claude-findings-response.md").read_text(encoding="utf-8")
    for d in ("ACCEPT", "REJECT_WITH_REASON"):
        if d not in resp:
            failures.append(f"the response prompt does not name {d}")
    if "RESOLVED" in resp and "does not resolve" not in resp.lower() \
            and "NEXT review target" not in resp:
        failures.append("the response prompt mentions RESOLVED without stating that "
                        "ACCEPT does not resolve; §5 gives RESOLVED only once the "
                        "repair is demonstrated in the next review target")
    if len(failures) == before:
        ok("the response prompt carries both dispositions and the ACCEPT limit")

    # ---- each prompt names the section it implements ----
    print()
    print("protocol anchoring")
    unanchored = []
    for name, section in FIVE.items():
        text = (PROMPTS / name).read_text(encoding="utf-8")
        if not re.search(rf"§{section}\b", text):
            unanchored.append(f"{name} (expected §{section})")
    if unanchored:
        failures.append("prompts that do not cite the protocol section they "
                        f"implement: {', '.join(unanchored)}")
    else:
        ok("every prompt cites the protocol section it implements")

    # ---- PLAN_DEVIATION, §9 ----
    print()
    print("PLAN_DEVIATION")
    impl = (PROMPTS / "04-claude-implement.md").read_text(encoding="utf-8")
    steps = ["PLAN_DEVIATION_ID", "affected requirement", "proposed plan change",
             "affected code/tests"]
    absent = [s for s in steps if s not in impl]
    if absent:
        failures.append(f"the implementation prompt drops §9 record fields: "
                        f"{', '.join(absent)}")
    elif "retrospectively" not in impl:
        failures.append("the implementation prompt does not carry §9's rule that a "
                        "deviation cannot be legitimised retrospectively at code "
                        "review, which is the part most easily skipped")
    else:
        ok("the implementation prompt carries §9's record fields and its "
           "retrospective-legitimisation bar")

    # ---- the two rulings that reversed an earlier reading ----
    # Both were judgement calls this file's author made where the protocol was
    # silent, and both were overruled on 8 September. They are under test because
    # a reverted judgement reverts quietly: the prompt still reads sensibly with
    # the old rule in it, and nothing else fails.
    print()
    print("rulings of 8 September")

    audit = (PROMPTS / "01-claude-audit-plan.md").read_text(encoding="utf-8")
    if re.search(r"no test is\s+`?PARTIAL`?", audit, re.I) or \
            re.search(r"implemented without the required test", audit, re.I):
        failures.append("01-claude-audit-plan.md again makes an untested "
                        "requirement PARTIAL. Ruled 8 September: the "
                        "implementation disposition and the verification status "
                        "stay separate, and absent tests are a test delta.")
    elif "separate" not in audit.lower():
        failures.append("01-claude-audit-plan.md no longer says the disposition "
                        "and test coverage are separate axes")
    else:
        ok("the audit prompt keeps disposition and test status separate")

    impl = (PROMPTS / "04-claude-implement.md").read_text(encoding="utf-8")
    criteria = ["normative behaviour", "ownership", "acceptance criteria",
                "required tests"]
    missing_c = [c for c in criteria if c not in impl.lower()]
    if missing_c:
        failures.append("04-claude-implement.md does not carry the explicit "
                        f"materiality criteria: {', '.join(missing_c)}. Ruled "
                        "8 September: apply the criteria first, and default to "
                        "MATERIAL only if uncertainty remains after them.")
    else:
        # The prompt quotes the ruling, and the quote contains the words "apply
        # explicit materiality criteria first". Searching the whole file for that
        # phrase therefore passed on a prompt whose own instruction had been
        # removed: quoting a rule satisfied a check meant to confirm the rule was
        # followed. Search the prompt's own text only, with quoted blocks (any
        # line indented four or more spaces) stripped out.
        own = "\n".join(l for l in impl.splitlines()
                        if not re.match(r"\s{4,}\S", l))
        pos_criteria = own.lower().find("normative behaviour")
        pos_default = own.lower().find("uncertainty remains")
        if not re.search(r"apply these criteria first", own, re.I):
            failures.append("04-claude-implement.md lists materiality criteria "
                            "but no longer instructs applying them before the "
                            "default, which is the part of the ruling that "
                            "changed behaviour")
        elif pos_criteria == -1 or pos_default == -1 or pos_criteria > pos_default:
            failures.append("04-claude-implement.md states the residual-"
                            "uncertainty default before the criteria it is meant "
                            "to follow; the order is the ruling")
        else:
            ok("the implementation prompt applies materiality criteria before "
               "the default, in its own words rather than the quoted ruling")

    # ---- the bootstrap prompt's control counts are real ----
    # The prompt tells the reviewer how well controlled these components are, as
    # a reason to trust them. A number typed into prose drifts the moment a
    # control is added, and an inflated one misrepresents the thing the reviewer
    # is being asked to rely on. So the counts are asserted there and verified
    # here by running the suites.
    print()
    print("bootstrap prompt control counts")
    boot = PROMPTS / "bootstrap-review.md"
    if not boot.is_file():
        failures.append("specs/prompts/bootstrap-review.md is missing; the "
                        "bootstrap review has no prompt to run against")
    else:
        text = boot.read_text(encoding="utf-8")
        claimed = {f"scripts/{m}": int(n) for m, n in
                   re.findall(r"scripts/(\w+\.py)\s+(\d+)\s+controls", text)}
        if not claimed:
            failures.append("bootstrap-review.md no longer states any control "
                            "counts, so nothing tells the reviewer whether these "
                            "components are controlled at all")
        wrong = []
        for rel, n in sorted(claimed.items()):
            p = REPO / rel
            if not p.is_file():
                wrong.append(f"{rel} is named but does not exist")
                continue
            import subprocess
            out = subprocess.run([sys.executable, str(p)], cwd=str(REPO),
                                 capture_output=True, text=True)
            actual = (out.stdout + out.stderr).count("[ok]")
            if actual != n:
                wrong.append(f"{rel}: prompt claims {n}, suite reports {actual}")
        if wrong:
            failures.append("bootstrap-review.md misstates its control counts:\n      "
                            + "\n      ".join(wrong))
        elif claimed:
            ok(f"all {len(claimed)} stated control counts match the suites")

        # Every component the gate covers must appear in the prompt, or it goes
        # to review unreviewed. bootstrap_gate.py was missing exactly this way.
        gate_py = REPO / "scripts" / "bootstrap_gate.py"
        if gate_py.is_file():
            import importlib.util as _il
            s_ = _il.spec_from_file_location("_bg_probe", gate_py)
            m_ = _il.module_from_spec(s_)
            s_.loader.exec_module(m_)
            required = list(m_.COMPONENTS) + list(m_.ALWAYS)
            unnamed = [c for c in required if c not in text]
            if unnamed:
                failures.append(
                    "bootstrap-review.md does not name every component the gate "
                    f"covers: {', '.join(unnamed)}. A component absent from the "
                    "prompt is one the reviewer is never asked about, while the "
                    "gate still treats it as reviewed.")
            else:
                ok(f"the prompt names all {len(required)} components the gate covers")

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("the five prompts agree with the protocol")
    return 0


if __name__ == "__main__":
    sys.exit(main())
