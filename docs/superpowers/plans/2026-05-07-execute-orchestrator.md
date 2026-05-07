# Execute Orchestrator Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the `/speckit.multi-agent.execute` orchestrator command that runs the full TDD workflow (test → implement → review → commit) by invoking subcommands sequentially with proper error handling and escalation.

**Architecture:** Subprocess-based orchestration invoking 4 workflow commands as separate processes. Each command returns exit code (0=success, 1=validation failure, 2=escalation required). Interactive mode uses human_feedback.py for prompts between steps. No PR creation in Phase 2.

**Tech Stack:** Python 3.12, subprocess, pathlib, argparse, existing lib modules (artifact_paths, human_feedback)

---

## File Structure

```
spec-kit-multi-agent-tdd/
├── commands/
│   ├── test.py              # Existing - Step 7 (test generation)
│   └── execute.py           # NEW - Orchestrator command
├── lib/
│   ├── artifact_paths.py    # Existing - Artifact path resolution
│   └── human_feedback.py    # Existing - Interactive prompts
├── tests/
│   ├── test_command_execute.py           # NEW - Unit tests
│   └── integration/
│       └── test_command_execute_e2e.sh   # NEW - Integration tests
└── extension.json           # UPDATE - Register execute command
```

**Responsibilities:**
- `commands/execute.py`: Orchestration logic, subprocess invocation, error handling
- `tests/test_command_execute.py`: Unit tests mocking subprocess calls
- `tests/integration/test_command_execute_e2e.sh`: End-to-end shell script with fake subcommands

---

## Task 1: Unit Test Scaffold

**Files:**
- Create: `/home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd/tests/test_command_execute.py`

- [ ] **Step 1: Write failing test for command scaffold**

