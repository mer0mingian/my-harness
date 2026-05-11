#!/usr/bin/env python3
"""Unit tests for TDD sequence enforcer hook handler.

Tests the PreToolUse hook that enforces RED before GREEN constitutional requirement.
Blocks implementation code writes unless tests are in RED state.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hooks.handlers.tdd_sequence_enforcer import (
    read_hook_input,
    is_source_code_write,
    extract_feature_id,
    validate_red_state,
    build_response,
    main
)


class TestReadHookInput:
    """Test reading and parsing hook input from stdin."""

    def test_read_valid_json(self):
        """Should parse valid JSON hook input."""
        input_data = {
            "tool": "Write",
            "args": {"file_path": "src/main.py", "content": "..."},
            "context": {"feature_id": "feat-123"}
        }
        input_json = json.dumps(input_data)

        with patch('sys.stdin.read', return_value=input_json):
            result = read_hook_input()

        assert result == input_data

    def test_read_empty_input(self):
        """Should handle empty input gracefully."""
        with patch('sys.stdin.read', return_value=''):
            with pytest.raises(ValueError, match="Empty input"):
                read_hook_input()

    def test_read_invalid_json(self):
        """Should raise error on invalid JSON."""
        with patch('sys.stdin.read', return_value='{invalid}'):
            with pytest.raises(ValueError, match="Invalid JSON"):
                read_hook_input()


class TestIsSourceCodeWrite:
    """Test detection of source code writes."""

    def test_detects_src_write(self):
        """Should detect writes to src/ directory."""
        hook_data = {
            "tool": "Write",
            "args": {"file_path": "src/auth/login.py"}
        }
        assert is_source_code_write(hook_data) is True

    def test_detects_app_write(self):
        """Should detect writes to app/ directory."""
        hook_data = {
            "tool": "Write",
            "args": {"file_path": "app/main.py"}
        }
        assert is_source_code_write(hook_data) is True

    def test_ignores_test_write(self):
        """Should not detect writes to tests/ directory."""
        hook_data = {
            "tool": "Write",
            "args": {"file_path": "tests/test_auth.py"}
        }
        assert is_source_code_write(hook_data) is False

    def test_ignores_docs_write(self):
        """Should not detect writes to docs/ directory."""
        hook_data = {
            "tool": "Write",
            "args": {"file_path": "docs/README.md"}
        }
        assert is_source_code_write(hook_data) is False

    def test_ignores_config_write(self):
        """Should not detect writes to config files."""
        hook_data = {
            "tool": "Write",
            "args": {"file_path": "pyproject.toml"}
        }
        assert is_source_code_write(hook_data) is False

    def test_handles_missing_file_path(self):
        """Should handle missing file_path gracefully."""
        hook_data = {
            "tool": "Write",
            "args": {}
        }
        assert is_source_code_write(hook_data) is False

    def test_handles_non_write_tool(self):
        """Should return False for non-Write tools."""
        hook_data = {
            "tool": "Read",
            "args": {"file_path": "src/main.py"}
        }
        assert is_source_code_write(hook_data) is False


class TestExtractFeatureId:
    """Test feature ID extraction from context."""

    def test_extract_from_context(self):
        """Should extract feature_id from context."""
        hook_data = {
            "context": {"feature_id": "feat-123"}
        }
        assert extract_feature_id(hook_data) == "feat-123"

    def test_extract_missing_context(self):
        """Should return None when context is missing."""
        hook_data = {}
        assert extract_feature_id(hook_data) is None

    def test_extract_missing_feature_id(self):
        """Should return None when feature_id is missing."""
        hook_data = {
            "context": {"other_key": "value"}
        }
        assert extract_feature_id(hook_data) is None

    def test_extract_empty_feature_id(self):
        """Should return None for empty feature_id."""
        hook_data = {
            "context": {"feature_id": ""}
        }
        assert extract_feature_id(hook_data) is None


class TestValidateRedState:
    """Test RED state validation via subprocess."""

    def test_valid_red_state(self):
        """Should return True and output for valid RED state."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "state": "RED",
            "validation_passed": True,
            "message": "Valid RED state"
        })

        # Mock both Path.exists and subprocess.run
        with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
            with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                is_valid, output = validate_red_state("feat-123", Path("/tmp/test"))

        assert is_valid is True
        assert output["state"] == "RED"
        assert output["validation_passed"] is True

    def test_green_state_blocked(self):
        """Should return False for GREEN state (tests passing)."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps({
            "state": "GREEN",
            "validation_passed": False,
            "message": "Tests are passing"
        })

        with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
            with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                is_valid, output = validate_red_state("feat-123", Path("/tmp/test"))

        assert is_valid is False
        assert output["state"] == "GREEN"

    def test_broken_state_blocked(self):
        """Should return False for BROKEN state (tests broken)."""
        mock_result = Mock()
        mock_result.returncode = 2
        mock_result.stdout = json.dumps({
            "state": "BROKEN",
            "validation_passed": False,
            "message": "Tests are broken"
        })

        with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
            with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                is_valid, output = validate_red_state("feat-123", Path("/tmp/test"))

        assert is_valid is False
        assert output["state"] == "BROKEN"

    def test_handles_script_not_found(self):
        """Should handle missing validation script."""
        with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', side_effect=FileNotFoundError("Script not found")):
            is_valid, output = validate_red_state("feat-123", Path("/tmp/test"))

        assert is_valid is False
        assert "error" in output
        assert "not found" in output["error"].lower()

    def test_handles_timeout(self):
        """Should handle validation timeout."""
        with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
            with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="test", timeout=30)):
                is_valid, output = validate_red_state("feat-123", Path("/tmp/test"))

        assert is_valid is False
        assert "error" in output

    def test_handles_invalid_json_output(self):
        """Should handle invalid JSON from validation script."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "not json"

        with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
            with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                is_valid, output = validate_red_state("feat-123", Path("/tmp/test"))

        assert is_valid is False
        assert "error" in output


