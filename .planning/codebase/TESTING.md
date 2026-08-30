# Testing Patterns

**Analysis Date:** 2026-08-30

## Test Framework

**Runner:**
- Go's built-in `testing` package (no external test framework)
- Run all tests: `go test ./...`
- Run specific package: `go test ./internal/core/domain/segment`
- Verbose output: `go test -v ./...`
- Coverage: `go test -cover ./...`

**Assertion Library:**
- No external assertion library; use manual comparisons with `if err != nil { t.Fatal(...) }`
- Error matching: `errors.Is(err, sentinel)` for sentinel error types

**Run Commands:**
```bash
go test ./...              # Run all tests
go test -v ./...           # Run with verbose output
go test -run TestName ./...# Run specific test
go test -cover ./...       # Show coverage per package
```

## Test File Organization

**Location:**
- Co-located with source files (e.g., `papers.go` and `papers_test.go` in same directory)
- Test data in `testdata/` subdirectories (e.g., `internal/core/domain/segment/testdata/demo.md`)

**Naming:**
- Test files: `{source}_test.go` (e.g., `classify_test.go`, `papers_test.go`)
- Test functions: `Test{Context}_{Behavior}()` (e.g., `TestClassify_ExactMatch()`, `TestSaveAndGetRun()`)
- Helper functions: `{verb}{noun}()` (e.g., `testPool()`, `loadFixture()`, `insertPaper()`)
- Table-driven test cases: cases stored in `[]struct{}`

**Structure:**
```
internal/
├── core/
│   └── domain/
│       └── segment/
│           ├── classify.go
│           ├── classify_test.go
│           └── testdata/
│               ├── demo.md
│               └── expected.json
└── adapters/
    └── secondary/
        └── store/
            ├── segmentation.go
            ├── segmentation_test.go
            └── (no testdata; uses database)
```

## Test Structure

**Suite Organization:**

Each test package uses these patterns:

1. **Helper functions at top**, marked with `t.Helper()`:
```go
func testPool(t *testing.T) *pgxpool.Pool {
	t.Helper()
	// Helper logic
}

func loadFixture(t *testing.T) []byte {
	t.Helper()
	// Load and validate test data
}
```

2. **Test functions ordered by concern**, not alphabetically:
```go
// Fixture validation first
func TestFixtureIntegrity(t *testing.T) { ... }

// Core behavior tests next
func TestClassify_ExactMatch(t *testing.T) { ... }
func TestClassify_ExactMatchBeatsPhraseScan(t *testing.T) { ... }

// Edge cases and error conditions
func TestClassify_BareContainer(t *testing.T) { ... }

// Integration/fixture-based tests last
func TestClassifyReproducesFixture(t *testing.T) { ... }
```

## Test Patterns

**Pattern: Table-Driven Tests**

Used extensively for cases with multiple inputs and expected outputs:

```go
func TestClassify_ExactMatch(t *testing.T) {
	cases := []struct {
		in   string
		want Role
	}{
		{"abstract", RoleAbstract},
		{"introduction", RoleIntroduction},
		{"results", RoleResults},
	}

	for _, c := range cases {
		t.Run(c.in, func(t *testing.T) {
			got := Classify(c.in)
			if got.Role != c.want {
				t.Errorf("role = %q, want %q", got.Role, c.want)
			}
		})
	}
}
```

**Pattern: Test Helpers with t.Helper()**

All helper functions call `t.Helper()` first to exclude themselves from test output line numbers:

```go
func testPool(t *testing.T) *pgxpool.Pool {
	t.Helper()

	url := os.Getenv("EPISTEMIC_OS_DB_URL")
	if url == "" {
		t.Skip("EPISTEMIC_OS_DB_URL is not set; start postgres and export it to run the store tests")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	pool, err := pgxpool.New(ctx, url)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	return pool
}
```

**Pattern: Skipping Database Tests**

Integration tests skip gracefully when external dependencies are unavailable:

```go
func testPool(t *testing.T) *pgxpool.Pool {
	t.Helper()

	url := os.Getenv("EPISTEMIC_OS_DB_URL")
	if url == "" {
		// Skip message names the variable so silent skips in CI are not mistaken for passes
		t.Skip("EPISTEMIC_OS_DB_URL is not set; start postgres and export it to run these tests")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	pool, err := pgxpool.New(ctx, url)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		t.Skipf("cannot reach postgres at EPISTEMIC_OS_DB_URL: %v", err)
	}

	t.Cleanup(pool.Close)
	return pool
}
```

