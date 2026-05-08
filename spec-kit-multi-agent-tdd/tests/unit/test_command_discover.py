#!/usr/bin/env python3
"""Unit tests for commands/discover.md — S7c Discovery phase command.

Verifies that discover.md has valid YAML frontmatter, all required steps,
correct skill references, template references, and exit codes as specified
by S7c.
"""

from pathlib import Path

import pytest
import yaml

# Path to the command markdown file under test
DISCOVER_MD = Path(__file__).parent.parent.parent / "commands" / "discover.md"


@pytest.fixture
def discover_md_content() -> str:
    """Load discover.md content once for all tests."""
    assert DISCOVER_MD.exists(), f"commands/discover.md not found at {DISCOVER_MD}"
    return DISCOVER_MD.read_text()


@pytest.fixture
def discover_md_frontmatter(discover_md_content: str) -> dict:
    """Parse and return the YAML frontmatter from discover.md."""
    assert discover_md_content.startswith("---"), (
        "commands/discover.md must start with YAML frontmatter delimited by '---'"
    )
    end = discover_md_content.find("---", 3)
    assert end != -1, "YAML frontmatter closing '---' not found in discover.md"
    raw_yaml = discover_md_content[3:end].strip()
    return yaml.safe_load(raw_yaml)


# ---------------------------------------------------------------------------
# Frontmatter tests
# ---------------------------------------------------------------------------

class TestFrontmatterValid:
    """YAML frontmatter must be present and parseable."""

    def test_frontmatter_is_valid_yaml(self, discover_md_frontmatter):
        """Frontmatter must parse as valid YAML."""
        assert isinstance(discover_md_frontmatter, dict), (
            "commands/discover.md frontmatter must be a valid YAML mapping"
        )

    def test_description_field_present(self, discover_md_frontmatter):
        """Frontmatter must contain a 'description' field."""
        assert "description" in discover_md_frontmatter, (
            "commands/discover.md frontmatter must contain 'description'"
        )
        assert discover_md_frontmatter["description"], (
            "commands/discover.md 'description' must not be empty"
        )

    def test_description_mentions_discovery(self, discover_md_frontmatter):
        """Description must mention Discovery phase or PRD."""
        desc = discover_md_frontmatter["description"].lower()
        assert "discovery" in desc or "prd" in desc, (
            "commands/discover.md 'description' must mention 'Discovery' or 'PRD'. "
            f"Got: {discover_md_frontmatter['description']}"
        )

    def test_skills_field_present(self, discover_md_frontmatter):
        """Frontmatter must contain a 'skills' list."""
        assert "skills" in discover_md_frontmatter, (
            "commands/discover.md frontmatter must contain 'skills'"
        )
        assert isinstance(discover_md_frontmatter["skills"], list), (
            "commands/discover.md 'skills' must be a list"
        )

    def test_general_grill_with_docs_skill_listed(self, discover_md_frontmatter):
        """'general-grill-with-docs' skill must be listed in frontmatter skills."""
        skills = discover_md_frontmatter.get("skills", [])
        assert "general-grill-with-docs" in skills, (
            "commands/discover.md must list 'general-grill-with-docs' in skills. "
            f"Found skills: {skills}"
        )

    def test_tools_field_present(self, discover_md_frontmatter):
        """Frontmatter must contain a 'tools' list."""
        assert "tools" in discover_md_frontmatter, (
            "commands/discover.md frontmatter must contain 'tools'"
        )

    def test_filesystem_read_tool_listed(self, discover_md_frontmatter):
        """'filesystem/read' tool must be listed."""
        tools = discover_md_frontmatter.get("tools", [])
        assert "filesystem/read" in tools, (
            f"'filesystem/read' must be in tools. Found: {tools}"
        )

    def test_filesystem_write_tool_listed(self, discover_md_frontmatter):
        """'filesystem/write' tool must be listed."""
        tools = discover_md_frontmatter.get("tools", [])
        assert "filesystem/write" in tools, (
            f"'filesystem/write' must be in tools. Found: {tools}"
        )

    def test_templates_field_present(self, discover_md_frontmatter):
        """Frontmatter must contain a 'templates' mapping."""
        assert "templates" in discover_md_frontmatter, (
            "commands/discover.md frontmatter must contain 'templates'"
        )
        assert isinstance(discover_md_frontmatter["templates"], dict), (
            "commands/discover.md 'templates' must be a YAML mapping"
        )

    def test_templates_prd_key_present(self, discover_md_frontmatter):
        """Templates must include 'prd' key pointing to prd-template.md."""
        templates = discover_md_frontmatter.get("templates", {})
        assert "prd" in templates, (
            f"'templates.prd' must be present. Found keys: {list(templates.keys())}"
        )
        assert "prd-template.md" in templates["prd"], (
            f"templates.prd must reference prd-template.md. Got: {templates['prd']}"
        )

    def test_templates_constitution_key_present(self, discover_md_frontmatter):
        """Templates must include 'constitution' key pointing to system-constitution-template.md."""
        templates = discover_md_frontmatter.get("templates", {})
        assert "constitution" in templates, (
            f"'templates.constitution' must be present. Found keys: {list(templates.keys())}"
        )
        assert "system-constitution-template.md" in templates["constitution"], (
            f"templates.constitution must reference system-constitution-template.md. "
            f"Got: {templates['constitution']}"
        )

    def test_exit_codes_field_present(self, discover_md_frontmatter):
        """Frontmatter must contain 'exit_codes' mapping."""
        assert "exit_codes" in discover_md_frontmatter, (
            "commands/discover.md frontmatter must contain 'exit_codes'"
        )

    def test_exit_code_0_present(self, discover_md_frontmatter):
        """Exit code 0 (Success) must be documented in frontmatter."""
        exit_codes = discover_md_frontmatter.get("exit_codes", {})
        assert 0 in exit_codes, (
            f"exit_codes must include 0 (Success). Found keys: {list(exit_codes.keys())}"
        )

    def test_exit_code_1_present(self, discover_md_frontmatter):
        """Exit code 1 (Validation failure) must be documented in frontmatter."""
        exit_codes = discover_md_frontmatter.get("exit_codes", {})
        assert 1 in exit_codes, (
            f"exit_codes must include 1 (Validation failure). Found keys: {list(exit_codes.keys())}"
        )

    def test_exit_code_2_present(self, discover_md_frontmatter):
        """Exit code 2 (Escalation required) must be documented in frontmatter."""
        exit_codes = discover_md_frontmatter.get("exit_codes", {})
        assert 2 in exit_codes, (
            f"exit_codes must include 2 (Escalation required). Found keys: {list(exit_codes.keys())}"
        )


