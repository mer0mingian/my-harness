# Technical Constitution

**Project:** {{project_name}}
**Version:** {{version}}
**Last Updated:** {{date}}
**Governance:** {{governance_rule}}

---

## 1. Technology Preferences

### 1.1 Backend Stack
- **Language:** {{backend.language}}
- **Web Framework:** {{backend.framework}}
- **Dependency Management:** {{backend.dep_manager}}
- **Database:** {{backend.database}}
- **ORM:** {{backend.orm}}

### 1.2 Frontend Stack
- **HTML Rendering:** {{frontend.rendering}}
- **Reactive UI:** {{frontend.reactive}}
- **CSS Framework:** {{frontend.css}}
- **Build Tool:** {{frontend.build}}

### 1.3 Testing & Quality
- **Unit Testing:** {{testing.unit}}
- **E2E Testing:** {{testing.e2e}}
- **Mocking:** {{testing.mocking}}
- **Coverage threshold:** {{testing.coverage_threshold}}

### 1.4 Infrastructure
- **Containerisation:** {{infra.container}}
- **Orchestration:** {{infra.orchestration}}
- **Secrets Management:** {{infra.secrets}}

**Rationale for choices:**
- {{rationale_bullet_1}}
- {{rationale_bullet_2}}

---

## 2. Solution Approach Constraints

### 2.1 Architecture Patterns
- **MUST:** {{arch.must_1}}
- **MUST NOT:** {{arch.must_not_1}}

### 2.2 API Design
- **MUST:** {{api.must_1}}
- **MUST NOT:** {{api.must_not_1}}

### 2.3 Data Access
- **MUST:** {{data.must_1}}
- **MUST NOT:** {{data.must_not_1}}

### 2.4 Error Handling
- **MUST:** {{err.must_1}}
- **MUST NOT:** {{err.must_not_1}}

**Rationale:**
- {{solution_rationale}}

---

## 3. Code Quality Standards

### 3.1 Naming Conventions
- **Functions:** {{naming.functions}}
- **Classes:** {{naming.classes}}
- **Constants:** {{naming.constants}}
- **Files:** {{naming.files}}

### 3.2 Documentation Requirements
- **MUST:** {{docs.must_1}}
- **SHOULD:** {{docs.should_1}}

### 3.3 Linting & Formatting
- **Formatter:** {{quality.formatter}}
- **Linter:** {{quality.linter}}
- **Type Checker:** {{quality.type_checker}}
- **Pre-commit:** {{quality.precommit}}

---

## 4. Security Baseline

### 4.1 Authentication & Authorization
- **MUST:** {{sec.authn_must}}
- **MUST NOT:** {{sec.authn_must_not}}

### 4.2 Data Protection
- **MUST:** Encrypt PII at rest ({{sec.encryption_at_rest}})
- **MUST:** Use {{sec.encryption_in_transit}} for all external communication
- **MUST NOT:** Log PII or credentials

### 4.3 Dependency Management
- **MUST:** {{sec.dep_must}}
- **MUST NOT:** {{sec.dep_must_not}}

---

## 5. Amendment Process

**Minor changes** (e.g. patch version bumps): {{amend.minor}}
**Major changes** (e.g. swapping primary database): {{amend.major}}
**Effective date:** Changes take effect on merge to the main branch.

---

## Appendix: Tooling Reference

| Category      | Tool                | Version          | Config File              |
| ------------- | ------------------- | ---------------- | ------------------------ |
| Language      | {{tool.language}}   | {{ver.language}} | {{cfg.language}}         |
| Dep manager   | {{tool.dep}}        | {{ver.dep}}      | {{cfg.dep}}              |
| Linter        | {{tool.linter}}     | {{ver.linter}}   | {{cfg.linter}}           |
| Type checker  | {{tool.types}}      | {{ver.types}}    | {{cfg.types}}            |
| Test runner   | {{tool.test}}       | {{ver.test}}     | {{cfg.test}}             |
| E2E framework | {{tool.e2e}}        | {{ver.e2e}}      | {{cfg.e2e}}              |
