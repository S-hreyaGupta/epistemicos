# Phase 3: Automated Proof - Context

**Gathered:** 2026-09-02 – 2026-09-03
**Status:** Ready for planning

> **`workflow.research` is `false`.** No researcher runs between this document and
> `gsd-planner`. The decisions below are final and are the planner's only briefing.

> **Every number in this document was measured during the discussion**, on this host,
> against the live compose PostgreSQL (loopback-bound, healthy). Nothing here is an
> estimate. Two decisions reversed a position that reasoning alone had produced — see
> **D-05** and **D-14** — which is why the measurements sit inline rather than summarised.

<domain>
## Phase Boundary

Automated negative tests deliberately break each of the three environment conditions and
assert that `make gate` fails **and names that cause**, so the gate's own behavior is
covered by the suite rather than by a manual checklist. Requirements: PROOF-01, PROOF-02,
PROOF-03 — plus **GATE-10**, declared new in this phase (D-19).

This phase adds no gate behavior. It proves the behavior Phase 2 built. It does not fix
failing tests, does not add pipeline capability, and does not re-litigate the escalation
mechanism.

**Two governance acts are in scope, both declared rather than absorbed:** the SC-5
criterion correction (D-12) and the GATE-10 amendment (D-19). Two further governance
changes were deliberately **refused** and registered instead — see Deferred Ideas 2 and 3.

</domain>

<decisions>
## Implementation Decisions

### Carried forward — locked before this discussion, not re-opened

These bind the planner and were not re-asked. Sources in `<canonical_refs>`.

- **Phase 2 D-07 / ROADMAP §Phase 3 Note on the harness** — `internal/platform/gate`
  exists and was built *as* Phase 3's harness. The plan starts from applying `gate.Make` /
  `gate.RunOptions`, not from rediscovering the tension at `PROJECT.md` lines 91-93.
- **Harness contract** — every proof calls `gate.SkipIfNested(t)` as its **first**
  statement. `EPISTEMIC_OS_TEST_MAKE_DEPTH` bounds recursion at depth 1.
- **Phase 2 D-11** — `gate:` carries a **target-scoped** `export
  EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate`, which overrides a caller's value. A proof
  cannot turn escalation off from outside; defeating it requires editing the Makefile.
- **Phase 2 D-01 / D-03** — the gate demands a live PostgreSQL and never starts one;
  `env-preflight` runs before `migrate` so `testenv` is the first voice.
- **Phase 1/2 house rule** — "turn intentions into things that fail." An assertion that
  cannot come back false is treated as equivalent to no assertion. This rule decided D-02,
  D-05, D-14, D-16 and D-18 below.
- **Phase 2 (02-03)** — negative controls run in a throwaway `git archive HEAD` copy, not
  by mutating the working tree.
- **GOV-01 obligation 2 (D-13)** — Phase 3's **first plan must open with the
  `make planning-parity PHASE=3` precondition**. GOV-01's text states explicitly that this
  is a **template obligation, not something Phase 3 inherits automatically**.
- **GOV-01 obligations 1, 3, 4** — start check before any planner is spawned; derived
  close sweep after UAT and security sign-off; the derivation's coverage bound stands as
  written.

**Start-check status at discussion time.** ROADMAP §Phase 3 `**Requirements**:` reads
`PROOF-01, PROOF-02, PROOF-03`; REQUIREMENTS.md's traceability table maps exactly those
three to Phase 3. They agreed **before** D-19 added GATE-10. **They no longer agree** —
which is exactly the change the start check exists to catch. The planner must land the
ROADMAP and REQUIREMENTS edits and re-run `make planning-parity PHASE=3` to green before
proceeding.

### Gate depth, placement, and cost

- **D-01: All three proofs shell out to `make gate`.** Not to `env-preflight`, not to any
  narrower target. SC-1/2/3 are worded "the gate fails", and every proof then exercises the
  real ordering (vet → gofmt → build → env-preflight → migrate → test), so a future reorder
  is caught by all three rather than by none.

  **Measured, and the measurement removed the cheap option:**

  | Nested child (warm cache, live Postgres) | Exit | Elapsed |
  |---|---|---|
  | PROOF-01 shape: `make gate`, `EPISTEMIC_OS_DB_URL` unset | 2 | 7.7s |
  | PROOF-02 shape: `make gate`, closed-port DSN | 2 | 6.4s |
  | PROOF-03 shape: full green `make gate` | 0 | 18.2s |
  | `make env-preflight`, closed-port DSN | **0** | 5.6s |

  "Shortest target per condition" saved **under one second** — and row 4 exited **0**,
  because the escalation flag is target-scoped to `gate` (D-11), so `env-preflight` alone is
  lenient. A proof calling it would have had to set the flag itself, and would then no longer
  prove that **the gate turns escalation on**. It was not a cheaper proof of the same claim;
  it was a proof of a weaker one.
  — **Reversibility:** reversible.

