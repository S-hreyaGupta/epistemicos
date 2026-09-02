package gate

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// TestNestingDepth drives the pure recursion-depth parser with synthetic
// inputs, per the house pattern testenv.TestRequired and
// TestPreambleInvariant_Control already use in this repository: the rule is
// demonstrated deliberate, not accidental. Unset and "0" are depth 0; "1"
// and "2" parse to their own depth; every malformed value — non-numeric,
// negative, or carrying stray whitespace — is a hard failure naming
// EPISTEMIC_OS_TEST_MAKE_DEPTH and the offending value, never depth 0 (which
// would recurse) and never a silent nested verdict (which would skip
// vacuously).
func TestNestingDepth(t *testing.T) {
	cases := []struct {
		name    string
		raw     string
		want    int
		wantErr bool
	}{
		{name: "unset", raw: "", want: 0},
		{name: "zero", raw: "0", want: 0},
		{name: "one", raw: "1", want: 1},
		{name: "two", raw: "2", want: 2},
		{name: "non-numeric", raw: "abc", wantErr: true},
		{name: "negative", raw: "-1", wantErr: true},
		{name: "trailing space", raw: "1 ", wantErr: true},
		{name: "leading space", raw: " 1", wantErr: true},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got, err := nestingDepth(c.raw)
			if c.wantErr {
				if err == nil {
					t.Fatalf("nestingDepth(%q) = %d, nil; want a non-nil error", c.raw, got)
				}
				if !strings.Contains(err.Error(), DepthEnv) {
					t.Fatalf("nestingDepth(%q) error %q does not name %s", c.raw, err.Error(), DepthEnv)
				}
				if !strings.Contains(err.Error(), c.raw) {
					t.Fatalf("nestingDepth(%q) error %q does not quote the offending value", c.raw, err.Error())
				}
				return
			}
			if err != nil {
				t.Fatalf("nestingDepth(%q) returned unexpected error: %v", c.raw, err)
			}
			if got != c.want {
				t.Fatalf("nestingDepth(%q) = %d, want %d", c.raw, got, c.want)
			}
		})
	}
}

