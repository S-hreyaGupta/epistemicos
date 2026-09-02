# Requirements: EpistemicOS

**Defined:** 2026-08-31
**Core Value:** `make gate` must be able to distinguish "tested and passed" from "tested nothing" — because every downstream verification claim is made through it, and a gate that passes vacuously makes all of them unfalsifiable.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

Derived from PROJECT.md ## Requirements ### Active, with one exception: GATE-05,
whose source is the agreed phase split and is documented under Traceability. The
single PROJECT.md line
"Automated negative tests prove the gate: each of the three environment conditions
is deliberately broken and the gate is asserted to fail *and* to name that cause"
is split into three atomic requirements (PROOF-01..03), one per condition, per the
atomicity rule in the requirements template. No requirement was new scope **as originally
derived on 2026-08-31**. Six have been added since, all at Phase 1 close on 2026-09-01 and
each traceable to a disposition Alex gave there: GATE-06, GATE-07, GATE-08, SEC-01, GOV-01 and GATE-09.
They ARE new scope, deliberately, and are marked as such rather than left under a blanket
claim that stopped being true the moment the first one was added.

### Gate Behavior

- [x] **GATE-01**: `make gate` fails and names the cause when `EPISTEMIC_OS_DB_URL` is unset
- [x] **GATE-02**: `make gate` fails and names the cause when the database is unreachable
- [x] **GATE-03**: `make gate` fails and names the cause when a fixture is unreadable
- [x] **GATE-04**: Content-conditional skips stay green and silent — a fixture that genuinely lacks a preamble is legitimate signal, not a gate failure
- [x] **GATE-08**: The escalation flag is documented where a developer will meet it, not only in the package doc comment: (a) `README.md` states the flag, its presence-based semantics (any non-empty value, including `"0"`, enables escalation) and what it changes; (b) the `Makefile` `help` target describes `make gate` accurately once it is strict — its current text, "Full static gate: vet + gofmt + build + test", becomes FALSE in Phase 2 when the gate requires a live database, so this is a correction, not an addition. Both use the post-GATE-07 name. Deferred from Phase 1 by Alex 2026-09-01 on the grounds that documenting the flag before it does anything would describe behaviour that does not exist; registered here so the obligation travels with Phase 2 if Phase 2 is moved or rescoped, rather than living as a promise in a UAT file. Makefile half complete at 02-01; README half complete at 02-03
- [x] **GATE-07**: The escalation flag is renamed to `EPISTEMIC_OS_TEST_REQUIRE_ENV`, because its scope is wider than `_DB` implies — it also escalates the cross-package fixture prerequisite, a filesystem condition. Decided by Alex 2026-09-01 at Phase 1 UAT: the package doc comment alone is not sufficient. Change is confined to `testenv.RequireEnv`'s value and the package doc comment (2 occurrences in Go); the exported identifier `RequireEnv` does not change, so the API surface accepted in Phase 1 UAT test 1 is unaffected. GATE-05's wording follows the rename when it lands. Phase 1's frozen plans and SUMMARYs keep the old name — they record what was built at the time and are not rewritten
- [x] **GATE-05**: With `EPISTEMIC_OS_TEST_REQUIRE_DB` set, a single shared test helper converts each environment skip — unset URL, unreachable database, unreadable fixture — into a failure naming that cause; with it unset, those skips remain
- [x] **GATE-06**: When escalation causes a failure, the message names the escalation flag (`testenv.RequireEnv`, whatever its value after GATE-07) **and prints the value it is set to**, on all three escalated paths. Presence-based semantics mean the string `0` enables escalation, so a reader who set `0` intending *off* must see `EPISTEMIC_OS_TEST_REQUIRE_DB="0"` in the failure itself. Measured at Phase 1 close: the unset-URL path says only "is set" and never prints the value, and the unreachable-database and unreadable-fixture paths do not name the flag at all — so neither reveals that escalation is why the run failed rather than skipped

