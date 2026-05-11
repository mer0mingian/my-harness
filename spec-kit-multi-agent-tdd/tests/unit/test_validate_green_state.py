#!/usr/bin/env python3
"""Unit tests for validate_green_state.py script.

Tests the standalone GREEN state validation script according to TDD specifications.
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
import scripts.validate_green_state as vgs
from lib.parse_test_evidence import TestEvidence, TestResult


# Get path to script (for CLI tests)
SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "validate_green_state.py"


@pytest.fixture
def mock_pytest_output_green():
    """Mock pytest output for GREEN state (all passing) with coverage."""
    return """
============================= test session starts ==============================
collected 5 items

tests/test_auth.py::TestAuth::test_login PASSED                          [ 20%]
tests/test_auth.py::TestAuth::test_logout PASSED                         [ 40%]
tests/test_auth.py::TestAuth::test_refresh PASSED                        [ 60%]
tests/test_profile.py::test_get_profile PASSED                           [ 80%]
tests/test_profile.py::test_update_profile PASSED                        [100%]

---------- coverage: platform linux, python 3.11.0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
src/auth.py                 45      5    89%
src/profile.py              30      3    90%
--------------------------------------------
TOTAL                       75      8    89%

============================== 5 passed in 0.08s ================================
"""


@pytest.fixture
def mock_pytest_output_red():
    """Mock pytest output for RED state (still failing)."""
    return """
============================= test session starts ==============================
collected 5 items

tests/test_auth.py::TestAuth::test_login FAILED                          [ 20%]
tests/test_auth.py::TestAuth::test_logout PASSED                         [ 40%]
tests/test_auth.py::TestAuth::test_refresh PASSED                        [ 60%]
tests/test_profile.py::test_get_profile FAILED                           [ 80%]
tests/test_profile.py::test_update_profile PASSED                        [100%]

=================================== FAILURES ===================================
________________________________ test_login ________________________________
tests/test_auth.py:12: AssertionError
E   AssertionError: assert False == True

=========================== short test summary info ============================
FAILED tests/test_auth.py::TestAuth::test_login - AssertionError: assert False == True
FAILED tests/test_profile.py::test_get_profile - NotImplementedError
========================== 2 failed, 3 passed in 0.12s =========================
"""


@pytest.fixture
def mock_pytest_output_broken():
    """Mock pytest output for BROKEN state (import errors)."""
    return """
============================= test session starts ==============================
collected 3 items

tests/test_auth.py::TestAuth::test_login ERROR                           [ 33%]
tests/test_auth.py::TestAuth::test_logout ERROR                          [ 66%]
tests/test_profile.py::test_get_profile PASSED                           [100%]

==================================== ERRORS ====================================
_____________________________ test_login _____________________________
tests/test_auth.py:10: ImportError
E   ImportError: cannot import name 'auth_service'

