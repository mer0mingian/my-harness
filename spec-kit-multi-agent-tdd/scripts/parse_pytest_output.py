#!/usr/bin/env python3
"""Thin CLI wrapper around lib/parse_test_evidence.py::parse_pytest_output().

Reads pytest output from stdin or file and outputs TestEvidence as JSON.

Usage:
    pytest tests/ | python3 scripts/parse_pytest_output.py
    python3 scripts/parse_pytest_output.py --file /tmp/pytest.txt
    python3 scripts/parse_pytest_output.py --file /tmp/pytest.txt --verbose

Exit Codes:
    0: Successful parsing (GREEN state)
    1: Parse error or RED state (normal test failures)
    2: System error (file not found, BROKEN state)
"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Add lib directory to path for imports
SCRIPT_DIR = Path(__file__).parent
LIB_DIR = SCRIPT_DIR.parent / "lib"
sys.path.insert(0, str(LIB_DIR))

from parse_test_evidence import load_patterns, parse_pytest_output


def main():
    """CLI entrypoint for parse_pytest_output wrapper."""
    parser = argparse.ArgumentParser(
        description="Parse pytest output and output TestEvidence as JSON.",
        epilog="Reads from stdin by default, or from --file if specified.",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Input file containing pytest output (default: stdin)",
        default=None,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (currently unused)",
    )

    args = parser.parse_args()

    # Read input
    try:
        if args.file:
            # Read from file
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(2)

            with open(file_path, "r") as f:
                pytest_output = f.read()
        else:
            # Read from stdin
            pytest_output = sys.stdin.read()

        # Validate input is not empty
        if not pytest_output or not pytest_output.strip():
            print("Error: Empty input provided", file=sys.stderr)
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(2)

    # Load patterns
    try:
        patterns = load_patterns()
    except Exception as e:
        print(f"Error loading patterns: {e}", file=sys.stderr)
        sys.exit(2)

    # Parse pytest output
    try:
        evidence = parse_pytest_output(pytest_output, patterns)
    except Exception as e:
        print(f"Error parsing pytest output: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert TestEvidence to dict and output as JSON
    try:
        evidence_dict = asdict(evidence)
        print(json.dumps(evidence_dict, indent=2))
    except Exception as e:
        print(f"Error serializing output: {e}", file=sys.stderr)
        sys.exit(1)

    # Exit based on state
    if evidence.state == "GREEN":
        sys.exit(0)
    elif evidence.state == "RED":
        sys.exit(1)
    elif evidence.state == "BROKEN":
        sys.exit(2)
    else:
        # Unknown state - treat as error
        sys.exit(1)


if __name__ == "__main__":
    main()
