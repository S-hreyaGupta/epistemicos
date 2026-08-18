package papertype

import (
	"os/exec"
	"strings"
	"testing"
)

// The same structural guard segment and methodology carry, for a reason that is
// almost the opposite of theirs and needs stating plainly.
//
// Their guard exists so no LLM can reach the classification. This package's whole
// purpose is to hold an LLM's answer, so that argument is unavailable — and the
// guard matters more, not less.
//
// What it protects is the SPLIT. The model call is a port, satisfied by an adapter,
// and everything in this package is deterministic: the prompt, the response
// contract, the quote verification, the routing rule. That split is what makes a
// stored verdict re-examinable. A raw response saved two years ago can be re-parsed
// by today's stricter checks, and its quotes re-verified against the same
// manuscript, with no network and no API key. If this package could reach the
// adapter, "re-check the old verdicts" would mean "pay to ask again", and the
// answers would come back different.
//
// The obvious way to lose that is convenience: a Classify() here that calls the
// model itself, because threading a port through a service is tedious. This test
// turns that into a conversation.
func TestPackageHasNoPortDependencies(t *testing.T) {
	const pkg = "github.com/EpistemicOS/epistemicos/internal/core/domain/papertype"

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
			if dep == bad || strings.Contains(dep, bad) {
				t.Errorf("papertype must stay callable with no network: forbidden dependency %q (matched %q)", dep, bad)
			}
		}
	}
}
