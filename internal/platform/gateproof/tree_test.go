package gateproof

import (
	"archive/tar"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
)

// materializeTree builds a throwaway copy of HEAD from Go, using only the
// standard library, and returns its root directory.
//
// This is ported deliberately from 02-03-PLAN.md's bash verification
// snippet (mktemp -d; git archive HEAD | tar -x -C), not transcribed: that
// form was vetted as a one-shot plan-verification step, not as per-test
// infrastructure that runs on every gate, in CI, on Windows and Linux. Four
// reasons decided the Go form here:
//
//  1. No build-host dependency. The bash form shells out to an external tar
//     binary; this form needs only archive/tar, so go.mod and go.sum stay
//     byte-unchanged.
//  2. It leaves nothing behind in the repository. The git-native alternative
//     to this approach registers a linked checkout inside .git's own
//     bookkeeping, and a killed test leaves a stale registration that only
//     an explicit prune step clears; a plain temp directory is cleared
//     idempotently by os.RemoveAll.
//  3. The extraction loop is where the traversal and entry-kind guards can
//     live — a shell-out extraction has nowhere to put them. Measured before
//     planning: all 230 tracked files are mode 100644, with zero symlinks
//     and zero executable bits, so the loop below handles exactly regular
//     files and directories and treats anything else as a hard failure.
//  4. `git archive HEAD` is content-deterministic, so the copy compiles
//     against the shared content-addressed GOCACHE and builds warm.
func materializeTree(t *testing.T) string {
	t.Helper()

	root, err := os.MkdirTemp("", "gateproof-*")
	if err != nil {
		t.Fatalf("materializeTree: os.MkdirTemp: %v", err)
	}
	// t.Cleanup, not a bare defer, because a defer does not survive a
	// timeout kill and DefaultTimeout exists because these children can
	// hang. Registered immediately, before any subprocess runs.
	t.Cleanup(func() {
		os.RemoveAll(root)
	})

	cmd := exec.Command("git", "archive", "--format=tar", "HEAD")
	cmd.Dir = gate.RepoRoot(t)

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		t.Fatalf("materializeTree: git archive: StdoutPipe: %v", err)
	}
	var stderr strings.Builder
	cmd.Stderr = &stderr

	if err := cmd.Start(); err != nil {
		t.Fatalf("materializeTree: git archive: Start: %v", err)
	}

	entryCount := 0
	tr := tar.NewReader(stdout)
	for {
		hdr, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			t.Fatalf("materializeTree: reading tar stream: %v", err)
		}

		cleaned := filepath.Clean(hdr.Name)
		if filepath.IsAbs(cleaned) {
			t.Fatalf("materializeTree: archive entry %q has an absolute name — refusing to extract", hdr.Name)
		}
		dest := filepath.Join(root, cleaned)
		if dest != root && !strings.HasPrefix(dest, root+string(os.PathSeparator)) {
			t.Fatalf("materializeTree: archive entry %q resolves outside the temp root — refusing to extract", hdr.Name)
		}

		switch hdr.Typeflag {
		case tar.TypeXGlobalHeader:
			// git archive --format=tar always emits one pax global header
			// entry (conventionally named "pax_global_header") carrying the
			// commit's metadata as an archive-format artifact, not tracked
			// content. archive/tar does not fold this into the following
			// entry the way it does a per-entry pax header, so it must be
			// skipped explicitly rather than treated as an unsupported
			// entry kind.
			continue
		case tar.TypeDir:
			if err := os.MkdirAll(dest, 0o755); err != nil {
				t.Fatalf("materializeTree: MkdirAll %s: %v", dest, err)
			}
		case tar.TypeReg:
			if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
				t.Fatalf("materializeTree: MkdirAll (parent of) %s: %v", dest, err)
			}
			data, err := io.ReadAll(tr)
			if err != nil {
				t.Fatalf("materializeTree: reading entry %q: %v", hdr.Name, err)
			}
			if err := os.WriteFile(dest, data, 0o644); err != nil {
				t.Fatalf("materializeTree: WriteFile %s: %v", dest, err)
			}
		default:
			t.Fatalf("materializeTree: archive entry %q has an unsupported type flag %q — measured before planning that every tracked file is a regular file or a directory; this is a loud failure rather than a quietly different tree", hdr.Name, string(hdr.Typeflag))
		}
		entryCount++
	}

	if err := cmd.Wait(); err != nil {
		t.Fatalf("materializeTree: git archive: Wait: %v (stderr: %s)", err, stderr.String())
	}
	if entryCount == 0 {
		t.Fatalf("materializeTree: git archive HEAD yielded zero entries")
	}

	return root
}

