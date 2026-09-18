# Citation edge cases: known, reproduced, not yet fixed

Cases where the extractor's behaviour is understood and wrong, recorded rather
than repaired. Alex Zamurko, 18 September 2026, on EC-1: *let's add it as an
edge case and record, we can fix it later.*

The point of the file is that each entry is reproduced and measured before it is
filed, so that "we can fix it later" starts from a known cost rather than from
a memory of a conversation. An entry states the shape, what the extractor does,
why, what it costs on the corpus, and what would close it.

Measured against `scripts/citation_extract.py` with all four corrections on
(`ampersand,segments,colon,cp`), over `data/md_full`, the corpus established
unchanged since 29 August in `PROVENANCE-GAP.md`.

---

## EC-1 — the coordinated "and" joining two narrative citations

**Confirmed correct usage**, not a malformed source. Alex checked it against the
style guidance: *right, I double checked it and it is a correct way to
reference.*

### The shape

```text
Seuring and Müller (2008) and Pagell and Wu (2009) structured the discussion.
                          ^^^
                          joins two works, not two authors
```

### What happens

The first citation parses. The second is lost.

```text
input     Smith (2020) and Jones (2021) disagree.
parsed    smith|2020
lost      and Jones (2021)        no_grammar_match
```

The reported span names its own cause. §6.1 walks left from the year to build
the envelope, `and` is eligible because it joins authors inside one work, so the
run starts at `and` — and no §4 production begins with a conjunction.

Nothing distinguishes the two jobs the word does:

```text
Duru and Therond (2015)              one work, two authors     parses
Smith (2020) and Jones (2021)        two works                 second lost
```

That is the whole defect. The token is eligible for a reason that is right in
one construction and wrong in the other, and the grammar sees only the token.

### What it costs

```text
12          occurrences across the nine in-profile papers
2.1%        of all 584 unresolved spans
1 of 15     works missed in gold paper 2 (c1d56945) attributable to it
```

The gap between twelve occurrences and one missed work is the useful part, and
it is not luck. A work is lost only when **every** occurrence of it sits in
coordinated position:

```text
Sauer and Seuring (2023)    2 occurrences, both coordinated      lost
Pagell and Wu (2009)        5 occurrences, 1 coordinated         recovered
Seuring and Müller (2008)   5 occurrences, 1 coordinated         recovered
```

So the occurrence count overstates the recall cost by roughly an order of
magnitude, because repetition rescues most of it. Anyone quoting the twelve as a
recall figure would be wrong, which is why both numbers are here.

Worth noting that the surviving Sauer occurrence is `Durach et al. (2017) and
Sauer \& Seuring (2023)` — the ampersand correction applies and the leading
`and` still takes it. Fixes do not compose their way out of this one.

### What would close it

The envelope would need to stop at a conjunction that follows a complete
citation, rather than treating every `and` as an author joiner. The signal is
available locally: a preceding `)` with a year in it means the `and` is joining
works. That is a change to §6.1, so it belongs in a spec revision rather than a
correction flag.

### Controls

`scripts/test_citation_extract.py` does not yet assert this, deliberately — the
current behaviour is wrong, and pinning it would make the eventual fix look like
a regression. It is pinned here instead.

---

## EC-2 — the possessive genitive is carried into the key

Found while measuring EC-1, and the more expensive of the two.

### The shape

```text
Fotiadis (2018) argues      ->  fotiadis|2018
Fotiadis's (2018) call      ->  fotiadis's|2018
```

Both parse. They are the same cited work and they receive different keys,
because `'s` is part of the matched CORE and nothing strips it.

### Why it is worse than being lost

A citation the extractor cannot parse lands in the unresolved list, where it can
be counted and argued about. This one does not. It is reported as `parsed`, with
a well-formed key, and the damage is downstream:

```text
distinct works, ea07e5f5          39 reported, 38 real
unmatched citation keys           exactly one: fotiadis's|2018
that work in the reference list   yes — "Fotiadis, A. (2018). Modelling wedding…"
```

So the paper's only reconciliation failure is an artefact of an apostrophe, and
the reference it failed to match is sitting in the same document. Nothing in the
output says so.

### Reach

```text
13 occurrences   across 6 of the 9 in-profile papers
4 papers         where the bare form also appears, so one work is counted twice
2 papers         where only the possessive appears, so the work is keyed wrong
                 with nothing to compare it against
```

`ad1e3ff9` (gold paper 1) carries `bartko's|1976`, `fine's|1998` and
`mcgraw and wong's|1996`. `c1d56945` (gold paper 2) carries none.

### What it costs, measured

Folding `'s` out of `author_phrase`, `surname` and `citation_key`, changing three
occurrences in gold paper 1 and nothing else, then rescoring through the same
`citation_candidate.py` and `gold_runner.py`:

```text
                as scored      with 's folded
recall            0.933            0.967
precision         0.884            0.916
```

**Recall crosses C1.** Alex Zamurko's threshold is ≥ 0.95 on both, set 28 August;
this moves one of the two over it on paper 1. Precision does not cross and is
not close, so the criteria are still unmet and the gap is elsewhere.

Paper 2 is unchanged by the fold, having no possessive occurrences, so this is
one paper's evidence and is not a corpus claim.

### What would close it

Strip a trailing `'s` or `'s` when deriving `surname` and `citation_key`, while
leaving `author_phrase` intact — rc3 §A requires `author_phrase` to record the
complete source phrase before reduction, so the possessive belongs in the phrase
and not in the identity derived from it. That is a §7 change, narrow, and
testable against the three occurrences above.

The measurement above deliberately folded `author_phrase` too, because the gold
set keys on it; a real fix would instead fold at the point the gold comparison
normalises. Worth saying plainly so the 0.967 is read as an upper bound on this
one change rather than as the result of the change that should be made.

### Controls

Not asserted in `test_citation_extract.py`, for the same reason as EC-1: the
current behaviour is wrong and pinning it would make the repair look like a
regression.

---

## How an entry gets here

A case is filed once it has been reproduced from a minimal input, its cause
traced to a numbered clause of the spec, and its corpus cost counted. A case
that has only been observed in a report is not an entry; it is something to go
and measure.

Nothing in this file is scheduled. It is a record of what is known to be wrong,
kept so the knowledge outlives the conversation it came from.

One note on how both entries were found. EC-1 came from Alex and was filed on
request. EC-2 was found while measuring EC-1 and was nearly filed wrong: the
first draft recorded it as *one occurrence, lost behind EC-1, unclear whether it
would parse alone*. Testing the bare form instead of assuming showed it parses,
keys differently, appears thirteen times, and costs more than EC-1 does. The
difference between the two drafts was one command. That is the argument for the
reproduce-and-measure rule above, and it is not hypothetical.
