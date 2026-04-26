# workflow-runtime-baseline.md
**Phase R research output — 2026-04-23**
Covers D1 (frontmatter inventory), D2 (Python 3.13 verification), D3 (hook API surfaces).

---

## D1 — Frontmatter Inventory

### File counts

| Location | Count |
|---|---|
| `.agents/agents/*.md` | 14 agents |
| `.agents/skills/*/SKILL.md` | 52 skills |
| `.agents/commands/*.md` | 5 commands |

---

### D1.1 — Agent frontmatter fields

**Observed fields** (across all 14 agents):

| Field | Status | Notes |
|---|---|---|
| `name` | Required — all 14 present | |
| `description` | Required — all 14 present | |
| `skills` | Required — all 14 present | Claude-Code-style list |
| `permission` | Required — all 14 present | Block present in all; see schema split below |
| `mode` | Optional / inconsistent | Present in 10, absent in `daniels-architect`, `daniels-orchestrator`, `python-dev` |
| `model` | Absent in all 14 | No agent declares a model; inherited from session default |
| `temperature` | Rare | Only `daniels-architect.md` sets `temperature: 0.1` |
| `source` | Rare | Set to `local` on 5 `stdd-*` subagents; absent elsewhere |

**`permission` block — two incompatible schemas in use:**

| Schema | Agents | Notes |
|---|---|---|
| `permission.skill` (OpenCode-style) | `c4-*.md`, `daniels-*.md`, `python-dev.md`, `tdd-*.md` (9 agents) | Key is a prefix or glob; value is `allow`/`deny`. Matches the dual-frontmatter convention in `CLAUDE.md`. |
| `permission.read/write/edit/bash` (file-ACL-style) | `stdd-critical-thinking-subagent.md`, `stdd-qa-subagent.md`, `stdd-solution-design-subagent.md`, `stdd-specification-agent.md`, `stdd-workflow-orchestrator.md` (5 agents) | File-path-based ACL. Different schema — no `permission.skill` key present at all. |

**Phase 0 implication:** The `Agent` pydantic model must accommodate both schemas. The `stdd-*` file-ACL agents predate the dual-frontmatter convention. They carry `skills:` lists (satisfying the Claude side) but their `permission` block cannot be read as `permission.skill` by the resolver.

---

### D1.2 — Skill frontmatter fields (SKILL.md)

**Observed fields:**

| Field | Status | Notes |
|---|---|---|
| `name` | Required per agentskills.io — present in 51/52 | One outlier: `alpine-js-patterns` |
| `description` | Required per agentskills.io — present in 51/52 | Same outlier |
| `metadata` | Rare / optional | Only seen in the requirements doc example; absent in all 52 live skills |
| `compatibility` | Rare | Only in example snippets; absent in all 52 live skills |

**Outlier — `alpine-js-patterns/SKILL.md`:** No YAML frontmatter at all. Opens with a bare markdown `#` heading. Fails agentskills.io spec. Will cause the validator to error.

---

### D1.3 — Command frontmatter fields

**Observed fields:**

| Field | Status | Notes |
|---|---|---|
| `description` | Present in all 5 | |
| `agent` | Present in all 5 | Names an agent; agent names don't always resolve to files (e.g. `daniels-workflow-orchestrator` is the frontmatter name, not the filename `stdd-workflow-orchestrator.md`) |
| `subtask` | Optional | Present in 4 of 5; absent in `stdd-feat-workflow.md` |
| `return` | Conditional | Present in 4 of 5; absent in `stdd-feat-workflow.md` (which delegates to sub-commands) |

Commands do **not** carry `allowed-tools` or `argument-hint` — these are the fields the planned `Command` pydantic schema will need to add as optional fields.

---

### D1.4 — Outlier summary (Phase 0 priorities)

