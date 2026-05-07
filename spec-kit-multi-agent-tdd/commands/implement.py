#!/usr/bin/env python3
"""
/speckit.multi-agent.implement Command Implementation (S4-002)

Prepares context for @make agent to implement code that passes tests.
Part of the Multi-Agent TDD workflow Phase 2.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional

# Add project root to sys.path for lib imports
# This allows 'from lib import artifact_paths' to work when running from commands/
script_dir = Path(__file__).parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

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
        return {
            'agents': {'implementation_agent': 'dev-specialist'},
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
            }
        }

    if yaml is None:
        print("Warning: PyYAML not installed, using default config", file=sys.stderr)
        return {
            'agents': {'implementation_agent': 'dev-specialist'},
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
            }
        }

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or {}
    except yaml.YAMLError as e:
        print(f"Warning: Config malformed at {config_path}: {e}, using defaults", file=sys.stderr)
        return {
            'agents': {'implementation_agent': 'dev-specialist'},
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
            }
        }


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
) -> Dict[str, str]:
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
    project_root: Path
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

    Returns:
        Path to created implementation notes artifact

    Raises:
        FileNotFoundError: If template file not found
    """
    # Get template path relative to commands directory
    # commands/implement.py -> spec-kit-multi-agent-tdd/templates/
    templates_dir = Path(__file__).parent.parent / "templates"
    template_file = templates_dir / "implementation-notes-template.md"

    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("implementation-notes-template.md")

    # Render template with variables
    feature_name = feature_id.replace('-', ' ').title()
    content = template.render(
        feature_id=feature_id,
        feature_name=feature_name,
        agent_name=agent_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
        status='draft'
    )

    # Resolve output path using artifact_paths library
    output_path = artifact_paths.resolve(
        feature_id, 'impl_notes', config, project_root
    )

    # Ensure parent directory exists
    artifact_paths.ensure_directory(output_path)

    # Write artifact
    output_path.write_text(content, encoding='utf-8')

    return output_path


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
        1: Error - test artifact not found or other failure
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

    args = parser.parse_args()
    project_root = args.project_root or Path.cwd()

    try:
        # Step 1: Load config
        config = load_config(project_root)
        agent_name = config.get('agents', {}).get('implementation_agent', 'dev-specialist')

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

        # Step 5: Create implementation notes artifact
        impl_notes_path = create_implementation_notes(
            args.feature_id, agent_name, config, project_root
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
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
