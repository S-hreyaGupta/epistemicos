# Consolidation Step 2 — §0, §2, §10, §14, §17, §19, rc1 against rc2

Against Alex Zamurko's consolidation workflow v6. 23 September 2026.

The six sections left after §8, §9, §11 and §12. Small by line count and not
small in consequence: **§19 unblocks the pilot**, and §14 turned out to contain
a closed rule this implementation was satisfying by accident.

```text
§0  capability and scope            rc1  19 ->  22 lines
§2  execution modes                      55 ->  74
§10 bibliography-absent mode             45 ->  51
§14 exit and abort semantics             66 ->  67
§17 mandatory conformance classes        27 ->  27
§19 freeze and GSD-pilot gate            16 ->  30
```

With this pair the execution-conformance document is dispositioned end to end.

---

## The finding that matters most: rc2 removes the pilot's blockers

rc1 §19 made freeze conditional on two external artifacts, for everything:

> - the exact Section Map v1.1 dependency is frozen/current and bound by
>   version + SHA-256 + freeze/disposition evidence;
> - Orchestrator v2.3 (or its formally superseding current contract) is
>   verified for the pipeline scope;

rc2 §19 removes both from the pilot's path, in as many words:

> Section Map and Orchestrator are **not** freeze dependencies for the
> standalone/no-map pilot scope.

This is the single most consequential change in the whole rc1 → rc2 diff for
whether the pilot can proceed, and it is invisible unless the sections are read
together. rc2 splits one conformance scope into three (§0), gives each its own
execution mode (§2), and then §19 gates them separately.

```text
rc1   two scopes    citation_v3_4_standalone_cli_apa7_like_v1
                    citation_v3_4_epistemicos_pipeline_apa7_like_v1

rc2   three scopes  citation_v3_4_standalone_cli_nomap_apa7_like_v1   <- pilot
                    citation_v3_4_standalone_cli_with_map_apa7_like_v1
                    citation_v3_4_epistemicos_pipeline_apa7_like_v1
```

The pilot scope "has no Section Map or Orchestrator runtime dependency" (§2.1).
The other two remain `not_yet_authoritative` until their dependencies are bound.

```text
disposition   REPLACE across §0, §2 and §19 — one change in three places
consequence   the pilot's freeze gate no longer waits on two artifacts this
              repository does not hold
```

### And a governance rule that should be read before it is tripped

rc2 §19 closes with a sentence rc1 has no equivalent of:

> The GSD pilot runbook MUST treat any attempt to Execute product code before
> the pilot target scope is frozen/current as a preflight failure. GSD planning,
> convergence, or code MUST NOT create new citation behavior; any discovered
> normative gap routes back to the specification lifecycle.

Read precisely: "Execute" is capitalised and names a GSD lifecycle stage, not
the act of running a program. The rule constrains the **GSD runbook**, not
conformance work — a conformance implementation built to demonstrate the
cases is what §19's own gate requires ("pilot-scope executable conformance
cases have accepted evidence").

The second half is the part to hold onto: *GSD planning, convergence, or code
MUST NOT create new citation behavior.* Every gap this work has found routes to
the spec, not to a local decision. That is what the deviation notes in
`citation_extract.py` are for, and it is worth recording that rc2 asks for
exactly that discipline in normative text.

```text
disposition   KEEP rc2's §19 gate text
note          not a constraint on conformance work; a constraint on GSD
```

---

## §14 — the exit-1 set is closed, and three conditions were being missed

rc1 and rc2 both list the conditions forcing exit 1. rc2 adds one and renames
two:

```text
NEW       any extracted citation with `author_resolution=not_resolved`
RENAME    residual missing_reference  -> candidate-level missing_reference
RENAME    possible_mismatch           -> candidate-level possible_mismatch
```

The renames follow the 28 August correction. The addition is new.

**The list is closed — twelve conditions — and the conformance map said it was
not.** C-078 read "the exit-1 finding set is not closed", which is wrong about
rc2 and right about the implementation. This file tested three proxies:

```text
every citation uniquely matched
no unresolved_citation
no `exact` author_structure_mismatch
```

Eight of rc2's twelve coincide with "not every citation uniquely matched" and
were satisfied without ever being consulted. Three do not coincide at all,
because they are facts about the **bibliography**, and no fact about the
bibliography alone can stop a citation matching:

```text
condition                     fixture                          was   rc2
residual uncited_reference    every citation matched, four      0     1
                              references nobody cited
unresolved_reference          every citation matched, one       0     1
                              malformed entry
any suspect reference         every citation matched, one       0     1
                              1600-character entry
```

Each was demonstrated exiting 0 where rc2 requires 1, on a document where the
old proxy is satisfied. Implemented as rc2's twelve, evaluated over the emitted
records rather than the locals the blocks were built from — a condition read
off the stream is what rc2's reader sees; one read off a local agrees with the
code that produced it whether or not the record reached the output.

```text
disposition   REPLACE — rc2's §14 list replaces rc1's
implemented   23 September. C-078 MET, with the control counting rc2's list
              rather than this file's tuple
corpus        no exit code changes: all thirteen papers already exited 1
```

