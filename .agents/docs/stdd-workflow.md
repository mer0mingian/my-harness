# Daniel's Spec- & Test-Driven Development (STDD) Workflow: Granular Architecture

This document summarizes the refined, multi-agent SDD workflow implementation, utilizing the `subtask2` plugin for deterministic agent chaining.

## Hierarchy & Roles

The workflow is managed by a single user-facing **Orchestrator** that delegates specific phases to highly-scoped subagents.

| Agent | Role | Key Skills | User-Facing? |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | Coordination, PM, Approval Gates | `subagent-driven-development`, `executing-plans`, `daniels-ask-questions-if-underspecified` | **YES** |
| **Spec Agent** | Requirements Engineer | `daniels-openspec`, `daniels-product-spec-formats`, `daniels-project-summary` | NO |
| **Critical Thinking** | Red Team Validator | `daniels-ask-questions-if-underspecified` | NO |
| **Architect Agent** | Solution Designer & C4 | `general-system-design`, `architecture-patterns`, `daniels-openspec`, `smart-docs` | NO |
| **QA Agent** | Test Architect & Auditor | `e2e-testing-patterns`, `webapp-testing`, `general-solid` | NO |
| **Python Dev** | Implementation Engineer (SWE) | `daniels-tdd`, `python-async-patterns`, `fastapi-templates`, `general-solid` | NO |

*Note: All agents possess `general-` base skills (rtk, git, system-design, etc.) to ensure a consistent environment.*

## Workflow Stages & Commands

The workflow uses sequential `return` chains in the command frontmatter to ensure deterministic handoffs between specialists.

### 1. Specification (`/01-specification`)
- **Flow**: Orchestrator -> Spec Agent (Init) -> Spec Agent (Draft) -> Critical Thinking (Audit) -> Spec Agent (Finalize).
- **Artifacts**: `openspec/changes/<slug>/proposal.md`, `specs/requirements.md`.
- **Gate**: User must approve the Feature Spec before proceeding.

### 2. Solution Design (`/02-design`)
- **Flow**: Orchestrator -> Architect Agent (Design) -> C4 Agents (Context/Container/Component) -> Architect Agent (Deepwiki Sync).
- **Artifacts**: `openspec/changes/<slug>/design.md`, `docs/technical/**`, `docs/deepwiki/**`.
- **Gate**: User must approve the Technical Design.

### 3. Technical Refinement (`/03-refine`)
- **Flow**: Orchestrator -> Architect Agent (Draft Plan) -> Critical Thinking (Audit Plan) -> QA Agent (E2E Test Creation) -> Orchestrator (Git/Workspace Setup).
- **Artifacts**: `docs/tasks/<feature>_tasks.md`, `openspec/changes/<slug>/tasks.md`, `tests/e2e/**`.
- **Gate**: User must approve the Delivery Plan and failing test suite.

### 4. Implementation (`/04-implement`)
- **Flow**: Orchestrator -> QA Agent (Verify Tests) -> Python Dev (TDD Implementation Loop) -> QA Agent (Final Review) -> Architect Agent (Merge & PR).
- **Artifacts**: Implementation code, Unit tests, Pull Request.
- **Gate**: Final PR merge by user.

## Master Orchestration
Execute the full sequence with:
```bash
/feat-workflow "Description of the feature"
```

---

## Technical Dependencies

1. **subtask2 Plugin**: Handles the `{as:name}` result capture and `$RESULT[name]` passing between stages. It enables the `return` chain that prevents context pollution.
2. **OpenSpec Framework**: Provides the organizational directory structure (`openspec/changes/`) for artifacts.
3. **Namespaced Skills**:
    - `general-*`: Shared base skills (rtk, git, solid, etc.).
    - `daniels-*`: Workflow-specific logic (openspec, spec-formats, tdd).
