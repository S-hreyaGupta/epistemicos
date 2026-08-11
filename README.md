# EpistemicOS

Takes a research paper PDF and produces markdown.

```
PDF  →  download  →  hash  →  Mathpix  →  markdown + SHA-256  →  Postgres
```

An HTTP API and a CLI, backed by Postgres. Thirty-nine files, four direct
dependencies.

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
in `internal/core` imports from `internal/adapters`.

Dependencies are pgx, golang-migrate, uuid and godotenv. No web framework, no
ORM, no DI container.

---

## The contract worth knowing

`ingest.Service` computes the SHA-256 of the markdown and hands it to
`PaperStore.UpdateMarkdown` in the same call that writes the markdown itself.
One statement, so the two cannot diverge.

Anything downstream that indexes into this text — by byte offset or otherwise —
can check what it holds against `papers.markdown_hash` before trusting it.

That guarantee is why `export-markdown` is a subcommand rather than a shell
pipeline: piping the API response through `jq` into a redirect appends a newline
and can inject CRLF, either of which silently breaks it.

**Mathpix output is not byte-reproducible.** Converting the same PDF twice
returns files of identical length but differing content. Re-converting a paper
therefore invalidates any offsets recorded against the previous conversion, and
the hash is what catches that.

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

`export-markdown` writes the stored markdown byte-exactly — no trimming, no
line-ending translation, no trailing newline — and prints its hash.

Mathpix credentials are required to convert. Without them the service still
starts and serves reads, but ingest fails at the conversion step and
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
inbound. Logs are `log/slog` JSON — grep by `correlation_id`.

Ingest dedupes on the content hash of the source PDF, so submitting the same
paper twice returns the existing record without re-converting.

---

## Database

One table beyond migration bookkeeping: `papers`.

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
