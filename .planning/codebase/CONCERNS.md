# Codebase Concerns

**Analysis Date:** 2026-08-30

## Tech Debt

**Unimplemented Step 9 Pointer Advancement:**
- Issue: Database schema missing `ExtractionRun.current_segmentation_run_id` column, preventing advancement of the specification's §9 pointer chain after segmentation runs
- Files: `internal/adapters/secondary/approved/papers.go:91-95`
- Impact: Step 2 and Step 3 are decoupled; the pointer chain cannot be walked as specified in §9. Subsequent pipeline steps cannot automatically find the current segmentation run
- Fix approach: Add `current_segmentation_run_id` column to `ExtractionRun` table (belongs in Step 2's schema, not Step 3), then implement advancement in the Post method of `papers.go`

**Panic-Based Error Handling in Segment Span Validation:**
- Issue: `SectionNode.Text()` and review context methods panic on out-of-range byte offsets instead of returning errors
- Files: `internal/core/domain/segment/node.go:112-115`, `internal/core/domain/segment/overlay.go` (similar pattern)
- Impact: Process crash if markdown does not match stored hash or offsets are corrupted. Unverified byte offsets from persistent storage become runtime panics instead of recoverable errors
- Fix approach: Return `(string, error)` instead of panicking; let callers decide whether to continue or abort

**Ignored I/O Errors in Mathpix Client:**
- Issue: `io.ReadAll` errors silently ignored when reading error response bodies
- Files: `internal/adapters/secondary/mathpix/client.go:122, 177`
  - Line 122: `b, _ := io.ReadAll(resp.Body)` in upload error path
  - Line 177: `b, _ := io.ReadAll(resp.Body)` in status check error path
- Impact: Partial error responses are returned as complete error messages; debugging becomes harder when network issues truncate error details
- Fix approach: Check and log `io.ReadAll` errors explicitly before including body in error message

**Rate Limiter Goroutine Lifecycle Not Managed:**
- Issue: `security.RateLimit()` starts a cleanup goroutine (`rl.sweep()`) that is never stopped when the server shuts down
- Files: `internal/platform/security/security.go:87`
- Impact: Minor goroutine leak on each server restart; no graceful shutdown coordination with main server shutdown
- Fix approach: Return a context-aware cleaner function or pass a shutdown channel to the RateLimit middleware factory

## Known Bugs

**HTTP Status Code Check Order in Mathpix Result Fetcher:**
- Bug: Status code validated AFTER body is read and may be empty on error
- Files: `internal/adapters/secondary/mathpix/client.go:200-206`
  - Reads entire response body (line 201), checks status (line 205)
  - If status is not 200, body is already consumed but may contain error details
- Trigger: Non-200 response from Mathpix after successful processing
- Workaround: Error message still includes the body; less clean but functional

## Security Considerations

**Configuration Migration Risk:**
- Risk: Rename from `PAPERLY_` to `EPISTEMIC_OS_` environment variable prefix may cause silent misconfiguration
- Files: `internal/platform/config/config.go:16-29, 76-86`
- Current mitigation: Explicit error message when old prefix is detected with `DB_URL` set; prevents silent failure
- Recommendations: Continue validating both prefixes; consider deprecation timeline for legacy prefix

**Permissive CORS Default:**
- Risk: Default `CORSAllowedOrigins = "*"` enables cross-origin requests from any domain in development mode
- Files: `internal/platform/config/config.go:71`, `internal/adapters/primary/http/main.go`
- Current mitigation: Default is explicitly documented as development-only; production must set to actual origin
- Recommendations: Consider warning log on startup when CORS is permissive; document production requirement more prominently

**Missing Input Validation in PDF Downloader:**
- Risk: URL passed to `pdfdownloader.Download()` not validated before HTTP request
- Files: `internal/adapters/secondary/pdfdownloader/downloader.go`
- Current mitigation: HTTP client enforces RFC 3986; malformed URLs fail at network layer
- Recommendations: Validate URL format before network call; log attempts to access private/reserved ranges (127.0.0.1, 10.0.0.0/8, etc.)

## Performance Bottlenecks

**Large Monolithic Functions in Segmentation:**
- Problem: `segment/build.go` contains 772 lines of heading detection and node building logic
- Files: `internal/core/domain/segment/build.go`
- Cause: Multiple concerns mixed: heading detection, title inference, parent linking, heading count tracking, offset computation
- Improvement path: Break into smaller functions with single concerns; current complexity makes optimization and testing harder

**Segmentation Store Write Path Complexity:**
- Problem: `SaveRun()` writes nodes, review tasks, and state in one transaction with multiple INSERT statements per node
- Files: `internal/adapters/secondary/store/segmentation.go:586` (largest file in storage layer)
- Cause: Need to maintain referential integrity across nodes, tasks, and review state; no batching or prepared statements for bulk insert
- Improvement path: Use PostgreSQL COPY for bulk node inserts; profile transaction commit time for large documents (1000+ nodes)

**No Database Connection Pool Tuning:**
- Problem: `pgxpool.New()` uses default pool settings (typically 4-8 connections)
- Files: `cmd/epistemicos-api/main.go:44`, `cmd/epistemicos-cli/classify.go:openPool()`
- Cause: Pool parameters are hardcoded defaults; no ability to tune for deployment scale
- Improvement path: Make `MaxConns`, `MinConns`, and `AcquireTimeout` configurable via environment variables; profile lock contention on store operations

## Fragile Areas

**Agent instrumentation in `.claude/` is unversioned and reverts silently (FINDING-02):**
- Files: `.claude/gsd-core/workflows/review.md` (review-run archive block), `.claude/gsd-core/bin/lib/state.cjs` (any local guard), `.claude/agents/gsd-executor.md` (the executor contract, incl. the `state.sync` call that fixes FINDING-01)
- Why fragile: `.gitignore:29` ignores `.claude/`, so every behavioural modification to the agent tooling lives only on disk in one worktree. It is not reviewable, does not survive recreating the worktree, and **`/gsd-update` reverts it silently** — leaving no trace it existed. Three known instances; this is a class, not coincidences.
- **READ THIS BEFORE CHOOSING A FIX THAT TOUCHES `.claude/`.** It decides the fix's shape, not just its durability: a guard that itself vanishes silently is a fix-shaped object with an undisclosed expiry. FINDING-01's disposition turned on this twice — and there is no fix for FINDING-01 that avoids `.claude/` entirely.
- Safe modification: any `.claude/` change ships with a durable instruction in the TRACKED planning docs **in the same commit**, stating what changed, where, why, and **how to detect it is gone**. Detection matters more than the instruction — an instruction with no detection assumes the next reader notices something invisible.
- Full record: `.planning/phases/02-enforcement-and-a-single-gate-definition/02-FINDING-02-gitignored-instrumentation.md`

**Byte Offset Contracts Without Runtime Validation:**
- Files: `internal/core/domain/segment/node.go:5-27`, all usages in `classify.go` and `overlay.go`
- Why fragile: Every span computation assumes markdown content matches stored hash, but hash is only verified on read, not on every use. A corrupted or mismatched markdown file causes panics deep in processing
- Safe modification: Add hash re-check before accessing `Text()` method in high-stakes paths; document offset trust assumptions in README
- Test coverage: `acceptance_test.go` tests happy path; missing tests for hash mismatch scenarios

**Specification §9 Pointer Chain Dangling:**
- Files: `internal/adapters/secondary/approved/papers.go:18-39` (missing advancement), `internal/core/ports/segmentation.go` (interface assumes §9 chain works)
- Why fragile: Specification requires three-level pointer walk; implementation can only advance first level. Downstream systems depending on §9 chain will fail silently or hang
- Safe modification: Do not build systems assuming §9 chain works until `current_segmentation_run_id` is added and advancement is implemented
- Test coverage: `acceptance_test.go` explicitly documents that §9 pointer chain cannot be tested yet

**HTTP Handler Error Responses Untested:**
- Files: `internal/adapters/primary/http/handlers.go`, `internal/adapters/primary/http/server.go` (no corresponding `*_test.go` files)
- Why fragile: Error handling paths in upload, status check, and result retrieval are not exercised by tests; bugs surface in production
- Safe modification: Add integration tests for HTTP error scenarios (malformed JSON, missing fields, network errors)
- Test coverage: Gap — HTTP layer has zero test coverage

**Markdown Hash Verification Skipped on Empty Hash:**
- Files: `internal/adapters/secondary/approved/papers.go:87`
- Why fragile: If `papers.markdown_hash` is empty string, verification is skipped (`if storedHash != ""`). Silently allows unverified offsets to proceed
- Safe modification: Enforce that hash is either missing (null) or populated; never empty string. Fail fast if hash is missing
- Test coverage: `papers_test.go` should test empty hash rejection

## Scaling Limits

**In-Memory Rate Limiter Bucket Growth:**
- Current capacity: Unbounded map of IP → bucket structs; 10-minute idle timeout
- Limit: At 1000 requests/minute with 1000 unique IPs, the map grows to 1000+ entries. Sweep runs every 2 minutes but may lag during traffic spikes
- Scaling path: Replace in-memory limiter with Redis-backed rate limiting or implement sliding-window counter algorithm with better cleanup guarantees

**Database Transaction Timeout Not Set:**
- Current capacity: Transactions use `context.Background()` passed from callers; no explicit timeout at transaction start
- Limit: Long-running transactions can hold locks indefinitely; no protection against hung database connections
- Scaling path: Wrap all `pool.Begin()` calls with a context timeout (e.g., 30 seconds); let callers override if needed

**PDF Staging Directory No Quota:**
- Current capacity: PDFs downloaded to local disk (`PDFDir`); no size limit or cleanup
- Limit: Unlimited growth; production deployments will eventually exhaust disk
- Scaling path: Add `--cleanup-after N days` option to CLI; implement disk usage monitoring in HTTP handler

## Dependencies at Risk

**Hardcoded Model Versions:**
- Risk: `claude-sonnet-4-5-20250929` hardcoded in three places; model deprecation or API changes break integration
- Files: `internal/adapters/secondary/llmclassify/claude.go:34`, `internal/adapters/secondary/llmsuggest/claude.go:62`
- Impact: If Anthropic deprecates model version, segmentation and role suggestion fail with API error
- Migration plan: Make model name configurable via environment variable; log warnings on startup if using deprecated models

**Mathpix API Version Pinned:**
- Risk: Mathpix v3 API URL hardcoded; no fallback if v3 is deprecated
- Files: `internal/adapters/secondary/mathpix/client.go:22`
- Impact: PDF processing stops working if Mathpix retires v3
- Migration plan: Store API version in config; implement v4 adapter before v3 deprecation

## Missing Critical Features

**No Async Processing for Long-Running Operations:**
- Problem: PDF ingest is fully synchronous — HTTP request blocks until Mathpix conversion completes
- Blocks: Cannot timeout long conversions; cannot queue jobs or prioritize urgent papers
- Blocks: Cannot provide progress feedback during conversion (progress bar, ETA)

**No Audit Trail for Review Decisions:**
- Problem: Review answers are stored but not the reviewer identity, timestamp of decision, or who changed what
- Blocks: Cannot trace who approved a paper; cannot audit for bias or training purposes

**No Rollback or Versioning for Stored Segmentation Results:**
- Problem: Once stored, a run's nodes are immutable; no way to rerun with improved rules or mark prior runs as superseded
- Blocks: Cannot improve rule version without manual data cleanup; users cannot compare old vs new segmentation side-by-side

## Test Coverage Gaps

**No HTTP Adapter Integration Tests:**
- What's not tested: HTTP handlers for `/api/v1/papers` POST/GET, error responses, status codes, header validation
- Files: `internal/adapters/primary/http/handlers.go`, `internal/adapters/primary/http/server.go` (39 lines of untested code)
- Risk: Bugs in HTTP layer surface in production; response serialization errors go undetected
- Priority: High — HTTP is the public API surface; errors here directly impact clients

**No Mathpix Client Error Scenario Tests:**
- What's not tested: Network timeouts, 5xx responses, malformed JSON responses, missing fields in status response
- Files: `internal/adapters/secondary/mathpix/client.go` (227 lines)
- Risk: Silent failures or panics when Mathpix returns unexpected responses
- Priority: High — Mathpix is external dependency; robustness requires testing failure cases

**No Concurrent Segmentation Tests:**
- What's not tested: Multiple concurrent `Segment()` calls; database transaction isolation; race conditions in node building
- Files: `internal/core/services/segmentation/gate.go`, `internal/adapters/secondary/store/segmentation.go`
- Risk: Concurrent runs may corrupt shared state or race on review task assignment
- Priority: Medium — not critical for single-node deployment, but essential before horizontal scaling

**Rate Limiter Edge Cases Untested:**
- What's not tested: Bucket expiry timing, cleanup sweeper under high load, clock skew handling
- Files: `internal/platform/security/security.go` (sweep function, bucket lifetime)
- Risk: Buckets may not expire as expected; sweeper may lag under traffic spike
- Priority: Medium — affects production availability

---

*Concerns audit: 2026-08-30*
