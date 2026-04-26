---
name: governance-test-strategy-writer
description: Generate or amend TEST_STRATEGY.md covering pyramid ratios, Playwright
  patterns, test data strategy, visual regression, and CI execution. Cross-references
  NFR IDs. Use when @governance-test-architect authors or updates the strategy.
---
# Governance Test Strategy Writer

Rules and templates for producing `docs/governance/TEST_STRATEGY.md`.

## Required sections (in order)

1. **Test Pyramid Ratios** — explicit numbers (e.g. 70/20/10 unit/integration/E2E).
2. **E2E Test Scope** — table of critical user journeys with IDs, NFR refs, priority.
3. **Playwright Implementation Patterns** — locator strategy, POM, auto-wait.
4. **Visual Regression Testing** — scope, tool, baseline management.
5. **Test Data Strategy** — fixtures vs factories vs realistic data, isolation.
6. **CI/CD Integration** — pre-commit / PR / main / nightly execution policy.
7. **Metrics & Reporting** — coverage target, flakiness target, duration budget.
8. **Test Maintenance** — quarterly review cadence and documentation rules.
9. **Appendix: Tool Configuration** — `playwright.config.py`, `pytest.ini`.

## Mandatory rules

- **Locators**: role-based (`get_by_role`, `get_by_label`, `get_by_test_id`)
  preferred. CSS/XPath only with explicit justification per test.
- **POM**: every E2E test MUST instantiate a Page Object class — no inline
  navigation logic in test bodies.
- **Auto-wait**: rely on Playwright auto-wait (`expect(...).to_be_visible()`
  patterns). `time.sleep()` is prohibited; `page.wait_for_timeout()` is
  last resort with a comment.
- **Retries**: max 2 retries per test in CI; persistently flaky tests are
  quarantined with an issue link.
- **Coverage gate**: CI fails if coverage drops below the threshold in section 7.

## Pyramid defaults

| Project shape           | Unit | Integration | E2E |
| ----------------------- | ---- | ----------- | --- |
| Backend API             | 70   | 25          | 5   |
| Full-stack web (default)| 70   | 20          | 10  |
| UI-heavy SPA / VTT      | 60   | 25          | 15  |
| Microservice mesh       | 60   | 30          | 10  |

If the user picks a non-default ratio, capture rationale in the section header.

## Critical user journey table format

```markdown
| Journey ID    | Description                                           | Test Count | NFRs Validated         | Priority |
|---------------|-------------------------------------------------------|------------|------------------------|----------|
| AUTH-001      | OAuth login -> landing page                           | 2          | NFR-SEC-001            | P0       |
| DICE-001      | GM rolls dice -> all players see result <200ms        | 3          | NFR-PERF-002, USE-001  | P0       |
```

Journey IDs follow `<DOMAIN>-NNN`. Pick stable domains (`AUTH`, `CHECKOUT`,
`SEARCH`, `ADMIN`, custom domains for the project).

## Playwright pattern reference (copy into the strategy doc)

```python
# pages/checkout_page.py
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

## Visual regression policy

- Public pages: every PR (Percy/Chromatic or Playwright snapshots).
- Authenticated workflows: per-release.
- Admin pages: manual QA only, unless flagged in NFR_CATALOG.
- Baselines captured in CI Docker image, never on developer laptops.

## CI execution matrix template

```markdown
| Trigger      | Tests run                          | Timeout | Workers |
|--------------|------------------------------------|---------|---------|
| Pre-commit   | Fast unit tests only               | 30s     | 1       |
| PR pipeline  | Unit + integration                 | 5m      | 4       |
| Main merge   | All + E2E                          | 15m     | 8       |
| Nightly      | All + visual regression            | 30m     | 16      |
```

## Authoring workflow

1. Load template `.agents/templates/governance/TEST_STRATEGY.template.md`.
2. Choose pyramid ratios from the project-shape table; record any override.
3. For each E2E journey, ensure the NFR cell is filled — challenge gaps.
4. Insert Playwright patterns block; do not change locator/POM/auto-wait rules.
5. Fill visual regression section based on interview answer.
6. Insert CI matrix.
7. Run schema validation.

## Output checklist

- [ ] Nine required sections present, in order.
- [ ] Pyramid totals 100%.
- [ ] Every E2E journey lists at least one NFR ID, or states `none` with reason.
- [ ] Playwright section forbids `time.sleep` and CSS-only locators.
- [ ] CI matrix lists pre-commit / PR / main / nightly rows.
- [ ] File validates against `test-strategy.schema.json`.