- **D-02: The D-03 ordering claim gets its own two cheap checks, separate from the proofs.**
  (a) `make -n gate` dry-run expansion asserts `env-preflight` precedes `migrate` — a
  structural claim checked structurally; D-07's non-uniform-weakness objection was about
  *output*, so it does not transfer to ordering. (b) PROOF-02's already-running nested gate
  additionally asserts `testenv`'s preamble is present — the effect, not just the order, at
  zero extra cost.

  **Two reasons, both given by the operator.** Each check gets a **single reason to fail** —
  the generalised form of Phase 2's carried warning #2, which is why a claim resting on two
  independent checks survives a reword. And it **degrades gracefully**: three nested gates
  will create pressure to trim, and if the ordering claim were only a side effect of the
  expensive proofs it would disappear with them silently. Here the cheap assertion survives
  the trim and the loss is visible. *This reasoning was stated as holding independent of what
  the measurement returned.*
  — **Reversibility:** reversible.

- **D-03: The proofs live in a separate package** (e.g. `internal/platform/gateproof`),
  importing `internal/platform/gate` and reaching **only its exported surface** —
  `SkipIfNested`, `Run`, `Make`, `RunOptions`, `RunResult`, `RepoRoot`, `DepthEnv`,
  `DefaultTimeout`.

  **The deciding property:** it makes Phase 2 D-07's binding condition 1 — "built as Phase
  3's harness, not Phase 2's version of one" — **compiler-enforced rather than asserted**. A
  proof needing `extraLines`, `normalizeElapsed` or `nestingDepth` fails to build, and the
  API was wrong. In the same package that condition survives as a claim nobody can falsify,
  which is the exact defect class this milestone removes — sitting inside the phase that
  proves the milestone.

  **Explicitly rejected:** relocating `makefile_test.go` for a cleaner boundary. It is a
  refactor available at any time, and doing it here edits frozen Phase 2 deliverables named
  by file in `02-02-SUMMARY.md` — **manufacturing a GOV-01 instance rather than finding one**.
  — **Reversibility:** costly — the package boundary *is* the enforcement of D-07 condition 1; collapsing it later removes the enforcement with nothing failing.

- **D-04: The three proofs are explicitly non-parallel.** Pinned, not left to Go's
  within-package default. Three proofs each shelling out to a full `make gate` against one
  shared compose database, made safe by a default nobody stated, is Phase 2's warning #3 with
  more at stake — and a later `t.Parallel()` is a one-line change with no visible consequence
  until CI goes flaky.
  — **Reversibility:** reversible.

### Cost, measured cold as well as warm

- **D-05: `DefaultTimeout` stays 240s, and its rationale comment is corrected and tagged PROOF-03.** The value was never wrong. The **rationale** was.

  `harness.go` documents 240s as "roughly six times the slowest plausible child measured on
  this host: a full `go test ./... -count=1` is ~13 seconds ... `make vet` alone is ~35
  seconds." Those are **warm** figures.

  | Run (fresh `GOCACHE`) | Exit | Elapsed |
  |---|---|---|
  | Cold parent, full green `make gate` | 0 | **141s** |
  | Child after cold parent, PROOF-01 shape | 2 | 11s |
  | Child after cold parent, PROOF-02 shape | 2 | 9s |
  | Child after cold parent, PROOF-03 shape | 0 | 21s |
  | **Cold child, no warm parent**, PROOF-01 shape | 2 | **85s** |

  **CI is fine, for a reason worth writing down:** on a cold runner the parent pays 141s
  doing vet and build, and the children inherit that cache — 11/9/21s, barely worse than
  warm. Phase 3 costs **~41s on top of a 141s cold CI gate**, and **~32s on top of an 18s
  warm local gate**. Not three cold builds.

  **But the true cold worst case is 85s, so the margin is 2.8×, not 6×.** The comment is
  corrected to cite the cold figure and name which case it is calibrated against, so the next
  reader is not calibrating on warm numbers again.

  **`harness.go` is tagged `PROOF-03` as part of the correction** — a code comment carrying a
  measured claim buying its way into the close sweep's coverage with one identifier. The
  tag's value is **not** getting `harness.go` into the set: measured, it is already in today,
  unprompted, via its "Phase 3" prose. Its value is **keeping it in when someone rewords that
  prose**. A durability property, not a coverage one. See Deferred Idea 2 for the derivation
  amendment this anticipates and why it is *not* taken here.
  — **Reversibility:** reversible.

- **D-06: The shared-database coupling is declared, and isolation is registered as a deferred item carrying the measurement.** Not described — **sized**.

  Measured via per-package intervals from `go test ./... -json`:

  | Package | start | end |
  |---|---|---|
  | `internal/adapters/secondary/store` | 2.42s | 6.57s |
  | `internal/adapters/secondary/approved` | 2.32s | 5.26s |
  | `internal/platform/gate` | 4.46s | 25.70s |

  **`gate` × `store`: +2.11s concurrent. `gate` × `approved`: +0.80s concurrent.** The path
  is real *today*, before Phase 3: Phase 2's nested `make test` runs the whole suite —
  including `store` — while the outer `store` package is running against the same database.
  Phase 3 adds `migrate` to what runs concurrently, via PROOF-03's full nested gate.

  Declared rather than fixed, because isolation is arguably its own requirement. Registered
  rather than merely declared, because **a declaration inside a plan closes with the phase; a
  named deferred item does not.**
  — **Reversibility:** reversible.

### Breaking the fixture (PROOF-03)

