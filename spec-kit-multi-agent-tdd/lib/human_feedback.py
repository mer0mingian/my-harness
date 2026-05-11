"""
Human feedback capture for Multi-Agent TDD workflow.

Provides simple interface for requesting human feedback at workflow stages.
"""

from typing import Optional


def request_feedback(
    stage: str,
    context: dict,
    skip: bool = False
) -> Optional[str]:
    """
    Request human feedback at a workflow stage.

    Args:
        stage: Workflow stage name (e.g., "Test Design Review")
        context: Context information to display to user
        skip: If True, skip feedback request and return None

    Returns:
        Feedback string or None if skipped/empty

    Example:
        >>> feedback = request_feedback(
        ...     stage="Test Design Review",
        ...     context={'feature_id': 'feat-123', 'test_count': 5},
        ...     skip=False
        ... )
        HUMAN FEEDBACK REQUESTED: Test Design Review
        ============================================================
        feature_id: feat-123
        test_count: 5
        Provide feedback (or press Enter to continue): Great work!
        >>> print(feedback)
        Great work!
    """
    if skip:
        return None

    # Print header
    print(f"\n{'='*60}")
    print(f"HUMAN FEEDBACK REQUESTED: {stage}")
    print(f"{'='*60}")

    # Print context
    for key, value in context.items():
        print(f"{key}: {value}")

    # Request input
    print("\nProvide feedback (or press Enter to continue): ", end='', flush=True)
    feedback = input().strip()

    return feedback if feedback else None


def append_to_artifact(artifact_path, feedback: str) -> None:
    """
    Append feedback to an artifact file.

    Args:
        artifact_path: Path to artifact file
        feedback: Feedback text to append
    """
    if not feedback:
        return

    with open(artifact_path, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## Human Feedback\n{feedback}\n")
