# Self-found, pending cycle 01

Defects found by the implementing agent on 17 September, after the cycle-01
target was frozen at `813d780c…` and before any review has run.

Under Alex Zamurko's ruling of 16 September these are admissible to the ledger
with `SOURCE = IMPLEMENTER_SELF_FOUND`, persistent identifiers and ordinary
lifecycle state. They are held here rather than raised because BOOTSTRAP-002 has
no cycle on record yet, and a `C01-Fnn` identifier raised before cycle 01's
review would put the agent's own findings and the reviewer's under one cycle
with nothing separating them.

**Nothing below has been repaired, deliberately.** Every file named is in the
frozen target. Editing one now would put an unreviewed change into a file under
review, which is the condition this run exists to prevent.

---

## 1. A refusal with no control, found by naming a different one

`scripts/test_run_review.py` had a control called *a drifted spec is not embedded
under its old hash*, which read as a control over the snapshot comparison in
`cmd_freeze`. It asserted only that freeze refused. Made to assert *why*, it
turned out the run-pin check refuses first and the snapshot comparison is never
reached.

That comparison — `run_review.py:1012` — appears unreachable by any fixture. It
hashes the copy it has just written against a hash taken from the same file a
few lines earlier in the same call, so the two differ only if the file changes
on disk between those two reads.

The control has been renamed to what it demonstrates. The branch is untouched.

## 2. Refusals no control names — five of 107

Measured by taking every `raise Refused` / `raise FormatError` in the nine
covered modules and asking whether any 14-character run of its message appears
in any of the five suites. 102 of 107 are named by a control. These five are
not:

```text
run_review.py:219       cannot resolve git HEAD; the run must pin a commit
run_review.py:903       cannot resolve the tree of <commit>
ledger.py:569           <id> is already RESOLVED
bootstrap_gate.py:718   runner not found
bootstrap_gate.py:741   this exact runner is already approved
```

Three are plainly reachable and simply untested: resolving a finding twice,
approving a runner that does not exist, approving the same runner twice.

Two are defensive branches of the same family as item 1. `cannot resolve the
tree` fires only if a commit that `rev-parse` has already resolved has no tree.

**The measurement is crude and its first version was wrong.** It initially
reported 95 of 107 unmatched, because it extracted long fragments of each
message while the controls assert short needles. The number above is from the
corrected method and has not been checked by anyone else. A reviewer should
treat 102 as an estimate.

## 3. The evidence schema may not be reviewable by this machinery at all

Found 18 September, while preparing the pin amendment that was supposed to bring
`specs/evidence-schema-v1.0.md` into cycle 02's target. The amendment is not the
answer, and the reason is worth stating.

The schema is one of the ten components the gate covers. Cycle 01 could not
review it because it is this run's governing pin, and `run_pins.py` is explicit
that an artifact governs a run or is reviewed by it, never both. The plan was an
amendment moving it between roles at cycle 02.

An amendment changes the pin role. It does not change this:

```text
findings_format.py:91   reads specs/evidence-schema-v1.0.md at run time for
                        FINDING_ID_GRAMMAR, from the live path, not from any
                        frozen copy
```

And the schema is not incidental to a cycle. It defines the directory layout,
`target.json`, `target.sha256`, `codex-input.md` and the Finding ID grammar — it
defines what a cycle's evidence *is*. So a cycle reviewing the schema produces
evidence structured by the document under review, and records findings whose
identifiers are validated against a grammar declared in the document under
review. Changing its pin role does not touch either.

**The sharp form.** A defect in the schema severe enough to matter is a defect
that prevents the review that would find it. If the schema declared a
`FINDING_ID_GRAMMAR` that refused valid identifiers, no finding about that could
be recorded. The failure mode and the detection mechanism are the same document.

This is not fatal and it is not an argument for skipping the schema. A human can
read it directly, and MC-2's checks over a cycle are mostly structural rather
than schema-derived. But it means the gate covering ten components covers nine
of them in the way it claims, and the tenth differently, and nothing currently
says so. A reader of `bootstrap_gate.py` would reasonably assume all ten are
reviewable the same way.

**Not repaired, and no amendment written.** The options are a second schema to
review the first against, which does not exist; accepting stable circularity and
recording it; or declaring the schema outside what this process can review and
handling it by direct human reading. That is a decision, not a fix, and it
belongs to the human at the gate rather than to the implementing agent who found
it.

## 4. What this says about the resolved set

Items 1 and 2 are the shape cycle 04 named: something green for a reason other
than the one it is named for. Item 1 was green for four review cycles.

Item 3 is a different shape and worth separating rather than lumping in. Nothing
there is broken or mislabelled; the machinery does what it says. What is wrong is
the scope of a claim — the gate covers ten components and one of them cannot be
covered the way the other nine are.

What the three share is how they were found. None came from a control failing.
All three came from asking a question no control asks: what does this control
actually demonstrate, which refusals has nobody named, and can this component be
reviewed at all.

That is the argument for the twenty-five. Twenty-five findings in BOOTSTRAP-001
are marked `RESOLVED` on controls written the same way, and six of those were
never re-verified. A green suite is evidence that the questions someone thought
to ask are answered, and nothing more.
