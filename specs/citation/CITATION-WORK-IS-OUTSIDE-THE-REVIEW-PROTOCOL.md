# The citation work is outside the review protocol, and that is correct

23 September 2026. Recorded for the freeze review, which would otherwise have
to discover it.

## What is true

`specs/implementation-review-protocol-v1.1.md` is the governing
implementation-review protocol. Alex Zamurko confirmed it authoritative on
9 September and `specs/PROTOCOL_STATUS.md` records the confirmation. Its §0.1
is unambiguous about scope:

```text
Every implementation run must reference the exact protocol version, commit,
and hash used.

No implementation run may begin until these fields are populated.
```

The citation extractor work is an implementation run by any reading. Twelve
defects found and fixed on 23 September alone, 81 of rc2's 86 conformance cases
carrying a control, a corpus disposition reconciler, and a mutation probe over
the suite. It references the protocol nowhere:

```console
$ grep -rl "implementation-review-protocol\|PROTOCOL_HASH\|BOOTSTRAP-00" \
      specs/citation/ scripts/citation_extract.py scripts/corpus_dispositions.py
$ ls runs/
BOOTSTRAP-001
BOOTSTRAP-002
```

No run directory, no frozen target, no independent review cycle, no findings
ledger. The whole citation programme sits outside the protocol written to
govern exactly this kind of work.

## Why that is not a violation

The protocol's own execution layer is not approved yet, and it refuses to open
a real run until it is:

```console
$ python scripts/bootstrap_gate.py check
BOOTSTRAP_REVIEW: NOT SATISFIED
  no bootstrap review on record.
```

BOOTSTRAP-001 reviewed that layer over four cycles and terminated at
`MAX_4_REACHED`, which is the designed exit rather than a failure. Thirty
findings, twenty-five resolved, five still open:

```console
$ python -c "import json;from collections import Counter;\
d=json.load(open('runs/BOOTSTRAP-001/plan-review/ledger.json'));\
print(Counter(v['state'] for v in d['findings'].values()))"
Counter({'RESOLVED': 25, 'OPEN': 5})
```

Asked on 16 September whether the layer was ready for real protocol runs, Alex
Zamurko ruled: *"not yet."* BOOTSTRAP-002 exists to verify the five repairs
independently, since §5 requires demonstration in a later review target and
`MAX_4_REACHED` is final for that loop. Until it completes and a human approves
it, no real run can be opened at all.

So the citation work could not have gone through the protocol even if someone
had tried to put it there. It is not out of compliance. It is earlier than the
thing it would comply with.

## What the freeze review should take from this

The evidence behind every citation figure on record was produced by the process
the protocol was written to replace: one agent auditing its own work, with
controls it wrote itself, and no independent reviewer at any point.

That is not an argument against the evidence. The suite reports 317 passing
controls, and a mutation probe runs 173 mutations and requires each to be
caught by the control that names it rather than by any control at all, which is
a stronger discipline than most of what preceded it here:

```console
$ python scripts/test_citation_extract.py | grep -c "\[ok\]"
317
$ python scripts/mutate_citation_suite.py | tail -1
  all 173 mutations were caught; the controls bite
```

It is an argument about what kind of evidence it is. Nothing
in the citation programme has been through the two controls the protocol exists
to supply: an independent reviewer who did not write the code, and a frozen
record binding what was reviewed to what was said about it.

BOOTSTRAP-001 is the reason to take that seriously rather than as bookkeeping.
Across its four cycles the rejection rate for repair claims never fell: five of
thirteen, then nine of twenty, then five of eleven. An independent reviewer
declined to confirm between a third and a half of the repairs claimed, every
time it was asked, on code written under the same discipline the citation work
uses today. Its own closing observation was that each rejected control tested
the case its repair was designed for and missed the case one step sideways.
That is a statement about how controls get written here, not about those five
defects, and the citation suite is written by the same hand.

## The one thing this note can check

Alex Zamurko's confirmation names a hash. The committed file has it:

```console
$ sha256sum specs/implementation-review-protocol-v1.1.md
296594a3c06cd2f9c66976c369b15804f39bbb2be37b5e62234d37fafd28d483
```

That is the value in his message of 9 September and the value recorded in
`runs/BOOTSTRAP-001/run.json`. Three independent places agree, so the
protocol's own pin verifies and the document in the repository is the document
he approved.

## What this note does not establish

That the citation work should have gone through the protocol. It could not
have.

That the freeze can proceed without it. That is the review's call and this note
takes no position on it.

That the consolidation workflow v6 says anything about this. v6 is not in the
repository and this note is written from the protocol, not from it.
