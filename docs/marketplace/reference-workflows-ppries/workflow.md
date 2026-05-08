# Fire-and-Forget Multi-Agent Workflow: Plan, Test, Implement, PR

This document outlines a 10-phase autonomous workflow for executing Linear issues without waiting for user input. Here's a concise overview:

## Core Phases

**Phase 1-3: Setup** — Verify repo readiness, fetch issue context via `@pm`, create a worktree with a properly named branch.

**Phase 4: Plan** — Analyze requirements and design an implementation strategy. Conditionally include test design for non-trivial tasks (API changes, bug fixes, new features, multi-module work).

**Phase 5: Review Plan** — Dispatch `@check` (testability & correctness) and `@simplify` (test scope) in parallel. Use a 3-cycle loop with convergence detection; merge findings with `@check` as the tiebreaker.

**Phase 6: Split into Tasks** — Break the plan into discrete 10-30 minute tasks, each with acceptance criteria, code context, file lists, and integration contracts where needed.

**Phase 7: Write Tests** — For each task, dispatch `@test` to write failing tests. Validate test files match patterns (`test_*.py`, `*_test.py`, etc.) using a pre/post baseline check. Handle four outcomes: TESTS_READY, NOT_TESTABLE, BLOCKED, or immediate pass (investigate).

**Phase 8: Implement** — Dispatch `@make` per task. Run in TDD mode (RED→GREEN) when tests exist; standard mode for NOT_TESTABLE tasks. Escalate test quality concerns to `@check` → `@test` → `@make` loop. Verify integration after all tasks.

**Phase 9: Final Review** — Dispatch `@check` and `@simplify` on the full diff. Use 3-cycle max with convergence detection.

**Phase 10: Commit & PR** — Stage changes, write conventional commits, create a draft PR with execution report, update Linear with a comment, and write a workflow summary.

## Key Safeguards

- **Failure handling:** Incomplete runs commit as "wip:" and create a draft PR with notes.
- **No hanging:** Treat any blocking prompts as failures.
- **Test isolation:** `@test` must not modify existing conftest.py (parallel safety).
- **Parallelism:** Independent tasks can be tested in parallel.
