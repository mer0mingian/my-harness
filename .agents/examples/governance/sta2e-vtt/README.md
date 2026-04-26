# STA2E VTT Lite — Phase 0 Example

A worked example of the Phase 0 governance artifacts for the Star Trek
Adventures 2e Virtual Tabletop test project. Use this as a reference when
authoring artifacts for a new enterprise project.

## Files

- [TECHNICAL_CONSTITUTION.md](./TECHNICAL_CONSTITUTION.md) — FastAPI + HTMX + Alpine.js stack, server-driven UI, Auth0.
- [NFR_CATALOG.md](./NFR_CATALOG.md) — seven NFRs covering performance, reliability, security, usability, maintainability. Notice NFR-PERF-002 (WebSocket fan-out under 200ms).
- [TEST_STRATEGY.md](./TEST_STRATEGY.md) — 60/25/15 pyramid (UI-heavy), six critical journeys cross-referenced to NFR IDs.

## How this was produced

1. `/governance-setup STA2E VTT Lite` would dispatch `@governance-lead`.
2. `@governance-lead` reads the existing `sta2e_minimal_vtt/` repo signals + this project's `legacy_docs/`.
3. `governance-interview-tech-stack` fills the gaps (multiplayer latency target, WCAG level, etc.).
4. `@governance-constitution-author`, `@governance-nfr-specialist`, and
   `@governance-test-architect` run in parallel.
5. `governance-validate-artifacts` confirms schema compliance and cross-references.

## What to copy / what to change for a different project

**Copy:**
- The section structure (always seven constitution sections, eight NFR
  categories, nine test-strategy sections).
- The NFR ID convention.
- The Playwright POM / role-locator / no-`time.sleep` discipline.

**Change:**
- The tech stack table in the constitution.
- The pyramid ratios if your project is more backend-heavy.
- The list of critical user journeys (these are VTT-specific).
- The compliance regimes (this project flags WCAG only; SaaS B2B usually adds SOC 2).
