#!/usr/bin/env python3
"""Tests for artifact template generator."""

import tempfile
from pathlib import Path
from datetime import datetime
import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from generate_artifact import (
    render_template,
    validate_output_path,
    get_available_templates,
    parse_custom_variables,
)


class TestRenderTemplate:
    """Test template rendering functionality."""

    def test_render_template_basic(self, tmp_path):
        """Renders template with required variables."""
        # Create a simple test template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text(
            "# Test Design: {{feature_name}}\n"
            "**Feature ID:** {{feature_id}}\n"
            "**Created:** {{timestamp}}\n"
        )

        # Render with required variables
        variables = {
            "feature_name": "User Login",
            "feature_id": "feat-123",
            "timestamp": "2024-01-15T10:30:00Z",
        }
        result = render_template("test-design", variables, template_dir)

        assert "# Test Design: User Login" in result
        assert "**Feature ID:** feat-123" in result
        assert "**Created:** 2024-01-15T10:30:00Z" in result

    def test_render_template_with_optional_vars(self, tmp_path):
        """Includes optional agent name."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text(
            "# Test Design: {{feature_name}}\n"
            "**Agent:** {{agent_name}}\n"
            "**Status:** {{status}}\n"
        )

        variables = {
            "feature_name": "User Login",
            "agent_name": "test-specialist",
            "status": "in-progress",
        }
        result = render_template("test-design", variables, template_dir)

        assert "**Agent:** test-specialist" in result
        assert "**Status:** in-progress" in result

    def test_render_template_missing_variable(self, tmp_path):
        """Fails with clear error when variable is missing."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text(
            "# Test Design: {{feature_name}}\n"
            "**Feature ID:** {{feature_id}}\n"
        )

        variables = {
            "feature_name": "User Login",
            # feature_id is missing
        }

        with pytest.raises(Exception) as exc_info:
            render_template("test-design", variables, template_dir)

        assert "feature_id" in str(exc_info.value).lower() or "undefined" in str(exc_info.value).lower()

    def test_render_template_nonexistent(self, tmp_path):
        """Fails when template doesn't exist."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        variables = {
            "feature_name": "User Login",
            "feature_id": "feat-123",
        }

        with pytest.raises(Exception) as exc_info:
            render_template("nonexistent-template", variables, template_dir)

        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()


class TestValidateOutputPath:
    """Test output path validation."""

    def test_validate_output_path_creates_directory(self, tmp_path):
        """Creates directories as needed."""
        output_dir = tmp_path / "artifacts" / "test"
        output_path = output_dir / "test-design.md"

        validated_path = validate_output_path(output_path)

        assert output_dir.exists()
        assert validated_path == output_path

    def test_validate_output_path_existing_directory(self, tmp_path):
        """Works with existing directory."""
        output_dir = tmp_path / "artifacts"
        output_dir.mkdir(parents=True)
        output_path = output_dir / "test-design.md"

        validated_path = validate_output_path(output_path)

        assert validated_path == output_path

    def test_validate_output_path_with_config_valid(self, tmp_path):
        """Accepts path within configured artifacts directory."""
        artifacts_dir = tmp_path / "artifacts"
        config = {"artifacts_dir": str(artifacts_dir)}
        output_path = artifacts_dir / "test" / "test-design.md"

        validated_path = validate_output_path(output_path, config)

        assert validated_path.is_absolute()
        assert output_path.parent.exists()

    def test_validate_output_path_with_config_invalid(self, tmp_path):
        """Rejects path outside configured artifacts directory."""
        artifacts_dir = tmp_path / "artifacts"
        config = {"artifacts_dir": str(artifacts_dir)}
        outside_path = tmp_path / "other" / "test-design.md"

        with pytest.raises(ValueError) as exc_info:
            validate_output_path(outside_path, config)

        assert "outside configured" in str(exc_info.value).lower()

    def test_validate_output_path_no_config(self, tmp_path):
        """Works without config (no validation constraint)."""
        output_path = tmp_path / "anywhere" / "test-design.md"

        validated_path = validate_output_path(output_path)

        assert validated_path.is_absolute()
        assert output_path.parent.exists()


class TestGetAvailableTemplates:
    """Test template discovery."""

    def test_list_available_templates(self, tmp_path):
        """Lists all available template files."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # Create test templates
        (template_dir / "test-design.md").write_text("# Test")
        (template_dir / "implementation-notes.md").write_text("# Impl")
        (template_dir / "arch-review.md").write_text("# Arch")
        (template_dir / "README.md").write_text("# Docs")  # Should be excluded

        templates = get_available_templates(template_dir)

        assert "test-design" in templates
        assert "implementation-notes" in templates
        assert "arch-review" in templates
        # README files and non-template patterns should be excluded
        assert "README" not in templates


