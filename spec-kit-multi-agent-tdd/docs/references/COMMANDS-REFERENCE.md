# SpecKit Commands Reference

**Date:** 2026-05-08  
**Purpose:** Comprehensive command reference for SpecKit + extensions workflow

---

## Command Overview by Phase

| Phase | Slash Command | Skills Used | Purpose | Artifacts Generated |
|-------|--------------|-------------|---------|-------------------|
| **0. Product-Level** | | | | |
| | `/speckit.matd.specify-product-brief`<br/>*(NEW - Phase 3)* | `general-grill-me` | • Interview user to elicit product vision<br/>• Generate product brief for NEW products | `product-brief.md` |
| | `/speckit.matd.specify-adr`<br/>*(NEW - Phase 3)* | `general-grill-me`<br/>`arch-mermaid-diagrams` | • Interview user about architectural decision<br/>• Generate standalone ADR with decision diagram | `adr-NNN-{slug}.md` |
| **1. Discovery** | | | | |
| | `/speckit.specify` | SpecKit native | • Create feature specification with automatic numbering, branch creation, directory structure | `${feature_id}-spec.md` |
| **2. Solution Design** | | | | |
| | `/speckit.matd.specify-solution-design`<br/>*(NEW - Phase 3)* | `arch-mermaid-diagrams`<br/>`arch-c4-architecture`<br/>`arch-smart-docs` | • Compare 3 solution approaches with ADR<br/>• Generate detailed Solution Design with 4 architectural views<br/>• Invoke c4-* agents sequentially (Context→Container→Component→Code) | `${feature_id}-adr.md` (includes C4 Context/Container for each alternative)<br/>`${feature_id}-solution-design.md` (Decomposition, Dependency, Interface, Data Design views) |
| **3. Refinement** | | | | |
| | `/speckit.plan` | SpecKit native | • Analyze specification and generate technical implementation plan | `${feature_id}-plan.md` |
| | `/speckit.tasks` | SpecKit native | • Break down plan and spec into actionable task list | `${feature_id}-tasks.md` |
| | `/speckit.analyze` | SpecKit native | • Analyze spec/plan/tasks for inconsistencies and gaps | Analysis report (inline or separate) |
| | `/speckit.checklist` | SpecKit native | • Create validation checklist ("unit tests for English") | `${feature_id}-checklist.md` |
| | `/speckit.agent-assign.assign` | Agent-Assign ext | • Scan available agents and assign them to tasks in tasks.md | `agent-assignments.yml` |
| | `/speckit.agent-assign.validate` | Agent-Assign ext | • Validate all agent assignments are correct and agents exist | Validation report |
| **4. Implementation** | | | | |
| | `/speckit.matd.test`<br/>*(Phase 2 - DONE)* | `dev-tdd`<br/>`stdd-test-author-constrained` | • Generate failing tests (RED state) for feature<br/>• Validate RED state with failure code detection<br/>• Delegate to matd-qa agent | `${feature_id}-test-design.md`<br/>Test files in `tests/` |
| | `/speckit.matd.implement`<br/>*(Phase 2 - DONE)* | `dev-tdd`<br/>`stdd-make-constrained-implementation` | • Validate RED state before implementation<br/>• Implement feature to achieve GREEN state<br/>• Integration checks via hooks (ruff, mypy)<br/>• Delegate to matd-dev agent | `${feature_id}-impl-notes.md` (optional)<br/>Source code in `src/` |
| | `/speckit.matd.review`<br/>*(Phase 2 - DONE)* | `review-check-correctness`<br/>`review-simplify-complexity` | • Parallel architecture + code review<br/>• Delegate to check (architect) + simplify (code review) agents in parallel<br/>• Conflict resolution (safety wins)<br/>• Review cycles (max 3) | `${feature_id}-arch-review.md`<br/>`${feature_id}-code-review.md` |
| | `/speckit.matd.commit`<br/>*(Phase 2 - DONE)* | `general-verification-before-completion` | • Validate all mandatory artifacts exist<br/>• Validate evidence chain (RED→GREEN proof)<br/>• Generate workflow summary<br/>• Create git commit | `${feature_id}-workflow-summary.md`<br/>Git commit |
| | `speckit workflow run workflows/matd-tdd.yml` | Orchestrates all above | • Execute full TDD workflow: test → implement → review → commit<br/>• Halt on gate failures with diagnostics<br/>• Interactive mode available via `--mode interactive` | All artifacts from test/implement/review/commit |
| | `/speckit.implement` | SpecKit native | • Execute implementation based on plan/tasks/spec artifacts | Source code changes |
| | `/speckit.agent-assign.execute` | Agent-Assign ext | • Execute tasks by spawning assigned agent for each task | Source code, tests, docs per task |

