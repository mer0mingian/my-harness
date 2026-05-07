#!/usr/bin/env python3
"""
/speckit.multi-agent.execute Command Implementation (S3.5-001 through S3.5-005)

Orchestrates full TDD workflow by invoking subcommands sequentially.
Part of the Multi-Agent TDD workflow Phase 2.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def invoke_subcommand(
    command: str,
    feature_id: str,
    project_root: Path,
    additional_args: Optional[list] = None
) -> Dict[str, Any]:
    """
    Invoke a workflow subcommand as subprocess.

    Args:
        command: Subcommand name (test, implement, review, commit)
        feature_id: Feature identifier
        project_root: Project root directory
        additional_args: Optional additional command arguments

    Returns:
        Result dict with:
        - status: SUCCESS | FAILED | BLOCKED
        - exit_code: Process exit code
        - stdout: Standard output
        - stderr: Standard error
        - command: Full command that was executed

    Exit code mapping:
        0 -> SUCCESS
        1 -> FAILED (validation failure)
        2 -> BLOCKED (escalation required)
    """
    # Build command path
    commands_dir = Path(__file__).parent
    command_script = commands_dir / f"{command}.py"

    # Build command arguments
    cmd = [sys.executable, str(command_script), feature_id]
    if additional_args:
        cmd.extend(additional_args)

    # Execute subprocess
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True
    )

    # Map exit code to status
    status_map = {
        0: 'SUCCESS',
        1: 'FAILED',
        2: 'BLOCKED',
    }
    status = status_map.get(result.returncode, 'FAILED')

    return {
        'status': status,
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'command': ' '.join(cmd),
    }


def request_interactive_approval(
    step_name: str,
    step_result: Dict[str, Any],
    feature_id: str
) -> bool:
    """
    Request user approval to continue after a step in interactive mode.

    Args:
        step_name: Name of completed step (test, implement, review)
        step_result: Result dict from invoke_subcommand
        feature_id: Feature identifier

    Returns:
        True if user approves continuation, False to abort
    """
    print(f"\n{'='*60}")
    print(f"INTERACTIVE CHECKPOINT: {step_name.upper()} completed")
    print(f"{'='*60}")
    print(f"Feature: {feature_id}")
    print(f"Status: {step_result['status']}")
    print(f"Exit code: {step_result['exit_code']}")

    if step_result['stdout']:
        print(f"\nOutput:\n{step_result['stdout'][:500]}")  # First 500 chars

    print(f"\nContinue to next step? (y/n): ", end='', flush=True)
    response = input().strip().lower()

    return response in ['y', 'yes', '']


def execute_workflow(
    feature_id: str,
    mode: str = 'auto',
    project_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Execute full TDD workflow by orchestrating subcommands.

    Args:
        feature_id: Feature identifier
        mode: Execution mode (auto or interactive)
        project_root: Project root directory (defaults to cwd)

    Returns:
        Workflow result dict with:
        - status: COMPLETED | VALIDATION_FAILED | ESCALATION_REQUIRED | ABORTED
        - feature_id: Feature identifier
        - failed_step: Step that failed (if not completed)
        - reason: Failure/escalation reason
        - artifacts: List of generated artifacts (if completed)
    """
    if project_root is None:
        project_root = Path.cwd()

    # Define workflow steps
    steps = ['test', 'implement', 'review', 'commit']

    # Track execution
    completed_steps = []

    # Execute each step
    for step in steps:
        print(f"\n{'='*60}")
        print(f"STEP: {step.upper()}")
        print(f"{'='*60}\n")

        # Invoke subcommand
        result = invoke_subcommand(step, feature_id, project_root)

        # Check result status
        if result['status'] == 'BLOCKED':
            return {
                'status': 'ESCALATION_REQUIRED',
                'feature_id': feature_id,
                'failed_step': step,
                'reason': result['stderr'] or 'Step blocked by gate',
                'exit_code': result['exit_code'],
                'completed_steps': completed_steps,
            }

        if result['status'] == 'FAILED':
            return {
                'status': 'VALIDATION_FAILED',
                'feature_id': feature_id,
                'failed_step': step,
                'reason': result['stderr'] or 'Step validation failed',
                'exit_code': result['exit_code'],
                'completed_steps': completed_steps,
            }

        # Step succeeded
        completed_steps.append(step)

        # Interactive mode checkpoint (except after final commit step)
        if mode == 'interactive' and step != 'commit':
            approved = request_interactive_approval(step, result, feature_id)
            if not approved:
                return {
                    'status': 'ABORTED',
                    'feature_id': feature_id,
                    'failed_step': step,
                    'reason': 'User rejected continuation in interactive mode',
                    'completed_steps': completed_steps,
                }

    # All steps completed successfully
    return {
        'status': 'COMPLETED',
        'feature_id': feature_id,
        'completed_steps': completed_steps,
    }


def main():
    """CLI entry point for /speckit.multi-agent.execute command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Execute full TDD workflow (test → implement → review → commit)"
    )
    parser.add_argument(
        "feature_id",
        help="Feature identifier (e.g., 'feat-123')"
    )
    parser.add_argument(
        "--mode",
        choices=['auto', 'interactive'],
        default='auto',
        help="Execution mode (default: auto)"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()

    try:
        result = execute_workflow(
            args.feature_id,
            mode=args.mode,
            project_root=args.project_root
        )

        # Print result
        print(f"\n{'='*60}")
        print(f"WORKFLOW RESULT: {result['status']}")
        print(f"{'='*60}\n")

        if result['status'] == 'COMPLETED':
            print(f"✓ Success! Feature {result['feature_id']} workflow completed.")
            print(f"\nCompleted steps: {', '.join(result['completed_steps'])}")
            return 0

        elif result['status'] == 'ESCALATION_REQUIRED':
            print(f"✗ Escalation required at step: {result['failed_step']}", file=sys.stderr)
            print(f"\nReason: {result['reason']}", file=sys.stderr)
            print(f"\nPartial progress: {', '.join(result['completed_steps'])}", file=sys.stderr)
            return 2

        elif result['status'] == 'VALIDATION_FAILED':
            print(f"✗ Validation failed at step: {result['failed_step']}", file=sys.stderr)
            print(f"\nReason: {result['reason']}", file=sys.stderr)
            print(f"\nPartial progress: {', '.join(result['completed_steps'])}", file=sys.stderr)
            return 1

        elif result['status'] == 'ABORTED':
            print(f"✗ Workflow aborted at step: {result['failed_step']}", file=sys.stderr)
            print(f"\nReason: {result['reason']}", file=sys.stderr)
            print(f"\nPartial progress: {', '.join(result['completed_steps'])}", file=sys.stderr)
            return 1

        else:
            print(f"✗ Unknown workflow status: {result['status']}", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
