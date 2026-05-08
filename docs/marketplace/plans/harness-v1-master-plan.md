# Harness v1 — Master plan

**Status:** Drafted, awaiting approval to deploy agents
**Last updated:** 2026-04-21
**Supersedes (in part):** [multi-agent-cli-harness-plan.md](multi-agent-cli-harness-plan.md), [multi-agent-plugins-marketplace-plan.md](multi-agent-plugins-marketplace-plan.md), [multi-container-harness-plan.md](multi-container-harness-plan.md)
**Companion:** [harness-v1-agent-tasks.md](harness-v1-agent-tasks.md) — copy-pasteable subagent prompts, one per task

---

## 1. Purpose

Deliver a working **v1** of the multi-agent-cli harness: a reproducible docker-compose sandbox that runs Claude Code, OpenCode, and Gemini CLI with a shared marketplace of skills/agents/commands, plus locally-hosted memory services (Haft, CodeGraphContext, optionally Graphiti). v1 must be usable immediately and onboardable by one teammate within a week with no additional tooling.

**Current workspace:** `/home/minged01/repositories/harness-workplace/`

## 2. Vision recap (what Daniel asked for)

1. **One marketplace**, three CLIs. Shared workflow plugins; same command surface; non-uniform orchestration is accepted.
2. **One sandboxed runtime**, easy to start, lightweight, usable across all of Daniel's repos. Primary interface is the agent CLI.
3. **Code bind-mounted from host**, never baked in. Dev can edit via VS Code Remote, WSL bash, or inside the container interchangeably.

## 3. Scope of v1 (what this plan delivers)

### harness-sandbox/ (populate the scaffold created on 2026-04-21)
- `Dockerfile` extending the pinned NVIDIA OpenShell-Community Gemini sandbox, layering in Claude Code, OpenCode, Chloe, rtk.
- `docker-compose.yml` — agent container, long-running, one per project, bind-mounts marketplace + project source + host `~/.claude`, `~/.opencode`, `~/.gemini`.
- `docker-compose.services.yml` — shared services stack: Haft MCP + CodeGraphContext MCP + their required DBs + `litho` (deepwiki-rs) gated behind the `docs` Compose profile so it only starts on `docker compose --profile docs run --rm litho ...`.
- ~~`docker-compose.graphiti.yml` — optional personal memory; separate file so `docker compose -f docker-compose.yml up` never starts it accidentally.~~ **[Superseded — see CGC integration]** Graphiti was dropped from v1; CGC now runs as the external `cgc` service in `docker-compose.yml` and provides only the structural code graph (no episodic memory).
- `.env.example` — placeholders for every API key and service config referenced by any compose file.
- `bin/harness` — host-side entry script: `harness up`, `harness shell`, `harness down`, `harness services up/down`.
- Short docs for quickstart and common attach patterns.

### my-harness/ (restructure the existing tree)
- `.agents/` confirmed as canonical source of truth for skills/agents/commands.
- Skill-isolation strategy applied: workflow-prefix audit + per-CLI ACL/list.
- `.claude/` symlinks + `settings.json` + `.claude-plugin/plugin.json` (markdown commands — **no TOML**).
- `.opencode/` symlinks + `permission.skill` ACLs on agent frontmatter.
- `.gemini/extensions/stdd-workflow/` with correct `gemini-extension.json` shape and scoped skill symlinks.
- Nested agent subdirs (`c4-architecture-agents/`, `daniels-workflow-agents/`, `tdd-agents/`) flattened per-CLI where required.
- Root `README.md` + `CLAUDE.md` refreshed; old plan docs marked deprecated with cross-links to this plan.

### Cross-repo
- Smoke-validation that each CLI loads its manifest and at least one STDD command resolves.

## 4. Out of scope for v1 (explicit)

- K3s / Kubernetes / OpenShell policy-engine orchestration → v2.
- Team-shared AWS deployment of Haft/CodeGraphContext → v2 (DevOps support pending).
- Neo4j caching for `litho` (optional upstream feature) → v2.
- `claude-reflect-system` and `opencode-skill-evolution` reflection loops → v2.
- Automated PR creation to the marketplace from skill-evolution tools → v2.
- codeburn installation — v1 mentions it in docs as a host-level tool, but does not install or wire it.
- Enterprise Architecture policy integration → v2+ (Stepstone overlay track).

## 5. Corrections from prior plans (applied by this plan)

The older `multi-agent-cli-harness-plan.md` contained several factual errors. This plan fixes them:

| Prior claim | Reality | Action in v1 |
|---|---|---|
| Claude Code commands are TOML | Claude Code uses markdown (`.claude/commands/*.md`) | Drop TOML pipeline for Claude Code entirely |
| Gemini CLI has `.gemini/mcp-servers.json` | Gemini CLI puts MCP config inside `gemini-extension.json` | Configure MCP inside the extension manifest |
| Custom MCP server lives in `.agents/mcp/` | Needed MCP servers (Haft, CGC, Graphiti) are external | `.agents/mcp/` is not created; MCP points at sibling compose services |
| "Migrate agents" handled flat | Existing agent directory has nested subfolders Claude Code doesn't recurse into | Flatten or per-CLI restructure via task M2 |
| Bash conversion script for TOML | Unnecessary given reality above | Deleted from scope |
| `.agents/configs/mcp_config.yaml` is authoritative | It's a research document | Treat as reference, do not ship |

## 6. Multi-repo boundaries

| File type | Belongs in | Reason |
|---|---|---|
| Skills, agents, commands, plugin manifests | `harness-tooling/` | Marketplace — changes often, versioned alongside workflow content |
| Dockerfile, compose files, entry script, `.env.example` | `harness-sandbox/` | Runtime — changes rarely, different release cadence |
| Planning docs | `harness-tooling/docs/marketplace/plans/` | Marketplace planning; not shipped in plugin bundles |
| Test project application code | `sta2e-vtt-lite/` | Fresh implementation using SpecKit/BMAD |
| Test project system docs & specs | `sta2e-vtt-lite-system/` | BMAD artifacts, legacy docs, architecture, C4 |
| Workspace-level `CLAUDE.md`, `.code-workspace` | `/home/minged01/repositories/harness-workplace/` | Parent workspace, shared across repos |
| Session memory (MEMORY.md) | `~/.claude/projects/...` | User-scoped; never committed |

## 7. Target end state (post-execution)

```
/home/minged01/repositories/harness-workplace/  (parent workspace)
├── CLAUDE.md                                   (workspace-level instructions)
├── RTK.md                                      (RTK token optimization config)
├── harness.code-workspace                      (VS Code multi-root workspace)
├── harness-tooling/                            (git, marketplace)
│   ├── .agents/
│   │   ├── skills/                             (prefixed: stdd-*, orchestrate-*, review-*, general-*, etc.)
│   │   ├── agents/
│   │   │   ├── prompts/                        (shared agent bodies)
│   │   │   ├── test-specialist.md              (TDD test agent)
│   │   │   ├── dev-specialist.md               (TDD implementation agent)
│   │   │   ├── arch-specialist.md              (Architecture reviewer)
│   │   │   ├── review-specialist.md            (Code reviewer)
│   │   │   └── …
│   │   └── commands/                           (.md for Claude Code + OpenCode)
│   ├── .claude-plugin/plugin.json              (marketplace manifest)
│   ├── spec-kit-multi-agent-tdd/               (SpecKit extension)
│   │   ├── .claude/commands/                   (slash commands)
│   │   │   ├── speckit.multi-agent.test.md
│   │   │   ├── speckit.multi-agent.implement.md
│   │   │   ├── speckit.multi-agent.review.md
│   │   │   └── speckit.multi-agent.commit.md
│   │   └── docs/                               (extension documentation)
│   ├── README.md                               (marketplace overview)
│   ├── CLAUDE.md                               (tooling repo instructions)
│   └── docs/
│       └── marketplace/plans/
│           ├── harness-v1-master-plan.md       (this doc)
│           └── harness-v1-agent-tasks.md       (companion)
├── harness-sandbox/                            (git, sandbox runtime)
│   ├── Dockerfile                              (two-stage: ca-ready + tools)
│   ├── docker-compose.yml                      (agent + cgc + litho services)
│   ├── workspace-template/                     (SpecKit workspace template)
│   │   ├── .claude/                            (team-shared Claude config)
│   │   │   └── mcp.json.example                (CGC + MCP servers)
│   │   ├── .specify/                           (SpecKit config)
│   │   ├── .harness.yml                        (workspace + plugin config)
│   │   ├── docs/                               (artifact directories)
│   │   ├── specs/                              (specifications)
│   │   └── architecture/                       (C4, ADRs, deepwiki)
│   ├── .env.example
│   ├── bin/
│   │   ├── harness                             (lifecycle manager)
│   │   └── sandbox-entrypoint.sh               (container init)
│   ├── README.md
│   ├── CLAUDE.md                               (sandbox repo instructions)
│   ├── Task-List.md                            (implementation tasks)
│   ├── Technical-Requirements.md               (requirements spec)
│   └── Roadmap.md                              (phase dependencies)
├── sta2e-vtt-lite/                             (git, test project - app code)
│   └── (empty until Phase 4)
└── sta2e-vtt-lite-system/                      (git, test project - system docs)
    └── legacy_docs/                            (BMAD migration source)
        ├── business/                           (user journeys)
        ├── architecture/                       (C4 diagrams, decisions)
        ├── game_mechanics/                     (STA 2e rules + data)
        └── specifications/                     (feature requirements)
```

