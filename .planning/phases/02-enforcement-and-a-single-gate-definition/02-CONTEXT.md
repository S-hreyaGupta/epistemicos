# Phase 2: Enforcement and a Single Gate Definition - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

> **`workflow.research` is `false`.** No researcher runs between this document and
> `gsd-planner`. The decisions below are final and are the planner's only briefing.

<domain>
## Phase Boundary

Turn on the escalation mechanism Phase 1 built, inside `make gate`, and collapse the gate to
a single definition that `ci.yml` calls rather than re-implements. Ten requirements: GATE-01,
GATE-02, GATE-03, GATE-06, GATE-07, GATE-08, GATE-09, CI-02, SEC-01, GOV-01. CI-01 is already
satisfied at phase base `868d45b` and must not regress.

This phase does not add pipeline capability, does not fix failing tests, and does not write
the negative proofs — those are PROOF-01/02/03 in Phase 3.

**One deliberate exception, decided in discussion:** Phase 2 builds the shell-out-to-make test
harness that Phase 3 needs, because two of this phase's own constraints (D-03's voiceless
preflight and D-05's `make test` banner) cannot be verified without it. See D-07.

</domain>

<decisions>
## Implementation Decisions

### Gate composition and database lifecycle

- **D-01:** `make gate` **demands** a running PostgreSQL. It never starts one — no dependency
  on `up`, no implicit `docker compose`. A gate that starts its own database can never fail for
  an unreachable one, which would make Success Criterion 2 unobservable locally and hollow out
  the milestone's central claim.
  — **Reversibility:** reversible — a prerequisite could be added later; nothing binds to its absence.

- **D-02:** The gate recipe becomes **vet → gofmt → build → `$(MAKE) migrate` → preflight → `$(MAKE) test`**.
  `migrate` is invoked through the existing target, not by pasting `go run ./cmd/epistemicos-cli migrate up`
  into gate — a copied body is a second definition of `migrate`, the exact defect CI-02 closes one
  level up. The vet/gofmt/build/migrate/test order matches what `ci.yml` runs today, so the
  collapse preserves CI-01's behavior step for step.
  — **Reversibility:** reversible.

- **D-03:** **A voiceless preflight step runs before `migrate`.** Its only job is to reach
  `testenv.Pool`'s escalated path so that `testenv` — not `migrate` — is the first thing to
  speak when the database is unreachable.

  Grounded in measurement, not assumption. With migrate ahead of the tests, migrate is the first
  reporter for two of the three conditions:

  | Condition | Without preflight, who reports | Text |
  |---|---|---|
  | `EPISTEMIC_OS_DB_URL` unset | `config.Load()` via `die()` | `EPISTEMIC_OS_DB_URL is required` — names the variable |
  | Database unreachable | `store.RunMigrations` | `new migrator: %w` — unaudited golang-migrate/pgx text; may not name the host in SC#2's terms, and may echo the DSN |
  | Fixture unreadable | unreachable from migrate | `testenv.Fixture` |

  **"Voiceless" is a testable constraint, not an intention.** On the unreachable-database path
  the preflight step's own stdout and stderr must be **empty**, and `testenv`'s message must be
  the only text a developer sees. Asserted, so that a helpful `@echo` added six months from now
  becomes a second voice that something notices.

  **Recorded side benefit** (not the goal, but claimed): because the preflight is ordered ahead
  of `migrate`, migrate never runs against an unreachable database, so its unaudited
  `new migrator: %w` text — the last plausible DSN-echo path outside `testenv` — becomes
  unreachable in normal operation. That closes the DSN-echo path on migrate as well as in `testenv`.
  — **Reversibility:** costly — removing the preflight silently transfers ownership of GATE-01 and GATE-02's messages to `store.RunMigrations`, whose text satisfies neither requirement and may leak the DSN. Nothing at the removal site would say so.

