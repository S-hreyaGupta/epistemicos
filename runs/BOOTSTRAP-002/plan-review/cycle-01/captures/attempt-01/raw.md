```text
TARGET_SHA256 813d780c3c5fe4744cec517d091fd00a6ffe8581e08a0aa0194b72ae67e47caa
```

I verified this digest against `target.json`. All nine reviewed scripts match their target hashes. The governing protocol and evidence-schema files also match their pinned hashes.

The auxiliary manifest matches its recorded digest. Four of the five named suites match their frozen entries directly. The working-tree runner suite differs; I recovered its matching version from commit `3144baa`, verified its SHA-256 against the manifest, and executed that version separately. All five frozen suites completed successfully. The findings below come from source inspection and additional isolated reproductions, not from interpreting those passing suites as proof of correctness.

Finding ID: C01-F01

Class: CONTRADICTORY IMPLEMENTATION MAPPING

Requirement ID: Protocol §5, accepted-repair lifecycle; §6, mechanically determined finding states.

Evidence:

This concerns BOOTSTRAP-001 finding **B01-F11**.

In [cycle_projection.py](/C:/EpistemicOS/epistemicos/scripts/cycle_projection.py:217), `replay()` still arms an acceptance whenever the current replayed state is `OPEN`. It does not check whether that acceptance predates the reopening it follows.

The reopening-date guard exists in `last_authorized()`, at line 383. It is absent from both `replay()` and `skipped_events()`.

I supplied this existing history, with all four cycles authorized:

```text
RAISED(1)
ACCEPT(1)
DEMONSTRATED(2)
REOPENED(3)
ACCEPT(2)
DEMONSTRATED(4)
```

The results were:

```text
replay:                 RESOLVED
last_authorized ACCEPT: None
controller state_after: RESOLVED
skipped_events:         []
```

The supplied ledger control inserts the backdated acceptance and then attempts a new `resolve` command. That exercises the repaired prerequisite lookup. It does not exercise state reconstruction from an existing history that already contains the subsequent demonstration.

Finding:

The claimed replay repair is not demonstrated. The command path refuses a new closure, but the state-reconstruction path still honors the same invalid closure when it is already recorded.

The ledger and controller therefore disagree with the prerequisite lookup about whether the finding was legitimately resolved. The diagnostic replay also reports no skipped event. This is the original defect surviving in the functions that determine the authoritative state.

Required correction:

Apply the same chronological eligibility rules to state replay, prerequisite lookup, and skipped-event reporting. Prefer one shared transition evaluator so the three implementations cannot disagree.

Add a control containing the complete historical sequence above, including the already-recorded demonstration. Verify the ledger’s effective state, cycle snapshots, controller state, and diagnostics. The backdated acceptance must not authorize resolution, and the finding must remain `OPEN`.

---

Finding ID: C01-F02

Class: CONTRADICTORY IMPLEMENTATION MAPPING

Requirement ID: Protocol §2, maximum four valid review cycles; §6, mandatory exits.

Evidence:

This concerns BOOTSTRAP-001 finding **B01-F02**.

In [loop_state.py](/C:/EpistemicOS/epistemicos/scripts/loop_state.py:546), a cleared terminal outcome is recorded as `cleared_latest` only when its boundary is the latest valid cycle. The new ceiling check at line 592 is inside the fallback handling for that latest boundary.

I constructed five MC-2-valid cycles with:

```text
RAISED(1)
ACCEPT(1)
DEMONSTRATED(5)
```

The finding remains open through cycle 4. Recorded authorizations clear `STALLED` at valid boundaries 2, 3, and 4.

The controller exited 0 and reported:

```text
VALID_CYCLE_COUNT: 5

n=4 ... -> STALLED
        STALLED at n=4 cleared by recorded authorization

n=5 ... -> CONVERGED

LOOP_STATUS: CONVERGED
```

It evaluated the fifth-cycle demonstration and made that boundary govern. It did not report the fifth cycle as an unauthorized continuation.

The supplied control demonstrates the repaired case where boundary 4 is the latest boundary. It does not test boundary 4 after a later evidence directory exists.

Finding:

The four-cycle ceiling is enforced when clearing the latest exit, but not when replaying a cleared historical exit. An authorization can still let the controller evaluate a fifth cycle and derive convergence from work outside the permitted budget.

