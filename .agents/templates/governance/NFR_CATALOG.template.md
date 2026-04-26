# Non-Functional Requirements Catalog

**Project:** {{project_name}}
**Version:** {{version}}
**Last Updated:** {{date}}
**Validation:** All NFRs must use EARS notation and have testable acceptance criteria.

---

## NFR Classification (ISO/IEC 25010)

1. **Performance Efficiency** (`PERF`) — response time, throughput, resource use.
2. **Reliability** (`REL`) — availability, fault tolerance, recoverability.
3. **Security** (`SEC`) — confidentiality, integrity, AuthN, AuthZ.
4. **Usability** (`USE`) — accessibility, learnability, error prevention.
5. **Maintainability** (`MAIN`) — modularity, testability, modifiability.
6. **Compatibility** (`COMP`) — interoperability, coexistence.
7. **Portability** (`PORT`) — adaptability, installability, env parity.
8. **Functional Suitability** (`FUNC`) — completeness, correctness, appropriateness.

EARS templates: ubiquitous, event-driven (`when`), state-driven (`while`),
unwanted (`if/then`), optional-feature (`where`).

---

## 1. Performance Efficiency

### NFR-PERF-001: {{title}}
**Category:** Performance Efficiency > {{subcategory}}
**Requirement (EARS):**
> {{ears_statement}}

**Acceptance Criteria:**
- {{ac_1}}
- {{ac_2}}

**Test Strategy:**
- {{test_strategy_1}}

**Priority:** {{priority}}
**Rationale:** {{rationale}}

---

## 2. Reliability

### NFR-REL-001: {{title}}
**Category:** Reliability > {{subcategory}}
**Requirement (EARS):**
> {{ears_statement}}

**Acceptance Criteria:**
- {{ac_1}}

**Test Strategy:**
- {{test_strategy_1}}

**Priority:** {{priority}}

---

## 3. Security

### NFR-SEC-001: {{title}}
**Category:** Security > {{subcategory}}
**Requirement (EARS):**
> {{ears_statement}}

**Acceptance Criteria:**
- {{ac_1}}

**Test Strategy:**
- {{test_strategy_1}}

**Priority:** {{priority}}

---

## 4. Usability

### NFR-USE-001: {{title}}
**Category:** Usability > {{subcategory}}
**Requirement (EARS):**
> {{ears_statement}}

**Acceptance Criteria:**
- {{ac_1}}

**Test Strategy:**
- {{test_strategy_1}}

**Priority:** {{priority}}

---

## 5. Maintainability

### NFR-MAIN-001: {{title}}
**Category:** Maintainability > {{subcategory}}
**Requirement (EARS):**
> {{ears_statement}}

**Acceptance Criteria:**
- {{ac_1}}

**Test Strategy:**
- {{test_strategy_1}}

**Priority:** {{priority}}

---

## Appendix: NFR Validation Matrix

| NFR ID         | Testable? | Automated test           | Manual test       | Monitoring          | Owner      |
| -------------- | --------- | ------------------------ | ----------------- | ------------------- | ---------- |
| NFR-PERF-001   | yes       | {{automated}}            | {{manual}}        | {{monitoring}}      | {{owner}}  |
| NFR-REL-001    | yes       | {{automated}}            | {{manual}}        | {{monitoring}}      | {{owner}}  |
| NFR-SEC-001    | yes       | {{automated}}            | {{manual}}        | {{monitoring}}      | {{owner}}  |
| NFR-USE-001    | yes       | {{automated}}            | {{manual}}        | {{monitoring}}      | {{owner}}  |
| NFR-MAIN-001   | yes       | {{automated}}            | {{manual}}        | {{monitoring}}      | {{owner}}  |

---

## NFR Lifecycle

1. **Definition (Phase 0):** Architect + PM define NFRs before Analysis phase.
2. **Refinement (Phase 2):** PM translates NFRs into user stories where applicable.
3. **Design (Phase 3):** Architect designs systems to meet NFRs (ADRs reference NFR IDs).
4. **Implementation (Phase 4):** Developers write tests validating NFRs.
5. **Monitoring (Phase 5):** SRE/DevOps configure alerts for NFR violations.
6. **Review (Quarterly):** Architect reviews NFR compliance, updates thresholds.
