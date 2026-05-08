---
description: "Solution Design: generate ADR comparing solution approaches and detailed C2/C3 architecture via c4-* agents"
agents:
  - c4-context
  - c4-container
  - c4-component
skills:
  - 'arch-mermaid-diagrams'
  - 'arch-c4-architecture'
  - 'arch-smart-docs'
tools:
  - 'filesystem/read'
  - 'filesystem/write'
templates:
  adr: templates/adr-template.md
  solution_design: templates/solution-design-template.md
exit_codes:
  0: "Success - ADR and Solution Design artifact created"
  1: "Validation failure - missing feature_id or c4-* agents not found"
  2: "Escalation required - template missing, contradiction detected, or write error"
---

# Solution Design Workflow (Multi-Agent TDD — ADR & Architecture)

This command generates an Architecture Decision Record comparing solution alternatives and a detailed Solution Design artifact using sequential c4-* agent orchestration.

## Prerequisites

- `feature_id` provided
- c4-context, c4-container, c4-component agents installed
- Templates available at `templates/adr-template.md` and `templates/solution-design-template.md`

## User Input

`/speckit.multi-agent.solution-design $ARGUMENTS`

**Arguments**:
- `$ARGUMENTS`: Feature identifier (e.g., `feat-123`). Required.

## Step 1: Validate Prerequisites

- If `$ARGUMENTS` is empty or not provided → ❌ Exit 1 with message: "Error: feature_id is required. Usage: /speckit.multi-agent.solution-design <feature_id>"
- Set `feature_id` from `$ARGUMENTS` (trim whitespace)
- Check that c4-context, c4-container, and c4-component agents exist in `.claude/agents/` or `~/.claude/agents/`
- If any c4-* agent is missing → ❌ Exit 1 with message listing all missing agents (all must be installed together with the plugin)
- Load config from `.specify/harness-tdd-config.yml` or use defaults:

| Key | Default | Purpose |
|-----|---------|---------|
| `artifacts.root` | `docs/features` | Root directory for feature artifacts |
| `workflow.agent_timeout` | `30` | Agent task timeout in minutes (default: 30 if key missing) |

If config file is missing or unreadable, continue with the defaults above. Log a warning but do not abort.

## Step 2: Load Context

Load all available context (in order of preference):

1. **PRD**: `{artifacts.root}/{feature_id}-prd.md`
2. **System Constitution**: search `docs/architecture/technical-constitution.md`, then `.specify/technical-constitution.md`
3. **Spec**: search `docs/features/{feature_id}.md`, `docs/features/{feature_id}-spec.md`, `.specify/specs/{feature_id}.md`
4. **Existing codebase analysis**: search for deepwiki/litho output in `docs/deepwiki/`, `docs/architecture/`. If none found AND `src/` exists, use `arch-smart-docs` skill to scan codebase structure.

If PRD and System Constitution are both missing:

⚠️ Warn: "Running solution-design without discover output increases spec drift risk. Proceeding with user input as primary context."

Proceed — ask user for a brief problem description to use as context.

## Step 3: Generate ADR

Using `arch-mermaid-diagrams` and `arch-c4-architecture` skills:

Fill `templates/adr-template.md` with **3 solution alternatives** (minimum 2). For each alternative:
- Description of the approach
- C1 Context mermaid diagram (C4Context syntax)
- C2 Container mermaid diagram (C4Container syntax)
- Pros/Cons evaluated against fixed criteria: **performance**, **maintainability**, **cost**, **complexity**

Agent recommendation: select the best alternative with explicit rationale referencing the criteria.

Save draft to: `{artifacts.root}/{feature_id}-adr.md`

- If `adr-template.md` is missing: ❌ Exit 2 with message: "Error: template not found at `templates/adr-template.md`"
- If save fails: ❌ Exit 2 with message: "Error: failed to write ADR to `{adr_path}`"

## Step 4: User Review Gate — ADR

**PAUSE. Present ADR to user.**

Show: "ADR created at `{adr_path}`. Please review the 3 solution alternatives. Which solution do you choose? (or accept the recommendation)"

