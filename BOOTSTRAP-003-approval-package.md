# Human review package — BOOTSTRAP-003, plan review

Assembled by `scripts/approval_package.py` from the run's own records. Every figure below is quoted from the tool that owns it; none is recomputed here.

**This package decides nothing.** The decision is recorded separately, by a person, with `bootstrap_gate.py record`. §7.3 permits exactly three outcomes: `APPROVE`, `RETURN_FOR_REWORK`, `REJECT`.

## MC-1 enforcement status

`CONVENTION_ONLY`

Every check in this layer is detection that holds while the checks run faithfully and nobody edits the records they read. The same writable code performs the checks on itself. Nothing here is technically enforced.

> **Development evidence, not a protocol outcome.** This run is marked `NOT_A_PROTOCOL_CYCLE`. Nothing in this package may be cited as a protocol result.

## Loop status and valid iteration count

The controller refuses to state an authoritative loop result for this run, and says why:

```text
REFUSED: BOOTSTRAP-003 is marked EXEMPT — BOOTSTRAP / DEVELOPMENT EVIDENCE, NOT_A_PROTOCOL_CYCLE

  Its cycles are development evidence. A loop state computed over them is not a
  protocol outcome, and nothing in the output would have said so.

  Pass --development to compute it anyway. The result is labelled and must not be
  cited as an authoritative protocol result.
```

Recomputed with `--development`. The result is labelled and is not a protocol outcome:

```text
loop state — C:\EpistemicOS\epistemicos\runs\BOOTSTRAP-003\plan-review

DEVELOPMENT EVIDENCE — NOT A PROTOCOL OUTCOME
  EXEMPT — BOOTSTRAP / DEVELOPMENT EVIDENCE, NOT_A_PROTOCOL_CYCLE
  The status below describes bootstrap evidence and does not establish a protocol
  result. §2 and §3 reserve authoritative outcomes to valid protocol cycles.

cycles
  cycle-01  VALID    -> n=1
  cycle-02  VALID    -> n=2
  cycle-03  VALID    -> n=3

VALID_CYCLE_COUNT: 3

authoritative findings
  cycle-01  1 finding(s): D01-F01
  cycle-02  1 finding(s): D02-F01
  cycle-03  1 finding(s): D02-F01
  every recorded finding is accounted for in the ledger
  and every one of them has a state the cycles that had reported it produce
  and none of them was raised in a cycle other than the one it records
  and no recurrence is left standing against a RESOLVED ledger entry

boundaries, in order
  n=1 (cycle-01)  OPEN 1  DISPUTED 0  RESOLVED 0   -> CONTINUE
  n=2 (cycle-02)  OPEN 1  DISPUTED 0  RESOLVED 1   -> CONTINUE
  n=3 (cycle-03)  OPEN 1  DISPUTED 0  RESOLVED 1   -> STALLED

§6 sets and exits at the governing boundary, n=3
  OPEN_3           1  D02-F01
  DISPUTED_3       0  -
  RESOLVED_3       1  D01-F01
  OPEN_2           1  D02-F01
  RESOLVED_NEW_3   0  -
  DISPUTED_NEW_3   0  -
  C STALLED                      |OPEN_3| >= |OPEN_2| (1 >= 1) and no new resolved/disputed   yes

LOOP_STATUS: STALLED  [DEVELOPMENT EVIDENCE — NOT A PROTOCOL OUTCOME]
The last valid cycle reduced nothing, resolved nothing and disputed nothing. Stop now rather than spending the remaining budget. Proceed to human plan review.

ledger at the stop boundary, n=3
  OPEN       1  D02-F01
  DISPUTED   0  -
  RESOLVED   1  D01-F01
```

## Findings

§7.2 requires disputes and unresolved findings to be presented separately. They are separate headings below; the full ledger follows both.

States below are reconstructed by the controller at its governing boundary, n=3, not read from the ledger's cached fields.

### Unresolved findings — the human decides each one

§7.2: the human determines whether each requires correction, is explicitly waived or accepted, or causes rejection of the plan.

- **D02-F01** · CONTRADICTORY IMPLEMENTATION MAPPING · section 4 review reporting; section 5 repair demonstration; section 6 convergence
  - found by: `CODEX_REVIEW`

### Disputes — the human adjudicates

§7.1: a dispute is a Codex finding plus a Claude `REJECT_WITH_REASON`.

None.

