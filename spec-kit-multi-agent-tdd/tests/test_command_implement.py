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
    update_impl_notes_with_green_evidence,
    run_integration_checks,
    update_impl_notes_with_integration_results,
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

            # Mock validate_red_state to return RED state
            mock_validation = {
                'state': 'RED',
                'validation_passed': True,
                'message': 'RED state validated',
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 1,
                'output': 'test output',
                'evidence': MagicMock(total_tests=3, passed=0, failed=3, errors=0)
            }

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root)]), \
                 patch('lib.test_runner.validate_red_state', return_value=mock_validation):
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

            # Mock validate_red_state to return RED state
            mock_validation = {
                'state': 'RED',
                'validation_passed': True,
                'message': 'RED state validated',
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 1,
                'output': 'test output',
                'evidence': MagicMock(total_tests=3, passed=0, failed=3, errors=0)
            }

            # Mock Path.exists() to return False for template file
            original_exists = Path.exists
            def mock_exists(self):
                # Return False only for template files, True for others
                if 'implementation-notes-template.md' in str(self):
                    return False
                return original_exists(self)

            # Do NOT create template file and mock its existence check
            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root)]), \
                 patch('lib.test_runner.validate_red_state', return_value=mock_validation), \
                 patch('pathlib.Path.exists', mock_exists):
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

            # Mock validate_red_state to return RED state
            mock_validation = {
                'state': 'RED',
                'validation_passed': True,
                'message': 'RED state validated',
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 1,
                'output': 'test output',
                'evidence': MagicMock(total_tests=3, passed=0, failed=3, errors=0)
            }

            # Mock write_text to raise PermissionError
            with patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")), \
                 patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root)]), \
                 patch('lib.test_runner.validate_red_state', return_value=mock_validation):
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
        """Missing template raises EscalationError."""
        from commands.implement import EscalationError

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

            # Mock Path.exists() to return False for template file
            original_exists = Path.exists
            def mock_exists(self):
                if 'implementation-notes-template.md' in str(self):
                    return False
                return original_exists(self)

            with patch('pathlib.Path.exists', mock_exists), \
                 pytest.raises(EscalationError) as exc_info:
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


class TestGreenValidation:
    """Test GREEN state validation functionality."""

    def test_main_validate_green_success(self):
        """GREEN validation with passing tests returns exit code 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_notes_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_notes_content = """# Implementation Notes: Feat 123

**Status:** draft

## RED→GREEN Evidence

### RED State (Initial/Before Implementation)

**Test Results:**
- Total tests: 3
- Passed: 0
- Failed: 3
"""
            impl_notes_path.write_text(impl_notes_content)

            # Mock validate_green_state to return GREEN state
            mock_validation = {
                'state': 'GREEN',
                'validation_passed': True,
                'message': 'GREEN state validated (3 tests passing)',
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 0,
                'output': 'All tests passed',
                'evidence': MagicMock(total_tests=3, passed=3, failed=0, errors=0),
                'coverage': {'percentage': 85, 'statements': 120, 'missing': 18, 'found': True}
            }

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root), '--validate-green']), \
                 patch('lib.test_runner.validate_green_state', return_value=mock_validation):
                exit_code = main()

            assert exit_code == 0, f"Expected exit code 0 for GREEN validation, got {exit_code}"

            # Check that impl notes were updated
            updated_content = impl_notes_path.read_text()
            assert '**Status:** complete' in updated_content
            assert 'GREEN State (After Implementation)' in updated_content

    def test_main_validate_green_red_failure(self):
        """GREEN validation with failing tests returns exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_notes_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_notes_path.write_text("# Implementation Notes\n**Status:** draft")

            # Mock validate_green_state to return RED state
            mock_validation = {
                'state': 'RED',
                'validation_passed': False,
                'message': 'Tests not passing (3 failures)',
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 1,
                'output': 'Tests failed',
                'evidence': MagicMock(total_tests=3, passed=0, failed=3, errors=0)
            }

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root), '--validate-green']), \
                 patch('lib.test_runner.validate_green_state', return_value=mock_validation):
                exit_code = main()

            assert exit_code == 1, f"Expected exit code 1 for RED validation failure, got {exit_code}"

    def test_main_validate_green_broken_escalation(self):
        """GREEN validation with broken tests returns exit code 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_notes_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_notes_path.write_text("# Implementation Notes\n**Status:** draft")

            # Mock validate_green_state to return BROKEN state
            mock_validation = {
                'state': 'BROKEN',
                'validation_passed': False,
                'message': 'Tests broken (3 errors)',
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 2,
                'output': 'Tests broken',
                'evidence': MagicMock(total_tests=3, passed=0, failed=0, errors=3)
            }

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root), '--validate-green']), \
                 patch('lib.test_runner.validate_green_state', return_value=mock_validation):
                exit_code = main()

            assert exit_code == 2, f"Expected exit code 2 for BROKEN escalation, got {exit_code}"

    def test_main_validate_green_missing_impl_notes(self):
        """GREEN validation without impl notes returns exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "features").mkdir(parents=True)

            # No impl notes created
            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root), '--validate-green']):
                exit_code = main()

            assert exit_code == 1, f"Expected exit code 1 for missing impl notes, got {exit_code}"


