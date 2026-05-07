#!/usr/bin/env python3
"""
/speckit.multi-agent.implement Command Implementation (S4-002)

Prepares context for @make agent to implement code that passes tests.
Part of the Multi-Agent TDD workflow Phase 2.
"""

import sys
import argparse
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Add project root to sys.path for lib imports
# This allows 'from lib import artifact_paths' to work when running from commands/
script_dir = Path(__file__).parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


class EscalationError(Exception):
    """Raised for system-level issues that require escalation (exit code 2)."""
    pass

try:
    import yaml
except ImportError:
    yaml = None

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
    sys.exit(1)

# Import artifact_paths library
try:
    from lib import artifact_paths
except ImportError:
    print("Error: lib.artifact_paths not available. Check project structure.", file=sys.stderr)
    sys.exit(1)


# Module-level constants
DEFAULT_IMPLEMENTATION_AGENT = 'dev-specialist'

DEFAULT_CONFIG = {
    'agents': {'implementation_agent': DEFAULT_IMPLEMENTATION_AGENT},
    'artifacts': {
        'root': 'docs/features',
        'types': {
            'test_design': 'test-design',
            'impl_notes': 'impl-notes',
        }
    },
    'test_framework': {
        'type': 'pytest',
        'file_patterns': ['tests/**/*.py'],
    },
    'integration_checks': {
        'enabled': True,
        'commands': [
            {
                'name': 'ruff',
                'command': 'ruff check src/',
                'critical': False
            },
            {
                'name': 'mypy',
                'command': 'mypy src/',
                'critical': False
            }
        ]
    }
}


def load_config(project_root: Path) -> dict:
    """
    Load harness-tdd-config.yml from project root.

    Returns default config if file not found or YAML not installed.

    Args:
        project_root: Project root directory

    Returns:
        Configuration dictionary with agents, artifacts, test_framework settings
    """
    config_path = project_root / ".specify" / "harness-tdd-config.yml"

    if not config_path.exists():
        # Return sensible defaults
        return DEFAULT_CONFIG.copy()

    if yaml is None:
        print("Warning: PyYAML not installed, using default config", file=sys.stderr)
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or DEFAULT_CONFIG.copy()
    except yaml.YAMLError as e:
        print(f"Warning: Config malformed at {config_path}: {e}, using defaults", file=sys.stderr)
        return DEFAULT_CONFIG.copy()


def find_test_design_artifact(
    feature_id: str,
    config: dict,
    project_root: Path
) -> Path:
    """
    Find test design artifact from step 7 (test command).

    Uses artifact_paths.find_existing to search configured locations.

    Args:
        feature_id: Feature identifier
        config: Configuration dictionary
        project_root: Project root directory

    Returns:
        Path to test design artifact

    Raises:
        FileNotFoundError: If test design artifact not found
    """
    test_artifact = artifact_paths.find_existing(
        feature_id, 'test_design', config, project_root
    )

    if not test_artifact:
        raise FileNotFoundError(
            f"Test design artifact not found for {feature_id}. "
            f"Run /speckit.multi-agent.test first."
        )

    return test_artifact


