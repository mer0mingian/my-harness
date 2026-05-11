# SpecKit Extensions Documentation

**Source**: `/home/minged01/repositories/harness-workplace/spec-kit/extensions/`  
**Copied**: 2026-05-12  
**Purpose**: Reference documentation for developing SpecKit extensions

---

## What are SpecKit Extensions?

SpecKit extensions are modular plugins that add new functionality to the [Spec Kit](https://github.com/github/spec-kit) framework without modifying the core. Extensions provide:

- **Custom commands** that integrate with AI agents (Claude, Gemini)
- **Hooks** that trigger automatically during specification workflows
- **Configuration templates** for team-specific tooling
- **Integration points** with external tools (Git, Jira, etc.)

Extensions are distributed via catalogs (curated or community) or direct URLs, and installed into `.specify/extensions/` within a project.

---

## Documentation Files

### Core Guides

| File | Description |
|------|-------------|
| [EXTENSIONS-OVERVIEW.md](./EXTENSIONS-OVERVIEW.md) | Extension system overview, catalog structure, installation basics |
| [EXTENSION-DEVELOPMENT-GUIDE.md](./EXTENSION-DEVELOPMENT-GUIDE.md) | **Start here** - Complete guide to creating extensions (manifest, commands, config, testing) |
| [EXTENSION-USER-GUIDE.md](./EXTENSION-USER-GUIDE.md) | Installing, managing, and using extensions in projects |
| [EXTENSION-PUBLISHING-GUIDE.md](./EXTENSION-PUBLISHING-GUIDE.md) | Submitting extensions to the community catalog |
| [EXTENSION-API-REFERENCE.md](./EXTENSION-API-REFERENCE.md) | Detailed manifest schema, validation rules, API reference |
| [RFC-EXTENSION-SYSTEM.md](./RFC-EXTENSION-SYSTEM.md) | Design rationale and architecture of the extension system |

### Examples

| Directory | Description |
|-----------|-------------|
| [examples/template/](./examples/template/) | Minimal extension template with example command |
| [examples/git/](./examples/git/) | Production git integration extension (5 commands, scripts) |

---

## Quick Reference

### Extension Structure

```
my-extension/
├── extension.yml              # Manifest (metadata, commands, hooks)
├── commands/                  # Command markdown files
│   └── my-command.md
├── scripts/                   # Optional helper scripts
│   ├── bash/
│   └── powershell/
├── my-ext-config.template.yml # Config template
├── README.md
├── LICENSE
└── .extensionignore          # Files to exclude on install
```

### Manifest Essentials

```yaml
schema_version: "1.0"
extension:
  id: "my-ext"                    # Lowercase, alphanumeric + hyphens
  name: "My Extension"
  version: "1.0.0"                # Semantic versioning
  description: "Brief description"
requires:
  speckit_version: ">=0.1.0"
provides:
  commands:
    - name: "speckit.my-ext.cmd" # Pattern: speckit.{ext-id}.{cmd}
      file: "commands/cmd.md"
```

### Command Naming

- **Pattern**: `speckit.{ext-id}.{command}`
- **Valid**: `speckit.jira.create-issue`, `speckit.git.commit`
- **Invalid**: `my-ext.cmd` (missing prefix), `speckit.cmd` (no namespace)

### Installation

```bash
# From curated catalog (by name)
specify extension add my-ext

# From GitHub release (direct URL)
specify extension add my-ext --from https://github.com/org/repo/archive/refs/tags/v1.0.0.zip

# Local development
specify extension add --dev /path/to/extension

# List installed extensions
specify extension list

# Remove extension
specify extension remove my-ext
```

---

## Relation to Harness Tooling

### MATD Extension

The `matd` (Multi-Agent Task Decomposition) extension in harness-tooling follows SpecKit extension conventions:

- **Location**: `harness-tooling/.agents/extensions/matd/`
- **Manifest**: `extension.yml` declares commands and hooks
- **Commands**: Installed to `.claude/commands/` when added
- **Integration**: Works with both SpecKit and standalone Claude Code projects

### Marketplace Configuration

The harness marketplace (`harness-tooling/.claude-plugin/plugin.json`) declares:

- Skills (`.agents/skills/`)
- Agents (`.agents/agents/`)
- Commands (`.agents/commands/`)
- Extensions (`.agents/extensions/`)

SpecKit extensions can be:
- **Bundled** in marketplace (distributed with plugin)
- **Referenced** via catalog (installed separately by users)

---

## Key Differences from Claude Code Skills/Commands

| SpecKit Extension | Claude Code Skill/Command |
|-------------------|---------------------------|
| Manifest: `extension.yml` | No manifest (files only) |
| Install location: `.specify/extensions/` | Skills: `.agents/skills/`, Commands: `.claude/commands/` |
| Commands: `speckit.{ext-id}.{cmd}` | Commands: `/{name}` (no prefix) |
| Config: Per-extension in `.specify/extensions/{ext-id}/` | Global: `.claude/settings.json` or project `.claude/settings.json` |
| Hooks: Declared in manifest (`after_tasks`, etc.) | Hooks: Configured in `settings.json` |
| Distribution: Catalog + GitHub releases | Distribution: Plugin bundles or manual copy |
| AI integration: Spec Kit CLI registers commands | AI integration: Direct file reading |

---

## Next Steps

1. **Read** [EXTENSION-DEVELOPMENT-GUIDE.md](./EXTENSION-DEVELOPMENT-GUIDE.md) for step-by-step creation guide
2. **Review** [examples/template/](./examples/template/) for minimal working example
3. **Study** [examples/git/](./examples/git/) for production-ready patterns
4. **Reference** [EXTENSION-API-REFERENCE.md](./EXTENSION-API-REFERENCE.md) for validation rules and schema details
5. **Compare** with `harness-tooling/.agents/extensions/matd/` to see harness-specific usage

---

## See Also

- **Harness MATD Extension**: `harness-tooling/.agents/extensions/matd/extension.yml`
- **Marketplace Plugin Manifest**: `harness-tooling/.claude-plugin/plugin.json`
- **SpecKit Main Repo**: https://github.com/github/spec-kit
- **Community Extensions**: https://speckit-community.github.io/extensions/