The runner’s refusal to create a fifth cycle is useful, but does not repair the controller’s handling of already-existing evidence. The controller explicitly undertakes to detect unauthorized continuations rather than trust that every directory was legitimately created.

The repair is therefore only partially demonstrated.

Required correction:

Enforce the ceiling while walking every valid-cycle boundary. Clearing a terminal outcome at boundary 4 must not permit evaluation of boundary 5 as an authorized continuation.

Add a control with an existing fifth cycle and a matching authorization for the fourth-cycle stall. Verify that the fourth boundary remains governing, the ceiling remains binding, and the fifth-cycle resolution cannot establish convergence.

---

Finding ID: C01-F03

Class: MISSING REQUIREMENT

Requirement ID: Protocol MC-2 check 9, mandatory hashed artifacts must be present and match their recorded hashes.

Evidence:

This concerns BOOTSTRAP-001 finding **B01-F07**.

In [validate_cycle.py](/C:/EpistemicOS/epistemicos/scripts/validate_cycle.py:218), `_governing_problems()` checks digest syntax and compares the target’s governing hashes with hashes reconstructed from the run record. It does not resolve and hash the governing artifacts.

I first established a passing fixture with real protocol and specification files and their actual SHA-256 values recorded consistently in the run and target. I then deleted both governing files without changing either record.

The validator still exited 0:

```text
Checks 1–10: PASS
Checks 11–15: N/A
```

No preserved governing copies were available in that fixture. Check 9 nevertheless passed.

The function’s own description acknowledges that it checks records rather than artifact bytes. The original malformed-hash and invented-set controls now fail correctly; this adjacent missing-artifact case still passes.

Finding:

Agreement between the target and run history does not establish that the mandatory governing artifacts are present or that their contents match the recorded hashes.

The B01-F07 repair closes the target-versus-run identity mismatch, but leaves the presence-and-content obligation of check 9 unimplemented for governing artifacts. Declaring this limitation does not satisfy that requirement.

Required correction:

Preserve or otherwise resolve the exact governing versions for each cycle, and have check 9 verify their existence and content hashes.

Use historical versions appropriate to the cycle rather than today’s mutable governing files, so a legitimate prospective amendment does not invalidate completed evidence.

Add controls that independently remove and alter governing protocol and specification artifacts while leaving all recorded digests consistent. Each must fail check 9 for the artifact defect.

---

Finding ID: C01-F04

Class: CONTRADICTORY IMPLEMENTATION MAPPING

Requirement ID: Protocol §0.2, frozen governing specification; MC-2 check 9, validation against the cycle’s governing artifacts.

Evidence:

This also concerns BOOTSTRAP-001 finding **B01-F07**.

At [validate_cycle.py](/C:/EpistemicOS/epistemicos/scripts/validate_cycle.py:282), `_governing_problems()` calls:

```python
items = run_pins.load_amendments(run_dir)
expect = run_pins.pin_hashes_for_cycle(run, items, int(target["cycle"]))
```

It does not call `validate_chain()` or `check_frozen_assignments()`.

The freeze path performs those validations before using the effective pin hashes. MC-2 therefore uses a weaker interpretation of the same history.

On a previously passing fixture, I added an amendment whose `prior_pin_set` named `never-pinned.md`, a set the run had never held. Direct chain validation rejected it:

```text
amendment 0 does not follow the pin history.
```

With that same amendment file present, MC-2 still exited 0, with checks 1–10 passing. The invalid amendment replay produced the recorded final set, so the validator accepted it.

Finding:

The new check compares the target against the result of replaying an amendment list, but does not establish that the list is a valid pin history.

Consequently, the runner can reject a governing history while the validator accepts a completed cycle against it. The claim that check 9 verifies the governing set against the run’s history is incomplete: it verifies against an unchecked reconstruction.

Required correction:

Use a shared validated-history operation before deriving the cycle’s effective governing hashes. Apply the chain and frozen-assignment constraints consistently in the runner and validator.

Add MC-2 controls for broken prior-set continuity, invalid amendment ordering, missing amendment attribution, and amendments that contradict completed assignments. Their expected failures must identify the history defect rather than depend on an unrelated digest mismatch.

---

Finding ID: C01-F05

Class: MISSING REQUIREMENT

