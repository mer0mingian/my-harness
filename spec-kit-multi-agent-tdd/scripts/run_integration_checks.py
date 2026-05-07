#!/usr/bin/env python3
"""
Integration Checks Runner (Phase 3, Task 1)

Execute integration checks (ruff, mypy, etc.) with timeout.
Quality gate for implementation phase.

Exit Codes:
    0: All passed
    1: Non-critical checks failed
    2: Critical checks failed

Usage:
    python3 scripts/run_integration_checks.py [project_root] [--timeout SECONDS]

Examples:
    # Run checks with default timeout (60s)
    python3 scripts/run_integration_checks.py

    # Run checks with custom timeout
    python3 scripts/run_integration_checks.py --timeout 30

    # Run checks on specific project
    python3 scripts/run_integration_checks.py /path/to/project

Configuration:
    Checks are configured in .specify/harness-tdd-config.yml:

    integration_checks:
      commands:
        - name: ruff
          cmd: "ruff check src/"
          critical: false
        - name: mypy
          cmd: "mypy src/"
          critical: true

Output:
    JSON to stdout with check results and summary:
    {
      "checks": [
        {
          "name": "ruff",
          "status": "passed",
          "critical": false,
          "output": "...",
          "exit_code": 0
        }
      ],
      "all_passed": true,
      "critical_failed": false
    }
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path for lib imports
script_dir = Path(__file__).parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import yaml
except ImportError:
    yaml = None


DEFAULT_CONFIG = {
    "integration_checks": {
        "enabled": False,
        "commands": []
    }
}


def load_config(project_root: Path) -> dict:
    """
    Load harness-tdd-config.yml from project root.

    Args:
        project_root: Project root directory

    Returns:
        Configuration dictionary with integration_checks section
    """
    config_path = project_root / ".specify" / "harness-tdd-config.yml"

    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    if yaml is None:
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or DEFAULT_CONFIG.copy()
    except yaml.YAMLError:
        return DEFAULT_CONFIG.copy()


def execute_check(
    check_config: Dict[str, Any],
    project_root: Path,
    timeout: int
) -> Dict[str, Any]:
    """
    Execute a single integration check.

    Args:
        check_config: Check configuration with name, cmd, critical
        project_root: Project root directory to run command in
        timeout: Timeout in seconds

    Returns:
        Check result dict with:
        - name: Check name
        - status: "passed" | "failed" | "skipped"
        - critical: bool
        - output: Command output
        - exit_code: Exit code
    """
    name = check_config["name"]
    cmd = check_config["cmd"]
    critical = check_config.get("critical", False)

    result = {
        "name": name,
        "status": "failed",
        "critical": critical,
        "output": "",
        "exit_code": -1
    }

    try:
        proc = subprocess.run(
            cmd.split(),
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        result["exit_code"] = proc.returncode
        result["output"] = (proc.stdout + proc.stderr).strip()

        if proc.returncode == 0:
            result["status"] = "passed"
        else:
            result["status"] = "failed"

    except subprocess.TimeoutExpired:
        result["status"] = "failed"
        result["output"] = f"Command timed out after {timeout} seconds"
        result["exit_code"] = -1

    except (FileNotFoundError, OSError) as e:
        # Tool not found or not executable
        if "No such file or directory" in str(e) or "Not a directory" in str(e):
            result["status"] = "skipped"
            result["output"] = f"Tool '{cmd.split()[0]}' not found"
            result["exit_code"] = -1
        else:
            result["status"] = "failed"
            result["output"] = f"Error executing check: {str(e)}"
            result["exit_code"] = -1

    except Exception as e:
        result["status"] = "failed"
        result["output"] = f"Error executing check: {str(e)}"
        result["exit_code"] = -1

    return result


def run_all_checks(
    project_root: Path,
    config: dict,
    timeout: int
) -> List[Dict[str, Any]]:
    """
    Run all configured integration checks.

    Args:
        project_root: Project root directory
        config: Configuration dict with integration_checks section
        timeout: Timeout in seconds per check

    Returns:
        List of check result dicts
    """
    checks_config = config.get("integration_checks", {})
    commands = checks_config.get("commands", [])

    results = []
    for check in commands:
        result = execute_check(check, project_root, timeout)
        results.append(result)

    return results


def classify_results(results: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Classify check results.

    Args:
        results: List of check result dicts

    Returns:
        Summary dict with:
        - all_passed: bool
        - critical_failed: bool
    """
    # Filter out skipped checks
    active_results = [r for r in results if r["status"] != "skipped"]

    if not active_results:
        return {
            "all_passed": True,
            "critical_failed": False
        }

    all_passed = all(r["status"] == "passed" for r in active_results)

    critical_failed = any(
        r["status"] == "failed" and r["critical"]
        for r in active_results
    )

    return {
        "all_passed": all_passed,
        "critical_failed": critical_failed
    }


def determine_exit_code(summary: Dict[str, bool]) -> int:
    """
    Determine exit code from summary.

    Args:
        summary: Summary dict from classify_results

    Returns:
        Exit code (0, 1, or 2)
    """
    if summary["all_passed"]:
        return 0
    elif summary["critical_failed"]:
        return 2
    else:
        return 1


def format_output(results: List[Dict[str, Any]]) -> str:
    """
    Format results as JSON string.

    Args:
        results: List of check result dicts

    Returns:
        JSON string
    """
    summary = classify_results(results)

    output = {
        "checks": results,
        "all_passed": summary["all_passed"],
        "critical_failed": summary["critical_failed"]
    }

    return json.dumps(output, indent=2)


def main() -> int:
    """
    CLI entry point.

    Returns:
        Exit code (0, 1, or 2)
    """
    parser = argparse.ArgumentParser(
        description="Run integration checks with timeout"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=None,
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds per check (default: 60)"
    )

    args = parser.parse_args()
    project_root = args.project_root or Path.cwd()

    # Load configuration
    config = load_config(project_root)

    # Run all checks
    results = run_all_checks(project_root, config, timeout=args.timeout)

    # Output JSON
    output = format_output(results)
    print(output)

    # Determine exit code
    summary = classify_results(results)
    exit_code = determine_exit_code(summary)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
