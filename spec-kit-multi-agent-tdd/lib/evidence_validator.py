"""
Evidence validation for Multi-Agent TDD workflow.

Validates constitutional evidence requirements (CONSTITUTION lines 120-144).
"""

from pathlib import Path
from typing import Optional

from . import artifact_paths


def validate_all(
    feature_id: str,
    config: dict,
    project_root: Optional[Path] = None
) -> tuple[bool, list[str]]:
    """
    Validate all constitutional evidence requirements.

    Args:
        feature_id: Feature identifier
        config: Configuration dictionary
        project_root: Optional project root (defaults to cwd)

    Returns:
        (valid, missing_items) tuple

    Example:
        >>> valid, missing = validate_all('feat-123', config)
        >>> if not valid:
        ...     print(f"Missing: {', '.join(missing)}")
    """
    if project_root is None:
        project_root = Path.cwd()

    missing = []

    # Step 7: Test Evidence
    test_design_path = artifact_paths.find_existing(
        feature_id, 'test_design', config, project_root
    )
    if not test_design_path:
        missing.append("Test design artifact (mandatory)")
    else:
        # Check for RED state evidence
        content = test_design_path.read_text(encoding='utf-8')
        if 'RED State Validation' not in content:
            missing.append("RED state evidence in test design")
        if not ('MISSING_BEHAVIOR' in content or 'ASSERTION_MISMATCH' in content):
            missing.append("Valid failure codes (MISSING_BEHAVIOR or ASSERTION_MISMATCH)")

    # Step 8: Implementation Evidence (impl notes optional per CONSTITUTION line 125)
    # Check for GREEN state proof in workflow summary instead
    summary_path = artifact_paths.find_existing(
        feature_id, 'workflow_summary', config, project_root
    )
    if summary_path:
        content = summary_path.read_text(encoding='utf-8')
        if 'GREEN State:' not in content:
            missing.append("GREEN state evidence in workflow summary")

    # Step 9: Review Evidence
    arch_review_path = artifact_paths.find_existing(
        feature_id, 'arch_review', config, project_root
    )
    if not arch_review_path:
        missing.append("Architecture review artifact (mandatory)")

    code_review_path = artifact_paths.find_existing(
        feature_id, 'code_review', config, project_root
    )
    if not code_review_path:
        missing.append("Code review artifact (mandatory)")

    # Step 10: Commit Evidence
    if not summary_path:
        missing.append("Workflow summary artifact (mandatory)")

    return len(missing) == 0, missing


def validate_test_evidence(
    feature_id: str,
    config: dict,
    project_root: Optional[Path] = None
) -> tuple[bool, list[str]]:
    """
    Validate test evidence (Step 7).

    Args:
        feature_id: Feature identifier
        config: Configuration dictionary
        project_root: Optional project root

    Returns:
        (valid, missing_items) tuple
    """
    if project_root is None:
        project_root = Path.cwd()

    missing = []

    test_design_path = artifact_paths.find_existing(
        feature_id, 'test_design', config, project_root
    )
    if not test_design_path:
        missing.append("Test design artifact")
        return False, missing

    content = test_design_path.read_text(encoding='utf-8')

    # Check RED state validation
    if 'RED State Validation' not in content:
        missing.append("RED state validation section")

    # Check failure codes
    if not ('MISSING_BEHAVIOR' in content or 'ASSERTION_MISMATCH' in content):
        missing.append("Valid failure codes")

    # Check valid RED confirmation
    if 'Valid RED: YES' not in content and 'Valid RED:** YES' not in content:
        missing.append("Valid RED confirmation")

    return len(missing) == 0, missing


def validate_review_evidence(
    feature_id: str,
    config: dict,
    project_root: Optional[Path] = None
) -> tuple[bool, list[str]]:
    """
    Validate review evidence (Step 9).

    Args:
        feature_id: Feature identifier
        config: Configuration dictionary
        project_root: Optional project root

    Returns:
        (valid, missing_items) tuple
    """
    if project_root is None:
        project_root = Path.cwd()

    missing = []

    arch_review_path = artifact_paths.find_existing(
        feature_id, 'arch_review', config, project_root
    )
    if not arch_review_path:
        missing.append("Architecture review artifact")

    code_review_path = artifact_paths.find_existing(
        feature_id, 'code_review', config, project_root
    )
    if not code_review_path:
        missing.append("Code review artifact")

    # Check for review verdict
    if arch_review_path:
        content = arch_review_path.read_text(encoding='utf-8')
        if 'Verdict:' not in content and '**Verdict:**' not in content:
            missing.append("Architecture review verdict")

    if code_review_path:
        content = code_review_path.read_text(encoding='utf-8')
        if 'Verdict:' not in content and '**Verdict:**' not in content:
            missing.append("Code review verdict")

    return len(missing) == 0, missing