Requirement ID: Evidence schema, bootstrap exception; protocol MC-1, accurately classified run evidence.

Evidence:

This concerns BOOTSTRAP-001 finding **B01-F14**, and the related development-evidence distinction described under B01-F08.

In [loop_state.py](/C:/EpistemicOS/epistemicos/scripts/loop_state.py:379), classification is:

```python
label = str(run.get("bootstrap_review", "")).strip()
kind = "DEVELOPMENT" if label.startswith("EXEMPT") else "PROTOCOL"
```

The controller now refuses a missing `run.json`, as claimed. However, missing or unrecognized classification inside an existing record defaults to `PROTOCOL`.

I used a completed fixture with:

```text
bootstrap_review: EXEMPT - NOT_A_PROTOCOL_CYCLE
mc1_enforcement: CONVENTION_ONLY
```

The ordinary controller invocation correctly refused it with exit 2.

I then removed only `bootstrap_review`, retaining the file and its valid enforcement status. The same ordinary invocation exited 0 and reported:

```text
LOOP_STATUS: CONVERGED
```

There was no development-evidence qualification.

Finding:

Deleting the entire metadata file is now refused, but deleting the field that establishes its classification promotes development evidence into an authoritative protocol outcome.

An existing JSON object with a valid enforcement-status field is not sufficient evidence that the run is a protocol run. The remaining fallback makes absence of classification mean the stronger classification.

The exact whole-file-deletion repair is demonstrated; the broader requirement to establish the run’s identity before reporting an authoritative outcome remains incomplete.

Required correction:

Require an explicit recognized classification. Missing, empty, or unrecognized values must produce `CANNOT CALCULATE`, without an authoritative outcome or an invented development label.

Apply the same classification rule across consumers. Add controls that remove only the classification field, leave it empty, and supply an unknown value while all other fixture prerequisites remain valid.

---

Finding ID: C01-F06

Class: MISSING REQUIREMENT

Requirement ID: Protocol §6, every finding from a valid cycle has one current state; MC-2, invalid-cycle events cannot supply authority.

Evidence:

In [loop_state.py](/C:/EpistemicOS/epistemicos/scripts/loop_state.py:486), authoritative finding reconciliation checks only whether an identifier exists as a key in `ledger["findings"]`.

Later, `sets_at()` reconstructs the finding’s state from events in valid cycles. If replay returns `None`, the identifier enters none of `OPEN`, `RESOLVED`, or `DISPUTED`. The controller does not reconcile that omission with the findings reported by valid reviews.

I constructed:

```text
Cycle 1: reviewer raises C01-F01; ledger records RAISED(1).
Cycle 2: reviewer reports C01-F01 as REPAIR NOT DEMONSTRATED.
```

With both cycles valid, the controller reported `STALLED`.

I then invalidated only cycle 1’s target hash. Cycle 2 remained valid and still contained the recurrence in both its raw and structured review.

The controller exited 0 and printed:

```text
cycle-01 INVALID
cycle-02 VALID -> n=1

cycle-02 1 finding(s): C01-F01
every recorded finding is accounted for in the ledger

OPEN_1      0
DISPUTED_1  0
RESOLVED_1  0

LOOP_STATUS: CONVERGED
```

Finding:

A finding explicitly reported by a valid review can disappear from all lifecycle sets while the controller claims it is accounted for.

Ignoring the invalid originating event is required. Treating the surviving valid recurrence as satisfied merely because a ledger key exists is not. The valid reviewer result still reports an unresolved defect, yet the controller derives convergence from its absence.

Required correction:

Reconcile valid review findings with effective lifecycle states, not merely ledger-key membership.

If a valid recurrence has no authoritative originating state, refuse calculation and identify the inconsistency, or apply an explicitly defined reconstruction rule that preserves the persistent identifier and the valid review’s unresolved result. Do not infer resolution or zero findings.

Add the two-cycle reproduction above and require that invalidating the origin cannot turn a valid unresolved recurrence into convergence.

---

Finding ID: C01-F07

Class: CONTRADICTORY IMPLEMENTATION MAPPING

Requirement ID: Evidence schema, cycle-directory identity; protocol MC-2 check 7; §6, cycle-based state calculation.

Evidence:

In [validate_cycle.py](/C:/EpistemicOS/epistemicos/scripts/validate_cycle.py:325), check 7 tests required-field presence and whether sibling targets declare the same cycle number. It does not verify that the target’s cycle agrees with its directory or that its `run_id` agrees with its containing run.

Meanwhile:

- `cycle_projection.cycle_dirs()` derives cycle numbers from directory names.
- `_governing_problems()` selects the effective pin history using `target["cycle"]`.
- `cmd_record()` writes the structured finding record’s cycle from `target.json`.

I tested the mismatches independently on passing fixtures, updating the target hash and input binding each time:

```text
Directory cycle-01, target cycle 2:
MC-2 exit 0; checks 1–10 PASS.

Containing run T-001, target run_id ANOTHER-RUN:
MC-2 exit 0; checks 1–10 PASS.
```

Finding:

The same accepted evidence can have different identities depending on which component reads it.

A directory can count as cycle 1 for event projection while selecting cycle 2’s governing pins during validation. Separately, a target can claim another run while being validated against the containing run’s metadata.

Sibling uniqueness does not establish identity consistency. This discrepancy can change which governing conditions and lifecycle events a supposedly valid cycle represents.

Required correction:

Validate the relationship between the directory, target, containing review, and run metadata. Require an allowed cycle number matching `cycle-NN`, matching run identity, and matching review type.

Use the validated identity consistently for governing-pin selection, findings capture, and event projection.

Add independent controls for each mismatch, including a cycle-number mismatch across a pin-amendment boundary.

---

Finding ID: C01-F08

Class: MISSING REQUIREMENT

Requirement ID: Protocol §0.1, governing protocol must be committed before a run begins and identified by its exact commit and hash.

Evidence:

In [run_review.py](/C:/EpistemicOS/epistemicos/scripts/run_review.py:217), `cmd_init()` obtains the repository’s current `HEAD` and records it as `protocol_commit`. It hashes the protocol from the working tree.

It does not verify that the protocol exists at that commit or that the committed blob matches the recorded protocol hash.

I created a fixture with a passing bootstrap approval, changed `specs/protocol.md` without committing it, and initialized an ordinary run without `--bootstrap-exempt`.

Initialization exited 0 and wrote `run.json`.

I then retrieved:

```text
<recorded protocol_commit>:specs/protocol.md
```

from Git and hashed those bytes. That digest did not equal the recorded protocol digest:

```text
PROTOCOL COMMIT HASH AGREES False
```

Finding:

A real run can begin under uncommitted protocol bytes while its record claims a commit containing different bytes.

The recorded commit and hash therefore do not identify one authoritative governing version. Recording an existing `HEAD` satisfies neither the committed-protocol prerequisite nor the relationship between the protocol path, commit, and hash.

Required correction:

Before creating the run record, resolve the protocol blob at the proposed governing commit and verify that its hash equals the exact bytes being pinned. Refuse an untracked protocol or a modified protocol version absent from that commit.

Add controls for a committed matching protocol, a modified tracked protocol, an untracked protocol, and a protocol absent from the recorded commit. Unrelated working-tree changes need not prevent initialization.

---

For **B02-F04**, the stated repair is demonstrated at the evidence strength requested by the brief. All three `capture-log.json` writes use `write_lf_atomic()`. The hash-matching frozen runner suite passed its structural control and its three behavioural primitive controls: successful LF writing, preservation of the prior generation after an injected partial-write failure, and complete replacement with staging cleanup. Its publication-recovery controls also passed. This establishes the stated structural and primitive-level evidence; it does not establish exhaustive crash or concurrent-writer safety.

For the other four requested repairs:

- **B01-F02:** the latest-fourth-boundary control passes, but historical-boundary handling remains defective as recorded above.
- **B01-F07:** malformed and invented target governing sets are rejected, but artifact verification and validation of the replayed history remain incomplete.
- **B01-F11:** command-side refusal passes, but existing-history state replay still accepts the invalid closure.
- **B01-F14:** missing-file refusal passes, but missing classification still permits an unqualified protocol outcome.

The isolated reproductions are preserved in [bootstrap002_review_checks.py](/C:/EpistemicOS/epistemicos/_probe/bootstrap002_review_checks.py). No reviewed production artifact or authoritative run ledger was changed.

**This review makes no claim of convergence.**
