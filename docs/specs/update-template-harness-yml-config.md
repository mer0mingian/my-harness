# Spec: Sync Workspace Template `.harness.yml` with Active Workspace

**Status:** Ready for review (no changes applied yet)
**Date:** 2026-05-14
**Scope:** Recommended updates to `harness-sandbox/workspace-template/.harness.yml`
**Related:** `bug-fix-invalid-char-harness-yml.md` (em-dash bug, still unresolved in template)

---

## 1. Objective

Synchronize the template `.harness.yml` (source of truth for new agent-workspaces) with proven values from the active `sta2e-agent-workspace/.harness.yml`, while keeping workspace-specific values parameterized.

**Files compared:**

- Template: `/home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml`
- Active:   `/home/minged01/repositories/sta2e-agent-workspace/.harness.yml`

---

## 2. Side-by-Side Differences

| # | Section | Template (current) | Active workspace | Should template change? |
|---|---------|--------------------|------------------|--------------------------|
| 1 | `workspace.name` (L9) | `<system-name>-agent-workspace` (placeholder) | `sta2e-vtt-agent-workspace` | **No** — workspace-specific, must stay parameterized |
| 2 | `components` (L16) | `[]` with commented examples | Two real components (`sta2e-vtt-lite-system`, `sta2e-vtt-lite`) | **No** — workspace-specific |
| 3 | `external_repos[*].path` (L37,L40) | Relative: `../../harness-tooling`, `../../harness-sandbox` | Absolute: `/home/minged01/repositories/harness-workplace/...` | **No** — template's relative paths are correct (portable across users); active workspace drifted to absolute paths |
| 4 | `external_repos[*].role` (L37,L41) | Uses em-dash `—` | Uses ASCII hyphen `-` | **Yes** — fix em-dashes (see Section 5, ties to existing bug-fix spec) |
| 5 | `plugins[matd].path` (L51) | `../../harness-tooling/.claude/.claude-plugin` (**broken path — directory does not exist**) | `.../harness-tooling/.agents/plugins/matd/.claude-plugin` (correct) | **Yes** — fix template to use `../../harness-tooling/.agents/plugins/matd/.claude-plugin` |
| 6 | `plugins` list (L46-59) | 2 plugins: `matd`, `harness-management-tools` | 4 plugins: adds `harness-cgc-skill`, `harness-deepwiki-skill` | **Yes (partial)** — add `harness-cgc-skill` and `harness-deepwiki-skill` as `enabled: true` defaults (skills aligned with always-on CGC + Litho MCP services) |
| 7 | `plugins[*].path` style (L51,L58) | Relative (`../../harness-tooling/...`) | Absolute | **No** — keep relative in template |
| 8 | `mcp_servers.litho.config.output` (L86) | `docs/deepwiki` | `docs/architecture` | **No (keep `docs/deepwiki`)** — the template's `litho.toml.example` and `README.md` already document that `docs/architecture` is an opt-in override; `docs/deepwiki` is the documented default. Active workspace customized this. |
| 9 | `mcp_servers.litho.config.languages` (L88-91) | `python, typescript, javascript` | `python, javascript` | **No** — keep template's superset (TS is common); workspace can prune |
| 10 | Em-dash characters throughout comments | 26 occurrences of `—` (U+2014) | All ASCII `-` | **Yes** — fix per `bug-fix-invalid-char-harness-yml.md` |
| 11 | `speckit.artifact_dirs.plans` (L266) | `docs/plans` | `plans` | **Discuss** — see Section 4 |
| 12 | `speckit.artifact_dirs.tasks` (L267) | `docs/tasks` | `tasks` | **Discuss** — see Section 4 |
| 13 | `speckit.artifact_dirs.tests` (L268) | `docs/tests` | `tests` | **Discuss** — see Section 4 |
| 14 | `speckit.extensions[harness-tdd-workflow].path` (L290) | `../../harness-tooling/spec-kit-multi-agent-tdd` | Absolute path | **No** — keep relative |
| 15 | `templates.source` (L320) | `../../harness-tooling/.speckit-templates` | Absolute path | **No** — keep relative |
| 16 | `documentation.overview` em-dashes (L332-345) | 14 em-dashes | ASCII hyphens | **Yes** — fix per bug-fix-invalid-char spec |

---

## 3. Recommended Updates to Template

### 3.1 Critical fixes (blocking — break installation today)

**Fix #1: Broken `matd` plugin path (L49-52)**

The current template path `../../harness-tooling/.claude/.claude-plugin` does not exist (`harness-tooling/.claude/` is absent). The correct path matches the structure used by the other plugins:

```yaml
# Before (broken):
- name: matd
  source: local
  path: ../../harness-tooling/.claude/.claude-plugin
  enabled: true

# After:
- name: matd
  source: local
  path: ../../harness-tooling/.agents/plugins/matd/.claude-plugin
  enabled: true
```

**Justification:** Confirmed via `find harness-tooling -name .claude-plugin -type d` — only `.agents/plugins/<name>/.claude-plugin` directories exist. Active workspace already uses the corrected path.

**Fix #2: Em-dashes (26 occurrences)**

Apply the substitution `—` (U+2014) → `-` per the existing `bug-fix-invalid-char-harness-yml.md` spec. Same scope, same file. Should be executed together with this sync.

### 3.2 Recommended additions

**Addition #1: Bundle CGC and Deepwiki skill plugins by default**

Active workspace adds two helper-skill plugins that pair with the always-on `codegraphcontext` and `litho` MCP servers. They are safe defaults — small, local, no auth.

