---
phase: 1
document: adjudication
supersedes: 8f3cb01
supersedes_note: amends finding 2 from `fixed` to `partially fixed`; scoreboard row and status text only, no other change
subject: three independent review passes over the Phase 1 plan set
adjudicated_at: 2026-08-31
plan_set_reviewed: cdad611 (freeze d92a8c9), planning-complete ded50c2
passes:
  - name: Alex
    kind: human, independent
    reviewed: 940727c (freeze d90b10d)
    findings: 6
    provenance: committed at 9aa59518, held outside this repository
  - name: Codex
    kind: external AI CLI (gpt-5.6-sol, reasoning=low)
    reviewed: 940727c/d90b10d, then 09a88c9/dd69e0e, then cdad611/d92a8c9
    findings: 20 severity-tagged in cycle 1, 3 in cycle 2, 3 in cycle 3
  - name: orchestrator
    kind: independent measurement against the working tree
    findings: 2 HIGH in cycle 1, plus coverage gaps and adjudications in all three
---

# Adjudication — Phase 1 review passes

Three independent passes reviewed the Phase 1 plan set. This document reconciles
them: for each of Alex's six findings, whether any convergence cycle found it, who
raised it, and whether it is fixed in the current plans; then what each pass found
that the others did not.

This is the criterion-2 evidence. It is written down because the reconciliation
existed only in a conversation transcript, and three separate artifacts in this
phase have already been lost or degraded that way — see **Provenance hazards**.

## Why this document exists

The milestone's thesis is that a gate which passes vacuously makes every claim
unfalsifiable. The same failure mode applies to review: a finding that is raised,
acted on, and then not recorded leaves a plan set that looks reviewed without
being auditable. Two of the three passes below produced findings that no committed
artifact retains. This document is the retention.

## Scoreboard

| # | Alex's finding | Found by a cycle? | Raised by | Fixed now? |
|---|---|---|---|---|
| 1 | 01-02 AC-14 policy contradiction | Partially, cycle 1, LOW | Codex | Narrowed and deferred, not eliminated |
| 2 | Frozen baseline changeable after freeze | Adjacent, cycle 1, HIGH | Orchestrator | Partially — value corrected, substitution procedure still unguarded |
| 3 | Credential-canary proof insufficient | Yes, cycle 1, MEDIUM + HIGH | Codex, then orchestrator | Yes |
| 4 | 01-01 tracer loses expected-failure exit status | Yes, cycle 1, HIGH | Codex | Yes |
| 5 | `go build ./...` to find unused imports in test files | **No — missed by all three cycles** | — | **Fixed by this adjudication** |
| 6 | T-01-10 restore guarantee under-specified | Yes, cycle 1, HIGH; reopened cycle 2 | Codex | Yes, after three cycles |

---

## 1 — 01-02 AC-14 policy contradiction

**Alex:** GATE-04 says a genuinely preamble-free fixture is legitimate signal and
its skips stay green, but the plan makes absence of a non-whitespace preamble a
hard `TestFixtureIntegrity` failure. The invariant fails before the skip branches
are reached.

**Found:** Partially. Codex reached the same territory in cycle 1 but rated it
LOW and framed it as a wording problem: *"'Green and silent' is interpreted as
PASS for the current fixture … the plan should distinguish it from the more
general GATE-04 behavior, under which a genuinely preamble-free fixture would
produce SKIP rather than PASS."* Alex named the mechanism; Codex named only the
ambiguity. Alex graded it correctly and Codex under-graded it.

**Status: narrowed and deferred, not eliminated.** `01-02-PLAN.md:232` still
`t.Fatal`s the returned message when non-empty. The plan's defence is at
`01-02-PLAN.md:65-75`: the fixture is hash-pinned, so the invariant only ever
evaluates one known document, and `loadFixture` checks SHA-256 and byte length
first — a swapped fixture fails on the hash before the preamble check is reached.
The plan states the distinction explicitly: PASS is required *for these pinned
bytes*; SKIP remains correct and legal for a genuinely preamble-free fixture.

