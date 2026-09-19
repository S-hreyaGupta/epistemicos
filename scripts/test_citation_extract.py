#!/usr/bin/env python3
"""Conformance controls for the v3.3 citation extractor.

    python scripts/test_citation_extract.py

Exit 0 = every control fired.

The cases are the specification's own. §12 of `citation-spec` lists what a
conformance suite must cover and states the expected output for most of it —
`World Bank (2024)` must NOT become `bank|2024`, `In May (2020)` must carry text
exactly `May (2020)`, `(Smith, 1500)` parses while `(Smith, 1499)` is invisible.
Those are not tests anyone invented here; they are the spec being read back to
the implementation.

That matters for what this suite can establish. Passing does not mean the
extractor is right. It means it agrees with the document it was written from on
the cases that document chose to pin, which is narrower and is the honest claim.

Two sections are not from §12. `author_phrase carries the whole production` and
the six-token cap control were added after `mutate_citation_suite.py` showed the
suite passing on an implementation with each rule broken. §12 states its
expectations as citation keys, so nothing in it constrained `author_phrase` —
the field whose truncation made the August refusal survey report two hits as
misses. A suite faithful to the spec was blind to the defect that actually
occurred, which is worth knowing about conformance suites generally: they
inherit the spec's blind spots, including about fields its consumers depend on.

Run `mutate_citation_suite.py` after changing this file. A control that cannot
fail is not evidence, and this suite has already contained two of them.

Not in `refresh_counts.SUITES`: `citation_extract.py` is not in the review
target and is not reached through `bootstrap_gate.covered()`.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

import citation_extract as ce  # noqa: E402

HEAD = "# Paper\n\n## Introduction\n\n"
REFS = "\n\n## References\n\nSmith, J. (2020). A paper. Journal, 1(1), 1-10.\n"


def extract(body_text: str, fixes=frozenset()):
    """Run the real pipeline over a minimal document containing body_text."""
    doc = HEAD + body_text + REFS
    text = ce.normalise(doc.encode("utf-8"))
    body, section, off, heads = ce.split_body_and_references(text)
    if "ampersand" in fixes:
        body = body.replace("\\&", "&")
    sents = ce.sentences(body)
    return ce.extract_citations(body, sents, heads, set(fixes))


def keys(cits):
    return [c["citation_key"] for c in cits]


def main() -> int:
    failures: list[str] = []

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    def case(label: str, body: str, want_keys=None, want_unres=None,
             want_text=None, want_authors=None, fixes=frozenset()):
        cits, unres = extract(body, fixes)
        got = keys(cits)
        if want_keys is not None and got != want_keys:
            failures.append(f"{label}\n      body {body!r}\n"
                            f"      got keys {got}\n      want    {want_keys}")
            return
        if want_authors is not None:
            phrases = [c["author_phrase"] for c in cits]
            if phrases != want_authors:
                failures.append(f"{label}\n      body {body!r}\n"
                                f"      got author_phrase {phrases}\n"
                                f"      want              {want_authors}")
                return
        if want_unres is not None:
            reasons = [u["reason"] for u in unres]
            if reasons != want_unres:
                failures.append(f"{label}\n      body {body!r}\n"
                                f"      got reasons {reasons}\n"
                                f"      want        {want_unres}")
                return
        if want_text is not None:
            texts = [u["text"] for u in unres]
            if want_text not in texts:
                failures.append(f"{label}\n      body {body!r}\n"
                                f"      unresolved text {texts}\n"
                                f"      want to contain {want_text!r}")
                return
        ok(label)

    print("citation extractor — §12 conformance")

    # ---- parenthetical, §12 row 3 ----
    print("\nparenthetical")
    case("one author", "Work follows (Smith, 2020).", ["smith|2020"])
    case("two authors with &", "Work follows (Ahnert & Fink, 2008).",
         ["ahnert|2008"])
    case("et al.", "Work follows (Smith et al., 2020).", ["smith|2020"])
    case("multi-segment, one occurrence each",
         "Work follows (Ahnert & Fink, 2008; Bartko, 1976).",
         ["ahnert|2008", "bartko|1976"])
    case("multi-year, one occurrence per year",
         "Work follows (Smith, 2020, 2021).", ["smith|2020", "smith|2021"])
    case("prefix e.g.", "Work follows (e.g., Smith, 2020).", ["smith|2020"])
    case("locator p. 14", "Work follows (Smith, 2020, p. 14).", ["smith|2020"])

    # ---- narrative, §12 row 4 ----
    print("\nnarrative")
    case("one author", "Smith (2020) argues this.", ["smith|2020"])
    case("and-terminated serial list",
         "Smith, Jones, and Brown (2020) argue this.", ["smith|2020"])
    case("et al.", "Smith et al. (2020) argue this.", ["smith|2020"])
    # §12 names this one explicitly, particles included in the key.
    case("particle surname", "van der Maas (2022) argues this.",
         ["van der maas|2022"])
    # And the same name where a sentence puts it, which §12 does not name and
    # the implementation did not handle: §4 says particles are "compared via
    # lower()", and the alternation was case-sensitive. Testing only the
    # spelling the spec happened to write is how that survived.
    case("the same particle surname, sentence-initial",
         "Van der Maas (2022) argues this.", ["van der maas|2022"])
    case("capitalised particle, parenthetical",
         "As shown (Da Silva et al., 2020).", ["da silva|2020"])
    case("two capitalised particles",
         "As shown (De La Cruz and Dessein, 2021).", ["de la cruz|2021"])
    case("capitalised particle after a conjunction",
         "As shown (Enthoven and Van den Broeck, 2023).", ["enthoven|2023"])
    # The limit of the rule, so the fix is not read as wider than it is.
    # SURNAME is (PARTICLE WS)* CORE — particles lead. A particle *inside* a
    # surname is outside the grammar as specified, and stays unresolved.
    case("a particle inside the surname is still out of grammar",
         "As shown (Oliveira da Silva et al., 2024).", [],
         want_unres=["no_grammar_match"])
    # CORE requires an upper-case initial, so this stays out too. It is a
    # source typo rather than a name form.
    case("a lower-case core is not a surname",
         "As shown (Da silva et al., 2017).", [],
         want_unres=["no_grammar_match"])

    # ---- adversarial narrative, §12 row 6 ----
    # The discard constraint: a STOP word before the author is dropped and the
    # citation parses; the group starts at the author, not the stop word.
    print("\nadversarial narrative")
    for lead in ("However,", "In", "See", "Unlike", "Curiously,"):
        case(f"{lead} Smith (2020) parses as smith|2020",
             f"Text here. {lead} Smith (2020) argues this.", ["smith|2020"])
    case("Following (2019) is a stopword surname",
         "Text here. Following (2019) we did this.", [],
         want_unres=["stopword_surname"])

    # ---- institutional, §12 row 7. The row this suite exists for. ----
    print("\ninstitutional")
    case("World Bank (2024) does NOT degrade to bank|2024",
         "Reported by World Bank (2024) in that year.", [],
         want_unres=["no_grammar_match"])
    case("European Commission (2023) stays whole and unresolved",
         "Reported by European Commission (2023) in that year.", [],
         want_unres=["no_grammar_match"])
    case("OECD (2024) is all_caps_surname", "Reported by OECD (2024) here.",
         [], want_unres=["all_caps_surname"])
    case("(OECD, 2024) is all_caps_surname too",
         "Reported here (OECD, 2024).", [], want_unres=["all_caps_surname"])

    # ---- historical and envelope, §12 row 5 ----
    print("\nhistorical range and envelope")
    case("Darwin 1859 keys, not no_year", "As shown (Darwin, 1859).",
         ["darwin|1859"])
    case("Machiavelli 1532 parses", "As shown (Machiavelli, 1532).",
         ["machiavelli|1532"])
    # The envelope boundary, both sides. 1500 is a YEAR; 1499 is not, so the
    # span is not even a candidate and produces no record of any kind.
    case("1500 is inside the envelope", "As shown (Smith, 1500).",
         ["smith|1500"])
    case("1499 is invisible, not unresolved", "As shown (Smith, 1499).",
         [], want_unres=[])
    case("forename-first is unresolved, not a citation",
         "As shown (Adam Smith, 1776).", [], want_unres=["no_grammar_match"])
    case("dual date is unresolved", "As shown (Marx, 1867/1990).",
         [], want_unres=["no_grammar_match"])
    case("square brackets produce no record at all",
         "As shown [Smith, 2020].", [], want_unres=[])

    # ---- unresolved spans, §12 row 11 ----
    # Which span a rejection reports is specified and differs by reason: a
    # post-parse rejection reports the accepted parse, a grammar failure
    # reports the whole candidate.
    print("\nrejection spans")
    case("In May (2020): text is the accepted parse, not the candidate",
         "Text here. In May (2020) we did this.", [],
         want_unres=["stopword_surname"], want_text="May (2020)")

    # ---- author_phrase, which §12 does not pin ----
    #
    # Added after a mutation probe, not from the spec. §12 states its expected
    # outputs as citation keys, so every case above passes unchanged when
    # author_phrase is cut at the first comma — the key is built from the first
    # surname either way. That cut is not hypothetical: it is the defect that
    # made the August refusal survey report two hits as misses, because the
    # matcher compared author phrases and the extractor had truncated them.
    #
    # So the suite was faithful to the spec and still blind to the bug that
    # actually happened, because the field that broke was one the spec never
    # stated an expectation for. These controls pin it.
    print("\nauthor_phrase carries the whole production")
    case("comma-separated authors are not cut at the first comma",
         "Work follows (Duru, Therond, and Fares, 2015).",
         ["duru|2015"], want_authors=["Duru, Therond, and Fares"])
    case("two comma-separated authors survive whole",
         "Work follows (Smith, Jones, 2015).",
         ["smith|2015"], want_authors=["Smith, Jones"])
    case("ampersand pairs keep both names",
         "Work follows (Ahnert & Fink, 2008).",
         ["ahnert|2008"], want_authors=["Ahnert & Fink"])
    case("et al. stays attached",
         "Work follows (Smith et al., 2020).",
         ["smith|2020"], want_authors=["Smith et al."])
    case("narrative serial list keeps every author",
         "Smith, Jones, and Brown (2020) argue this.",
         ["smith|2020"], want_authors=["Smith, Jones, and Brown"])

    # ---- C2 boundary, §12 row 8 ----
    print("\nC2 sentence boundary")
    case("a previous sentence's last token cannot enter the run",
         "Data came from the USA. Smith (2020) argues this.", ["smith|2020"])
    # Also added after the probe. The case above passes with the six-token cap
    # removed entirely, because the sentence start stops the walk first — it was
    # testing the sentence bound and reporting the cap. The cap is observable
    # only in how far back a rejected span reaches, so that is what to assert:
    # six eligible tokens precede the year here, and "Alpha" is the seventh.
    case("the run stops at six eligible tokens, not at the sentence start",
         "We used Alpha Beta Gamma Delta Epsilon Zeta Smith (2020) here.",
         [], want_unres=["no_grammar_match"],
         want_text="Beta Gamma Delta Epsilon Zeta Smith (2020)")

    # ---- unicode, §12 row 9 ----
    print("\nunicode")
    case("accented surnames key", "As shown (García, 2020; Müller, 2019).",
         ["garcía|2020", "müller|2019"])

    # ---- noise the spec accepts by design, §12 row 11 ----
    print("\ndeclared noise")
    case("bare year", "As shown (2019) it went up.", [],
         want_unres=["no_grammar_match"])
    case("comma-less", "As shown (Smith 2020).", [],
         want_unres=["no_grammar_match"])
    case("quantity parenthetical, admitted by the wider year range",
         "We surveyed (1850 participants) in total.", [],
         want_unres=["no_grammar_match"])

    # ---- aborts, §12 row 18 ----
    print("\naborts")
    for label, doc, code in (
        ("no references section", "# P\n\n## Intro\n\nSmith (2020).\n", 3),
        # §12 pins this as a boundary pair, and both sides matter: a document
        # whose sectioning really lives in h1 is refused rather than remapped,
        # while a stray second h1 alongside h2 structure is tolerated. Testing
        # only the abort would pass on an implementation that aborted on every
        # second h1 and threw away ordinary papers with a title and an
        # appendix heading.
        ("sectioning lives in h1: two h1, no h2",
         "# A\n\ntext\n\n# B\n\nmore\n", 4),
    ):
        try:
            ce.split_body_and_references(ce.normalise(doc.encode()))
            failures.append(f"{label}: expected abort {code}, none raised")
        except ce.Abort as a:
            if a.code != code:
                failures.append(f"{label}: aborted {a.code}, expected {code}")
            else:
                ok(f"exit {code}: {label}")

    try:
        ce.split_body_and_references(ce.normalise(
            b"# A\n\ntext\n\n# B\n\n## Intro\n\nSmith (2020).\n\n"
            b"## References\n\nSmith, J. (2020). A paper. Journal, 1(1), 1-10.\n"))
        ok("a stray second h1 alongside h2 structure is tolerated")
    except ce.Abort as a:
        failures.append(f"two h1 with an h2 present aborted {a.code}; §3.2 "
                        f"tolerates a stray extra h1 and only refuses when "
                        f"sectioning apparently lives in h1")

    # ---- §3, the unmarked-up label ----
    #
    # Four corpus papers aborted at exit 3 from August to 19 September with a
    # complete reference list present, because Mathpix wrote `References` as
    # plain text rather than a heading. Ruled by Alex Zamurko on 18 September:
    # the standalone line is the boundary when no marked-up heading exists,
    # with alphabetical ordering as confirmation only.
    print("\nan unmarked-up References label")

    ENTRIES = ("Adams, J. (2001). A paper. Journal, 1(1), 1-10.\n"
               "Baker, R. (2002). Another. Journal, 2(1), 1-10.\n"
               "Clark, S. (2003). A third. Journal, 3(1), 1-10.\n"
               "Dunn, M. (2004). A fourth. Journal, 4(1), 1-10.\n"
               "Evans, T. (2005). A fifth. Journal, 5(1), 1-10.\n")

    def splits(doc: str):
        return ce.split_body_and_references(ce.normalise(doc.encode()))

    try:
        body, refs, _, _ = splits(
            "# P\n\n## Intro\n\nAs shown (Adams, 2001).\n\nReferences\n\n" + ENTRIES)
        if "Adams, J." not in refs:
            failures.append("the plain-text label was found but the section "
                            "below it did not come back as references")
        elif "References" in body:
            failures.append("the label was left in the body, so it would be "
                            "scanned for citations")
        else:
            ok("a standalone `References` line is a section boundary")
    except ce.Abort as a:
        failures.append(f"a plain-text References label with five ordered "
                        f"entries below it still aborted {a.code}")

    # The label alone cannot be enough, or any paragraph ending in the word
    # splits the paper.
    for label, doc in (
        ("nothing below it", "# P\n\n## Intro\n\nText.\n\nReferences\n"),
        # Three entries, in perfect alphabetical order, so the ordering check
        # passes and only the entry count can refuse this. The first version
        # used a single entry, which the ordering check rejects on its own —
        # so the control named for the count was being decided by the other
        # rule, and the mutation probe caught it immediately.
        ("too few entries below it",
         "# P\n\n## Intro\n\nText.\n\nReferences\n\n"
         "Adams, J. (2001). A paper. Journal, 1(1), 1-10.\n"
         "Baker, R. (2002). Another. Journal, 2(1), 1-10.\n"
         "Clark, S. (2003). A third. Journal, 3(1), 1-10.\n"),
        ("prose below it, not entries",
         "# P\n\n## Intro\n\nText.\n\nReferences\n\n"
         "were consulted throughout the study and are listed elsewhere.\n"),
    ):
        try:
            splits(doc)
            failures.append(f"a `References` line with {label} was accepted "
                            f"as a boundary; the confirmation check did not "
                            f"hold")
        except ce.Abort as a:
            if a.code != 3:
                failures.append(f"{label}: aborted {a.code}, expected 3")
            else:
                ok(f"refused: a `References` line with {label}")

    # Out of order is the confirmation the ruling names.
    try:
        splits("# P\n\n## Intro\n\nText.\n\nReferences\n\n"
               "Evans, T. (2005). A paper. Journal, 1(1), 1-10.\n"
               "Dunn, M. (2004). Another. Journal, 2(1), 1-10.\n"
               "Clark, S. (2003). A third. Journal, 3(1), 1-10.\n"
               "Baker, R. (2002). A fourth. Journal, 4(1), 1-10.\n"
               "Adams, J. (2001). A fifth. Journal, 5(1), 1-10.\n")
        failures.append("a reverse-alphabetical run was accepted; the "
                        "ordering confirmation did not hold")
    except ce.Abort as a:
        ok("refused: entries below the label are not in order") \
            if a.code == 3 else failures.append(
                f"reverse-alphabetical aborted {a.code}, expected 3")

    # A real heading still wins, so the fallback cannot change any paper that
    # already worked.
    try:
        body, refs, _, _ = splits(
            "# P\n\n## Intro\n\nReferences were consulted.\n\n"
            "## References\n\n" + ENTRIES)
        if "Adams, J." in refs and "were consulted" in body:
            ok("a marked-up heading still takes priority over a stray line")
        else:
            failures.append("the fallback displaced a real heading")
    except ce.Abort as a:
        failures.append(f"a document with a real heading aborted {a.code}")

    try:
        ce.normalise(b"\xff\xfe invalid")
        failures.append("invalid UTF-8 did not abort")
    except ce.Abort as a:
        ok("exit 5: invalid utf-8") if a.code == 5 else failures.append(
            f"invalid UTF-8 aborted {a.code}, expected 5")

    # ---- the four August corrections, each behind its flag ----
    print("\nthe four corrections, on and off")
    amp = "As shown (Ahnert \\& Fink, 2008)."
    case("escaped ampersand is invisible without the flag", amp, [],
         want_unres=["no_grammar_match"])
    case("and parses with it", amp, ["ahnert|2008"], fixes={"ampersand"})

    colon = "As shown (Kunda, 1990: 480) in that work."
    case("colon locator is unresolved without the flag", colon, [],
         want_unres=["no_grammar_match"])
    case("and parses with it", colon, ["kunda|1990"], fixes={"colon"})
    # The digit requirement is what separates a locator from a following
    # author, and it is the whole reason the rule is safe.
    case("colon flag does not swallow a following author",
         "As shown (Wezel, 2024: Wezel et al.) here.", [],
         want_unres=["no_grammar_match"], fixes={"colon"})

    case("cp. is not a cue without the flag",
         "As shown (cp. Liu et al., 2012) here.", [],
         want_unres=["no_grammar_match"])
    case("and is one with it", "As shown (cp. Liu et al., 2012) here.",
         ["liu|2012"], fixes={"cp"})

    # segments: one bad segment must not take the good ones with it.
    seg = "As shown (Smith, 2020; nonsense here; Jones, 2021) in that work."
    cits, unres = extract(seg)
    if keys(cits):
        failures.append("without the segments flag a damaged group still "
                        f"yielded {keys(cits)}; §6.2 is whole-span")
    else:
        ok("a damaged group loses everything without the segments flag")
    cits, unres = extract(seg, {"segments"})
    if keys(cits) != ["smith|2020", "jones|2021"]:
        failures.append(f"with the segments flag, expected both citations, "
                        f"got {keys(cits)}")
    elif [u["reason"] for u in unres] != ["no_grammar_match"]:
        failures.append(f"the bad segment should be reported alone, got "
                        f"{[u['reason'] for u in unres]}")
    else:
        ok("with it, the good segments survive and the bad one is reported")

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("  the extractor agrees with §12 on the cases it pins, and with the")
    print("  two rules §12 leaves unstated that a mutation probe found unheld")
    return 0


if __name__ == "__main__":
    sys.exit(main())
