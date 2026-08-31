## Review Instructions

**Verify against source — do not review the plan text in isolation.** The plans reference real files, migrations, routes, and tests in this repo (repo root is the current working directory).
1. Open the referenced files and check each claim against the actual code.
2. For every strength or concern, cite concrete `path/to/file:line` evidence plus the mechanism.
3. When a plan asserts a mechanism works (a guard, a query filter, a test that exercises a path), trace whether it actually does what is claimed — do not take the plan's word for it.
4. If you cannot read the repo (no file access), say so and downgrade that finding to an open question rather than asserting it.

Findings citing `file:line` evidence are weighted far more heavily than impressionistic ones; a review that only restates the plan's own claims has low value.

### IMPORTANT — this is CYCLE 2 of a plan-review-convergence loop

Cycle 1 of review raised 4 HIGH concerns and 14 actionable non-HIGH findings against an EARLIER version of these plans. The plans were then rewritten to incorporate that feedback (commits 09a88c9, dd69e0e, d61eac2) and re-frozen at a new phase base commit `030521b`.

**You are reviewing the CURRENT plan set.** Report what remains UNRESOLVED NOW. Do not re-report cycle-1 findings that the replan already addressed. For each concern you raise, state explicitly whether it is:
- NEWLY RAISED in this cycle, or
- PARTIALLY RESOLVED (acknowledged in the plan, mitigation described but not verifiable/complete), or
- STILL UNRESOLVED from a prior cycle.

For every MEDIUM/LOW concern, state whether it is ACTIONABLE — i.e. whether it would be invisible to `/gsd-execute-phase` unless incorporated into a PLAN.md task, action, acceptance_criteria, verify command, must_haves item, threat model, artifact list, or an explicit deferral/rejection rationale. If the concern is ALREADY covered by some element of the current PLAN.md files, say so and mark it NOT ACTIONABLE, citing the plan line that covers it.

Analyze each plan and provide:

1. **Summary** — One-paragraph assessment
2. **Strengths** — What's well-designed (bullet points)
3. **Concerns** — Potential issues, gaps, risks (bullet points with severity: HIGH/MEDIUM/LOW, and the resolution status label above)
4. **Suggestions** — Specific improvements (bullet points)
5. **Risk Assessment** — Overall risk level (LOW/MEDIUM/HIGH) with justification

Focus on:
- Missing edge cases or error handling
- Dependency ordering issues
- Scope creep or over-engineering
- Security considerations
- Performance implications
- Whether the plans actually achieve the phase goals

Output your review in markdown format.
