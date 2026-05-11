# spec-kit-agent-assign Extension Analysis

**Location:** /home/minged01/repositories/harness-workplace/spec-kit-agent-assign/
**Analyzed:** 2026-05-07
**Purpose:** Empirical study of a real SpecKit extension implementation

---

## Directory Structure

```
spec-kit-agent-assign/
├── extension.yml                    # Extension manifest (YAML)
├── commands/                        # Command definitions
│   ├── assign.md                    # Agent assignment command
│   ├── validate.md                  # Assignment validation command
│   └── execute.md                   # Agent-powered execution command
├── README.md                        # User documentation
├── CLAUDE.md                        # Claude Code instructions (excluded from install)
├── CHANGELOG.md                     # Version history
├── LICENSE                          # MIT License
├── agents.png                       # Documentation image
├── .extensionignore                 # Install exclusion rules
├── .gitignore                       # Git exclusion rules
└── .git/                            # Git repository (excluded from install)
```

**Key Observations:**
- Extension root contains ONLY the manifest, commands directory, and documentation
- No Python scripts, no shell helpers, no lib/ or src/ directories
- Commands are pure markdown files with YAML frontmatter
- .extensionignore excludes developer-only files (.git, CLAUDE.md, .specify/)

---

## Manifest File Analysis

**File:** `/home/minged01/repositories/harness-workplace/spec-kit-agent-assign/extension.yml`

```yaml
schema_version: "1.0"

extension:
  id: "agent-assign"                # Extension ID (used in command namespacing)
  name: "Agent Assign"              # Display name
  version: "1.1.0"                  # Semantic version
  description: "Assign specialized Claude Code agents to spec-kit tasks for targeted execution"
  author: "xuyang"
  repository: "https://github.com/xymelon/spec-kit-agent-assign"
  license: "MIT"

requires:
  speckit_version: ">=0.7.1"        # Minimum spec-kit version required
  commands:                          # Dependencies on other spec-kit commands
    - "speckit.tasks"
    - "speckit.implement"

provides:
  commands:
    - name: "speckit.agent-assign.assign"
      file: "commands/assign.md"
      description: "Scan available agents and assign them to tasks in tasks.md"
    - name: "speckit.agent-assign.validate"
      file: "commands/validate.md"
      description: "Validate that all agent assignments are correct and agents exist"
    - name: "speckit.agent-assign.execute"
      file: "commands/execute.md"
      description: "Execute tasks by spawning the assigned agent for each task"

hooks:
  after_tasks:                       # Hook that runs after /speckit.tasks
    command: "speckit.agent-assign.assign"
    optional: true
    prompt: "Assign agents to the generated tasks?"
    description: "Automatically assign specialized agents to tasks after generation"

tags:
  - "agent"
  - "automation"
  - "implementation"
```

**Manifest Pattern Analysis:**

| Field | Purpose | Pattern |
|-------|---------|---------|
| `extension.id` | Namespace prefix for commands | kebab-case, used as `speckit.{id}.{command}` |
| `requires.speckit_version` | Version constraint | Semver range (>=, >, <, <=, ==) |
| `requires.commands` | Command dependencies | List of fully-qualified command names |
| `provides.commands` | Commands this extension adds | Each has name, file path, description |
| `provides.commands[].name` | Command invocation name | Format: `speckit.{extension-id}.{command-name}` |
| `provides.commands[].file` | Command definition path | Relative to extension root |
| `hooks.after_tasks` | Hook integration point | Triggers after specified command completes |
| `hooks.*.optional` | User confirmation required | If true, prompts user before running |
| `tags` | Extension categorization | Used for discovery/filtering |

**Critical Insight:** Commands are namespaced as `speckit.{extension-id}.{command-name}`, not just `{extension-id}.{command-name}`. This extension uses `speckit.agent-assign.assign`, not `agent-assign.assign`.

---

## Command Implementation Format

### Structure: 100% Markdown + YAML Frontmatter

All three commands follow the same pattern:
- **YAML frontmatter** (between `---` delimiters) for metadata
- **Markdown body** for command instructions to Claude Code

### Command 1: assign.md