**Pattern: Fixture Integrity Checks**

Separate tests validate test data before other tests depend on it:

```go
const fixtureSHA256 = "a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e"
const fixtureBytes = 81492

func TestFixtureIntegrity(t *testing.T) {
	src := loadFixture(t)

	// Assert no CRLF (fixture marked -text in .gitattributes)
	for i, b := range src {
		if b == '\r' {
			t.Fatalf("fixture contains a carriage return at byte %d; it must be stored with LF line endings only", i)
		}
	}
}

func loadFixture(t *testing.T) []byte {
	t.Helper()

	src, err := os.ReadFile(filepath.Join("testdata", "demo.md"))
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}

	// Validate file is unchanged
	if len(src) != fixtureBytes {
		t.Fatalf("fixture is %d bytes, want %d — file has been altered", len(src), fixtureBytes)
	}

	sum := sha256.Sum256(src)
	if got := hex.EncodeToString(sum[:]); got != fixtureSHA256 {
		t.Fatalf("fixture SHA-256 is %s, want %s", got, fixtureSHA256)
	}

	return src
}
```

**Pattern: Cleanup with t.Cleanup()**

Tests register cleanup actions that run after the test completes:

```go
func insertPaper(t *testing.T, pool *pgxpool.Pool, status, markdown, storedHash string) string {
	t.Helper()

	id := uuid.NewString()
	_, err := pool.Exec(context.Background(), `
		INSERT INTO papers (id, url, hash, title, status, error, markdown, markdown_hash)
		VALUES ($1, '', $2, '', $3, '', $4, $5)`,
		id, uuid.NewString(), status, markdown, storedHash)
	if err != nil {
		t.Fatalf("insert paper: %v", err)
	}

	// Cleanup registered after insert succeeds
	t.Cleanup(func() {
		_, _ = pool.Exec(context.Background(), `DELETE FROM papers WHERE id = $1`, id)
	})

	return id
}
```

**Pattern: Subtest Organization (t.Run)**

Tests are split into subtests for logical grouping:

```go
func TestClassify_MultiRoleMatch(t *testing.T) {
	// Organized by scenario, not by assertion type
	t.Run("multi_role_case", func(t *testing.T) {
		got := Classify("background and literature review")
		if got.Status != StatusUnresolved {
			t.Fatalf("status = %q, want %q", got.Status, StatusUnresolved)
		}
	})

	t.Run("zero_match_case", func(t *testing.T) {
		got := Classify("structural model")
		if got.Status != StatusUnresolved {
			t.Fatalf("status = %q, want %q", got.Status, StatusUnresolved)
		}
	})
}
```

**Pattern: Error Sentinel Matching**

Errors are compared using `errors.Is()` instead of type assertions:

```go
func TestGet_NotFound(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	_, _, err := src.Get(context.Background(), uuid.NewString())
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ports.ErrNotFound", err)
	}
}
```

## Acceptance Testing

**Specification-Based Tests:**

Tests are written against the specification and named after its sections/acceptance criteria:

```go
// TestAC13_HashMismatchIsRefused — AC-13 acceptance criterion
func TestAC13_HashMismatchIsRefused(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	const markdown = "# A Study Of Things\n\nBody text.\n"
	id := insertPaper(t, pool, "ready", markdown, hashOf("completely different text"))

	_, _, err := src.Get(context.Background(), id)
	if err == nil {
		t.Fatal("the adapter returned markdown whose hash does not match it")
	}
	if !strings.Contains(err.Error(), "hashes to") {
		t.Errorf("error = %q, want it to name the hash mismatch", err)
	}
}

// TestAC13_MatchingHashIsAccepted — Inverse test
func TestAC13_MatchingHashIsAccepted(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	const markdown = "# A Study Of Things\n\nBody text.\n"
	want := hashOf(markdown)
	id := insertPaper(t, pool, "ready", markdown, want)

	gotMarkdown, gotHash, err := src.Get(context.Background(), id)
	if err != nil {
		t.Fatalf("Get: %v", err)
	}
	if gotMarkdown != markdown {
		t.Errorf("markdown = %q, want %q", gotMarkdown, markdown)
	}
}
```

**Fixture-Based Integration Tests:**

Tests reproduce behavior against a complete reference fixture with expected output:

