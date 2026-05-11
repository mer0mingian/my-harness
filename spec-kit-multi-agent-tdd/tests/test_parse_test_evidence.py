"""Tests for test evidence parser.

Test-driven development for S2B-003: Build Test Evidence Parser Script
"""

import json
import pytest
from pathlib import Path
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from parse_test_evidence import (
    TestResult,
    TestEvidence,
    parse_pytest_output,
    classify_failure,
    detect_state,
)


@pytest.fixture
def patterns():
    """Shared patterns fixture for all test classes."""
    return {
        "failure_codes": {
            "MISSING_BEHAVIOR": [
                r"(?i)not implemented",
                r"(?i)notimplementederror",
                r"(?i)abstractmethod",
                r"(?i)function.*has no implementation",
            ],
            "ASSERTION_MISMATCH": [
                r"(?i)assert.*failed",
                r"(?i)assertionerror",
                r"(?i)expected.*but.*got",
                r"(?i)AssertionError:",
            ],
            "TEST_BROKEN": [
                r"(?i)syntaxerror",
                r"(?i)indentationerror",
                r"(?i)nameerror",
                r"(?i)importerror",
                r"(?i)attributeerror.*test",
            ],
            "ENV_BROKEN": [
                r"(?i)modulenotfounderror",
                r"(?i)connection.*refused",
                r"(?i)permission denied",
                r"(?i)no such file or directory",
                r"(?i)timeout",
            ],
        },
        "pytest_patterns": {
            "test_line": r"^(.+\.py)::(\w+)::(\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
            "test_line_no_class": r"^(.+\.py)::(\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
            "summary_line": r"^=+ (\d+) (passed|failed|errors?|skipped)",
            "final_summary": r"^=+\s+(.+)\s+in\s+[\d\.]+s\s*=+$",
            "failure_start": r"^_+ (.+) _+$",
            "error_section": r"^=+ ERRORS =+$",
            "failure_section": r"^=+ FAILURES =+$",
            "error_message": r"^E\s+(.*)$",
            "location_line": r"^(.+\.py):(\d+):\s*(\w+)$",
            "collected": r"^collected (\d+) items?",
        },
    }


# Sample pytest outputs for testing
PYTEST_OUTPUT_GREEN = """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 3 items

tests/test_auth.py::test_login PASSED                                    [ 33%]
tests/test_auth.py::test_logout PASSED                                   [ 66%]
tests/test_api.py::test_create_user PASSED                              [100%]

============================== 3 passed in 0.12s ===============================
"""

PYTEST_OUTPUT_RED_MISSING_BEHAVIOR = """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 2 items

tests/test_auth.py::test_login FAILED                                    [ 50%]
tests/test_auth.py::test_logout PASSED                                   [100%]

=================================== FAILURES ===================================
_________________________________ test_login ___________________________________

    def test_login():
>       raise NotImplementedError("login function not implemented")
E       NotImplementedError: login function not implemented

tests/test_auth.py:10: NotImplementedError
=========================== short test summary info ============================
FAILED tests/test_auth.py::test_login - NotImplementedError: login function not implemented
========================= 1 failed, 1 passed in 0.12s ==========================
"""

PYTEST_OUTPUT_RED_ASSERTION_MISMATCH = """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 2 items

tests/test_auth.py::test_login PASSED                                    [ 50%]
tests/test_auth.py::test_logout FAILED                                   [100%]

=================================== FAILURES ===================================
_________________________________ test_logout __________________________________

    def test_logout():
>       assert auth.logout() == True
E       AssertionError: assert False == True

tests/test_auth.py:15: AssertionError
=========================== short test summary info ============================
FAILED tests/test_auth.py::test_logout - AssertionError: assert False == True
========================= 1 passed, 1 failed in 0.12s ==========================
"""

PYTEST_OUTPUT_BROKEN_TEST_BROKEN = """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 1 items

tests/test_api.py F                                                      [100%]

=================================== FAILURES ===================================
_______________________________ test_create_user _______________________________

tests/test_api.py:5: in <module>
    def test_create_user()
                         ^
E   SyntaxError: invalid syntax

=========================== short test summary info ============================
FAILED tests/test_api.py::test_create_user - SyntaxError: invalid syntax
============================== 1 failed in 0.12s ================================
"""

PYTEST_OUTPUT_BROKEN_ENV_BROKEN = """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 1 items

tests/test_api.py E                                                      [100%]

==================================== ERRORS ====================================
_______________________________ test_create_user _______________________________

    def test_create_user():
>       from api.users import create_user
E       ModuleNotFoundError: No module named 'api.users'

tests/test_api.py:5: ModuleNotFoundError
=========================== short test summary info ============================
ERROR tests/test_api.py::test_create_user - ModuleNotFoundError: No module named 'api.users'
============================== 1 error in 0.12s =================================
"""

