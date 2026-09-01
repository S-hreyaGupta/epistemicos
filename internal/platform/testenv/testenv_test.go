package testenv

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestHostFromURL covers the pure host-extraction cases: a full DSN, a DSN
// pointing at a closed port, a keyword/value DSN, the empty string, and a
// malformed string.
func TestHostFromURL(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{
			name: "full DSN with userinfo, port and query",
			in:   "postgres://u:pw@dbhost.example.com:5432/dbname?sslmode=disable",
			want: "dbhost.example.com:5432",
		},
		{
			name: "DSN pointing at a closed port",
			in:   "postgres://u:pw@127.0.0.1:1/nodb?sslmode=disable",
			want: "127.0.0.1:1",
		},
		{
			name: "keyword/value DSN",
			in:   "host=x port=5432 password=pw dbname=db",
			want: "",
		},
		{
			name: "empty string",
			in:   "",
			want: "",
		},
		{
			name: "malformed string",
			in:   "postgres://u:pw@ bad host/db",
			want: "",
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := hostFromURL(c.in)
			if got != c.want {
				t.Fatalf("hostFromURL(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}

// TestHostFromURL_Control_NeverReturnsUserinfo is a two-step negative
// control: it first proves the secret really is present in the raw input
// DSN (so the second assertion could fail), then asserts hostFromURL never
// returns it. An absence assertion that has never been shown able to detect
// a presence proves nothing.
func TestHostFromURL_Control_NeverReturnsUserinfo(t *testing.T) {
	const secret = "DSNLEAKCANARY"
	dsn := "postgres://u:" + secret + "@127.0.0.1:5432/db?sslmode=disable"

	if !strings.Contains(dsn, secret) {
		t.Fatalf("negative control broken: raw input DSN does not contain %q", secret)
	}

	got := hostFromURL(dsn)
	if strings.Contains(got, secret) {
		t.Fatalf("hostFromURL(%q) = %q leaked the userinfo secret %q", dsn, got, secret)
	}
}

// TestUnparseableURLMsg_Control_NoLeak is the same two-step shape against
// unparseableURLMsg, using the database-name leak token this plan's
// acceptance criteria name. It first proves the token would appear in a
// naive rendering that interpolated the DSN, then asserts the real constant
// contains neither the token nor any part of the DSN, and does name
// URLEnv — a message that leaks nothing and says nothing is not an
// improvement.
func TestUnparseableURLMsg_Control_NoLeak(t *testing.T) {
	const secret = "DSNLEAKCANARY"
	dsn := "postgres://u:pw@ bad host/" + secret

	naive := fmt.Sprintf("cannot parse %q: some library error", dsn)
	if !strings.Contains(naive, secret) {
		t.Fatalf("negative control broken: naive rendering does not contain %q", secret)
	}

	if strings.Contains(unparseableURLMsg, secret) {
		t.Fatalf("unparseableURLMsg leaked the token %q: %s", secret, unparseableURLMsg)
	}
	if strings.Contains(unparseableURLMsg, dsn) {
		t.Fatalf("unparseableURLMsg leaked the DSN %q: %s", dsn, unparseableURLMsg)
	}
	if !strings.Contains(unparseableURLMsg, URLEnv) {
		t.Fatalf("unparseableURLMsg does not name %s: %s", URLEnv, unparseableURLMsg)
	}
}

// TestRequired drives RequireEnv directly: unset and empty are false; the
// string "1" and the string "0" are both true, pinning the presence-based
// rule deliberately rather than accidentally.
func TestRequired(t *testing.T) {
	cases := []struct {
		name  string
		unset bool
		value string
		want  bool
	}{
		{name: "unset", unset: true, want: false},
		{name: "empty string", value: "", want: false},
		{name: "string one", value: "1", want: true},
		{name: "string zero", value: "0", want: true},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if c.unset {
				old, existed := os.LookupEnv(RequireEnv)
				if err := os.Unsetenv(RequireEnv); err != nil {
					t.Fatalf("Unsetenv: %v", err)
				}
				t.Cleanup(func() {
					if existed {
						_ = os.Setenv(RequireEnv, old)
					}
				})
			} else {
				t.Setenv(RequireEnv, c.value)
			}

			if got := Required(); got != c.want {
				t.Fatalf("Required() = %v, want %v", got, c.want)
			}
		})
	}
}

// TestFixture_SuccessPath covers only the non-escalated success case:
// reading a file that exists returns its exact bytes. The skip and fail
// branches are not asserted from inside a test — driving a testing.T from
// outside to observe a skip or fail decision is the gate proof, and that is
// PROOF-03 in Phase 3.
func TestFixture_SuccessPath(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "fixture.txt")
	want := []byte("fixture contents\n")

	if err := os.WriteFile(path, want, 0o600); err != nil {
		t.Fatalf("WriteFile: %v", err)
	}

	got := Fixture(t, path)
	if string(got) != string(want) {
		t.Fatalf("Fixture(%q) = %q, want %q", path, got, want)
	}
}
