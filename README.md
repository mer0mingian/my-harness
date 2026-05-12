# Harness Tooling - Multi-Agent Development Marketplace

**Skills, agents, commands, and workflow integrations for Claude Code, OpenCode, Gemini CLI, and SpecKit.**

---

## What's Inside

- **70+ Skills** - Reusable expertise in architecture, development, testing, orchestration
- **Multiple Workflow Integrations** - MATD (Multi-Agent Test-Driven Development) for different CLI ecosystems
- **C4 Architecture** - Progressive disclosure with level-specific guidance (Context → Container → Component → Code)
- **SpecKit Extension** - PRIES workflow for spec-kit CLI
- **Claude Code Plugin** - Native plugin support for Claude Code sessions

---

## MATD: Two Integration Points

This repository provides **two distinct artifacts** for the MATD (Multi-Agent Test-Driven Development) workflow:

### 1. matd SpecKit Extension
- **Location**: `spec-kit-multi-agent-tdd/`
- **Purpose**: SpecKit CLI extension implementing PRIES workflow (PM → Refine → Implement → Evaluate → Simplify)
- **Usage**: Integrates with GitHub's SpecKit tool (`specify` CLI)
- **Commands**: `/speckit.matd.test`, `/speckit.matd.execute`, `/speckit.matd.specify-*`
- **Audience**: Teams using SpecKit for specification-driven development
- **Installation**: Via SpecKit extension system (`specify extension add`)

### 2. matd Claude Code Plugin
- **Location**: `.agents/plugins/matd/`
- **Purpose**: Skills, agents, and commands for Claude Code marketplace
- **Usage**: Add `plugins: [matd]` to `.harness.yaml` for marketplace integration
- **Commands**: `/matd-01-specification` through `/matd-04-implement`
- **Audience**: Claude Code users working in harness sandbox or standalone projects
- **Installation**: Via marketplace manifest (see Quick Install below)

### How They Relate

Both implementations share the same **Multi-Agent TDD methodology**:
- Specialized agents (Orchestrator, Architect, Specifier, QA, Dev, Critical Thinker)
- Test-driven development with RED → GREEN → REFACTOR cycle
- Progressive architectural disclosure (C4 model)
- Structured artifact creation (specs, plans, tests, implementations)

They differ in:
- **CLI integration layer** - SpecKit extension vs Claude Code plugin manifest
- **Command namespace** - `/speckit.matd.*` vs `/matd-*`
- **Artifact format** - SpecKit templates vs OpenSpec directory structure
- **Execution model** - SpecKit hooks vs Claude Code agent orchestration

**Which to use?**
- Use **SpecKit extension** if working in a SpecKit-managed codebase (`specify init` was run)
- Use **Claude Code plugin** for general Claude Code workflows or harness sandbox projects
- Both can coexist; choose based on primary workflow tool

---

## Quick Install

### Claude Code (Recommended)

```bash
cd /path/to/harness-tooling

# Project-scoped (this project only)
claude plugin install ./.claude-plugin/plugin.json --scope project

# User-scoped (all projects)
claude plugin install ./.claude-plugin/plugin.json --scope user
```

Verify installation:
```bash
claude .
# In chat:
/agents    # Should list 5 matd-* agents
/skills    # Should list 70+ skills
```

### OpenCode

OpenCode reads directly from the flat `.agents/` structure. No installation needed - just clone this repo.

```bash
# In your project
git clone <harness-tooling-url> .harness-tooling

# OpenCode auto-discovers agents/skills in .agents/
```

### SpecKit Extension

```bash
specify extension add harness-tdd-workflow \
  --from /path/to/harness-tooling/spec-kit-multi-agent-tdd
```

### Complete Registration Guide

For detailed installation instructions, troubleshooting, and advanced topics, see [docs/PLUGIN_REGISTRATION_GUIDE.md](docs/PLUGIN_REGISTRATION_GUIDE.md).

**Note:** Gemini CLI support is scaffolded but not implemented in v1.

---

## Repository Layout

