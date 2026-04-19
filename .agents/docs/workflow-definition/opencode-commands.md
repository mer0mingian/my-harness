# OpenCode Commands Documentation

This document summarizes the OpenCode commands system from https://opencode.ai/docs/commands/

## Overview

Custom commands let you specify a prompt you want to run when that command is executed in the TUI. They are in addition to built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`.

## Creating Commands

### File-Based Commands

Create markdown files in the `commands/` directory:

**Location:**
- Global: `~/.config/opencode/commands/`
- Per-project: `.opencode/commands/`

**File:** `.opencode/commands/test.md`
```yaml
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---
Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

**Usage:** `/test`

### JSON Configuration

Add commands via OpenCode config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report...",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

## Prompt Config

### Arguments

| Placeholder | Description |
|--------------|-------------|
| `$ARGUMENTS` | All arguments passed to command |
| `$1` | First argument |
| `$2` | Second argument |
| `$3` | Third argument |
| ... | And so on... |

**Example:**
```yaml
---
description: Create a new file
---
Create a file named $1 in directory $2 with content: $3
```

Usage: `/create-file config.json src "{ \"key\": \"value\" }"`

### Shell Output

Use *!`command`* to inject bash command output into your prompt:

```yaml
---
description: Analyze test coverage
---
Here are the current test results:
!`npm test`
Based on these results, suggest improvements to increase coverage.
```

Commands run in the project's root directory.

### File References

Include files using `@` followed by the filename:

```yaml
---
description: Review component
---
Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

## Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `template` | string | Yes | The prompt sent to the LLM |
| `description` | string | No | Shown in TUI |
| `agent` | string | No | Which agent executes (defaults to current) |
| `subtask` | boolean | No | Force subagent invocation |
| `model` | string | No | Override default model |

### Agent Option

Specifies which agent should execute the command. If it's a subagent, triggers subagent invocation by default. Set `subtask: false` to disable.

### Subtask Option

Forces the command to trigger a subagent invocation. Useful to avoid polluting primary context, even if agent is set to `primary` mode.

### Model Option

Overrides the default model for this specific command.

## Built-in Commands

OpenCode includes built-in commands:
- `/init` - Initialize a project
- `/undo` - Undo last action
- `/redo` - Redo last action
- `/share` - Share current session
- `/help` - Show help

**Note:** Custom commands can override built-in commands.

## Related Plugins

This commands system is enhanced by:
- **subtask2** - Adds chaining, `$TURN[n]`, `$RESULT[name]`, `{as:name}` capture, inline overrides (`{model:}`, `{agent:}`), and model aliases

See main README for more details on subtask2 features.