## 8. Execution phases

| Phase | Goal | Parallelism | Gate |
|---|---|---|---|
| **0 — Research** | Pin down facts the plan depends on (upstream Dockerfile, MCP server specs) | All 4 research tasks in parallel | Main thread synthesizes; no write yet |
| **1 — Sandbox build** | Populate `harness-sandbox/` | 5 tasks parallel after R2/R3/R4 land | `docker compose config` validates, image builds |
| **2 — Marketplace restructure** | Fix my-harness format errors + apply isolation | M1/M2 parallel; then M3/M4/M5 parallel; then M6 | Symlinks resolve; manifests are valid JSON |
| **3 — Docs consolidation** | Deprecate old plans, refresh READMEs | 1 task | Cross-references land |
| **4 — Validation** | Smoke-test that each CLI can see the marketplace | V1 automated; V2 manual (needs host CLIs) | Daniel signs off |

Dependency DAG:
```
Phase 0: R1  R2  R3  R4   (all parallel)
             │   │   │
             v   v   v
Phase 1:  S1 S2 S3 S4 S5  (parallel after R2/R3/R4)
Phase 2 (needs R1):
           M1 ─┐
           M2 ─┼─> M3 ─┐
                │      │
                ├─> M4 ─┼─> M6
                │      │
                └─> M5 ─┘
Phase 3:   D1  (parallel with Phase 2 once M1 done)
Phase 4:   V1  (after all above)
           V2  (manual, Daniel runs)
```

## 9. Delegation principles

### What stays in the main thread (Opus)

- Synthesizing Phase 0 research into concrete Phase 1/2 prompts.
- Any hinge decision that wasn't pre-answered (e.g., Haft requires a DB we didn't know about).
- Reviewing each phase's output before launching the next.
- Anything touching git history, branches, or remotes.
- Anything that deletes content (archival moves are staged but main thread confirms).

### What subagents do

- Mechanical inventory (list files, check naming, validate JSON).
- File writing from a fully specified template (Dockerfile, compose, manifests, symlink trees).
- Upstream doc fetching + structured summary.
- Read-only verification passes.

### Model tier

- **Haiku** for mechanical / deterministic tasks (inventory, JSON validation, symlink audit).
- **Sonnet** for tasks needing judgment (writing a Dockerfile from upstream, reconciling nested agent folders across three CLIs).
- **No Opus subagents.** If a task needs Opus reasoning, it belongs in the main thread.

### Guardrails in every prompt

Every subagent prompt explicitly states:
- Workspace parent path: `/mnt/c/memory/`
- Which repo it's allowed to write to (and which it MUST NOT touch).
- Whether it may write files at all (research tasks return text only).
- Forbidden actions: no `git commit`, no `git push`, no deletions, no destructive rewrites.
- Expected response format + size cap.

## 10. Where to find the per-task prompts

All subagent prompts, dependencies, and validation criteria live in:

**[harness-v1-agent-tasks.md](harness-v1-agent-tasks.md)**

Each task is copy-pasteable into the `Agent` tool call. The tasks doc is authoritative for execution; this doc is authoritative for reasoning.

## 11. How to deploy (for Daniel)

1. Read this plan + the tasks doc. Object to anything you'd change now — it's much cheaper to adjust here than mid-execution.
2. Say **"deploy phase 0"** (or equivalent). Main thread launches R1–R4 in parallel.
3. After Phase 0 reports land, main thread synthesizes findings and proposes Phase 1/2 prompts (with research findings inlined). Confirm before Phase 1.
4. Phase 1 + 2 + 3 roll out; main thread reports progress between phases.
5. Phase 4 V1 runs automated; V2 requires you to run the CLIs against the repo manually — main thread hands you the exact commands.

## 12. Manual / human-only steps (not delegated)

- `git remote add origin` + initial push for `harness-sandbox`. No gh CLI; pick GitHub repo URL manually.
- Filling `.env` from `.env.example` with real API keys. Subagents never see secrets.
- Moving the workspace from `/mnt/c/memory/` to WSL ext4 when convenient. The layout transplants whole; no plan rework needed.
- Registering the marketplace with each CLI for the first time (`claude marketplace add …`, OpenCode plugin install, Gemini extension install). Subagents write the manifests; Daniel runs the install commands.

## 13. Rollback story

- harness-sandbox: git is fresh; `git reset --hard HEAD` wipes any failed phase. Nothing in the sandbox repo depends on live state.
- my-harness: every restructure task creates a branch. The user merges; a failed pass is `git checkout main` away from the prior state. No task does destructive rewrites on `main`.
- Services: `docker compose down -v` wipes local state without touching host.
