---
description: "Define test strategy using grill-me interview"
agent: matd-qa
skills:
  - 'general-grill-me'
  - 'dev-tdd'
  - 'arch-mermaid-diagrams'
tools:
  - 'filesystem/read'
  - 'filesystem/write'
templates:
  test-strategy: .speckit-templates/qa/test-strategy-template.md
exit_codes:
  0: "Success - test strategy created"
  1: "Validation failure - required inputs missing"
  2: "Escalation required - template missing or write error"
---

# Test Strategy Workflow (MATD — QA-Level Strategy)

This command runs a grill-me session to define the testing approach for a project or product. Use this to establish test pyramid ratios, patterns, tools, and coverage targets before writing individual test designs.

## Prerequisites

- Project or product context available (product brief recommended but not required)
- Template available at `.speckit-templates/qa/test-strategy-template.md`

## User Input

`/speckit.matd.specify-test-strategy [PROJECT_NAME]`

**Arguments**:
- `[PROJECT_NAME]`: Optional project identifier. If not provided, will be determined during grill-me session.

## Step 1: Load Configuration

Load from `.specify/harness-tdd-config.yml` or use defaults:

| Key | Default | Purpose |
|-----|---------|---------|
| `artifacts.root` | `docs/testing` | Root directory for test strategy |
| `workflow.agent_timeout` | `30` | Agent task timeout in minutes |
| `planning.skill` | `grill-me` | Skill used for discovery questioning |

If config file is missing or unreadable, continue with the defaults above. Log a warning to stderr but do not abort.

## Step 2: Check Existing Test Strategy

**Check for existing test strategy:**

Search for: `docs/testing/TEST_STRATEGY.md`

- If found: mention it to the user — "Test strategy already exists at `docs/testing/TEST_STRATEGY.md`, will merge updates" — then proceed
- If not found: continue (will create from template in Step 5)

## Step 3: Check Related Artifacts

Search in order for context:

1. `docs/product-brief.md` — Product-level context
2. `docs/architecture/technical-constitution.md` — Technical constraints and NFRs
3. `docs/testing/*.md` — Existing test documentation

- If found: load them silently for reference during grill-me session
- If not found: note that test strategy can be created independently

## Step 4: Run Grill-Me Session (general-grill-me skill)

Use the `general-grill-me` skill throughout this step.

**Goal:** Reach consensus on testing approach, test pyramid ratios, patterns, and quality gates through relentless questioning.

**Approach:**
- Ask questions **one at a time**, waiting for user response before continuing
- Reference loaded context (product brief, constitution) in your questions
- Track unanswered/deferred questions separately from answered ones
- Continue until you reach consensus with the user OR user signals done (e.g., "that's enough")
- Allow user to defer unknowns — note them as open questions, do not block on them

**Questions must cover all test strategy sections:**

### A. Testing Philosophy & Principles (5-7 questions)

- **Core Philosophy**: What is your testing philosophy? (e.g., TDD-first, risk-based, behavior-driven)
- **Quality Mindset**: What does "high quality" mean for this project? Speed? Reliability? User experience?
- **Testing Principles**: What 3-5 core principles should guide all testing decisions?
- **Quality Gates**: What must pass before code can be merged? Before deployment?
- **Team Skills**: What is the team's testing maturity level? (Junior, intermediate, expert)

### B. Test Pyramid Strategy (8-10 questions)

- **System Type**: What kind of system is this? (API, web app, mobile app, CLI, data pipeline, etc.)
- **Testing Priorities**: What matters most? Fast feedback? Deep integration coverage? User journey validation?
- **Current State**: If tests exist, what is the current unit:integration:e2e ratio?
- **Ideal Distribution**: What should the unit:integration:e2e ratio be? (e.g., 70:20:10)
- **Unit Test Scope**: What should unit tests cover? (Functions? Classes? Modules?)
- **Integration Test Scope**: What should integration tests cover? (API endpoints? Database interactions? Service boundaries?)
- **E2E Test Scope**: What should E2E tests cover? (Critical user journeys? Smoke tests? Full flows?)
- **Execution Time Targets**: How fast should each layer run? (Unit: <1s, Integration: <5s, E2E: <30s?)
- **Rationale**: Why this distribution? What tradeoffs were considered?

### C. Test Patterns & Conventions (5-7 questions)

- **Naming Conventions**: How should tests be named? (Given-When-Then? test_*, it_*, describe blocks?)
- **Test Organization**: How should test files be organized? (Mirror src/? Separate test/?)
- **Common Patterns**: What test patterns are preferred? (Arrange-Act-Assert? Given-When-Then? Four-phase test?)
- **Mocking Strategy**: When should mocks be used? When should real implementations be used?
- **Anti-Patterns**: What testing anti-patterns should be avoided? (e.g., test interdependence, flaky tests)

### D. Tools & Frameworks (4-6 questions)

- **Existing Stack**: What testing tools/frameworks are already in use?
- **Unit Testing**: What tool for unit tests? (pytest, jest, junit, etc.)
- **Integration Testing**: What tool for integration tests? (same as unit? separate?)
- **E2E Testing**: What tool for E2E tests? (Playwright, Cypress, Selenium, etc.)
- **Coverage Tool**: What tool for coverage measurement?
- **CI/CD Integration**: What CI/CD platform? (GitHub Actions, GitLab CI, Jenkins, etc.)

### E. Coverage Targets (4-5 questions)

