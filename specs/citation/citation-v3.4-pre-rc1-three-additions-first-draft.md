# Citation spec v3.3 → v3.4 — the three additions

**Date:** 21 August 2026
**Measured against:** the eleven ingested papers

Three things were asked for. One is already in the spec, one is half there, one
is genuinely missing. There is also a fourth thing that has to be fixed first,
because on our own corpus the spec stops before any of the three matter.

---

## 0. The blocker: four of eleven papers abort before extraction begins

§3.3 exits 3 when no h2–h4 heading is named `references`, `bibliography` or
`works cited`. Run against what we actually have:

```
paper      h1  h2   references section     verdict
17bef7c6    2  10   -                      EXIT 3
2af68a7f    1   6   -                      EXIT 3
43338825    1  45   REFERENCES             proceeds
5da73cf4    0   7   REFERENCES             proceeds
849f8fc6    1  24   References             proceeds
ad1e3ff9    1  10   REFERENCES             proceeds
bf2fdc4a    1   6   -                      EXIT 3
c1d56945    0   9   References             proceeds
c22df19f    1  12   References             proceeds
ea07e5f5    2  13   References             proceeds
ed6a890a    1   6   -                      EXIT 3
```

**Four of eleven produce no output at all.** Not a bad answer — no answer. Those
four are the papers where Mathpix emitted "References" as body text rather than
as a heading, which is the same fault Step 3 v2.9 already fixes on our side.

The spec should recover the same way, and say when it did.

### Replacement for §3.3

> ### 3.3 References section (exit 3)
>
> Starts at the first h2–h4 heading with `lower(clean(name))` ∈
> { `references`, `bibliography`, `works cited` }; ends before the next heading
> of level ≤ that heading's level, else EOF.
>
> **Fallback, applied only when no such heading exists.** Scan for a line whose
> entire trimmed content, lowercased, is one of the three names. It starts the
> references section iff at least **three** of the following ten non-blank
> trimmed lines match `ENTRY_START` (§4). The section ends at the next h1–h6
> heading, else EOF. The threshold makes a passing mention of the word
> "references" in prose unable to trigger it.
>
> Absent under both rules → exit 3.
>
> The `meta` record gains `references_source` ∈ { `heading`, `inferred` }. A
> bibliography found by fallback is a weaker premise than one the document
> marked, and a downstream absence claim resting on it should be able to say so.

**Also amend §12**, conformance suite, a new row:

| class | must cover |
|-------|-----------|
| references fallback | plain-text `References` line followed by 3 entry-start lines → section found, `references_source:"inferred"`; the same line followed by 2 → exit 3; the word "references" in a prose sentence never triggers it; heading present → `"heading"` and the fallback never runs |

---

## 1. Positioning of the reference

**Half of this already exists.** §6.3 emits `section_level`, `section_name`,
`section_type` and `section_roles` from §3.4's stack, and `sentence_position` ∈
{ start, middle, end }. Section positioning is done and needs nothing.

What does not exist is anything **relative to the previous sentence**.
`sentence_position` describes where the citation sits inside its own sentence,
which is a different question.

Why it matters, and how often: a citation occupying an entire sentence of its own
—

> Wedding vendors adapted rapidly. (Smith, 2020).

— makes no claim in its own sentence. It supports the preceding one. Measured
across the seven papers that currently proceed: **10 of 908 citations**, 1.1%.
Rare, and unambiguous when it occurs, which is the right profile for a
deterministic flag.

### Additions to §6.3, after `sentence_position`

> - `sentence_index` = 0-based ordinal of the containing sentence among body
>   sentences in source order, continuous across sections. This is what makes
>   adjacency computable: two citations are in consecutive sentences iff their
>   indices differ by one.
> - `previous_sentence_end` = `content_end` of the sentence at
>   `sentence_index − 1`, or `null` when this is the first body sentence.
>   Emitted rather than left to be recomputed, because recovering it requires
>   re-running §5 over the whole document to find one offset.
> - `standalone` = `true` iff `group_start = sentence_start` **and**
>   `group_end = content_end` — the citation group is the entire sentence
>   content. Such a citation asserts nothing in its own sentence and attaches
>   backwards.
>
> All three are derived from spans §5 and §6.3 already compute. Nothing new is
> parsed and the determinism claim is unaffected.

**Deliberately not added:** any judgement about *what* the citation attaches to.
`standalone` says the sentence carries no claim of its own; it does not say the
previous sentence is the supported claim, because a citation can equally support
a whole preceding paragraph. That is claim–citation linking, which §0 puts out of
scope.

**§9 block 2** gains the three fields after `sentence_position`, in that order.

**§12** gains:

| class | must cover |
|-------|-----------|
| sentence relations | `sentence_index` continuous across a heading boundary; `previous_sentence_end` null for the first body sentence; `standalone` true for a citation-only sentence with and without a trailing period, false when one word precedes it |

---

## 2. Output format for the file

§9 is complete for **stdout** and specifies nothing about a file. Four things are
needed, and one of them is the whole point.

### New §9.1

