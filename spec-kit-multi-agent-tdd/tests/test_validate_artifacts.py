"""
Tests for artifact validator (S2B-004).

Tests validation of TDD workflow artifacts:
- File existence checks
- Template section validation
- Evidence timestamp validation (RED before GREEN)
- RED/GREEN state evidence validation
"""

import json
from pathlib import Path
from datetime import datetime
import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from validate_artifacts import (
    validate_artifact_exists,
    validate_template_sections,
    validate_evidence_timestamps,
    validate_red_green_evidence,
    validate_feature_artifacts,
)


@pytest.fixture
def temp_artifacts_dir(tmp_path):
    """Create temporary artifacts directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return artifacts


@pytest.fixture
def sample_test_design(temp_artifacts_dir):
    """Create a valid test design artifact."""
    content = """# Test Design: Sample Feature

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

## Test Implementation Details

Technical details.

## Escalations

No blockers.

## Decision

**Route:** implement
"""
    file_path = temp_artifacts_dir / "feat-123-test-design.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_arch_review(temp_artifacts_dir):
    """Create a valid architecture review artifact."""
    content = """# Architecture Review: Sample Feature

**Feature ID:** feat-123
**Reviewer:** @arch
**Status:** draft
**Created:** 2024-01-15T11:00:00Z

## Review Scope

Scope documented.

## Architecture Impacts

### Design Alignment
Assessment here.

### Component Design
Components evaluated.

### Data Flow & Dependencies
Data flow documented.

## Safety Constraints

### Strengths
Good points.

### Concerns
No concerns.

### Blockers
No blockers.

## Recommendations

Suggestions here.

## Review Cycle

Cycle 1.

## Verdict

**Verdict:** APPROVED
"""
    file_path = temp_artifacts_dir / "feat-123-arch-review.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_code_review(temp_artifacts_dir):
    """Create a valid code review artifact."""
    content = """# Code Review: Sample Feature

**Feature ID:** feat-123
**Reviewer:** @review
**Status:** draft
**Created:** 2024-01-15T12:00:00Z

## Review Scope

Scope documented.

## Code Quality

### Readability & Maintainability
Code is readable.

### Test Quality
Tests are good.

### Error Handling
Errors handled.

## Test Coverage

### Strengths
Good code.

### Concerns
No concerns.

### Blockers
No blockers.

## Code Smells Detected

None detected.

## Security Review

Secure.

## Performance Review

Performant.

## Review Cycle

Cycle 1.

## Verdict

**Verdict:** APPROVED
"""
    file_path = temp_artifacts_dir / "feat-123-code-review.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_workflow_summary(temp_artifacts_dir):
    """Create a valid workflow summary with proper timestamps."""
    content = """# Workflow Summary: Sample Feature

**Feature ID:** feat-123
**Status:** completed
**Created:** 2024-01-15T10:00:00Z
**Completed:** 2024-01-15T13:00:00Z

## Feature Information

Workflow completed successfully.

## Test Evidence

All artifacts created.

### Test Design (Step 7)
- **Path:** `docs/tests/test-design/feat-123-test-design.md`
- **Agent:** @test
- **Status:** COMPLETED
- **RED State:** Valid (MISSING_BEHAVIOR confirmed)

**Test Evidence:**
- RED State Timestamp: 2024-01-15T10:30:00Z
- GREEN State Timestamp: 2024-01-15T11:45:00Z
- RED State: MISSING_BEHAVIOR confirmed
- GREEN State: All tests passing

## Implementation Evidence

### Implementation Notes (Step 8)
- **Path:** `docs/implementation/feat-123-implementation-notes.md`
- **Agent:** @implement
- **Status:** COMPLETED
- **GREEN State:** All tests passing

Implementation completed.

## Review Evidence

### Architecture Review (Step 9)
- **Path:** `docs/reviews/arch-review/feat-123-arch-review.md`
- **Reviewer:** @arch
- **Status:** APPROVED

### Code Review (Step 9)
- **Path:** `docs/reviews/code-review/feat-123-code-review.md`
- **Reviewer:** @review
- **Status:** APPROVED

## Review Metrics

Metrics tracked.

## Technical Debt

None.

## Escalations

None.

## Commit Information

**Commit Hash:** abc123

## Lessons Learned

Good workflow.

## Next Steps

