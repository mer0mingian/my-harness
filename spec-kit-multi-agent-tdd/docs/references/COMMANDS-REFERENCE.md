# SpecKit Commands Reference

**Date:** 2026-05-08  
**Purpose:** Comprehensive command reference for SpecKit + extensions workflow

---

## Command Overview by Phase

| Phase | Slash Command | Skills Used | Purpose | Artifacts Generated |
|-------|--------------|-------------|---------|-------------------|
| **1. Discovery** | | | | |
| | `/speckit.specify` | SpecKit native | • Create feature specification with automatic numbering, branch creation, directory structure | `${feature_id}-spec.md` |
| | `/speckit.multi-agent.discover`<br/>*(NEW - Phase 3)* | `general-grill-with-docs` | • Interview user relentlessly via grill-me skill to build shared understanding<br/>• Generate PRD and Technical Constitution | `${feature_id}-prd.md`<br/>`technical-constitution.md` |
| **2. Solution Design** | | | | |
| | `/speckit.multi-agent.solution-design`<br/>*(NEW - Phase 3)* | `arch-mermaid-diagrams`<br/>`arch-c4-architecture`<br/>`arch-smart-docs` | • Compare 3 solution approaches with ADR<br/>• Generate detailed Solution Design with 4 architectural views<br/>• Invoke c4-* agents sequentially (Context→Container→Component→Code) | `${feature_id}-adr.md` (includes C4 Context/Container for each alternative)<br/>`${feature_id}-solution-design.md` (Decomposition, Dependency, Interface, Data Design views) |
| **3. Refinement** | | | | |
| | `/speckit.plan` | SpecKit native | • Analyze specification and generate technical implementation plan | `${feature_id}-plan.md` |
| | `/speckit.tasks` | SpecKit native | • Break down plan and spec into actionable task list | `${feature_id}-tasks.md` |
| | `/speckit.analyze` | SpecKit native | • Analyze spec/plan/tasks for inconsistencies and gaps | Analysis report (inline or separate) |
| | `/speckit.checklist` | SpecKit native | • Create validation checklist ("unit tests for English") | `${feature_id}-checklist.md` |
| | `/speckit.agent-assign.assign` | Agent-Assign ext | • Scan available agents and assign them to tasks in tasks.md | `agent-assignments.yml` |
| | `/speckit.agent-assign.validate` | Agent-Assign ext | • Validate all agent assignments are correct and agents exist | Validation report |
| **4. Implementation** | | | | |
| | `/speckit.multi-agent.test`<br/>*(Phase 2 - DONE)* | `dev-tdd`<br/>`stdd-test-author-constrained` | • Generate failing tests (RED state) for feature<br/>• Validate RED state with failure code detection<br/>• Delegate to @test-specialist agent | `${feature_id}-test-design.md`<br/>Test files in `tests/` |
| | `/speckit.multi-agent.implement`<br/>*(Phase 2 - DONE)* | `dev-tdd`<br/>`stdd-make-constrained-implementation` | • Validate RED state before implementation<br/>• Implement feature to achieve GREEN state<br/>• Run integration checks (ruff, mypy)<br/>• Delegate to @dev-specialist agent | `${feature_id}-impl-notes.md` (optional)<br/>Source code in `src/` |
| | `/speckit.multi-agent.review`<br/>*(Phase 2 - DONE)* | `review-check-correctness`<br/>`review-simplify-complexity` | • Parallel architecture + code review<br/>• Delegate to @arch-specialist + @review-specialist (parallel)<br/>• Conflict resolution (safety wins)<br/>• Review cycles (max 3) | `${feature_id}-arch-review.md`<br/>`${feature_id}-code-review.md` |
| | `/speckit.multi-agent.commit`<br/>*(Phase 2 - DONE)* | `general-verification-before-completion` | • Validate all mandatory artifacts exist<br/>• Validate evidence chain (RED→GREEN proof)<br/>• Generate workflow summary<br/>• Create git commit | `${feature_id}-workflow-summary.md`<br/>Git commit |
| | `/speckit.multi-agent.execute`<br/>*(Phase 2 - DONE)* | Orchestrates all above | • Execute full TDD workflow: test → implement → review → commit<br/>• Halt on gate failures with diagnostics<br/>• Interactive mode available | All artifacts from test/implement/review/commit |
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
/speckit.multi-agent.discover feat-123
```

**Outputs:** Spec + PRD + Technical Constitution

---

### Solution Design Phase
```bash
# Multi-Agent TDD (Phase 3)
/speckit.multi-agent.solution-design feat-123
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
# Full automated workflow
/speckit.multi-agent.execute feat-123

