package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/approved"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/llmsuggest"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
)

// runSuggest asks an LLM which role each unresolved section should have, and
// prints the answers.
//
// IT WRITES NOTHING. Not to section_nodes, not to review_decisions, not
// anywhere. Specification §13 defers the LLM from the MVP, and this command
// respects that by staying outside the pipeline entirely: it reads a run that
// has already completed, and prints suggestions for a person to accept or
// reject.
//
// The separation is what keeps segmentation reproducible. The same markdown
// yields the same sections and the same open questions whether or not this
// command is ever run, and whether or not the network is up.
func runSuggest(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "suggest: run id is required (from `segment`)")
		os.Exit(2)
	}
	runID := args[0]

	cfg, err := config.Load()
	if err != nil {
		die(err)
	}

	apiKey := os.Getenv("ANTHROPIC_API_KEY")
	if apiKey == "" {
		die(fmt.Errorf("suggest: ANTHROPIC_API_KEY is not set; add it to .env"))
	}

	pool, err := pgxpool.New(context.Background(), cfg.DBURL)
	if err != nil {
		die(err)
	}
	defer pool.Close()

	ctx := context.Background()

	segStore := store.NewPostgresSegmentationStore(pool)
	run, err := segStore.GetRun(ctx, runID)
	if err != nil {
		die(err)
	}

	// The markdown is needed for the excerpts. Fetching it through the same
	// adapter the pipeline uses means the hash is verified here too — an
	// excerpt sliced from unverified text would be as wrong as a stored span.
	source := approved.NewPapersSource(pool)
	markdown, _, err := source.Get(ctx, run.ExtractionRunID)
	if err != nil {
		die(fmt.Errorf("suggest: fetch markdown: %w", err))
	}
	md := []byte(markdown)

	var (
		sections []llmsuggest.Section
		ordinals []int
	)

	for _, task := range run.Tasks {
		if task.SectionOrdinal < 0 || task.SectionOrdinal >= len(run.Nodes) {
			continue // title ambiguity has no section
		}

		node := run.Nodes[task.SectionOrdinal]

		// The same context a human reviewer would be shown: the headings above
		// it, then the section itself. That is not a coincidence — if the
		// suggester sees less than the reviewer, its answers are not comparable
		// to theirs.
		ctxInfo, ok := segment.ContextFor(run.Nodes, task.SectionOrdinal)
		if !ok {
			continue
		}

		sections = append(sections, llmsuggest.Section{
			Heading:   node.HeadingRaw,
			Ancestors: ctxInfo.AncestorHeadings,
			Excerpt:   excerpt(ctxInfo.Text(md), 400),
		})
		ordinals = append(ordinals, task.SectionOrdinal)
	}

	if len(sections) == 0 {
		fmt.Println("No unresolved sections in this run.")
		return
	}

	fmt.Fprintf(os.Stderr, "asking about %d unresolved sections...\n\n", len(sections))

	client := llmsuggest.New(apiKey)
	suggestions, err := client.Suggest(ctx, sections)
	if err != nil {
		die(err)
	}

	fmt.Printf("%d suggestions — ADVISORY ONLY, nothing has been saved\n\n", len(suggestions))

	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "SECTION\tSUGGESTED\tSURE?\tWHY")
	fmt.Fprintln(w, "-------\t---------\t-----\t---")

	for _, s := range suggestions {
		fmt.Fprintf(w, "%s\t%s\t%s\t%s\n",
			truncate(s.Heading, 40), s.Role, s.Confidence, truncate(s.Reasoning, 56))
	}
	_ = w.Flush()

	fmt.Printf("\nNothing was written. Segmentation stays deterministic — the same paper\n")
	fmt.Printf("produces the same sections and the same open questions with or without\n")
	fmt.Printf("this command. These are a first draft for a reviewer, not a decision.\n")
}

// excerpt returns the opening of a section's text on a single line.
//
// The section itself can run to several thousand characters; the first few
// hundred are almost always enough to tell a methodology section from a results
// one, and sending the whole thing would cost more without deciding more.
func excerpt(s string, n int) string {
	s = strings.Join(strings.Fields(s), " ")
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}
