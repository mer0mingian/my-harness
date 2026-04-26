---
name: governance-interview-tech-stack
description: Conduct a structured interview that captures tech preferences, solution
  approach constraints, NFR priorities, and test strategy posture. Use when starting
  Phase 0 of the BMAD workflow on a new enterprise project, or when amending an
  existing TECHNICAL_CONSTITUTION/NFR_CATALOG/TEST_STRATEGY.
---
# Governance Interview Skill

A short, opinionated checklist that produces enough structured input for the
constitution, NFR, and test-strategy authors to work without inventing facts.

## When to use

- `@governance-lead` runs Phase 0 and the user has not yet supplied a constitution.
- `/governance-update-constitution` is invoked and a section is being amended.
- A new NFR category needs to be added (e.g. compliance request).

## Block 1 — Project context (always)

Ask once, in one message:

1. Project name, one-line goal, target users.
2. Greenfield or brownfield? If brownfield, list any docs/files already encoding
   tech choices (CLAUDE.md, README.md, pyproject.toml, package.json, etc.).
3. Compliance regimes that apply: SOC 2, HIPAA, GDPR, PCI-DSS, WCAG, ADA, none.
4. Deployment target: local-only, single-tenant SaaS, multi-tenant SaaS, on-prem.

## Block 2 — Tech stack (constitution input)

Confirm or challenge defaults:

| Topic                     | Default                                          | Ask if unclear                          |
| ------------------------- | ------------------------------------------------ | --------------------------------------- |
| Backend language          | Python 3.12+                                     | Anything else mandated?                 |
| Web framework             | FastAPI                                          | Flask/Django/none acceptable?           |
| Dependency manager        | `uv`                                             | `pip`/`poetry` permitted?               |
| Database                  | PostgreSQL 15+                                   | Other engines used in fleet?            |
| Frontend rendering        | Server-side Jinja2 + HTMX                        | SPA required?                           |
| Reactive UI               | Alpine.js 3.x                                    | React/Vue mandated?                     |
| CSS                       | Tailwind 3.x                                     | Custom design system?                   |
| Container runtime         | Docker + docker-compose                          | K8s/serverless target?                  |
| Linter / formatter        | ruff                                             | Black/isort still used?                 |
| Type checker              | mypy strict                                      | pyright?                                |

## Block 3 — Solution approach (constitution input)

Yes/no/rationale on each:

- Server-driven UI (no client-side state machines)?
- CQRS or event sourcing for write-heavy paths?
- HATEOAS / hypermedia for REST?
- Soft deletes mandatory?
- Structured logging (JSON) with correlation IDs?
- Circuit breakers for external APIs?

## Block 4 — Security baseline (constitution input)

- Identity provider (Auth0, Okta, Cognito, custom)?
- Token policy (access/refresh TTL)?
- Encryption at rest standard (AES-256-GCM default)?
- Encryption in transit (TLS 1.3 default)?
- Secrets management (env + vault)?
- Dependency CVE scan cadence?

## Block 5 — NFR priorities (NFR catalog input)

For each ISO/IEC 25010 category, ask: "Is this a P0 launch blocker, P1 high, P2
medium, or out-of-scope?" Capture at least:

- Performance: target p95 latency under load.
- Reliability: uptime SLO, RTO, RPO.
- Security: AuthN, encryption, dependency CVE policy.
- Usability: WCAG conformance level, supported viewport range.
- Maintainability: minimum coverage threshold.
- Compatibility: target browsers and versions.
- Portability: 12-factor compliance, dev/staging/prod parity.

## Block 6 — Test strategy posture (test strategy input)

- Test pyramid ratios (default 70/20/10, override allowed).
- E2E framework choice (Playwright Python default).
- Visual regression scope (every PR, nightly, off).
- Locator policy (role-based default, exceptions explicit).
- CI execution policy (workers, retries, timeout budgets).

## Output format

Return a structured map the author agents can consume directly. Example shape:

```yaml
project:
  name: "STA2E VTT Lite"
  greenfield: true
  compliance: ["WCAG 2.1 AA"]
tech_stack:
  backend: { language: "Python 3.12+", framework: "FastAPI", dep_manager: "uv" }
  frontend: { rendering: "Jinja2+HTMX", reactive: "Alpine.js 3.x", css: "Tailwind 3.x" }
solution:
  server_driven_ui: true
  cqrs: false
  hateoas: true
security:
  idp: "Auth0"
  token_ttl: { access: "15m", refresh: "7d" }
nfr_priorities:
  perf: "P0"
  rel: "P1"
  sec: "P0"
  use: "P0"
  maintain: "P1"
test_strategy:
  pyramid: { unit: 70, integration: 20, e2e: 10 }
  e2e_framework: "Playwright Python"
  visual_regression: "every PR"
```

## Anti-patterns

- Asking the user 30 questions one at a time. Batch all of Block 1 first, then
  iterate on remaining blocks only where defaults don't fit.
- Inventing answers when the user is silent. Mark `TBD` and stop.
- Skipping the brownfield repo scan. The repo often answers half the questions.
