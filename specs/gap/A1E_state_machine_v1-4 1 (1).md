# A.1-E State Machine v1.4 — EpistemicOS

**Version:** `A1E-SM-1.4`. **Form:** narrow versioned amendment/addendum to `A1E-SM-1.3`. **Relationship to v1.3 (explicit):** every state, event, transition, review
path, candidate-universe rule, epoch rule, reopening rule, verification rule,
revision-protection rule, invariant (I-SM-*), and test of `A1E-SM-1.3` is
carried UNCHANGED except the exactly-enumerated modifications below
(namespaced family `MI-*`; no v1.3 ID altered or reused).

Specifically, `A1E-SM-1.4` supersedes the unconditional candidate-terminal
semantics of `CREATE_GAP_RECORD` and `ATTACH_RESTATEMENT` in the carried
candidate transition table and amends the candidate-closure portion of
`I-SM-25` as defined in MI-22/MI-23, and supersedes the carried candidate-state
field requirements where they conflict with the frozen `A1E-GS-1.4`
candidate representation as defined in MI-24. All other portions of those carried
rules remain unchanged. This amendment resolves exactly one newly exposed lifecycle problem: **MULTI-INSTANCE_CANDIDATE_ROUTING**.
**Amendment record:** "Multi-instance routing amendment. A1E-SM-1.4 changes candidate routing from one terminal routing action per candidate to one terminal routing obligation per frozen Step-11 extraction_instance_id. The original candidate remains one lifecycle object and closes only after all instances are terminally routed as CREATED or ATTACHED. Routing review is nonterminal. Monotonic state_revision and stale-request rejection remain unchanged; parallel routing is logically commutative but mutations are serialized through revision protection. No detection, extraction, identity, candidate-universe, verification, or canonical schema semantics are otherwise changed. Concrete per-instance routing representation remains owned by the Gap Object Schema."
**Supersession note (same version, pre-freeze):** this issuance replaces the interim 11A-built v1.4 draft. Deltas from that draft, conceded: the draft's Step-4-defined "routing-disposition ledger" was exactly the canonical-representation invention this amendment prohibits and is REMOVED — per-instance routing representation is declared as a schema dependency instead; the conceptual instance-status vocabulary {UNROUTED, ROUTING_REVIEW_OPEN, CREATED, ATTACHED} is adopted; the concurrency model is corrected to serialized-by-revision with the normative stale-retry example; the test suite was initially expanded to twenty-two rows and is now expanded to twenty-eight rows to cover the GS-1.4 candidate-state field synchronization;
; the interim draft's final status changed to the schema-dependency form;
that dependency is now satisfied by frozen A1E-GS-1.4 as defined in
MI-18/MI-19/MI-24.

## MI-1 Problem

Frozen upstream behavior now permits: (A) Step-10 `CD-EMIT-12` — one compound candidate may contain multiple independently asserted deficiency propositions; (B) Step-6 `DP-CROSS-3` — independent deficiency propositions MUST remain separate. Step 11 may therefore lawfully produce candidate C1 → extraction instances I1, I2, I3, each requiring independent Step-12 routing. The v1.3-effective rule (1 candidate → 1 CREATE_GAP_RECORD or ATTACH_RESTATEMENT → closed) is insufficient. Required: 1 candidate → N extracted instances → N independent routing obligations → candidate closes only after every instance is terminally resolved.

## MI-2 One candidate; no fission

The original Step-10 candidate remains ONE lifecycle object. Explicitly prohibited: candidate fission; `child_candidate_id`; `subcandidate_id`; synthetic candidates per extracted instance; duplicate candidate creation; any change to candidate-universe counts. The routing unit is **`candidate_id` + `extraction_instance_id`** — never a new candidate.

## MI-3 Frozen extraction-instance set

After Step 11 emits `EXTRACTION_COMPLETE`, the associated Step-11 bundle defines the frozen set **I(C) = {extraction_instance_id_1 … extraction_instance_id_N}**, immutable for the current routing cycle. Step 12 MUST route exactly this set and MUST NOT add, delete, merge, replace, or semantically modify instances. Any correction requires the existing lawful review/reopen mechanism — never silent Step-12 mutation.

## MI-4 Routing target and payload

