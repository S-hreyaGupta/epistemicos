# Phase 2: Enforcement and a Single Gate Definition - Pattern Map

**Mapped:** 2026-09-01
**Files analyzed:** 8 (code/config under change) + 1 new (D-07 harness) + 1 standalone target (D-13/D-15)
**Analogs found:** 8 / 9 (one file — the D-07 shell-out harness — has no true in-repo analog; closest partial match reported below)

Research was skipped for this phase (`workflow.research: false`); CONTEXT.md is the sole source
for the file list and the canonical analog relationships, which this document verifies and
extends with concrete excerpts.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `internal/platform/testenv/testenv.go` (`RequireEnv` rename + tripwire, D-08/D-09) | utility (test-support config) | request-response (env read, fail/skip decision) | `internal/platform/config/config.go` lines 76-86 | exact — same "name the rename" shape |
| `internal/platform/testenv/testenv.go` (shared escalation-preamble builder, GATE-06) | utility | request-response | `internal/platform/testenv/testenv.go` `Pool`/`Fixture` themselves (self-referential refactor) | exact — extracting existing inline logic into a shared helper |
| `internal/platform/testenv/testenv_test.go` (D-04 reachability assertion + D-10 tripwire test) | test | CRUD/event-driven (env mutation + assertion) | `internal/platform/testenv/testenv_test.go` `TestRequired` (existing file, same file) | exact — same `t.Setenv`/table-driven idiom already in file |
| `Makefile` (`gate`, `test`, `migrate`, `help` reshape, D-01/02/03/05/06/11) | config (build recipe) | batch | `Makefile` existing `gate`/`test` recipes (same file) | exact — reshape in place |
| `.github/workflows/ci.yml` (`go` job collapse, CI-02) | config (CI pipeline) | batch | `.github/workflows/ci.yml` existing `go` job (same file) | exact — collapse in place |
| `docker-compose.yml` line 9 (SEC-01 loopback bind) | config | — | `docker-compose.yml` (same file, one-line edit) | exact |
| `internal/core/domain/segment/acceptance_test.go:435` (GATE-09 length guard) | test | request-response (fixture-driven assertion) | `internal/core/domain/segment/build_test.go:199-201` and `fixture_test.go:185-187` | exact — two already-correct in-package guards |
| `README.md` §"The gate" (~269) and §Quickstart (~165) (GATE-08 docs) | config (docs) | — | `README.md` same sections (same file) | exact — text correction in place |
| New Go test: shell-out-to-`make` harness (D-07, lives in a new or existing test file, likely under `internal/platform/testenv/` or a new `test/` / `internal/platform/gate/` package — file path is the planner's decision, not fixed here) | test (process-invocation harness) | request-response via subprocess | `internal/core/domain/segment/deps_test.go` (`TestPackageHasNoPortDependencies`) | partial — closest available `exec.Command`-based test in the repo, but invokes `go list`, not `make`, and for an unrelated purpose (architecture guard, not gate behavior) |
| Standalone parity-check target (D-13/D-15: ROADMAP vs REQUIREMENTS.md requirement-set comparison, PROJECT.md ID validity) | utility/script (governance tooling) | batch | none found — no existing standalone comparison script in the repo | no analog — build from scratch per D-13's stated shape (travels across phases, human-runnable) |
| `01-01`'s `<precondition>` block (shape D-13's start check imitates in the phase's first PLAN.md) | n/a — planning artifact, not source code | n/a | `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-PLAN.md` lines 280-319 | exact — this is the literal shape to imitate, not a code analog |

## Pattern Assignments

### `internal/platform/testenv/testenv.go` — GATE-07 rename tripwire (D-08)

**Analog:** `internal/platform/config/config.go` lines 76-86

```go
if c.DBURL == "" {
	// Name the rename rather than the absence. Somebody with a working
	// .env from last week has a set variable and an empty config, and
	// "DB_URL is required" sends them to look at a line that is right
	// there in front of them.
	if os.Getenv(legacyEnvPrefix+"DB_URL") != "" {
		return nil, fmt.Errorf(
			"%sDB_URL is required, but %sDB_URL is set: the prefix was renamed from %s to %s on 24 August 2026. Rename it in your .env",
			EnvPrefix, legacyEnvPrefix, legacyEnvPrefix, EnvPrefix)
	}
	return nil, fmt.Errorf("%sDB_URL is required", EnvPrefix)
}
```

**Shape to mirror in `testenv.go`:** check whether the new name (`EPISTEMIC_OS_TEST_REQUIRE_ENV`)
is unset while the old name (`EPISTEMIC_OS_TEST_REQUIRE_DB`) is set; if so, fail naming the
rename and the date/phase, not just the absence. D-10 additionally requires the failure text to
carry its own reasoning ("this name was renamed in Phase 2; Phase 1's plans still teach it") —
`config.go`'s branch is the structural precedent (branch shape, error-wrapping with `%w`/`Errorf`
style) but its message text is shorter than what D-10 requires; extend the message, don't shorten
D-10's requirement to match.

