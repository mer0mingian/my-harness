# Commands vs Skills: Architecture and Relationship

**Sources:** manage-command-creator, manage-skill-creator, .agents/commands/, .agents/skills/, .agents/agents/  
**Extracted:** 2026-05-07

## Overview

The harness-tooling marketplace architecture defines three distinct abstractions for extending Claude Code capabilities:

1. **Commands** - User-invocable slash commands for workflow automation
2. **Skills** - Knowledge packages that extend agent capabilities
3. **Agents** - Specialized agent personas with specific permissions and capabilities

All three are declared in plugin manifests and discoverable via Claude Code's plugin system.

---

## Command Architecture

### What is a Command?

A **command** is a markdown file that becomes a slash command (e.g., `/submit-stack`, `/ensure-ci`) invokable by users in Claude Code conversations. Commands are reusable workflows that get expanded into prompts when invoked.

### Format and Structure

Commands are **Markdown files with YAML frontmatter**:

```markdown
---
description: Brief description shown in /help (required)
argument-hint: <placeholder> (optional, if command takes arguments)
agent: agent-name (optional, delegates to specific agent)
subtask: true/false (optional, marks as subtask for orchestration)
options: (optional, command-specific options)
  key: value
return: (optional, array of subtask execution steps)
  - /subtask {agent: name && as: phase_id} Task description
---

# Command Title

[Detailed instructions for the agent to execute autonomously]
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | ✅ Yes | Brief description shown in `/help` output |
| `argument-hint` | ❌ No | Placeholder shown in help (e.g., `<description>`, `[base-branch]`) |
| `agent` | ❌ No | Specific agent to delegate execution to |
| `subtask` | ❌ No | Marks command as subtask (for orchestration workflows) |
| `options` | ❌ No | Command-specific options (e.g., `skip_tests: false`) |
| `return` | ❌ No | Array of orchestrated subtask steps with agent delegation |

### Location

Commands can be installed at two levels:

- **Project-level**: `.claude/commands/` (git repo specific)
- **Global/User-level**: `~/.claude/commands/` (available everywhere)

### Invocation

Commands are invoked as slash commands:

```bash
/command-name [arguments]
```

### Command Types and Patterns

Based on the analyzed examples, commands follow distinct patterns:

#### 1. **Workflow Automation Pattern**

Structure: Analyze → Act → Report

Example: `pries-implement.md`

```yaml
---
description: "BMAD Phase 4 (Implementation): execute full 10-phase PRIES workflow"
agent: pries-pm
subtask: true
options:
  skip_tests: false
  parallel_tasks: false
  review_cycles: 3
return:
  - /subtask {agent: pries-pm && as: phase1_verify} Verify repo state...
  - /subtask {agent: pries-pm && as: phase2_ticket} Fetch issue context...
  # ... more orchestrated phases
---
```

**Key features:**
- Multi-phase orchestration
- Agent delegation via `/subtask` syntax
- Conditional logic based on file existence
- Clear success criteria

#### 2. **Iterative Fixing Pattern**

Structure: Run → Parse → Fix → Repeat

Example: `ensure-ci` (from references)

**Key features:**
- Maximum iteration limits
- Stuck detection logic
- Per-error-type fix instructions
- TodoWrite progress tracking

#### 3. **Agent Delegation Pattern**

Structure: Context → Delegate → Iterate

Example: `create-implementation-plan` (from references)

**Key features:**
- Task tool invocation with `subagent_type="subagent"`
- User review checkpoints
- No code modification during planning phase
- Explicit save-to-disk trigger

#### 4. **Simple Execution Pattern**

Structure: Parse Arguments → Execute → Return Output

Example: `codex-review` (from references)

**Key features:**
- Optional argument handling
- Direct script/tool invocation
- Minimal additional logic
- Output pass-through

### Naming Conventions

- Command names MUST be kebab-case (hyphens, NOT underscores)
  - ✅ CORRECT: `submit-stack`, `ensure-ci`, `pries-implement`
  - ❌ WRONG: `submit_stack`, `ensure_ci`, `pries_implement`
- File names match command names: `my-command.md` → invoked as `/my-command`

---

## Skill Architecture

### What is a Skill?

A **skill** is a modular, self-contained package that extends Claude's capabilities by providing specialized knowledge, workflows, and tools. Skills are "onboarding guides" that transform Claude from a general-purpose agent into a specialized agent.

### Format and Structure

Skills are **directories containing a SKILL.md file with optional bundled resources**:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/      - Executable code (Python/Bash/etc.)
    ├── references/   - Documentation loaded into context as needed
    └── assets/       - Files used in output (templates, icons, etc.)
```

