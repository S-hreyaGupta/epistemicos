# EpistemicOS

Takes a research paper PDF and produces markdown.

```
PDF  →  download  →  hash  →  Mathpix  →  markdown + SHA-256  →  Postgres
```

An HTTP API and a CLI, backed by Postgres. Thirty-nine files, four direct
dependencies.

A description of every file is in [`docs/FILES.md`](docs/FILES.md).

---

## How it works

The whole pipeline lives in `internal/core/services/ingest/ingest.go`. Everything
else is plumbing around it. Nine steps, in order.

### 1 · A PDF arrives

Two ways in, and they converge immediately.

**By URL** — `POST /api/v1/papers` with `{"url": "..."}`, or
`epistemicos-cli ingest <url>`. `pdfdownloader` fetches it and returns a stream.

**By upload** — `POST /api/v1/papers` as `multipart/form-data` with a `file`
field.

Both land in the same private method, so there is one conversion path rather
than two.

### 2 · Staged to disk

The stream is written to a temporary file under `PAPERLY_PDF_VOLUME`, named
`tmp-<uuid>.pdf`.

It goes to disk rather than staying in memory because both of the next two steps
need a file path: hashing reads it, and Mathpix uploads it.

### 3 · Hashed

`hasher` computes an MD5 over the file. This is the **content** hash — it
identifies the PDF itself, and it is the dedupe key.

MD5 is deliberate. This is not a security boundary; it is a lookup key, and
collisions between two real research papers are not a practical concern.

### 4 · Deduped

`GetByHash` asks whether this exact PDF has been seen before.

**If yes** — the temporary file is deleted and the existing record returned. No
Mathpix call, no cost, no duplicate row. Submitting the same paper twice is
free.

**If no** — carry on.

The unique constraint on `papers.hash` in the database backs this up, so two
simultaneous ingests of the same paper cannot both create a row.

### 5 · A pending row is written

Before any slow work begins, a row is saved with `status = pending`.

That ordering matters: if conversion fails or the process dies, there is a
visible record of the attempt with an error message, rather than silence.

### 6 · The PDF is moved to its permanent home

Renamed from `tmp-<uuid>.pdf` to `<paper-id>.pdf`. From here the file is
addressable by the paper's identity rather than by an accident of upload order.

### 7 · Mathpix converts it

Status moves to `processing`, then `mathpix.Client.Process` runs three phases,
because the Mathpix API is asynchronous:

**Upload** — the PDF is POSTed as multipart with
`options_json: {"conversion_formats":{"md":true}}`. Mathpix returns a `pdf_id`.

**Poll** — status is checked on an interval until it reports `completed`. An
`error` status fails the run with the message Mathpix gave.

**Fetch** — the finished markdown is retrieved.

A title is extracted best-effort from the first heading in the output. Many
papers yield nothing here, which is expected and not an error.

Requesting the `md` format specifically means maths comes back
dollar-delimited (`$$ … $$`) rather than in LaTeX bracket form.

### 8 · The markdown is hashed

`sha256(markdown)`, hex-encoded.

Note this is a **different hash from step 3**, over different bytes, for a
different purpose. Step 3 identifies the source PDF. This one lets any consumer
prove the markdown it holds is the markdown that was stored.

### 9 · Both are written together

```go
store.UpdateMarkdown(ctx, id, title, markdown, markdownHash)
```

One call, one SQL statement. The markdown and its hash cannot diverge, because
there is no code path that writes one without the other.

Status becomes `ready`.

---

## Why the hash matters

**Mathpix output is not byte-reproducible.** Converting the same PDF twice
returns files of identical length but differing content — presumably an embedded
identifier of fixed width.

So re-converting a paper invalidates anything recorded against the previous
conversion. Byte offsets into the old markdown will still be valid *numbers*;
they will simply point at the wrong text, silently.

`papers.markdown_hash` is what catches that. Any consumer holding offsets, or a
copy of the text, checks the hash before trusting what it has.

The same guarantee is why `export-markdown` is a subcommand rather than a shell
pipeline: piping the API response through `jq` into a redirect appends a newline
and can inject CRLF, either of which breaks the property the hash exists to
protect.

---

## Layout