Step-12 routing events are amended so the routing target is explicitly `candidate_id` + `extraction_instance_id`. A routing request includes at minimum: `candidate_id` · `extraction_instance_id` · `expected_current_state` · `expected_state_revision` · Step-11 extraction bundle reference/digest · routing payload. The `extraction_instance_id` must exist in I(C); an unknown instance → deterministic rejection (`rejected_unknown_instance`); a request lacking the instance target → deterministic rejection (`rejected_incomplete_routing_target`). These are lifecycle-behavior rejection labels only — no concrete storage field is invented where the Gap Object Schema does not already define it (MI-18).

## MI-5 Instance routing statuses (conceptual)

Per extraction instance, the conceptual routing status is exactly one of: **UNROUTED · ROUTING_REVIEW_OPEN · CREATED · ATTACHED**. Only **CREATED** and **ATTACHED** are TERMINAL routing dispositions. **ROUTING_REVIEW_OPEN is explicitly NONTERMINAL** — routing review is never a terminal disposition. These are lifecycle statuses whose canonical representation is schema-owned (MI-18/MI-19).

## MI-6 CREATE_GAP_RECORD (per extraction instance)

Amended from candidate-terminal to PER-EXTRACTION-INSTANCE behavior. `CREATE_GAP_RECORD(Ii)` must: 1. consume exactly one `extraction_instance_id`; 2. create exactly one canonical gap record (record-side creation semantics unchanged from the carried layer); 3. mark Ii terminally routed as CREATED; 4. preserve every sibling instance's routing status; 5. NOT close the parent candidate unless all extraction instances are terminally routed. The same `extraction_instance_id` may never create more than one gap record.

## MI-7 ATTACH_RESTATEMENT (per extraction instance)

Amended analogously. `ATTACH_RESTATEMENT(Ii, Gx)` must: 1. consume exactly one `extraction_instance_id`; 2. attach exactly that extracted instance to target Gx under Step-9 / Step-12 identity rules (all v1.3 target-state, epoch, and revision-bump legality unchanged); 3. mark Ii terminally routed as ATTACHED; 4. preserve sibling routing statuses; 5. NOT close the parent candidate unless every instance is terminally routed. The same `extraction_instance_id` may not subsequently CREATE a gap record.

## MI-8 Mutually exclusive terminal outcome

For every instance Ii, exactly one of {CREATED, ATTACHED} may eventually hold. Forbidden: Ii → CREATED and ATTACHED; Ii → CREATED twice; Ii → ATTACHED to G1 and G2; Ii → silently omitted; Ii → automatically merged with sibling Ij.

## MI-9 Mixed routing (normative)

Mixed outcomes are lawful. Normative example: C1 with I1, I2, I3 → I1 CREATE_GAP_RECORD → G1; I2 ATTACH_RESTATEMENT → G7; I3 CREATE_GAP_RECORD → G2. The candidate remains unresolved until all three routing obligations are terminally completed; then and only then C1 → `closed`.

## MI-10 Candidate closure predicate (MUST-FREEZE invariant)

The old effective rule (first successful CREATE or ATTACH → candidate closed) is REPLACED by: **CANDIDATE_ROUTING_COMPLETE(C)** iff for every `extraction_instance_id` Ii ∈ I(C): routing_status(Ii) ∈ {CREATED, ATTACHED} AND no Ii is UNROUTED or ROUTING_REVIEW_OPEN. Only if CANDIDATE_ROUTING_COMPLETE(C) = TRUE may the parent candidate transition `gap_resolving` → `closed`.

## MI-11 Single-instance backward compatibility

For N = 1, behavior is equivalent to `A1E-SM-1.3`: C1 with I1 → CREATE_GAP_RECORD → no remaining obligations → C1 `closed`; likewise I1 → ATTACH_RESTATEMENT → C1 `closed`. The amendment changes nothing for ordinary single-instance candidates except making `extraction_instance_id` explicit.

## MI-12 Routing review (reuse; nonterminal)

If an instance cannot yet be routed: Ii → ROUTING_REVIEW_OPEN; the parent candidate must NOT close; already-routed siblings remain routed (example: I1 CREATED, I2 ROUTING_REVIEW_OPEN, I3 ATTACHED → candidate unresolved). When review resolves I2 to CREATED or ATTACHED, the closure predicate is re-evaluated. The EXISTING routing-review State Machine behavior is reused: the candidate occupies the existing `routing_review_required` path while any instance holds ROUTING_REVIEW_OPEN, returning to `gap_resolving` on resolution — the frozen vocabulary expresses instance-level review without any new state, so no new state is created and no blocker arises on this point.

