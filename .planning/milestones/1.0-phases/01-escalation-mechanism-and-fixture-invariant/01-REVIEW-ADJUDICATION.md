---
phase: 01-escalation-mechanism-and-fixture-invariant
adjudicates: 01-REVIEW.md
adjudicated_by: orchestrator (/gsd-execute-phase 01)
adjudicated_on: 2026-09-01
review_commit: c606fe6
disposition: finding upheld on fact, severity corrected, one supporting claim refuted
amended_on: 2026-09-01
amendment: >-
  Corrected during /gsd-secure-phase 01. The first version cited T-01-01 and T-01-09 as
  the covering threat entries and missed T-01-02, which addresses the Ping branch directly.
  It also credited CR-01's proposed fix as a fresh, viable improvement and queued it for
  Phase 2, when cross-AI review had already raised and rejected that exact remediation.
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

- **T-01-02** (`01-01-PLAN.md`) — *"`testenv.Pool`, the `Ping` error branch"*, `medium`,
  disposition `mitigate`. **This is the on-point entry.** It names the branch CR-01
  names, states the disclosure in as many words — *"It does disclose the user and
  database name; accepted at `medium` for a test-only helper against a loopback compose
  service"* — and records the mitigation actually taken: host text is derived only via
  `hostFromURL`, which returns `net/url`'s Host and so never the userinfo component,
  pinned by a unit test whose negative control first proves it can detect a leak.
- **T-01-01** (`01-01-PLAN.md`) — the `pgxpool.New` parse-error branch, `medium`.
- **T-01-09** (`01-03-PLAN.md`) — the DSNs in Scenarios C and D, `medium`.

**Correction to the first version of this adjudication.** It cited only T-01-01 and
T-01-09 and missed T-01-02 — the entry written specifically about this branch. The
conclusion does not change, and the evidence for it is stronger than first stated: the
phase did not merely cover this disclosure incidentally under a neighbouring threat, it
has a dedicated entry for precisely this code path.

T-01-01 and T-01-09 were **corrected downward from `high`** during cycle-1 review, on
measurement: pgx redacts the password on all four DSN shapes tested, so the impact at
the pinned version is DSN-metadata disclosure, not credential disclosure. Both state
the consequence explicitly — *"below `security_block_on: high`, so no longer
phase-blocking."* T-01-02 was authored at `medium` and never carried a higher rating.

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

### The proposed remediation was ALREADY RAISED AND REJECTED

**This section replaces an error in the first version of this adjudication**, which
credited the remediation as a fresh, viable improvement and queued it for Phase 2. It
is not fresh. Cross-AI review raised the identical proposal during planning, and
`01-01-PLAN.md` records it under **Rejected, with rationale**:

> *"Prefer emitting a stable error category for `Ping` rather than appending the
> complete pgx error"* — MEDIUM — *"…it carries the dial diagnosis Phase 3's PROOF-02
> needs to assert against. Dropping it would replace real diagnosis with a category
> name."*

So CR-01's fix is not an unconsidered improvement the phase overlooked. It is a
proposal the phase considered, argued against in writing, and declined. Re-raising it
without engaging that rationale is the same failure as re-grading the severity without
engaging the threat model.

What the first version got right and still stands: dropping `err` would not break
Phase 1's own criteria. `01-01-PLAN.md` verification item 6 and `01-03-PLAN.md`
Scenario C require the escalated closed-port failure to **name the host and port**, and
`hostFromURL` returns `parsed.Host`, which already carries the port (`127.0.0.1:1`)
and is interpolated separately from `err`. The constraint is not Phase 1. The
constraint is Phase 3.

**A live question this exposes, for Phase 3 rather than for me.** The rejection rests
on PROOF-02 needing the dial diagnosis. REQUIREMENTS.md states PROOF-02 as: *"An
automated test proves the gate fails and **names the unreachable host** when the
database cannot be reached."* Naming the host is satisfied by `hostFromURL` alone,
without `err`. The rejection's stated reason may therefore be broader than PROOF-02
literally requires. That is a real question — it is not resolved here, and it is not
resolved by asserting either reading. It belongs to whoever writes Phase 3, who will
know what the proof actually needs to assert against.

**Residual worth carrying forward.** The disclosure occurs on the non-escalated skip
path too, which is the path ordinary developer and CI runs take. The acceptance
statements are scoped: T-01-09 to *"the DSNs constructed in Scenarios C and D,"* which
carry throwaway values, and T-01-02 to *"a test-only helper against a loopback compose
service."* Both scopes hold for how this repository runs today — the CI DSN is the
compose default on localhost.

Neither scope covers a DSN pointing somewhere real with a meaningful username or
database name. Nothing in `testenv.Pool` enforces the loopback assumption the
acceptance rests on; it is a property of current usage, not of the code. That is the
strongest form of the review's point, it is the reason CR-01 is upheld rather than
dismissed, and it is what Phase 2 should weigh when it turns enforcement on and the
same helper starts deciding whether CI goes red.

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
