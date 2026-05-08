"""
Tests for template files.

Validates that all template files:
- Exist and are readable
- Have proper metadata headers
- Contain required sections
- Use consistent formatting
"""

import os
from pathlib import Path
import pytest
import re


class TestSystemConstitutionTemplate:
    """Tests for system-constitution-template.md"""

    @pytest.fixture
    def template_path(self):
        """Path to system-constitution-template.md"""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / "templates" / "system-constitution-template.md"

    @pytest.fixture
    def template_content(self, template_path):
        """Load template content"""
        assert template_path.exists(), f"Template not found at {template_path}"
        return template_path.read_text()

    def test_system_constitution_template_exists(self, template_path):
        """Verify system-constitution-template.md exists"""
        assert template_path.exists(), "system-constitution-template.md not found"
        assert template_path.is_file(), "system-constitution-template.md is not a file"

    def test_system_constitution_has_title_header(self, template_content):
        """Verify template has proper title header"""
        assert template_content.startswith("# System Constitution:"), \
            "Template should start with '# System Constitution:' header"

    def test_system_constitution_has_metadata_section(self, template_content):
        """Verify template has metadata (system_name, version, status, timestamp)"""
        metadata_fields = ["System Name:", "Version:", "Status:", "Created:"]
        for field in metadata_fields:
            assert field in template_content, \
                f"Missing metadata field: {field}"

    def test_system_constitution_has_tech_radar_section(self, template_content):
        """Verify Tech Radar section exists"""
        assert "## Tech Radar" in template_content, \
            "Missing '## Tech Radar' section"

    def test_system_constitution_has_team_tech_skills_section(self, template_content):
        """Verify Team Tech Skills section exists"""
        assert "## Team Tech Skills" in template_content, \
            "Missing '## Team Tech Skills' section"

    def test_system_constitution_has_compliance_governance_section(self, template_content):
        """Verify Compliance & Governance section exists"""
        assert "## Compliance & Governance" in template_content, \
            "Missing '## Compliance & Governance' section"

    def test_system_constitution_has_nfr_section(self, template_content):
        """Verify Non-Functional Requirements section exists"""
        assert "## Non-Functional Requirements" in template_content, \
            "Missing '## Non-Functional Requirements' section"

    def test_system_constitution_has_observability_subsection(self, template_content):
        """Verify Observability subsection under NFR"""
        assert "### Observability" in template_content, \
            "Missing '### Observability' subsection under Non-Functional Requirements"

    def test_system_constitution_has_testing_strategy_subsection(self, template_content):
        """Verify Testing Strategy subsection under NFR"""
        assert "### Testing Strategy" in template_content, \
            "Missing '### Testing Strategy' subsection under Non-Functional Requirements"

    def test_system_constitution_has_performance_subsection(self, template_content):
        """Verify Performance subsection under NFR"""
        assert "### Performance" in template_content, \
            "Missing '### Performance' subsection under Non-Functional Requirements"

    def test_system_constitution_has_scalability_subsection(self, template_content):
        """Verify Scalability subsection under NFR"""
        assert "### Scalability" in template_content, \
            "Missing '### Scalability' subsection under Non-Functional Requirements"

    def test_system_constitution_has_reliability_subsection(self, template_content):
        """Verify Reliability subsection under NFR"""
        assert "### Reliability" in template_content, \
            "Missing '### Reliability' subsection under Non-Functional Requirements"

    def test_system_constitution_nfr_subsections_are_h3(self, template_content):
        """Verify all NFR subsections use ### (h3) heading"""
        # Extract the NFR section
        nfr_start = template_content.find("## Non-Functional Requirements")
        assert nfr_start != -1, "NFR section not found"

        # Check for remaining sections that would mark end of NFR
        verification_start = template_content.find("---", nfr_start)
        nfr_content = template_content[nfr_start:verification_start]

        subsections = ["Observability", "Testing Strategy", "Performance", "Scalability", "Reliability"]
        for subsection in subsections:
            pattern = f"### {subsection}"
            assert pattern in nfr_content, \
                f"NFR subsection '{subsection}' not properly formatted as h3"

    def test_system_constitution_has_verification_checklist(self, template_content):
        """Verify template has verification checklist"""
        assert "**Verification Checklist:**" in template_content, \
            "Missing verification checklist"
        assert "- [ ]" in template_content, \
            "Verification checklist should use checkbox format"

    def test_system_constitution_uses_template_variables(self, template_content):
        """Verify template uses Jinja2/mustache template variables"""
        # Should have at least system_name variable
        assert "{{system_name}}" in template_content or \
               "{{version}}" in template_content or \
               "{{timestamp}}" in template_content, \
            "Template should use template variables like {{variable_name}}"

    def test_system_constitution_has_inline_guidance(self, template_content):
        """Verify sections have inline guidance comments"""
        # Check for guidance text patterns (italicized or indented)
        guidance_patterns = [
            "_Inventory of technologies",
            "_Document the technical competencies",
            "_Legal, regulatory",
        ]
        found_guidance = False
        for pattern in guidance_patterns:
            if pattern in template_content:
                found_guidance = True
                break

        assert found_guidance, \
            "Template sections should include inline guidance comments"

    def test_system_constitution_sections_order(self, template_content):
        """Verify sections appear in expected order"""
        sections = [
            "## Tech Radar",
            "## Team Tech Skills",
            "## Compliance & Governance",
            "## Non-Functional Requirements",
            "### Observability",
            "### Testing Strategy",
            "### Performance",
            "### Scalability",
            "### Reliability",
        ]

        last_pos = -1
        for section in sections:
            pos = template_content.find(section)
            assert pos != -1, f"Section '{section}' not found"
            assert pos > last_pos, \
                f"Section '{section}' appears out of order"
            last_pos = pos

    def test_system_constitution_no_unresolved_placeholders(self, template_content):
        """Verify template structure is complete (basic check)"""
        # Should not have incomplete patterns like "{{" without closing "}}"
        open_braces = template_content.count("{{")
        close_braces = template_content.count("}}")
        assert open_braces == close_braces, \
            "Template has unmatched placeholder braces"

    def test_system_constitution_markdown_validity(self, template_content):
        """Verify basic markdown validity"""
        lines = template_content.split("\n")

        # Count headers to ensure structure
        h2_count = sum(1 for line in lines if line.startswith("## "))
        h3_count = sum(1 for line in lines if line.startswith("### "))

        assert h2_count >= 4, "Template should have at least 4 h2 sections"
        assert h3_count >= 5, "Template should have at least 5 h3 subsections (NFR items)"


