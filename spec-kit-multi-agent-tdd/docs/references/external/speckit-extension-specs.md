# SpecKit Extension Technical Specifications

**Source:** spec-kit/docs/reference/ and spec-kit/extensions/
**Extracted:** 2026-05-07

## Overview

SpecKit extensions are modular packages that add new commands and functionality without bloating the core framework. They integrate with external tools (Jira, Linear, GitHub), automate tasks via hooks, and are versioned independently from the core.

**Key Design Principles:**
- Convention over configuration
- Fail-safe defaults (invalid extensions warn but don't break core)
- Backward compatibility (extensions are additive only)
- Security first (extensions run in same context as AI agent)

---

## Extension Structure

### Required Directory Layout

```text
my-extension/
├── extension.yml                    # Manifest (REQUIRED)
├── commands/                        # Command files (REQUIRED - at least 1)
│   ├── example.md                   # Universal command format
│   └── another-cmd.md
├── config-template.yml              # Config template (OPTIONAL)
├── scripts/                         # Helper scripts (OPTIONAL)
│   ├── helper.sh
│   └── helper.ps1
├── docs/                            # Documentation (RECOMMENDED)
│   └── usage.md
├── README.md                        # Overview (RECOMMENDED)
├── LICENSE                          # License file (RECOMMENDED)
├── CHANGELOG.md                     # Version history (RECOMMENDED)
└── .extensionignore                 # Installation exclusions (OPTIONAL)
```

### Installation Structure

After installation via `specify extension add`, extensions are installed to:

```text
.specify/extensions/{extension-id}/
├── extension.yml
├── {ext-id}-config.yml             # From template, user edits
├── {ext-id}-config.local.yml       # Gitignored local overrides
├── {ext-id}-config.template.yml    # Reference template
├── commands/                        # Command markdown files
├── scripts/                         # Helper scripts
├── docs/                            # Documentation
└── README.md
```

### Exclusion File: `.extensionignore`

Extensions can include a `.extensionignore` file at the root to exclude development-only files during installation:

**Format:** `.gitignore`-compatible patterns (powered by `pathspec` library)
- Blank lines and `#` comments ignored
- `*` matches anything except `/`
- `**` matches zero or more directories
- `?` matches single character except `/`
- Trailing `/` restricts to directories only
- Patterns with `/` anchored to extension root
- `!` negates previous exclusion
- Backslashes normalized to forward slashes

**Example:**
```gitignore
# Development files
tests/
.github/
.gitignore

# Build artifacts
__pycache__/
*.pyc
dist/

# Keep only built README
docs/
CONTRIBUTING.md
```

**Limitation:** Cannot re-include files inside excluded directories (e.g., `tests/` then `!tests/important.py` won't work).

---

## Extension Manifest (`extension.yml`)

### Schema Version 1.0

**Required Root Fields:**
- `schema_version`: Must be `"1.0"`
- `extension`: Metadata block
- `requires`: Compatibility requirements
- `provides`: What the extension provides

### Complete Manifest Structure

```yaml
schema_version: "1.0"

extension:
  # REQUIRED fields
  id: "my-ext"                        # Pattern: ^[a-z0-9-]+$
  name: "My Extension"                # Human-readable name
  version: "1.0.0"                    # Semantic versioning: X.Y.Z
  description: "Brief description"    # <200 characters
  author: "Your Name"
  repository: "https://github.com/you/spec-kit-my-ext"
  license: "MIT"                      # SPDX identifier
  
  # OPTIONAL fields
  homepage: "https://example.com"

requires:
  # REQUIRED
  speckit_version: ">=0.1.0"         # Version specifier
  
  # OPTIONAL
  tools:
    - name: "tool-name"
      version: ">=1.0.0"               # Optional version constraint
      required: true                   # Default: false
      description: "Tool description"
      install_url: "https://install.url"
      check_command: "tool --version"  # Optional verification
  
  commands:                            # Core commands needed
    - "speckit.tasks"
  
  scripts:                             # Core scripts required
    - "check-prerequisites.sh"

provides:
  # REQUIRED - at least one command or hook
  commands:
    - name: "speckit.my-ext.hello"     # Pattern: speckit.{ext-id}.{command}
      file: "commands/hello.md"
      description: "Say hello"
      aliases: ["speckit.my-ext.hi"]   # Optional, same pattern
  
  # OPTIONAL
  config:
    - name: "my-ext-config.yml"
      template: "config-template.yml"
      description: "Extension configuration"
      required: false                  # Default: false

# OPTIONAL
hooks:
  after_tasks:                         # Event name
    command: "speckit.my-ext.hello"    # Command to execute
    optional: true                     # Prompt user (default: true)
    prompt: "Run hello command?"       # For optional hooks
    description: "Hook description"
    condition: null                    # Future: conditional execution

# OPTIONAL - for catalog discovery
tags:
  - "example"
  - "utility"

# OPTIONAL - default config values
defaults:
  feature:
    enabled: true
    auto_sync: false

# OPTIONAL - JSON Schema for config validation
config_schema:
  type: "object"
  required: ["project"]
  properties:
    project:
      type: "object"
      required: ["key"]
      properties:
        key:
          type: "string"
          pattern: "^[A-Z]{2,10}$"
```

### Validation Rules

1. **Extension ID:** `^[a-z0-9-]+$` (lowercase, alphanumeric, hyphens only)
   - Valid: `my-ext`, `tool-123`, `awesome-plugin`
   - Invalid: `MyExt`, `my_ext`, `my ext`

2. **Version:** Semantic versioning `X.Y.Z`
   - Valid: `1.0.0`, `0.1.0`, `2.5.3`
   - Invalid: `1.0`, `v1.0.0`, `1.0.0-beta`

3. **Command Name:** `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`
   - Format: `speckit.{extension-id}.{command-name}`
   - Valid: `speckit.my-ext.hello`, `speckit.tool.cmd`
   - Invalid: `my-ext.hello`, `speckit.hello`, `speckit.my-ext.CreateIssues`

4. **Aliases:** Same pattern as command name, namespace must match `extension.id`

5. **File Paths:** Must be relative to extension root
   - Valid: `commands/hello.md`, `commands/subdir/cmd.md`
   - Invalid: `/absolute/path.md`, `../outside.md`

6. **Version Specifier Examples:**
   - `>=0.1.0` - Any version 0.1.0 or higher
   - `>=0.1.0,<2.0.0` - Version 0.1.x or 1.x
   - `==0.1.0` - Exactly 0.1.0

---

## Command Architecture

### Universal Command Format

Commands are written **once** in a universal Markdown format. The SpecKit CLI converts them to agent-specific formats during registration (Claude, Gemini, Copilot, Cursor, etc. - 15+ agents supported).

**File Location:** `commands/{command-name}.md`

### Command File Structure

```markdown
---
# YAML Frontmatter (REQUIRED)
description: "Command description"          # REQUIRED
tools:                                      # OPTIONAL
  - 'mcp-server/tool_name'
  - 'other-mcp-server/other_tool'
scripts:                                    # OPTIONAL
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---

# Command Title

Command documentation in Markdown.

## Prerequisites

1. Requirement 1
2. Requirement 2

## User Input

$ARGUMENTS

## Steps

### Step 1: Load Configuration

Load extension configuration from the project:

```bash
config_file=".specify/extensions/my-ext/my-ext-config.yml"

if [ ! -f "$config_file" ]; then
  echo "❌ Error: Configuration not found"
  exit 1
fi

# Read configuration values
setting=$(yq eval '.settings.key' "$config_file")

# Apply environment variable overrides
setting="${SPECKIT_MY_EXT_KEY:-$setting}"

echo "📋 Configuration loaded: $setting"
```

### Step 2: Execute Main Logic

```markdown
Use MCP tools to perform the action:

- Tool: example-mcp-server example_tool
- Parameters: { "key": "$setting" }
```

### Step 3: Output Results

```bash
echo "✅ Command completed successfully!"
echo "Results:"
echo "  • Item 1: Value"
echo "  • Item 2: Value"
```

## Configuration Reference

This command uses:
- **settings.key**: Description (Type: string, Required: Yes)
- **settings.feature**: Description (Type: boolean, Default: false)

## Environment Variables

- `SPECKIT_MY_EXT_KEY` - Overrides `settings.key`

## Troubleshooting

### "Configuration not found"
**Solution**: Create config from template
```

### Special Placeholders

- `$ARGUMENTS` - User-provided arguments (replaced by AI agent)
- Extension context automatically injected:
  ```markdown
  <!-- Extension: {extension-id} -->
  <!-- Config: .specify/extensions/{extension-id}/ -->
  ```

### Script Path Rewriting

Extension commands use relative paths that get rewritten during registration:

**In extension:**
```yaml
scripts:
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
```

**After registration to `.claude/commands/`:**
```yaml
scripts:
  sh: .specify/scripts/bash/helper.sh
  ps: .specify/scripts/powershell/helper.ps1
```

This allows commands to reference core SpecKit scripts.

### Command Registration Process

1. **Installation**: User runs `specify extension add my-ext`
2. **Validation**: CLI validates `extension.yml` against schema
3. **Extraction**: Files copied to `.specify/extensions/my-ext/`
4. **Conversion**: Commands converted from universal format to agent-specific format
5. **Registration**: 
   - Claude Code: Creates `.claude/commands/speckit.my-ext.{cmd}.md`
   - Gemini CLI: Creates `.gemini/commands/speckit.my-ext.{cmd}.toml`
   - Copilot: Creates `.copilot/commands/speckit.my-ext.{cmd}.md`
   - (15+ agents supported)
6. **Skills** (optional): If project uses skills integration, commands auto-registered as agent skills

### Multi-Agent Support

The same command file works across all agents:

| Agent | Output Format | Location |
|-------|---------------|----------|
| Claude Code | Markdown with YAML frontmatter | `.claude/commands/{cmd}.md` |
| Gemini CLI | TOML | `.gemini/commands/{cmd}.toml` |
| GitHub Copilot | Markdown | `.copilot/commands/{cmd}.md` |
| Cursor | Agent-specific format | `.cursor/commands/` |
| ...15+ agents | Various | Various locations |

---

## Integration Points

### Hook System

**Purpose:** Automatic command execution at lifecycle events

**Available Hook Points:**
- `before_specify` / `after_specify` - Specification generation
- `before_plan` / `after_plan` - Implementation planning
- `before_tasks` / `after_tasks` - Task generation
- `before_implement` / `after_implement` - Implementation
- `before_analyze` / `after_analyze` - Cross-artifact analysis
- `before_checklist` / `after_checklist` - Checklist generation
- `before_clarify` / `after_clarify` - Spec clarification
- `before_constitution` / `after_constitution` - Constitution update
- `before_taskstoissues` / `after_taskstoissues` - Tasks-to-issues conversion

**Hook Definition in `extension.yml`:**

```yaml
hooks:
  after_tasks:
    command: "speckit.my-ext.analyze"    # Command to execute
    optional: true                       # Prompt user (false = auto-execute)
    prompt: "Run analysis?"              # For optional hooks
    description: "Analyze generated tasks"
    condition: null                      # Future: conditional expression
```

**Hook Registration:**

When extension is installed, hooks are registered in `.specify/extensions.yml`:

```yaml
hooks:
  after_tasks:
    - extension: my-ext
      command: speckit.my-ext.analyze
      enabled: true
      optional: true
      prompt: "Run analysis?"
      description: "Analyze generated tasks"
```

**Hook Execution Flow:**

1. Core command completes (e.g., `/speckit.tasks`)
2. Core command checks for hooks at end of execution
3. For optional hooks: AI agent prompts user
4. For mandatory hooks: AI agent executes automatically
5. Hook command executes with full context

**Hook Message Format:**

Optional hooks:
```markdown
## Extension Hooks

**Optional Hook**: my-ext
Command: `/speckit.my-ext.analyze`
Description: Analyze generated tasks

Prompt: Run analysis?
To execute: `/speckit.my-ext.analyze`
```

Mandatory hooks:
```markdown
**Automatic Hook**: my-ext
Executing: `/speckit.my-ext.analyze`
EXECUTE_COMMAND: speckit.my-ext.analyze
```

### Template Resolution

When multiple extensions provide the same template, priority determines which is used:

**Priority Field:** Lower number = higher precedence (default: 10)

```bash
# Set extension priority
specify extension set-priority my-ext 5
```

**Use Cases:**
- Override default templates with organization-specific versions
- Ensure critical extension templates take precedence

### API/Tool Integration

**MCP Tools Declaration:**

Commands declare required MCP tools in frontmatter:

```yaml
---
tools:
  - 'jira-mcp-server/epic_create'
  - 'jira-mcp-server/story_create'
---
```

**Tool Verification:**

During installation, CLI checks for required tools:

```yaml
requires:
  tools:
    - name: "jira-mcp-server"
      required: true
      version: ">=1.0.0"
      check_command: "jira --version"
```

**AI Agent Integration:**

1. Extension declares tools in frontmatter
2. CLI passes tool declarations to AI agent during registration
3. AI agent verifies tool availability when command is invoked
4. AI agent provides appropriate error if tool missing

---

## Configuration

### Configuration File Hierarchy

**Four-Layer Resolution** (highest priority last):

1. **Extension Defaults** - From `extension.yml` → `defaults` section
2. **Project Config** - `.specify/extensions/{ext-id}/{ext-id}-config.yml`
3. **Local Overrides** - `.specify/extensions/{ext-id}/{ext-id}-config.local.yml` (gitignored)
4. **Environment Variables** - `SPECKIT_{EXT_ID}_*`

### Example Configuration

**Extension defaults in `extension.yml`:**
```yaml
defaults:
  project:
    key: null
  features:
    auto_sync: false
  timeout: 30
```

**Project config (`my-ext-config.yml`):**
```yaml
project:
  key: "MYPROJ"

features:
  auto_sync: true
```

**Local override (`my-ext-config.local.yml`):**
```yaml
project:
  key: "DEVTEST"  # Override for local development
```

**Environment variables:**
```bash
export SPECKIT_MY_EXT_PROJECT_KEY="CITEST"
export SPECKIT_MY_EXT_TIMEOUT=60
```

**Final resolved config:** Environment variables win

### Configuration Loading Pattern

**In command file:**

```bash
#!/usr/bin/env bash
EXT_DIR=".specify/extensions/my-ext"
CONFIG_FILE="$EXT_DIR/my-ext-config.yml"
LOCAL_CONFIG="$EXT_DIR/my-ext-config.local.yml"

# Start with defaults from extension.yml
defaults=$(yq eval '.defaults' "$EXT_DIR/extension.yml" -o=json)

# Merge project config
if [ -f "$CONFIG_FILE" ]; then
  project_config=$(yq eval '.' "$CONFIG_FILE" -o=json)
  defaults=$(echo "$defaults $project_config" | jq -s '.[0] * .[1]')
fi

# Merge local config
if [ -f "$LOCAL_CONFIG" ]; then
  local_config=$(yq eval '.' "$LOCAL_CONFIG" -o=json)
  defaults=$(echo "$defaults $local_config" | jq -s '.[0] * .[1]')
fi

# Apply environment variable overrides
if [ -n "${SPECKIT_MY_EXT_PROJECT_KEY:-}" ]; then
  defaults=$(echo "$defaults" | jq ".project.key = \"$SPECKIT_MY_EXT_PROJECT_KEY\"")
fi

echo "$defaults"
```

### Configuration Schema Validation

**Define schema in `extension.yml`:**

```yaml
config_schema:
  type: "object"
  required: ["project"]
  properties:
    project:
      type: "object"
      required: ["key"]
      properties:
        key:
          type: "string"
          pattern: "^[A-Z]{2,10}$"
          description: "Project key (2-10 uppercase letters)"
    features:
      type: "object"
      properties:
        auto_sync:
          type: "boolean"
    timeout:
      type: "integer"
      minimum: 1
      maximum: 300
```

**Validation in command:**

```python
import jsonschema

schema = load_yaml(".specify/extensions/my-ext/extension.yml")['config_schema']
config = json.loads(config_json)

try:
    jsonschema.validate(config, schema)
except jsonschema.ValidationError as e:
    print(f"❌ Invalid config: {e.message}")
    exit(1)
```

### Environment Variable Pattern

**Format:** `SPECKIT_{EXTENSION_ID}_{CONFIG_PATH}`

**Examples:**
- `SPECKIT_JIRA_PROJECT_KEY` → `project.key`
- `SPECKIT_LINEAR_API_KEY` → `api.key`
- `SPECKIT_GITHUB_TOKEN` → `token`

**Transformation:**
- Extension ID uppercased
- Underscores separate nested keys
- Replaces corresponding config value

### Core Environment Variables

Beyond extension-specific vars, SpecKit supports core environment variables:

| Variable | Description |
|----------|-------------|
| `SPECKIT_CATALOG_URL` | Override full catalog stack with single URL |
| `GH_TOKEN` / `GITHUB_TOKEN` | GitHub token for private repositories |

---

## Extension Catalog System

### Dual Catalog Architecture

**Two Built-in Catalogs:**

1. **Default Catalog** (`catalog.json`)
   - Priority: 1 (highest)
   - Install Allowed: Yes
   - Purpose: Curated, installable extensions
   - URL: `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json`

2. **Community Catalog** (`catalog.community.json`)
   - Priority: 2
   - Install Allowed: No (discovery only)
   - Purpose: Browse community extensions
   - URL: `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json`

### Catalog Stack Resolution

**Order of precedence** (first match wins):

1. `SPECKIT_CATALOG_URL` environment variable (replaces all catalogs)
2. Project-level `.specify/extension-catalogs.yml`
3. User-level `~/.specify/extension-catalogs.yml`
4. Built-in default stack (both catalogs above)

### Catalog Configuration File

**`.specify/extension-catalogs.yml`:**

```yaml
catalogs:
  - name: "default"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json"
    priority: 1
    install_allowed: true
    description: "Built-in catalog of installable extensions"
  
  - name: "internal"
    url: "https://internal.company.com/spec-kit/catalog.json"
    priority: 2
    install_allowed: true
    description: "Internal company extensions"
  
  - name: "community"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json"
    priority: 3
    install_allowed: false
    description: "Community extensions (discovery only)"
```

### Catalog Entry Format

**In catalog JSON:**

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-01-28T14:30:00Z",
  "extensions": {
    "my-ext": {
      "name": "My Extension",
      "id": "my-ext",
      "description": "Extension description",
      "author": "Your Name",
      "version": "1.0.0",
      "download_url": "https://github.com/you/spec-kit-my-ext/archive/refs/tags/v1.0.0.zip",
      "repository": "https://github.com/you/spec-kit-my-ext",
      "homepage": "https://github.com/you/spec-kit-my-ext",
      "documentation": "https://github.com/you/spec-kit-my-ext/blob/main/docs/",
      "changelog": "https://github.com/you/spec-kit-my-ext/blob/main/CHANGELOG.md",
      "license": "MIT",
      "requires": {
        "speckit_version": ">=0.1.0",
        "tools": [
          {
            "name": "tool-name",
            "version": ">=1.0.0"
          }
        ]
      },
      "tags": ["tag1", "tag2"],
      "verified": true,
      "downloads": 100,
      "stars": 25
    }
  }
}
```

**Required Fields:**
- `name`, `id`, `version`, `download_url`, `repository`

**Optional Fields:**
- `description`, `author`, `license`, `homepage`, `documentation`, `changelog`
- `requires`, `tags`, `verified`, `downloads`, `stars`, `checksum`

### Catalog Management Commands

```bash
# List active catalogs
specify extension catalog list

# Add catalog (project-scoped)
specify extension catalog add \
  --name "internal" \
  --priority 2 \
  --install-allowed \
  https://internal.company.com/catalog.json

# Remove catalog
specify extension catalog remove internal

# Search across all catalogs
specify extension search jira

# Install (only from install_allowed catalogs)
specify extension add jira
```

---

## Key Takeaways

### Critical Requirements

1. **Manifest is Required**
   - Must have `extension.yml` at root
   - Must follow schema version 1.0
   - Must declare at least one command or hook

2. **Commands Use Universal Format**
   - Markdown files with YAML frontmatter
   - `$ARGUMENTS` placeholder for user input
   - Relative script paths rewritten during registration
   - Same file works across 15+ AI agents

3. **Naming Conventions are Strict**
   - Extension ID: `^[a-z0-9-]+$`
   - Version: Semantic versioning `X.Y.Z`
   - Command name: `speckit.{ext-id}.{command-name}`

4. **Configuration is Layered**
   - Four layers: defaults → project → local → env vars
   - Environment variables: `SPECKIT_{EXT_ID}_{KEY}`
   - Local overrides are gitignored
   - Schema validation via JSON Schema

5. **Hooks Enable Automation**
   - Trigger at lifecycle events (before/after core commands)
   - Optional hooks prompt user
   - Mandatory hooks auto-execute
   - Registered in `.specify/extensions.yml`

6. **Extensions are Isolated**
   - Installed to `.specify/extensions/{ext-id}/`
   - Cannot modify core functionality
   - Can be disabled without removal
   - Version controlled independently

7. **Multi-Catalog Support**
   - Dual catalog system (installable + discovery)
   - Catalog stack with priority resolution
   - `install_allowed` flag controls installation
   - `SPECKIT_CATALOG_URL` for single-catalog override

### Installation Workflow

```bash
# 1. Search for extension
specify extension search jira

# 2. View details
specify extension info jira

# 3. Install extension
specify extension add jira

# 4. Configure (copy template, edit)
cp .specify/extensions/jira/jira-config.template.yml \
   .specify/extensions/jira/jira-config.yml
vim .specify/extensions/jira/jira-config.yml

# 5. Use commands in AI agent
claude
> /speckit.jira.specstoissues
```

### Development Workflow

```bash
# 1. Create extension directory
mkdir my-extension
cd my-extension

# 2. Create manifest
cat > extension.yml << 'EOF'
schema_version: "1.0"
extension:
  id: "my-ext"
  name: "My Extension"
  version: "1.0.0"
  description: "My custom extension"
  author: "Your Name"
  repository: "https://github.com/you/spec-kit-my-ext"
  license: "MIT"
requires:
  speckit_version: ">=0.1.0"
provides:
  commands:
    - name: "speckit.my-ext.hello"
      file: "commands/hello.md"
      description: "Say hello"
EOF

# 3. Create command
mkdir commands
cat > commands/hello.md << 'EOF'
---
description: "Say hello command"
---
# Hello Command

```bash
echo "Hello, $ARGUMENTS!"
```
EOF

# 4. Test locally
specify extension add --dev /path/to/my-extension

# 5. Verify installation
specify extension list

# 6. Test command
claude
> /speckit.my-ext.hello world

# 7. Remove for iteration
specify extension remove my-ext
```

### Security Considerations

1. **Trust Boundary:** Extensions run with same privileges as AI agent
2. **Verified Badge:** Only for reviewed extensions in default catalog
3. **Community Extensions:** Show warning during installation
4. **No Secrets in Config:** Use environment variables
5. **Sandboxing:** Future feature (Phase 2)
6. **Package Integrity:** Future feature (checksums, signatures)

### Best Practices

1. **Naming:** Use descriptive IDs (`jira-integration` not `ji`)
2. **Versioning:** Follow SemVer (MAJOR.MINOR.PATCH)
3. **Documentation:** Include README, CHANGELOG, docs/
4. **Configuration:** Use templates, validate with schema
5. **Compatibility:** Specify version ranges, not exact versions
6. **Testing:** Test with `--dev` before publishing
7. **Git Ignore:** Add `*.local.yml`, `.cache/`, `.backup/`

---

## Python API Quick Reference

```python
from specify_cli.extensions import (
    ExtensionManifest,
    ExtensionManager,
    ExtensionRegistry,
    ExtensionCatalog,
    HookExecutor,
    CommandRegistrar
)

# Load manifest
manifest = ExtensionManifest(Path("extension.yml"))

# Install extension
manager = ExtensionManager(project_root)
manifest = manager.install_from_directory(source_dir, speckit_version)

# Manage registry
registry = ExtensionRegistry(extensions_dir)
registry.add(extension_id, metadata)
is_installed = registry.is_installed(extension_id)

# Search catalog
catalog = ExtensionCatalog(project_root)
results = catalog.search(query, tag, author, verified_only)
ext_info = catalog.get_extension_info(extension_id)

# Execute hooks
hook_executor = HookExecutor(project_root)
hooks = hook_executor.get_hooks_for_event("after_tasks")
hook_executor.register_hooks(manifest)

# Register commands
registrar = CommandRegistrar()
registered = registrar.register_commands_for_claude(
    manifest, extension_dir, project_root
)
```

---

## File Paths Reference

| Path | Description |
|------|-------------|
| `.specify/extensions/` | Extensions root directory |
| `.specify/extensions/.registry` | Installation metadata (JSON) |
| `.specify/extensions/.cache/` | Catalog cache |
| `.specify/extensions/.backup/` | Config backups |
| `.specify/extensions/{ext-id}/` | Extension directory |
| `.specify/extensions/{ext-id}/extension.yml` | Extension manifest |
| `.specify/extensions/{ext-id}/{ext-id}-config.yml` | User config (version controlled) |
| `.specify/extensions/{ext-id}/{ext-id}-config.local.yml` | Local overrides (gitignored) |
| `.specify/extensions/{ext-id}/commands/` | Command markdown files |
| `.specify/extensions/{ext-id}/scripts/` | Helper scripts |
| `.specify/extensions.yml` | Project extension config (hooks, settings) |
| `.specify/extension-catalogs.yml` | Project catalog stack config |
| `~/.specify/extension-catalogs.yml` | User catalog stack config |
| `.claude/commands/speckit.{ext}.{cmd}.md` | Registered Claude commands |
| `.gemini/commands/speckit.{ext}.{cmd}.toml` | Registered Gemini commands |

---

*This document extracted from SpecKit v0.1.0 reference documentation and RFC-EXTENSION-SYSTEM.md*
