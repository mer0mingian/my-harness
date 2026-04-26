# PRIES Workflow Usage Guide

**Audience:** Engineers using the PRIES plugin to implement features.
**Prerequisite:** Phase 0 governance complete (`/governance-setup` has run).

---

## When to use

- After Phase 0 (governance) is complete in your repo.
- The feature has clear acceptance criteria and at least one NFR ID
  (or an explicit "no NFR — reason: ..." note).
- TDD is appropriate (most features). For pure config or wiring, use
  `--skip-tests` or accept NOT_TESTABLE escalation.

## Quick start

### Full workflow

```bash
/pries-implement STA-001
```

Runs all 10 phases. Produces a draft PR with the workflow report
embedded in the body. The PR is `wip:` if any phase escalated.

### Standalone review

```bash
/pries-review-only                  # uncommitted changes
/pries-review-only pr:42            # an open PR
/pries-review-only feat/abc-123     # a branch
/pries-review-only docs/plans/x.md  # a plan markdown
```

Returns `verdict`, `check_findings`, `simplify_findings`, and a
`requires_human_review` flag. No code is written.

### Standalone tests

```bash
/pries-test-only "Momentum sync over WebSocket"
/pries-test-only docs/specs/feature-x.md
```

Writes failing tests in allowed patterns only, classifies failures, and
hands off TESTS_READY for downstream `/pries-implement` or manual
@pries-make dispatch.

### CI/CD validation gate

```bash
/pries-validate
```

Suitable for pre-merge hooks. Exit 0 on PASS; non-zero on FAIL.

## What the workflow produces

After `/pries-implement <ID>` completes successfully:

- Branch `feat/<id>-<slug>` with conventional commits per task.
- `docs/tickets/<id>.md` updated (state, status log, comments).
- `docs/tickets/<id>-plan.md` — converged plan from Phase 5.
- `docs/tickets/<id>-tasks.md` — task decomposition from Phase 6.
- New test files in `tests/` matching allowed patterns.
- Implementation code within the per-task file manifests.
- Draft PR with embedded workflow report:
  - Phases run, cycles per review phase, convergence status.
  - Verification commands and exit codes.
  - Per-AC pass/fail results.
  - All findings (BLOCKER/CRITICAL/MAJOR/MINOR + HIGH/MEDIUM/LOW).

## Customization

### Skill assignments

Each agent's skill list lives in `.agents/agents/pries-*.md`.
Edit the `skills:` (Claude) and the matching pattern in `permission.skill:`
(OpenCode) to adjust.

### Review cycle limits

Pass `--review-cycles=N` to `/pries-implement`. Default is 3. Lower for
fast iteration on trusted code; higher for high-risk changes.

### Test patterns

Default allowed patterns are in `pries-test.md` `permission.write` /
`permission.edit`. Add or restrict patterns for your repo's test layout.
Existing `conftest.py` should remain immutable.

### Convergence thresholds

The convergence rule lives in
`.agents/skills/review-orchestrate-dual-review/SKILL.md`. The default
("two consecutive cycles with zero new BLOCKER/CRITICAL/HIGH") is
project-portable. Tighten or relax as needed.

### File-manifest scope

`@pries-make` honours the manifest provided by `@pries-pm`. To pre-set
a manifest, edit Phase 4 of `pries-implement.md` to read from a project
file.

## Common scenarios

### "My ticket has no NFR ref"

The PM agent will recommend `/governance-add-nfr` before proceeding.
Either:

- Add the NFR (preferred for governed surfaces).
- Or add an explicit `**Related Artifacts:** none — reason: ...` line
  to the ticket markdown.

### "Tests pass on first run"

Phase 7 expects RED. If tests pass immediately, the workflow flags this
as suspicious — either the feature already exists or the test asserts
something already true. @pries-check is dispatched to investigate.

### "@check and @simplify disagree"

Merge rules in `review-orchestrate-dual-review` resolve most cases:
correctness > style. When they don't, `requires_human_review: true` and
the workflow stops with a `wip:` PR.

### "I want to skip tests"

Use `/pries-implement <ID> --skip-tests` for genuinely non-testable
work (config, wiring). The workflow records NOT_TESTABLE and runs
@pries-check for sign-off before proceeding.

## Troubleshooting

| Symptom                                | Likely cause                                  | Fix                                                       |
| -------------------------------------- | --------------------------------------------- | --------------------------------------------------------- |
| Workflow blocks at Phase 1             | Dirty tree or missing governance              | Stash/commit; run `/governance-setup`                     |
| @pries-test returns BLOCKED            | Missing acceptance criteria or context        | PM clarifies ticket; re-dispatch                          |
| @pries-make returns SCOPE_ESCALATION   | Manifest too narrow                           | PM expands manifest or splits task                        |
| Convergence never reached              | Real BLOCKERs that need human attention       | Address findings, then resume / new run                   |
| `pries-validate` flags pyramid drift   | New tests added without strategy update       | Update `TEST_STRATEGY.md` or rebalance tests              |

## See also

- [PRIES integration guide](./pries-workflow-integration.md)
- [Governance integration](./technical-governance-integration.md)
- [PRIES skill mapping](../../docs/pries-skill-mapping.md)
- [BMAD integration](../../docs/integration-bmad-method.md)
