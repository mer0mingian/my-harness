#!/usr/bin/env python3
"""
Artifact validator for Multi-Agent TDD workflow (S2B-004).

Validates that all mandatory artifacts exist and conform to template structure.
Ensures RED-before-GREEN TDD compliance through evidence timestamp validation.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any


# Template section requirements
TEMPLATE_SECTIONS = {
    "test_design": [
        "Test Design:",
        "Test Strategy",
        "Acceptance Criteria Mapping",
        "RED State Validation",
        "Escalations",
        "Decision",
    ],
    "arch_review": [
        "Architecture Review:",
        "Architecture Impacts",
        "Safety Constraints",
        "Verdict",
    ],
    "code_review": [
        "Code Review:",
        "Code Quality",
        "Test Coverage",
        "Verdict",
    ],
    "workflow_summary": [
        "Workflow Summary:",
        "Feature Information",
        "Test Evidence",
        "Implementation Evidence",
        "Review Evidence",
        "Commit Information",
    ],
}


def validate_artifact_exists(artifact_path: Path) -> bool:
    """Check if artifact file exists."""
    return artifact_path.exists() and artifact_path.is_file()


def validate_template_sections(
    artifact_path: Path, template_sections: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate required headers/sections present in artifact.

    Returns:
        Tuple of (is_valid, missing_sections)
    """
    if not artifact_path.exists():
        return False, template_sections

    content = artifact_path.read_text()
    missing_sections = []

    for section in template_sections:
        # Escape section name and remove trailing colon if present for matching
        section_base = section.rstrip(':')
        section_escaped = re.escape(section_base)

        # Match section as:
        # 1. Markdown header: # Section or ## Section (with optional colon)
        # 2. Bold text: **Section:** or **Section**
        # 3. Plain text with word boundary
        pattern = rf"(?:^#{1,6}\s+{section_escaped}:?|^\*\*{section_escaped}:?\*\*|\b{section_escaped}\b)"

        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            missing_sections.append(section)

    is_valid = len(missing_sections) == 0
    return is_valid, missing_sections


def validate_evidence_timestamps(artifacts_dir: Path) -> Tuple[bool, str]:
    """
    Check RED timestamp < GREEN timestamp.

    Returns:
        Tuple of (is_valid, message)
    """
    # Find workflow summary (should be the file with 'workflow-summary' in name)
    workflow_files = list(artifacts_dir.glob("*workflow-summary.md"))

    if not workflow_files:
        return False, "Workflow summary not found"

    workflow_summary = workflow_files[0]
    content = workflow_summary.read_text()

    # Extract timestamps using regex
    red_pattern = r"RED State Timestamp:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?)"
    green_pattern = r"GREEN State Timestamp:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?)"

    red_match = re.search(red_pattern, content)
    green_match = re.search(green_pattern, content)

    if not red_match:
        return False, "RED state timestamp not found"
    if not green_match:
        return False, "GREEN state timestamp not found"

    red_timestamp_str = red_match.group(1)
    green_timestamp_str = green_match.group(1)

    try:
        # Parse ISO 8601 timestamps
        red_timestamp = datetime.fromisoformat(red_timestamp_str.replace("Z", "+00:00"))
        green_timestamp = datetime.fromisoformat(green_timestamp_str.replace("Z", "+00:00"))

        if red_timestamp < green_timestamp:
            return True, f"RED ({red_timestamp_str}) before GREEN ({green_timestamp_str})"
        else:
            return False, f"Invalid timestamp order: RED ({red_timestamp_str}) after GREEN ({green_timestamp_str})"

    except ValueError as e:
        return False, f"Invalid timestamp format: {e}"


def validate_red_green_evidence(artifacts_dir: Path) -> Tuple[bool, str]:
    """
    Check RED and GREEN state evidence exists.

    Returns:
        Tuple of (is_valid, message)
    """
    # Find workflow summary
    workflow_files = list(artifacts_dir.glob("*workflow-summary.md"))

    if not workflow_files:
        return False, "Workflow summary not found"

    workflow_summary = workflow_files[0]
    content = workflow_summary.read_text()

    # Check for RED state evidence
    red_patterns = [
        r"RED State:",
        r"RED State Timestamp:",
        r"MISSING_BEHAVIOR",
        r"ASSERTION_MISMATCH",
    ]

    red_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in red_patterns)

    # Check for GREEN state evidence
    green_patterns = [
        r"GREEN State:",
        r"GREEN State Timestamp:",
        r"All tests passing",
        r"tests passing",
    ]

    green_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in green_patterns)

    if red_found and green_found:
        return True, "Both RED and GREEN evidence found"
    elif not red_found:
        return False, "RED state evidence missing"
    elif not green_found:
        return False, "GREEN state evidence missing"
    else:
        return False, "Both RED and GREEN state evidence missing"


