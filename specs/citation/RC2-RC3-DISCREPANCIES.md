# Where rc3 and rc2 disagree, and how each was resolved

Opened 21 September 2026, the day rc2 arrived. Alex Zamurko's consolidation
brief asks for exactly this:

> Where the evidence permits more than one reconstruction, identify the
> ambiguity and resolve it explicitly rather than silently selecting one.

Six so far. Every one was found by **implementing** the rule rather than by
reading it, which is worth saying plainly: five of the six look fine on the
page and only fail when run. Each entry records what was chosen and why, so the
consolidation can overturn it knowingly rather than inherit it by accident.

---

## 1. rc3 says rc2's production carries a maximum label length. It does not.

rc3 §B1b, forbidding the citation side from inventing its own grammar:

> rc2's production already carries the bound, the terminal-period handling and
> the maximum label length.

rc2 §7.4 carries two of the three. The head is bounded by the entry start and
the parenthesis holding the first YEAR, and one trailing period is removed.
There is **no maximum label length anywhere in rc2**.

```text
chosen    no length bound implemented
because   a constant that governs what counts as an author label has to come
          from the specification, not from whoever is typing. Inventing one
          here would be the second definition rc3 B1b exists to prevent.
risk      an unbounded label means a malformed entry could produce a very long
          non-person key. Nothing in the corpus does.
```

---

## 2. rc3 counts FAO among the institutional cases. rc2 cannot reach it.

rc3's §I puts institutional authors at 8, and the Slack adjudication of 29
August moved `(FAO, 2018)` and `(FAO, 2005)` into that class from all-caps.

Both occur in `c1d56945` as:

```text
FAO, 2005. Building on Gender, Agrobiodiversity and Local Knowledge.
FAO, 2018. The 10 Elements of Agroecology.
```

There is no year parenthesis, so rc2 §7.4 produces no `reference_author_head`
at all; and if it did, the head would contain a comma, which §7.4 refuses:

> A comma-containing organization author that cannot be distinguished from an
> unsupported person-list form is therefore unresolved rather than guessed.

```text
chosen    FAO stays unresolved
because   rc2 states the refusal and its reason. The two are indistinguishable
          from a `Smith, J.`-shaped person list at the comma, and rc2 prefers
          unresolved to guessed.
consequence  rc3's institutional 8 is not reachable under rc2's own production.
             4 of the 8 are recovered; FAO is 2 of the remainder.
```

---

## 3. rc2 §7.4's period rule defeats rc2's own person path.

The sharpest of the six, and invisible on the page.

```text
§7.4   reference_author_head is the trimmed text before the opening "(" ...
       with one trailing period removed
§2     INITIALS = \p{Lu}\.(?:[- ]?\p{Lu}\.)*
§7.4   A person list is one or more units:  SURNAME, WS INITIALS
```

For `Bartko, J. (1976).` the head is `Bartko, J.` and the rule removes the
period, giving `Bartko, J` — which no longer satisfies INITIALS. Applied
literally, **no person reference can ever parse**, and every one falls through
to the non-person branch.

Measured: 1 of 1036 corpus references produced an author list.

§7.4 also requires the list to consume the head "after ordinary separator
punctuation normalization", a phrase defined nowhere. That may be where the
original resolved this.

```text
chosen    the trailing period is removed only when it is not an initial
because   it preserves the case the rule exists for — `World Bank.` still
          loses its period — without defeating the primary path. 683 of 1036
          references now yield an author list.
for the consolidation   either state the exception, or define "ordinary
                        separator punctuation normalization".
```

---

## 4. rc2 §6.8 strips the possessive on one side only.

§6.8:

> Only when deriving a **person identity candidate surname**, strip one
> trailing ASCII `'s` or typographic `’s`.

`visible_authors` is defined in §6.7 as "ordered normalized surnames" and is
not named in §6.8. Read literally the possessive stays attached, so
`Tepper's (2000)` yields `["tepper's"]` and is compared against a reference
`['tepper']`.

That comparison can never pass. Measured: nine false mismatches, every one of
that exact shape, out of twenty-two.

