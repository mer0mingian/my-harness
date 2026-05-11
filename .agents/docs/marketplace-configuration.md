# Marketplace Configuration Guide

Comprehensive documentation for the manifest-based overlay resolution system that controls which skills, agents, commands, and plugins are available to CLIs in the harness sandbox.

## Overview

### What is the Marketplace?

The **marketplace** is a curated collection of skills, agents, commands, and plugins living in `harness-tooling/.agents/`. Projects opt into marketplace assets via a **manifest-based overlay system** that:

- Allows granular per-project selection of tools
- Supports named bundles for common workflows
- Enables private overrides without modifying committed manifests
- Works across multiple CLIs (Claude Code, OpenCode, Gemini)

### Core Principles

1. **Manifest-based opt-in** — No tool is available by default; projects explicitly declare what they need
2. **Three-layer merge** — Workspace defaults → committed project config → private local overrides
3. **Union semantics** — Lists merge additively; later layers augment earlier ones
4. **Bundle expansion** — Named bundles expand to concrete asset lists before exclusion
5. **Container-absolute symlinks** — Overlay contains symlinks to container paths for bind-mount safety

## Manifest Structure

### Complete Schema

```yaml
# .harness.yaml (committed) or .harness.local.yaml (gitignored)

# Which agent CLIs to populate (default: all three)
clis:
  - claude
  - opencode
  - gemini

# Named bundles (expanded first)
bundles:
  - pries-core
  - essentials

# Direct asset references (unioned with bundle expansions)
skills:
  - code-graph-context
  - architecture-wiki

agents:
  - custom-agent

commands:
  - custom-command

plugins:
  - matd
  - harness-cgc-skill

# Subtraction (applied after all unions)
exclude:
  skills:
    - unwanted-skill
  agents:
    - noisy-agent
  commands:
    - deprecated-command
  plugins:
    - legacy-plugin
```

### Field Descriptions

| Field | Type | Purpose | Default |
|-------|------|---------|---------|
| `clis` | list | Which CLI configs to populate | `[claude, opencode, gemini]` |
| `bundles` | list | Named bundle references (see bundles.yaml) | `[]` |
| `skills` | list | Direct skill references (filenames under `.agents/skills/`) | `[]` |
| `agents` | list | Direct agent references (filenames under `.agents/agents/`) | `[]` |
| `commands` | list | Direct command references (filenames under `.agents/commands/`) | `[]` |
| `plugins` | list | Plugin directory names under `.agents/plugins/` | `[]` |
| `exclude` | object | Asset subtraction applied last | `{skills:[], agents:[], commands:[], plugins:[]}` |

### Filename Resolution

For skills, agents, and commands, the resolver:
1. First looks for an exact match (e.g., `code-graph-context`)
2. Falls back to `<name>.md` if the exact match doesn't exist (e.g., `code-graph-context.md`)
3. Reports an error if neither exists

**Example:**
```yaml
skills:
  - code-graph-context  # Resolves to code-graph-context.md if found
  - custom-skill        # Resolves to custom-skill/ if it's a directory
```

## Resolution Flow

### Five-Stage Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Load profiles/default.yaml (workspace-wide defaults)    │
│    - Defines default CLIs [claude, opencode, gemini]       │
│    - Empty bundles/skills/agents/commands/plugins          │
└─────────────────────────────────────┬───────────────────────┘
                                      ↓ union merge (lists combine)
┌─────────────────────────────────────────────────────────────┐
│ 2. Load ${PROJECT}/.harness.yaml (committed config)        │
│    - Project-specific bundles and direct references        │
│    - Checked into version control                          │
└─────────────────────────────────────┬───────────────────────┘
                                      ↓ union merge
┌─────────────────────────────────────────────────────────────┐
│ 3. Load ${PROJECT}/.harness.local.yaml (private overrides) │
│    - Gitignored developer-specific additions               │
│    - Useful for experimental skills or local tools         │
└─────────────────────────────────────┬───────────────────────┘
                                      ↓ bundle expansion
┌─────────────────────────────────────────────────────────────┐
│ 4. Expand bundles via .agents/configs/bundles.yaml         │
│    - Each bundle name → {skills, agents, commands, plugins}│
│    - Unknown bundle = hard error                           │
│    - Apply exclude: subtraction                            │
└─────────────────────────────────────┬───────────────────────┘
                                      ↓ validation & symlinking
