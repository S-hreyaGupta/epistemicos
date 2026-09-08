Worked for 30s

The five decisions are incorporated below as enforceable protocol rules. The final verification table checks both the new controls and preservation of every element in the original workflow.

Claude–Codex Minimal Implementation and Review Workflow

0. Protocol governance and baseline

0.1 Governing protocol

This workflow is a version-controlled governing specification.

Before a run begins, record:

PROTOCOL_PATH
PROTOCOL_VERSION
PROTOCOL_COMMIT
PROTOCOL_HASH

The authoritative protocol must be committed to git. Slack, chat history, or other transient communication channels are not authoritative copies.

Every implementation run must reference the exact protocol version and commit used.

---

0.2 Freeze the specification and baseline

Record:

SPEC_PATH
SPEC_VERSION
SPEC_HASH

BASELINE_COMMIT
BASELINE_TEST_RESULT
BASELINE_GOLD_RESULT
GOLD_SET_VERSION
GOLD_SET_HASH

If no executable implementation exists yet:

BASELINE_COMMIT: NONE
BASELINE_TEST_RESULT: NOT_APPLICABLE
BASELINE_GOLD_RESULT: NOT_APPLICABLE
REASON: no executable baseline implementation

A baseline result must never be manufactured retrospectively.

Where an executable baseline exists, the frozen Gold Set must be run before implementation.

---

1. Claude audits frozen spec → current code

Claude audits every implementable requirement in the frozen specification against the current implementation.

Each requirement receives exactly one disposition:

DONE
PARTIAL
MISSING
CONFLICT

Claude produces:

SPEC → CODE → TEST mapping

For each requirement:

Requirement ID:
Spec location:
Normative requirement:

Disposition:
DONE | PARTIAL | MISSING | CONFLICT

Current code:
Current tests:

Required implementation delta:
Required deterministic/conformance test:
Dependencies/blockers:

Claude then produces a bounded implementation plan containing only changes justified by the audit.

No implementation occurs at this stage.

---

2. Plan review loop — Claude ↔ Codex

Maximum:

4 VALID CODEX REVIEW CYCLES

Only cycles that pass the MC-2 conformance gate count toward this maximum.

---

2.1 Freeze the review target for every cycle

Every cycle receives its own directory.

Example:

plan-review/
cycle-01/
cycle-02/
cycle-03/
cycle-04/

Before Codex reviews the plan, capture:

target
target.sha256
codex-input.md

"target" identifies or contains the exact plan artifact reviewed in that cycle.

After Codex returns, capture:

codex-output-raw.md

No repair may occur before the raw Codex output has been captured.

A repaired plan creates a new target and therefore a new review cycle.

---

3. Mandatory controls for every Codex review cycle

MC-1 — Codex findings cannot be modified by Claude

The authoritative Codex review evidence must be technically separated from the implementing agent.

The review runner writes:

codex-output-raw.md
findings.json

After capture:

Claude/implementing agent:
READ = permitted
WRITE = denied
DELETE = denied

The authoritative review directory must therefore be protected by filesystem permissions, repository permissions, an append-only evidence store, or an equivalent technical boundary.

Claude may write separately:

claude-response.md
repaired-target

Claude may not overwrite the authoritative Codex findings.

Enforcement status

Each run must record:

MC1_ENFORCEMENT:
TECHNICALLY_ENFORCED
or
CONVENTION_ONLY

If the infrastructure cannot enforce write protection, the protocol must state:

MC1_ENFORCEMENT: CONVENTION_ONLY

In that case, statements such as “Codex findings are immutable” are prohibited. The control is procedural rather than guaranteed.

---

MC-2 — Per-cycle evidence completeness must be mechanically checked

Every completed review cycle must contain:

target
target.sha256
codex-input.md
codex-output-raw.md

A deterministic conformance check must verify:

1. target exists
2. target.sha256 exists
3. codex-input.md exists
4. codex-output-raw.md exists

5. required files are non-empty

6. SHA256(target) == value recorded in target.sha256

