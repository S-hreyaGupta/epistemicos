package logging

import (
	"bytes"
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestCorrelationMiddleware_MintsIDAndEchoesHeader(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewJSONHandler(&buf, nil))

	var seenID string
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		seenID = CorrelationIDFromContext(r.Context())
		w.WriteHeader(http.StatusOK)
	})

	srv := httptest.NewServer(CorrelationMiddleware(logger)(handler))
	defer srv.Close()

	resp, err := http.Get(srv.URL)
	if err != nil {
		t.Fatalf("GET: %v", err)
	}
	defer resp.Body.Close()

	headerID := resp.Header.Get("X-Correlation-ID")
	if headerID == "" {
		t.Errorf("middleware should set X-Correlation-ID")
	}
	if seenID != headerID {
		t.Errorf("context ID (%q) should match header (%q)", seenID, headerID)
	}
	if !strings.Contains(buf.String(), headerID) {
		t.Errorf("access log should mention the correlation ID")
	}
}

func TestCorrelationMiddleware_RespectsInboundID(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewJSONHandler(&buf, nil))
	handler := http.HandlerFunc(func(_ http.ResponseWriter, _ *http.Request) {})
	srv := httptest.NewServer(CorrelationMiddleware(logger)(handler))
	defer srv.Close()

	req, _ := http.NewRequest("GET", srv.URL, nil)
	req.Header.Set("X-Correlation-ID", "upstream-id-123")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("Do: %v", err)
	}
	defer resp.Body.Close()

	if got := resp.Header.Get("X-Correlation-ID"); got != "upstream-id-123" {
		t.Errorf("inbound ID should be threaded through: got %q", got)
	}
}

func TestCorrelationMiddleware_LogsHTTPStatus(t *testing.T) {
	var buf bytes.Buffer
	logger := slog.New(slog.NewJSONHandler(&buf, nil))
	handler := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusTeapot)
	})
	srv := httptest.NewServer(CorrelationMiddleware(logger)(handler))
	defer srv.Close()
	resp, err := http.Get(srv.URL)
	if err != nil {
		t.Fatalf("GET: %v", err)
	}
	defer resp.Body.Close()

	var entry map[string]any
	if err := json.Unmarshal([]byte(strings.TrimSpace(buf.String())), &entry); err != nil {
		t.Fatalf("log decode: %v", err)
	}
	if entry["status"].(float64) != 418 {
		t.Errorf("status: %+v", entry)
	}
}

func TestWithCorrelationID_RoundTrip(t *testing.T) {
	ctx := WithCorrelationID(context.Background(), "abc")
	if got := CorrelationIDFromContext(ctx); got != "abc" {
		t.Errorf("round-trip failed: %q", got)
	}
}