# ---------------------------------------------------------------------------
# Step heading presence tests
# ---------------------------------------------------------------------------

class TestStepHeadingsPresent:
    """All 10 steps must be present as '## Step N:' headings."""

    @pytest.mark.parametrize("step_num", range(1, 11))
    def test_step_heading_present(self, discover_md_content, step_num):
        """Each step N (1-10) must have a '## Step N:' heading."""
        heading = f"## Step {step_num}:"
        assert heading in discover_md_content, (
            f"commands/discover.md must contain heading '{heading}'"
        )


# ---------------------------------------------------------------------------
# Step 1 — Load Configuration
# ---------------------------------------------------------------------------

class TestStep1LoadConfiguration:
    """Step 1 must reference config loading with correct keys and defaults."""

    def _step1_content(self, full_content: str) -> str:
        start = full_content.find("## Step 1:")
        assert start != -1, "## Step 1: not found in discover.md"
        end = full_content.find("## Step 2:", start)
        assert end != -1, "## Step 2: not found after Step 1 in discover.md"
        return full_content[start:end]

    def test_step1_references_config_file(self, discover_md_content):
        """Step 1 must reference .specify/harness-tdd-config.yml."""
        content = self._step1_content(discover_md_content)
        assert "harness-tdd-config.yml" in content, (
            "Step 1 must reference '.specify/harness-tdd-config.yml'"
        )

    def test_step1_references_artifacts_root(self, discover_md_content):
        """Step 1 must mention artifacts.root config key."""
        content = self._step1_content(discover_md_content)
        assert "artifacts.root" in content or "artifacts_root" in content or "artifacts" in content, (
            "Step 1 must reference the artifacts.root config key"
        )

    def test_step1_references_agent_timeout(self, discover_md_content):
        """Step 1 must mention agent_timeout."""
        content = self._step1_content(discover_md_content)
        assert "agent_timeout" in content, (
            "Step 1 must reference 'agent_timeout' config key with default 30"
        )

    def test_step1_agent_timeout_default_30(self, discover_md_content):
        """Step 1 must document agent_timeout default of 30."""
        content = self._step1_content(discover_md_content)
        assert "agent_timeout" in content and "30" in content, (
            "Step 1 must document that agent_timeout defaults to 30"
        )


