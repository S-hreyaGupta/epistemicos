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

import json as _json
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
    body, section, off, heads, _src = ce.split_body_and_references(text)
    if "ampersand" in fixes:
        body = body.replace("\\&", "&")
    sents = ce.sentences(body)
    return ce.extract_citations(body, sents, heads, set(fixes))[:3]


def keys(cits):
    return [c["citation_key"] for c in cits]


# Module level so a crash cannot discard what has already been recorded.
#
# Seventeen controls index `cits[0]` or similar without first checking the
# list is non-empty. Under a mutation that stops something parsing, one of
# those raises IndexError — and the traceback replaces the report, so every
# failure collected up to that point is lost. On 22 September the mutation
# probe read that as "no control failed" for a mutation the suite HAD caught:
# §6.3's control recorded the failure and a control 1400 lines later crashed
# before it could be printed.
#
# Guarding all seventeen is the wrong shape; the defect is that the report is
# only emitted on the happy path. `__main__` below now prints the failures
# whatever happens, so a crash reports a crash AND the findings.
FAILURES: list[str] = []


def rc2_spec_path() -> Path | None:
    """rc2's execution-conformance document, located from the working directory.

    Not from `__file__`: the mutation probe copies the suite into a temp
    directory and runs it there, so a path relative to this file resolves into
    the temp directory and the read fails. Six mutations crashed that way rather
    than taking a control red, and the probe reported them as WRONG CONTROL.
    """
    probe = Path.cwd()
    for _ in range(4):
        cand = probe / "specs/citation/citation-v3.4-rc2-execution-conformance.md"
        if cand.exists():
            return cand
        probe = probe.parent
    return None


def rc2_section(number: str) -> list[str]:
    """The lines of rc2's first ```text block under `### <number>`.

    So a control can assert against rc2's own list instead of a tuple somebody
    typed from memory. §11.3's field list was miscounted twice by eye — once as
    eight, once as ten — before it was read this way.
    """
    p = rc2_spec_path()
    if p is None:
        return []
    out, in_sec, in_block = [], False, False
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.startswith("### "):
            if in_sec and out:
                break
            in_sec = ln.startswith(f"### {number} ")
            continue
        if in_sec and ln.strip().startswith("```"):
            if in_block:
                break
            in_block = True
            continue
        if in_sec and in_block:
            out.append(ln)
    return out


def rc2_declared() -> dict[str, list[str]]:
    """rc2's declared key order per record type, read from rc2's own bytes.

    Walks up from the working directory rather than from this file, because the
    mutation probe copies the suite into a temp directory and runs it there.
    An earlier version resolved the path relative to `__file__`, which made
    six mutations crash on a missing spec file instead of taking a control red
    — reported as WRONG CONTROL, which is the probe working correctly on a
    broken probe.

    Reading rc2 rather than `ce.KEY_ORDER` is the point. Comparing the output
    against the table the output was built from is self-consistent by
    construction: it can show the table was not applied, never that the table
    is wrong. The probe demonstrated exactly that — swapping two keys inside
    KEY_ORDER survived, because the control moved with it.
    """
    p = rc2_spec_path()
    if p is None:
        return {}
    out: dict[str, list[str]] = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.startswith('{"type":'):
            try:
                parsed = _json.loads(ln)
            except ValueError:
                continue
            out.setdefault(parsed["type"], list(parsed))
    return out