**File:** `/home/minged01/repositories/harness-workplace/spec-kit-agent-assign/commands/assign.md`
**Format:** Markdown with YAML frontmatter
**Length:** 121 lines

**Frontmatter:**
```yaml
---
description: Scan available Claude Code agents and assign them to tasks in tasks.md
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks
handoffs:
  - label: Validate Assignments
    agent: speckit.agent-assign.validate
    prompt: Validate all agent assignments
    send: true
  - label: Execute With Agents
    agent: speckit.agent-assign.execute
    prompt: Execute tasks with assigned agents
---
```

**Frontmatter Fields:**
- `description` - Command description shown in help/UI
- `scripts.sh` - Shell script path for prerequisite checks (references spec-kit core scripts)
- `scripts.ps` - PowerShell equivalent
- `handoffs` - Agent handoff suggestions (shown as quick actions after command completes)
- `handoffs[].label` - Button/link text
- `handoffs[].agent` - Target command to invoke
- `handoffs[].prompt` - Pre-filled prompt text
- `handoffs[].send` - Auto-send (true) vs wait for user edit (false)

**Body Structure (7 numbered steps):**

1. **User Input Section:**
   ```markdown
   ## User Input
   
   ```text
   $ARGUMENTS
   ```
   
   You **MUST** consider the user input before proceeding (if not empty).
   ```
   The `$ARGUMENTS` placeholder is replaced by spec-kit with actual user input when command is invoked.

2. **Outline Section (numbered steps 1-7):**
   ```markdown
   ## Outline
   
   1. **Setup**: Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list...
   2. **Scan Agent Definitions**: Discover all available Claude Code agent definition files...
   3. **Load Tasks**: Read tasks.md from FEATURE_DIR...
   4. **Auto-Match Agents to Tasks**: For each task, analyze its description...
   5. **Present Assignments for Confirmation**: Display a summary table...
   6. **Write Agent Assignments File**: Generate `agent-assignments.yml`...
   7. **Report**: Output a summary...
   ```

**Key Pattern Observations:**
- Uses `{SCRIPT}` placeholder (replaced by spec-kit with platform-appropriate script path from frontmatter)
- Instructions are imperative ("Run X", "Parse Y", "Generate Z")
- Includes detailed formatting examples (tables, YAML structures)
- References spec-kit core prerequisite scripts, but they're NOT in the extension directory
- File I/O operations are described in natural language, not scripted

### Command 2: validate.md

**File:** `/home/minged01/repositories/harness-workplace/spec-kit-agent-assign/commands/validate.md`
**Format:** Markdown with YAML frontmatter
**Length:** 125 lines

**Frontmatter:**
```yaml
---
description: Validate that all agent assignments are correct and agents exist
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks
handoffs:
  - label: Reassign Agents
    agent: speckit.agent-assign.assign
    prompt: Reassign agents to fix validation issues
  - label: Execute With Agents
    agent: speckit.agent-assign.execute
    prompt: Execute tasks with assigned agents
    send: true
---
```

**Body Highlights:**
- Explicitly states "This command is **READ-ONLY**"
- 7 numbered steps: Setup, Check file exists, Load inputs, Rescan agents, Run validation checks, Generate report, Final verdict
- Detailed validation check specs (Check 1: Coverage, Check 2: Agent Existence, etc.)
- Includes example output format with pass/fail verdicts

**Validation Checks Implemented:**
1. **Coverage** - Every task has an assignment
2. **Agent Existence** - All assigned agents exist on disk
3. **Agent Conflicts** - No duplicate agent names at different hierarchy levels
4. **Agent Drift** - Detect agents added/removed since assignment
5. **Frontmatter Validity** - Agent files have proper YAML frontmatter

### Command 3: execute.md

**File:** `/home/minged01/repositories/harness-workplace/spec-kit-agent-assign/commands/execute.md`
**Format:** Markdown with YAML frontmatter
**Length:** 133 lines

**Frontmatter:**
```yaml
---
description: Execute tasks by spawning the assigned agent for each task
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---
```

**Notable Differences:**
- No handoffs (final command in workflow)
- Script includes `--include-tasks` flag for task content parsing

