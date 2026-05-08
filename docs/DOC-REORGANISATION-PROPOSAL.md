# Documentation Reorganisation Proposal

**Date:** 2026-05-08  
**Scope:** `docs/` and `spec-kit-multi-agent-tdd/docs/`  
**Purpose:** Separate SpecKit-extension docs from Harness marketplace docs so each concern has a clear home.

**Note (2026-05-08):** This proposal covers `.md` documentation only. The 6 structural markdown test files (`test_command_commit.py`, `test_command_discover.py`, `test_command_implement.py`, `test_command_review.py`, `test_command_test.py`, `test_templates.py`) under `spec-kit-multi-agent-tdd/tests/unit/` were removed in commit `04d0fa2` as part of the test-strategy decision documented in `docs/plans/PHASE3-IMPLEMENTATION-PLAN.md` and `docs/plans/ROADMAP-Multi-Agent-TDD.md`. They never appeared in the inventory below (which lists docs, not test files), so no inventory or move-list changes are required here. The remaining unit tests in `spec-kit-multi-agent-tdd/tests/unit/` are Python logic tests and stay in place.

---

## 1. Current Inventory

### Root-level `.md` files

| Path | Classification | Description |
|------|---------------|-------------|
| `README.md` | marketplace | Top-level repo README — marketplace overview, skill library, quick-start |

### `docs/` — top-level files

| Path | Classification | Description |
|------|---------------|-------------|
| `docs/README.md` | marketplace | Documentation hub index — navigation table covering harness-v1 plans, workflow runtime, reference workflows |
| `docs/PRD.md` | marketplace | Short PRD for the harness-tooling marketplace (not the TDD workflow) |
| `docs/Solution Design.md` | marketplace | Part 1 solution design for the marketplace/harness architecture |
| `docs/workflow-runtime-mermaid-grammar.md` | marketplace | Mermaid sequenceDiagram grammar spec for the harness-workflow-runtime Phase R deliverable |

### `docs/plans/`

| Path | Classification | Description |
|------|---------------|-------------|
| `docs/plans/harness-v1-master-plan.md` | marketplace | Comprehensive delivery plan for Harness v1 (two-repo architecture, phases 0-4) |
| `docs/plans/harness-v1-agent-tasks.md` | marketplace | Copy-pasteable subagent prompts to execute the harness-v1 master plan |
| `docs/plans/harness-workflow-runtime-plan.md` | marketplace | Implementation plan + C4 architecture for the harness-workflow-runtime plugin |
| `docs/plans/ROADMAP-Multi-Agent-TDD.md` | speckit-extension | Roadmap for the Multi-Agent TDD workflow (slices, phases, dependencies) |
| `docs/plans/PLAN-Multi-Agent-TDD-Implementation.md` | speckit-extension | Implementation plan (vertical slices) for the SpecKit multi-agent TDD extension |
| `docs/plans/TASK-LIST-Multi-Agent-TDD.md` | speckit-extension | Granular slice-level task list with acceptance criteria for the TDD extension |
| `docs/plans/PRD-Multi-Agent-TDD-Workflow.md` | speckit-extension | Product requirements document for the multi-agent TDD workflow extension |
| `docs/plans/CONSTITUTION-Multi-Agent-TDD.md` | speckit-extension | Non-bypassable constitutional principles governing the TDD workflow agents |
| `docs/plans/ARTIFACT-SUMMARY.md` | speckit-extension | Artifact templates and configuration summary for the TDD workflow |
| `docs/plans/GAP-FIX-RECOMMENDATIONS.md` | speckit-extension | Gap analysis and fix recommendations for Phase 2 of the TDD workflow |
| `docs/plans/PHASE2-UPDATED-Execute-Command.md` | speckit-extension | Updated Phase 2 plan for the orchestrated execute command (Slice 3.5 details) |
| `docs/plans/PHASE3-IMPLEMENTATION-PLAN.md` | speckit-extension | Phase 3 implementation plan (discovery and solution design phase) |
| `docs/plans/SLICE8-CONFIG-PLAN.md` | speckit-extension | Phase 2 Slice 8 config feature implementation plan |

### `docs/notes/`

| Path | Classification | Description |
|------|---------------|-------------|
| `docs/notes/AGENTS.md` | marketplace | AGENTS.md for the notes environment — litho.toml, pyproject.toml config notes |
| `docs/notes/CLAUDE.md` | marketplace | CLAUDE.md for the marketplace context — links to master plan, agent tasks |

### `docs/deep-research/`

