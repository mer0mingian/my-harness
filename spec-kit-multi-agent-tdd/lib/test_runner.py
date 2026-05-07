#!/usr/bin/env python3
"""Test runner for TDD workflow validation.

Provides functions to run tests and validate RED/GREEN states during the TDD cycle.
Used by implement command (S4-003) to enforce RED state before implementation.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .parse_test_evidence import parse_pytest_output, TestEvidence, load_patterns


def run_tests(
    project_root: Path,
    test_command: str = "pytest",
    test_paths: Optional[List[str]] = None
) -> Tuple[int, str, str]:
    """
    Run test command and capture output.

    Args:
        project_root: Project root directory
        test_command: Command to run (e.g., "pytest", "npm test")
        test_paths: Optional list of test paths to run (e.g., ['tests/', 'test_*.py'])

    Returns:
        Tuple of (exit_code, stdout, stderr)
        - exit_code: Test command exit code (0=success, non-zero=failures/errors)
        - stdout: Captured standard output from test execution
        - stderr: Captured standard error from test execution

    Example:
        >>> exit_code, stdout, stderr = run_tests(
        ...     Path('/path/to/project'),
        ...     'pytest',
        ...     ['tests/']
        ... )
        >>> print(f"Tests {'passed' if exit_code == 0 else 'failed'}")
    """
    # Build command
    cmd = [test_command]
    if test_paths:
        cmd.extend(test_paths)
    if test_command == "pytest":
        cmd.extend(["-v", "--tb=short"])  # Verbose, short traceback

    # Run tests
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout, result.stderr


def validate_red_state(
    project_root: Path,
    config: dict,
    feature_id: str
) -> Dict:
    """
    Validate that tests are in RED state before implementation.

    This is the TDD entry validation gate. It enforces that tests must be
    FAILING (RED state) before implementation begins. This prevents:
    - Implementing code when tests already pass (no work needed)
    - Implementing when tests are broken (fix tests first)

    Args:
        project_root: Project root directory
        config: Configuration dict with test_framework settings
        feature_id: Feature identifier for context

    Returns:
        Result dict with:
        - state: RED | GREEN | BROKEN
        - evidence: TestEvidence object with detailed test results
        - timestamp: ISO timestamp of validation
        - exit_code: Test command exit code
        - output: Full test output (stdout)
        - validation_passed: bool (True if RED, False if GREEN/BROKEN)
        - message: Human-readable result message

    Example:
        >>> result = validate_red_state(
        ...     Path('/path/to/project'),
        ...     config,
        ...     'feat-auth-login'
        ... )
        >>> if not result['validation_passed']:
        ...     print(f"Cannot proceed: {result['message']}")
        ...     sys.exit(1)
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    test_config = config.get('test_framework', {})
    test_command = test_config.get('type', 'pytest')

    # Get test paths from config
    test_patterns = test_config.get('file_patterns', ['tests/'])

    # Convert patterns to actual paths pytest can use
    # For simplicity, use 'tests/' directory if patterns include tests/**/*.py
    test_paths = []
    for pattern in test_patterns:
        if 'tests/' in pattern:
            test_paths.append('tests/')
            break
    if not test_paths:
        test_paths = test_patterns

    # Run tests
    exit_code, stdout, stderr = run_tests(project_root, test_command, test_paths)

    # Load patterns for parsing
    patterns = load_patterns()

    # Parse evidence
    evidence = parse_pytest_output(stdout, patterns)

    # Check state and build result
    if evidence.state == "GREEN":
        return {
            'state': 'GREEN',
            'evidence': evidence,
            'timestamp': timestamp,
            'exit_code': exit_code,
            'output': stdout,
            'validation_passed': False,
            'message': (
                f"Tests already passing ({evidence.passed}/{evidence.total_tests}). "
                f"No implementation needed or tests may be broken. "
                f"Feature: {feature_id}"
            )
        }
    elif evidence.state == "BROKEN":
        # Collect broken test details
        broken_tests = [
            r for r in evidence.results
            if r.failure_code in ['TEST_BROKEN', 'ENV_BROKEN']
        ]
        broken_summary = "; ".join(
            f"{r.name} ({r.failure_code})"
            for r in broken_tests[:3]  # Show first 3
        )
        if len(broken_tests) > 3:
            broken_summary += f" and {len(broken_tests) - 3} more"

        return {
            'state': 'BROKEN',
            'evidence': evidence,
            'timestamp': timestamp,
            'exit_code': exit_code,
            'output': stdout,
            'validation_passed': False,
            'message': (
                f"Tests broken ({evidence.errors} errors). "
                f"Fix test issues before implementing. "
                f"Broken: {broken_summary}. "
                f"Feature: {feature_id}"
            )
        }
    else:  # RED
        # Collect failing test summary
        failing_tests = [
            r for r in evidence.results
            if r.status == 'failed' and r.failure_code in ['MISSING_BEHAVIOR', 'ASSERTION_MISMATCH']
        ]
        failing_summary = "; ".join(
            f"{r.name} ({r.failure_code})"
            for r in failing_tests[:3]  # Show first 3
        )
        if len(failing_tests) > 3:
            failing_summary += f" and {len(failing_tests) - 3} more"

        return {
            'state': 'RED',
            'evidence': evidence,
            'timestamp': timestamp,
            'exit_code': exit_code,
            'output': stdout,
            'validation_passed': True,
            'message': (
                f"RED state validated ({evidence.failed} failing tests). "
                f"Ready for implementation. "
                f"Failing: {failing_summary}. "
                f"Feature: {feature_id}"
            )
        }
