// epistemicos-api is the HTTP server for the ingest path:
// POST/GET /api/v1/papers, /health, /metrics.
//
// Its whole job is PDF in, markdown out, persisted with its content hash.
package main

import (
	"context"
	"fmt"
	stdhttp "net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"

	httpadapter "github.com/EpistemicOS/epistemicos/internal/adapters/primary/http"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/hasher"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/mathpix"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/pdfdownloader"
	"github.com/EpistemicOS/epistemicos/internal/adapters/secondary/store"
	"github.com/EpistemicOS/epistemicos/internal/core/services/ingest"
	"github.com/EpistemicOS/epistemicos/internal/platform/config"
	"github.com/EpistemicOS/epistemicos/internal/platform/logging"
	"github.com/EpistemicOS/epistemicos/internal/platform/metrics"
	"github.com/EpistemicOS/epistemicos/internal/platform/preflight"
	"github.com/EpistemicOS/epistemicos/internal/platform/security"
)

func main() {
	_ = godotenv.Load()

	cfg, err := config.Load()
	if err != nil {
		fatalf("config: %v", err)
	}

	if err := store.RunMigrations(cfg.DBURL); err != nil {
		fatalf("migrations: %v", err)
	}

	pool, err := pgxpool.New(context.Background(), cfg.DBURL)
	if err != nil {
		fatalf("pgxpool: %v", err)
	}
	defer pool.Close()

	if err := ensureDatabaseIdentity(context.Background(), pool, cfg.DBURL); err != nil {
		fatalf("database identity preflight: %v\n"+
			"  The connection string and the server disagree. Either repoint the\n"+
			"  configuration or rename the database; do not proceed with the two\n"+
			"  out of step.", err)
	}

	metricsReg := metrics.New()

	paperStore := store.NewPostgresPaperStore(pool)
	downloader := pdfdownloader.New()
	processor := mathpix.New(cfg.MathpixID, cfg.MathpixKey)
	h := hasher.New()

	ingestSvc := ingest.New(paperStore, downloader, processor, h, cfg.PDFDir)

	// Mathpix preflight: a deployment with no credentials can still start
	// and serve reads, but the capabilities surface says so rather than
	// letting an upload fail at the point of conversion.
	mathpixOK := cfg.MathpixID != "" && cfg.MathpixKey != ""
	if mathpixOK {
		res := preflight.CheckMathpix(context.Background(), cfg.MathpixID, cfg.MathpixKey)
		if !res.OK {
			fmt.Fprintf(os.Stderr, "warn: mathpix preflight failed: %s\n", res.Reason)
			mathpixOK = false
		}
	}

	srv := httpadapter.NewServer(
		ingestSvc,
		httpadapter.WithMetrics(metricsReg),
		httpadapter.WithCapabilities(httpadapter.Capabilities{
			MathpixEnabled: mathpixOK,
		}),
	)

	logger := logging.New()

	// Middleware chain (outer→inner):
	//   CORS → SecurityHeaders → RateLimit → CorrelationID → API
	var handler stdhttp.Handler = srv.Handler()
	handler = logging.CorrelationMiddleware(logger)(handler)
	if cfg.RateLimitRPM > 0 {
		handler = security.RateLimit(security.RateLimitConfig{
			RequestsPerMinute: cfg.RateLimitRPM,
			Burst:             cfg.RateLimitBurst,
			Match:             security.MutatingRequestMatcher,
		})(handler)
	}
	handler = security.SecurityHeaders()(handler)
	handler = security.CORS(cfg.CORSAllowedOrigins)(handler)

	server := &stdhttp.Server{
		Addr:              cfg.ListenAddr,
		Handler:           handler,
		ReadHeaderTimeout: 10 * time.Second,
	}

	// Graceful shutdown on SIGINT/SIGTERM.
	idle := make(chan struct{})
	go func() {
		sig := make(chan os.Signal, 1)
		signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
		<-sig
		ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()
		_ = server.Shutdown(ctx)
		close(idle)
	}()

	fmt.Printf("epistemicos-api listening on %s\n", cfg.ListenAddr)
	if err := server.ListenAndServe(); err != nil && err != stdhttp.ErrServerClosed {
		fatalf("listen: %v", err)
	}
	<-idle
}

// identityQuerier is the one thing the preflight needs from the pool: a row
// carrying two strings. An interface, so the refusal can be exercised without
// a Postgres server — *pgxpool.Pool satisfies it.
type identityQuerier interface {
	QueryRow(ctx context.Context, sql string, args ...any) pgx.Row
}

// ensureDatabaseIdentity asks the server what it is and returns an error if
// startup must not continue.
//
// The database has to be the one configuration names. POSTGRES_DB and
// POSTGRES_USER apply only at first initialisation, so the prefix rename of
// 24 August changed the configuration and could not change the volume: for
// three weeks the config said epistemicos and the server was paperly. Nothing
// noticed because nothing compared them, and this is the comparison.
//
// Fatal rather than a warning, unlike the Mathpix probe. A deployment missing
// Mathpix credentials can still serve reads honestly; a deployment writing to
// a database other than the one it reports is producing evidence attributed to
// the wrong place, and every count and hash downstream inherits that.
//
// This was four statements inside main() until 18 September, which meant the
// decision to abort could not be reached by any control: thirteen controls
// covered CheckDatabaseIdentity returning not-OK, and nothing covered what the
// API then did about it. Package main has no test file and `go test ./...`
// reported "[no test files]" for it on every run, so changing the preflight to
// a warning, or deleting the call, would have passed everything. Extracted so
// that the refusal itself is testable; see main_test.go.
func ensureDatabaseIdentity(ctx context.Context, q identityQuerier, dsn string) error {
	var gotDB, gotUser string
	if err := q.QueryRow(ctx, preflight.IdentityQuery).Scan(&gotDB, &gotUser); err != nil {
		return fmt.Errorf("could not ask the server what it is: %w", err)
	}
	if res := preflight.CheckDatabaseIdentity(dsn, gotDB, gotUser); !res.OK {
		return fmt.Errorf("%s", res.Reason)
	}
	return nil
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
