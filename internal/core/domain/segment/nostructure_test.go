package segment

import "testing"

// A document with no headings at all is the one case where every later step is
// working from nothing, and until 3R it was also the case that raised the
// fewest questions. These tests pin the shape that fixes it.

func headlessRun(t *testing.T) Run {
	t.Helper()
	md := []byte("This document has no headings at all.\n\nJust prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	return NewRun(doc, "test-run", "deadbeef")
}

// TestNewRun_HeadlessDocumentRaisesBothQuestions.
//
// Two tasks, and the separation is the point. Merging them was considered: a
// headless document has no title either, so it already raised a
// title_ambiguity task and could never pass unlooked-at.
//
// But that task asks what the paper is CALLED. A reviewer can answer it
// perfectly well while the document still has no structural signal of any kind,
// and the run would then pass. There is one decision per task, so a merged task
// would force a reviewer who can name the paper but considers it unusable to
// answer only one of those.
func TestNewRun_HeadlessDocumentRaisesBothQuestions(t *testing.T) {
	run := headlessRun(t)

	if len(run.Tasks) != 2 {
		t.Fatalf("generated %d tasks, want 2 (no_structure and title_ambiguity): %+v", len(run.Tasks), run.Tasks)
	}

	seen := map[ReviewReason]ReviewTask{}
	for _, task := range run.Tasks {
		seen[task.Reason] = task
	}

	structure, ok := seen[ReasonNoStructure]
	if !ok {
		t.Fatalf("no no_structure task; a document with no headings would pass the gate on a title alone")
	}
	if structure.SectionOrdinal != 0 {
		t.Errorf("no_structure section ordinal = %d, want 0 — it concerns the whole-document node", structure.SectionOrdinal)
	}

	title, ok := seen[ReasonTitleAmbiguity]
	if !ok {
		t.Fatalf("no title_ambiguity task; §4 is explicit that nothing is auto-promoted")
	}
	if title.SectionOrdinal != -1 {
		t.Errorf("title section ordinal = %d, want -1 — there is no candidate node to point at", title.SectionOrdinal)
	}

	// The two carry different section references, which is also what keeps them
	// apart under UNIQUE(segmentation_run_id, section_id): one holds the node,
	// one holds NULL, and NULLs do not collide.
	if structure.SectionOrdinal == title.SectionOrdinal {
		t.Error("both tasks point at the same section; the schema's one-task-per-section rule would reject the pair")
	}
}

// TestNewRun_HeadlessNodeClassificationIsUntouched.
//
// The task is a GATE requirement, not a report of a classification failure —
// exactly as title_ambiguity leaves the title fields alone. §5 resolved this
// node structurally and deliberately, and the run is Completed. Marking it
// unresolved to force a question would be the tool lying about what it found in
// order to get someone's attention.
func TestNewRun_HeadlessNodeClassificationIsUntouched(t *testing.T) {
	run := headlessRun(t)

	if run.Status != RunCompleted {
		t.Errorf("run status = %q, want %q", run.Status, RunCompleted)
	}

	n := run.Nodes[0]
	if n.Classification.Role != RoleUnknown {
		t.Errorf("role = %q, want %q", n.Classification.Role, RoleUnknown)
	}
	if n.Classification.Status != StatusResolved {
		t.Errorf("status = %q, want %q — raising the task must not rewrite what the machine concluded", n.Classification.Status, StatusResolved)
	}
	if n.Classification.Method != MethodStructural {
		t.Errorf("method = %q, want %q", n.Classification.Method, MethodStructural)
	}
}

// TestNewRun_StructuredDocumentRaisesNoStructureTask is the negative case, and
// it matters more than it looks: the rule keys off the SHAPE §5 produces rather
// than off "were there headings", so a document that legitimately resolves to
// few nodes must not trip it.
func TestNewRun_StructuredDocumentRaisesNoStructureTask(t *testing.T) {
	md := []byte("# A Study Of Things\n\nAuthors.\n\n## Methodology\n\nMethod prose.\n")

	doc, err := Build(md)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	for _, task := range NewRun(doc, "test-run", "deadbeef").Tasks {
		if task.Reason == ReasonNoStructure {
			t.Fatalf("raised no_structure on a document with headings: %+v", task)
		}
	}
}

// TestNewStructureDecision_AllowsUnknown.
//
// AssignableRoles excludes Unknown everywhere else, because a task exists
// precisely because something could not be classified and Unknown would let a
// reviewer close a genuine question with the one value meaning "there was no
// question".
//
// That argument does not hold here. This node is ALREADY resolved Unknown by
// rule; the reviewer is being asked whether a structureless document may
// proceed, not to supply a missing role. Unknown is the ordinary way to say yes,
// and refusing it would leave the task with no way to be answered at all.
func TestNewStructureDecision_AllowsUnknown(t *testing.T) {
	task := ReviewTask{Reason: ReasonNoStructure, SectionOrdinal: 0}

	d, err := NewStructureDecision(task, "t1", "", "shreya", "prose only, but readable")
	if err != nil {
		t.Fatalf("NewStructureDecision with an empty role: %v", err)
	}
	if d.AssignedRole != RoleUnknown {
		t.Errorf("role = %q, want %q — an empty role accepts the document as-is", d.AssignedRole, RoleUnknown)
	}
	if d.Decision != DecisionResolve {
		t.Errorf("decision = %q, want %q", d.Decision, DecisionResolve)
	}

	if _, err := NewStructureDecision(task, "t1", RoleMethodology, "shreya", ""); err != nil {
		t.Errorf("naming a real role for the whole document: %v", err)
	}
}

// TestNewStructureDecision_RefusesOtherTasks and its mirror: a no_structure task
// must not be answered with an ordinary role decision. Both directions are
// checked because the failure is silent — a role decision on this task would
// look like a perfectly good answer to a question nobody asked.
func TestNewStructureDecision_RefusesOtherTasks(t *testing.T) {
	if _, err := NewStructureDecision(ReviewTask{Reason: ReasonZeroRoleMatch}, "t1", RoleResults, "shreya", ""); err == nil {
		t.Error("accepted a structure decision for a zero_role_match task")
	}
	if _, err := NewRoleDecision(ReviewTask{Reason: ReasonNoStructure}, "t1", RoleResults, "shreya", ""); err == nil {
		t.Error("accepted a role decision for a no_structure task; it answers a question that was not asked")
	}
}

// TestNewRejection_RequiresAReason.
//
// On a rejection the comment is not a note, it is the sentence the author reads.
// "unclear" is not something an author can act on, and neither is silence.
func TestNewRejection_RequiresAReason(t *testing.T) {
	task := ReviewTask{Reason: ReasonZeroRoleMatch}

	if _, err := NewRejection(task, "t1", "shreya", ""); err == nil {
		t.Error("accepted a rejection with no comment; the author would be told nothing")
	}
	if _, err := NewRejection(task, "t1", "shreya", "   "); err == nil {
		t.Error("accepted a whitespace-only comment")
	}
	if _, err := NewRejection(task, "t1", "", "the heading is an OCR artifact"); err == nil {
		t.Error("accepted a rejection with no reviewer; a decision that outranks the machine cannot be anonymous")
	}
}

// TestNewRejection_AssignsNothing.
//
// A rejection carrying a role would make the effective view two things at once,
// and the overlay is the one place in this system where ambiguity is served to
// consumers as fact.
func TestNewRejection_AssignsNothing(t *testing.T) {
	d, err := NewRejection(ReviewTask{Reason: ReasonZeroRoleMatch}, "t1", "shreya", "unintelligible")
	if err != nil {
		t.Fatalf("NewRejection: %v", err)
	}

	if d.AssignedRole != "" || d.AssignedContentClass != "" ||
		d.AssignedDocumentTitleText != "" || d.AssignedDocumentTitleNodeID != "" {
		t.Errorf("rejection carries an assignment: %+v", d)
	}
	if !d.Rejected() {
		t.Error("Rejected() is false on a rejection")
	}
}

// TestNewRejection_WorksForEveryReason.
//
// The role constructors are split by reason because a role cannot answer "what
// is this paper called". Rejection is not an answer to either question, so the
// split does not apply: a reviewer who cannot name the paper rejects the title
// task exactly as they would reject a heading.
func TestNewRejection_WorksForEveryReason(t *testing.T) {
	for _, reason := range []ReviewReason{
		ReasonZeroRoleMatch, ReasonMultiRoleMatch, ReasonTitleAmbiguity, ReasonNoStructure,
	} {
		if _, err := NewRejection(ReviewTask{Reason: reason}, "t1", "shreya", "cannot be answered"); err != nil {
			t.Errorf("%s: %v", reason, err)
		}
	}
}
