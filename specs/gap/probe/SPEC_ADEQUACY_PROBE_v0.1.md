# Spec-adequacy probe — A.1-E against Gold Set v0.1

**What this is.** Claude applying `A1E-BR-1.2`'s decision procedure (§38.15, D0–D6)
to the manuscript, and comparing the result to Alex Zamurko's annotation.

**What this is not.** A code baseline. A single unbounded pass has more context
and more freedom than the bounded typed calls the design uses, so a good result
here is not evidence the pipeline will work. **Failure is informative; success is
not.**

Run 7 September 2026 against `manuscript_normalised.txt` (two-column reading
order recovered, soft hyphens removed per `GOLD_SET_v0.1.md`).

---

## The manuscript's stated focus, as G5 requires

```text
RQ         How do agroecological practices inform the design of
           regenerative supply chains?

"design"   the recurring coordination, governance, and market-linkage
           arrangements that connect agroecological production with
           downstream demand

objective  systematizing agroecological practices for producing,
           coordinating and delivering agri-food products in ways that
           can regenerate socio-ecological systems
```

Everything below turns on this. G5 is satisfied only by explicit discourse
linkage (38.14 A) or proposition-level alignment with this focus (38.14 B), and
**shared topic never satisfies it.**

---

## Result

14 candidate units surfaced by deficiency-predicate scan. Classified under
§38.15.

```text
unit   char    §          gold        probe                    agree
C01    3382    intro      G1  GAP     UNCERTAIN(T3)             NO
C02    3573    intro      G2  GAP     GAP                       yes
C03    3654    intro      G3  GAP     GAP ×3 instances          partial
C04    5675    intro      G4  GAP     GAP                       yes
C05    8935    Table 1    N1  —       OTHER                     yes*
C06    9434    Table 1    N1  —       UNCERTAIN(T3)             yes*
C07   10908    §2.1       G5  GAP     GAP (restatement)         yes
C08   12262    Table 1    N1  —       FUTURE_RESEARCH           yes
C09   27063    §4.1       —           OTHER                     yes
C10   33622    §4.3       —           OTHER                     yes
C11   52468    §4.5       —           OTHER                     yes
C12   52937    §4.5       G6  GAP     OTHER                     NO
C13   69241    §5          —          OTHER                     yes
C14   74472    §6          —          OTHER                     yes
N2    §6 p.12  concl      N2  —       FUTURE_RESEARCH           yes

positives   3 clean agreements, 1 partial, 2 disagreements
negatives   8 of 8 agree
```

`*` Same output, different rule. See DL-02.

---

## The two disagreements

### C12 / gold G6 — the rulebook already excludes it, and not on section grounds

> There is limited evidence on the autonomy of these organizations after the
> assistance program ends

```text
D1 assertion    deficiency predicated             ROUTE A
D2 target       "evidence" = prior knowledge      → D3
D3 grounding    "these organizations" anaphoric,
                antecedent present                 context_supported → D4
D4 function     38.14 A — no explicit linkage
                38.14 B — "evidence on cooperative autonomy after an
                assistance programme" is not the same question,
                relationship or phenomenon-aspect as "how agroecological
                practices inform supply chain design". Topical overlap
                via "organizing forms" only, which 38.14 B excludes
                by name.
                                                   linkage clearly absent
                                                   → OTHER (BR-OTH-5)
```

The annotation tags it GAP and adds that the tool "should distinguish a
motivating gap from a gap reported as a result". **D07 already does that, and by
a different mechanism than section role.** G5 excludes it because its proposition
does not align with the study's focus, and §38.14 says in terms that section
location is never evidence either way.

So the register's HD-01 is answered more decisively than either option (a) or
(b) suggested: section never gates membership, positioning does, and G6 fails
positioning on its content.

### C01 / gold G1 — no rule for agenda-level positioning

> Prior sustainable supply chain research has often emphasized "do less harm"
> practices and incremental improvements, which can understate the scale of
> change implied by ecological degradation

D1–D3 pass. G5 is the problem. The annotation's own note says the function is
"positioning of the RSCM agenda rather than the gap this paper fills directly."

