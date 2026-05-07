---
description: "Generate failing tests (RED state) for feature"
agent: test-specialist
tools:
  - 'filesystem/read'
  - 'filesystem/write'
  - 'bash/execute'
scripts:
  validate_red: scripts/validate_red_state.py
  extract_ac: scripts/extract_acceptance_criteria.py
  escalate: scripts/escalate_broken_tests.py
exit_codes:
  0: "Success - valid RED state confirmed"
  1: "Validation failure - tests passing (GREEN) or no valid RED failures"
  2: "Escalation required - tests broken (TEST_BROKEN or ENV_BROKEN)"
---

# Test Generation Workflow (Multi-Agent TDD Phase 3)

This command spawns the @test-specialist agent to write failing tests (RED state) for a feature specification and generates a test design artifact.

## Prerequisites

- Feature specification exists in one of the standard locations
- Test framework (pytest) configured
- Python environment with pytest available
- Configuration file at `.specify/harness-tdd-config.yml` (optional, uses defaults if missing)

## User Input

**Command**: `/speckit.multi-agent.test $FEATURE_ID [--run-tests] [--allow-non-test-files --justification "reason"]`

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--run-tests`: (Optional) Run tests and validate RED state after agent completes
- `--allow-non-test-files`: (Optional) Allow modifications outside test file patterns
- `--justification`: (Required with --allow-non-test-files) Reason for bypassing file gate

## Step 1: Find Spec Artifact

Search for spec in order of precedence:
1. `docs/features/${FEATURE_ID}.md`
2. `docs/specs/${FEATURE_ID}-spec.md`
3. `docs/specs/${FEATURE_ID}.md`
4. `.specify/specs/${FEATURE_ID}.md`

**If not found**: ❌ Exit 1 with error listing checked locations

**On success**: Read spec content for next steps

## Step 2: Extract Acceptance Criteria

Execute the acceptance criteria extraction script:

```bash
python3 scripts/extract_acceptance_criteria.py --file ${SPEC_PATH} --format json
```

**Expected output**: JSON with acceptance criteria list and count

**Exit codes**:
- 0: Successfully extracted AC → Continue to Step 3
- 1: No AC found in spec → ❌ Exit 1 with error
- 2: System error → ❌ Exit 2 with error

**Validation**: Ensure at least one acceptance criterion exists (AC-1, AC-2, etc.)

## Step 3: Load Configuration

Load harness configuration from `.specify/harness-tdd-config.yml` or use defaults:

**Default configuration includes**:
- Agent names (test-specialist, dev-specialist, arch-specialist, review-specialist)
- Test framework settings (pytest, file patterns)
- Failure code classifications (valid RED vs. broken)
- Artifact paths and templates

**File gate restrictions** (from config):
- Test file patterns: `tests/**/*.py`, `**/test_*.py`, `**/*_test.py`
- Unless `--allow-non-test-files` flag provided, agent can only create/modify files matching these patterns

## Step 4: Build Agent Context

Prepare structured context for @test-specialist:

**Context includes**:
- Feature ID: `${FEATURE_ID}`
- Spec content: Full spec markdown
- Acceptance criteria: Extracted AC list from Step 2
- Test patterns: From config (file patterns agent must follow)
- Valid failure codes: MISSING_BEHAVIOR, ASSERTION_MISMATCH
- File gate restrictions: Allowed patterns or bypass justification

**Instructions for agent**:
1. Write failing tests (RED state) for all acceptance criteria
2. Use test patterns from config
3. Tests MUST fail initially with MISSING_BEHAVIOR or ASSERTION_MISMATCH
4. DO NOT write implementation code
5. RESPECT file gate restrictions

## Step 5: Spawn Test Agent

**MVP Implementation (Phase 2-3)**:
- Write context to temporary file in `/tmp/test-agent-context-${FEATURE_ID}-*.txt`
- Print instructions for manual agent invocation
- Agent consumes context file and writes tests

**Future (Phase 4+)**:
- Automate via Claude Code Agent API
- Direct agent spawning without manual invocation

**Agent deliverables**:
- Test files in `tests/` directory matching configured patterns
- All tests failing with valid RED state codes
- No implementation code written

## Step 6: Validate RED State (if --run-tests flag)

If `--run-tests` flag provided, execute validation:

```bash
python3 scripts/validate_red_state.py ${FEATURE_ID} --project-root ${PROJECT_ROOT}
```

**Expected output**: JSON with validation results

**Exit codes**:
- 0: Valid RED state → Continue to Step 7
- 1: Invalid state (GREEN or no valid RED) → ❌ Exit 1 with validation failure
- 2: Broken tests → Escalate in Step 6b

**Validation checks**:
- At least one test failed
- All failures use valid RED codes (MISSING_BEHAVIOR, ASSERTION_MISMATCH)
- No TEST_BROKEN, ENV_BROKEN, or other error codes

### Step 6b: Handle Broken Tests (if needed)

If validation exits with code 2 (broken tests), escalate:

```bash
python3 scripts/escalate_broken_tests.py --file evidence.json --format human
```

**Escalation report includes**:
- Failure codes (TEST_BROKEN, ENV_BROKEN, etc.)
- Root cause diagnosis for each code
- Recommended actions
- List of affected tests

**Output to stderr**: Human-readable escalation report

**Then**: ❌ Exit 2 with escalation details

## Step 7: Generate Test Design Artifact

Create artifact at path from config (default: `docs/tests/test-design/${FEATURE_ID}-test-design.md`)

**Artifact includes**:
- Feature ID and name
- Timestamp
- Status (draft, validated, etc.)
- Bypass information (if --allow-non-test-files used)
- Test evidence (if --run-tests used)
- RED state validation results (if --run-tests used)
- Escalation details (if tests broken)

**Template location**:
- Custom: `.specify/templates/test-design-template.md`
- Built-in: `templates/test-design-template.md`

**Template variables**:
- `feature_id`: Feature identifier
- `feature_name`: Extracted from spec H1 heading
- `timestamp`: ISO 8601 UTC timestamp
- `status`: draft, validated, etc.
- `bypass_info`: File gate bypass details (if applicable)
- `evidence`: Test execution evidence (if --run-tests)
- `valid_red`: Boolean validation result (if --run-tests)
- `escalation`: Escalation details (if broken)

## Exit Codes

- **0**: Success
  - Agent spawned and artifact created
  - If --run-tests: valid RED state confirmed
- **1**: Validation failure
  - Spec not found
  - No acceptance criteria
  - Tests passing (GREEN state)
  - No valid RED failures
- **2**: Escalation required
  - Tests broken (TEST_BROKEN, ENV_BROKEN)
  - System error (pytest not found, etc.)

## Output Examples

### Success (without --run-tests)

```
=== Agent Invocation Required ===
Please invoke @test-specialist agent with the following context:
Feature ID: feat-123
Context file: /tmp/test-agent-context-feat-123-abc123.txt

NOTE: This is Phase 2 MVP behavior (context-file handoff).
      Future phases will automate via Claude Code Agent API.
================================

✓ Success!
  Spec: /path/to/docs/features/feat-123.md
  Artifact: /path/to/docs/tests/test-design/feat-123-test-design.md

Next steps:
  1. Invoke @test-specialist agent with context file
  2. Review test design artifact
  3. Run tests to verify RED state
```

### Success (with --run-tests, valid RED)

```
✓ Success!
  Spec: /path/to/docs/features/feat-123.md
  Artifact: /path/to/docs/tests/test-design/feat-123-test-design.md

Next steps:
  1. Review test design artifact with RED state validation
  2. Proceed to implementation if RED state is valid
```

### Validation Failure (GREEN state)

```
✗ Validation failure: Tests not in valid RED state
  Artifact: /path/to/docs/tests/test-design/feat-123-test-design.md

Review the test design artifact for details.
```

### Escalation Required (broken tests)

```
⚠ ESCALATION REQUIRED

Test execution failed: 2 broken test(s)

  TEST_BROKEN: test_user_login
    Location: tests/test_auth.py:15
    Root cause: Test code has syntax errors or invalid test structure
    Action: Fix syntax errors in test code

  ENV_BROKEN: test_db_connection
    Location: tests/test_db.py:8
    Root cause: Test environment configuration issue
    Action: Check dependencies, virtual environment, pytest installation

✗ Escalation required: Tests are broken
  Artifact: /path/to/docs/tests/test-design/feat-123-test-design.md

Review the test design artifact for escalation details.
```

## Configuration Reference

`.specify/harness-tdd-config.yml`:

```yaml
version: '1.0'
agents:
  test_agent: test-specialist
  implementation_agent: dev-specialist
  arch_reviewer: arch-specialist
  code_reviewer: review-specialist

artifacts:
  test_design:
    path: 'docs/tests/test-design/{feature_id}-test-design.md'
    template: '.specify/templates/test-design-template.md'
    mandatory: true

test_framework:
  type: pytest
  file_patterns:
    - 'tests/**/*.py'
    - '**/test_*.py'
    - '**/*_test.py'
  failure_codes:
    valid_red:
      - MISSING_BEHAVIOR
      - ASSERTION_MISMATCH
      - AssertionError
      - NameError
      - AttributeError
    invalid_escalate:
      - TEST_BROKEN
      - ENV_BROKEN
      - SyntaxError
      - ImportError
      - ModuleNotFoundError
```

## File Gate Bypass

When `--allow-non-test-files` is used with `--justification`:

**Context passed to agent includes**:
```
⚠️  BYPASS ACTIVE: Non-test files allowed
Justification: Need to create test fixtures in src/

You may create/modify files outside test patterns if necessary.
```

**Without bypass** (default):
```
You MUST only create/modify files matching these patterns:
- tests/**/*.py
- **/test_*.py
- **/*_test.py

Files not matching these patterns will be rejected.
If you need to modify non-test files, request --allow-non-test-files flag.
```

## Related Commands

- `/speckit.multi-agent.implement`: Implement feature (requires valid RED state)
- `/speckit.multi-agent.review`: Review implementation and tests
- `/speckit.multi-agent.validate`: Validate full feature lifecycle

## Implementation Notes

**Current (Phase 2-3)**:
- Context-file handoff to agent (MVP)
- Manual agent invocation required
- Artifact generation automated

**Future (Phase 4+)**:
- Direct agent spawning via Claude Code Agent API
- Automated test execution and validation
- Integration with CI/CD pipelines
