# File reference

Every tracked file, what it does, and why it exists. Thirty-nine files.

---

## Entry points

### `cmd/epistemicos-api/main.go` — 123 lines

The HTTP server. Loads config, runs migrations, opens the Postgres pool, wires
the four adapters into `ingest.Service`, probes Mathpix credentials, assembles
the middleware chain, and serves until SIGINT or SIGTERM.

The middleware order is deliberate, outermost first: CORS → security headers →
rate limit → correlation ID → routes.

### `cmd/epistemicos-cli/main.go` — 139 lines

The command-line counterpart. Four subcommands:

| Command | Does |
|---|---|
| `migrate up` | Applies pending database migrations |
| `ingest <url>` | Downloads, converts and stores one paper |
| `list` | Prints every stored paper, newest first |
| `export-markdown` | See below |

Shares no code with the API beyond the service layer — both construct the same
`ingest.Service` from the same adapters.

### `cmd/epistemicos-cli/export.go` — 116 lines

`export-markdown <paper-id> --out <path>`. Reads a paper's stored markdown and
writes it to a file **byte-exactly** — no trimming, no line-ending translation,
no trailing newline — then prints the byte count and the stored hash.

It exists as a subcommand rather than a shell pipeline because the obvious
alternative (curl the API, pipe through `jq`, redirect to a file) silently
mutates the bytes: `jq` appends a newline and Windows redirection can inject
CRLF. Either breaks the guarantee that the file's SHA-256 equals
`papers.markdown_hash`.

---

## The core — business logic, no external dependencies

### `internal/core/domain/paper/paper.go` — 46 lines

The `Paper` type and its lifecycle. Three identifiers worth distinguishing:

| Field | Is |
|---|---|
| `ID` | A UUID, assigned on ingest |
| `Hash` | MD5 of the **source PDF** — the dedupe key |
| `MarkdownHash` | SHA-256 of the **converted markdown** — the integrity check |

`Status` moves `pending` → `downloading` → `processing` → `ready`, or to
`failed` with a reason in `Error`.

### `internal/core/ports/ingest.go` — 38 lines

Three interfaces the core needs from the outside world:

- **`PDFDownloader`** — a URL becomes a stream of bytes
- **`MarkdownProcessor`** — a PDF file path becomes `(title, markdown)`
- **`Hasher`** — bytes become a content hash

Naming them as interfaces is what lets the core stay testable and keeps Mathpix
swappable.

### `internal/core/ports/store.go` — 40 lines

`PaperStore`: `Save`, `GetByID`, `GetByHash`, `List`, `UpdateStatus`,
`UpdateMarkdown`.

`UpdateMarkdown` takes the markdown *and* its hash together, in one call. That
signature is the reason the two can never drift apart.

### `internal/core/services/ingest/ingest.go` — 166 lines

**The heart of the system.** Everything else is plumbing around this file. Full
walkthrough in the README; in short it stages the PDF, hashes it, checks for a
duplicate, saves a `pending` row, converts through Mathpix, computes the
markdown hash, and stores both in a single write.

---

## Adapters — the outside world

### `internal/adapters/primary/http/server.go` — 70 lines

Route table and dependency wiring. Every endpoint is registered in one function,
so the API surface is greppable in one place.

### `internal/adapters/primary/http/handlers.go` — 137 lines

The six handlers. `handleCreatePaper` branches on content type: JSON means
ingest-by-URL, multipart means a direct file upload.

### `internal/adapters/primary/http/dto.go` — 56 lines

Request and response shapes, and the mapping from `paper.Paper` to JSON.
Markdown is omitted from list responses to keep them small, and included on the
detail endpoint along with its hash.

### `internal/adapters/secondary/pdfdownloader/downloader.go` — 53 lines

Fetches a URL and returns a `ReadCloser`. Returns a stream rather than writing
to disk — the ingest service owns file lifecycle, so it decides where bytes
land.

### `internal/adapters/secondary/mathpix/client.go` — 226 lines

**The conversion.** Three-phase, because Mathpix is asynchronous:

1. **Upload** — POST the PDF as multipart, with
   `options_json: {"conversion_formats":{"md":true}}`. Returns a `pdf_id`.
2. **Poll** — check status on an interval until it reports `completed`, or
   fail on `error`.
3. **Fetch** — retrieve the finished markdown.

