#!/usr/bin/env python3
"""Tests for /speckit.multi-agent.commit command implementation (S6-002)."""

import tempfile
from pathlib import Path
from datetime import datetime
import pytest
import sys
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.commit import (
    load_config,
    find_artifact,
    generate_workflow_summary,
    execute_commit_command,
)


class TestLoadConfig:
    """Test config file loading and defaults."""

    def test_load_config_from_file(self, tmp_path):
        """Loads config from .specify/harness-tdd-config.yml."""
        config_path = tmp_path / ".specify" / "harness-tdd-config.yml"
        config_path.parent.mkdir(parents=True)
        config_data = {
            "version": "1.0",
            "artifacts": {
                "root": "docs/features",
                "types": {
                    "test_design": "test-design",
                    "impl_notes": "impl-notes",
                    "arch_review": "arch-review",
                    "code_review": "code-review",
                    "workflow_summary": "workflow-summary",
                }
            }
        }
        config_path.write_text(yaml.dump(config_data))

        result = load_config(project_root=tmp_path)
        assert result["version"] == "1.0"
        assert result["artifacts"]["root"] == "docs/features"

    def test_load_config_uses_defaults_when_missing(self, tmp_path):
        """Uses built-in defaults when config file not found."""
        result = load_config(project_root=tmp_path)

        # Should return default config
        assert "artifacts" in result
        assert result["artifacts"]["root"] == "docs/features"
        assert "test_design" in result["artifacts"]["types"]


class TestFindArtifact:
    """Test artifact discovery."""

    def test_find_test_design_artifact(self, tmp_path):
        """Finds test design artifact."""
        artifact_path = tmp_path / "docs" / "features" / "feat-123-test-design.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("# Test Design\nTests for feature.")

        result = find_artifact(
            "feat-123", "test_design", load_config(tmp_path), tmp_path
        )
        assert result == artifact_path

    def test_find_impl_notes_artifact(self, tmp_path):
        """Finds implementation notes artifact."""
        artifact_path = tmp_path / "docs" / "features" / "feat-123-impl-notes.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("# Implementation Notes\nImpl details.")

        result = find_artifact(
            "feat-123", "impl_notes", load_config(tmp_path), tmp_path
        )
        assert result == artifact_path

    def test_find_arch_review_artifact(self, tmp_path):
        """Finds architecture review artifact."""
        artifact_path = tmp_path / "docs" / "features" / "feat-123-arch-review.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("# Architecture Review\nArch feedback.")

        result = find_artifact(
            "feat-123", "arch_review", load_config(tmp_path), tmp_path
        )
        assert result == artifact_path

    def test_find_code_review_artifact(self, tmp_path):
        """Finds code review artifact."""
        artifact_path = tmp_path / "docs" / "features" / "feat-123-code-review.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("# Code Review\nCode feedback.")

        result = find_artifact(
            "feat-123", "code_review", load_config(tmp_path), tmp_path
        )
        assert result == artifact_path

    def test_find_artifact_returns_none_when_missing(self, tmp_path):
        """Returns None when artifact not found."""
        result = find_artifact(
            "feat-999", "test_design", load_config(tmp_path), tmp_path
        )
        assert result is None


