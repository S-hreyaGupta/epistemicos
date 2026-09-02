---
phase: 02-enforcement-and-a-single-gate-definition
plan: 05
type: post-checkpoint-sweep
runbook: 02-GOV-SWEEP-RUNBOOK.md
status: in-progress
---

# GOV-01 Close Sweep

Runs GOV-01's second required mechanism (D-12): the phase-**close** derived-artifact
sweep, after every wave plan, UAT and security sign-off. The phase-**start** check
(D-12's first run) already passed at the `02-01-PLAN.md` precondition and its
correction is recorded at `788136f`.

Precondition re-run by this executor, independently, before this document was
started:

```
PRECONDITION OK: four SUMMARYs landed; verification passed, UAT complete, security
verified with 0 open threats; all three checkpoints commit-after the final SUMMARY.
LAST_SUMMARY=46d587e78c355818a4cf1abd89151b655449cead
```

## Task 1 — Derivation

**The rule (GOV-01's amended text):** every tracked file under `.planning/` that
names this phase number or one of its ten requirement IDs — GATE-01, GATE-02,
GATE-03, CI-02, GATE-06, GATE-07, GATE-08, GATE-09, SEC-01, GOV-01.

**Command, recorded verbatim:**

```bash
IDS='GATE-01|GATE-02|GATE-03|CI-02|GATE-06|GATE-07|GATE-08|GATE-09|SEC-01|GOV-01'
derive() {
  git ls-files '.planning/*' | while IFS= read -r f; do
    if grep -qE "($IDS)|[Pp]hase 2([^0-9.]|$)|(^|/)02-" "$f" 2>/dev/null; then printf '%s\n' "$f"; fi
  done | sort -u
}
derive
```

The phase-number term is anchored the same way `scripts/planning-parity.sh` anchors
phase numbers: `[Pp]hase 2` must be followed by end-of-line or a non-digit,
non-`.` character, so `Phase 2` does not match `Phase 21` and does not match
`Phase 2.1` (a future decimal insertion). `(^|/)02-` matches this phase's own
directory/file-name convention (`02-01-PLAN.md`, `02-GOV-SWEEP.md`, …) without
matching an unrelated `-02-` substring mid-path.

**Run twice, compared byte-for-byte:**

```
$ derive > run1.txt
$ derive > run2.txt
$ diff run1.txt run2.txt && echo "REPRODUCIBLE: byte-identical"
REPRODUCIBLE: byte-identical
```

**Row count:** 52.

**Deduplicated (E21):** 52 unique entries from 52 raw lines — `sort -u` count equals
raw count; no path appears twice even though several files (this phase's own
PLAN/SUMMARY pairs, REQUIREMENTS.md) match on more than one ground (a requirement
ID **and** a phase-number mention).

**Non-empty (E22):** 52 > 0, and `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`
and `.planning/PROJECT.md` are all present — a derivation that returned 0 rows here
would be a defect in the derivation, not a clean sweep, because these three files are
known by construction to name the phase.

**Sorted (E23):** `derive`'s output is piped through `sort -u`, and the run above is
byte-identical to its own sorted form.

**The derived list (52 artifacts):**

```
.planning/PROJECT.md
.planning/REQUIREMENTS.md
.planning/ROADMAP.md
.planning/STATE.md
.planning/codebase/ARCHITECTURE.md
.planning/codebase/CONCERNS.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-PLAN.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-01-SUMMARY.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-02-PLAN.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-PLAN.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-03-SUMMARY.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-PLAN-MANIFEST.json
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-REVIEW-ADJUDICATION.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-SECURITY.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-UAT.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/01-VERIFICATION.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-codex.err
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-codex.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-plan-00.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-plan-01.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-plan-02.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-prompt.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T173329/gsd-review-requirements.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T184435/gsd-review-codex.err
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T184435/gsd-review-plan-00.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T184435/gsd-review-plan-01.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T184435/gsd-review-plan-02.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T184435/gsd-review-prompt.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T184435/gsd-review-requirements.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T191655/gsd-review-codex.err
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T191655/gsd-review-plan-00.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T191655/gsd-review-plan-01.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T191655/gsd-review-plan-02.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T191655/gsd-review-prompt.md
.planning/phases/01-escalation-mechanism-and-fixture-invariant/review-runs/20260831T191655/gsd-review-requirements.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-01-PLAN.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-01-SUMMARY.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-02-PLAN.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-02-SUMMARY.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-03-PLAN.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-03-SUMMARY.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-04-PLAN.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-04-SUMMARY.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-CONTEXT.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-DISCUSSION-LOG.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-FINDING-01-state-authority.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-FINDING-02-gitignored-instrumentation.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-GOV-SWEEP-RUNBOOK.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-PATTERNS.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-SECURITY.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-UAT.md
.planning/phases/02-enforcement-and-a-single-gate-definition/02-VERIFICATION.md
```

(`02-GOV-SWEEP.md` itself does not appear — it did not exist at the moment the
derivation ran, inside the same task that creates it. It will appear on any run of
the derivation from this commit onward, which is expected and not itself a defect.)

### The derivation's bound

Coverage is artifacts that explicitly name the phase or a requirement ID. **Anything
else is out of scope by design, not assumed covered.** Two concrete, known edges:

1. **`.planning/config.json` is untracked** (recorded in `STATE.md` §Blockers/Concerns:
   *"`.planning/config.json` is untracked. `cmdConfigNewProject` refuses to overwrite
   an existing config, so it is protected from regeneration only while the file stays
   in place."*). `git ls-files '.planning/*'` cannot see an untracked file by
   construction, so a tracked-files derivation is blind to it regardless of its
   content. Confirmed at this sweep: `git ls-files --error-unmatch .planning/config.json`
   fails (not tracked).
2. **A `.planning/` document that discusses this phase's requirements purely in
   prose, naming no ID and no phase number, escapes the same way `PROJECT.md` did
   before 02-04 tagged it** (D-15's own measurement: 0 requirement IDs, 0 phase-number
   mentions in `PROJECT.md` before that plan). Tagging closes the instance that was
   found; it does not close the class. Any future planning document written the same
   way is invisible to this derivation until it is tagged.
3. **A live-demonstrated third edge, already on record in REQUIREMENTS.md's GOV-01
   text:** `.github/workflows/ci.yml`'s `go` job name went stale (CI-02 collapsed the
   job onto `make gate`, and the job's `name:` line — "vet + test + fmt" — stopped
   being true) in a file this derivation **does not cover at all**, because `ci.yml`
   is not under `.planning/` and, at the time, named neither the phase number nor a
   requirement ID. Found by a human running UAT test 12, not by this mechanism.
   Fixed at `d256c4c`, not re-litigated here (the coverage bound explicitly excludes
   `ci.yml`, unchanged by this sweep by design).

None of these are defects in the derivation as specified — they are the bound GOV-01's
own text requires this sweep to state rather than merely observe.

<!-- evidence-table-placeholder -->

<!-- rearm-log-placeholder -->