# ---------------------------------------------------------------------------
# Step 2 — Validate Inputs
# ---------------------------------------------------------------------------

class TestStep2ValidateInputs:
    """Step 2 must validate feature_id from $ARGUMENTS."""

    def _step2_content(self, full_content: str) -> str:
        start = full_content.find("## Step 2:")
        assert start != -1, "## Step 2: not found in discover.md"
        end = full_content.find("## Step 3:", start)
        assert end != -1, "## Step 3: not found after Step 2 in discover.md"
        return full_content[start:end]

    def test_step2_handles_empty_arguments(self, discover_md_content):
        """Step 2 must describe exit when $ARGUMENTS is empty."""
        content = self._step2_content(discover_md_content)
        assert "empty" in content.lower() or "ARGUMENTS" in content, (
            "Step 2 must handle empty $ARGUMENTS case"
        )

    def test_step2_exit_code_1_on_no_feature_id(self, discover_md_content):
        """Step 2 must specify Exit 1 when no feature_id provided."""
        content = self._step2_content(discover_md_content)
        assert "Exit 1" in content or "exit 1" in content.lower(), (
            "Step 2 must specify Exit 1 when feature_id is not provided"
        )

    def test_step2_sets_feature_id(self, discover_md_content):
        """Step 2 must set feature_id from $ARGUMENTS."""
        content = self._step2_content(discover_md_content)
        assert "feature_id" in content, (
            "Step 2 must set 'feature_id' from $ARGUMENTS"
        )


# ---------------------------------------------------------------------------
# Step 3 — Check Existing Artifacts
# ---------------------------------------------------------------------------

class TestStep3CheckExistingArtifacts:
    """Step 3 must handle existing PRD (mention + proceed) and existing constitution (silent load)."""

    def _step3_content(self, full_content: str) -> str:
        start = full_content.find("## Step 3:")
        assert start != -1, "## Step 3: not found in discover.md"
        end = full_content.find("## Step 4:", start)
        assert end != -1, "## Step 4: not found after Step 3 in discover.md"
        return full_content[start:end]

    def test_step3_searches_for_existing_prd(self, discover_md_content):
        """Step 3 must search for an existing PRD file."""
        content = self._step3_content(discover_md_content)
        assert "prd" in content.lower(), (
            "Step 3 must search for existing PRD"
        )

    def test_step3_mentions_prd_if_found(self, discover_md_content):
        """Step 3 must mention the PRD to the user if it already exists."""
        content = self._step3_content(discover_md_content)
        # Must contain logic for notifying user about existing PRD
        has_mention = (
            "mention" in content.lower()
            or "already exists" in content.lower()
            or "will merge" in content.lower()
        )
        assert has_mention, (
            "Step 3 must mention existing PRD to user ('already exists', 'will merge', etc.)"
        )

    def test_step3_proceeds_after_existing_prd(self, discover_md_content):
        """Step 3 must proceed (not abort) when PRD exists."""
        content = self._step3_content(discover_md_content)
        assert "proceed" in content.lower() or "continue" in content.lower(), (
            "Step 3 must say 'proceed' or 'continue' after finding an existing PRD"
        )

    def test_step3_searches_for_existing_constitution(self, discover_md_content):
        """Step 3 must search for an existing System Constitution."""
        content = self._step3_content(discover_md_content)
        assert "constitution" in content.lower(), (
            "Step 3 must search for existing System Constitution"
        )

    def test_step3_loads_constitution_silently(self, discover_md_content):
        """Step 3 must load existing constitution silently (no warning)."""
        content = self._step3_content(discover_md_content)
        assert "silent" in content.lower() or "no warning" in content.lower(), (
            "Step 3 must load existing constitution silently (without warning)"
        )


