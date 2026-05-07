#!/usr/bin/env python3
"""
File Gate Enforcer Hook Handler

PreToolUse hook that blocks non-test files during test phase.
Constitutional enforcement - prevents implementation code from being written before tests exist.

Hook Type: PreToolUse (triggers before Write tool executes)
Trigger Condition: tool == "Write" && phase == "test"

Input (JSON from stdin):
{
  "tool": "Write",
  "args": {
    "file_path": "/path/to/file.py",
    "content": "..."
  },
  "phase": "test"
}

Output (JSON to stdout):
{
  "action": "allow" | "block",
  "reason": "Human-readable explanation"
}

Exit Codes:
- 0: Allow write (file matches test pattern)
- 2: Block write (file does not match test pattern)
- 1: Error (malformed input)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


# Default test file patterns
DEFAULT_TEST_PATTERNS = [
    "tests/**/*.py",
    "test_*.py",
    "*_test.py"
]


def load_test_patterns() -> List[str]:
    """
    Load test file patterns from config.

    Returns default patterns if config not available.

    Returns:
        List of glob patterns for test files
    """
    # Try to load from config
    try:
        project_root = Path.cwd()
        config_path = project_root / ".specify" / "harness-tdd-config.yml"

        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    patterns = config.get('test_framework', {}).get('file_patterns', DEFAULT_TEST_PATTERNS)
                    return patterns
            except ImportError:
                # YAML not available, use defaults
                pass
            except Exception:
                # Error loading config, use defaults
                pass
    except Exception:
        # Any error, use defaults
        pass

    return DEFAULT_TEST_PATTERNS


def matches_test_pattern(file_path: str, patterns: List[str]) -> bool:
    """
    Check if file path matches any test pattern.

    Uses pathlib.Path.match() for glob pattern matching.
    Supports both relative and absolute paths.

    Args:
        file_path: Path to file being written
        patterns: List of glob patterns (e.g., "tests/**/*.py")

    Returns:
        True if file matches any pattern, False otherwise
    """
    path = Path(file_path)

    for pattern in patterns:
        # Try matching against the full path
        if path.match(pattern):
            return True

        # Also try matching just the filename for patterns like "test_*.py"
        if path.name and Path(path.name).match(pattern):
            return True

        # For patterns like "tests/**/*.py", check if path contains tests/ directory
        if "tests/" in pattern or "tests\\" in pattern:
            # Check if the path contains tests directory anywhere
            if "tests" in path.parts or "tests" in str(path):
                # Further validate it matches the pattern structure
                try:
                    if path.match(pattern):
                        return True
                    # Try relative match from tests directory
                    parts = path.parts
                    if "tests" in parts:
                        tests_idx = parts.index("tests")
                        rel_path = Path(*parts[tests_idx:])
                        if rel_path.match(pattern):
                            return True
                except (ValueError, IndexError):
                    pass

    return False


def main():
    """
    Main hook handler entry point.

    Reads JSON from stdin, validates file path against test patterns,
    outputs JSON decision, and exits with appropriate code.
    """
    try:
        # Read hook context from stdin
        hook_input = json.load(sys.stdin)

        # Extract fields
        tool = hook_input.get("tool")
        args = hook_input.get("args", {})
        file_path = args.get("file_path", "")
        phase = hook_input.get("phase", "")

        # Only enforce during test phase
        if phase != "test":
            output = {
                "action": "allow",
                "reason": f"Not in test phase (current phase: {phase or 'none'})"
            }
            print(json.dumps(output))
            sys.exit(0)

        # Load test patterns from config
        patterns = load_test_patterns()

        # Check if file matches test patterns
        if matches_test_pattern(file_path, patterns):
            output = {
                "action": "allow",
                "reason": f"File matches test pattern: {file_path}"
            }
            print(json.dumps(output))
            sys.exit(0)
        else:
            output = {
                "action": "block",
                "reason": (
                    f"Cannot write non-test file during test phase. "
                    f"File '{file_path}' does not match any test patterns: {patterns}. "
                    f"Only test files can be created during test phase."
                )
            }
            print(json.dumps(output))
            sys.exit(2)

    except json.JSONDecodeError as e:
        error_output = {
            "action": "block",
            "reason": f"Invalid JSON input: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        error_output = {
            "action": "block",
            "reason": f"Hook error: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