## MI-13 State revision

Monotonic `state_revision` is preserved unchanged; every routing mutation remains conditional on `expected_state_revision = current state_revision`; stale-request protection is never weakened.

## MI-14 Concurrency (serialized by revision)

Deterministic behavior under parallel routing — two concurrent writes against the same `state_revision` never both succeed. Normative model: candidate revision = 20; Worker A routes I1 with expected_revision=20; Worker B routes I2 with expected_revision=20. A commits first → revision 20 → 21. B's write (expected=20, actual=21) → `rejected_stale`. B reloads candidate@21 and retries I2 → revision 21 → 22. The final routing result is independent of which worker commits first, assuming lawful retries. **Frozen:** parallel routing operations are LOGICALLY COMMUTATIVE, but mutations remain SERIALIZED by `state_revision`; stale-request rejection is never weakened to enable concurrency.

## MI-15 Idempotence and conflict rejection

Idempotence key: `candidate_id` + `extraction_instance_id` + routing-outcome identity. An exact retry of an already-applied routing operation → idempotent no-op / same result — it must NOT create another gap record, create another restatement, or increment any semantic routing count twice. Conflicting second routing — CREATE then ATTACH; ATTACH then CREATE; CREATE G1 then CREATE G2; ATTACH G1 then ATTACH G2 — → deterministic rejection (`rejected_duplicate_disposition`).

## MI-16 Candidate universe unchanged

This amendment does NOT alter: Step-10 candidate detection; detection-completion attestation; `CANDIDATE_UNIVERSE_CLOSED`; candidate census; epoch logic; candidate reopening; persistence-reason spawned-candidate semantics. Per-instance routing is NOT `CANDIDATE_CREATED`; one compound candidate counts as ONE candidate throughout the candidate universe.

## MI-17 Ownership (frozen)

STEP 11 produces the frozen extraction-instance set. STEP 4 defines lifecycle legality and completion conditions for routing that set. STEP 12 performs the CREATE_GAP_RECORD / ATTACH_RESTATEMENT decisions for individual instances. STEP 9 provides the identity rules Step 12 uses. No identity logic and no extraction logic enters Step 4.

## MI-18 Gap Object Schema boundary — SATISFIED BY A1E-GS-1.4

`A1E-SM-1.4` invents NO canonical candidate fields; the frozen Gap Object Schema owns candidate representation. The previously identified schema dependency is now satisfied by frozen `A1E-GS-1.4`, which provides the canonical `gap_candidate.routing_set` representation required for per-instance routing. Step 4 consumes that representation and defines only lifecycle legality, state compatibility, routing completion, and closure semantics. No `routing_disposition_ledger`, `instance_routing[]`, `promoted_gap_ids[]`, `attached_to_gap_ids[]`, or equivalent Step-4-owned canonical representation is introduced. The exact candidate-state compatibility rules are synchronized in MI-24.

## MI-19 Frozen GS-1.4 schema interface (consumed, not designed)

`A1E-SM-1.4` consumes the frozen `A1E-GS-1.4` routing representation. For every frozen `extraction_instance_id`, Step 4 can determine: 1. whether it is UNROUTED; 2. whether ROUTING_REVIEW_OPEN; 3. whether it terminally CREATED a record; 4. whether it terminally ATTACHED to a record; 5. the corresponding `target_gap_id` where terminal; 6. whether every instance has a terminal routing outcome. Canonical field design remains Step-2 ownership. Candidate-state required/forbidden-field compatibility is defined by MI-24.

## MI-22 Explicit supersession of v1.3 routing atomicity

For `A1E-SM-1.4`, the carried v1.3 invariant `I-SM-25` is AMENDED only
with respect to candidate closure during `CREATE_GAP_RECORD` and
`ATTACH_RESTATEMENT`.

The record-side atomicity requirements of `I-SM-25` remain unchanged.

For a per-extraction-instance routing event:

### CREATE_GAP_RECORD(Ii)

The atomic transaction includes:

