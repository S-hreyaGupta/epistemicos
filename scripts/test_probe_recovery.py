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

    # ---- SELF-F05: the state that actually happened ----
    #
    # 8 October, close to one in the morning. A run was killed between
    # truncating scripts/loop_state.py and writing the mutation into it, and
    # the tree was left holding an empty 1163-line covered component. Recovery
    # compared the empty file against the digest of what it had meant to write,
    # found no match, and refused. Every guard behaved as designed and the
    # repository stayed broken until someone read `git status` by hand.
    #
    # The sentinel here names a mutation that never landed, which is the whole
    # point: on disk there is neither the original nor the mutation.
    t4 = build()
    (t4 / "scripts" / "subject.py").write_bytes(b"")
    sentinel(t4, MUTATED_BYTES)

    r4 = run_probe(t4)
    after4 = (t4 / "scripts" / "subject.py").read_bytes()
    blob4 = r4.stdout + r4.stderr
    if after4 == b"":
        failures.append(
            "an empty source file with a live sentinel was left empty. "
            "Refusing is the right instinct everywhere else here, and it is "
            "wrong in this one case: nobody edits a file down to zero bytes, "
            "so there is no human work being protected by the refusal.")
    elif after4 != HEAD_BYTES:
        failures.append(f"the empty file was rewritten with something that is "
                        f"not HEAD: {after4[:80]!r}")
    elif "empty" not in blob4:
        failures.append(f"the file was restored without saying it had been "
                        f"found empty, so a reader cannot tell this from an "
                        f"ordinary recovery\n{blob4[:300]}")
    elif (t4 / "_probe" / ".active-mutation.json").exists():
        failures.append("the sentinel survived recovery from the empty case")
    else:
        ok("an empty file left by a kill mid-write is restored, and says so")

    # The other half, and the one that stops the case above from arising. A
    # write that fails partway must leave the original untouched rather than a
    # truncated file. os.fsync is made to raise, which is the closest a test
    # can get to the process dying with the file open.
    t5 = build()
    subj = t5 / "scripts" / "subject.py"
    sys.path.insert(0, str(t5 / "_probe"))
    for _m in ("mutate_repairs",):
        sys.modules.pop(_m, None)
    import mutate_repairs as _mr  # noqa: E402

    _real_fsync = os.fsync
    os.fsync = lambda fd: (_ for _ in ()).throw(OSError("simulated kill"))
    try:
        _mr.write_atomic(subj, "this text must never reach the file\n")
    except OSError:
        pass
    finally:
        os.fsync = _real_fsync
    # Both branches below are the same violation, so both say so in the same
    # words. The first version named only the empty case, and when the probe
    # mutated this repair the other branch fired instead: the write landed and
    # fsync raised after it, leaving the target holding the new text. The
    # control was right and its wording was too narrow to recognise itself,
    # which is a smaller copy of the defect class this whole layer chases.
    if subj.read_bytes() == b"":
        failures.append(
            "a write that did not complete emptied the target. write_text "
            "truncates before it fills, and this repair exists so the target "
            "is never left half written.")
    elif subj.read_bytes() != HEAD_BYTES:
        failures.append(
            f"a write that did not complete changed the target anyway: "
            f"{subj.read_bytes()[:80]!r}. The new content must not be visible "
            f"until the whole of it is on disk.")
    else:
        ok("a write that does not complete leaves the original intact")
    sys.path.remove(str(t5 / "_probe"))

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
