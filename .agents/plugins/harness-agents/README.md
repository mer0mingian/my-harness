# Harness Agents Plugin

Multi-agent TDD workflow specialist agents for Claude Code.

## Overview

This plugin provides 5 specialist agent definitions that implement a structured TDD workflow with clear role separation and constitutional constraints. Each agent has specific capabilities, permissions, and responsibilities.

## Agents

### @test - Test Specialist
**Role**: Writes failing tests BEFORE implementation
- **Capabilities**: test_generation, test_design, red_state_validation
- **Critical Constraint**: MUST NOT write implementation code
- **Permissions**: Write access to test files only (`tests/**`)
- **Skills**: stdd-test-author-constrained, python-testing-uv-playwright, review-e2e-testing-patterns

### @make - Dev Specialist
**Role**: Implements code to achieve GREEN tests
- **Capabilities**: implementation, refactoring, green_state_achievement
- **Critical Constraint**: MUST NOT alter test code under any circumstances
- **Permissions**: Write access to production code only (`src/**`, `app/**`, `lib/**`)
- **Skills**: stdd-make-constrained-implementation, general-python-environment, python-fastapi-templates

### @check - Architecture Specialist
**Role**: Reviews for architectural flaws and safety violations
- **Capabilities**: architecture_review, safety_validation, risk_assessment
- **Critical Constraint**: Read-only permissions, safety constraints ALWAYS win
- **Permissions**: Read-only, inspection commands only
- **Skills**: review-check-correctness, review-differential-review

### @simplify - Review Specialist
**Role**: Identifies unnecessary complexity
- **Capabilities**: complexity_analysis, refactoring_suggestions, code_quality_review
- **Critical Constraint**: Defers to @check on safety concerns
- **Permissions**: Read-only, inspection commands only
- **Skills**: review-simplify-complexity, general-solid, python-design-patterns

### @qa - QA Specialist
**Role**: Validates acceptance criteria via browser and CLI testing
- **Capabilities**: acceptance_validation, e2e_testing, integration_testing, evidence_capture
- **Critical Constraint**: Limited write access (e2e/integration tests only)
- **Permissions**: Write access to `tests/e2e/**` and `tests/integration/**` only
- **Skills**: python-testing-uv-playwright, review-webapp-testing, review-e2e-testing-patterns

## Installation

### From Claude Code CLI

```bash
claude plugin install /path/to/harness-tooling/.agents/plugins/harness-agents
```

### Verify Installation

```bash
# Check plugin is installed
claude plugin list

# Verify agents are available
ls ~/.claude/agents/
```

You should see:
- test-specialist.md
- dev-specialist.md
- arch-specialist.md
- review-specialist.md
- qa-specialist.md

## Usage

Agents can be invoked via Claude Code's agent system. Each agent has specific skills and permissions that enforce TDD workflow constraints.

### Example Workflow

1. **@test** writes failing tests for a feature
2. **@make** implements code to make tests pass
3. **@check** reviews for architectural/safety issues
4. **@simplify** suggests complexity improvements
5. **@qa** validates acceptance via e2e tests

## Constitutional Principles

### Test Immutability (CRITICAL)
Developer agents (@make, @check, @simplify, @qa) are NEVER permitted to modify test code. This includes:
- Altering test assertions
- Changing test setup/teardown
- Modifying fixtures or mocks
- Adjusting expected values
- Commenting out tests
- Skipping tests

### Agent Specialization
Each agent has ONE responsibility:
- @test: Write failing tests, classify failures
- @make: Achieve GREEN state, implement features
- @check: Review architecture, identify risks
- @simplify: Review complexity, suggest improvements
- @qa: Validate acceptance, capture evidence

### Conflict Resolution
- Safety constraints (from @check) ALWAYS win over simplicity (from @simplify)
- @qa cannot approve failing tests
- Test modifications require returning to @test through proper workflow

## Version

**1.0.0** - Initial release for Phase 1, Slice 1 of Multi-Agent TDD Workflow system

## License

MIT

## Author

Daniel Mingers (minged01@stepstone.com)