Deploy to staging.
"""
    file_path = temp_artifacts_dir / "feat-123-workflow-summary.md"
    file_path.write_text(content)
    return file_path


# Test: validate_artifact_exists
def test_validate_artifact_exists_file_present(sample_test_design):
    """Test artifact existence check - file exists."""
    assert validate_artifact_exists(sample_test_design) is True


def test_validate_artifact_exists_file_missing(temp_artifacts_dir):
    """Test artifact existence check - file missing."""
    missing = temp_artifacts_dir / "missing-file.md"
    assert validate_artifact_exists(missing) is False


# Test: validate_template_sections
def test_validate_template_sections_complete(sample_test_design):
    """Test section validation - all required sections present."""
    required_sections = [
        "Test Design:",
        "Test Strategy",
        "Acceptance Criteria Mapping",
        "RED State Validation",
        "Escalations",
        "Decision",
    ]
    is_valid, missing = validate_template_sections(sample_test_design, required_sections)
    assert is_valid is True
    assert missing == []


def test_validate_template_sections_missing(sample_test_design):
    """Test section validation - detect missing sections."""
    required_sections = [
        "Test Design:",
        "Test Strategy",
        "Missing Section",  # This section doesn't exist
        "Another Missing",  # This section doesn't exist
    ]
    is_valid, missing = validate_template_sections(sample_test_design, required_sections)
    assert is_valid is False
    assert "Missing Section" in missing
    assert "Another Missing" in missing


# Test: validate_evidence_timestamps
def test_validate_evidence_timestamps_valid(sample_workflow_summary):
    """Test timestamp validation - RED before GREEN (valid)."""
    artifacts_dir = sample_workflow_summary.parent
    is_valid, message = validate_evidence_timestamps(artifacts_dir)
    assert is_valid is True
    assert "RED (2024-01-15T10:30:00Z) before GREEN (2024-01-15T11:45:00Z)" in message


def test_validate_evidence_timestamps_invalid(temp_artifacts_dir):
    """Test timestamp validation - GREEN before RED (invalid)."""
    # Create workflow summary with invalid timestamps (GREEN before RED)
    content = """# Workflow Summary: Sample Feature

**Feature ID:** feat-123

## Quality Assurance

**Test Evidence:**
- RED State Timestamp: 2024-01-15T12:00:00Z
- GREEN State Timestamp: 2024-01-15T10:00:00Z
"""
    file_path = temp_artifacts_dir / "feat-123-workflow-summary.md"
    file_path.write_text(content)

    is_valid, message = validate_evidence_timestamps(temp_artifacts_dir)
    assert is_valid is False
    assert "Invalid timestamp order" in message or "after" in message.lower()


def test_validate_evidence_timestamps_missing(temp_artifacts_dir):
    """Test timestamp validation - timestamps missing."""
    # Create workflow summary without timestamps
    content = """# Workflow Summary: Sample Feature

**Feature ID:** feat-123

## Quality Assurance

No timestamps.
"""
    file_path = temp_artifacts_dir / "feat-123-workflow-summary.md"
    file_path.write_text(content)

    is_valid, message = validate_evidence_timestamps(temp_artifacts_dir)
    assert is_valid is False
    assert "missing" in message.lower() or "not found" in message.lower()


# Test: validate_red_green_evidence
def test_validate_red_green_evidence_present(sample_workflow_summary):
    """Test RED/GREEN evidence validation - both states present."""
    artifacts_dir = sample_workflow_summary.parent
    is_valid, message = validate_red_green_evidence(artifacts_dir)
    assert is_valid is True
    assert "Both RED and GREEN evidence found" in message


def test_validate_red_green_evidence_missing_red(temp_artifacts_dir):
    """Test RED/GREEN evidence validation - RED state missing."""
    content = """# Workflow Summary: Sample Feature

**Feature ID:** feat-123

## Quality Assurance

**Test Evidence:**
- GREEN State: All tests passing
"""
    file_path = temp_artifacts_dir / "feat-123-workflow-summary.md"
    file_path.write_text(content)

    is_valid, message = validate_red_green_evidence(temp_artifacts_dir)
    assert is_valid is False
    assert "RED" in message or "missing" in message.lower()


def test_validate_red_green_evidence_missing_green(temp_artifacts_dir):
    """Test RED/GREEN evidence validation - GREEN state missing."""
    content = """# Workflow Summary: Sample Feature

**Feature ID:** feat-123

## Quality Assurance

