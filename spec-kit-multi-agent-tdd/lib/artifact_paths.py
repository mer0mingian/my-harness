"""
Artifact path resolution for Multi-Agent TDD workflow.

Provides standardized path resolution for all workflow artifacts with
configurable search paths and naming conventions.
"""

from pathlib import Path
from typing import Optional


# Default artifact types and their suffixes
DEFAULT_ARTIFACT_TYPES = {
    'spec': 'spec',
    'test_design': 'test-design',
    'impl_notes': 'impl-notes',
    'arch_review': 'arch-review',
    'code_review': 'code-review',
    'workflow_summary': 'workflow-summary',
}

# Default search paths (in priority order)
DEFAULT_SEARCH_PATHS = [
    'docs/features',
    'docs/specs',
    '.specify/specs',
]


def resolve(
    feature_id: str,
    artifact_type: str,
    config: Optional[dict] = None,
    project_root: Optional[Path] = None
) -> Path:
    """
    Resolve path for a workflow artifact.

    Args:
        feature_id: Feature identifier (e.g., 'feat-123')
        artifact_type: Type of artifact (spec, test_design, etc.)
        config: Optional configuration dict with artifacts.root and artifacts.types
        project_root: Optional project root (defaults to cwd)

    Returns:
        Path to artifact (may not exist yet)

    Example:
        >>> resolve('feat-123', 'test_design')
        PosixPath('docs/features/feat-123-test-design.md')
    """
    if project_root is None:
        project_root = Path.cwd()

    # Get artifact root from config or use default
    if config and 'artifacts' in config:
        artifact_root = config['artifacts'].get('root', DEFAULT_SEARCH_PATHS[0])
        artifact_types = config['artifacts'].get('types', DEFAULT_ARTIFACT_TYPES)
    else:
        artifact_root = DEFAULT_SEARCH_PATHS[0]
        artifact_types = DEFAULT_ARTIFACT_TYPES

    # Get suffix for artifact type
    suffix = artifact_types.get(artifact_type, artifact_type)

    # Construct path
    filename = f"{feature_id}-{suffix}.md"
    return project_root / artifact_root / filename


def find_existing(
    feature_id: str,
    artifact_type: str,
    config: Optional[dict] = None,
    project_root: Optional[Path] = None
) -> Optional[Path]:
    """
    Find existing artifact by searching configured paths.

    Args:
        feature_id: Feature identifier
        artifact_type: Type of artifact
        config: Optional configuration dict
        project_root: Optional project root

    Returns:
        Path to existing artifact or None if not found

    Example:
        >>> find_existing('feat-123', 'spec')
        PosixPath('docs/specs/feat-123-spec.md')  # if exists
    """
    if project_root is None:
        project_root = Path.cwd()

    # Get search paths from config or use defaults
    if config and 'artifacts' in config:
        search_paths = config['artifacts'].get('search_paths', DEFAULT_SEARCH_PATHS)
        artifact_types = config['artifacts'].get('types', DEFAULT_ARTIFACT_TYPES)
    else:
        search_paths = DEFAULT_SEARCH_PATHS
        artifact_types = DEFAULT_ARTIFACT_TYPES

    # Get suffix for artifact type
    suffix = artifact_types.get(artifact_type, artifact_type)
    filename = f"{feature_id}-{suffix}.md"

    # Search in priority order
    for search_path in search_paths:
        candidate = project_root / search_path / filename
        if candidate.exists():
            return candidate

    return None


def ensure_directory(path: Path) -> None:
    """
    Ensure parent directory exists for an artifact path.

    Args:
        path: Path to artifact file
    """
    path.parent.mkdir(parents=True, exist_ok=True)
