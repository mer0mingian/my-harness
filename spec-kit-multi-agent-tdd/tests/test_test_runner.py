#!/usr/bin/env python3
"""Tests for test_runner module (S4-003)."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add project root to sys.path
script_dir = Path(__file__).parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import pytest
from lib.test_runner import run_tests, validate_red_state
from lib.parse_test_evidence import TestEvidence, TestResult


class TestRunTests:
    """Tests for run_tests function."""

    def test_run_tests_basic(self, tmp_path):
        """Test basic test execution."""
        # Mock subprocess.run
        with patch('lib.test_runner.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "test output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            exit_code, stdout, stderr = run_tests(tmp_path)

            assert exit_code == 0
            assert stdout == "test output"
            assert stderr == ""
            mock_run.assert_called_once()

    def test_run_tests_with_paths(self, tmp_path):
        """Test test execution with specific paths."""
        with patch('lib.test_runner.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = "test failed"
            mock_result.stderr = "error"
            mock_run.return_value = mock_result

            exit_code, stdout, stderr = run_tests(
                tmp_path,
                test_command='pytest',
                test_paths=['tests/test_foo.py']
            )

            assert exit_code == 1
            assert stdout == "test failed"
            assert stderr == "error"

            # Verify command includes paths and flags
            call_args = mock_run.call_args
            assert 'tests/test_foo.py' in call_args[0][0]
            assert '-v' in call_args[0][0]
            assert '--tb=short' in call_args[0][0]

    def test_run_tests_non_pytest_command(self, tmp_path):
        """Test with non-pytest test command."""
        with patch('lib.test_runner.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "npm test output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            exit_code, stdout, stderr = run_tests(
                tmp_path,
                test_command='npm test'
            )

            assert exit_code == 0
            # Verify no pytest-specific flags added
            call_args = mock_run.call_args
            assert '-v' not in call_args[0][0]


class TestValidateRedState:
    """Tests for validate_red_state function."""

    @pytest.fixture
    def mock_config(self):
        """Standard config fixture."""
        return {
            'test_framework': {
                'type': 'pytest',
                'file_patterns': ['tests/**/*.py'],
            }
        }

    @pytest.fixture
    def red_evidence(self):
        """RED state test evidence."""
        return TestEvidence(
            state='RED',
            total_tests=3,
            passed=0,
            failed=3,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name='test_login',
                    status='failed',
                    failure_code='MISSING_BEHAVIOR',
                    error_message='NotImplementedError: login not implemented',
                    file_path='tests/test_auth.py',
                    line_number=10
                ),
                TestResult(
                    name='test_logout',
                    status='failed',
                    failure_code='ASSERTION_MISMATCH',
                    error_message='AssertionError: expected 200, got 404',
                    file_path='tests/test_auth.py',
                    line_number=20
                ),
                TestResult(
                    name='test_password_reset',
                    status='failed',
                    failure_code='MISSING_BEHAVIOR',
                    error_message='NotImplementedError',
                    file_path='tests/test_auth.py',
                    line_number=30
                ),
            ],
            summary='3 tests: 3 failed (state: RED)'
        )

    @pytest.fixture
    def green_evidence(self):
        """GREEN state test evidence."""
        return TestEvidence(
            state='GREEN',
            total_tests=3,
            passed=3,
            failed=0,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name='test_login',
                    status='passed',
                    failure_code=None,
                    error_message=None,
                    file_path='tests/test_auth.py',
                    line_number=10
                ),
                TestResult(
                    name='test_logout',
                    status='passed',
                    failure_code=None,
                    error_message=None,
                    file_path='tests/test_auth.py',
                    line_number=20
                ),
                TestResult(
                    name='test_password_reset',
                    status='passed',
                    failure_code=None,
                    error_message=None,
                    file_path='tests/test_auth.py',
                    line_number=30
                ),
            ],
            summary='3 tests: 3 passed (state: GREEN)'
        )

    @pytest.fixture
    def broken_evidence(self):
        """BROKEN state test evidence."""
        return TestEvidence(
            state='BROKEN',
            total_tests=3,
            passed=0,
            failed=0,
            errors=3,
            skipped=0,
            results=[
                TestResult(
                    name='test_login',
                    status='error',
                    failure_code='TEST_BROKEN',
                    error_message='SyntaxError: invalid syntax',
                    file_path='tests/test_auth.py',
                    line_number=10
                ),
                TestResult(
                    name='test_logout',
                    status='error',
                    failure_code='ENV_BROKEN',
                    error_message='ModuleNotFoundError: No module named pytest',
                    file_path='tests/test_auth.py',
                    line_number=20
                ),
                TestResult(
                    name='test_password_reset',
                    status='error',
                    failure_code='TEST_BROKEN',
                    error_message='IndentationError: unexpected indent',
                    file_path='tests/test_auth.py',
                    line_number=30
                ),
            ],
            summary='3 tests: 3 errors (state: BROKEN)'
        )

    def test_validate_red_state_success(self, tmp_path, mock_config, red_evidence):
        """Test successful RED state validation."""
        with patch('lib.test_runner.run_tests') as mock_run, \
             patch('lib.test_runner.parse_pytest_output') as mock_parse, \
             patch('lib.test_runner.load_patterns') as mock_load:

            mock_run.return_value = (1, "test output", "")
            mock_parse.return_value = red_evidence
            mock_load.return_value = {}

            result = validate_red_state(tmp_path, mock_config, 'feat-auth')

            assert result['state'] == 'RED'
            assert result['validation_passed'] is True
            assert 'Ready for implementation' in result['message']
            assert result['evidence'] == red_evidence
            assert 'timestamp' in result
            assert 'output' in result

    def test_validate_red_state_green_failure(self, tmp_path, mock_config, green_evidence):
        """Test validation failure when tests are GREEN."""
        with patch('lib.test_runner.run_tests') as mock_run, \
             patch('lib.test_runner.parse_pytest_output') as mock_parse, \
             patch('lib.test_runner.load_patterns') as mock_load:

            mock_run.return_value = (0, "test output", "")
            mock_parse.return_value = green_evidence
            mock_load.return_value = {}

            result = validate_red_state(tmp_path, mock_config, 'feat-auth')

            assert result['state'] == 'GREEN'
            assert result['validation_passed'] is False
            assert 'already passing' in result['message']
            assert 'No implementation needed' in result['message']

    def test_validate_red_state_broken_failure(self, tmp_path, mock_config, broken_evidence):
        """Test validation failure when tests are BROKEN."""
        with patch('lib.test_runner.run_tests') as mock_run, \
             patch('lib.test_runner.parse_pytest_output') as mock_parse, \
             patch('lib.test_runner.load_patterns') as mock_load:

            mock_run.return_value = (2, "test output", "")
            mock_parse.return_value = broken_evidence
            mock_load.return_value = {}

            result = validate_red_state(tmp_path, mock_config, 'feat-auth')

            assert result['state'] == 'BROKEN'
            assert result['validation_passed'] is False
            assert 'broken' in result['message'].lower()
            assert 'Fix test issues' in result['message']

    def test_validate_red_state_message_includes_summary(self, tmp_path, mock_config, red_evidence):
        """Test that validation message includes test summary."""
        with patch('lib.test_runner.run_tests') as mock_run, \
             patch('lib.test_runner.parse_pytest_output') as mock_parse, \
             patch('lib.test_runner.load_patterns') as mock_load:

            mock_run.return_value = (1, "test output", "")
            mock_parse.return_value = red_evidence
            mock_load.return_value = {}

            result = validate_red_state(tmp_path, mock_config, 'feat-auth')

            # Message should include failing test names/codes
            assert 'feat-auth' in result['message']
            assert 'Failing:' in result['message']

    def test_validate_red_state_truncates_long_lists(self, tmp_path, mock_config):
        """Test that long test lists are truncated in message."""
        # Create evidence with many failing tests
        results = [
            TestResult(
                name=f'test_{i}',
                status='failed',
                failure_code='MISSING_BEHAVIOR',
                error_message=f'Test {i} failed',
                file_path='tests/test_many.py',
                line_number=i*10
            )
            for i in range(10)
        ]

        many_fails_evidence = TestEvidence(
            state='RED',
            total_tests=10,
            passed=0,
            failed=10,
            errors=0,
            skipped=0,
            results=results,
            summary='10 tests: 10 failed (state: RED)'
        )

        with patch('lib.test_runner.run_tests') as mock_run, \
             patch('lib.test_runner.parse_pytest_output') as mock_parse, \
             patch('lib.test_runner.load_patterns') as mock_load:

            mock_run.return_value = (1, "test output", "")
            mock_parse.return_value = many_fails_evidence
            mock_load.return_value = {}

            result = validate_red_state(tmp_path, mock_config, 'feat-many')

            # Message should truncate to first 3 and add "and N more"
            assert 'and 7 more' in result['message']
