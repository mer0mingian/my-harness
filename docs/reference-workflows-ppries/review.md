# Code Review Orchestrator

This document defines a workflow for systematically reviewing code changes and architectural plans. Here's a concise summary:

## Core Process

The orchestrator follows four steps:

1. **Classify Input**: Determines whether the review targets uncommitted changes, a specific commit, branch, pull request, or a plan document.

2. **Gather Context**: Retrieves relevant diffs, full file contents, and project conventions (AGENTS.md, CONVENTIONS.md, .editorconfig).

3. **Dispatch Two Reviewers**: 
   - **@check** evaluates correctness, risks, and compliance
   - **@simplify** identifies unnecessary complexity
   - Both are mandatory for complete assessment

4. **Present Findings**: Reports results in a standardized format showing verdicts, issues, and verification steps.

## Key Principles

- Preserve each reviewer's native severity/priority scales without merging them
- Report only what agents actually found—no invented issues
- Include all relevant findings even if both agents flag the same area with different rationales
- Gate decision (merge approval) comes exclusively from @check
- Simplification recommendations are advisory only

The format ensures stakeholders see both technical correctness and design efficiency perspectives clearly separated.
