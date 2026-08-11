// epistemicos-cli is the offline counterpart of epistemicos-api.
//
//	epistemicos-cli migrate up                       Apply DB migrations
//	epistemicos-cli ingest <url>                     Ingest a paper by URL
//	epistemicos-cli list                             List ingested papers
//	epistemicos-cli export-markdown <id> --out <p>   Write stored markdown byte-exactly
package main

import (
	"context"
	"fmt"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/hasher"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/mathpix"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/pdfdownloader"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/services/ingest"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	_ = godotenv.Load()

	cmd := os.Args[1]
	args := os.Args[2:]

	switch cmd {
	case "migrate":
		runMigrate(args)
	case "ingest":
		runIngest(args)
	case "list":
		runList()
	case "export-markdown":
		runExportMarkdown(args)
	case "help", "-h", "--help":
		usage()
	default:
		fmt.Fprintf(os.Stderr, "unknown command: %s\n", cmd)
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `epistemicos-cli

Commands:
  migrate up               Apply DB migrations
  ingest <url>             Ingest a paper from a URL
  list                     List ingested papers
  export-markdown <paper-id> --out <path>
                           Write a paper's stored markdown to a file byte-exactly (no
                           trimming, no line-ending translation, no trailing newline) and
                           print its markdown_hash.`)
}

func runMigrate(args []string) {
	cfg, err := config.Load()
	if err != nil {
		die(err)
	}
	if len(args) == 0 || args[0] == "up" {
		if err := store.RunMigrations(cfg.DBURL); err != nil {
			die(err)
		}
		fmt.Println("migrations applied")
		return
	}
	fmt.Fprintf(os.Stderr, "migrate: unsupported subcommand %q\n", args[0])
	os.Exit(2)
}

func runIngest(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "ingest: url is required")
		os.Exit(2)
	}
	svc, cleanup := buildIngest()
	defer cleanup()

	p, err := svc.FromURL(context.Background(), args[0])
	if err != nil {
		die(err)
	}
	fmt.Printf("ingested:\n  id:     %s\n  hash:   %s\n  title:  %s\n  status: %s\n",
		p.ID, p.Hash, p.Title, p.Status)
}

func runList() {
	svc, cleanup := buildIngest()
	defer cleanup()

	papers, err := svc.List(context.Background())
	if err != nil {
		die(err)
	}
	if len(papers) == 0 {
		fmt.Println("(no papers ingested yet)")
		return
	}
	for _, p := range papers {
		fmt.Printf("%s  %s  %-12s  %s\n",
			p.ID, p.CreatedAt.Format("2006-01-02 15:04"), p.Status, p.Title)
	}
}

func buildIngest() (*ingest.Service, func()) {
	cfg, err := config.Load()
	if err != nil {
		die(err)
	}
	pool, err := pgxpool.New(context.Background(), cfg.DBURL)
	if err != nil {
		die(err)
	}

	paperStore := store.NewPostgresPaperStore(pool)
	downloader := pdfdownloader.New()
	processor := mathpix.New(cfg.MathpixID, cfg.MathpixKey)
	h := hasher.New()

	svc := ingest.New(paperStore, downloader, processor, h, cfg.PDFDir)
	return svc, func() { pool.Close() }
}

func die(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
