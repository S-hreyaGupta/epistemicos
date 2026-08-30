<!-- refreshed: 2026-08-30 -->
# Architecture

**Analysis Date:** 2026-08-30

## System Overview

EpistemicOS is a research paper ingestion and processing system. It accepts PDF documents (by URL or upload), converts them to markdown using Mathpix, stores them persistently in PostgreSQL, and provides tools to segment and analyze the content. The architecture follows the **Hexagonal (Ports & Adapters)** pattern, with strict separation between core business logic and infrastructure concerns.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Primary Adapters (Inbound)                       │
├──────────────────────────────┬──────────────────────────────────────────────┤
│  HTTP REST API               │  CLI Commands                                │
│  `internal/adapters/         │  `cmd/epistemicos-cli/`                      │
│   primary/http/`             │  - ingest, classify, segment, review, etc.   │
└──────────────┬───────────────┴───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Core Services (Business Logic)                         │
├────────────────┬────────────────┬──────────────────┬───────────────────────┤
│  ingest.Service│  papertype.    │  segmentation.   │  (Future services)    │
│                │  Service       │  Service         │  review, export, etc. │
│                │                │                  │                       │
│ `internal/core/│ `internal/core/│ `internal/core/  │                       │
│  services/     │  services/     │  services/       │                       │
│  ingest/`      │  papertype/`   │  segmentation/`  │                       │
└────┬───────────┴────┬───────────┴────┬─────────────┴───────────────────────┘
     │                │                │
     ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│               Core Domain (No External Dependencies)                          │
