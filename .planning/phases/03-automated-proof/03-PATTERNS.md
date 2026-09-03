# Phase 3: Automated Proof - Pattern Map

**Mapped:** 2026-09-03
**Files analyzed:** 2 (1 new package with ~6 tests, 1 modified file)
**Analogs found:** 2 / 2 (both strong)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `internal/platform/gateproof/proof01_test.go` (PROOF-01: unset URL) | test (subprocess proof) | request-response (shell out, assert on captured output) | `internal/platform/gate/makefile_test.go:31-65` (`TestEnvPreflightIsVoiceless`) | exact — same differential/vacuity-guard shape |
| `internal/platform/gateproof/proof02_test.go` (PROOF-02: closed-port DSN) | test (subprocess proof) | request-response | `internal/platform/gate/makefile_test.go:31-65` + `closedPortDSN` const (`:12`) | exact |
| `internal/platform/gateproof/proof03_test.go` (PROOF-03: fixture-as-directory, throwaway tree) | test (subprocess proof + fixture mutation) | request-response + file-I/O | `.planning/phases/02-.../02-03-PLAN.md:527-534` (bash verification's `git archive HEAD` shape) + `makefile_test.go` (assertion shape) | role-match — the archive mechanism exists today only as a bash verification snippet, not as Go code; PROOF-03 is the first Go implementation of it |
| `internal/platform/gateproof/sc5_control_proof01_test.go` (differential control, D-11/D-13) | test (differential control) | request-response, reuses captured `RunResult` | `makefile_test.go:31-65` (differential shape) + D-16's "reuse the proof's own captured intact-tree result, guard it is real" | role-match |
| `internal/platform/gateproof/sc5_control_proof02_test.go` | test (differential control) | request-response | same as above | role-match |
| `internal/platform/gateproof/sc5_control_proof03_test.go` | test (differential control) | request-response + file-I/O (own throwaway tree, Makefile line stripped) | same as above, plus the `git archive HEAD` bash pattern | role-match |
| `internal/platform/gate/harness.go` (MODIFIED: add `RunOptions.Dir`; correct `DefaultTimeout` doc comment, tag `PROOF-03`) | config/utility (struct field + doc comment) | n/a | itself — `RunOptions` (`:134-145`), `Run`'s `cmd.Dir = RepoRoot(t)` (`:188`) | exact — this is an in-place additive edit to an existing struct, not a new pattern |

## Pattern Assignments

### `internal/platform/gateproof/proof01_test.go` / `proof02_test.go` (test, request-response)

**Analog:** `internal/platform/gate/makefile_test.go` (`TestEnvPreflightIsVoiceless`, lines 31-65) and package doc comment (`harness.go` lines 1-36 for the recursion-hazard framing).

**Imports pattern** (`makefile_test.go` lines 1-6, adapted for cross-package use):
```go
package gate

import (
	"strings"
	"testing"
)
```
For `gateproof`, add the harness import since the proof now lives outside `package gate`:
```go
package gateproof

import (
	"strings"
	"testing"

	"github.com/<module>/internal/platform/gate"
	"github.com/<module>/internal/platform/testenv"
)
```
(Confirm module path from `go.mod` before use — not read in this pass.)

**SkipIfNested-first + subprocess + vacuity guard** (`makefile_test.go` lines 31-47, this is the load-bearing shape to copy verbatim):
```go
func TestEnvPreflightIsVoiceless(t *testing.T) {
	SkipIfNested(t)

	env := []string{
		"EPISTEMIC_OS_DB_URL=" + closedPortDSN,
		"EPISTEMIC_OS_TEST_REQUIRE_ENV=TestEnvPreflightIsVoiceless",
	}
	unset := []string{"EPISTEMIC_OS_TEST_REQUIRE_DB"}

	makeSide := Make(t, "env-preflight", RunOptions{Silent: true, Env: env, Unset: unset})
	directSide := Run(t, []string{"go", "test", "./internal/platform/testenv/", "-count=1"}, RunOptions{Env: env, Unset: unset})

	// If the Make side passed, the unreachable-database condition was not
	// reproduced and every assertion below would be vacuous.
	if makeSide.ExitCode == 0 {
		t.Fatalf("make env-preflight exited 0 against a closed port — the unreachable-database condition was not reproduced; result=%+v", makeSide)
	}
```
Called from `gateproof` this becomes `gate.SkipIfNested(t)`, `gate.Make(t, "gate", gate.RunOptions{...})` per D-01 (every proof shells to `make gate`, not `env-preflight`).

**Same-line preamble+cause assertion (D-18)** — copy the "contains X" shape from lines 52-56, but bind both substrings and require them on the SAME line (`strings.Split(combined, "\n")`, loop, check both `Contains` calls on one line) rather than two independent `strings.Contains` calls against the whole `Combined` blob — that whole-blob shape is what `makefile_test.go` uses today and is explicitly NOT sufficient for D-18's proofs:
```go
if !strings.Contains(makeSide.Combined, "127.0.0.1:1") {
	t.Errorf("make env-preflight output does not name the unreachable host 127.0.0.1:1:\n%s", makeSide.Combined)
}
if !strings.Contains(makeSide.Combined, "EPISTEMIC_OS_TEST_REQUIRE_ENV") {
	t.Errorf("make env-preflight output does not carry testenv's escalation preamble (EPISTEMIC_OS_TEST_REQUIRE_ENV):\n%s", makeSide.Combined)
}
```
D-18 requires both substrings verified on the SAME line of `Combined`, since `EPISTEMIC_OS_DB_URL`/`RequireEnv` tokens can appear scattered across unrelated Makefile-help/README/skip-message lines. Write a small local helper (e.g. `lineContainsBoth(combined, a, b string) bool`) rather than reusing `extraLines`, which solves a different problem (multiset diff, not same-line conjunction).

**Constants to reuse or extend** (`makefile_test.go` lines 8-17):
```go
const closedPortDSN = "postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable"
const composeDSN = "postgres://epistemicos:epistemicos@127.0.0.1:5432/epistemicos?sslmode=disable"
```
`closedPortDSN` is `internal/platform/gate`'s unexported constant — PROOF-02 cannot import it (D-03's package boundary). Redeclare an equivalent local constant in `gateproof` with the same host token `127.0.0.1:1` (D-17: this couples to nothing, since it is test-supplied, not a golang-migrate/testenv string).

