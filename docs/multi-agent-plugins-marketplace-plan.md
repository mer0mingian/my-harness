# Multi-Agent Plugin Marketplace Strategy

**Status:** Research complete — strategy defined  
**Last updated:** 2026-04-20  
**Builds on:** [multi-agent-cli-harness-plan.md](multi-agent-cli-harness-plan.md)

---

## 1. Goal

Define a set of **workflow plugins** — each bundling hooks, commands, agents, skills, and MCP config — that can be installed from a single repository into **OpenCode**, **Claude Code**, and **Gemini CLI**, and produce close-to-identical behaviour when the same task is given to any of them.

The reference workflow is the **STDD Feature Workflow** (`.agents/commands/stdd-feat-workflow.md`), a four-stage orchestrated pipeline:

```
/stdd-feat-workflow $FEATURE
  └─ Stage 1: /stdd-01-specification  (ask + spec)
  └─ Stage 2: /stdd-02-design         (architecture)
  └─ Stage 3: /stdd-03-refine         (TDD + edge cases)
  └─ Stage 4: /stdd-04-implement      (code)
```

---

## 2. What Each CLI Supports Today

### 2.1 Claude Code — Plugins

| Component | Support | Notes |
|---|---|---|
| Skills | ✅ Native | `.claude/skills/<name>/SKILL.md`; also reads `.agents/skills/` via standard |
| Agents | ✅ Native | `.claude/agents/<name>.md`, frontmatter `skills: [...]` for per-agent assignment |
| Hooks | ✅ Native | `settings.json` `hooks:` block |
| Commands (slash) | ✅ Native | `.claude/commands/*.md` (also `.claude/skills/`) |
| MCP servers | ✅ Native | `settings.json` `mcpServers:` or `.mcp.json` |
| Plugin bundle format | ✅ Official | `.claude-plugin/plugin.json` manifest; distributed via GitHub URL |
| Per-agent skill isolation | ✅ Fine-grained | `skills: [skill1, skill2]` in agent frontmatter |
| Team marketplace | ✅ | `extraKnownMarketplaces` in settings.json |

### 2.2 Gemini CLI — Extensions

| Component | Support | Notes |
|---|---|---|
| Skills | ✅ Native | `extensions/<name>/skills/*.md`, loaded on-demand via `activate_skill` |
| Agents | ✅ Native | `extensions/<name>/agents/*.md` YAML frontmatter |
| Hooks | ✅ Native | Shell scripts, 11 lifecycle events via `settings.json` |
| Commands (slash) | ✅ Native | `extensions/<name>/commands/*.toml` |
| MCP servers | ✅ Native | Declared in `gemini-extension.json` `mcpServers:` block |
| Extension bundle format | ✅ Official | `gemini-extension.json` manifest; installed from GitHub URL |
| Per-agent skill isolation | ✅ Via scope | Skills inside an extension are scoped to it; `activate_skill` keeps them lazy |
| Central registry | ❌ None | GitHub URLs only; community gallery at geminicli.com |

### 2.3 OpenCode — Plugins

| Component | Support | Notes |
|---|---|---|
| Skills | ✅ Native | `.agents/skills/`, `.opencode/skills/`, `.claude/skills/` all discovered |
| Agents | ✅ Native | `.opencode/agents/*.md` YAML frontmatter; `permission:` block |
| Hooks (JS) | ✅ Native | Event subscription in plugin JS/TS module |
| Hooks (YAML) | ✅ Via plugin | `opencode-yaml-hooks`: `hooks.yaml` global + project |
| Commands (slash) | ✅ Native | `.opencode/commands/*.md` |
| MCP servers | ✅ Native | `opencode.jsonc` `mcp:` block |
| Plugin bundle format | ⚠️ JS only | Plugins are JS/TS modules — no declarative manifest |
| Per-agent skill isolation | ⚠️ ACL only | `permission.skill: { "prefix-": allow }` — prefix/wildcard ACL, not `skills:` list |
| `skills:` field in agent | ❌ Not yet | Open issue: `sst/opencode#19343` — watch for merge |
| Team marketplace | ❌ None | npm or GitHub URLs; no curated registry |

---

## 3. The Agent Skills Standard — The Portable Core

The **Agent Skills open standard** (agentskills.io, published 2025-12-18) is the primary cross-CLI compatibility layer, and **this harness is already using it correctly**.

The canonical skill path `.agents/skills/<name>/SKILL.md` is:
- Read natively by **OpenCode** (also reads `.claude/skills/`, `.opencode/skills/`)
- The standard path for **Gemini CLI** extensions
- Read by **Claude Code** once issue `anthropics/claude-code#31005` merges (currently requires `.claude/skills/`)

