package papertype

import (
	"strings"
	"testing"
)

// The manuscript these quotes are drawn from. Written with the typography Mathpix
// actually emits — a curly apostrophe, an en dash, a mid-sentence line break —
// because that typography is the whole reason VerifyQuotes is not
// strings.Contains.
const manuscript = "# Collective disclosure in extended supply chains\n\n" +
	"## Abstract\n\nWe surveyed 189 extended supply chains and estimated a regression\n" +
	"model of disclosure on structure. The firm’s own reporting was coded by hand.\n\n" +
	"## 4 Methodology\n\nData were drawn from Bloomberg and hand-coded — two raters,\n" +
	"with disagreements resolved by discussion.\n"

func response(answer, verdict string) string {
	return "<thinking>reasoning here</thinking>\n<answer>\n" + answer + "\n</answer>\n<verdict>" + verdict + "</verdict>"
}

const answerA = `{
  "primary_type": "A",
  "subtype": null,
  "secondary_type": null,
  "decision_rule": 2,
  "confidence": "high",
  "evidence": [
    {"quote": "We surveyed 189 extended supply chains and estimated a regression", "signals": "own data collection"},
    {"quote": "Data were drawn from Bloomberg and hand-coded", "signals": "archival dataset"}
  ],
  "counter_evidence": null,
  "boundary_case": null,
  "limits_from_selection": null,
  "rationale": "The paper collects and analyses its own data.",
  "unclassified_reason": null
}`

func TestParse(t *testing.T) {
	got, err := Parse(response(answerA, "A"))
	if err != nil {
		t.Fatalf("Parse: %v", err)
	}

	if got.PrimaryType != TypeEmpirical {
		t.Errorf("primary = %q, want %q", got.PrimaryType, TypeEmpirical)
	}
	if got.DecisionRule != 2 {
		t.Errorf("decision_rule = %d, want 2", got.DecisionRule)
	}
	if len(got.Evidence) != 2 {
		t.Errorf("evidence = %d items, want 2", len(got.Evidence))
	}
	if !got.Empirical() {
		t.Error("an A verdict is not Empirical()")
	}
}

// TestParse_VerdictTagMustAgree. The answer arrives twice on purpose. A reply cut
// off mid-JSON has no verdict tag at all, and one whose tag disagrees with its own
// JSON did not follow the contract whatever else it says.
func TestParse_VerdictTagMustAgree(t *testing.T) {
	_, err := Parse(response(answerA, "B"))
	if err == nil {
		t.Fatal("accepted a response whose verdict tag contradicts its JSON")
	}
	if !strings.Contains(err.Error(), "primary_type") {
		t.Errorf("error = %q, want it to name the disagreement", err)
	}
}

func TestParse_Malformed(t *testing.T) {
	cases := []struct {
		name, raw, want string
	}{
		{"no answer block", "<verdict>A</verdict>", "no <answer> block"},
		{"no verdict block", "<answer>" + answerA + "</answer>", "no <verdict> block"},
		{"not json", response("this is not json", "A"), "not valid JSON"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			_, err := Parse(c.raw)
			if err == nil {
				t.Fatal("accepted a malformed response")
			}
			if !strings.Contains(err.Error(), c.want) {
				t.Errorf("error = %q, want it to mention %q", err, c.want)
			}
		})
	}
}

// TestParse_FencedJSON. Models wrap JSON in a fence despite being told not to.
// Trimming it hides nothing, because a non-JSON remainder still fails to decode.
func TestParse_FencedJSON(t *testing.T) {
	raw := response("```json\n"+answerA+"\n```", "A")
	if _, err := Parse(raw); err != nil {
		t.Errorf("rejected fenced JSON: %v", err)
	}
}

