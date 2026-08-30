# External Integrations

**Analysis Date:** 2026-08-30

## APIs & External Services

**PDF-to-Markdown Conversion:**
- Mathpix (v3 API) - Converts PDF documents to markdown with LaTeX formatting
  - SDK/Client: Custom HTTP client in `internal/adapters/secondary/mathpix/client.go`
  - Auth: `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` environment variables
  - Base URL: `https://api.mathpix.com/v3`
  - Process: Upload PDF → Poll status → Fetch markdown (asynchronous)
  - Optional: Deployment can start without credentials; capabilities endpoint reports `mathpix_enabled=false`
  - Implementation file: `internal/adapters/secondary/mathpix/client.go`

**LLM Classification & Suggestions:**
- Anthropic Claude API - Classifies paper research type (empirical vs out-of-scope)
  - SDK/Client: Custom HTTP client in `internal/adapters/secondary/llmclassify/claude.go` and `internal/adapters/secondary/llmsuggest/claude.go`
  - Auth: `ANTHROPIC_API_KEY` environment variable
  - Models: `claude-sonnet-4-5-20250929` (default, stored with verdicts for reproducibility)
  - Endpoints:
    - **Classification (llmclassify)**: In-pipeline decision gate, strict response validation, all quotes verified
    - **Suggestions (llmsuggest)**: Advisory only, outside pipeline, reads completed runs, prints suggestions, writes nothing
  - Timeout: 300 seconds for classification (longer due to step-by-step reasoning)
  - Implementation files:
    - `internal/adapters/secondary/llmclassify/claude.go` - Classification service
    - `internal/adapters/secondary/llmsuggest/claude.go` - Suggestion advisory service

**PDF Fetching:**
- HTTP(S) downloader - Fetches PDFs from URLs
  - SDK/Client: Standard library `net/http` in `internal/adapters/secondary/pdfdownloader/downloader.go`
  - No auth required
  - Returns file stream to caller
  - Implementation file: `internal/adapters/secondary/pdfdownloader/downloader.go`

## Data Storage

**Databases:**
- PostgreSQL 16
  - Connection: `EPISTEMIC_OS_DB_URL` environment variable (required)
  - Example: `postgres://user:password@host:5432/epistemicos?sslmode=disable`
  - Client: `github.com/jackc/pgx/v5` (connection pooling via pgxpool)
  - Tables managed via migrations in `internal/adapters/secondary/store/migrations/`:
    - `papers` - Ingested documents with markdown and status
    - `segments` - Document structure (headings, sections)
    - `paper_type` - Research classification verdicts
    - `review_gate_*` - Human review decisions and evidence
    - `research_unit` - Multi-study detection and classification
    - And supporting tables for consensus, methodology, etc.
  - Schema version: Latest via `golang-migrate` (currently 12 migrations)
  - Implementation file: `internal/adapters/secondary/store/postgres.go`

**File Storage:**
- Local filesystem only
  - PDFs staged in: `EPISTEMIC_OS_PDF_VOLUME` (default `./data/pdfs`)
  - Naming: `tmp-<uuid>.pdf` during processing, renamed to `<paper-id>.pdf` for permanence
  - Volume mount in Docker Compose: `pdf_data:/data/pdfs`
  - No cloud storage integration
  - Implementation file: `internal/core/services/ingest/ingest.go`

**Caching:**
- None - No explicit cache layer (Redis, Memcached, etc.)
- Database is single source of truth
- Deduplication via content hash (MD5) prevents redundant Mathpix calls

## Authentication & Identity

**API Authentication:**
- None implemented - No API key or bearer token authentication
- All endpoints are public; CORS controls which origins can call them
- Review operations identified by `--by <reviewer>` flag in CLI

**Secrets Locations:**
- Environment variables only:
  - `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` - Mathpix credentials
  - `ANTHROPIC_API_KEY` - Claude API key
  - `EPISTEMIC_OS_DB_URL` - Database connection string
- `.env` file for local development (not committed)
- Docker Compose environment section for containerized deployment
- No `.env` file checking in CI (each environment manages its own secrets)

## Monitoring & Observability

**Metrics:**
- OpenTelemetry integration for distributed tracing and metrics
- Implementation: `internal/platform/metrics/metrics.go`
- Endpoints:
  - `/metrics` - Prometheus-compatible metrics endpoint on API
  - No external metrics backend detected (metrics collected in-memory)

**Logging:**
- Standard Go logger with correlation IDs
- Implementation: `internal/platform/logging/logging.go`
- Correlation middleware: Adds unique ID to each request for tracing
- Error tracking: Written to database `papers.error` field
- No external log aggregation (CloudWatch, Datadog, etc.) detected

**Health Checks:**
- API: `GET /health` endpoint
- Docker Compose: Health checks configured for both postgres and api services
- Simple status endpoint, no detailed diagnostics

## CI/CD & Deployment

**Hosting:**
- Docker containers (self-managed or on-premise)
- Example in Docker Compose shows postgres + api on same host
- No cloud platform lock-in detected

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
  - Triggers: Push to main, pull requests to main
  - Jobs:
    - `go` job: Linting (vet, gofmt), building, testing
    - `docker` job: Docker image build smoke test
  - Go 1.24 with module caching
  - No deployment step in CI (deployment is manual or external process)

**Build Artifacts:**
- Two binaries:
  - `epistemicos-api` - HTTP server on port 9082
  - `epistemicos-cli` - Offline command-line tool for migrations and operations
- Docker image: `epistemicos-api:ci` for API service only

## Environment Configuration

**Required Environment Variables:**
- `EPISTEMIC_OS_DB_URL` - PostgreSQL connection string (no default, required)

**Optional Environment Variables:**
- `MATHPIX_APP_ID` - Mathpix app ID (empty = PDF conversion disabled)
- `MATHPIX_APP_KEY` - Mathpix app key (empty = PDF conversion disabled)
- `ANTHROPIC_API_KEY` - Claude API key (empty = classification/suggestions disabled)
- `EPISTEMIC_OS_LISTEN_ADDR` - API bind address (default `:9082`)
- `EPISTEMIC_OS_PDF_VOLUME` - PDF staging directory (default `./data/pdfs`)
- `EPISTEMIC_OS_CORS_ALLOWED_ORIGINS` - CORS allowed origins (default `*`, comma-separated list)
- `EPISTEMIC_OS_RATE_LIMIT_RPM` - Requests per minute limit (default 60, 0 disables)
- `EPISTEMIC_OS_RATE_LIMIT_BURST` - Burst capacity per IP (default 20)

**Legacy Variable Names:**
- Old prefix `PAPERLY_` no longer supported (renamed 2026-08-24)
- Old deployment with `PAPERLY_DB_URL` will fail with helpful error message directing to rename

## Webhooks & Callbacks

**Incoming:**
- None detected - No webhook receiver endpoints

**Outgoing:**
- None detected - No external system notifications
- Mathpix calls are request-response only (no callbacks)
- Anthropic calls are request-response only (no callbacks)

## Data Flow Summary

1. **Ingest Flow:** PDF (URL or upload) → HTTP download → MD5 hash → PostgreSQL dedup check → store pending → Mathpix conversion → SHA-256 markdown hash → PostgreSQL storage
2. **Classification Flow:** Markdown → Anthropic Claude → Verdict (stored with model name) → Database
3. **Suggestion Flow:** Completed run → Anthropic Claude → Advisory suggestions (read-only, no write)
4. **Review Flow:** CLI operations update review verdicts → PostgreSQL timestamps and comments → No external notifications

---

*Integration audit: 2026-08-30*
