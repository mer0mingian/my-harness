#!/usr/bin/env python3
"""Unit tests for escalate_broken_tests.py script.

Tests the standalone escalation report generator for broken tests.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

import pytest


# Test fixtures
SAMPLE_EVIDENCE_BROKEN = {
    "state": "BROKEN",
    "total_tests": 3,
    "passed": 1,
    "failed": 2,
    "errors": 0,
    "skipped": 0,
    "results": [
        {
            "name": "test_login",
            "status": "passed",
            "failure_code": None,
            "error_message": None,
            "file_path": "tests/test_auth.py",
            "line_number": 10
        },
        {
            "name": "test_broken_syntax",
            "status": "failed",
            "failure_code": "TEST_BROKEN",
            "error_message": "SyntaxError: invalid syntax at line 42",
            "file_path": "tests/test_broken.py",
            "line_number": 42
        },
        {
            "name": "test_missing_module",
            "status": "failed",
            "failure_code": "ENV_BROKEN",
            "error_message": "ModuleNotFoundError: No module named 'missing_lib'",
            "file_path": "tests/test_env.py",
            "line_number": 15
        }
    ],
    "summary": "2 failed, 1 passed"
}

SAMPLE_EVIDENCE_VALID_RED = {
    "state": "RED",
    "total_tests": 2,
    "passed": 0,
    "failed": 2,
    "errors": 0,
    "skipped": 0,
    "results": [
        {
            "name": "test_feature_a",
            "status": "failed",
            "failure_code": "MISSING_BEHAVIOR",
            "error_message": "NotImplementedError",
            "file_path": "tests/test_feature.py",
            "line_number": 20
        },
        {
            "name": "test_feature_b",
            "status": "failed",
            "failure_code": "ASSERTION_MISMATCH",
            "error_message": "AssertionError: expected 10 but got 5",
            "file_path": "tests/test_feature.py",
            "line_number": 30
        }
    ],
    "summary": "2 failed"
}


def get_script_path() -> Path:
    """Get path to escalate_broken_tests.py script."""
    return Path(__file__).parent.parent.parent / "scripts" / "escalate_broken_tests.py"


class TestEscalateBrokenTestsStdin:
    """Tests for reading TestEvidence from stdin."""

    def test_broken_tests_escalation(self, tmp_path: Path):
        """Should generate escalation report for broken tests."""
        script = get_script_path()

        result = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(SAMPLE_EVIDENCE_BROKEN),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nStderr: {result.stderr}"

        output = json.loads(result.stdout)

        # Validate structure
        assert output["escalation_required"] is True
        assert len(output["failure_codes"]) == 2
        assert "TEST_BROKEN" in output["failure_codes"]
        assert "ENV_BROKEN" in output["failure_codes"]

        # Validate root causes
        assert len(output["root_causes"]) == 2

        # Find TEST_BROKEN root cause
        test_broken = next(rc for rc in output["root_causes"] if rc["code"] == "TEST_BROKEN")
        assert "syntax" in test_broken["diagnosis"].lower()
        assert "fix" in test_broken["recommendation"].lower()
        assert "test_broken_syntax" in test_broken["affected_tests"]

        # Find ENV_BROKEN root cause
        env_broken = next(rc for rc in output["root_causes"] if rc["code"] == "ENV_BROKEN")
        assert "environment" in env_broken["diagnosis"].lower() or "configuration" in env_broken["diagnosis"].lower()
        assert "test_missing_module" in env_broken["affected_tests"]

        # Validate summary
        assert "2 tests broken" in output["summary"].lower()

    def test_valid_red_state_no_escalation(self):
        """Should exit 1 when no broken tests found (valid RED state)."""
        script = get_script_path()

        result = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(SAMPLE_EVIDENCE_VALID_RED),
            capture_output=True,
            text=True
        )

        assert result.returncode == 1, f"Expected exit 1 for no escalation, got {result.returncode}"


class TestEscalateBrokenTestsFile:
    """Tests for reading TestEvidence from file."""

    def test_read_from_file(self, tmp_path: Path):
        """Should read TestEvidence from --file argument."""
        script = get_script_path()
        evidence_file = tmp_path / "evidence.json"
        evidence_file.write_text(json.dumps(SAMPLE_EVIDENCE_BROKEN))

        result = subprocess.run(
            [sys.executable, str(script), "--file", str(evidence_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["escalation_required"] is True


class TestEscalateBrokenTestsHumanFormat:
    """Tests for human-readable output format."""

    def test_human_readable_format(self):
        """Should generate human-readable report with --format human."""
        script = get_script_path()

        result = subprocess.run(
            [sys.executable, str(script), "--format", "human"],
            input=json.dumps(SAMPLE_EVIDENCE_BROKEN),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Should contain human-readable elements
        assert "ESCALATION REQUIRED" in result.stdout
        assert "TEST_BROKEN" in result.stdout
        assert "ENV_BROKEN" in result.stdout
        assert "test_broken_syntax" in result.stdout
        assert "test_missing_module" in result.stdout
        assert "Root Cause:" in result.stdout or "Diagnosis:" in result.stdout
        assert "Recommendation:" in result.stdout or "Action:" in result.stdout


class TestEscalateBrokenTestsErrorHandling:
    """Tests for error conditions."""

    def test_invalid_json(self):
        """Should exit 2 on invalid JSON input."""
        script = get_script_path()

        result = subprocess.run(
            [sys.executable, str(script)],
            input="not valid json",
            capture_output=True,
            text=True
        )

        assert result.returncode == 2

    def test_missing_file(self):
        """Should exit 2 on missing input file."""
        script = get_script_path()

        result = subprocess.run(
            [sys.executable, str(script), "--file", "/nonexistent/file.json"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 2


class TestFailureCodeMapping:
    """Tests for specific failure code mappings."""

    def test_import_error_mapping(self):
        """Should map ImportError to root cause and recommendation."""
        evidence = {
            "state": "BROKEN",
            "total_tests": 1,
            "passed": 0,
            "failed": 1,
            "errors": 0,
            "skipped": 0,
            "results": [
                {
                    "name": "test_import",
                    "status": "failed",
                    "failure_code": "IMPORT_ERROR",
                    "error_message": "ImportError: cannot import name 'foo'",
                    "file_path": "tests/test_imports.py",
                    "line_number": 5
                }
            ],
            "summary": "1 failed"
        }

        script = get_script_path()
        result = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(evidence),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)

        import_error = next(rc for rc in output["root_causes"] if rc["code"] == "IMPORT_ERROR")
        assert "import" in import_error["diagnosis"].lower()
        assert "pythonpath" in import_error["recommendation"].lower() or "install" in import_error["recommendation"].lower()

    def test_syntax_error_mapping(self):
        """Should map SyntaxError to root cause and recommendation."""
        evidence = {
            "state": "BROKEN",
            "total_tests": 1,
            "passed": 0,
            "failed": 1,
            "errors": 0,
            "skipped": 0,
            "results": [
                {
                    "name": "test_syntax",
                    "status": "failed",
                    "failure_code": "SYNTAX_ERROR",
                    "error_message": "SyntaxError: invalid syntax",
                    "file_path": "tests/test_syntax.py",
                    "line_number": 10
                }
            ],
            "summary": "1 failed"
        }

        script = get_script_path()
        result = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(evidence),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)

        syntax_error = next(rc for rc in output["root_causes"] if rc["code"] == "SYNTAX_ERROR")
        assert "syntax" in syntax_error["diagnosis"].lower()
        assert "linter" in syntax_error["recommendation"].lower() or "fix" in syntax_error["recommendation"].lower()
