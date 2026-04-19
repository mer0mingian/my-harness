# Workflow Definition Documentation

This directory contains documentation about OpenCode agent workflows and related tooling.

## External Resources

### 1. opencode-background-agents (kdcokenny)

**Repository:** https://github.com/kdcokenny/opencode-background-agents

**Commit:** 5ee26eed888b9071420f8d7d445e322412ac0c3d

**Summary:**
A plugin for OpenCode that enables async background delegation. Allows users to fire off research tasks, continue brainstorming or coding, and retrieve results when needed. Solves the context compaction problem where AI loses track of research when context windows fill up.

**Installation:**
```
ocx add kdco/background-agents --from https://registry.kdco.dev
```

Or for full experience with specialist agents, planning tools, and research protocols:
```
ocx add kdco/workspace --from https://registry.kdco.dev
```

---

### Agent Information (opencode-background-agents)

**Repository:** https://github.com/kdcokenny/opencode-background-agents

**Commit:** 5ee26eed888b9071420f8d7d445e322412ac0c3d

**Summary:**
A plugin for OpenCode that enables async background delegation. Allows users to fire off research tasks, continue brainstorming or coding, and retrieve results when needed. Solves the context compaction problem where AI loses track of research when context windows fill up.

**Installation:**
```
ocx add kdco/background-agents --from https://registry.kdco.dev
```

Or for full experience with specialist agents, planning tools, and research protocols:
```
ocx add kdco/workspace --from https://registry.kdco.dev
```

---

### Agent Information (opencode-background-agents)

#### Tools Provided

| Tool | Purpose |
|------|---------|
| `delegate(prompt, agent)` | Launch a background task |
| `delegation_read(id)` | Retrieve a specific result |
| `delegation_list()` | List all delegations with titles and summaries |

#### Delegation Routing

| Agent Type | Tool | Why |
|------------|------|-----|
| Read-only sub-agents | `delegate` | Background session, async |
| Write-capable sub-agents | `task` | Native task, preserves undo/branching |

**Constraint:** Only read-only sub-agents (permissions: `edit=deny`, `write=deny`, `bash={"*":"deny"}`) can use `delegate`. Write-capable sub-agents must use native `task` tool.

#### Lifecycle Behavior

The plugin mirrors Claude Code-style background-agent lifecycle behavior:

- Stable delegation IDs are reused across state, artifact path, notifications, and retrieval
- Explicit lifecycle transitions: `registered` → `running` → terminal
- Terminal-state protection (late progress events cannot regress terminal status)
- Persistence occurs before terminal notification delivery
- `delegation_read(id)` blocks until terminal/timeout and returns deterministic terminal info with persisted fallback
- Compaction carries forward running and unread completed delegation context with retrieval hints

#### Limitations

1. **Read-Only Sub-Agents Only**: Background delegations run in isolated sessions outside OpenCode's session tree. The undo/branching system cannot track changes made in background sessions.
2. **Timeout**: Delegations timeout after **15 minutes**.
3. **Real-Time Monitoring**: Use OpenCode navigation shortcuts:
   - `Ctrl+X Up` - Jump to parent session
   - `Ctrl+X Left` - Previous sub-agent
   - `Ctrl+X Right` - Next sub-agent

#### How It Works

```
1. delegate    →  "Research OAuth2 PKCE best practices"
2. Continue    →  Keep coding, brainstorming, reviewing
3. Notified    →  <task-notification> arrives on terminal state
4. Retrieve    →  AI calls delegation_read() to get the result
```

Results are persisted to `~/.local/share/opencode/delegations/` as markdown files.

---

### 2. subtask2 (spoons-and-mirrors)

**Repository:** https://github.com/spoons-and-mirrors/subtask2

**Commit:** 92cba0bf80af69662f642e37868923bc54a91c2e

**Summary:**
A plugin that enhances OpenCode's `/command` handler with chaining, relaying, ad-hoc subtasks, inline parameter overrides, and model aliases. Lowers session entropy with a more deterministic agentic loop.

**Installation:**
```json
{
  "plugins": ["@spoons-and-mirrors/subtask2@latest"]
}
```

---

### Key Features (subtask2)

#### 1. `return` - Chaining prompts and commands

Use `return` to tell the main agent what to do after a command completes. Supports prompts, /commands, and chaining.

```yaml
subtask: true
return: Look again, challenge the findings, then implement the valid fixes.
---
Review the PR# $ARGUMENTS for bugs.
```

Multiple sequential prompts:
```yaml
subtask: true
return:
  - Implement the fix
  - Run the tests
---
Find the bug in auth.ts
```

Trigger /commands in return:
```yaml
subtask: true
return:
  - /revise-plan make the UX as horribly impractical as imaginable
  - /implement-plan
---
Design the auth system for $ARGUMENTS
```

#### 2. Context & Results

##### `$TURN[n]` - Reference previous conversation turns

Inject previous conversation turns into commands:

```yaml
subtask: true
---
Review the following conversation and provide a concise summary:
$TURN[10]
```

