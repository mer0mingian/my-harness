#!/usr/bin/env python3
"""Unit tests for commands/implement.md — S8-002 agent timeout config.

Verifies that implement.md Phase 1 Step 1 (Load Configuration) loads
agent_timeout from config with default: 30, and that Step 7 (Print Agent
Invocation Instructions) includes a timeout instruction with required elements.
"""

from pathlib import Path

import pytest

# Path to the command markdown file under test
IMPLEMENT_MD = Path(__file__).parent.parent.parent / "commands" / "implement.md"


@pytest.fixture
def implement_md_content() -> str:
    """Load implement.md content once for all tests."""
    assert IMPLEMENT_MD.exists(), f"commands/implement.md not found at {IMPLEMENT_MD}"
    return IMPLEMENT_MD.read_text()


class TestStep1LoadsAgentTimeout:
    """Step 1 (Load Configuration) in Phase 1 must mention agent_timeout."""

    def test_step1_mentions_agent_timeout(self, implement_md_content):
        """Step 1 must list agent_timeout as a loaded config key."""
        assert "agent_timeout" in implement_md_content, (
            "commands/implement.md Step 1 must reference 'agent_timeout' as a "
            "config key loaded from .specify/harness-tdd-config.yml"
        )

    def test_step1_section_contains_agent_timeout(self, implement_md_content):
        """The Phase 1 Step 1 Load Configuration section must mention agent_timeout."""
        # Find Phase 1 Step 1 section
        step1_start = implement_md_content.find("### Step 1: Load Configuration")
        assert step1_start != -1, "Phase 1 Step 1 (Load Configuration) section not found in implement.md"

        # Find where Step 1 ends (next ### heading)
        step2_start = implement_md_content.find("### Step 2:", step1_start)
        assert step2_start != -1, "Phase 1 Step 2 section not found in implement.md"

        step1_content = implement_md_content[step1_start:step2_start]
        assert "agent_timeout" in step1_content, (
            "Phase 1 Step 1 (Load Configuration) section must reference 'agent_timeout'. "
            f"Step 1 content:\n{step1_content}"
        )

    def test_step1_agent_timeout_has_default_30(self, implement_md_content):
        """Phase 1 Step 1 must document default value of 30 for agent_timeout."""
        step1_start = implement_md_content.find("### Step 1: Load Configuration")
        assert step1_start != -1, "Phase 1 Step 1 not found in implement.md"

        step2_start = implement_md_content.find("### Step 2:", step1_start)
        assert step2_start != -1, "Phase 1 Step 2 section not found in implement.md"

        step1_content = implement_md_content[step1_start:step2_start]

        has_default_30 = (
            "agent_timeout" in step1_content
            and "30" in step1_content
            and ("default" in step1_content.lower() or "missing" in step1_content.lower())
        )
        assert has_default_30, (
            "implement.md Phase 1 Step 1 must document that agent_timeout defaults to 30 "
            "when the key is missing from config. "
            f"Step 1 content:\n{step1_content}"
        )


class TestStep7AgentTimeoutInstruction:
    """Step 7 (Print Agent Invocation Instructions) must include timeout instruction."""

    def test_step7_section_contains_timeout_reference(self, implement_md_content):
        """Step 7 agent delegation must include a timeout instruction."""
        step7_start = implement_md_content.find("### Step 7:")
        assert step7_start != -1, "Phase 1 Step 7 section not found in implement.md"

        # Find where Step 7 ends (next heading or Phase 2 section)
        phase2_start = implement_md_content.find("## Phase 2", step7_start)
        next_heading = implement_md_content.find("### Step", step7_start + 1)

        # Use the closer boundary
        if phase2_start == -1:
            end = next_heading if next_heading != -1 else len(implement_md_content)
        elif next_heading == -1:
            end = phase2_start
        else:
            end = min(phase2_start, next_heading)

        step7_content = implement_md_content[step7_start:end]

        has_timeout = (
            "agent_timeout" in step7_content
            or "timeout" in step7_content.lower()
        )
        assert has_timeout, (
            "Step 7 (Print Agent Invocation Instructions) must include a timeout "
            "instruction referencing the agent_timeout value. "
            f"Step 7 content:\n{step7_content}"
        )

    def test_step7_timeout_instructs_partial_results_on_timeout(self, implement_md_content):
        """Step 7 timeout instruction must tell agent to output partial results."""
        step7_start = implement_md_content.find("### Step 7:")
        assert step7_start != -1, "Phase 1 Step 7 section not found in implement.md"

        phase2_start = implement_md_content.find("## Phase 2", step7_start)
        next_heading = implement_md_content.find("### Step", step7_start + 1)

        if phase2_start == -1:
            end = next_heading if next_heading != -1 else len(implement_md_content)
        elif next_heading == -1:
            end = phase2_start
        else:
            end = min(phase2_start, next_heading)

        step7_content = implement_md_content[step7_start:end]

        has_partial = (
            "partial" in step7_content.lower()
            or "incomplete" in step7_content.lower()
        )
        assert has_partial, (
            "Step 7 timeout instruction must tell the agent to output partial results "
            "when timeout is reached. "
            f"Step 7 content:\n{step7_content}"
        )

    def test_step7_timeout_instructs_escalate_to_human(self, implement_md_content):
        """Step 7 timeout instruction must tell agent to escalate to human."""
        step7_start = implement_md_content.find("### Step 7:")
        assert step7_start != -1, "Phase 1 Step 7 section not found in implement.md"

        phase2_start = implement_md_content.find("## Phase 2", step7_start)
        next_heading = implement_md_content.find("### Step", step7_start + 1)

        if phase2_start == -1:
            end = next_heading if next_heading != -1 else len(implement_md_content)
        elif next_heading == -1:
            end = phase2_start
        else:
            end = min(phase2_start, next_heading)

        step7_content = implement_md_content[step7_start:end]

        has_escalate = (
            "escalate" in step7_content.lower()
            or "human" in step7_content.lower()
        )
        assert has_escalate, (
            "Step 7 timeout instruction must tell the agent to escalate to human "
            "when timeout is reached. "
            f"Step 7 content:\n{step7_content}"
        )