- **D-04:** The preflight runs the **whole package, unfiltered**: `go test ./internal/platform/testenv/ -count=1`,
  no `-run` filter. `go test -run '^TestX$'` against a name that no longer exists exits 0 and
  reports ok — a preflight wired that way would pass vacuously the moment the test is renamed,
  reintroducing this milestone's defect inside its own fix. With no name in the Makefile there is
  no name to drift from, so the vacuous-pass path does not exist rather than being guarded against.

  A belt-and-braces "assert at least one test ran" was considered and **rejected**: an assertion
  guarding a structurally impossible condition can never come back false, which makes it
  indistinguishable from an assertion that is not wired up.

  **Two costs accepted explicitly, so neither is a surprise later:** (a) `testenv`'s own package
  tests now touch a database — honest, since `testenv` is the database helper; (b) the
  reachability assertion runs twice, once in preflight and once in the full suite.
  — **Reversibility:** reversible.

### Escalation wiring and the GATE-07 rename

- **D-05:** Escalation is **gate-scoped**, not Makefile-wide, and **`make test` prints a banner**
  declaring that it is the lenient run and that `make gate` is the one that proves anything. A
  Makefile-wide `export` was rejected: it removes the convenience without removing the lenient
  run, since a developer without Docker simply falls back to `go test ./...`, which still skips
  silently. Only the name would have been removed.

  **The banner is a testable constraint:** assert that `make test`'s output contains it, so it
  cannot be quietly dropped when someone tidies the Makefile. A banner nobody checks is a claim
  that cannot come back false.
  — **Reversibility:** reversible.

- **D-06:** `gate` calls **`$(MAKE) test`** rather than duplicating the `go test ./... -count=1`
  line. This is CI-02's principle one level down: a duplicated invocation between the `test`
  target and the `gate` target is the same defect the milestone is closing between the `Makefile`
  and `ci.yml`.
  — **Reversibility:** reversible.

- **D-07:** **Phase 2 builds the shell-out-to-make harness, and builds it as *Phase 3's* harness.**
  D-03's voiceless constraint and D-05's banner both require asserting the behavior of Make
  targets from inside the suite Make governs — precisely the tension recorded at `PROJECT.md`
  lines 91-93 that Phase 3 is chartered to solve for PROOF-01/02/03.

  Static Makefile-text assertions were rejected on a non-uniform-weakness argument: a text check
  for "the preflight recipe contains no `echo`" checks the *less likely* half — the voiceless
  constraint is about **output**, and the likely decay is a tool inside that step starting to
  print, which text assertions cannot see. A text assertion would have been adequate for the
  banner alone.

  **Two binding conditions on the front-loading:**
  1. Build it as Phase 3's harness, not as Phase 2's version of one. If Phase 3 rewrites it, the
     front-loading bought nothing and cost scope.
  2. **Record on the roadmap that Phase 2 has taken a slice of PROOF-01/02/03's design question**,
     so Phase 3's plan starts from "apply the existing harness" rather than rediscovering the
     tension at `PROJECT.md` lines 91-93.
  — **Reversibility:** one-way — Phase 3's plan will be written against this harness's existence and shape. Replacing it after Phase 3 binds to it means rewriting Phase 3's proofs, not just the harness.

- **D-08:** GATE-07 is a **hard cut plus a tripwire**. `testenv.RequireEnv`'s value becomes
  `EPISTEMIC_OS_TEST_REQUIRE_ENV`; the old name is not honored. But if
  `EPISTEMIC_OS_TEST_REQUIRE_DB` is set while the new name is unset, the run **fails naming the
  rename** — the same shape `internal/platform/config/config.go:80-86` already uses for the
  `PAPERLY_` → `EPISTEMIC_OS_` rename ("name the rename rather than the absence").

  Without the tripwire, a stale `..._REQUIRE_DB=1` in someone's shell silently downgrades them to
  a lenient run they believe is strict — the vacuous-pass direction this milestone exists to
  remove. The exported identifier `RequireEnv` does not change, so the API surface accepted at
  Phase 1 UAT test 1 is unaffected.
  — **Reversibility:** costly — Phase 3's proofs and the Makefile will both bind to the literal new name.

- **D-09:** **`testenv.go`'s package doc comment is corrected in the same commit as the rename.**
  It currently argues *against* renaming — "queued for review rather than resolved by a rename
  here, because renaming it after Phase 2 and Phase 3 bind to the literal name is no longer local
  to this package" — which goes false the moment the rename lands. This is a stale-artifact
  instance we can see coming rather than find later; a separate cleanup commit is not acceptable.
  — **Reversibility:** reversible.