1. validation of `candidate_id + extraction_instance_id`;
2. validation of current state and `state_revision`;
3. creation of exactly one canonical gap record for Ii;
4. the associated processing-envelope and audit effects required by the
   carried State Machine;
5. transition of Ii to terminal routing status CREATED;
6. evaluation of `CANDIDATE_ROUTING_COMPLETE(C)`.

Candidate closure is included in that same atomic transaction ONLY IF
`CANDIDATE_ROUTING_COMPLETE(C) = TRUE` after applying the routing event.

Otherwise the parent candidate remains `gap_resolving`.

### ATTACH_RESTATEMENT(Ii, Gx)

The atomic transaction includes:

1. validation of `candidate_id + extraction_instance_id`;
2. validation of current state, target-record legality, epoch, and
   `state_revision`;
3. attachment of exactly Ii to target Gx under the carried Step-9/Step-12
   legality rules;
4. all required target-record revision and audit effects;
5. transition of Ii to terminal routing status ATTACHED;
6. evaluation of `CANDIDATE_ROUTING_COMPLETE(C)`.

Candidate closure is included in that same atomic transaction ONLY IF
`CANDIDATE_ROUTING_COMPLETE(C) = TRUE` after applying the routing event.

Otherwise the parent candidate remains `gap_resolving`.

Therefore, under `A1E-SM-1.4`:

`CREATE_GAP_RECORD` and `ATTACH_RESTATEMENT` remain atomic routing mutations,
but they are no longer unconditionally candidate-terminal.

No other `I-SM-25` atomicity requirement is changed.

## MI-23 Amended candidate transition rows

The following v1.3 candidate-transition rows are superseded for
`A1E-SM-1.4`.

| Object | Current state | Event | Condition | Next state |
|---|---|---|---|---|
| candidate | `gap_resolving` | `CREATE_GAP_RECORD(Ii)` | routing event lawful AND `CANDIDATE_ROUTING_COMPLETE(C) = FALSE` after Ii becomes CREATED | `gap_resolving` |
| candidate | `gap_resolving` | `CREATE_GAP_RECORD(Ii)` | routing event lawful AND `CANDIDATE_ROUTING_COMPLETE(C) = TRUE` after Ii becomes CREATED | `closed` |
| candidate | `gap_resolving` | `ATTACH_RESTATEMENT(Ii,Gx)` | routing event lawful AND `CANDIDATE_ROUTING_COMPLETE(C) = FALSE` after Ii becomes ATTACHED | `gap_resolving` |
| candidate | `gap_resolving` | `ATTACH_RESTATEMENT(Ii,Gx)` | routing event lawful AND `CANDIDATE_ROUTING_COMPLETE(C) = TRUE` after Ii becomes ATTACHED | `closed` |

For N = 1, the closure predicate becomes TRUE after the sole lawful
CREATE/ATTACH event, reproducing the v1.3 terminal behavior.

For N > 1, intermediate successful CREATE/ATTACH events leave the parent
candidate in `gap_resolving`.

The carried v1.3 unconditional rows:

`gap_resolving + CREATE_GAP_RECORD → closed`

and

`gap_resolving + ATTACH_RESTATEMENT → closed`

are therefore replaced by the four conditional rows above.

## MI-24 GS-1.4 candidate-state field synchronization

The carried v1.3 candidate-state field requirements are superseded where
they conflict with the frozen `A1E-GS-1.4` candidate representation.

For `A1E-SM-1.4`, the required/forbidden candidate-side fields are:

### detected

- `boundary_state` absent;
- `routing_outcome` absent;
- `routing_set` absent.

### gap_extracting

- `boundary_state = GAP`;
- `routing_outcome` absent;
- `routing_set` absent.

### gap_resolving

- `boundary_state = GAP`;
- `routing_outcome` absent;
- `routing_set` present;
- `routing_set` contains the complete frozen Step-11 extraction-instance set;
- at least one instance is nonterminal
  (`UNROUTED` or `ROUTING_REVIEW_OPEN`),
  unless the current atomic routing transaction makes
  `CANDIDATE_ROUTING_COMPLETE(C) = TRUE` and closes the candidate.

### routing_review_required

- `boundary_state = GAP`;
- `routing_outcome` absent;
- `routing_set` present;
- at least one routing instance has
  `routing_status = ROUTING_REVIEW_OPEN`;
- candidate remains nonterminal.