- **D-07: PROOF-03 runs `make gate` inside a throwaway `git archive HEAD` copy**, reusing
  02-03's established negative-control pattern. The working tree is never touched.

  **"Mutate and restore" was killed by measurement, not preference:** `segment` ran
  3.34s→5.28s while `gate` ran 4.46s→25.70s — **they overlap**, so mutating `demo.md` in the
  real tree corrupts a file another package is concurrently reading, and the failure lands
  somewhere unrelated to PROOF-03. A `defer` also does not survive a timeout kill, and
  `DefaultTimeout` exists because these children can hang.

  **"Fixture-root indirection in `testenv`" was refused on principle:** a bypass built for a
  proof is still a bypass, and an env-overridable fixture root is a seam through the exact
  mechanism this milestone exists to make trustworthy.
  — **Reversibility:** reversible.

  **CORRECTION, 2026-09-03 (pattern-mapper finding, verified by the orchestrator before
  planning).** This decision and D-11 both say the copy "reuses 02-03's **established**
  negative-control pattern." That overstates what exists. Measured: `git archive` appears in
  **zero** Go files; `TestGATE09_HeadingGuard_Control`
  (`internal/core/domain/segment/acceptance_test.go:448`) is explicitly *"permanent,
  **mutation-free**"* and drives the function with synthetic inputs, never materialising a tree.
  The throwaway copy lives in **`02-03-PLAN.md`'s bash verify script** (`mktemp -d` →
  `git archive HEAD | tar -x -C` → `perl -0pi` defeat edit → nested `go test`), executed once at
  plan-verification time.

  **The decision stands — the shape is proven in this repo and is still the right one.** What
  changes is the work: Phase 3 writes the **first Go implementation** of tree materialisation,
  shared by PROOF-03 and all three SC-5 controls, and unlike the bash original it runs on **every
  gate, in CI, on Windows and Linux**. That promotes one detail from incidental to a decision the
  planner must make rather than inherit: the bash form shells out to `tar`, which is a build-host
  dependency the Go form need not take on — `git archive --format=tar` into Go's `archive/tar`,
  or `git worktree add`, are both git-native alternatives. **Planner: choose deliberately and
  record the choice; do not port the pipe verbatim on the assumption it was already vetted for
  this use.** It was vetted as a one-shot verification step, not as per-test infrastructure.

- **D-08: `RunOptions` gains a `Dir` field.** Measured: `gate.Run` hard-sets
  `cmd.Dir = RepoRoot(t)` and `RunOptions` has no `Dir`. The throwaway copy requires one.

  This is an **addition to the exported surface, not a rewrite**, so D-07 condition 1
  survives it: a proof needing an *unexported* helper still fails to build. D-03's separate
  package is what makes that check real, and this is the first thing to test it.

  **`DepthEnv` handling must not change.** `buildChildEnv` sets it **last**, after `Unset`
  and `Env`, and skips any base/overlay entry naming it — deliberately, so a caller cannot
  defeat the recursion guard. `Dir` is orthogonal and must leave that exactly as is.
  — **Reversibility:** costly — the exported surface is Phase 3's contract with the harness; removing `Dir` later breaks PROOF-03 and all three controls.

- **D-09: Inside the copy, `demo.md` is replaced by a directory** — not deleted.
  `os.ReadFile` on a directory fails on both Windows and Linux: a genuine **read failure**,
  which is what GATE-03 and PROOF-03 actually say. Deleting proves the **absent** case, and
  absence is not unreadability — letting an adjacent proof stand in for the stated one is the
  habit this milestone keeps breaking.

  "Both, as two subtests" was rejected as buying something the requirement does not ask for,
  at ~18-21s per extra nested gate. If the absence case is ever wanted it is a cheap addition
  later.

  **Known consequence, measured:** replacing `demo.md` breaks more than the one
  `testenv.Fixture` call site — `segment`'s own direct reads (`fixture_test.go`'s hash pin)
  fail hard regardless of escalation. This is why PROOF-03 must assert on the escalation
  preamble rather than on the gate merely failing. See D-14.
  — **Reversibility:** reversible.

### Proving the proofs (SC-5)

- **D-10: SC-5's literal wording is unreachable through the harness, and is registered as a finding rather than absorbed.** `buildChildEnv` sets `DepthEnv` last and skips any entry naming
  it, so a control that spawns the proof package hands it depth 1 and **every proof
  `SkipIfNested`-skips**. The control would see three skips and a green run — a vacuous pass,
  inside the mechanism built to remove vacuous passes.
  — **Reversibility:** reversible (a record, not a mechanism).

- **D-11: SC-5 is proven by a differential** — the same `make gate` invocation against two
  trees: the real one, and a `git archive HEAD` copy with
  `gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate` stripped from the Makefile.

  **The entailment must be stated in the assertion's own comment**, not left for a reader to
  reconstruct: the proofs assert the gate fails; if the defeated tree lacks the escalation
  preamble, the proofs would fail. Proving the premise proves the consequent — say what the
  assertion is standing in for.
  — **Reversibility:** reversible.

