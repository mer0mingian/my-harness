#!/usr/bin/env python3
"""
Unit tests for hooks/handlers/file_gate_enforcer.py

Tests the constitutional enforcement hook that blocks non-test files during test phase.
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
HANDLER_PATH = PROJECT_ROOT / "hooks" / "handlers" / "file_gate_enforcer.py"


class TestFileGateEnforcer:
    """Test suite for file gate enforcer hook handler."""

    def test_allows_test_file_in_tests_directory(self):
        """Test files in tests/ directory should be allowed."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "tests/test_foo.py",
                "content": "test content"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Should allow test file, got exit code {result.returncode}"

        output = json.loads(result.stdout)
        assert output["action"] == "allow"
        assert "reason" in output

    def test_allows_test_file_with_test_prefix(self):
        """Files matching test_*.py pattern should be allowed."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "test_bar.py",
                "content": "test content"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["action"] == "allow"

    def test_allows_test_file_with_test_suffix(self):
        """Files matching *_test.py pattern should be allowed."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "foo_test.py",
                "content": "test content"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["action"] == "allow"

    def test_blocks_implementation_file(self):
        """Implementation files should be blocked during test phase."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "src/main.py",
                "content": "implementation code"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 2, f"Should block implementation file, got exit code {result.returncode}"

        output = json.loads(result.stdout)
        assert output["action"] == "block"
        assert "reason" in output
        assert "test phase" in output["reason"].lower()

    def test_blocks_arbitrary_python_file(self):
        """Arbitrary Python files should be blocked during test phase."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "utils.py",
                "content": "some code"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 2
        output = json.loads(result.stdout)
        assert output["action"] == "block"

    def test_handles_nested_test_paths(self):
        """Test files in nested paths should be allowed."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "tests/unit/auth/test_login.py",
                "content": "test content"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["action"] == "allow"

    def test_handles_absolute_paths(self):
        """Absolute paths to test files should be allowed."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "/home/user/project/tests/test_auth.py",
                "content": "test content"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["action"] == "allow"

    def test_handles_missing_phase(self):
        """Hook should handle missing phase gracefully."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "src/main.py",
                "content": "code"
            }
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        # Should allow by default when phase is not specified
        assert result.returncode == 0

    def test_only_enforces_during_test_phase(self):
        """Hook should not block during other phases."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "src/main.py",
                "content": "code"
            },
            "phase": "implement"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        # Should allow during implement phase
        assert result.returncode == 0

    def test_handles_malformed_json_input(self):
        """Hook should handle malformed JSON gracefully."""
        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input="not valid json",
            capture_output=True,
            text=True
        )

        # Should exit with error code
        assert result.returncode != 0

    def test_validates_json_output_structure(self):
        """All outputs should be valid JSON with required fields."""
        hook_input = {
            "tool": "Write",
            "args": {
                "file_path": "tests/test_foo.py",
                "content": "test"
            },
            "phase": "test"
        }

        result = subprocess.run(
            [sys.executable, str(HANDLER_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        output = json.loads(result.stdout)
        assert "action" in output
        assert "reason" in output
        assert output["action"] in ["allow", "block"]
