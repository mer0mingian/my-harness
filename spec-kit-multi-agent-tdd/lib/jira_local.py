"""
Local Jira structure management for Multi-Agent TDD workflow.

Creates and manages Epic/Story folder structure for team sync (future Jira integration).
"""

from pathlib import Path
from typing import Optional
from datetime import datetime


DEFAULT_JIRA_ROOT = '.specify/epics'


def create_epic_folder(
    epic_id: str,
    title: str,
    project_root: Optional[Path] = None,
    jira_root: Optional[str] = None
) -> Path:
    """
    Create Epic folder with EPIC.md metadata file.

    Args:
        epic_id: Epic identifier (e.g., 'epic-001')
        title: Epic title
        project_root: Optional project root (defaults to cwd)
        jira_root: Optional Jira root directory (defaults to .specify/epics)

    Returns:
        Path to epic folder

    Example:
        >>> create_epic_folder('epic-001', 'User Authentication')
        PosixPath('.specify/epics/epic-001-user-authentication')
    """
    if project_root is None:
        project_root = Path.cwd()
    if jira_root is None:
        jira_root = DEFAULT_JIRA_ROOT

    # Create epic folder name (kebab-case)
    folder_name = f"{epic_id}-{title.lower().replace(' ', '-')}"
    epic_folder = project_root / jira_root / folder_name

    # Create folder
    epic_folder.mkdir(parents=True, exist_ok=True)

    # Create EPIC.md if it doesn't exist
    epic_file = epic_folder / 'EPIC.md'
    if not epic_file.exists():
        content = f"""---
epic_id: {epic_id}
epic_key: null  # Future Jira Epic key
title: {title}
status: Planning
created: {datetime.now().isoformat()}
stories: []
---

# Epic: {title}

## Description
[Epic description and value proposition]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Stories
[Stories will be listed here as they are created]
"""
        epic_file.write_text(content, encoding='utf-8')

    return epic_folder


def create_story_file(
    epic_id: str,
    story_id: str,
    title: str,
    feature_id: str,
    project_root: Optional[Path] = None,
    jira_root: Optional[str] = None
) -> Path:
    """
    Create Story markdown file within Epic folder.

    Args:
        epic_id: Parent epic identifier
        story_id: Story identifier (e.g., 'story-001')
        title: Story title
        feature_id: Linked feature identifier (e.g., 'feat-123')
        project_root: Optional project root
        jira_root: Optional Jira root directory

    Returns:
        Path to story file

    Example:
        >>> create_story_file('epic-001', 'story-001', 'Login Flow', 'feat-auth-login')
        PosixPath('.specify/epics/epic-001-.../story-001-login-flow.md')
    """
    if project_root is None:
        project_root = Path.cwd()
    if jira_root is None:
        jira_root = DEFAULT_JIRA_ROOT

    # Find epic folder
    epic_folders = list((project_root / jira_root).glob(f"{epic_id}-*"))
    if not epic_folders:
        raise FileNotFoundError(f"Epic folder for {epic_id} not found")

    epic_folder = epic_folders[0]

    # Create story filename (kebab-case)
    filename = f"{story_id}-{title.lower().replace(' ', '-')}.md"
    story_file = epic_folder / filename

    # Create story file
    content = f"""---
story_id: {story_id}
story_key: null  # Future Jira Story key
epic: {epic_id}
title: {title}
status: Todo
feature_id: {feature_id}
created: {datetime.now().isoformat()}
---

# Story: {title}

## User Story
As a [persona]
I want [capability]
So that [benefit]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Workflow Artifacts
- Spec: `docs/features/{feature_id}-spec.md`
- Test Design: `docs/features/{feature_id}-test-design.md`
- Implementation Notes: `docs/features/{feature_id}-impl-notes.md` (optional)
- Arch Review: `docs/features/{feature_id}-arch-review.md`
- Code Review: `docs/features/{feature_id}-code-review.md`
- Workflow Summary: `docs/features/{feature_id}-workflow-summary.md`

## Notes
[Additional context, dependencies, technical decisions]
"""
    story_file.write_text(content, encoding='utf-8')

    return story_file


def update_story_status(
    story_id: str,
    status: str,
    project_root: Optional[Path] = None,
    jira_root: Optional[str] = None
) -> None:
    """
    Update story status in frontmatter.

    Args:
        story_id: Story identifier
        status: New status (Todo, In Progress, Done, etc.)
        project_root: Optional project root
        jira_root: Optional Jira root directory
    """
    if project_root is None:
        project_root = Path.cwd()
    if jira_root is None:
        jira_root = DEFAULT_JIRA_ROOT

    # Find story file
    story_files = list((project_root / jira_root).glob(f"*/{story_id}-*.md"))
    if not story_files:
        raise FileNotFoundError(f"Story file for {story_id} not found")

    story_file = story_files[0]

    # Read content
    content = story_file.read_text(encoding='utf-8')

    # Update status in frontmatter
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('status:'):
            lines[i] = f'status: {status}'
            break

    # Write back
    story_file.write_text('\n'.join(lines), encoding='utf-8')


def link_artifacts_to_story(
    story_id: str,
    artifacts: list[Path],
    project_root: Optional[Path] = None,
    jira_root: Optional[str] = None
) -> None:
    """
    Update story file with actual artifact paths.

    Args:
        story_id: Story identifier
        artifacts: List of artifact paths
        project_root: Optional project root
        jira_root: Optional Jira root directory
    """
    if project_root is None:
        project_root = Path.cwd()
    if jira_root is None:
        jira_root = DEFAULT_JIRA_ROOT

    # Find story file
    story_files = list((project_root / jira_root).glob(f"*/{story_id}-*.md"))
    if not story_files:
        return  # Story doesn't exist yet, skip linking

    story_file = story_files[0]

    # Read content
    content = story_file.read_text(encoding='utf-8')

    # Append artifacts section if not already present
    if '## Generated Artifacts' not in content:
        artifact_list = '\n'.join(f"- [{a.name}]({a})" for a in artifacts)
        content += f"\n\n## Generated Artifacts\n{artifact_list}\n"
        story_file.write_text(content, encoding='utf-8')
