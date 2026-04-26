---
description: "Inspect the harness workflow runtime (Phase 1 stub; /workflow run|advance|status|reset land in Phase 3)."
---

# harness-workflow-runtime — Phase 1 stub

The `harness-workflow-runtime` plugin is loaded.

This is a **Phase 1 scaffold** command. In later phases `/workflow` will dispatch to:

- `/workflow run <workflow-id>` — initialise a workflow and enter phase 1 (Phase 3).
- `/workflow advance` — validate the prior phase's artifact, transition to the next phase (Phase 3).
- `/workflow status` — pretty-print current workflow + phase state (Phase 3).
- `/workflow reset` — wipe workflow state, with confirmation (Phase 3).
- `/new-workflow` — interactive Q&A to author a new workflow.yaml (Phase 6).

## Smoke test

Phase 1 acceptance (see `docs/harness-workflow-runtime-plan.md` §8 Phase 1):

1. `/workflow` renders this text — ✅ the command was discovered by Claude Code.
2. Run any tool call (e.g., ask Claude to read a file). Set `HARNESS_WORKFLOW_TRACE=1` in your shell first to make the no-op PreToolUse hook visible on stderr.
3. If both happen, Phase 1 smoke is green.

## Status

- ✅ Phase 0: pydantic schemas + validator CLI (`python -m harness_workflow.validate`)
- ✅ Phase 1: plugin scaffold (this command + the no-op hook)
- ⏳ Phase 2: resolver (`harness_workflow/resolver.py`)
- ⏳ Phase 3: state manager + `/workflow` state machine
- ⏳ Phase 4: real enforcement hooks (replace the no-op)
- ⏳ Phase 5: mermaid sequence compiler
- ⏳ Phase 6: `/new-workflow` interview
- ⏳ Phase 7: example workflow (`stdd-feat`)
- ⏳ Phase 8: OpenCode parity
- ⏳ Phase 9: docs + handoff
