---
status: complete
phase: 03-automated-proof
source: [03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md, 03-04-SUMMARY.md]
started: 2026-09-04T05:04:40Z
updated: 2026-09-04T05:07:00Z
---

## Scope Note — read before treating this as phase-wide coverage

**This UAT covers only the 35 deliverables sourced from the four plan SUMMARYs
(03-01 through 03-04). It does NOT cover six commits made outside any plan tonight:**
the `materializeTree` pipe-drain fix (`60bb107`), `gate.Run`'s `WaitDelay` fix (`fe052fb`),
the code-review fixes WR-01 (`errors.Is(exec.ErrWaitDelay)`, `1caa410`) and WR-02
(`materializeTree` comment correction, `f329265`), the T-03-14 password-leak fix
(`f75949d`), and the `tree_drain_test.go` control-drift fix (`efa54d4`).

Each of these six has its own captured falsifiability evidence (real reverted/restored
output, not asserted) — recorded in `03-INCIDENT-01`, `03-INCIDENT-02`, `03-REVIEW-FIX-SUMMARY.md`,
and `03-SECURITY-FIX-SUMMARY.md` respectively — but **none of it appears in this UAT
artifact**, because `uat.classify-coverage` only reads the four plan SUMMARYs by design,
and none of these six commits produced or belongs to a `*-SUMMARY.md`.

This is the same SUMMARY-scope blind spot the code review hit — its own Tier-2 SUMMARY
extraction missed the same files, and only its Tier-3 git-diff cross-check caught them.
**This is the third time tonight the same blind spot surfaced** (code review's file-scoping,
the security audit's threat-register coverage gap for the same three test files, and now
UAT's deliverable extraction) — one mechanism (`SUMMARY.md`-sourced scoping), three
different downstream tools it silently narrows. Recorded here rather than left implicit,
so "35/35 passed" is never read as "the whole phase's changes were UAT'd."

## Current Test

[testing complete]

## Tests

### 1. 03-01: Proof package spine + PROOF-01 (11 deliverables, all auto-covered)
expected: |
  D1 package compiles against gate's exported surface only (go build/vet/gofmt clean,
  no unexported symbol leakage) — D2 PROOF-01/intact_tree: unset DSN escalates, preamble
  + EPISTEMIC_OS_DB_URL on one line — D3 lineContainsBoth falsifiable + no-parallel-marker
  pinned — D4 nested recursion terminates at depth 1 (3 SKIP, exit 0) — D5 RunOptions.Dir
  additive, buildChildEnv byte-unchanged — D6 DefaultTimeout rationale corrected to
  measured 85s/2.8x — D7 materializeTree/stripEscalationExport clean, go.mod/go.sum
  untouched — D8 SC-5 control shows no preamble on defeated side — D9 requireIntact guard
  has a real failing path — D10 order-independent under -shuffle=on — D11 full make gate
  green, working tree byte-unchanged
result: pass
source: automated

### 2. 03-02: PROOF-02 + ordering check (8 deliverables, all auto-covered)
expected: |
  D1 PROOF-02/intact_tree: closed-port DSN escalates, preamble + 127.0.0.1:1 on one line —
  D2 testenv.RequireEnv observed in Combined (D-02b) — D3 SC-5 control shows no preamble,
  no dependency-prose assertion — D4 requireIntact guard has a real failing path — D5
  ordering check passes structurally against make -n gate's dry-run — D6 ordering check
  falsifiable (captured transposed-Makefile failure) — D7 order-independent under
  -shuffle=on — D8 full make gate green, compose Postgres never stopped
result: pass
source: automated

### 3. 03-03: PROOF-03 + fixture-unreadable control (8 deliverables, all auto-covered)
expected: |
  D1 breakFixture refuses real repo root and non-regular-file targets — D2 PROOF-03/intact_tree:
  broken fixture escalates, preamble + path suffix on one line — D3 assertion binds to path
  suffix only, never full spelling or OS errno text — D4 SC-5 control (doubly-defeated copy)
  shows no preamble, no exit-code/reporter-text assertion — D5 requireIntact guard has a real
  failing path — D6 order-independent, all three proofs + controls pass together — D7 real
  demo.md never touched, byte-identical throughout — D8 full make gate green, compose Postgres
  never stopped
result: pass
source: automated

### 4. 03-04: Governance close (8 deliverables, all auto-covered)
expected: |
  D1 GATE-10's REQUIREMENTS.md entry carries all five of D-19's obligations, GATE-06
  byte-untouched — D2 ROADMAP's SC-5 correction carries both D-12 obligations — D3
  make planning-parity PHASE=3 green (run 3x) — D4 03-FINDING-01 gives D-21's correction a
  durable home, committed — D5 STATE.md's 2026-09-03 entry gains exactly one pointer line,
  nothing else changed — D6 two deferred items registered with their sizing measurements —
  D7 GATE-10 marked Complete, planning-parity stays green — D8 full make gate green, no file
  outside .planning/ touched
result: pass
source: automated

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

none
