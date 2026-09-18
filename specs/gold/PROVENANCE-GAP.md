# The citation figures rest on an implementation nobody can now run

Found 18 September 2026, while trying to produce a candidate to score the gold
sets against.

## What was looked for, and where

```text
Get-ChildItem C:\ -Recurse -Filter "impl_v34*.py"          nothing
Get-ChildItem C:\ -Recurse -Filter "corpus_run_*" -Directory   nothing
every *.py under C:\Users\gupta containing AUTHORS_NARR,
    unresolved_citation or apa7_like                       nothing
uploads to this session                                    specs and state
                                                           documents only
this repository                                            no extractor
```

The implementation used for the corpus runs of 28 and 29 August is not in
version control, is not on this machine, and was never uploaded here.

## What rests on it

Every citation accuracy figure produced so far:

```text
71.5%          run 1, eleven papers
83.1%          after the ampersand correction
92.2%          run 2, six reconciling papers, after \& and B4
91.2%          run 3, nine papers, +621 citations
93.2%          after the colon locator and cp.
95.0%          on the corrected denominator
1502 / 1611    the counts behind all of the above
142            the residual, and its decomposition into 22 classes
+17, +12       what rc3 tasks 1 and 2 are each said to be worth
```

**rc3 is frozen with those counts in its §I.** `ddc6f1f8…`, 3 September.

The corpus-run reports recorded provenance carefully — implementation SHA, all
input hashes, all output hashes, Python and regex versions, raw and transformed
inputs separately. That was the right instinct and it is worth saying that the
gap is not carelessness about provenance. The hash of the implementation was
recorded. The implementation was not kept.

So there is a digest naming an artifact nobody has. That is the same shape as
B01-F07 in the execution layer: a recorded hash that agrees with itself and
identifies nothing anyone can check.

## What this does and does not mean

It does not mean the figures are wrong. They were produced, reported and argued
over in detail, and the corrections applied along the way were real.

It means they are not reproducible, and nobody can now ask a question of that
run that the run did not already answer. If a reviewer disputes the residual
decomposition, or wants to know whether a particular citation was in the 142,
there is no way to find out except by rebuilding the extractor and hoping it
behaves the same.

It also means rc3's §I is frozen on evidence that cannot be re-derived. That is
not a defect in rc3. It is a fact about what freezing it captured.

## The inputs survived, and they are unchanged

Established 18 September, after the searches above came back empty.

`data/md_full/` holds all fourteen corpus papers, written 29 August 18:55, two
minutes after `data/all_md.b64` — the pipe-delimited base64 export the markdown
was moved out of the database with. That is the corpus the runs read.

Both papers now carrying gold sets are byte-identical in that directory to what
`papers.markdown` holds today:

```text
ad1e3ff9   md_full cff9bb85d74fbac8…   database cff9bb85d74fbac8…   same
c1d56945   md_full 48b2b2f459e5cad8…   database 48b2b2f459e5cad8…   same
```

So the corpus has not drifted since 29 August. Whatever was measured then was
measured against these bytes, and anything measured now is measured against the
same ones.

That matters more than it first appears. A replacement implementation cannot
reproduce the old figures, because the old implementation is gone. But it can be
run against the identical text, so a new figure and an old figure would differ
only by the extractor — which is the comparison anyone would actually want.

What survived and what did not is worth stating plainly:

```text
inputs       intact, verified byte-identical to the database
outputs      gone — corpus_run_2/ and the raw per-paper results
the code     gone
the reports  in Slack only, not in this repository
```

## What would close it

Either the implementation turns up — another machine, a notebook, a container,
wherever those runs were actually performed — or the figures are re-derived from
an implementation that is in version control this time, and the old ones are
kept as history rather than as current evidence.

The four gold sets in this directory are unaffected and wait for either. They
were annotated by hand from the manuscripts and verified against the corpus
markdown, so they do not depend on the extractor at all. They are the first
citation evidence that does not.
