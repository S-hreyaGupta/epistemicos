# Ruling: which compound surnames the grammar supports

Two messages, six hours apart. The second refines the first and is the one that
governs; the first is kept because the second is written as an amendment to it
and reads oddly without it.

## The ruling as first given

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

---

# The refinement, 6 October 2026, 12:11 AM

Alex Zamurko, in workflow, answering the two open points above and adding a
third mechanism. Quoted in full for the same reason as before:

    Agreed. Please proceed with the deterministic boundary, with one refinement
    to preserve recall without reintroducing guessing.

    The citation grammar should directly support compound surnames when their
    structure is explicit in the citation string: hyphenated forms,
    apostrophised forms, and multi-word surnames containing a defined surname
    particle. Capitalisation alone should not be sufficient to confirm a
    compound surname.

    For the particle allow-list, a conservative v1 can include:

    "de, da, do, dos, das, del, della, di, du, des, la, le, van, von, der, den,
    ter, ten, el, al, bin, ibn"

    and recognised sequences such as:

    "de la, de las, de los, van der, van den, von der"

    "El" should therefore be added for El Akremi. The current behaviour that
    returns only "Akremi" should be treated as a defect because it silently
    truncates the cited surname rather than preserving uncertainty.

    For bare two-token forms such as Pircher Verdorfer, the parser may capture
    the two words as a candidate, but should not confirm them as a compound
    surname from capitalisation alone. The corresponding reference-list entry
    should confirm the author identity and surname boundary. If it cannot, the
    case remains unresolved. This means Pircher Verdorfer is unresolved under
    the current direct grammar, but not necessarily permanently.

    A small exclusion list should also prevent obvious surrounding prose from
    being absorbed into the candidate. A conservative v1 could include:

    "in, by, from, of, for, with, without, as, at, on, to, via, see, cf,
    compare, following, according, unlike, contra, versus, vs, the, a, an, and,
    or, but"

    The exclusion should be case-insensitive, so In Smith (2020) cannot become
    "In Smith".

    The resulting rule is:

    explicit surname structure → accept directly;
    excluded contextual token → do not absorb;
    bare two-capitalised-token form → candidate only, requiring reference-list
    confirmation;
    no deterministic confirmation → unresolved.

    This also handles the earlier failure mode: World Bank (2024) should not be
    treated as a personal compound surname merely because both words are
    capitalised. Identity/type confirmation is still required.

And answering the two questions put to him, 6 October 2026, 12:46 AM:

    Additive, not replacement. Keep all currently validated surname particles,
    including "zu" and "zur", and add the new particles to that existing list.

    For "al", add a specific safeguard for "et al.". "al" should remain a valid
    surname particle, but when it appears as part of "et al.", it must be
    treated as the citation abbreviation and never as part of a surname.

    For ambiguous two-word names such as "Pircher Verdorfer", keep
    reference-list confirmation as a separate recovery step. Do not broaden the
    direct surname grammar to accept any two capitalised words automatically.

## What this changes against the first ruling

The first ruling left `Pircher Verdorfer` unresolved permanently. It is now
unresolved *pending a recovery step*, which is a better outcome and a different
one: the recall is deferred rather than given up.

The particle set is no longer ours to choose. It is his list, added to the one
already in use, and `el` is his decision rather than mine. The paragraph above
recording that addition as the implementing agent's is superseded.

## Deferred, by his instruction of 6 October

**Reference-list confirmation of bare two-token candidates is future work.**
Alex Zamurko, in writing, the same morning: "Let's keep the reference list
confirmation as a future work. So, we can continue with other parts."

Until it exists, a bare two-capitalised-token form has no deterministic
confirmation available, so by the last line of his own rule it remains
unresolved. That is the same observable behaviour as today, reached by a
different route, and the difference matters: today it is unresolved because
nothing looks, and under this ruling it is unresolved because the thing that
would look has not been built yet.

## What is being built now

    1. the particle set, additive: the current set plus his, el included
    2. the multi-word sequences, de la / de las / de los / van der / van den /
       von der
    3. a second core in a surname ONLY where a particle joins it
    4. the contextual exclusion list, case-insensitive
    5. the et al. safeguard, with a control of its own
    6. bare two-token forms: unresolved, pending the deferred recovery step

Not being built: anything that confirms a compound surname from capitalisation,
and anything that reads the reference list to do it.
