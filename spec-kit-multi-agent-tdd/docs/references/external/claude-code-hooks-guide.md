# Claude Code Hooks Guide

**Source:** https://code.claude.com/docs/en/hooks-guide  
**Reference:** https://code.claude.com/docs/en/hooks  
**Extracted:** 2026-05-07

## Table of Contents

- [Hooks Overview](#hooks-overview)
- [Hook Types](#hook-types)
- [Hook Implementation](#hook-implementation)
- [Executable Scripts via Hooks](#executable-scripts-via-hooks)
- [Hook Lifecycle](#hook-lifecycle)
- [Integration Patterns](#integration-patterns)
- [Code Examples](#code-examples)
- [Relevant to Our Use Case](#relevant-to-our-use-case)
- [Key Takeaways](#key-takeaways)

## Hooks Overview

### What Are Hooks?

Hooks are **user-defined shell commands** that execute at specific points in Claude Code's lifecycle. They provide **deterministic control** over Claude Code's behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them.

### Purpose

- **Enforce project rules** - Block dangerous commands, protect files
- **Automate repetitive tasks** - Format code, run tests, send notifications
- **Integrate with existing tools** - Connect to CI/CD, audit systems, external services
- **Control Claude's behavior** - Validate inputs, inject context, manage permissions

### When to Use Hooks

Use hooks for **deterministic rules** that should always apply:
- Auto-format code after edits
- Block edits to protected files
- Send notifications when Claude needs input
- Re-inject context after compaction
- Audit configuration changes
- Validate commands before execution

For decisions requiring **judgment**, use:
- **Prompt-based hooks** - Single-turn LLM evaluation
- **Agent-based hooks** - Multi-turn verification with tool access

### Complementary Extensions

- **Skills** (`/en/skills`) - Additional instructions and executable commands
- **Subagents** (`/en/sub-agents`) - Run tasks in isolated contexts
- **Plugins** (`/en/plugins`) - Package extensions to share across projects

## Hook Types

Claude Code supports five hook handler types:

### 1. Command Hooks (`type: "command"`)

**Most common type.** Run shell commands with JSON input/output.

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh",
  "async": false,
  "shell": "bash",
  "timeout": 600,
  "if": "Bash(git *)"
}
```

**Input:** JSON via stdin  
**Output:** Exit codes + stdout/stderr  
**Execution:** Synchronous by default, supports async mode

### 2. HTTP Hooks (`type: "http"`)

POST event data to HTTP endpoints. Useful for web services, cloud functions, shared audit systems.

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/tool-use",
  "headers": {
    "Authorization": "Bearer $MY_TOKEN"
  },
  "allowedEnvVars": ["MY_TOKEN"],
  "timeout": 30
}
```

**Input:** JSON as POST request body  
**Output:** HTTP response body (same JSON format as command hooks)  
**Environment:** Header values support `$VAR_NAME` interpolation

### 3. MCP Tool Hooks (`type: "mcp_tool"`)

Call tools on already-connected MCP servers.

```json
{
  "type": "mcp_tool",
  "server": "my_server",
  "tool": "security_scan",
  "input": { "file_path": "${tool_input.file_path}" },
  "timeout": 60
}
```

**Input:** Tool arguments with `${path}` substitution  
**Output:** Tool text output (parsed as JSON if valid)  
**Requirements:** MCP server must be connected

### 4. Prompt Hooks (`type: "prompt"`)

Single-turn LLM evaluation for decisions requiring judgment.

```json
{
  "type": "prompt",
  "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains\"}.",
  "model": "claude-sonnet-4-6",
  "timeout": 30
}
```

**Input:** Prompt with `$ARGUMENTS` placeholder  
**Output:** JSON with `{"ok": true/false, "reason": "..."}` decision  
**Default Model:** Haiku (configurable)

### 5. Agent Hooks (`type: "agent"`) - Experimental

Multi-turn verification with tool access (Read, Grep, Glob).

```json
{
  "type": "agent",
  "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
  "timeout": 120
}
```

**Input:** Prompt with `$ARGUMENTS` placeholder  
**Output:** JSON with `{"ok": true/false, "reason": "..."}` decision  
**Default Timeout:** 60 seconds, up to 50 tool-use turns  
**Status:** Experimental - behavior may change

## Hook Implementation

### Configuration Structure

Hooks use **three-level nesting**:

```json
{
  "hooks": {
    "EVENT_NAME": [              // Hook event
      {
        "matcher": "pattern",    // Matcher group
        "hooks": [               // Hook handlers
          {
            "type": "command",
            "command": "...",
            "if": "Tool(pattern)"
          }
        ]
      }
    ]
  }
}
```

### Hook Locations & Scope

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All your projects | No, local to your machine |
| `.claude/settings.json` | Single project | Yes, can be committed to repo |
| `.claude/settings.local.json` | Single project | No, gitignored |
| Managed policy settings | Organization-wide | Yes, admin-controlled |
| Plugin `hooks/hooks.json` | When plugin enabled | Yes, bundled with plugin |
| Skill/agent frontmatter | Component lifetime | Yes, defined in component file |

### Registration

Add hooks to any of the above locations. The file watcher picks up changes automatically. Run `/hooks` in Claude Code to browse all configured hooks.

To **disable all hooks**, set `"disableAllHooks": true` in settings.

### Hook Scripts

#### Shell Scripts

```bash
#!/bin/bash
# protect-files.sh

INPUT=$(cat)  # Read JSON from stdin
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2  # Exit code 2 = block
  fi
done

exit 0  # Exit code 0 = allow
```

**Make executable (macOS/Linux):**
```bash
chmod +x .claude/hooks/protect-files.sh
```

#### Python Scripts

```python
#!/usr/bin/env python3
import sys
import json

# Read JSON input from stdin
hook_input = json.load(sys.stdin)

command = hook_input.get('tool_input', {}).get('command', '')

# Validation logic
if 'rm -rf' in command:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Destructive command blocked"
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Allow by default
sys.exit(0)
```

**Make executable:**
```bash
chmod +x .claude/hooks/validate.py
```

## Executable Scripts via Hooks

### Execution Model

1. **Event fires** at lifecycle point (e.g., before tool execution)
2. **Claude Code spawns shell** (bash/zsh/cmd) with hook command
3. **JSON input piped to stdin** with event-specific data
4. **Script processes input** and makes decision
5. **Output via stdout/stderr and exit code**
6. **Claude Code processes result** - allow, block, or add context

### Input/Output Contract

#### Input Format (stdin)

Every hook receives JSON on stdin with common fields:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|auto|dontAsk|bypassPermissions",
  "hook_event_name": "PreToolUse",
  "agent_id": "unique-id",      // only in subagents
  "agent_type": "Explore"       // only with --agent or in subagents
}
```

Plus event-specific fields. Example for `PreToolUse`:

```json
{
  "session_id": "abc123",
  "cwd": "/Users/sarah/myproject",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "tool_use_id": "toolu_01xyz"
}
```

#### Output Format

**Exit Codes:**

| Code | Meaning | Processing |
|------|---------|------------|
| **0** | Success | Parse stdout for JSON output |
| **2** | Blocking error | Ignore stdout, use stderr as error message |
| **Other** | Non-blocking error | Show stderr in transcript, continue |

**Structured JSON Output (exit 0):**

```json
{
  "continue": true,
  "stopReason": "Build failed",
  "suppressOutput": false,
  "systemMessage": "Warning message",
  "decision": "block",
  "reason": "Explanation",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "Text",
    "updatedInput": { "modified": "fields" },
    "additionalContext": "Context for Claude",
    "sessionTitle": "Auto-generated session name"
  }
}
```

**Simple stderr output (exit 2):**

```bash
echo "Blocked: dropping tables is not allowed" >&2
exit 2
```

### Environment Variables

**Available in all hooks:**
- `$CLAUDE_PROJECT_DIR` - Project root (quote for spaces: `"$CLAUDE_PROJECT_DIR"`)
- `$CLAUDE_CODE_REMOTE` - `"true"` in web, unset in local CLI
- Standard shell environment

**Available in SessionStart, Setup, CwdChanged, FileChanged:**
- `$CLAUDE_ENV_FILE` - Path to file for persisting env vars to subsequent Bash commands

**In plugin hooks:**
- `${CLAUDE_PLUGIN_ROOT}` - Plugin installation directory
- `${CLAUDE_PLUGIN_DATA}` - Plugin persistent data directory

#### Persisting Environment Variables

```bash
# In SessionStart or CwdChanged hook
direnv export bash > "$CLAUDE_ENV_FILE"

# Or manually:
echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
echo 'export DEBUG=true' >> "$CLAUDE_ENV_FILE"
```

Claude Code sources `$CLAUDE_ENV_FILE` as a script preamble before each Bash command.

### Security Considerations

- **Hook scripts have full shell access** - treat as privileged code
- **Scripts execute in user's shell environment** - sourcing profile files
- **Managed settings can override** - enterprise policies take precedence
- **Deny rules always win** - hooks can't bypass managed deny lists
- **Review third-party plugins** - they can include hooks with arbitrary code execution

**Prevent shell profile pollution:**

```bash
# In ~/.zshrc or ~/.bashrc
if [[ $- == *i* ]]; then
  echo "Shell ready"  # Only in interactive shells
fi
```

## Hook Lifecycle

### All Hook Events

| Event | When it fires | Category |
|-------|---------------|----------|
| `SessionStart` | Session begins or resumes | Session-level |
| `Setup` | `--init-only`, `--init`, or `--maintenance` in `-p` mode | Session-level |
| `SessionEnd` | Session terminates | Session-level |
| `UserPromptSubmit` | User submits prompt | Turn-level |
| `UserPromptExpansion` | User command expands into prompt | Turn-level |
| `Stop` | Claude finishes responding | Turn-level |
| `StopFailure` | Turn ends due to API error | Turn-level |
| `PreToolUse` | Before tool call executes | Agentic loop |
| `PermissionRequest` | Permission dialog appears | Agentic loop |
| `PermissionDenied` | Tool denied by auto mode classifier | Agentic loop |
| `PostToolUse` | After tool call succeeds | Agentic loop |
| `PostToolUseFailure` | After tool call fails | Agentic loop |
| `PostToolBatch` | After full batch of parallel tool calls | Agentic loop |
| `Notification` | Claude Code sends notification | Async events |
| `FileChanged` | Watched file changes on disk | Async events |
| `CwdChanged` | Working directory changes | Async events |
| `ConfigChange` | Configuration file changes during session | Async events |
| `InstructionsLoaded` | CLAUDE.md or rules loaded into context | Async events |
| `PreCompact` | Before context compaction | Async events |
| `PostCompact` | After context compaction | Async events |
| `WorktreeCreate` | Worktree being created | Async events |
| `WorktreeRemove` | Worktree being removed | Async events |
| `SubagentStart` | Subagent spawned | Specialized |
| `SubagentStop` | Subagent finishes | Specialized |
| `TeammateIdle` | Agent team teammate about to go idle | Specialized |
| `TaskCreated` | Task being created via TaskCreate | Specialized |
| `TaskCompleted` | Task being marked as completed | Specialized |
| `Elicitation` | MCP server requests user input | Specialized |
| `ElicitationResult` | After user responds to MCP elicitation | Specialized |

### Matcher Patterns by Event

Each event type matches on a specific field:

| Event | Matches | Example Values |
|-------|---------|----------------|
| Tool events (`PreToolUse`, `PostToolUse`, etc.) | Tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | Session source | `startup`, `resume`, `clear`, `compact` |
| `Setup` | CLI flag | `init`, `maintenance` |
| `SessionEnd` | Exit reason | `clear`, `logout`, `prompt_input_exit` |
| `Notification` | Notification type | `permission_prompt`, `idle_prompt`, `auth_success` |
| `SubagentStart`/`SubagentStop` | Agent type | `general-purpose`, `Explore`, `Plan` |
| `PreCompact`/`PostCompact` | Trigger | `manual`, `auto` |
| `ConfigChange` | Config source | `user_settings`, `project_settings`, `skills` |
| `FileChanged` | Literal filenames (pipe-separated) | `.envrc\|.env` |
| `StopFailure` | Error type | `rate_limit`, `authentication_failed`, `server_error` |
| `InstructionsLoaded` | Load reason | `session_start`, `nested_traversal`, `include` |
| `UserPromptExpansion` | Command name | Your skill/command names |
| `Elicitation`/`ElicitationResult` | MCP server name | Your configured MCP servers |

**Events with no matcher support:**
`UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `CwdChanged`

### Matcher Pattern Syntax

| Pattern | Evaluated As | Example |
|---------|--------------|---------|
| `"*"`, `""`, or omitted | Match all | Fires on every occurrence |
| Letters, digits, `_`, `\|` only | Exact string or pipe-separated list | `Bash`, `Edit\|Write` |
| Contains other characters | JavaScript regex | `^Notebook`, `mcp__.*` |

**Match MCP tools:**

MCP tools use pattern: `mcp__<server>__<tool>`

```json
{
  "matcher": "mcp__memory__.*"     // All tools from memory server
}
{
  "matcher": "mcp__.*__write.*"    // Any write tool from any server
}
```

### Advanced Filtering: The `if` Field

**Requires:** Claude Code v2.1.85+

The `if` field uses **permission rule syntax** to filter hooks by tool name AND arguments together.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git *)",
            "command": "check-git-policy.sh"
          }
        ]
      }
    ]
  }
}
```

**Behavior:**
- Hook process spawns ONLY when:
  - Subcommand matches pattern (e.g., `git push`)
  - Command too complex to parse
- Works on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`
- Other events: adding `if` prevents hook from running

