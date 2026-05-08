"""
Unit tests for lib/jira_local.py — auto_create_story_structure function.

Tests follow TDD red-green-refactor: written before implementation.
All filesystem tests use tmp_path fixture for isolation.
"""

import pytest
from pathlib import Path
from lib.jira_local import auto_create_story_structure


class TestAutoCreateStoryStructure:
    """Tests for auto_create_story_structure()."""

    def test_creates_directory_and_file_when_both_missing(self, tmp_path):
        """Creating structure from scratch creates the epic dir and story file."""
        result = auto_create_story_structure(
            feature_id="feat-001",
            epic_id="epic-001",
            story_id="story-001",
            jira_root=str(tmp_path / "epics"),
        )
        expected_path = tmp_path / "epics" / "epic-001" / "story-001.md"
        assert result["created"] is True
        assert result["path"] == str(expected_path)
        assert expected_path.exists()
        assert (tmp_path / "epics" / "epic-001").is_dir()

    def test_idempotent_second_call_returns_created_false(self, tmp_path):
        """Second call with same args returns created=False without overwriting."""
        jira_root = str(tmp_path / "epics")
        auto_create_story_structure(
            feature_id="feat-001",
            epic_id="epic-001",
            story_id="story-001",
            jira_root=jira_root,
        )
        story_path = tmp_path / "epics" / "epic-001" / "story-001.md"
        original_content = story_path.read_text()

        result = auto_create_story_structure(
            feature_id="feat-001",
            epic_id="epic-001",
            story_id="story-001",
            jira_root=jira_root,
        )
        assert result["created"] is False
        assert result["path"] == str(story_path)
        # File unchanged
        assert story_path.read_text() == original_content

    def test_raises_value_error_for_empty_epic_id(self, tmp_path):
        """Empty epic_id raises ValueError."""
        with pytest.raises(ValueError, match="epic_id"):
            auto_create_story_structure(
                feature_id="feat-001",
                epic_id="",
                story_id="story-001",
                jira_root=str(tmp_path / "epics"),
            )

    def test_raises_value_error_for_empty_story_id(self, tmp_path):
        """Empty story_id raises ValueError."""
        with pytest.raises(ValueError, match="story_id"):
            auto_create_story_structure(
                feature_id="feat-001",
                epic_id="epic-001",
                story_id="",
                jira_root=str(tmp_path / "epics"),
            )

    def test_created_file_contains_required_frontmatter_keys(self, tmp_path):
        """Created story file has all required frontmatter keys."""
        auto_create_story_structure(
            feature_id="feat-001",
            epic_id="epic-001",
            story_id="story-001",
            jira_root=str(tmp_path / "epics"),
        )
        content = (tmp_path / "epics" / "epic-001" / "story-001.md").read_text()
        assert "story_id: story-001" in content
        assert "epic_id: epic-001" in content
        assert "feature_id: feat-001" in content
        assert "status: open" in content

    def test_created_file_contains_required_section_headings(self, tmp_path):
        """Created story file has all required section headings."""
        auto_create_story_structure(
            feature_id="feat-001",
            epic_id="epic-001",
            story_id="story-001",
            jira_root=str(tmp_path / "epics"),
        )
        content = (tmp_path / "epics" / "epic-001" / "story-001.md").read_text()
        assert "# Story: story-001" in content
        assert "## Description" in content
        assert "## Acceptance Criteria" in content
        assert "## Tasks" in content

    def test_custom_jira_root_path_is_respected(self, tmp_path):
        """Custom jira_root produces file under the given path."""
        custom_root = str(tmp_path / "custom" / "jira")
        result = auto_create_story_structure(
            feature_id="feat-999",
            epic_id="epic-999",
            story_id="story-999",
            jira_root=custom_root,
        )
        expected = tmp_path / "custom" / "jira" / "epic-999" / "story-999.md"
        assert result["created"] is True
        assert result["path"] == str(expected)
        assert expected.exists()

    def test_default_jira_root_used_when_not_provided(self, tmp_path, monkeypatch):
        """When jira_root omitted, function uses default .specify/epics relative to cwd."""
        monkeypatch.chdir(tmp_path)
        result = auto_create_story_structure(
            feature_id="feat-001",
            epic_id="epic-001",
            story_id="story-001",
        )
        expected = tmp_path / ".specify" / "epics" / "epic-001" / "story-001.md"
        assert result["created"] is True
        assert expected.exists()


class TestCommitMdJiraAutoCreateStories:
    """Verify commit.md Step 1 documents jira.auto_create_stories config key."""

    def test_commit_md_step1_has_auto_create_stories_key(self):
        """commit.md Step 1 must reference jira.auto_create_stories config key."""
        commit_md_path = Path(__file__).parent.parent.parent / "commands" / "commit.md"
        content = commit_md_path.read_text(encoding="utf-8")
        assert "jira.auto_create_stories" in content
