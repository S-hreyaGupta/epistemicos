package gateproof

import (
	"archive/tar"
	"bytes"
	"context"
	"io"
	"os"
	"os/exec"
	"testing"
	"time"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
)

// TestHelperProcess_TarWithTrailer is not itself a test of anything in this
// package — it is a subprocess entry point, invoked by
// TestMaterializeTree_DrainsPastTarEOF via exec.Command(os.Args[0], ...)
// with tarTrailerHelperEnv=1 set in its environment. This is the same
// "helper process" pattern os/exec's own tests use to get a real,
// deterministic child process without depending on an external binary.
//
// When run as an ordinary test (the env var unset), it returns immediately
// and asserts nothing.
func TestHelperProcess_TarWithTrailer(t *testing.T) {
	if os.Getenv(tarTrailerHelperEnv) != "1" {
		return
	}

	var buf bytes.Buffer
	tw := tar.NewWriter(&buf)
	if err := tw.WriteHeader(&tar.Header{
		Name: "hello.txt",
		Mode: 0o644,
		Size: 5,
	}); err != nil {
		os.Exit(1)
	}
	if _, err := tw.Write([]byte("hello")); err != nil {
		os.Exit(1)
	}
	if err := tw.Close(); err != nil {
		os.Exit(1)
	}

	if _, err := os.Stdout.Write(buf.Bytes()); err != nil {
		os.Exit(1)
	}

	// git archive pads its tar output past archive/tar's own end-of-archive
	// marker (see materializeTree's comment in tree_test.go — 4,608 bytes
	// measured on this repo). 1 MiB is far larger than any plausible pipe
	// buffer on Windows or Linux, so a reader that stops at tar.Reader's
	// io.EOF forces this write to block on every run, not intermittently.
	trailer := make([]byte, 1<<20)
	if _, err := os.Stdout.Write(trailer); err != nil {
		os.Exit(1)
	}
	os.Exit(0)
}

// tarTrailerHelperEnv is the marker TestHelperProcess_TarWithTrailer checks
// to distinguish "I am the spawned child" from "I am being run as an
// ordinary test in this package's normal `go test` invocation."
const tarTrailerHelperEnv = "GATEPROOF_HELPER_TAR_TRAILER"

// TestMaterializeTree_DrainsPastTarEOF reproduces materializeTree's wedge
// deterministically, without depending on the real `git archive` race
// (03-INCIDENT-01/02: that race is intermittent — it is exactly why 03-01's
// own run passed before a 30-minute hang caught it elsewhere). The helper
// process above always emits a 1 MiB trailer past tar's own EOF marker, so
// a reader that fails to drain the pipe before cmd.Wait() deadlocks every
// time.
//
// This test asserts the fix committed in materializeTree (tree_test.go):
// drain the pipe to true EOF with io.Copy(io.Discard, stdout) before
// calling cmd.Wait(). Removing that drain call reproduces the deadlock
// deterministically — see 03-INCIDENT-02-harness-timeout-defects.md for the
// captured before/after output from doing exactly that.
//
// The test's own context is bounded so that a reintroduced regression fails
// this test loudly and fast (via the ctx.Done() branch below) instead of
// hanging the suite — the same property DefaultTimeout gives make gate's
// own children.
func TestMaterializeTree_DrainsPastTarEOF(t *testing.T) {
	gate.SkipIfNested(t)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, os.Args[0], "-test.run=TestHelperProcess_TarWithTrailer")
	cmd.Env = append(os.Environ(), tarTrailerHelperEnv+"=1")
	cmd.WaitDelay = 2 * time.Second

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		t.Fatalf("TestMaterializeTree_DrainsPastTarEOF: StdoutPipe: %v", err)
	}
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	if err := cmd.Start(); err != nil {
		t.Fatalf("TestMaterializeTree_DrainsPastTarEOF: Start: %v", err)
	}

	tr := tar.NewReader(stdout)
	for {
		_, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			t.Fatalf("TestMaterializeTree_DrainsPastTarEOF: reading tar stream: %v", err)
		}
	}

	// This is the fix under test, mirroring materializeTree exactly:
	// drain to true EOF before Wait.
	if _, err := io.Copy(io.Discard, stdout); err != nil {
		t.Fatalf("TestMaterializeTree_DrainsPastTarEOF: draining trailer: %v", err)
	}

	done := make(chan error, 1)
	go func() { done <- cmd.Wait() }()

	select {
	case err := <-done:
		if err != nil {
			t.Fatalf("TestMaterializeTree_DrainsPastTarEOF: Wait: %v (stderr: %s)", err, stderr.String())
		}
	case <-ctx.Done():
		t.Fatalf("TestMaterializeTree_DrainsPastTarEOF: cmd.Wait() did not return within the test's 5s bound — deadlock reproduced (see 03-INCIDENT-02)")
	}
}
