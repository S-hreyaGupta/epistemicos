package segment

import "testing"

// TestNewRun_Fixture checks the run-level fields §15 predicts, and that task
// generation produces exactly the five tasks expected.json records.
func TestNewRun_Fixture(t *testing.T) {
	md := loadFixture(t)
	exp := loadExpected(t)

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := NewRun(doc, "test-run", fixtureSHA256)

	if run.Status != RunCompleted {
		t.Errorf("status = %q, want %q", run.Status, RunCompleted)
	}
	if run.StructuralRuleVersion != "2.6" {
		t.Errorf("structural_rule_version = %q, want \"2.6\"", run.StructuralRuleVersion)
	}
	if run.DocumentTitleStatus != TitleIdentified {
		t.Errorf("title status = %q, want %q", run.DocumentTitleStatus, TitleIdentified)
	}
	if run.DocumentTitleMethod != MethodSingletonH1 {
		t.Errorf("title method = %q, want %q", run.DocumentTitleMethod, MethodSingletonH1)
	}
	if run.DocumentTitleSourceLevel != 1 {
		t.Errorf("title source level = %d, want 1", run.DocumentTitleSourceLevel)
	}
	if run.DocumentTitleText != exp.SectionNodes[0].HeadingRaw {
		t.Errorf("title text = %q, want %q", run.DocumentTitleText, exp.SectionNodes[0].HeadingRaw)
	}

	if len(run.Tasks) != len(exp.ReviewTasks) {
		t.Fatalf("generated %d review tasks, want %d", len(run.Tasks), len(exp.ReviewTasks))
	}

	ordinalOf := map[string]int{}
	for i, n := range exp.SectionNodes {
		ordinalOf[n.SectionID] = i
	}

	for i, want := range exp.ReviewTasks {
		got := run.Tasks[i]

		if string(got.Reason) != want.ReviewReason {
			t.Errorf("task %d reason = %q, want %q", i, got.Reason, want.ReviewReason)
		}
		if got.SectionOrdinal != ordinalOf[want.SectionID] {
			t.Errorf("task %d section ordinal = %d, want %d (%s)", i, got.SectionOrdinal, ordinalOf[want.SectionID], want.SectionID)
		}
		if got.Status != TaskOpen {
			t.Errorf("task %d status = %q, want %q", i, got.Status, TaskOpen)
		}
		if len(got.CandidateRoles) != len(want.CandidateRoles) {
			t.Errorf("task %d candidates = %v, want %v", i, got.CandidateRoles, want.CandidateRoles)
		}
	}
}

// TestNewRun_UnidentifiedTitleRaisesATask covers §4's third case at run level.
//
// A document whose first H1 resolves to an ordinary role has no title, and that
// must surface as a question rather than as silence. Without the task, "no
// title identified" is indistinguishable from "no title needed".
func TestNewRun_UnidentifiedTitleRaisesATask(t *testing.T) {
	md := []byte("# Introduction\n\nOpening prose.\n\n## Methodology\n\nMethod prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := NewRun(doc, "test-run", "deadbeef")

	var found bool
	for _, task := range run.Tasks {
		if task.Reason == ReasonTitleAmbiguity {
			found = true
			if task.SectionOrdinal != -1 {
				t.Errorf("title task section ordinal = %d, want -1", task.SectionOrdinal)
			}
		}
	}
	if !found {
		t.Error("no title_ambiguity task was raised for a document with no identifiable title")
	}
}

// TestNewRun_ResolvedNodesRaiseNoTask guards the other direction. A run that
// raised a task per node would satisfy any count check that only looked for
// missing tasks, and would bury the real questions.
func TestNewRun_ResolvedNodesRaiseNoTask(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n## Methodology\n\nMethod prose.\n\n## Results\n\nResults prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := NewRun(doc, "test-run", "deadbeef")

	if len(run.Tasks) != 0 {
		t.Errorf("generated %d tasks for a document where everything resolved, want 0: %+v", len(run.Tasks), run.Tasks)
	}
}

// TestNewRun_BareContainerRaisesNoTask is the §7 boundary at run level.
//
// "Supporting information" resolves to Unknown by structural assignment. It
// must not reach a human: the heading carries no epistemic claim to adjudicate,
// and routing it to review would put noise in front of the genuine questions.
func TestNewRun_BareContainerRaisesNoTask(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n## Supporting information\n\nSupplementary prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	run := NewRun(doc, "test-run", "deadbeef")

	if len(run.Tasks) != 0 {
		t.Errorf("generated %d tasks, want 0 — a bare container is a complete answer: %+v", len(run.Tasks), run.Tasks)
	}

	node := doc.Nodes[1]
	if node.Classification.Role != RoleUnknown {
		t.Errorf("container role = %q, want %q", node.Classification.Role, RoleUnknown)
	}
	if node.Container != ContainerAppendix {
		t.Errorf("container = %q, want %q", node.Container, ContainerAppendix)
	}
}
