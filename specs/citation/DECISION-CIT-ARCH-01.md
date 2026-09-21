# Decision CIT-ARCH-01 — citation identity authority

Recorded in the form Alex Zamurko's consolidation workflow v6 requires for
Step 3 adjudication.

```text
Decision ID      CIT-ARCH-01
Decision-maker   Alex Zamurko
Date             21 September 2026, #citation, 21:52
```

## Issue

v3.3 and v3.4 give different answers to the same question and the running
implementation followed both.

```text
v3.3        the extractor derives citation_key at extraction time, from the
            citation's own syntax

rc1 §2.2    author_kind, authoritative citation_key and distinct cited-work
rc2 §3.2    identity require bibliography-grounded resolution. "Syntax alone
            MUST NOT establish" them.
```

rc1 and rc2 agree with each other. The conflict is v3.3 against v3.4, and v3.3
is the separate lineage the code was written from.

## Decision, verbatim

> In-text citation evidence may generate and narrow candidate reference
> identities, but it may not independently confirm reference identity. A
> citation is CONFIRMED only when it matches a compatible reference-list entry.
> If no compatible entry exists, classify it as MISSING_REFERENCE while
> preserving the citation-derived candidate. If multiple compatible entries
> remain, classify it as AMBIGUOUS; do not guess.

## Reading

Four clauses, and each already has a counterpart in rc2. Checked against the
files rather than assumed:

```text
may generate and narrow candidates     rc2 §8: "Pass 1 syntax creates
                                       deterministic identity candidates only"
may not independently confirm          rc2 arch §3.2: "Syntax alone MUST NOT
                                       establish"
CONFIRMED only on a compatible entry   rc2 arch §3.2: "established only when
                                       bibliography resolution supports one
                                       candidate identity"
multiple compatible → AMBIGUOUS        rc2 §8.3 and ambiguous_author_resolution
missing preserves the candidate        rc2 §9.4: "the diagnostic candidate key
                                       remains non-authoritative"
```

So the decision is **v3.4's model**, and it does not introduce anything rc2
does not already specify. That matters for Step 3: it is a `REPLACE` with text
already present and checked, which the workflow requires before `REPLACE` is
valid.

One clause is worth reading twice. "**Preserving** the citation-derived
candidate" means `MISSING_REFERENCE` is not a discard. The candidate survives
in the record as non-authoritative evidence, which is exactly what rc2 §8.4 and
§9.4 build and what rc3 A1's three terminal states report.

## Remainder

**Empty.** The decision settles the authority question for every affected row.
It does not by itself say what the key format becomes, but that is not a
remainder — rc2 §7.5 already specifies `person|…|year` and `non_person|…|year`,
so it is a consequence with its own source text rather than an open question.

Per the workflow's rule 5, an empty remainder means the decision **may change
the affected row dispositions**.

## What it changes

```text
dispositioned   the v3.3 branch of every identity row becomes DROP, and rc2's
                text becomes the REPLACE
unblocked       ~10 conformance cases directly — C-037..C-045, C-052 — and the
                surrounding identity work they sit in
```

Against rc2's conformance matrix, the decision reaches roughly a third of what
is currently unimplemented:

```text
10  C-037..C-045, C-052   3×3 identity decision table
 4  C-048..C-051          ambiguous_author_resolution and reservation
 4  C-053..C-055, C-061   candidate-level diagnostics
 5  C-056..C-060          §9.4 repair rules
 3  C-066, C-067, C-009   bibliography-absent identity states
```

## What it costs, stated honestly

This is not a small change and the record should say so before anyone plans
against it.

```text
citation_key         becomes null until bibliography resolution confirms it.
                     Today every parsed citation carries one from extraction.
ordering             references must be assembled before identity, which the
                     non-person path already does; person identity has to move
                     behind the same boundary.
key format           rc2 §7.5 prefixes person keys, so every existing key,
                     both gold sets, and every conformance case asserting a
                     key changes shape.
gold scoring         the gold sets key on author phrase and year, so they
                     survive the prefix; the candidate adapter does not yet.
```

The current implementation already sits on the correct side of this line for
non-person authors, because rc3 B1b could not be built any other way. What the
decision does is require the same for person authors, where v3.3's shortcut is
still in place.

## Status

```text
Step 3    CIT-ARCH-01 DECIDED, remainder empty, dispositions may change
Step 4    consolidation may now build the identity sections from rc2's text
          rather than holding them UNRESOLVED
code      NOT YET IMPLEMENTED. Recorded as the next substantial piece rather
          than started at the end of a working day.
```
