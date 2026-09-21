# Consolidation Step 2 — the matrix and register pairs

Against Alex Zamurko's consolidation workflow v6, 21 September 2026. These are
the last two pairs, and they complete Step 2's structural coverage.

```text
citation-v3.4-rc1-conformance-matrix.md      73f4ba54…  227 lines  SUPERSEDED
citation-v3.4-rc2-conformance-matrix.md      f0f1aa37…  138 lines  CURRENT

citation-v3.4-rc1-deferred-work-register.md  7d241438…  282 lines  SUPERSEDED
citation-v3.4-rc2-deferred-work-register.md  0bf1cc12…  230 lines  CURRENT
```

---

## The conformance matrix

Both documents are renumbered, so the comparison is by title and by case
identifier rather than by section number.

```text
rc1                                   rc2                                    disposition
────────────────────────────────────────────────────────────────────────────────────────
1. Status vocabulary                  1. Evidence states                     REPLACE
2. Conformance matrix                 2. Conformance matrix                  REPLACE
3. Prefix attestation coverage        —                                      see below
4. Corpus finding classification      3. Blocking-finding taxonomy           REPLACE
5. Freeze checklist                   4. GSD-pilot freeze checklist          REPLACE
5.1 Candidate identity                4.1 Candidate identity                 MOVE
5.2 Static specification completeness 4.2 Static closure                     REPLACE
5.3 External dependency gates         5.  Non-pilot scope gates              MOVE
5.4 Executable conformance            4.3 Pilot-scope executable evidence    REPLACE
5.5 Independent review / authority    4.4 Independent review / freeze        REPLACE
—                                     4.5 GSD-pilot preflight                NEW
6. Current verdict                    6. Current verdict                     REPLACE
```

The shape of the change is the pilot. rc1's checklist is a general freeze gate;
rc2's is a **GSD-pilot** freeze gate with a preflight, and the dependency gates
are lifted out into their own section because they explicitly "do not block
pilot-scope freeze".

### One case disappeared, and it is a MOVE

```text
rc1   87 case identifiers, C-001 … C-087
rc2   86 case identifiers, C-001 … C-086
```

The missing one is **C-087**, and rc1's verbatim row:

> | C-087 | no accuracy claim from 11 papers | governance | artifact review |
> corpus report labels itself regression/conformance only |

Its scope is `governance`. rc2's matrix has no governance-scope rows at all —
every one of its 86 is `pilot`, `standalone_map` or `pipeline`. So the case was
not deleted; the governance scope was lifted out of a pilot matrix.

The rule survives in three places, checked rather than assumed:

```text
rc2 architecture §18   "The current manuscript corpus is regression/conformance
                       discovery evidence. It is not a population-validity
                       sample and MUST NOT support generalized accuracy claims."

rc2 register X-11      population-level validation study, "deferred but
                       required before generalized accuracy claims"

rc3 §A5                "Extraction accuracy, precision and recall MUST NOT be
                       reported until a gold set exists."
```

```text
disposition   MOVE — from the matrix into rc2 architecture §18, rc2 X-11 and
              rc3 A5, with rc3 stating it most strongly
```

**Not a DROP**, and worth having checked. A missing case identifier is exactly
what Step 2's gate is for, and the naive reading — 87 became 86, one case was
cut — would have been wrong.

It is also the one already implemented. rc3 A5's form of this rule is what the
summary record obeys today: it carries `candidate_parse_rate` and no accuracy
field, with a control that goes red if any key matching accuracy, precision or
recall appears.

---

## The deferred-work register

```text
rc1   X-01 … X-14
rc2   X-01 … X-14, titles identical for all fourteen
```

No item added, none removed, none renumbered. The titles match exactly. What
changed is inside the entries and in the surrounding sections, which are not
dispositioned here.

Two entries are load-bearing for findings already recorded elsewhere, and both
say the same thing in rc1 and rc2:

```text
X-07   Broader bibliography author grammars. "Includes comma-containing
       organization authors and richer full-forename list parsing."
       → confirms discrepancy 2 (FAO stays unresolved) and is the identifier
         rc3 §C3 misnames — discrepancy 7

X-08   ConversionArtifactAnnotations / conversion repair, deferred upstream.
       → the likely referent of rc3 A2's undefined `conversion_artifact`
         exclusion reason
```

```text
disposition   KEEP for all fourteen X-items at the title level
              entry bodies NOT dispositioned — this pair's clause-level
              comparison is outstanding
```

---

## Step 2 status — structural coverage complete

```text
architecture            rc1 → rc2   COMPLETE
execution conformance   rc1 → rc2   10 sections IDENTICAL and closed,
                                    10 CHANGED and identified
conformance matrix      rc1 → rc2   structural, and C-087 resolved as MOVE
deferred-work register  rc1 → rc2   structural, X-01..X-14 KEEP at title level
rc2 → rc3                           seven discrepancies recorded
v3.3 → v3.4                         CIT-ARCH-01 DECIDED
```

**Across all four pairs: no `DROP` and no `UNRESOLVED` found.** Every rc1 rule
that appeared to vanish turned out to have moved, and each move was checked to
its destination rather than assumed:

```text
rc1 arch §8    Bibliography-grounded author kind  → rc2 arch §3.2
rc1 arch §17   Atomic publication                 → rc2 execution conformance
rc1 matrix     C-087 no accuracy claim            → rc2 arch §18, X-11, rc3 A5
```

What remains for Step 2 is clause-level work inside the ten CHANGED execution
sections and the entry bodies of the register. What is settled is the shape:
**nothing was deleted, the grammar did not move, and the whole of the change
is the identity and reporting model.**
