# Accepted risks

Status: DRAFT. Nothing here is accepted until Alex Zamurko says so, item by
item. Until then this is a list of things that are true about the system and
not yet ruled on.

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
