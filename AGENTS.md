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
│   ├── plugins/                      # Plugin bundles
│   │   ├── matd/                     # MATD Claude Code plugin
│   │   │   └── .claude-plugin/
│   │   │       └── plugin.json       # References agents/ and skills/
│   │   ├── harness-cgc-skill/        # CodeGraphContext integration
│   │   └── harness-workflow-runtime/ # Workflow state management
│   └── configs/
│       └── bundles.yaml              # Named skill/agent bundles
│
├── .claude/                          # Claude Code symlink structure
│   ├── .claude-plugin/
│   │   └── plugin.json               # Main plugin manifest
│   ├── agents/ → .agents/agents/     # Symlinks for Claude Code
│   └── skills/ → .agents/skills/
│
├── spec-kit-multi-agent-tdd/         # SpecKit extension (separate integration)
│   ├── extension.json                # SpecKit extension manifest
│   ├── commands/                     # SpecKit command implementations
│   ├── templates/                    # Artifact templates
│   └── hooks/                        # SpecKit lifecycle hooks
│
└── .gemini/                          # Gemini CLI extensions (v2)
    └── extensions/
        └── matd-research/
```

---

## The Two "matd" Artifacts

### 1. matd Claude Code Plugin (`.agents/plugins/matd/`)

**What it is:** A Claude Code plugin that bundles MATD agents and skills from the marketplace.

**Manifest:** `.agents/plugins/matd/.claude-plugin/plugin.json`
```json
{
  "name": "matd",
  "version": "1.0.0",
  "description": "Multi-Agent Test-Driven Development workflow for SpecKit",
  "agents": "../../../agents/",
  "skills": "../../../skills/"
}
```

**How it works:**
- References the shared `.agents/agents/` and `.agents/skills/` directories
- When installed via marketplace manifest, expands to include all matd-* agents
- Commands available: `/matd-01-specification`, `/matd-02-design`, `/matd-03-refine`, `/matd-04-implement`

**Installation:**
```yaml
# .harness.yaml (marketplace manifest)
plugins:
  - matd