| Outlier | File(s) | Impact on Phase 0 schema |
|---|---|---|
| No frontmatter at all | `alpine-js-patterns/SKILL.md` | Validator must handle gracefully; emit actionable error. |
| `Specification.md` at skills root (not in a subdir) | `.agents/skills/Specification.md` | Not a skill; a spec document. No SKILL.md. Should be moved to `docs/`. Will confuse glob-based scanners. |
| `permission` uses file-ACL schema (no `permission.skill`) | 5 `stdd-*` agents | Schema needs a union type or separate model; resolver must detect schema variant. |
| `name` ≠ directory name (19 mismatches) | e.g. `arch-api-design-principles/` has `name: api-design-principles` | agentskills.io requires name to match the directory. Either the dirs or the `name:` fields are wrong. All 19 mismatches follow the same pattern: directory carries the workflow prefix, `name:` field drops it. Phase 0 schema decision needed: enforce dir==name, or allow mismatch with a warning? |
| Skills without a recognised workflow prefix | `alpine-js-patterns`, `brainstorming`, `context-*`, `database-migration`, `databases`, `docker-expert`, `filesystem-context`, `mcp-builder`, `mobile-android-design`, `multi-agent-patterns`, `skill-auditor`, `skill-creator` (≈16 skills) | Covered by the existing "Skill-naming audit deferred" note in `CLAUDE.md`. Not blockers for Phase 0, but the resolver's glob expansion must not assume all skills have a prefix. |
| `python-packaging/SKILL.md` contains two `name:` fields | `name: Build wheels` and `name: Publish to PyPI` appear inside the skill body (GitHub Actions step names, not frontmatter) | False positive from the name scanner. The frontmatter `name: python-packaging` is correct. Validator must scope the name check to frontmatter only. |

---

### D1.5 — agentskills.io naming compliance

Rules: lowercase, hyphens only, ≤64 chars, no `anthropic`, no `claude`.

| Check | Result |
|---|---|
| Lowercase | All 51 skills with `name:` field pass |
| Hyphens only | All pass |
| ≤64 chars | All pass |
| No `anthropic` or `claude` | All pass |
| `name:` field matches directory name | 19 mismatches (see §D1.4) — consistent pattern, not random drift |

---

## D2 — Python 3.13 Verification

**Finding: Python 3.13 IS present. The Python floor decision is unblocked.**

### Trace

1. `harness-sandbox/Dockerfile` extends `ghcr.io/nvidia/openshell-community/sandboxes/gemini:latest` (the tag used at scaffold time; pinned commit `36c558e929359830bf272868f42de7bf47bd2716` recorded via LABEL).
2. The Gemini-layer Dockerfile (`sandboxes/gemini/Dockerfile` at that commit) itself extends `ghcr.io/nvidia/openshell-community/sandboxes/base:latest`.
3. The base-layer Dockerfile (`sandboxes/base/Dockerfile` at that commit) installs Python via `uv`:
   ```dockerfile
   COPY --from=ghcr.io/astral-sh/uv:0.10.8 /uv /usr/local/bin/uv
   RUN uv python install 3.13 && \
       ln -s $(uv python find 3.13) /usr/local/bin/python3 && \
       ln -s $(uv python find 3.13) /usr/local/bin/python && \
       uv cache clean
   ```
   A venv is also seeded with Python 3.13: `uv venv --python 3.13 --seed /sandbox/.venv`.
4. `uv` is explicitly present (`uv tool install codegraphcontext` is called in the harness Dockerfile), confirming `uv` survives to the final image.

**No mitigation paths are required.** The three options listed in §13 of the plan are moot; do not pick one.

---

## D3 — Hook API Surfaces

### Claude Code hooks

