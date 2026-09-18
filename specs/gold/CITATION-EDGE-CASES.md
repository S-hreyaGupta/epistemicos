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

**It costs twice per work, which this entry first missed.** Established in
`ADJUDICATION-paper-1.md`: the gold set holds `bartko 1976` and the candidate
produces `bartko's 1976`, so the gold item goes unmatched — a miss — and the
possessive form is absent from gold — a false positive. Three works, six
penalties. That is why both figures move together above, which the first
version of this entry recorded without explaining.

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

## EC-3 — the six-token envelope attributes long author lists to the wrong author

Unlike EC-1 and EC-2, this one is **spec-conformant**. §6.1 says the C2 run
collects eligible tokens "at most 6", and the implementation collects at most
six. Nothing here is a coding error, and it cannot be repaired without amending
the specification.

### The shape

A narrative citation with five or six authors runs past six tokens, so the run
starts partway through the author list. §6.2's longest-admissible-suffix rule
then parses what it can see, which is a shorter but perfectly well-formed
author list, and reports it with confidence.

```text
source     El Akremi, Gond, Swaen, De Roeck, and Igalens (2015)
run        [Gond,] [Swaen,] [De] [Roeck,] [and] [Igalens]     six, cap reached
parsed     author_phrase "Gond, Swaen, De Roeck, and Igalens"
key        gond|2015
```

The work is by El Akremi and colleagues. It is recorded as Gond.

This is not a refusal. It is a `parsed` record with a well-formed key,
indistinguishable in the output from a correct one, which puts it in the same
family as EC-2 and makes it the most expensive of the three.

### Every instance in the corpus

Four, all the same shape — first author dropped, second author becomes the key:

```text
50408397   El Akremi, Gond, Swaen, De Roeck, and Igalens (2015)   -> gond|2015
e1b418a4   Mackinnon, Jorm, Christensen, Korten, Jacomb, and
           Rodgers (1999)                                          -> jorm|1999
e1b418a4   Mayer, Thau, Workman, Van Dijke, and De Cremer (2012)   -> workman|2012
ad1e3ff9   Van den Brink and Van der Woerd (2004)                  -> den brink|2004
```

The last one also produces a duplicate: the same work is cited
parenthetically elsewhere in that paper, where no C2 run is needed, and keys
correctly as `van den brink|2004`. So one work, two keys, one of them wrong —
the EC-2 pattern arriving by a different route.

Three of the four predate the particle fix of 18 September and are live today.
The fourth, `den brink`, was invisible before it: the citation did not parse at
all. So that fix turned one silent miss into one wrong record, which is worth
saying plainly even though it raised recall on both gold papers.

### What a larger envelope is worth, measured

```text
cap    parsed    unresolved    effect
 6      1103        574        as specified
 7      1103        574
 8      1102        575        three of the four corrected
 9+     1102        575        nothing further changes at any size up to 16
```

Per work, at 8:

```text
Mackinnon et al. 1999     jorm|1999      ->  mackinnon|1999      corrected
Mayer et al. 2012         workman|2012   ->  mayer|2012          corrected
Van den Brink … 2004      two keys       ->  van den brink|2004  corrected, duplicate gone
El Akremi et al. 2015     gond|2015      ->  unresolved          see EC-4
```

Nothing is lost, and no new key appears anywhere else in the corpus, so on this
corpus the envelope is not acting as a false-positive brake at these sizes.
That is evidence from ten papers and not an argument about the rule.

The El Akremi case turns a wrong attribution into an honest refusal, which is
an improvement of a different kind: a refusal is counted and arguable, a wrong
attribution is neither.

### What would close it

An amendment to §6.1 raising the cap. The measurement above says 8 captures
everything this corpus contains and that 9 through 16 add nothing, but a cap
chosen from ten papers is a cap fitted to ten papers, and the number belongs to
whoever owns the specification rather than to this file.

**This needs a decision, not a repair.** Nothing here has been changed.

---

## EC-4 — a compound surname whose first word is not a particle

Found inside EC-3, and it is why raising the envelope leaves one of the four
unresolved rather than correct.

```text
El Akremi       "El" is not in PARTICLE, so SURNAME cannot span both words
                SURNAME = (PARTICLE WS)* CORE — one CORE, particles ahead of it
```