class TestParseCustomVariables:
    """Test custom variable parsing."""

    def test_parse_custom_variables_single(self):
        """Parses single custom variable."""
        result = parse_custom_variables(["author=John Doe"])
        assert result == {"author": "John Doe"}

    def test_parse_custom_variables_multiple(self):
        """Parses multiple custom variables."""
        result = parse_custom_variables([
            "author=John Doe",
            "version=2.0",
            "status=draft"
        ])
        assert result == {
            "author": "John Doe",
            "version": "2.0",
            "status": "draft"
        }

    def test_parse_custom_variables_with_equals(self):
        """Handles values containing equals signs."""
        result = parse_custom_variables(["url=https://example.com?a=b"])
        assert result == {"url": "https://example.com?a=b"}

    def test_parse_custom_variables_invalid_format(self):
        """Raises error for invalid format."""
        with pytest.raises(ValueError) as exc_info:
            parse_custom_variables(["invalid"])
        assert "key=value" in str(exc_info.value).lower()


class TestCLIIntegration:
    """End-to-end CLI tests."""

    def test_cli_basic_usage(self, tmp_path, monkeypatch):
        """End-to-end with minimal args."""
        # Set up test environment
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text(
            "# Test Design: {{feature_name}}\n"
            "**Feature ID:** {{feature_id}}\n"
            "**Created:** {{timestamp}}\n"
        )

        output_dir = tmp_path / "artifacts"
        output_path = output_dir / "feat-123-test-design.md"

        # Simulate CLI execution
        from generate_artifact import main

        monkeypatch.setattr(sys, "argv", [
            "generate_artifact.py",
            "test-design",
            "feat-123",
            "User Login",
            "--output", str(output_path),
            "--template-dir", str(template_dir),
        ])

        exit_code = main()

        assert exit_code == 0
        assert output_path.exists()
        content = output_path.read_text()
        assert "User Login" in content
        assert "feat-123" in content

    def test_cli_with_all_options(self, tmp_path, monkeypatch):
        """End-to-end with all flags."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text(
            "# Test Design: {{feature_name}}\n"
            "**Feature ID:** {{feature_id}}\n"
            "**Agent:** {{agent_name}}\n"
            "**Status:** {{status}}\n"
            "**Version:** {{version}}\n"
        )

        output_dir = tmp_path / "artifacts"
        output_path = output_dir / "feat-123-test-design.md"

        from generate_artifact import main

        monkeypatch.setattr(sys, "argv", [
            "generate_artifact.py",
            "test-design",
            "feat-123",
            "User Login",
            "--output", str(output_path),
            "--agent", "test-specialist",
            "--template-dir", str(template_dir),
            "--var", "status=draft",
            "--var", "version=2.0",
        ])

        exit_code = main()

        assert exit_code == 0
        assert output_path.exists()
        content = output_path.read_text()
        assert "test-specialist" in content
        assert "status: draft" in content or "Status:** draft" in content
        assert "version: 2.0" in content or "Version:** 2.0" in content

    def test_cli_file_exists_no_force(self, tmp_path, monkeypatch, capsys):
        """Prompts when file exists without --force."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text("# Test: {{feature_name}}")

        output_dir = tmp_path / "artifacts"
        output_dir.mkdir()
        output_path = output_dir / "test-design.md"
        output_path.write_text("# Existing content")

        from generate_artifact import main

        # Simulate user saying "no" to overwrite
        monkeypatch.setattr("builtins.input", lambda _: "n")
        monkeypatch.setattr(sys, "argv", [
            "generate_artifact.py",
            "test-design",
            "feat-123",
            "User Login",
            "--output", str(output_path),
            "--template-dir", str(template_dir),
        ])

        exit_code = main()

        assert exit_code == 1
        # Original content should remain
        assert output_path.read_text() == "# Existing content"

    def test_cli_file_exists_with_force(self, tmp_path, monkeypatch):
        """Overwrites existing file with --force."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design.md"
        test_template.write_text("# Test: {{feature_name}}")

        output_dir = tmp_path / "artifacts"
        output_dir.mkdir()
        output_path = output_dir / "test-design.md"
        output_path.write_text("# Existing content")

        from generate_artifact import main

        monkeypatch.setattr(sys, "argv", [
            "generate_artifact.py",
            "test-design",
            "feat-123",
            "User Login",
            "--output", str(output_path),
            "--template-dir", str(template_dir),
            "--force",
        ])

        exit_code = main()

        assert exit_code == 0
        content = output_path.read_text()
        assert "User Login" in content
        assert "Existing content" not in content

    def test_list_available_templates_cli(self, tmp_path, monkeypatch, capsys):
        """Shows available templates with --list."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test-design.md").write_text("# Test")
        (template_dir / "arch-review.md").write_text("# Arch")

        from generate_artifact import main

        monkeypatch.setattr(sys, "argv", [
            "generate_artifact.py",
            "--list",
            "--template-dir", str(template_dir),
        ])

        exit_code = main()
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "test-design" in captured.out
        assert "arch-review" in captured.out

    def test_cli_minimal_args(self, tmp_path, monkeypatch):
        """Run with ONLY required args (feat-id, feat-name) - tests default filters in templates."""
        # Create template with optional variables that have defaults
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        test_template = template_dir / "test-design-template.md"
        test_template.write_text(
            "# Test Design: {{feature_name}}\n"
            "**Feature ID:** {{feature_id}}\n"
            "**Status:** {{status|default('draft')}}\n"
            "**Agent:** {{agent_name}}\n"
            "**Created:** {{timestamp}}\n"
        )

        output_dir = tmp_path / "artifacts"
        output_path = output_dir / "feat-999-test-design-template.md"

        from generate_artifact import main

        # Only provide template, feature_id, feature_name (no --var flags)
        monkeypatch.setattr(sys, "argv", [
            "generate_artifact.py",
            "test-design-template",
            "feat-999",
            "Test Feature",
            "--agent", "test-specialist",
            "--output", str(output_path),
            "--template-dir", str(template_dir),
        ])

        exit_code = main()

        assert exit_code == 0
        assert output_path.exists()
        content = output_path.read_text()
        assert "Test Feature" in content
        assert "feat-999" in content
        # Status should default to 'draft' via Jinja filter
        assert "Status:** draft" in content
        assert "test-specialist" in content


