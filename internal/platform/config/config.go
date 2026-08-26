// Package config loads runtime configuration from environment
// variables. Kept deliberately small — each field has a default
// where one is sane.
//
// Every field here backs something this system does: connect to Postgres,
// bind the API, stage PDFs, authenticate to Mathpix, and bound inbound
// request rates.
package config

import (
	"fmt"
	"os"
	"strconv"
)

// EnvPrefix is the environment-variable prefix.
//
// Renamed from PAPERLY_ to EPISTEMIC_OS_ on 24 August 2026. The old prefix was
// kept for continuity with a predecessor deployment that no longer exists, and
// a name nobody recognises is worse than a rename nobody has to do.
//
// Load reports the old names explicitly rather than falling back to them: a
// silent fallback would leave two spellings working indefinitely and neither
// one canonical.
const EnvPrefix = "EPISTEMIC_OS_"

// legacyEnvPrefix is only ever used to produce a better error message. Nothing
// reads a value through it.
const legacyEnvPrefix = "PAPERLY_"

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
		DBURL:              env(EnvPrefix+"DB_URL", ""),
		ListenAddr:         env(EnvPrefix+"LISTEN_ADDR", ":9082"),
		PDFDir:             env(EnvPrefix+"PDF_VOLUME", "./data/pdfs"),
		MathpixID:          env("MATHPIX_APP_ID", ""),
		MathpixKey:         env("MATHPIX_APP_KEY", ""),
		CORSAllowedOrigins: env(EnvPrefix+"CORS_ALLOWED_ORIGINS", "*"),
		RateLimitRPM:       envInt(EnvPrefix+"RATE_LIMIT_RPM", 60),
		RateLimitBurst:     envInt(EnvPrefix+"RATE_LIMIT_BURST", 20),
	}

	if c.DBURL == "" {
		// Name the rename rather than the absence. Somebody with a working
		// .env from last week has a set variable and an empty config, and
		// "DB_URL is required" sends them to look at a line that is right
		// there in front of them.
		if os.Getenv(legacyEnvPrefix+"DB_URL") != "" {
			return nil, fmt.Errorf(
				"%sDB_URL is required, but %sDB_URL is set: the prefix was renamed from %s to %s on 24 August 2026. Rename it in your .env",
				EnvPrefix, legacyEnvPrefix, legacyEnvPrefix, EnvPrefix)
		}
		return nil, fmt.Errorf("%sDB_URL is required", EnvPrefix)
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