PYTEST_OUTPUT_MIXED = """============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0
collected 4 items

tests/test_auth.py::test_login PASSED                                    [ 25%]
tests/test_auth.py::test_logout FAILED                                   [ 50%]
tests/test_api.py::test_create_user ERROR                                [ 75%]
tests/test_api.py::test_delete_user SKIPPED                             [100%]

=================================== FAILURES ===================================
_________________________________ test_logout __________________________________

    def test_logout():
>       assert auth.logout() == True
E       AssertionError: assert False == True

tests/test_auth.py:15: AssertionError
==================================== ERRORS ====================================
_______________________________ test_create_user _______________________________

    def test_create_user():
>       from api.users import create_user
E       ModuleNotFoundError: No module named 'api.users'

tests/test_api.py:5: ModuleNotFoundError
=========================== short test summary info ============================
FAILED tests/test_auth.py::test_logout - AssertionError: assert False == True
ERROR tests/test_api.py::test_create_user - ModuleNotFoundError: No module named 'api.users'
================== 1 passed, 1 failed, 1 error, 1 skipped in 0.12s =============
"""


class TestClassifyFailure:
    """Test failure classification logic."""

    def test_classify_missing_behavior(self, patterns):
        """Test classification of MISSING_BEHAVIOR failures."""
        error_msg = "NotImplementedError: login function not implemented"
        assert classify_failure(error_msg, patterns) == "MISSING_BEHAVIOR"

    def test_classify_assertion_mismatch(self, patterns):
        """Test classification of ASSERTION_MISMATCH failures."""
        error_msg = "AssertionError: assert False == True"
        assert classify_failure(error_msg, patterns) == "ASSERTION_MISMATCH"

    def test_classify_test_broken(self, patterns):
        """Test classification of TEST_BROKEN failures."""
        error_msg = "SyntaxError: invalid syntax"
        assert classify_failure(error_msg, patterns) == "TEST_BROKEN"

    def test_classify_env_broken(self, patterns):
        """Test classification of ENV_BROKEN failures."""
        error_msg = "ModuleNotFoundError: No module named 'api.users'"
        assert classify_failure(error_msg, patterns) == "ENV_BROKEN"

    def test_classify_unknown(self, patterns):
        """Test classification of unknown failure types."""
        error_msg = "UnknownError: something weird happened"
        assert classify_failure(error_msg, patterns) == "UNKNOWN"


class TestDetectState:
    """Test state detection logic."""

    def test_detect_green_state(self):
        """Test GREEN state detection (all tests pass)."""
        evidence = TestEvidence(
            state="",
            total_tests=3,
            passed=3,
            failed=0,
            errors=0,
            skipped=0,
            results=[],
            summary="",
        )
        assert detect_state(evidence) == "GREEN"

    def test_detect_red_state_missing_behavior(self):
        """Test RED state detection with MISSING_BEHAVIOR."""
        evidence = TestEvidence(
            state="",
            total_tests=2,
            passed=1,
            failed=1,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_login",
                    status="failed",
                    failure_code="MISSING_BEHAVIOR",
                    error_message="NotImplementedError",
                    file_path="tests/test_auth.py",
                    line_number=10,
                )
            ],
            summary="",
        )
        assert detect_state(evidence) == "RED"

    def test_detect_red_state_assertion_mismatch(self):
        """Test RED state detection with ASSERTION_MISMATCH."""
        evidence = TestEvidence(
            state="",
            total_tests=2,
            passed=1,
            failed=1,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_logout",
                    status="failed",
                    failure_code="ASSERTION_MISMATCH",
                    error_message="AssertionError",
                    file_path="tests/test_auth.py",
                    line_number=15,
                )
            ],
            summary="",
        )
        assert detect_state(evidence) == "RED"

    def test_detect_broken_state_test_broken(self):
        """Test BROKEN state detection with TEST_BROKEN."""
        evidence = TestEvidence(
            state="",
            total_tests=1,
            passed=0,
            failed=1,
            errors=0,
            skipped=0,
            results=[
                TestResult(
                    name="test_create_user",
                    status="failed",
                    failure_code="TEST_BROKEN",
                    error_message="SyntaxError",
                    file_path="tests/test_api.py",
                    line_number=5,
                )
            ],
            summary="",
        )
        assert detect_state(evidence) == "BROKEN"

    def test_detect_broken_state_env_broken(self):
        """Test BROKEN state detection with ENV_BROKEN."""
        evidence = TestEvidence(
            state="",
            total_tests=1,
            passed=0,
            failed=0,
            errors=1,
            skipped=0,
            results=[
                TestResult(
                    name="test_create_user",
                    status="error",
                    failure_code="ENV_BROKEN",
                    error_message="ModuleNotFoundError",
                    file_path="tests/test_api.py",
                    line_number=5,
                )
            ],
            summary="",
        )
        assert detect_state(evidence) == "BROKEN"


