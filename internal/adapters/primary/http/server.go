// Package http hosts the REST API.
//
// The surface is deliberately small: ingest a PDF, list papers, fetch one.
// There are no analysis endpoints — slot extraction, archetype rules, flags
// and their dismissal belonged to the v2 pipeline and are not part of this
// system. See docs/architecture.md.
package http

import (
	"net/http"

	"github.com/EpistemicOS/epistemicos/internal/core/services/ingest"
	"github.com/EpistemicOS/epistemicos/internal/platform/metrics"
)

// Capabilities advertises which optional subsystems are wired so a client
// can disable controls before the user clicks a no-op button. The shape is
// intentionally narrow — extend by adding fields, not types.
type Capabilities struct {
	MathpixEnabled bool `json:"mathpix_enabled"`
}

// Server bundles dependencies and exposes the http.Handler.
type Server struct {
	ingest       *ingest.Service
	metrics      *metrics.Registry
	capabilities Capabilities
	mux          *http.ServeMux
}

// ServerOption configures the server.
type ServerOption func(*Server)

// WithMetrics attaches a metrics registry. When set, the server exposes
// GET /metrics in Prometheus text format.
func WithMetrics(r *metrics.Registry) ServerOption {
	return func(s *Server) { s.metrics = r }
}

// WithCapabilities sets the capabilities surface returned by
// GET /api/v1/capabilities. A client polls this once on load so it can
// disable controls whose backing service is not wired.
func WithCapabilities(c Capabilities) ServerOption {
	return func(s *Server) { s.capabilities = c }
}

// NewServer constructs a server. Routes are registered here so the list of
// endpoints is grep-able in one place.
func NewServer(ingestSvc *ingest.Service, opts ...ServerOption) *Server {
	s := &Server{
		ingest: ingestSvc,
		mux:    http.NewServeMux(),
	}

	for _, opt := range opts {
		opt(s)
	}

	s.mux.HandleFunc("GET /health", s.handleHealth)
	s.mux.HandleFunc("GET /api/v1/capabilities", s.handleCapabilities)
	s.mux.HandleFunc("POST /api/v1/papers", s.handleCreatePaper)
	s.mux.HandleFunc("GET /api/v1/papers", s.handleListPapers)
	s.mux.HandleFunc("GET /api/v1/papers/{id}", s.handleGetPaper)
	s.mux.HandleFunc("GET /metrics", s.handleMetrics)

	return s
}

// Handler returns the http.Handler. Wrap with middleware (CORS, logging) at
// the caller's discretion.
func (s *Server) Handler() http.Handler {
	return s.mux
}