# ---------------------------------------------------------------------------
# Step 4 — Load Context
# ---------------------------------------------------------------------------

class TestStep4LoadContext:
    """Step 4 must load spec artifact and prior artifacts for merge context."""

    def _step4_content(self, full_content: str) -> str:
        start = full_content.find("## Step 4:")
        assert start != -1, "## Step 4: not found in discover.md"
        end = full_content.find("## Step 5:", start)
        assert end != -1, "## Step 5: not found after Step 4 in discover.md"
        return full_content[start:end]

    def test_step4_loads_spec_artifact(self, discover_md_content):
        """Step 4 must load the spec artifact."""
        content = self._step4_content(discover_md_content)
        assert "spec" in content.lower(), (
            "Step 4 must load spec artifact"
        )


# ---------------------------------------------------------------------------
# Step 5 — Grill-Me Session
# ---------------------------------------------------------------------------

class TestStep5GrillMeSession:
    """Step 5 must use general-grill-with-docs skill and cover PRD sections."""

    def _step5_content(self, full_content: str) -> str:
        start = full_content.find("## Step 5:")
        assert start != -1, "## Step 5: not found in discover.md"
        end = full_content.find("## Step 6:", start)
        assert end != -1, "## Step 6: not found after Step 5 in discover.md"
        return full_content[start:end]

    def test_step5_references_grill_with_docs_skill(self, discover_md_content):
        """Step 5 must explicitly reference the general-grill-with-docs skill."""
        content = self._step5_content(discover_md_content)
        assert "general-grill-with-docs" in content, (
            "Step 5 must reference the 'general-grill-with-docs' skill"
        )

    def test_step5_questions_one_at_a_time(self, discover_md_content):
        """Step 5 must instruct asking questions one at a time."""
        content = self._step5_content(discover_md_content)
        assert "one at a time" in content.lower() or "one question" in content.lower(), (
            "Step 5 must instruct asking questions one at a time"
        )

    def test_step5_covers_prd_sections(self, discover_md_content):
        """Step 5 must mention PRD section coverage."""
        content = self._step5_content(discover_md_content)
        # At least some PRD section names must appear
        prd_sections = ["Business Value", "Goals", "Risks", "Dependencies", "Metrics"]
        found = [s for s in prd_sections if s in content]
        assert len(found) >= 3, (
            f"Step 5 must cover PRD sections. Found only: {found} from expected: {prd_sections}"
        )

    def test_step5_allows_deferring_unknowns(self, discover_md_content):
        """Step 5 must allow user to defer unknown questions."""
        content = self._step5_content(discover_md_content)
        assert "defer" in content.lower() or "open question" in content.lower(), (
            "Step 5 must allow user to defer unknown answers as open questions"
        )

    def test_step5_reaches_consensus(self, discover_md_content):
        """Step 5 must aim for consensus."""
        content = self._step5_content(discover_md_content)
        assert "consensus" in content.lower(), (
            "Step 5 must mention reaching consensus"
        )

    def test_step5_extracts_for_constitution(self, discover_md_content):
        """Step 5 must extract tech constraints/NFRs for the System Constitution."""
        content = self._step5_content(discover_md_content)
        has_constitution_extraction = (
            "constitution" in content.lower()
            or "nfr" in content.lower()
            or "tech constraint" in content.lower()
            or "non-functional" in content.lower()
        )
        assert has_constitution_extraction, (
            "Step 5 must extract tech constraints or NFRs for the System Constitution"
        )


# ---------------------------------------------------------------------------
# Step 6 — Generate/Update PRD
# ---------------------------------------------------------------------------

