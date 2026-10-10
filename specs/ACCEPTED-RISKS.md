# Accepted risks

Status: RULED. Alex Zamurko gave a decision on every item on 9 October 2026,
and refined two of them on 10 October after being told what the AR-2 repair
does and does not establish. Each entry below carries its decision at the top.

Four accepted within internal bootstrap limits, two requiring work:

```text
AR-1  ACCEPT conditionally   High     production integrity explicitly excluded
AR-2  REPAIR                 High     residual kept: procedural, not enforced
AR-3  ACCEPT conditionally   Medium   coverage limits must be documented
AR-4  BLOCKING               Critical independent execution required
AR-5  ACCEPT conditionally   Medium   figures marked invalid, originals kept
AR-6  ACCEPT                 Low      an appropriate safeguard
```

His framing for the whole set, 9 October: "Four risks can be accepted within
internal bootstrap limits. Two require further work. No major architectural
changes are necessary at this stage."

And the distinction he drew on 10 October, which governs how AR-1 is read:

Critical functional defects are failures that can produce incorrect decisions
during normal operation. These block bootstrap. Adversarial integrity risks
are deliberate manipulation of writable code or records. These may be
conditionally accepted for internal bootstrap, but cannot be claimed as
protected. Keeping those two apart is what stops AR-1's acceptance from
looking like a contradiction of the rule that anything permitting an invalid
approval is critical.

Alex Zamurko, 9 October 2026: "Let's distinguish what can be reliably verified
now from what needs stronger protection later, and explicitly document any
risks we accept."

A risk belongs here when all three are true: it is understood, it is not fixed,
and leaving it unfixed is a choice rather than an oversight. Writing one down
accurately is the implementing agent's job. Accepting it is not.

Each entry says what the risk is, what would actually remove it, and what it
would cost. The cost matters: a risk accepted without knowing the price of
removing it is not an informed decision.

---

## AR-1 Every control in this layer is a convention, not an enforcement

**ACCEPTED CONDITIONALLY.** Alex Zamurko, 9 October 2026: "Controls are not
technically enforced, but this is acceptable for internal bootstrap, where the
objective is to verify correctness rather than prevent deliberate tampering.
Stronger enforcement is required before operational use."

**The scope limit, stated explicitly rather than implied.** This acceptance
covers internal bootstrap only. Nothing in this repository may be described as
protected against deliberate manipulation of its code or records, in any
document, package or report. The acceptance is of an adversarial integrity
risk, not of a functional defect, and the two are kept apart on purpose: a
failure that produces a wrong decision in normal operation still blocks. What
is accepted here is that someone who sets out to defeat these checks can.

**Outstanding, and not a condition anyone has scheduled.** "Before operational
use" has no date and no definition of when operational use begins. Whoever
makes that call needs this entry in front of them, because the acceptance
silently expires at a moment nobody has named.

**What is true.** `MC1_ENFORCEMENT` is `CONVENTION_ONLY`. The same writable
code performs the checks on itself. Nothing in the repository prevents someone
editing a record that a check reads, re-running the check, and getting a pass.
Every statement this layer makes holds while the checks run faithfully and the
records are not tampered with.

**What would remove it.** Checks running somewhere the implementing agent
cannot write: a CI runner with its own copy of the protocol, signed commits, or
records in append-only storage.

**What that costs.** Infrastructure that does not exist yet, and a change in
how the work is done day to day. It is not a small change, and it is not
obviously the right next thing while the layer is still finding defects in
itself.

**Why it might be accepted anyway.** The bootstrap phase is about whether the
checks are correct, not about whether they are tamper-proof. A check that is
wrong fails safely nowhere; a check that is right but only conventionally
enforced still catches honest mistakes, which is what has happened fifty-six
times so far.

---

## AR-2 An approval record cannot prove who wrote it

**REPAIR, with a residual that stays on this list.** Alex Zamurko, 9 October
2026: "Approval records cannot establish who authorised a decision. Since
linking records to verifiable original messages is relatively inexpensive,
accepting this weakness without improvement is unjustified."

And on 10 October, after being told that linking to a message makes the claim
checkable rather than proven: "the authorised person does not necessarily need
to write or sign the repository record. If an independent checker verifies the
original message's author, decision, target and correspondence with the
repository record, that can establish authorisation sufficiently for internal
bootstrap. Decision: Complete the inexpensive repair. Retain the residual risk
that verification is procedural rather than technically enforced."

