#!/usr/bin/env python3
"""
Tests for manifest validation script.
Following TDD: these tests are written first to define expected behavior.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

# Import the module we're testing (will be implemented after tests)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from validate_manifests import (
    validate_plugin_manifest,
    validate_extension_manifest,
    validate_agent_definition,
    validate_config_yaml,
)


class TestPluginManifestValidation:
    """Test plugin.json validation."""

    def test_valid_plugin_manifest(self):
        """Valid plugin.json passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            agents_dir = plugin_dir / "agents"
            agents_dir.mkdir()

            # Create the agent file
            agent_file = agents_dir / "test.md"
            agent_file.write_text("""---
name: test-agent
description: Test agent
mode: subagent
---

# Test Agent
""")

            # Create plugin.json
            plugin_json = plugin_dir / "plugin.json"
            valid_manifest = {
                "name": "test-plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "agents": ["agents/test.md"]
            }

            with open(plugin_json, 'w') as f:
                json.dump(valid_manifest, f)

            result = validate_plugin_manifest(plugin_json)
            assert result["valid"] is True
            assert result["errors"] == []

    def test_missing_required_fields(self):
        """Plugin manifest missing required fields fails validation."""
        invalid_manifest = {
            "name": "test-plugin",
            "version": "1.0.0"
            # Missing description and agents
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_manifest, f)
            f.flush()

            result = validate_plugin_manifest(Path(f.name))
            assert result["valid"] is False
            assert len(result["errors"]) > 0
            assert any("required" in err.lower() for err in result["errors"])

            Path(f.name).unlink()

    def test_invalid_version_format(self):
        """Plugin manifest with invalid version format fails."""
        invalid_manifest = {
            "name": "test-plugin",
            "version": "1.0",  # Invalid: should be semver
            "description": "Test plugin",
            "agents": ["agents/test.md"]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_manifest, f)
            f.flush()

            result = validate_plugin_manifest(Path(f.name))
            assert result["valid"] is False
            assert any("version" in err.lower() for err in result["errors"])

            Path(f.name).unlink()

    def test_empty_agents_array(self):
        """Plugin manifest with empty agents array fails."""
        invalid_manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "agents": []  # Empty array
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_manifest, f)
            f.flush()

            result = validate_plugin_manifest(Path(f.name))
            assert result["valid"] is False

            Path(f.name).unlink()

    def test_plugin_with_missing_agent_file(self):
        """Plugin with non-existent agent file should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            plugin_json = plugin_dir / "plugin.json"

            manifest = {
                "name": "test-plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "agents": ["agents/missing.md"]  # This file doesn't exist
            }

            with open(plugin_json, 'w') as f:
                json.dump(manifest, f)

            result = validate_plugin_manifest(plugin_json)
            assert result["valid"] is False
            assert any("Agent file not found" in e for e in result["errors"])

    def test_plugin_with_existing_agent_file(self):
        """Plugin with existing agent file should pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            agents_dir = plugin_dir / "agents"
            agents_dir.mkdir()

            # Create the agent file
            agent_file = agents_dir / "test.md"
            agent_file.write_text("""---
name: test-agent
description: Test agent
mode: subagent
---

# Test Agent
""")

            # Create plugin.json
            plugin_json = plugin_dir / "plugin.json"
            manifest = {
                "name": "test-plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "agents": ["agents/test.md"]
            }

            with open(plugin_json, 'w') as f:
                json.dump(manifest, f)

            result = validate_plugin_manifest(plugin_json)
            assert result["valid"] is True
            assert result["errors"] == []


class TestExtensionManifestValidation:
    """Test extension.json validation."""

    def test_valid_extension_manifest(self):
        """Valid extension.json passes validation."""
        valid_manifest = {
            "name": "test-extension",
            "version": "1.0.0",
            "description": "Test extension",
            "commands": ["test", "implement"]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_manifest, f)
            f.flush()

            result = validate_extension_manifest(Path(f.name))
            assert result["valid"] is True
            assert result["errors"] == []

            Path(f.name).unlink()

    def test_extension_with_optional_fields(self):
        """Extension manifest with all optional fields passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extension_dir = Path(tmpdir)
            templates_dir = extension_dir / "templates"
            templates_dir.mkdir()

            # Create extension.json
            extension_json = extension_dir / "extension.json"
            valid_manifest = {
                "name": "test-extension",
                "version": "1.0.0",
                "description": "Test extension",
                "author": "Test Author",
                "commands": ["test", "implement"],
                "templates": {
                    "directory": "templates/"
                },
                "config": {
                    "file": "config.yml",
                    "schema": "schema.json"
                },
                "hooks": {
                    "install": "hooks/install.sh"
                }
            }

            with open(extension_json, 'w') as f:
                json.dump(valid_manifest, f)

            result = validate_extension_manifest(extension_json)
            assert result["valid"] is True

    def test_missing_commands(self):
        """Extension manifest missing commands fails validation."""
        invalid_manifest = {
            "name": "test-extension",
            "version": "1.0.0",
            "description": "Test extension"
            # Missing commands
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_manifest, f)
            f.flush()

            result = validate_extension_manifest(Path(f.name))
            assert result["valid"] is False
            assert any("required" in err.lower() for err in result["errors"])

            Path(f.name).unlink()

    def test_extension_with_missing_template_directory(self):
        """Extension with non-existent template directory should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extension_dir = Path(tmpdir)
            extension_json = extension_dir / "extension.json"

            manifest = {
                "name": "test-extension",
                "version": "1.0.0",
                "description": "Test extension",
                "commands": ["test"],
                "templates": {"directory": "missing_templates/"}  # This doesn't exist
            }

            with open(extension_json, 'w') as f:
                json.dump(manifest, f)

            result = validate_extension_manifest(extension_json)
            assert result["valid"] is False
            assert any("Template directory not found" in e for e in result["errors"])

    def test_extension_with_existing_template_directory(self):
        """Extension with existing template directory should pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extension_dir = Path(tmpdir)
            templates_dir = extension_dir / "templates"
            templates_dir.mkdir()

            # Create extension.json
            extension_json = extension_dir / "extension.json"
            manifest = {
                "name": "test-extension",
                "version": "1.0.0",
                "description": "Test extension",
                "commands": ["test"],
                "templates": {"directory": "templates/"}
            }

            with open(extension_json, 'w') as f:
                json.dump(manifest, f)

            result = validate_extension_manifest(extension_json)
            assert result["valid"] is True
            assert result["errors"] == []


class TestAgentDefinitionValidation:
    """Test agent .md frontmatter validation."""

    def test_valid_agent_definition(self):
        """Valid agent definition passes validation."""
        valid_agent = """---
