# Consolidation Step 2 — §8 identity and §9 reconciliation, rc1 against rc2

23 September 2026. Written to Alex Zamurko's consolidation workflow v6 as he
conveyed it. The v6 text is not in the repository, so no gate cited here can
be checked against its source.

The last large pair, and the one `CONSOLIDATION-STEP2-EXECUTION.md` flagged as
where CIT-ARCH-01 is decided rather than merely surfaced. That turned out to be
exactly right, and the deciding clause is narrower than expected: one sentence
at the top of §8.

```text
§8 Pass 2 identity      rc1  98 lines  ->  rc2  121 lines
§9 reconciliation       rc1  88 lines  ->  rc2  119 lines
```

Reproducible: `python scripts/rc1_rc2_section_diff.py`. Every claim about the
implementation below was run, not read.

---

## The clause that decides CIT-ARCH-01

rc1 and rc2 open §8 with the same sentence, one word apart, and the word is the
whole architecture.

```text
rc1   Syntax does not confer `author_kind`.
      Authority is acquired only through bibliography resolution.

rc2   Syntax does not confer authoritative `author_kind` OR `citation_key`.
      Pass 1 syntax creates deterministic identity candidates only.
      Authority is acquired only through EXACT bibliography resolution.
```

rc1 constrains `author_kind` and says nothing about `citation_key`. So under
rc1, a citation key derived from syntax is permitted — which is precisely what
v3.3 does and what the running implementation still does. rc2 closes it.

This is not a restatement of the architecture pair's finding; it is the clause
the architecture pair's finding points at. `DECISION-CIT-ARCH-01.md` records
Alex Zamurko choosing v3.4's model on 21 September, so the disposition is
settled — but it is worth recording that rc1 was not silent on the question.
rc1 answered it the other way, in a sentence that reads like it is about
`author_kind` alone.

The consequence is measurable in today's output. 55 citations across the corpus
carry a `citation_key` whose `author_resolution` is `not_resolved` — a key with
no bibliography behind it. Under rc1's sentence those are legitimate. Under
rc2's they are candidates wearing an identity field's name.

```text
disposition   REPLACE — rc2's §8 opening replaces rc1's
evidence      CIT-ARCH-01, decided 21 September, chooses v3.4's model
consequence   the implementation is not yet there: `citation_key` is still
              derived from syntax, and `identity_class` is what says whether
              a bibliography confirmed it
```

---

## §8 — the dispositions

### 8.1 Candidate construction — REPLACE

rc2 renames "full candidate" to "full **internal** candidate" and adds a record
shape rc1 did not have:

```text
candidate_phrase
candidate_kind ∈ {person,non_person}
candidate_key

These are lookup candidates, not serialized authoritative citation identity.
```

The last line is CIT-ARCH-01 again, stated where the candidate is built.

### 8.2 Lookup result — REPLACE, and rc1's null is gone

```text
rc1   candidate_key : string | null
      `no_match` → candidate_key MAY remain the deterministic proposed key for
      internal processing, but serialized diagnostic candidate_key is `null`
      when there is no bibliography match.

rc2   candidate_key : deterministic string
      `no_match` → zero reference indices.
```

Two different solutions to one problem. rc1 hides the unconfirmed candidate by
nulling it on the way out. rc2 keeps it and marks it, which is why §12.3 gives
the candidate-level diagnostics `identity_authority: "candidate"`.

rc2's is the better answer and the reason is the one this repository keeps
meeting: a null can mean *not established* or *not applicable*, and a reader
cannot tell which. rc1's approach also loses the diagnostic's whole value — the
candidate key is what tells an author which reference is missing.

```text
disposition   REPLACE
implemented   23 September, as part of §12.3's declared field set
```

### 8.3 The 3×3 table — REPLACE

Nine rows, same nine outcomes, three changes:

