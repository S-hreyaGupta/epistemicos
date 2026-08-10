// Package logging adds correlation-ID middleware on top of log/slog.
// Each inbound HTTP request gets an ID that follows the request through
// downstream calls via context. Logs from handlers / services include
// the ID so a single request's life cycle is greppable end-to-end.
package logging

import (
	"context"
	"log/slog"
	"net/http"
	"os"

	"github.com/google/uuid"
)

type ctxKey struct{}

// New returns a slog.Logger configured for JSON output to stdout.
// Suitable for production where logs are scraped; tests should swap in
// their own handler.
func New() *slog.Logger {
	return slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
}

// WithCorrelationID returns a new context carrying the given ID.
func WithCorrelationID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, ctxKey{}, id)
}

// CorrelationIDFromContext fetches the correlation ID; empty if none.
func CorrelationIDFromContext(ctx context.Context) string {
	v, _ := ctx.Value(ctxKey{}).(string)
	return v
}

// CorrelationMiddleware mints a correlation ID per request, stuffs it
// into the request context + response header, and logs a one-line
// access entry on completion.
//
// Header name X-Correlation-ID is standard-ish; clients may also send
// it to thread an upstream ID through this service.
func CorrelationMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			id := r.Header.Get("X-Correlation-ID")
			if id == "" {
				id = uuid.NewString()
			}
			w.Header().Set("X-Correlation-ID", id)

			ctx := WithCorrelationID(r.Context(), id)
			rw := &statusRecorder{ResponseWriter: w, status: 200}
			next.ServeHTTP(rw, r.WithContext(ctx))

			logger.LogAttrs(ctx, slog.LevelInfo, "http",
				slog.String("correlation_id", id),
				slog.String("method", r.Method),
				slog.String("path", r.URL.Path),
				slog.Int("status", rw.status),
			)
		})
	}
}

// statusRecorder lets the middleware see the response status code that
// the inner handler wrote.
type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (s *statusRecorder) WriteHeader(code int) {
	s.status = code
	s.ResponseWriter.WriteHeader(code)
}