def main() -> int:
    failures: list[str] = FAILURES

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
    #
    # This control asserted `Bartko's` until 22 September, which was the
    # REDUCED phrase — `Following` had been dropped. It passed because the
    # extractor was doing what rc3 §A forbids, so a control written to pin
    # §A was in fact pinning its violation. It now asserts the complete run,
    # which is what §A says, and the reduced form is pinned beside it.
    case("author_phrase keeps what the manuscript wrote",
         "Following Bartko's (1976) formula, we did this.",
         ["bartko|1976"], want_authors=["Following Bartko's"])
    # A possessive inside a name is not a trailing one.
    case("a name is not truncated at an internal apostrophe",
         "As shown (O'Brien, 2020).", ["o'brien|2020"])

    # ---- rc2 §6.3, C-019 and C-020: reduction is ADDITIVE ----
    print("\nrc2 §6.3 — STOP reduction is additive, not destructive")

    def phrases(body_text, fixes=frozenset()):
        cits, _u, _e = extract(body_text, fixes)
        return [(c["author_phrase"], c["stop_reduced_phrase"]) for c in cits]

    got = phrases("As Podsakoff et al. (2003) showed, this holds.")
    if got != [("As Podsakoff et al.", "Podsakoff et al.")]:
        failures.append(f"§6.3: both phrases survive reduction — got {got}")
    else:
        ok("§6.3: author_phrase is the full run, the reduced form is separate")

    # "If full_phrase fully satisfies AUTHORS_NARR" there is no reduction, and
    # the field must be null rather than a copy. A copy would make the two
    # indistinguishable and §8.1 would build a duplicate second candidate.
    got = phrases("Podsakoff et al. (2003) showed this.")
    if got != [("Podsakoff et al.", None)]:
        failures.append(f"§6.3: no reduction means no reduced phrase — "
                        f"got {got}")
    else:
        ok("§6.3: stop_reduced_phrase is null when nothing was removed")

    # C-020, stated on its own: STOP reduction MUST never rewrite the source
    # field. The identity still comes from the reduced phrase.
    cits, _u, _e = extract("From Han and Kim (2010) we take this.")
    if not cits:
        failures.append("§6.3: the lead-in case still has to parse")
    elif cits[0]["author_phrase"] != "From Han and Kim":
        failures.append(f"C-020: the source surface is not rewritten — got "
                        f"{cits[0]['author_phrase']!r}")
    elif cits[0]["citation_key"] != "han|2010":
        failures.append(f"§6.3: identity comes from the REDUCED phrase — got "
                        f"{cits[0]['citation_key']!r}")
    else:
        ok("C-020: the full surface is kept and the identity still reduces")

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
        # "no references section" used to sit here expecting exit 3. rc2 §14
        # allocates exit 3 to "invalid section map" and gives a missing
        # bibliography no exit at all — §10 processes it instead. The case
        # moved to the §10 block below rather than being deleted, because the
        # behaviour it pinned is still pinned, just inverted.
        #
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

    def source_of(doc: str, label: str):
        """The references_source, or None having recorded the abort.

        rc2 §10 removed the exit-3 refusal, so an Abort reaching here is the
        defect rather than the expected outcome — and letting it propagate
        would crash the run and discard every failure recorded before it,
        which is exactly how a caught mutation came to read as uncaught on
        22 September.
        """
        try:
            return splits(doc)[4]
        except ce.Abort as a:
            failures.append(f"{label}: aborted exit {a.code}. rc2 §14 has no "
                            f"exit for a missing bibliography; §10 processes "
                            f"the manuscript instead")
            return None

    try:
        body, refs, _, _, _ = splits(
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
        # These asserted exit 3 until 22 September. rc2 §10 removed that abort,
        # so refusal now shows as `not_available` rather than as a throw —
        # which is a STRONGER assertion, not a weaker one: the old form passed
        # on any abort for any reason, and this names the outcome.
        src = source_of(doc, label)
        if src is not None and src != "not_available":
            failures.append(f"a `References` line with {label} was accepted "
                            f"as a boundary; the confirmation check did not "
                            f"hold — got references_source {src!r}")
        else:
            ok(f"refused: a `References` line with {label}")

    # Out of order is the confirmation the ruling names.
    src = source_of(
        "# P\n\n## Intro\n\nText.\n\nReferences\n\n"
        "Evans, T. (2005). A paper. Journal, 1(1), 1-10.\n"
        "Dunn, M. (2004). Another. Journal, 2(1), 1-10.\n"
        "Clark, S. (2003). A third. Journal, 3(1), 1-10.\n"
        "Baker, R. (2002). A fourth. Journal, 4(1), 1-10.\n"
        "Adams, J. (2001). A fifth. Journal, 5(1), 1-10.\n",
        "reverse-alphabetical")
    if src is not None and src != "not_available":
        failures.append(f"a reverse-alphabetical run was accepted; the "
                        f"ordering confirmation did not hold — got {src!r}")
    else:
        ok("refused: entries below the label are not in order")

    # A real heading still wins, so the fallback cannot change any paper that
    # already worked.
    try:
        body, refs, _, _, _ = splits(
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
        body, section, off, heads, _src = ce.split_body_and_references(text)
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
    elif s["uniquely_matched_occurrences"] != 0:
        failures.append(f"an author_structure_mismatch occurrence must not "
                        f"count as matched — got "
                        f"{s['uniquely_matched_occurrences']}")
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
        # uniquely_matched_occurrences — not from the et_al rule forcing it.
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
    # FOUR classes since §8.3 rows 6-9 landed. This fixture produces three of
    # them and no ambiguous one, so the fourth is asserted zero here and
    # exercised by the row-6 control below — a partition summed over three
    # names while the code can emit four holds only while the fourth stays
    # empty, and that is not an invariant.
    counts = (s["unique_reference_match_occurrences"],
              s["bibliography_key_ambiguous_occurrences"],
              s["identity_not_resolved_occurrences"],
              s["author_resolution_ambiguous_occurrences"])
    if sum(counts) != s["parsed"]:
        failures.append(f"§11.2: the identity classes must partition the "
                        f"parsed occurrences — {sum(counts)} vs "
                        f"{s['parsed']}")
    elif not all(counts[:3]):
        failures.append(f"the partition control needs all three reachable "
                        f"classes present or it cannot see a double-count — "
                        f"got {counts}")
    elif counts[3] != 0:
        failures.append(f"this fixture has no ambiguous occurrence; got "
                        f"{counts[3]}")
    else:
        ok("§11.2: the identity classes partition the parsed occurrences")

    # And the six rows that CANNOT be reached, said out loud rather than
    # left as untested code. §8.3: "If no STOP-reduced candidate exists, S is
    # no_match." rc2 §6.3's additive STOP reduction is C-019, unimplemented,
    # so nothing here ever produces one.
    # A PARENTHETICAL still has one candidate, so its S stays no_match and the
    # first column is still what it reaches.
    if any(c.get("stop_reduced_phrase") for c in
           [ident("As shown (Smith, 2020) here.", R_ONE)[0]] if c):
        failures.append("a parenthetical occurrence gained a reduced phrase; "
                        "§6.3 creates one for NARRATIVE candidates only")
    else:
        ok("§8.3: a parenthetical has one candidate, so its S is no_match")

    # ---- §8.1's second candidate, and §8.3's rows 4 and 5 ----
    #
    # These were unreachable until C-019 landed on 22 September. The comment
    # that used to sit here said implementing them would be writing code no
    # input could reach; that is no longer true and both now have an input.

    # Row 4: F=no_match, S=unique → author_resolution=stop_reduced, and the
    # STOP key is the authoritative one.
    cit, amb, _s = ident("As Smith et al. (2020) showed this.", R_ONE)
    if cit is None:
        failures.append("§8.3 row 4: the lead-in occurrence did not parse")
    elif cit["author_resolution"] != "stop_reduced":
        failures.append(f"§8.3 row 4: F=no_match, S=unique is stop_reduced — "
                        f"got {cit['author_resolution']!r}")
    elif cit["match_state_full"] != "no_match":
        failures.append(f"§8.3 row 4: the FULL candidate must not match — got "
                        f"{cit['match_state_full']!r}")
    elif cit["candidate_key"] != "smith|2020":
        failures.append(f"§8.3 row 4: the STOP key is authoritative — got "
                        f"{cit['candidate_key']!r}")
    elif cit["identity_class"] != "unique_reference_match":
        failures.append(f"§8.3 row 4: identity is resolved — got "
                        f"{cit['identity_class']!r}")
    else:
        ok("§8.3 row 4: no_match/unique → stop_reduced, STOP key authoritative")

    # Row 5: F=no_match, S=nonunique → same STOP key, plus ambiguous_citation.
    cit, amb, _s = ident("As Smith et al. (2020) showed this.", R_DUP)
    if cit is None or cit["author_resolution"] != "stop_reduced":
        failures.append(f"§8.3 row 5: still stop_reduced — got "
                        f"{cit and cit['author_resolution']!r}")
    elif cit["match_state_stop_reduced"] != "nonunique":
        failures.append(f"§8.3 row 5: S must be nonunique — got "
                        f"{cit['match_state_stop_reduced']!r}")
    elif len(amb) != 1:
        failures.append(f"§8.3 row 5: exactly one ambiguous_citation — got "
                        f"{len(amb)}")
    else:
        ok("§8.3 row 5: no_match/nonunique → stop_reduced + ambiguous_citation")

    # §9.4's precondition, now live. "exactly one deterministic internal
    # candidate exists" — a reduced occurrence has two, so no candidate-level
    # diagnostic may name either. Nothing in the corpus reaches this, so the
    # input is built here; without it the rule would be implemented and
    # unexercised.
    with _tf.TemporaryDirectory() as td:
        p = Path(td) / "paper.md"
        p.write_text(HEAD + "As Nobody et al. (1999) argued this."
                     + R_NONE, encoding="utf-8")
        lines, _c = ce.run(p, {"ampersand", "segments"})
    cit = next((l for l in lines if l.get("type") == "citation"), None)
    mr = [l for l in lines if l.get("type") == "missing_reference"]
    if cit is None or not cit.get("stop_reduced_phrase"):
        failures.append("§8.4: the two-candidate fixture did not reduce")
    elif cit["identity_class"] != "identity_not_resolved":
        failures.append(f"§8.4: the fixture must resolve to nothing — got "
                        f"{cit['identity_class']!r}")
    elif mr:
        failures.append(f"§8.4: two candidates suppress candidate-level "
                        f"diagnostics — got {len(mr)} missing_reference")
    else:
        ok("§8.4: two internal candidates suppress the §9.4 diagnostic")

    # ---- §8.3 rows 6 to 9, §8.5 reservation, §8.6 double resolution ----
    #
    # No corpus input reaches these. The fixture is built, and it is buildable
    # through the real pipeline rather than by injection: a bibliography
    # carrying an institutional entry whose label IS the lead-in plus the
    # surname, beside the person entry for the same surname.
    R_BOTH = ("From Tether (2018). A report. Publisher.\n"
              "Tether, B. (2018). A paper. Journal, 1(1), 1-10.\n"
              "Brown, L. (2017). Unrelated. J, 2, 1.\n")

    def amb(body_text, refs):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + "\n\n## References\n\n" + refs,
                         encoding="utf-8")
            lines, _c = ce.run(p, {"ampersand", "segments"})
        return (next((l for l in lines if l.get("type") == "citation"), None),
                [l for l in lines
                 if l.get("type") == "ambiguous_author_resolution"],
                [l for l in lines if l.get("type") == "uncited_reference"],
                lines[-1])

    cit, aar, unc, summ = amb("From Tether (2018) we take this.", R_BOTH)
    if cit is None:
        failures.append("§8.3 row 6: the fixture did not parse")
    elif cit["author_resolution"] != "ambiguous":
        failures.append(f"§8.3 row 6: two matching candidates with different "
                        f"keys is ambiguous — got {cit['author_resolution']!r}")
    elif cit["citation_key"] is not None or cit["author_kind"] != "undetermined":
        failures.append("§8.3: an ambiguous occurrence establishes no "
                        "citation_key and no author_kind")
    elif len(aar) != 1:
        failures.append(f"§8.3: EXACTLY ONE ambiguous_author_resolution per "
                        f"occurrence, never one per candidate — got {len(aar)}")
    elif [x["candidate"] for x in aar[0]["candidates"]] != ["full",
                                                            "stop_reduced"]:
        failures.append("C-048: the record carries both candidates, named")
    elif summ["author_resolution_ambiguous_occurrences"] != 1:
        failures.append("§11.2: the fourth identity class is counted")
    else:
        ok("§8.3 row 6: different keys → ambiguous, nothing established")

    # §8.5. Both reserved indices must leave the pool, or ambiguity turns into
    # two false uncited references — which is the one outcome the section
    # names twice.
    if any(u["reference_key"] in ("tether|2018", "non_person|from tether|2018")
           for u in unc):
        failures.append(f"§8.5: reserved indices must not emit "
                        f"uncited_reference — got "
                        f"{[u['reference_key'] for u in unc]}")
    elif [u["reference_key"] for u in unc] != ["brown|2017"]:
        failures.append(f"§8.5: only the genuinely unreserved entry is "
                        f"uncited — got {[u['reference_key'] for u in unc]}")
    else:
        ok("§8.5: ambiguity-reserved references leave the pool")

    # §8.6, and the finding that goes with it. The abort is implemented and
    # CANNOT FIRE, by rc2's own construction rather than by ours: §6.3 creates
    # a reduced phrase only when the full phrase FAILS the person grammar, and
    # §8.1 keys the full candidate `person|` only when it PASSES. So whenever
    # both candidates exist they are in different namespaces — `non_person|…`
    # against a bare surname — and cannot serialize the same string.
    #
    # Same shape as §9.4's precedence list: well formed, and with no input.
    # Recorded rather than asserted as behaviour, and the namespace split is
    # pinned instead, since that is the thing actually holding.
    if cit["candidate_key_full"] == cit["candidate_key_stop_reduced"]:
        failures.append("§8.6: the two candidate keys collided, so the "
                        "double-resolution abort is now reachable")
    elif not cit["candidate_key_full"].startswith("non_person|"):
        failures.append(f"§8.6: a reduced occurrence keys its FULL candidate "
                        f"non-person — got {cit['candidate_key_full']!r}")
    else:
        ok("§8.6: the two candidates cannot collide, so exit 6 has no input")

    # ---- rc2 §6.6, the surface grouping key ----
    print("\nrc2 §6.6 — surface grouping is not identity")

    def sgk(body_text, refs):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + refs, encoding="utf-8")
            lines, _c = ce.run(p, {"ampersand", "segments"})
        return ([l for l in lines if l.get("type") == "citation"],
                [l for l in lines if l.get("type") == "unresolved_citation"],
                lines[-1])

    R_SG = ("\n\n## References\n\nSmith, J. (2020). A. J, 1, 1.\n"
            "Jones, K. (2019). B. J, 2, 1.\nFine, R. (1998). C. J, 3, 1.\n")

    # C-022. The type carries meaning: a bare year is a JSON INTEGER and a
    # suffixed one a string, so `2020` and `"2020"` are different groups.
    # Asserted on the serialized bytes, because "it is an array" is exactly
    # the claim a quoted string would also satisfy in Python.
    cits, _u, _s = sgk("As shown (Smith, 2020) here.", R_SG)
    key = cits[0]["citation_surface_group_key"]
    blob = _json.dumps(key, separators=(",", ":"), ensure_ascii=False)
    if blob != '["smith",2020]':
        failures.append(f"C-022: the key serializes as a JSON array with an "
                        f"integer year — got {blob}")
    elif not isinstance(key, list) or isinstance(key[1], str):
        failures.append(f"C-022: a bare year is an integer, not a string — "
                        f"got {key!r}")
    else:
        ok("C-022: the surface key is a JSON array, bare year an integer")

    # And the two shapes that are NOT integers.
    cits, _u, _s = sgk("See (Smith, n.d.) and (Smith, 2020a).", R_SG)
    got = [c["citation_surface_group_key"][1] for c in cits]
    if got != ["nd", "2020a"]:
        failures.append(f"C-022: a suffixed year and n.d. stay strings — "
                        f"got {got!r}")
    else:
        ok("C-022: a suffixed year and n.d. are strings, not integers")

    # C-023, and this is the point of the whole section. Normalization is
    # lower plus whitespace and NOTHING else, so two surfaces meaning one work
    # stay separate. Anything that collapsed them would be doing identity work
    # under an aggregation name.
    cits, _u, summ = sgk("As shown (Smith and Jones, 2020) and "
                         "(Smith & Jones, 2020) here.", R_SG)
    surfaces = [c["citation_surface_group_key"][0] for c in cits]
    if surfaces != ["smith and jones", "smith & jones"]:
        failures.append(f"C-023: `and` and `&` remain surface-distinct — "
                        f"got {surfaces!r}")
    elif summ["distinct_surface_groups"] != 2:
        failures.append(f"C-023: two surfaces, two groups — got "
                        f"{summ['distinct_surface_groups']}")
    else:
        ok("C-023: punctuation and `and`/`&` remain surface-distinct")

    # DISTINCT is the word doing the work, and the control above cannot see
    # it: two occurrences with two surfaces give 2 either way, so a count of
    # occurrences passes it. This repeats one surface, where the two figures
    # diverge — 2 parsed, 1 group. Added 22 September after the mutation probe
    # showed the occurrences-not-groups mutation surviving.
    cits, _u, summ = sgk("As shown (Smith, 2020) and later (Smith, 2020) "
                         "again.", R_SG)
    if len(cits) != 2:
        failures.append(f"§11: the repeated-surface fixture needs two "
                        f"occurrences — got {len(cits)}")
    elif summ["distinct_surface_groups"] != 1:
        failures.append(f"C-023: two occurrences of ONE surface is one "
                        f"group — got {summ['distinct_surface_groups']}")
    else:
        ok("C-023: the count is of distinct groups, not of occurrences")

    # §6.8 names this field as one the possessive strip MUST NOT touch.
    cits, _u, _s = sgk("Following Fine's (1998) formula, we did this.", R_SG)
    if "fine's" not in cits[0]["citation_surface_group_key"][0]:
        failures.append(f"§6.8: the possessive survives in the SURFACE key — "
                        f"got {cits[0]['citation_surface_group_key']!r}")
    elif cits[0]["citation_key"] != "fine|1998":
        failures.append(f"§6.8: the identity still strips it — got "
                        f"{cits[0]['citation_key']!r}")
    else:
        ok("§6.8: the possessive survives the surface key, not the identity")

    # C-024. The instrumentation assertion rc2 asks for, as a behavioural one:
    # two occurrences with DIFFERENT surface keys resolving to the SAME
    # identity is only possible if identity never consumed the surface key.
    cits, _u, _s = sgk("As shown (Smith and Jones, 2020) and "
                       "(Smith & Jones, 2020) here.", R_SG)
    ids = {c["citation_key"] for c in cits}
    sks = {tuple(c["citation_surface_group_key"]) for c in cits}
    if len(sks) != 2:
        failures.append("C-024: the fixture needs two distinct surface keys")
    elif ids != {"smith|2020"}:
        failures.append(f"C-024: identity must not vary with the surface key "
                        f"— got {ids}")
    else:
        ok("C-024: two surface groups, one identity — the key is not consumed")

    # C-025, and it is PARTIAL rather than met. "Always emitted" includes
    # bibliography-absent mode, which is C-009 and not implemented, so only
    # half the claim can be exercised. Both halves that CAN be are.
    cits, unres, summ = sgk("As shown (Smith, 2020) and (Nobody et al., "
                            "1899 BCE) here.", R_SG)
    if "distinct_surface_groups" not in summ:
        failures.append("C-025: distinct_surface_groups is always emitted")
    elif any("citation_surface_group_key" not in u for u in unres):
        failures.append("§12: an unresolved_citation carries the field too")
    elif any(u["citation_surface_group_key"] is not None for u in unres):
        failures.append("§12: and it is null there, having no author phrase")
    else:
        ok("C-025: the summary count and the null on unresolved records")

    # ---- rc2 §10 and §11.3, bibliography-absent mode ----
    #
    # This case used to live in the aborts block expecting exit 3. rc2 §14
    # allocates exit 3 to "invalid section map" and gives a missing
    # bibliography no exit at all: §10 processes the manuscript instead.
    # Refusing it threw away every citation in the document to report one
    # thing about the bibliography, which is the shape of the defect that
    # cost this corpus four papers and 582 citations until 19 September.
    print("\nrc2 §10 / §11.3 — bibliography-absent mode")

    def absent(body_text):
        """Catches Abort deliberately: the whole point of §10 is that there
        is no longer an abort here, so a control that let one propagate would
        report a crash where it should report a failure."""
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text, encoding="utf-8")
            try:
                lines, code = ce.run(p, {"ampersand", "segments"})
            except ce.Abort as a:
                return None, a.code, {}
        return lines, code, lines[-1]

    lines, code, summ = absent("As shown (Smith, 2020) here.")
    if lines is None:
        failures.append(f"§10: a manuscript with no bibliography is still "
                        f"READ — got abort exit {code}, and rc2 §14 has no "
                        f"exit for a missing bibliography")
        lines, cit = [], None
    cit = next((l for l in lines if l.get("type") == "citation"), None)
    if lines and cit is None:
        failures.append("§10: a manuscript with no bibliography is still "
                        "READ — Pass 1 extraction is performed")
    elif summ["references_source"] != "not_available":
        failures.append(f"C-009: references_source is not_available — got "
                        f"{summ['references_source']!r}")
    elif not any(l.get("type") == "bibliography_absent" for l in lines):
        failures.append("C-009: exactly one bibliography_absent record")
    else:
        ok("§10: no bibliography is processed, not refused")

    # C-066, and the distinction the whole section turns on.
    if cit is None:
        failures.append("C-066: no citation to check, see above")
    elif cit["author_resolution"] != "not_evaluated":
        failures.append(f"C-066: author_resolution is not_evaluated, which is "
                        f"NOT not_resolved — got {cit['author_resolution']!r}")
    elif cit["identity_class"] != "not_evaluated":
        failures.append(f"C-066: the identity state says not_evaluated — got "
                        f"{cit['identity_class']!r}")
    elif cit["author_kind"] != "undetermined" or cit["citation_key"] is not None:
        failures.append("C-066: undetermined kind, null key")
    elif cit["citation_surface_group_key"] is None:
        failures.append("C-025: citation_surface_group_key stays COMPUTED — "
                        "it is a surface property and never needed the "
                        "bibliography")
    else:
        ok("C-066: not_evaluated is a different state from not_resolved")

    # §10's suppression list, all nine. Emitting any of them would be claiming
    # a reconciliation that never ran.
    forbidden = {"reference", "unresolved_reference",
                 "ambiguous_author_resolution", "missing_reference",
                 "uncited_reference", "duplicate_reference_key",
                 "ambiguous_citation", "possible_mismatch",
                 "author_structure_mismatch"}
    lines2, _c, _s = absent("As shown (Smith, 2020; Jones, 2019) and "
                            "Brown (2018) argued this.")
    leaked = sorted({l["type"] for l in lines2} & forbidden)
    if leaked:
        failures.append(f"§10: these MUST NOT be emitted with no "
                        f"bibliography — got {leaked}")
    else:
        ok("§10: all nine reconciliation record types are suppressed")

    # C-067. `0` is a measurement; `null` is the absence of one. A reader
    # averaging match rates across a corpus has to be able to tell them apart.
    # rc2 §11.3's list, PARSED out of rc2 rather than retyped. The hand-typed
    # version of this tuple was wrong twice in one day: the consolidation
    # document counted the section's fields as eight, a correction counted them
    # as ten-null, and the truth is nine null and one zero. Two people counting
    # by eye got two different wrong answers, so the list is generated.
    #
    # `resolved_citation_occurrences` is deliberately excluded: §11.3 sets it to
    # `0`, not null, because zero citations WERE resolved and that is a
    # measurement. Asserting it null would contradict the section.
    spec113 = rc2_section("11.3")
    nulled = tuple(l.split("=")[0].strip() for l in spec113
                   if l.strip().endswith("null"))
    if len(nulled) != 9:
        failures.append(f"C-067: expected nine null fields in rc2 §11.3, "
                        f"parsed {len(nulled)} — the section moved or the "
                        f"parse is wrong, and either way this control is not "
                        f"checking what it says")
    # `author_structure_mismatches` is not rc2's; it is this file's extra, and
    # §11.3's reasoning applies to it for the same reason.
    nulled = nulled + ("author_structure_mismatches",)
    wrong = [k for k in nulled if summ.get(k, "missing") is not None]
    if wrong:
        failures.append(f"C-067: not-evaluated quantities are null, never 0 — "
                        f"got {[(k, summ[k]) for k in wrong]}")
    elif summ["identity_resolution_performed"] is not False:
        failures.append("§11.4: identity_resolution_performed says so plainly")
    elif summ["parsed"] != 1 or summ["distinct_surface_groups"] != 1:
        failures.append(f"§11.1: extraction figures are REAL, not null — "
                        f"Pass 1 ran. Got parsed={summ['parsed']}")
    else:
        ok("C-067: identity counts null, extraction counts real")

    # The other two sources, so the field is not just a constant.
    lines3, _c, s3 = absent("Smith (2020) argued this.\n\n## References\n\n"
                            "Smith, J. (2020). A paper. Journal, 1(1), 1-10.\n")
    if s3["references_source"] != "detected":
        failures.append(f"C-006: a marked-up heading is `detected` — got "
                        f"{s3['references_source']!r}")
    else:
        ok("C-006: a marked-up References heading reports detected")

    # ---- rc2 §13 and §12.1, file output and canonical bytes ----
    #
    # Every control here compares BYTES. §12.1's clauses are byte properties —
    # UTF-8, no BOM, LF only, exactly one trailing LF — and a test that parses
    # the lines back cannot see any of them. That is not hypothetical: until
    # 22 September the stream went out through `print()`, which on Windows
    # translates LF to CRLF, so every run on the author's machine violated
    # §12.1 and no control noticed.
    print("\nrc2 §13 / §12.1 — file output and canonical bytes")

    # In-process rather than subprocess, and the reason is the mutation probe
    # rather than taste. Six spawns per suite run, times roughly a hundred
    # mutations, took the probe past its timeout — and a probe that cannot
    # finish checks nothing. `main()` is the real entry point either way; only
    # the process boundary is dropped.
    import io as _io

    class _Result:
        __slots__ = ("stdout", "returncode")

        def __init__(self, stdout, returncode):
            self.stdout, self.returncode = stdout, returncode

    class _BinStdout:
        """Stands in for sys.stdout, carrying the .buffer main() writes to.

        `write` MODELS A WINDOWS TEXT LAYER: it translates LF to CRLF, exactly
        as text-mode stdout does there. Writes through `.buffer` are binary and
        untranslated, which is the distinction §12.1 turns on.

        Without this the two paths are indistinguishable on Linux — encoding a
        string and writing bytes give the same result — so the mutation that
        replaces `sys.stdout.buffer.write(payload)` with `print(...)` SURVIVED.
        That is the defect this file carried until 22 September, when every run
        on the author's Windows machine was emitting the CRLF §12.1 forbids,
        invisible on Linux and invisible to any test that parsed the lines back.
        A platform-specific defect nothing can catch on the other platform is
        one that comes back.
        """

        def __init__(self):
            self.buffer = _io.BytesIO()

        def write(self, s):
            self.buffer.write(s.encode("utf-8").replace(b"\n", b"\r\n"))

        def flush(self):
            pass

    def cli(args):
        cap, old_out, old_argv = _BinStdout(), sys.stdout, sys.argv
        sys.stdout, sys.argv = cap, [str(Path(ce.__file__))] + args
        try:
            code = ce.main()
        finally:
            sys.stdout, sys.argv = old_out, old_argv
        return _Result(cap.buffer.getvalue(), code)

    with _tf.TemporaryDirectory() as td:
        d = Path(td)
        paper = d / "paper.md"
        paper.write_text(HEAD + "As shown (Smith, 2020) and Müller (2019).\n"
                         "\n\n## References\n\nSmith, J. (2020). A. J, 1, 1.\n"
                         "Müller, K. (2019). B. J, 2, 1.\n", encoding="utf-8")

        r1 = cli([str(paper), "--fix", "all"])
        out_file = d / "explicit.jsonl"
        r2 = cli([str(paper), "--fix", "all", "--out", str(out_file)])

        # C-071. "writes the byte-identical canonical stream that would be
        # written to stdout" — so the comparison is the file against stdout,
        # not the file against a re-serialization of it.
        if not out_file.exists():
            failures.append("C-071: --out wrote no file")
        elif out_file.read_bytes() != r1.stdout:
            failures.append("C-071: --out bytes differ from stdout bytes")
        elif r2.stdout != r1.stdout:
            failures.append("C-071: asking for --out changed stdout")
        else:
            ok("C-071: --out and stdout are byte-identical")

        # §12.1, the four byte properties.
        b = r1.stdout
        if b.startswith(b"\xef\xbb\xbf"):
            failures.append("§12.1: no BOM")
        elif b"\r" in b:
            failures.append("§12.1: LF line ending only — found a CR. On "
                            "Windows this is what text-mode stdout does")
        elif not b.endswith(b"\n") or b.endswith(b"\n\n"):
            failures.append("§12.1: the final line ends with exactly one LF")
        elif b"\n\n" in b:
            failures.append("§12.1: no blank lines")
        else:
            ok("§12.1: UTF-8, no BOM, LF only, one trailing LF")

        # "non-ASCII characters emitted raw" — not \u escapes.
        if b"M\xc3\xbcller" not in b:
            failures.append("§12.1: non-ASCII is emitted raw, not escaped")
        else:
            ok("§12.1: non-ASCII characters are emitted raw")

        # C-072. The name is content-derived, so the same manuscript always
        # publishes to the same filename and a different one never collides.
        dirtarget = d / "bydir"
        dirtarget.mkdir()
        cli([str(paper), "--fix", "all", "--out", str(dirtarget)])
        written = sorted(p.name for p in dirtarget.iterdir())
        meta = _json.loads(r1.stdout.split(b"\n")[0].decode("utf-8"))
        want = f"{meta['canonical_sha256']}.citations.jsonl"
        if written != [want]:
            failures.append(f"C-072: a directory target names the file "
                            f"<canonical_sha256>.citations.jsonl — got "
                            f"{written}")
        elif (dirtarget / want).read_bytes() != r1.stdout:
            failures.append("C-072: and it carries the same bytes")
        else:
            ok("C-072: a directory target is named for canonical_sha256")

        # And the digest is over the INPUT, not the output — §2's
        # canonical_manuscript_bytes, which is what makes the name stable.
        import hashlib as _hl
        canon = ce.normalise(paper.read_bytes()).encode("utf-8")
        if meta["canonical_sha256"] != _hl.sha256(canon).hexdigest():
            failures.append("§2: canonical_sha256 is over the normalised "
                            "INPUT bytes, not over the output")
        else:
            ok("§2: canonical_sha256 is over canonical_manuscript_bytes")

        # C-073. "no partial authoritative file". The scratch file lives in
        # the destination directory so the rename is atomic, and it must not
        # survive the run.
        leftovers = [p.name for p in dirtarget.iterdir()
                     if p.name.startswith(".citations-")
                     or p.name.endswith(".tmp")]
        if leftovers:
            failures.append(f"C-073: publication left scratch files behind — "
                            f"{leftovers}")
        else:
            ok("C-073: atomic publication leaves no scratch file")

        # §13: "For exits 2-5, the two-line error stream is written to the
        # requested file as the authoritative error artifact." An abort must
        # not leave a previous run's normal output sitting at the target.
        bad = d / "bad.md"
        bad.write_bytes(b"# A\n\ntext\n\n# B\n\nmore\n")      # exit 4
        reused = d / "reused.jsonl"
        cli([str(paper), "--fix", "all", "--out", str(reused)])
        before = reused.read_bytes()
        rb = cli([str(bad), "--fix", "all", "--out", str(reused)])
        after = reused.read_bytes()
        if rb.returncode != 4:
            failures.append(f"§13: the fixture should abort 4, got "
                            f"{rb.returncode}")
        elif after == before:
            failures.append("§13: an abort left the previous normal artifact "
                            "in place; the error stream is authoritative")
        elif len(after.rstrip(b"\n").split(b"\n")) != 2:
            failures.append(f"§13: exits 2-5 write EXACTLY the two-line error "
                            f"stream — got {len(after.split(chr(10).encode()))}")
        elif after != rb.stdout:
            failures.append("§13: the file and stdout carry the same bytes "
                            "on the abort path too")
        else:
            ok("§13: an abort publishes the two-line error stream, not a "
               "partial artifact")

        # ---- §12.2, block order ----
        #
        #     Empty blocks emit nothing. Blocks never interleave.
        #
        # Both halves are checked. "Never interleave" is the one that was
        # being broken: the two §9.4 diagnostics shared a list, so
        # missing_reference reopened seven times on paper ad1e3ff9 until
        # 22 September.
        SPEC_ORDER = ["meta", "citation", "unresolved_citation",
                      "excluded_candidate", "citation_error",
                      "bibliography_absent", "reference",
                      "unresolved_reference", "ambiguous_author_resolution",
                      "missing_reference", "uncited_reference",
                      "duplicate_reference_key", "ambiguous_citation",
                      "possible_mismatch", "author_structure_mismatch",
                      "summary"]

        def block_order(payload):
            seen, order, reopened = set(), [], []
            for ln in payload.rstrip(b"\n").split(b"\n"):
                t = _json.loads(ln.decode("utf-8"))["type"]
                if t not in seen:
                    seen.add(t)
                    order.append(t)
                elif order[-1] != t:
                    reopened.append(t)
            return order, reopened

        # A fixture producing BOTH §9.4 diagnostics, so the interleaving this
        # control exists for is reachable. Built rather than hunted from the
        # corpus: the first version searched `data/md_full` relative to
        # ce.__file__, which resolves to a temp directory once the mutation
        # probe copies the module, so the control failed for a reason that had
        # nothing to do with block order.
        # `(Felfe, 2006)` against two 2006 Felfe entries is here for §12.3's
        # sake rather than §12.2's: it is the only way to get an
        # `ambiguous_citation` record into the fixture, and without one that
        # record type is absent from `rec_by_type` and skipped entirely. The
        # mutation renaming its `citation_key` back to rc1's `candidate_key`
        # SURVIVED until this line was added — the control could not see a
        # record the document never produced.
        mixed = d / "mixed.md"
        mixed.write_text(
            HEAD + "As shown (Whiteman, 2000) and (Smith, 2020) and "
            "(Adams and Boyle, 2015) and (Felfe, 2006) here.\n\n"
            "## References\n\n"
            "Whitman, R. (2000). Pairs by edit distance. J, 1, 1.\n"
            "Adams, J. (2015). One author, cited as two. J, 2, 1.\n"
            "Felfe, J. (2006). One work. J, 7, 1.\n"
            "Felfe, J. (2006). A different work, same key. J, 8, 1.\n"
            "Jones, K. (2019). A. J, 3, 1.\nBrown, L. (2018). B. J, 4, 1.\n"
            "Davis, M. (2017). C. J, 5, 1.\nEvans, N. (2016). D. J, 6, 1.\n",
            encoding="utf-8")
        ls, _c = ce.run(mixed, {"ampersand", "segments"})
        got = {x["type"] for x in ls}
        # Three blocks have to be non-empty or the control cannot see their
        # order: the two §9.4 diagnostics, and author_structure_mismatch,
        # which §12.2 puts LAST and which this implementation was emitting
        # fourth. An empty block is unordered by definition.
        need = {"possible_mismatch", "missing_reference",
                "author_structure_mismatch"}
        if not need <= got:
            failures.append(f"§12.2: the fixture must populate {sorted(need)} "
                            f"for their order to be observable — got "
                            f"{sorted(got & need)}")
        else:
            order, reopened = block_order(ce.serialize(ls))
            if reopened:
                failures.append(f"§12.2: blocks never interleave — these "
                                f"reopened: {sorted(set(reopened))}")
            elif [t for t in order if t in SPEC_ORDER] != \
                    [t for t in SPEC_ORDER if t in order]:
                failures.append(f"§12.2: block order — got {order}")
            else:
                ok("§12.2: blocks are in order and never interleave")

        # ---- §12.3, declared key order per record ----
        #
        #     keys in the exact order declared for each record below
        #
        # Read off the serialized BYTES, not off the dicts, because the order
        # only exists once the record is written. json.loads preserves it, so
        # the comparison is against what a reader of the file would see.
        #
        # This asserts rc2's declared keys come first, in rc2's order. It does
        # NOT assert the record stops there: this implementation carries
        # `candidate_state`, `stop_reduced_phrase` and the two candidate keys
        # beyond what rc2 declares, so a byte golden against rc2 would still
        # differ on the tail. That is why C-068 stays PARTIAL.
        declared_by_type = rc2_declared()
        if declared_by_type:
            # `summary` used to be excluded here alongside `meta`, because its
            # field SET differed and not just its order — rc2's
            # `uniquely_matched_*` against v3.3's `matched_*`, and twelve rc2
            # fields this file did not emit. All twenty-one landed on
            # 23 September, so the summary is checked like any other record.
            #
            # `meta` came in on 23 September and is no longer excluded. It was
            # v3.3's one-field form while the question "which specification
            # does this output declare governs it" was open. The answer turned
            # out not to need asking: the rules implemented ARE rc2's and
            # rc3's, so `3.3` was not an undecided label, it was a wrong one.
            #
            # rc2's `meta` example carries two forms, the full §12.2 envelope
            # and §14's two-field error-stream version. Both are keyed `meta`,
            # so `rc2_declared` keeps the FIRST it meets, which is the full
            # one. The error stream's shape is checked by §13's own controls.
            pass

        rec_by_type = {}
        for ln in ce.serialize(ls).rstrip(b"\n").split(b"\n"):
            r = _json.loads(ln.decode("utf-8"))
            rec_by_type.setdefault(r["type"], r)

        if not declared_by_type:
            failures.append("§12.3: rc2's execution-conformance document was "
                            "not found, so the declared order could not be "
                            "read. Not passing on a check that did not run")
        else:
            # `want` filters rc2's declared keys down to the ones the record
            # actually has, and then checks their ORDER. That was the whole
            # check until 23 September, and it meant a declared field this
            # file never emitted passed silently: filtered out of `want`,
            # never compared, never reported.
            #
            # Twelve fields were absent that way across five record types —
            # `identity_authority` and `example` on both candidate-level
            # diagnostics, `evidence`, `citation_key` on `ambiguous_citation`,
            # `reference_index` on `author_structure_mismatch`, and meta's
            # four. The control was green, named §12.3, and tested order only.
            # So `absent` is now reported separately from `bad`.
            bad, absent = [], []
            for t, declared in declared_by_type.items():
                r = rec_by_type.get(t)
                if r is None:
                    continue
                gone = [k for k in declared if k not in r]
                if gone:
                    absent.append(f"{t}: {gone}")
                want = [k for k in declared if k in r]
                if list(r)[:len(want)] != want:
                    bad.append(f"{t}: got {list(r)[:len(want)]}, want {want}")
            checked = [t for t in declared_by_type if t in rec_by_type]
            if absent:
                failures.append("§12.3: rc2 declares fields this file does not "
                                "emit — " + "; ".join(absent))
            elif bad:
                failures.append("§12.3: declared key order — " + "; ".join(bad))
            elif "citation" not in rec_by_type or "reference" not in rec_by_type:
                failures.append("§12.3: the fixture must carry both a citation "
                                "and a reference for this to check anything")
            else:
                ok(f"§12.3: {len(checked)} record types lead with the key "
                   f"order rc2's own document declares")

        # The two fields rc2 declares and this file did not emit until
        # 22 September. `surname` held the right value under a name that
        # stops being accurate for an institutional entry.
        ref = rec_by_type.get("reference")
        if ref is not None and "identity_author_phrase" not in ref:
            failures.append("§7.4: the reference's identity field is named "
                            "identity_author_phrase, not surname")
        elif ref is not None and "surname" in ref:
            failures.append("§7.4: `surname` should be gone from reference "
                            "records, not carried alongside")
        else:
            ok("§7.4: references carry identity_author_phrase")

        # ---- §12.4, total deterministic order ----
        #
        #     Every block MUST have a total deterministic ordering; two
        #     distinct records may not remain tied on every declared key.
        #
        # C-070 is the reachable instance. Extraction walks left to right, so
        # (group_start, segment_start) is ascending by construction and the
        # `year` key that breaks a tie within one group was never applied:
        # `(Smith, 2021, 2020)` emitted 2021 first until 22 September.
        multi = d / "multi.md"
        for order in (("2020", "2021"), ("2021", "2020")):
            multi.write_text(
                HEAD + f"As shown (Smith, {order[0]}, {order[1]}) here."
                "\n\n## References\n\nSmith, J. (2020). A. J, 1, 1.\n"
                "Smith, J. (2021). B. J, 2, 1.\n", encoding="utf-8")
            ls, _c = ce.run(multi, {"ampersand", "segments"})
            years = [x["year"] for x in ls if x.get("type") == "citation"]
            if years != ["2020", "2021"]:
                failures.append(f"C-070: two years in one segment order by "
                                f"year, whichever way the manuscript writes "
                                f"them — source {order} gave {years}")
                break
        else:
            ok("C-070: multi-year citations order by year, not by source")

        # §12.4's invariant itself, over a real paper: no two records of the
        # same type may be tied on every declared key. Checked for the two
        # blocks whose keys this implementation can evaluate.
        ls, _c = ce.run(paper, {"ampersand", "segments"})
        keyed = [(x["group_start"], x["segment_start"], x["year"],
                  _json.dumps(x["citation_surface_group_key"],
                              separators=(",", ":"), ensure_ascii=False))
                 for x in ls if x.get("type") == "citation"]
        if len(keyed) != len(set(keyed)):
            failures.append("§12.4: two citation records are tied on every "
                            "declared key")
        elif keyed != sorted(keyed):
            failures.append("§12.4: citations are not in the declared order")
        else:
            ok("§12.4: citations are totally ordered, no two tied")

        # ---- C-030 and §7.3's closed suspect_reasons list ----
        #
        # "In press." is a real reference whose year does not exist yet. It
        # was emitted as a `reference` row with a null key carrying `no_year`
        # in suspect_reasons — but C-030 says "no reference row/key", and
        # §7.3 closes suspect_reasons at three, none of them no_year.
        inpress = d / "inpress.md"
        inpress.write_text(
            HEAD + "As shown (Smith, 2020) here.\n\n## References\n\n"
            "Smith, J. (2020). A paper. Journal, 1(1), 1-10.\n"
            "Bhattacharjee, A., Dana, J., & Baron, J. In press. Anti-profit "
            "beliefs. Journal of Personality.\n", encoding="utf-8")
        ls, _c = ce.run(inpress, {"ampersand", "segments"})
        refs_out = [x for x in ls if x.get("type") == "reference"]
        urefs = [x for x in ls if x.get("type") == "unresolved_reference"]
        if any("no_year" in (r.get("suspect_reasons") or []) for r in refs_out):
            failures.append("§7.3: suspect_reasons is closed at terminator, "
                            "overlong, embedded_entry_pattern — no_year is "
                            "not one of them")
        elif any(r["reference_key"] is None for r in refs_out):
            failures.append("C-030: a no-year entry produces no reference "
                            "row and no key")
        elif [u["reason"] for u in urefs] != ["no_year"]:
            failures.append(f"C-030: it emits unresolved_reference(no_year) — "
                            f"got {[u['reason'] for u in urefs]}")
        else:
            ok("C-030: a no-year entry is unresolved, not a keyless reference")

        # C-032, the order. rc2 numbers them 1 terminator, 2 overlong,
        # 3 embedded_entry_pattern, and a closed ORDERED list is only closed
        # if nothing else gets in.
        SUSPECT = ["terminator", "overlong", "embedded_entry_pattern"]
        ls, _c = ce.run(paper, {"ampersand", "segments"})
        offenders = []
        for r in (x for x in ls if x.get("type") == "reference"):
            rs = r.get("suspect_reasons") or []
            if [x for x in rs if x in SUSPECT] != [x for x in SUSPECT
                                                   if x in rs]:
                offenders.append(rs)
            elif set(rs) - set(SUSPECT):
                offenders.append(rs)
        if offenders:
            failures.append(f"C-032: suspect_reasons are the closed three, in "
                            f"§7.3's order — got {offenders[:3]}")
        else:
            ok("C-032: suspect_reasons are closed and ordered")

        # C-083. Same input, two runs, byte-identical output. The strongest
        # determinism statement available, and it costs one more process.
        r3 = cli([str(paper), "--fix", "all"])
        if r3.stdout != r1.stdout:
            failures.append("C-083: two runs over the same input produced "
                            "different bytes")
        else:
            ok("C-083: the same input produces byte-identical output twice")

    # ---- rc2 §5 and §6, the sentence-relative fields ----
    print("\nrc2 §5 / §6 — sentence-relative fields")

    with _tf.TemporaryDirectory() as td:
        sp = Path(td) / "paper.md"
        sp.write_text(
            HEAD + "First sentence here.\n\n(Smith, 2020).\n\n"
            "More text follows (Jones, 2019).\n\n## Method\n\n"
            "After a heading, text (Brown, 2018) continues."
            "\n\n## References\n\nSmith, J. (2020). A. J, 1, 1.\n"
            "Jones, K. (2019). B. J, 2, 1.\nBrown, L. (2018). C. J, 3, 1.\n",
            encoding="utf-8")
        ls, _c = ce.run(sp, {"ampersand", "segments"})
    sc = [l for l in ls if l.get("type") == "citation"]

    # C-026. "0-based ordinal among body sentences, continuous across
    # sections" — the counter does not restart at a heading, and `## Method`
    # sits between the second and third of these.
    if [c["sentence_index"] for c in sc] != [1, 2, 3]:
        failures.append(f"C-026: sentence_index is continuous across "
                        f"headings — got {[c['sentence_index'] for c in sc]}")
    else:
        ok("C-026: sentence_index continues across a heading")

    # C-027. "previous sentence content_end, or null for the first body
    # sentence." None of these is the first sentence, so all three carry a
    # value; the null case needs its own fixture below.
    # The value is the PREVIOUS sentence's content_end, which is necessarily
    # before this sentence begins. Checking that it merely ascends is not
    # enough: pointing each record at its OWN content_end also ascends, and
    # the mutation probe caught that control passing.
    if any(c["previous_sentence_end"] is None for c in sc):
        failures.append("C-027: only the FIRST body sentence has a null "
                        "previous_sentence_end")
    elif any(c["previous_sentence_end"] >= c["sentence_start"] for c in sc):
        failures.append(
            f"C-027: previous_sentence_end is the PRIOR sentence's "
            f"content_end, so it precedes this sentence's start — got "
            f"{[(c['previous_sentence_end'], c['sentence_start']) for c in sc]}")
    else:
        ok("C-027: previous_sentence_end carries the prior content_end")

    with _tf.TemporaryDirectory() as td:
        sp = Path(td) / "paper.md"
        sp.write_text(HEAD + "(Smith, 2020) opens the body.\n\n"
                      "## References\n\nSmith, J. (2020). A. J, 1, 1.\n",
                      encoding="utf-8")
        ls, _c = ce.run(sp, {"ampersand", "segments"})
    first = next(l for l in ls if l.get("type") == "citation")
    if first["previous_sentence_end"] is not None:
        failures.append(f"C-027: the first body sentence has null — got "
                        f"{first['previous_sentence_end']!r}")
    elif first["sentence_index"] != 0:
        failures.append(f"C-026: the first body sentence is index 0 — got "
                        f"{first['sentence_index']}")
    # `(Smith, 2020) opens the body.` STARTS its sentence and does not end it.
    # That pairing is what separates `standalone` from `sentence_position ==
    # start`, and the first fixture had no case of it — so dropping the
    # end-condition from standalone changed nothing there, and the probe
    # reported the mutation surviving.
    elif first["sentence_position"] != "start":
        failures.append("C-028: this fixture must START the sentence for the "
                        "next check to discriminate")
    elif first["standalone"]:
        failures.append("C-028: standalone needs BOTH ends; starting the "
                        "sentence is not enough")
    else:
        ok("C-027/C-028: first sentence null, and start alone is not "
           "standalone")

    # C-028. "standalone = true iff group_start == sentence_start AND
    # group_end == content_end", and §6 says what it is NOT: "positional
    # only. It does not infer which claim the citation supports."
    #
    # `(Smith, 2020).` is its own paragraph and so its own sentence. The
    # other two sit inside sentences with prose either side.
    if [c["standalone"] for c in sc] != [True, False, False]:
        failures.append(f"C-028: standalone is the citation-only sentence — "
                        f"got {[c['standalone'] for c in sc]}")
    elif sc[0]["sentence_position"] != "start":
        failures.append("C-028: a standalone citation also starts its "
                        "sentence")
    else:
        ok("C-028: standalone marks the citation-only sentence")

    # ---- rc2 §15, the invariant-injection seam ----
    #
    # The `From Tether` fixture above reaches row 6 through real parsing, which
    # is worth keeping as an integration check. It is NOT how rc2 says to
    # execute these cases: the matrix marks C-042 to C-047 `injection` in its
    # Evidence column, and §15 exists because those states are not
    # manuscript-reachable. Contriving a manuscript was doing by hand what the
    # spec provides a seam for.
    print("\nrc2 §15 — the invariant-injection seam")

    INJ_BODY = "As shown (Smith, 2020) here."
    INJ_REFS = ("\n\n## References\n\nSmith, J. (2020). A paper. Journal, "
                "1(1), 1-10.\n")

    def inject(full, reduced):
        """Bind the seam, run, unbind. Returns (lines, abort_args)."""
        ce._RESOLVER_SEAM = lambda _f, _s: (full, reduced)
        try:
            with _tf.TemporaryDirectory() as td:
                p = Path(td) / "paper.md"
                p.write_text(HEAD + INJ_BODY + INJ_REFS, encoding="utf-8")
                return ce.run(p, {"ampersand", "segments"})[0], None
        except ce.Abort as e:
            return None, e.args
        finally:
            ce._RESOLVER_SEAM = None

    # C-042 to C-045: every non-no_match pair with different keys is the same
    # outcome. Four cases, four state pairs, one branch — and now each pair is
    # actually exercised rather than one standing in for four.
    pairs = [("C-042 unique/unique", ("a|2020", "unique", [0]),
              ("b|2020", "unique", [1])),
             ("C-043 unique/nonunique", ("a|2020", "unique", [0]),
              ("b|2020", "nonunique", [1, 2])),
             ("C-044 nonunique/unique", ("a|2020", "nonunique", [0, 1]),
              ("b|2020", "unique", [2])),
             ("C-045 nonunique/nonunique", ("a|2020", "nonunique", [0, 1]),
              ("b|2020", "nonunique", [2, 3]))]
    bad = []
    for label, f, s in pairs:
        lines, ab = inject(f, s)
        if ab:
            bad.append(f"{label} aborted: {ab}")
            continue
        c = next((l for l in lines if l.get("type") == "citation"), None)
        aar = [l for l in lines
               if l.get("type") == "ambiguous_author_resolution"]
        if c is None or c["author_resolution"] != "ambiguous":
            bad.append(f"{label} → {c and c['author_resolution']!r}")
        elif len(aar) != 1 or c["citation_key"] is not None:
            bad.append(f"{label}: one record, no key — got {len(aar)}, "
                       f"{c['citation_key']!r}")
    if bad:
        failures.append("§8.3 rows 6-9 by injection: " + "; ".join(bad))
    else:
        ok("§15: all four different-key state pairs → ambiguous")

    # C-047, and it is the one that would be easy to get wrong. Two DIFFERENT
    # candidate keys naming the SAME reference index is explicitly "permitted
    # and remains ordinary author-resolution ambiguity" — not exit 6. An
    # implementation that guarded on overlapping indices instead of on equal
    # keys passes every other case here and fails this one.
    lines, ab = inject(("a|2020", "unique", [0]), ("b|2020", "unique", [0]))
    if ab:
        failures.append(f"C-047: a shared reference index across different "
                        f"candidate keys must NOT abort — got exit {ab[0]}")
    else:
        c = next(l for l in lines if l.get("type") == "citation")
        if c["author_resolution"] != "ambiguous":
            failures.append(f"C-047: shared index is ordinary ambiguity — got "
                            f"{c['author_resolution']!r}")
        else:
            ok("C-047: a shared reference index is ambiguity, not exit 6")

    # §15's mandatory case, verbatim: "sets both candidates to non-empty
    # results with the same candidate_key; expected result = exit 6".
    lines, ab = inject(("a|2020", "unique", [0]), ("a|2020", "unique", [1]))
    if not ab:
        failures.append("§8.6: two non-empty lookups with the SAME "
                        "candidate_key must abort")
    elif ab[0] != 6:
        failures.append(f"§8.6: exit 6, got {ab[0]}")
    elif ab[1] != "same_candidate_identity_double_resolution":
        failures.append(f"§8.6: rc2 names the reason — got {ab[1]!r}")
    else:
        ok("§15/§8.6: same candidate_key on both lookups → exit 6")

    # "It MUST NOT alter Pass-1 parsing; candidate spans; ..." The seam sits
    # after extraction, so this is structural — pinned anyway, because the
    # seam's whole licence is that it cannot reach backwards.
    lines, _ab = inject(("a|2020", "no_match", []), ("b|2020", "no_match", []))
    c = next(l for l in lines if l.get("type") == "citation")
    if c["author_phrase"] != "Smith" or c["group_start"] is None:
        failures.append(f"§15: the seam must not alter Pass-1 parsing or "
                        f"candidate spans — got {c['author_phrase']!r}")
    else:
        ok("§15: injection leaves Pass-1 parsing and spans untouched")

    # "It MUST NOT be reachable through CLI flags, environment variables,
    # config files, API parameters." The seam is a module attribute the
    # harness rebinds; nothing on the command line can name it.
    if ce._RESOLVER_SEAM is not None:
        failures.append("§15: the seam is left bound after use; production "
                        "must bind the real resolver")
    elif "seam" in open(Path(ce.__file__)).read().split("def main()")[1]:
        failures.append("§15: main() mentions the seam, so a flag could "
                        "reach it")
    else:
        ok("§15: no CLI path can bind the seam, and it is unbound by default")

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
        if len(pm) != 1 or pm[0]["evidence"] != rule:
            failures.append(f"§9.4 {label}: expected one possible_mismatch "
                            f"with rule {rule} — got "
                            f"{[(x['rule']) for x in pm]}, {len(mr)} missing")
            break
    else:
        ok("§9.4: all three repair rules pair their reference")

    # REFERENCE order decides, not rule order. This control was written
    # rule-major first and failed against a correct implementation.
    #
    # rc2 originally listed the rules "in precedence order" and said "take the
    # first rule that matches", which read as though a contest between rules
    # could arise. It cannot, and Alex Zamurko amended §9.4 on 21 September to
    # say so: a pair qualifies when EXACTLY ONE rule matches, and ordering
    # applies to the reference scan only.
    #
    # Why two rules can never match one reference, as a proof rather than the
    # 1500-2099 enumeration first offered:
    #
    #   rule 1 vs 2 and 3   rule 1 requires cand_phrase != ref_phrase;
    #                       rules 2 and 3 require them exactly equal
    #   rule 2 vs rule 3    swapping digits at places a and b shifts the value
    #                       by (d_a - d_b) * (10^a - 10^b), and 10^a - 10^b is
    #                       a multiple of 9 for every a != b. So a
    #                       transposition always moves a number by a multiple
    #                       of 9 and can never move it by 1.
    #
    # That holds for digit strings of any length, not just four-digit years.
    # So `len(matched) >= 2` in repair_rule is unreachable, and no control
    # pins it — a control for a branch that cannot be entered would be green
    # for a reason other than the one it names, which is the defect this file
    # exists to catch.
    mr, pm = diag("As shown (Whiteman, 2000) here.",
                  "\n\n## References\n\nWhiteman, R. (1999). Year adjacent. "
                  "J, 1, 1.\nWhitman, R. (2000). Edit distance. J, 2, 1.\n"
                  + PAD)
    if len(pm) != 1:
        failures.append(f"§9.4: one candidate pairs at most once — got "
                        f"{len(pm)}")
    elif pm[0]["evidence"] != "year_adjacent":
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

    # The amendment's own words, pinned. A transposition shifts a number by a
    # multiple of 9, so rules 2 and 3 cannot both match; verified here over
    # every digit string of length 2 to 5 rather than asserted from the
    # algebra alone.
    both = [(s, t) for L in range(2, 6)
            for n in range(10 ** (L - 1), 10 ** L)
            for s in (str(n),)
            for i in range(L - 1) if s[i] != s[i + 1]
            for t in (s[:i] + s[i + 1] + s[i] + s[i + 2:],)
            if abs(int(t) - int(s)) == 1]
    if both:
        failures.append(f"§9.4: a transposition that is also year_adjacent "
                        f"would make two rules match — found {both[:3]}")
    elif ce.repair_rule("person", "smith", "2000", "person", "smith", "2000"):
        failures.append("§9.4: equal phrase and equal year matches no rule, "
                        "so the pair does not qualify")
    else:
        ok("§9.4: EXACTLY ONE rule can match, so no pair is ever ambiguous")

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
    # Was `citation_key is None and author_kind is None`. rc2 §12.3 removes
    # both fields from this record and puts `identity_authority: "candidate"`
    # in their place, which is a stronger statement of the same rule: an absent
    # field cannot be read as an unestablished one, and the literal says
    # positively what authority the record has rather than leaving a reader to
    # infer it from two nulls.
    elif "citation_key" in mr[0] or "author_kind" in mr[0]:
        failures.append(f"§9.4/§12.3: this record must not carry citation_key "
                        f"or author_kind at all — got {sorted(mr[0])}")
    elif mr[0].get("identity_authority") != "candidate":
        failures.append(f"§12.3: identity_authority is the literal "
                        f"'candidate' — got {mr[0].get('identity_authority')!r}")
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
    elif "citation_key" in pm[0] or "author_kind" in pm[0]:
        failures.append(f"§9.4/§12.3: a possible_mismatch must not carry "
                        f"citation_key or author_kind either — "
                        f"got {sorted(pm[0])}")
    elif pm[0].get("identity_authority") != "candidate":
        failures.append(f"§12.3: identity_authority is the literal "
                        f"'candidate' on possible_mismatch too — got "
                        f"{pm[0].get('identity_authority')!r}")
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

    # ------------------- the CLI's fix set
    print("\nthe canonical fix set")

    # `--fix all` exists so no caller has to retype FIXES. Two that did had
    # drifted. The control has to compare against ce.FIXES rather than a list
    # written here, or it becomes the fourth copy to go stale.
    import subprocess as _sp
    with _tf.TemporaryDirectory() as td:
        p = Path(td) / "paper.md"
        p.write_text(HEAD + "As shown (Jones, 2019) here."
                     "\n\n## References\n\nJones, K. (2019). A. J, 1, 1.\n",
                     encoding="utf-8")
        out = _sp.run([sys.executable, str(Path(ce.__file__)), str(p),
                       "--fix", "all"], capture_output=True, text=True)
    applied = None
    for ln in out.stdout.splitlines():
        if '"type":"meta"' in ln or '"type": "meta"' in ln:
            applied = _json.loads(ln).get("fixes_applied")
            break
    if applied is None:
        failures.append(f"--fix all produced no meta line (rc={out.returncode}, "
                        f"stderr={out.stderr[:80]!r})")
    elif sorted(applied) != sorted(ce.FIXES):
        failures.append(f"--fix all applied {applied}, but FIXES is "
                        f"{sorted(ce.FIXES)}")
    else:
        ok("--fix all expands to exactly FIXES, whatever FIXES becomes")

    # ------------------- rc2 §9.6, uncited references
    print("\nrc2 §9.6 — uncited references")

    def unc(body_text, refs):
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "paper.md"
            p.write_text(HEAD + body_text + refs, encoding="utf-8")
            lines, _c = ce.run(p, {"ampersand", "segments"})
        return [l for l in lines if l.get("type") == "uncited_reference"]

    # The residual itself. Nothing in the body matches any entry, so every
    # keyed entry is left over.
    u = unc("As shown (Smith, 2020) here.", "\n\n## References\n\n" + PAD)
    if len(u) != 4:
        failures.append(f"§9.6: every remaining keyed reference is uncited — "
                        f"got {len(u)} of 4")
    elif [x["index"] for x in u] != [0, 1, 2, 3]:
        failures.append("§9.6: uncited_reference rows are indexed in order")
    elif [x["reference_index"] for x in u] != [0, 1, 2, 3]:
        failures.append("§9.6: the pool is built in reference SOURCE order")
    else:
        ok("§9.6: every remaining keyed reference is emitted, in source order")

    # "After exact authoritative matches". The cited one must drop out, and
    # this control is what stops §9.6 being a list of the whole bibliography.
    u = unc("As shown (Jones, 2019) here.", "\n\n## References\n\n" + PAD)
    if len(u) != 3:
        failures.append(f"§9.6: an exactly matched reference is not uncited — "
                        f"got {len(u)}, expected 3")
    elif any(x["reference_key"] == "jones|2019" for x in u):
        failures.append("§9.6: the matched entry appeared in the residual")
    else:
        ok("§9.6: an exact authoritative match leaves the pool")

    # "...and candidate-level possible-mismatch pairing". §9.4 popped it, so
    # it must not reappear here. Without this the same entry is reported twice
    # under two contradictory headings.
    u = unc("As shown (Whiteman, 2000) here.",
            "\n\n## References\n\nWhitman, R. (2000). A paper. J, 1, 1.\n"
            + PAD)
    if any(x["reference_key"] == "whitman|2000" for x in u):
        failures.append("§9.6: a reference paired by §9.4 was ALSO reported "
                        "uncited; one entry cannot be both")
    elif len(u) != 4:
        failures.append(f"§9.6: the four unpaired entries remain — got {len(u)}")
    else:
        ok("§9.6: a mismatch-paired reference does not reappear as uncited")

    # "every remaining UNIQUE keyed reference". Two entries sharing a key have
    # no unambiguous identity, so neither is a residual. Five such groups
    # exist in the corpus and every one is two different works by the same
    # first author in the same year.
    u = unc("As shown (Nobody, 1999) here.",
            "\n\n## References\n\nJones, K. (2019). First work. J, 1, 1.\n"
            "Jones, K., and Roe, P. (2019). Second work. J, 2, 1.\n"
            "Brown, L. (2018). B. J, 2, 1.\nDavis, M. (2017). C. J, 3, 1.\n"
            "Evans, N. (2016). D. J, 4, 1.\n")
    if any(x["reference_key"] == "jones|2019" for x in u):
        failures.append("§9.6: a duplicated key is not a UNIQUE keyed "
                        "reference and must not be reported uncited")
    elif len(u) != 3:
        failures.append(f"§9.6: the three uniquely keyed entries remain — "
                        f"got {len(u)}")
    else:
        ok("§9.6: a duplicated reference key is not a uncited candidate")

    # "unresolved_reference rows are never uncited-reference candidates
    # because they have no authoritative reference identity." Structural here
    # — no key, so never in the pool — and pinned anyway, because "it cannot
    # happen" is what this suite keeps discovering was untrue.
    u = unc("As shown (Nobody, 1999) here.",
            "\n\n## References\n\nMalone, T. An untitled entry with no year.\n"
            + PAD)
    if any(x.get("reference_key") in (None, "") for x in u):
        failures.append("§9.6: a keyless reference reached the residual")
    elif len(u) != 4:
        failures.append(f"§9.6: only the four keyed entries are uncited — "
                        f"got {len(u)}")
    else:
        ok("§9.6: an unresolved_reference is never a uncited candidate")

    # ---------------------------------------------------------------- §2
    #
    #     Every manuscript coordinate is a half-open, zero-based UTF-8 byte
    #     offset into `canonical_manuscript_bytes`.
    #
    # The whole class of defect here is silent: a code-point index is a
    # perfectly plausible integer, it stays in range, it sorts in the right
    # order, and every count built on it comes out the same. Nothing errors.
    # Measured 22 September before the fix, across the thirteen in-profile
    # papers: 14,834 of 15,570 emitted offsets — 95.3% — named a position
    # holding unrelated text.
    #
    # So these controls do not check the offsets against an expected number.
    # They take each record's own text and ask whether slicing the manuscript
    # BYTES by that record's own coordinates returns it. That is the only
    # form of the check that cannot pass for the wrong reason: a wrong offset
    # yields a wrong slice, and there is no third possibility.
    print("\nrc2 §2 — coordinates are UTF-8 byte offsets")

    def sliced(body: str, fixes=frozenset({"ampersand"}), refs=REFS):
        """Every (record, field-pair) span, and what the bytes hold there."""
        doc = HEAD + body + refs
        p = Path(_tf.mkdtemp()) / "p.md"
        p.write_bytes(doc.encode("utf-8"))
        lines, _c = ce.run(p, set(fixes))
        # Rebuild canonical bytes the way §2 defines them, from the file —
        # NOT from anything `run` returns. A control that asked the extractor
        # for the text it measured against would agree with itself.
        text = ce.normalise(p.read_bytes())
        if "ampersand" in fixes:
            text = text.replace("\\&", "&")
        if "mathyear" in fixes:
            text = ce.unwrap_math_years(text)
        raw = text.encode("utf-8")
        out = []
        for rec in lines:
            for val, s, e in (("citation_group", "group_start", "group_end"),
                              ("citation_segment", "segment_start",
                               "segment_end"),
                              ("text", "start", "end")):
                if (rec.get(val) is not None
                        and isinstance(rec.get(s), int)
                        and isinstance(rec.get(e), int)):
                    out.append((rec.get("type"), val, rec[val],
                                raw[rec[s]:rec[e]].decode("utf-8", "replace")))
        return out

    # An all-ASCII document. Byte offsets and code-point indices are IDENTICAL
    # here, so this control passes either way — which is exactly why it is not
    # the evidence. It is here to show the slicing harness itself works, so
    # that a failure in the next control means the offsets and not the check.
    spans = sliced("Growth is documented (Smith, 2020) widely.")
    wrong = [s for s in spans if s[2] != s[3]]
    if not spans:
        failures.append("§2: the ASCII control produced no spans to check")
    elif wrong:
        failures.append(f"§2: the slicing harness disagrees on pure ASCII, "
                        f"where bytes and code points cannot differ — {wrong[0]}")
    else:
        ok(f"§2: on ASCII every one of {len(spans)} spans slices its own text")

    # The real one. Every character before the citation is multi-byte, so a
    # code-point index is guaranteed to land short — 2 bytes per character in
    # the accented run, 3 per em-dash and curly quote.
    #
    # This is not a contrived document. Mathpix output carries accented
    # surnames, en-dashes and curly quotes within the first few hundred
    # characters of every paper in this corpus, which is why the pre-fix
    # figure was 95% and not 5%.
    #
    # Interleaved rather than front-loaded, so the displacement grows across
    # the document. A single citation after a single accented run would fail
    # by a fixed amount, which an off-by-N patch could absorb; here the error
    # is different at every site and only a real conversion holds.
    # The four characters are rc2's own, not chosen here. C-003's evidence
    # column reads "β, —, ’, ﬁ spans slice exact bytes", and they are four
    # different widths — 2, 3, 3 and 3 bytes — so a patch that assumed one
    # multiplier passes on some and fails on others.
    LEAD = ("Schön, Müller und Björk — β decay, don’t say ﬁnal — "
            "établissent qu'il s'agit d'une étude préliminaire. ")
    spans = sliced(LEAD
                   + "Growth is documented (Smith, 2020) widely. "
                   + "Le résumé — très détaillé — précède (Jones, 2019) ici. "
                   + "Weiterführende Überlegungen zeigen (Brown, 2018) dies. "
                   + "Une dernière remarque (Davis, 2017) là.",
                   refs=("\n\n## References\n\n"
                         "Smith, J. (2020). A paper. Journal, 1(1), 1-10.\n\n"
                         "Jones, R. (2019). Another. Journal, 2(1), 1-10.\n\n"
                         "Brown, K. (2018). A third. Journal, 3(1), 1-10.\n\n"
                         "Davis, L. (2017). A fourth. Journal, 4(1), 1-10.\n"))
    wrong = [s for s in spans if s[2] != s[3]]
    if not spans:
        failures.append("§2: the multi-byte control produced no spans")
    elif wrong:
        t, field, want, got = wrong[0]
        failures.append(f"§2: {len(wrong)} of {len(spans)} spans do not slice "
                        f"their own text out of the manuscript bytes — "
                        f"{t}.{field} is {want!r}, bytes hold {got!r}")
    else:
        ok(f"§2: after {len(LEAD.encode()) - len(LEAD)} bytes of multi-byte "
           f"lead-in, all {len(spans)} spans still slice their own text")

    # rc3 D1, and the reason the two byte-changing fixes moved ahead of
    # canonicalisation:
    #
    #     exclusion     does not change bytes   safe at any stage
    #     substitution  changes bytes           every downstream offset shifts
    #
    # Applied after the canonical bytes are fixed, `\& -> &` shortens the body
    # under every citation that follows it and NOTHING ERRORS. Measured on
    # paper 4918fd7d before the move: 0 of 264 citations could slice their own
    # group; with the fixes off, 123 of 123 could. A control that only ran
    # with fixes off would have reported the extractor healthy.
    body = ("Early work (Alpha \\& Beta, 2001) and (Gamma \\& Delta, 2002) "
            "and (Epsilon \\& Zeta, 2003) set this out. "
            "Growth is documented (Smith, 2020) widely.")
    spans = sliced(body, fixes=frozenset({"ampersand"}))
    wrong = [s for s in spans if s[2] != s[3]]
    if len(spans) < 4:
        failures.append(f"§2/D1: expected at least four spans, got {len(spans)}")
    elif wrong:
        t, field, want, got = wrong[0]
        failures.append(f"§2/D1: with `ampersand` on, {len(wrong)} of "
                        f"{len(spans)} spans are displaced — {t}.{field} is "
                        f"{want!r}, bytes hold {got!r}. The substitution is "
                        f"running after canonicalisation.")
    else:
        ok(f"rc3 D1: three `\\&` substitutions precede canonicalisation, so "
           f"all {len(spans)} spans still slice their own text")

    # Both byte-changing fixes together, in the order rc3 §J pins. `mathyear`
    # rewrites `$(2012)$` to `(2012)`, which shortens the text again and by a
    # different amount, so an implementation that moved only `ampersand`
    # ahead of the hash passes the control above and fails this one.
    body = ("Early work (Alpha \\& Beta, 2001) set this out. "
            "Later $(2012)$ and $(2016)$ work followed. "
            "Growth is documented (Smith, 2020) widely.")
    spans = sliced(body, fixes=frozenset({"ampersand", "mathyear"}))
    wrong = [s for s in spans if s[2] != s[3]]
    if len(spans) < 3:
        failures.append(f"§2/§J: expected at least three spans, got {len(spans)}")
    elif wrong:
        t, field, want, got = wrong[0]
        failures.append(f"§2/§J: with both byte-changing fixes on, "
                        f"{len(wrong)} of {len(spans)} spans are displaced — "
                        f"{t}.{field} is {want!r}, bytes hold {got!r}")
    else:
        ok(f"rc3 §J: ampersand then mathyear, both before canonicalisation — "
           f"all {len(spans)} spans hold")

    # rc2 §2 binds `canonical_sha256` to "exactly canonical_manuscript_bytes",
    # and D1 puts the ingest transforms before it. Those two together mean the
    # digest has to cover the SAME bytes the offsets index — otherwise a
    # reader who fetches the manuscript by its recorded hash gets a document
    # the coordinates do not fit.
    #
    # Recomputed here from the file rather than read back from the output,
    # for the same reason as above.
    import hashlib as _hl
    doc = (HEAD + "Early work (Alpha \\& Beta, 2001) set this out. "
           + "Growth is documented (Smith, 2020) widely." + REFS)
    p = Path(_tf.mkdtemp()) / "p.md"
    p.write_bytes(doc.encode("utf-8"))
    digests = {}
    for fx in (frozenset(), frozenset({"ampersand"})):
        ls, _c = ce.run(p, set(fx))
        t = ce.normalise(p.read_bytes())
        if "ampersand" in fx:
            t = t.replace("\\&", "&")
        digests[bool(fx)] = (ls[0]["canonical_sha256"],
                             _hl.sha256(t.encode("utf-8")).hexdigest())
    # Order matters between these two, and the first version had it backwards.
    # Checking the binding first made the second branch unreachable: a digest
    # taken before the transform fails the binding check too, so "unchanged by
    # a byte-changing fix" could never be the reported reason. A branch that
    # cannot fire is the same defect as a check that passes for the wrong
    # reason. The movement test goes first because it is the narrower claim.
    if digests[False][0] == digests[True][0]:
        failures.append("rc3 D1: canonical_sha256 is unchanged by a "
                        "byte-changing fix, so it is being computed before "
                        "the ingest transform rather than after it")
    elif any(a != b for a, b in digests.values()):
        failures.append(f"§2: canonical_sha256 is not the digest of the bytes "
                        f"the offsets index — {digests}")
    else:
        ok("§2/D1: canonical_sha256 covers the post-transform bytes, and "
           "moves when the transform does")

    # The guard, not the conversion. `to_byte_coordinates` used to skip any
    # coordinate outside the table instead of raising, which left code-point
    # values sitting in the same field as byte values with nothing to tell
    # them apart. An offset that cannot be converted means the record was
    # built against a different string, and rc2 §14 exit 6 is "internal
    # invariant violation".
    try:
        ce.to_byte_coordinates([{"type": "citation", "start": 10 ** 6}],
                               "short text")
        failures.append("§2: an out-of-range coordinate was accepted; a wrong "
                        "offset must not survive the conversion silently")
    except ce.Abort as a:
        if a.code != 6:
            failures.append(f"§2: out-of-range coordinate aborted {a.code}, "
                            f"not §14's exit 6 for an invariant violation")
        else:
            ok("§2: an unconvertible coordinate aborts, exit 6, rather than "
               "staying in the record as a code-point index")

    # And the null case it must NOT abort on: `previous_sentence_end` is None
    # for the first sentence, and §11.3 nulls ten fields outright. Making the
    # guard strict is only correct if it stays quiet on a legitimate null.
    rec = {"type": "citation", "previous_sentence_end": None, "start": 3}
    try:
        ce.to_byte_coordinates([rec], "a é c")
        if rec["previous_sentence_end"] is not None:
            failures.append("§2: a null coordinate was converted to a number")
        elif rec["start"] != 4:
            failures.append(f"§2: start 3 in 'a é c' is byte 4, got "
                            f"{rec['start']}")
        else:
            ok("§2: a null coordinate passes through as null, and the "
               "sibling offset still converts")
    except ce.Abort as a:
        failures.append(f"§2: a legitimate null coordinate aborted "
                        f"{a.code} {a.reason}")

    # ------------------------------------------------------ §11, §11.4, C-052
    #
    # rc2 declares 21 summary fields and this file emitted 9 of them until
    # 23 September. The twelve added are not decoration: §11.1 and §11.2 are
    # arithmetic invariants over them, and an invariant you cannot evaluate is
    # not an invariant.
    print("\nrc2 §11 — summary fields and the invariants over them")

    def summ_of(body, refs=REFS, fixes=frozenset({"ampersand"})):
        p = Path(_tf.mkdtemp()) / "p.md"
        p.write_bytes((HEAD + body + refs).encode("utf-8"))
        ls, _c = ce.run(p, set(fixes))
        return [l for l in ls if l.get("type") == "summary"][0]

    # Which fields rc2 declares, read out of rc2's own example line. A list
    # typed into this control would be a copy of the implementation's list, and
    # two copies of the same table agree with each other whatever either says.
    #
    # Field SET only. Their ORDER is §12.3's business and is checked there,
    # against the same bytes — duplicating it here would mean two controls to
    # keep in step and one of them eventually lying.
    declared = rc2_declared().get("summary")
    if not declared:
        failures.append("§11: rc2's summary example line was not found, so "
                        "this block establishes nothing")
    else:
        got = list(ce.canonical_order(summ_of("A claim (Smith, 2020) holds.")))
        missing = [k for k in declared if k not in got]
        if missing:
            failures.append(f"§11: rc2 declares summary fields this file does "
                            f"not emit — {missing}")
        else:
            ok(f"§11: all {len(declared)} of rc2's summary fields are emitted, "
               f"with this file's {len(got) - len(declared)} extras alongside")

    # §11.1, the extraction invariant, and rc2 says "always" — so it is checked
    # in bibliography-absent mode too, where every identity count goes null.
    # Extraction does not need a bibliography, and §11.3 leaves these three out
    # of its null list precisely because they were still measured.
    # `(OECD, 2020)` is in the fixture on purpose: it fails §6's all-caps
    # surname rule and becomes an `unresolved_citation`, so the right-hand side
    # has two non-zero terms.
    #
    # The first version used two ordinary citations, both of which parsed. That
    # made `unresolved_extraction_occurrences` zero, so `total = extracted`
    # held with the unresolved term absent — and the mutation that drops the
    # term entirely SURVIVED. Caught by the probe, which is the only thing that
    # could have caught it: the control was green, named the right rule, and
    # tested half of it.
    for label, refs in (("with a bibliography", REFS),
                        ("with none at all", "\n\nPlain closing text.\n")):
        s = summ_of("A claim (Smith, 2020) holds. Also (OECD, 2020) says so.",
                    refs=refs)
        lhs = s["total_citation_occurrences"]
        extracted = s["extracted_citation_occurrences"]
        unres_occ = s["unresolved_extraction_occurrences"]
        if lhs != extracted + unres_occ:
            failures.append(f"§11.1: total must equal extracted + unresolved "
                            f"{label} — {lhs} != {extracted} + {unres_occ}")
        elif not extracted or not unres_occ:
            failures.append(f"§11.1: the invariant was checked {label} with "
                            f"extracted={extracted} and unresolved={unres_occ}; "
                            f"a zero term makes it hold without being tested")
        else:
            ok(f"§11.1: total {lhs} = extracted {extracted} + unresolved "
               f"{unres_occ}, {label}")

    # §11.2's identity partition, which is C-052: "resolved + author_ambiguous
    # + not_resolved = extracted". Every extracted occurrence gets exactly one
    # of rc2 §9.2's identity states, so a citation that fell through every
    # branch would show up here as arithmetic rather than as a missing field.
    s = summ_of("A claim (Smith, 2020) holds. Nobody (Ghost, 1999) agrees.")
    lhs = s["extracted_citation_occurrences"]
    rhs = (s["resolved_citation_occurrences"]
           + s["author_resolution_ambiguous_occurrences"]
           + s["identity_not_resolved_occurrences"])
    if lhs != rhs:
        failures.append(f"§11.2/C-052: the identity partition must be exact — "
                        f"extracted {lhs} != {rhs}")
    elif s["resolved_citation_occurrences"] == 0 or \
            s["identity_not_resolved_occurrences"] == 0:
        failures.append("§11.2/C-052: the partition was checked on a document "
                        "where one side is empty, so it would balance without "
                        "the states being assigned")
    else:
        ok("§11.2/C-052: resolved + ambiguous + not_resolved = extracted, "
           "with both a resolved and an unresolved occurrence present")

    # §11.2's second equation, and the one that caught a real defect. It is
    # only evidence because the two sides come from different places:
    # `resolved_citation_occurrences` from whether a key is in the reference
    # index, the right-hand side from `identity_class`.
    #
    # Computed as the sum, this would have been true on all thirteen papers
    # and said nothing. Computed independently, it was FALSE on seven of them,
    # because `resolved` had been written as "has a non-null citation_key" and
    # rc2 §11.4 says "non-null AUTHORITATIVE citation_key" — 55 corpus
    # citations have the first and not the second.
    lhs = s["resolved_citation_occurrences"]
    rhs = (s["unique_reference_match_occurrences"]
           + s["bibliography_key_ambiguous_occurrences"])
    if lhs != rhs:
        failures.append(f"§11.2: resolved must equal unique_reference_match + "
                        f"bibliography_key_ambiguous — {lhs} != {rhs}")
    else:
        ok("§11.2: resolved = unique_reference_match + key_ambiguous, each "
           "side computed from a different field")

    # §11.4's authority distinction, stated as its own control because the
    # arithmetic above can be satisfied by two wrong numbers that happen to
    # agree. A citation with no reference behind it keeps its syntax-derived
    # key — rc2 §8: "syntax does not confer authoritative citation_key" — and
    # must NOT be counted as resolved or as a work cited.
    p = Path(_tf.mkdtemp()) / "p.md"
    p.write_bytes((HEAD + "Nobody (Ghost, 1999) agrees." + REFS).encode("utf-8"))
    ls, _c = ce.run(p, {"ampersand"})
    ghost = next((c for c in ls if c.get("type") == "citation"
                  and c.get("year") == "1999"), None)
    s = [l for l in ls if l.get("type") == "summary"][0]
    if ghost is None:
        failures.append("§11.4: the authority control's citation did not parse")
    elif ghost["citation_key"] is None:
        failures.append("§11.4: this control needs a citation that HAS a key "
                        "without authority; this one has no key, so it would "
                        "pass under either model")
    elif s["resolved_citation_occurrences"] != 0:
        failures.append(f"§11.4: a key with no bibliography entry behind it is "
                        f"not resolved — got "
                        f"{s['resolved_citation_occurrences']}")
    elif s["distinct_works_cited"] != 0:
        failures.append(f"§11.4: a key with no reference is not a work cited — "
                        f"got {s['distinct_works_cited']}")
    else:
        ok(f"§11.4: {ghost['citation_key']!r} has a key and no authority, so "
           f"it counts toward neither resolved nor works cited")

    # C-051, and §8.5's fourth bullet: "reserved indices ... do not count as
    # uniquely matched unless independently matched by another unambiguous
    # occurrence." §11.4 says the same thing from the other end —
    # `uniquely_matched_occurrences` are occurrences whose key maps to EXACTLY
    # ONE reference row.
    #
    # A key held by two entries was counted as a unique match until
    # 23 September. The occurrence was `bibliography_key_ambiguous`, emitted
    # `ambiguous_citation`, reserved both reference indices — and still
    # reported `uniquely_matched_works: 1`. Ambiguous by every field in the
    # output except the one this case is about.
    #
    # The conformance map had C-051 NOT for a reason that had stopped being
    # true: "the summary has no uniquely-matched-works count to assert +0
    # against". The count landed the same morning; the rule was still broken
    # underneath it, which is why the case was tested rather than re-read.
    # Its own fixture: `through_cli` hardcodes a one-entry bibliography, which
    # cannot hold a duplicate key. Two Felfe 2006 entries are a real corpus
    # shape, not a contrivance — five such groups across four papers, every one
    # two genuinely different works by the same first author in the same year.
    _p = Path(_tf.mkdtemp()) / "p.md"
    _p.write_bytes((
        HEAD + "As shown (Felfe, 2006) here. Also (Smith, 2020) elsewhere."
        + "\n\n## References\n\n"
        "Felfe, J. (2006). One work. Journal, 7(1), 1-10.\n\n"
        "Felfe, J. (2006). A different work, same key. Journal, 8(1), 1-10.\n\n"
        "Smith, J. (2020). A paper. Journal, 1(1), 1-10.\n"
    ).encode("utf-8"))
    ls, _c = ce.run(_p, {"ampersand"})
    s = [l for l in ls if l.get("type") == "summary"][0]
    amb = [l for l in ls if l.get("type") == "ambiguous_citation"]
    if not amb:
        failures.append("C-051: the fixture produced no ambiguous_citation, so "
                        "there is nothing reserved and the case is untested")
    elif s["bibliography_key_ambiguous_occurrences"] != 1:
        failures.append(f"C-051: expected exactly one key-ambiguous "
                        f"occurrence, got "
                        f"{s['bibliography_key_ambiguous_occurrences']}")
    # Both halves in one branch, and the message names the rule rather than
    # the arithmetic. Split across two branches, the "must still count" guard
    # fired FIRST under the mutation that re-admits duplicate keys — so the
    # probe reported WRONG CONTROL for a control that was catching the defect,
    # under a message about the opposite failure.
    #
    # Expected 1 and 1: Smith counts, Felfe does not. Over-counting gives 2,
    # excluding everything gives 0, and counting the wrong one alone is caught
    # by the key check below.
    elif (s["uniquely_matched_occurrences"], s["uniquely_matched_works"]) != (1, 1):
        failures.append(
            f"C-051: a key held by two references counts +0 toward uniquely "
            f"matched, and the unambiguous occurrence beside it still counts "
            f"— got occurrences={s['uniquely_matched_occurrences']}, "
            f"works={s['uniquely_matched_works']}, expected 1 and 1")
    elif not any(c.get("type") == "citation"
                 and c.get("citation_key") == "smith|2020"
                 and c.get("identity_class") == "unique_reference_match"
                 for c in ls):
        failures.append("C-051: the surviving match must be smith|2020; a "
                        "count of 1 that named the ambiguous work instead "
                        "would satisfy the arithmetic and not the rule")
    else:
        ok(f"C-051: reserved indices {amb[0]['reference_indices']} count +0, "
           f"and the unambiguous occurrence beside them still counts")

    # §11.2: the two candidate-level diagnostics are "over a SUBSET of
    # identity_not_resolved_occurrences", not additional partition states.
    # Their sum can therefore never exceed it — the check that would catch an
    # occurrence being counted under two candidate keys.
    s = summ_of("Nobody (Ghost, 1999) agrees. Neither (Phantom, 1998) does.")
    diag = (s["reference_missing_occurrences"]
            + s["possible_mismatch_occurrences"])
    inr = s["identity_not_resolved_occurrences"]
    if diag > inr:
        failures.append(f"§11.2: the diagnostics count occurrences twice — "
                        f"{diag} diagnostic occurrences over {inr} unresolved")
    elif diag == 0:
        failures.append("§11.2: the subset bound was checked with no "
                        "diagnostics emitted, so it holds vacuously")
    else:
        ok(f"§11.2: {diag} diagnostic occurrences within {inr} "
           f"identity_not_resolved, counted once each")

    _spec_txt = (rc2_spec_path().read_text(encoding="utf-8")
                 if rc2_spec_path() else "")

    # ----------------------------------------- §13, §14, C-074/075/076/077
    #
    # The abort streams, as BYTES, against rc2's own declared shape. C-077 read
    # NOT with the note "what is unpinned is the two-line error stream's exact
    # bytes, which needs a byte golden this repository does not have". This is
    # that golden, and it found a defect the moment it existed:
    #
    #     rc2 §14   2 -> unsupported citation style
    #     emitted      unsupported citation style: 100% of 12 author-year
    #                  parentheticals omit the comma before the year, ...
    #
    # rc2's reason table is a closed mapping from code to STRING, and the
    # string is part of a two-line contract a consumer parses. Worse, the two
    # exit-2 sites disagreed with each other — one bare, one long, same code.
    # The explanation now goes to stderr, which §14 calls non-normative.
    print("\nrc2 §13/§14 — the abort streams, byte for byte")

    _rt = re.search(r"The `code` and `reason` vary by exit:.*?```text\n(.*?)```",
                    _spec_txt, re.S)
    reason_of = {}
    if _rt:
        for ln in _rt.group(1).strip().splitlines():
            if "->" in ln:
                c, _, r = ln.partition("->")
                reason_of[int(c.strip())] = r.strip()

    _bad = Path(_tf.mkdtemp()) / "utf8.md"
    _bad.write_bytes(b"\xff\xfe not utf-8 at all")
    _head = Path(_tf.mkdtemp()) / "head.md"
    _head.write_bytes(b"# One\n\ntext\n\n# Two\n\nmore\n")
    _style = Path(_tf.mkdtemp()) / "style.md"
    _style.write_bytes((HEAD + " ".join(
        f"Work follows (Smith{i} 20{10 + i})." for i in range(12))
        + "\n\n## References\n\nSmith, J. (2020). A. J, 1, 1.\n").encode("utf-8"))

    # 3 is the invalid-section-map abort and 6 the invariant failure. Neither
    # is reachable from a document: §2.1 forbids a supplied map in the pilot
    # scope, and 6 needs §15's test-only seam, which C-046 exercises. Named
    # rather than quietly skipped.
    ABORTS = [(5, _bad), (4, _head), (2, _style)]
    UNREACHABLE_FROM_A_DOCUMENT = {3, 6}

    if not reason_of:
        failures.append("§14: rc2's reason table was not found, so the stream "
                        "could not be checked against it")
    else:
        expected_meta = (
            b'{"type":"meta","spec_version":"' + ce.SPEC_VERSION.encode()
            + b'","citation_rule_version":"'
            + ce.CITATION_RULE_VERSION.encode() + b'"}')
        bad = []
        for code, path in ABORTS:
            cap, _o, _a = _BinStdout(), sys.stdout, sys.argv
            sys.stdout, sys.argv = cap, [str(Path(ce.__file__)), str(path)]
            try:
                got_code = ce.main()
            finally:
                sys.stdout, sys.argv = _o, _a
            raw = cap.buffer.getvalue()

            if got_code != code:
                bad.append(f"exit {code}: got {got_code}")
                continue
            # §12.1's byte properties apply to the error stream too.
            if raw.startswith(b"\xef\xbb\xbf"):
                bad.append(f"exit {code}: BOM")
            elif b"\r" in raw:
                bad.append(f"exit {code}: CR present, §12.1 is LF only")
            elif not raw.endswith(b"\n"):
                bad.append(f"exit {code}: no final LF")
            elif len(raw.rstrip(b"\n").split(b"\n")) != 2:
                bad.append(f"exit {code}: §14 says exactly two lines, got "
                           f"{len(raw.rstrip(chr(10).encode()).splitlines())}")
            else:
                meta_line, err_line = raw.rstrip(b"\n").split(b"\n")
                if meta_line != expected_meta:
                    bad.append(f"exit {code}: meta line is\n        "
                               f"{meta_line.decode()}\n      rc2 declares\n"
                               f"        {expected_meta.decode()}")
                else:
                    want = (b'{"type":"error","code":' + str(code).encode()
                            + b',"reason":"'
                            + reason_of[code].encode("utf-8") + b'"}')
                    if err_line != want:
                        bad.append(f"exit {code}: error line is\n        "
                                   f"{err_line.decode()}\n      rc2 declares\n"
                                   f"        {want.decode()}")
        if bad:
            failures.append("§14/C-077: the abort stream does not match rc2's "
                            "declared bytes —\n      " + "\n      ".join(bad))
        else:
            ok(f"§14/C-077: {len(ABORTS)} abort streams are byte-exact against "
               f"rc2's table; {sorted(UNREACHABLE_FROM_A_DOCUMENT)} need a "
               f"supplied map or §15's seam")

        # §13: "For exits 2-5, the two-line error stream is written to the
        # requested file as the authoritative error artifact." Same bytes, and
        # no normal record anywhere in it.
        _d = Path(_tf.mkdtemp())
        _target = _d / "out.jsonl"
        cap, _o, _a = _BinStdout(), sys.stdout, sys.argv
        sys.stdout, sys.argv = cap, [str(Path(ce.__file__)), str(_bad),
                                     "--out", str(_target)]
        try:
            _c = ce.main()
        finally:
            sys.stdout, sys.argv = _o, _a
        if not _target.exists():
            failures.append("§13: for exits 2-5 the error stream is written to "
                            "the requested file as the authoritative artifact")
        elif _target.read_bytes() != cap.buffer.getvalue():
            failures.append("§13: the file and stdout must carry the same "
                            "bytes; they differ")
        elif b'"type":"citation"' in _target.read_bytes():
            failures.append("§14: no normal record may precede the error "
                            "stream, and none may be in the artifact")
        else:
            ok("§13: the abort artifact is the stdout stream exactly, two "
               "lines, no normal record")

    # ------------------------------------------------------------ §1.1, C-068
    #
    # rc2 §1.1's rule-identity constants, read out of §1.1's own block rather
    # than retyped. `meta` carried v3.3's single field until 23 September, and
    # that was not a neutral undecided state: every rule the extractor runs is
    # rc2's or rc3's, so the output was describing a v3.4 run under v3.3's
    # name. Waiting to correct it meant continuing to emit a wrong label.
    print("\nrc2 §1.1 — rule identity")

    pinned = {}
    for ln in rc2_section("1.1"):
        if "=" in ln:
            k, _, v = ln.partition("=")
            pinned[k.strip()] = v.strip().strip('"')
    want = {"spec_version": ce.SPEC_VERSION,
            "citation_profile": ce.CITATION_PROFILE,
            "citation_rule_version": ce.CITATION_RULE_VERSION}
    if not pinned:
        failures.append("§1.1: rc2's pinned-constant block was not found, so "
                        "this control establishes nothing")
    else:
        wrong = {k: (pinned.get(k), v) for k, v in want.items()
                 if pinned.get(k) != v}
        if wrong:
            failures.append(f"§1.1: rule identity must match rc2's pinned "
                            f"constants — (rc2, ours) {wrong}")
        elif pinned.get("ET_AL_MIN_AUTHORS") != str(ce.ET_AL_MIN_AUTHORS):
            failures.append(f"§1.1: ET_AL_MIN_AUTHORS is "
                            f"{pinned.get('ET_AL_MIN_AUTHORS')} in rc2, "
                            f"{ce.ET_AL_MIN_AUTHORS} here")
        else:
            ok(f"§1.1: spec_version {ce.SPEC_VERSION}, profile "
               f"{ce.CITATION_PROFILE}, rule version and ET_AL_MIN_AUTHORS "
               f"all match rc2's pinned block")

    # §1.1: "citation_profile and ET_AL_MIN_AUTHORS are properties of
    # citation_rule_version; they are NOT independently selectable runtime
    # inputs." So no CLI flag may set any of them.
    # The ARGPARSE options only. A first version searched the whole of `main`
    # for the quoted names and went red on the error-stream meta dict, which
    # names `citation_rule_version` because §14 requires it to. The claim is
    # "not selectable", so the evidence is the option list, not the file.
    import inspect as _inspect
    _cli_src = _inspect.getsource(ce.main) if hasattr(ce, "main") else ""
    declared_opts = re.findall(r"add_argument\(\s*[\"']([^\"']+)[\"']",
                               _cli_src)
    leaked = [o for o in declared_opts
              if o.strip("-").replace("-", "_") in
              ("citation_profile", "citation_rule_version", "spec_version",
               "et_al_min_authors", "profile", "rule_version")]
    if not declared_opts:
        failures.append("§1.1: no CLI options were found to inspect, so this "
                        "control did not run")
    elif leaked:
        failures.append(f"§1.1: these are properties of citation_rule_version, "
                        f"not selectable runtime inputs — the CLI declares "
                        f"{leaked}")
    else:
        ok(f"§1.1: none of the {len(declared_opts)} CLI options selects the "
           f"profile, rule version or et-al threshold")

    # rc2 §14's error stream has its OWN meta: two fields, not §12.2's eight.
    #
    # Through the CLI, reading the BYTES it writes. A first version built the
    # record itself and handed it to `ce.serialize`, which checks that this
    # control can construct rc2's shape and says nothing about whether `main`
    # emits it.
    _bad = Path(_tf.mkdtemp()) / "bad.md"
    _bad.write_bytes(b"\xff\xfe not utf-8 at all")
    _cap, _out, _argv = _BinStdout(), sys.stdout, sys.argv
    sys.stdout, sys.argv = _cap, [str(Path(ce.__file__)), str(_bad)]
    try:
        _code = ce.main()
    finally:
        sys.stdout, sys.argv = _out, _argv
    _stream = _cap.buffer.getvalue().decode("utf-8").splitlines()
    if _code != 5 or len(_stream) != 2:
        failures.append(f"§14: invalid UTF-8 is exit 5 and exactly two lines "
                        f"— got exit {_code}, {len(_stream)} line(s)")
    else:
        err_meta = _json.loads(_stream[0])
        if list(err_meta) != ["type", "spec_version", "citation_rule_version"]:
            failures.append(f"§14: the error stream's meta is exactly type, "
                            f"spec_version, citation_rule_version — got "
                            f"{list(err_meta)}")
        elif err_meta["citation_rule_version"] != ce.CITATION_RULE_VERSION:
            failures.append("§14: the error stream must name the ruleset that "
                            "refused the document")
        else:
            ok("§14: invalid UTF-8 writes two lines, and the meta names the "
               "ruleset that refused the document")


    # ------------------------------------------------------------ C-031, and
    # every other closed set rc2 declares
    #
    # C-031 asks for "schema rejection" on `unresolved_reference.reason`: only
    # `entry_start_grammar | orphan_line | no_year`. The same requirement
    # applies to every closed enum in rc2, so this checks them together rather
    # than one at a time.
    #
    # Written after two closed sets turned out to have drifted in one day —
    # §3.2's STOP list was five tokens short and §3.1's PREFIX list was five
    # cues short. Neither was findable by testing a sample, which is the whole
    # property of a closed set. So the rule here is: for every value field rc2
    # closes, no emitted value may fall outside it.
    #
    # The sweep across the thirteen corpus papers found ZERO violations in
    # these eight, so this is a guard rather than a fix. What it guards against
    # is the direction the other two drifted in — a set gaining a member here
    # that rc2 does not have, or losing one it does.
    print("\nrc2's closed value enums — nothing outside any of them")

    def _inline_enum(pat):
        m = re.search(pat, _spec_txt)
        return {x.strip().strip("`") for x in m.group(1).split(",")} if m else set()

    ENUMS = {
        "author_resolution": _inline_enum(r"author_resolution ∈ \{([^}]+)\}"),
        "author_kind": _inline_enum(r"author_kind ∈ \{([^}]+)\}"),
        "style": _inline_enum(r"style ∈ \{([^}]+)\}"),
        "section_level": _inline_enum(r"section_level ∈ \{([^}]+)\}"),
        "evidence": _inline_enum(r"`evidence ∈ \{([^}]+)\}`"),
        "failed": _inline_enum(r"`failed ∈ \{([^}]+)\}`"),
    }
    # `reason` is TWO closed enums under one field name — §6.4's for
    # `unresolved_citation` and §7's for `unresolved_reference` — so the sweep
    # keys on (record type, field). Keyed on the field alone it reported
    # `no_grammar_match` as a violation of the reference enum, which is a flaw
    # in the check rather than a defect in the run: right value, wrong record.
    _rr = re.search(r"Closed `unresolved_reference\.reason` enum:.*?```text\n(.*?)```",
                    _spec_txt, re.S)
    _rc = re.search(r"### 6\.4 Unresolved-citation reasons.*?```text\n(.*?)```",
                    _spec_txt, re.S)
    ENUMS[("unresolved_reference", "reason")] = (
        set(_rr.group(1).split()) if _rr else set())
    ENUMS[("unresolved_citation", "reason")] = (
        set(_rc.group(1).split()) if _rc else set())

    empty = [k for k, v in ENUMS.items() if not v]
    if empty:
        failures.append(f"C-031: these closed sets could not be read out of "
                        f"rc2, so the sweep proves nothing for them — {empty}")
    else:
        # One fixture per branch, chosen so that EVERY declared value in
        # every closed enum is reached. That is the real bar, and the first
        # version of this control did not clear it: it ran six fixtures,
        # reached 12 of the 21 values, and guarded the rest with a floor of
        # "at least 14" that was a number picked rather than derived.
        #
        # A subset check is only evidence over the values it reaches. Testing
        # a sample is exactly what a closed set defeats, which is how §3.1 and
        # §3.2 both drifted unnoticed.
        R1 = ("\n\n## References\n\n"
              "Smith, J. (2020). A. Journal, 1(1), 1-10.\n")
        FIXTURES = [
            ("two resolved, one non-ASCII",
             "As shown (Smith, 2020) and Müller (2019) here.",
             R1.rstrip("\n") + "\n\nMüller, K. (2019). B. Journal, 2(1), 1-10.\n"),
            # §10: not_evaluated / undetermined
            ("bibliography absent", "As shown (Smith, 2020) here.",
             "\n\nPlain closing text with no reference list.\n"),
            # §8.3 row 3: a key held by two entries
            ("duplicate key", "As shown (Felfe, 2006) here.",
             "\n\n## References\n\nFelfe, J. (2006). One. Journal, 7(1), 1-10."
             "\n\nFelfe, J. (2006). Two. Journal, 8(1), 1-10.\n"),
            # §9.4's three repair rules, one fixture each
            ("repair: surname_edit_distance_1", "As shown (Whiteman, 2000) here.",
             "\n\n## References\n\nWhitman, R. (2000). A. Journal, 1(1), 1-10.\n"),
            ("repair: year_adjacent", "As shown (Whitman, 2001) here.",
             "\n\n## References\n\nWhitman, R. (2000). A. Journal, 1(1), 1-10.\n"),
            ("repair: year_transposition", "As shown (Whitman, 2001) here.",
             "\n\n## References\n\nWhitman, R. (2010). A. Journal, 1(1), 1-10.\n"),
            # §9.3's two failure modes
            ("mismatch: order", "As shown (Smith & Brown, 2020) here.",
             "\n\n## References\n\nSmith, J., & Jones, K. (2020). A. J, 1, 1.\n"),
            ("mismatch: count", "As shown (Smith & Brown, 2020) here.", R1),
            # §7's three unresolved_reference reasons
            ("bad entries", "As shown (Smith, 2020) here.",
             R1.rstrip("\n") + "\n\na stray orphan line with no entry grammar"
             "\n\nMalone, T. An entry with no year at all."
             "\n\nUlker Demirel, E., & Ciftci, G. (2020). A review. J, 3, 1.\n"),
            # §6.4's three unresolved_citation reasons
            ("bad candidates",
             "As shown (OECD, 2020) here. Table (2020) reports it. "
             "See (Table 2020) also.", R1),
            # §6.3 stop reduction, and the narrative style
            ("narrative, stop-reduced", "As Table Smith (2020) reports this.", R1),
            # non_person identity
            ("non-person", "The report (World Bank, 2020) says so.",
             "\n\n## References\n\nWorld Bank (2020). A report. WB.\n"),
        ]
        # `section_level` needs its own document: `none` is text before any
        # heading, and h3/h4 need nesting, neither of which fits above.
        LEVELS = ("Opening text with (Smith, 2020) before any heading.\n\n"
                  "# Paper\n\n## Introduction\n\nMore (Smith, 2020).\n\n"
                  "### Sub\n\nMore (Smith, 2020).\n\n"
                  "#### Deep\n\nYet more (Smith, 2020)." + R1)

        emitted = {k: set() for k in ENUMS}
        docs = [HEAD + b + r for _l, b, r in FIXTURES] + [LEVELS]
        for doc in docs:
            p = Path(_tf.mkdtemp()) / "p.md"
            p.write_bytes(doc.encode("utf-8"))
            try:
                ls, _c = ce.run(p, {"ampersand"})
            except ce.Abort:
                continue
            for r in ls:
                for key in ENUMS:
                    if isinstance(key, tuple):
                        rtype, field = key
                        if r.get("type") == rtype and r.get(field) is not None:
                            emitted[key].add(r[field])
                    elif key in r and r[key] is not None:
                        emitted[key].add(r[key])

        # `ambiguous` is reachable only through §15's test-only injection seam
        # — §8.3 rows 6 to 9 need both candidates to match on different keys,
        # which no document can produce. Named rather than silently tolerated,
        # and C-042 to C-045 are what cover it.
        UNREACHABLE = {("author_resolution", "ambiguous")}

        violations = {str(k): sorted(emitted[k] - ENUMS[k])
                      for k in ENUMS if emitted[k] - ENUMS[k]}
        unreached = {str(k): sorted(v) for k in ENUMS
                     if (v := {x for x in ENUMS[k] - emitted[k]
                               if (k, x) not in UNREACHABLE})}
        total = sum(len(v) for v in ENUMS.values())
        if violations:
            failures.append(f"C-031: values emitted outside a set rc2 closes — "
                            f"{violations}")
        elif unreached:
            failures.append(f"C-031: these declared values were never reached, "
                            f"so the subset check says nothing about them — "
                            f"{unreached}")
        else:
            ok(f"C-031: every one of the {total} values across "
               f"{len(ENUMS)} closed enums is reached, and nothing outside "
               f"them is emitted")

    # ------------------------------------------------------- §3.1, C-016/017
    #
    # The other closed set, and it had the same defect as §3.2's: six of rc2's
    # eleven members. rc2 calls the missing five "the five newly added
    # multiword forms", so they arrived with rc2 and were never picked up.
    #
    # Unlike the STOP gap this one was NOT latent. Two corpus groups used one
    # each, and in both the group parsed while silently dropping the single
    # citation sitting behind the prefix — `Osadchiy et al., 2015` out of a
    # three-citation group in gold paper 1, and `Sonnentag & Frese, 2003`.
    print("\nrc2 §3.1 — every parenthetical PREFIX, one case each")

    _m31 = re.search(r"### 3\.1 Closed parenthetical PREFIX set.*?```text\n(.*?)```",
                     _spec_txt, re.S)
    declared_prefix = ([l.strip() for l in _m31.group(1).strip().splitlines()
                        if l.strip()] if _m31 else [])

    if not declared_prefix:
        failures.append("§3.1: rc2's PREFIX block was not found, so the closed "
                        "set could not be read and this block proves nothing")
    elif set(declared_prefix) != set(ce.PREFIX_CUES):
        failures.append(
            f"§3.1: the PREFIX set must equal rc2's closed list — "
            f"in rc2 not ours {[c for c in declared_prefix if c not in ce.PREFIX_CUES]}, "
            f"in ours not rc2 {[c for c in ce.PREFIX_CUES if c not in declared_prefix]}")
    else:
        ok(f"§3.1: all {len(declared_prefix)} cues, and no others — this "
           f"file's set equals rc2's closed list exactly")

        # C-016, one case per prefix. Every member must carry a citation
        # through, and `author_phrase` must be the author rather than any part
        # of the cue — rc2 §6: "author_phrase EXCLUDES a supported
        # parenthetical PREFIX".
        bad = []
        for cue in declared_prefix:
            cits, _u, _e = extract(f"It holds ({cue} Smith, 2020) here.")
            if keys(cits) != ["smith|2020"]:
                bad.append((cue, keys(cits)))
            elif cits[0]["author_phrase"] != "Smith":
                bad.append((cue, f"author_phrase={cits[0]['author_phrase']!r}"))
        if bad:
            failures.append(f"§3.1/C-016: every closed PREFIX form must parse "
                            f"with the cue excluded from author_phrase — "
                            f"{len(bad)} failed, e.g. {bad[:3]}")
        else:
            ok(f"§3.1/C-016: all {len(declared_prefix)} cues parse, and none "
               f"leaks into author_phrase")

        # C-017, longest-match precedence. "The matcher MUST choose the longest
        # matching member before considering a shorter member. Therefore
        # `see also` cannot decompose to `see`, and a multiword form ending in
        # `see` cannot decompose to the standalone `see` prefix."
        #
        # STRUCTURAL, and stated as such rather than dressed up. On every input
        # that could be built here the two orders agree: a short match leaves a
        # lowercase remainder (`also Smith`, `see Smith`), CORE requires a
        # capital, so the short branch fails and the alternation backtracks to
        # the long one. Output cannot tell them apart. What CAN be checked is
        # that the compiled alternation offers the long form first, which is
        # what rc2's "before considering" asks for.
        pats = ce.build_patterns({"ampersand"})
        src = pats["seg"].pattern
        # The cue alternation, split into MEMBERS. A substring search is wrong
        # here and said so loudly: `src.find("see")` lands inside
        # `for\ a\ similar\ approach,\ see`, so every long form looked as
        # though it came after the short one it contains.
        #
        # `re.escape` both sides, because the pattern was built with it and
        # whether it escapes a space is version-dependent — this Python emits
        # `see\ also`.
        inner = src[src.index("(?:(?:") + len("(?:(?:"):]
        inner = inner[:inner.index(")")]
        members = inner.split("|")
        pos = {c: (members.index(re.escape(c))
                   if re.escape(c) in members else -1)
               for c in declared_prefix}
        missing = [c for c, i in pos.items() if i < 0]
        if missing:
            failures.append(f"§3.1/C-017: these cues are not in the compiled "
                            f"segment pattern at all — {missing}")
        else:
            out_of_order = [
                (a, b) for a in declared_prefix for b in declared_prefix
                if a != b and b.endswith(a) and pos[b] > pos[a]]
            if out_of_order:
                failures.append(
                    f"§3.1/C-017: a longer form must be offered before the "
                    f"shorter one it contains — {out_of_order[:3]} are the "
                    f"wrong way round")
            else:
                pairs = [(a, b) for a in declared_prefix for b in declared_prefix
                         if a != b and b.endswith(a)]
                ok(f"§3.1/C-017: {len(pairs)} shorter-inside-longer pair(s), "
                   f"every long form offered first (structural, see comment)")

    # ------------------------------------------------------------ §3.2, C-018
    #
    # C-018: "every STOP token has deterministic behavior | synthetic suite |
    # ONE CASE PER TOKEN". Exhaustive, because rc2 §3.2 says the list "is
    # closed and versioned" and a closed set is the one place where testing a
    # sample proves nothing about the rest.
    #
    # It found five. rc2's last line — panel, column, row, appendix, exhibit —
    # was never copied into this file, and the corpus contains zero of them,
    # so nothing else could have noticed. What it costs, measured:
    #
    #     Panel (2020) reports     keyed `panel|2020`, a citation to a work by
    #                              an author named Panel
    #     As Panel Smith (2020)    no_grammar_match — the real citation lost,
    #                              where `As Table Smith (2020)` resolves
    #
    # One invents a citation and the other drops one.
    print("\nrc2 §3.2 — every STOP token, one case each")

    _m = re.search(r"### 3\.2 Closed STOP set.*?```text\n(.*?)```",
                   _spec_txt, re.S)
    declared_stop = set(_m.group(1).split()) if _m else set()

    if not declared_stop:
        failures.append("§3.2: rc2's STOP block was not found, so the closed "
                        "set could not be read and this block proves nothing")
    elif declared_stop != ce.STOP:
        failures.append(
            f"§3.2: the STOP set must equal rc2's closed list — "
            f"in rc2 not ours {sorted(declared_stop - ce.STOP)}, "
            f"in ours not rc2 {sorted(ce.STOP - declared_stop)}")
    else:
        ok(f"§3.2: all {len(declared_stop)} tokens, and no others — this file's "
           f"set equals rc2's closed list exactly")

        # One case per token, both behaviours rc2 gives a STOP word.
        #
        #   §6   a parsed first CORE whose lowercase value is STOP
        #        -> stopword_surname, never a citation
        #   §6.3 a leading STOP token is removable, so the phrase behind it
        #        still resolves
        #
        # Tokens ending in `.` are excluded from the second shape only: `Jan.
        # Smith (2020)` is an initialled forename in APA, not a reduction, and
        # rc2's own §3.2 normalisation strips a trailing comma/semicolon/colon
        # but not a period. Stated rather than silently skipped.
        # rc2 §6 says "a PARSED first CORE whose lowercase value is STOP".
        # Thirteen of the 109 can never be a parsed CORE at all — the single
        # letter `a`, and the twelve period-final month abbreviations — so
        # they reach `no_grammar_match` instead, which is the correct outcome
        # rather than a defect.
        #
        # The partition is by a property of rc2's OWN tokens: one character,
        # or ending in a period. Not by `ce.CORE`, which would move the buckets
        # with the implementation and leave the control passing either way.
        #
        # What holds for all 109 without exception is the thing that matters:
        # a STOP token leading a candidate NEVER becomes a citation.
        bad_cite, bad_reason, bad_reduce, skipped = [], [], [], []
        for tok in sorted(declared_stop):
            word = tok[:1].upper() + tok[1:]
            core_shaped = len(tok) > 1 and not tok.endswith(".")
            cits, unres, _e = extract(f"{word} (2020) reports this.")
            if cits:
                bad_cite.append((tok, keys(cits)))
            else:
                want = "stopword_surname" if core_shaped else "no_grammar_match"
                if not any(u["reason"] == want for u in unres):
                    bad_reason.append((tok, want,
                                       [u["reason"] for u in unres]))
            if not core_shaped:
                skipped.append(tok)
                continue
            cits, _u, _e = extract(f"As {word} Smith (2020) reports this.")
            if keys(cits) != ["smith|2020"]:
                bad_reduce.append((tok, keys(cits)))

        if bad_cite:
            failures.append(f"§6: a STOP token leading a candidate must never "
                            f"become a citation — {len(bad_cite)} did, "
                            f"e.g. {bad_cite[:4]}")
        elif bad_reason:
            failures.append(f"§6: {len(bad_reason)} STOP token(s) rejected "
                            f"for the wrong reason, e.g. {bad_reason[:4]}")
        elif len(skipped) != 13:
            failures.append(f"§6: expected exactly 13 tokens that cannot be a "
                            f"parsed CORE — got {len(skipped)}. rc2's list "
                            f"moved, and the partition needs re-deriving "
                            f"rather than the count adjusting")
        else:
            ok(f"§6: none of the {len(declared_stop)} STOP tokens becomes a "
               f"citation — {len(declared_stop) - 13} as stopword_surname, "
               f"13 as no_grammar_match because they cannot be a CORE")

        if bad_reduce:
            failures.append(f"§6.3: a leading STOP token must be removable so "
                            f"the phrase behind it still resolves — "
                            f"{len(bad_reduce)} failed, e.g. {bad_reduce[:4]}")
        else:
            ok(f"§6.3: all {len(declared_stop) - len(skipped)} non-abbreviated "
               f"tokens reduce away, leaving smith|2020 "
               f"({len(skipped)} tokens that cannot be a CORE, excluded)")

    # -------------------------------------------------------- §9.1, C-049/050
    #
    # rc2 §9.1's record. The duplicate groups were being COMPUTED — `unique_keys`
    # is their complement, and §8.5, §9.4 and §9.6 all depend on it — and never
    # EMITTED. Five groups across four papers, zero records, so the one thing a
    # reader needs in order to see why those references were held back was the
    # one thing the output did not say.
    print("\nrc2 §9.1 — duplicate reference keys")

    DUP = ("\n\n## References\n\n"
           "Felfe, J. (2006). One work. Journal, 7(1), 1-10.\n\n"
           "Felfe, J. (2006). A different work. Journal, 8(1), 1-10.\n\n"
           "Smith, J. (2020). A paper. Journal, 1(1), 1-10.\n")

    def dups_of(body, refs=DUP):
        p = Path(_tf.mkdtemp()) / "p.md"
        p.write_bytes((HEAD + body + refs).encode("utf-8"))
        ls, _c = ce.run(p, {"ampersand"})
        return ls, [r for r in ls if r.get("type") == "duplicate_reference_key"]

    ls, d = dups_of("As shown (Felfe, 2006) and (Smith, 2020) here.")
    if len(d) != 1:
        failures.append(f"§9.1: one record per key holding two or more "
                        f"entries — got {len(d)}")
    elif d[0]["reference_indices"] != sorted(d[0]["reference_indices"]):
        failures.append(f"§9.1: indices ascending — got "
                        f"{d[0]['reference_indices']}")
    elif len(d[0]["reference_indices"]) != 2:
        failures.append(f"§9.1: both members must be named — got "
                        f"{d[0]['reference_indices']}")
    else:
        ok(f"§9.1: one record for {d[0]['reference_key']!r}, indices "
           f"{d[0]['reference_indices']} ascending")

    # `cited` is CIT-ARCH-01 again. Both branches, because a field hardcoded
    # to `true` passes on this whole corpus — all five real groups are cited,
    # so nothing here would have noticed.
    if d and d[0]["cited"] is not True:
        failures.append("§9.1: an occurrence authoritatively matching the "
                        "duplicate key sets cited=true")
    else:
        _ls2, d2 = dups_of("As shown (Smith, 2020) alone here.")
        if len(d2) != 1:
            failures.append(f"§9.1: the uncited-duplicate fixture produced "
                            f"{len(d2)} record(s), not one")
        elif d2[0]["cited"] is not False:
            failures.append(f"§9.1: a duplicate key no occurrence cites is "
                            f"cited=false — got {d2[0]['cited']!r}")
        else:
            ok("§9.1: cited is true when an occurrence matches the key and "
               "false when none does, on the same bibliography")

    # rc2's second sentence: "candidate-level missing/mismatch keys do not set
    # `cited=true`". UNREACHABLE in this implementation, and stated rather than
    # claimed as a control, because a control that cannot fire is worse than
    # none — it reads as evidence.
    #
    #   missing_reference keys carry identity_class=identity_not_resolved,
    #   which §8.2 gives only to keys matching ZERO references; a duplicate key
    #   matches two or more, so the sets are disjoint.
    #
    #   possible_mismatch pairs against the unmatched pool, and §9.4 builds
    #   that pool from unique keys only, so no duplicate-group reference can
    #   enter it.
    #
    # Measured before being relied on: across the corpus, zero candidate-level
    # keys are also duplicate keys. The structural argument and the count
    # agree, which is the only reason the argument is recorded rather than
    # chased.
    dup_keys = {r["reference_key"] for r in ls
                if r.get("type") == "duplicate_reference_key"}
    cand_keys = {r["candidate_key"] for r in ls
                 if r.get("type") in ("missing_reference", "possible_mismatch")}
    if dup_keys & cand_keys:
        failures.append(f"§9.1: a candidate-level key reached a duplicate key "
                        f"— {dup_keys & cand_keys}. The clause about "
                        f"cited=true is reachable after all and needs a real "
                        f"control, not the disjointness argument")
    else:
        ok("§9.1: candidate-level keys and duplicate keys are disjoint, so "
           "rc2's cited=true caveat cannot be violated here")

    # §12.4: "smallest member reference_index, then reference_key UTF-8 bytes".
    # TWO groups, because with one the block is trivially ordered and a
    # mutation reversing it is a no-op — that mutation survived until this
    # fixture existed. The bibliography puts `zeta` before `alpha` so source
    # order and key order disagree, and only the index rule gives this answer.
    TWO = ("\n\n## References\n\n"
           "Zeta, Q. (2001). First group, first member. Journal, 1(1), 1-10.\n\n"
           "Zeta, Q. (2001). First group, second member. Journal, 2(1), 1-10.\n\n"
           "Alpha, R. (2002). Second group, first member. Journal, 3(1), 1-10.\n\n"
           "Alpha, R. (2002). Second group, second member. Journal, 4(1), 1-10.\n")
    _ls3, d3 = dups_of("As shown (Zeta, 2001) and (Alpha, 2002) here.", refs=TWO)
    got = [x["reference_key"] for x in d3]
    if len(d3) != 2:
        failures.append(f"§12.4: the ordering fixture must produce two "
                        f"duplicate groups — got {len(d3)}")
    elif got != ["zeta|2001", "alpha|2002"]:
        failures.append(f"§12.4: duplicate_reference_key orders by smallest "
                        f"member reference_index, not by key — got {got}")
    elif sorted(got) == got:
        failures.append(f"§12.4: this fixture must distinguish index order "
                        f"from key order, and {got} is in key order too")
    else:
        ok(f"§12.4: {got} — ordered by smallest member index, against "
           f"alphabetical order of the keys")

    # §10 lists this among the nine suppressed types.
    p = Path(_tf.mkdtemp()) / "p.md"
    p.write_bytes((HEAD + "As shown (Felfe, 2006) here.\n\nPlain close.\n")
                  .encode("utf-8"))
    ls_abs, _c = ce.run(p, {"ampersand"})
    if any(r.get("type") == "duplicate_reference_key" for r in ls_abs):
        failures.append("§10: duplicate_reference_key is suppressed when the "
                        "bibliography is absent")
    else:
        ok("§10: no duplicate_reference_key without a bibliography")

    # ------------------------------------------------------------ §14, C-078
    #
    # rc2 §14 lists TWELVE finding conditions that force exit 1, and the list
    # is closed. The conformance map read "the exit-1 finding set is not
    # closed" until 23 September, which was wrong about rc2 and right about
    # this file: three proxies were tested, and eight of the twelve happened to
    # coincide with "not every citation uniquely matched".
    #
    # Three did not coincide, and each exited 0 where rc2 requires 1. All three
    # share a shape: they are findings about the BIBLIOGRAPHY, and no fact
    # about the bibliography alone can make a citation fail to match.
    print("\nrc2 §14 — the closed exit-1 finding set")

    # rc2's twelve, parsed from rc2 rather than retyped. A list typed here
    # would be a copy of FINDINGS_FORCING_EXIT1 and would agree with it
    # whatever either said.
    spec14 = [l.strip("- ").strip() for l in
              (rc2_spec_path().read_text(encoding="utf-8")
               .split("Exit 1 is forced by any of:")[1]
               .split("An `et_al`")[0].splitlines())
              if l.strip().startswith("-")]
    if len(spec14) != 12:
        failures.append(f"§14: expected twelve conditions in rc2's list, "
                        f"parsed {len(spec14)}; the section moved or the parse "
                        f"is wrong, and either way this block establishes "
                        f"nothing")
    elif len(ce.FINDINGS_FORCING_EXIT1) != len(spec14):
        failures.append(f"§14/C-078: rc2 lists {len(spec14)} finding "
                        f"conditions, this file evaluates "
                        f"{len(ce.FINDINGS_FORCING_EXIT1)}")
    else:
        ok(f"§14/C-078: all {len(spec14)} of rc2's finding conditions are "
           f"evaluated, and the set is closed")

    def exit_of(body, refs):
        p = Path(_tf.mkdtemp()) / "p.md"
        p.write_bytes((HEAD + body + refs).encode("utf-8"))
        ls, code = ce.run(p, {"ampersand"})
        return ls, code, ls[-1].get("exit_findings", [])

    CITED = "As shown (Smith, 2020) here."
    ONE = "\n\n## References\n\nSmith, J. (2020). A paper. Journal, 1(1), 1-10.\n"

    # Exit 0 has to be REACHABLE, or every case below passes for free.
    _ls, code, found = exit_of(CITED, ONE)
    if code != 0 or found:
        failures.append(f"§14: a clean document must exit 0 — got {code} "
                        f"with {found}. Every case below would then pass "
                        f"whatever the rule said")
    else:
        ok("§14: a clean document exits 0, so exit 1 below means something")

    # The three that do NOT coincide with "not uniquely matched". Each is a
    # fact about the bibliography, and the citation still matches perfectly.
    PAD = ("\n\nJones, K. (2019). B. Journal, 2(1), 1-10."
           "\n\nBrown, L. (2018). C. Journal, 3(1), 1-10."
           "\n\nDavis, M. (2017). D. Journal, 4(1), 1-10.\n")
    for label, refs, want in (
        ("residual uncited_reference",
         ONE.rstrip("\n") + PAD, "residual uncited_reference"),
        ("unresolved_reference",
         ONE.rstrip("\n") + "\n\na stray orphan line with no entry grammar"
         + PAD, "unresolved_reference"),
        ("any suspect reference",
         ONE.rstrip("\n") + "\n\nWilson, R. (2015). " + ("x" * 1600)
         + ". Journal, 9(1), 1-10." + PAD, "any suspect reference"),
    ):
        ls, code, found = exit_of(CITED, refs)
        um = [l for l in ls if l.get("type") == "summary"][0]
        if code != 1:
            failures.append(f"§14: {label} forces exit 1 — got {code}")
        elif want not in found:
            failures.append(f"§14: exit 1 came from {found}, not from the "
                            f"named condition {want!r}. Right answer, wrong "
                            f"reason")
        elif um["uniquely_matched_occurrences"] != um["extracted_citation_occurrences"]:
            failures.append(f"§14: this fixture must have EVERY citation "
                            f"uniquely matched, or the old proxy would have "
                            f"caught it and {label} proves nothing")
        else:
            ok(f"§14: {label} forces exit 1 with every citation still "
               f"uniquely matched")

    # C-002: "CRLF/lone CR→LF then NFC", canonical bytes exactly pinned.
    # Both directions matter. NFC composition SHORTENS the text — `e` + U+0301
    # is two code points and three bytes, `é` is one and two — so a document
    # that is not normalised produces coordinates against a longer string than
    # the one `canonical_sha256` names.
    raw = b"# P\r\n\r\nCafe\xcc\x81 said\r(Smith, 2020).\r\nNext.\n"
    got = ce.normalise(raw)
    want = "# P\n\nCafé said\n(Smith, 2020).\nNext.\n"
    if got != want:
        failures.append(f"§2/C-002: normalisation is not CRLF/CR→LF then NFC "
                        f"— got {got!r}, want {want!r}")
    elif len(got.encode("utf-8")) != len(want.encode("utf-8")):
        failures.append("§2/C-002: canonical byte length disagrees")
    else:
        ok("§2/C-002: CRLF and lone CR become LF, then NFC composes — "
           "canonical bytes are exactly pinned")

    # C-004, the converse of everything above: three counts legitimately stay
    # in CODE POINTS, and rc2 §1.3 lists them by name.
    #
    #     OSA edit distance unit         code point after NFC
    #     CORE minimum length            >= 2 code points
    #     reference overlong threshold   > 1500 code points
    #
    # The trap is symmetrical with the offsets one. Converting these to bytes
    # would also be silent: an accented surname would fail a CORE check it
    # passes, and a 1200-character reference with accents would be flagged
    # overlong. So each is exercised on input where bytes and code points
    # disagree, and the expected answer is the code-point one.

    # OSA over code points. `Müller` vs `Miller` is one substitution in code
    # points and two bytes apart in UTF-8 — ü is two bytes, i is one — so a
    # byte-based distance returns 2 and the rule's `<= 1` never fires.
    if ce._osa("müller", "miller") != 1:
        failures.append(f"§1.3/C-004: osa counts code points, not bytes — "
                        f"müller/miller is {ce._osa('müller', 'miller')}, "
                        f"want 1")
    elif ce._osa("smith", "smiht") != 1:
        failures.append("§1.3/C-004: osa must count a transposition as 1")
    else:
        ok("§1.3/C-004: osa is one substitution apart on müller/miller, so "
           "the unit is a code point")

    # CORE >= 2 code points. `Bé` is two code points and three bytes; a
    # byte-length floor would accept a one-code-point surname that happens to
    # be multi-byte, which is the failure that has no visible symptom.
    cits, _u, _e = extract("The result (Bé, 2020) holds.")
    if not cits or cits[0]["citation_key"] != "bé|2020":
        failures.append(f"§1.3/C-004: a two-code-point CORE must parse — "
                        f"got {keys(cits)}")
    else:
        cits2, _u2, _e2 = extract("The result (É, 2020) holds.")
        if cits2 and cits2[0].get("citation_key"):
            failures.append(f"§1.3/C-004: a one-code-point surname parsed as "
                            f"{keys(cits2)}; CORE's floor is being measured "
                            f"in bytes, where É is 2")
        else:
            ok("§1.3/C-004: CORE's floor is 2 code points — Bé parses, É "
               "does not, though both are 2+ bytes")

    # overlong > 1500 code points. An assembled entry of 1400 code points made
    # of 2-byte characters is 2800 bytes: well over the threshold if it were
    # read as bytes, well under it as code points.
    long_ref = "Müller, A. (2020). " + ("ü" * 1400) + ". Journal, 1(1), 1-10.\n"
    p = Path(_tf.mkdtemp()) / "p.md"
    p.write_bytes((HEAD + "A claim (Müller, 2020) holds."
                   + "\n\n## References\n\n" + long_ref).encode("utf-8"))
    ls, _c = ce.run(p, {"ampersand"})
    refs = [r for r in ls if r.get("type") == "reference"]
    if not refs:
        failures.append("§1.3/C-004: the overlong probe produced no reference")
    elif "overlong" in (refs[0].get("suspect_reasons") or []):
        failures.append(f"§1.3/C-004: a {len(long_ref)}-code-point entry "
                        f"({len(long_ref.encode())} bytes) was flagged "
                        f"overlong; the 1500 threshold is counting bytes")
    else:
        ok(f"§1.3/C-004: {len(long_ref.encode())} bytes of reference is not "
           f"overlong at {len(long_ref)} code points")

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("  the extractor agrees with §12 on the cases it pins, and with the")
    print("  two rules §12 leaves unstated that a mutation probe found unheld")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        import traceback
        print("\nCRASHED before the report. Controls that had already failed:")
        for _f in FAILURES:
            print("FAIL:", _f)
        if not FAILURES:
            print("  (none — the crash is the whole finding)")
        print()
        traceback.print_exc()
        sys.exit(1)
