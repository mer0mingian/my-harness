# Autonomous Multi-Agent Workflow for OpenCode — Complete Content

This document describes a fire-and-forget system that orchestrates multiple specialized AI agents to autonomously plan, test, implement, and submit code changes based on Linear issue IDs.

## Core Architecture

The system dispatches five purpose-built agents with constrained tool access:

- **`@check`** — Design reviewer using an 8-point risk framework (Assumptions, Failure Modes, Edge Cases, Compatibility, Security, Ops, Scale, Testability)
- **`@simplify`** — Complexity reviewer flagging overengineering and YAGNI violations
- **`@test`** — TDD test author writing failing tests before implementation
- **`@make`** — Task implementor with sandboxed bash access
- **`@pm`** — Linear CLI integration for issue management

## Key Workflow Phases

The `/workflow` command executes ten sequential phases: repo verification, issue fetching, git worktree creation, implementation planning, parallel review cycles (max 3 with convergence detection), task decomposition, test writing with failure classification, implementation with TDD validation, final review, and draft PR creation.

## Trust Model & Tool Access

Reviewers (`@check`, `@simplify`) have read-only access. The test author (`@test`) writes only test files matching defined patterns. The implementor (`@make`) can edit code but cannot run git, pip, or curl. This separation prevents unintended modifications.

## TDD Integration

Tests must classify failures into four categories: MISSING_BEHAVIOR and ASSERTION_MISMATCH qualify as valid RED; TEST_BROKEN and ENV_BROKEN require investigation. The implementor validates RED before proceeding to implementation.

## Adoption & Customization

Installation requires copying agent definitions to `~/.config/opencode/agents/`, installing the Linear CLI, configuring bash permissions globally, and customizing paths for your repository. Model selection, review cycles, branch naming, and test patterns are all configurable.

## Standalone Usage

Individual agents and the `/review` command work independently of the full workflow, enabling ad-hoc use cases like reviewing code without implementation context or writing tests before starting work.
