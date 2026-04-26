---
name: review-simplify-complexity
description: YAGNI and overengineering detection using the delete-test methodology
  with explicit protected-pattern allowlist (retries, circuit breakers, auth, audit
  logging, migration guardrails). Outputs simplification opportunities with effort
  estimates. Strictly out of scope for security/correctness — those belong to
  @pries-check. Use when @pries-simplify reviews a diff, plan, or PR.
---
# Review: Simplify Complexity

Complexity reviewer skill for the PRIES `@pries-simplify` agent.
Identifies overengineering, premature optimization, dead abstractions, and
over-configuration — without straying into the correctness/security lane
that belongs to `@pries-check`.

## When to use

- The dual-review orchestrator dispatches @pries-simplify alongside
  @pries-check.
- A standalone simplification review of a feature branch or PR.
- After implementation, before merge: catch unnecessary complexity that
  arrived "in case we need it later."

## Scope boundaries

**In scope**:

- Premature optimization (caches before measurement, micro-tweaks).
- Over-abstraction (interface for one implementation).
- YAGNI violations (config knobs, plugin points, no current consumer).
- Structural bloat (deep folder nests, util grab-bags, parallel hierarchies).
- Dead code (unreachable branches, unused exports).
- Over-configuration (env vars no one sets, feature flags with one branch).

**Out of scope** — defer to @pries-check:

- Security flaws.
- Reliability or correctness bugs.
- Race conditions, concurrency hazards.
- Compatibility breaks.

If a finding straddles the line, **route it to @check** instead of
emitting under @simplify.

## Protected patterns (do NOT flag unless demonstrably unused)

Operational concerns that look like complexity but defend real failure
modes:

- Retries with backoff and jitter.
- Circuit breakers, bulkheads, rate limiters.
- Idempotency keys, deduplication tokens.
- AuthN/AuthZ checks at object level.
- Audit logging on sensitive actions.
- Rollback flags, dual-writes, migration guardrails.
- Feature flags during rollouts.

These are protected. Flag only when:

- The pattern is provably unreachable (no caller).
- The pattern protects a failure mode that no longer exists (e.g.,
  legacy provider removed).

## Delete-test methodology

For each candidate complexity, run the delete-test mentally:

1. **Imagine deleting the component.** What concrete user-visible or
   ops-visible behavior changes?
2. **Justify in one sentence.** If the justification reads "in case we
   need it later," it is YAGNI.
3. **Verify usage.** Grep for references; one caller behind a flag that
   is never enabled equals zero callers.
4. **Propose a concrete alternative.** Inline, drop, collapse, replace.
   "Maybe simplify someday" is not a finding.
5. **Gate against operational reality.** Re-check the protected-pattern
   list. If it overlaps, do not emit.

A finding survives the delete-test only when steps 1–4 produce a
concrete simpler replacement and step 5 doesn't veto.

## Severity scale

Native to @simplify; never normalised to @check's scale:

| Severity | Definition                                                |
| -------- | --------------------------------------------------------- |
| HIGH     | Removing this saves >100 LOC or eliminates a folder layer |
| MEDIUM   | Eliminates an unused abstraction or dead branch           |
| LOW      | Style-level cleanup; nice to have                         |

All severities are **advisory**. @simplify never blocks a merge.

## Constitution integration

When `docs/governance/TECHNICAL_CONSTITUTION.md` defines KISS rules
(typically §3 Code Quality Standards), cite the rule in the finding's
`constitution_ref` field. Examples:

- "Constitution §3.2 — Composition over inheritance" → flag a deep class
  hierarchy.
- "Constitution §3.4 — YAGNI for plugin points" → flag a registry with
  one implementation.

## Output contract

```yaml
findings:
  - id: SMP-001
    severity: HIGH
    location: "app/services/broadcast.py"
    problem: |
      Three-layer abstraction (BroadcastInterface -> WebSocketBroadcaster
      -> InMemoryBroadcastQueue) with exactly one implementation each.
    delete_test:
      consequence: "No behavioural change; tests still pass with inline calls."
      one_sentence_justification: "None — the abstraction has no second user."
      usage_count: 1
    suggestion: "Inline WebSocketBroadcaster into the route handler. Reintroduce the interface when a second transport (SSE, polling) actually appears."
    estimated_effort_minutes: 30
    constitution_ref: "§3.4 YAGNI"
  - id: SMP-002
    severity: MEDIUM
    location: "app/config.py"
    problem: "BROADCAST_TIMEOUT env var read but never set in any environment."
    delete_test:
      consequence: "Default value applies; no environment depends on the override."
      one_sentence_justification: "Defensive flag, never used."
      usage_count: 0
    suggestion: "Inline the constant; drop the env-var read."
    estimated_effort_minutes: 5
summary:
  high: 1
  medium: 1
  low: 0
notes: "Did not flag retry-with-backoff in broadcast.py (protected pattern)."
```

## Caps

- Maximum **8 findings** per review (forces ruthless prioritisation).
- A finding with `usage_count: 0` is automatically promoted to at least
  MEDIUM severity.

## Anti-patterns

- Flagging a circuit breaker as "complexity" without proof of disuse.
- Recommending a refactor that crosses the @check correctness lane
  (e.g., "remove the retry handler").
- Emitting findings phrased as "consider simplifying"; always include a
  concrete alternative.
- Flagging tests as overengineered (test thoroughness is rarely YAGNI).
- Recommending changes that increase coupling under the banner of
  "simpler."
