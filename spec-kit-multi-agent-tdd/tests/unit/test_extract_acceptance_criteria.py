#!/usr/bin/env python3
"""Unit tests for scripts/extract_acceptance_criteria.py"""

import json
import subprocess
import tempfile
from pathlib import Path
import pytest
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestExtractAcceptanceCriteriaScript:
    """Test extract_acceptance_criteria.py script."""

    @pytest.fixture
    def spec_with_ac(self):
        """Sample spec with acceptance criteria."""
        return """# Feature: User Login

## Acceptance Criteria
- AC-1: User can login with email and password
- AC-2: Invalid credentials show error message
- AC-3: Successful login redirects to dashboard

## Related Artifacts
- NFR-PERF-001
"""

    @pytest.fixture
    def spec_without_ac(self):
        """Sample spec without acceptance criteria section."""
        return """# Feature: User Login

## User Stories
- As a user...

## Technical Requirements
- Backend API
"""

    @pytest.fixture
    def script_path(self):
        """Path to the script being tested."""
        return Path(__file__).parent.parent.parent / "scripts" / "extract_acceptance_criteria.py"

    def test_stdin_json_output(self, spec_with_ac, script_path):
        """Reads from stdin and outputs JSON by default."""
        result = subprocess.run(
            ["python3", str(script_path)],
            input=spec_with_ac,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "acceptance_criteria" in data
        assert "count" in data
        assert data["count"] == 3
        assert len(data["acceptance_criteria"]) == 3
        assert "AC-1: User can login with email and password" in data["acceptance_criteria"]

    def test_file_input(self, spec_with_ac, script_path, tmp_path):
        """Reads from file with --file flag."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_with_ac)

        result = subprocess.run(
            ["python3", str(script_path), "--file", str(spec_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["count"] == 3

    def test_list_format(self, spec_with_ac, script_path):
        """Outputs as newline-separated list with --format list."""
        result = subprocess.run(
            ["python3", str(script_path), "--format", "list"],
            input=spec_with_ac,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "AC-1: User can login with email and password"
        assert lines[1] == "AC-2: Invalid credentials show error message"
        assert lines[2] == "AC-3: Successful login redirects to dashboard"

    def test_count_format(self, spec_with_ac, script_path):
        """Outputs count only with --format count."""
        result = subprocess.run(
            ["python3", str(script_path), "--format", "count"],
            input=spec_with_ac,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert result.stdout.strip() == "3"

    def test_no_ac_found_exit_1(self, spec_without_ac, script_path):
        """Exits with code 1 when no AC found."""
        result = subprocess.run(
            ["python3", str(script_path)],
            input=spec_without_ac,
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        # Should still output valid JSON with empty array
        data = json.loads(result.stdout)
        assert data["count"] == 0
        assert data["acceptance_criteria"] == []

    def test_file_not_found_exit_2(self, script_path):
        """Exits with code 2 when file not found."""
        result = subprocess.run(
            ["python3", str(script_path), "--file", "/nonexistent/file.md"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 2
        assert "not found" in result.stderr.lower() or "no such file" in result.stderr.lower()

    def test_various_formats(self, script_path):
        """Handles various AC formatting styles."""
        spec = """
## Acceptance Criteria
- AC-1: Numbered list item
* AC-2: Asterisk bullet item
- **AC-3**: Bold formatted item
  - AC-4: Indented item
- AC-5: Plain item

## Next Section
"""
        result = subprocess.run(
            ["python3", str(script_path)],
            input=spec,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["count"] == 5

    def test_h3_section(self, script_path):
        """Finds AC in H3 heading (### Acceptance Criteria)."""
        spec = """
# Feature

### Acceptance Criteria
- AC-1: First item
- AC-2: Second item

### Next Section
"""
        result = subprocess.run(
            ["python3", str(script_path)],
            input=spec,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["count"] == 2

    def test_case_insensitive_heading(self, script_path):
        """Finds AC with case-insensitive heading match."""
        spec = """
## ACCEPTANCE CRITERIA
- AC-1: First item
- AC-2: Second item

## NEXT SECTION
"""
        result = subprocess.run(
            ["python3", str(script_path)],
            input=spec,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["count"] == 2

    def test_stops_at_next_heading(self, script_path):
        """Stops extracting at next heading."""
        spec = """
## Acceptance Criteria
- AC-1: First item
- AC-2: Second item

## Technical Requirements
- Not an AC item
"""
        result = subprocess.run(
            ["python3", str(script_path)],
            input=spec,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["count"] == 2
        assert "Not an AC item" not in str(data["acceptance_criteria"])

    def test_empty_stdin_exit_2(self, script_path):
        """Exits with code 2 when stdin is empty."""
        result = subprocess.run(
            ["python3", str(script_path)],
            input="",
            capture_output=True,
            text=True
        )

        # Empty content is not an error, just no AC found
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["count"] == 0
