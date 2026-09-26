# A terminal exit at boundary n, with valid cycles beyond it

26 September 2026, found while repairing C01-F01. Not raised by cycle-01's
review, not repaired, and open for Alex Zamurko.

## What happens today

C01-F01's repair gave `replay`, `last_authorized` and `skipped_events` one
shared transition evaluator. On the history the reviewer supplied, the ledger
now rebuilds the state correctly:

```text
RAISED(1) ACCEPT(1) DEMONSTRATED(2) REOPENED(3) ACCEPT(2) DEMONSTRATED(4)

ledger show        OPEN, and names the cycle-02 ACCEPT as never having taken
                   effect, because it predates the cycle-03 reopening
controller         LOOP_STATUS: CONVERGED
```

The controller is not wrong about the boundary it chose. `sets_at_boundary`
walks n upward and `decide()` is asked at each one; at n=2 the finding really
had been resolved, nothing was open, and CONVERGED is the correct reading of
the loop as it stood at the end of cycle 2. The walk breaks at the first
uncleared terminal exit, so cycles 03 and 04 are never evaluated and the
reopening never enters the answer.

## Why it is still a problem

One record, two answers. The ledger says the finding is OPEN and the
controller says the loop converged. A consumer acting on `LOOP_STATUS` and a
consumer reading the ledger reach opposite conclusions, which is the shape of
B01-F11 rather than a new kind of fault.

The controller also states, in its own words, that it exists to detect
unauthorized continuations rather than to trust that every cycle directory was
legitimately created. Cycles 03 and 04 are exactly that: evidence produced
after a terminal exit that no recorded authorization clears. Today they are
not reported as anything at all. They are simply not reached.

## Why it was not repaired here

Because the repair is a ruling, not a coding decision, and three defensible
answers exist:

```text
1  the exit governs and the later cycles are reported as an unauthorized
   continuation
       keeps the historical answer honest and names the irregularity, but
       leaves LOOP_STATUS disagreeing with the ledger

2  the LATEST boundary governs, and the passed exit is reported alongside it
       makes the controller agree with the ledger, at the cost of letting
       work done after an uncleared exit decide the outcome, which is the
       direction C01-F02 warns about

3  the loop cannot be described by either boundary and escalates
       safest, and it converts an ordinary recurrence into a human decision
       every time a finding reopens after a convergence
```

Position 1 and position 2 are opposites on the question C01-F02 is circling:
whether evidence beyond a boundary may be evaluated. Choosing here, quietly,
inside a repair for a different finding, is how a protocol acquires a rule
nobody ruled on.

## What is in place meanwhile

`scripts/test_ledger.py` carries the full history as a control and asserts the
two halves that are settled: the rebuild holds the finding OPEN, and the
diagnostic names the backdated acceptance and says why it did not take. The
controller's answer is recorded as a tripwire with three branches, so a change
in either direction fires:

```text
controller still says CONVERGED    ok, recorded as this gap
controller says anything else      FAIL, naming the new status and pointing
                                   back at this note
```

That is deliberately not a green tick on correct behaviour. It is a marker on
behaviour nobody has ruled on, and the control says so where a reader will
find it.

## Related, and distinct

C01-F02 requires the four-valid-cycle ceiling to be enforced while walking
every boundary rather than only in the fallback for the latest one. That is
the same walk and a different rule: the ceiling is about how many cycles may
be spent, this is about what a boundary means when evidence exists past it.
Repairing C01-F02 will touch this code and should not be taken to have settled
this question as a side effect.
