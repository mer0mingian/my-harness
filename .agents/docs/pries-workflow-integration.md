# PRIES Workflow Integration

**Status:** Stable
**Phase:** BMAD Phase 4 (Implementation)
**Audience:** Plugin maintainers, BMAD orchestrators, CI/CD authors

This document describes how the PRIES workflow plugin (PM → Make → Test →
Review → Simplify) integrates with the rest of the harness-tooling
marketplace and the broader BMAD lifecycle.

---

## Section 1: BMAD Phase 4 Implementation

PRIES is the **execution arm** of BMAD. Phases 0–3 produce specifications;
PRIES turns specifications into tested, reviewed, mergeable code.

### Artefact consumption

| BMAD Phase           | Artefact                                | PRIES consumer        |
| -------------------- | --------------------------------------- | --------------------- |
| Phase 0 Governance   | `docs/governance/TECHNICAL_CONSTITUTION.md` | @pries-check (compliance), @pries-simplify (KISS rules) |
| Phase 0 Governance   | `docs/governance/NFR_CATALOG.md`        | @pries-pm (validation), @pries-check (cross-ref) |
| Phase 0 Governance   | `docs/governance/TEST_STRATEGY.md`      | @pries-test (pyramid), `pries-validate` (drift) |
| Phase 1 Analysis     | `docs/business/PROBLEM_STATEMENT.md`    | @pries-pm (context)   |
| Phase 2 PM           | `docs/product/spec.md`, user stories     | @pries-pm (criteria)  |
| Phase 3 Architecture | `docs/architecture/ADR-*.md`            | @pries-make (constraints), @pries-check (compliance) |

### Validation gates

Before `/pries-implement` runs, the workflow blocks on:

1. Clean working tree.
2. Presence of `docs/governance/` artefacts.
3. The issue ticket referencing at least one NFR ID **or** an explicit
   "no NFR — reason: ..." note.

`/pries-validate` is the standalone CI form of these gates.

### ADR compliance

@pries-check loads any `docs/architecture/ADR-*.md` files and verifies:

- The diff doesn't contradict an `Accepted` ADR (e.g., introducing a new
  framework when ADR-0007 mandates FastAPI).
- New abstractions align with patterns blessed in Architecture phase.

### User-story acceptance mapping

Each PRIES task carries `acceptance_criteria` derived from the user
story's "Given/When/Then" or numbered AC list. @pries-test produces one
contract test per AC; @pries-make confirms each AC passes by id in the
output contract.

---

## Section 2: Workflow Phases (10-phase breakdown)

Mirrors `docs/reference-workflows-ppries/workflow.md` with PRIES-plugin
specifics.

| # | Phase             | Agent          | Skill(s)                                            | Artefact                                  |
| - | ----------------- | -------------- | --------------------------------------------------- | ----------------------------------------- |
| 1 | Verify repo       | @pries-pm      | general-using-git-worktrees                         | Clean tree, governance present            |
| 2 | Fetch issue       | @pries-pm      | stdd-pm-linear-integration                          | Ticket package YAML                       |
| 3 | Create worktree   | @pries-pm      | general-using-git-worktrees                         | `feat/<id>-<slug>` worktree               |
| 4 | Plan              | @pries-pm      | arch-writing-plans, stdd-product-spec-formats       | `docs/tickets/<id>-plan.md`               |
| 5 | Review plan       | @check + @simplify | review-orchestrate-dual-review                  | Converged review (max 3 cycles)           |
| 6 | Split into tasks  | @pries-pm      | arch-writing-plans                                  | `docs/tickets/<id>-tasks.md`              |
| 7 | Write tests       | @pries-test    | stdd-test-author-constrained                        | Test files (RED state)                    |
| 8 | Implement         | @pries-make    | stdd-make-constrained-implementation                | GREEN state, passing tests                |
| 9 | Final review      | @check + @simplify | review-orchestrate-dual-review                  | Final converged review                    |
|10 | Commit & PR       | @pries-pm      | general-finishing-a-development-branch              | Draft PR with workflow report             |

### Agent dispatch sequence

Sequential by default. Parallelism is allowed in:

- Phase 5 / Phase 9: @check and @simplify run concurrently.
- Phase 7 / Phase 8 with `--parallel-tasks`: independent tasks run in
  parallel. Tasks with shared file lists serialize.