**Test Evidence:**
- RED State: MISSING_BEHAVIOR confirmed
"""
    file_path = temp_artifacts_dir / "feat-123-workflow-summary.md"
    file_path.write_text(content)

    is_valid, message = validate_red_green_evidence(temp_artifacts_dir)
    assert is_valid is False
    assert "GREEN" in message or "missing" in message.lower()


# Test: validate_feature_artifacts (integration tests)
def test_validate_feature_artifacts_complete(
    temp_artifacts_dir,
    sample_test_design,
    sample_arch_review,
    sample_code_review,
    sample_workflow_summary,
):
    """Test full validation - all mandatory artifacts present and valid."""
    report = validate_feature_artifacts("feat-123", temp_artifacts_dir)

    assert report["feature_id"] == "feat-123"
    assert report["valid"] is True
    assert report["artifacts"]["test_design"]["exists"] is True
    assert report["artifacts"]["test_design"]["valid_structure"] is True
    assert report["artifacts"]["arch_review"]["exists"] is True
    assert report["artifacts"]["code_review"]["exists"] is True
    assert report["artifacts"]["workflow_summary"]["exists"] is True
    assert report["evidence"]["red_green_transition"] is True
    assert report["evidence"]["timestamps_valid"] is True
    assert report["errors"] == []


def test_validate_feature_artifacts_missing_mandatory(temp_artifacts_dir):
    """Test full validation - missing mandatory artifacts."""
    # Only create workflow summary, missing other mandatory artifacts
    content = "# Workflow Summary: Sample Feature\n"
    (temp_artifacts_dir / "feat-123-workflow-summary.md").write_text(content)

    report = validate_feature_artifacts("feat-123", temp_artifacts_dir)

    assert report["valid"] is False
    assert report["artifacts"]["test_design"]["exists"] is False
    assert report["artifacts"]["arch_review"]["exists"] is False
    assert report["artifacts"]["code_review"]["exists"] is False
    assert len(report["errors"]) > 0


def test_validate_feature_artifacts_malformed_structure(temp_artifacts_dir):
    """Test full validation - artifacts exist but malformed structure."""
    # Create artifacts with missing sections
    (temp_artifacts_dir / "feat-123-test-design.md").write_text("# Test Design: Sample\n\nIncomplete.")
    (temp_artifacts_dir / "feat-123-arch-review.md").write_text("# Architecture Review: Sample\n\nIncomplete.")
    (temp_artifacts_dir / "feat-123-code-review.md").write_text("# Code Review: Sample\n\nIncomplete.")
    (temp_artifacts_dir / "feat-123-workflow-summary.md").write_text("# Workflow Summary: Sample\n\nIncomplete.")

    report = validate_feature_artifacts("feat-123", temp_artifacts_dir)

    assert report["valid"] is False
    # At least some artifacts should have invalid structure
    assert any(
        not artifact["valid_structure"]
        for artifact in report["artifacts"].values()
        if artifact["exists"]
    )


# Test: CLI usage (basic integration)
def test_cli_basic_usage(
    temp_artifacts_dir,
    sample_test_design,
    sample_arch_review,
    sample_code_review,
    sample_workflow_summary,
    monkeypatch,
    capsys,
):
    """Test CLI with valid artifacts - exit code 0."""
    # Import main after fixtures are set up
    from validate_artifacts import main

    # Mock command-line arguments
    monkeypatch.setattr(
        "sys.argv",
        ["validate_artifacts.py", "feat-123", "--artifacts-dir", str(temp_artifacts_dir)],
    )

    # Should exit with code 0 (success)
    try:
        main()
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 0

    captured = capsys.readouterr()
    assert "VALID" in captured.out or "valid" in captured.out


def test_cli_missing_artifacts(temp_artifacts_dir, monkeypatch, capsys):
    """Test CLI with missing artifacts - exit code 1."""
    from validate_artifacts import main

    monkeypatch.setattr(
        "sys.argv",
        ["validate_artifacts.py", "feat-123", "--artifacts-dir", str(temp_artifacts_dir)],
    )

    # Should exit with code 1 (validation failure)
    try:
        main()
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 1

    captured = capsys.readouterr()
    assert "INVALID" in captured.out or "invalid" in captured.out or "error" in captured.out.lower()


def test_cli_json_format(
    temp_artifacts_dir,
    sample_test_design,
    sample_arch_review,
    sample_code_review,
    sample_workflow_summary,
    monkeypatch,
    capsys,
):
    """Test CLI with JSON output format."""
    from validate_artifacts import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_artifacts.py",
            "feat-123",
            "--artifacts-dir",
            str(temp_artifacts_dir),
            "--format",
            "json",
        ],
    )

    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()

    # Should be valid JSON
    try:
        report = json.loads(captured.out)
        assert report["feature_id"] == "feat-123"
        assert "valid" in report
        assert "artifacts" in report
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")


def test_cli_verbose_output(
    temp_artifacts_dir,
    sample_test_design,
    sample_arch_review,
    sample_code_review,
    sample_workflow_summary,
    monkeypatch,
    capsys,
):
    """Test CLI with verbose flag shows detailed results."""
    from validate_artifacts import main

    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_artifacts.py",
            "feat-123",
            "--artifacts-dir",
            str(temp_artifacts_dir),
            "--verbose",
        ],
    )

    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()

    # Verbose output should include artifact details
    assert "test-design" in captured.out.lower() or "test_design" in captured.out.lower()
    assert "arch-review" in captured.out.lower() or "arch_review" in captured.out.lower()
    assert "code-review" in captured.out.lower() or "code_review" in captured.out.lower()
