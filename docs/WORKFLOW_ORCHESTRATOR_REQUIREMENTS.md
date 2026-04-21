# Workflow Orchestrator Tool: Complete Feature Requirements

**Session Date:** 2026-04-22
**Status:** Final specification from comprehensive tool evaluation and comparison

---

## Core Requirements

### 1. Licensing & Openness

- Free and open source
- Apache 2.0, MIT, or equivalent license preferred

### 2. Multi-CLI Support

Support or extensibility for:

- Claude Code (primary)
- Gemini CLI
- OpenCode

### 3. Workflow Definition

- **Custom workflows:** Define static, manual workflows (not auto-generated/pre-built)
- **Manual chaining:** Explicitly compose steps and agent handoffs
- **Shareable format:** Export as plugins for all supported CLI tools
- Workflow node defintions support usage of Agent CLI skills according to https://agentskills.io/home

### 4. Per-Workflow-Step Agent Configuration

Each step can specify:

- **Agent/Model assignment:** Which model/agent handles this step
- **Skill access:** Which skills/tools are available to this step
- **MCP servers:** Which MCP servers are accessible
- **Hooks:** Which lifecycle hooks can execute
- **Permission model:**
  - Write access constraints (e.g., test agent: `**/test_*.py` only)
  - Bash scope (sandboxed vs. unrestricted)
  - External API access (Linear, GitHub, etc.)
  - File system scope (read-only, specific directories, etc.)
- **Convergence gates:** When to escalate vs. retry (e.g., 3 iterations max)
- **Parallel review logic:** Multiple reviewers in parallel, fresh reviewers on rework

### 5. Permission/Constraint Enforcement Model

- **Hard enforcement:** Not prompt-based soft enforcement
- **Per-step constraints:** Different steps have different permissions
- **File-pattern gates:** e.g., post-step validation ensures only `**/test_*.py` created by test agent
- **Sandboxing:** Worktree isolation, container isolation, or WASM per agent
- **Independent validation:** Orchestrator validates independently (never trusts agent self-report)
- **Blocking gates:** No path from FAIL to next step (e.g., pre-push hooks block on lint/type failure)

### 6. Plugin Creation & Distribution

- Create plugins for Claude Code, Gemini CLI, Codex CLI
- Plugins include:
  - Hooks (proper formatting)
  - Skills (SKILL.md format)
  - Agents (Agent.md/CLAUDE.md formatting)
- Plugins are version-controlled and distributable (marketplace or manual)

---

## Workflow Features

### 7. Loop/Iteration Support

**Explicit loop syntax required:**

- Parallel iteration with fan-out/fan-in patterns
- Convergence detection (e.g., "same findings twice = stop early")
- Escalation logic (e.g., 3 iterations → escalate to human)
- Conditional looping (while/until patterns)
- Max iteration limits with fail-safe

**Example:**

```
Phase 5: Parallel review (Check + Simplify) — max 3 cycles with convergence detection
  ↓ [same findings twice = stop early]
Phase 6: Implementation
```

### 8. Skill/Tool Assignment Per Step

Different workflow steps have access to different skills:

- **Per-step tool selection** (not just per-agent)
- **Explicit skill binding** to specific workflow steps
- **Skills discoverable** and loadable on-demand (not all loaded at startup)

**Example:**

```
Step: Plan
  Skills: /code:analyze, /code:plan

Step: Write Tests
  Skills: /code:write (test files), /code:validate

Step: Implement
  Skills: /code:write (source files), /code:edit, /code:test

Step: Review
  Skills: /code:analyze, /code:review (read-only)
```

### 9. Validation Gates

Per-step validation requirements:

- Independent validation (orchestrator, not agent self-report)
- File pattern enforcement (e.g., only `**/test_*.py` created by test agent)
- Blocking state transitions (no FAIL → next step paths)
- Pre-step gates (spec validation, preconditions)
- Pre-push gates (linting, type checking, coverage thresholds)

**Example:**

```
Step 8: Implement
  Output: Source code changes

Gate: Validate
  ✓ Type checking passes
  ✓ Tests pass (RED tests before implementation)
  ✓ File patterns correct (test_*.py for tests, src/*.py for impl)
  ✓ Coverage threshold met

If FAIL: Escalate to review or retry
If PASS: Proceed to Step 9
```

### 10. Orchestration Patterns

- Sequential execution with clear handoffs
- Parallel execution with result aggregation
- Conditional branching (if/then/else)
- Recursive/hierarchical decomposition
- Cross-agent message passing (for Agent Teams)

---

## File Discovery & Directory Scoping (Critical Requirement)

### 11. File-Based Skill Discovery

**Mirrors Claude Code's SKILL.md loading mechanism:**

- Tool discovers skills by scanning directories for `SKILL.md` files
- Glob pattern support: `**/SKILL.md`, `skills/*/SKILL.md`, `internal-*.md`, etc.
- Progressive loading strategy:
  1. **Advertise (~100 tokens):** Inject skill names + descriptions at startup
  2. **Load (on-demand):** Agent calls `load_skill` → full SKILL.md content
  3. **Read resources (on-demand):** Agent calls `read_skill_resource` → supplementary files only when referenced
  4. **Execute (on-demand):** Agent calls `run_skill_script` → scripts execute when invoked

