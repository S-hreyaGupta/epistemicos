// Package metrics is a tiny in-process metrics registry that emits
// Prometheus-format text. Hand-rolled to avoid a heavy client
// dependency — v2 Phase 2 needs counters and histograms, not the full
// Prometheus client surface.
//
// Three primitives:
//
//   - Counter: monotonically increasing (extraction calls, flags
//     emitted, dismissals).
//   - Gauge: arbitrary float (active analyses).
//   - Histogram: latency buckets (extraction latency per slot type).
//
// Each metric supports labels for low-cardinality breakdowns. Cardinality
// must be bounded — never label by paper ID or flag ID.
package metrics

import (
	"fmt"
	"io"
	"sort"
	"sync"
	"time"
)

// Registry is the in-process metric store.
type Registry struct {
	mu         sync.RWMutex
	counters   map[string]*Counter
	gauges     map[string]*Gauge
	histograms map[string]*Histogram
}

// New returns an empty registry.
func New() *Registry {
	return &Registry{
		counters:   map[string]*Counter{},
		gauges:     map[string]*Gauge{},
		histograms: map[string]*Histogram{},
	}
}

// Counter is monotonically increasing. Inc/Add increment per
// label-value tuple; the same label set returns the same series.
type Counter struct {
	name string
	help string
	mu   sync.Mutex
	vals map[string]float64
}

// Inc increments by 1.
func (c *Counter) Inc(labels ...string) { c.Add(1, labels...) }

// Add increments by n.
func (c *Counter) Add(n float64, labels ...string) {
	key := joinLabels(labels)
	c.mu.Lock()
	c.vals[key] += n
	c.mu.Unlock()
}

// NewCounter registers a counter. Re-registration with the same name is
// idempotent — returns the existing counter.
func (r *Registry) NewCounter(name, help string) *Counter {
	r.mu.Lock()
	defer r.mu.Unlock()
	if c, ok := r.counters[name]; ok {
		return c
	}
	c := &Counter{name: name, help: help, vals: map[string]float64{}}
	r.counters[name] = c
	return c
}

// Gauge is a settable float.
type Gauge struct {
	name string
	help string
	mu   sync.Mutex
	vals map[string]float64
}

func (g *Gauge) Set(v float64, labels ...string) {
	key := joinLabels(labels)
	g.mu.Lock()
	g.vals[key] = v
	g.mu.Unlock()
}

func (g *Gauge) Add(v float64, labels ...string) {
	key := joinLabels(labels)
	g.mu.Lock()
	g.vals[key] += v
	g.mu.Unlock()
}

func (r *Registry) NewGauge(name, help string) *Gauge {
	r.mu.Lock()
	defer r.mu.Unlock()
	if g, ok := r.gauges[name]; ok {
		return g
	}
	g := &Gauge{name: name, help: help, vals: map[string]float64{}}
	r.gauges[name] = g
	return g
}

// Histogram is a fixed-bucket latency observer. Buckets are seconds.
type Histogram struct {
	name    string
	help    string
	buckets []float64
	mu      sync.Mutex
	counts  map[string][]uint64
	sums    map[string]float64
	totals  map[string]uint64
}

// DefaultBuckets cover the analyze pipeline range — fast LLM hits to
// upper-bound timeouts.
var DefaultBuckets = []float64{0.05, 0.1, 0.5, 1, 2, 5, 10, 20, 30, 60}

// Observe records one latency in seconds.
func (h *Histogram) Observe(seconds float64, labels ...string) {
	key := joinLabels(labels)
	h.mu.Lock()
	defer h.mu.Unlock()
	counts := h.counts[key]
	if counts == nil {
		counts = make([]uint64, len(h.buckets))
		h.counts[key] = counts
	}
	for i, bound := range h.buckets {
		if seconds <= bound {
			counts[i]++
		}
	}
	h.sums[key] += seconds
	h.totals[key]++
}

// ObserveSince is a convenience that observes time.Since(start).
func (h *Histogram) ObserveSince(start time.Time, labels ...string) {
	h.Observe(time.Since(start).Seconds(), labels...)
}

func (r *Registry) NewHistogram(name, help string, buckets []float64) *Histogram {
	r.mu.Lock()
	defer r.mu.Unlock()
	if h, ok := r.histograms[name]; ok {
		return h
	}
	if buckets == nil {
		buckets = DefaultBuckets
	}
	h := &Histogram{
		name:    name,
		help:    help,
		buckets: buckets,
		counts:  map[string][]uint64{},
		sums:    map[string]float64{},
		totals:  map[string]uint64{},
	}
	r.histograms[name] = h
	return h
}