**Syntax options:**
- `$TURN[6]` - last 6 turns (chronological order)
- `$TURN[:3]` - just the 3rd turn from the end
- `$TURN[:2:5:8]` - specific turns at indices 2, 5, and 8
- `$TURN[*]` - all turns in the session

Works in:
- Command body templates
- Command arguments
- Return prompts

##### `{as:name}` and `$RESULT[name]` - Named results

Capture command outputs and reference them later:

```yaml
return:
  - /research {as:research}
  - /design {as:design}
  - "Implement based on $RESULT[research] and $RESULT[design]"
```

Multi-model comparison:
```yaml
return:
  - /subtask {model:opus && as:opus-plan} Plan the auth system
  - /subtask {model:gpt && as:gpt-plan} Plan the auth system
  - "Compare $RESULT[opus-plan] vs $RESULT[gpt-plan] and pick the best approach"
```

#### 3. Inline Syntax - Overrides and ad-hoc subtasks

##### `{model:...}` - Model override

```bash
/plan {model:anthropic/claude-sonnet-4} design auth system
```

##### `{agent:...}` - Agent override

```bash
/research {agent:explore} find auth patterns
```

##### Combining overrides

Use `&&` to combine multiple overrides:

```bash
/plan {model:opus && agent:build && as:plan} implement the feature
```

##### `/subtask {...} prompt` - Ad-hoc subtasks

```yaml
return:
  - /subtask {model:openai/gpt-4o && agent:build} Implement the feature
  - Summarize what was done
```

With result capture:
```yaml
return:
  - /subtask {model:opus && as:analysis} Analyze the codebase
  - Based on $RESULT[analysis], implement the feature
```

##### Simple inline subtasks

```bash
/subtask tell me a joke
/subtask {model:openai/gpt-4o} analyze this code
/subtask {agent:explore && as:findings} find auth patterns
```

#### 4. Model Aliases

Create short names for frequently used models:

```bash
/subtask -a opus github-copilot/claude-opus-4.5
/subtask -a sonnet anthropic/claude-sonnet-4
/subtask -a gpt openai/gpt-4o
```

List aliases: `/subtask -a`

Delete alias: `/subtask -a opus -d`

Using aliases:
```bash
/subtask {model:opus} analyze this code
/mycommand {model:sonnet && agent:build} do the thing
```

Aliases are stored in `~/.config/opencode/subtask2.jsonc`.

#### 5. Generic Message Handling

When a `subtask: true` command completes, OpenCode injects a synthetic user message. Subtask2 intercepts this and replaces it with your `return` prompt.

**Priority:** `return` param > config `generic_return` > built-in default > opencode original

Configuration (`~/.config/opencode/subtask2.jsonc`):
```json
{
  "replace_generic": true,
  "generic_return": "custom return prompt",
  "model_aliases": {
    "opus": "github-copilot/claude-opus-4.5",
    "sonnet": "anthropic/claude-sonnet-4"
  }
}
```

#### Coming Soon