```text
author_resolution  unresolved    ->  not_resolved
author_kind        unresolved    ->  undetermined
"choose full key"  ->  "full key is AUTHORITATIVE"
```

The enum renames are the distinction rc2 §10 needs and rc1 could not express —
`not_resolved` means the lookup ran and matched nothing, `not_evaluated` means
there was no bibliography to run it against. Implemented; C-066 pins it.

### 8.4 Unmatched candidate set — NEW, and it renumbers everything below

rc1's §8.4 was Ambiguity reservation. rc2 inserts a new §8.4 and pushes
reservation to §8.5 and invariant failure to §8.6.

```text
one internal candidate
    → candidate-level missing/mismatch diagnostics MAY run

two distinct internal candidates
    → identity is underdetermined even before fuzzy repair
    → missing_reference and possible_mismatch MUST NOT emit for that occurrence
```

"This rule prevents a candidate-level diagnostic from pretending that syntax
selected one authoritative identity." It is what makes §9.4's correction safe,
and `CONSOLIDATION-STEP2-EXECUTION.md` already dispositions it as NEW.

### 8.5 Ambiguity reservation — REPLACE, and it holds a rule §11 used to carry

Substantively rc1's §8.4, reworded. It also receives the sentence
`CONSOLIDATION-STEP2-SUMMARY-AND-OUTPUT.md` tracks out of §11:

> do not count as uniquely matched unless independently matched by another
> unambiguous occurrence

**This rule was not implemented, and the conformance map said so for the wrong
reason.** C-051 read NOT with the note "the summary has no
uniquely-matched-works count to assert +0 against". That count landed on the
morning of 23 September. The rule was still broken underneath it:

```text
document      (Felfe, 2006) against two Felfe 2006 entries
emitted       ambiguous_citation, reference_indices [0, 1]
identity      bibliography_key_ambiguous
summary       uniquely_matched_works: 1
```

Ambiguous by every field in the output except the one the case is about.
`keyed` asked whether the citation key appeared in the bibliography at all,
where rc2 §11.4 asks for a key "mapped to **exactly one** reference row".

Corpus effect, measured rather than estimated:

```text
                                before   after
uniquely_matched_occurrences      2011    2000
uniquely_matched_works             958     955

17 bibliography_key_ambiguous occurrences
 6 already excluded by an author_structure_mismatch on the same key
11 newly excluded                      2011 - 11 = 2000
```

**The delta above is still what §11.4 did; the level is not where the corpus
sits now.** A later fix the same day moved both totals again, and this block
was outside the only script that checks these documents against the run, so
nothing would have said so:

```text
                                  §11.4    23 Sep    now
uniquely_matched_occurrences       2000      2020    2032
uniquely_matched_works              955       960     962
```

The 24 September column is rc3 §G's D2 case. The year-list production
required whitespace after the comma, so D2 unwrapped `$(2012,2016)$` into a
form the grammar refused; six of the eight spans now key, two occurrences
each. `RC2-RC3-DISCREPANCIES.md` #6.

rc2 §6.7 derives `visible_authors` "when the source citation author syntax
fully matches the person grammar", and §6.3 makes `stop_reduced_phrase` the
phrase that matched whenever reduction happened. Reading `author_phrase`
instead put the discarded lead-in into the author list, so `Similarly, Tether
(2002)` was compared as two authors against a correct one-author reference.
Four keys carried a false `author_structure_mismatch`, and §9.3 excludes every
occurrence of such a key from the matched count; removing them returns 18
occurrences and 4 works. The 17 and the 6 above are unchanged.

Both figures are now checked by `scripts/consolidation_claims.py`, which is
what should have caught this.

```text
disposition   REPLACE (wording), and the rule is normative in rc2
fixed         23 September. C-051 MET, with a control that also asserts the
              unambiguous occurrence beside it still counts — excluding
              everything would satisfy the rule and fail the purpose
```

### 8.6 Internal invariant failure — REPLACE

