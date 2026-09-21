# Both missing artifacts were in the assistant's own outputs folder

21 September 2026. Recovered while trying to answer a question from Alex
Zamurko about where rc3's `leading_gloss` count came from.

```text
rc3, frozen at ddc6f1f8…   RECOVERED   755 lines, exact hash match
impl_v34.py                RECOVERED   537 lines, exact hash match
corpus runs 1, 2, 3        RECOVERED
```

Both had been recorded as unrecoverable. `PROVENANCE-GAP.md` said the
implementation "is not in version control, is not on this machine, and was
never uploaded here". `RC3-FOUND.md` and the Step 1 inventory said no file
anywhere hashes to `ddc6f1f8…`.

All three statements were false, and every search that produced them was
looking in the wrong place.

---

## Where they were, and why nothing found them

They were in the assistant's own outputs directory, under `gsd/`, untouched
since 5 September. Copies are now in this repository at
`specs/citation/citation-v3.4-rc3-amendments-frozen.md` and
`specs/gold/recovered/`.

Everything ever searched, and what each covered:

```text
this repository                 the extractor's own lineage
session uploads, 1099 files     what was handed to the assistant
C:\ by filename                 impl_v34*.py, corpus_run_*
C:\ by content                  candidate_revision, NON_PERSON_AUTHOR
Downloads, by first line        what was downloaded from Slack
#citation Files tab             what was posted
git, 1250 blobs incl. dangling  what was ever committed
Google Drive, two needles       what was stored
nine byte normalisations        whether ddc6f1f8 was an encoding of c392982e
```

Not one of them covers the directory the assistant writes into. The uploads
folder was searched exhaustively — that is where material *arrives*. Its
sibling, where material *is produced*, was never searched once in three
separate hunts.

`PROVENANCE-GAP.md` records a `Get-ChildItem C:\ -Recurse -Filter
"impl_v34*.py"` that returned nothing, and the file was on `C:\` the whole
time. The likely reason is that the path runs through
`AppData\Roaming\Claude\…`, and a recursive scan without `-Force` that meets
access-denied errors continues past the subtree rather than failing. That is a
hypothesis, not a finding. Re-running the same command with `-Force
-ErrorAction SilentlyContinue` would settle it, and is worth doing before any
future search result is trusted as negative.

**The lesson is narrower and worse than "search more places".** A negative
search result was recorded three times as a property of the artifact — "nobody
has it", "it lives only in Slack" — when it was a property of the search. This
is the same defect the conformance suite keeps producing: a check that passes
for a reason other than the one it is named for. A search that finds nothing
is evidence about where you looked.

---

## What rc3 at `ddc6f1f8…` actually changes

Nothing in the grammar. The diff against `c392982e…` is **append-only**, twenty
lines at the end:

```text
735a736,755   a governing-spec note resolved 4 September, and a pointer to
              CITATION_v3.4_rc3_FREEZE.md
```

§A2 is byte-identical. Every amendment this repository implemented from
`c392982e…` is implemented from the frozen text too, so **no implementation
change follows from the recovery**. The two digests were never a grammar
question.

`c392982e…` is a truncated copy — a second download that stops before the
governing note. The frozen file is the authoritative one and is now in the
repository beside it.

---

## What `impl_v34.py` settles, and it is the substantive finding

`CITATION_CORPUS_RUN_3.md` records `impl_v34.py 50077031…`. The recovered file
hashes to exactly that, so this is the implementation behind every citation
accuracy figure quoted since 28 August.

It contains **no candidate-exclusion machinery at all**:

```text
excluded            0 occurrences
candidate_state     0
leading_gloss       0
conversion_artifact 0
url_or_image        0
publisher_metadata  0
```

Its only `reason` vocabulary is reference-side: `entry_start_grammar`,
`orphan_line`, `no_year`, `terminator`, `overlong`, `embedded_entry_pattern`.

So rc3 §A2's thirty exclusions were **not produced by the implementation**.
`CITATION_RESIDUAL_142.md` says where they came from, in its own words:

> Treat these as indicative. The classification is a heuristic pass and the 45
> are subject to gold adjudication; it is evidence that the gold set is the
> highest-value remaining item, not a substitute for one.

A2 presents as a closed set with exact counts. Its source is a pass its own
author labelled indicative and explicitly not a substitute for adjudication.
That is worth knowing before any of the six counts is treated as normative,
not only the two that lack rules.

---

## A candidate definition for `leading_gloss`

Recoverable from the evidence, and offered as a candidate rather than asserted.

`CITATION_RESIDUAL_142.md` names four examples of the 45 correctly-refused
spans: `(2014)`, `i.e., respect and dignity`, `MBSR`, and mathpix image links.
The second is a gloss. Filtering `CITATION_UNRESOLVED_109.md` for spans that
open with a gloss marker and carry no year gives six:

```text
e.g., goal setting or intellectual stimulation
e.g., using images and metaphors in a speech
e.g., from the Minnesota Satisfaction Questionnaire
e.g., emotional stability, conscientiousness, psychological capital, ...
i.e., distributive, procedural, informational, and interpersonal
i.e., respect and dignity
```

Each is a segment left behind by group splitting. The full parenthetical does
contain citations — `(e.g., goal setting or intellectual stimulation; Barling,
Weber, & Kelloway, 1996; …)` — and splitting on `;` leaves the lead-in text as
its own detected occurrence with no author-year in it.

```text
candidate definition   a split-produced segment whose text opens with a gloss
                       marker (e.g., i.e., viz., namely) and contains no YEAR
```

Six here against A2's eleven, but the 109 list is a subset of the residual the
count was taken over, so the two are consistent rather than in conflict. The
shape is what this establishes; the count is not re-derived.

Note the distinction this has to keep. rc3 **B5**, "bounded lead-in cue, +17",
is the *recovery* rule for `(e.g., Tepper, 2000)` — a real citation behind a
gloss. `leading_gloss` is the *exclusion* for the gloss with no citation in it.
Same marker, opposite dispositions, separated by whether a YEAR survives in the
span. Any definition that misses that separation will delete seventeen real
citations.

`conversion_artifact` has no comparable evidence trail and stays undefined.

---

## What this obliges

```text
RC3-FOUND.md                 corrected — the hash is not wrong, the search was
PROVENANCE-GAP.md            corrected — the implementation exists
CONSOLIDATION-STEP1-INVENTORY.md §4   corrected — nothing is unrecoverable
```

Stale claims were deleted rather than marked superseded, per the practice this
repository already follows.

Still open and genuinely undecided: whether `leading_gloss` takes the candidate
definition above, and what `conversion_artifact` means. Both are Alex Zamurko's
to settle. The difference after today is that the first has evidence attached
and the second is known to have none.