**Examples:**
- `"Bash(git *)"` - Git commands only
- `"Edit(*.ts)"` - TypeScript files only
- `"Bash(npm test)"` - Specific npm command

### Execution Flow

1. **Event fires** at lifecycle point
2. **All matching matcher groups selected** based on matcher pattern
3. **For each matching group:**
   - Filter handlers by `if` field (if present)
   - Run matching handlers **in parallel**
   - **Deduplication:** Identical commands run once
4. **Aggregate results:**
   - **Decision precedence:** Most restrictive wins
   - **Context aggregation:** All `additionalContext` combined
5. **Apply decision** to Claude Code behavior

### Async Hooks (Background Execution)

```json
{
  "type": "command",
  "command": "npm run type-check && npm run lint",
  "async": true,
  "asyncRewake": false
}
```

| Option | Behavior |
|--------|----------|
| `async: true` | Run in background, don't block |
| `asyncRewake: true` | Run in background, wake Claude on exit code 2 with stderr/stdout as system reminder |

**Use cases:**
- Long-running CI/CD operations
- File uploads
- Monitoring/polling
- Background validation

## Integration Patterns

### Hooks + Commands

**Pattern 1: Hooks Can Execute Commands**

```bash
#!/bin/bash
# Hook script that calls external command

# Validate with external tool
"$CLAUDE_PROJECT_DIR"/bin/validate-change.sh "$FILE_PATH"

if [ $? -ne 0 ]; then
  echo "Validation failed" >&2
  exit 2
fi
```

