package segment

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// fixtureSHA256 is the SHA-256 of testdata/demo.md, the reference fixture named
// in specification v2.1 §15.
//
// This constant is the reason .gitattributes marks the fixture `-text`. Every
// offset in expected.json is a byte offset into these exact bytes, so any
// transformation of the file — most plausibly core.autocrlf=true rewriting LF
// as CRLF on a Windows checkout — invalidates all 22 spans at once. Under CRLF
// each span would shift by one byte per preceding line, which produces a
// failure that reads as a segmentation bug and sends someone hunting through
// the parser. Asserting the hash first converts that into one unambiguous
// error naming the fixture.
const fixtureSHA256 = "a5f1feb02d617bcc0e2314f8ad6d0df1c7bedd9631f22493c87c57b09917242e"

// fixtureBytes is the fixture's length in bytes, asserted alongside the hash
// purely so a truncation reports its own size rather than an opaque hash
// mismatch.
const fixtureBytes = 81492

// fixtureHasPreamble declares, for the exact bytes pinned above, whether the
// fixture begins with non-whitespace content before its first heading. It is
// a declaration about the pinned fixture, not a runtime decision: repinning
// to a fixture without a preamble is legitimate, but it must flip this
// constant in the same diff that changes fixtureSHA256 and fixtureBytes.
// Flipping it alone, without repinning, silences the preamble assertion
// below against the fixture currently pinned instead of declaring a
// property of a new one.
const fixtureHasPreamble = true

// expectedNode is the subset of expected.json this phase can check. The
// remaining fields — roles, content classes, classification status — are
// produced by phases 2 through 4 and are asserted there.
type expectedNode struct {
	SectionID       string  `json:"section_id"`
	ParentSectionID *string `json:"parent_section_id"`
	NodeKind        string  `json:"node_kind"`
	HeadingRaw      string  `json:"heading_raw"`
	HeadingLevel    int     `json:"heading_level"`
	StartOffset     int     `json:"start_offset"`
	EndOffset       int     `json:"end_offset"`

	// The §6 and §7 pipeline outputs. The three nullable fields are pointers
	// because null and "" are different states here: a null semantic_heading
	// means a bare structural container with nothing to classify, while an
	// empty string would mean a heading that normalized away to nothing.
	HeadingNormalized   string  `json:"heading_normalized"`
	SemanticHeading     *string `json:"semantic_heading"`
	StructuralContainer *string `json:"structural_container"`
	AppendixLabel       *string `json:"appendix_label"`

	// The §6 classification outputs. PrimaryRole and ClassificationMethod are
	// null on every unresolved node, which is the point: §8's overlay model
	// requires the stored determination to record having no answer rather than
	// carrying a placeholder a later reader would mistake for a decision.
	//
	// ContentClass is null on unresolved nodes too, since it is derived from
	// the role — but NOT on the document title, which has a null role and an
	// administrative class. The title is not unclassified; it is classified as
	// something that is not a section role.
	PrimaryRole          *string `json:"primary_role"`
	ContentClass         *string `json:"content_class"`
	ClassificationStatus string  `json:"classification_status"`
	ClassificationMethod *string `json:"classification_method"`
}

// expectedTask mirrors one entry of expected.json's ReviewTasks.
type expectedTask struct {
	ReviewTaskID    string   `json:"review_task_id"`
	SectionID       string   `json:"section_id"`
	ReviewReason    string   `json:"review_reason"`
	CandidateRoles  []string `json:"candidate_roles"`
	MatchedKeywords []string `json:"matched_keywords"`
	Status          string   `json:"status"`
}

type expectedOutput struct {
	SectionNodes []expectedNode `json:"SectionNodes"`
	ReviewTasks  []expectedTask `json:"ReviewTasks"`
}

// loadFixture returns the fixture's bytes, having first proved they are the
// bytes expected.json was computed against. Every test that consumes offsets
// goes through here rather than calling os.ReadFile directly.
func loadFixture(t *testing.T) []byte {
	t.Helper()

	src, err := os.ReadFile(filepath.Join("testdata", "demo.md"))
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}

	if len(src) != fixtureBytes {
		t.Fatalf("fixture is %d bytes, want %d — the file has been altered, most likely by line-ending conversion; check that .gitattributes still marks it -text", len(src), fixtureBytes)
	}

	sum := sha256.Sum256(src)
	if got := hex.EncodeToString(sum[:]); got != fixtureSHA256 {
		t.Fatalf("fixture SHA-256 is %s, want %s — the length is right but the content is not, so every byte offset in expected.json is invalid against it", got, fixtureSHA256)
	}

	return src
}

// loadExpected returns the parsed expected output.
func loadExpected(t *testing.T) expectedOutput {
	t.Helper()

	raw, err := os.ReadFile(filepath.Join("testdata", "expected.json"))
	if err != nil {
		t.Fatalf("read expected.json: %v", err)
	}

	var out expectedOutput
	if err := json.Unmarshal(raw, &out); err != nil {
		t.Fatalf("parse expected.json: %v", err)
	}
	if len(out.SectionNodes) == 0 {
		t.Fatal("expected.json contains no SectionNodes")
	}

	return out
}

