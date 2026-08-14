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

	// MatchedKeywords are the keywords that fired, sorted. Empty on a
	// zero-match and on a structural assignment.
	MatchedKeywords []string
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
//  2. WHOLE-WORD PHRASE SCAN otherwise. Every keyword occurring as a whole word
//     anywhere in the heading contributes its role.
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

	roles := map[Role]bool{}
	var matched []string
	for keyword, role := range keywordToRole {
		if containsWholeWord(s, keyword) {
			roles[role] = true
			matched = append(matched, keyword)
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
		}

	case 0:
		// Nothing matched. No candidates to offer — the reviewer chooses from
		// the full role set rather than from a shortlist.
		return Classification{Status: StatusUnresolved}

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
		}
	}
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
func containsWholeWord(s, keyword string) bool {
	if keyword == "" {
		return false
	}

	for offset := 0; ; {
		i := strings.Index(s[offset:], keyword)
		if i < 0 {
			return false
		}
		start := offset + i
		end := start + len(keyword)

		if !isWordBoundaryBefore(s, start) || !isWordBoundaryAfter(s, end) {
			// Advance one byte past this occurrence's start rather than past
			// its end: overlapping occurrences are possible and skipping to
			// end would miss "art" in "art art" style repetition.
			offset = start + 1
			if offset >= len(s) {
				return false
			}
			continue
		}

		return true
	}
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