**Until that Claude Code issue merges:** the symlink `.claude/skills/ → ../.agents/skills/` (already in the harness plan) is the correct bridge.

### 3.1 Skill Naming Convention for Isolation

Since OpenCode's skill isolation is ACL-based (prefix wildcards), and Claude Code's is explicit list-based, **skill names should carry a workflow prefix**. This enables scoping in both CLIs:

```
stdd-ask-questions-if-underspecified/   ← STDD workflow skills
stdd-openspec/
stdd-product-spec-formats/
stdd-test-driven-development/
stdd-project-summary/

orchestrate-dispatching-parallel-agents/  ← Orchestration skills
orchestrate-executing-plans/
orchestrate-subagent-driven-development/
orchestrate-finishing-a-development-branch/

review-differential-review/              ← Review workflow skills
review-systematic-debugging/
review-e2e-testing-patterns/
```

This convention already exists in the harness. **Enforce it strictly** — a skill without a workflow prefix is a global utility skill (e.g., `brainstorming`, `docker-expert`).

---

## 4. Skill Isolation Strategy Per CLI

### 4.1 Claude Code — Explicit `skills:` list

In each agent definition, explicitly enumerate allowed skills:

```yaml
# .claude/agents/daniels-workflow-orchestrator.md
---
name: daniels-workflow-orchestrator
description: Master orchestrator for the STDD feature development workflow
skills:
  - stdd-ask-questions-if-underspecified
  - stdd-openspec
  - stdd-product-spec-formats
  - stdd-project-summary
  - orchestrate-executing-plans
  - orchestrate-dispatching-parallel-agents
---
```

Skills not in the list are invisible to this agent. This is the strictest isolation available.

### 4.2 Gemini CLI — Extension scoping

Skills bundled inside an extension are only available within that extension's context. The `activate_skill` mechanism keeps them lazy-loaded. Structure each workflow as its own extension:

```
.gemini/extensions/stdd-workflow/
├── gemini-extension.json
├── agents/daniels-workflow-orchestrator.md
├── skills/                         ← symlinks to .agents/skills/stdd-*/
│   ├── stdd-ask-questions-if-underspecified/ → ../../../../.agents/skills/stdd-ask-questions-if-underspecified/
│   ├── stdd-openspec/ → ...
│   └── stdd-product-spec-formats/ → ...
└── commands/
    ├── stdd-feat-workflow.toml
    └── stdd-0{1..4}-*.toml
```

### 4.3 OpenCode — Prefix ACL

Use the `permission.skill` block with the workflow prefix as the ACL key. For agents that should only see STDD skills:

```yaml
# .opencode/agents/daniels-workflow-orchestrator.md (or .agents/agents/)
---
description: Master orchestrator for the STDD feature development workflow
mode: subagent
permission:
  skill:
    "stdd-": allow
    "orchestrate-": allow
    "": deny        # deny everything not explicitly allowed
  edit:
    "": deny
    "specs/**": allow
    "openspec/**": allow
  bash:
    "": deny
    "git status*": allow
    "git log*": allow
---
```

This is the closest OpenCode can get today. It's coarser than Claude Code's explicit list, but the prefix convention makes it deterministic.

**Watch:** `sst/opencode#19343` — if merged, replace the ACL with `skills: [stdd-ask-questions-if-underspecified, ...]`.

---

## 5. Workflow Portability Strategy

### 5.1 The Portability Ladder

Not all workflow components are equally portable. Work from the most portable layer outward:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1 — Skills (SKILL.md)                                │
│  Portable: Claude Code ✅  OpenCode ✅  Gemini CLI ✅       │
│  No changes needed. Already in .agents/skills/.             │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2 — Agent system prompts (markdown body)             │
│  Shared: same .md body referenced by all three CLIs         │
│  Frontmatter differs per CLI — thin per-CLI wrappers        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3 — Commands / slash commands                        │
│  Claude Code: .md  ✅  OpenCode: .md  ✅  Gemini: .toml ⚠️ │
│  Already dual-format in .agents/commands/                   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4 — Hooks                                            │
│  Not portable. Define separately per CLI, same logic.       │
│  opencode-yaml-hooks enables external YAML for OpenCode.    │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5 — Orchestration / workflow engine                  │
│  Not portable. opencode-workflows (YAML) for OpenCode only. │
│  Claude Code: slash command chains. Gemini CLI: none.       │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Shared Agent Prompt Files

Both Claude Code and OpenCode support externalising the agent body via file inclusion. Use a shared prompt file and thin per-CLI frontmatter wrappers:

```
.agents/agents/
├── prompts/
│   └── daniels-workflow-orchestrator.txt   ← shared body, all CLIs read this
├── daniels-workflow-orchestrator.md         ← OpenCode frontmatter wrapper
└── (symlinked or copied into .claude/agents/ and .gemini/extensions/stdd-workflow/agents/)
```

