#!/usr/bin/env python3
"""Unit tests for validate_feature_artifacts.py script.

Tests the standalone CLI wrapper for artifact validation.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def temp_artifacts_dir(tmp_path):
    """Create temporary artifacts directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return artifacts


@pytest.fixture
def sample_complete_artifacts(temp_artifacts_dir):
    """Create a complete set of valid artifacts."""
    # Test design
    test_design = """# Test Design: Sample Feature

**Feature ID:** feat-123
**Agent:** @test
**Status:** draft
**Created:** 2024-01-15T10:00:00Z

## Test Strategy

Testing approach documented here.

## Acceptance Criteria Mapping

Criteria mapping table.

## RED State Validation

RED state confirmed.

## Escalations

No blockers.

## Decision

**Route:** implement
"""
    (temp_artifacts_dir / "feat-123-test-design.md").write_text(test_design)

    # Implementation notes (optional)
    impl_notes = """# Implementation Notes: Sample Feature

**Feature ID:** feat-123
**Agent:** @implement
**Status:** completed

## Implementation Approach

Code written using TDD.
"""
    (temp_artifacts_dir / "feat-123-implementation-notes.md").write_text(impl_notes)

    # Architecture review
    arch_review = """# Architecture Review: Sample Feature

**Feature ID:** feat-123
**Reviewer:** @arch

## Architecture Impacts

Design is sound.

## Safety Constraints

No constraints violated.

## Verdict

**Verdict:** APPROVED
"""
    (temp_artifacts_dir / "feat-123-arch-review.md").write_text(arch_review)

    # Code review
    code_review = """# Code Review: Sample Feature

**Feature ID:** feat-123
**Reviewer:** @review

## Code Quality

Code is clean.

## Test Coverage

Tests are comprehensive.

## Verdict

**Verdict:** APPROVED
"""
    (temp_artifacts_dir / "feat-123-code-review.md").write_text(code_review)

    # Workflow summary with timestamps
    workflow_summary = """# Workflow Summary: Sample Feature

**Feature ID:** feat-123
**Status:** completed

## Feature Information

Workflow completed successfully.

## Test Evidence

**Test Evidence:**
- RED State Timestamp: 2024-01-15T10:30:00Z
- GREEN State Timestamp: 2024-01-15T11:45:00Z
- RED State: MISSING_BEHAVIOR confirmed
- GREEN State: All tests passing

## Implementation Evidence

Implementation completed.

## Review Evidence

Reviews approved.

## Commit Information

**Commit Hash:** abc123
"""
    (temp_artifacts_dir / "feat-123-workflow-summary.md").write_text(workflow_summary)

    return temp_artifacts_dir