- **D-12: ROADMAP §Phase 3 SC-5 is corrected, sequenced through the GOV-01 start check.**
  Reworded to what is provable; `make planning-parity PHASE=3` runs **first**, because D-13
  requires that check anyway — so the sequencing is free, and the edit lands in a run that
  also confirms ROADMAP's requirement set matches the traceability table. An isolated ROADMAP
  edit is exactly the kind that can quietly disagree with REQUIREMENTS.

  **Two things the correction must carry:**
  1. **Name `buildChildEnv`'s deliberate ordering as what falsified the wording** — not
     merely that it is false. The wording was accurate until 02-02 built a guard that made it
     unreachable. **A criterion falsified by a later deliberate decision reads differently
     from one that was always wrong, and the next reader needs to know which.** Same shape as
     `harness.go`'s timeout rationale and `ci.yml`'s job name.
  2. **Record it explicitly as GOV-01's *sweep* half.** The requirement set is untouched;
     this corrects what a document *says* about it. That is the distinction 02-04 wrote into
     GOV-01's own text, and **this is its first use on a criterion rather than a status
     field**.
  — **Reversibility:** reversible.

- **D-13: Three controls, one per condition — not one.** The three conditions were **measured
  to fail differently** in the defeated tree (`config` / `migrate` / `segment`'s hash pin).
  One control would have to paper over that, and **papering over is exactly how the exit-code
  version looked sound.**
  — **Reversibility:** reversible.

- **D-14: The differential binds to the escalation preamble, NOT to the exit code.**

  **This reversed a design that reasoning had produced and measurement falsified.** The
  differential was first specified as "the real tree fails while the defeated copy exits 0."
  Measured:

  | Condition | DEFEATED (export stripped) | INTACT |
  |---|---|---|
  | PROOF-01 URL unset | exit=**2**, preamble ABSENT, `config die: required` | exit=**2**, preamble PRESENT |
  | PROOF-02 closed port | exit=**2**, preamble ABSENT, `migrate: new migrator` | exit=**2**, preamble PRESENT, `testenv: unreachable` |
  | PROOF-03 fixture=dir | exit=**2**, preamble ABSENT | exit=**2**, preamble PRESENT, `testenv: fixture` |

  **Exit code is 2 in all six cells.** An exit-code differential could not come back false —
  the milestone's own defect class, caught by measurement rather than by review. Two causes:
  with escalation stripped, `migrate` becomes the reporter and fails anyway (D-03's point,
  measured from the other side); and the directory-fixture also breaks `segment`'s own hash
  pin, which fails hard regardless of escalation.

  **The escalation preamble discriminates cleanly in all six cells**, and it is built from
  `testenv.RequireEnv` — an exported constant the project owns.
  — **Reversibility:** reversible.

- **D-15: Reporter identity is asserted only where the reporter's text is ours.** PROOF-01's
  control additionally asserts `config`'s message in the defeated tree — `config` is ours.
  PROOF-02's control does **not** assert `new migrator`: that is golang-migrate's text, and
  pinning to it is Phase 2's carried warning #2 done on purpose. This gets the "who spoke"
  signal without reintroducing a defect already paid for.
  — **Reversibility:** reversible.

- **D-16: Each control reuses its proof's captured intact-tree `RunResult`, and asserts that result is real before comparing.** The control adds only the defeated-tree run.

  Running both sides independently would cost ~64s on an 18s gate (**4.5×**), and
  independence bought at that price is independence someone removes in six months — leaving
  the coupling back **without** the assertion that made it safe.

  **The guard's comment must state what will read as redundant later:** it is **not** checking
  that the proof passed. It is checking that the proof **ran**. A control comparing against a
  result that was never produced is the vacuous-pass shape one indirection along, and the `if`
  exists to make that specific failure loud rather than silent.
  — **Reversibility:** reversible.

### What the assertions bind to

- **D-17: Assertions bind to exported constants where they exist, and to test-supplied values elsewhere.** PROOF-01 → `testenv.URLEnv`. Every preamble check → `testenv.RequireEnv`.
  PROOF-02 → the host string the test itself supplied (`127.0.0.1:1`), which couples to
  nothing. No proof quotes prose `testenv` could reword.

  **Exporting `testenv`'s message builders was refused, for this phase's own reason:** binding
  a proof to a builder shared with the code under proof means a reword changes both sides
  simultaneously, so the assertion **cannot fail on a reword**. It stops checking the message
  and starts checking that the same function was called. **"Cannot drift" and "cannot come
  back false" are the same property described from opposite ends**, and this milestone exists
  to remove the second.

  **PROOF-03 binds to the common suffix `core/domain/segment/testdata/demo.md`.** The path has
  two spellings — on disk `internal/core/domain/segment/testdata/demo.md`, in the message the
  call-site literal `../../../core/domain/segment/testdata/demo.md`
  (`segmentation_test.go:244`). The suffix is the actual invariant: move the fixture and both
  spellings change, so the assertion fails — correct; change only the call site's relative
  depth and the suffix survives — also correct, because the file did not move. **This is the
  one genuine coupling left and is recorded as such rather than treated as closed** — but it
  is coupled to *where the fixture lives*, which is what GATE-03 names.
  — **Reversibility:** reversible.

- **D-18: Each proof asserts the preamble and the cause appear on a SINGLE line**, not as
  independent conjuncts.

  `Contains(cause)` alone is weaker than it looks: `EPISTEMIC_OS_DB_URL` appears in the
  Makefile help, in README, in `config`'s error, **and in `testenv`'s own lenient *skip*
  message** — so it passes on a run that skipped. And `exit != 0` cannot rescue it, since
  exit=2 was measured in all six cells including every defeated one; as a conjunct it does no
  work, inside the phase about checks that do no work.

  Measured available: all three escalated paths format preamble and cause into **one**
  `Fatalf`, so they land on one line. Asserting same-line rules out the lenient-skip false
  positive **structurally**, and rules out the cause appearing in Makefile help while the
  preamble appears in an unrelated failure.
  — **Reversibility:** reversible.

- **D-19: GATE-10 — declared NEW SCOPE in Phase 3.** D-18 couples the proofs to the preamble
  and cause arriving in **one message**, which is GATE-06's design but **not its stated text**.
  Someone splitting that `Fatalf` in two would break three proofs without violating any
  written requirement, and the failure would read as a proof defect rather than a requirement
  change. So the requirement says it.

  **Recorded as a declared amendment, NOT as the sweep half.** GATE-06's text is not false, it
  is **incomplete** — and adding a constraint is a scope act however small the change and
  however clearly the measurement shows no code moves. Recording it as a sweep would set a
  precedent the next person reads as licence to strengthen requirements under a sweep, which
  is a worse cost than one extra line in Phase 3's requirement set. **The distinction only has
  value if it is held when holding it is inconvenient.**

  **Why this does not contradict deferring the GOV-01 derivation amendment** (Deferred Idea
  2), since on the surface it looks like the opposite call: that one was refused because Phase
  3's close sweep would run against a rule the phase changed — a check validating its own
  amendment. GATE-06 is not GOV-01's rule; amending it does not touch the sweep's logic, so
  the self-reference does not arise. **Different objection, not a reversal.**

  **A new ID, not a re-listed GATE-06.** GATE-06 stays Phase 2 / Complete, byte-untouched —
  accurate for what it required and when. GATE-10 states the single-message constraint, maps
  to Phase 3, and cites GATE-06 as what it strengthens. This preserves REQUIREMENTS.md's
  stated **one-requirement-one-phase** invariant (which `planning-parity.sh` does *not*
  enforce), keeps frozen records frozen, and needs no script change — its ID regex is
  `[A-Z]{2,}-[0-9]{2}` with no hard-coded prefix. Existing GATE IDs run to 09.

  **This is the fourth application of one pattern: do not edit the historical record, write
  beside it.** The others: `01-REVIEW-ADJUDICATION.md` left unedited with a disposition layer
  beside it; `030521b` left in STATE.md as the record of a rejection rather than scrubbed;
  `d90b10d` left deliberately unannotated as the review-of-record.

  **GATE-10's text must make clear it strengthens rather than duplicates** — it is the
  constraint GATE-06's design always had and never stated, which the proofs then depended on.
  Otherwise the next sweep finds two requirements about the same message and cannot tell which
  is authoritative.

  **Phase 3's requirement set growing is the honest outcome.** Phase 2's grew by six, every one
  declared rather than slid in, and that is precisely why the growth was reviewable. A phase
  whose requirement set never moves is either lucky or not looking.
  — **Reversibility:** costly — three proofs bind to GATE-10; withdrawing it returns them to depending on an unwritten property.

### Phase 3's close sweep

- **D-20: Phase 3's close sweep writes no SUMMARY file.** It produces `03-GOV-SWEEP.md` and
  its own commit. The name is the mechanism — the same shape as 02's rename that took the
  runbook out of the wave graph.

  **The mechanism, measured, and it is not the one on record.** `isPhaseComplete`
  (`verification.cjs:565`) is `verification.status === 'passed'`, and the staleness rule
  (`verification.cjs`, `#2348`) is *"a `*-VERIFICATION.md` is stale when a summary is newer
  than it."* Measured live:

  | Phase | `verification.status` |
  |---|---|
  | 01 | `passed` |
  | 02 | **`stale`** |

  Phase 2 reads `stale` because `02-05-SUMMARY.md` is newer than `02-VERIFICATION.md`, so
  `isPhaseComplete` returns false and `completed_phases` reverts to 1. **This is structural
  for any phase whose sweep runs after verification and writes a SUMMARY — and GOV-01 mandates
  that timing.** With no SUMMARY written, the staleness comparison has nothing newer to find.

  **The SUMMARY filename is NOT mandated by GOV-01** — verified: GOV-01's requirement text
  never mentions a summary, and ROADMAP's sweep entry does not either. The "own commit and
  summary" wording is Phase 2's **D-16**, a CONTEXT decision. So this is a plan-shape choice
  and costs nothing; no GATE-10-style declaration is needed.

  **State the divergence from Phase 2 explicitly** in `03-GOV-SWEEP.md`: 02's sweep wrote a
  SUMMARY, 03's does not, and a reader comparing the two phases must find the reason rather
  than infer an inconsistency.
  — **Reversibility:** reversible.

- **D-21: Correct `13071ff`'s recorded diagnosis in place, restating the original claim.**
  The same treatment FINDING-01 received when its normalizer-bug cause proved false.

  `13071ff`'s commit message and the finding registered from it both name **SUMMARY-to-PLAN
  pairing** — *"its phase-completion heuristic does not recognize the post-checkpoint
  runbook's SUMMARY (02-05-SUMMARY.md, associated with 02-GOV-SWEEP-RUNBOOK.md rather than a
  \*-PLAN.md file) as completing Phase 2."* That is wrong, and it is **inverted**: the pairing
  never enters the computation. `scanPhasePlans`'s SUMMARY/PLAN counts feed
  `total_plans`/`completed_plans`, different fields entirely. Phase completion routes through
  `isPhaseComplete` → `verification.status === 'passed'`, and `02-05-SUMMARY.md` is not
  *unrecognised* — it **is** seen, it **is** newer than `02-VERIFICATION.md`, and being seen is
  exactly what marks verification stale.

  **Record what the wrong diagnosis would have caused, not merely that it was wrong:** teaching
  the SUMMARY/PLAN pairing to recognise runbooks — the fix the recorded mechanism implies —
  would have changed nothing. `completed_phases` would still read 1, because pairing is not
  what the counter consults. A wrong mechanism yields a wrong fix that *appears* responsive.

  **Second instance this week of a registered finding describing a mechanism that was not the
  one operating** — FINDING-01's normalizer diagnosis was the first. Both were explanations
  that fit the evidence, asserted rather than measured, and both were falsified by someone
  reading the code path instead of the finding. Commits are immutable, so the correction lands
  in the artifacts and cites `13071ff`.
  — **Reversibility:** reversible.

