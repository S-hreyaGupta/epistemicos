package papertype

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"strings"
	"testing"

	domain "github.com/EpistemicOS/epistemicos/internal/core/domain/papertype"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

const paper = "# A study of things\n\n## Abstract\n\nWe surveyed 189 extended supply chains and " +
	"estimated a regression model.\n\n## 4 Methodology\n\nData were hand-coded by two raters.\n"

type fakeSource struct{ markdown string }

func (f *fakeSource) Get(context.Context, string) (string, string, error) {
	sum := sha256.Sum256([]byte(f.markdown))
	return f.markdown, hex.EncodeToString(sum[:]), nil
}

type fakeClassifier struct {
	raw   string
	err   error
	calls int
}

func (f *fakeClassifier) Classify(context.Context, string, string) (string, string, error) {
	f.calls++
	if f.err != nil {
		return "", "", f.err
	}
	return f.raw, "test-model", nil
}

type fakeStore struct {
	saved   []ports.PaperTypeRecord
	current *ports.PaperTypeRecord
}

func (f *fakeStore) SaveVerdict(_ context.Context, r *ports.PaperTypeRecord) error {
	f.saved = append(f.saved, *r)
	f.current = r
	return nil
}

func (f *fakeStore) CurrentVerdict(_ context.Context, _, _ string) (*ports.PaperTypeRecord, error) {
	if f.current == nil {
		return nil, ports.ErrNotFound
	}
	return f.current, nil
}

var (
	_ ports.ApprovedMarkdownSource = (*fakeSource)(nil)
	_ ports.PaperTypeClassifier    = (*fakeClassifier)(nil)
	_ ports.PaperTypeStore         = (*fakeStore)(nil)
)

func reply(body, verdict string) string {
	return "<thinking>x</thinking><answer>" + body + "</answer><verdict>" + verdict + "</verdict>"
}

// Quotes here are real substrings of paper, so they verify.
const empiricalAnswer = `{
  "primary_type": "A", "subtype": null, "secondary_type": null,
  "decision_rule": 2, "confidence": "high",
  "evidence": [
    {"quote": "We surveyed 189 extended supply chains", "signals": "own survey"},
    {"quote": "Data were hand-coded by two raters", "signals": "own coding"}
  ],
  "counter_evidence": null, "boundary_case": null,
  "limits_from_selection": null, "rationale": "Its own data.",
  "unclassified_reason": null
}`

// A review, with quotes that are also real. The point of this fixture is the
// TYPE, not the quotes.
const reviewAnswer = `{
  "primary_type": "B", "subtype": "systematic_review", "secondary_type": null,
  "decision_rule": 1, "confidence": "high",
  "evidence": [
    {"quote": "We surveyed 189 extended supply chains", "signals": "screening"},
    {"quote": "Data were hand-coded by two raters", "signals": "extraction"}
  ],
  "counter_evidence": null, "boundary_case": null,
  "limits_from_selection": null, "rationale": "A protocol-driven synthesis.",
  "unclassified_reason": null
}`

// Same verdict as empiricalAnswer, but one quote is invented.
const paraphrasedAnswer = `{
  "primary_type": "A", "subtype": null, "secondary_type": null,
  "decision_rule": 2, "confidence": "high",
  "evidence": [
    {"quote": "We surveyed 189 extended supply chains", "signals": "own survey"},
    {"quote": "The authors conducted eighteen months of fieldwork", "signals": "invented"}
  ],
  "counter_evidence": null, "boundary_case": null,
  "limits_from_selection": null, "rationale": "Its own data.",
  "unclassified_reason": null
}`

func harness(raw string) (*Service, *fakeClassifier, *fakeStore) {
	c := &fakeClassifier{raw: raw}
	s := &fakeStore{}
	return New(&fakeSource{markdown: paper}, c, s), c, s
}

func TestClassify(t *testing.T) {
	svc, _, store := harness(reply(empiricalAnswer, "A"))

	got, err := svc.Classify(context.Background(), "paper-1")
	if err != nil {
		t.Fatalf("Classify: %v", err)
	}

	if got.Record.Verdict.PrimaryType != domain.TypeEmpirical {
		t.Errorf("type = %q", got.Record.Verdict.PrimaryType)
	}
	if got.Record.QuotesVerified != 2 || got.Record.QuotesExpected != 2 {
		t.Errorf("quotes %d of %d, want 2 of 2", got.Record.QuotesVerified, got.Record.QuotesExpected)
	}
	if got.Record.PromptVersion != domain.PromptVersion {
		t.Errorf("prompt version = %q, want %q", got.Record.PromptVersion, domain.PromptVersion)
	}
	if got.Record.Model != "test-model" {
		t.Errorf("model = %q; without it two verdicts cannot be compared", got.Record.Model)
	}
	if got.Record.RawResponse == "" {
		t.Error("the raw response was not kept; the verdict could never be re-examined")
	}
	if len(store.saved) != 1 {
		t.Errorf("saved %d verdicts, want 1", len(store.saved))
	}
}

