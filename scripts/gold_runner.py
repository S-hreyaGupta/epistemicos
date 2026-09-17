#!/usr/bin/env python3
"""§15 Gold Set validation: score a candidate, and refuse to let a total hide a loss.

    python scripts/gold_runner.py --gold <gold.json> --candidate <candidate.json>
    python scripts/gold_runner.py --gold <gold.json> --candidate <c.json> \
        --baseline <b.json>

Exit 0 = scored, and nothing the protocol calls unacceptable was found.
Exit 1 = refused; nothing scored.
Exit 3 = scored, and there are regressions. §15.1: "Aggregate improvement does
         not override an unacceptable regression."

The sentence this exists for
----------------------------
§15.1 requires six comparisons and then says aggregate improvement does not
override an unacceptable regression. A runner that reported one accuracy figure
would satisfy the letter of "aggregate performance" and defeat the sentence,
because the one number a regression is easiest to hide inside is the total. So a
regression here is its own exit code, not a line in a report someone may not
read to the end.

A regression is a case the baseline got right and the candidate gets wrong. It
is not the same as a new false positive and is reported separately, because the
repair for each is different.

Identity, not position
----------------------
Gold items are matched on a declared key, never on where they appear in the
source. Byte offsets move whenever an upstream transform lands — the citation
work has two such transforms specified and unimplemented — and a gold set keyed
to offsets stops matching without anything erroring. The key is whatever the
gold set declares in `key_fields`; the runner does not choose it.

No baseline
-----------
§15.2: record `BASELINE_GOLD_RESULT = NOT_APPLICABLE` and evaluate against
predefined acceptance criteria. The criteria must be supplied and must have been
written before the run: `--criteria` takes a file, and the report records its
hash. Criteria invented after seeing the score are not criteria, and this tool
cannot detect that — it records the hash so someone else can.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class Refused(Exception):
    """Exit 1, score nothing."""


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p: Path, what: str) -> dict:
    if not p.is_file():
        raise Refused(f"{what} not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise Refused(f"{what} is not valid JSON: {e}")


def key_of(item: dict, fields: tuple[str, ...]) -> tuple:
    """The identity of one item, built only from the declared fields."""
    return tuple(str(item.get(f, "")).strip().lower() for f in fields)


def items_of(doc: dict, fields: tuple[str, ...], what: str) -> dict[tuple, dict]:
    raw = doc.get("items")
    if raw is None:
        raise Refused(f"{what} has no `items` array")
    out: dict[tuple, dict] = {}
    for it in raw:
        k = key_of(it, fields)
        if not any(part for part in k):
            raise Refused(
                f"{what} contains an item with no value in any key field "
                f"{fields}. An item with an empty identity matches every other "
                f"empty one, which would score as agreement.\n  {it}")
        # Duplicates are kept as counts rather than collapsed: two occurrences
        # of one citation are two occurrences, and silently deduplicating them
        # would move the denominator without saying so.
        n = 1
        base = k
        while k in out:
            n += 1
            k = base + (f"#{n}",)
        out[k] = it
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="gold_runner.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gold", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--baseline", default="",
                    help="§15.1. Omit for §15.2, which needs --criteria.")
    ap.add_argument("--criteria", default="",
                    help="§15.2 predefined acceptance criteria, written before "
                         "the run")
    ap.add_argument("--out", default="", help="write the report here as well")
    a = ap.parse_args()

    gold_p = Path(a.gold).resolve()
    gold = load(gold_p, "gold set")

    fields = tuple(gold.get("key_fields") or ())
    if not fields:
        raise Refused(
            "the gold set declares no `key_fields`, so there is no stated basis "
            "for deciding whether a candidate item is the same item.\n"
            "  The runner will not choose one: a matching rule invented here "
            "would be a second\n  definition of identity, and the gold set is "
            "the first.")

    cand_p = Path(a.candidate).resolve()
    cand = load(cand_p, "candidate")

    # The gold set is written against one exact source. A candidate produced
    # from different bytes is not scoreable against it, and scoring it anyway
    # is how a gold set silently stops measuring anything.
    g_src = (gold.get("source") or {}).get("sha256")
    c_src = (cand.get("source") or {}).get("sha256")
    if g_src and c_src and g_src != c_src:
        raise Refused(
            "the candidate was produced from different source bytes than the "
            "gold set was written against.\n"
            f"  gold      {g_src}\n"
            f"  candidate {c_src}\n"
            "  Re-annotate against the new source, or run the candidate "
            "against the old one. Scoring\n  across the two measures the "
            "difference between the texts, not the extractor.")
    if not g_src or not c_src:
        unbound = True
    else:
        unbound = False

    G = items_of(gold, fields, "gold set")
    C = items_of(cand, fields, "candidate")

    tp = sorted(set(G) & set(C))
    fn = sorted(set(G) - set(C))          # gold says it is there, candidate missed it
    fp = sorted(set(C) - set(G))          # candidate produced it, gold does not have it

    R: list[str] = []
    W = R.append
    W("# Gold Set validation — §15")
    W("")
    W(f"gold set   `{gold.get('gold_set', gold_p.name)}`  "
      f"sha256 `{sha256_file(gold_p)}`")
    W(f"candidate  `{cand_p.name}`  sha256 `{sha256_file(cand_p)}`")
    W(f"identity   `{' + '.join(fields)}` — declared by the gold set, not "
      f"chosen here")
    W("")
    if unbound:
        W("> Neither the gold set nor the candidate records the SHA-256 of the "
          "source it was made from, so this run cannot establish that they "
          "describe the same text. The score below is only as good as that "
          "assumption.")
        W("")

    W("## Candidate against gold")
    W("")
    W(f"- gold items            {len(G)}")
    W(f"- candidate items       {len(C)}")
    W(f"- correct (TP)          {len(tp)}")
    W(f"- missed (FN)           {len(fn)}")
    W(f"- spurious (FP)         {len(fp)}")
    recall = len(tp) / len(G) if G else 0.0
    precision = len(tp) / len(C) if C else 0.0
    W(f"- recall                {recall:.3f}")
    W(f"- precision             {precision:.3f}")
    W("")

    exit_code = 0

    if a.baseline:
        # ---- §15.1, the six comparisons ----
        base_p = Path(a.baseline).resolve()
        base = load(base_p, "baseline")
        b_src = (base.get("source") or {}).get("sha256")
        if g_src and b_src and g_src != b_src:
            raise Refused(
                "the baseline was produced from different source bytes than "
                "the gold set.\n  Comparing it with the candidate would "
                "measure two texts, not two extractors.")
        B = items_of(base, fields, "baseline")

        b_tp = set(B) & set(G)
        c_tp = set(C) & set(G)

        regressions = sorted(b_tp - c_tp)     # baseline right, candidate wrong
        improvements = sorted(c_tp - b_tp)    # candidate right, baseline wrong
        retained = sorted(b_tp & c_tp)
        new_fp = sorted((set(C) - set(G)) - (set(B) - set(G)))
        new_fn = sorted((set(G) - set(C)) - (set(G) - set(B)))

        W("## §15.1 — baseline against candidate")
        W("")
        W(f"baseline   `{base_p.name}`  sha256 `{sha256_file(base_p)}`")
        W("")
        W("§15.1 requires all six. They are separate because the repair for "
          "each is different.")
        W("")
        W(f"- targeted improvements          {len(improvements)}")
        W(f"- previously correct, retained   {len(retained)}")
        W(f"- new false positives            {len(new_fp)}")
        W(f"- new false negatives            {len(new_fn)}")
        W(f"- **regressions**                **{len(regressions)}**")
        W(f"- aggregate: baseline {len(b_tp)}/{len(G)} correct, "
          f"candidate {len(c_tp)}/{len(G)}")
        W("")

        if regressions:
            exit_code = 3
            W("### Regressions")
            W("")
            W("§15.1: *aggregate improvement does not override an unacceptable "
              "regression.* Each of these was correct before and is not now. "
              "Whether any is acceptable is a human decision; this tool only "
              "refuses to let the total speak for them.")
            W("")
            for k in regressions:
                it = B[k]
                W(f"- `{' · '.join(str(x) for x in k)}`")
                if it.get("context"):
                    W(f"  - {it['context'][:160]}")
            W("")
            net = len(improvements) - len(regressions)
            if net > 0:
                W(f"> The candidate is ahead on aggregate by {net}. That is "
                  f"reported and it settles nothing: {len(regressions)} case(s) "
                  f"that worked no longer do.")
                W("")
    else:
        # ---- §15.2, no executable baseline ----
        W("## §15.2 — no executable baseline")
        W("")
        W("```text")
        W("BASELINE_GOLD_RESULT = NOT_APPLICABLE")
        W("```")
        W("")
        if not a.criteria:
            raise Refused(
                "no baseline and no --criteria.\n"
                "  §15.2 evaluates the candidate against predefined acceptance "
                "criteria. Without them\n  there is a score and nothing to "
                "judge it against, and a threshold chosen after seeing\n  the "
                "score is not a criterion.")
        crit_p = Path(a.criteria).resolve()
        if not crit_p.is_file():
            raise Refused(f"acceptance criteria not found: {crit_p}")
        W(f"Acceptance criteria: `{crit_p.name}`  sha256 "
          f"`{sha256_file(crit_p)}`")
        W("")
        W("The hash is recorded so that someone else can establish the "
          "criteria predate this run. This tool cannot: it sees the file, not "
          "when it was written.")
        W("")
        W(quote_file(crit_p))
        W("")

    # ---- the misses, always, and never folded into a rate ----
    if fn:
        W("## Missed by the candidate")
        W("")
        for k in fn[:60]:
            it = G[k]
            W(f"- `{' · '.join(str(x) for x in k)}`")
            if it.get("context"):
                W(f"  - {it['context'][:160]}")
        if len(fn) > 60:
            W(f"- … and {len(fn) - 60} more")
        W("")
    if fp:
        W("## Produced but not in the gold set")
        W("")
        W("Either the candidate is wrong or the gold set is incomplete. The "
          "second is common on a first annotation pass and is not a failure of "
          "the candidate; it is a reason to re-read the source.")
        W("")
        for k in fp[:60]:
            W(f"- `{' · '.join(str(x) for x in k)}`")
        if len(fp) > 60:
            W(f"- … and {len(fp) - 60} more")
        W("")

    report = "\n".join(R) + "\n"
    if a.out:
        dest = Path(a.out).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
        print(f"wrote {dest}")
    else:
        print(report)

    if exit_code == 3:
        print(f"REGRESSIONS: {len(regressions)}. §15.1 — aggregate improvement "
              f"does not override an unacceptable regression.", file=sys.stderr)
    return exit_code


def quote_file(p: Path) -> str:
    return "```text\n" + p.read_text(encoding="utf-8").rstrip() + "\n```"


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
