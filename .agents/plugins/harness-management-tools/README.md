# Harness Management Tools Plugin

Plugin and extension management skills for Claude Code and SpecKit within the harness marketplace.

## Included Skills

### manage-plugin-creation

Master guide for creating Claude Code plugins from scratch. Covers:

- Plugin architecture and directory structure
- plugin.json manifest format and fields
- Adding skills, agents, commands to plugins
- Hooks and MCP server integration
- Local testing workflow
- Marketplace integration
- Best practices and troubleshooting

**Use when:**
- Creating new Claude Code plugins
- Understanding plugin structure
- Working with plugin manifests
- Testing plugins locally
- Preparing for marketplace distribution

### manage-speckit-extension

Guide for creating SpecKit extensions for Spec-Driven Development workflows. Covers:

- Extension architecture and directory structure
- extension.yml manifest format and fields
- Creating custom SpecKit commands
- Workflow hooks integration
- Helper scripts and config templates
- Publishing to catalogs
- Local testing and development

**Use when:**
- Building custom SpecKit commands
- Adding workflow hooks to SpecKit
- Integrating tools with SpecKit
- Creating organization-specific extensions
- Publishing to community or org catalogs

## Installation

This plugin is part of the harness-tooling marketplace. To use:

1. Add harness-tooling marketplace to Claude Code
2. Install this plugin
3. Skills will be available automatically

## Related Plugins

- **harness-agents**: TDD workflow specialist agents
- **harness-workflow-runtime**: Workflow resolution and execution

## Resources

### Claude Code Resources

- [Create plugins - Claude Code Docs](https://code.claude.com/docs/en/plugins)
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [GitHub - anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

### SpecKit Resources

- [SpecKit Extensions](https://github.com/github/spec-kit/tree/main/extensions)
- [Extension Development Guide](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-DEVELOPMENT-GUIDE.md)
- [Community Extensions](https://speckit-community.github.io/extensions/)

## License

See LICENSE file in the harness-tooling repository.
