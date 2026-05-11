#!/usr/bin/env python3
"""TDD Sequence Enforcer - PreToolUse Hook Handler.

Enforces RED before GREEN constitutional requirement by blocking implementation
code writes unless tests are in valid RED state (failing with MISSING_BEHAVIOR
or ASSERTION_MISMATCH).

Hook Type: PreToolUse
Trigger: tool == "Write" && path.startsWith("src/") || path.startsWith("app/")

Exit Codes:
    0: Allow write (valid RED state or non-source write)
    2: Block write (not in RED state, validation failed, or error)

Usage:
    echo '{"tool":"Write","args":{"file_path":"src/main.py"},"context":{"feature_id":"feat-123"}}' | \\
        python3 hooks/handlers/tdd_sequence_enforcer.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional


def read_hook_input() -> Dict[str, Any]:
    """
    Read and parse hook input from stdin.

    Returns:
        Dictionary with tool, args, and context

    Raises:
        ValueError: If input is empty or invalid JSON
    """
    input_text = sys.stdin.read()

    if not input_text or not input_text.strip():
        raise ValueError("Empty input received")

    try:
        return json.loads(input_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")


def is_source_code_write(hook_data: Dict[str, Any]) -> bool:
    """
    Detect if this is a write to source code (src/ or app/).

    Args:
        hook_data: Hook input dictionary

    Returns:
        True if writing to src/ or app/ directories
    """
    if hook_data.get("tool") != "Write":
        return False

    file_path = hook_data.get("args", {}).get("file_path", "")
    if not file_path:
        return False

    # Normalize path
    path = Path(file_path)

    # Check if writing to source directories
    parts = path.parts
    if not parts:
        return False

    # First directory component indicates source code
    source_dirs = {"src", "app", "lib"}
    return parts[0] in source_dirs


def extract_feature_id(hook_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract feature_id from hook context.

    Args:
        hook_data: Hook input dictionary

    Returns:
        Feature ID string or None if not found
    """
    context = hook_data.get("context", {})
    feature_id = context.get("feature_id")

    # Return None for empty strings
    if feature_id and isinstance(feature_id, str) and feature_id.strip():
        return feature_id.strip()

    return None


def validate_red_state(
    feature_id: str,
    project_root: Path
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate RED state by calling validate_red_state.py script.

    Args:
        feature_id: Feature identifier
        project_root: Project root directory

    Returns:
        Tuple of (is_valid, output_dict)
        - is_valid: True if valid RED state (exit code 0)
        - output_dict: Validation output or error dict
    """
    script_path = project_root / "scripts" / "validate_red_state.py"

    if not script_path.exists():
        return False, {
            "error": f"Validation script not found: {script_path}"
        }

    try:
        result = subprocess.run(
            ["python3", str(script_path), feature_id, "--project-root", str(project_root)],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        # Parse JSON output from script
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            return False, {
                "error": f"Invalid JSON from validation script: {result.stdout[:200]}"
            }

        # Exit code 0 means valid RED state
        is_valid = result.returncode == 0

        return is_valid, output

    except FileNotFoundError as e:
        return False, {
            "error": f"Script not found: {e}"
        }
    except subprocess.TimeoutExpired:
        return False, {
            "error": "Validation timed out after 60 seconds"
        }
    except Exception as e:
        return False, {
            "error": f"Validation error: {e}"
        }


def build_response(
    action: str,
    reason: str,
    validation_output: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build hook response JSON.

    Args:
        action: "allow" or "block"
        reason: Human-readable reason
        validation_output: Optional validation output dict

    Returns:
        Response dictionary
    """
    return {
        "action": action,
        "reason": reason,
        "red_state_validation": validation_output
    }


def main() -> int:
    """
    Main hook handler execution.

    Returns:
        Exit code: 0 to allow, 2 to block
    """
    try:
        # Read hook input
        hook_data = read_hook_input()

        # Check if this is a source code write
        if not is_source_code_write(hook_data):
            # Not a source write - allow without validation
            response = build_response(
                action="allow",
                reason="Not a source code write, no TDD validation needed"
            )
            print(json.dumps(response, indent=2))
            return 0

        # Source code write - need feature_id
        feature_id = extract_feature_id(hook_data)
        if not feature_id:
            # No feature_id - block
            response = build_response(
                action="block",
                reason="No feature_id provided in context. Cannot validate RED state."
            )
            print(json.dumps(response, indent=2))
            return 2

        # Validate RED state
        project_root = Path.cwd()
        is_valid, validation_output = validate_red_state(feature_id, project_root)

        if is_valid:
            # Valid RED state - allow write
            message = validation_output.get("message", "Valid RED state confirmed")
            response = build_response(
                action="allow",
                reason=message,
                validation_output=validation_output
            )
            print(json.dumps(response, indent=2))
            return 0
        else:
            # Invalid RED state or error - block write
            message = validation_output.get("message") or validation_output.get("error", "RED state validation failed")
            response = build_response(
                action="block",
                reason=message,
                validation_output=validation_output
            )
            print(json.dumps(response, indent=2))
            return 2

    except Exception as e:
        # Handle any unexpected errors
        response = build_response(
            action="block",
            reason=f"Hook handler error: {e}"
        )
        print(json.dumps(response, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
