# Workflow Orchestrator Tool: Complete Feature Requirements

**Session Date:** 2026-04-22
**Revised:** 2026-04-24 — incorporates session decisions on (a) two-tier plugin architecture, (b) `pydantic-ai-skills` + custom pydantic models as the schema layer, (c) sequence diagrams (mermaid / zenuml) and YAML are both first-class authoring surfaces compiling to one canonical manifest, (d) Drawflow/Baklava canvas deprioritised to v1.2+, (e) Claude Code + OpenCode full parity, Gemini CLI research-only.
**Status:** Approved scope for v1 of the `harness-workflow-runtime` plugin. Implementation plan: [harness-workflow-runtime-plan.md](../marketplace/plans/harness-workflow-runtime-plan.md).

---

## Core Requirements

### 1. Licensing & Openness

- Free and open source.
- Apache 2.0, MIT, or equivalent license preferred.
- Compliant with the [agentskills.io](https://agentskills.io/) open standard (Anthropic, Dec 2025; adopted by MS/OpenAI/Atlassian/Figma/Cursor/GitHub).

### 2. Multi-CLI Support

Primary v1 targets — full feature parity:

- **Claude Code** (primary; teammates work in it exclusively).
- **OpenCode** (full parity via froggy/subtasks2-class plugin).

Secondary v1 target — scoped subset:

- **Gemini CLI** — research workflows only; hook-based enforcement not available (see §19).

### 3. Workflow Definition

- **Custom workflows:** define static, manually chained workflows. Not auto-generated.
- **Multiple authoring surfaces, one compiled target.** The runtime plugin loads a **canonical `workflow.yaml`** (the compiled manifest). The YAML can be produced from multiple front-ends (see §18), all sharing one pydantic-backed compiler:
  1. **Sequence diagram** (mermaid `sequenceDiagram` or zenuml) — primary v1 authoring surface. Y-axis = phase sequence; X-axis = agents.
  2. **Interview command** (`/new-workflow`) — guided Q&A.
  3. **GUI canvas** (Drawflow / Baklava) — v1.2+; also exposes agent / skill / hook property editing.
- **Round-trip is asymmetric.** The compiler always emits a mermaid view from the canonical YAML for review. Going the other way — regenerating a diagram from a richly-annotated YAML — is lossy, because sequence notation cannot express every manifest field (complex file-pattern constraints, per-phase MCP-server lists, custom extensions). Fields that do not fit in the diagram remain authored in the YAML; the diagram is a **coarse skeleton view**.
- **Shareable as plugins** across the supported CLIs via the marketplace (see §6 and §6a).
- **Workflow nodes use Agent CLI skills** per the [agentskills.io](https://agentskills.io/home) spec. Skill references in the YAML use the `<workflow-prefix>-<role>-*` glob convention (e.g. `stdd-pm-*`).

### 4. Per-Workflow-Step Agent Configuration

Each phase can specify:

- **Agent / model assignment:** which driver agent runs the phase; which worker subagents are spawned.
- **Skill access:** which skill globs are available to the phase (expanded to explicit allowlists by the resolver).
- **MCP servers:** which MCP servers are accessible.
- **Hooks:** which lifecycle hooks execute (pre/post tool, pre/post phase).
- **Permission model:**
  - Write-access constraints (e.g. test writer: `**/test_*.py` only).
  - Bash scope (sandboxed vs. unrestricted).
  - External API access (Linear, GitHub, etc.).
  - File-system scope (read-only, specific directories).
- **Convergence gates:** max iterations, convergence rule (e.g. `same_findings_twice`), escalation target.
- **Parallel review logic:** multiple reviewers in parallel; fresh reviewers on rework.

### 5. Permission / Constraint Enforcement Model

- **Hard enforcement, layered** — not prompt-based self-policing:
  1. **Frontmatter / YAML (author-time)**: declares intent.
  2. **pydantic schema (CI / pre-commit)**: rejects malformed declarations before merge.
  3. **Resolver (session-start)**: expands globs into CLI-native ACLs (`allowedTools`, `permission.skill`).
  4. **Hooks (runtime)**: `PreToolUse` blocks disallowed calls; `PostToolUse` verifies file-pattern constraints, rolls back violations via git.
  5. **Container (blast-radius cap)**: the sandbox caps anything the above miss.
- **Per-step constraints:** different phases have different ACLs.
- **File-pattern gates:** post-step validation enforces only declared patterns were written.
- **Sandboxing:** worktree isolation + the shared sandbox container.
- **Independent validation:** the runtime plugin validates artifacts; never trusts the agent's self-report.
- **Blocking gates:** no path from FAIL to the next phase. A failed gate either retries the current phase, escalates to human, or aborts the workflow.

### 5a. Schema validation via pydantic (NEW)

One schema layer, three usages. All models live in the `harness-workflow-runtime` plugin's Python package.

| Artifact | Model source | Notes |
|---|---|---|
| `SKILL.md` | `pydantic_ai_skills.Skill` (upstream) | Full agentskills.io compliance inherited. Name constraints, description length, body-size warnings. |
| `AGENT.md` (dual Claude/OpenCode frontmatter) | `harness_workflow.schemas.Agent` | Custom — no upstream equivalent. Validates `skills:` globs, `permission.skill`, model, description. |
| Slash command frontmatter (`.claude/commands/*.md`) | `harness_workflow.schemas.Command` | Validates `allowed-tools`, `argument-hint`, `description`. |
| Hook entries (in `settings.json`) | `harness_workflow.schemas.HookEntry` | Validates matcher + command + event. |
| Workflow phase manifest (`workflow.yaml`) | `harness_workflow.schemas.WorkflowManifest` + `PhaseManifest` | The central contract. Encodes phases, drivers, workers, skills, gates, convergence, artifacts. |

The same models are used at **three points**:

- **CI / pre-commit** — fail fast on malformed frontmatter or YAML.
- **Install-time / session-start resolver** — expand globs, emit per-phase ACLs into CLI-native config.
- **Runtime hooks** — read the workflow manifest and current phase state, compute allow/deny on tool calls.

`pydantic-ai` (the agent framework) itself is **not** used as a runtime; only `pydantic` + `pydantic-ai-skills` as libraries.

### 6. Plugin Creation & Distribution

- Create plugins for **Claude Code, OpenCode, Gemini CLI**.
- Plugins include: hooks (proper formatting), skills (SKILL.md format), agents (AGENT.md / CLAUDE.md format), slash commands, workflow manifests.
- Plugins are version-controlled and distributable (marketplace or manual install).

### 6a. Two-tier plugin architecture (NEW)

| Tier | Plugin | Responsibility | Cadence |
|---|---|---|---|
| **Runtime** | `harness-workflow-runtime` (prerequisite — installed once per repo) | Schema models, resolver, hooks, `/workflow run|advance|status|reset`, `/new-workflow` interview command, state-file management. CLI-agnostic core; CLI-specific adapters. | Stable; breaking changes are rare and versioned. |
| **Workflow** | Per-workflow plugins — e.g. `stdd-feat`, `arch-review`, `story-refinement` (installed as needed) | A workflow manifest + the agents / skills / hooks specific to that workflow. Declares a dependency on a minimum runtime version. | High. Teams add their own. |

The runtime plugin does not ship any workflows. Workflow plugins ship no runtime code. They communicate through the workflow manifest schema.

---

## Workflow Features

### 7. Loop / Iteration Support

Explicit loop syntax in the phase manifest:

- Parallel iteration with fan-out / fan-in.
- Convergence detection (e.g. `same_findings_twice`).
- Escalation logic (e.g. `3 iterations → human`).
- Conditional looping (while/until patterns).
- Max-iteration limits with fail-safe.

Loops are **collapsed into phase metadata**, not expressed as graph topology. This keeps the DAG canvas clean and the YAML reviewable.

Example:

```
Phase 5: Parallel review (Check + Simplify) — max 3 cycles with convergence detection
  ↓ [same findings twice = stop early]
Phase 6: Implementation
```

### 8. Skill / Tool Assignment Per Step

Per-phase tool selection (not just per-agent). Skills are discoverable and loaded on-demand, not all at startup.

```
Phase: Plan
  Skills: stdd-plan-*

Phase: Write Tests
  Skills: stdd-test-*

Phase: Implement
  Skills: stdd-impl-*

Phase: Review
  Skills: review-*, general-git-*
```

### 9. Validation Gates

Per-phase validation requirements:

- Independent validation (runtime plugin, not agent self-report).
- File-pattern enforcement (`test_*.py` from test writer, `src/**` from implementer).
- Blocking state transitions.
- Pre-phase gates (prior artifact exists + validates).
- Pre-push gates (lint, typecheck, coverage thresholds).

### 10. Orchestration Patterns

- Sequential execution with clear handoffs.
- Parallel execution with result aggregation.
- Conditional branching (if/then/else).
- Recursive / hierarchical decomposition.
- Cross-agent message passing.

**Convergence, loop, and gate semantics live in the phase YAML schema and are enforced by the runtime plugin's hooks — never by agents self-policing.** An agent cannot silently decide it's converged; convergence is a post-phase check against the previous phase's output, run by the runtime.

---

## File Discovery & Directory Scoping

### 11. File-Based Skill Discovery

Mirrors Claude Code's SKILL.md loading mechanism and conforms to the [agentskills.io](https://agentskills.io/) progressive-disclosure spec. [`pydantic-ai-skills`](https://pypi.org/project/pydantic-ai-skills/) is the reference implementer and is used directly for SKILL.md validation.

- Tool discovers skills by scanning directories for `SKILL.md` files.
- Glob pattern support: `**/SKILL.md`, `skills/*/SKILL.md`, `stdd-*/SKILL.md`.
- Progressive loading:
  1. **Advertise (~100 tokens)**: inject skill names + descriptions at startup.
  2. **Load (on-demand)**: full SKILL.md loaded when the agent calls `load_skill`.
  3. **Read resources (on-demand)**: supplementary files loaded only when referenced.
  4. **Execute (on-demand)**: scripts executed when invoked.

Example:

```
Startup: "You have skills: code-review, test-writer, implementer, reviewer"
         (~200 tokens total for 10 skills)

During execution:
  Agent requests: "Load code-review skill"
  → Full SKILL.md content loaded (~2-5KB)

  Agent reads:    "I need POLICY_FAQ.md"
  → Only that file loaded (~1KB)

  Agent runs:     "Execute validate.py file=report.json"
  → Script executed as subprocess
```

### 12. Directory Scoping with Priority System

Multi-level discovery with clear priority:

```
Priority order (highest → lowest):
  1. .project/skills/*/SKILL.md           (project-local, committed to git)
  2. .team/skills/*/SKILL.md              (team-shared, optional)
  3. ~/.config/skills/*/SKILL.md          (user-global)
  4. /usr/local/skills/*/SKILL.md         (system-global, optional)

When skill names conflict: first match wins (project level overrides global).
```

### 13. Agent Access Control via File Patterns

Agents specify which skill directories / files they can access:

```yaml
# Option 1: skill wildcard patterns
agent: code_reviewer
  skills: ["review-*", "!review-write"]   # allow review-* except review-write

# Option 2: file-type restrictions
agent: test_writer
  resource_extensions: [".md", ".txt"]
  script_extensions: [".py"]

# Option 3: directory scoping
agent: implementer
  skill_directories:
    - .project/skills/stdd-impl-*
  resource_directories: ["references"]

# Option 4: approval gates
agent: deployer
  scripts:
    require_approval: true
    timeout_seconds: 300
    resource_limits:
      memory_mb: 512
      max_runtime_seconds: 120
```

---

## Anti-Patterns (What NOT to Build)

The marketplace **does** ship example workflows (`stdd-feat`, `arch-review`) that users opt into by installing their plugins. What it does **not** do:

### 14. No auto-assigned agents

- No implicit "if the task sounds like X, a reviewer wakes up."
- No "18 specialist personas" bundled as defaults.
- Workflow plugins declare their agents explicitly; the runtime does not pick.

### 15. No auto-loaded skill sets

- No skill auto-attaches based on task heuristics.
- Workflow plugins declare their skill globs; the resolver expands them to explicit lists.

### 16. No auto-generated workflows

- No "describe your task, get a workflow."
- Workflows are authored via the `/new-workflow` interview command or the Drawflow canvas (v1.1). Both produce YAML that a human reviews.

### 17. No self-learning / auto-improving

- No extracting patterns from PR feedback into new skills.
- No token-hungry third-party reflection plugins.
- Workflows are static once defined. Same workflow → same execution.

---

## Authoring, Validation, and Scope

### 18. Authoring UX

Three primary interfaces for creating workflow descriptions, in priority order for v1:

**Tier 1 — Manual, diagram-driven (primary v1):**

- Author a **sequence diagram** (mermaid `sequenceDiagram` or zenuml). Y-axis = phase sequence; X-axis = agents. Messages carry phase names; notes and a documented bracket convention carry inline metadata (e.g. `[skills: stdd-pm-*; writes: docs/tickets/**; converge: same_findings_twice, max=3]`).
- Author **agent definitions** (dual-frontmatter Markdown) and **hook definitions** (YAML fragments merged into `settings.json`) as separate files alongside the diagram.
- The compiler parses diagram + definitions into the canonical `workflow.yaml` and per-CLI ACLs. `par` blocks → parallel phases; `loop` blocks → convergence-gated phases; participants → agents.
- Rationale: mermaid is the notation ML engineers already sketch informal workflows in; it renders natively in VS Code + GitHub previews; the grammar we need is small enough to parse with a focused Python module.

**Tier 2 — Guided, conversational (ships alongside Tier 1):**

- The `/new-workflow` slash command interviews the author in structured Q&A and emits the same canonical YAML + a mermaid diagram. Validator runs before writing.
- Rationale: lowest-friction path for authors who prefer answering questions over drafting a diagram. Shares the compiler backend with Tier 1.

**Tier 3 — GUI canvas (v1.2+, deprioritised):**

- Drawflow or Baklava.js node canvas. Node = phase; driver / worker agents are node metadata. Additionally exposes **inline editors for agents, skills, hooks, and commands** so a teammate can author the full plugin surface without leaving the canvas, and may later hook into Claude Code directly (e.g., launch an authored workflow from the canvas).
- Compiles to the same canonical YAML. Deliberately shipped after Tier 1 + 2 have been dogfooded, so the GUI's property-editor forms reflect real schema usage rather than speculative fields.

**Rejected (not re-opened):**

- **BPMN.** Notation overhead mismatches an ML-engineering audience that thinks in DAGs.
- **Stately.ai Studio.** Hosted / proprietary; cannot ship.
- **Kestra, Windmill, Node-RED.** Schema-coupled to their runtimes, licence-awkward (AGPL), or weaker semantic fit than a purpose-built canvas.

All three tiers emit the same canonical YAML through a single pydantic-backed compiler (see implementation plan §7).

### 19. Gemini CLI scope (NEW)

- Scoped to research workflows only in v1.
- No hook-based enforcement — Gemini CLI's extension model does not expose a comparable pre-tool-use hook.
- The resolver emits Gemini extension manifests scoped to research skills. ACL hooks are omitted for Gemini.
- Aligns with the v1 architecture-decisions memo: "Gemini CLI is scoped to research workflows, not feature dev."

---

## Concrete Example: TDD Orchestration Workflow

Illustrative only. Skill references use `/code:*` placeholder syntax for readability; in practice they follow the `<workflow>-<role>-*` glob convention (e.g. `stdd-test-*` rather than `/code:write`).

### Workflow Definition (YAML)

```yaml
name: tdd-development
description: Test-driven development with parallel reviews and convergence gates.
phases: 11

phase_1:
  name: Setup
  driver: orchestrator
  steps:
    - verify_repo_structure
    - create_worktree
  skills: [/code:validate, /code:setup]
  no_write_access: true

phase_2:
  name: Fetch Issue
  driver: orchestrator
  steps:
    - fetch_issue_from_linear
    - parse_spec
  skills: [/code:analyze, /linear:read]
  external_apis: [linear]

phase_3:
  name: Parallel Review (Design & Simplify)
  driver: orchestrator
  workers: [reviewer_design, reviewer_simplify]
  concurrent_agents: 2
  convergence:
    max_iterations: 3
    convergence_rule: same_findings_twice
  agents:
    reviewer_design:
      model: claude-opus
      skills: [/code:analyze, /code:review]
      constraints:
        write_access: false
    reviewer_simplify:
      model: claude-opus
      skills: [/code:analyze, /code:review]
      constraints:
        write_access: false
  output_gate:
    approval_rule: all_reviewers_approve

phase_4:
  name: Decompose Work
  driver: architect
  model: claude-opus
  skills: [/code:analyze, /code:plan]
  output: work_units.json
  constraints:
    write_access: false

phase_5:
  name: Test-First Loop (per work unit)
  loop:
    type: fan_out
    items: work_units.json
    max_parallel: 2

  phase_5a:
    name: Write Failing Tests
    driver: test_writer
    model: claude-sonnet-4-6
    skills: [/code:write, /code:validate]
    constraints:
      write_access: "test_*.py, tests/**"
      bash_scope: sandboxed_pytest
      external_apis: []
    output_gate:
      validation: pytest_shows_red
      file_pattern_check: only_test_files_created

  phase_5b:
    name: Implement to Green
    driver: implementer
    model: claude-sonnet-4-6
    skills: [/code:write, /code:edit, /code:test]
    constraints:
      write_access: "src/**, lib/**"
      bash_scope: sandboxed_no_pip_git
      external_apis: []
    output_gate:
      validation: pytest_shows_green
      file_pattern_check: only_source_files_created
      coverage_threshold: ">= 95%"

phase_6:
  name: Final Review (Adversarial)
  driver: adversarial_reviewer
  model: claude-opus
  skills: [/code:analyze, /code:review, /code:test]
  constraints:
    write_access: false
  convergence:
    max_iterations: 1
    escalation_rule: if_issues_found_escalate_to_human

phase_7:
  name: Integration Tests
  driver: test_runner
  model: claude-opus
  skills: [/code:test, /code:validate]
  constraints:
    bash_scope: sandboxed_pytest
  output_gate:
    validation: all_tests_pass
    coverage_threshold: ">= 95%"

phase_8:
  name: Commit & PR
  driver: orchestrator
  skills: [/code:commit, /code:pr_create]
  constraints:
    write_access: git_operations_only
  gates:
    pre_commit:
      - lint_passes
      - type_check_passes
      - tests_pass
      - coverage_threshold_met
    pre_push:
      - ci_checks_pass
```

### Skill Directory Structure

```
my-tdd-workflow/
  .project/
    skills/
      code-review/SKILL.md
        - description: Review code for best practices
        - resources/: [POLICY.md, CHECKLIST.md]
        - scripts/: []

      test-writer/SKILL.md
        - description: Write test specifications
        - resources/: [TEST_PATTERNS.md]
        - scripts/: [validate_tests.py]

      implementer/SKILL.md
        - description: Implement code to pass tests
        - resources/: [DESIGN_PATTERNS.md, ARCHITECTURE.md]
        - scripts/: [run_tests.py, check_coverage.py]

  workflows/
    tdd-workflow.yaml

  agents/
    test_writer.md
    implementer.md
    reviewer.md
```

### Agent Definition Example

```markdown
# .project/agents/test_writer.md

---
description: Writes failing test specifications
model: claude-sonnet-4-6
permissions:
  skills: ["/code:write", "/code:validate"]
  write_access_pattern: "test_*.py"
  bash_scope: sandboxed_pytest
  external_apis: []
---

You are a test architecture specialist. Your responsibilities:

1. Read the feature specification
2. Design comprehensive test scenarios covering:
   - Happy path
   - Edge cases
   - Error conditions
   - Performance bounds
3. Write failing test stubs that will be implemented next

When writing tests:
- Use the TEST_PATTERNS.md resource for example patterns
- Ensure tests fail initially (RED state)
- Classify failures by type (assertion, exception, timeout)
- Document assumptions and expected behaviors

Available skills:
- /code:write (write test files)
- /code:validate (validate test syntax)
```

### Skill Definition Example

```markdown
# .project/skills/test-writer/SKILL.md

---
name: test-writer
description: Design and write comprehensive test specifications for features. Use when starting TDD cycle, writing failing tests, or designing test architecture.
compatibility: Requires Python 3.10+, pytest
metadata:
  author: team-qa
  version: "2.1"
---

# Test Writer Skill

## When to Use
- Starting a new feature implementation (TDD cycle)
- Writing failing test specifications
- Designing test scenarios and edge cases

## Process

### 1. Read the Feature Specification
- Understand requirements from issue
- Identify acceptance criteria
- Note performance/security constraints

### 2. Design Test Scenarios
Reference TEST_PATTERNS.md for examples. Design tests covering:
- **Happy path:** Standard use case
- **Edge cases:** Boundary conditions, empty input, max size
- **Error handling:** Invalid input, missing dependencies, timeouts
- **Performance:** Execution time, memory usage

### 3. Write Failing Tests
Create test file with pattern: `test_<feature>.py`

```python
# test_user_auth.py
import pytest
from src.auth import authenticate

def test_successful_login():
    """Happy path: valid credentials return user object."""
    user = authenticate(email="test@example.com", password="correct")
    assert user is not None
    assert user.email == "test@example.com"

def test_invalid_password():
    """Edge case: invalid password raises AuthError."""
    with pytest.raises(AuthError):
        authenticate(email="test@example.com", password="wrong")

def test_empty_email():
    """Edge case: empty email raises ValidationError."""
    with pytest.raises(ValidationError):
        authenticate(email="", password="password")
```