class TestGenerateWorkflowSummary:
    """Test workflow summary generation."""

    def test_generate_workflow_summary_success(self, tmp_path):
        """Creates workflow summary artifact with all artifact paths."""
        # Create required artifacts
        config = load_config(tmp_path)
        artifact_paths = {
            "test_design": tmp_path / "docs" / "features" / "feat-123-test-design.md",
            "impl_notes": tmp_path / "docs" / "features" / "feat-123-impl-notes.md",
            "arch_review": tmp_path / "docs" / "features" / "feat-123-arch-review.md",
            "code_review": tmp_path / "docs" / "features" / "feat-123-code-review.md",
        }
        for path in artifact_paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# Artifact\nContent")

        output_path = tmp_path / "docs" / "features" / "feat-123-workflow-summary.md"

        result = generate_workflow_summary(
            feature_id="feat-123",
            feature_name="Test Feature",
            artifact_paths=artifact_paths,
            output_path=output_path,
            template_dir=None,
        )

        assert result == output_path
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "feat-123" in content
        assert "Test Feature" in content
        assert "draft" in content

    def test_generate_workflow_summary_with_custom_template(self, tmp_path):
        """Uses custom template when provided."""
        # Create custom template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text(
            "# Custom: {{feature_name}}\nFeature: {{feature_id}}\nStatus: {{status}}"
        )

        artifact_paths = {
            "test_design": tmp_path / "docs" / "features" / "feat-123-test-design.md",
            "impl_notes": tmp_path / "docs" / "features" / "feat-123-impl-notes.md",
            "arch_review": tmp_path / "docs" / "features" / "feat-123-arch-review.md",
            "code_review": tmp_path / "docs" / "features" / "feat-123-code-review.md",
        }
        for path in artifact_paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# Artifact")

        output_path = tmp_path / "docs" / "features" / "feat-123-workflow-summary.md"

        result = generate_workflow_summary(
            feature_id="feat-123",
            feature_name="Custom Test",
            artifact_paths=artifact_paths,
            output_path=output_path,
            template_dir=template_dir,
        )

        assert result == output_path
        content = output_path.read_text()
        assert "Custom: Custom Test" in content
        assert "Feature: feat-123" in content

    def test_generate_workflow_summary_missing_template_escalates(self, tmp_path):
        """Raises FileNotFoundError when explicit template_dir doesn't exist."""
        artifact_paths = {
            "test_design": tmp_path / "docs" / "features" / "feat-123-test-design.md",
            "impl_notes": tmp_path / "docs" / "features" / "feat-123-impl-notes.md",
            "arch_review": tmp_path / "docs" / "features" / "feat-123-arch-review.md",
            "code_review": tmp_path / "docs" / "features" / "feat-123-code-review.md",
        }
        for path in artifact_paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# Artifact")

        output_path = tmp_path / "docs" / "features" / "feat-123-workflow-summary.md"

        # Use nonexistent template directory (explicitly provided)
        nonexistent_dir = tmp_path / ".specify" / "nonexistent"

        with pytest.raises(FileNotFoundError):
            generate_workflow_summary(
                feature_id="feat-123",
                feature_name="Test Feature",
                artifact_paths=artifact_paths,
                output_path=output_path,
                template_dir=nonexistent_dir,  # Explicitly provided but doesn't exist
            )


