---
name: plugin-creation
description: Master guide for creating Claude Code plugins from scratch. Use when building new plugins, understanding plugin architecture, structuring plugin manifests (plugin.json), declaring skills/agents/commands, testing plugins locally, or preparing for marketplace distribution. Covers the complete plugin lifecycle.
---

# Claude Code Plugin Creation

Complete guide for building Claude Code plugins with correct structure, manifests, and marketplace integration.

## When to Use

- Creating new Claude Code plugins
- Understanding Claude Code plugin architecture
- Working with plugin.json manifests
- Declaring skills, agents, commands in plugins
- Testing plugins locally before distribution
- Preparing plugins for marketplace submission
- Troubleshooting plugin loading issues

## Quick Start

### 1. Plugin Directory Structure

Every Claude Code plugin follows this structure:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json           # Required: Plugin manifest
├── skills/                   # Optional: Skill definitions
│   └── my-skill/
│       ├── SKILL.md          # Required for each skill
│       ├── references/       # Optional: Reference docs
│       ├── scripts/          # Optional: Helper scripts
│       └── assets/           # Optional: Templates, files
├── agents/                   # Optional: Agent definitions
│   └── my-agent.md
├── commands/                 # Optional: Slash commands
│   └── my-command.md
├── hooks/                    # Optional: Lifecycle hooks
│   └── hooks.json
├── .mcp.json                 # Optional: MCP server config
├── README.md                 # Required: Documentation
└── LICENSE                   # Required: License file
```

### 2. Create plugin.json Manifest

File: `.claude-plugin/plugin.json`

**Minimal required manifest:**

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin description"
}
```

**Complete manifest with all options:**

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Detailed plugin description",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/you"
  },
  "repository": "https://github.com/you/my-plugin",
  "homepage": "https://my-plugin-docs.com",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2", "productivity"],
  "category": "productivity",
  "skills": [
    "skills/my-skill/SKILL.md"
  ],
  "agents": [
    "agents/my-agent.md"
  ],
  "commands": [
    "commands/my-command.md"
  ],
  "installation": {
    "target": ".claude/",
    "files": ["skills/", "agents/", "commands/"]
  }
}
```

### 3. Manifest Field Reference

**Required fields:**
- `name`: Plugin identifier (lowercase, alphanumeric, hyphens)
- `version`: Semantic version (MAJOR.MINOR.PATCH)
- `description`: Short description (1-2 sentences)

**Optional fields:**
- `author`: Object with name, email, url
- `repository`: Source code URL
- `homepage`: Documentation URL
- `license`: SPDX license identifier (e.g., "MIT", "Apache-2.0")
- `keywords`: Array of search terms
- `category`: Plugin category (productivity, testing, review, etc.)
- `skills`: Array of relative paths to SKILL.md files
- `agents`: Array of relative paths to agent markdown files
- `commands`: Array of relative paths to command markdown files
- `installation`: Object specifying target directory and files to copy

### 4. Adding Plugin Components

#### Skills

Create skill directory with SKILL.md:

```
skills/my-skill/
├── SKILL.md                  # Required
├── references/               # Optional
│   └── detailed-guide.md
├── scripts/                  # Optional
│   └── helper.py
└── assets/                   # Optional
    └── template.json
```

**SKILL.md structure:**

```markdown
---
name: skill-name
description: When to use this skill (be comprehensive - this determines auto-invocation)
---

# Skill Title

## Purpose

What this skill does.

## When to Use

Clear triggers for when Claude should use this skill.

## Instructions

Step-by-step guidance for Claude to follow.
```

Reference the skill in plugin.json:

```json
{
  "skills": [
    "skills/my-skill/SKILL.md"
  ]
}
```

#### Agents

Create agent definition file:

**File**: `agents/my-agent.md`

```markdown
---
name: my-agent
description: Agent description
---

# My Agent

## Role

What this agent specializes in.

## Instructions

How the agent should approach tasks.

## Tools

Tools this agent can use.
```

Reference in plugin.json:

```json
{
  "agents": [
    "agents/my-agent.md"
  ]
}
```

#### Commands

Create command file with frontmatter:

**File**: `commands/my-command.md`

```markdown
---
name: my-command
description: Command description
---

# My Command

Instructions for executing this command.

## Parameters

- param1: Description
- param2: Description

## Example

