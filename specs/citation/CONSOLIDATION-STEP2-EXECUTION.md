# Consolidation Step 2 — the execution conformance document, rc1 against rc2

Against Alex Zamurko's consolidation workflow v6, 21 September 2026.

```text
citation-v3.4-rc1-execution-conformance.md   11edbf89…  1402 lines  SUPERSEDED
citation-v3.4-rc2-execution-conformance.md   4fa95af1…  1576 lines  CURRENT
```

The largest pair, and the one carrying the grammar.

**The grammar did not change.** Comparing section text rather than titles, ten
of rc2's twenty numbered sections are byte-identical to rc1's, and they are
exactly the ones a grammar change would have to touch:

```text
IDENTICAL   §1  pinned constants and canonical text
            §3  closed lexical and grammar primitives
            §4  document structure
            §5  sentence segmentation
            §6  Pass 1 — citation occurrence extraction
            §7  bibliography assembly and reference identity
            §13 file output and atomicity
            §15 test-only invariant-injection seam
            §16 out of envelope and accepted limitations
            §18 corpus blocking taxonomy

CHANGED     §0  capability and scope                 7 lines
            §2  execution modes                     47
            §8  Pass 2 — identity                   93
            §9  reconciliation                     109
            §10 bibliography-absent mode            24
            §11 summary invariants                 100
            §12 canonical JSONL output              58
            §14 exit and abort semantics             5
            §17 mandatory conformance classes        4
            §19 freeze and GSD-pilot gate           40
```

So rc1 → rc2 is one thing, stated plainly: **it rewrites the identity and
reporting model and leaves the parser alone.** PREFIX, STOP, the candidate
envelope, parenthetical and narrative parsing, sentence segmentation and
bibliography assembly all survive unchanged.

That is the single most useful fact in this pair. It means the grammar this
implementation is built from did not move between rc1 and rc2, and every
unimplemented conformance case in §8 to §12 belongs to one coherent body of
work rather than to scattered drift.

Reproducible: `python scripts/rc1_rc2_section_diff.py`.

---

## Structural comparison

```text
rc1   68 headings
rc2   71 headings
```

Three sections are genuinely new. Everything below each insert shifts by one,
which accounts for most of what looks like renumbering.

```text
rc2 §2.2   Standalone with supplied map           NEW
rc2 §8.4   Unmatched candidate set                NEW
rc2 §11.3  Bibliography absence                   NEW
```

Seven sections keep their number and change their title. Each was read; the
retitles are not cosmetic and are listed with what they signal.

```text
§2.1   Standalone mode
    →  Standalone no-map mode — GSD pilot target
       Scope narrowing. The pilot is now named IN the section rather than
       inferred from the package.

§9.1   Identity and duplicate index
    →  Bibliography identity and duplicate index
       Disambiguation: the index is the bibliography's, not the citation's.

§9.2   Per-occurrence outcome classification
    →  Identity classification
       The reframing rc1 §11 -> rc2 §9 made in the architecture file, landing
       here. Outcomes become identity states.

§9.3   Unique matches and author structure
    →  Unique EXACT matches and author structure
       One word, and it is load-bearing: it separates a unique match from a
       unique exact match, which is what rc2 §9.3's author-structure rule
       then qualifies.

§9.4   Missing versus possible mismatch
    →  CANDIDATE-LEVEL possible mismatch and missing reference
       This is the one normative correction Alex Zamurko named when he posted
       the package on 28 August.

§11.2  Reconciliation partition — only when performed
    →  Identity-resolution invariant — conditional
       Same conditional-partition idea, restated on identity rather than
       reconciliation.

§19    Freeze gate
    →  Freeze and GSD-pilot gate
```

---

## The one normative correction, located

Alex Zamurko, posting the rc2 package on 28 August:

> One normative correction was necessary in rc2: `missing_reference` and
> `possible_mismatch` are now explicitly candidate-level diagnostics when exact
> bibliography identity is absent. They cannot manufacture an authoritative
> `citation_key`; `citation_key` stays null until bibliography evidence
> establishes identity.

It lands in **§9.4**, whose retitle carries it, and rc2's verbatim text there:

> This subsection applies only to occurrences where:
> `identity_class = identity_not_resolved AND exactly one deterministic
> internal candidate exists`
>
> The diagnostic candidate key remains **non-authoritative**. [...] Neither
> diagnostic establishes `citation_key`, `author_kind`, or
> `resolved_citation_occurrences`.