Wait for user to confirm chosen solution before proceeding.

Update ADR: set `status: accepted`, record chosen alternative in `## Decision` section.

## Step 5: Invoke @c4-context Agent (Sequential)

Delegate to **@c4-context** agent with `arch-c4-architecture` and `arch-mermaid-diagrams` skills.

**Provide ALL context:** PRD + System Constitution + ADR (chosen solution summary) + codebase analysis (if available)

**Task for agent:** Generate C1 Context diagram for the chosen solution showing system boundary, external actors, and high-level interactions.

**Output:** C1 Context section content for solution-design artifact.

**If contradiction detected** (agent output conflicts with PRD or Constitution):
⚠️ Interrupt: describe the contradiction to user and request resolution before continuing. ❌ Exit 2 if unresolved.

## Step 6: Invoke @c4-container Agent (Sequential)

Delegate to **@c4-container** agent with `arch-c4-architecture` and `arch-mermaid-diagrams` skills.

**Provide ALL context:** PRD + Constitution + ADR + C1 output from Step 5 + codebase analysis

**Task:** Generate C2 Container diagram for the chosen solution.

**Output:** C2 Container section for solution-design artifact (this is the primary Decomposition View diagram).

**If contradiction detected:** interrupt and request resolution. ❌ Exit 2 if unresolved.

## Step 7: Invoke @c4-component Agent (Sequential)

Delegate to **@c4-component** agent with `arch-c4-architecture` and `arch-mermaid-diagrams` skills.

**Provide ALL context:** PRD + Constitution + ADR + C1 + C2 outputs + codebase analysis

**Task:** Generate C3 Component diagram for the chosen solution (internal structure of primary container).

**Output:** C3 Component section for solution-design artifact.

**If contradiction detected:** interrupt and request resolution. ❌ Exit 2 if unresolved.

## Step 8: Generate Remaining Views

Using outputs from Steps 5–7:

- **Dependency View:** Extract internal and external dependencies from C2/C3 diagrams. Describe coupling analysis.
- **Interface View:** Extract API contracts and interfaces visible in C2/C3. Note event schemas if event-driven.
- **Data Design View:** Generate data flow diagram (flowchart mermaid) and ERD (erDiagram mermaid) based on entities visible in C2/C3.

## Step 9: Assemble and Save Solution Design

Fill `templates/solution-design-template.md` with all outputs from Steps 5–8.

Save to: `{artifacts.root}/{feature_id}-solution-design.md`

- If `solution-design-template.md` is missing: ❌ Exit 2 with message: "Error: template not found at `templates/solution-design-template.md`"
- If save fails: ❌ Exit 2 with message: "Error: failed to write Solution Design to `{solution_design_path}`"

## Step 10: Validate Artifacts

Call: `python3 scripts/validate_artifact_structure.py {adr_path} {solution_design_path}`

- Post-generation warn-only check
- If the script exits 0: all good, continue to Step 11
- If issues found: escalate to human with diagnostics (do not fail silently)
- Exit code 2 from the validator means escalate: present the diagnostics to the user

## Step 11: Report

Show:

```
✓ ADR created at: {adr_path} (solution: <chosen alternative name>)
✓ Solution Design created at: {solution_design_path}
```

Suggest next step:

> Run `/speckit.plan {feature_id}` (Refinement phase)

## Exit Codes

- **0**: Success — ADR and Solution Design artifact created
- **1**: Validation failure — missing feature_id or c4-* agents not found
- **2**: Escalation required — template missing, contradiction unresolved, or write error

## Configuration Reference

`.specify/harness-tdd-config.yml` keys used by this command:

```yaml
artifacts:
  root: docs/features          # Root dir for ADR and solution-design output

workflow:
  agent_timeout: 30            # Agent task timeout in minutes (default: 30)
```

## Related Commands

- `/speckit.multi-agent.discover`: Run discovery phase (prerequisite for this command)
- `/speckit.plan`: Refinement phase (next step after solution-design)
- `/speckit.multi-agent.test`: Generate failing tests for a specified feature
- `/speckit.multi-agent.implement`: Implement feature code (RED → GREEN)
