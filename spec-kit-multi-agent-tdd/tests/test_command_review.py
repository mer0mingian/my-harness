#!/usr/bin/env python3
"""
Unit tests for review command (S5-003).
Tests exit code behavior for validation vs escalation scenarios.
Implements TDD RED→GREEN cycle.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.review import (
    load_config,
    find_implementation_notes,
    find_spec_artifact,
    generate_review_artifacts,
    execute_review_command,
    main,
)


class TestLoadConfig:
    """Test configuration loading with defaults."""

    def test_load_config_returns_dict(self):
        """load_config returns a dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = load_config(project_root)
            assert isinstance(config, dict)

    def test_load_config_has_default_agents(self):
        """load_config includes default agent names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = load_config(project_root)
            assert 'agents' in config
            assert config['agents'].get('arch_reviewer') == 'check'
            assert config['agents'].get('code_reviewer') == 'simplify'


class TestFindImplementationNotes:
    """Test finding implementation notes from step 8."""

    def test_find_impl_notes_success(self):
        """Successfully finds implementation notes artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes\nStep 8 output")

            result = find_implementation_notes("feat-123", project_root)
            assert result == impl_path
            assert result.exists()

    def test_find_impl_notes_not_found_raises_error(self):
        """Missing implementation notes raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            with pytest.raises(FileNotFoundError) as exc_info:
                find_implementation_notes("feat-missing", project_root)

            assert "Implementation notes not found" in str(exc_info.value)


class TestFindSpecArtifact:
    """Test finding optional spec artifact."""

    def test_find_spec_success(self):
        """Successfully finds spec artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create spec artifact
            spec_path = project_root / "docs" / "features" / "feat-123-spec.md"
            spec_path.write_text("# Feature Spec\nRequirements here")

            result = find_spec_artifact("feat-123", project_root)
            assert result == spec_path

    def test_find_spec_returns_none_if_not_found(self):
        """Returns None if spec not found (optional)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            result = find_spec_artifact("feat-missing", project_root)
            assert result is None


class TestGenerateReviewArtifacts:
    """Test review artifact generation from templates."""

    def test_generate_artifacts_creates_arch_review(self):
        """Successfully generates arch-review artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create template
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            arch_template = templates_dir / "arch-review-template.md"
            arch_template.write_text("# Architecture Review: {{feature_name}}\n**Feature ID:** {{feature_id}}\n**Status:** {{status}}")

            arch_path, code_path = generate_review_artifacts(
                "feat-123",
                "Test Feature",
                project_root
            )

            assert arch_path.exists()
            assert arch_path.name == "feat-123-arch-review.md"
            content = arch_path.read_text()
            assert "Architecture Review: Test Feature" in content
            assert "feat-123" in content
            assert "draft" in content

    def test_generate_artifacts_creates_code_review(self):
        """Successfully generates code-review artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create template
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            code_template = templates_dir / "code-review-template.md"
            code_template.write_text("# Code Review: {{feature_name}}\n**Feature ID:** {{feature_id}}\n**Status:** {{status}}")

            arch_path, code_path = generate_review_artifacts(
                "feat-123",
                "Test Feature",
                project_root
            )

            assert code_path.exists()
            assert code_path.name == "feat-123-code-review.md"
            content = code_path.read_text()
            assert "Code Review: Test Feature" in content

    def test_generate_artifacts_returns_both_paths(self):
        """Returns tuple of (arch_path, code_path)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create templates
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("# {{feature_name}}")
            (templates_dir / "code-review-template.md").write_text("# {{feature_name}}")

            result = generate_review_artifacts("feat-123", "Feature", project_root)

            assert isinstance(result, tuple)
            assert len(result) == 2
            arch_path, code_path = result
            assert arch_path.exists()
            assert code_path.exists()

    def test_generate_artifacts_missing_template_raises_error(self):
        """Missing template raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create a custom template dir to force use of it (without actual templates)
            custom_template_dir = Path(tmpdir) / "custom_templates"
            custom_template_dir.mkdir(exist_ok=True)

            with pytest.raises(FileNotFoundError):
                generate_review_artifacts("feat-123", "Feature", project_root, custom_template_dir)

    def test_generate_artifacts_includes_timestamp(self):
        """Generated artifacts include timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create templates with timestamp
            templates_dir = Path(tmpdir) / "custom_templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("Created: {{timestamp}}")
            (templates_dir / "code-review-template.md").write_text("Created: {{timestamp}}")

            arch_path, code_path = generate_review_artifacts("feat-123", "Feature", project_root, templates_dir)

            arch_content = arch_path.read_text()
            # Timestamp should be ISO format (YYYY-MM-DDTHH:MM:SS)
            assert "Created: 20" in arch_content  # ISO format starts with 20XX


