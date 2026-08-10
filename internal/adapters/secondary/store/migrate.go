package store

import (
	"embed"
	"errors"
	"fmt"
	"strings"

	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/pgx/v5"
	"github.com/golang-migrate/migrate/v4/source/iofs"
)

//go:embed migrations/*.sql
var migrationsFS embed.FS

// RunMigrations applies all up-migrations against the DB at dbURL.
// Safe to call on every startup — golang-migrate is idempotent.
//
// The pgx/v5 migrate driver registers under the "pgx5" scheme, but
// pgxpool expects the standard "postgres://" URL we accept from
// callers. We rewrite the scheme here so both layers are happy with
// the same env variable.
func RunMigrations(dbURL string) error {
	src, err := iofs.New(migrationsFS, "migrations")
	if err != nil {
		return fmt.Errorf("open embedded migrations: %w", err)
	}

	migrateURL := dbURL
	switch {
	case strings.HasPrefix(migrateURL, "postgres://"):
		migrateURL = "pgx5://" + strings.TrimPrefix(migrateURL, "postgres://")
	case strings.HasPrefix(migrateURL, "postgresql://"):
		migrateURL = "pgx5://" + strings.TrimPrefix(migrateURL, "postgresql://")
	}

	m, err := migrate.NewWithSourceInstance("iofs", src, migrateURL)
	if err != nil {
		return fmt.Errorf("new migrator: %w", err)
	}

	if err := m.Up(); err != nil && !errors.Is(err, migrate.ErrNoChange) {
		return fmt.Errorf("apply migrations: %w", err)
	}
	return nil
}

// keep pgx driver registered with golang-migrate
var _ = pgx.Postgres{}