class TestUpdateImplNotesWithGreenEvidence:
    """Test updating impl notes with GREEN evidence."""

    def test_update_impl_notes_success(self):
        """Successfully updates impl notes with GREEN evidence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "impl-notes.md"
            original_content = """# Implementation Notes: Feat 123

**Status:** draft

## RED→GREEN Evidence

### RED State (Initial/Before Implementation)

**Test Results:**
- Total tests: 3
- Failed: 3

### GREEN State (After Implementation)

(To be filled after implementation)
"""
            artifact_path.write_text(original_content)

            validation_result = {
                'state': 'GREEN',
                'timestamp': '2024-01-01T00:00:00Z',
                'output': 'All tests passed',
                'evidence': MagicMock(total_tests=3, passed=3, failed=0, errors=0),
                'coverage': {'percentage': 85, 'statements': 120, 'missing': 18, 'found': True}
            }

            update_impl_notes_with_green_evidence(artifact_path, validation_result)

            updated_content = artifact_path.read_text()

            # Check status updated
            assert '**Status:** complete' in updated_content

            # Check GREEN section added
            assert '### GREEN State (After Implementation)' in updated_content
            assert 'Total: 3' in updated_content
            assert 'Passed: 3' in updated_content
            assert '**GREEN Validation:** YES' in updated_content

            # Check coverage added
            assert 'Coverage Metrics' in updated_content
            assert 'Percentage: 85%' in updated_content

    def test_update_impl_notes_no_coverage(self):
        """Updates impl notes without coverage metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "impl-notes.md"
            original_content = """# Implementation Notes

**Status:** draft

## RED→GREEN Evidence

### RED State (Initial/Before Implementation)

Test output here
"""
            artifact_path.write_text(original_content)

            validation_result = {
                'state': 'GREEN',
                'timestamp': '2024-01-01T00:00:00Z',
                'output': 'All tests passed',
                'evidence': MagicMock(total_tests=3, passed=3, failed=0, errors=0),
                'coverage': None
            }

            update_impl_notes_with_green_evidence(artifact_path, validation_result)

            updated_content = artifact_path.read_text()

            # Check GREEN section added without coverage
            assert '### GREEN State (After Implementation)' in updated_content
            assert 'Coverage Metrics' not in updated_content


