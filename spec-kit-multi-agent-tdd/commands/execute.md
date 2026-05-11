---
description: "Execute full TDD workflow (test → implement → review → commit)"
agent: workflow-orchestrator
tools:
  - 'filesystem/read'
  - 'bash/execute'
scripts:
  invoke_test: /speckit.matd.test
  invoke_implement: /speckit.matd.implement
  invoke_review: /speckit.matd.review
  invoke_commit: /speckit.matd.commit
exit_codes:
  0: "Success - workflow completed or user aborted in interactive mode"
  1: "Validation failure at any step"
  2: "Escalation required - critical failure in workflow step"
---

# Execute Orchestrator (Steps 7-10)

This command orchestrates the complete TDD workflow by invoking subcommands sequentially. It handles both automated and interactive execution modes, with proper error handling and escalation.

## Prerequisites

- Feature specification exists
- Git repository initialized
- All subcommands available (test, implement, review, commit)
- Configuration file at `.specify/harness-tdd-config.yml` (optional)

## User Input

**Command**: `/speckit.matd.execute $FEATURE_ID [--mode=auto|interactive] [--project-root PATH]`

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--mode`: Execution mode (default: auto)
  - `auto`: Run all steps sequentially without pausing
  - `interactive`: Pause after each step for user approval
- `--project-root`: Project root directory (default: current directory)

## Overview

The execute orchestrator manages the complete TDD workflow lifecycle:

**Workflow Steps**:
1. `/speckit.matd.test` - Generate failing tests (RED)
2. `/speckit.matd.implement` - Implement feature (GREEN)
3. `/speckit.matd.review` - Review implementation and tests
4. `/speckit.matd.commit` - Commit changes to git

**Key Features**:
- Sequential execution with dependency enforcement
- Halt on first failure (fail-fast)
- Interactive checkpoints (optional)
- Clear escalation path
- Partial progress tracking

## Step 1: Invoke Test Command

Execute the test generation subcommand:

```bash
/speckit.matd.test ${FEATURE_ID}
```

**Exit code handling**:
- **0**: Tests generated (RED state valid) → Continue to Step 2
- **1**: Validation failure (spec not found, no AC, tests GREEN) → ❌ Exit 1 with failure details
- **2**: Tests broken (TEST_BROKEN, ENV_BROKEN) → ❌ Exit 2 with escalation

**On success**: Track 'test' as completed step

**On failure**: 
- Print failure details from stderr
- Report failed step: 'test'
- Exit with same code as subcommand

## Step 2: Invoke Implement Command

Execute the implementation subcommand:

```bash
/speckit.matd.implement ${FEATURE_ID}
```

**Exit code handling**:
- **0**: Implementation complete (GREEN state valid) → Continue to Step 3
- **1**: Tests still failing (implementation incomplete) → ❌ Exit 1 with failure details
- **2**: Critical failure (design issues, broken tests) → ❌ Exit 2 with escalation

**On success**: Track 'implement' as completed step

**On failure**: 
- Print failure details from stderr
- Report failed step: 'implement'
- Report partial progress: completed 'test' step
- Exit with same code as subcommand

## Step 3: Invoke Review Command

Execute the review subcommand:

```bash
/speckit.matd.review ${FEATURE_ID}
```

**Exit code handling**:
- **0**: Reviews complete (implementation and arch reviews) → Continue to Step 4
- **1**: Validation failure (missing implementation notes, incomplete reviews) → ❌ Exit 1 with failure details
- **2**: BLOCKED verdict (review failed, changes required) → ❌ Exit 2 with escalation

**On success**: Track 'review' as completed step

**On failure**: 
- Print failure details from stderr
- Report failed step: 'review'
- Report partial progress: completed 'test', 'implement' steps
- Exit with same code as subcommand

## Step 4: Invoke Commit Command

Execute the commit subcommand:

```bash
/speckit.matd.commit ${FEATURE_ID}
```

**Exit code handling**:
- **0**: Committed successfully → ✓ Workflow complete
- **1**: Validation failure (uncommitted changes, validation errors) → ❌ Exit 1 with failure details
- **2**: System error (git not available, permissions) → ❌ Exit 2 with escalation

**On success**: Track 'commit' as completed step, return success

**On failure**: 
- Print failure details from stderr
- Report failed step: 'commit'
- Report partial progress: completed 'test', 'implement', 'review' steps
- Exit with same code as subcommand

## Interactive Mode (if --mode=interactive)

After each step (except commit), pause for user approval:

**Interactive Checkpoint Display**:
```
============================================================
INTERACTIVE CHECKPOINT: TEST completed
============================================================
Feature: feat-123
Status: SUCCESS
Exit code: 0

Output:
[First 500 chars of stdout]

Continue to next step? (y/n): _
```

**User Response Handling**:
- `y`, `yes`, or empty (Enter): Continue to next step
- `n`, `no`, or any other input: Abort workflow

**On Abort**:
- Status: 'ABORTED'
- Failed step: Current step
- Reason: 'User rejected continuation in interactive mode'
- Completed steps: List of steps completed before abort
- Exit code: 0 (user-initiated abort is success)

**Note**: No checkpoint after 'commit' step (final step)

## Escalation Handling

If any subcommand fails with exit code 1 or 2:

**Failure Status Mapping**:
- Exit code 1 → Status: 'VALIDATION_FAILED'
- Exit code 2 → Status: 'ESCALATION_REQUIRED'

**Error Report Includes**:
- Failed step name
- Failure reason (from stderr)
- Partial progress (list of completed steps)
- Original exit code

**Output Format**:
```
============================================================
WORKFLOW RESULT: ESCALATION_REQUIRED
============================================================

✗ Escalation required at step: implement

Reason: Implementation incomplete - 2 tests still failing

Partial progress: test

