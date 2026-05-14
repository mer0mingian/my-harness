# harness-tooling — Documentation Index

Documentation hub for the **harness-tooling** marketplace repo. For the repo overview, see [../README.md](../README.md); for workspace-level context, see `../../CLAUDE.md`.

Sibling repo runtime docs: [../../harness-sandbox/docs/](../../harness-sandbox/docs/).

---

## Setup

- **[../README.md](../README.md)** — Repo overview, quick install for Claude Code / OpenCode / SpecKit.
- **[PLUGIN_REGISTRATION_GUIDE.md](PLUGIN_REGISTRATION_GUIDE.md)** — Full install + register guide. Plugin manifest lives at `.claude-plugin/plugin.json` (root) and `.agents/plugins/<name>/.claude-plugin/plugin.json` (per-plugin).

## Usage

- **[../AGENTS.md](../AGENTS.md)** — Agent / plugin architecture, MATD integration paths (Claude Code plugin vs SpecKit extension), agent role catalog.
- **[../spec-kit-multi-agent-tdd/USER-GUIDE.md](../spec-kit-multi-agent-tdd/USER-GUIDE.md)** — Using the matd SpecKit extension (`harness-tdd-workflow`).
- **[../.speckit-templates/README.md](../.speckit-templates/README.md)** — SpecKit template assets bundled by this repo.

## Architecture

- **[Solution Design.md](Solution%20Design.md)** — Hierarchical plugin architecture, monorepo + symlink registry, artifact pipeline.
- **[CLI-HOOKS-IMPLEMENTATION-SUMMARY.md](CLI-HOOKS-IMPLEMENTATION-SUMMARY.md)** — Hybrid command + hooks approach for automated doc updates (2026-05-12).
- **[DESIGN-CLI-HOOKS-AUTOMATION.md](DESIGN-CLI-HOOKS-AUTOMATION.md)** — Design notes for the same.
- **[architecture/](architecture/)** — Tldraw boards (`Agentic Engineering Tool build`, `Agentic Engineering Workflow`, `Scaling Agentic Engineering to Teams`).
- **[deep-research/](deep-research/)** — Background research:
  - `operational-architectures.md` — Operational architecture patterns
  - `scaling-software-teams.md` — Team scaling strategies
  - `workflows-via-command-chaining.md` — Workflow orchestration via command chaining

## Specs

- **[specs/](specs/)** — Active bug fixes and feature specs:
  - `bug-fix-claude-startup-errors.md`
  - `bug-fix-invalid-char-harness-yml.md`
  - `bug-fix-stony-compose-profile.md`
  - `bug-fix-wrong-agent-format.md`
  - `update-template-harness-yml-config.md`
- **[plans/](plans/)** — Active planning artifacts:
  - `matd-training-exercise-job-recommendations.md`
  - `open-bugs.md`, `open-features.md`
- **[marketplace/plans/](marketplace/plans/)** — Marketplace evolution plans:
  - `harness-v1-master-plan.md` — v1 delivery plan
  - `harness-v1-agent-tasks.md` — Subagent prompts for v1
  - `harness-workflow-runtime-plan.md` — Workflow runtime plugin
  - `matd-plugin-spec.md` — MATD plugin specification
  - `m3-m4-m5-subagent-prompts.md` — Plugin structure prompts
  - `c4-architecture-improvement-proposal.md` — C4 refactor rationale
- **[marketplace/reference-workflows-ppries/](marketplace/reference-workflows-ppries/)** — Reference multi-agent workflow implementation (PRIES).

## Development & Operations

- **[../IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)** — Active implementation plan.
- **[../scripts/](../scripts/)** — Helper scripts (CLI hooks, doc automation).
- **[../install.sh](../install.sh)** — Bootstrap installer.

## Archive

- **[archive/](archive/)** — Deprecated plans, kept for historical context only. Each archived file has a deprecation banner. Do NOT use for new work.

---

## Quick Links by Use Case

### "I want to install the marketplace plugin"
1. [../README.md#quick-install](../README.md#quick-install)
2. [PLUGIN_REGISTRATION_GUIDE.md](PLUGIN_REGISTRATION_GUIDE.md)
3. Manifest: `.claude-plugin/plugin.json`

### "I want to understand the MATD workflow"
1. [../AGENTS.md](../AGENTS.md) — Two MATD integration paths
2. [marketplace/plans/matd-plugin-spec.md](marketplace/plans/matd-plugin-spec.md) — Spec
3. [../spec-kit-multi-agent-tdd/USER-GUIDE.md](../spec-kit-multi-agent-tdd/USER-GUIDE.md) — SpecKit usage

### "I want to add a new skill / agent / command"
1. Drop the file in `.agents/skills/<name>/SKILL.md`, `.agents/agents/<name>.md`, or `.agents/commands/<name>.md`.
2. The Claude Code plugin manifest (`.claude-plugin/plugin.json`) references those directories — no manifest edits needed.
3. OpenCode picks up new files automatically.

### "I'm hunting a bug or open issue"
1. [specs/](specs/) — Latest bug-fix and config-update specs
2. [plans/open-bugs.md](plans/open-bugs.md)
3. [plans/open-features.md](plans/open-features.md)

---

*Last Updated: 2026-05-14*
