// Package preflight performs startup-time validation of external
// service credentials. Catches "MATHPIX_APP_ID is malformed" at boot
// rather than at the first conversion attempt.
//
// Designed to be cheap and non-fatal: probe results are returned to
// the caller (typically main.go), which logs them and adjusts the
// capability surface. A failed probe does not crash the server — the
// affected feature is just advertised as disabled.
package preflight

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// Result is the outcome of a single probe.
type Result struct {
	Service string
	OK      bool
	Reason  string // human-readable detail on failure
}

const probeTimeout = 5 * time.Second

// CheckMathpix verifies the configured Mathpix credentials. Hits the
// /v3/pdf-results endpoint with a clearly-invalid ID; expects 401 if
// the credentials are wrong, 404 if right. Either is acceptable —
// what we want to detect is a missing/malformed credential set, not
// upstream errors.
func CheckMathpix(ctx context.Context, appID, appKey string) Result {
	r := Result{Service: "mathpix"}
	if appID == "" || appKey == "" {
		r.Reason = "MATHPIX_APP_ID or MATHPIX_APP_KEY is empty"
		return r
	}

	probeCtx, cancel := context.WithTimeout(ctx, probeTimeout)
	defer cancel()

	req, err := http.NewRequestWithContext(probeCtx, http.MethodGet, "https://api.mathpix.com/v3/pdf-results/preflight-probe-noop", nil)
	if err != nil {
		r.Reason = fmt.Sprintf("build request: %v", err)
		return r
	}
	req.Header.Set("app_id", appID)
	req.Header.Set("app_key", appKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		r.Reason = fmt.Sprintf("probe call failed: %v", err)
		return r
	}
	defer resp.Body.Close()
	// 401 → bad credentials. 404 → credentials accepted, no such pdf.
	// Anything 2xx-5xx (other than 401) means credentials were processed.
	if resp.StatusCode == http.StatusUnauthorized {
		r.Reason = "Mathpix rejected credentials (401)"
		return r
	}
	r.OK = true
	return r
}

// IdentityQuery asks a Postgres server which database and user the connection
// is actually on. The caller runs it and passes the answer to
// CheckDatabaseIdentity.
const IdentityQuery = "SELECT current_database(), current_user"

// CheckDatabaseIdentity compares the database and user a connection string
// names against the database and user the server reported.
//
// Why this exists. POSTGRES_DB and POSTGRES_USER apply only when the volume is
// first initialised. The prefix rename of 24 August changed the configuration
// from paperly to epistemicos and could not change the already-initialised
// volume, so for three weeks the config said one thing and the server was
// another. Nothing noticed, because nothing compared them: the API had never
// been run under Compose, so the one path where the two would have met was
// never taken.
//
// A mismatch here is not cosmetic. Every migration, every count and every hash
// in a report is attributed to a database named in configuration, and if that
// name is not the database the work happened in, the attribution is wrong in a
// way no later check can recover.
//
// The caller supplies what the server said rather than a handle, because the
// two drivers in this repository have incompatible query signatures and
// unifying them behind an interface would be more machinery than the one line
// it saves. The comparison is the part with judgement in it, and this is that
// part on its own.
func CheckDatabaseIdentity(dsn, gotDB, gotUser string) Result {
	r := Result{Service: "database-identity"}

	wantDB, wantUser, err := parseDSNIdentity(dsn)
	if err != nil {
		r.Reason = fmt.Sprintf("cannot read the configured identity: %v", err)
		return r
	}
	if wantDB == "" && wantUser == "" {
		r.Reason = "the connection string names neither a database nor a user, so there is nothing to compare"
		return r
	}
	if gotDB == "" && gotUser == "" {
		// A blank answer is not agreement. Without this, a failed query whose
		// error the caller swallowed would read as a passing check.
		r.Reason = "the server reported neither a database nor a user; the query did not run"
		return r
	}

	var wrong []string
	if wantDB != "" && wantDB != gotDB {
		wrong = append(wrong, fmt.Sprintf("database: configured %q, connected to %q", wantDB, gotDB))
	}
	if wantUser != "" && wantUser != gotUser {
		wrong = append(wrong, fmt.Sprintf("user: configured %q, connected as %q", wantUser, gotUser))
	}
	if len(wrong) > 0 {
		r.Reason = strings.Join(wrong, "; ")
		return r
	}

	r.OK = true
	return r
}

// parseDSNIdentity pulls the database and user out of a connection string.
// Handles the URL form, postgres://user:pass@host:port/dbname, and the keyword
// form, "user=x dbname=y". Returns empty strings for parts the string does not
// name, which is not an error: a DSN may legitimately rely on environment
// defaults, and reporting a mismatch against a value nobody configured would be
// a false alarm.
func parseDSNIdentity(dsn string) (dbName, user string, err error) {
	if dsn == "" {
		return "", "", fmt.Errorf("empty connection string")
	}

	if strings.HasPrefix(dsn, "postgres://") || strings.HasPrefix(dsn, "postgresql://") {
		u, perr := url.Parse(dsn)
		if perr != nil {
			return "", "", perr
		}
		if u.User != nil {
			user = u.User.Username()
		}
		dbName = strings.TrimPrefix(u.Path, "/")
		// A URL may still override either through query parameters.
		q := u.Query()
		if v := q.Get("dbname"); v != "" {
			dbName = v
		}
		if v := q.Get("user"); v != "" {
			user = v
		}
		return dbName, user, nil
	}

	for _, field := range strings.Fields(dsn) {
		k, v, ok := strings.Cut(field, "=")
		if !ok {
			continue
		}
		switch k {
		case "dbname":
			dbName = v
		case "user":
			user = v
		}
	}
	return dbName, user, nil
}
