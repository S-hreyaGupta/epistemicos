# A.1-E source manifest — 13 documents

Hashed 7 September 2026 from the files posted in #gap.

Byte counts match §12.1 of the source-document register on all thirteen, so the
register was built from exactly these bytes. Anything that does not match a line
below is not the artefact, whatever it is named locally.

```text
doc  file                                              bytes    sha256 (first 16)
D01  A1E_annotation_validation_protocol_v1-2.md        35,251   e4b2ec8ccbdc8943
D02  A1E_state_machine_v1-4 1.md                       24,022   bcff5718c4e73bd2
D03  A1E_resolution_spec_v1-0 5.md                    114,351   d458acb5839718a7
D04  A1E_verification_spec_v1-0.md                     74,922   b29bf81c0af88550
D05  A1E_extraction_spec_v1-0 5.md                     67,626   73b84b4a82ce69c4
D06  A1E_gap_extraction_contract_v1-2.md               51,842   b512bb90173232df
D07  A1E_boundary_rulebook_v1-2 1.md                   79,334   814934253cdf112b
D08  A1E_deficiency_predicate_registry_v1-1 2.md       87,271   9bf36dd9b05b63ce
D09  A1E_gap_object_schema_v1-4.md                     82,067   095ae8902c01dbcc
D10  A1E_candidate_detection_v1-0 4.md                 97,206   92904551dc4add74
D11  A1E_object_rules_v1-1 2.md                       122,287   132ff40575581bb6
D12  A1E_merge_gap_identity_v1-0 8.md                 164,557   2f44ac4fc1a56109
D13  A1E_signal_library_v1-1 2.md                     128,372   1274316bacc9390e
```

The trailing ` 1`, ` 2`, ` 4`, ` 5`, ` 8` in nine filenames are browser download
suffixes, not version information. No document states them. Downstream documents
pin the same artefacts by names without the suffixes, so whether a pinned name
refers to one of these files is unestablished by the documents themselves. The
hashes above are what resolves that, not the names.

## Verified against the register, 7 September

Three claims checked directly rather than taken from the register.

**Self-declared FROZEN — seven, confirmed.** D01, D06, D07, D08, D11, D12, D13
each carry a literal "declared FROZEN at v1.x" at their own foot.

**Not frozen — six, confirmed.** D02, D03, D04, D05, D09, D10 each state
"READY FOR INDEPENDENT FREEZE AUDIT", "not self-frozen", "NOT YET FROZEN" or
"READY FOR INDEPENDENT AMENDMENT AUDIT".

**The contradiction — confirmed, D03 line 12 verbatim:**

> Pinned frozen inputs (all frozen): contract v1.2 · `A1E-GS-1.4` · protocol
> v1.2 · `A1E-SM-1.4` · `A1E-BR-1.2` · `A1E-DPR-1.1` · `A1E-SL-1.1` ·
> `A1E-OR-1.1` · `A1E-GI-1.0` · `A1E-CD-1.0` · `A1E-EX-1.0`.

Four of those — GS-1.4, SM-1.4, CD-1.0, EX-1.0 — deny it about themselves.

**Absent inputs — nine documents, not six.** `SM-1.3` and `GS-1.3` are
referenced 48 times across nine of the thirteen. D11 alone cites them 26 times.
Neither file exists in the set.

## D05 already found and fixed this

Worth separating from the rest, because it changes what the fix looks like.

The extraction spec corrected its own dependency-status language in two
same-version rounds:

> **11C:** dependency-status language corrected — `A1E-SM-1.4` is pinned as the
> required State Machine interface but is not described as frozen anywhere in
> active normative text

> **11D:** all remaining active descriptions of the State Machine as frozen
> corrected to pinned-interface wording

And it audited itself for the correction under a rule worth quoting in full:

> mechanical audit performed under the ANTI-WHITELIST RULE — expectations
> derived from the normative dependency state (`A1E-SM-1.4` = PINNED /
> DEPENDENCY-GATED / NOT FROZEN), no wording accepted because a prior
> same-version audit accepted it, and every residual frozen/State-Machine
> co-occurrence individually classified rather than pattern-whitelisted.

So this is not thirteen documents disagreeing. One document identified the exact
defect, fixed it, and refused to trust its own previous audit while doing so.
D03 and D04 have not adopted that correction.

The fix is therefore narrower than "resolve the frozen-status inconsistency": it
is applying D05's pinned-interface wording to D03 line 12 and D04's equivalent.
