// Controls over the startup refusal.
//
// Package main had no test file at all until 18 September 2026, and
// `go test ./...` reported "[no test files]" for it on every run since the
// repository was created. That mattered more than it sounds: the database
// identity preflight was described in docs/db-identity-closure.md as fatal,
// thirteen controls covered preflight.CheckDatabaseIdentity returning not-OK,
// and nothing anywhere covered what the API did with that answer. Changing the
// preflight to a warning, or deleting the call, would have passed every control
// in the repository.
//
// Alex Zamurko's wording on the closure record kept the conditional — a
// disagreement causes a fatal refusal *if the negative control demonstrates
// this*. These are that control.
//
// What they cover and what they do not is stated at the bottom of this file,
// because a control that is read as covering more than it does is the failure
// mode this whole layer keeps finding in itself.
package main

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5"
)

// stubRow returns a fixed identity, or a fixed error, without a server.
type stubRow struct {
	db, user string
	err      error
}

func (r stubRow) Scan(dest ...any) error {
	if r.err != nil {
		return r.err
	}
	if len(dest) != 2 {
		return errors.New("identity query must select exactly two columns")
	}
	*(dest[0].(*string)) = r.db
	*(dest[1].(*string)) = r.user
	return nil
}

type stubQuerier struct {
	row      stubRow
	gotQuery string
}

func (q *stubQuerier) QueryRow(_ context.Context, sql string, _ ...any) pgx.Row {
	q.gotQuery = sql
	return q.row
}

const agreeingDSN = "postgres://epistemicos:secret@localhost:5432/epistemicos?sslmode=disable"

func TestEnsureDatabaseIdentity(t *testing.T) {
	tests := []struct {
		name    string
		dsn     string
		row     stubRow
		wantErr string // substring; empty means startup should continue
	}{
		{
			name: "agreement lets startup continue",
			dsn:  agreeingDSN,
			row:  stubRow{db: "epistemicos", user: "epistemicos"},
		},
		{
			// The one that actually happened, 24 August to 18 September.
			name:    "the mismatch this was written for stops startup",
			dsn:     agreeingDSN,
			row:     stubRow{db: "paperly", user: "paperly"},
			wantErr: "paperly",
		},
		{
			name:    "one half wrong is still wrong",
			dsn:     agreeingDSN,
			row:     stubRow{db: "epistemicos", user: "paperly"},
			wantErr: "paperly",
		},
		{
			// A check that passes when it did not run is worse than no check.
			//
			// The needle is "the query did not run" and not "nothing", which
			// is what it said first. Both refusal messages below contain the
			// word nothing — this one ends "nothing to compare" — so the
			// looser needle passed on either message and the two controls
			// could not tell each other's failure apart. A control that
			// cannot distinguish the case it is named for is the defect this
			// repository keeps finding, and it got in here while writing the
			// controls against it.
			name:    "a server that answers nothing is not agreement",
			dsn:     agreeingDSN,
			row:     stubRow{db: "", user: ""},
			wantErr: "the query did not run",
		},
		{
			name:    "a query that fails stops startup rather than being ignored",
			dsn:     agreeingDSN,
			row:     stubRow{err: errors.New("connection reset")},
			wantErr: "could not ask the server what it is",
		},
		{
			name:    "a connection string naming neither is not agreement",
			dsn:     "postgres://localhost:5432/",
			row:     stubRow{db: "epistemicos", user: "epistemicos"},
			wantErr: "nothing to compare",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			q := &stubQuerier{row: tt.row}
			err := ensureDatabaseIdentity(context.Background(), q, tt.dsn)

			if tt.wantErr == "" {
				if err != nil {
					t.Fatalf("startup should have continued, got refusal: %v", err)
				}
				return
			}
			if err == nil {
				t.Fatalf("startup continued on %q; the API would have served "+
					"while connected to a database other than the one it reports",
					tt.name)
			}
			if !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("refused, but not for the stated reason\n"+
					"  got:  %v\n  want it to mention: %q", err, tt.wantErr)
			}
		})
	}
}

// The refusal has to be reached by asking the server, not by reading the
// connection string twice. A preflight that never queried would agree with
// itself on every deployment and report green for the exact fault it exists to
// catch — which is the shape of B01-F07 and of the original defect here.
func TestEnsureDatabaseIdentityActuallyAsksTheServer(t *testing.T) {
	q := &stubQuerier{row: stubRow{db: "epistemicos", user: "epistemicos"}}
	if err := ensureDatabaseIdentity(context.Background(), q, agreeingDSN); err != nil {
		t.Fatalf("unexpected refusal: %v", err)
	}
	if q.gotQuery == "" {
		t.Fatal("the preflight returned agreement without querying the server")
	}
	if !strings.Contains(q.gotQuery, "current_database") ||
		!strings.Contains(q.gotQuery, "current_user") {
		t.Fatalf("queried something other than the server's own identity: %q", q.gotQuery)
	}
}

// What these do not cover.
//
// They cover the decision: given what the server answered, does startup stop.
// They do not cover the three lines in main() that call fatalf on the error,
// because reaching those means running a process and asserting an exit code,
// and a mismatch that still connects is awkward to construct — the connection
// string determines which database you reach, so in ordinary operation the two
// agree by construction. The fault this guards against arrives through a DSN
// form where the name is not what it appears, or a proxy, and reproducing that
// in a test is a larger piece of work than this.
//
// So the uncovered surface went from "the whole startup decision" to "one
// if-statement", and that residue is named here rather than left for someone to
// discover in the same way this gap was found.
