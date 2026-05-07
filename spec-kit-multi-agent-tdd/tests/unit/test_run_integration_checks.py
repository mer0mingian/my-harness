#!/usr/bin/env python3
"""
Unit tests for scripts/run_integration_checks.py

Tests the integration checks runner in isolation.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, call

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts import run_integration_checks


class TestLoadConfig:
    """Test configuration loading."""

    def test_loads_integration_checks_from_config(self, tmp_path):
        """Should load integration_checks section from config."""
        config_dir = tmp_path / ".specify"
        config_dir.mkdir()
        config_file = config_dir / "harness-tdd-config.yml"

        config_file.write_text("""
integration_checks:
  commands:
    - name: ruff
      cmd: "ruff check src/"
      critical: false
    - name: mypy
      cmd: "mypy src/"
      critical: true
""")

        config = run_integration_checks.load_config(tmp_path)

        assert "integration_checks" in config
        assert "commands" in config["integration_checks"]
        assert len(config["integration_checks"]["commands"]) == 2
        assert config["integration_checks"]["commands"][0]["name"] == "ruff"
        assert config["integration_checks"]["commands"][1]["critical"] is True

    def test_returns_empty_config_when_file_missing(self, tmp_path):
        """Should return default config when config file not found."""
        config = run_integration_checks.load_config(tmp_path)

        assert isinstance(config, dict)
        # Default config should have integration_checks disabled
        assert config.get("integration_checks", {}).get("enabled") is False

    def test_handles_malformed_yaml(self, tmp_path):
        """Should handle malformed YAML gracefully."""
        config_dir = tmp_path / ".specify"
        config_dir.mkdir()
        config_file = config_dir / "harness-tdd-config.yml"

        config_file.write_text("invalid: yaml: content:")

        config = run_integration_checks.load_config(tmp_path)

        # Should return default config
        assert isinstance(config, dict)


class TestExecuteCheck:
    """Test individual check execution."""

    @patch("subprocess.run")
    def test_executes_check_with_timeout(self, mock_run):
        """Should execute check command with configured timeout."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="All checks passed",
            stderr=""
        )

        check_config = {
            "name": "ruff",
            "cmd": "ruff check src/",
            "critical": False
        }

        result = run_integration_checks.execute_check(
            check_config, Path("/test"), timeout=30
        )

        mock_run.assert_called_once()
        args = mock_run.call_args
        assert args[1]["timeout"] == 30
        assert result["status"] == "passed"
        assert result["exit_code"] == 0

    @patch("subprocess.run")
    def test_handles_command_failure(self, mock_run):
        """Should handle non-zero exit codes."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Found 5 errors"
        )

        check_config = {
            "name": "mypy",
            "cmd": "mypy src/",
            "critical": True
        }

        result = run_integration_checks.execute_check(
            check_config, Path("/test"), timeout=60
        )

        assert result["status"] == "failed"
        assert result["exit_code"] == 1
        assert result["critical"] is True
        assert "Found 5 errors" in result["output"]

    @patch("subprocess.run")
    def test_handles_timeout(self, mock_run):
        """Should handle command timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="mypy src/", timeout=30
        )

        check_config = {
            "name": "mypy",
            "cmd": "mypy src/",
            "critical": True
        }

        result = run_integration_checks.execute_check(
            check_config, Path("/test"), timeout=30
        )

        assert result["status"] == "failed"
        assert "timed out" in result["output"].lower()

    @patch("subprocess.run")
    def test_handles_missing_tool(self, mock_run):
        """Should skip check when tool not found."""
        mock_run.side_effect = FileNotFoundError("[Errno 2] No such file or directory: 'ruff'")

        check_config = {
            "name": "ruff",
            "cmd": "ruff check src/",
            "critical": False
        }

        result = run_integration_checks.execute_check(
            check_config, Path("/test"), timeout=60
        )

        assert result["status"] == "skipped"
        assert "not found" in result["output"].lower()


class TestRunAllChecks:
    """Test running all configured checks."""

    @patch("scripts.run_integration_checks.execute_check")
    def test_runs_all_configured_checks(self, mock_execute):
        """Should execute all checks from config."""
        mock_execute.return_value = {
            "name": "test",
            "status": "passed",
            "critical": False,
            "output": "",
            "exit_code": 0
        }

        config = {
            "integration_checks": {
                "commands": [
                    {"name": "ruff", "cmd": "ruff check", "critical": False},
                    {"name": "mypy", "cmd": "mypy src/", "critical": True}
                ]
            }
        }

        results = run_integration_checks.run_all_checks(
            Path("/test"), config, timeout=60
        )

        assert len(results) == 2
        assert mock_execute.call_count == 2

    def test_returns_empty_for_no_checks(self):
        """Should return empty list when no checks configured."""
        config = {"integration_checks": {"commands": []}}

        results = run_integration_checks.run_all_checks(
            Path("/test"), config, timeout=60
        )

        assert results == []


