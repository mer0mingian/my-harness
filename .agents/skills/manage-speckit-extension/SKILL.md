---
name: manage-speckit-extension
description: Create and manage SpecKit extensions for Spec-Driven Development workflows. Use when building custom SpecKit commands, adding workflow hooks, integrating external tools with SpecKit, extending the specify CLI, creating organization-specific SpecKit extensions, working with extension.yml manifests, publishing to extension catalogs, or when user mentions "create SpecKit extension", "SpecKit plugin", or "extend SpecKit".
---

# SpecKit Extension Creation

Guide for creating SpecKit extensions to add custom functionality to Spec-Driven Development workflows.

## Quick Start

### 1. Extension Directory Structure

Every SpecKit extension follows this structure:

```
my-extension/
├── extension.yml             # Required: Extension manifest
├── commands/                 # Optional: Command definitions
│   └── hello.md
├── scripts/                  # Optional: Helper scripts
│   ├── bash/
│   │   └── helper.sh
│   └── powershell/
│       └── helper.ps1
├── config/                   # Optional: Config templates
│   └── my-ext-config.template.yml
├── tests/                    # Optional: Test files
│   └── test_hello.py
├── README.md                 # Required: Documentation
└── LICENSE                   # Required: License file
```

### 2. Minimal Extension Manifest

**File**: `extension.yml`

```yaml
schema_version: "1.0"

extension:
  id: "my-ext"
  name: "My Extension"
  version: "1.0.0"
  description: "My custom extension"

requires:
  speckit_version: ">=0.1.0"

provides:
  commands:
    - name: "speckit.my-ext.hello"
      file: "commands/hello.md"
      description: "Say hello"
```

### 3. Create Command File

**File**: `commands/hello.md`

```markdown
---
description: "Say hello command"
tools:                              # Optional: AI tools this command uses
  - 'bash/execute'
scripts:                            # Optional: Helper scripts
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---

# Hello Command

This command says hello to the user.

## User Input

$ARGUMENTS

## Steps

1. Greet the user
2. Show extension is working
3. Display any provided arguments

```bash
echo "Hello from my extension!"
echo "Arguments: $ARGUMENTS"

# Load extension config if available
CONFIG_FILE=".specify/extensions/my-ext/my-ext-config.yml"
if [ -f "$CONFIG_FILE" ]; then
  echo "Config found: $CONFIG_FILE"
fi
```

## Expected Output

- Greeting message
- Argument display
- Config file status
```

### 4. Local Testing

```bash
# Install extension locally for testing
specify extension add --dev /path/to/my-extension

# Verify installation
specify extension list

# Test command (via Claude Code)
/speckit.my-ext.hello world

# Remove after testing
specify extension remove my-ext
```

## Extension Manifest Reference

For complete manifest specification, see [references/manifest.md](references/manifest.md):
- Required and optional fields
- Hook integration points
- Configuration options
- Version compatibility

## Command Creation

For detailed command patterns, see [references/commands.md](references/commands.md):
- Command file structure
- Available variables ($ARGUMENTS, $PROJECT_ROOT, etc.)
- Helper script integration
- Testing patterns

## Integration Patterns

Common extension patterns in [references/patterns.md](references/patterns.md):
- Tool integration extension (wrap external tools)
- Workflow extension (add custom steps)
- Domain-specific extension (org standards)
- Quality gate extension (validation hooks)

## Publishing Extensions

For publishing workflow, see [references/publishing.md](references/publishing.md):
- Prepare release checklist
- GitHub release process
- Community catalog submission
- Organization catalog setup

## Best Practices

### Command Naming
- Follow pattern: `speckit.{ext-id}.{command}`
- Use clear, descriptive command names
- Keep extension ID short (3-15 characters)
- Use hyphens for multi-word IDs

Examples:
- `speckit.docker.build`
- `speckit.sec.scan`
- `speckit.org.validate`

### Extension Scope
- **Keep focused**: One clear purpose per extension
- **Single responsibility**: Don't bundle unrelated functionality
- **Composable**: Allow combining with other extensions

### Configuration
- **Provide sensible defaults**: Extension works out of the box
- **Document config**: Clear examples in README
- **Validate config**: Check config at runtime, fail gracefully

### Testing
- **Test all commands**: Every command works as documented
- **Test hooks**: Hooks execute at correct points
- **Test dependencies**: Handle missing tools gracefully
- **Test edge cases**: Invalid input, missing config

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for solutions to:
- Extension not loading
- Commands not available
- Hooks not executing
- Dependency issues

## Extension Development Checklist

Before publishing:

- [ ] Valid extension.yml with all required fields
- [ ] README.md with installation and usage instructions
- [ ] LICENSE file included
- [ ] All commands tested and working
- [ ] Hooks tested (if included)
- [ ] Config templates provided (if needed)
- [ ] Helper scripts included (if needed)
- [ ] Version follows semantic versioning
- [ ] Git repository created
- [ ] GitHub release with version tag
- [ ] Catalog submission prepared (if applicable)
- [ ] Documentation complete

## Resources

- [SpecKit Extensions README](https://github.com/github/spec-kit/tree/main/extensions)
- [Extension Development Guide](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-DEVELOPMENT-GUIDE.md)
- [Extension API Reference](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-API-REFERENCE.md)
- [Community Extensions Catalog](https://speckit-community.github.io/extensions/)

## Related Skills

- `manage-plugin-creation`: Creating Claude Code plugins
- `manage-skill-creator`: Creating individual skills
- `python-packaging`: Python packaging for SpecKit extensions