def find_spec_artifact(feature_id: str, project_root: Path) -> Optional[Path]:
    """
    Find feature spec artifact in common locations.

    Searches standard spec locations without requiring configuration.

    Args:
        feature_id: Feature identifier
        project_root: Project root directory

    Returns:
        Path to spec artifact if found, None otherwise
    """
    candidates = [
        project_root / "docs" / "features" / f"{feature_id}-spec.md",
        project_root / "docs" / "features" / f"{feature_id}.md",
        project_root / "docs" / "specs" / f"{feature_id}-spec.md",
        project_root / ".specify" / "specs" / f"{feature_id}.md",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def prepare_agent_context(
    feature_id: str,
    test_artifact: Path,
    spec_artifact: Optional[Path],
    config: dict,
    project_root: Path
) -> Dict[str, Any]:
    """
    Prepare context bundle for implementation agent.

    Returns dict with paths to resources (not inline content).
    This allows the orchestrator/plugin to pass paths to the agent.

    Args:
        feature_id: Feature identifier
        test_artifact: Path to test design artifact
        spec_artifact: Path to spec artifact (optional)
        config: Configuration dictionary
        project_root: Project root directory

    Returns:
        Dictionary mapping context keys to paths/values:
        - feature_id: The feature identifier
        - test_design_path: Path to test design artifact
        - test_file_patterns: List of test file patterns from config
        - spec_path: Path to spec artifact (if available)
    """
    test_patterns = config.get('test_framework', {}).get('file_patterns', [])

    context = {
        'feature_id': feature_id,
        'test_design_path': str(test_artifact),
        'test_file_patterns': test_patterns,
    }

    if spec_artifact:
        context['spec_path'] = str(spec_artifact)

    return context


def create_implementation_notes(
    feature_id: str,
    agent_name: str,
    config: dict,
    project_root: Path,
    red_state_evidence: Optional[Dict] = None
) -> Path:
    """
    Generate implementation notes artifact from template.

    Creates a draft implementation notes artifact using Jinja2 template.
    Always creates artifact for Phase 2 simplicity.

    Args:
        feature_id: Feature identifier
        agent_name: Name of implementation agent
        config: Configuration dictionary
        project_root: Project root directory
        red_state_evidence: Optional RED state validation result to include in artifact

    Returns:
        Path to created implementation notes artifact

    Raises:
        EscalationError: If template file not found or corrupted (system issue)
        PermissionError: If cannot create output directory (escalation)
        OSError: If cannot write artifact file (escalation)
    """
    # Get template path relative to commands directory
    # commands/implement.py -> spec-kit-multi-agent-tdd/templates/
    templates_dir = Path(__file__).parent.parent / "templates"
    template_file = templates_dir / "implementation-notes-template.md"

    if not template_file.exists():
        raise EscalationError(f"Template not found: {template_file}")

    # Setup Jinja2 environment
    try:
        env = Environment(loader=FileSystemLoader(str(templates_dir)))
        template = env.get_template("implementation-notes-template.md")
    except Exception as e:
        raise EscalationError(f"Cannot load template: {e}")

    # Render template with variables
    feature_name = feature_id.replace('-', ' ').title()
    content = template.render(
        feature_id=feature_id,
        feature_name=feature_name,
        agent_name=agent_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
        status='draft',
        red_state_evidence=red_state_evidence
    )

    # Resolve output path using artifact_paths library
    output_path = artifact_paths.resolve(
        feature_id, 'impl_notes', config, project_root
    )

    # Ensure parent directory exists (permission errors are escalation)
    try:
        artifact_paths.ensure_directory(output_path)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create output directory {output_path.parent}: {e}"
        )

    # Write artifact
    try:
        output_path.write_text(content, encoding='utf-8')
    except PermissionError as e:
        raise PermissionError(
            f"Cannot write artifact to {output_path}: {e}"
        )
    except OSError as e:
        raise OSError(
            f"Cannot write artifact to {output_path}: {e}"
        )

    return output_path


def run_integration_checks(
    project_root: Path,
    config: dict,
    feature_id: str
) -> List[Dict]:
    """
    Run configured integration checks.

    Integration checks are additional quality gates that run after GREEN state
    validation passes. These include linters, type checkers, formatters, and
    security scanners. By default, failures are warnings and don't block the
    workflow, unless marked as critical.

    Args:
        project_root: Project root directory
        config: Configuration dict with integration_checks section
        feature_id: Feature identifier for context

    Returns:
        List of check results, each with:
        - name: Check name (e.g., "ruff", "mypy")
        - command: Command that was run
        - exit_code: Exit code from command
        - passed: bool (exit code == 0)
        - output: Command output (stdout + stderr)
        - critical: bool (whether failure should block workflow)

    Example:
        >>> results = run_integration_checks(
        ...     Path('/path/to/project'),
        ...     config,
        ...     'feat-auth-login'
        ... )
        >>> passed_count = sum(1 for r in results if r['passed'])
        >>> critical_failures = [r for r in results if not r['passed'] and r['critical']]
    """
    checks_config = config.get('integration_checks', {})

    if not checks_config.get('enabled', False):
        return []

    commands = checks_config.get('commands', [])
    results = []

    for check in commands:
        name = check['name']
        command = check['command']
        critical = check.get('critical', False)

        print(f"  Running {name}...", end=' ', flush=True)

        try:
            result = subprocess.run(
                command.split(),
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout per check
            )

            passed = result.returncode == 0

            results.append({
                'name': name,
                'command': command,
                'exit_code': result.returncode,
                'passed': passed,
                'output': result.stdout + result.stderr,
                'critical': critical
            })

            if passed:
                print("✓ PASS")
            else:
                if critical:
                    print("✗ FAIL (CRITICAL)")
                else:
                    print("⚠ FAIL (warning)")

        except subprocess.TimeoutExpired:
            results.append({
                'name': name,
                'command': command,
                'exit_code': -1,
                'passed': False,
                'output': f"Timeout after 60 seconds",
                'critical': critical
            })
            print("✗ TIMEOUT")

        except Exception as e:
            results.append({
                'name': name,
                'command': command,
                'exit_code': -1,
                'passed': False,
                'output': str(e),
                'critical': critical
            })
            print(f"✗ ERROR: {e}")

    return results