```
.agents/                    # Canonical source (flat structure for OpenCode)
├── agents/                 # 5 MATD agents (matd-*.md)
├── skills/                 # 70+ skills (*/SKILL.md)
└── commands/               # 5 workflow commands (matd-*.md)

.claude/                    # Claude Code plugin structure
├── .claude-plugin/
│   └── plugin.json         # Plugin manifest
├── agents/                 # Symlinks → .agents/agents/matd-*.md
└── skills/                 # Symlinks → .agents/skills/*/

.gemini/                    # Gemini CLI scaffolding (v2)
└── extensions/
    └── matd-research/
        └── README.md       # Placeholder

docs/                       # Planning and specifications
├── marketplace/
│   └── plans/              # Architecture proposals, M3-M5 specs
└── harness-v1-master-plan.md
```

---

## MATD Workflow Overview

### The 4 Phases

1. **Specification** - `matd-specifier` drafts requirements → `matd-critical-thinker` validates
2. **Design** - `matd-architect` creates C4 diagrams and technical design
3. **Refinement** - `matd-architect` plans tasks → `matd-qa` writes E2E tests (RED)
4. **Implementation** - `matd-dev` implements via TDD → `matd-qa` verifies (GREEN)

### Workflow Commands

```bash
/matd-01-specification "User can register with email and password"
# → matd-orchestrator delegates to matd-specifier and matd-critical-thinker
# → User approves spec

/matd-02-design
# → matd-architect creates 4 C4 levels (Context, Container, Component, Code as needed)
# → User approves design

/matd-03-refine
# → matd-architect breaks down tasks
# → matd-qa writes E2E tests (RED)
# → User approves plan

/matd-04-implement
# → matd-dev implements to make tests GREEN
# → matd-qa final verification
# → matd-architect creates PR
```

### Agent Roles

| Agent | Symbol | Role | Read | Write | Orchestrate |
|-------|--------|------|------|-------|-------------|
| **matd-orchestrator** | - | PM Coordinator | ✓ | ✗ | ✓ |
| **matd-specifier** | Res | Requirements Engineer | ✓ | openspec/, docs/business/ | ✗ |
| **matd-critical-thinker** | Crit | Red Team Validator | ✓ | ✗ | ✗ |
| **matd-architect** | Arch | Solution Designer | ✓ | ✓ | ✓ |
| **matd-qa** | QA | Test Architect | ✓ | tests/, openspec/ | ✗ |
| **matd-dev** | SWE | Implementation Engineer | ✓ | app/, src/, lib/ | ✗ |

---

## Sibling Repositories

This repo is part of a 4-repo workspace:

| Repository | Purpose | Location |
|-----------|---------|----------|
| **harness-tooling** (this repo) | Marketplace - skills, agents, commands | `./` |
| **harness-sandbox** | Docker runtime - sandbox environment | `../harness-sandbox/` |
| **sta2e-vtt-lite** | Test project - application code | `../sta2e-vtt-lite/` |
| **sta2e-vtt-lite-system** | Test project - specs and docs | `../sta2e-vtt-lite-system/` |

See [`../GETTING_STARTED.md`](../GETTING_STARTED.md) for complete workspace setup.

---

## Skill Categories

### Architecture (`arch-*`)
- `arch-c4-architecture` - C4 model diagrams with Mermaid
- `arch-mermaid-diagrams` - General Mermaid syntax
- `arch-api-design-principles` - REST/GraphQL/OpenAPI design
- `arch-architecture-patterns` - Microservices, event-driven, etc.
- `arch-smart-docs` - deepwiki integration

### Development (`dev-*`)
- `dev-tdd` - Test-driven development practices
- `dev-alpine-js-patterns` - Lightweight frontend interactivity
- `dev-backend-to-frontend-handoff` - API contracts
- `dev-database-migration` - Schema evolution
- `dev-databases` - SQLAlchemy, async patterns

### Python (`python-*`)
- `python-async-patterns` - asyncio, aiohttp
- `python-code-style` - PEP 8, ruff, mypy
- `python-fastapi-templates` - FastAPI best practices
- `python-testing-uv-playwright` - Modern test stack