OpenCode syntax: `{file:./prompts/daniels-workflow-orchestrator.txt}` in the agent `.md` body.  
Claude Code / Gemini CLI: include the prompt text directly or via similar mechanism.

### 5.3 The STDD Workflow Across All Three CLIs

#### Trigger (all CLIs)

| CLI | Command | Mechanic |
|---|---|---|
| OpenCode | `/stdd-feat-workflow $FEATURE` | `.agents/commands/stdd-feat-workflow.md` |
| Claude Code | `/stdd-feat-workflow $FEATURE` | `.claude/commands/stdd-feat-workflow.md` |
| Gemini CLI | `/stdd-feat-workflow $FEATURE` | `.gemini/extensions/stdd-workflow/commands/stdd-feat-workflow.toml` |

#### Orchestration

| CLI | Mechanism | Definition |
|---|---|---|
| OpenCode | `daniels-workflow-orchestrator` agent + sub-commands | `.agents/agents/daniels-workflow-orchestrator.md` |
| OpenCode (enhanced) | `opencode-workflows` YAML definition | `.opencode/workflows/stdd-feat-workflow.yaml` |
| Claude Code | Agent invoked from command frontmatter `agent:` field | `.claude/agents/daniels-workflow-orchestrator.md` |
| Gemini CLI | Sub-agent defined in extension `agents/` | `.gemini/extensions/stdd-workflow/agents/daniels-workflow-orchestrator.md` |

#### STDD OpenCode Workflow YAML (via `opencode-workflows`)

```yaml
# .opencode/workflows/stdd-feat-workflow.yaml
id: stdd-feat-workflow
name: "STDD Feature Workflow"
description: "Granular spec-driven development pipeline"
inputs:
  feature:
    description: "Feature to develop"
    required: true
steps:
  - id: specification
    type: agent
    agent: daniels-workflow-orchestrator
    prompt: |
      Execute Stage 1 — Specification for: {{inputs.feature}}
      Run /stdd-01-specification {{inputs.feature}} and wait for user approval.
  - id: design
    type: agent
    agent: daniels-workflow-orchestrator
    condition: "{{steps.specification.approved}}"
    prompt: |
      Execute Stage 2 — Design.
      Run /stdd-02-design and wait for user approval.
  - id: refinement
    type: agent
    agent: daniels-workflow-orchestrator
    condition: "{{steps.design.approved}}"
    prompt: |
      Execute Stage 3 — Refinement.
      Run /stdd-03-refine and wait for user approval.
  - id: implementation
    type: agent
    agent: daniels-workflow-orchestrator
    condition: "{{steps.refinement.approved}}"
    prompt: |
      Execute Stage 4 — Implementation.
      Run /stdd-04-implement.
```

---

## 6. Recommended New Plugins to Add

### 6.1 `opencode-workflows` (IgorWarzocha)

**What:** Adds a `workflow` tool and `/workflow run <id>` command. Workflow definitions are YAML files in `.opencode/workflows/` — human-readable, LLM-friendly, no JS required.

**Why add it:** The STDD workflow's 4-stage sequential pipeline with approval gates is exactly the use case. YAML definitions are more maintainable than hardcoded agent prompt chains. Provides the closest OpenCode analog to Claude Code's command-chain orchestration.

**Install:**
```json
// opencode.jsonc
"plugin": ["opencode-workflows"]
```

### 6.2 `opencode-yaml-hooks` / `OpenCode-Hooks` (mer0mingian fork)

**What:** Loads hook definitions from `hooks.yaml` instead of requiring hardcoded JS in a plugin module.

**Why add it:** Hooks defined in YAML are readable alongside Claude Code's `settings.json` hooks and Gemini CLI's `settings.json` hooks — the same logical intent can live in adjacent, human-readable files for each CLI. Easier to audit, maintain, and keep in sync across CLIs.

**Config locations:**
- Global: `~/.config/opencode/hook/hooks.yaml`
- Project: `.opencode/hook/hooks.yaml`

**Install:**
```bash
bun add "https://github.com/mer0mingian/OpenCode-Hooks.git"
```

### 6.3 `opencode-skills-collection` (npm)

**What:** Plugin that automatically downloads and keeps skills updated from a remote registry.

**Why consider it:** If skills are distributed across team members via a shared GitHub repo, this plugin can auto-sync them without manual copying. However, the current harness already handles this via git — only add if team members need to use the harness without cloning the full repo.

---

## 7. Single-Repo Structure for Workflow Plugins

