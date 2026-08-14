package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/approved"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/services/segmentation"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
)

// runIngestFile ingests a PDF already on disk.
//
// The existing `ingest` command takes a URL, which covers the ordinary case of
// fetching a paper from a publisher. A PDF that arrived by other means — email,
// a chat message, a colleague's hand — has no URL, and inventing one to satisfy
// the command would be worse than accepting the file directly.
//
// The service already exposes FromUpload for the HTTP path; this reuses it, so
// a file ingested here goes through exactly the same dedupe, hashing and
// conversion as one fetched from the web.
func runIngestFile(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "ingest-file: path is required")
		os.Exit(2)
	}

	f, err := os.Open(args[0])
	if err != nil {
		die(err)
	}
	defer f.Close()

	svc, cleanup := buildIngest()
	defer cleanup()

	fmt.Fprintln(os.Stderr, "converting via Mathpix, this takes a minute or two...")

	p, err := svc.FromUpload(context.Background(), f)
	if err != nil {
		die(err)
	}

	fmt.Printf("ingested:\n  id:     %s\n  hash:   %s\n  status: %s\n  bytes:  %d markdown\n",
		p.ID, p.Hash, p.Status, len(p.Markdown))
	fmt.Printf("\nnext:\n  epistemicos-cli segment %s\n", p.ID)
}

// runSegment runs Step 3 over an already-ingested paper and prints the result.
//
// The printed table is the answer to "what do we actually get at the end": one
// row per section, with where it sits, what it was classified as, and how that
// classification was reached. The review tasks follow, because an honest answer
// includes the questions the machine could not settle.
func runSegment(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "segment: paper id is required")
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

	ctx := context.Background()

	source := approved.NewPapersSource(pool)
	segStore := store.NewPostgresSegmentationStore(pool)
	svc := segmentation.New(source, segStore)

	runID, err := svc.Segment(ctx, paperID)
	if err != nil {
		die(err)
	}

	run, err := segStore.GetRun(ctx, runID)
	if err != nil {
		die(err)
	}

	printRun(run)
}

func printRun(run *segment.Run) {
	fmt.Printf("segmentation run %s\n", run.ID)
	fmt.Printf("  status:        %s\n", run.Status)
	fmt.Printf("  markdown hash: %s\n", run.ApprovedMarkdownHash)
	fmt.Printf("  rule version:  %s\n", run.StructuralRuleVersion)

	fmt.Printf("  headings:      ")
	for level := 1; level <= 6; level++ {
		fmt.Printf("H%d=%d ", level, run.HeadingCounts[level])
	}
	fmt.Println()

	if run.DocumentTitleStatus == segment.TitleIdentified {
		fmt.Printf("  title:         %s\n", truncate(run.DocumentTitleText, 68))
		fmt.Printf("  title found by: %s\n", run.DocumentTitleMethod)
	} else {
		fmt.Printf("  title:         (unresolved — a review task was raised)\n")
	}

	fmt.Printf("\n%d sections\n\n", len(run.Nodes))

	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "#\tLVL\tHEADING\tROLE\tCLASS\tHOW\tWHERE\tBYTES")
	fmt.Fprintln(w, "-\t---\t-------\t----\t-----\t---\t-----\t-----")

	for _, n := range run.Nodes {
		// The title node has no role BY DESIGN — "document_title" is a node
		// kind, not a section role, and §4 leaves the role null. Printing an
		// empty role as "unresolved" here would report a deliberate, correct
		// determination as a failure, which is exactly the confusion v2.0's
		// two-axis model exists to prevent.
		role := string(n.Classification.Role)
		switch {
		case n.Kind == segment.KindDocumentTitle:
			role = "(document title)"
		case role == "":
			role = "— needs review"
		}

		how := string(n.Classification.Method)
		if how == "" {
			how = "—"
		}

		// An appendix answers WHERE the content sits; the role answers what it
		// does. Both are stored and both matter, so both are shown — otherwise
		// "Appendix A" looks like an ordinary unclassified section.
		where := "—"
		if n.Container != "" {
			where = string(n.Container)
			if n.AppendixLabel != "" {
				where += " " + n.AppendixLabel
			}
		}

		heading := strings.Repeat("  ", indentFor(n.HeadingLevel)) + truncate(n.HeadingRaw, 44)

		fmt.Fprintf(w, "%d\tH%d\t%s\t%s\t%s\t%s\t%s\t%d–%d\n",
			n.Ordinal, n.HeadingLevel, heading,
			role, n.Classification.ContentClass, how, where,
			n.StartOffset, n.EndOffset)
	}
	_ = w.Flush()

	if len(run.Tasks) == 0 {
		fmt.Printf("\nNo review tasks — every section classified cleanly.\n")
		return
	}

	fmt.Printf("\n%d review tasks — these need a human\n\n", len(run.Tasks))

	tw := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(tw, "SECTION\tWHY\tCANDIDATES")
	fmt.Fprintln(tw, "-------\t---\t----------")

	for _, task := range run.Tasks {
		heading := "(whole document)"
		if task.SectionOrdinal >= 0 && task.SectionOrdinal < len(run.Nodes) {
			heading = truncate(run.Nodes[task.SectionOrdinal].HeadingRaw, 44)
		}

		candidates := "— reviewer picks from the full list"
		if len(task.CandidateRoles) > 0 {
			parts := make([]string, 0, len(task.CandidateRoles))
			for _, r := range task.CandidateRoles {
				parts = append(parts, string(r))
			}
			candidates = strings.Join(parts, " or ")
		}

		fmt.Fprintf(tw, "%s\t%s\t%s\n", heading, task.Reason, candidates)
	}
	_ = tw.Flush()

	fmt.Printf("\nThe reviewer's decision goes in the review_decisions table. It does not\n")
	fmt.Printf("overwrite anything above — the machine's answer stays as provenance, and\n")
	fmt.Printf("the effective value is computed at read time.\n")
}

// indentFor renders the tree shape. H1 and H2 are both flush left because the
// H1 is the document title rather than a section above the H2s.
func indentFor(level int) int {
	if level <= 2 {
		return 0
	}
	return level - 2
}

func truncate(s string, n int) string {
	s = strings.ReplaceAll(s, "\n", " ")
	if len(s) <= n {
		return s
	}
	return s[:n-1] + "…"
}
