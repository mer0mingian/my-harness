---
name: review-orchestrate-dual-review
description: Coordinates parallel @pries-check (correctness) and @pries-simplify
  (complexity) review agents with up to 3 convergence cycles, finding-merge rules
  (correctness > style), severity preservation, and human-escalation gates. Use
  when /pries-review-only or the main /pries-implement workflow needs a unified
  dual review report.
---
# Review: Orchestrate Dual Review

Orchestrates the PRIES dual-review pattern: dispatch `@pries-check` and
`@pries-simplify` in parallel against a target artefact (plan, diff, branch,
or PR), iterate until convergence, then merge findings into a unified
report without losing native severity.

## When to use

- The `/pries-review-only` command is invoked.
- Phase 5 (review plan) or Phase 9 (final review) of `/pries-implement`.
- Pre-commit / pre-merge validation that needs both correctness and
  simplicity reviewers.
- A standalone diff requires both checkers and a converged verdict.

## Inputs

```yaml
target_kind: uncommitted | commit | branch | pr | plan
target_ref: HEAD | <sha> | <branch> | <pr_number> | <path/to/plan.md>
max_cycles: 3        # default
review_scope: full | light | minimal
```

## Step 1: classify input

Inspect the target and produce the canonical artefact set for both
reviewers:

- **uncommitted**: `git diff` + `git diff --stat` + full files of touched
  modules.
- **commit**: `git show <sha>` + ancestor context.
- **branch**: `git diff <base>...<head>` + commit log.
- **pr**: `gh pr view <num> --json files,body` + diff.
- **plan**: the plan markdown plus the files it references.

## Step 2: gather convention context

Auto-discover and include the following if present:

- `AGENTS.md`, `CLAUDE.md`, `CONVENTIONS.md`, `.editorconfig`.
- `docs/governance/TECHNICAL_CONSTITUTION.md` (constitution rules).
- `docs/governance/NFR_CATALOG.md` (NFR IDs for cross-reference).
- `docs/governance/TEST_STRATEGY.md` (test pyramid expectations).
- `pyproject.toml` / `package.json` for tooling baseline.

These travel with the dispatch payload so reviewers cite real rules.

## Step 3: parallel dispatch

Dispatch **both** reviewers concurrently using the
`orchestrate-dispatching-parallel-agents` pattern:

- `@pries-check` consumes `review-check-correctness` skill.
- `@pries-simplify` consumes `review-simplify-complexity` skill.

Both are mandatory; do not skip @simplify just because @check returned
clean. Reviewers are independent.

## Step 4: convergence loop (max 3 cycles)

After cycle N completes:

1. Aggregate findings: dedupe identical (location, problem) tuples.
2. Detect changes since cycle N-1:
   - **Resolved**: previous finding now absent or refuted.
   - **Persisted**: same finding still present.
   - **New**: not in cycle N-1.
3. Convergence rule:
   - If **two consecutive cycles** produce zero new BLOCKER/CRITICAL
     findings AND zero new HIGH-severity simplify findings, declare
     **converged** and stop.
   - If max_cycles is reached without convergence, set
     `requires_human_review: true` and stop.

Between cycles, the developer (or @make) addresses BLOCKER findings.
Re-dispatch only when the diff has changed.

## Step 5: merge rules (correctness > style)

When @check and @simplify findings touch the same location:

| Scenario                                    | Result                                        |
| ------------------------------------------- | --------------------------------------------- |
| @check BLOCKER + @simplify "remove this"    | Keep code, fix correctness; ignore simplify   |
| @check clean + @simplify HIGH               | Apply simplification                          |
| @check MAJOR + @simplify HIGH (same file)   | Note both; correctness fix takes priority     |
| @check approves + @simplify recommends      | Surface simplify advice as advisory           |

**@check verdict gates the merge.** @simplify findings are advisory and
never block merge on their own.

## Severity preservation

Do **not** translate severities to a unified scale. Report each
reviewer's native scale:

- @check: BLOCKER, CRITICAL, MAJOR, MINOR.
- @simplify: HIGH, MEDIUM, LOW (advisory).

The orchestrator's job is to surface, not normalise.

## Output contract

```yaml
verdict: APPROVE | REQUEST_CHANGES | BLOCK
converged: true
cycles_run: 2
requires_human_review: false
check_summary:
  verdict: APPROVE
  blocker: 0
  critical: 0
  major: 1
  minor: 2
simplify_summary:
  high: 0
  medium: 1
  low: 3
findings:
  check:
    - id: CHK-001
      severity: MAJOR
      location: "app/api/momentum.py:L45"
      problem: "..."
      suggestion: "..."
  simplify:
    - id: SMP-001
      severity: MEDIUM
      location: "app/services/broadcast.py"
      problem: "Three-layer abstraction with one implementation"
      suggestion: "Inline; reintroduce abstraction when second user appears."
notes: "Cycle 2 produced no new BLOCKER findings; converged."
```

## Human escalation gate

Set `requires_human_review: true` when:

- Cycle 3 still has open BLOCKER findings.
- @check and @simplify give contradictory direction on the same line and
  the merge rules above don't resolve it (rare).
- Either reviewer's confidence is consistently `low` for BLOCKER findings.

The user, not the orchestrator, decides how to proceed.

## Anti-patterns

- Merging severities into a single scale (loses signal).
- Letting @simplify block a merge.
- Skipping @simplify because @check returned clean.
- Re-dispatching reviewers without a real diff change between cycles.
- Declaring convergence on cycle 1 (must observe stability across cycles).