The residual is exactly Alex's case: update the fixture **and** its pins together
to a preamble-free document, and `TestFixtureIntegrity` hard-fails where GATE-04
says SKIP is legitimate. The plan concedes this at `01-02-PLAN.md:90` and routes
it to 01-03 Task 3's developer disposition list. Under the convergence contract an
explicit deferral closes the finding, which is why it stopped being reported — but
the contradiction still exists in that one case and is a live decision, not a
resolved one.

## 2 — Frozen baseline changeable after freeze

**Alex:** the manifest pins `phase_base_commit = fcebad1` but 01-03 permits
substituting another branch-point commit and merely recording it. Should be halt
then re-freeze.

**Found:** Adjacent, from a different direction. The orchestrator's cycle-1 HIGH
found the base was *factually wrong* — `868d45b` landed after `fcebad1` and
modified `.github/workflows/ci.yml`, so both audit criteria returned 1 where the
plan required 0, before any Phase 1 code existed. It also found that the plan's
escape hatch never fired, because `fcebad1` genuinely **is** an ancestor: the
guard tested ancestry when the plan needed "is this the tip at phase start".
Codex asserted the opposite, calling the range *"presently valid"*.

Alex's finding is the governance defect one level up: not that the base was wrong,
but that the plan permitted changing a frozen value without re-freezing.

**Status: partially fixed.** The wrong *value* is corrected and recorded: the
`"substitute the actual commit this phase branched from"` clause is gone from all
three plans, the base is re-anchored to `030521b`, and `01-01` Task 1 carries a
`<precondition>` asserting all four properties (`01-01-PLAN.md:109`).

That guard catches a **wrong anchor**. It does not catch an **ungated
substitution**, and the second is what Alex objected to. A base moved forward past
a real change satisfies all four properties — which is precisely why `030521b`
passes them. The substitution *procedure* is therefore still unguarded: the
specific `fcebad1` error is gone, the mechanism that permitted it is not. The
substitution at `dd69e0e` was itself neither halted nor human-approved.

## 3 — Credential-canary proof insufficient

**Alex:** T-01-09 is high/blocking but the verifier executes neither canary, and
`| grep -c PWLEAKCANARY = 0` alone does not prove `go test` failed or that the
malformed DSN reached the `pgxpool.New` parse branch.

**Found:** Yes, by both other passes, in two distinct forms.

Codex, cycle 1, MEDIUM — the proof-sufficiency half, nearly verbatim: *"needs an
independent assertion that `go test` exited nonzero and emitted the fixed
parse-error message."* Codex did **not** name the verifier-execution gap; Alex did.

The orchestrator, cycle 1, HIGH — went past both passes. The canary could not fail
**at all**: pgx v5.7.2 already redacts the password on every DSN form measured
(`u:xxxxxx`, `password=xxxxx`), so every canary criterion passed at HEAD with zero
code written. Alex's finding is adjacent but not the same claim: he says the proof
is weak, the measurement says it is vacuous. Alex was closer to it than Codex was.

**Status: fixed.** Scenario D is rebuilt on a **database-name** token, which the
library does echo verbatim — measured count 1 at the phase base, required 0 after
the change — with four independent assertions and its own negative control proving
the detector can see the token (`01-01-PLAN.md:429-430`, `01-03-PLAN.md:655`).
T-01-01 and T-01-09 are downgraded `high` to `medium` with the disproving
measurement recorded, and both left the blocking list.

## 4 — 01-01 tracer loses the expected-failure exit status

**Alex:** pipes `go test` into `grep` without preserving or asserting `go test`'s
status, so the pipeline can succeed because `grep` succeeded.

**Found:** Yes. Codex, cycle 1, HIGH — the load-bearing finding of the whole
review, and it named 01-01 Task 1's tracer `<automated>` block explicitly.

**Status: fixed.** `01-01-PLAN.md:416` is capture form:
`out=$(…); st=$?; test "$st" -ne 0 && printf '%s' "$out" | grep -q …`. Each plan
also carries a frontmatter prohibition forbidding the bare-pipeline shape.

