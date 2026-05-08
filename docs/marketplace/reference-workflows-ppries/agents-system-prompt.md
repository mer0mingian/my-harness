# System Prompt Sections for Multi-Agent Workflow

This configuration guide provides templates for two key system prompt sections:

## Git Workflow Section

The document recommends a development approach using feature branches and git worktrees, keeping the main branch protected. Key conventions include:

- Using a bare clone with worktrees structure
- Converting slashes to hyphens in worktree directory names (e.g., branch `user/foo` becomes directory `user-foo`)
- Following "Conventional Commits" standards for commit messages
- Running worktree commands from the repository root

## Multi-Agent Workflow Section

This section outlines when to engage multiple specialized agents:

**Trigger conditions:** Projects involving 3+ files, API/schema modifications, work exceeding 30 minutes, or issues spanning multiple concerns.

**Process flow:** The workflow follows these phases—Setup (involving project management and worktree creation), Planning (with conditional test design consideration), review checkpoints, task distribution to implementation agents, test-driven development cycle (RED→GREEN), and final reviews.

The guide references additional documentation at `~/.config/opencode/docs/multi-agent-workflow.md` for detailed task-splitting specifications, integration contracts, and format examples.