---

### `internal/platform/testenv/testenv.go` — GATE-06 shared escalation-preamble builder

**Analog:** the three existing escalated `t.Fatalf` call sites in the same file (`testenv.go`),
which is what the new shared builder replaces/backs.

**Site 1 — `Pool`, missing URL** (line 93):
```go
if Required() {
	t.Fatalf("%s is not set, and %s is set: escalation is on, so this test cannot be skipped for a missing database URL", URLEnv, RequireEnv)
}
```

**Site 2 — `Pool`, unreachable database** (lines 125-127):
```go
if Required() {
	t.Fatalf("cannot reach postgres at %s (from %s): %v", host, URLEnv, err)
}
t.Skipf("cannot reach postgres at %s (from %s): %v", host, URLEnv, err)
```

**Site 3 — `Fixture`, unreadable fixture** (lines 151-153):
```go
if Required() {
	t.Fatalf("fixture not readable at %s: %v", path, err)
}
t.Skipf("fixture not readable at %s: %v", path, err)
```

**Pattern to extract:** all three sites currently branch on `Required()` and hand-write their own
`Fatalf`/`Skipf` pair. Per Claude's Discretion (GATE-06 — message contract), the new shared
preamble builder must emit the flag name and its value quoted —
`EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"` — appended/prefixed consistently across all three
escalated messages, and per D-03 the unreachable-database message additionally carries the
remediation (`— run make up`) in the same sentence. The unescalated `t.Skipf` branches (sites 2
and 3's non-required paths) are explicitly left untouched — GATE-06 governs escalation-caused
failures only.

**No-DSN discipline to preserve verbatim** (`hostFromURL`, lines 58-71, and `unparseableURLMsg`,
line 48): the `t.Fatal(unparseableURLMsg)` call at line 110 uses an argument-free constant, never
a format string interpolating the raw DSN or the pgx error. Any new shared builder must not
introduce a new formatting path that could interpolate a raw DSN.

---

### `internal/platform/testenv/testenv_test.go` — D-04 reachability assertion, D-10 tripwire test

**Analog:** `TestRequired` in the same file (lines 103-140), the existing table-driven
`os.Setenv`/`t.Setenv`/`t.Cleanup` idiom for exercising `RequireEnv`-adjacent env state:

```go
func TestRequired(t *testing.T) {
	cases := []struct {
		name  string
		unset bool
		value string
		want  bool
	}{
		{name: "unset", unset: true, want: false},
		{name: "empty string", value: "", want: false},
		{name: "string one", value: "1", want: true},
		{name: "string zero", value: "0", want: true},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if c.unset {
				old, existed := os.LookupEnv(RequireEnv)
				if err := os.Unsetenv(RequireEnv); err != nil {
					t.Fatalf("Unsetenv: %v", err)
				}
				t.Cleanup(func() {
					if existed {
						_ = os.Setenv(RequireEnv, old)
					}
				})
			} else {
				t.Setenv(RequireEnv, c.value)
			}

			if got := Required(); got != c.want {
				t.Fatalf("Required() = %v, want %v", got, c.want)
			}
		})
	}
}
```

D-10's new test (old name set, new name unset → rename error) should use this same
`os.LookupEnv`/`t.Setenv`/`t.Cleanup` pattern to drive both env vars deterministically.

D-04's preflight is a `go test ./internal/platform/testenv/ -count=1` invocation from the
Makefile, not a new test function per se — but the file's doc comment at the top of
`testenv_test.go` (currently absent) should be updated to note the package tests now touch a
database, per D-04's stated cost (a).

The file's negative-control idiom (`TestHostFromURL_Control_NeverReturnsUserinfo`,
`TestUnparseableURLMsg_Control_NoLeak`, lines 57-101) is the established two-step
"prove-the-secret-would-appear, then assert it doesn't" shape already in this file; not directly
needed for D-04/D-10 but worth keeping consistent if any new test touches DSN-adjacent text.

