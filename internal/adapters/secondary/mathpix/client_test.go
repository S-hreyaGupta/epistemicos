package mathpix

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestClient_Process_HappyPath exercises the upload → poll → fetch
// sequence against a stubbed Mathpix server. Validates that the
// adapter handles each step in order and returns the extracted title
// and markdown.
func TestClient_Process_HappyPath(t *testing.T) {
	const wantMarkdown = "# A Test Paper\n\nBody text.\n"

	statusCalls := 0

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case r.Method == http.MethodPost && r.URL.Path == "/pdf":
			// Upload.
			if r.Header.Get("app_id") != "test-id" {
				t.Errorf("missing app_id header")
			}
			_ = json.NewEncoder(w).Encode(pdfResponse{PDFID: "pdf-123"})

		case r.Method == http.MethodGet && r.URL.Path == "/pdf/pdf-123":
			// Status. Return completed on the second call to exercise polling.
			statusCalls++
			st := "split"
			if statusCalls >= 2 {
				st = "completed"
			}
			_ = json.NewEncoder(w).Encode(statusResponse{Status: st, PercentDone: 100})

		case r.Method == http.MethodGet && r.URL.Path == "/pdf/pdf-123.md":
			// Result markdown.
			_, _ = w.Write([]byte(wantMarkdown))

		default:
			t.Errorf("unexpected request: %s %s", r.Method, r.URL.Path)
			http.NotFound(w, r)
		}
	}))
	defer srv.Close()

	// Stage a fake PDF file so the multipart upload has something to send.
	dir := t.TempDir()
	pdfPath := filepath.Join(dir, "paper.pdf")
	if err := os.WriteFile(pdfPath, []byte("%PDF-stub"), 0o644); err != nil {
		t.Fatalf("write stub pdf: %v", err)
	}

	c := New("test-id", "test-key").WithBaseURL(srv.URL)
	title, md, err := c.Process(context.Background(), pdfPath)
	if err != nil {
		t.Fatalf("Process: %v", err)
	}
	if title != "A Test Paper" {
		t.Errorf("title: got %q, want %q", title, "A Test Paper")
	}
	if !strings.Contains(md, "Body text.") {
		t.Errorf("markdown body missing; got %q", md)
	}
	if statusCalls < 2 {
		t.Errorf("expected at least 2 status polls, got %d", statusCalls)
	}
}
