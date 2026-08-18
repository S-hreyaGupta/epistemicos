package exhibit

import (
	"os/exec"
	"strings"
	"testing"
)

// The third package to carry this guard, and the reason is the same as segment's:
// extraction must stay deterministic, so nothing here may reach a port or an
// adapter through which a model could be wired in.
//
// The temptation here is specific and worth naming. Table detection is a pile of
// fiddly rules, and "just ask an LLM which of these blocks is a table" is an
// obvious shortcut that would work reasonably well. It would also make the same
// paper yield different tables on different days, with byte offsets that no
// longer reproduce, and the failure would look like a paper that changed rather
// than a system that did.
//
// If a model is ever the right answer here, it belongs behind a port with its
// answer stored and its evidence verified, the way papertype does it. Not inside
// this package.
func TestPackageHasNoPortDependencies(t *testing.T) {
	const pkg = "github.com/EpistemicOS/epistemicos/internal/core/domain/exhibit"

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
				t.Errorf("exhibit must stay deterministic and offline: forbidden dependency %q (matched %q)", dep, bad)
			}
		}
	}
}
