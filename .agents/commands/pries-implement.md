---
description: "BMAD Phase 4 (Implementation): execute the full 10-phase PRIES workflow against an issue ID. Orchestrates PM → Test → Make → Check → Simplify with convergence-bounded review cycles and a draft PR at the end."
agent: pries-pm
subtask: true
options:
  skip_tests: false
  parallel_tasks: false
  review_cycles: 3
return:
  # Phase 1: Verify repo readiness.
  - /subtask {agent: pries-pm && as: phase1_verify} Verify repo state for issue "$ARGUMENTS". Confirm clean working tree, fetch origin, and read CLAUDE.md / AGENTS.md / docs/governance/* for context. Block if dirty or governance artefacts missing (require /governance-setup first).

  # Phase 2: Fetch issue context.
  - /subtask {agent: pries-pm && as: phase2_ticket} Using stdd-pm-linear-integration, fetch issue "$ARGUMENTS" (Linear or markdown fallback), validate NFR/constitution refs, and produce the structured ticket package.

  # Phase 3: Create worktree.
  - /subtask {agent: pries-pm && as: phase3_worktree} Using general-using-git-worktrees and the slug from $RESULT[phase2_ticket], create the isolated worktree at .worktrees/feat/<id>-<slug> on branch feat/<id>-<slug>.

  # Phase 4: Plan.
  - /subtask {agent: pries-pm && as: phase4_plan} From $RESULT[phase2_ticket], draft an implementation plan. Include task list (10–30 min units each), file manifest per task, test design summary, and integration contracts for cross-task dependencies. Save to docs/tickets/$ARGUMENTS-plan.md.

  # Phase 5: Review plan (parallel @check + @simplify, max 3 cycles).
  - /subtask {agent: pries-check && as: phase5_check_1} Review the plan in $RESULT[phase4_plan] using review-check-correctness. Cycle 1 = full 8-pillar sweep. Iteration: 1.
  - /subtask {agent: pries-simplify && as: phase5_simplify_1} Review the plan in $RESULT[phase4_plan] using review-simplify-complexity. Iteration: 1.
  - /subtask {agent: pries-pm && as: phase5_merge} Apply the orchestrate-dual-review merge rules to $RESULT[phase5_check_1] and $RESULT[phase5_simplify_1]. If converged, set converged=true. Otherwise dispatch a second cycle (and a third if needed). At cycle 3 with open BLOCKERs, set requires_human_review=true and stop.

  # Phase 6: Split into tasks.
  - /subtask {agent: pries-pm && as: phase6_tasks} From the converged plan, emit a task list. Each task: id, description, acceptance_criteria, code_context, file_manifest, integration_contracts. Save to docs/tickets/$ARGUMENTS-tasks.md.

  # Phase 7: Write tests (per task).
  - /subtask {agent: pries-test && as: phase7_tests} For each task in $RESULT[phase6_tasks], dispatch stdd-test-author-constrained. Validate file patterns; run pytest --collect-only baseline. Classify failures. Emit TESTS_READY / NOT_TESTABLE / BLOCKED per task. NOT_TESTABLE requires @pries-check sign-off — pause and dispatch @pries-check for adjudication if encountered.

  # Phase 8: Implement (per task).
  - /subtask {agent: pries-make && as: phase8_implement} For each task with TESTS_READY, dispatch in tdd mode. For NOT_TESTABLE tasks (with sign-off), dispatch in standard mode. Verify GREEN per task. After all tasks complete, run integration tests across the worktree.

  # Phase 9: Final review (full diff, max 3 cycles).
  - /subtask {agent: pries-check && as: phase9_check_final} Review the full diff using review-check-correctness against the converged plan and NFR_CATALOG. Iteration: 1. Cycle until converged or max 3.
  - /subtask {agent: pries-simplify && as: phase9_simplify_final} Review the full diff using review-simplify-complexity. Iteration: 1.
  - /subtask {agent: pries-pm && as: phase9_merge_final} Merge findings via orchestrate-dual-review. If BLOCKERs remain, loop back to @pries-make for fixes (max 3 cycles). At max with open BLOCKERs, set requires_human_review=true.

  # Phase 10: Commit & PR.
  - /subtask {agent: pries-pm && as: phase10_commit} Stage changes, write conventional commits per task, push branch, create a draft PR via `gh pr create`, embed the workflow execution report (phases, cycles, findings, verification) in the PR body, and post a Linear comment linking the PR.

  # Final summary.
  - "PRIES implementation for '$ARGUMENTS' complete. Draft PR created. Review the workflow report attached to the PR body, then promote from Draft → Open when satisfied."
---
# PRIES Implement: $ARGUMENTS

**BMAD Phase 4 — Implementation.** Orchestrates the full 10-phase PRIES
workflow against issue `$ARGUMENTS`. Requires Phase 0 (governance) to be
complete; will block if `docs/governance/` artefacts are missing.

## Options

- `--skip-tests` — bypass Phase 7 (NOT_TESTABLE for the whole task; rare).
- `--parallel-tasks` — dispatch independent tasks concurrently in Phase 7/8.
- `--review-cycles=N` — override max review cycles (default 3).

## Failure modes

- **Dirty working tree** → block at Phase 1.
- **Missing governance artefacts** → block at Phase 1; recommend `/governance-setup`.
- **Test broken / env broken** → escalate to @pries-check; do not silently retry.
- **Reviewer convergence not reached** → set `requires_human_review: true` and
  stop with a draft PR labelled `wip:` and a notes block.
- **GREEN unreachable in 3 attempts** → @pries-make returns BLOCKED;
  workflow commits as `wip:` with notes.

## Outputs

- `feat/<id>-<slug>` branch with conventional commits.
- Draft PR with embedded workflow report.
- Updated `docs/tickets/<id>.md` (status, comments).
- Plan + task breakdown under `docs/tickets/<id>-plan.md`,
  `docs/tickets/<id>-tasks.md`.
