# Parked work

Work that was built or investigated and then deliberately set aside. Not
abandoned, and not unfinished by accident.

This file exists because the two failure modes around parked work are both
expensive. One is rediscovering a problem somebody already solved. The other is
finding a half-built package and having to guess whether it was left that way on
purpose. Each entry below says what exists, what does not, why it stopped, and
what would restart it.

**Status at 17 August 2026**

| | Parked | Code in the repo? | Decided by |
|---|---|---|---|
| 1 | Table and figure extraction | **Yes**, tested, wired to a CLI command | Alex, 17 Aug |
| 2 | The published XGBoost methodology model | No | Alex, 17 Aug |
| 3 | Weak-keyword tier for section roles | No | Alex, 16 Aug |

---

## 1. Table and figure extraction

**Parked because:** we can operate without tables for now.

### What exists

| File | State |
|---|---|
| `internal/core/domain/exhibit/exhibit.go` | Complete |
| `internal/core/domain/exhibit/exhibit_test.go` | 23 fixtures, each taken from a real paper |
| `internal/core/domain/exhibit/deps_test.go` | Determinism guard |
| `cmd/epistemicos-cli/exhibits.go` | `exhibits <paper-id> [--rows]` |

It is left in the tree on purpose. Nothing depends on it, the command is
additive, and deleting a tested package to "clean up" would mean rebuilding it
and rediscovering the same ten papers' worth of edge cases.

### What it does

Measured across all ten ingested papers, 902,867 characters:

- **74 tables**, 70 of them captioned (95%), 851 rows of cell data
- **20 figures**, with the page and crop box each was cut from
- 27 tables contain LaTeX in their cells

It also names the section each exhibit sits in, by calling the segmenter on the
same bytes rather than loading a stored run.

### What does not exist

**Persistence.** The command prints. There is no table, no store, no migration.
That was the deliberate stopping point: the output should be looked at on a few
papers and the shape agreed before it is written down.

**LaTeX stripping.** 27 of 74 tables have math in their cells, so those values
are not plain strings and a numeric column is not yet numeric. Flagged per table
as `HasLatex`; nothing acts on the flag.

**Section attribution is positional only.** See below.

### Three findings worth not losing

**The naive rule fails silently.** "A caption is a line starting `Table N` whose
next line is a table row" scores 61 of 74 across ten papers, and **zero of twenty
on one of them** — a paper whose captions put the label on its own line. Nothing
errors. That paper simply appears to contain no tables. Any future version of
this must report a count per paper so a sudden zero is visible.

**Position is not authorship.** A caption lands where it fitted on the page.
On the ESG paper, *Table 1. Loadings, reliability, and convergent validity* is
measurement-model material sitting inside §4.2 Structural model; Tables 4 and 5
are results sitting in the Discussion. The better link is the paper's own
cross-reference — nineteen lines across the ten papers say things like *"Table 3
shows the results of the hypotheses testing"*, which look like false positives to
a caption detector and are in fact the document saying what each table is for.
**Store both** when this is picked up.

**We do not need Mathpix's CDN.** Every figure URL carries its page number and
crop box, so a figure can be re-cut from the PDF we already store at ingest.
Verified by rendering page 19 of the ESG paper at successive scales and finding
the one where the crop stops clipping: **240 DPI**, recorded as
`exhibit.MathpixRenderDPI` with the method beside it.

This one has a deadline attached. All 26 images across the ten papers are links
to `cdn.mathpix.com` and nothing is stored on our side. If those URLs expire, every
figure in every ingested paper becomes a dead link, quietly and all at once. The
fix is cheap now and gets more expensive with every paper ingested.

### What would restart it

A consumer that needs table data — most likely whatever reads results sections
and wants the numbers behind them. At that point: agree the storage shape, write
the migration, add LaTeX stripping, and add the cross-reference link.

---

## 2. The published XGBoost methodology model

**Parked because:** the counting step works without it. Five of five
single-method papers correct, both mixed-methods papers flagged.

### Where things stand

The glossary from Kosztyán et al. (2025) is implemented in
`internal/core/domain/methodology` under the paper's CC BY licence, with
attribution in the source. Their trained model is **not** used and their code
repository is **not** used.

Two blockers, and they are different in kind:

**Licence.** The repository `github.com/kzst/article_classifier` carries no
licence file, which by default means all rights reserved. Reading it is fine;
copying it into ours is not.

**Security.** The model is distributed as a Python pickle, and loading a pickle
executes whatever code is inside it. A two-year-old binary from an unlicensed
repository with no checksum is not something to open on a machine that holds
credentials.

An email went to the corresponding author, Zsolt T. Kosztyán, on 17 August 2026,
asking for a licence and for the model exported as JSON rather than pickle.

### What would restart it

A reply granting both. If it arrives, the next step is measured rather than
assumed: run their model against the same papers and see whether it beats
counting. If we run it at all, it goes in a throwaway container with no network
and no access to our data.

### The cheaper thing to try first

Only **95 of the 301** glossary terms are labelled as leaning quantitative or
qualitative. The other 206 are counted, displayed, and move the score not at all.
On the ESG paper that meant 346 term occurrences fired and only 95 counted — the
verdict rested on about a quarter of what was found.

Labelling more of the 206 against the methods literature is a morning's work,
needs no licence, stays deterministic, and would tell us how much of the gap is
actually the model's doing.

---

## 3. Weak-keyword tier for section roles

**Parked because:** a good idea, and time-consuming. Alex's words, 16 August.

The idea was a second, lower-confidence keyword tier for section headings that
match nothing in the main role table. It was overtaken: parent inheritance (2.2)
and child consensus (2.3) between them took the reference paper from nine open
review questions to none, which was the problem the weak tier existed to solve.

### What would restart it

A paper where inheritance and consensus both fail and a human is still being
asked about headings that a looser keyword list would have answered. Worth
checking the review queue for that pattern before building anything.