Source: official Claude Code docs (https://code.claude.com/docs/en/hooks), verified 2026-04-23.

**Relevant events for the runtime plugin:**

| Event | Matcher | Blocks on exit 2? | Use in runtime plugin |
|---|---|---|---|
| `PreToolUse` | Tool name (exact, pipe-sep, or regex) | Yes — denies tool call | Primary enforcement hook; deny tools outside phase allowlist |
| `PostToolUse` | Tool name | Yes — stops agentic loop | File-pattern check; `git restore` on violation |
| `SessionStart` | `startup\|resume\|clear\|compact` | No | Resolver: expand globs, emit ACLs on session start |

**Blocking contract (PreToolUse):**

- Exit 2 + stderr message = tool denied; stderr shown to Claude/user as block reason.
- Exit 0 + JSON `hookSpecificOutput.permissionDecision: "deny"` = structured deny (preferred; allows reason string).
- Exit 0 + JSON `hookSpecificOutput.permissionDecision: "allow"` or empty = allow.

**Matcher syntax:**

| Pattern | Example | Behaviour |
|---|---|---|
| Exact string | `Bash` | Matches that tool only |
| Pipe-separated | `Write\|Edit\|MultiEdit` | Matches any of the listed tools |
| Regex | `^mcp__.*` | Full regex; anchored with `^`/`$` |
| Omitted / `"*"` | — | Matches all tools |

**Hook config location:** `.claude/settings.json` → `hooks` array. Fragment merged via `settings.fragment.json` at install time.

**Additional events available (not used in v1 but notable):**

- `UserPromptSubmit` — block prompts (exit 2).
- `SubagentStart` / `SubagentStop` — lifecycle of spawned subagents.
- 26 total events documented; the above three are the runtime plugin's v1 surface.

---

### OpenCode plugin host (froggy / `@opencode-ai/plugin`)

**Finding: "froggy" as a standalone package does not exist at the expected GitHub repos. The canonical OpenCode plugin SDK is `@opencode-ai/plugin` (npm), and community packages like `opencode-froggy` are thin wrappers built on top of it.**

- Official plugin docs: https://opencode.ai/docs/plugins/
- Community wrapper on npm: `opencode-froggy` (v0.10.1) — provides pre-built agents/skills on top of `@opencode-ai/plugin`; not the plugin host itself.
- Plugin host is the OpenCode CLI itself, which loads TypeScript plugins from `.opencode/plugin/` or npm.

**OpenCode hook event names (complete list from official docs):**

| Category | Events |
|---|---|
| Tool | `tool.execute.before`, `tool.execute.after` |
| Session | `session.created`, `session.updated`, `session.deleted`, `session.idle`, `session.error`, `session.status`, `session.compacted`, `session.diff` |
| Message | `message.updated`, `message.removed`, `message.part.updated`, `message.part.removed` |
| Permission | `permission.asked`, `permission.replied` |
| Command | `command.executed` |
| File | `file.edited`, `file.watcher.updated` |
| Shell | `shell.env` |
| LSP | `lsp.client.diagnostics`, `lsp.updated` |
| TUI | `tui.prompt.append`, `tui.command.execute`, `tui.toast.show` |
| Other | `installation.updated`, `server.connected`, `todo.updated` |

**Tool blocking pattern (OpenCode):**

```typescript
"tool.execute.before": async (input, output) => {
  if (input.tool === "write" && !allowedPath(output.args.filePath)) {
    throw new Error("Write outside phase allowlist blocked")
  }
}
```
Throwing inside `tool.execute.before` blocks the tool call. OpenCode plugins are TypeScript (Bun runtime), not Python.

**Phase 0 / Phase 8 implication:** The OpenCode adapter (`adapters/opencode.py`) cannot call Python hooks directly. It must either (a) shell out to the Python hook script from a TypeScript wrapper, or (b) the plugin ships a thin `.opencode/plugin/*.ts` file that shells out to the same Python hook binary. The adapter seam boundary is: Python core logic → thin TS shell wrapper → OpenCode hook event. This design choice should be confirmed before Phase 8 starts.

**Maintenance status:** `@opencode-ai/plugin` is actively maintained (OpenCode AI org). No deprecation signals found as of 2026-04-23.
