package segment

import (
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"
)

// keywordToRole inverts roleKeywords once at package load.
//
// Inverting is safe only because no keyword belongs to two roles; if one ever
// did, this map would silently keep whichever role happened to be built last
// and the loss would be invisible. TestRoleTableMatchesTable asserts the
// property rather than leaving it implied by the table's current contents.
var keywordToRole = func() map[string]Role {
	m := make(map[string]Role, 160)
	for role, keywords := range roleKeywords {
		for _, k := range keywords {
			m[strings.ToLower(strings.TrimSpace(k))] = role
		}
	}
	return m
}()

// Classification is the outcome of §6 steps 4-5 for one heading.
//
// The zero value is not a valid classification. Read Status first: on
// StatusUnresolved, Role is empty and MUST stay empty — see §8's overlay model,
// which lets a human decision take effect at read time without overwriting what
// the machine determined. That only works if the stored determination honestly
// records having no answer.
type Classification struct {
	// Role is the determined role, or empty when unresolved.
	Role Role

	// ContentClass is derived from Role, empty when Role is.
	ContentClass ContentClass

	Status ClassificationStatus

	// Method is set only when Status is StatusResolved.
	Method ClassificationMethod

	// CandidateRoles is populated only on a multi-role match: the roles that
	// tied, sorted, for a human to choose between. Empty on a zero-match, where
	// there is nothing to offer.
	CandidateRoles []Role

	// MatchedKeywords are the keywords that COUNTED, deduplicated and sorted.
	// Empty on a zero-match and on a structural assignment. A keyword suppressed
	// under §6 step 5a is absent here and present in Matches.
	MatchedKeywords []string

	// Matches is every occurrence the phrase scan found, in position order,
	// including the ones that were suppressed. Empty on an exact match and on a
	// structural assignment.
	//
	// The suppressed ones are kept rather than discarded so that "why did this
	// resolve to theory when `background` is an introduction keyword?" has an
	// answer in the data instead of requiring someone to re-derive it. Same
	// principle as never overwriting the machine's determination with a human's:
	// keep the reasoning, and let a reader judge it.
	Matches []KeywordMatch
}

// KeywordMatch is ONE OCCURRENCE of one keyword at one position in a heading.
//
// The distinction between an occurrence and a keyword is the whole point of this
// type. "Background and theoretical background" contains the keyword `background`
// twice: once standing alone, and once inside `theoretical background`. Those are
// the same string and two different pieces of evidence, and a rule that reasons
// about keywords rather than positions cannot tell them apart.
type KeywordMatch struct {
	Keyword string
	Role    Role

	// Start and End are byte offsets into the semantic heading, half-open.
	Start int
	End   int

	// SuppressedBy names the longer overlapping keyword that swallowed this
	// occurrence, or is empty when the occurrence counted toward the role tally.
	SuppressedBy string
}

