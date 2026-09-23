# Consolidation Step 2 — §11 summary invariants and §12 canonical output, rc1 against rc2

Against Alex Zamurko's consolidation workflow v6. 23 September 2026.

Two of the ten CHANGED sections `CONSOLIDATION-STEP2-EXECUTION.md` identified
and left undispositioned, taken together because §12's record shapes are what
§11's invariants are computed over.

```text
§11 summary invariants   rc1  52 lines  ->  rc2  106 lines
§12 canonical JSONL      rc1 173 lines  ->  rc2  183 lines
```

Every disposition below was checked against the running extractor, and four of
them turned out to be unimplemented rather than merely unrecorded. Those are
marked and were fixed the same day.

Reproducible: the section diff is `python scripts/rc1_rc2_section_diff.py`;
the implementation claims are the controls named in each row.

---

## §11 — the four dispositions

### 11.1 Extraction invariant — KEEP

```text
total_citation_occurrences = extracted + unresolved_extraction
```

Byte-identical in intent; rc2 only rewraps the `+`. No decision needed.

Worth one line on why it survived untouched: this is the only summary invariant
that does not mention identity, so it is the only one the bibliography-absent
mode of rc2 §10 leaves standing. Extraction never needed a reference list.

### 11.2 The partition — REPLACE, and rc1's version was arithmetically unsatisfiable

This is the substantive change in the pair, and it is three changes wearing one
section number.

```text
rc1   total_citation_occurrences
      = unique_reference_match + bibliography_key_ambiguous
      + reference_missing + possible_mismatch
      + author_resolution_ambiguous + unresolved_identity

rc2   extracted_citation_occurrences
      = resolved_citation_occurrences
      + author_resolution_ambiguous_occurrences
      + identity_not_resolved_occurrences

      where resolved = unique_reference_match + bibliography_key_ambiguous
```

**1. The left-hand side moves from `total` to `extracted`.** rc1's partition
cannot balance. By rc1's own §11.1, `total` includes
`unresolved_extraction_occurrences` — candidates that failed the grammar and
were emitted as `unresolved_citation`. By rc1 §9.2, outcome classification
happens "after §8 identity resolution", which those rows never reach, so they
have no outcome to be counted under. rc1 partitions a total it cannot classify.

Measured on this corpus, the gap is exact and it is not small:

```text
paper           total  extracted  unres_extr   rc1 gap
17bef7c6          118        101          17        17
2af68a7f          152        134          18        18
43338825          126        117           9         9
4918fd7d          283        264          19        19
50408397          241        236           5         5
849f8fc6           69         68           1         1
ad1e3ff9          190        185           5         5
bf2fdc4a          169        160           9         9
c1d56945          243        219          24        24
e1b418a4          213        200          13        13
ea07e5f5          110        107           3         3
ed6a890a          196        186          10        10
CORPUS           2235       2102         133       133
```

rc1's §11.2 would be off by 133 on thirteen papers. rc2's holds exactly on all
thirteen. So this is not a preference between two formulations; rc2 corrects a
defect, and the correction is undocumented anywhere outside the section text.

**2. The two candidate-level diagnostics leave the partition.** rc1 counted
`reference_missing` and `possible_mismatch` as identity states. rc2 makes them
"diagnostics over a subset of `identity_not_resolved_occurrences` ... **not**
additional identity-partition states." This is the 28 August normative
correction, which `CONSOLIDATION-STEP2-EXECUTION.md` located in §9.4 — it lands
in §11.2 as well, and the two together are one change.

**3. `unresolved_identity_occurrences` → `identity_not_resolved_occurrences`.**
A rename. rc1's name appears twice in rc1 and zero times in rc2, so nothing
carries the old spelling forward.

```text
disposition   REPLACE — rc2's §11.2 replaces rc1's
evidence      rc1's arithmetic fails by exactly unresolved_extraction_
              occurrences, measured at 133 over the corpus. rc2's holds on all
              thirteen papers.
control       §11.2/C-052, and §11.2's second equation, each computed from a
              different field so neither side is derived from the other
```

### 11.3 Bibliography absence — NEW, and it is a field list rather than prose

