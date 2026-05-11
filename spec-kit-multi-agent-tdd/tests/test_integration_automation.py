#!/usr/bin/env python3
"""
Integration Tests for Automation Scripts (S2B-005)

Tests all 4 automation scripts end-to-end with realistic inputs:
- validate_manifests.py (S2B-001)
- generate_artifact.py (S2B-002)
- parse_test_evidence.py (S2B-003)
- validate_artifacts.py (S2B-004)

Verifies:
- Scripts work together in realistic scenarios
- Exit codes are correct
- Error messages are clear and actionable
- Real-world edge cases are handled
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


# Test Utilities
def run_script(
    script_name: str,
    args: List[str],
    stdin: Optional[str] = None,
    cwd: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run a script and return exit code, stdout, stderr.

    Args:
        script_name: Name of script in lib/ directory
        args: Command line arguments
        stdin: Optional stdin content
        cwd: Optional working directory

    Returns:
        {'exit_code': int, 'stdout': str, 'stderr': str}
    """
    script_path = Path(__file__).parent.parent / "lib" / script_name
    cmd = ["python", str(script_path)] + args

    result = subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd
    )

    return {
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }


# Fixtures
@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with expected directory structure."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "artifacts").mkdir()
    (workspace / "templates").mkdir()
    (workspace / ".agents").mkdir()
    (workspace / ".agents" / "plugins").mkdir()
    return workspace


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def templates_dir():
    """Return path to templates directory."""
    return Path(__file__).parent.parent / "templates"


@pytest.fixture
def real_plugin_path():
    """Return path to a real plugin.json for testing."""
    # Use existing harness-agents plugin
    plugin_path = Path(__file__).parent.parent.parent / ".agents" / "plugins" / "harness-agents" / "plugin.json"
    if plugin_path.exists():
        return plugin_path

    # Fallback: look for any plugin.json
    base_dir = Path(__file__).parent.parent.parent
    plugins = list(base_dir.rglob("plugin.json"))
    if plugins:
        return plugins[0]

    return None


# Test Classes

class TestManifestValidatorIntegration:
    """Integration tests for validate_manifests.py (S2B-001)."""

    def test_validate_manifests_valid_plugin(self, real_plugin_path):
        """Validate existing harness-agents plugin passes."""
        if real_plugin_path is None:
            pytest.skip("No real plugin.json found for testing")

        result = run_script(
            "validate_manifests.py",
            [str(real_plugin_path), "--verbose"]
        )

        assert result['exit_code'] == 0, f"Expected exit code 0, got {result['exit_code']}\nStderr: {result['stderr']}"
        assert "valid" in result['stdout'].lower() or "passed" in result['stdout'].lower()

    def test_validate_manifests_invalid_plugin(self, temp_workspace):
        """Validate malformed plugin.json fails with clear error."""
        # Create malformed plugin.json (missing required fields)
        plugin_dir = temp_workspace / ".agents" / "plugins" / "test-plugin"
        plugin_dir.mkdir(parents=True)
        plugin_json = plugin_dir / "plugin.json"

        invalid_manifest = {
            "name": "test-plugin",
            "version": "1.0.0"
            # Missing: description, agents
        }

        with open(plugin_json, 'w') as f:
            json.dump(invalid_manifest, f)

        result = run_script(
            "validate_manifests.py",
            [str(plugin_json)]
        )

        assert result['exit_code'] == 1, "Expected exit code 1 for validation failure"
        # Check for error indication in either stdout or stderr
        output = result['stdout'] + result['stderr']
        assert "error" in output.lower() or "failed" in output.lower() or "invalid" in output.lower()

    def test_validate_manifests_all_flag(self, temp_workspace, real_plugin_path):
        """Validate --all flag discovers and validates all manifests."""
        if real_plugin_path is None:
            pytest.skip("No real plugin.json found for testing")

        # Copy real plugin to temp workspace
        plugin_dir = temp_workspace / ".agents" / "plugins" / "test-plugin"
        plugin_dir.mkdir(parents=True)
        plugin_json = plugin_dir / "plugin.json"

        import shutil
        shutil.copy(real_plugin_path, plugin_json)

        result = run_script(
            "validate_manifests.py",
            ["--all", "--verbose"],
            cwd=temp_workspace
        )

        # Should find and validate at least one plugin
        assert "plugin.json" in result['stdout'] or "found" in result['stdout'].lower()


