#!/usr/bin/env python3
"""rc2 §19's Unicode gate item, demonstrated rather than assumed.

    python scripts/unicode_gate.py

Exit 0 = the execution environment satisfies rc2's Unicode requirement, or the
         gap is bounded and shown not to reach this contract's corpus.
Exit 1 = the gap reaches something this contract depends on.
Exit 2 = could not run.

Why this exists
---------------
rc2 §19 lists eight things required before the GSD pilot scope can be frozen.
Seven need a person. One is mechanically checkable and nobody had checked it:

    Unicode 15.0.0 behavior required by this contract is demonstrated in the
    execution environment

and §1.1 pins `Unicode = 15.0.0` alongside `spec_version` and
`citation_rule_version`. It sits in the rule-identity block, so it is part of
what makes two runs comparable.

It went unexamined because nothing fails when it is wrong. That is the same
shape as every other defect this repository has found: the run completes, the
numbers look reasonable, and the answer is different from the one the contract
asks for.

WHAT THE GAP ACTUALLY IS
------------------------
A Python build carries one Unicode database, fixed at compile time and not
selectable. `unicodedata.unidata_version` reports it. If it is below 15.0.0
then characters assigned in 14.0 or 15.0 are UNASSIGNED to this build:

    `ch.isalpha()`    False for letters added in 14.0 and 15.0
    `ch.lower()`      identity where 15.0 would case-fold
    NFC               identity, where 15.0 may compose

Two of those reach rc2 directly. §7's non-person head test requires an entry to
contain "at least one Unicode letter", and §1.4 defines `lower(x)` as Unicode
simple lowercase. Code-point COUNTING (§1.3's osa unit, CORE floor, overlong
threshold) is unaffected, because counting does not consult the tables.

WHAT BOUNDS IT
--------------
Unicode's Normalization Stability Policy: a string whose characters are all
assigned in version X normalises identically in every version from X onward.
So NFC is fixed for anything already assigned — which is the whole corpus, and
that is checked below rather than assumed.

So the honest statement is not "the environment is wrong" and not "it does not
matter". It is: the environment differs from the pin, the difference is
observable on rules this contract uses, and it does not reach any character
present in this corpus. Whether that is enough for the gate is a decision for
the freeze review, not for this script.
"""

from __future__ import annotations

import collections
import pathlib
import sys
import unicodedata

REPO = pathlib.Path(__file__).resolve().parent.parent
CORPUS = REPO / "data" / "md_full"
sys.path.insert(0, str(REPO / "scripts"))

import citation_extract as ce  # noqa: E402

PINNED = "15.0.0"

# Characters assigned in Unicode 14.0 and 15.0, each a LETTER under 15.0.
# Named rather than generated, so a reader can check them against the standard.
ADDED_AFTER_13 = [
    (0x10780, "LATIN SMALL LETTER MODIFIER CAPITAL L", "14.0, Latin Ext-F"),
    (0x1DF00, "LATIN SMALL LETTER FENG DIGRAPH", "14.0, Latin Ext-G"),
    (0x0870, "ARABIC LETTER ALEF WITH ATTACHED FATHA", "14.0"),
    (0x1E030, "MODIFIER LETTER CYRILLIC SMALL A", "15.0"),
]


def main() -> int:
    env = unicodedata.unidata_version
    print(f"  python           {sys.version.split()[0]}")
    print(f"  unicodedata      {env}")
    print(f"  rc2 §1.1 pins    {PINNED}")
    print(f"  platform         {sys.platform}\n")

    if env == PINNED:
        print("  The execution environment matches rc2's pin. §19's Unicode")
        print("  item is satisfied directly and nothing below is needed.")
        return 0

    print(f"  DIFFERS. rc2 §19 asks for {PINNED} behaviour to be demonstrated")
    print(f"  in the execution environment, and this one carries {env}.\n")

    # 1. Is the difference observable at all, on rules rc2 uses?
    print("  Observable on rc2's own rules — §7's 'at least one Unicode")
    print("  letter' and §1.4's lower(x):\n")
    print(f"    {'code point':12s} {'assigned':9s} {'isalpha':8s} {'lower moves':11s} name")
    observable = 0
    for cp, name, added in ADDED_AFTER_13:
        ch = chr(cp)
        try:
            unicodedata.name(ch)
            assigned = "yes"
        except ValueError:
            assigned = "NO"
        moves = ch.lower() != ch
        if assigned == "NO":
            observable += 1
        print(f"    U+{cp:05X}      {assigned:9s} {str(ch.isalpha()):8s} "
              f"{str(moves):11s} {name} ({added})")
    print(f"\n    {observable} of {len(ADDED_AFTER_13)} are letters under "
          f"{PINNED} and unassigned here.\n")

    # 2. Does it reach the corpus? This is what decides severity.
    if not CORPUS.is_dir():
        print(f"  corpus not found at {CORPUS}; cannot bound the gap")
        return 2

    unassigned: collections.Counter = collections.Counter()
    total = 0
    for f in sorted(CORPUS.glob("*.md")):
        text = ce.normalise(f.read_bytes())
        total += len(text)
        for ch in set(text):
            try:
                unicodedata.name(ch)
            except ValueError:
                if not ch.isspace():
                    unassigned[f"U+{ord(ch):04X}"] += 1

    print(f"  Bounding it against the corpus, {total} code points:\n")
    if unassigned:
        print(f"    characters unassigned under {env}: {dict(unassigned)}")
        print("\n    These are processed against tables that do not know them.")
        print("    §7's letter test and §1.4's lower() may both differ from")
        print(f"    what {PINNED} would give. This reaches the contract.")
        return 1

    print(f"    every character is assigned under {env} — none added in 14.0")
    print("    or 15.0 appears anywhere in the corpus.\n")
    print("    Unicode's Normalization Stability Policy fixes NFC for any")
    print("    character already assigned, so §2's canonical bytes are the")
    print(f"    same under {env} and {PINNED} for this corpus. The observable")
    print("    difference above cannot be reached by input that does not")
    print("    contain the characters it concerns.\n")
    print("  VERDICT")
    print(f"    The environment does NOT match rc2 §1.1's pin, and the gap is")
    print(f"    bounded: observable in principle, unreachable by this corpus.")
    print("    §19's item asks for a demonstration in the execution")
    print("    environment, and this is that demonstration rather than a")
    print("    claim that the item is met. Whether a bounded gap satisfies")
    print("    the gate is a freeze-review decision, not this script's.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