Also extracts a best-effort title from the first heading in the output.

The `md` conversion format matters: it produces dollar-delimited maths (`$$`)
rather than LaTeX bracket delimiters.

### `internal/adapters/secondary/hasher/md5.go` — 42 lines

MD5 over the source PDF, used purely as a dedupe key. Not a security boundary,
which is why MD5 is adequate here.

### `internal/adapters/secondary/store/postgres.go` — 145 lines

`PaperStore` implemented on pgx. `Save` upserts on `id`; the unique constraint
on `hash` is what makes dedupe reliable even under concurrent ingests.

### `internal/adapters/secondary/store/migrate.go` — 50 lines

Runs migrations at startup via golang-migrate. The SQL files are embedded into
the binary with `go:embed`, so deployment is one artefact with no external
schema files to ship.

### `internal/adapters/secondary/store/migrations/`

| File | Does |
|---|---|
| `0001_initial.up.sql` | Creates `papers` — id, url, hash, title, status, error, markdown, timestamps, unique constraint on hash |
| `0001_initial.down.sql` | Drops it |
| `0004_markdown_hash.up.sql` | Adds `markdown_hash`, backfills existing rows |
| `0004_markdown_hash.down.sql` | Drops the column |

Numbering jumps from `0001` to `0004`. The gap is deliberate and those numbers
are not reused, so a database carrying earlier migration history stays
consistent.

---

## Platform — cross-cutting concerns

### `internal/platform/config/config.go` — 90 lines

Reads seven environment variables, applies defaults, and refuses to start
without `PAPERLY_DB_URL`. Every field backs something the system actually does.

### `internal/platform/logging/logging.go` — 75 lines

Structured JSON logging via `log/slog`, plus middleware that mints or accepts an
`X-Correlation-ID` per request. Grep by `correlation_id` to follow one request
through the logs.

### `internal/platform/metrics/metrics.go` — 328 lines

A small hand-rolled Prometheus registry — counters, gauges, histograms — served
at `/metrics`. Hand-rolled to avoid pulling in the full Prometheus client for
three primitives.

### `internal/platform/security/security.go` — 218 lines

Three middlewares: CORS, security headers, and a per-IP rate limiter that
applies only to mutating requests, so reads are never throttled.

### `internal/platform/preflight/preflight.go` — 64 lines

Checks Mathpix credentials at boot by calling the API with a deliberately
invalid document ID. A `401` means the credentials are wrong; anything else
means they were accepted. Non-fatal by design — the server starts either way and
reports the result on `/api/v1/capabilities`.

---

## Tests

| File | Covers |
|---|---|
| `hasher/md5_test.go` | Hash stability and correctness |
| `mathpix/client_test.go` | Upload, poll and fetch against a stub server |
| `logging/logging_test.go` | Correlation ID minting and propagation |
| `metrics/metrics_test.go` | Counters, gauges, histogram buckets |
| `security/security_test.go` | CORS, headers, rate-limit behaviour |

---

## Build and configuration

| File | Does |
|---|---|
| `go.mod` | Module path and four direct dependencies |
| `go.sum` | Dependency checksums |
| `Makefile` | `up`, `migrate`, `build`, `test`, `gate`, `fmt`, `vet`, `clean` |
| `docker-compose.yml` | Postgres for local development, plus the API service |
| `deploy/Dockerfile.api` | Two-stage build producing a static binary on Alpine |
| `.github/workflows/ci.yml` | `go vet`, `gofmt`, `go build`, `go test`, plus a Docker build smoke test |
| `.env.example` | Template for local configuration — copy to `.env` and fill in |
| `.gitignore` | Excludes binaries, `.env*`, IDE files and `/data` |
| `.gitattributes` | Pins `*.go`, `go.mod` and `go.sum` to LF line endings |
| `README.md` | Overview, pipeline walkthrough, API, database, configuration |

### Why `.gitattributes` matters

Under `core.autocrlf=true` on Windows, Go files are checked out as CRLF, and
`gofmt -l .` then reports every file as unformatted — so the format gate fires
on line-ending noise rather than real drift.

`go.mod` and `go.sum` are pinned for a different reason: the Go toolchain
rewrites them as LF on every touch, so without the pin they show permanently
modified in `git status`. A pair of files that always looks changed is exactly
where a real dependency change would hide.
