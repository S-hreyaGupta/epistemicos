#!/usr/bin/env python3
"""How far is the existing bootstrap-review work from satisfying the gate?

    python _probe\\gate_gap.py

Read-only. Nothing is created.

CORRECTED 25 September. The first version of this file asked whether a frozen
target had ever PINNED each covered file, and printed "REVIEWED, UNCHANGED"
when one had. That is not the same question. A target is what a reviewer was
going to be shown; `codex-output-raw.md` is evidence that a reviewer was
actually shown it. BOOTSTRAP-002/cycle-01 froze nine of the ten covered files
and has no capture at all, and the first version reported all nine as reviewed.

Freezing a target is a claim about intent. Only the capture is evidence. So a
cycle counts here only if it has a non-empty raw capture beside its target,
which is the distinction the whole repository exists to keep.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "scripts" / "bootstrap_gate.py"

spec = importlib.util.spec_from_file_location("_gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def cycles() -> list[dict]:
    """Every frozen cycle, with whether a reviewer was demonstrably shown it."""
    out = []
    for t in sorted((REPO / "runs").rglob("target.json")):
        try:
            d = json.loads(t.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        cap = t.parent / "codex-output-raw.md"
        captured = cap.is_file() and cap.stat().st_size > 0
        out.append({
            "target": t,
            "dir": t.parent,
            "run": d.get("run_id"),
            "cycle": d.get("cycle"),
            "files": {e["path"]: e["sha256"]
                      for e in (d.get("plan_files") or [])
                      if isinstance(e, dict) and "path" in e},
            "pins": list(d.get("governing_pins") or []),
            "captured": captured,
            "capture_bytes": cap.stat().st_size if cap.is_file() else 0,
        })
    return out


def main() -> int:
    cov = gate.covered(REPO)
    cyc = cycles()

    print(f"  covered set: {len(cov)} files\n")
    print("  frozen cycles, and whether a reviewer was actually shown them\n")
    for c in cyc:
        state = (f"CAPTURED {c['capture_bytes']:,}b" if c["captured"]
                 else "NO CAPTURE — frozen but never reviewed")
        print(f"    {c['run']} cycle {c['cycle']}   "
              f"{len(c['files'])} plan_files   {state}")

    print("\n  per covered file, counting only cycles with a capture\n")
    reviewed, stale, never = [], [], []
    for rel, now in sorted(cov.items()):
        hits = [c for c in cyc if c["captured"] and c["files"].get(rel) == now]
        frozen_only = [c for c in cyc
                       if not c["captured"] and rel in c["files"]]
        older = [c for c in cyc
                 if c["captured"] and rel in c["files"]
                 and c["files"][rel] != now]
        if hits:
            reviewed.append(rel)
            w = hits[-1]
            print(f"    REVIEWED AT THESE BYTES   {rel}")
            print(f"                                {w['run']} cycle {w['cycle']}")
        elif older:
            stale.append(rel)
            w = older[-1]
            print(f"    REVIEWED, THEN CHANGED    {rel}")
            print(f"                                reviewed {w['files'][rel][:16]}"
                  f" in {w['run']} cycle {w['cycle']}")
            print(f"                                on disk  {now[:16]}")
        else:
            never.append(rel)
            extra = ""
            if frozen_only:
                f = frozen_only[-1]
                extra = (f"   (frozen in {f['run']} cycle {f['cycle']}, "
                         f"never reviewed)")
            pinned = [c['run'] for c in cyc if rel in c["pins"]]
            if pinned:
                extra += f"   (pinned as GOVERNING in {', '.join(sorted(set(pinned)))})"
            print(f"    NO REVIEW EVIDENCE        {rel}{extra}")

    print(f"\n    reviewed at current bytes {len(reviewed)}   "
          f"changed since review {len(stale)}   no evidence {len(never)}")

    print("\n  what remains\n")
    if never or stale:
        print(f"    {len(never) + len(stale)} of {len(cov)} covered files have no")
        print("    review evidence at the bytes on disk. A decision recorded now")
        print("    would approve code no reviewer saw, which is B01-F09 and what")
        print("    --target exists to prevent.")
        print("\n    So the bootstrap review has to be RUN, not assembled.")
    else:
        print("    Every covered file has capture-backed review evidence at its")
        print("    current bytes. What is missing is a single frozen target that")
        print("    lists all of them, the four evidence files, and the decision.")

    print("\n  evidence files under bootstrap-review/")
    for name in gate.EVIDENCE:
        p = REPO / "bootstrap-review" / name
        state = "present" if p.is_file() and p.stat().st_size else "MISSING"
        print(f"    {name:24s} {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
