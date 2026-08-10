package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
)

// exportFlags holds the parsed arguments for export-markdown. It is
// deliberately NOT reviewerFlags: that type is shared by the two
// reviewer-matching subcommands and its name would be misleading on a
// command that has nothing to do with reviewer matching.
type exportFlags struct {
	paperID string
	outPath string
}

// parseExportFlags is a hand-rolled flag parser, matching
// parseReviewerFlags in reviewer.go, to keep dependencies minimal. The
// first positional argument is the paper-id; the rest are --key value
// pairs.
func parseExportFlags(args []string) exportFlags {
	var f exportFlags
	i := 0
	if i < len(args) && !strings.HasPrefix(args[i], "--") {
		f.paperID = args[i]
		i++
	}
	for ; i < len(args); i++ {
		switch args[i] {
		case "--out":
			i++
			if i < len(args) {
				f.outPath = args[i]
			}
		}
	}
	return f
}

// runExportMarkdown implements paperly-cli export-markdown <paper-id> --out <path>.
//
// It loads the paper from Postgres and writes Paper.Markdown to the
// named file BYTE-EXACTLY, then prints the byte count and the stored
// markdown_hash so the operator can pair the file with the DB record.
//
// Why a subcommand rather than a shell pipeline: the obvious
// alternative, curl the API and pipe through jq into a redirect,
// silently mutates the bytes. The jq raw-output mode appends a trailing
// newline and Windows shell redirection can inject CRLF. Either one
// breaks the property this command exists to guarantee, namely that the
// SHA-256 of the written file equals papers.markdown_hash.
//
// --out is required rather than defaulted on purpose: this command
// overwrites whatever it is pointed at, so it never writes to a path
// the operator did not name.
func runExportMarkdown(args []string) {
	flags := parseExportFlags(args)
	if flags.paperID == "" {
		fmt.Fprintln(os.Stderr, "export-markdown: paper id is required")
		os.Exit(2)
	}
	if flags.outPath == "" {
		fmt.Fprintln(os.Stderr, "export-markdown: --out is required")
		os.Exit(2)
	}

	cfg, err := config.Load()
	if err != nil {
		die(err)
	}
	pool, err := pgxpool.New(context.Background(), cfg.DBURL)
	if err != nil {
		die(fmt.Errorf("export-markdown: db connect: %w", err))
	}
	defer pool.Close()

	// GetByID directly rather than reviewer.go readMarkdown: this
	// command also needs p.MarkdownHash, which readMarkdown discards.
	paperStore := store.NewPostgresPaperStore(pool)
	p, err := paperStore.GetByID(context.Background(), paper.ID(flags.paperID))
	if err != nil {
		die(fmt.Errorf("export-markdown: load paper %s: %w", flags.paperID, err))
	}
	if p == nil {
		die(fmt.Errorf("export-markdown: paper %s not found", flags.paperID))
	}
	// Refuse to write an empty fixture. An empty file is a silent
	// failure that would later read as a legitimately empty document.
	if p.Markdown == "" {
		die(fmt.Errorf("export-markdown: paper %s has no markdown", flags.paperID))
	}

	out := flags.outPath
	if dir := filepath.Dir(out); dir != "" {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			die(fmt.Errorf("export-markdown: mkdir %s: %w", dir, err))
		}
	}
	// BYTE-EXACT WRITE. The markdown goes to disk unmodified: no
	// trimming, no line-ending translation, no added trailing newline,
	// no buffered writer, no formatting verb. Byte-exactness is the
	// entire point of this command — do not introduce any transform
	// between p.Markdown and the file.
	if err := os.WriteFile(out, []byte(p.Markdown), 0o644); err != nil {
		die(fmt.Errorf("export-markdown: write %s: %w", out, err))
	}

	fmt.Printf("exported:\n  id:     %s\n  bytes:  %d\n  hash:   %s\n  out:    %s\n",
		p.ID, len(p.Markdown), p.MarkdownHash, out)
}
