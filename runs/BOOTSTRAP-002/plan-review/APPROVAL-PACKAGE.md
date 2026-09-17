# Human review package — BOOTSTRAP-002, plan review

Assembled by `scripts/approval_package.py` from the run's own records. Every figure below is quoted from the tool that owns it; none is recomputed here.

**This package decides nothing.** The decision is recorded separately, by a person, with `bootstrap_gate.py record`. §7.3 permits exactly three outcomes: `APPROVE`, `RETURN_FOR_REWORK`, `REJECT`.

## MC-1 enforcement status

`CONVENTION_ONLY`

Every check in this layer is detection that holds while the checks run faithfully and nobody edits the records they read. The same writable code performs the checks on itself. Nothing here is technically enforced.

> **Development evidence, not a protocol outcome.** This run is marked `NOT_A_PROTOCOL_CYCLE`. Nothing in this package may be cited as a protocol result.

## Loop status and valid iteration count

The controller refuses to state an authoritative loop result for this run, and says why:

```text
REFUSED: BOOTSTRAP-002 is marked EXEMPT — BOOTSTRAP / DEVELOPMENT EVIDENCE, NOT_A_PROTOCOL_CYCLE

  Its cycles are development evidence. A loop state computed over them is not a
  protocol outcome, and nothing in the output would have said so.

  Pass --development to compute it anyway. The result is labelled and must not be
  cited as an authoritative protocol result.
```

Recomputed with `--development`. The result is labelled and is not a protocol outcome:

```text
loop state — /sessions/elegant-wizardly-bardeen/mnt/epistemicos/runs/BOOTSTRAP-002/plan-review

DEVELOPMENT EVIDENCE — NOT A PROTOCOL OUTCOME
  EXEMPT — BOOTSTRAP / DEVELOPMENT EVIDENCE, NOT_A_PROTOCOL_CYCLE
  The status below describes bootstrap evidence and does not establish a protocol
  result. §2 and §3 reserve authoritative outcomes to valid protocol cycles.

cycles
  cycle-01  INVALID  4. [FAIL] codex-output-raw.md exists
            does not count toward the budget and its events are ignored

VALID_CYCLE_COUNT: 0

LOOP_STATUS: CONTINUE
No valid cycle has been completed, so §6 has nothing to measure. Repair the evidence and rerun.
```

## Findings

No `ledger.json` yet, so there are no findings to present.

```text
no findings recorded in /sessions/elegant-wizardly-bardeen/mnt/epistemicos/runs/BOOTSTRAP-002/plan-review
```

This is the ordinary state of a run whose cycles are frozen and whose review has not been recorded. It is not a defect, and it is not an absence of findings: no review has reported yet.

## MC-2 conformance, every cycle

The gate is run now, against the frozen evidence, rather than quoted from a stored result. A recorded PASS is a claim about the past; this is the gate's answer today.

### cycle-01 — `MC2_CONFORMANCE: FAIL`

<details><summary>full gate output</summary>

```text
MC-2 conformance — /sessions/elegant-wizardly-bardeen/mnt/epistemicos/runs/BOOTSTRAP-002/plan-review/cycle-01

   1. [PASS] target.json exists
   2. [PASS] target.sha256 exists
   3. [PASS] codex-input.md exists
   4. [FAIL] codex-output-raw.md exists
          not found
   5. [FAIL] all required files non-empty
          skipped, missing: codex-output-raw.md
   6. [FAIL] (not reached)
          earlier checks failed
   7. [FAIL] (not reached)
          earlier checks failed
   8. [FAIL] (not reached)
          earlier checks failed
   9. [FAIL] (not reached)
          earlier checks failed
  10. [FAIL] (not reached)
          earlier checks failed
  11. [FAIL] (not reached)
          earlier checks failed
  12. [FAIL] (not reached)
          earlier checks failed
  13. [FAIL] (not reached)
          earlier checks failed
  14. [FAIL] (not reached)
          earlier checks failed
  15. [FAIL] (not reached)
          earlier checks failed

MC2_CONFORMANCE: FAIL
REVIEW_CYCLE_STATUS: INVALID
This cycle does not count toward the four-cycle budget or any loop state. Repair the evidence and rerun.
```

</details>

> At least one cycle does not currently pass. A package is still produced: whether that blocks approval is the human's decision, not this tool's.

## What is being approved

From `cycle-01`, the most recent frozen cycle.

Target digest: `813d780c3c5fe4744cec517d091fd00a6ffe8581e08a0aa0194b72ae67e47caa`

9 artifact(s):

- `scripts/validate_cycle.py` · `d7183baf425cd3fcd204f85c9301569b6e8c587b33cdb259c1af2c13d013b611`
- `scripts/run_review.py` · `b0110725ae145d05a8b3b6d6315cfc722201c7551be82320f76588239e020aa2`
- `scripts/ledger.py` · `f15a27f2d604daa9c1502c22b82d26549df24e142cafa1e9b5193efb01ae1820`
- `scripts/loop_state.py` · `4839fff415bb2d6bd099709bf99e1cf6a7ccd137c6ffbcad9cefd5275bd71d70`
- `scripts/bootstrap_gate.py` · `44e292a85ae299663e3713c403a04f34bc17d673fce6b31f5167b51a4190eb1c`
- `scripts/findings_format.py` · `27dcf377b0014b3ac2563da61597675fc0bca9c95bce18d1b776bcb22ee53a90`
- `scripts/cycle_projection.py` · `78403ecadf990d2426b5f7e7681909e9456d3a195aa79965b9ec3e7f32026b93`
- `scripts/authority.py` · `c0a394d68ba5f13168dfc78b029ed6799f7bd16b25a21ba5f4ff4401e2efa6d6`
- `scripts/run_pins.py` · `20a22852b3a2c3642ea8a2c0a01ae23e58aedf8e421e1135dc592fcfdb149753`

The bytes reviewed are preserved under `cycle-01/artifacts/`. They are what the reviewer saw, and they do not change when the working tree does.

## §7 coverage

Checked against §7's list rather than against what this package managed to produce, so an item that stopped being generated shows as absent instead of vanishing.

- [x] final plan
- [x] final plan hash
- [x] loop status
- [x] valid iteration count
- [ ] SPEC -> CODE -> TEST mapping
- [ ] resolved findings
- [ ] disputes
- [ ] unresolved findings
- [x] MC-1 enforcement status
- [x] MC-2 conformance results for every valid cycle

**4 of 10 not present.**

- *SPEC -> CODE -> TEST mapping*: the output of a §1 plan audit. A bootstrap run reviews code directly and has no plan, so there is no mapping to produce. Named here rather than omitted, because a reviewer who cannot see what is missing cannot weigh it.
- *resolved findings*: no review has been recorded for this run yet, so there is no ledger to read them from.
- *disputes*: no review has been recorded for this run yet, so no disposition has been rejected.
- *unresolved findings*: no review has been recorded for this run yet. This is not the same as there being none.

---

## Recording the decision

§7.3 permits `APPROVE`, `RETURN_FOR_REWORK`, `REJECT`. Nothing in this file records one.

```text
python scripts/bootstrap_gate.py record \
    --decision APPROVE|RETURN_FOR_REWORK|REJECT \
    --decided-by "<name>" \
    --note "<where the decision was made, and on what>"
```