**Body Highlights (9 numbered steps):**
1. Setup
2. Check assignment file exists
3. Load implementation context (tasks.md, agent-assignments.yml, plan.md, spec.md, etc.)
4. Project setup verification (ignore files)
5. Parse execution plan (phases, dependencies, assignments)
6. **Execute tasks phase by phase** - This is the core implementation logic
7. Progress tracking
8. Error handling
9. Completion validation

**Execution Modes Defined:**
- **Mode A (Default)**: Execute task inline in current context
- **Mode B (Specialized Agent)**: Spawn named agent with task-specific prompt

**Critical Pattern:** The execute command describes TWO different execution strategies and tells Claude Code how to choose between them based on the agent assignment.

---

## Scripts and Helpers

**Actual Scripts in Extension:** NONE

**Script References in Commands:**
- `scripts/bash/check-prerequisites.sh` (referenced in frontmatter)
- `scripts/powershell/check-prerequisites.ps1` (referenced in frontmatter)

**Reality Check:** These scripts are NOT in the spec-kit-agent-assign directory. They are part of the spec-kit core installation, located in the host project's `.specify/` directory. Extensions reference them, but do not ship them.

**Pattern:**
- Extensions declare script dependencies in frontmatter
- Spec-kit runtime resolves script paths from core installation
- `{SCRIPT}` placeholder in command body is replaced with actual path at execution time
- Scripts return JSON output that commands parse for context (FEATURE_DIR, AVAILABLE_DOCS, etc.)

**No Python/Shell Helpers:** This extension has ZERO executable scripts of its own. All logic is expressed as natural language instructions to Claude Code in the command markdown files.

---

## Agent Integration

### How Agents Are Used

**Discovery Mechanism:**
The `assign` command scans for agent definition files following Claude Code's official hierarchy:

1. **Project-level** (highest priority): `.claude/agents/*.md`
2. **User-level** (lowest priority): `~/.claude/agents/*.md`

**Agent File Format:**
Standard Claude Code agent definition files (markdown with YAML frontmatter):

```markdown
---
description: Backend development specialist for Python/FastAPI
---

You are a backend development specialist...
```

**Agent Invocation:**
The `execute` command uses the assigned agent name to spawn a subagent:
- Mode A (default): Execute inline
- Mode B (named agent): "Use the assigned agent (by name) to execute this task"

**Key Insight:** The extension does NOT define any agents. It DISCOVERS and ROUTES to existing agents. Agents are maintained separately in `.claude/agents/` directories.

### Agent Assignment Storage

**File:** `agent-assignments.yml` (generated in feature directory)

**Format:**
```yaml
# Agent Assignments
# Feature: <feature-name from plan.md or branch name>
# Generated: <timestamp>
# Command: /speckit.agent-assign.assign

agents_scanned:
  - name: "backend-dev"
    source: "project"
    description: "Backend development specialist"
  - name: "frontend-dev"
    source: "project"
    description: "Frontend React/TypeScript specialist"

assignments:
  T001:
    agent: "default"
    reason: "General setup task, no specialized agent needed"
  T002:
    agent: "backend-dev"
    reason: "Task involves data model creation, matches backend-dev capabilities"
```

**Storage Location:** `FEATURE_DIR/agent-assignments.yml` (alongside `tasks.md`, `plan.md`, etc.)

---

## Key Patterns Observed

### 1. Extension Structure

```
extension-root/
├── extension.yml                    # Manifest (REQUIRED)
└── commands/                        # Command definitions (REQUIRED)
    ├── command1.md
    ├── command2.md
    └── command3.md
```

**Anti-patterns NOT observed:**
- No scripts/ directory
- No lib/ or src/ directory
- No requirements.txt or package.json
- No executable code of any kind

**Conclusion:** SpecKit extensions are pure command definitions, not code packages.

### 2. Command File Pattern