// TestFixtureIntegrity is deliberately separate from the detection tests below.
// If the fixture is wrong, every other assertion in this package is meaningless,
// and a single failure naming the file is more useful than twenty failures
// naming offsets.
func TestFixtureIntegrity(t *testing.T) {
	src := loadFixture(t)

	// The fixture is stored with LF. A stray CR would mean the -text pin was
	// removed or the file was regenerated on Windows, and while the hash check
	// above already catches that, this names the cause directly.
	for i, b := range src {
		if b == '\r' {
			t.Fatalf("fixture contains a carriage return at byte %d; it must be stored with LF line endings only", i)
		}
	}

	// The preamble property AC-14 depends on is asserted here, once, against
	// the hash-pinned bytes, rather than re-derived (and skipped) inside the
	// acceptance test. It is decidable here because loadFixture already
	// proved these are the exact pinned bytes: a louder failure — the hash or
	// length mismatch above — fires first if that ever stops being true. It
	// is deliberately NOT asserted in acceptance_test.go, where the same
	// question has to be answered per run and a fixture that legitimately
	// lacks a preamble would have to decline rather than fail; asserting it
	// there would turn AC-14's two content-conditional declines into a gate
	// failure class, which is exactly what GATE-04 forbids. A failure here
	// means the fixture was replaced or regenerated, not that this assertion
	// drifted — the pinning constants at the top of this file are where to
	// look. fixtureHasPreamble is how a genuinely preamble-free fixture is
	// admitted: declared beside the hash and length so it cannot be repinned
	// quietly, and it is a declared value rather than a skip, so the
	// permissive case is visible in the diff instead of absent from the run.
	if msg := preambleInvariant(src, detectHeadings(src), fixtureHasPreamble); msg != "" {
		t.Fatal(msg)
	}
}

// preambleInvariant decides whether the fixture's preamble property holds,
// gated on declaredHasPreamble, and returns the empty string when it does or
// a one-line failure message naming the fixture otherwise. It is a pure
// function, driven from parameters rather than reading fixtureHasPreamble
// directly, precisely so the negative proof in TestPreambleInvariant_Control
// can drive it against synthetic inputs without mutating any tracked file.
//
// Order matters: the no-headings case is checked first and unconditionally,
// because a fixture with no headings is not a preamble-free fixture — it is
// one where AC-14 indexes headings[0] and panics, and a panic is neither
// green nor silent. The declaration gate only waives the two preamble checks
// that follow it.
func preambleInvariant(src []byte, headings []Heading, declaredHasPreamble bool) string {
	if len(headings) == 0 {
		return "testdata/demo.md: no headings detected"
	}

	if !declaredHasPreamble {
		return ""
	}

	firstHeading := headings[0].ByteStart
	if firstHeading == 0 {
		return "testdata/demo.md: first heading starts at byte 0; AC-14 requires a non-whitespace preamble"
	}

	if len(strings.TrimSpace(string(src[:firstHeading]))) == 0 {
		return "testdata/demo.md: bytes [0,N) are whitespace only"
	}

	return ""
}

// TestPreambleInvariant_Control is the permanent, mutation-free negative
// proof that preambleInvariant can both fail and pass, and that its
// declaredHasPreamble gate is real rather than decorative. It drives the
// function directly with synthetic inputs instead of temporarily rewriting
// testdata/demo.md and restoring it afterward.
func TestPreambleInvariant_Control(t *testing.T) {
	validPreamble := []byte("Some real preamble text.\n# Heading\nBody.")
	zeroOffsetSrc := []byte("# Heading\nBody.")
	whitespacePreamble := []byte(" \t\n\n# Heading\nBody.")

	t.Run("no headings at all", func(t *testing.T) {
		msg := preambleInvariant(validPreamble, nil, true)
		if msg == "" {
			t.Fatal("expected a non-empty message for a heading-less input, got empty string")
		}
		if !strings.Contains(msg, "testdata/demo.md") {
			t.Fatalf("message %q does not name the fixture file", msg)
		}
	})

	t.Run("first heading at byte 0", func(t *testing.T) {
		headings := []Heading{{ByteStart: 0}}
		msg := preambleInvariant(zeroOffsetSrc, headings, true)
		if msg == "" {
			t.Fatal("expected a non-empty message for a zero-offset first heading, got empty string")
		}
		if !strings.Contains(msg, "testdata/demo.md") {
			t.Fatalf("message %q does not name the fixture file", msg)
		}
	})

	t.Run("whitespace-only preamble", func(t *testing.T) {
		headings := []Heading{{ByteStart: 4}}
		msg := preambleInvariant(whitespacePreamble, headings, true)
		if msg == "" {
			t.Fatal("expected a non-empty message for a whitespace-only preamble, got empty string")
		}
		if !strings.Contains(msg, "testdata/demo.md") {
			t.Fatalf("message %q does not name the fixture file", msg)
		}
	})

	t.Run("valid preamble", func(t *testing.T) {
		headings := []Heading{{ByteStart: 26}}
		msg := preambleInvariant(validPreamble, headings, true)
		if msg != "" {
			t.Fatalf("expected the empty string for a valid preamble, got %q", msg)
		}
	})

	t.Run("declared preamble-free", func(t *testing.T) {
		headings := []Heading{{ByteStart: 0}}
		msg := preambleInvariant(zeroOffsetSrc, headings, false)
		if msg != "" {
			t.Fatalf("expected the empty string when declaredHasPreamble is false, got %q", msg)
		}
	})

	t.Run("declared preamble-free, but no headings", func(t *testing.T) {
		msg := preambleInvariant(zeroOffsetSrc, nil, false)
		if msg == "" {
			t.Fatal("expected a non-empty message when there are no headings, even when declaredHasPreamble is false, got empty string")
		}
		if !strings.Contains(msg, "testdata/demo.md") {
			t.Fatalf("message %q does not name the fixture file", msg)
		}
	})
}

