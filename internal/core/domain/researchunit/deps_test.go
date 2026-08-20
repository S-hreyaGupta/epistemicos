package researchunit

import (
	"os/exec"
	"strings"
	"testing"
)

// The fourth package with this guard, and here it protects a decision rather than
// a property.
//
// The gate is deterministic BY CHOICE, not by necessity. A model could answer
// "how many studies does this paper report?" quite well, and on the day someone
// wants the ambiguous cases handled the obvious move is to reach for one from
// inside this package.
//
// That would be wrong in a specific way. This gate REFUSES papers. A
// non-deterministic refusal means the same manuscript is accepted on Tuesday and
// rejected on Thursday, with no record of why, and the paper's author is the one
// who has to explain it. When the model is added it goes behind a port with its
// answer stored and its quotes verified, as papertype does — so a refusal can
// always be traced to a specific prompt and a specific reply.
//
// This test is what makes that a conversation instead of a diff.
func TestPackageHasNoPortDependencies(t *testing.T) {
	const pkg = "github.com/EpistemicOS/epistemicos/internal/core/domain/researchunit"

	out, err := exec.Command("go", "list", "-deps", pkg).Output()
	if err != nil {
		t.Fatalf("go list -deps %s: %v", pkg, err)
	}

	forbidden := []string{"/internal/core/ports", "/internal/adapters/", "net/http"}

	for _, dep := range strings.Split(string(out), "\n") {
		dep = strings.TrimSpace(dep)
		if dep == "" {
			continue
		}
		for _, bad := range forbidden {
			if strings.Contains(dep, bad) {
				t.Errorf("researchunit must refuse papers deterministically: forbidden dependency %q (matched %q)", dep, bad)
			}
		}
	}
}
