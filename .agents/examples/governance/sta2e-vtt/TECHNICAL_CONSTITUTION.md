# Technical Constitution — STA2E VTT Lite

**Project:** Star Trek Adventures 2e Virtual Tabletop (Lite)
**Version:** 1.0
**Last Updated:** 2026-04-26
**Governance:** Requires tech lead approval for amendments. Major changes also need PM sign-off.

---

## 1. Technology Preferences

### 1.1 Backend Stack
- **Language:** Python 3.12+
- **Web Framework:** FastAPI 0.110+ (async-native, automatic OpenAPI docs).
- **Dependency Management:** `uv` (REQUIRED). 10-100x faster than pip/poetry.
- **Database:** PostgreSQL 15+ via asyncpg.
- **ORM:** SQLAlchemy 2.x with async support.
- **WebSocket:** FastAPI native WebSocket support.

### 1.2 Frontend Stack
- **HTML Rendering:** Server-side Jinja2 templates + HTMX.
- **Reactive UI:** Alpine.js 3.x.
- **CSS Framework:** Tailwind CSS 3.4+.
- **Build Tool:** None (CDN for HTMX/Alpine). Keep deployment simple.

### 1.3 Testing & Quality
- **Unit Testing:** pytest 8.x with pytest-asyncio.
- **E2E Testing:** Playwright (Python bindings).
- **Mocking:** pytest-mock (wraps unittest.mock).
- **Coverage threshold:** 80%.

### 1.4 Infrastructure
- **Containerisation:** Docker with multi-stage builds.
- **Orchestration:** docker-compose (local + dev). K3s for v2.
- **Secrets Management:** `.env.local` for dev, sandbox shell injects for runtime.

**Rationale for choices:**
- Server-driven UI eliminates client/server desync, which is fatal for multiplayer VTT state.
- HTMX + Alpine keep bundle <30 kB and require no build pipeline, matching the local-first v1 goal.

---

## 2. Solution Approach Constraints

### 2.1 Architecture Patterns
- **MUST:** Server holds the authoritative game state. Client state is limited to form inputs, modal visibility, and dropdown open/closed flags.
  Rationale: VTT requires consistency across multiple connected clients.
- **MUST NOT:** Implement client-side routers, Redux/Zustand stores, or SPA frameworks (React, Vue, Angular).
  Rationale: Conflicts with server-driven UI; introduces build pipeline.

### 2.2 API Design
- **MUST:** REST endpoints under `/api/v1/`, kebab-case paths (`/api/v1/dice-rolls`).
  Rationale: Stable convention used by HTMX templates.
- **MUST:** WebSocket events use a typed envelope `{type, payload, ts}`.
  Rationale: Enables versioned event schemas.

### 2.3 Data Access
- **MUST:** Use Alembic migrations for all schema changes.
  Rationale: Auditable, reversible.
- **MUST:** Game state lives in PostgreSQL JSONB columns plus an audit_logs table.
  Rationale: Flexible schema for character sheets, plus durable audit trail.
- **MUST NOT:** Cache game state in Redis as the system of record.
  Rationale: Durability risk; Redis may be added later as a read-through cache only.

### 2.4 Error Handling
- **MUST:** Use structured JSON logs with a per-request correlation ID.
  Rationale: Required for multiplayer-incident forensics.
- **MUST NOT:** Return raw stack traces to end users.
  Rationale: Security risk.

---

## 3. Code Quality Standards

### 3.1 Naming Conventions
- **Functions:** `snake_case`, verb-noun (`roll_dice`, `get_character_by_id`).
- **Classes:** `PascalCase`, noun (`CharacterRepository`, `DiceRoller`).
- **Constants:** `UPPER_SNAKE_CASE` (`MAX_PLAYERS_PER_SESSION`).
- **Files:** `snake_case.py`.

### 3.2 Documentation Requirements
- **MUST:** Google-style docstrings for all public functions/classes.
  Rationale: Consistent rendering with mkdocs / Sphinx.
- **MUST:** Type hints for every public function (PEP 484).
  Rationale: Required by mypy strict.
- **SHOULD:** ADRs for any change that touches WebSocket event schema or auth flow.

### 3.3 Linting & Formatting
- **Formatter:** `ruff format`.
- **Linter:** `ruff check` with rules `E, F, I, N, UP, RUF`.
- **Type Checker:** `mypy` in strict mode.
- **Pre-commit:** All checks must pass before commit.

---

## 4. Security Baseline

### 4.1 Authentication & Authorization
- **MUST:** OAuth 2.0 + PKCE via Auth0.
  Rationale: No custom auth surface to maintain.
- **MUST:** Access tokens TTL = 15 min, refresh tokens TTL = 7 days.
- **MUST NOT:** Store passwords. Auth0 handles credentials.

### 4.2 Data Protection
- **MUST:** Encrypt PII at rest (AES-256-GCM via PostgreSQL TDE in prod).
- **MUST:** Use TLS 1.3 for all external traffic.
- **MUST NOT:** Log JWT tokens, API keys, or character notes (may contain PII).

### 4.3 Dependency Management
- **MUST:** Pin exact versions via `uv lock`.
- **MUST:** Run `uv pip audit` weekly in CI.
- **MUST NOT:** Use packages with high/critical CVEs in the last 30 days without an exemption.

---

## 5. Amendment Process

**Minor changes** (e.g. patch python version, swap a CDN host): tech lead PR approval.
**Major changes** (e.g. swap PostgreSQL for MongoDB, add React): require an ADR, two architect approvals, and PM sign-off. Must include a migration plan and rollback strategy.

**Effective date:** Changes take effect on merge to `main`.

---

## Appendix: Tooling Reference

| Category      | Tool          | Version | Config File           |
| ------------- | ------------- | ------- | --------------------- |
| Language      | Python        | 3.12+   | pyproject.toml        |
| Dep manager   | uv            | latest  | pyproject.toml        |
| Linter        | ruff          | latest  | pyproject.toml        |
| Type checker  | mypy          | 1.8+    | pyproject.toml        |
| Test runner   | pytest        | 8.x     | pyproject.toml        |
| E2E framework | Playwright    | 1.45+   | playwright.config.py  |