## 5 — `go build ./...` does not find unused imports in test files

**Alex:** 01-01 says to use `go build ./...` to find unused imports in test files.
`go build` doesn't compile `_test.go`.

**Found: no.** Missed by all three convergence cycles. Codex actively endorsed the
error in cycle 1: *"The plan appropriately tells the executor to let the compiler
determine unused imports."* This is the only one of Alex's six that no cycle
reached, and it was still live in the plans at `ded50c2`.

**Measured**, on a scratch module with an unused `os` import in a `_test.go` file,
Go 1.24.13:

```
go build ./...   exit 0        names nothing
go vet ./...     exit 1        "os" imported and not used
go test ./...    build failed  "os" imported and not used
```

Alex is right. `go build` does not compile `_test.go` files, so it exits clean
while the unused import is still present.

**Severity qualifier.** All three `<automated>` blocks in 01-01 (`:416`, `:499`,
`:569`) run `go vet ./...` and `go test ./...`, both of which do catch it. So the
defect is caught at verify time and never reaches a green phase. The cost is a
misleading instruction: an executor following the `<action>` sees a clean
`go build`, concludes the imports are fine, and then fails verification for a
reason the action told it could not happen. It is a wasted debug cycle, not an
undetected escape.

**Status: fixed by this adjudication.** Both call sites in `01-01-PLAN.md` now
name `go vet ./...` and state why `go build ./...` is the wrong tool here.

## 6 — T-01-10 restore guarantee under-specified

**Alex:** requires unconditional restoration but names no trap or status-preserving
mechanism, and the verifier doesn't exercise move → expected failure → restore.

**Found:** Yes. Codex, cycle 1, HIGH — Alex's finding almost word for word: the
plan said the restore must run "regardless of exit status" but named no
`trap`/`finally` and no pre/post hash comparison.

This finding then took all three cycles to actually close. Cycle 2 found the
*named* mechanism still broken: the restore and the trap-clearing were
`;`-separated under `pipefail` with no `set -e`, so a failed restore disarmed the
guard on the very next statement — the exact outcome the mitigation claimed to
prevent. Cycle 3 confirmed the rework is fail-closed by execution against a
stand-in, not by argument.

**Status: fixed.** T-01-10 remains `high` and is the phase's only blocking entry.
The trap is installed before the move; the inbound path has four `||`-guarded
aborts so `trap - EXIT INT TERM` is unreachable except on a proven-restored path;
SHA-256 is captured before and compared after against the pinned constant; and
`01-03-PLAN.md:514` adds a `*_TRAP_ARMED` stop-and-recover criterion. Alex's
"verifier doesn't exercise move → expected failure → restore" is now the
acceptance criterion itself.

---

## What Codex found that Alex did not

Net of the six overlaps, from Codex's 20 severity-tagged cycle-1 findings:

**01-01** — the skip/fail behaviour of `Pool` and `Fixture`'s failure branch is
never unit-tested (MEDIUM); appending the raw `Ping` error is an avoidable
disclosure dependency (MEDIUM); "all three environment conditions are decided in
one package" is imprecise (LOW); `EPISTEMIC_OS_TEST_REQUIRE_DB` gates the fixture
too, so the name is narrower than the behaviour (LOW); presence-semantics treating
`0` and `false` as enabled is defensible but surprising (LOW).

**01-02** — the negative proof mutates tracked source with no precise restoration
(MEDIUM); `git diff --stat` cannot prove restoration because the file is
intentionally modified (MEDIUM); failure-message requirements are over-specified
(LOW); the empty-heading guard protects only `TestFixtureIntegrity` while AC-14
still indexes `headings[0]` (LOW).

**01-03** — `files_modified: []` contradicts the required summary artifact
(MEDIUM); the clean `git status` criterion conflicts with writing that summary
(MEDIUM); verification commands are POSIX-only with the shell unspecified
(MEDIUM); "at least 38 `--- PASS` lines" is indirect proof (LOW); the compose
database's end state is unstated (LOW); the E1–E4 probe edges add noise (LOW).

