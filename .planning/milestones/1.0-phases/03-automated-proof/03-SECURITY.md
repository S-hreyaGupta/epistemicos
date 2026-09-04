---
phase: 3
slug: automated-proof
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-09-04
---

# Phase 3 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
>
> State B run: all four plans (03-01..03-04) carried plan-time `<threat_model>` blocks
> (`register_authored_at_plan_time: true`), but three test files were committed tonight
> outside any plan's scope (`harness_waitdelay_test.go`, `harness_errwaitdelay_test.go`,
> `tree_drain_test.go`) — no plan's threat model could have covered code that didn't exist
> when it was written. The mechanical short-circuit rule (ASVS L1 + plan-authored + zero
> open) would have skipped auditor verification entirely; the orchestrator declined to take
> that shortcut given the coverage gap, added T-03-13 to cover the uncovered files, and
> dispatched the full `gsd-security-auditor` regardless.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Test process → `make` subprocess | `gateproof` spawns full `make gate` / `make -n gate` runs with a constructed environment | subprocess argv, env, captured stdout/stderr |
| Test process → `git` subprocess | `git archive --format=tar HEAD` spawned; stdout parsed as a tar stream | tar entry names/content (all from `HEAD`, not attacker-controlled beyond the repo itself) |
| Tar stream → filesystem | Archive entry names decide paths written under a temp root | filenames only — the one place an external byte stream chooses a filesystem destination |
| `RunOptions.Dir` → subprocess working directory | New field lets a caller point a `make` subprocess elsewhere than `RepoRoot(t)` | directory path, always `os.MkdirTemp`-derived at every real call site |
| Ambient environment → recursion guard | `EPISTEMIC_OS_TEST_MAKE_DEPTH` gates whether every assertion in the package runs | integer depth marker |
| Test output → CI log | Failure reports print `RunResult.Combined` — full subprocess stdout+stderr | subprocess output, which may carry DSN-derived text (see T-03-05 lineage, T-03-13, T-03-14) |
| Constructed DSN → child environment | Throwaway DSNs (`unreachableDSN`, closed-port literals) layered onto `EPISTEMIC_OS_DB_URL` for negative-path proofs | synthetic, non-real credentials by construction |
| Planning documents → planner/executor agents | ROADMAP.md / REQUIREMENTS.md are inputs every future agent plans against | requirement IDs, scope statements |
| STATE.md → every agent reading project position | Many writers, no owner; contents treated as authoritative | project state, deviation/deferral records |
| Governance record → future readers | A correction recorded without its original claim is indistinguishable from a document that was always right | historical claims and their falsifiers |
| CLI `migrate` subcommand → stderr → CI/operator log | `store.RunMigrations` wraps golang-migrate's own errors with `%w`; on a malformed DSN, the wrapped error embeds the raw connection string, which `die()` prints unredacted | full connection string including password, on the specific `net/url.Parse`-failure branch (see T-03-14) |

---

## Threat Register

