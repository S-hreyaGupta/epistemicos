TARGET_SHA256: `5a0cd07cc17a409769421df55d2236d1942317c1888689315c2c037580d52200`
The target digest and all eleven preserved component digests match. Their working copies also match.
Finding ID: D02-F01
Status: REPAIR NOT DEMONSTRATED
Evidence:
In `scripts/findings_format.py:235`, the signal net runs only when `found` is empty. The new malformed declarations covered by this repair remain invisible when another finding parses successfully. For example, prepend the target hash to:

```
Finding ID: D03-F90
Class: UNTESTED RULE
Evidence: First defect.
Finding: First rule lacks coverage.
Required correction: Add coverage.

Finding-ID D03-F91
Class: UNTESTED RULE
Evidence: Second defect.
Finding: Second rule lacks coverage.
Required correction: Add coverage.
```

Source tracing establishes that:

* Both header passes recognize only `D03-F90`; `Finding-ID` matches neither.
* The first `Class:` supplies one structured finding.
* The signal net is skipped because that finding exists.
* Extraction produces one finding without a parsing problem; `capture_validity(..., zero_asserted=False)` consequently accepts the capture.

Finding:
The reference case is repaired, but the declaration safeguard remains incomplete. The same malformed declaration rejected in isolation can disappear in a mixed review. This also exposes the safeguard failure described by the earlier B02-F01 repair.
Required correction:
Reconcile declaration signals against recognized finding blocks even when some findings parse. Preserve acceptance of prose references. Add mixed-review controls containing a canonical finding followed by each malformed declaration already tested in isolation.
Repair assessments:

* SELF-F01: The stated third repair is supported by source inspection and preserved execution evidence. The package obtains the controller's governing-boundary sets instead of grouping cached ledger states, and refuses an unsuccessful or unreadable controller result. The preserved run records both the resolved baseline and invalidated-demonstration control passing.
* D01-F01: The boundary-limited replay and originating-cycle contradiction checks remain present. I found no regression in those repairs.
* SELF-F02 and SELF-F03: No new contrary evidence established here. Their prior assessments retain their stated limits; this review adds no fresh execution verification.

One additional interface issue is visible: `loop_state.py:592` returns prose with exit 0 when every cycle is invalid, even with `--json`. The package rejects that unreadable result, so this path does not recreate SELF-F01's false clean package. It should nevertheless return a defined JSON result or an explicit failure.
I could not independently execute the Python controls: the available Python commands failed to launch, and WSL access was denied. The findings above distinguish source analysis from the preserved run's observations; the mutation probe was not run.
This review does not claim convergence.
