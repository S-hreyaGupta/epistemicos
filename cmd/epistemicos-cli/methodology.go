package main

import (
	"context"
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/methodology"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
)

// runMethodology classifies an ingested paper as quantitative or qualitative.
//
// It reads Step 2's markdown directly and does not touch segmentation. That is
// the whole point of where this sits: a paper with sixty-five open review tasks
// still has a methodology, and waiting for a human to work through them before
// answering a question about the whole document would buy nothing.
func runMethodology(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "methodology: paper id is required")
		os.Exit(2)
	}
	paperID := args[0]

	cfg, err := config.Load()
	if err != nil {
		die(err)
	}
	pool, err := pgxpool.New(context.Background(), cfg.DBURL)
	if err != nil {
		die(err)
	}
	defer pool.Close()

	p, err := store.NewPostgresPaperStore(pool).GetByID(context.Background(), paper.ID(paperID))
	if err != nil {
		die(fmt.Errorf("methodology: load paper %s: %w", paperID, err))
	}
	if p == nil {
		die(fmt.Errorf("methodology: paper %s not found", paperID))
	}
	if p.Markdown == "" {
		die(fmt.Errorf("methodology: paper %s has no markdown; run ingest first", paperID))
	}

	printMethodology(p, methodology.Classify(p.Markdown))
}

func printMethodology(p *paper.Paper, r methodology.Result) {
	fmt.Printf("paper %s\n", p.ID)
	fmt.Printf("  markdown:  %d characters\n", len(p.Markdown))
	fmt.Printf("  hash:      %s\n\n", p.MarkdownHash)

	verdict := string(r.Class)
	if r.Status != methodology.StatusResolved {
		verdict = "— needs review"
	}
	fmt.Printf("  METHODOLOGY:   %s\n", verdict)
	fmt.Printf("  score:         %+.2f   (-1 qualitative … +1 quantitative)\n", r.Score)
	fmt.Printf("  qualitative:   %.2f terms per 10k characters\n", r.QualitativeRate)
	fmt.Printf("  quantitative:  %.2f terms per 10k characters\n", r.QuantitativeRate)
	fmt.Printf("  how:           %s\n", r.Method)

	if r.MixedFlag {
		fmt.Printf("\n  ** MIXED METHODS mentioned. The published model has no mixed category,\n")
		fmt.Printf("     so this is a flag for a human, not a third answer. **\n")
	}

	fmt.Printf("\n  glossary reach: %d of %d terms present, %d occurrences\n",
		r.DistinctTerms, methodology.GlossarySize(), r.TotalOccurrences)

	if len(r.Matches) == 0 {
		fmt.Printf("\nNothing in the glossary appeared. That is not a qualitative paper, it is\n")
		fmt.Printf("a document this vocabulary cannot see.\n")
		return
	}

	fmt.Printf("\nthe evidence\n\n")
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "TERM\tCOUNT\tCOUNTS TOWARD")
	fmt.Fprintln(w, "----\t-----\t-------------")
	for _, m := range r.Matches {
		toward := m.Marker
		if toward == "" {
			toward = "— neither"
		}
		fmt.Fprintf(w, "%s\t%d\t%s\n", truncate(m.Term, 40), m.Count, toward)
	}
	_ = w.Flush()

	fmt.Printf("\nTerms marked \"neither\" are counted and shown but do not move the score.\n")
	fmt.Printf("They are the columns a trained model would use and this lexical rule does\n")
	fmt.Printf("not, which is the gap between what we built and the published method.\n")
}

