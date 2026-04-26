---
description: "Standalone test authoring: runs @pries-test to write failing tests for a feature without dispatching implementation."
agent: pries-test
subtask: true
return:
  # Step 1: Build the task package from the user's feature description.
  - /subtask {agent: pries-pm && as: test_only_task} Treat "$ARGUMENTS" as a feature description or pointer to a markdown spec. Build a task package: title, acceptance_criteria, code_context (grep relevant symbols), target test file path matching **/test_*.py or **/*_test.py.

  # Step 2: Write tests, validate RED.
  - /subtask {agent: pries-test && as: test_only_write} Using stdd-test-author-constrained, write failing tests for $RESULT[test_only_task]. Run pytest --collect-only baseline pre/post. Classify each failure. Emit TESTS_READY (with red_state) or NOT_TESTABLE (with @check sign-off requirement) or BLOCKED.

  # Step 3: Final summary.
  - "Test authoring complete. See the failure classification above. To implement, run /pries-implement against the issue or call @pries-make directly with the task package."
---
# PRIES Test Only: $ARGUMENTS

Standalone test-authoring workflow. Use to:

- Write failing tests before starting work (TDD discipline).
- Backfill missing tests for an existing feature.
- Verify a bug reproduction test before fixing.

`$ARGUMENTS` may be:

- A feature description ("Momentum sync over WebSocket").
- A path to a spec markdown file.
- An acceptance-criteria block.

## Output

- New test files in allowed patterns only (see `pries-test` agent).
- `red_state` list with classifications.
- `escalate_to_check` flag if mixed failure codes appear.

## Constraints

- Production code is not modified.
- Existing `conftest.py` is not modified (parallel safety).
- NOT_TESTABLE verdict requires @pries-check sign-off — the workflow
  will pause for adjudication.
