# Final Review Report: STA-001 Momentum Pool Sync

**Workflow:** /pries-implement STA-001
**Phase:** 9 (Final Review)
**Verdict:** APPROVE
**Converged:** true (2 cycles)
**Requires human review:** false

---

## @pries-check (Correctness Reviewer)

**Verdict:** APPROVE
**Iteration:** 2
**Risk summary:** 0 BLOCKER, 0 CRITICAL, 1 MAJOR, 2 MINOR

### Findings

**CHK-001 — MAJOR (resolved cycle 2)**
- **Pillar:** Failure Modes
- **Location:** `app/services/broadcast.py:L39-L52`
- **NFR refs:** [NFR-PERF-002, NFR-REL-004]
- **Problem (cycle 1):** Original implementation iterated subscribers
  serially with `await q.put(payload)`; one slow consumer blocked the
  fanout for all peers, breaking the 200 ms budget.
- **Resolution (cycle 2):** Implementation switched to
  `asyncio.gather` with per-call `asyncio.wait_for(timeout=250 ms)` and
  evicts subscribers that exceed the deadline.
- **Status:** Resolved. Tests `test_broadcast_latency_under_200ms`
  and `test_slow_consumer_does_not_block_fanout` cover the regression.

**CHK-002 — MAJOR (open, advisory follow-up)**
- **Pillar:** Ops Readiness
- **Location:** `app/services/broadcast.py`
- **NFR refs:** [NFR-MAIN-001]
- **Problem:** No structured logging on subscriber eviction; oncall has
  no signal when fanout is dropping clients.
- **Suggestion:** Add `structlog` event `broadcast.subscriber.evicted`
  with `scene_id` and `reason` fields. Non-blocking for STA-001;
  recommend follow-up ticket.
- **Confidence:** medium.

**CHK-003 — MINOR**
- **Pillar:** Testability
- **Location:** `tests/services/test_broadcast.py`
- **Problem:** Latency test uses real `time.perf_counter()`; could be
  flaky on shared CI runners.
- **Suggestion:** Tag with `@pytest.mark.flaky` or move to integration
  tier with a retry budget.

**CHK-004 — MINOR**
- **Pillar:** Edge Cases
- **Location:** `app/api/momentum.py`
- **Problem:** No rate limit on `/ws/scene/<id>/momentum` upgrade.
- **Suggestion:** Apply existing IP-based limiter middleware.

---

## @pries-simplify (Complexity Reviewer)

**Iteration:** 2
**Summary:** 0 HIGH, 0 MEDIUM, 1 LOW

### Findings

**SMP-001 — MEDIUM (resolved cycle 2)**
- **Location:** `app/services/broadcast.py`
- **Problem (cycle 1):** Originally introduced `BroadcastInterface`
  abstract class with one concrete `WebSocketBroadcaster` and one
  `InMemoryBroadcastQueue` (used only by tests).
- **Delete-test:** Two implementations existed only because the test
  fixture aliased one — usage_count = 1 production caller.
- **Suggestion:** Inline `WebSocketBroadcaster` into a single
  `Broadcaster` class; reintroduce interface when a second transport
  (SSE, polling-bridge) actually appears.
- **Resolution (cycle 2):** Interface removed; single `Broadcaster`
  class. Constitution §3.4 (YAGNI) compliant.
- **Status:** Resolved.

**SMP-002 — LOW**
- **Location:** `app/services/broadcast.py:L21`
- **Problem:** `defaultdict(set)` + `discard()` is fine, but the
  `if not targets: return` early-exit duplicates logic that
  `asyncio.gather([])` already handles cleanly.
- **Delete-test:** Removing the early-exit changes nothing (gather of
  empty list returns []).
- **Suggestion:** Drop the early-exit branch (3 LOC saved).
- **Effort:** 5 min.

---

## Merged verdict (orchestrator)

| Source        | Severity / Action       |
| ------------- | ----------------------- |
| @check BLOCKER | 0 — proceed              |
| @check CRITICAL | 0                        |
| @check MAJOR  | 1 open (advisory follow-up: structured logging) |
| @simplify HIGH | 0                        |

**Merge gate (from @check):** APPROVE.
**Advisory items:** CHK-002 (logging follow-up), SMP-002 (3 LOC).

## Verification (from @pries-make)

```yaml
status: GREEN
mode: tdd
files_changed:
  - app/services/broadcast.py
  - app/api/momentum.py
  - app/static/js/momentum-sync.js
  - app/templates/scene.html
verification:
  command: "uv run pytest -q"
  exit_code: 0
  excerpt: "27 passed in 1.84s"
criteria_results:
  - criterion: AC-1 (WS connection on scene activation)
    result: PASS
    evidence: tests/api/test_momentum.py::test_ws_upgrade
  - criterion: AC-2 (200 ms latency)
    result: PASS
    evidence: tests/services/test_broadcast.py::test_broadcast_latency_under_200ms
  - criterion: AC-3 (graceful degradation)
    result: PASS
    evidence: tests/e2e/test_momentum_sync.spec.py::test_polling_fallback
  - criterion: AC-4 (multi-client E2E)
    result: PASS
    evidence: tests/e2e/test_momentum_sync.spec.py::test_two_tab_sync
  - criterion: AC-5 (disconnect cleanup)
    result: PASS
    evidence: tests/services/test_broadcast.py::test_subscriber_removed_on_disconnect
regression:
  ran: "uv run pytest -q"
  exit_code: 0
  newly_failing: []
```

## Convergence record

- **Cycle 1:** 1 BLOCKER (CHK-001, fanout blocking), 1 MEDIUM
  (SMP-001, premature interface).
- **Cycle 2:** Both resolved by @pries-make in a single follow-up;
  cycle 2 produced 0 new BLOCKER/CRITICAL → **converged**.

## Outcome

Draft PR opened: `feat/sta-001-momentum-sync` → `main`.
Linear comment posted with PR link and execution summary.
Issue state advanced to `In Review`.

Follow-up tickets recommended:

- STA-002: Add structured logging for subscriber eviction (CHK-002).
- STA-003: Apply rate limiter to WS upgrade route (CHK-004).
