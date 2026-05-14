# Plugin & Extension Registration Guide

This guide explains how to install and register harness-tooling components for different CLI ecosystems.

---

## Overview

harness-tooling provides multiple integration points:

| CLI | Integration Type | Manifest Location | Installation Method |
|-----|------------------|-------------------|---------------------|
| **Claude Code** | Plugin | `.claude-plugin/plugin.json` | `claude plugin install` |
| **SpecKit** | Extension | `spec-kit-multi-agent-tdd/extension.json` | `specify extension add` |
| **OpenCode** | Directory | `.agents/` (flat structure) | Clone repo (auto-discovers) |
| **Gemini CLI** | Extension | `.gemini/extensions/` | `gemini extensions install` (v2 planned) |

---

## Claude Code Plugin Installation

### Project-Scoped Installation (Recommended)

Install for the current project only:

```bash
cd /path/to/harness-tooling
claude plugin install ./.claude-plugin/plugin.json --scope project
```

### User-Scoped Installation

Install globally for all Claude Code sessions:

```bash
cd /path/to/harness-tooling
claude plugin install ./.claude-plugin/plugin.json --scope user
```

### Verification

```bash
claude .
# In chat session:
/agents    # Should list 5+ matd-* agents
/skills    # Should list 70+ skills
```

### Plugin Manifest Location

**Primary manifest**: `.claude-plugin/plugin.json`

This manifest references the canonical marketplace:
- Agents: `.agents/agents/`
- Skills: `.agents/skills/`
- Commands: `.agents/commands/`

**Alternative plugin**: `.agents/plugins/matd/.claude-plugin/plugin.json`

The matd-specific plugin provides the same content via relative paths (`../../../agents/`).

### Updating

```bash
git pull origin dev
# Changes take effect immediately (symlinks)
# No re-installation needed
```

---

## SpecKit Extension Installation

### Automatic Installation (via Workspace Manifest)

If your project has a `.harness.yml` file:

```yaml
plugins:
  - matd
```

The extension installs automatically when SpecKit initializes.

### Manual Installation

```bash
specify extension add harness-tdd-workflow \
  --from /path/to/harness-tooling/spec-kit-multi-agent-tdd
```

### Verification

```bash
specify extension list
# Should show: harness-tdd-workflow v1.0.0
```

### Extension Manifest Location

**Manifest**: `spec-kit-multi-agent-tdd/extension.json`

Defines:
- Commands: `test`, `implement`, `review`, `commit`, etc.
- Templates: Artifact generation templates
- Hooks: SpecKit lifecycle integration

### Updating

```bash
cd /path/to/harness-tooling
git pull origin dev
specify extension reload harness-tdd-workflow
```

---

## OpenCode Integration

### Installation

OpenCode reads directly from the flat `.agents/` directory structure. No installation needed.

```bash
# Clone repo into your project
cd /path/to/your-project
git clone <harness-tooling-url> .harness-tooling

# OpenCode auto-discovers:
# - .agents/agents/*.md
# - .agents/skills/*/SKILL.md
# - .agents/commands/*.md
```

### Verification

```bash
opencode .
# Agents/skills/commands available immediately
```

### No Manifest Required

OpenCode uses directory conventions:
- Agent files: `.agents/agents/<name>.md`
- Skill files: `.agents/skills/<name>/SKILL.md`
- Command files: `.agents/commands/<name>.md`

---

## Gemini CLI Integration (Planned v2)

### Installation (Not Yet Implemented)

```bash
cd .gemini/extensions/matd-research
gemini extensions install .
```

**Status**: Scaffolded but not implemented in v1. See `.gemini/extensions/` for placeholder structure.

---

## Troubleshooting

### "Plugin not found" (Claude Code)

**Problem**: `claude plugin install` fails with "not found"

**Solution**: Ensure you're in the harness-tooling root directory and the manifest exists:

```bash
ls ./.claude-plugin/plugin.json
# Should show: ./.claude-plugin/plugin.json
```

### "Extension not found" (SpecKit)

**Problem**: `specify extension add` fails

**Solution**: Use absolute path to extension directory:

```bash
specify extension add harness-tdd-workflow \
  --from /home/user/harness-tooling/spec-kit-multi-agent-tdd
```

### "Agent not found" (All CLIs)

**Problem**: Agent commands fail with "agent not found"

**Solution**:

For Claude Code:
```bash
# Check symlinks
ls -la .claude/agents/
# Should show symlinks to .agents/agents/*.md
```

For SpecKit:
```bash
# Ensure matd plugin is installed
claude plugin list | grep matd
```

For OpenCode:
```bash
# Check agent files exist
ls .harness-tooling/.agents/agents/
```

### "Skill not found" (All CLIs)

**Problem**: Skill references fail

**Solution**:

1. Verify skill exists:
   ```bash
   ls .agents/skills/<skill-name>/SKILL.md
   ```

2. Check frontmatter `name:` field matches directory name:
   ```bash
   grep "^name:" .agents/skills/<skill-name>/SKILL.md
   ```

---

## Plugin vs Extension: What's the Difference?

### Plugin (Claude Code)
- **Format**: JSON manifest with directory references
- **Installation**: Via `claude plugin install`
- **Discovery**: Reads directories specified in `plugin.json`
- **Namespace**: Uses agent/skill names directly

### Extension (SpecKit)
- **Format**: JSON manifest with command definitions
- **Installation**: Via `specify extension add`
- **Discovery**: Registers commands from `extension.json`
- **Namespace**: Prefixed with extension name (`/speckit.matd.*`)

### Directory Structure (OpenCode)
- **Format**: File-based conventions
- **Installation**: Git clone (no registration)
- **Discovery**: Scans `.agents/` directory tree
- **Namespace**: Uses file names directly

---

## Advanced Topics

### Creating Custom Plugins

To create a new Claude Code plugin:

1. Create plugin directory structure:
   ```bash
   mkdir -p .agents/plugins/my-plugin/.claude-plugin
   ```

2. Create `plugin.json` manifest:
   ```json
   {
     "name": "my-plugin",
     "version": "1.0.0",
     "description": "My custom plugin",
     "agents": "../../../agents/",
     "skills": "../../../skills/"
   }
   ```

3. Reference marketplace assets via relative paths to `.agents/`

See [AGENTS.md](../AGENTS.md) for full plugin architecture details.

### Creating Custom Extensions

To create a new SpecKit extension:

1. Create extension directory with `extension.json`:
   ```json
   {
     "name": "my-extension",
     "version": "1.0.0",
     "description": "My custom extension",
     "commands": {
       "my-command": {
         "file": "commands/my-command.md",
         "description": "Description"
       }
     }
   }
   ```

2. Add command implementations in `commands/` directory

3. Install via `specify extension add`

See [spec-kit-multi-agent-tdd/USER-GUIDE.md](../spec-kit-multi-agent-tdd/USER-GUIDE.md) for extension development patterns.

---

## Related Documentation

- [AGENTS.md](../AGENTS.md) - Complete plugin/extension architecture
- [README.md](../README.md#quick-install) - Quick start installation
- [spec-kit-multi-agent-tdd/USER-GUIDE.md](../spec-kit-multi-agent-tdd/USER-GUIDE.md) - SpecKit extension usage
- [.agents/README.md](../.agents/README.md) - Marketplace structure

---

**Last Updated**: 2026-05-12
**Maintainer**: harness-tooling team
