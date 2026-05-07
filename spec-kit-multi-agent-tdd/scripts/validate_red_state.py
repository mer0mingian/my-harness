#!/usr/bin/env python3
"""Standalone RED state validation script for TDD constitutional enforcement.

This script validates that tests are in valid RED state (failing correctly with
MISSING_BEHAVIOR or ASSERTION_MISMATCH) before allowing implementation work.

Exit Codes:
    0: Valid RED state (tests failing correctly)
    1: Invalid state (tests passing or no tests)
    2: System error (tests broken or pytest not available)

Usage:
    python3 scripts/validate_red_state.py feat-123
    python3 scripts/validate_red_state.py feat-123 --project-root /path/to/project
    python3 scripts/validate_red_state.py feat-123 --verbose
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import from lib modules
try:
    from lib.parse_test_evidence import parse_pytest_output, TestEvidence, load_patterns
except ImportError:
    # Try relative import if run from scripts/
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from lib.parse_test_evidence import parse_pytest_output, TestEvidence, load_patterns


def run_pytest(project_root: Path, verbose: bool = False) -> Tuple[int, str, str]:
    """
    Run pytest and capture output.

    Args:
        project_root: Project root directory
        verbose: Whether to print debug info to stderr

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    cmd = ['pytest', 'tests/', '-v', '--tb=short']

    if verbose:
        print(f"[DEBUG] Running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"[DEBUG] Working directory: {project_root}", file=sys.stderr)

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        raise FileNotFoundError("pytest not found. Install pytest: pip install pytest")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Test execution timed out after 5 minutes")


def classify_failure_codes(evidence: TestEvidence) -> List[str]:
    """
    Extract unique failure codes from test evidence.

    Args:
        evidence: TestEvidence object with test results

    Returns:
        List of unique failure codes found in failures
    """
    codes = set()
    for result in evidence.results:
        if result.failure_code:
            codes.add(result.failure_code)
    return sorted(list(codes))


def validate_red_state(
    evidence: TestEvidence,
    feature_id: str,
    verbose: bool = False
) -> Tuple[int, Dict]:
    """
    Validate that tests are in valid RED state.

    Valid RED: Tests failing with MISSING_BEHAVIOR or ASSERTION_MISMATCH
    Invalid: Tests passing (GREEN) or no tests
    Broken: Tests failing with TEST_BROKEN, ENV_BROKEN, or other errors

    Args:
        evidence: Parsed test evidence
        feature_id: Feature identifier for context
        verbose: Whether to print debug info to stderr

    Returns:
        Tuple of (exit_code, output_dict)
    """
    if verbose:
        print(f"[DEBUG] State: {evidence.state}", file=sys.stderr)
        print(f"[DEBUG] Total tests: {evidence.total_tests}", file=sys.stderr)
        print(f"[DEBUG] Failed: {evidence.failed}", file=sys.stderr)
        print(f"[DEBUG] Passed: {evidence.passed}", file=sys.stderr)

    # Extract failure codes
    failure_codes = classify_failure_codes(evidence)

    # Collect failure messages for evidence
    failure_messages = []
    for result in evidence.results:
        if result.status in ['failed', 'error'] and result.error_message:
            failure_messages.append(f"{result.name}: {result.error_message}")

    # Build base output
    output = {
        "state": evidence.state,
        "evidence": {
            "test_count": evidence.total_tests,
            "failed_count": evidence.failed + evidence.errors,
            "failure_codes": failure_codes,
            "failure_messages": failure_messages,
            "pytest_output": ""  # Will be added by caller
        },
        "validation_passed": False,
        "message": ""
    }

    # Check state and determine exit code
    if evidence.state == "GREEN":
        # Tests passing - no work needed
        output["validation_passed"] = False
        output["message"] = (
            f"Tests are passing (GREEN state). No implementation needed. "
            f"Feature: {feature_id}"
        )
        return 1, output

    elif evidence.state == "BROKEN":
        # Tests broken - escalate
        broken_codes = [code for code in failure_codes
                       if code in ['TEST_BROKEN', 'ENV_BROKEN', 'SYNTAX_ERROR', 'IMPORT_ERROR']]

        output["validation_passed"] = False
        output["message"] = (
            f"Tests are broken ({len(broken_codes)} broken failures). "
            f"Fix test environment before implementation. "
            f"Broken codes: {', '.join(broken_codes)}. "
            f"Feature: {feature_id}"
        )
        return 2, output

    elif evidence.state == "RED":
        # Check if we have valid RED failure codes
        valid_red_codes = ['MISSING_BEHAVIOR', 'ASSERTION_MISMATCH']
        has_valid_red = any(code in valid_red_codes for code in failure_codes)

        if not has_valid_red:
            # RED but no valid RED codes - invalid
            output["validation_passed"] = False
            output["message"] = (
                f"Tests failing but with unexpected codes: {', '.join(failure_codes)}. "
                f"Expected MISSING_BEHAVIOR or ASSERTION_MISMATCH. "
                f"Feature: {feature_id}"
            )
            return 1, output

        # Valid RED state
        output["validation_passed"] = True
        output["message"] = (
            f"Valid RED state confirmed ({evidence.failed} failing tests). "
            f"Ready for implementation. "
            f"Failure codes: {', '.join(failure_codes)}. "
            f"Feature: {feature_id}"
        )
        return 0, output

    else:
        # Unknown state
        output["validation_passed"] = False
        output["message"] = f"Unknown state: {evidence.state}. Feature: {feature_id}"
        return 2, output


def handle_no_tests(feature_id: str) -> Tuple[int, Dict]:
    """
    Handle case where no tests were found.

    Args:
        feature_id: Feature identifier

    Returns:
        Tuple of (exit_code, output_dict)
    """
    output = {
        "state": "NONE",
        "evidence": {
            "test_count": 0,
            "failed_count": 0,
            "failure_codes": [],
            "failure_messages": [],
            "pytest_output": ""
        },
        "validation_passed": False,
        "message": f"No tests found. Cannot validate RED state. Feature: {feature_id}"
    }
    return 1, output


def handle_pytest_error(error: Exception, feature_id: str) -> Tuple[int, Dict]:
    """
    Handle pytest execution errors.

    Args:
        error: Exception that occurred
        feature_id: Feature identifier

    Returns:
        Tuple of (exit_code, output_dict)
    """
    output = {
        "state": "ERROR",
        "evidence": {
            "test_count": 0,
            "failed_count": 0,
            "failure_codes": [],
            "failure_messages": [],
            "pytest_output": ""
        },
        "validation_passed": False,
        "message": f"System error: {str(error)}. Feature: {feature_id}"
    }

    # Determine if this is a system error (exit 2) or invalid state (exit 1)
    if isinstance(error, FileNotFoundError):
        # pytest not found - system error
        output["message"] = f"pytest not installed or not in PATH. Install with: pip install pytest. Feature: {feature_id}"
        return 2, output
    else:
        # Other error - system error
        return 2, output


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate tests are in RED state before implementation",
        epilog="Exit codes: 0=valid RED, 1=invalid state, 2=broken/system error"
    )
    parser.add_argument(
        "feature_id",
        help="Feature identifier (e.g., 'feat-123')"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print debug information to stderr"
    )

    args = parser.parse_args()

    try:
        # Load failure classification patterns
        patterns = load_patterns()

        # Run tests
        exit_code, stdout, stderr = run_pytest(args.project_root, args.verbose)

        if args.verbose:
            print(f"[DEBUG] Pytest exit code: {exit_code}", file=sys.stderr)

        # Check for no tests collected
        if "collected 0 items" in stdout or exit_code == 5:
            exit_code, output = handle_no_tests(args.feature_id)
            output["evidence"]["pytest_output"] = stdout
            print(json.dumps(output, indent=2))
            return exit_code

        # Parse pytest output
        evidence = parse_pytest_output(stdout, patterns)

        # Validate RED state
        exit_code, output = validate_red_state(evidence, args.feature_id, args.verbose)

        # Add full pytest output to evidence
        output["evidence"]["pytest_output"] = stdout

        # Output JSON to stdout
        print(json.dumps(output, indent=2))

        return exit_code

    except FileNotFoundError as e:
        exit_code, output = handle_pytest_error(e, args.feature_id)
        print(json.dumps(output, indent=2))
        return exit_code

    except Exception as e:
        if args.verbose:
            import traceback
            print("[DEBUG] Exception occurred:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

        exit_code, output = handle_pytest_error(e, args.feature_id)
        print(json.dumps(output, indent=2))
        return exit_code


if __name__ == "__main__":
    sys.exit(main())
