#!/usr/bin/env python3
"""Break each repair in turn. Does its control notice?

    python _probe\\mutate_repairs.py

Exit 0 = every repair has a control that goes red when the repair is removed.
Exit 1 = one does not, and it is named.
Exit 2 = could not run.

Why
---
Eight findings were repaired on 26 September and each commit claims a control
that holds it. A control written beside a repair, by the same hand, on the
same afternoon, is exactly the kind that passes because the repair happens to
be there rather than because it is checking for it. That is the defect class
this whole run keeps finding, and asserting it about my own work without
testing it would be the same mistake with a different subject.

So each repair is removed, one at a time, from the real file, and its suite is
run. The repair's control must go red, and the failure must mention something
specific to that repair rather than any failure at all: a suite that goes red
for an unrelated reason establishes nothing about the control named.

`mutate_citation_suite.py` does this for the extractor and has done since
September; the review layer, which is the more consequential of the two, has
had no equivalent. This is a start on that rather than the whole of it: one
mutation per repair as each is made, not a general mutation probe. A repair
that arrives without a line here has not been shown to be watched.

A crashed suite is refused rather than counted, for the reason
`vacuity_sweep.py` records at length: a traceback is the one signal a failing
control never produces, and reading a crash as a catch means the control was
never consulted.

The tree is checked before the first mutation and again after the last. An
earlier run of this probe left `run_review.py` mutated over a weekend, its
protocol-integrity check replaced with `if False:`. The restore runs in a
`finally`, which does not survive the process being killed, and nothing else
in the repository would have noticed a check that had been switched off.
Every suite run in that window passed for a reason other than the one it
names, which is precisely the defect this probe was written to find, arriving
by way of the probe. So a run refuses to start against a tree that is already
dirty, and says so loudly if it fails to leave one clean.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

# The mutation currently applied, written before the file is touched and
# removed after it is put back.
#
# The `finally` below covers an exception and a Ctrl+C. It does not run when
# the process is killed outright, which is what closing a terminal window does.
# On 5 October that left `if False:` sitting in loop_state.py, with this probe
# reporting nothing at all because it never reached its own report. The start
# guard caught it at the next run, which is one run late: a commit in between
# would have carried a disabled check into the record, and the suites would all
# have passed.
#
# So the mutation in progress is recorded on disk and the next run puts it
# back. Untracked on purpose: a file that exists only while a mutation is
# applied has no business in the history.
ACTIVE = Path(__file__).resolve().parent / ".active-mutation.json"

# (finding, file, exact source to replace, replacement, suite, needle)
#
# The needle is matched against the suite's own failure text and has to be
# specific to the control the repair is supposed to have. "expected FAIL" or a
# bare non-zero exit would be satisfied by any breakage at all.
MUTATIONS = [
    ("C01-F01  the reopening guard in the shared evaluator",
     "cycle_projection.py",
     # Disambiguated when C02-F02 gave REJECT_WITH_REASON the same guard, at
     # which point this anchor matched two branches and the probe refused rather
     # than mutating an arbitrary one. The comment line below it belongs to the
     # ACCEPT branch alone.
     "            if self.reopened_at is not None and c < self.reopened_at:\n"
     "                # Insertion order says when a thing was written down.",
     "            if False:\n"
     "                # Insertion order says when a thing was written down.",
     "test_ledger.py",
     # "backdated" appears in the [ok] text and in comments, not in any
     # FAILURE message, so the first version of this needle reported WRONG
     # CONTROL about a control that was working. The failures say "predates
     # the reopening" and "dated before the reopening"; this matches both.
     "the reopening"),

    ("C01-F02  the ceiling binding at every boundary",
     "loop_state.py",
     "        if n >= MAX_VALID_CYCLES:\n"
     "            lines.append(f\"        {status} at n={n} was cleared, and the \"",
     "        if False:\n"
     "            lines.append(f\"        {status} at n={n} was cleared, and the \"",
     "test_ledger.py",
     "fifth cycle"),

    ("C01-F03  check 9 reading the governing artifacts",
     "validate_cycle.py",
     "    if bad:\n"
     "        return [\"the governing artifacts",
     "    if False:\n"
     "        return [\"the governing artifacts",
     "test_validate_cycle.py",
     "governing"),

    ("C01-F04  MC-2 validating the pin history before replaying it",
     "validate_cycle.py",
     "        expect = run_pins.governing_pin_hashes(run, run_dir,\n"
     "                                               int(target[\"cycle\"]))",
     "        expect = run_pins.pin_hashes_for_cycle(\n"
     "            run, run_pins.load_amendments(run_dir), int(target[\"cycle\"]))",
     "test_validate_cycle.py",
     "amendment history"),

    ("C01-F05  no default classification for a run",
     "loop_state.py",
     "    kind, problem = run_pins.run_kind(run)\n"
     "    if problem:",
     "    kind, problem = run_pins.run_kind(run)\n"
     "    problem = None\n"
     "    kind = kind or run_pins.PROTOCOL\n"
     "    if problem:",
     "test_ledger.py",
     "bootstrap_review"),

    ("C01-F06  a reported finding must have a state",
     "loop_state.py",
     "    if _stateless:\n"
     "        raise CannotCalculate(",
     "    if False:\n"
     "        raise CannotCalculate(",
     "test_ledger.py",
     "authoritative state"),

    ("C01-F07  cycle identity, not only uniqueness",
     "validate_cycle.py",
     "        ok7 = not clashes and not mismatch",
     "        ok7 = not clashes",
     "test_validate_cycle.py",
     "check 7"),

    ("C01-F08  the commit and the hash describing one document",
     "run_review.py",
     "    if _committed != sha256_file(protocol):",
     "    if False:",
     "test_run_review.py",
     "protocol"),

    ("C02-F03  the age exemption refused to evidence that is not old",
     "validate_cycle.py",
     "    if _gph is None and _gp is None:\n"
     "        if _modern:",
     "    if _gph is None and _gp is None:\n"
     "        if False:",
     "test_validate_cycle.py",
     "artifacts were preserved"),

    ("C02-F04  a recurrence must not stand against a RESOLVED entry",
     "loop_state.py",
     "            if state_after(f, upto) == RESOLVED:\n"
     "                _unreopened.append(",
     "            if False:\n"
     "                _unreopened.append(",
     "test_ledger.py",
     "a recurrence reported against a RESOLVED ledger entry"),

    ("C02-F07  the gate's evidence must name the target it decides about",
     "bootstrap_gate.py",
     "    if _tdigest not in _input:",
     "    if False:",
     "test_bootstrap_gate.py",
     "never names"),

    # The first version of this mutation removed the `n >= 1` guard and was
    # reported MISSED, correctly. cycle-00 parses as 0 either way and check 7
    # refuses it for mismatching a target that says cycle 1, so that control
    # passes whether the guard is there or not: it exercises the mismatch path,
    # not the rule. The rule this finding is about is the digit count, which is
    # what the checker and the controller disagreed on, so that is what gets
    # removed here. Putting it back to (\d+) makes cycle-1 and cycle-001 parse
    # as cycle 1 again and satisfy check 7, which is the defect exactly.
    ("C02-F05  one cycle-directory grammar, not two that disagree",
     "run_pins.py",
     "CYCLE_DIR = re.compile(r\"cycle-(\\d{2})\\Z\")",
     "CYCLE_DIR = re.compile(r\"cycle-(\\d+)\\Z\")",
     "test_validate_cycle.py",
     "cycle-1 passed MC-2"),

    # Not the function, the call. Deleting the body would also take the
    # damaged-generation refusal with it, and the control that then goes red is
    # about mismatched findings rather than about ownership. Removing the call
    # leaves exactly the pre-repair behaviour: recovery heals a designation that
    # exists and does nothing for one that was earned and never written.
    ("C02-F06  an interrupted designation is recovered before a new candidate",
     "run_review.py",
     "    _recovered = recover_pending_designation(cycle)",
     "    _recovered = None",
     "test_run_review.py",
     "designated after an interruption"),

    # The comparison, not the derivation. Removing the git call would make the
    # check fail to run, which goes red for the wrong reason: a checker that
    # cannot derive anything is not the same as one that derives and does not
    # look. This leaves the derivation in place and stops it mattering, which is
    # exactly the pre-repair behaviour where each hash was well formed on its own.
    ("C02-F08  the reviewed diff is the change between the target's commits",
     "validate_cycle.py",
     "                    if _actual != str(_recorded):",
     "                    if False:",
     "test_run_review.py",
     # The CONTROL's complaint, not the checker's refusal. Reported as a
     # [WRONG CONTROL] on the first run, correctly: with the comparison removed
     # nothing refuses, so the checker's message is exactly the text that cannot
     # appear. What appears is the control saying the swap was accepted.
     #
     # Reported [WRONG CONTROL] a second time too, and that one was not about
     # the needle. The control's fixture was being refused by check 10 over a
     # stale digest in codex-input.md, so it had never established anything
     # about check 14. Two probe runs, two different faults in my own work, both
     # of them invisible to a green suite.
     #
     # And a third time, after C02-F08's second pass added the blob comparison.
     # That check subsumes this one for a moved candidate, so the swap control
     # stopped isolating this rule: removing the digest comparison left the
     # scenario refused by the stronger check. The needle now points at the
     # control that tampers with the recorded digest alone, which is the only
     # case this rule answers for by itself.
     "recording a change set these commits do not produce"),

    # Three fallbacks, three mutations. One would leave the other two unwatched
    # while the line reported them as covered, which is the mistake C02-F02
    # already made once.
    ("C02-F09a  a declared artifact's snapshot is not optional",
     "validate_cycle.py",
     "    if strict_markers:",
     "    if False:",
     "test_run_review.py",
     "snapshot of the test results was deleted"),

    ("C02-F09b  the approval record's snapshot is not optional",
     "validate_cycle.py",
     "    elif _snap_approval is not None and not _snap_approval.is_file() and _mod13:",
     "    elif False:",
     "test_run_review.py",
     "snapshot of the approval record was deleted"),

    ("C02-F09c  the approved plan's snapshot is not optional",
     "validate_cycle.py",
     "                if _mod13 and not snap.is_file():",
     "                if False:",
     "test_run_review.py",
     "snapshot of the approved plan was deleted"),

    ("C02-F10a  the control sources are preserved, not only listed",
     "run_review.py",
     "        _dst.write_bytes((REPO / _e[\"path\"]).read_bytes())\n"
     "        if sha256_file(_dst) != _e[\"sha256\"]:",
     "        if False:",
     "test_run_review.py",
     "bytes were not preserved"),

    ("C02-F10b  a control suite that does not pass has to be named",
     "run_review.py",
     "    if _unexpected:",
     "    if False:",
     "test_run_review.py",
     "froze with a failing control suite and said nothing"),

    # C02-F03's second pass, raised again by cycle 03. Three rules: the format
    # dates the record, an unknown format is refused, and the marker list still
    # dates the targets frozen before the field existed.
    ("C02-F03b  a declared evidence format dates the record on its own",
     "validate_cycle.py",
     "    if fmt is not None:",
     "    if False:",
     "test_validate_cycle.py",
     "declaring an evidence format while omitting"),

    ("C02-F03c  an evidence format this gate does not know is refused",
     "validate_cycle.py",
     "    if _fmt is not None and _fmt not in run_pins.EVIDENCE_FORMATS:",
     "    if False:",
     "test_validate_cycle.py",
     "evidence format this gate does not know"),

    ("C02-F03d  the auxiliary manifest dates a record too",
     "validate_cycle.py",
     "    \"auxiliary_evidence_sha256\",      # B03-F02, the control manifest\n",
     "",
     "test_validate_cycle.py",
     "dated only by its auxiliary evidence manifest"),

    # C02-F04's second pass. Two rules: a transcription that disagrees with the
    # review is refused, and the classification every later check reads comes
    # from the review rather than from the transcription.
    ("C02-F04b  a restated classification is refused, not overruled quietly",
     "loop_state.py",
     "        if _mismatch:",
     "        if False:",
     "test_ledger.py",
     "recorded in findings.json as a new finding"),

    ("C02-F04c  the classification comes from the reparsed review",
     "loop_state.py",
     "            if f.get(\"id\") in raw_kinds:",
     "            if False:",
     "test_ledger.py",
     "carries no classification"),

    # C03-F02, Alex Zamurko's ruling of 2 October and its two corrections.
    # Three rules: nothing enters the scope by being imported without being
    # declared, the list must be what its own history produces, and a scope
    # change that exists only on disk is not a scope change.
    ("C03-F02a  an undeclared import is refused, not absorbed",
     "bootstrap_gate.py",
     "    if missed:",
     "    if False:",
     "test_bootstrap_gate.py",
     "imported a module the manifest does not declare"),

    ("C03-F02b  the manifest's list must be what its history produces",
     "bootstrap_gate.py",
     "    if sorted(replayed) != sorted(comps):",
     "    if False:",
     "test_bootstrap_gate.py",
     "not what its history produces"),

    # This line used to point at a `git status --porcelain` guard. Cycle 04's
    # repair replaced that query with a byte comparison against HEAD, so the
    # needle stopped existing and the probe reported itself broken rather than
    # reporting a catch. The rule is the same one; the line now names where it
    # actually lives.
    ("C03-F02c  a scope change that exists only on disk is refused",
     "bootstrap_gate.py",
     "    if committed(COVERED_MANIFEST) != _live:",
     "    if False:",
     "test_bootstrap_gate.py",
     "a scope change that was never committed"),

    # C02-F02's second pass. One rule, two guards, because §5 gives a finding
    # two dispositions and a guard on one of them is a guard on half the rule.
    # That is how this finding arrived twice.
    ("C02-F02d  an acceptance cannot predate the raise, in replay",
     "cycle_projection.py",
     "            if self.raised_at is not None and c < self.raised_at:\n"
     "                return False, _before_raise(self.raised_at, \"accepted\")",
     "            if False:\n                pass",
     "test_ledger.py",
     "dated before the finding was raised took effect"),

    ("C02-F02e  nor can a rejection, in replay",
     "cycle_projection.py",
     "            if self.raised_at is not None and c < self.raised_at:\n"
     "                return False, _before_raise(self.raised_at, \"rejected\")",
     "            if False:\n                pass",
     "test_ledger.py",
     "rejection dated before the raise took effect"),

    # Five lines, one anchor. The byte comparison replaced the header
    # comparison as the rule on 5 October, so there is now one rule where there
    # were four, and mutating the header comparison changes nothing: the bytes
    # still differ and the gate still refuses. Pointing all five at the rule and
    # keeping their separate needles asserts something the single line cannot,
    # that each control is still live and still goes red when the rule goes.
    ("C02-F08b  the preserved patch names the change's own objects",
     "validate_cycle.py",
     "                        elif _pbytes != _gen:",
     "                        elif False:",
     "test_run_review.py",
     "patch of an entirely different change"),

    # C02-F08's third pass. Cycle 04 named three ways past the comparison as it
    # stood, and one mutation removing the whole comparison would report all
    # three as watched while any one of them could be reintroduced alone. So
    # each hole is reopened on its own, in the shape it had before the repair.
    ("C02-F08c  paths and modes are part of what the patch must agree about",
     "validate_cycle.py",
     "                        elif _pbytes != _gen:",
     "                        elif False:",
     "test_run_review.py",
     "naming a file the change never touched"),

    ("C02-F08d  two files moving between the same objects are two entries",
     "validate_cycle.py",
     "                        elif _pbytes != _gen:",
     "                        elif False:",
     "test_run_review.py",
     "showing one of two identical changes"),

    ("C02-F08e  an empty change set is compared like any other",
     "validate_cycle.py",
     "                        elif _pbytes != _gen:",
     "                        elif False:",
     "test_run_review.py",
     "accepted any patch at all"),

    # The hunk bodies, which the header comparison could not reach and which I
    # had recorded as a known limit rather than closed.
    ("C02-F08f  the hunks are part of the patch, not only its headers",
     "validate_cycle.py",
     "                        elif _pbytes != _gen:",
     "                        elif False:",
     "test_run_review.py",
     "a line the candidate does not contain"),

    # D01-F01, BOOTSTRAP-003 cycle 01. Two rules, two mutations: the replay is
    # limited to the cycles that had reported the finding, and the recorded
    # origin must agree with the event that records it. Each needs its own
    # line, because with the first in place removing the second changes nothing
    # any control could see, which is the shape this probe keeps finding.
    ("D01-F01a  a finding's state comes from the cycles that reported it",
     "loop_state.py",
     "        _through = {v for v in valid if v <= num}",
     "        _through = set(valid)",
     "test_ledger.py",
     # Two corrections to this one line, both reported by the probe rather than
     # noticed by me. First it pointed at the reviewer's own fixture and read
     # MISSED, because that fixture carries a contradictory origin as well and
     # the other rule refuses it first. Then it pointed at the right fixture's
     # SUCCESS text and read WRONG CONTROL, because what a failing control
     # prints is its failure message. This is that message.
     "raised consistently in cycle 2"),

    ("D01-F01b  a recorded origin must agree with its own history",
     "loop_state.py",
     "        if any(c != _declared for c in _events):",
     "        if False:",
     "test_ledger.py",
     "disagrees with its own RAISED event"),

    ("C03-F01  a finished review is reparsed with its own grammar",
     "loop_state.py",
     "        _grammar = structured.get(\"finding_id_grammar\")",
     "        _grammar = None",
     "test_ledger.py",
     "broke a completed cycle"),

    # C03-F02's second pass, raised by cycle 04. Two rules: the approval has to
    # be in the record, and a question the repository cannot answer is not a yes.
    ("C03-F02d  the approval itself must be in the repository record",
     "bootstrap_gate.py",
     "    if committed(_appr_rel) != appr.read_bytes():",
     "    if False:",
     "test_bootstrap_gate.py",
     "untracked and ignored"),

    ("C03-F02e  a provenance query that fails refuses rather than proceeds",
     "bootstrap_gate.py",
     "        if r.returncode != 0:",
     "        if False:",
     "test_bootstrap_gate.py",
     "cannot be read at all: refused for the wrong reason"),

    ("C02-F01  a frozen prompt's exemption is bound to a recorded finding",
     "test_prompts.py",
     "        return fid in json.loads(lp.read_text(encoding=\"utf-8\")).get(\"findings\", {})",
     "        return True",
     "test_prompts.py",
     "in no ledger was reported as recorded"),

    # C02-F02 is three rules, so three mutations. One would leave the other two
    # unwatched while the line reported them as covered.
    ("C02-F02a  a demonstration belongs to a later cycle than its acceptance",
     "cycle_projection.py",
     "            if self.accepted_at is not None and c <= self.accepted_at:",
     "            if False:",
     "test_ledger.py",
     "same-cycle demonstration resolved"),

    ("C02-F02b  a recurrence is observed later than the resolution it undoes",
     "cycle_projection.py",
     "            if self.demonstrated_at is not None and c <= self.demonstrated_at:",
     "            if False:",
     "test_ledger.py",
     "same cycle as the resolution it undoes"),

    ("C02-F02c  a rejection carries the same reopening guard as an acceptance",
     "cycle_projection.py",
     "            if self.reopened_at is not None and c < self.reopened_at:\n"
     "                return False, (f\"dated before the cycle "
     "{self.reopened_at:02d} \"",
     "            if False:\n"
     "                return False, (f\"dated before the cycle "
     "{self.reopened_at:02d} \"",
     "test_ledger.py",
     "dated before the reopening took effect"),

    ("C02-F11  the label reaches the zero-valid-cycle return as well",
     "loop_state.py",
     "        print(\"\\n\".join(lines) if not a.quiet else labelled(\"CONTINUE\"))",
     "        print(\"\\n\".join(lines) if not a.quiet else \"LOOP_STATUS: CONTINUE\")",
     "test_ledger.py",
     "unlabelled status through --quiet"),

    # Not repairs. The §6 exit order, which Alex Zamurko asked on 28 September
    # to be tested at cycle 4 specifically, because every other exit was only
    # ever exercised where the ceiling was not competing with it. Disabling
    # either branch sends its scenario to MAX_4_REACHED, which is the exact
    # failure the new controls exist to refuse, so these two mutations are what
    # make them evidence rather than decoration.
    ("exit A  converging at the ceiling is CONVERGED, not MAX_4",
     "loop_state.py",
     "    if not cur[OPEN] and not cur[DISPUTED]:",
     "    if False:",
     "test_ledger.py",
     "a fourth cycle that converges"),

    ("exit B  a dispute at the ceiling needs a human, not MAX_4",
     "loop_state.py",
     "    if not cur[OPEN] and cur[DISPUTED]:",
     "    if False:",
     "test_ledger.py",
     "only a dispute left"),

    ("exit C  an unchanged ledger stalls rather than reaching the ceiling",
     "loop_state.py",
     "        if stalled:\n"
     "            return (\"STALLED\",",
     "        if False:\n"
     "            return (\"STALLED\",",
     "test_ledger.py",
     "an unchanged ledger at the ceiling"),
]


def run_suite(name: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, str(SCRIPTS / name)],
                          env=env, capture_output=True, text=True, timeout=900)


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _head() -> str:
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def recover() -> int:
    """Put back a mutation that a killed run left applied. 0 = clear to start.

    Deliberately narrow. It restores only when the file is byte for byte the
    mutated content this probe wrote and HEAD is where it was, so an edit made
    in between cannot be destroyed by a recovery that assumed it knew better.
    When anything has moved it says what it knows and refuses, which is the
    same rule as everywhere else here: a restore that might be wrong is worse
    than a message that is certainly right.
    """
    if not ACTIVE.is_file():
        return 0
    try:
        rec = json.loads(ACTIVE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  [CANNOT RUN] {ACTIVE.name} cannot be read ({exc}), so a "
              f"mutation may still be\n  applied and this probe cannot tell "
              f"which one. Check `git status` and `git diff`\n  before running "
              f"anything else against this tree.")
        return 2
    rel = str(rec.get("path", ""))
    label = str(rec.get("finding", "an unnamed mutation"))
    path = REPO / rel
    if not rel or not path.is_file():
        print(f"  [CANNOT RUN] {rel!r} is recorded as mutated and is not a "
              f"file. Restore it by hand,\n  then delete {ACTIVE.name}.")
        return 2
    with path.open("r", encoding="utf-8", newline="") as fh:
        live = fh.read()
    if _head() != rec.get("head") or _sha_text(live) != rec.get("mutated"):
        print(f"  [CANNOT RUN] a previous run was killed while {rel} carried "
              f"the mutation for\n  {label}, and the file or the commit has "
              f"moved since. It is not restored here,\n  because a recovery "
              f"that guesses is worse than one that refuses. Read `git diff "
              f"{rel}`,\n  put it back yourself, then delete {ACTIVE.name}.")
        return 2
    # The bytes HEAD holds for this path, written directly.
    #
    # This was `git checkout -- <path>`, which restores from the INDEX, not from
    # HEAD, while the message below said HEAD. BOOTSTRAP-003's reviewer built
    # the case: unchanged HEAD, mutated working bytes matching the sentinel,
    # different bytes staged. Recovery returned 0, wrote the staged bytes, and
    # reported that it had restored from HEAD. The sentence was false and the
    # file was wrong, and nothing here could have noticed either.
    #
    # `git show HEAD:<path>` names its source in the command, cannot be
    # satisfied by anything in the index, and leaves the index alone, which
    # matters because someone else's staged work is not this probe's to revert.
    r = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
                       capture_output=True)
    if r.returncode != 0:
        print(f"  [CANNOT RUN] {rel} could not be read from HEAD: "
              f"{r.stderr.decode('utf-8', 'replace').strip()}")
        return 2
    path.write_bytes(r.stdout)
    # Verified rather than assumed: the file now holds what HEAD holds.
    with path.open("r", encoding="utf-8", newline="") as fh:
        if _sha_text(fh.read()) != hashlib.sha256(r.stdout).hexdigest():
            print(f"  [CANNOT RUN] {rel} was rewritten from HEAD and does not "
                  f"match HEAD afterwards. Restore it by hand.")
            return 2
    ACTIVE.unlink()
    print(f"  [recovered] a previous run was killed while {rel} held the "
          f"mutation for\n  {label}. It is restored from HEAD. That run "
          f"established nothing about anything;\n  this one starts from a "
          f"clean tree.\n")
    return 0


def modified(rel_paths: list[str]) -> list[str]:
    """Which of these repo-relative paths git reports as changed."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain", "--"] + rel_paths,
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git status failed:\n{r.stderr.strip()}")
    return sorted({ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip()})


