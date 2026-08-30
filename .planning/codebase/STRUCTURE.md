# Codebase Structure

**Analysis Date:** 2026-08-30

## Directory Layout

```
epistemicos-gsd-pilot/
├── cmd/                         # Entry points (CLI and API servers)
│   ├── epistemicos-api/
│   │   └── main.go             # HTTP API server (123 lines)
│   └── epistemicos-cli/
│       ├── main.go             # CLI command dispatcher (139 lines)
│       ├── classify.go         # Paper type classification command
│       ├── segment.go          # Run segmentation command
│       ├── review.go           # Review management commands
│       ├── resolve.go          # Record reviewer answers
│       ├── reject.go           # Run-level rejection
│       ├── gate.go             # Gate status queries
│       ├── researchunit.go     # Research unit management
│       ├── methodology.go      # Methodology output
│       ├── exhibits.go         # Exhibit (table/figure) output
│       ├── suggest.go          # LLM suggestions
│       ├── export.go           # Export markdown to file
│       └── [other subcommands]
│
├── internal/                    # Private Go packages
│   ├── core/                   # Core business logic (NO external deps)
│   │   ├── domain/             # Domain models, aggregates, rules
│   │   │   ├── exhibit/        # Table/figure extraction
│   │   │   │   ├── exhibit.go
│   │   │   │   ├── exhibit_test.go
│   │   │   │   └── deps_test.go
│   │   │   ├── methodology/    # Research methodology glossary
│   │   │   │   ├── classify.go
│   │   │   │   ├── glossary.go
│   │   │   │   ├── testdata/   # Real markdown from papers
│   │   │   │   └── [tests]
│   │   │   ├── paper/          # Paper aggregate (status lifecycle)
│   │   │   │   └── paper.go
│   │   │   ├── papertype/      # Paper type classification rules
│   │   │   │   ├── papertype.go
│   │   │   │   ├── prompt.go
│   │   │   │   └── [tests]
│   │   │   ├── researchunit/   # PICO: population, intervention, comparator, outcome
│   │   │   │   ├── detect.go
│   │   │   │   ├── unit.go
│   │   │   │   └── [tests]
│   │   │   └── segment/        # Markdown parsing, section classification
│   │   │       ├── build.go    # AST construction
│   │   │       ├── classify.go # Section type rules
│   │   │       ├── [tests with testdata/]
│   │   │       └── testdata/   # Real markdown samples
│   │   │
│   │   ├── ports/              # Interfaces (contracts with outside world)
│   │   │   ├── ingest.go       # PDFDownloader, MarkdownProcessor, Hasher
│   │   │   ├── store.go        # PaperStore (persistence)
│   │   │   ├── papertype.go    # PaperTypeGate
│   │   │   ├── segmentation.go # SegmentationStore, ApprovedMarkdownSource
│   │   │   └── researchunit.go # ResearchUnitGate
│   │   │
│   │   └── services/           # Use case orchestration (thin layer)
│   │       ├── ingest/
│   │       │   ├── ingest.go   # Main: PDF staging, hash, Mathpix, markdown store
│   │       │   └── [tests]
│   │       ├── papertype/      # Paper classification service
│   │       ├── segmentation/   # Step 3: segment + classify
│   │       └── [other services]
│   │
│   ├── adapters/               # Framework/infrastructure adapters
│   │   ├── primary/            # Incoming (request adapters)
│   │   │   └── http/
│   │   │       ├── server.go      # Route table, dependency wiring
│   │   │       ├── handlers.go    # Six HTTP handlers
│   │   │       ├── dto.go         # Request/response shapes
│   │   │       └── [tests]
│   │   │
│   │   └── secondary/          # Outgoing (implementation adapters)
│   │       ├── store/          # PostgreSQL implementation
│   │       │   ├── postgres.go        # PaperStore CRUD
│   │       │   ├── segmentation.go    # SegmentationStore CRUD
│   │       │   ├── migrate.go         # Migration runner
│   │       │   ├── migrations/        # SQL migration files
│   │       │   │   ├── 0001_initial.up.sql
│   │       │   │   ├── 0001_initial.down.sql
│   │       │   │   ├── 0004_markdown_hash.up.sql
│   │       │   │   └── [others]
│   │       │   ├── authorreturn.go    # Author return report persistence
│   │       │   ├── runrejection.go    # Run-level rejection persistence
│   │       │   ├── researchunit.go    # Research unit CRUD
│   │       │   ├── papertype.go       # Paper type verdict storage
│   │       │   └── [tests]
│   │       │
│   │       ├── mathpix/        # Mathpix PDF→markdown API
│   │       │   ├── client.go        # 3-phase async: upload, poll, fetch
│   │       │   └── [tests]
│   │       │
│   │       ├── pdfdownloader/  # HTTP PDF fetch
│   │       │   ├── downloader.go
│   │       │   └── [tests]
│   │       │
│   │       ├── hasher/         # MD5 content hashing
│   │       │   ├── md5.go
│   │       │   └── [tests]
│   │       │
│   │       ├── approved/       # Wrapper: store with hash verification
│   │       │   ├── papers.go
│   │       │   └── [tests]
│   │       │
│   │       ├── llmclassify/    # Claude API for paper classification
│   │       │   └── claude.go
│   │       │
│   │       └── llmsuggest/     # Claude API for advisory suggestions
│   │           └── claude.go
│   │
│   └── platform/               # Cross-cutting infrastructure
│       ├── config/             # Environment variable loading
│       │   └── config.go       # EPISTEMIC_OS_* prefix, legacy fallback
│       ├── logging/            # Structured logging
│       │   ├── logging.go
│       │   └── [tests]
│       ├── metrics/            # Prometheus metrics
│       │   ├── metrics.go
│       │   └── [tests]
│       ├── security/           # CORS, rate limiting, security headers
│       │   ├── security.go
│       │   └── [tests]
│       └── preflight/          # Startup checks
│           └── preflight.go    # Mathpix credential validation
│
├── deploy/                      # Deployment configuration
│   ├── Dockerfile.api          # Docker image for HTTP API server
│   └── [other deploy artifacts]
│
├── docs/                        # Documentation
│   └── FILES.md                # File reference (what each file does, why it exists)
│
├── go.mod                       # Go module definition
├── go.sum                       # Go dependency checksums
├── Makefile                     # Common build/test targets
├── docker-compose.yml          # Local dev: Postgres + API
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore patterns
├── README.md                   # Project overview
└── [root level config files]
```

