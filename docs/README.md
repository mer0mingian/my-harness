# Documentation Index — harness-tooling

This is the documentation hub for the **harness-tooling** marketplace repository. For workspace-level context, see the parent `CLAUDE.md` at `/home/minged01/repositories/harness-workplace/CLAUDE.md`.

---

## Quick Navigation

| I want to... | Start here |
|--------------|-----------|
| **Understand v1 scope and delivery plan** | [harness-v1-master-plan.md](#core-planning-documents) |
| **Execute implementation tasks** | [harness-v1-agent-tasks.md](#core-planning-documents) |
| **Build workflow orchestration runtime** | [Workflow Runtime section](#workflow-runtime-documents) |
| **Integrate BMAD methodology** | [integration-bmad-method.md](#integration-strategies) |
| **Understand skill naming decisions** | [decisions-skill-naming-resolution.md](#decisions--resolutions) |
| **Learn from reference implementations** | [marketplace/reference-workflows-ppries/](#reference-implementations) |
| **Deep-dive research topics** | [deep-research/](#research--exploration) |
| **Multi-Agent TDD workflow** | [SpecKit TDD section](#speckit-multi-agent-tdd) |

---

## Document Status Legend

- ✅ **Approved** — Authoritative, implementation should follow
- 🚧 **Draft** — Under review, subject to change
- 📋 **Decision Required** — Blocked pending approval
- 📚 **Reference** — Informational, not prescriptive
- 🗄️ **Archived** — Superseded, kept for historical context

---

## Core Planning Documents

### harness-v1-master-plan.md
**Status:** ✅ Approved  
**Last Updated:** 2026-04-21  
**Purpose:** Comprehensive delivery plan for v1 of the multi-agent-cli harness  
**Audience:** All contributors

**Contents:**
- Two-repo architecture (harness-tooling marketplace + harness-sandbox runtime)
- Execution phases 0-4 with dependency DAG
- Target end state with complete directory tree
- Delegation principles for subagent work
- Rollback strategy

**Supersedes:** `multi-agent-cli-harness-plan.md`, `multi-agent-plugins-marketplace-plan.md`, `multi-container-harness-plan.md` (all in [archive/](archive/))

**Companion:** [harness-v1-agent-tasks.md](marketplace/plans/harness-v1-agent-tasks.md)

---

### harness-v1-agent-tasks.md
**Status:** ✅ Approved  
**Last Updated:** 2026-04-21  
**Purpose:** Copy-pasteable subagent prompts for executing the master plan  
**Audience:** Main thread orchestrator

**Contents:**
- Phase 0 (Research): R1-R4 tasks
- Phase 1 (Sandbox): S1-S5 tasks
- Phase 2 (Marketplace): M1-M6 tasks
- Phase 3 (Docs): D1 task
- Phase 4 (Validation): V1-V2 tasks
- Each task: prompt, model tier, dependencies, deliverables, validation criteria

**Relationship:** Execution companion to [harness-v1-master-plan.md](marketplace/plans/harness-v1-master-plan.md)

---

## Workflow Runtime Documents

### WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md
**Status:** ✅ Approved scope for v1  
**Last Updated:** 2026-04-24  
**Purpose:** Complete feature specification for harness-workflow-runtime plugin  
**Audience:** Runtime implementers

**Contents:**
- Core requirements (licensing, multi-CLI support, workflow definition)
- Per-phase configuration (agents, skills, MCP, permissions, gates)
- Enforcement model (5-layer validation: frontmatter → pydantic → resolver → hooks → container)
- Schema validation via pydantic-ai-skills
- Two-tier plugin architecture (runtime vs. workflow plugins)
- Authoring UX (Tier 1: mermaid, Tier 2: interview, Tier 3: GUI canvas)
- Anti-patterns (what NOT to build)
- Concrete TDD orchestration example

**Companion:** [harness-workflow-runtime-plan.md](marketplace/plans/harness-workflow-runtime-plan.md), [workflow-runtime-mermaid-grammar.md](#workflow-runtime-mermaid-grammarmd)

---

### harness-workflow-runtime-plan.md
**Status:** 🚧 Draft, awaiting Phase R approval  
**Created:** 2026-04-23  
**Purpose:** Implementation plan with C4 architecture for workflow-runtime plugin  
**Audience:** Implementers

**Contents:**
- C4 diagrams (Context, Container, Component, Code views)
- 9 implementation phases (R through 9) with effort estimates
- Deliverable file inventory
- Risk mitigation table
- Acceptance criteria for v1 complete
- Rollout strategy
- Key decisions resolved 2026-04-24

**Parent:** [harness-v1-master-plan.md](marketplace/plans/harness-v1-master-plan.md)  
**Companion:** [WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md](#workflow_orchestrator_requirementsmd)

---

### workflow-runtime-mermaid-grammar.md
**Status:** ✅ Specification for Tier 1 authoring  
**Created:** 2026-04-23 (Phase R deliverable)  
**Purpose:** Defines supported mermaid sequenceDiagram subset for workflow authoring  
**Audience:** Workflow authors, compiler implementers

**Contents:**
- Accepted constructs: `participant`, `->>/-->` messages, `par` blocks, `loop` blocks, `note over`
- Bracket-metadata convention `[key: value; key: value]` for inline phase config
- Deferred/rejected constructs with rationale
- Worked TDD workflow example (11-phase)
- BNF grammar reference
- Round-trip lossy fields report

**Companion:** [WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md](#workflow_orchestrator_requirementsmd) §18 Tier 1

---

### research-workflow-runtime-baseline.md
**Status:** 📚 Phase R research output  
**Created:** 2026-04-23  
**Purpose:** Baseline findings from Phase R research  
**Audience:** Phase 0+ implementers

**Contents:**
- D1: Frontmatter inventory (agents, skills, commands)
- D2: Python 3.13 verification (✅ present in base image)
- D3: Hook API surfaces (Claude Code, OpenCode)
- Outlier summary (19 name/directory mismatches, schema variants)
- agentskills.io naming compliance audit

**Note:** Originally in `notes/` subdirectory; promoted to root as formal research deliverable.

---

## Integration Strategies

### integration-bmad-method.md
**Status:** 📋 Planning  
**Created:** 2026-04-26  
**Purpose:** Strategy for integrating BMAD (Breakthrough Method for Agile AI-Driven Development) with harness workflows  
**Audience:** Planning/architecture team

**Contents:**
- BMAD methodology overview (4 phases: Analysis → PM → Architecture → Implementation)
- Alignment matrix: BMAD concepts ↔ harness implementation
- Two integration patterns:
  - **Pattern A (Recommended):** BMAD as specification phase feeding harness implementation
  - **Pattern B:** BMAD workflow as native harness plugin
- Implementation roadmap (Phases 1-5)
- bmad-planning.yaml example
- References to BMAD documentation and internal docs

**Dependencies:** Requires [harness-workflow-runtime](#workflow-runtime-documents) v1 complete (Phase 1 prerequisite)

---

## Decisions & Resolutions

### decisions-skill-naming-resolution.md
**Status:** 📋 Decision Required  
**Created:** 2026-04-26  
**Blocking:** Phase 3+ of workflow runtime implementation  
**Purpose:** Recommendation for resolving directory/frontmatter name mismatches  
**Audience:** Decision makers

**Contents:**
- Challenge: 19 skills have directory name (`review-differential-review/`) ≠ frontmatter name (`differential-review`)
- Root cause: agentskills.io spec keys on frontmatter `name:`, resolver follows spec
- Three options analyzed:
  - **Option A (Recommended):** Rename frontmatter to include prefix
  - **Option B:** Violate spec, key on directory
  - **Option C:** Dual-key catalog (support both)
- Quality implications, spec compliance analysis
- Implementation plan (4 phases, ~30 min total)
- Long-term quality gates

**Decision:** Approve Option A or request alternative

---

## Reference Implementations

### marketplace/reference-workflows-ppries/
**Status:** 📚 Reference implementation by ppries  
**Purpose:** Working multi-agent workflow example for OpenCode  
**Audience:** Workflow authors, anyone learning the patterns

**Key Files:**
- `README.md` — Complete workflow description
- `multi-agent-workflow.md` — Core architecture
- `agents-system-prompt.md` — Agent behavior definitions
- Agent definitions: `check.md`, `simplify.md`, `test.md`, `make.md`, `pm.md`, `review.md`, `source.md`, `workflow.md`
- `opencode-config.example.json` — Configuration template

**Patterns Demonstrated:**
- Fire-and-forget autonomous orchestration
- Constrained tool access per agent role
- TDD integration with failure classification
- Parallel review cycles with convergence detection
- Linear CLI integration
- Standalone agent usage

**Note:** Directory renamed from `reference_workflow by ppries/` to `reference-workflows-ppries/` for consistency.

---

## Research & Exploration

### deep-research/
**Purpose:** In-depth research documents on architecture patterns and methodologies  
**Status:** 📚 Informational reference material

**Documents:**

#### bmad-c4-relationship.md
**Purpose:** Explores relationship between BMAD methodology and C4 architecture modeling  
**Note:** Renamed from `BMAD <-> C4.md` for filename consistency

#### operational-architectures.md
**Purpose:** Research on operational architecture patterns

#### scaling-software-teams.md
**Purpose:** Research on team scaling strategies

#### workflows-via-command-chaining.md
**Purpose:** Exploration of workflow orchestration through command chaining patterns

**Audience:** Architects, researchers, anyone exploring advanced patterns  
**Note:** These are exploration documents, not implementation specifications

---

## SpecKit Multi-Agent TDD

Active planning documents for the Multi-Agent TDD Workflow implementation, located in `speckit-tdd/plans/`.

| Document | Purpose |
|----------|---------|
| [ROADMAP-Multi-Agent-TDD.md](speckit-tdd/plans/ROADMAP-Multi-Agent-TDD.md) | 12-slice roadmap with dependency graph and effort estimates |
| [PLAN-Multi-Agent-TDD-Implementation.md](speckit-tdd/plans/PLAN-Multi-Agent-TDD-Implementation.md) | Vertical slice implementation plan |
| [TASK-LIST-Multi-Agent-TDD.md](speckit-tdd/plans/TASK-LIST-Multi-Agent-TDD.md) | Granular task breakdown (66 tasks) |
| [CONSTITUTION-Multi-Agent-TDD.md](speckit-tdd/plans/CONSTITUTION-Multi-Agent-TDD.md) | Constitutional principles and non-bypassable gates |
| [ARTIFACT-SUMMARY.md](speckit-tdd/plans/ARTIFACT-SUMMARY.md) | Artifact details and configuration |
| [PRD-Multi-Agent-TDD-Workflow.md](speckit-tdd/plans/PRD-Multi-Agent-TDD-Workflow.md) | Product requirements |

---

## Archive

### archive/
**Purpose:** Deprecated planning documents kept for historical context  
**Status:** 🗄️ Archived — DO NOT USE for new work

**Contents:**
- Plans superseded by [harness-v1-master-plan.md](marketplace/plans/harness-v1-master-plan.md)
- Each archived file has a deprecation banner linking to current authoritative docs

---

## Document Maintenance

### When to Update This Index

- New document added to docs/
- Document status changes (draft → approved)
- Document superseded or archived
- Significant reorganization

### Contribution Guidelines

1. **Check this index first** before creating a new doc — avoid duplication
2. **Update the index** when adding/moving/archiving documents
3. **Add status metadata** to document frontmatter (Status, Last Updated, Purpose)
4. **Link related documents** using relative paths
5. **Archive don't delete** — move superseded docs to archive/ with deprecation banner

---

## Cross-Repository Documents

These live in the parent workspace or sibling repo:

| Document | Location | Purpose |
|----------|----------|---------|
| Workspace CLAUDE.md | `/home/minged01/repositories/harness-workplace/CLAUDE.md` | Parent workspace instructions |
| harness-sandbox docs | `../harness-sandbox/docs/` | Runtime stack documentation |
| Session memory | `~/.claude/projects/.../MEMORY.md` | Ephemeral session context |

---

**Last Updated:** 2026-04-26  
**Maintainer:** harness-tooling team  
**Feedback:** Open an issue or update via PR
