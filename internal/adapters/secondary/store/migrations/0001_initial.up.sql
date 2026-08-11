-- The papers table: one row per ingested document.

CREATE TABLE IF NOT EXISTS papers (
    id          UUID PRIMARY KEY,
    url         TEXT,
    hash        VARCHAR(64) NOT NULL,
    title       TEXT NOT NULL DEFAULT '',
    status      VARCHAR(32) NOT NULL,
    error       TEXT NOT NULL DEFAULT '',
    markdown    TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT  papers_hash_unique UNIQUE (hash)
);

CREATE INDEX IF NOT EXISTS idx_papers_created_at ON papers (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_papers_status     ON papers (status);