┌─────────────────────────────────────────────────────────────┐
│ 5. Build overlay at ${HARNESS_OVERLAY_PATH}                │
│    - Per-CLI subdirs: overlay/{claude,opencode,gemini}/    │
│    - Symlinks to /workspace/marketplace/.agents/...        │
│    - Overlay bind-mounted read-only into container         │
└─────────────────────────────────────────────────────────────┘
```

### Union Merge Rules

**For lists** (clis, bundles, skills, agents, commands, plugins):
- Elements from all three layers combine
- Duplicates collapse via `unique`
- Order is not guaranteed

**For scalars** (not used in current schema):
- Later layers override earlier ones

**For exclude** (special case):
- Objects merge (layer 1 `*` layer 2 `*` layer 3)
- Subtraction happens **after** all union merges and bundle expansion

### Execution

Host-side script: `harness-sandbox/bin/harness-resolve`

**Environment inputs:**
```bash
PROJECT_PATH=/path/to/project              # Required
MARKETPLACE_PATH=/path/to/harness-tooling  # Required
HARNESS_OVERLAY_PATH=./.harness-overlay    # Optional (default)
HARNESS_PROFILE_FILE=profiles/default.yaml # Optional (default)
```

**Invocation (from harness sandbox bin/harness):**
```bash
PROJECT_PATH="${PROJECT_DIR}" \
MARKETPLACE_PATH="${MARKETPLACE_PATH}" \
HARNESS_OVERLAY_PATH="${OVERLAY_DIR}" \
  "${SANDBOX_ROOT}/bin/harness-resolve"
```

**Output:**
```
[harness-resolve] overlay built at: ./.harness-overlay
[harness-resolve] CLIs:     claude, opencode, gemini
[harness-resolve] bundles:  pries-core
[harness-resolve] skills:   9
[harness-resolve] agents:   5
[harness-resolve] commands: 4
[harness-resolve] plugins:  1
```

## Bundle System

### What are Bundles?

**Bundles** are named collections of skills, agents, commands, and plugins defined in `harness-tooling/.agents/configs/bundles.yaml`. They provide workflow-aligned presets for common use cases.

### Available Bundles

#### pries-core

PRIES-aligned workflow: **P**M → **R**equirements → **I**mplement → **E**xplore → **S**implify

**Contents:**
```yaml
pries-core:
  skills:
    - review-simplify-complexity
    - review-check-correctness
    - review-differential-review
    - review-orchestrate-dual-review
    - orchestrate-executing-plans
    - orchestrate-subagent-driven-development
    - general-verification-before-completion
  agents:
    - pries-pm
    - pries-make
    - pries-test
    - pries-check
    - pries-simplify
  commands:
    - pries-implement
    - pries-validate
    - pries-review-only
    - pries-test-only
  plugins:
    - harness-workflow-runtime
```

**Use when:** Following PRIES methodology for feature development

#### essentials

General-purpose review, simplify, and debugging skills for ad-hoc development.

**Contents:**
```yaml
essentials:
  skills:
    - review-simplify-complexity
    - review-check-correctness
    - review-differential-review
    - review-systematic-debugging
    - general-verification-before-completion
    - general-finishing-a-development-branch
    - general-git-guardrails-claude-code
  agents:
    - tdd-code-reviewer
  commands: []
  plugins: []
```

**Use when:** Working without a strict workflow but need quality guardrails

### Creating Custom Bundles

Add entries to `harness-tooling/.agents/configs/bundles.yaml`:

```yaml
bundles:
  my-custom-bundle:
    skills:
      - skill-one
      - skill-two
    agents:
      - my-agent
    commands:
      - my-command
    plugins:
      - my-plugin
```

**Validation:**
- All referenced assets must exist under `harness-tooling/.agents/{skills,agents,commands,plugins}/`
- `harness-resolve` fails loudly on missing items

### Mixing Bundles with Direct References

Bundles and direct lists **union**:

```yaml
bundles:
  - pries-core          # Brings in 9 skills, 5 agents, 4 commands, 1 plugin

skills:
  - code-graph-context  # Added on top of pries-core skills

exclude:
  skills:
    - review-orchestrate-dual-review  # Remove from final set
