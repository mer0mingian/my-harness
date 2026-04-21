> **DEPRECATED 2026-04-21** — superseded by
> [../harness-v1-master-plan.md](../harness-v1-master-plan.md) and
> [../harness-v1-agent-tasks.md](../harness-v1-agent-tasks.md). Kept for historical reference only.

# Unified Multi-Agent CLI Harness Implementation Plan

This document outlines the implementation plan for creating a unified harness that works across OpenCode, Claude Code, and Gemini CLI. The goal is to centralize all skills, agents, commands, and configurations in a single location (`.agents/`) while maintaining backward compatibility and supporting each CLI's unique format requirements.

---

## 1. Directory Structure Overview

### 1.1 Target Architecture

```
/home/mer0/repositories/my-harness/
├── .agents/                    # Central source of truth (existing + expanded)
│   ├── skills/                 # All skill definitions (from .opencode/)
│   ├── agents/                 # All agent definitions (from .opencode/)
│   ├── commands/              # Command definitions (multiple formats)
│   ├── mcp/                    # MCP server configurations
│   └── docs/                   # (existing)

├── .opencode/                  # Backward compatible symlinks
│   ├── skills/ ────────► ../.agents/skills/
│   ├── agents/ ────────► ../.agents/agents/
│   ├── commands/ ──────► ../.agents/commands/
│   └── (existing: plugin/, node_modules/)

├── .claude/                    # Claude Code integration (NEW)
│   ├── commands/ ──────► ../.agents/commands/
│   └── settings.json           # Claude Code config

└── .gemini/                    # Gemini CLI integration (NEW)
    └── extensions/
        └── agents/
            ├── gemini-extension.json
            └── (pointed to by .agents/)
```

### 1.2 Existing Structure (Pre-Migration)

**Current `.opencode/` structure:**

```
.opencode/
├── skills/                        # 40 skill directories
│   ├── alpine-js-patterns/
│   ├── api-design-principles/
│   ├── architecture-patterns/
│   ├── brainstorming/
│   ├── ... (36 more)
│   └── [each contains: SKILL.md]

├── agents/                       # Agent definitions
│   ├── c4-architecture-agents/
│   ├── daniels-workflow-agents/
│   ├── tdd-agents/
│   ├── daniels-architect.md
│   ├── daniels-orchestrator.md
│   └── python-dev.md

├── commands/                     # Markdown command files
│   ├── stdd-feat-workflow.md
│   ├── stdd-04-implement.md
│   ├── stdd-03-refine.md
│   ├── stdd-02-design.md
│   └── stdd-01-specification.md

├── plugin/                       # OpenCode-specific plugins
│   ├── kdco-primitives/
│   └── background-agents.ts

├── node_modules/                # Dependencies
├── package.json
└── bun.lock
```

**Current `.agents/` structure:**

```
.agents/
├── configs/
│   ├── overview_skill_sources.yml
│   ├── mcp_config.yaml
│   ├── overview_skills_on_agents.yml
│   ├── overview_preferred_models.yml
│   ├── overview_plugins.yml
│   ├── overview_agents_skills.yml
│   └── opencode-config-backup.json

└── docs/
    ├── stdd-workflow.md
    └── web research/
        └── (various research files)
```

---

## 2. Implementation Steps (Shell Commands)

### 2.1 Phase 1: Create Central Harness Directory

```bash
# Add subdirectories to existing .agents/ directory
mkdir -p .agents/{skills,agents,commands,mcp}

# Verify creation
ls -la .agents/
```

### 2.2 Phase 2: Migrate Skills

```bash
# Copy all skills from .opencode/skills/ to .agents/skills/
cp -r .opencode/skills/* .agents/skills/

# Verify migration
ls .agents/skills/ | wc -l
# Expected: 40 skills

# List skill names
ls .agents/skills/
```

### 2.3 Phase 3: Migrate Agents

```bash
# Copy all agents from .opencode/agents/ to .agents/agents/
cp -r .opencode/agents/* .agents/agents/

# Verify migration
ls -la .agents/agents/
```

### 2.4 Phase 4: Migrate Commands and Convert Formats

```bash
# Copy existing markdown commands
cp -r .opencode/commands/* .agents/commands/

# Create TOML versions for Claude Code and Gemini CLI
# (See Section 3 for conversion strategy)

# Verify both formats exist
ls .agents/commands/
```

### 2.5 Phase 5: Create OpenCode Symlinks (Backward Compatibility)

```bash
# Remove old directories (backup first)
mv .opencode/skills .opencode/skills.bak
mv .opencode/agents .opencode/agents.bak
mv .opencode/commands .opencode/commands.bak

# Create symlinks to central harness
ln -s ../.agents/skills .opencode/skills
ln -s ../.agents/agents .opencode/agents
ln -s ../.agents/commands .opencode/commands

# Verify symlinks
ls -la .opencode/ | grep "^l"
```

### 2.6 Phase 6: Create Claude Code Directory

