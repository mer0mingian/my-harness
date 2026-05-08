---
description: "Implement feature code (RED → GREEN)"
agent: dev-specialist
tools:
  - 'filesystem/read'
  - 'filesystem/write'
  - 'bash/execute'
scripts:
  validate_red: scripts/validate_red_state.py
  validate_green: scripts/validate_green_state.py
  integration_checks: scripts/run_integration_checks.py
exit_codes:
  0: "Success - GREEN state achieved, integration checks passed"
  1: "Validation failure - RED state invalid, GREEN not achieved, or critical integration failures"
  2: "Escalation required - tests broken (BROKEN state) or regression detected"
---

# Implementation Workflow (Multi-Agent TDD Step 8)

This command prepares context for the @dev-specialist agent to implement code that makes tests pass (RED → GREEN transition). It validates entry conditions, creates implementation notes artifact, and manages post-implementation validation.

## Prerequisites

- Test design artifact exists from Step 7 (test command)
- Tests are in valid RED state (failing with MISSING_BEHAVIOR or ASSERTION_MISMATCH)
- Test framework (pytest) configured
- Python environment with pytest available
- Configuration file at `.specify/harness-tdd-config.yml` (optional, uses defaults if missing)

## Two-Phase Execution Model

### Phase 1: RED State Entry (default behavior)

**Purpose**: Prepare implementation context and validate RED state entry conditions

**Command**: `/speckit.multi-agent.implement $FEATURE_ID [--project-root PATH]`

### Phase 2: GREEN State Validation (post-implementation)

**Purpose**: Validate implementation success and run integration checks

**Command**: `/speckit.multi-agent.implement $FEATURE_ID --validate-green [--project-root PATH]`

## User Input

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--project-root PATH`: (Optional) Project root directory (default: current directory)
- `--validate-green`: (Optional) Skip RED validation, validate GREEN state instead

## Phase 1 Workflow: RED State Entry

### Step 1: Load Configuration

Load harness configuration from `.specify/harness-tdd-config.yml` or use defaults.

**Default configuration includes**:
- Agent names (dev-specialist for implementation)
- Test framework settings (pytest, file patterns)
- Artifact paths and templates
- Integration check commands
- `workflow.agent_timeout` — agent task timeout in minutes (default: 30 if key missing)

### Step 2: Find Test Design Artifact

Search for test design artifact from Step 7:

Uses `artifact_paths.find_existing()` to search configured locations.

**Default search paths**:
- `docs/features/${FEATURE_ID}/test-design-${FEATURE_ID}.md`
- `docs/tests/test-design/test-design-${FEATURE_ID}.md`
- `.specify/artifacts/${FEATURE_ID}/test-design-${FEATURE_ID}.md`

**If not found**: ❌ Exit 1 with error - test design required before implementation

**On success**: Continue to Step 3

### Step 3: Find Spec Artifact (Optional)

Search for feature spec in common locations:

1. `docs/features/${FEATURE_ID}.md`
2. `docs/specs/${FEATURE_ID}-spec.md`
3. `docs/specs/${FEATURE_ID}.md`
4. `.specify/specs/${FEATURE_ID}.md`

**If not found**: Continue without spec (optional resource)

**On success**: Include spec path in agent context

### Step 4: Prepare Agent Context

Build context bundle for @dev-specialist agent:

**Context includes**:
- `feature_id`: Feature identifier
- `test_design_path`: Path to test design artifact (for agent to read)
- `test_file_patterns`: List of test file patterns from config
- `spec_path`: Path to spec artifact (if available)

**Instructions for agent**:
1. Read test design artifact at `test_design_path`
2. Read spec artifact at `spec_path` (if provided)
3. Implement code to make tests pass
4. DO NOT modify test files (unless fixing broken tests)
5. Focus on minimal implementation to achieve GREEN state

### Step 5: Validate RED State Entry

Execute RED state validation:

```bash
python3 scripts/validate_red_state.py ${FEATURE_ID} --project-root ${PROJECT_ROOT}
```

**Expected output**: JSON with validation results

**Exit codes**:
- 0: Valid RED state → Continue to Step 6
- 1: Invalid state (GREEN or no failures) → ❌ Exit 1 with validation failure
- 2: Broken tests → ❌ Exit 2 with escalation

**Validation checks**:
- At least one test failed
- All failures use valid RED codes (MISSING_BEHAVIOR, ASSERTION_MISMATCH, AssertionError, NameError, AttributeError)
- No TEST_BROKEN, ENV_BROKEN, SyntaxError, ImportError, or ModuleNotFoundError

**RED State Evidence Structure**:
```python
{
    'state': 'RED',  # or 'GREEN', 'BROKEN'
    'validation_passed': True,  # or False
    'timestamp': '2024-01-01T12:00:00Z',
    'message': 'Valid RED state confirmed',
    'evidence': {
        'total_tests': 5,
        'passed': 0,
        'failed': 5,
        'errors': 0
    },
    'output': '... pytest output ...'
}
```

### Step 6: Create Implementation Notes Artifact

Generate implementation notes artifact from template:

**Template location**:
- Custom: `.specify/templates/implementation-notes-template.md`
- Built-in: `templates/implementation-notes-template.md`

**Artifact output path** (from config):
- Default: `docs/features/${FEATURE_ID}/impl-notes-${FEATURE_ID}.md`
- Configurable via `artifacts.impl_notes.path` in config

**Template variables**:
- `feature_id`: Feature identifier
- `feature_name`: Extracted from feature_id (title-cased)
- `agent_name`: Implementation agent name (dev-specialist)
- `timestamp`: ISO 8601 UTC timestamp
- `status`: 'draft' (will be updated to 'complete' after GREEN validation)
- `red_state_evidence`: RED validation result from Step 5

**Artifact sections**:
1. Feature metadata (ID, name, timestamp, status, agent)
2. RED→GREEN Evidence
   - RED State (Before Implementation) - from Step 5 validation
   - GREEN State (After Implementation) - placeholder, filled in Phase 2
3. Integration Validation Results - placeholder, filled in Phase 2
4. Notes - for developer to document implementation approach
5. Refactoring - for tracking refactoring steps after GREEN

**On success**: ✓ Print artifact path

### Step 7: Print Agent Invocation Instructions

Print instructions for next step (agent invocation):

```
==========================================================
NEXT STEP: Invoke implementation agent
==========================================================

