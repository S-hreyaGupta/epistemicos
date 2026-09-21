---
document_id: citation_v3_4_gsd_pilot_task_contract
version: "1.0"
artifact_kind: pilot_task_addendum_and_manual_comparator
governing_pilot_runbook:
  artifact: PILOT_RUNBOOK_6
  sha256: df0a587c3d9d3289e57ab48f7e28e89d7edf7d5f45dc888fb1f179374d861876
governance_basis:
  artifact: authoritative_technical_spec_standard_v0.1_rc3
  sha256: e5185b132ac22e3c373fff6358538d11d21e33ce572e800190c6078bb0c2a63b
pilot_target_scope: citation_v3_4_standalone_cli_nomap_apa7_like_v1
normative_product_authority: none
---

# Citation v3.4 — GSD Pilot Task Contract / Manual Comparator

## 1. Role of this file

This file is **not** a Citation technical specification and MUST NOT create product behavior.

It has two pilot-process roles:

1. task-specific addendum to `PILOT_RUNBOOK (6)`;
2. manual comparator brief that is frozen/hashed before GSD onboarding.

The pilot runbook's sequence, independence criteria, evaluation criteria, VOID/FAIL/PASS rules, plan-manifest rules, sealing rules and recoverability test remain unchanged.

For the Citation pilot, replace only the runbook's task-specific work item and done conditions with this file.

## 2. Exact candidate package presented for freeze/pilot preparation

| Artifact | SHA-256 |
|---|---|
| `01_citation_architecture_v3.4_rc2.md` | `4a60b994845a323d5ee1170559d3f9017abf62aeaf4bc7fc0bc1992e335adb9e` |
| `02_citation_execution_conformance_v3.4_rc2.md` | `4fa95af15755c569d5a5135321a22fdfab85464c4ee92c09a8808d73318aa466` |
| `03_citation_v3.4_conformance_matrix_freeze_checklist_rc2.md` | `f0f1aa37603e20be650159cf8b91896ea222ad2562f40d55c3a9e804640566b8` |
| `04_citation_v3.4_dependency_deferred_work_register_rc2.md` | `0bf1cc12e93ce1911916644d620d387f23ee0b14f41662b752846ba1858d5698` |

Only File 2 may become the governing product implementation contract. File 1 is Level-3 architecture context; Files 3–4 are supporting evidence/registers.

## 3. Citation-specific pilot preflight

Before GSD `Discuss` begins, add these checks to the runbook preflight:

```text
[ ] File 2 exact bytes have completed independent review
[ ] File 2 content_state = frozen
[ ] pilot target scope authority_state = current
[ ] frozen File 2 SHA-256 recorded in pilot baseline
[ ] File 3 pilot-scope freeze checklist is satisfied
[ ] manual comparator = this exact file, copied/frozen outside the worktree
[ ] manual comparator SHA-256 recorded in pilot baseline
```

Any failure above occurs before GSD execution and therefore:

```text
→ PILOT VOID / DO NOT START THE CITATION TASK
```

This does not mean the Citation specification is defective; it means this product task is not eligible for the process pilot yet.

## 4. Pilot task

Implement exactly the frozen/current conformance scope:

```text
citation_v3_4_standalone_cli_nomap_apa7_like_v1
```

The implementation MUST conform to the exact frozen bytes of:

```text
citation_execution_conformance v3.4
```

No Section Map integration and no EpistemicOS orchestration work belongs to this pilot.

## 5. In scope for the implementation task

- canonical manuscript transform and invalid UTF-8 behavior;
- UTF-8 byte coordinates;
- standalone structural/heading fallback;
- bibliography detection: `detected | inferred | not_available`;
- supported author–year candidate envelope;
- parenthetical/narrative extraction;
- closed PREFIX and STOP behavior;
- extraction-layer surface grouping;
- bibliography extraction and reference identity;
- bibliography-grounded citation identity resolution;
- 3×3 candidate-resolution table;
- ambiguity reservation;
- candidate-level missing-reference/possible-mismatch diagnostics;
- uncited/duplicate/ambiguity diagnostics;
- author-structure checking;
- bibliography-absent behavior;
- canonical JSONL serialization and total ordering;
- stdout/file equivalence;
- atomic publication;
- exits 0–6;
- test-only invariant-injection seam;
- executable pilot-scope conformance suite.