// stripEscalationExport removes the single line in the copy's Makefile that
// declares the gate target's target-scoped escalation export
// (EPISTEMIC_OS_TEST_REQUIRE_ENV, set to make-gate), and fails unless
// exactly one line was removed. The exactly-one check is what stops a
// Makefile reword from silently turning a differential into a comparison of
// two identical trees.
func stripEscalationExport(t *testing.T, root string) {
	t.Helper()

	if root == gate.RepoRoot(t) {
		t.Fatalf("stripEscalationExport: refusing to strip the escalation export from the real repository root — this must operate on a materializeTree copy only")
	}

	makefilePath := filepath.Join(root, "Makefile")
	data, err := os.ReadFile(makefilePath)
	if err != nil {
		t.Fatalf("stripEscalationExport: reading %s: %v", makefilePath, err)
	}

	lines := strings.Split(string(data), "\n")
	var kept []string
	removed := 0
	for _, line := range lines {
		if strings.Contains(line, "gate: export") && strings.Contains(line, "EPISTEMIC_OS_TEST_REQUIRE_ENV") {
			removed++
			continue
		}
		kept = append(kept, line)
	}

	if removed != 1 {
		t.Fatalf("stripEscalationExport: removed %d lines from %s, want exactly 1 — the escalation-export line was not found as expected", removed, makefilePath)
	}

	if err := os.WriteFile(makefilePath, []byte(strings.Join(kept, "\n")), 0o644); err != nil {
		t.Fatalf("stripEscalationExport: writing %s: %v", makefilePath, err)
	}
}

// TestMaterializeTree_Control drives materializeTree and stripEscalationExport
// against their stated behavior: the returned directory holds the repository's
// top-level files and testenv's source, it lives outside the repository root,
// and stripping the escalation export changes only the copy's Makefile —
// never the real one.
func TestMaterializeTree_Control(t *testing.T) {
	gate.SkipIfNested(t)

	realRoot := gate.RepoRoot(t)
	realMakefile := filepath.Join(realRoot, "Makefile")
	before, err := os.ReadFile(realMakefile)
	if err != nil {
		t.Fatalf("TestMaterializeTree_Control: reading real Makefile: %v", err)
	}

	root := materializeTree(t)

	if root == realRoot || strings.HasPrefix(realRoot, root) || strings.HasPrefix(root, realRoot) {
		t.Fatalf("TestMaterializeTree_Control: materialized root %q is not outside the repository root %q", root, realRoot)
	}

	for _, rel := range []string{
		"Makefile",
		"go.mod",
		"go.sum",
		filepath.Join("internal", "platform", "testenv", "testenv.go"),
	} {
		if _, err := os.Stat(filepath.Join(root, rel)); err != nil {
			t.Errorf("TestMaterializeTree_Control: expected %s in materialized tree: %v", rel, err)
		}
	}

	stripEscalationExport(t, root)

	copyMakefile, err := os.ReadFile(filepath.Join(root, "Makefile"))
	if err != nil {
		t.Fatalf("TestMaterializeTree_Control: reading copy's Makefile after strip: %v", err)
	}
	if string(copyMakefile) == string(before) {
		t.Errorf("TestMaterializeTree_Control: stripEscalationExport did not change the copy's Makefile")
	}

	after, err := os.ReadFile(realMakefile)
	if err != nil {
		t.Fatalf("TestMaterializeTree_Control: reading real Makefile after strip: %v", err)
	}
	if string(after) != string(before) {
		t.Fatalf("TestMaterializeTree_Control: the real Makefile changed — stripEscalationExport must never touch the working tree")
	}
}