Agent: dev-specialist
Instructions: Implement code to make tests pass
Test design: /path/to/test-design-feat-123.md
Feature spec: /path/to/feat-123.md  # if available
Output artifact: /path/to/impl-notes-feat-123.md

NOTE: Agent will read test files from patterns:
  - tests/**/*.py
  - **/test_*.py
  - **/*_test.py
```

**Agent timeout instruction**:
Complete this task within ${agent_timeout} minutes (default: 30). If you cannot achieve GREEN state within the time limit, output partial results with a summary of completed work, then escalate to human with what remains and the current test state.

**Phase 1 Exit**: Exit 0 (success - context prepared, artifact created)

## Phase 2 Workflow: GREEN State Validation

Invoked with `--validate-green` flag after agent completes implementation.

### Step 1: Find Implementation Notes Artifact

Search for existing implementation notes artifact created in Phase 1.

**If not found**: ❌ Exit 1 with error - run without --validate-green first

**On success**: Read artifact to extract baseline test count

### Step 2: Extract Baseline Test Count

Parse implementation notes artifact to find baseline test count from RED State section:

```markdown
### RED State (Before Implementation)
...
Total tests: 5
```

**If found**: Use as baseline for regression detection in Step 3

**If not found**: Continue without baseline (regression check skipped)

### Step 3: Validate GREEN State

Execute GREEN state validation:

```bash
python3 scripts/validate_green_state.py ${FEATURE_ID} --project-root ${PROJECT_ROOT} --baseline-count ${BASELINE_COUNT}
```

**Expected output**: JSON with validation results

**Exit codes**:
- 0: Valid GREEN state → Continue to Step 4
- 1: Invalid state (still RED or no tests) → ❌ Exit 1 with validation failure
- 2: Regression detected → ❌ Exit 2 with escalation

**Validation checks**:
- All tests passed (no failures)
- Test count matches or exceeds baseline (no test deletion)
- No TEST_BROKEN, ENV_BROKEN, or other error codes
- Optional coverage metrics (if available)

**GREEN State Evidence Structure**:
```python
{
    'state': 'GREEN',  # or 'RED', 'BROKEN'
    'validation_passed': True,  # or False
    'timestamp': '2024-01-01T12:30:00Z',
    'message': 'Valid GREEN state confirmed',
    'evidence': {
        'total_tests': 5,
        'passed': 5,
        'failed': 0,
        'errors': 0
    },
    'output': '... pytest output ...',
    'coverage': {  # optional
        'found': True,
        'percentage': 95.5,
        'statements': 200,
        'missing': 9
    }
}
```

**Regression Detection**:
If baseline count available and current test count < baseline:
- Exit 2 (escalation)
- Error message: "Regression: test count decreased from {baseline} to {current}"

### Step 4: Run Integration Checks

Execute configured integration checks:

```bash
# Example integration checks from config
ruff check src/
mypy src/
```

**Check results structure**:
```python
[
    {
        'name': 'ruff',
        'command': 'ruff check src/',
        'exit_code': 0,
        'passed': True,
        'output': '... command output ...',
        'critical': False
    },
    {
        'name': 'mypy',
        'command': 'mypy src/',
        'exit_code': 1,
        'passed': False,
        'output': '... error output ...',
        'critical': False
    }
]
```

**Critical vs. Non-Critical Checks**:
- **Critical** (`critical: true`): Failure blocks workflow (Exit 1)
- **Non-Critical** (`critical: false`): Failure is warning only (Continue)

**Default integration checks** (from config):
- ruff (code linter) - non-critical
- mypy (type checker) - non-critical

**Check execution**:
- Run each check in project root directory
- 60 second timeout per check
- Capture stdout + stderr
- Print status: ✓ PASS, ⚠ FAIL (warning), ✗ FAIL (CRITICAL), ✗ TIMEOUT

**If critical failures**: ❌ Exit 1 with critical check failures

**On success**: Continue to Step 5

### Step 5: Update Implementation Notes Artifact

Update artifact with GREEN state evidence and integration results.

#### 5a: Add GREEN State Evidence

Update status from 'draft' to 'complete':
```markdown
**Status:** complete
```

Insert GREEN state section after RED state section:
```markdown
### GREEN State (After Implementation)

**Test Success Output:**
```
... pytest output snippet (first 500 chars) ...
```

**Passing Tests:**
- Total: 5
- Passed: 5
- Failed: 0
- Errors: 0

**Timestamp:** 2024-01-01T12:30:00Z

**GREEN Validation:** YES

**Coverage Metrics:**  # if available
- Percentage: 95.5%
- Statements: 200
- Missing: 9
```

#### 5b: Add Integration Validation Results

Insert integration validation section before Notes section:
```markdown
## Integration Validation Results

**Summary:** 1/2 checks passed

| Check | Command | Status |
|-------|---------|--------|
| ruff | `ruff check src/` | ✓ PASS |
| mypy | `mypy src/` | ⚠ FAIL (warning) |

**Failed Checks:**

### mypy
Command: `mypy src/`
Exit code: 1
Critical: No

```
... output snippet (first 500 chars) ...
```
```

**On success**: ✓ Print updated artifact path

### Step 6: Print Success Summary

Print GREEN validation summary:

```
==========================================================
GREEN STATE VALIDATION
==========================================================

Test State: GREEN
Timestamp: 2024-01-01T12:30:00Z

Valid GREEN state confirmed - implementation verified

✓ GREEN state confirmed - implementation verified

==========================================================
INTEGRATION VALIDATION
==========================================================

  Running ruff... ✓ PASS
  Running mypy... ⚠ FAIL (warning)

Integration checks: 1/2 passed

✓ Updated implementation notes: /path/to/impl-notes-feat-123.md
```

**Phase 2 Exit**: Exit 0 (success - GREEN achieved, checks passed)

## Exit Codes

- **0**: Success
  - Phase 1: Context prepared, RED state validated, artifact created
  - Phase 2: GREEN state validated, integration checks passed (or non-critical failures only)
- **1**: Validation failure
  - Test design artifact not found
  - Invalid RED state (tests passing or no failures)
  - Invalid GREEN state (tests still failing)
  - Critical integration check failures
- **2**: Escalation required
  - Tests broken (TEST_BROKEN, ENV_BROKEN)
  - Regression detected (test count decreased)
  - System error (template not found, permission denied)

## Output Examples

### Phase 1 Success (RED State Entry)

```
Implementation workflow for: feat-123
Agent: dev-specialist

✓ Found test design: /path/to/test-design-feat-123.md
✓ Found spec: /path/to/feat-123.md

📋 Agent Context:
  feature_id: feat-123
  test_design_path: /path/to/test-design-feat-123.md
  spec_path: /path/to/feat-123.md
  test_file_patterns:
    - tests/**/*.py
    - **/test_*.py
    - **/*_test.py

============================================================
TDD ENTRY VALIDATION
============================================================

Test State: RED
Timestamp: 2024-01-01T12:00:00Z

Valid RED state confirmed - proceeding with implementation

✓ RED state confirmed - proceeding with implementation

✓ Created implementation notes: /path/to/impl-notes-feat-123.md

============================================================
NEXT STEP: Invoke implementation agent
============================================================

Agent: dev-specialist
Instructions: Implement code to make tests pass
Test design: /path/to/test-design-feat-123.md
Feature spec: /path/to/feat-123.md
Output artifact: /path/to/impl-notes-feat-123.md

NOTE: Agent will read test files from patterns:
  - tests/**/*.py
  - **/test_*.py
  - **/*_test.py
```

### Phase 2 Success (GREEN State Validation)

```
============================================================
GREEN STATE VALIDATION
============================================================

Test State: GREEN
Timestamp: 2024-01-01T12:30:00Z

Valid GREEN state confirmed - implementation verified

✓ GREEN state confirmed - implementation verified

============================================================
INTEGRATION VALIDATION
============================================================

  Running ruff... ✓ PASS
  Running mypy... ✓ PASS

Integration checks: 2/2 passed

✓ Updated implementation notes: /path/to/impl-notes-feat-123.md
```

### Validation Failure (Still RED)

```
============================================================
GREEN STATE VALIDATION
============================================================

Test State: RED
Timestamp: 2024-01-01T12:30:00Z

Tests still failing after implementation

✗ GREEN state validation failed
  State: RED
  All tests must PASS (GREEN state) after implementation

  Evidence:
    Total tests: 5
    Passed: 2
    Failed: 3
    Errors: 0
```

### Escalation (Broken Tests)

```
============================================================
TDD ENTRY VALIDATION
============================================================

Test State: BROKEN
Timestamp: 2024-01-01T12:00:00Z

Tests have errors that prevent RED/GREEN classification

✗ TDD entry validation failed
  State: BROKEN
  Tests must be FAILING (RED state) before implementation

  Evidence:
    Total tests: 5
    Passed: 0
    Failed: 2
    Errors: 3

  Escalation required: Fix test issues before implementing
```

### Escalation (Regression Detected)

```
============================================================
GREEN STATE VALIDATION
============================================================

Test State: GREEN
Timestamp: 2024-01-01T12:30:00Z

Regression: test count decreased from 5 to 3

✗ GREEN state validation failed
  State: REGRESSION
  Test count decreased - possible test deletion

  Evidence:
    Baseline tests: 5
    Current tests: 3
    Missing tests: 2
```

### Critical Integration Failure

```
============================================================
INTEGRATION VALIDATION
============================================================

  Running ruff... ✓ PASS
  Running mypy... ✗ FAIL (CRITICAL)

Integration checks: 1/2 passed

✗ Critical integration checks failed:
  - mypy: mypy src/
```

## Configuration Reference

`.specify/harness-tdd-config.yml`:

```yaml
version: '1.0'
agents:
  implementation_agent: dev-specialist

artifacts:
  root: 'docs/features'
  types:
    test_design: 'test-design'
    impl_notes: 'impl-notes'

test_framework:
  type: pytest
  file_patterns:
    - 'tests/**/*.py'
    - '**/test_*.py'
    - '**/*_test.py'