```python
#!/usr/bin/env python3
"""
Unit tests for execute command (S3.5-001 through S3.5-005).
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.execute import (
    invoke_subcommand,
    execute_workflow,
    main,
)


class TestInvokeSubcommand:
    """Test subprocess invocation wrapper."""
    
    def test_invoke_success_exit_0(self):
        """Subcommand exits 0 returns success status."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Success output",
                stderr=""
            )
            
            result = invoke_subcommand('test', 'feat-123', Path.cwd())
            
            assert result['status'] == 'SUCCESS'
            assert result['exit_code'] == 0
            assert 'test' in result['command']
            mock_run.assert_called_once()
    
    def test_invoke_validation_failure_exit_1(self):
        """Subcommand exits 1 returns validation failure."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Validation failed: tests not in RED state"
            )
            
            result = invoke_subcommand('test', 'feat-123', Path.cwd())
            
            assert result['status'] == 'FAILED'
            assert result['exit_code'] == 1
            assert 'Validation failed' in result['stderr']
    
    def test_invoke_escalation_exit_2(self):
        """Subcommand exits 2 returns blocked/escalation."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=2,
                stdout="",
                stderr="ESCALATION: Tests broken (TEST_BROKEN)"
            )
            
            result = invoke_subcommand('test', 'feat-123', Path.cwd())
            
            assert result['status'] == 'BLOCKED'
            assert result['exit_code'] == 2
            assert 'ESCALATION' in result['stderr']


class TestExecuteWorkflow:
    """Test full workflow orchestration."""
    
    def test_all_steps_success(self):
        """All 4 subcommands succeed completes workflow."""
        with patch('commands.execute.invoke_subcommand') as mock_invoke:
            # All commands return success
            mock_invoke.return_value = {
                'status': 'SUCCESS',
                'exit_code': 0,
                'stdout': 'Step completed',
                'stderr': ''
            }
            
            result = execute_workflow('feat-123', mode='auto', project_root=Path.cwd())
            
            assert result['status'] == 'COMPLETED'
            assert result['feature_id'] == 'feat-123'
            
            # Verify all 4 commands invoked in order
            assert mock_invoke.call_count == 4
            calls = [call[0][0] for call in mock_invoke.call_args_list]
            assert calls == ['test', 'implement', 'review', 'commit']
    
    def test_halt_on_test_blocked(self):
        """Test command escalation halts workflow."""
        with patch('commands.execute.invoke_subcommand') as mock_invoke:
            mock_invoke.return_value = {
                'status': 'BLOCKED',
                'exit_code': 2,
                'stdout': '',
                'stderr': 'Tests broken (TEST_BROKEN)'
            }
            
            result = execute_workflow('feat-123', mode='auto', project_root=Path.cwd())
            
            assert result['status'] == 'ESCALATION_REQUIRED'
            assert 'test' in result['failed_step']
            assert 'Tests broken' in result['reason']
            
            # Only test command invoked, not implement/review/commit
            assert mock_invoke.call_count == 1
    
    def test_halt_on_implement_failed(self):
        """Implementation failure halts before review."""
        with patch('commands.execute.invoke_subcommand') as mock_invoke:
            def side_effect(cmd, *args, **kwargs):
                if cmd == 'test':
                    return {'status': 'SUCCESS', 'exit_code': 0, 'stdout': '', 'stderr': ''}
                elif cmd == 'implement':
                    return {'status': 'FAILED', 'exit_code': 1, 'stdout': '', 
                            'stderr': 'Tests still failing (GREEN not achieved)'}
                else:
                    pytest.fail(f"Unexpected command: {cmd}")
            
            mock_invoke.side_effect = side_effect
            
            result = execute_workflow('feat-123', mode='auto', project_root=Path.cwd())
            
            assert result['status'] == 'VALIDATION_FAILED'
            assert 'implement' in result['failed_step']
            
            # Test + implement invoked, but not review/commit
            assert mock_invoke.call_count == 2


class TestInteractiveMode:
    """Test interactive mode prompts."""
    
    def test_interactive_prompts_between_steps(self):
        """Interactive mode prompts user between each step."""
        with patch('commands.execute.invoke_subcommand') as mock_invoke, \
             patch('commands.execute.request_interactive_approval') as mock_approval:
            
            mock_invoke.return_value = {
                'status': 'SUCCESS',
                'exit_code': 0,
                'stdout': 'Step completed',
                'stderr': ''
            }
            mock_approval.return_value = True  # User approves each step
            
            result = execute_workflow('feat-123', mode='interactive', project_root=Path.cwd())
            
            assert result['status'] == 'COMPLETED'
            
            # Approval requested 3 times (after test, implement, review - not after commit)
            assert mock_approval.call_count == 3
    
    def test_interactive_abort_on_reject(self):
        """User rejection in interactive mode halts workflow."""
        with patch('commands.execute.invoke_subcommand') as mock_invoke, \
             patch('commands.execute.request_interactive_approval') as mock_approval:
            
            mock_invoke.return_value = {
                'status': 'SUCCESS',
                'exit_code': 0,
                'stdout': 'Step completed',
                'stderr': ''
            }
            # User rejects after test step
            mock_approval.return_value = False
            
            result = execute_workflow('feat-123', mode='interactive', project_root=Path.cwd())
            
            assert result['status'] == 'ABORTED'
            assert 'User rejected' in result['reason']
            
            # Only test command invoked
            assert mock_invoke.call_count == 1


class TestMainCLI:
    """Test CLI argument parsing."""
    
    def test_feature_id_required(self, capsys):
        """Feature ID argument is required."""
        with patch('sys.argv', ['execute.py']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # argparse error
    
    def test_default_auto_mode(self):
        """Default mode is auto."""
        with patch('sys.argv', ['execute.py', 'feat-123']), \
             patch('commands.execute.execute_workflow') as mock_exec:
            
            mock_exec.return_value = {'status': 'COMPLETED', 'feature_id': 'feat-123'}
            
            exit_code = main()
            
            assert exit_code == 0
            mock_exec.assert_called_once()
            assert mock_exec.call_args[1]['mode'] == 'auto'
    
    def test_interactive_mode_flag(self):
        """--mode=interactive enables interactive mode."""
        with patch('sys.argv', ['execute.py', 'feat-123', '--mode=interactive']), \
             patch('commands.execute.execute_workflow') as mock_exec:
            
            mock_exec.return_value = {'status': 'COMPLETED', 'feature_id': 'feat-123'}
            
            exit_code = main()
            
            assert exit_code == 0
            assert mock_exec.call_args[1]['mode'] == 'interactive'
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
python -m pytest tests/test_command_execute.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'commands.execute'"

- [ ] **Step 3: Commit test scaffold**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
git add tests/test_command_execute.py
git commit -m "test: add execute command unit test scaffold (S3.5-001)"
```

---

## Task 2: Execute Command Implementation

**Files:**
- Create: `/home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd/commands/execute.py`

