---
phase: 01-escalation-mechanism-and-fixture-invariant
reviewed: 2026-09-01T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - internal/platform/testenv/testenv.go
  - internal/platform/testenv/testenv_test.go
  - internal/adapters/secondary/store/segmentation_test.go
  - internal/adapters/secondary/store/authorreturn_test.go
  - internal/adapters/secondary/store/researchunit_test.go
  - internal/adapters/secondary/store/runrejection_test.go
  - internal/adapters/secondary/store/segmentation_decision_test.go
  - internal/adapters/secondary/approved/papers_test.go
  - internal/core/domain/segment/fixture_test.go
findings:
  critical: 1
  warning: 0
  info: 2
  total: 3
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-09-01
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

The escalation/skip logic in `testenv.go` gets the three headline properties right:
`Required()` is genuinely presence-based (`"0"` enables escalation, verified by
`TestRequired`), the non-escalated path still skips on every unmet condition, and the
`unparseableURLMsg` branch is a correctly argument-free constant with a negative
control (`TestUnparseableURLMsg_Control_NoLeak`) proving it. `preambleInvariant` in
`fixture_test.go` gates narrowly — the no-headings check runs unconditionally before
the `declaredHasPreamble` gate is consulted, so the waiver cannot swallow the one
check that must never be skipped. Test isolation across all six store/adapter test
files is sound: every fixture uses a fresh `uuid.NewString()` id and registers its own
`t.Cleanup`, so there is no ordering dependency between tests.

However, one of the connection-string-disclosure properties this phase exists to
guarantee does not actually hold. Priority #4 asks specifically whether "no component
of the DSN (user, host, database name, query parameters) may reach test output" — and
on the unreachable-database path, it does not. This was verified empirically (see
CR-01), not merely inferred from reading the code: `pgxpool.Pool.Ping`'s error, when
the pool cannot connect, is (or wraps) a `*pgconn.ConnectError`, whose `Error()`
method in pgx v5.7.2 literally formats `` failed to connect to `user=%s database=%s`: ``
from the pool's parsed config. `testenv.Pool` forwards that error verbatim via `%v`
into both the `Fatalf` and `Skipf` messages, so the username and database name from
`EPISTEMIC_OS_DB_URL` reach test output (and therefore CI logs) on every unreachable-
database run — exactly the class of leak the package's own doc comment says the
`unparseableURLMsg` constant was designed to prevent, just reached through a different
branch that was not given the same treatment.

## Critical Issues

### CR-01: Ping-failure branch leaks the DSN's username and database name

**File:** `internal/platform/testenv/testenv.go:113-129`

**Issue:** When `pool.Ping(ctx)` fails, the code forwards `err` verbatim via `%v` into
both `t.Fatalf` (escalated) and `t.Skipf` (non-escalated):

```go
if err := pool.Ping(ctx); err != nil {
    pool.Close()

    host := hostFromURL(dsn)
    if host == "" {
        host = "<unknown host — " + URLEnv + " did not parse to one>"
    }

    if Required() {
        t.Fatalf("cannot reach postgres at %s (from %s): %v", host, URLEnv, err)
    }
    t.Skipf("cannot reach postgres at %s (from %s): %v", host, URLEnv, err)
}
```

The surrounding comment claims this is safe because the error "is measured to be
built by pgx from the parsed config, not from the raw DSN." That claim is true but
does not establish safety — the parsed config carries the username and database name
exactly as much as it carries the host, and pgx's own `ConnectError` type formats
those two fields directly into its error string.

I verified this empirically against the pinned version (`github.com/jackc/pgx/v5
v5.7.2`, confirmed via `go.mod`). Reading
`pgconn/errors.go` in the module cache:

```go
func (e *ConnectError) Error() string {
	prefix := fmt.Sprintf("failed to connect to `user=%s database=%s`:", e.Config.User, e.Config.Database)
	...
}
```

and reproducing it with a throwaway program against an unreachable port (no real
database involved — a pure dial failure, the same class `Pool` hits when postgres is
down):

```
dsn := "postgres://secretuser:secretpw@127.0.0.1:1/secretdbname?sslmode=disable"
pool, _ := pgxpool.New(ctx, dsn)
err := pool.Ping(ctx)
fmt.Println(err)
```
```
Ping err: failed to connect to `user=secretuser database=secretdbname`: 127.0.0.1:1 (127.0.0.1): dial error: dial tcp 127.0.0.1:1: connectex: ...
```