## Directory Purposes

**`cmd/`:**
- Purpose: Entry points for distributed binaries (API server, CLI tool)
- Contains: `main()` functions, command dispatch, dependency wiring
- Key files: `cmd/epistemicos-api/main.go`, `cmd/epistemicos-cli/main.go`

**`internal/core/domain/`:**
- Purpose: Pure business logic, aggregates, domain rules
- Key invariant: **No external dependencies** (no adapters, no I/O, only stdlib)
- Contains: Data models (Paper, Segment, Exhibit, etc.), business rules, tests with real data
- Why separate: Core logic is testable and reusable; domain rules don't change when infrastructure does

**`internal/core/ports/`:**
- Purpose: Define contracts between core logic and outside world
- Contains: Go interfaces (`PaperStore`, `MarkdownProcessor`, `Hasher`, etc.)
- Why: Lets core logic stay testable (mock implementations); adapters become swappable

**`internal/core/services/`:**
- Purpose: Orchestrate workflows by composing domain logic with adapter ports
- Contains: `ingest.Service`, `segmentation.Service`, `papertype.Service`
- Pattern: Thin layer; all heavy lifting happens in domain or adapters

**`internal/adapters/primary/http/`:**
- Purpose: HTTP REST API surface
- Contains: Routes, request handlers, DTOs, error responses
- Dependencies: Ingest service, metrics, config

**`internal/adapters/secondary/store/`:**
- Purpose: PostgreSQL persistence (PaperStore implementation)
- Contains: CRUD operations, SQL migrations (embedded via `go:embed`)
- Database: `epistemicos` database, `papers`, `runs`, `run_segments`, etc. tables

**`internal/adapters/secondary/mathpix/`:**
- Purpose: Mathpix API client (PDF→markdown conversion)
- Contains: Upload, poll, fetch phases

**`internal/platform/`:**
- Purpose: Infrastructure and cross-cutting concerns
- Contains: Config loading, logging, metrics, security middleware, startup checks
- Applies to: Both API server and CLI

**`deploy/`:**
- Purpose: Deployment artifacts
- Contains: Dockerfiles, deployment scripts
- Used by: CI/CD, local docker-compose

