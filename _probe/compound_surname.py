#!/usr/bin/env python3
"""What does the compound-surname fixture actually emit?

    python _probe\\compound_surname.py

Read-only. The control at `a compound personal surname is not read as an
institution` asserts that no emitted citation_key starts with `non_person|`.
On 25 September a live-fixture guard showed the fixture emits no citation at
all, so the assertion has never had a subject: it passes because there is
nothing to be wrong rather than because the key is person-shaped.

Before choosing a fix, this prints what the fixture really produces. The two
repairs point in opposite directions and only the measurement decides:

    the citation IS parsed, keyed person    the control is fine and my guard
                                            is reading the wrong variable

    the citation is unresolved              the control is untestable as
                                            written, and whether that is an
                                            extractor defect is a separate
                                            question about rc2 §7.4 and §8
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import citation_extract as ce  # noqa: E402

# Taken from the suite, not retyped. The first version of this probe used
# `# T\n\n`, which opens no section, so every candidate fell in front matter
# and was excluded as publisher_metadata under §E. That produced a confident
# and entirely wrong conclusion about a control whose fixture does open a
# section. Read the constant rather than inventing one.
_suite = (REPO / "scripts" / "test_citation_extract.py").read_text(
    encoding="utf-8")
HEAD = next(eval(l.split("=", 1)[1].strip())
            for l in _suite.splitlines() if l.startswith("HEAD = "))

PV = ("\n\n## References\n\nPircher Verdorfer, A. (2016). Mindfulness and "
      "leadership. Journal, 1(1), 1-10.\n")
BODY = "Varies across individuals (Pircher Verdorfer, 2016) markedly."


def main() -> int:
    print(f"  HEAD, read from the suite: {HEAD!r}\n")
    text = ce.normalise((HEAD + BODY + PV).encode("utf-8"))
    body, section, off, heads, _src = ce.split_body_and_references(text)
    body = body.replace("\\&", "&")
    sents = ce.sentences(body)
    bib, bib_unres = ce.assemble_references(section, off)

    # bib_unres was discarded by the first two versions of this probe, which
    # printed an empty reference side and said nothing about why. A reference
    # that failed to key looks exactly like a reference that was never there.
    print("  reference side")
    for r in bib:
        print(f"    keyed        key={r.get('reference_key')!r}  "
              f"kind={r.get('author_kind')!r}")
    for u in bib_unres:
        print(f"    UNRESOLVED   reason={u.get('reason')!r}")
        print(f"                 {str(u.get('assembled') or u.get('text'))[:64]!r}")
    if not bib and not bib_unres:
        print("    nothing at all, so the References section was not found")

    npk = frozenset(r["reference_key"] for r in bib
                    if r.get("author_kind") == "non_person" and r["reference_key"])
    print(f"    non_person keys passed to extraction: {sorted(npk) or 'none'}")

    cits, unres, excl, errs = ce.extract_citations(
        body, sents, heads, {"ampersand", "segments"}, npk)

    print(f"\n  citation side")
    print(f"    parsed              {len(cits)}")
    for c in cits:
        print(f"      key={c.get('citation_key')!r}  "
              f"kind={c.get('author_kind')!r}  "
              f"phrase={c.get('author_phrase')!r}")
    print(f"    unresolved          {len(unres)}")
    for u in unres:
        print(f"      text={u.get('text')!r}  reason={u.get('reason')!r}")
    print(f"    excluded            {len(excl)}")
    for x in excl:
        print(f"      text={x.get('text')!r}  "
              f"reason={x.get('excluded_reason')!r}")
    print(f"    citation_error      {len(errs)}")

    print("\n  what this means for the control")
    if cits and not any(str(c.get("citation_key", "")).startswith("non_person|")
                        for c in cits):
        print("    The citation IS parsed and keyed person. The control is")
        print("    sound and the guard I added is reading the wrong thing.")
        return 0
    if not cits:
        print("    No citation is emitted, so `any(... for c in cits)` has")
        print("    never had anything to range over. The control has been")
        print("    reporting success about a key that does not exist, on the")
        print("    real extractor, not only under the sweep.")
        print("    The guard is correct. What it exposes is a separate")
        print("    question: should this parenthetical parse?")
        return 1
    print("    The citation is parsed and keyed non_person, which is the")
    print("    defect the control names. It would now fail correctly.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
