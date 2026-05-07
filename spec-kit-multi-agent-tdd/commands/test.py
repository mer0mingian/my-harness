#!/usr/bin/env python3
"""
/speckit.multi-agent.test Command Implementation (S3-002)

Spawns @test-specialist agent to write tests and creates test design artifact.
Part of the Multi-Agent TDD workflow Phase 3.
"""

import sys
import os
import tempfile
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except ImportError:
    print("Error: jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
    sys.exit(1)


# Default configuration when .specify/harness-tdd-config.yml not found
DEFAULT_CONFIG = {
    'version': '1.0',
    'agents': {
        'test_agent': 'test-specialist',
        'implementation_agent': 'dev-specialist',
        'arch_reviewer': 'arch-specialist',
        'code_reviewer': 'review-specialist',
    },
    'artifacts': {
        'test_design': {
            'path': 'docs/tests/test-design/{feature_id}-test-design.md',
            'template': '.specify/templates/test-design-template.md',
            'mandatory': True,
        }
    },
    'test_framework': {
        'type': 'pytest',
        'file_patterns': [
            'tests/**/*.py',
            '**/test_*.py',
            '**/*_test.py',
        ],
        'failure_codes': {
            'valid_red': [
                'MISSING_BEHAVIOR',
                'ASSERTION_MISMATCH',
                'AssertionError',
                'NameError',
                'AttributeError',
            ],
            'invalid_escalate': [
                'TEST_BROKEN',
                'ENV_BROKEN',
                'SyntaxError',
                'ImportError',
                'ModuleNotFoundError',
            ]
        }
    }
}


def find_spec_artifact(feature_id: str, project_root: Optional[Path] = None) -> Path:
    """
    Find spec artifact for feature-id in common locations.

    Args:
        feature_id: Feature identifier (e.g., 'feat-123')
        project_root: Project root directory (defaults to CWD)

    Returns:
        Path to spec artifact

    Raises:
        FileNotFoundError: If spec not found in any candidate location
    """
    if project_root is None:
        project_root = Path.cwd()

    candidates = [
        project_root / "docs" / "features" / f"{feature_id}.md",
        project_root / "docs" / "specs" / f"{feature_id}-spec.md",
        project_root / "docs" / "specs" / f"{feature_id}.md",
        project_root / ".specify" / "specs" / f"{feature_id}.md",
    ]

    for path in candidates:
        if path.exists():
            return path

    # Build helpful error message
    checked_paths = "\n  - ".join(str(p) for p in candidates)
    raise FileNotFoundError(
        f"Spec artifact not found for feature: {feature_id}\n"
        f"Checked locations:\n  - {checked_paths}"
    )


def load_config(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load harness-tdd-config.yml from project root or use defaults.

    Args:
        project_root: Project root directory (defaults to CWD)

    Returns:
        Configuration dictionary
    """
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / ".specify" / "harness-tdd-config.yml"

    if not config_path.exists():
        print(f"INFO: Config not found at {config_path}, using defaults", file=sys.stderr)
        return DEFAULT_CONFIG.copy()

    if yaml is None:
        print("WARNING: PyYAML not installed, using defaults", file=sys.stderr)
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or DEFAULT_CONFIG.copy()
    except yaml.YAMLError as e:
        print(f"WARNING: Config malformed at {config_path}: {e}, using defaults", file=sys.stderr)
        return DEFAULT_CONFIG.copy()


def get_artifact_path(
    feature_id: str,
    config: Dict[str, Any],
    project_root: Optional[Path] = None
) -> Path:
    """
    Get test design artifact output path from config.

    Args:
        feature_id: Feature identifier
        config: Configuration dictionary
        project_root: Project root directory (defaults to CWD)

    Returns:
        Resolved Path for output artifact
    """
    if project_root is None:
        project_root = Path.cwd()

    # Read from config
    artifact_config = config.get('artifacts', {}).get('test_design', {})
    path_template = artifact_config.get(
        'path',
        'docs/tests/test-design/{feature_id}-test-design.md'
    )

    # Substitute variables
    path = path_template.format(
        feature_id=feature_id,
        timestamp=datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    )

    # Resolve relative to project root
    output_path = project_root / path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def extract_acceptance_criteria(spec_content: str) -> List[str]:
    """
    Extract AC-N items from spec markdown (case-insensitive, flexible format).

    Args:
        spec_content: Full spec file content

    Returns:
        List of acceptance criteria strings (without leading dash)
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


def build_agent_context(feature_id: str, spec_content: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build structured context for @test-specialist agent.

    Args:
        feature_id: Feature identifier
        spec_content: Full spec file content
        config: Configuration dictionary

    Returns:
        Agent context dictionary
    """
    context = {
        'feature_id': feature_id,
        'spec_content': spec_content,
        'acceptance_criteria': extract_acceptance_criteria(spec_content),
        'test_patterns': config.get('test_framework', {}).get('file_patterns', []),
        'valid_failure_codes': config.get('test_framework', {}).get('failure_codes', {}).get('valid_red', []),
        'instructions': (
            "Write failing tests (RED state) for all acceptance criteria. "
            "Tests MUST fail initially with MISSING_BEHAVIOR or ASSERTION_MISMATCH. "
            "DO NOT write implementation code."
        )
    }
    return context


def spawn_test_agent(
    feature_id: str,
    spec_content: str,
    config: Dict[str, Any],
    project_root: Optional[Path] = None
) -> int:
    """
    Spawn @test-specialist agent to write tests.

    MVP IMPLEMENTATION (Phase 2):
    - Writes context file to /tmp/ directory for agent consumption
    - Prints instructions for manual agent invocation via CLI
    - Does NOT use Claude Code Agent API (planned for Phase 3+)

    This MVP approach is intentional per spec review:
    - Spec S3-002 mentions "/agents.spawn test-specialist" as future goal
    - Phase 2 accepts context-file handoff pattern
    - Full automation via Agent API deferred to later phases

    Args:
        feature_id: Feature identifier
        spec_content: Full spec content
        config: Configuration dictionary
        project_root: Project root directory (defaults to CWD)

    Returns:
        Exit code (0 for success)
    """
    if project_root is None:
        project_root = Path.cwd()

    # Build agent context
    context = build_agent_context(feature_id, spec_content, config)

    # Format prompt
    prompt = f"""
You are @test-specialist writing tests for feature: {context['feature_id']}

SPEC CONTENT:
{context['spec_content']}

ACCEPTANCE CRITERIA:
{chr(10).join('- ' + ac for ac in context['acceptance_criteria'])}

TEST PATTERNS:
{chr(10).join('- ' + p for p in context['test_patterns'])}

VALID FAILURE CODES:
{', '.join(context['valid_failure_codes'])}

TASK:
1. Write failing tests (RED state) for all acceptance criteria
2. Use test patterns from config
3. Tests MUST fail initially (MISSING_BEHAVIOR or ASSERTION_MISMATCH)
4. DO NOT write implementation code

DELIVERABLES:
- Test files in tests/ directory
- Tests that fail with valid RED state codes
"""

    # Write context file to temp directory (portable, secure)
    # MVP: Manual cleanup after agent invocation
    fd, temp_path = tempfile.mkstemp(prefix=f"test-agent-context-{feature_id}-", suffix=".txt")
    context_file = Path(temp_path)
    os.close(fd)  # Close the file descriptor, we'll write to it later
    context_file.write_text(prompt, encoding='utf-8')

    # Print instructions for manual invocation (MVP approach)
    print(f"\n=== Agent Invocation Required ===")
    print(f"Please invoke @test-specialist agent with the following context:")
    print(f"Feature ID: {feature_id}")
    print(f"Context file: {context_file}")
    print(f"\nNOTE: This is Phase 2 MVP behavior (context-file handoff).")
    print(f"      Future phases will automate via Claude Code Agent API.")
    print(f"================================\n")

    return 0  # Success


def generate_test_design_artifact(
    feature_id: str,
    feature_name: str,
    output_path: Path,
    template_dir: Optional[Path] = None
) -> Path:
    """
    Generate test design artifact from template.

    Args:
        feature_id: Feature identifier
        feature_name: Human-readable feature name
        output_path: Where to write artifact
        template_dir: Custom template directory (optional)

    Returns:
        Path to generated artifact
    """
    # Determine template directory
    if template_dir is None or not template_dir.exists():
        # Use built-in template
        # commands/test.py -> spec-kit-multi-agent-tdd/templates/
        script_dir = Path(__file__).parent.parent
        template_dir = script_dir / "templates"

    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined
    )

    # Load template
    template = env.get_template("test-design-template.md")

    # Render with variables
    variables = {
        "feature_id": feature_id,
        "feature_name": feature_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "draft",
    }
    content = template.render(**variables)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')

    return output_path


def execute_test_command(feature_id: str, project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Execute /speckit.multi-agent.test command end-to-end.

    Args:
        feature_id: Feature identifier
        project_root: Project root directory (defaults to CWD)

    Returns:
        Result dictionary with status and artifact path

    Raises:
        FileNotFoundError: If spec not found
    """
    if project_root is None:
        project_root = Path.cwd()

    # Step 1: Find and read spec
    spec_path = find_spec_artifact(feature_id, project_root)
    spec_content = spec_path.read_text(encoding='utf-8')

    # Extract feature name from spec (first H1 heading)
    feature_name = feature_id  # Default
    for line in spec_content.split('\n'):
        if line.startswith('# '):
            feature_name = line[2:].strip()
            break

    # Step 2: Load config
    config = load_config(project_root)

    # Step 3: Determine output path
    output_path = get_artifact_path(feature_id, config, project_root)

    # Step 4: Spawn test agent
    spawn_test_agent(feature_id, spec_content, config, project_root)

    # Step 5: Generate test design artifact
    # Check for custom template
    custom_template_dir = project_root / ".specify" / "templates"
    if not custom_template_dir.exists():
        custom_template_dir = None

    artifact_path = generate_test_design_artifact(
        feature_id=feature_id,
        feature_name=feature_name,
        output_path=output_path,
        template_dir=custom_template_dir
    )

    return {
        "status": "success",
        "feature_id": feature_id,
        "spec_path": str(spec_path),
        "artifact_path": str(artifact_path),
    }


def main():
    """CLI entry point for /speckit.multi-agent.test command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Spawn @test-specialist agent and create test design artifact"
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

    try:
        result = execute_test_command(args.feature_id, args.project_root)
        print(f"\n✓ Success!")
        print(f"  Spec: {result['spec_path']}")
        print(f"  Artifact: {result['artifact_path']}")
        print(f"\nNext steps:")
        print(f"  1. Invoke @test-specialist agent with context file")
        print(f"  2. Review test design artifact")
        print(f"  3. Run tests to verify RED state")
        return 0
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
