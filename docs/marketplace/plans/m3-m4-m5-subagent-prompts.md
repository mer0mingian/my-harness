# M3-M5 Subagent Execution Prompts

**Status:** Ready for Execution  
**Created:** 2026-05-08  
**Prerequisites:** M2 complete (agents renamed to matd-*)

---

## M3 — .claude/ Plugin Structure + plugin.json

**Agent:** general-purpose  
**Model:** sonnet  
**Writes files:** Yes — `.claude/` tree, symlinks, `plugin.json`  
**Depends on:** M2 complete  
**Parallel with:** N/A

### Prompt

```
You are creating the Claude Code plugin structure for the MATD (Multi-Agent Test-Driven Development) plugin in /home/minged01/repositories/harness-workplace/harness-tooling/

Reference the spec at: /home/minged01/repositories/harness-workplace/harness-tooling/docs/marketplace/plans/matd-plugin-spec.md

Create this structure:

.claude/
├── agents/                  # Symlinks to .agents/agents/matd-*.md
│   ├── matd-architect.md -> ../../.agents/agents/matd-architect.md
│   ├── matd-critical-thinker.md -> ../../.agents/agents/matd-critical-thinker.md
│   ├── matd-dev.md -> ../../.agents/agents/matd-dev.md
│   ├── matd-qa.md -> ../../.agents/agents/matd-qa.md
│   └── matd-specifier.md -> ../../.agents/agents/matd-specifier.md
│   # NOTE: matd-orchestrator NOT included (OpenCode only)
│   # NOTE: C4 agents NOT included (will be deprecated)
│
├── skills/                  # Symlinks to .agents/skills/* used by MATD agents
│   ├── arch-api-design-principles -> ../../.agents/skills/arch-api-design-principles/
│   ├── arch-architecture-patterns -> ../../.agents/skills/arch-architecture-patterns/
│   ├── arch-c4-architecture -> ../../.agents/skills/arch-c4-architecture/
│   ├── arch-design-system-patterns -> ../../.agents/skills/arch-design-system-patterns/
│   ├── arch-mermaid-diagrams -> ../../.agents/skills/arch-mermaid-diagrams/
│   ├── arch-smart-docs -> ../../.agents/skills/arch-smart-docs/
│   ├── dev-alpine-js-patterns -> ../../.agents/skills/dev-alpine-js-patterns/
│   ├── dev-backend-to-frontend-handoff -> ../../.agents/skills/dev-backend-to-frontend-handoff/
│   ├── dev-database-migration -> ../../.agents/skills/dev-database-migration/
│   ├── dev-databases -> ../../.agents/skills/dev-databases/
│   ├── dev-diagnose -> ../../.agents/skills/dev-diagnose/
│   ├── dev-tdd -> ../../.agents/skills/dev-tdd/
│   ├── general-finishing-a-development-branch -> ../../.agents/skills/general-finishing-a-development-branch/
│   ├── general-git-advanced-workflows -> ../../.agents/skills/general-git-advanced-workflows/
│   ├── general-git-guardrails-claude-code -> ../../.agents/skills/general-git-guardrails-claude-code/
│   ├── general-grill-me -> ../../.agents/skills/general-grill-me/
│   ├── general-grill-with-docs -> ../../.agents/skills/general-grill-with-docs/
│   ├── general-improve-codebase-architecture -> ../../.agents/skills/general-improve-codebase-architecture/
│   ├── general-python-environment -> ../../.agents/skills/general-python-environment/
│   ├── general-rtk-usage -> ../../.agents/skills/general-rtk-usage/
│   ├── general-solid -> ../../.agents/skills/general-solid/
│   ├── general-system-design -> ../../.agents/skills/general-system-design/
│   ├── general-using-git-worktrees -> ../../.agents/skills/general-using-git-worktrees/
│   ├── general-verification-before-completion -> ../../.agents/skills/general-verification-before-completion/
│   ├── orchestrate-dispatching-parallel-agents -> ../../.agents/skills/orchestrate-dispatching-parallel-agents/
│   ├── orchestrate-executing-plans -> ../../.agents/skills/orchestrate-executing-plans/
│   ├── orchestrate-multi-agent-patterns -> ../../.agents/skills/orchestrate-multi-agent-patterns/
│   ├── orchestrate-subagent-driven-development -> ../../.agents/skills/orchestrate-subagent-driven-development/
│   ├── python-async-patterns -> ../../.agents/skills/python-async-patterns/
│   ├── python-code-style -> ../../.agents/skills/python-code-style/
│   ├── python-configuration -> ../../.agents/skills/python-configuration/
│   ├── python-design-patterns -> ../../.agents/skills/python-design-patterns/
│   ├── python-fastapi-templates -> ../../.agents/skills/python-fastapi-templates/
│   ├── python-packaging -> ../../.agents/skills/python-packaging/
│   ├── python-testing-uv-playwright -> ../../.agents/skills/python-testing-uv-playwright/
│   ├── review-check-correctness -> ../../.agents/skills/review-check-correctness/
│   ├── review-differential-review -> ../../.agents/skills/review-differential-review/
│   ├── review-e2e-testing-patterns -> ../../.agents/skills/review-e2e-testing-patterns/
│   ├── review-simplify-complexity -> ../../.agents/skills/review-simplify-complexity/
│   ├── review-systematic-debugging -> ../../.agents/skills/review-systematic-debugging/
│   ├── review-webapp-testing -> ../../.agents/skills/review-webapp-testing/
│   ├── stdd-ask-questions-if-underspecified -> ../../.agents/skills/stdd-ask-questions-if-underspecified/
│   ├── stdd-make-constrained-implementation -> ../../.agents/skills/stdd-make-constrained-implementation/
│   ├── stdd-openspec -> ../../.agents/skills/stdd-openspec/
│   ├── stdd-pm-linear-integration -> ../../.agents/skills/stdd-pm-linear-integration/
│   ├── stdd-product-spec-formats -> ../../.agents/skills/stdd-product-spec-formats/
│   ├── stdd-project-summary -> ../../.agents/skills/stdd-project-summary/
│   ├── stdd-test-author-constrained -> ../../.agents/skills/stdd-test-author-constrained/
│   └── stdd-test-driven-development -> ../../.agents/skills/stdd-test-driven-development/
│
└── .claude-plugin/
    └── plugin.json          # Plugin manifest

Create .claude-plugin/plugin.json with this content:

{
  "name": "matd",
  "version": "1.0.0",
  "description": "Multi-Agent Test-Driven Development workflow for SpecKit. Provides orchestrated TDD workflow with specialized agents for requirements, architecture, QA, and implementation.",
  "author": "Daniel Minges",
  "agents": "agents/",
  "skills": "skills/"
}

Tasks:
1. Create .claude/ directory structure
2. Create symlinks for 5 MATD agents (NOT orchestrator, NOT C4 agents)
3. Create symlinks for all skills listed above
4. Create .claude-plugin/plugin.json with exact content above
5. Use relative symlinks (../../.agents/...)
6. DO NOT commit

Use Bash (ln -s), Write (for plugin.json only). No Read needed for simple symlinks.

Response format:
- Directory structure created
- Agent symlinks: 5 created
- Skill symlinks: X created
- plugin.json: created
- git status output
```