// Classify determines a role for one semantic heading: §6 steps 4-5.
//
// An EMPTY semantic heading means §7 recognised a bare structural container —
// "Appendix B", "Supporting information" — and there is nothing to classify.
// That resolves to RoleUnknown by structural assignment and raises no review
// task, because the heading carries no epistemic claim for a human to
// adjudicate. It is a complete answer, not a failure to find one.
//
// Otherwise:
//
//  1. EXACT MATCH runs first and wins outright. A heading that IS a keyword
//     resolves to that keyword's role immediately, and the phrase scan never
//     runs. This ordering is what stops "background" — an introduction keyword
//     that also appears inside several theory keywords — from producing a tie
//     when it stands alone as the whole heading.
//
//  2. WHOLE-WORD PHRASE SCAN otherwise. Every OCCURRENCE of every keyword,
//     with its position, is collected. Positions matter — see step 2a.
//
//     2a. NESTED-OCCURRENCE SUPPRESSION (2.7). An occurrence whose span lies
//     strictly inside another occurrence's span is suppressed and does not
//     count toward the role tally.
//
//     Five keywords in the table sit inside a longer keyword of a different
//     role: `background` inside `theoretical background` and inside
//     `background literature`, `results` inside `discussion of results`, and
//     `summary` inside both `summary and conclusion(s)`. Whenever the longer
//     one fires the shorter one fires too, and the pair looks like two roles
//     disagreeing when it is one span read twice.
//
//     This is NOT tie-breaking, which §6 forbids and should keep forbidding.
//     Tie-breaking picks a winner between two genuine matches. This removes a
//     match that was never independent: `background` observed nothing about
//     "Argumentation: Theoretical Background" that `theoretical background`
//     had not already observed.
//
//     The rule is stated over SPANS, not keywords, and the difference is
//     load-bearing. "Background and theoretical background" contains
//     `background` twice — once alone, once nested. Suppressing the keyword
//     would discard both and resolve the heading to theory, silently losing a
//     real ambiguity. Suppressing the occurrence keeps the standalone one, and
//     the heading correctly stays a question.
//
//  3. COUNT DISTINCT ROLES, not keyword hits. Three methodology keywords in one
//     heading are one role and resolve cleanly; one methodology keyword and one
//     results keyword are two roles and do not. Counting hits instead would
//     make a verbose methodology heading look like a tie, and this is the
//     single most consequential line in §6.
//
// Exactly one role resolves. Zero or more than one leaves Role empty with
// StatusUnresolved, which §8 turns into a ReviewTask. The two unresolved cases
// are distinguished by CandidateRoles: populated on a tie, empty on a miss.
func Classify(semanticHeading string) Classification {
	s := strings.TrimSpace(semanticHeading)

	if s == "" {
		return Classification{
			Role:         RoleUnknown,
			ContentClass: ContentClassFor(RoleUnknown),
			Status:       StatusResolved,
			Method:       MethodStructural,
		}
	}

	if role, ok := keywordToRole[s]; ok {
		return Classification{
			Role:            role,
			ContentClass:    ContentClassFor(role),
			Status:          StatusResolved,
			Method:          MethodRule,
			MatchedKeywords: []string{s},
		}
	}

	matches := scanKeywords(s)
	suppressNested(matches)

	roles := map[Role]bool{}
	seen := map[string]bool{}
	var matched []string
	for _, m := range matches {
		if m.SuppressedBy != "" {
			continue
		}
		roles[m.Role] = true
		if !seen[m.Keyword] {
			seen[m.Keyword] = true
			matched = append(matched, m.Keyword)
		}
	}
	sort.Strings(matched)

	switch len(roles) {
	case 1:
		var only Role
		for role := range roles {
			only = role
		}
		return Classification{
			Role:            only,
			ContentClass:    ContentClassFor(only),
			Status:          StatusResolved,
			Method:          MethodRule,
			MatchedKeywords: matched,
			Matches:         matches,
		}

	case 0:
		// Nothing matched. No candidates to offer — the reviewer chooses from
		// the full role set rather than from a shortlist.
		//
		// Matches is carried even here: a heading where every occurrence was
		// suppressed is a different situation from one where nothing fired at
		// all, and the two must stay distinguishable.
		return Classification{Status: StatusUnresolved, Matches: matches}

	default:
		candidates := make([]Role, 0, len(roles))
		for role := range roles {
			candidates = append(candidates, role)
		}
		sort.Slice(candidates, func(i, j int) bool { return candidates[i] < candidates[j] })

		return Classification{
			Status:          StatusUnresolved,
			CandidateRoles:  candidates,
			MatchedKeywords: matched,
			Matches:         matches,
		}
	}
}