```text
disposition   REPLACE — rc2's §9.4 text replaces rc1's
evidence      the change is stated by its author in the channel AND visible
              in the section title AND present in the section body
```

Worth recording that all three agree. This is the only substantive change in
this pair whose intent is documented outside the files themselves, and it is
the one that needed least reconstruction as a result.

---

## What the three new sections are for

### §8.4 Unmatched candidate set — NEW

```text
one internal candidate
    → candidate-level missing/mismatch diagnostics MAY run

two distinct internal candidates
    → identity is underdetermined even before fuzzy repair
    → missing_reference and possible_mismatch MUST NOT emit for that occurrence
```

This is what makes §9.4's correction safe. Without it, an occurrence with two
viable candidates could still emit a candidate-level diagnostic naming one of
them, which is the guess the correction exists to prevent. `NEW`, and
load-bearing for the section above it.

### §11.3 Bibliography absence — NEW

Summary fields go `null` rather than `0` when identity resolution did not run.
`0` would mean "ran and found none"; `null` means "not evaluated". rc1 carried
the distinction in prose; rc2 makes it a field list.

**"Eight" was wrong, corrected 23 September.** rc2 §11.3 has ten entries: nine
null and one zero, the zero being `resolved_citation_occurrences`, which is a
real measurement rather than an absent one. The count is now generated from
rc2's bytes in `CONSOLIDATION-STEP2-SUMMARY-AND-OUTPUT.md` and in C-067's
control, because it was miscounted twice by eye — once as eight here, once as
ten in the correction.

### §2.2 Standalone with supplied map — NEW

A third execution scope between the pilot and the orchestrated pipeline, and
explicitly "separate from the pilot target". Matches rc2's architecture §14.2,
which is also new. Scope work, not behaviour.

---

## What is NOT covered here

**All ten are now dispositioned, 23 September.**

```text
§8  Pass 2 identity            93 lines   CONSOLIDATION-STEP2-IDENTITY-AND-
§9  reconciliation            109 lines   RECONCILIATION.md
§11 summary invariants        100 lines   CONSOLIDATION-STEP2-SUMMARY-AND-
§12 canonical JSONL            58 lines   OUTPUT.md
§0, §2, §10, §14, §17, §19               CONSOLIDATION-STEP2-SCOPE-AND-GATE.md
```

§11 and §12 are dispositioned clause by clause in
`CONSOLIDATION-STEP2-SUMMARY-AND-OUTPUT.md`. Taken together rather than in
order, because §12's record shapes are what §11's invariants are computed over.
Two findings from that pair are worth carrying here:

- rc1 §11.2's partition is **arithmetically unsatisfiable** — it partitions
  `total_citation_occurrences` over identity outcomes that `unresolved_citation`
  rows never receive. Off by 133 on this corpus. rc2 corrects it silently by
  moving the left-hand side to `extracted_citation_occurrences`.
- rc1 uses six summary terms in its invariants and defines none of them. rc2
  §11.4 defines all six plus `identity_resolution_performed`, which rc1 lacks.

Three findings from the other two pairs worth carrying here:

- **rc1 §8's opening clause permits a syntax-derived `citation_key`** and rc2
  forbids it. That one sentence is what CIT-ARCH-01 decides; rc1 was not silent
  on the question, it answered it the other way.
- **rc2 §19 removes Section Map and Orchestrator as freeze dependencies for the
  pilot scope.** The single most consequential change in the pair for whether
  work can proceed, and invisible unless §0, §2 and §19 are read together.
- **rc2 §14's exit-1 set is closed** at twelve conditions. Three of them were
  being missed entirely — all three facts about the bibliography, which no
  proxy over citation matching can see.

What no longer needs covering: §3 and §6 were flagged as the dangerous
undiffed sections, on the reasoning that a silent wording change in the grammar
would do the most damage. Both are byte-identical, so that risk is closed
rather than outstanding.

---

## Step 2 status after this pair

```text
architecture            rc1 → rc2   COMPLETE
execution conformance   rc1 → rc2   COMPLETE, 23 September.
                                    10 sections byte-identical, 10 CHANGED
                                    dispositioned clause by clause.
conformance matrix      rc1 → rc2   COMPLETE
deferred-work register  rc1 → rc2   COMPLETE
rc2 → rc3                           seven discrepancies recorded
```

No `DROP` and no `UNRESOLVED` found in what has been compared so far, in either
pair.
