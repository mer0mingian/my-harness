# my-harness

Personal harness for project, architecture, and code-knowledge management. Opinionated skills, agents, and slash commands shared across **Claude Code**, **OpenCode**, and **Gemini CLI**.

The canonical content lives in [.agents/](.agents/) and is used by every CLI via symlinks — edit once, available everywhere.

```
.agents/
├── skills/      # Claude-style skills (one dir each, with SKILL.md)
├── agents/      # subagent definitions (.md)
└── commands/    # slash commands in mixed formats:
                 #   *.md             → Claude Code
                 #   *.toml           → OpenCode
                 #   *.gemini.toml    → Gemini CLI
```

## Quickstart

Pick a scope and run the one-liner. The script clones this repo to `~/.my-harness/` (source of truth) and symlinks the three subdirs into each CLI's config path.

**User scope** — available in every project on this machine:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/mer0mingian/my-harness/main/install.sh) --scope user --clis all
```

**Project scope** — only the current working directory:

```bash
cd /path/to/your/project
bash <(curl -fsSL https://raw.githubusercontent.com/mer0mingian/my-harness/main/install.sh) --scope project --clis all
```

**Interactive** (prompts for scope and CLIs):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/mer0mingian/my-harness/main/install.sh)
```

### Flags

| Flag | Values | Default | Meaning |
|---|---|---|---|
| `--scope` | `user`, `project` | *(prompt)* | Where symlinks are placed. |
| `--clis` | `claude`, `opencode`, `gemini`, `all` (comma-list) | *(prompt)* | Which CLIs to wire up. |
| `--src-dir` | path | `~/.my-harness` | Where to clone/update the source of truth. |
| `--ssh` / `--https` | flag | `--https` | Clone via SSH (needs keys configured) or HTTPS. |

Re-running the script is safe — it's idempotent. Existing symlinks pointing at the correct source are left alone; real dirs in the way are backed up as `<name>.bak.<timestamp>`.

## What the script does

Per CLI, it creates these symlinks. **User scope** paths shown — **project scope** uses `./.claude/`, `./.opencode/`, `./.gemini/` in the current directory instead.

| CLI | Target (user scope) | → | Source |
|---|---|---|---|
| Claude Code | `~/.claude/skills` | → | `<src>/.agents/skills` |
| Claude Code | `~/.claude/agents` | → | `<src>/.agents/agents` |
| Claude Code | `~/.claude/commands` | → | `<src>/.agents/commands` |
| OpenCode | `~/.config/opencode/skills` | → | `<src>/.agents/skills` |
| OpenCode | `~/.config/opencode/agent` | → | `<src>/.agents/agents` |
| OpenCode | `~/.config/opencode/command` | → | `<src>/.agents/commands` |
| Gemini CLI | `~/.gemini/commands` | → | `<src>/.agents/commands` |

`<src>` defaults to `~/.my-harness`. The commands directory is shared across all three CLIs — each one only reads files in its own format (`.md`, `.toml`, `.gemini.toml`) and ignores the rest.

## Manual install

If you'd rather not run a downloaded script, do the same thing by hand:

```bash
# 1. Clone the source of truth (once, globally).
git clone https://github.com/mer0mingian/my-harness.git ~/.my-harness

# 2. Symlink into each CLI you use. User scope example:
SRC=~/.my-harness/.agents

# Claude Code
mkdir -p ~/.claude
ln -sf "$SRC/skills"   ~/.claude/skills
ln -sf "$SRC/agents"   ~/.claude/agents
ln -sf "$SRC/commands" ~/.claude/commands

# OpenCode
mkdir -p ~/.config/opencode
ln -sf "$SRC/skills"   ~/.config/opencode/skills
ln -sf "$SRC/agents"   ~/.config/opencode/agent
ln -sf "$SRC/commands" ~/.config/opencode/command

# Gemini CLI
mkdir -p ~/.gemini
ln -sf "$SRC/commands" ~/.gemini/commands
```

For **project scope**, replace the target roots with `./.claude`, `./.opencode`, `./.gemini` in your project directory.

## Update

```bash
git -C ~/.my-harness pull
```

All CLIs see the new content immediately — no re-linking needed.

## Uninstall

Symlinks only; nothing is copied. Remove per CLI:

```bash
# User scope
rm ~/.claude/{skills,agents,commands}
rm ~/.config/opencode/{skills,agent,command}
rm ~/.gemini/commands

# Source of truth (optional)
rm -rf ~/.my-harness
```

For project scope, remove the matching links under `./.claude`, `./.opencode`, `./.gemini`.

## Platform notes

Tested on Ubuntu/Debian, including WSL2. On Windows, install inside WSL rather than the host — the script uses POSIX symlinks.
