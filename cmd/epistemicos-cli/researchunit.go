package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/researchunit"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
)

// runResearchUnit applies the multi-study gate and, for a single-study paper,
// creates RU1 and places every section relative to it.
//
// Deterministic throughout: no model, no network. It reads Step 2's markdown and
// calls the segmenter itself, so the section roles it places are computed from the
// same bytes rather than read from a stored run that may have been produced under
// different rules.
func runResearchUnit(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "research-unit: paper id is required")
		os.Exit(2)
	}
	paperID := args[0]

	pool, cleanup := openPool()
	defer cleanup()

	p, err := store.NewPostgresPaperStore(pool).GetByID(context.Background(), paper.ID(paperID))
	if err != nil {
		die(err)
	}
	if p == nil {
		die(fmt.Errorf("research-unit: paper %s not found", paperID))
	}
	if p.Markdown == "" {
		die(fmt.Errorf("research-unit: paper %s has no markdown; run ingest first", paperID))
	}

	doc, err := segment.Build([]byte(p.Markdown))
	if err != nil {
		die(fmt.Errorf("research-unit: segment: %w", err))
	}

	headings := make([]researchunit.Heading, 0, len(doc.Nodes))
	for _, n := range doc.Nodes {
		headings = append(headings, researchunit.Heading{
			Ordinal: n.Ordinal,
			Level:   n.HeadingLevel,
			Text:    strings.TrimSpace(n.HeadingRaw),
			Role:    string(n.Classification.Role),
		})
	}

	gate := researchunit.Detect(headings, p.Markdown)

	// Stored BEFORE the routing below, and for every verdict rather than only
	// the ones that proceed.
	//
	// The refusals are the rows most worth having. A `multi` explains why a
	// paper stopped, and an `uncertain` is the question a human will be asked —
	// and "re-run the command and read the terminal" is not a review surface.
	//
	// Writing it first also means a paper that is about to be refused has its
	// record on disk before the process is allowed to end.
	if err := store.NewPostgresResearchUnitStore(pool).
		SaveGate(context.Background(), string(p.ID), p.MarkdownHash, gate); err != nil {
		die(fmt.Errorf("research-unit: store verdict: %w", err))
	}

	fmt.Printf("paper %s\n", p.ID)
	fmt.Printf("  markdown:  %d characters\n", len(p.Markdown))
	fmt.Printf("  sections:  %d\n", len(doc.Nodes))
	fmt.Printf("  rules:     %s\n\n", gate.RuleVersion)
	fmt.Printf("  GATE:      %s\n", strings.ToUpper(string(gate.Verdict)))
	fmt.Printf("  because:   %s\n", gate.Reason)

	if len(gate.Evidence) > 0 {
		fmt.Printf("\n  what was found\n\n")
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		fmt.Fprintln(w, "  KIND\tLABEL\tSTUDY\tWHERE\tTEXT")
		fmt.Fprintln(w, "  ----\t-----\t-----\t-----\t----")
		for _, e := range gate.Evidence {
			where := "heading"
			if e.Ordinal < 0 {
				where = "prose"
			}
			fmt.Fprintf(w, "  %s\t%s\t%s\t%s\t%s\n", e.Kind, e.Label, e.Group, where, truncate(e.Text, 52))
		}
		_ = w.Flush()
	}

	switch gate.Verdict {
	case researchunit.VerdictMulti:
		fmt.Printf("\nOUT OF SCOPE. No research unit was created.\n\n")
		fmt.Printf("This is the failure the gate exists to prevent: with %d studies in one\n", gate.StudyCount)
		fmt.Printf("manuscript, a single-study pipeline would attach the method of one study to\n")
		fmt.Printf("the results of another. That output looks like a finding rather than an error.\n\n")
		fmt.Printf("The verdict above and the %d labels behind it ARE stored, under rule version\n", len(gate.Evidence))
		fmt.Printf("%s. A refusal with no record is a paper that stopped for reasons nobody can\n", gate.RuleVersion)
		fmt.Printf("look up afterwards.\n")
		return

	case researchunit.VerdictUncertain:
		fmt.Printf("\nNEEDS A HUMAN. No research unit was created.\n\n")
		fmt.Printf("The signals could mean either one study in stages or several studies, and\n")
		fmt.Printf("only reading the sections settles it. Answering \"single\" wrongly would\n")
		fmt.Printf("corrupt every link in the paper, so the gate asks rather than guesses.\n\n")
		fmt.Printf("The verdict and its evidence are stored, so the question survives this\n")
		fmt.Printf("terminal. There is no queue to put it in yet — see FUTURE_WORK item V.\n")
		return
	}

	unit := researchunit.NewSingleStudy(paperID, researchunit.StatusAcceptedSingleStudy)

	fmt.Printf("\n  research unit\n\n")
	fmt.Printf("    ref:     %s\n", unit.Ref)
	fmt.Printf("    label:   %s\n", unit.Label)
	fmt.Printf("    type:    %s, index %d\n", unit.Type, unit.Index)
	fmt.Printf("    status:  %s\n", unit.Status)

	assignments := researchunit.Assign(headings, unit)

	fmt.Printf("\n  where each section sits\n\n")
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "  #\tHEADING\tROLE\tBELONGS TO\tUNIT")
	fmt.Fprintln(w, "  -\t-------\t----\t----------\t----")
	for _, a := range assignments {
		role := a.Role
		if role == "" {
			role = "—"
		}
		ref := a.UnitRef
		if ref == "" {
			ref = "—"
		}
		fmt.Fprintf(w, "  %d\t%s\t%s\t%s\t%s\n", a.SectionOrdinal, truncate(a.Heading, 44), role, a.Scope, ref)
	}
	_ = w.Flush()

	counts := researchunit.Summary(assignments)
	fmt.Printf("\n  %d study, %d manuscript, %d both, %d undetermined\n",
		counts[researchunit.ScopeStudy], counts[researchunit.ScopeManuscript],
		counts[researchunit.ScopeBoth], counts[researchunit.ScopeUndetermined])

	fmt.Printf("\n\"both\" is not a hedge. An introduction motivates the paper AND states the\n")
	fmt.Printf("study's question; a discussion interprets results AND makes claims about the\n")
	fmt.Printf("literature. That split is real but it happens at paragraph level, and forcing\n")
	fmt.Printf("a side here would produce a value indistinguishable from a confident one.\n")
	fmt.Printf("\n\"undetermined\" is the document title, an appendix, or a section Step 3 could\n")
	fmt.Printf("not classify. Guessing here would answer a question a human is already asked.\n")
	fmt.Printf("\nNothing is stored yet. The unit and these assignments are computed on demand.\n")
}