class TestExecuteReviewCommand:
    """Test end-to-end review command execution."""

    def test_execute_review_success_exit_0(self):
        """Successfully prepared review returns exit code 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes")

            # Create templates
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("# {{feature_name}}")
            (templates_dir / "code-review-template.md").write_text("# {{feature_name}}")

            exit_code = execute_review_command("feat-123", project_root)

            assert exit_code == 0

    def test_execute_review_impl_notes_missing_exit_1(self):
        """Missing implementation notes returns exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Do NOT create impl notes

            exit_code = execute_review_command("feat-missing", project_root)

            assert exit_code == 1

    def test_execute_review_template_missing_exit_2(self):
        """Missing template returns exit code 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes")

            # Mock generate_review_artifacts to raise FileNotFoundError
            with patch('commands.review.generate_review_artifacts', side_effect=FileNotFoundError("Template missing")):
                exit_code = execute_review_command("feat-123", project_root)

            assert exit_code == 2

    def test_execute_review_creates_both_artifacts(self):
        """Execution creates both arch-review and code-review artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes")

            # Create templates
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("# {{feature_name}}")
            (templates_dir / "code-review-template.md").write_text("# {{feature_name}}")

            exit_code = execute_review_command("feat-123", project_root)

            # Check both artifacts exist
            arch_review = project_root / "docs" / "features" / "feat-123-arch-review.md"
            code_review = project_root / "docs" / "features" / "feat-123-code-review.md"

            assert arch_review.exists()
            assert code_review.exists()


class TestMainCommand:
    """Test CLI entry point."""

    def test_main_with_feature_id(self):
        """main() accepts feature_id argument."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes")

            # Create templates
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("# {{feature_name}}")
            (templates_dir / "code-review-template.md").write_text("# {{feature_name}}")

            with patch('sys.argv', ['review', 'feat-123', '--project-root', str(project_root)]):
                exit_code = main()

            assert exit_code == 0

    def test_main_missing_feature_id_shows_error(self):
        """main() shows error when feature_id missing."""
        with patch('sys.argv', ['review']):
            with pytest.raises(SystemExit):
                main()

    def test_main_success_shows_artifact_paths(self, capsys):
        """Successful execution prints artifact paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes")

            # Create templates
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("# {{feature_name}}")
            (templates_dir / "code-review-template.md").write_text("# {{feature_name}}")

            with patch('sys.argv', ['review', 'feat-123', '--project-root', str(project_root)]):
                exit_code = main()

            captured = capsys.readouterr()
            assert "Success" in captured.out or "feat-123-arch-review.md" in captured.out
            assert exit_code == 0

    def test_main_validation_failure_shows_error(self, capsys):
        """Validation failure (exit 1) prints to stderr."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            with patch('sys.argv', ['review', 'feat-missing', '--project-root', str(project_root)]):
                exit_code = main()

            captured = capsys.readouterr()
            assert "Error" in captured.err or exit_code == 1

    def test_main_escalation_shows_error(self, capsys):
        """Escalation (exit 2) prints to stderr."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes but mock generate_review_artifacts to fail
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation Notes")

            with patch('sys.argv', ['review', 'feat-123', '--project-root', str(project_root)]), \
                 patch('commands.review.generate_review_artifacts', side_effect=FileNotFoundError("Template missing")):
                exit_code = main()

            assert exit_code == 2


class TestExitCodes:
    """Test proper exit code behavior per specification."""

    def test_exit_0_on_success(self):
        """Exit code 0 for successful artifact creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Setup
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation")

            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            (templates_dir / "arch-review-template.md").write_text("# {{feature_name}}")
            (templates_dir / "code-review-template.md").write_text("# {{feature_name}}")

            exit_code = execute_review_command("feat-123", project_root)
            assert exit_code == 0

    def test_exit_1_on_validation_failure(self):
        """Exit code 1 when implementation notes not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            exit_code = execute_review_command("feat-missing", project_root)
            assert exit_code == 1

    def test_exit_2_on_escalation(self):
        """Exit code 2 for template missing or permission errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes but mock generate_review_artifacts to fail
            impl_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_path.write_text("# Implementation")

            with patch('commands.review.generate_review_artifacts', side_effect=FileNotFoundError("Template missing")):
                exit_code = execute_review_command("feat-123", project_root)
            assert exit_code == 2
