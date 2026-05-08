#!/usr/bin/env python3
"""Unit tests for validate_artifact_structure.py script.

Tests the post-generation artifact validation helper. Tests are written
first (TDD RED phase) before the implementation exists.

Exit Codes:
    0: All artifacts valid
    1: Warnings (issues found but non-blocking)
    2: Error (e.g. file not found, cannot read)
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the script module for testing (will fail until implementation exists)
import scripts.validate_artifact_structure as vas

# Get path to script (for CLI tests)
SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "validate_artifact_structure.py"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_test_design_artifact(tmp_path):
    """Create a valid test-design artifact file."""
    content = """---
type: test-design
feature: feat-001
version: "1.0"
---

## Acceptance Criteria

- The system shall do X
- The system shall do Y

## Test Cases

### TC-001: Happy path
Given X, When Y, Then Z
"""
    artifact = tmp_path / "test-design.md"
    artifact.write_text(content)
    return artifact


@pytest.fixture
def valid_adr_artifact(tmp_path):
    """Create a valid ADR artifact file with cross-reference."""
    prd_file = tmp_path / "prd.md"
    prd_file.write_text("---\ntype: prd\n---\n## What & Why\n\n## Business Value\n\n## Goals & No-goals\n")

    content = f"""---
type: adr
prd_ref: {prd_file}
feature: feat-001
---

## Context

We needed to choose a database.

## Decision

We chose PostgreSQL.
"""
    artifact = tmp_path / "adr.md"
    artifact.write_text(content)
    return artifact


@pytest.fixture
def artifact_missing_section(tmp_path):
    """Create a test-design artifact missing '## Test Cases'."""
    content = """---
type: test-design
feature: feat-001
---

## Acceptance Criteria

- The system shall do X
"""
    artifact = tmp_path / "missing-section.md"
    artifact.write_text(content)
    return artifact


@pytest.fixture
def artifact_invalid_yaml(tmp_path):
    """Create an artifact with invalid YAML frontmatter."""
    content = """---
