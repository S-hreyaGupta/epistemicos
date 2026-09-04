---
phase: 02
slug: enforcement-and-a-single-gate-definition
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on (high). Blocking gate.
threats_open: 0
threats_total: 23
threats_closed: 18
threats_open_below_threshold: 5
asvs_level: 1
block_on: high
created: 2026-09-02
audited_by: gsd-security-auditor (opus)
register_authored_at_plan_time: true
---

# Phase 02 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register authored at plan time across the four PLAN files (02-01..02-04). The audit
verified that each declared mitigation is actually present in the implemented code —
by reading source, running `docker compose ps` / `docker port`, grepping call sites,
and cross-checking SUMMARY.md verification records — not by reading plan-text claims.

---

## Threat Register (summary)

23 threats. 18 closed, 5 open and all below the `high` blocking threshold.

The three threats at or above `block_on: high` are all CLOSED, each on re-measured
rather than declared evidence:

| Threat | What it is | Evidence |
|---|---|---|
| **T-02-07** (DoS) | The subprocess harness could recurse unboundedly | `buildChildEnv` sets `DepthEnv` LAST (`harness.go:254`, after unset/overlay at 247), so a caller naming it in `Unset` cannot defeat it; `SkipIfNested(t)` is the first statement of every spawning test; `exec.CommandContext` + `DefaultTimeout` on every `Run`; `TestRunTimesOut` drives the timeout branch (100ms vs a 5s sleep) rather than asserting the const exists |
| **T-02-12** (EoP) | **SEC-01** — compose PostgreSQL published on all interfaces | `docker-compose.yml:13` declares the loopback mapping AND the running container reports `127.0.0.1:5432->5432/tcp` with no `0.0.0.0` and no `[::]`. Both halves — which required the recreate the plan performed, not a file-only edit |
| **T-02-18** (Repudiation) | The parity check could pass without checking | Absent phase section and missing argument both hard-fail; the scratch-copy control fails AND names `GOV-01` specifically |

Open and non-blocking: T-02-01 and T-02-13 (DSN user and database name disclosed on
the unreachable path; password redacted by pgx), T-02-11 (`make` resolved from
PATH, on AR-03's terms), T-02-14 (a PR can modify the Makefile that CI runs — a
standing property of any make-based CI, and the `go` job holds no repo secrets),
T-02-SC (supply chain: `go.mod` and `go.sum` byte-unchanged since base `868d45b`,
`make` unchanged at 4.4.1).

## Verification Notes

**T-02-09 — a documentation/code mismatch, recorded rather than accepted.** The
plan's mitigation text claims `TestMakeTestPrintsLenientBanner` "reports no
subprocess output on failure". That is false: `makefile_test.go:89` and `:92` both
interpolate `result.Combined` into `t.Errorf`. The residual was then assessed
independently rather than assumed. No raw DSN is printed whole anywhere in the
codebase — `testenv.go:149` prints the variable NAME, and `:182` prints only the
host via `hostFromURL`'s host-only extraction, alongside the argument-free
`unparseableURLMsg` constant. The compose credentials the test carries are the
public defaults already committed in `docker-compose.yml` and `ci.yml`, not secrets.
Recorded CLOSED with this caveat, because the underlying threat does not
materialize through this gap — but the plan text and the test disagree, and that
should be corrected in a future revision.

**T-02-17 — the GATE-09 negative control passed vacuously, and why the threat stays
closed.** The plan's own control was defeated by a Windows environment-variable
collision: `TMP` reassignment broke `go.mod` resolution inside the mutated copy, so
`go test` failed on a module error that the check read as a successful negative.
Documented in `02-03-SUMMARY.md`'s appended correction. The guard was then
re-measured with a non-exported directory name, and all five heading-free subtests
genuinely fail with the guard defeated. T-02-17 is closed on that corrected
re-measurement, NOT on the frozen plan's defective control.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Status | Accepted By | Date |
|---------|------------|-----------|--------|-------------|------|
| AR-01 | T-01-02 / T-02-01 / T-02-13 | DSN user and database name disclosed on the `Ping`-unreachable path; password redacted by pgx. Accepted at Phase 1 on the premise of "a loopback compose service" — **that premise was measured FALSE at Phase 1 sign-off and is now measured TRUE**: SEC-01 rebinds the compose PostgreSQL to loopback only, confirmed live. The residual disclosure is unchanged and remains accepted on its own terms, but its stated containment boundary is now factually accurate rather than repaired in name only. **Boundary repaired; residual still open, non-blocking.** | open — below threshold; boundary repaired | Alex Zamurko (Phase 1); boundary repair verified this audit | 2026-09-01 / 2026-09-02 |
| AR-02 | T-01-11 | Compose PostgreSQL bound to all interfaces at Phase 1, reachable from the local network with guessable defaults. Converted from an accepted risk to a scheduled fix (SEC-01) on the explicit condition that it "stands only until SEC-01 lands". **SEC-01 landed in `a527644` and is verified on both required halves.** **RESOLVED — retired, not carried forward.** | **CLOSED** | Alex Zamurko (accepted, then scheduled); resolution verified this audit | 2026-09-01 / 2026-09-02 |
| AR-03 | T-01-SC / T-02-SC | The host `make` binary (GNU Make 4.4.1, ezwinports) executes every gate measurement across both phases; installed via winget mid-Phase-1, with no legitimacy audit beyond winget's own hash verification. Carried forward unchanged: `make --version` is still 4.4.1 at the same path, `go.mod` and `go.sum` are byte-unchanged since base, and no Phase 2 plan contains a package-manager install task. | open — below threshold | Alex Zamurko | 2026-09-01 |

**T-01-11 is CLOSED** as of this audit — the same evidence that resolves AR-02
closes it. It is not carried forward as open.

---

## Orchestrator re-verification (2026-09-02)

The auditor writes no files by contract, so this file was persisted by the
orchestrator. Before persisting, its load-bearing claims were independently
re-measured rather than transcribed:

| Claim | Re-measured result |
|---|---|
| SEC-01 live binding | `docker port` reports `5432/tcp -> 127.0.0.1:5432` |
| The T-02-09 discrepancy is real | `makefile_test.go:89` and `:92` do interpolate `result.Combined` |
| No whole DSN is ever printed | `testenv.go:149` prints the variable NAME; `:182` prints the host only |
| Supply chain unchanged | `git diff 868d45b..HEAD -- go.mod go.sum` is empty |
| T-02-07's depth guard | depth=1 skips both spawning tests; a malformed marker hard-fails |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open (non-blocking) | Run By |
|------------|---------------|--------|----------------------|--------|
| 2026-09-02 | 23 | 18 | 5 (0 blocking) | gsd-security-auditor (opus), ASVS L1, `block_on: high` |

HEAD at audit: `d17051a`. No implementation file was modified by the audit.
`make gate` was deliberately NOT run by the auditor — a verifier agent was running
it concurrently, and two simultaneous migration runs against one database risk a
spurious failure that would look like a real finding.

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented — AR-01 carried with repaired boundary, AR-02 resolved, AR-03 carried forward
- [x] `threats_open: 0` confirmed — no open threat at or above `block_on: high`
- [x] AR-02 explicitly resolved; T-01-11 closes with it
- [x] T-02-09 mismatch recorded rather than silently accepted
- [ ] Operator sign-off — pending (UAT)

**Verdict: SECURED.** `threats_open: 0`.