Composite key = plan + Threat ID (each plan's `<threat_model>` restarts numbering from T-03-01).

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| 03-01 T-03-01 | DoS | nested `make gate` recursion | high | mitigate | `SkipIfNested(t)` first-statement, `buildChildEnv` `DepthEnv`-last byte-unchanged, `DefaultTimeout` bound. Depth-1 measured: 7 SKIP, exit 0. See Audit Trail note on control drift. | closed |
| 03-01 T-03-02 | Tampering | `archive/tar` extraction into temp root | high | mitigate | Abs-name reject, escape-root reject, entry-kind hard fail, zero-entry fail — all verified present. | closed |
| 03-01 T-03-03 | Tampering | defeat edits reaching the working tree | high | mitigate | Repo-root refusal in `stripEscalationExport`; `git status --porcelain` / `git diff --stat` on Makefile, go.mod, go.sum, testenv/ verified empty. | closed |
| 03-01 T-03-04 | EoP | `gate.RunOptions.Dir` | medium | mitigate | Zero-value fallback to `RepoRoot(t)`; every real call site passes an `os.MkdirTemp` root; `Dir` absent from `buildChildEnv`'s signature. | closed |
| 03-01 T-03-05 | Info Disclosure | `RunResult.Combined` in failure output | medium | mitigate | PROOF-01 unsets both `URLEnv` and `RequireEnv`; SEC-01 loopback binding verified live (`docker-compose.yml:13`, `127.0.0.1:5432:5432`). See T-03-14. | closed |
| 03-01 T-03-06 | DoS | shared compose database contention | medium | accept | Measured `gate`×`store` +2.11s, `gate`×`approved` +0.80s; registered as a deferred item by 03-04. | closed (see Accepted Risks) |
| 03-01 T-03-07 | Spoofing | `make`/`git` resolved from `PATH` | low | accept | Same terms as Phase 1 AR-03, Phase 2 T-02-11. | closed (see Accepted Risks) |
| 03-01 T-03-SC | Tampering | dependency installation | low | accept | No package-manager install task; stdlib only; `go.mod`/`go.sum` diff empty. | closed (see Accepted Risks) |
| 03-02 T-03-01 | DoS | nested `make gate` recursion | high | mitigate | Carried unchanged from 03-01. | closed |
| 03-02 T-03-02 | Tampering | defeat edits reaching the working tree | high | mitigate | Same guards; tree clean; scratch falsifiability file confirmed absent. | closed |
| 03-02 T-03-03 | Info Disclosure | pgx dial diagnosis in failure output | medium | mitigate | `unreachableDSN` is `u`/`pw` against a closed port; measured 0 credential-token occurrences. | closed |
| 03-02 T-03-04 | Tampering | binding an assertion to a dependency's prose | medium | mitigate | D-15 comment present; `"new migrator"` string absent from `proof02_test.go` entirely. | closed |
| 03-02 T-03-05 | DoS | shared compose database contention | medium | accept | Same as 03-01 T-03-06. | closed (see Accepted Risks) |
| 03-02 T-03-06 | Spoofing | `make`/`git` resolved from `PATH` | low | accept | Same terms. | closed (see Accepted Risks) |
| 03-02 T-03-SC | Tampering | dependency installation | low | accept | Same as above. | closed (see Accepted Risks) |
| 03-03 T-03-01 | Tampering | `breakFixture` reaching the working tree | high | mitigate | Repo-root refusal; regular-file precondition; `demo.md` diff empty. | closed |
| 03-03 T-03-02 | DoS | nested `make gate` recursion | high | mitigate | Same as 03-01 T-03-01. | closed |
| 03-03 T-03-03 | Tampering | `archive/tar` extraction, exercised twice | high | mitigate | Same guards as 03-01 T-03-02. | closed |
| 03-03 T-03-04 | DoS | shared compose database contention | medium | accept | PROOF-03 is why this threat grew (nested `migrate` + full suite). Same measurement basis. | closed (see Accepted Risks) |
| 03-03 T-03-05 | Info Disclosure | failure output from full nested suite run | medium | mitigate | Ambient compose DSN, loopback-bound (SEC-01 verified live). See T-03-14 — the amplification path this entry did not anticipate. | closed |
| 03-03 T-03-06 | Spoofing | `make`/`git` resolved from `PATH` | low | accept | Same terms. | closed (see Accepted Risks) |
| 03-03 T-03-SC | Tampering | dependency installation | low | accept | Same as above. | closed (see Accepted Risks) |
| 03-04 T-03-08 | Repudiation | a governance act made silently | high | mitigate | Parity check green at phase end; SC-5 correction block present in ROADMAP.md. | closed |
| 03-04 T-03-09 | Tampering | editing a frozen historical record | high | mitigate | `git diff` on REQUIREMENTS.md: all GATE-06 hits are additions inside GATE-10; no removed line touches GATE-06's entry. | closed |
| 03-04 T-03-10 | Repudiation | a correction not surviving its host file | medium | mitigate | `03-FINDING-01-phase-completion-diagnosis.md` tracked and committed; STATE.md carries a pointer. | closed |
| 03-04 T-03-11 | Tampering | a deferred item registered without its measurement | medium | mitigate | STATE.md's deferred entries carry specific measured numbers, not descriptions. | closed |
| 03-04 T-03-12 | EoP | a sweep silently adding a requirement | medium | mitigate | GATE-10 declared before planning as an explicit scope act, not folded into a sweep. | closed |
| 03-04 T-03-SC | Tampering | dependency installation | low | accept | No code, no package-manager install; `.planning/`-only. | closed (see Accepted Risks) |
| **T-03-13** | **Info Disclosure** | `gate.Run`'s fallthrough `t.Fatalf`, `materializeTree`'s failure paths, and the new `errors.Is(runErr, exec.ErrWaitDelay)` branch — plus three test files committed outside any plan tonight | medium | mitigate | Independently re-verified by both the auditor and the orchestrator (live reproduction, not trust): no call site places a DSN in argv; the new `ErrWaitDelay` branch prints nothing; `git archive` has no plausible path to a credential in its own stderr; all three out-of-band files' synthetic subprocesses (`bash sleep`, self-exec'd helpers) never touch a real DSN. No new instance of T-01-01's pattern was introduced by tonight's code. | closed |
| **T-03-14** | **Info Disclosure** | `internal/adapters/secondary/store/migrate.go:38-41`'s `net/url.Parse`-failure branch, printed unredacted by `cmd/epistemicos-cli/main.go`'s `die()` | medium | accept (pending remediation) | **Pre-existing defect, outside the phase-3 diff, newly amplified by Phase 3.** `RunMigrations` wraps golang-migrate's own parse error via `fmt.Errorf("new migrator: %w", err)`; on a malformed `EPISTEMIC_OS_DB_URL` this embeds the raw connection string with password, and `die()` prints it verbatim to stderr with no redaction. **Independently reproduced twice** by the orchestrator with a synthetic credential (`FAKE_SYNTHETIC_SECRET_XYZ`): appears verbatim on the parse-failure branch (malformed port), absent (0 occurrences) on the well-formed-but-unreachable control case — confirming the leak is specific to `net/url.Parse` failure, exactly T-01-01's original pattern (fixed in `testenv.Pool` via the argument-free `unparseableURLMsg` const; `store.RunMigrations` is the un-remediated twin, never audited because it sat outside Phase 1's and Phase 3's file scope until now). **Why Phase 3 owns registering it, not just fixing it silently:** PROOF-03 is the new amplification path — by design it passes the ambient DSN through unmasked (the fixture condition needs a working database connection), and prints `RunResult.Combined` verbatim on any nested-gate failure. On a host or CI runner with a malformed `EPISTEMIC_OS_DB_URL`, PROOF-03's nested gate fails at `migrate`, and the password reaches the CI log. Severity is `medium` (not `high`) because: the credential is loopback-bound (SEC-01, verified live); the trigger is a malformed DSN, not the normal path; and the defective code itself is outside this phase's file scope. **Severity rises to high if a non-loopback or production DSN ever flows through this path.** **Fixed at commit `f75949d`**: the `net/url.Parse`-failure branch is now substituted with an argument-free constant mirroring `testenv.go`'s `unparseableURLMsg`; every other error from `NewWithSourceInstance` (including AR-01's accepted pgx dial-failure disclosure) is unchanged, verified by live before/after/control captures (see `03-SECURITY-FIX-SUMMARY.md`). | **closed** |

