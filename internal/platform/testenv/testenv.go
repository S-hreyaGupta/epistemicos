// Package testenv is the one place the database-backed tests decide whether
// to skip or fail on an unmet environment condition.
//
// By default, an unmet condition — EPISTEMIC_OS_DB_URL unset, the database
// unreachable, a cross-package fixture unreadable — skips: a developer
// without Docker running still gets a green build for a reason unrelated to
// their change. Setting EPISTEMIC_OS_TEST_REQUIRE_DB to any non-empty value,
// including the string "0", turns each of those skips into a failure that
// names its specific cause. Any non-empty value enables escalation
// deliberately: a typo in the value then errs toward enforcing rather than
// toward a silently vacuous pass, which is the failure direction this
// package exists to remove.
//
// The flag's name is narrower than its reach. It also escalates the
// cross-package fixture prerequisite in Fixture, which is a filesystem
// condition, not a database one. That asymmetry is deliberate for this
// milestone and is queued for review rather than resolved by a rename here,
// because renaming it after Phase 2 and Phase 3 bind to the literal name is
// no longer local to this package.
package testenv

import (
	"context"
	"net/url"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// URLEnv names the environment variable holding the PostgreSQL connection
// string the database-backed tests connect to.
const URLEnv = "EPISTEMIC_OS_DB_URL"

// RequireEnv names the environment variable that, when set to any non-empty
// value, escalates every environment skip in this package to a failure.
const RequireEnv = "EPISTEMIC_OS_TEST_REQUIRE_DB"

// unparseableURLMsg is the entire message emitted when URLEnv is set but its
// value cannot be parsed as a PostgreSQL connection string. It takes no
// arguments and no format verbs: the value and the underlying library error
// are deliberately withheld, because both carry the connection string. This
// is an argument-free constant, not a format string that today happens not
// to be given the DSN — a later edit that wants to add detail has to change
// this constant's type, which is visible in review, instead of adding one
// more verb to an existing Fatalf.
const unparseableURLMsg = URLEnv + " is set, but its value is not a usable PostgreSQL connection string; the value and the underlying library error are deliberately withheld here, since both carry the connection string"

// Required reports whether RequireEnv is set to any non-empty value,
// including "0". Presence-based rather than value-parsed: a typo in the
// value then errs toward enforcing rather than toward a silently vacuous
// pass, which is the failure direction this package exists to remove.
func Required() bool {
	return os.Getenv(RequireEnv) != ""
}

// hostFromURL returns the host component of a PostgreSQL connection string,
// for use in skip and failure messages. It is the only function in this
// package permitted to derive display text from the connection string, and
// it must never return anything drawn from the userinfo component — the
// url.URL.Host field never carries it. Returns the empty string on a parse
// error, and also for a keyword/value DSN (one beginning "host=", for
// example), which parses without producing a URL host.
func hostFromURL(raw string) string {
	parsed, err := url.Parse(raw)
	if err != nil {
		return ""
	}
	return parsed.Host
}

// Pool connects to URLEnv and returns a ready pool, or skips or fails the
// calling test depending on Required(). Every skip-or-fail decision for the
// database-backed tests is made here, in this documented order — the order
// matters, because it is what makes the answer well-defined when more than
// one condition is unsatisfiable at once:
//
//  1. URLEnv unset — fail if Required(), else skip.
//  2. URLEnv set but unparseable — always fail, in both modes. This matches
//     the phase-base classification, where a malformed URL already failed
//     rather than skipped.
//  3. Database unreachable — fail if Required(), else skip.
//
// Fixture, below, is called only after Pool has already returned, so a
// fixture condition can never mask a database condition.
func Pool(t *testing.T) *pgxpool.Pool {
	t.Helper()

	dsn := os.Getenv(URLEnv)
	if dsn == "" {
		if Required() {
			t.Fatalf("%s is not set, and %s is set: escalation is on, so this test cannot be skipped for a missing database URL", URLEnv, RequireEnv)
		}
		t.Skipf("%s is not set; start postgres and export it to run these tests", URLEnv)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		// pgx v5.7.2 redacts only the password on a parse error and echoes
		// everything else in the connection string — scheme, user, host,
		// database name and query — verbatim into err. Forwarding either
		// the raw value or err here would publish the whole DSN minus one
		// field to the CI log, so this branch emits the fixed constant and
		// nothing else, in both modes: a malformed URL already failed
		// (t.Fatalf, not t.Skipf) at the phase base.
		t.Fatal(unparseableURLMsg)
	}

	if err := pool.Ping(ctx); err != nil {
		pool.Close()

		host := hostFromURL(dsn)
		if host == "" {
			host = "<unknown host — " + URLEnv + " did not parse to one>"
		}

		// The Ping error is measured to be built by pgx from the parsed
		// config, not from the raw DSN, and is kept because it carries the
		// dial diagnosis the unreachable-host proof asserts against; the
		// connection string itself is still never interpolated here.
		if Required() {
			t.Fatalf("cannot reach postgres at %s (from %s): %v", host, URLEnv, err)
		}
		t.Skipf("cannot reach postgres at %s (from %s): %v", host, URLEnv, err)
	}

	t.Cleanup(pool.Close)
	return pool
}
