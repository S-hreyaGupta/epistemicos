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

import re
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
    return ce.extract_citations(body, sents, heads, set(fixes))[:3]


def keys(cits):
    return [c["citation_key"] for c in cits]


def main() -> int:
    failures: list[str] = []

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    def case(label: str, body: str, want_keys=None, want_unres=None,
             want_text=None, want_authors=None, fixes=frozenset()):
        cits, unres, _excl = extract(body, fixes)
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
    # rc3 B2: a lower-case core is admitted, but ONLY immediately after a
    # matched particle. `Da silva` is a name; `smith` on its own is not, and
    # relaxing CORE generally would admit ordinary prose into the candidate
    # run. This control pinned the pre-B2 refusal and now pins the rule.
    case("a lower-case core after a particle is a surname",
         "As shown (Da silva et al., 2017).", ["da silva|2017"])
    case("a lower-case core without a particle is not",
         "As shown (smith, 2020).", [], want_unres=["no_grammar_match"])

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
    # ---- EC-2, the possessive ----
    #
    # `Bartko's (1976)` and `Bartko (1976)` are one work. Carrying the `'s`
    # into the derived identity split it in two and cost twice per work: a
    # miss against the gold set's `bartko`, and a false positive for
    # `bartko's`. Six of gold paper 1's nine discrepancies were three works
    # counted that way, and repairing it took the paper over both acceptance
    # thresholds. Ruled by Alex Zamurko on 18 September as an extractor error
    # rather than an annotation one.
    print("\nthe possessive is not part of the identity")
    case("a possessive surname keys to the bare name",
         "Following Bartko's (1976) formula, we did this.", ["bartko|1976"])
    case("the bare form keys identically",
         "Following Bartko (1976) we did this.", ["bartko|1976"])
    case("a possessive on the last of several authors",
         "We follow McGraw and Wong's (1996) method.", ["mcgraw|1996"])
    # rc3 §A: author_phrase records the complete source phrase. The manuscript
    # wrote the possessive, so the record keeps it and only the identity moves.
    case("author_phrase keeps what the manuscript wrote",
         "Following Bartko's (1976) formula, we did this.",
         ["bartko|1976"], want_authors=["Bartko's"])
    # A possessive inside a name is not a trailing one.
    case("a name is not truncated at an internal apostrophe",
         "As shown (O'Brien, 2020).", ["o'brien|2020"])

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
    # rc3 B1 removes the six-token cap this used to pin:
    #
    #     Do not reintroduce a token cap. C2 removed the six-token cap for a
    #     reason and the corpus still contains the case that removed it:
    #     Van den Brink and Van der Woerd, 7 tokens, present twice.
    #
    # The cap produced EC-3 — four works attributed to the wrong author,
    # silently, because the run began partway through the author list. So the
    # control inverts: a run longer than six is reached in full, and what
    # bounds it is eligibility and the sentence start rather than a count.
    case("a seven-token author list is reached in full",
         "In that context, Van den Brink and Van der Woerd (2004) show this.",
         ["van den brink|2004"])
    case("the run still stops at an ineligible token",
         "We used Alpha Beta Gamma Delta Epsilon Zeta Smith (2020) here.",
         [], want_unres=["no_grammar_match"],
         want_text="Alpha Beta Gamma Delta Epsilon Zeta Smith (2020)")
    case("and still never crosses the sentence start",
         "Data came from the USA. Smith (2020) argues this.", ["smith|2020"])

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

    # ---- rc3 B7, `and colleagues` ----
    print("\nrc3 B7: and colleagues")
    for n in ("Jost", "Colquitt", "Dalal"):
        case(f"{n} and colleagues, narrative",
             f"{n} and colleagues (2012) argue this.", [f"{n.lower()}|2012"])
    case("parenthetical form", "As shown (Smith and colleagues, 2020).",
         ["smith|2020"])
    # Closed, so it must not generalise to "and <noun>" — that would make a
    # real two-author pair ambiguous.
    case("a real two-author pair is unaffected",
         "Smith and Jones (2020) argue this.", ["smith|2020"],
         want_authors=["Smith and Jones"])
    case("the word alone is not a cue",
         "We thanked colleagues (2020) for help.", [],
         want_unres=["no_grammar_match"])

    # ---- rc3 B8, the possessive gap ----
    print("\nrc3 B8: possessive with a bounded gap")
    case("simple possessive, which rc2 already covered",
         "We follow Fine's (1998) here.", ["fine|1998"])
    case("et al.'s, no gap",
         "We follow Mackey et al.'s (2017) meta-analysis.", ["mackey|2017"])
    case("one intervening noun",
         "We follow Martinko et al.'s review (2013) here.", ["martinko|2013"])
    case("three intervening tokens, the measured maximum",
         "We follow Harter's definition of authenticity (2002) here.",
         ["harter|2002"])
    # The bound, and every terminator rc3 names.
    case("four intervening tokens is too many",
         "We follow Harter's very detailed definition of authenticity (2002).",
         [], want_unres=["no_grammar_match"])
    case("no possessive means no gap is allowed",
         "We follow Smith review (2020) here.", [],
         want_unres=["no_grammar_match"])
    case("the gap does not cross a comma",
         "We follow Harter's work, elsewhere (2002).", [],
         want_unres=["no_grammar_match"])

    # ---- rc3 B5, bounded lead-in cues ----
    print("\nrc3 B5: lead-in cues, a closed set")
    for cue in ("see", "see also", "see for example", "for an overview",
                "for a review", "for a recent review", "for a meta-analysis",
                "for a critique", "for critiques", "for a similar approach",
                "for comparative examples", "for details"):
        case(f"cue {cue!r}", f"Work follows ({cue}, Smith, 2020).",
             ["smith|2020"])
    case("the trailing form, where the cue follows the citation",
         "Work follows (see Smith, 2013, for a critique).", ["smith|2013"])
    # CLOSED is the safety argument: an open "for a <noun>" form would admit
    # ordinary prose ahead of any parenthetical year.
    case("a cue outside the set is not a cue",
         "Work follows (for a banana, Smith, 2020).", [],
         want_unres=["no_grammar_match"])
    case("the §4 prefix cues still work",
         "Work follows (e.g., Smith, 2020).", ["smith|2020"])

    # ---- §10 exit 2, the author-date style guard ----
    #
    # The existing exit-2 test looks for numeric and superscript citations.
    # c22df19f has neither and still scores 30.5%, because its style is
    # comma-less author-date throughout — which nothing detected. It was
    # classified out of profile in August by a person reading a report, and
    # that judgement has been quoted as a result ever since. Alex Zamurko
    # ruled on 18 September that it needs an implemented rule.
    print("\nauthor-date style guard")

    import tempfile as _tf

    def through_cli(body: str, fixes=frozenset({"ampersand"})):
        doc = (HEAD + body + "\n\n## References\n\n"
               "Smith, J. (2020). A paper. Journal, 1(1), 1-10.\n")
        p = Path(_tf.mkdtemp()) / "p.md"
        p.write_bytes(doc.encode("utf-8"))
        return ce.run(p, set(fixes))

    APA_12 = " ".join(f"Work follows (Smith{i}, 20{10+i})." for i in range(12))
    BARE_12 = " ".join(f"Work follows (Smith{i} 20{10+i})." for i in range(12))

    try:
        through_cli(APA_12)
        ok("an APA document passes the style guard")
    except ce.Abort as a:
        failures.append(f"an all-APA document aborted {a.code}; the guard "
                        f"fires on the style it exists to accept")

    try:
        through_cli(BARE_12)
        failures.append("a wholly comma-less author-date document was "
                        "accepted; the guard did not fire")
    except ce.Abort as a:
        if a.code != 2:
            failures.append(f"comma-less document aborted {a.code}, expected 2")
        else:
            ok("exit 2: a comma-less author-date document is refused")

    # A ratio over three parentheticals means nothing, so there is a floor.
    try:
        through_cli("Work follows (Smith 2010). And (Jones 2011).")
        ok("too few parentheticals to judge a style: not refused")
    except ce.Abort as a:
        failures.append(f"two comma-less parentheticals aborted {a.code}; "
                        f"the sample floor did not hold")

    # And the in-profile papers sit at 0-2%, so a couple of stray ones must
    # not trip it.
    try:
        through_cli(APA_12 + " Work follows (Odd 1999).")
        ok("a stray comma-less citation among APA ones does not trip it")
    except ce.Abort as a:
        failures.append(f"one comma-less citation among twelve APA ones "
                        f"aborted {a.code}")

    # Surnames of two characters or more, because CORE is `\p{Lu}NAMECHAR+`
    # and a one-letter name is not a surname. The first version of this
    # fixture used `(A, 2022)` and counted two of three.
    share, total = ce.comma_less_share(
        "(Smith, 2020) (Jones 2021) (Brown, 2022)")
    if total != 3 or abs(share - 1/3) > 1e-9:
        failures.append(f"comma_less_share counted {total} at {share:.2f}, "
                        f"expected 3 at 0.33")
    else:
        ok("comma_less_share counts both forms and reports the ratio")

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
    cits, unres, _excl = extract(seg)
    if keys(cits):
        failures.append("without the segments flag a damaged group still "
                        f"yielded {keys(cits)}; §6.2 is whole-span")
    else:
        ok("a damaged group loses everything without the segments flag")
    cits, unres, _excl = extract(seg, {"segments"})
    if keys(cits) != ["smith|2020", "jones|2021"]:
        failures.append(f"with the segments flag, expected both citations, "
                        f"got {keys(cits)}")
    elif [u["reason"] for u in unres] != ["no_grammar_match"]:
        failures.append(f"the bad segment should be reported alone, got "
                        f"{[u['reason'] for u in unres]}")
    else:
        ok("with it, the good segments survive and the bad one is reported")

    # ------------------------------------------------------ rc3 §A, §E, B10
    #
    # §G names six A-series conformance cases. All six are here; the two rc3
    # lists under `non_citation_year`, `leading_gloss` and `conversion_artifact`
    # are not, because no rule for them exists to test against — see
    # EXCLUSION-COVERAGE.md, which records the measurement behind that.

    print("\nrc3 §A output contract — three terminal states")

    def doc(body_text, head=HEAD, refs=REFS):
        """Run the whole pipeline and hand back the emitted record stream.

        References are assembled first and their non-person keys passed in,
        which is rc2 §8's ordering: authority comes from the bibliography, not
        from citation syntax.
        """
        text = ce.normalise((head + body_text + refs).encode("utf-8"))
        body, section, off, heads = ce.split_body_and_references(text)
        body = body.replace("\\&", "&")
        sents = ce.sentences(body)
        bib, _bib_unres = ce.assemble_references(section, off)
        npk = frozenset(r["reference_key"] for r in bib
                        if r.get("author_kind") == "non_person"
                        and r["reference_key"])
        return (body,) + ce.extract_citations(body, sents, heads,
                                              {"ampersand", "segments"}, npk)[:3]

    def excluded(body_text, head=HEAD):
        return doc(body_text, head)[3]

    # B10 / §G: "mathpix cdn URL → excluded_candidate/url_or_image". The years
    # are the image's pixel dimensions, which is why it is a candidate at all.
    url = ("![](https://cdn.mathpix.com/cropped/f7ae2f9b-69c3-4256-a0e5-"
           "7689118f0ca6-07.jpg?height=1895&width=1318&top_left_y=344)")
    x = excluded(url)
    if [r["excluded_reason"] for r in x] != ["url_or_image"]:
        failures.append(f"a mathpix image URL should be excluded as "
                        f"url_or_image, got {[r.get('excluded_reason') for r in x]}")
    else:
        ok("a mathpix cdn image URL is excluded_candidate/url_or_image")

    # The negative that makes the rule anchored rather than containment-based:
    # the span must BE a URL, not merely contain one.
    body, cits, unres, x = doc("As reported (Smith, 2020; https://example.org/"
                               "page) here.")
    if x:
        failures.append("a group that merely CONTAINS a URL was excluded; the "
                        "rule is anchored, not containment")
    elif keys(cits) != ["smith|2020"]:
        failures.append(f"(Smith, 2020; https://…) should still parse under "
                        f"segment splitting, got {keys(cits)}")
    else:
        ok("a citation beside a URL parses and is not url_or_image")

    # The same shape as it actually occurs in the corpus: `(BIS, 2014,
    # https://www.gov.uk/…)` in `2af68a7f`. An institutional author with the
    # source URL inside the group. It does not parse — rc3 B1b, blocked on rc2,
    # is what would recover it — and the control is that the URL does not turn a
    # known gap into a correct refusal. Excluding it would take a citation B1b's
    # recall is waiting for off A5's denominator, where it would stop being
    # counted as missing.
    #
    # The expectation here was written as `all_caps_surname` first, from the
    # rule that refuses `BIS`, and the extractor said `no_grammar_match`: the
    # trailing URL stops the whole group matching before the surname is ever
    # examined. Checked rather than predicted, which is the only reason the
    # fixture is right.
    body, cits, unres, x = doc("As reported (BIS, 2014, https://www.gov.uk/"
                               "government/organisations) here.")
    if x:
        failures.append(f"(BIS, 2014, https://…) is an unresolved institutional "
                        f"author, not a correct refusal; it was excluded as "
                        f"{[r['excluded_reason'] for r in x]}")
    elif [u["reason"] for u in unres] != ["no_grammar_match"]:
        failures.append(f"(BIS, 2014, https://…) should be an unresolved "
                        f"citation, got {[u['reason'] for u in unres]}")
    else:
        ok("an institutional author with a URL stays unresolved, not excluded")

    # §E, front matter. Structural: above the first h2. The span below is the
    # journal's own line, and six of the fourteen corpus papers carry one.
    front = ("# Paper\n\nTo cite this article: Jesús Labrador Fernández, "
             "Pedro César Martínez Morán & Gisela Delfino (2023) Lessons "
             "learned, Cogent Business & Management, 10:3.\n\n## Introduction"
             "\n\n")
    x = excluded("Ordinary text here.", head=front)
    if [r["excluded_reason"] for r in x] != ["publisher_metadata"]:
        failures.append(f"'To cite this article:' above the first h2 should be "
                        f"excluded_candidate/publisher_metadata, got "
                        f"{[r.get('excluded_reason') for r in x]}")
    else:
        ok("§E: a candidate above the first h2 is publisher_metadata")

    # §E, the other half, by section name this time.
    x = excluded("Text.\n\n## Citation information\n\nCite this article as: "
                 "Lessons learned, Cogent Business & Management (2023), 10.")
    if [r["excluded_reason"] for r in x] != ["publisher_metadata"]:
        failures.append(f"a candidate under `## Citation information` should be "
                        f"publisher_metadata, got "
                        f"{[r.get('excluded_reason') for r in x]}")
    else:
        ok("§E: a candidate under `## Citation information` is excluded")

    # The negative for the envelope: an ordinary section is still in it.
    body, cits, unres, x = doc("As shown (Smith, 2020) here.")
    if x:
        failures.append(f"an ordinary in-text citation was excluded: "
                        f"{[r['excluded_reason'] for r in x]}")
    else:
        ok("a citation under an ordinary heading is not excluded")

    # B10's named collision with D2. rc3: "Blanket math-span exclusion would
    # delete three real citations — Baron $(2012,2016)$ …". It must NOT be
    # excluded; it is a citation awaiting D2's unwrapping, and excluding it
    # would take a real citation off A5's denominator.
    body, cits, unres, x = doc("Additional work by Baron $(2012,2016)$ found.")
    if x:
        failures.append(f"a year-only math span is D2's unwrap case and MUST "
                        f"NOT be excluded, got {[r['excluded_reason'] for r in x]}")
    else:
        ok("B10/D2: a year-only math span is not math_expression")

    # And the positive, so the branch is not vacuous: math that is not
    # year-only carries no citation and is a correct refusal.
    x = excluded(r"The model $\alpha = 0.96 (2012) + x$ converged.")
    if [r.get("excluded_reason") for r in x] != ["math_expression"]:
        failures.append(f"a math span that is not year-only should be "
                        f"math_expression, got "
                        f"{[r.get('excluded_reason') for r in x]}")
    else:
        ok("B10: a math span that is not year-only is math_expression")

    # A2: the set is closed, and the code says so rather than trusting itself.
    if set(ce.EXCLUDED_REASONS) != {"leading_gloss", "url_or_image",
                                    "publisher_metadata", "math_expression",
                                    "conversion_artifact", "non_citation_year"}:
        failures.append(f"rc3 A2's excluded_reason set is CLOSED and has "
                        f"drifted: {sorted(ce.EXCLUDED_REASONS)}")
    else:
        ok("A2: excluded_reason is rc3's closed six-member set")

    try:
        ce._excl("x", 0, 1, "bare_locator", None, [], [])
    except AssertionError:
        ok("A2: a reason outside the closed set is refused, incl. bare_locator")
    else:
        failures.append("_excl accepted a reason outside rc3 A2's closed set; "
                        "`bare_locator` belongs to §C, not to correct refusal")

    # A1 + A3, the completeness invariant, over a document carrying all three
    # states at once. "Every detected candidate terminates as parsed,
    # unresolved, or correctly excluded. Nothing disappears silently."
    mixed = ("As shown (Smith, 2020) here. Then " + url +
             " and (nonsense here, 2021 unparseable) too.")
    body, cits, unres, x = doc(mixed)
    n_c1 = len(ce.c1_spans(body))
    states = [c["candidate_state"] for c in cits] \
        + [u["candidate_state"] for u in unres] \
        + [r["candidate_state"] for r in x]
    if not cits or not unres or not x:
        failures.append(f"the mixed document should reach all three states, "
                        f"got parsed {len(cits)} unres {len(unres)} excl {len(x)}")
    elif any(s not in ce.CANDIDATE_STATES for s in states):
        failures.append(f"a record carried a state outside A1's three: {states}")
    elif len(states) != n_c1:
        failures.append(f"A3 completeness: {n_c1} detected candidate(s) but "
                        f"{len(states)} terminal state(s) — a candidate was "
                        f"dropped or double-counted")
    else:
        ok("A1/A3: every detected candidate reaches exactly one of three states")

    # A4: "excluded span → excluded_candidate, NOT absent". The earlier draft
    # rc3 corrects had exclusion prevent candidacy, which would make this
    # record vanish and the 30-item accounting unreproducible.
    if not any(r["type"] == "excluded_candidate" for r in x):
        failures.append("an excluded span left no record; A4 requires it to be "
                        "present as excluded_candidate, not absent")
    else:
        ok("A4: an excluded span is emitted, not silently dropped")

    # A5, on the summary this time, which needs the CLI path.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "paper.md"
        p.write_text(HEAD + mixed + REFS, encoding="utf-8")
        lines, _code = ce.run(p, {"ampersand", "segments"})
    s = lines[-1]
    if s["extraction_denominator"] != s["parsed"] + s["unresolved"]:
        failures.append(f"A5: extraction_denominator must be parsed + "
                        f"unresolved, got {s['extraction_denominator']}")
    elif s["detected_candidates"] != s["extraction_denominator"] + s["excluded"]:
        failures.append("A5: detected_candidates must be parsed + unresolved "
                        "+ excluded")
    elif s["excluded"] == 0:
        failures.append("A5's denominator control ran on a document with "
                        "nothing excluded, so it would pass either way")
    else:
        ok("A5: the denominator excludes excluded_candidate")

    # A5: "Extraction accuracy, precision and recall MUST NOT be reported until
    # a gold set exists." The summary is the record that would carry them, so
    # the control is that it does not.
    #
    # This runs BEFORE the parse-rate check below, and that ordering is load
    # bearing. Probed the other way round, a mutation renaming
    # `candidate_parse_rate` to `extraction_accuracy` was "caught" by a
    # KeyError from the parse-rate check — a crash, not a control going red for
    # its own reason, and the banned-name control never executed at all. The
    # same shape as a build break being mistaken for a failing test.
    banned = [k for k in s
              if re.search(r"accuracy|precision|recall", k, re.I)]
    if banned:
        failures.append(f"A5 forbids the summary reporting accuracy, precision "
                        f"or recall; found {banned}")
    else:
        ok("A5: the summary reports a parse rate and no accuracy figure")

    if "candidate_parse_rate" not in s:
        failures.append("A5: the summary carries no candidate_parse_rate")
    elif abs(s["candidate_parse_rate"]
             - s["parsed"] / s["extraction_denominator"]) > 1e-9:
        failures.append("A5: candidate_parse_rate is parsed / "
                        "extraction_denominator")
    else:
        ok("A5: candidate_parse_rate is over the corrected denominator")

    # ------------------------------------- rc2 §7.4 / rc3 B1b, non-person
    #
    # rc3 B1b is the amendment rc3 forbids writing from rc3 alone. rc2 arrived
    # 21 September with the production, and these are §G's three cases plus the
    # negatives that make the rule safe rather than merely effective.

    print("\nrc2 §7.4 / rc3 B1b — institutional authors")

    IMF = ("\n\n## References\n\nInternational Monetary Fund. (2022). "
           "War sets back the global recovery. IMF.\n")

    # §G: "International Monetary Fund, 2022 → non_person via reconciliation"
    body, cits, unres, x = doc("Growth slowed (International Monetary Fund, "
                               "2022) sharply.", refs=IMF)
    if keys(cits) != ["non_person|international monetary fund|2022"]:
        failures.append(f"§G: (International Monetary Fund, 2022) keys the "
                        f"complete label — got {keys(cits)}")
    else:
        ok("§G: (International Monetary Fund, 2022) keys the complete label")

    # §G: "National Statistical Institute, 2022 → 3 cores, MUST reach a
    # candidate". Three cores is what defeated the merged B1/B1a production
    # rc3 corrected, so the control names the count.
    NSI = ("\n\n## References\n\nNational Statistical Institute. (2022). "
           "Active companies by economic sector. INE.\n")
    body, cits, unres, x = doc("Spain has 3,430,663 enterprises (National "
                               "Statistical Institute, 2022) today.", refs=NSI)
    if keys(cits) != ["non_person|national statistical institute|2022"]:
        failures.append(f"§G: a three-core institutional name reaches a "
                        f"candidate — got {keys(cits)}")
    else:
        ok("§G: a three-core institutional name reaches a candidate")

    # §G: "World Bank (2024) → MUST NOT yield bank|2024". The narrative form,
    # where `Bank (2024)` on its own satisfies AUTHORS_NARR and the wrong
    # answer is one discard away.
    WB = ("\n\n## References\n\nWorld Bank. (2024). Governance indicators. "
          "World Bank Group.\n")
    body, cits, unres, x = doc("Provided by the World Bank (2024) annually.",
                               refs=WB)
    if "bank|2024" in keys(cits):
        failures.append("§G: World Bank (2024) keys the whole label, never "
                        "bank|2024 — it degraded to bank|2024")
    elif keys(cits) != ["non_person|world bank|2024"]:
        failures.append(f"§G: World Bank (2024) keys the whole label, never "
                        f"bank|2024 — got {keys(cits)}")
    else:
        ok("§G: World Bank (2024) keys the whole label, never bank|2024")

    # rc2 §8, the negative that matters most: syntax does not confer identity.
    # Same sentence, no bibliography entry, and the span must stay unresolved.
    body, cits, unres, x = doc("Provided by the World Bank (2024) annually.")
    if cits:
        failures.append(f"rc2 §8: with no reference entry, the institution stays "
                        f"unresolved — it was keyed {keys(cits)}")
    else:
        ok("rc2 §8: with no reference entry, the institution stays unresolved")

    # The safeguard rc2 §7.4 states in terms. `Pircher Verdorfer` is a PERSON
    # with a compound surname and is the same shape as `Population Pyramid`:
    # two capitalised words, no comma, a year. Only the bibliography separates
    # them, and here it says person.
    PV = ("\n\n## References\n\nPircher Verdorfer, A. (2016). Mindfulness and "
          "leadership. Journal, 1(1), 1-10.\n")
    body, cits, unres, x = doc("Varies across individuals (Pircher Verdorfer, "
                               "2016) markedly.", refs=PV)
    if any(c["citation_key"].startswith("non_person|") for c in cits):
        failures.append(f"a compound personal surname is not read as an "
                        f"institution — got {keys(cits)}")
    else:
        ok("a compound personal surname is not read as an institution")

    # rc2 §7.4's no-comma rule, on the reference side, with rc2's own reason:
    # a comma-containing organisation author cannot be told apart from an
    # unsupported person-list form, so it is unresolved rather than guessed.
    if ce.non_person_head("FAO, 2005") is not None:
        failures.append("rc2 §7.4: no comma, at least one letter, non-empty — a "
                        "comma-containing head was accepted")
    elif ce.non_person_head("World Bank") != "world bank":
        failures.append("rc2 §7.4: no comma, at least one letter, non-empty — a "
                        "clean head was not normalised")
    else:
        ok("rc2 §7.4: no comma, at least one letter, non-empty")

    # §7.4's head boundary and its one trailing period.
    got = ce.reference_author_head("World Bank. (2016). Available at: x")
    if got != "World Bank":
        failures.append(f"rc2 §7.4: the head stops at the year paren, one period "
                        f"removed — got {got!r}")
    else:
        ok("rc2 §7.4: the head stops at the year paren, one period removed")

    # The reference side end to end, which is what the citation side matches
    # against. Four corpus entries were unresolved_reference before this.
    bib, bib_unres = ce.assemble_references(
        "World Bank. (2016). Governance indicators. World Bank Group.\n", 0)
    if not bib or bib[0].get("reference_key") != "non_person|world bank|2016":
        failures.append(f"rc2 §7.4: an institutional reference entry is keyed, "
                        f"not refused — got "
                        f"{[r.get('reference_key') for r in bib]}")
    else:
        ok("rc2 §7.4: an institutional reference entry is keyed, not refused")

    # --------------------------- rc2 §6.7 / §9.3, author-structure coherence
    #
    # The check that was missing. §8 reconciled on `surname|year` and threw
    # away everything else the in-text form asserts, so `Smith et al. (2020)`
    # and a one-author `Smith, J. (2020).` matched cleanly. 790 of this
    # corpus's 2094 citations carry the et al. form, so it is the check that
    # was rare, not the cases.

    print("\nrc2 §6.7 / §9.3 — author-structure coherence")

    import tempfile as _tf

    def run_doc(body_text, refs):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + refs, encoding="utf-8")
            return ce.run(p, {"ampersand", "segments"})

    def mism(body_text, refs):
        lines, _code = run_doc(body_text, refs)
        return [l for l in lines
                if l.get("type") == "author_structure_mismatch"]

    R2 = ("\n\n## References\n\nSmith, J., & Brown, K. (2020). A paper. "
          "Journal, 1(1), 1-10.\n")
    R1 = ("\n\n## References\n\nSmith, J. (2020). A paper. Journal, "
          "1(1), 1-10.\n")
    R3 = ("\n\n## References\n\nSmith, J., Brown, K., & Davis, L. (2020). "
          "A paper. Journal, 1(1), 1-10.\n")

    # §6.7, the fields themselves.
    f, v, c = ce.person_form("Smith & Jones")
    if (f, v, c) != ("exact", ["smith", "jones"],
                     {"kind": "exact", "value": 2}):
        failures.append(f"§6.7: exact form, visible authors and constraint — "
                        f"got {(f, v, c)}")
    else:
        ok("§6.7: exact form carries its visible authors and count")

    f, v, c = ce.person_form("Smith et al.")
    if (f, v, c) != ("et_al", ["smith"],
                     {"kind": "minimum", "value": ce.ET_AL_MIN_AUTHORS}):
        failures.append(f"§6.7: et al. is a MINIMUM constraint of "
                        f"ET_AL_MIN_AUTHORS — got {(f, v, c)}")
    else:
        ok("§6.7: et al. is a minimum constraint, not a count")

    # Particles retained, which rc2 states and which matters because the
    # identity key retains them too. Dropping them on one side only would make
    # the structure check disagree with the key built from the same phrase.
    _f, v, _c = ce.person_form("van der Maas & de Vries")
    if v != ["van der maas", "de vries"]:
        failures.append(f"§6.7: normalization retains particles — got {v}")
    else:
        ok("§6.7: particles are retained in visible_authors")

    # §9.3's two rules, each way round.
    if mism("As shown (Smith & Brown, 2020) here.", R2):
        failures.append("§9.3: exact passes when count and order agree — a "
                        "correct pair emitted a mismatch")
    else:
        ok("§9.3: exact passes when count and order agree")

    m = mism("As shown (Smith & Brown, 2020) here.", R1)
    if not m or m[0]["failed"] != "count":
        failures.append(f"§9.3: exact fails on count — got "
                        f"{[x['failed'] for x in m]}")
    else:
        ok("§9.3: exact fails on count against a one-author reference")

    m = mism("As shown (Smith & Jones, 2020) here.", R2)
    if not m or m[0]["failed"] != "order":
        failures.append(f"§9.3: exact fails on order — two authors each side "
                        f"and the second differs, got "
                        f"{[x['failed'] for x in m]}")
    else:
        ok("§9.3: exact fails on order when the second author differs")

    # "If count and order both fail, failed=count."
    m = mism("As shown (Jones & Davis & Lee, 2020) here.", R2)
    if m and m[0]["failed"] != "count":
        failures.append(f"§9.3: when count and order both fail, failed=count "
                        f"— got {m[0]['failed']}")
    else:
        ok("§9.3: count takes precedence when both halves fail")

    if mism("As shown (Smith et al., 2020) here.", R3):
        failures.append("§9.3: et_al passes against three authors — a correct "
                        "pair emitted a mismatch")
    else:
        ok("§9.3: et_al passes against a three-author reference")

    m = mism("As shown (Smith et al., 2020) here.", R2)
    if not m or m[0]["failed"] != "count":
        failures.append(f"§9.3: et_al fails below ET_AL_MIN_AUTHORS — a "
                        f"two-author work never takes et al., got "
                        f"{[x['failed'] for x in m]}")
    else:
        ok("§9.3: et_al fails against a two-author reference")

    # "The et_al rule compares every visible author, not only the first, so
    # `Smith, Jones, et al. (2020)` is checked on both."
    #
    # That form does NOT parse under v3.3: AUTHORS_PAREN admits `SURNAME WS et
    # WS al.` or a surname list, not a list followed by et al. Written as an
    # end-to-end control it produced an unresolved citation and no mismatch,
    # and asserting a rule through input the grammar cannot build would test
    # nothing. So the property is pinned where it IS reachable — the phrase
    # carries every visible author, which is what the comparison consumes —
    # and the end-to-end case waits on the grammar rc2 §2 specifies.
    _f, v, c = ce.person_form("Smith, Jones, et al.")
    if v != ["smith", "jones"]:
        failures.append(f"§9.3: an et_al phrase must carry EVERY visible "
                        f"author, since the rule compares all of them — "
                        f"got {v}")
    elif c != {"kind": "minimum", "value": ce.ET_AL_MIN_AUTHORS}:
        failures.append(f"§9.3: two visible names plus et al. is still a "
                        f"minimum constraint — got {c}")
    else:
        ok("§9.3: an et_al phrase carries every visible author, not just one")

    # The nulls. rc2: "A null takes no part in the check", because a false
    # mismatch against a pair that genuinely matched is worse than no check.
    NULL_REF = ("\n\n## References\n\nSmith, John. (2020). A paper. Journal, "
                "1(1), 1-10.\n")
    if mism("As shown (Smith & Brown, 2020) here.", NULL_REF):
        failures.append("a reference whose author list is not confidently "
                        "derivable must take no part in the check")
    else:
        ok("a full-forename reference takes no part in the check")

    if ce.reference_authors("Smith, J., et al.") is not None:
        failures.append("a reference containing et al. itself is not a "
                        "derivable author list")
    else:
        ok("a reference containing et al. yields no author list")

    # The partial case, which is the one that matters and which the two
    # controls above do NOT reach: both fail at the FIRST unit, so an
    # implementation returning whatever it had collected so far would still
    # return an empty list and look correct. Here the first unit parses and
    # the second does not, so a partial list is `['smith']` — a confident
    # wrong answer about a two-author work. rc2 §7.4 requires the list to
    # consume the ENTIRE head or yield nothing. Found by a surviving mutation,
    # not by reading.
    if ce.reference_authors("Smith, J., Brown, John") is not None:
        failures.append(f"a list that parses partway must yield nothing, not "
                        f"a partial list — got "
                        f"{ce.reference_authors('Smith, J., Brown, John')}")
    else:
        ok("a list that parses partway yields nothing, not a partial list")

    # The citation-side null, which is what stops a compound surname the
    # grammar cannot express from producing a confident wrong answer.
    _f, v, _c = ce.person_form("El Akremi et al.")
    if v is not None:
        failures.append(f"a compound surname outside the grammar must yield "
                        f"no structure rather than a partial one — got {v}")
    else:
        ok("a surname the grammar cannot express yields no structure")

    # §6.8's possessive, on this side too. Nine corpus mismatches were this
    # and this alone.
    _f, v, _c = ce.person_form("Tepper's")
    if v != ["tepper"]:
        failures.append(f"§6.8: the possessive is stripped before comparison "
                        f"— got {v}, which cannot match any reference")
    else:
        ok("§6.8: a possessive surname compares as the bare name")

    # rc2 §7.4's head, and the period that is an initial rather than a
    # terminator. Taken literally this rule left 1 of 1036 corpus references
    # with a derivable author list.
    if ce.reference_author_head("Bartko, J. (1976). Title.") != "Bartko, J.":
        failures.append("rc2 §7.4: a trailing period that IS an initial must "
                        "survive, or no person list can ever parse")
    else:
        ok("rc2 §7.4: a period belonging to an initial is not stripped")

    # `and` as a separator must not glue onto the next surname.
    if ce.reference_authors("Faems, D., De Visser, M., Andries, P.") != \
            ["faems", "de visser", "andries"]:
        failures.append("the `and` separator consumed the start of a surname; "
                        "Andries became ries")
    else:
        ok("a surname beginning with `and` is not split by the separator")

    # rc2 §9.3: identity survives. Alex Zamurko, 20 September: the occurrence
    # does not count as uniquely matched. Both, in one document.
    lines, code = run_doc("As shown (Smith & Brown, 2020) here.", R1)
    s = lines[-1]
    cit = next(l for l in lines if l.get("type") == "citation")
    if cit["citation_key"] != "smith|2020":
        failures.append("a mismatch must not erase the established identity")
    elif s["matched_occurrences"] != 0:
        failures.append(f"an author_structure_mismatch occurrence must not "
                        f"count as matched — got "
                        f"{s['matched_occurrences']}")
    elif code != 1:
        failures.append(f"an exact mismatch forces exit 1 — got {code}")
    else:
        ok("a mismatch keeps the identity, loses the match, and exits 1")

    lines, code = run_doc("As shown (Smith et al., 2020) here.", R2)
    if not any(l.get("type") == "author_structure_mismatch" for l in lines):
        failures.append("the et_al exit control ran on a document with no "
                        "mismatch, so it would pass either way")
    elif code != 1:
        # This document also has an unresolved-free, fully matched profile,
        # so exit 1 here comes from the mismatch alone being subtracted from
        # matched_occurrences — not from the et_al rule forcing it.
        ok("an et_al mismatch does not itself force exit 1")
    else:
        ok("an et_al mismatch is reported without forcing exit 1 on its own")

    # -------------------------------------------- rc3 B6 and D2
    print("\nrc3 B6 compact year-suffix, D2 math-wrapped years")

    case("B6: 2019a,b expands to two occurrences",
         "As shown (Sharma et al., 2019a,b) here.",
         ["sharma|2019a", "sharma|2019b"])
    case("B6: three suffixes expand to three",
         "As shown (Sharma et al., 2019a,b,c) here.",
         ["sharma|2019a", "sharma|2019b", "sharma|2019c"])
    case("B6: the narrative form expands too",
         "Sharma et al. (2019a,b) argue this.",
         ["sharma|2019a", "sharma|2019b"])
    # "Do not generalise to arbitrary year inference." A base with no suffix
    # cannot take a bare one, which is what keeps an ordinary multi-year
    # parenthetical out of the production.
    case("B6: an ordinary multi-year list is not a compact suffix list",
         "As shown (Smith, 2020, 2021) here.", ["smith|2020", "smith|2021"])
    case("B6: a single suffixed year is unchanged",
         "As shown (Smith, 2020a) here.", ["smith|2020a"])

    if ce.expand_year("2019") != ["2019"] or ce.expand_year("n.d.") != ["nd"]:
        failures.append("B6: expand_year leaves an ordinary year alone")
    else:
        ok("B6: expand_year leaves an ordinary year and n.d. alone")

    # `BASE_YEAR SUFFIX ("," SUFFIX)+` requires the suffix ON THE BASE. A bare
    # base followed by suffixes is not the production and must not expand.
    # Pinned here rather than through a document because the grammar cannot
    # build `2020,a` — a mutation making the base suffix optional was
    # unreachable end to end and survived, which is how this control exists.
    if ce.expand_year("2020,a") != ["2020,a"]:
        failures.append(f"B6: a base year with no suffix of its own is not a "
                        f"compact list — got {ce.expand_year('2020,a')}")
    else:
        ok("B6: a bare base year does not take a following suffix")

    # D2's MATCH and its three NEGATIVEs, stated as rules rather than advice
    # because "without the year-only and author-context restrictions, 'fix
    # upstream' leaves the implementer to decide which math spans are
    # citations, which is the discretion the rule exists to remove."
    d2 = ce.unwrap_math_years
    if d2(r"Additional work by Baron $(2012,2016)$ found.") != \
            "Additional work by Baron (2012,2016) found.":
        failures.append("D2: a year-only math span with an author before it "
                        "is unwrapped")
    else:
        ok("D2: a year-only span with an author context is unwrapped")

    for neg, why in [
            (r"The model $(2012,2016) + x$ converged.", "span is not year-only"),
            (r"We set $\alpha=0.96$ here.", "not a year list"),
            (r"A standalone $(2014)$ sits here.", "no preceding author")]:
        if d2(neg) != neg:
            failures.append(f"D2 negative — {why}: {neg!r} was altered")
            break
    else:
        ok("D2: all three of rc3's negatives are left alone")

    # And the finding. D2 unwraps correctly and recovers nothing, because the
    # form it produces is refused by the grammar D2 says it satisfies. Pinned
    # as a control so that if the year-list production is ever widened, this
    # says so out loud rather than a corpus number quietly moving.
    cits, unres, _x = extract("Additional work by Baron (2012,2016) found.")
    if keys(cits):
        failures.append(f"the year-list production has been widened to accept "
                        f"a comma with no whitespace. v3.3 §4 is "
                        f"`(?:, WS YEAR)*`; if this is now intended, D2 is "
                        f"worth its +3 and RC2-RC3-DISCREPANCIES.md #6 is "
                        f"resolved. Got {keys(cits)}")
    else:
        ok("D2: the unwrapped form still does not parse — worth 0, not +3")

    # -------------------------------------------- rc3 §C, citation errors
    print("\nrc3 §C — citation errors, a diagnostic class")

    def errs_for(body_text, refs=REFS):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + refs, encoding="utf-8")
            lines, _c = ce.run(p, {"ampersand", "segments"})
        return [l for l in lines if l.get("type") == "citation_error"], lines

    # rc3's two exemplars, and the pair is what distinguishes a case count
    # from a defect count.
    e, lines = errs_for("As shown (Gualandris, et al., 2024; p.56) here.")
    if len(e) != 1:
        failures.append(f"§C1: ONE record per parenthetical group, never one "
                        f"per defect — got {len(e)} records")
    elif e[0]["defects"] != ["et_al_punctuation", "wrong_locator_separator"]:
        failures.append(f"§C1: the Gualandris group carries two defects — "
                        f"got {e[0]['defects']}")
    elif e[0]["scope"] != "parenthetical_group":
        failures.append("§C1: scope is the parenthetical group")
    else:
        ok("§C1: one record per group, two defects listed, group-scoped")

    e, lines = errs_for("As shown (Barbier, 2022; P.923) here.")
    cit = [l for l in lines if l.get("type") == "citation"]
    if len(e) != 1 or e[0]["defects"] != ["wrong_locator_separator"]:
        failures.append(f"§C: the Barbier group carries ONE defect — got "
                        f"{[x['defects'] for x in e]}")
    elif not cit:
        failures.append("§C: `citation_error` is ORTHOGONAL to "
                        "candidate_state — Barbier parses AND carries an "
                        "error, and here it did not parse")
    else:
        ok("§C: Barbier parses and still carries one error — orthogonal axes")

    # C2 names the case-insensitivity as load-bearing: `P.923` is only a
    # locator because the pattern ignores case.
    if not ce.citation_errors("(Barbier, 2022; P.923)"):
        failures.append("§C2: the uppercase `P.` must be recognised; C2 calls "
                        "that dependency load-bearing")
    else:
        ok("§C2: an uppercase locator is recognised, as C2 requires")

    for text, want in [
            ("(Whiteman et al, 2013)", "et_al_punctuation"),
            ("(Choi at al., 2001)", "et_al_punctuation"),
            ("(Lu and Shang 2017)", "missing_comma_before_year"),
            ("(Smith, Weed, & Ramsay, 2005-present)", "non_numeric_year")]:
        got = ce.citation_errors(text)
        if want not in got:
            failures.append(f"§C: {text} should carry {want} — got {got}")
            break
    else:
        ok("§C: each of rc3's named defect shapes is detected")

    # The negatives. A well-formed group carries no error, and the two that
    # fired before the rule was narrowed stay quiet.
    # The last three are the ones that fired before the rule was narrowed.
    # `since` and `and` are excluded by the capital-initial requirement;
    # `See` and `Table` are capitalised and need the STOP guard, which is a
    # separate mechanism and is why both appear here.
    for clean in ["(Smith et al., 2020)", "(Smith, 2020, p. 14)",
                  "(running since 2005)", "(2011, 2012, and 2013)",
                  "(See 2020)", "(Table 2020)"]:
        if ce.citation_errors(clean):
            failures.append(f"§C: {clean} is not a citation error — got "
                            f"{ce.citation_errors(clean)}")
            break
    else:
        ok("§C: well-formed groups, stop words and non-author years are clean")

    # "The grammar MUST NOT be loosened to accept these forms."
    cits, unres, _x = extract("As shown (Lu and Shang 2017) here.")
    if keys(cits):
        failures.append(f"§C: the grammar was loosened to accept a malformed "
                        f"form; rc3 forbids it. Got {keys(cits)}")
    else:
        ok("§C: naming the defect did not loosen the grammar")

    # And the defect list is ordered by declaration, not by discovery, so two
    # implementations emit the same list for the same group.
    if ce.citation_errors("(Gualandris, et al., 2024; p.56)") != \
            ce.citation_errors("(Gualandris, et al., 2024; p.56)"):
        failures.append("§C: the defect list must be deterministic")
    elif ce.CITATION_ERROR_DEFECTS.index("et_al_punctuation") > \
            ce.CITATION_ERROR_DEFECTS.index("wrong_locator_separator"):
        failures.append("§C: defects are listed in declaration order")
    else:
        ok("§C: the defect list is in declaration order, not discovery order")

    # ------------------------- rc2 §8.2 / §8.3, identity — CIT-ARCH-01
    print("\nrc2 §8.2 / §8.3 — identity states, per CIT-ARCH-01")

    R_ONE = ("\n\n## References\n\nSmith, J. (2020). A paper. Journal, "
             "1(1), 1-10.\n")
    R_DUP = ("\n\n## References\n\nSmith, J. (2020). A paper. Journal, "
             "1(1), 1-10.\nSmith, J. (2020). A different paper. Other, "
             "2(1), 1-9.\n")
    R_NONE = ("\n\n## References\n\nJones, K. (2019). Unrelated. "
              "Journal, 1(1), 1-10.\nBrown, L. (2018). Also unrelated. "
              "Journal, 2(1), 1-9.\nDavis, M. (2017). Third. J, 3, 1.\n"
              "Evans, N. (2016). Fourth. J, 4, 1.\nFord, O. (2015). "
              "Fifth. J, 5, 1.\n")

    def ident(body_text, refs):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + refs, encoding="utf-8")
            lines, _c = ce.run(p, {"ampersand", "segments"})
        cit = next((l for l in lines if l.get("type") == "citation"), None)
        amb = [l for l in lines if l.get("type") == "ambiguous_citation"]
        return cit, amb, lines[-1]

    # §8.3 row 2: F=unique, S=no_match → full_phrase, key authoritative.
    c, amb, _s = ident("As shown (Smith, 2020) here.", R_ONE)
    if not c or c["match_state"] != "unique":
        failures.append(f"§8.2: one keyed reference is a unique match — got "
                        f"{c and c['match_state']}")
    elif c["author_resolution"] != "full_phrase":
        failures.append(f"§8.3 unique/no_match is full_phrase — got "
                        f"{c['author_resolution']}")
    elif c["identity_class"] != "unique_reference_match":
        failures.append(f"§8.3: a unique match is unique_reference_match — "
                        f"got {c['identity_class']}")
    elif len(c["reference_indices"]) != 1:
        failures.append("§8.2: unique means exactly one reference index")
    elif amb:
        failures.append("§8.3: a unique match emits no ambiguous_citation")
    else:
        ok("§8.3: unique/no_match → full_phrase, one reference index")

    # §8.3 row 3: F=nonunique → same key, AND emit ambiguous_citation.
    c, amb, _s = ident("As shown (Smith, 2020) here.", R_DUP)
    if not c or c["match_state"] != "nonunique":
        failures.append(f"§8.2: two references sharing a key is nonunique — "
                        f"got {c and c['match_state']}")
    elif len(c["reference_indices"]) != 2:
        failures.append(f"§8.2: nonunique carries every index — got "
                        f"{c['reference_indices']}")
    elif c["reference_indices"] != sorted(c["reference_indices"]):
        failures.append("§8.2: reference_indices are ascending")
    elif len(amb) != 1:
        failures.append(f"§8.3: nonunique emits exactly one "
                        f"ambiguous_citation — got {len(amb)}")
    elif c["identity_class"] != "bibliography_key_ambiguous":
        failures.append(f"§8.3: nonunique is bibliography_key_ambiguous — "
                        f"got {c['identity_class']}")
    else:
        ok("§8.3: nonunique/no_match → ambiguous_citation, key retained")

    # §8.3 row 1: F=no_match → not_resolved. CIT-ARCH-01's core case: the
    # citation parses, and identity is NOT established by that alone.
    c, amb, _s = ident("As shown (Smith, 2020) here.", R_NONE)
    if not c:
        failures.append("the citation should still parse with no matching "
                        "reference; extraction and identity are separate")
    elif c["match_state"] != "no_match":
        failures.append(f"§8.2: no keyed reference is no_match — got "
                        f"{c['match_state']}")
    elif c["author_resolution"] != "not_resolved":
        failures.append(f"§8.3 no_match/no_match is not_resolved — got "
                        f"{c['author_resolution']}")
    elif c["identity_class"] != "identity_not_resolved":
        failures.append(f"§8.3: got {c['identity_class']}")
    elif c["reference_indices"] != []:
        failures.append("§8.2: no_match carries zero reference indices")
    else:
        ok("§8.3: no_match → not_resolved, and the citation still parses")

    # CIT-ARCH-01: "preserving the citation-derived candidate". The candidate
    # survives the failure to confirm; it is not discarded.
    if c and c.get("candidate_key") != "smith|2020":
        failures.append(f"CIT-ARCH-01 preserves the citation-derived "
                        f"candidate when nothing confirms it — got "
                        f"{c and c.get('candidate_key')}")
    else:
        ok("CIT-ARCH-01: an unconfirmed candidate is preserved, not discarded")

    # rc2 §11.2's partition, which is what makes the three classes countable.
    #
    # The fixture must contain ALL THREE classes at once. Written first with
    # only unique and not_resolved, a mutation that double-counted the
    # ambiguous class survived, because the class it double-counted was empty.
    # A partition control over two of three parts is not a partition control.
    R_MIX = ("\n\n## References\n\nSmith, J. (2020). A paper. Journal, "
             "1(1), 1-10.\nSmith, J. (2020). A different paper. Other, "
             "2(1), 1-9.\nBrown, L. (2018). Third. J, 3, 1.\n")
    _c, _a, s = ident("As shown (Smith, 2020; Brown, 2018; Jones, 2019) here.",
                      R_MIX)
    counts = (s["unique_reference_match_occurrences"],
              s["bibliography_key_ambiguous_occurrences"],
              s["identity_not_resolved_occurrences"])
    if sum(counts) != s["parsed"]:
        failures.append(f"§11.2: the identity classes must partition the "
                        f"parsed occurrences — {sum(counts)} vs "
                        f"{s['parsed']}")
    elif not all(counts):
        failures.append(f"the partition control needs all three classes "
                        f"present or it cannot see a double-count — got "
                        f"{counts}")
    else:
        ok("§11.2: the identity classes partition the parsed occurrences")

    # And the six rows that CANNOT be reached, said out loud rather than
    # left as untested code. §8.3: "If no STOP-reduced candidate exists, S is
    # no_match." rc2 §6.3's additive STOP reduction is C-019, unimplemented,
    # so nothing here ever produces one.
    if any(c.get("stop_reduced_phrase") for c in
           [ident("As shown (Smith, 2020) here.", R_ONE)[0]] if c):
        failures.append("a STOP-reduced candidate exists, so §8.3's other "
                        "six rows are now reachable and must be implemented")
    else:
        ok("§8.3: S is always no_match here, so six rows stay unreachable")

    # ------------------- rc2 §9.4 / §9.5, candidate-level diagnostics
    print("\nrc2 §9.4 — candidate-level missing reference and repair")

    def diag(body_text, refs):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + refs, encoding="utf-8")
            lines, _c = ce.run(p, {"ampersand", "segments"})
        return ([l for l in lines if l.get("type") == "missing_reference"],
                [l for l in lines if l.get("type") == "possible_mismatch"])

    PAD = ("Jones, K. (2019). A. J, 1, 1.\nBrown, L. (2018). B. J, 2, 1.\n"
           "Davis, M. (2017). C. J, 3, 1.\nEvans, N. (2016). D. J, 4, 1.\n")

    # The three rules, each with the reference that should pair.
    for label, cite, entry, rule in [
            ("surname_edit_distance_1",
             "(Whiteman, 2000)", "Whitman, R. (2000). A paper. J, 1, 1.",
             "surname_edit_distance_1"),
            ("year_adjacent",
             "(Madison, 2010)", "Madison, R. (2009). A paper. J, 1, 1.",
             "year_adjacent"),
            ("year_transposition",
             "(Larsen, 2019)", "Larsen, R. (2091). A paper. J, 1, 1.",
             "year_transposition")]:
        mr, pm = diag(f"As shown {cite} here.",
                      "\n\n## References\n\n" + entry + "\n" + PAD)
        if len(pm) != 1 or pm[0]["rule"] != rule:
            failures.append(f"§9.4 {label}: expected one possible_mismatch "
                            f"with rule {rule} — got "
                            f"{[(x['rule']) for x in pm]}, {len(mr)} missing")
            break
    else:
        ok("§9.4: all three repair rules pair their reference")

    # REFERENCE order decides, not rule order. rc2: "scan unmatched references
    # in source order and take the first rule that matches." That is
    # reference-major, and this control was written rule-major first and
    # failed against a correct implementation.
    #
    # rc2 also lists the rules "in precedence order", which reads as though it
    # settles a contest between them. It cannot: rule 1 requires equal years
    # and rules 2 and 3 require different ones, and no year pair is both
    # transposed and adjacent — checked exhaustively over 1500-2099. So at
    # most one rule can match any single reference and the precedence list is
    # unexercisable. Recorded rather than asserted as behaviour.
    mr, pm = diag("As shown (Whiteman, 2000) here.",
                  "\n\n## References\n\nWhiteman, R. (1999). Year adjacent. "
                  "J, 1, 1.\nWhitman, R. (2000). Edit distance. J, 2, 1.\n"
                  + PAD)
    if len(pm) != 1:
        failures.append(f"§9.4: one candidate pairs at most once — got "
                        f"{len(pm)}")
    elif pm[0]["rule"] != "year_adjacent":
        failures.append(f"§9.4: references are scanned in SOURCE order, so "
                        f"the 1999 entry pairs first — got {pm[0]['rule']}")
    else:
        ok("§9.4: reference source order decides which entry pairs")

    # And the claim the comment above rests on, pinned so it cannot rot.
    if ce.repair_rule("person", "smith", "2020", "person", "smith", "2020"):
        failures.append("§9.4: an exact match is not a repair; it would have "
                        "resolved as a unique match")
    elif (ce.repair_rule("person", "whitman", "2000",
                         "person", "whiteman", "2000")
          != "surname_edit_distance_1"):
        failures.append("§9.4: equal years and one edit is rule 1")
    elif (ce.repair_rule("person", "smith", "2000", "person", "smith", "1999")
          != "year_adjacent"):
        failures.append("§9.4: equal phrases and adjacent years is rule 2")
    else:
        ok("§9.4: the rules are mutually exclusive on one reference")

    # The CORE length floor. rc2: "candidate CORE length >= 4 code points",
    # which is what stops short surnames pairing with anything one letter away.
    if ce.repair_rule("person", "wu", "2020", "person", "xu", "2020"):
        failures.append("§9.4: a candidate CORE shorter than 4 code points "
                        "must not pair by edit distance")
    else:
        ok("§9.4: the CORE length floor stops short surnames pairing")

    # "A pair MUST have the same candidate/reference author kind."
    if ce.repair_rule("person", "world bank", "2020",
                      "non_person", "world bank", "2021"):
        failures.append("§9.4: a pair must share author kind")
    else:
        ok("§9.4: a person candidate never pairs with a non-person reference")

    # Nothing established. rc2 says it twice and CIT-ARCH-01 says it again.
    mr, pm = diag("As shown (Smith, 2020) here.",
                  "\n\n## References\n\n" + PAD)
    if len(mr) != 1:
        failures.append(f"§9.4: an unpairable candidate emits one "
                        f"missing_reference — got {len(mr)}")
    elif mr[0]["citation_key"] is not None or mr[0]["author_kind"] is not None:
        failures.append("§9.4: neither diagnostic establishes citation_key "
                        "or author_kind")
    elif mr[0]["candidate_key"] != "smith|2020":
        failures.append("CIT-ARCH-01: the candidate is preserved in the "
                        "diagnostic")
    else:
        ok("§9.4: missing_reference preserves the candidate, establishes none")

    # C-054 is that same rule on the other diagnostic, and it was unpinned
    # until now. The emission sets both fields to None and no control asked,
    # so the mutation probe had nothing to make red. rc2 states the rule for
    # BOTH diagnostics; the suite only held one of them.
    mr, pm = diag("As shown (Whiteman, 2000) here.",
                  "\n\n## References\n\nWhitman, R. (2000). A paper. J, 1, 1."
                  "\n" + PAD)
    if len(pm) != 1:
        failures.append(f"§9.4: the repair pairs — got {len(pm)}")
    elif pm[0]["citation_key"] is not None or pm[0]["author_kind"] is not None:
        failures.append("§9.4: a possible_mismatch establishes no citation_key "
                        "or author_kind either")
    elif pm[0]["candidate_key"] != "whiteman|2000":
        failures.append("§9.4: possible_mismatch preserves the CANDIDATE, not "
                        "the reference it paired with")
    else:
        ok("§9.4: a possible_mismatch establishes no citation_key")

    # C-060. rc2 qualifies merge_suspected by the candidate's OWN phrase and
    # year appearing inside a suspect entry — "targeted, not global". Both
    # halves need pinning: a flag hardcoded True passes any control that only
    # looks at the merged case, and one hardcoded False passes any control
    # that only looks at the clean one.
    MERGED = ("Kowalski, T. (2015). A paper. Smith, J. (2020). A merged "
              "entry. J, 1, 1.\n" + PAD)
    mr_hit, _ = diag("As shown (Smith, 2020) here.",
                     "\n\n## References\n\n" + MERGED)
    mr_miss, _ = diag("As shown (Smith, 2020) here.",
                      "\n\n## References\n\n" + PAD)
    if len(mr_hit) != 1 or len(mr_miss) != 1:
        failures.append(f"§9.5: both candidates are unpairable and emit one "
                        f"missing_reference each — got {len(mr_hit)}, "
                        f"{len(mr_miss)}")
    elif not mr_hit[0]["merge_suspected"]:
        failures.append("§9.5: a candidate whose phrase and year sit inside a "
                        "merged entry is merge_suspected")
    elif mr_miss[0]["merge_suspected"]:
        failures.append("§9.5: merge_suspected is targeted, not global")
    else:
        ok("§9.5: merge_suspected is targeted at the candidate, not global")

    # A paired reference leaves the pool, so a second candidate cannot claim
    # the same entry. Without this, one typo'd reference repairs every
    # citation that happens to be one letter away from it.
    # BOTH candidates must be pairable with the one entry, or the control
    # cannot see the pool at all. Written first with `Whitemen`, which is
    # edit-distance TWO from `Whitman` and so was never a candidate for it —
    # the control passed whether or not the pool was emptied. `Whitmen` is
    # one edit, like `Whiteman`.
    mr, pm = diag("As shown (Whiteman, 2000; Whitmen, 2000) here.",
                  "\n\n## References\n\nWhitman, R. (2000). One entry. "
                  "J, 1, 1.\n" + PAD)
    if len(pm) != 1:
        failures.append(f"§9.4: a paired reference is removed from the pool, "
                        f"so exactly one of two equally close candidates "
                        f"pairs — got {len(pm)}")
    else:
        ok("§9.4: a paired reference leaves the pool and pairs only once")

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