---

## Phase Workflow Sequences

### Discovery Phase
```bash
# Standard SpecKit workflow
/speckit.specify feat-123

# Enhanced with Multi-Agent TDD (Phase 3)
/speckit.specify feat-123
/speckit.matd.specify-product-brief feat-123
```

**Outputs:** Spec + Technical Constitution

---

### Solution Design Phase
```bash
# Multi-Agent TDD (Phase 3)
/speckit.matd.specify-solution-design feat-123
```

**Outputs:** ADR (compares 3 approaches) + Solution Design (4 architectural views)

---

### Refinement Phase
```bash
# SpecKit native planning
/speckit.plan feat-123
/speckit.tasks feat-123
/speckit.analyze feat-123
/speckit.checklist feat-123

# Agent assignment (optional, if using agent-assign extension)
/speckit.agent-assign.assign feat-123
/speckit.agent-assign.validate feat-123
```

**Outputs:** Plan + Tasks + Analysis + Checklist + Agent Assignments

---

### Implementation Phase

**Option A: Multi-Agent TDD Workflow (Recommended)**
```bash
# Full automated workflow via workflow runtime
speckit workflow run workflows/matd-tdd.yml --feature-id feat-123

# Or step-by-step
/speckit.matd.test feat-123
/speckit.matd.implement feat-123
/speckit.matd.review feat-123
/speckit.matd.commit feat-123
```

**Option B: Agent-Assign Workflow**
```bash
/speckit.agent-assign.execute feat-123
```

**Option C: Standard SpecKit**
```bash
/speckit.implement feat-123
```

**Outputs:** Tests + Implementation + Reviews + Workflow Summary + Commit

---