// joinLabels collapses ["k1","v1","k2","v2"] → `k1="v1",k2="v2"`.
// Pairs of (key, value); odd-length input is dropped to avoid silent
// data corruption at the metric site.
func joinLabels(kv []string) string {
	if len(kv)%2 != 0 {
		return ""
	}
	if len(kv) == 0 {
		return ""
	}
	parts := make([]string, 0, len(kv)/2)
	for i := 0; i < len(kv); i += 2 {
		parts = append(parts, fmt.Sprintf("%s=%q", kv[i], kv[i+1]))
	}
	return joinComma(parts)
}

func joinComma(parts []string) string {
	out := ""
	for i, p := range parts {
		if i > 0 {
			out += ","
		}
		out += p
	}
	return out
}

// WriteText emits the Prometheus 0.0.4 text format. Stable ordering by
// metric name for diff-friendly output.
func (r *Registry) WriteText(w io.Writer) error {
	r.mu.RLock()
	defer r.mu.RUnlock()

	names := make([]string, 0, len(r.counters)+len(r.gauges)+len(r.histograms))
	for n := range r.counters {
		names = append(names, n)
	}
	for n := range r.gauges {
		names = append(names, n)
	}
	for n := range r.histograms {
		names = append(names, n)
	}
	sort.Strings(names)

	for _, name := range names {
		switch {
		case r.counters[name] != nil:
			if err := writeCounter(w, r.counters[name]); err != nil {
				return err
			}
		case r.gauges[name] != nil:
			if err := writeGauge(w, r.gauges[name]); err != nil {
				return err
			}
		case r.histograms[name] != nil:
			if err := writeHistogram(w, r.histograms[name]); err != nil {
				return err
			}
		}
	}
	return nil
}

func writeCounter(w io.Writer, c *Counter) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if _, err := fmt.Fprintf(w, "# HELP %s %s\n# TYPE %s counter\n", c.name, c.help, c.name); err != nil {
		return err
	}
	keys := sortedKeys(c.vals)
	for _, k := range keys {
		if k == "" {
			if _, err := fmt.Fprintf(w, "%s %g\n", c.name, c.vals[k]); err != nil {
				return err
			}
			continue
		}
		if _, err := fmt.Fprintf(w, "%s{%s} %g\n", c.name, k, c.vals[k]); err != nil {
			return err
		}
	}
	return nil
}

func writeGauge(w io.Writer, g *Gauge) error {
	g.mu.Lock()
	defer g.mu.Unlock()
	if _, err := fmt.Fprintf(w, "# HELP %s %s\n# TYPE %s gauge\n", g.name, g.help, g.name); err != nil {
		return err
	}
	keys := sortedKeys(g.vals)
	for _, k := range keys {
		if k == "" {
			if _, err := fmt.Fprintf(w, "%s %g\n", g.name, g.vals[k]); err != nil {
				return err
			}
			continue
		}
		if _, err := fmt.Fprintf(w, "%s{%s} %g\n", g.name, k, g.vals[k]); err != nil {
			return err
		}
	}
	return nil
}

func writeHistogram(w io.Writer, h *Histogram) error {
	h.mu.Lock()
	defer h.mu.Unlock()
	if _, err := fmt.Fprintf(w, "# HELP %s %s\n# TYPE %s histogram\n", h.name, h.help, h.name); err != nil {
		return err
	}
	keys := sortedKeys(h.totals)
	for _, k := range keys {
		counts := h.counts[k]
		for i, b := range h.buckets {
			lbl := fmt.Sprintf("le=%q", floatToString(b))
			labels := lbl
			if k != "" {
				labels = k + "," + lbl
			}
			if _, err := fmt.Fprintf(w, "%s_bucket{%s} %d\n", h.name, labels, counts[i]); err != nil {
				return err
			}
		}
		infLabel := `le="+Inf"`
		labels := infLabel
		if k != "" {
			labels = k + "," + infLabel
		}
		if _, err := fmt.Fprintf(w, "%s_bucket{%s} %d\n", h.name, labels, h.totals[k]); err != nil {
			return err
		}
		sumLabels := k
		if sumLabels == "" {
			if _, err := fmt.Fprintf(w, "%s_sum %g\n%s_count %d\n", h.name, h.sums[k], h.name, h.totals[k]); err != nil {
				return err
			}
		} else {
			if _, err := fmt.Fprintf(w, "%s_sum{%s} %g\n%s_count{%s} %d\n",
				h.name, sumLabels, h.sums[k], h.name, sumLabels, h.totals[k]); err != nil {
				return err
			}
		}
	}
	return nil
}

func sortedKeys[V any](m map[string]V) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

func floatToString(f float64) string {
	return fmt.Sprintf("%g", f)
}