class TestRealTemplates:
    """Integration tests with actual project templates."""

    def test_generate_all_template_types(self, tmp_path):
        """Generates all 5 template types successfully."""
        # Get actual template directory
        project_root = Path(__file__).parent.parent
        template_dir = project_root / "templates"

        if not template_dir.exists():
            pytest.skip("Project templates not found")

        output_dir = tmp_path / "artifacts"

        templates = [
            "test-design-template",
            "implementation-notes-template",
            "arch-review-template",
            "code-review-template",
            "workflow-summary-template",
        ]

        variables = {
            "feature_name": "Test Feature",
            "feature_id": "feat-test-001",
            "timestamp": datetime.now().isoformat() + "Z",
            "agent_name": "test-agent",
            "status": "draft",
            "version": "1.0",
            "cycle_number": "1",
            "max_cycles": "3",
            # Variables for workflow-summary template
            "completion_timestamp": datetime.now().isoformat() + "Z",
            "duration_minutes": "45",
            "branch_name": "feat/test-feature",
            "commit_hash": "abc123",
            "commit_message": "Test commit",
            "pr_url": "https://github.com/test/pr/1",
            "test_count": "10",
            "test_file_count": "3",
            "coverage_percentage": "85",
            "files_created_count": "2",
            "files_modified_count": "5",
            "files_deleted_count": "0",
            "arch_review_cycles": "1",
            "arch_concerns_count": "0",
            "arch_blockers_count": "0",
            "code_review_cycles": "1",
            "code_concerns_count": "2",
            "code_blockers_count": "0",
            "review_efficiency_score": "8.5",
            "coordination_score": "9.0",
        }

        for template_name in templates:
            result = render_template(template_name, variables, template_dir)

            # Verify basic structure
            assert len(result) > 0
            assert "Test Feature" in result
            assert "feat-test-001" in result

            # Save to file to verify path handling
            output_path = output_dir / f"{template_name}.md"
            validate_output_path(output_path)
            output_path.write_text(result)

            assert output_path.exists()