### Claude's Discretion

Not selected for discussion, or explicitly left to defaults. Each is requirement-faithful and
none contradicts a decision above.

- **Stream selection.** Assertions read `RunResult.Combined`. The harness's own doc warns
  `Combined` is concatenation, not interleaving, so no proof may assume ordering **between**
  the two streams. D-18's same-line requirement is within one stream, so this is safe.
- **The throwaway copy is built once and shared** across PROOF-03 and the three controls where
  the tree contents allow, rather than re-extracted per test — `git archive HEAD` plus the
  defeat edit is deterministic, and `GOCACHE` is content-addressed and shared, so the copy
  builds warm. A control needing a *differently* defeated tree gets its own.
- **Vacuity guard placement.** Each proof asserts its condition was reproduced before asserting
  anything about the message — the `makeSide.ExitCode == 0` shape already used at
  `makefile_test.go:44`. Note D-18's finding: exit code alone is not a sufficient guard here,
  so the preamble check carries that weight.
- **Test naming** follows `TestContext_Behavior` per CONVENTIONS.md, with the requirement ID in
  the name (e.g. `TestPROOF01_GateNamesUnsetURL`) so `grep PROOF-01` reaches the test.
- **CI wall-clock** is accepted as measured: ~+41s on a 141s cold CI gate. No CI config change;
  `ci.yml`'s `go` job stays a single `make gate` step (CI-02).
