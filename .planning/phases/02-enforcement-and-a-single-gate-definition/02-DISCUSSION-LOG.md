# Phase 2: Enforcement and a Single Gate Definition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 2-Enforcement and a Single Gate Definition
**Areas discussed:** DB lifecycle in `make gate`; Escalation wiring + the rename cut; GOV-01's home and evidence
**Area offered but not selected:** GATE-06 message contract (captured as Claude's discretion)

---

## DB lifecycle in `make gate`

### Q1 — Does `make gate` bring up PostgreSQL itself, or demand one already running?

| Option | Description | Selected |
|--------|-------------|----------|
| Demand a running DB | Gate never starts Postgres; keeps SC#2 observable at all | ✓ |
| Gate depends on `up` | Convenient, but makes GATE-02 unreachable locally | |
| Gate probes, prints `make up`, exits 1 | Same enforcement, friendlier failure, extra message to keep honest | |

**User's choice:** Demand a running DB.
**Notes:** —

### Q2 — Where does the `migrate` step live inside the single gate definition, and in what order?

| Option | Description | Selected |
|--------|-------------|----------|
| `$(MAKE) migrate` between build and test | Mirrors `ci.yml`'s order; reuses the target instead of copying its body | ✓ |
| Inline `go run ... migrate up` in gate | Same order, but a second definition of `migrate` that can drift | |
| Prerequisite: `gate: vet migrate` | Cheapest edit, but reorders the gate relative to CI | |

**User's choice:** `$(MAKE) migrate` between build and test.
**Notes:** —

### Q3 — When the database is unreachable, who owns the message that names the cause?

Presented after measuring the three failure paths: with migrate ahead of the tests, `config.Load()`
reports the unset-URL case (naming the variable) and `store.RunMigrations` reports the unreachable
case via unaudited `new migrator: %w` text that may not name the host and may echo the DSN.

| Option | Description | Selected |
|--------|-------------|----------|
| Preflight keeps it in `testenv` | A check before migrate routes through `testenv.Pool`'s escalated path | ✓ (amended) |
| Harden migrate to own it | Honest, but edits production code and widens the phase | |
| Measure it, then accept if it passes | Cheapest, but pins a success criterion to a third-party error string | |

**User's choice:** Option 1, amended.
**Notes:** Take the remediation line from option 3 of Q1 and put it inside `testenv`'s own failure
message rather than in a preflight step — that message already has to name the host for SC#2, so
"cannot reach postgres at `<host>` — run `make up`" is one message carrying both cause and fix. A
separate preflight authoring its own remediation means two descriptions of one condition, and
keeping them honest with each other is the maintenance burden that option flags. One message can't
disagree with itself.

Claude flagged that the amendment collided with Q2's ordering — if nothing reaches `testenv` before
migrate, `testenv`'s improved message is never printed. User resolved it: **the check stays, as a
voiceless caller of `testenv`.** Two additions:
- Make "voiceless" a **testable constraint** rather than an intention: on the unreachable-database
  path the preflight's own output must be empty and the only text a developer sees is `testenv`'s.
  Otherwise someone adds a helpful echo in six months and it becomes a second voice unnoticed.
- Record the **side benefit**: ordering it this way means migrate only ever runs against a database
  already proven reachable, so its unaudited error text never reaches a developer. That closes the
  DSN-echo path on migrate as well as in `testenv` — not the goal, but worth having on the record.

### Q4 — How does the preflight prove it actually ran, rather than passing vacuously?

Raised because `go test -run '^TestX$'` against a missing name exits 0 and reports ok.

| Option | Description | Selected |
|--------|-------------|----------|
| No `-run` filter — run the whole package | No name to drift from; the vacuous-pass path does not exist | ✓ |
| Keep `-run`, assert the test executed | Keeps testenv's tests pure; adds output parsing and a second name to keep honest | |
| Both — whole package plus a count assertion | Belt and braces | |

**User's choice:** No `-run` filter.
**Notes:** Claude's own stated doubt about option 3 was the deciding argument — an assertion
guarding a structurally impossible condition can't come back false, making it indistinguishable
from an assertion that isn't wired up, which is the shape this milestone exists because of. Both
costs accepted explicitly so neither is a surprise later: `testenv`'s package tests now touch a
database, and the reachability assertion runs twice. Both honest — `testenv` is the database
helper, so its tests touching a database is what it should look like.

---

## Escalation wiring + the rename cut

### Q1 — Which targets does escalation apply to — just `gate`, or the whole Makefile?

Framed against PROJECT.md's out-of-scope line: an opt-out target for running the gate without a
database. `make test` staying lenient makes it a target that prints ok for a suite that tested
nothing.

| Option | Description | Selected |
|--------|-------------|----------|
| Whole Makefile — `export` at the top | No Make target can produce a vacuous green | |
| Gate only — target-scoped export | `make test` keeps today's behavior; the opt-out arrives by omission | |
| Gate only, and `test` says so | Escalation gate-scoped; `make test` prints a banner declaring its limits | ✓ |

**User's choice:** Option 3.
**Notes:** Option 1's cost is worse than stated — a developer without Docker loses `make test` and
falls back to `go test ./...`, which still skips silently. It removes the convenience without
removing the lenient run, just the name on it. Same treatment as the voiceless preflight: make the
banner a **testable constraint**, asserting `make test`'s output contains it, so it can't be
quietly dropped when someone tidies the Makefile. A banner nobody checks is the
claim-that-can't-come-back-false shape again.

### Q2 — How does Phase 2 assert the voiceless preflight and the `make test` banner?

Raised because both mean testing a Make target from inside the suite Make governs — the tension at
PROJECT.md lines 91-93 that Phase 3 is chartered to solve.

| Option | Description | Selected |
|--------|-------------|----------|
| Behavioral harness now, Phase 3 reuses it | Front-loads Phase 3's design question; Phase 2 closes with both constraints enforced | ✓ |
| Static assertions on the Makefile now | Cheap, no recursion; proves the recipe says the right thing, not that running it does | |
| Minimal behavioral check, expect Phase 3 to replace it | Honest about sequencing; risks two coexisting harnesses | |

**User's choice:** Option 1.
**Notes:** Option 2's weakness isn't uniform. "Preflight recipe contains no echo" doesn't prove the
step is silent — the voiceless constraint is about output, and the likely decay is a tool inside
that step starting to print, which text assertions can't see. It checks the less likely half. For
the banner it would be fine. Two conditions on front-loading: (1) build it as Phase 3's harness,
not Phase 2's version of one — if Phase 3 rewrites it, the front-loading bought nothing and cost
scope; (2) record explicitly that Phase 2 has taken a slice of PROOF-01/02/03's design question, so
Phase 3's plan starts from "apply the existing harness" rather than rediscovering the tension.

### Q3 — Is GATE-07 a hard cut, or does `EPISTEMIC_OS_TEST_REQUIRE_DB` keep working?

Grounded in `config.Load()`'s existing `PAPERLY_` → `EPISTEMIC_OS_` precedent, and in `testenv.go`'s
doc comment, which currently argues against renaming.

| Option | Description | Selected |
|--------|-------------|----------|
| Hard cut + tripwire on the old name | One name; a stale old-name export fails naming the rename instead of silently downgrading | ✓ |
| Hard cut, nothing else | Smallest change; a stale export fails toward silence | |
| Honor both, warn on the old one | Nobody broken; two names for one condition, with no removal date | |

**User's choice:** Option 1.
**Notes:** Two things to settle with it. The tripwire needs a **stated lifetime** — it's a second
reference to a name nobody should be using, and if nothing says when it goes, it's permanent by
default. And `testenv.go`'s doc comment argues AGAINST renaming, which goes false the moment the
rename lands: same commit, or it's the eighth stale-artifact instance this week and one we could
see coming.

### Q4 — What is the tripwire's stated lifetime?

Grounded in REQUIREMENTS.md: Phase 1's frozen plans and SUMMARYs keep the old name and are never
rewritten.

| Option | Description | Selected |
|--------|-------------|----------|
| Permanent, deliberately — and say why | The guard matches a permanent hazard | ✓ |
| Remove at milestone close, with a gate | Transitional, registered as a gated backlog item | |
| Remove when Phase 3's proofs land | Proofs assert the gate's behavior, not a developer's shell | |

**User's choice:** Option 1.
**Notes:** Options 2 and 3 both retire the tripwire while the documents that create the risk are
still there. Two additions: the tripwire needs a **test** (assert that setting the old name while
the new one is unset produces the rename error) because a permanent mechanism nobody verifies is
the recurring shape; and the reasoning goes **in the failure message**, not only in a code comment
— "this name was renamed in Phase 2; Phase 1's plans still teach it" tells the 2028 reader why
they're seeing it, and unlike a comment it can't be dropped without the test noticing.

### Q5 — (raised at the area check) `$(MAKE) test` vs. a duplicated `go test` line, and the flag's value

**User's choice:** Both, briefly. `gate` calls `$(MAKE) test`; the flag's value is **not** `1`.
**Notes:** Duplicating the `go test` line is the same defect the milestone is closing between the
Makefile and `ci.yml` — CI-02's principle one level down. On the value: presence-based semantics
mean any non-empty value works, so the value is free, and GATE-06 already requires the failure to
print it. Spend it on something that identifies the caller — `make-gate`. A failure then
distinguishes `EPISTEMIC_OS_TEST_REQUIRE_ENV="make-gate"` (the Makefile turned it on) from `"1"`
(their own export, `go test` direct). `"1"` only says escalation is on, which the failure already
implies. One honest limit: a target-scoped export overrides the environment, so someone with a
stale export running `make gate` still sees `make-gate` — it distinguishes paths, not precedence,
and that should be stated so nobody reads more into it.

---

## GOV-01's home and evidence

### Q1 — Where does the stale-artifact sweep live?

| Option | Description | Selected |
|--------|-------------|----------|
| Its own final plan in the phase | Runs after every plan, UAT and security sign-off; cannot be skipped | ✓ (extended) |
| A section of VERIFICATION.md | No extra plan; but the check shares a document with one of its subjects | |
| A final task inside the last code plan | No new structure; runs before the events it exists to catch | |

**User's choice:** Option 1, **extended to two runs**.
**Notes:** 2 and 3 both run before the events that create staleness, and 3 admits it — that's how
all four recorded instances were missed. 2 also puts the check inside one of its own subjects. But
all three options are closure-scoped, and that isn't sufficient: the instance this session found —
ROADMAP listing four Phase 2 requirements while REQUIREMENTS had ten — would have done its damage
at phase **start**, with a planner planning against four and silently dropping six, including
GOV-01 itself. So GOV-01 needs two runs: a narrow, cheap **start** check (ROADMAP's requirement set
== REQUIREMENTS', before any planner is spawned) and the full four-artifact **close** sweep as
option 1's plan. Without the first, GOV-01 doesn't catch the class it was created for, which is now
seven instances and counting.

### Q2 — Where does the phase-start requirement-set parity check live?

| Option | Description | Selected |
|--------|-------------|----------|
| A precondition in the phase's first plan | Executor-honored, unskippable; but doesn't travel to later phases | ✓ (for enforcement) |
| A `make` target outside the gate | Travels and is human-runnable; but nothing forces it to run | ✓ (for mechanism) |
| A test in the Go suite, so the gate enforces it | Structural and free everywhere; but makes the gate fail on docs-only drift | |

**User's choice:** Option 1 for the enforcement, option 2 for the mechanism — their costs cancel.
**Notes:** The check lives in a standalone target (travels across phases, runnable any time,
reusable by Phase 3 without rewriting); the phase's first plan opens with a precondition that
invokes it and halts on disagreement, the shape `01-01` already used. Option 2 alone is an
intention; option 1 alone doesn't travel; together neither problem survives. Option 3 is rejected on
its own stated cost — making `make gate` fail on docs-only drift changes what the gate means, in
the milestone whose entire purpose is that the gate means exactly one thing. Residual cost, stated
rather than hidden: every phase's first plan has to carry the precondition, so Phase 3 repeating it
is a template obligation rather than something inherited. Acceptable — GOV-01 is phase-scoped — but
it's the thing that will be forgotten, so it belongs in the requirement text rather than in the plan
that happens to be first.

### Q3 — Is the sweep's artifact list closed at the four GOV-01 names, or something wider?

Framed with a concrete uncovered case: PROJECT.md's Key Decisions table carries six `— Pending` rows
that go false when Phase 2 lands.

| Option | Description | Selected |
|--------|-------------|----------|
| Derive the list mechanically | Bounded, reproducible, self-extending; produces the evidence table for free | ✓ |
| Closed list, extended to six | Auditable; the seventh artifact type is uncovered until someone is bitten | |
| A class rule with the four as examples | Widest in principle; scope judged at sweep time | |

**User's choice:** Option 1, with a test demanded before accepting it.
**Notes:** 3 fails the test applied all week — scope judged at sweep time means an under-scoped
sweep looks identical to a thorough one, so it can't come back false. 2 is
discovery-by-being-bitten, the mode GOV-01 exists to replace, and it only covers PROJECT.md because
Claude happened to notice it a minute earlier. The derivation being reproducible handles the first
half of its own cost — run it twice, get the same list, checkable in a way a judgement call isn't.
The second half was demanded as a live test rather than trusted: **does the derivation actually
catch PROJECT.md?** With the stated fork — if its rows name IDs, the mechanism is demonstrated on a
live case; if not, the requirement must say so, because bounded coverage honestly bounded beats wide
coverage nobody can verify.

**Measurement performed:** PROJECT.md contains **0** requirement IDs and **0** phase-number
mentions. All six `— Pending` rows are prose. The derivation does not catch it.

### Q4 — PROJECT.md escapes the derivation. Accept the bound, or close it at the subject?

| Option | Description | Selected |
|--------|-------------|----------|
| Make PROJECT.md self-catching | Tag its rows with requirement IDs so it falls inside the derivation | |
| Accept the bound, state it in the requirement | Known declared hole rather than a silent one | |
| Both — tag it, and still state the bound | Closes today's gap and documents the mechanism's edge | ✓ |

**User's choice:** Option 3.
**Notes:** They're not two changes for one problem, they're two different jobs — tagging closes the
instance found, stating the bound documents what the mechanism cannot see. Option 1 alone leaves a
derivation with a silent limit: the ninth untagged artifact escapes exactly as PROJECT.md did, and
nobody learns the mechanism has an edge until it happens again. One addition on the tagging cost
Claude named ("a wrong ID is a false sweep row"): make it mechanically checkable — every ID tagged
in PROJECT.md must exist in REQUIREMENTS.md's traceability table, so a typo fails the derivation
rather than producing a phantom row that looks like coverage. User also noted the measurement result
was cleaner than either party expected, and that the eighth instance is now caught by the mechanism
rather than found by accident — the first time in this milestone that has been true.

### Q5 — (raised at the area check) Evidence form, and sweep recursion

**User's choice:** Both proposed defaults accepted, with one addition each.
**Notes:**
- **Evidence:** per-artifact table, and record *why* the form matters — a diff shows what changed
  but cannot distinguish "checked and current" from "not checked", the ambiguity GOV-01 exists to
  remove, one level up. The confirmed-current rows are the proof the sweep ran at all.
- **Recursion:** the wording / requirement-set-anchor-disposition partition is right, with two
  things pinned. **Termination:** re-arm until a pass produces zero corrections — this terminates
  because each pass removes a false claim from a finite artifact set. **Halt case:** registering
  GOV-01 *added* a requirement, which made REQUIREMENTS stale a fifth time in the same commit. A
  pass that adds a requirement isn't correcting a stale claim, it's changing scope — the sweep
  should HALT there rather than re-arm. Correcting what a document says about the set is a sweep;
  changing the set is a decision, and it needs a human.

---

## Claude's Discretion

Offered as a fourth gray area and not selected, or not raised as a decision point; defaults stated
in CONTEXT.md so the planner does not re-ask.

- **GATE-06 — message contract.** One shared escalation-preamble builder in `testenv` used by all
  three escalated paths, printing the flag name and its quoted value; the unreachable-database
  message additionally carries the remediation per the Q3 amendment above; unescalated skip messages
  left unchanged, since GATE-06 governs escalation-caused failures by its own text.
- **GATE-09 — the length guard.** Use-site guard at `acceptance_test.go:435`, `t.Fatalf` on zero
  headings (a normal test failure, not a skip and not a panic), length guard only, the two
  already-guarded sites untouched.
- **SEC-01 — loopback bind.** `docker-compose.yml` line 9 only; the `api` service's port is not
  changed.
- **GATE-08 — documentation.** The flag is documented in README's "The gate" section rather than
  the Configuration table (test-time flag, not runtime config); the section's command summary and
  the `Makefile` `help` text for `gate` and `test` are corrected.

## Deferred Ideas

- Binding the compose `api` service (`"9082:9082"`) to loopback — same shape as SEC-01, but SEC-01
  names the database binding only and the API is meant to be reachable. Belongs in a security pass.
- Applying the requirement-ID tagging convention beyond PROJECT.md, so future prose-only planning
  documents don't escape the derivation the same way. Defining a documentation convention is not
  this phase's work.
- `make test`'s banner as a general pattern for other targets that can produce a green-but-unproven
  result. This phase changes only the targets its requirements name.