### boundary_review_required

- `boundary_state = UNCERTAIN`;
- required uncertainty payload present;
- `routing_outcome = uncertain_queued`;
- `routing_set` absent;
- candidate remains on the existing nonterminal/suspended boundary-review path.

### closed — non-GAP

- `routing_outcome = rejected_non_gap`;
- `routing_set` absent.

### closed — GAP

- `boundary_state = GAP`;
- candidate-level `routing_outcome` absent;
- `routing_set` present;
- every routing instance has
  `routing_status ∈ {CREATED, ATTACHED}`;
- therefore `CANDIDATE_ROUTING_COMPLETE(C) = TRUE`.

The former GAP-side candidate-level values
`routing_outcome = promoted` and
`routing_outcome = attached_as_restatement`
are not lawful under `A1E-GS-1.4`.

Per-instance terminal routing is represented exclusively through
`gap_candidate.routing_set.instances[]`.

This amendment changes representation requirements only.
It does not change any lifecycle transition, extraction rule,
identity rule, candidate-universe rule, or routing decision.

## MI-20 Amendment tests (28 additive deterministic tests; no unaffected v1.3 test altered)

SM-MI-01 · N=1; I1 CREATE → C `closed`. 
SM-MI-02 · N=1; I1 ATTACH → C `closed`. 
SM-MI-03 · N=2; I1 CREATE → I1 terminal; I2 UNROUTED → C remains `gap_resolving`. 
SM-MI-04 · then I2 CREATE → both terminal → C `closed`. 
SM-MI-05 · I1 CREATE; I2 ATTACH → mixed routing lawful → C `closed` after both. 
SM-MI-06 · N=3; CREATE / ATTACH / CREATE → exactly three terminal dispositions → one parent close. 
SM-MI-07 · duplicate identical CREATE for I1 → idempotent no-op → one record only. 
SM-MI-08 · CREATE I1 then ATTACH I1 → `rejected_duplicate_disposition`. 
SM-MI-09 · ATTACH I1→G1 then ATTACH I1→G2 → `rejected_duplicate_disposition`. 
SM-MI-10 · I1 CREATED; I2 ROUTING_REVIEW_OPEN → C cannot close (predicate false). 
SM-MI-11 · review resolves I2 → ATTACHED → closure predicate re-evaluated → C `closed`. 
SM-MI-12 · unknown `extraction_instance_id` (∉ I(C)) → `rejected_unknown_instance`. 
SM-MI-13 · routing request against stale `state_revision` → `rejected_stale`. 
SM-MI-14 · parallel I1/I2 requests from the same revision → one succeeds; the other `rejected_stale`; reload + retry succeeds → final disposition set deterministic. 
SM-MI-15 · routing order I1-then-I2 vs I2-then-I1 → same terminal routing set and same candidate terminal state. 
SM-MI-16 · Step 12 attempts to alter the frozen Step-11 instance set → prohibited; review/reopen pathway required. 
SM-MI-17 · candidate has one unrouted instance; close request → rejected. 
SM-MI-18 · per-instance routing of a compound candidate → candidate census remains ONE candidate.

SM-MI-19 · N=2; I1 CREATE → record G1 is created atomically; I1 becomes CREATED; closure predicate remains false because I2 is UNROUTED → parent candidate remains `gap_resolving`.

SM-MI-20 · N=2; I1 CREATED; I2 ATTACH → target-record mutation + I2 ATTACHED occur atomically; closure predicate becomes true → parent candidate closes in the same routing transaction.

SM-MI-21 · carried v1.3 unconditional `gap_resolving + CREATE_GAP_RECORD → closed` behavior is attempted while another extraction instance remains UNROUTED → prohibited by MI-10/MI-23; candidate remains `gap_resolving`.

SM-MI-22 · carried v1.3 unconditional `gap_resolving + ATTACH_RESTATEMENT → closed` behavior is attempted while another extraction instance remains ROUTING_REVIEW_OPEN → prohibited by MI-10/MI-23; candidate does not close.

SM-MI-23 · candidate in `gap_extracting` → `boundary_state = GAP`; `routing_outcome` absent; `routing_set` absent.

SM-MI-24 · candidate enters `gap_resolving` after `EXTRACTION_COMPLETE` → `boundary_state = GAP`; `routing_outcome` absent; `routing_set` present and contains the complete frozen Step-11 extraction-instance set.

