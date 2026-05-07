#!/usr/bin/env python3
"""Unit tests for validate_red_state.py script.

Tests the standalone RED state validation script according to TDD specifications.
We test the internal functions directly rather than subprocess calls for better control.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the script module for testing
import scripts.validate_red_state as vrs
from lib.parse_test_evidence import TestEvidence, TestResult


# Get path to script (for CLI tests)
SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "validate_red_state.py"


@pytest.fixture
def mock_pytest_output_red():
    """Mock pytest output for valid RED state (MISSING_BEHAVIOR)."""
    return """
============================= test session starts ==============================
collected 5 items

tests/test_auth.py::TestAuth::test_login FAILED                          [ 20%]
tests/test_auth.py::TestAuth::test_logout FAILED                         [ 40%]
tests/test_auth.py::TestAuth::test_refresh FAILED                        [ 60%]
tests/test_profile.py::test_get_profile FAILED                           [ 80%]
tests/test_profile.py::test_update_profile FAILED                        [100%]

=================================== FAILURES ===================================
________________________________ test_login ________________________________
tests/test_auth.py:12: NotImplementedError
E   NotImplementedError: login not implemented

________________________________ test_logout ________________________________
tests/test_auth.py:18: AssertionError
E   AssertionError: assert False == True

=========================== short test summary info ============================
FAILED tests/test_auth.py::TestAuth::test_login - NotImplementedError: login not implemented
FAILED tests/test_auth.py::TestAuth::test_logout - AssertionError: assert False == True
FAILED tests/test_auth.py::TestAuth::test_refresh - NotImplementedError
FAILED tests/test_profile.py::test_get_profile - NotImplementedError
FAILED tests/test_profile.py::test_update_profile - AssertionError
============================== 5 failed in 0.12s ================================
"""


@pytest.fixture
def mock_pytest_output_green():
    """Mock pytest output for GREEN state (all passing)."""
    return """
============================= test session starts ==============================
collected 5 items

tests/test_auth.py::TestAuth::test_login PASSED                          [ 20%]
tests/test_auth.py::TestAuth::test_logout PASSED                         [ 40%]
tests/test_auth.py::TestAuth::test_refresh PASSED                        [ 60%]
tests/test_profile.py::test_get_profile PASSED                           [ 80%]
tests/test_profile.py::test_update_profile PASSED                        [100%]

============================== 5 passed in 0.08s ================================
"""


@pytest.fixture
def mock_pytest_output_broken():
    """Mock pytest output for BROKEN state (TEST_BROKEN)."""
    return """
============================= test session starts ==============================
collected 3 items

tests/test_auth.py::TestAuth::test_login ERROR                           [ 33%]
tests/test_auth.py::TestAuth::test_logout ERROR                          [ 66%]
tests/test_profile.py::test_get_profile ERROR                            [100%]

==================================== ERRORS ====================================
_____________________________ test_login _____________________________
tests/test_auth.py:10: SyntaxError
E   SyntaxError: invalid syntax

_____________________________ test_logout _____________________________
tests/test_auth.py:20: ImportError
E   ImportError: cannot import name 'auth_service'

