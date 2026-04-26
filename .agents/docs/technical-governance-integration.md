# Technical Governance — Integration Points

How Phase 0 governance artifacts feed the BMAD planning workflow and the
PRIES implementation workflow. This document is read by humans and by the
`@governance-lead`, `@bmad-*`, and `@pm`/`@test`/`@make`/`@check`/`@simplify`
agents.

---

## TL;DR

| Phase | Workflow | What it consumes from `docs/governance/`                   |
| ----- | -------- | ----------------------------------------------------------- |
| 0     | governance | Produces all three artifacts.                              |
| 1     | BMAD Analysis | Constitution constraints (no React etc.), NFR priorities. |
| 2     | BMAD PM   | NFR IDs cited in user stories' acceptance criteria.         |
| 3     | BMAD Architecture | Validates ADRs against constitution; cites NFR IDs.   |
| 4a    | PRIES @pm | Linear/Jira ticket descriptions reference NFR IDs.          |
| 4b    | PRIES @test | TEST_STRATEGY patterns + NFR IDs drive test generation.   |
| 4c    | PRIES @make | Constitution dictates tech stack and code style.          |
| 4d    | PRIES @check | Constitution + NFR_CATALOG drive review checklist.       |
| 4e    | PRIES @simplify | Constitution KISS rules anchor refactor decisions.    |

---

## 1. BMAD integration

### Phase 0 -> Phase 1 hand-off

Phase 0 ends when `governance-validate-artifacts` returns `overall: PASS` (or
`WARN` with explicit user override). The Governance Lead's final message:

1. Lists the three artifact paths.
2. Lists any `TBD` markers that need human decisions before the project can
   ship.
3. Recommends `/bmad-spec <feature>` to begin Phase 1.

### What Phase 1 (Analysis) reads

`@bmad-analyst` reads:
- `docs/governance/TECHNICAL_CONSTITUTION.md` — to know which solution
  approaches are off the table before framing the problem.
- `docs/governance/NFR_CATALOG.md` priorities — to weight the analysis (e.g.
  a P0 latency NFR forces analysis to consider real-time UX).

### What Phase 2 (PM) reads

`@bmad-pm` reads:
- `docs/governance/NFR_CATALOG.md` — every user story carries acceptance
  criteria of the form "must satisfy NFR-PERF-001". The PM never invents a
  threshold; they cite the NFR.
- `docs/governance/TEST_STRATEGY.md` — to ensure proposed stories map to
  existing critical journeys or trigger new ones.

### What Phase 3 (Architecture) reads

`@bmad-architect` reads all three artifacts. The constitution is binding:

- A proposed ADR that conflicts with constitution Section 2 must include a
  formal exception (Amendment Process Section 5) or be rewritten.
- ADRs cite NFR IDs they satisfy (e.g. "ADR-007 chooses fan-out over
  broadcast to satisfy NFR-PERF-002").

A linter check (CI hook) flags ADRs proposing tech that the constitution
prohibits.

---

## 2. PRIES integration

PRIES (PM -> Make -> Test -> Review -> Simplify) is the implementation
workflow that runs inside BMAD Phase 4.

### `@pm`

Reads NFR_CATALOG. When fetching a Linear ticket, validates that the ticket
description references at least one NFR ID. If not, posts a comment asking
PM to add one before implementation starts.

### `@test`

Reads TEST_STRATEGY + NFR_CATALOG. Generates Playwright tests using:
- Locator strategy (role -> label -> test_id, never CSS).
- Page Object Model pattern.
- Auto-wait, never `time.sleep`.
- Factory or fixture pattern from Section 5 of the strategy.

For each NFR cited in the ticket, generates an assertion that exercises the
acceptance criterion (axe scan for NFR-USE-001, perf timer for NFR-PERF-002,
etc.).

### `@make`

Reads TECHNICAL_CONSTITUTION. Validates each command/library it would use:

- Uses `uv` not `pip`.
- Uses framework named in the constitution.
- Adheres to naming and docstring conventions.
- Refuses to scaffold anything explicitly prohibited (e.g. React component).
  Surfaces a "Constitution Exception Request" instead.

### `@check`

Reads all three artifacts. Review checklist includes:

- [ ] No constitution violation introduced (tech stack, patterns).
- [ ] Every new public function has a type hint and docstring.
- [ ] Each NFR cited in the ticket has at least one passing test asserting
      its acceptance criterion.
- [ ] Coverage threshold (NFR-MAIN-001) satisfied.

When violations are found, `@check` does not auto-reject; it produces a
structured exception request listing options (comply / amend constitution /
escalate).

### `@simplify`

Reads TECHNICAL_CONSTITUTION's Section 2 ("Solution Approach Constraints")
and any KISS / YAGNI rules. Flags refactors that:

- Introduce abstractions the constitution does not require.
- Add a new framework or service without a constitution amendment.

---

## 3. CI gate sketch

```yaml
# .github/workflows/governance.yml
name: Phase 0 governance gate
on:
  pull_request:
    paths:
      - "docs/governance/**"
      - "src/**"
      - "tests/**"

jobs:
  validate-governance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install jsonschema pyyaml
      - run: python .agents/skills/governance-validate-artifacts/scripts/validate.py --root .
```

A failing run blocks merge until either the artifacts are fixed or an
exception is approved via the Amendment Process.

---

## 4. Reusability for non-VTT projects

The governance plugin is project-agnostic by design:

- Templates substitute project-specific values via placeholder tokens.
- The interview skill always asks the same eight blocks, so any enterprise
  project can run `/governance-setup` without code changes.
- The example under `.agents/examples/governance/sta2e-vtt/` is reference
  only; new projects start from the empty templates.

For a SaaS B2B project, expect:
- More NFRs in the SEC and PORT categories (SOC 2, multi-tenant isolation).
- A different pyramid (often 70/20/10 or 70/25/5 — backend-heavy).
- Critical journeys focused on billing, onboarding, RBAC.

For a mobile-only project, swap Playwright for Detox / Maestro in the test
strategy. The skill rules and validator do not assume Playwright; they
assume "an E2E framework is named and POM is required". Update the
`framework` field accordingly.
