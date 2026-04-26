# BMAD Integration Strategy for Harness Workflow Runtime

**Status:** Planning  
**Date:** 2026-04-26  
**Context:** Integration of BMAD methodology with harness SDD cycle for specification-driven development

---

## Table of Contents

1. [Workspace Overview](#workspace-overview)
2. [Current Development State](#current-development-state)
3. [BMAD Method Overview](#bmad-method-overview)
4. [Integration Architecture](#integration-architecture)
5. [Implementation Roadmap](#implementation-roadmap)
6. [References](#references)

---

## Workspace Overview

### Repository Structure

This workspace contains two sibling repositories with distinct responsibilities:

| Repository | Purpose | Cadence | Status |
|------------|---------|---------|--------|
| **[harness-tooling](../README.md)** | Marketplace for skills, agents, commands, and plugin manifests consumed by Claude Code, OpenCode, and Gemini CLI | Changes often | ✅ Active development |
| **[harness-sandbox](../../harness-sandbox/)** | Docker runtime stack: Dockerfile, docker-compose, host-side entry wrapper | Changes rarely | 📦 Fresh scaffold |

### Architectural Boundaries

**harness-tooling** (this repo):
- `.agents/` — canonical source for skills, agents, commands
- `.claude/`, `.opencode/`, `.gemini/` — thin wrappers (symlinks to `.agents/`)
- Skill naming: `stdd-*`, `orchestrate-*`, `review-*`, `general-*` prefixes
- Dual frontmatter: Both Claude Code and OpenCode formats maintained

**harness-sandbox**:
- Base: NVIDIA OpenShell-Community + Claude Code, OpenCode, Chloe, rtk
- Services: Haft MCP, CodeGraphContext MCP, optional Graphiti memory
- Not a monorepo — code bind-mounted from host, never baked into image

---

## Current Development State

### harness-tooling Status

**Recent Activity (last 15 commits):**
- Name audit proposal for skill prefixing
- Multi-agent compatibility corrections
- Plan updated for YAML/Drawflow/sequence diagram workflow creation
- Workflow orchestrator requirements finalized (2026-04-24)
- Reference workflows provided

**Current Inventory:**
- ~50+ skills across workflow categories
- Agent definitions with dual frontmatter (Claude/OpenCode)
- Commands in markdown format (no TOML for Claude Code)
- Gemini CLI scoped to research workflows only

**Active Documents:**
- [harness-v1-master-plan.md](harness-v1-master-plan.md) — v1 delivery scope
- [harness-v1-agent-tasks.md](harness-v1-agent-tasks.md) — subagent prompts
- [WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md](WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md) — complete feature spec
- [workflow-runtime-mermaid-grammar.md](workflow-runtime-mermaid-grammar.md) — sequence diagram authoring

### harness-sandbox Status

- Fresh scaffold created 2026-04-21
- Awaiting population per master plan Phase 1 (Sandbox build)
- Target: reproducible docker-compose sandbox
- Entry script: `bin/harness` for `up`, `shell`, `down`, `services` commands

---

## BMAD Method Overview

### What is BMAD?

**BMAD** (Breakthrough Method for Agile AI-Driven Development) is an AI-driven development framework that structures the entire software lifecycle from ideation through implementation using specialized AI agents and YAML-based workflow blueprints.

**Core Principles:**

1. **Structured Workflows** — YAML-based blueprints orchestrating specialized agent tasks
2. **Progressive Context Building** — 4 distinct phases, each producing documents that inform the next
3. **Specialized Agent Teams** — 12+ domain experts (PM, Architect, Developer, UX, QA, etc.)
4. **Living Documentation** — Everything versioned in Git for traceability
5. **Governance & Auditability** — Machine-readable history for compliance (SOC 2, HIPAA)

### BMAD Workflow Phases

**Phase 1: Analysis**
- Analyst agent clarifies goals, constraints, business context
- Outputs: Problem statement, stakeholder analysis, constraints document

**Phase 2: Product Management**
- PM agent defines requirements, user stories, acceptance criteria
- Outputs: Product Requirements Document (PRD), user stories, success metrics

**Phase 3: Architecture Design**
- Architect agent designs technical foundation, system boundaries
- Outputs: Architecture Decision Records (ADR), technical specifications

**Phase 4: Implementation**
- Developer agents implement following TDD/BDD patterns
- Outputs: Code, tests, integration artifacts

### BMAD vs. Traditional Agile

| Aspect | Traditional Agile | BMAD Method |
|--------|------------------|-------------|
| Planning | Human-driven, often informal | AI-driven, structured, documented |
| Documentation | Minimal, often outdated | Living, versioned, machine-readable |
| Traceability | Manual linking | Automatic artifact chains |
| Consistency | Varies by team/individual | Enforced by workflow schema |
| Compliance | Post-hoc audits | Built-in governance |

---

## Integration Architecture

### Alignment: BMAD ↔ Harness

Your harness-workflow-runtime design **already implements core BMAD principles**:

| BMAD Concept | Harness Implementation | Status |
|--------------|------------------------|--------|
| YAML workflow blueprints | `workflow.yaml` canonical manifest | ✅ Specified |
| Specialized agents | Agent definitions in `.agents/agents/` with role-based skills | ✅ Implemented |
| Progressive disclosure | `pydantic-ai-skills` progressive loading (advertise → load → execute) | ✅ Specified |
| Phase-based execution | Mermaid sequence diagrams → YAML compiler → phase orchestration | 🚧 In design |
| Validation gates | Independent validation via hooks, not agent self-report | ✅ Specified |
| Living documentation | Git-versioned workflows + artifacts | ✅ Architectural decision |
| Governance | pydantic schema validation at CI/runtime | ✅ Specified |

### Two Integration Patterns

#### Pattern A: BMAD as Specification Phase (Recommended)

Use BMAD planning agents to generate **input artifacts** that trigger harness implementation workflows.

```
┌─────────────────────────────────────────────────────────────┐
│                    BMAD Planning Phase                       │
│  (Analyst → PM → Architect → Product Owner)                  │
│                                                              │
│  Outputs:                                                    │
│  - docs/requirements/PRD-feature-X.md                        │
│  - docs/architecture/ADR-001-architecture.md                 │
│  - docs/tickets/USER-STORY-123.md                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Artifacts as inputs
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Harness STDD Implementation Workflow            │
│  (PM fetch → Arch decompose → Test write → Implement → Review)│
│                                                              │
│  Reads artifacts from docs/                                  │
│  Executes with skill-based constraints                       │
└─────────────────────────────────────────────────────────────┘
```

**Flow:**

1. **Trigger BMAD planning**: `/bmad-spec <feature-description>`
2. **BMAD agents execute**: Analysis → PM → Architecture phases
3. **Artifacts written**: Structured documents in `docs/requirements/`, `docs/architecture/`, `docs/tickets/`
4. **Validation gate**: Schema validation ensures BMAD outputs are well-formed
5. **Auto-trigger STDD**: Harness workflow starts with artifact URIs as phase 1 inputs
6. **Implementation proceeds**: Test-first development with independent validation

**Benefits:**
- Clean separation: specification vs. implementation
- BMAD handles "what to build" uncertainty
- Harness handles "how to build it" execution
- Both use same workflow runtime infrastructure

#### Pattern B: BMAD Workflow as Harness Plugin (Advanced)

Encode BMAD workflows directly in harness manifest format, making BMAD a first-class workflow plugin.

**Example: `bmad-planning.yaml`**

```yaml
name: bmad-specification-development
description: BMAD-style planning phase with specialized agents
version: "1.0"
runtime_dependency: "harness-workflow-runtime >= 1.0"

phases:
  phase_1:
    name: Problem Analysis
    driver: bmad-analyst
    model: claude-opus-4-7
    skills: [bmad-analyst-*, general-research-*]
    constraints:
      write_access: docs/analysis/**
      read_access: ["**/*.md", "src/**"]
      external_apis: []
    output:
      artifacts: [docs/analysis/problem-statement.md]
      schema: schemas/problem-statement.json
    gates:
      validation: validate-problem-statement.py
      approval_rule: stakeholder_review_optional

  phase_2:
    name: Product Management
    driver: bmad-pm
    model: claude-opus-4-7
    skills: [bmad-pm-*, stdd-pm-*, general-planning-*]
    constraints:
      write_access: docs/requirements/**
      read_access: docs/analysis/**
    convergence:
      max_iterations: 3
      convergence_rule: stakeholder_approved
      escalation: human_review
    output:
      artifacts: 
        - docs/requirements/PRD.md
        - docs/requirements/user-stories.md
      schema: schemas/prd.json

  phase_3:
    name: Architecture Design
    driver: bmad-architect
    model: claude-opus-4-7
    skills: [bmad-arch-*, stdd-arch-*, arch-api-design-principles]
    constraints:
      write_access: docs/architecture/**
      read_access: ["docs/requirements/**", "src/**"]
    output:
      artifacts:
        - docs/architecture/ADR-NNN-title.md
        - docs/architecture/system-design.md
      schema: schemas/adr.json
    gates:
      validation: validate-architecture.py
      approval_rule: architect_review_required

  phase_4:
    name: Handoff to Implementation
    driver: orchestrator
    skills: [orchestrate-*, general-git-*]
    steps:
      - validate_all_artifacts
      - create_implementation_branch
      - trigger_stdd_workflow
    constraints:
      write_access: .github/workflows/**, scripts/**
```

**Benefits:**
- Unified runtime for both planning and implementation
- Single workflow manifest language
- Consistent validation and gating
- Native support for BMAD convergence patterns

**Tradeoffs:**
- Requires developing `bmad-*` skills
- Heavier upfront investment
- Tighter coupling between planning and execution

---

## Implementation Roadmap

### Phase 1: Foundation (Prerequisite)

**Goal:** Complete harness-workflow-runtime v1 per master plan

**Tasks:**
- ✅ Finalize workflow orchestrator requirements
- ✅ Define mermaid sequence diagram grammar
- 🚧 Implement YAML compiler (diagram → canonical manifest)
- 🚧 Implement runtime hooks (PreToolUse, PostToolUse, phase gates)
- 🚧 Implement `/workflow run|advance|status|reset` commands
- 🚧 Implement `/new-workflow` interview command

**Deliverable:** Working harness-workflow-runtime plugin installed in Claude Code + OpenCode

### Phase 2: BMAD Skill Development

**Goal:** Create BMAD-compatible skills for specification phases

**Tasks:**

1. **bmad-analyst-*** skills
   - `bmad-analyst-problem-framing.md` — Structured problem analysis
   - `bmad-analyst-stakeholder-mapping.md` — Identify decision makers, users, constraints
   - `bmad-analyst-context-gathering.md` — Research existing docs, codebase, APIs

2. **bmad-pm-*** skills
   - `bmad-pm-prd-authoring.md` — Product Requirements Document structure
   - `bmad-pm-user-story-writing.md` — User story format (Job Stories / Gherkin)
   - `bmad-pm-acceptance-criteria.md` — Testable acceptance conditions

3. **bmad-architect-*** skills
   - `bmad-arch-adr-authoring.md` — Architecture Decision Record format
   - `bmad-arch-system-design.md` — Component diagrams, API contracts
   - `bmad-arch-tech-stack-selection.md` — Framework/library choices with rationale

**Deliverable:** ~12 BMAD skills installable via marketplace

### Phase 3: BMAD Planning Workflow

**Goal:** Implement Pattern A (BMAD as specification phase)

**Tasks:**

1. **Author workflow in mermaid:**

```mermaid
sequenceDiagram
    participant Orc as Orchestrator
    participant Ana as BMAD Analyst
    participant PM as BMAD PM
    participant Arch as BMAD Architect
    
    Orc->>Ana: analyze-problem [skills: bmad-analyst-*; writes: docs/analysis/**]
    Ana->>PM: define-requirements [skills: bmad-pm-*; writes: docs/requirements/**; converge: stakeholder_approved, max=3]
    PM->>Arch: design-architecture [skills: bmad-arch-*; writes: docs/architecture/**]
    Arch->>Orc: validate-artifacts [skills: orchestrate-*; writes: none]
```

2. **Compile to `bmad-planning.yaml`**
3. **Define validation schemas** for PRD, ADR, user stories
4. **Create `/bmad-spec` command** that:
   - Prompts for feature description
   - Runs BMAD planning workflow
   - Validates output artifacts
   - Offers to trigger STDD implementation workflow

**Deliverable:** `/bmad-spec <feature>` command functional in Claude Code

### Phase 4: Integration Testing

**Goal:** Dogfood BMAD → STDD pipeline on real feature

**Tasks:**

1. **Select pilot feature** from backlog
2. **Run `/bmad-spec <feature>`** — capture planning artifacts
3. **Review artifacts** — validate PRD, ADR, user stories quality
4. **Run `/stdd-feat`** using BMAD artifacts as inputs
5. **Measure:**
   - Artifact quality (schema compliance, completeness)
   - Handoff friction (manual edits needed)
   - Developer satisfaction (did planning artifacts help?)

**Deliverable:** Case study document + workflow refinements

### Phase 5: Advanced Patterns (Optional)

**Goal:** Implement Pattern B (BMAD as native workflow plugin)

**Tasks:**

1. **Port BMAD workflow to native harness format** (see Pattern B example)
2. **Implement convergence gates** specific to BMAD (stakeholder approval loops)
3. **Integrate with Linear/Jira** for ticket creation from BMAD outputs
4. **Canvas authoring** — expose BMAD workflow in Drawflow GUI (v1.2+)

**Deliverable:** `bmad-planning` workflow plugin installable standalone

---

## Recommended Next Steps

### Immediate (This Week)

1. **Map BMAD phases to harness concepts** — validate alignment in workshop session
2. **Create issue for BMAD integration** — link to this document
3. **Draft first BMAD skill** — `bmad-analyst-problem-framing.md` as proof-of-concept
4. **Test mermaid authoring** — hand-author simple BMAD workflow in sequence diagram

### Near-term (Next Sprint)

1. **Complete harness-workflow-runtime Phase 1 tasks** per master plan
2. **Develop BMAD skill suite** (Phase 2 tasks)
3. **Author BMAD planning workflow** in mermaid (Phase 3)
4. **Smoke-test end-to-end** — BMAD planning → artifact validation → STDD trigger

### Future

1. **Pilot on production feature** (Phase 4)
2. **Gather feedback** from team using BMAD → STDD pipeline
3. **Iterate on artifacts schemas** based on what STDD phases actually need
4. **Consider Pattern B** if team wants tighter integration

---

## References

### BMAD Method Documentation

- [BMAD Method Official Docs](https://docs.bmad-method.org/) — Complete framework documentation
- [BMAD Workflow Map](https://docs.bmad-method.org/reference/workflow-map/) — Visual workflow reference
- [BMAD GitHub Repository](https://github.com/bmad-code-org/BMAD-METHOD) — Open-source method definition
- [What is BMAD Method? - Medium](https://medium.com/@visrow/what-is-bmad-method-a-simple-guide-to-the-future-of-ai-driven-development-412274f91419) — Beginner's guide
- [Architecting a BMAD Workflow System - Gud Prompt](https://gudprompt.com/p/architecting-a-bmad-method-wor-38220433) — Implementation architecture

### Harness Internal Documentation

- [harness-v1-master-plan.md](harness-v1-master-plan.md) — v1 delivery plan
- [WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md](WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md) — Complete feature spec
- [workflow-runtime-mermaid-grammar.md](workflow-runtime-mermaid-grammar.md) — Sequence diagram compiler spec
- [harness-v1-agent-tasks.md](harness-v1-agent-tasks.md) — Subagent execution prompts

### External Standards

- [agentskills.io](https://agentskills.io/) — Open standard for agent skills (Anthropic, Dec 2025)
- [pydantic-ai-skills](https://pypi.org/project/pydantic-ai-skills/) — Reference implementation for SKILL.md validation

---

## Appendix: Key Definitions

**BMAD** — Breakthrough Method for Agile AI-Driven Development. YAML-based workflow framework with specialized planning agents.

**SDD Cycle** — Specification-Driven Development. Your harness's STDD (Structured Test-Driven Development) workflow pattern.

**Workflow Runtime** — `harness-workflow-runtime` plugin. Schema models, resolver, hooks, state management for workflow execution.

**Phase** — One step in a workflow. Has driver agent, skills, constraints, gates, convergence rules.

**Progressive Disclosure** — agentskills.io pattern: advertise skill names at startup, load full SKILL.md on-demand, execute scripts only when invoked.

**Canonical Manifest** — `workflow.yaml` compiled from mermaid/interview/canvas authoring surfaces. Single source of truth for runtime.

**Validation Gate** — Independent check enforced by runtime hooks, not agent self-report. Blocks phase transition on failure.

**Convergence** — Loop termination condition (e.g., `same_findings_twice`, `stakeholder_approved`). Prevents infinite iteration.

---

**Document Status:** Draft for review  
**Next Review:** After Phase 1 completion (harness-workflow-runtime v1)  
**Ownership:** harness-tooling maintainers  
**Related Issues:** (to be created)
