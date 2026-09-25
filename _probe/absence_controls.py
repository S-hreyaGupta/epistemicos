#!/usr/bin/env python3
"""What do the three absence-shaped controls actually have to judge?

    python _probe\\absence_controls.py

Read-only. The vacuity sweep's read probe named four survivors that read
citation-side output and passed with it empty. One is an attribution artefact.
The other three share a shape:

    cits, unres, _x = extract(...)
    if keys(cits):
        failures.append(...)
    else:
        ok("... the form is refused ...")

Each is named for a REFUSAL and tests only an ABSENCE. `not cits` is equally
true of a span that was refused, a span that was never detected, and a run
that emits nothing at all, so the control cannot tell those apart and has been
reporting the first whichever held.

The repair is to require the refusal to be visible. That only works if the
extractor actually emits something to see, and whether it does is a
measurement rather than a guess: the compound-surname probe assumed a fixture
header and drew a confident wrong conclusion twice before it was read off the
suite instead. So this prints all three record streams for all three fixtures
first, and the repair is written afterwards.

    unresolved_citation present   the repair is `elif not unres: fail`, and
                                  the control gains the half it is named for

    nothing on any list           the span is not detected at all, which is a
                                  finding about the extractor rather than the
                                  suite, and the control should say so
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import citation_extract as ce  # noqa: E402

# Read from the suite rather than retyped, for the reason in the docstring.
_suite = (REPO / "scripts" / "test_citation_extract.py").read_text(
    encoding="utf-8")


def _const(name: str) -> str:
    return next(eval(l.split("=", 1)[1].strip())
                for l in _suite.splitlines() if l.startswith(f"{name} = "))


HEAD = _const("HEAD")
REFS = _const("REFS")

# (control label, suite line, body, which helper the control uses)
CASES = [
    ("rc2 §8: with no reference entry, the institution stays unresolved",
     1123, "Provided by the World Bank (2024) annually.", "doc"),
    ("§4: widening the year list left the author/year comma required",
     1722, "As shown (Smith 2020) here.", "extract"),
    ("§C: naming the defect did not loosen the grammar",
     1803, "As shown (Lu and Shang 2017) here.", "extract"),
]


def run(body_text: str, helper: str):
    """The suite's own two helpers, reproduced exactly.

    `doc` assembles the bibliography first and passes the non-person keys in,
    which is rc2 §8's ordering; `extract` does not. The §8 control uses `doc`
    and the other two use `extract`, and the difference decides what a
    refusal even looks like, so they are not interchangeable here.
    """
    text = ce.normalise((HEAD + body_text + REFS).encode("utf-8"))
    body, section, off, heads, _src = ce.split_body_and_references(text)
    body = body.replace("\\&", "&")
    sents = ce.sentences(body)
    if helper == "doc":
        bib, _bu = ce.assemble_references(section, off)
        npk = frozenset(r["reference_key"] for r in bib
                        if r.get("author_kind") == "non_person"
                        and r["reference_key"])
        return ce.extract_citations(body, sents, heads,
                                    {"ampersand", "segments"}, npk)[:4]
    return ce.extract_citations(body, sents, heads, set())[:4]


def main() -> int:
    repairable = 0
    for label, line, body_text, helper in CASES:
        print(f"\n  {label}")
        print(f"    suite line {line}, via {helper}()")
        print(f"    body {body_text!r}")
        cits, unres, excl, errs = run(body_text, helper)

        print(f"    citation           {len(cits)}")
        for c in cits:
            print(f"      key={c.get('citation_key')!r}")
        print(f"    unresolved         {len(unres)}")
        for u in unres:
            print(f"      text={u.get('text')!r}  reason={u.get('reason')!r}")
        print(f"    excluded           {len(excl)}")
        for x in excl:
            print(f"      text={x.get('text')!r}  "
                  f"reason={x.get('excluded_reason')!r}")
        print(f"    citation_error     {len(errs)}")
        for e in errs:
            print(f"      text={e.get('text')!r}")

        if cits:
            print("    -> PARSES. The control's named defect is live and it")
            print("       should be failing today.")
        elif unres or excl or errs:
            where = ("unresolved" if unres else
                     "excluded" if excl else "citation_error")
            print(f"    -> refused, and the refusal is visible on {where}.")
            print("       The control can assert it instead of asserting an")
            print("       absence, and then an empty run fails it.")
            repairable += 1
        else:
            print("    -> nothing on any list. The span is not detected at")
            print("       all, so no assertion over the record stream can")
            print("       distinguish refusal from silence. Same state the")
            print("       compound surname is in, and a finding about the")
            print("       extractor rather than about the control.")

    print(f"\n  {repairable} of {len(CASES)} can be repaired inside the suite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
