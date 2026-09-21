# Citation v3.4 rc3 — freeze record

4 September 2026.

`CITATION_v3.4_rc3_AMENDMENTS.md` is frozen. The text below is the stamp of the
document as frozen. Any change requires a new revision and a new stamp; the
frozen text is not edited in place.

```text
file     CITATION_v3.4_rc3_AMENDMENTS.md
sha256   ddc6f1f80c93d12d6268cda03fffb6720adac3b4bb9bc5da351f8c5a28a108e2
bytes    29,586      lines 755
```

## What freezing this satisfies

The governing-spec note at the end of the frozen document names the dependency:
this is the governing amendment set for rc3, it amends the four-file rc2
package, and nothing else amends rc2. The implementation work queued behind the
freeze is §I's two forward tiers.

```text
SPECIFIED AND AGREED
  B5  bounded lead-in cue        +17
  B6  compact year-suffix         +2
                                 +19

BOUNDED NEW GRAMMAR
  B1a surname production          +9
  B1b non_person citation path    +8
  B8  possessive, bounded gap     +7
  B7  and colleagues              +4
  B2  lowercase core after particle  +1
  B9  segment-split orphan        +1
                                 +30
```

Stated as §A5 requires, measured and counted kept apart:

```text
CURRENTLY MEASURED
  all detected candidates          1502 / 1611  =  93.2%
  excluding the classified 30      1502 / 1581  =  95.0%

COUNTED CONSEQUENCE, NOT MEASURED
  if B5 and B6 recover all 19 registered cases with zero regressions
                                   1521 / 1581  =  96.2%
```

These map onto the two GSD subject tasks Alex defined in #citation on
31 August, each with a countable done condition:

```text
task 1   B1a + B1b     bounded SURNAME production, plus the citation-side
                       NON_PERSON_AUTHOR detection path      +17

task 2   B7 + B8 + B9  and colleagues, possessive with a bounded gap,
                       segment-split orphan                  +12

residual B2            lowercase core after a matched particle  +1
                                                             ----
                                                              +30
```

Task 1 deliberately bounds the production rather than the span: `Van den Brink
and Van der Woerd` is seven tokens and appears twice in the corpus, so any token
cap breaks it. B1a and B1b are separate because a person surname production
cannot reach `International Monetary Fund` without admitting `of` as a particle,
which would corrupt the person grammar to reach organisations.

## Baseline the frozen document records

```text
corpus       9 in-profile reconciling papers, 14-paper export
baseline     1502 / 1611  =  93.2%   after \& + rc2-B4 segment splitting
                                     + rc3-B3 colon locator + rc3-B4 cp.
residual     109, fully classified, zero unclassified
```

## Not covered by this freeze

Two ingest transforms are normative in §J and **not implemented**:
`ampersand_unescape_v1` and `math_wrapped_year_parenthetical_unwrap_v1`. The
measured figures used an ad hoc `sed` for the first. D2 has no measured result
and no hash because it has not been run. Freezing the specification does not
make these exist.

## Precedent

Same treatment as `INGEST_STAGE1_v8.md`, frozen 1 September 2026 at
`91d73e0a6747511d07c09e78535569e748b980cd86148177c9bfcac9c308bceb`, 36,490
bytes, 984 lines. That hash was re-verified against the file on 4 September and
still matches.
