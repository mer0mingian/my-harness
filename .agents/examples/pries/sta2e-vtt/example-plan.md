# Implementation Plan: STA-001 Momentum Pool Sync

**Issue:** STA-001
**Worktree:** `.worktrees/feat/sta-001-momentum-sync`
**Branch:** `feat/sta-001-momentum-sync`
**Status:** Converged after 2 review cycles.

---

## Architecture summary

Add a WebSocket broadcast layer over the existing `momentum` HTTP API.
Server holds a per-scene subscription set; on every Momentum mutation
(add, spend, retrieve), fan-out the new pool state to subscribers.
Clients connect on scene activation; falls back to 1 Hz HTTP polling
when WS handshake fails.

## Task decomposition

### Task 1: Server-side broadcast service

- **File manifest**:
  - `app/services/broadcast.py` (new)
  - `tests/services/test_broadcast.py` (new)
- **Acceptance criteria**:
  - AC-1 (connection lifecycle): `connect`/`disconnect` add/remove
    subscriber correctly.
  - AC-2 (latency): `broadcast(scene_id, payload)` calls all
    subscribers within 200 ms (measured under 50 concurrent
    connections in the test).
- **Dependencies**: stdlib `asyncio`, no new packages.

### Task 2: WebSocket route + Momentum API hook

- **File manifest**:
  - `app/api/momentum.py` (modify — add WS upgrade route + fan-out call)
  - `tests/api/test_momentum.py` (new — contract test for WS upgrade
    and broadcast on POST)
- **Acceptance criteria**:
  - AC-1, AC-2 (server side).
  - AC-5 (cleanup): subscription removed on disconnect within 30 s.
- **Integration contract** with Task 1: `app.services.broadcast.Broadcaster`
  injected as FastAPI dependency.

### Task 3: Client-side connection + fallback

- **File manifest**:
  - `app/static/js/momentum-sync.js` (new)
  - `app/templates/scene.html` (modify — include script, status
    indicator div)
  - `tests/e2e/test_momentum_sync.spec.py` (new — Playwright)
- **Acceptance criteria**:
  - AC-3 (fallback): HTTP polling kicks in when WS handshake fails;
    UI shows "polling" indicator.
  - AC-4 (multi-client E2E): two tabs, latency assertion.
- **Integration contract** with Task 2: subscribes to
  `/ws/scene/<id>/momentum`; expects JSON payload with `pool` and
  `version` fields.

## Test strategy notes

- Unit: broadcast service (Task 1) and route logic (Task 2) under
  `tests/services/`, `tests/api/`.
- Integration: WS lifecycle in `tests/api/test_momentum.py` using
  `httpx.AsyncClient` + WS test util.
- E2E: multi-tab Playwright in `tests/e2e/`, latency assertion via
  `time.perf_counter()` between tab-A POST and tab-B receive.

## Convergence record

- **Cycle 1 (@check)**: 1 BLOCKER ("no send timeout, slow client blocks
  fanout"), 1 MAJOR ("E2E missing multi-client sync test").
- **Cycle 1 (@simplify)**: 1 MEDIUM ("BroadcastInterface abstraction
  premature").
- **Cycle 2 (@check)**: BLOCKER resolved (250 ms send timeout added);
  MAJOR resolved (multi-tab Playwright planned in Task 3); 0 new
  BLOCKER/CRITICAL → **converged**.
- **Cycle 2 (@simplify)**: MEDIUM resolved (interface dropped, single
  concrete `Broadcaster` class).

## NFR cross-references

- AC-2 → NFR-PERF-002 (sync latency, P0).
- AC-3 → NFR-REL-004 (graceful degradation, P1) — recommend adding if
  not present (`/governance-add-nfr`).
- AC-5 → NFR-MAIN-002 (resource cleanup, P2) — recommend adding.
