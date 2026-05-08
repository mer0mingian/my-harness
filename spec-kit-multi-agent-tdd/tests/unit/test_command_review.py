#!/usr/bin/env python3
"""Unit tests for commands/review.md — S8-001 config-driven parallel/sequential dispatch.

Verifies that review.md Step 1 loads parallel_enabled from config and
Step 7 has conditional branching for both parallel_enabled: true and
parallel_enabled: false execution paths.
"""

from pathlib import Path

import pytest

# Path to the command markdown file under test
REVIEW_MD = Path(__file__).parent.parent.parent / "commands" / "review.md"


@pytest.fixture
def review_md_content() -> str:
    """Load review.md content once for all tests."""
    assert REVIEW_MD.exists(), f"commands/review.md not found at {REVIEW_MD}"
    return REVIEW_MD.read_text()


class TestStep1LoadsParallelEnabled:
    """Step 1 (Load Configuration) must mention parallel_enabled."""

    def test_step1_mentions_parallel_enabled(self, review_md_content):
        """Step 1 must list parallel_enabled as a loaded config key."""
        assert "parallel_enabled" in review_md_content, (
            "commands/review.md Step 1 must reference 'parallel_enabled' as a "
            "config key loaded from .specify/harness-tdd-config.yml"
        )

    def test_step1_section_contains_parallel_enabled(self, review_md_content):
        """The Load Configuration section specifically must mention parallel_enabled."""
        # Find Step 1 section
        step1_start = review_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in review.md"

        # Find where Step 1 ends (next ## heading)
        step2_start = review_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in review.md"

        step1_content = review_md_content[step1_start:step2_start]
        assert "parallel_enabled" in step1_content, (
            "Step 1 (Load Configuration) section must reference 'parallel_enabled'. "
            f"Step 1 content:\n{step1_content}"
        )


class TestStep7ConditionalBranching:
    """Step 7 (Invoke Parallel Reviewers) must describe conditional dispatch."""

    def test_step7_has_parallel_enabled_true_branch(self, review_md_content):
        """Step 7 must describe behavior when parallel_enabled: true."""
        assert "parallel_enabled: true" in review_md_content, (
            "commands/review.md Step 7 must contain 'parallel_enabled: true' branch "
            "instructing both @check and @simplify to run simultaneously"
        )

    def test_step7_has_parallel_enabled_false_branch(self, review_md_content):
        """Step 7 must describe behavior when parallel_enabled: false."""
        assert "parallel_enabled: false" in review_md_content, (
            "commands/review.md Step 7 must contain 'parallel_enabled: false' branch "
            "instructing @check to run first, then @simplify sequentially"
        )

    def test_step7_section_contains_both_branches(self, review_md_content):
        """The Invoke Reviewers section must contain both conditional paths."""
        step7_start = review_md_content.find("## Step 7:")
        assert step7_start != -1, "Step 7 section not found in review.md"

        # Find where Step 7 ends (next ## heading)
        step8_start = review_md_content.find("## Step 8:", step7_start)
        assert step8_start != -1, "Step 8 section not found in review.md"

        step7_content = review_md_content[step7_start:step8_start]

        assert "parallel_enabled: true" in step7_content, (
            "Step 7 must contain 'parallel_enabled: true' conditional branch. "
            f"Step 7 content:\n{step7_content}"
        )
        assert "parallel_enabled: false" in step7_content, (
            "Step 7 must contain 'parallel_enabled: false' conditional branch. "
            f"Step 7 content:\n{step7_content}"
        )

    def test_step7_parallel_true_describes_simultaneous_execution(self, review_md_content):
        """parallel_enabled: true branch must describe simultaneous agent execution."""
        step7_start = review_md_content.find("## Step 7:")
        step8_start = review_md_content.find("## Step 8:", step7_start)
        step7_content = review_md_content[step7_start:step8_start]

        # Must mention simultaneous/parallel execution concept near the true branch
        has_simultaneous = (
            "simultaneously" in step7_content
            or "parallel" in step7_content.lower()
            or "at the same time" in step7_content
        )
        assert has_simultaneous, (
            "Step 7 parallel_enabled: true branch must describe simultaneous execution "
            "(e.g., 'simultaneously', 'parallel', 'at the same time')"
        )

    def test_step7_parallel_false_describes_sequential_execution(self, review_md_content):
        """parallel_enabled: false branch must describe sequential agent execution."""
        step7_start = review_md_content.find("## Step 7:")
        step8_start = review_md_content.find("## Step 8:", step7_start)
        step7_content = review_md_content[step7_start:step8_start]

        has_sequential = (
            "sequential" in step7_content.lower()
            or "then @simplify" in step7_content
            or "first" in step7_content
        )
        assert has_sequential, (
            "Step 7 parallel_enabled: false branch must describe sequential execution "
            "(e.g., 'sequentially', '@check first, then @simplify')"
        )

    def test_step7_default_is_false_when_key_missing(self, review_md_content):
        """Step 1 must document that default is false when key missing."""
        # Extract Step 1 section only
        step1_start = review_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in review.md"

        step2_start = review_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in review.md"

        step1_content = review_md_content[step1_start:step2_start]

        # Check that Step 1 section contains both "default" and "false" near parallel_enabled
        has_default_false = (
            "default" in step1_content.lower()
            and "false" in step1_content
            and "parallel_enabled" in step1_content
        )
        assert has_default_false, (
            "review.md Step 1 must document that parallel_enabled defaults to false "
            "when the key is missing from config. "
            f"Step 1 content:\n{step1_content}"
        )