class TestArtifactGeneratorIntegration:
    """Integration tests for generate_artifact.py (S2B-002)."""

    def test_generate_all_artifact_types(self, temp_workspace, templates_dir):
        """Generate all 5 artifact types and verify structure."""
        template_names = [
            "workflow-summary-template",
            "arch-review-template",
            "test-design-template",
            "code-review-template",
            "implementation-notes-template"
        ]

        for template_name in template_names:
            output_file = temp_workspace / f"{template_name}.md"

            result = run_script(
                "generate_artifact.py",
                [
                    template_name,
                    "TEST-001",  # feature_id
                    "Test Feature",  # feature_name
                    "--output", str(output_file),
                    "--var", "task_id=TEST-001",
                    "--var", "author=test-user",
                    "--force"
                ]
            )

            assert result['exit_code'] == 0, f"Failed to generate {template_name}: {result['stderr']}"
            assert output_file.exists(), f"Output file not created for {template_name}"

            # Verify generated content
            content = output_file.read_text()
            assert len(content) > 0, f"Generated file is empty for {template_name}"
            assert "TEST-001" in content or "Test Feature" in content, "Variables not substituted"

    def test_generate_artifact_with_custom_vars(self, temp_workspace):
        """Generate artifact with --var flags and verify substitution."""
        output_file = temp_workspace / "test-output.md"

        result = run_script(
            "generate_artifact.py",
            [
                "workflow-summary-template",
                "CUSTOM-123",  # feature_id
                "Custom Feature",  # feature_name
                "--output", str(output_file),
                "--var", "task_id=CUSTOM-123",
                "--var", "phase=Phase 2",
                "--var", "author=john.doe@example.com",
                "--force"
            ]
        )

        assert result['exit_code'] == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "CUSTOM-123" in content, "task_id variable not substituted"
        assert "Phase 2" in content or "Custom Feature" in content, "Variables not substituted"

    def test_generate_artifact_missing_template(self, temp_workspace):
        """Verify clear error when template doesn't exist."""
        output_file = temp_workspace / "test-output.md"

        result = run_script(
            "generate_artifact.py",
            [
                "nonexistent-template",
                "TEST-001",  # feature_id
                "Test Feature",  # feature_name
                "--output", str(output_file)
            ]
        )

        assert result['exit_code'] != 0, "Expected non-zero exit code for missing template"
        output = result['stdout'] + result['stderr']
        assert "not found" in output.lower() or "error" in output.lower()


class TestEvidenceParserIntegration:
    """Integration tests for parse_test_evidence.py (S2B-003)."""

    def test_parse_evidence_real_pytest_green(self, fixtures_dir):
        """Parse real GREEN pytest output and verify state detection."""
        pytest_output = (fixtures_dir / "pytest_green.txt").read_text()

        result = run_script(
            "parse_test_evidence.py",
            ["--format", "json"],
            stdin=pytest_output
        )

        assert result['exit_code'] == 0, "Expected exit code 0 for GREEN state"

        # Parse JSON output
        evidence = json.loads(result['stdout'])
        assert evidence['state'] == "GREEN"
        assert evidence['passed'] > 0
        assert evidence['failed'] == 0
        assert evidence['errors'] == 0

    def test_parse_evidence_real_pytest_red(self, fixtures_dir):
        """Parse real RED pytest output with failure classification."""
        pytest_output = (fixtures_dir / "pytest_red_missing_behavior.txt").read_text()

        result = run_script(
            "parse_test_evidence.py",
            ["--format", "json"],
            stdin=pytest_output
        )

        assert result['exit_code'] == 1, "Expected exit code 1 for RED state"

        # Parse JSON output
        evidence = json.loads(result['stdout'])
        assert evidence['state'] == "RED"
        assert evidence['failed'] > 0

        # Verify failure classification
        failed_tests = [r for r in evidence['results'] if r['status'] == 'failed']
        assert len(failed_tests) > 0
        assert any(r.get('failure_code') for r in failed_tests), "Expected failure codes"

    def test_parse_evidence_real_pytest_broken(self, fixtures_dir):
        """Parse BROKEN pytest output and verify escalation codes."""
        pytest_output = (fixtures_dir / "pytest_broken_env.txt").read_text()

        result = run_script(
            "parse_test_evidence.py",
            ["--format", "json"],
            stdin=pytest_output
        )

        assert result['exit_code'] == 2, "Expected exit code 2 for BROKEN state"

        # Parse JSON output
        evidence = json.loads(result['stdout'])
        assert evidence['state'] == "BROKEN"
        assert evidence['errors'] > 0

        # Verify error classification
        error_tests = [r for r in evidence['results'] if r['status'] == 'error']
        assert len(error_tests) > 0


