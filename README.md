# my-harness

The skills/agents/commands marketplace for Daniel's multi-agent-cli harness.

## Repos

| Repo | Role |
|---|---|
| `my-harness` (this repo) | Marketplace — skills, agents, commands, plugin manifests |
| `../harness-sandbox` | Runtime — Docker orchestration, container setup, sandbox |

## Install into each CLI

### Claude Code

Plugin manifest at [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

```bash
/plugin marketplace add <repo-url>   # URL TBD — repo not yet published
```

### OpenCode

Plugin array declared in [`.opencode/opencode.jsonc`](.opencode/opencode.jsonc). Add this repo as a plugin entry in the `plugin:` array.

### Gemini CLI

Extension at [`.gemini/extensions/research/`](.gemini/extensions/research/).

```bash
gemini extensions install <path-to-this-repo>/.gemini/extensions/research
```

## Layout

```
.agents/          # Canonical source of truth
├── skills/       # All skill dirs (SKILL.md per skill)
├── agents/       # Agent definitions (.md with YAML frontmatter)
└── commands/     # Slash commands (.md, .toml, .gemini.toml formats)

.claude/          # Claude Code wrappers (symlinks → .agents/)
.opencode/        # OpenCode wrappers (symlinks → .agents/) + opencode.jsonc
.gemini/          # Gemini CLI extension manifests + scoped skill views
.claude-plugin/   # Claude Code plugin manifest (plugin.json)
```

## Quickstart (install.sh)

Pick a scope and run the one-liner. The script clones this repo and symlinks the three subdirs into each CLI's config path.

**User scope** — available in every project on this machine:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/mer0mingian/my-harness/main/install.sh) --scope user --clis all
```

**Project scope** — only the current working directory:

```bash
cd /path/to/your/project
bash <(curl -fsSL https://raw.githubusercontent.com/mer0mingian/my-harness/main/install.sh) --scope project --clis all
```

Re-running is safe — it is idempotent.

## Update

```bash
git -C ~/.my-harness pull
```

All CLIs see new content immediately — no re-linking needed.

## Where to learn more

Full architecture and task breakdown: [docs/harness-v1-master-plan.md](docs/harness-v1-master-plan.md)

## Platform notes

Tested on Ubuntu/Debian, including WSL2. On Windows, install inside WSL rather than the host — the script uses POSIX symlinks.
