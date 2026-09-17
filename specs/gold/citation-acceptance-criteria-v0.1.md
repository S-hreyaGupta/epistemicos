# Citation extraction — acceptance criteria, v0.1

For §15.2, which evaluates a candidate against predefined acceptance criteria
when there is no executable baseline.

**Written 17 September 2026, before the first score was computed.** The gold
sets and the candidate files existed; nobody had run one against the other. That
ordering is the only thing that makes a threshold a criterion rather than a
description, and it is asserted here because nothing can verify it after the
fact.

## Unit

Distinct cited works, not occurrences. The gold sets list each work once; the
candidate is collapsed to works by `citation_candidate.py`, which records the
occurrence count per work so nothing is destroyed.

## Criteria

```text
C1  recall    >= 0.95     of the works a paper cites, the extractor finds at
                          least one occurrence of at least 95%

C2  precision >= 0.95     of the works the extractor reports, at least 95% are
                          works the annotator recorded

C3  no institutional author in the gold set is entirely absent from the
    candidate

C4  no multi-token surname in the gold set is entirely absent from the candidate
```

## Why 95

It is Alex Zamurko's figure, set on 28 August 2026: *"Stop once both precision
and recall are ≥95%."* Adopted rather than chosen here.

## Why C3 and C4 exist separately

C1 and C2 are aggregates and can be met while the specific classes rc3 was
written for all fail, because those classes are a small fraction of any paper.
rc3 §B1a claims +17 for multi-token surnames and §B1b claims +8 for
institutional authors; if those rules are worth what they claim, the cases
should be present, and an aggregate that hides their absence is the same defect
as an aggregate hiding a regression.

## What failing these does not mean

A work in the gold set and absent from the candidate is a miss by the
extractor. A work in the candidate and absent from the gold set is **either** a
false positive **or** a citation the annotator did not record. The second is
ordinary on a first annotation pass and is not a failure of the extractor. C2 is
therefore a weaker claim than C1 and should be read as a prompt to re-read the
manuscript, not as a verdict.

## Scope

Two papers, `ad1e3ff9` and `c1d56945`, of the fourteen in the corpus. Meeting
these criteria on two papers is not meeting them on the corpus, and this
document does not claim otherwise.
