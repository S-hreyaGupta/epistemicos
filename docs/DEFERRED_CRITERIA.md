# Deferred acceptance criteria

Step 3's specification (v2.4 §14) lists sixteen acceptance criteria. Thirteen
are tested inside Step 3. Three could not be, because each is a claim about
something that lives outside it.

This file exists so they are not forgotten. Each one names the step that owns
it, so whoever builds that step inherits the obligation rather than
rediscovering it.

**Status at 14 August 2026**

| | Criterion | Owner | State |
|---|---|---|---|
| AC-11 | The current-run pointer advances only on success | **Step 2** | Waiting on `ExtractionRun` |
| AC-12 | Sections reach the right consumers | **Step 4** | Waiting on Step 4 |
| AC-13 | A hash mismatch fails the run and writes nothing | **Step 3 (adapter)** | ✅ Done — `internal/adapters/secondary/approved/papers_test.go` |
| AC-15 | Parent inheritance, and its four limits | **Step 3 (domain)** | ✅ Done — `internal/core/domain/segment/inherit_test.go` |
| AC-16 | Child consensus, and its five limits | **Step 3 (domain)** | ✅ Done — `internal/core/domain/segment/consensus_test.go` |

---

## For Step 2 — AC-11

> **AC-11** Reprocessing creates a new run; `current_segmentation_run_id`
> advances only on `Completed`; a `Failed` rerun leaves the prior current run
> authoritative.

### Why it isn't tested yet

Specification §9 describes a three-level pointer chain:

```
Manuscript → ManuscriptVersion → ExtractionRun → SegmentationRun
```

None of those entities exists in this repository. There is a flat `papers`
table and no approval workflow. Testing AC-11 today would mean creating
`ExtractionRun.current_segmentation_run_id` purely so a test could read it back,
which demonstrates nothing except that a column can be created.

### What Step 3 already does about it

`internal/adapters/secondary/approved/papers.go` carries a
`TODO(step9-pointer)` comment recording the advancement as a **deferred
obligation** rather than skipping it silently. A `SegmentationRun` stores the
`extraction_run_id` it was given; it simply cannot advance a pointer on a row
that does not exist.

### What Step 2 needs to do

1. Create `ExtractionRun` with a `current_segmentation_run_id` column.
2. Advance that pointer **only** when a segmentation run reaches `Completed`.
   A `Failed` rerun must leave the previous run authoritative — a failed rerun
   that clears the pointer is worse than no rerun, because a consumer then sees
   a paper with no current segmentation and cannot tell whether it was never
   segmented or was segmented and then broken.
3. Write the test at the same time. It needs three cases: a first successful
   run sets the pointer; a second successful run moves it; a failed run leaves
   it where it was.
4. Delete the `TODO(step9-pointer)` comment and the G5 note in the adapter,
   and replace the adapter with one that reads from `ExtractionRun`.

### The related decision this unblocks

Step 2 has **no approval gate**. `papers.status = 'ready'` means Mathpix
finished converting, not that a human approved the extraction — there has never
been an `Approved` value in this codebase. Step 3 maps `ready` onto the
specification's `Approved` as a deliberate, temporary simplification, permitted
by §12 G5 and commented in the adapter.

**The consequence, recorded so it cannot become an assumption nobody remembers
making:** until a real approval gate exists, "approved" means "conversion
completed", and no human has reviewed extraction quality. Every segmentation
produced through the current adapter inherits that.

---

## For Step 4 — AC-12

> **AC-12** Consumption classes: a `funding` node never reaches Step 4
> extraction; a `references` node is available to citation checking; a
> `data_availability` node is readable by the compliance check; all present in
> the stored output.

### Why it isn't tested in Step 3

It is a claim about what Step 4 **does** with the labels, not about whether the
labels are right. Step 3 cannot test another step's behaviour without inventing
that step.

### What Step 3 already guarantees

Every section carries a `content_class` derived from its role, and that class is
correct on every node. Two tests establish it:

- `TestAC01_StandardPaper` — every resolved section has a class, and every
  unresolved one has none
- `TestRoleTableMatchesTable` — each role's class matches the authoritative role
  table

So the labels Step 4 will consume are already under test. What is untested is
that Step 4 respects them.

### The four classes and what each means

| Class | Roles | What Step 4 should do |
|---|---|---|
| `analytical` | abstract, introduction, literature_review, theory, methodology, results, discussion, limitations, conclusion | The substance. This is what extraction reads. |
| `citation_source` | references | Available to citation checking; **not** treated as claims by the paper |
| `compliance_disclosure` | data_availability, ethics_statement | Readable by compliance checks |
| `administrative` | acknowledgments, funding, author_contributions, conflict_of_interest | **Never reaches extraction.** A funding statement is not a finding. |

### What Step 4 needs to do

1. Filter by `content_class`, not by role. The classes exist precisely so a new
   role can be added without every consumer needing to learn about it.
2. Test that an `administrative` section — funding is the clearest case — never
   reaches the extraction path. This is the half of AC-12 that actually bites:
   treating a funding acknowledgement as a research claim would put a sponsor's
   name into an evidence chain.
3. Test that `references` is reachable by citation checking and
   `compliance_disclosure` by the compliance check.

### One thing to read before building it

Read the **effective** classification, not the stored one.

A section a human has reviewed carries the machine's original answer in
`section_nodes` and the human's decision in `review_decisions`. The machine's
answer is never overwritten — deliberately, so it stays possible to measure how
often the classifier is wrong. The value Step 4 should act on is computed at
read time: the human's decision where one exists, the machine's otherwise.

`EffectiveFor` in `internal/core/domain/segment/overlay.go` implements this.
Reading `primary_role` directly will silently ignore every human correction ever
made.

---

## For Step 3 — AC-13 ✅

> **AC-13** Hash mismatch → `Failed`, no nodes written as current, pointer not
> advanced.

**Done.** `internal/adapters/secondary/approved/papers_test.go`.

Written in the adapter rather than the domain because that is where the check
lives. The domain sees text going in and sections coming out; it has no way to
reach a database row.

Four cases: a stored hash that does not match its markdown is refused, a
matching one is accepted, a paper that has not finished converting is refused,
and a `ready` paper with no markdown is refused.

The last of those guards a state that would otherwise "succeed" into nothing —
an empty document produces one whole-document node covering zero bytes, which
looks identical to a paper that genuinely had no headings.