The summary now also carries `exit_findings` — the names of the conditions that
fired. Not an rc2 field. §14 says exit 1 means "one or more defined finding
conditions" and then lists twelve; a bare `1` tells a reader that some member of
a twelve-item set is true and leaves them to work out which.

---

## §10 — bibliography absence, and two enum values rc1 could not express

Already dispositioned as behaviour in `CONSOLIDATION-STEP2-EXECUTION.md`. The
clause-level changes:

```text
rc1  Pass 2 identity resolution   not performed
rc2  Pass 2 identity resolution   NOT EVALUATED

rc1  author_kind        = unresolved      author_resolution = unresolved
rc2  author_kind        = undetermined    author_resolution = not_evaluated
```

"Not performed" and "not evaluated" are the same distinction as `0` against
`null`, one level up: rc1's vocabulary cannot separate *the lookup ran and
matched nothing* from *there was nothing to run it against*. rc2 gives the
second its own word in both fields.

rc2 also adds a shape constraint absent from rc1: "`bibliography_absent` has
exactly two fields, no index, and appears iff `references_source=not_available`."
Implemented; C-009 and C-066 pin it.

```text
disposition   REPLACE
```

---

## §17 — two conformance classes retitled

```text
14. mismatch pairing precedence
 -> candidate-level mismatch pairing precedence AND PROOF THAT IT DOES NOT
    ESTABLISH CITATION IDENTITY

17. bibliography-absent nullable summary
 -> bibliography-absent `not_evaluated` IDENTITY STATE and nullable summary
```

Both add a requirement rather than rewording one. Case 14 now demands proof of
a negative — that the pairing establishes nothing — which is C-053 and C-054,
closed on 23 September once `identity_authority` was emitted. Case 17 adds the
identity state to what was a summary-shape requirement.

```text
disposition   REPLACE, and both are met
```

---

## §0 and §2 — scope, covered above

§0 declares the three scopes and names the pilot. §2 splits standalone into
§2.1 no-map and §2.2 with-map, pushes orchestrated to §2.3, and renumbers the
determinism tuple to §2.4. One substantive line beyond the scope split:

```text
rc1  section_map_bytes : null | exact Section Map v1.1 JSONL bytes   [optional]
rc2  section_map_bytes                                        [FORBIDDEN]
     The implementation MUST execute the deterministic standalone structure
     fallback in §4.
```

In the pilot scope a supplied map is not merely absent, it is forbidden. rc1
allowed one optionally and fell back when it was missing. This implementation
accepts no map argument at all, so it satisfies the stricter rule — but it
satisfies it by never having offered the option, which is worth stating rather
than claiming as conformance.

```text
disposition   REPLACE
note          met structurally, not by an implemented prohibition. C-084 to
              C-086 are the map-consuming scopes and rc2 marks them
              OUTSIDE_PILOT
```

---

## Dispositions, collected

```text
§0    two scopes become three        REPLACE   pilot named in the document
§2.1  standalone -> no-map, map      REPLACE   a supplied map is FORBIDDEN here
§2.2  standalone with map            NEW
§2.3  orchestrated                   REPLACE   renumbered from 2.2
§2.4  determinism tuple              REPLACE   renumbered from 2.3
§10   not performed -> not evaluated  REPLACE
§10   bibliography_absent shape      NEW       two fields, no index
§14   exit-1 condition added         REPLACE   + three were being missed
§17   classes 14 and 17 retitled     REPLACE   both add a requirement
§19   freeze gate split by scope     REPLACE   PILOT UNBLOCKED
§19   GSD runbook preflight rule     NEW
```

No `DROP`, no `UNRESOLVED` in this pair.

---

## Step 2 status — the execution pair is complete

```text
architecture            rc1 -> rc2   COMPLETE
execution conformance   rc1 -> rc2   COMPLETE
                                     10 sections byte-identical
                                     10 sections dispositioned clause by clause
conformance matrix      rc1 -> rc2   COMPLETE
deferred-work register  rc1 -> rc2   COMPLETE
rc2 -> rc3                           seven discrepancies recorded
v3.3 -> v3.4                         DECIDED, CIT-ARCH-01
```

Across the whole of Step 2: **no `DROP`**. Two `MOVE`s, both keeping their rule
normative. Two rows were opened as `UNRESOLVED` and both closed the same day,
neither having been a conflict between rc1 and rc2:

```text
meta's rule identity     CLOSED — the output declares v3.4, because the rules
                         it runs are rc2's and rc3's throughout and `3.3` was
                         a wrong label rather than an undecided one
identity_class spelling  CLOSED — §11's, because the counts are named after
                         it. rc2 disagreeing with itself is a finding for the
                         consolidation, not a decision it had to wait on
```

The one open implementation item, §9.1's `duplicate_reference_key`, was also
closed: five groups across four papers, five records now emitted.

What Step 3 needs that this does not supply: the workflow v6 text is still not
in the repository, so every gate these documents cite is one a reader cannot
check against its source.
