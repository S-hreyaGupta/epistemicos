package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/approved"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/llmclassify"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	domain "github.com/EpistemicOS/epistemicos/internal/core/domain/papertype"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
	"github.com/EpistemicOS/epistemicos/internal/core/services/papertype"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
)

// buildPaperType assembles the classification gate.
//
// An empty ANTHROPIC_API_KEY is not fatal here. It becomes an error at the moment
// a classification is actually attempted, which is the right moment: `review`,
// `resolve` and `effective` all construct a segmentation service that holds this
// gate and none of them ever calls it, so refusing to start without a key would
// block three commands that do not need one.
func buildPaperType(pool *pgxpool.Pool) *papertype.Service {
	return papertype.New(
		approved.NewPapersSource(pool),
		llmclassify.New(os.Getenv("ANTHROPIC_API_KEY")),
		store.NewPostgresPaperTypeStore(pool),
	)
}

// runClassify classifies a paper and prints the verdict with its evidence.
//
// It prints rather than routes. The routing happens in `segment`, and keeping the
// two separate means asking about a conceptual paper on purpose is a normal
// action rather than an error.
func runClassify(args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "classify: paper id is required")
		os.Exit(2)
	}
	paperID := args[0]

	force := false
	for _, a := range args[1:] {
		if a == "--force" {
			force = true
		}
	}

	pool, cleanup := openPool()
	defer cleanup()

	svc := buildPaperType(pool)
	ctx := context.Background()

	var (
		result *papertype.Result
		err    error
	)
	if force {
		// A fresh call even though a verdict exists. Verdicts are append-only, so
		// this adds a second answer rather than replacing the first — which is
		// the point when comparing two models or two prompt versions.
		result, err = svc.Classify(ctx, paperID)
	} else {
		result, err = svc.Verdict(ctx, paperID)
	}
	if err != nil {
		die(err)
	}

	printVerdict(result)

	if result.Record.Verdict.Empirical() {
		fmt.Printf("\nThis paper proceeds. Next:\n  epistemicos-cli segment %s\n", paperID)
		return
	}

	fmt.Printf("\nOUT OF SCOPE. `segment` will refuse this paper.\n")
	fmt.Printf("We only handle empirical papers today, and Step 3's role table is built\n")
	fmt.Printf("from the sections empirical papers have. On this paper it would not fail —\n")
	fmt.Printf("it would produce a plausible answer that means nothing.\n")
}

func printVerdict(r *papertype.Result) {
	rec := r.Record
	v := rec.Verdict

	fmt.Printf("paper %s\n", rec.PaperID)
	fmt.Printf("  markdown hash:  %s\n", rec.MarkdownHash)
	if r.Cached {
		fmt.Printf("  source:         stored verdict (pass --force to ask again)\n")
	} else {
		fmt.Printf("  source:         fresh classification\n")
	}
	fmt.Println()

	fmt.Printf("  TYPE:           %s   %s\n", v.PrimaryType, typeName(v.PrimaryType))
	if v.Subtype != "" {
		fmt.Printf("  subtype:        %s\n", v.Subtype)
	}
	if v.SecondaryType != "" {
		fmt.Printf("  secondary:      %s   %s\n", v.SecondaryType, typeName(v.SecondaryType))
	}
	fmt.Printf("  decision rule:  %d\n", v.DecisionRule)
	fmt.Printf("  confidence:     %s\n", v.Confidence)
	fmt.Printf("  empirical:      %v\n", v.Empirical())
	if v.BoundaryCase != "" {
		fmt.Printf("  boundary case:  %s\n", v.BoundaryCase)
	}
	if v.LimitsFromSelection != "" {
		fmt.Printf("  limits:         %s\n", v.LimitsFromSelection)
	}
	if v.Rationale != "" {
		fmt.Printf("  why:            %s\n", v.Rationale)
	}

	fmt.Printf("\n  prompt version: %s\n", rec.PromptVersion)
	fmt.Printf("  model:          %s\n", rec.Model)
	fmt.Printf("  input form:     %s\n", rec.InputForm)

	fmt.Printf("\n  quotes verified: %d of %d\n", rec.QuotesVerified, rec.QuotesExpected)
	if rec.QuotesVerified != rec.QuotesExpected {
		fmt.Printf("\n  ** THE MODEL QUOTED TEXT THAT IS NOT IN THIS PAPER. **\n")
		fmt.Printf("     A verdict resting on words the paper does not contain is not\n")
		fmt.Printf("     evidence, whichever way it points. `segment` will refuse this\n")
		fmt.Printf("     paper even if the verdict says A.\n")
	}

	fmt.Printf("\nthe evidence\n\n")
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "IN PAPER\tPOINTS TO\tQUOTE")
	fmt.Fprintln(w, "--------\t---------\t-----")
	for _, e := range v.Evidence {
		fmt.Fprintf(w, "%s\t%s\t%s\n", tick(e.Verified), v.PrimaryType, truncate(e.Quote, 66))
	}
	if v.CounterEvidence != nil {
		fmt.Fprintf(w, "%s\t%s\t%s\n", tick(v.CounterEvidence.Verified),
			v.CounterEvidence.PointsTo, truncate(v.CounterEvidence.Quote, 66))
	}
	_ = w.Flush()

	fmt.Printf("\nEvery quote is checked as an exact substring of the paper, after folding\n")
	fmt.Printf("typography the model may have normalised. A cross means the words are not\n")
	fmt.Printf("there, which is how a paraphrased answer is caught.\n")

	if v.PrimaryType == domain.TypeUnclassified {
		fmt.Printf("\nUNCLASSIFIED is a real answer, not a failure: %s\n", v.UnclassifiedReason)
	}
}

