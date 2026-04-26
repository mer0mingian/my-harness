---
description: "Standalone dual review (no implementation): runs @pries-check and @pries-simplify against the current diff/branch/PR with up to 3 convergence cycles."
agent: pries-pm
subtask: true
options:
  target: "uncommitted"
  review_cycles: 3
return:
  # Step 1: Classify the target.
  - /subtask {agent: pries-pm && as: review_classify} Classify review target "$ARGUMENTS" (uncommitted | <sha> | <branch> | pr:<num> | <path/to/plan.md>). Gather the artefact set: diffs, full files, governance artefacts, AGENTS.md / CLAUDE.md / CONVENTIONS.md.

  # Step 2: Cycle 1 — parallel @check + @simplify.
  - /subtask {agent: pries-check && as: rev_check_1} Review $RESULT[review_classify] using review-check-correctness. Iteration: 1.
  - /subtask {agent: pries-simplify && as: rev_simplify_1} Review $RESULT[review_classify] using review-simplify-complexity. Iteration: 1.

  # Step 3: Convergence check.
  - /subtask {agent: pries-pm && as: rev_merge_1} Apply orchestrate-dual-review merge rules to $RESULT[rev_check_1] and $RESULT[rev_simplify_1]. If converged, emit unified report and stop. Otherwise wait for the user to address findings, then optionally re-run.

  # Step 4: Final report.
  - "Dual review complete. See the unified report above. @check verdict gates merge approval; @simplify findings are advisory."
---
# PRIES Review Only: $ARGUMENTS

Standalone dual-review workflow. Use when you want @pries-check + @pries-simplify
findings without triggering implementation.

## Targets

- `uncommitted` (default) — current `git diff` against HEAD.
- `<sha>` — a specific commit.
- `<branch>` — branch diff against `main`.
- `pr:<num>` — open GitHub pull request.
- `<path/to/plan.md>` — review a markdown plan/spec.

## Cycle behaviour

Up to 3 convergence cycles. Cycles 2–3 require an actual diff change
between cycles; otherwise the orchestrator declares "no change to review."

## Output

Unified report with:

- `verdict` (APPROVE / REQUEST_CHANGES / BLOCK) — from @check.
- `check_findings` (BLOCKER/CRITICAL/MAJOR/MINOR).
- `simplify_findings` (HIGH/MEDIUM/LOW, advisory).
- `requires_human_review` flag if convergence not reached.
