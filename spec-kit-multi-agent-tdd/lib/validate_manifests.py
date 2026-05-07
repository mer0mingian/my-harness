#!/usr/bin/env python3
"""
Manifest Validator for Multi-Agent TDD Workflow (S2B-001)

Validates plugin.json, extension.json, agent definition files, and config YAML files
against their expected schemas. Used in CI/CD pipelines, pre-commit hooks, and
integration tests.

Usage:
    python validate_manifests.py <path> [<path> ...] [--verbose]
    python validate_manifests.py --all [--verbose]

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

import yaml

try:
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    print("Error: jsonschema library not found. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


# Schema file paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent
SCHEMAS_DIR = SCRIPT_DIR / "schemas"
PLUGIN_SCHEMA_PATH = SCHEMAS_DIR / "plugin-schema.json"
EXTENSION_SCHEMA_PATH = SCHEMAS_DIR / "extension-schema.json"


def load_json_schema(schema_path: Path) -> Dict[str, Any]:
    """Load a JSON schema from file."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file {schema_path}: {e}", file=sys.stderr)
        sys.exit(1)


def validate_plugin_manifest(path: Path) -> Dict[str, Any]:
    """
    Validate a plugin.json manifest file.

    Args:
        path: Path to plugin.json file

    Returns:
        Dict with keys:
            - valid: bool
            - errors: List[str]
            - path: str
    """
    result = {
        "valid": True,
        "errors": [],
        "path": str(path)
    }

    try:
        with open(path, 'r') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        result["valid"] = False
        result["errors"].append(f"File not found: {path}")
        return result
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
        return result

    # Validate against schema
    schema = load_json_schema(PLUGIN_SCHEMA_PATH)
    try:
        validate(instance=manifest, schema=schema)
    except ValidationError as e:
        result["valid"] = False
        # Format the error message to be more readable
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        result["errors"].append(f"Validation error at {error_path}: {e.message}")
    except SchemaError as e:
        result["valid"] = False
        result["errors"].append(f"Schema error: {e.message}")

    return result


def validate_extension_manifest(path: Path) -> Dict[str, Any]:
    """
    Validate an extension.json manifest file.

    Args:
        path: Path to extension.json file

    Returns:
        Dict with keys:
            - valid: bool
            - errors: List[str]
            - path: str
    """
    result = {
        "valid": True,
        "errors": [],
        "path": str(path)
    }

    try:
        with open(path, 'r') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        result["valid"] = False
        result["errors"].append(f"File not found: {path}")
        return result
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
        return result

    # Validate against schema
    schema = load_json_schema(EXTENSION_SCHEMA_PATH)
    try:
        validate(instance=manifest, schema=schema)
    except ValidationError as e:
        result["valid"] = False
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        result["errors"].append(f"Validation error at {error_path}: {e.message}")
    except SchemaError as e:
        result["valid"] = False
        result["errors"].append(f"Schema error: {e.message}")

    return result


def validate_agent_definition(path: Path) -> Dict[str, Any]:
    """
    Validate an agent definition .md file's frontmatter.

    Checks for required fields: name, description, mode

    Args:
        path: Path to agent .md file

    Returns:
        Dict with keys:
            - valid: bool
            - errors: List[str]
            - path: str
    """
    result = {
        "valid": True,
        "errors": [],
        "path": str(path)
    }

    try:
        with open(path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        result["valid"] = False
        result["errors"].append(f"File not found: {path}")
        return result

    # Parse frontmatter (YAML between --- delimiters)
    if not content.startswith('---'):
        result["valid"] = False
        result["errors"].append("No frontmatter found (should start with '---')")
        return result

    # Find the closing ---
    try:
        end_idx = content.index('---', 3)
        frontmatter_content = content[3:end_idx].strip()
    except ValueError:
        result["valid"] = False
        result["errors"].append("Frontmatter not properly closed (missing second '---')")
        return result

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_content)
    except yaml.YAMLError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid YAML in frontmatter: {e}")
        return result

    # Check required fields
    required_fields = ['name', 'description', 'mode']
    for field in required_fields:
        if field not in frontmatter:
            result["valid"] = False
            result["errors"].append(f"Missing required field: {field}")

    return result


def validate_config_yaml(path: Path) -> Dict[str, Any]:
    """
    Validate a config YAML file (basic structure validation).

    Checks:
        - Valid YAML syntax
        - Expected top-level keys exist: agents, quality_gates, artifact_config, workflow_config

    Args:
        path: Path to config YAML file

    Returns:
        Dict with keys:
            - valid: bool
            - errors: List[str]
            - path: str
    """
    result = {
        "valid": True,
        "errors": [],
        "path": str(path)
    }

    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        result["valid"] = False
        result["errors"].append(f"File not found: {path}")
        return result
    except yaml.YAMLError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid YAML: {e}")
        return result

    # Check expected top-level keys
    expected_keys = ['agents', 'quality_gates', 'artifact_config', 'workflow_config']
    missing_keys = []

    for key in expected_keys:
        if key not in config:
            missing_keys.append(key)

    if missing_keys:
        result["valid"] = False
        result["errors"].append(f"Missing expected top-level keys: {', '.join(missing_keys)}")

    return result