- **D-10:** **The tripwire is permanent, deliberately, and says why.** Phase 1's frozen plans and
  SUMMARYs keep the old name and are never rewritten (REQUIREMENTS.md, GATE-07), so
  `EPISTEMIC_OS_TEST_REQUIRE_DB` stays permanently discoverable in documents a reader has every
  reason to trust. The hazard is permanent; the guard matches it. Retiring the tripwire at
  milestone close, or when Phase 3's proofs land, would reopen the silent-downgrade path while
  the documents that create the risk are still there.

  Two required properties:
  - **The tripwire has a test.** Assert that setting the old name while the new one is unset
    produces the rename error. A permanent mechanism nobody verifies is the recurring shape:
    someone tidies it away, nothing fails, and the path reopens without a signal.
  - **The reasoning lives in the failure message, not only in a code comment** — e.g. "this name
    was renamed in Phase 2; Phase 1's plans still teach it". Unlike a comment, it cannot be
    dropped without the test noticing.
  — **Reversibility:** reversible.

- **D-11:** `make gate` sets the flag to **`make-gate`**, not `1`. Presence-based semantics make
  any non-empty value equivalent, and GATE-06 already requires the failure to print the value —
  so the value is free, and it is spent identifying the caller. A failure then distinguishes the
  two paths a developer can be on:

  ```
  EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"   the Makefile turned it on
  EPISTEMIC_OS_TEST_REQUIRE_ENV="1"           their own export, go test direct
  ```

  `1` would only say escalation is on, which the failure already implies. The caller's name says
  something the failure does not otherwise carry.

  **Stated limit, to be documented so nobody reads more into it:** a target-scoped export
  overrides the environment, so someone with a stale export running `make gate` still sees
  `make-gate`. It distinguishes **paths, not precedence**.
  — **Reversibility:** reversible.

### GOV-01 — the stale-artifact sweep

- **D-12:** **GOV-01 runs twice, not once.** A closure-only sweep does not catch the class GOV-01
  was created for.

  | Run | What | When |
  |---|---|---|
  | **Phase start** | ROADMAP's requirement set for the phase equals REQUIREMENTS.md's traceability table | before any planner is spawned |
  | **Phase close** | the full derived-artifact sweep (D-14) | after every plan, UAT and security sign-off |

  Grounding: the instance this session found — ROADMAP listing four Phase 2 requirements while
  REQUIREMENTS.md carried ten — would have done its damage at phase **start**, with a planner
  planning against four and silently dropping six, GOV-01 itself among them. A closure sweep
  catches that only after the plan is already written against the wrong set. This phase's start
  check has already been run manually and the correction committed as `788136f`; the decision
  here is that it must have a home other than "someone noticed."
  — **Reversibility:** reversible.

- **D-13:** **Start check: standalone target for the mechanism, plan precondition for the
  enforcement.** The comparison lives in a standalone target/script — it travels across phases,
  is runnable by a human at any time, and Phase 3 reuses it without rewriting it. The phase's
  first plan opens with a `<precondition>` that invokes it and halts on disagreement, the same
  shape `01-01`'s precondition used, which the executor honors and cannot skip. A target nobody
  is forced to run is an intention; a precondition alone does not travel. Together, neither
  problem survives.

  **Rejected:** making parity a Go test so `make gate` enforces it. Its own cost decides it —
  that would make the gate fail on docs-only drift, changing what the gate means, in the one
  milestone whose entire purpose is that the gate means exactly one thing.

  **Residual cost, stated rather than hidden:** every phase's first plan must carry the
  precondition, so Phase 3 repeating it is a template obligation rather than something inherited.
  Acceptable — GOV-01 is phase-scoped — but it is the thing that will be forgotten, so **it
  belongs in GOV-01's requirement text, not in the plan that happens to be first.**
  — **Reversibility:** reversible.

