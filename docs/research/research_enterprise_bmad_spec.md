# Enterprise-Grade BMAD Specification Enhancement

**Research Report**  
**Date:** 2026-04-26  
**Status:** Proposal for Review  
**Context:** Enhancing BMAD methodology with enterprise-grade specifications for technology preferences, solution constraints, NFRs, and E2E testing

---

## Executive Summary

This research identifies critical specification gaps in the standard BMAD workflow and proposes **three new artifacts** to capture enterprise requirements that don't fit traditional PRDs or ADRs:

1. **TECHNICAL_CONSTITUTION.md** — Governance document defining non-negotiable architectural principles, technology preferences, and solution approach constraints
2. **NFR_CATALOG.md** — Structured non-functional requirements with testable acceptance criteria
3. **TEST_STRATEGY.md** — E2E testing blueprint defining test pyramid ratios, Playwright patterns, and data strategies

These artifacts integrate into BMAD as **Phase 0: Technical Governance** (pre-analysis), providing persistent constraints that guide all subsequent phases.

---

## Table of Contents

1. [Gap Analysis](#1-gap-analysis)
2. [Proposed Artifacts](#2-proposed-artifacts)
3. [BMAD Integration Strategy](#3-bmad-integration-strategy)
4. [PRIES Workflow Integration](#4-pries-workflow-integration)
5. [STA2E VTT Example](#5-sta2e-vtt-example)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [References](#7-references)

---

## 1. Gap Analysis

### 1.1 What Standard BMAD Phases Cover Well

Standard BMAD (Analysis → PM → Architecture → Implementation) excels at:

| Phase | Strengths | Artifact Types |
|-------|-----------|----------------|
| **Analysis** | Problem framing, stakeholder identification, business context | Problem statements, stakeholder maps, constraints |
| **PM** | User-facing requirements, acceptance criteria, success metrics | PRDs, user stories, roadmaps |
| **Architecture** | System design, component boundaries, major technical decisions | ADRs, system diagrams, API contracts |
| **Implementation** | Code generation following TDD/BDD patterns | Tests, source code, deployment scripts |

**Key insight:** BMAD assumes requirements and architecture decisions are *discoverable* through each phase. This works for greenfield projects but breaks down when:
- The project has established **technology conventions** ("we always use Alpine.js, not React")
- There are **regulatory constraints** (HIPAA, GDPR, SOC 2 compliance)
- The team has **hard-won lessons** embedded in code style, testing patterns, or deployment procedures

### 1.2 What Standard BMAD Phases Miss

Four categories of critical requirements fall through the cracks:

#### A. Technology Preferences

**Examples:**
- "Prefer Alpine.js over React for progressive enhancement"
- "Use `uv` for Python dependency management, not `pip` or `poetry`"
- "FastAPI for APIs, no Flask or Django"
- "PostgreSQL only; no MongoDB experiments without approval"

**Why it matters:**
- AI agents default to popular choices (React, pip) unless explicitly constrained
- Tech stack fragmentation creates maintenance burden
- Legacy choices have hidden dependencies (e.g., HTMX requires server-rendered templates)

**Where it doesn't fit:**
- **Not a PRD concern** — users don't care about Alpine.js vs React
- **Not an ADR** — these aren't *decisions* being made; they're *governance rules* that predate the current project

**Current workaround:** Repeat preferences in every ADR → brittle, inconsistent enforcement

---

#### B. Solution Approach Constraints

**Examples:**
- "Server-driven UI: no client-side state beyond form inputs"
- "Event sourcing for audit trails; no direct database updates"
- "Prefer composition over inheritance for all new code"
- "REST APIs must use hypermedia (HATEOAS) for discoverability"

**Why it matters:**
- These constraints shape the *entire solution space*, not just one component
- Violating them creates architectural debt that's expensive to fix
- AI agents need these boundaries *before* designing solutions

**Where it doesn't fit:**
- **Not a PRD** — business users don't know what "server-driven UI" means
- **Not a single ADR** — these cut across multiple components and decisions
- **Not a user story** — no user persona for "must use event sourcing"

**Current workaround:** Implicit knowledge in architect's head → lost when team changes

---

#### C. Non-Functional Requirements (NFRs)

**Examples:**
- "API response time p95 < 200ms under 1000 concurrent users"
- "WCAG 2.1 Level AA compliance for all public-facing pages"
- "Data encrypted at rest (AES-256) and in transit (TLS 1.3+)"
- "System must survive single AZ failure with < 30s recovery time"

**Why it matters:**
- NFRs are *testable constraints* that define "done"
- Missing them leads to post-launch performance fires, security incidents, accessibility lawsuits
- AI agents can generate tests *from* NFRs if specified formally

**Where it doesn't fit:**
- **Sometimes in PRD** — but often as vague requirements ("must be fast", "should be secure")
- **Sometimes in ADRs** — but ADRs focus on *how* to achieve NFRs, not the thresholds themselves
- **Never in user stories** — "As a user, I want p95 latency < 200ms" makes no sense

**Current workaround:** Scattered across PRDs, ADRs, and tribal knowledge → untestable, unverified

**Industry standard:** [ISO/IEC 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) defines 8 quality characteristics (Functional Suitability, Performance Efficiency, Compatibility, Usability, Reliability, Security, Maintainability, Portability) with 31 sub-characteristics. Enterprise projects need explicit NFR catalogs.

---

#### D. E2E Test Strategy

**Examples:**
- "70% unit, 20% integration, 10% E2E per test pyramid"
- "Playwright tests must use Page Object Model pattern"
- "Visual regression tests for all public-facing pages (Percy/Chromatic)"
- "Test data: factories for unit tests, fixtures for integration, realistic anonymized data for E2E"

**Why it matters:**
- E2E tests are expensive (slow, flaky, high maintenance)
- Without strategy, teams either over-test (brittle CI) or under-test (production bugs)
- Playwright best practices ([official docs](https://playwright.dev/docs/best-practices)) require upfront decisions (locator strategies, auto-waiting vs explicit waits, screenshot baselines)

**Where it doesn't fit:**
- **Not a PRD** — testing is a technical implementation detail
- **Not an ADR** — testing strategy isn't a single decision; it's a collection of patterns
- **Not a user story** — no user-facing acceptance criteria

**Current workaround:** Ad-hoc decisions during implementation → inconsistent test quality

**Industry guidance:**
- [Test pyramid (2025)](https://www.devzery.com/post/software-testing-pyramid-guide-2025): "The traditional ratio suggests about 70% unit tests, 20% integration tests, and 10% end-to-end tests"
- [Playwright best practices (2026)](https://www.browserstack.com/guide/playwright-best-practices): "Prioritize role locators (getByRole()) to select elements... CSS and XPath are not recommended"
- [Visual regression testing](https://www.browserstack.com/percy/visual-regression-testing): "Baseline screenshots should be captured in a controlled, consistent environment"

---

### 1.3 Why These Gaps Matter for Enterprise Applications

**Compliance & Auditability:**
- SOC 2, HIPAA, PCI-DSS require documented security controls → scattered across ADRs is insufficient
- Auditors need *one artifact* showing "these are our security NFRs"

**Team Scaling:**
- New developers onboard faster with explicit tech preferences → reduces "why are we using X?" questions
- Consistent testing patterns reduce PR review churn

**AI Agent Effectiveness:**
- Agents that know "never use React" *before* Phase 3 (Architecture) avoid wasted design cycles
- NFRs specified in [EARS notation](https://alistairmavin.com/ears/) become directly testable

**Long-Term Maintainability:**
- Solution approach constraints prevent architectural drift
- Test strategy ensures uniform test quality across features

---

## 2. Proposed Artifacts

### 2.1 TECHNICAL_CONSTITUTION.md

**Purpose:** Single authoritative document recording non-negotiable architectural principles, technology preferences, and solution approach constraints.

**Inspiration:** [GitHub spec-kit constitution](https://github.com/github/spec-kit) — "creates a persistent governance document stored at .specify/memory/constitution.md that AI agents reference throughout the specification, planning, and implementation phases"

**Template:**

```markdown
# Technical Constitution

**Project:** [Project Name]  
**Version:** 1.0  
**Last Updated:** [Date]  
**Governance:** Requires architect approval for amendments

---

## 1. Technology Preferences

### 1.1 Backend Stack
- **Language:** Python 3.12+
- **Web Framework:** FastAPI (preferred) | Flask (legacy only)
- **Dependency Management:** `uv` (REQUIRED) | `pip` (prohibited in new projects)
- **Database:** PostgreSQL 15+ (primary) | SQLite (development/testing only)
- **ORM:** SQLAlchemy 2.x with async support

### 1.2 Frontend Stack
- **HTML Rendering:** Server-side templates (Jinja2) with HTMX
- **Reactive UI:** Alpine.js 3.x (preferred) | React (prohibited without approval)
- **CSS Framework:** Tailwind CSS 3.x
- **Build Tool:** None (use CDN for Alpine/HTMX) | Vite (only if bundling required)

### 1.3 Testing & Quality
- **Unit Testing:** pytest with pytest-asyncio
- **E2E Testing:** Playwright (Python bindings)
- **Mocking:** pytest-mock, never unittest.mock
- **Coverage:** pytest-cov with 80% minimum threshold

### 1.4 Infrastructure
- **Containerization:** Docker with multi-stage builds
- **Orchestration:** docker-compose (local/dev) | K8s (production)
- **Secrets Management:** Environment variables + .env files (dev) | HashiCorp Vault (prod)

**Rationale for Choices:**
- `uv` vs `pip`: 10-100x faster dependency resolution ([source](https://github.com/astral-sh/uv))
- Alpine.js vs React: Progressive enhancement, no build step, sub-15kb bundle
- FastAPI vs Flask: Native async, automatic OpenAPI docs, pydantic validation

---

## 2. Solution Approach Constraints

### 2.1 Architecture Patterns
- **MUST:** Use Clean Architecture (domain/application/infrastructure layers)
- **MUST:** Implement CQRS for write-heavy workflows (audit logs, event sourcing)
- **MUST NOT:** Use active record pattern; prefer repository pattern
- **MUST NOT:** Implement client-side state machines; keep state server-side

### 2.2 API Design
- **MUST:** All APIs follow REST + HATEOAS (hypermedia links in responses)
- **MUST:** Use JSON:API spec for pagination, filtering, includes
- **MUST:** Return 4xx for client errors, 5xx only for server failures
- **MUST NOT:** Expose internal IDs; use UUIDs or slugs for public APIs

### 2.3 Data Access
- **MUST:** Use database migrations (Alembic) for all schema changes
- **MUST:** Implement soft deletes (deleted_at timestamp) for audit trails
- **MUST NOT:** Use raw SQL in application code; use ORM or query builder
- **MUST NOT:** Perform joins in application code; push to database

### 2.4 Error Handling
- **MUST:** Use structured logging (JSON) with correlation IDs
- **MUST:** Implement circuit breakers for external API calls
- **MUST NOT:** Swallow exceptions; always log or re-raise
- **MUST NOT:** Return stack traces to end users (security risk)

**Rationale:**
- HATEOAS: Self-documenting APIs, reduces client coupling
- Soft deletes: Regulatory compliance (GDPR right-to-erasure requires audit trail)
- Circuit breakers: Prevents cascading failures in microservices

---

## 3. Code Quality Standards

### 3.1 Naming Conventions
- **Functions:** `snake_case`, verb-noun (e.g., `get_user`, `validate_email`)
- **Classes:** `PascalCase`, noun (e.g., `UserRepository`, `EmailValidator`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `API_TIMEOUT`)
- **Files:** `snake_case.py` (e.g., `user_service.py`, not `UserService.py`)

### 3.2 Documentation Requirements
- **MUST:** Docstrings for all public functions/classes (Google style)
- **MUST:** Type hints for all function signatures (PEP 484)
- **MUST:** README.md with setup instructions, architecture diagram
- **SHOULD:** ADRs for all major technical decisions

### 3.3 Linting & Formatting
- **Formatter:** `ruff format` (replaces Black)
- **Linter:** `ruff check` with project-specific ruleset
- **Type Checker:** `mypy` in strict mode
- **Pre-commit:** All checks must pass before commit

---

## 4. Security Baseline

### 4.1 Authentication & Authorization
- **MUST:** Use OAuth 2.0 + OIDC for external auth
- **MUST:** Implement RBAC with least-privilege principle
- **MUST NOT:** Store passwords in plaintext; use bcrypt/argon2
- **MUST NOT:** Hardcode secrets; use environment variables or vault

### 4.2 Data Protection
- **MUST:** Encrypt PII at rest (AES-256-GCM)
- **MUST:** Use TLS 1.3 for all external communication
- **MUST:** Sanitize user inputs (prevent SQL injection, XSS)
- **MUST NOT:** Log PII or credentials

### 4.3 Dependency Management
- **MUST:** Pin exact versions in requirements.txt
- **MUST:** Run `uv pip audit` weekly for CVE checks
- **MUST:** Update dependencies monthly (non-breaking)
- **MUST NOT:** Use packages with known high/critical CVEs

---

## 5. Amendment Process

**Minor Changes** (e.g., updating Python version from 3.12 to 3.13):
- Propose via PR to this document
- Requires 1 architect approval

**Major Changes** (e.g., switching from PostgreSQL to MongoDB):
- Requires ADR justifying the change
- Requires 2 architect approvals + PM sign-off
- Must include migration plan and rollback strategy

**Effective Date:** Changes take effect upon merge to main branch

---

## Appendix: Tooling Reference

| Category | Tool | Version | Config File |
|----------|------|---------|-------------|
| Python | uv | latest | pyproject.toml |
| Linter | ruff | latest | ruff.toml |
| Type Checker | mypy | 1.8+ | mypy.ini |
| Formatter | ruff format | latest | ruff.toml |
| Testing | pytest | 8.x | pyproject.toml |
| E2E | Playwright | 1.40+ | playwright.config.json |
```

**Usage in BMAD:**
- **Phase 0 (pre-analysis):** Architect creates/updates constitution
- **All agents:** Reference constitution before making technology/design choices
- **Validation gate:** Lint ADRs for constitution violations (e.g., "this ADR proposes React, but constitution prohibits it")

---

### 2.2 NFR_CATALOG.md

**Purpose:** Structured catalog of non-functional requirements with measurable acceptance criteria.

**Inspiration:** 
- [ISO/IEC 25010 Software Quality Model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [EARS notation (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/)
- [ADR Y-Statements](https://medium.com/olzzio/y-statements-10eb07b5a177) for capturing consequences

**Template:**

```markdown
# Non-Functional Requirements Catalog

**Project:** [Project Name]  
**Version:** 1.0  
**Last Updated:** [Date]  
**Validation:** All NFRs must have testable acceptance criteria

---

## NFR Classification (ISO/IEC 25010)

1. **Performance Efficiency** — Response time, throughput, resource utilization
2. **Reliability** — Availability, fault tolerance, recoverability
3. **Security** — Confidentiality, integrity, authentication, authorization
4. **Usability** — Accessibility, learnability, error prevention
5. **Maintainability** — Modularity, testability, modifiability
6. **Compatibility** — Interoperability, coexistence
7. **Portability** — Adaptability, installability

---

## 1. Performance Efficiency

### NFR-PERF-001: API Response Time
**Category:** Performance Efficiency > Throughput  
**Requirement (EARS):**  
> When a user requests data via any REST API endpoint, the system shall return a response within 200ms (p95) under normal load conditions.

**Normal Load:** ≤ 1000 concurrent requests  
**Acceptance Criteria:**
- p50 latency ≤ 100ms
- p95 latency ≤ 200ms
- p99 latency ≤ 500ms
- 0% timeouts under normal load

**Test Strategy:**
- Load testing with Locust or k6
- Monitor with OpenTelemetry traces
- Fail if p95 > 200ms in staging environment

**Priority:** P0 (launch blocker)  
**Rationale:** User research shows 250ms is perceived as "instant"; exceeding this degrades UX

---

### NFR-PERF-002: Database Query Performance
**Category:** Performance Efficiency > Resource Utilization  
**Requirement (EARS):**  
> While the system is processing user requests, all database queries shall execute in ≤ 50ms (p95).

**Acceptance Criteria:**
- No N+1 query patterns (use eager loading)
- All queries use appropriate indexes
- Query plans reviewed in code review

**Test Strategy:**
- `pytest-django` query counter assertions
- Slow query log alerts (> 100ms)
- Database EXPLAIN analysis in CI

**Priority:** P1 (high)

---

## 2. Reliability

### NFR-REL-001: Service Availability
**Category:** Reliability > Availability  
**Requirement (EARS):**  
> The system shall maintain 99.9% uptime (measured monthly) excluding planned maintenance windows.

**Acceptance Criteria:**
- Max unplanned downtime: 43 minutes/month
- Planned maintenance: < 4 hours/month, during off-peak hours
- Health check endpoint returns 200 OK within 1s

**Test Strategy:**
- Uptime monitoring (UptimeRobot, Pingdom)
- Synthetic monitoring for critical user paths
- Chaos engineering tests (kill random pods)

**Priority:** P0 (launch blocker)

---

### NFR-REL-002: Data Durability
**Category:** Reliability > Recoverability  
**Requirement (EARS):**  
> When a user submits data, the system shall ensure zero data loss (RPO = 0) and recovery within 30 minutes (RTO = 30m) in case of single AZ failure.

**Acceptance Criteria:**
- Database: Multi-AZ synchronous replication
- Backups: Automated daily with 30-day retention
- Disaster recovery drills: Quarterly

**Test Strategy:**
- Simulate AZ failure in staging
- Measure RTO/RPO in DR drills
- Verify backup restore procedures

**Priority:** P0 (compliance requirement)

---

## 3. Security

### NFR-SEC-001: Authentication
**Category:** Security > Authentication  
**Requirement (EARS):**  
> When a user attempts to access a protected resource, the system shall require valid OAuth 2.0 access token with appropriate scope.

**Acceptance Criteria:**
- No API endpoints accessible without auth (except public docs)
- Tokens expire after 1 hour (access) / 7 days (refresh)
- Failed login attempts rate-limited (5 attempts/15 min)

**Test Strategy:**
- Security scanning (OWASP ZAP)
- Negative tests (expired tokens, invalid scopes)
- Penetration testing (annual)

**Priority:** P0 (security baseline)

---

### NFR-SEC-002: Data Encryption
**Category:** Security > Confidentiality  
**Requirement (EARS):**  
> The system shall encrypt all PII at rest using AES-256-GCM and in transit using TLS 1.3.

**Acceptance Criteria:**
- Database: Transparent Data Encryption (TDE) enabled
- File storage: Server-side encryption (SSE-S3)
- Network: TLS 1.3 with strong cipher suites only

**Test Strategy:**
- SSL Labs scan (A+ rating required)
- Database encryption audit
- Data-at-rest verification scripts

**Priority:** P0 (compliance: GDPR, HIPAA)

---

## 4. Usability

### NFR-USE-001: Accessibility
**Category:** Usability > Accessibility  
**Requirement (EARS):**  
> All public-facing pages shall conform to WCAG 2.1 Level AA standards.

**Acceptance Criteria:**
- Automated tests: axe-core passing score
- Manual audit: Screen reader compatible (NVDA, JAWS)
- Keyboard navigation: All interactive elements accessible via Tab
- Color contrast: Minimum 4.5:1 for text, 3:1 for UI components

**Test Strategy:**
- Playwright axe-core integration tests
- Manual testing with screen readers
- Annual accessibility audit (external firm)

**Priority:** P0 (legal compliance: ADA)

---

### NFR-USE-002: Mobile Responsiveness
**Category:** Usability > Adaptability  
**Requirement (EARS):**  
> The system shall render correctly on viewports from 320px (mobile) to 2560px (4K desktop).

**Acceptance Criteria:**
- No horizontal scrolling on any viewport width
- Touch targets: Minimum 44x44px (WCAG 2.5.5)
- Responsive images: Serve appropriately sized assets

**Test Strategy:**
- Playwright visual regression tests (320px, 768px, 1920px)
- Manual testing on real devices (iOS, Android)
- Lighthouse mobile performance score ≥ 90

**Priority:** P1 (high)

---

## 5. Maintainability

### NFR-MAIN-001: Code Coverage
**Category:** Maintainability > Testability  
**Requirement (EARS):**  
> All new code shall maintain ≥ 80% line coverage with meaningful tests (not just coverage theater).

**Acceptance Criteria:**
- Unit tests: 90%+ coverage for business logic
- Integration tests: 70%+ for API endpoints
- E2E tests: Cover critical user journeys (login, checkout, etc.)

**Test Strategy:**
- CI fails if coverage drops below 80%
- Code review: Verify tests assert behavior, not implementation
- Mutation testing (optional): Detect weak tests

**Priority:** P1 (quality gate)

---

### NFR-MAIN-002: Technical Debt Management
**Category:** Maintainability > Modifiability  
**Requirement (EARS):**  
> The system shall allocate 20% of sprint capacity to technical debt reduction (refactoring, dependency updates, tooling improvements).

**Acceptance Criteria:**
- Technical debt tracked in backlog (tagged "tech-debt")
- Quarterly architecture review identifies debt hotspots
- Major dependencies updated within 3 months of release

**Test Strategy:**
- Sprint retrospectives review debt reduction progress
- Code metrics: Cyclomatic complexity < 10, function length < 50 LOC

**Priority:** P2 (medium)

---

## 6. Compatibility

### NFR-COMP-001: Browser Support
**Category:** Compatibility > Coexistence  
**Requirement (EARS):**  
> The system shall support the last 2 major versions of Chrome, Firefox, Safari, and Edge.

**Acceptance Criteria:**
- No JavaScript errors in supported browsers
- Polyfills for missing features (e.g., IntersectionObserver in Safari)
- Graceful degradation for unsupported browsers (IE11: show message)

**Test Strategy:**
- BrowserStack cross-browser testing
- Playwright tests run against Chrome, Firefox, WebKit
- Manual smoke tests on Safari/Edge

**Priority:** P1 (high)

---

## 7. Portability

### NFR-PORT-001: Environment Parity
**Category:** Portability > Adaptability  
**Requirement (EARS):**  
> The system shall run identically in development, staging, and production environments (12-factor app principles).

**Acceptance Criteria:**
- All config via environment variables (no hardcoded values)
- Dependencies pinned to exact versions (requirements.lock)
- Dockerized for reproducible builds

**Test Strategy:**
- Integration tests run in Docker container
- Staging environment mirrors production architecture
- Smoke tests after deployment verify config correctness

**Priority:** P0 (operational requirement)

---

## Appendix: NFR Validation Matrix

| NFR ID | Testable? | Automated Test? | Manual Test? | Monitoring? | Owner |
|--------|-----------|-----------------|--------------|-------------|-------|
| PERF-001 | ✅ | Locust load test | - | OpenTelemetry | SRE |
| PERF-002 | ✅ | pytest query counter | Code review | Slow query log | Backend |
| REL-001 | ✅ | Chaos test | DR drill | Uptime monitor | SRE |
| REL-002 | ✅ | Backup restore | DR drill | Backup alerts | SRE |
| SEC-001 | ✅ | OWASP ZAP | Pentest | Auth logs | Security |
| SEC-002 | ✅ | TLS scan | Encryption audit | - | Security |
| USE-001 | ✅ | axe-core | Screen reader | - | Frontend |
| USE-002 | ✅ | Visual regression | Device testing | Lighthouse | Frontend |
| MAIN-001 | ✅ | Coverage report | Code review | - | All |
| MAIN-002 | ❌ | - | Retrospective | Tech debt % | Tech Lead |
| COMP-001 | ✅ | Playwright browsers | BrowserStack | - | Frontend |
| PORT-001 | ✅ | Docker CI | Staging deploy | - | DevOps |

---

## NFR Lifecycle

1. **Definition (Phase 0):** Architect + PM define NFRs before Analysis phase
2. **Refinement (Phase 2):** PM translates NFRs into user stories where applicable
3. **Design (Phase 3):** Architect designs systems to meet NFRs (ADRs reference NFR IDs)
4. **Implementation (Phase 4):** Developers write tests validating NFRs
5. **Monitoring (Phase 5):** SRE/DevOps configure alerts for NFR violations
6. **Review (Quarterly):** Architect reviews NFR compliance, updates thresholds
```

**Usage in BMAD:**
- **Phase 0:** Define NFRs for new projects
- **Phase 2 (PM):** Reference NFR IDs in user stories ("acceptance: must meet NFR-PERF-001")
- **Phase 3 (Architecture):** Design to satisfy NFRs, cite them in ADRs
- **Phase 4 (Implementation):** Generate tests from NFRs using EARS templates
- **Validation gate:** CI checks that all P0 NFRs have passing tests

---

### 2.3 TEST_STRATEGY.md

**Purpose:** E2E testing blueprint defining test pyramid ratios, Playwright patterns, data strategies, and visual regression requirements.

**Inspiration:**
- [Playwright Best Practices (2026)](https://www.browserstack.com/guide/playwright-best-practices)
- [Test Pyramid Strategy](https://www.devzery.com/post/software-testing-pyramid-guide-2025)
- [Visual Regression Testing](https://www.browserstack.com/percy/visual-regression-testing)
- [Test Data Strategies](https://www.testim.io/blog/test-data-is-critical-how-to-best-generate-manage-and-use-it/)

**Template:**

```markdown
# E2E Test Strategy

**Project:** [Project Name]  
**Version:** 1.0  
**Last Updated:** [Date]  
**Test Framework:** Playwright (Python)

---

## 1. Test Pyramid Ratios

Following [industry guidance](https://www.devzery.com/post/software-testing-pyramid-guide-2025), our target distribution:

| Test Type | Target % | Current % | Count | Avg Runtime |
|-----------|----------|-----------|-------|-------------|
| **Unit** | 70% | 68% | 1,234 | 0.1s/test |
| **Integration** | 20% | 22% | 389 | 0.5s/test |
| **E2E** | 10% | 10% | 178 | 5s/test |

**Total Test Suite:** ~1,800 tests running in ~15 minutes (CI)

**Rationale:**
- **Unit tests (70%):** Fast feedback, pinpoint failures, low maintenance
- **Integration tests (20%):** Verify service boundaries, DB interactions, external APIs
- **E2E tests (10%):** Validate critical user journeys, prevent showstopper bugs

**Exceptions:**
- For UI-heavy apps, E2E may increase to 15% (trade-off: slower CI)
- For microservices, integration may increase to 30% (service communication is core value)

---

## 2. E2E Test Scope

### 2.1 Critical User Journeys

E2E tests focus on **business-critical workflows** with high user impact:

| Journey ID | Description | Test Count | Priority |
|------------|-------------|------------|----------|
| **AUTH-001** | User registration → email verification → login | 3 | P0 |
| **AUTH-002** | Password reset flow | 2 | P0 |
| **CHECKOUT-001** | Add to cart → checkout → payment → confirmation | 8 | P0 |
| **ADMIN-001** | Admin creates/edits/deletes content | 5 | P1 |
| **SEARCH-001** | User searches → filters results → views detail | 4 | P1 |

**Selection Criteria:**
- **P0 (must-test):** Revenue-generating, authentication, data integrity
- **P1 (should-test):** Frequent workflows, admin/power-user features
- **P2 (nice-to-test):** Edge cases, rarely used features

**NOT covered by E2E:**
- ❌ Unit-level validation (e.g., email format regex) → unit tests
- ❌ Error messages for invalid inputs → integration tests
- ❌ Non-critical UI tweaks (button color) → visual regression snapshots

---

## 3. Playwright Implementation Patterns

### 3.1 Locator Strategy

Per [Playwright best practices](https://playwright.dev/docs/best-practices), prioritize:

1. **Role locators (PREFERRED):**
   ```python
   page.get_by_role("button", name="Submit")
   page.get_by_role("textbox", name="Email")
   ```
   - Mirrors how users and screen readers perceive the page
   - Resilient to DOM changes

2. **Label/placeholder locators:**
   ```python
   page.get_by_label("Password")
   page.get_by_placeholder("Enter your email")
   ```
   - Good for forms

3. **Test IDs (fallback for dynamic content):**
   ```python
   page.get_by_test_id("user-menu")
   ```
   - Only when role/label locators are ambiguous

4. **CSS/XPath (PROHIBITED without approval):**
   - Brittle, breaks on styling changes
   - Use only for third-party widgets without semantic HTML

---

### 3.2 Page Object Model (POM)

All E2E tests use POM pattern for maintainability:

```python
# pages/checkout_page.py
from playwright.sync_api import Page

class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.get_by_label("Email")
        self.submit_button = page.get_by_role("button", name="Place Order")
    
    def fill_email(self, email: str):
        self.email_input.fill(email)
    
    def submit_order(self):
        self.submit_button.click()
        self.page.wait_for_url("**/order-confirmation")

# tests/test_checkout.py
from pages.checkout_page import CheckoutPage

def test_checkout_happy_path(page):
    checkout = CheckoutPage(page)
    checkout.fill_email("user@example.com")
    checkout.submit_order()
    assert "Order #" in page.text_content("h1")
```

**Benefits:**
- Changes to UI only require updating page objects, not all tests
- Reusable methods reduce duplication
- Clear separation: page objects = "how", tests = "what"

---

### 3.3 Auto-Waiting vs Explicit Waits

**Prefer Playwright's auto-waiting** (built-in):
```python
# ✅ GOOD: Auto-waits for element to be visible, enabled, stable
page.get_by_role("button", name="Submit").click()

# ❌ BAD: Manual sleep (fragile, slow)
import time
time.sleep(2)
page.get_by_role("button", name="Submit").click()
```

**Use explicit waits only when necessary:**
```python
# ✅ GOOD: Wait for network event
with page.expect_response("**/api/users"):
    page.get_by_role("button", name="Load More").click()

# ✅ GOOD: Wait for specific condition
page.wait_for_function("() => document.querySelectorAll('.item').length > 10")
```

**Never use:**
- `time.sleep()` → replaced by `page.wait_for_timeout()` (last resort)
- `wait_for_selector()` → use role-based locators instead

---

## 4. Visual Regression Testing

### 4.1 Scope

Visual regression tests capture UI appearance, not functionality:

| Page Type | Coverage | Tool | Frequency |
|-----------|----------|------|-----------|
| **Public pages** | 100% (all routes) | Percy/Chromatic | Every PR |
| **Authenticated pages** | Key workflows only | Playwright screenshots | Every PR |
| **Admin pages** | Not covered | Manual QA | Release testing |

**What triggers visual diffs:**
- CSS changes (intentional or accidental)
- Component library updates
- Browser rendering changes

---

### 4.2 Baseline Management

Per [visual regression best practices](https://www.browserstack.com/percy/visual-regression-testing):

1. **Capture baselines in CI, not locally**
   - Local: Different fonts, screen resolution, OS rendering
   - CI: Consistent Docker environment

2. **Review baselines before approving**
   - Auto-approve only for expected changes (new feature)
   - Reject if unintended CSS leaks (e.g., navbar broken)

3. **Update baselines after design changes**
   - Run `playwright test --update-snapshots`
   - Commit updated screenshots to Git

**Playwright Configuration:**
```python
# playwright.config.py
expect.set_options(
    threshold=0.2,  # Allow 20% pixel difference (font rendering variance)
    max_diff_pixels=100  # Ignore minor anti-aliasing differences
)
```

---

### 4.3 Visual Test Example

```python
# tests/visual/test_homepage.py
import pytest
from playwright.sync_api import Page

@pytest.mark.visual
def test_homepage_appearance(page: Page):
    page.goto("https://example.com")
    
    # Wait for dynamic content to load
    page.wait_for_selector("[data-testid='hero-section']")
    
    # Capture full-page screenshot
    expect(page).to_have_screenshot("homepage-desktop.png", full_page=True)

@pytest.mark.visual
def test_homepage_mobile(page: Page):
    page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE
    page.goto("https://example.com")
    expect(page).to_have_screenshot("homepage-mobile.png")
```

**Run visual tests separately:**
```bash
# Skip visual tests in fast CI pipeline
pytest -m "not visual"

# Run visual tests nightly or on-demand
pytest -m visual --update-snapshots
```

---

## 5. Test Data Strategy

### 5.1 Fixtures vs Factories

Per [test data best practices](https://www.testim.io/blog/test-data-is-critical-how-to-best-generate-manage-and-use-it/):

| Approach | Use Case | Example |
|----------|----------|---------|
| **Fixtures** | Shared reference data (countries, currencies) | `pytest.fixture` with static JSON |
| **Factories** | Test-specific records (users, orders) | `factory_boy` or custom builders |
| **Realistic Data** | E2E tests requiring domain fidelity | Anonymized production data subset |

**When to use each:**

**Fixtures (shared, static):**
```python
# conftest.py
@pytest.fixture(scope="session")
def country_codes():
    return ["US", "CA", "GB", "FR", "DE"]

def test_country_dropdown(page, country_codes):
    dropdown = page.get_by_label("Country")
    for code in country_codes:
        assert dropdown.locator(f"option[value='{code}']").is_visible()
```

**Factories (dynamic, unique):**
```python
# factories.py
import factory
from models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Faker("user_name")
    is_active = True

# test_user.py
def test_user_registration(page):
    user = UserFactory.build()  # Generate unique user data
    page.goto("/register")
    page.get_by_label("Email").fill(user.email)
    page.get_by_label("Username").fill(user.username)
    # ...
```

**Realistic Data (E2E only):**
- **Source:** Anonymized production database snapshot
- **Storage:** SQL dump or JSON fixtures in `tests/fixtures/realistic/`
- **Refresh:** Quarterly (ensure GDPR compliance: no real PII)

---

### 5.2 Data Isolation

Each test must clean up after itself:

**❌ BAD (state leaks between tests):**
```python
def test_create_user():
    create_user("test@example.com")  # Persists in DB

def test_login():
    login("test@example.com")  # Assumes user exists (flaky!)
```

**✅ GOOD (isolated):**
```python
@pytest.fixture
def test_user(db_session):
    user = UserFactory.create()
    yield user
    db_session.delete(user)  # Cleanup
    db_session.commit()

def test_create_user(test_user):
    # Use factory-created user
    assert test_user.is_active

def test_login(test_user):
    # Each test gets its own user
    login(test_user.email)
```

**Strategies:**
- **Unit tests:** In-memory SQLite (fast, no cleanup needed)
- **Integration tests:** Transaction rollback after each test
- **E2E tests:** Dedicated test database, reset between runs

---

### 5.3 Sensitive Data Handling

**NEVER:**
- ❌ Commit real PII to Git
- ❌ Use production credentials in tests
- ❌ Hardcode API keys in test code

**ALWAYS:**
- ✅ Use `faker` library for realistic but fake data
- ✅ Store secrets in `.env.test` (gitignored)
- ✅ Mask sensitive data in logs/screenshots

```python
from faker import Faker
fake = Faker()

def test_checkout(page):
    page.get_by_label("Credit Card").fill(fake.credit_card_number())  # Fake but valid format
    page.get_by_label("CVV").fill(fake.credit_card_security_code())
```

---

## 6. CI/CD Integration

### 6.1 Test Execution Strategy

| Environment | When | Tests Run | Timeout | Parallelization |
|-------------|------|-----------|---------|-----------------|
| **Pre-commit** | Before commit | Fast unit tests only | 30s | Local (1 worker) |
| **PR Pipeline** | On PR open/update | Unit + integration | 5 min | 4 workers |
| **Main Branch** | After merge | All tests + E2E | 15 min | 8 workers |
| **Nightly** | 2 AM daily | All + visual regression | 30 min | 16 workers |

**Playwright Parallelization:**
```bash
# Run tests across 4 workers
pytest --workers 4 tests/e2e/

# Run specific browser (default: Chromium)
pytest --browser firefox tests/e2e/
```

---

### 6.2 Flaky Test Handling

Per [Playwright guidance](https://playwright.dev/docs/test-retries):

**Auto-retry flaky tests (max 2 retries):**
```python
# pytest.ini
[pytest]
playwright_retries = 2
```

**Quarantine persistently flaky tests:**
```python
@pytest.mark.skip(reason="Flaky: times out on CI (issue #123)")
def test_slow_api():
    # ...
```

**Root cause analysis:**
- Check for race conditions (missing `wait_for_*` calls)
- Review network stability (add retries for external APIs)
- Validate test data (ensure fixtures don't conflict)

---

## 7. Metrics & Reporting

### 7.1 Test Quality Metrics

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| **Coverage** | ≥ 80% | 85% | ↑ |
| **Flakiness Rate** | < 2% | 1.5% | → |
| **Test Duration** | ≤ 15 min | 12 min | ↓ |
| **E2E Pass Rate** | ≥ 95% | 97% | ↑ |

**Tracked via:**
- Coverage: `pytest-cov` report in CI
- Flakiness: Retry count per test (logged)
- Duration: CI pipeline metrics
- Pass rate: GitHub Actions badge

---

### 7.2 Test Reporting

**Playwright HTML Report:**
```bash
pytest --html=report.html --self-contained-html
```

**Artifacts uploaded to CI:**
- Screenshots for failed tests
- Video recordings for E2E failures
- Trace files for debugging (Playwright Inspector)

**Example:**
```python
# pytest.ini
[pytest]
playwright_artifacts_dir = test-results/
playwright_video = retain-on-failure
playwright_screenshot = only-on-failure
```

---

## 8. Test Maintenance

### 8.1 Quarterly Reviews

**Actions:**
- Remove obsolete tests (for deprecated features)
- Update baselines for visual regression tests
- Review flaky tests (fix or quarantine)
- Update test data factories (align with production schema)

---

### 8.2 Test Documentation

**Required for all E2E tests:**
- **Purpose:** What user journey does this test validate?
- **Preconditions:** Required test data, feature flags
- **Expected outcome:** Success criteria

**Example:**
```python
def test_checkout_with_discount_code(page):
    """
    Test ID: CHECKOUT-003
    Purpose: Validate that discount codes reduce total price at checkout
    
    Preconditions:
    - User is logged in
    - Cart contains 2 items ($50 total)
    - Discount code "SAVE10" is active (10% off)
    
    Expected Outcome:
    - Total price is $45 (10% discount applied)
    - Order confirmation shows discount line item
    """
    # Test implementation...
```

---

## Appendix: Tool Configuration

### A.1 Playwright Config

```python
# playwright.config.py
from playwright.sync_api import sync_playwright

config = {
    "base_url": "http://localhost:8000",
    "timeout": 30000,  # 30s per action
    "expect_timeout": 5000,  # 5s for assertions
    "browsers": ["chromium", "firefox", "webkit"],
    "workers": 4,
    "retries": 2,
    "video": "retain-on-failure",
    "screenshot": "only-on-failure",
    "trace": "retain-on-failure"
}
```

### A.2 pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (DB, external APIs)
    e2e: End-to-end tests (Playwright)
    visual: Visual regression tests
    slow: Tests taking > 5s
addopts =
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```
```

**Usage in BMAD:**
- **Phase 0:** Define test strategy before implementation starts
- **Phase 3 (Architecture):** Reference test strategy in ADRs ("per TEST_STRATEGY.md, use POM pattern")
- **Phase 4 (Implementation):** `@test` agent consumes TEST_STRATEGY.md to generate Playwright tests
- **Validation gate:** Check that E2E tests follow strategy (role locators, no sleep, etc.)

---

## 3. BMAD Integration Strategy

### 3.1 Where These Artifacts Fit

**Recommended:** Add **Phase 0: Technical Governance** before Analysis phase.

```
┌──────────────────────────────────────────────────────────┐
│  Phase 0: Technical Governance (ONE-TIME SETUP)          │
│  Agent: @architect or @tech-lead                         │
│  Outputs:                                                │
│  - TECHNICAL_CONSTITUTION.md                             │
│  - NFR_CATALOG.md (initial draft)                        │
│  - TEST_STRATEGY.md                                      │
│  Gate: Constitution approved by tech lead + PM           │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│  Phase 1: Analysis                                       │
│  Agent: @bmad-analyst                                    │
│  Reads: TECHNICAL_CONSTITUTION (constraints)             │
│  Outputs: Problem statement, stakeholder map             │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│  Phase 2: Product Management                             │
│  Agent: @bmad-pm                                         │
│  Reads: NFR_CATALOG (reference NFR IDs in stories)      │
│  Outputs: PRD, user stories                              │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│  Phase 3: Architecture Design                            │
│  Agent: @bmad-architect                                  │
│  Reads: TECHNICAL_CONSTITUTION + NFR_CATALOG             │
│  Validates: ADRs don't violate constitution              │
│  Outputs: ADRs citing NFRs, system design                │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│  Phase 4: Implementation                                 │
│  Agent: @test, @make (PRIES workflow)                    │
│  Reads: TEST_STRATEGY.md (patterns), NFR_CATALOG (tests) │
│  Outputs: Tests validating NFRs, implementation          │
└──────────────────────────────────────────────────────────┘
```

**Why Phase 0?**
- **Not discoverable:** Tech preferences and NFRs are *constraints on the solution space*, not outputs of analysis
- **Persistent:** Constitution rarely changes; creating it per-feature is wasteful
- **Authoritative:** One source of truth for all BMAD phases

**Alternative (lighter-weight):** Augment Phase 3 (Architecture) with constitution/NFR sections in ADRs. **Not recommended** — leads to duplication and inconsistent enforcement.

---

### 3.2 Who Creates These Artifacts

| Artifact | Primary Author | Reviewers | Cadence |
|----------|----------------|-----------|---------|
| **TECHNICAL_CONSTITUTION** | Tech Lead or Architect | Senior Engineers, PM | Once per project + quarterly reviews |
| **NFR_CATALOG** | Architect + PM | Security, SRE, Legal | Once per project, updated per major feature |
| **TEST_STRATEGY** | QA Lead or Senior Engineer | Tech Lead, DevOps | Once per project, updated as tooling evolves |

**Agent Assignment:**
- Use **@bmad-architect** (or dedicated **@tech-lead** agent) for Phase 0
- Provide skill: `bmad-phase0-constitution-authoring.md`

---

### 3.3 Validation Gates

Phase 0 outputs must pass validation before Phase 1 starts:

| Artifact | Validation Check | Tool/Method |
|----------|------------------|-------------|
| **TECHNICAL_CONSTITUTION** | - All sections filled<br>- Tech stack choices justified<br>- Security baseline includes auth + encryption | Schema validation (JSON schema or checklist) |
| **NFR_CATALOG** | - All NFRs use EARS notation<br>- P0 NFRs have test strategies<br>- Thresholds are measurable | EARS syntax linter + NFR schema |
| **TEST_STRATEGY** | - Test pyramid ratios defined<br>- E2E scope lists critical journeys<br>- Locator strategy specified | Checklist review |

**Automated validation:**
```python
# scripts/validate_phase0.py
import json
from pathlib import Path

def validate_constitution(path: Path):
    content = path.read_text()
    required_sections = [
        "Technology Preferences",
        "Solution Approach Constraints",
        "Security Baseline"
    ]
    for section in required_sections:
        assert f"## {section}" in content, f"Missing section: {section}"

def validate_nfr_catalog(path: Path):
    content = path.read_text()
    # Check all NFRs use EARS keywords: "shall", "when", "while", "where"
    nfr_blocks = content.split("### NFR-")
    for block in nfr_blocks[1:]:  # Skip header
        assert any(kw in block.lower() for kw in ["shall", "when", "while", "where"]), \
            f"NFR missing EARS notation: {block[:50]}"

if __name__ == "__main__":
    validate_constitution(Path("TECHNICAL_CONSTITUTION.md"))
    validate_nfr_catalog(Path("NFR_CATALOG.md"))
    print("✅ Phase 0 artifacts validated")
```

---

### 3.4 Constitution Enforcement in Later Phases

**Phase 2 (PM):**
- **Validation:** User stories reference NFR IDs for acceptance criteria
- **Example:** "Story-123 acceptance: API latency must meet NFR-PERF-001"

**Phase 3 (Architecture):**
- **Validation:** ADRs cite TECHNICAL_CONSTITUTION when making tech choices
- **Example:** "ADR-005 chooses Alpine.js per TECHNICAL_CONSTITUTION § 1.2 (Frontend Stack)"
- **Enforcement:** Linter flags ADRs proposing prohibited tech (e.g., React)

**Phase 4 (Implementation):**
- **Validation:** Code review checklist includes "Does this follow TECHNICAL_CONSTITUTION?"
- **Test generation:** `@test` agent generates NFR validation tests from NFR_CATALOG

---

## 4. PRIES Workflow Integration

The [PRIES workflow](../harness-tooling/docs/reference-workflows-ppries/) (PM → Make → Test → Review → Simplify) maps cleanly to BMAD Phase 4 (Implementation):

### 4.1 How PRIES Agents Consume Phase 0 Artifacts

| PRIES Agent | Phase 0 Artifact | How It's Used |
|-------------|------------------|---------------|
| **@pm** | NFR_CATALOG.md | References NFR IDs in Linear tickets ("must satisfy NFR-PERF-001") |
| **@test** | TEST_STRATEGY.md<br>NFR_CATALOG.md | - Generates Playwright tests following POM pattern<br>- Creates NFR validation tests (load tests, accessibility scans)<br>- Uses fixture/factory strategies defined in TEST_STRATEGY |
| **@make** | TECHNICAL_CONSTITUTION.md | - Validates tech choices (uses `uv`, not `pip`)<br>- Follows solution approach (server-driven UI)<br>- Applies code quality standards (naming, docstrings) |
| **@check** | TECHNICAL_CONSTITUTION.md<br>NFR_CATALOG.md | - Validates ADRs don't violate constitution<br>- Ensures NFRs are satisfied in implementation<br>- Flags deviations for human review |
| **@simplify** | TECHNICAL_CONSTITUTION.md | Flags over-engineering relative to constitution's KISS principles |

### 4.2 Example: @test Agent Using TEST_STRATEGY.md

**Scenario:** Implement checkout flow for e-commerce site.

**Input to @test:**
- Task: "Write E2E test for checkout happy path"
- Context files: `TEST_STRATEGY.md`, `NFR_CATALOG.md`

**@test agent workflow:**

1. **Read TEST_STRATEGY.md:**
   - Test pyramid: This is a critical user journey → qualifies for E2E test
   - Locator strategy: Use role locators (`get_by_role`)
   - Page Object Model: Create `CheckoutPage` class
   - Data strategy: Use `UserFactory` for test user

2. **Read NFR_CATALOG.md:**
   - NFR-PERF-001: API response time < 200ms → not directly testable in E2E, but flag slow pages
   - NFR-USE-001: WCAG 2.1 AA compliance → run axe-core accessibility scan

3. **Generate test:**

```python
# tests/e2e/pages/checkout_page.py (POM per TEST_STRATEGY)
from playwright.sync_api import Page

class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.get_by_label("Email")  # Role locator
        self.submit_button = page.get_by_role("button", name="Place Order")
    
    def fill_email(self, email: str):
        self.email_input.fill(email)
    
    def submit_order(self):
        self.submit_button.click()
        self.page.wait_for_url("**/order-confirmation")  # Auto-wait

# tests/e2e/test_checkout.py
import pytest
from pages.checkout_page import CheckoutPage
from factories import UserFactory  # Data strategy from TEST_STRATEGY
from axe_playwright_python.sync_playwright import Axe  # NFR-USE-001

def test_checkout_happy_path(page):
    """
    Test ID: CHECKOUT-001
    Purpose: Validate user can complete checkout flow
    NFRs: NFR-USE-001 (accessibility)
    """
    # Setup test data (factory per TEST_STRATEGY § 5.1)
    user = UserFactory.build()
    
    # Navigate to checkout
    checkout = CheckoutPage(page)
    checkout.fill_email(user.email)
    checkout.submit_order()
    
    # Verify success
    assert "Order #" in page.text_content("h1")
    
    # NFR-USE-001: WCAG 2.1 AA compliance
    axe = Axe()
    results = axe.run(page)
    assert len(results.violations) == 0, f"Accessibility violations: {results.violations}"
```

**Key points:**
- ✅ Uses role locators (per TEST_STRATEGY § 3.1)
- ✅ Implements POM pattern (per TEST_STRATEGY § 3.2)
- ✅ Uses factory for test data (per TEST_STRATEGY § 5.1)
- ✅ Validates NFR-USE-001 accessibility (from NFR_CATALOG)
- ✅ Auto-waiting, no `time.sleep()` (per TEST_STRATEGY § 3.3)

---

### 4.3 Example: @check Agent Validating Constitution Compliance

**Scenario:** Review ADR proposing to use React instead of Alpine.js.

**Input to @check:**
- ADR-042: "Use React for dynamic product catalog UI"
- Context files: `TECHNICAL_CONSTITUTION.md`

**@check agent workflow:**

1. **Read TECHNICAL_CONSTITUTION.md § 1.2 (Frontend Stack):**
   - "Reactive UI: Alpine.js 3.x (preferred) | React (prohibited without approval)"

2. **Flag violation:**
   ```
   ⚠️ Constitution Violation Detected
   
   ADR-042 proposes React, but TECHNICAL_CONSTITUTION.md § 1.2 prohibits React 
   without architect approval.
   
   Rationale from constitution:
   - Alpine.js preferred for progressive enhancement, no build step, <15kb bundle
   - React requires build tooling, increases complexity
   
   Recommendation:
   - Option A: Use Alpine.js with `x-for` directive for dynamic lists
   - Option B: Seek architect exception with justification
   
   If Option B: ADR must include:
   1. Why Alpine.js is insufficient (technical limitation)
   2. Build tooling impact assessment
   3. Bundle size increase (target: <100kb total)
   ```

3. **Escalate to human:**
   - @check does NOT auto-reject (human has final say)
   - Provides rationale + alternatives for informed decision

---

### 4.4 PRIES Phase Integration Matrix

| PRIES Phase | BMAD Phase | Phase 0 Artifacts Used | Validation |
|-------------|------------|------------------------|------------|
| **PM Fetch** | Phase 2 output | NFR_CATALOG (reference NFR IDs in tickets) | Linear ticket has NFR references |
| **Test Write** | Phase 4a | TEST_STRATEGY, NFR_CATALOG | Tests follow strategy, validate NFRs |
| **Make** | Phase 4b | TECHNICAL_CONSTITUTION | Code follows tech stack, patterns |
| **Check** | Phase 4c | All Phase 0 artifacts | Constitution compliance, NFRs met |
| **Simplify** | Phase 4d | TECHNICAL_CONSTITUTION | No over-engineering per KISS |

---

## 5. STA2E VTT Example

### 5.1 Project Context

**STA2E VTT Lite:** Virtual Tabletop for Star Trek Adventures 2e RPG
- **Tech Stack:** FastAPI, HTMX, Alpine.js, PostgreSQL, `uv` dependency management
- **Architecture:** Server-driven UI, minimal client state, WebSocket for multiplayer sync
- **NFRs:** Multiplayer sync latency < 200ms, WCAG 2.1 AA accessibility, mobile-responsive
- **E2E Requirements:** Bridge station workflows, dice rolling, character sheet CRUD, state machine coverage

---

### 5.2 Mock TECHNICAL_CONSTITUTION.md

```markdown
# Technical Constitution — STA2E VTT Lite

**Project:** Star Trek Adventures 2e Virtual Tabletop  
**Version:** 1.0  
**Last Updated:** 2026-04-26  
**Governance:** Requires tech lead approval for amendments

---

## 1. Technology Preferences

### 1.1 Backend Stack
- **Language:** Python 3.12+
- **Web Framework:** FastAPI 0.100+ (async-native, automatic OpenAPI docs)
- **Dependency Management:** `uv` (REQUIRED) — 10-100x faster than pip
- **Database:** PostgreSQL 15+ with asyncpg driver
- **ORM:** SQLAlchemy 2.x with async support
- **WebSocket:** FastAPI native WebSocket support (no external library)

### 1.2 Frontend Stack
- **HTML Rendering:** Server-side Jinja2 templates + HTMX
- **Reactive UI:** Alpine.js 3.x for client-side interactivity
- **CSS Framework:** Tailwind CSS 3.4+ (utility-first)
- **Build Tool:** None (CDN for Alpine/HTMX) — keep deployment simple

**Rationale:**
- **Server-driven UI:** Reduces client complexity, easier to test, better SEO
- **HTMX:** Replaces React for dynamic updates without JavaScript framework overhead
- **Alpine.js:** 15kb bundle for dropdowns, modals, form validation — no webpack/vite needed

### 1.3 Testing Stack
- **Unit:** pytest 8.x with pytest-asyncio
- **E2E:** Playwright (Python) for browser automation
- **Mocking:** pytest-mock (wraps unittest.mock)
- **Load Testing:** Locust for multiplayer sync performance

---

## 2. Solution Approach Constraints

### 2.1 Server-Driven UI (Core Principle)
- **MUST:** All application state lives on the server
- **MUST:** Client state limited to: form inputs, dropdown open/closed, modal visibility
- **MUST NOT:** Implement client-side routers, Redux/Zustand stores, or SPAs
- **MUST NOT:** Use React, Vue, or Angular

**Why:** VTT requires authoritative server for multiplayer consistency. Client state = desyncs.

### 2.2 Multiplayer Sync
- **MUST:** Use WebSocket for real-time updates (dice rolls, character position)
- **MUST:** Implement optimistic UI updates with rollback on server rejection
- **MUST:** Broadcast state changes to all connected clients within 200ms (NFR-PERF-002)
- **MUST NOT:** Use polling for real-time features (inefficient, high latency)

### 2.3 Data Persistence
- **MUST:** Use PostgreSQL JSONB columns for flexible game state (character sheets, bridge stations)
- **MUST:** Implement audit log for all state changes (who changed what, when)
- **MUST NOT:** Store game state in Redis/Memcached (durability risk)

---

## 3. Code Quality Standards

### 3.1 Python Style
- **Formatter:** `ruff format` (replaces Black)
- **Linter:** `ruff check` with rules: E, F, I, N, UP, RUF
- **Type Checker:** `mypy` in strict mode (no `Any` types without justification)

### 3.2 Naming Conventions
- **API Routes:** `/api/v1/characters`, `/api/v1/dice-rolls` (kebab-case)
- **Database Tables:** `characters`, `bridge_stations`, `audit_logs` (snake_case)
- **Python Classes:** `CharacterRepository`, `DiceRoller` (PascalCase)
- **Functions:** `get_character_by_id`, `roll_dice` (snake_case, verb-noun)

---

## 4. Security Baseline

### 4.1 Authentication
- **MUST:** OAuth 2.0 with Auth0 (no custom auth)
- **MUST:** JWT access tokens (15 min expiry), refresh tokens (7 day expiry)
- **MUST NOT:** Store passwords (Auth0 handles this)

### 4.2 Authorization
- **MUST:** Implement role-based access control (Game Master, Player)
- **Game Masters:** Full CRUD on all game state
- **Players:** Read-only on shared state, CRUD on own characters

### 4.3 Data Protection
- **MUST:** Sanitize all user inputs (prevent XSS in character names, notes)
- **MUST:** Use parameterized queries (SQLAlchemy prevents SQL injection)
- **MUST NOT:** Log JWT tokens, passwords, or PII

---

## 5. Amendment Process

**Minor:** Updating Python version (3.12 → 3.13) — 1 tech lead approval  
**Major:** Switching from PostgreSQL to MongoDB — requires ADR + PM sign-off
```

---

### 5.3 Mock NFR_CATALOG.md

```markdown
# Non-Functional Requirements Catalog — STA2E VTT Lite

---

## 1. Performance Efficiency

### NFR-PERF-001: API Response Time
**Requirement (EARS):**  
> When a user requests data via REST API, the system shall return a response within 200ms (p95).

**Acceptance Criteria:**
- p50 ≤ 100ms, p95 ≤ 200ms, p99 ≤ 500ms
- Test: Locust load test with 100 concurrent users

**Priority:** P0

---

### NFR-PERF-002: WebSocket Latency
**Requirement (EARS):**  
> When a Game Master rolls dice, the system shall broadcast results to all players within 200ms.

**Acceptance Criteria:**
- End-to-end latency (GM roll → player sees result) ≤ 200ms (p95)
- Test: Playwright E2E with artificial network latency

**Priority:** P0 (core feature)

---

## 2. Reliability

### NFR-REL-001: Session Persistence
**Requirement (EARS):**  
> When a user's WebSocket connection drops, the system shall allow reconnection within 30s without data loss.

**Acceptance Criteria:**
- Session state persisted in PostgreSQL, not memory
- Reconnect restores game state (no "where was I?" confusion)

**Test:** E2E test simulating network interruption

**Priority:** P1

---

## 3. Usability

### NFR-USE-001: Accessibility
**Requirement (EARS):**  
> All public-facing pages shall conform to WCAG 2.1 Level AA.

**Acceptance Criteria:**
- axe-core automated tests pass (0 violations)
- Screen reader compatible (tested with NVDA)
- Keyboard navigation: All buttons/links accessible via Tab

**Test:** Playwright + axe-playwright-python

**Priority:** P0 (legal requirement)

---

### NFR-USE-002: Mobile Responsiveness
**Requirement (EARS):**  
> The system shall render correctly on viewports from 375px (iPhone SE) to 2560px (4K).

**Acceptance Criteria:**
- No horizontal scrolling
- Touch targets ≥ 44x44px
- Visual regression tests pass (375px, 768px, 1920px)

**Test:** Playwright visual snapshots

**Priority:** P1

---

## 4. Security

### NFR-SEC-001: Authentication
**Requirement (EARS):**  
> When a user attempts to access a protected resource, the system shall require valid JWT token.

**Acceptance Criteria:**
- Expired tokens rejected (401 Unauthorized)
- Missing tokens rejected (401 Unauthorized)
- Invalid signatures rejected (401 Unauthorized)

**Test:** pytest integration tests

**Priority:** P0

---

## 5. Maintainability

### NFR-MAIN-001: Test Coverage
**Requirement:**  
> All new code shall maintain ≥ 80% line coverage.

**Acceptance Criteria:**
- Unit tests: 90%+ coverage for business logic
- E2E tests: Cover critical user journeys (see TEST_STRATEGY.md)

**Test:** pytest-cov report in CI

**Priority:** P1
```

---

### 5.4 Mock TEST_STRATEGY.md (Excerpts)

```markdown
# E2E Test Strategy — STA2E VTT Lite

---

## 2. E2E Test Scope

### 2.1 Critical User Journeys

| Journey ID | Description | Test Count | Priority |
|------------|-------------|------------|----------|
| **AUTH-001** | OAuth login → landing page | 2 | P0 |
| **CHAR-001** | Create/edit/delete character | 4 | P0 |
| **DICE-001** | Game Master rolls dice → players see result | 3 | P0 |
| **BRIDGE-001** | Navigate bridge stations (Helm, Tactical, Comms) | 6 | P0 |
| **SYNC-001** | Multiplayer: GM updates state → players auto-refresh | 5 | P0 |

**Selection Rationale:**
- **DICE-001:** Core gameplay feature; failure = unplayable
- **BRIDGE-001:** Unique to Star Trek RPG; no off-the-shelf components
- **SYNC-001:** Validates NFR-PERF-002 (WebSocket latency)

---

## 3. Playwright Patterns

### 3.1 Locator Strategy
```python
# ✅ GOOD: Role-based (preferred)
page.get_by_role("button", name="Roll Dice")
page.get_by_label("Character Name")

# ✅ GOOD: Test IDs for dynamic content
page.get_by_test_id("bridge-station-helm")

# ❌ BAD: CSS selectors (brittle)
page.locator(".btn-primary")  # Breaks if Tailwind class changes
```

### 3.2 WebSocket Testing
```python
# Wait for WebSocket message
async def test_dice_roll_broadcast(page):
    # GM rolls dice
    await page.get_by_role("button", name="Roll 2d20").click()
    
    # Wait for WebSocket broadcast
    await page.wait_for_function(
        "() => document.querySelector('[data-testid=\"dice-result\"]').textContent.includes('Result:')"
    )
    
    # Verify result displayed
    result = await page.get_by_test_id("dice-result").text_content()
    assert "Result:" in result
```

---

## 5. Test Data Strategy

### 5.1 Factories
```python
# factories.py
import factory
from models import Character

class CharacterFactory(factory.Factory):
    class Meta:
        model = Character
    
    name = factory.Sequence(lambda n: f"Lt. Commander Data-{n}")
    role = "Science Officer"
    species = "Android"
    attributes = {"control": 12, "daring": 8, "fitness": 11}

# test_character_crud.py
def test_create_character(page):
    char = CharacterFactory.build()
    page.get_by_label("Character Name").fill(char.name)
    # ...
```

### 5.2 Realistic Data (Bridge Stations)
```python
# Fixture for bridge station presets (static, shared)
@pytest.fixture(scope="session")
def bridge_stations():
    return [
        {"id": "helm", "name": "Helm", "icon": "🚀"},
        {"id": "tactical", "name": "Tactical", "icon": "🎯"},
        {"id": "comms", "name": "Communications", "icon": "📡"},
        {"id": "engineering", "name": "Engineering", "icon": "🔧"}
    ]
```
```

---

### 5.5 How STA2E VTT Benefits from Phase 0 Artifacts

**Before Phase 0 (pain points):**
- ❌ Developers unsure whether to use React or Alpine.js → constitution says Alpine.js
- ❌ PM writes vague NFR: "dice rolls should be fast" → NFR-PERF-002 specifies <200ms
- ❌ E2E tests use CSS selectors → brittle → TEST_STRATEGY mandates role locators
- ❌ No test coverage for multiplayer sync → TEST_STRATEGY identifies SYNC-001 as P0

**After Phase 0 (benefits):**
- ✅ @bmad-analyst reads TECHNICAL_CONSTITUTION, never proposes React
- ✅ @bmad-pm writes user story: "Acceptance: must meet NFR-PERF-002"
- ✅ @test agent generates Playwright tests with role locators (per TEST_STRATEGY)
- ✅ @check agent validates that ADRs cite NFR-PERF-002 when designing WebSocket architecture
- ✅ @make agent uses `uv` (per constitution), not `pip`

**Result:** Faster development, consistent code quality, fewer rework cycles.

---

## 6. Implementation Roadmap

### Phase 1: Template Creation (Week 1)
- [ ] Create canonical templates for TECHNICAL_CONSTITUTION, NFR_CATALOG, TEST_STRATEGY
- [ ] Define JSON schemas for validation
- [ ] Document EARS notation guidelines for NFR authoring

### Phase 2: Pilot on STA2E VTT (Week 2-3)
- [ ] Author Phase 0 artifacts for STA2E VTT project
- [ ] Run through BMAD workflow manually (no automation)
- [ ] Measure:
  - Time to create artifacts (target: <4 hours)
  - NFR coverage (target: 100% of P0 requirements)
  - Constitution violations caught in review (expect 2-3 per project)

### Phase 3: Agent Skill Development (Week 4-5)
- [ ] Create `bmad-phase0-constitution-authoring.md` skill
- [ ] Create `bmad-phase0-nfr-catalog-authoring.md` skill
- [ ] Create `bmad-phase0-test-strategy-authoring.md` skill
- [ ] Train agents to reference Phase 0 artifacts in later phases

### Phase 4: Validation Automation (Week 6)
- [ ] Implement `validate_phase0.py` script (Python)
- [ ] Add pre-commit hook for constitution syntax checking
- [ ] Create EARS notation linter for NFR_CATALOG
- [ ] Integrate with CI (GitHub Actions)

### Phase 5: PRIES Integration (Week 7-8)
- [ ] Update `@test` agent to consume TEST_STRATEGY.md
- [ ] Update `@check` agent to enforce TECHNICAL_CONSTITUTION
- [ ] Update `@make` agent to validate tech stack choices
- [ ] Document PRIES workflow changes in reference docs

### Phase 6: Documentation & Training (Week 9)
- [ ] Write "How to Author a Technical Constitution" guide
- [ ] Record demo video: BMAD with Phase 0 artifacts
- [ ] Create checklist for Phase 0 review
- [ ] Onboard team to new workflow

### Phase 7: Rollout (Week 10+)
- [ ] Mandate Phase 0 for all new BMAD projects
- [ ] Conduct retrospective after 3 projects
- [ ] Refine templates based on feedback
- [ ] Measure impact: rework cycles, constitution violations, NFR test coverage

---

## 7. References

### Research Sources

**Governance Frameworks:**
- [GitHub spec-kit constitution](https://github.com/github/spec-kit) — Persistent governance for AI-driven development
- [spec-kit constitution command](https://deepwiki.com/github/spec-kit/5.1-speckit.constitution) — How constitutions work in practice
- [Spec-Driven Development with Spec Kit](https://linuxera.org/spec-driven-development-with-spec-kit/) — Structured development guide

**NFR Standards:**
- [ISO/IEC 25010:2023 Software Quality Model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) — Industry standard for NFR classification
- [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/) — Templates for testable requirements
- [EARS Tutorial](https://medium.com/paramtech/ears-the-easy-approach-to-requirements-syntax-b09597aae31d) — Practical examples

**Architecture Decision Records:**
- [MADR (Markdown ADR) Template](https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html) — Lightweight ADR format
- [Y-Statements for ADRs](https://medium.com/olzzio/y-statements-10eb07b5a177) — Capturing consequences
- [Microsoft Azure ADR Guide](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record) — Enterprise best practices

**E2E Testing:**
- [Playwright Best Practices (2026)](https://www.browserstack.com/guide/playwright-best-practices) — Locator strategies, POM, auto-waiting
- [Test Pyramid Strategy (2025)](https://www.devzery.com/post/software-testing-pyramid-guide-2025) — 70/20/10 ratio guidance
- [Visual Regression Testing](https://www.browserstack.com/percy/visual-regression-testing) — Baseline management
- [Test Data Strategies](https://www.testim.io/blog/test-data-is-critical-how-to-best-generate-manage-and-use-it/) — Fixtures vs factories

**RFC & Design Documents:**
- [Companies Using RFCs](https://blog.pragmaticengineer.com/rfcs-and-design-docs/) — Airbnb, Amazon, Stripe patterns
- [RFC Templates](https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design) — Industry examples

**Technical Constraints:**
- [Architecture Constraints Documentation](https://roboy-sw-documentation-template.readthedocs.io/en/latest/02_architecture_constraints.html) — What to document
- [Handling Architecture Constraints](https://subscription.packtpub.com/book/web-development/9781838645649/2/ch02lvl1sec34/handling-various-architecture-constraints) — Practical strategies

### Internal Documentation

- [BMAD Integration Strategy](../harness-tooling/docs/integration-bmad-method.md) — harness-workflow-runtime alignment
- [PRIES Workflow Reference](../harness-tooling/docs/reference-workflows-ppries/) — PM → Make → Test → Review → Simplify
- [Harness V1 Master Plan](../harness-tooling/docs/harness-v1-master-plan.md) — Overall delivery scope

---

## Appendix A: Quick Start Checklist

**For New Projects:**

- [ ] 1. Create `TECHNICAL_CONSTITUTION.md` (tech lead + 2 senior engineers)
- [ ] 2. Define NFR_CATALOG.md for P0 requirements (architect + PM + security)
- [ ] 3. Author TEST_STRATEGY.md (QA lead + senior backend engineer)
- [ ] 4. Validate artifacts with `validate_phase0.py`
- [ ] 5. Review & approve (tech lead sign-off required)
- [ ] 6. Commit to `docs/governance/` directory
- [ ] 7. Proceed to BMAD Phase 1 (Analysis)

**For Existing Projects:**

- [ ] 1. Extract implicit tech preferences from codebase → TECHNICAL_CONSTITUTION
- [ ] 2. Document existing NFRs from PRD/ADRs → NFR_CATALOG
- [ ] 3. Formalize current testing practices → TEST_STRATEGY
- [ ] 4. Validate against reality (do tests actually follow strategy?)
- [ ] 5. Iterate to close gaps (update strategy or fix tests)
- [ ] 6. Enforce going forward (all new PRs must comply)

---

## Appendix B: Template Downloads

**Full templates available at:**
- `/templates/TECHNICAL_CONSTITUTION.template.md`
- `/templates/NFR_CATALOG.template.md`
- `/templates/TEST_STRATEGY.template.md`
- `/scripts/validate_phase0.py`

**JSON Schemas:**
- `/schemas/technical-constitution.schema.json`
- `/schemas/nfr-catalog.schema.json`
- `/schemas/test-strategy.schema.json`

---

## Summary of Recommendations

1. **Add Phase 0: Technical Governance** to BMAD workflow
   - Creates: TECHNICAL_CONSTITUTION, NFR_CATALOG, TEST_STRATEGY
   - Runs once per project (before Analysis phase)
   - Provides persistent constraints for all subsequent phases

2. **Use ISO/IEC 25010 + EARS notation** for NFR specification
   - Ensures testable, measurable requirements
   - Integrates with automated test generation

3. **Enforce constitution via validation gates**
   - Linter checks ADRs for violations
   - CI blocks merges violating tech stack rules
   - @check agent flags deviations during code review

4. **Integrate with PRIES workflow**
   - @test consumes TEST_STRATEGY for E2E patterns
   - @make follows TECHNICAL_CONSTITUTION tech stack
   - @check validates NFR compliance

5. **Pilot on STA2E VTT project**
   - Dogfood the workflow on real-world project
   - Measure impact: rework cycles, test coverage, constitution violations
   - Refine templates based on learnings

---

**Next Steps:** Review this proposal → approve/iterate → implement Phase 1 (template creation) → pilot on STA2E VTT
