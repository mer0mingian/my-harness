# E2E Test Strategy

**Project:** {{project_name}}
**Version:** {{version}}
**Last Updated:** {{date}}
**Test Framework:** {{e2e_framework}}

---

## 1. Test Pyramid Ratios

| Test Type      | Target % | Notes                                                  |
| -------------- | -------- | ------------------------------------------------------ |
| Unit           | 70%      | Fast feedback, pinpoint failures, low maintenance.     |
| Integration    | 20%      | Service boundaries, DB, external APIs.                 |
| E2E            | 10%      | Critical user journeys.                                |

**Rationale for chosen ratios:** Company standard 70/20/10 test pyramid ensures consistency across projects.

---

## 2. E2E Test Scope

### 2.1 Critical User Journeys

| Journey ID    | Description                          | Test Count | NFRs Validated      | Priority |
| ------------- | ------------------------------------ | ---------- | ------------------- | -------- |
| {{id_1}}      | {{desc_1}}                           | {{n_1}}    | {{nfrs_1}}          | {{p_1}}  |
| {{id_2}}      | {{desc_2}}                           | {{n_2}}    | {{nfrs_2}}          | {{p_2}}  |

**Selection criteria:**
- **P0:** revenue-generating, AuthN, data integrity, regulatory.
- **P1:** frequent workflows, admin/power-user features.
- **P2:** edge cases, rarely used features.

**Not covered by E2E:**
- Unit-level validation (regex, value checks) -> unit tests.
- Error messages for invalid inputs -> integration tests.
- Non-critical UI tweaks (button colour) -> visual regression snapshots.

---

## 3. Playwright Implementation Patterns

### 3.1 Locator Strategy

Prefer in this order:

1. Role locators: `page.get_by_role("button", name="Submit")`
2. Label / placeholder locators: `page.get_by_label("Email")`
3. Test IDs (fallback): `page.get_by_test_id("user-menu")`
4. CSS / XPath: PROHIBITED unless explicitly justified per test.

### 3.2 Page Object Model

Every E2E test instantiates a Page Object class. No inline navigation logic in
test bodies.

```python
from playwright.sync_api import Page

class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.email = page.get_by_label("Email")
        self.submit = page.get_by_role("button", name="Place Order")

    def fill_email(self, email: str) -> None:
        self.email.fill(email)

    def submit_order(self) -> None:
        self.submit.click()
        self.page.wait_for_url("**/order-confirmation")
```

### 3.3 Auto-wait vs explicit waits

- Rely on Playwright auto-wait for visibility, enabled, stable.
- `time.sleep()` is **prohibited**.
- `page.wait_for_timeout()` only as last resort, with a comment.
- Use `page.expect_response(...)` for network events.

---

## 4. Visual Regression Testing

| Page type            | Coverage                | Tool                      | Frequency       |
| -------------------- | ----------------------- | ------------------------- | --------------- |
| Public pages         | {{public_coverage}}     | {{public_tool}}           | {{public_freq}} |
| Authenticated pages  | {{auth_coverage}}       | {{auth_tool}}             | {{auth_freq}}   |
| Admin pages          | {{admin_coverage}}      | {{admin_tool}}            | {{admin_freq}}  |

Baselines are captured in CI Docker images, never on developer laptops.

---

## 5. Test Data Strategy

| Approach        | Use Case                                       | Example tool       |
| --------------- | ---------------------------------------------- | ------------------ |
| Fixtures        | Shared reference data (countries, currencies)  | `pytest.fixture`   |
| Factories       | Test-specific records (users, orders)          | `factory_boy`      |
| Realistic data  | E2E flows requiring domain fidelity            | Anonymised dump    |

Each test cleans up after itself (transaction rollback for integration, fixture
teardown for E2E). Sensitive data is generated with `faker`; production
credentials are never used in tests.

---

## 6. CI/CD Integration

| Trigger        | When                  | Tests run                          | Timeout | Workers |
| -------------- | --------------------- | ---------------------------------- | ------- | ------- |
| Pre-commit     | Before commit         | Fast unit tests only               | 30s     | 1       |
| PR pipeline    | On PR open/update     | Unit + integration                 | 5m      | 4       |
| Main branch    | After merge           | All tests + E2E                    | 15m     | 8       |
| Nightly        | 02:00 daily           | All + visual regression            | 30m     | 16      |

**Flaky test policy:** auto-retry max 2 times in CI; persistent flakes are
quarantined with an issue link.

---

## 7. Metrics & Reporting

| Metric              | Target              |
| ------------------- | ------------------- |
| Coverage            | >= {{coverage_target}}% |
| Flakiness rate      | < {{flake_target}}%   |
| Test duration       | <= {{duration_target}} |
| E2E pass rate       | >= {{e2e_pass_target}}% |

Artifacts uploaded to CI on failure: screenshots, videos, Playwright traces.

---

## 8. Test Maintenance

- Quarterly review removes obsolete tests, refreshes baselines, fixes flakes.
- Every E2E test carries a docstring: purpose, preconditions, expected outcome,
  NFR IDs validated.

---

## 9. Appendix: Tool Configuration

### Playwright config

```python
# playwright.config.py
config = {
    "base_url": "{{base_url}}",
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
    integration: Integration tests (DB, external APIs)
    e2e: End-to-end tests (Playwright)
    visual: Visual regression tests
addopts =
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-fail-under={{coverage_target}}
```