### Resolved findings

1 resolved.

`RESOLVED` under §5 means a repair was demonstrated in a later review target. It does not mean the repair was re-verified afterwards.

<details><summary>Full ledger</summary>

```text
findings ledger — C:\EpistemicOS\epistemicos\runs\BOOTSTRAP-003\plan-review

  D01-F01  [RESOLVED]  MISSING REQUIREMENT  (MC-2 authoritative-finding accounting; protocol section 6 boundary-specific finding sets and convergence)
      cycle 01  RAISED             -> OPEN  the stateless-finding check replays history over every valid
      cycle 01  ACCEPT             -> OPEN  reproduced as described: moving only the RAISED event to a l
      cycle 02  DEMONSTRATED       -> RESOLVED  cycle 02 review: boundary-limited replay rejects a later RAI

  D02-F01  [OPEN]  CONTRADICTORY IMPLEMENTATION MAPPING  (section 4 review reporting; section 5 repair demonstration; section 6 convergence)
      cycle 02  RAISED             -> OPEN  a canonical finding identifier anywhere in a zero-finding re
      cycle 02  ACCEPT             -> OPEN  reproduced: the reviewer supplied the target hash and a sent

  OPEN      1
  RESOLVED  1
  DISPUTED  0
```

</details>

## Implementer-disclosed defects

Found by the implementing agent, not raised by any reviewer, and therefore not in the ledger above. They carry no cycle-generated identifier because no cycle produced them.

### SELF-F02 — `REPAIRED_UNREVIEWED`

The mutation probe writes a deliberately broken line into tracked source, runs a suite, and restores the file in a finally block. A finally does not run when the process is killed outright, which is what closing a terminal window does. A killed run therefore left a disabled check sitting in the repository, with every suite passing for a reason other than the one it names, and nothing else in the repository able to notice.

- affected: _probe/mutate_repairs.py. Not a covered component; it is preserved in cycle evidence as an instrument, and the review of 4 October states explicitly that its results are assertions rather than executed evidence.
- severity: Moderate. It cannot alter a record or a frozen cycle. It can make every suite in the repository pass while a check is switched off, and a commit made in that window would carry the disabled check into the history. The window on 5 October was about forty minutes and nothing was committed in it.
- discovered: Implementer-disclosed. The probe's own docstring has named this risk since late September, and the mitigation was a start-time guard that only catches it on the next run. It happened on 5 October 2026: a PowerShell window was closed mid-run and left 'if False:' in scripts/loop_state.py, where it sat until the next probe run refused to start.
- repair: Record the mutation on disk before the file is touched, carrying the finding, the path, HEAD, and the digest of the text about to be written. The next run restores from HEAD and says what it did. The recovery is narrow on purpose: if HEAD has moved or the file is not byte for byte what the probe wrote, it refuses and says so rather than overwriting an edit made since.

`REPAIRED_UNREVIEWED` means a repair has landed with controls behind it, and nobody independent has examined it. It is not a resolution.

### SELF-F04 — `OPEN`

The loop-state controller has a --json flag whose purpose is to give a caller the governing boundary and the section 6 sets without parsing prose, so that no second component has to restate the rule. When every cycle in a run fails the MC-2 gate, the controller takes an early return six hundred lines above the --json branch: it prints a paragraph of English and exits 0. A caller that asked for machine output receives unparseable text under a success code. The flag's own documentation promises it 'exits non-zero exactly as the ordinary run does', and it does, which is the problem: the ordinary run's exit 0 is a human-readable CONTINUE, and through this interface the same 0 asserts that a state was established when none was computed.

- affected: scripts/loop_state.py, a covered component of the BOOTSTRAP-003 target. The --json branch itself was added on 8 October 2026 as the third repair of SELF-F01.
- severity: Moderate, and lower than it looks. The one caller that exists, approval_package.py, refuses a result it cannot parse, so this does not reach an approval document today. What it is, is a success code asserting something the program never computed, in the interface built specifically so that callers would not have to guess. The next caller written against it will have no reason to expect prose.
- discovered: Raised by the BOOTSTRAP-003 cycle 03 reviewer, outside the finding format and therefore not captured in the ledger. Their words: 'loop_state.py:592 returns prose with exit 0 when every cycle is invalid, even with --json. The package rejects that unreadable result, so this path does not recreate SELF-F01's false clean package. It should nevertheless return a defined JSON result or an explicit failure.' Recorded here rather than left in the review body, because a defect that carries no identifier is one nothing in this repository will ask about again.
- repair: Not yet landed. The early return must honour --json. The emitted object must not carry empty open, resolved and disputed lists, because an empty list is the same silent zero this layer keeps finding: a caller cannot tell 'nothing is open' from 'the sets were never computed'. Either omit the set keys and carry an explicit flag saying the walk did not run, or exit non-zero. The sole caller must then be controlled against that shape rather than assumed to survive it.