**What the repair does.** An approval must now carry a source: the medium, a
reference precise enough to find the message, and the authorising words
themselves. `scripts/authority.py` refuses one without it.

**What stays true and is accepted.** The implementing agent types the record,
including the quote, so a quote that was never said would pass. The repair
moves this from unverifiable to checkable, not from broken to fixed. Closing
it needs a person other than the implementing agent to compare the record
against the original message, which is Alex's own route above and is a
procedure rather than a control.

**Records written before the requirement are not retrofitted.** They declare
`<kind>/1` and are read under the rule in force when they were made; `/2`
carries a source. Editing an approval recorded weeks ago to add a field nobody
asked for at the time would be rewriting evidence, and a gate that refuses its
own history is no better. This is C03-F01's principle, which Codex forced on
the review parser in BOOTSTRAP-002.

**What is true.** `authority.py` requires an approval to name a person, give a
reason, carry a timestamp, and match the exact bytes it approves. It cannot
establish that the named person wrote it. Every approval in this repository was
typed by the implementing agent from a message Alex sent elsewhere. The code
says so itself, in the refusal text: "This is a procedural control under
MC1_ENFORCEMENT: CONVENTION_ONLY. It does not force a sequence and does not
establish who wrote the approval."

**What is verifiable today.** That an approval exists; that it names someone;
that it gives a reason of real length; that its hashes match the captures it
displaced and installed, so it cannot be lifted and reused for a different
action; and that the displaced capture was preserved rather than overwritten.

**What is not.** Authorship. The actual evidence is Alex's message in Slack or
WhatsApp, which lives outside the repository and is not bound to the record.

**What would remove it.** Alex writing and committing the approval himself, or
signing it, or the record carrying a resolvable reference to the message that
authorised it, such as a Slack permalink with the quoted text, so a reader can
check the claim against the source.

**What that costs.** The third option is cheap and is proposed as a repair
rather than an accepted risk. The first two cost Alex's time on every
supersession.

---

## AR-3 The mutation set only covers the repairs someone wrote mutations for

**ACCEPTED CONDITIONALLY.** Alex Zamurko, 9 October 2026: "Complete mutation
coverage is unrealistic. Testing every known blocking repair is sufficient for
bootstrap, provided coverage limitations are documented." And his standard for
sufficient testing: "Every known blocking failure must have a reproducible
test. Exhaustive coverage is unnecessary."

**The condition, and where we stand against it.** The bar is every known
blocking repair, and the set currently covers every repair, blocking or not:
fifty-six of fifty-six caught in the sweep of 9 October. We are above his bar
rather than at it, which is worth knowing because the bar is what holds when
the set stops keeping up.

**The documented limitation.** "All fifty-six caught" is a statement about the
set, not about the code. It says nothing about a repair for which nobody wrote
a mutation, and it cannot, because that is a question about something absent.

**What is true.** The probe tests fifty-six repairs. It says nothing about a
repair for which no mutation was written, and it cannot, because that is a
question about something absent. "All fifty-six caught" is a statement about
the set, not about the code.

**What would remove it.** Coverage measurement that identifies repaired
behaviour with no mutation aimed at it. Nothing like that exists here, and a
general solution is a research problem rather than an afternoon.

**Why it might be accepted.** The set grew by being written alongside each
repair, so the gap is between "repairs made" and "repairs with mutations", not
between "all behaviour" and "tested behaviour". Every repair since BOOTSTRAP-002
has had a mutation written at the same time as the fix.

---

## AR-4 The cycle 03 reviewer could not execute anything

**BLOCKING. Critical.** Alex Zamurko, 9 October 2026: "SELF-F01 has not been
independently executed. Source inspection and developer-generated results
cannot fully establish runtime correctness. Independent execution is required
before closure." And his standard for adequate reviewer evidence: "Behavioural
claims require independent execution because source inspection alone cannot
establish runtime behaviour."

**The order of attempts, his, from 10 October.** Test execution capability
before freezing the review. If Codex cannot execute, use a separate
independent runner against the exact frozen commit and require Codex to assess
that evidence. If neither is available, SELF-F01 remains unverified.

