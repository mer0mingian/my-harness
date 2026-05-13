---
description: "Implement feature code (RED → GREEN)"
agent: matd-dev
tools:
  - 'filesystem/read'
  - 'filesystem/write'
  - 'bash/execute'
scripts:
  validate_red: scripts/validate_red_state.py
  validate_green: scripts/validate_green_state.py
exit_codes:
  0: "Success - GREEN state achieved"
  1: "Validation failure - RED state invalid or GREEN not achieved"
  2: "Escalation required - tests broken (BROKEN state) or regression detected"
---

# Implementation Workflow (Multi-Agent TDD Step 8)

This command orchestrates the RED → GREEN transition: validates RED entry, invokes @matd-dev agent for implementation, validates GREEN exit.

## Prerequisites

- Test design artifact exists from Step 7 (test command)
- Tests are in valid RED state (failing with MISSING_BEHAVIOR or ASSERTION_MISMATCH)
- Test framework (pytest) configured
- Python environment with pytest available
- Configuration file at `.specify/harness-tdd-config.yml` (optional, uses defaults if missing)

## User Input

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--project-root PATH`: (Optional) Project root directory (default: current directory)

## Workflow

### Step 1: Load Configuration

Load harness configuration from `.specify/harness-tdd-config.yml` or use defaults.

**Default configuration includes**:
- Agent names (matd-dev for implementation)
- Test framework settings (pytest, file patterns)
- Artifact paths and templates
- `workflow.agent_timeout` — agent task timeout in minutes (default: 30 if key missing)

### Step 2: Find Test Design Artifact

Search for test design artifact from Step 7 using `artifact_paths.find_existing()`.

**Default search paths**:
- `docs/features/${FEATURE_ID}/test-design-${FEATURE_ID}.md`
- `docs/tests/test-design/test-design-${FEATURE_ID}.md`
- `.specify/artifacts/${FEATURE_ID}/test-design-${FEATURE_ID}.md`

**If not found**: ❌ Exit 1 with error - test design required before implementation

### Step 3: Find Spec Artifact (Optional)

Search for feature spec in common locations:
1. `docs/features/${FEATURE_ID}.md`
2. `docs/specs/${FEATURE_ID}-spec.md`
3. `docs/specs/${FEATURE_ID}.md`
4. `.specify/specs/${FEATURE_ID}.md`

**If not found**: Continue without spec (optional resource)

### Step 4: Validate RED State Entry

Execute RED state validation:

```bash
python3 scripts/validate_red_state.py ${FEATURE_ID} --project-root ${PROJECT_ROOT}
```

**Exit codes**:
- 0: Valid RED state → Continue to Step 5
- 1: Invalid state (GREEN or no failures) → ❌ Exit 1 with validation failure
- 2: Broken tests → ❌ Exit 2 with escalation

**Validation checks**:
- At least one test failed
- All failures use valid RED codes (MISSING_BEHAVIOR, ASSERTION_MISMATCH, AssertionError, NameError, AttributeError)
- No TEST_BROKEN, ENV_BROKEN, SyntaxError, ImportError, or ModuleNotFoundError

**RED State Evidence Structure**:
```python
{
    'state': 'RED',
    'validation_passed': True,
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

### Step 5: Create Implementation Notes Artifact

Generate implementation notes artifact from template.

**Template location**:
- Custom: `.specify/templates/implementation-notes-template.md`
- Built-in: `templates/implementation-notes-template.md`

**Artifact output path** (from config):
- Default: `docs/features/${FEATURE_ID}/impl-notes-${FEATURE_ID}.md`
- Configurable via `artifacts.impl_notes.path` in config

**Template variables**:
- `feature_id`: Feature identifier
- `feature_name`: Extracted from feature_id (title-cased)
- `agent_name`: Implementation agent name (matd-dev)
- `timestamp`: ISO 8601 UTC timestamp
- `status`: 'draft' (will be updated to 'complete' after GREEN validation)
- `red_state_evidence`: RED validation result from Step 4

**Artifact sections**:
1. Feature metadata (ID, name, timestamp, status, agent)
2. RED State Evidence (from Step 4 validation)
3. GREEN State Evidence (placeholder, filled in Step 8)
4. Notes - for developer to document implementation approach
5. Refactoring - for tracking refactoring steps after GREEN

### Step 6: Invoke matd-dev Agent

Invoke @matd-dev agent with implementation context:

**Agent**: matd-dev

**Context**:
- `feature_id`: Feature identifier
- `test_design_path`: Path to test design artifact
- `spec_path`: Path to spec artifact (if available)
- `test_file_patterns`: List of test file patterns from config

**Instructions**:
1. Read test design artifact at `test_design_path`
2. Read spec artifact at `spec_path` (if provided)
3. Implement code to make tests pass
4. DO NOT modify test files (unless fixing broken tests)
5. Focus on minimal implementation to achieve GREEN state

**Timeout**: Complete this task within ${agent_timeout} minutes (default: 30). If you cannot achieve GREEN state within the time limit, output partial results with a summary of completed work, then escalate to human with what remains and the current test state.

**Print agent invocation instructions**:
```
==========================================================
NEXT STEP: Invoke implementation agent
==========================================================

Agent: matd-dev
Instructions: Implement code to make tests pass
Test design: /path/to/test-design-feat-123.md
Feature spec: /path/to/feat-123.md  # if available
Output artifact: /path/to/impl-notes-feat-123.md

NOTE: Agent will read test files from patterns:
  - tests/**/*.py
  - **/test_*.py
  - **/*_test.py
```

### Step 7: Validate GREEN State

After agent completes implementation, execute GREEN state validation:

```bash
python3 scripts/validate_green_state.py ${FEATURE_ID} --project-root ${PROJECT_ROOT} --baseline-count ${BASELINE_COUNT}
```

**Baseline count**: Extracted from RED state evidence (Step 4)

**Exit codes**:
- 0: Valid GREEN state → Continue to Step 8
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
    'state': 'GREEN',
    'validation_passed': True,
    'timestamp': '2024-01-01T12:30:00Z',
    'message': 'Valid GREEN state confirmed',
    'evidence': {
        'total_tests': 5,
        'passed': 5,
        'failed': 0,
        'errors': 0
    },
    'output': '... pytest output ...',
    'coverage': {
        'found': True,
        'percentage': 95.5,
        'statements': 200,
        'missing': 9
    }
}
```

**Regression Detection**:
If test count < baseline:
- Exit 2 (escalation)
- Error message: "Regression: test count decreased from {baseline} to {current}"

### Step 8: Update Implementation Notes Artifact

Update artifact with GREEN state evidence.

**Status update**: Change from 'draft' to 'complete'

**Insert GREEN state section**:
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

**Print success**:
```
==========================================================
GREEN STATE VALIDATION
==========================================================