`OPEN` means disclosed, not repaired. It is not a resolution.

### Resolved and no longer outstanding — 2

Listed by identifier only. `RESOLVED` here means an independent review examined the repair in a later target and found it held, and the register carries that reviewer's own limits with it.

- **SELF-F01** · resolved per BOOTSTRAP-003 cycle 03 reviewer
- **SELF-F03** · resolved per BOOTSTRAP-003 cycle 03 reviewer


## MC-2 conformance, every cycle

The gate is run now, against the frozen evidence, rather than quoted from a stored result. A recorded PASS is a claim about the past; this is the gate's answer today.

### cycle-01 — `MC2_CONFORMANCE: PASS`

<details><summary>full gate output</summary>

```text
MC-2 conformance — C:\EpistemicOS\epistemicos\runs\BOOTSTRAP-003\plan-review\cycle-01

   1. [PASS] target.json exists
   2. [PASS] target.sha256 exists
   3. [PASS] codex-input.md exists
   4. [PASS] codex-output-raw.md exists
   5. [PASS] all required files non-empty
   6. [PASS] target.sha256 matches target
   7. [PASS] cycle identity consistent and unique
          cycle 1 in plan-review, matching its directory and run
   8. [PASS] referenced git commit exists
          resolved: badd8ec5b23b2153903df2b47fa713d69ccef0e8
   9. [PASS] mandatory hashed artifacts present and matching
  10. [PASS] codex-input.md contains target SHA-256 verbatim
  11. [N/A ] candidate commit present and exists
          review_type is 'plan'; §10.2 applies to implementation review only
  12. [N/A ] candidate tree hash matches the candidate tree
          review_type is 'plan'; §10.2 applies to implementation review only
  13. [N/A ] approved-plan hash matches the frozen approved plan
          review_type is 'plan'; §10.2 applies to implementation review only
  14. [N/A ] diff hash matches the reviewed diff
          review_type is 'plan'; §10.2 applies to implementation review only
  15. [N/A ] test-result hash matches the supplied test results
          review_type is 'plan'; §10.2 applies to implementation review only

MC2_CONFORMANCE: PASS
```

</details>

### cycle-02 — `MC2_CONFORMANCE: PASS`

<details><summary>full gate output</summary>

```text
MC-2 conformance — C:\EpistemicOS\epistemicos\runs\BOOTSTRAP-003\plan-review\cycle-02

   1. [PASS] target.json exists
   2. [PASS] target.sha256 exists
   3. [PASS] codex-input.md exists
   4. [PASS] codex-output-raw.md exists
   5. [PASS] all required files non-empty
   6. [PASS] target.sha256 matches target
   7. [PASS] cycle identity consistent and unique
          cycle 2 in plan-review, matching its directory and run
   8. [PASS] referenced git commit exists
          resolved: badd8ec5b23b2153903df2b47fa713d69ccef0e8
   9. [PASS] mandatory hashed artifacts present and matching
  10. [PASS] codex-input.md contains target SHA-256 verbatim
  11. [N/A ] candidate commit present and exists
          review_type is 'plan'; §10.2 applies to implementation review only
  12. [N/A ] candidate tree hash matches the candidate tree
          review_type is 'plan'; §10.2 applies to implementation review only
  13. [N/A ] approved-plan hash matches the frozen approved plan
          review_type is 'plan'; §10.2 applies to implementation review only
  14. [N/A ] diff hash matches the reviewed diff
          review_type is 'plan'; §10.2 applies to implementation review only
  15. [N/A ] test-result hash matches the supplied test results
          review_type is 'plan'; §10.2 applies to implementation review only

MC2_CONFORMANCE: PASS
```

</details>

### cycle-03 — `MC2_CONFORMANCE: PASS`

<details><summary>full gate output</summary>