**Pattern 2: Commands Cannot Directly Invoke Hooks**

Commands run as regular tools. Hooks fire automatically based on lifecycle events. To trigger hook behavior from a command, emit the event the hook watches (e.g., edit a file to trigger `PostToolUse`).

### Hooks + Skills

**Skill-Scoped Hooks** (defined in skill frontmatter):

```yaml
---
name: my-skill
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
---
```

**Scope:** Active only while skill is active. Cleaned up when skill finishes.

**Use cases:**
- Skill-specific validations
- Temporary behavior overrides
- Component-specific automation

### Hooks + MCP Servers

**MCP Tool Hooks:**

```json
{
  "type": "mcp_tool",
  "server": "security_scanner",
  "tool": "scan_file",
  "input": {
    "file_path": "${tool_input.file_path}",
    "check_type": "security"
  }
}
```

**Substitution Variables:**
- `${tool_name}` - Current tool name
- `${tool_input.*}` - Tool input fields
- Other hook input fields

**Requirements:**
- MCP server must be already connected
- Tool must be available on that server

### Common Orchestration Patterns

#### 1. Auto-Approve + Context Injection

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\", \"updatedPermissions\": [{\"type\": \"setMode\", \"mode\": \"acceptEdits\", \"destination\": \"session\"}]}}}'"
          }
        ]
      }
    ]
  }
}
```

Auto-approves ExitPlanMode AND switches to acceptEdits mode.

#### 2. Validation Pipeline

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "if": "Edit(*.py)",
            "command": "validate-python.sh"
          },
          {
            "type": "command",
            "if": "Edit(*.ts)",
            "command": "validate-typescript.sh"
          }
        ]
      }
    ]
  }
}
```