38.14 offers no third form. A deficiency that positions the *field's agenda*,
which the study then joins, is neither explicit discourse linkage nor
proposition-level alignment with the study's own focus. The procedure's exits are
OTHER when linkage is clearly absent and UNCERTAIN(T3) when alignment is
indeterminate. Agenda-framing is indeterminate rather than clearly absent, so:
**UNCERTAIN(T3)**.

---

## The partial: C03 / gold G3

> we lack a clear account of which coordination arrangements and market linkages
> can support regenerative outcomes, where capabilities need to reside, and how
> governance can move beyond purely transactional exchange

Classified GAP, and it aligns with the focus by containment — the study defines
"design" as exactly these arrangements.

But the unit asserts **three** deficiencies. `DP-CROSS-3` requires one
`(relation, knowledge_kind)` pair per deficiency proposition, and §38.13 governs
multi-proposition treatment, so this should yield three extraction instances. The
annotation records one gap with three sub-gaps. Not a disagreement about class,
a disagreement about cardinality, and Step 9 identity would then have to decide
whether the three are one gap or three.

---

## Decision log — where the documents underdetermined and I chose

This is the output that matters. Each of these was resolved to run at all.

**DL-01 — HD-01, resolved by D07 rather than by the register's options.**
Section location never satisfies or defeats G5 (§38.14). Membership is decided by
positioning function on propositional content. Consequence: C12 is OTHER. Chosen
because §38.14 states it explicitly; no interpretation was required.

**DL-02 — HD-10 is live, and my agreement on C05/C06/C08 is luck.**
No rule in D07 or D08 governs deficiencies attributed to cited works. Table 1
carries three. I excluded them on G5 grounds. The annotation excludes them on
attribution grounds. **Same output, different rule**, which means the corpus does
not distinguish the two readings here and a manuscript where an attributed
deficiency *does* align with the focus would separate them. That case is not in
this manuscript.

**DL-03 — "we lack" and the D2 target test.**
C03 says "we lack a clear account". D2 routes present-study targets to
OWN_LIMITATION. Nothing in D07 or D08 says whether first-person plural in an
introduction denotes the present study or the scholarly community. I read it as
the community, because the clause concerns the state of accounts in the
literature and precedes any description of this study. A rule is needed; the
opposite reading turns the manuscript's primary specification into
OWN_LIMITATION.

**DL-04 — compound splitting cardinality.**
Applied `DP-CROSS-3` and split C03 into three. The annotation does not. Neither
document states which is authoritative when a gold set and an extraction spec
disagree on cardinality.

**DL-05 — no exit for agenda-level positioning.**
C01. 38.14 has two forms and neither fits a deficiency that positions the field's
agenda rather than this study's contribution. I took UNCERTAIN(T3) over OTHER
because alignment is arguable, not clearly absent. A third form, or an explicit
statement that agenda-framing is OTHER, would remove the judgement.

**DL-06 — the world/capability rule did the most work and nobody flagged it.**
Five of the eight negatives (C09, C10, C11, C13, C14) were excluded at D2 by
`BR-CROSS-14`: the deficiency targets practitioner capability or the world, not
knowledge. None appears in the gold set at all. That rule is carrying more of the
precision than any positioning rule, and it is untested by this gold set because
the annotator never considered these units candidates.

---

## What the probe actually establishes

The specification is **usable**. §38.15 terminated in exactly one class for all
fifteen units, and the failure routing was never ambiguous at D1–D3. That is not
nothing; most specifications this size do not survive contact with a real
document.

It **disagrees with the annotation on two of six positives**, and in both cases
the rulebook has the stronger argument on its own terms. That is a finding about
the gold set as much as about the specification.

Five of eighteen open decisions did not arise. Six did not bite. The ones that
did are DL-02, DL-03, DL-04 and DL-05, and only DL-03 and DL-05 change an
outcome.

**What it does not establish.** That a bounded pipeline reaches the same result.
Every classification above used the full manuscript, the full rulebook, and the
stated focus simultaneously. CALL 1 in the design gets a candidate and its
co-text envelope, not the introduction's focus statement 3,000 characters away.
G5 in particular is not computable from a candidate window, and that is a design
question the specifications do not currently answer.