- **D-14:** **The close sweep's artifact list is derived mechanically, not typed:** every tracked
  file under `.planning/` that names this phase number or one of its requirement IDs. Bounded,
  reproducible (run it twice, get the same list — checkable in a way a judgement call is not),
  and self-extending: a new artifact type is covered the day it is created. The derivation is
  also the evidence table's row list.

  **Rejected:** a closed six-artifact list (discovery-by-being-bitten, the mode GOV-01 replaces,
  and it would have covered PROJECT.md only because PROJECT.md was noticed by accident); and a
  class rule with the named four as examples (scope judged at sweep time, so an under-scoped
  sweep looks identical to a thorough one — nothing comes back false).
  — **Reversibility:** reversible.

- **D-15:** **PROJECT.md gets requirement-ID tags, *and* the derivation's coverage bound gets
  written into GOV-01.** These are two different jobs, not two changes for one problem.

  **Measured during discussion:** PROJECT.md contains **0** requirement IDs and **0**
  phase-number mentions. All six `— Pending` rows in its Key Decisions table are pure prose, and
  four of them describe Phase 2 work that goes false when this phase lands. So the derivation in
  D-14 does not catch PROJECT.md — the eighth instance would escape on day one.

  - **Tagging closes the instance we found:** tag the Key Decisions rows and Active bullets with
    the requirement IDs they already correspond to, bringing PROJECT.md inside the derivation
    permanently.
  - **Stating the bound documents what the mechanism cannot see:** GOV-01's text must say that
    coverage is artifacts explicitly naming the phase or a requirement ID, and that anything else
    is **out of scope by design rather than assumed covered**. Tagging alone leaves a derivation
    with a silent limit — the ninth untagged artifact escapes exactly as PROJECT.md did, and
    nobody learns the mechanism has an edge until it happens again.
  - **A wrong ID is a false sweep row, so make that mechanically checkable:** every ID tagged in
    PROJECT.md must exist in REQUIREMENTS.md's traceability table. A typo then fails the
    derivation rather than producing a phantom row that looks like coverage. This folds into the
    same standalone target as D-13's parity comparison.
  — **Reversibility:** reversible.

- **D-16:** **The close sweep lives in its own final plan**, executed after every other plan has
  landed and after UAT and security sign-off — the checkpoints that produced all four instances
  GOV-01 tabulates. It gets its own commit and summary and cannot be skipped by a phase that ran
  out of steam. A VERIFICATION.md section was rejected (VERIFICATION.md is itself on the sweep's
  list, so the check and one of its subjects would share a document, and it runs before UAT,
  where three of the four instances were created); a closing task inside the last code plan was
  rejected (it runs before the events it exists to catch, which is how all four were missed).

  **Cost accepted:** a plan that writes no code, which the executor and verifier machinery is not
  shaped around.
  — **Reversibility:** reversible.

- **D-17:** **Evidence is a per-artifact table**, one row per derived artifact, each with an
  explicit *confirmed current* or *corrected* verdict and the correcting commit. Not a diff. A
  diff shows what changed but cannot distinguish "checked and current" from "not checked" —
  GOV-01's own ambiguity one level up. **The confirmed-current rows are the proof the sweep ran
  at all.**
  — **Reversibility:** reversible.

- **D-18:** **Sweep recursion, with a halt case.** A correction that changes only wording re-runs
  nothing. A correction that changes a requirement set, an anchor, or a disposition **re-arms**
  the sweep. Re-arm until a pass produces zero corrections; this terminates because each pass
  removes a false claim from a finite artifact set.

  **One case breaks that, and it has already occurred:** registering GOV-01 *added* a requirement,
  which made REQUIREMENTS.md stale a fifth time in the same commit. A pass that **adds a
  requirement is not correcting a stale claim, it is changing scope** — the sweep must **HALT**
  there for a human rather than re-arm. Correcting what a document says about the set is a sweep;
  changing the set is a decision.
  — **Reversibility:** reversible.

### Claude's Discretion

Not selected for discussion. Defaults stated so the planner does not re-ask; each is
requirement-faithful and none contradicts a decision above.

- **GATE-06 — message contract.** One shared escalation-preamble builder in `testenv`, used by
  all three escalated paths, emitting the flag name and its value quoted:
  `EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"`. Three hand-written messages would be three things
  to keep in agreement. Per D-03, the unreachable-database message additionally carries the
  remediation in the same sentence — cause and fix in one message that cannot disagree with
  itself. The **unescalated skip** messages are left as they are: GATE-06 governs
  escalation-caused failures by its own text, and this phase should not widen it.

