#!/usr/bin/env python3
"""Controls for the extractor-output to gold-candidate adapter.

    python scripts/test_citation_candidate.py

Exit 0 = every control fired.

Not in `refresh_counts.SUITES`: this file is not in the review target and is not
reached through `bootstrap_gate.covered()`.

The adapter sits between two things that must not be allowed to agree by
construction. The gold set keys on the author phrase a human read; the extractor
also emits the phrase it read. If the adapter ever fell back on `citation_key`
instead, the comparison would test whether the extractor agrees with its own
surname derivation, which is the grammar under test.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent
REPO = SRC.parent


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SRC / "citation_candidate.py"), *args],
        cwd=str(REPO), capture_output=True, text=True)


def jsonl(p: Path, recs) -> Path:
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return p


def main() -> int:
    failures: list[str] = []
    t = Path(tempfile.mkdtemp())

    def ok(m: str) -> None:
        print(f"  [ok] {m}")

    def refuses(label: str, needle: str, *args: str) -> None:
        r = run(*args)
        blob = r.stdout + r.stderr
        if r.returncode != 1:
            failures.append(f"{label}: expected exit 1, got {r.returncode}\n{blob[:300]}")
        elif needle.lower() not in blob.lower():
            failures.append(f"{label}: refused for the wrong reason\n"
                            f"  wanted {needle!r}\n  got {blob.strip()[:220]}")
        else:
            ok(f"refused: {label}")

    print("citation candidate adapter")

    good = [{"type": "citation", "candidate_state": "parsed",
             "author_phrase": "Smith", "year": "2020"}]

    refuses("extractor output that is not there", "not found",
            "--output", str(t / "absent.jsonl"), "--paper", "paper-1",
            "--out", str(t / "o.json"))

    refuses("a gold set that does not exist", "no gold set",
            "--output", str(jsonl(t / "a.jsonl", good)), "--paper", "paper-9",
            "--out", str(t / "o.json"))

    (t / "bad.jsonl").write_text('{"type": "citation"\n', encoding="utf-8")
    refuses("output that is not valid JSON", "not valid JSON",
            "--output", str(t / "bad.jsonl"), "--paper", "paper-1",
            "--out", str(t / "o.json"))

    # rc3 §A requires author_phrase on every citation record. A parsed citation
    # without one cannot be scored against a phrase-keyed gold set, and the
    # adapter must not reconstruct it from citation_key: that derivation is the
    # thing under test.
    refuses("parsed citations that carry only a citation_key",
            "author_phrase",
            "--output", str(jsonl(t / "keyonly.jsonl", [
                {"type": "citation", "candidate_state": "parsed",
                 "citation_key": "person|smith|2020"}])),
            "--paper", "paper-1", "--out", str(t / "o.json"))

    # ---- the collapse ----
    recs = [{"type": "citation", "candidate_state": "parsed",
             "author_phrase": "Smith", "year": "2020"} for _ in range(4)]
    recs += [{"type": "citation", "candidate_state": "parsed",
              "author_phrase": "Jones", "year": "2021"}]
    recs += [{"type": "citation", "candidate_state": "unresolved_citation",
              "author_phrase": "Panel Smith"}]
    recs += [{"type": "citation", "candidate_state": "excluded_candidate",
              "author_phrase": "https://example.com/2019"}]
    out = t / "cand.json"
    r = run("--output", str(jsonl(t / "many.jsonl", recs)), "--paper", "paper-1",
            "--out", str(out))
    if r.returncode != 0:
        failures.append(f"a normal conversion failed:\n{r.stdout}{r.stderr}")
    else:
        d = json.loads(out.read_text(encoding="utf-8"))
        if len(d["items"]) != 2:
            failures.append(f"five parsed occurrences of two works became "
                            f"{len(d['items'])} items, not 2")
        elif d["collapsed"]["parsed_occurrences"] != 5:
            failures.append(
                f"the occurrence count behind the collapse is "
                f"{d['collapsed']['parsed_occurrences']}, not 5. Without it "
                f"nobody reading the score can tell how much repetition stood "
                f"behind it.")
        else:
            ok("occurrences collapse to distinct works, and the ratio is stated")

        # A declined candidate is the extractor refusing. Counting it as an
        # extraction would score a refusal as a success.
        if any(i["author_phrase"].startswith("panel") or
               i["author_phrase"].startswith("http") for i in d["items"]):
            failures.append("an unresolved or excluded candidate was scored as "
                            "an extracted citation; the extractor declined and "
                            "this counts it as a success")
        elif d["candidate_states"]["unresolved_citation"] != 1 or \
                d["candidate_states"]["excluded_candidate"] != 1:
            failures.append(f"the non-parsed states were not counted: "
                            f"{d['candidate_states']}")
        else:
            ok("unresolved and excluded candidates are counted, not scored")

        if d["key_fields"] != ["author_phrase", "year"]:
            failures.append(f"the candidate declares {d['key_fields']}, which "
                            f"is not what the gold set keys on")
        else:
            ok("identity is taken from the gold set, not chosen by the adapter")

    # ---- it must actually score against the real gold set ----
    real = json.loads(
        (REPO / "specs" / "gold" / "citation-paper-1-v0.1.json")
        .read_text(encoding="utf-8"))
    exact = [{"type": "citation", "candidate_state": "parsed",
              "author_phrase": i["author_phrase"], "year": i["year"]}
             for i in real["items"]]
    c2 = t / "exact.json"
    run("--output", str(jsonl(t / "exact.jsonl", exact)), "--paper", "paper-1",
        "--out", str(c2))
    crit = t / "crit.md"; crit.write_text("recall >= 0.95\n", encoding="utf-8")
    g = subprocess.run(
        [sys.executable, str(SRC / "gold_runner.py"),
         "--gold", str(REPO / "specs" / "gold" / "citation-paper-1-v0.1.json"),
         "--candidate", str(c2), "--criteria", str(crit)],
        cwd=str(REPO), capture_output=True, text=True)
    if g.returncode != 0:
        failures.append(f"the adapter's output did not score: {g.stderr[:300]}")
    elif "recall                1.000" not in g.stdout:
        failures.append(
            "a candidate built from the gold set's own phrases did not score "
            "1.0 against it, so the adapter and the gold set disagree about "
            f"identity somewhere.\n{g.stdout[:400]}")
    else:
        ok("a candidate carrying the gold set's own phrases scores 1.0 "
           "end to end")

    shutil.rmtree(t, ignore_errors=True)
    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("  extractor output reaches the gold runner without either side "
          "bending toward the other")
    return 0


if __name__ == "__main__":
    sys.exit(main())
