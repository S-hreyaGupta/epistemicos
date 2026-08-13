package segment

import (
	"os/exec"
	"strings"
	"testing"
)

// The determinism boundary around this package is STRUCTURAL, and this test is
// what makes it executable rather than conventional: internal/core/domain/segment
// must never gain a dependency that could carry an LLM call, so segmentation
// cannot be turned non-deterministic by a single wiring line in the composition
// root. There is no ports.RoleClassifier interface to implement and nothing to
// inject, and this test is what keeps that true.
//
// Read this before changing the test:
//
//   - It is the FIRST executable architecture guard in this repository. The
//     hexagonal direction ("core packages never import from adapters/",
//     CONVENTIONS.md Module Design) was previously maintained by convention and
//     code review alone — there are no other import-guard tests and no build
//     tags anywhere in this codebase. There is no precedent file to compare
//     this one against, so it is written to fail loudly and readably instead.
//   - exec.Command appears in no other _test.go in this repository. That is
//     deliberate, not an oversight. "go list -deps" reports the full TRANSITIVE
//     import set, which is the only thing that catches a violation introduced
//     three packages away. Do not "simplify" this into a scan of this
//     directory's own import blocks — that would catch direct imports only.
//   - The match is a substring test against two path fragments rather than an
//     allowlist. That is deliberate too: it lets github.com/yuin/goldmark pass
//     without any listing. goldmark is a considered exception — pure Go, no
//     transitive dependencies, no I/O — and the property that is load-bearing
//     here is that no port and no adapter is REACHABLE, not that the package
//     has zero third-party imports. Note that internal/core/domain/archetype/*
//     already imports github.com/google/uuid, so CLAUDE.md's claim that the
//     core domain has zero external dependencies was already inaccurate before
//     this package existed.
func TestPackageHasNoPortDependencies(t *testing.T) {
	const pkg = "github.com/EpistemicOS/epistemicos/internal/core/domain/segment"

	out, err := exec.Command("go", "list", "-deps", pkg).Output()
	if err != nil {
		t.Fatalf("go list -deps %s: %v", pkg, err)
	}

	// Any port is an interface an LLM adapter could satisfy; any adapter may be
	// an LLM client outright. Either one reaching this package would put a
	// non-deterministic component inside the classification path.
	forbidden := []string{"/internal/core/ports", "/internal/adapters/"}

	for _, dep := range strings.Split(string(out), "\n") {
		dep = strings.TrimSpace(dep)
		if dep == "" {
			continue
		}
		for _, bad := range forbidden {
			if strings.Contains(dep, bad) {
				t.Errorf("segment must stay LLM-unreachable: forbidden dependency %q (matched %q)", dep, bad)
			}
		}
	}
}
