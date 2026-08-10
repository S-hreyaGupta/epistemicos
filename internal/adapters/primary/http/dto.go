package http

import (
	"time"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
)

// CreatePaperRequest is the body of POST /api/v1/papers when ingesting
// by URL. For direct uploads the request is multipart/form-data with a
// "file" field.
type CreatePaperRequest struct {
	URL string `json:"url"`
}

// PaperResponse is the JSON projection of paper.Paper.
//
// Markdown is omitted from list responses to keep them small; the
// detail endpoint (GET /api/v1/papers/{id}) includes it.
type PaperResponse struct {
	ID       string `json:"id"`
	URL      string `json:"url,omitempty"`
	Hash     string `json:"hash"`
	Title    string `json:"title"`
	Status   string `json:"status"`
	Error    string `json:"error,omitempty"`
	Markdown string `json:"markdown,omitempty"`
	// MarkdownHash is the hex SHA-256 of Markdown. Returned alongside it so a
	// consumer can verify the text it received is the text that was stored.
	MarkdownHash string    `json:"markdown_hash,omitempty"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// ErrorResponse is the canonical error envelope.
type ErrorResponse struct {
	Error string `json:"error"`
}

func paperToResponse(p *paper.Paper, includeMarkdown bool) PaperResponse {
	resp := PaperResponse{
		ID:        string(p.ID),
		URL:       p.URL,
		Hash:      string(p.Hash),
		Title:     p.Title,
		Status:    string(p.Status),
		Error:     p.Error,
		CreatedAt: p.CreatedAt,
		UpdatedAt: p.UpdatedAt,
	}
	if includeMarkdown {
		resp.Markdown = p.Markdown
		resp.MarkdownHash = p.MarkdownHash
	}
	return resp
}