```markdown
---
description: Short description for UI
scripts:
  sh: path/to/prerequisite.sh --flags
  ps: path/to/prerequisite.ps1 -Flags
handoffs:
  - label: "Next Step"
    agent: "speckit.extension-id.command-name"
    prompt: "Pre-filled prompt text"
    send: true
---

## User Input

\```text
$ARGUMENTS
\```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Step Name**: Imperative instructions for Claude Code...
2. **Next Step**: More detailed instructions with examples...
```

**Placeholders:**
- `$ARGUMENTS` - Replaced with user input when command is invoked
- `{SCRIPT}` - Replaced with platform-appropriate script path from frontmatter

### 3. Manifest Command Naming

**Pattern:** `speckit.{extension-id}.{command-name}`

**Examples:**
- Extension ID: `agent-assign`
- Command names: `assign`, `validate`, `execute`
- Full command names: `speckit.agent-assign.assign`, `speckit.agent-assign.validate`, `speckit.agent-assign.execute`

**Invocation:** `/speckit.agent-assign.assign` (slash prefix added by user or UI)

### 4. Dependency Declaration

**In Manifest:**
```yaml
requires:
  speckit_version: ">=0.7.1"
  commands:
    - "speckit.tasks"
    - "speckit.implement"
```

**Effect:**
- Spec-kit validates version compatibility before installation
- Commands listed in `requires.commands` must be available (from core or other extensions)

**References vs Dependencies:**
- `requires.commands` - Hard dependencies (must exist)
- `scripts` in command frontmatter - Soft references (resolved at runtime)

### 5. Hook Integration

**In Manifest:**
```yaml
hooks:
  after_tasks:
    command: "speckit.agent-assign.assign"
    optional: true
    prompt: "Assign agents to the generated tasks?"
    description: "Automatically assign specialized agents to tasks after generation"
```

**Hook Naming:** `after_{command-name}` triggers after the specified command completes

**Optional Hooks:**
- `optional: true` - User is prompted before execution
- `optional: false` - Runs automatically without confirmation

**Available Hook Points:** Documented in spec-kit core (e.g., `after_tasks`, `after_plan`, `after_implement`)

### 6. Handoff Pattern

**In Command Frontmatter:**
```yaml
handoffs:
  - label: "Next Step"
    agent: "speckit.extension-id.command"
    prompt: "Pre-filled prompt"
    send: true
```

**Effect:** Creates quick action buttons/links after command completes

**Send Flag:**
- `send: true` - Auto-execute the handoff command
- `send: false` - Show prompt, wait for user to edit/confirm

**Use Case:** Workflow chaining (assign → validate → execute)

### 7. File I/O Pattern

**NOT Done:** Shell scripts, Python scripts, file manipulation code

**IS Done:** Natural language instructions to Claude Code:
```markdown
6. **Write Agent Assignments File**: Generate `agent-assignments.yml` in FEATURE_DIR with the following structure:

   ```yaml
   agents_scanned:
     - name: "backend-dev"
       source: "project"
   ```

   Write this file to `FEATURE_DIR/agent-assignments.yml`.
```

**Pattern:** Describe the desired file format and location. Claude Code performs the actual I/O.

### 8. Prerequisite Script Pattern

**Script Reference:**
```yaml
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks
```

**Command Body:**
```markdown
1. **Setup**: Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list.
```

**What Scripts Return:**
JSON object with context variables:
- `FEATURE_DIR` - Absolute path to current feature directory
- `AVAILABLE_DOCS` - List of available spec files (plan.md, spec.md, etc.)
- Other metadata (feature name, branch name, etc.)

**Script Location:** Spec-kit core installation (`.specify/scripts/`), NOT in extension directory

### 9. Error Handling Pattern

**Validation First:**
- `assign` command checks for agent files
- `validate` command checks for assignment file
- `execute` command checks for both

**Graceful Degradation:**
```markdown
If the agent definition file is missing at execution time, fall back to `default` mode and warn the user
```

**Clear Error Messages:**
```markdown
If missing, **STOP** and report: "No agent-assignments.yml found. Run `/speckit.agent-assign.assign` first."
```

### 10. Documentation Pattern

**README.md:** User-facing documentation with:
- Problem statement
- Solution overview
- Benchmarks/evaluation
- Quick start guide
- Command reference
- Architecture explanation
- Installation instructions

