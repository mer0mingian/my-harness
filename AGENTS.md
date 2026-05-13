# Agent and Plugin Architecture

This document clarifies the marketplace structure and the different integration points for agent-based workflows.

---

## Repository Purpose

**harness-tooling** is the **canonical source** for:
- Skills (70+ reusable expertise modules)
- Agents (specialized AI personas)
- Commands (workflow entry points)
- Plugins (bundled integrations)
- Workflow extensions (CLI-specific integrations)

It serves **multiple agent CLI ecosystems**:
- **Claude Code** - Via plugin manifest (`.claude-plugin/plugin.json`)
- **OpenCode** - Via flat `.agents/` directory structure
- **Gemini CLI** - Via extensions in `.gemini/` (v2 planned)
- **SpecKit** - Via extension system (`spec-kit-multi-agent-tdd/`)

---

## Directory Structure

```
harness-tooling/
├── .agents/                          # Canonical marketplace (all CLIs)
│   ├── agents/                       # 5+ specialized agents
│   ├── skills/                       # 70+ reusable skills
│   ├── commands/                     # Workflow commands
│   └── plugins/                      # Plugin bundles
│
├── .claude-plugin/
│   └── plugin.json                   # Main Claude Code plugin manifest
│
├── spec-kit-multi-agent-tdd/         # SpecKit extension
│   ├── extension.json                # SpecKit extension manifest
│   ├── commands/                     # SpecKit command implementations
│   └── templates/                    # Artifact templates
│
└── .gemini/                          # Gemini CLI extensions (v2)
```

---

## MATD: Two Integration Paths

This repository provides **two distinct artifacts** for the MATD (Multi-Agent Test-Driven Development) workflow:

### 1. matd Claude Code Plugin

**Location**: `.agents/plugins/matd/` or `.claude-plugin/plugin.json`

**Installation**:
```bash
claude plugin install ./.claude-plugin/plugin.json --scope project
```

**Commands**: `/matd-01-specification`, `/matd-02-design`, `/matd-03-refine`, `/matd-04-implement`

**Target**: Claude Code users in harness sandbox or standalone projects

### 2. matd SpecKit Extension

**Location**: `spec-kit-multi-agent-tdd/`

**Installation**:
```bash
specify extension add harness-tdd-workflow --from /path/to/spec-kit-multi-agent-tdd
```

**Commands**: `/speckit.matd.test`, `/speckit.matd.implement`, `/speckit.matd.review`, etc.

**Target**: Teams using SpecKit for specification-driven development

### Key Differences

| Aspect | Claude Code Plugin | SpecKit Extension |
|--------|-------------------|-------------------|
| **Integration** | Claude Code marketplace | SpecKit CLI |
| **Namespace** | `/matd-*` | `/speckit.matd.*` |
| **Artifacts** | OpenSpec directory | SpecKit templates |
| **Installation** | `claude plugin install` | `specify extension add` |

Both share the same MATD methodology (specialized agents, TDD cycle, C4 architecture) but serve different workflows.

---

## Agent Roles

The MATD workflow uses 6 specialized agents:

| Agent | Role | Location |
|-------|------|----------|
| `matd-orchestrator` | PM Coordinator | `.agents/agents/matd-orchestrator.md` |
| `matd-specifier` | Requirements Engineer | `.agents/agents/matd-specifier.md` |
| `matd-critical-thinker` | Red Team Validator | `.agents/agents/matd-critical-thinker.md` |
| `matd-architect` | Solution Designer | `.agents/agents/matd-architect.md` |
| `matd-qa` | Test Architect | `.agents/agents/matd-qa.md` |
| `matd-dev` | Implementation Engineer | `.agents/agents/matd-dev.md` |

**Agent definitions** live in `.agents/agents/` and contain:
- Full role description and responsibilities
- Skill assignments
- Permission constraints
- Temperature and mode settings

See individual agent files for complete details.

---

## Marketplace Plugin System

### What are Plugins?

Plugins are **self-contained directories** under `.agents/plugins/` that bundle related skills, agents, commands, or MCP servers with metadata.

### Available Plugins

| Plugin | Purpose |
|--------|---------|
| **matd** | MATD workflow for Claude Code |
| **harness-cgc-skill** | CodeGraphContext integration |
| **harness-workflow-runtime** | Workflow state management |
| **harness-management-tools** | Plugin/extension creation and management |

### Plugin vs Extension

**Plugin** (`.agents/plugins/matd/`):
- Claude Code-specific packaging
- References marketplace assets via relative paths
- Installed via `claude plugin install`

**Extension** (`spec-kit-multi-agent-tdd/`):
- SpecKit-specific packaging
- Self-contained with own commands and templates
- Installed via `specify extension add`

---

## Development and Maintenance

### Where Changes Go

| Change Type | Location |
|-------------|----------|
| New skills | `.agents/skills/<skill-name>/` |
| New agents | `.agents/agents/<agent-name>.md` |
| Claude Code commands | `.agents/commands/<command-name>.md` |
| SpecKit commands | `spec-kit-multi-agent-tdd/commands/<command>.md` |
| Plugin metadata | `.agents/plugins/<plugin>/.claude-plugin/plugin.json` |
| Extension metadata | `spec-kit-multi-agent-tdd/extension.json` |

### Updating Plugins

```bash
# Add new agent to marketplace
cd .agents/agents
vim matd-new-role.md

# Plugin.json automatically includes all agents/ via directory reference
# No manifest update needed

# Verify
git pull origin dev  # Changes take effect immediately via symlinks
```

### Updating Extensions

```bash
# Add new SpecKit command
cd spec-kit-multi-agent-tdd/commands
vim new-command.md

# Register in extension.json
cd ..
vim extension.json  # Add to "commands": { ... }

# Reload
specify extension reload harness-tdd-workflow
```

---

## Choosing the Right Integration

### Use matd Claude Code Plugin When:
- Working in Claude Code sessions
- Using harness sandbox environment
- Need marketplace skill library integration
- Want `/matd-*` workflow commands

### Use matd SpecKit Extension When:
- Project is SpecKit-enabled (`specify init` was run)
- Following SpecKit artifact conventions
- Need `/speckit.matd.*` command namespace
- Team standardizes on `specify` CLI

### Can Both Coexist?
Yes. A project can have both:
- `.harness.yaml` referencing the matd plugin (for Claude Code)
- `.specify/extensions/harness-tdd-workflow` (for SpecKit)

They operate independently and can complement each other.

---

## Summary

- **harness-tooling** maintains skills, agents, and commands for multiple CLI ecosystems
- **matd Claude Code plugin** packages marketplace assets for Claude Code sessions
- **matd SpecKit extension** provides SpecKit CLI integration with its own implementation
- Both share the same MATD methodology but serve different workflows
- Choose based on your primary CLI tool (Claude Code vs SpecKit)
- Both can coexist in a project for teams using multiple tools

---

## Related Documentation

- **Quick Start**: [README.md](README.md#quick-install)
- **Complete Registration Guide**: [docs/PLUGIN_REGISTRATION_GUIDE.md](docs/PLUGIN_REGISTRATION_GUIDE.md)
- **SpecKit Usage**: [spec-kit-multi-agent-tdd/USER-GUIDE.md](spec-kit-multi-agent-tdd/USER-GUIDE.md)
- **Architecture Details**: [docs/marketplace/plans/harness-v1-master-plan.md](docs/marketplace/plans/harness-v1-master-plan.md)

---

**Last Updated:** 2026-05-12  
**Maintainer:** harness-tooling team
