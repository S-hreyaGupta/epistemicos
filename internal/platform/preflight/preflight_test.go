package preflight

import (
	"strings"
	"testing"
)

// The identity check exists because configuration said `epistemicos` and the
// server was `paperly` for three weeks, and nothing compared them.
//
// Both halves are covered here: reading the configured identity out of a
// connection string, and comparing it with what the server answered. The check
// takes the answer rather than a handle, so the comparison needs no database —
// which is the reason for that shape. Only the one line that runs
// IdentityQuery is left to integration, and main.go is where it lives.
func TestParseDSNIdentity(t *testing.T) {
	cases := []struct {
		name     string
		dsn      string
		wantDB   string
		wantUser string
		wantErr  bool
	}{
		{
			name:     "the URL form this repository uses",
			dsn:      "postgres://epistemicos:epistemicos@localhost:5432/epistemicos?sslmode=disable",
			wantDB:   "epistemicos",
			wantUser: "epistemicos",
		},
		{
			// The exact shape of the three-week mismatch: config naming one
			// database while the volume held another.
			dsn:      "postgres://epistemicos:pw@postgres:5432/epistemicos",
			name:     "config naming epistemicos, as docker-compose.yml did",
			wantDB:   "epistemicos",
			wantUser: "epistemicos",
		},
		{
			name:     "postgresql:// is the same scheme under another name",
			dsn:      "postgresql://u:p@h:5432/d",
			wantDB:   "d",
			wantUser: "u",
		},
		{
			name:     "keyword form",
			dsn:      "host=localhost user=alice dbname=books sslmode=disable",
			wantDB:   "books",
			wantUser: "alice",
		},
		{
			// Query parameters override the path and userinfo, so a DSN can
			// name one database in the path and another in the query. Reading
			// only the path would compare against a value the driver ignores.
			name:     "query parameters win over the path",
			dsn:      "postgres://u:p@h:5432/ignored?dbname=real&user=realuser",
			wantDB:   "real",
			wantUser: "realuser",
		},
		{
			// Not an error. A DSN may rely on PGDATABASE and friends, and
			// reporting a mismatch against a value nobody configured would be
			// a false alarm.
			name:     "names neither part",
			dsn:      "host=localhost sslmode=disable",
			wantDB:   "",
			wantUser: "",
		},
		{
			name:    "empty",
			dsn:     "",
			wantErr: true,
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			db, user, err := parseDSNIdentity(c.dsn)
			if c.wantErr {
				if err == nil {
					t.Fatalf("expected an error for %q, got db=%q user=%q", c.dsn, db, user)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error for %q: %v", c.dsn, err)
			}
			if db != c.wantDB || user != c.wantUser {
				t.Errorf("for %q\n  got  db=%q user=%q\n  want db=%q user=%q",
					c.dsn, db, user, c.wantDB, c.wantUser)
			}
		})
	}
}

func TestCheckDatabaseIdentity(t *testing.T) {
	const dsn = "postgres://epistemicos:pw@localhost:5432/epistemicos"

	t.Run("agreement passes", func(t *testing.T) {
		r := CheckDatabaseIdentity(dsn, "epistemicos", "epistemicos")
		if !r.OK {
			t.Fatalf("matching identity reported a problem: %q", r.Reason)
		}
	})

	// The three-week mismatch exactly: configuration renamed, volume not.
	t.Run("the mismatch this was written for", func(t *testing.T) {
		r := CheckDatabaseIdentity(dsn, "paperly", "paperly")
		if r.OK {
			t.Fatal("configured epistemicos, connected to paperly, reported OK")
		}
		for _, want := range []string{"epistemicos", "paperly", "database", "user"} {
			if !strings.Contains(r.Reason, want) {
				t.Errorf("the reason does not mention %q, so it does not say "+
					"what is wrong: %q", want, r.Reason)
			}
		}
	})

	t.Run("one half wrong is still wrong", func(t *testing.T) {
		if r := CheckDatabaseIdentity(dsn, "epistemicos", "paperly"); r.OK {
			t.Error("right database, wrong user, reported OK")
		}
		if r := CheckDatabaseIdentity(dsn, "paperly", "epistemicos"); r.OK {
			t.Error("wrong database, right user, reported OK")
		}
	})

	// A check that passes when it did not run is worse than no check, because
	// a green result is read as evidence. Both directions of "nothing to
	// compare" must fail rather than pass.
	t.Run("a blank answer is not agreement", func(t *testing.T) {
		r := CheckDatabaseIdentity(dsn, "", "")
		if r.OK {
			t.Fatal("the server reported nothing and the check passed")
		}
		if !strings.Contains(r.Reason, "did not run") {
			t.Errorf("failed, but not for the query not running: %q", r.Reason)
		}
	})

	t.Run("a DSN naming nothing is not agreement", func(t *testing.T) {
		r := CheckDatabaseIdentity("host=localhost sslmode=disable",
			"epistemicos", "epistemicos")
		if r.OK {
			t.Fatal("nothing configured to compare against, and it passed")
		}
	})

	t.Run("an unreadable DSN fails", func(t *testing.T) {
		if r := CheckDatabaseIdentity("", "epistemicos", "epistemicos"); r.OK {
			t.Fatal("empty connection string reported OK")
		}
	})
}
