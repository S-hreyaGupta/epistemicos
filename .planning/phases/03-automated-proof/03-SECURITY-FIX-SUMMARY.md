---
phase: 03
slug: automated-proof
type: security-fix
status: complete
tags: [security-fix, T-03-14, control-drift]
requires: []
provides: [T-03-14-closed, gateproof-control-drift-closed]
affects: [internal/adapters/secondary/store/migrate.go, internal/platform/gateproof/tree_drain_test.go, internal/platform/gateproof/gateproof_test.go]
key-files:
  modified:
    - internal/adapters/secondary/store/migrate.go
    - internal/platform/gateproof/tree_drain_test.go
    - internal/platform/gateproof/gateproof_test.go
    - .planning/phases/03-automated-proof/03-SECURITY.md
key-decisions:
  - "T-03-14 fixed by substituting an argument-free constant for the *url.Error branch only, mirroring testenv.go's unparseableURLMsg discipline exactly — no fmt verb, no argument position a connection-string-derived value could occupy."
  - "AR-01's accepted pgx dial-failure disclosure (user=/database=, password redacted) was left untouched by design — the fix discriminates narrowly on errors.As(*url.Error), verified live to leave the well-formed-but-unreachable control case byte-identical before and after."
  - "Control-drift fix scoped to the one missing gate.SkipIfNested(t) call in TestMaterializeTree_DrainsPastTarEOF; gateproof_test.go's doc comment corrected to name TestHelperProcess_TarWithTrailer as the documented (and legitimate) exception, rather than silently leaving 'every test' literally false."
actuals:
  tokens: 9800
  tasks: 5
  commits: 2
duration: "~45 min"
completed: 2026-09-04
---

# Phase 3 Security Fixes: T-03-14 password leak + gateproof control drift

Two independent, unrelated-file fixes from the 2026-09-04 Phase 3 security audit
(`03-SECURITY.md`): a real, live password leak on `store.RunMigrations`'s
`net/url.Parse`-failure branch (T-03-14), and a false "every test calls
`SkipIfNested` first" invariant claim caused by `TestMaterializeTree_DrainsPastTarEOF`
missing that call.

## Accomplishments

1. **T-03-14 closed** — `store.RunMigrations`'s `*url.Error` branch (from a malformed
   `EPISTEMIC_OS_DB_URL`) no longer forwards golang-migrate's wrapped error, which
   embedded the raw connection string (including password) verbatim via `net/url.Error`'s
   own `Error()` rendering, printed unredacted by `cmd/epistemicos-cli/main.go`'s `die()`.
   Fixed with an argument-free constant, `unparseableURLMsg`, discriminated via
   `errors.As(err, &urlErr)` on exactly the `*url.Error` case — every other error from
   `migrate.NewWithSourceInstance` (notably pgx's own dial-failure diagnostics, accepted
   under AR-01) is forwarded unchanged.
2. **Control drift closed** — `TestMaterializeTree_DrainsPastTarEOF` now calls
   `gate.SkipIfNested(t)` as its literal first statement, like every other real test in
   `internal/platform/gateproof/`. `gateproof_test.go`'s package doc comment corrected to
   name the one legitimate, documented exception (`TestHelperProcess_TarWithTrailer`, a
   subprocess entry point, not a real test) instead of asserting an unqualified "every
   test" that a mechanical enumeration falsifies.

## Deviations from Plan

None — plan executed exactly as written. Both fixes were scoped exactly as directed:
`migrate.go` only for T-03-14, and `tree_drain_test.go`'s one-line guard (plus the
necessary `gateproof_test.go` doc-comment correction the task's own verification step
called for) for the control drift.

## Falsifiability Demonstration — T-03-14 (Task 2)

All captures below use only a synthetic, non-real credential
(`FAKE_SYNTHETIC_SECRET_XYZ`). Never a real credential, anywhere.

### (a) BEFORE fix — parse-failure branch (leaking)

Command:
```
EPISTEMIC_OS_DB_URL='postgres://epistemicos:FAKE_SYNTHETIC_SECRET_XYZ@127.0.0.1:notaport/epistemicos' \
  go run ./cmd/epistemicos-cli migrate up
```