---

### `Makefile` — D-01/02/03/05/06/11 gate reshape

**Analog:** the file's own existing `gate` and `test` recipes (lines 35-45), which this plan
reshapes in place:

```make
test:
	go test ./... -count=1

# The gate CI enforces. Run it before pushing.
gate: vet
	@unformatted=$$(gofmt -l .); \
	if [ -n "$$unformatted" ]; then \
		echo "unformatted files:"; echo "$$unformatted"; exit 1; \
	fi
	go build ./...
	go test ./... -count=1

migrate:
	go run ./cmd/epistemicos-cli migrate up
```

**Target shape per D-02/D-06:** `gate: vet → gofmt → build → $(MAKE) migrate → preflight →
$(MAKE) test` — note `migrate` and `test` are invoked via `$(MAKE)`, not by re-pasting their
bodies (this is the existing `migrate` target already present at lines 47-48, reused not copied).

**D-11's flag setting on the `gate` target** — no existing `export FOO=value` precedent in this
Makefile; the closest structural precedent for a target-scoped env var is `up`'s use of
`docker compose exec` (line 21), which is unrelated in purpose. The `gate` recipe will need a
line such as `EPISTEMIC_OS_TEST_REQUIRE_ENV=make-gate` prefixed to the `test`/preflight
invocations — no in-repo Makefile precedent for this exact idiom; standard Make `VAR=value target`
or `export VAR=value` syntax applies.

