# harness-workflow-runtime

**Status:** Phase 0 — schema layer + validator CLI only. Not yet a runnable plugin (hooks, slash commands, resolver, state manager land in Phases 1–6).

See [docs/harness-workflow-runtime-plan.md](../../../docs/harness-workflow-runtime-plan.md) for the full v1 roadmap and [docs/WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md](../../../docs/WORKFLOW_ORCHESTRATOR_REQUIREMENTS.md) for scope.

## What this delivers (Phase 0)

Pydantic schemas and a validator CLI for the harness multi-agent workflow marketplace. Validates:

- `SKILL.md` files per the [agentskills.io](https://agentskills.io/) spec.
- Agent frontmatter (dual-convention: OpenCode `permission.skill` and STDD `permission.read/write/edit/bash`).
- Claude / OpenCode slash-command frontmatter (both native and STDD `agent`/`subtask`/`return` styles).
- `workflow.yaml` phase manifests.
- `settings.json` hook entries.

The same models are reused in Phase 2 (resolver) and Phase 4 (hooks).

## Install (dev)

```bash
cd .agents/plugins/harness-workflow-runtime
uv venv
uv pip install -e '.[dev]'
```

Or with standard pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```bash
# Validate the whole marketplace tree
python -m harness_workflow.validate /path/to/my-harness

# Strict mode — warnings become errors
python -m harness_workflow.validate --strict /path/to/my-harness

# Validate a single file
python -m harness_workflow.validate .agents/skills/some-skill/SKILL.md
```

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Clean — no issues, or warnings-only without `--strict` |
| `1` | Warnings encountered with `--strict` |
| `2` | Validation errors |

## Run tests

```bash
uv run pytest
```

## Schema models at a glance

See [`harness_workflow/schemas.py`](harness_workflow/schemas.py) for the full definitions. Top-level exports:

| Model | Validates |
|---|---|
| `Skill` | `SKILL.md` frontmatter (agentskills.io compliant) |
| `Agent` | Agent markdown frontmatter |
| `Permissions` | `permission.*` block — accepts both OpenCode and STDD conventions |
| `Command` | Slash-command frontmatter |
| `HookMatcher` / `HookCommand` | `settings.json` hook entries |
| `PhaseManifest` / `WorkflowManifest` | `workflow.yaml` phase + workflow definitions |

## Known warnings on the current marketplace

The validator run against the current `.agents/` tree will flag:

- `alpine-js-patterns/SKILL.md` — no frontmatter (error).
- `.agents/skills/Specification.md` — loose file at skills root (skipped by the scanner).
- 19 skills where the directory name does not match the frontmatter `name:` (warnings).

These are pre-existing tree state; Phase 0 does not remediate them.