| Path | Classification | Description |
|------|---------------|-------------|
| `docs/deep-research/operational-architectures.md` | shared | Research on operational architectures for spec-driven development with AI teams (references CONSTITUTION / PLAN.md concepts applicable to both) |
| `docs/deep-research/scaling-software-teams.md` | marketplace | Research on scaling software teams — general harness/team context |
| `docs/deep-research/workflows-via-command-chaining.md` | shared | Technical report on multi-agent workflow orchestration via command chaining (covers both harness runtime and SpecKit workflow) |

### `docs/reference-workflows-ppries/`

| Path | Classification | Description |
|------|---------------|-------------|
| `docs/reference-workflows-ppries/README.md` | marketplace | Index for the PPRIES reference workflow set (OpenCode autonomous multi-agent workflow) |
| `docs/reference-workflows-ppries/agents-system-prompt.md` | marketplace | System prompt sections for the PPRIES multi-agent workflow |
| `docs/reference-workflows-ppries/check.md` | marketplace | PPRIES `check` agent/command reference |
| `docs/reference-workflows-ppries/make.md` | marketplace | PPRIES `make` agent/command reference |
| `docs/reference-workflows-ppries/multi-agent-workflow.md` | marketplace | PPRIES multi-agent workflow summary |
| `docs/reference-workflows-ppries/pm.md` | marketplace | PPRIES `pm` agent/command reference |
| `docs/reference-workflows-ppries/review.md` | marketplace | PPRIES `review` agent/command reference |
| `docs/reference-workflows-ppries/simplify.md` | marketplace | PPRIES `simplify` agent/command reference |
| `docs/reference-workflows-ppries/source.md` | marketplace | PPRIES `source` reference (stub) |
| `docs/reference-workflows-ppries/test.md` | marketplace | PPRIES `test` agent/command reference |
| `docs/reference-workflows-ppries/workflow.md` | marketplace | PPRIES fire-and-forget workflow: plan, test, implement, PR |

### `docs/archive/`

| Path | Classification | Description |
|------|---------------|-------------|
| `docs/archive/WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md` | marketplace | Archived full feature spec for harness-workflow-runtime v1 (superseded by workflow-runtime-plan) |
| `docs/archive/decisions-skill-naming-resolution.md` | marketplace | Archived skill naming convention decision document |
| `docs/archive/integration-bmad-method.md` | marketplace | Archived BMAD integration strategy for the harness workflow runtime |
| `docs/archive/multi-agent-cli-harness-plan.md` | marketplace | Deprecated; superseded by harness-v1-master-plan |
| `docs/archive/multi-agent-plugins-marketplace-plan.md` | marketplace | Deprecated; superseded by harness-v1-master-plan |
| `docs/archive/multi-container-harness-plan.md` | marketplace | Deprecated; superseded by harness-v1-master-plan |
| `docs/archive/research-workflow-runtime-baseline.md` | marketplace | Phase R research baseline for workflow-runtime (Mermaid grammar input) |

### `spec-kit-multi-agent-tdd/docs/`

| Path | Classification | Description |
|------|---------------|-------------|
| `spec-kit-multi-agent-tdd/docs/plans/ARCHITECTURAL-CORRECTION-PLAN.md` | speckit-extension | Plan to migrate Python commands to Markdown-based commands |
| `spec-kit-multi-agent-tdd/docs/plans/PHASE3-GRILLING-QUESTIONS.md` | speckit-extension | Grilling questions for Phase 3 architectural decisions |
| `spec-kit-multi-agent-tdd/docs/references/COMMANDS-REFERENCE.md` | speckit-extension | SpecKit commands reference (spec, design, refine, implement commands) |
| `spec-kit-multi-agent-tdd/docs/references/architecture-recommendations.md` | speckit-extension | Architecture recommendations specific to spec-kit-multi-agent-tdd |
| `spec-kit-multi-agent-tdd/docs/references/phase3-gap-learnings.md` | speckit-extension | Learnings and gaps discovered during Phase 3 |
| `spec-kit-multi-agent-tdd/docs/references/python-reusability-analysis.md` | speckit-extension | Analysis of Python code reusability for architectural correction |
| `spec-kit-multi-agent-tdd/docs/references/reusability-summary.md` | speckit-extension | Summary of Python reusability analysis for architectural correction |
| `spec-kit-multi-agent-tdd/docs/references/external/agentskills-io-standard.md` | speckit-extension | External reference: AgentSkills.io open standard |
| `spec-kit-multi-agent-tdd/docs/references/external/claude-code-hooks-guide.md` | speckit-extension | External reference: Claude Code hooks guide |
| `spec-kit-multi-agent-tdd/docs/references/external/claude-code-skills-official.md` | speckit-extension | External reference: Claude Code skills official documentation |
| `spec-kit-multi-agent-tdd/docs/references/external/commands-vs-skills.md` | speckit-extension | External reference: commands vs skills architecture and relationship |
| `spec-kit-multi-agent-tdd/docs/references/external/spec-kit-agent-assign-analysis.md` | speckit-extension | External reference: spec-kit-agent-assign extension analysis |
| `spec-kit-multi-agent-tdd/docs/references/external/speckit-extension-specs.md` | speckit-extension | External reference: SpecKit extension technical specifications |