Already dispositioned as NEW in `CONSOLIDATION-STEP2-EXECUTION.md`; recorded
here for the count, which that document gets wrong, and which the first draft of
this document also got wrong in the other direction.

```text
rc2 §11.3 has TEN entries: nine null and one zero.

null   author_resolution_ambiguous_occurrences
       identity_not_resolved_occurrences
       unique_reference_match_occurrences
       bibliography_key_ambiguous_occurrences
       reference_missing_occurrences
       possible_mismatch_occurrences
       uniquely_matched_occurrences
       uniquely_matched_works
       distinct_works_cited

zero   resolved_citation_occurrences
```

`CONSOLIDATION-STEP2-EXECUTION.md` says eight. This document said ten-null
before the block above was generated from rc2's bytes rather than counted by
eye. Both readings were produced the same way and both were wrong, which is the
argument for generating the list.

The one zero is not an oversight in rc2 and is the most useful line in the
section: zero citations were resolved, and that IS a measurement. Everything
else was not measured at all, and `0` would claim it had been.

```text
disposition   KEEP rc2's list; correct the earlier document's "eight" to
              "nine null and one zero"
control       C-067, which reads the nine off §11.3 rather than from memory
```

### 11.4 Summary field semantics — REPLACE, and rc1 wrote equations over undefined terms

rc1's field-semantics block defines five fields. rc1's invariants use eleven.

```text
used by rc1's invariants, defined nowhere in rc1
    bibliography_reconciliation_performed
    total_citation_occurrences
    extracted_citation_occurrences
    unresolved_extraction_occurrences
    reference_missing_occurrences
    possible_mismatch_occurrences
```

rc2 §11.4 defines all six, plus `identity_resolution_performed`, which does not
appear in rc1 at all — rc1 had only the reconciliation flag, and rc2 makes
identity resolution the primary condition with reconciliation equal to it "in
v3.4".

Two definitions change materially rather than being tightened:

```text
resolved_citation_occurrences
  rc1  "occurrences with non-null authoritative citation_key; INCLUDES unique
        match, bibliography-key ambiguous, reference missing, and possible
        mismatch outcomes"
  rc2  "extracted occurrences with a non-null authoritative citation_key"
       and, per §11.2, exactly unique_reference_match + key_ambiguous
```

This looks at first like rc1 contradicting itself — how can a
`reference_missing` outcome have an authoritative key? It does not contradict
itself. rc1 §9.4 opens "For each **resolved** citation key with no reference
match", so in rc1 a key is resolved by syntax and reconciliation happens
afterwards. rc1 is internally consistent; the word `authoritative` simply means
something weaker there than it does in rc2. **This is CIT-ARCH-01 surfacing in
§11**, and it is the same disagreement the architecture pair records in §8, so
it needs no separate decision — but it does need noting that §11 is a second
place the decision binds.

```text
uniquely_matched_works
  rc1  "distinct REFERENCE INDICES with at least one unambiguous matched
        occurrence"
  rc2  "distinct authoritative CITATION KEYS mapped to exactly one reference
        row"
```

The counting basis moves from the reference side to the citation side. Under
exact-key identity these coincide, and that was verified rather than assumed —
both bases give the same number on all thirteen papers. Recorded as a
restatement with evidence, not as a change in meaning.

```text
disposition   REPLACE — rc2's §11.4 replaces rc1's §11.3
evidence      rc2 defines six terms rc1 used and never defined, and one
              (identity_resolution_performed) rc1 does not have
consequence   the definitional shift in `resolved_citation_occurrences` is
              CIT-ARCH-01, already decided for v3.4's model
```

### Two rc1 sentences that are not in rc2 §11

Both look like `DROP` and neither is.