1. **Loop** - Run a command repeatedly until a condition is met (in development)
2. **Parallel** - Run multiple subtasks concurrently (pending PR #6478)

---

## Summary Table

| Feature | opencode-background-agents | subtask2 |
|---------|---------------------------|----------|
| **Primary Purpose** | Async background delegation | Enhanced command chaining |
| **Key Tools** | delegate, delegation_read, delegation_list | return, $TURN, $RESULT, {as:name} |
| **Model Override** | No | Yes ({model:...}) |
| **Agent Override** | No | Yes ({agent:...}) |
| **Result Capture** | Via delegation_read | Via {as:name} and $RESULT |
| **Timeout** | 15 minutes | N/A |
| **Installation** | ocx add kdco/background-agents | plugins in config |

---

## References

- OpenCode Commands Documentation: https://opencode.ai/docs/commands/
- OCX Registry: https://github.com/kdcokenny/ocx
- OCX Installation: https://github.com/kdcokenny/ocx

---

### 3. opencode-froggy (smartfrog)

**Repository:** https://github.com/smartfrog/opencode-froggy

**Commit:** fa0e4a4749186bd9dddb708669c86bce1be87155

**Summary:**
OpenCode plugin providing hooks, specialized agents (architect, doc-writer, rubber-duck, partner, code-reviewer, code-simplifier), skills (ask-questions-if-underspecified, tdd), and tools (gitingest, pdf-to-markdown, blockchain queries, agent-promote).

**Installation:**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-froggy"]
}
```

---

### Agents (opencode-froggy)

| Agent | Mode | Description |
|-------|------|-------------|
| `architect` | subagent | Strategic technical advisor providing high-leverage guidance on architecture, code structure, and complex engineering trade-offs. Read-only. |
| `doc-writer` | subagent | Technical writer that crafts clear, comprehensive documentation (README, API docs, architecture docs, user guides). |
| `code-reviewer` | subagent | Read-only code review agent for quality, correctness, security, and maintainability feedback. |
| `code-simplifier` | subagent | Simplifies recently modified code for clarity and maintainability while strictly preserving behavior. |
| `partner` | subagent | Strategic ideation partner that breaks frames, expands solution spaces, and surfaces non-obvious strategic options. Read-only. |
| `rubber-duck` | subagent | Strategic thinking partner for exploratory dialogue. Challenges assumptions, asks pointed questions, and sharpens thinking through conversational friction. Read-only. |

---

### Skills (opencode-froggy)

| Skill | Description |
|-------|-------------|
| `ask-questions-if-underspecified` | Clarify requirements before implementing. Use when serious doubts arise. |
| `tdd` | Apply Test-Driven Development workflow for new features and bugfixes. |

#### Skill Discovery Locations

Priority (highest to lowest):
1. Project: `<project>/.opencode/skill/`
2. Global: `~/.config/opencode/skill/`
3. Plugin: `<plugin>/skill/`

---

### Tools (opencode-froggy)

| Tool | Description |
|------|-------------|
| `gitingest` | Fetch a GitHub repository's full content via gitingest.com |
| `prompt-session` | Send a message to a child session (subagent) to continue the conversation |
| `list-child-sessions` | List all child sessions (subagents) of the current session |
| `pdf-to-markdown` | Convert a text-based PDF into enriched Markdown |
| `agent-promote` | Promote an agent to primary (default) or specify grade |
| Blockchain tools | `eth-transaction`, `eth-address-balance`, `eth-address-txs`, `eth-token-transfers` for Ethereum/EVM chains |

---

### Commands (opencode-froggy)

| Command | Description | Agent |
|---------|-------------|-------|
| `/agent-promote <name> [grade]` | Promote an agent to primary (default) or specify grade | - |
| `/agent-demote <name>` | Demote an agent to subagent | - |
| `/commit-push` | Stage, commit, and push changes with user confirmation | `build` |
| `/diff-summary [source] [target]` | Show working tree changes or diff between branches | - |
| `/doc-changes` | Update documentation based on uncommitted changes | `doc-writer` |
| `/review-changes` | Review uncommitted changes | `code-reviewer` |
| `/review-pr <source> <target>` | Review diff from source branch into target branch | `code-reviewer` |
| `/send-to [agent] <message>` | Send a message to a child session | - |
| `/simplify-changes` | Simplify uncommitted changes | `code-simplifier` |
| `/tests-coverage` | Run full test suite with coverage report and suggest fixes | `build` |

---

### Hooks (opencode-froggy)

Hooks run actions on session events. Configuration is loaded from standard OpenCode configuration directories.

**Supported Events:**
- `session.idle` - Emitted when a session becomes idle and has files modified via `write` or `edit`
- `session.created` - Emitted when a session is created
- `session.deleted` - Emitted when a session is deleted
- `tool.before.*` - Emitted before any tool executes
- `tool.after.*` - Emitted after any tool executes

**Conditions:**
- `isMainSession` - Run only for the main session
- `hasCodeChange` - Run only if at least one modified file looks like code

**Supported Actions:**
- Command action
- Tool action
- Bash action

---

### 4. opencode-plugin-openspec (Octane0411)

**Repository:** https://github.com/Octane0411/opencode-plugin-openspec

**Commit:** 54864428bd0cb2afeb36f6558ca714b7bbc1203f

**Summary:**
An OpenCode plugin that integrates OpenSpec, providing a dedicated agent for planning and specifying software architecture. Addresses the problem where AI agents attempt to start implementing code changes immediately before the planning phase is complete.

**Installation:**
```json
{
  "plugin": ["opencode-plugin-openspec"]
}
```

#### Agents (opencode-plugin-openspec)

| Agent | Mode | Description |
|-------|------|-------------|
| `openspec-plan` | primary | OpenSpec Architect - Plan and specify software architecture. Color: #FF6B6B |

**Allowed to edit:** `project.md`, `AGENTS.md`, `openspec/**`, `specs/**`
**Allowed bash:** openspec commands, git read-only, filesystem exploration
**Denied:** All other edit and bash operations (implementation code is read-only)

---

## Summary Table

| Feature | opencode-background-agents | subtask2 | opencode-froggy | opencode-plugin-openspec |
|---------|---------------------------|----------|-----------------|--------------------------|
| **Primary Purpose** | Async background delegation | Enhanced command chaining | Agents, skills, hooks, tools | OpenSpec planning agent |
| **Agents** | - | - | 6 (architect, code-reviewer, doc-writer, code-simplifier, partner, rubber-duck) | 1 (openspec-plan) |
| **Skills** | - | - | 2 (ask-questions-if-underspecified, tdd) | - |
| **Tools** | delegate, delegation_read, delegation_list | return, $TURN, $RESULT, {as:name} | gitingest, pdf-to-markdown, blockchain, agent-promote | - |
| **Commands** | - | - | 10+ | - |
| **Hooks** | - | - | Yes | - |
| **Timeout** | 15 minutes | N/A | N/A | N/A |
| **Installation** | ocx add kdco/background-agents | plugins in config | plugins in config | plugins in config |