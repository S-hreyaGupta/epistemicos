package store

import (
	"embed"
	"errors"
	"fmt"
	"net/url"
	"strings"

	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/pgx/v5"
	"github.com/golang-migrate/migrate/v4/source/iofs"
)

//go:embed migrations/*.sql
var migrationsFS embed.FS

// unparseableURLMsg is the entire message emitted when NewWithSourceInstance
// fails specifically because the connection string could not be parsed as a
// URL. It takes no arguments and no format verbs: the value and the
// underlying *url.Error are deliberately withheld, since both carry the
// connection string, including any password. This mirrors
// internal/platform/testenv/testenv.go's unparseableURLMsg discipline
// exactly — an argument-free constant, not a format string that today
// happens not to be given the DSN, so a later edit that wants to add detail
// has to change this constant's type, which is visible in review, instead of
// adding one more verb to an existing wrap.
const unparseableURLMsg = "new migrator: connection string is not a usable PostgreSQL URL; the value and the underlying library error are deliberately withheld here, since both carry the connection string"

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
		// A *url.Error from net/url.Parse renders as
		// `fmt.Sprintf("%s %q: %s", op, url, err)` — embedding the raw
		// connection string, including any password, verbatim. That is
		// exactly T-01-01's original defect class (see testenv.go's
		// unparseableURLMsg), so this branch is substituted with an
		// argument-free constant instead of forwarding err. Every other
		// error from NewWithSourceInstance (e.g. pgx's own dial-failure
		// diagnostics, which already redact the password per AR-01) is
		// forwarded unchanged.
		var urlErr *url.Error
		if errors.As(err, &urlErr) {
			return errors.New(unparseableURLMsg)
		}
		return fmt.Errorf("new migrator: %w", err)
	}

	if err := m.Up(); err != nil && !errors.Is(err, migrate.ErrNoChange) {
		return fmt.Errorf("apply migrations: %w", err)
	}
	return nil
}

// keep pgx driver registered with golang-migrate
var _ = pgx.Postgres{}
