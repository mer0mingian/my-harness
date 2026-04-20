# CLAUDE.md — my-harness (marketplace)

This is the MARKETPLACE repo in a two-repo harness. The sibling sandbox
runtime lives at `../harness-sandbox`. The parent workspace `CLAUDE.md`
at `/mnt/c/memory/CLAUDE.md` covers cross-repo scope.

## Scope of this repo

Skills, agents, commands, and plugin manifests consumed by Claude Code,
OpenCode, and Gemini CLI. Do NOT add Dockerfile, docker-compose, or any
runtime orchestration here — those belong in `../harness-sandbox`.

## Canonical source

All skills, agents, commands live under `.agents/`. Per-CLI directories
(`.claude/`, `.opencode/`, `.gemini/`) are thin wrappers:
- `.claude/skills`, `.claude/agents`, `.claude/commands` — symlinks to `.agents/…`
- `.opencode/skills`, `.opencode/agents`, `.opencode/commands` — symlinks to `.agents/…`
- `.gemini/extensions/research/` — scoped view: only `review-*` + `general-*` skills

## Skill naming

Skills carry workflow prefixes: `stdd-`, `orchestrate-`, `review-`, `general-`.
Roughly 20 legacy skills remain un-prefixed pending a later audit pass
(see session memory: "Skill-naming audit deferred to a later session").

## Agent frontmatter

Every agent file under `.agents/agents/` carries BOTH a Claude-Code-style
`skills:` list AND an OpenCode-style `permission.skill:` ACL. Preserve
both when editing — they are consumed by different CLIs.

## Plans

- Master plan: [docs/harness-v1-master-plan.md](docs/harness-v1-master-plan.md)
- Task definitions: [docs/harness-v1-agent-tasks.md](docs/harness-v1-agent-tasks.md)
- Archived plans: [docs/archive/](docs/archive/)