7. cycle identifier is unique

8. where target references a git commit:
referenced commit exists

9. where target references additional hashed artifacts:
recorded hashes match those artifacts

Result:

MC2_CONFORMANCE:
PASS | FAIL

If:

MC2_CONFORMANCE = FAIL

then:

REVIEW_CYCLE_STATUS = INVALID

An invalid cycle:

- cannot support a Codex finding;
- cannot count toward "CONVERGED";
- cannot count toward "STALLED";
- cannot count toward "MAX_4_REACHED";
- cannot count toward the four-cycle maximum.

The evidence failure must be repaired and the review cycle rerun.

---

MC-3 — Gold Set performance is comparative where a baseline exists

Where executable baseline code exists, preserve Gold Set results:

BEFORE implementation
AND
AFTER final implementation

using the same frozen Gold Set version/hash.

Where no executable baseline exists:

BASELINE_GOLD_RESULT = NOT_APPLICABLE

and the candidate is evaluated against predefined Gold acceptance criteria.

---

4. Codex reviews the implementation plan

Codex reviews the exact frozen plan against the frozen specification.

Codex uses the following closed finding vocabulary:

MISSING REQUIREMENT

WRONG OWNERSHIP

NONDETERMINISTIC WHERE D POSSIBLE

SEMANTIC STEP TOO BROAD

UNTESTED RULE

CONTRADICTORY IMPLEMENTATION MAPPING

Every finding receives a persistent identifier.

Example:

Finding ID: C02-F03
Class: UNTESTED RULE
Requirement ID: R-B7
Evidence:
Finding:
Required correction:

The vocabulary remains unchanged across cycles so that finding sets remain comparable.

The raw Codex response is captured before summarisation, interpretation, or Claude response.

---

5. Claude responds to Codex findings

Claude must respond to every finding with exactly one disposition:

ACCEPT

or:

REJECT_WITH_REASON

ACCEPT

Claude accepts the finding and repairs the plan.

The original Codex finding remains unchanged in the authoritative review record.

Its state becomes:

RESOLVED

once the repair is demonstrated in the next review target.

---

REJECT_WITH_REASON

Claude records:

Finding ID:
Disposition: REJECT_WITH_REASON
Reason:
Spec evidence:

Claude does not erase, rewrite, or close the Codex finding.

Its state becomes:

DISPUTED

and requires human adjudication.

---

6. Mechanically determine the plan-loop state

For each valid cycle, every Codex finding has one current state:

OPEN
RESOLVED
DISPUTED

Define:

OPEN_n
= set of actionable OPEN finding IDs after cycle n

RESOLVED_NEW_n
= findings that were OPEN after cycle n-1
and became RESOLVED during cycle n

DISPUTED_NEW_n
= findings that were OPEN after cycle n-1
and became DISPUTED during cycle n

For cycle "n > 1", progress exists iff:

|OPEN_n| < |OPEN_n-1|

OR

RESOLVED_NEW_n is non-empty

OR

DISPUTED_NEW_n is non-empty

A newly recorded dispute therefore counts as progress because an unresolved finding has been converted into an explicit human-adjudication issue.

Merely re-raising an already existing dispute does not count as progress.

---

Exit A — CONVERGED

OPEN_n = ∅
AND
DISPUTED_n = ∅

Stop the automated plan loop.

Proceed to human plan review with:

LOOP_STATUS = CONVERGED

---

Exit B — STALLED

For any valid cycle "n > 1":

STALLED
IFF

|OPEN_n| >= |OPEN_n-1|

AND

RESOLVED_NEW_n = ∅

AND

DISPUTED_NEW_n = ∅

In other words, the immediately preceding valid cycle produced no reduction in open actionable findings and no previously open finding became resolved or disputed.

Stop the automated loop immediately.

Do not consume additional cycles merely because fewer than four have been used.

Proceed to human plan review with:

LOOP_STATUS = STALLED

---

Exit C — MAX_4_REACHED

If:

VALID_CYCLE_COUNT = 4

and neither "CONVERGED" nor an earlier "STALLED" exit occurred:

LOOP_STATUS = MAX_4_REACHED

Stop automated review.

---

Otherwise — CONTINUE

If:

not CONVERGED
not STALLED
VALID_CYCLE_COUNT < 4

Claude repairs the plan.

A new plan version is produced.

Return to Step 2 and create a new per-cycle review target.

---

7. Human review of the implementation plan

Human review occurs after:

CONVERGED
STALLED
or
MAX_4_REACHED

The states are not equivalent.

The review package must contain:

final plan
final plan hash

loop status
valid iteration count

SPEC → CODE → TEST mapping

resolved findings
disputes
unresolved findings

MC-1 enforcement status
MC-2 conformance results for every valid cycle

---

7.1 Disputes

A dispute is:

Codex finding
+
Claude REJECT_WITH_REASON

The human adjudicates the dispute.

---

7.2 Unresolved findings

An unresolved finding remains "OPEN".

The human determines whether it:

requires correction
is explicitly waived/accepted
or causes rejection of the plan

Disputes and unresolved findings must be presented separately.

---

7.3 Human decision

Permitted outcomes:

APPROVE
RETURN_FOR_REWORK
REJECT

If approved:

APPROVED_PLAN_HASH
APPROVAL_RECORD

are frozen.

---

8. Claude implements the approved plan

Claude implements only the exact approved plan.

Before Codex implementation review, run:

build/check
deterministic tests
conformance tests
regression tests

Mechanical or deterministic failures return directly to Claude for repair.

---

9. PLAN_DEVIATION control

A material change outside the approved plan may not be introduced silently.

If implementation requires such a change:

1. STOP implementation.

2. Record:
PLAN_DEVIATION_ID
reason
affected requirement
proposed plan change
affected code/tests

3. Do not implement the deviation.

4. Return to Step 7:
HUMAN REVIEW OF THE IMPLEMENTATION PLAN.

5. Human reviews the revised plan.

6. If approved:
freeze new APPROVED_PLAN_HASH.

7. Resume implementation only against the newly approved plan.

Therefore:

MATERIAL PLAN DEVIATION
→ MANDATORY RETURN TO HUMAN PLAN APPROVAL

A deviation cannot be legitimised retrospectively during code review.

---

10. Implementation review loop — Claude ↔ Codex

Maximum:

4 VALID CODEX REVIEW CYCLES

The same MC-1, MC-2 and loop-state rules apply.

Every cycle receives its own directory:

implementation-review/
cycle-01/
cycle-02/
cycle-03/
cycle-04/

---

10.1 Freeze the exact implementation target per cycle

Before every Codex call, capture:

target
target.sha256
codex-input.md

For implementation review, "target" must identify the exact candidate under review, including at minimum:

candidate commit
candidate tree hash
approved plan hash
exact diff identity/hash
relevant test-result identity/hash

After Codex returns:

codex-output-raw.md

is captured before Claude modifies anything.

Run the MC-2 conformance gate.

Only a passing cycle is valid.

---

11. Codex reviews the exact implementation

Codex receives:

frozen specification
approved plan
exact candidate commit/hash
exact implementation diff
relevant tests
deterministic/conformance/regression results

Codex uses the same closed finding vocabulary:

MISSING REQUIREMENT
WRONG OWNERSHIP
NONDETERMINISTIC WHERE D POSSIBLE
SEMANTIC STEP TOO BROAD
UNTESTED RULE
CONTRADICTORY IMPLEMENTATION MAPPING

The raw review is preserved through MC-1 and MC-2.

---

12. Claude responds and repairs

For every finding:

ACCEPT
→ repair implementation

or:

REJECT_WITH_REASON
→ preserve as DISPUTED

Claude cannot modify the authoritative Codex evidence where MC-1 is technically enforced.

A repair creates a new candidate and therefore a new review cycle.

---

13. Determine implementation-loop exit

