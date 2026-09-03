package gate

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
	"time"
)

// errWaitDelaySpawnerEnv marks that this invocation of the test binary
// should play the "spawner" helper-process role for
// TestGateRun_ErrWaitDelayMisclassification (WR-01, 03-REVIEW.md): a
// direct child that exits successfully almost immediately, after starting
// a grandchild that outlives it and keeps holding the inherited
// stdout/stderr pipe open — without the driving ctx ever expiring.
const errWaitDelaySpawnerEnv = "GATE_HELPER_ERRWAITDELAY_SPAWNER"

// errWaitDelayMarkerEnv names the file the spawner writes, as its own
// observable side effect, before starting the grandchild and exiting.
// Its presence is independent proof the process genuinely started and ran
// — regardless of how gate.Run later classifies the outcome — which is
// what makes the pre-fix t.Fatalf("... could not be started") demonstrably
// wrong rather than merely undesirable phrasing.
const errWaitDelayMarkerEnv = "GATE_HELPER_ERRWAITDELAY_MARKER"

// errWaitDelayGrandchildSleepSeconds must comfortably outlast runWaitDelay
// (5s) so the grandchild is still holding the pipe when WaitDelay's forced
// pipe-close fires.
const errWaitDelayGrandchildSleepSeconds = 10

// errWaitDelayDrivingTimeout is deliberately far larger than runWaitDelay
// and than errWaitDelayGrandchildSleepSeconds: this test's entire premise
// is that ctx never expires (ctx.Err() stays nil throughout), and the
// exec.ErrWaitDelay classification fires anyway — because the spawner (the
// direct child) exits successfully on its own almost immediately, which is
// what starts WaitDelay's timer per the stdlib's own doc comment, not
// because the context was ever canceled.
const errWaitDelayDrivingTimeout = 30 * time.Second

// errWaitDelayBoundThreshold discriminates "WaitDelay forced the return at
// ~runWaitDelay (5s)" from "the grandchild's own sleep bounded it instead"
// (errWaitDelayGrandchildSleepSeconds, 10s) or "ctx itself expired"
// (errWaitDelayDrivingTimeout, 30s). It sits strictly between the first and
// the other two.
const errWaitDelayBoundThreshold = 8 * time.Second

// errWaitDelayMarkerPollInterval/Timeout bound the diagnostic goroutine
// that polls for the marker file below. They are independent of gate.Run's
// own timing and exist only to produce an early, plainly-printed
// confirmation that the spawner ran — printed via plain fmt to os.Stderr,
// deliberately not via *testing.T, because a goroutine that keeps calling
// T methods after the main test goroutine has Fatal'd (Goexit'd) produces
// "Log in goroutine after Test has completed" failures. See
// 03-INCIDENT-02-harness-timeout-defects.md's "Two pitfalls" section for a
// worked example of exactly this hazard in a sibling test.
const (
	errWaitDelayMarkerPollInterval = 50 * time.Millisecond
	errWaitDelayMarkerPollTimeout  = 2 * time.Second
)

// TestHelperProcess_ErrWaitDelaySpawner plays WR-01's exact scenario: a
// direct child that starts, does real observable work (writes a marker
// file), and exits 0 promptly — while a grandchild it spawned and never
// waits for survives underneath it, inheriting the same stdout handle
// gate.Run's internal pipe gave this process.
//
// The grandchild is `bash`/`sleep`, mirroring
// TestHelperProcess_WaitDelaySpawner's own documented reasoning
// (harness_waitdelay_test.go): a self-exec'd grandchild surviving past
// this test's own return would hold the compiled test binary's file open
// on Windows and break `go test`'s own cleanup.
//
// Not itself a test of anything in this package — a subprocess entry
// point, invoked only when errWaitDelaySpawnerEnv is set.
func TestHelperProcess_ErrWaitDelaySpawner(t *testing.T) {
	if os.Getenv(errWaitDelaySpawnerEnv) != "1" {
		return
	}

	if marker := os.Getenv(errWaitDelayMarkerEnv); marker != "" {
		if err := os.WriteFile(marker, []byte("spawner ran\n"), 0o644); err != nil {
			os.Exit(1)
		}
	}

	grandchild := exec.Command("bash", "-c", fmt.Sprintf("printf 'grandchild-alive\\n'; sleep %d", errWaitDelayGrandchildSleepSeconds))
	// Inherit the spawner's own stdout/stderr *os.File directly (not a new
	// pipe), so the grandchild holds the SAME underlying handle gate.Run's
	// copier goroutine reads from.
	grandchild.Stdout = os.Stdout
	grandchild.Stderr = os.Stderr
	if err := grandchild.Start(); err != nil {
		os.Exit(1)
	}
	// Deliberately not Wait()-ing for the grandchild. Deliberately NOT
	// sleeping ourselves either, unlike TestHelperProcess_WaitDelaySpawner
	// — this process exits successfully right away. Per the stdlib's own
	// WaitDelay doc comment, WaitDelay's timer starts as soon as Wait
	// observes THIS process has exited, not only when ctx is canceled, so
	// exiting immediately is what reproduces exec.ErrWaitDelay without the
	// driving ctx ever timing out.
	os.Exit(0)
}

