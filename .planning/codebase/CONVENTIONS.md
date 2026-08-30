# Coding Conventions

**Analysis Date:** 2026-08-30

## Naming Patterns

**Files:**
- Source: snake_case (e.g., `papers.go`, `classify_test.go`)
- Packages: lowercase, single word (e.g., `segment`, `store`, `http`)
- Test files: suffix with `_test.go` (e.g., `papers_test.go`, `classify_test.go`)

**Functions:**
- Exported: CamelCase starting with uppercase (e.g., `Build()`, `NewRun()`, `Classify()`)
- Unexported: camelCase starting with lowercase (e.g., `testPool()`, `detectHeadings()`, `hashOf()`)
- Test functions: `TestContext_Behavior()` pattern (e.g., `TestClassify_ExactMatch()`, `TestSaveAndGetRun()`)

**Variables:**
- Constants: UPPER_CASE or CamelCase (e.g., `RunProcessing`, `fixtureSHA256`, `maxUploadBytes`)
- Package-level: descriptive names with semantic meaning (e.g., `keywordToRole`, `fixtureSHA256`)
- Interface-driven naming: Verb+Noun pattern (e.g., `PapersSource`, `SegmentationStore`)

**Types:**
- Exported structs: CamelCase (e.g., `Config`, `Run`, `Classification`, `ErrorResponse`)
- Interfaces: Verb+er pattern (e.g., `Hasher`, `Store`) or Noun pattern (e.g., `PapersSource`)
- String type aliases for domain values (e.g., `Role`, `RunStatus`, `ReviewReason`)

## Code Style

**Formatting:**
- Go's standard `gofmt` formatting is enforced (run `go fmt ./...`)
- Import blocks: standard library, then external, then internal (grouped with blank lines)
- Line continuation: idiomatic Go patterns (no excessive line breaks)

**Linting:**
- No external linter enforced explicitly
- Follow Go conventions and idioms strictly
- Error handling: explicit error returns, no silent failures

**Error Handling:**

**Pattern: Explicit Error Returns**
```go
// Always return errors explicitly
func Load() (*Config, error) {
	c := &Config{...}
	if c.DBURL == "" {
		return nil, fmt.Errorf("%sDB_URL is required", EnvPrefix)
	}
	return c, nil
}
```

**Pattern: Sentinel Error Matching**
```go
// Use errors.Is() for error matching, not string comparison
if !errors.Is(err, ports.ErrNotFound) {
	t.Errorf("error = %v, want ports.ErrNotFound", err)
}
```

**Pattern: Error Context in Messages**
```go
// Provide context in error messages for debugging
if os.Getenv(legacyEnvPrefix+"DB_URL") != "" {
	return nil, fmt.Errorf(
		"%sDB_URL is required, but %sDB_URL is set: the prefix was renamed...",
		EnvPrefix, legacyEnvPrefix)
}
```

## Import Organization

**Order:**
1. Standard library imports (fmt, context, os, etc.)
2. External dependencies (github.com/...)
3. Internal project imports (github.com/EpistemicOS/epistemicos/internal/...)

**Path Aliases:**
- Standard library: `stdhttp` for "net/http" when conflicting (e.g., `stdhttp.Server`)
- No aliases needed for most imports; use full paths
- Underscore imports used for side effects (e.g., database drivers)

## Comments

**When to Comment:**
- Every exported function and type must have a comment starting with the name
- Explain the "why" for non-obvious logic, not the "what"
- Document pre-conditions and post-conditions
- Link to specification sections (e.g., "§4 assigns it separately")

**Example: Function Documentation**
```go
// Classify returns the role classification for a heading.
// The classification Status indicates whether the determination is Resolved or Unresolved.
// On Unresolved, Role is empty — see §8's overlay model.
func Classify(heading string) Classification {
```

**Example: Type Documentation**
```go
// Classification is the outcome of §6 steps 4-5 for one heading.
//
// The zero value is not a valid classification. Read Status first: on
// StatusUnresolved, Role is empty and MUST stay empty — see §8's overlay model.
type Classification struct {
	Role Role
	...
}
```

**Comment Style:**
- Use proper English with punctuation
- Multi-paragraph comments use blank lines between paragraphs
- Complex logic gets block comments explaining the algorithm
- Use `// TODO(context):` or `// TODO(phase):` for deferred work (e.g., `// TODO(step9-pointer):`)

## Function Design

**Size:** 
- Functions kept concise; large complex operations broken into smaller helpers
- Handler functions in adapters layer do dispatch, not heavy logic
- Domain logic in core/domain packages

**Parameters:**
- Pass context as first parameter in functions that need it: `func Example(ctx context.Context, ...)`
- Avoid boolean parameters for flags; use structs for options (e.g., `Config` struct with fields)
- Use variadic options pattern for optional configuration (e.g., `WithMetrics()`)

**Return Values:**
- Functions return (value, error) when they can fail
- Explicitly return nil or default values on error paths
- Never use bare returns in packages with error returns (use explicit return values)

## Module Design

**Package-level Documentation:**
```go
// Package config loads runtime configuration from environment variables.
// Kept deliberately small — each field has a default where one is sane.
package config
```

**Exports:**
- Only export what's needed for the package's responsibility
- Unexported helpers and internal state stay lowercase
- Unexported fields in exported structs are kept minimal

**Repository Pattern:**
- Adapter layer packages implement domain ports (interfaces)
- `NewPostgresXyzStore()` creates store implementations
- Stores accept pgxpool.Pool dependency injection

**Middleware Pattern:**
```go
// Middleware chain applied in order
var handler stdhttp.Handler = srv.Handler()
handler = logging.CorrelationMiddleware(logger)(handler)
handler = security.RateLimit(cfg)(handler)
handler = security.SecurityHeaders()(handler)
handler = security.CORS(cfg.Origins)(handler)
```

## Configuration

**Environment Variables:**
- Prefix: `EPISTEMIC_OS_` (was `PAPERLY_` until 2026-08-24, now deprecated)
- Pattern: `EnvPrefix + "KEY_NAME"` for building var names
- Defaults: Provided where sensible, required ones have explicit checks
- Example: `EPISTEMIC_OS_DB_URL` (required), `EPISTEMIC_OS_LISTEN_ADDR` (default `:9082`)

**Configuration Structure:**
```go
type Config struct {
	// Field comments explain purpose and defaults
	DBURL string            // Required
	ListenAddr string       // Default ":9082"
	PDFDir string           // Default "./data/pdfs"
	RateLimitRPM int        // Default 60, 0 disables
}
```

## Error Messages

**Pattern: Context-Rich Messages**
- Include variable name and expected value
- Reference configuration, not just assertions
- Example: `"EPISTEMIC_OS_DB_URL is required"`
- Example: `"fixture SHA-256 is %s, want %s — the length is right but the content is not"`

**Pattern: Structured Logging**
```go
log.Printf("ingest from url failed: %v", err)
// Not: log.Printf("ERROR: something broke")
```

## Constants and Magic Numbers

**Pattern: Named Constants**
```go
const (
	RunProcessing RunStatus = "Processing"
	RunCompleted  RunStatus = "Completed"
)
```

**Pattern: Magic Numbers Named**
```go
const maxUploadBytes = 50 << 20 // 50 MB

// Not: if size > 52428800 {
```

## Time and Context

**Pattern: Explicit Timeouts**
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
```

**Pattern: Graceful Shutdown**
```go
ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
defer cancel()
_ = server.Shutdown(ctx)
```

---

*Convention analysis: 2026-08-30*
