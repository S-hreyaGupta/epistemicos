# Phase 3: Automated Proof - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `03-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-09-02 – 2026-09-03
**Phase:** 3-Automated Proof
**Areas discussed:** Gate depth per proof, Breaking the fixture, Proving the proofs, What
assertions bind to, Phase 3's close sweep

**Note on method.** Six measurements were taken during this discussion rather than after it.
Two of them **reversed** a position that reasoning had already produced, and one of those
would have written a vacuous assertion into CONTEXT.md. They are recorded per-area below.

---

## Gate depth per proof

### Q1 — How far up the gate does each proof shell out?

| Option | Description | Selected |
|--------|-------------|----------|
| All three call `make gate` | Highest fidelity; matches ROADMAP's Note; three nested gates | |
| Shortest target per condition | PROOF-01/02 → `env-preflight`, PROOF-03 → `gate`; cheapest | |
| Gate for all three + one cheap ordering proof | SC-1/2/3 proven as worded; ordering claim carried separately | ✓ |

**User's choice:** Gate for all three, plus a separate cheap ordering proof.
**Notes:** Two reasons beyond fidelity, both stated as holding *whatever the measurement
returned*. Each test gets a single reason to fail — Phase 2's warning-2 fix generalised; the
D-03 claim survives a reword because it rests on two checks that fail differently. And it
degrades gracefully: three nested gates create pressure to trim, and under "all three call
`make gate`" alone the ordering claim would disappear with them silently, because it was only
ever a side effect.

**Measurement taken (warm cache, live Postgres):** PROOF-01 shape 7.7s (exit 2), PROOF-02
shape 6.4s (exit 2), PROOF-03 shape 18.2s (exit 0), `make env-preflight` closed-port **5.6s,
exit 0**. Two findings: the cheap option saved under one second, and `env-preflight` alone
*passes* against an unreachable database because the escalation flag is target-scoped to
`gate`. "Shortest target" was therefore not a cheaper proof of the same claim but a proof of a
weaker one.

### Q2 — What does the cheap ordering proof assert?

| Option | Description | Selected |
|--------|-------------|----------|
| `make -n gate` recipe expansion | Structural, near-zero cost, no database | |
| Positional assertion in PROOF-02's output | Free; proves effect; but an absence check | |
| Both — structure and effect | Two cheap checks failing for different reasons | ✓ |

**User's choice:** Both.
**Notes:** Reordering the recipe fails the first; a change leaving order intact but letting
migrate speak anyway fails the second. Neither carries the other's job.

### Q3 — Where do PROOF-01/02/03 live?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate package, harness as external API | D-07 condition 1 becomes compiler-enforced | ✓ |
| Same package (`internal/platform/gate`) | Simplest; condition stays an unfalsifiable claim | |
| Separate package + move `makefile_test.go` | Cleanest boundary; touches frozen Phase 2 files | |

**User's choice:** Separate package, harness used as an external API.
**Notes:** "The deciding property is that it makes D-07's condition compiler-enforced rather
than asserted. Under option 2 the condition survives as a claim nobody can falsify, which is
the exact defect class this milestone exists to remove — and it would be sitting inside the
phase that proves the milestone." Option 3 refused: the cleaner boundary "isn't worth touching
frozen Phase 2 deliverables to get… doing it here manufactures a GOV-01 instance rather than
finding one."

### Q4 — Shared compose database under PROOF-03's nested `migrate` + full suite

| Option | Description | Selected |
|--------|-------------|----------|
| Declare the coupling, keep the shared database | Makes Phase 2's warning #3 declared | |
| Isolate the nested run on its own database | Removes the path; new machinery | |
| Declare now, register isolation as a deferred item | Declaration that outlives the phase | ✓ |

**User's choice:** Declare now, register isolation as a deferred item — **with the
interference path measured rather than described.**
**Notes:** "A declaration inside a plan closes with the phase; a named deferred item doesn't."
And: "if that's demonstrable, the deferred item carries a measurement… either way it beats 'a
real interference path stays open', which is true but not sized."

**Measurement taken:** per-package intervals from `go test ./... -json`. `gate` 4.46→25.70s,
`store` 2.42→6.57s, `approved` 2.32→5.26s. **`gate` × `store` +2.11s concurrent; `gate` ×
`approved` +0.80s.** The path is real today, before Phase 3.

### Q5 — Follow-ups (user-initiated, two of four taken)

**Non-parallel:** pinned explicitly. "Three proofs each shelling out to a full `make gate`
against one shared compose database, made safe by a default nobody stated, is Phase 2's
warning #3 with more at stake. A later `t.Parallel()` would be a one-line change with no
visible consequence until CI goes flaky."