### Review (`review-*`)
- `review-check-correctness` - Behavioral validation
- `review-e2e-testing-patterns` - Integration test design
- `review-systematic-debugging` - Root cause analysis
- `review-webapp-testing` - Playwright patterns

### Orchestration (`orchestrate-*`)
- `orchestrate-dispatching-parallel-agents` - Concurrent subagents
- `orchestrate-executing-plans` - Batch execution
- `orchestrate-subagent-driven-development` - Sequential delegation

### STDD (`stdd-*`)
- `stdd-openspec` - OpenSpec directory structure
- `stdd-product-spec-formats` - Job Stories, EARS, Gherkin
- `stdd-test-driven-development` - Red-Green-Refactor
- `stdd-ask-questions-if-underspecified` - Requirement clarification

### General (`general-*`)
- `general-verification-before-completion` - Pre-completion checks
- `general-git-guardrails-claude-code` - Safe git operations
- `general-system-design` - High-level architecture
- `general-solid` - SOLID principles

---

## Creating a New Skill

```bash
cd .agents/skills
mkdir my-new-skill
cd my-new-skill

cat > SKILL.md << 'EOF'
---
name: my-new-skill
description: When to use this skill (shown in /skills list)
---

# Skill Title

[Content here]
EOF

# For Claude Code, symlink into .claude/skills/
cd ../../../.claude/skills
ln -s ../../.agents/skills/my-new-skill ./
```

---

## C4 Architecture Improvements

**Recent Change (2026-05-08):** Consolidated 4 C4 specialist agents into single `matd-architect` with level-specific guidance.

### Before
- 4 separate agents: `matd-c4-context`, `matd-c4-container`, `matd-c4-component`, `matd-c4-code`
- Complex delegation: orchestrator → architect → C4 specialist

### After
- Single `matd-architect` agent
- 5 reference files in `arch-c4-architecture/references/`:
  - `c4-best-practices.md` - Simon Brown guidelines, progressive disclosure
  - `c4-level-context.md` - System boundary, external actors
  - `c4-level-container.md` - Deployable units, technology
  - `c4-level-component.md` - Internal components, interfaces
  - `c4-level-code.md` - Classes, schemas, sequences

### Usage

```bash
# In matd-02-design command:
/subtask {agent: matd-architect} Create C4 Context diagram focusing ONLY on 
  system boundary and external actors. Use arch-c4-architecture skill with 
  references/c4-level-context.md guidance.
```

See [docs/marketplace/plans/c4-architecture-improvement-proposal.md](docs/marketplace/plans/c4-architecture-improvement-proposal.md) for full rationale.

---

## Update Skills

```bash
git pull origin dev
# All Claude Code sessions see new content immediately (symlinks)
# No re-installation needed
```

---

## Development

### Running Tests (Planned)
```bash
# Validate plugin.json
jq empty .claude-plugin/plugin.json

# Check agent frontmatter
yq eval '.name' .agents/agents/matd-architect.md
```

### Branch Strategy
- `main` - Stable releases
- `dev` - Active development (current: 7 commits ahead of origin)
- `feat/*` - Feature branches

---

## Documentation

- [GETTING_STARTED.md](../GETTING_STARTED.md) - Team onboarding guide
- [docs/harness-v1-master-plan.md](docs/harness-v1-master-plan.md) - Complete architecture
- [docs/marketplace/plans/matd-plugin-spec.md](docs/marketplace/plans/matd-plugin-spec.md) - MATD specification
- [docs/marketplace/plans/m3-m4-m5-subagent-prompts.md](docs/marketplace/plans/m3-m4-m5-subagent-prompts.md) - Plugin structure

---

## Platform Notes

- **Tested on:** Ubuntu/Debian, WSL2
- **Windows:** Install inside WSL (POSIX symlinks required)
- **Claude Code:** v2.1+ required for plugin support
- **OpenCode:** Works with flat `.agents/` structure (no plugin needed)

---

**Last Updated:** 2026-05-08 (M3-M5 complete, C4 refactor complete)