- [ ] **Step 1: Write minimal execute.py to pass subprocess tests**

```python
#!/usr/bin/env python3
"""
/speckit.multi-agent.execute Command Implementation (S3.5-001 through S3.5-005)

Orchestrates full TDD workflow by invoking subcommands sequentially.
Part of the Multi-Agent TDD workflow Phase 2.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def invoke_subcommand(
    command: str,
    feature_id: str,
    project_root: Path,
    additional_args: Optional[list] = None
) -> Dict[str, Any]:
    """
    Invoke a workflow subcommand as subprocess.
    
    Args:
        command: Subcommand name (test, implement, review, commit)
        feature_id: Feature identifier
        project_root: Project root directory
        additional_args: Optional additional command arguments
    
    Returns:
        Result dict with:
        - status: SUCCESS | FAILED | BLOCKED
        - exit_code: Process exit code
        - stdout: Standard output
        - stderr: Standard error
        - command: Full command that was executed
    
    Exit code mapping:
        0 -> SUCCESS
        1 -> FAILED (validation failure)
        2 -> BLOCKED (escalation required)
    """
    # Build command path
    commands_dir = Path(__file__).parent
    command_script = commands_dir / f"{command}.py"
    
    # Build command arguments
    cmd = [sys.executable, str(command_script), feature_id]
    if additional_args:
        cmd.extend(additional_args)
    
    # Execute subprocess
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    # Map exit code to status
    status_map = {
        0: 'SUCCESS',
        1: 'FAILED',
        2: 'BLOCKED',
    }
    status = status_map.get(result.returncode, 'FAILED')
    
    return {
        'status': status,
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'command': ' '.join(cmd),
    }


def request_interactive_approval(
    step_name: str,
    step_result: Dict[str, Any],
    feature_id: str
) -> bool:
    """
    Request user approval to continue after a step in interactive mode.
    
    Args:
        step_name: Name of completed step (test, implement, review)
        step_result: Result dict from invoke_subcommand
        feature_id: Feature identifier
    
    Returns:
        True if user approves continuation, False to abort
    """
    print(f"\n{'='*60}")
    print(f"INTERACTIVE CHECKPOINT: {step_name.upper()} completed")
    print(f"{'='*60}")
    print(f"Feature: {feature_id}")
    print(f"Status: {step_result['status']}")
    print(f"Exit code: {step_result['exit_code']}")
    
    if step_result['stdout']:
        print(f"\nOutput:\n{step_result['stdout'][:500]}")  # First 500 chars
    
    print(f"\nContinue to next step? (y/n): ", end='', flush=True)
    response = input().strip().lower()
    
    return response in ['y', 'yes', '']


def execute_workflow(
    feature_id: str,
    mode: str = 'auto',
    project_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Execute full TDD workflow by orchestrating subcommands.
    
    Args:
        feature_id: Feature identifier
        mode: Execution mode (auto or interactive)
        project_root: Project root directory (defaults to cwd)
    
    Returns:
        Workflow result dict with:
        - status: COMPLETED | VALIDATION_FAILED | ESCALATION_REQUIRED | ABORTED
        - feature_id: Feature identifier
        - failed_step: Step that failed (if not completed)
        - reason: Failure/escalation reason
        - artifacts: List of generated artifacts (if completed)
    """
    if project_root is None:
        project_root = Path.cwd()
    
    # Define workflow steps
    steps = ['test', 'implement', 'review', 'commit']
    
    # Track execution
    completed_steps = []
    
    # Execute each step
    for step in steps:
        print(f"\n{'='*60}")
        print(f"STEP: {step.upper()}")
        print(f"{'='*60}\n")
        
        # Invoke subcommand
        result = invoke_subcommand(step, feature_id, project_root)
        
        # Check result status
        if result['status'] == 'BLOCKED':
            return {
                'status': 'ESCALATION_REQUIRED',
                'feature_id': feature_id,
                'failed_step': step,
                'reason': result['stderr'] or 'Step blocked by gate',
                'exit_code': result['exit_code'],
                'completed_steps': completed_steps,
            }
        
        if result['status'] == 'FAILED':
            return {
                'status': 'VALIDATION_FAILED',
                'feature_id': feature_id,
                'failed_step': step,
                'reason': result['stderr'] or 'Step validation failed',
                'exit_code': result['exit_code'],
                'completed_steps': completed_steps,
            }
        
        # Step succeeded
        completed_steps.append(step)
        
        # Interactive mode checkpoint (except after final commit step)
        if mode == 'interactive' and step != 'commit':
            approved = request_interactive_approval(step, result, feature_id)
            if not approved:
                return {
                    'status': 'ABORTED',
                    'feature_id': feature_id,
                    'failed_step': step,
                    'reason': 'User rejected continuation in interactive mode',
                    'completed_steps': completed_steps,
                }
    
    # All steps completed successfully
    return {
        'status': 'COMPLETED',
        'feature_id': feature_id,
        'completed_steps': completed_steps,
    }


def main():
    """CLI entry point for /speckit.multi-agent.execute command."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Execute full TDD workflow (test → implement → review → commit)"
    )
    parser.add_argument(
        "feature_id",
        help="Feature identifier (e.g., 'feat-123')"
    )
    parser.add_argument(
        "--mode",
        choices=['auto', 'interactive'],
        default='auto',
        help="Execution mode (default: auto)"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    try:
        result = execute_workflow(
            args.feature_id,
            mode=args.mode,
            project_root=args.project_root
        )
        
        # Print result
        print(f"\n{'='*60}")
        print(f"WORKFLOW RESULT: {result['status']}")
        print(f"{'='*60}\n")
        
        if result['status'] == 'COMPLETED':
            print(f"✓ Success! Feature {result['feature_id']} workflow completed.")
            print(f"\nCompleted steps: {', '.join(result['completed_steps'])}")
            return 0
        
        elif result['status'] == 'ESCALATION_REQUIRED':
            print(f"✗ Escalation required at step: {result['failed_step']}", file=sys.stderr)
            print(f"\nReason: {result['reason']}", file=sys.stderr)
            print(f"\nPartial progress: {', '.join(result['completed_steps'])}", file=sys.stderr)
            return 2
        
        elif result['status'] == 'VALIDATION_FAILED':
            print(f"✗ Validation failed at step: {result['failed_step']}", file=sys.stderr)
            print(f"\nReason: {result['reason']}", file=sys.stderr)
            print(f"\nPartial progress: {', '.join(result['completed_steps'])}", file=sys.stderr)
            return 1
        
        elif result['status'] == 'ABORTED':
            print(f"✗ Workflow aborted at step: {result['failed_step']}", file=sys.stderr)
            print(f"\nReason: {result['reason']}", file=sys.stderr)
            print(f"\nPartial progress: {', '.join(result['completed_steps'])}", file=sys.stderr)
            return 1
        
        else:
            print(f"✗ Unknown workflow status: {result['status']}", file=sys.stderr)
            return 1
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run tests to verify they pass**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
python -m pytest tests/test_command_execute.py -v
```