**The open decision he named, and his answer.** Whether independently produced
execution evidence, reviewed by Codex, satisfies EC-4. His recommendation is
yes, "provided the implementing agent does not control that evidence."

**What that condition means in practice, and it is the whole thing.** The
strongest cheap version is the tests running on GitHub against the exact
frozen commit, with the log published by GitHub rather than pasted in by the
implementing agent. It establishes that the tests ran on that commit and
passed, which is the part that could otherwise be fabricated or quoted
selectively. It does not establish that the tests are good tests, because the
implementing agent wrote them; that half is Codex reading the test sources.
Both halves together are adequate. Either alone is not.

**A residual no runner removes.** The implementing agent writes the prompt
that directs the reviewer. A reviewer pointed at the wrong things is still
independent and still less useful. The prompt is frozen with the cycle and can
be read before the review runs, which is a mitigation rather than a fix.

**What is true.** BOOTSTRAP-003's cycle 03 reviewer said: "I could not
independently execute the Python controls: the available Python commands failed
to launch, and WSL access was denied." Its assessment of SELF-F01's third
repair rests on reading the source and reading the preserved output of a run
the implementing agent performed. That is independent reading of dependent
evidence.

**What would remove it.** A reviewer that can run the controls itself. That is
what the fourth cycle is for, if its environment permits.

**Why it matters for EC-4.** This is the clearest case of the difference
between evidence and adequate evidence, and it is why the judgement in EC-4 is
reserved rather than folded into a tick.

---

## AR-5 The historical measurement figures were never restated

**ACCEPTED CONDITIONALLY, with an action.** Alex Zamurko, 9 October 2026:
"Historical performance figures are unreliable, but citation evaluation is
outside the current bootstrap scope. Mark the figures invalid and recalculate
when citation work resumes." And on 10 October: "AR-5 should also be marked
invalid directly beside the affected historical figures, preserving the
original values for traceability."

**The action, which is specific.** Each affected figure is marked invalid
where it sits, in `scripts/citation_extract.py`, with the original value left
in place. Not deleted, not corrected, not moved to a footnote. A reader who
finds the number finds the warning in the same breath, and a reader checking
the history still sees what was originally claimed.

**What is true.** SELF-F03 was a defect in the gold runner that scored the
candidate and the baseline by different rules, inflating every improvement
figure measured through `--baseline`. The figures already recorded in
`citation_extract.py`, including +0.011 and +0.040 for rc3 B1a, were measured
with the defect present and have not been recomputed.

**The decision already taken.** They were deliberately left as they were, on
6 October, on the grounds that restating them from a re-run nobody has reviewed
would be a different kind of wrong. The register says so.

**What would remove it.** Re-measuring each one and having the new figures
reviewed. The citation work is in the backlog, so this follows it rather than
blocking the phase.

---

## AR-6 The probe tests committed source, not the working tree

**ACCEPTED. Low.** Alex Zamurko, 9 October 2026: "Testing committed code in
disposable copies prevents damage to the working repository. Refusing to test
relevant uncommitted changes is an appropriate safeguard."

**It bit its own author within a day, which is worth recording.** On
10 October the control that proves the tree survives an interrupted run kept
reporting an abandoned checkout surviving. The reason was that the control
clones the repository, so it was faithfully testing the committed probe while
every fix for that defect sat uncommitted. Two attempts went into explaining a
control that was behaving exactly as this entry says it behaves. That control
now copies the working-tree probe into its clone and commits it there, so the
one thing under test is the thing about to be committed; everything else in
the clone stays at HEAD.

**What is true.** Since 9 October the probe builds a disposable checkout of
HEAD and mutates that. It therefore tests what is committed. An uncommitted
edit in the working tree is not what gets tested, and the probe refuses to run
at all when the files it would mutate differ from HEAD.

**Why this is a deliberate trade.** The alternative is what we had before,
where the probe wrote into the live controller and every way a run could die
was a way to leave a disabled check behind. That cost us an emptied controller
overnight on 8 October. Testing committed source is the price of not being able
to damage the source at all.

**What to watch for.** The refusal is what keeps this honest. If it is ever
loosened so a run can proceed with a dirty tree, this risk becomes a defect.