Use exactly the same mechanically defined states as the plan loop:

CONVERGED
STALLED
MAX_4_REACHED
CONTINUE

No separate or subjective implementation-loop definition is permitted.

---

14. Human review of final code

Human review occurs after:

CONVERGED
STALLED
or
MAX_4_REACHED

The review package contains:

frozen specification
approved plan
candidate commit/hash

exact implementation diff
deterministic test results
conformance test results
regression test results

resolved findings
disputes
unresolved findings

loop status
valid iteration count

MC-1 enforcement status
MC-2 result for every valid cycle

any approved plan deviations

Human decision:

APPROVE
RETURN_FOR_REWORK
REJECT

If approved, freeze the exact candidate commit/hash.

---

15. Gold Set validation

15.1 Existing executable baseline

Run the same frozen Gold Set against:

BASELINE
vs
FINAL CANDIDATE

Compare at minimum:

targeted improvements
previously correct cases retained
new false positives
new false negatives
regressions
aggregate performance

Aggregate improvement does not override an unacceptable regression.

---

15.2 No executable baseline

Record:

BASELINE_GOLD_RESULT = NOT_APPLICABLE

Run the frozen Gold Set against the candidate and evaluate against predefined acceptance criteria.

---

16. Final freeze / release decision

The release evidence contains:

PROTOCOL_VERSION / COMMIT / HASH
SPEC_VERSION / HASH

APPROVED_PLAN_HASH
FINAL_CANDIDATE_COMMIT / HASH

PLAN_LOOP_STATUS
IMPLEMENTATION_LOOP_STATUS

MC1_ENFORCEMENT
MC2_CONFORMANCE_RESULTS

DISPUTE DISPOSITIONS
UNRESOLVED-FINDING DISPOSITIONS

BASELINE_GOLD_RESULT
FINAL_GOLD_RESULT
GOLD_COMPARISON

FINAL HUMAN DECISION

Only then is the capability frozen/released.

---

Minimal execution view

0. PROTOCOL + BASELINE
Commit/version protocol in git.
Freeze spec.
Freeze existing baseline tests + Gold.
If no executable baseline → mark N/A.

1. CLAUDE AUDIT + PLAN
DONE / PARTIAL / MISSING / CONFLICT
SPEC → CODE → TEST
bounded plan
deterministic/conformance tests

2. PLAN REVIEW LOOP
EACH cycle:
freeze exact target
capture exact Codex input
capture raw Codex output
enforce MC-1
run MC-2 gate

Codex reviews with closed finding vocabulary

Claude:
ACCEPT → repair
REJECT_WITH_REASON → DISPUTED

Mechanical exit:
CONVERGED
STALLED
MAX 4

3. HUMAN PLAN REVIEW
separately:
disputes
unresolved findings

approve / return / reject
freeze approved plan

4. CLAUDE IMPLEMENTS
deterministic/conformance/regression checks

MATERIAL PLAN DEVIATION
→ STOP
→ return to human plan review

5. CODE REVIEW LOOP
EACH cycle:
freeze exact candidate
capture exact Codex input
capture raw Codex output
enforce MC-1
run MC-2 gate

Codex reviews exact implementation

Claude:
ACCEPT → repair
REJECT_WITH_REASON → DISPUTED

Mechanical exit:
CONVERGED
STALLED
MAX 4

6. HUMAN CODE REVIEW

7. GOLD SET
baseline ↔ candidate if baseline exists
otherwise candidate ↔ predefined acceptance criteria

8. FINAL FREEZE / RELEASE

Verification table — changes and preservation

