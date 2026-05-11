#!/usr/bin/env python3
"""Test Evidence Parser for Multi-Agent TDD Workflow.

Parses pytest output and extracts structured RED/GREEN state with failure
classification codes. Supports automated test evidence analysis for TDD
workflow gates (Steps 7, 8, 10).

Usage:
    pytest tests/ | python parse_test_evidence.py
    python parse_test_evidence.py --input test_output.txt
    python parse_test_evidence.py --format summary
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class TestResult:
    """Individual test result with classification."""

    __test__ = False  # Prevent pytest from collecting this as a test class

    name: str
    status: str  # "passed", "failed", "error", "skipped"
    failure_code: Optional[str]  # Classification code or None
    error_message: Optional[str]
    file_path: str
    line_number: Optional[int]


@dataclass
class TestEvidence:
    """Complete test evidence with state classification."""

    __test__ = False  # Prevent pytest from collecting this as a test class

    state: str  # "RED", "GREEN", "BROKEN"
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    results: List[TestResult]
    summary: str


def load_patterns(patterns_file: Optional[str] = None) -> Dict:
    """Load failure classification patterns from YAML config.

    Args:
        patterns_file: Path to YAML patterns file. If None, uses default.

    Returns:
        Dictionary with failure_codes and pytest_patterns.
    """
    if patterns_file is None:
        # Use default patterns file from config directory
        script_dir = Path(__file__).parent
        patterns_file = script_dir.parent / "config" / "test-patterns.yml"

    if not Path(patterns_file).exists():
        # Return default patterns if file not found
        return get_default_patterns()

    if yaml is None:
        print(
            "Warning: PyYAML not installed. Using default patterns.", file=sys.stderr
        )
        return get_default_patterns()

    with open(patterns_file, "r") as f:
        return yaml.safe_load(f)


def get_default_patterns() -> Dict:
    """Get default failure classification patterns.

    Returns:
        Dictionary with failure_codes and pytest_patterns.
    """
    return {
        "failure_codes": {
            "MISSING_BEHAVIOR": [
                r"(?i)not implemented",
                r"(?i)notimplementederror",
                r"(?i)abstractmethod",
                r"(?i)function.*has no implementation",
            ],
            "ASSERTION_MISMATCH": [
                r"(?i)assert.*failed",
                r"(?i)assertionerror",
                r"(?i)expected.*but.*got",
                r"(?i)AssertionError:",
            ],
            "TEST_BROKEN": [
                r"(?i)syntaxerror",
                r"(?i)indentationerror",
                r"(?i)nameerror",
                r"(?i)importerror",
                r"(?i)attributeerror.*test",
            ],
            "ENV_BROKEN": [
                r"(?i)modulenotfounderror",
                r"(?i)connection.*refused",
                r"(?i)permission denied",
                r"(?i)no such file or directory",
                r"(?i)timeout",
            ],
        },
        "pytest_patterns": {
            "test_line": r"^(.+\.py)::(\w+)::(\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
            "test_line_no_class": r"^(.+\.py)::(\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
            "summary_line": r"^=+ (\d+) (passed|failed|errors?|skipped)",
            "final_summary": r"^=+\s+(.+)\s+in\s+[\d\.]+s\s*=+$",
            "failure_start": r"^_+ (.+) _+$",
            "error_section": r"^=+ ERRORS =+$",
            "failure_section": r"^=+ FAILURES =+$",
            "error_message": r"^E\s+(.*)$",
            "location_line": r"^(.+\.py):(\d+):\s*(\w+)$",
            "collected": r"^collected (\d+) items?",
        },
    }


def classify_failure(error_message: str, patterns: Dict) -> str:
    """Classify failure into one of four codes.

    Args:
        error_message: Error message from test failure.
        patterns: Dictionary with failure_codes patterns.

    Returns:
        Classification code: MISSING_BEHAVIOR, ASSERTION_MISMATCH,
        TEST_BROKEN, ENV_BROKEN, or UNKNOWN.
    """
    if not error_message:
        return "UNKNOWN"

    failure_codes = patterns.get("failure_codes", {})

    # Check each failure code category in priority order
    for code in ["ENV_BROKEN", "TEST_BROKEN", "MISSING_BEHAVIOR", "ASSERTION_MISMATCH"]:
        patterns_list = failure_codes.get(code, [])
        for pattern in patterns_list:
            if re.search(pattern, error_message):
                return code

    return "UNKNOWN"


def detect_state(evidence: TestEvidence) -> str:
    """Determine RED/GREEN/BROKEN state from test evidence.

    Logic:
    - GREEN: all tests pass (passed == total_tests)
    - BROKEN: any TEST_BROKEN or ENV_BROKEN failures
    - RED: any MISSING_BEHAVIOR or ASSERTION_MISMATCH failures

    Args:
        evidence: TestEvidence object with results.

    Returns:
        State string: "RED", "GREEN", or "BROKEN".
    """
    # Check if all tests passed
    if evidence.passed == evidence.total_tests and evidence.total_tests > 0:
        return "GREEN"

    # Check for BROKEN states (highest priority)
    for result in evidence.results:
        if result.failure_code in ["TEST_BROKEN", "ENV_BROKEN"]:
            return "BROKEN"

    # Check for RED states (valid TDD failures)
    for result in evidence.results:
        if result.failure_code in ["MISSING_BEHAVIOR", "ASSERTION_MISMATCH"]:
            return "RED"

    # If we have failures but couldn't classify them, consider BROKEN
    if evidence.failed > 0 or evidence.errors > 0:
        return "BROKEN"

    # Default to GREEN (edge case: all skipped tests)
    return "GREEN"


def parse_pytest_output(output: str, patterns: Dict) -> TestEvidence:
    """Parse pytest output and extract structured test evidence.

    Args:
        output: Raw pytest output string.
        patterns: Dictionary with failure_codes and pytest_patterns.

    Returns:
        TestEvidence object with parsed results and state.
    """
    lines = output.split("\n")
    results: List[TestResult] = []
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    total_tests = 0

    # Extract test patterns
    pytest_patterns = patterns.get("pytest_patterns", {})
    test_line_pattern = pytest_patterns.get("test_line", "")
    test_line_no_class_pattern = pytest_patterns.get("test_line_no_class", "")
    final_summary_pattern = pytest_patterns.get("final_summary", "")
    location_pattern = pytest_patterns.get("location_line", "")
    error_msg_pattern = pytest_patterns.get("error_message", "")

    # First pass: collect test results
    current_failure = None
    failure_lines = []
    in_failure_section = False
    in_summary_section = False

    for line in lines:
        line = line.rstrip()

        # Try matching test result line with class first
        match = re.match(test_line_pattern, line) if test_line_pattern else None
        if match:
            file_path, class_name, test_name, status = match.groups()
            full_name = f"{class_name}::{test_name}"
            status_lower = status.lower()

            results.append(
                TestResult(
                    name=full_name,
                    status=status_lower,
                    failure_code=None,
                    error_message=None,
                    file_path=file_path,
                    line_number=None,
                )
            )
            continue

        # Try matching test result line without class
        match = re.match(test_line_no_class_pattern, line) if test_line_no_class_pattern else None
        if match:
            file_path, test_name, status = match.groups()
            status_lower = status.lower()

            results.append(
                TestResult(
                    name=test_name,
                    status=status_lower,
                    failure_code=None,
                    error_message=None,
                    file_path=file_path,
                    line_number=None,
                )
            )
            continue

        # Track "short test summary info" section
        if re.match(r"^=+ short test summary info =+$", line):
            in_summary_section = True
            in_failure_section = False
            # Process any pending failure
            if current_failure and failure_lines:
                _process_failure(current_failure, failure_lines, results, patterns)
                current_failure = None
                failure_lines = []
            continue

        # Parse short summary lines (FAILED/ERROR lines with full test names)
        if in_summary_section:
            # Match: FAILED tests/test_auth.py::test_logout - AssertionError: ...
            # Match: ERROR tests/test_api.py::test_create_user - ModuleNotFoundError: ...
            summary_match = re.match(
                r"^(FAILED|ERROR)\s+(.+?)\s+-\s+(.+)$", line
            )
            if summary_match:
                status, full_test_name, error_msg = summary_match.groups()
                status_lower = status.lower()

                # Extract file path and test name
                if "::" in full_test_name:
                    parts = full_test_name.split("::")
                    file_path = parts[0]
                    test_name = "::".join(parts[1:])
                else:
                    file_path = full_test_name
                    test_name = full_test_name

                # Check if we already have this test in results
                existing = None
                for r in results:
                    if r.name == test_name or full_test_name.endswith(r.name):
                        existing = r
                        break

                if not existing:
                    # Add new result
                    results.append(
                        TestResult(
                            name=test_name,
                            status=status_lower,
                            failure_code=classify_failure(error_msg, patterns),
                            error_message=error_msg,
                            file_path=file_path,
                            line_number=None,
                        )
                    )
                else:
                    # Update existing result
                    existing.status = status_lower
                    existing.error_message = error_msg
                    existing.failure_code = classify_failure(error_msg, patterns)
                continue

        # Track failure sections
        section_pattern = pytest_patterns.get('failure_section', r"^=+ FAILURES =+$")
        error_section_pattern = pytest_patterns.get('error_section', r"^=+ ERRORS =+$")
        if re.match(section_pattern, line) or re.match(error_section_pattern, line):
            in_failure_section = True
            in_summary_section = False
            continue

        # Detect failure/error section start
        failure_start_pattern = pytest_patterns.get('failure_start', r"^_+ .+ _+$")
        if in_failure_section and re.match(failure_start_pattern, line):
            # Save previous failure if any
            if current_failure and failure_lines:
                _process_failure(current_failure, failure_lines, results, patterns)

            # Start new failure
            current_failure = line
            failure_lines = []
            continue

        # Collect failure details
        if in_failure_section and current_failure:
            failure_lines.append(line)

        # Parse final summary line (more flexible matching)
        if final_summary_pattern and re.match(final_summary_pattern, line):
            match = re.match(final_summary_pattern, line)
            if match and match.groups():
                summary_text = match.group(1)
                _parse_summary_counts(summary_text, counts)

    # Process last failure if any
    if current_failure and failure_lines:
        _process_failure(current_failure, failure_lines, results, patterns)

    # Calculate totals
    total_tests = sum(counts.values())

    # If no summary found, count from results
    if total_tests == 0 and results:
        for result in results:
            status = result.status
            if status == "passed":
                counts["passed"] += 1
            elif status == "failed":
                counts["failed"] += 1
            elif status == "error":
                counts["errors"] += 1
            elif status == "skipped":
                counts["skipped"] += 1
        total_tests = len(results)

    # Create evidence object
    evidence = TestEvidence(
        state="",  # Will be set by detect_state
        total_tests=total_tests,
        passed=counts["passed"],
        failed=counts["failed"],
        errors=counts["errors"],
        skipped=counts["skipped"],
        results=results,
        summary="",  # Will be generated
    )

    # Detect state
    evidence.state = detect_state(evidence)

    # Generate summary
    parts = []
    if counts["passed"] > 0:
        parts.append(f"{counts['passed']} passed")
    if counts["failed"] > 0:
        parts.append(f"{counts['failed']} failed")
    if counts["errors"] > 0:
        parts.append(f"{counts['errors']} error")
    if counts["skipped"] > 0:
        parts.append(f"{counts['skipped']} skipped")

    evidence.summary = f"{total_tests} tests: {', '.join(parts)} (state: {evidence.state})"

    return evidence


def _parse_summary_counts(summary_text: str, counts: Dict[str, int]):
    """Parse summary line and update counts dictionary."""
    # Match patterns like "3 passed, 1 failed, 1 error in 0.12s"
    # Note: pytest emits plural "errors" but we store as "errors" key
    for match in re.finditer(r"(\d+)\s+(passed|failed|errors?|skipped)", summary_text):
        count, status = match.groups()
        # Normalize "error" or "errors" to "errors" key
        if status in ("error", "errors"):
            counts["errors"] = int(count)
        else:
            counts[status] = int(count)


def _process_failure(
    failure_header: str, failure_lines: List[str], results: List[TestResult], patterns: Dict
):
    """Process a failure section and update the corresponding test result."""
    # Extract test name from header
    test_name_match = re.match(r"^_+ (.+) _+$", failure_header)
    if not test_name_match:
        return

    test_name = test_name_match.group(1).strip()

    # Find matching result
    result = None
    for r in results:
        # Use exact match first, then suffix match (::test_name)
        if r.name == test_name or r.name.endswith(f"::{test_name}"):
            result = r
            break

    if not result:
        return

    # Extract error message and location
    error_messages = []
    location_line = None
    error_type = None

    for line in failure_lines:
        # Extract error message lines (start with E)
        error_match = re.match(patterns.get("pytest_patterns", {}).get("error_message", ""), line)
        if error_match:
            error_messages.append(error_match.group(1))

        # Extract location line
        location_match = re.match(
            patterns.get("pytest_patterns", {}).get("location_line", ""), line
        )
        if location_match:
            file_path, line_num, error_type = location_match.groups()
            location_line = int(line_num)
            result.file_path = file_path
            result.line_number = location_line

    # Combine error messages
    full_error_msg = " ".join(error_messages) if error_messages else None

    # If no error message extracted, try to find error type in location line
    if not full_error_msg and error_type:
        full_error_msg = error_type

    result.error_message = full_error_msg

    # Classify failure
    if full_error_msg:
        result.failure_code = classify_failure(full_error_msg, patterns)


def format_summary(evidence: TestEvidence) -> str:
    """Format test evidence as human-readable summary.

    Args:
        evidence: TestEvidence object.

    Returns:
        Formatted summary string.
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"TEST EVIDENCE SUMMARY")
    lines.append("=" * 60)
    lines.append(f"State: {evidence.state}")
    lines.append(f"Total Tests: {evidence.total_tests}")
    lines.append(f"  Passed: {evidence.passed}")
    lines.append(f"  Failed: {evidence.failed}")
    lines.append(f"  Errors: {evidence.errors}")
    lines.append(f"  Skipped: {evidence.skipped}")
    lines.append("")

    if evidence.results:
        lines.append("Test Results:")
        lines.append("-" * 60)
        for result in evidence.results:
            status_icon = {
                "passed": "✓",
                "failed": "✗",
                "error": "⚠",
                "skipped": "○",
            }.get(result.status, "?")

            line = f"{status_icon} {result.name} ({result.status})"

            if result.failure_code:
                line += f" - {result.failure_code}"

            lines.append(line)

            if result.error_message:
                lines.append(f"  Error: {result.error_message}")

            if result.file_path:
                location = result.file_path
                if result.line_number:
                    location += f":{result.line_number}"
                lines.append(f"  Location: {location}")

            lines.append("")

    lines.append("=" * 60)
    lines.append(evidence.summary)
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI entrypoint for test evidence parser."""
    parser = argparse.ArgumentParser(
        description="Parse pytest output and extract structured test evidence."
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Input file containing pytest output (default: stdin)",
        default=None,
    )
    parser.add_argument(
        "--patterns",
        "-p",
        help="YAML file with custom patterns (default: config/test-patterns.yml)",
        default=None,
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    # Load patterns
    try:
        patterns = load_patterns(args.patterns)
    except Exception as e:
        print(f"Error loading patterns: {e}", file=sys.stderr)
        patterns = get_default_patterns()

    # Read input
    if args.input:
        try:
            with open(args.input, "r") as f:
                pytest_output = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(3)
    else:
        pytest_output = sys.stdin.read()

    # Parse output
    try:
        evidence = parse_pytest_output(pytest_output, patterns)
    except Exception as e:
        print(f"Error parsing pytest output: {e}", file=sys.stderr)
        sys.exit(3)

    # Format output
    if args.format == "json":
        # Convert to JSON-serializable dict
        evidence_dict = asdict(evidence)
        print(json.dumps(evidence_dict, indent=2))
    else:  # summary
        print(format_summary(evidence))

    # Exit code based on state
    exit_codes = {"GREEN": 0, "RED": 1, "BROKEN": 2}
    sys.exit(exit_codes.get(evidence.state, 3))


if __name__ == "__main__":
    main()
