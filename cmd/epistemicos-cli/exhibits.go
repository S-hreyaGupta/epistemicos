package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/exhibit"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
)

// runExhibits extracts a paper's tables and figures and prints them.
//
// It reads Step 2's markdown and calls segment.Build itself rather than loading a
// stored segmentation run. Both are pure functions of the same bytes, so the join
// needs no database state and cannot be run against a stale set of offsets. It
// also means this works on a paper that has never been segmented.
func runExhibits(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "exhibits: paper id is required")
		os.Exit(2)
	}
	paperID := args[0]

	showRows := false
	for _, a := range args[1:] {
		if a == "--rows" {
			showRows = true
		}
	}

	pool, cleanup := openPool()
	defer cleanup()

	p, err := store.NewPostgresPaperStore(pool).GetByID(context.Background(), paper.ID(paperID))
	if err != nil {
		die(err)
	}
	if p == nil {
		die(fmt.Errorf("exhibits: paper %s not found", paperID))
	}
	if p.Markdown == "" {
		die(fmt.Errorf("exhibits: paper %s has no markdown; run ingest first", paperID))
	}

	md := []byte(p.Markdown)
	tables, figures := exhibit.Extract(md)

	// Section attribution, from the same bytes.
	var nodes []segment.SectionNode
	if doc, err := segment.Build(md); err == nil {
		nodes = doc.Nodes
	}

	fmt.Printf("paper %s\n", p.ID)
	fmt.Printf("  markdown:  %d characters\n", len(p.Markdown))
	fmt.Printf("  hash:      %s\n\n", p.MarkdownHash)
	fmt.Printf("  %d tables, %d figures\n\n", len(tables), len(figures))

	if len(tables) > 0 {
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		fmt.Fprintln(w, "LABEL\tCAPTION\tCOLS\tROWS\tCAPTION FROM\tSITS IN")
		fmt.Fprintln(w, "-----\t-------\t----\t----\t------------\t-------")
		for _, t := range tables {
			label := t.Kind + " " + t.Label
			if t.Label == "" {
				label = "(unlabelled)"
			}
			caption := t.Caption
			if caption == "" {
				caption = "—"
			}
			rows := fmt.Sprintf("%d", len(t.Rows))
			if n := len(t.ContinuationOffsets); n > 0 {
				rows += fmt.Sprintf(" (+%d block)", n)
			}
			latex := ""
			if t.HasLatex {
				latex = " ƒ"
			}
			fmt.Fprintf(w, "%s%s\t%s\t%d\t%s\t%s\t%s\n",
				label, latex, truncate(caption, 46), t.ColumnCount(), rows,
				t.CaptionSource, truncate(sectionAt(nodes, t.StartOffset), 30))
		}
		_ = w.Flush()
		fmt.Printf("\nƒ marks a table with LaTeX in its cells: those values are not plain strings.\n")
		fmt.Printf("\"SITS IN\" is where the table PHYSICALLY falls, which is not always the section\n")
		fmt.Printf("it belongs to — a caption lands where it fitted on the page.\n")
	}

	if len(figures) > 0 {
		fmt.Printf("\n")
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		fmt.Fprintln(w, "LABEL\tCAPTION\tPAGE\tCROP\tSITS IN")
		fmt.Fprintln(w, "-----\t-------\t----\t----\t-------")
		for _, f := range figures {
			crop := "—"
			if f.CropWidth > 0 {
				crop = fmt.Sprintf("%dx%d @%d,%d", f.CropWidth, f.CropHeight, f.CropX, f.CropY)
			}
			page := "—"
			if f.Page > 0 {
				page = fmt.Sprintf("%d", f.Page)
			}
			fmt.Fprintf(w, "fig %s\t%s\t%s\t%s\t%s\n",
				f.Label, truncate(f.Caption, 46), page, crop,
				truncate(sectionAt(nodes, f.StartOffset), 30))
		}
		_ = w.Flush()

		fmt.Printf("\nThe crop box is the figure's position on that page of the PDF, at %d DPI.\n", exhibit.MathpixRenderDPI)
		fmt.Printf("It is why we do not depend on Mathpix's CDN: every figure can be re-cut from\n")
		fmt.Printf("the PDF we already store at ingest.\n")
	}

	if len(tables) == 0 && len(figures) == 0 {
		fmt.Printf("No tables or figures. Some papers genuinely have none — one of the\n")
		fmt.Printf("qualitative papers in the set has a single table and no figures at all.\n")
		return
	}

	if !showRows {
		fmt.Printf("\nPass --rows to print the table contents.\n")
		return
	}

	for _, t := range tables {
		fmt.Printf("\n──────────────────────────────────────────────────────────────────────\n")
		fmt.Printf("%s %s. %s\n\n", t.Kind, t.Label, t.Caption)
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		if len(t.Header) > 0 {
			fmt.Fprintln(w, strings.Join(truncateAll(t.Header, 22), "\t"))
			marks := make([]string, len(t.Header))
			for i := range marks {
				marks[i] = "------"
			}
			fmt.Fprintln(w, strings.Join(marks, "\t"))
		}
		for _, row := range t.Rows {
			fmt.Fprintln(w, strings.Join(truncateAll(row, 22), "\t"))
		}
		_ = w.Flush()
	}
}

// sectionAt names the section whose span contains off.
func sectionAt(nodes []segment.SectionNode, off int) string {
	best := ""
	for _, n := range nodes {
		if n.StartOffset <= off {
			best = strings.TrimSpace(n.HeadingRaw)
			continue
		}
		break
	}
	if best == "" {
		return "—"
	}
	return best
}

func truncateAll(in []string, n int) []string {
	out := make([]string, len(in))
	for i, s := range in {
		out[i] = truncate(s, n)
	}
	return out
}
