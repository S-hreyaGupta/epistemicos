// Package ingest contains the ingest use case: take a paper source
// (URL or uploaded PDF), persist it, send it through Mathpix, and store the
// resulting markdown together with its SHA-256.
//
// The hash is computed here, in the same call that writes the markdown, so
// the two cannot diverge. A consumer holding a copy of the text can check
// it against the stored hash before trusting it.
package ingest

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"

	"github.com/google/uuid"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// Service orchestrates the ingest pipeline. It runs synchronously; Mathpix
// conversion dominates the latency and there is no queue in front of it.
type Service struct {
	store      ports.PaperStore
	downloader ports.PDFDownloader
	processor  ports.MarkdownProcessor
	hasher     ports.Hasher
	pdfDir     string
	now        func() time.Time // injectable for tests
}

// New constructs the service. pdfDir is the local directory used to
// stage downloaded PDFs before handing them to the markdown processor.
func New(
	store ports.PaperStore,
	downloader ports.PDFDownloader,
	processor ports.MarkdownProcessor,
	hasher ports.Hasher,
	pdfDir string,
) *Service {
	return &Service{
		store:      store,
		downloader: downloader,
		processor:  processor,
		hasher:     hasher,
		pdfDir:     pdfDir,
		now:        time.Now,
	}
}

// FromURL accepts a paper URL, downloads it, hashes it, dedupes, runs
// Mathpix, and persists the result. Returns the canonical paper —
// either freshly ingested or an existing one matched by content hash.
func (s *Service) FromURL(ctx context.Context, url string) (*paper.Paper, error) {
	if url == "" {
		return nil, fmt.Errorf("url is required")
	}

	body, err := s.downloader.Download(ctx, url)
	if err != nil {
		return nil, fmt.Errorf("download: %w", err)
	}
	defer body.Close()

	return s.fromReader(ctx, url, body)
}

// FromUpload accepts an uploaded PDF reader (e.g. from a multipart
// form). url is empty for direct uploads.
func (s *Service) FromUpload(ctx context.Context, r io.Reader) (*paper.Paper, error) {
	return s.fromReader(ctx, "", r)
}

func (s *Service) fromReader(ctx context.Context, url string, r io.Reader) (*paper.Paper, error) {
	if err := os.MkdirAll(s.pdfDir, 0o755); err != nil {
		return nil, fmt.Errorf("create pdf dir: %w", err)
	}

	// Stage the PDF to a temp file so we can hash and Mathpix-process it.
	tmpPath := filepath.Join(s.pdfDir, "tmp-"+uuid.NewString()+".pdf")
	if err := writeToFile(tmpPath, r); err != nil {
		return nil, err
	}
	// We don't defer-remove because we hash before deciding whether to
	// keep the file. If dedupe finds an existing paper, we discard.

	hash, err := s.hasher.HashFile(tmpPath)
	if err != nil {
		_ = os.Remove(tmpPath)
		return nil, fmt.Errorf("hash: %w", err)
	}

	// Dedupe: if a paper with the same hash already exists, return it.
	if existing, err := s.store.GetByHash(ctx, hash); err == nil {
		_ = os.Remove(tmpPath)
		return existing, nil
	}

	// Persist a pending row so failures are visible.
	p := &paper.Paper{
		ID:        paper.ID(uuid.NewString()),
		URL:       url,
		Hash:      hash,
		Status:    paper.StatusPending,
		CreatedAt: s.now().UTC(),
		UpdatedAt: s.now().UTC(),
	}
	if err := s.store.Save(ctx, p); err != nil {
		_ = os.Remove(tmpPath)
		return nil, err
	}

	// Move the PDF to its canonical resting place.
	finalPath := filepath.Join(s.pdfDir, string(p.ID)+".pdf")
	if err := os.Rename(tmpPath, finalPath); err != nil {
		_ = s.store.UpdateStatus(ctx, p.ID, paper.StatusFailed, fmt.Sprintf("rename pdf: %v", err))
		return nil, fmt.Errorf("rename pdf: %w", err)
	}

	// Convert via Mathpix.
	if err := s.store.UpdateStatus(ctx, p.ID, paper.StatusProcessing, ""); err != nil {
		return nil, err
	}
	title, markdown, err := s.processor.Process(ctx, finalPath)
	if err != nil {
		_ = s.store.UpdateStatus(ctx, p.ID, paper.StatusFailed, fmt.Sprintf("mathpix: %v", err))
		return nil, fmt.Errorf("mathpix: %w", err)
	}

	sum := sha256.Sum256([]byte(markdown))
	markdownHash := hex.EncodeToString(sum[:])

	if err := s.store.UpdateMarkdown(ctx, p.ID, title, markdown, markdownHash); err != nil {
		return nil, err
	}

	// Re-read so caller gets the canonical record.
	return s.store.GetByID(ctx, p.ID)
}

// List returns all ingested papers, most-recent first.
func (s *Service) List(ctx context.Context) ([]*paper.Paper, error) {
	return s.store.List(ctx)
}

// Get returns a single paper by ID.
func (s *Service) Get(ctx context.Context, id paper.ID) (*paper.Paper, error) {
	return s.store.GetByID(ctx, id)
}

func writeToFile(path string, r io.Reader) error {
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("create %s: %w", path, err)
	}
	defer f.Close()
	if _, err := io.Copy(f, r); err != nil {
		return fmt.Errorf("write %s: %w", path, err)
	}
	return nil
}
