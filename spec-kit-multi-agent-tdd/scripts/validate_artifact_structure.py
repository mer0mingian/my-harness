#!/usr/bin/env python3
"""Post-generation artifact structure validation helper.

Validates artifact files for correct structure after generation. This script
is warn-only: it never blocks a workflow, but reports structural issues.

Validates 4 things:
1. Required sections present — based on artifact type from YAML frontmatter
2. YAML frontmatter valid — the frontmatter block parses without error
3. Cross-references exist — if artifact references another file, that file exists
4. File size reasonable — not empty (< 10 bytes), not oversized (> 51200 bytes)

Exit Codes:
    0: All artifacts valid (no issues)
    1: Warnings (issues found but non-blocking)
    2: Error (e.g. file not found, cannot read)

Usage:
    python3 scripts/validate_artifact_structure.py <artifact_path> [<path2> ...]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


# ---------------------------------------------------------------------------
# Template registry — extensible dict mapping artifact type → required sections
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "test-design": ["## Acceptance Criteria", "## Test Cases"],
    "arch-review": ["## Verdict", "## Findings"],
    "code-review": ["## Verdict", "## Findings"],
    "workflow-summary": ["## Summary", "## Artifacts"],
    "prd": ["## What & Why", "## Business Value", "## Goals & No-goals"],
    "adr": ["## Context", "## Decision"],
    "solution-design": ["## Decomposition View", "## Dependency View"],
}

# Cross-reference frontmatter keys to check — maps key name to description
CROSS_REF_KEYS: List[str] = [
    "prd_ref",
    "adr_ref",
    "design_ref",
    "spec_ref",
]

# File size bounds (bytes)
FILE_SIZE_MIN = 10
FILE_SIZE_MAX = 51200


# ---------------------------------------------------------------------------
# Core validation logic
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Tuple[bool, Optional[Dict], str]:
    """Parse YAML frontmatter from a markdown document.

    Frontmatter is the block between the first pair of '---' delimiters.

    Args:
        content: Full file content as string.

    Returns:
        Tuple of (is_valid, parsed_dict, error_message).
        is_valid is False if parsing fails or no frontmatter found.
        parsed_dict is None on failure.
    """
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return True, {}, ""  # No frontmatter is not an error — just empty dict

    # Find closing ---
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return False, None, "Frontmatter block opened with '---' but never closed"

    frontmatter_text = "\n".join(lines[1:end_idx])
    try:
        parsed = yaml.safe_load(frontmatter_text)
        if parsed is None:
            parsed = {}
        return True, parsed, ""
    except yaml.YAMLError as exc:
        return False, None, f"YAML parse error: {exc}"


def check_required_sections(
    content: str,
    artifact_type: Optional[str],
) -> Dict[str, List[str]]:
    """Check which required sections are present and which are missing.

    Args:
        content: Full artifact content.
        artifact_type: Value of the 'type' frontmatter field.

    Returns:
        Dict with 'present' and 'missing' lists of section headings.
    """
    if not artifact_type or artifact_type not in REQUIRED_SECTIONS:
        return {"present": [], "missing": []}

    expected = REQUIRED_SECTIONS[artifact_type]
    present = [section for section in expected if section in content]
    missing = [section for section in expected if section not in content]
    return {"present": present, "missing": missing}


def check_cross_references(frontmatter: Dict) -> Dict[str, List[str]]:
    """Check that any file paths referenced in frontmatter actually exist.

    Args:
        frontmatter: Parsed frontmatter dict.

    Returns:
        Dict with 'found' and 'missing' lists of referenced paths.
    """
    found: List[str] = []
    missing: List[str] = []

    for key in CROSS_REF_KEYS:
        if key not in frontmatter:
            continue
        ref_value = frontmatter[key]
        if not ref_value:
            continue
        ref_path = Path(str(ref_value))
        if ref_path.exists():
            found.append(str(ref_value))
        else:
            missing.append(str(ref_value))

    return {"found": found, "missing": missing}


def check_file_size(path: Path) -> Dict[str, Any]:
    """Check if file size is within acceptable bounds.

    Args:
        path: Path to the artifact file.

    Returns:
        Dict with 'bytes' (int) and 'ok' (bool).
    """
    size = path.stat().st_size
    ok = FILE_SIZE_MIN <= size <= FILE_SIZE_MAX
    return {"bytes": size, "ok": ok}


def validate_single_artifact(path: Path) -> Dict[str, Any]:
    """Validate a single artifact file.

    Args:
        path: Path to the artifact file.

    Returns:
        Dict with 'path', 'checks', and 'issues' keys.
    """
    issues: List[str] = []

    # --- File size check (stat only, no read needed) ---
    size_check = check_file_size(path)
    if not size_check["ok"]:
        if size_check["bytes"] < FILE_SIZE_MIN:
            issues.append(
                f"File is empty or too small ({size_check['bytes']} bytes); "
                f"minimum is {FILE_SIZE_MIN} bytes"
            )
        else:
            issues.append(
                f"File size too large ({size_check['bytes']} bytes); "
                f"maximum is {FILE_SIZE_MAX} bytes (~50KB)"
            )

    # --- Read content ---
    content = path.read_text(encoding="utf-8", errors="replace")

    # --- Frontmatter validity ---
    fm_valid, frontmatter, fm_error = parse_frontmatter(content)
    if not fm_valid:
        issues.append(f"Invalid YAML frontmatter: {fm_error}")

    # Fallback to empty dict if parse failed (so later checks can run)
    if frontmatter is None:
        frontmatter = {}

    # --- Artifact type ---
    artifact_type: Optional[str] = frontmatter.get("type") if frontmatter else None

    # --- Required sections ---
    sections_check = check_required_sections(content, artifact_type)
    for section in sections_check["missing"]:
        issues.append(f"Missing required section: {section}")

    # --- Cross references ---
    xref_check = check_cross_references(frontmatter)
    for ref in xref_check["missing"]:
        issues.append(f"Cross-reference not found on disk: {ref}")

    return {
        "path": str(path),
        "checks": {
            "frontmatter_valid": fm_valid,
            "required_sections": sections_check,
            "cross_references": xref_check,
            "file_size": size_check,
        },
        "issues": issues,
    }


def validate_artifacts(paths: List[Path]) -> Dict[str, Any]:
    """Validate multiple artifact files and aggregate results.

    Args:
        paths: List of Path objects to validate.

    Returns:
        Dict with 'overall' ("ok" | "warnings") and 'artifacts' list.
    """
    artifact_results = [validate_single_artifact(p) for p in paths]

    has_issues = any(len(r["issues"]) > 0 for r in artifact_results)
    overall = "warnings" if has_issues else "ok"

    return {
        "overall": overall,
        "artifacts": artifact_results,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI entry point.

    Returns:
        Exit code: 0 = all valid, 1 = warnings, 2 = error
    """
    parser = argparse.ArgumentParser(
        description="Validate post-generation artifact structure (warn-only)",
        epilog="Exit codes: 0=all valid, 1=warnings (non-blocking), 2=error (file not found)"
    )
    parser.add_argument(
        "artifact_paths",
        nargs="+",
        help="One or more artifact file paths to validate"
    )

    args = parser.parse_args()

    # Resolve paths and check existence
    paths: List[Path] = []
    missing_files: List[str] = []
    for raw in args.artifact_paths:
        p = Path(raw)
        if not p.exists():
            missing_files.append(raw)
        else:
            paths.append(p)

    # If any files are missing, report error (exit 2)
    if missing_files:
        error_output: Dict[str, Any] = {
            "overall": "errors",
            "artifacts": [
                {
                    "path": path_str,
                    "checks": {
                        "frontmatter_valid": False,
                        "required_sections": {"present": [], "missing": []},
                        "cross_references": {"found": [], "missing": []},
                        "file_size": {"bytes": 0, "ok": False},
                    },
                    "issues": [f"File not found: {path_str}"],
                }
                for path_str in missing_files
            ],
        }
        print(json.dumps(error_output, indent=2))
        return 2

    # Validate all found paths
    output = validate_artifacts(paths)
    print(json.dumps(output, indent=2))

    if output["overall"] == "ok":
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
