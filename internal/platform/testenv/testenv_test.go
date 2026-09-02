// This file's own tests now touch a database via TestPoolReachesDatabase —
// D-04's accepted cost (a): testenv is the database helper, so its tests
// exercising the thing every other package's tests skip or fail against is
// honest rather than circular.
package testenv

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
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

// TestPoolReachesDatabase is the reachability assertion env-preflight exists
// to run: it calls Pool and then queries through the returned pool, so a
// discarded-but-successful connection cannot pass this test — only a query
// that actually returns a row can. This is D-04's reachability assertion:
// the thing env-preflight runs so that testenv, not migrate, is the first to
// speak when the database is unreachable. It skips when escalation is off
// and no database is reachable, and fails naming the cause when escalation
// is on and it is not — both inherited from Pool's own skip-or-fail
// decision, exercised here rather than reimplemented.
func TestPoolReachesDatabase(t *testing.T) {
	pool := Pool(t)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var got int
	if err := pool.QueryRow(ctx, "SELECT 1").Scan(&got); err != nil {
		t.Fatalf("SELECT 1 through the pool Pool(t) returned: %v", err)
	}
	if got != 1 {
		t.Fatalf("SELECT 1 through the pool Pool(t) returned = %d, want 1", got)
	}
}

// TestEscalationPreamble pins escalationPreamble's rendering across the
// three flag values this plan's failure messages are measured against:
// make-gate (the caller identity make gate sets), "0" (a value a developer
// might mistake for "off"), and "1" (a bare manual export). Every case must
// contain both RequireEnv itself and the value rendered with Go's %q, so a
// reader can distinguish 0 from "0" from " 0".
func TestEscalationPreamble(t *testing.T) {
	cases := []string{"make-gate", "0", "1"}

	for _, value := range cases {
		t.Run(value, func(t *testing.T) {
			t.Setenv(RequireEnv, value)

			got := escalationPreamble()
			if !strings.Contains(got, RequireEnv) {
				t.Fatalf("escalationPreamble() = %q, want it to contain %s", got, RequireEnv)
			}
			want := fmt.Sprintf("%s=%q", RequireEnv, value)
			if !strings.Contains(got, want) {
				t.Fatalf("escalationPreamble() = %q, want it to contain %s", got, want)
			}
		})
	}
}

// TestRenameTripwireMsg drives renameTripwireMsg directly with synthetic
// arguments rather than through the environment — the preambleInvariant
// pattern Phase 1 established — over all four combinations of {legacy set,
// legacy unset} x {current set, current unset}. Only the legacy-set,
// current-unset combination is non-empty. The final row proves the
// no-interpolation property behaviorally: a distinctive token placed in the
// legacyValue position must not appear in the returned message.
func TestRenameTripwireMsg(t *testing.T) {
	cases := []struct {
		name        string
		legacy      string
		current     string
		wantEmpty   bool
		wantContain []string
		wantAbsent  string
	}{
		{name: "both unset", legacy: "", current: "", wantEmpty: true},
		{name: "legacy unset, current set", legacy: "", current: "make-gate", wantEmpty: true},
		{name: "both set", legacy: "1", current: "make-gate", wantEmpty: true},
		{
			name:        "legacy set, current unset",
			legacy:      "1",
			current:     "",
			wantEmpty:   false,
			wantContain: []string{legacyRequireEnv, RequireEnv},
		},
		{
			name:       "legacy set, current unset: legacyValue is never interpolated",
			legacy:     "DSNLEAKCANARY",
			current:    "",
			wantEmpty:  false,
			wantAbsent: "DSNLEAKCANARY",
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := renameTripwireMsg(c.legacy, c.current)
			if c.wantEmpty {
				if got != "" {
					t.Fatalf("renameTripwireMsg(%q, %q) = %q, want empty", c.legacy, c.current, got)
				}
				return
			}
			if got == "" {
				t.Fatalf("renameTripwireMsg(%q, %q) = %q, want non-empty", c.legacy, c.current, got)
			}
			for _, want := range c.wantContain {
				if !strings.Contains(got, want) {
					t.Fatalf("renameTripwireMsg(%q, %q) = %q, want it to contain %q", c.legacy, c.current, got, want)
				}
			}
			if c.wantAbsent != "" && strings.Contains(got, c.wantAbsent) {
				t.Fatalf("renameTripwireMsg(%q, %q) = %q leaked its legacyValue argument %q", c.legacy, c.current, got, c.wantAbsent)
			}
		})
	}
}

// TestRenameTripwireMsg_Control_DetectsTheTripwireCase is the two-step
// negative control this file already uses twice: first assert the empty
// result for a combination that must not trip, then assert the non-empty
// result for the combination that must — so the assertion is demonstrated
// able to distinguish the two rather than merely never failing.
func TestRenameTripwireMsg_Control_DetectsTheTripwireCase(t *testing.T) {
	if got := renameTripwireMsg("1", "make-gate"); got != "" {
		t.Fatalf("negative control broken: renameTripwireMsg(%q, %q) = %q, want empty (both set must not trip)", "1", "make-gate", got)
	}
	if got := renameTripwireMsg("1", ""); got == "" {
		t.Fatalf("negative control broken: renameTripwireMsg(%q, %q) = empty, want non-empty (legacy set/current unset must trip)", "1", "")
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