| ID | Required element | Source | Implemented in workflow | Verification criterion | Status |
|---|---|---|---|---|---|
| V01 | Claude audits frozen spec against current code | Original prompt | Step 1 | Audit exists before plan/implementation | PRESERVED |
| V02 | "DONE / PARTIAL / MISSING / CONFLICT" | Original prompt | Step 1 | Every implementable requirement has exactly one disposition | PRESERVED |
| V03 | "SPEC → CODE → TEST" mapping | Original prompt | Step 1 | Mapping exists for every requirement | PRESERVED |
| V04 | Add deterministic/conformance tests | Original prompt | Steps 1, 8 | Required tests specified in plan and run during implementation | PRESERVED |
| V05 | Send plan to Codex for independent assessment | Original prompt | Steps 2–4 | Every plan review has frozen target and Codex output | PRESERVED |
| V06 | Codex identifies contradictions/problems | Original prompt | Step 4 | Review uses closed finding vocabulary | PRESERVED + STRENGTHENED |
| V07 | Claude solves accepted Codex findings | Original prompt | Step 5 | "ACCEPT" finding produces repair | PRESERVED |
| V08 | Claude cannot silently dismiss Codex finding | Mandatory control | Steps 3, 5 | Only "ACCEPT" or "REJECT_WITH_REASON"; authoritative finding retained | ENFORCED |
| V09 | Maximum 3–4 iterations | Original prompt | Steps 2, 10 | Maximum explicitly fixed at 4 valid cycles | PRESERVED |
| V10 | Stop before max when review completes | Original intent | Step 6 | "CONVERGED" exits immediately | PRESERVED + CLARIFIED |
| V11 | Distinguish "CONVERGED / STALLED / MAX 4" | Prior comments | Steps 6, 13 | Three separately recorded terminal states | ENFORCED |
| V12 | "STALLED" has mechanically checkable predicate | New decision 1 | Step 6 | Formula uses open count plus newly resolved/disputed states | ADDED / ENFORCED |
| V13 | New disputes count as progress | Latest comments | Step 6 | "DISPUTED_NEW_n ≠ ∅" prevents stall | ADDED / ENFORCED |
| V14 | Re-raised existing disputes do not count as progress | Latest comments | Step 6 | Only "DISPUTED_NEW_n" counts | ADDED / ENFORCED |
| V15 | Human approves implementation plan after loop exit | Original prompt | Step 7 | Human gate occurs after any of three terminal states | PRESERVED |
| V16 | "STALLED" reaches human review | Latest comments | Steps 6–7 | Explicit transition "STALLED → Step 7" | ADDED / ENFORCED |
| V17 | "MAX 4" reaches human review without being called convergence | Prior comments | Steps 6–7 | Status remains "MAX_4_REACHED" | ENFORCED |
| V18 | Disputes and unresolved findings remain separate | Prior comments | Step 7 | Separate sections and human actions | ENFORCED |
| V19 | Human adjudicates "REJECT_WITH_REASON" disputes | Prior comments | Step 7 | Dispute requires human adjudication | ENFORCED |
| V20 | Claude implements only human-approved plan | Original prompt | Step 8 | "APPROVED_PLAN_HASH" frozen before implementation | PRESERVED + STRENGTHENED |
| V21 | Plan deviation cannot be introduced silently | Prior workflow | Step 9 | Explicit "PLAN_DEVIATION" record | PRESERVED + STRENGTHENED |
| V22 | Material plan deviation returns to human plan approval | New decision 4 | Step 9 | Mandatory stop and return to Step 7 | ADDED / ENFORCED |
| V23 | Deterministic checks before Codex code review | Original prompt | Step 8 | Build/deterministic/conformance/regression checks precede review | PRESERVED |
| V24 | Codex reviews exact implementation | Original prompt | Steps 10–11 | Exact commit/hash, diff, tests and results supplied | PRESERVED |
| V25 | Claude↔Codex code-review loop | Original prompt | Steps 10–13 | Same repair/review process repeated | PRESERVED |
| V26 | Code loop capped at 4 valid iterations | Original prompt | Step 10 | Maximum = 4 valid cycles | PRESERVED |
| V27 | Human code review after convergence or cap | Original prompt | Step 14 | Human gate after "CONVERGED", "STALLED", or "MAX_4" | PRESERVED + CLARIFIED |
| V28 | Freeze review target per cycle | Mandatory control/comments | Steps 2, 10 | Every cycle has independent target/hash | ENFORCED |
| V29 | Capture exact Codex input per cycle | Mandatory control/comments | Steps 2, 10 | "codex-input.md" required | ENFORCED |
| V30 | Capture raw Codex output per cycle | Mandatory control/comments | Steps 2, 10 | "codex-output-raw.md" required before repairs | ENFORCED |
| V31 | MC-2 is mechanically checked rather than merely documented | New decision 2 | Step 3 | Deterministic evidence conformance gate runs every cycle | ADDED / ENFORCED |
| V32 | Invalid evidence cycle does not count | New decision 2 | Step 3 | Failed MC-2 cycle excluded from all loop-state calculations | ADDED / ENFORCED |
| V33 | "target.sha256" must actually match target | Latest comments | Step 3 | SHA-256 comparison required by gate | ADDED / ENFORCED |
| V34 | Codex findings technically protected from Claude modification | New decision 3 | Step 3 | Implementing agent lacks write/delete permission to authoritative evidence | ADDED / ENFORCED WHERE SUPPORTED |
| V35 | If technical immutability is absent, claim is downgraded | New decision 3 | Step 3 | "MC1_ENFORCEMENT=CONVENTION_ONLY"; immutable claim prohibited | ADDED |
| V36 | Closed Codex finding vocabulary | Prior comments | Steps 4, 11 | Six fixed finding classes used across cycles | ENFORCED |
| V37 | Finding IDs persist across cycles | Prior control logic | Steps 4–5 | Same issue keeps same identifier | ENFORCED |
| V38 | Gold Set baseline run before implementation where possible | Mandatory control | Step 0 | Baseline Gold recorded before Step 8 | ENFORCED |
| V39 | No fake baseline when first implementation has no code | Prior comments | Steps 0, 15 | Explicit "NOT_APPLICABLE" | ENFORCED |
| V40 | Final Gold Set run after human-reviewed implementation | Original prompt | Step 15 | Frozen candidate evaluated after code review | PRESERVED |
| V41 | Gold evaluates regression, not only aggregate improvement | Prior workflow | Step 15 | Gains, retained cases, FP, FN and regressions compared | PRESERVED |
| V42 | Protocol itself committed to git | New decision 5 | Step 0 | Path/version/commit/hash required before run | ADDED / ENFORCED |
| V43 | Run references exact protocol version | New decision 5 | Steps 0, 16 | Release record contains protocol version/commit/hash | ADDED / ENFORCED |
| V44 | Final freeze/release remains human-governed | Original workflow implication | Step 16 | Final human decision recorded with evidence | PRESERVED |

