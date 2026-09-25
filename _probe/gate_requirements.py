#!/usr/bin/env python3
"""Exactly what the bootstrap gate needs, asked of the gate itself.

    python _probe\\gate_requirements.py

Read-only. Imports bootstrap_gate and calls its own functions, so this cannot
drift from what `check` and `record` actually require. Nothing is created.

The frozen review target has to pin the covered set FILE FOR FILE: a covered
file missing from the target means nobody reviewed it, and a target file the
gate does not cover means approving it binds nothing. So the `--file` list for
`run_review.py freeze` is not a judgement, it is this output.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "scripts" / "bootstrap_gate.py"

spec = importlib.util.spec_from_file_location("_gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def main() -> int:
    print("  bootstrap exception")
    available, why = gate.bootstrap_exception_available(REPO)
    print(f"    available: {available}")
    for line in why:
        print(f"    {line}")

    print("\n  declared roots")
    for rel in list(gate.COMPONENTS) + list(gate.ALWAYS):
        p = REPO / rel
        mark = "" if p.is_file() else "   MISSING"
        print(f"    {rel}{mark}")

    print("\n  dependency closure, reached rather than declared")
    try:
        deps = gate.closure(REPO)
    except Exception as e:
        print(f"    could not compute: {e}")
        deps = {}
    if not deps:
        print("    (none)")
    for rel, via in sorted(deps.items()):
        names = ", ".join(Path(v).name for v in via)
        print(f"    {rel}   via {names}")

    print("\n  the covered set — this is the --file list for freeze")
    try:
        cov = gate.covered(REPO)
    except Exception as e:
        print(f"    REFUSED: {e}")
        return 1
    for rel, digest in sorted(cov.items()):
        print(f"    {digest[:16]}  {rel}")
    print(f"    {len(cov)} files")

    print("\n  freeze command, composed from the covered set")
    files = " ".join(f"--file {rel}" for rel in sorted(cov))
    print(f"    python scripts/run_review.py freeze --run <RUN> --type plan \\")
    print(f"        --prompt <PROMPT> {files}")

    print("\n  evidence the decision will require, under bootstrap-review/")
    for name in gate.EVIDENCE:
        p = REPO / "bootstrap-review" / name
        state = "present" if p.is_file() and p.stat().st_size else "MISSING"
        print(f"    {name:24s} {state}")

    print("\n  candidate prompts on disk")
    pdir = REPO / "specs" / "prompts"
    if pdir.is_dir():
        for p in sorted(pdir.glob("*.md")):
            print(f"    {p.relative_to(REPO).as_posix()}")
    else:
        print("    specs/prompts/ does not exist")

    print("\n  pin/target separation")
    print("    init requires --spec, and a file cannot be both a run pin and a")
    print("    review target. None of the covered files above may be passed as")
    print("    --spec. specs/evidence-schema-v1.0.md is covered, so it is the")
    print("    one most likely to be reached for by habit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
