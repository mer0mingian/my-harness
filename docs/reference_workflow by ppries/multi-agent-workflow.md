# Multi-Agent Workflow Summary

This document outlines a structured approach for collaborative development using multiple specialized agents.

## Core Principle

"Use the multi-agent workflow when 3+ files need changes, API changes are involved, work exceeds 30 minutes, or cross-cutting concerns exist."

## Key Workflow Phases

The process involves seven sequential steps: establishing context via Linear, creating a detailed implementation plan, parallel reviews by check and simplify agents, breaking work into discrete tasks, test writing, implementation in TDD mode, and final reviews.

## Critical Decision Points

The workflow includes a decision table that determines whether tests should be written upfront and routes implementation accordingly. Tasks triggering public API changes, bug fixes, or business logic additions require test design sections.

## Task Splitting Requirements

Each task must specify: clear description, acceptance criteria, actual code snippets (not just paths), explicit file lists including new files marked "(create)", and test file locations. Integration contracts document API changes and task dependencies.

## Scope Boundaries

The multi-agent approach doesn't handle file renames, deletions, Git operations, Kubernetes deployments, or new dependencies without explicit approval. These remain with the main agent.

## Setup Prerequisites

Initial setup requires fetching task details from Linear, setting up a Git worktree (with "/" replaced by "-"), and changing to the new working directory before planning begins.
