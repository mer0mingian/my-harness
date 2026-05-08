#!/usr/bin/env python3
"""Unit tests for commands/commit.md — S8-002 agent timeout config.

Verifies that commit.md Step 1 (Load Configuration) loads agent_timeout
from config with default: 30, and that Step 3 (Generate Workflow Summary)
includes a timeout instruction with the required elements.
"""

from pathlib import Path

import pytest

# Path to the command markdown file under test
COMMIT_MD = Path(__file__).parent.parent.parent / "commands" / "commit.md"


@pytest.fixture
def commit_md_content() -> str:
    """Load commit.md content once for all tests."""
    assert COMMIT_MD.exists(), f"commands/commit.md not found at {COMMIT_MD}"
    return COMMIT_MD.read_text()


class TestStep1LoadsAgentTimeout:
    """Step 1 (Load Configuration) must mention agent_timeout."""

    def test_step1_mentions_agent_timeout(self, commit_md_content):
        """Step 1 must list agent_timeout as a loaded config key."""
        assert "agent_timeout" in commit_md_content, (
            "commands/commit.md Step 1 must reference 'agent_timeout' as a "
            "config key loaded from .specify/harness-tdd-config.yml"
        )

    def test_step1_section_contains_agent_timeout(self, commit_md_content):
        """The Load Configuration section specifically must mention agent_timeout."""
        step1_start = commit_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in commit.md"

        # Find where Step 1 ends (next ## heading)
        step2_start = commit_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in commit.md"

        step1_content = commit_md_content[step1_start:step2_start]
        assert "agent_timeout" in step1_content, (
            "Step 1 (Load Configuration) section must reference 'agent_timeout'. "
            f"Step 1 content:\n{step1_content}"
        )

    def test_step1_agent_timeout_has_default_30(self, commit_md_content):
        """Step 1 must document default value of 30 for agent_timeout."""
        step1_start = commit_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in commit.md"

        step2_start = commit_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in commit.md"

        step1_content = commit_md_content[step1_start:step2_start]

        has_default_30 = (
            "agent_timeout" in step1_content
            and "30" in step1_content
            and ("default" in step1_content.lower() or "missing" in step1_content.lower())
        )
        assert has_default_30, (
            "commit.md Step 1 must document that agent_timeout defaults to 30 "
            "when the key is missing from config. "
            f"Step 1 content:\n{step1_content}"
        )


class TestStep3AgentTimeoutInstruction:
    """Step 3 (Generate Workflow Summary) must include timeout instruction."""

    def test_step3_section_contains_timeout_reference(self, commit_md_content):
        """Step 3 must include a timeout instruction."""
        step3_start = commit_md_content.find("## Step 3:")
        assert step3_start != -1, "Step 3 section not found in commit.md"

        # Find where Step 3 ends (next ## heading)
        step4_start = commit_md_content.find("## Step 4:", step3_start)
        assert step4_start != -1, "Step 4 section not found in commit.md"

        step3_content = commit_md_content[step3_start:step4_start]

        has_timeout = (
            "agent_timeout" in step3_content
            or "timeout" in step3_content.lower()
        )
        assert has_timeout, (
            "Step 3 (Generate Workflow Summary) must include a timeout instruction "
            "referencing the agent_timeout value. "
            f"Step 3 content:\n{step3_content}"
        )

    def test_step3_timeout_instructs_partial_results_on_timeout(self, commit_md_content):
        """Step 3 timeout instruction must tell agent to output partial results."""
        step3_start = commit_md_content.find("## Step 3:")
        assert step3_start != -1, "Step 3 section not found in commit.md"

        step4_start = commit_md_content.find("## Step 4:", step3_start)
        assert step4_start != -1, "Step 4 section not found in commit.md"

        step3_content = commit_md_content[step3_start:step4_start]

        has_partial = (
            "partial" in step3_content.lower()
            or "incomplete" in step3_content.lower()
        )
        assert has_partial, (
            "Step 3 timeout instruction must tell the agent to output partial results "
            "when timeout is reached. "
            f"Step 3 content:\n{step3_content}"
        )

    def test_step3_timeout_instructs_escalate_to_human(self, commit_md_content):
        """Step 3 timeout instruction must tell agent to escalate to human."""
        step3_start = commit_md_content.find("## Step 3:")
        assert step3_start != -1, "Step 3 section not found in commit.md"

        step4_start = commit_md_content.find("## Step 4:", step3_start)
        assert step4_start != -1, "Step 4 section not found in commit.md"

        step3_content = commit_md_content[step3_start:step4_start]

        has_escalate = (
            "escalate" in step3_content.lower()
            or "human" in step3_content.lower()
        )
        assert has_escalate, (
            "Step 3 timeout instruction must tell the agent to escalate to human "
            "when timeout is reached. "
            f"Step 3 content:\n{step3_content}"
        )
