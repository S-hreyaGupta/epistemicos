package security

import (
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

func okHandler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
}

func TestCORS_AllowedOrigin_Echoed(t *testing.T) {
	mw := CORS("http://localhost:3000")(okHandler())
	r := httptest.NewRequest(http.MethodGet, "/x", nil)
	r.Header.Set("Origin", "http://localhost:3000")
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if got := w.Header().Get("Access-Control-Allow-Origin"); got != "http://localhost:3000" {
		t.Errorf("ACAO: %q", got)
	}
}

func TestCORS_DisallowedOrigin_NoHeader(t *testing.T) {
	mw := CORS("http://allowed.example")(okHandler())
	r := httptest.NewRequest(http.MethodGet, "/x", nil)
	r.Header.Set("Origin", "http://evil.example")
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if got := w.Header().Get("Access-Control-Allow-Origin"); got != "" {
		t.Errorf("expected no ACAO, got %q", got)
	}
}

func TestCORS_Wildcard_AllowsAny(t *testing.T) {
	mw := CORS("*")(okHandler())
	r := httptest.NewRequest(http.MethodGet, "/x", nil)
	r.Header.Set("Origin", "http://anything.example")
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if got := w.Header().Get("Access-Control-Allow-Origin"); got != "http://anything.example" {
		t.Errorf("ACAO: %q", got)
	}
}

func TestCORS_OptionsPreflight_ShortCircuits(t *testing.T) {
	called := false
	inner := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		called = true
		w.WriteHeader(http.StatusOK)
	})
	mw := CORS("*")(inner)
	r := httptest.NewRequest(http.MethodOptions, "/x", nil)
	r.Header.Set("Origin", "http://allowed.example")
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if called {
		t.Errorf("inner handler should not run on OPTIONS")
	}
	if w.Code != http.StatusNoContent {
		t.Errorf("status: %d", w.Code)
	}
}

func TestSecurityHeaders_AlwaysSet(t *testing.T) {
	mw := SecurityHeaders()(okHandler())
	r := httptest.NewRequest(http.MethodGet, "/x", nil)
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	wants := map[string]string{
		"X-Content-Type-Options": "nosniff",
		"X-Frame-Options":        "DENY",
		"Referrer-Policy":        "no-referrer",
	}
	for k, v := range wants {
		if got := w.Header().Get(k); got != v {
			t.Errorf("%s: got %q, want %q", k, got, v)
		}
	}
	if w.Header().Get("Strict-Transport-Security") != "" {
		t.Errorf("HSTS should not be set on plain HTTP")
	}
}

func TestSecurityHeaders_HSTSOnHTTPS(t *testing.T) {
	mw := SecurityHeaders()(okHandler())
	r := httptest.NewRequest(http.MethodGet, "/x", nil)
	r.Header.Set("X-Forwarded-Proto", "https")
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if w.Header().Get("Strict-Transport-Security") == "" {
		t.Errorf("HSTS should be set when X-Forwarded-Proto=https")
	}
}

func TestRateLimit_BurstThenBlock(t *testing.T) {
	mw := RateLimit(RateLimitConfig{
		RequestsPerMinute: 60,
		Burst:             3,
		Match:             MutatingRequestMatcher,
	})(okHandler())

	// Three POSTs from the same IP should succeed (burst).
	for i := 0; i < 3; i++ {
		r := httptest.NewRequest(http.MethodPost, "/x", nil)
		r.RemoteAddr = "1.2.3.4:1234"
		w := httptest.NewRecorder()
		mw.ServeHTTP(w, r)
		if w.Code != http.StatusOK {
			t.Errorf("burst request %d unexpectedly blocked: status %d", i+1, w.Code)
		}
	}
	// Fourth POST in the same instant should be rate-limited.
	r := httptest.NewRequest(http.MethodPost, "/x", nil)
	r.RemoteAddr = "1.2.3.4:1234"
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if w.Code != http.StatusTooManyRequests {
		t.Errorf("expected 429 after burst, got %d", w.Code)
	}
}

func TestRateLimit_GETsNotLimited(t *testing.T) {
	mw := RateLimit(RateLimitConfig{
		RequestsPerMinute: 1,
		Burst:             1,
		Match:             MutatingRequestMatcher,
	})(okHandler())
	// Many GETs from the same IP should never block.
	for i := 0; i < 10; i++ {
		r := httptest.NewRequest(http.MethodGet, "/x", nil)
		r.RemoteAddr = "1.2.3.4:1234"
		w := httptest.NewRecorder()
		mw.ServeHTTP(w, r)
		if w.Code != http.StatusOK {
			t.Errorf("GET %d unexpectedly blocked: %d", i, w.Code)
		}
	}
}

func TestRateLimit_PerIPIsolation(t *testing.T) {
	mw := RateLimit(RateLimitConfig{
		RequestsPerMinute: 60,
		Burst:             1,
		Match:             MutatingRequestMatcher,
	})(okHandler())

	// Each IP gets its own bucket.
	var wg sync.WaitGroup
	for _, ip := range []string{"1.1.1.1:80", "2.2.2.2:80"} {
		wg.Add(1)
		go func(ip string) {
			defer wg.Done()
			r := httptest.NewRequest(http.MethodPost, "/x", nil)
			r.RemoteAddr = ip
			w := httptest.NewRecorder()
			mw.ServeHTTP(w, r)
			if w.Code != http.StatusOK {
				t.Errorf("IP %s should have its own bucket, got %d", ip, w.Code)
			}
		}(ip)
	}
	wg.Wait()
}

func TestRateLimit_ForwardedForUsed(t *testing.T) {
	mw := RateLimit(RateLimitConfig{
		RequestsPerMinute: 60,
		Burst:             1,
		Match:             MutatingRequestMatcher,
	})(okHandler())

	// First request from X-Forwarded-For 1.1.1.1 — uses up that bucket.
	r := httptest.NewRequest(http.MethodPost, "/x", nil)
	r.RemoteAddr = "10.0.0.1:0"
	r.Header.Set("X-Forwarded-For", "1.1.1.1, 10.0.0.1")
	w := httptest.NewRecorder()
	mw.ServeHTTP(w, r)
	if w.Code != http.StatusOK {
		t.Fatalf("first XFF request blocked: %d", w.Code)
	}

	// Second request with same XFF — should now be blocked.
	r2 := httptest.NewRequest(http.MethodPost, "/x", nil)
	r2.RemoteAddr = "10.0.0.1:0"
	r2.Header.Set("X-Forwarded-For", "1.1.1.1, 10.0.0.1")
	w2 := httptest.NewRecorder()
	mw.ServeHTTP(w2, r2)
	if w2.Code != http.StatusTooManyRequests {
		t.Errorf("expected 429 on second same-XFF request, got %d", w2.Code)
	}
}

func TestRateLimit_Refill(t *testing.T) {
	// Use the internal type to inject a fake clock.
	rl := &rateLimiter{
		fillEvery: 10 * time.Millisecond,
		burst:     1,
		buckets:   make(map[string]*bucket),
		now:       func() time.Time { return time.Unix(0, 0) },
	}
	if !rl.allow("ip1") {
		t.Fatal("first allow should succeed")
	}
	if rl.allow("ip1") {
		t.Fatal("burst consumed; second allow should fail at same instant")
	}
	// Advance clock by enough to refill one token.
	rl.now = func() time.Time { return time.Unix(0, int64(20*time.Millisecond)) }
	if !rl.allow("ip1") {
		t.Errorf("after refill, allow should succeed")
	}
}