├────────────────┬──────────────┬──────────────┬──────────────────────────────┤
│  Paper         │  Segment     │  Methodology │  ResearchUnit, Exhibit,    │
│  PaperType     │  Classify    │  Glossary    │  Entity Extraction         │
│  Ports (intf.) │  Rules       │              │                            │
│                │              │              │                            │
│  `internal/core│`internal/core│`internal/core│                            │
│   /domain/`    │ /domain/`    │ /domain/`    │                            │
│  `internal/core│              │              │                            │
│   /ports/`     │              │              │                            │
└─────┬──────────┴──────────────┴──────────────┴──────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                   Secondary Adapters (Outbound)                              │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────────┤
│ PostgreSQL   │ Mathpix PDF→ │ PDF Download │ MD5 Hasher  │ LLM Adapters     │
│ Store        │ Markdown     │ Client       │ (Content)   │ (Claude)         │
│              │ Converter    │              │             │ Classifier,      │
│ `internal/   │              │ `internal/   │ `internal/  │ Suggester        │
│  adapters/   │ `internal/   │  adapters/   │  adapters/  │                  │
│  secondary/  │  adapters/   │  secondary/  │  secondary/ │ `internal/       │
│  store/`     │  secondary/  │  pdfdownload │  hasher/`   │  adapters/       │
│              │  mathpix/`   │  er/`        │             │  secondary/llm*/ │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    External Systems & Infrastructure                         │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────────┤
│ PostgreSQL   │ Mathpix API  │ HTTP/PDFs    │ SHA-256,     │ Anthropic Claude │
│ Database     │ (PDF→MD)     │ (Downloads)  │ MD5 (stdlib) │ API              │
│ (epistemicos │              │              │              │                  │
│  schema)     │              │              │              │                  │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **HTTP Server** | REST API routes, middleware, request/response handling | `internal/adapters/primary/http/server.go` |
| **Ingest Service** | Orchestrates PDF→markdown pipeline (9 steps) | `internal/core/services/ingest/ingest.go` |
| **Paper Store** | PostgreSQL persistence for papers with status tracking | `internal/adapters/secondary/store/postgres.go` |
| **Mathpix Client** | 3-phase async PDF→markdown conversion (upload, poll, fetch) | `internal/adapters/secondary/mathpix/client.go` |
| **PDF Downloader** | Fetches PDFs from URLs as streams | `internal/adapters/secondary/pdfdownloader/downloader.go` |
| **Hasher** | MD5 hashing for content deduplication | `internal/adapters/secondary/hasher/md5.go` |
| **Segmentation Service** | Step 3: segment markdown, classify sections, persist runs | `internal/core/services/segmentation/service.go` |
| **Paper Type Service** | Classifies papers as empirical/systematic/conceptual | `internal/core/services/papertype/service.go` |
| **Platform Config** | Environment variable loading with legacy fallback | `internal/platform/config/config.go` |
| **Platform Logging** | Structured logging with correlation IDs | `internal/platform/logging/logging.go` |
| **Platform Metrics** | Prometheus metrics registry | `internal/platform/metrics/metrics.go` |
| **Security** | CORS, rate limiting, security headers middleware | `internal/platform/security/security.go` |

## Pattern Overview

**Overall:** Hexagonal Architecture (Ports & Adapters)

**Key Characteristics:**
- **Testable**: Core business logic has no external dependencies; all I/O through interfaces (ports)
- **Swappable**: Adapters can be replaced without changing core logic (e.g., different markdown processor, different database)
- **Deterministic**: Domain packages (`internal/core/domain/`) import only stdlib; no framework coupling
- **Layered**: Clear separation: API → Services → Domain logic → Adapters → External systems

## Layers

**HTTP Primary Adapter:**
- Purpose: Expose REST API endpoints for paper ingestion
- Location: `internal/adapters/primary/http/`
- Contains: Route table, handlers, DTOs, error responses
- Depends on: Ingest service, metrics, config
- Used by: HTTP clients (browsers, curl, SDKs)
- Routes:
  - `GET /health` - health check
  - `GET /api/v1/capabilities` - advertise enabled features (Mathpix, etc.)
  - `POST /api/v1/papers` - ingest paper (JSON URL or multipart file upload)
  - `GET /api/v1/papers` - list all papers
  - `GET /api/v1/papers/{id}` - fetch one paper with markdown
  - `GET /metrics` - Prometheus metrics

**CLI Primary Adapter:**
- Purpose: Command-line interface for ingest, classification, segmentation, review workflows
- Location: `cmd/epistemicos-cli/`
- Contains: Command dispatch, subcommand implementations
- Depends on: Same core services as HTTP adapter
- Used by: Operators, automation scripts

**Core Services Layer:**
- Purpose: Orchestrate business workflows
- Location: `internal/core/services/`
- Responsibilities:
  - **ingest**: PDF staging, hashing, deduplication, Mathpix conversion, markdown storage
  - **papertype**: Paper classification gate (empirical vs. systematic/conceptual)
  - **segmentation**: Markdown segmentation, section classification, run persistence
- These services compose domain logic with adapter ports

**Domain Layer (Core):**
- Purpose: Pure business rules and domain concepts
- Location: `internal/core/domain/` and `internal/core/ports/`
- Contains: Aggregates (`Paper`), value objects, domain logic rules
- Key domains:
  - `paper/`: Paper aggregate with lifecycle states (pending → downloading → processing → ready/failed)
  - `segment/`: Document structure (sections, exhibits, research units, methodological elements)
  - `exhibit/`: Table and figure extraction with caption and positioning rules
  - `methodology/`: Research methodology glossary and classification
  - `researchunit/`: Empirical research unit detection (population, intervention, outcome, comparator)
  - `papertype/`: Paper type classification rules
- **Ports** define contracts:
  - `ingest.go`: PDFDownloader, MarkdownProcessor, Hasher
  - `store.go`: PaperStore persistence interface
  - `segmentation.go`: SegmentationStore, ApprovedMarkdownSource
  - `papertype.go`: PaperTypeGate
  - `researchunit.go`: ResearchUnitGate

**Secondary Adapters Layer:**
- Purpose: Implement domain ports by connecting to external systems
- Location: `internal/adapters/secondary/`
- Components:
  - **store/**: PostgreSQL implementation of PaperStore (CRUD, migrations embedded)
  - **mathpix/**: HTTP client for Mathpix API (upload → poll → fetch)
  - **pdfdownloader/**: HTTP client for downloading PDFs
  - **hasher/**: MD5 file hashing
  - **llmclassify/**: Claude API adapter for paper classification
  - **llmsuggest/**: Claude API adapter for advisory suggestions
  - **approved/**: Wrapper around store for segmentation workflow

**Platform Layer:**
- Purpose: Cross-cutting infrastructure concerns
- Location: `internal/platform/`
- Components:
  - **config/**: Environment variable loading (EPISTEMIC_OS_* prefix, legacy PAPERLY_* fallback)
  - **logging/**: Structured logging with correlation IDs (middleware-injected)
  - **metrics/**: Prometheus registry and metric collectors
  - **security/**: CORS, rate limiting (per-IP, configurable RPM/burst), security headers
  - **preflight/**: Startup checks (e.g., Mathpix credential validation)

## Data Flow

### Primary Request Path: PDF Ingestion (Ingest)

The **complete pipeline** is orchestrated in `internal/core/services/ingest/ingest.go`:

1. **Entry** (`internal/adapters/primary/http/handlers.go:handleCreatePaper`)
   - Route dispatcher: JSON request → `ingest.FromURL()`, multipart upload → `ingest.FromUpload()`
   - Max upload size: 50 MB

2. **Stream to Disk** (`internal/core/services/ingest/ingest.go:fromReader`)
   - PDF bytes written to staging file `{PDFDir}/tmp-{uuid}.pdf`
   - Reason: Both hasher and Mathpix need a file path

3. **Content Hash** (`internal/adapters/secondary/hasher/md5.go`)
   - MD5 hash computed over source PDF
   - Purpose: Deduplication key (identifies the source document)
   - Stored as `paper.Hash`

4. **Deduplication Check** (`internal/adapters/secondary/store/postgres.go:GetByHash`)
   - Query: `SELECT * FROM papers WHERE hash = $1`
   - If found: Return existing paper, delete temp file, short-circuit (no Mathpix cost)
   - Constraint: Unique index on `papers.hash` prevents concurrent duplicate inserts

5. **Persist Pending Row** (`internal/adapters/secondary/store/postgres.go:Save`)
   - Insert: `status = "pending"`, `url = $url`, `hash = $hash`, `created_at`, `updated_at`
   - Reason: Failures become visible; no silent discards
   - If Mathpix fails later, status = `"failed"`, `error` field populated

6. **Move to Permanent Location** (OS rename)
   - `{PDFDir}/tmp-{uuid}.pdf` → `{PDFDir}/{paper-id}.pdf`
   - Reason: Paper now addressable by its identity, not upload order

7. **Mathpix Conversion** (`internal/adapters/secondary/mathpix/client.go`)
   - Status updated to `"processing"`
   - Phase 1 (Upload): POST PDF multipart to Mathpix, receive `pdf_id`
   - Phase 2 (Poll): Check status on interval until `"completed"` or `"error"`
   - Phase 3 (Fetch): Retrieve markdown from Mathpix
   - Extract title: Best-effort parse first markdown heading

8. **Markdown Hash** (SHA-256)
   - Compute: `sha256(markdown)`
   - Purpose: Integrity verification (consumers can verify byte offsets against this hash)
   - Format: Hex-encoded

9. **Atomic Write** (`internal/adapters/secondary/store/postgres.go:UpdateMarkdown`)
   - Single statement: `UPDATE papers SET markdown = $1, markdown_hash = $2, status = 'ready' WHERE id = $3`
   - Reason: Markdown and hash cannot drift; any offset-based indexing is verifiable

**Return:** `Paper` aggregate with all fields populated (id, url, hash, title, markdown, markdown_hash, status=ready)

### Secondary Path: Segmentation (Step 3)

Entry point: CLI `segment <paper-id>` or (future) API endpoint

1. **Fetch Approved Markdown** (`internal/adapters/secondary/approved/papers.go:Get`)
   - Query paper from store
   - Verify: `sha256(markdown) == stored_markdown_hash`
   - Return: (markdown bytes, hash string)
   - Reason: Hash re-verified here to ensure bytes haven't been transformed

2. **Paper Type Gate** (`internal/core/services/segmentation/service.go:Segment`)
   - Precondition check: Is this paper empirical? (run gate first, before segmentation)
   - Reason: Empirical papers have expected sections; systematic/conceptual papers classify wrongly
   - If gate fails: No partial run persisted

3. **Build Document Tree** (`internal/core/domain/segment/build.go`)
   - Parse markdown into AST (headings, paragraphs, tables, figures)
   - Construct role hierarchy based on section structure
   - Extract methodological elements (PICO: population, intervention, comparator, outcome)

4. **Classify Sections** (`internal/core/domain/segment/classify.go`)
   - Rule-based section type classification
   - Assign roles based on heading levels and text patterns

5. **Persist Run** (`internal/adapters/secondary/store/segmentation.go:SaveRun`)
   - Insert run record with:
     - `paper_id`, `status = "complete"`, `segments` (JSON array with byte offsets)
   - Byte offsets verified against markdown_hash

**Return:** Run ID; run is now ready for review

### Error Handling Strategy

**Domain errors** are specific, defined in `internal/core/ports/store.go`:
- `ErrNotFound`: Resource doesn't exist
- `ErrDecisionsFrozen`: Run already consumed, no more changes allowed
- `ErrAlreadyReturned`: Author return report already sent
- `ErrAlreadyRejected`: Run-level rejection already recorded

**Adapter errors** wrap with context:
- `fmt.Errorf("component: %w", err)` — preserve original error, add layer name
- HTTP handlers translate to status codes and error responses

**Service errors** fail fast:
- Mathpix upload fails → status = `"failed"`, error message stored
- Process dies → next run of CLI sees `status = "processing"` and retries
- DB connection lost → HTTP 500, client retries

## State Management

**Paper Lifecycle** (`internal/core/domain/paper/paper.go`):
```
pending → downloading → processing → ready
              ↓            ↓
              └─────────► failed