class TestExecuteCommitCommand:
    """Test end-to-end commit command execution."""

    def test_execute_commit_success_all_artifacts_present(self, tmp_path):
        """Returns exit code 0 when all required artifacts exist."""
        # Create all required artifacts
        config = load_config(tmp_path)
        required_artifacts = {
            "test_design": "feat-123-test-design.md",
            "impl_notes": "feat-123-impl-notes.md",
            "arch_review": "feat-123-arch-review.md",
            "code_review": "feat-123-code-review.md",
        }

        artifacts_dir = tmp_path / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        for artifact_name in required_artifacts.values():
            (artifacts_dir / artifact_name).write_text("# Artifact\nContent")

        # Create template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text(
            "# Workflow: {{feature_name}}\n"
            "Feature: {{feature_id}}\n"
            "Status: {{status}}\n"
            "Timestamp: {{timestamp}}\n"
        )

        exit_code = execute_commit_command(
            feature_id="feat-123",
            project_root=tmp_path,
        )

        assert exit_code == 0

        # Verify workflow summary created
        workflow_summary = artifacts_dir / "feat-123-workflow-summary.md"
        assert workflow_summary.exists()

    def test_execute_commit_fails_missing_test_design(self, tmp_path):
        """Returns exit code 1 when test design missing."""
        # Create only some artifacts (missing test design)
        artifacts_dir = tmp_path / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        (artifacts_dir / "feat-123-impl-notes.md").write_text("# Impl Notes")
        (artifacts_dir / "feat-123-arch-review.md").write_text("# Arch Review")
        (artifacts_dir / "feat-123-code-review.md").write_text("# Code Review")

        # Create template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text("# Workflow: {{feature_name}}")

        exit_code = execute_commit_command(
            feature_id="feat-123",
            project_root=tmp_path,
        )

        assert exit_code == 1

    def test_execute_commit_fails_missing_impl_notes(self, tmp_path):
        """Returns exit code 1 when implementation notes missing."""
        artifacts_dir = tmp_path / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        (artifacts_dir / "feat-123-test-design.md").write_text("# Test Design")
        (artifacts_dir / "feat-123-arch-review.md").write_text("# Arch Review")
        (artifacts_dir / "feat-123-code-review.md").write_text("# Code Review")

        # Create template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text("# Workflow: {{feature_name}}")

        exit_code = execute_commit_command(
            feature_id="feat-123",
            project_root=tmp_path,
        )

        assert exit_code == 1

    def test_execute_commit_fails_missing_arch_review(self, tmp_path):
        """Returns exit code 1 when architecture review missing."""
        artifacts_dir = tmp_path / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        (artifacts_dir / "feat-123-test-design.md").write_text("# Test Design")
        (artifacts_dir / "feat-123-impl-notes.md").write_text("# Impl Notes")
        (artifacts_dir / "feat-123-code-review.md").write_text("# Code Review")

        # Create template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text("# Workflow: {{feature_name}}")

        exit_code = execute_commit_command(
            feature_id="feat-123",
            project_root=tmp_path,
        )

        assert exit_code == 1

    def test_execute_commit_fails_missing_code_review(self, tmp_path):
        """Returns exit code 1 when code review missing."""
        artifacts_dir = tmp_path / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        (artifacts_dir / "feat-123-test-design.md").write_text("# Test Design")
        (artifacts_dir / "feat-123-impl-notes.md").write_text("# Impl Notes")
        (artifacts_dir / "feat-123-arch-review.md").write_text("# Arch Review")

        # Create template
        template_dir = tmp_path / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text("# Workflow: {{feature_name}}")

        exit_code = execute_commit_command(
            feature_id="feat-123",
            project_root=tmp_path,
        )

        assert exit_code == 1

    def test_execute_commit_falls_back_to_builtin_template(self, tmp_path):
        """Uses built-in template when no custom template provided."""
        # Create all required artifacts but no custom template
        artifacts_dir = tmp_path / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        (artifacts_dir / "feat-123-test-design.md").write_text("# Test Design")
        (artifacts_dir / "feat-123-impl-notes.md").write_text("# Impl Notes")
        (artifacts_dir / "feat-123-arch-review.md").write_text("# Arch Review")
        (artifacts_dir / "feat-123-code-review.md").write_text("# Code Review")

        # No .specify/templates directory created
        # Should still succeed by using built-in template

        exit_code = execute_commit_command(
            feature_id="feat-123",
            project_root=tmp_path,
        )

        assert exit_code == 0

        # Verify workflow summary was created
        workflow_summary = artifacts_dir / "feat-123-workflow-summary.md"
        assert workflow_summary.exists()

    def test_execute_commit_with_custom_project_root(self, tmp_path):
        """Respects custom project root parameter."""
        custom_root = tmp_path / "custom" / "project"
        artifacts_dir = custom_root / "docs" / "features"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        (artifacts_dir / "feat-456-test-design.md").write_text("# Test Design")
        (artifacts_dir / "feat-456-impl-notes.md").write_text("# Impl Notes")
        (artifacts_dir / "feat-456-arch-review.md").write_text("# Arch Review")
        (artifacts_dir / "feat-456-code-review.md").write_text("# Code Review")

        # Create template
        template_dir = custom_root / ".specify" / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "workflow-summary-template.md"
        template_file.write_text("# Workflow: {{feature_name}}")

        exit_code = execute_commit_command(
            feature_id="feat-456",
            project_root=custom_root,
        )

        assert exit_code == 0

        workflow_summary = artifacts_dir / "feat-456-workflow-summary.md"
        assert workflow_summary.exists()