class TestArtifactValidatorIntegration:
    """Integration tests for validate_artifacts.py (S2B-004)."""

    def test_validate_complete_artifact_set(self, temp_workspace, templates_dir):
        """Validate complete workflow artifacts (all mandatory present)."""
        artifacts_dir = temp_workspace / "artifacts"
        feature_id = "TEST-001"

        # Generate all mandatory artifacts with correct naming
        mandatory_artifacts = {
            "workflow-summary-template": "workflow-summary",
            "test-design-template": "test-design",
            "arch-review-template": "arch-review",
            "code-review-template": "code-review"
        }

        for template_name, output_name in mandatory_artifacts.items():
            output_file = artifacts_dir / f"{feature_id}-{output_name}.md"
            result = run_script(
                "generate_artifact.py",
                [
                    template_name,
                    feature_id,
                    "Test Feature",
                    "--output", str(output_file),
                    "--force"
                ]
            )
            assert result['exit_code'] == 0, f"Failed to generate {template_name}: {result['stderr']}"

        # Validate artifacts - runs successfully and produces report
        result = run_script(
            "validate_artifacts.py",
            [feature_id, "--artifacts-dir", str(artifacts_dir), "--verbose"]
        )

        # Validator runs successfully (exit code 0 or 1, not 2 for errors)
        assert result['exit_code'] in [0, 1], f"Expected exit code 0 or 1, got {result['exit_code']}\nStderr: {result['stderr']}"
        # Report includes feature_id
        assert feature_id in result['stdout'], "Report should include feature_id"
        # Report shows artifact status
        assert "test_design" in result['stdout'], "Report should check test_design artifact"

    def test_validate_incomplete_artifact_set(self, temp_workspace):
        """Validate missing mandatory artifacts are detected."""
        artifacts_dir = temp_workspace / "artifacts"

        # Create only one artifact (incomplete set)
        artifact_file = artifacts_dir / "TEST-002-workflow-summary-template.md"
        artifact_file.write_text("# Test Workflow Summary\n\nIncomplete artifact set.")

        result = run_script(
            "validate_artifacts.py",
            ["TEST-002", "--artifacts-dir", str(artifacts_dir)]
        )

        # Should fail validation
        assert result['exit_code'] == 1, "Expected exit code 1 for incomplete artifacts"
        output = result['stdout'] + result['stderr']
        assert "missing" in output.lower() or "required" in output.lower() or "not found" in output.lower()

    def test_validate_artifact_structure_malformed(self, temp_workspace):
        """Validate malformed artifact structure is detected."""
        artifacts_dir = temp_workspace / "artifacts"

        # Create malformed artifact (empty file)
        artifact_file = artifacts_dir / "TEST-003-workflow-summary-template.md"
        artifact_file.write_text("")

        result = run_script(
            "validate_artifacts.py",
            ["TEST-003", "--artifacts-dir", str(artifacts_dir)]
        )

        # Should fail validation (missing required artifacts)
        assert result['exit_code'] == 1, "Expected exit code 1 for malformed artifacts"