- **GATE-09 — the length guard.** Use-site guard at
  `internal/core/domain/segment/acceptance_test.go:435`; `headings[0]` appears once in that
  function, so a use-site guard satisfies Alex's stated constraint. Zero headings produces
  `t.Fatalf` naming the fixture and the condition — a *normal test failure*, per the verbatim
  acceptance text; not a skip (a skip would read as content-conditional, and a malformed fixture
  is not legitimate signal) and not a panic. **Length guard only**; `fixtureHasPreamble` is not
  joined by a second declaration mechanism. The two already-guarded index sites
  (`build_test.go:205`, `fixture_test.go:193`) are not touched.

- **SEC-01 — loopback bind.** `docker-compose.yml` line 9 becomes `"127.0.0.1:5432:5432"`. The
  `api` service's `"9082:9082"` is **not** changed — SEC-01 names the PostgreSQL binding only.
  See Deferred Ideas.

- **GATE-08 — documentation.** README's **"The gate"** section (~line 269) is where the flag is
  documented, not the Configuration table — it is a test-time flag, not a runtime config
  variable, and the table describes the running service. It must state presence-based semantics
  (any non-empty value, including `"0"`, enables escalation), what escalation changes, and
  D-11's paths-not-precedence limit. The same section's command summary
  (`go vet + gofmt + go build + go test`) is corrected to the D-02 sequence, and the gate's
  dependence on a running database is stated where the quickstart teaches `make up`. The
  `Makefile` `help` text for `gate` — currently `Full static gate: vet + gofmt + build + test`,
  which becomes false under D-01 — is corrected, and `test`'s help line reflects D-05's lenient
  banner.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

ROADMAP.md carries no `Canonical refs:` line for this phase; the list below was accumulated from
REQUIREMENTS.md, PROJECT.md, and the codebase scout.

### Requirements and governance
- `.planning/REQUIREMENTS.md` — the ten requirement texts. GATE-09's acceptance text is verbatim
  from Alex and must not be paraphrased; GATE-07 bounds the rename to `RequireEnv`'s value and the
  package doc comment; GOV-01 carries the four-instance table this phase's sweep is built from
- `.planning/ROADMAP.md` §Phase 2 — the eleven success criteria, the `Requirements note` recording
  the four-vs-ten correction, and the `Preserves: CI-01` line
- `.planning/PROJECT.md` — §Constraints (hard fail, no exception, locally and in CI), §Out of Scope
  (no opt-out target), and **lines 91-93**, the recorded tension D-07 takes a slice of. Also the
  subject of D-15's tagging
- `.planning/STATE.md` — §Accumulated Context, the Phase 1 decision entries that bind this phase,
  and §Blockers/Concerns

### Phase 1 record (what this phase builds on)
- `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-UAT.md` — the dispositions
  that produced GATE-06/07/08 and GATE-09
- `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-SECURITY.md` — the sign-off
  that converted AR-02 into SEC-01; T-01-11 stays open until SEC-01 lands
- `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-VERIFICATION.md` — the
  measured Phase 1 baseline this phase's changes are diffed against
- `.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md` — the measured
  escalation baseline (38 tests, 0 skips escalated; leak-token count 0)

### Code under change
- `internal/platform/testenv/testenv.go` — `RequireEnv` (D-08), the package doc comment (D-09),
  the three escalated paths (GATE-06), and `hostFromURL` / `unparseableURLMsg`, whose no-DSN
  discipline must be preserved
- `internal/platform/testenv/testenv_test.go` — gains the reachability assertion (D-04); today its
  tests are pure and never call `Pool`
- `Makefile` — `gate`, `test`, `migrate`, `help` (D-01, D-02, D-03, D-05, D-06, D-11, GATE-08)
- `.github/workflows/ci.yml` — the `go` job collapses to `make gate`; the `services: postgres`
  block and job-level `EPISTEMIC_OS_DB_URL` stay (CI-01), the inline `migrate` step goes (CI-02)
- `docker-compose.yml` line 9 — SEC-01
- `internal/core/domain/segment/acceptance_test.go` line 435 — GATE-09
- `README.md` §"The gate" (~line 269) and §Quickstart (~line 165) — GATE-08

