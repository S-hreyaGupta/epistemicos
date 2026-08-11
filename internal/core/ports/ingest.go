// Package ports defines the interfaces the core depends on. Adapters
// in internal/adapters/{primary,secondary} implement them.
//
// Each port is small and intentional. Avoid adding methods that only
// one adapter needs — push specialization into the adapter package.
package ports

import (
	"context"
	"io"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
)

// PDFDownloader fetches a PDF from a URL.
//
// Implementations should be idempotent: calling Download for the same
// URL twice should produce equivalent results. The caller owns the
// returned ReadCloser and must Close it.
type PDFDownloader interface {
	Download(ctx context.Context, url string) (io.ReadCloser, error)
}

// MarkdownProcessor turns a PDF into markdown-with-LaTeX. Mathpix is
// the production implementation. The contract is markdown that
// preserves LaTeX expressions; this system does not re-OCR.
type MarkdownProcessor interface {
	// Process consumes a PDF file path and returns (title, markdown).
	// The title is best-effort extracted from the first heading.
	Process(ctx context.Context, pdfPath string) (title string, markdown string, err error)
}

// Hasher computes a content hash for dedupe. MD5 is fine for content
// addressing — it's not used for security.
type Hasher interface {
	HashFile(filePath string) (paper.Hash, error)
	HashBytes(content []byte) paper.Hash
}