```

**Usage:**
```bash
# In Claude Code session
/matd-01-specification "Add user authentication"
/agents    # Lists matd-orchestrator, matd-architect, etc.
```

**Target audience:** Claude Code users in harness sandbox or standalone projects

---

### 2. matd SpecKit Extension (`spec-kit-multi-agent-tdd/`)

**What it is:** A SpecKit CLI extension implementing the MATD workflow with PRIES methodology.

**Manifest:** `spec-kit-multi-agent-tdd/extension.json`
```json
{
  "name": "harness-tdd-workflow",
  "version": "1.0.0",
  "description": "MATD workflow commands and artifact templates for SpecKit",
  "commands": {
    "test": { "file": "commands/test.md", ... },
    "execute": { "file": "commands/execute.md", ... },
    ...
  }
}
```

**How it works:**
- Standalone extension for SpecKit CLI (`specify` command)
- Has its own command implementations (not shared with Claude Code plugin)
- Uses SpecKit template system for artifact generation
- Hooks into SpecKit lifecycle (init, plan, analyze, etc.)

**Installation:**
```bash
# Via SpecKit extension manager
specify extension add harness-tdd-workflow --from /path/to/harness-tooling/spec-kit-multi-agent-tdd
```

**Usage:**
```bash
# In SpecKit-enabled project
/speckit.matd.test feat-001
/speckit.matd.execute feat-001 --mode=auto
/speckit.matd.specify-product-brief feat-001
```

**Target audience:** Teams using SpecKit for specification-driven development

---

## Relationship Between the Two

### Shared Concepts
- Both implement **Multi-Agent Test-Driven Development**
- Both use specialized agent roles (Orchestrator, Architect, QA, Dev, Specifier, Critical Thinker)
- Both follow RED → GREEN → REFACTOR TDD cycle
- Both use C4 architecture model for progressive disclosure

### Differences

| Aspect | matd Claude Code Plugin | matd SpecKit Extension |
|--------|------------------------|------------------------|
| **Integration Point** | Claude Code marketplace | SpecKit extension system |
| **Command Namespace** | `/matd-*` | `/speckit.matd.*` |
| **Artifact Format** | OpenSpec directory structure | SpecKit templates |
| **Agent Discovery** | Via `.agents/agents/` symlinks | Embedded in extension commands |
| **Skill References** | Via `.agents/skills/` marketplace | SpecKit-specific implementations |
| **Installation** | Marketplace manifest (`.harness.yaml`) | SpecKit extension manager |
| **Execution Model** | Claude Code agent orchestration | SpecKit command hooks |

### Why Two Implementations?

1. **Different CLI ecosystems** - SpecKit and Claude Code have different plugin architectures
2. **Workflow compatibility** - SpecKit users expect `specify` CLI conventions; Claude Code users expect `/` commands
3. **Artifact management** - SpecKit uses its own template system; Claude Code uses marketplace skills
4. **Team adoption** - Some teams standardize on SpecKit; others use Claude Code directly

---

## Marketplace Plugin System

### What are Plugins?

Plugins are **self-contained directories** under `.agents/plugins/` that bundle related skills, agents, commands, or MCP servers with metadata.

### Available Plugins

| Plugin | Purpose | References |
|--------|---------|------------|
| **matd** | MATD workflow for Claude Code | `agents/`, `skills/` |
| **harness-cgc-skill** | CodeGraphContext integration | `skills/code-graph-context/` |
| **harness-workflow-runtime** | Workflow state management | Metadata only |
| **harness-deepwiki-skill** | DeepWiki C4 documentation | (structure TBD) |

### Plugin vs Extension

**Plugin** (`.agents/plugins/matd/`):
- Claude Code-specific packaging
- References marketplace assets via relative paths
- Installed via marketplace manifest resolution
- Part of the overlay system

**Extension** (`spec-kit-multi-agent-tdd/`):
- SpecKit-specific packaging
- Self-contained with own commands and templates
- Installed via SpecKit extension manager
- Independent of marketplace overlay

---

## Agent Roles

### matd Agents (Shared Methodology)

| Agent | Symbol | Role | Permissions |
|-------|--------|------|-------------|
| **matd-orchestrator** | - | PM Coordinator | Read, Orchestrate |
| **matd-specifier** | Res | Requirements Engineer | Read, Write (openspec/, docs/business/) |
| **matd-critical-thinker** | Crit | Red Team Validator | Read only |
| **matd-architect** | Arch | Solution Designer | Read, Write, Orchestrate |
| **matd-qa** | QA | Test Architect | Read, Write (tests/, openspec/) |
| **matd-dev** | SWE | Implementation Engineer | Read, Write (app/, src/, lib/) |

**Note:** Agent definitions live in `.agents/agents/matd-*.md` and are shared by both the Claude Code plugin and SpecKit extension (conceptually, not by code reference).

---

## Choosing the Right Integration

### Use matd Claude Code Plugin When:
- Working in Claude Code sessions
- Using harness sandbox environment
- Need marketplace skill library integration
- Want `/matd-*` workflow commands
- Project uses `.harness.yaml` manifest system

### Use matd SpecKit Extension When:
- Project is SpecKit-enabled (`specify init` was run)
- Following SpecKit artifact conventions
- Need `/speckit.matd.*` command namespace
- Want SpecKit template-based artifact generation
- Team standardizes on `specify` CLI

### Can Both Coexist?
Yes. A project can have:
- `.harness.yaml` referencing the matd plugin (for Claude Code)
- `.specify/extensions/harness-tdd-workflow` (for SpecKit)

They operate independently and can complement each other.

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

### Updating the matd Plugin

```bash
# Add new agent to marketplace
cd .agents/agents
vim matd-new-role.md

# Plugin.json automatically includes all agents/ via directory reference
# No plugin manifest update needed

# Verify
jq '.agents' .agents/plugins/matd/.claude-plugin/plugin.json
# Output: "../../../agents/" (includes all)
```

### Updating the matd Extension

```bash
# Add new SpecKit command
cd spec-kit-multi-agent-tdd/commands
vim new-command.md

# Register in extension.json
cd ..
vim extension.json
# Add to "commands": { ... }

# Test via SpecKit
specify extension reload harness-tdd-workflow
```

---

## Summary

- **harness-tooling** maintains skills, agents, and commands for multiple CLI ecosystems
- **matd Claude Code plugin** packages marketplace assets for Claude Code sessions
- **matd SpecKit extension** provides SpecKit CLI integration with its own implementation
- Both share the same MATD methodology but serve different workflows
- Choose based on your primary CLI tool (Claude Code vs SpecKit)
- Both can coexist in a project for teams using multiple tools

For installation and usage details:
- **Quick Start**: [README.md](README.md#quick-install)
- **Complete Registration Guide**: [docs/PLUGIN_REGISTRATION_GUIDE.md](docs/PLUGIN_REGISTRATION_GUIDE.md)
- **SpecKit Usage**: [spec-kit-multi-agent-tdd/USER-GUIDE.md](spec-kit-multi-agent-tdd/USER-GUIDE.md)
