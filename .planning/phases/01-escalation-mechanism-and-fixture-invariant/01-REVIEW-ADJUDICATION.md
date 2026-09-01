---
phase: 01-escalation-mechanism-and-fixture-invariant
adjudicates: 01-REVIEW.md
adjudicated_by: orchestrator (/gsd-execute-phase 01)
adjudicated_on: 2026-09-01
review_commit: c606fe6
disposition: finding upheld on fact, severity corrected, one supporting claim refuted
---

# Adjudication of 01-REVIEW.md

`01-REVIEW.md` is committed unaltered at `c606fe6`. This file records where the
orchestrator agrees with it and where it does not, with evidence. Nothing in the
review was edited, downgraded in place, or removed.

## CR-01 — Ping error discloses `user=` and `database=`

**Severity as filed: BLOCKER (critical). Adjudicated: MEDIUM, not phase-blocking.**

### The behavioural claim is CONFIRMED

`internal/platform/testenv/testenv.go` forwards the `pool.Ping(ctx)` error via `%v`
into both the `Fatalf` and `Skipf` messages, and pgx v5.7.2 builds that error from
the parsed config, so the username and database name reach test output. Observed
directly:

```
cannot reach postgres at 127.0.0.1:1 (from EPISTEMIC_OS_DB_URL):
  failed to connect to `user=u database=nodb`: 127.0.0.1:1 (127.0.0.1): dial error: ...
```

Two independent sources agree. The reviewer reproduced it with a throwaway program
against an unreachable port. The phase's own measured ground truth recorded the same
thing before any code was written (`01-03-PLAN.md`, "Verified ground truth"):

> The `Ping` error is built by the library from the parsed config, not the raw DSN:
> ``failed to connect to `user=u database=nodb`: …``. It names the host, omits the
> password, and **discloses the user and database name.**

The reviewer found something real. It did not find something new.

### The BLOCKER grade is NOT supported

This exact disclosure is already in the phase's threat model, assessed and graded:

- **T-01-01** (`01-01-PLAN.md`) — `testenv.Pool`, information disclosure, `medium`.
- **T-01-09** (`01-03-PLAN.md`) — the DSNs in Scenarios C and D, `medium`.

Both were **corrected downward from `high`** during cycle-1 review, on measurement:
pgx redacts the password on all four DSN shapes tested, so the impact at the pinned
version is DSN-metadata disclosure, not credential disclosure. Both entries state the
consequence explicitly — *"below `security_block_on: high`, so no longer
phase-blocking."*

A finding cannot be a blocker for a phase that measured it, graded it, wrote down why
it is medium, and shipped on that basis. Re-grading it BLOCKER without engaging that
reasoning substitutes a fresh first impression for a recorded, evidenced decision.
The severity is corrected to `medium`. The finding stays on the record.

### One supporting claim is REFUTED

The review states the code carries *"the doc comment's (incorrect) claim of safety."*
It does not. The comment reads:

> The Ping error is measured to be built by pgx from the parsed config, not from the
> raw DSN, and is **kept** because it carries the dial diagnosis the unreachable-host
> proof asserts against; **the connection string itself is still never interpolated
> here.**

Both halves are true, and the claim is narrower than the review read into it. It
asserts that the raw DSN string is never interpolated — correct, the message is built
by pgx from the parsed config — not that no metadata is disclosed. The word "kept"
states plainly that the error is retained on purpose. The comment is an accurate
record of a deliberate decision, not a false assurance.

### The proposed remediation is VIABLE, and belongs to Phase 2

The review proposes dropping `err` from the message, matching the `unparseableURLMsg`
pattern. Checked against the criteria that constrain this message:

- `01-01-PLAN.md` verification item 6 and `01-03-PLAN.md` Scenario C both require the
  escalated closed-port failure to **name the host and port**.
- `hostFromURL` returns `parsed.Host`, which already carries the port (`127.0.0.1:1`),
  and it is interpolated separately from `err`.

So dropping `err` would still satisfy both criteria. The remediation is sound and
cheap, and the review deserves credit for it. It is nonetheless **out of scope for
Phase 1**, which is frozen at `c96ecb2`, complete, and deliberately shipped this as an
accepted `medium`. It is queued for Phase 2 disposition alongside the five contract
decisions.

**Residual worth carrying forward:** the disclosure occurs on the non-escalated skip
path too, which is the path ordinary developer and CI runs take. T-01-09 scopes its
acceptance to "the DSNs constructed in Scenarios C and D," which carry throwaway
values. A real DSN with a meaningful username or database name is outside what that
entry actually assessed. That gap is the strongest form of the review's point and is
the reason the finding is upheld rather than dismissed.

## CR-02, CR-03 — INFO

Accepted as filed, no adjustment.

- `hostFromURL`'s `"did not parse to one"` fallback conflates a malformed DSN with a
  valid keyword/value DSN that simply has no URL host. Cosmetic today; worth fixing
  when the message is next touched.
- `Fatalf`/`Skipf` message duplication across the three skip-or-fail sites is a drift
  risk, not a bug. Phase 3 asserts against these strings verbatim, which raises the
  cost of drift and argues for consolidating them into constants before then.

## What the review confirmed clean

Recorded because a review's negative results are evidence too, and this phase's
central claims are exactly what it checked:

- `Required()` is genuinely presence-based — `"0"` enables escalation, so a typo errs
  toward enforcing rather than toward a vacuously green gate. Covered by `TestRequired`.
- The non-escalated path still skips on every condition — no CI-reddening regression.
- `unparseableURLMsg` is argument-free, with a working negative control.
- `preambleInvariant` gates narrowly: the no-headings check is unconditional and runs
  ahead of the `declaredHasPreamble` waiver, so the declaration is not a blanket waiver.
- All six store/adapter test files use per-test UUIDs with `t.Cleanup` — no test-order
  dependency, consistent with the `-shuffle=on` results.
