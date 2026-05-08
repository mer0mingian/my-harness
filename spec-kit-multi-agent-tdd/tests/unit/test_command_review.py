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
        """Step 7 or Step 1 must document that default is false when key missing."""
        has_default_false = (
            "default" in review_md_content.lower()
            and "false" in review_md_content
            and "parallel_enabled" in review_md_content
        )
        assert has_default_false, (
            "review.md must document that parallel_enabled defaults to false "
            "when the key is missing from config"
        )
