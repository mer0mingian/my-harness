#!/usr/bin/env python3
"""Generate escalation report for BROKEN tests.

Maps failure codes (TEST_BROKEN, ENV_BROKEN, IMPORT_ERROR, SYNTAX_ERROR) to
root causes and actionable recommendations for manual intervention.

Usage:
    cat evidence.json | python3 escalate_broken_tests.py
    python3 escalate_broken_tests.py --file evidence.json
    python3 escalate_broken_tests.py --file evidence.json --format human

Exit Codes:
    0: Escalation report generated
    1: No broken tests (no escalation needed)
    2: System error (invalid input, file not found, etc.)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


# Failure code to diagnosis/recommendation mapping
ESCALATION_MAP = {
    "TEST_BROKEN": {
        "diagnosis": "Syntax error or invalid test code",
        "recommendation": "Review test file, fix syntax errors"
    },
    "ENV_BROKEN": {
        "diagnosis": "Test environment configuration issue",
        "recommendation": "Check dependencies, virtual environment, pytest installation"
    },
    "IMPORT_ERROR": {
        "diagnosis": "Module import failed",
        "recommendation": "Verify imports, check PYTHONPATH, install missing packages"
    },
    "SYNTAX_ERROR": {
        "diagnosis": "Python syntax error in test or source",
        "recommendation": "Fix syntax error, run linter"
    }
}


def extract_root_causes(evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract root causes from TestEvidence.

    Args:
        evidence: TestEvidence dictionary

    Returns:
        List of root cause dictionaries with code, diagnosis, recommendation, affected_tests
    """
    # Group failures by failure_code
    failures_by_code: Dict[str, List[Dict[str, Any]]] = {}

    for result in evidence.get("results", []):
        if result.get("status") == "failed":
            failure_code = result.get("failure_code")

            # Map known broken codes (handle both formats)
            if failure_code in ["TEST_BROKEN", "ENV_BROKEN", "IMPORT_ERROR", "SYNTAX_ERROR"]:
                if failure_code not in failures_by_code:
                    failures_by_code[failure_code] = []
                failures_by_code[failure_code].append(result)

    # Build root causes
    root_causes = []
    for code, failures in failures_by_code.items():
        mapping = ESCALATION_MAP.get(code, {
            "diagnosis": "Unknown failure type",
            "recommendation": "Review test output for details"
        })

        root_cause = {
            "code": code,
            "diagnosis": mapping["diagnosis"],
            "recommendation": mapping["recommendation"],
            "affected_tests": [f["name"] for f in failures]
        }
        root_causes.append(root_cause)

    return root_causes


def generate_escalation_report(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Generate escalation report from TestEvidence.

    Args:
        evidence: TestEvidence dictionary

    Returns:
        Escalation report dictionary
    """
    root_causes = extract_root_causes(evidence)

    if not root_causes:
        # No broken tests
        return {
            "escalation_required": False,
            "failure_codes": [],
            "root_causes": [],
            "summary": "No broken tests - no escalation required"
        }

    failure_codes = [rc["code"] for rc in root_causes]
    total_broken = sum(len(rc["affected_tests"]) for rc in root_causes)

    return {
        "escalation_required": True,
        "failure_codes": failure_codes,
        "root_causes": root_causes,
        "summary": f"{total_broken} tests broken - manual intervention required"
    }


def format_human_readable(report: Dict[str, Any]) -> str:
    """Format escalation report as human-readable text.

    Args:
        report: Escalation report dictionary

    Returns:
        Human-readable string
    """
    if not report["escalation_required"]:
        return "No escalation required - all tests in valid state\n"

    lines = ["=" * 60]
    lines.append("ESCALATION REQUIRED")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Summary: {report['summary']}")
    lines.append("")
    lines.append("Broken Tests by Failure Code:")
    lines.append("")

    for root_cause in report["root_causes"]:
        lines.append(f"[{root_cause['code']}]")
        lines.append(f"  Root Cause: {root_cause['diagnosis']}")
        lines.append(f"  Recommendation: {root_cause['recommendation']}")
        lines.append(f"  Affected Tests:")
        for test_name in root_cause["affected_tests"]:
            lines.append(f"    - {test_name}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0=success, 1=no escalation, 2=error)
    """
    parser = argparse.ArgumentParser(
        description="Generate escalation report for broken tests"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to TestEvidence JSON file (default: stdin)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    try:
        # Read TestEvidence
        if args.file:
            if not args.file.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                return 2
            evidence_json = args.file.read_text()
        else:
            evidence_json = sys.stdin.read()

        # Parse JSON
        try:
            evidence = json.loads(evidence_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            return 2

        # Generate report
        report = generate_escalation_report(evidence)

        # Output
        if args.format == "human":
            output = format_human_readable(report)
            print(output)
        else:
            print(json.dumps(report, indent=2))

        # Exit code based on escalation status
        if report["escalation_required"]:
            return 0  # Success - escalation report generated
        else:
            return 1  # No escalation needed

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