def main() -> int:
    # An optional filter, because a whole run is twenty-odd suite executions and
    # correcting one line of this file should not cost all of them. Matched
    # against the finding label, so `C02-F08` takes one mutation and `C02-F02`
    # takes the three that make up that finding.
    #
    # A filtered run is not a verification run: it says nothing about the
    # repairs it skipped, and the summary below says which it looked at rather
    # than claiming the whole set.
    # Recovery first, before the arguments are even looked at.
    #
    # It used to sit after the filter check, so `mutate_repairs.py NOPE` exited
    # on "nothing matches" with a mutation still applied to tracked source. The
    # argument list has nothing to do with whether the working tree is in a
    # state this probe left behind, and a tree left mutated should be put back
    # whatever you asked for. Found by test_probe_recovery.py, whose fixture
    # passes a filter that matches nothing precisely so that no mutation runs.
    rc = recover()
    if rc:
        return rc

    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    selected = [m for m in MUTATIONS
                if not want or any(w.lower() in m[0].lower() for w in want)]
    if want and not selected:
        print(f"  [CANNOT RUN] nothing matches {', '.join(want)}")
        return 2

    # The clean-tree guard follows recovery above, because the commonest reason
    # this tree is dirty is this probe itself, and "commit or discard them
    # first" is the wrong instruction for a file this process mutated and
    # failed to put back.
    targets = sorted({f"scripts/{m[1]}" for m in selected})
    try:
        dirty = modified(targets)
    except RuntimeError as exc:
        print(f"  [CANNOT RUN] {exc}")
        return 2
    if dirty:
        print("  [CANNOT RUN] this probe writes to tracked source and restores "
              "it afterwards,\n  so it can only run against a clean tree. These "
              "already differ from HEAD:\n")
        for p in dirty:
            print(f"      {p}")
        print("\n  Commit or discard them first. Started from here, each restore "
              "would put the\n  file back to whatever it held at the start, which "
              "is not the same as putting\n  it back to the repaired source, and "
              "the result would say nothing about the\n  repairs.")
        return 2

    bad = 0
    for finding, fname, old, new, suite, needle in selected:
        path = SCRIPTS / fname
        # newline="" on the READ as well, not only on the writes below. Without
        # it Python translates CRLF to LF on the way in, so `original` is not
        # the file's bytes and restoring it rewrites every line ending in the
        # file. That is how run_pins.py came back [LEFT MODIFIED] on
        # 30 September after a restore that had put the source back correctly:
        # the probe reported a real difference it had introduced itself.
        # `Path.read_text` only grew a newline argument in 3.13, while
        # `write_text` has had one since 3.10, so the read is spelled out.
        with path.open("r", encoding="utf-8", newline="") as _f:
            original = _f.read()
        found = original.count(old)
        if found != 1:
            hint = ""
            if found == 0 and new in original:
                hint = ("\n      The replacement text is there instead, so the "
                        "mutation is already applied:\n      an earlier run "
                        "wrote it and did not restore it.")
            print(f"  [BROKEN PROBE] {finding}\n"
                  f"      the source this mutation replaces appears {found} "
                  f"times in {fname}, not\n      once, so the mutation cannot "
                  f"be applied. That is reported rather than\n      counted as "
                  f"a catch.{hint}")
            bad += 1
            continue

        # The record goes down BEFORE the file is touched, and carries the
        # digest of what is about to be written. Written after, a kill in the
        # gap would leave a mutated file with nothing naming it, which is the
        # state this is here to prevent.
        mutated = original.replace(old, new, 1)
        ACTIVE.write_text(json.dumps({
            "finding": finding,
            "path": f"scripts/{fname}",
            "head": _head(),
            "mutated": _sha_text(mutated),
        }, indent=2) + "\n", encoding="utf-8")
        # newline="" so a run on Windows does not rewrite the file's endings
        # on its way past, and on the restore as well as the write.
        path.write_text(mutated, encoding="utf-8", newline="")
        try:
            r = run_suite(suite)
        except subprocess.TimeoutExpired as _exc:
            # Not a catch and not a miss. The suite never finished, so nothing
            # at all is known about the control this mutation is aimed at, and
            # saying so is the only honest report.
            #
            # Seen on 29 September with a remaining time of minus 2138 seconds,
            # which is not a hang: a negative remainder means the deadline had
            # already passed when the wait began, because the machine slept
            # between starting the suite and waiting on it. Ninety minutes of
            # sleep and a genuinely wedged suite arrive here identically, and
            # neither says anything about the repair.
            #
            # Before this the exception escaped and killed the run. The restore
            # still happened, because it is in the finally below, and the tree
            # was clean afterwards. But the output was a traceback, which is the
            # one signal a failing control never produces, so reading it as
            # anything about the repairs would have been the same mistake this
            # probe refuses everywhere else.
            # Say which of the two it was rather than leaving the reader to
            # guess. A negative remainder is a deadline that passed while
            # nothing was executing, which only happens if the machine slept.
            _t = getattr(_exc, "timeout", None)
            _why = ("the machine slept mid-run: the deadline passed while "
                    "nothing was executing"
                    if isinstance(_t, (int, float)) and _t < 0
                    else "the suite genuinely ran past the limit")
            print(f"  [COULD NOT RUN] {finding}\n"
                  f"      {suite} did not finish. Nothing is established about "
                  f"its control\n      either way. Remaining time {_t}, so "
                  f"{_why}. Re-run it.")
            bad += 1
            continue
        finally:
            path.write_text(original, encoding="utf-8", newline="")
            ACTIVE.unlink(missing_ok=True)

        blob = (r.stdout or "") + (r.stderr or "")
        if "Traceback (most recent call last)" in (r.stderr or ""):
            print(f"  [CRASHED] {finding}\n"
                  f"      {suite} crashed rather than failing controls, so "
                  f"its output says nothing about which controls hold.")
            bad += 1
        elif r.returncode == 0:
            print(f"  [MISSED] {finding}\n"
                  f"      the repair was removed and {suite} still passed. "
                  f"Nothing in that suite is checking for it.")
            bad += 1
        elif needle.lower() not in blob.lower():
            print(f"  [WRONG CONTROL] {finding}\n"
                  f"      {suite} went red, and not for anything mentioning "
                  f"{needle!r}. Something failed; it is not shown to be the "
                  f"control this repair is supposed to have.")
            bad += 1
        else:
            print(f"  [caught] {finding}")

    left = modified(targets)
    if left:
        print(f"\n  [LEFT MODIFIED] the probe did not restore everything it "
              f"wrote to:\n")
        for p in left:
            print(f"      {p}")
        print("\n  Restore them with `git checkout --` before running anything "
              "else. Until then\n  every suite in the repository is reading "
              "source this probe broke on purpose.")
        bad += 1

    print()
    _of = (f"{len(selected)} selected repair(s)" if want
           else f"{len(MUTATIONS)} repairs")
    if bad:
        print(f"  {bad} of {_of} are not demonstrably held by a control.")
        return 1
    print(f"  all {_of} go red when removed, each in a control that names what "
          f"it is about.")
    if want:
        print(f"  Only {', '.join(want)} was looked at. The rest of the set is "
              f"not established\n  by this run.")
    print("  That is not proof the repairs are correct. It is proof they are")
    print("  watched, which is the claim each commit made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
