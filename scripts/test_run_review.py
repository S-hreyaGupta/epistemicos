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
    for name in ("run_review.py", "validate_cycle.py", "bootstrap_gate.py",
                 "ledger.py", "loop_state.py", "findings_format.py",
                 "cycle_projection.py", "authority.py", "run_pins.py"):
        shutil.copy2(SRC / name, tmp / "scripts" / name)
    (tmp / "specs").mkdir()
    # Copied rather than stubbed: it is a covered component now (B01-F10), so
    # the gate hashes it and a stub would diverge from the real one.
    shutil.copy2(SRC.parent / "specs" / "evidence-schema-v1.0.md",
                 tmp / "specs" / "evidence-schema-v1.0.md")
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


def do_init(tmp: Path, *extra: str) -> subprocess.CompletedProcess:
    # --bootstrap-exempt because these fixtures test the runner's own mechanics
    # and are development evidence, not protocol cycles. Labelling them honestly
    # is the point of the flag. The gate's own effect on init is controlled
    # separately, below, so exempting here does not hide it.
    return runner(tmp, "init", "--run", "T-001", "--bootstrap-exempt",
                  "--protocol", "specs/protocol.md", "--spec", "specs/spec.md",
                  *extra)


def approve_bootstrap(tmp: Path) -> subprocess.CompletedProcess:
    """Record a bootstrap approval bound to a target covering the gate's set.

    B01-F09 makes --target mandatory, so the fixture has to freeze one. Built
    from the gate's own covered set rather than a hand-written list, so adding a
    component to the gate does not silently leave this fixture approving five of
    six things.
    """
    (tmp / "bootstrap-review").mkdir(parents=True, exist_ok=True)
    for n in ("codex-input.md", "codex-output-raw.md", "findings.md",
              "claude-response.md"):
        write_lf(tmp / "bootstrap-review" / n, f"contents of {n}\n")

    import importlib.util
    spec_ = importlib.util.spec_from_file_location(
        "_bg_rr", tmp / "scripts" / "bootstrap_gate.py")
    mod = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(mod)

    rel_target = "runs/B-BOOT/plan-review/cycle-01/target.json"
    (tmp / rel_target).parent.mkdir(parents=True, exist_ok=True)
    write_lf(tmp / rel_target, json.dumps({
        "review_type": "plan", "run_id": "B-BOOT", "cycle": 1,
        "plan_files": [{"path": p, "sha256": h}
                       for p, h in mod.covered(tmp).items()],
    }, indent=2) + "\n")

    return sh(sys.executable, str(tmp / "scripts" / "bootstrap_gate.py"),
              "record", "--decision", "APPROVE", "--decided-by", "Alex Zamurko",
              "--note", "#gap, 9 Sep 2026, Alex Zamurko: fixture approval",
              "--target", rel_target, cwd=tmp)


def impl_approval(tmp: Path, run_id: str = "T-001") -> str:
    """Write §7.3's plan approval record and return the approved plan's hash.

    B02-F07 made the approval record mandatory for an implementation freeze,
    because the whole implementation evidence set is now preserved and validated
    from the preserved copies — and you cannot preserve an approved plan that
    nothing names. Decision F already said check 13 refuses without the record
    rather than passing vacuously; this makes freeze refuse at the same point
    instead of leaving the cycle to fail the gate afterwards.

    Returns the real hash rather than a dummy: freeze verifies that the supplied
    --approved-plan-hash matches the artifact the approval names, so a fixture
    passing an arbitrary digest is now refused, correctly.

    Module level on purpose. Four controls tonight crashed as NameErrors because
    helpers defined part-way through main() were not yet bound where they were
    used, and a crash reads as a pass.
    """
    plan = tmp / "plan" / "01-PLAN.md"
    digest = hashlib.sha256(plan.read_bytes()).hexdigest()
    # write_lf does not create parents. Without this the helper raised
    # FileNotFoundError, which killed the suite two thirds of the way through
    # and produced no FAIL line — so the grep read clean and the count refresh
    # recorded 29 controls where there are 95.
    (tmp / "runs" / run_id / "plan-approval").mkdir(parents=True, exist_ok=True)
    write_lf(tmp / "runs" / run_id / "plan-approval" / "approval.json",
             json.dumps({"decision": "APPROVE",
                         "approved_plan_hash": digest,
                         "approved_plan_path": "plan/01-PLAN.md",
                         "decided_by": "Alex Zamurko",
                         "decided_at": "2026-09-12T00:00:00Z"}, indent=2) + "\n")
    return digest


def do_freeze(tmp: Path, *extra: str) -> subprocess.CompletedProcess:
    return runner(tmp, "freeze", "--run", "T-001", "--type", "plan",
                  "--prompt", "specs/prompt.md", "--file", "plan/01-PLAN.md", *extra)


def reply_for(tmp: Path, body: str, run: str = "T-001",
              rtype: str = "plan", cycle: int = 1) -> str:
    """A reply quoting the cycle's target hash.

    Capture validity requires it: the review prompt tells the reviewer to quote
    the target SHA-256, and a capture without it is not demonstrably a capture
    of this target. Fixtures have to satisfy the same rule real captures do.
    """
    p = (tmp / "runs" / run / f"{rtype}-review" / f"cycle-{cycle:02d}"
         / "target.sha256")
    if not p.is_file():
        # Some fixtures deliberately have no frozen cycle — recording against an
        # unfrozen directory is one of the refusals under test. Those never
        # reach capture validity, so the body alone is right.
        return body
    return f"TARGET_SHA256 {p.read_text(encoding='utf-8').strip()}\n\n{body}"


