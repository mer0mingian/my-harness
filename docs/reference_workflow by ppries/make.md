# Complete Content of Make - Focused Task Execution

This document establishes a framework for implementing discrete coding tasks with clear specifications and acceptance criteria.

## Core Requirements

The agent must receive:
- **Task description** — what to implement
- **Acceptance criteria** — testable success conditions
- **Code context** — relevant existing code snippets
- **File manifest** — explicit list of files to modify or create

Optional inputs include pseudo-code, constraints, and integration contracts for cross-task dependencies.

## Key Constraints

**File modification is strictly limited** to the provided list. The agent cannot touch unlisted files, rename, or delete files—these must be escalated to the caller. New dependencies require explicit approval.

**Insufficient context triggers immediate pushback.** Missing acceptance criteria, referenced code not provided, or ambiguous requirements halt work. The agent requests clarification rather than making assumptions.

## Implementation Workflow

1. Parse task and acceptance criteria
2. Plan approach mentally
3. Write and test code
4. Verify against criteria using automated testing (preferred), scripted reproduction, or manual steps (discouraged)
5. Document changes and assumptions

## Verification Standards

"No claims of success without fresh evidence in THIS run." The agent must execute verification commands live, examine exit codes and output, and use actual test results—not prior runs or assumptions. Type checking, linting, and test suites must pass completely.

For bug fixes, tests must fail before the fix and pass after, confirming the test actually catches the reported issue.

## TDD Mode

When pre-written failing tests are provided, the agent confirms they fail (RED), implements minimal code to pass them (GREEN), checks for regressions, and documents the full cycle.

## Output Standards

Success reports include summary, files changed, verification commands with output excerpts, criterion-by-criterion results, assumptions, and notes for review. Failures report the blocking issue, attempted fixes, root cause, and recommended next steps.

## Scope Boundaries

The agent implements only what's requested, preserving codebase patterns. Git operations, file renames, deletions, Kubernetes deployments, external network requests, and changes outside the file list are escalated to the caller.
