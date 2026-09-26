#!/usr/bin/env python3
"""Which decisions are made in more than one file?

    python _probe\\duplicated_decisions.py

Read-only. Reports candidates; establishes nothing on its own.

Seven of the eight findings repaired on 26 September were one shape: a rule
that existed in several places, with one copy shorter than the others.

    C01-F01  replay, last_authorized and skipped_events each walked a
             finding's history with their own transition rules, and the
             reopening guard was in one of the three
    C01-F04  the freeze path validated the amendment chain; MC-2 replayed it
             without validating
    C01-F05  `startswith("EXEMPT") else PROTOCOL` written out in four files
    C01-F08  the commit and the hash recorded by two separate steps that
             never compared their answers

Each was found by a reviewer reading code. The cycle-02 prompt asks the next
reviewer to look for a fourth copy of the rules just merged, which is a fair
thing to ask and a poor thing to do by eye across ten files.

What this looks for
-------------------
A DECISION, not a mention: a string literal used in a comparison. `==`, `!=`,
`in`, `startswith`, `endswith`. Those are the shapes the four findings above
took. A dict lookup like `run["protocol"]` is shared vocabulary rather than a
duplicated rule, so subscripts and plain arguments are ignored.

A literal compared against in two or more of the covered files is a candidate
for a rule with more than one implementation. It is only a candidate:

    legitimate    a shared constant's VALUE appearing where it is defined and
                  where it is documented, or two files that both consume one
                  vocabulary the protocol fixes
    the defect    two files independently deciding the same question, which
                  is how they come to disagree

Distinguishing those needs reading, which is the point: this narrows ten files
to a list short enough to read.

What it cannot see
------------------
A rule duplicated without a literal. `if state == OPEN` uses a name, and
`Walk.apply`'s transitions are structure rather than strings. C01-F01 would
NOT have been caught by this. So a clean report is not evidence of no
duplication, and saying so is the whole reason this docstring exists.
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

# The gate's covered set, read rather than asserted.
import bootstrap_gate  # noqa: E402

COMPARE_METHODS = {"startswith", "endswith"}
# Short strings carry too little meaning to be a rule; single characters and
# separators are formatting.
MIN_LEN = 4

# A language idiom, not a rule anyone could implement twice.
IDIOMS = {"__main__"}

# Read on 26 September and accepted, with the reason. Small enough to read,
# which is the only thing that makes a list like this honest: the vacuity
# sweep's pinned twenty became 130 unread survivors, and the lesson there was
# that a list nobody re-reads is worse than no list.
#
# A candidate NOT here is new since that reading and has not been looked at.
REVIEWED = {
    "ACCEPT":
        "the ledger WRITES this event and cycle_projection REPLAYS it. One "
        "vocabulary with a producer and a consumer, not two implementations "
        "of one rule, and an event cycle_projection does not know refuses "
        "loudly rather than passing through.",
    "REJECT_WITH_REASON":
        "same as ACCEPT: written by the ledger, replayed by the projection.",
    "APPROVE":
        "two DIFFERENT records that happen to share a word. bootstrap_gate "
        "reads bootstrap-review/decision.json; validate_cycle reads the "
        "run's plan-approval/approval.json. Neither decides the other's "
        "question.",
    "plan":
        "REVIEW_TYPES, a vocabulary the protocol closes. Both sides enforce "
        "the closure: validate_cycle fails check 9 on a review_type outside "
        "it, and C01-F07 added check 7's agreement with the directory.",
    "implementation":
        "same as 'plan'.",
    "path":
        "a key in the hashed-artifact schema, checked for presence by both "
        "the gate and the validator. Shared schema vocabulary.",
    "sha256":
        "same as 'path'.",
}


class Decisions(ast.NodeVisitor):
    """String literals this file compares against, with line numbers."""

    def __init__(self) -> None:
        self.hits: dict[str, list[int]] = defaultdict(list)

    def _add(self, node, value) -> None:
        if (isinstance(value, str) and len(value) >= MIN_LEN
                and value not in IDIOMS):
            self.hits[value].append(node.lineno)

    def visit_Compare(self, node: ast.Compare) -> None:
        for side in [node.left, *node.comparators]:
            if isinstance(side, ast.Constant):
                self._add(node, side.value)
            # `x in ("a", "b")` is one decision over several values.
            elif isinstance(side, (ast.Tuple, ast.List, ast.Set)):
                for e in side.elts:
                    if isinstance(e, ast.Constant):
                        self._add(node, e.value)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (isinstance(node.func, ast.Attribute)
                and node.func.attr in COMPARE_METHODS):
            for a in node.args:
                if isinstance(a, ast.Constant):
                    self._add(node, a.value)
                elif isinstance(a, (ast.Tuple, ast.List, ast.Set)):
                    for e in a.elts:
                        if isinstance(e, ast.Constant):
                            self._add(node, e.value)
        self.generic_visit(node)


def main() -> int:
    covered = [p for p in bootstrap_gate.covered(REPO) if p.endswith(".py")]
    print(f"  {len(covered)} covered python files, read from "
          f"bootstrap_gate.covered()\n")

    per_file: dict[str, dict[str, list[int]]] = {}
    for rel in covered:
        src = (REPO / rel).read_text(encoding="utf-8")
        d = Decisions()
        d.visit(ast.parse(src))
        per_file[rel] = dict(d.hits)

    shared: dict[str, dict[str, list[int]]] = defaultdict(dict)
    for rel, hits in per_file.items():
        for lit, lines in hits.items():
            shared[lit][rel] = lines

    multi = {lit: files for lit, files in shared.items() if len(files) > 1}
    new = sorted(set(multi) - set(REVIEWED))
    gone = sorted(set(REVIEWED) - set(multi))

    print(f"  {len(multi)} literal(s) compared against in more than one "
          f"file.")
    print(f"  {len(multi) - len(new)} read on 26 September and accepted, "
          f"{len(new)} not.\n")

    if new:
        print("  NOT YET READ. Each is a candidate, not a finding. The")
        print("  question for each is whether the files consume one")
        print("  vocabulary the protocol fixes, or independently decide the")
        print("  same question. The second is how they come to disagree.\n")
        for lit in new:
            print(f"    {lit!r}   in {len(multi[lit])} files")
            for rel in sorted(multi[lit]):
                print(f"      {rel}:"
                      f"{','.join(str(n) for n in multi[lit][rel])}")
            print()

    if gone:
        print("  Accepted previously and no longer duplicated. Good, and the")
        print("  reason should come out of REVIEWED deliberately:\n")
        for lit in gone:
            print(f"    {lit!r}")
        print()

    if new or gone:
        return 1

    print("  Nothing new. The accepted set is unchanged, and each entry's")
    print("  reason is in REVIEWED beside it.")
    print("  This does not establish that no rule is duplicated: a rule with")
    print("  no string literal in it is invisible here, and C01-F01 was one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