**`docs/`:**
- Purpose: Project documentation
- Key file: `FILES.md` — describes every tracked file and why it exists

## Key File Locations

**Entry Points:**
- HTTP API server: `cmd/epistemicos-api/main.go` — wires all components, starts HTTP listener
- CLI: `cmd/epistemicos-cli/main.go` — command dispatcher

**Configuration:**
- Environment loading: `internal/platform/config/config.go` — reads `EPISTEMIC_OS_*` env vars
- Docker Compose setup: `docker-compose.yml` — Postgres + API for local dev
- Makefile: `Makefile` — build, test, gate, migrate targets

**Core Logic:**
- **Ingest orchestration:** `internal/core/services/ingest/ingest.go` (166 lines, the heart of the system)
- **Segmentation:** `internal/core/services/segmentation/service.go` — Step 3 (segment, classify, persist)
- **Paper Type:** `internal/core/services/papertype/service.go` — Classification gate
- **Domain aggregates:** `internal/core/domain/*/` — Paper, Segment, Exhibit, Methodology, ResearchUnit, PaperType
- **Domain rules:** `internal/core/domain/segment/classify.go`, `internal/core/domain/researchunit/detect.go`, etc.

**Infrastructure:**
- **HTTP API:** `internal/adapters/primary/http/server.go` (route table), `handlers.go` (logic)
- **Database:** `internal/adapters/secondary/store/postgres.go` (PaperStore), `migrations/` (SQL)
- **Mathpix:** `internal/adapters/secondary/mathpix/client.go` (3-phase async)
- **PDF Download:** `internal/adapters/secondary/pdfdownloader/downloader.go`
- **Hashing:** `internal/adapters/secondary/hasher/md5.go`

**Testing:**
- Test files co-located with implementation: `*_test.go`
- Test fixtures: `internal/core/domain/*/testdata/`
- Test dependencies/mocks: `*_deps_test.go` (in same package, not exposed)

## Naming Conventions

**Packages (directories):**
- Lowercase, no underscores: `papertype`, `mathpix`, `pdfdownloader`
- Interface types grouped in `ports/` (not `interfaces/`)
- Adapters in `adapters/{primary,secondary}/`
- Domain logic in `domain/`
- Services in `services/`
- Platform concerns in `platform/`

**Files:**
- Implementation: `service.go`, `client.go`, `postgres.go`
- Interfaces: Grouped in single file per port (`store.go`, `ingest.go`)
- Tests: `*_test.go` co-located with implementation
- Test dependencies: `*_deps_test.go` (mocks, fixtures for the whole package)
- Migrations: `{sequence}_{description}.{up,down}.sql` (e.g., `0001_initial.up.sql`)

**Types (Go identifiers):**
- Aggregates: `Paper`, `Segment`, `Run`, `Exhibit`, `ResearchUnit`
- Ports (interfaces): `PaperStore`, `MarkdownProcessor`, `Hasher`, `PDFDownloader`, `SegmentationStore`
- Services: `Service` (always; scoped by package name, e.g., `ingest.Service`, `segmentation.Service`)
- Adapters: `PostgresPaperStore`, `MathpixClient`, `PDFDownloader`, `MD5Hasher`
- Constants: `StatusPending`, `StatusReady`, `ErrNotFound`, `StatusProcessing`
- Value objects: `ID`, `Hash`, `Status` (all string-based, domain-specific)

**Functions:**
- Constructors: `New` or `New{Type}` (e.g., `NewServer`, `NewService`)
- Interface method names: Short, active voice (`Save`, `GetByID`, `UpdateMarkdown`, `Process`)
- Handler functions: `handle{Resource}{Action}` (e.g., `handleCreatePaper`, `handleListPapers`)

**Variables:**
- Private (package-scoped): `store`, `processor`, `mux`, `pool`, `s` (service receiver)
- Configuration: UPPERCASE in env vars (`EPISTEMIC_OS_DB_URL`, `MATHPIX_APP_ID`)
- Errors: `err` (always), wrapped with context (`fmt.Errorf("context: %w", err)`)

## Where to Add New Code

**New CLI Subcommand:**
1. Create `cmd/epistemicos-cli/{command}.go` with a `run{Command}([]string)` function
2. Add case statement in `cmd/epistemicos-cli/main.go:main()`
3. Implement using existing adapters and services (or create new services if needed)
4. Update usage text in `usage()` function

