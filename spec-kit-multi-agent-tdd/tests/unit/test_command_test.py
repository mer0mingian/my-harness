#!/usr/bin/env python3
"""Unit tests for commands/test.md — S8-002 agent timeout config.

Verifies that test.md Step 3 (Load Configuration) loads agent_timeout
from config with default: 30, and that the agent invocation step (Step 5)
includes a timeout instruction with the required elements.
"""

from pathlib import Path

import pytest

# Path to the command markdown file under test
TEST_MD = Path(__file__).parent.parent.parent / "commands" / "test.md"


@pytest.fixture
def test_md_content() -> str:
    """Load test.md content once for all tests."""
    assert TEST_MD.exists(), f"commands/test.md not found at {TEST_MD}"
    return TEST_MD.read_text()


class TestStep3LoadsAgentTimeout:
    """Step 3 (Load Configuration) must mention agent_timeout."""

    def test_step3_mentions_agent_timeout(self, test_md_content):
        """Step 3 must list agent_timeout as a loaded config key."""
        assert "agent_timeout" in test_md_content, (
            "commands/test.md Step 3 must reference 'agent_timeout' as a "
            "config key loaded from .specify/harness-tdd-config.yml"
        )

    def test_step3_section_contains_agent_timeout(self, test_md_content):
        """The Load Configuration section specifically must mention agent_timeout."""
        step3_start = test_md_content.find("## Step 3:")
        assert step3_start != -1, "Step 3 section not found in test.md"

        # Find where Step 3 ends (next ## heading)
        step4_start = test_md_content.find("## Step 4:", step3_start)
        assert step4_start != -1, "Step 4 section not found in test.md"

        step3_content = test_md_content[step3_start:step4_start]
        assert "agent_timeout" in step3_content, (
            "Step 3 (Load Configuration) section must reference 'agent_timeout'. "
            f"Step 3 content:\n{step3_content}"
        )

    def test_step3_agent_timeout_has_default_30(self, test_md_content):
        """Step 3 must document default value of 30 for agent_timeout."""
        step3_start = test_md_content.find("## Step 3:")
        assert step3_start != -1, "Step 3 section not found in test.md"

        step4_start = test_md_content.find("## Step 4:", step3_start)
        assert step4_start != -1, "Step 4 section not found in test.md"

        step3_content = test_md_content[step3_start:step4_start]

        has_default_30 = (
            "agent_timeout" in step3_content
            and "30" in step3_content
            and ("default" in step3_content.lower() or "missing" in step3_content.lower())
        )
        assert has_default_30, (
            "test.md Step 3 must document that agent_timeout defaults to 30 "
            "when the key is missing from config. "
            f"Step 3 content:\n{step3_content}"
        )


class TestStep5AgentTimeoutInstruction:
    """Step 5 (Spawn Test Agent) must include timeout instruction."""

    def test_step5_section_contains_timeout_value(self, test_md_content):
        """Step 5 agent delegation must include the timeout value reference."""
        step5_start = test_md_content.find("## Step 5:")
        assert step5_start != -1, "Step 5 section not found in test.md"

        # Find where Step 5 ends (next ## heading)
        step6_start = test_md_content.find("## Step 6:", step5_start)
        assert step6_start != -1, "Step 6 section not found in test.md"

        step5_content = test_md_content[step5_start:step6_start]
        has_timeout = (
            "agent_timeout" in step5_content
            or "timeout" in step5_content.lower()
        )
        assert has_timeout, (
            "Step 5 (Spawn Test Agent) must include a timeout instruction "
            "referencing the agent_timeout value. "
            f"Step 5 content:\n{step5_content}"
        )

    def test_step5_timeout_instructs_partial_results_on_timeout(self, test_md_content):
        """Step 5 timeout instruction must tell agent to output partial results."""
        step5_start = test_md_content.find("## Step 5:")
        assert step5_start != -1, "Step 5 section not found in test.md"

        step6_start = test_md_content.find("## Step 6:", step5_start)
        assert step6_start != -1, "Step 6 section not found in test.md"

        step5_content = test_md_content[step5_start:step6_start]

        has_partial = (
            "partial" in step5_content.lower()
            or "incomplete" in step5_content.lower()
            or "partial results" in step5_content.lower()
        )
        assert has_partial, (
            "Step 5 timeout instruction must tell the agent to output partial results "
            "when timeout is reached. "
            f"Step 5 content:\n{step5_content}"
        )

    def test_step5_timeout_instructs_escalate_to_human(self, test_md_content):
        """Step 5 timeout instruction must tell agent to escalate to human."""
        step5_start = test_md_content.find("## Step 5:")
        assert step5_start != -1, "Step 5 section not found in test.md"

        step6_start = test_md_content.find("## Step 6:", step5_start)
        assert step6_start != -1, "Step 6 section not found in test.md"

        step5_content = test_md_content[step5_start:step6_start]

        has_escalate = (
            "escalate" in step5_content.lower()
            or "human" in step5_content.lower()
        )
        assert has_escalate, (
            "Step 5 timeout instruction must tell the agent to escalate to human "
            "when timeout is reached. "
            f"Step 5 content:\n{step5_content}"
        )