The username and database name appear in the error text even for the simplest
"nothing is listening on that port" case — no authentication attempt is needed to
trigger it, because pgx builds the message from `Config.User`/`Config.Database`
unconditionally in `ConnectError.Error()`, before any wire-protocol exchange happens.
`testenv.Pool` then puts that string straight into the test's `Fatalf`/`Skipf`
message with `%v`, so it lands in CI output on every unreachable-database run, in
both escalation modes. This is the exact disclosure vector `unparseableURLMsg`
(lines 40-48) was written to prevent on the parse-failure path; the Ping-failure path
was not given the equivalent treatment, and the doc comment's safety argument for it
is incorrect.

Password is not at risk here (pgx does redact it, and `%v` on `ConnectError` never
includes it), but username and database name are two of the four components priority
#4 explicitly names as forbidden, and they leak unconditionally on this path.

**Fix:** Do not interpolate `err` into the message at all — treat this branch the
same way `unparseableURLMsg` treats the parse-failure branch, and use the
already-redacted `host` plus a fixed, argument-free classification instead:

```go
if err := pool.Ping(ctx); err != nil {
    pool.Close()

    host := hostFromURL(dsn)
    if host == "" {
        host = "<unknown host — " + URLEnv + " did not parse to one>"
    }

    // The pgx error is deliberately withheld: pgconn.ConnectError.Error()
    // (v5.7.2) formats "failed to connect to `user=%s database=%s`: ..."
    // directly from the pool's config, so forwarding it verbatim — even on
    // a plain dial failure, with no authentication attempted — publishes
    // the DSN's username and database name to test output.
    const msg = "cannot reach postgres at %s (from %s); the underlying pgx error is withheld because it embeds the connection string's username and database name"
    if Required() {
        t.Fatalf(msg, host, URLEnv)
    }
    t.Skipf(msg, host, URLEnv)
}
```

If the dial diagnosis genuinely needs to survive for debugging, it must be extracted
through an allow-listed unwrap (e.g. checking for a `*net.OpError` via `errors.As`
and reporting only its `Op`/`Err` text) rather than ever calling `.Error()` or `%v`
on the top-level `err`, since any wrapper pgx puts around it may carry the same
`user=`/`database=` prefix.

## Info

### IN-01: `hostFromURL`'s fallback text conflates "malformed" with "no host component"

**File:** `internal/platform/testenv/testenv.go:116-119`

**Issue:** `hostFromURL` returns `""` both when `raw` fails to parse and when it
parses successfully but has no URL host (a keyword/value DSN such as `host=x
port=5432 ...`, or a Unix-socket-style `postgres:///dbname`). `Pool` then always
substitutes `"<unknown host — %s did not parse to one>"` for the empty string,
which is factually wrong in the second case — the value did parse, it just isn't in
URL form. This doesn't leak anything and doesn't change the skip/fail decision, but
it can send a developer looking for a "parse error" that doesn't exist when the real
cause is a keyword/value DSN.

**Fix:** Either word the fallback message more neutrally ("host not determinable from
%s") or have `hostFromURL` distinguish the two cases (e.g. return a `(string, bool)`
pair, or a sentinel) so `Pool` can report which one actually happened.

### IN-02: Near-duplicate Fatalf/Skipf message pairs

**File:** `internal/platform/testenv/testenv.go:92-95, 125-128, 151-154`

**Issue:** All three skip-or-fail decision points repeat the same message text once
for the `Fatalf` branch and once for the `Skipf` branch, differing only in which
`testing.T` method is called. This is a minor duplication (three call sites, two
lines each) rather than the kind the 38-call-site unification in this phase was
aimed at, but it is a source of drift risk: a future edit to one branch's wording
that misses its twin would make the escalated and non-escalated messages
inconsistent for the same cause.

**Fix:** Not urgent, but a small helper such as
`func skipOrFail(t *testing.T, format string, args ...any)` that centralizes the
`if Required() { t.Fatalf(...) } else { t.Skipf(...) }` branch would remove the
duplication and make CR-01's fix (a single shared message string) easier to apply
consistently across all three call sites.

---

_Reviewed: 2026-09-01_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
