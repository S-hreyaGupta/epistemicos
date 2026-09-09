#!/usr/bin/env python3
"""Reconstruct a pre-snapshot cycle's reviewed bytes, verified by hash.

    python scripts/backfill_snapshot.py runs/BOOTSTRAP-001/plan-review/cycle-01

Exit 0 = every artifact was reconstructed and its hash matched the record.
Exit 1 = at least one could not be, and nothing was written.
Exit 2 = could not run.

Why this exists, once
---------------------
BOOTSTRAP-001 cycle 01 was frozen before freeze preserved the reviewed bytes.
Its target records a path and a SHA-256 for each artifact, and check 9 then
re-hashed the live tree — so repairing the code that review asked me to repair
invalidated the cycle that asked.

Alex Zamurko, 9 September 2026:

    Revalidate Cycle 01 only if the exact reviewed bytes can be mechanically
    reconstructed and verified from preserved evidence; otherwise rerun the
    review as a new valid cycle. Retroactively declaring it valid without exact
    reconstruction would weaken the audit trail. Exact proof is acceptable;
    assumption is not.

They can be. The target pins `protocol_commit`, and every artifact at that
commit hashes to the value the target already recorded. So this reads each blob
out of git at that commit, hashes it, and writes it only when the hash matches
the record made at freeze time. The recorded hash is the arbiter throughout;
nothing here decides that bytes are correct because they look plausible.

If any artifact does not reconstruct exactly, this writes nothing at all. A
partially reconstructed cycle would be worse than an invalid one, because it
would look complete.

Not a general tool. Cycles frozen after the snapshot change carry their own
preserved copies and never need this.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def git_blob(commit: str, path: str) -> bytes | None:
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    cycle = Path(argv[1]).resolve()
    target_json = cycle / "target.json"
    if not target_json.is_file():
        print(f"not a frozen cycle directory: {cycle}", file=sys.stderr)
        return 2

    snap = cycle / "artifacts"
    if snap.exists():
        print(f"{snap.relative_to(REPO).as_posix()} already exists; refusing to "
              "overwrite preserved evidence", file=sys.stderr)
        return 1

    target = json.loads(target_json.read_text(encoding="utf-8"))
    commit = target.get("protocol_commit")
    entries = target.get("plan_files") or []
    if not commit or not entries:
        print("target carries no protocol_commit or no plan_files", file=sys.stderr)
        return 1

    print(f"reconstructing {len(entries)} artifact(s) from {commit[:12]}")
    print()

    # Reconstruct everything and verify before writing anything.
    recovered: list[tuple[str, bytes]] = []
    failures: list[str] = []
    for e in entries:
        path, want = e["path"], e["sha256"]
        blob = git_blob(commit, path)
        if blob is None:
            failures.append(f"{path}: not present at {commit[:12]}")
            continue
        got = hashlib.sha256(blob).hexdigest()
        if got != want:
            failures.append(f"{path}: hash differs\n"
                            f"      recorded  {want}\n"
                            f"      at commit {got}")
            continue
        recovered.append((path, blob))
        print(f"  [verified] {path}")

    if failures:
        print()
        for f in failures:
            print(f"  [FAILED] {f}")
        print()
        print("Nothing written. The exact reviewed bytes are not reconstructable "
              "for every\nartifact, so under the 9 September ruling this cycle "
              "cannot be revalidated and\nthe review must be rerun as a new "
              "cycle.")
        return 1

    for path, blob in recovered:
        dest = snap / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)

    write_note(cycle, commit, recovered)
    print()
    print(f"wrote {len(recovered)} preserved copies under "
          f"{snap.relative_to(REPO).as_posix()}/")
    print("Every one was verified against the SHA-256 recorded at freeze time.")
    return 0


def write_note(cycle: Path, commit: str, recovered: list[tuple[str, bytes]]) -> None:
    lines = [
        "# Reconstructed snapshot",
        "",
        "This cycle was frozen before `freeze` preserved the reviewed bytes, so",
        "these copies were reconstructed rather than captured at the time.",
        "",
        f"Source: git commit `{commit}`, which the target records as",
        "`protocol_commit`.",
        "",
        "Each file below was read from that commit and its SHA-256 compared with",
        "the value recorded in `target.json` at freeze time. All matched. The",
        "recorded hash is what establishes these are the reviewed bytes; the",
        "commit is only where they were found.",
        "",
        "```text",
    ]
    for path, blob in recovered:
        lines.append(f"{hashlib.sha256(blob).hexdigest()}  {path}")
    lines += [
        "```",
        "",
        "Reconstructed under Alex Zamurko's ruling of 9 September 2026, which",
        "permits revalidation only where the exact bytes can be mechanically",
        "reconstructed and verified, and requires a rerun otherwise.",
        "",
        "Cycles frozen after that change carry snapshots taken at freeze time and",
        "need no reconstruction.",
        "",
    ]
    with (cycle / "SNAPSHOT_NOTE.md").open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