**Summary:** 53 docs inventoried — 3 shared, 14 speckit-extension (in `docs/plans/`), 24 marketplace, 12 speckit-extension already correctly placed in `spec-kit-multi-agent-tdd/docs/`.

---

## 2. Proposed Target Structure

The core problem: the 10 `*-Multi-Agent-TDD.*` files and their companions (`ARTIFACT-SUMMARY`, `GAP-FIX-RECOMMENDATIONS`, `PHASE2-*`, `PHASE3-*`, `SLICE8-*`) are SpecKit-extension planning docs sitting in `docs/plans/` alongside the 3 harness-specific plan files. They should live in `docs/speckit-tdd/plans/` so the boundary is immediately visible.

The `docs/README.md` currently only indexes harness docs — it does not reference any of the SpecKit plans. That confirms they drifted into `docs/plans/` without being wired into the index.

```
harness-tooling/
├── README.md                             (stays — marketplace root README)
├── docs/
│   ├── README.md                         (stays — updated to add speckit-tdd section)
│   ├── PRD.md                            (stays — marketplace PRD)
│   ├── Solution Design.md                (stays — marketplace solution design)
│   ├── workflow-runtime-mermaid-grammar.md  (stays — harness runtime grammar spec)
│   │
│   ├── marketplace/                      (NEW — move harness-specific plans here)
│   │   ├── plans/
│   │   │   ├── harness-v1-master-plan.md
│   │   │   ├── harness-v1-agent-tasks.md
│   │   │   └── harness-workflow-runtime-plan.md
│   │   └── reference-workflows-ppries/   (move here from docs/)
│   │       └── *.md (10 files)
│   │
│   ├── speckit-tdd/                      (NEW — all SpecKit multi-agent TDD docs)
│   │   └── plans/
│   │       ├── ROADMAP-Multi-Agent-TDD.md
│   │       ├── PLAN-Multi-Agent-TDD-Implementation.md
│   │       ├── TASK-LIST-Multi-Agent-TDD.md
│   │       ├── PRD-Multi-Agent-TDD-Workflow.md
│   │       ├── CONSTITUTION-Multi-Agent-TDD.md
│   │       ├── ARTIFACT-SUMMARY.md
│   │       ├── GAP-FIX-RECOMMENDATIONS.md
│   │       ├── PHASE2-UPDATED-Execute-Command.md
│   │       ├── PHASE3-IMPLEMENTATION-PLAN.md
│   │       └── SLICE8-CONFIG-PLAN.md
│   │
│   ├── notes/                            (stays — environment config notes)
│   ├── deep-research/                    (stays — research papers; classification is fine)
│   └── archive/                          (stays — all marketplace archive)
│
└── spec-kit-multi-agent-tdd/
    └── docs/                             (stays — all 12 files already correct)
        ├── plans/
        │   ├── ARCHITECTURAL-CORRECTION-PLAN.md
        │   └── PHASE3-GRILLING-QUESTIONS.md
        └── references/
            ├── COMMANDS-REFERENCE.md
            ├── architecture-recommendations.md
            ├── phase3-gap-learnings.md
            ├── python-reusability-analysis.md
            ├── reusability-summary.md
            └── external/
                └── *.md (6 files)
```

**Rationale for the two-level split inside `docs/`:**

- `docs/marketplace/plans/` holds the three harness-v1 plans (runtime, master, tasks). Keeping them one extra level deep is a worthwhile trade-off for clarity — they are already well-indexed in `docs/README.md`.
- `docs/speckit-tdd/plans/` mirrors the naming of `spec-kit-multi-agent-tdd/docs/plans/` to make the relationship obvious. The 10 SpecKit planning files are high-volume (the task list alone is 1,500+ lines) and deserve their own subdirectory.
- `reference-workflows-ppries/` moves into `docs/marketplace/` rather than staying at `docs/` top-level, because it is definitively marketplace content and the top-level `docs/` will be cleaner with only the four root files plus three named subdirectories.
- `docs/notes/`, `docs/deep-research/`, and `docs/archive/` stay under `docs/` — they have mixed or marketplace-only content and their current names are self-explanatory.

