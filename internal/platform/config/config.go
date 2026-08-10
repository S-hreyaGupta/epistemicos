// Package config loads runtime configuration from environment
// variables. Kept deliberately small — each field has a default
// where one is sane.
//
// Every field here backs something this system actually does. There are no
// LLM settings, no extractor knobs and no analysis toggle, because this
// system makes no LLM calls and runs no analysis — it downloads a PDF,
// converts it, and stores the result.
package config

import (
	"fmt"
	"os"
	"strconv"
)

// EnvPrefix is the environment-variable prefix. Retained as PAPERLY_ for
// continuity with existing deployments and .env files; renaming it is a
// breaking change for anything already running.
const EnvPrefix = "PAPERLY_"

// Config holds the runtime knobs for epistemicos-api and epistemicos-cli.
type Config struct {
	// DBURL is the Postgres connection string. Required.
	DBURL string

	// ListenAddr is the API bind address.
	ListenAddr string

	// PDFDir is where downloaded PDFs are staged before conversion.
	PDFDir string

	// MathpixID and MathpixKey authenticate the PDF→markdown conversion.
	// Startup is allowed without them so the service can serve reads, but
	// ingest will fail at processing time and /api/v1/capabilities reports
	// mathpix_enabled=false.
	MathpixID  string
	MathpixKey string

	// CORSAllowedOrigins is a comma-separated list of origins or "*".
	// Default "*" enables permissive CORS for local dev; production
	// deploys should set it to the actual client origin.
	CORSAllowedOrigins string

	// RateLimitRPM is the sustained per-IP requests-per-minute on
	// mutating endpoints. 0 disables the limiter.
	RateLimitRPM int

	// RateLimitBurst is the per-IP burst capacity.
	RateLimitBurst int
}

// Load reads environment variables and returns a populated Config, or
// an error if a required variable is missing.
func Load() (*Config, error) {
	c := &Config{
		DBURL:              env("PAPERLY_DB_URL", ""),
		ListenAddr:         env("PAPERLY_LISTEN_ADDR", ":9082"),
		PDFDir:             env("PAPERLY_PDF_VOLUME", "./data/pdfs"),
		MathpixID:          env("MATHPIX_APP_ID", ""),
		MathpixKey:         env("MATHPIX_APP_KEY", ""),
		CORSAllowedOrigins: env("PAPERLY_CORS_ALLOWED_ORIGINS", "*"),
		RateLimitRPM:       envInt("PAPERLY_RATE_LIMIT_RPM", 60),
		RateLimitBurst:     envInt("PAPERLY_RATE_LIMIT_BURST", 20),
	}

	if c.DBURL == "" {
		return nil, fmt.Errorf("PAPERLY_DB_URL is required")
	}

	return c, nil
}

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func envInt(key string, def int) int {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return def
	}
	return n
}