**Validation:** 
- 5 agent symlinks point to correct matd-* files
- All skill symlinks resolve correctly
- plugin.json valid JSON
- `git status` shows only .claude/ as untracked

---

## M4 — Verify OpenCode Compatibility

**Agent:** general-purpose  
**Model:** sonnet  
**Writes files:** No — verification only  
**Depends on:** M2 complete  
**Parallel with:** M3

### Prompt

```
You are verifying OpenCode compatibility for the MATD plugin in /home/minged01/repositories/harness-workplace/harness-tooling/

OpenCode reads agents and skills directly from the flat .agents/ structure. No .opencode/ directory is needed.

Verify:
1. Check that .agents/agents/ is flat (no nested subdirectories)
2. Check that all matd-*.md agents have:
   - `name:` field matching filename (e.g., matd-architect)
   - `permission:` blocks for read/write/edit/bash/skill
3. List all matd-* agents found
4. Confirm no nested agent directories exist

Use Bash (ls, find, grep). No Write needed.

Response format:
✓ .agents/agents/ is flat
✓ Found X matd-* agents
✓ All agents have name: field
✓ All agents have permission: blocks
✓ No nested directories found

OpenCode compatibility: VERIFIED
No changes needed.
```

**Expected result:** Verification passes, no changes needed.

---

## M5 — .gemini/ Scaffolding Only

**Agent:** general-purpose  
**Model:** sonnet  
**Writes files:** Yes — .gemini/ scaffold  
**Depends on:** N/A  
**Parallel with:** M3, M4

### Prompt

```
You are creating minimal Gemini CLI scaffolding in /home/minged01/repositories/harness-workplace/harness-tooling/

Per the spec, Gemini gets scaffolding ONLY (no functional plugin for v1).

Create this structure:

.gemini/
├── extensions/
│   └── matd-research/
│       └── README.md
└── .gitkeep

.gemini/extensions/matd-research/README.md content:

# MATD Research Extension (Planned)

**Status:** Scaffolding only - v2 feature

## Purpose

The MATD (Multi-Agent Test-Driven Development) workflow will support Gemini CLI in v2 for:
- Research-only tasks
- No hooks or state machine enforcement
- Scoped extensions for exploration

## Current State

This directory is a placeholder. Gemini support planned for v2 after dogfooding MATD workflow with Claude Code and OpenCode.

## v1 Workflow Support

For v1, use:
- **Claude Code** - Full MATD workflow with plugin
- **OpenCode** - Full MATD workflow via flat .agents/ structure
- **Gemini** - Not supported (scaffolding only)

---

Tasks:
1. Create .gemini/extensions/matd-research/ directory
2. Write README.md with content above
3. Create .gemini/.gitkeep
4. DO NOT commit

Use Bash (mkdir -p), Write (README.md only).

Response format:
- .gemini/ structure created
- README.md: placeholder written
- git status output
```

**Validation:** 
- .gemini/ directory exists
- README.md explains v2 scope
- .gitkeep preserves empty directory

---

## Execution Order

Run in parallel:
- M3 (Claude Code plugin) - Serial dependency: needs output for commit
- M4 (OpenCode verification) - Independent, can run anytime
- M5 (Gemini scaffolding) - Independent, can run anytime

After all complete:
- Review M3 symlink structure
- Verify M4 passed
- Commit all three together

---

**Ready for subagent dispatch.**