*Status: open · closed · open — below `high` threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (high) count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**`threats_open: 0`** — T-03-14 is `medium`, below the `high` block threshold, so it does not block Phase 3's advancement. It is left `open` rather than `closed` in this table because — unlike every accept-disposition entry below, which closes cleanly on a stable, already-measured condition — it names a live, reproducible defect the user has not yet dispositioned. Recorded as open rather than quietly marked closed-by-acceptance.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-04 | 03-01 T-03-06, 03-02 T-03-05, 03-03 T-03-04 | Shared compose database contention, measured (`gate`×`store` +2.11s, `gate`×`approved` +0.80s), present before Phase 3 and grown by PROOF-03's full nested suite run. Not taken in-phase because isolation is arguably its own requirement; registered as a STATE.md deferred item by 03-04 with its measurement. | Orchestrator, per D-06 (03-CONTEXT.md) | 2026-09-04 |
| AR-05 | 03-01 T-03-07, 03-02 T-03-06, 03-03 T-03-06 | `make`/`git` resolved from `PATH` inside the test binary. Accepted on the same terms as Phase 1's AR-03 and Phase 2's T-02-11: an attacker able to place a binary earlier on the developer's `PATH` already has code execution. `git` is newly added to the invoked set this phase. | Orchestrator, consistent with prior-phase precedent | 2026-09-04 |
| AR-06 | 03-01/02/03/04 T-03-SC | No package-manager install task exists anywhere in Phase 3; every new file uses only the standard library and this repository's own packages. Verified: `git diff --stat -- go.mod go.sum` empty across the whole phase. | Orchestrator | 2026-09-04 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-04 | 29 | 28 | 1 (T-03-14, medium, non-blocking) | gsd-security-auditor (opus) + orchestrator independent verification |
| 2026-09-04 | 29 | 29 | 0 | Both findings below fixed and closed: T-03-14 at commit `f75949d`, the `TestMaterializeTree_DrainsPastTarEOF` control drift at commit `efa54d4`. See `03-SECURITY-FIX-SUMMARY.md`. |