- **Line Coverage**: What is the minimum line coverage target? (e.g., 80%, 90%)
- **Branch Coverage**: What is the minimum branch coverage target?
- **Critical Paths**: Should critical paths have higher coverage requirements? (e.g., 100%)
- **Coverage Enforcement**: How should coverage be enforced? (CI failure? Warning? Advisory?)
- **Exemptions**: Are there any files/paths that should be exempt from coverage requirements?

### F. CI/CD Integration (5-6 questions)

- **Pipeline Stages**: What test stages should exist in the CI pipeline? (pre-commit, PR, main, release)
- **Pre-commit Tests**: What should run before commit? (unit only? linting?)
- **PR Tests**: What should run on pull requests? (all tests? subset?)
- **Main Branch Tests**: What should run on main branch commits?
- **Release Tests**: What should run before release? (full suite? smoke tests?)
- **Failure Handling**: How should test failures be handled? (Block merge? Alert? Auto-rollback?)

### G. Performance & Load Testing (3-5 questions)

- **Performance Requirements**: Are there performance requirements? (latency, throughput)
- **Load Scenarios**: What load scenarios need testing? (normal load, peak load, stress)
- **Performance Benchmarks**: What are the performance benchmarks? (p50, p95, p99 latency targets)
- **Load Testing Tools**: What tools for load testing? (k6, Gatling, JMeter, Locust)

### H. Security Testing (3-4 questions)

- **Security Requirements**: Are there security compliance requirements? (GDPR, SOC2, PCI-DSS)
- **Static Analysis**: What static security analysis tools? (Bandit, SonarQube, Snyk)
- **Dependency Scanning**: Should dependencies be scanned for vulnerabilities?
- **Security Test Coverage**: What security scenarios need testing? (auth, authz, injection, XSS)

### I. Test Data Management (3-5 questions)

- **Test Data Strategy**: How should test data be managed? (fixtures, factories, seed data)
- **Data Generation**: Should test data be generated? Hand-crafted? Mix?
- **Data Privacy**: Are there privacy concerns with test data? (PII, GDPR)
- **Environment Data**: What data is needed per environment? (local, CI, staging)

### J. Testing Workflow (2-3 questions)

- **TDD Adoption**: Is TDD required? Recommended? Optional?
- **Developer Workflow**: What is the expected developer testing workflow?
- **Test Review**: Should tests be reviewed separately or with code?

## Step 5: Generate Test Pyramid Visualization (Optional)

If the user's responses include clear test pyramid ratios, generate a Mermaid diagram visualization:

- Use `arch-mermaid-diagrams` skill to create a pyramid diagram
- Show the unit:integration:e2e distribution
- Include execution time targets for each layer
- Save diagram to: `docs/testing/test-pyramid.md` (embedded Mermaid)

If ratios are unclear or user defers, skip this step.

## Step 6: Generate Test Strategy Document

- Fill `.speckit-templates/qa/test-strategy-template.md` with answers gathered in the grill-me session
- If existing test strategy found (Step 2): merge new information into it — do not overwrite sections that are already complete unless the user provided updates in this session
- Save to: `docs/testing/TEST_STRATEGY.md`
- If save fails: ❌ Exit 2 with message: "Error: failed to write test strategy to `docs/testing/TEST_STRATEGY.md`"
- If `test-strategy-template.md` is missing: ❌ Exit 2 with message: "Error: template not found at `.speckit-templates/qa/test-strategy-template.md`"

## Step 7: Save Open Questions (if any)

- If any questions were deferred by user during the grill-me session:
  - Save them to: `docs/testing/test-strategy-open-questions.md`
  - Format: a simple list with each unanswered question and the context in which it arose
- If no open questions exist: skip this step entirely — do not create an empty file

## Step 8: Report

Show a final summary:

```
✓ Test strategy created/updated at: docs/testing/TEST_STRATEGY.md
✓ Test pyramid visualization at: docs/testing/test-pyramid.md (if generated)
⚠ Open questions saved at: docs/testing/test-strategy-open-questions.md (only if any)
```

Suggest next steps:

> Test strategy is now available as context for feature test designs. When creating test specs with `/speckit.matd.test`, the matd-qa agent can reference this strategy for test pyramid guidance.
>
> **Recommended next steps:**
> 1. Review test strategy with team
> 2. Set up CI/CD pipeline stages according to strategy
> 3. Configure coverage enforcement in CI
> 4. Create first feature test design using this strategy

## Exit Codes

- **0**: Success — test strategy created or updated
- **1**: Validation failure — required inputs missing
- **2**: Escalation required — template missing or write error

## Configuration Reference

`.specify/harness-tdd-config.yml` keys used by this command:

```yaml
artifacts:
  root: docs/testing           # Root dir for test strategy output

workflow:
  agent_timeout: 30            # Grill-me session timeout in minutes

planning:
  skill: grill-me              # Skill used for discovery
```

## Related Commands

- `/speckit.matd.test`: Create feature test design (use this for individual feature tests)
- `/speckit.matd.specify-product-brief`: Create product brief (provides context for test strategy)
- `/speckit.matd.execute`: Execute TDD workflow (RED-GREEN-REFACTOR)

## Test Strategy vs Test Design

**Use Test Strategy when:**
- Starting a new project or product
- Need to define overall testing approach
- Establishing test pyramid ratios
- Defining quality gates and coverage targets
- Setting up CI/CD testing pipeline

**Use Test Design when:**
- Adding tests for individual features
- Need detailed test scenarios
- Creating test cases and assertions
- Planning feature-level test implementation

**Note:** Test strategy is OPTIONAL but recommended. Feature test designs can be created independently without a test strategy, but having one ensures consistency across features.
