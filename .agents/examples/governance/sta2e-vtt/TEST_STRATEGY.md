# E2E Test Strategy — STA2E VTT Lite

**Project:** Star Trek Adventures 2e Virtual Tabletop (Lite)
**Version:** 1.0
**Last Updated:** 2026-04-26
**Test Framework:** Playwright Python

---

## 1. Test Pyramid Ratios

| Test Type      | Target % | Notes                                                                |
| -------------- | -------- | -------------------------------------------------------------------- |
| Unit           | 70%      | Dice roll math, NFR rules engine, character sheet validation.        |
| Integration    | 20%      | Repositories, WebSocket envelope round-trip, Auth0 JWT validation.   |
| E2E            | 10%      | Critical multiplayer flows, bridge station navigation.               |

**Rationale:** Adheres to company standard 70/20/10 test pyramid for consistency across projects.

---

## 2. E2E Test Scope

### 2.1 Critical User Journeys

| Journey ID    | Description                                                  | Test Count | NFRs Validated                | Priority |
| ------------- | ------------------------------------------------------------ | ---------- | ----------------------------- | -------- |
| AUTH-001      | OAuth login -> landing page                                  | 2          | NFR-SEC-001                   | P0       |
| CHAR-001      | Create / edit / delete character sheet                       | 4          | NFR-USE-001                   | P0       |
| DICE-001      | GM rolls dice -> all players see result within 200ms         | 3          | NFR-PERF-002, NFR-USE-001     | P0       |
| BRIDGE-001    | Navigate Helm / Tactical / Comms / Engineering stations      | 6          | NFR-USE-001, NFR-USE-002      | P0       |
| SYNC-001      | GM updates shared state -> players auto-refresh              | 5          | NFR-PERF-002, NFR-REL-001     | P0       |
| RECONN-001    | Drop & resume WebSocket without losing state                 | 2          | NFR-REL-001                   | P1       |

**Selection rationale:**
- DICE-001 is the most-played feature; failure is a release blocker.
- BRIDGE-001 covers Star-Trek-specific UI with no off-the-shelf coverage.
- SYNC-001 directly validates the headline NFR (NFR-PERF-002).

**Not covered by E2E:**
- Dice math edge cases -> unit tests.
- Auth0 token refresh timing -> integration tests.
- Tailwind class changes -> visual regression snapshots.

---

## 3. Playwright Implementation Patterns

### 3.1 Locator Strategy

Prefer in this order:

1. Role: `page.get_by_role("button", name="Roll Dice")`
2. Label: `page.get_by_label("Character Name")`
3. Test ID: `page.get_by_test_id("bridge-station-helm")`
4. CSS / XPath: PROHIBITED unless documented exception per test (e.g. third-party iframe).

### 3.2 Page Object Model

Every E2E test uses a Page Object class. Example skeleton:

```python
from playwright.sync_api import Page

class BridgePage:
    def __init__(self, page: Page):
        self.page = page
        self.helm_tab = page.get_by_role("tab", name="Helm")
        self.tactical_tab = page.get_by_role("tab", name="Tactical")
        self.dice_button = page.get_by_role("button", name="Roll 2d20")
        self.dice_result = page.get_by_test_id("dice-result")

    def open_helm(self) -> None:
        self.helm_tab.click()

    def roll_dice(self) -> None:
        self.dice_button.click()
        # Auto-wait: result must appear within 200ms (NFR-PERF-002).
        self.dice_result.wait_for(state="visible", timeout=500)
```

### 3.3 Auto-wait vs explicit waits

- Rely on Playwright auto-wait for visibility / enabled / stable.
- `time.sleep()` is **prohibited**.
- For WebSocket events, use `page.expect_event("websocket")` or assert against rendered DOM (which only updates after the event arrives).

---

## 4. Visual Regression Testing

| Page type            | Coverage                  | Tool                        | Frequency       |
| -------------------- | ------------------------- | --------------------------- | --------------- |
| Public pages         | 100% of routes            | Playwright snapshots        | Every PR        |
| Authenticated pages  | Bridge stations + char sheet | Playwright snapshots     | Every PR        |
| Admin pages          | None (manual QA only)     | -                           | Release testing |

Baselines captured in CI Docker image (Linux, Chromium only) to keep font rendering deterministic.

---

## 5. Test Data Strategy

| Approach        | Use Case                                       | Tool               |
| --------------- | ---------------------------------------------- | ------------------ |
| Fixtures        | Bridge station presets, dice notation table    | `pytest.fixture`   |
| Factories       | Characters, sessions, players                  | `factory_boy`      |
| Realistic data  | Sample published campaigns for E2E reads only  | Anonymised JSON    |

**Isolation:** Each E2E test gets a fresh PostgreSQL schema via the `pytest-postgresql` plugin. Fixtures roll back at end-of-test.

```python
import factory
from app.models import Character

class CharacterFactory(factory.Factory):
    class Meta:
        model = Character

    name = factory.Sequence(lambda n: f"Lt. Cmdr Data-{n}")
    role = "Science Officer"
    species = "Android"
    attributes = factory.LazyFunction(lambda: {"control": 12, "daring": 8, "fitness": 11})
```

Sensitive data is generated with `faker`; production credentials are never used.

---

## 6. CI/CD Integration

| Trigger        | When                  | Tests run                          | Timeout | Workers |
| -------------- | --------------------- | ---------------------------------- | ------- | ------- |
| Pre-commit     | Before commit         | Fast unit tests only               | 30s     | 1       |
| PR pipeline    | On PR open / update   | Unit + integration                 | 5m      | 4       |
| Main branch    | After merge to main   | All tests + E2E                    | 15m     | 8       |
| Nightly        | 02:07 daily           | All + visual regression + axe-core | 30m     | 16      |

**Flaky test policy:** auto-retry max 2 times in CI; persistent flakes are quarantined with a Linear ticket and a deadline.

---

## 7. Metrics & Reporting

| Metric              | Target              |
| ------------------- | ------------------- |
| Coverage            | >= 80%              |
| Flakiness rate      | < 2%                |
| Test duration (PR)  | <= 5 minutes        |
| E2E pass rate       | >= 97%              |

Artifacts uploaded to CI on failure: screenshots, videos, Playwright traces.

---

## 8. Test Maintenance

- **Quarterly review:** remove obsolete tests (deprecated bridge stations), refresh visual baselines, fix flakes.
- **Documentation required for every E2E test:**

```python
def test_dice_roll_broadcast(page):
    """
    Test ID: DICE-001
    Purpose: Validate that GM dice rolls reach all players within 200ms.
    Preconditions: GM and one player already authenticated; both joined to session ABC.
    Expected outcome: Player page renders dice result element with the rolled value within 200ms of GM clicking Roll.
    NFRs: NFR-PERF-002, NFR-USE-001.
    """
    ...
```

---

## 9. Appendix: Tool Configuration

### Playwright config

```python
# playwright.config.py
config = {
    "base_url": "http://localhost:8000",
    "timeout": 30000,
    "expect_timeout": 5000,
    "browsers": ["chromium", "firefox", "webkit"],
    "workers": 4,
    "retries": 2,
    "video": "retain-on-failure",
    "screenshot": "only-on-failure",
    "trace": "retain-on-failure",
}
```

### pytest.ini

```ini
[pytest]
testpaths = tests
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (DB, Auth0 mocks, WebSocket envelope)
    e2e: End-to-end tests (Playwright)
    visual: Visual regression tests
addopts =
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-fail-under=80
```
