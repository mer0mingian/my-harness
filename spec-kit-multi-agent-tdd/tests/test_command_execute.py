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
