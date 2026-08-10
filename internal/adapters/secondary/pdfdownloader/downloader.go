// Package pdfdownloader fetches PDFs from URLs.
// Lifted from v1 (internal/ingest/adapters/pdf/downloader.go) and
// adapted to the v2 ports.PDFDownloader contract (returns a
// ReadCloser instead of writing to a destination path — the ingest
// service owns the local-file lifecycle).
package pdfdownloader

import (
	"context"
	"fmt"
	"io"
	"net/http"
)

// HTTPDownloader downloads PDFs over HTTP(S).
type HTTPDownloader struct {
	client *http.Client
}

// New returns a downloader using http.DefaultClient.
func New() *HTTPDownloader {
	return &HTTPDownloader{client: http.DefaultClient}
}

// NewWithClient lets callers inject a custom http.Client (timeouts,
// transports, etc.).
func NewWithClient(c *http.Client) *HTTPDownloader {
	if c == nil {
		c = http.DefaultClient
	}
	return &HTTPDownloader{client: c}
}

// Download fetches the URL and returns the response body as a
// ReadCloser. The caller MUST Close the returned reader.
func (d *HTTPDownloader) Download(ctx context.Context, url string) (io.ReadCloser, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	resp, err := d.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("download pdf: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		return nil, fmt.Errorf("unexpected status %d for %s", resp.StatusCode, url)
	}

	return resp.Body, nil
}