**Example:**

```
Startup: "You have skills: code-review, test-writer, implementer, reviewer"
         (~200 tokens total for 10 skills)

During execution:
  Agent requests: "Load code-review skill"
  → Full SKILL.md content loaded (~2-5KB)

  Agent reads: "I need the POLICY_FAQ.md reference"
  → Only that file loaded (~1KB)

  Agent runs: "Execute validate.py with file=report.json"
  → Script executed as subprocess
```

### 12. Directory Scoping with Priority System

**Multi-level discovery with clear priority:**

```
Priority order (highest → lowest):
  1. .project/skills/*/SKILL.md           (project-local, committed to git)
  2. .team/skills/*/SKILL.md              (team-shared, optional)
  3. ~/.config/skills/*/SKILL.md          (user-global)
  4. /usr/local/skills/*/SKILL.md         (system-global, optional)

When skill names conflict: First match wins (project level overrides global)
```

**Directory structure example:**

```
my-project/
  .project/
    skills/
      code-review/SKILL.md        # Project-specific (highest priority)
      test-writer/SKILL.md
      custom-deploy/SKILL.md

  workflows/
    tdd-workflow.yaml             # References .project/skills/*

~/.config/
  skills/
    generic-linter/SKILL.md       # User-global (fallback)
    code-formatter/SKILL.md
```

**Wildcard patterns for discovery:**

- `code-*` → matches code-review, code-analyze, etc.
- `test-*` → matches test-writer, test-reviewer, etc.
- `internal-*` → matches internal-deploy, internal-audit, etc.
- `**` → matches all nested directories

### 13. Agent Access Control via File Patterns

Agents specify which skill directories/files they can access:

**Permission control options:**

```yaml
# Option 1: Skill wildcard patterns
agent: code_reviewer
  skills: ["code-*", "!code-write"]    # Allow code-* except code-write

# Option 2: File type restrictions
agent: test_writer
  resource_extensions: [".md", ".txt"]  # Only these file types readable
  script_extensions: [".py"]            # Only Python scripts executable

# Option 3: Directory scoping
agent: implementer
  skill_directories:
    - .project/skills/impl-*            # Only implementation skills
  resource_directories: ["references"]  # Only access references/ folder

# Option 4: Approval gates
agent: deployer
  scripts:
    require_approval: true              # Require human approval before execution
    timeout_seconds: 300
    resource_limits:
      memory_mb: 512
      max_runtime_seconds: 120
```

---

## Anti-Patterns (What NOT to Build)

### 14. No need for Pre-Defined Agents

- Do not include 18 "specialist agent personas"
- Do not auto-assign agents to steps
- Users define custom agents from scratch

### 15. No need for Pre-Defined Skill Sets

- Do not bundle 13+ pre-built skills
- Do not auto-load common skills
- Users define custom skills

### 16. No need for Pre-Defined Chains/Workflows

- Do not include ready-made workflow templates
- Do not auto-generate workflows from task descriptions
- Users manually define each workflow step

### 17. No need for Self-Learning/Auto-Improving

- Do not extract patterns from code reviews
- Do not learn from PR feedback
- Workflows are static once defined and shared
- Same workflow runs consistently every time

---

## Concrete Example: TDD Orchestration Workflow

This example demonstrates the complete feature set:

### Workflow Definition (YAML-style)

