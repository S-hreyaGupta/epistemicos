package metrics

import (
	"bytes"
	"strings"
	"testing"
)

func TestCounter_AccumulatesPerLabelSet(t *testing.T) {
	r := New()
	c := r.NewCounter("paperly_extractor_calls_total", "extractor invocations")
	c.Inc("type", "method_of_record")
	c.Inc("type", "method_of_record")
	c.Inc("type", "disclosure")

	var buf bytes.Buffer
	if err := r.WriteText(&buf); err != nil {
		t.Fatalf("WriteText: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, `paperly_extractor_calls_total{type="method_of_record"} 2`) {
		t.Errorf("missing series:\n%s", out)
	}
	if !strings.Contains(out, `paperly_extractor_calls_total{type="disclosure"} 1`) {
		t.Errorf("missing series:\n%s", out)
	}
}

func TestCounter_NoLabels(t *testing.T) {
	r := New()
	c := r.NewCounter("paperly_analyze_total", "analyses")
	c.Add(3)
	var buf bytes.Buffer
	_ = r.WriteText(&buf)
	if !strings.Contains(buf.String(), "paperly_analyze_total 3") {
		t.Errorf("missing unlabeled series:\n%s", buf.String())
	}
}

func TestHistogram_Buckets(t *testing.T) {
	r := New()
	h := r.NewHistogram("paperly_extractor_latency_seconds", "latency", []float64{0.1, 1, 10})
	h.Observe(0.05) // bucket 0.1
	h.Observe(0.5)  // bucket 1
	h.Observe(5)    // bucket 10
	h.Observe(50)   // +Inf only

	var buf bytes.Buffer
	_ = r.WriteText(&buf)
	out := buf.String()
	if !strings.Contains(out, "paperly_extractor_latency_seconds_count 4") {
		t.Errorf("expected count=4:\n%s", out)
	}
	if !strings.Contains(out, `paperly_extractor_latency_seconds_bucket{le="0.1"} 1`) {
		t.Errorf("expected 0.1 bucket=1:\n%s", out)
	}
	if !strings.Contains(out, `paperly_extractor_latency_seconds_bucket{le="1"} 2`) {
		t.Errorf("expected 1 bucket=2 (cumulative):\n%s", out)
	}
	if !strings.Contains(out, `paperly_extractor_latency_seconds_bucket{le="10"} 3`) {
		t.Errorf("expected 10 bucket=3 (cumulative):\n%s", out)
	}
	if !strings.Contains(out, `paperly_extractor_latency_seconds_bucket{le="+Inf"} 4`) {
		t.Errorf("expected +Inf bucket=4:\n%s", out)
	}
}

func TestGauge_SetAndAdd(t *testing.T) {
	r := New()
	g := r.NewGauge("paperly_active_analyses", "in-flight")
	g.Set(5)
	g.Add(-2)
	var buf bytes.Buffer
	_ = r.WriteText(&buf)
	if !strings.Contains(buf.String(), "paperly_active_analyses 3") {
		t.Errorf("expected 3:\n%s", buf.String())
	}
}

func TestRegister_Idempotent(t *testing.T) {
	r := New()
	c1 := r.NewCounter("x", "h")
	c2 := r.NewCounter("x", "h")
	if c1 != c2 {
		t.Errorf("re-registration should return the same counter")
	}
}