**CI cold cache:** "the 6–18s figures are warm… If DefaultTimeout's 4 minutes was set against
those, it's calibrated on the wrong baseline."

**Measurement taken (fresh `GOCACHE`):** cold parent full green gate **141s**; children after
a cold parent 11s / 9s / 21s; **cold child with no warm parent 85s**. The CI case is fine —
the parent warms the cache and the children inherit it. But `DefaultTimeout`'s documented "six
times the slowest plausible child" is measured against warm figures; against the true cold
worst case the margin is **2.8×, not 6×**.

**Trim trigger:** deliberately skipped — "a judgement best made when the pressure actually
arrives, and the cheap ordering proof already means a trim doesn't take the ordering claim
with it."

### Q6 — `DefaultTimeout` and its now-false rationale

| Option | Description | Selected |
|--------|-------------|----------|
| Keep 240s, correct the comment with the cold number | The value was never wrong; the rationale was | ✓ |
| Raise it and correct the comment | Treats 2.8× as too thin; slower hang reporting | |
| Keep 240s, correct, add per-proof timeouts | Three more numbers that can go stale the same way | |

**User's choice:** Keep 240s, correct the comment — **plus tag the corrected comment with its
requirement ID.**
**Notes:** "The reason `harness.go` is invisible to the sweep is that it names no requirement
ID… So make the corrected comment cite the requirement it serves. A comment that names an ID
enters the derived sweep set… That turns the bound from a permanent blind spot into an opt-in
— any code comment carrying a measured claim can buy its way into coverage with one
identifier." Also registered the class with its two instances (`ci.yml`, `harness.go`):
"Neither was found by a sweep. Both were found by someone running something."

### Q7 — Where the GOV-01 derivation amendment lands

| Option | Description | Selected |
|--------|-------------|----------|
| Declare it as a new Phase 3 requirement | Amend now; sweep then runs against a changed rule | |
| Register it, take only the comment correction now | Decide at milestone close | ✓ |
| Amend now, IDs-only repo-wide, no phase-number term | Strictly better rule; still Phase 3 scope | (rule shape adopted) |

**User's choice:** Option 2, adopting option 3's rule shape when the amendment lands.
**Notes:** "The deciding factor is option 1's own stated cost: the close sweep would run
against a rule the phase changed. That's the same self-reference we rejected when
VERIFICATION.md was floated as GOV-01's home — a check can't be its own subject." And, on the
tag: "the tag's value isn't getting `harness.go` into the set — it's already in today,
unprompted. It's keeping it in when someone rewords the prose. That's a durability property,
not a coverage one, and it's a better argument for the amendment than the one I gave."

**Measurement taken:** widening `git ls-files '.planning/*'` → `git ls-files` costs 5.3s over
227 tracked files and takes the derived set 51 → 54. Added: `harness.go` ✓, `testenv_test.go`
✓, `classify_test.go` ✗ — a false positive on "phase 3's done-condition", the segmentation
pipeline's phase 3. This is why the amendment must drop the phase-number term outside
`.planning/`.

---

## Breaking the fixture

### Q1 — How does PROOF-03 make `demo.md` unreadable?

| Option | Description | Selected |
|--------|-------------|----------|
| Throwaway `git archive HEAD` copy | Reuses 02-03's pattern; needs a `Dir` option | ✓ |
| Mutate and restore in the real tree | Cheapest; retired by Phase 1; concurrency hazard | |
| Fixture-root indirection in `testenv` | Fastest; adds a seam to the proven mechanism | |

**User's choice:** Throwaway `git archive HEAD` copy.
**Notes:** "The overlap measurement kills option 2 outright — `segment` and `gate` run
concurrently, so mutating the real tree corrupts a file another package is reading, and the
failure lands somewhere unrelated to PROOF-03. Measured, not argued." Option 3 refused on its
own reasoning: "a bypass built for a proof is still a bypass." On the `Dir` extension: "It's an
addition to the exported surface rather than a rewrite, so D-07's condition 1 stays
compiler-enforceable… That's the property we chose the separate package for, and this is the
first thing to test it." Also noted: "the overlap number does double duty: it decides this
question and sizes the deferred isolation item. One measurement, two uses."

### Q2 — What exactly makes it unreadable inside the copy?

| Option | Description | Selected |
|--------|-------------|----------|
| Replace the file with a directory | Genuine read failure; portable | ✓ |
| Delete the file | Simplest; proves the *absent* case | |
| Both, as two subtests | Covers both; ~18-21s more per gate run | |