class TestBuildResponse:
    """Test response building."""

    def test_allow_response(self):
        """Should build allow response."""
        validation_output = {
            "state": "RED",
            "validation_passed": True,
            "message": "Valid RED state"
        }

        response = build_response(
            action="allow",
            reason="Tests in RED state",
            validation_output=validation_output
        )

        assert response["action"] == "allow"
        assert response["reason"] == "Tests in RED state"
        assert response["red_state_validation"]["state"] == "RED"

    def test_block_response(self):
        """Should build block response."""
        validation_output = {
            "state": "GREEN",
            "validation_passed": False,
            "message": "Tests passing"
        }

        response = build_response(
            action="block",
            reason="Tests not in RED state",
            validation_output=validation_output
        )

        assert response["action"] == "block"
        assert response["reason"] == "Tests not in RED state"
        assert response["red_state_validation"]["state"] == "GREEN"

    def test_response_without_validation_output(self):
        """Should build response without validation output."""
        response = build_response(
            action="block",
            reason="No feature_id provided"
        )

        assert response["action"] == "block"
        assert response["reason"] == "No feature_id provided"
        assert response["red_state_validation"] is None


class TestMain:
    """Test main execution flow."""

    def test_allows_non_source_write(self, capsys):
        """Should allow non-source code writes without validation."""
        input_data = {
            "tool": "Write",
            "args": {"file_path": "tests/test_auth.py"},
            "context": {"feature_id": "feat-123"}
        }

        with patch('sys.stdin.read', return_value=json.dumps(input_data)):
            exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["action"] == "allow"
        assert "Not a source code write" in response["reason"]

    def test_blocks_source_write_without_feature_id(self, capsys):
        """Should block source writes without feature_id."""
        input_data = {
            "tool": "Write",
            "args": {"file_path": "src/main.py"},
            "context": {}
        }

        with patch('sys.stdin.read', return_value=json.dumps(input_data)):
            exit_code = main()

        assert exit_code == 2
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["action"] == "block"
        assert "No feature_id" in response["reason"]

    def test_allows_source_write_with_valid_red(self, capsys):
        """Should allow source write when tests are in valid RED state."""
        input_data = {
            "tool": "Write",
            "args": {"file_path": "src/auth/login.py"},
            "context": {"feature_id": "feat-123"}
        }

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "state": "RED",
            "validation_passed": True,
            "message": "Valid RED state"
        })

        with patch('sys.stdin.read', return_value=json.dumps(input_data)):
            with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
                with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                    exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["action"] == "allow"
        assert "Valid RED state" in response["reason"]

    def test_blocks_source_write_with_green_state(self, capsys):
        """Should block source write when tests are passing (GREEN)."""
        input_data = {
            "tool": "Write",
            "args": {"file_path": "src/auth/login.py"},
            "context": {"feature_id": "feat-123"}
        }

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps({
            "state": "GREEN",
            "validation_passed": False,
            "message": "Tests already passing"
        })

        with patch('sys.stdin.read', return_value=json.dumps(input_data)):
            with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
                with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                    exit_code = main()

        assert exit_code == 2
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["action"] == "block"
        assert "Tests already passing" in response["reason"]

    def test_blocks_source_write_with_broken_state(self, capsys):
        """Should block source write when tests are broken."""
        input_data = {
            "tool": "Write",
            "args": {"file_path": "src/auth/login.py"},
            "context": {"feature_id": "feat-123"}
        }

        mock_result = Mock()
        mock_result.returncode = 2
        mock_result.stdout = json.dumps({
            "state": "BROKEN",
            "validation_passed": False,
            "message": "Tests are broken"
        })

        with patch('sys.stdin.read', return_value=json.dumps(input_data)):
            with patch('hooks.handlers.tdd_sequence_enforcer.Path.exists', return_value=True):
                with patch('hooks.handlers.tdd_sequence_enforcer.subprocess.run', return_value=mock_result):
                    exit_code = main()

        assert exit_code == 2
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["action"] == "block"
        assert "Tests are broken" in response["reason"]

    def test_handles_invalid_input(self, capsys):
        """Should handle invalid input gracefully."""
        with patch('sys.stdin.read', return_value='invalid json'):
            exit_code = main()

        assert exit_code == 2
        captured = capsys.readouterr()
        response = json.loads(captured.out)
        assert response["action"] == "block"
        assert "error" in response["reason"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
