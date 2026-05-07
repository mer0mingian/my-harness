# Task List: Multi-Agent TDD Workflow Implementation

**Version:** 1.0  
**Date:** 2026-05-07  
**Status:** Planning  
**Derived From:** PLAN-Multi-Agent-TDD-Implementation.md

---

## Task Organization

Tasks organized by vertical slice with clear dependencies, acceptance criteria, and estimated effort. Each task is independently testable.

**Legend:**
- **ID:** Unique task identifier (SLICE#-TASK#)
- **Priority:** P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- **Effort:** Hours or story points
- **Dependencies:** Prerequisites (task IDs or "None")

---

## Slice 1: Foundation - Agent Definitions & Basic Runtime

### S1-001: Create harness-agents Plugin Manifest
**Priority:** P0  
**Effort:** 30 min  
**Dependencies:** None

**Description:** Create plugin.json for harness-agents Claude Code plugin.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.claude-plugin/harness-agents/plugin.json`
- [ ] Manifest declares plugin name, version, description
- [ ] Manifest lists 5 agent definition files
- [ ] Installation target: `.claude/agents/`
- [ ] JSON validates with `jq .`

**Files Changed:**
- Create: `harness-tooling/.claude-plugin/harness-agents/plugin.json`

---

### S1-002: Adapt test-specialist Agent Definition (REUSE)
**Priority:** P0  
**Effort:** 15 min  
**Dependencies:** S1-001

**Description:** Copy and adapt existing `pries-test.md` agent for @test specialist role.

**Reuse Strategy:**
- Source: `harness-tooling/.agents/agents/pries-test.md`
- Target: `harness-tooling/.claude-plugin/harness-agents/agents/test-specialist.md`
- Keep existing skills: `stdd-test-author-constrained`, `python-testing-uv-playwright`, `stdd-test-driven-development`
- Keep existing permissions and constraints

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.claude-plugin/harness-agents/agents/test-specialist.md`
- [ ] Markdown format with YAML frontmatter
- [ ] Frontmatter fields: `name: test-specialist`, `description`, `tools`, `skills`
- [ ] Role documented in system prompt: "@test"
- [ ] Capabilities: test_generation, test_design, red_state_validation
- [ ] Constraints: MUST write failing tests, MUST NOT write implementation, **MUST NOT alter tests once written**
- [ ] Failure codes defined: MISSING_BEHAVIOR, ASSERTION_MISMATCH (valid RED), TEST_BROKEN, ENV_BROKEN (invalid)
- [ ] Skills assigned: `stdd-test-author-constrained`, `python-testing-uv-playwright`, `stdd-test-driven-development`

**Files Changed:**
- Copy: `pries-test.md` → `test-specialist.md`

**Note:** Python-focused initially. Java support (JUnit 5 skill) added in future phase.

---

### S1-003: Adapt dev-specialist Agent Definition (REUSE)
**Priority:** P0  
**Effort:** 15 min  
**Dependencies:** S1-001

**Description:** Copy and adapt existing `pries-make.md` agent for @make specialist role.

**Reuse Strategy:**
- Source: `harness-tooling/.agents/agents/pries-make.md`
- Target: `harness-tooling/.claude-plugin/harness-agents/agents/dev-specialist.md`
- Keep existing skills: `stdd-make-constrained-implementation`, `general-python-environment`, `python-fastapi-templates`
- Keep existing TDD validation logic

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.claude-plugin/harness-agents/agents/dev-specialist.md`
- [ ] Markdown format with YAML frontmatter
- [ ] Frontmatter fields: `name: dev-specialist`, `description`, `tools`, `skills`
- [ ] Role documented in system prompt: "@make"
- [ ] Capabilities: implementation, refactoring, green_state_achievement
- [ ] TDD validation: before_implementation (run tests, verify RED, halt if GREEN)
- [ ] **Critical constraint**: MUST NOT alter test code under any circumstances
- [ ] Refactoring: runs after GREEN state achieved
- [ ] Skills assigned: `stdd-make-constrained-implementation`, `general-python-environment`, `python-fastapi-templates`

**Files Changed:**
- Copy: `pries-make.md` → `dev-specialist.md`

**Note:** Python-focused initially. Java support (Spring Boot skill) added in future phase.

---

### S1-004: Adapt arch-specialist Agent Definition (REUSE)
**Priority:** P0  
**Effort:** 15 min  
**Dependencies:** S1-001

**Description:** Copy and adapt existing `pries-check.md` agent for @check specialist role.

**Reuse Strategy:**
- Source: `harness-tooling/.agents/agents/pries-check.md`
- Target: `harness-tooling/.claude-plugin/harness-agents/agents/arch-specialist.md`
- Keep existing skills: `review-check-correctness`, `review-differential-review`
- Keep existing 8-pillar risk framework

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.claude-plugin/harness-agents/agents/arch-specialist.md`
- [ ] Markdown format with YAML frontmatter
- [ ] Frontmatter fields: `name: arch-specialist`, `description`, `tools`, `skills`
- [ ] Role documented in system prompt: "@check"
- [ ] Review criteria: safety_constraints (security, data integrity, backward compatibility)
- [ ] Verdict logic: ACCEPTABLE | NEEDS_REVISION | BLOCKED
- [ ] Conflict resolution: safety constraints ALWAYS win over @simplify
- [ ] Skills assigned: `review-check-correctness`, `review-differential-review`, `stdd-test-driven-development`
- [ ] Read-only permissions (no code mutations)

**Files Changed:**
- Copy: `pries-check.md` → `arch-specialist.md`

**Note:** Language-agnostic. Works for both Python and Java without modification.

---

### S1-005: Adapt review-specialist Agent Definition (REUSE)
**Priority:** P0  
**Effort:** 15 min  
**Dependencies:** S1-001

**Description:** Copy and adapt existing `pries-simplify.md` agent for @simplify specialist role.

**Reuse Strategy:**
- Source: `harness-tooling/.agents/agents/pries-simplify.md`
- Target: `harness-tooling/.claude-plugin/harness-agents/agents/review-specialist.md`
- Keep existing skills: `review-simplify-complexity`, `general-solid`, `python-design-patterns`
- Keep existing delete-test methodology and protected-pattern allowlist

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.claude-plugin/harness-agents/agents/review-specialist.md`
- [ ] Markdown format with YAML frontmatter
- [ ] Frontmatter fields: `name: review-specialist`, `description`, `tools`, `skills`
- [ ] Role documented in system prompt: "@simplify"
- [ ] Review criteria: complexity (cyclomatic, nesting, length), duplication, readability
- [ ] Verdict logic: ACCEPTABLE | NEEDS_REVISION
- [ ] Conflict resolution: defer to @check when safety constraints present
- [ ] Skills assigned: `review-simplify-complexity`, `general-solid`, `python-design-patterns`
- [ ] Read-only permissions (no code mutations)

**Files Changed:**
- Copy: `pries-simplify.md` → `review-specialist.md`

**Note:** Python-focused initially. Java support (Java design patterns skill) added in future phase.

---

### S1-006: Create qa-specialist Agent Definition (NEW)
**Priority:** P0  
**Effort:** 2 hours  
**Dependencies:** S1-001

**Description:** Create new @qa agent for browser/CLI validation (not reusing stdd-qa-subagent.md due to overlapping responsibilities).

**Why Not Reuse:**
- `stdd-qa-subagent.md` has write access to `tests/**` (overlaps with @test)
- Too broad (includes implementation review, overlaps with @check/@simplify)
- Missing focus on browser automation and CLI validation

**New Agent Design:**
- **Focus**: Acceptance validation via browser and CLI testing
- **Permissions**: Read-only for production code, write access to `tests/e2e/**` and `tests/integration/**` only
- **Validation types**: Browser (routes, forms, UI elements, responsive), CLI (commands, output, exit codes)

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.claude-plugin/harness-agents/agents/qa-specialist.md`
- [ ] Markdown format with YAML frontmatter
- [ ] Frontmatter fields: `name: qa-specialist`, `description`, `tools`, `skills`, `permissionMode`
- [ ] Role documented in system prompt: "@qa"
- [ ] QA gates: cli (test_suite, linting, type_checking, coverage), browser (routes, forms, ui_elements, responsive)
- [ ] Permissions: Read-only for `src/**`, write access for `tests/e2e/**` and `tests/integration/**` only
- [ ] Skills assigned: `python-testing-uv-playwright`, `review-webapp-testing`, `review-e2e-testing-patterns`, `general-verification-before-completion`
- [ ] Evidence capture: screenshots, test outputs, validation reports

**Files Changed:**
- Create: `harness-tooling/.claude-plugin/harness-agents/agents/qa-specialist.md`

**Note:** Python-focused initially. Java support (Selenium/TestNG skills) added in future phase.

---

### S1-007: Implement /agents.spawn Command
**Priority:** P1  
**Effort:** 2 hours  
**Dependencies:** S1-002 through S1-006

**Description:** Runtime command to spawn specialist agents with context.

**Acceptance Criteria:**
- [ ] Command available: `/agents.spawn <agent-name> <task-description>`
- [ ] Loads agent definition from `.claude/agents/<agent-name>.md`
- [ ] Parses YAML frontmatter for agent configuration
- [ ] Passes TDD workflow context and principles to agent
- [ ] Agent spawns in isolated session
- [ ] Returns agent session ID

**Files Changed:**
- Create: `harness-tooling/.claude-plugin/harness-agents/commands/spawn.py` (or shell script)

---

### S1-008: Implement /agents.assign-task Command
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S1-007

**Description:** Route task file to appropriate specialist agent.

**Acceptance Criteria:**
- [ ] Command available: `/agents.assign-task <agent-name> <task-file>`
- [ ] Reads task file content
- [ ] Spawns agent with task context
- [ ] Validates agent capabilities match task requirements
- [ ] Returns assignment confirmation

**Files Changed:**
- Create: `harness-tooling/.claude-plugin/harness-agents/commands/assign-task.py`

---

### S1-009: Test Plugin Installation
**Priority:** P0  
**Effort:** 30 min  
**Dependencies:** S1-001 through S1-008

**Description:** Verify harness-agents plugin installs correctly.

**Acceptance Criteria:**
- [ ] `claude plugin install ../harness-tooling/.claude-plugin/harness-agents` succeeds
- [ ] `claude plugin list` shows harness-agents (active)
- [ ] All 5 agent definitions copied to `.claude/agents/`
- [ ] Commands `/agents.spawn` and `/agents.assign-task` available
- [ ] No errors in installation logs

**Files Changed:**
- None (verification only)

---

## Slice 2: SpecKit Extension Structure & Configuration

### S2-001: Create SpecKit Extension Manifest
**Priority:** P0  
**Effort:** 45 min  
**Dependencies:** None

**Description:** Create extension.json for harness-tdd-workflow SpecKit extension.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/extension.json`
- [ ] Manifest declares extension name, version, description
- [ ] Declares commands: test, implement, review, commit, plan
- [ ] Declares template directory: `templates/`
- [ ] Declares config file: `harness-tdd-config.yml`
- [ ] JSON validates

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/extension.json`

---

### S2-002: Create Configuration Template
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S2-001

**Description:** Document all configuration options with comments.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/harness-tdd-config.yml.template`
- [ ] All artifact types documented (test_design, implementation_notes, arch_review, code_review, workflow_summary)
- [ ] Path configuration examples (default + custom)
- [ ] Mandatory flags documented
- [ ] Gates configuration documented (auto/manual, max_cycles)
- [ ] Planning configuration documented (grill-me integration)
- [ ] YAML validates

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/harness-tdd-config.yml.template`

---

### S2-003: Create Install Hook Script
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S2-002

**Description:** Script that runs on extension installation.

**Acceptance Criteria:**
- [ ] Script created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/hooks/install.sh`
- [ ] Copies config template to `.specify/harness-tdd-config.yml`
- [ ] Creates `.specify/templates/` directory
- [ ] Copies all 5 artifact templates to `.specify/templates/`
- [ ] Script idempotent (safe to re-run)
- [ ] Executable permission set

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/hooks/install.sh`

---

### S2-004: Test Extension Installation
**Priority:** P0  
**Effort:** 30 min  
**Dependencies:** S2-001 through S2-003

**Description:** Verify harness-tdd-workflow extension installs correctly.

**Acceptance Criteria:**
- [ ] `specify extension add harness-tdd-workflow --from ../harness-tooling/.speckit-extensions/harness-tdd-workflow` succeeds
- [ ] `specify extension list` shows harness-tdd-workflow (active)
- [ ] Config file created: `.specify/harness-tdd-config.yml`
- [ ] Templates directory created: `.specify/templates/`
- [ ] All 5 templates copied
- [ ] No errors in installation logs

**Files Changed:**
- None (verification only)

---

## Slice 2B: Automation Scripts (Optional Enhancement)

**Purpose:** Build Python automation scripts to accelerate deterministic tasks throughout implementation.

**Estimated Time Savings:** ~20 hours across workflow execution  
**Development Effort:** ~6-7 hours  
**ROI:** Immediate (saves time in Slices 3-6)

### S2B-001: Build Manifest Validator Script
**Priority:** P2  
**Effort:** 2 hours  
**Dependencies:** S2-001

**Description:** Python script to validate plugin.json, extension.json, agent definitions, and config YAML files.

**Automates Tasks:** S1-001 through S1-006, S2-001, S2-002 validation

**Acceptance Criteria:**
- [ ] Script created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/validate_manifests.py`
- [ ] Validates plugin.json structure (JSON Schema)
- [ ] Validates extension.json structure (JSON Schema)
- [ ] Validates agent definitions (markdown + YAML frontmatter format)
- [ ] Validates config YAML (schema conformance)
- [ ] Reports errors with file name, line number, field name
- [ ] Provides fix suggestions
- [ ] Exit code 0 (success) or 1 (validation failed)

**Libraries:** `pathlib`, `json`, `jsonschema`, `pyyaml`

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/validate_manifests.py`
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/schemas/plugin-schema.json`
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/schemas/extension-schema.json`

**Time Saved:** ~6 hours (manual validation of 8 manifests/configs)

---

### S2B-002: Build Artifact Template Generator Script
**Priority:** P2  
**Effort:** 2 hours  
**Dependencies:** S3-001, S4-001, S5-001, S5-002, S6-001 (templates must exist first)

**Description:** Python script to render artifact templates with Jinja2 variable substitution.

**Automates Tasks:** Creating artifacts from templates in Slices 3-6

**Acceptance Criteria:**
- [ ] Script created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/generate_artifact.py`
- [ ] Renders any template from `.specify/templates/`
- [ ] Substitutes variables: `{{feature_id}}`, `{{feature_name}}`, `{{timestamp}}`, `{{agent_name}}`
- [ ] Creates output directory if missing
- [ ] Validates output path matches config
- [ ] CLI usage: `generate_artifact.py test-design feat-123 "User Login"`
- [ ] Returns success/failure with clear error messages

**Libraries:** `jinja2`, `pathlib`, `pyyaml`, `argparse`

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/generate_artifact.py`

**Time Saved:** ~5 hours (manual template copy/paste for 7+ artifacts)

---

### S2B-003: Build Test Evidence Parser Script
**Priority:** P2  
**Effort:** 2.5 hours  
**Dependencies:** None (can start early)

**Description:** Python script to parse test runner output and extract RED/GREEN state with structured failure codes.

**Automates Tasks:** S3-004 (failure code detection), S4-003 (TDD entry validation), S4-004 (GREEN state validation)

**Acceptance Criteria:**
- [ ] Script created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/parse_test_evidence.py`
- [ ] Parses pytest output (Python)
- [ ] Classifies failures: MISSING_BEHAVIOR, ASSERTION_MISMATCH, TEST_BROKEN, ENV_BROKEN
- [ ] Detects RED vs GREEN vs BROKEN state
- [ ] Extracts test counts, failure locations, error messages
- [ ] Outputs structured JSON report
- [ ] CLI usage: `pytest tests/ | parse_test_evidence.py`
- [ ] Configurable regex patterns per framework

**Libraries:** `re`, `json`, `argparse`, `dataclasses`

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/parse_test_evidence.py`
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/config/test-patterns.yml` (failure code regex)

**Time Saved:** ~4 hours (manual test output analysis across 3 workflow executions)

---

### S2B-004: Build Artifact Validator Script
**Priority:** P2  
**Effort:** 1.5 hours  
**Dependencies:** S6-001 (workflow summary template)

**Description:** Python script to validate all mandatory artifacts exist and conform to templates.

**Automates Tasks:** S6-003 (artifact validation), S6-004 (evidence validation)

**Acceptance Criteria:**
- [ ] Script created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/validate_artifacts.py`
- [ ] Checks file existence for mandatory artifacts
- [ ] Validates template sections present (all headers exist)
- [ ] Validates evidence timestamps (RED before GREEN)
- [ ] Validates RED/GREEN state evidence present
- [ ] Reports missing artifacts or malformed structure
- [ ] CLI usage: `validate_artifacts.py feat-123`
- [ ] Exit code 0 (valid) or 1 (invalid)

**Libraries:** `pathlib`, `re`, `pyyaml`, `argparse`

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/scripts/validate_artifacts.py`

**Time Saved:** ~3 hours (manual artifact validation before each PR)

---

### S2B-005: Integration Test for Automation Scripts
**Priority:** P2  
**Effort:** 1 hour  
**Dependencies:** S2B-001 through S2B-004

**Description:** Verify all automation scripts work end-to-end.

**Acceptance Criteria:**
- [ ] Test manifest validator with valid and invalid manifests
- [ ] Test artifact generator with all 5 templates
- [ ] Test evidence parser with pytest output samples
- [ ] Test artifact validator with complete and incomplete artifact sets
- [ ] All scripts exit with correct exit codes
- [ ] All error messages are clear and actionable

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/tests/test_automation_scripts.py`

---

**Slice 2B Summary:**
- **Total tasks:** 5
- **Total effort:** ~9 hours (development + testing)
- **Time saved:** ~20 hours (across multiple workflow executions)
- **ROI:** 2.2x (pays for itself after first workflow execution)
- **Priority:** P2 (optional enhancement, not blocking)

---

## Slice 3: Step 7 - Write Tests Workflow

### S3-001: Create Test Design Artifact Template
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S2-001

**Description:** Jinja2 template for test design artifact.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/test-design-template.md`
- [ ] Sections: Test Strategy, Acceptance Criteria Mapping, RED State Validation, Escalations, Decision
- [ ] Placeholders: `{{feature_id}}`, `{{feature_name}}`, `{{timestamp}}`, `{{agent_name}}`
- [ ] File format: Markdown
- [ ] Example content in comments

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/test-design-template.md`

---

### S3-002: Implement /speckit.multi-agent.test Command
**Priority:** P0  
**Effort:** 2.5 hours  
**Dependencies:** S1-002, S3-001

**Description:** Command to spawn @test agent and create test design artifact.

**Acceptance Criteria:**
- [ ] Command created: `/speckit.multi-agent.test <feature-id>`
- [ ] Reads spec artifact for feature context
- [ ] Spawns @test agent via `/agents.spawn test-specialist`
- [ ] Passes test requirements and acceptance criteria to agent
- [ ] Agent writes test code
- [ ] Creates test design artifact from template
- [ ] Artifact path configurable via harness-tdd-config.yml

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/test.py`

---

### S3-003: Implement File Gate Validation
**Priority:** P0  
**Effort:** 1.5 hours  
**Dependencies:** S3-002

**Description:** Enforce only test file patterns in step 7.

**Acceptance Criteria:**
- [ ] File patterns configurable: `tests/**/*.py`, `__tests__/**/*.ts`, `*_test.go`
- [ ] Block non-test file changes
- [ ] Report violations with clear error messages
- [ ] Gate bypassed only with manual override + justification
- [ ] Violations logged in test design artifact

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/test.py`

---

### S3-004: Implement Failure Code Detection
**Priority:** P0  
**Effort:** 2 hours  
**Dependencies:** S3-002

**Description:** Parse test output for structured failure codes.

**Acceptance Criteria:**
- [ ] Valid RED codes detected: MISSING_BEHAVIOR, ASSERTION_MISMATCH
- [ ] Invalid codes detected: TEST_BROKEN, ENV_BROKEN
- [ ] Regex patterns configurable per test framework (pytest, Jest, Go)
- [ ] Structured output format: `{code: "MISSING_BEHAVIOR", location: "test_login.py:42", message: "..."}`
- [ ] Failures documented in RED State Validation section

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/lib/failure_parser.py`
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/test.py`

---

### S3-005: Implement Escalation Logic
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S3-004

**Description:** Escalate invalid failure codes to human.

**Acceptance Criteria:**
- [ ] If TEST_BROKEN detected → escalate (test code issue)
- [ ] If ENV_BROKEN detected → escalate (environment issue)
- [ ] Escalation documented in test design artifact
- [ ] Workflow halts until escalation resolved
- [ ] Escalation includes diagnostic information

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/test.py`

---

### S3-006: Test Step 7 Workflow End-to-End
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S3-001 through S3-005

**Description:** Verify complete test writing workflow.

**Acceptance Criteria:**
- [ ] `/speckit.multi-agent.test feat-123` executes successfully
- [ ] @test agent spawns with correct context
- [ ] Test files created in appropriate directory
- [ ] Tests fail (RED state)
- [ ] Test design artifact created with all sections
- [ ] File gate blocks implementation files
- [ ] Valid RED codes accepted, invalid codes escalate
- [ ] Workflow halts if escalation occurs

**Files Changed:**
- None (verification only)

---

## Slice 4: Step 8 - Implement Workflow

### S4-001: Create Implementation Notes Template
**Priority:** P2  
**Effort:** 45 min  
**Dependencies:** S2-001

**Description:** Jinja2 template for implementation notes artifact (optional).

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/implementation-notes-template.md`
- [ ] Sections: Implementation Approach, Files Modified, RED→GREEN Evidence, Refactoring, Integration Validation, Notes
- [ ] Placeholders: `{{feature_id}}`, `{{feature_name}}`, `{{agent_name}}`, `{{timestamp}}`
- [ ] Markdown format

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/implementation-notes-template.md`

---

### S4-002: Implement /speckit.multi-agent.implement Command
**Priority:** P0  
**Effort:** 2.5 hours  
**Dependencies:** S1-003, S4-001

**Description:** Command to spawn @make agent and create implementation.

**Acceptance Criteria:**
- [ ] Command created: `/speckit.multi-agent.implement <feature-id>`
- [ ] Reads test design artifact from step 7
- [ ] Spawns @make agent via `/agents.spawn dev-specialist`
- [ ] Passes test code and requirements to agent
- [ ] Agent writes implementation code
- [ ] Creates implementation notes artifact (if configured)
- [ ] Artifact path configurable

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/implement.py`

---

### S4-003: Implement TDD Entry Validation
**Priority:** P0  
**Effort:** 2 hours  
**Dependencies:** S4-002

**Description:** Enforce RED state before implementation.

**Acceptance Criteria:**
- [ ] Before implementation: run test command (configurable: `pytest`, `npm test`)
- [ ] Parse test output for pass/fail status
- [ ] If tests already pass → STOP (no implementation needed or tests broken)
- [ ] Document RED state evidence in implementation notes
- [ ] Test output captured with timestamps

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/lib/test_runner.py`
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/implement.py`

---

### S4-004: Implement GREEN State Validation
**Priority:** P0  
**Effort:** 1.5 hours  
**Dependencies:** S4-003

**Description:** Verify all tests pass after implementation.

**Acceptance Criteria:**
- [ ] After implementation: run test command
- [ ] All tests from step 7 must pass
- [ ] No new test failures introduced
- [ ] Document GREEN state evidence in implementation notes
- [ ] Evidence includes test output, coverage metrics

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/lib/test_runner.py`
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/implement.py`

---

### S4-005: Implement Integration Validation
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S4-004

**Description:** Run configurable integration checks.

**Acceptance Criteria:**
- [ ] Configurable command list: `[pytest, ruff check, mypy]`
- [ ] Each command runs independently
- [ ] Pass/fail status captured per command
- [ ] Results documented in integration validation section
- [ ] Workflow continues even if non-critical checks fail (warnings)

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/implement.py`

---

### S4-006: Test Step 8 Workflow End-to-End
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S4-001 through S4-005

**Description:** Verify complete implementation workflow.

**Acceptance Criteria:**
- [ ] `/speckit.multi-agent.implement feat-123` executes successfully
- [ ] Reads test design artifact from step 7
- [ ] TDD entry validation runs, verifies RED state
- [ ] If tests already pass, workflow halts with explanation
- [ ] @make agent implements code
- [ ] All tests pass (GREEN state)
- [ ] Integration validation runs
- [ ] Implementation notes artifact created (if enabled)
- [ ] RED→GREEN evidence captured

**Files Changed:**
- None (verification only)

---

## Slice 5: Step 9 - Review Workflow (Parallel Agents)

### S5-001: Create Arch Review Template
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S2-001

**Description:** Jinja2 template for architecture review artifact.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/arch-review-template.md`
- [ ] Sections: Safety Constraints, Architectural Concerns, Recommended Actions, Escalations, Verdict Rationale, Conflicts with @simplify, Review Cycle
- [ ] Placeholders: `{{feature_id}}`, `{{reviewer_name}}`, `{{verdict}}`, `{{cycle_count}}`
- [ ] Markdown format

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/arch-review-template.md`

---

### S5-002: Create Code Review Template
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S2-001

**Description:** Jinja2 template for code review artifact.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/code-review-template.md`
- [ ] Sections: Complexity Analysis, Code Duplication, Readability Assessment, Recommendations, Trade-Offs, Conflicts with @check, Verdict Rationale, Review Cycle
- [ ] Placeholders: `{{feature_id}}`, `{{reviewer_name}}`, `{{verdict}}`, `{{complexity_score}}`
- [ ] Markdown format

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/code-review-template.md`

---

### S5-003: Implement /speckit.multi-agent.review Command
**Priority:** P0  
**Effort:** 3 hours  
**Dependencies:** S1-004, S1-005, S5-001, S5-002

**Description:** Command to spawn parallel review agents.

**Acceptance Criteria:**
- [ ] Command created: `/speckit.multi-agent.review <feature-id>`
- [ ] Spawns @check and @simplify agents in parallel
- [ ] Passes implementation code and artifacts to both agents
- [ ] Agents review independently
- [ ] Creates arch review artifact from template
- [ ] Creates code review artifact from template
- [ ] Artifact paths configurable

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/review.py`

---

### S5-004: Implement Conflict Resolution Logic
**Priority:** P0  
**Effort:** 2 hours  
**Dependencies:** S5-003

**Description:** Resolve conflicts between @check and @simplify.

**Acceptance Criteria:**
- [ ] Cross-reference both review artifacts
- [ ] If @check identifies safety constraint → @simplify defers
- [ ] If @simplify suggests simplification violating @check → document conflict, keep @check decision
- [ ] Conflicts documented in both artifacts for transparency
- [ ] Conflict resolution logged

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/review.py`

---

### S5-005: Implement Review Cycle Management
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S5-003

**Description:** Track and limit review cycles.

**Acceptance Criteria:**
- [ ] Max review cycles configurable (default: 3)
- [ ] Cycle count tracked in review artifacts
- [ ] If reviews don't converge after max cycles → escalate to human
- [ ] Convergence detection: same findings as previous cycle
- [ ] Cycle history preserved in artifacts

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/review.py`

---

### S5-006: Implement Verdict Enforcement
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S5-004

**Description:** Enforce safety constraints from @check.

**Acceptance Criteria:**
- [ ] ACCEPTABLE verdict → workflow continues
- [ ] NEEDS_REVISION verdict → agent revises code
- [ ] BLOCKED verdict → workflow halts, escalates to human
- [ ] Verdicts non-bypassable (constitutional requirement)
- [ ] Escalation includes verdict rationale

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/review.py`

---

### S5-007: Test Step 9 Workflow End-to-End
**Priority:** P0  
**Effort:** 1.5 hours  
**Dependencies:** S5-001 through S5-006

**Description:** Verify complete review workflow.

**Acceptance Criteria:**
- [ ] `/speckit.multi-agent.review feat-123` executes successfully
- [ ] @check and @simplify agents spawn in parallel
- [ ] Both reviews complete independently
- [ ] Arch review artifact created with safety constraints validated
- [ ] Code review artifact created with complexity analysis
- [ ] Conflicts detected and documented
- [ ] Safety constraints non-bypassable (BLOCKED halts workflow)
- [ ] Review cycles tracked, max enforced

**Files Changed:**
- None (verification only)

---

## Slice 6: Step 10 - Commit & Workflow Summary

### S6-001: Create Workflow Summary Template
**Priority:** P0  
**Effort:** 1.5 hours  
**Dependencies:** S2-001

**Description:** Jinja2 template for workflow summary artifact.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/workflow-summary-template.md`
- [ ] Sections: Run Metadata, TDD Evidence, Review Outcomes, Unresolved Items, Artifacts Generated, PR Information, Manual Overrides, Metrics, Lessons Learned, Sign-Off
- [ ] Placeholders: `{{start_datetime}}`, `{{end_datetime}}`, `{{test_count}}`, `{{coverage}}`, `{{verdict}}`
- [ ] Markdown format

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/templates/workflow-summary-template.md`

---

### S6-002: Implement /speckit.multi-agent.commit Command
**Priority:** P0  
**Effort:** 2.5 hours  
**Dependencies:** S6-001

**Description:** Command to validate artifacts and create workflow summary.

**Acceptance Criteria:**
- [ ] Command created: `/speckit.multi-agent.commit <feature-id>`
- [ ] Validates all mandatory artifacts exist
- [ ] Creates workflow summary artifact from template
- [ ] Commits all artifacts and code to feature branch
- [ ] Updates spec lifecycle marker: `Status: Implemented`
- [ ] Artifact path configurable

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/commit.py`

---

### S6-003: Implement Artifact Validation
**Priority:** P0  
**Effort:** 1.5 hours  
**Dependencies:** S6-002

**Description:** Validate all mandatory artifacts exist and conform to templates.

**Acceptance Criteria:**
- [ ] File existence checks for mandatory artifacts (test_design, arch_review, code_review)
- [ ] Template schema validation (all sections present)
- [ ] Optional artifact checks (implementation_notes if configured)
- [ ] Workflow summary always created (mandatory)
- [ ] Validation failures halt workflow with clear error messages

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/lib/artifact_validator.py`
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/commit.py`

---

### S6-004: Implement Evidence Validation
**Priority:** P0  
**Effort:** 1.5 hours  
**Dependencies:** S6-003

**Description:** Validate RED→GREEN evidence exists.

**Acceptance Criteria:**
- [ ] RED state evidence present (test outputs with failure codes)
- [ ] GREEN state evidence present (test outputs with pass status)
- [ ] Integration validation results present
- [ ] Evidence timestamps validated (RED before GREEN)
- [ ] Evidence validation failures halt workflow

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/lib/artifact_validator.py`

---

### S6-005: Implement Git Commit Logic
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S6-004

**Description:** Commit all artifacts and code to feature branch.

**Acceptance Criteria:**
- [ ] Git add all artifacts: `git add docs/`
- [ ] Git add implementation code
- [ ] Commit message: `feat: [feature-id] workflow artifacts`
- [ ] Commit includes all mandatory artifacts
- [ ] Commit hash captured in workflow summary

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/commit.py`

---

### S6-006: Test Step 10 Workflow End-to-End
**Priority:** P0  
**Effort:** 1 hour  
**Dependencies:** S6-001 through S6-005

**Description:** Verify complete commit workflow.

**Acceptance Criteria:**
- [ ] `/speckit.multi-agent.commit feat-123` executes successfully
- [ ] All mandatory artifacts validated
- [ ] Workflow summary created with all sections
- [ ] All artifacts committed to feature branch
- [ ] Spec lifecycle updated to `Status: Implemented`
- [ ] Evidence requirements validated
- [ ] Command fails if mandatory artifacts missing

**Files Changed:**
- None (verification only)

---

## Slice 7: Grill-Me Integration (Interactive Planning)

### S7-001: Implement /speckit.multi-agent.plan Command
**Priority:** P1  
**Effort:** 2 hours  
**Dependencies:** None

**Description:** Command for interactive planning with grill-me skill.

**Acceptance Criteria:**
- [ ] Command created: `/speckit.multi-agent.plan --mode=interactive`
- [ ] Loads grill-me skill if available (via skill discovery API)
- [ ] Falls back to standard planning if grill-me not found
- [ ] Creates plan artifact with TDD-specific sections
- [ ] Plan linked to spec for traceability

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/plan.py`

---

### S7-002: Implement Grill-Me Skill Discovery
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S7-001

**Description:** Check if grill-me skill available before loading.

**Acceptance Criteria:**
- [ ] Search paths: `.claude/marketplace-skills/`, `~/.agents/skills/`
- [ ] If grill-me found → load and activate
- [ ] If not found → log warning, fall back to standard planning
- [ ] No hard dependency (graceful degradation)
- [ ] Skill path logged for debugging

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/plan.py`

---

### S7-003: Implement Interactive Q&A Session
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S7-002

**Description:** Run grill-me interactive session for test scenarios.

**Acceptance Criteria:**
- [ ] Prompts user with clarifying questions about test scenarios
- [ ] Explores edge cases interactively
- [ ] Documents decisions in plan artifact
- [ ] Q&A transcript captured
- [ ] Session timeout configurable

**Files Changed:**
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/commands/plan.py`

---

### S7-004: Test Interactive Planning End-to-End
**Priority:** P1  
**Effort:** 45 min  
**Dependencies:** S7-001 through S7-003

**Description:** Verify interactive planning workflow.

**Acceptance Criteria:**
- [ ] `/speckit.multi-agent.plan --mode=interactive` loads grill-me skill
- [ ] Interactive Q&A session runs for test scenarios
- [ ] Plan artifact created with decisions documented
- [ ] Fallback to standard planning if grill-me not found
- [ ] No errors if grill-me unavailable

**Files Changed:**
- None (verification only)

---

## Slice 8: Configuration & Customization

### S8-001: Create Configuration Documentation
**Priority:** P1  
**Effort:** 2 hours  
**Dependencies:** S2-002

**Description:** Comprehensive guide for harness-tdd-config.yml.

**Acceptance Criteria:**
- [ ] File created: `harness-tooling/docs/TDD-WORKFLOW-CONFIG.md`
- [ ] All configuration options documented
- [ ] Examples for common scenarios (minimal, full rigor, corporate)
- [ ] Artifact customization guide
- [ ] Gate customization guide
- [ ] Template override guide

**Files Changed:**
- Create: `harness-tooling/docs/TDD-WORKFLOW-CONFIG.md`

---

### S8-002: Implement Configuration Validation
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S2-002

**Description:** Validate configuration schema on extension load.

**Acceptance Criteria:**
- [ ] JSON Schema defined for harness-tdd-config.yml
- [ ] Schema validation runs on extension install
- [ ] Schema validation runs on config file change
- [ ] Validation errors include line numbers and fix suggestions
- [ ] Invalid config halts extension load

**Files Changed:**
- Create: `harness-tooling/.speckit-extensions/harness-tdd-workflow/lib/config_validator.py`
- Modify: `harness-tooling/.speckit-extensions/harness-tdd-workflow/hooks/install.sh`

---

### S8-003: Test Artifact Customization
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S8-001, S8-002

**Description:** Verify artifact path and mandatory flag customization.

**Acceptance Criteria:**
- [ ] Toggle implementation notes from optional to mandatory
- [ ] Change artifact paths to custom directories
- [ ] All artifacts land in configured paths
- [ ] Mandatory flags enforced (validation fails if missing)
- [ ] Config changes hot-reload without reinstall

**Files Changed:**
- None (verification only)

---

### S8-004: Test Template Override
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S8-001, S8-002

**Description:** Verify teams can override default templates.

**Acceptance Criteria:**
- [ ] Copy default template to custom location
- [ ] Edit custom template (add/remove sections)
- [ ] Update config to point to custom template
- [ ] Artifacts generated from custom template
- [ ] Template validation catches invalid Jinja2 syntax

**Files Changed:**
- None (verification only)

---

## Slice 9: Cleanup - Remove PRIES Plugin & Merge Phase 5

### S9-001: Archive PRIES Plugin
**Priority:** P1  
**Effort:** 30 min  
**Dependencies:** Slices 1-8 complete

**Description:** Move PRIES plugin to archive directory.

**Acceptance Criteria:**
- [ ] Directory created: `harness-tooling/archive/pries-plugin/`
- [ ] All PRIES extension files moved to archive
- [ ] Deprecation notice added to archived README
- [ ] Archive includes: extension.json, README.md, docs/
- [ ] Original PRIES directory deleted

**Files Changed:**
- Create: `harness-tooling/archive/pries-plugin/` (move from `.speckit-extensions/pries-workflow/`)
- Delete: `harness-tooling/.speckit-extensions/pries-workflow/`

---

### S9-002: Update Marketplace README
**Priority:** P1  
**Effort:** 30 min  
**Dependencies:** S9-001

**Description:** Remove PRIES references from marketplace documentation.

**Acceptance Criteria:**
- [ ] `harness-tooling/README.md` no longer references PRIES
- [ ] Migration path documented (PRIES → harness-tdd-workflow)
- [ ] Archive location noted for historical reference
- [ ] New dual-plugin architecture explained

**Files Changed:**
- Modify: `harness-tooling/README.md`

---

### S9-003: Review Phase 5 Worktree Changes
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S9-001

**Description:** Audit harness-sandbox phase 5 worktree for completable work.

**Acceptance Criteria:**
- [ ] List all changed files in phase 5 worktree
- [ ] Identify completed work (documentation, configs)
- [ ] Identify incomplete work (code in progress)
- [ ] Document merge strategy (what to keep, what to discard)
- [ ] Conflicts identified and resolution planned

**Files Changed:**
- None (audit only)

---

### S9-004: Merge Phase 5 Worktree
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S9-003

**Description:** Merge completed parts of phase 5 into main branch.

**Acceptance Criteria:**
- [ ] Checkout main branch in harness-sandbox
- [ ] Merge completed documentation updates
- [ ] Merge completed configuration changes
- [ ] Resolve conflicts with updated docs
- [ ] Discard incomplete code
- [ ] Commit merge with clear message

**Files Changed:**
- Modify: `harness-sandbox/docs/` (merge updates)
- Modify: `harness-sandbox/workspace-template/` (merge configs)

---

### S9-005: Close Phase 5 Worktree
**Priority:** P1  
**Effort:** 15 min  
**Dependencies:** S9-004

**Description:** Remove phase 5 worktree after merge.

**Acceptance Criteria:**
- [ ] Worktree removed: `git worktree remove phase5-pries-workflow`
- [ ] Branch deleted (if no longer needed): `git branch -d phase5-pries-workflow`
- [ ] Worktree directory cleaned up
- [ ] No orphaned files remain

**Files Changed:**
- None (cleanup only)

---

### S9-006: Document PRIES Deprecation in ADR
**Priority:** P2  
**Effort:** 45 min  
**Dependencies:** S9-001, S9-004

**Description:** Architectural Decision Record for PRIES deprecation.

**Acceptance Criteria:**
- [ ] ADR created: `harness-sandbox/architecture/adrs/###-deprecate-pries-plugin.md`
- [ ] Context: Why PRIES deprecated (superpowers dependency, rigidity)
- [ ] Decision: Dual-plugin architecture chosen
- [ ] Consequences: Migration path, team impact
- [ ] Status: Accepted

**Files Changed:**
- Create: `harness-sandbox/architecture/adrs/###-deprecate-pries-plugin.md`

---

## Slice 10: Update Requirements, Tasks, Roadmap Docs

### S10-001: Update Technical-Requirements.md
**Priority:** P1  
**Effort:** 2 hours  
**Dependencies:** S9-006

**Description:** Replace PRIES requirements with dual-plugin requirements.

**Acceptance Criteria:**
- [ ] Remove all PRIES-specific requirements
- [ ] Add REQ-AGENT-* requirements (harness-agents plugin)
- [ ] Add REQ-WORKFLOW-* requirements (harness-tdd-workflow extension)
- [ ] Add REQ-ARTIFACT-* requirements (5 artifacts)
- [ ] Add REQ-GATE-* requirements (TDD, review, evidence)
- [ ] Update traceability matrix
- [ ] Version bump: v1.0 → v2.0

**Files Changed:**
- Modify: `harness-sandbox/Technical-Requirements.md`

---

### S10-002: Update Task-List.md
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S10-001

**Description:** Replace PRIES tasks with dual-plugin tasks.

**Acceptance Criteria:**
- [ ] Remove PRIES installation tasks
- [ ] Add harness-agents installation tasks (from Slice 1)
- [ ] Add harness-tdd-workflow installation tasks (from Slice 2)
- [ ] Add workflow tasks (from Slices 3-6)
- [ ] Update testing tasks (from Slices 3-6)
- [ ] Update dependencies and acceptance criteria

**Files Changed:**
- Modify: `harness-sandbox/Task-List.md`

---

### S10-003: Update Roadmap.md
**Priority:** P1  
**Effort:** 1.5 hours  
**Dependencies:** S10-002

**Description:** Replace PRIES phases with dual-plugin phases.

**Acceptance Criteria:**
- [ ] Replace PRIES phases with 11 vertical slices
- [ ] Update dependencies (multi-agent workflow depends on agent definitions)
- [ ] Update success criteria (5 artifacts created, quality gates enforced)
- [ ] Update effort estimates (35-42 hours)
- [ ] Update parallelization opportunities
- [ ] Update critical path

**Files Changed:**
- Modify: `harness-sandbox/Roadmap.md`

---

### S10-004: Cross-Reference Validation
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S10-001, S10-002, S10-003

**Description:** Verify all cross-references between docs updated.

**Acceptance Criteria:**
- [ ] Grep for "PRIES" in all docs (should be zero matches)
- [ ] Grep for "superpowers" in workflow docs (should be zero matches outside references section)
- [ ] All REQ-ID references valid
- [ ] All task IDs valid
- [ ] All file paths accurate

**Files Changed:**
- None (verification only)

---

## Slice 11: Remove Superpowers & Update Sandbox Docs

### S11-001: Audit Superpowers References
**Priority:** P1  
**Effort:** 30 min  
**Dependencies:** S10-004

**Description:** Find all superpowers mentions in harness-sandbox docs.

**Acceptance Criteria:**
- [ ] Grep search: `rg -i superpowers harness-sandbox/docs/`
- [ ] List all files with superpowers references
- [ ] Categorize: installation, workflow, skills, commands
- [ ] Document removal strategy per category

**Files Changed:**
- None (audit only)

---

### S11-002: Update Sandbox CLAUDE.md
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S11-001

**Description:** Remove superpowers, add dual-plugin documentation.

**Acceptance Criteria:**
- [ ] Remove superpowers from common commands
- [ ] Add dual-plugin installation instructions
- [ ] Update workflow description (PRIES → harness-tdd-workflow)
- [ ] Document agent definitions in `.claude/agents/`
- [ ] Update marketplace integration section

**Files Changed:**
- Modify: `harness-sandbox/CLAUDE.md`

---

### S11-003: Update Sandbox README
**Priority:** P1  
**Effort:** 45 min  
**Dependencies:** S11-002

**Description:** Remove superpowers prerequisites, add dual-plugin.

**Acceptance Criteria:**
- [ ] Remove superpowers from prerequisites
- [ ] Add harness-agents and harness-tdd-workflow to marketplace section
- [ ] Update quickstart to use dual-plugin workflow
- [ ] Update onboarding instructions

**Files Changed:**
- Modify: `harness-sandbox/README.md`

---

### S11-004: Update Sandbox Installation Guide
**Priority:** P1  
**Effort:** 30 min  
**Dependencies:** S11-002

**Description:** Replace superpowers installation with dual-plugin.

**Acceptance Criteria:**
- [ ] Remove superpowers installation steps
- [ ] Add harness-agents installation steps
- [ ] Add harness-tdd-workflow installation steps
- [ ] Update verification steps

**Files Changed:**
- Modify: `harness-sandbox/docs/sandbox-install.md`

---

### S11-005: Final Documentation Review
**Priority:** P1  
**Effort:** 1 hour  
**Dependencies:** S11-001 through S11-004

**Description:** Comprehensive review of all documentation changes.

**Acceptance Criteria:**
- [ ] No superpowers references in harness-sandbox docs (except historical/archive)
- [ ] Dual-plugin architecture consistently documented
- [ ] All installation guides accurate
- [ ] All workflow guides accurate
- [ ] All cross-references valid

**Files Changed:**
- None (verification only)

---

## Task Summary Statistics

| Slice | Total Tasks | P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low) |
|-------|-------------|---------------|-----------|-------------|----------|
| Slice 1: Foundation | 9 | 6 | 3 | 0 | 0 |
| Slice 2: SpecKit Extension | 4 | 3 | 1 | 0 | 0 |
| Slice 2B: Automation Scripts | 5 | 0 | 0 | 5 | 0 |
| Slice 3: Write Tests | 6 | 5 | 1 | 0 | 0 |
| Slice 4: Implement | 6 | 4 | 2 | 0 | 0 |
| Slice 5: Review | 7 | 5 | 2 | 0 | 0 |
| Slice 6: Commit | 6 | 5 | 1 | 0 | 0 |
| Slice 7: Grill-Me | 4 | 0 | 4 | 0 | 0 |
| Slice 8: Configuration | 4 | 0 | 4 | 0 | 0 |
| Slice 9: Cleanup | 6 | 0 | 5 | 1 | 0 |
| Slice 10: Update Docs | 4 | 0 | 4 | 0 | 0 |
| Slice 11: Remove Superpowers | 5 | 0 | 5 | 0 | 0 |
| **TOTAL** | **66** | **28** | **32** | **6** | **0** |