- [x] **GATE-09**: A heading-free fixture fails normally rather than panicking. Acceptance text as specified by Alex Zamurko, 2026-09-01, verbatim:

  > A heading-free fixture MUST produce a normal test failure and MUST NOT panic.
  > No test may index `headings[0]` before proving `len(headings) > 0`.

  **Constraints on the fix, as specified:** a **length guard only** — no second declaration mechanism. `fixtureHasPreamble` already exists and must not be joined by another declared-state constant. Where `headings[0]` is used more than once in a function, the guard goes **immediately after parsing**; where it is used once, a use-site guard satisfies it.

  **Measured at Phase 1 close** — three `headings[0]` index sites exist repo-wide and only one is unguarded:

  | Site | State |
  |---|---|
  | `internal/core/domain/segment/acceptance_test.go:435` | **UNGUARDED** — the subject of this requirement; `headings[0]` appears once in the file, so a use-site guard applies |
  | `internal/core/domain/segment/build_test.go:205` | already guarded by `len(headings) == 0` at `:199` |
  | `internal/core/domain/segment/fixture_test.go:193` | already guarded by `len(headings) == 0` at `:185` |

  The requirement is nonetheless stated repo-wide ("no test may index…"), so a fourth site added later inherits it rather than repeating the defect.

  **Governance framing, as Alex specified it:** this is a **newly discovered Phase 2 hardening requirement, NOT a retroactive modification of the frozen Phase 1 acceptance basis.** Phase 1's acceptance stands exactly as verified and signed — its plans, freeze `c96ecb2`/`8edae22`, `VERIFICATION.md` (`passed`, 5/5) and `SECURITY.md` (signed, `threats_open: 0`) are untouched and remain accurate for what Phase 1 undertook. Phase 1 was contractually forbidden from editing `acceptance_test.go` (GATE-04 required it byte-identical to phase base `868d45b`), so this was never a Phase 1 defect and closing it is not a correction of Phase 1. It supersedes the AC-14 backlog item, which is now closed

### Continuous Integration

- [x] **CI-01**: CI provisions PostgreSQL and applies migrations so the database-backed tests actually execute on every push and pull request — **done at `868d45b`**
- [x] **CI-02**: `ci.yml` calls `make gate` rather than re-implementing it, so the gate has exactly one definition

### Security

- [x] **SEC-01**: The compose PostgreSQL binds loopback only — `docker-compose.yml:9` reads `"127.0.0.1:5432:5432"`, not `"5432:5432"`. As written, Docker publishes the service on all interfaces (`0.0.0.0:5432->5432/tcp`, `[::]:5432->5432/tcp`), so an instance with guessable defaults (`epistemicos`/`epistemicos`) is reachable from the local network. Registered by Alex 2026-09-01 at Phase 1 security sign-off, converting accepted risk AR-02 into a scheduled fix on the grounds that a one-character-class change against real exposure should not sit as an indefinite acceptance. Out of Phase 1's scope: the file is byte-unchanged since phase base `868d45b`, and editing it would have failed Phase 1's own "nothing outside `internal/` and `.planning/`" audit — which is why this is Phase 2 work and not a Phase 1 defect. Closes AR-02; T-01-11 stays open until it lands

### Governance

