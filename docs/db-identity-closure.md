# Database identity: closure record

The configured database and the connected database agree, and the path that
would notice if they stopped agreeing has been exercised.

Recorded at Alex Zamurko's request, 18 September 2026: *retain the successful
run's commit, resolved database/user identity, and the relevant config hash, so
this is reproducible evidence rather than only an operational note.*

## What was wrong

`POSTGRES_DB` and `POSTGRES_USER` apply only when a Postgres volume is first
initialised. The environment-variable prefix was renamed from `PAPERLY_` to
`EPISTEMIC_OS_` on 24 August 2026 and the configured database name changed with
it, but the volume had already been initialised. For three weeks the
configuration said `epistemicos` and the server was `paperly`.

Nothing detected it, and the reason is worth stating separately from the fault:
the API had never been run under Compose, so the one path on which the two
values would have met was never taken. The defect was not that a check failed.
It was that the code carrying the two values into the same place had not run.

## The evidence

```text
commit                  15e7f4ad3546a480d8a7f163438a6738e2d0d5a7
                        "Database-identity preflight, and the .env loader test"

configured, tracked     docker-compose.yml
                        sha256 72bc14848c87ed0cfedcdffcce0c35a99c4f3717a0b1d1fc0536ef04d8ca18d2
                          POSTGRES_DB:   epistemicos
                          POSTGRES_USER: epistemicos
                          EPISTEMIC_OS_DB_URL:
                            postgres://epistemicos:…@postgres:5432/epistemicos?sslmode=disable

configured, local       .env, which is gitignored and holds credentials

                        The non-secret resolved identity, in plaintext,
                        because it is the part that carries meaning and it
                        survives a password change:
                          database  epistemicos
                          user      epistemicos
                          host      localhost
                          port      5432
                          sslmode   disable

                        And the sha256 of the whole DB_URL line, which
                        identifies the exact configuration that was used:
                        f071c2cc0e18dd2767067a2bb1b4ee346cf0fbbf5fb7cd500c40c23393b17fe1

                        Both, for different jobs. Alex Zamurko, 18 September:
                        the full-line hash establishes which exact
                        secret-bearing configuration ran, but it is not a
                        durable semantic identifier, because rotating the
                        password changes the hash while the identity it is
                        standing in for has not changed at all. A reader six
                        months from now wants to know which database this was,
                        and a hash that moved for an unrelated reason cannot
                        tell them.

resolved by the server  SELECT current_database(), current_user
                        epistemicos / epistemicos
                        PostgreSQL 16.14 on x86_64-pc-linux-musl,
                        compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit

corpus, six counts      papers 14, with markdown 14, segmentation_runs 17,
                        section_nodes 725, review_tasks 349,
                        review_decisions 0
                        equal to the Phase 0B counts taken before the rename

                        Six equal counts, and nothing more than that. This
                        block was headed "corpus, unchanged" until 18
                        September, which claimed more than six integers can
                        carry: equal row counts are consistent with altered
                        content and would not distinguish it.
```

## What was done

The rename was made in Postgres rather than by repointing the configuration,
because five places in tracked configuration plus CI already said `epistemicos`
and `paperly` had been deliberately retired on 24 August.

```sql
ALTER DATABASE paperly RENAME TO epistemicos;
ALTER ROLE paperly RENAME TO epistemicos;   -- via a temporary superuser:
                                            -- a session cannot rename itself
ALTER ROLE epistemicos WITH PASSWORD '…';
```

A rename preserves the role and database objects, so ownership followed without
reassignment. The six counts above were taken after and are equal to the
counts taken before, which is what six counts can say.

## What stops it recurring

`preflight.CheckDatabaseIdentity` compares the identity the connection string
names against what the server answers to `preflight.IdentityQuery`. It runs at
API startup and is **fatal**, unlike the Mathpix probe, which warns.

The asymmetry is deliberate. A deployment without Mathpix credentials can serve
reads honestly and say so in its capabilities. A deployment writing while
connected to a database other than the one it reports produces artifacts,
counts and hashes attributed to the wrong environment, and everything derived
from them inherits that attribution with no later check able to recover it.

Thirteen controls cover `CheckDatabaseIdentity` itself, including the mismatch
as it actually occurred and the case where the server answers nothing — a check
that passes when it did not run is worse than no check, because green is read
as evidence.

They cover the function. They do not cover the sentence above it. Whether the
API is fatal on a mismatch is decided in `cmd/epistemicos-api/main.go`, a
package with no test file, so "and is **fatal**" is a description of the source
rather than something a control holds down. See the closing section.

## The closure itself

`epistemicos-api` was started against this database at commit `15e7f4a` and
reported `listening on :9082`, which means it passed the preflight.

That is the first time this API has been run against this database. The check
and the first execution of the path it lives on arrived within a minute of each
other, and neither would have been worth much alone: a check nobody runs is not
a check, and a path nobody takes is where a mismatch survives three weeks.

## What this record establishes, and what it does not

Rewritten 18 September after Alex Zamurko read the first version, which claimed
two things it could not support.

It establishes:

```text
configuration and server named the same database and user at that run,
  resolved by the server itself and not inferred from configuration

six recorded counts are equal to the Phase 0B counts taken before the rename

the identity check runs on the startup path, because the API started and
  reported listening, which it does only after the check returns
```

It does not establish:

**That the corpus is unchanged.** Six equal counts do not carry that. Rows can
be rewritten without the count moving, and nothing here would see it. The
stronger claim is available and is not made here: `PROVENANCE-GAP.md` records
two of the fourteen papers as byte-identical between `data/md_full/` and
`papers.markdown`, by sha256, which is real evidence for two papers and not for
the corpus. Extending it to fourteen is a command nobody has run.

**That a future disagreement will stop the API.** This was asserted, and the
evidence for it is one layer below the claim. `TestCheckDatabaseIdentity`
covers six cases including the mismatch as it occurred, and what it shows is
that `preflight.CheckDatabaseIdentity` *returns* not-OK. The decision to treat
that as fatal lives in `main.go`, in package `main`, which has no test file at
all — `go test ./...` reports `cmd/epistemicos-api [no test files]`, and has
on every run.

So the function is covered and the wiring is not. A refactor that made the
preflight a warning, or dropped the call, would pass every control in this
repository. That is the same shape as the defect this document is about: the
check existed and the path carrying it had never been exercised.

Alex Zamurko's wording on 18 September kept the conditional deliberately, that
a disagreement causes a fatal refusal *if the negative control demonstrates
this*, and no control in this repository currently demonstrates it.

It also says nothing about whether `epistemicos` is the right name, which was
decided on 24 August and is not revisited here.
