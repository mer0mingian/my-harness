#!/usr/bin/env python3
"""Standalone GREEN state validation script for TDD constitutional enforcement.

This script validates that tests are in valid GREEN state (all passing) after
implementation work. Complements validate_red_state.py for TDD cycle completion.

Exit Codes:
    0: Valid GREEN state (all tests passing)
    1: Still failing (tests not all passing yet)
    2: System error (tests broken, pytest not available, regression detected)

Usage:
    python3 scripts/validate_green_state.py feat-123
    python3 scripts/validate_green_state.py feat-123 --project-root /path/to/project
    python3 scripts/validate_green_state.py feat-123 --baseline-count 5
    python3 scripts/validate_green_state.py feat-123 --verbose
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
    # Build command - include coverage if src/ directory exists
    cmd = ['pytest', 'tests/', '-v', '--tb=short']

    # Add coverage if src/ directory exists
    src_path = project_root / 'src'
    if src_path.exists() and src_path.is_dir():
        cmd.extend(['--cov=src', '--cov-report=term'])

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


def extract_coverage_metrics(test_output: str) -> Optional[Dict]:
    """
    Extract coverage metrics from test output.

    Looks for pytest-cov output patterns in test output and extracts
    coverage percentage and statement counts if available.

    Args:
        test_output: Test command stdout

    Returns:
        Dict with coverage metrics if found, None otherwise

    Example output:
        {
            'percentage': 85,
            'statements': 120,
            'missing': 18,
            'found': True
        }
    """
    if not test_output:
        return None

    # Look for pytest-cov coverage line:
    # TOTAL                                     120     18    85%
    import re

    # Pattern for pytest-cov total line
    # Format: "TOTAL <spaces> statements missing percentage"
    pattern = r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%'
    match = re.search(pattern, test_output)

    if match:
        statements = int(match.group(1))
        missing = int(match.group(2))
        percentage = int(match.group(3))

        return {
            'percentage': percentage,
            'statements': statements,
            'missing': missing,
            'found': True
        }

    return None


def validate_green_state(
    evidence: TestEvidence,
    feature_id: str,
    baseline_count: Optional[int] = None,
    coverage: Optional[Dict] = None,
    verbose: bool = False
) -> Tuple[int, Dict]:
    """
    Validate that tests are in valid GREEN state.

    Valid GREEN: All tests passing
    Still failing: Tests still failing (RED)
    Broken: Tests failing with TEST_BROKEN, ENV_BROKEN, or import/syntax errors

    Args:
        evidence: Parsed test evidence
        feature_id: Feature identifier for context
        baseline_count: Expected test count from RED phase (for regression detection)
        coverage: Optional coverage metrics dict
        verbose: Whether to print debug info to stderr

    Returns:
        Tuple of (exit_code, output_dict)
    """
    if verbose:
        print(f"[DEBUG] State: {evidence.state}", file=sys.stderr)
        print(f"[DEBUG] Total tests: {evidence.total_tests}", file=sys.stderr)
        print(f"[DEBUG] Failed: {evidence.failed}", file=sys.stderr)
        print(f"[DEBUG] Passed: {evidence.passed}", file=sys.stderr)
        if baseline_count:
            print(f"[DEBUG] Baseline count: {baseline_count}", file=sys.stderr)

    # Extract coverage percentage
    coverage_pct = coverage.get('percentage') if coverage else None

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
            "passed_count": evidence.passed,
            "failed_count": evidence.failed + evidence.errors,
            "coverage": coverage_pct,
            "failure_messages": failure_messages,
            "pytest_output": ""  # Will be added by caller
        },
        "validation_passed": False,
        "regression_detected": False,
        "message": ""
    }

    # Check for regression (tests deleted)
    if baseline_count and evidence.total_tests < baseline_count:
        output["regression_detected"] = True
        output["validation_passed"] = False
        output["message"] = (
            f"Regression detected: test count decreased from {baseline_count} to {evidence.total_tests}. "
            f"Tests may have been deleted. "
            f"Feature: {feature_id}"
        )
        return 2, output

    # Check state and determine exit code
    if evidence.state == "BROKEN":
        # Tests broken - escalate
        broken_tests = [
            r for r in evidence.results
            if r.failure_code in ['TEST_BROKEN', 'ENV_BROKEN', 'SYNTAX_ERROR', 'IMPORT_ERROR']
        ]
        broken_summary = "; ".join(
            f"{r.name} ({r.failure_code})"
            for r in broken_tests[:3]
        )
        if len(broken_tests) > 3:
            broken_summary += f" and {len(broken_tests) - 3} more"

        output["validation_passed"] = False
        output["message"] = (
            f"Tests are broken ({len(broken_tests)} broken failures). "
            f"Fix test environment before completing implementation. "
            f"Broken: {broken_summary}. "
            f"Feature: {feature_id}"
        )
        return 2, output

    elif evidence.state == "RED":
        # Still failing - not done yet
        failing_tests = [r for r in evidence.results if r.status == 'failed']
        failing_summary = "; ".join(
            f"{r.name} ({r.failure_code or 'UNKNOWN'})"
            for r in failing_tests[:3]
        )
        if len(failing_tests) > 3:
            failing_summary += f" and {len(failing_tests) - 3} more"

        output["validation_passed"] = False
        output["message"] = (
            f"Tests still failing ({evidence.failed} failures, {evidence.errors} errors). "
            f"Implementation incomplete. "
            f"Failing: {failing_summary}. "
            f"Feature: {feature_id}"
        )
        return 1, output

    elif evidence.state == "GREEN":
        # Valid GREEN state
        coverage_msg = ""
        if coverage_pct is not None:
            coverage_msg = f" Coverage: {coverage_pct}%."

        baseline_msg = ""
        if baseline_count:
            if evidence.total_tests > baseline_count:
                baseline_msg = f" (baseline: {baseline_count} tests, added {evidence.total_tests - baseline_count})"
            elif evidence.total_tests == baseline_count:
                baseline_msg = f" (baseline: {baseline_count} tests)"

        output["validation_passed"] = True
        output["message"] = (
            f"Valid GREEN state confirmed ({evidence.total_tests} tests passing). "
            f"Implementation complete.{coverage_msg}{baseline_msg} "
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
            "passed_count": 0,
            "failed_count": 0,
            "coverage": None,
            "failure_messages": [],
            "pytest_output": ""
        },
        "validation_passed": False,
        "regression_detected": False,
        "message": f"No tests found. Cannot validate GREEN state. Feature: {feature_id}"
    }
    return 2, output


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
            "passed_count": 0,
            "failed_count": 0,
            "coverage": None,
            "failure_messages": [],
            "pytest_output": ""
        },
        "validation_passed": False,
        "regression_detected": False,
        "message": f"System error: {str(error)}. Feature: {feature_id}"
    }

    # Determine if this is a system error (exit 2)
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
        description="Validate tests are in GREEN state after implementation",
        epilog="Exit codes: 0=valid GREEN, 1=still failing, 2=broken/system error/regression"
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
        "--baseline-count",
        type=int,
        default=None,
        help="Expected test count from RED phase (for regression detection)"
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

        # Extract coverage metrics
        coverage = extract_coverage_metrics(stdout)

        # Validate GREEN state
        exit_code, output = validate_green_state(
            evidence,
            args.feature_id,
            baseline_count=args.baseline_count,
            coverage=coverage,
            verbose=args.verbose
        )

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