func TestValidate(t *testing.T) {
	base := func() Verdict {
		v, err := Parse(response(answerA, "A"))
		if err != nil {
			t.Fatalf("base: %v", err)
		}
		return v
	}

	cases := []struct {
		name string
		mut  func(*Verdict)
		want string
	}{
		{"bad type", func(v *Verdict) { v.PrimaryType = "E" }, "not one of A, B, C, D"},
		{"rule zero", func(v *Verdict) { v.DecisionRule = 0 }, "decision_rule is 0"},
		{"rule six", func(v *Verdict) { v.DecisionRule = 6 }, "decision_rule is 6"},
		{"bad confidence", func(v *Verdict) { v.Confidence = "very high" }, "not high, medium or low"},
		{"A with subtype", func(v *Verdict) { v.Subtype = SubtypeMetaAnalysis }, "must not carry a subtype"},
		{"B without subtype", func(v *Verdict) { v.PrimaryType = TypeSynthesis }, "requires a subtype"},
		{"D without subtype", func(v *Verdict) { v.PrimaryType = TypeFormal }, "requires a subtype"},
		{"secondary equals primary", func(v *Verdict) { v.SecondaryType = TypeEmpirical }, "equals primary_type"},
		{"bad secondary", func(v *Verdict) { v.SecondaryType = "Z" }, "secondary_type"},
		{"reason on a classified verdict", func(v *Verdict) { v.UnclassifiedReason = "why" }, "unclassified_reason set"},
		{"one evidence item", func(v *Verdict) { v.Evidence = v.Evidence[:1] }, "want 2 to 4"},
		{"no evidence", func(v *Verdict) { v.Evidence = nil }, "want 2 to 4"},
		{"empty quote", func(v *Verdict) { v.Evidence[0].Quote = "  " }, "empty quote"},
		{"counter points nowhere", func(v *Verdict) {
			v.CounterEvidence = &CounterEvidence{Quote: "a quote", PointsTo: "Z"}
		}, "points_to"},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			v := base()
			c.mut(&v)
			err := v.validate()
			if err == nil {
				t.Fatal("validate accepted it")
			}
			if !strings.Contains(err.Error(), c.want) {
				t.Errorf("error = %q, want it to mention %q", err, c.want)
			}
		})
	}
}

// TestValidate_UnclassifiedNeedsAReason. Refusal is a real answer, and the whole
// reason refusal is made cheap is that it teaches us something. Without the reason
// it is indistinguishable from a model that gave up.
func TestValidate_UnclassifiedNeedsAReason(t *testing.T) {
	v, err := Parse(response(answerA, "A"))
	if err != nil {
		t.Fatalf("base: %v", err)
	}
	v.PrimaryType = TypeUnclassified

	if err := v.validate(); err == nil || !strings.Contains(err.Error(), "unclassified_reason") {
		t.Fatalf("error = %v, want it to demand a reason", err)
	}

	v.UnclassifiedReason = "the input breaks off mid-sentence"
	if err := v.validate(); err != nil {
		t.Errorf("rejected an UNCLASSIFIED verdict that gave its reason: %v", err)
	}
}

// TestEmpirical is the routing rule. Getting the B-with-secondary-A case wrong
// would park a paper that carries a real empirical study of its own.
func TestEmpirical(t *testing.T) {
	cases := []struct {
		name      string
		primary   Type
		secondary Type
		want      bool
	}{
		{"A", TypeEmpirical, "", true},
		{"A with a formal model", TypeEmpirical, TypeFormal, true},
		{"B with its own empirical study", TypeSynthesis, TypeEmpirical, true},
		{"B alone", TypeSynthesis, "", false},
		{"C", TypeConceptual, "", false},
		{"D", TypeFormal, "", false},
		{"D with a conceptual part", TypeFormal, TypeConceptual, false},
		{"unclassified", TypeUnclassified, "", false},
	}

	for _, c := range cases {
		v := Verdict{PrimaryType: c.primary, SecondaryType: c.secondary}
		if got := v.Empirical(); got != c.want {
			t.Errorf("%s: Empirical() = %v, want %v", c.name, got, c.want)
		}
	}
}

// TestVerifyQuotes_FoldsTypographyButNotWords is the core of the verifier.
//
// Every "should verify" case below is a faithful quote that a byte comparison
// would reject. Every "should not" case is a paraphrase, which is exactly what
// the verifier exists to catch.
func TestVerifyQuotes_FoldsTypographyButNotWords(t *testing.T) {
	cases := []struct {
		name  string
		quote string
		want  bool
	}{
		{
			"exact",
			"We surveyed 189 extended supply chains",
			true,
		},
		{
			"straight apostrophe against the source's curly one",
			"The firm's own reporting was coded by hand",
			true,
		},
		{
			"hyphen against the source's em dash",
			"Data were drawn from Bloomberg and hand-coded - two raters",
			true,
		},
		{
			"a line break in the source read as a space",
			"estimated a regression model of disclosure on structure",
			true,
		},
		{
			"collapsed double space",
			"We surveyed 189   extended    supply chains",
			true,
		},
		{
			"a paraphrase, one word changed",
			"We surveyed 189 extended supply networks",
			false,
		},
		{
			"invented entirely",
			"We conducted eighteen months of participant observation",
			false,
		},
		{
			"right words, wrong case",
			"we surveyed 189 extended supply chains",
			false,
		},
		{
			"empty",
			"",
			false,
		},
	}

	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			v := Verdict{Evidence: []Evidence{{Quote: c.quote}}}
			n := VerifyQuotes(manuscript, &v)

			if got := v.Evidence[0].Verified; got != c.want {
				t.Errorf("Verified = %v, want %v for %q", got, c.want, c.quote)
			}

			wantCount := 0
			if c.want {
				wantCount = 1
			}
			if n != wantCount {
				t.Errorf("VerifyQuotes returned %d, want %d", n, wantCount)
			}
		})
	}
}

