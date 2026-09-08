# Gold Set v0.1 — A.1-E gap extraction

**Source manuscript.** Rodríguez, Amaya-Rivas, Samaniego, Luzzini, Merino-Gaibor,
"From agroecology to regenerative supply chain design: A systematic literature
review", *Journal of Purchasing and Supply Management*, S1478-4092(26)00063-4.

**Annotator.** Alex Zamurko, 7 September 2026, posted in #gap.

**Status.** Single-annotator baseline, **not** gold under `A1E-AVP-1.2` (D01).
D01 defines how gold is made, adjudicated and compared so that system output can
be scored without circularity. This annotation was produced by the author of the
specifications, so scoring a system built from those specifications against it is
not independent. Either D01's regime is applied to it, or it is used as a
single-annotator baseline and labelled as one. This file takes the second
reading until someone decides otherwise.

---

## Positive cases — six tagged gaps

Character offsets are into the normalised manuscript text defined in
§"Text normalisation" below. All six were confirmed present **verbatim** on
7 September 2026.

```text
id   §      p   char    relation / type              verbatim
G1   §1     1   3246    constrained / unable to capture      yes
G2   §1     1   3488    limited / insufficient               yes
G3   §1     1   3641    missing / absent                     yes
G4   §1     2   5623    disconnected / not integrated        yes
G5   §2.1   2  10869    limited / insufficient               yes
G6   §4.5   9  52791    limited / insufficient               yes
```

**G1** — positioning of the RSCM agenda rather than the gap this paper fills.

> Prior sustainable supply chain research has often emphasized "do less harm"
> practices and incremental improvements, which can understate the scale of
> change implied by ecological degradation

**G2** — the primary gap. A synthesis is missing, and it is what motivates a
review design.

> Yet, despite progress in conceptualizing RSCM, the literature still offers
> limited design-relevant synthesis for agri-food supply chains.

**G3** — specification of G2 into three sub-gaps: coordination arrangements and
market linkages, where capabilities reside, governance beyond transactional
exchange. These are the three to check against the §5.1 contributions.

> we lack a clear account of which coordination arrangements and market linkages
> can support regenerative outcomes, where capabilities need to reside, and how
> governance can move beyond purely transactional exchange

**G4** — justifies the choice of agroecology as evidence base.

> Yet purchasing and SCM research has only partially engaged with this body of
> evidence, even though it directly concerns inter-organizational coordination
> and value distribution in supply chains.

**G5** — restates G2 and G3 in the literature review, now attributed to the RSCM
literature specifically. Same deficiency.

> However, it remains less explicit about the concrete coordination and
> governance arrangements through which regeneration is pursued in agri-food
> supply chains, where ecological outcomes depend on land-based production and
> multi-actor interdependence

**G6** — appears in Results. A finding *about the reviewed literature*, not a gap
motivating this study.

> There is limited evidence on the autonomy of these organizations after the
> assistance program ends

---

## Negative controls — two deliberately untagged

**N1 — Table 1, §2.1 p.2.** Future-research gaps attributed to cited papers, e.g.
"Regeneration remains a nascent concept in business." These are gaps stated by
*other* authors and reported here. Not the paper's own gaps, although they ground
G2 and G3.

**N2 — §6, p.12.** "Future research should therefore test the proposed
configurations and their boundary conditions through comparative and
longitudinal designs, examine how procurement and contracting mechanisms shape
capability development and governance across configurations, and develop
feasible metrics for regenerative performance and distributive justice at the
supply chain level." A gap the paper opens for others, not one it addresses.
FUTURE_RESEARCH.

---

## What this set decides that the register left open

**HD-01 — does GAP membership require an eligible positioning context?**
The register listed three options; the annotation takes none of them. G6 is
tagged as a gap *and* flagged as needing separation from a motivating gap. So
membership is decided by function, and section role becomes a recorded property
with downstream consequence:

```text
motivating gap        §1 introduction, §2 literature review   G1..G5
gap reported as a result   §4 results                          G6
gap opened for future research  §6 conclusion                  N2
```

**HD-10 — where is the rule for attributed / reported deficiencies?**
The register found none in D07 or D08. N1 supplies it: a deficiency attributed to
a cited work is not the manuscript's own gap, but may ground one.

Both belong in the consolidated specification, not only here.

---

## Text normalisation — required, and it is a real finding

The six quotes are verbatim **only after** two normalisations. Neither is
optional, and a naive extraction fails all six.

**1. Reading order.** The manuscript is two-column. `pdftotext -layout`
interleaves the columns mid-sentence:

```text
... emphasized "do less harm" practices and in­ Agricultural supply chains sit
at the center of today's socio-ecological cremental improvements, which can
understate ...
```

One sentence, split by text from the adjacent column. No verbatim match survives
this. Plain `pdftotext` (no `-layout`) recovers reading order on this document.

**2. Soft hyphens.** The PDF carries U+00AD at line-broken words:

```text
in­cremental   ->  stripping U+00AD alone leaves  "in cremental"
liter­ature    ->                                  "liter ature"
organi­zations ->                                  "organi zations"
```

The soft hyphen **and the whitespace following it** must be removed together.
Removing only the character leaves a word split by a space, which no exact-span
comparison will find. Three of the six quotes fail on this alone.

```python
n = re.sub(r'­\s*', '', text)   # soft hyphen + following whitespace
n = re.sub(r'-\n\s*', '', n)         # hard hyphen at line break
n = re.sub(r'\s+', ' ', n)
```

**Consequence, and it is the same shape as the ampersand problem in ingest.**
The extraction rules are fine; the bytes reaching them are wrong. A.1-E's
source-grounding requirement — verbatim quote, exact span — cannot be evaluated
against naive PDF text at all. Gold must be scored against the manuscript's
canonical stored text, which in this system is `papers.markdown` produced by the
conversion path, not against a local `pdftotext` run.

**Open dependency.** That means Gold Set v0.1 needs this manuscript in the
corpus. It is not among the fourteen rows measured on 4 September, and the ingest
path is mid-migration under Stage 1 v9. Either the manuscript is ingested first,
or the gold runner is given a pinned text artifact with its own hash and the
divergence from `papers.markdown` is recorded.

---

## Not established here

- Whether the six are complete. The annotation says every deficiency statement
  was tagged; that is one annotator's sweep, not a measured recall.
- Whether G1 is a gap this paper fills or only positioning. The annotation says
  positioning; A.1-E has no rule that distinguishes them.
- G5 as restatement of G2/G3 is asserted, not resolved under `A1E-GI-1.0`.
  Identity is a Step-9 decision and this set records the annotator's reading of
  it, not a rule application.