def discover_manifests(root_dir: Path) -> Dict[str, List[Path]]:
    """
    Auto-discover manifest files in the harness-tooling directory.

    Returns:
        Dict with keys:
            - plugins: List[Path] to plugin.json files
            - extensions: List[Path] to extension.json files
            - agents: List[Path] to agent .md files
    """
    manifests = {
        "plugins": [],
        "extensions": [],
        "agents": []
    }

    # Find plugin.json files
    for plugin_json in root_dir.rglob("plugin.json"):
        # Skip if in .claude/plugins/ (those are installed copies)
        if ".claude/plugins/" not in str(plugin_json):
            # Only include if it has agents (runtime plugins may not)
            try:
                with open(plugin_json, 'r') as f:
                    plugin_data = json.load(f)
                if "agents" in plugin_data:
                    manifests["plugins"].append(plugin_json)
            except (json.JSONDecodeError, FileNotFoundError):
                # Still include it for validation to catch the error
                manifests["plugins"].append(plugin_json)

    # Find extension.json files
    for extension_json in root_dir.rglob("extension.json"):
        manifests["extensions"].append(extension_json)

    # Find agent files referenced in plugins
    for plugin_path in manifests["plugins"]:
        try:
            with open(plugin_path, 'r') as f:
                plugin_data = json.load(f)

            if "agents" in plugin_data:
                plugin_dir = plugin_path.parent
                for agent_rel_path in plugin_data["agents"]:
                    agent_path = plugin_dir / agent_rel_path
                    if agent_path.exists():
                        manifests["agents"].append(agent_path)
        except (json.JSONDecodeError, FileNotFoundError):
            # Skip plugins that can't be read
            pass

    return manifests


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Validate manifest files for Multi-Agent TDD Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s plugin.json
  %(prog)s extension.json agents/test-specialist.md
  %(prog)s --all
  %(prog)s --all --verbose
        """
    )

    parser.add_argument(
        'paths',
        nargs='*',
        type=Path,
        help='Paths to manifest files to validate'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Auto-discover and validate all manifests in harness-tooling/'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show all checked files and detailed results'
    )

    args = parser.parse_args()

    # Determine what to validate
    files_to_validate = []

    if args.all:
        # Auto-discover manifests from harness-tooling root
        # Navigate up from lib/ -> spec-kit-multi-agent-tdd/ -> harness-tooling/
        root_dir = SCRIPT_DIR.parent.parent
        if args.verbose:
            print(f"Discovering manifests in {root_dir}...")

        manifests = discover_manifests(root_dir)

        for plugin_path in manifests["plugins"]:
            files_to_validate.append(("plugin", plugin_path))

        for extension_path in manifests["extensions"]:
            files_to_validate.append(("extension", extension_path))

        for agent_path in manifests["agents"]:
            files_to_validate.append(("agent", agent_path))

        if args.verbose:
            print(f"Found {len(manifests['plugins'])} plugins, "
                  f"{len(manifests['extensions'])} extensions, "
                  f"{len(manifests['agents'])} agents")
            print()

    elif args.paths:
        # Validate specified paths
        for path in args.paths:
            # Infer type from filename/extension
            if path.name == "plugin.json":
                files_to_validate.append(("plugin", path))
            elif path.name == "extension.json":
                files_to_validate.append(("extension", path))
            elif path.suffix == ".yml" or path.suffix == ".yaml":
                files_to_validate.append(("config", path))
            elif path.suffix == ".md":
                files_to_validate.append(("agent", path))
            else:
                print(f"Warning: Cannot infer type for {path}, skipping", file=sys.stderr)
    else:
        parser.print_help()
        sys.exit(1)

    # Validate all files
    all_valid = True
    results = []

    for file_type, file_path in files_to_validate:
        if args.verbose:
            print(f"Validating {file_type}: {file_path}")

        if file_type == "plugin":
            result = validate_plugin_manifest(file_path)
        elif file_type == "extension":
            result = validate_extension_manifest(file_path)
        elif file_type == "agent":
            result = validate_agent_definition(file_path)
        elif file_type == "config":
            result = validate_config_yaml(file_path)
        else:
            continue

        results.append(result)

        if not result["valid"]:
            all_valid = False

        if args.verbose or not result["valid"]:
            status = "✓ PASS" if result["valid"] else "✗ FAIL"
            print(f"  {status}: {file_path}")

            if not result["valid"]:
                for error in result["errors"]:
                    print(f"    - {error}")

    # Summary
    if args.verbose or not all_valid:
        print()

    total = len(results)
    passed = sum(1 for r in results if r["valid"])
    failed = total - passed

    print(f"Validation complete: {passed}/{total} passed, {failed}/{total} failed")

    if all_valid:
        print("All validations passed ✓")
        sys.exit(0)
    else:
        print("Some validations failed ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
