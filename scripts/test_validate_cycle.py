#!/usr/bin/env python3
"""Negative controls for the MC-2 conformance gate.

Every one of the fifteen checks is demonstrated failing on a fixture built to
break exactly that check, and clean plan and implementation cycles are
demonstrated passing.

A gate whose checks are never shown to fail is the defect class the v1.0
gate-hardening milestone found thirteen times: a check that cannot come back
false reports success while testing nothing.

Checks 11 to 15 apply to implementation review only. That creates a second way
to build the same defect: report them PASS on a plan cycle they never examined.
So this suite also asserts they come back N/A there, and that N/A is distinct
from PASS in the output.

    python scripts/test_validate_cycle.py

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

sys.path.insert(0, str(SRC))
# B01-F07: the control derives the expected spec digest from the same function
# the gate and the runner use. Computing it here by hand would make this suite a
# third implementation of the format, and three copies of a rule disagree even
# more readily than two.
import run_pins  # noqa: E402


def write_lf(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)


def make_repo() -> tuple[Path, str, str]:
    """A throwaway repo so REPO resolves to the fixture. Returns (root, commit, tree)."""
    tmp = Path(tempfile.mkdtemp(prefix="mc2-")).resolve()
    (tmp / "scripts").mkdir()
    # run_pins comes too: the gate imports it for the shared spec-digest format
    # (B01-F07). Without it validate_cycle dies at import, emits no check marks,
    # and every control in this suite reports the wrong thing. test_ledger.py
    # was broken in exactly this way on 14 September by the same kind of change.
    for _n in ("validate_cycle.py", "run_pins.py"):
        shutil.copy2(SRC / _n, tmp / "scripts" / _n)
    write_lf(tmp / "plan.md", "# plan\n\nbody\n")
    write_lf(tmp / "candidate.diff", "--- a\n+++ b\n@@ -1 +1 @@\n-x\n+y\n")
    write_lf(tmp / "tests.txt", "ok 1 - everything\n")
    sh("git", "init", "-q", cwd=tmp)
    sh("git", "config", "user.email", "t@t", cwd=tmp)
    sh("git", "config", "user.name", "t", cwd=tmp)
    sh("git", "add", "-A", cwd=tmp)
    sh("git", "commit", "-qm", "fixture", cwd=tmp)
    commit = sh("git", "rev-parse", "HEAD", cwd=tmp).stdout.strip()
    tree = sh("git", "rev-parse", "HEAD^{tree}", cwd=tmp).stdout.strip()
    return tmp, commit, tree


def build(root: Path, commit: str, tree: str, kind: str = "plan",
          mutate=None, sibling: dict | None = None, approval: bool = True) -> Path:
    review = root / "runs" / "T-001" / f"{kind}-review"
    cycle = review / "cycle-01"
    cycle.mkdir(parents=True)

    # B01-F07, the half cycle 04 found still open. Check 9 used to compare the
    # target's governing digests with each other, so these fixtures needed no
    # run at all. It now replays the run's pin history and requires the recorded
    # set to be the one that history produces, which means the fixture has to
    # own a run for its claims to be about.
    #
    # The pins here are the ones _governed() writes into the target. A fixture
    # whose run disagreed with its own targets would make every control below
    # fail for that reason instead of the one it names.
    write_lf(root / "runs" / "T-001" / "run.json", json.dumps({
        "run_id": "T-001",
        "bootstrap_review": "APPROVED",
        "mc1_enforcement": "CONVENTION_ONLY",
        "protocol": {"path": "specs/protocol.md", "sha256": "a" * 64},
        "spec_files": [{"path": "specs/spec.md", "sha256": "b" * 64}],
    }, indent=2) + "\n")

    target = {
        "review_type": kind,
        "run_id": "T-001",
        "cycle": 1,
        "protocol_commit": commit,
        "protocol_sha256": "2" * 64,
        "spec_sha256": "0" * 64,
        "frozen_at": "2026-09-08T13:40:00Z",
    }
    plan_hash = sha256_file(root / "plan.md")
    if kind == "plan":
        target["plan_files"] = [{"path": "plan.md", "sha256": plan_hash}]
        # Preserved copy: check 9 validates the snapshot, not the live tree,
        # so a cycle survives the repairs its review asked for.
        snap = cycle / "artifacts" / "plan.md"
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_bytes((root / "plan.md").read_bytes())
    else:
        target.update({
            "candidate_commit": commit,
            "candidate_tree_hash": tree,
            "approved_plan_hash": plan_hash,
            "diff_path": "candidate.diff",
            "diff_hash": sha256_file(root / "candidate.diff"),
            "test_result_path": "tests.txt",
            "test_result_hash": sha256_file(root / "tests.txt"),
        })
        if approval:
            write_lf(root / "runs" / "T-001" / "plan-approval" / "approval.json",
                     json.dumps({"decision": "APPROVE",
                                 # B01-F06: name the artifact, or check 13 can
                                 # only compare a hash with a copy of itself.
                                 "approved_plan_path": "plan.md",
                                 "approved_plan_hash": plan_hash}, indent=2))

    if mutate:
        target = mutate(target, cycle, root) or target

    write_lf(cycle / "target.json", json.dumps(target, indent=2))
    digest = sha256_file(cycle / "target.json")
    write_lf(cycle / "target.sha256", digest + "\n")
    write_lf(cycle / "codex-input.md", f"Review target {digest}\n\n(contents)\n")
    write_lf(cycle / "codex-output-raw.md", "C01-F01 | UNTESTED RULE | R-B7 | ...\n")

    if sibling is not None:
        sib = review / "cycle-02"
        sib.mkdir()
        write_lf(sib / "target.json", json.dumps(sibling, indent=2))
    return cycle


def run(root: Path, cycle: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(root / "scripts" / "validate_cycle.py"),
                        str(cycle)], capture_output=True, text=True)
    return r.returncode, r.stdout


def marks(output: str) -> dict[int, str]:
    out = {}
    for line in output.splitlines():
        s = line.strip()
        if s and s[0].isdigit() and "[" in s and "]" in s:
            try:
                n = int(s.split(".", 1)[0])
            except ValueError:
                continue
            out[n] = s[s.index("[") + 1:s.index("]")].strip()
    return out


def main() -> int:
    failures: list[str] = []
    made: list[Path] = []

    def fresh():
        root, commit, tree = make_repo()
        made.append(root)
        return root, commit, tree

    def expect_fail(label: str, check: int, kind: str, mutate=None,
                    also: tuple[int, ...] = (), **kw) -> None:
        """One mutation, one red check.

        Fixture-validity audit, Alex Zamurko 16 September: "each negative
        control should first establish that its fixture satisfies all
        prerequisites except the single condition it intends to violate."

        The builder and the two clean-cycle controls above already give half of
        that: every fixture here comes from the same builder, which is shown to
        pass unmutated. The half that was missing is the other direction. This
        asserted the intended check went red and never asked what else did, so a
        mutation that broke four checks satisfied a control about one of them,
        and the control would have stayed green if its own check had stopped
        being reachable.

        `also` names checks a mutation legitimately takes with it — a malformed
        target.json cannot be read by anything downstream of it — so that the
        cascade is declared per control rather than tolerated everywhere.
        """
        root, commit, tree = fresh()
        cycle = build(root, commit, tree, kind, mutate=mutate, **kw)
        rc, out = run(root, cycle)
        if rc == 0:
            failures.append(f"{label}: expected FAIL, gate passed")
            return
        got = marks(out)
        if got.get(check) != "FAIL":
            failures.append(f"{label}: expected check {check} to FAIL, "
                            f"it was {got.get(check)!r}")
            return
        collateral = sorted(n for n, v in got.items()
                            if v == "FAIL" and n != check and n not in also)
        if collateral:
            failures.append(
                f"{label}: check {check} failed as intended, and so did "
                f"{collateral}. The fixture violates more than the one "
                f"condition this control is about, so it does not show that "
                f"check {check} is what caught it. Declare the cascade with "
                f"also=(...) if it is genuine.")
            return
        print(f"  [ok] check {check:>2} fails on: {label}")

    # ---- B01-F07: the governing digests are checked, not merely present ----
    # Check 7 confirmed protocol_sha256 and spec_sha256 EXIST and stopped there.
    # Codex set both to the literal "not-a-hash", recomputed target.sha256, and
    # MC-2 returned PASS. The protocol's check 9 is "recorded hashes match the
    # referenced artifacts", so that is where this belongs; it needed no new
    # check and no change to the schema.
    def _governed(protocol_hash: str, spec_hash: str | None = None,
                  drop_hashes: bool = False):
        """A target carrying a governing pin set, as freeze writes since B02-F06."""
        pins = {"specs/protocol.md": "a" * 64, "specs/spec.md": "b" * 64}

        def _m(target, cycle, root):
            target["governing_pins"] = sorted(pins)
            if not drop_hashes:
                target["governing_pin_hashes"] = pins
            target["protocol_sha256"] = protocol_hash
            target["spec_sha256"] = (
                spec_hash if spec_hash is not None
                else run_pins.spec_digest([{"path": "specs/spec.md",
                                            "sha256": "b" * 64}]))
            return target
        return _m

    # What these controls do NOT cover, found by probing rather than assumed:
    # changing the digest FORMAT in run_pins leaves every control here green,
    # because they ask that same function for the expected value. They test that
    # the gate and the writer share one definition, not that the definition is
    # the documented one. The control that pins the format is in
    # test_run_review.py, "spec_sha256 is not reproducible from its documented
    # definition", which recomputes it by hand. Both roles are needed; neither
    # substitutes for the other.
    #
    # The baseline first. Without it every refusal below could be refusing for
    # some unrelated reason and the controls would look green while proving
    # nothing, which is what cycle 03 caught in B01-F11's control.
    root, commit, tree = fresh()
    rc, out = run(root, build(root, commit, tree, "plan",
                              mutate=_governed("a" * 64)))
    if rc != 0 or marks(out).get(9) != "PASS":
        failures.append(f"a cycle whose digests DO describe its governing set "
                        f"was refused, so the refusals below establish "
                        f"nothing:\n{out}")
    else:
        print("  [ok] check  9 passes on digests that match the governing set")

    expect_fail("a protocol digest that is not a digest", 9, "plan",
                mutate=_governed("not-a-hash"))
    expect_fail("a protocol digest that is well formed but not this cycle's",
                9, "plan", mutate=_governed("c" * 64))
    expect_fail("a spec digest that does not describe the governing set",
                9, "plan", mutate=_governed("a" * 64, spec_hash="d" * 64))
    expect_fail("governing pins declared with no hashes to check them against",
                9, "plan", mutate=_governed("a" * 64, drop_hashes=True))

    # The two cycle 04 asked for. Codex: "The named negative controls change one
    # assertion while retaining the other, leaving consistent false assertions
    # untested." Every control above keeps a real pin set and breaks one field.
    # Neither of these does. They make the whole governing set false and
    # internally agreed, which is the target Codex built and the gate passed.
    def _fabricated(target, cycle, root):
        """Codex's reproduction: an invented set that agrees with itself."""
        target["governing_pins"] = ["missing-protocol.md"]
        target["governing_pin_hashes"] = {"missing-protocol.md": "not-a-hash"}
        target["protocol_sha256"] = "not-a-hash"
        target["spec_sha256"] = run_pins.spec_digest([])
        return target

    expect_fail("an invented governing set whose every field agrees with itself",
                9, "plan", mutate=_fabricated)

    # And the same shape with well formed digests, so the syntax check cannot be
    # what catches it. Only replaying the run's history can: these are real
    # looking hashes for a pin set this run never had. Without this control the
    # repair could be nothing but the hex check and still look complete.
    def _foreign(target, cycle, root):
        target["governing_pins"] = ["specs/elsewhere.md"]
        target["governing_pin_hashes"] = {"specs/elsewhere.md": "e" * 64}
        target["protocol_sha256"] = "e" * 64
        target["spec_sha256"] = run_pins.spec_digest([])
        return target

    expect_fail("a well formed governing set the run's history never produced",
                9, "plan", mutate=_foreign)

    # The one that isolates the history replay. Both controls above are also
    # caught by the syntax check or by the protocol-identity check, so neither
    # shows that replaying run.json does any work. This target declares the run's
    # real protocol with its real digest, well formed hashes throughout, and a
    # spec_sha256 correctly derived over its own contents. It is consistent in
    # every way the old check could see. The only thing wrong with it is that the
    # run never pinned specs/invented.md, which nothing but the run's own history
    # can say.
    def _extra_pin(target, cycle, root):
        pins = {"specs/protocol.md": "a" * 64,
                "specs/spec.md": "b" * 64,
                "specs/invented.md": "c" * 64}
        target["governing_pins"] = sorted(pins)
        target["governing_pin_hashes"] = pins
        target["protocol_sha256"] = "a" * 64
        target["spec_sha256"] = run_pins.spec_digest(
            [{"path": "specs/spec.md", "sha256": "b" * 64},
             {"path": "specs/invented.md", "sha256": "c" * 64}])
        return target

    expect_fail("a governing set carrying a spec the run never pinned, "
                "self-consistent in every other way", 9, "plan",
                mutate=_extra_pin)

    # C01-F04. Every control above breaks something in the TARGET. This one
    # leaves the target entirely correct and breaks the history it was derived
    # from, which nothing in the target can show.
    #
    # The gate called `load_amendments` and `pin_hashes_for_cycle` and neither
    # `validate_chain` nor `check_frozen_assignments`. The freeze path called
    # all four. So the runner could reject a governing history while the gate
    # accepted a completed cycle conducted against it.
    #
    # Codex's amendment: `prior_pin_set` names `never-pinned.md`, a set this
    # run never held. Direct chain validation refuses it with "amendment 0
    # does not follow the pin history". The replay nevertheless produces the
    # set actually recorded, so every comparison check 9 was able to make
    # agreed, and MC-2 exited 0 with checks 1 to 10 passing.
    #
    # The target has to carry a governing set for this to reach check 9 at all.
    # Without one it is a cycle frozen before `governing_pin_hashes` existed,
    # the governing comparison is skipped, and the control passes while testing
    # nothing. That is how the first version of this control reported "gate
    # passed": it was right, and it was right about a fixture that never got
    # near the code under test.
    def _invalid_chain(target, cycle, root):
        _governed("a" * 64)(target, cycle, root)
        run_dir = root / "runs" / "T-001"
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        final = list(run_pins.initial_pin_set(run))
        write_lf(run_dir / "pin-amendments.json", json.dumps({
            "schema": run_pins.SCHEMA,
            "amendments": [{
                "reason": "fixture: a prior set this run never held, replaying "
                          "to exactly the set the target already records",
                "affected_artifacts": final,
                "prior_pin_set": ["never-pinned.md"],
                "new_pin_set": final,
                "effective_cycle": 1,
                "authorized_by": "review fixture",
                "at": "2026-09-26T00:00:00Z"}]}, indent=2) + "\n")
        return target

    expect_fail("an amendment history the runner rejects, replayed by the gate "
                "without checking it", 9, "plan", mutate=_invalid_chain)

    # And the historical case, which must NOT fail. Cycles 01 and 02 of
    # BOOTSTRAP-001 were frozen before governing_pin_hashes existed. Failing
    # them now would invalidate two completed cycles and strip authority from
    # every event recorded in them, which is the retroactive invalidation Alex
    # Zamurko ruled out on 10 September arriving through a check instead of an
    # amendment.
    root, commit, tree = fresh()
    rc, out = run(root, build(root, commit, tree, "plan"))
    if rc != 0 or marks(out).get(9) != "PASS":
        failures.append(
            "a cycle frozen before governing_pin_hashes existed was refused. "
            f"That invalidates completed history through a new check:\n{out}")
    else:
        print("  [ok] check  9 does not invalidate cycles older than the field")

    # ---- clean fixtures ----
    root, commit, tree = fresh()
    rc, out = run(root, build(root, commit, tree, "plan"))
    m = marks(out)
    if rc != 0:
        failures.append(f"clean plan cycle did not pass:\n{out}")
    else:
        print("  [ok] clean plan cycle passes")
        na = [n for n in range(11, 16) if m.get(n) != "N/A"]
        if na:
            failures.append(f"checks {na} should be N/A on a plan cycle, "
                            f"got {[m.get(n) for n in na]}. Reporting PASS for a "
                            f"check that was never evaluated is the defect this "
                            f"gate exists to catch.")
        else:
            print("  [ok] checks 11-15 report N/A on a plan cycle, not PASS")

    root, commit, tree = fresh()
    rc, out = run(root, build(root, commit, tree, "implementation"))
    if rc != 0:
        failures.append(f"clean implementation cycle did not pass:\n{out}")
    else:
        m = marks(out)
        evaluated = [n for n in range(11, 16) if m.get(n) == "PASS"]
        if len(evaluated) != 5:
            failures.append(f"implementation cycle should evaluate 11-15, got {m}")
        else:
            print("  [ok] clean implementation cycle passes all fifteen")

    # ---- checks 1-10 ----
    # These four mutate the cycle AFTER build(), because build() writes the
    # required files last and a mutate hook would be overwritten by it.
    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    (cyc / "codex-output-raw.md").unlink()
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(4) != "FAIL":
        failures.append("check 4 did not fail on a missing required file")
    else:
        print("  [ok] check  4 fails on: missing required file")

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "codex-input.md", "")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(5) != "FAIL":
        failures.append("check 5 did not fail on an empty required file")
    else:
        print("  [ok] check  5 fails on: empty required file")

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "target.sha256", "a" * 64 + "\n")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(6) != "FAIL":
        failures.append("check 6 did not fail on a wrong target.sha256")
    else:
        print("  [ok] check  6 fails on: target.sha256 does not match target")

    expect_fail("duplicate cycle identifier", 7, "plan",
                sibling={"review_type": "plan", "run_id": "T-001", "cycle": 1})
    expect_fail("referenced commit does not resolve", 8, "plan",
                mutate=lambda t, c, r: {**t, "protocol_commit": "deadbeef" * 5})
    expect_fail("declared artifact hash is wrong", 9, "plan",
                mutate=lambda t, c, r: {**t, "plan_files": [
                    {"path": "plan.md", "sha256": "b" * 64}]})
    expect_fail("review_type outside the closed set", 9, "plan",
                mutate=lambda t, c, r: {**t, "review_type": "other"})

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "codex-input.md", "Review the plan.\n")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(10) != "FAIL":
        failures.append("check 10 did not fail when the input lacks the target hash")
    else:
        print("  [ok] check 10 fails on: codex-input.md does not carry the target hash")

    root, commit, tree = fresh()
    cyc = build(root, commit, tree, "plan")
    write_lf(cyc / "target.json", "{ not json")
    rc, out = run(root, cyc)
    if rc == 0 or marks(out).get(7) != "FAIL":
        failures.append("check 7 did not fail on unparseable target.json")
    else:
        print("  [ok] check  7 fails on: target.json is not valid JSON")

    # ---- checks 11-15, §10.2 ----
    # An unresolvable candidate commit takes checks 8 and 12 with it: 8 resolves
    # the referenced commit and 12 hashes that commit's tree, so neither has
    # anything left to work on. Declared rather than tolerated, so that a
    # cascade growing a seventh member is a failure and not a shrug.
    expect_fail("candidate commit does not resolve", 11, "implementation",
                also=(8, 12),
                mutate=lambda t, c, r: {**t, "candidate_commit": "deadbeef" * 5})
    expect_fail("candidate tree hash is wrong", 12, "implementation",
                mutate=lambda t, c, r: {**t, "candidate_tree_hash": "a" * 40})
    expect_fail("approved-plan hash disagrees with the approval record", 13,
                "implementation",
                mutate=lambda t, c, r: {**t, "approved_plan_hash": "c" * 64})
    expect_fail("no approval record to match against", 13, "implementation",
                approval=False)
    expect_fail("diff hash does not match the diff", 14, "implementation",
                mutate=lambda t, c, r: {**t, "diff_hash": "d" * 64})
    expect_fail("diff artifact is missing", 14, "implementation",
                mutate=lambda t, c, r: {**t, "diff_path": "nope.diff"})
    expect_fail("test-result hash does not match", 15, "implementation",
                mutate=lambda t, c, r: {**t, "test_result_hash": "e" * 64})
    # Each §10.1 field is consumed by exactly one later check, so removing it
    # fails check 9 for its absence and that check for having nothing to read.
    # The pairing is the point: it says which check owns which field, and if one
    # of these ever cascades somewhere else the control says so.
    #
    # candidate_commit takes 11 and 12 both, because 12 hashes the tree of the
    # commit 11 resolves.
    _consumes = {
        "candidate_commit":   (11, 12),
        "candidate_tree_hash": (12,),
        "approved_plan_hash":  (13,),
        "diff_hash":           (14,),
        "test_result_hash":    (15,),
    }
    for field, downstream in _consumes.items():
        expect_fail(f"§10.1 field absent: {field}", 9, "implementation",
                    also=downstream,
                    mutate=lambda t, c, r, f=field: {k: v for k, v in t.items() if k != f})

    for p in made:
        shutil.rmtree(p, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("all negative controls fired; every check is falsifiable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