**CLAUDE.md:** Claude Code instructions with:
- Project overview
- Extension structure
- Command format notes
- Integration points

**.extensionignore:** Exclude developer-only files from user installations:
```
.git/
.gitignore
CLAUDE.md
.specify/
.claude/
```

---

## Comparison to Spec-Kit Documentation

### Matches Documented Spec

| Feature | Documented | Implemented | Match |
|---------|-----------|-------------|-------|
| Manifest format | YAML with extension, requires, provides | ✓ | YES |
| Command files | Markdown with YAML frontmatter | ✓ | YES |
| Command namespacing | `speckit.{id}.{command}` | ✓ | YES |
| Script references | Frontmatter scripts field | ✓ | YES |
| Handoffs | Frontmatter handoffs array | ✓ | YES |
| Hooks | Manifest hooks section | ✓ | YES |
| Dependency declaration | requires.commands | ✓ | YES |

### Deviations from Generic Extension Patterns

**NOT USED (despite being common in other extension systems):**
- No executable scripts in extension directory
- No package.json or requirements.txt
- No lib/ or src/ directory structure
- No build/compile step
- No tests directory
- No executable entry points

**USED (unique to spec-kit model):**
- Pure markdown command definitions
- Natural language instructions to AI
- Reference to core scripts, not bundled scripts
- Agent discovery via file system scanning
- YAML artifacts for state storage

---

## Architecture Insights

### Extension Execution Model

```
User invokes: /speckit.agent-assign.assign

Spec-Kit Runtime:
1. Loads extension.yml
2. Finds command definition: commands/assign.md
3. Resolves {SCRIPT} placeholder from frontmatter scripts
4. Replaces $ARGUMENTS with user input
5. Passes complete markdown to Claude Code as system prompt

Claude Code:
1. Reads markdown instructions
2. Executes numbered steps in order
3. Performs file I/O, shell commands, agent spawning as needed
4. Returns results to user

Spec-Kit Runtime:
5. Displays handoff options from frontmatter
6. User clicks handoff → repeat cycle for next command
```

### No Imperative Code Paradox

**Observation:** This extension performs complex logic (agent scanning, task matching, YAML generation, subagent spawning) WITHOUT any executable code.

**How:**
- All logic is declarative (described to Claude Code)
- Claude Code interprets instructions and performs actions
- File I/O happens via Claude Code's built-in tools
- Shell commands executed by Claude Code's bash tool
- Agent spawning uses Claude Code's agent invocation API

**Implication:** SpecKit extensions are AI-native, not traditional software packages.

### State Management

**Persistent State:**
- `agent-assignments.yml` (generated by assign, read by validate/execute)
- Agent definition files (`.claude/agents/*.md`)
- Spec files (`tasks.md`, `plan.md`, etc.)

**Ephemeral State:**
- Command execution context (FEATURE_DIR, AVAILABLE_DOCS from prerequisite script)
- Agent registry (rebuilt from file scan on each command)

**No Runtime State:**
- No databases
- No in-memory caches
- No daemon processes

### Dependency Architecture

```
spec-kit-agent-assign (this extension)
  ├── depends on: spec-kit core >= 0.7.1
  │   └── provides: check-prerequisites.sh
  ├── depends on: speckit.tasks command
  ├── depends on: speckit.implement command
  └── discovers: .claude/agents/*.md (runtime)
```

**Loose Coupling:**
- Extension does NOT bundle spec-kit core scripts
- Extension does NOT bundle agent definitions
- Extension discovers resources at runtime

**Tight Integration:**
- Commands reference core prerequisite scripts
- Hooks integrate with core workflow
- Handoffs chain commands together

---

## Summary: What This Extension Teaches Us

### 1. Extension = Manifest + Command Definitions

**Structure:**
```
extension-root/
├── extension.yml       # Metadata, dependencies, hooks
└── commands/*.md       # Natural language instructions for Claude Code
```

No scripts, no code, no build artifacts.

### 2. Commands = YAML Frontmatter + Markdown Body

**Frontmatter:** Metadata (description, script references, handoffs)
**Body:** Numbered steps of imperative instructions for Claude Code