---

## 3. Move List

```
MOVE: docs/plans/ROADMAP-Multi-Agent-TDD.md → docs/speckit-tdd/plans/ROADMAP-Multi-Agent-TDD.md
REASON: SpecKit TDD extension planning doc misplaced in the marketplace plans directory.

MOVE: docs/plans/PLAN-Multi-Agent-TDD-Implementation.md → docs/speckit-tdd/plans/PLAN-Multi-Agent-TDD-Implementation.md
REASON: SpecKit TDD extension implementation plan misplaced in the marketplace plans directory.

MOVE: docs/plans/TASK-LIST-Multi-Agent-TDD.md → docs/speckit-tdd/plans/TASK-LIST-Multi-Agent-TDD.md
REASON: SpecKit TDD task list misplaced in the marketplace plans directory.

MOVE: docs/plans/PRD-Multi-Agent-TDD-Workflow.md → docs/speckit-tdd/plans/PRD-Multi-Agent-TDD-Workflow.md
REASON: SpecKit TDD PRD misplaced in the marketplace plans directory.

MOVE: docs/plans/CONSTITUTION-Multi-Agent-TDD.md → docs/speckit-tdd/plans/CONSTITUTION-Multi-Agent-TDD.md
REASON: SpecKit TDD constitution misplaced in the marketplace plans directory.

MOVE: docs/plans/ARTIFACT-SUMMARY.md → docs/speckit-tdd/plans/ARTIFACT-SUMMARY.md
REASON: SpecKit TDD artifact summary misplaced in the marketplace plans directory.

MOVE: docs/plans/GAP-FIX-RECOMMENDATIONS.md → docs/speckit-tdd/plans/GAP-FIX-RECOMMENDATIONS.md
REASON: SpecKit TDD Phase 2 gap analysis misplaced in the marketplace plans directory.

MOVE: docs/plans/PHASE2-UPDATED-Execute-Command.md → docs/speckit-tdd/plans/PHASE2-UPDATED-Execute-Command.md
REASON: SpecKit TDD Phase 2 execution command plan misplaced in the marketplace plans directory.

MOVE: docs/plans/PHASE3-IMPLEMENTATION-PLAN.md → docs/speckit-tdd/plans/PHASE3-IMPLEMENTATION-PLAN.md
REASON: SpecKit TDD Phase 3 plan misplaced in the marketplace plans directory.

MOVE: docs/plans/SLICE8-CONFIG-PLAN.md → docs/speckit-tdd/plans/SLICE8-CONFIG-PLAN.md
REASON: SpecKit TDD Slice 8 config plan misplaced in the marketplace plans directory.

MOVE: docs/plans/harness-v1-master-plan.md → docs/marketplace/plans/harness-v1-master-plan.md
REASON: Harness marketplace planning doc should live under the explicit marketplace subtree.

MOVE: docs/plans/harness-v1-agent-tasks.md → docs/marketplace/plans/harness-v1-agent-tasks.md
REASON: Harness marketplace planning doc should live under the explicit marketplace subtree.

MOVE: docs/plans/harness-workflow-runtime-plan.md → docs/marketplace/plans/harness-workflow-runtime-plan.md
REASON: Harness marketplace planning doc should live under the explicit marketplace subtree.

MOVE: docs/reference-workflows-ppries/ → docs/marketplace/reference-workflows-ppries/
REASON: PPRIES workflow references are exclusively marketplace content; consolidates all marketplace material under one subdirectory.
```

Total: **13 individual file moves + 1 directory move** (10 files inside reference-workflows-ppries).

---

## 4. Reference Fixes Required

### 4a. Links broken by moving the 10 SpecKit files out of `docs/plans/`

The SpecKit plan files contain many same-directory relative links (`[FOO](FOO.md)`). After moving them to `docs/speckit-tdd/plans/`, all those links remain valid **within** that group — they all move together and the relative paths stay the same. The only links that break are the ones pointing **across** the old boundary.

