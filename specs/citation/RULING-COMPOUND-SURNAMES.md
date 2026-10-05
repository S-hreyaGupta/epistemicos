# Ruling: which compound surnames the grammar supports

Alex Zamurko, 5 October 2026, in workflow. Quoted in full, because the rule is
the words rather than my reading of them:

    The citation grammar should support compound surnames when their structure
    is explicit in the citation string: hyphenated surnames, apostrophised
    surnames, and multi-word surnames containing a defined set of recognised
    surname particles. Support stops where identifying the surname would
    require inferring whether an adjacent word is part of the author's name
    rather than applying one of those explicit grammatical rules. Such cases
    should remain unresolved rather than being forced into a surname
    interpretation.

Asked for on 28 September as the outstanding item on compound surnames, with
`El Akremi`, `Pircher Verdorfer`, `Carrieri de Souza` and `Oliveira da Silva`
named as the structures in question.

## What it decides

Supported, because the string says so:

    hyphenated          Pircher-Verdorfer      the hyphen is the structure
    apostrophised       O'Brien, D'Angelo      the apostrophe is the structure
    particle-joined     Carrieri de Souza      the particle is the structure
                        Oliveira da Silva
                        van der Maas           leading particles, already in

Not supported, and left unresolved rather than guessed:

    two bare cores      Pircher Verdorfer      nothing in the string says the
                                               first word is part of the name

## Why this unblocks rc3 B1a

B1a proposed `(PARTICLE WS)* CORE (WS (PARTICLE WS)? CORE)?`. It was
implemented on 21 September and reverted the same day, for a reason recorded
in `citation_extract.py` above `CORE_AFTER_PARTICLE`: the OPTIONAL bare second
core lets a surname reach backwards into the sentence.

    In Smith (2020)            -> in smith|2020        §12: STOP discarded
    Following Bartko's (1976)  -> following bartko|1976
    World Bank (2024)          -> world bank|2024      §12: must NOT degrade
    (Adam Smith, 1776)         -> adam smith|1776      §12: forename-first
                                                       is unresolved

The note concluded that B1a needs rc2 or v3.4's two-pass split, because in a
single pass nothing downstream catches these.

This ruling removes the bare second core. What remains is a second core only
where a particle introduces it, and a particle cannot appear by accident in
front of a citation: `In`, `Following`, `World` and `Adam` are not particles.
So the four cases above stay safe in a single pass, and the narrower form can
be implemented now rather than waiting on the architecture.

    SURNAME = (PARTICLE WS)* CORE (WS PARTICLE WS CORE)*

## What the ruling leaves to us, and what that costs

**The particle set is not defined by the ruling.** It says "a defined set of
recognised surname particles" and leaves the membership open. The current set
in `citation_extract.py` is de, del, della, der, den, di, da, dos, du, la, le,
van, von, ter, ten, zu, zur. `El Akremi` is one of the four names the ruling
was asked about and `el` is not in that set, so supporting it means adding it.

That addition is the implementing agent's decision, not Alex Zamurko's, and is
recorded as such here so a later reader does not find it wearing his authority.
It goes to the next independent review with the rest.

Today `El Akremi (2018)` keys as `akremi`: the grammar matches from the second
word and the `El` is dropped silently. A truncated surname that nothing reports
is the failure mode this ruling exists to prevent, so the status quo is not a
neutral place to stand.

**The ruling costs recall, deliberately.** `Pircher Verdorfer` and every form
like it stay unresolved permanently. The full B1a was measured at +0.011 recall
on gold paper 1 and +0.040 on paper 2; the narrower form will be less, and the
difference is the price of never guessing. That trade is Alex Zamurko's to make
and he made it knowing the number.

## Consequences for existing controls

One control inverts, by this ruling rather than quietly:

    test_citation_extract.py
      "a particle inside the surname is still out of grammar"
      asserts `Oliveira da Silva et al.` stays unresolved

It becomes a supported form. The control is rewritten to assert the new
boundary, `Pircher Verdorfer`, rather than deleted: a boundary with no control
is where this one came from.
