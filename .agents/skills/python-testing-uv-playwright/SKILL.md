---
name: python-testing-uv-playwright
description: |
  Run Python Playwright E2E tests using uv package manager. Use when:
  - Running Python pytest-playwright tests
  - Need E2E testing for Python web applications
  - Working with playwright.sync_api in Python
  - NOTE: For JavaScript/TypeScript Playwright tests (.spec.js), use rtk or npx instead
---

# Python Testing with UV & Playwright

## Running Tests

### Python pytest-playwright (`.py` files)
```bash
# Run all Python E2E tests
uv run pytest tests/e2e/test_m16_playwright.py -v

# Run specific test class
uv run pytest tests/e2e/test_m16_playwright.py::TestRightSidebar -v

# Run specific test
uv run pytest tests/e2e/test_m16_playwright.py::TestRightSidebar::test_right_sidebar_visible -v

# Run with coverage
uv run pytest tests/ --cov=sta --cov-report=html
```

### JavaScript/TypeScript Playwright (`.spec.js` files)
```bash
# Use rtk for token-optimized output
rtk playwright test tests/e2e/

# Or use npx directly
npx playwright test tests/e2e/

# With specific browser
npx playwright test tests/e2e/ --project=chromium
```

## Key Points

- **Python tests**: Use `uv run pytest` (not `uv run playwright`)
- **JS tests**: Use `rtk playwright` or `npx playwright test`
- **RTK does NOT support Python** `.py` test files (use `uv run pytest` instead)

## How It Works

The `tests/e2e/conftest.py` automatically starts the web server:
- Uses the project's `.venv/bin/python` if available, otherwise `python3`
- Starts uvicorn on port 5001
- Waits for server to be ready before running tests

## Common Issues

### Server fails to start
If you see `RuntimeError: Web server failed to start`:
- Check that port 5001 is not already in use
- Verify `.venv/bin/python` exists or `python3` is available

### Event loop errors
If you see `RuntimeError: Runner.run() cannot be called from a running event loop`:
- This was fixed with `tests/e2e/pytest.ini` configuration
- If persists, try: `uv run pytest tests/e2e/test_m16_playwright.py -v -p no:asyncio`

## Test Files in This Project

| File | Type | Recommended Command |
|------|------|---------------------|
| `tests/e2e/m16.right-sidebar.spec.js` | JavaScript Playwright | `rtk playwright test tests/e2e/` ✅ Works |
| `tests/e2e/test_m16_playwright.py` | Python pytest-playwright | `uv run pytest tests/e2e/test_m16_playwright.py -v` ✅ Works |