**Note:** Slice 2B (Automation Scripts) is optional but highly recommended (2.2x ROI, saves ~20 hours).

---

## Completion Tracking

**Slice 1 (Foundation)**: [ ] 0/9  
**Slice 2 (SpecKit Extension)**: [ ] 0/4  
**Slice 2B (Automation Scripts)**: [ ] 0/5 (optional)  
**Slice 3 (Write Tests)**: [ ] 0/6  
**Slice 4 (Implement)**: [ ] 0/6  
**Slice 5 (Review)**: [ ] 0/7  
**Slice 6 (Commit)**: [ ] 0/6  
**Slice 7 (Grill-Me)**: [ ] 0/4  
**Slice 8 (Configuration)**: [ ] 0/4  
**Slice 9 (Cleanup)**: [ ] 0/6  
**Slice 10 (Update Docs)**: [ ] 0/4  
**Slice 11 (Remove Superpowers)**: [ ] 0/5

**Overall Progress**: [ ] 0/66 (0%)  
**Core Progress** (excluding Slice 2B): [ ] 0/61 (0%)

---

## Related Documents

- [PLAN-Multi-Agent-TDD-Implementation.md](PLAN-Multi-Agent-TDD-Implementation.md) — Implementation plan (vertical slices)
- [ROADMAP-Multi-Agent-TDD.md](ROADMAP-Multi-Agent-TDD.md) — Task dependencies and execution strategy
- [PRD-Multi-Agent-TDD-Workflow.md](PRD-Multi-Agent-TDD-Workflow.md) — Product requirements
- [CONSTITUTION-Multi-Agent-TDD.md](CONSTITUTION-Multi-Agent-TDD.md) — Constitutional principles
