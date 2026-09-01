---
phase: 01
slug: escalation-mechanism-and-fixture-invariant
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on (high). Blocking gate.
threats_open: 0
threats_total: 15
threats_closed: 12
threats_open_below_threshold: 3
asvs_level: 1
block_on: high
created: 2026-09-01
audited_by: gsd-security-auditor (opus)
register_authored_at_plan_time: true
---

# Phase 01 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register authored at plan time across the three PLAN files. The audit verified that
each declared mitigation is actually present, by running commands rather than reading
claims. No implementation file was modified by the audit.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Process → environment | `EPISTEMIC_OS_DB_URL` and `EPISTEMIC_OS_TEST_REQUIRE_DB` are read from the ambient environment by `testenv` | A DSN (user, password, host, database name); a presence-only flag |
| Process → test output / CI log | Every skip-or-fail message from `testenv.Pool` and `testenv.Fixture` | Failure text; **includes DSN user and database name — see T-01-02** |
| Process → local PostgreSQL | `pgxpool` connection to the compose service | Test fixtures and rows; compose-default credentials |
| Repository → working tree | The hash-pinned fixture `testdata/demo.md`, moved during the 01-03 unreadable-fixture proof | File bytes pinned by SHA-256 |
| Host toolchain → phase evidence | GNU Make installed mid-phase; `make gate` produced the phase's central measurements | Executable code — see T-01-SC |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-01 | Information Disclosure | `testenv.Pool`, `pgxpool.New` parse-error branch | medium | mitigate | `t.Fatal(unparseableURLMsg)` — argument-free const, no verbs, both modes. Re-measured: leak token 0 on both DSN forms, `cannot parse` absent, status 1. Control test passes and was proven able to detect the token. | closed |
| T-01-02 | Information Disclosure | `testenv.Pool`, the `Ping` error branch | medium | mitigate + **accept (residual)** | Declared control present and working: `hostFromURL` returns `net/url` Host only, never userinfo; sole host-text source; control test passes. **Residual disclosure of user and database name accepted — see AR-01.** | open — below `high` threshold (non-blocking) |
| T-01-03 | Tampering | `EPISTEMIC_OS_TEST_REQUIRE_DB` | low | accept | Presence-based; every unmet condition calls `Skipf`/`Fatal` and never returns a pool, so tampering cannot manufacture a false pass. Default suite re-measured: 38 skips, exit 0. | closed |
| T-01-04 | Denial of Service | 5s connect timeout in `testenv.Pool` | low | accept | `testenv.go:98`, covers both `pgxpool.New` and `Ping`; identical to the phase-base helper. | closed |
| T-01-05 | Tampering | `path` parameter of `testenv.Fixture` | low | accept | Exactly one call site repo-wide, a compile-time literal. No variable, env, or user input reaches the parameter. | closed |
| T-01-06 | Tampering | `testdata/demo.md` and its pinning constants | medium | mitigate | `fixtureSHA256`/`fixtureBytes` byte-identical to base; length and hash checks both run before any offset assertion; on-disk hash equals the pin. | closed |
| T-01-07 | Repudiation | AC-14 content-conditional declines | medium | mitigate | `git diff --name-only 868d45b..HEAD -- acceptance_test.go` empty (anchored, not `HEAD`); both declines present; `t.Skip` count 2 == 2 at base. | closed |
| T-01-08 | Tampering | Line-ending conversion on checkout | low | accept | `.gitattributes` marks the fixture `-text`; CR scan in `fixture_test.go`; on-disk hash matches, so no CRLF rewrite occurred. | closed |
| T-01-09 | Information Disclosure | DSNs constructed in Scenarios C and D | medium | mitigate | Scenario D re-run on both DSN forms: token 0, `cannot parse` absent, status non-zero. Scenario DSNs carry throwaway values by construction. | closed |
| T-01-10 | Tampering | `testdata/demo.md` during the 01-03 Task 2 move | **high** | mitigate | **The only entry at or above `block_on`.** Verified as a guard, not as luck — see the note below the table. | closed |
| T-01-11 | Elevation of Privilege | Local compose PostgreSQL instance | low | accept | Accepted rationale said "loopback port". **Measured false** — the service binds `0.0.0.0`. Re-accepted with a corrected rationale — see AR-02. | open — below `high` threshold (non-blocking) |
| T-01-12 | Repudiation | The escalated-green measurement | medium | mitigate | Re-measured against the live database: baseline skip set 38, escalated pass set 42, `comm -23` empty, escalated exit 0 with test-level skip count 0. The measurement is real. | closed |
| T-01-13 | Tampering | The negative proof procedure | low | accept | No `os.WriteFile`/`Rename`/`Remove`/`Create` anywhere in `fixture_test.go`; the control drives synthetic values. The mutate-and-restore surface is genuinely absent. | closed |
| T-01-14 | Repudiation | The phase base commit in the manifest | medium | mitigate | All five anchor assertions re-run live; manifest `status: approved`, `868d45b`, Alex Zamurko, 2026-09-01; freeze `FROZEN` at `8edae22`; approval detector verified in both directions; base-independent blob pins hold. | closed |
| T-01-SC | Tampering | Dependency installation | low | accept | Accepted rationale said "no package-manager install task exists". **Refuted by the execution record** — a winget install ran mid-phase. Re-accepted with a corrected rationale — see AR-03. | open — below `high` threshold (non-blocking) |

