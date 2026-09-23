# rc2 §19's Unicode gate item

23 September 2026. `python scripts/unicode_gate.py` regenerates everything here.

rc2 §19 lists eight conditions the GSD pilot scope must satisfy before freeze.
Seven need a person. One is mechanically checkable, and it had not been checked:

```text
Unicode 15.0.0 behavior required by this contract is demonstrated in the
execution environment
```

§1.1 pins it alongside `spec_version` and `citation_rule_version`, in the
rule-identity block. It is part of what makes two runs comparable.

---

## What was found

```text
python           3.10.12
unicodedata      13.0.0
rc2 §1.1 pins    15.0.0
platform         linux
```

The environment carries Unicode 13.0.0. A Python build holds one Unicode
database, fixed at compile time and not selectable at runtime, so this is a
property of the interpreter rather than something the extractor can set.

**This measurement is of the Linux environment the analysis runs in. It is not
necessarily the environment the extractor runs in on another machine, and the
script reports its platform for exactly that reason. Running it elsewhere is
one command and the answer may differ.**

---

## Whether the difference is observable

It is, on two rules rc2 states.

```text
code point   assigned  isalpha  name
U+10780      NO        False    LATIN SMALL LETTER MODIFIER CAPITAL L (14.0)
U+1DF00      NO        False    LATIN SMALL LETTER FENG DIGRAPH (14.0)
U+00870      NO        False    ARABIC LETTER ALEF WITH ATTACHED FATHA (14.0)
U+1E030      NO        False    MODIFIER LETTER CYRILLIC SMALL A (15.0)
```

All four are letters under Unicode 15.0.0. Under 13.0.0 they are unassigned,
so:

```text
§7    "it contains at least one Unicode letter"   would answer NO where
                                                  15.0.0 answers YES
§1.4  lower(x), Unicode simple lowercase          identity where 15.0.0
                                                  may case-fold
```

One thing this does NOT reach: §1.3's three code-point counts — the osa unit,
CORE's floor of 2, and the 1500 overlong threshold. Counting code points does
not consult the tables, so those are identical under any version.

---

## Whether it reaches this contract

```text
corpus                                 1,367,617 code points
characters unassigned under 13.0.0     NONE
```

Not one character added in Unicode 14.0 or 15.0 appears anywhere in the
thirteen papers.

And NFC is fixed regardless, by Unicode's Normalization Stability Policy: a
string whose characters are all assigned in version X normalises identically in
every version from X onward. Every corpus character is assigned in 13.0.0 or
earlier, so §2's `canonical_manuscript_bytes` are the same bytes under 13.0.0
and 15.0.0 for this corpus. That is the property the whole byte-offset contract
rests on, and it is the one that survives the version gap intact.

---

## What this is, and what it is not

It is a **demonstration**, which is the word §19 uses. It is not a claim that
the item is met.

```text
the environment does not match the pin          established
the difference is observable on rc2's rules     established, four characters
it reaches any character in this corpus         NO
§2's canonical bytes differ for this corpus     NO, by the stability policy
```

Whether a bounded gap satisfies the gate is a freeze-review decision. What can
be said without one: nothing in the current corpus is processed differently
than Unicode 15.0.0 would process it, and the first manuscript containing a
character added in 14.0 or 15.0 would be.

Two ways to close it properly if the review wants it closed rather than
bounded:

```text
run on a Python whose unicodedata is 15.0.0      a newer interpreter carries a
                                                 newer database; check
                                                 unicodedata.unidata_version on
                                                 the candidate build rather
                                                 than assuming a version map
vendor the tables                                a package that ships its own
                                                 Unicode data, independent of
                                                 the interpreter build
```

Either makes the gate item a match rather than an argument. Neither is a
decision this file takes.

One note on the first: which Python release carries which Unicode version is
not something this environment can establish about another one, so it is left
as a thing to check rather than stated. `scripts/unicode_gate.py` prints the
answer wherever it is run, which is the point of it reporting its platform.
