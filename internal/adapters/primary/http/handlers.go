package http

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

const maxUploadBytes = 50 << 20 // 50 MB

func (s *Server) handleHealth(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

// handleCapabilities returns which optional subsystems are wired. A client
// polls this once on load and disables controls accordingly — discovering
// that Mathpix is unconfigured by watching an upload fail is noisier.
func (s *Server) handleCapabilities(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, s.capabilities)
}

// handleMetrics serves the Prometheus text exposition format. Returns
// 404 if no registry is attached — keeps the endpoint inert in
// deployments that aren't scraping.
func (s *Server) handleMetrics(w http.ResponseWriter, _ *http.Request) {
	if s.metrics == nil {
		http.NotFound(w, nil)
		return
	}
	w.Header().Set("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
	if err := s.metrics.WriteText(w); err != nil {
		log.Printf("metrics write: %v", err)
	}
}

// handleCreatePaper accepts either a JSON body with a URL or a
// multipart/form-data upload with a "file" field.
func (s *Server) handleCreatePaper(w http.ResponseWriter, r *http.Request) {
	ct := r.Header.Get("Content-Type")
	switch {
	case ct == "application/json":
		s.createFromURL(w, r)
	case len(ct) >= 19 && ct[:19] == "multipart/form-data":
		s.createFromUpload(w, r)
	default:
		writeJSON(w, http.StatusUnsupportedMediaType, ErrorResponse{Error: "expected application/json or multipart/form-data"})
	}
}

func (s *Server) createFromURL(w http.ResponseWriter, r *http.Request) {
	var req CreatePaperRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, ErrorResponse{Error: "invalid JSON body"})
		return
	}
	if req.URL == "" {
		writeJSON(w, http.StatusBadRequest, ErrorResponse{Error: "url is required"})
		return
	}

	p, err := s.ingest.FromURL(r.Context(), req.URL)
	if err != nil {
		log.Printf("ingest from url failed: %v", err)
		writeJSON(w, http.StatusInternalServerError, ErrorResponse{Error: "ingest failed"})
		return
	}
	writeJSON(w, http.StatusCreated, paperToResponse(p, false))
}

func (s *Server) createFromUpload(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseMultipartForm(maxUploadBytes); err != nil {
		writeJSON(w, http.StatusBadRequest, ErrorResponse{Error: "invalid multipart form"})
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		writeJSON(w, http.StatusBadRequest, ErrorResponse{Error: "file field is required"})
		return
	}
	defer file.Close()

	p, err := s.ingest.FromUpload(r.Context(), file)
	if err != nil {
		log.Printf("ingest from upload failed: %v", err)
		writeJSON(w, http.StatusInternalServerError, ErrorResponse{Error: "ingest failed"})
		return
	}
	writeJSON(w, http.StatusCreated, paperToResponse(p, false))
}

func (s *Server) handleListPapers(w http.ResponseWriter, r *http.Request) {
	papers, err := s.ingest.List(r.Context())
	if err != nil {
		log.Printf("list papers failed: %v", err)
		writeJSON(w, http.StatusInternalServerError, ErrorResponse{Error: "list failed"})
		return
	}

	out := make([]PaperResponse, 0, len(papers))
	for _, p := range papers {
		out = append(out, paperToResponse(p, false))
	}
	writeJSON(w, http.StatusOK, out)
}

func (s *Server) handleGetPaper(w http.ResponseWriter, r *http.Request) {
	id := paper.ID(r.PathValue("id"))
	if id == "" {
		writeJSON(w, http.StatusBadRequest, ErrorResponse{Error: "id is required"})
		return
	}

	p, err := s.ingest.Get(r.Context(), id)
	if err != nil {
		if errors.Is(err, ports.ErrNotFound) {
			writeJSON(w, http.StatusNotFound, ErrorResponse{Error: "paper not found"})
			return
		}
		log.Printf("get paper failed: %v", err)
		writeJSON(w, http.StatusInternalServerError, ErrorResponse{Error: "get failed"})
		return
	}
	writeJSON(w, http.StatusOK, paperToResponse(p, true))
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(body); err != nil {
		log.Printf("encode response: %v", err)
	}
}