=========================== short test summary info ============================
ERROR tests/test_auth.py::TestAuth::test_login - ImportError: cannot import name 'auth_service'
ERROR tests/test_auth.py::TestAuth::test_logout - SyntaxError: invalid syntax
======================= 2 error, 1 passed in 0.05s ============================
"""


class TestValidateGreenStateExitCodes:
    """Test exit code behavior of validate_green_state internal functions."""

    def test_valid_green_state_returns_exit_0(self):
        """Test that valid GREEN state returns exit code 0."""
        # Create mock evidence for GREEN state
        evidence = TestEvidence(
            state="GREEN",
            total_tests=5,
            passed=5,
            failed=0,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="passed",
                    failure_code=None,
                    error_message=None,
                    file_path="tests/test_auth.py",
                    line_number=12
                ),
            ],
            summary="5 tests: 5 passed (state: GREEN)"
        )

        coverage = {"percentage": 85, "statements": 120, "missing": 18, "found": True}

        exit_code, output = vgs.validate_green_state(
            evidence, "feat-123", coverage=coverage
        )
        assert exit_code == 0, f"Expected exit 0 for valid GREEN, got {exit_code}"
        assert output["validation_passed"] is True

    def test_red_state_returns_exit_1(self):
        """Test that RED state (still failing) returns exit code 1."""
        evidence = TestEvidence(
            state="RED",
            total_tests=5,
            passed=3,
            failed=2,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="failed",
                    failure_code="ASSERTION_MISMATCH",
                    error_message="AssertionError: assert False == True",
                    file_path="tests/test_auth.py",
                    line_number=12
                ),
            ],
            summary="5 tests: 2 failed, 3 passed (state: RED)"
        )

        exit_code, output = vgs.validate_green_state(evidence, "feat-456")
        assert exit_code == 1, f"Expected exit 1 for RED, got {exit_code}"
        assert output["validation_passed"] is False

    def test_broken_state_returns_exit_2(self):
        """Test that BROKEN state returns exit code 2."""
        evidence = TestEvidence(
            state="BROKEN",
            total_tests=3,
            passed=1,
            failed=0,
            errors=2,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="error",
                    failure_code="IMPORT_ERROR",
                    error_message="ImportError: cannot import",
                    file_path="tests/test_auth.py",
                    line_number=10
                ),
            ],
            summary="3 tests: 2 error, 1 passed (state: BROKEN)"
        )

        exit_code, output = vgs.validate_green_state(evidence, "feat-789")
        assert exit_code == 2, f"Expected exit 2 for BROKEN, got {exit_code}"
        assert output["validation_passed"] is False


class TestValidateGreenStateRegressionDetection:
    """Test regression detection when baseline count provided."""

    def test_regression_detected_when_tests_deleted(self):
        """Test that regression is detected when test count decreases."""
        evidence = TestEvidence(
            state="GREEN",
            total_tests=3,
            passed=3,
            failed=0,
            errors=0,
            skipped=0,
            results=[],
            summary="3 tests: 3 passed (state: GREEN)"
        )

        # Baseline was 5, now only 3 - tests were deleted
        exit_code, output = vgs.validate_green_state(
            evidence, "feat-789", baseline_count=5
        )

        assert exit_code == 2, "Should return exit 2 for regression"
        assert output["regression_detected"] is True
        assert "regression" in output["message"].lower()

    def test_no_regression_when_test_count_matches(self):
        """Test that no regression when test count matches baseline."""
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

        exit_code, output = vgs.validate_green_state(
            evidence, "feat-123", baseline_count=5
        )

        assert exit_code == 0, "Should return exit 0 for valid GREEN"
        assert output["regression_detected"] is False

    def test_no_regression_when_tests_added(self):
        """Test that no regression when test count increases (good)."""
        evidence = TestEvidence(
            state="GREEN",
            total_tests=7,
            passed=7,
            failed=0,
            errors=0,
            skipped=0,
            results=[],
            summary="7 tests: 7 passed (state: GREEN)"
        )

        exit_code, output = vgs.validate_green_state(
            evidence, "feat-123", baseline_count=5
        )

        assert exit_code == 0, "Should return exit 0 for valid GREEN with more tests"
        assert output["regression_detected"] is False


class TestValidateGreenStateJSONOutput:
    """Test JSON output structure and content."""

    def test_json_has_required_fields(self):
        """Test that JSON output has all required fields."""
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

        exit_code, output = vgs.validate_green_state(evidence, "feat-123")

        # Check required fields
        assert "state" in output
        assert "evidence" in output
        assert "validation_passed" in output
        assert "message" in output
        assert "regression_detected" in output

    def test_green_state_json_structure(self):
        """Test JSON structure for valid GREEN state."""
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

        coverage = {"percentage": 85, "statements": 120, "missing": 18, "found": True}

        exit_code, output = vgs.validate_green_state(
            evidence, "feat-123", coverage=coverage
        )

        assert output["state"] == "GREEN"
        assert output["validation_passed"] is True
        assert output["evidence"]["test_count"] == 5
        assert output["evidence"]["passed_count"] == 5
        assert output["evidence"]["failed_count"] == 0
        assert output["evidence"]["coverage"] == 85

    def test_coverage_included_in_evidence(self):
        """Test that coverage metrics are included in evidence."""
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

        coverage = {"percentage": 75, "statements": 100, "missing": 25, "found": True}

        exit_code, output = vgs.validate_green_state(
            evidence, "feat-123", coverage=coverage
        )

        assert "coverage" in output["evidence"]
        assert output["evidence"]["coverage"] == 75


class TestValidateGreenStateCoverageExtraction:
    """Test coverage metrics extraction from pytest output."""

    def test_extracts_coverage_from_pytest_output(self):
        """Test coverage extraction from pytest-cov output."""
        pytest_output = """
============================= test session starts ==============================
tests/test_auth.py::test_login PASSED

---------- coverage: platform linux, python 3.11.0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
src/auth.py                 120     18    85%
--------------------------------------------
TOTAL                       120     18    85%

============================== 1 passed in 0.08s ================================
"""

        coverage = vgs.extract_coverage_metrics(pytest_output)

        assert coverage is not None
        assert coverage["percentage"] == 85
        assert coverage["statements"] == 120
        assert coverage["missing"] == 18

    def test_returns_none_when_no_coverage(self):
        """Test that None returned when no coverage in output."""
        pytest_output = """
============================= test session starts ==============================
tests/test_auth.py::test_login PASSED
============================== 1 passed in 0.08s ================================
"""

        coverage = vgs.extract_coverage_metrics(pytest_output)
        assert coverage is None


class TestValidateGreenStateEdgeCases:
    """Test edge cases and error handling."""

    def test_no_tests_found(self):
        """Test handling when no tests are found."""
        exit_code, output = vgs.handle_no_tests("feat-123")

        # Should return exit 2 (system error - cannot validate without tests)
        assert exit_code == 2
        assert "no tests" in output["message"].lower()
        assert output["evidence"]["test_count"] == 0

    def test_pytest_not_found(self):
        """Test handling when pytest is not installed."""
        error = FileNotFoundError("pytest not found")
        exit_code, output = vgs.handle_pytest_error(error, "feat-123")

        # Should return exit 2 (system error)
        assert exit_code == 2
        assert "pytest" in output["message"].lower()


class TestValidateGreenStateCLI:
    """Test CLI behavior."""

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

    def test_accepts_baseline_count_argument(self):
        """Test that --baseline-count argument is accepted."""
        # This test just checks argument parsing works
        # We'd need a real test environment to validate behavior
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True
        )

        # Help should mention baseline-count
        assert "--baseline-count" in result.stdout or "--baseline" in result.stdout
