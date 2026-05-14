# Bug Fix Spec: Wrong Agent File Format (.yml instead of .md)

**Status:** Ready for implementation
**Branch:** `harness-sandbox` dev branch
**Severity:** Medium — agents fail to load silently in fresh workspaces
**Story Points:** 2

---

## 1. Bug Description

The `workspace-template/.claude/agents/` directory ships five `.yml` stub files (`arch-specialist.yml`, `dev-specialist.yml`, `qa-specialist.yml`, `review-specialist.yml`, `test-specialist.yml`). Claude Code does **not** load `.yml` files from this directory — it only recognizes `.md` files with YAML frontmatter. As a result, every workspace spawned from the template starts with **zero functional sandbox-local agents**, and users get no warning.

## 2. Root Cause

| Commit     | Change                                                                      |
| ---------- | --------------------------------------------------------------------------- |
| `82b9c85`  | Removed legacy agent stubs from `workspace-template/.claude/agents/`        |
| `50bef80`  | **Regression** — re-added the same agents as `.yml` mock files              |

The regression mistook the agent files for generic config (where `.yml` is fine) rather than Claude Code agent definitions (which require `.md` + frontmatter). The canonical `.md` versions already exist in `harness-tooling` and are delivered via the plugin install path; the sandbox-local stubs are redundant **and** structurally wrong.

## 3. Correct Format (for reference)

Claude Code agents are markdown files with YAML frontmatter:

```markdown
---
name: agent-name
description: Short description of what the agent does
tools: Read, Edit, Bash
---

System prompt body in markdown.
```

`.yml` files in `.claude/agents/` are silently ignored. There is no fallback parser.

## 4. Proposed Fix

**Strategy:** Rely on the `harness-tooling` plugin to deliver agents (matd-* set is canonical). The sandbox template directory exists only as a mount point.

### Actions

| Action  | Target                                                              |
| ------- | ------------------------------------------------------------------- |
| Delete  | `workspace-template/.claude/agents/arch-specialist.yml`             |
| Delete  | `workspace-template/.claude/agents/dev-specialist.yml`              |
| Delete  | `workspace-template/.claude/agents/qa-specialist.yml`               |
| Delete  | `workspace-template/.claude/agents/review-specialist.yml`           |
| Delete  | `workspace-template/.claude/agents/test-specialist.yml`             |
| Keep    | `workspace-template/.claude/agents/.gitkeep` (preserves empty dir)  |
| Document| matd-* agents in `harness-tooling` are canonical; `*-specialist` names from old `harness-agents` are deprecated |

### Scope

- **In scope:** `harness-sandbox/workspace-template/` only.
- **Out of scope:** Existing user workspaces. Users who already spawned a workspace from the broken template can manually delete the stub `.yml` files; no migration tooling needed.

## 5. Prevention

Two-layer guard:

### (a) Pre-commit hook

Add to `harness-sandbox` repo (or workspace root if shared):

```yaml
# .pre-commit-config.yaml
- id: block-yml-agents
  name: Block .yml files in workspace-template/.claude/agents/
  entry: bash -c 'if git diff --cached --name-only | grep -E "workspace-template/\.claude/agents/.*\.ya?ml$"; then echo "ERROR: Claude Code agents must be .md with YAML frontmatter, not .yml"; exit 1; fi'
  language: system
  pass_filenames: false
```

Rationale: catches the mistake at commit time, where it is cheapest to fix.

### (b) README note

Add to `harness-sandbox/workspace-template/.claude/agents/README.md` (or the workspace-template top-level README):

> **Agents directory is intentionally empty.**
> Sandbox-local agents are delivered via the `harness-tooling` plugin (matd-* canonical set).
> If you add an agent here, it **must** be a `.md` file with YAML frontmatter — Claude Code silently ignores `.yml` / `.yaml` files in this directory.

CI lint rule (option b) was considered redundant given the pre-commit hook. "All of the above" (option d) was rejected as overkill.

## 6. Files Affected

```
/home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.claude/agents/
  - arch-specialist.yml      [DELETE]
  - dev-specialist.yml       [DELETE]
  - qa-specialist.yml        [DELETE]
  - review-specialist.yml    [DELETE]
  - test-specialist.yml      [DELETE]
  - .gitkeep                 [KEEP]
```

Plus:

- `harness-sandbox/.pre-commit-config.yaml` (new or amended)
- `harness-sandbox/workspace-template/.claude/agents/README.md` (new) **or** note added to existing workspace-template README

## 7. Validation

After fix, verify:

```bash
ls -A /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.claude/agents/
# Expected output (single line):
# .gitkeep
```

Additional checks:

1. `git status` shows the five `.yml` files as deleted.
2. Pre-commit hook fires on a test commit that re-introduces a `.yml` file under the guarded path.
3. A freshly spawned workspace loads matd-* agents from the plugin (not from `.claude/agents/`).
4. No references to `*-specialist.yml` remain in the repo (`rg "specialist\.yml"` returns nothing).
