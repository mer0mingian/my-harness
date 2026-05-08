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


class TestSolutionDesignTemplate:
    """Tests for solution-design-template.md"""

    @pytest.fixture
    def template_path(self):
        """Path to solution-design-template.md"""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / "templates" / "solution-design-template.md"

    @pytest.fixture
    def template_content(self, template_path):
        """Load template content"""
        assert template_path.exists(), f"Template not found at {template_path}"
        return template_path.read_text()

    def test_solution_design_template_exists(self, template_path):
        """Verify solution-design-template.md exists"""
        assert template_path.exists(), "solution-design-template.md not found"
        assert template_path.is_file(), "solution-design-template.md is not a file"

    def test_solution_design_has_yaml_frontmatter(self, template_content):
        """Verify template has YAML frontmatter"""
        assert template_content.startswith("---"), \
            "Template should start with YAML frontmatter (---)"
        assert template_content.count("---") >= 2, \
            "Template should have closing YAML frontmatter (---)"

    def test_solution_design_has_type_field(self, template_content):
        """Verify YAML frontmatter has type: solution-design"""
        assert 'type: solution-design' in template_content, \
            "YAML frontmatter should have 'type: solution-design'"

    def test_solution_design_has_adr_ref_field(self, template_content):
        """Verify YAML frontmatter has adr_ref field"""
        assert 'adr_ref:' in template_content, \
            "YAML frontmatter should have 'adr_ref' field"

    def test_solution_design_has_feature_id_field(self, template_content):
        """Verify YAML frontmatter has feature_id field"""
        assert 'feature_id:' in template_content, \
            "YAML frontmatter should have 'feature_id' field"

    def test_solution_design_has_decomposition_view(self, template_content):
        """Verify Decomposition View section exists"""
        assert "## Decomposition View" in template_content, \
            "Missing '## Decomposition View' section"

    def test_solution_design_has_dependency_view(self, template_content):
        """Verify Dependency View section exists"""
        assert "## Dependency View" in template_content, \
            "Missing '## Dependency View' section"

    def test_solution_design_has_interface_view(self, template_content):
        """Verify Interface View section exists"""
        assert "## Interface View" in template_content, \
            "Missing '## Interface View' section"

    def test_solution_design_has_data_design_view(self, template_content):
        """Verify Data Design View section exists"""
        assert "## Data Design View" in template_content, \
            "Missing '## Data Design View' section"

    def test_solution_design_has_c4container_diagram(self, template_content):
        """Verify C4Container mermaid diagram exists"""
        assert "C4Container" in template_content, \
            "Template should have C4Container mermaid diagram"
        assert "```mermaid" in template_content, \
            "Template should have mermaid code blocks"

    def test_solution_design_has_c4component_diagram(self, template_content):
        """Verify C4Component mermaid diagram exists"""
        assert "C4Component" in template_content, \
            "Template should have C4Component mermaid diagram"

    def test_solution_design_has_erdiagram(self, template_content):
        """Verify erDiagram mermaid diagram exists"""
        assert "erDiagram" in template_content, \
            "Template should have erDiagram mermaid diagram"

    def test_solution_design_has_flowchart(self, template_content):
        """Verify flowchart mermaid diagram exists"""
        assert "flowchart" in template_content, \
            "Template should have flowchart mermaid diagram"

    def test_solution_design_has_internal_dependencies(self, template_content):
        """Verify Internal Dependencies subsection exists"""
        assert "### Internal Dependencies" in template_content, \
            "Missing '### Internal Dependencies' subsection"

    def test_solution_design_has_external_dependencies(self, template_content):
        """Verify External Dependencies subsection exists"""
        assert "### External Dependencies" in template_content, \
            "Missing '### External Dependencies' subsection"

    def test_solution_design_has_coupling_analysis(self, template_content):
        """Verify Coupling Analysis subsection exists"""
        assert "### Coupling Analysis" in template_content, \
            "Missing '### Coupling Analysis' subsection"

    def test_solution_design_has_c2_container_subsection(self, template_content):
        """Verify C2 Container Diagram subsection exists"""
        assert "### C2 Container Diagram" in template_content, \
            "Missing '### C2 Container Diagram' subsection"

    def test_solution_design_has_c3_component_subsection(self, template_content):
        """Verify C3 Component Diagram subsection exists"""
        assert "### C3 Component Diagram" in template_content, \
            "Missing '### C3 Component Diagram' subsection"

    def test_solution_design_has_external_api_subsection(self, template_content):
        """Verify External API Contracts subsection exists"""
        assert "### External API Contracts" in template_content, \
            "Missing '### External API Contracts' subsection"

    def test_solution_design_has_internal_interface_subsection(self, template_content):
        """Verify Internal Interface Definitions subsection exists"""
        assert "### Internal Interface Definitions" in template_content, \
            "Missing '### Internal Interface Definitions' subsection"

    def test_solution_design_has_event_schemas_subsection(self, template_content):
        """Verify Event Schemas subsection exists"""
        assert "### Event Schemas" in template_content, \
            "Missing '### Event Schemas' subsection"

    def test_solution_design_has_data_flow_diagram_subsection(self, template_content):
        """Verify Data Flow Diagram subsection exists"""
        assert "### Data Flow Diagram" in template_content, \
            "Missing '### Data Flow Diagram' subsection"

    def test_solution_design_has_erd_subsection(self, template_content):
        """Verify Entity-Relationship Diagram subsection exists"""
        assert "### Entity-Relationship Diagram" in template_content, \
            "Missing '### Entity-Relationship Diagram' subsection"

    def test_solution_design_has_key_schemas_subsection(self, template_content):
        """Verify Key Schemas subsection exists"""
        assert "### Key Schemas" in template_content, \
            "Missing '### Key Schemas' subsection"

    def test_solution_design_has_verification_checklist(self, template_content):
        """Verify template has verification checklist"""
        assert "**Verification Checklist:**" in template_content, \
            "Missing verification checklist"
        assert "- [ ]" in template_content, \
            "Verification checklist should use checkbox format"

    def test_solution_design_uses_template_variables(self, template_content):
        """Verify template uses Jinja2/mustache template variables"""
        assert "{{feature_id}}" in template_content, \
            "Template should use {{feature_id}} variable"
        assert "{{timestamp}}" in template_content, \
            "Template should use {{timestamp}} variable"

    def test_solution_design_has_inline_guidance(self, template_content):
        """Verify sections have inline guidance comments"""
        # Check for guidance text patterns (italicized)
        guidance_patterns = [
            "Decompose the system into logical containers",
            "Map out the dependencies between system components",
            "Define the boundary contracts",
            "Specify how data flows through the system",
        ]
        found_guidance = 0
        for pattern in guidance_patterns:
            if pattern in template_content:
                found_guidance += 1

        assert found_guidance >= 2, \
            "Template sections should include inline guidance comments"

    def test_solution_design_views_order(self, template_content):
        """Verify views appear in expected order"""
        views = [
            "## Decomposition View",
            "## Dependency View",
            "## Interface View",
            "## Data Design View",
        ]

        last_pos = -1
        for view in views:
            pos = template_content.find(view)
            assert pos != -1, f"View '{view}' not found"
            assert pos > last_pos, \
                f"View '{view}' appears out of order"
            last_pos = pos

    def test_solution_design_no_unresolved_placeholders(self, template_content):
        """Verify template structure is complete (basic check)"""
        # Should not have incomplete patterns like "{{" without closing "}}"
        open_braces = template_content.count("{{")
        close_braces = template_content.count("}}")
        assert open_braces == close_braces, \
            "Template has unmatched placeholder braces"

    def test_solution_design_markdown_validity(self, template_content):
        """Verify basic markdown validity"""
        lines = template_content.split("\n")

        # Count headers to ensure structure
        h2_count = sum(1 for line in lines if line.startswith("## "))
        h3_count = sum(1 for line in lines if line.startswith("### "))

        assert h2_count == 4, "Template should have exactly 4 h2 views"
        assert h3_count >= 11, "Template should have at least 11 h3 subsections"


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
            "solution-design-template.md",
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

    def test_solution_design_has_all_required_views(self, templates_dir):
        """Verify solution-design has all required views"""
        template_file = templates_dir / "solution-design-template.md"
        content = template_file.read_text()

        required_views = [
            "## Decomposition View",
            "## Dependency View",
            "## Interface View",
            "## Data Design View",
        ]

        for view in required_views:
            assert view in content, \
                f"solution-design-template.md missing required view: {view}"

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