**User's choice:** Replace with a directory.
**Notes:** "Option 2 fails its own test — absence isn't unreadability, and an adjacent proof
standing in for the stated one is the habit we keep breaking." Option 3: "buying something the
requirement doesn't ask for… the phase whose job is proving the stated condition shouldn't
spend its budget on an adjacent one." Carried forward to the assertions area: "the errno text
differs across platforms, so binding to the path is the portable choice — a constraint arriving
from measurement rather than preference."

---

## Proving the proofs

*Added to the queue by the user after the initial selection, positioned after Breaking the
fixture "since how the fixture gets broken decides whether a throwaway copy is even available
to defeat the mechanism in."*

**Constraint surfaced before the options:** `buildChildEnv` sets `DepthEnv` last and skips any
entry naming it, deliberately, so a control spawning the proof package hands it depth 1 and
every proof `SkipIfNested`-skips. SC-5's literal wording is not reachable through the harness.

### Q1 — How is SC-5 proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Differential: one command, two trees | Reuses the copy machinery; no depth-guard hole | ✓ |
| Direct: run the proof package in the defeated copy | Literal SC-5; puts a hole in the guard | |
| Measured demonstration at verification | Zero machinery; the decaying manual checklist | |

**User's choice:** Differential.
**Notes:** "The entailment is sound and worth stating in the test rather than leaving implicit…
a reader shouldn't have to reconstruct that, so the assertion's comment should say what it is
standing in for." And: the depth-guard finding "should be registered rather than absorbed."

### Q2 — What happens to ROADMAP SC-5's now-unreachable wording?

| Option | Description | Selected |
|--------|-------------|----------|
| Correct SC-5 on the record, cite the guard | GOV-01's sweep half; set untouched | |
| Leave SC-5, record the entailment in verification | Criterion nobody can satisfy stays | |
| Correct SC-5 **and** run the Phase 3 start check first | Same as 1, sequencing free via D-13 | ✓ |

**User's choice:** Correct, sequenced through the start check.
**Notes:** "It's option 1 with the sequencing free… An isolated correction to ROADMAP is
exactly the kind of edit that could quietly disagree with REQUIREMENTS, and this makes that
checkable in the same pass." Two things to carry: name `buildChildEnv`'s deliberate ordering as
what falsified it, because "a criterion falsified by a later deliberate decision reads
differently from one that was always wrong"; and record it explicitly as GOV-01's sweep half —
"its first use on a criterion rather than a status field."

### Q3 — What does the differential assert, and one control or three?

| Option | Description | Selected |
|--------|-------------|----------|
| Three controls, each binding to the preamble | Discriminates in all six cells | ✓ |
| One control, PROOF-02 only | Sharpest cell; adjacent-proof substitution | |
| Three controls + reporter identity for both | Adds `new migrator`, foreign text | (partially adopted) |

**User's choice:** Three controls binding to the preamble, **with option 3's reporter-identity
assertion taken only where the reporter's text is ours.**
**Notes:** "config is ours; migrate's `new migrator` is golang-migrate's, and pinning to it is
Phase 2's warning #2 done on purpose. That gets the 'who spoke' signal for PROOF-01 without
reintroducing a defect we already paid to fix." On three rather than one: "the three conditions
were measured to fail differently in the defeated tree, and one control would have to paper
over that. Papering over is precisely how the exit-code version looked sound."

**Measurement taken — and it reversed the assistant's own design.** The differential had been
specified as "the real tree fails while the defeated copy exits 0." Against a defeated copy
(`gate: export …` stripped) and an intact one, **exit code was 2 in all six cells**: PROOF-01
defeated fell to `config die: required`, PROOF-02 defeated to `migrate: new migrator`, and
PROOF-03 defeated still failed because replacing `demo.md` also breaks `segment`'s own
hash-pinned reads. The escalation preamble was ABSENT in all three defeated cells and PRESENT
in all three intact ones. An exit-code differential could not have come back false — the
milestone's own defect class, caught before it was written down.

*(A first run of this measurement returned exit=127 on two rows; the cause was a malformed
`env` invocation in the probe script — options after assignments — not a finding. Rerun
correctly before any conclusion was drawn.)*

### Q4 — Reuse the proof's intact-tree run, or run both sides independently?

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse the proof's run as the control's intact side | ~+32s; couples proof and control | |
| Run both sides independently | ~+64s on an 18s gate (4.5×); independent | |
| Reuse, and assert the shared result is real | Same cost as 1, closes the coupling's failure mode | ✓ |