### Read-only context (measured during discussion; not changed in this phase)
- `internal/platform/config/config.go` lines 76-86 — the `PAPERLY_` rename tripwire D-08 mirrors
- `internal/adapters/secondary/store/migrate.go` lines 24-47 — the `new migrator: %w` path D-03
  routes around

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`internal/platform/config/config.go:80-86`** — a working rename-tripwire precedent with its
  rationale already written ("Name the rename rather than the absence"). D-08 mirrors its shape
  rather than inventing one.
- **`internal/platform/testenv`** — already the single skip-or-fail decision point for all 38
  database-backed call sites, with `Required()`, `hostFromURL`, and the argument-free
  `unparseableURLMsg`. GATE-06's shared preamble and D-04's reachability assertion both belong
  here; nothing new needs to be created to own them.
- **The `migrate` target** — exists and is correct; D-02 reuses it rather than copying it.
- **`01-01`'s `<precondition>` block** — the executor-honored, non-skippable shape D-13's start
  check reuses.

### Established Patterns
- **Presence-based escalation** — any non-empty value including `"0"` enables it; a typo errs
  toward enforcing. D-11's `make-gate` value is chosen inside this rule, not against it.
- **No DSN in any message** — `hostFromURL` returns only `url.URL.Host`, never userinfo;
  `unparseableURLMsg` is a constant, not a format string, so a later edit wanting detail must
  change its type. D-03 extends this discipline by routing around migrate rather than trusting it.
- **Turn intentions into things that fail** — recurring across this discussion (D-03, D-05, D-10,
  D-13, D-17). An assertion that cannot come back false is treated as equivalent to no assertion.
- **Frozen artifacts are not rewritten** — Phase 1's plans and SUMMARYs keep the old flag name;
  D-10's permanence follows from that rather than overriding it.

### Integration Points
- `Makefile` `gate` is where enforcement, the preflight, migrate, and the flag value all meet —
  the single definition CI-02 collapses `ci.yml` onto.
- `ci.yml`'s `go` job after collapse: checkout → setup-go → `make gate`, keeping
  `services: postgres` and the job-level `EPISTEMIC_OS_DB_URL`. Removing the inline `migrate` step
  is CI-02's actual content; the `docker` smoke job is untouched.
- `internal/platform/testenv` is where every named cause is authored, and the only place any of
  them should be.

</code_context>

<specifics>
## Specific Ideas

- **"One message can't disagree with itself."** The unreachable-database failure carries cause and
  remediation in a single `testenv` sentence — `cannot reach postgres at <host> — run make up` —
  rather than a preflight adding its own remediation line. A second description of one condition
  is a maintenance burden with nothing keeping the two honest.
- **The flag's value as a signature.** `EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"` in a failure
  tells the reader *who* turned escalation on, which `"1"` does not.
- **The tripwire's message carries its own reasoning** — "this name was renamed in Phase 2; Phase
  1's plans still teach it" — so a 2028 reader sees a decision rather than a leftover, and the
  reasoning cannot be dropped without a test noticing.
- **The measurement that decided D-15:** 0 requirement IDs and 0 phase mentions in PROJECT.md.
  This is the first instance in this milestone caught by a mechanism rather than by accident.

</specifics>

<deferred>
## Deferred Ideas

- **Bind the compose `api` service to loopback.** `docker-compose.yml` publishes `"9082:9082"` on
  all interfaces, the same shape SEC-01 corrects for PostgreSQL. SEC-01 names the database binding
  only, and the API is a service intended to be reachable, so the two are not the same finding.
  Recorded here rather than silently noticed and dropped — belongs in a security pass, not this
  phase.
- **Apply D-15's requirement-ID tagging convention beyond PROJECT.md.** Any future planning
  document that discusses requirements in prose escapes D-14's derivation the same way. A
  convention, rather than a one-off tagging of PROJECT.md, would close the class — but defining
  and enforcing a documentation convention is not this phase's work.
- **`make test`'s banner as a general pattern.** Other targets that can produce a
  green-but-unproven result would benefit from the same treatment. Out of scope: this phase
  changes only the targets its requirements name.

</deferred>

---

*Phase: 2-Enforcement and a Single Gate Definition*
*Context gathered: 2026-09-01*
