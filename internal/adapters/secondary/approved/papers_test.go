package approved

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// testPool connects to PAPERLY_DB_URL, or skips.
//
// Skipping rather than failing keeps a developer without Docker from seeing a
// red build for a reason unrelated to their change. The skip message names the
// variable so a silent skip in CI is not mistaken for a pass.
func testPool(t *testing.T) *pgxpool.Pool {
	t.Helper()

	url := os.Getenv("PAPERLY_DB_URL")
	if url == "" {
		t.Skip("PAPERLY_DB_URL is not set; start postgres and export it to run these tests")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	pool, err := pgxpool.New(ctx, url)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		t.Skipf("cannot reach postgres: %v", err)
	}

	t.Cleanup(pool.Close)
	return pool
}

// insertPaper writes a papers row directly, so a test can construct states the
// ingest service would never produce — including the corrupt one AC-13 is
// about.
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

	t.Cleanup(func() {
		_, _ = pool.Exec(context.Background(), `DELETE FROM papers WHERE id = $1`, id)
	})

	return id
}

func hashOf(s string) string {
	sum := sha256.Sum256([]byte(s))
	return hex.EncodeToString(sum[:])
}

// TestAC13_HashMismatchIsRefused is acceptance criterion AC-13.
//
// It could not be written in internal/core/domain/segment, which sees only text
// going in and sections coming out. The check lives here, so the test does too.
//
// # Why this matters more than it looks
//
// papers.markdown and papers.markdown_hash are written in a single statement, so
// they cannot normally diverge. "Cannot normally" is not a property Step 3 can
// rest on: every byte offset it produces indexes into this exact text. Markdown
// that does not match its recorded hash yields spans that slice the WRONG BYTES
// — and the result is not an error, it is a plausible-looking quotation of a
// paper that says something the authors did not write.
//
// That is why the adapter recomputes rather than trusting. The cost is one
// SHA-256 over text just read from a database; the failure it prevents is a
// confident, wrong quote three phases downstream.
func TestAC13_HashMismatchIsRefused(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	const markdown = "# A Study Of Things\n\nBody text.\n"

	// The corruption: a row whose stored hash belongs to different text. In
	// production this could come from a partial write, a manual UPDATE, or a
	// restored backup that mixed generations.
	id := insertPaper(t, pool, "ready", markdown, hashOf("completely different text"))

	_, _, err := src.Get(context.Background(), id)
	if err == nil {
		t.Fatal("the adapter returned markdown whose hash does not match it; every offset derived from that text would be unverifiable")
	}
	if !strings.Contains(err.Error(), "hashes to") {
		t.Errorf("error = %q, want it to name the hash mismatch", err)
	}
}

// TestAC13_MatchingHashIsAccepted is the other half. A check that refuses
// everything satisfies the test above and is useless.
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
	if gotHash != want {
		t.Errorf("hash = %q, want %q", gotHash, want)
	}
}

// TestAC13_UnconvertedPaperIsRefused covers the §2 precondition as this
// repository implements it.
//
// The specification requires an ExtractionRun with status = Approved. There is
// no such entity here, so 'ready' stands in for it — and 'ready' means only
// that Mathpix finished, not that a human approved anything. Whatever the word
// means, a paper that has NOT reached it must not be segmented, and this is
// what makes that a check rather than an assumption.
func TestAC13_UnconvertedPaperIsRefused(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	const markdown = "# A Study Of Things\n\nBody text.\n"

	for _, status := range []string{"pending", "downloading", "processing", "failed"} {
		t.Run(status, func(t *testing.T) {
			id := insertPaper(t, pool, status, markdown, hashOf(markdown))

			if _, _, err := src.Get(context.Background(), id); err == nil {
				t.Errorf("a paper with status %q was accepted for segmentation", status)
			}
		})
	}
}

// TestAC13_EmptyMarkdownIsRefused guards a state that would otherwise segment
// "successfully" into nothing.
//
// A ready paper with no markdown produces a run with one whole-document node
// covering zero bytes. That is a completed run over an empty document — which
// looks identical to a paper that genuinely had no headings, and is exactly the
// kind of quiet nonsense §10 exists to prevent.
func TestAC13_EmptyMarkdownIsRefused(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	id := insertPaper(t, pool, "ready", "", "")

	if _, _, err := src.Get(context.Background(), id); err == nil {
		t.Fatal("a ready paper with no markdown was accepted")
	}
}

// TestGet_NotFound checks the sentinel so callers can errors.Is rather than
// string-match.
func TestGet_NotFound(t *testing.T) {
	pool := testPool(t)
	src := NewPapersSource(pool)

	_, _, err := src.Get(context.Background(), uuid.NewString())
	if !errors.Is(err, ports.ErrNotFound) {
		t.Errorf("error = %v, want ports.ErrNotFound", err)
	}
}
