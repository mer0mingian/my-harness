# MATD Plugin Specification

**Status:** Approved  
**Created:** 2026-05-08  
**Parent:** [harness-v1-master-plan.md](harness-v1-master-plan.md)

---

**Scope Note:** This specification describes the **matd Claude Code plugin** (`.agents/plugins/matd/`). The repository also contains a separate **matd SpecKit extension** (`spec-kit-multi-agent-tdd/`) that implements the same MATD methodology for the SpecKit CLI. See [AGENTS.md](../../../AGENTS.md) for the distinction between these two artifacts.

---

## Purpose

The **MATD (Multi-Agent Test-Driven Development) Plugin** provides the complete workflow runtime for Claude Code sessions. It implements the MATD methodology with specialized agents and marketplace skills.

## Plugin Architecture

### Option B: Modular Plugin Structure

```
harness-tooling/
├── .agents/                        # Canonical flat structure (OpenCode compatible)
│   ├── agents/
│   │   ├── matd-orchestrator.md
│   │   ├── matd-specifier.md
│   │   ├── matd-critical-thinker.md
│   │   ├── matd-architect.md
│   │   ├── matd-c4-context.md
│   │   ├── matd-c4-container.md
│   │   ├── matd-c4-component.md
│   │   ├── matd-c4-code.md
│   │   ├── matd-qa.md
│   │   └── matd-dev.md
│   └── skills/                     # Existing skills (no rename)
│       ├── arch-*/
│       ├── dev-*/
│       ├── general-*/
│       ├── orchestrate-*/
│       ├── python-*/
│       ├── review-*/
│       └── stdd-*/
│
└── .claude/                        # Claude Code plugin structure (nested, symlinked)
    ├── agents/                     # Symlinks → .agents/agents/matd-*.md
    ├── skills/                     # Symlinks → .agents/skills/*
    └── .claude-plugin/
        └── plugin.json             # MATD plugin manifest
```

**Separate plugins for non-MATD content:**
- `harness-manage-plugin/` - manage-* skills (skill-creator, mcp-builder, etc.)
- `harness-file-ops-plugin/` - file-ops-* skills (pdf, pptx, xlsx)
- `harness-context-plugin/` - context-* skills
- Additional marketplace plugins grouped by prefix

## Agent Mapping: Diagram → MATD

Based on the "Agentic Engineering Workflow" diagram, the workflow has these roles:

| Diagram Role | MATD Agent | Source(s) | Responsibilities |
|---|---|---|---|
| **Orchestrator** | `matd-orchestrator` | `stdd-workflow-orchestrator` | User-facing PM, workflow coordination, approval gates |
| **Res** (Research) | `matd-specifier` | `stdd-specification-agent` | Requirements engineering, stakeholder interviews, spec writing |
| **Crit** | `matd-critical-thinker` | `stdd-critical-thinking-subagent` | Red team validation, edge case discovery, risk analysis |
| **Arch** (general + C4s) | `matd-architect` | `daniels-architect` | Solution design, architecture patterns; delegates to C4 specialists |
| - | `matd-c4-context` | `c4-context` | C4 Context diagram generation |
| - | `matd-c4-container` | `c4-container` | C4 Container diagram generation |
| - | `matd-c4-component` | `c4-component` | C4 Component diagram generation |
| - | `matd-c4-code` | `c4-code` | C4 Code diagram generation |
| **QA** | `matd-qa` | `stdd-qa-subagent` | Test architecture, E2E test creation, test verification |
| **SWE** | `matd-dev` | `python-dev` + `pries-make` | TDD implementation with file-manifest enforcement |

### Gap Analysis

✅ **Perfect 1:1 mapping** - All diagram roles have corresponding MATD agents.

## Agent Skill Permissions

Each agent has access to specific skill categories aligned with their role:

### matd-orchestrator
**Role:** User-facing PM and workflow coordinator

**Allowed skills:**
- `orchestrate-*` (all orchestration skills)
- `general-*` (all general skills)
- `stdd-openspec`
- `stdd-pm-linear-integration`
- `stdd-ask-questions-if-underspecified`

**Rationale:** Needs full orchestration capabilities, issue tracking, and stakeholder communication.

### matd-specifier
**Role:** Requirements engineer

**Allowed skills:**
- `stdd-product-spec-formats`
- `stdd-project-summary`
- `stdd-openspec`
- `stdd-ask-questions-if-underspecified`
- `general-grill-*`
- `general-system-design`

**Rationale:** Focused on requirements gathering, spec writing, and clarifying ambiguities.

### matd-critical-thinker
**Role:** Red team validator

**Allowed skills:**
- `stdd-ask-questions-if-underspecified`
- `review-check-correctness`
- `general-grill-*`

**Rationale:** Discovers edge cases, challenges assumptions, validates completeness.

### matd-architect
**Role:** Solution designer

**Allowed skills:**
- `arch-*` (all architecture skills)
- `general-system-design`
- `general-improve-codebase-architecture`
- `stdd-openspec`
- `dev-backend-to-frontend-handoff`

