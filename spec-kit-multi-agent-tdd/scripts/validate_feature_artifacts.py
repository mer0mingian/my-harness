#!/usr/bin/env python3
"""Standalone feature artifact validation script for TDD constitutional enforcement.

This script validates that all 5 mandatory artifacts exist with correct structure
before allowing git commit. Evidence gate enforcement.

Exit Codes:
    0: All artifacts valid
    1: Missing or invalid artifacts
    2: System error

Usage:
    python3 scripts/validate_feature_artifacts.py feat-123
    python3 scripts/validate_feature_artifacts.py feat-123 --project-root /path/to/project
    python3 scripts/validate_feature_artifacts.py feat-123 --format json
    python3 scripts/validate_feature_artifacts.py feat-123 --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Import from lib modules
try:
    from lib.validate_artifacts import (
        validate_artifact_exists,
        validate_template_sections,
        validate_evidence_timestamps,
        validate_red_green_evidence,
        TEMPLATE_SECTIONS,
    )
    from lib.artifact_paths import resolve
except ImportError:
    # Try relative import if run from scripts/
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from lib.validate_artifacts import (
        validate_artifact_exists,
        validate_template_sections,
        validate_evidence_timestamps,
        validate_red_green_evidence,
        TEMPLATE_SECTIONS,
    )
    from lib.artifact_paths import resolve


# Artifact types to validate
ARTIFACT_TYPES = {
    "test_design": "test-design",
    "impl_notes": "implementation-notes",
    "arch_review": "arch-review",
    "code_review": "code-review",
    "workflow_summary": "workflow-summary",
}

# Mandatory artifacts (impl_notes is optional)
MANDATORY_ARTIFACTS = ["test_design", "arch_review", "code_review", "workflow_summary"]


def resolve_artifact_path(feature_id: str, artifact_type: str, project_root: Path) -> Path:
    """
    Resolve path for an artifact file.

    Args:
        feature_id: Feature identifier
        artifact_type: Type of artifact
        project_root: Project root directory

    Returns:
        Path to artifact file
    """
    suffix = ARTIFACT_TYPES.get(artifact_type, artifact_type)
    artifacts_dir = project_root / "artifacts"
    return artifacts_dir / f"{feature_id}-{suffix}.md"


def validate_artifact_structure(artifact_path: Path, artifact_type: str) -> Dict[str, Any]:
    """
    Validate structure of a specific artifact.

    Args:
        artifact_path: Path to artifact file
        artifact_type: Type of artifact

    Returns:
        Dict with validation results
    """
    result = {
        "exists": False,
        "valid": False,
        "issues": [],
    }

    # Check existence
    if not validate_artifact_exists(artifact_path):
        result["issues"].append(f"Artifact not found: {artifact_path}")
        return result

    result["exists"] = True

    # Validate structure if template sections are defined
    if artifact_type in TEMPLATE_SECTIONS:
        required_sections = TEMPLATE_SECTIONS[artifact_type]
        is_valid, missing_sections = validate_template_sections(artifact_path, required_sections)

        if is_valid:
            result["valid"] = True
        else:
            result["valid"] = False
            result["issues"].append(f"Missing sections: {', '.join(missing_sections)}")
    else:
        # No template validation for artifacts without defined sections
        result["valid"] = True

    return result


def validate_all_artifacts(feature_id: str, project_root: Path) -> Dict[str, Any]:
    """
    Validate all feature artifacts.

    Args:
        feature_id: Feature identifier
        project_root: Project root directory

    Returns:
        Validation report dictionary
    """
    artifacts_dir = project_root / "artifacts"

    report = {
        "feature_id": feature_id,
        "valid": True,
        "artifacts": {},
        "timestamp_order_valid": True,
        "message": "",
        "errors": [],
    }

    # Validate each artifact
    for artifact_type in ARTIFACT_TYPES.keys():
        artifact_path = resolve_artifact_path(feature_id, artifact_type, project_root)
        validation = validate_artifact_structure(artifact_path, artifact_type)

        report["artifacts"][artifact_type] = validation

        # Check if mandatory artifact is missing or invalid
        if artifact_type in MANDATORY_ARTIFACTS:
            if not validation["exists"]:
                report["valid"] = False
                report["errors"].append(f"Mandatory artifact missing: {artifact_type}")
            elif not validation["valid"]:
                report["valid"] = False
                report["errors"].extend(validation["issues"])

    # Validate timestamps if workflow summary exists
    workflow_summary = report["artifacts"]["workflow_summary"]
    if workflow_summary["exists"]:
        # Validate RED/GREEN evidence
        red_green_valid, red_green_msg = validate_red_green_evidence(artifacts_dir)
        if not red_green_valid:
            report["valid"] = False
            report["errors"].append(f"Evidence validation failed: {red_green_msg}")

        # Validate timestamp ordering
        timestamps_valid, timestamps_msg = validate_evidence_timestamps(artifacts_dir)
        report["timestamp_order_valid"] = timestamps_valid
        report["message"] = timestamps_msg

        if not timestamps_valid:
            report["valid"] = False
            report["errors"].append(f"Timestamp validation failed: {timestamps_msg}")
    else:
        report["timestamp_order_valid"] = False
        report["message"] = "Workflow summary missing - cannot validate timestamps"

    return report


def format_text_output(report: Dict[str, Any], verbose: bool = False) -> str:
    """
    Format validation report as human-readable text.

    Args:
        report: Validation report
        verbose: Whether to show detailed output

    Returns:
        Formatted text output
    """
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Artifact Validation Report: {report['feature_id']}")
    lines.append(f"{'='*60}\n")

    status = "✓ VALID" if report["valid"] else "✗ INVALID"
    lines.append(f"Status: {status}\n")

    if verbose or not report["valid"]:
        lines.append("Artifacts:")
        for artifact_type, info in report["artifacts"].items():
            exists_mark = "✓" if info["exists"] else "✗"
            valid_mark = "✓" if info["valid"] else "✗"

            if info["exists"]:
                mandatory = " (mandatory)" if artifact_type in MANDATORY_ARTIFACTS else " (optional)"
                lines.append(f"  {exists_mark} {artifact_type}{mandatory}: exists {valid_mark} structure")
                if info["issues"]:
                    for issue in info["issues"]:
                        lines.append(f"    - {issue}")
            else:
                mandatory = " (MANDATORY)" if artifact_type in MANDATORY_ARTIFACTS else " (optional)"
                lines.append(f"  {exists_mark} {artifact_type}{mandatory}: MISSING")

        lines.append("\nTimestamp Validation:")
        timestamp_mark = "✓" if report["timestamp_order_valid"] else "✗"
        lines.append(f"  {timestamp_mark} {report['message']}")

    if report["errors"]:
        lines.append("\nErrors:")
        for error in report["errors"]:
            lines.append(f"  - {error}")

    lines.append(f"\n{'='*60}\n")

    return "\n".join(lines)


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Validate TDD workflow artifacts for a feature",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s feat-123
  %(prog)s feat-123 --project-root /path/to/project
  %(prog)s feat-123 --format json
  %(prog)s feat-123 --verbose

Validates:
  - test_design: Feature ID, Acceptance Criteria, Test Strategy
  - impl_notes: Feature ID, Implementation Approach (optional)
  - arch_review: Feature ID, Verdict, Safety Constraints
  - code_review: Feature ID, Verdict, Quality Issues
  - workflow_summary: Feature ID, TDD Evidence, Review Verdicts

Exit Codes:
  0: All artifacts valid
  1: Missing or invalid artifacts
  2: System error
        """,
    )

    parser.add_argument(
        "feature_id",
        help="Feature identifier (e.g., feat-123)",
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Path to project root directory (default: current directory)",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed validation results",
    )

    args = parser.parse_args()

    # Validate artifacts
    try:
        report = validate_all_artifacts(args.feature_id, args.project_root)

        # Output report
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print(format_text_output(report, verbose=args.verbose))

        # Exit with appropriate code
        sys.exit(0 if report["valid"] else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
