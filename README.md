# EpistemicOS

Takes a research paper PDF and produces markdown.

```
PDF  →  download  →  hash  →  Mathpix  →  markdown + SHA-256  →  Postgres
```

That is the entire system. Nothing else is here — no analysis, no LLM calls, no
section parsing, no frontend.

---

## Scope

This repository is a deliberate narrowing of the `paperly` codebase, which grew
a second system on top of this one: twelve LLM-backed slot extractors, seven
archetype rules over their output, a rubric engine, an editor's-note
synthesiser, an eval harness, a section splitter, and a React frontend.

Roughly 17,000 of that repository's 22,500 Go lines belonged to layers above the
ingest path. None of them are here — **absent, not disabled behind a flag**. A
flag leaves code reachable, importable, and available to depend on by accident.

What remains is 30 files that make one thing work.

| In | Out |
|---|---|
| PDF download from a URL | Slot extraction, archetype rules, flags |
| Content hashing and dedupe | Section splitting and role classification |
| Mathpix conversion | LLM clients, rubric engine, synthesiser |
| Markdown persistence with SHA-256 | Eval harness and gold corpus |
| Ingest HTTP API and CLI | React frontend |

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
  secondary/hasher/        Content addressing
  secondary/store/         Postgres via pgx, migrations

internal/platform/         config, logging, metrics, security, preflight
```

Hexagonal: the core depends on interfaces, adapters implement them, and nothing
in `internal/core` imports from `internal/adapters`.

Four ports. One store. Four direct dependencies — pgx, golang-migrate, uuid,
godotenv. No web framework, no ORM, and no Anthropic SDK.

---

## The one contract worth knowing

`ingest.Service` computes the SHA-256 of the markdown and hands it to
`PaperStore.UpdateMarkdown` in the same call that writes the markdown itself.
One statement, so the two cannot diverge.

Anything downstream that indexes into this text — by byte offset or otherwise —
can check what it holds against `papers.markdown_hash` before trusting it. That
guarantee is the reason the hash exists, and the reason `export-markdown` is a
subcommand rather than a shell pipeline: piping the API response through `jq`
into a redirect appends a newline and can inject CRLF, either of which silently
breaks it.

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

Missing Mathpix credentials do not prevent startup. The service runs, serves
reads, and reports `mathpix_enabled: false`. Discovering the same fact by
watching an upload fail is noisier.

---

## Database

One table beyond migration bookkeeping: `papers`.

| Migration | Adds |
|---|---|
| `0001_initial` | `papers` |
| `0004_markdown_hash` | `papers.markdown_hash` |

Numbering skips `0002` and `0003`. Those created `slots`, `flags` and
`editor_notes` for the removed pipeline. The gap is deliberate and the numbers
are not reused, so a database that already applied them stays consistent.

**One inherited defect worth knowing.** `markdown_hash` is
`NOT NULL DEFAULT ''`. Any staleness check written as `a.Hash != b.Hash`
therefore passes trivially when both sides are empty — precisely the rows with
no integrity guarantee. A consumer must treat the empty string as *absent*,
never as a match.

---

## The gate

```bash
make gate     # go vet + gofmt + go build + go test
```

CI runs the same four. `gofmt` is enforced here, unlike in the predecessor
repository where it was never gated and twenty-five files had accumulated
drift. Starting clean means it can stay clean.

`.gitattributes` pins `*.go`, `go.mod` and `go.sum` to LF. Without the first the
format gate fires on `core.autocrlf` noise instead of real drift; without the
others `go.mod` and `go.sum` show permanently modified, which is exactly where a
real dependency change would hide.
