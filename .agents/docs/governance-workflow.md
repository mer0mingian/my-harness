# Technical Governance Workflow — Usage Guide

A short guide for users invoking the Phase 0 Technical Governance workflow on
a new or existing enterprise project.

---

## When to use

- **New project**: run before BMAD Phase 1 (Analysis). The artifacts capture
  constraints that should not be re-discovered every feature.
- **Existing project (brownfield)**: run when there is no existing
  `docs/governance/` directory, or when an audit reveals scattered tech
  preferences and ungoverned NFRs.
- **Periodic refresh**: quarterly, or after any major dependency shift /
  compliance change.

---

## How to invoke

```text
/governance-setup <project name or short brief>
```

What happens:

1. `@governance-lead` scans the repo for existing tech-stack signals
   (CLAUDE.md, README.md, pyproject.toml, package.json, .editorconfig).
2. It runs the `governance-interview-tech-stack` skill — eight question
   blocks, batched, no question that the repo already answers.
3. It dispatches three authors in parallel:
   - `@governance-constitution-author` -> `docs/governance/TECHNICAL_CONSTITUTION.md`
   - `@governance-nfr-specialist` -> `docs/governance/NFR_CATALOG.md`
   - `@governance-test-architect` -> `docs/governance/TEST_STRATEGY.md`
4. It runs `governance-validate-artifacts` to schema-check all three.
5. It returns a summary with paths, validation status, and the next
   recommended command (`/bmad-spec` to begin Phase 1).

Total time on a brownfield repo: typically 20-40 minutes (mostly the
interview).

---

## Auxiliary commands

- `/governance-update-constitution <section>` — amend a specific
  constitution section without rewriting approved content.
- `/governance-add-nfr <subject>` — add a single NFR using EARS notation,
  preserving stable IDs.
- `/governance-validate` — re-run validation any time, e.g. before a PR
  merge or as a CI gate.

---

## What the artifacts contain

| File                                            | Sections (canonical)                                                                                                    |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `docs/governance/TECHNICAL_CONSTITUTION.md`     | Header, Tech Preferences, Solution Approach, Code Quality, Security Baseline, Amendment Process, Tooling Appendix.       |
| `docs/governance/NFR_CATALOG.md`                | ISO/IEC 25010 sections (PERF, REL, SEC, USE, MAIN, COMP, PORT, FUNC), each NFR with EARS statement, AC, test, priority.  |
| `docs/governance/TEST_STRATEGY.md`              | Pyramid, E2E scope, Playwright patterns, visual regression, test data, CI matrix, metrics, maintenance, tool config.      |

All three are markdown — humans read them, agents parse them, the validator
checks them.

---

## How later workflows consume them

- BMAD Analysis / PM / Architecture agents read all three when planning.
- PRIES `@pm` cites NFR IDs in tickets.
- PRIES `@test` generates Playwright tests using TEST_STRATEGY patterns and
  NFR acceptance criteria.
- PRIES `@make` validates each command against the constitution
  (`uv` not `pip`, etc.).
- PRIES `@check` enforces the constitution and NFR_CATALOG during review.

See [technical-governance-integration.md](./technical-governance-integration.md)
for the full integration matrix.

---

## Customising for your tech stack

The interview skill is opinionated about Python/FastAPI/HTMX/Alpine because
that is the reference stack used in Stepstone projects. To adapt:

1. **Different backend** (Node, Go, Rust): override the Block 2 defaults
   during the interview. The constitution writer will use whatever you
   confirm.
2. **Different frontend** (React, Vue): you can permit React via the
   interview, but the writer will require a rationale because the default
   constitution prohibits client-side state machines. Prepare to justify.
3. **Different E2E framework** (Cypress, Playwright TS, Detox): change the
   `framework` field in the test strategy interview answer; the skill rules
   (POM required, no `time.sleep`) still apply.

If you maintain multiple project types in the same fleet, consider keeping
`.agents/examples/governance/<project-shape>/` reference artifacts (e.g.
`sta2e-vtt/`, `saas-b2b/`, `mobile/`) as starting points.

---

## Anti-patterns

- **Skipping Phase 0** because "we already know our stack". The constitution
  is for new contributors and AI agents who do not have your tribal
  knowledge.
- **Treating the constitution as immutable**. Amendments are expected — see
  the Amendment Process section. The point is that changes are explicit and
  auditable, not impossible.
- **Loading all NFRs as P0**. If everything is a launch blocker, nothing is.
  Use P1/P2 to capture aspirational targets honestly.
- **Writing E2E tests that bypass the strategy**. The strategy is normative
  for `@test` — if you need an exception, document it in the test docstring
  with a link to a refactor ticket.