`El Akremi et al. (2015)` and `(El Akremi et al., 2015: 2)` both fail, so with
a larger envelope the work has no key at all in `50408397` rather than a wrong
one. One work on this corpus.

The same limit covers `Carrieri de Souza` and `Oliveira da Silva` from paper 2,
where the particle sits *inside* the surname rather than ahead of it. Three
works, all unresolved, all refused for the same structural reason.

Widening PARTICLE to include `el` would fix one case and not the other two,
which are CORE PARTICLE CORE and outside the production's shape entirely.

## EC-5 — citations inside footnotes are invisible

Found 18 September while accounting for the last unexplained miss in gold
paper 1. Structural rather than grammatical, and the only entry here that
produces **no record of any kind** — not a citation, not an unresolved span.

### The shape

Mathpix renders footnote *definitions* as `[^n]:` blocks and places them at the
end of the document, after the reference list. §3 splits body from references at
the References heading and extracts only from the body, so every footnote body
falls on the wrong side of that line and is never read.

```text
...a specific category (country of origin or industry group) (Dooley et al., 2019).

[^7]:    ${ }^{8}$ This variable meas...
```

`(Dooley et al., 2019)` is a well-formed parenthetical with a valid year. It
appears in neither output list. A reader of the results cannot tell it exists.

### Reach

```text
31 footnote blocks   across 5 of the 9 in-profile papers
11 citations         would parse if the same text sat in the body
 2 papers            ad1e3ff9 and e1b418a4 carry all eleven
```

```text
ad1e3ff9   Cohen (1988), Fagiolo (2007), Dooley et al. (2019)
e1b418a4   Earley et al. (1989), Cook and Campbell (1979) x2,
           Buhrmester et al. (2011), Colquitt et al. (2015) x2,
           Kline (2011), Kline's (2011)
```

### Why it costs recall rather than being a scope choice

The annotation reads footnotes. Gold paper 1 contains `fagiolo 2007` and
`dooley et al. 2019`, both of which are cited in footnotes, so the gold set and
the extractor disagree about what part of the document counts.

`dooley et al. 2019` is one of the five works gold paper 1 still misses at
v0.2, and it is the only one of the five without a cause in this register —
which is how the entry was found.

### What would close it

A §3 change: footnote definition blocks are body text wherever the converter
puts them, and the body/references split should exclude them from the reference
side rather than swallow them. The ambiguity is real — a `[^n]:` block after the
References heading looks structurally like part of the reference list — so this
is a specification question about what the body is, not a bug in the splitter.

**This needs a decision, not a repair.** Nothing has been changed.

## How an entry gets here

A case is filed once it has been reproduced from a minimal input, its cause
traced to a numbered clause of the spec, and its corpus cost counted. A case
that has only been observed in a report is not an entry; it is something to go
and measure.

Nothing in this file is scheduled. It is a record of what is known to be wrong,
kept so the knowledge outlives the conversation it came from.

One note on how these were found, because each came out of the one before it.

EC-1 came from Alex Zamurko and was filed on request. EC-2 was found while
measuring EC-1, and was nearly filed wrong: the first draft recorded it as *one
occurrence, lost behind EC-1, unclear whether it would parse alone*. Testing the
bare form instead of assuming showed it parses, keys differently, appears
thirteen times, and costs more than EC-1. EC-3 and EC-4 came out of a
spec-conformance fix to particle matching, which raised recall on both gold
papers and simultaneously turned one silent miss into one wrong record; chasing
that single regression is what surfaced the envelope.

Three of the four were found by following a measurement that did not match
expectation, rather than by anything designed to look for them. The one
designed check in this area — the conformance suite — passed throughout, because
§12 pins the string `van der Maas (2022)` and the suite tested that string.

Two corrections were made to this file after first writing, both because a set
difference disagreed with a direct look. EC-2's cost was recorded as one
penalty per work and is two. EC-3's cap-8 effect was recorded as two works
corrected and two orphaned, and is three corrected and one turned into a
refusal; the missing key was already present from another occurrence and the
set difference hid it. Both are noted rather than silently amended, since the
failure mode is the subject of the file.