```

**Result:** All pries-core skills + code-graph-context, minus review-orchestrate-dual-review

## Plugin System

### What are Plugins?

Plugins are **self-contained directories** under `harness-tooling/.agents/plugins/` that can bundle skills, agents, commands, or MCP servers with metadata. They use the `.claude-plugin/plugin.json` manifest format.

### Plugin Structure

```
harness-tooling/.agents/plugins/
├── matd/
│   └── .claude-plugin/
│       └── plugin.json         # Required manifest
├── harness-cgc-skill/
│   └── .claude-plugin/
│       └── plugin.json
└── harness-workflow-runtime/
    └── .claude-plugin/
        └── plugin.json
```

### Plugin Manifest Format

**Minimal example (metadata-only):**
```json
{
  "name": "harness-workflow-runtime",
  "version": "0.1.0",
  "description": "Runtime plugin for multi-agent CLI workflows",
  "author": "Daniel Mingers",
  "license": "MIT"
}
```

**With skill references:**
```json
{
  "name": "harness-cgc-skill",
  "version": "1.0.0",
  "description": "CodeGraphContext skill for querying code graphs",
  "author": "Daniel Minges",
  "skills": "../../skills/code-graph-context/"
}
```

**With multiple asset types:**
```json
{
  "name": "matd",
  "version": "1.0.0",
  "description": "Multi-Agent Test-Driven Development workflow",
  "author": "Daniel Minges",
  "agents": "../../../agents/",
  "skills": "../../../skills/"
}
```

### Path Resolution in plugin.json

**All paths are relative to the `.claude-plugin/` directory:**

```
harness-tooling/.agents/
├── plugins/
│   └── matd/
│       └── .claude-plugin/
│           └── plugin.json       # CWD for path resolution
├── skills/                       # ../../../skills/
├── agents/                       # ../../../agents/
└── commands/                     # ../../../commands/
```

**Examples:**
| `plugin.json` path | Resolved target |
|-------------------|-----------------|
| `"../../skills/code-graph-context/"` | `.agents/skills/code-graph-context/` |
| `"../../../agents/"` | `.agents/agents/` (directory of agents) |
| `"../../skills/custom.md"` | `.agents/skills/custom.md` (single file) |

### Available Plugins

| Plugin | Purpose | Contents |
|--------|---------|----------|
| `matd` | Multi-Agent TDD workflow for Claude Code | Agents + skills directories |
| `harness-cgc-skill` | CodeGraphContext MCP integration | Single skill reference |
| `harness-workflow-runtime` | Workflow state machine and enforcement | Metadata-only runtime |
| `harness-deepwiki-skill` | DeepWiki architecture documentation | (structure TBD) |

**Note on matd:** This is the **Claude Code plugin** for MATD workflow. There is also a separate **SpecKit extension** (`spec-kit-multi-agent-tdd/`) that implements the same MATD methodology for the SpecKit CLI. They share conceptual design but are distinct implementations. See [AGENTS.md](../../AGENTS.md) for details on the two artifacts.

### Plugin Installation

**In .harness.yaml:**
```yaml
plugins:
  - matd
  - harness-cgc-skill
```

**Resolution:**
1. Plugin directory name looked up under `.agents/plugins/`
2. `.claude-plugin/plugin.json` loaded
3. Paths resolved relative to `.claude-plugin/` location
4. Symlinks created in overlay for CLI consumption

## Path Resolution Details

### Container Path Mapping

The overlay directory (`${HARNESS_OVERLAY_PATH}`, default `.harness-overlay/`) is bind-mounted **read-only** into the container at `/opt/harness-overlay`.

**Symlink targets** in the overlay use **container-absolute paths**:

```bash
# Host structure
.harness-overlay/claude/skills/code-graph-context.md
  → /workspace/marketplace/.agents/skills/code-graph-context.md

# Container runtime
/opt/harness-overlay/claude/skills/code-graph-context.md
  → /workspace/marketplace/.agents/skills/code-graph-context.md
      (bind mount from host harness-tooling/)