class TestStep6GeneratePRD:
    """Step 6 must use prd-template.md and save to artifacts.root."""

    def _step6_content(self, full_content: str) -> str:
        start = full_content.find("## Step 6:")
        assert start != -1, "## Step 6: not found in discover.md"
        end = full_content.find("## Step 7:", start)
        assert end != -1, "## Step 7: not found after Step 6 in discover.md"
        return full_content[start:end]

    def test_step6_references_prd_template(self, discover_md_content):
        """Step 6 must reference prd-template.md."""
        content = self._step6_content(discover_md_content)
        assert "prd-template.md" in content, (
            "Step 6 must reference 'prd-template.md'"
        )

    def test_step6_saves_prd_artifact(self, discover_md_content):
        """Step 6 must save the PRD artifact."""
        content = self._step6_content(discover_md_content)
        assert "save" in content.lower() or "write" in content.lower(), (
            "Step 6 must save/write the PRD artifact"
        )

    def test_step6_merges_when_prd_exists(self, discover_md_content):
        """Step 6 must merge into existing PRD rather than overwriting."""
        content = self._step6_content(discover_md_content)
        assert "merge" in content.lower() or "not overwrite" in content.lower() or "do not overwrite" in content.lower(), (
            "Step 6 must merge new information when an existing PRD is found"
        )

    def test_step6_prd_path_includes_feature_id(self, discover_md_content):
        """Step 6 must reference a PRD path pattern including feature_id."""
        content = self._step6_content(discover_md_content)
        assert "feature_id" in content or "{feature_id}" in content or "feature_id}-prd" in content, (
            "Step 6 must reference a path pattern containing feature_id for the PRD output"
        )


# ---------------------------------------------------------------------------
# Step 7 — Generate/Update System Constitution
# ---------------------------------------------------------------------------

class TestStep7GenerateConstitution:
    """Step 7 must use system-constitution-template.md and handle existing files."""

    def _step7_content(self, full_content: str) -> str:
        start = full_content.find("## Step 7:")
        assert start != -1, "## Step 7: not found in discover.md"
        end = full_content.find("## Step 8:", start)
        assert end != -1, "## Step 8: not found after Step 7 in discover.md"
        return full_content[start:end]

    def test_step7_references_constitution_template(self, discover_md_content):
        """Step 7 must reference system-constitution-template.md."""
        content = self._step7_content(discover_md_content)
        assert "system-constitution-template.md" in content, (
            "Step 7 must reference 'system-constitution-template.md'"
        )

    def test_step7_merges_when_constitution_exists(self, discover_md_content):
        """Step 7 must merge into existing constitution silently."""
        content = self._step7_content(discover_md_content)
        assert "merge" in content.lower() or "existing" in content.lower(), (
            "Step 7 must merge into existing constitution when found"
        )

    def test_step7_saves_constitution(self, discover_md_content):
        """Step 7 must save the System Constitution artifact."""
        content = self._step7_content(discover_md_content)
        assert "save" in content.lower() or "write" in content.lower(), (
            "Step 7 must save/write the System Constitution artifact"
        )


# ---------------------------------------------------------------------------
# Step 8 — Save Open Questions
# ---------------------------------------------------------------------------

class TestStep8SaveOpenQuestions:
    """Step 8 must save deferred questions to an open-questions file."""

    def _step8_content(self, full_content: str) -> str:
        start = full_content.find("## Step 8:")
        assert start != -1, "## Step 8: not found in discover.md"
        end = full_content.find("## Step 9:", start)
        assert end != -1, "## Step 9: not found after Step 8 in discover.md"
        return full_content[start:end]

    def test_step8_mentions_open_questions(self, discover_md_content):
        """Step 8 must mention open-questions file."""
        content = self._step8_content(discover_md_content)
        assert "open-questions" in content.lower() or "open questions" in content.lower(), (
            "Step 8 must mention saving open questions"
        )

    def test_step8_skips_when_no_open_questions(self, discover_md_content):
        """Step 8 must skip file creation when no open questions exist."""
        content = self._step8_content(discover_md_content)
        assert "skip" in content.lower() or "no open" in content.lower() or "if no" in content.lower(), (
            "Step 8 must skip open-questions file creation when there are none"
        )

    def test_step8_saves_to_artifacts_root(self, discover_md_content):
        """Step 8 must save open-questions to the artifacts root path."""
        content = self._step8_content(discover_md_content)
        assert "feature_id" in content or "artifacts" in content, (
            "Step 8 must reference a path that includes feature_id or artifacts root"
        )


# ---------------------------------------------------------------------------
# Step 9 — Validate Artifacts
# ---------------------------------------------------------------------------

