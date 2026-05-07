#!/usr/bin/env python3
"""
Unit tests for implement command (S4-002).
Tests exit code behavior for validation vs escalation scenarios.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.implement import (
    load_config,
    find_test_design_artifact,
    find_spec_artifact,
    prepare_agent_context,
    create_implementation_notes,
    main,
)


class TestExitCodes:
    """Test exit code behavior for implement command."""

    def test_main_success_exit_0(self):
        """Successfully prepared implementation returns exit code 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)
            (project_root / ".specify").mkdir(parents=True)

            # Create test design artifact
            test_design_path = project_root / "docs" / "features" / "feat-123-test-design.md"
            test_design_path.write_text("# Test Design\nTests here")

            # Create templates directory
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            template_file = templates_dir / "implementation-notes-template.md"
            template_file.write_text("# {{ feature_name }}\nAgent: {{ agent_name }}")

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root)]):
                exit_code = main()

            assert exit_code == 0, f"Expected exit code 0, got {exit_code}"

    def test_main_validation_error_exit_1(self):
        """Test artifact not found returns exit code 1 (validation error)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # No test design artifact created
            with patch('sys.argv', ['implement', 'feat-missing', '--project-root', str(project_root)]):
                exit_code = main()

            assert exit_code == 1, f"Expected exit code 1 for missing artifact, got {exit_code}"

    def test_main_template_missing_exit_2(self):
        """Missing template file returns exit code 2 (escalation)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure with test design
            (project_root / "docs" / "features").mkdir(parents=True)
            test_design_path = project_root / "docs" / "features" / "feat-123-test-design.md"
            test_design_path.write_text("# Test Design")

            # Do NOT create template file
            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root)]):
                exit_code = main()

            assert exit_code == 2, f"Expected exit code 2 for missing template, got {exit_code}"

    def test_main_permission_error_exit_2(self):
        """Permission error writing artifact returns exit code 2 (escalation)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create test design artifact
            test_design_path = project_root / "docs" / "features" / "feat-123-test-design.md"
            test_design_path.write_text("# Test Design")

            # Create template
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            template_file = templates_dir / "implementation-notes-template.md"
            template_file.write_text("# {{ feature_name }}")

            # Mock write_text to raise PermissionError
            with patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")):
                with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root)]):
                    exit_code = main()

            assert exit_code == 2, f"Expected exit code 2 for permission error, got {exit_code}"


class TestCreateImplementationNotes:
    """Test implementation notes creation and exception handling."""

    def test_create_notes_success(self):
        """Successfully creates implementation notes artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create template
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            template_file = templates_dir / "implementation-notes-template.md"
            template_file.write_text("# {{ feature_name }}\nAgent: {{ agent_name }}")

            config = {
                'artifacts': {
                    'root': 'docs/features',
                    'types': {'impl_notes': 'impl-notes'}
                }
            }

            result = create_implementation_notes('feat-123', 'test-agent', config, project_root)

            assert result.exists()
            assert result.name == 'feat-123-impl-notes.md'
            content = result.read_text()
            assert 'Feat 123' in content  # feature_name rendered
            assert 'test-agent' in content  # agent_name rendered

    def test_create_notes_template_missing_raises_fnf(self):
        """Missing template raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Do NOT create template
            config = {
                'artifacts': {
                    'root': 'docs/features',
                    'types': {'impl_notes': 'impl-notes'}
                }
            }

            with pytest.raises(FileNotFoundError) as exc_info:
                create_implementation_notes('feat-123', 'test-agent', config, project_root)

            assert 'Template not found' in str(exc_info.value)

    def test_create_notes_permission_error_raises_perm(self):
        """Permission error writing artifact raises PermissionError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create template
            templates_dir = project_root.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            template_file = templates_dir / "implementation-notes-template.md"
            template_file.write_text("# {{ feature_name }}")

            config = {
                'artifacts': {
                    'root': 'docs/features',
                    'types': {'impl_notes': 'impl-notes'}
                }
            }

            # Mock write_text to raise PermissionError
            with patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")):
                with pytest.raises(PermissionError):
                    create_implementation_notes('feat-123', 'test-agent', config, project_root)


class TestFindTestDesignArtifact:
    """Test finding test design artifacts."""

    def test_find_existing_artifact(self):
        """Finds existing test design artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            test_design = project_root / "docs" / "features" / "feat-123-test-design.md"
            test_design.write_text("# Test Design")

            config = {'artifacts': {'root': 'docs/features'}}

            result = find_test_design_artifact('feat-123', config, project_root)
            assert result == test_design

    def test_missing_artifact_raises_fnf(self):
        """Missing test design raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            config = {'artifacts': {'root': 'docs/features'}}

            with pytest.raises(FileNotFoundError) as exc_info:
                find_test_design_artifact('feat-missing', config, project_root)

            assert 'Test design artifact not found' in str(exc_info.value)
            assert 'Run /speckit.multi-agent.test first' in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