```text
MC-2 conformance — C:\EpistemicOS\epistemicos\runs\BOOTSTRAP-003\plan-review\cycle-03

   1. [PASS] target.json exists
   2. [PASS] target.sha256 exists
   3. [PASS] codex-input.md exists
   4. [PASS] codex-output-raw.md exists
   5. [PASS] all required files non-empty
   6. [PASS] target.sha256 matches target
   7. [PASS] cycle identity consistent and unique
          cycle 3 in plan-review, matching its directory and run
   8. [PASS] referenced git commit exists
          resolved: badd8ec5b23b2153903df2b47fa713d69ccef0e8
   9. [PASS] mandatory hashed artifacts present and matching
  10. [PASS] codex-input.md contains target SHA-256 verbatim
  11. [N/A ] candidate commit present and exists
          review_type is 'plan'; §10.2 applies to implementation review only
  12. [N/A ] candidate tree hash matches the candidate tree
          review_type is 'plan'; §10.2 applies to implementation review only
  13. [N/A ] approved-plan hash matches the frozen approved plan
          review_type is 'plan'; §10.2 applies to implementation review only
  14. [N/A ] diff hash matches the reviewed diff
          review_type is 'plan'; §10.2 applies to implementation review only
  15. [N/A ] test-result hash matches the supplied test results
          review_type is 'plan'; §10.2 applies to implementation review only

MC2_CONFORMANCE: PASS
```

</details>

## What is being approved

From `cycle-03`, the most recent frozen cycle.

Target digest: `5a0cd07cc17a409769421df55d2236d1942317c1888689315c2c037580d52200`

11 artifact(s):

- `specs/covered-components.json` · `49cf5da6961051efc096cc073fd0cca3b4b13f24bc1c9d8fb3e86e41a89ac30e`
- `specs/evidence-schema-v1.0.md` · `4203ba64bd5ba1db9cd56357c8bf9dd8e6efb419fab7f7635a415c272d3a739c`
- `scripts/authority.py` · `c0a394d68ba5f13168dfc78b029ed6799f7bd16b25a21ba5f4ff4401e2efa6d6`
- `scripts/bootstrap_gate.py` · `901d18105cfa50d27ac948aa8beaf2e112de19f8ee2a38dd9c02b8c108c6985b`
- `scripts/cycle_projection.py` · `27b1e5782d6b4cdc46d0bbb997722099d7f244bc6d90e65d235f3ac405572a17`
- `scripts/findings_format.py` · `5f5edcda76869865442756b395f30085b4cbe2c01135fbbfc721270eafc279db`
- `scripts/ledger.py` · `2f86764173e423cb775cf7d47768440b7185f69681032117ee7cc7f154ddeb84`
- `scripts/loop_state.py` · `c44e1676ab570167d40452f8c29733f552c6dccd3d01c05c7d0840365f987386`
- `scripts/run_pins.py` · `661b7d89a267061cc454a93780c987c3de6c471b4c472230165ece74c8e1b5b2`
- `scripts/run_review.py` · `9b2f02ef20640fa2f5cd5f72cc9e1bbbe2d869f2ecfd1c5274472097d5358a4b`
- `scripts/validate_cycle.py` · `7b8c45b9fa7edb4fefa025c8c010499983750396300e399a66e299966f22e768`

The bytes reviewed are preserved under `cycle-03/artifacts/`. They are what the reviewer saw, and they do not change when the working tree does.

## §7 coverage

Checked against §7's list rather than against what this package managed to produce, so an item that stopped being generated shows as absent instead of vanishing.

- [x] final plan
- [x] final plan hash
- [x] loop status
- [x] valid iteration count
- [ ] SPEC -> CODE -> TEST mapping
- [x] resolved findings
- [x] disputes
- [x] unresolved findings
- [x] MC-1 enforcement status
- [x] MC-2 conformance results for every valid cycle

**1 of 10 not present.**

- *SPEC -> CODE -> TEST mapping*: the output of a §1 plan audit. A bootstrap run reviews code directly and has no plan, so there is no mapping to produce. Named here rather than omitted, because a reviewer who cannot see what is missing cannot weigh it.

---

## Recording the decision

§7.3 permits `APPROVE`, `RETURN_FOR_REWORK`, `REJECT`. Nothing in this file records one.

```text
python scripts/bootstrap_gate.py record \
    --decision APPROVE|RETURN_FOR_REWORK|REJECT \
    --decided-by "<name>" \
    --note "<where the decision was made, and on what>"
```
