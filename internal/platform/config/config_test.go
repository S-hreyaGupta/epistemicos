package config

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/joho/godotenv"
)

// The real .env carries a tab rather than a space after MATHPIX_APP_ID=:
//
//	MATHPIX_APP_ID=\tepistemicos_9c30aa_644a3b
//
// Spotted 17 September. godotenv's parser trims leading whitespace from a
// value, twice over, so the loaded value is clean — but that is a property of a
// dependency, established by reading its source, and nothing in this repository
// held it. If a future godotenv stopped trimming, or the loader were replaced,
// the app ID would silently carry a leading tab and Mathpix would reject it
// with an authentication error that points nowhere near the cause.
//
// This runs the real path: a .env on disk, godotenv, then Load.
func TestLoadTrimsWhitespaceAfterEquals(t *testing.T) {
	cases := []struct {
		name string
		line string
	}{
		{"tab, as the real .env has it", "MATHPIX_APP_ID=\tepistemicos_9c30aa_644a3b"},
		{"space", "MATHPIX_APP_ID= epistemicos_9c30aa_644a3b"},
		{"several spaces", "MATHPIX_APP_ID=   epistemicos_9c30aa_644a3b"},
		{"tab both sides", "MATHPIX_APP_ID=\tepistemicos_9c30aa_644a3b\t"},
	}

	const want = "epistemicos_9c30aa_644a3b"

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			dir := t.TempDir()
			envFile := filepath.Join(dir, ".env")
			body := c.line + "\n" + EnvPrefix + "DB_URL=postgres://u:p@h:5432/d\n"
			if err := os.WriteFile(envFile, []byte(body), 0o600); err != nil {
				t.Fatal(err)
			}

			// godotenv does not overwrite variables already set, so the
			// environment has to be clear for the file to be what is read.
			t.Setenv("MATHPIX_APP_ID", "")
			os.Unsetenv("MATHPIX_APP_ID")
			t.Setenv(EnvPrefix+"DB_URL", "")
			os.Unsetenv(EnvPrefix + "DB_URL")

			if err := godotenv.Load(envFile); err != nil {
				t.Fatalf("godotenv could not read the file: %v", err)
			}

			cfg, err := Load()
			if err != nil {
				t.Fatalf("Load: %v", err)
			}
			if cfg.MathpixID != want {
				t.Errorf("app ID is %q, want %q", cfg.MathpixID, want)
				if strings.TrimLeft(cfg.MathpixID, " \t") == want {
					t.Log("the value is right apart from leading whitespace, " +
						"which is exactly the failure this test exists for: " +
						"Mathpix would reject it with an authentication error " +
						"pointing nowhere near the cause")
				}
			}
		})
	}
}

// The rename of 24 August left people with working .env files whose variables
// were suddenly ignored. Load names the rename rather than reporting an absence,
// and that message is the whole value of the branch.
func TestLoadNamesTheRenameRatherThanTheAbsence(t *testing.T) {
	t.Setenv(EnvPrefix+"DB_URL", "")
	os.Unsetenv(EnvPrefix + "DB_URL")
	t.Setenv(legacyEnvPrefix+"DB_URL", "postgres://u:p@h:5432/d")

	_, err := Load()
	if err == nil {
		t.Fatal("expected an error when only the legacy variable is set")
	}
	if !strings.Contains(err.Error(), legacyEnvPrefix+"DB_URL") {
		t.Errorf("the error does not mention the legacy variable that is set, "+
			"so it sends the reader to look at a line that is already correct: %v", err)
	}
	if !strings.Contains(err.Error(), "renamed") {
		t.Errorf("the error does not say the prefix was renamed: %v", err)
	}
}

func TestLoadRequiresADatabaseURL(t *testing.T) {
	t.Setenv(EnvPrefix+"DB_URL", "")
	os.Unsetenv(EnvPrefix + "DB_URL")
	t.Setenv(legacyEnvPrefix+"DB_URL", "")
	os.Unsetenv(legacyEnvPrefix + "DB_URL")

	if _, err := Load(); err == nil {
		t.Fatal("Load succeeded with no database URL configured")
	}
}
