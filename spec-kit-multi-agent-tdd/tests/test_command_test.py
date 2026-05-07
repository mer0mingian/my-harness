#!/usr/bin/env python3
"""Tests for /speckit.multi-agent.test command implementation (S3-002)."""

import tempfile
from pathlib import Path
from datetime import datetime
import pytest
import sys
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.test import (
    find_spec_artifact,
    get_artifact_path,
    load_config,
    extract_acceptance_criteria,
    build_agent_context,
    spawn_test_agent,
    generate_test_design_artifact,
    execute_test_command,
)


class TestFindSpecArtifact:
    """Test spec artifact location and discovery."""

    def test_find_spec_in_docs_features(self, tmp_path):
        """Finds spec in docs/features directory."""
        spec_path = tmp_path / "docs" / "features" / "feat-123.md"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text("# Feature: User Login")

        result = find_spec_artifact("feat-123", project_root=tmp_path)
        assert result == spec_path

    def test_find_spec_in_docs_specs(self, tmp_path):
        """Finds spec in docs/specs directory."""
        spec_path = tmp_path / "docs" / "specs" / "feat-123-spec.md"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text("# Feature: User Login")

        result = find_spec_artifact("feat-123", project_root=tmp_path)
        assert result == spec_path

    def test_find_spec_in_specify_specs(self, tmp_path):
        """Finds spec in .specify/specs directory."""
        spec_path = tmp_path / ".specify" / "specs" / "feat-123.md"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text("# Feature: User Login")

        result = find_spec_artifact("feat-123", project_root=tmp_path)
        assert result == spec_path

    def test_find_spec_not_found(self, tmp_path):
        """Raises clear error when spec not found."""
        with pytest.raises(FileNotFoundError) as exc_info:
            find_spec_artifact("feat-999", project_root=tmp_path)

        # Error should list checked paths
        assert "feat-999" in str(exc_info.value)
        assert "docs/features" in str(exc_info.value)


class TestLoadConfig:
    """Test config file loading and defaults."""

    def test_load_config_from_file(self, tmp_path):
        """Loads config from .specify/harness-tdd-config.yml."""
        config_path = tmp_path / ".specify" / "harness-tdd-config.yml"
        config_path.parent.mkdir(parents=True)
        config_data = {
            "version": "1.0",
            "agents": {
                "test_agent": "test-specialist"
            },
            "artifacts": {
                "test_design": {
                    "path": "docs/tests/{feature_id}-test-design.md",
                    "mandatory": True
                }
            }
        }
        config_path.write_text(yaml.dump(config_data))

        result = load_config(project_root=tmp_path)
        assert result["version"] == "1.0"
        assert result["agents"]["test_agent"] == "test-specialist"

    def test_load_config_uses_defaults_when_missing(self, tmp_path):
        """Uses built-in defaults when config file not found."""
        result = load_config(project_root=tmp_path)

        # Should return default config
        assert "agents" in result
        assert "test_agent" in result["agents"]
        assert result["agents"]["test_agent"] == "test-specialist"
        assert "artifacts" in result
        assert "test_design" in result["artifacts"]

    def test_load_config_malformed_uses_defaults(self, tmp_path, capsys):
        """Uses defaults and warns when config is malformed."""
        config_path = tmp_path / ".specify" / "harness-tdd-config.yml"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("invalid: yaml: [unclosed")

        result = load_config(project_root=tmp_path)

        # Should return defaults
        assert "agents" in result
        assert result["agents"]["test_agent"] == "test-specialist"

        # Verify warning was emitted
        captured = capsys.readouterr()
        assert "WARNING: Config malformed" in captured.err


class TestGetArtifactPath:
    """Test artifact output path resolution."""

    def test_get_artifact_path_from_config(self, tmp_path):
        """Resolves path from config with template substitution."""
        config = {
            "artifacts": {
                "test_design": {
                    "path": "docs/tests/test-design/{feature_id}-test-design.md"
                }
            }
        }

        result = get_artifact_path("feat-123", config, project_root=tmp_path)
        expected = tmp_path / "docs" / "tests" / "test-design" / "feat-123-test-design.md"
        assert result == expected

    def test_get_artifact_path_creates_directories(self, tmp_path):
        """Creates parent directories if they don't exist."""
        config = {
            "artifacts": {
                "test_design": {
                    "path": "docs/tests/test-design/{feature_id}-test-design.md"
                }
            }
        }

        result = get_artifact_path("feat-123", config, project_root=tmp_path)
        assert result.parent.exists()

    def test_get_artifact_path_uses_default(self, tmp_path):
        """Uses default path when not in config."""
        config = {}  # Empty config

        result = get_artifact_path("feat-123", config, project_root=tmp_path)
        expected = tmp_path / "docs" / "tests" / "test-design" / "feat-123-test-design.md"
        assert result == expected