### Convergence rules

- **Max 3 cycles** per review phase (Phase 5 and Phase 9).
- **Convergence** = two consecutive cycles with zero new BLOCKER /
  CRITICAL findings (and zero new HIGH simplify findings).
- **Escalation** = at cycle 3 with open BLOCKERs, set
  `requires_human_review: true` and stop with a `wip:` draft PR.

### Failure handling

| Failure                              | Action                                     |
| ------------------------------------ | ------------------------------------------ |
| Dirty working tree at Phase 1        | Block; user fixes manually                 |
| Missing governance at Phase 1        | Block; recommend `/governance-setup`       |
| @pries-test returns BLOCKED          | Pause; surface gap; user clarifies         |
| @pries-test returns NOT_TESTABLE     | Dispatch @pries-check for sign-off         |
| @pries-make returns SCOPE_ESCALATION | Pause; PM updates manifest; resume         |
| @pries-make returns BLOCKED (3x)     | Commit `wip:`, draft PR with notes         |
| Convergence not reached at cycle 3   | `requires_human_review: true`, draft `wip:` |
| External system unreachable          | Document in PR notes; mark NOT_TESTABLE    |

---

## Section 3: Tool Access & Sandboxing

Trust model mirrors `docs/reference-workflows-ppries/`:

| Agent          | Read   | Write                          | Bash (allowed)                                         |
| -------------- | ------ | ------------------------------ | ------------------------------------------------------ |
| @pries-pm      | All    | `docs/tickets/`                | linear *, ls, grep, cat, git worktree, git diff (RO)   |
| @pries-check   | All    | None                           | ls, grep, cat, git diff/show/log (RO), gh pr view      |
| @pries-simplify| All    | None                           | ls, grep, cat, git diff/show/log (RO), gh pr view      |
| @pries-test    | All    | `tests/**`, `**/test_*.py`, `**/*_test.py`, `test_data/`, `test_fixtures/` (existing `conftest.py` immutable) | pytest, ruff, git diff --name-only (RO) |
| @pries-make    | All    | `app/`, `src/`, `lib/`, `tests/` (lockfiles denied) | pytest, ruff, mypy, no git, no pip, no curl, no sudo  |

### Sandboxing rationale

- **@pries-check / @pries-simplify** are reviewers; granting write would
  blur reviewer/author roles and corrupt the dual-review verdict.
- **@pries-test** writing only test files prevents "I made the test pass
  by changing production." TDD discipline.
- **@pries-make** banning git/pip/curl prevents accidental scope creep
  (drive-by commits, surprise dependency additions, network exfil).
- Existing `conftest.py` is immutable for **parallel-test safety**: a
  fixture mutation could break unrelated suites running concurrently.

---

## Section 4: Integration with Other Workflows

### Pre-requisites

- **Phase 0 (Governance) must run first.** `/governance-setup` produces
  the three governance artefacts that PRIES gates against.
- Without `docs/governance/`, `/pries-implement` blocks at Phase 1.

### Optional planning phases

- `/bmad-spec` (Phase 1) for analyst-led problem statement.
- `/bmad-pm` (Phase 2) for spec and user stories.
- `/bmad-architect` (Phase 3) for ADRs.

These are optional; if a ticket already carries enough context (acceptance
criteria + NFR refs), PRIES can run directly.

### Standalone PRIES

For repos with minimal BMAD adoption:

- `/governance-setup` once.
- `/pries-implement <ID>` per feature.
- `/pries-validate` in CI.

The full BMAD planning chain is recommended for greenfield enterprise
projects but is not required.

### Compatibility matrix

| CLI         | Skills | Agents | Commands |
| ----------- | ------ | ------ | -------- |
| Claude Code | ✅      | ✅      | ✅        |
| OpenCode    | ✅      | ✅ (via permission ACL) | ✅ |
| Gemini CLI  | review-* + general-* only (research scope) | n/a | n/a |

`.claude/` and `.opencode/` are symlinks to `.agents/`, so adding a skill
or agent here makes it visible to both CLIs immediately.

---

## References

- [PRIES skill mapping](../../docs/pries-skill-mapping.md)
- [PRIES reference workflow](../../docs/reference-workflows-ppries/)
- [BMAD integration](../../docs/integration-bmad-method.md)
- [Governance integration](./technical-governance-integration.md) (sibling)