```yaml
name: tdd-development
description: Test-driven development with parallel reviews and convergence gates
phases: 11

phase_1:
  name: Setup
  agent: orchestrator
  steps:
    - verify_repo_structure
    - create_worktree
  skills: [/code:validate, /code:setup]
  no_write_access: true

phase_2:
  name: Fetch Issue
  agent: orchestrator
  steps:
    - fetch_issue_from_linear
    - parse_spec
  skills: [/code:analyze, /linear:read]
  external_apis: [linear]

phase_3:
  name: Parallel Review (Design & Simplify)
  agent: parallel_reviewers
  concurrent_agents: 2
  convergence:
    max_iterations: 3
    convergence_rule: "same_findings_twice"
  agents:
    - reviewer_design:
        model: claude-opus
        skills: [/code:analyze, /code:review]
        constraints:
          write_access: false
    - reviewer_simplify:
        model: claude-opus
        skills: [/code:analyze, /code:review]
        constraints:
          write_access: false
  output_gate:
    approval_rule: "all_reviewers_approve"

phase_4:
  name: Decompose Work
  agent: architect
  model: claude-opus
  skills: [/code:analyze, /code:plan]
  output: work_units.json
  constraints:
    write_access: false

phase_5:
  name: Test-First Loop (per work unit)
  loop:
    type: fan_out
    items: work_units.json
    max_parallel: 2

  phase_5a:
    name: Write Failing Tests
    agent: test_writer
    model: claude-sonnet-4-6
    skills: [/code:write, /code:validate]
    constraints:
      write_access: "test_*.py, tests/**"  # File pattern constraint
      bash_scope: "sandboxed_pytest"
      external_apis: []
    output_gate:
      validation: "pytest_shows_red"
      file_pattern_check: "only_test_files_created"

  phase_5b:
    name: Implement to Green
    agent: implementer
    model: claude-sonnet-4-6
    skills: [/code:write, /code:edit, /code:test]
    constraints:
      write_access: "src/**, lib/**"      # Only source/lib files
      bash_scope: "sandboxed_no_pip_git"  # Can't install/change git
      external_apis: []
    output_gate:
      validation: "pytest_shows_green"
      file_pattern_check: "only_source_files_created"
      coverage_threshold: ">= 95%"

phase_6:
  name: Final Review (Adversarial)
  agent: adversarial_reviewer
  model: claude-opus
  skills: [/code:analyze, /code:review, /code:test]
  constraints:
    write_access: false
  convergence:
    max_iterations: 1
    escalation_rule: "if_issues_found_escalate_to_human"

phase_7:
  name: Integration Tests
  agent: test_runner
  model: claude-opus
  skills: [/code:test, /code:validate]
  constraints:
    bash_scope: "sandboxed_pytest"
  output_gate:
    validation: "all_tests_pass"
    coverage_threshold: ">= 95%"

phase_8:
  name: Commit & PR
  agent: orchestrator
  skills: [/code:commit, /code:pr_create]
  constraints:
    write_access: "git_operations_only"
  gates:
    pre_commit:
      - "lint_passes"
      - "type_check_passes"
      - "tests_pass"
      - "coverage_threshold_met"
    pre_push:
      - "ci_checks_pass"
```

### Skill Directory Structure

```
my-tdd-workflow/
  .project/
    skills/
      code-review/SKILL.md
        - description: Review code for best practices
        - resources/: [POLICY.md, CHECKLIST.md]
        - scripts/: []

      test-writer/SKILL.md
        - description: Write test specifications
        - resources/: [TEST_PATTERNS.md]
        - scripts/: [validate_tests.py]

      implementer/SKILL.md
        - description: Implement code to pass tests
        - resources/: [DESIGN_PATTERNS.md, ARCHITECTURE.md]
        - scripts/: [run_tests.py, check_coverage.py]

  workflows/
    tdd-workflow.yaml

  agents/
    test_writer.md
    implementer.md
    reviewer.md
```

### Agent Definition Example

```markdown
# .project/agents/test_writer.md

---
description: Writes failing test specifications
model: claude-sonnet-4-6
permissions:
  skills: ["/code:write", "/code:validate"]
  write_access_pattern: "test_*.py"
  bash_scope: "sandboxed_pytest"
  external_apis: []
---

You are a test architecture specialist. Your responsibilities:

1. Read the feature specification
2. Design comprehensive test scenarios covering:
   - Happy path
   - Edge cases
   - Error conditions
   - Performance bounds
3. Write failing test stubs that will be implemented next

When writing tests:
- Use the TEST_PATTERNS.md resource for example patterns
- Ensure tests fail initially (RED state)
- Classify failures by type (assertion, exception, timeout)
- Document assumptions and expected behaviors

Available skills:
- /code:write (write test files)
- /code:validate (validate test syntax)
```

### Skill Definition Example

```markdown
# .project/skills/test-writer/SKILL.md

---
name: test-writer
description: Design and write comprehensive test specifications for features. Use when starting TDD cycle, writing failing tests, or designing test architecture.
compatibility: Requires Python 3.10+, pytest
metadata:
  author: team-qa
  version: "2.1"
---

# Test Writer Skill

## When to Use
- Starting a new feature implementation (TDD cycle)
- Writing failing test specifications
- Designing test scenarios and edge cases

## Process

### 1. Read the Feature Specification
- Understand requirements from issue
- Identify acceptance criteria
- Note performance/security constraints

### 2. Design Test Scenarios
Reference TEST_PATTERNS.md for examples. Design tests covering:
- **Happy path:** Standard use case
- **Edge cases:** Boundary conditions, empty input, max size
- **Error handling:** Invalid input, missing dependencies, timeouts
- **Performance:** Execution time, memory usage

### 3. Write Failing Tests
Create test file with pattern: `test_<feature>.py`

```python
# test_user_auth.py
import pytest
from src.auth import authenticate

def test_successful_login():
    """Happy path: valid credentials return user object."""
    user = authenticate(email="test@example.com", password="correct")
    assert user is not None
    assert user.email == "test@example.com"

def test_invalid_password():
    """Edge case: invalid password raises AuthError."""
    with pytest.raises(AuthError):
        authenticate(email="test@example.com", password="wrong")

def test_empty_email():
    """Edge case: empty email raises ValidationError."""
    with pytest.raises(ValidationError):
        authenticate(email="", password="password")
```