class TestClassifyResults:
    """Test result classification."""

    def test_classifies_all_passed(self):
        """Should classify when all checks pass."""
        results = [
            {"status": "passed", "critical": False},
            {"status": "passed", "critical": True}
        ]

        summary = run_integration_checks.classify_results(results)

        assert summary["all_passed"] is True
        assert summary["critical_failed"] is False

    def test_classifies_non_critical_failure(self):
        """Should classify non-critical failures."""
        results = [
            {"status": "failed", "critical": False},
            {"status": "passed", "critical": True}
        ]

        summary = run_integration_checks.classify_results(results)

        assert summary["all_passed"] is False
        assert summary["critical_failed"] is False

    def test_classifies_critical_failure(self):
        """Should classify critical failures."""
        results = [
            {"status": "passed", "critical": False},
            {"status": "failed", "critical": True}
        ]

        summary = run_integration_checks.classify_results(results)

        assert summary["all_passed"] is False
        assert summary["critical_failed"] is True

    def test_handles_skipped_checks(self):
        """Should handle skipped checks correctly."""
        results = [
            {"status": "skipped", "critical": False},
            {"status": "passed", "critical": True}
        ]

        summary = run_integration_checks.classify_results(results)

        # Skipped checks don't affect pass/fail
        assert summary["all_passed"] is True
        assert summary["critical_failed"] is False


class TestExitCodes:
    """Test exit code determination."""

    def test_exit_0_when_all_passed(self):
        """Should return 0 when all checks pass."""
        summary = {"all_passed": True, "critical_failed": False}

        exit_code = run_integration_checks.determine_exit_code(summary)

        assert exit_code == 0

    def test_exit_1_when_non_critical_failed(self):
        """Should return 1 when only non-critical checks fail."""
        summary = {"all_passed": False, "critical_failed": False}

        exit_code = run_integration_checks.determine_exit_code(summary)

        assert exit_code == 1

    def test_exit_2_when_critical_failed(self):
        """Should return 2 when critical checks fail."""
        summary = {"all_passed": False, "critical_failed": True}

        exit_code = run_integration_checks.determine_exit_code(summary)

        assert exit_code == 2


class TestOutputFormat:
    """Test JSON output format."""

    def test_outputs_valid_json(self):
        """Should output valid JSON to stdout."""
        results = [
            {
                "name": "ruff",
                "status": "passed",
                "critical": False,
                "output": "All good",
                "exit_code": 0
            }
        ]

        output = run_integration_checks.format_output(results)
        data = json.loads(output)

        assert "checks" in data
        assert "all_passed" in data
        assert "critical_failed" in data
        assert len(data["checks"]) == 1

    def test_includes_all_check_fields(self):
        """Should include all required fields in output."""
        results = [
            {
                "name": "mypy",
                "status": "failed",
                "critical": True,
                "output": "Type error",
                "exit_code": 1
            }
        ]

        output = run_integration_checks.format_output(results)
        data = json.loads(output)

        check = data["checks"][0]
        assert check["name"] == "mypy"
        assert check["status"] == "failed"
        assert check["critical"] is True
        assert check["output"] == "Type error"
        assert check["exit_code"] == 1


class TestCLIIntegration:
    """Test command-line interface."""

    @patch("scripts.run_integration_checks.run_all_checks")
    @patch("scripts.run_integration_checks.load_config")
    def test_accepts_project_root_arg(self, mock_load, mock_run):
        """Should accept --project-root argument."""
        mock_load.return_value = {"integration_checks": {"commands": []}}
        mock_run.return_value = []

        with patch("sys.argv", ["run_integration_checks.py", "/test/path"]):
            exit_code = run_integration_checks.main()

        mock_load.assert_called_once()
        assert mock_load.call_args[0][0] == Path("/test/path")

    @patch("scripts.run_integration_checks.run_all_checks")
    @patch("scripts.run_integration_checks.load_config")
    def test_accepts_timeout_arg(self, mock_load, mock_run):
        """Should accept --timeout argument."""
        mock_load.return_value = {"integration_checks": {"commands": []}}
        mock_run.return_value = []

        with patch("sys.argv", ["run_integration_checks.py", "--timeout", "30"]):
            exit_code = run_integration_checks.main()

        mock_run.assert_called_once()
        assert mock_run.call_args[1]["timeout"] == 30

    @patch("scripts.run_integration_checks.run_all_checks")
    @patch("scripts.run_integration_checks.load_config")
    def test_defaults_to_current_directory(self, mock_load, mock_run):
        """Should default to current directory when no project_root given."""
        mock_load.return_value = {"integration_checks": {"commands": []}}
        mock_run.return_value = []

        with patch("sys.argv", ["run_integration_checks.py"]):
            exit_code = run_integration_checks.main()

        # Should be called with current directory
        called_path = mock_load.call_args[0][0]
        assert isinstance(called_path, Path)

    @patch("scripts.run_integration_checks.run_all_checks")
    @patch("scripts.run_integration_checks.load_config")
    def test_prints_json_to_stdout(self, mock_load, mock_run, capsys):
        """Should print JSON output to stdout."""
        mock_load.return_value = {"integration_checks": {"commands": []}}
        mock_run.return_value = []

        with patch("sys.argv", ["run_integration_checks.py"]):
            exit_code = run_integration_checks.main()

        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "checks" in data