Multiple validators run in parallel, all must pass.

#### 3. Environment Reload Chain

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ],
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ],
    "FileChanged": [
      {
        "matcher": ".envrc|.env",
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

Keeps environment synchronized across directory changes and file updates.

## Code Examples

### Example 1: Auto-Format Code After Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

### Example 2: Block Protected Files

```bash
#!/bin/bash
# .claude/hooks/protect-files.sh

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

**Registration:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

### Example 3: Desktop Notifications

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

**Platform variants:**
- **macOS:** `osascript -e 'display notification "..." with title "..."'`
- **Linux:** `notify-send 'Claude Code' 'Claude Code needs your attention'`
- **Windows:** `powershell.exe -Command "[System.Windows.Forms.MessageBox]::Show(...)"`

### Example 4: Re-Inject Context After Compaction

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}
```

Text written to stdout is added to Claude's context.

### Example 5: Audit Configuration Changes

```json
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log"
          }
        ]
      }
    ]
  }
}
```

### Example 6: Environment Reload with direnv

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ],
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

### Example 7: Python Hook - Validate Bash Commands

```python
#!/usr/bin/env python3
"""
Hook script: Validate Bash commands before execution.
Blocks destructive patterns and logs command history.
"""
import sys
import json
import re
from datetime import datetime

def validate_command(command: str) -> tuple[bool, str]:
    """Validate command against blocklist patterns."""
    
    dangerous_patterns = [
        (r'rm\s+-rf\s+/', 'Destructive rm -rf on root'),
        (r'chmod\s+777', 'Overly permissive chmod'),
        (r'DROP\s+TABLE', 'SQL DROP TABLE'),
        (r'>\s*/dev/sd[a-z]', 'Direct disk write'),
    ]
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, reason
    
    return True, ""

def log_command(command: str, allowed: bool, reason: str = ""):
    """Log command to audit file."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "command": command,
        "allowed": allowed,
        "reason": reason
    }
    
    with open("/tmp/claude-command-audit.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def main():
    # Read JSON input from stdin
    hook_input = json.load(sys.stdin)
    
    # Extract command
    command = hook_input.get('tool_input', {}).get('command', '')
    
    # Validate
    allowed, reason = validate_command(command)
    
    # Log
    log_command(command, allowed, reason)
    
    if not allowed:
        # Return structured JSON denial
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Blocked: {reason}"
            }
        }
        print(json.dumps(output))
        sys.exit(0)
    
    # Allow command
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**Registration:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-bash.py"
          }
        ]
      }
    ]
  }
}
```

### Example 8: HTTP Hook - External Validation Service

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "http",
            "url": "https://compliance-service.company.com/validate-code-change",
            "headers": {
              "Authorization": "Bearer $COMPLIANCE_API_KEY",
              "X-Team-ID": "$TEAM_ID"
            },
            "allowedEnvVars": ["COMPLIANCE_API_KEY", "TEAM_ID"],
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Example 9: Prompt Hook - Quality Gate

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the changes made in this turn. Check if: 1) All requested features are implemented, 2) Tests are written, 3) Documentation is updated. If any are missing, respond with {\"ok\": false, \"reason\": \"what's missing\"}. Otherwise respond with {\"ok\": true}.",
            "model": "claude-sonnet-4-6",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Example 10: Agent Hook - Test Verification

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite with 'npm test' and check the results. If any tests fail, respond with {\"ok\": false, \"reason\": \"test failure details\"}. If all pass, respond with {\"ok\": true}. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## Relevant to Our Use Case

### spec-kit-multi-agent-tdd Python Scripts

The spec-kit-multi-agent-tdd project has Python scripts that could be integrated via hooks:

#### Integration Strategy

**1. Python Script Hooks for Workflow Automation**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "if": "Edit(*.py)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/spec-kit-multi-agent-tdd/scripts/validate-python-edit.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "if": "Edit(tests/*.py)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/spec-kit-multi-agent-tdd/scripts/run-affected-tests.py"
          }
        ]
      }
    ]
  }
}
```

**2. Spec Validation Hooks**

```python
#!/usr/bin/env python3
"""
Hook: Validate that code changes align with spec.
Location: spec-kit-multi-agent-tdd/hooks/validate-spec-alignment.py
"""
import sys
import json
from pathlib import Path

def load_spec(spec_path: Path) -> dict:
    """Load project spec from YAML/JSON."""
    # Implementation
    pass

def validate_against_spec(file_path: str, spec: dict) -> tuple[bool, str]:
    """Check if edited file aligns with spec requirements."""
    # Implementation
    pass

def main():
    hook_input = json.load(sys.stdin)
    file_path = hook_input.get('tool_input', {}).get('file_path', '')
    
    # Load spec
    spec = load_spec(Path('spec-kit-multi-agent-tdd/spec.yaml'))
    
    # Validate
    valid, reason = validate_against_spec(file_path, spec)
    
    if not valid:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Spec violation: {reason}"
            }
        }
        print(json.dumps(output))
    
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**3. Test-Driven Development Enforcement**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "if": "Edit(src/*.py)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/spec-kit-multi-agent-tdd/hooks/enforce-tdd.py"
          }
        ]
      }
    ]
  }
}
```

```python
#!/usr/bin/env python3
"""
Hook: Enforce TDD - block src edits if no corresponding test exists.
"""
import sys
import json
from pathlib import Path

def has_corresponding_test(src_file: str) -> bool:
    """Check if test file exists for source file."""
    src_path = Path(src_file)
    test_path = Path('tests') / f"test_{src_path.name}"
    return test_path.exists()

def main():
    hook_input = json.load(sys.stdin)
    file_path = hook_input.get('tool_input', {}).get('file_path', '')
    
    if file_path.startswith('src/') and not has_corresponding_test(file_path):
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "TDD violation: No test file exists. Create test first."
            }
        }
        print(json.dumps(output))
    
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**4. Context Injection for BMAD Workflow**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/spec-kit-multi-agent-tdd/hooks/inject-bmad-context.py"
          }
        ]
      }
    ]
  }
}
```

```python
#!/usr/bin/env python3
"""
Hook: Inject BMAD workflow context at session start.
"""
import sys
import json
from pathlib import Path

def get_current_phase() -> str:
    """Determine current BMAD phase from project state."""
    # Read from .bmad-state or similar
    pass

def get_phase_instructions(phase: str) -> str:
    """Get instructions for current phase."""
    instructions = {
        "requirements": "Focus on gathering requirements. Use /brainstorm and /grill-me.",
        "design": "Focus on architecture. Use /arch-c4 and /arch-writing-plans.",
        "implementation": "Focus on TDD. Use /stdd-test-driven-development.",
        "verification": "Focus on validation. Use /general-verification-before-completion."
    }
    return instructions.get(phase, "")

def main():
    phase = get_current_phase()
    instructions = get_phase_instructions(phase)
    
    context = f"""
BMAD Workflow Context:
- Current Phase: {phase}
- Phase Instructions: {instructions}
- Spec Location: spec-kit-multi-agent-tdd/spec.yaml
- Test Strategy: TDD with pytest
"""
    
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }
    print(json.dumps(output))
    sys.exit(0)

if __name__ == '__main__':
    main()
```

### Recommended Hook Locations for spec-kit-multi-agent-tdd

```
spec-kit-multi-agent-tdd/
├── .claude/
│   ├── hooks/
│   │   ├── validate-spec-alignment.py
│   │   ├── enforce-tdd.py
│   │   ├── inject-bmad-context.py
│   │   └── run-affected-tests.py
│   └── settings.json              # Hook registrations
├── scripts/
│   └── validate-python-edit.py
└── spec.yaml
```

### Integration Benefits

1. **Automatic Spec Enforcement** - Hooks block changes that violate spec
2. **TDD Guardrails** - Prevent implementation before tests
3. **Phase-Aware Context** - Inject relevant instructions per BMAD phase
4. **Continuous Testing** - Run affected tests after each edit
5. **Audit Trail** - Log all spec violations and decisions

## Key Takeaways

### Core Concepts

1. **Hooks provide deterministic control** - Unlike LLM-based decisions, hooks ALWAYS fire at lifecycle points
2. **Five hook types** - command, http, mcp_tool, prompt, agent (experimental)
3. **Three-level nesting** - event → matcher group → handler
4. **Parallel execution** - All matching hooks run simultaneously, results aggregated
5. **Most restrictive wins** - One deny overrides all allows

### Executable Scripts

1. **Shell scripts are first-class** - Bash, Python, Node.js, any executable
2. **JSON input on stdin** - Structured data with event-specific fields
3. **Exit codes control behavior** - 0=allow, 2=block, other=non-blocking error
4. **Structured JSON output** - For complex decisions beyond allow/block
5. **Environment variables available** - `$CLAUDE_PROJECT_DIR`, `$CLAUDE_ENV_FILE` (selective)

### Best Practices

1. **Use matchers to scope hooks** - Don't fire on every event
2. **Use `if` field for fine-grained control** - Filter by tool name AND arguments
3. **Make scripts executable** - `chmod +x` on macOS/Linux
4. **Quote paths with spaces** - `"$CLAUDE_PROJECT_DIR"`
5. **Return JSON for complex decisions** - Exit 0 + JSON output
6. **Use stderr for human messages** - Exit 2 + stderr for blocking
7. **Avoid shell profile pollution** - Wrap `echo` in `if [[ $- == *i* ]]`
8. **Test hooks manually** - Pipe sample JSON to script
9. **Check `/hooks` menu** - Verify registration
10. **Use async for long operations** - Don't block the session

### Security

1. **Hooks have full shell access** - Treat as privileged code
2. **Managed settings override user hooks** - Enterprise policies win
3. **Deny rules always take precedence** - Hooks can't bypass deny lists
4. **Review third-party plugins** - They can include arbitrary hooks
5. **Use `allowedEnvVars` for HTTP headers** - Explicit allowlist for security

### Limitations

1. **Hooks can't call `/` commands** - Only shell commands and tools
2. **PostToolUse can't undo** - Tool already executed
3. **PermissionRequest doesn't fire in `-p` mode** - Use PreToolUse instead
4. **Stop hooks fire on every response** - Not just task completion
5. **Multiple `updatedInput` hooks race** - Last one wins (non-deterministic)
6. **10-minute default timeout** - Configurable per hook

### Integration Opportunities

1. **Spec-driven development** - Validate changes against spec YAML
2. **TDD enforcement** - Block implementation without tests
3. **Phase-aware workflows** - Inject context per BMAD phase
4. **Continuous testing** - Run affected tests after edits
5. **Audit logging** - Track all spec violations and decisions
6. **External compliance** - HTTP hooks to corporate validation services
7. **Auto-formatting** - Format code after every edit
8. **Environment sync** - Reload env vars with direnv/devbox on changes

### Debugging

1. **`/hooks` menu** - Browse all configured hooks
2. **`--debug-file /tmp/claude.log`** - Full execution logs
3. **`/debug`** - Enable logging mid-session
4. **Test scripts manually** - `echo '{"tool_name":"Bash"}' | ./hook.sh`
5. **Check exit codes** - `echo $?` after manual test
6. **Validate JSON** - Ensure no shell profile pollution
7. **Make scripts executable** - Common cause of "command not found"
8. **Verify file paths** - Use absolute paths or `$CLAUDE_PROJECT_DIR`

### Further Reading

- **Hooks Reference** (`/en/hooks`) - Full event schemas and advanced features
- **Skills Guide** (`/en/skills`) - Complement hooks with instructions
- **Permissions Guide** (`/en/permissions`) - How hooks interact with permission rules
- **Subagents Guide** (`/en/sub-agents`) - Isolated execution contexts
- **Plugins Guide** (`/en/plugins`) - Package hooks for sharing