**Rationale:** Designs solutions, creates ADRs, delegates to C4 specialists.

### matd-c4-context
**Role:** C4 Context diagram specialist

**Allowed skills:**
- `arch-c4-architecture`
- `arch-mermaid-diagrams`
- `general-system-design`

**Rationale:** Generates system context diagrams.

### matd-c4-container
**Role:** C4 Container diagram specialist

**Allowed skills:**
- `arch-c4-architecture`
- `arch-mermaid-diagrams`

**Rationale:** Generates container-level architecture diagrams.

### matd-c4-component
**Role:** C4 Component diagram specialist

**Allowed skills:**
- `arch-c4-architecture`
- `arch-mermaid-diagrams`
- `arch-api-design-principles`

**Rationale:** Generates component diagrams with API interfaces.

### matd-c4-code
**Role:** C4 Code diagram specialist

**Allowed skills:**
- `arch-c4-architecture`
- `arch-mermaid-diagrams`

**Rationale:** Generates code-level sequence/class diagrams.

### matd-qa
**Role:** Test architect and auditor

**Allowed skills:**
- `review-*` (all review skills)
- `python-testing-uv-playwright`
- `review-e2e-testing-patterns`
- `review-webapp-testing`
- `stdd-test-author-constrained`
- `general-verification-before-completion`

**Rationale:** Creates E2E tests, verifies implementation, audits test coverage.

### matd-dev
**Role:** Implementation engineer

**Allowed skills:**
- `dev-*` (all dev skills)
- `python-*` (all Python skills)
- `stdd-test-driven-development`
- `stdd-make-constrained-implementation`
- `general-python-environment`
- `general-solid`
- `general-verification-before-completion`

**Rationale:** Implements features with TDD, respects file manifests, runs within sandbox constraints.

### Base Skills (ALL agents)
- `general-rtk-usage` - Token optimization
- `general-git-guardrails-claude-code` - Safe git operations
- `general-finishing-a-development-branch` - Branch hygiene
- `general-using-git-worktrees` - Workspace isolation

## matd-dev: Merged Implementation

The `matd-dev` agent merges capabilities from two sources:

1. **`python-dev`** - Enterprise Python patterns, FastAPI stack, async expertise
2. **`pries-make`** - File-manifest enforcement, TDD discipline, sandbox constraints

### Key Responsibilities
- Implement features strictly per OpenSpec tasks
- Follow Red-Green-Refactor TDD loop
- Respect file-manifest boundaries (no unauthorized file creation/deletion)
- No new dependencies without approval
- Sandboxed bash (no git, pip, curl, sudo)
- Verify via fresh test output

### Output Contract
Every implementation includes:
- `status`: GREEN / SCOPE_ESCALATION / BLOCKED
- `files_changed`: List of modified files
- `verification`: Command, exit code, test output excerpt
- `criteria_results`: Per-criterion PASS/FAIL with evidence
- `regression`: Regression test results

### Escalation Triggers
- `SCOPE_ESCALATION`: File outside manifest needed, rename required, new dependency needed
- `BLOCKED`: Missing inputs, broken test environment, three failed GREEN attempts

## Implementation Tasks

### M2: Flatten and Restructure (Modified)

**Current state:** `.agents/agents/` is already flat ✅

**New tasks:**
1. Rename existing agents to `matd-*` prefix
2. Merge `python-dev` + `pries-make` → `matd-dev`
3. Update all agent frontmatter with:
   - New names
   - Workflow context (reference diagram)
   - Skill permission lists (per tables above)
   - MATD-specific coordination notes

### M3: Claude Code Plugin Structure

Create `.claude/` nested structure with symlinks:

```bash
.claude/
├── agents/
│   ├── matd-orchestrator.md -> ../../.agents/agents/matd-orchestrator.md
│   ├── matd-specifier.md -> ../../.agents/agents/matd-specifier.md
│   └── ... (all matd-* agents)
├── skills/
│   ├── arch-api-design-principles -> ../../.agents/skills/arch-api-design-principles/
│   └── ... (all skills used by MATD agents)
└── .claude-plugin/
    └── plugin.json
```

**plugin.json structure:**
```json
{
  "name": "matd",
  "version": "1.0.0",
  "description": "Multi-Agent Test-Driven Development workflow for SpecKit",
  "agents": "agents/",
  "skills": "skills/"
}
```

### M4: OpenCode Compatibility

OpenCode reads flat `.agents/` directly - no changes needed. Permission ACLs in agent frontmatter work natively.

### M5: Gemini Scaffolding Only

Create `.gemini/` directory structure but **no functional plugin**:
```
.gemini/
├── extensions/
│   └── matd-research/
│       └── README.md  # "Gemini support planned for v2"
└── .gitkeep
```

## References

- Diagram: `/home/minged01/repositories/harness-workplace/Agentic Engineering Workflow.png`
- Claude Code plugin docs: https://code.claude.com/docs/en/plugins-reference
- STDD workflow reference: [.agents/docs/stdd-workflow.md](../../.agents/docs/stdd-workflow.md)