Captured output, verbatim:
```
new migrator: failed to open database: parse "pgx5://epistemicos:FAKE_SYNTHETIC_SECRET_XYZ@127.0.0.1:notaport/epistemicos": invalid port ":notaport" after host
exit status 1
```

The synthetic secret appears verbatim — the leak, reproduced.

### (b) AFTER fix — parse-failure branch (safe)

Same command, run after the fix (commit `f75949d`):

```
new migrator: connection string is not a usable PostgreSQL URL; the value and the underlying library error are deliberately withheld here, since both carry the connection string
exit status 1
```

Occurrences of `FAKE_SYNTHETIC_SECRET_XYZ` in this output: **0** (grep -c confirmed 0).

### (c) Control case — well-formed-but-unreachable DSN, BEFORE and AFTER

Command:
```
EPISTEMIC_OS_DB_URL='postgres://epistemicos:FAKE_SYNTHETIC_SECRET_XYZ@127.0.0.1:1/epistemicos?connect_timeout=2' \
  go run ./cmd/epistemicos-cli migrate up
```

Captured output — **identical before and after the fix** (`diff` confirmed no
difference):
```
new migrator: failed to open database: failed to connect to `user=epistemicos database=epistemicos`:
	127.0.0.1:1 (127.0.0.1): dial error: dial tcp 127.0.0.1:1: connectex: No connection could be made because the target machine actively refused it.
	127.0.0.1:1 (127.0.0.1): dial error: dial tcp 127.0.0.1:1: connectex: No connection could be made because the target machine actively refused it.
exit status 1
```

Occurrences of `FAKE_SYNTHETIC_SECRET_XYZ`: **0**, both before and after. `user=` and
`database=` are present, matching AR-01's already-accepted pgx dial-failure disclosure
exactly. **The discriminator was not broadened** — this confirms the fix narrowly targets
the `*url.Error` parse-failure branch and leaves every other error path (including AR-01's
accepted residual) untouched.

## Control-Drift Fix — Depth Re-measurement (Task 3)

### Depth 0 (normal, non-nested `go test`)

Before and after the fix, `TestMaterializeTree_DrainsPastTarEOF` runs identically:
```
=== RUN   TestMaterializeTree_DrainsPastTarEOF
--- PASS: TestMaterializeTree_DrainsPastTarEOF (0.48s)
PASS
```
Confirms `gate.SkipIfNested(t)` is a no-op at depth 0 — no behavior change for the
normal test-run path.

### Depth 1 (`EPISTEMIC_OS_TEST_MAKE_DEPTH=1`) — full package

**Before the fix** (7 SKIP, 2 PASS):
```
--- SKIP: TestLineContainsBoth_Control (0.00s)
--- SKIP: TestGateproof_NoParallelMarker (0.00s)
--- SKIP: TestGateOrdersPreflightBeforeMigrate (0.00s)
--- SKIP: TestPROOF01_GateNamesUnsetURL (0.00s)
--- SKIP: TestPROOF02_GateNamesUnreachableHost (0.00s)
--- SKIP: TestPROOF03_GateNamesUnreadableFixture (0.00s)
--- PASS: TestHelperProcess_TarWithTrailer (0.00s)
--- PASS: TestMaterializeTree_DrainsPastTarEOF (0.47s)   <- did not skip (the drift)
--- SKIP: TestMaterializeTree_Control (0.00s)
```

**After the fix** (8 SKIP, 1 PASS):
```
--- SKIP: TestLineContainsBoth_Control (0.00s)
--- SKIP: TestGateproof_NoParallelMarker (0.00s)
--- SKIP: TestGateOrdersPreflightBeforeMigrate (0.00s)
--- SKIP: TestPROOF01_GateNamesUnsetURL (0.00s)
--- SKIP: TestPROOF02_GateNamesUnreachableHost (0.00s)
--- SKIP: TestPROOF03_GateNamesUnreadableFixture (0.00s)
--- PASS: TestHelperProcess_TarWithTrailer (0.00s)        <- documented exception, not a real test
--- SKIP: TestMaterializeTree_DrainsPastTarEOF (0.00s)    <- now skips, matches every other real test
--- SKIP: TestMaterializeTree_Control (0.00s)
```

