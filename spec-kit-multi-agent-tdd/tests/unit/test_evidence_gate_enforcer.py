#!/usr/bin/env python3
"""
Unit tests for evidence_gate_enforcer hook handler.

Tests the pre-commit hook that validates feature artifacts before allowing git commits.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Add hooks/handlers to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "handlers"))

from evidence_gate_enforcer import (
    extract_feature_id,
    is_git_commit_command,
    parse_hook_input,
    validate_and_respond,
)


class TestParseHookInput:
    """Test hook input parsing from stdin."""

    def test_parse_valid_json(self):
        """Should parse valid hook JSON input."""
        input_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }
        input_json = json.dumps(input_data)

        result = parse_hook_input(input_json)

        assert result == input_data

    def test_parse_invalid_json(self):
        """Should raise ValueError on invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_hook_input("not valid json")

    def test_parse_empty_input(self):
        """Should raise ValueError on empty input."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_hook_input("")


class TestIsGitCommitCommand:
    """Test git commit command detection."""

    def test_detects_simple_commit(self):
        """Should detect simple git commit."""
        assert is_git_commit_command("git commit -m 'message'")

    def test_detects_commit_with_flags(self):
        """Should detect commit with various flags."""
        assert is_git_commit_command("git commit -am 'message'")
        assert is_git_commit_command("git commit --amend")
        assert is_git_commit_command("git commit --no-verify -m 'msg'")

    def test_detects_commit_with_whitespace(self):
        """Should handle extra whitespace."""
        assert is_git_commit_command("  git  commit  -m 'msg'  ")

    def test_ignores_non_commit_commands(self):
        """Should not match non-commit git commands."""
        assert not is_git_commit_command("git status")
        assert not is_git_commit_command("git add .")
        assert not is_git_commit_command("git push")
        assert not is_git_commit_command("git log --oneline")

    def test_ignores_commit_in_message(self):
        """Should not match 'commit' in other contexts."""
        assert not is_git_commit_command("echo 'git commit'")
        assert not is_git_commit_command("cat commit.txt")


class TestExtractFeatureId:
    """Test feature ID extraction."""

    def test_extracts_from_context(self):
        """Should extract feature_id from context."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'message'"},
            "context": {"feature_id": "feat-123"},
        }

        feature_id = extract_feature_id(hook_data)
        assert feature_id == "feat-123"

    def test_extracts_from_commit_message_prefix(self):
        """Should extract from feat-XXX prefix in commit message."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-456: Add new feature'"},
            "context": {},
        }

        feature_id = extract_feature_id(hook_data)
        assert feature_id == "feat-456"

    def test_extracts_from_commit_message_brackets(self):
        """Should extract from [feat-XXX] in commit message."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m '[feat-789] Update code'"},
            "context": {},
        }

        feature_id = extract_feature_id(hook_data)
        assert feature_id == "feat-789"

    def test_extracts_from_multiline_message(self):
        """Should extract from multiline commit message."""
        hook_data = {
            "tool": "Bash",
            "args": {
                "command": "git commit -m 'feat-999: Title\n\nDetailed description'"
            },
            "context": {},
        }

        feature_id = extract_feature_id(hook_data)
        assert feature_id == "feat-999"

    def test_prefers_context_over_message(self):
        """Should prefer context feature_id over parsed message."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-111: Message'"},
            "context": {"feature_id": "feat-222"},
        }

        feature_id = extract_feature_id(hook_data)
        assert feature_id == "feat-222"

    def test_returns_none_when_not_found(self):
        """Should return None when feature_id not found."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'Fix typo'"},
            "context": {},
        }

        feature_id = extract_feature_id(hook_data)
        assert feature_id is None


class TestValidateAndRespond:
    """Test validation and response generation."""

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_allows_commit_when_valid(self, mock_run):
        """Should allow commit when artifacts are valid."""
        # Mock successful validation
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "feature_id": "feat-123",
                "valid": True,
                "artifacts": {},
                "evidence": {},
                "errors": [],
            }
        )
        mock_run.return_value = mock_result

        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }

        response, exit_code = validate_and_respond(hook_data)

        assert exit_code == 0
        assert response["action"] == "allow"
        assert "valid" in response["reason"].lower()
        assert response["validation_report"]["valid"] is True

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_blocks_commit_when_invalid(self, mock_run):
        """Should block commit when artifacts are invalid."""
        # Mock failed validation
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps(
            {
                "feature_id": "feat-123",
                "valid": False,
                "artifacts": {"test_design": {"exists": False}},
                "evidence": {},
                "errors": ["Mandatory artifact missing: test_design"],
            }
        )
        mock_run.return_value = mock_result

        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }

        response, exit_code = validate_and_respond(hook_data)

        assert exit_code == 2
        assert response["action"] == "block"
        assert "invalid" in response["reason"].lower()
        assert response["validation_report"]["valid"] is False

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_blocks_when_no_feature_id(self, mock_run):
        """Should block commit when feature_id cannot be extracted."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'Fix typo'"},
            "context": {},
        }

        response, exit_code = validate_and_respond(hook_data)

        assert exit_code == 2
        assert response["action"] == "block"
        assert "feature_id" in response["reason"].lower()

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_blocks_on_validation_script_error(self, mock_run):
        """Should block commit when validation script fails."""
        # Mock script error
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stderr = "Script error"
        mock_run.return_value = mock_result

        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }

        response, exit_code = validate_and_respond(hook_data)

        assert exit_code == 2
        assert response["action"] == "block"
        assert "error" in response["reason"].lower()

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_calls_validation_script_correctly(self, mock_run):
        """Should call validate_artifacts.py with correct arguments."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {"feature_id": "feat-123", "valid": True, "artifacts": {}, "errors": []}
        )
        mock_run.return_value = mock_result

        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }

        validate_and_respond(hook_data)

        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "python3" in call_args[0]
        assert any("validate_artifacts.py" in str(arg) for arg in call_args)
        assert "feat-123" in call_args
        assert "--format" in call_args
        assert "json" in call_args


class TestHookIntegration:
    """Integration tests for the hook handler."""

    def test_non_git_command_passes_through(self, capsys):
        """Should not intercept non-git commands."""
        hook_data = {
            "tool": "Bash",
            "args": {"command": "ls -la"},
            "context": {},
        }

        # The hook should not process this
        result = is_git_commit_command(hook_data["args"]["command"])
        assert result is False

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_end_to_end_allow_flow(self, mock_run, capsys):
        """Test complete flow for allowing commit."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "feature_id": "feat-123",
                "valid": True,
                "artifacts": {},
                "evidence": {},
                "errors": [],
            }
        )
        mock_run.return_value = mock_result

        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }

        response, exit_code = validate_and_respond(hook_data)

        assert exit_code == 0
        assert response["action"] == "allow"

    @patch("evidence_gate_enforcer.subprocess.run")
    def test_end_to_end_block_flow(self, mock_run, capsys):
        """Test complete flow for blocking commit."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps(
            {
                "feature_id": "feat-123",
                "valid": False,
                "artifacts": {},
                "evidence": {},
                "errors": ["Missing test design"],
            }
        )
        mock_run.return_value = mock_result

        hook_data = {
            "tool": "Bash",
            "args": {"command": "git commit -m 'feat-123: Add feature'"},
            "context": {"feature_id": "feat-123"},
        }

        response, exit_code = validate_and_respond(hook_data)

        assert exit_code == 2
        assert response["action"] == "block"
