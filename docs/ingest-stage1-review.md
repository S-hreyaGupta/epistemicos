# Ingest Stage 1: where the spec and the code actually stand

Reviewed 19 September 2026, at Alex Zamurko's request, against what is in this
repository rather than against what was said about it.

**Summary: the specification is ready to freeze. The implementation has not
started.** Those are both fine as facts. They are not fine as one sentence,
and the exchange that ended "freeze ready!" was about the document.

## 1. The specification is not in the repository

`INGEST_STAGE1_v8.md` exists as a Slack attachment and nowhere else.

```text
find . -iname "*ingest*"
  internal/core/ports/ingest.go
  internal/core/services/ingest/ingest.go
```

No spec. §0.1 of the governing protocol says in terms that a Slack copy is not
authoritative, and this is the third artifact to land in that position:
`PILOT_RUNBOOK` was never committed, which is why the pilot's own criteria
could not be found when the verdict was due; rc3 is frozen at `ddc6f1f8…` and
exists only as an attachment.

A document cannot be frozen where it cannot be hashed. Committing it is the
first step, not a tidy-up afterwards.

## 2. The specification is not implemented

Not partially. The vocabulary the spec is written in does not appear in the
codebase at all:

```text
UploadIntent          0 occurrences in any .go or .sql
parent_paper_id       0
ParentID              0
legacyMD5             0
manuscript_id         0
UploadSource          0
```

And the three things the spec changes are all still in their pre-spec state:

```text
§6   delete GetByHash        still called, ingest.go:99
§7.5 drop papers_hash_unique still present, 0001_initial.up.sql:13
§5   legacyMD5 + SHA-256     the PDF is hashed with MD5 only; SHA-256 is
                             computed for the markdown and nothing else
§3   UploadIntent.Validate() fromReader opens with os.MkdirAll; there is no
                             validate call at the service boundary
```

The latest migration is `0012_run_rejection`. Nothing Stage-1-shaped exists.

This is not a criticism of the spec work, which is thorough. It is that
"freeze ready" was said about a document, and the question asked afterwards
was about the system.

### Where the confusion is easy

Reading the thread back, the replies describe the *document* in the vocabulary
of the *code*:

> "Added at the top of `fromReader`, before the temp file is written."

That is true of the spec text. `fromReader` in `ingest.go` has no such call.
Both readings are natural and they are not the same claim.

## 3. Dedupe fails open on a database error

Found while reading, not in the spec, and it gets worse when the spec lands.

```go
// ingest.go:99
if existing, err := s.store.GetByHash(ctx, hash); err == nil {
    _ = os.Remove(tmpPath)
    return existing, nil
}
```

The store does distinguish the two cases properly:

```go
// postgres.go:139
if errors.Is(err, pgx.ErrNoRows) {
    return nil, ports.ErrNotFound
}
return nil, fmt.Errorf("scan paper: %w", err)
```

The caller discards that distinction. `err != nil` means "no duplicate, carry
on" whether the row was absent or the database was unreachable. So a transient
database failure during the dedupe lookup silently becomes "this is a new
paper."

Right now `papers_hash_unique` catches the consequence: the subsequent `Save`
violates the constraint and the request fails loudly. **§7.5 drops that
constraint.** So implementing the spec removes the net that currently masks
this, and the failure mode changes from a noisy insert error to a duplicate
row.

The repair is three lines — treat `ports.ErrNotFound` as "proceed" and
anything else as fatal — and it should land before §7.5, not after.

## 4. The ingest path has no tests

```text
internal/core/services/ingest          0 test files
internal/adapters/primary/http         0 test files
internal/adapters/secondary/pdfdownloader  0 test files
```

`go test ./...` reports `[no test files]` for all three, and has since the
repository was created. The store and the hasher are covered; the service that
orchestrates them, the HTTP surface that calls it, and the downloader are not.

This is the same shape as `cmd/epistemicos-api`, which got its first test file
on 18 September after a claim in the closure record turned out to rest on a
control one layer below what it asserted. The ingest service is the more
exposed of the two: it writes files, moves them, calls an external API, and
mutates rows, and none of that is exercised anywhere.

## What this review does not say

That the ingest code is wrong. It works — the API ran against the corrected
database on 18 September and the fourteen-paper corpus came through this path.
Stage 1 is a planned change to something functioning, not a rescue.

Nor that the spec is wrong. The four points Alex raised on 26 August were all
real and all closed in the document.

What it says is narrower: **the document is ready and the work is not started,
and one defect in the current code becomes more serious the moment the spec
lands.**

## Suggested order

```text
1  commit INGEST_STAGE1_v8.md to specs/ and record its hash
2  repair the dedupe error handling, before §7.5 removes the constraint
   that currently masks it
3  give the ingest service its first tests, since Stage 1 will rewrite it
   and there is nothing to regress against
4  then implement Stage 1
```

Step 3 is the one worth arguing for. Stage 1 changes hashing, dedupe, the
schema and the service boundary at once, and right now there is no test that
would notice if any of it broke.