[stderr output from failed subcommand]
```

## Exit Codes

- **0**: Success or user-aborted
  - All steps completed successfully
  - User aborted in interactive mode (not a failure)
- **1**: Validation failure
  - Subcommand validation failed (spec missing, tests GREEN, etc.)
  - User aborted in interactive mode (alternative exit path)
- **2**: Escalation required
  - Critical failure in any step
  - Tests broken, design issues, system errors
  - Requires manual intervention

## Output Examples

### Success (auto mode)

```
============================================================
STEP: TEST
============================================================

[test command output]

============================================================
STEP: IMPLEMENT
============================================================

[implement command output]

============================================================
STEP: REVIEW
============================================================

[review command output]

============================================================
STEP: COMMIT
============================================================

[commit command output]

============================================================
WORKFLOW RESULT: COMPLETED
============================================================

✓ Success! Feature feat-123 workflow completed.

Completed steps: test, implement, review, commit
```

### Success (interactive mode, user continued all steps)

```
============================================================
STEP: TEST
============================================================

[test command output]

============================================================
INTERACTIVE CHECKPOINT: TEST completed
============================================================
Feature: feat-123
Status: SUCCESS
Exit code: 0

Output:
✓ Tests generated (RED state valid)
...

Continue to next step? (y/n): y

[... similar for implement, review ...]

============================================================
STEP: COMMIT
============================================================

[commit command output]

============================================================
WORKFLOW RESULT: COMPLETED
============================================================

✓ Success! Feature feat-123 workflow completed.

Completed steps: test, implement, review, commit
```

### User Abort (interactive mode)

```
============================================================
STEP: TEST
============================================================

[test command output]

============================================================
INTERACTIVE CHECKPOINT: TEST completed
============================================================
Feature: feat-123
Status: SUCCESS
Exit code: 0

Output:
✓ Tests generated (RED state valid)
...

Continue to next step? (y/n): n

============================================================
WORKFLOW RESULT: ABORTED
============================================================

✗ Workflow aborted at step: test

Reason: User rejected continuation in interactive mode

Partial progress: test
```

### Validation Failure (implement step)

```
============================================================
STEP: TEST
============================================================

✓ Tests generated (RED state valid)

============================================================
STEP: IMPLEMENT
============================================================

✗ Implementation incomplete - 2 tests still failing

============================================================
WORKFLOW RESULT: VALIDATION_FAILED
============================================================

✗ Validation failed at step: implement

Reason: Implementation incomplete - 2 tests still failing

Partial progress: test
```

### Escalation Required (review step)

```
============================================================
STEP: TEST
============================================================

✓ Tests generated (RED state valid)

============================================================
STEP: IMPLEMENT
============================================================

✓ Implementation complete (GREEN state valid)

============================================================
STEP: REVIEW
============================================================

✗ BLOCKED: Architecture review failed
  - Verdict: BLOCKED
  - Concerns: Database schema changes require separate PR

============================================================
WORKFLOW RESULT: ESCALATION_REQUIRED
============================================================

✗ Escalation required at step: review

Reason: BLOCKED: Architecture review failed
  - Verdict: BLOCKED
  - Concerns: Database schema changes require separate PR

Partial progress: test, implement
```

## Subcommand Invocation Details

**Command Execution**:
```bash
python3 commands/${STEP}.py ${FEATURE_ID}
```

**Working Directory**: `${PROJECT_ROOT}`

**Output Capture**:
- stdout: Captured and displayed
- stderr: Captured for error reporting
- Exit code: Used for status determination

**Process Isolation**:
- Each subcommand runs as separate subprocess
- No shared state between subcommands
- Artifacts written to filesystem for handoff

## Configuration Reference

`.specify/harness-tdd-config.yml`:

```yaml
version: '1.0'

# Workflow steps (in execution order)
workflow:
  steps:
    - test
    - implement
    - review
    - commit

# Exit code interpretation
exit_codes:
  success: 0
  validation_failed: 1
  escalation_required: 2

# Interactive mode settings
interactive:
  checkpoint_after:
    - test
    - implement
    - review
  # No checkpoint after commit (final step)
```

## Related Commands

- `/speckit.matd.test`: Generate failing tests (RED)
- `/speckit.matd.implement`: Implement feature (GREEN)
- `/speckit.matd.review`: Review implementation and tests
- `/speckit.matd.commit`: Commit changes to git
- `/speckit.matd.validate`: Validate full feature lifecycle (separate command)

## Implementation Notes

**Current (Phase 2-3)**:
- Subcommand invocation via subprocess
- Sequential execution (no parallelism)
- Fail-fast behavior (halt on first failure)
- Partial progress tracking

**Future (Phase 4+)**:
- Parallel execution where possible (test + review in parallel)
- Retry logic for transient failures
- Workflow visualization
- Integration with CI/CD pipelines
- Workflow state persistence for resume

## Error Handling Patterns

**Subprocess Failure**:
- Capture stdout/stderr
- Map exit code to status
- Preserve original error message
- Track partial progress

**User Abort**:
- Clean exit (code 0)
- Report completed steps
- No rollback (steps are idempotent)

**Escalation**:
- Exit code 2 for critical issues
- Include failure context
- Preserve artifacts for debugging
- No automatic recovery

## Workflow State Tracking

**Completed Steps List**:
- Populated as steps succeed
- Included in all exit scenarios
- Used for partial progress reporting

**Status Values**:
- `COMPLETED`: All steps finished
- `VALIDATION_FAILED`: Subcommand validation error
- `ESCALATION_REQUIRED`: Critical failure
- `ABORTED`: User stopped in interactive mode

**Artifact Trail**:
- Test design artifact (from test step)
- Implementation notes (from implement step)
- Review artifacts (from review step)
- Commit reference (from commit step)
