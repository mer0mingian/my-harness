#!/usr/bin/env python3
"""
Evidence Gate Enforcer - Pre-commit hook handler.

Blocks git commits without valid evidence artifacts.
Constitutional enforcement of TDD workflow commit gate.

Hook Type: PreToolUse
Trigger: tool == "Bash" && args.command.contains("git commit")

Exit Codes:
    0: Allow commit (all evidence valid)
    2: Block commit (missing or invalid evidence)
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional


def parse_hook_input(input_str: str) -> Dict[str, Any]:
    """
    Parse JSON hook input from stdin.

    Args:
        input_str: JSON string from hook framework

    Returns:
        Parsed hook data dictionary

    Raises:
        ValueError: If input is empty or invalid JSON
    """
    if not input_str or not input_str.strip():
        raise ValueError("Empty input")

    try:
        return json.loads(input_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def is_git_commit_command(command: str) -> bool:
    """
    Check if command is a git commit command.

    Args:
        command: Shell command string

    Returns:
        True if command is git commit, False otherwise
    """
    # Match git commit with optional flags
    # Pattern: git commit (with optional leading whitespace and flags)
    pattern = r'^\s*git\s+commit\b'
    return bool(re.search(pattern, command, re.IGNORECASE))


def extract_feature_id(hook_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract feature_id from hook context or commit message.

    Extraction order:
    1. context.feature_id (highest priority)
    2. feat-XXX prefix in commit message
    3. [feat-XXX] in commit message

    Args:
        hook_data: Hook input data dictionary

    Returns:
        Feature ID string or None if not found
    """
    # Try context first
    context = hook_data.get("context", {})
    if "feature_id" in context:
        return context["feature_id"]

    # Try extracting from commit message
    command = hook_data.get("args", {}).get("command", "")

    # Extract message from git commit -m 'message' or git commit -m "message"
    # Handle both single and double quotes
    message_patterns = [
        r"-m\s+['\"]([^'\"]+)['\"]",  # -m 'message' or -m "message"
        r"-m\s+(\S+)",  # -m message (no quotes)
    ]

    message = None
    for pattern in message_patterns:
        match = re.search(pattern, command)
        if match:
            message = match.group(1)
            break

    if not message:
        return None

    # Try to extract feat-XXX from message
    # Patterns: "feat-123: message" or "[feat-123] message"
    feature_patterns = [
        r'\b(feat-\d+)\b',  # feat-123
        r'\[(feat-\d+)\]',  # [feat-123]
    ]

    for pattern in feature_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def validate_and_respond(hook_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Validate feature artifacts and generate response.

    Calls lib/validate_artifacts.py to check evidence.

    Args:
        hook_data: Hook input data

    Returns:
        Tuple of (response_dict, exit_code)
    """
    # Extract feature_id
    feature_id = extract_feature_id(hook_data)

    if not feature_id:
        response = {
            "action": "block",
            "reason": "Cannot extract feature_id from commit message or context",
            "validation_report": None,
        }
        return response, 2

    # Find validation script
    script_dir = Path(__file__).parent.parent.parent
    validation_script = script_dir / "scripts" / "validate_feature_artifacts.py"

    if not validation_script.exists():
        response = {
            "action": "block",
            "reason": f"Validation script not found: {validation_script}",
            "validation_report": None,
        }
        return response, 2

    # Call validation script
    try:
        result = subprocess.run(
            ["python3", str(validation_script), feature_id, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse validation result
        if result.returncode == 0:
            # Valid artifacts
            validation_report = json.loads(result.stdout)
            response = {
                "action": "allow",
                "reason": f"All evidence artifacts valid for {feature_id}",
                "validation_report": validation_report,
            }
            return response, 0

        elif result.returncode == 1:
            # Invalid artifacts
            validation_report = json.loads(result.stdout)
            response = {
                "action": "block",
                "reason": f"Evidence artifacts invalid for {feature_id}",
                "validation_report": validation_report,
            }
            return response, 2

        else:
            # Script error
            response = {
                "action": "block",
                "reason": f"Validation script error: {result.stderr}",
                "validation_report": None,
            }
            return response, 2

    except subprocess.TimeoutExpired:
        response = {
            "action": "block",
            "reason": "Validation script timeout",
            "validation_report": None,
        }
        return response, 2

    except Exception as e:
        response = {
            "action": "block",
            "reason": f"Validation error: {str(e)}",
            "validation_report": None,
        }
        return response, 2


def main():
    """
    Main entry point for hook handler.

    Reads hook input from stdin, validates, and outputs response to stdout.

    Exit codes:
        0: Allow commit
        2: Block commit
    """
    try:
        # Read hook input from stdin
        input_str = sys.stdin.read()

        # Parse input
        hook_data = parse_hook_input(input_str)

        # Check if this is a git commit command
        command = hook_data.get("args", {}).get("command", "")
        if not is_git_commit_command(command):
            # Not a git commit, allow through
            response = {
                "action": "allow",
                "reason": "Not a git commit command",
                "validation_report": None,
            }
            print(json.dumps(response, indent=2))
            sys.exit(0)

        # Validate and respond
        response, exit_code = validate_and_respond(hook_data)

        # Output response
        print(json.dumps(response, indent=2))
        sys.exit(exit_code)

    except ValueError as e:
        # Input parsing error
        response = {
            "action": "block",
            "reason": f"Input error: {str(e)}",
            "validation_report": None,
        }
        print(json.dumps(response, indent=2), file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        # Unexpected error
        response = {
            "action": "block",
            "reason": f"Unexpected error: {str(e)}",
            "validation_report": None,
        }
        print(json.dumps(response, indent=2), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