Test State: GREEN
Timestamp: 2024-01-01T12:30:00Z

Valid GREEN state confirmed - implementation verified

✓ GREEN state confirmed - implementation verified
✓ Updated implementation notes: /path/to/impl-notes-feat-123.md
```

**Note**: Integration checks (ruff, mypy) run automatically via post_implement hooks defined in `.specify/hooks.yml`

## Exit Codes

- **0**: Success - GREEN state validated, implementation complete
- **1**: Validation failure
  - Test design artifact not found
  - Invalid RED state (tests passing or no failures)
  - Invalid GREEN state (tests still failing)
- **2**: Escalation required
  - Tests broken (TEST_BROKEN, ENV_BROKEN)
  - Regression detected (test count decreased)
  - System error (template not found, permission denied)

## Output Examples

### Success Flow

```
Implementation workflow for: feat-123
Agent: matd-dev

✓ Found test design: /path/to/test-design-feat-123.md
✓ Found spec: /path/to/feat-123.md

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

Agent: matd-dev
Instructions: Implement code to make tests pass
Test design: /path/to/test-design-feat-123.md
Feature spec: /path/to/feat-123.md
Output artifact: /path/to/impl-notes-feat-123.md

NOTE: Agent will read test files from patterns:
  - tests/**/*.py
  - **/test_*.py
  - **/*_test.py

[Agent executes implementation...]

============================================================
GREEN STATE VALIDATION
============================================================

Test State: GREEN
Timestamp: 2024-01-01T12:30:00Z

Valid GREEN state confirmed - implementation verified

✓ GREEN state confirmed - implementation verified
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

## Configuration Reference

`.specify/harness-tdd-config.yml`:

```yaml
version: '1.0'
agents:
  implementation_agent: matd-dev

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

workflow:
  agent_timeout: 30  # minutes
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

## Notes

_Developer notes on implementation approach, challenges, decisions_

## Refactoring

_Track refactoring steps after achieving GREEN state_
```

## Related Commands

- `/speckit.matd.test`: Generate tests (Step 7) - prerequisite for implement
- `/speckit.matd.review`: Review implementation and tests (Step 9)
- `/speckit.matd.commit`: Commit implementation (Step 10)

## Integration Checks

Integration checks (linting, type checking, security scans) are managed via SpecKit hooks in `.specify/hooks.yml`.

See: `.specify/hooks.yml` for post_implement hook configuration.

## Implementation Notes

**Current (Phase 2-3)**:
- Single-phase execution (RED → implement → GREEN)
- Integration checks delegated to SpecKit hooks
- Baseline test count for regression detection
- Coverage metrics (optional, if pytest-cov available)
- Template-based artifact generation with Jinja2

**Future (Phase 4+)**:
- Direct agent spawning via Claude Code Agent API
- Automated implementation execution
- Real-time test feedback during implementation
- Integration with CI/CD pipelines