class TestExtractAcceptanceCriteria:
    """Test acceptance criteria extraction from spec."""

    def test_extract_ac_basic(self):
        """Extracts AC items from spec markdown."""
        spec_content = """
# Feature: User Login

## Acceptance Criteria
- AC-1: User can enter username and password
- AC-2: System validates credentials
- AC-3: User is redirected to dashboard on success

## Related Artifacts
- NFR-PERF-001
"""
        result = extract_acceptance_criteria(spec_content)
        assert len(result) == 3
        assert "AC-1: User can enter username and password" in result
        assert "AC-2: System validates credentials" in result
        assert "AC-3: User is redirected to dashboard on success" in result

    def test_extract_ac_stops_at_next_section(self):
        """Stops extracting at next heading."""
        spec_content = """
## Acceptance Criteria
- AC-1: First criterion
- AC-2: Second criterion

## Technical Requirements
- Not an AC item
"""
        result = extract_acceptance_criteria(spec_content)
        assert len(result) == 2
        assert "Not an AC item" not in result

    def test_extract_ac_empty_section(self):
        """Returns empty list when no AC section found."""
        spec_content = """
# Feature: User Login

## User Stories
- As a user...
"""
        result = extract_acceptance_criteria(spec_content)
        assert result == []

    def test_extract_ac_h3_heading(self):
        """Extracts AC from H3 heading (### Acceptance Criteria)."""
        spec_content = """
# Feature: User Login

### Acceptance Criteria
- AC-1: User can enter username
- AC-2: System validates input

### Technical Requirements
- Not an AC item
"""
        result = extract_acceptance_criteria(spec_content)
        assert len(result) == 2
        assert "AC-1: User can enter username" in result
        assert "AC-2: System validates input" in result
        assert "Not an AC item" not in result

    def test_extract_ac_uppercase_heading(self):
        """Extracts AC from uppercase heading (## ACCEPTANCE CRITERIA)."""
        spec_content = """
# Feature: User Login

## ACCEPTANCE CRITERIA
- AC-1: First criterion
- AC-2: Second criterion

## NEXT SECTION
- Not an AC item
"""
        result = extract_acceptance_criteria(spec_content)
        assert len(result) == 2
        assert "AC-1: First criterion" in result
        assert "AC-2: Second criterion" in result

    def test_extract_ac_asterisk_bullets(self):
        """Extracts AC items using asterisk bullets (* AC-1:)."""
        spec_content = """
## Acceptance Criteria
* AC-1: First criterion
* AC-2: Second criterion
- AC-3: Third criterion (dash bullet)

## Related Artifacts
"""
        result = extract_acceptance_criteria(spec_content)
        assert len(result) == 3
        assert "AC-1: First criterion" in result
        assert "AC-2: Second criterion" in result
        assert "AC-3: Third criterion (dash bullet)" in result

    def test_extract_ac_bold_formatting(self):
        """Extracts AC items with bold formatting (- **AC-1**:)."""
        spec_content = """
## Acceptance Criteria
- **AC-1**: First bold criterion
- **AC-2**: Second bold criterion

## Next Section
"""
        result = extract_acceptance_criteria(spec_content)
        assert len(result) == 2
        assert "**AC-1**: First bold criterion" in result
        assert "**AC-2**: Second bold criterion" in result


class TestBuildAgentContext:
    """Test agent context structure building."""

    def test_build_agent_context_complete(self):
        """Builds complete context for test agent."""
        spec_content = """
# Feature: User Login

## Acceptance Criteria
- AC-1: User can login
- AC-2: Invalid credentials rejected
"""
        config = {
            "test_framework": {
                "file_patterns": ["tests/**/*.py", "**/test_*.py"],
                "failure_codes": {
                    "valid_red": ["MISSING_BEHAVIOR", "ASSERTION_MISMATCH"]
                }
            }
        }

        result = build_agent_context("feat-123", spec_content, config)

        assert result["feature_id"] == "feat-123"
        assert result["spec_content"] == spec_content
        assert len(result["acceptance_criteria"]) == 2
        assert "tests/**/*.py" in result["test_patterns"]
        assert "MISSING_BEHAVIOR" in result["valid_failure_codes"]
        assert "Write failing tests" in result["instructions"]
        assert "DO NOT write implementation code" in result["instructions"]


