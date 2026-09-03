package gate

import (
	"fmt"
	"os"
	"os/exec"
	"testing"
	"time"
)

// waitDelaySpawnerEnv marks that this invocation of the test binary should
// play the "spawner" helper-process role, mirroring the TestHelperProcess_*
// self-exec pattern used elsewhere in this project (see
// internal/platform/gateproof/tree_drain_test.go) to get a real,
// deterministic subprocess tree without depending on a real `make`/`go
// test` invocation.
const waitDelaySpawnerEnv = "GATE_HELPER_WAITDELAY_SPAWNER"

// waitDelayGrandchildSleepSeconds is how long the surviving grandchild
// holds the inherited stdout pipe open, in whole seconds (passed as a
// `sleep` argument — see below for why the grandchild is a plain `sleep`
// rather than another copy of this test binary). It must comfortably
// outlast waitDelayDrivingTimeout + runWaitDelay (the bound a
// correctly-fixed gate.Run should return within — measured ~7s on this
// host).
const waitDelayGrandchildSleepSeconds = 12

// waitDelayDrivingTimeout is the RunOptions.Timeout the driving test passes
// to gate.Run. Measured on this host: a 200ms timeout was too tight — the
// spawner's own process-start latency (loading the Go runtime for a fresh
// test-binary invocation) sometimes exceeds 200ms, so the direct child got
// killed before it finished starting its grandchild at all, and the test
// observed a fast, empty return that looked like a pass but reproduced
// nothing. 2s gives comfortable headroom for process-start latency while
// staying short relative to waitDelayGrandchildSleepSeconds.
const waitDelayDrivingTimeout = 2 * time.Second

// TestHelperProcess_WaitDelaySpawner plays the role of `make`: it starts a
// grandchild (`bash -c "... sleep N"`, not another copy of this test
// binary — see below) that inherits its own stdout/stderr handles — the
// same handles gate.Run's internal pipe gave IT — and then outlives the
// driving test's short Timeout, so ctx cancellation kills THIS process
// (the direct child) while the grandchild survives underneath it, still
// holding the pipe. Kill() has no process group or job object to reach
// through to the grandchild — exactly the platform mechanism
// 03-INCIDENT-02 measured on Windows for make -> go test -> test-binary.
//
// The grandchild is `bash`/`sleep`, the same external-command approach
// TestRunTimesOut already uses in this package, rather than a second
// self-exec of this test binary: a self-exec'd grandchild surviving past
// this test's own return holds the compiled test binary's underlying file
// open on Windows, and `go test` tries to remove/replace that file as part
// of its own post-run cleanup — producing a spurious "Access is denied"
// non-zero exit from the `go test` process despite every test having
// passed. Measured while developing this test. `bash`/`sleep` are not
// files `go test` manages, so no such conflict arises.
//
// Not itself a test of anything in this package — a subprocess entry
// point, invoked only when waitDelaySpawnerEnv is set.
func TestHelperProcess_WaitDelaySpawner(t *testing.T) {
	if os.Getenv(waitDelaySpawnerEnv) != "1" {
		return
	}

	grandchild := exec.Command("bash", "-c", fmt.Sprintf("printf 'grandchild-alive\\n'; sleep %d", waitDelayGrandchildSleepSeconds))
	// Inherit the spawner's own stdout/stderr *os.File directly (not a new
	// pipe), so the grandchild holds the SAME underlying handle gate.Run's
	// copier goroutine reads from.
	grandchild.Stdout = os.Stdout
	grandchild.Stderr = os.Stderr
	if err := grandchild.Start(); err != nil {
		os.Exit(1)
	}
	// Deliberately not Wait()-ing for the grandchild — exactly what `make`
	// does not do for go test's own descendants either.

	// Outlive the driving test's short Timeout, so ctx cancellation kills
	// this process, not the grandchild.
	time.Sleep((waitDelayGrandchildSleepSeconds + 3) * time.Second)
	os.Exit(0)
}

// waitDelayBoundThreshold is the elapsed-time cutoff
// TestGateRun_WaitDelayBoundsGrandchildHang asserts against. A correctly
// bounded gate.Run() returns at waitDelayDrivingTimeout + runWaitDelay
// (measured ~7s on this host); waitDelayGrandchildSleepSeconds (12s) is
// what a gate.Run() WITHOUT WaitDelay set is bounded by instead — the
// grandchild's own finite sleep, not the intended timeout. 9s sits
// strictly between the two, so this single threshold discriminates fixed
// from broken.
const waitDelayBoundThreshold = 9 * time.Second

// TestGateRun_WaitDelayBoundsGrandchildHang proves runWaitDelay is
// reachable: it is what lets gate.Run return with TimedOut=true, within
// waitDelayBoundThreshold, when a grandchild the direct child spawned and
// never waited for survives the direct child's context-triggered kill,
// holding the inherited stdout pipe open. Without runWaitDelay, cmd.Run()
// (which calls Wait() internally) blocks until the grandchild exits on its
// own — waitDelayGrandchildSleepSeconds later, past
// waitDelayBoundThreshold — and the `if ctx.Err() ==
// context.DeadlineExceeded` branch below it is never usefully reached: by
// the time it runs, the entire point of a bounded timeout is already
// defeated.
//
// The call is made directly on this test's own goroutine, not wrapped in a
// driving goroutine + select: the synthetic grandchild's sleep is itself
// finite (waitDelayGrandchildSleepSeconds), so the worst case this test
// can ever take is bounded by that constant regardless of whether the fix
// under test is present — there is no unbounded-hang case to guard against
// with an outer select. Bounding via the synthetic grandchild's own finite
// lifetime is both simpler and safe.
//
// Verified by temporarily removing `cmd.WaitDelay = runWaitDelay` from
// harness.go: this test failed, reporting an elapsed time at
// waitDelayGrandchildSleepSeconds (~12.3s) — at or past
// waitDelayBoundThreshold. Restored and reconfirmed passing at ~7s. Both
// captured outputs are recorded in
// 03-INCIDENT-02-harness-timeout-defects.md.
func TestGateRun_WaitDelayBoundsGrandchildHang(t *testing.T) {
	SkipIfNested(t)

	argv := []string{os.Args[0], "-test.run=TestHelperProcess_WaitDelaySpawner"}

	start := time.Now()
	result := Run(t, argv, RunOptions{
		Timeout: waitDelayDrivingTimeout,
		Env:     []string{waitDelaySpawnerEnv + "=1"},
	})
	elapsed := time.Since(start)

	if !result.TimedOut {
		t.Fatalf("gate.Run: TimedOut = false, want true; result=%+v (elapsed %s)", result, elapsed)
	}
	if elapsed >= waitDelayBoundThreshold {
		t.Fatalf("gate.Run: took %s, at or past waitDelayBoundThreshold (%s) — WaitDelay did not bound the wait (see 03-INCIDENT-02); result=%+v", elapsed, waitDelayBoundThreshold, result)
	}
}