**Assertion binding targets (D-17):**
- PROOF-01 → `testenv.URLEnv` (exported, `testenv.go:37`)
- Every preamble check → `testenv.RequireEnv` (exported, `testenv.go:41`), never the unexported `escalationPreamble()` builder
- PROOF-02 → the literal host string the test itself supplies (`"127.0.0.1:1"`), never `new migrator` (golang-migrate's own text — D-15 explicitly forbids pinning to it)

---

### `internal/platform/gateproof/proof03_test.go` (test, request-response + file-I/O)

**Analog for the throwaway-copy mechanism:** `.planning/phases/02-enforcement-and-a-single-gate-definition/02-03-PLAN.md` lines 524-534 — this is currently a bash verification snippet, not Go code; PROOF-03 is the first Go implementation and must port this shape:
```bash
# NEGATIVE CONTROL — defeat the guard and the control MUST fail. This is what
# separates a load-bearing guard from a decorative one. Mutate a throwaway
# copy so the working tree is never modified.
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
git archive HEAD | tar -x -C "$TMP" || { echo "FAIL: could not materialize a clean copy"; exit 1; }
cp $F "$TMP/$F"
perl -0pi -e 's/if len\(headings\) == 0 \{/if false \{/' "$TMP/$F"
grep -q 'if false {' "$TMP/$F" || { echo "FAIL: the negative control did not apply"; exit 1; }
if ( cd "$TMP" && go test ./internal/core/domain/segment/ -count=1 -run 'TestGATE09_HeadingGuard_Control' >/dev/null 2>&1 ); then
  echo "FAIL: the control still passes with the guard defeated"; exit 1
fi
```
**End-to-end shape to port into Go (using `os/exec`, `os.MkdirTemp`, `t.Cleanup`):**
1. **Creation:** `os.MkdirTemp("", "gateproof-*")`, then run `git archive HEAD | tar -x -C <tmp>` (two piped subprocesses, or `exec.Command("git", "archive", "HEAD")` piped into `exec.Command("tar", "-x", "-C", tmp)`).
2. **Defeat edit (D-09):** inside the copy, replace `internal/core/domain/segment/testdata/demo.md` with a directory of the same name — `os.Remove` then `os.Mkdir` at that path inside the tmp tree (not deletion alone, per D-09 — must produce a genuine read failure, not an absence).
3. **Use:** `gate.Run` (not `gate.Make`, since `RunOptions.Dir` — the D-08 addition — must point at the tmp tree) invoking `["make", "gate"]` with `RunOptions{Dir: tmpDir, ...}`.
4. **Cleanup:** `t.Cleanup(func() { os.RemoveAll(tmpDir) })` immediately after the directory is created — not a bare `defer`, since D-07 explicitly notes `defer` does not survive a timeout kill and `t.Cleanup` is the idiom that does (still bounded by `DefaultTimeout`, but registered before any subprocess runs).

**Message-path assertion (D-17's PROOF-03 clause):** bind to the common suffix, not the full path — the source-of-truth call site is `internal/adapters/secondary/store/segmentation_test.go:244`:
```go
md := testenv.Fixture(t, "../../../core/domain/segment/testdata/demo.md")
```
The suffix `core/domain/segment/testdata/demo.md` is the invariant to assert `strings.Contains` against in the failure output — not the full relative literal `../../../core/domain/segment/testdata/demo.md`, and not the on-disk absolute path `internal/core/domain/segment/testdata/demo.md`. Use `strings.HasSuffix` or `strings.Contains` against exactly `"core/domain/segment/testdata/demo.md"`.

**Escalated `t.Fatalf` sites the proofs assert against** (`internal/platform/testenv/testenv.go`):
- `:149` — `Pool`, URL-unset branch: `"%s: %s is not set — export it, or run make up and export the compose DSN"` (preamble + `URLEnv`) — PROOF-01's target
- `:182` — `Pool`, unreachable-database branch: `"%s: cannot reach postgres at %s (from %s) — run make up: %v"` (preamble + host + `URLEnv` + pgx error) — PROOF-02's target
- `:212` — `Fixture`, unreadable-fixture branch: `"%s: fixture not readable at %s: %v"` (preamble + path + os error) — PROOF-03's target

All three format preamble and cause into a single `Fatalf` call — this is GATE-10's subject and D-18's structural basis; do not split the assertion across multiple `Fatalf`/`Errorf` calls when porting.

---

### `internal/platform/gateproof/sc5_control_proof0{1,2,3}_test.go` (differential controls, D-11/D-13/D-16)

**Analog:** same `makefile_test.go` differential shape, extended per D-16 to reuse the proof's own already-captured intact-tree `RunResult` rather than re-running it:

```go
// Guard: this control is not checking that the proof passed — it is checking
// that the proof RAN. A control comparing against a result that was never
// produced would be the vacuous-pass shape one indirection along.
intact := <captured RunResult from the corresponding PROOF-0N run — package-level
           var or t.Run subtest ordering ensures this ran first>
if intact.ExitCode == 0 && !<condition-specific expectation> {
    t.Fatalf("proof result unavailable or did not reproduce its condition — cannot run the differential")
}

defeated := gate.Run(t, []string{"make", "gate"}, gate.RunOptions{Dir: defeatedTmpDir, ...})

// Entailment stated in the comment per D-11: the proofs assert the gate
// fails; if the defeated tree lacks the escalation preamble, the proofs
// would fail. Proving the premise proves the consequent.
if strings.Contains(defeated.Combined, testenv.RequireEnv) {
    t.Errorf("defeated tree (escalation export stripped) still shows the escalation preamble — the differential does not discriminate")
}
```

**Defeated-tree construction (D-11):** same `git archive HEAD` mechanism as PROOF-03, plus stripping the target-scoped export at `Makefile` line 77 (`gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate`) from the copy, e.g. via `sed`/line-delete on the copied `Makefile` before running — never on the working tree's `Makefile`.

**Reporter-identity assertion (D-15):** PROOF-01's control additionally asserts `config`'s own message text in the defeated tree (project-owned reporter). PROOF-02's control must NOT assert `new migrator` (golang-migrate's own text).

---

### `internal/platform/gate/harness.go` (MODIFIED)

**Current `RunOptions` shape** (lines 133-145) — `Dir` is the only field to add, appended after the existing four, following the same one-line doc-comment-per-field convention:
```go
type RunOptions struct {
	// Env holds KEY=VALUE entries layered onto the child's environment, on
	// top of the parent's os.Environ().
	Env []string
	// Unset names variables removed from the child's environment before Env
	// is applied.
	Unset []string
	// Timeout bounds the child process. Zero means DefaultTimeout.
	Timeout time.Duration
	// Silent adds -s on the Make path (see Make).
	Silent bool
}
```
Add:
```go
	// Dir overrides the subprocess's working directory. Empty means
	// RepoRoot(t) — the historical default every existing caller relies on.
```

**Where `Dir` plugs into `Run`** (line 188, currently hard-set): change
```go
cmd.Dir = RepoRoot(t)
```
to something like
```go
dir := opts.Dir
if dir == "" {
	dir = RepoRoot(t)
}
cmd.Dir = dir
```
placed before `cmd := exec.CommandContext(...)` or immediately after, consistent with the existing `timeout := opts.Timeout; if timeout == 0 { timeout = DefaultTimeout }` idiom two lines above (lines 172-175) — copy that exact zero-value-fallback shape for `Dir`.

**`DepthEnv`-last ordering (D-08 constraint) — do NOT touch** (`buildChildEnv`, lines 224-257): `Dir` is orthogonal to environment construction; the function signature and body are untouched. Verify by re-reading only if a diff review is needed — no code path here interacts with `Dir`.

**`DefaultTimeout` doc comment correction (D-05):** current text (lines 67-73) cites warm figures (~13s/~35s) for a "roughly six times" claim. Per CONTEXT.md D-05, correct to cite the cold-cache measurement (`Cold child, no warm parent, PROOF-01 shape: 85s`) and state the margin is 2.8×, not 6×, and tag the comment `PROOF-03`:
```go
// DefaultTimeout bounds every subprocess Run spawns unless RunOptions.Timeout
// overrides it. It sits below go test's 10-minute per-package default so a
// hung child is reported as a hung child rather than surfacing as a hung
// parent. [PROOF-03] Measured cold (fresh GOCACHE, no warm parent build): the
// worst observed child, PROOF-01's shape, took 85s — a margin of 2.8×, not
// the 6× a warm-cache measurement would suggest. Calibrate future changes
// against the cold case, not the warm one.
const DefaultTimeout = 4 * time.Minute
```

---

## Shared Patterns

### SkipIfNested-first (harness contract, non-negotiable)
**Source:** `internal/platform/gate/harness.go` lines 94-108 (`SkipIfNested`), reused by every test in `makefile_test.go`.
**Apply to:** every proof and every control in `gateproof` — must be each test function's literal first statement.
```go
func SkipIfNested(t *testing.T) {
	t.Helper()
	depth, err := nestingDepth(os.Getenv(DepthEnv))
	if err != nil {
		t.Fatal(err)
	}
	if depth > 0 {
		t.Skipf("nested Make invocation at depth %d (%s=%q): the outer run owns this assertion", depth, DepthEnv, os.Getenv(DepthEnv))
	}
}
```

### Vacuity guard before any content assertion
**Source:** `makefile_test.go` lines 43-47.
**Apply to:** all three proofs and all three controls — assert the target condition was actually reproduced (non-zero exit, or in the SC-5 controls' case, the intact-side result exists and is non-vacuous per D-16) before asserting anything about message content.

### Differential subprocess comparison
**Source:** `makefile_test.go` lines 40-41 (`makeSide` vs `directSide`), reused structurally (not literally — different sides) by the three SC-5 controls (intact `make gate` run vs defeated-tree `make gate` run).

### Bind to exported constants / test-supplied values only (D-17)
**Source:** `testenv.go` lines 35-41 (`URLEnv`, `RequireEnv`), never the unexported `escalationPreamble()` (line 54).
**Apply to:** every proof and control's content assertions.

### `127.0.0.1`, never `localhost`
**Source:** `makefile_test.go` line 15-16 comment, `closedPortDSN`/`composeDSN` constants.
**Apply to:** any new DSN constant in `gateproof`.

### Zero-value-fallback idiom for optional `RunOptions` fields
**Source:** `harness.go` lines 172-175 (`Timeout`).
**Apply to:** the new `Dir` field in `RunOptions`.

### Test naming
**Source:** `.planning/codebase/CONVENTIONS.md` line 15 (`TestContext_Behavior`), and this phase's own discretion note: include the requirement ID, e.g. `TestPROOF01_GateNamesUnsetURL`.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `internal/platform/gateproof/proof03_test.go`'s `git archive HEAD` Go implementation | test (file-I/O) | file-I/O | No existing Go code performs this — the only precedent is a bash verification snippet in `02-03-PLAN.md` (lines 524-534). The planner must treat that bash shape as the spec to port into `os/exec`+`os.MkdirTemp`+`t.Cleanup`, not as an existing Go analog. |

## Metadata

**Analog search scope:** `internal/platform/gate/`, `internal/platform/testenv/`, `internal/adapters/secondary/store/`, `internal/core/domain/segment/`, `.planning/phases/02-enforcement-and-a-single-gate-definition/`, `.planning/codebase/`
**Files scanned:** `harness.go`, `makefile_test.go`, `testenv.go`, `segmentation_test.go` (fixture call site), `fixture_test.go`, `acceptance_test.go` (GATE-09 control), `02-03-PLAN.md` (bash verification), `CONVENTIONS.md`
**Pattern extraction date:** 2026-09-03