```
FIX: docs/plans/PHASE2-UPDATED-Execute-Command.md — change "../spec-kit-multi-agent-tdd/docs/plans/ARCHITECTURAL-CORRECTION-PLAN.md" to "../../spec-kit-multi-agent-tdd/docs/plans/ARCHITECTURAL-CORRECTION-PLAN.md"
NOTE: After move, this file is at docs/speckit-tdd/plans/PHASE2-UPDATED-Execute-Command.md so the relative depth to spec-kit-multi-agent-tdd/ increases by one level.
```

```
FIX: docs/plans/ROADMAP-Multi-Agent-TDD.md — change "../harness-tooling/docs/PRD-Multi-Agent-TDD-Workflow.md" to "PRD-Multi-Agent-TDD-Workflow.md"
NOTE: This link is already broken (points outside repo). After move, the PRD is in the same directory — use a simple relative link.
```

```
FIX: docs/plans/PLAN-Multi-Agent-TDD-Implementation.md — change "../harness-tooling/docs/PRD-Multi-Agent-TDD-Workflow.md" to "PRD-Multi-Agent-TDD-Workflow.md"
NOTE: Same broken cross-repo link pattern. After move both files are co-located in docs/speckit-tdd/plans/.
```

### 4b. Links broken by moving the 3 harness plan files out of `docs/plans/`

```
FIX: docs/plans/harness-v1-agent-tasks.md (→ docs/marketplace/plans/harness-v1-agent-tasks.md) — change "[../harness-v1-master-plan.md](../harness-v1-master-plan.md)" to "[harness-v1-master-plan.md](harness-v1-master-plan.md)"
NOTE: After move, both files are co-located in docs/marketplace/plans/.
```

```
FIX: docs/plans/harness-workflow-runtime-plan.md (→ docs/marketplace/plans/harness-workflow-runtime-plan.md) — change "[harness-v1-master-plan.md](harness-v1-master-plan.md)" to "[harness-v1-master-plan.md](harness-v1-master-plan.md)"
NOTE: Both files co-located in docs/marketplace/plans/ after move — relative link stays the same. No change needed.
```

### 4c. Links in `docs/archive/` pointing to plans that moved

The archive files link into the old `docs/plans/` location using relative same-directory links (e.g., `[harness-v1-master-plan.md](harness-v1-master-plan.md)`). They were written when all plan files were siblings inside `docs/plans/` (before `plans/` was a subdirectory at all). These need updates.

```
FIX: docs/archive/integration-bmad-method.md — change "[harness-v1-master-plan.md](harness-v1-master-plan.md)" to "[harness-v1-master-plan.md](../marketplace/plans/harness-v1-master-plan.md)"
FIX: docs/archive/integration-bmad-method.md — change "[harness-v1-agent-tasks.md](harness-v1-agent-tasks.md)" to "[harness-v1-agent-tasks.md](../marketplace/plans/harness-v1-agent-tasks.md)"
FIX: docs/archive/integration-bmad-method.md — change "[workflow-runtime-mermaid-grammar.md](workflow-runtime-mermaid-grammar.md)" to "[workflow-runtime-mermaid-grammar.md](../workflow-runtime-mermaid-grammar.md)"
NOTE: workflow-runtime-mermaid-grammar.md stays at docs/ root so the path changes from a sibling to parent-level reference.
```

```
FIX: docs/archive/WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md — change "[harness-workflow-runtime-plan.md](harness-workflow-runtime-plan.md)" to "[harness-workflow-runtime-plan.md](../marketplace/plans/harness-workflow-runtime-plan.md)"
```

```
FIX: docs/archive/multi-agent-cli-harness-plan.md — change "[../harness-v1-master-plan.md](../harness-v1-master-plan.md)" to "[../marketplace/plans/harness-v1-master-plan.md](../marketplace/plans/harness-v1-master-plan.md)"
FIX: docs/archive/multi-agent-cli-harness-plan.md — change "[../harness-v1-agent-tasks.md](../harness-v1-agent-tasks.md)" to "[../marketplace/plans/harness-v1-agent-tasks.md](../marketplace/plans/harness-v1-agent-tasks.md)"
```

```
FIX: docs/archive/multi-agent-plugins-marketplace-plan.md — change "[../harness-v1-master-plan.md](../harness-v1-master-plan.md)" to "[../marketplace/plans/harness-v1-master-plan.md](../marketplace/plans/harness-v1-master-plan.md)"
FIX: docs/archive/multi-agent-plugins-marketplace-plan.md — change "[../harness-v1-agent-tasks.md](../harness-v1-agent-tasks.md)" to "[../marketplace/plans/harness-v1-agent-tasks.md](../marketplace/plans/harness-v1-agent-tasks.md)"
```