```text
"Counts are per citation occurrence, not per diagnostic record."
    MOVED, and NARROWED. Zero occurrences in rc2 as a general statement. rc2
    instead says it per-field, on the two diagnostics only: "occurrences
    represented by candidate-level missing_reference diagnostics". The general
    claim becomes two specific ones. Nothing is lost for the fields rc2 covers;
    the general rule no longer exists for any field rc2 adds later.

"Ambiguity-reserved entries do not count as uniquely matched unless
 independently matched elsewhere."
    MOVED OUT OF THE NORMATIVE TEXT. rc2 keeps reservation itself (§8.5, and
    §9.4's pool construction excludes reserved indices), but this specific
    claim about `uniquely_matched` survives only as conformance case C-051,
    "reserved is not uniquely matched | summary assertion | counts +0 absent
    independent match".

    A normative rule became a test case. That is a real weakening: a case in
    the matrix is something to verify, a sentence in §11 is something to
    implement. C-051 is currently NOT MET here for exactly the reason the
    demotion predicts — the summary has no uniquely-matched-works count to
    assert `+0` against.
```

```text
disposition   both MOVE, neither DROP
open          C-051 should be restored to §11's normative text in the
              consolidated document, not left as a matrix row
```

---

## §12 — the dispositions, and four things that were not implemented

§12's changes are smaller in line count and larger in consequence, because the
implementation is checked against these shapes byte for byte.

### 12.2 Block order — REPLACE

`bibliography_absent` moves from block 13 to block 4, gaining the qualifier
"singleton only when `references_source=not_available`". Everything below it
shifts by one. Already implemented; §12.2's order is stated as one tuple.

### 12.2 `mode` — REPLACE

```text
rc1  mode ∈ {standalone, orchestrated}
rc2  mode ∈ {standalone_nomap, standalone_map, orchestrated}
```

Follows rc2 §2.2 being new. Scope, not behaviour — except that `mode` is a
`meta` field, and `meta` is the one record this implementation still does not
emit in rc2's shape. See the open question at the end.

### 12.3 Two enum sets — REPLACE

```text
author_resolution
  rc1  {full_phrase, stop_reduced, unresolved, ambiguous}
  rc2  {full_phrase, stop_reduced, not_resolved, ambiguous, not_evaluated}

author_kind
  rc1  {person, non_person, unresolved}
  rc2  {person, non_person, undetermined}
```

Both renames are the distinction rc2 §10 needs and rc1 could not express:
`not_resolved` means the lookup ran and matched nothing, `not_evaluated` means
there was no bibliography to run it against. `undetermined` does the same work
on the kind. Already implemented, and C-066 pins it.

### 12.3 The two candidate-level diagnostics — REPLACE, AND WAS NOT IMPLEMENTED

```text
rc1  {"type":"missing_reference","citation_key":…,"example":…,
      "occurrences":…,"merge_suspected":…}
rc2  {"type":"missing_reference","candidate_key":…,
      "identity_authority":"candidate","example":…,
      "occurrences":…,"merge_suspected":…}

rc1  {"type":"possible_mismatch","citation_key":…,"reference_index":…,
      "reference_key":…,"evidence":…}
rc2  {"type":"possible_mismatch","candidate_key":…,
      "identity_authority":"candidate","reference_index":…,
      "reference_key":…,"evidence":…}
```

`citation_key` → `candidate_key` was implemented. `identity_authority` and
`example` were not, and `evidence` was still emitted under rc1's name `rule`.

`identity_authority` is worth more than a rename. The implementation carried
`citation_key: null, author_kind: null` on both records to say "this
establishes nothing" — which is the right claim expressed badly, because a null
can mean *not established* or *not applicable* and a reader cannot tell which.
rc2's literal `"candidate"` says positively what authority the record has.

```text
disposition   REPLACE
implemented   23 September. The two nulls are gone, replaced by the literal.
control       C-053 and C-054 now require the fields to be ABSENT rather than
              null, and require the literal
```

### 12.3 `ambiguous_citation` and `author_structure_mismatch` — WAS NOT IMPLEMENTED

```text
ambiguous_citation          rc2 declares `citation_key` and `example`;
                            this file emitted `candidate_key` and no example
author_structure_mismatch   rc2 declares `reference_index` and `example`;
                            this file emitted neither
```

`reference_index` is not cosmetic. §12.4 orders the block by
`(citation index of first corresponding occurrence, reference_index, failed)`,
so without the field two mismatches on one citation can remain tied on every
key the block is ordered by — which §12.4 forbids in as many words.

### How twelve declared fields stayed absent behind a green control

Worth recording, because the shape recurs.

§12.3's control read rc2's declared key order out of rc2's own bytes — the
right source — and then compared it like this:

```python
want = [k for k in declared if k in r]        # filter to present keys
if list(r)[:len(want)] != want: ...           # check their order
```

The filter is the defect. A declared field the implementation never emitted was
removed from `want`, never compared, and never reported. The control was green,
named §12.3, and tested ordering only. Twelve fields were absent that way
across five record types.

The control now reports declared-but-absent separately from out-of-order. Eight
of the twelve were fixed the same day; the remaining four are `meta`'s and are
the open question below.

### 12.4 Two sort keys — REPLACE

```text
missing_reference    rc1  "first occurrence position of citation_key,
                          then citation_key UTF-8 bytes"
                     rc2  candidate_key in both places
possible_mismatch    rc1  "pairing order established in §9.4"
                     rc2  "CANDIDATE pairing order established in §9.4"
```

Both follow the candidate-level correction. Consistent renames, no behaviour
change.

### 12.3 `unresolved_reference` reasons — NEW, closed set stated

rc2 adds the closed list in §12 itself:
`entry_start_grammar | orphan_line | no_year`. rc1 left it to §7. This is
C-031, and all three are implemented.

---

## Dispositions, collected

```text
§11.1  extraction invariant             KEEP
§11.2  the partition                    REPLACE   rc1's is unsatisfiable by 133
§11.3  bibliography absence             KEEP      earlier count of 8 is wrong;
                                                  nine null and one zero
§11.4  field semantics                  REPLACE   rc1 undefined six of its terms
§11    "per occurrence not per record"  MOVE      narrowed to two fields
§11    ambiguity-reserved sentence      MOVE      demoted to C-051; restore it
§12.2  block order                      REPLACE
§12.2  mode enum                        REPLACE
§12.3  author_resolution / author_kind  REPLACE
§12.3  the two diagnostics' shape       REPLACE   identity_authority was absent
§12.3  ambiguous_citation               REPLACE   citation_key, example absent
§12.3  author_structure_mismatch        REPLACE   reference_index, example absent
§12.3  unresolved_reference reasons     KEEP rc2's closed list
§12.4  two sort keys                    REPLACE
```

No `DROP`. Two `MOVE`s, one of which weakens a normative rule into a test case
and should be reversed in the consolidated document.

One `UNRESOLVED`, and it is not a conflict between rc1 and rc2:

```text
UNRESOLVED   meta's rule identity
```

rc2 §1.1 pins `spec_version = "3.4"`, `citation_rule_version =
"citation_v3.4_apa7_like_v1"`, `citation_profile = "apa7_like_v1"` and `mode`.
None of the four exists in v3.3, whose `meta` is the whole of
`{"type":"meta","spec_version":"3.3"}` — which is what this implementation
emits. So emitting any of them is the output declaring which specification
governs it, and `citation_rule_version` is half of rc2's own fingerprint tuple
`(canonical_manuscript_bytes, citation_rule_version)`, which is what decides
whether two runs are comparable at all.

That is a normative decision about what the artifact claims, not a formatting
fix, so it is left for the consolidation rather than taken here. It is the only
thing keeping C-068 open apart from rc3's additional fields, which rc3 requires
and which will not close while both documents are in force.

The summary's field names were taken, and the ground is on record: Alex
Zamurko's amendment of 20 September is written in rc2's vocabulary —
"`author_structure_mismatch` occurrences MUST NOT contribute to
`uniquely_matched_occurrences` or `uniquely_matched_works`" — which makes the
rename a decision already made rather than one this work would be making. There
is no equivalent instruction for `meta`.

---

## Step 2 status after this pair

```text
architecture            rc1 -> rc2   COMPLETE
conformance matrix      rc1 -> rc2   COMPLETE
deferred-work register  rc1 -> rc2   COMPLETE
execution conformance   rc1 -> rc2   10 IDENTICAL and closed
                                     §11 and §12 dispositioned clause by clause
                                     §8 and §9 remain, 202 changed lines
                                     §0, §2, §10, §14, §17, §19 remain, small
rc2 -> rc3                           seven discrepancies recorded
```

§8 and §9 are the last large pair, and they are where CIT-ARCH-01 is decided
rather than merely surfaced.