## 6. Explicitly out of scope

- Section Map input;
- EpistemicOS Orchestrator integration;
- citation → human review tasks;
- claim ↔ citation linking;
- source support/credibility/validity assessment;
- numeric citation identity;
- additional citation profiles;
- conversion repair;
- broader deferred work listed in File 4.

A GSD plan that adds any out-of-scope capability without a new governing spec is defective.

## 7. Product authority rule

If the GSD plan, Codex review, implementation, corpus run or tests reveal behavior that the frozen spec does not define:

```text
STOP the affected implementation path
record a specification finding
route to the spec revision lifecycle
do NOT let Claude, Codex or the implementer choose the missing behavior
```

If code and the frozen spec disagree:

```text
code is non-conformant
```

unless the spec is formally revised through the governing lifecycle.

## 8. Manual comparator brief

The manual brief for the same task is:

> Build the standalone/no-map Citation v3.4 implementation exactly from the frozen Level-5 execution spec. Preserve deterministic byte-level behavior, do not infer product behavior from code or GSD, implement the full pilot-scope conformance suite, and stop on any normative gap instead of filling it in. The implementation is done only when all pilot-scope conformance cases pass, the regression corpus has no unresolved blocking finding, output is byte-deterministic, abort/atomic-publication behavior is exact, and no out-of-scope integration work is introduced.

This paragraph plus §§4–10 constitutes the manual comparator artifact. It is frozen before onboarding; it is not edited after seeing a GSD plan.

## 9. Task done conditions

The product task is done only when all are true:

```text
[ ] implementation accepts the pilot-scope inputs only
[ ] every C-001 through C-083 pilot-scope case has executed evidence
[ ] all PREFIX cases pass
[ ] all STOP cases pass
[ ] all 3×3 identity cells pass
[ ] invariant-injection exit6 case passes
[ ] candidate-level missing/mismatch diagnostics never acquire citation identity
[ ] bibliography-absent exact output passes
[ ] canonical JSONL byte goldens pass
[ ] stdout and --out bytes are identical
[ ] atomic publication/failure injection passes
[ ] same pinned input twice → byte-identical output
[ ] bounded-termination test passes
[ ] 11-paper regression corpus completes
[ ] every unexpected corpus finding has a B1–B10 disposition
[ ] no blocking corpus finding remains
[ ] no pilot-out-of-scope code was added
```

These are task done conditions. They are separate from the GSD pilot's four adoption criteria.

## 10. Required persisted implementation evidence

GSD planning should account for durable artifacts sufficient to recover:

```text
governing frozen spec identity + SHA
implementation plan
conformance test mapping
test results
golden-byte results
corpus run result
blocking-finding dispositions
implementation verification result
```

The pilot runbook separately tests whether GSD's persisted planning state makes task/phase/status/approved plan/findings/provenance/next action recoverable without chat history.

## 11. Plan-review defect rubric for this task

A plan concern is actionable when it would cause, permit, or fail to test any of:

- behavior outside the frozen Level-5 contract;
- a hidden runtime choice affecting deterministic output;
- code-point manuscript offsets;
- silent in-envelope citation loss;
- syntax-derived authoritative citation identity without bibliography support;
- candidate-level missing/mismatch diagnostics being treated as resolved identity;
- ambiguity being guessed away;
- non-total output ordering;
- incorrect null-vs-zero semantics;
- non-atomic authoritative file publication;
- untested exit/failure behavior;
- Section Map/pipeline scope creep;
- inability to map a consequential rule to executable evidence.

Severity/counting remains the pilot runbook's frozen `CYCLE_SUMMARY` rubric.

## 12. Pilot terminal decision

Do not modify the pilot's adoption logic.

After valid preflight, the existing runbook decides:

```text
PILOT FAIL
NO VERDICT / second task
PILOT INCONCLUSIVE
PILOT PASS
```

based on its fixed done-condition validity gate and four evaluation criteria.

The quality of the Citation implementation does not authorize reweighting the GSD pilot criteria after results are observed.