- **`03-GOV-SWEEP.md` invocation** follows 02's precedent — invoked explicitly by path after
  verification, UAT and security sign-off, never reachable from `/gsd-execute-phase`. Its
  filename must not end `-PLAN.md` (`plan-scan.cjs:141` schedules every such file).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

ROADMAP.md carries no `Canonical refs:` line for this phase. The list below was accumulated
from REQUIREMENTS.md, PROJECT.md, ROADMAP.md, the codebase scout, and the measurements taken
during this discussion.

### Requirements and governance
- `.planning/REQUIREMENTS.md` — PROOF-01/02/03 texts; GATE-06's text, which **D-19 amends via
  the new GATE-10**; GOV-01's four obligations, of which obligation 2 (the
  `make planning-parity PHASE=3` precondition) binds this phase's **first plan**; the
  Traceability table and its stated one-requirement-one-phase invariant
- `.planning/ROADMAP.md` §Phase 3 — the five success criteria (**SC-5 is corrected by D-12**),
  the `**Requirements**:` line (**gains GATE-10 per D-19**), and the **Note on the harness**,
  which is this phase's starting contract
- `.planning/PROJECT.md` — §Constraints (hard fail, no exception, locally and in CI), §Out of
  Scope, and **lines 91-93**, the recorded tension SC-4 charters this phase to solve
- `.planning/STATE.md` — §Accumulated Context (the 02-02 harness entries), §Blockers/Concerns
  (the amended Phase 3 design-question entry naming exactly what 02-02 did and did not solve),
  and §Pending Todos