```
cmd/
  epistemicos-api/         HTTP server — ingest, list, fetch
  epistemicos-cli/         migrate, ingest, list, export-markdown

internal/core/
  domain/paper/            Paper aggregate and its lifecycle
  ports/                   PDFDownloader, MarkdownProcessor, Hasher, PaperStore
  services/ingest/         The use case: PDF in, markdown + hash out

internal/adapters/
  primary/http/            REST surface
  secondary/pdfdownloader/ URL → PDF
  secondary/mathpix/       PDF → markdown-with-LaTeX
  secondary/hasher/        Content addressing for dedupe
  secondary/store/         Postgres via pgx, migrations

internal/platform/         config, logging, metrics, security, preflight
```

Hexagonal: the core depends on interfaces, adapters implement them, and nothing
in `internal/core` imports from `internal/adapters`. That direction is what
keeps Mathpix swappable and the ingest logic testable without a network.

Dependencies are pgx, golang-migrate, uuid and godotenv. No web framework, no
ORM, no DI container.

---

## Quickstart

```bash
cp .env.example .env         # fill in MATHPIX_APP_ID and MATHPIX_APP_KEY
make up                      # start postgres
make migrate                 # apply migrations
make build                   # build both binaries
./bin/epistemicos-api        # serves on :9082
```

```bash
./bin/epistemicos-cli ingest <url>
./bin/epistemicos-cli list
./bin/epistemicos-cli export-markdown <paper-id> --out paper.md
```

Mathpix credentials are required to convert. Without them the service still
starts and serves reads, but ingest fails at step 7 and
`/api/v1/capabilities` reports `mathpix_enabled: false`.

---

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness |
| `GET` | `/api/v1/capabilities` | Whether Mathpix is wired |
| `POST` | `/api/v1/papers` | Ingest by URL (JSON) or upload (multipart) |
| `GET` | `/api/v1/papers` | List, reverse-chronological |
| `GET` | `/api/v1/papers/{id}` | Fetch one, with markdown and its hash |
| `GET` | `/metrics` | Prometheus text format |

Every request carries an `X-Correlation-ID`, minted server-side or accepted
inbound. Logs are `log/slog` JSON — grep by `correlation_id` to follow one
request end to end.

---

## Database

One table beyond migration bookkeeping: `papers`.

| Column | Holds |
|---|---|
| `id` | UUID, the paper's identity |
| `url` | Source URL, empty for direct uploads |
| `hash` | MD5 of the source PDF — unique, the dedupe key |
| `title` | Best-effort, extracted from the markdown |
| `status` | `pending` / `downloading` / `processing` / `ready` / `failed` |
| `error` | Populated when `status = failed` |
| `markdown` | The Mathpix output |
| `markdown_hash` | SHA-256 of that markdown |
| `created_at` / `updated_at` | Timestamps |

| Migration | Adds |
|---|---|
| `0001_initial` | `papers` |
| `0004_markdown_hash` | `papers.markdown_hash` |

Numbering starts at `0001` and jumps to `0004`. The gap is deliberate and those
numbers are not reused, so a database carrying earlier migration history stays
consistent.

**One defect worth knowing.** `markdown_hash` is `NOT NULL DEFAULT ''`. A
staleness check written as `a.Hash != b.Hash` therefore passes trivially when
both sides are empty — precisely the rows with no integrity guarantee. Treat the
empty string as *absent*, never as a match.

---

## The gate

```bash
make gate     # go vet + gofmt + go build + go test
```

CI runs the same four, and `gofmt` is enforced rather than advisory.

`.gitattributes` pins `*.go`, `go.mod` and `go.sum` to LF. Without the first the
format gate fires on `core.autocrlf` noise instead of real drift; without the
others `go.mod` and `go.sum` show permanently modified, which is where a real
dependency change would hide.

---

## Configuration

Copy `.env.example` to `.env`.

| Variable | Required | Default |
|---|---|---|
| `PAPERLY_DB_URL` | yes | — |
| `MATHPIX_APP_ID` / `MATHPIX_APP_KEY` | for conversion | — |
| `PAPERLY_LISTEN_ADDR` | no | `:9082` |
| `PAPERLY_PDF_VOLUME` | no | `./data/pdfs` |
| `PAPERLY_CORS_ALLOWED_ORIGINS` | no | `*` |
| `PAPERLY_RATE_LIMIT_RPM` | no | `60` |
| `PAPERLY_RATE_LIMIT_BURST` | no | `20` |

The `PAPERLY_` prefix is legacy naming retained so existing deployments and
`.env` files keep working. Renaming it is a breaking change for anything already
running.

`.env` is gitignored and must stay that way — it holds live credentials.
