TARGET_SHA256 `98824d136395e83c86289e8cda20f56a43478cf96f30d0ff9a07c4f59f36f49a`
The target, eleven component snapshots, pinned protocol, auxiliary manifest, preserved sources, and observed-run record match their recorded hashes. All five execution-layer control suites passed independent reruns, as did the approval-package and gold-runner suites. The full mutation probe was not run.
Finding ID: D01-F01
Class: MISSING REQUIREMENT
Requirement ID: MC-2 authoritative-finding accounting; protocol §6 boundary-specific finding sets and convergence
Evidence:
In [loop_state.py (line 645)](/C:/EpistemicOS/epistemicos/scripts/loop_state.py:645), the stateless-finding check replays history over `set(valid)`, including cycles later than the review that reported the finding. Boundary calculation subsequently uses only `valid[:n]`.
An isolated fixture contained two MC-2-valid cycles. Cycle 01 reported one new finding; cycle 02 explicitly reported zero. With the ledger recording `RAISED(1)`, the controller returned `STALLED`. Changing only that history event to `RAISED(2)`, while retaining `cycle_raised: 1` and the unchanged reviewer evidence, produced exit 0 and:

```
cycle-01  1 finding(s): D01-F01
every recorded finding is accounted for in the ledger
and every one of them has a state the valid cycles produce

n=1 (cycle-01) OPEN 0 DISPUTED 0 RESOLVED 0 -> CONVERGED
LOOP_STATUS: CONVERGED
```

Finding:
A finding reported by an authoritative review can disappear from its own cycle boundary because the reconciliation check accepts a state established only in a later cycle. The controller consequently declares convergence at a boundary whose reviewer reported an unresolved finding.
This differs from a legitimate convergence followed by a later reopening: here, the original boundary already reports the finding. Reporting the later cycle as an unauthorized continuation does not correct the false original outcome.
Required correction:
Before evaluating each boundary, require every finding reported by valid reviews through that boundary to have an authoritative state using only those cycles. Refuse contradictory originating-cycle metadata and history rather than allowing a later `RAISED` event to satisfy an earlier review. Add a control retaining the original reviewer evidence while moving only the raising event to a later valid cycle; require refusal without `LOOP_STATUS`.
Previously open repairs

* C02-F08 — demonstrated for the reported defects. Check 14 compares the complete preserved patch with a regenerated patch, including an empty expected change set. The runner controls exercise substituted patches, altered paths, omitted duplicate-blob changes, nonempty patches against empty changes, and altered hunk bodies under correct headers. The suite passed. This establishes the implemented patch-equality rule, without establishing a full mutation-probe run.
* C03-F02 — demonstrated for the reported defects. `manifest_provenance` fetches committed manifest and approval bytes and compares them with the consumed files. Failed queries refuse. The ignored-untracked, staged-only, committed-positive, and unreadable-repository controls passed.

These assessments provide external development evidence; they do not change BOOTSTRAP-002’s terminal result or ledger states.
Implementer-disclosed defects

* SELF-F01 — partially repaired; closure not supported. Missing and unparseable ledgers now refuse. However, a readable ledger containing `{"findings": {}}` beside a valid review reporting a finding still produces an approval package with exit 0. The controller’s omission error is quoted, but the unresolved-findings section says “None” and its coverage item is marked present. I reproduced this. Reconcile findings before asserting empty categories, and return `CANNOT_ESTABLISH` when that reconciliation fails.
* SELF-F02 — repair not demonstrated as claimed. The preserved recovery source runs `git checkout -- <path>`, which restores from the index, not HEAD. In an isolated fixture with unchanged HEAD, matching mutated working bytes, and different staged bytes, recovery returned 0, restored the staged bytes, deleted the sentinel, and claimed restoration from HEAD. Recovery must explicitly establish the restoration source and handle intervening index changes. The disabled-check window also remains open until recovery runs.
* SELF-F03 — the stated repair is supported. Supplemental live-source inspection confirms that candidate and baseline both call `apply_variants`, with an existing-gold-match guard. The variant-bearing self-comparison control passed. This does not validate the historical improvement figures or constitute frozen-component approval of `gold_runner.py`.

The claim that none of these defects can produce a false green is too broad: SELF-F02 concerns passing suites while checks are disabled, and SELF-F01 can still falsely present an empty findings category.
Earlier repairs
No recurrence of the nineteen resolved findings’ stated reproductions was established. Source inspection and passing controls support their transition, budget, pin-history, classification, identity, capture-recovery, snapshot, evidence-binding, and historical-grammar repairs. D01-F01 identifies an additional boundary-accounting gap adjacent to C01-F06; the earlier invalid-origin refusal itself still holds. General mutation sensitivity remains unverified.
This review did not converge. D01-F01 remains actionable, and SELF-F01 and SELF-F02 are not demonstrated closed. No authoritative protocol outcome is claimed for this development-evidence run.