class TestStep9ValidateArtifacts:
    """Step 9 must call validate_artifact_structure.py post-generation."""

    def _step9_content(self, full_content: str) -> str:
        start = full_content.find("## Step 9:")
        assert start != -1, "## Step 9: not found in discover.md"
        end = full_content.find("## Step 10:", start)
        assert end != -1, "## Step 10: not found after Step 9 in discover.md"
        return full_content[start:end]

    def test_step9_calls_validate_artifact_structure(self, discover_md_content):
        """Step 9 must reference validate_artifact_structure.py."""
        content = self._step9_content(discover_md_content)
        assert "validate_artifact_structure.py" in content, (
            "Step 9 must call 'scripts/validate_artifact_structure.py'"
        )

    def test_step9_is_post_generation_only(self, discover_md_content):
        """Step 9 must indicate it runs post-generation (warn only, not block)."""
        content = self._step9_content(discover_md_content)
        has_nonblocking = (
            "post-generation" in content.lower()
            or "warn" in content.lower()
            or "do not block" in content.lower()
        )
        assert has_nonblocking, (
            "Step 9 must be post-generation only and warn on issues without blocking"
        )

    def test_step9_escalates_on_issues(self, discover_md_content):
        """Step 9 must escalate to human if validation finds issues."""
        content = self._step9_content(discover_md_content)
        assert "escalate" in content.lower() or "human" in content.lower(), (
            "Step 9 must escalate to human with diagnostics if validation finds issues"
        )


# ---------------------------------------------------------------------------
# Step 10 — Report
# ---------------------------------------------------------------------------

class TestStep10Report:
    """Step 10 must report results and suggest next step."""

    def _step10_content(self, full_content: str) -> str:
        start = full_content.find("## Step 10:")
        assert start != -1, "## Step 10: not found in discover.md"
        # Step 10 is the last step; read to Exit Codes section or end
        end = full_content.find("## Exit Codes", start)
        if end == -1:
            end = len(full_content)
        return full_content[start:end]

    def test_step10_shows_prd_created(self, discover_md_content):
        """Step 10 must report PRD created/updated."""
        content = self._step10_content(discover_md_content)
        assert "prd" in content.lower() or "PRD" in content, (
            "Step 10 must report PRD created/updated"
        )

    def test_step10_shows_constitution_created(self, discover_md_content):
        """Step 10 must report System Constitution created/updated."""
        content = self._step10_content(discover_md_content)
        assert "constitution" in content.lower(), (
            "Step 10 must report System Constitution created/updated"
        )

    def test_step10_suggests_next_step(self, discover_md_content):
        """Step 10 must suggest the next command to run."""
        content = self._step10_content(discover_md_content)
        assert "solution-design" in content.lower() or "next step" in content.lower(), (
            "Step 10 must suggest next step (solution-design or similar)"
        )


# ---------------------------------------------------------------------------
# Exit codes in body
# ---------------------------------------------------------------------------

class TestExitCodesInBody:
    """Exit codes 0, 1, 2 must be documented in the command body."""

    def test_exit_code_0_documented_in_body(self, discover_md_content):
        """Exit code 0 (Success) must be documented in body."""
        # Look in the Exit Codes section of the body
        assert "0: Success" in discover_md_content or "**0**" in discover_md_content or "exit code 0" in discover_md_content.lower(), (
            "Exit code 0 (Success) must be documented in the command body"
        )

    def test_exit_code_1_documented_in_body(self, discover_md_content):
        """Exit code 1 (Validation failure) must be documented in body."""
        assert "1: Validation" in discover_md_content or "**1**" in discover_md_content or "exit 1" in discover_md_content.lower() or "Exit 1" in discover_md_content, (
            "Exit code 1 (Validation failure) must be documented in the command body"
        )

    def test_exit_code_2_documented_in_body(self, discover_md_content):
        """Exit code 2 (Escalation required) must be documented in body."""
        assert "2: Escalation" in discover_md_content or "**2**" in discover_md_content or "exit 2" in discover_md_content.lower() or "Exit 2" in discover_md_content, (
            "Exit code 2 (Escalation required) must be documented in the command body"
        )