Expected: PASS (all tests green)

- [ ] **Step 3: Make execute.py executable**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
chmod +x commands/execute.py
```

- [ ] **Step 4: Commit implementation**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
git add commands/execute.py
git commit -m "feat: implement execute orchestrator command (S3.5-002, S3.5-003, S3.5-004)"
```

---

## Task 3: Integration Test Script

**Files:**
- Create: `/home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd/tests/integration/test_command_execute_e2e.sh`

- [ ] **Step 1: Write integration test script**

```bash
#!/bin/bash
# Integration tests for /speckit.multi-agent.execute command (S3.5-005)
# Creates fake subcommands and tests full orchestration flow

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Setup test environment
setup() {
    # Create temp directory for fake commands
    export FAKE_COMMANDS_DIR=$(mktemp -d)
    export ORIGINAL_PATH="$PATH"
    
    # Create fake Python interpreter wrapper that uses fake commands
    cat > "$FAKE_COMMANDS_DIR/python" << 'EOF'
#!/bin/bash
# Fake Python wrapper that intercepts execute.py subcommand calls

# If this is a subcommand invocation (test.py, implement.py, etc.)
if [[ "$2" =~ (test|implement|review|commit)\.py$ ]]; then
    CMD_NAME=$(basename "$2" .py)
    FAKE_CMD="$FAKE_COMMANDS_DIR/${CMD_NAME}"
    
    if [[ -x "$FAKE_CMD" ]]; then
        # Execute fake command instead
        exec "$FAKE_CMD" "${@:3}"
    fi
fi

# Otherwise, use real Python
exec python3 "$@"
EOF
    chmod +x "$FAKE_COMMANDS_DIR/python"
    
    # Prepend fake commands dir to PATH
    export PATH="$FAKE_COMMANDS_DIR:$PATH"
    
    info "Test environment initialized"
    info "Fake commands dir: $FAKE_COMMANDS_DIR"
}

teardown() {
    # Restore PATH
    export PATH="$ORIGINAL_PATH"
    
    # Clean up temp directory
    if [[ -n "${FAKE_COMMANDS_DIR:-}" ]] && [[ -d "$FAKE_COMMANDS_DIR" ]]; then
        rm -rf "$FAKE_COMMANDS_DIR"
    fi
    
    info "Test environment cleaned up"
}

# Test: All steps succeed
test_all_steps_success() {
    info "Test: All 4 subcommands succeed"
    
    # Create fake subcommands that all succeed
    for cmd in test implement review commit; do
        cat > "$FAKE_COMMANDS_DIR/$cmd" << EOF
#!/bin/bash
echo "$cmd command executed successfully"
exit 0
EOF
        chmod +x "$FAKE_COMMANDS_DIR/$cmd"
    done
    
    # Run execute command
    if python3 commands/execute.py feat-123 > /tmp/execute_output.txt 2>&1; then
        EXIT_CODE=$?
        if [[ $EXIT_CODE -eq 0 ]]; then
            pass "All steps succeed: exit code 0"
        else
            fail "All steps succeed: expected exit 0, got $EXIT_CODE"
        fi
        
        # Verify all steps executed
        if grep -q "STEP: TEST" /tmp/execute_output.txt && \
           grep -q "STEP: IMPLEMENT" /tmp/execute_output.txt && \
           grep -q "STEP: REVIEW" /tmp/execute_output.txt && \
           grep -q "STEP: COMMIT" /tmp/execute_output.txt; then
            pass "All 4 steps executed"
        else
            fail "Not all steps executed"
        fi
        
        # Verify success message
        if grep -q "COMPLETED" /tmp/execute_output.txt; then
            pass "Success message displayed"
        else
            fail "Success message not found"
        fi
    else
        fail "Command execution failed unexpectedly"
    fi
}

# Test: Test command fails with exit 1
test_validation_failure() {
    info "Test: Test command validation failure (exit 1)"
    
    # Test command fails validation
    cat > "$FAKE_COMMANDS_DIR/test" << 'EOF'
#!/bin/bash
echo "Validation failed: tests not in RED state" >&2
exit 1
EOF
    chmod +x "$FAKE_COMMANDS_DIR/test"
    
    # Run execute command (should fail with exit 1)
    if python3 commands/execute.py feat-123 > /tmp/execute_output.txt 2>&1; then
        fail "Validation failure: expected non-zero exit, got 0"
    else
        EXIT_CODE=$?
        if [[ $EXIT_CODE -eq 1 ]]; then
            pass "Validation failure: exit code 1"
        else
            fail "Validation failure: expected exit 1, got $EXIT_CODE"
        fi
    fi
    
    # Verify error message
    if grep -q "VALIDATION_FAILED" /tmp/execute_output.txt; then
        pass "Validation failure message displayed"
    else
        fail "Validation failure message not found"
    fi
    
    # Verify workflow halted at test step
    if ! grep -q "STEP: IMPLEMENT" /tmp/execute_output.txt; then
        pass "Workflow halted before implement step"
    else
        fail "Workflow did not halt after test failure"
    fi
}

# Test: Test command escalates with exit 2
test_escalation() {
    info "Test: Test command escalation (exit 2)"
    
    # Test command requires escalation
    cat > "$FAKE_COMMANDS_DIR/test" << 'EOF'
#!/bin/bash
echo "ESCALATION: Tests broken (TEST_BROKEN)" >&2
exit 2
EOF
    chmod +x "$FAKE_COMMANDS_DIR/test"
    
    # Run execute command (should fail with exit 2)
    if python3 commands/execute.py feat-123 > /tmp/execute_output.txt 2>&1; then
        fail "Escalation: expected non-zero exit, got 0"
    else
        EXIT_CODE=$?
        if [[ $EXIT_CODE -eq 2 ]]; then
            pass "Escalation: exit code 2"
        else
            fail "Escalation: expected exit 2, got $EXIT_CODE"
        fi
    fi
    
    # Verify escalation message
    if grep -q "ESCALATION_REQUIRED" /tmp/execute_output.txt; then
        pass "Escalation message displayed"
    else
        fail "Escalation message not found"
    fi
}

# Test: Implement command fails after test succeeds
test_halt_at_implement() {
    info "Test: Halt at implement step"
    
    # Test succeeds, implement fails
    cat > "$FAKE_COMMANDS_DIR/test" << 'EOF'
#!/bin/bash
echo "Tests generated successfully"
exit 0
EOF
    chmod +x "$FAKE_COMMANDS_DIR/test"
    
    cat > "$FAKE_COMMANDS_DIR/implement" << 'EOF'
#!/bin/bash
echo "Implementation failed: tests still failing" >&2
exit 1
EOF
    chmod +x "$FAKE_COMMANDS_DIR/implement"
    
    # Run execute command
    if python3 commands/execute.py feat-123 > /tmp/execute_output.txt 2>&1; then
        fail "Implement failure: expected non-zero exit, got 0"
    else
        EXIT_CODE=$?
        if [[ $EXIT_CODE -eq 1 ]]; then
            pass "Implement failure: exit code 1"
        else
            fail "Implement failure: expected exit 1, got $EXIT_CODE"
        fi
    fi
    
    # Verify test ran but review did not
    if grep -q "STEP: TEST" /tmp/execute_output.txt && \
       grep -q "STEP: IMPLEMENT" /tmp/execute_output.txt && \
       ! grep -q "STEP: REVIEW" /tmp/execute_output.txt; then
        pass "Workflow halted after implement step"
    else
        fail "Workflow did not halt correctly"
    fi
}

# Test: Interactive mode
test_interactive_mode() {
    info "Test: Interactive mode with auto-continue"
    
    # Create fake subcommands that all succeed
    for cmd in test implement review commit; do
        cat > "$FAKE_COMMANDS_DIR/$cmd" << EOF
#!/bin/bash
echo "$cmd command executed successfully"
exit 0
EOF
        chmod +x "$FAKE_COMMANDS_DIR/$cmd"
    done
    
    # Run in interactive mode with auto-yes input
    if echo -e "y\ny\ny" | python3 commands/execute.py feat-123 --mode=interactive > /tmp/execute_output.txt 2>&1; then
        pass "Interactive mode: exit code 0"
        
        # Verify interactive checkpoints appeared
        if grep -q "INTERACTIVE CHECKPOINT" /tmp/execute_output.txt; then
            pass "Interactive checkpoints displayed"
        else
            fail "Interactive checkpoints not found"
        fi
    else
        fail "Interactive mode execution failed"
    fi
}

# Main test execution
main() {
    echo "========================================"
    echo "Execute Command Integration Tests"
    echo "========================================"
    echo ""
    
    # Change to project root
    cd "$(dirname "$0")/../.."
    
    setup
    
    # Run tests
    test_all_steps_success
    test_validation_failure
    test_escalation
    test_halt_at_implement
    test_interactive_mode
    
    teardown
    
    # Summary
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo "Tests run: $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "${RED}Failed: $TESTS_FAILED${NC}"
        exit 1
    else
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    fi
}

main "$@"
```