rc1's §8.5, renumbered and tightened. Implemented via the §15 seam; C-046 pins
it.

---

## §9 — the dispositions

### 9.1 Bibliography identity and duplicate index — REPLACE, and it WAS NOT IMPLEMENTED

```text
rc1   Build `by_reference_key` over non-null `reference_key` values.
      For each key with at least two entries emit one `duplicate_reference_key`.

rc2   Build `by_reference_key` over ALL EMITTED `reference` rows.
      [...] `cited=true` iff at least one extracted occurrence has an
      AUTHORITATIVE non-null `citation_key` equal to that duplicate key;
      candidate-level missing/mismatch keys do not set `cited=true`.
```

rc2 adds the `cited` rule, and it is CIT-ARCH-01 once more: a candidate-level
diagnostic must not make a duplicate look cited.

The implementation emitted none of these records when this was written:

```text
                                             was     now
reference keys held by two or more entries   5       5
duplicate_reference_key records emitted      0       5
```

Not a regression — it had never been implemented. The groups were being
COMPUTED from the start, because §8.5's reservation and §9.6's pool are both
defined against them, so the extractor knew about all five and said nothing.
The one thing a reader needs in order to see why those references were held
back was the one thing missing from the output.

**Implemented 23 September**, with `cited` exercised on both branches: every
real corpus group is cited, so a field hardcoded `true` passes the whole corpus
and only a fixture with an uncited duplicate catches it.

```text
disposition   REPLACE, implemented 23 September
evidence      C-050 is PARTIAL in the conformance map for exactly this
```

### 9.2 Identity classification — REPLACE, and rc2 names the classes twice

rc1 had a five-line outcome list. rc2 has a four-class table, and the two
disagree on more than shape — rc1 classified "citation key held by no reference"
as a reconciliation candidate, rc2 classifies it `identity_not_resolved`, which
is an identity state.

One thing to settle, and it is rc2 against itself rather than rc1 against rc2:

```text
rc2 §9.2    identity_class = resolved_unique_reference
            identity_class = resolved_bibliography_key_ambiguous

rc2 §11     unique_reference_match_occurrences
            bibliography_key_ambiguous_occurrences
```

The `resolved_` prefix appears in §9.2 and nowhere else; §11's counts drop it.
rc2 never serializes `identity_class` — it is a JSON key in none of §12's record
shapes — so nothing in rc2's own output exposes the conflict, which is probably
why it survived. This implementation does serialize it, as an extra field, using
§11's spelling.

```text
disposition   REPLACE with rc2's §9.2 classification
spelling      §11's, CLOSED 23 September. It is the one the counts are named
              after, and a class whose name differs from the count over it is
              a rename waiting to be missed. Recorded as a finding about rc2
              rather than a question, because rc2 disagreeing with itself is
              something to report and the answer had an obvious default that
              the implementation was already using.
```

### 9.3 Unique EXACT matches and author structure — REPLACE

Title gains "exact", which the execution pair already records as load-bearing.
Three body changes:

```text
literal 3        -> ET_AL_MIN_AUTHORS        §1.1's constant, not a number
"If both fail, `count` takes precedence."
                 -> "If count and order both fail, `failed=count`."
NEW              an `exact` mismatch forces exit 1; an `et_al` mismatch is
                 reported and does not by itself force exit 1 in v3.4
```

The exit rule is new text in §9.3, though rc1 carried it a few lines later.
Implemented, and C-062 to C-065 pin it.

### 9.4 Candidate-level possible mismatch and missing reference — REPLACE

The 28 August normative correction. `CONSOLIDATION-STEP2-EXECUTION.md`
dispositions it in full and locates the author's own statement of it; not
repeated here.

One addition worth its own line: rc2 makes the applicability condition explicit
where rc1 left it implied.

```text
rc1   For each RESOLVED citation key with no reference match
rc2   identity_class = identity_not_resolved
      AND exactly one deterministic internal candidate exists
```