name: test-specialist
description: Test specialist agent for TDD workflow
mode: subagent
temperature: 0.2
---

# Test Specialist

Agent content here.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(valid_agent)
            f.flush()

            result = validate_agent_definition(Path(f.name))
            assert result["valid"] is True
            assert result["errors"] == []

            Path(f.name).unlink()

    def test_missing_required_frontmatter_fields(self):
        """Agent definition missing required fields fails validation."""
        invalid_agent = """---
name: test-specialist
mode: subagent
---

# Test Specialist
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(invalid_agent)
            f.flush()

            result = validate_agent_definition(Path(f.name))
            assert result["valid"] is False
            assert any("description" in err.lower() for err in result["errors"])

            Path(f.name).unlink()

    def test_no_frontmatter(self):
        """Agent definition without frontmatter fails validation."""
        invalid_agent = """# Test Specialist

No frontmatter here.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(invalid_agent)
            f.flush()

            result = validate_agent_definition(Path(f.name))
            assert result["valid"] is False

            Path(f.name).unlink()


class TestConfigYAMLValidation:
    """Test config YAML validation."""

    def test_valid_config_yaml(self):
        """Valid config YAML passes validation."""
        valid_config = {
            "version": "1.0",
            "agents": {
                "test_agent": "test-specialist",
                "implementation_agent": "dev-specialist"
            },
            "quality_gates": {
                "default_mode": "auto"
            },
            "artifact_config": {
                "test_design": {
                    "mandatory": True
                }
            },
            "workflow_config": {
                "parallel_enabled": False
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(valid_config, f)
            f.flush()

            result = validate_config_yaml(Path(f.name))
            assert result["valid"] is True
            assert result["errors"] == []

            Path(f.name).unlink()

    def test_invalid_yaml_syntax(self):
        """Config with invalid YAML syntax fails validation."""
        invalid_yaml = """
version: 1.0
agents:
  test_agent: test-specialist
    invalid indentation here
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()

            result = validate_config_yaml(Path(f.name))
            assert result["valid"] is False

            Path(f.name).unlink()

    def test_missing_top_level_keys(self):
        """Config missing expected top-level keys fails validation."""
        invalid_config = {
            "version": "1.0",
            "agents": {}
            # Missing quality_gates, artifact_config, workflow_config
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()

            result = validate_config_yaml(Path(f.name))
            assert result["valid"] is False
            assert any("quality_gates" in err.lower() or "artifact" in err.lower()
                      for err in result["errors"])

            Path(f.name).unlink()


class TestIntegrationWithRealFiles:
    """Integration tests with actual Phase 1 files."""

    def test_harness_agents_plugin_manifest(self):
        """Real harness-agents plugin.json passes validation."""
        plugin_path = Path("/home/minged01/repositories/harness-workplace/harness-tooling/.agents/plugins/harness-agents/plugin.json")

        if plugin_path.exists():
            result = validate_plugin_manifest(plugin_path)
            assert result["valid"] is True, f"Validation failed: {result['errors']}"

    def test_spec_kit_extension_manifest(self):
        """Real spec-kit-multi-agent-tdd extension.json passes validation."""
        extension_path = Path("/home/minged01/repositories/harness-workplace/harness-tooling/spec-kit-multi-agent-tdd/extension.json")

        if extension_path.exists():
            result = validate_extension_manifest(extension_path)
            assert result["valid"] is True, f"Validation failed: {result['errors']}"

    def test_real_agent_definitions(self):
        """All real agent definitions pass validation."""
        agents_dir = Path("/home/minged01/repositories/harness-workplace/harness-tooling/.agents/plugins/harness-agents/agents")

        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.md"))
            assert len(agent_files) == 5, f"Expected 5 agent files, found {len(agent_files)}"

            for agent_file in agent_files:
                result = validate_agent_definition(agent_file)
                assert result["valid"] is True, f"Agent {agent_file.name} failed: {result['errors']}"