```yaml
# Append after harness-management-tools (line 59):

  # Code Graph Context Skill
  # Guides agents on how to query the cgc MCP server effectively
  - name: harness-cgc-skill
    source: local
    path: ../../harness-tooling/.agents/plugins/harness-cgc-skill/.claude-plugin
    enabled: true

  # Deepwiki / Litho Skill
  # Guides agents on documentation generation workflows
  - name: harness-deepwiki-skill
    source: local
    path: ../../harness-tooling/.agents/plugins/harness-deepwiki-skill/.claude-plugin
    enabled: true
```

**Justification:** These plugins exist in `harness-tooling/.agents/plugins/`, are referenced by the active workspace, and align with the template's always-enabled `codegraphcontext` + `litho` MCP servers. New workspaces should get this guidance out of the box.

### 3.3 Updates to leave as workspace-specific (parameterized in template)

- `workspace.name` — keep placeholder `<system-name>-agent-workspace`
- `components` — keep empty list with commented examples
- `external_repos[*].path` — keep relative (`../../harness-tooling`, `../../harness-sandbox`); the active workspace's absolute paths are a drift bug, not a template improvement
- All `plugins[*].path` and `speckit.extensions[*].path` — keep relative
- `templates.source` — keep relative

### 3.4 Updates to explicitly reject

- `mcp_servers.litho.config.output: docs/architecture` — **do not adopt.** The template documents `docs/deepwiki` as the default in `litho.toml.example` (line 17 explicitly calls out the difference). Workspaces that want a unified `docs/architecture` location override via `litho.toml` per the documented pattern.
- `mcp_servers.litho.config.languages: [python, javascript]` — **do not adopt.** Template superset includes `typescript`; trimming is a per-workspace choice.

---

## 4. Open Question: SpecKit Artifact Directory Layout

The active workspace flattens three directories that the template nests under `docs/`:

| Key | Template | Active | Observation |
|-----|----------|--------|-------------|
| `plans` | `docs/plans` | `plans` | Active uses top-level |
| `tasks` | `docs/tasks` | `tasks` | Active uses top-level |
| `tests` | `docs/tests` | `tests` | Active uses top-level |
| `qa`    | `docs/qa`    | `docs/qa` | Both nested (consistent) |

The template's `documentation.overview` paragraph explicitly references `docs/plans/active/*.md` and `docs/tasks/active/*.md`, suggesting the nested layout is the intended convention.

**Recommendation:** **Keep template values (`docs/plans`, `docs/tasks`, `docs/tests`).** The active workspace appears to have drifted; the inline documentation prose still describes the nested layout. If the team has decided to flatten, that should be a separate documented decision (and `documentation.overview` should be updated to match).

**Decision needed from user:** confirm whether the flattening in the active workspace was intentional. If yes, update template (artifact_dirs + overview prose together). If no, the active workspace should be corrected back to nested.

---

## 5. Interaction with `bug-fix-invalid-char-harness-yml.md`

The em-dash fix and the configuration sync touch the same file and the same lines. **Recommendation:** execute the em-dash fix first (mechanical character substitution, already specified in detail) and then apply the configuration changes from this spec on top. Either:

- (A) Merge: roll both into a single PR titled "Sync template .harness.yml and remove em-dashes", citing both specs.
- (B) Sequence: land bug-fix-invalid-char-harness-yml.md first, then this spec.

Option (A) is recommended for minimal review churn since both edits are scoped to the same file and neither blocks the other.

---

## 6. Summary of Recommended Template Edits

| # | Line(s) | Change | Severity |
|---|---------|--------|----------|
| 1 | L51 | Fix `matd` plugin path: `.claude/.claude-plugin` → `.agents/plugins/matd/.claude-plugin` | **Critical (broken today)** |
| 2 | After L59 | Add `harness-cgc-skill` plugin entry, enabled | Recommended |
| 3 | After L59 | Add `harness-deepwiki-skill` plugin entry, enabled | Recommended |
| 4 | 26 lines | Replace em-dash `—` with ASCII `-` | **Critical (parser breakage)** |

All other differences are either workspace-specific (correctly parameterized) or drift in the active workspace that should not propagate.

---

## 7. Validation Steps (post-change)

1. **YAML parses cleanly under strict parser:**
   ```bash
   yamllint -d "{rules: {non-printable-characters: enable}}" \
     harness-sandbox/workspace-template/.harness.yml
   ```
   Expected: zero warnings.

2. **No em-dash characters remain:**
   ```bash
   grep -nP '\x{2014}' harness-sandbox/workspace-template/.harness.yml
   ```
   Expected: no output.

3. **All plugin paths resolve from a sample workspace location:**
   ```bash
   cd /tmp && mkdir -p test-workspace && cd test-workspace
   for p in $(yq '.plugins[].path' \
       /home/minged01/repositories/harness-workplace/harness-sandbox/workspace-template/.harness.yml); do
     test -d "$p" && echo "OK: $p" || echo "MISSING: $p"
   done
   ```
   Expected: all four plugin paths report OK when the workspace lives at the documented `harness-workplace/<workspace>/` depth (two levels above `harness-tooling`).

4. **Smoke test: spin up a fresh workspace from template:**
   ```bash
   harness init test-workspace --template workspace-template
   cd test-workspace && harness up
   ```
   Expected: all four plugins install without "path not found" errors; `cgc` and `litho` MCP servers start.

5. **Reference check:** confirm `documentation.overview` (workflow phase descriptions) remains consistent with `artifact_dirs` layout after any directory changes.

---

## 8. Out of Scope

- Refactoring the active `sta2e-agent-workspace` to use relative paths (separate hygiene task).
- Adding new MCP servers or plugins not already present in either file.
- Changing the always-enabled set (`codegraphcontext`, `litho`, `aws_docs`).
- Restructuring `speckit.extensions` ordering or sources.