## Artifact Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      DISCOVERY PHASE                            │
├─────────────────────────────────────────────────────────────────┤
│ /speckit.specify                                                │
│   └─> feat-123-spec.md                                         │
│                                                                  │
│ /speckit.matd.specify-product-brief (Phase 3)                        │
│   ├─> feat-123-spec.md                                         │
│   └─> technical-constitution.md                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SOLUTION DESIGN PHASE                         │
├─────────────────────────────────────────────────────────────────┤
│ /speckit.matd.specify-solution-design (Phase 3)                 │
│   ├─> feat-123-adr.md                                          │
│   │    (3 alternatives with C4 Context/Container each)          │
│   └─> feat-123-solution-design.md                              │
│        ├─ Decomposition View (C4: Context/Container/Comp/Code) │
│        ├─ Dependency View (coupling, graphs)                    │
│        ├─ Interface View (API contracts, events)                │
│        └─ Data Design View (ERD, schemas, data flow)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     REFINEMENT PHASE                            │
├─────────────────────────────────────────────────────────────────┤
│ /speckit.plan → feat-123-plan.md                               │
│ /speckit.tasks → feat-123-tasks.md                             │
│ /speckit.analyze → Analysis report                             │
│ /speckit.checklist → feat-123-checklist.md                     │
│ /speckit.agent-assign.assign → agent-assignments.yml           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   IMPLEMENTATION PHASE                          │
├─────────────────────────────────────────────────────────────────┤
│ speckit workflow run workflows/matd-tdd.yml (orchestrates all)  │
│                                                                  │
│ /speckit.matd.test                                      │
│   ├─> feat-123-test-design.md                                  │
│   └─> tests/test_*.py (failing tests - RED)                    │
│                                                                  │
│ /speckit.matd.implement                                 │
│   ├─> feat-123-impl-notes.md (optional)                        │
│   └─> src/*.py (GREEN implementation)                          │
│                                                                  │
│ /speckit.matd.review (parallel)                         │
│   ├─> feat-123-arch-review.md (@arch-specialist)               │
│   └─> feat-123-code-review.md (@review-specialist)             │
│                                                                  │
│ /speckit.matd.commit                                    │
│   ├─> feat-123-workflow-summary.md                             │
│   └─> Git commit (all artifacts + code)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Command Details

### SpecKit Native Commands

**Source:** [GitHub SpecKit](https://github.com/github/spec-kit)

| Command | Arguments | Description | Artifacts |
|---------|-----------|-------------|-----------|
| `/speckit.specify` | `<feature-description>` | Creates structured specification with automatic feature numbering, branch creation, directory structure | `${feature_id}-spec.md` |
| `/speckit.plan` | `<feature-id>` | Analyzes spec and generates technical implementation plan | `${feature_id}-plan.md` |
| `/speckit.tasks` | `<feature-id>` | Breaks down plan/spec into actionable task list | `${feature_id}-tasks.md` |
| `/speckit.analyze` | `<feature-id>` | Analyzes spec/plan/tasks for inconsistencies and gaps | Analysis report |
| `/speckit.checklist` | `<feature-id>` | Creates validation checklist for specification | `${feature_id}-checklist.md` |
| `/speckit.implement` | `<feature-id>` | Executes implementation based on artifacts | Source code |

### Agent-Assign Extension Commands

**Source:** [spec-kit-agent-assign](https://github.com/xymelon/spec-kit-agent-assign)

| Command | Arguments | Description | Artifacts |
|---------|-----------|-------------|-----------|
| `/speckit.agent-assign.assign` | `<feature-id>` | Scans available agents (.claude/agents/, ~/.claude/agents/) and assigns to tasks | `agent-assignments.yml` |
| `/speckit.agent-assign.validate` | `<feature-id>` | Validates assignments are correct and agents exist | Validation report |
| `/speckit.agent-assign.execute` | `<feature-id>` | Spawns assigned agent for each task execution | Per-task artifacts |

### Multi-Agent TDD Extension Commands (Phase 2-3)

**Source:** This project (`spec-kit-multi-agent-tdd`)

| Command | Arguments | Status | Description | Artifacts |
|---------|-----------|--------|-------------|-----------|
| `/speckit.matd.specify-product-brief` | `[product-name]` | **Phase 3** | Uses grill-me skill for product-level discovery, generates product brief | `product-brief.md` |
| `/speckit.matd.specify-adr` | `[decision-title]` | **Phase 3** | Uses grill-me skill for ADR creation, generates standalone ADR with decision diagram | `adr-NNN-{slug}.md` |
| `/speckit.matd.specify-product-brief` | `<feature-id>` | **Phase 3** | Uses grill-with-docs skill for relentless questioning, generates spec + Technical Constitution | `${feature_id}-spec.md`<br/>`technical-constitution.md` |
| `/speckit.matd.specify-solution-design` | `<feature-id>` | **Phase 3** | Creates ADR comparing 3 approaches, generates Solution Design with 4 views, invokes c4-* agents | `${feature_id}-adr.md`<br/>`${feature_id}-solution-design.md` |
| `/speckit.matd.test` | `<feature-id>` | ✅ **Done** | Generates failing tests (RED), validates failure codes, delegates to @test-specialist | `${feature_id}-test-design.md`<br/>`tests/test_*.py` |
| `/speckit.matd.implement` | `<feature-id>`<br/>`[--skip-integration]` | ✅ **Done** | Validates RED→GREEN, implements feature, runs integration checks, delegates to @dev-specialist | `${feature_id}-impl-notes.md`<br/>`src/*.py` |
| `/speckit.matd.review` | `<feature-id>`<br/>`[--max-cycles=N]` | ✅ **Done** | Parallel architecture + code review, conflict resolution, review cycles (max 3) | `${feature_id}-arch-review.md`<br/>`${feature_id}-code-review.md` |
| `/speckit.matd.commit` | `<feature-id>` | ✅ **Done** | Validates artifacts + evidence, generates workflow summary, creates git commit | `${feature_id}-workflow-summary.md`<br/>Git commit |
| `speckit workflow run workflows/matd-tdd.yml` | `--feature-id <id>`<br/>`[--mode interactive]` | ✅ **Done** | Orchestrates test→implement→review→commit workflow with gate enforcement via workflow runtime | All test/implement/review/commit artifacts |

---

## Skill Mapping

| Skill | Used By Commands | Purpose |
|-------|------------------|---------|
| `general-grill-me` | `/speckit.matd.specify-product-brief`<br/>`/speckit.matd.specify-adr` | Relentless questioning for shared understanding |
| `general-grill-with-docs` | `/speckit.matd.specify-product-brief` | Domain-aware questioning, updates CONTEXT.md inline |
| `arch-mermaid-diagrams` | `/speckit.matd.specify-solution-design` | Mermaid syntax for C4, sequence, class diagrams |
| `arch-c4-architecture` | `/speckit.matd.specify-solution-design` | C4 model workflow and best practices |
| `arch-smart-docs` | `/speckit.matd.specify-solution-design` | Codebase architecture analysis and pattern recognition |
| `dev-tdd` | `/speckit.matd.test`<br/>`/speckit.matd.implement` | Test-driven development workflow |
| `stdd-test-author-constrained` | `/speckit.matd.test` | Write tests with constraints enforcement |
| `stdd-make-constrained-implementation` | `/speckit.matd.implement` | Implement code with TDD constraints |
| `review-check-correctness` | `/speckit.matd.review` | Architecture review for correctness |
| `review-simplify-complexity` | `/speckit.matd.review` | Code review for simplification |
| `general-verification-before-completion` | `/speckit.matd.commit` | Verify all requirements before claiming done |

---

## Configuration

Commands use configuration from `.specify/harness-tdd-config.yml`:

```yaml
agents:
  test_agent: "test-specialist"
  implementation_agent: "dev-specialist"
  arch_reviewer: "arch-specialist"
  code_reviewer: "review-specialist"

artifacts:
  root: "docs/features"
  types:
    spec: "spec"
    prd: "prd"
    adr: "adr"
    solution_design: "solution-design"
    test_design: "test-design"
    impl_notes: "impl-notes"
    arch_review: "arch-review"
    code_review: "code-review"
    workflow_summary: "workflow-summary"

gates:
  default_mode: "auto"
  max_review_cycles: 3
  convergence_detection: true

planning:
  skill: "grill-me"
  interactive_by_default: true
```

---

## Complete Command Mapping (Agent Assignments & Outputs)

This table shows the complete mapping of MATD commands to their assigned agents, skills, and output locations.

| Command | Agent | Primary Skills | Output Location | Purpose |
|---------|-------|---------------|-----------------|---------|
| `/speckit.matd.specify-product-brief` | matd-specifier | general-grill-me, stdd-project-summary | `docs/product-brief.md` | Product-level vision and context for new products |
| `/speckit.matd.specify-adr` | matd-architect | general-grill-me, arch-mermaid-diagrams | `docs/architecture/decisions/adr-NNN-{slug}.md` | Architecture decision records with diagrams |
| `/speckit.matd.specify-solution-design` | matd-architect | arch-c4-architecture, arch-mermaid-diagrams, arch-smart-docs | `openspec/changes/<id>/design.md` + C4 diagrams | Technical design with 4 architectural views |
| `/speckit.matd.test` | matd-qa | dev-tdd, stdd-test-author-constrained | `tests/*.py`, `${feature_id}-test-design.md` | RED state - failing tests with design doc |
| `/speckit.matd.implement` | matd-dev | dev-tdd, stdd-make-constrained-implementation | `src/*.py`, `${feature_id}-impl-notes.md` | GREEN state - implementation to pass tests |
| `/speckit.matd.review` | matd-architect, matd-review | review-check-correctness, review-simplify-complexity | `${feature_id}-arch-review.md`, `${feature_id}-code-review.md` | Parallel architecture and code review |
| `/speckit.matd.commit` | matd-orchestrator | general-verification-before-completion | `${feature_id}-workflow-summary.md`, git commit | Evidence validation and workflow summary |
| `speckit workflow run workflows/matd-tdd.yml` | matd-orchestrator | Orchestrates test/implement/review/commit | All artifacts from sub-commands | Full TDD workflow orchestration via workflow runtime |

### Notes:
- **Product-brief is optional**: Specs can exist without a product-brief
- **Spec integration**: New specs optionally enhance/update existing product-brief
- **Agent specialization**: Each MATD agent has specific skills aligned with their role
- **Output paths**: Configurable via `.specify/harness-tdd-config.yml`

---

## Sources

- [GitHub SpecKit Repository](https://github.com/github/spec-kit)
- [SpecKit Documentation](https://github.github.com/spec-kit/quickstart.html)
- [spec-kit-agent-assign Extension](https://github.com/xymelon/spec-kit-agent-assign)
- [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Microsoft: Spec-Driven Development](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
