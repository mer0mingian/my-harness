---
name: governance-nfr-writer
description: Generate or amend NFR_CATALOG.md using ISO/IEC 25010 categories and
  EARS notation. Enforces stable IDs, testable acceptance criteria, and explicit
  test strategies. Use when @governance-nfr-specialist authors or updates the
  catalog.
---
# Governance NFR Writer

Rules and templates for producing `docs/governance/NFR_CATALOG.md`.

## ISO/IEC 25010 categories (use these exactly)

| Category code | ISO 25010 quality          | Typical NFRs                                  |
| ------------- | -------------------------- | --------------------------------------------- |
| `PERF`        | Performance Efficiency     | Latency, throughput, resource utilisation     |
| `REL`         | Reliability                | Availability, fault tolerance, recoverability |
| `SEC`         | Security                   | AuthN, AuthZ, encryption, audit               |
| `USE`         | Usability                  | Accessibility, learnability, error prevention |
| `MAIN`        | Maintainability            | Modularity, testability, modifiability        |
| `COMP`        | Compatibility              | Interoperability, coexistence                 |
| `PORT`        | Portability                | Adaptability, installability, env parity      |
| `FUNC`        | Functional Suitability     | Completeness, correctness, appropriateness    |

NFR IDs follow the pattern `NFR-<CODE>-NNN` (zero-padded). Never renumber.

## EARS templates (pick one per NFR)

| Type             | Pattern                                                                       |
| ---------------- | ----------------------------------------------------------------------------- |
| Ubiquitous       | "The <system> shall <response>."                                              |
| Event-driven     | "When <trigger>, the <system> shall <response>."                              |
| State-driven     | "While <state>, the <system> shall <response>."                               |
| Unwanted         | "If <unwanted condition>, then the <system> shall <response>."                |
| Optional feature | "Where <feature is included>, the <system> shall <response>."                 |

Each requirement statement must contain at least one of the EARS keywords:
`shall`, `when`, `while`, `where`, `if/then`. The validator enforces this.

## NFR block format (canonical)

```markdown
### NFR-PERF-001: API Response Time
**Category:** Performance Efficiency > Throughput
**Requirement (EARS):**
> When a user requests data via any REST API endpoint, the system shall return a response within 200ms (p95) under normal load conditions.

**Acceptance Criteria:**
- p50 latency <= 100ms
- p95 latency <= 200ms
- p99 latency <= 500ms

**Test Strategy:**
- Locust load test, 1000 concurrent users
- p95 measured over 10-minute window in staging

**Priority:** P0
**Rationale:** UX research shows >250ms feels sluggish.
```

Required fields per block: ID, Category, Requirement (EARS), Acceptance
Criteria, Test Strategy, Priority. `Rationale` is optional but encouraged.

## Authoring workflow

1. Load template `.agents/templates/governance/NFR_CATALOG.template.md`.
2. For each ISO 25010 category present in interview output, emit at least one
   NFR; skip categories the user marked out-of-scope.
3. Number NFRs sequentially per category (PERF-001, PERF-002, ...).
4. For every NFR, ensure the EARS statement contains a measurable threshold
   ("200ms", "99.9%", "AES-256-GCM", etc.). If a number is missing, write
   `TBD: target threshold pending architect input`.
5. Append the NFR Validation Matrix table at the bottom listing every NFR with
   its automated/manual test type and owner.
6. Run schema validation.

## Priority rules

- At least one P0 NFR per category that applies to the project.
- A category with only P2 NFRs is suspicious — challenge the user.
- Compliance-driven NFRs (WCAG, GDPR, HIPAA) are always P0 if the project is
  subject to that regime.

## Linkage rules

- NFRs may cite ADRs ("see ADR-005") but ADRs cite NFRs (not the other way
  around for design decisions). Keep this catalog the source of truth.
- The `@bmad-pm` agent will reference NFR IDs in user stories. IDs MUST be
  stable across amendments.

## Output checklist

- [ ] At least one NFR per applicable ISO 25010 category.
- [ ] Every NFR uses an EARS keyword.
- [ ] Every NFR has measurable Acceptance Criteria and a named Test Strategy.
- [ ] NFR Validation Matrix appendix present.
- [ ] File validates against `nfr.schema.json`.
