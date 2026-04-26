# Non-Functional Requirements Catalog — STA2E VTT Lite

**Project:** Star Trek Adventures 2e Virtual Tabletop (Lite)
**Version:** 1.0
**Last Updated:** 2026-04-26
**Validation:** All NFRs use EARS notation and have testable acceptance criteria.

---

## NFR Classification (ISO/IEC 25010)

1. Performance Efficiency (`PERF`)
2. Reliability (`REL`)
3. Security (`SEC`)
4. Usability (`USE`)
5. Maintainability (`MAIN`)
6. Compatibility (`COMP`)
7. Portability (`PORT`)
8. Functional Suitability (`FUNC`)

---

## 1. Performance Efficiency

### NFR-PERF-001: API Response Time
**Category:** Performance Efficiency > Throughput
**Requirement (EARS):**
> When a user requests data via any REST endpoint under `/api/v1/`, the system shall return a response within 200ms (p95) under nominal load (<= 100 concurrent users).

**Acceptance Criteria:**
- p50 latency <= 100ms
- p95 latency <= 200ms
- p99 latency <= 500ms
- 0% timeouts at nominal load.

**Test Strategy:**
- Locust load test, 100 concurrent users, 10-minute window in staging.
- OpenTelemetry traces sampled 5% in production.

**Priority:** P0
**Rationale:** Users perceive >250ms as sluggish; HTMX swaps amplify the perception.

---

### NFR-PERF-002: WebSocket Broadcast Latency
**Category:** Performance Efficiency > Time Behaviour
**Requirement (EARS):**
> When a Game Master rolls dice or updates shared bridge state, the system shall broadcast the resulting event to all connected players within 200ms (p95) end-to-end.

**Acceptance Criteria:**
- p95 GM-action -> client-render <= 200ms.
- 100% of events delivered (no silent drops).
- Reconnect within 30s restores all missed events.

**Test Strategy:**
- Playwright E2E with two pages connected to the same session, asserting timestamp delta.
- Synthetic monitor in production tracking GM-roll round-trip.

**Priority:** P0
**Rationale:** Core multiplayer experience; >200ms desync ruins dice-narrative immediacy.

---

## 2. Reliability

### NFR-REL-001: Session Persistence Across Disconnect
**Category:** Reliability > Recoverability
**Requirement (EARS):**
> When a user's WebSocket connection drops, the system shall allow reconnection within 30 seconds without any loss of game state.

**Acceptance Criteria:**
- Session state persisted in PostgreSQL, never only in memory.
- Reconnect replays missed events from the audit log.

**Test Strategy:**
- Playwright E2E that simulates network interruption mid-encounter.
- Chaos test killing the WebSocket worker pod and asserting recovery.

**Priority:** P1
**Rationale:** GMs and players regularly experience flaky home Wi-Fi.

---

## 3. Security

### NFR-SEC-001: Authentication Required for Game APIs
**Category:** Security > Authentication
**Requirement (EARS):**
> When a user attempts to access any endpoint under `/api/v1/` (except `/health` and `/auth/*`), the system shall require a valid Auth0-issued JWT.

**Acceptance Criteria:**
- Expired tokens rejected with 401.
- Missing tokens rejected with 401.
- Invalid signatures rejected with 401.
- Failed attempts rate-limited to 5/15min/IP.

**Test Strategy:**
- pytest integration tests with crafted tokens.
- OWASP ZAP scan in nightly CI.

**Priority:** P0
**Rationale:** Game state can include private campaign notes.

---

## 4. Usability

### NFR-USE-001: Accessibility
**Category:** Usability > Accessibility
**Requirement (EARS):**
> The system shall conform to WCAG 2.1 Level AA on all public-facing pages.

**Acceptance Criteria:**
- axe-core scan reports 0 violations on all routes covered by E2E.
- Keyboard navigation reaches every interactive control via Tab.
- Colour contrast >= 4.5:1 for body text, 3:1 for UI components.

**Test Strategy:**
- Playwright + `axe-playwright-python` integration on each E2E journey.
- Manual NVDA pass before each release.

**Priority:** P0
**Rationale:** Legal compliance (ADA-equivalent in target markets).

---

### NFR-USE-002: Mobile Responsiveness
**Category:** Usability > Adaptability
**Requirement (EARS):**
> The system shall render correctly on viewports from 375px (iPhone SE) to 2560px (4K desktop).

**Acceptance Criteria:**
- No horizontal scrolling on any supported viewport.
- Touch targets >= 44x44px (WCAG 2.5.5).

**Test Strategy:**
- Playwright visual snapshots at 375, 768, 1920px.
- Lighthouse mobile score >= 90 in nightly run.

**Priority:** P1

---

## 5. Maintainability

### NFR-MAIN-001: Code Coverage
**Category:** Maintainability > Testability
**Requirement (EARS):**
> The system shall maintain at least 80% line coverage on all production code paths in `src/`.

**Acceptance Criteria:**
- pytest-cov reports >= 80% on every PR.
- CI fails the build if coverage drops below 80%.

**Test Strategy:**
- pytest-cov on every PR.
- Mutation testing nightly (mutmut) to detect coverage theatre.

**Priority:** P1

---

## Appendix: NFR Validation Matrix

| NFR ID         | Testable | Automated test               | Manual test       | Monitoring        | Owner      |
| -------------- | -------- | ---------------------------- | ----------------- | ----------------- | ---------- |
| NFR-PERF-001   | yes      | Locust + pytest-benchmark    | -                 | OpenTelemetry     | Backend    |
| NFR-PERF-002   | yes      | Playwright E2E (sync test)   | Live playtest     | Synthetic monitor | Backend    |
| NFR-REL-001    | yes      | Playwright + chaos test      | DR drill quarterly| Uptime monitor    | SRE        |
| NFR-SEC-001    | yes      | pytest integration + ZAP     | Pentest annual    | Auth logs         | Security   |
| NFR-USE-001    | yes      | Playwright + axe-core        | NVDA screen reader| -                 | Frontend   |
| NFR-USE-002    | yes      | Playwright visual snapshots  | Real device check | Lighthouse        | Frontend   |
| NFR-MAIN-001   | yes      | pytest-cov                   | -                 | -                 | All        |