```
FIX: docs/archive/multi-container-harness-plan.md — change "[../harness-v1-master-plan.md](../harness-v1-master-plan.md)" to "[../marketplace/plans/harness-v1-master-plan.md](../marketplace/plans/harness-v1-master-plan.md)"
FIX: docs/archive/multi-container-harness-plan.md — change "[../harness-v1-agent-tasks.md](../harness-v1-agent-tasks.md)" to "[../marketplace/plans/harness-v1-agent-tasks.md](../marketplace/plans/harness-v1-agent-tasks.md)"
```

### 4d. Links in `docs/notes/CLAUDE.md` pointing to plan files that moved

```
FIX: docs/notes/CLAUDE.md — change "[docs/harness-v1-master-plan.md](docs/harness-v1-master-plan.md)" to "[docs/marketplace/plans/harness-v1-master-plan.md](../marketplace/plans/harness-v1-master-plan.md)"
FIX: docs/notes/CLAUDE.md — change "[docs/harness-v1-agent-tasks.md](docs/harness-v1-agent-tasks.md)" to "[docs/marketplace/plans/harness-v1-agent-tasks.md](../marketplace/plans/harness-v1-agent-tasks.md)"
NOTE: Current links in CLAUDE.md use paths relative to the repo root so they are already incorrect; the fix should use correct relative paths from docs/notes/.
```

### 4e. `docs/README.md` — index requires updating

The README index will no longer point at valid relative paths for the plan files. These are not simple link fixes — the README will need its `## Core Planning Documents` and `## Workflow Runtime Documents` sections updated to point to the new locations, and a new `## SpecKit Multi-Agent TDD` section added.

```
FIX: docs/README.md — update all plan file links in "Core Planning Documents" from "plans/harness-v1-*.md" to "marketplace/plans/harness-v1-*.md"
FIX: docs/README.md — update workflow runtime links from "plans/harness-workflow-runtime-plan.md" to "marketplace/plans/harness-workflow-runtime-plan.md"
FIX: docs/README.md — update reference-workflows-ppries/ links from "reference-workflows-ppries/" to "marketplace/reference-workflows-ppries/"
FIX: docs/README.md — add new "## SpecKit Multi-Agent TDD" navigation section pointing to "speckit-tdd/plans/"
```

### 4f. `docs/archive/integration-bmad-method.md` — reference to `../README.md`

```
FIX: docs/archive/integration-bmad-method.md — change "[harness-tooling](../README.md)" to "[harness-tooling](../../README.md)"
NOTE: This is already broken — the archive file sits in docs/archive/ so ../README.md resolves to docs/README.md not the repo root README.md. Target should be ../../README.md.
```

---

## 5. Files That Stay In Place

| File | Reason |
|------|--------|
| `README.md` (repo root) | Correct location for repo root marketplace README |
| `docs/README.md` | Central doc index; stays at docs/ root but content needs updating (see fixes) |
| `docs/PRD.md` | Marketplace PRD; four top-level files are a sensible landing zone |
| `docs/Solution Design.md` | Marketplace solution design; same rationale |
| `docs/workflow-runtime-mermaid-grammar.md` | Marketplace runtime grammar spec; same rationale |
| `docs/notes/AGENTS.md` | Environment config notes; unambiguously non-content |
| `docs/notes/CLAUDE.md` | Environment CLAUDE.md; unambiguously non-content |
| `docs/deep-research/operational-architectures.md` | Classified `shared`; research background applicable to both concerns; moving it would be arbitrary |
| `docs/deep-research/scaling-software-teams.md` | General research background; not actionable planning doc |
| `docs/deep-research/workflows-via-command-chaining.md` | Classified `shared`; general reference |
| `docs/archive/*` (all 7 files) | Archive is a graveyard — files should not move out of archive; internal links get fixed in place |
| `spec-kit-multi-agent-tdd/docs/plans/*` (2 files) | Already correctly co-located with the extension code |
| `spec-kit-multi-agent-tdd/docs/references/*` (11 files) | Already correctly co-located with the extension code |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total docs inventoried | 53 |
| Classified marketplace | 36 |
| Classified speckit-extension | 24 (12 already in correct location) |
| Classified shared | 3 |
| Files that move | 23 (13 individual files + 10 files in reference-workflows-ppries directory move) |
| Reference fixes required | 21 distinct link changes across 9 files |
| Files staying in place | 30 |
