# Citation specification: which document governs

Written 19 September 2026, because "send me the final citations spec" turned
out not to have a single answer.

```text
VERSION GOVERNING THE CODE   v3.3
AUTHORITATIVE                pending one confirmation from Alex Zamurko
```

## What exists

```text
citation-spec-v3.3.md
  sha256   239ee6bdd6cbdaf94f3e007d23fa47826ce2b11b60a03da0d9b667ba1a0a980e
  456 lines
  the document scripts/citation_extract.py is written from, clause by clause
  §4 grammar, §5 sentences, §6 envelope, §7 assembly, §8 reconciliation,
  §9 output contract, §10 exit codes, §12 conformance suite

citation-v3.4-rc1-architecture.md
  sha256   6a615c8136543ef492598196a918b2c1e4b62bb54fdbcca4bd12af28bac66cb0
  435 lines
  front matter says:  content_state: review_candidate
                      frozen_at: null
                      authoritative_source: docs/specs/citation_architecture_v3.4_rc1.md
  that path does not exist in this repository
  nothing implements this document

rc3
  sha256   ddc6f1f80c93d12d6268cda03fffb6720adac3b4bb9bc5da351f8c5a28a108e2
  NOT IN THIS REPOSITORY — a Slack attachment only
  frozen 3 September with the August corpus figures in its §I
  named repeatedly in the records; never read by the current implementation
```

Both files here were copied byte-for-byte from the attachments they came from
and verified against them before commit. Neither was converted, reformatted or
edited.

## So which is final?

Nobody can currently say, and that is the finding rather than an inconvenience.

- The **code** implements v3.3, and its 70-control conformance suite is built
  from v3.3 §12's own case list.
- **v3.4 rc1** declares itself a review candidate with `frozen_at: null`, so on
  its own terms it does not govern anything yet.
- **rc3** is described in the records as frozen, and is the document three
  correction classes were named against — the multi-token surnames, the
  institutional authors, the possessives. It is not here and has never been
  compared against v3.3.

The three cannot all be the final spec, and the version numbering does not
order them: rc3 post-dates v3.3 by numbering unknown, while v3.4 rc1 is
numerically later and explicitly unfrozen.

## What this means for the figures

Every citation accuracy number produced so far — 0.939 / 0.958 on paper 1,
0.873 / 0.989 on paper 2, 2130 parsed across the corpus — was produced by an
implementation of v3.3.

If rc3 is the governing specification, those numbers describe conformance to a
superseded document, and the gap between them is unmeasured because rc3 has
never been read here. That is not a claim that they are wrong. It is that
nothing currently establishes what they are conformance *to*.

`PROVENANCE-GAP.md` records the related problem for the August run: its
implementation is gone. This is the same shape on the specification side.

## What would settle it

One line naming the governing document, and rc3 in the repository so it can be
hashed and diffed against v3.3. If rc3 governs, the difference between the two
is the work; if v3.3 governs, rc3 should be recorded as superseded so it stops
being cited.

Until then this file says v3.3 governs the code, which is a statement about
what was built rather than about what should have been.