```

### Why Container Paths?

1. **Bind-mount safety** — Symlinks resolve correctly inside the container regardless of host path structure
2. **Cross-platform** — Works on Windows (WSL), macOS, Linux without path translation
3. **Portability** — Same overlay works on different developer machines

### Overlay Structure

```
${HARNESS_OVERLAY_PATH}/
├── claude/
│   ├── skills/
│   │   ├── code-graph-context.md → /workspace/marketplace/.agents/skills/code-graph-context.md
│   │   └── review-simplify-complexity.md → /workspace/marketplace/.agents/skills/review-simplify-complexity.md
│   ├── agents/
│   │   └── pries-pm.md → /workspace/marketplace/.agents/agents/pries-pm.md
│   ├── commands/
│   │   └── pries-implement.md → /workspace/marketplace/.agents/commands/pries-implement.md
│   └── plugins/
│       └── matd/ → /workspace/marketplace/.agents/plugins/matd/
├── opencode/
│   └── (same structure as claude/)
└── gemini/
    └── (same structure as claude/)
```

### CLI Integration

Container-side script `harness-sandbox/bin/harness-link-clis` wires the overlay into each CLI's config directory:

| CLI | Config Directory | Overlay Source | Notes |
|-----|------------------|----------------|-------|
| Claude Code | `~/.claude.harness/` | `/opt/harness-overlay/claude/` | Via `CLAUDE_CONFIG_DIR` env var |
| OpenCode | `~/.config/opencode/` | `/opt/harness-overlay/opencode/` | Uses singular `agent/` and `command/` subdirs |
| Gemini | `~/.gemini/` | `/opt/harness-overlay/gemini/` | Only consumes `commands/` → `commands/` and `plugins/` → `extensions/` |

**Linking logic (idempotent on container start):**
```bash
# Claude Code example
ln -sfn /opt/harness-overlay/claude/skills   ~/.claude.harness/skills
ln -sfn /opt/harness-overlay/claude/agents   ~/.claude.harness/agents
ln -sfn /opt/harness-overlay/claude/commands ~/.claude.harness/commands
ln -sfn /opt/harness-overlay/claude/plugins  ~/.claude.harness/plugins
```

**Safety:** Never overwrites real directories, only symlinks or missing paths

## Practical Examples

### Example 1: Minimal Project

**Goal:** Essential quality tools without workflow overhead

```yaml
# .harness.yaml
bundles:
  - essentials
```

**Result:**
- 7 skills (simplify-complexity, check-correctness, differential-review, systematic-debugging, verification, finishing-branch, git-guardrails)
- 1 agent (tdd-code-reviewer)
- Available in all CLIs (default)

### Example 2: PRIES + CodeGraphContext

**Goal:** Full PRIES workflow with code graph querying

```yaml
# .harness.yaml
clis:
  - claude          # Only Claude Code needed
bundles:
  - pries-core
skills:
  - code-graph-context  # Add CGC on top of pries-core skills
plugins:
  - harness-cgc-skill   # MCP integration for CGC
```

**Result:**
- 10 skills (9 from pries-core + code-graph-context)
- 5 agents (pries-pm, pries-make, pries-test, pries-check, pries-simplify)
- 4 commands (pries-implement, pries-validate, pries-review-only, pries-test-only)
- 2 plugins (harness-workflow-runtime from bundle + harness-cgc-skill direct)
- Overlay populated for Claude Code only

### Example 3: Custom Skill Mix with Exclusions

**Goal:** PRIES workflow but skip dual-review (prefer differential-review)

```yaml
# .harness.yaml
bundles:
  - pries-core

exclude:
  skills:
    - review-orchestrate-dual-review  # Not needed, have differential-review
```

**Result:**
- 8 skills (9 from pries-core minus excluded one)
- All pries-core agents, commands, plugins unchanged

### Example 4: Plugin-Only Configuration

**Goal:** Use matd workflow without referencing skills directly

```yaml
# .harness.yaml
plugins:
  - matd
```

**Result:**
- matd plugin loads
- matd's `plugin.json` expands to include `agents/` and `skills/` directories
- All agents and skills from those directories become available
- No bundles, no direct references

### Example 5: Local Developer Override

**Goal:** Test experimental skill without modifying committed config

**Project .harness.yaml (committed):**
```yaml
bundles:
  - essentials
```

**Developer .harness.local.yaml (gitignored):**
```yaml
skills:
  - experimental-skill
  - debug-helper