class TestStep1LoadsAgentTimeout:
    """Step 1 (Load Configuration) must also mention agent_timeout — S8-002."""

    def test_step1_mentions_agent_timeout(self, review_md_content):
        """Step 1 must list agent_timeout as a loaded config key."""
        assert "agent_timeout" in review_md_content, (
            "commands/review.md Step 1 must reference 'agent_timeout' as a "
            "config key loaded from .specify/harness-tdd-config.yml"
        )

    def test_step1_section_contains_agent_timeout(self, review_md_content):
        """The Load Configuration section specifically must mention agent_timeout."""
        step1_start = review_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in review.md"

        step2_start = review_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in review.md"

        step1_content = review_md_content[step1_start:step2_start]
        assert "agent_timeout" in step1_content, (
            "Step 1 (Load Configuration) section must reference 'agent_timeout'. "
            f"Step 1 content:\n{step1_content}"
        )

    def test_step1_agent_timeout_has_default_30(self, review_md_content):
        """Step 1 must document default value of 30 for agent_timeout."""
        step1_start = review_md_content.find("## Step 1:")
        assert step1_start != -1, "Step 1 section not found in review.md"

        step2_start = review_md_content.find("## Step 2:", step1_start)
        assert step2_start != -1, "Step 2 section not found in review.md"

        step1_content = review_md_content[step1_start:step2_start]

        has_default_30 = (
            "agent_timeout" in step1_content
            and "30" in step1_content
            and ("default" in step1_content.lower() or "missing" in step1_content.lower())
        )
        assert has_default_30, (
            "review.md Step 1 must document that agent_timeout defaults to 30 "
            "when the key is missing from config. "
            f"Step 1 content:\n{step1_content}"
        )


class TestStep7AgentTimeoutInstruction:
    """Step 7 (Invoke Parallel Reviewers) must include timeout instruction — S8-002."""

    def test_step7_section_contains_timeout_reference(self, review_md_content):
        """Step 7 agent delegation must include a timeout instruction."""
        step7_start = review_md_content.find("## Step 7:")
        assert step7_start != -1, "Step 7 section not found in review.md"

        step8_start = review_md_content.find("## Step 8:", step7_start)
        assert step8_start != -1, "Step 8 section not found in review.md"

        step7_content = review_md_content[step7_start:step8_start]

        has_timeout = (
            "agent_timeout" in step7_content
            or "timeout" in step7_content.lower()
        )
        assert has_timeout, (
            "Step 7 (Invoke Parallel Reviewers) must include a timeout instruction "
            "referencing the agent_timeout value. "
            f"Step 7 content:\n{step7_content}"
        )

    def test_step7_timeout_instructs_partial_results_on_timeout(self, review_md_content):
        """Step 7 timeout instruction must tell agent to output partial results."""
        step7_start = review_md_content.find("## Step 7:")
        assert step7_start != -1, "Step 7 section not found in review.md"

        step8_start = review_md_content.find("## Step 8:", step7_start)
        assert step8_start != -1, "Step 8 section not found in review.md"

        step7_content = review_md_content[step7_start:step8_start]

        has_partial = (
            "partial" in step7_content.lower()
            or "incomplete" in step7_content.lower()
        )
        assert has_partial, (
            "Step 7 timeout instruction must tell the agent to output partial results "
            "when timeout is reached. "
            f"Step 7 content:\n{step7_content}"
        )

    def test_step7_timeout_instructs_escalate_to_human(self, review_md_content):
        """Step 7 timeout instruction must tell agent to escalate to human."""
        step7_start = review_md_content.find("## Step 7:")
        assert step7_start != -1, "Step 7 section not found in review.md"

        step8_start = review_md_content.find("## Step 8:", step7_start)
        assert step8_start != -1, "Step 8 section not found in review.md"

        step7_content = review_md_content[step7_start:step8_start]

        has_escalate = (
            "escalate" in step7_content.lower()
            or "human" in step7_content.lower()
        )
        assert has_escalate, (
            "Step 7 timeout instruction must tell the agent to escalate to human "
            "when timeout is reached. "
            f"Step 7 content:\n{step7_content}"
        )