// TestDetectHeadings_Fixture is the phase 1 done-condition from §15: the
// detector must find exactly the 22 headings the specification names, at the
// levels it names, in document order.
//
// The level distribution is asserted as a whole rather than as a total, because
// a total alone passes if an H3 is misread as an H2. The distribution is what
// §15 actually claims: 1 H1, 8 H2, 12 H3, 1 H4, and no H5 or H6 anywhere.
func TestDetectHeadings_Fixture(t *testing.T) {
	src := loadFixture(t)
	exp := loadExpected(t)

	got := detectHeadings(src)

	if len(got) != len(exp.SectionNodes) {
		t.Fatalf("detected %d headings, want %d", len(got), len(exp.SectionNodes))
	}

	wantCounts := map[int]int{1: 1, 2: 8, 3: 12, 4: 1, 5: 0, 6: 0}
	gotCounts := map[int]int{}
	for _, h := range got {
		gotCounts[h.Level]++
	}
	for level := 1; level <= 6; level++ {
		if gotCounts[level] != wantCounts[level] {
			t.Errorf("H%d count is %d, want %d", level, gotCounts[level], wantCounts[level])
		}
	}
}

// TestDetectHeadings_MatchesExpectedText checks each detected heading against
// the heading_raw expected.json records for the node at the same position.
//
// This is the assertion that makes the phase meaningful. Counting headings
// proves the parser found the right NUMBER of things; comparing the text proves
// it found the right things, and that TextStart/TextStop delimit the heading
// text with markers and any closing '###' already removed.
func TestDetectHeadings_MatchesExpectedText(t *testing.T) {
	src := loadFixture(t)
	exp := loadExpected(t)

	got := detectHeadings(src)
	if len(got) != len(exp.SectionNodes) {
		t.Fatalf("detected %d headings, want %d; run TestDetectHeadings_Fixture first", len(got), len(exp.SectionNodes))
	}

	for i, want := range exp.SectionNodes {
		h := got[i]

		if h.Level != want.HeadingLevel {
			t.Errorf("heading %d (%s): level %d, want %d", i, want.SectionID, h.Level, want.HeadingLevel)
		}

		if text := string(src[h.TextStart:h.TextStop]); text != want.HeadingRaw {
			t.Errorf("heading %d (%s): text %q, want %q", i, want.SectionID, text, want.HeadingRaw)
		}
	}
}

// TestDetectHeadings_OffsetsAreWellFormed asserts the two structural properties
// every downstream phase relies on, independently of what any heading says.
//
// ByteStart must address a '#'. goldmark documents Pos() as the first non-space
// byte of the block's opening line, and for an ATX heading that byte is the '#'
// — but it is documented behaviour of a dependency, not a guarantee of this
// package, so it is verified against the source bytes rather than assumed. If
// goldmark ever regresses Pos(), this fails here rather than producing spans
// that are silently off by the indent.
//
// Headings must also be strictly increasing. detectHeadings performs no sort
// and relies on ast.Walk visiting in document order; this is what makes that
// reliance safe to state.
func TestDetectHeadings_OffsetsAreWellFormed(t *testing.T) {
	src := loadFixture(t)
	got := detectHeadings(src)

	prev := -1
	for i, h := range got {
		if h.ByteStart < 0 || h.ByteStart >= len(src) {
			t.Fatalf("heading %d: ByteStart %d is outside the document [0,%d)", i, h.ByteStart, len(src))
		}
		if src[h.ByteStart] != '#' {
			t.Errorf("heading %d: ByteStart %d addresses %q, want '#'", i, h.ByteStart, src[h.ByteStart])
		}
		if h.ByteStart <= prev {
			t.Errorf("heading %d: ByteStart %d does not follow the previous heading at %d", i, h.ByteStart, prev)
		}
		prev = h.ByteStart

		if h.TextStart > h.TextStop {
			t.Errorf("heading %d: inverted text range [%d,%d)", i, h.TextStart, h.TextStop)
		}
		if h.TextStart < h.ByteStart {
			t.Errorf("heading %d: TextStart %d precedes ByteStart %d", i, h.TextStart, h.ByteStart)
		}
		if h.TextStop > len(src) {
			t.Errorf("heading %d: TextStop %d exceeds the document length %d", i, h.TextStop, len(src))
		}
	}
}
