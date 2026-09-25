# Six controls asserted an absence and nothing else

25 September 2026. The vacuity sweep went from refusing to passing on this
date. This is why, written so the change can be checked rather than trusted.

## What the sweep asks, and what it could not answer

`scripts/vacuity_sweep.py` disables all three citation-side record emitters
and runs the suite. A control that still passes is not testing anything the
extractor emits. On 25 September the first completed empty run put that number
at 130 of 323, against a pinned list of 20 that had been read by hand.

Re-pinning to 130 would have asserted, 110 times over, the exact thing the
file exists to catch: a number that passes because nobody looked at it. So it
refused, and the refusal was correct. But refusing is not a result, and
reading 130 labels one at a time is work that does not get done.

## The property that made reading them unnecessary

Grouping the survivors by the suite's own section headings showed something
the flat list had hidden. All twenty-three groups are all-or-nothing. Not one
section has some controls surviving and some going red:

```text
rc2 §4.2  the standalone heading contract        23 of 23 survive
rc2 §6.7 / §9.3  author-structure coherence      14 of 14 survive
rc2 §13 / §12.1  file output and canonical bytes 12 of 12 survive
rc2 §14  the closed exit-1 finding set             7 of 7 survive
...                                          twenty-three groups, all N of N
```

That is what a suite organised by subject looks like, and it is a hint:
survival is a property of what a section tests, not of how carefully each
control was written. The testable form of that hint is one line, and it was
already written in the sweep's own docstring before anyone acted on it:

    does this control read any citation-side output at all?

A control that reads nothing the three emitters produce is testing a constant,
the reference side, the output bytes or an abort. An empty citation stream
tells it nothing either way, and there is nothing in it to read. A control
that does read, and passes with all three empty, is the defect.

## How it was measured

The disabled build returns read-logging lists. Each read made from outside the
extractor prints the suite line that made it. Two details decide whether the
number means anything:

```text
the immediate caller decides        run() consumes all three lists itself
                                    while building the summary, so counting
                                    those flags every end-to-end control
                                    regardless of what it asserts

attribution is by SOURCE position   the suite prints its failures on the way
                                    out, so a control that goes red prints
                                    nothing at its own position. 193 go red
                                    in the disabled run, and by stream order
                                    every read all 193 made lands on whichever
                                    survivor prints next
```

Stream order gave 8 survivors with clusters of twenty-two and thirty reads on
single controls, which is what that leak looks like from outside. Source order
gave 4, one of which was `case()` calling `ok()` on a control's behalf from
line 227. Closing that gave 3, each with its own lines.

The markers go to file descriptor 2 rather than stdout, because several
controls capture stdout to compare it byte for byte or to parse it as JSON. An
earlier version printed to stdout and the suite died on a `JSONDecodeError`
inside a control, which is a diagnostic corrupting the artifact under test.

## The three that read the empty output

All three have one shape: named for a refusal, asserting only an absence.

```text
rc2 §8   with no reference entry, the institution stays unresolved
§4       widening the year list left the author/year comma required
§C       naming the defect did not loosen the grammar
```

Each was written as `if keys(cits): fail else: ok(...)`. `not cits` is equally
true of a span the grammar refused, a span never detected at all, and a run
emitting nothing, so the control reported the first whichever one held. The
§8 case is the sharpest: a span silently dropped is not the refusal §8 asks
for, it is the failure §8 exists to prevent, wearing the same absence.

Measured first rather than guessed, because the compound-surname probe drew a
confident wrong conclusion twice from an invented fixture header. All three
fixtures produce an `unresolved_citation` with reason `no_grammar_match`, so
all three could be repaired inside the suite: assert the refusal and its
reason, and an empty run fails them.

## The three that were already known

With the pin no longer deciding the verdict, every survivor is measured, and
three more appeared. They are exactly the three the pinned list had marked
PAIRED ONLY, with the note that each was sound because of a positive sitting
beside it in the file rather than because of anything internal:

```text
1499 is invisible, not unresolved
square brackets produce no record at all
a damaged group loses everything without the segments flag
```

The measurement and the hand reading agreed to the label, on three of twenty,
with no other pinned control flagged. That agreement is the reason to trust
the probe on the other 120.

Their claim really is about absence, so the repair is not to assert presence
but to make the pairing part of the control. `case()` gained an `alive=`
argument naming a companion body that must still produce a citation; the
inline one asserts its companion directly. Absence only carries information
once presence is shown possible on the same path, and that is now said in the
control rather than implied by what sits next to it.

## What the sweep now checks

```text
was    the survivor set is exactly the pinned twenty
now    no surviving control reads citation-side output
```

124 survive the empty run and not one of them asks the citation side
anything. Unlike a list of labels, this does not go stale as the suite grows:
a new control that reads the empty output and passes fails the sweep on the
day it is written, without anyone re-reading anything.

## What this does not establish

Not that the 123 are well written. It establishes that none of them can be
fooled by an empty citation stream, which is one failure mode, and the one
this file was built to find. `mutate_citation_suite.py` asks the complementary
question about the rule each control names, and `--census` asks whether each
record type is watched at all. Three different questions, and a control can
still be weak in ways none of the three reaches.

One survivor is dropped before the split, because its label is built with an
f-string containing a count that changes when the emitters are off, so the
text differs between the two runs. It is a label artefact rather than a
control, and it is excluded by intersecting with the baseline.