### SKILL.md Structure

```markdown
---
name: skill-name
description: Comprehensive description of what the skill does and when to use it
---

# Skill Title

[Instructions and guidance for using the skill]

## Bundled Resources

- **references/patterns.md** - Detailed patterns (load as needed)
- **scripts/tool.py** - Executable script (may run without loading)
- **assets/template/** - Output templates (not loaded into context)
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ Yes | Skill name (used for triggering) |
| `description` | ✅ Yes | PRIMARY TRIGGER - what skill does AND when to use it |
| `license` | ❌ No | License reference (e.g., "Complete terms in LICENSE.txt") |

**Critical**: The `description` field is the primary triggering mechanism. It must include:
- What the skill does
- Specific triggers/contexts for when to use it
- All "when to use" information (body is only loaded AFTER triggering)

### Progressive Disclosure Design

Skills use a three-level loading system:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words, <500 lines)
3. **Bundled resources** - As needed by Claude (loaded on demand)

### Bundled Resources

#### Scripts (`scripts/`)

Executable code for tasks requiring deterministic reliability.

**When to include:**
- Same code repeatedly rewritten
- Deterministic reliability needed
- Token efficiency important

**Example:** `scripts/rotate_pdf.py` for PDF rotation

**Benefits:**
- Token efficient
- Deterministic execution
- May execute without loading into context

#### References (`references/`)

Documentation loaded into context as needed to inform Claude's process.

**When to include:**
- Documentation Claude should reference while working
- Database schemas, API specs, domain knowledge
- Detailed workflow guides

**Examples:**
- `references/finance.md` - Financial schemas
- `references/patterns.md` - Command patterns
- `references/examples.md` - Real code examples

**Best practice:** Keep SKILL.md lean; move detailed info to references

#### Assets (`assets/`)

Files used in output, not loaded into context.

**When to include:**
- Files used in final output
- Templates, images, icons
- Boilerplate code

**Examples:**
- `assets/logo.png` - Brand assets
- `assets/slides.pptx` - PowerPoint templates
- `assets/frontend-template/` - HTML/React boilerplate

### Location

Skills are stored in:
- Marketplace: `.agents/skills/` (harness-tooling)
- Installed: `.claude/skills/` or custom locations defined in plugin manifests

### Invocation

Skills are **auto-triggered** by Claude Code when:
1. The `description` field matches user intent
2. Claude determines the skill is needed for the task

Skills can also be explicitly invoked via the `Skill` tool in autonomous mode.

---

## Agent Architecture

### What is an Agent?

An **agent** is a specialized persona with specific capabilities, permissions, and skills. Agents are defined in markdown files and referenced by commands for delegation.

### Format and Structure

Agents are **Markdown files with YAML frontmatter**:

```markdown
---
name: agent-name
description: Agent's role and purpose
source: local
mode: subagent
temperature: 0.2
skills:
  - skill-name-1
  - skill-name-2
