// Package preflight performs startup-time validation of external
// service credentials. Catches "ANTHROPIC_API_KEY is empty" and
// "MATHPIX_APP_ID is malformed" before the first user click rather
// than at first analysis attempt.
//
// Designed to be cheap and non-fatal: probe results are returned to
// the caller (typically main.go), which logs them and adjusts the
// capability surface. A failed probe does not crash the server — the
// affected feature is just advertised as disabled.
package preflight

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// Result is the outcome of a single probe.
type Result struct {
	Service string
	OK      bool
	Reason  string // human-readable detail on failure
}

const probeTimeout = 5 * time.Second

// CheckAnthropic verifies that the configured Anthropic API key is
// shape-valid and accepted by the Messages endpoint. Sends a minimal
// 1-token request to keep the probe cost negligible. Returns OK=true
// only on a 2xx response.
func CheckAnthropic(ctx context.Context, baseURL, key, model string) Result {
	r := Result{Service: "anthropic"}
	if key == "" {
		r.Reason = "ANTHROPIC_API_KEY is empty"
		return r
	}
	if !strings.HasPrefix(key, "sk-ant-") {
		r.Reason = "ANTHROPIC_API_KEY does not look like an Anthropic key (expected sk-ant- prefix)"
		return r
	}
	if model == "" {
		r.Reason = "PAPERLY_LLM_MODEL is empty"
		return r
	}

	probeCtx, cancel := context.WithTimeout(ctx, probeTimeout)
	defer cancel()

	body := map[string]any{
		"model":      model,
		"max_tokens": 1,
		"messages":   []map[string]string{{"role": "user", "content": "ping"}},
	}
	raw, _ := json.Marshal(body)
	req, err := http.NewRequestWithContext(probeCtx, http.MethodPost, baseURL+"/v1/messages", strings.NewReader(string(raw)))
	if err != nil {
		r.Reason = fmt.Sprintf("build request: %v", err)
		return r
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", key)
	req.Header.Set("anthropic-version", "2023-06-01")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		r.Reason = fmt.Sprintf("probe call failed: %v", err)
		return r
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		r.OK = true
		return r
	}
	r.Reason = fmt.Sprintf("Anthropic API returned %d", resp.StatusCode)
	return r
}

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