// scanKeywords returns every whole-word occurrence of every keyword in s,
// ordered by position, then longest first, then alphabetically.
//
// The ordering is not cosmetic. keywordToRole is a map and Go randomises map
// iteration, so without a total order the suppression pass below would name a
// different suppressor on different runs and two runs over the same paper would
// store different provenance. Deterministic output is the whole product here.
func scanKeywords(s string) []KeywordMatch {
	var out []KeywordMatch
	for keyword, role := range keywordToRole {
		for _, span := range wholeWordSpans(s, keyword) {
			out = append(out, KeywordMatch{
				Keyword: keyword,
				Role:    role,
				Start:   span[0],
				End:     span[1],
			})
		}
	}

	sort.Slice(out, func(i, j int) bool {
		if out[i].Start != out[j].Start {
			return out[i].Start < out[j].Start
		}
		if out[i].End != out[j].End {
			return out[i].End > out[j].End
		}
		return out[i].Keyword < out[j].Keyword
	})
	return out
}

// suppressNested marks every occurrence strictly contained by a longer one.
//
// STRICTLY: an occurrence never suppresses itself, and two occurrences with
// identical spans cannot exist, because an identical span is an identical
// substring and therefore the same keyword.
//
// Containment is transitive, so a three-deep nest resolves to the outermost
// survivor without iterating: if x is inside y and y is inside z, then x is
// inside z, and the loop finds a suppressor for both x and y.
func suppressNested(matches []KeywordMatch) {
	for i := range matches {
		a := matches[i]
		for j := range matches {
			if i == j {
				continue
			}
			b := matches[j]
			if b.Start <= a.Start && a.End <= b.End && (b.End-b.Start) > (a.End-a.Start) {
				matches[i].SuppressedBy = b.Keyword
				break
			}
		}
	}
}

// wholeWordSpans returns the half-open byte span of every occurrence of keyword
// in s that is bounded by non-word characters.
//
// Occurrences are found by advancing ONE BYTE past each candidate start rather
// than past its end. Overlapping occurrences are possible, and skipping to the
// end would miss the second "art" in "art art".
func wholeWordSpans(s, keyword string) [][2]int {
	if keyword == "" {
		return nil
	}

	var out [][2]int
	for offset := 0; offset <= len(s)-len(keyword); {
		i := strings.Index(s[offset:], keyword)
		if i < 0 {
			break
		}
		start := offset + i
		end := start + len(keyword)

		if isWordBoundaryBefore(s, start) && isWordBoundaryAfter(s, end) {
			out = append(out, [2]int{start, end})
		}
		offset = start + 1
	}
	return out
}

// containsWholeWord reports whether keyword occurs in s bounded by non-word
// characters on both sides.
//
// Written by hand rather than as a regexp for two reasons. RE2 has no
// lookbehind, so the reference implementation's `(?<!\w)…(?!\w)` cannot be
// transcribed directly; and this runs 156 times per heading, so avoiding 156
// compiled patterns and their match machinery is worth the twenty lines.
//
// The boundary test is what makes the match safe. "results" must not fire on
// "resultsets", and — the case that actually bites — "art" must not fire on
// "particular". A plain strings.Contains would classify half the corpus as
// literature_review on the strength of "state of the art".
// It delegates to wholeWordSpans so there is exactly one implementation of the
// boundary test. Two would drift, and a drift here is a wrong role rather than
// a visible failure.
func containsWholeWord(s, keyword string) bool {
	return len(wholeWordSpans(s, keyword)) > 0
}

// isWordBoundaryBefore reports whether the rune ending at byte index i is a
// non-word rune, or whether i is the start of the string.
func isWordBoundaryBefore(s string, i int) bool {
	if i == 0 {
		return true
	}
	r, _ := utf8.DecodeLastRuneInString(s[:i])
	return !isWordRune(r)
}

// isWordBoundaryAfter reports whether the rune beginning at byte index i is a
// non-word rune, or whether i is the end of the string.
func isWordBoundaryAfter(s string, i int) bool {
	if i >= len(s) {
		return true
	}
	r, _ := utf8.DecodeRuneInString(s[i:])
	return !isWordRune(r)
}

// isWordRune matches the reference implementation's \w: letters, digits and
// underscore, Unicode-aware.
//
// Unicode-aware is not decoration. Headings reach this function normalized but
// not transliterated, so "análisis de datos" is a real input, and treating the
// á as a non-word character would let a keyword match across it.
func isWordRune(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsDigit(r)
}
