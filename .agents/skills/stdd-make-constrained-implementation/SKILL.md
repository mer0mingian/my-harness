---
name: stdd-make-constrained-implementation
description: Sandboxed code implementation with strict file-boundary enforcement,
  TDD GREEN-mode validation, and escalation rules for renames/deletes/scope creep.
  Forbids git, pip, uv, curl, network, and shell danger commands. Use when
  @pries-make implements a task plan against a fixed file manifest, with or without
  pre-written failing tests.
---
# STDD Make: Constrained Implementation

Implementation skill for the PRIES `@make` agent. Enforces hard file
boundaries from the task manifest, blocks dangerous shell operations, and
validates GREEN state when tests are present.

## When to use

- A task has been planned with a concrete file manifest.
- Tests have been authored (TDD mode) or the change is NOT_TESTABLE
  (standard mode with explicit @check sign-off).
- Implementation must occur without git, pip, network, or other side
  effects beyond the listed files.

## Required inputs

The dispatcher must provide:

1. **Task description** — what to implement, in one or two sentences.
2. **Acceptance criteria** — testable success conditions.
3. **Code context** — existing function signatures, modules, fixtures.
4. **File manifest** — explicit list of files allowed to be created
   or modified. No globs.
5. **Mode** — `tdd` (must run pre-written tests, expect RED, achieve GREEN)
   or `standard` (no tests; allowed only after NOT_TESTABLE sign-off).
6. **Optional** — pseudo-code, integration contracts, constraints.

If any required input is missing, return `BLOCKED` with the gap. Do not
guess.

## File-boundary enforcement (HARD)

- Modify or create **only** files listed in the manifest.
- Renames, deletes, or moves are forbidden — escalate to caller.
- Adding a new dependency (pip/uv/npm/poetry add) is forbidden — escalate.
- Creating new files outside the manifest is forbidden — escalate.

If implementation cannot be completed within the manifest, return
`SCOPE_ESCALATION` with:

- The unlisted files needed.
- The reason (refactor, new abstraction, missing fixture, etc.).
- A proposed expanded manifest.

The caller decides whether to expand the manifest or split the task.

## Forbidden bash commands

The skill must never invoke:

- `git *` (commit, push, branch, checkout, merge, rebase, stash).
- `pip`, `uv add`, `uv pip`, `poetry add`, `npm install`, `yarn add`.
- `curl`, `wget`, `nc`, `ssh`, anything that opens an outbound socket.
- `sudo`, `su`, package manager installs.
- `rm -rf`, recursive deletes outside the manifest.

Permitted bash includes: `pytest`, `python -m`, `ruff`, `mypy`, `ls`,
`cat`, `grep`, `diff`, `git diff --name-only` (read-only), and
project-defined test commands. Any uncertainty → escalate.

## TDD GREEN workflow

When `mode: tdd`:

1. **Verify RED**: run the pre-written tests and confirm they fail with
   `MISSING_BEHAVIOR` or `ASSERTION_MISMATCH`. If they fail with
   `TEST_BROKEN` or `ENV_BROKEN`, escalate to @pries-check.
2. **Plan minimal change**: identify the smallest delta within the manifest
   that flips the failing assertions to pass.
3. **Implement**: edit only manifest files.
4. **Re-run tests**: confirm GREEN. Capture `pytest` output verbatim.
5. **Regression sweep**: run the broader test suite if the manifest
   touches shared modules. Report any newly failing tests as a regression.
6. **Document**: cycle summary in the output.

If GREEN cannot be reached in 3 attempts, return `BLOCKED` with the
specific failure. Do not relax the tests.

## Standard (non-TDD) workflow

When `mode: standard` (NOT_TESTABLE only):

1. Implement the change within the manifest.
2. Run available smoke checks (linter, type checker).
3. Document why TDD was not applicable; reference the @pries-check
   sign-off recorded in the run report.

## Verification standard

Borrowed from `general-verification-before-completion`:

> No claims of success without fresh evidence in THIS run.

- Execute verification commands live in the same dispatch.
- Capture exit codes and the relevant output excerpt.
- Map each acceptance criterion to a passing test or smoke check.
- Do not reuse output from a prior cycle.

## Escalation triggers

Return `SCOPE_ESCALATION` when:

- The manifest is missing a file required to satisfy the criteria.
- A new dependency is needed.
- A rename, delete, or move is unavoidable.
- The task scope exceeds the agreed time budget (typically 30 min).

Return `BLOCKED` when:

- Required input is missing or contradictory.
- Tests fail with an environment error (ENV_BROKEN).
- Three GREEN attempts have failed.
- An external system is unreachable in a way that prevents validation.

## Output contract

```yaml
status: GREEN | SCOPE_ESCALATION | BLOCKED
mode: tdd
files_changed:
  - app/api/momentum.py
  - app/services/broadcast.py
verification:
  command: "uv run pytest tests/api/test_momentum.py -q"
  exit_code: 0
  excerpt: "5 passed in 0.42s"
criteria_results:
  - criterion: "Momentum updates broadcast within 200 ms"
    result: PASS
    evidence: "tests/api/test_momentum.py::test_broadcast_latency"
  - criterion: "Graceful degradation when WebSocket unavailable"
    result: PASS
    evidence: "tests/api/test_momentum.py::test_falls_back_to_polling"
regression:
  ran: "uv run pytest -q"
  exit_code: 0
  newly_failing: []
notes: "Refactored broadcast loop to async fan-out; no new deps."
```

## Anti-patterns

- "I refactored a related file while I was in there."
- Disabling or weakening a failing test to declare GREEN.
- Adding `try/except: pass` to silence an error rather than fixing it.
- Calling out to the network or installing a package without escalation.
- Reporting GREEN without re-running tests in the current dispatch.
