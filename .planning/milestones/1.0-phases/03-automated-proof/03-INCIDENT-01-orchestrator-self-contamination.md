---
type: incident
phase: 03-automated-proof
raised_by: execute-phase orchestrator
raised_at: 2026-09-03T12:05:00Z
severity: measurement-invalidating
status: declared
affects: [03-01 verification re-run, DefaultTimeout cold-path rationale]
---

# INCIDENT-01: Orchestrator self-contamination of a timing measurement

## What happened

While verifying 03-01's PROOF-01 claim independently, the orchestrator started a
second heavy workload **on the same machine, against the same Postgres, while the
first verification run was still in flight**.

Timeline (UTC):

| Time | Event |
|---|---|
| 11:44:06 | Background verification starts: `go test ./internal/platform/gateproof/ -run TestPROOF01 -count=1 -v -timeout 30m` |
| 11:44:16 | That run's test binary spawns `git archive --format=tar HEAD` inside `materializeTree` |
| ~11:48 | Orchestrator starts a **competing** `go test ./... -count=1` at the repo root |
| ~11:58 | Competing run killed at the 9m20s tool timeout |
| 12:04 | Contamination declared; no timing number reported from the affected run |

The competing command was intended to measure "how long does the full suite take at
root". It was a bad experiment for two independent reasons:

1. **It was concurrent with the run it would be compared against.** Two full Go test
   suites and two `migrate` invocations contended for CPU and for a single Postgres
   instance.
2. **It was not the measurement it claimed to be.** At the repo root the `gateproof`
   package is *not* nested, so `go test ./...` there executes the PROOF tests, each of
   which spawns its own nested `make gate`. The command silently included the very
   workload whose cost it was trying to isolate.

## Consequence

Roughly 11 of the affected run's 16 observed minutes overlapped the competing run.
**Its wall time is void for timing purposes** and no duration from it may be used to
decide between the cold-build-cache and stale-documentation hypotheses for
`DefaultTimeout`'s "85s / 2.8x margin" rationale. A clean, uncontended re-run is
required before that question can be answered.

## Declaration

The orchestrator declared this contamination itself, unprompted, in the turn
immediately following the bad command, and refused to report a duration from the
affected run. It is recorded here rather than only in conversation because a verbal
declaration does not survive a context reset, and the void measurement would
otherwise look like a usable data point to the next reader.

A second, smaller error was made and corrected in the same investigation: an initial
`grep -cE "compile|cd \$WORK"` conflated `cd $WORK` bookkeeping lines with real
`compile.exe` invocations, producing one wrong count that was retracted and re-measured
against raw `go build -x` output before any conclusion was drawn from it.

## What this incident does NOT invalidate

These were established by read-only inspection or by uncontended measurement and stand
independently of the contamination:

- `GOCACHE` is user-level (`C:\Users\gupta\AppData\Local\go-build`) and is shared by a
  `materializeTree` copy; `GOFLAGS` is empty; there is no `-trimpath` in the build.
- Because there is no `-trimpath`, the build action ID is **path-dependent**: a copy at
  a new path recompiles the main module's packages even though content is byte-identical
  and the cache is shared. Confirmed against raw `go build -x` output, whose `compile.exe`
  command line carries the absolute copy path.
- That miss is **permanent but cheap**: `materializeTree` uses a new temp path every run
  so it never warms, but a fresh-path `go build ./...` is 27 compiles in ~4s versus ~2s
  warm. It cannot account for minute-scale runtime.
- The `DefaultTimeout` comment's clause "the children inherit that cache" is therefore
  **false for the copy-based child** (`defeated_tree_control`) and true for the
  same-path child (`intact_tree`) — an error of roughly 2 seconds, not minutes.
- `DefaultTimeout = 4 * time.Minute`.

## Open, being investigated separately

The affected run was found deadlocked, not slow: over 19m35s, `git.exe` had consumed
0.203s CPU and the test binary 0.297s, both unchanged across a 10s re-sample. The
process tree showed no `make.exe` at any point — the run never reached a nested
`make gate`, and has been blocked inside `materializeTree` on `git archive` since 7
seconds after start. That is a defect in its own right and is tracked separately; it is
not a product of this contamination, since it began before the competing run started.

See also: [[03-INCIDENT-02]] if the `materializeTree` deadlock is confirmed.