class TestParsePytestOutput:
    """Test pytest output parsing."""

    def test_parse_green_output(self, patterns):
        """Test parsing of GREEN (all pass) output."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_GREEN, patterns)

        assert evidence.state == "GREEN"
        assert evidence.total_tests == 3
        assert evidence.passed == 3
        assert evidence.failed == 0
        assert evidence.errors == 0
        assert evidence.skipped == 0
        assert len(evidence.results) == 3
        assert all(r.status == "passed" for r in evidence.results)

    def test_parse_red_missing_behavior(self, patterns):
        """Test parsing of RED output with MISSING_BEHAVIOR."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_RED_MISSING_BEHAVIOR, patterns)

        assert evidence.state == "RED"
        assert evidence.total_tests == 2
        assert evidence.passed == 1
        assert evidence.failed == 1

        failed_test = next(r for r in evidence.results if r.status == "failed")
        assert failed_test.failure_code == "MISSING_BEHAVIOR"
        assert "NotImplementedError" in failed_test.error_message

    def test_parse_red_assertion_mismatch(self, patterns):
        """Test parsing of RED output with ASSERTION_MISMATCH."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_RED_ASSERTION_MISMATCH, patterns)

        assert evidence.state == "RED"
        assert evidence.total_tests == 2
        assert evidence.passed == 1
        assert evidence.failed == 1

        failed_test = next(r for r in evidence.results if r.status == "failed")
        assert failed_test.failure_code == "ASSERTION_MISMATCH"
        assert "AssertionError" in failed_test.error_message

    def test_parse_broken_test_broken(self, patterns):
        """Test parsing of BROKEN output with TEST_BROKEN."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_BROKEN_TEST_BROKEN, patterns)

        assert evidence.state == "BROKEN"
        assert evidence.total_tests == 1
        assert evidence.failed == 1

        failed_test = evidence.results[0]
        assert failed_test.failure_code == "TEST_BROKEN"
        assert "SyntaxError" in failed_test.error_message

    def test_parse_broken_env_broken(self, patterns):
        """Test parsing of BROKEN output with ENV_BROKEN."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_BROKEN_ENV_BROKEN, patterns)

        assert evidence.state == "BROKEN"
        assert evidence.total_tests == 1
        assert evidence.errors == 1

        error_test = evidence.results[0]
        assert error_test.failure_code == "ENV_BROKEN"
        assert "ModuleNotFoundError" in error_test.error_message

    def test_parse_mixed_output(self, patterns):
        """Test parsing of mixed output with multiple states."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_MIXED, patterns)

        # Should be BROKEN due to ENV_BROKEN taking precedence
        assert evidence.state == "BROKEN"
        assert evidence.total_tests == 4
        assert evidence.passed == 1
        assert evidence.failed == 1
        assert evidence.errors == 1
        assert evidence.skipped == 1

        # Check all results are captured
        assert len(evidence.results) == 4


class TestDataClasses:
    """Test data class structures."""

    def test_test_result_creation(self):
        """Test TestResult data class."""
        result = TestResult(
            name="test_login",
            status="passed",
            failure_code=None,
            error_message=None,
            file_path="tests/test_auth.py",
            line_number=10,
        )

        assert result.name == "test_login"
        assert result.status == "passed"
        assert result.failure_code is None
        assert result.error_message is None

    def test_test_evidence_creation(self):
        """Test TestEvidence data class."""
        evidence = TestEvidence(
            state="GREEN",
            total_tests=3,
            passed=3,
            failed=0,
            errors=0,
            skipped=0,
            results=[],
            summary="3 tests: 3 passed (state: GREEN)",
        )

        assert evidence.state == "GREEN"
        assert evidence.total_tests == 3
        assert evidence.passed == 3
        assert "GREEN" in evidence.summary


class TestIntegration:
    """Integration tests with real pytest outputs."""

    def test_end_to_end_green(self, patterns):
        """End-to-end test: GREEN state workflow."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_GREEN, patterns)

        # Verify all aspects of parsing
        assert evidence.state == "GREEN"
        assert evidence.total_tests == evidence.passed
        assert len(evidence.results) == 3
        assert "3 passed" in evidence.summary

    def test_end_to_end_red(self, patterns):
        """End-to-end test: RED state workflow."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_RED_MISSING_BEHAVIOR, patterns)

        # Verify RED state is properly detected
        assert evidence.state == "RED"
        assert evidence.failed > 0

        # Verify failure classification
        failed_tests = [r for r in evidence.results if r.status == "failed"]
        assert all(
            r.failure_code in ["MISSING_BEHAVIOR", "ASSERTION_MISMATCH"]
            for r in failed_tests
        )

    def test_end_to_end_broken(self, patterns):
        """End-to-end test: BROKEN state workflow."""
        evidence = parse_pytest_output(PYTEST_OUTPUT_BROKEN_ENV_BROKEN, patterns)

        # Verify BROKEN state is properly detected
        assert evidence.state == "BROKEN"

        # Verify failure classification
        broken_tests = [
            r
            for r in evidence.results
            if r.failure_code in ["TEST_BROKEN", "ENV_BROKEN"]
        ]
        assert len(broken_tests) > 0