```bash
# Create .claude/ directory for Claude Code
mkdir -p .claude/commands

# Create symlinks to command storage
ln -s ../.agents/commands .claude/commands

# Create Claude Code settings
cat > .claude/settings.json << 'EOF'
{
  "claudeCode": {
    "enabled": true,
    "commandDir": ".claude/commands"
  }
}
EOF
```

### 2.7 Phase 7: Create Gemini CLI Extension

```bash
# Create Gemini CLI extensions directory
mkdir -p .gemini/extensions/agents

# Create Gemini extension manifest
cat > .gemini/extensions/agents/gemini-extension.json << 'EOF'
{
  "name": "agents",
  "version": "1.0.0",
  "description": "Unified CLI harness for AI-assisted development",
  "entry": "../.agents",
  "commands": {
    "directory": "../.agents/commands"
  }
}
EOF

# Note: Gemini CLI extensions typically point to external directories
# The actual command loading depends on Gemini CLI's extension mechanism
```

---

## 3. Command Adapter Strategy

### 3.1 Format Differences

| CLI         | Format   | File Extension | Loading Mechanism                                    |
| ----------- | -------- | -------------- | ---------------------------------------------------- |
| OpenCode    | Markdown | `*.md`       | Parses `## Usage`, `## Parameters` sections      |
| Claude Code | TOML     | `*.toml`     | `name`, `description`, `prompt` top-level keys |
| Gemini CLI  | TOML     | `*.toml`     | Similar to Claude Code with Gemini-specific fields   |

### 3.2 Hybrid Approach Strategy

**Recommended: Dual-Format Storage**

Store commands in a canonical format (TOML) and use format-specific filenames:

```
.agents/commands/
├── stdd-feat-workflow.md          # OpenCode format
├── stdd-feat-workflow.toml       # Claude Code format
├── stdd-feat-workflow.gemini.toml # Gemini CLI format
├── stdd-01-specification.md     # OpenCode format
├── stdd-01-specification.toml   # Claude Code format
└── stdd-01-specification.gemini.toml
```

### 3.3 Conversion Script

Create a conversion script to generate all formats from a canonical source:

```bash
#!/bin/bash
# scripts/convert-commands.sh

COMMANDS_DIR=".agents/commands"

# Function to convert Markdown to TOML (Claude Code)
convert_md_to_toml() {
    local md_file="$1"
    local toml_file="${2:-$(echo $md_file | sed 's/\.md$/.toml/')}"

    # Parse markdown and generate TOML
    # This is a simplified version - full implementation would parse sections
    local name=$(basename "$md_file" .md)

    cat > "$toml_file" << EOF
name = "$name"
description = "Converted from markdown source"
prompt = """$(cat "$md_file")"""
EOF
}

# Convert all markdown commands
for md in "$COMMANDS_DIR"/*.md; do
    [ -e "$md" ] || continue
    toml="${md%.md}.toml"
    echo "Converting: $md -> $toml"
    convert_md_to_toml "$md" "$toml"
done

echo "Conversion complete"
```

### 3.4 Format Specification Examples

**OpenCode Markdown Format (`stdd-feat-workflow.md`):**

```markdown
# Feature Workflow

## Description
Complete workflow for implementing new features.

## Steps
1. Create specification
2. Design solution
3. Implement
4. Verify

## Usage
/stdd-feat-workflow
```

**Claude Code TOML Format (`stdd-feat-workflow.toml`):**

```toml
name = "stdd-feat-workflow"
description = "Complete workflow for implementing new features."

[instructions]
primary = """
Complete workflow for implementing new features.
Steps:
1. Create specification
2. Design solution
3. Implement
4. Verify
"""
```

**Gemini CLI TOML Format (`stdd-feat-workflow.gemini.toml`):**

```toml
command = "stdd-feat-workflow"
description = "Complete workflow for implementing new features."

[geminicli]
version = "1.0"
enabled = true
```

---

## 4. MCP Configuration

### 4.1 Current MCP Setup

There is currently no `.mcp.json` in the project. The `.agents/configs/mcp_config.yaml` file exists but may be outdated or a research document.

### 4.2 Unified MCP Configuration Strategy

**Option 1: Shared `.mcp.json`**

Create a single `.mcp.json` at the root that can be symlinked or referenced by all CLIs:

```json
{
  "mcpServers": {
    "agents-tools": {
      "command": "node",
      "args": [".agents/mcp/server.js"],
      "env": {}
    },
    "git-integration": {
      "command": "uvicorn",
      "args": ["sta.mcp.git:app"]
    }
  }
}
```

**Option 2: CLI-Specific MCP Configs**

Each CLI may require its own MCP configuration format:

```
.mcp.json                 # OpenCode / Claude Code (shared)
.gemini/mcp-servers.json # Gemini CLI specific
```

### 4.3 MCP Server Implementation

For custom MCP servers, create them in `.agents/mcp/`:

```
.agents/mcp/
├── server.js            # Main MCP server entry
├── tools/
│   ├── git.js
│   ├── docker.js
│   └── database.js
└── package.json
```

---

## 5. Verification Steps

### 5.1 Verify OpenCode Integration

```bash
# Check that OpenCode can see the symlinked resources
ls -la .opencode/skills
ls -la .opencode/agents
ls -la .opencode/commands

# Test skill loading (OpenCode-specific command)
# /opencode-list-skills  # or equivalent OpenCode command
```

### 5.2 Verify Claude Code Integration

```bash
# Check Claude Code directory exists
ls -la .claude/

# Verify symlinks are correct
readlink .claude/commands

# Test command visibility
ls .claude/commands/
```

### 5.3 Verify Gemini CLI Integration

```bash
# Check Gemini extension exists
ls -la .gemini/extensions/agents/

# Verify manifest
cat .gemini/extensions/agents/gemini-extension.json
```

### 5.4 Full Integration Test

```bash
#!/bin/bash
# scripts/verify-integration.sh

echo "=== Unified Harness Verification ==="

echo -e "\n1. Checking central .agents/..."
[ -d ".agents" ] && echo "   ✓ .agents/ exists" || echo "   ✗ Missing"
[ -d ".agents/skills" ] && echo "   ✓ skills/ exists" || echo "   ✗ Missing"
[ -d ".agents/agents" ] && echo "   ✓ agents/ exists" || echo "   ✗ Missing"
[ -d ".agents/commands" ] && echo "   ✓ commands/ exists" || echo "   ✗ Missing"

echo -e "\n2. Checking OpenCode backward compatibility..."
[ -L ".opencode/skills" ] && echo "   ✓ skills/ symlink" || echo "   ✗ Missing"
[ -L ".opencode/agents" ] && echo "   ✓ agents/ symlink" || echo "   ✗ Missing"
[ -L ".opencode/commands" ] && echo "   ✓ commands/ symlink" || echo "   ✗ Missing"

echo -e "\n3. Checking Claude Code integration..."
[ -d ".claude" ] && echo "   ✓ .claude/ exists" || echo "   ✗ Missing"
[ -L ".claude/commands" ] && echo "   ✓ commands/ symlink" || echo "   ✗ Missing"

echo -e "\n4. Checking Gemini CLI integration..."
[ -d ".gemini/extensions/agents" ] && echo "   ✓ extension exists" || echo "   ✗ Missing"
[ -f ".gemini/extensions/agents/gemini-extension.json" ] && echo "   ✓ manifest exists" || echo "   ✗ Missing"

echo -e "\n5. Checking skills count..."
SKILLS_COUNT=$(ls .agents/skills/ 2>/dev/null | wc -l)
echo "   Skills: $SKILLS_COUNT"

echo -e "\n=== Verification Complete ==="
```

---

## 6. Rollback Plan

If migration fails, restore from backups:

```bash
# Remove symlinks
rm .opencode/skills .opencode/agents .opencode/commands

# Restore backups
mv .opencode/skills.bak .opencode/skills
mv .opencode/agents.bak .opencode/agents
mv .opencode/commands.bak .opencode/commands

# Note: .agents/ directory already existed with configs/docs
# Only remove the newly added subdirectories if needed
rm -rf .agents/skills .agents/agents .agents/commands .agents/mcp
```

---

## 7. Implementation Checklist

- [ ] Add subdirectories to existing `.agents/` directory
- [ ] Migrate skills (40 directories)
- [ ] Migrate agents
- [ ] Migrate commands
- [ ] Create command conversion script
- [ ] Generate TOML formats for all commands
- [ ] Create OpenCode symlinks (backward compat)
- [ ] Create `.claude/` directory and symlinks
- [ ] Create `.gemini/` extension
- [ ] Create unified MCP config (if needed)
- [ ] Run verification script
- [ ] Test with each CLI (OpenCode, Claude Code, Gemini CLI)
- [ ] Document any CLI-specific quirks

---

## 8. Notes and Considerations

1. **Central directory already exists**: The `.agents/` directory already exists with `configs/` and `docs/` subdirectories. This plan expands it to be the central source of truth for skills, agents, commands, and MCP configurations.
2. **OpenCode-specific plugin**: The `.opencode/plugin/` directory contains OpenCode-specific code (`background-agents.ts`) that should remain in `.opencode/` as it's tied to OpenCode's API.
3. **Node modules**: Dependencies in `.opencode/node_modules/` should either remain in `.opencode/` or be duplicated in `.agents/` depending on usage.
4. **Gemini CLI extension mechanism**: The actual Gemini CLI extension loading mechanism may differ. This plan assumes a directory-based extension system. Adjust based on Gemini CLI's actual documentation.
5. **Testing priority**: Test with OpenCode first (since it already works), then verify Claude Code and Gemini CLI integrations.

---

*Document Version: 1.1*
*Updated: 2026-04-19*