```text
chosen    the possessive is stripped from visible_authors too
because   these ARE surnames used for identity comparison, which is §6.8's own
          scope, and rc2 is explicit elsewhere that a false mismatch is worse
          than no check because it teaches a reviewer to ignore the field.
          22 mismatches became 8.
for the consolidation   name visible_authors in §6.8, or say why it is excluded.
```

---

## 5. rc2 §9.3 specifies a rule v3.3's grammar cannot express.

§9.3:

> The et_al rule compares every visible author, not only the first, so
> `Smith, Jones, et al. (2020)` is checked on both.

That form does not parse. v3.3 §4's `AUTHORS_PAREN` admits `SURNAME WS et WS
al.` or a surname list, not a list followed by `et al.`. rc2 §2's grammar is
the same shape.

```text
chosen    the property is pinned where it is reachable — the phrase carries
          every visible author — and the end-to-end case is not asserted
because   a conformance case built on input the grammar cannot produce tests
          nothing, and would report green for a rule never exercised.
for the consolidation   either the grammar admits the form, or §9.3's example
                        should not use it.
```

---

## 6. rc3 D2 unwraps into a form the grammar refuses, and forbids fixing it.

D2 is normative in rc3 §J, unimplemented, and counted in §I as **+3**.

```text
MATCH    $ ( YEAR_LIST ) $
         where YEAR_LIST satisfies the citation year-list grammar IN FULL
ACTION   strip the enclosing $ delimiters. NOTHING INSIDE IS ALTERED.
```

Implemented exactly, it finds every corpus case and strips the delimiters
correctly. What it hands the parser is:

```text
Baron (2012,2016)
```

which does not parse, because the year-list production requires whitespace
after the comma:

```text
v3.3 §4    CITE_NARR = AUTHORS_NARR WS \( WS? YEAR (?:, WS YEAR)* ... \)
rc2 §6.2   prose only — "one or more YEAR_TOKEN values", separator
           unspecified
```

So D2's two clauses cannot both hold. The contents do **not** satisfy the
year-list grammar, and D2 forbids altering them.

```text
chosen    implemented faithfully, and left worth 0
because   widening `(?:, WS YEAR)*` would change every citation in the corpus
          rather than the eight D2 touches, on the strength of a clause rc3
          does not contain. A transform that recovers nothing is a finding;
          a grammar quietly widened to make §I's number appear is not.
for the consolidation   either the year-list production drops the required
                        whitespace, or D2's ACTION allows normalising the
                        separator, or D2 is worth 0 and §I's +3 comes off.
```

Pinned as a conformance control, so if the production is ever widened the
suite says so instead of a corpus figure moving quietly.

---

## A measurement note, not a discrepancy: "worth" counts occurrences

rc3 B6 is "Worth 2". Implemented, it recovers **4 occurrences and 0 works**.

Both corpus cases are `Sharma et al., 2019a,b` in `ad1e3ff9`, which is gold
paper 1. Both `sharma|2019a` and `sharma|2019b` are in the gold set, and both
were already being found — the paper writes each out in full elsewhere. So the
compact form adds occurrences of works already matched.

```text
corpus parsed   2098 -> 2102    +4 occurrences
gold recall     0.980 -> 0.980   unchanged
```

Neither figure is wrong. rc3's residual counts occurrences and the gold sets
score distinct works, so an amendment can be worth its stated number and move
recall by nothing. Worth stating before the consolidation puts the two columns
side by side and someone reconciles them.

---

## What these have in common

None was visible from reading. Each was found by running the rule against
fourteen papers and looking at what came out:

```text
1  found by implementing B1b and having nothing to implement
2  found by FAO not appearing in the results
3  found by the check reporting ZERO mismatches, which was too clean
4  found by nine mismatches all sharing one shape
5  found by a conformance case producing an unresolved citation
6  found by a transform working perfectly and recovering nothing
```

Number 3 is the one to dwell on. A check that finds nothing looks like a check
that found nothing wrong. It was actually a check that could not run, and the
only reason it surfaced is that zero was treated as suspicious rather than as
good news.