func typeName(t domain.Type) string {
	switch t {
	case domain.TypeEmpirical:
		return "empirical — its own observations of the world"
	case domain.TypeSynthesis:
		return "evidence synthesis — aggregates other studies under a protocol"
	case domain.TypeConceptual:
		return "conceptual — theory built by argumentation, no data"
	case domain.TypeFormal:
		return "formal — theorems, proofs, analytical derivation"
	case domain.TypeUnclassified:
		return "the model declined to classify it"
	}
	return ""
}

func tick(ok bool) string {
	if ok {
		return "yes"
	}
	return "NO"
}

// openPool loads config and connects. Shared by the commands that need a pool and
// nothing else from the platform layer.
func openPool() (*pgxpool.Pool, func()) {
	cfg, err := config.Load()
	if err != nil {
		die(err)
	}
	pool, err := pgxpool.New(context.Background(), cfg.DBURL)
	if err != nil {
		die(err)
	}
	return pool, func() { pool.Close() }
}

// explainGateFailure turns the service's sentinel errors into something a person
// can act on, which is why segment inspects its error rather than only printing it.
//
// A refusal is not a crash and should not read like one. "Exit 1, wrapped error
// chain" tells a user their command broke; what actually happened is that the
// system did its job and declined a paper, and the difference matters because one
// of those needs fixing and the other does not.
func explainGateFailure(paperID string, err error) {
	fmt.Fprintf(os.Stderr, "\n%v\n\n", err)

	switch {
	case errors.Is(err, papertype.ErrNotEmpirical):
		fmt.Fprintf(os.Stderr, "This paper is out of scope, so Step 3 did not run and nothing was written.\n")
		fmt.Fprintf(os.Stderr, "To see the evidence behind that decision:\n")
		fmt.Fprintf(os.Stderr, "  epistemicos-cli classify %s\n", paperID)
	case errors.Is(err, papertype.ErrUnverifiedQuotes):
		fmt.Fprintf(os.Stderr, "The classifier cited text that is not in the paper, so its answer was not\n")
		fmt.Fprintf(os.Stderr, "used to route anything. To ask again:\n")
		fmt.Fprintf(os.Stderr, "  epistemicos-cli classify %s --force\n", paperID)
	case errors.Is(err, ports.ErrNotFound):
		fmt.Fprintf(os.Stderr, "Nothing found. Check the id with `epistemicos-cli list`.\n")
	}

	os.Exit(1)
}
