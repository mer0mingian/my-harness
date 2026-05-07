#!/usr/bin/env python3
"""
Artifact Template Generator

Renders Jinja2 templates with variable substitution for automated artifact creation.
Part of the Multi-Agent TDD workflow Phase 2.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
except ImportError:
    print("Error: jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None  # Optional dependency


def get_template_directory() -> Path:
    """
    Get the templates directory relative to this script.

    Returns:
        Path to templates directory
    """
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / "templates"
    return template_dir


def get_available_templates(template_dir: Optional[Path] = None) -> List[str]:
    """
    List all available template files (excluding README and non-template files).

    Args:
        template_dir: Directory containing templates (default: auto-detect)

    Returns:
        List of template names (without .md extension)
    """
    if template_dir is None:
        template_dir = get_template_directory()

    if not template_dir.exists():
        return []

    templates = []
    for template_file in template_dir.glob("*.md"):
        # Exclude README files and other non-template patterns
        if template_file.stem.upper() == "README":
            continue

        templates.append(template_file.stem)

    return sorted(templates)


def render_template(
    template_name: str,
    variables: Dict[str, Any],
    template_dir: Optional[Path] = None
) -> str:
    """
    Render a Jinja2 template with provided variables.

    Args:
        template_name: Name of template (without .md extension)
        variables: Dictionary of variables for substitution
        template_dir: Directory containing templates (default: auto-detect)

    Returns:
        Rendered template content

    Raises:
        TemplateNotFound: If template doesn't exist
        Exception: If required variables are missing
    """
    if template_dir is None:
        template_dir = get_template_directory()

    if not template_dir.exists():
        raise FileNotFoundError(
            f"Template directory not found: {template_dir}\n"
            f"Expected structure: {template_dir.parent}/templates/"
        )

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,  # Raise error on undefined variables
        autoescape=False,  # We're rendering Markdown, not HTML
    )

    # Load and render template
    try:
        template = env.get_template(f"{template_name}.md")
    except TemplateNotFound:
        available = get_available_templates(template_dir)
        raise TemplateNotFound(
            f"Template '{template_name}' not found in {template_dir}\n"
            f"Available templates: {', '.join(available)}"
        )

    try:
        rendered = template.render(**variables)
        return rendered
    except Exception as e:
        # Provide helpful error message for missing variables
        if "undefined" in str(e).lower():
            raise Exception(
                f"Template rendering failed: {e}\n"
                f"Ensure all required variables are provided.\n"
                f"Provided variables: {', '.join(variables.keys())}"
            )
        raise


def validate_output_path(output_path: Path) -> Path:
    """
    Validate and prepare output path, creating directories as needed.

    Args:
        output_path: Path where artifact will be written

    Returns:
        Validated output path

    Raises:
        ValueError: If path validation fails
    """
    # Convert to Path object if string
    output_path = Path(output_path)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def parse_custom_variables(var_args: List[str]) -> Dict[str, str]:
    """
    Parse custom variable arguments in key=value format.

    Args:
        var_args: List of strings in "key=value" format

    Returns:
        Dictionary of parsed variables

    Raises:
        ValueError: If format is invalid
    """
    variables = {}

    for var_arg in var_args:
        if "=" not in var_arg:
            raise ValueError(
                f"Invalid variable format: '{var_arg}'\n"
                f"Expected format: key=value"
            )

        # Split on first equals to handle values containing =
        key, value = var_arg.split("=", 1)
        variables[key] = value

    return variables


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file (default: harness-tdd-config.yml)

    Returns:
        Configuration dictionary (or empty dict if no config found)
    """
    if config_path is None:
        script_dir = Path(__file__).parent
        config_path = script_dir.parent / "harness-tdd-config.yml"

    if not config_path.exists():
        return {}

    if yaml is None:
        print(
            f"Warning: PyYAML not installed, cannot load config from {config_path}",
            file=sys.stderr
        )
        return {}

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config or {}
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}", file=sys.stderr)
        return {}


def check_file_exists(output_path: Path, force: bool) -> bool:
    """
    Check if output file exists and handle overwrite logic.

    Args:
        output_path: Path to check
        force: If True, overwrite without prompting

    Returns:
        True if should proceed, False otherwise
    """
    if not output_path.exists():
        return True

    if force:
        return True

    # Prompt user
    response = input(f"File exists: {output_path}\nOverwrite? [y/N]: ")
    return response.lower() in ('y', 'yes')


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate artifacts from Jinja2 templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s test-design feat-123 "User Login" --agent test-specialist
  %(prog)s workflow-summary feat-123 "User Login" --output ./artifacts/
  %(prog)s arch-review feat-456 "Payment API" --var status=draft --var version=2.0
  %(prog)s --list
        """
    )

    # Template listing
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available templates and exit"
    )

    # Required positional arguments (unless --list is used)
    parser.add_argument(
        "template_name",
        nargs="?",
        help="Name of template (without .md extension)"
    )
    parser.add_argument(
        "feature_id",
        nargs="?",
        help="Feature identifier (e.g., feat-123)"
    )
    parser.add_argument(
        "feature_name",
        nargs="?",
        help="Human-readable feature name"
    )

    # Optional arguments
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: ./artifacts/<feature-id>-<template>.md)"
    )
    parser.add_argument(
        "--agent",
        default="orchestrator",
        help="Agent name (default: orchestrator)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Config file path (default: ../harness-tdd-config.yml)"
    )
    parser.add_argument(
        "--var",
        action="append",
        default=[],
        dest="custom_vars",
        help="Custom variable in key=value format (can be used multiple times)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting"
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        help="Template directory (default: auto-detect)"
    )

    return parser


def main() -> int:
    """
    Main CLI entrypoint.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Handle --list flag
    if args.list:
        template_dir = args.template_dir or get_template_directory()
        templates = get_available_templates(template_dir)

        if not templates:
            print(f"No templates found in {template_dir}", file=sys.stderr)
            return 1

        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        return 0

    # Validate required arguments
    if not args.template_name or not args.feature_id or not args.feature_name:
        parser.error("template_name, feature_id, and feature_name are required (unless using --list)")

    try:
        # Load configuration
        config = load_config(args.config)

        # Build variables dictionary
        variables = {
            "feature_id": args.feature_id,
            "feature_name": args.feature_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent_name": args.agent,
            "version": config.get("version", "1.0"),
        }

        # Add custom variables
        if args.custom_vars:
            custom_vars = parse_custom_variables(args.custom_vars)
            variables.update(custom_vars)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            output_dir = Path(config.get("artifacts_dir", "./artifacts"))
            output_path = output_dir / f"{args.feature_id}-{args.template_name}.md"

        # Validate output path
        output_path = validate_output_path(output_path)

        # Check if file exists
        if not check_file_exists(output_path, args.force):
            print("Aborted.", file=sys.stderr)
            return 1

        # Render template
        template_dir = args.template_dir or get_template_directory()
        rendered = render_template(args.template_name, variables, template_dir)

        # Write output
        output_path.write_text(rendered)

        print(f"✓ Artifact generated: {output_path}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