=========================== short test summary info ============================
ERROR tests/test_auth.py::TestAuth::test_login - SyntaxError: invalid syntax
ERROR tests/test_auth.py::TestAuth::test_logout - ImportError: cannot import name 'auth_service'
ERROR tests/test_profile.py::test_get_profile - ModuleNotFoundError: No module named 'profile_lib'
============================== 3 error in 0.05s =================================
"""


@pytest.fixture
def mock_pytest_not_found():
    """Mock scenario where pytest is not installed."""
    return FileNotFoundError("pytest not found")


class TestValidateRedStateExitCodes:
    """Test exit code behavior of validate_red_state internal functions."""

    def test_valid_red_state_returns_exit_0(self):
        """Test that valid RED state returns exit code 0."""
        # Create mock evidence for RED state
        evidence = TestEvidence(
            state="RED",
            total_tests=5,
            passed=0,
            failed=5,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="failed",
                    failure_code="MISSING_BEHAVIOR",
                    error_message="NotImplementedError: not implemented",
                    file_path="tests/test_auth.py",
                    line_number=12
                ),
                TestResult(
                    name="test_logout",
                    status="failed",
                    failure_code="ASSERTION_MISMATCH",
                    error_message="AssertionError: assert False == True",
                    file_path="tests/test_auth.py",
                    line_number=18
                ),
            ],
            summary="5 tests: 5 failed (state: RED)"
        )

        exit_code, output = vrs.validate_red_state(evidence, "feat-123")
        assert exit_code == 0, f"Expected exit 0 for valid RED, got {exit_code}"
        assert output["validation_passed"] is True

    def test_green_state_returns_exit_1(self):
        """Test that GREEN state (tests passing) returns exit code 1."""
        evidence = TestEvidence(
            state="GREEN",
            total_tests=5,
            passed=5,
            failed=0,
            errors=0,
            skipped=0,
            results=[],
            summary="5 tests: 5 passed (state: GREEN)"
        )

        exit_code, output = vrs.validate_red_state(evidence, "feat-456")
        assert exit_code == 1, f"Expected exit 1 for GREEN, got {exit_code}"
        assert output["validation_passed"] is False

    def test_broken_state_returns_exit_2(self):
        """Test that BROKEN state returns exit code 2."""
        evidence = TestEvidence(
            state="BROKEN",
            total_tests=3,
            passed=0,
            failed=0,
            errors=3,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="error",
                    failure_code="TEST_BROKEN",
                    error_message="SyntaxError: invalid syntax",
                    file_path="tests/test_auth.py",
                    line_number=10
                ),
            ],
            summary="3 tests: 3 error (state: BROKEN)"
        )

        exit_code, output = vrs.validate_red_state(evidence, "feat-789")
        assert exit_code == 2, f"Expected exit 2 for BROKEN, got {exit_code}"
        assert output["validation_passed"] is False


class TestValidateRedStateJSONOutput:
    """Test JSON output structure and content."""

    def test_json_has_required_fields(self):
        """Test that JSON output has all required fields."""
        evidence = TestEvidence(
            state="RED",
            total_tests=5,
            passed=0,
            failed=5,
            errors=0,
            skipped=0,
            results=[],
            summary="5 tests: 5 failed (state: RED)"
        )

        exit_code, output = vrs.validate_red_state(evidence, "feat-123")

        # Check required fields
        assert "state" in output
        assert "evidence" in output
        assert "validation_passed" in output
        assert "message" in output

    def test_red_state_json_structure(self):
        """Test JSON structure for valid RED state."""
        evidence = TestEvidence(
            state="RED",
            total_tests=5,
            passed=0,
            failed=5,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="failed",
                    failure_code="MISSING_BEHAVIOR",
                    error_message="NotImplementedError",
                    file_path="tests/test_auth.py",
                    line_number=12
                ),
                TestResult(
                    name="test_logout",
                    status="failed",
                    failure_code="ASSERTION_MISMATCH",
                    error_message="AssertionError",
                    file_path="tests/test_auth.py",
                    line_number=18
                ),
            ],
            summary="5 tests: 5 failed (state: RED)"
        )

        exit_code, output = vrs.validate_red_state(evidence, "feat-123")

        assert output["state"] == "RED"
        assert output["validation_passed"] is True
        assert output["evidence"]["test_count"] == 5
        assert output["evidence"]["failed_count"] == 5
        assert "MISSING_BEHAVIOR" in output["evidence"]["failure_codes"]
        assert "ASSERTION_MISMATCH" in output["evidence"]["failure_codes"]


class TestValidateRedStateFailureClassification:
    """Test failure code classification logic."""

    def test_classifies_missing_behavior(self):
        """Test MISSING_BEHAVIOR classification."""
        evidence = TestEvidence(
            state="RED",
            total_tests=1,
            passed=0,
            failed=1,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="failed",
                    failure_code="MISSING_BEHAVIOR",
                    error_message="NotImplementedError: function not implemented",
                    file_path="tests/test_auth.py",
                    line_number=12
                ),
            ],
            summary="1 tests: 1 failed (state: RED)"
        )

        failure_codes = vrs.classify_failure_codes(evidence)
        assert "MISSING_BEHAVIOR" in failure_codes

        exit_code, output = vrs.validate_red_state(evidence, "feat-123")
        assert exit_code == 0  # Valid RED

    def test_classifies_assertion_mismatch(self):
        """Test ASSERTION_MISMATCH classification."""
        evidence = TestEvidence(
            state="RED",
            total_tests=1,
            passed=0,
            failed=1,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="failed",
                    failure_code="ASSERTION_MISMATCH",
                    error_message="AssertionError: assert 1 == 2",
                    file_path="tests/test_auth.py",
                    line_number=12
                ),
            ],
            summary="1 tests: 1 failed (state: RED)"
        )

        failure_codes = vrs.classify_failure_codes(evidence)
        assert "ASSERTION_MISMATCH" in failure_codes

        exit_code, output = vrs.validate_red_state(evidence, "feat-123")
        assert exit_code == 0  # Valid RED

    def test_classifies_test_broken(self):
        """Test TEST_BROKEN classification."""
        evidence = TestEvidence(
            state="BROKEN",
            total_tests=1,
            passed=0,
            failed=0,
            errors=1,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="error",
                    failure_code="TEST_BROKEN",
                    error_message="SyntaxError: invalid syntax",
                    file_path="tests/test_auth.py",
                    line_number=10
                ),
            ],
            summary="1 tests: 1 error (state: BROKEN)"
        )

        failure_codes = vrs.classify_failure_codes(evidence)
        assert "TEST_BROKEN" in failure_codes

        exit_code, output = vrs.validate_red_state(evidence, "feat-123")
        assert exit_code == 2  # Escalate


class TestValidateRedStateEdgeCases:
    """Test edge cases and error handling."""

    def test_no_tests_found(self):
        """Test handling when no tests are found."""
        exit_code, output = vrs.handle_no_tests("feat-123")

        # Should return exit 1 (invalid state - no work to do)
        assert exit_code == 1
        assert "no tests" in output["message"].lower()
        assert output["evidence"]["test_count"] == 0

    def test_pytest_not_found(self):
        """Test handling when pytest is not installed."""
        error = FileNotFoundError("pytest not found")
        exit_code, output = vrs.handle_pytest_error(error, "feat-123")

        # Should return exit 2 (system error)
        assert exit_code == 2
        assert "pytest" in output["message"].lower()


class TestValidateRedStateCLI:
    """Test CLI behavior (without mocking internal functions)."""

    def test_requires_feature_id(self):
        """Test that feature_id is required."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True
        )

        # Should fail due to missing required argument
        assert result.returncode != 0
        assert "feature_id" in result.stderr or "required" in result.stderr
