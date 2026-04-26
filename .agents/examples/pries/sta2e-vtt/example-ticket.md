# Feature: Real-time Momentum Pool Synchronization

**Issue ID:** STA-001
**Type:** Feature
**Priority:** P0
**State:** Backlog

## User Stories

- As a GM, I want Momentum changes to sync to all players instantly so
  the table state stays consistent without manual refresh.
- As a player, I want to see updated Momentum without refreshing so I
  can make decisions based on current pool state.

## Acceptance Criteria

- AC-1: WebSocket connection established on scene activation (HTTP →
  WS upgrade succeeds, server emits `connected` event).
- AC-2: Momentum updates broadcast to all connected clients within
  200 ms (NFR-PERF-002 — multiplayer sync latency).
- AC-3: Graceful degradation if WebSocket unavailable (HTTP polling
  fallback at 1 Hz; UI shows "polling" indicator).
- AC-4: E2E test validates multi-client sync (Playwright, 2 tabs,
  asserts <200 ms propagation).
- AC-5: Disconnect handling (server cleans up subscription within
  30 s; reconnecting client receives current pool state).

## Related Artifacts

- **NFR-PERF-002** (multiplayer sync latency) — sync within 200 ms.
- **TECHNICAL_CONSTITUTION.md §2.1** (Real-time stack: FastAPI +
  Alpine.js + WebSockets).
- **TEST_STRATEGY.md §4** (Playwright E2E pattern, multi-tab pattern).

## Status Log

- 2026-04-26T10:30:00Z — Created (draft, awaiting PM agent ingest).

## Comments

(none yet)