**User's choice:** Reuse, plus a realness assertion.
**Notes:** "Option 1's coupling is fine right up until the proof stops running, at which point
the control compares against an empty result and passes trivially… one `if` makes it local, and
a control that can't come back false is the whole subject of this phase." Option 2: "64s on an
18s gate is 4.5×, and independence bought at that price is independence someone removes in six
months, leaving the coupling back but without the assertion that made it safe." Required in the
comment: "it isn't checking the proof passed. It's checking the proof RAN."

---

## What assertions bind to

### Q1 — What do the "names that cause" assertions bind to?

| Option | Description | Selected |
|--------|-------------|----------|
| Exported constants where they exist, test-supplied values elsewhere | No proof quotes rewordable prose | ✓ |
| String literals throughout | Closest to what a developer reads; warning #2 as policy | |
| Export `testenv`'s message builders | Cannot drift; assertion moves with what it checks | |

**User's choice:** Exported constants and test-supplied values.
**Notes:** Option 3 refused explicitly and for this phase's own reason: "Binding the proof to a
builder shared with the code under proof means a reword changes both sides simultaneously — so
the assertion cannot fail on a reword. It stops checking the message and starts checking that
the same function was called. 'Cannot drift' and 'cannot come back false' are the same property
described from opposite ends, and we've spent two weeks removing the second."

On PROOF-03's path, resolved in the same answer: bind to the common suffix
`core/domain/segment/testdata/demo.md`. "That's the actual invariant. Move the fixture and both
spellings change, so the assertion fails — correct. Change only the call site's relative depth
and the suffix survives — also correct, because the file didn't move." Recorded as the one
genuine coupling left, "coupled to where the fixture lives, which is the thing the requirement
names."

### Q2 — What shape does each proof's assertion take?

| Option | Description | Selected |
|--------|-------------|----------|
| Same-line: preamble and cause in one line | Rules out the lenient-skip false positive structurally | ✓ |
| Three independent conjuncts | Contains a conjunct measured unable to fail | |
| Same-line + assert the lenient form absent | Binds to rewordable skip prose | |

**User's choice:** Same-line — **and amend GATE-06 to require single-message delivery.**
**Notes:** "Option 2 contains a conjunct that cannot come back false, measured — exit≠0 holds
in all six cells including every defeated one. A check doing no work, sitting inside the phase
about checks that do no work." On the amendment: "someone splitting that `Fatalf` into two
calls would break three proofs without violating any written requirement, and the failure would
look like a proof defect rather than a requirement change… Then the proofs couple to a stated
requirement rather than to an implementation detail that happens to hold. That's the same move
as the `harness.go` tag and the SC-5 correction — third time this discuss, which suggests it's
the phase's actual theme."

### Q3 — How is the amendment recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep half — same as SC-5, no new scope | Stretches the sweep/scope boundary | |
| Declared amendment to a Phase 2 requirement | Phase 3's set grows; boundary held | ✓ |
| Register it, take nothing now | Proofs couple to an unwritten property all phase | |

**User's choice:** Declared amendment.
**Notes:** "The distinction only has value if it's held when holding it is inconvenient…
Recording it as a sweep would set a precedent that the next person reads as licence, which is a
worse cost than one extra line in Phase 3's requirement set." On the apparent inconsistency with
deferring the GOV-01 derivation amendment: "That one was refused because Phase 3's close sweep
would have run against a rule the phase changed — a check validating its own amendment. GATE-06
isn't GOV-01's rule… Different objection, not a reversal." And: "Phase 3's set growing is the
honest outcome. Phase 2's grew by six, every one declared rather than slid in, and that's
precisely why the growth was reviewable. A phase whose requirement set never moves is either
lucky or not looking."

### Q4 — GATE-06 re-listed, or a new ID?

| Option | Description | Selected |
|--------|-------------|----------|
| New ID (GATE-10), cross-referencing GATE-06 | Preserves the one-phase invariant and frozen records | ✓ |
| Re-list GATE-06 under Phase 3 | One requirement, strengthened; breaks the invariant | |
| Amend GATE-06's text in place, no new row | Smallest diff; manufactures a GOV-01 instance | |

