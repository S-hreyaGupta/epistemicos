// Package store implements PaperStore on top of pgx.
//
// v1 used gorm; v2 uses pgx directly for simpler control and fewer
// dependencies. Migrations are handled by golang-migrate; see
// internal/adapters/secondary/store/migrations.
package store

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// PostgresPaperStore implements ports.PaperStore.
type PostgresPaperStore struct {
	pool *pgxpool.Pool
}

// NewPostgresPaperStore returns a store backed by the given pool.
// The caller owns the pool's lifecycle.
func NewPostgresPaperStore(pool *pgxpool.Pool) *PostgresPaperStore {
	return &PostgresPaperStore{pool: pool}
}

// Save inserts or updates a paper. The unique constraint on hash means
// re-saving content-equal papers updates the existing row.
func (s *PostgresPaperStore) Save(ctx context.Context, p *paper.Paper) error {
	now := time.Now().UTC()
	if p.CreatedAt.IsZero() {
		p.CreatedAt = now
	}
	p.UpdatedAt = now

	_, err := s.pool.Exec(ctx, `
		INSERT INTO papers (id, url, hash, title, status, error, markdown, markdown_hash, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
		ON CONFLICT (id) DO UPDATE SET
			url        = EXCLUDED.url,
			hash       = EXCLUDED.hash,
			title      = EXCLUDED.title,
			status     = EXCLUDED.status,
			error      = EXCLUDED.error,
			markdown   = EXCLUDED.markdown,
			updated_at = EXCLUDED.updated_at,
			markdown_hash = EXCLUDED.markdown_hash
`,
		p.ID, p.URL, p.Hash, p.Title, p.Status, p.Error, p.Markdown, p.MarkdownHash,
		p.CreatedAt, p.UpdatedAt,
	)
	if err != nil {
		return fmt.Errorf("save paper: %w", err)
	}
	return nil
}

// GetByID returns the paper with that ID, or ports.ErrNotFound.
func (s *PostgresPaperStore) GetByID(ctx context.Context, id paper.ID) (*paper.Paper, error) {
	row := s.pool.QueryRow(ctx, baseSelect+`WHERE id = $1`, id)
	return scanPaper(row)
}

// GetByHash returns the paper with the given content hash, or
// ports.ErrNotFound.
func (s *PostgresPaperStore) GetByHash(ctx context.Context, h paper.Hash) (*paper.Paper, error) {
	row := s.pool.QueryRow(ctx, baseSelect+`WHERE hash = $1`, h)
	return scanPaper(row)
}

// List returns papers most-recent-first.
func (s *PostgresPaperStore) List(ctx context.Context) ([]*paper.Paper, error) {
	rows, err := s.pool.Query(ctx, baseSelect+`ORDER BY created_at DESC`)
	if err != nil {
		return nil, fmt.Errorf("list papers: %w", err)
	}
	defer rows.Close()

	var out []*paper.Paper
	for rows.Next() {
		p, err := scanPaper(rows)
		if err != nil {
			return nil, err
		}
		out = append(out, p)
	}
	return out, rows.Err()
}

// UpdateStatus updates only status + error. Used by the ingest service
// to flip a paper to processing, ready, or failed.
func (s *PostgresPaperStore) UpdateStatus(ctx context.Context, id paper.ID, status paper.Status, errMsg string) error {
	_, err := s.pool.Exec(ctx, `
		UPDATE papers SET status = $1, error = $2, updated_at = NOW()
		WHERE id = $3
	`, status, errMsg, id)
	if err != nil {
		return fmt.Errorf("update status: %w", err)
	}
	return nil
}

func (s *PostgresPaperStore) UpdateMarkdown(ctx context.Context, id paper.ID, title, markdown, markdownHash string) error {
	_, err := s.pool.Exec(ctx, `
		UPDATE papers
		   SET title = $1, markdown = $2, markdown_hash = $3,
		       status = $4, error = '', updated_at = NOW()
		 WHERE id = $5
	`, title, markdown, markdownHash, paper.StatusReady, id)
	if err != nil {
		return fmt.Errorf("update markdown: %w", err)
	}
	return nil
}

// row interface lets QueryRow and Rows share scanPaper.
type row interface {
	Scan(dest ...any) error
}

const baseSelect = `
SELECT id, url, hash, title, status, error, markdown, markdown_hash, created_at, updated_at
FROM papers

`

func scanPaper(r row) (*paper.Paper, error) {
	var p paper.Paper
	err := r.Scan(
		&p.ID, &p.URL, &p.Hash, &p.Title, &p.Status, &p.Error, &p.Markdown, &p.MarkdownHash,
		&p.CreatedAt, &p.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ports.ErrNotFound
		}
		return nil, fmt.Errorf("scan paper: %w", err)
	}
	return &p, nil
}
