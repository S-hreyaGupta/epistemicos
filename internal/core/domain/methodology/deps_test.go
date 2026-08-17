package methodology

import (
	"os/exec"
	"strings"
	"testing"
)

// The same structural guard segment carries, for the same reason and one more.
//
// SAME REASON. This package must stay LLM-unreachable, so a determination cannot
// be made non-deterministic by a single wiring line in the composition root.
// There is no ports.MethodologyClassifier to implement and nothing to inject.
//
// ONE MORE. The published method ends in a trained XGBoost model, and the
// obvious way to reach it from Go is a Python sidecar or a CGo binding. Either
// would arrive here as a new dependency. That may one day be the right call —
// but it is a decision about determinism and about a licence the authors have
// not granted, and it should be made deliberately rather than discovered in a
// diff. This test turns it into a conversation.
//
// The guard is a substring test rather than an allowlist, matching segment's,
// and this package currently imports only the standard library.
func TestPackageHasNoPortDependencies(t *testing.T) {
	const pkg = "github.com/EpistemicOS/epistemicos/internal/core/domain/methodology"

	out, err := exec.Command("go", "list", "-deps", pkg).Output()
	if err != nil {
		t.Fatalf("go list -deps %s: %v", pkg, err)
	}

	forbidden := []string{"/internal/core/ports", "/internal/adapters/"}

	for _, dep := range strings.Split(string(out), "\n") {
		dep = strings.TrimSpace(dep)
		if dep == "" {
			continue
		}
		for _, bad := range forbidden {
			if strings.Contains(dep, bad) {
				t.Errorf("methodology must stay LLM-unreachable: forbidden dependency %q (matched %q)", dep, bad)
			}
		}
	}
}
