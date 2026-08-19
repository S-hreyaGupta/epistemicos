# Future work

Everything known and not done. Two kinds of entry, kept in one file on purpose:
**parked** work that was built and then set aside, and a **to-do list** of smaller
things that are simply not done yet.

The two failure modes around deferred work are both expensive. One is
rediscovering a problem somebody already solved. The other is finding a half-built
package and having to guess whether it was left that way on purpose. So each
parked entry says what exists, what does not, why it stopped, and what would
restart it.

**Status at 17 August 2026**

## Parked

| | Parked | Code in the repo? | Decided by |
|---|---|---|---|
| 1 | Table and figure extraction | **Yes**, tested, wired to a CLI command | Alex, 17 Aug |
| 2 | The published XGBoost methodology model | No | Alex, 17 Aug |
| 3 | Weak-keyword tier for section roles | No | Alex, 16 Aug |

## To do

Smallest first. Each names the file it belongs to, so it can be picked up without
reading this whole document.

| | Item | Where | Size |
|---|---|---|---|
| A | **Strip LaTeX from table cells.** 27 of 74 tables carry `$\beta$`, `$\mathrm{R}^{2}$` and similar, so a numeric column is not yet numeric. `HasLatex` flags them; nothing acts on it. | `domain/exhibit` | hours |
| B | **Unescape captions.** Figure B1 of the ESG paper reads `Distribution of N/As count and N/A\%`. Captions need the same treatment as cells, sharing one function rather than growing two. | `domain/exhibit` | minutes |
| C | **Persist exhibits.** The `exhibits` command prints and stores nothing. Deliberate: look at the output on a few papers and agree the shape first. | new migration | day |
| D | **Store tables by cross-reference as well as position.** A caption lands where it fitted on the page, not where its table is discussed. Nineteen lines across the ten papers say things like *"Table 3 shows the results"* — that is the document naming its own link. | `domain/exhibit` | day |
| E | **Download figure images at ingest.** All 26 images point at `cdn.mathpix.com`. Nothing is stored our side. See parked item 1 for the deadline this carries. | `services/ingest` | day |
| F | **Label more of the 301 glossary terms.** Only 95 are marked; the other 206 are counted and move nothing. On the ESG paper the verdict rested on a quarter of what fired. | `domain/methodology` | morning |
| G | **A borderline test case for the paper-type gate.** Five of five is five papers. The cases that will break it are conceptual-versus-narrative-review, and empirical-with-a-formal-model. | `domain/papertype` | hours |
| H | **Report exhibit counts per paper.** One paper hid a total extraction failure. Anything built on this should make a sudden zero visible rather than silent. | wherever it lands | hours |
| I | **Rotate the Mathpix key, and unpin the credentials message.** The console password has been sitting in a pinned WhatsApp message for weeks. | operational | minutes |

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

**Escapes leak into captions.** Seen on the first real run: the ESG paper's
figure B1 comes back as `Distribution of N/As count and N/A\%` — Mathpix's
backslash-escaped percent sign, passed through verbatim. Captions need the same
unescaping as cells, and the two should share one function rather than growing
separate ones.

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