integration_checks:
  enabled: true
  commands:
    - name: ruff
      command: 'ruff check src/'
      critical: false
    - name: mypy
      command: 'mypy src/'
      critical: false
    - name: security-scan
      command: 'bandit -r src/'
      critical: true  # block on security issues
```

## Implementation Notes Artifact Template

`templates/implementation-notes-template.md`:

```markdown
# Implementation Notes: {{ feature_name }}

**Feature ID:** {{ feature_id }}
**Agent:** {{ agent_name }}
**Timestamp:** {{ timestamp }}
**Status:** {{ status }}

## RED→GREEN Evidence

### RED State (Before Implementation)

**Test Failure Output:**
```
{{ red_state_evidence.output[:500] }}
```

**Failing Tests:**
- Total tests: {{ red_state_evidence.evidence.total_tests }}
- Passed: {{ red_state_evidence.evidence.passed }}
- Failed: {{ red_state_evidence.evidence.failed }}
- Errors: {{ red_state_evidence.evidence.errors }}

**Timestamp:** {{ red_state_evidence.timestamp }}

**RED Validation:** YES

### GREEN State (After Implementation)

_To be filled after implementation_

## Integration Validation Results

_To be filled after integration checks_

## Notes

_Developer notes on implementation approach, challenges, decisions_

## Refactoring

_Track refactoring steps after achieving GREEN state_
```

## Related Commands

- `/speckit.multi-agent.test`: Generate tests (Step 7) - prerequisite for implement
- `/speckit.multi-agent.review`: Review implementation and tests (Step 9)
- `/speckit.multi-agent.commit`: Commit implementation (Step 10)

## Implementation Notes

**Current (Phase 2-3)**:
- Two-phase execution model (RED entry → GREEN validation)
- Integration checks with critical/non-critical distinction
- Baseline test count for regression detection
- Coverage metrics (optional, if pytest-cov available)
- Template-based artifact generation with Jinja2

**Future (Phase 4+)**:
- Direct agent spawning via Claude Code Agent API
- Automated implementation execution
- Real-time test feedback during implementation
- Integration with CI/CD pipelines
