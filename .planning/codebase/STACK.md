# Technology Stack

**Analysis Date:** 2026-08-30

## Languages

**Primary:**
- Go 1.24.0 - All backend code, API server, CLI tools, and business logic

**Secondary:**
- Markdown - Generated output format from PDF conversion via Mathpix
- SQL - Database schema and migrations

## Runtime

**Environment:**
- Go 1.24.0 compiled binaries
- Docker containers (Alpine 3.21 base image for production deployment)

**Package Manager:**
- Go modules (`go.mod`, `go.sum`)
- Lockfile: `go.sum` (present and committed)

## Frameworks

**Core:**
- Standard library `net/http` - HTTP server and client implementation
- No external web framework (raw stdlib for routing and middleware)

**Database:**
- `github.com/jackc/pgx/v5` v5.7.2 - PostgreSQL driver with connection pooling
- `github.com/golang-migrate/migrate/v4` v4.19.1 - Database schema migrations

**Testing:**
- `github.com/stretchr/testify` v1.10.0 - Test assertions and mocking

**Build/Dev:**
- `make` - Build automation via `Makefile`
- Docker for containerized deployment
- GitHub Actions for CI/CD (`github.com/actions/checkout@v4`, `github.com/actions/setup-go@v5`)

## Key Dependencies

**Critical:**
- `github.com/jackc/pgx/v5` v5.7.2 - PostgreSQL connection and querying. Why: Core persistence layer for all data
- `github.com/golang-migrate/migrate/v4` v4.19.1 - Database migrations. Why: Schema version management and deployment safety
- `github.com/google/uuid` v1.6.0 - UUID generation. Why: Paper and run identifiers throughout the system

**Infrastructure:**
- `github.com/joho/godotenv` v1.5.1 - Environment variable loading from `.env` files
- `github.com/yuin/goldmark` v1.8.5 - Markdown parsing and manipulation
- OpenTelemetry (`go.opentelemetry.io/*`) - Distributed tracing and metrics collection (automatic instrumentation)

**Development:**
- Docker and Docker Compose for local PostgreSQL
- `gofmt` and `go vet` enforced via CI

## Configuration

**Environment:**
- Loaded via `github.com/joho/godotenv` from `.env` file at runtime
- All configuration through environment variables with `EPISTEMIC_OS_` prefix (renamed from `PAPERLY_` on 2026-08-24)
- Legacy prefix detection with helpful error messages for old deployments

**Build:**
- `Dockerfile.api` - Multi-stage build: golang:1.24-alpine for compilation, alpine:3.21 for runtime
- CGO disabled for static binary compilation
- `Makefile` targets: `build-api`, `build-cli`, `build`, `test`, `fmt`, `vet`, `gate`, `migrate`

## Platform Requirements

**Development:**
- Go 1.24.0
- Docker and Docker Compose for local services
- `make` utility
- PostgreSQL 16 (via Docker)

**Production:**
- Docker runtime
- PostgreSQL 16+ database server
- Environment variables: `EPISTEMIC_OS_DB_URL` (required), plus Mathpix and Anthropic API credentials
- Minimum configuration: database connection string
- Optional: Mathpix credentials, rate limiting parameters, CORS origins

**Network:**
- Outbound HTTPS to `api.mathpix.com/v3` (PDF conversion)
- Outbound HTTPS to Anthropic API endpoints (LLM classification and suggestions)
- HTTP/HTTPS for client requests on configurable port (default 9082)

---

*Stack analysis: 2026-08-30*
