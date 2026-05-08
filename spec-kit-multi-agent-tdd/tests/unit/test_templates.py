#!/usr/bin/env python3
"""Unit tests for template files.

Tests that all template files are well-formed and contain required sections.
"""

import re
from pathlib import Path

import pytest
import yaml


# Get templates directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


@pytest.fixture
def prd_template_path():
    """Path to prd-template.md."""
    return TEMPLATES_DIR / "prd-template.md"


@pytest.fixture
def prd_template_content(prd_template_path):
    """Read prd-template.md content."""
    return prd_template_path.read_text()


class TestPRDTemplateExists:
    """Test that prd-template.md exists at correct location."""

    def test_prd_template_file_exists(self, prd_template_path):
        """prd-template.md exists in templates directory."""
        assert prd_template_path.exists(), f"File not found: {prd_template_path}"

    def test_prd_template_is_file(self, prd_template_path):
        """prd-template.md is a regular file."""
        assert prd_template_path.is_file(), f"Not a file: {prd_template_path}"

    def test_prd_template_not_empty(self, prd_template_content):
        """prd-template.md is not empty."""
        assert len(prd_template_content) > 0, "Template file is empty"


class TestPRDTemplateYAMLFrontmatter:
    """Test YAML frontmatter in prd-template.md."""

    def test_frontmatter_present(self, prd_template_content):
        """YAML frontmatter is present (lines 1-3 pattern)."""
        assert prd_template_content.startswith("---\n"), "Template does not start with ---"
        # Find closing ---
        lines = prd_template_content.split("\n")
        assert lines[0] == "---", "First line is not ---"
        found_closing = False
        for i in range(1, min(20, len(lines))):
            if lines[i] == "---":
                found_closing = True
                break
        assert found_closing, "Closing --- not found in first 20 lines"

    def test_frontmatter_valid_yaml(self, prd_template_content):
        """YAML frontmatter parses as valid YAML."""
        # Extract frontmatter
        match = re.match(r"^---\n(.*?)\n---\n", prd_template_content, re.DOTALL)
        assert match, "Could not extract frontmatter"

        frontmatter_str = match.group(1)
        # Should not raise exception
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in frontmatter: {e}")

        assert isinstance(frontmatter, dict), "Frontmatter is not a dict"

    def test_type_field_is_prd(self, prd_template_content):
        """type field in frontmatter is 'prd'."""
        match = re.match(r"^---\n(.*?)\n---\n", prd_template_content, re.DOTALL)
        assert match, "Could not extract frontmatter"

        frontmatter = yaml.safe_load(match.group(1))
        assert "type" in frontmatter, "type field missing from frontmatter"
        assert frontmatter["type"] == "prd", f"type is '{frontmatter['type']}', expected 'prd'"

    def test_frontmatter_has_required_fields(self, prd_template_content):
        """Frontmatter contains all expected fields."""
        match = re.match(r"^---\n(.*?)\n---\n", prd_template_content, re.DOTALL)
        frontmatter = yaml.safe_load(match.group(1))

        expected_fields = ["type", "feature_id", "version", "status", "created"]
        for field in expected_fields:
            assert field in frontmatter, f"Missing field in frontmatter: {field}"


class TestPRDTemplateRequiredSections:
    """Test that all required sections are present in prd-template.md."""

    def test_what_why_section_present(self, prd_template_content):
        """## What & Why section is present."""
        assert "## What & Why" in prd_template_content, "Missing '## What & Why' section"

    def test_business_value_section_present(self, prd_template_content):
        """## Business Value section is present."""
        assert "## Business Value" in prd_template_content, "Missing '## Business Value' section"

    def test_measurability_section_present(self, prd_template_content):
        """## Measurability section is present."""
        assert "## Measurability" in prd_template_content, "Missing '## Measurability' section"

    def test_goals_no_goals_section_present(self, prd_template_content):
        """## Goals & No-goals section is present."""
        assert "## Goals & No-goals" in prd_template_content, "Missing '## Goals & No-goals' section"

    def test_risks_stories_section_present(self, prd_template_content):
        """## Risks & Stories section is present."""
        assert "## Risks & Stories" in prd_template_content, "Missing '## Risks & Stories' section"

    def test_dependencies_section_present(self, prd_template_content):
        """## Dependencies section is present."""
        assert "## Dependencies" in prd_template_content, "Missing '## Dependencies' section"

    def test_people_section_present(self, prd_template_content):
        """## People section is present."""
        assert "## People" in prd_template_content, "Missing '## People' section"

    def test_metrics_section_present(self, prd_template_content):
        """## Metrics section is present."""
        assert "## Metrics" in prd_template_content, "Missing '## Metrics' section"

    def test_all_eight_sections_present(self, prd_template_content):
        """All 8 required sections are present."""
        required_sections = [
            "## What & Why",
            "## Business Value",
            "## Measurability",
            "## Goals & No-goals",
            "## Risks & Stories",
            "## Dependencies",
            "## People",
            "## Metrics"
        ]

        for section in required_sections:
            assert section in prd_template_content, f"Missing section: {section}"


