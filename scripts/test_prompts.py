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
PROTOCOL = REPO / "specs" / "implementation-review-protocol-v1.0.md"
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

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("the five prompts agree with the protocol")
    return 0


if __name__ == "__main__":
    sys.exit(main())