permission:
  read:
    '*': allow
  write:
    docs/specific/**: allow
  bash:
    'ls *': allow
    'grep *': allow
  skill:
    "prefix-": allow
---

# Agent Persona: Agent Name

[Detailed persona description, mission, rules, workflow SOP]
```

### Frontmatter Fields

| Field | Description |
|-------|-------------|
| `name` | Agent identifier |
| `description` | Agent role and purpose |
| `source` | Agent source (`local` for project agents) |
| `mode` | Execution mode (`subagent`) |
| `temperature` | Model temperature (e.g., `0.2` for deterministic) |
| `skills` | Array of skill names agent can use |
| `permission` | Granular permission controls (read, write, edit, bash, skill) |

### Permission Model

Agents define fine-grained permissions:

```yaml
permission:
  read:
    '*': allow                    # Allow all reads
  write:
    docs/tickets/**: allow        # Allow writes to specific paths
    '*': deny                     # Deny all other writes
  edit:
    docs/tickets/**: allow
  bash:
    '*': deny                     # Deny all bash by default
    'ls *': allow                 # Allow specific commands
    'grep *': allow
    'git worktree *': allow
  skill:
    "stdd-": allow                # Allow skills with prefix
    "general-using-git-worktrees": allow
    "": deny                      # Deny all others
```

### Example Agent: pries-pm

```yaml
---
name: pries-pm
description: PRIES Phase 1 Product Manager / Requirements Validator
source: local
mode: subagent
temperature: 0.2
skills:
  - stdd-pm-linear-integration
  - stdd-product-spec-formats
  - stdd-ask-questions-if-underspecified
  - stdd-project-summary
  - general-using-git-worktrees
permission:
  read:
    '*': allow
  write:
    docs/tickets/**: allow
  bash:
    'linear *': allow
    'git worktree *': allow
    'grep *': allow
---
```

This agent:
- Specializes in product management and requirements validation
- Has access to specific skills
- Can only write to `docs/tickets/`
- Has limited bash permissions (Linear, git worktree, grep)

---

## Commands vs Skills vs Agents: Key Differences

| Aspect | Commands | Skills | Agents |
|--------|----------|--------|--------|
| **Purpose** | User-invokable workflows | Knowledge packages | Specialized personas |
| **Format** | Markdown + YAML frontmatter | Directory with SKILL.md + resources | Markdown + YAML frontmatter |
| **Invocation** | User: `/command-name` | Auto-triggered by description match | Referenced by commands via `agent:` field |
| **Trigger** | Explicit by user | Implicit by Claude (description matching) | Explicit delegation from commands |
| **Location** | `.claude/commands/` or `~/.claude/commands/` | `.agents/skills/` | `.agents/agents/` |
| **Naming** | kebab-case, must match filename | No strict convention | No strict convention |
| **Arguments** | Supports `<required>` or `[optional]` | N/A (no direct invocation) | N/A (delegated with context) |
| **Bundled Resources** | No | Yes (scripts, references, assets) | No (references skills instead) |
| **Progressive Loading** | Entire file loaded on invocation | 3-level (metadata → body → resources) | Entire file loaded on delegation |
| **Permission Model** | No granular permissions | No permissions (runs as Claude) | Fine-grained permissions (read, write, bash, skill) |
| **Primary Use Case** | Automate user workflows | Extend Claude's knowledge | Isolate responsibilities with constraints |

---

## Example Analysis

### Example Command: pries-implement.md

**Location:** `.agents/commands/pries-implement.md`

**Structure:**

```markdown
---
description: "BMAD Phase 4 (Implementation): execute full 10-phase PRIES workflow"
agent: pries-pm
subtask: true
options:
  skip_tests: false
  parallel_tasks: false
  review_cycles: 3
return:
  - /subtask {agent: pries-pm && as: phase1_verify} Verify repo state...
  - /subtask {agent: pries-pm && as: phase2_ticket} Fetch issue context...
  - /subtask {agent: pries-pm && as: phase3_worktree} Create worktree...
  - /subtask {agent: pries-pm && as: phase4_plan} Draft plan...
  - /subtask {agent: pries-check && as: phase5_check_1} Review plan...
  - /subtask {agent: pries-simplify && as: phase5_simplify_1} Review plan...
  - /subtask {agent: pries-pm && as: phase5_merge} Merge reviews...
  # ... more phases
---

# PRIES Implement: $ARGUMENTS

**BMAD Phase 4 — Implementation.** Orchestrates the full 10-phase PRIES
workflow against issue `$ARGUMENTS`.

## Options

- `--skip-tests` — bypass Phase 7
- `--parallel-tasks` — dispatch independent tasks concurrently
- `--review-cycles=N` — override max review cycles (default 3)

## Outputs

- `feat/<id>-<slug>` branch with conventional commits
- Draft PR with embedded workflow report
- Updated `docs/tickets/<id>.md`
```

**Key observations:**
- Orchestrates multiple agents (pries-pm, pries-check, pries-simplify, pries-test, pries-make)
- Uses `/subtask` syntax for agent delegation
- Supports options and conditional logic
- Produces structured outputs (branches, PRs, tickets)

### Example Command: stdd-01-specification.md

**Location:** `.agents/commands/stdd-01-specification.md`

**Structure:**

```markdown
---
description: "Stage 1: Feature Specification"
agent: daniels-workflow-orchestrator
subtask: true
return:
  - /subtask {agent: daniels-spec-agent && as: spec_init} Define project summary...
  - /subtask {agent: daniels-spec-agent && as: spec_draft} Create proposal.md...
  - /subtask {agent: daniels-critical-thinking-agent && as: spec_audit} Review requirements...
  - /subtask {agent: daniels-spec-agent} Finalize artifacts...
  - "Stage 1 complete. Please review and reply 'Approved' to continue."
---

# Feature Specification: $ARGUMENTS

Initiating the specification sequence...
```

**Key observations:**
- Multi-agent orchestration (spec-agent, critical-thinking-agent)
- Human approval gate (waits for user input)
- Sequential phases with named results (`spec_init`, `spec_draft`, `spec_audit`)
- Minimal body (most logic in frontmatter)

### Example Skill: manage-skill-creator

**Location:** `.agents/skills/manage-skill-creator/SKILL.md`

**Structure:**

```markdown
---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities...

## Core Principles

### Concise is Key

The context window is a public good...

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility...

## Bundled Resources

This skill includes reference documentation for detailed guidance:

- **references/patterns.md** - Detailed patterns (load as needed)
- **references/examples.md** - Real examples (load as needed)
- **references/best-practices.md** - Quality checklist (load as needed)
```

**Directory structure:**

```
manage-skill-creator/
├── SKILL.md
├── LICENSE.txt
├── README.md (not loaded, for humans)
└── references/
    ├── workflows.md
    ├── output-patterns.md
    ├── patterns.md
    ├── examples.md
    └── best-practices.md
```

**Key observations:**
- Comprehensive triggering description (includes "when to use")
- Progressive disclosure (references loaded on demand)
- Procedural knowledge (how to create skills)
- Bundled references for detailed guidance
- README.md exists but not for AI consumption

### Example Skill: manage-command-creator

**Location:** `.agents/skills/manage-command-creator/SKILL.md`

**Structure:**

```markdown
---
name: command-creator
description: This skill should be used when creating a Claude Code slash command. Use when users ask to "create a command", "make a slash command", "add a command", or want to document a workflow as a reusable command.
---

# Command Creator

This skill guides the creation of Claude Code slash commands...

## About Slash Commands

Slash commands are markdown files stored in `.claude/commands/`...

## Bundled Resources

- **references/patterns.md** - Command patterns (workflow automation, iterative fixing, etc.)
- **references/examples.md** - Real command examples with full source
- **references/best-practices.md** - Quality checklist, writing guidelines

## Command Creation Workflow

### Step 1: Determine Location
### Step 2: Show Command Patterns
### Step 3: Gather Command Information
### Step 4: Generate Optimized Command
### Step 5: Create the Command File
### Step 6: Test and Iterate
```

**Key observations:**
- Guides command creation (meta-skill)
- References command patterns and examples
- Step-by-step workflow
- Auto-detects project vs global location

### Example Skill: arch-writing-plans

**Location:** `.agents/skills/arch-writing-plans/SKILL.md`

**Structure:**

```markdown
---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context...

## Scope Check

If the spec covers multiple independent subsystems...

## File Structure

Before defining tasks, map out which files will be created or modified...

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development...
```

**Key observations:**
- Procedural knowledge for planning
- Clear constraints (no placeholders, exact file paths)
- Self-review checklist
- Execution handoff instructions
- References bundled skill (subagent-driven-development)

### Example Agent: pries-pm

**Location:** `.agents/agents/pries-pm.md`

**Structure:**

```markdown
---
name: pries-pm
description: PRIES Phase 1 Product Manager / Requirements Validator
source: local
mode: subagent
temperature: 0.2
skills:
  - stdd-pm-linear-integration
  - stdd-product-spec-formats
  - stdd-ask-questions-if-underspecified
  - stdd-project-summary
  - general-using-git-worktrees
permission:
  read:
    '*': allow
  write:
    docs/tickets/**: allow
  edit:
    docs/tickets/**: allow
  bash:
    '*': deny
    'linear *': allow
    'git worktree *': allow
  skill:
    "stdd-": allow
    "general-using-git-worktrees": allow
    "": deny
---

# Agent Persona: PRIES PM (Phase 1)

You are the **Product Manager** for the PRIES workflow...

## Mission

Given an issue ID (e.g. `STA-001`):
1. Fetch the issue (Linear CLI or markdown fallback)
2. Validate references to governance docs
3. Create isolated git worktree
4. Draft file manifest
5. Hand off task package

## Core Rules & Constraints

- **Read-only against the codebase**
- **Use Linear CLI when available**
- **Markdown fallback** when Linear unavailable
- **NFR validation is mandatory**
- **Underspecified tickets get questions**

## Workflow SOP

1. **Fetch ticket**
2. **Cross-check governance**
3. **Create worktree**
4. **Draft file manifest**
5. **Update ticket state**
6. **Emit task package**

## Output Contract

```yaml
issue:
  id: STA-001
  title: "Feature Title"
  state: "In Progress"
  worktree: ".worktrees/feat/sta-001-slug"
  branch: "feat/sta-001-slug"
acceptance_criteria: [...]
governance_refs: [...]
draft_file_manifest: [...]
```
```

**Key observations:**
- Clear mission and constraints
- Fine-grained permissions (can only write to docs/tickets/)
- Explicit skills available
- Defined input/output contract
- Anti-patterns documented

---

## Relationship and Integration

### How Commands and Skills Interact

**Commands invoke skills implicitly:**

When a command executes, Claude may auto-trigger skills based on the task requirements. For example:

- `/pries-implement` command executes
- Claude detects need for planning → triggers `arch-writing-plans` skill
- Claude needs to validate governance → triggers governance-validation skills
- Claude writes tests → triggers `dev-tdd` skill

**Skills are never directly invoked by commands.** Instead:
1. Command provides instructions
2. Claude executes instructions
3. Claude's skill-matching system triggers relevant skills
4. Skills provide knowledge/context to Claude
5. Claude completes command execution

### How Commands Delegate to Agents

**Commands explicitly delegate to agents via frontmatter:**

```markdown
---
agent: pries-pm
return:
  - /subtask {agent: pries-pm && as: phase1} Task 1
  - /subtask {agent: pries-check && as: phase2} Task 2
  - /subtask {agent: pries-simplify && as: phase3} Task 3
---
```

**Agent delegation flow:**

1. User invokes command: `/pries-implement STA-001`
2. Command's `agent: pries-pm` field delegates to pries-pm agent
3. Command's `return` array orchestrates multi-agent workflow
4. Each `/subtask` invokes a specific agent with context
5. Agents execute with their skill sets and permissions
6. Results flow back to orchestrating command

### How Agents Use Skills

**Agents declare skills in their frontmatter:**

```yaml
skills:
  - stdd-pm-linear-integration
  - general-using-git-worktrees
  - stdd-ask-questions-if-underspecified
```

**Agent + skill flow:**

1. Command delegates to agent
2. Agent receives persona, mission, constraints
3. Agent has access to declared skills
4. Claude (as agent) auto-triggers skills when needed
5. Skills provide knowledge/tools to agent
6. Agent completes delegated task

### Complete Integration Example

**User invokes:** `/pries-implement STA-001`

**Flow:**

1. **Command loads:** `pries-implement.md`
2. **Command delegates to:** `pries-pm` agent
3. **Agent loads:** `pries-pm.md` persona with permissions and skills
4. **Agent has skills:** `stdd-pm-linear-integration`, `general-using-git-worktrees`, etc.
5. **Command orchestrates:**
   - Phase 1: Agent `pries-pm` verifies repo state
     - Skill `general-using-git-worktrees` auto-triggers for worktree knowledge
   - Phase 2: Agent `pries-pm` fetches ticket
     - Skill `stdd-pm-linear-integration` auto-triggers for Linear integration
   - Phase 3: Agent `pries-pm` creates worktree
   - Phase 4: Agent `pries-pm` drafts plan
     - Skill `arch-writing-plans` might auto-trigger for planning guidance
   - Phase 5: Agent `pries-check` reviews plan
     - Skill `review-check-correctness` auto-triggers
   - Phase 5: Agent `pries-simplify` reviews plan (parallel)
     - Skill `review-simplify-complexity` auto-triggers
   - Phase 6-10: Continue with `pries-test`, `pries-make`, etc.

6. **Result:** Draft PR created with full workflow report

### Can Commands Call Skills Directly?

**No.** Commands do not directly call skills. Skills are auto-triggered by Claude's matching system when the task requirements align with the skill's description.

### Can Skills Call Commands?

**No.** Skills do not invoke commands. Skills provide knowledge and workflows that help Claude execute commands more effectively.

### Can Skills Call Other Skills?

**Implicitly, yes.** Skills can reference other skills in their instructions:

```markdown
## Execution Handoff

After saving the plan, offer execution choice:

**1. Subagent-Driven (recommended)**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development

**2. Inline Execution**
- **REQUIRED SUB-SKILL:** Use superpowers:executing-plans
```

This is a **recommendation to Claude**, not a direct invocation. Claude's skill-matching system will trigger the referenced skill when appropriate.

### Can Agents Call Commands?

**Yes, indirectly.** Agents can invoke commands if they have the appropriate bash permissions:

```yaml
permission:
  bash:
    '/command-name *': allow
```

However, the typical pattern is:
- **Commands orchestrate agents** (top-down)
- **Agents execute with skills** (knowledge layer)
- Commands are user-facing entry points, not agent tools

---

## Creator Tools

### /command-creator (manage-command-creator skill)

**Purpose:** Guide creation of Claude Code slash commands

**What it generates:**

1. **Location detection:**
   - Checks if in git repo
   - Defaults to project (`.claude/commands/`) or global (`~/.claude/commands/`)
   - Allows user override

2. **Pattern selection:**
   - Shows 4 main patterns (Workflow Automation, Iterative Fixing, Agent Delegation, Simple Execution)
   - Helps user choose appropriate structure

3. **Information gathering:**
   - Command name (kebab-case enforced)
   - Description for `/help`
   - Arguments (required `<>` vs optional `[]`)
   - Workflow steps
   - Tool/agent restrictions

4. **Command generation:**
   - Creates markdown file with YAML frontmatter
   - Agent-optimized instructions (imperative/infinitive form)
   - Explicit tool usage
   - Clear error handling
   - Success criteria

5. **File creation:**
   - Writes to appropriate location
   - Ensures directory exists
   - Confirms with user

**Example output:** A complete command file like `pries-implement.md` or `ensure-ci.md`

### /skill-creator (manage-skill-creator skill)

**Purpose:** Guide creation of effective skills

**What it generates:**

1. **Understanding phase:**
   - Asks for concrete examples of skill usage
   - Validates triggering scenarios
   - Clarifies functionality

2. **Planning phase:**
   - Identifies reusable resources:
     - Scripts (deterministic code)
     - References (documentation)
     - Assets (templates, files)

3. **Initialization:**
   - Runs `scripts/init_skill.py <skill-name> --path <output-directory>`
   - Creates skill directory structure:
     ```
     skill-name/
     ├── SKILL.md (template with TODOs)
     ├── LICENSE.txt
     ├── scripts/ (example files)
     ├── references/ (example files)
     └── assets/ (example files)
     ```

4. **Resource implementation:**
   - User/Claude adds scripts, references, assets
   - Scripts are tested for correctness
   - References are organized by domain/framework

5. **SKILL.md authoring:**
   - Writes frontmatter (`name`, `description` with triggers)
   - Writes body (instructions, bundled resource references)
   - Keeps body lean (<500 lines)
   - Uses progressive disclosure patterns

6. **Packaging:**
   - Runs `scripts/package_skill.py <path/to/skill-folder>`
   - Validates structure and frontmatter
   - Creates `.skill` file (zip with .skill extension)
   - Reports validation errors if any

**Example output:** A complete skill directory like `manage-skill-creator/` or `arch-writing-plans/`

### Comparison: Command-Creator vs Skill-Creator

| Aspect | Command-Creator | Skill-Creator |
|--------|-----------------|---------------|
| **Output Format** | Single markdown file | Directory with SKILL.md + resources |
| **Bundled Resources** | No | Yes (scripts, references, assets) |
| **Initialization** | Manual file creation | Automated via `init_skill.py` |
| **Packaging** | No packaging step | Automated via `package_skill.py` |
| **Validation** | Manual review | Automated validation in packaging |
| **Distribution** | Copy .md file | Distribute .skill file (zip) |
| **Naming** | Strict kebab-case | No strict convention |
| **Triggering** | User invocation | Auto-triggered by description match |
| **Location** | `.claude/commands/` | `.agents/skills/` or custom |

---

## Key Takeaways

### Architectural Summary

1. **Commands are user-facing workflow automation tools**
   - Invoked explicitly via `/command-name`
   - Orchestrate agents and define execution flow
   - Support arguments and options
   - Can delegate to specialized agents

2. **Skills are knowledge packages for Claude**
   - Auto-triggered by description matching
   - Provide procedural knowledge, domain expertise, tools
   - Support bundled resources (scripts, references, assets)
   - Use progressive disclosure to minimize context usage

3. **Agents are specialized personas with constraints**
   - Delegated to by commands via `agent:` field and `/subtask` syntax
   - Have specific skills, permissions, and missions
   - Isolated responsibilities with fine-grained access control
   - Execute within defined constraints (read-only, write to specific paths, limited bash)

### Critical Design Patterns

1. **Commands orchestrate, agents execute, skills provide knowledge**
   - Top-down: Command → Agent → Skill
   - Commands define "what" and "when"
   - Agents define "who" and "how" (with constraints)
   - Skills define "knowledge" and "tools"

2. **Progressive disclosure minimizes context usage**
   - Skills: metadata → body → resources (load on demand)
   - Commands: frontmatter defines orchestration, body provides instructions
   - Agents: frontmatter defines permissions/skills, body provides persona

3. **Separation of concerns**
   - **User workflows** → Commands
   - **Agent capabilities** → Skills
   - **Agent constraints** → Agents
   - **Automation logic** → Commands
   - **Domain knowledge** → Skills
   - **Execution personas** → Agents

4. **Multi-agent orchestration via commands**
   - Commands use `/subtask` syntax to delegate to agents
   - Agents work in parallel or sequence
   - Results flow between phases via `$RESULT[phase_id]`
   - Convergence cycles for iterative refinement

### When to Create Each

**Create a Command when:**
- You have a repetitive workflow users invoke explicitly
- You need multi-step orchestration with agent delegation
- You want workflow automation triggered by users
- Example: `/submit-stack`, `/ensure-ci`, `/pries-implement`

**Create a Skill when:**
- You have specialized knowledge/tools Claude needs
- You want capabilities auto-triggered by task requirements
- You have bundled resources (scripts, docs, templates)
- Example: `arch-writing-plans`, `dev-tdd`, `manage-skill-creator`

**Create an Agent when:**
- You need a specialized persona with specific constraints
- You want fine-grained permissions and skill access
- You need isolated responsibility boundaries
- Example: `pries-pm`, `pries-check`, `pries-test`

### Integration Best Practices

1. **Commands should be user-centric** - Describe what the workflow does from the user's perspective
2. **Skills should be knowledge-centric** - Focus on procedural knowledge and tools
3. **Agents should be persona-centric** - Define clear roles, missions, and constraints
4. **Use commands for orchestration** - Don't put orchestration logic in skills or agents
5. **Use skills for reusable knowledge** - Don't duplicate knowledge across commands
6. **Use agents for isolation** - Don't give unbounded permissions to commands
7. **Keep SKILL.md lean** - Move details to bundled references
8. **Keep command frontmatter rich** - Orchestration logic belongs in frontmatter
9. **Keep agent permissions minimal** - Grant only what's needed for the mission
10. **Document anti-patterns** - Explicitly state what NOT to do in each artifact

---

## Conclusion

The harness-tooling architecture provides three complementary abstractions:

- **Commands** = User-invocable workflows (slash commands)
- **Skills** = Knowledge packages (auto-triggered capabilities)
- **Agents** = Specialized personas (delegated executors with constraints)

Together, they enable:
- Reusable workflow automation (commands)
- Domain expertise injection (skills)
- Multi-agent orchestration (commands + agents)
- Fine-grained access control (agents)
- Progressive knowledge loading (skills)
- Separation of concerns (all three)

This architecture powers the BMAD methodology, PRIES workflow, and multi-agent TDD patterns used throughout the harness ecosystem.