```
my-harness/
├── .agents/                          ← Central source of truth
│   ├── skills/                       ← All SKILL.md files (portable, agent-skills standard)
│   │   ├── stdd-*/                   ← STDD workflow skills (prefixed)
│   │   ├── orchestrate-*/            ← Orchestration skills
│   │   ├── review-*/                 ← Review workflow skills
│   │   └── general-*/               ← Global utilities
│   ├── agents/                       ← Agent definitions
│   │   ├── prompts/                  ← Shared agent body text (referenced by all CLIs)
│   │   ├── daniels-workflow-orchestrator.md
│   │   └── daniels-architect.md
│   └── commands/                     ← Multi-format commands
│       ├── stdd-feat-workflow.md     ← OpenCode + Claude Code format
│       ├── stdd-feat-workflow.toml   ← Claude Code TOML (optional)
│       └── stdd-feat-workflow.gemini.toml  ← Gemini CLI format
│
├── .opencode/
│   ├── opencode.jsonc                ← Plugins, MCP config
│   ├── workflows/                    ← opencode-workflows YAML definitions
│   │   └── stdd-feat-workflow.yaml
│   ├── hook/hooks.yaml               ← opencode-yaml-hooks definitions
│   ├── skills/ → ../.agents/skills/  ← symlink
│   ├── agents/ → ../.agents/agents/  ← symlink
│   └── commands/ → ../.agents/commands/  ← symlink
│
├── .claude/
│   ├── settings.json                 ← Hooks, MCP config, marketplace
│   ├── skills/ → ../.agents/skills/  ← symlink (until #31005 merges)
│   ├── agents/ → ../.agents/agents/  ← symlink
│   └── commands/ → ../.agents/commands/  ← symlink
│
└── .gemini/
    └── extensions/
        └── stdd-workflow/
            ├── gemini-extension.json  ← MCP config, context file
            ├── GEMINI.md             ← Context injected each session
            ├── agents/ → ../../../../.agents/agents/  ← symlink
            ├── skills/               ← Symlinks to stdd-* skills only
            │   ├── stdd-ask-questions-if-underspecified/ → ../../../../.agents/skills/...
            │   └── stdd-openspec/ → ...
            └── commands/ → ../../../../.agents/commands/  ← symlink
```

---

## 8. Gaps and What to Watch

### Currently unsolvable

| Gap | Affected CLI | Workaround |
|---|---|---|
| No `skills:` list in agent frontmatter | OpenCode | Prefix ACL (`permission.skill`) |
| Claude Code doesn't read `.agents/skills/` | Claude Code | Symlink `.claude/skills/ → .agents/skills/` |
| Gemini CLI has no orchestration/workflow engine | Gemini CLI | Manual stage-by-stage execution |
| OpenCode plugin format is JS, not declarative | All | YAML hooks + YAML workflows reduce JS surface |

### Open issues to watch

| Issue | What changes if merged | Priority |
|---|---|---|
| `sst/opencode#19343` | `skills:` list in OpenCode agent frontmatter — full parity with Claude Code | High |
| `anthropics/claude-code#31005` | Claude Code reads `.agents/skills/` natively — removes symlink need | Medium |
| `sst/opencode#20474` | `hidden: true` per-skill frontmatter flag — opt-out of agent visibility | Low |

---

## 9. Implementation Roadmap

### Phase 1 — Already done (per harness plan v1.1)
- [x] `.agents/skills/`, `.agents/agents/`, `.agents/commands/` populated
- [x] Multi-format commands (.md, .toml, .gemini.toml) for all stdd-* stages
- [x] Symlinks from `.opencode/` to `.agents/`

### Phase 2 — Skill isolation (next)
- [ ] Audit `stdd-*` agent definitions: add `skills:` list to Claude Code agent frontmatter
- [ ] Add `permission.skill: { "stdd-": allow, "orchestrate-": allow, "": deny }` to OpenCode STDD agent definitions
- [ ] Create `.gemini/extensions/stdd-workflow/skills/` with symlinks to `stdd-*` skills only

### Phase 3 — Hook alignment
- [ ] Add `opencode-yaml-hooks` plugin
- [ ] Write `.opencode/hook/hooks.yaml` mirroring Claude Code's `settings.json` hooks block
- [ ] Document side-by-side: what each hook does in each CLI

### Phase 4 — OpenCode workflow YAML
- [ ] Add `opencode-workflows` plugin
- [ ] Write `.opencode/workflows/stdd-feat-workflow.yaml` (see Section 5.3)
- [ ] Test full pipeline execution via `/workflow run stdd-feat-workflow feature="X"`

### Phase 5 — Distribution
- [ ] Add `.claude-plugin/plugin.json` manifest for Claude Code marketplace distribution
- [ ] Add `gemini-extension.json` manifest for Gemini CLI distribution
- [ ] Add `install.sh` entry for OpenCode plugin declaration in `opencode.jsonc`
- [ ] Tag repo as v1.0.0 for version-pinned installs
