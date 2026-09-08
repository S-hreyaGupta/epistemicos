#!/usr/bin/env python3
"""Negative controls for the review cycle runner.

Every refusal in run_review.py is demonstrated firing on a fixture built to
trigger exactly that refusal, and the happy path is demonstrated producing a
cycle that passes the MC-2 gate.

A runner whose refusals are never shown to fire is the same defect the v1.0
gate-hardening milestone found thirteen times: a check that cannot come back
false. These are the controls.

The fixture is a throwaway git repository with the two scripts copied in, so
REPO resolves to the fixture and nothing writes into the real runs/ tree.

    python scripts/test_run_review.py

Exit 0 = every expectation held.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent
PROTOCOL_BODY = "# protocol\n\nV01 ...\n"
SPEC_BODY = "# spec\n\nrule G1\n"
PROMPT_BODY = "Review the plan against the spec. Report findings.\n"


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)


def write_lf(p: Path, text: str) -> None:
    """Fixtures must be byte-identical on every platform.

    Path.write_text translates \\n to the platform line ending, so a fixture
    written this way hashes differently on Windows and on Linux. That is how
    this suite first failed: it passed on Linux and failed on Windows, on a
    fixture whose bytes were never meant to vary.
    """
    with p.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def make_repo() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="runner-")).resolve()
    (tmp / "scripts").mkdir()
    for name in ("run_review.py", "validate_cycle.py"):
        shutil.copy2(SRC / name, tmp / "scripts" / name)
    (tmp / "specs").mkdir()
    write_lf(tmp / "specs" / "protocol.md", PROTOCOL_BODY)
    write_lf(tmp / "specs" / "spec.md", SPEC_BODY)
    write_lf(tmp / "specs" / "prompt.md", PROMPT_BODY)
    (tmp / "plan").mkdir()
    write_lf(tmp / "plan" / "01-PLAN.md", "# plan\n\nstep one\n")

    sh("git", "init", "-q", cwd=tmp)
    sh("git", "config", "user.email", "t@t", cwd=tmp)
    sh("git", "config", "user.name", "t", cwd=tmp)
    sh("git", "add", "-A", cwd=tmp)
    sh("git", "commit", "-qm", "fixture", cwd=tmp)
    return tmp


def runner(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return sh(sys.executable, str(tmp / "scripts" / "run_review.py"), *args, cwd=tmp)


def do_init(tmp: Path) -> subprocess.CompletedProcess:
    return runner(tmp, "init", "--run", "T-001",
                  "--protocol", "specs/protocol.md", "--spec", "specs/spec.md")


def do_freeze(tmp: Path, *extra: str) -> subprocess.CompletedProcess:
    return runner(tmp, "freeze", "--run", "T-001", "--type", "plan",
                  "--prompt", "specs/prompt.md", "--file", "plan/01-PLAN.md", *extra)


def fake_cycles(tmp: Path, n: int, close_last: bool = True) -> None:
    """n cycle directories, each with raw output unless the last is left open."""
    rd = tmp / "runs" / "T-001" / "plan-review"
    for i in range(1, n + 1):
        c = rd / f"cycle-{i:02d}"
        c.mkdir(parents=True)
        write_lf(c / "target.json", json.dumps({"cycle": i}))
        if i < n or close_last:
            write_lf(c / "codex-output-raw.md", "findings\n")


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def expect_refused(label: str, needle: str, body) -> None:
        tmp = make_repo()
        made.append(tmp)
        r = body(tmp)
        if r.returncode == 0:
            failures.append(f"{label}: expected refusal, exit 0\n{r.stdout}")
            return
        text = r.stderr + r.stdout
        if needle.lower() not in text.lower():
            failures.append(f"{label}: refused, but not for the stated reason\n"
                            f"  wanted {needle!r}\n  got    {text.strip()[:300]}")
            return
        print(f"  [ok] refused: {label}")

    # ---- happy path first; every negative below is meaningless without it ----
    tmp = make_repo()
    made.append(tmp)
    r = do_init(tmp)
    if r.returncode != 0:
        failures.append(f"init failed:\n{r.stderr}{r.stdout}")
    else:
        run_json = tmp / "runs" / "T-001" / "run.json"
        run = json.loads(run_json.read_text(encoding="utf-8"))
        # Derived from the file's actual bytes, not from re-encoding the constant.
        # The claim under test is the digest-over-digests formula in spec_digest;
        # re-hashing SPEC_BODY would instead be testing file I/O, which is what
        # made this assertion platform-dependent in the first place.
        on_disk = hashlib.sha256((tmp / "specs" / "spec.md").read_bytes()).hexdigest()
        want = hashlib.sha256(f"specs/spec.md:{on_disk}\n".encode()).hexdigest()
        if run["spec_sha256"] != want:
            failures.append("spec_sha256 is not reproducible from its documented definition")
        else:
            print("  [ok] init pins protocol and specs; spec_sha256 reproducible by hand")

        if b"\r" in run_json.read_bytes():
            failures.append("run.json carries CR bytes; its hash will not reproduce "
                            "on another platform")
        else:
            print("  [ok] run.json is LF on this platform")

        r = do_freeze(tmp)
        if r.returncode != 0:
            failures.append(f"freeze failed:\n{r.stderr}{r.stdout}")
        else:
            cyc = tmp / "runs" / "T-001" / "plan-review" / "cycle-01"
            digest = (cyc / "target.sha256").read_text(encoding="utf-8").strip()
            ci = (cyc / "codex-input.md").read_text(encoding="utf-8")
            if digest not in ci:
                failures.append("frozen input does not carry the target hash")
            else:
                print("  [ok] freeze binds codex-input.md to the target hash")

            crlf = [n for n in ("target.json", "target.sha256", "codex-input.md")
                    if b"\r" in (cyc / n).read_bytes()]
            if crlf:
                failures.append(f"frozen evidence carries CR bytes: {', '.join(crlf)}\n"
                                "  the same freeze on another platform would produce a "
                                "different TARGET_SHA256")
            else:
                print("  [ok] frozen evidence is LF, so its hashes are platform-neutral")

            write_lf(tmp / "reply.md", "C01-F01 | UNTESTED RULE | R-B7 | ...\n")
            r = runner(tmp, "record", "--cycle", str(cyc),
                       "--output", "reply.md", "--invocation", "manual")
            if r.returncode != 0:
                failures.append(f"record failed the MC-2 gate on a clean cycle:\n{r.stdout}")
            elif "MC2_CONFORMANCE: PASS" not in r.stdout:
                failures.append(f"record did not run the gate:\n{r.stdout}")
            else:
                print("  [ok] recorded cycle passes the MC-2 gate end to end")

            inv = json.loads((cyc / "invocation.json").read_text(encoding="utf-8"))
            if inv.get("invocation") != "manual":
                failures.append("invocation mode not recorded")
            else:
                print("  [ok] invocation mode recorded, with its limit stated")

    # ---- refusals ----
    expect_refused("init twice on one run id", "already exists",
                   lambda t: (do_init(t), do_init(t))[1])

    expect_refused("freeze without init", "no run.json", do_freeze)

    def protocol_drift(t: Path):
        do_init(t)
        write_lf(t / "specs" / "protocol.md", PROTOCOL_BODY + "V22 added later\n")
        return do_freeze(t)
    expect_refused("protocol edited after init", "protocol changed since init", protocol_drift)

    def spec_drift(t: Path):
        do_init(t)
        write_lf(t / "specs" / "spec.md", SPEC_BODY + "rule G8\n")
        return do_freeze(t)
    expect_refused("spec edited after init", "spec changed since init", spec_drift)

    def missing_prompt(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "plan",
                      "--prompt", "specs/nope.md", "--file", "plan/01-PLAN.md")
    expect_refused("prompt file missing", "prompt file not found", missing_prompt)

    def empty_prompt(t: Path):
        do_init(t)
        write_lf(t / "specs" / "prompt.md", "")
        return do_freeze(t)
    expect_refused("prompt file empty", "prompt file is empty", empty_prompt)

    def no_plan_file(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "plan",
                      "--prompt", "specs/prompt.md")
    expect_refused("plan review with no artifact", "needs at least one --file", no_plan_file)

    def budget(t: Path):
        do_init(t)
        fake_cycles(t, 4)
        return do_freeze(t)
    expect_refused("fifth cycle exceeds the budget", "exceed the 4-cycle budget", budget)

    def prev_open(t: Path):
        do_init(t)
        fake_cycles(t, 1, close_last=False)
        return do_freeze(t)
    expect_refused("previous cycle has no recorded output", "no recorded output", prev_open)

    def impl_missing(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "implementation",
                      "--prompt", "specs/prompt.md", "--candidate-commit", "HEAD")
    expect_refused("implementation review missing approved plan hash", "requires --approved-plan-hash", impl_missing)

    def impl_bad_hash(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "implementation",
                      "--prompt", "specs/prompt.md", "--candidate-commit", "HEAD",
                      "--approved-plan-hash", "NOT-A-HASH")
    expect_refused("approved plan hash not a digest", "64-char hex", impl_bad_hash)

    def record_twice(t: Path):
        do_init(t)
        do_freeze(t)
        cyc = t / "runs" / "T-001" / "plan-review" / "cycle-01"
        write_lf(t / "reply.md", "findings\n")
        runner(t, "record", "--cycle", str(cyc), "--output", "reply.md",
               "--invocation", "manual")
        write_lf(t / "reply2.md", "different findings\n")
        return runner(t, "record", "--cycle", str(cyc), "--output", "reply2.md",
                      "--invocation", "manual")
    expect_refused("re-recording raw output", "write-once", record_twice)

    def record_unfrozen(t: Path):
        write_lf(t / "reply.md", "findings\n")
        return runner(t, "record", "--cycle", str(t / "nowhere"),
                      "--output", "reply.md", "--invocation", "manual")
    expect_refused("record against an unfrozen directory", "not a frozen cycle", record_unfrozen)

    def record_empty(t: Path):
        do_init(t)
        do_freeze(t)
        write_lf(t / "reply.md", "")
        return runner(t, "record", "--cycle",
                      str(t / "runs" / "T-001" / "plan-review" / "cycle-01"),
                      "--output", "reply.md", "--invocation", "manual")
    expect_refused("empty reviewer output", "reviewer output is empty", record_empty)

    def freeze_over_existing(t: Path):
        do_init(t)
        fake_cycles(t, 1)
        # next_cycle only counts directories, so a non-directory sitting on the
        # next cycle's name is the one way the path can be occupied. Without the
        # guard this surfaces as a mkdir traceback rather than a refusal.
        write_lf(t / "runs" / "T-001" / "plan-review" / "cycle-02", "stray\n")
        return do_freeze(t)
    expect_refused("cycle path already occupied", "already exists", freeze_over_existing)

    for t in made:
        shutil.rmtree(t, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("all controls fired; every refusal is reachable and the happy path passes MC-2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