**Two findings beyond the register, both independently reproduced/verified by the orchestrator, not accepted on the auditor's word alone:**

1. **T-03-14** (above) — a real, live, reproducible password leak on `store.RunMigrations`'s parse-failure branch, pre-existing but newly amplified by PROOF-03. Presented to the user for an explicit remediation decision.

2. **Control drift in `TestMaterializeTree_DrainsPastTarEOF`** (`tree_drain_test.go`, committed outside any plan tonight). It does not call `gate.SkipIfNested(t)` and bypasses `buildChildEnv` (`cmd.Env = append(os.Environ(), ...)`, passing the depth marker through un-incremented). This falsifies two written claims: `gateproof_test.go`'s own comment ("Every test in this package calls `gate.SkipIfNested(t)` as its first statement") and `03-01-SUMMARY.md`'s coverage claim ("3 SKIP, 0 FAIL" — measured now at 7 SKIP + 2 PASS, since this file adds a second real test that runs at any depth). **The underlying threat (T-03-01, nested recursion) stays substantively mitigated** — this test's own child (`os.Args[0] -test.run=TestHelperProcess_TarWithTrailer`) writes a synthetic tar and exits without ever invoking `make`, bounded at 5s ctx + 2s WaitDelay, with no recursion amplification possible. But a declared control is now false in a milestone whose stated purpose is removing claims nobody can falsify. Not fixed in this pass — recommend either adding `gate.SkipIfNested(t)` to this test or correcting the doc comment to state the actual invariant (verified by direct enumeration: this project's independent grep confirms every real test in `gateproof/` besides this one does call `SkipIfNested` first).

Both findings independently confirmed by the orchestrator via direct source reading and live reproduction (a synthetic credential, never a real one) before being recorded here — not accepted on the auditor's report alone.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed (T-03-14 is medium, below the `high` block threshold)
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-04 — with T-03-14 and the `tree_drain_test.go` control-drift finding both flagged for an explicit user remediation decision, not silently closed.