SM-MI-25 · candidate in `routing_review_required` → `boundary_state = GAP`; `routing_outcome` absent; `routing_set` present; at least one instance has `routing_status = ROUTING_REVIEW_OPEN`; candidate remains nonterminal.

SM-MI-26 · candidate in `boundary_review_required` → `boundary_state = UNCERTAIN`; required uncertainty payload present; `routing_outcome = uncertain_queued`; `routing_set` absent.

SM-MI-27 · closed non-GAP candidate → `routing_outcome = rejected_non_gap`; `routing_set` absent.

SM-MI-28 · closed GAP candidate → `boundary_state = GAP`; candidate-level `routing_outcome` absent; `routing_set` present; every instance has `routing_status ∈ {CREATED, ATTACHED}`.

## MI-21 Freeze check


| Check | Status | Evidence |
|---|---|---|
| **ARCHITECTURE** | | |
| parent candidate remains one lifecycle object | PASS | MI-2; SM-MI-18 |
| no candidate fission | PASS | MI-2 prohibition list |
| extraction_instance_id is the routing target | PASS | MI-4; SM-MI-12 |
| mixed CREATE/ATTACH outcomes supported | PASS | MI-9; SM-MI-05/06 |
| routing review is nonterminal | PASS | MI-5; MI-12; SM-MI-10/11 |
| only CREATED/ATTACHED are terminal | PASS | MI-5; MI-8 |
| candidate closes only after all instances terminal | PASS | MI-10; SM-MI-03/04/17 |
| carried I-SM-25 candidate-closure semantics explicitly amended | PASS | MI-22 |
| old unconditional CREATE_GAP_RECORD → closed row explicitly superseded | PASS | MI-23; SM-MI-19/21 |
| old unconditional ATTACH_RESTATEMENT → closed row explicitly superseded | PASS | MI-23; SM-MI-20/22 |
| record-side atomicity preserved while candidate closure is conditional | PASS | MI-22 |
| **DETERMINISM** | | |
| duplicate routing is idempotent | PASS | MI-15; SM-MI-07 |
| conflicting duplicate rejected | PASS | MI-15; SM-MI-08/09 |
| stale state_revision protection unchanged | PASS | MI-13; SM-MI-13 |
| concurrent same-revision writes do not both commit | PASS | MI-14; SM-MI-14 |
| retry after stale rejection is deterministic | PASS | MI-14 worked model |
| routing order does not affect final semantic disposition set | PASS | MI-14/MI-15; SM-MI-15 |
| **OWNERSHIP** | | |
| Step 4 performs no extraction | PASS | MI-17 |
| Step 4 performs no identity comparison | PASS | MI-17 |
| Step 4 creates no Step-2 schema fields | PASS | MI-18 prohibition; MI-19 |
| Step 4 modifies no candidate-universe semantics | PASS | MI-16; SM-MI-18 |
| Step 4 performs no Step-13 verification | PASS | scope; carried v1.3 rules |
| **BACKWARD COMPATIBILITY** | | |
| N=1 behaves as A1E-SM-1.3 | PASS | MI-11; SM-MI-01/02 |
| existing states unchanged unless explicitly amended | PASS | addendum form; MI-12 reuse |
| existing event names preserved where possible | PASS | only CREATE_GAP_RECORD/ATTACH_RESTATEMENT payload-amended; no renames |
| **SCHEMA DEPENDENCY** | | |
| lifecycle requirements on per-instance routing representation explicit | PASS | MI-19 six determinations |
| concrete canonical representation remains Step-2 ownership | PASS | MI-18 |
| frozen GS-1.4 satisfies the per-instance routing representation required by SM-1.4 | PASS | MI-18; MI-19 |
| candidate-state required/forbidden fields synchronized with GS-1.4 | PASS | MI-24 |
| old GAP-side promoted / attached_as_restatement candidate-level routing_outcome values superseded | PASS | MI-24 |
| closed GAP candidate requires complete terminal routing_set | PASS | MI-10; MI-24 |

**A1E-SM-1.4 is internally coherent and synchronized with frozen
`A1E-GS-1.4`. The previously blocking schema dependency is satisfied.
READY FOR INDEPENDENT FREEZE AUDIT.**