class TestAllTemplatesExist:
    """Test that all expected templates exist"""

    @pytest.fixture
    def templates_dir(self):
        """Path to templates directory"""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / "templates"

    def test_all_required_templates_exist(self, templates_dir):
        """Verify all required template files exist"""
        required_templates = [
            "arch-review-template.md",
            "code-review-template.md",
            "implementation-notes-template.md",
            "test-design-template.md",
            "workflow-summary-template.md",
            "system-constitution-template.md",
        ]

        for template_name in required_templates:
            template_path = templates_dir / template_name
            assert template_path.exists(), \
                f"Required template '{template_name}' not found at {template_path}"
            assert template_path.is_file(), \
                f"Template '{template_name}' exists but is not a file"

    def test_all_templates_are_readable(self, templates_dir):
        """Verify all templates are readable files"""
        for template_file in templates_dir.glob("*-template.md"):
            assert template_file.is_file(), f"{template_file.name} is not a file"
            content = template_file.read_text()
            assert len(content) > 0, f"Template {template_file.name} is empty"

    def test_all_templates_have_proper_markdown(self, templates_dir):
        """Verify all templates have proper markdown structure"""
        for template_file in templates_dir.glob("*-template.md"):
            content = template_file.read_text()
            # Should either start with # or with --- (YAML frontmatter)
            assert content.startswith("#") or content.startswith("---"), \
                f"Template {template_file.name} should start with markdown header or YAML frontmatter"


class TestTemplateConsistency:
    """Test consistency across all templates"""

    @pytest.fixture
    def templates_dir(self):
        """Path to templates directory"""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / "templates"

    def test_templates_have_proper_structure(self, templates_dir):
        """Verify templates have structured content"""
        for template_file in templates_dir.glob("*-template.md"):
            content = template_file.read_text()

            # All templates should have some form of headers
            has_headers = "##" in content
            assert has_headers, \
                f"Template {template_file.name} should have markdown headers"

    def test_system_constitution_has_all_required_sections(self, templates_dir):
        """Verify system-constitution has all required sections"""
        template_file = templates_dir / "system-constitution-template.md"
        content = template_file.read_text()

        required_sections = [
            "## Tech Radar",
            "## Team Tech Skills",
            "## Compliance & Governance",
            "## Non-Functional Requirements",
            "### Observability",
            "### Testing Strategy",
            "### Performance",
            "### Scalability",
            "### Reliability",
        ]

        for section in required_sections:
            assert section in content, \
                f"system-constitution-template.md missing required section: {section}"

    def test_templates_have_verification_checklists(self, templates_dir):
        """Verify templates include verification checklists"""
        for template_file in templates_dir.glob("*-template.md"):
            content = template_file.read_text()

            # All templates should have some form of verification/checklist
            has_checklist = "**Verification Checklist:**" in content or \
                            "**Checklist:**" in content or \
                            "- [ ]" in content

            assert has_checklist, \
                f"Template {template_file.name} should have verification checklist"