## What only the orchestrator found

Reached by neither Codex nor Alex:

- **The pgx-redaction disproof** (cycle 1, HIGH) — the phase's one blocking
  security control could not fail. Strictly stronger than Alex's finding 3.
- **ROADMAP success criterion 3 half-unverified** (cycle 1) — no scenario covered
  the unescalated unreachable-database or unreadable-fixture branches. Became
  Scenarios A2 and A3.
- **The zero-skip criterion had no command** in the `<automated>` block (cycle 2
  adjudication, narrowing a Codex finding whose stated mechanism was wrong).
- **Set equality vs set containment** mislabel (cycle 2, LOW).
- **The trap's recovery guarantee is narrower than the prose claims** (cycle 3) —
  the trap is a no-op on the re-hash, hash-mismatch and `RESTORE_MISSING` paths.
- **`mktemp -d` volume unpinned** (cycle 3, LOW).

## Disagreements and who was right

| Point | Codex | Independent measurement | Right |
|---|---|---|---|
| Phase base `fcebad1` | "presently valid" | `868d45b` touches `ci.yml` inside the range; both audit criteria fail | Orchestrator |
| Credential leak via `pgxpool.New` | Accepted the plan's premise, called the fix "materially better" | pgx v5.7.2 redacts the password on all four DSN shapes; canary passes unchanged at the base | Orchestrator |
| POSIX-only commands on Windows | MEDIUM, "not directly runnable in the current shell" | Git Bash present; every command ran correctly. Documentation gap real, runnability claim not | Split |
| Zero-skip under `pipefail` | `grep -c` exiting 1 breaks the check | Command substitution discards pipeline status; the mandated form is safe. Finding stands on narrower ground | Orchestrator on mechanism, Codex on the finding |
| `printf \| grep -q` SIGPIPE | MEDIUM, newly raised | Not reproduced at 100 KB / 1 MB / 5 MB — `rc=0`, `PIPESTATUS=0 0`. Bash's builtin `printf` does not surface the closed pipe | Orchestrator; kept as hardening |
| `go build` finds unused test imports | Endorsed the plan's instruction | `go build ./...` exits 0 with an unused import in `_test.go` | **Alex** |

## Provenance hazards

Three ways evidence from this phase has been lost or degraded. Recorded because
the pattern, not any single instance, is the finding.

1. **Alex's review is not in this repository.** `9aa59518` is absent from
   `rev-list --all`, the reflog, and the shared object store across both
   worktrees. STATE.md at `9a3fe7b` recorded the intent: *"Alex's review complete,
   findings held outside this repository."* His six findings survive here only
   because they were re-entered by hand.

2. **`01-REVIEWS.md` is rewritten each cycle, not appended.** Only cycle 3 is on
   disk. Cycles 1 and 2 exist solely at `2041093` and `aeb4a98`. The convergence
   workflow states the opposite — *"REVIEWS.md accumulates history across cycles;
   resolved findings from prior cycles remain in the file as audit trail"* — and
   forbids grepping it for counts on that basis. The prohibition held anyway
   because counts came from the `CYCLE_SUMMARY` contract, but it is correct for
   the wrong reason, and any future code trusting the stated accumulation would
   read one cycle as the whole history.

3. **One cycle-1 finding was never written down.** The LOW finding *"`git diff
   --name-only` with no revision range is vacuous after an atomic commit — anchor
   it to the plan's base commit"* was reported to the orchestrator in the review
   agent's return message and counted toward the 14 actionable, but appears
   nowhere in the committed `01-REVIEWS.md` (`atomic commit` → 0 hits,
   `01-01 Task 3` → 0, `Anchor it` → 0). It drove a plan change — 01-01 now
   anchors its diffs to `030521b` — while leaving no trace in the audit artifact.
   The return message is ephemeral, so its provenance existed nowhere until this
   document.