def validate_feature_artifacts(feature_id: str, artifacts_dir: Path) -> Dict[str, Any]:
    """
    Main validation function for all feature artifacts.

    Returns:
        Validation report dictionary
    """
    artifacts_dir = Path(artifacts_dir)

    # Define expected artifact paths
    artifact_paths = {
        "test_design": artifacts_dir / f"{feature_id}-test-design.md",
        "implementation_notes": artifacts_dir / f"{feature_id}-implementation-notes.md",
        "arch_review": artifacts_dir / f"{feature_id}-arch-review.md",
        "code_review": artifacts_dir / f"{feature_id}-code-review.md",
        "workflow_summary": artifacts_dir / f"{feature_id}-workflow-summary.md",
    }

    # Mandatory artifacts (implementation_notes is optional)
    mandatory_artifacts = ["test_design", "arch_review", "code_review", "workflow_summary"]

    # Initialize report
    report: Dict[str, Any] = {
        "feature_id": feature_id,
        "valid": True,
        "artifacts": {},
        "evidence": {},
        "errors": [],
    }

    # Validate each artifact
    for artifact_type, artifact_path in artifact_paths.items():
        artifact_info = {
            "exists": False,
            "valid_structure": False,
            "missing_sections": [],
        }

        # Check existence
        exists = validate_artifact_exists(artifact_path)
        artifact_info["exists"] = exists

        if not exists:
            if artifact_type in mandatory_artifacts:
                report["errors"].append(f"Mandatory artifact missing: {artifact_type}")
                report["valid"] = False
        else:
            # Validate structure for artifacts with defined sections
            if artifact_type in TEMPLATE_SECTIONS:
                is_valid, missing = validate_template_sections(
                    artifact_path, TEMPLATE_SECTIONS[artifact_type]
                )
                artifact_info["valid_structure"] = is_valid
                artifact_info["missing_sections"] = missing

                if not is_valid:
                    report["errors"].append(
                        f"{artifact_type} missing sections: {', '.join(missing)}"
                    )
                    report["valid"] = False

        report["artifacts"][artifact_type] = artifact_info

    # Validate evidence (only if workflow summary exists)
    if report["artifacts"]["workflow_summary"]["exists"]:
        # Validate RED/GREEN evidence
        red_green_valid, red_green_msg = validate_red_green_evidence(artifacts_dir)
        report["evidence"]["red_green_transition"] = red_green_valid
        if not red_green_valid:
            report["errors"].append(f"Evidence validation failed: {red_green_msg}")
            report["valid"] = False

        # Validate timestamps
        timestamps_valid, timestamps_msg = validate_evidence_timestamps(artifacts_dir)
        report["evidence"]["timestamps_valid"] = timestamps_valid
        report["evidence"]["message"] = timestamps_msg
        if not timestamps_valid:
            report["errors"].append(f"Timestamp validation failed: {timestamps_msg}")
            report["valid"] = False
    else:
        report["evidence"]["red_green_transition"] = False
        report["evidence"]["timestamps_valid"] = False
        report["evidence"]["message"] = "Workflow summary missing"

    return report


def format_report_text(report: Dict[str, Any], verbose: bool = False) -> str:
    """Format validation report as human-readable text."""
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
            structure_mark = "✓" if info.get("valid_structure", True) else "✗"

            if info["exists"]:
                lines.append(f"  {exists_mark} {artifact_type}: exists {structure_mark} structure")
                if info.get("missing_sections"):
                    lines.append(f"    Missing: {', '.join(info['missing_sections'])}")
            else:
                lines.append(f"  {exists_mark} {artifact_type}: MISSING")

        lines.append("\nEvidence:")
        evidence = report.get("evidence", {})
        red_green_mark = "✓" if evidence.get("red_green_transition") else "✗"
        timestamp_mark = "✓" if evidence.get("timestamps_valid") else "✗"

        lines.append(f"  {red_green_mark} RED/GREEN transition")
        lines.append(f"  {timestamp_mark} Timestamps: {evidence.get('message', 'N/A')}")

    if report["errors"]:
        lines.append("\nErrors:")
        for error in report["errors"]:
            lines.append(f"  - {error}")

    lines.append(f"\n{'='*60}\n")

    return "\n".join(str(line) for line in lines)


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Validate TDD workflow artifacts for a feature",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s feat-123
  %(prog)s feat-123 --artifacts-dir ./artifacts
  %(prog)s feat-123 --verbose
  %(prog)s feat-123 --format json
        """,
    )

    parser.add_argument(
        "feature_id",
        help="Feature identifier (e.g., feat-123)",
    )

    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("./artifacts"),
        help="Path to artifacts directory (default: ./artifacts/)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed validation results",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Validate artifacts
    try:
        report = validate_feature_artifacts(args.feature_id, args.artifacts_dir)

        # Output report
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print(format_report_text(report, verbose=args.verbose))

        # Exit with appropriate code
        sys.exit(0 if report["valid"] else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
