# Bug Fix Spec: Claude Code Startup Errors

**Status:** Ready for implementation
**Branch:** `harness-tooling` main
**Severity:** High — every Claude Code session launched from the parent workspace prints plugin-load errors at startup
**Story Points:** 2

---

## 1. Bug Description

When Claude Code starts in `/home/minged01/repositories/harness-workplace/` (or any subdirectory that inherits the `my-plugins` marketplace registration), it emits startup errors related to the **`all-my-skills@my-plugins`** plugin. The marketplace claims a `plugin.json` exists at a path that is not present on disk, so the plugin loader fails before any skill/agent/command from the local marketplace can be registered.

A separate `superpowers@superpowers-marketplace` version-pin error has been observed in the same startup output. It is **host-only** (the host has `5.1.0` cached while the marketplace pins `4.0.0`) and is **out of scope** for this fix — superpowers must not be installed inside the sandbox at all (see Section 6).

## 2. Root Cause

The local marketplace manifest at:

```
/home/minged01/repositories/harness-workplace/harness-tooling/.claude-plugin/marketplace.json
```

declares the `all-my-skills` plugin with:

```json
{
  "name": "all-my-skills",
  "source": "./.claude/plugins/all-my-skills/.claude-plugin/plugin.json",
  "description": "Daniel's STDD + orchestration + review workflows for Claude Code"
}
```

The resolved absolute path is:

```
/home/minged01/repositories/harness-workplace/harness-tooling/.claude/plugins/all-my-skills/.claude-plugin/plugin.json
```

**This path does not exist.** The repository has no `.claude/plugins/` directory at all. The actual skills/agents/commands tree lives under `.agents/`:

```
harness-tooling/
├── .claude-plugin/
│   └── marketplace.json        # the registration
├── .agents/
│   ├── skills/                  # 60+ skill directories
│   ├── agents/                  # daniels-orchestrator, matd-*, ...
│   ├── commands/                # matd-* command files
│   └── plugins/                 # 6 sibling plugins (harness-agents, matd, etc.)
│       └── …/.claude-plugin/plugin.json
```

There is no `plugin.json` anywhere that matches the `all-my-skills` declaration, so the loader cannot resolve the plugin source.

### Evidence

Found `plugin.json` files under `harness-tooling/`:

```
.agents/plugins/harness-agents/plugin.json
.agents/plugins/harness-management-tools/.claude-plugin/plugin.json
.agents/plugins/matd/.claude-plugin/plugin.json
.agents/plugins/harness-cgc-skill/.claude-plugin/plugin.json
.agents/plugins/harness-workflow-runtime/.claude-plugin/plugin.json
.agents/plugins/harness-deepwiki-skill/.claude-plugin/plugin.json
```

None at the declared `./.claude/plugins/all-my-skills/.claude-plugin/plugin.json`.

Installation record (`~/.claude/plugins/installed_plugins.json`) confirms the loader is still trying:

```json
"all-my-skills@my-plugins": [
  {
    "scope": "local",
    "installPath": ".../my-plugins/all-my-skills/5dd8b81c42af",
    "version": "5dd8b81c42af",
    "projectPath": "/home/minged01/repositories/harness-workplace"
  }
]
```

…but the cache directory `~/.claude/plugins/cache/my-plugins/all-my-skills/5dd8b81c42af/` is empty — the stale install snapshot is not a viable source either.

## 3. Proposed Fix

Bring the `marketplace.json` declaration in line with the actual repo layout. Two viable options:

### Option A (recommended) — Add the missing manifest

Create `.claude-plugin/plugin.json` next to the existing `marketplace.json` and treat `harness-tooling/` itself as the `all-my-skills` plugin root. This is the lowest-churn fix and matches how the other six plugins under `.agents/plugins/*` are structured.

1. Create `harness-tooling/.claude-plugin/plugin.json` with the minimal manifest:
   ```json
   {
     "name": "all-my-skills",
     "version": "0.1.0",
     "description": "Daniel's STDD + orchestration + review workflows for Claude Code",
     "skills": ".agents/skills",
     "agents": ".agents/agents",
     "commands": ".agents/commands"
   }
   ```
   (Adjust field names/structure to match the format used by the working sibling plugins under `.agents/plugins/*/.claude-plugin/plugin.json`.)

2. Update `marketplace.json` to point at this manifest:
   ```diff
   - "source": "./.claude/plugins/all-my-skills/.claude-plugin/plugin.json",
   + "source": "./.claude-plugin/plugin.json",
   ```

### Option B — Move/rename content to match the declared path

Create the directory tree `.claude/plugins/all-my-skills/.claude-plugin/` and place a `plugin.json` there that re-roots skills/agents/commands at the repo's `.agents/` content (via relative paths or by moving files). Higher churn; only choose this if there's a separate reason to introduce `.claude/plugins/` as a convention.

**Decision: go with Option A** unless the team has already standardised on `.claude/plugins/<name>/` elsewhere.

After the fix:

```bash
# Force the marketplace cache to refresh the plugin
/plugin marketplace update my-plugins
/plugin reinstall all-my-skills@my-plugins
```

(Exact command names depend on the Claude Code CLI version; `/plugin` subcommands cover marketplace refresh and reinstall.)

## 4. Note on Superpowers (Out of Scope)

Startup logs also show a `superpowers@superpowers-marketplace` version mismatch (marketplace pins `4.0.0`, host cache holds `5.1.0`). This is a **host-only** plugin and is intentionally **not** installed inside the sandbox. No change is needed in this repo for that error; it should be silenced at the host level (uninstall/repin on the host) outside this spec.

## 5. Model Pin

`settings.json` intentionally leaves the model unpinned. No change.

## 6. Validation Steps

1. **Static check** — confirm the manifest resolves:
   ```bash
   test -f /home/minged01/repositories/harness-workplace/harness-tooling/.claude-plugin/plugin.json && echo OK
   ```
2. **Marketplace check** — `marketplace.json` `source` for `all-my-skills` points at an existing file:
   ```bash
   jq -r '.plugins[] | select(.name=="all-my-skills") | .source' \
     /home/minged01/repositories/harness-workplace/harness-tooling/.claude-plugin/marketplace.json
   ```
3. **Clean reinstall** — remove stale install cache for `all-my-skills`, then refresh:
   ```bash
   rm -rf ~/.claude/plugins/cache/my-plugins/all-my-skills
   # then in Claude Code:
   /plugin marketplace update my-plugins
   /plugin reinstall all-my-skills@my-plugins
   ```
4. **Startup check** — launch a fresh Claude Code session in `/home/minged01/repositories/harness-workplace/`. Expected output:
   - No `all-my-skills` load error.
   - Skills from `.agents/skills/` appear in `/skills` (or equivalent listing).
5. **Smoke test** — invoke one skill that lives under `.agents/skills/` (e.g. `stdd-test-driven-development`) and confirm it loads.

## 7. Out of Scope

- Superpowers host-side version conflict (see Section 4).
- Restructuring the six sibling plugins under `.agents/plugins/*` — they already resolve correctly.
- Model pinning in `settings.json`.