```go
// TestClassifyReproducesFixture — Runs phase 3 over entire fixture
func TestClassifyReproducesFixture(t *testing.T) {
	exp := loadExpected(t)

	for _, want := range exp.SectionNodes {
		if want.NodeKind == "document_title" {
			continue
		}

		t.Run(want.SectionID, func(t *testing.T) {
			_, _, semantic := ParseContainer(StripIdentifiers(Normalize(want.HeadingRaw)))
			got := Classify(semantic)

			if string(got.Role) != derefOrEmpty(want.PrimaryRole) {
				t.Errorf("primary_role = %q, want %q", got.Role, derefOrEmpty(want.PrimaryRole))
			}
		})
	}
}
```

## Test Data

**Location:**
- Fixtures stored in `testdata/` subdirectories
- Example: `internal/core/domain/segment/testdata/demo.md` (reference specification fixture)
- JSON fixtures: `expected.json` storing expected output for reproducibility tests

**Data Management:**
- Fixtures kept with special line-ending handling (marked `-text` in `.gitattributes`)
- Fixtures validated by hash before tests depend on them
- Test-generated database rows cleaned up with `t.Cleanup()`

**Example: Fixture Loading**
```go
func loadExpected(t *testing.T) expectedOutput {
	t.Helper()

	raw, err := os.ReadFile(filepath.Join("testdata", "expected.json"))
	if err != nil {
		t.Fatalf("read expected.json: %v", err)
	}

	var out expectedOutput
	if err := json.Unmarshal(raw, &out); err != nil {
		t.Fatalf("parse expected.json: %v", err)
	}
	if len(out.SectionNodes) == 0 {
		t.Fatal("expected.json contains no SectionNodes")
	}

	return out
}
```

## Coverage

**Requirements:**
- No explicit coverage target enforced
- High coverage expected for domain logic (`internal/core/domain/`)
- Integration tests run against actual PostgreSQL when database is available

**View Coverage:**
```bash
go test -cover ./internal/core/domain/segment/
# Output: ok      github.com/EpistemicOS/epistemicos/internal/core/domain/segment	1.234s	coverage: 92.3% of statements
```

## Test Types

**Unit Tests:**
- Scope: Single function or small logical unit
- Location: `internal/core/domain/` packages
- Example: `TestClassify_ExactMatch()` tests keyword matching logic
- No database; all inputs are parameters or fixtures

**Integration Tests:**
- Scope: Adapter + external dependency (PostgreSQL)
- Location: `internal/adapters/secondary/store/` packages
- Database required; tests skip if `EPISTEMIC_OS_DB_URL` not set
- Example: `TestSaveAndGetRun()` tests round-trip through PostgreSQL

**Acceptance Tests:**
- Scope: Validates specification compliance
- Location: Same package as tested code
- Named after specification sections (e.g., `TestAC13_*`, `TestBuild_Fixture()`)
- Example: `TestAC13_HashMismatchIsRefused()` validates acceptance criterion

**E2E Tests:**
- Not present in this codebase
- Integration with real Mathpix is tested in CLI (manual or deployment verification)

## Common Patterns

**Async Testing / Context Usage:**
```go
func TestSomethingAsync(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	result := make(chan error, 1)
	go func() {
		result <- someAsync(ctx)
	}()

	select {
	case err := <-result:
		if err != nil {
			t.Fatalf("async operation failed: %v", err)
		}
	case <-ctx.Done():
		t.Fatal("timeout waiting for async operation")
	}
}
```

**Error Testing:**
```go
func TestErrorCondition(t *testing.T) {
	_, _, err := someFunction()
	if err == nil {
		t.Fatal("expected error but got nil")
	}
	if !strings.Contains(err.Error(), "expected message") {
		t.Errorf("error = %q, want to contain 'expected message'", err)
	}
}
```

**Round-Trip Testing (Marshal/Unmarshal):**
```go
func TestSaveAndGetRun(t *testing.T) {
	pool := testPool(t)
	s := NewPostgresSegmentationStore(pool)
	ctx := context.Background()

	want := fixtureRun(t)
	cleanup(t, pool, want.ID)

	// Save
	if err := s.SaveRun(ctx, &want); err != nil {
		t.Fatalf("SaveRun: %v", err)
	}

	// Get and compare
	got, err := s.GetRun(ctx, want.ID)
	if err != nil {
		t.Fatalf("GetRun: %v", err)
	}

	if got.ID != want.ID {
		t.Errorf("id = %q, want %q", got.ID, want.ID)
	}
}
```

---

*Testing analysis: 2026-08-30*