### 3. Script References ≠ Script Bundling

**Pattern:** Reference spec-kit core scripts, don't bundle them.
**Mechanism:** `{SCRIPT}` placeholder resolved by spec-kit runtime.

### 4. Agent Discovery > Agent Bundling

**Pattern:** Scan file system for `.claude/agents/*.md`, don't ship agents.
**Mechanism:** Claude Code's built-in agent hierarchy.

### 5. YAML Artifacts for State

**Pattern:** Generate YAML files for persistent state (`agent-assignments.yml`).
**Mechanism:** Natural language instructions to Claude Code for file I/O.

### 6. Handoffs for Workflow Chaining

**Pattern:** Declare next-step commands in frontmatter.
**Mechanism:** Spec-kit runtime shows handoff options after command completes.

### 7. Hooks for Workflow Integration

**Pattern:** Declare hook integration points in manifest.
**Mechanism:** Spec-kit runtime triggers hook commands after specified events.

### 8. Validation Before Execution

**Pattern:** Separate validate command (read-only) before execute command (write).
**Mechanism:** Early error detection without side effects.

### 9. Mode Selection in Execute Commands

**Pattern:** Describe multiple execution strategies, let Claude Code choose.
**Mechanism:** Conditional logic in markdown instructions ("If X, do Y; else do Z").

### 10. Documentation-Driven Development

**Pattern:** README.md explains user workflow, CLAUDE.md explains implementation.
**Mechanism:** Separate docs for users vs AI agent developers.

---

## Recommended Adoption Patterns

For implementing `spec-kit-multi-agent-tdd`:

### DO:
- Create manifest with `tdd` extension ID
- Define commands as markdown files with YAML frontmatter
- Reference spec-kit core prerequisite scripts (don't bundle)
- Use YAML artifacts for state (test-assignments.yml, tdd-config.yml)
- Declare handoffs for workflow chaining (create → red → green → refactor)
- Add hooks for integration (after_tasks, after_implement)
- Scan for test agent definitions (don't bundle agents)
- Use numbered step outlines in command bodies
- Describe file formats and content in natural language
- Add validation commands before execution commands

### DON'T:
- Bundle Python/shell scripts in extension directory
- Create lib/ or src/ directories
- Use imperative code for logic
- Duplicate spec-kit core functionality
- Bundle test agent definitions with extension
- Assume FEATURE_DIR or other context variables
- Skip prerequisite script calls
- Mix read and write operations in validation commands
- Hardcode file paths (use FEATURE_DIR from prerequisite script)
- Forget handoff options for workflow continuity

### LEVERAGE:
- spec-kit core prerequisite scripts for context variables
- Claude Code's agent spawning for test execution
- YAML artifacts for test-code-spec traceability
- Handoffs for RED-GREEN-REFACTOR cycle automation
- Hooks for automatic test assignment after task generation
- Agent hierarchy for test specialist discovery
- Natural language instructions for complex logic

---

## Next Steps

1. **Design Manifest:** Define `tdd` extension with commands (create-test, red, green, refactor, verify)
2. **Map Commands:** Align TDD workflow steps to spec-kit command pattern
3. **Define Artifacts:** Specify YAML formats for test assignments, coverage tracking, etc.
4. **Draft Commands:** Write markdown command definitions following this pattern
5. **Test Discovery:** Determine how to scan for test agents and tools
6. **Handoff Chains:** Design workflow transitions (create → red → green → refactor → verify)
7. **Hook Integration:** Decide which spec-kit core commands should trigger TDD hooks
8. **Validation Strategy:** Separate read-only validation from write operations
9. **Documentation:** Write README.md (user workflow) and CLAUDE.md (AI instructions)
10. **Exclusions:** Define .extensionignore to exclude developer-only files

---

**Analysis Complete.** This extension demonstrates that SpecKit extensions are fundamentally different from traditional software packages. They are AI-native artifacts: structured natural language instructions packaged as versioned, installable units. The absence of executable code is not a limitation but a feature—it makes extensions portable, inspectable, and maintainable by AI agents themselves.