func TestGate_LetsAnEmpiricalPaperThrough(t *testing.T) {
	svc, _, _ := harness(reply(empiricalAnswer, "A"))

	if _, err := svc.Gate(context.Background(), "paper-1"); err != nil {
		t.Fatalf("Gate refused an empirical paper: %v", err)
	}
	if err := svc.Allow(context.Background(), "paper-1"); err != nil {
		t.Errorf("Allow: %v", err)
	}
}

func TestGate_RefusesASystematicReview(t *testing.T) {
	svc, _, _ := harness(reply(reviewAnswer, "B"))

	_, err := svc.Gate(context.Background(), "paper-1")
	if !errors.Is(err, ErrNotEmpirical) {
		t.Fatalf("error = %v, want ErrNotEmpirical", err)
	}
	// The message has to say what it was taken to be. "Refused" alone gives the
	// person nothing to disagree with.
	if !strings.Contains(err.Error(), "systematic_review") {
		t.Errorf("error = %q, want it to name the subtype", err)
	}
}

// TestGate_RefusesAnUnverifiedVerdictEvenWhenItSaysYes is the case worth having.
//
// The tempting shortcut is to check quotes only on refusals. But an unverified
// "A" is an answer we have just shown to be unsupported, and letting it route a
// paper because we liked the direction is exactly the reasoning the verifier
// exists to prevent.
func TestGate_RefusesAnUnverifiedVerdictEvenWhenItSaysYes(t *testing.T) {
	svc, _, _ := harness(reply(paraphrasedAnswer, "A"))

	result, err := svc.Gate(context.Background(), "paper-1")
	if !errors.Is(err, ErrUnverifiedQuotes) {
		t.Fatalf("error = %v, want ErrUnverifiedQuotes", err)
	}
	if result == nil || !result.Record.Verdict.Empirical() {
		t.Fatal("this test needs a verdict that says A")
	}
	if result.Record.QuotesVerified != 1 {
		t.Errorf("verified %d quotes, want 1 of 2", result.Record.QuotesVerified)
	}
}

// TestClassify_StoresAVerdictWhoseQuotesFailed. The failed verdict is the one
// worth keeping: it is the evidence that the prompt or the model needs work.
func TestClassify_StoresAVerdictWhoseQuotesFailed(t *testing.T) {
	svc, _, store := harness(reply(paraphrasedAnswer, "A"))

	if _, err := svc.Classify(context.Background(), "paper-1"); err != nil {
		t.Fatalf("Classify: %v", err)
	}
	if len(store.saved) != 1 {
		t.Fatalf("saved %d verdicts, want 1 — a paraphrased answer must still be recorded", len(store.saved))
	}
	if store.saved[0].QuotesVerified == store.saved[0].QuotesExpected {
		t.Error("the record does not show the quote failure")
	}
}

// TestVerdict_UsesTheStoredAnswer. Classification costs a model call, so asking
// twice about an unchanged paper should not.
func TestVerdict_UsesTheStoredAnswer(t *testing.T) {
	svc, classifier, _ := harness(reply(empiricalAnswer, "A"))
	ctx := context.Background()

	if _, err := svc.Verdict(ctx, "paper-1"); err != nil {
		t.Fatalf("first: %v", err)
	}
	second, err := svc.Verdict(ctx, "paper-1")
	if err != nil {
		t.Fatalf("second: %v", err)
	}

	if classifier.calls != 1 {
		t.Errorf("called the model %d times, want 1", classifier.calls)
	}
	if !second.Cached {
		t.Error("the second verdict is not marked as cached")
	}
}

// TestClassify_ContractFailureCarriesTheRawResponse. Diagnosing a broken contract
// without seeing what came back is guesswork.
func TestClassify_ContractFailureCarriesTheRawResponse(t *testing.T) {
	svc, _, store := harness("the model ignored the format entirely")

	_, err := svc.Classify(context.Background(), "paper-1")
	if err == nil {
		t.Fatal("accepted a response with no answer block")
	}
	if !strings.Contains(err.Error(), "the model ignored the format entirely") {
		t.Errorf("error = %q, want it to include the raw response", err)
	}
	if len(store.saved) != 0 {
		t.Error("stored a verdict that could not be parsed")
	}
}

func TestClassify_ModelError(t *testing.T) {
	svc, classifier, _ := harness("")
	classifier.err = errors.New("api is down")

	if _, err := svc.Classify(context.Background(), "paper-1"); err == nil {
		t.Fatal("Classify hid a transport failure")
	}
}