def update_impl_notes_with_integration_results(
    artifact_path: Path,
    integration_results: List[Dict]
) -> None:
    """
    Update implementation notes with integration check results.

    Adds a new section after the RED→GREEN Evidence section documenting
    integration validation results including pass/fail status, command
    output for failures, and overall summary.

    Args:
        artifact_path: Path to impl notes artifact
        integration_results: List of integration check results from run_integration_checks

    Raises:
        FileNotFoundError: If artifact_path does not exist
        OSError: If cannot read or write artifact file
    """
    content = artifact_path.read_text(encoding='utf-8')

    # Build integration validation section
    passed = sum(1 for r in integration_results if r['passed'])
    total = len(integration_results)

    integration_section = f"""
## Integration Validation Results

**Summary:** {passed}/{total} checks passed

| Check | Command | Status |
|-------|---------|--------|
"""

    for result in integration_results:
        status = "✓ PASS" if result['passed'] else ("✗ FAIL (CRITICAL)" if result['critical'] else "⚠ FAIL (warning)")
        integration_section += f"| {result['name']} | `{result['command']}` | {status} |\n"

    integration_section += "\n"

    # Add failed check details
    failures = [r for r in integration_results if not r['passed']]
    if failures:
        integration_section += "**Failed Checks:**\n\n"
        for result in failures:
            integration_section += f"### {result['name']}\n"
            integration_section += f"Command: `{result['command']}`\n"
            integration_section += f"Exit code: {result['exit_code']}\n"
            integration_section += f"Critical: {'Yes' if result['critical'] else 'No'}\n\n"
            integration_section += f"```\n{result['output'][:500]}\n```\n\n"

    # Insert before Notes section if it exists, otherwise append
    # This ensures it comes after GREEN State evidence
    if "## Notes" in content:
        content = content.replace("## Notes", f"{integration_section}\n## Notes")
    elif "## Refactoring" in content:
        content = content.replace("## Refactoring", f"{integration_section}\n## Refactoring")
    elif "## Integration Validation" in content:
        # Already has integration validation section (from template), replace it
        import re
        pattern = r'## Integration Validation.*?(?=## |$)'
        content = re.sub(pattern, integration_section.strip() + "\n\n", content, flags=re.DOTALL)
    else:
        content = content + "\n" + integration_section

    artifact_path.write_text(content, encoding='utf-8')


def update_impl_notes_with_green_evidence(
    artifact_path: Path,
    validation_result: Dict
) -> None:
    """
    Update implementation notes artifact with GREEN state evidence.

    Updates the existing artifact to mark it as complete and adds GREEN state
    evidence section with passing test results.

    Args:
        artifact_path: Path to impl notes artifact
        validation_result: GREEN validation result dict from validate_green_state

    Raises:
        FileNotFoundError: If artifact_path does not exist
        OSError: If cannot read or write artifact file
    """
    content = artifact_path.read_text(encoding='utf-8')

    # Update status line from 'draft' to 'complete'
    content = re.sub(
        r'\*\*Status:\*\* .*',
        '**Status:** complete',
        content
    )

    # Build GREEN evidence section
    evidence = validation_result['evidence']
    output_snippet = validation_result['output'][:500] if validation_result['output'] else ""

    green_evidence = f"""
### GREEN State (After Implementation)

**Test Success Output:**
```
{output_snippet}
```

**Passing Tests:**
- Total: {evidence.total_tests}
- Passed: {evidence.passed}
- Failed: {evidence.failed}
- Errors: {evidence.errors}

**Timestamp:** {validation_result['timestamp']}

**GREEN Validation:** YES
"""

    # Add coverage section if available
    coverage = validation_result.get('coverage')
    if coverage and coverage.get('found'):
        green_evidence += f"""
**Coverage Metrics:**
- Percentage: {coverage['percentage']}%
- Statements: {coverage['statements']}
- Missing: {coverage['missing']}
"""

    # Insert after RED State section (before next ### heading or end of file)
    # Find the RED State section and insert GREEN after it
    red_section_pattern = r'(### RED State.*?)(\n### |\Z)'
    match = re.search(red_section_pattern, content, re.DOTALL)

    if match:
        # Insert GREEN evidence after RED State section
        content = re.sub(
            red_section_pattern,
            rf'\1{green_evidence}\n\2',
            content,
            flags=re.DOTALL
        )
    else:
        # Fallback: append at end of RED→GREEN Evidence section
        evidence_pattern = r'(## RED→GREEN Evidence.*?)(\n## |\Z)'
        content = re.sub(
            evidence_pattern,
            rf'\1{green_evidence}\n\2',
            content,
            flags=re.DOTALL
        )

    artifact_path.write_text(content, encoding='utf-8')


