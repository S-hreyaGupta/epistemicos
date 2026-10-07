#!/usr/bin/env python3
"""Controls for the mutation probe's crash recovery.

    python scripts/test_probe_recovery.py

Exit 0 = every control fired.

Why this file exists
--------------------
SELF-F02 claimed that a probe run killed mid-mutation is restored from HEAD on
the next run. BOOTSTRAP-003's reviewer showed the claim was false: the recovery
ran `git checkout -- <path>`, which restores from the INDEX, and in a fixture
with different bytes staged it wrote those staged bytes and reported that it
had restored from HEAD.

The repair was mine and so was the defect, and the reason it survived is that
the probe had no controls at all. It is an instrument, preserved in cycle
evidence and read by reviewers, and until now nothing tested it.

The fixture is a throwaway git repository with its own `_probe/`, so the real
repository is never written to.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent
REPO = SRC.parent
PROBE = REPO / "_probe" / "mutate_repairs.py"

HEAD_BYTES = b"# committed\nVALUE = 1\n"
STAGED_BYTES = b"# staged, and not what HEAD holds\nVALUE = 2\n"
MUTATED_BYTES = b"# mutated by a run that was killed\nVALUE = 999\n"


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    print("probe crash recovery")

    def build() -> Path:
        t = Path(tempfile.mkdtemp(prefix="probe-")).resolve()
        made.append(t)
        (t / "scripts").mkdir()
        (t / "_probe").mkdir()
        shutil.copy(PROBE, t / "_probe" / "mutate_repairs.py")
        sh("git", "init", "-q", cwd=t)
        sh("git", "config", "user.email", "t@example.com", cwd=t)
        sh("git", "config", "user.name", "t", cwd=t)
        (t / "scripts" / "subject.py").write_bytes(HEAD_BYTES)
        sh("git", "add", "-A", cwd=t)
        sh("git", "commit", "-qm", "the committed state", cwd=t)
        return t

    def sentinel(t: Path, mutated: bytes) -> None:
        head = sh("git", "rev-parse", "HEAD", cwd=t).stdout.strip()
        (t / "_probe" / ".active-mutation.json").write_text(json.dumps({
            "finding": "a killed run",
            "path": "scripts/subject.py",
            "head": head,
            "mutated": hashlib.sha256(mutated).hexdigest(),
        }, indent=2) + "\n", encoding="utf-8")

    def run_probe(t: Path) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        return subprocess.run(
            [sys.executable, str(t / "_probe" / "mutate_repairs.py"),
             "NO-SUCH-FINDING"],
            cwd=str(t), env=env, capture_output=True, text=True)

    # ---- the reviewer's case: different bytes staged ----
    #
    # HEAD holds one thing, the index holds another, the working tree holds the
    # mutation. Recovery must write HEAD's bytes. `git checkout -- <path>`
    # wrote the index's, which is the defect this control exists for.
    t = build()
    (t / "scripts" / "subject.py").write_bytes(STAGED_BYTES)
    sh("git", "add", "scripts/subject.py", cwd=t)
    (t / "scripts" / "subject.py").write_bytes(MUTATED_BYTES)
    sentinel(t, MUTATED_BYTES)

    r = run_probe(t)
    after = (t / "scripts" / "subject.py").read_bytes()
    blob = r.stdout + r.stderr
    if after == STAGED_BYTES:
        failures.append(
            "recovery restored the STAGED bytes while reporting HEAD. That is "
            "the defect BOOTSTRAP-003 reported: `git checkout -- <path>` reads "
            "the index, and the index is not the repaired source.")
    elif after != HEAD_BYTES:
        failures.append(
            f"recovery left the file as neither HEAD nor the index: "
            f"{after!r}")
    elif "recovered" not in blob:
        failures.append(f"the file was restored and nothing said so\n{blob[:300]}")
    else:
        ok("a killed run is restored from HEAD, not from the index")

    if (t / "_probe" / ".active-mutation.json").exists():
        failures.append("the sentinel survived a successful recovery, so the "
                        "next run would try to recover a file already restored")
    else:
        ok("the sentinel is removed once the file is back")

    # ---- the index is not this probe's to revert ----
    staged_now = sh("git", "show", ":scripts/subject.py", cwd=t).stdout.encode()
    if staged_now != STAGED_BYTES:
        failures.append(
            "recovery rewrote the index. Someone else's staged work is not "
            "this probe's to discard, and restoring the file does not require "
            "touching it.")
    else:
        ok("the index is left exactly as it was")

    # ---- it refuses rather than guessing when HEAD has moved ----
    t2 = build()
    (t2 / "scripts" / "subject.py").write_bytes(MUTATED_BYTES)
    sentinel(t2, MUTATED_BYTES)
    rec = json.loads((t2 / "_probe" / ".active-mutation.json")
                     .read_text(encoding="utf-8"))
    rec["head"] = "0" * 40
    (t2 / "_probe" / ".active-mutation.json").write_text(
        json.dumps(rec, indent=2) + "\n", encoding="utf-8")

    r2 = run_probe(t2)
    blob2 = r2.stdout + r2.stderr
    if (t2 / "scripts" / "subject.py").read_bytes() != MUTATED_BYTES:
        failures.append(
            "recovery restored a file although HEAD had moved since the "
            "mutation. A recovery that guesses is worse than one that refuses.")
    # The refusal's own words, not the bare phrase `CANNOT RUN`. The first
    # version of this control looked for that phrase and got it from the
    # argument filter, which prints it too — so it passed while recovery was
    # never reached at all. A control satisfied by the wrong message is the
    # defect this whole probe exists to find.
    elif "has moved since" not in blob2:
        failures.append(f"HEAD had moved and nothing refused for that reason\n"
                        f"{blob2[:300]}")
    else:
        ok("a moved HEAD refuses rather than restoring from the wrong commit")

    # ---- and it does nothing at all when there is no sentinel ----
    t3 = build()
    r3 = run_probe(t3)
    if "recovered" in (r3.stdout + r3.stderr):
        failures.append("recovery reported restoring something with no "
                        "sentinel present")
    elif (t3 / "scripts" / "subject.py").read_bytes() != HEAD_BYTES:
        failures.append("a run with no sentinel rewrote the subject anyway")
    else:
        ok("no sentinel, nothing recovered, nothing written")

    for p in made:
        shutil.rmtree(p, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("  the probe's recovery names its source and leaves the rest alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