```

**Result:**
- All essentials bundle assets
- Plus experimental-skill and debug-helper
- Other developers unaffected

### Example 6: Multi-CLI with Different Needs

**Goal:** Claude Code gets full PRIES, Gemini only gets commands

```yaml
# .harness.yaml
clis:
  - claude
  - gemini

bundles:
  - pries-core  # Skills/agents ignored by Gemini, commands used
```

**Result:**
- Claude Code overlay: skills/ agents/ commands/ plugins/ all populated
- Gemini overlay: commands/ populated (Gemini ignores skills/agents)
- OpenCode not configured (not in clis list)

## Troubleshooting

### Skills Not Showing Up

**Symptom:** Skill appears in manifest but not available in CLI

**Diagnosis:**
1. Check `harness-resolve` output for skill count
2. Verify overlay directory: `ls ${HARNESS_OVERLAY_PATH}/<cli>/skills/`
3. Check container wiring: `ls ~/.claude.harness/skills/` (inside container)

**Common causes:**
- Skill name typo in manifest
- Skill doesn't exist in marketplace (harness-resolve would fail)
- Bundle exclusion removed it (check exclude: block)
- CLI-specific: Gemini ignores skills, only consumes commands

**Fix:**
```bash
# Re-run resolution
PROJECT_PATH=/path/to/project MARKETPLACE_PATH=/path/to/harness-tooling \
  harness-sandbox/bin/harness-resolve

# Check what was selected
jq '.skills' <<< "${RESOLVED}"
```

### Plugin Not Loading

**Symptom:** Plugin referenced but CLI doesn't recognize it

**Diagnosis:**
1. Verify plugin directory exists: `ls harness-tooling/.agents/plugins/<name>/`
2. Check `plugin.json` exists: `ls harness-tooling/.agents/plugins/<name>/.claude-plugin/plugin.json`
3. Validate `plugin.json` syntax: `jq . <plugin.json>`
4. Check path references: are they relative to `.claude-plugin/` dir?

**Common causes:**
- Wrong directory name in manifest (must match `.agents/plugins/<dir>/`)
- Missing `.claude-plugin/` subdirectory
- Invalid JSON in `plugin.json`
- Relative paths pointing outside marketplace tree

**Fix:**
```json
// Correct: paths relative to .claude-plugin/
{
  "name": "my-plugin",
  "skills": "../../skills/my-skill.md"
}

// Wrong: absolute or host paths
{
  "name": "my-plugin",
  "skills": "/workspace/marketplace/.agents/skills/my-skill.md"  // Don't do this
}
```

### Conflicts Between Bundles

**Symptom:** Two bundles include the same skill with different versions or incompatible configs

**Diagnosis:**
1. Bundles union; duplicates collapse (not a conflict)
2. If actual conflict exists (e.g., different skill files with same name), last one wins via symlink overwrite
3. Check bundle definitions: `yq '.bundles' harness-tooling/.agents/configs/bundles.yaml`

**Resolution strategy:**
```yaml
# If bundle A and bundle B both include skill-x but you only want A's version:
bundles:
  - bundle-a

skills:
  - skill-from-b-only  # Cherry-pick instead of using bundle-b

# Or explicitly exclude:
bundles:
  - bundle-a
  - bundle-b

exclude:
  skills:
    - skill-x  # Remove from both bundles, add back manually if needed
```

### Unknown Bundle Error

**Symptom:** `harness-resolve` fails with "Unknown bundle: <name>"

**Cause:** Bundle name in manifest not defined in `bundles.yaml`

**Fix:**
```yaml
# Check available bundles
yq '.bundles | keys' harness-tooling/.agents/configs/bundles.yaml

# Output: [essentials, pries-core]

# Fix typo or add bundle definition
bundles:
  - pries-core  # Was "pries-core-workflow" (wrong)
```

### Missing Items Error

**Symptom:** `harness-resolve` fails with "manifest references items not found in marketplace"

**Cause:** Skill/agent/command/plugin name doesn't exist in marketplace

**Fix:**
```bash
# List available skills
ls harness-tooling/.agents/skills/

# Check if it's a filename match issue (.md suffix)
ls harness-tooling/.agents/skills/my-skill*

