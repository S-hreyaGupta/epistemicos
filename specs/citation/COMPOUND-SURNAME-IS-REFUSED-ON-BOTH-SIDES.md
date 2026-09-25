# A two-word personal surname parses on neither side

25 September 2026, found by the vacuity sweep's first completed empty run.

`Pircher Verdorfer` is a real author in this corpus, with a compound personal
surname and no particle. Measured against the current extractor:

```text
reference   Pircher Verdorfer, A. (2016). Mindfulness and leadership. J, 1, 1.
            -> UNRESOLVED, reason entry_start_grammar
            no reference_key, so no author_kind either

citation    (Pircher Verdorfer, 2016)
            -> UNRESOLVED, reason no_grammar_match
            no citation_key
```

Both refusals are silent in the sense that matters: the document produces
records saying something was missed, and nothing says the two are the same
author or that a person was lost.

## How it surfaced, which is the more useful half

A suite control named `a compound personal surname is not read as an
institution` asserted that no emitted `citation_key` starts with
`non_person|`. Its reasoning, from its own comment: this has the same shape as
`Population Pyramid, 2022`, two capitalised words and a year, and only the
bibliography can tell them apart.

That reasoning is sound and the premise is false. The bibliography cannot tell
them apart here because the entry never keys. And the assertion was written as
`any(... for c in cits)`, which is False over an empty list, so with no
citation emitted the control reported success about a key that does not exist.

It had done so since it was written, on the real extractor, not only under the
sweep. The sweep found it because emptying the emitters is the one condition
under which a vacuous control is indistinguishable from a sound one, and
looking at the survivors is what turns that into a finding.

## What this does and does not establish

It does not establish that the grammar is wrong. rc2 §7.4's head rule and
§7.1's entry-start rule are both closed lists, and a compound surname may have
been deliberately left out of them. That is a reading of the specification and
it has not been done.

It does establish that the corpus contains an author neither side can express,
and that the only control pointed at the case was reporting success without
looking. `author_structure_mismatch` cannot fire here either, because there is
no citation and no reference to compare.

## Where it is recorded

`scripts/test_citation_extract.py` now records the refusal rather than
asserting the absence of a wrong key. Three branches, so a change in either
direction fires:

```text
the citation starts parsing        -> FAIL, re-read this note first
the refusal reason changes         -> FAIL, naming the new reason
neither, still no_grammar_match    -> ok, recorded as a gap
```

That is deliberately not a green tick on correct behaviour. It is a tripwire on
behaviour nobody has ruled on.

## Open, for Alex Zamurko

Should `Pircher Verdorfer` parse, on either side or both? The three positions
are all defensible and the choice is not the implementing agent's:

```text
1  both grammars accept compound surnames
       recovers a real author, widens two closed lists

2  neither does, and the refusal is correct
       compound surnames are indistinguishable from institutional names
       without a comma, and rc2 §8 already says syntax must not decide that

3  the reference accepts it and the citation does not
       the bibliography is where authority lives under §8, so keying the
       entry would let §8 settle the citation without widening §7.4
```

Position 2 is the current behaviour and may well be the intended one. What is
not defensible is the state this note was written from: the behaviour
unexamined, and the only control over it passing because it had nothing to
read.
