package gateproof

import (
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/platform/gate"
)

// TestGateOrdersPreflightBeforeMigrate is the structural half of D-02, D-03's
// ordering claim: `env-preflight` runs before `migrate` in the `gate`
// target's recipe, so testenv — not store.RunMigrations — is the first
// reporter for an unreachable database or an unset EPISTEMIC_OS_DB_URL. If
// the two were transposed, golang-migrate's unaudited wrapper text becomes
// the first voice and satisfies neither GATE-01 nor GATE-02, and nothing at
// the transposition site would say so.
//
// Why this is checked structurally when 02-02's TestEnvPreflightIsVoiceless
// refused a Makefile-text assertion for a related claim: that refusal (D-07)
// rests on a non-uniform-weakness argument about *output* — the likely decay
// there is a tool inside the step starting to print, which a text assertion
// cannot see. Ordering is a structural claim, not an output one, and
// `make -n gate`'s dry-run expansion is the recipe as Make itself resolved
// it — variables expanded, $(MAKE) recursion shown — rather than the
// Makefile's raw bytes, so that objection does not transfer here.
//
// Why this check is separate from the expensive proofs (D-02): each check
// gets a single reason to fail, so a claim resting on two independent checks
// survives a reword of either. Three nested `make gate` proofs create
// pressure to trim, and if the ordering claim existed only as a side effect
// of an expensive proof it would disappear with it silently. This check
// costs a fraction of a second and performs no nested `make gate`, so it
// survives that trim and the loss becomes visible rather than silent. The
// other leg is PROOF-02's in-run observation that testenv.RequireEnv appears
// in a real nested gate's output at all (D-02b, proof02_test.go) — an effect
// check obtained from a run that happens anyway, at zero extra cost. A
// reader deleting one of these two checks should find this comment naming
// what the claim drops to.
func TestGateOrdersPreflightBeforeMigrate(t *testing.T) {
	gate.SkipIfNested(t)

	// -n is Make's dry run: it prints the recipe as Make resolved it, with
	// variables expanded and $(MAKE) recursion shown, without executing
	// anything. gate.Run rather than gate.Make because the -n flag must
	// precede the target and Make's argv builder only places -s there.
	result := gate.Run(t, []string{"make", "-n", "gate"}, gate.RunOptions{})

	// Guard first: a dry run of a well-formed Makefile exits 0 even when the
	// real recipe would fail, so a non-zero exit here means the expansion
	// itself is broken and the ordering assertion below would be vacuous.
	if result.TimedOut {
		t.Fatalf("make -n gate timed out — the dry-run expansion could not be obtained: %+v", result)
	}
	if result.ExitCode != 0 {
		t.Fatalf("make -n gate exited %d — the dry-run expansion could not be obtained, so the ordering assertion below would be vacuous:\n%s", result.ExitCode, result.Combined)
	}

	preflightIndex := -1
	migrateIndex := -1
	lines := strings.Split(result.Combined, "\n")
	for i, line := range lines {
		line = strings.TrimSuffix(line, "\r")
		if preflightIndex == -1 && strings.Contains(line, "env-preflight") {
			preflightIndex = i
		}
		if migrateIndex == -1 && strings.Contains(line, "migrate") {
			migrateIndex = i
		}
	}

	if preflightIndex == -1 {
		t.Fatalf("make -n gate's expansion contains no line invoking env-preflight:\n%s", result.Combined)
	}
	if migrateIndex == -1 {
		t.Fatalf("make -n gate's expansion contains no line invoking migrate:\n%s", result.Combined)
	}

	// The assertion is a strict ordering comparison, not two presence
	// checks: if the two recipe lines were transposed in the Makefile, this
	// must fail.
	if !(preflightIndex < migrateIndex) {
		t.Fatalf("make -n gate's expansion does not order env-preflight (line %d: %q) before migrate (line %d: %q) — D-03's ordering claim does not hold structurally:\n%s",
			preflightIndex, lines[preflightIndex], migrateIndex, lines[migrateIndex], result.Combined)
	}
}