// TestNormalizeElapsed covers both elapsed-time shapes measured on this
// host and confirms every other character is left untouched.
func TestNormalizeElapsed(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{
			name: "per-test parenthesised elapsed",
			in:   "--- PASS: TestFoo (0.01s)",
			want: "--- PASS: TestFoo (ELAPSED)",
		},
		{
			name: "trailing package elapsed",
			in:   "ok\tgithub.com/EpistemicOS/epistemicos/internal/platform/testenv\t2.517s",
			want: "ok\tgithub.com/EpistemicOS/epistemicos/internal/platform/testenv\tELAPSED",
		},
		{
			name: "both in the same line",
			in:   "--- PASS: TestFoo (0.01s)\tok\t2.517s",
			want: "--- PASS: TestFoo (ELAPSED)\tok\tELAPSED",
		},
		{
			name: "no elapsed token present",
			in:   "some ordinary line of output",
			want: "some ordinary line of output",
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := normalizeElapsed(c.in)
			if got != c.want {
				t.Fatalf("normalizeElapsed(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}

// TestExtraLines covers the multiset comparison: a got that is a
// sub-multiset of want (including a duplicated line accounted for by a
// matching duplicate in want) reports no extra lines, and Make's own
// diagnostic voice is dropped before comparing.
func TestExtraLines(t *testing.T) {
	cases := []struct {
		name string
		got  string
		want string
	}{
		{
			name: "identical single line",
			got:  "ok",
			want: "ok",
		},
		{
			name: "got is a sub-multiset of want",
			got:  "a\nb",
			want: "a\nb\nc",
		},
		{
			name: "duplicated line accounted for by a matching duplicate",
			got:  "a\na",
			want: "a\na\nb",
		},
		{
			name: "make's own diagnostic voice is dropped",
			got:  "ok\nmake: *** [Makefile:12: gate] Error 2\nmake[1]: *** [Makefile:5: test] Error 1",
			want: "ok",
		},
		{
			name: "elapsed-time differences do not count as extra",
			got:  "--- PASS: TestFoo (0.02s)",
			want: "--- PASS: TestFoo (0.01s)",
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := extraLines(c.got, c.want)
			if len(got) != 0 {
				t.Fatalf("extraLines(%q, %q) = %v, want empty", c.got, c.want, got)
			}
		})
	}
}

// TestExtraLines_Control_DetectsAnAddedLine is the two-step control proving
// the voicelessness assertion can come back false, per the pattern
// TestHostFromURL_Control_NeverReturnsUserinfo and
// TestUnparseableURLMsg_Control_NoLeak already use in this repository: first
// prove the comparison reports nothing for identical inputs, then prove it
// reports the one line added to one side. Task 3 relies on this comparison;
// this is the proof it can fail before that reliance is placed.
func TestExtraLines_Control_DetectsAnAddedLine(t *testing.T) {
	want := "line one\nline two"

	if extra := extraLines(want, want); len(extra) != 0 {
		t.Fatalf("extraLines(want, want) = %v, want empty — control setup is broken", extra)
	}

	got := want + "\nan extra line the recipe printed"
	extra := extraLines(got, want)
	if len(extra) != 1 || extra[0] != "an extra line the recipe printed" {
		t.Fatalf("extraLines did not detect the added line: got %v", extra)
	}
}

// TestRepoRootFindsGoMod asserts RepoRoot returns a directory that actually
// contains go.mod and the Makefile the harness invokes targets in.
func TestRepoRootFindsGoMod(t *testing.T) {
	root := RepoRoot(t)

	if _, err := os.Stat(filepath.Join(root, "go.mod")); err != nil {
		t.Fatalf("RepoRoot() = %q, but go.mod is not there: %v", root, err)
	}
	if _, err := os.Stat(filepath.Join(root, "Makefile")); err != nil {
		t.Fatalf("RepoRoot() = %q, but Makefile is not there: %v", root, err)
	}
}

// The five tests above drive pure functions with synthetic inputs and spawn
// no subprocess, so none of them calls SkipIfNested — noted here so a
// reader does not conclude the guard was forgotten. The two tests below do
// spawn a child and each calls SkipIfNested(t) as its first statement.

// TestRunIncrementsDepth spawns a child that echoes back the depth marker it
// was given, and asserts the value genuinely observed in the child's own
// environment — not asserted in a comment — is the parent's depth (0, since
// this test itself runs undeclared and SkipIfNested has already passed)
// plus one.
func TestRunIncrementsDepth(t *testing.T) {
	SkipIfNested(t)

	result := Run(t, []string{"bash", "-c", "printf '%s' \"$" + DepthEnv + "\""}, RunOptions{})

	if result.TimedOut {
		t.Fatal("gate.Run: child timed out echoing its depth marker")
	}
	if result.ExitCode != 0 {
		t.Fatalf("gate.Run: child exited %d: %s", result.ExitCode, result.Combined)
	}
	if result.Stdout != "1" {
		t.Fatalf("child observed %s=%q, want \"1\" (parent depth 0, plus one)", DepthEnv, result.Stdout)
	}
}

// TestRunTimesOut drives the DefaultTimeout kill path rather than describing
// it: TestRunTimesOut is named in T-02-07's mitigation as one of three
// controls on a high-rated threat, and asserting TimedOut is false on a
// fast child (as the other tests in this file incidentally do) never
// exercises the timeout branch, the context cancellation, or TimedOut's
// true case. This test proves the per-call Timeout is honored, not merely
// the const: it uses a short 100ms timeout against a several-second sleep,
// and asserts the whole call returned in well under DefaultTimeout.
func TestRunTimesOut(t *testing.T) {
	SkipIfNested(t)

	start := time.Now()
	result := Run(t, []string{"bash", "-c", "sleep 5"}, RunOptions{Timeout: 100 * time.Millisecond})
	elapsed := time.Since(start)

	if !result.TimedOut {
		t.Fatalf("gate.Run: TimedOut = false, want true (child slept 5s against a 100ms timeout); result=%+v", result)
	}
	if result.ExitCode == 0 {
		t.Fatalf("gate.Run: ExitCode = 0 on a timed-out child, want non-zero; result=%+v", result)
	}
	if elapsed >= DefaultTimeout {
		t.Fatalf("gate.Run: took %s, at or over DefaultTimeout (%s) — the per-call Timeout was not honored", elapsed, DefaultTimeout)
	}
}