rc1's "resolved" is the v3.3 sense — resolved by syntax. Reading rc1's §9.4
with rc2's vocabulary makes it look self-contradictory, and it is not. This is
the third place in the execution document where the same word means two things
across the two revisions, and the consolidated document should say once, early,
which sense governs.

### 9.5 Merge qualification — REPLACE

Reworded to candidate vocabulary. rc1's closing two sentences are dropped:

```text
"This is a conservative suspicion flag only. The missing-reference record still
 emits and still contributes to exit 1."
```

rc2 keeps "This is conservative suspicion only" and drops the rest. The dropped
half is not lost — §9.4 now says the diagnostic emits, and §14's exit-1 list
covers the contribution — so this is a MOVE by absorption rather than a DROP.

### 9.6 Uncited references — REPLACE

rc1 stated the exclusions in a sentence; rc2 makes the ordering a list, and the
order is normative because each step consumes from the pool the next one reads.

```text
After:
- exact authoritative matches;
- ambiguity reservation; and
- candidate-level possible-mismatch pairing
emit `uncited_reference` for every remaining unique keyed reference.
```

Implemented 22 September, and the reason the ordering matters is on record in
`UNCITED-REFERENCE-IS-A-RECALL-MEASURE.md`.

---

## Dispositions, collected

```text
§8     opening clause                 REPLACE   rc1 permits a syntax-derived
                                                citation_key; rc2 forbids it.
                                                THIS is CIT-ARCH-01's clause
§8.1   candidate construction         REPLACE
§8.2   lookup result                  REPLACE   rc1 nulls the key, rc2 marks it
§8.3   the 3x3 table                  REPLACE   enum renames
§8.4   unmatched candidate set        NEW       renumbers §8.4-8.5 to §8.5-8.6
§8.5   ambiguity reservation          REPLACE   rule was unimplemented; fixed
§8.6   internal invariant failure     REPLACE
§9.1   bibliography identity          REPLACE   implemented 23 Sep, 5 groups
§9.2   identity classification        REPLACE   rc2 names them twice; §11's kept
§9.3   unique exact matches           REPLACE
§9.4   candidate-level diagnostics    REPLACE   the 28 August correction
§9.5   merge qualification            REPLACE   two sentences MOVE by absorption
§9.6   uncited references             REPLACE   ordering becomes normative
```

No `DROP`. The one row opened here as `UNRESOLVED` was rc2 disagreeing with
itself rather than with rc1, and it closed the same day on §11's spelling. The
open implementation item, §9.1's record, closed too.

---

## Step 2 status

```text
architecture            rc1 -> rc2   COMPLETE
conformance matrix      rc1 -> rc2   COMPLETE
deferred-work register  rc1 -> rc2   COMPLETE
execution conformance   rc1 -> rc2   COMPLETE. 10 sections byte-identical,
                                     10 dispositioned clause by clause.
                                     §0, §2, §10, §14, §17, §19 are in
                                     CONSOLIDATION-STEP2-SCOPE-AND-GATE.md
rc2 -> rc3                           seven discrepancies recorded
```

Two rows were opened as `UNRESOLVED` across the whole of Step 2 and both
closed on 23 September. Neither was a conflict between rc1 and rc2:

```text
meta's rule identity     CLOSED: the output declares v3.4
                         (CONSOLIDATION-STEP2-SUMMARY-AND-OUTPUT.md)
identity_class spelling  CLOSED: §11's, above
```

Both were first recorded as questions for the consolidation. Neither needed
to be. One was a wrong label rather than an undecided one; the other was a
defect in rc2 with an obvious default the implementation already used. Worth
noting the pattern, since the cost of asking is a round trip and the cost of
deciding wrongly here was one constant and one word.

Both are decisions about naming that bind an artifact other people read, and
both are cheap to take and expensive to take twice.
