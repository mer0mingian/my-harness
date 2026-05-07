#!/usr/bin/env python3
"""Unit tests for scripts/parse_pytest_output.py CLI wrapper."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Get paths
SCRIPT_DIR = Path(__file__).parent.parent.parent / "scripts"
PARSE_SCRIPT = SCRIPT_DIR / "parse_pytest_output.py"


class TestParsePytestOutputCLI:
    """Test parse_pytest_output.py CLI wrapper."""

    def test_script_exists(self):
        """Verify script file exists."""
        assert PARSE_SCRIPT.exists(), f"Script not found: {PARSE_SCRIPT}"

    def test_reads_from_stdin(self):
        """Test reading pytest output from stdin."""
        pytest_output = """
============================= test session starts ==============================
collected 5 items

tests/test_auth.py::test_login PASSED                                    [ 20%]
tests/test_auth.py::test_logout PASSED                                   [ 40%]
tests/test_api.py::test_create_user FAILED                               [ 60%]
tests/test_api.py::test_delete_user PASSED                               [ 80%]
tests/test_api.py::test_update_user PASSED                               [100%]

=========================== short test summary info ============================
FAILED tests/test_api.py::test_create_user - AssertionError: assert False
========================= 4 passed, 1 failed in 0.12s ==========================
"""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT)],
            input=pytest_output,
            capture_output=True,
            text=True,
        )

        # Should exit with code 1 (RED state - has failures)
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"

        # Output should be valid JSON
        output = json.loads(result.stdout)

        # Verify structure
        assert output["state"] == "RED"
        assert output["total_tests"] == 5
        assert output["passed"] == 4
        assert output["failed"] == 1
        assert "results" in output
        assert "summary" in output

    def test_reads_from_file(self):
        """Test reading pytest output from file using --file flag."""
        pytest_output = """
============================= test session starts ==============================
collected 3 items

tests/test_sample.py::test_one PASSED                                    [ 33%]
tests/test_sample.py::test_two PASSED                                    [ 66%]
tests/test_sample.py::test_three PASSED                                  [100%]

============================== 3 passed in 0.05s ===============================
"""
        # Create temp file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(pytest_output)
            temp_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, str(PARSE_SCRIPT), "--file", temp_file],
                capture_output=True,
                text=True,
            )

            # Should exit with code 0 (GREEN state - all pass)
            assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"

            # Output should be valid JSON
            output = json.loads(result.stdout)

            # Verify GREEN state
            assert output["state"] == "GREEN"
            assert output["total_tests"] == 3
            assert output["passed"] == 3
            assert output["failed"] == 0

        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_exit_code_green(self):
        """Test exit code 0 for GREEN state."""
        pytest_output = """
============================= test session starts ==============================
collected 1 items

tests/test_sample.py::test_pass PASSED                                   [100%]

============================== 1 passed in 0.01s ===============================
"""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT)],
            input=pytest_output,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_exit_code_red(self):
        """Test exit code 1 for RED state (normal test failures)."""
        pytest_output = """
============================= test session starts ==============================
collected 1 items

tests/test_sample.py::test_fail FAILED                                   [100%]

=========================== short test summary info ============================
FAILED tests/test_sample.py::test_fail - AssertionError: Expected True
============================== 1 failed in 0.01s ===============================
"""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT)],
            input=pytest_output,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1

    def test_exit_code_broken(self):
        """Test exit code 2 for BROKEN state (env/test broken)."""
        pytest_output = """
============================= test session starts ==============================
collected 1 items

tests/test_sample.py::test_error ERROR                                   [100%]

=========================== short test summary info ============================
ERROR tests/test_sample.py::test_error - ModuleNotFoundError: No module named 'foo'
============================== 1 error in 0.01s ================================
"""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT)],
            input=pytest_output,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2

    def test_empty_stdin_error(self):
        """Test exit code 1 for empty stdin."""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT)],
            input="",
            capture_output=True,
            text=True,
        )

        # Should exit with error code 1 (parse error)
        assert result.returncode == 1

    def test_file_not_found_error(self):
        """Test exit code 2 for file not found."""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT), "--file", "/nonexistent/file.txt"],
            capture_output=True,
            text=True,
        )

        # Should exit with error code 2 (system error)
        assert result.returncode == 2
        assert "Error" in result.stderr or result.returncode == 2

    def test_json_output_structure(self):
        """Test that JSON output has correct structure."""
        pytest_output = """
============================= test session starts ==============================
collected 2 items

tests/test_sample.py::test_one PASSED                                    [ 50%]
tests/test_sample.py::test_two FAILED                                    [100%]

=========================== short test summary info ============================
FAILED tests/test_sample.py::test_two - AssertionError
========================= 1 passed, 1 failed in 0.01s ==========================
"""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT)],
            input=pytest_output,
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)

        # Required fields
        assert "state" in output
        assert "total_tests" in output
        assert "passed" in output
        assert "failed" in output
        assert "errors" in output
        assert "skipped" in output
        assert "results" in output
        assert "summary" in output

        # State should be one of the valid values
        assert output["state"] in ["RED", "GREEN", "BROKEN"]

        # Results should be a list
        assert isinstance(output["results"], list)

    def test_verbose_flag_accepted(self):
        """Test that --verbose flag is accepted (even if not used)."""
        pytest_output = """
============================= test session starts ==============================
collected 1 items

tests/test_sample.py::test_pass PASSED                                   [100%]

============================== 1 passed in 0.01s ===============================
"""
        result = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT), "--verbose"],
            input=pytest_output,
            capture_output=True,
            text=True,
        )

        # Should still work and produce valid output
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["state"] == "GREEN"