`TestMaterializeTree_DrainsPastTarEOF` now skips at depth 1, like every other real test.

### Doc-comment claim re-verified, not assumed

Mechanically enumerated the first statement of every `func Test*` in
`internal/platform/gateproof/*.go` after the fix:

| File | Test | First statement |
|---|---|---|
| gateproof_test.go | TestLineContainsBoth_Control | `gate.SkipIfNested(t)` |
| gateproof_test.go | TestGateproof_NoParallelMarker | `gate.SkipIfNested(t)` |
| ordering_test.go | TestGateOrdersPreflightBeforeMigrate | `gate.SkipIfNested(t)` |
| proof01_test.go | TestPROOF01_GateNamesUnsetURL | `gate.SkipIfNested(t)` |
| proof02_test.go | TestPROOF02_GateNamesUnreachableHost | `gate.SkipIfNested(t)` |
| proof03_test.go | TestPROOF03_GateNamesUnreadableFixture | `gate.SkipIfNested(t)` |
| tree_drain_test.go | TestHelperProcess_TarWithTrailer | `if os.Getenv(tarTrailerHelperEnv) != "1" {` |
| tree_drain_test.go | TestMaterializeTree_DrainsPastTarEOF | `gate.SkipIfNested(t)` (now) |
| tree_test.go | TestMaterializeTree_Control | `gate.SkipIfNested(t)` |

`gateproof_test.go`'s original unqualified claim ("Every test in this package calls
`gate.SkipIfNested(t)` as its first statement") is **still literally false** after the
fix, because `TestHelperProcess_TarWithTrailer` — by its own doc comment, "not itself a
test of anything in this package" — never calls it. This was verified directly, not
assumed. The doc comment was corrected (not just the drift test) to name this exception
precisely, citing the measured depth-1 count (8 SKIP, 1 PASS) rather than leaving an
unqualified claim that a mechanical grep contradicts.

## Out-of-Scope Observation (not fixed, not touched)

Running the full `gateproof` package test suite (unrelated to the two files this task
scoped in) surfaced two environment-dependent behaviors in `TestPROOF03_GateNamesUnreadableFixture`,
neither caused by, nor related to, either fix in this SUMMARY:

1. Without `EPISTEMIC_OS_DB_URL` exported in the invoking shell, the nested `make gate`
   subprocess it shells out to fails at `env-preflight` (`EPISTEMIC_OS_DB_URL is not set`)
   — a pre-existing environment-setup requirement of that test, not a regression.
2. With `EPISTEMIC_OS_DB_URL` exported, a full run of `TestPROOF03_GateNamesUnreadableFixture`
   (which shells out to a real nested `make gate`, itself running `go build`, `go vet`, and
   the full test suite twice) took over 12 minutes in this session and printed a goroutine
   dump consistent with a test-binary timeout, on a sandboxed Windows shell.

Neither observation touches `migrate.go`, `tree_drain_test.go`, or `gateproof_test.go`;
`proof03_test.go` was read but not modified, per this task's explicit scope boundary.
Logged here per the deviation rules' scope-boundary guidance rather than investigated or
fixed — out of scope for this security-fix pass.

## Self-Check: PASSED

- `internal/adapters/secondary/store/migrate.go` — FOUND, contains `unparseableURLMsg` and
  `errors.As(err, &urlErr)`.
- `internal/platform/gateproof/tree_drain_test.go` — FOUND, contains
  `gate.SkipIfNested(t)` as `TestMaterializeTree_DrainsPastTarEOF`'s first statement.
- `internal/platform/gateproof/gateproof_test.go` — FOUND, doc comment corrected.
- Commit `f75949d` — FOUND in `git log --oneline --all`.
- Commit `efa54d4` — FOUND in `git log --oneline --all`.