func TestVerifyQuotes_CountsAndCoversCounterEvidence(t *testing.T) {
	v := Verdict{
		Evidence: []Evidence{
			{Quote: "We surveyed 189 extended supply chains"},
			{Quote: "a sentence that is not in the paper at all"},
		},
		CounterEvidence: &CounterEvidence{
			Quote:    "disagreements resolved by discussion",
			PointsTo: TypeConceptual,
		},
	}

	if n := VerifyQuotes(manuscript, &v); n != 1 {
		t.Errorf("verified %d evidence quotes, want 1", n)
	}
	if !v.CounterEvidence.Verified {
		t.Error("counter-evidence quote not verified though it is in the paper")
	}
	if v.AllQuotesVerified() {
		t.Error("AllQuotesVerified is true with an invented quote present")
	}
}

// TestAllQuotesVerified_FalseBeforeVerification. The unsafe direction here is a
// verdict that has never been checked reading as though it had been.
func TestAllQuotesVerified_FalseBeforeVerification(t *testing.T) {
	v, err := Parse(response(answerA, "A"))
	if err != nil {
		t.Fatalf("Parse: %v", err)
	}

	if v.AllQuotesVerified() {
		t.Fatal("a freshly parsed verdict reports its quotes verified")
	}

	if n := VerifyQuotes(manuscript, &v); n != 2 {
		t.Fatalf("verified %d of 2 quotes from the real manuscript", n)
	}
	if !v.AllQuotesVerified() {
		t.Error("still false after verifying both quotes")
	}
}

func TestReason(t *testing.T) {
	cases := []Verdict{
		{PrimaryType: TypeEmpirical},
		{PrimaryType: TypeSynthesis, Subtype: SubtypeSystematicReview},
		{PrimaryType: TypeConceptual},
		{PrimaryType: TypeFormal, Subtype: SubtypeProof},
		{PrimaryType: TypeUnclassified, UnclassifiedReason: "an editorial"},
		{PrimaryType: "E"},
	}

	for _, v := range cases {
		if strings.TrimSpace(v.Reason()) == "" {
			t.Errorf("%q produced an empty reason", v.PrimaryType)
		}
	}
}

func TestBuildInput(t *testing.T) {
	got, err := BuildInput(FormFull, nil, "Some manuscript text.")
	if err != nil {
		t.Fatalf("BuildInput: %v", err)
	}
	if !strings.Contains(got, "INPUT FORM: FULL") {
		t.Error("the input does not state its form; the prompt branches on it")
	}
	if !strings.Contains(got, "Some manuscript text.") {
		t.Error("the manuscript is missing from the input")
	}
}

// TestBuildInput_SelectionNeedsItsHeadings. The prompt's central asymmetry is
// that a COMPLETE heading list makes a missing methods section into evidence.
// Sending a selection without one would invite the model to rule out types from
// silence.
func TestBuildInput_SelectionNeedsItsHeadings(t *testing.T) {
	if _, err := BuildInput(FormSelection, nil, "Abstract text."); err == nil {
		t.Fatal("accepted a SELECTION with no heading list")
	}

	got, err := BuildInput(FormSelection, []string{"## Abstract", "## 4 Methodology"}, "Abstract text.")
	if err != nil {
		t.Fatalf("BuildInput: %v", err)
	}
	if !strings.Contains(got, "COMPLETE HEADING LIST") || !strings.Contains(got, "4 Methodology") {
		t.Errorf("the heading list is missing:\n%s", got)
	}
}

func TestBuildInput_EmptyBody(t *testing.T) {
	if _, err := BuildInput(FormFull, nil, "   \n "); err == nil {
		t.Error("accepted an empty manuscript")
	}
}

// TestPromptIsVersionedAndComplete guards the two ways this prompt has already
// been broken once: the rules losing their numbers, and truncation being
// conflated with a deliberate selection.
func TestPromptIsVersionedAndComplete(t *testing.T) {
	p := Prompt()

	if PromptVersion == "" {
		t.Error("PromptVersion is empty; a verdict could not be traced to a prompt")
	}

	for _, want := range []string{
		"\n1. A systematic synthesis protocol",
		"\n2. The paper collects new data",
		"\n3. Theorems, proofs",
		"\n4. Concepts or theory",
		"\n5. Nothing fits",
	} {
		if !strings.Contains(p, want) {
			t.Errorf("the decision procedure is missing %q; all five rules were numbered \"1.\" once already", want)
		}
	}

	if !strings.Contains(p, "A SELECTION IS NOT TRUNCATION") {
		t.Error("the selection-is-not-truncation rule is gone; every sliced paper would come back UNCLASSIFIED")
	}
	if !strings.Contains(p, "<verdict>") {
		t.Error("the prompt no longer asks for the verdict tag that Parse requires")
	}
}