- `.planning/phases/02-enforcement-and-a-single-gate-definition/02-CONTEXT.md` — **D-07**
  (harness as Phase 3's, its two binding conditions), **D-11** (the `make-gate` flag value and
  its paths-not-precedence limit), **D-03** (voiceless preflight ordering), **D-16** (the
  sweep's own plan — source of the "own commit and summary" wording D-20 departs from)
- `.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP.md` — the
  derivation command verbatim (`git ls-files '.planning/*'`), the per-artifact evidence table
  shape, and the re-arm/halt rule
- `.planning/phases/02-enforcement-and-a-single-gate-definition/02-FINDING-01-state-authority.md`
  — STATE.md's many-writers problem, and the precedent for **D-21**'s in-place correction with
  the original claim restated
- `.planning/phases/02-enforcement-and-a-single-gate-definition/02-FINDING-02-gitignored-instrumentation.md`
  — **constrains any fix touching `.claude/`**; read before choosing one, not after

### Code this phase writes or changes
- `internal/platform/gate/harness.go` — `RunOptions` gains `Dir` (**D-08**);
  `DefaultTimeout`'s rationale comment is corrected and tagged `PROOF-03` (**D-05**);
  `buildChildEnv`'s `DepthEnv`-last ordering **must not change**
- `internal/platform/gate/makefile_test.go` — the differential pattern (`extraLines`, make side
  vs direct side) and the `ExitCode == 0` vacuity guard the proofs reuse in shape;
  `closedPortDSN` and `composeDSN` constants. **Not moved** (D-03)
- `internal/platform/gateproof/` (new) — PROOF-01/02/03 and the three SC-5 controls
- `Makefile` — read-only here; `gate`'s target-scoped export at line 77 is what the controls
  strip **in the copy**, never in the tree

### Read-only context, measured during discussion
- `internal/platform/testenv/testenv.go` — exported `URLEnv` (:37) and `RequireEnv` (:41), the
  tokens D-17 binds to; `escalationPreamble` (:54) unexported; the three escalated `t.Fatalf`
  sites (:149, :182, :212), each formatting preamble and cause into **one** message, which is
  D-18's structural basis and GATE-10's subject; `hostFromURL` (:112) and the no-DSN
  discipline; `Pool`'s documented four-step order and the note that `Fixture` runs only after
  `Pool` returns
- `internal/adapters/secondary/store/segmentation_test.go:244` — the repo's **only**
  `testenv.Fixture` call, and the source of PROOF-03's message path spelling
- `internal/core/domain/segment/fixture_test.go` — the hash-pinned direct reads of `demo.md`
  that fail independently of escalation (the measured cause behind D-09 and D-14)
- `scripts/planning-parity.sh` — the start check D-13 requires; its ID regex
  `[A-Z]{2,}-[0-9]{2}` accepts GATE-10 with no change; it does **not** enforce
  one-requirement-one-phase
- `.claude/gsd-core/bin/lib/verification.cjs` — `isPhaseComplete` (:565) and the `#2348`
  staleness rule, the measured basis for **D-20** and **D-21**
- `.planning/codebase/TESTING.md`, `.planning/codebase/CONVENTIONS.md` — naming and structure
  conventions the new package follows

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`internal/platform/gate`** — built as this phase's harness and confirmed at a human
  checkpoint. `Make`, `Run`, `RunOptions`, `RunResult`, `SkipIfNested`, `RepoRoot`, `DepthEnv`,
  `DefaultTimeout` are all exported; only `Dir` is missing (D-08).
- **`makefile_test.go`'s differential shape** — `extraLines` multiset comparison plus an
  explicit "the condition was not reproduced" guard before any content assertion. The SC-5
  controls are the same shape with a different pair of sides.
- **`closedPortDSN = "postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable"`** — reproduces the
  unreachable-database condition without stopping the compose service, and its host token
  `127.0.0.1:1` is test-supplied, so PROOF-02 couples to nothing.
- **02-03's `git archive HEAD` negative-control pattern** — D-07 and D-11 reuse it rather than
  inventing a tree-isolation approach.
- **`01-01`/`02-01`'s `<precondition>` block** — the executor-honored, non-skippable shape
  GOV-01 obligation 2 reuses for `make planning-parity PHASE=3`.

### Established Patterns
- **Turn intentions into things that fail.** Decided D-02, D-05, D-14, D-16 and D-18 here.
  Twice in this discussion an assertion that *could not come back false* was caught by
  measurement rather than review.
- **Bind to what we own.** Exported constants and test-supplied values, never foreign prose
  (D-15, D-17). `new migrator` is golang-migrate's; `config`'s message is ours.
- **Do not edit the historical record — write beside it.** Fourth application at D-19.
- **`127.0.0.1`, never `localhost`** — this host has no `::1` listener, and `localhost`
  resolves there first. Carried from D-11's finding.
- **Frozen artifacts are not rewritten** — which is why D-03 refused to relocate
  `makefile_test.go` and D-19 refused to re-list GATE-06.

### Integration Points
- `internal/platform/gateproof` → `internal/platform/gate`'s **exported surface only**; the
  package boundary is the enforcement mechanism, not a stylistic choice (D-03).
- Every proof → `make gate` as a subprocess at depth 1; the nested gate runs `migrate` and the
  full suite against the **shared** compose database, concurrently with the outer suite (D-06's
  measured coupling).
- `harness.go`'s `PROOF-03` tag → the close sweep's derived artifact list; today via its
  "Phase 3" prose, and durably via the tag once the derivation amendment lands.

</code_context>

<specifics>
## Specific Ideas

- **"Cannot drift" and "cannot come back false" are the same property described from opposite
  ends.** The reason `testenv`'s message builders are not exported for the proofs to bind to
  (D-17). A shared builder makes the assertion move with what it checks.
- **"It isn't checking the proof passed. It's checking the proof RAN."** The sentence D-16
  requires in the shared-result guard's comment, because the `if` will read as redundant later.
- **A criterion falsified by a later deliberate decision reads differently from one that was
  always wrong.** D-12's framing for the SC-5 correction — the shape shared by `ci.yml`'s job
  name and `harness.go`'s timeout rationale.
- **The tag's value is not coverage, it is durability.** `harness.go` is already in the derived
  set via prose; the `PROOF-03` tag keeps it there when the prose is reworded.
- **"The distinction only has value if it's held when holding it is inconvenient."** Why
  GATE-10 is a declared amendment rather than a sweep correction (D-19).
- **"A phase whose requirement set never moves is either lucky or not looking."**
- **Make the dependency explicit where a reader will meet it.** Identified during discussion as
  this phase's recurring theme, on its third instance: the `harness.go` tag (D-05), the SC-5
  correction (D-12), and GATE-10 (D-19).

</specifics>

<deferred>
## Deferred Ideas

Registered rather than absorbed, because **a declaration inside a plan closes with the phase; a
named deferred item does not.** Each carries its measurement.

1. **Isolate PROOF-03's nested run on its own database or schema.** Measured interference,
   present *today* before Phase 3: `gate` × `store` **+2.11s concurrent**, `gate` × `approved`
   **+0.80s**, from per-package intervals in `go test ./... -json` (`store` 2.42→6.57s,
   `approved` 2.32→5.26s, `gate` 4.46→25.70s). Phase 2's nested `make test` already runs
   `store` tests against the compose database while the outer `store` package is running;
   Phase 3 adds `migrate` to that set. Not taken because it is arguably its own requirement —
   new machinery in a phase scoped to three proofs.

2. **Amend GOV-01's close-sweep derivation to IDs-only, repo-wide.** The current rule is
   path-scoped — `git ls-files '.planning/*'` — so a requirement-ID tag in a file outside
   `.planning/` buys nothing; `ci.yml` and `harness.go` would each stay invisible **fully
   tagged**. Measured: widening to `git ls-files` costs 5.3s over 227 tracked files and takes
   the derived set 51 → 54, adding `harness.go` ✓, `testenv_test.go` ✓, and `classify_test.go`
   ✗ — a **false positive**, matching on "phase 3's done-condition", the *segmentation
   pipeline's* phase 3. So the amendment must be **IDs-only outside `.planning/`, with no
   phase-number term**: requirement IDs are globally unambiguous, phase numbers are not, and
   the phase-number term is the sole noise source.
   **Refused for Phase 3 deliberately:** Phase 3's own close sweep would then run against a
   rule the phase changed — a check validating its own amendment, the same self-reference that
   disqualified VERIFICATION.md as GOV-01's home. Decide at milestone close. Nothing is lost by
   waiting: `harness.go` is already in the derived set today via its "Phase 3" prose.
   **The argument for the amendment, verbatim, because it is better than the one first given:**
   the tag's value is **not** getting `harness.go` into the set — it is already in, unprompted.
   It is **keeping it in when someone rewords the prose.** A durability property, not a
   coverage one.

3. **Register the class: a measured or descriptive claim in a code file outside `.planning/`,
   accurate when written, invisible to the derivation.** Two instances:

   | File | Claim that went stale | Found by |
   |---|---|---|
   | `.github/workflows/ci.yml` | job named `vet + test + fmt` after CI-02 collapsed it to one `make gate` step | a human running Phase 2 UAT test 12 |
   | `internal/platform/gate/harness.go` | `DefaultTimeout` "roughly six times the slowest plausible child" — warm figures; the cold worst case is 85s, a 2.8× margin | a cold-cache measurement in this discussion |

   **Neither was found by a sweep. Both were found by someone running something.** This is
   GOV-01's declared bound behaving as declared, not a defect in it — recorded so the next
   reader learns the mechanism has an edge from the register rather than from the next escape.

4. **SC-5's literal wording is unreachable through the harness, by design.** `buildChildEnv`
   sets `DepthEnv` last and skips any entry naming it, so a control spawning the proof package
   hands it depth 1 and every proof `SkipIfNested`-skips — three skips and a green run. D-12
   corrects the criterion and D-11 supplies what is provable instead; this entry preserves *why*
   the original wording could not stand, so the correction is not later mistaken for a
   weakening.

5. **`13071ff`'s recorded diagnosis is wrong; its correction is D-21's scope**, carried here so
   it travels if Phase 3 is rescoped: the registered finding names SUMMARY-to-PLAN pairing; the
   operating mechanism is `verification.cjs`'s `#2348` staleness rule plus `isPhaseComplete`'s
   `status === 'passed'`. The wrong diagnosis implies a fix — teaching the pairing to recognise
   runbooks — that would have left `completed_phases` reading 1.

### Out of scope, noted and not acted on
- **Relocating `makefile_test.go`** into the proof package for a cleaner boundary (D-03). A
  refactor available at any time; doing it here would edit frozen Phase 2 deliverables.
- **Adding the fixture-*absence* case to PROOF-03** alongside the unreadable case (D-09). Cheap
  to add later; GATE-03 says unreadable, and the budget belongs to the stated condition.

</deferred>

---

*Phase: 3-Automated Proof*
*Context gathered: 2026-09-02 – 2026-09-03*