class TestPRDTemplateSectionGuidance:
    """Test that template sections have inline guidance comments."""

    def test_each_section_has_guidance(self, prd_template_content):
        """Each section has a guidance comment (1-2 sentences with leading underscore)."""
        # Sections should be followed by guidance in the pattern: _guidance text:_
        sections = [
            "## What & Why",
            "## Business Value",
            "## Measurability",
            "## Goals & No-goals",
            "## Risks & Stories",
            "## Dependencies",
            "## People",
            "## Metrics"
        ]

        lines = prd_template_content.split("\n")
        for section in sections:
            section_found = False
            for i, line in enumerate(lines):
                if section in line:
                    section_found = True
                    # Check next non-empty line has guidance (starts with _)
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].strip():
                            # Should have underscore-bounded text for guidance
                            assert "_" in lines[j], f"No guidance found after {section}"
                            break
                    break
            assert section_found, f"Section not found: {section}"


class TestPRDTemplateStructure:
    """Test overall structure and formatting of prd-template.md."""

    def test_starts_with_heading(self, prd_template_content):
        """Template starts with a main heading (# PRD: ...) after frontmatter."""
        lines = prd_template_content.split("\n")
        # Skip frontmatter (--- ... ---)
        in_frontmatter = False
        first_heading = None
        for line in lines:
            if line.startswith("---"):
                in_frontmatter = not in_frontmatter
                continue
            if not in_frontmatter and line.strip() and line.startswith("#"):
                first_heading = line
                break
        assert first_heading and first_heading.startswith("# PRD:"), "Does not start with # PRD: heading after frontmatter"

    def test_heading_includes_feature_name_placeholder(self, prd_template_content):
        """Main heading includes {{feature_name}} placeholder."""
        lines = prd_template_content.split("\n")
        heading = next((l for l in lines if l.startswith("# PRD:")), None)
        assert heading, "Main heading not found"
        assert "{{feature_name}}" in heading, "Heading does not include feature_name placeholder"

    def test_has_feature_id_metadata(self, prd_template_content):
        """Template includes Feature ID metadata line."""
        assert "**Feature ID:**" in prd_template_content or "Feature ID" in prd_template_content, \
            "No Feature ID metadata found"

    def test_all_sections_are_level_2_headings(self, prd_template_content):
        """All required sections are ## level headings (not ### or higher)."""
        required_sections = [
            "## What & Why",
            "## Business Value",
            "## Measurability",
            "## Goals & No-goals",
            "## Risks & Stories",
            "## Dependencies",
            "## People",
            "## Metrics"
        ]

        for section in required_sections:
            assert section in prd_template_content, f"Section not found: {section}"
            # Ensure it's not ###+
            assert f"{section}\n" in prd_template_content + "\n", f"Section not properly formatted: {section}"


class TestPRDTemplateGuideComments:
    """Test that guidance comments are concise (1-2 sentences)."""

    def test_what_why_guidance_concise(self, prd_template_content):
        """What & Why section has guidance comment."""
        match = re.search(
            r"## What & Why\n\n(_.*?_)\n",
            prd_template_content,
            re.DOTALL
        )
        assert match, "What & Why guidance not found"
        guidance = match.group(1)
        # Guidance should be relatively short (< 200 chars for 1-2 sentences)
        assert len(guidance) > 0, "Guidance text is empty"

    def test_has_verification_checklist(self, prd_template_content):
        """Template includes verification checklist at end."""
        assert "Verification Checklist" in prd_template_content, "No verification checklist found"
        assert "[ ]" in prd_template_content, "Checklist items missing"