def fake_cycles(tmp: Path, n: int, close_last: bool = True) -> None:
    """n cycle directories, each with raw output unless the last is left open.

    These deliberately do NOT pass MC-2 — they carry a target.json with only a
    cycle number and no hashed artifacts. That makes them the right fixture for
    "a directory exists" questions and the wrong one for anything about the
    four-cycle budget, which counts cycles that pass the gate. See B01-F01.
    """
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

            # The reviewer is asked to judge conformance to the protocol, so the
            # protocol has to be in the file it is judging from. An earlier
            # version named PROTOCOL_SHA256 in the header and stopped, which
            # would have produced a review of a document the reviewer never saw.
            proto_text = (tmp / "specs" / "protocol.md").read_text(encoding="utf-8")
            body = "\n".join(l for l in proto_text.splitlines() if l.strip())
            missing = [l for l in body.splitlines() if l not in ci]
            if missing:
                failures.append(
                    "codex-input.md does not carry the protocol text, only its "
                    "hash. The reviewer cannot read a hash, so it would be asked "
                    "to check conformance to a document it never saw.\n"
                    f"  first absent line: {missing[0][:70]!r}")
            else:
                print("  [ok] codex-input.md carries the protocol text, not just its hash")

            crlf = [n for n in ("target.json", "target.sha256", "codex-input.md")
                    if b"\r" in (cyc / n).read_bytes()]
            if crlf:
                failures.append(f"frozen evidence carries CR bytes: {', '.join(crlf)}\n"
                                "  the same freeze on another platform would produce a "
                                "different TARGET_SHA256")
            else:
                print("  [ok] frozen evidence is LF, so its hashes are platform-neutral")

            write_lf(tmp / "reply.md", reply_for(tmp,
                "Finding ID: C01-F01\nClass: UNTESTED RULE\n"
                "Requirement ID: R-B7\nEvidence: ...\n"))
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

    # ---- B01-F14: the enforcement status is required, not just written ----
    # cmd_init wrote mc1_enforcement, but nothing required it when a run was
    # consumed, so the rule held only for runs that already satisfied it. The
    # actual BOOTSTRAP-001 run lacked the field and was accepted for cycle 02.
    def strip_mc1(t: Path):
        do_init(t)
        rj = t / "runs" / "T-001" / "run.json"
        d = json.loads(rj.read_text(encoding="utf-8"))
        d.pop("mc1_enforcement", None)
        write_lf(rj, json.dumps(d, indent=2) + "\n")
        return do_freeze(t)
    expect_refused("a run with no mc1_enforcement", "records no mc1_enforcement",
                   strip_mc1)

    def bad_mc1(t: Path):
        do_init(t)
        rj = t / "runs" / "T-001" / "run.json"
        d = json.loads(rj.read_text(encoding="utf-8"))
        d["mc1_enforcement"] = "ENFORCED"
        write_lf(rj, json.dumps(d, indent=2) + "\n")
        return do_freeze(t)
    expect_refused("a run claiming an unrecognised enforcement status",
                   "not a recognised status", bad_mc1)

    # A new run writes it, so the positive side is covered too: a refusal-only
    # pair would pass just as well if init had stopped writing the field.
    tmc = make_repo(); made.append(tmc)
    do_init(tmc)
    _rj = json.loads((tmc / "runs/T-001/run.json").read_text(encoding="utf-8"))
    if _rj.get("mc1_enforcement") != "CONVENTION_ONLY":
        failures.append(f"init did not record the enforcement status: "
                        f"{_rj.get('mc1_enforcement')!r}")
    else:
        print("  [ok] a new run records its enforcement status")

    def protocol_drift(t: Path):
        do_init(t)
        write_lf(t / "specs" / "protocol.md", PROTOCOL_BODY + "V22 added later\n")
        return do_freeze(t)
    # The message changed with B02-F05: the pin check now walks the effective
    # governing set rather than run.json's protocol and spec_files separately,
    # so one refusal covers both and names the path. The needle asserts the
    # path, which is what a reader needs, rather than which branch produced it.
    expect_refused("protocol edited after init",
                   "governing artifact changed: specs/protocol.md",
                   protocol_drift)

    def spec_drift(t: Path):
        do_init(t)
        write_lf(t / "specs" / "spec.md", SPEC_BODY + "rule G8\n")
        return do_freeze(t)
    expect_refused("spec edited after init",
                   "governing artifact changed: specs/spec.md", spec_drift)

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

    # ---- B01-F01: the budget counts valid cycles, not directories ----
    # This control used to call fake_cycles(4), which builds directories that
    # fail MC-2, and assert the fifth freeze was refused. So it asserted that
    # four INVALID cycles exhaust the budget — the finding itself, written down
    # as expected behaviour and passing for weeks.
    #
    # §2: "Only cycles that pass the MC-2 conformance gate count toward this
    # maximum." §3: an invalid cycle "cannot consume one of the four valid
    # review cycles."
    print()
    print("the four-cycle budget counts valid cycles")

    tbud = make_repo(); made.append(tbud)
    do_init(tbud)
    fake_cycles(tbud, 4)
    r = do_freeze(tbud)
    if r.returncode != 0 and "budget" in (r.stdout + r.stderr):
        failures.append("four cycles that fail MC-2 exhausted the budget; "
                        "invalid cycles cannot consume it")
    else:
        print("  [ok] four cycles that fail MC-2 do not consume the budget")

    # And four that pass it do. Built through the real freeze and record path,
    # because a fixture that hand-writes cycles is how the control above came to
    # assert the wrong thing.
    tfull = make_repo(); made.append(tfull)
    do_init(tfull)

    def close_cycle(root: Path, n: int) -> bool:
        c = root / "runs" / "T-001" / "plan-review" / f"cycle-{n:02d}"
        th = (c / "target.sha256").read_text(encoding="utf-8").strip()
        write_lf(root / f"reply{n}.md",
                 f"TARGET_SHA256 {th}\n\nNo findings in any category.\n")
        rr = runner(root, "record", "--cycle",
                    f"runs/T-001/plan-review/cycle-{n:02d}",
                    "--output", f"reply{n}.md", "--invocation", "manual",
                    "--zero-findings")
        return rr.returncode == 0

    def led(root: Path, *a: str) -> subprocess.CompletedProcess:
        return sh(sys.executable, str(root / "scripts" / "ledger.py"), *a,
                  "--review", "runs/T-001/plan-review", cwd=root)

    built = 0
    for i in range(1, 5):
        if do_freeze(tfull).returncode != 0:
            break
        if not close_cycle(tfull, i):
            break
        built = i
        # The loop has to stay on CONTINUE for four cycles, which means each one
        # must show progress. A cycle that only adds an open finding is STALLED
        # by §6 at n=2 — correctly — and the freeze after it is refused before
        # the budget is ever consulted. So each cycle resolves the previous
        # finding and raises its own.
        if i > 1:
            led(tfull, "resolve", "--cycle", str(i), "--id", f"C{i-1:02d}-F01",
                "--evidence", "repaired and demonstrated in this cycle")
        led(tfull, "raise", "--cycle", str(i), "--id", f"C{i:02d}-F01",
            "--class", "UNTESTED RULE")
        led(tfull, "respond", "--cycle", str(i), "--id", f"C{i:02d}-F01",
            "--disposition", "ACCEPT", "--note", "will repair next cycle")

    if built < 4:
        failures.append(f"fixture: only built {built} valid cycle(s), cannot "
                        "test the budget")
    else:
        r = do_freeze(tfull)
        if r.returncode == 0:
            failures.append("a fifth cycle was frozen after four valid ones")
        elif "budget" not in (r.stdout + r.stderr):
            failures.append(f"refused, but not for the budget\n{r.stdout}{r.stderr}")
        else:
            print("  [ok] four cycles that pass MC-2 do consume the budget")

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

    # ---- B01-F17: the other three implementation refusals ----
    # cmd_freeze raises five refusals for implementation review. Two were
    # exercised above and three were not, while this suite's closing line said
    # every refusal is reachable. Each is a distinct guard on a distinct §10.1
    # field, so covering two of five and claiming five is the same shape of
    # over-claim as the seam-1 probes.
    GOOD_HASH = "a" * 64

    def impl_no_commit(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "implementation",
                      "--prompt", "specs/prompt.md",
                      "--approved-plan-hash", GOOD_HASH)
    expect_refused("implementation review with no candidate commit",
                   "requires --candidate-commit", impl_no_commit)

    def impl_unresolvable_commit(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "implementation",
                      "--prompt", "specs/prompt.md",
                      "--candidate-commit", "0" * 40,
                      "--approved-plan-hash", GOOD_HASH)
    expect_refused("candidate commit that does not resolve",
                   "does not resolve", impl_unresolvable_commit)

    # ---- B01-F07: the recorded hashes describe THIS cycle's pin set ----
    # Codex: "protocol_sha256 and spec_sha256 are checked for presence only; no
    # check ties them to the pinned artifacts or to run.json." They were copied
    # verbatim from run.json, so they described the set as it stood at init.
    #
    # BOOTSTRAP-001 shows the consequence: its cycle 02 records the digest of a
    # spec set that the amendment effective at cycle 2 had already released.
    print()
    print("recorded hashes follow the cycle's own pin set (B01-F07)")

    t7 = make_repo(); made.append(t7)
    do_init(t7); do_freeze(t7)
    run7 = json.loads((t7 / "runs/T-001/run.json").read_text(encoding="utf-8"))
    tgt7a = json.loads((t7 / "runs/T-001/plan-review/cycle-01/target.json")
                       .read_text(encoding="utf-8"))
    if tgt7a["protocol_sha256"] != run7["protocol_sha256"]:
        failures.append("cycle 01 records a protocol hash that is not the "
                        "pinned one")
    elif tgt7a["spec_sha256"] != run7["spec_sha256"]:
        failures.append("with no amendment in force the recorded spec digest "
                        "should equal the run's")
    else:
        print("  [ok] with no amendment, the recorded hashes match the run")

    # Now release the spec from the governing set, effective cycle 2. The next
    # cycle must record a different spec digest, because a different set governs
    # it. Copying run.json forward would leave both cycles claiming the same one.
    # Cycle 01 closed through the real record path. Writing codex-output-raw.md
    # by hand leaves no findings.json, the controller then refuses to say
    # whether another cycle is permitted, and B01-F02's check blocks the freeze
    # — so this control would report a pin failure that never happened. One open
    # finding, raised in the ledger, keeps the loop on CONTINUE.
    _th7 = (t7 / "runs/T-001/plan-review/cycle-01/target.sha256") \
        .read_text(encoding="utf-8").strip()
    write_lf(t7 / "reply7.md",
             f"TARGET_SHA256 {_th7}\n\nFinding ID: C01-F01\n"
             "Class: UNTESTED RULE\nEvidence: x\n")
    _r7 = runner(t7, "record", "--cycle", "runs/T-001/plan-review/cycle-01",
                 "--output", "reply7.md", "--invocation", "manual")
    if _r7.returncode != 0:
        failures.append(f"fixture: could not record cycle 01\n{_r7.stderr}{_r7.stdout}")
    _l7 = sh(sys.executable, str(t7 / "scripts" / "ledger.py"), "raise",
             "--review", "runs/T-001/plan-review", "--cycle", "1",
             "--id", "C01-F01", "--class", "UNTESTED RULE", cwd=t7)
    if _l7.returncode != 0:
        failures.append(f"fixture: could not raise the finding\n{_l7.stderr}{_l7.stdout}")

    # Written here rather than calling amend(), which is defined further down in
    # this function and was therefore not yet bound: the block crashed on a
    # NameError after the first assertion, printing one [ok] and no failure.
    # A control that never runs is indistinguishable from one that passed.
    write_lf(t7 / "runs" / "T-001" / "pin-amendments.json", json.dumps({
        "schema": "run-pin-amendments/1",
        "amendments": [{
            "effective_cycle": 2,
            "reason": "the pinned spec is also a review target, which the "
                      "separation specification forbids",
            "affected_artifacts": ["specs/spec.md"],
            "prior_pin_set": ["specs/protocol.md", "specs/spec.md"],
            "new_pin_set": ["specs/protocol.md"],
            "authorized_by": "Alex Zamurko",
            "at": "2026-09-10T00:00:00Z",
        }]}, indent=2) + "\n")
    r = do_freeze(t7)
    if r.returncode != 0:
        failures.append(f"freeze after the amendment failed\n{r.stdout}{r.stderr}")
    else:
        tgt7b = json.loads((t7 / "runs/T-001/plan-review/cycle-02/target.json")
                           .read_text(encoding="utf-8"))
        if tgt7b["spec_sha256"] == tgt7a["spec_sha256"]:
            failures.append(
                "cycle 02 records the same spec digest as cycle 01 despite an "
                "amendment releasing the spec; the field is copied from "
                "run.json rather than derived from what governs the cycle")
        elif "specs/spec.md" in tgt7b.get("governing_pins", []):
            failures.append("the released spec is still in the governing set")
        else:
            print("  [ok] releasing a spec changes what the next cycle records")

        # And cycle 01 is untouched: its record still describes the set it was
        # actually conducted under. "Never validate historical cycles against
        # the latest pin set" applies to what they recorded, too.
        again = json.loads((t7 / "runs/T-001/plan-review/cycle-01/target.json")
                           .read_text(encoding="utf-8"))
        if again["spec_sha256"] != tgt7a["spec_sha256"]:
            failures.append("the amendment changed what cycle 01 recorded")
        else:
            print("  [ok] the earlier cycle's record is unchanged by the "
                  "amendment")

    # ---- B01-F04: the reviewer is given what it is asked to judge against ----
    # Codex: "compose_input carries the protocol but not the pinned spec, and
    # for implementation review omits the target identifiers entirely." A hash
    # in a header is not a document a reviewer can read.
    print()
    print("the review input carries the spec and the target identity")

    t4 = make_repo(); made.append(t4)
    do_init(t4); do_freeze(t4)
    ci4 = (t4 / "runs/T-001/plan-review/cycle-01/codex-input.md") \
        .read_text(encoding="utf-8")
    spec_body = (t4 / "specs" / "spec.md").read_text(encoding="utf-8").strip()
    if spec_body.splitlines()[0] not in ci4:
        failures.append("the composed input does not contain the pinned spec "
                        "text, only its hash")
    elif "The pinned specification" not in ci4:
        failures.append("the spec is present but not identified as the pinned "
                        "specification")
    else:
        print("  [ok] the pinned spec is embedded, not merely hashed")

    # Editing a pinned spec must not silently reach the reviewer: the text
    # embedded has to be the text the header names.
    t4b = make_repo(); made.append(t4b)
    do_init(t4b)
    sp = t4b / "specs" / "spec.md"
    sp.write_text(sp.read_text(encoding="utf-8") + "\nrule G9\n", encoding="utf-8")
    r = do_freeze(t4b)
    if r.returncode == 0:
        failures.append("a cycle was frozen embedding a spec that no longer "
                        "matches the hash in its own header")
    else:
        print("  [ok] refused: a drifted spec is not embedded under its old hash")

    # Implementation review: the §10.1 fields have to reach the reviewer.
    t4c = make_repo(); made.append(t4c)
    do_init(t4c)
    write_lf(t4c / "diff.txt", "diff --git a/x b/x\n")
    write_lf(t4c / "results.txt", "3 passed\n")
    head4 = sh("git", "rev-parse", "HEAD", cwd=t4c).stdout.strip()
    plan4 = impl_approval(t4c)
    r = runner(t4c, "freeze", "--run", "T-001", "--type", "implementation",
               "--prompt", "specs/prompt.md", "--candidate-commit", head4,
               "--approved-plan-hash", plan4, "--diff", "diff.txt",
               "--test-results", "results.txt")
    if r.returncode != 0:
        failures.append(f"implementation freeze failed\n{r.stdout}{r.stderr}")
    else:
        ci = (t4c / "runs/T-001/implementation-review/cycle-01/codex-input.md") \
            .read_text(encoding="utf-8")
        # The field names are the target's own, not invented here. Writing
        # test_result_sha256 when the target records test_result_hash is how a
        # control asserts something the system never claimed.
        missing = [f for f in (head4, plan4, "candidate_tree_hash",
                               "test_result_hash", "diff_hash") if f not in ci]
        if missing:
            failures.append(
                "the implementation review input omits target identifiers the "
                f"reviewer needs: {missing}")
        else:
            print("  [ok] an implementation review input carries the §10.1 "
                  "target identity")

    # ---- B01-F05: a mutable reference is resolved before it is recorded ----
    # Alex Zamurko, 10 September: "resolve any mutable reference such as HEAD to
    # an immutable commit SHA at freeze time and verify the corresponding tree
    # hash." Before this the reference was stored as typed, so a target could
    # name HEAD and the reviewed implementation could move underneath it while
    # checks 11 and 12 kept passing against whatever HEAD had become.
    print()
    print("mutable candidate references")

    t5 = make_repo(); made.append(t5)
    do_init(t5)
    write_lf(t5 / "diff.txt", "diff --git a/x b/x\n")
    write_lf(t5 / "results.txt", "ok\n")
    head = sh("git", "rev-parse", "HEAD", cwd=t5).stdout.strip()
    plan5 = impl_approval(t5)
    r = runner(t5, "freeze", "--run", "T-001", "--type", "implementation",
               "--prompt", "specs/prompt.md", "--candidate-commit", "HEAD",
               "--approved-plan-hash", plan5, "--diff", "diff.txt",
               "--test-results", "results.txt")
    if r.returncode != 0:
        failures.append(f"freezing with HEAD was refused outright; the decision "
                        f"is to resolve it, not reject it\n{r.stdout}{r.stderr}")
    else:
        tgt = json.loads((t5 / "runs/T-001/implementation-review/cycle-01"
                          / "target.json").read_text(encoding="utf-8"))
        if tgt["candidate_commit"] == "HEAD":
            failures.append("the target recorded the literal reference HEAD, so "
                            "the reviewed implementation can still move under it")
        elif tgt["candidate_commit"] != head:
            failures.append(f"HEAD resolved to {tgt['candidate_commit']}, "
                            f"expected {head}")
        elif tgt.get("candidate_commit_supplied") != "HEAD":
            failures.append("the target does not record that a mutable "
                            "reference was supplied, so a reader cannot tell")
        else:
            # The tree must belong to the resolved commit, not be re-derived
            # from the name a second time.
            tree = sh("git", "rev-parse", f"{head}^{{tree}}", cwd=t5).stdout.strip()
            if tgt["candidate_tree_hash"] != tree:
                failures.append("the recorded tree does not belong to the "
                                "resolved commit")
            else:
                print("  [ok] HEAD is resolved to an immutable SHA, the "
                      "reference is recorded, and the tree matches")

    # And the resolution has to actually bind: moving HEAD afterwards must not
    # change what the frozen cycle refers to.
    if r.returncode == 0:
        write_lf(t5 / "later.txt", "a commit made after the freeze\n")
        sh("git", "add", "-A", cwd=t5)
        sh("git", "commit", "-qm", "after the freeze", cwd=t5)
        new_head = sh("git", "rev-parse", "HEAD", cwd=t5).stdout.strip()
        tgt = json.loads((t5 / "runs/T-001/implementation-review/cycle-01"
                          / "target.json").read_text(encoding="utf-8"))
        if new_head == head:
            failures.append("fixture: HEAD did not move")
        elif tgt["candidate_commit"] != head:
            failures.append("the frozen target followed HEAD to a later commit")
        else:
            print("  [ok] the frozen target still names the commit that was "
                  "reviewed after HEAD moves on")

    def impl_no_diff(t: Path):
        do_init(t)
        return runner(t, "freeze", "--run", "T-001", "--type", "implementation",
                      "--prompt", "specs/prompt.md", "--candidate-commit", "HEAD",
                      "--approved-plan-hash", GOOD_HASH)
    expect_refused("implementation review with no diff", "requires --diff",
                   impl_no_diff)

    def impl_no_test_results(t: Path):
        do_init(t)
        write_lf(t / "candidate.diff", "--- a\n+++ b\n@@ -1 +1 @@\n-x\n+y\n")
        return runner(t, "freeze", "--run", "T-001", "--type", "implementation",
                      "--prompt", "specs/prompt.md", "--candidate-commit", "HEAD",
                      "--approved-plan-hash", GOOD_HASH, "--diff", "candidate.diff")
    expect_refused("implementation review with no test results",
                   "requires --test-results", impl_no_test_results)

    def record_twice(t: Path):
        do_init(t)
        do_freeze(t)
        cyc = t / "runs" / "T-001" / "plan-review" / "cycle-01"
        write_lf(t / "reply.md", reply_for(t,
                     "Finding ID: C01-F01\nClass: UNTESTED RULE\n"
                     "Requirement ID: R-B7\nEvidence: ...\n"))
        runner(t, "record", "--cycle", str(cyc), "--output", "reply.md",
               "--invocation", "manual")
        write_lf(t / "reply2.md", reply_for(t, "Finding ID: C01-F02\n"
                                       "Class: WRONG OWNERSHIP\n"))
        return runner(t, "record", "--cycle", str(cyc), "--output", "reply2.md",
                      "--invocation", "manual")
    # Was a flat write-once refusal. Issue 6 replaced it: a second capture is
    # recorded and preserved, it simply does not displace the designated one
    # without explicit invalidation. The evidence is still never overwritten.
    expect_refused("re-recording without superseding", "already the authoritative",
                   record_twice)

    def record_unfrozen(t: Path):
        write_lf(t / "reply.md", reply_for(t,
                     "Finding ID: C01-F01\nClass: UNTESTED RULE\n"
                     "Requirement ID: R-B7\nEvidence: ...\n"))
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

    # ---- the bootstrap gate, from the runner's side ----
    # Every init above passes --bootstrap-exempt, so without these three the gate
    # would be entirely absent from this suite and could be deleted from
    # cmd_init without a single test noticing.
    print()
    print("bootstrap gate")

    def real_init(t: Path) -> subprocess.CompletedProcess:
        return runner(t, "init", "--run", "A1E-001", "--protocol",
                      "specs/protocol.md", "--spec", "specs/spec.md")

    expect_refused("a real run created with no bootstrap review",
                   "bootstrap_review not satisfied", real_init)

    t2 = make_repo(); made.append(t2)
    if approve_bootstrap(t2).returncode != 0:
        failures.append("could not record a bootstrap approval in the fixture")
    else:
        r = real_init(t2)
        if r.returncode != 0:
            failures.append("a real run was refused despite an approved bootstrap "
                            f"review; the gate would block everything:\n{r.stdout}{r.stderr}")
        else:
            run_json = json.loads(
                (t2 / "runs" / "A1E-001" / "run.json").read_text(encoding="utf-8"))
            if run_json.get("bootstrap_review") != "APPROVED":
                failures.append("the run does not record that it ran under an "
                                "approved bootstrap review")
            else:
                print("  [ok] a real run proceeds once the bootstrap review is approved")

    # Editing a gated component after approval must re-block, or the approval
    # outlives the code it covered. Asserted inline rather than through
    # expect_refused, which builds its own fresh repo: this control needs the
    # same repo that was just approved, and a fresh one would refuse for the
    # ordinary no-review reason and look like a pass.
    p = t2 / "scripts" / "validate_cycle.py"
    p.write_text(p.read_text(encoding="utf-8") + "\n# later edit\n", encoding="utf-8")
    r = runner(t2, "init", "--run", "A1E-002", "--protocol", "specs/protocol.md",
               "--spec", "specs/spec.md")
    blob = (r.stdout + r.stderr).lower()
    if r.returncode == 0:
        failures.append("a real run was created after a reviewed component "
                        "changed; the approval outlived the code it covered")
    elif "has changed since it was reviewed" not in blob:
        failures.append("refused after a component changed, but not for that "
                        f"reason:\n  got {blob.strip()[:300]}")
    else:
        print("  [ok] refused: a real run after a reviewed component changed")

    # ---- issue 4: authoritative per-cycle findings ----
    # Alex Zamurko, 9 September: "Add tests for populated findings, explicit
    # zero findings, missing findings, and malformed findings."
    print()
    print("authoritative findings")

    def recorded(t: Path, body: str, *extra: str):
        do_init(t)
        do_freeze(t)
        write_lf(t / "reply.md", reply_for(t, body))
        cyc = t / "runs" / "T-001" / "plan-review" / "cycle-01"
        return runner(t, "record", "--cycle", str(cyc), "--output", "reply.md",
                      "--invocation", "manual", *extra), cyc

    POPULATED = ("Finding ID: C01-F01\nClass: UNTESTED RULE\nEvidence: x\n\n"
                 "Finding ID: C01-F02\nClass: WRONG OWNERSHIP\nEvidence: y\n")

    t6 = make_repo(); made.append(t6)
    r, cyc = recorded(t6, POPULATED)
    if r.returncode != 0:
        failures.append(f"recording populated findings failed:\n{r.stdout}{r.stderr}")
    else:
        d = json.loads((cyc / "findings.json").read_text(encoding="utf-8"))
        ids = [f["id"] for f in d["findings"]]
        if ids != ["C01-F01", "C01-F02"] or d["count"] != 2:
            failures.append(f"findings.json did not capture both findings: {d}")
        elif d.get("source_sha256") != hashlib.sha256(
                (cyc / "codex-output-raw.md").read_bytes()).hexdigest():
            failures.append("findings.json is not bound to the capture it was "
                            "extracted from")
        else:
            print("  [ok] populated: both findings extracted and bound to the capture")

    t7 = make_repo(); made.append(t7)
    r, cyc = recorded(t7, "The plan is sound. No findings.\n", "--zero-findings")
    if r.returncode != 0:
        failures.append(f"explicit zero findings should record:\n{r.stdout}{r.stderr}")
    else:
        d = json.loads((cyc / "findings.json").read_text(encoding="utf-8"))
        if d["count"] != 0 or not d.get("zero_findings_asserted"):
            failures.append("zero findings recorded without the assertion flag")
        else:
            print("  [ok] explicit zero: recorded as asserted, not inferred")

    t8 = make_repo(); made.append(t8)
    r, _ = recorded(t8, "The plan is sound. No findings.\n")
    if r.returncode == 0:
        failures.append("a review with no finding blocks recorded silently as "
                        "zero; absence must never mean zero")
    elif "--zero-findings" not in (r.stdout + r.stderr):
        failures.append("refused a no-blocks review without naming --zero-findings")
    else:
        print("  [ok] refused: no finding blocks and no explicit zero assertion")

    t9 = make_repo(); made.append(t9)
    r, _ = recorded(t9, POPULATED, "--zero-findings")
    if r.returncode == 0:
        failures.append("--zero-findings accepted alongside two finding blocks")
    else:
        print("  [ok] refused: --zero-findings contradicted by present findings")

    t10 = make_repo(); made.append(t10)
    r, cyc = recorded(t10, "Finding ID: C01-F01\nClass: SOMETHING INVENTED\n")
    if r.returncode == 0:
        failures.append("a class outside the closed vocabulary was recorded")
    elif (cyc / "codex-output-raw.md").exists():
        failures.append("raw output was written despite the findings being "
                        "unparseable; nothing should be written on refusal")
    else:
        print("  [ok] refused: class outside §4, and nothing written")

    t11 = make_repo(); made.append(t11)
    r, cyc = recorded(t11, "Finding ID: C01-F01\nEvidence: no class line here\n")
    if r.returncode == 0:
        failures.append("a finding block with no Class: line was recorded")
    else:
        print("  [ok] refused: finding block with no class")

    # ---- issue 5: deterministic review-result integrity ----
    # Alex Zamurko's minimum spec, 9 September. The first version of
    # --zero-findings stopped absence meaning zero, but left the case he named:
    # the reviewer produced findings, the parser failed to see them, and an
    # honest operator asserts zero over a review nobody read correctly.
    print()
    print("review-result integrity")

    t12 = make_repo(); made.append(t12)
    r, _ = recorded(t12, "Required correction: separate the deficiency.\n",
                    "--zero-findings")
    if r.returncode == 0:
        failures.append("zero was asserted over a review carrying finding "
                        "signals the parser did not account for")
    else:
        print("  [ok] refused: zero asserted over an unparsed finding signal")

    t13 = make_repo(); made.append(t13)
    r, _ = recorded(t13, "Finding ID: not-an-id\nClass: UNTESTED RULE\n")
    if r.returncode == 0:
        failures.append("an identifier outside the canonical grammar was "
                        "silently accepted")
    elif "canonical grammar" not in (r.stdout + r.stderr):
        failures.append("refused a bad identifier without naming the grammar")
    else:
        print("  [ok] refused: identifier outside the canonical grammar")

    # Requirement 5: never silently corrected. The refusal above must not have
    # written a repaired identifier anywhere.
    t14 = make_repo(); made.append(t14)
    r, cyc = recorded(t14, "Finding ID: C1-F1\nClass: UNTESTED RULE\n")
    if (cyc / "findings.json").exists():
        failures.append("a findings.json was written for a review whose "
                        "identifier failed the grammar")
    else:
        print("  [ok] a malformed identifier writes nothing, corrected or otherwise")

    # The grammar has one authoritative home, and the runner reads it rather
    # than restating it. Break the declaration and the parse must stop.
    t15 = make_repo(); made.append(t15)
    sch = t15 / "specs" / "evidence-schema-v1.0.md"
    sch.write_text(sch.read_text(encoding="utf-8")
                   .replace("FINDING_ID_GRAMMAR", "REMOVED_GRAMMAR"),
                   encoding="utf-8")
    r, _ = recorded(t15, "Finding ID: C01-F01\nClass: UNTESTED RULE\n")
    if r.returncode == 0:
        failures.append("the runner parsed findings with no canonical grammar "
                        "declared; it is carrying its own copy")
    else:
        print("  [ok] refused: no canonical grammar declared in the schema")

    # ---- issue 6: authoritative capture ----
    # Before this, a failed capture killed the cycle, so the only way to retry
    # was to delete what was there. That happened three times in one afternoon,
    # two junk captures passed MC-2, and a better capture sat unnoticed in
    # another directory with nothing saying which governed.
    print()
    print("authoritative capture")

    def with_target(t: Path, body: str) -> str:
        th = (t / "runs" / "T-001" / "plan-review" / "cycle-01"
              / "target.sha256").read_text(encoding="utf-8").strip()
        return f"TARGET_SHA256 {th}\n\n{body}"

    GOOD = "Finding ID: C01-F01\nClass: UNTESTED RULE\nEvidence: x\n"

    t16 = make_repo(); made.append(t16)
    do_init(t16); do_freeze(t16)
    cyc = t16 / "runs" / "T-001" / "plan-review" / "cycle-01"
    write_lf(t16 / "junk.md", "Get-Clipboard -Raw | Set-Content reply.md\n")
    r = runner(t16, "record", "--cycle", str(cyc), "--output", "junk.md",
               "--invocation", "manual")
    if r.returncode == 0:
        failures.append("a capture not quoting the target hash was accepted")
    elif not (cyc / "captures" / "attempt-01" / "raw.md").is_file():
        failures.append("a rejected capture was not preserved; the only way to "
                        "retry is then to delete evidence, which is the "
                        "behaviour issue 6 removes")
    else:
        print("  [ok] an invalid capture is refused and preserved, not discarded")

    write_lf(t16 / "good.md", with_target(t16, GOOD))
    r = runner(t16, "record", "--cycle", str(cyc), "--output", "good.md",
               "--invocation", "manual", "--reason", "attempt 1 caught the shell command")
    if r.returncode != 0:
        failures.append(f"a valid retry after a failed capture was refused:\n{r.stdout}{r.stderr}")
    else:
        log = json.loads((cyc / "capture-log.json").read_text(encoding="utf-8"))
        if log["authoritative"] != 2 or len(log["attempts"]) != 2:
            failures.append(f"capture log did not record both attempts: {log}")
        else:
            print("  [ok] the first valid capture becomes authoritative, both kept")

    write_lf(t16 / "other.md", with_target(t16, GOOD.replace("F01", "F02")))
    r = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
               "--invocation", "manual")
    if r.returncode == 0:
        failures.append("a later capture displaced the authoritative one with "
                        "no explicit invalidation")
    else:
        print("  [ok] refused: a later capture cannot displace silently")

    r = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
               "--invocation", "manual", "--supersede-capture")
    if r.returncode == 0:
        failures.append("--supersede-capture was accepted with no reason")
    else:
        print("  [ok] refused: superseding without a stated reason")

    # ---- ruling 3, 9 September: supersession needs an outside authority ----
    # "Allowing the implementing agent to choose a later Codex capture creates a
    # direct cherry-picking path. Preserving all attempts is not sufficient if
    # the same party can decide which one governs."
    #
    # --reason alone was not an outside authority. It is a string the
    # implementing agent types, in a command the implementing agent runs.
    log_before = json.loads((cyc / "capture-log.json").read_text(encoding="utf-8"))
    superseded = log_before["authoritative_sha256"]
    superseding = hashlib.sha256((t16 / "other.md").read_bytes()).hexdigest()
    approval_path = cyc / "capture-supersession-approval.json"

    r = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
               "--invocation", "manual", "--supersede-capture",
               "--reason", "partial paste; full reply recaptured")
    if r.returncode == 0:
        failures.append("supersession succeeded on a reason alone, with no "
                        "approval from outside the implementing agent")
    elif "not authorized" not in (r.stdout + r.stderr):
        failures.append(f"supersession refused, but not for want of authority:\n"
                        f"{r.stdout}{r.stderr}")
    elif superseding not in (r.stdout + r.stderr):
        failures.append("the refusal did not print the hashes the approval must "
                        "name, so obtaining one would be guesswork")
    else:
        print("  [ok] refused: a reason alone does not authorize supersession")

    def approve(**over):
        rec = {"schema": "capture-supersession/1",
               "cycle": cyc.name,
               "superseded_sha256": superseded,
               "superseding_sha256": superseding,
               "authorized_by": "Alex Zamurko",
               "reason": "attempt 2 truncated mid-finding; recapture is complete",
               "at": "2026-09-09T21:40:00Z"}
        rec.update(over)
        write_lf(approval_path, json.dumps(rec, indent=2) + "\n")

    def refuse_with(label: str, needle: str, **over) -> None:
        approve(**over)
        rr = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
                    "--invocation", "manual", "--supersede-capture",
                    "--reason", "partial paste; full reply recaptured")
        if rr.returncode == 0:
            failures.append(f"{label}: accepted")
        elif needle.lower() not in (rr.stdout + rr.stderr).lower():
            failures.append(f"{label}: refused for the wrong reason\n"
                            f"  wanted {needle!r}\n  got {(rr.stderr + rr.stdout)[:300]}")
        else:
            print(f"  [ok] refused: {label}")

    refuse_with("an approval naming nobody", "authorized_by", authorized_by="")
    refuse_with("an approval whose reason is a placeholder", "at least",
                reason="ok")
    refuse_with("an approval for a different capture", "does not match",
                superseding_sha256="0" * 64)
    refuse_with("an approval for a different cycle", "does not match",
                cycle="cycle-09")
    refuse_with("an approval of the wrong kind", "schema",
                schema="runner-approval/1")

    # B02-F10, second half. Alex Zamurko: "Add negative controls for every
    # claimed refusal, including malformed JSON and absent timestamp cases."
    # Both refusals existed in require_approval and neither was exercised, while
    # the suite's closing line reported every refusal as reachable.
    refuse_with("an approval with no timestamp", "no `at` timestamp", at="")

    write_lf(approval_path, "{ this is not json\n")
    r = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
               "--invocation", "manual", "--supersede-capture",
               "--reason", "partial paste; full reply recaptured")
    if r.returncode == 0:
        failures.append("a malformed approval record was accepted")
    elif "not valid JSON" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the malformed record\n"
                        f"{r.stdout}{r.stderr}")
    else:
        print("  [ok] refused: an approval record that is not valid JSON")

    # ---- B02-F04: a refused supersession must leave the cycle intact ----
    # Codex's reproduction, exactly: a valid authoritative capture, a correctly
    # bound approval, and a replacement containing a finding, invoked with
    # --zero-findings. The command returned 1 saying "Nothing written" while
    # codex-output-raw.md and findings.json had already been deleted and the
    # log still designated the old attempt. The bytes survived in captures/;
    # the cycle did not.
    approve()
    before_raw = (cyc / "codex-output-raw.md").read_bytes()
    before_fj = (cyc / "findings.json").read_bytes()
    before_log = json.loads((cyc / "capture-log.json").read_text(encoding="utf-8"))
    r = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
               "--invocation", "manual", "--supersede-capture",
               "--reason", "partial paste; full reply recaptured",
               "--zero-findings")
    if r.returncode == 0:
        failures.append("--zero-findings was accepted against a reply carrying "
                        "a finding")
    elif not (cyc / "codex-output-raw.md").is_file():
        failures.append("a refused supersession deleted codex-output-raw.md; "
                        "the cycle was destroyed by a command that reported "
                        "nothing written")
    elif not (cyc / "findings.json").is_file():
        failures.append("a refused supersession deleted findings.json")
    elif (cyc / "codex-output-raw.md").read_bytes() != before_raw:
        failures.append("a refused supersession altered the authoritative raw "
                        "capture")
    elif (cyc / "findings.json").read_bytes() != before_fj:
        failures.append("a refused supersession altered findings.json")
    else:
        after_log = json.loads((cyc / "capture-log.json").read_text(encoding="utf-8"))
        if after_log.get("authoritative") != before_log.get("authoritative"):
            failures.append("a refused supersession moved the designation")
        else:
            print("  [ok] a refused supersession leaves the authoritative "
                  "capture, findings and designation intact")

    # The refusal above created an attempt directory. The log must know about
    # it, or next_attempt (which counts directories) and the log disagree, and
    # the next designation points past the end of the recorded attempts. Found
    # only because the B02-F04 control happened to run a refusal before a
    # success; nothing was asserting it.
    _log = json.loads((cyc / "capture-log.json").read_text(encoding="utf-8"))
    _dirs = sorted((cyc / "captures").glob("attempt-*"))
    if len(_log["attempts"]) != len(_dirs):
        failures.append(
            f"the capture log records {len(_log['attempts'])} attempt(s) but "
            f"{len(_dirs)} exist on disk. A refused attempt is preserved and "
            "must be recorded, or the count of attempts is understated.")
    else:
        print(f"  [ok] a refused attempt is recorded in the log, not only on "
              f"disk ({len(_dirs)} attempts)")

    r = runner(t16, "record", "--cycle", str(cyc), "--output", "other.md",
               "--invocation", "manual", "--supersede-capture",
               "--reason", "partial paste; full reply recaptured")
    if r.returncode != 0:
        failures.append(f"an authorized supersession was refused:\n{r.stdout}{r.stderr}")
    else:
        log = json.loads((cyc / "capture-log.json").read_text(encoding="utf-8"))
        # Every attempt so far, counted rather than hardcoded. A refused
        # supersession still preserves its attempt — that is issue 6's whole
        # point — so inserting the B02-F04 control above consumes a number, and
        # a literal 3 here made this control fail for a reason that had nothing
        # to do with what it tests.
        n_attempts = len(log["attempts"])
        kept = all((cyc / "captures" / f"attempt-{i:02d}" / "raw.md").is_file()
                   for i in range(1, n_attempts + 1))
        inv = (log.get("invalidated") or [{}])[-1]
        if log["authoritative"] != n_attempts:
            failures.append(
                f"supersession did not move the designation to the new attempt: "
                f"authoritative={log['authoritative']}, attempts={n_attempts}")
        elif not kept:
            failures.append("supersession removed a prior attempt; both must be "
                            "preserved")
        elif not log.get("invalidated"):
            failures.append("supersession did not record the invalidation")
        elif inv.get("authorized_by") != "Alex Zamurko":
            failures.append("the invalidation record does not carry the "
                            "authority, so deleting the approval file would "
                            f"leave an unattributed supersession: {inv}")
        else:
            print("  [ok] an authorized supersession moves the designation, "
                  "keeps every attempt and records who authorized it")

    # The staged files are an implementation detail of the swap and must never
    # outlive it. A leftover .staged file is a half-written record sitting in a
    # cycle directory, which is the kind of thing a later reader treats as
    # evidence.
    debris = sorted(p.name for p in cyc.glob("*.staged")) + \
             sorted(p.name for p in cyc.glob(".*.staged"))
    if debris:
        failures.append(f"staging files survived in the cycle directory: "
                        f"{debris}")
    else:
        print("  [ok] no staging files are left behind in the cycle")

    # ---- B02-F01 and B02-F02: the parser reads what the prompt asks for ----
    # Two defects found by cycle 02, in the module that exists to stop the
    # prompt, the parser and the ledger from disagreeing.
    print()
    print("recurrence blocks, and blocks the strict parser cannot see")

    import importlib.util as _iu
    _sp = _iu.spec_from_file_location("_ff", SRC / "findings_format.py")
    _ff = _iu.module_from_spec(_sp); _sp.loader.exec_module(_ff)

    def parses(label: str, body: str, want_ids, want_kinds=None) -> None:
        got, probs = _ff.extract(body)
        if probs:
            failures.append(f"{label}: unexpected problems {probs}")
            return
        if [g["id"] for g in got] != list(want_ids):
            failures.append(f"{label}: got {[g['id'] for g in got]}, "
                            f"wanted {list(want_ids)}")
            return
        if want_kinds and [g.get("kind") for g in got] != list(want_kinds):
            failures.append(f"{label}: kinds {[g.get('kind') for g in got]}")
            return
        print(f"  [ok] parsed: {label}")

    def refuses(label: str, body: str, needle: str) -> None:
        got, probs = _ff.extract(body)
        if not probs:
            failures.append(f"{label}: parsed cleanly, expected a problem "
                            f"(got {[g['id'] for g in got]})")
        elif not any(needle.lower() in p.lower() for p in probs):
            failures.append(f"{label}: wrong problem\n  wanted {needle!r}\n"
                            f"  got {probs}")
        else:
            print(f"  [ok] refused: {label}")

    NEW = "Finding ID: B02-F01\nClass: UNTESTED RULE\nEvidence: x\n"
    REC = ("Finding ID: B01-F11\nStatus: REPAIR NOT DEMONSTRATED\n"
           "Evidence: x\nFinding: y\nRequired correction: z\n")

    parses("a new finding", NEW, ["B02-F01"], ["finding"])
    parses("a recurrence with no Class line", REC, ["B01-F11"], ["recurrence"])
    parses("a review mixing both forms", NEW + "\n" + REC,
           ["B02-F01", "B01-F11"], ["finding", "recurrence"])

    refuses("a block carrying both Class and Status",
            "Finding ID: B02-F01\nClass: UNTESTED RULE\n"
            "Status: REPAIR NOT DEMONSTRATED\nEvidence: x\n",
            "either a new finding")
    refuses("a block with neither Class nor Status",
            "Finding ID: B02-F01\nEvidence: x\n", "neither a Class")
    refuses("an unrecognised Status",
            "Finding ID: B01-F11\nStatus: LOOKS FINE TO ME\nEvidence: x\n",
            "not recognised")

    # B02-F01 proper. Codex's reproduction: one canonical block, one indented by
    # a single space. Before the repair this returned one identifier and an
    # empty problems list, because the signal net only ran when nothing parsed.
    refuses("a second block indented by one space",
            NEW + "\n Finding ID: B02-F02\nClass: UNTESTED RULE\nEvidence: y\n",
            "apparent finding block")
    # Caught by the SIGNALS net rather than by the loose-header comparison: when
    # the indented block is the only one, nothing parses at all. Verified by
    # mutation — with the loose comparison disabled this control still passes,
    # so it is evidence about the signal net and is labelled as such. Left in
    # because two independent mechanisms covering the case is worth recording,
    # and a control named for the wrong mechanism is worth not having.
    refuses("a review whose only block is indented, caught by the signal net",
            " Finding ID: B02-F01\nClass: UNTESTED RULE\nEvidence: x\n",
            "signals that one is present")

    # And the class really does come from the ledger, not from the review.
    tf = make_repo(); made.append(tf)
    do_init(tf); do_freeze(tf)
    sh(sys.executable, str(tf / "scripts" / "ledger.py"), "raise",
       "--review", "runs/T-001/plan-review", "--cycle", "1", "--id", "C01-F01",
       "--class", "WRONG OWNERSHIP", cwd=tf)
    write_lf(tf / "rec.md", with_target(tf, "Finding ID: C01-F01\n"
                                            "Status: REPAIR NOT DEMONSTRATED\n"
                                            "Evidence: x\nFinding: y\n"
                                            "Required correction: z\n"))
    r = runner(tf, "record", "--cycle", "runs/T-001/plan-review/cycle-01",
               "--output", "rec.md", "--invocation", "manual")
    if r.returncode != 0:
        failures.append(f"a recurrence was refused:\n{r.stdout}{r.stderr}")
    else:
        fj = json.loads((tf / "runs/T-001/plan-review/cycle-01/findings.json")
                        .read_text(encoding="utf-8"))
        rec0 = fj["findings"][0]
        if rec0.get("class") != "WRONG OWNERSHIP":
            failures.append(f"the recurrence class was not resolved from the "
                            f"ledger: {rec0}")
        elif rec0.get("kind") != "recurrence":
            failures.append(f"the recurrence was not marked as one: {rec0}")
        else:
            print("  [ok] a recurrence takes its class from the ledger, not the "
                  "review")

    tu = make_repo(); made.append(tu)
    do_init(tu); do_freeze(tu)
    write_lf(tu / "rec.md", with_target(tu, "Finding ID: C01-F09\n"
                                            "Status: REPAIR NOT DEMONSTRATED\n"
                                            "Evidence: x\n"))
    r = runner(tu, "record", "--cycle", "runs/T-001/plan-review/cycle-01",
               "--output", "rec.md", "--invocation", "manual")
    if r.returncode == 0:
        failures.append("a recurrence was recorded for an identifier the ledger "
                        "has never seen")
    elif "never" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the unknown identifier\n"
                        f"{r.stdout}{r.stderr}")
    else:
        print("  [ok] refused: a recurrence for an identifier never raised")

    # ---- run-pin and review-target separation, 10 September ----
    # "No review process may require an artifact to remain byte-invariant for
    # the duration of a run while simultaneously requiring that same artifact
    # version to change in order to resolve review findings."
    #
    # BOOTSTRAP-001 required exactly that and deadlocked between cycles 01 and
    # 02. Nothing compared the pin set against the target list, so the
    # contradiction was only discoverable by hitting it.
    print()
    print("run pins and review targets are disjoint")

    tp = make_repo(); made.append(tp)
    do_init(tp)
    # Freeze a cycle whose review target IS the run's pinned spec.
    r = runner(tp, "freeze", "--run", "T-001", "--type", "plan",
               "--prompt", "specs/prompt.md", "--file", "specs/spec.md")
    if r.returncode == 0:
        failures.append("a cycle was frozen with the run's pinned spec as its "
                        "own review target; the governing invariant is not "
                        "enforced")
    elif "exactly one role" not in (r.stdout + r.stderr):
        failures.append(f"freeze refused, but not for the separation rule\n"
                        f"{r.stdout}{r.stderr}")
    elif (tp / "runs/T-001/plan-review/cycle-01").exists():
        failures.append("freeze refused but left a cycle directory behind")
    else:
        print("  [ok] refused: an artifact that is both a run pin and a review "
              "target")

    # The ordinary case still works, or the check above is just breaking freeze.
    if do_freeze(tp).returncode != 0:
        failures.append("freeze of an ordinary cycle was refused by the "
                        "separation check")
    else:
        print("  [ok] a cycle whose target is not a pinned artifact still freezes")

    # ---- the amendment history ----
    def amend(root: Path, **over) -> None:
        rec = {
            "effective_cycle": 2,
            "reason": "the pinned spec is also a review target, which the "
                      "separation specification forbids",
            "affected_artifacts": ["specs/spec.md"],
            "prior_pin_set": ["specs/protocol.md", "specs/spec.md"],
            "new_pin_set": ["specs/protocol.md"],
            "authorized_by": "Alex Zamurko",
            "at": "2026-09-10T00:00:00Z",
        }
        rec.update(over)
        write_lf(root / "runs" / "T-001" / "pin-amendments.json", json.dumps({
            "schema": "run-pin-amendments/1", "amendments": [rec]}, indent=2) + "\n")

    def amend_refuses(label: str, needle: str, **over) -> None:
        # These refuse inside check_pins_still_hold, before the loop controller
        # is consulted, so cycle 01 does not need closing here. The control
        # asserts the amendment chain is rejected, and the message it matches on
        # says which rule rejected it.
        root = make_repo(); made.append(root)
        do_init(root); do_freeze(root)
        amend(root, **over)
        rr = do_freeze(root)
        if rr.returncode == 0:
            failures.append(f"{label}: accepted")
        elif needle.lower() not in (rr.stdout + rr.stderr).lower():
            failures.append(f"{label}: refused for the wrong reason\n"
                            f"  wanted {needle!r}\n"
                            f"  got {(rr.stderr + rr.stdout)[:300]}")
        else:
            print(f"  [ok] refused: {label}")

    amend_refuses("an amendment that starts from a pin set that never existed",
                  "does not follow the pin history",
                  prior_pin_set=["specs/protocol.md"])

    # ---- B02-F05: amendments are constrained by role ----
    # "The governing protocol cannot be removed; added pins must be validated."
    # The first version accepted any structurally valid edit, so an inconvenient
    # mandatory pin could simply be dropped and a new one declared without ever
    # being checked.
    amend_refuses("an amendment that removes the governing protocol",
                  "removes the governing protocol",
                  affected_artifacts=["specs/protocol.md"],
                  new_pin_set=["specs/spec.md"])
    amend_refuses("an amendment adding a pin with no hash",
                  "without binding them to their bytes",
                  affected_artifacts=["specs/extra.md"],
                  new_pin_set=["specs/protocol.md", "specs/spec.md",
                               "specs/extra.md"])
    amend_refuses("an amendment adding a pin with something other than a sha256",
                  "other than a sha256",
                  affected_artifacts=["specs/extra.md"],
                  new_pin_set=["specs/protocol.md", "specs/spec.md",
                               "specs/extra.md"],
                  added_pin_hashes={"specs/extra.md": "not-a-hash"})

    # An added pin, properly bound, must then actually be checked. Codex's
    # finding was that the pin check walked run.json's original entries only,
    # so a newly declared governing artifact was never hashed at all.
    tx = make_repo(); made.append(tx)
    do_init(tx); do_freeze(tx)
    write_lf(tx / "runs/T-001/plan-review/cycle-01/codex-output-raw.md", "x\n")
    write_lf(tx / "specs" / "extra.md", "an added governing artifact\n")
    extra_hash = hashlib.sha256(
        (tx / "specs" / "extra.md").read_bytes()).hexdigest()
    amend(tx, affected_artifacts=["specs/extra.md"],
          new_pin_set=["specs/protocol.md", "specs/spec.md", "specs/extra.md"],
          added_pin_hashes={"specs/extra.md": extra_hash})
    p_extra = tx / "specs" / "extra.md"
    p_extra.write_text(p_extra.read_text(encoding="utf-8") + "edited\n",
                       encoding="utf-8")
    r = do_freeze(tx)
    if r.returncode == 0:
        failures.append("an amendment-added governing artifact was edited and "
                        "the freeze accepted it; added pins are declared but "
                        "not checked")
    elif "governing artifact changed" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the added pin's drift\n"
                        f"{r.stdout}{r.stderr}")
    else:
        print("  [ok] refused: an artifact added by amendment is checked like "
              "any other governing pin")
    amend_refuses("an amendment with nobody's name on it", "missing",
                  authorized_by="")
    amend_refuses("an amendment whose reason is a placeholder", "at least",
                  reason="because")
    amend_refuses("an amendment whose declared artifacts are not what changed",
                  "do not match what it changes",
                  affected_artifacts=["specs/protocol.md"])

    # And the amendment actually releases the pin, or the whole exercise is a
    # record of a change that did not take effect.
    # Cycle 01 is closed through the real record path rather than by writing raw
    # output by hand. A hand-written cycle has no findings.json, and the loop
    # controller then refuses to say whether another cycle is permitted, so
    # freeze would be blocked by B01-F02's check and this control would report a
    # pin failure that never happened. The finding is also raised in the ledger,
    # because the controller refuses when a recorded finding is unaccounted for,
    # and one open finding is what makes the loop CONTINUE rather than converge.
    tr = make_repo(); made.append(tr)
    do_init(tr); do_freeze(tr)
    write_lf(tr / "reply.md", with_target(tr, GOOD))
    rec = runner(tr, "record", "--cycle", "runs/T-001/plan-review/cycle-01",
                 "--output", "reply.md", "--invocation", "manual")
    if rec.returncode != 0:
        failures.append(f"fixture: could not record cycle 01\n{rec.stdout}{rec.stderr}")
    rl = sh(sys.executable, str(tr / "scripts" / "ledger.py"), "raise",
            "--review", "runs/T-001/plan-review", "--cycle", "1",
            "--id", "C01-F01", "--class", "UNTESTED RULE", cwd=tr)
    if rl.returncode != 0:
        failures.append(f"fixture: could not raise the finding\n{rl.stdout}{rl.stderr}")
    spec_p = tr / "specs" / "spec.md"
    spec_p.write_text(spec_p.read_text(encoding="utf-8") + "\nrepaired\n",
                      encoding="utf-8")
    r = do_freeze(tr)
    if r.returncode == 0:
        failures.append("cycle 02 froze with the pinned spec edited and no "
                        "amendment recorded")
    elif "run pins no longer hold" not in (r.stdout + r.stderr):
        failures.append(f"refused, but not for the pin drift\n{r.stdout}{r.stderr}")
    else:
        print("  [ok] editing a pinned spec still blocks the next cycle")

    amend(tr)
    r = do_freeze(tr)
    if r.returncode != 0:
        failures.append("the recorded amendment did not release the pin, so the "
                        f"loop is still deadlocked\n{r.stdout}{r.stderr}")
    elif not (tr / "runs/T-001/plan-review/cycle-02").is_dir():
        failures.append("freeze reported success but opened no cycle 02")
    else:
        print("  [ok] a recorded amendment releases the pin from cycle 02 onward")

    # ---- B02-F06: an amendment cannot rewrite a completed cycle ----
    # Codex: "An amendment appended after review can retroactively change what
    # governed an already completed cycle." The old forward-only control only
    # showed that effective_cycle=2 gave different answers for cycles 1 and 2.
    # It never appended a backdated amendment after a cycle existed.
    tb = make_repo(); made.append(tb)
    do_init(tb); do_freeze(tb)
    tgt1 = json.loads((tb / "runs/T-001/plan-review/cycle-01/target.json")
                      .read_text(encoding="utf-8"))
    if "governing_pins" not in tgt1:
        failures.append("the frozen cycle does not record what governed it, so "
                        "nothing can be checked against it")
    else:
        print(f"  [ok] a frozen cycle records its governing pin set "
              f"({len(tgt1['governing_pins'])} artifacts)")
        write_lf(tb / "runs/T-001/plan-review/cycle-01/codex-output-raw.md", "x\n")
        # Effective at cycle 1, which already exists and recorded both pins.
        amend(tb, effective_cycle=1)
        r = do_freeze(tb)
        if r.returncode == 0:
            failures.append("a backdated amendment was accepted after the cycle "
                            "it affects had already been frozen")
        elif "already happened" not in (r.stdout + r.stderr):
            failures.append(f"refused, but not for the retroactive change\n"
                            f"{r.stdout}{r.stderr}")
        else:
            print("  [ok] refused: an amendment that would change what a "
                  "completed cycle ran under")

    # Cycle 01 must still be checked against what it was conducted under. An
    # amendment that reached backwards would rewrite the conditions of a review
    # that already happened.
    import importlib.util as _ilu
    _s = _ilu.spec_from_file_location("_rp", tr / "scripts" / "run_pins.py")
    _m = _ilu.module_from_spec(_s); _s.loader.exec_module(_m)
    run_obj = json.loads((tr / "runs/T-001/run.json").read_text(encoding="utf-8"))
    items = _m.load_amendments(tr / "runs" / "T-001")
    at1 = _m.pins_for_cycle(run_obj, items, 1)
    at2 = _m.pins_for_cycle(run_obj, items, 2)
    if "specs/spec.md" not in at1:
        failures.append("the amendment reached back into cycle 01, rewriting the "
                        f"conditions of a review that already happened: {at1}")
    elif "specs/spec.md" in at2:
        failures.append(f"the amendment did not take effect at cycle 02: {at2}")
    else:
        print("  [ok] the amendment applies forward only; cycle 01 keeps its own "
              "pins")

    # ---- B01-F08: the gate must hold at freeze, not only at init ----
    # A run can sit for days between init and its first cycle, and every cycle is
    # where the tooling is actually relied upon. Checking only at init let a
    # component change in between and a cycle freeze against tooling whose
    # approval no longer covered it.
    t4 = make_repo(); made.append(t4)
    if approve_bootstrap(t4).returncode != 0 or real_init(t4).returncode != 0:
        failures.append("could not reach an approved real run for the freeze-time "
                        "bootstrap control")
    else:
        vc = t4 / "scripts" / "validate_cycle.py"
        vc.write_text(vc.read_text(encoding="utf-8") + "\n# edited after init\n",
                      encoding="utf-8")
        r = runner(t4, "freeze", "--run", "A1E-001", "--type", "plan",
                   "--prompt", "specs/prompt.md", "--file", "plan/01-PLAN.md")
        blob = (r.stdout + r.stderr).lower()
        if r.returncode == 0:
            failures.append("a cycle froze against tooling whose bootstrap "
                            "approval no longer covers it; the gate was checked "
                            "at init and never again")
        elif "no longer holds" not in blob:
            failures.append("freeze refused after the component changed, but not "
                            f"on the bootstrap gate:\n  {blob.strip()[:220]}")
        else:
            print("  [ok] refused: freezing a cycle after a covered component changed")

    # An exempt run must stay exempt at freeze too, or development evidence
    # becomes impossible to produce the moment any component is edited.
    t5 = make_repo(); made.append(t5)
    do_init(t5)
    vc = t5 / "scripts" / "validate_cycle.py"
    vc.write_text(vc.read_text(encoding="utf-8") + "\n# edited\n", encoding="utf-8")
    if do_freeze(t5).returncode != 0:
        failures.append("an exempt run was blocked by the bootstrap gate at "
                        "freeze; exempt means exempt at every step or the flag "
                        "does not do what it says")
    else:
        print("  [ok] an exempt run still freezes after a component changes")

    # And the exempt path must label itself, or it is a silent bypass.
    t3 = make_repo(); made.append(t3)
    do_init(t3)
    exempt = json.loads((t3 / "runs" / "T-001" / "run.json").read_text(encoding="utf-8"))
    if "NOT_A_PROTOCOL_CYCLE" not in exempt.get("bootstrap_review", ""):
        failures.append("--bootstrap-exempt does not label the run as development "
                        "evidence, so an exempt run and a real one are "
                        "indistinguishable in the record")
    else:
        print("  [ok] --bootstrap-exempt labels the run NOT_A_PROTOCOL_CYCLE")

    # ---- B03-F01: nothing but a completed CONTINUE is permission ----
    # The check tested for controller exit code 2 and the four terminal
    # statuses, and permitted everything else. The replay added for B01-F11
    # raises UnknownEvent; loop_state caught only CannotCalculate; so an
    # unrecognised event exited 1 with a traceback and no LOOP_STATUS, and the
    # empty status fell straight through to permission. Codex reproduced it and
    # opened cycle-02 on a controller that had crashed.
    print()
    print("an undeterminable loop state is not permission (B03-F01)")

    tB = make_repo(); made.append(tB)
    do_init(tB); do_freeze(tB)
    write_lf(tB / "replyB.md",
             reply_for(tB, "Finding ID: C01-F01\nClass: UNTESTED RULE\n"
                           "Evidence: x\n"))
    _rb = runner(tB, "record", "--cycle", "runs/T-001/plan-review/cycle-01",
                 "--output", "replyB.md", "--invocation", "manual")
    if _rb.returncode != 0:
        failures.append(f"fixture: could not record cycle 01\n{_rb.stderr}{_rb.stdout}")
    _lb = sh(sys.executable, str(tB / "scripts" / "ledger.py"), "raise",
             "--review", "runs/T-001/plan-review", "--cycle", "1",
             "--id", "C01-F01", "--class", "UNTESTED RULE", cwd=tB)
    if _lb.returncode != 0:
        failures.append(f"fixture: could not raise the finding\n{_lb.stderr}{_lb.stdout}")

    cyc2 = tB / "runs" / "T-001" / "plan-review" / "cycle-02"

    # First that the next cycle opens at all. Without this every refusal below
    # could be refusing for some unrelated reason and the control would pass
    # while proving nothing, which is B01-F11's control exactly.
    if do_freeze(tB).returncode != 0:
        failures.append("fixture: cycle 02 would not open even with a healthy "
                        "ledger, so the refusals below establish nothing")
    else:
        shutil.rmtree(cyc2)
        print("  [ok] with a healthy ledger and CONTINUE, the next cycle opens")

    led = tB / "runs" / "T-001" / "plan-review" / "ledger.json"
    healthy = led.read_text(encoding="utf-8")

    # The reproduction: an event replay has no transition for.
    doc = json.loads(healthy)
    doc["findings"]["C01-F01"]["history"].append(
        {"at": "2026-09-14T00:00:00Z", "cycle": 1, "event": "BANANA",
         "note": "an event no version of replay knows", "state": "OPEN"})
    write_lf(led, json.dumps(doc, indent=2) + "\n")

    _rb2 = do_freeze(tB)
    if _rb2.returncode == 0:
        failures.append("an unrecognised ledger event stopped the controller "
                        "calculating and the runner opened the next cycle "
                        "anyway. B03-F01 unrepaired.")
        if cyc2.exists():
            shutil.rmtree(cyc2)
    elif cyc2.exists():
        failures.append("the freeze refused the unknown event but left a "
                        "cycle-02 directory behind")
    else:
        print("  [ok] refused: a controller that cannot calculate is not "
              "permission")

    write_lf(led, healthy)

    # The rest of the boundary, driven by stubbing the controller. The finding
    # is about what this runner accepts as an answer, so the cases worth testing
    # are the answers a controller can give, not only the one bug that exposed
    # them. Replacing a covered component is why the fixture is exempt.
    for label, body, expect in (
        ("a controller that exits non-zero saying nothing",
         "import sys\nsys.exit(3)\n", "exit 3"),
        # The decisive one. Every other non-zero case also trips the
        # missing-status check, so they would still refuse even if the exit code
        # were ignored, just for the wrong reason. This one says CONTINUE on its
        # way out: only a check that reads the exit code refuses it.
        ("a controller that says CONTINUE and then fails",
         "import sys\nprint('LOOP_STATUS: CONTINUE')\nsys.exit(1)\n", "exit 1"),
        ("a controller that exits 0 and reports no status",
         "print('all quiet')\n", "no LOOP_STATUS line"),
        ("a status this runner does not recognise",
         "print('LOOP_STATUS: BANANA')\n", "does not recognise"),
        ("two statuses in one run",
         "print('LOOP_STATUS: CONTINUE')\nprint('LOOP_STATUS: CONVERGED')\n",
         "2 LOOP_STATUS lines"),
    ):
        write_lf(tB / "scripts" / "loop_state.py", body)
        res = do_freeze(tB)
        out = res.stdout + res.stderr
        if res.returncode == 0:
            failures.append(f"the runner treated {label} as permission to open "
                            f"another cycle")
            if cyc2.exists():
                shutil.rmtree(cyc2)
        elif expect not in out:
            failures.append(f"refused {label}, but not for that reason:\n"
                            f"      {out.strip().splitlines()[:1]}")
        elif cyc2.exists():
            failures.append(f"refused {label} but left a cycle-02 directory")
        else:
            print(f"  [ok] refused: {label}")

    # ---- B03-F02: the controls are recorded beside the target, not in it ----
    # Cycle 03's prompt said "the suites are in the target". They were not, and
    # cycle 02 had already said so in prose that no Finding ID block carried, so
    # nothing transcribed it and the sentence survived into the next prompt.
    #
    # The repair records them instead of pretending they were reviewed. This
    # control exists to keep both halves true: the manifest is written and
    # accurate, and the suites still do not appear as target artifacts. A repair
    # that quietly added them to plan_files would satisfy the first half and
    # reintroduce the defect, so the second assertion is the load-bearing one.
    print()
    print("control suites are recorded, not targeted (B03-F02)")

    def _sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    tA = make_repo(); made.append(tA)
    # The fixture copies no suites, so plant two. Their names only have to match
    # the glob; their contents are never executed.
    write_lf(tA / "scripts" / "test_alpha.py", "# alpha\nprint('[ok] a')\n")
    write_lf(tA / "scripts" / "test_beta.py", "# beta\nprint('[ok] b')\n")
    sh("git", "add", "-A", cwd=tA)
    sh("git", "commit", "-qm", "suites", cwd=tA)
    do_init(tA); do_freeze(tA)

    cycA = tA / "runs/T-001/plan-review/cycle-01"
    amA = cycA / "auxiliary-evidence.json"
    tgtA = json.loads((cycA / "target.json").read_text(encoding="utf-8"))

    if not amA.is_file():
        failures.append("freeze wrote no auxiliary-evidence.json, so the "
                        "control versions behind the stated counts are not "
                        "recorded anywhere in the cycle")
    else:
        manA = json.loads(amA.read_text(encoding="utf-8"))
        listed = {s["path"]: s["sha256"] for s in manA["suites"]}
        want = {f"scripts/test_{n}.py": _sha(tA / "scripts" / f"test_{n}.py")
                for n in ("alpha", "beta")}
        if listed != want:
            failures.append(f"the manifest does not record the suites as they "
                            f"stood at freeze:\n    listed {listed}\n"
                            f"    actual {want}")
        else:
            print(f"  [ok] the manifest records every suite at freeze "
                  f"({len(listed)} of them)")

        if tgtA.get("auxiliary_evidence_sha256") != _sha(amA):
            failures.append("target.json does not record the manifest's digest, "
                            "so a later change to it would leave nothing to "
                            "compare against")
        else:
            print("  [ok] target.json records the manifest digest, and "
                  "target.sha256 covers target.json")

        # The whole point. Recording must not become membership.
        targeted = {r["path"] for r in tgtA.get("plan_files", [])}
        if targeted & set(listed):
            failures.append(
                "a control suite appears in plan_files. Recording the suites "
                "must not put them in the target: the gate refuses a target "
                "carrying artifacts outside its covered set, and the claim "
                "B03-F02 was raised about would be true again.")
        else:
            print("  [ok] no control suite appears in the review target")

        # The record is of freeze-time bytes. Later edits are ordinary work and
        # must not rewrite what the cycle says it measured.
        write_lf(tA / "scripts" / "test_alpha.py", "# alpha changed\n")
        after = json.loads(amA.read_text(encoding="utf-8"))
        if after != manA:
            failures.append("editing a suite after freeze changed the frozen "
                            "manifest")
        elif listed.get("scripts/test_alpha.py") == _sha(
                tA / "scripts" / "test_alpha.py"):
            failures.append("the manifest still matches the edited suite, so it "
                            "is not recording freeze-time bytes")
        else:
            print("  [ok] a later suite edit leaves the frozen record unchanged")

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