*Status: open · closed · open — below `high` threshold (non-blocking)*
*Only open threats at or above `block_on: high` count toward `threats_open`. All three open items are `medium` or `low`.*

### T-01-10 — closed as a guard, not as an outcome

The only `high` entry, and the one that could have blocked the phase. A fixture that
happens to be intact is not evidence that a guard would have held, so the auditor
executed both spellings of the restore procedure against a throwaway stand-in with the
inbound `mv` forced to fail. The real fixture was never touched.

| Spelling | Exit | Fixture in tree | Trap |
|---|---|---|---|
| Old (`;`-separated, the cycle-2 finding) | 1 | **ABSENT — corrupt tree** | already disarmed |
| Corrected (the plan's verbatim acceptance criterion) | 1 | present, hash matches | `RESTORE_FAILED_TRAP_ARMED` — trap fired and restored |

The trap-clearing statement is unreachable except on a proven-restored path. The
mitigation would have held under failure, which is what "closed" is supposed to mean.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-01-02 | **DSN user and database name are disclosed in test output on the unreachable-database path, in BOTH modes.** Measured with a meaningful DSN: escalated (`Fatalf`) status 1, and non-escalated (`Skipf`) **status 0** — the exit-0 path an ordinary developer or CI run takes — each printing `user=` and `database=` 33 times. The password is redacted by pgx (count 0) on every shape tested. Accepted because impact at pgx v5.7.2 is DSN metadata, not credentials, and the error carries the dial diagnosis Phase 3's PROOF-02 asserts against; removing it was raised in cross-AI planning review and rejected with rationale. **The scope this was originally accepted under is FALSE, not merely unenforced.** T-01-02's frozen rationale accepts the disclosure *"at `medium` for a test-only helper against a **loopback compose service**"* — and that compose service binds `0.0.0.0:5432`, not loopback, as measured and recorded in **AR-02**. The auditor flagged this directly: *"the same false premise is load-bearing for two acceptances."* So two things are wrong with the original boundary, not one: nothing in `testenv.Pool` restricts which DSN it prints from (unenforced), AND the service the acceptance named as its containment is reachable from the local network (untrue). The residual is accepted anyway — impact at pgx v5.7.2 is DSN metadata, not credentials, and no production data is reachable — but it is accepted on the measured facts, not on the original rationale, which no longer holds. **Phase 2 must re-weigh this before enforcement makes this helper decide whether CI goes red**, and must not inherit the loopback assumption. See AR-02. | Pending operator sign-off | 2026-09-01 |
| AR-02 | T-01-11 | **The compose PostgreSQL binds `0.0.0.0:5432`, not loopback.** `docker-compose.yml:9` declares `"5432:5432"`, which Docker publishes on all interfaces; live: `0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp`. With guessable defaults (`epistemicos`/`epistemicos`) the instance is reachable from the local network. The original acceptance said "loopback port" — that premise is false. Accepted as a local development service holding only test fixtures, with **no production data reachable**, and **not a regression of this phase**: `docker-compose.yml` is byte-unchanged since the phase base. Loopback-only would be `"127.0.0.1:5432:5432"`. | Pending operator sign-off | 2026-09-01 |
| AR-03 | T-01-SC | **A package-manager install ran mid-phase and produced the phase's central evidence.** `go.mod`/`go.sum` are byte-unchanged since the base, so the original rationale holds for Go dependencies — but GNU Make 4.4.1 (`ezwinports.make`) was installed via winget during 01-03 and placed at `C:/Users/gupta/bin/make.exe`, and that binary executed every `make gate` run behind this phase's central claim. Operator approval was obtained and recorded before installing (a real control, and the executor correctly halted rather than self-approving). Provenance now on record: winget `ezwinports.make` 4.4.1, publisher ezwinports (Eli Zaretskii, sourceforge.net/projects/ezwinports), GPL-3.0, installer hash verified by winget at install time; on-disk `make.exe` sha256 `cc6dc291113dcbcc7735835acbfc23c52ed037e4e124ff2d7a0aeae6df563a9f`. Accepted; no legitimacy audit was performed beyond winget's own hash verification. | Pending operator sign-off | 2026-09-01 |

**These three are open, not closed.** They are recorded here so they do not resurface as
undiscovered findings. **All three** exist because a written rationale was contradicted by
measurement — AR-02 on the loopback binding, AR-03 on "no package-manager install task
exists", and AR-01 on the same loopback premise AR-02 falsifies. That is worth more
attention than a clean register would have been.

**Amendment, 2026-09-01, at the operator's instruction before signing.** AR-01 originally
said only that the scope was *not enforced by code*. It did not say that the scope as
originally stated was *factually false*, so it read as a residual with a loose boundary
rather than one whose stated boundary had been measured wrong — and it would have been
signed still leaning on loopback. Alex asked for the three entries to be quoted in full
before signing, which is how the omission was found. The count in the audit trail below
was "two rationales contradicted"; it is three.

---

## Unregistered attack surface

No `## Threat Flags` section exists in any of the three SUMMARYs, so that channel
supplied nothing. Two pieces of surface appeared during implementation that no threat
entry anticipated. Both are folded into the open threats above rather than
double-counted:

- **Mid-phase host-toolchain install** (winget → `make.exe` on PATH) — recorded against T-01-SC / AR-03.
- **Compose service on `0.0.0.0`**, contradicting two acceptance rationales — recorded against T-01-11 / AR-02, and load-bearing for AR-01's scope claim.

---

## Residual noted for the record (not an open threat)

`01-03-SUMMARY.md` records that the **unescalated** preserved-fixture-skip run did not
use a verbatim-specified command: the plan spells the trap verbatim only for the
escalated case, so the executor reconstructed it by substituting
`env -u EPISTEMIC_OS_TEST_REQUIRE_DB`. No transcript of that single invocation
survives, so it cannot be confirmed by artifact that all four guards were present in
it. Outcome evidence contradicts harm — fixture byte-identical to the pin, integrity
test green, no deletion in `git status` — and the guard shape is proven fail-closed, so
T-01-10 stays closed. **A future plan that says "use the procedure below" should spell
the command for every invocation that uses it.**

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-01 | 15 | 12 | 3 (0 blocking) | gsd-security-auditor (opus), ASVS L1, `block_on: high` |

Audit hygiene: no implementation file modified, no file written by the auditor.
Repository untouched — same three untracked byproducts, fixture hash unchanged, 0 paths
outside `internal/` and `.planning/` in the diff from base, compose `postgres` left
running per 01-03's declared end state. Stand-in reproductions ran only under the
scratchpad directory.

Orchestrator spot-checks of the auditor's three open findings: compose binding
`0.0.0.0:5432` **confirmed**; `docker-compose.yml` unchanged since base **confirmed**;
`make.exe` sha256 **confirmed**; T-01-02 residual **confirmed** at 33 occurrences each
of user and database name on both paths, password 0.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log (AR-01, AR-02, AR-03)
- [x] `threats_open: 0` confirmed — no open threat at or above `block_on: high`
- [x] `status: verified` set in frontmatter
- [ ] **Operator sign-off on AR-01, AR-02, AR-03** — the three acceptances are recorded
      but not yet signed. Two of them replace a rationale that measurement contradicted,
      so they are a decision, not a formality.

**Approval:** verified 2026-09-01 (automated audit) — operator sign-off pending on the
three accepted risks.