> ### 9.1 File output
>
> `--out <path>` writes the byte-identical stream of §9 to `<path>`. Absent
> `--out`, behaviour is unchanged.
>
> **The determinism claim extends to the file.** Same input bytes → identical
> file bytes. It follows that no field may be derived from the clock, the
> filesystem, the run, or the machine — a `generated_at` timestamp in `meta`
> would break the claim, and is the obvious thing someone adds later without
> noticing. Stated here so that it is a rule rather than an oversight.
>
> **Default name**, when the caller supplies a directory rather than a file:
> `<sha256-of-normalized-input>.citations.jsonl`, hex, lowercase, over the text
> after §2 normalization. Content-derived so that re-running overwrites one file
> with identical bytes instead of accumulating near-copies, and so that a file
> can be matched to its input without a side table.
>
> **Atomic write.** Write to a temporary file in the destination directory, then
> rename over the target. A crashed or killed run must never leave a truncated
> file in place: JSONL is line-oriented, so a half-written file parses cleanly as
> fewer records — silent loss with no error, which is the one failure this spec
> is otherwise built to make impossible.
>
> **Completeness marker.** The `summary` record is last (§9), so a file whose
> final line is not a `summary` or an `error` record is incomplete and MUST be
> treated as a failed run regardless of the process exit code.
>
> **On exit 2–5** the two-line error output of §10 is written to the file as
> well. A run that aborted should leave a file saying why, not no file at all —
> absence is indistinguishable from "never ran".

**§12** gains:

| class | must cover |
|-------|-----------|
| file output | `--out` bytes identical to stdout bytes; default filename equals the input hash; two runs over one input produce one file, byte-identical; an abort leaves a two-line file; a file not ending in `summary`/`error` is rejected by the harness |

---

## 3. Compare in-text with the reference list

**This is largely done and better than asked for.** §8 already produces
`missing_reference`, `uncited_reference`, `ambiguous_citation`,
`duplicate_reference_key` and `possible_mismatch` with three named repair rules.
Nothing there needs adding.

But it compares **keys**, and the key is `surname|year`. Everything else the
in-text form asserts is thrown away before the comparison — and one of those
things is asserted by nearly half of all citations.

### The gap, measured

`et al.` appears in **438 of 908 citations, 48.2%** across the seven papers that
currently proceed.

`Smith et al. (2020)` asserts a work with three or more authors. Its key is
`smith|2020`. A reference reading `Smith, J. (2020). …` — one author — has the
identical key and matches cleanly. The inventory reports success. There are two
different works and nothing in the output says so.

The same holds in the other direction: `Smith (2020)` against a five-author
reference, and `Smith & Jones (2020)` against a three-author one.

This is **structural** coherence, not validity, so it sits inside §0's scope line
rather than outside it.

### Addition to §7, per entry

> `author_count` = the number of author positions in `assembled` before the first
> YEAR, counted as matches of `(?:PARTICLE WS)*CORE, WS INITIALS` separated by
> `,` or `&`/`and`. `null` when the count is not confidently derivable — a
> reference using full forenames, or one containing `et al.` itself. A `null`
> takes no part in the check below.

### New §8 step, after step 6

> **6a. `author_count_mismatch`** over matched works only — keys in
> `matched_work_keys` whose single reference has a non-null `author_count`.
>
> The citation's assertion is read from its own form:
>
> | in-text form | asserts |
> |---|---|
> | `SURNAME et al.` | `>= 3` |
> | `SURNAME & SURNAME`, `SURNAME and SURNAME` | `== 2` |
> | serial list of *n* surnames | `== n` |
> | `SURNAME` alone | `== 1` |
>
> Emit one record per (citation_key, reference_index) pair whose assertion is
> contradicted by `author_count`. The match itself is NOT withdrawn: the key
> still matched, and a mismatch here is a finding about the pair rather than a
> reason to declare the reference missing.
>
> **`>= 3` is the APA reading and is style-dependent.** Older APA and several
> other styles use `et al.` from the fourth author, some from the second. The
> conservative rule is therefore `>= 3`, which flags only the unambiguous
> failures — `et al.` against a one- or two-author reference — and stays silent
> on the disputed boundary.

### New §9 block, between 10 and 11

```
{"type":"author_count_mismatch","citation_key":"…","reference_index":0,"asserted":"…","reference_author_count":0,"example":"…"}
```

`asserted` ∈ { `">=3"`, `"==1"`, `"==2"`, `"==3"` … }, verbatim from the table.
Ordered by first-occurrence order of the citation key. **§7's `reference` block
gains `author_count` after `year`.**

### Exit code: deliberately NOT changed

§8 step 8 lists what forces exit 1. `author_count_mismatch` should **not** join
it, at least not in v3.4. Every other member of that list is a structural defect
in the document; this one rests on a style convention the spec cannot observe,
and making it fail a run would mean an inventory that refuses papers over a
disagreement about when `et al.` begins.

Emit it, count it, and decide after a calibration run over the corpus.

**§12** gains:

| class | must cover |
|-------|-----------|
| author agreement | `Smith et al. (2020)` against a one-author reference → mismatch, match retained; against a three-author reference → silent; `Smith & Jones (2020)` against three authors → mismatch; reference with full forenames → `author_count:null`, no record; reference containing `et al.` → `null`; mismatch does not affect the exit code |

---

## Order of work

| | Amendment | Papers affected today | Kind |
|---|---|---|---|
| 0 | References-section fallback | **4 of 11 — no output at all** | blocking |
| 3 | Author-count agreement | 438 of 908 citations carry `et al.` | behaviour |
| 1 | Sentence-relative positioning | 10 of 908 standalone | additive |
| 2 | File output contract | all | contract |

**Amendment 0 first, and it is not close.** The other three describe fields on
output that four of our eleven papers never reach.

---

## A note on the measurements

The counts in §1 and §3 come from a simplified implementation of the spec's own
grammar, run over the seven papers that pass §3.3 today — enough to size the
amendments, not enough to be the spec's own numbers. The §0 table is exact: it
implements §3.1, §3.2 and §3.3 as written.