def run_script(feature_id, project_root=None, extra_args=None):
    """Helper to run the validation script."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "validate_feature_artifacts.py"
    cmd = [sys.executable, str(script_path), feature_id]

    if project_root:
        cmd.extend(["--project-root", str(project_root)])

    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return result


class TestValidateFeatureArtifactsScript:
    """Test suite for validate_feature_artifacts.py script."""

    def test_script_exists(self):
        """Test that the script file exists and is executable."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "validate_feature_artifacts.py"
        assert script_path.exists(), f"Script not found: {script_path}"
        # Check shebang
        with open(script_path) as f:
            first_line = f.readline()
            assert first_line.startswith("#!"), "Script should have shebang line"

    def test_all_artifacts_valid_exit_0(self, sample_complete_artifacts):
        """Test exit code 0 when all artifacts are valid."""
        result = run_script("feat-123", project_root=sample_complete_artifacts.parent)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"

    def test_missing_artifacts_exit_1(self, temp_artifacts_dir):
        """Test exit code 1 when artifacts are missing."""
        result = run_script("feat-123", project_root=temp_artifacts_dir.parent)
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"

    def test_json_output_valid_artifacts(self, sample_complete_artifacts):
        """Test JSON output format with valid artifacts."""
        result = run_script(
            "feat-123",
            project_root=sample_complete_artifacts.parent,
            extra_args=["--format", "json"]
        )

        # Should be valid JSON
        data = json.loads(result.stdout)

        assert data["valid"] is True
        assert data["feature_id"] == "feat-123"
        assert "artifacts" in data
        assert "test_design" in data["artifacts"]
        assert "arch_review" in data["artifacts"]
        assert "code_review" in data["artifacts"]
        assert "workflow_summary" in data["artifacts"]
        assert "impl_notes" in data["artifacts"]

        # Check artifact details
        assert data["artifacts"]["test_design"]["exists"] is True
        assert data["artifacts"]["test_design"]["valid"] is True
        assert data["artifacts"]["test_design"]["issues"] == []

    def test_json_output_missing_artifacts(self, temp_artifacts_dir):
        """Test JSON output with missing artifacts."""
        result = run_script(
            "feat-123",
            project_root=temp_artifacts_dir.parent,
            extra_args=["--format", "json"]
        )

        data = json.loads(result.stdout)

        assert data["valid"] is False
        assert data["feature_id"] == "feat-123"
        assert any(not art["exists"] for art in data["artifacts"].values())

    def test_timestamp_validation(self, temp_artifacts_dir):
        """Test timestamp ordering validation."""
        # Create artifacts with invalid timestamp order (GREEN before RED)
        (temp_artifacts_dir / "feat-123-test-design.md").write_text("""
# Test Design: Test

## Test Strategy
Test

## Acceptance Criteria Mapping
Map

## RED State Validation
RED

## Escalations
None

## Decision
Implement
""")

        (temp_artifacts_dir / "feat-123-arch-review.md").write_text("""
# Architecture Review: Test

## Architecture Impacts
Good

## Safety Constraints
Safe

## Verdict
APPROVED
""")

        (temp_artifacts_dir / "feat-123-code-review.md").write_text("""
# Code Review: Test

## Code Quality
Good

## Test Coverage
Good

## Verdict
APPROVED
""")

        (temp_artifacts_dir / "feat-123-workflow-summary.md").write_text("""
# Workflow Summary: Test

## Feature Information
Info

## Test Evidence
- RED State Timestamp: 2024-01-15T12:00:00Z
- GREEN State Timestamp: 2024-01-15T10:00:00Z

## Implementation Evidence
Done

## Review Evidence
Done

## Commit Information
Done
""")

        result = run_script(
            "feat-123",
            project_root=temp_artifacts_dir.parent,
            extra_args=["--format", "json"]
        )

        data = json.loads(result.stdout)
        assert data["valid"] is False
        assert data["timestamp_order_valid"] is False

    def test_invalid_structure(self, temp_artifacts_dir):
        """Test validation of artifact structure."""
        # Create artifacts with missing required sections
        (temp_artifacts_dir / "feat-123-test-design.md").write_text("""
# Test Design: Incomplete
Only has title, missing required sections.
""")

        (temp_artifacts_dir / "feat-123-arch-review.md").write_text("""
# Architecture Review: Incomplete
Missing sections.
""")

        (temp_artifacts_dir / "feat-123-code-review.md").write_text("""
# Code Review: Incomplete
Missing sections.
""")

        (temp_artifacts_dir / "feat-123-workflow-summary.md").write_text("""
# Workflow Summary: Incomplete
Missing sections.
""")

        result = run_script(
            "feat-123",
            project_root=temp_artifacts_dir.parent,
            extra_args=["--format", "json"]
        )

        data = json.loads(result.stdout)
        assert data["valid"] is False

        # At least some artifacts should have validation issues
        has_issues = any(
            art["exists"] and (not art["valid"] or art["issues"])
            for art in data["artifacts"].values()
        )
        assert has_issues

    def test_help_output(self):
        """Test --help flag."""
        result = run_script("--help")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "validate" in result.stdout.lower()

    def test_feature_id_required(self):
        """Test that feature_id argument is required."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "validate_feature_artifacts.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "feature" in result.stderr.lower()

    def test_error_handling_invalid_path(self):
        """Test error handling for invalid project root."""
        result = run_script(
            "feat-123",
            project_root="/nonexistent/path/that/does/not/exist",
            extra_args=["--format", "json"]
        )

        # Should handle gracefully - either exit 1 (validation failure) or 2 (system error)
        assert result.returncode in [1, 2]

    def test_verbose_output(self, sample_complete_artifacts):
        """Test verbose output includes details."""
        result = run_script(
            "feat-123",
            project_root=sample_complete_artifacts.parent,
            extra_args=["--verbose"]
        )

        # Verbose should show artifact details
        assert "test-design" in result.stdout.lower() or "test_design" in result.stdout.lower()
        assert "arch-review" in result.stdout.lower() or "arch_review" in result.stdout.lower()

    def test_impl_notes_optional(self, temp_artifacts_dir):
        """Test that implementation notes are optional (not required for validation to pass)."""
        # Create mandatory artifacts only (no impl_notes)
        (temp_artifacts_dir / "feat-123-test-design.md").write_text("""
# Test Design: Test

## Test Strategy
Test

## Acceptance Criteria Mapping
Map

## RED State Validation
RED

## Escalations
None

## Decision
Implement
""")

        (temp_artifacts_dir / "feat-123-arch-review.md").write_text("""
# Architecture Review: Test

## Architecture Impacts
Good

## Safety Constraints
Safe

## Verdict
APPROVED
""")

        (temp_artifacts_dir / "feat-123-code-review.md").write_text("""
# Code Review: Test

## Code Quality
Good

## Test Coverage
Good

## Verdict
APPROVED
""")

        (temp_artifacts_dir / "feat-123-workflow-summary.md").write_text("""
# Workflow Summary: Test

## Feature Information
Info

## Test Evidence
- RED State Timestamp: 2024-01-15T10:00:00Z
- GREEN State Timestamp: 2024-01-15T11:00:00Z
- RED State: MISSING_BEHAVIOR
- GREEN State: All tests passing

## Implementation Evidence
Done

## Review Evidence
Done

## Commit Information
Done
""")

        result = run_script(
            "feat-123",
            project_root=temp_artifacts_dir.parent,
            extra_args=["--format", "json"]
        )

        data = json.loads(result.stdout)
        # Should be valid even without impl_notes
        assert data["valid"] is True
        assert data["artifacts"]["impl_notes"]["exists"] is False