class TestSpawnTestAgent:
    """Test agent invocation mechanism."""

    def test_spawn_test_agent_creates_context_file(self, tmp_path, capsys):
        """Creates context file for agent invocation in temp directory."""
        spec_content = "# Feature: User Login"
        config = {
            "test_framework": {
                "file_patterns": ["tests/**/*.py"]
            }
        }

        result = spawn_test_agent("feat-123", spec_content, config, project_root=tmp_path)

        # Check context file was created (capture output to get path)
        captured = capsys.readouterr()
        assert "Agent Invocation Required" in captured.out
        assert "feat-123" in captured.out

        # Extract context file path from output
        import re
        context_match = re.search(r'Context file: (.+)', captured.out)
        assert context_match, "Context file path not found in output"
        context_file_path = Path(context_match.group(1))

        assert context_file_path.exists()
        content = context_file_path.read_text()
        assert "feat-123" in content
        assert "Write failing tests" in content
        assert result == 0  # Success

        # Cleanup
        context_file_path.unlink()

    def test_spawn_test_agent_prints_instructions(self, tmp_path, capsys):
        """Prints instructions for manual agent invocation."""
        spec_content = "# Feature: User Login"
        config = {"test_framework": {"file_patterns": []}}

        spawn_test_agent("feat-123", spec_content, config, project_root=tmp_path)

        captured = capsys.readouterr()
        assert "Agent Invocation Required" in captured.out
        assert "@test-specialist" in captured.out
        assert "feat-123" in captured.out


class TestGenerateTestDesignArtifact:
    """Test artifact generation from template."""

    def test_generate_artifact_basic(self, tmp_path):
        """Generates test design artifact from template."""
        # Create minimal template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "test-design-template.md"
        template_file.write_text("""# Test Design: {{feature_name}}

**Feature ID:** {{feature_id}}
**Created:** {{timestamp}}
""")

        output_path = tmp_path / "docs" / "tests" / "feat-123-test-design.md"

        result = generate_test_design_artifact(
            feature_id="feat-123",
            feature_name="User Login",
            output_path=output_path,
            template_dir=template_dir
        )

        assert result == output_path
        assert output_path.exists()

        content = output_path.read_text()
        assert "# Test Design: User Login" in content
        assert "**Feature ID:** feat-123" in content

    def test_generate_artifact_falls_back_to_builtin(self, tmp_path):
        """Falls back to built-in template when custom not found."""
        output_path = tmp_path / "docs" / "tests" / "feat-123-test-design.md"

        # Should use built-in template (from spec-kit-multi-agent-tdd/templates/)
        result = generate_test_design_artifact(
            feature_id="feat-123",
            feature_name="User Login",
            output_path=output_path,
            template_dir=None  # Force fallback
        )

        assert result == output_path
        assert output_path.exists()


class TestExecuteTestCommand:
    """Test end-to-end command execution."""

    def test_execute_test_command_success(self, tmp_path):
        """Executes complete test command flow successfully."""
        # Setup: Create spec file
        spec_path = tmp_path / "docs" / "features" / "feat-123.md"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text("""# Feature: User Login

## Acceptance Criteria
- AC-1: User can login with valid credentials
- AC-2: Invalid credentials are rejected
""")

        # Setup: Create config
        config_path = tmp_path / ".specify" / "harness-tdd-config.yml"
        config_path.parent.mkdir(parents=True)
        config_data = {
            "artifacts": {
                "test_design": {
                    "path": "docs/tests/{feature_id}-test-design.md"
                }
            }
        }
        config_path.write_text(yaml.dump(config_data))

        # Execute command
        result = execute_test_command("feat-123", project_root=tmp_path)

        # Verify: artifact created
        artifact_path = tmp_path / "docs" / "tests" / "feat-123-test-design.md"
        assert artifact_path.exists()

        # Note: Context file is now created in system temp directory via tempfile.mkstemp()
        # We cannot predict the exact path, but it exists until manually cleaned up
        # This is acceptable for MVP (Phase 2) behavior

        assert result["status"] == "success"
        assert result["artifact_path"] == str(artifact_path)

    def test_execute_test_command_spec_not_found(self, tmp_path):
        """Fails gracefully when spec not found."""
        with pytest.raises(FileNotFoundError) as exc_info:
            execute_test_command("feat-999", project_root=tmp_path)

        assert "feat-999" in str(exc_info.value)

    def test_execute_test_command_uses_custom_template(self, tmp_path):
        """Uses custom template when available."""
        # Setup spec
        spec_path = tmp_path / "docs" / "features" / "feat-123.md"
        spec_path.parent.mkdir(parents=True)
        spec_path.write_text("# Feature: Test")

        # Setup custom template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "test-design-template.md"
        template_file.write_text("CUSTOM: {{feature_id}}")

        # Execute
        result = execute_test_command("feat-123", project_root=tmp_path)

        # Verify custom template was used
        artifact_path = Path(result["artifact_path"])
        content = artifact_path.read_text()
        assert "CUSTOM: feat-123" in content
