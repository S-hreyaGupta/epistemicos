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
                        content and would not distinguish it. The content
                        claim is below, and is a different measurement.

corpus, content         All fourteen papers' markdown, md5 as the server
                        computes it, against the bytes in data/md_full/ —
                        exported 29 August 18:55, before the rename:

                        17bef7c6  699d9f105a098b23e7dff4517194c601
                        2af68a7f  5690b03127e5bf99531599e09b9f68db
                        43338825  52b01e6b72d93eda928e47d58a07b6bb
                        4918fd7d  852e2e407b37912e7bba7d3963faeaaf
                        50408397  e8c3776f40e15cfd89ff6e8ae80212f1
                        5da73cf4  26601fae605c5b55673b8ce02e96aa0a
                        849f8fc6  f55bc30bf6752750285cbc89f2aac875
                        ad1e3ff9  818511aaf25ecf56194712bb3da3f46e
                        bf2fdc4a  5608402e9225d9cd8ec1e398a9c662f9
                        c1d56945  e771b52372fa2cb3fb059755c8e23c00
                        c22df19f  bfe20256c82a1412ff686732831ebe2a
                        e1b418a4  df72154144d46138d0b849a4f67d07cc
                        ea07e5f5  b454757c677224f9ebeed261503094c6
                        ed6a890a  120c415a8aa12248ea9b34e6f75bfd8d

                        14 of 14 identical. The hashes are written out here
                        because data/ is gitignored, so the evidence has to
                        live in the record rather than beside it.
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

all fourteen papers' markdown is byte-identical to data/md_full/, which was
  written on 29 August, before the rename — so the corpus content did not
  change across it, and not merely the number of rows

the identity check runs on the startup path, because the API started and
  reported listening, which it does only after the check returns
```

The corpus line was added on 18 September and is the reason the earlier
"corpus, unchanged" wording is not simply deleted but replaced. Six counts
could not support it; fourteen hashes can, and the two are different
measurements that were briefly conflated.

Two qualifications on it. The comparison is md5, which is sound against
accidental change and not against deliberate substitution — `PROVENANCE-GAP.md`
additionally carries sha256 for two of the fourteen. And it establishes that
the database agrees with `data/md_full/`, so it inherits whatever that export
was; it is a statement about drift since 29 August, not about the corpus being
correct.

It does not establish:

**That `main()` calls `os.Exit` on a disagreement.** Narrower than it was, and
the remaining gap is now one `if` statement.

As first written this record asserted that a future disagreement would stop the
API, and the evidence was a layer below the claim: `TestCheckDatabaseIdentity`
showed `preflight.CheckDatabaseIdentity` *returning* not-OK, while the decision
to treat that as fatal sat inline in `main()`, in a package with no test file at
all. `go test ./...` reported `cmd/epistemicos-api [no test files]` on every run
since the repository was created. A refactor that made the preflight a warning,
or dropped the call, would have passed everything here.

Closed on 18 September by extracting `ensureDatabaseIdentity` and giving
package `main` its first controls — `cmd/epistemicos-api/main_test.go`, seven
of them, including the `paperly` mismatch as it actually occurred, a server
answering blank, and a failing query. What they hold down is the decision:
given what the server said, startup stops.

What they still do not reach is the three lines that call `fatalf` on that
error, which would mean running a process and asserting an exit code. A
mismatch that still connects is awkward to construct, because the connection
string determines which database you reach, so in ordinary operation the two
agree by construction; the fault this guards against arrives through a DSN form
where the name is not what it appears, or through a proxy.

Alex Zamurko's wording on 18 September kept the conditional deliberately, that
a disagreement causes a fatal refusal *if the negative control demonstrates
this*. The refusal is now demonstrated. The exit is not, and that residue is
named here rather than left for someone to find the way this gap was found.

It also says nothing about whether `epistemicos` is the right name, which was
decided on 24 August and is not revisited here.