type: test-design
feature: [unclosed bracket
invalid: : yaml: :
---

## Acceptance Criteria

## Test Cases
"""
    artifact = tmp_path / "invalid-yaml.md"
    artifact.write_text(content)
    return artifact


@pytest.fixture
def artifact_missing_cross_ref(tmp_path):
    """Create an ADR artifact referencing a non-existent PRD."""
    content = """---
type: adr
prd_ref: /nonexistent/path/to/prd.md
feature: feat-001
---

## Context

We needed to choose something.

## Decision

We chose something.
"""
    artifact = tmp_path / "adr-missing-ref.md"
    artifact.write_text(content)
    return artifact


@pytest.fixture
def artifact_too_large(tmp_path):
    """Create an artifact that exceeds 51200 bytes."""
    content = "---\ntype: test-design\n---\n## Acceptance Criteria\n\n## Test Cases\n\n"
    # Pad to exceed 51200 bytes
    content += "x" * 52000
    artifact = tmp_path / "too-large.md"
    artifact.write_text(content)
    return artifact


@pytest.fixture
def artifact_empty(tmp_path):
    """Create an artifact that is empty (< 10 bytes)."""
    artifact = tmp_path / "empty.md"
    artifact.write_text("")
    return artifact


@pytest.fixture
def artifact_unknown_type(tmp_path):
    """Create an artifact with a type not in the registry."""
    content = """---
type: custom-unknown-type
feature: feat-001
---

## Some Section

Content here.
"""
    artifact = tmp_path / "unknown-type.md"
    artifact.write_text(content)
    return artifact


# ---------------------------------------------------------------------------
# Tests: validate_single_artifact (core logic)
# ---------------------------------------------------------------------------

class TestValidSingleArtifact:
    """Test validate_single_artifact returns correct structure for valid artifact."""

    def test_valid_artifact_all_checks_pass(self, valid_test_design_artifact):
        """Valid artifact produces overall ok and no issues."""
        result = vas.validate_single_artifact(valid_test_design_artifact)

        assert result["path"] == str(valid_test_design_artifact)
        assert result["issues"] == []

        checks = result["checks"]
        assert checks["frontmatter_valid"] is True
        assert checks["required_sections"]["missing"] == []
        assert checks["file_size"]["ok"] is True

    def test_valid_artifact_sections_present_listed(self, valid_test_design_artifact):
        """Present sections are listed in required_sections.present."""
        result = vas.validate_single_artifact(valid_test_design_artifact)

        present = result["checks"]["required_sections"]["present"]
        assert "## Acceptance Criteria" in present
        assert "## Test Cases" in present

    def test_valid_artifact_file_size_bytes_reported(self, valid_test_design_artifact):
        """File size in bytes is reported accurately."""
        result = vas.validate_single_artifact(valid_test_design_artifact)

        expected_bytes = valid_test_design_artifact.stat().st_size
        assert result["checks"]["file_size"]["bytes"] == expected_bytes


class TestMissingRequiredSection:
    """Test detection of missing required sections."""

    def test_missing_section_listed_in_missing(self, artifact_missing_section):
        """Missing section appears in required_sections.missing."""
        result = vas.validate_single_artifact(artifact_missing_section)

        missing = result["checks"]["required_sections"]["missing"]
        assert "## Test Cases" in missing

    def test_present_section_not_in_missing(self, artifact_missing_section):
        """Present section is not in missing list."""
        result = vas.validate_single_artifact(artifact_missing_section)

        missing = result["checks"]["required_sections"]["missing"]
        assert "## Acceptance Criteria" not in missing

    def test_missing_section_produces_issue(self, artifact_missing_section):
        """A missing section produces an entry in issues."""
        result = vas.validate_single_artifact(artifact_missing_section)

        assert len(result["issues"]) > 0
        assert any("## Test Cases" in issue for issue in result["issues"])


class TestInvalidYAMLFrontmatter:
    """Test handling of invalid YAML frontmatter."""

    def test_invalid_yaml_sets_frontmatter_valid_false(self, artifact_invalid_yaml):
        """Invalid YAML frontmatter sets frontmatter_valid to False."""
        result = vas.validate_single_artifact(artifact_invalid_yaml)

        assert result["checks"]["frontmatter_valid"] is False

    def test_invalid_yaml_produces_issue(self, artifact_invalid_yaml):
        """Invalid YAML frontmatter produces an issue entry."""
        result = vas.validate_single_artifact(artifact_invalid_yaml)

        assert len(result["issues"]) > 0
        assert any("frontmatter" in issue.lower() or "yaml" in issue.lower()
                   for issue in result["issues"])


class TestCrossReferenceMissingFile:
    """Test cross-reference validation when referenced file is missing."""

    def test_missing_cross_ref_in_missing_list(self, artifact_missing_cross_ref):
        """Path to missing file appears in cross_references.missing."""
        result = vas.validate_single_artifact(artifact_missing_cross_ref)

        missing_refs = result["checks"]["cross_references"]["missing"]
        assert len(missing_refs) > 0
        assert any("/nonexistent/path/to/prd.md" in ref for ref in missing_refs)

    def test_missing_cross_ref_produces_issue(self, artifact_missing_cross_ref):
        """Missing cross reference produces an issue entry."""
        result = vas.validate_single_artifact(artifact_missing_cross_ref)

        assert len(result["issues"]) > 0

    def test_valid_cross_ref_in_found_list(self, valid_adr_artifact):
        """Existing referenced file appears in cross_references.found."""
        result = vas.validate_single_artifact(valid_adr_artifact)

        found_refs = result["checks"]["cross_references"]["found"]
        assert len(found_refs) > 0


class TestFileSizeChecks:
    """Test file size boundary conditions."""

    def test_file_too_large_size_not_ok(self, artifact_too_large):
        """File exceeding 51200 bytes has file_size.ok = False."""
        result = vas.validate_single_artifact(artifact_too_large)

        assert result["checks"]["file_size"]["ok"] is False
        assert result["checks"]["file_size"]["bytes"] > 51200

    def test_file_too_large_produces_issue(self, artifact_too_large):
        """Oversized file produces an issue entry."""
        result = vas.validate_single_artifact(artifact_too_large)

        assert len(result["issues"]) > 0
        assert any("size" in issue.lower() or "large" in issue.lower() or "bytes" in issue.lower()
                   for issue in result["issues"])

    def test_empty_file_size_not_ok(self, artifact_empty):
        """Empty file (< 10 bytes) has file_size.ok = False."""
        result = vas.validate_single_artifact(artifact_empty)

        assert result["checks"]["file_size"]["ok"] is False
        assert result["checks"]["file_size"]["bytes"] < 10

    def test_empty_file_produces_issue(self, artifact_empty):
        """Empty file produces an issue entry."""
        result = vas.validate_single_artifact(artifact_empty)

        assert len(result["issues"]) > 0
        assert any("empty" in issue.lower() or "size" in issue.lower()
                   for issue in result["issues"])


class TestUnknownArtifactType:
    """Test behavior for artifact types not in the registry."""

    def test_unknown_type_no_required_sections_error(self, artifact_unknown_type):
        """Unknown type produces no missing sections (registry has no entry)."""
        result = vas.validate_single_artifact(artifact_unknown_type)

        assert result["checks"]["required_sections"]["missing"] == []

    def test_unknown_type_no_issues_from_sections(self, artifact_unknown_type):
        """Unknown type does not produce issues from missing required sections."""
        result = vas.validate_single_artifact(artifact_unknown_type)

        # Issues might exist for other reasons but not for missing sections
        section_issues = [i for i in result["issues"]
                          if "missing section" in i.lower() or "required section" in i.lower()]
        assert section_issues == []


# ---------------------------------------------------------------------------
# Tests: validate_artifacts (multi-artifact aggregation)
# ---------------------------------------------------------------------------

class TestValidateArtifactsAggregation:
    """Test validate_artifacts aggregation of multiple artifacts."""

    def test_all_valid_overall_ok(self, valid_test_design_artifact):
        """All valid artifacts produce overall 'ok'."""
        output = vas.validate_artifacts([valid_test_design_artifact])

        assert output["overall"] == "ok"

    def test_artifact_with_issues_overall_warnings(self, artifact_missing_section):
        """Artifact with issues produces overall 'warnings'."""
        output = vas.validate_artifacts([artifact_missing_section])

        assert output["overall"] == "warnings"

    def test_output_has_artifacts_list(self, valid_test_design_artifact):
        """Output contains 'artifacts' list with one entry per input."""
        output = vas.validate_artifacts([valid_test_design_artifact])

        assert "artifacts" in output
        assert len(output["artifacts"]) == 1

    def test_multiple_artifacts_all_in_output(self, valid_test_design_artifact, artifact_missing_section):
        """Multiple artifacts each appear in the output list."""
        output = vas.validate_artifacts([valid_test_design_artifact, artifact_missing_section])

        assert len(output["artifacts"]) == 2

    def test_mixed_artifacts_overall_warnings(self, valid_test_design_artifact, artifact_missing_section):
        """Mix of valid and invalid artifacts produces overall 'warnings'."""
        output = vas.validate_artifacts([valid_test_design_artifact, artifact_missing_section])

        assert output["overall"] == "warnings"


# ---------------------------------------------------------------------------
# Tests: Exit codes via CLI
# ---------------------------------------------------------------------------

class TestExitCodes:
    """Test correct exit codes from CLI invocation."""

    def test_valid_artifact_exits_0(self, valid_test_design_artifact):
        """Valid artifact produces exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Expected 0, got {result.returncode}. stderr: {result.stderr}"

    def test_missing_section_exits_1(self, artifact_missing_section):
        """Artifact with missing section produces exit code 1 (warning)."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_missing_section)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, f"Expected 1, got {result.returncode}. stderr: {result.stderr}"

    def test_invalid_yaml_exits_1(self, artifact_invalid_yaml):
        """Artifact with invalid YAML produces exit code 1 (warning)."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_invalid_yaml)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, f"Expected 1, got {result.returncode}. stderr: {result.stderr}"

    def test_missing_cross_ref_exits_1(self, artifact_missing_cross_ref):
        """Artifact with missing cross-reference produces exit code 1."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_missing_cross_ref)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, f"Expected 1, got {result.returncode}. stderr: {result.stderr}"

    def test_file_too_large_exits_1(self, artifact_too_large):
        """Oversized artifact produces exit code 1."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_too_large)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, f"Expected 1, got {result.returncode}. stderr: {result.stderr}"

    def test_empty_file_exits_1(self, artifact_empty):
        """Empty artifact produces exit code 1."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_empty)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, f"Expected 1, got {result.returncode}. stderr: {result.stderr}"

    def test_unknown_type_exits_0(self, artifact_unknown_type):
        """Unknown artifact type produces exit code 0 (no required sections to check)."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_unknown_type)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Expected 0, got {result.returncode}. stderr: {result.stderr}"

    def test_file_not_found_exits_2(self, tmp_path):
        """Non-existent file produces exit code 2 (error)."""
        nonexistent = tmp_path / "does-not-exist.md"
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(nonexistent)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 2, f"Expected 2, got {result.returncode}. stderr: {result.stderr}"


# ---------------------------------------------------------------------------
# Tests: JSON output structure
# ---------------------------------------------------------------------------

class TestJSONOutput:
    """Test that CLI produces valid JSON to stdout."""

    def test_output_is_valid_json(self, valid_test_design_artifact):
        """CLI output is parseable JSON."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Output is not valid JSON: {e}\nOutput: {result.stdout}")

        assert "overall" in data
        assert "artifacts" in data

    def test_artifact_entry_has_required_fields(self, valid_test_design_artifact):
        """Each artifact entry in JSON has path, checks, issues."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        entry = data["artifacts"][0]
        assert "path" in entry
        assert "checks" in entry
        assert "issues" in entry

    def test_checks_has_required_keys(self, valid_test_design_artifact):
        """checks dict contains frontmatter_valid, required_sections, cross_references, file_size."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        checks = data["artifacts"][0]["checks"]
        assert "frontmatter_valid" in checks
        assert "required_sections" in checks
        assert "cross_references" in checks
        assert "file_size" in checks

    def test_required_sections_has_present_and_missing(self, valid_test_design_artifact):
        """required_sections has 'present' and 'missing' keys."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        rs = data["artifacts"][0]["checks"]["required_sections"]
        assert "present" in rs
        assert "missing" in rs

    def test_cross_references_has_found_and_missing(self, valid_test_design_artifact):
        """cross_references has 'found' and 'missing' keys."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        cr = data["artifacts"][0]["checks"]["cross_references"]
        assert "found" in cr
        assert "missing" in cr

    def test_file_size_has_bytes_and_ok(self, valid_test_design_artifact):
        """file_size has 'bytes' and 'ok' keys."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        fs = data["artifacts"][0]["checks"]["file_size"]
        assert "bytes" in fs
        assert "ok" in fs

    def test_overall_ok_for_valid_artifact(self, valid_test_design_artifact):
        """overall is 'ok' for a valid artifact."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(valid_test_design_artifact)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)
        assert data["overall"] == "ok"

    def test_overall_warnings_for_artifact_with_issues(self, artifact_missing_section):
        """overall is 'warnings' for artifact with issues."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(artifact_missing_section)],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)
        assert data["overall"] == "warnings"

    def test_file_not_found_outputs_json_with_errors(self, tmp_path):
        """Non-existent file outputs JSON with overall 'errors'."""
        nonexistent = tmp_path / "does-not-exist.md"
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(nonexistent)],
            capture_output=True,
            text=True
        )
        # Should still produce JSON even on error
        try:
            data = json.loads(result.stdout)
            assert data["overall"] == "errors"
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON output even for error case. Got: {result.stdout}")
