---
name: general-rtk-usage
description: |
  Use RTK (Rust Token Killer) CLI for token-optimized command execution. RTK is a high-performance CLI proxy 
  that reduces LLM token consumption by 60-90% on common dev commands. Use when:
  - Running common CLI commands (git, npm, pytest, docker, etc.)
  - Need to optimize token usage in CLI outputs
  - Working with GitHub CLI (gh), Docker, npm, or other supported commands
  - NOTE: Does NOT support Python pytest-playwright (.py) files - only JavaScript/TypeScript
---

# RTK Usage Guide

## What is RTK?

RTK (Rust Token Killer) is a CLI proxy that provides compact, token-optimized output for common development commands. It reduces LLM token consumption by 60-90%.

## Supported Commands

| Command | Description |
|---------|-------------|
| `rtk git` | Git commands with compact output |
| `rtk gh` | GitHub CLI with optimized output |
| `rtk pytest` | Pytest with compact output |
| `rtk docker` | Docker with compact output |
| `rtk npm` | npm with filtered output |
| `rtk playwright` | Playwright E2E tests with compact output |
| `rtk ruff` | Ruff linter with compact output |

## Playwright with RTK

**IMPORTANT: RTK Playwright ONLY supports JavaScript/TypeScript test files.**

### IMPORTANT: RTK Output is Compact

RTK playwright shows only test results in compact format:
- PASS/FAIL counts
- Test names that failed
- Short error messages

It does NOT show:
- Full stack traces
- Test setup/teardown details  
- Browser console logs
- HTTP request/response details

For full debugging, you MUST read the log files (see "Reading Full Playwright Logs" below).

### Works ✅
```bash
rtk playwright test tests/e2e/
rtk playwright test tests/e2e/example.spec.js --project=chromium
```

### Does NOT Work ❌
```bash
rtk playwright test tests/e2e/test_example.py  # Python pytest-playwright
# Error: [RTK:PASSTHROUGH] playwright parser: All parsing tiers failed
```

RTK's parser only recognizes `.spec.js`, `.spec.ts`, `.test.js`, `.test.ts` patterns.

## Usage Examples

```bash
# Git commands
rtk git status
rtk git log --oneline -10

# Run tests
rtk pytest tests/
rtk pytest tests/ -k "test_name"

# Docker
rtk docker ps
rtk docker logs container_id

# npm
rtk npm run build
```

## Reading Full Playwright Logs

When RTK gives compact output, you need the full logs to debug test failures.

### Option 1: Read RTK Log File
RTK saves full output to a tee log file. Look for the path in the RTK output:
```
[full output: ~/.local/share/rtk/tee/<timestamp>_playwright.log]
```
Read it with:
```bash
cat ~/.local/share/rtk/tee/<timestamp>_playwright.log
```
Or use rtk read:
```bash
rtk read ~/.local/share/rtk/tee/<timestamp>_playwright.log
```

### Option 2: Run Without RTK
For verbose output directly in terminal:
```bash
npx playwright test tests/e2e/ --project=chromium --reporter=line
```

## When NOT to Use RTK

- Python pytest-playwright tests (use `uv run pytest` instead)
- Commands not in the supported list (use native CLI)
- Need full verbose output for debugging