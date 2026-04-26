---
name: stdd-test-author-constrained
description: TDD test authoring with strict failure classification (MISSING_BEHAVIOR,
  ASSERTION_MISMATCH, TEST_BROKEN, ENV_BROKEN), file pattern enforcement, and
  RED-state validation. Use when @pries-test or any TDD agent must write failing
  tests BEFORE implementation in a sandboxed manner that prevents production code
  modification and conftest.py side effects.
---
# STDD Test Author Constrained

Constrained TDD test authoring skill that enforces the PRIES test contract:
write failing tests before implementation, classify failures, restrict file
writes to test patterns only, and never modify shared `conftest.py` files.

## When to use

- The `pries-test` agent is dispatched to author tests for a task.
- Any TDD workflow that requires a verifiable RED state before GREEN.
- A test author must distinguish "test broken" from "code missing" failures.
- Tests must be added without breaking existing parallel-safe fixtures.

## File constraints (HARD)

The skill may **only** create or modify files matching one of:

| Pattern                  | Notes                                       |
| ------------------------ | ------------------------------------------- |
| `**/test_*.py`           | Standard pytest module naming               |
| `**/*_test.py`           | Alternate pytest naming                     |
| `**/conftest.py`         | **Only if creating new** in a new directory |
| `**/test_data/**`        | Static fixture data                         |
| `**/test_fixtures/**`    | Reusable fixture code                       |

**Production code is off-limits.** Modifying an existing `conftest.py` is
forbidden — it would break parallel test isolation. Renaming, deleting, or
moving any file is forbidden; escalate to the caller.

## Pre/post baseline check

Before writing tests:

1. Run `pytest --collect-only -q` and capture the test count and module list.
2. Author the new test file(s).
3. Re-run `pytest --collect-only -q` and diff. Only newly added tests should
   appear. Pre-existing tests must remain in the manifest unchanged.

If the diff shows missing pre-existing tests, abort and report
`TEST_BROKEN` — the new file likely shadowed or imported a fixture badly.

## Failure classification taxonomy

After writing tests, run the new tests and classify each failure:

| Code                | Meaning                                  | Valid RED? | Action                                           |
| ------------------- | ---------------------------------------- | ---------- | ------------------------------------------------ |
| MISSING_BEHAVIOR    | Function/class/route does not exist      | YES        | Hand off to @make for implementation             |
| ASSERTION_MISMATCH  | Code exists, behaviour differs           | YES        | Hand off to @make for implementation             |
| TEST_BROKEN         | Test has Python error or wrong import    | NO         | Fix the test before proceeding                   |
| ENV_BROKEN          | Missing dependency, fixture, network     | NO         | Escalate to caller; do not silently install      |

**Only MISSING_BEHAVIOR and ASSERTION_MISMATCH qualify as RED.** All other
codes block the workflow until resolved.

## Mixed-failure escalation

If a single dispatch produces a mix of valid and invalid failure codes, set
`escalate_to_check: true`. The orchestrator must route the test set back to
@pries-check for adjudication before any GREEN work begins.

Other escalation triggers:

- More than 2 mocks in any single test (suggests design smell).
- Nondeterministic behaviour (timing, random, network) without a seed/fake.
- New shared fixtures introduced (must be reviewed for parallel safety).

## NOT_TESTABLE verdict

Permitted **only** when the change is one of:

- Pure config edits (no logic).
- External-system integration without a harness or contract test.
- Non-deterministic behaviour with no reasonable fake.
- Pure wiring (DI registration, route registration with no branching).

A NOT_TESTABLE verdict requires explicit `@pries-check` sign-off recorded in
the run report. Do not bypass.

## Required inputs

The dispatcher must provide:

- Task description (one or two sentences).
- Acceptance criteria (numbered list, testable phrasing).
- Code context (actual function signatures or files under test).
- Target test file path (one of the allowed patterns).

If any input is missing, return `BLOCKED` with the specific gap. Do not
guess.

## Test philosophy

Write **contract tests** that verify:

- Public API behaviour: inputs, outputs, raised errors.
- Specified edge cases from acceptance criteria.
- Bug reproduction: a fix's test must fail before the fix and pass after.

Avoid:

- Asserting on private attributes or implementation details.
- Trivial tests for constructors, plain getters, dataclasses.
- Asserting on mock calls without behavioural meaning.

## Output contract

Return a structured report:

```yaml
status: TESTS_READY | NOT_TESTABLE | BLOCKED
files_added:
  - tests/feature_x/test_feature_x.py
files_modified: []  # MUST stay empty for conftest.py and production
red_state:
  - test_id: tests/feature_x/test_feature_x.py::test_returns_404
    classification: MISSING_BEHAVIOR
  - test_id: tests/feature_x/test_feature_x.py::test_validates_input
    classification: ASSERTION_MISMATCH
escalate_to_check: false
notes: "Fixture parity verified via collect-only diff."
```

## Anti-patterns

- Modifying production code "just to make the import work."
- Editing existing `conftest.py` to add a fixture (violates parallel safety).
- Marking a TEST_BROKEN failure as RED to unblock @make.
- Returning NOT_TESTABLE without @pries-check approval.
- Suppressing failures with `pytest.mark.skip` to declare TESTS_READY.