# Or step-by-step
/speckit.multi-agent.test feat-123
/speckit.multi-agent.implement feat-123
/speckit.multi-agent.review feat-123
/speckit.multi-agent.commit feat-123
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
│ /speckit.multi-agent.discover (Phase 3)                        │
│   ├─> feat-123-prd.md                                          │
│   └─> technical-constitution.md                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SOLUTION DESIGN PHASE                         │
├─────────────────────────────────────────────────────────────────┤
│ /speckit.multi-agent.solution-design (Phase 3)                 │
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
│ /speckit.multi-agent.execute (orchestrates all below)          │
│                                                                  │
│ /speckit.multi-agent.test                                      │
│   ├─> feat-123-test-design.md                                  │
│   └─> tests/test_*.py (failing tests - RED)                    │
│                                                                  │
│ /speckit.multi-agent.implement                                 │
│   ├─> feat-123-impl-notes.md (optional)                        │
│   └─> src/*.py (GREEN implementation)                          │
│                                                                  │
│ /speckit.multi-agent.review (parallel)                         │
│   ├─> feat-123-arch-review.md (@arch-specialist)               │
│   └─> feat-123-code-review.md (@review-specialist)             │
│                                                                  │
│ /speckit.multi-agent.commit                                    │
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
| `/speckit.multi-agent.discover` | `<feature-id>` | **Phase 3** | Uses grill-with-docs skill for relentless questioning, generates PRD + Technical Constitution | `${feature_id}-prd.md`<br/>`technical-constitution.md` |
| `/speckit.multi-agent.solution-design` | `<feature-id>` | **Phase 3** | Creates ADR comparing 3 approaches, generates Solution Design with 4 views, invokes c4-* agents | `${feature_id}-adr.md`<br/>`${feature_id}-solution-design.md` |
| `/speckit.multi-agent.test` | `<feature-id>` | ✅ **Done** | Generates failing tests (RED), validates failure codes, delegates to @test-specialist | `${feature_id}-test-design.md`<br/>`tests/test_*.py` |
| `/speckit.multi-agent.implement` | `<feature-id>`<br/>`[--skip-integration]` | ✅ **Done** | Validates RED→GREEN, implements feature, runs integration checks, delegates to @dev-specialist | `${feature_id}-impl-notes.md`<br/>`src/*.py` |
| `/speckit.multi-agent.review` | `<feature-id>`<br/>`[--max-cycles=N]` | ✅ **Done** | Parallel architecture + code review, conflict resolution, review cycles (max 3) | `${feature_id}-arch-review.md`<br/>`${feature_id}-code-review.md` |
| `/speckit.multi-agent.commit` | `<feature-id>` | ✅ **Done** | Validates artifacts + evidence, generates workflow summary, creates git commit | `${feature_id}-workflow-summary.md`<br/>Git commit |
| `/speckit.multi-agent.execute` | `<feature-id>`<br/>`[--mode=auto\|interactive]` | ✅ **Done** | Orchestrates test→implement→review→commit workflow with gate enforcement | All test/implement/review/commit artifacts |

---

## Skill Mapping

| Skill | Used By Commands | Purpose |
|-------|------------------|---------|
| `general-grill-with-docs` | `/speckit.multi-agent.discover` | Domain-aware questioning, updates CONTEXT.md inline |
| `arch-mermaid-diagrams` | `/speckit.multi-agent.solution-design` | Mermaid syntax for C4, sequence, class diagrams |
| `arch-c4-architecture` | `/speckit.multi-agent.solution-design` | C4 model workflow and best practices |
| `arch-smart-docs` | `/speckit.multi-agent.solution-design` | Codebase architecture analysis and pattern recognition |
| `dev-tdd` | `/speckit.multi-agent.test`<br/>`/speckit.multi-agent.implement` | Test-driven development workflow |
| `stdd-test-author-constrained` | `/speckit.multi-agent.test` | Write tests with constraints enforcement |
| `stdd-make-constrained-implementation` | `/speckit.multi-agent.implement` | Implement code with TDD constraints |
| `review-check-correctness` | `/speckit.multi-agent.review` | Architecture review for correctness |
| `review-simplify-complexity` | `/speckit.multi-agent.review` | Code review for simplification |
| `general-verification-before-completion` | `/speckit.multi-agent.commit` | Verify all requirements before claiming done |

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

## Sources

- [GitHub SpecKit Repository](https://github.com/github/spec-kit)
- [SpecKit Documentation](https://github.github.com/spec-kit/quickstart.html)
- [spec-kit-agent-assign Extension](https://github.com/xymelon/spec-kit-agent-assign)
- [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Microsoft: Spec-Driven Development](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