Usage example.
```

For namespaced commands, use subdirectories:

```
commands/
├── namespace/
│   ├── command1.md           # Becomes /namespace:command1
│   └── command2.md           # Becomes /namespace:command2
└── simple.md                 # Becomes /simple
```

Reference in plugin.json:

```json
{
  "commands": [
    "commands/my-command.md",
    "commands/namespace/command1.md"
  ]
}
```

### 5. Hooks (Advanced)

**File**: `hooks/hooks.json`

```json
{
  "beforeCommand": {
    "pattern": ".*",
    "script": "echo 'Before command hook'"
  },
  "afterCommand": {
    "pattern": "git commit",
    "script": "echo 'After git commit'"
  }
}
```

**Important:** Do NOT declare hooks in plugin.json. Claude Code v2.1+ automatically loads hooks/hooks.json. Declaring it causes duplicate detection errors.

### 6. MCP Server Integration

**File**: `.mcp.json`

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

## Local Testing Workflow

### Step 1: Create Test Project

```bash
mkdir test-project
cd test-project
git init
```

### Step 2: Install Plugin Locally

```bash
# Method 1: Copy to .claude/plugins/
mkdir -p .claude/plugins/my-plugin
cp -r /path/to/plugin/* .claude/plugins/my-plugin/

# Method 2: Symlink for live editing
ln -s /path/to/plugin .claude/plugins/my-plugin
```

### Step 3: Verify Installation

Start Claude Code and check:

```
/skill
```

Your skills should appear in the list.

```
/my-command
```

Your commands should be available.

### Step 4: Test Components

Test each component:

1. **Skills**: Trigger situations where the skill should auto-invoke
2. **Commands**: Execute slash commands with various parameters
3. **Agents**: Call agents and verify their behavior
4. **Hooks**: Trigger hook conditions and check execution

### Step 5: Iterate

Make changes to your plugin source, then:

```bash
# If using symlink: changes are immediate
# If using copy: re-copy files
rm -rf .claude/plugins/my-plugin
cp -r /path/to/plugin/* .claude/plugins/my-plugin/
```

Restart Claude Code to pick up changes.

## Marketplace Integration

### Marketplace Structure

Marketplace repos contain:

```
marketplace-repo/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace index
└── plugins/
    ├── plugin1/
    │   └── .claude-plugin/plugin.json
    └── plugin2/
        └── .claude-plugin/plugin.json
```

### marketplace.json Format

```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name/.claude-plugin/plugin.json",
      "description": "Plugin description",
      "version": "1.0.0",
      "keywords": ["keyword1", "keyword2"],
      "category": "productivity"
    }
  ]
}
```

### Adding Plugin to Marketplace

1. Add plugin to `plugins/` directory
2. Update `marketplace.json` with plugin entry
3. Commit and push

Users install via:

```bash
/plugin marketplace add https://github.com/you/marketplace
/plugin install plugin-name@marketplace-name
```

## Best Practices

### Structure

- **Keep skills focused**: One clear purpose per skill
- **Use progressive disclosure**: Move details to references/
- **Bundle smartly**: Only include essential files
- **Name clearly**: Use descriptive, searchable names

### Documentation

- **Comprehensive descriptions**: Help Claude understand when to invoke
- **Clear examples**: Show expected usage patterns
- **Document dependencies**: List required tools, commands
- **Include troubleshooting**: Common issues and solutions

### Versioning

- **Semantic versioning**: MAJOR.MINOR.PATCH
- **Update both locations**: plugin.json AND marketplace.json
- **Changelog**: Track changes in README or separate file
- **Git tags**: Tag releases for version tracking

### Testing

- **Test all components**: Skills, agents, commands, hooks
- **Test edge cases**: Invalid input, missing dependencies
- **Test installation**: Fresh install in clean environment
- **Test upgrades**: Existing installation → new version

## Common Issues

### Plugin Not Loading

**Symptoms**: Plugin doesn't appear in /skill or /plugin list

**Solutions**:
1. Check plugin.json is valid JSON (use jsonlint)
2. Verify file paths in plugin.json are correct
3. Ensure SKILL.md has valid YAML frontmatter
4. Check for duplicate plugin names
5. Restart Claude Code after changes

### Skills Not Triggering

**Symptoms**: Skill exists but doesn't auto-invoke

**Solutions**:
1. Improve skill description (be more specific about triggers)
2. Check YAML frontmatter is valid
3. Verify skill is referenced in plugin.json
4. Test with explicit /skill invocation first

### Commands Not Found

**Symptoms**: /command shows "command not found"

**Solutions**:
1. Check command file has valid frontmatter
2. Verify command is listed in plugin.json
3. Check file path is correct (relative to plugin root)
4. Ensure command name matches file

### Hooks Not Executing

**Symptoms**: hooks.json exists but hooks don't run

**Solutions**:
1. Don't declare hooks in plugin.json (auto-loaded in v2.1+)
2. Check hooks.json is valid JSON
3. Verify pattern matches the trigger
4. Check script has correct permissions
5. Test hook script independently

## Plugin Development Checklist

Before publishing:

- [ ] Valid plugin.json with all required fields
- [ ] README.md with installation and usage instructions
- [ ] LICENSE file included
- [ ] All skills have complete SKILL.md with frontmatter
- [ ] All commands have valid frontmatter
- [ ] All agents have proper definitions
- [ ] Hooks tested (if included)
- [ ] MCP servers configured (if included)
- [ ] Local testing completed
- [ ] Version bumped appropriately
- [ ] Git repository created
- [ ] Release tagged with version
- [ ] Marketplace entry prepared (if applicable)

## Resources

- [Create plugins - Claude Code Docs](https://code.claude.com/docs/en/plugins)
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Agent Skills - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [GitHub - anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- [GitHub - anthropics/skills](https://github.com/anthropics/skills)

## Related Skills

- `manage-skill-creator`: Creating individual skills
- `manage-mcp-builder`: Building MCP servers
- `manage-command-creator`: Creating slash commands