Preservation verdict

Original workflow elements dropped: 0

Mandatory controls dropped: 0

Latest requested changes incorporated: 5 / 5

1. STALLED exact predicate                    ✓
2. MC-2 mechanical conformance gate           ✓
3. MC-1 technical boundary / explicit fallback ✓
4. PLAN_DEVIATION → human plan gate           ✓
5. Protocol committed/versioned in git        ✓

The resulting control chain is:

GIT-VERSIONED PROTOCOL
↓
FROZEN SPEC + BASELINE
↓
CLAUDE AUDIT / PLAN
↓
PER-CYCLE EVIDENCED CODEX LOOP
↓
CONVERGED | STALLED | MAX 4
↓
HUMAN PLAN APPROVAL
↓
CLAUDE IMPLEMENTATION
│
└── material deviation → HUMAN PLAN APPROVAL
↓
DETERMINISTIC CHECKS
↓
PER-CYCLE EVIDENCED CODEX CODE LOOP
↓
CONVERGED | STALLED | MAX 4
↓
HUMAN CODE REVIEW
↓
GOLD VALIDATION
↓
FINAL FREEZE / RELEASEOne substantive change from the prior version is worth noting: “MAX 4” now means four valid review cycles, not four Codex calls. A cycle failing the evidence-conformance gate cannot consume the review budget; otherwise MC-2 failure could itself force premature termination.
