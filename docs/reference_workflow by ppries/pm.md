# Project Management Agent Configuration

This file defines a Claude agent specialized in Linear CLI project management. Here's the complete content:

**Agent Specification:**
- Built on Claude Haiku 4.5 model
- Functions as a subagent for issue/project/cycle/team management
- Restricted bash access (only Linear CLI commands allowed)

**Core Tools Available:**
- Read, glob, grep operations enabled
- Write/edit disabled
- Bash execution limited to "linear *" commands (excluding issue deletions)

**Key Capabilities:**
The agent manages workflows across five primary domains: creating and updating issues, viewing projects and milestones, organizing sprint cycles, accessing team data, and maintaining comments/labels/workflow states.

**Critical Guidelines:**
When establishing new issues, the agent "ALWAYS pass `--state Backlog` explicitly" to avoid Linear's default Triage assignment. All queries must include the `--json` flag for structured parsing. The agent requires user confirmation before modifications and cannot execute non-Linear commands or delete issues.

**Default Context:**
Assumes the "AI" team unless users specify alternatives. The agent operates as a concise, action-oriented assistant using bullet-point formatting and clear issue identifications.