class TestIntegrationChecks:
    """Test integration validation functionality."""

    def test_run_integration_checks_disabled(self):
        """Integration checks disabled returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {
                'integration_checks': {
                    'enabled': False
                }
            }

            results = run_integration_checks(project_root, config, 'feat-123')

            assert results == []

    def test_run_integration_checks_no_config(self):
        """No integration checks config returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {}

            results = run_integration_checks(project_root, config, 'feat-123')

            assert results == []

    def test_run_integration_checks_passing(self):
        """Integration checks passing returns success results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'echo', 'command': 'echo test', 'critical': False}
                    ]
                }
            }

            results = run_integration_checks(project_root, config, 'feat-123')

            assert len(results) == 1
            assert results[0]['name'] == 'echo'
            assert results[0]['passed'] is True
            assert results[0]['exit_code'] == 0
            assert 'test' in results[0]['output']
            assert results[0]['critical'] is False

    def test_run_integration_checks_failing_non_critical(self):
        """Integration checks failing non-critical returns warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'false', 'command': 'false', 'critical': False}
                    ]
                }
            }

            results = run_integration_checks(project_root, config, 'feat-123')

            assert len(results) == 1
            assert results[0]['name'] == 'false'
            assert results[0]['passed'] is False
            assert results[0]['exit_code'] == 1
            assert results[0]['critical'] is False

    def test_run_integration_checks_failing_critical(self):
        """Integration checks failing critical returns critical failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'false', 'command': 'false', 'critical': True}
                    ]
                }
            }

            results = run_integration_checks(project_root, config, 'feat-123')

            assert len(results) == 1
            assert results[0]['name'] == 'false'
            assert results[0]['passed'] is False
            assert results[0]['critical'] is True

    def test_run_integration_checks_timeout(self):
        """Integration checks timing out returns timeout result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'sleep', 'command': 'sleep 120', 'critical': False}
                    ]
                }
            }

            results = run_integration_checks(project_root, config, 'feat-123')

            assert len(results) == 1
            assert results[0]['name'] == 'sleep'
            assert results[0]['passed'] is False
            assert results[0]['exit_code'] == -1
            assert 'Timeout' in results[0]['output']

    def test_run_integration_checks_multiple(self):
        """Multiple integration checks run independently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'echo1', 'command': 'echo pass', 'critical': False},
                        {'name': 'false', 'command': 'false', 'critical': False},
                        {'name': 'echo2', 'command': 'echo pass2', 'critical': False}
                    ]
                }
            }

            results = run_integration_checks(project_root, config, 'feat-123')

            assert len(results) == 3
            assert results[0]['passed'] is True
            assert results[1]['passed'] is False
            assert results[2]['passed'] is True

    def test_update_impl_notes_with_integration_results(self):
        """Update impl notes with integration check results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "feat-123-impl-notes.md"
            original_content = """# Implementation Notes

## RED→GREEN Evidence

### RED State

Content here

## Notes

Some notes
"""
            artifact_path.write_text(original_content)

            integration_results = [
                {
                    'name': 'ruff',
                    'command': 'ruff check src/',
                    'passed': True,
                    'exit_code': 0,
                    'output': 'All checks passed',
                    'critical': False
                },
                {
                    'name': 'mypy',
                    'command': 'mypy src/',
                    'passed': False,
                    'exit_code': 1,
                    'output': 'Error: type mismatch',
                    'critical': False
                }
            ]

            update_impl_notes_with_integration_results(artifact_path, integration_results)

            updated_content = artifact_path.read_text()

            # Check integration section added
            assert '## Integration Validation Results' in updated_content
            assert '**Summary:** 1/2 checks passed' in updated_content
            assert 'ruff' in updated_content
            assert '✓ PASS' in updated_content
            assert 'mypy' in updated_content
            assert '⚠ FAIL (warning)' in updated_content
            assert 'Failed Checks:' in updated_content
            assert 'Error: type mismatch' in updated_content

    def test_green_validation_with_integration_checks(self):
        """GREEN validation runs integration checks after test validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_notes_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_notes_content = """# Implementation Notes: Feat 123

**Status:** draft

## RED→GREEN Evidence

### RED State (Initial/Before Implementation)

**Test Results:**
- Total tests: 3

## Notes

Some notes
"""
            impl_notes_path.write_text(impl_notes_content)

            # Mock validate_green_state to return GREEN state
            mock_validation = {
                'state': 'GREEN',
                'evidence': MagicMock(total_tests=3, passed=3, failed=0, errors=0),
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 0,
                'output': 'All tests passed',
                'validation_passed': True,
                'message': 'GREEN state validated',
                'coverage': None
            }

            # Config with integration checks
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'echo', 'command': 'echo pass', 'critical': False}
                    ]
                },
                'artifacts': {
                    'root': 'docs/features',
                    'types': {'impl_notes': 'impl-notes'}
                }
            }

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root), '--validate-green']), \
                 patch('commands.implement.load_config', return_value=config), \
                 patch('lib.test_runner.validate_green_state', return_value=mock_validation):
                exit_code = main()

            assert exit_code == 0

            # Check integration results added to impl notes
            updated_content = impl_notes_path.read_text()
            assert '## Integration Validation Results' in updated_content
            assert 'echo' in updated_content

    def test_green_validation_with_critical_integration_failure(self):
        """GREEN validation with critical integration check failure returns exit code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Setup directory structure
            (project_root / "docs" / "features").mkdir(parents=True)

            # Create impl notes artifact
            impl_notes_path = project_root / "docs" / "features" / "feat-123-impl-notes.md"
            impl_notes_content = """# Implementation Notes: Feat 123

**Status:** draft

## RED→GREEN Evidence

### RED State

Content
"""
            impl_notes_path.write_text(impl_notes_content)

            # Mock validate_green_state to return GREEN state
            mock_validation = {
                'state': 'GREEN',
                'evidence': MagicMock(total_tests=3, passed=3, failed=0, errors=0),
                'timestamp': '2024-01-01T00:00:00Z',
                'exit_code': 0,
                'output': 'All tests passed',
                'validation_passed': True,
                'message': 'GREEN state validated',
                'coverage': None
            }

            # Config with critical integration check
            config = {
                'integration_checks': {
                    'enabled': True,
                    'commands': [
                        {'name': 'false', 'command': 'false', 'critical': True}
                    ]
                },
                'artifacts': {
                    'root': 'docs/features',
                    'types': {'impl_notes': 'impl-notes'}
                }
            }

            with patch('sys.argv', ['implement', 'feat-123', '--project-root', str(project_root), '--validate-green']), \
                 patch('commands.implement.load_config', return_value=config), \
                 patch('lib.test_runner.validate_green_state', return_value=mock_validation):
                exit_code = main()

            assert exit_code == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