- [x] **GOV-01**: Phase 2 does not close until a **post-checkpoint stale-artifact sweep** has revalidated `ROADMAP.md`, the phase adjudication documents, `*-VERIFICATION.md` and `REQUIREMENTS.md` against the phase's **final** requirement set, evidence set, commit/base anchors, and recorded dispositions — and each is either confirmed current or corrected, with the correction recorded rather than made silently. The finding this closes, in Alex's framing from Phase 1 close: **checkpoint-derived state can invalidate previously accurate governance artifacts without changing their files.** Every instance below was accurate when written; none was edited; each was falsified by a decision taken afterward, and each was found by accident rather than by a step that looks for them:

  | Artifact | Claim that went stale | Falsified by |
  |---|---|---|
  | `ROADMAP.md` | `030521b` called "the verified phase base" | the base decision naming `868d45b` |
  | `01-REVIEW-ADJUDICATION.md` | cited T-01-01/T-01-09, missed T-01-02; credited an already-rejected fix | reading the frozen threat model while building the security register |
  | `01-VERIFICATION.md` | cited the superseded adjudication; "queued for Phase 2" | that adjudication being amended mid-run |
  | `REQUIREMENTS.md` | "No requirement here is new scope" | GATE-06/07/08 and SEC-01 being added at UAT |

  Treated as **one process finding, not four clerical errors** (Alex, 2026-09-01). A phase whose checkpoints change requirements, anchors or dispositions must assume its own governance artifacts have drifted, and check, rather than assume they are current because nobody edited them

  **The four obligations below are part of GOV-01, not of any one phase's plans.**
  Each currently lives only in a phase `CONTEXT.md`, which means it would not
  travel if this phase were moved or rescoped — the same way the requirement set
  itself failed to travel and produced this finding.

  **1. The sweep runs TWICE per phase, not once (D-12).** A **start check** that
  ROADMAP's requirement set for the phase equals REQUIREMENTS.md's traceability
  table for that phase, run *before any planner is spawned*; and the **close
  sweep** over derived artifacts. The first run is non-negotiable, and this
  milestone is why: ROADMAP listed four Phase 2 requirements while this file
  already carried ten. That damage lands at phase START — a planner plans against
  four and silently drops six, GOV-01 itself among them. A closure-only sweep
  catches it only after the plan is written against the wrong set. This phase's
  start check was run manually and its correction committed as `788136f`.

  **2. Every phase's first plan carries the start check as a plan precondition
  (D-13).** The comparison lives in a standalone target — `make planning-parity
  PHASE=<n>`, backed by `scripts/planning-parity.sh` — because a target travels
  across phases and a human can run it at any time. The phase's first plan opens
  with a precondition that invokes it and halts on disagreement, because a target
  nobody is forced to run is an intention, not a check. The residual cost, stated
  plainly because it is the part that will be forgotten: **every** phase's first
  plan must carry it, so Phase 3 repeating it is a template obligation and not
  something it inherits automatically. This belongs in the requirement precisely
  because it would otherwise live in whichever plan happened to be first.

  **3. The close sweep's artifact list is DERIVED, not typed (D-14).** The rule:
  every tracked file under `.planning/` that names this phase number or one of its
  requirement IDs. Three properties make it the right rule — it is **bounded**, it
  is **reproducible** (run it twice and get the same list, which is checkable in a
  way a judgement call is not), and it is **self-extending**, so a new artifact
  type is covered the day it is created rather than the day someone remembers it.
  The derivation is also the evidence table's row list: scope and evidence are the
  same object, so an under-scoped sweep cannot present itself as a thorough one.

  **4. The derivation's coverage bound (D-14, D-15).** Coverage is artifacts that
  explicitly name the phase or a requirement ID. **Anything else is out of scope by
  design, not assumed covered.** The bound has to be written down rather than
  merely observed: tagging `PROJECT.md` closes the instance that was found, but a
  derivation with an unstated limit lets the ninth untagged artifact escape exactly
  as `PROJECT.md` did, and nobody learns the mechanism has an edge until it happens
  again. The measurement that produced this: `PROJECT.md` contained **0** requirement
  IDs and **0** phase-number mentions, so the derivation would not have caught it —
  and it is the first instance in this milestone found by a mechanism rather than by
  accident. Every ID tagged in `PROJECT.md` must exist in the traceability table;
  `scripts/planning-parity.sh` enforces that, so a typo fails the derivation instead
  of producing a phantom row that reads exactly like coverage.

  **The bound, demonstrated live (2026-09-02, Phase 2 UAT test 12).** The first
  instance found OUTSIDE the sweep set, and the reason obligation 4 is written down
  rather than left as an observation. `.github/workflows/ci.yml`'s `go` job was named
  `vet + test + fmt`. That name was accurate until CI-02 collapsed the job onto a
  single `run: make gate` step — it stopped being true when the thing it describes
  changed, and nobody edited it. That is precisely GOV-01's finding, reproduced in a
  file the derivation **does not cover**: `ci.yml` is not under `.planning/`, and it
  names neither the phase number nor a requirement ID, so no sweep pass would ever
  have surfaced it.

  **Fixed at `d256c4c`** (renamed to `make gate`). The defect is not left standing as
  its own exhibit: a wrong name on the CI page misleads everyone who reads it, and the
  evidence survives in git history either way. This entry is the record; the commit is
  the citation.

  This is the accepted bound behaving exactly as declared, not a defect in it. The
  instance was found by a human running an acceptance test, which is the residual
  channel the bound leaves open. It is recorded here so the next reader learns the
  mechanism has an edge from the register rather than from the next escape.

### Gate Proof