# Either fix manifest name or add missing asset to marketplace
```

### Overlay Symlinks Broken

**Symptom:** Overlay contains symlinks but they're dangling inside container

**Cause:** Symlinks use host paths instead of container paths (harness-resolve bug)

**Diagnosis:**
```bash
# Check symlink target (should be /workspace/marketplace/...)
readlink .harness-overlay/claude/skills/some-skill.md

# Wrong: /home/user/harness-tooling/.agents/skills/some-skill.md
# Right: /workspace/marketplace/.agents/skills/some-skill.md
```

**Fix:** File a bug; harness-resolve should always emit container-absolute paths

### Private Manifest Not Loading

**Symptom:** `.harness.local.yaml` changes ignored

**Diagnosis:**
1. Check file exists: `ls -la .harness.local.yaml`
2. Verify YAML syntax: `yq . .harness.local.yaml`
3. Re-run harness-resolve (doesn't auto-detect changes)

**Common causes:**
- Typo in filename (must be exactly `.harness.local.yaml`)
- YAML parse error (silent failure in some jq versions)
- Not re-running resolution after edit

**Fix:**
```bash
# Validate YAML
yq . .harness.local.yaml || echo "YAML syntax error"

# Force rebuild
rm -rf .harness-overlay/
harness-sandbox/bin/harness-resolve
```

## Advanced Topics

### Dynamic Manifest Generation

Manifests can be **generated programmatically** before calling `harness-resolve`:

```bash
# Example: project-specific bundle selection based on git branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ "${BRANCH}" == feature/* ]]; then
  cat > .harness.local.yaml <<EOF
bundles: [pries-core]
EOF
else
  cat > .harness.local.yaml <<EOF
bundles: [essentials]
EOF
fi

harness-resolve
```

### Workspace-Wide Overrides

Edit `harness-sandbox/profiles/default.yaml` to change **all projects** in the workspace:

```yaml
# profiles/default.yaml — force code-graph-context everywhere

clis: [claude, opencode, gemini]
skills:
  - code-graph-context  # Available to all projects by default
bundles: []
```

**Caution:** Projects can't remove items from the default profile (only add or exclude)

### Cross-CLI Compatibility

Not all asset types work in all CLIs:

| Asset Type | Claude Code | OpenCode | Gemini |
|------------|-------------|----------|--------|
| Skills | ✅ | ✅ | ❌ (ignored) |
| Agents | ✅ | ✅ | ❌ (ignored) |
| Commands | ✅ | ✅ | ✅ |
| Plugins | ✅ | ✅ | ✅ (as extensions) |

**Strategy for multi-CLI projects:**
```yaml
# Use all three CLIs but understand limitations
clis: [claude, opencode, gemini]

bundles:
  - pries-core  # Skills/agents work in Claude+OpenCode, commands work in all
```

### Bundle Composition Patterns

**Layered composition:**
```yaml
# Base workflow + specialized add-ons
bundles:
  - essentials       # Base quality tools
plugins:
  - matd             # Add TDD workflow on top
skills:
  - code-graph-context  # Add CGC queries
```

**Subtractive refinement:**
```yaml
# Start big, carve out what you don't need
bundles:
  - pries-core
exclude:
  agents:
    - pries-simplify  # Skip simplify agent for this project
```

### Debugging Resolution

Enable verbose output:

```bash
# Add debug tracing to harness-resolve
set -x  # Add to top of bin/harness-resolve

# Or inspect intermediate JSON
PROJECT_JSON="$(yaml_to_json .harness.yaml)"
echo "${PROJECT_JSON}" | jq .

# Check final merged manifest
echo "${MERGED}" | jq .

# Check post-bundle-expansion
echo "${RESOLVED}" | jq .
```

## Summary

The marketplace configuration system provides:

✅ **Manifest-driven asset selection** — Explicit, version-controlled, auditable
✅ **Three-layer composition** — Workspace defaults + project config + local overrides
✅ **Bundle abstraction** — Workflow-aligned presets with escape hatches
✅ **Plugin packaging** — Self-contained extensions with relative path safety
✅ **Multi-CLI support** — Claude Code, OpenCode, Gemini from one manifest
✅ **Container-safe paths** — Bind-mount friendly, cross-platform portable

**Next steps:**
- Add project-specific `.harness.yaml` with desired bundles/skills
- Optionally create `.harness.local.yaml` for private experiments
- Run `harness-resolve` to build overlay
- Attach container and verify assets loaded in CLI
