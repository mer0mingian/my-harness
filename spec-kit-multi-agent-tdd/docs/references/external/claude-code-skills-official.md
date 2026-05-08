# Claude Code Skills - Official Documentation

**Source:** https://code.claude.com/docs/en/skills  
**Extracted:** 2026-05-07  
**Related Sources:**
- Agent Skills Open Standard: https://agentskills.io
- Claude Code Commands Reference: https://code.claude.com/docs/en/commands

## Table of Contents

1. [Skills Overview](#skills-overview)
2. [Skills vs Commands](#skills-vs-commands)
3. [File Structure](#file-structure)
4. [Skill Format Specification](#skill-format-specification)
5. [Where Skills Live](#where-skills-live)
6. [Configuration via Frontmatter](#configuration-via-frontmatter)
7. [Types of Skill Content](#types-of-skill-content)
8. [Implementation Patterns](#implementation-patterns)
9. [Advanced Patterns](#advanced-patterns)
10. [Bundled Skills](#bundled-skills)
11. [Best Practices](#best-practices)
12. [Key Takeaways](#key-takeaways)

---

## Skills Overview

### What are Skills?

From the official documentation:

> Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

**Key characteristics:**

- Skills are markdown files containing instructions for Claude
- Can be invoked directly by users with `/skill-name` slash commands
- Can be automatically loaded by Claude when relevant to the conversation
- Follow the [Agent Skills](https://agentskills.io) open standard
- Support dynamic context injection via shell command execution
- Can run in isolated subagent contexts
- Content loads only when used, minimizing token cost

### When to Create a skill

Create a skill when you:

- Keep pasting the same instructions, checklist, or multi-step procedure into chat
- Have a section of CLAUDE.md that has grown into a procedure rather than a fact
- Want procedural knowledge that only loads when needed
- Need repeatable workflows with side effects (deploy, commit, etc.)

**The key insight from the docs:**

> Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it.

---

## Skills vs Commands

### Unified System

**Important note from the documentation:**

> **Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Your existing `.claude/commands/` files keep working. Skills add optional features: a directory for supporting files, frontmatter to control whether you or Claude invokes them, and the ability for Claude to load them automatically when relevant.

### Comparison Table

| Aspect | Built-in Commands | Bundled Skills | Custom Skills |
|--------|------------------|----------------|---------------|
| **Implementation** | Fixed logic coded into CLI | Prompt-based (detailed instructions) | User-defined markdown |
| **Examples** | `/help`, `/compact`, `/model` | `/simplify`, `/batch`, `/debug`, `/loop` | User-created workflows |
| **Invocation** | User only | User or Claude (auto) | User or Claude (configurable) |
| **Location** | Built into CLI | Built into CLI | User/project/plugin directories |
| **Customization** | None | None | Full control |
| **Token cost** | Zero (fixed logic) | When invoked | Only when loaded |

### Key Distinction

From the documentation:

> Unlike most built-in commands, which execute fixed logic directly, bundled skills are prompt-based: they give Claude detailed instructions and let it orchestrate the work using its tools. You invoke them the same way as any other skill, by typing `/` followed by the skill name.

---

## File Structure

### Basic Structure

Every skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md           # Required: main instructions
├── template.md        # Optional: template for Claude to fill in
├── examples/
│   └── sample.md      # Optional: example output showing expected format
├── scripts/
│   └── validate.sh    # Optional: script Claude can execute
└── references/
    └── detailed.md    # Optional: detailed reference documentation
```

### Directory Locations

Where you store a skill determines who can use it:

| Location | Path | Applies to |
|----------|------|------------|
| **Enterprise** | See managed settings | All users in your organization |
| **Personal** | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| **Project** | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| **Plugin** | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

**Precedence:** Enterprise > Personal > Project

**Plugin namespacing:** Plugin skills use `plugin-name:skill-name` namespace to avoid conflicts.

### Legacy Command Files

Files in `.claude/commands/` still work but skills are recommended:

```
.claude/commands/deploy.md  # Legacy (still works)
.claude/skills/deploy/SKILL.md  # Recommended (more features)
```

If a skill and command share the same name, the skill takes precedence.

### Live Change Detection

From the documentation:

> Claude Code watches skill directories for file changes. Adding, editing, or removing a skill under `~/.claude/skills/`, the project `.claude/skills/`, or a `.claude/skills/` inside an `--add-dir` directory takes effect within the current session without restarting.

**Exception:** Creating a top-level skills directory that didn't exist when the session started requires restarting Claude Code.

### Automatic Discovery from Nested Directories

When working with files in subdirectories, Claude Code automatically discovers skills from nested `.claude/skills/` directories. Example:

```
packages/frontend/
└── .claude/skills/
    └── frontend-patterns/
        └── SKILL.md
```

This supports monorepo setups where packages have their own skills.

---

## Skill Format Specification

### Agent Skills Open Standard

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which is an open format that works across multiple AI tools (Claude Code, OpenCode, Gemini CLI, Cursor, GitHub Copilot, and others).

### SKILL.md Format

Every `SKILL.md` file contains two parts:

1. **YAML frontmatter** between `---` markers (optional but recommended)
2. **Markdown content** with the instructions Claude follows

### Minimal Example

```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```

### Agent Skills Spec Requirements

From the Agent Skills specification (https://agentskills.io/specification):

#### Required Fields

| Field | Constraints | Description |
|-------|-------------|-------------|
| `name` | Max 64 chars, lowercase letters/numbers/hyphens only, must not start/end with hyphen, must match directory name | Skill identifier |
| `description` | Max 1024 chars, non-empty | What the skill does and when to use it |

#### Optional Fields (Agent Skills Spec)

| Field | Constraints | Description |
|-------|-------------|-------------|
| `license` | No limit | License name or reference |
| `compatibility` | Max 500 chars | Environment requirements |
| `metadata` | Key-value map | Arbitrary additional metadata |
| `allowed-tools` | Space-separated string | Pre-approved tools (experimental) |

### Claude Code Extensions

Claude Code extends the Agent Skills standard with additional frontmatter fields:

---

## Configuration via Frontmatter

### Complete Frontmatter Reference

All fields are optional except where noted. Only `description` is recommended.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name. If omitted, uses directory name. Lowercase letters, numbers, hyphens only (max 64 chars) |
| `description` | **Recommended** | What the skill does and when to use it. Claude uses this to decide when to apply the skill |
| `when_to_use` | No | Additional context for when Claude should invoke the skill. Appended to `description` |
| `argument-hint` | No | Hint shown during autocomplete, e.g., `[issue-number]` or `[filename] [format]` |
| `arguments` | No | Named positional arguments for `$name` substitution. Space-separated string or YAML list |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from auto-loading. Use for manual-only workflows. Default: `false` |
| `user-invocable` | No | Set to `false` to hide from `/` menu. Use for background knowledge. Default: `true` |
| `allowed-tools` | No | Tools Claude can use without asking permission. Space-separated string or YAML list |
| `model` | No | Model to use when skill is active. Accepts same values as `/model` command |
| `effort` | No | Effort level when skill is active. Options: `low`, `medium`, `high`, `xhigh`, `max` |
| `context` | No | Set to `fork` to run in a forked subagent context |
| `agent` | No | Which subagent type to use when `context: fork` is set |
| `hooks` | No | Hooks scoped to this skill's lifecycle |
| `paths` | No | Glob patterns that limit when skill is activated. Comma-separated or YAML list |
| `shell` | No | Shell to use for `` !`command` `` blocks. Options: `bash` (default) or `powershell` |

### Example: Complete Frontmatter

```yaml
---
name: deploy
description: Deploy the application to production
when_to_use: Use when the user asks to deploy, push to production, or release a new version
argument-hint: [environment]
arguments: [environment]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(npm *)
model: claude-sonnet-4.5
effort: high
context: fork
agent: general-purpose
paths: "src/**/*.ts, package.json"
shell: bash
---

Deploy to $environment:
1. Run tests
2. Build application  
3. Push to deployment target
4. Verify deployment
```

### Control Who Invokes a Skill

From the documentation:

> By default, both you and Claude can invoke any skill. You can type `/skill-name` to invoke it directly, and Claude can load it automatically when relevant to your conversation.

#### Invocation Control Fields

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
|-------------|----------------|-------------------|--------------------------|
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description not in context, full skill loads when you invoke |
| `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

**Use `disable-model-invocation: true` for:**
- Workflows with side effects (deploy, commit, send messages)
- Actions where timing matters
- Tasks that require user approval

**Use `user-invocable: false` for:**
- Background knowledge that isn't actionable
- Context that Claude should know but users shouldn't invoke

### String Substitutions

Skills support dynamic value substitution:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Specific argument by 0-based index (e.g., `$ARGUMENTS[0]`) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`, `$2`) |
| `$name` | Named argument from `arguments` frontmatter list |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Current effort level (`low`, `medium`, `high`, `xhigh`, `max`) |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's `SKILL.md` file |

#### Example with Named Arguments

```yaml
---
arguments: [component, from, to]
---

Migrate the $component component from $from to $to.
Preserve all existing behavior and tests.
```

Running `/migrate-component SearchBar React Vue` makes:
- `$component` = `SearchBar`
- `$from` = `React`
- `$to` = `Vue`

### Pre-approve Tools

The `allowed-tools` field grants permission for listed tools while the skill is active:

```yaml
---
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

**Important notes:**
- Does not restrict which tools are available
- Your permission settings still govern unlisted tools
- For project skills, takes effect after workspace trust dialog
- Review project skills before trusting a repository

---

## Types of Skill Content

From the documentation, skills can be categorized by their content type:

### Reference Content

Adds knowledge Claude applies to your current work:
- Conventions
- Patterns
- Style guides
- Domain knowledge

**Characteristics:**
- Runs inline (not in subagent)
- Stays in context throughout session
- Should be concise

**Example:**

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

### Task Content

Gives Claude step-by-step instructions for specific actions:
- Deployments
- Commits
- Code generation
- Analysis workflows

**Characteristics:**
- Often invoked directly with `/skill-name`
- May use `disable-model-invocation: true`
- Can run in subagent context

**Example:**

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

### Writing Guidelines

From the documentation:

> Keep the body itself concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost. State what to do rather than narrating how or why, and apply the same conciseness test you would for CLAUDE.md content.

---

## Implementation Patterns

### Dynamic Context Injection

The `` !`<command>` `` syntax runs shell commands **before** the skill content is sent to Claude:

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

**How it works:**
1. Each `` !`<command>` `` executes immediately (preprocessing)
2. Output replaces the placeholder
3. Claude receives the fully-rendered prompt with actual data

**Multi-line commands:**

````yaml
---
name: environment-check
---

## Environment
```!
node --version
npm --version
git status --short
```
````

**Security control:**

To disable shell execution, set `"disableSkillShellExecution": true` in settings. Each command is replaced with `[shell command execution disabled by policy]`.

### Supporting Files

Skills can include multiple files to keep `SKILL.md` focused:

```
my-skill/
├── SKILL.md           # Overview and navigation
├── reference.md       # Detailed API docs (loaded when needed)
├── examples.md        # Usage examples (loaded when needed)
└── scripts/
    └── helper.py      # Utility script (executed, not loaded)
```

Reference supporting files from `SKILL.md`:

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

**Best practice from the docs:**

> Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

### Skill Content Lifecycle

From the documentation:

> When you or Claude invoke a skill, the rendered `SKILL.md` content enters the conversation as a single message and stays there for the rest of the session. Claude Code does not re-read the skill file on later turns.

**Auto-compaction behavior:**

- Skills are carried forward within a token budget during auto-compaction
- Re-attached after summary with first 5,000 tokens of each skill
- Skills share a combined budget of 25,000 tokens
- Budget fills from most recently invoked skill first
- Older skills can be dropped entirely if many invoked

**If a skill stops working after compaction:**

The documentation notes:

> If a skill seems to stop influencing behavior after the first response, the content is usually still present and the model is choosing other tools or approaches. Strengthen the skill's `description` and instructions so the model keeps preferring it, or use hooks to enforce behavior deterministically. If the skill is large or you invoked several others after it, re-invoke it after compaction to restore the full content.

### Running Skills in Subagents

Add `context: fork` to run a skill in isolation:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

**How it works:**

1. New isolated context is created
2. Subagent receives skill content as its prompt
3. `agent` field determines execution environment (model, tools, permissions)
4. Results are summarized and returned to main conversation

**Important warning from the docs:**

> `context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like "use these API conventions" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output.

### Skills and Subagents

Two-way relationship:

| Approach | System prompt | Task | Also loads |
|----------|---------------|------|------------|
| Skill with `context: fork` | From agent type (`Explore`, `Plan`, etc.) | SKILL.md content | CLAUDE.md |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md |

---

## Advanced Patterns

### Pass Arguments to Skills

Arguments are available via the `$ARGUMENTS` placeholder:

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

When you run `/fix-issue 123`, Claude receives "Fix GitHub issue 123 following our coding standards..."

**Auto-append behavior:**

> If you invoke a skill with arguments but the skill doesn't include `$ARGUMENTS`, Claude Code appends `ARGUMENTS: <your input>` to the end of the skill content so Claude still sees what you typed.

### Restrict Claude's Skill Access

From the documentation:

> By default, Claude can invoke any skill that doesn't have `disable-model-invocation: true` set.

**Three ways to control skill invocation:**

1. **Disable all skills** by denying the Skill tool in `/permissions`:
   ```
   Skill
   ```

2. **Allow or deny specific skills** using permission rules:
   ```
   # Allow only specific skills
   Skill(commit)
   Skill(review-pr *)

   # Deny specific skills
   Skill(deploy *)
   ```

3. **Hide individual skills** by adding `disable-model-invocation: true` to frontmatter

**Permission syntax:**
- `Skill(name)` - exact match
- `Skill(name *)` - prefix match with any arguments

**Important note:**

> The `user-invocable` field only controls menu visibility, not Skill tool access. Use `disable-model-invocation: true` to block programmatic invocation.

### Override Skill Visibility from Settings

The `skillOverrides` setting in `.claude/settings.local.json` controls skill visibility without editing the skill itself:

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

**Visibility states:**

| Value | Listed to Claude | In `/` menu |
|-------|------------------|-------------|
| `"on"` | Name and description | Yes |
| `"name-only"` | Name only | Yes |
| `"user-invocable-only"` | Hidden | Yes |
| `"off"` | Hidden | Hidden |

**Use cases:**
- Skills from shared project repos
- Skills provided by MCP servers
- Managing description budget for many skills

**Note:** Plugin skills are not affected by `skillOverrides`. Manage those through `/plugin`.

### Deep Reasoning with Ultrathink

From the documentation:

> To request deeper reasoning when a skill runs, include `ultrathink` anywhere in the skill content.

This triggers extended thinking mode for one-off deep reasoning tasks.

### Generate Visual Output

Skills can bundle scripts in any language to generate visual output like interactive HTML files.

**Example pattern from the docs:**

1. Skill includes a Python script in `scripts/` directory
2. Skill content uses `${CLAUDE_SKILL_DIR}` to reference the script
3. Claude runs the script, which generates an HTML file
4. Script opens the file in the browser

The documentation includes a complete example of a codebase visualizer that generates an interactive tree view with:
- Collapsible directories
- File size indicators
- Color-coded file types
- Summary statistics sidebar
- Bar chart of file types

**Key insight:**

> This pattern works for any visual output: dependency graphs, test coverage reports, API documentation, or database schema visualizations. The bundled script does the work while Claude handles orchestration.

---

## Bundled Skills

Claude Code includes built-in skills available in every session:

From the commands reference:

- `/simplify` - Review changed code for reuse, quality, and efficiency
- `/batch` - Process multiple items with the same operation
- `/debug` - Systematic debugging workflow
- `/loop` - Run a prompt or slash command on a recurring interval
- `/claude-api` - Build, debug, and optimize Claude API applications
- `/schedule` - Create, update, list, or run scheduled remote agents
- And others listed in `/commands`

These are prompt-based (not fixed logic) and marked **Skill** in the commands reference Purpose column.

---

## Best Practices

### From the Official Documentation

1. **Create skills instead of pasting instructions**
   - When you keep pasting the same checklist
   - When CLAUDE.md grows into procedures rather than facts

2. **Keep SKILL.md concise**
   - Under 500 lines recommended
   - Every line is a recurring token cost
   - Move detailed reference to separate files

3. **Write effective descriptions**
   - Include specific keywords
   - Describe both what and when
   - Put key use case first (truncated at 1,536 chars)

4. **Use appropriate invocation control**
   - `disable-model-invocation: true` for side effects
   - `user-invocable: false` for background knowledge

5. **Structure for progressive disclosure**
   - Metadata (~100 tokens): name and description
   - Instructions (< 5000 tokens recommended): SKILL.md body
   - Resources (as needed): scripts, references, assets

6. **Reference supporting files effectively**
   - Document what each file contains
   - Explain when Claude should load it
   - Keep individual files focused

7. **Use dynamic context injection wisely**
   - For live data that changes between invocations
   - Remember it's preprocessing, not Claude execution
   - Consider security with `disableSkillShellExecution`

8. **Choose appropriate context**
   - Inline for reference/knowledge
   - `context: fork` for isolated tasks with explicit instructions
   - Don't fork for pure guidelines without tasks

### Troubleshooting

From the documentation:

**Skill not triggering:**
1. Check description includes keywords users would naturally say
2. Verify skill appears in "What skills are available?"
3. Try rephrasing to match description more closely
4. Invoke directly with `/skill-name`

**Skill triggers too often:**
1. Make description more specific
2. Add `disable-model-invocation: true` for manual invocation only

**Skill descriptions are cut short:**
- Skills share a character budget (1% of context window, min 8,000 chars)
- Each entry capped at 1,536 characters
- Raise limit with `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var
- Set low-priority skills to `"name-only"` in `skillOverrides`

---

## Key Takeaways

### Critical Insights

1. **Skills follow an open standard**
   - Based on Agent Skills (https://agentskills.io)
   - Works across multiple AI tools (Claude Code, OpenCode, Cursor, etc.)
   - Open to contributions from the ecosystem

2. **Progressive disclosure is central to the design**
   - Descriptions loaded at startup (minimal cost)
   - Full content loads only when invoked
   - Supporting files loaded only when needed
   - Enables large skill libraries without context bloat

3. **Skills have replaced custom commands**
   - Legacy `.claude/commands/` files still work
   - New work should use `.claude/skills/`
   - Skills add directories, frontmatter, and auto-invocation

4. **Two distinct use cases**
   - **Reference content**: Knowledge Claude applies inline
   - **Task content**: Step-by-step workflows often invoked manually

5. **Invocation control is sophisticated**
   - User invocation: always available unless `user-invocable: false`
   - Claude invocation: always available unless `disable-model-invocation: true`
   - Visibility can be overridden in settings without editing skills

6. **Dynamic context injection is powerful**
   - `` !`command` `` runs before Claude sees content
   - Enables grounding in live data (git status, API responses, etc.)
   - Can be disabled for security with settings flag

7. **Skills can run in subagents**
   - `context: fork` creates isolated execution
   - Choose agent type with `agent` field
   - Only makes sense for skills with explicit task instructions

8. **Content stays in context**
   - Invoked skills enter conversation and stay there
   - Not re-read on later turns
   - Auto-compaction may drop older skills

9. **Tools can be pre-approved**
   - `allowed-tools` grants permission while skill is active
   - Doesn't restrict availability, just approval requirement
   - Respect workspace trust for project skills

10. **Skill discovery is automatic**
    - Nested `.claude/skills/` directories discovered automatically
    - Supports monorepo patterns
    - Live reload on file changes (no restart needed)

### Architecture Principles

From the broader documentation context:

1. **Skills are for procedures, CLAUDE.md is for facts**
   - Move procedures from CLAUDE.md to skills
   - Keep CLAUDE.md for project-specific knowledge

2. **Use hooks for enforcement, skills for guidance**
   - Skills provide instructions
   - Hooks provide deterministic automation

3. **Skills, subagents, and hooks work together**
   - Skills can invoke subagents (`context: fork`)
   - Subagents can preload skills
   - Skills can define scoped hooks

4. **Plugins package skills for distribution**
   - Skills in `<plugin>/skills/` namespace
   - Install once, use across projects
   - Marketplace-friendly

### Development Workflow

1. **Start with CLAUDE.md**
   - Add project-specific facts and context

2. **Extract to skills when appropriate**
   - Procedures that grow beyond 20-30 lines
   - Workflows you invoke repeatedly
   - Reference material that's only sometimes needed

3. **Add supporting files as skills grow**
   - Keep SKILL.md under 500 lines
   - Move details to `references/`
   - Bundle scripts in `scripts/`

4. **Use frontmatter to optimize behavior**
   - Set appropriate invocation controls
   - Pre-approve frequently used tools
   - Add path restrictions for focus

5. **Test invocation**
   - Try auto-invocation (ask questions matching description)
   - Try manual invocation (`/skill-name`)
   - Check skill appears in "What skills are available?"

6. **Share appropriately**
   - Personal: `~/.claude/skills/` for your workflows
   - Project: `.claude/skills/` for team workflows
   - Plugin: for cross-project reuse

---

## Related Documentation

- **[Commands reference](https://code.claude.com/docs/en/commands)** - Built-in commands and bundled skills
- **[Create custom subagents](https://code.claude.com/docs/en/sub-agents)** - Task-specific agent isolation
- **[Create plugins](https://code.claude.com/docs/en/plugins)** - Package skills for distribution
- **[Automate workflows with hooks](https://code.claude.com/docs/en/hooks-guide)** - Deterministic automation
- **[CLAUDE.md best practices](https://code.claude.com/docs/en/best-practices)** - Write effective context
- **[Permissions reference](https://code.claude.com/docs/en/permissions)** - Control tool and skill access
- **[Agent Skills specification](https://agentskills.io/specification)** - Open standard format
- **[Debug your configuration](https://code.claude.com/docs/en/debug-your-config)** - Diagnose skill issues

---

## Code Examples

### Example 1: Simple Reference Skill

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats: `{ error: string, code: number }`
- Include request validation with zod schemas
- Use standard HTTP status codes
- Document with JSDoc comments
```

### Example 2: Task Skill with Dynamic Context

```yaml
---
name: summarize-changes
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```

### Example 3: Deploy Skill with Manual Invocation

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(npm *) Bash(ssh *)
context: fork
agent: general-purpose
---

Deploy to production:

1. Verify on main branch: `git branch --show-current`
2. Run full test suite: `npm test`
3. Build production bundle: `npm run build`
4. Push to deployment: `npm run deploy:prod`
5. Verify deployment: `curl https://api.example.com/health`
6. Report results
```

### Example 4: Research Skill with Subagent

```yaml
---
name: deep-research
description: Research a topic thoroughly in the codebase
context: fork
agent: Explore
arguments: [topic]
---

Research "$topic" thoroughly:

1. Use Glob to find relevant files
2. Use Grep to search for related code patterns
3. Read key files to understand implementation
4. Summarize findings with specific file references and code examples
5. Note any inconsistencies or areas needing attention
```

### Example 5: Skill with Supporting Files

**Directory structure:**

```
pdf-processor/
├── SKILL.md
├── scripts/
│   ├── extract_text.py
│   └── merge_pdfs.py
└── references/
    └── api-reference.md
```

**SKILL.md:**

```yaml
---
name: pdf-processor
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
allowed-tools: Bash(python3 *)
---

# PDF Processing Skill

Process PDF documents using bundled scripts.

## Operations

### Extract text from PDF

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_text.py input.pdf
```

### Merge multiple PDFs

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/merge_pdfs.py output.pdf input1.pdf input2.pdf
```

## Additional resources

For complete API details and advanced options, see [api-reference.md](references/api-reference.md).
```

### Example 6: Skill with Named Arguments

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
arguments: [component, from_framework, to_framework]
---

Migrate the $component component from $from_framework to $to_framework:

1. Read the original component implementation
2. Identify framework-specific patterns in $from_framework
3. Map patterns to $to_framework equivalents
4. Rewrite component in $to_framework
5. Preserve all existing behavior and tests
6. Update imports and dependencies
```

Usage: `/migrate-component SearchBar React Vue`

### Example 7: Skill with Path Restrictions

```yaml
---
name: typescript-patterns
description: TypeScript patterns and conventions for this project
paths: "src/**/*.ts, src/**/*.tsx"
---

TypeScript conventions for this codebase:

- Use strict null checks
- Prefer `interface` over `type` for object shapes
- Use `const` assertions for literal types
- Export types with `export type` syntax
- Use generic constraints for type safety
```

This skill only loads when working with TypeScript files.

---

## Appendix: Agent Skills Specification Summary

From https://agentskills.io/specification:

### Required Frontmatter Fields

```yaml
name: skill-name           # Max 64 chars, lowercase + hyphens only
description: What this skill does  # Max 1024 chars, should include when to use
```

### Optional Frontmatter Fields

```yaml
license: Apache-2.0
compatibility: Requires git, docker, jq, and internet access
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(git *) Read
```

### Progressive Disclosure Model

1. **Metadata** (~100 tokens): Name and description loaded at startup
2. **Instructions** (< 5000 tokens recommended): Full SKILL.md body when activated
3. **Resources** (as needed): Scripts, references, assets loaded on demand

### Validation

Use the `skills-ref` reference library:

```bash
skills-ref validate ./my-skill
```

Checks frontmatter validity and naming conventions.

---

**End of Document**