- [ ] **PROOF-01**: An automated test proves the gate fails and names `EPISTEMIC_OS_DB_URL` when that variable is unset
- [ ] **PROOF-02**: An automated test proves the gate fails and names the unreachable host when the database cannot be reached
- [ ] **PROOF-03**: An automated test proves the gate fails and names the fixture path when a fixture is unreadable

## v2 Requirements

None. This milestone is deliberately narrow; the next milestones are the specs
already in flight (ingest, section map, citation), which are verified *through*
this gate rather than alongside it.

## Out of Scope

Explicitly excluded. Carried forward from PROJECT.md ## Requirements ### Out of Scope.

| Feature | Reason |
|---------|--------|
| Ingest, section map, and citation specs | In flight, but they become their own milestones once the gate can be trusted to verify them |
| An opt-out target for running the gate without a database | Reintroduces exactly the ambiguity this milestone exists to remove |
| Failing the gate on content-conditional skips | A test declining because the fixture does not exercise a criterion is real signal, not an untested assertion — see GATE-04 |
| A drift check between `ci.yml` and `make gate` | Superseded by CI-02, which collapses the two to a single definition |
| Fixing failing tests | With Postgres up the suite is healthy; this milestone is about what the gate can prove, not about test correctness |

## Traceability

Which phases cover which requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-04 | Phase 1 | Complete |
| GATE-05 | Phase 1 | Complete |
| GATE-01 | Phase 2 | Complete |
| GATE-02 | Phase 2 | Complete |
| GATE-03 | Phase 2 | Complete |
| GATE-06 | Phase 2 | Complete |
| GATE-07 | Phase 2 | Complete |
| GATE-08 | Phase 2 | Complete (Makefile half at 02-01; README half at 02-03) |
| SEC-01 | Phase 2 | Complete |
| GATE-09 | Phase 2 | Complete |
| GOV-01 | Phase 2 (closure gate) | Complete (start check passed at 02-01 precondition; closure sweep 02-GOV-SWEEP.md ran two passes, terminated 2026-09-02 with zero corrections on the second) |
| CI-01 | Delivered at `868d45b` (not planned) | Complete |
| CI-02 | Phase 2 | Complete |
| PROOF-01 | Phase 3 | Pending |
| PROOF-02 | Phase 3 | Pending |
| PROOF-03 | Phase 3 | Pending |

**Coverage:**

- v1 requirements: 10 total
- Already satisfied: 1 (CI-01)
- Mapped to phases: 9
- Unmapped: 0 ✓

**Note on CI-01:** satisfied before the roadmap existed, at commit `868d45b`,
which added a `services: postgres` block, `EPISTEMIC_OS_DB_URL`, and a `migrate`
step to `ci.yml`. Verified at the time: 38 database-backed tests pass, 0 skip,
and the full suite reports 0 skips. No phase plans it. Phase 2 must preserve this
behavior while collapsing the job to `make gate` — the inline `migrate` step
`868d45b` added is CI-only today, and removing that asymmetry is CI-02's job, not
a re-delivery of CI-01.

**Note on GATE-05's provenance.** Every other requirement here traces to a bullet
in PROJECT.md ## Requirements ### Active. GATE-05 does not, and that gap is worth
stating rather than leaving for a reader to notice.

Its source is the agreed non-enforcing/enforcing phase split: Phase 1 builds the
escalation mechanism, Phase 2 turns it on. PROJECT.md's Active bullets are all
written as claims about `make gate` ("`make gate` fails loudly and names the cause
when X"), which are enforcement claims and therefore land in Phase 2. PROJECT.md
was written before that split existed, so it has no bullet for the mechanism the
split puts in Phase 1 — even though GATE-01, GATE-02 and GATE-03 all depend on it.

Without GATE-05, Phase 1's success criteria exceed its requirement mapping: four
of its five criteria describe the helper and the flag, and only one (the fixture
invariant) maps to a requirement. That is a coverage gap in the requirements, not
a mis-titled phase.

This is not new scope — it is the mechanism the phase split already specifies —
but its traceability runs to that split, not to PROJECT.md. PROJECT.md's own
Evolution section is where it belongs: *"New requirements emerged? → Add to
Active"*, applied at the Phase 1 transition. Until then it is grounded here, in
this note, and nowhere else.

---
*Requirements defined: 2026-08-31*
*Last updated: 2026-08-31 after initial definition*