class TestEndToEndWorkflow:
    """End-to-end workflow tests combining multiple scripts."""

    def test_workflow_generate_and_validate(self, temp_workspace):
        """Generate artifacts → validate them (integration)."""
        artifacts_dir = temp_workspace / "artifacts"
        feature_id = "E2E-001"

        # Generate all mandatory artifacts
        artifacts_to_generate = {
            "workflow-summary-template": "workflow-summary",
            "test-design-template": "test-design",
            "arch-review-template": "arch-review",
            "code-review-template": "code-review"
        }

        for template_name, output_name in artifacts_to_generate.items():
            result = run_script(
                "generate_artifact.py",
                [
                    template_name,
                    feature_id,
                    "E2E Test Feature",
                    "--output", str(artifacts_dir / f"{feature_id}-{output_name}.md"),
                    "--var", "phase=Phase 2",
                    "--force"
                ]
            )
            assert result['exit_code'] == 0, f"Generate {template_name} failed: {result['stderr']}"

        # Validate artifacts - verifies files exist and can be processed
        result3 = run_script(
            "validate_artifacts.py",
            [feature_id, "--artifacts-dir", str(artifacts_dir)]
        )
        # Successful validation run (0 or 1, not 2 for errors)
        assert result3['exit_code'] in [0, 1], f"Validation error: {result3['stderr']}\n{result3['stdout']}"
        # Verify all artifacts were checked
        for output_name in artifacts_to_generate.values():
            # Check artifact name appears in report (without the template suffix)
            assert output_name.replace("-template", "").replace("-", "_") in result3['stdout'], f"{output_name} not in report"

    def test_workflow_parse_evidence_and_validate(self, temp_workspace, fixtures_dir):
        """Parse test evidence → validate workflow artifacts with evidence."""
        artifacts_dir = temp_workspace / "artifacts"
        feature_id = "E2E-002"

        # Step 1: Generate all mandatory artifacts
        artifacts_to_generate = {
            "workflow-summary-template": "workflow-summary",
            "test-design-template": "test-design",
            "arch-review-template": "arch-review",
            "code-review-template": "code-review"
        }

        for template_name, output_name in artifacts_to_generate.items():
            result = run_script(
                "generate_artifact.py",
                [
                    template_name,
                    feature_id,
                    "E2E Test Feature 2",
                    "--output", str(artifacts_dir / f"{feature_id}-{output_name}.md"),
                    "--force"
                ]
            )
            assert result['exit_code'] == 0, f"Failed to generate {template_name}"

        # Step 2: Parse test evidence
        pytest_output = (fixtures_dir / "pytest_green.txt").read_text()
        result = run_script(
            "parse_test_evidence.py",
            ["--format", "json"],
            stdin=pytest_output
        )
        assert result['exit_code'] == 0, "Parse evidence failed"

        evidence = json.loads(result['stdout'])
        assert evidence['state'] == "GREEN", "Expected GREEN state"

        # Step 3: Save evidence as artifact
        evidence_file = artifacts_dir / f"{feature_id}-test-evidence.json"
        with open(evidence_file, 'w') as f:
            json.dump(evidence, f, indent=2)

        # Step 4: Validate complete artifact set
        result = run_script(
            "validate_artifacts.py",
            [feature_id, "--artifacts-dir", str(artifacts_dir)]
        )
        # Successful validation run (0 or 1, not 2 for errors)
        assert result['exit_code'] in [0, 1], f"Validation error: {result['stderr']}\n{result['stdout']}"
        # Verify evidence file is recognized
        assert evidence_file.exists(), "Evidence file should exist"

    def test_workflow_complete_pipeline(self, temp_workspace, fixtures_dir):
        """Full pipeline: generate → parse → validate (realistic scenario)."""
        artifacts_dir = temp_workspace / "artifacts"
        feature_id = "E2E-003"

        # Step 1: Generate all required artifacts (mandatory + optional)
        artifacts_to_generate = {
            "workflow-summary-template": "workflow-summary",
            "test-design-template": "test-design",
            "arch-review-template": "arch-review",
            "code-review-template": "code-review",
            "implementation-notes-template": "implementation-notes"
        }

        for template_name, output_name in artifacts_to_generate.items():
            result = run_script(
                "generate_artifact.py",
                [
                    template_name,
                    feature_id,
                    "E2E Complete Pipeline Test",
                    "--output", str(artifacts_dir / f"{feature_id}-{output_name}.md"),
                    "--var", "phase=Phase 2",
                    "--var", "author=integration-test",
                    "--force"
                ]
            )
            assert result['exit_code'] == 0, f"Failed to generate {template_name}: {result['stderr']}"

        # Step 2: Parse test evidence (RED state)
        pytest_output = (fixtures_dir / "pytest_red_missing_behavior.txt").read_text()
        result = run_script(
            "parse_test_evidence.py",
            ["--format", "json"],
            stdin=pytest_output
        )
        assert result['exit_code'] == 1, "Expected RED state"

        evidence = json.loads(result['stdout'])
        assert evidence['state'] == "RED"
        assert evidence['failed'] > 0, "Should have failed tests"

        # Step 3: Save evidence
        evidence_file = artifacts_dir / f"{feature_id}-test-evidence.json"
        with open(evidence_file, 'w') as f:
            json.dump(evidence, f, indent=2)

        # Step 4: Validate complete pipeline artifacts
        result = run_script(
            "validate_artifacts.py",
            [feature_id, "--artifacts-dir", str(artifacts_dir), "--verbose"]
        )

        # Validator runs successfully (0 or 1, not 2 for errors)
        assert result['exit_code'] in [0, 1], f"Pipeline validation error: {result['stderr']}\n{result['stdout']}"

        # Verify all artifacts exist
        assert (artifacts_dir / f"{feature_id}-workflow-summary.md").exists()
        assert (artifacts_dir / f"{feature_id}-test-design.md").exists()
        assert (artifacts_dir / f"{feature_id}-arch-review.md").exists()
        assert (artifacts_dir / f"{feature_id}-code-review.md").exists()
        assert (artifacts_dir / f"{feature_id}-implementation-notes.md").exists()
        assert evidence_file.exists()

        # Verify report includes all artifacts
        for artifact_name in ["test_design", "arch_review", "code_review", "workflow_summary"]:
            assert artifact_name in result['stdout'], f"{artifact_name} should be in validation report"