def main():
    """
    CLI entry point for /speckit.multi-agent.implement command.

    Command flow:
    1. Load configuration
    2. Find test design artifact (required)
    3. Find spec artifact (optional)
    4. Prepare agent context
    5. Create implementation notes artifact
    6. Print instructions for agent invocation

    Exit codes:
        0: Success - context prepared, artifact created
        1: Validation error - test artifact not found, invalid feature-id
        2: Blocked/escalation - system issues (corrupt config, missing template, permission errors)
    """
    parser = argparse.ArgumentParser(
        description="Prepare implementation step of TDD workflow"
    )
    parser.add_argument(
        "feature_id",
        help="Feature identifier (e.g., 'feat-123')"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--validate-green",
        action="store_true",
        help="Validate GREEN state after implementation (skips RED validation)"
    )

    args = parser.parse_args()
    project_root = args.project_root or Path.cwd()

    try:
        # Step 1: Load config
        config = load_config(project_root)
        agent_name = config.get('agents', {}).get('implementation_agent', DEFAULT_IMPLEMENTATION_AGENT)

        # GREEN validation phase (Phase 2)
        if args.validate_green:
            print(f"\n{'='*60}")
            print("GREEN STATE VALIDATION")
            print(f"{'='*60}\n")

            from lib.test_runner import validate_green_state

            # Find existing impl notes to get baseline test count
            impl_notes_path = artifact_paths.find_existing(
                args.feature_id, 'impl_notes', config, project_root
            )

            if not impl_notes_path:
                print(f"✗ Implementation notes not found", file=sys.stderr)
                print(f"  Run without --validate-green first", file=sys.stderr)
                return 1

            # Extract baseline test count from impl notes (if available)
            baseline_test_count = None
            try:
                impl_content = impl_notes_path.read_text(encoding='utf-8')
                # Look for "Total tests: N" in RED State section
                match = re.search(r'### RED State.*?Total tests: (\d+)', impl_content, re.DOTALL)
                if match:
                    baseline_test_count = int(match.group(1))
            except Exception:
                pass  # baseline_test_count stays None

            # Validate GREEN state
            validation_result = validate_green_state(
                project_root, config, args.feature_id, baseline_test_count
            )

            print(f"Test State: {validation_result['state']}")
            print(f"Timestamp: {validation_result['timestamp']}")
            print(f"\n{validation_result['message']}\n")

            if not validation_result['validation_passed']:
                print(f"✗ GREEN state validation failed", file=sys.stderr)
                print(f"  State: {validation_result['state']}", file=sys.stderr)
                print(f"  All tests must PASS (GREEN state) after implementation", file=sys.stderr)
                print(f"\n  Evidence:", file=sys.stderr)
                print(f"    Total tests: {validation_result['evidence'].total_tests}", file=sys.stderr)
                print(f"    Passed: {validation_result['evidence'].passed}", file=sys.stderr)
                print(f"    Failed: {validation_result['evidence'].failed}", file=sys.stderr)
                print(f"    Errors: {validation_result['evidence'].errors}", file=sys.stderr)

                if validation_result['state'] == 'BROKEN':
                    return 2  # Escalation
                else:
                    return 1  # Validation failure (still RED)

            print("✓ GREEN state confirmed - implementation verified\n")

            # Run integration checks
            print(f"{'='*60}")
            print("INTEGRATION VALIDATION")
            print(f"{'='*60}\n")

            integration_results = run_integration_checks(
                project_root, config, args.feature_id
            )

            if integration_results:
                # Show summary
                passed_checks = sum(1 for r in integration_results if r['passed'])
                total_checks = len(integration_results)
                print(f"\nIntegration checks: {passed_checks}/{total_checks} passed\n")

                # Check for critical failures
                critical_failures = [r for r in integration_results if not r['passed'] and r['critical']]
                if critical_failures:
                    print(f"✗ Critical integration checks failed:", file=sys.stderr)
                    for r in critical_failures:
                        print(f"  - {r['name']}: {r['command']}", file=sys.stderr)
                    return 1  # Fail workflow on critical integration failures

                # Update impl notes with integration results
                update_impl_notes_with_integration_results(
                    impl_notes_path, integration_results
                )
            else:
                print("No integration checks configured (skipped)\n")

            # Update impl notes artifact with GREEN evidence
            update_impl_notes_with_green_evidence(
                impl_notes_path, validation_result
            )

            print(f"✓ Updated implementation notes: {impl_notes_path}\n")
            return 0

        # RED validation phase (Phase 1 - existing logic)
        print(f"Implementation workflow for: {args.feature_id}")
        print(f"Agent: {agent_name}\n")

        # Step 2: Find test design artifact
        test_artifact = find_test_design_artifact(
            args.feature_id, config, project_root
        )
        print(f"✓ Found test design: {test_artifact}")

        # Step 3: Find spec (optional)
        spec_artifact = find_spec_artifact(args.feature_id, project_root)
        if spec_artifact:
            print(f"✓ Found spec: {spec_artifact}")

        # Step 4: Prepare agent context
        context = prepare_agent_context(
            args.feature_id, test_artifact, spec_artifact, config, project_root
        )

        print(f"\n📋 Agent Context:")
        for key, value in context.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")

        # Step 4.5: TDD Entry Validation (RED state check)
        print(f"\n{'='*60}")
        print("TDD ENTRY VALIDATION")
        print(f"{'='*60}\n")

        from lib.test_runner import validate_red_state

        validation_result = validate_red_state(project_root, config, args.feature_id)

        print(f"Test State: {validation_result['state']}")
        print(f"Timestamp: {validation_result['timestamp']}")
        print(f"\n{validation_result['message']}\n")

        if not validation_result['validation_passed']:
            print(f"✗ TDD entry validation failed", file=sys.stderr)
            print(f"  State: {validation_result['state']}", file=sys.stderr)
            print(f"  Tests must be FAILING (RED state) before implementation", file=sys.stderr)
            print(f"\n  Evidence:", file=sys.stderr)
            print(f"    Total tests: {validation_result['evidence'].total_tests}", file=sys.stderr)
            print(f"    Passed: {validation_result['evidence'].passed}", file=sys.stderr)
            print(f"    Failed: {validation_result['evidence'].failed}", file=sys.stderr)
            print(f"    Errors: {validation_result['evidence'].errors}", file=sys.stderr)

            if validation_result['state'] == 'BROKEN':
                # Escalation case
                print(f"\n  Escalation required: Fix test issues before implementing", file=sys.stderr)
                return 2
            else:
                # GREEN state - validation failure
                print(f"\n  Tests already passing - no implementation needed or tests broken", file=sys.stderr)
                return 1

        print("✓ RED state confirmed - proceeding with implementation\n")

        # Step 5: Create implementation notes artifact with RED evidence
        impl_notes_path = create_implementation_notes(
            args.feature_id, agent_name, config, project_root,
            red_state_evidence=validation_result
        )
        print(f"\n✓ Created implementation notes: {impl_notes_path}")

        # Step 6: Print instructions for next step
        print(f"\n{'='*60}")
        print("NEXT STEP: Invoke implementation agent")
        print(f"{'='*60}")
        print(f"\nAgent: {agent_name}")
        print("Instructions: Implement code to make tests pass")
        print(f"Test design: {test_artifact}")
        if spec_artifact:
            print(f"Feature spec: {spec_artifact}")
        print(f"Output artifact: {impl_notes_path}")
        print(f"\nNOTE: Agent will read test files from patterns:")
        for pattern in context['test_file_patterns']:
            print(f"  - {pattern}")

        return 0

    except FileNotFoundError as e:
        # Test artifact not found = validation error (exit 1)
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1

    except EscalationError as e:
        # Escalation errors = system issues (exit 2)
        print(f"✗ Escalation: {e}", file=sys.stderr)
        return 2

    except (PermissionError, OSError) as e:
        # Permission/filesystem errors = escalation (exit 2)
        print(f"✗ Escalation: {e}", file=sys.stderr)
        return 2

    except Exception as e:
        # Unexpected errors = escalation (exit 2)
        print(f"✗ Escalation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