**New Service (Use Case):**
1. Create `internal/core/services/{usecase}/service.go`
2. Define the service struct with dependencies injected (ports, not adapters)
3. Implement methods that orchestrate domain logic
4. Write tests in `{usecase}/service_test.go`, mocking the ports
5. Wire into CLI commands and/or HTTP handlers

**New Domain Model:**
1. Create `internal/core/domain/{entity}/{entity}.go`
2. Define the aggregate/entity type and lifecycle (constants for status, etc.)
3. Implement domain logic (rules, validations) in this file or split into `{entity}_*.go`
4. **No I/O or adapters here.** If I/O is needed, that's a service concern.
5. Test in `{entity}_test.go`, using real data (testdata/)

**New Port (Interface):**
1. Add to `internal/core/ports/{concern}.go` or create a new file
2. Define interface with methods needed by core logic
3. Document behavior and invariants
4. Create adapter implementation in `internal/adapters/secondary/{provider}/`

**New HTTP Endpoint:**
1. Add handler in `internal/adapters/primary/http/handlers.go`
2. Register route in `internal/adapters/primary/http/server.go:NewServer()`
3. Define request/response DTOs in `dto.go`
4. Use existing services; if new logic needed, create a service

**New Database Migration:**
1. Create `internal/adapters/secondary/store/migrations/{next_sequence}_{description}.up.sql`
2. Create corresponding `.down.sql` for rollback
3. Run with `go run ./cmd/epistemicos-cli migrate up`
4. Embedded automatically via `go:embed` (no manual action needed)

**Utility/Helper Functions:**
1. If domain-specific: Add to relevant domain package (e.g., segment classification helper)
2. If infrastructure: Add to platform package (e.g., new log format in `logging/`)
3. If widely reused: Create `internal/util/` package (rare; prefer to scope narrowly)

## Special Directories

**`internal/core/domain/*/testdata/`:**
- Purpose: Real markdown/data samples from actual papers
- Content: Not generated; taken from the ten ingested papers used to validate domain rules
- Why: Tests document which papers exhibit which shapes (e.g., "Table caption above the table, found in Paper A")
- Note: Committed to repo; never generated

**`internal/adapters/secondary/store/migrations/`:**
- Purpose: SQL migration files (database schema evolution)
- Generated: No; handwritten SQL
- Committed: Yes
- Format: `{sequence}_{description}.{up,down}.sql`
  - Sequence: 4-digit, zero-padded (0001, 0002, etc.)
  - up: Create/alter tables, add columns, etc.
  - down: Undo the up migration (drop table, remove column, etc.)
- Execution: Embedded via `go:embed` in `migrate.go`; run at startup by API, manually by CLI `migrate up`

**`deploy/`:**
- Purpose: Deployment configuration
- Contents: Dockerfiles, CI scripts
- Note: Not imported by code; used by CI/CD and local docker-compose

**`.claude/` (excluded from analysis):**
- Purpose: GSD tooling (vendored; not project code)
- Note: Ignore for codebase analysis

**`docs/`:**
- Purpose: Project documentation
- Key file: `FILES.md` — comprehensive file reference

**`.planning/codebase/` (generated):**
- Purpose: Output of `/gsd-map-codebase` — architecture and structure analysis
- Files: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md

## Development Workflow

**Setup:**
1. `git clone ...`
2. `cp .env.example .env` and configure (set `EPISTEMIC_OS_DB_URL`, Mathpix credentials)
3. `make up` — start Postgres via docker-compose
4. `make migrate` — run database migrations

**Local Development:**
1. Run API: `go run ./cmd/epistemicos-api` (listens on :9082)
2. Run CLI: `go run ./cmd/epistemicos-cli <command>`
3. Or build: `make build` → `./bin/epistemicos-{api,cli}`

**Before Push:**
1. `make gate` — runs vet, gofmt check, build, test
2. All tests must pass (`make test`)
3. Code must be formatted (`go fmt ./...`)
4. No vet warnings (`go vet ./...`)

**Code Organization Principles:**
- Core logic independent of infrastructure (testable, swappable)
- Adapters implement ports; don't define new interfaces
- Services orchestrate; don't contain business rules
- Domain packages are leaf nodes (no imports from other packages except stdlib)
- Errors flow up; services and adapters decide how to handle them
- Configuration injected at startup; no global state or singletons

---

*Structure analysis: 2026-08-30*
