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
                        postgres://epistemicos:REDACTED@localhost:5432/epistemicos?sslmode=disable
                        sha256 of that line, so the exact configuration is
                        identifiable without being reproduced here:
                        f071c2cc0e18dd2767067a2bb1b4ee346cf0fbbf5fb7cd500c40c23393b17fe1

resolved by the server  SELECT current_database(), current_user
                        epistemicos / epistemicos
                        PostgreSQL 16.14 on x86_64-pc-linux-musl,
                        compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit

corpus, unchanged       papers 14, with markdown 14, segmentation_runs 17,
                        section_nodes 725, review_tasks 349,
                        review_decisions 0
                        identical to the Phase 0B counts taken before the
                        rename
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
reassignment. The six counts above were taken after and are unchanged.

## What stops it recurring

`preflight.CheckDatabaseIdentity` compares the identity the connection string
names against what the server answers to `preflight.IdentityQuery`. It runs at
API startup and is **fatal**, unlike the Mathpix probe, which warns.

The asymmetry is deliberate. A deployment without Mathpix credentials can serve
reads honestly and say so in its capabilities. A deployment writing while
connected to a database other than the one it reports produces artifacts,
counts and hashes attributed to the wrong environment, and everything derived
from them inherits that attribution with no later check able to recover it.

Thirteen controls cover it, including the mismatch as it actually occurred, and
including the case where the server answers nothing — a check that passes when
it did not run is worse than no check, because green is read as evidence.

## The closure itself

`epistemicos-api` was started against this database at commit `15e7f4a` and
reported `listening on :9082`, which means it passed the preflight.

That is the first time this API has been run against this database. The check
and the first execution of the path it lives on arrived within a minute of each
other, and neither would have been worth much alone: a check nobody runs is not
a check, and a path nobody takes is where a mismatch survives three weeks.

## What this record does not establish

That the rename was correct in any sense beyond identity. It establishes that
configuration and server now agree, that the corpus survived it unchanged, and
that a future disagreement will stop the API rather than be discovered in a
report weeks later.

It says nothing about whether `epistemicos` is the right name, which is a
decision made on 24 August and not revisited here.