**`help` text to correct (GATE-08):**
```make
	@echo "  make test        Go tests"
	@echo "  make gate        Full static gate: vet + gofmt + build + test"
```
Both lines go false under D-01 (gate no longer just "vet + gofmt + build + test" — it now
requires a running database and runs migrate/preflight) and D-05 (test's banner). Update both.

---

### `.github/workflows/ci.yml` — CI-02 collapse to `make gate`

**Analog:** the file's own `go` job (lines 10-71), which collapses onto the Makefile's `gate`
target:

```yaml
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: epistemicos
          POSTGRES_USER: epistemicos
          POSTGRES_PASSWORD: epistemicos
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U epistemicos -d epistemicos"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    env:
      EPISTEMIC_OS_DB_URL: postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.24"
          cache: true
      - name: go vet
        run: go vet ./...
      - name: gofmt
        run: |
          unformatted=$(gofmt -l .)
          if [ -n "$unformatted" ]; then
            echo "unformatted files:"
            echo "$unformatted"
            exit 1
          fi
      - name: go build
        run: go build ./...
      - name: migrate
        run: go run ./cmd/epistemicos-cli migrate up
      - name: go test
        run: go test ./... -count=1
```

**Per canonical_refs:** `services: postgres` and the job-level `EPISTEMIC_OS_DB_URL` stay
(CI-01 preservation); the five `go vet`/`gofmt`/`go build`/`migrate`/`go test` steps collapse into
a single `run: make gate` step. The `docker` smoke job (lines 73-79) is untouched.

---

### `docker-compose.yml` — SEC-01 loopback bind

**Analog:** the file's own line 9, one-line edit:

```yaml
  postgres:
    ...
    ports:
      - "5432:5432"
```
becomes
```yaml
    ports:
      - "127.0.0.1:5432:5432"
```

The `api` service's `"9082:9082"` (line 23) is explicitly not touched — see Deferred Ideas in
CONTEXT.md.

---

### `internal/core/domain/segment/acceptance_test.go:435` — GATE-09 length guard

**Analog 1 — `build_test.go` lines 198-206** (index guard, not touched, but the idiom to match):
```go
	headings := detectHeadings(md)
	if len(headings) == 0 {
		t.Fatal("no headings detected")
	}

	// Every unowned byte must fall before the first heading, or inside a
	// heading line — that is, between a '#' and the newline ending its line.
	preambleEnd := headings[0].ByteStart
```

**Analog 2 — `fixture_test.go` lines 184-195** (the declared-based guard used inside
`preambleInvariant`):
```go
func preambleInvariant(src []byte, headings []Heading, declaredHasPreamble bool) string {
	if len(headings) == 0 {
		return "testdata/demo.md: no headings detected"
	}

	if !declaredHasPreamble {
		return ""
	}

	firstHeading := headings[0].ByteStart
```

**Current unguarded use site — `acceptance_test.go` lines 424-437** (`TestAC14_PreHeadingContentHasNoNode`):
```go
func TestAC14_PreHeadingContentHasNoNode(t *testing.T) {
	md := loadFixture(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	headings := detectHeadings(md)
	firstHeading := headings[0].ByteStart
```

**Pattern to add at line 435:** insert a `len(headings) == 0` guard immediately after the
`detectHeadings(md)` call and before `headings[0].ByteStart` is indexed, matching the two analogs'
`t.Fatal`/`t.Fatalf` idiom — a normal test failure naming the fixture and the condition, not a
skip and not a panic. Per Claude's Discretion: length guard only, no second declaration mechanism
alongside `fixtureHasPreamble`.

---

### `README.md` — GATE-08 documentation

**Analog:** the file's own §"The gate" (lines 269-280) and §Quickstart (lines 166-189):

```markdown
## The gate

​```bash
make gate     # go vet + gofmt + go build + go test
​```

CI runs the same four, and `gofmt` is enforced rather than advisory.
```

```markdown
## Quickstart

​```bash
cp .env.example .env         # fill in MATHPIX_APP_ID and MATHPIX_APP_KEY
make up                      # start postgres
make migrate                 # apply migrations
make build                   # build both binaries
./bin/epistemicos-api        # serves on :9082
​```
```

**Corrections needed per Claude's Discretion (GATE-08):**
1. §"The gate" command summary `go vet + gofmt + go build + go test` → corrected to the D-02
   sequence (vet → gofmt → build → migrate → preflight → test), and the flag's presence-based
   semantics (any non-empty value including `"0"` enables escalation), what escalation changes,
   and D-11's paths-not-precedence limit must be documented here — not in the Configuration table
   (that table describes runtime service config, this is a test-time flag).
2. §Quickstart is where the gate's dependence on a running database should be stated, since that
   is where `make up` is already taught (line 170).

---

## Shared Patterns

### "Name the rename, not the absence" (GATE-07 tripwire)
**Source:** `internal/platform/config/config.go` lines 76-86
**Apply to:** `internal/platform/testenv/testenv.go`'s new tripwire branch (D-08)
Structural precedent only — D-10 requires more in the message text (self-contained reasoning)
than `config.go`'s existing branch carries, so extend rather than copy verbatim.

### Presence-based escalation semantics
**Source:** `internal/platform/testenv/testenv.go` `Required()` (lines 50-56) and
`testenv_test.go` `TestRequired` (lines 103-140)
**Apply to:** every new/modified escalation-adjacent test and the GATE-08 documentation of the
flag's semantics — any non-empty value including `"0"` enables escalation; this rule is
unchanged by the D-08 rename, only the variable name changes.

### No-DSN-in-messages discipline
**Source:** `internal/platform/testenv/testenv.go` `hostFromURL` (lines 58-71) and
`unparseableURLMsg` (line 48, an argument-free constant)
**Apply to:** the new shared escalation-preamble builder (GATE-06) and D-03's preflight step —
neither may introduce a new formatting path that interpolates the raw connection string.

### `$(MAKE) target` reuse over recipe duplication (CI-02's principle one level down)
**Source:** `Makefile`'s existing `migrate` target (lines 47-48), already correct and reused as-is
**Apply to:** D-02 (gate calls `$(MAKE) migrate`) and D-06 (gate calls `$(MAKE) test`) — neither
duplicates the underlying command.

### Executor-honored, non-skippable `<precondition>` block
**Source:** `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-PLAN.md`
lines 280-319 (full block reproduced below)
**Apply to:** this phase's first PLAN.md, for D-13's GOV-01 start check
```xml
  <precondition>
The phase base commit `868d45bf873c9e147f18a099171b99afa348f4a3` is valid as an
audit anchor. Assert all four before writing any code, and halt if any fails:
`git rev-parse --verify 868d45bf873c9e147f18a099171b99afa348f4a3` succeeds;
`git merge-base --is-ancestor 868d45bf873c9e147f18a099171b99afa348f4a3 HEAD` exits 0;
`git log --format=%H 868d45bf873c9e147f18a099171b99afa348f4a3..HEAD -- Makefile .github/workflows/ci.yml`
...
Ancestry alone is not sufficient — the cycle-1 base satisfied ancestry while
failing the last two, which is exactly the failure this precondition exists to
catch, and it must be caught here, before any Phase 1 code makes the tree
indistinguishable from a genuine violation. If any assertion fails, halt and
report. ...
  </precondition>
```
The shape to reuse: numbered assertions run *before any code is written*, explicit halt-and-report
on any failure, and no silent repair path (a mismatch is a `checkpoint:decision`, never an
executor judgement call). D-13's start check (ROADMAP requirement set vs REQUIREMENTS.md
traceability table) should be phrased as an equivalent precondition in this phase's first plan.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| D-07's shell-out-to-`make` test harness (new file, path is the planner's decision) | test | process-invocation / request-response via subprocess | No existing test in the repo shells out to `make` or asserts on a Make target's stdout/stderr/exit code. The closest available analog is `internal/core/domain/segment/deps_test.go`'s `TestPackageHasNoPortDependencies`, which uses `exec.Command("go", "list", "-deps", pkg).Output()` and asserts on the captured output/error — the general Go `os/exec`-invocation idiom (capture `.Output()`, check `err`, assert on stdout content) transfers, but its subject (`go list`, for dependency-graph auditing) and purpose (architecture guard) are unrelated to invoking `make gate`/`make test` and asserting on voicelessness/banner text. No file anywhere in the repo shells out to `make` specifically — confirmed via a repo-wide search for `os/exec`/`exec.Command`, which returned only the five `deps_test.go` files (one per core domain package, all following the same architecture-guard pattern as `segment`'s). |
| D-13/D-15 standalone parity-check target/script (ROADMAP vs REQUIREMENTS.md comparison, PROJECT.md requirement-ID validity) | utility/script (governance tooling) | batch (file-diff/comparison) | No existing standalone comparison script exists anywhere in the repo (`.planning/`, root, or `internal/`). Build from the shape D-13 states directly (travels across phases, human-runnable, reused unchanged by Phase 3) — RESEARCH.md is not available to supply an external pattern either, since research was skipped for this phase. |

## Metadata

**Analog search scope:** `internal/platform/config/`, `internal/platform/testenv/`,
`internal/core/domain/segment/`, `internal/adapters/secondary/store/`, `Makefile`,
`.github/workflows/ci.yml`, `docker-compose.yml`, `README.md`, repo-wide search for
`os/exec`/`exec.Command`, `.planning/phases/01-escalation-mechanism-and-fixture-invariant/`
**Files scanned:** 13 read directly; 5 matched by `os/exec` grep (all `deps_test.go` variants,
one read in full)
**Pattern extraction date:** 2026-09-01
