// Package preflight performs startup-time validation of external
// service credentials. Catches "MATHPIX_APP_ID is malformed" at boot
// rather than at the first conversion attempt.
//
// Designed to be cheap and non-fatal: probe results are returned to
// the caller (typically main.go), which logs them and adjusts the
// capability surface. A failed probe does not crash the server — the
// affected feature is just advertised as disabled.
package preflight

import (
	"context"
	"fmt"
	"net/http"
	"time"
)

// Result is the outcome of a single probe.
type Result struct {
	Service string
	OK      bool
	Reason  string // human-readable detail on failure
}

const probeTimeout = 5 * time.Second

// CheckMathpix verifies the configured Mathpix credentials. Hits the
// /v3/pdf-results endpoint with a clearly-invalid ID; expects 401 if
// the credentials are wrong, 404 if right. Either is acceptable —
// what we want to detect is a missing/malformed credential set, not
// upstream errors.
func CheckMathpix(ctx context.Context, appID, appKey string) Result {
	r := Result{Service: "mathpix"}
	if appID == "" || appKey == "" {
		r.Reason = "MATHPIX_APP_ID or MATHPIX_APP_KEY is empty"
		return r
	}

	probeCtx, cancel := context.WithTimeout(ctx, probeTimeout)
	defer cancel()

	req, err := http.NewRequestWithContext(probeCtx, http.MethodGet, "https://api.mathpix.com/v3/pdf-results/preflight-probe-noop", nil)
	if err != nil {
		r.Reason = fmt.Sprintf("build request: %v", err)
		return r
	}
	req.Header.Set("app_id", appID)
	req.Header.Set("app_key", appKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		r.Reason = fmt.Sprintf("probe call failed: %v", err)
		return r
	}
	defer resp.Body.Close()
	// 401 → bad credentials. 404 → credentials accepted, no such pdf.
	// Anything 2xx-5xx (other than 401) means credentials were processed.
	if resp.StatusCode == http.StatusUnauthorized {
		r.Reason = "Mathpix rejected credentials (401)"
		return r
	}
	r.OK = true
	return r
}
