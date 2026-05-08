#!/usr/bin/env python3
"""Unit tests for commands/solution-design.md — S7d YAML frontmatter validation.

Validates machine-readable metadata in the frontmatter:
- YAML is parseable
- All three required c4-* agents are declared
"""

from pathlib import Path

import yaml
import pytest

SOLUTION_DESIGN_MD = (
    Path(__file__).parent.parent.parent / "commands" / "solution-design.md"
)


def _parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter delimited by '---'."""
    lines = content.splitlines()
    if lines[0].strip() != "---":
        raise ValueError("No opening '---' found in frontmatter")
    end = next(
        (i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if end is None:
        raise ValueError("No closing '---' found in frontmatter")
    yaml_block = "\n".join(lines[1:end])
    return yaml.safe_load(yaml_block)


@pytest.fixture(scope="module")
def solution_design_frontmatter() -> dict:
    """Load and parse frontmatter from solution-design.md once for all tests."""
    assert SOLUTION_DESIGN_MD.exists(), (
        f"commands/solution-design.md not found at {SOLUTION_DESIGN_MD}"
    )
    content = SOLUTION_DESIGN_MD.read_text()
    return _parse_frontmatter(content)


class TestFrontmatterParseable:
    """YAML frontmatter must be valid and parseable."""

    def test_frontmatter_is_valid_yaml(self, solution_design_frontmatter):
        """Frontmatter must parse without error and return a dict."""
        assert isinstance(solution_design_frontmatter, dict), (
            "Parsed frontmatter must be a dict, got: "
            f"{type(solution_design_frontmatter)}"
        )

    def test_frontmatter_has_description(self, solution_design_frontmatter):
        """Frontmatter must contain a non-empty 'description' field."""
        assert "description" in solution_design_frontmatter, (
            "Frontmatter must have a 'description' field"
        )
        assert solution_design_frontmatter["description"], (
            "Frontmatter 'description' must not be empty"
        )


class TestRequiredAgentsDeclared:
    """All three c4-* agents must be declared in the frontmatter 'agents' list."""

    REQUIRED_AGENTS = ["c4-context", "c4-container", "c4-component"]

    def test_agents_field_present(self, solution_design_frontmatter):
        """Frontmatter must have an 'agents' list."""
        assert "agents" in solution_design_frontmatter, (
            "Frontmatter must declare an 'agents' field"
        )
        assert isinstance(solution_design_frontmatter["agents"], list), (
            "Frontmatter 'agents' must be a list"
        )

    @pytest.mark.parametrize("agent", REQUIRED_AGENTS)
    def test_required_agent_declared(self, agent, solution_design_frontmatter):
        """Each required c4-* agent must appear in the 'agents' list."""
        declared = solution_design_frontmatter.get("agents", [])
        assert agent in declared, (
            f"Agent '{agent}' must be declared in frontmatter 'agents' list. "
            f"Currently declared: {declared}"
        )
