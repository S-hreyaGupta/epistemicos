// Package security holds the HTTP middleware that hardens paperly-api
// for production exposure: CORS, security headers, and a simple
// per-IP token-bucket rate limiter for mutating endpoints.
//
// Intentionally narrow scope — auth and TLS termination are deferred
// to the reverse proxy / ingress layer.
package security

import (
	"net"
	"net/http"
	"strings"
	"sync"
	"time"
)

// CORS returns a middleware that adds the standard CORS headers and
// short-circuits OPTIONS preflights. allowedOrigins of "*" enables
// permissive CORS (development); a comma-separated list of origins
// restricts to those.
func CORS(allowedOrigins string) func(http.Handler) http.Handler {
	parsed := parseOriginList(allowedOrigins)
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			origin := r.Header.Get("Origin")
			if origin != "" && allowed(parsed, origin) {
				w.Header().Set("Access-Control-Allow-Origin", origin)
				w.Header().Set("Vary", "Origin")
				w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
				w.Header().Set("Access-Control-Allow-Headers", "Content-Type, X-Correlation-ID")
				w.Header().Set("Access-Control-Max-Age", "600")
			}
			if r.Method == http.MethodOptions {
				w.WriteHeader(http.StatusNoContent)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

// SecurityHeaders adds a baseline set of security response headers.
// HSTS is only emitted when the request appears to be HTTPS to avoid
// pinning over plain HTTP (which a browser would refuse anyway, but
// also breaks local-dev iteration).
func SecurityHeaders() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			h := w.Header()
			h.Set("X-Content-Type-Options", "nosniff")
			h.Set("X-Frame-Options", "DENY")
			h.Set("Referrer-Policy", "no-referrer")
			h.Set("Permissions-Policy", "interest-cohort=()")
			if isHTTPS(r) {
				h.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
			}
			next.ServeHTTP(w, r)
		})
	}
}

// RateLimitConfig configures the token-bucket limiter. Refill rate and
// burst are per-IP; the limiter only applies to method paths whose
// matcher returns true (typically POST endpoints).
type RateLimitConfig struct {
	RequestsPerMinute int                      // sustained per-IP rate
	Burst             int                      // bucket capacity
	Match             func(*http.Request) bool // returns true if rate limit applies
}

// RateLimit returns middleware enforcing a per-IP token bucket on
// requests that match cfg.Match. Buckets are stored in memory and
// expire after 10 minutes of inactivity (a janitor goroutine sweeps).
func RateLimit(cfg RateLimitConfig) func(http.Handler) http.Handler {
	if cfg.RequestsPerMinute <= 0 {
		cfg.RequestsPerMinute = 60
	}
	if cfg.Burst <= 0 {
		cfg.Burst = 10
	}
	rl := &rateLimiter{
		fillEvery: time.Minute / time.Duration(cfg.RequestsPerMinute),
		burst:     cfg.Burst,
		buckets:   make(map[string]*bucket),
		now:       time.Now,
	}
	go rl.sweep()
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if cfg.Match != nil && !cfg.Match(r) {
				next.ServeHTTP(w, r)
				return
			}
			if !rl.allow(clientIP(r)) {
				w.Header().Set("Retry-After", "60")
				http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

// MutatingRequestMatcher returns true for HTTP methods that mutate
// state — the natural target for rate limiting. Convenience helper
// callers pass as RateLimitConfig.Match.
func MutatingRequestMatcher(r *http.Request) bool {
	switch r.Method {
	case http.MethodPost, http.MethodPut, http.MethodPatch, http.MethodDelete:
		return true
	default:
		return false
	}
}

// --- helpers ---

func parseOriginList(s string) []string {
	if strings.TrimSpace(s) == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p != "" {
			out = append(out, p)
		}
	}
	return out
}

func allowed(list []string, origin string) bool {
	for _, o := range list {
		if o == "*" || o == origin {
			return true
		}
	}
	return false
}

func isHTTPS(r *http.Request) bool {
	if r.TLS != nil {
		return true
	}
	// Honour X-Forwarded-Proto when behind a TLS-terminating proxy.
	return strings.EqualFold(r.Header.Get("X-Forwarded-Proto"), "https")
}

// clientIP extracts the client IP from X-Forwarded-For (first hop) or
// falls back to RemoteAddr. Used as the rate-limit bucket key.
func clientIP(r *http.Request) string {
	if xf := r.Header.Get("X-Forwarded-For"); xf != "" {
		// "client, proxy1, proxy2" — take the leftmost.
		if comma := strings.IndexByte(xf, ','); comma >= 0 {
			return strings.TrimSpace(xf[:comma])
		}
		return strings.TrimSpace(xf)
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

type bucket struct {
	tokens    float64
	updatedAt time.Time
}

type rateLimiter struct {
	mu        sync.Mutex
	buckets   map[string]*bucket
	fillEvery time.Duration
	burst     int
	now       func() time.Time
}

// allow consumes one token from the IP's bucket. Returns true if the
// caller may proceed, false if the bucket is empty.
func (rl *rateLimiter) allow(ip string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	now := rl.now()
	b, ok := rl.buckets[ip]
	if !ok {
		b = &bucket{tokens: float64(rl.burst), updatedAt: now}
		rl.buckets[ip] = b
	}
	// Refill since last access.
	elapsed := now.Sub(b.updatedAt)
	b.tokens += float64(elapsed) / float64(rl.fillEvery)
	if b.tokens > float64(rl.burst) {
		b.tokens = float64(rl.burst)
	}
	b.updatedAt = now
	if b.tokens < 1.0 {
		return false
	}
	b.tokens -= 1.0
	return true
}

// sweep periodically drops idle bucket entries to bound memory.
func (rl *rateLimiter) sweep() {
	ticker := time.NewTicker(2 * time.Minute)
	defer ticker.Stop()
	for now := range ticker.C {
		rl.mu.Lock()
		for ip, b := range rl.buckets {
			if now.Sub(b.updatedAt) > 10*time.Minute {
				delete(rl.buckets, ip)
			}
		}
		rl.mu.Unlock()
	}
}