// TestGateRun_ErrWaitDelayMisclassification is WR-01's regression test
// (03-REVIEW.md). It proves gate.Run classifies a benign WaitDelay-forced
// completion (exec.ErrWaitDelay, returned while ctx.Err() is nil) as
// TimedOut, rather than falling through to the misleading "could not be
// started" t.Fatalf — for a process that demonstrably DID start (the
// marker file below) and exited successfully on its own.
//
// Falsifiability: verified by temporarily removing the
// `errors.Is(runErr, exec.ErrWaitDelay)` branch from harness.go's Run,
// running this test, and capturing the resulting t.Fatalf firing well
// after the marker-observed print — i.e. after the spawner had plainly
// already started, run, and exited. Both captured outputs (fix removed,
// fix restored) are recorded in 03-INCIDENT-02-harness-timeout-defects.md.
func TestGateRun_ErrWaitDelayMisclassification(t *testing.T) {
	SkipIfNested(t)

	markerDir := t.TempDir()
	marker := filepath.Join(markerDir, "spawner-ran")

	// Poll for the marker file on a goroutine that outlives (or races)
	// gate.Run's own return, and report via plain fmt — not *testing.T —
	// so this print survives even if Run's t.Fatalf Goexits the main test
	// goroutine before Run returns to us.
	observed := make(chan struct{})
	go func() {
		deadline := time.Now().Add(errWaitDelayMarkerPollTimeout)
		for time.Now().Before(deadline) {
			if _, err := os.Stat(marker); err == nil {
				fmt.Fprintf(os.Stderr, "MARKER OBSERVED at %s: spawner process started, wrote its marker, and exited — independent of whatever gate.Run later classifies this call as\n", time.Now().Format(time.RFC3339Nano))
				close(observed)
				return
			}
			time.Sleep(errWaitDelayMarkerPollInterval)
		}
		fmt.Fprintf(os.Stderr, "MARKER NOT OBSERVED within %s\n", errWaitDelayMarkerPollTimeout)
		close(observed)
	}()

	argv := []string{os.Args[0], "-test.run=TestHelperProcess_ErrWaitDelaySpawner"}

	start := time.Now()
	result := Run(t, argv, RunOptions{
		Timeout: errWaitDelayDrivingTimeout,
		Env: []string{
			errWaitDelaySpawnerEnv + "=1",
			errWaitDelayMarkerEnv + "=" + marker,
		},
	})
	elapsed := time.Since(start)

	<-observed // Ensure the diagnostic goroutine's print has flushed.

	if _, err := os.Stat(marker); err != nil {
		t.Fatalf("TestGateRun_ErrWaitDelayMisclassification: marker file missing — spawner did not run as expected: %v", err)
	}

	if !result.TimedOut {
		t.Fatalf("gate.Run: TimedOut = false, want true; result=%+v (elapsed %s)", result, elapsed)
	}
	if elapsed >= errWaitDelayBoundThreshold {
		t.Fatalf("gate.Run: took %s, at or past errWaitDelayBoundThreshold (%s) — WaitDelay-forced ErrWaitDelay did not bound the wait as expected (see 03-INCIDENT-02 WR-01 addendum); result=%+v", elapsed, errWaitDelayBoundThreshold, result)
	}
	if elapsed >= errWaitDelayDrivingTimeout {
		t.Fatalf("gate.Run: took %s, at or past the driving timeout (%s) — ctx expired, which defeats this test's premise that WaitDelay alone forces the outcome", elapsed, errWaitDelayDrivingTimeout)
	}
}