- [ ] **Step 2: Make script executable**

```bash
chmod +x /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd/tests/integration/test_command_execute_e2e.sh
```

- [ ] **Step 3: Run integration tests**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
./tests/integration/test_command_execute_e2e.sh
```

Expected: All 5 integration tests pass

- [ ] **Step 4: Commit integration tests**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
git add tests/integration/test_command_execute_e2e.sh
git commit -m "test: add execute command integration tests (S3.5-005)"
```

---

## Task 4: Register Command in Extension

**Files:**
- Modify: `/home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd/extension.json`

- [ ] **Step 1: Add execute command registration**

Update the `commands` section in extension.json:

```json
{
  "name": "harness-tdd-workflow",
  "version": "1.0.0",
  "description": "Multi-agent TDD workflow commands and artifact templates for SpecKit",
  "author": "Harness Sandbox Team",
  "commands": {
    "test": {
      "file": "commands/test.py",
      "description": "Spawn @test-specialist agent to write failing tests for a feature",
      "usage": "/speckit.multi-agent.test <feature-id>",
      "arguments": [
        {
          "name": "feature_id",
          "required": true,
          "description": "Feature identifier (e.g., 'feat-123')"
        }
      ]
    },
    "execute": {
      "file": "commands/execute.py",
      "description": "Execute full TDD workflow (test → implement → review → commit)",
      "usage": "/speckit.multi-agent.execute <feature-id> [--mode=auto|interactive]",
      "arguments": [
        {
          "name": "feature_id",
          "required": true,
          "description": "Feature identifier (e.g., 'feat-123')"
        },
        {
          "name": "--mode",
          "required": false,
          "description": "Execution mode: auto (default) or interactive"
        }
      ]
    },
    "implement": {
      "description": "Spawn @dev-specialist agent to implement feature (Phase 3)"
    },
    "review": {
      "description": "Spawn review agents for code and architecture review (Phase 3)"
    },
    "commit": {
      "description": "Create Git commit with TDD workflow metadata (Phase 3)"
    },
    "plan": {
      "description": "Generate multi-agent execution plan for feature (Phase 3)"
    }
  },
  "templates": {
    "directory": "templates/"
  },
  "config": {
    "file": "harness-tdd-config.yml",
    "schema": "config-schema.json"
  },
  "hooks": {
    "install": "hooks/install.sh"
  }
}
```

