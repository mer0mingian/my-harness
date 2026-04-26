---
name: review-check-correctness
description: 8-point risk framework review (Assumptions, Failure Modes, Edge Cases,
  Compatibility, Security, Ops, Scale, Testability) with severity grading and
  blocking-verdict authority. Tracks finding convergence across review cycles and
  cross-references NFR_CATALOG entries. Use when @pries-check evaluates a plan,
  diff, or PR for correctness gates.
---
# Review: Check Correctness

The correctness reviewer's playbook for the PRIES `@check` agent. Provides a
structured 8-pillar risk framework, severity grading rubric, convergence
tracking across cycles, and integration with Phase 0 governance NFRs.

## When to use

- A plan, diff, branch, or PR needs correctness review before merge.
- The orchestrator has dispatched both @pries-check and @pries-simplify; this
  skill drives the @pries-check side of the dual review.
- Pre-merge gating: the @check verdict is binding for merge approval.
- CI/CD validation gates that need structured risk findings.

## The 8-pillar risk framework

For each pillar, review the artefact and record any concrete findings.

### 1. Assumptions

- What unstated assumptions does this code/design rely on?
- Which assumptions are implicit in inputs, environment, or call ordering?
- Where is "happy path" assumed without validation?

### 2. Failure Modes

- For each external boundary (DB, network, queue, FS, env var), what happens
  on timeout, partial success, malformed payload, or provider outage?
- What is the blast radius? Local request? User session? Whole tenant?
- Is degradation graceful, or does it cascade?

### 3. Edge Cases

- Empty / null / max-length inputs.
- Concurrency: races, double-submit, retries, idempotency.
- Timezone, locale, leap year/second, DST boundaries.
- Boundary integers (0, 1, MAX, negative).

### 4. Compatibility

- API: response shape changes that break clients.
- Database: schema drift, index changes, deprecated columns.
- Wire protocol: serialisation incompatibilities, version skew.
- Feature flags: stale flag references, default mismatch.

### 5. Security

- AuthN/AuthZ: object-level access control, role escalation paths.
- Injection: SQL, command, template, deserialisation.
- Data exposure: PII in logs, secrets in errors, info leak in 4xx.
- Supply chain: new deps, pinned versions, license compatibility.

### 6. Operational Readiness

- Logs: structured, correlation IDs, no secrets.
- Metrics: SLI alignment, alert hooks.
- Tracing: span boundaries cover the new surface.
- Runbook: oncall has a rollback path.

### 7. Scale & Performance

- Hot paths: allocations, N+1 queries, sync I/O in async context.
- Caches: invalidation correctness, stampede risk.
- Background jobs: queue depth, fan-out limits, retry storms.
- Memory: unbounded buffers, leaks under load.

### 8. Testability

- Are the new tests sufficient for the risk surface?
- Are tests deterministic (no time, network, random without seed)?
- Do tests assert behaviour, not implementation details?
- Coverage for failure modes from pillars 1–7.

## Severity grading rubric

Map each finding to exactly one of the four severities. Be conservative —
without concrete evidence, cap at MAJOR.

| Severity  | Definition                                                         | Action            |
| --------- | ------------------------------------------------------------------ | ----------------- |
| BLOCKER   | Demonstrable outage, data loss, breach, or contract break path     | Merge denied      |
| CRITICAL  | Clear mechanism for significant production problems                | Fix before merge  |
| MAJOR     | Plausible failure under realistic load or edge conditions          | Fix or follow-up  |
| MINOR     | Style, smell, or low-probability concern                           | Optional          |

A BLOCKER finding must include: location, the exact mechanism, the failure
scenario, and a concrete reproduction or trace path. Vague concerns are not
BLOCKERs — escalate them only when evidence supports it.

## NFR cross-reference

When `docs/governance/NFR_CATALOG.md` exists, every finding should reference
the relevant NFR ID(s). Examples:

- A latency regression on a hot path → reference `NFR-PERF-XXX`.
- A new endpoint without rate limiting → reference `NFR-SEC-XXX`.
- A reduction in test pyramid coverage → reference `NFR-MAIN-001`.

If no NFR governs the surface, note the gap and recommend a new NFR via
`/governance-add-nfr`.

## Convergence detection (multi-cycle)

PRIES allows up to 3 review cycles per phase. Track findings across cycles:

1. **Cycle 1**: full pillar sweep, record N findings.
2. **Cycle 2**: re-review only the diff since cycle 1. Findings may be:
   - Resolved (do not re-emit).
   - Unchanged (re-emit, mark `iteration: 2`).
   - New (add, mark `iteration: 2`).
3. **Cycle 3**: same pattern. If cycle 3 produces no new BLOCKER/CRITICAL
   findings, declare **converged**. If new BLOCKERs appear, escalate to
   human review.

Convergence is reached when:

- Two consecutive cycles produce zero new BLOCKER or CRITICAL findings.
- All BLOCKER findings from earlier cycles are either resolved or have an
  approved waiver in the run report.

## Output contract

```yaml
verdict: APPROVE | REQUEST_CHANGES | BLOCK
iteration: 1
converged: false
findings:
  - id: CHK-001
    pillar: Failure Modes
    severity: BLOCKER
    location: "app/api/momentum.py:L45-L62"
    nfr_refs: [NFR-PERF-002]
    problem: "WebSocket broadcast has no timeout; a slow client blocks all subscribers."
    scenario: "Single mobile client with weak network blocks the GM updates for all players."
    suggestion: "Add 250 ms send timeout; drop the slow consumer with a structured log."
    confidence: high
  - id: CHK-002
    pillar: Testability
    severity: MAJOR
    location: "tests/api/test_momentum.py"
    nfr_refs: []
    problem: "No multi-client sync test; only single-subscriber asserted."
    scenario: "Regressions in fan-out logic would not be caught."
    suggestion: "Add Playwright multi-tab test asserting <200 ms propagation."
    confidence: medium
risk_summary:
  blocker: 1
  critical: 0
  major: 1
  minor: 0
```

## Caps

- Maximum **10 findings** per cycle. Prioritise BLOCKER > CRITICAL > MAJOR.
- Maximum **3 "missing context"** findings per review (forces concrete claims).
- Severity cannot exceed MAJOR without a concrete failure mechanism.

## Anti-patterns

- Listing every theoretical concern as a BLOCKER.
- Re-emitting a finding the dev already addressed in the previous cycle.
- Approving a diff while flagging a BLOCKER (verdict must match severity).
- Reviewing implementation when only a plan was requested (or vice versa).
- Skipping NFR cross-reference when `NFR_CATALOG.md` is present.