```

**Run Lifecycle** (segmentation):
- `created` → `complete` (or persisted as review decisions applied)

**Database Consistency**:
- Unique constraint on `papers.hash` enforces deduplication
- Markdown + markdown_hash written in single statement (atomic)
- Run persisted only after hash verification (no partial state)

**Thread Safety**:
- Ingest service is synchronous (Mathpix latency dominates)
- Database handles concurrent ingests (unique constraint on hash)
- No in-process caching of papers (always fetch from store)

## Key Abstractions

**Paper Aggregate** (`internal/core/domain/paper/paper.go`):
- Represents one ingested research paper
- Owns: source URL, content hash (dedup), title, markdown, markdown hash, status, error
- Lifecycle: pending → downloading → processing → ready | failed
- Invariant: If `status == ready`, both `markdown` and `markdown_hash` are populated

**PaperStore Port** (`internal/core/ports/store.go`):
- Interface: Abstract data persistence
- Implementations: `PostgresPaperStore` (only one implementation currently)
- Methods: Save, GetByID, GetByHash, List, UpdateStatus, UpdateMarkdown
- Reason: Core logic never knows it's talking to Postgres; tests can mock

**Markdown Processor Port** (`internal/core/ports/ingest.go`):
- Interface: PDF file → (title, markdown)
- Implementation: `mathpix.Client` (3-phase async)
- Reason: Could swap for a different provider (e.g., PyMuPDF, pdfplumber) without changing core

**Segment Aggregate** (`internal/core/domain/segment/`):
- Represents parsed, classified document structure
- Contains: Section tree, extracted exhibits (tables/figures), research units
- No I/O; pure business rules

**Run Aggregate** (segmentation output):
- Represents segmentation result for a paper
- Owns: Paper ID, status, segments, review decisions, rejection status
- Persisted in `runs` and `run_segments` tables

## Entry Points

**HTTP API Server:**
- Location: `cmd/epistemicos-api/main.go`
- Triggered: `go run ./cmd/epistemicos-api` or `epistemicos-api` binary
- Initialization:
  1. Load `.env` with `godotenv.Load()`
  2. Load config: `config.Load()` reads `EPISTEMIC_OS_*` env vars
  3. Run migrations: `store.RunMigrations(cfg.DBURL)`
  4. Connect to Postgres: `pgxpool.New(...)`
  5. Instantiate adapters: paperStore, downloader, processor, hasher
  6. Construct ingest service
  7. Probe Mathpix (preflight check, non-blocking failure)
  8. Assemble middleware chain (CORS → SecurityHeaders → RateLimit → CorrelationID → Routes)
  9. Serve HTTP until SIGINT/SIGTERM → graceful shutdown (15s timeout)
- Binds: `cfg.ListenAddr` (default `:9082`)

**CLI:**
- Location: `cmd/epistemicos-cli/main.go`
- Triggered: `epistemicos-cli <command> [args]`
- Commands: migrate, ingest, ingest-file, classify, segment, review, resolve, reject, gate, return-to-author, effective, suggest, methodology, exhibits, research-unit, list, export-markdown, help
- Each command:
  1. Loads `.env`
  2. Loads config
  3. Connects to Postgres
  4. Instantiates same core services as API
  5. Executes subcommand (e.g., `ingest.FromURL(...)`)
  6. Prints result or error to stdout/stderr

## Architectural Constraints

- **Threading:** Synchronous, single-threaded per request. Mathpix conversion is the latency bottleneck; no queue in front of it.
- **Global state:** None. Each request/invocation creates fresh service instances.
- **Circular imports:** None. Dependency direction: adapters/CLI → services → domain ← ports. Ports define contracts; domain implements them.
- **Configuration:** All environment variables; no config files. `.env` file for dev convenience (loaded by `godotenv`).
- **Logging:** Structured, with correlation IDs injected per HTTP request (middleware).
- **Metrics:** Optional Prometheus registry; inert if not wired.
- **Error recovery:** None. Failures are logged and returned to caller; no retries built into adapters.

## Anti-Patterns to Avoid

### Bypassing the Paper Type Gate

**What happens:** Calling `segmentation.Service.Segment()` on an unclassified paper (one that hasn't passed the empirical-paper classification check).

**Why it's wrong:** Empirical papers have expected section types (introduction, methods, results, discussion). Non-empirical papers (systematic reviews, opinion pieces) classify wrongly when run through empirical section rules, creating confusing/misleading segmentation results.

**Do this instead:** Always run `papertype.Service.Classify()` first. If the paper is not empirical (type A), reject it and don't proceed to segmentation. The gate in `segmentation.Service.Segment()` enforces this at runtime: `if s.gate == nil { return error }`. Do not pass `nil` for the gate.

### Writing Markdown Without Hash

**What happens:** Modifying a paper's markdown without recomputing and storing its hash in the same transaction.

**Why it's wrong:** Consumers rely on byte offsets into the markdown. Without the hash, they have no way to verify the offsets are valid. A stale offset into modified markdown could extract the wrong phrase.

**Do this instead:** Use the `UpdateMarkdown(ctx, id, title, markdown, markdownHash)` method on `PaperStore`. It atomically updates both in a single statement, so they never drift.

### Trusting Byte Offsets Without Verification

**What happens:** Code extracts a substring from markdown using a stored byte offset without first verifying the markdown hash.

**Why it's wrong:** If the markdown was modified upstream (e.g., normalized line endings), the offset is now wrong.

**Do this instead:** Before using an offset, verify `sha256(markdown) == stored_markdown_hash`. See `internal/core/services/segmentation/service.go:Segment()` for the pattern.

### Mocking the Store in Segmentation Tests

**What happens:** Creating a mock `PaperStore` that returns arbitrary markdown without going through the actual store.

**Why it's wrong:** The mock might return markdown that doesn't match the hash it claims, hiding bugs where code forgets to re-verify.

**Do this instead:** For segmentation tests, use the real `ApprovedMarkdownSource` adapter (`internal/adapters/secondary/approved/papers.go`), which enforces hash verification. Only mock if you're testing the segmentation service's error handling.

## Error Handling

**Strategy:** Errors are surfaced, not silently swallowed. Callers decide what to do (retry, fail, ignore).

**Patterns:**

- **Wrapping:** `fmt.Errorf("context: %w", err)` — preserves stack, adds layer name
- **Specific errors:** `ErrNotFound`, `ErrDecisionsFrozen`, etc., defined in ports so callers can `errors.Is()` against them
- **Status field:** For slow operations like Mathpix, `paper.Status` tracks progress. On failure, `paper.Status = "failed"`, `paper.Error = "description"`. Next run can see the failure and retry.
- **HTTP responses:** Errors are JSON `{"error": "message"}` with appropriate status codes (400, 404, 500)
- **CLI:** Errors are printed to stderr and exit code is non-zero

## Cross-Cutting Concerns

**Logging:**
- Framework: `log` stdlib + structured fields (correlation ID)
- Middleware: `logging.CorrelationMiddleware` injects request ID into logs
- Format: Text (simple), no JSON marshalling
- Visibility: Startup config, adapter errors, Mathpix polling retries, metrics writes

**Validation:**
- **HTTP handlers:** Check for required fields (URL, file), parse JSON, multipart parsing
- **Core services:** Validate before expensive operations (e.g., URL is required before download)
- **Domain:** Business rules enforced (e.g., empirical paper precondition for segmentation)

**Authentication:**
- **Not implemented.** API is open; no auth layer.
- **Future:** Would live in HTTP middleware (bearer token or similar)

**Rate Limiting:**
- **Framework:** `security.RateLimit` middleware
- **Config:** `EPISTEMIC_OS_RATE_LIMIT_RPM` (requests per minute, default 60), `EPISTEMIC_OS_RATE_LIMIT_BURST` (burst capacity, default 20)
- **Scope:** Per-IP, on mutating endpoints (POST)
- **Behavior:** Rejects requests over limit with 429 status

**CORS:**
- **Middleware:** `security.CORS` with configurable allowed origins
- **Default:** `*` (permissive, for dev). Set `EPISTEMIC_OS_CORS_ALLOWED_ORIGINS` in production.

---

*Architecture analysis: 2026-08-30*