- [ ] **Step 2: Validate JSON syntax**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
python3 -m json.tool extension.json > /dev/null
```

Expected: No output (valid JSON)

- [ ] **Step 3: Commit extension update**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
git add extension.json
git commit -m "feat: register execute command in extension manifest"
```

---

## Task 5: Documentation and Verification

**Files:**
- Modify: `/home/minged01/repositories/harness-workplace/harness-tooling/docs/plans/PHASE2-UPDATED-Execute-Command.md`

- [ ] **Step 1: Update Phase 2 doc to remove PR references**

In PHASE2-UPDATED-Execute-Command.md, update line 142 note to clarify:

```markdown
# NOTE: PR creation removed from Phase 2 scope (future enhancement)
# Execute command stops at git commit (Step 10)
# PR creation will be implemented in Phase 3 as separate enhancement
```

- [ ] **Step 2: Run all unit tests**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
python -m pytest tests/test_command_execute.py -v
```

Expected: All tests pass

- [ ] **Step 3: Run all integration tests**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
./tests/integration/test_command_execute_e2e.sh
```

Expected: All integration tests pass

- [ ] **Step 4: Verify command is executable**

Run:
```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
python3 commands/execute.py --help
```

Expected: Help message displays with usage information

- [ ] **Step 5: Final commit with documentation**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd
git add docs/plans/PHASE2-UPDATED-Execute-Command.md
git commit -m "docs: clarify PR creation out of Phase 2 scope"
```

---

## Self-Review Checklist

**Spec Coverage:**
- [x] S3.5-001: Command scaffold with CLI entry point - Task 1 & 2
- [x] S3.5-002: Subcommand orchestration via subprocess - Task 2
- [x] S3.5-003: Error handling and gate enforcement - Task 2
- [x] S3.5-004: Interactive mode integration - Task 2
- [x] S3.5-005: End-to-end testing - Task 3

**Acceptance Criteria (lines 166-171):**
- [x] Command invokes all 4 subcommands sequentially - `execute_workflow()` function
- [x] Halts on first gate failure - Exit code checking in orchestration loop
- [x] Escalates to human with clear diagnostics - Error result dicts with reason/context
- [x] Workflow summary created on success - COMPLETED status with completed_steps
- [x] Interactive mode prompts between steps - `request_interactive_approval()` function

**Placeholder Check:**
- [x] No TBD/TODO placeholders
- [x] All file paths are absolute
- [x] All code blocks are complete
- [x] All test commands show expected output
- [x] No "implement later" or "add validation" without code

**Type Consistency:**
- [x] `invoke_subcommand()` returns Dict[str, Any] consistently
- [x] `execute_workflow()` returns Dict[str, Any] consistently
- [x] Exit codes: 0=success, 1=validation failure, 2=escalation
- [x] Status values: SUCCESS, FAILED, BLOCKED, COMPLETED, VALIDATION_FAILED, ESCALATION_REQUIRED, ABORTED

**Constitutional Constraints Met:**
- [x] No gate bypassing (gates enforced via exit codes)
- [x] Artifacts validated implicitly (subcommands create them, failure = no artifact)
- [x] Halts on BLOCKED verdict (exit code 2)
- [x] Human feedback optional (interactive mode), gates not bypassable

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-07-execute-orchestrator.md`.

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
