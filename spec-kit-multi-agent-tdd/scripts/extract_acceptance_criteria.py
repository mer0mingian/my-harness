#!/usr/bin/env python3
"""
Extract acceptance criteria from spec markdown.

Reads spec markdown from stdin or file and extracts AC-N items.
Outputs in JSON, list, or count format.

Exit Codes:
  0: Successfully extracted AC
  1: No AC found in input
  2: System error (file not found, parse error)

Usage:
  cat spec.md | python3 extract_acceptance_criteria.py
  python3 extract_acceptance_criteria.py --file spec.md
  python3 extract_acceptance_criteria.py --format list < spec.md
  python3 extract_acceptance_criteria.py --format count --file spec.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List


def extract_acceptance_criteria(spec_content: str) -> List[str]:
    """
    Extract AC-N items from spec markdown (case-insensitive, flexible format).

    State machine for section detection:
    1. Find "## Acceptance Criteria" or "## AC" section (H2 or H3)
    2. Extract all bullet points or numbered items
    3. Stop at next heading (##)

    Pattern matching supports:
    - Numbered lists: `1. AC-1: ...`
    - Bullet lists: `- AC-1: ...` or `* AC-1: ...`
    - Bold: `- **AC-1**: ...`
    - Plain: `- User can login`
    - Nested/indented bullets

    Args:
        spec_content: Full spec file content

    Returns:
        List of acceptance criteria strings (without leading bullet/dash)
    """
    criteria = []
    in_ac_section = False
    ac_heading_level = 0

    for line in spec_content.split('\n'):
        # Match heading like "## Acceptance Criteria" (case-insensitive, H2 or H3)
        heading_match = re.match(r'^(#{2,3})\s+acceptance\s+criteria', line, re.IGNORECASE)
        if heading_match:
            in_ac_section = True
            ac_heading_level = len(heading_match.group(1))  # Store heading level (2 or 3)
            continue

        if in_ac_section:
            # Exit on same or higher-level heading (## or # if we were in ###)
            heading_match = re.match(r'^(#{1,})\s', line)
            if heading_match and len(heading_match.group(1)) <= ac_heading_level:
                break

            # Match AC items: "- AC-1:", "* AC-2:", "  - AC-3:", "- **AC-4**:"
            ac_match = re.match(r'^\s*[-*]\s+(?:\*\*)?AC-', line)
            if ac_match:
                # Remove leading bullet/asterisk and whitespace
                cleaned = re.sub(r'^\s*[-*]\s+', '', line.strip())
                criteria.append(cleaned)

    return criteria


def format_output(criteria: List[str], format_type: str) -> str:
    """
    Format acceptance criteria based on output type.

    Args:
        criteria: List of acceptance criteria
        format_type: Output format ('json', 'list', 'count')

    Returns:
        Formatted string ready for stdout
    """
    if format_type == 'json':
        data = {
            "acceptance_criteria": criteria,
            "count": len(criteria)
        }
        return json.dumps(data, indent=2)
    elif format_type == 'list':
        return '\n'.join(criteria)
    elif format_type == 'count':
        return str(len(criteria))
    else:
        raise ValueError(f"Unknown format type: {format_type}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract acceptance criteria from spec markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cat spec.md | python3 extract_acceptance_criteria.py
  python3 extract_acceptance_criteria.py --file docs/features/feat-123.md
  python3 extract_acceptance_criteria.py --format list < spec.md
  python3 extract_acceptance_criteria.py --format count --file spec.md

Exit Codes:
  0: Successfully extracted AC
  1: No AC found in input
  2: System error (file not found, parse error)
        """
    )
    parser.add_argument(
        '--file',
        type=Path,
        default=None,
        help='Read spec from file instead of stdin'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'list', 'count'],
        default='json',
        help='Output format (default: json)'
    )

    args = parser.parse_args()

    try:
        # Read input from file or stdin
        if args.file:
            if not args.file.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                return 2
            spec_content = args.file.read_text(encoding='utf-8')
        else:
            spec_content = sys.stdin.read()

        # Check for empty input
        if not spec_content.strip():
            # Empty input - output empty result, exit 1
            criteria = []
        else:
            # Extract acceptance criteria
            criteria = extract_acceptance_criteria(spec_content)

        # Format output
        output = format_output(criteria, args.format)
        print(output)

        # Exit 1 if no AC found, 0 otherwise
        return 1 if len(criteria) == 0 else 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