**User's choice:** New ID.
**Notes:** "GATE-06 stays accurate for what it required and when, which is the same principle as
leaving `01-ADJUDICATION` unedited with a disposition layer beside it, and leaving `030521b` in
STATE.md as the record of a rejection rather than scrubbing it. Fourth application of that
pattern now: don't edit the historical record, write beside it." Option 3's cost "names itself —
manufacturing a GOV-01 instance inside the phase that found two." Required in GATE-10's text:
"GATE-10 isn't a new requirement that happens to resemble GATE-06. It's the constraint GATE-06's
design always had and never stated… otherwise the next sweep finds two requirements about the
same message and can't tell which is authoritative."

**Verified during discussion:** `planning-parity.sh`'s ID regex is `[A-Z]{2,}-[0-9]{2}` with no
hard-coded prefix, so GATE-10 works with no script change; and the script does *not* enforce
REQUIREMENTS.md's stated one-requirement-one-phase invariant, which is why option 2 would have
broken it silently.

---

## Phase 3's close sweep

*Added by the user at the final check: "settle now how its sweep is invoked and whether the
progress heuristic will do the same thing — otherwise it recurs in a phase whose subject is
proving mechanisms work."*

### Q1 — How does Phase 3 handle the close-sweep-stales-verification mechanism?

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep writes no `*-SUMMARY.md` | The name is the mechanism; nothing newer to find | ✓ |
| Re-run `verify-work` after the sweep | Verification post-dates the sweep; ordering loop | |
| Accept it, hand-correct, record the real mechanism | Known-wrong counter left in place | |

**User's choice:** Sweep writes no SUMMARY — plus the correction below, "which is independent
of the option."
**Notes:** Two things settled inside it, both raised by the user: whether the SUMMARY filename
is mandated by GOV-01 or is GSD convention (**verified: convention** — GOV-01's requirement text
never mentions a summary; the "own commit and summary" wording is Phase 2's D-16, a CONTEXT
decision, so renaming costs nothing and needs no declaration); and that the divergence from
Phase 2 must be stated explicitly, "a reader comparing the two phases should find the reason
rather than infer an inconsistency."

**Measurement taken:** `verification.status` reads `passed` for Phase 1 and **`stale`** for
Phase 2. `isPhaseComplete` (`verification.cjs:565`) is `status === 'passed'`; the `#2348`
staleness rule is "a `*-VERIFICATION.md` is stale when a summary is newer than it."

### Q2 — What happens to `13071ff`'s recorded diagnosis?

| Option | Description | Selected |
|--------|-------------|----------|
| Correct it in place, restate the original claim | FINDING-01's precedent | ✓ |
| Record it as a new Phase 3 finding only | Leaves the wrong mechanism standing alone | |

**User's choice:** Correct in place.
**Notes:** "The real mechanism is `verification.cjs`'s #2348 — a `*-VERIFICATION.md` is stale
when a summary is newer than it, and `isPhaseComplete` requires `status === 'passed'`. The
pairing never enters it. Correct both on the record, and say what the wrong diagnosis would have
caused: teaching the pairing to recognise runbooks, and the counter still reading 1." And: "That's
the second time this week a registered finding turned out to describe a mechanism that wasn't the
one operating — the normalizer diagnosis in FINDING-01 was the first. Both were explanations that
fit the evidence, asserted rather than measured, and both were falsified by someone reading the
code path instead of the finding."

---

## Claude's Discretion

Left to defaults, none contradicting a decision above: stream selection (`RunResult.Combined`,
never assuming interleaving between streams); building the throwaway copy once and sharing it
where tree contents allow; vacuity-guard placement following `makefile_test.go:44`'s shape; test
naming carrying the requirement ID; accepting CI wall-clock as measured with no `ci.yml` change;
and `03-GOV-SWEEP.md`'s explicit by-path invocation with a filename that must not end `-PLAN.md`.

The user explicitly declined one further area — the cost trim trigger — and accepted defaults on
three planner-shaped questions: CI wall-clock, whether the copy is built once and shared, and the
`Dir` extension's exact shape on `RunOptions`.

## Deferred Ideas

1. Isolate PROOF-03's nested run on its own database or schema (carries the +2.11s / +0.80s
   overlap measurement).
2. Amend GOV-01's close-sweep derivation to IDs-only repo-wide, no phase-number term (carries the
   51→54 / 5.3s / 227-file measurement and the `classify_test.go` false positive).
3. Register the class of measured claims in code files outside `.planning/`, with its two
   instances (`ci.yml`'s job name, `harness.go`'s timeout rationale).
4. SC-5's literal wording being unreachable through the harness by design.
5. `13071ff`'s wrong diagnosis and what the implied fix would have failed to do.

Out of scope, noted and not acted on: relocating `makefile_test.go` into the proof package; adding
the fixture-absence case to PROOF-03 alongside the unreadable case.
