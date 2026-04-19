# GenerateAgents.md - Output Styles Summary

This document summarizes the two output styles available in [GenerateAgents.md](https://github.com/originalankur/GenerateAgents.md).

## Overview

GenerateAgents.md is a tool that automatically generates `AGENTS.md` files for any GitHub or local repository. It supports two distinct styles via the `--style` flag:

| Style         | Flag                                | Purpose                                               |
| ------------- | ----------------------------------- | ----------------------------------------------------- |
| Comprehensive | `--style comprehensive` (default) | Detailed guide with high-level architectural overview |
| Strict        | `--style strict`                  | Focused on constraints and anti-patterns only         |

## Comprehensive Style (Default)

**Purpose:** Build a detailed, expansive guide that gives a brand-new AI agent a complete tour of the repository.

### Output Sections

```markdown
# AGENTS.md — <repo-name>
## Project Overview
## Agent Persona
## Tech Stack
## Architecture
## Code Style
## Anti-Patterns & Restrictions
## Database & State Management
## Error Handling & Logging
## Testing Commands
## Testing Guidelines
## Security & Compliance
## Dependencies & Environment
## PR & Git Rules
## Documentation Standards
## Common Patterns
## Agent Workflow / SOP
## Few-Shot Examples
```

### Characteristics

- **High-level abstractions**: Extracts project architecture, directory mappings, data flow principles
- **Agent personas**: Defines how the AI should behave
- **Detailed explanations**: Includes rationale and context for decisions
- **Complete overview**: From tech stack to testing to documentation standards
- **Best for**: New developers or AI agents needing full context about the codebase

### Example (Flask)

The comprehensive Flask AGENTS.md includes:

- Python 3.9+ with Flask 2.3, SQLAlchemy 2.0, pytest
- Application Factory and Blueprint patterns
- `mypy --strict` typing requirements
- Detailed database connection lifecycle with context locals
- Extensive code style rules (120 char line length, naming conventions)

---

## Strict Style

**Purpose:** Give the agent *only* what it can't easily `grep` for itself - strict constraints, undocumented quirks, and things it must *never* do.

> Research suggests that broad, descriptive codebase summaries can sometimes distract LLMs and drive up token costs. The strict style combats this.

### Output Sections

```markdown
# AGENTS.md — <repo-name>
## Code Style & Strict Rules
## Anti-Patterns & Restrictions
## Security & Compliance
## Lessons Learned (Past Failures)
## Repository Quirks & Gotchas
## Execution Commands
```

### Characteristics

- **Minimal context**: Only constraints and rules, no high-level overview
- **Action-focused**: What the agent *must* and *must not* do
- **Token-efficient**: Smaller output, less distraction
- **Past failures**: Lessons learned from reverted commits (via `--analyze-git-history`)
- **Best for**: Experienced developers or scenarios requiring minimal token usage

### Example (Flask)

The strict Flask AGENTS.md includes:

- `ruff` linter rules (B, E, F, I, UP, W)
- Import style: one import per line (no `from x import a, b`)
- Never use `app.run()` in production
- Never wrap `app` directly for middleware (use `app.wsgi_app`)
- Context-local objects (`request`, `g`, `session`)

---

## Comparison

| Aspect                      | Comprehensive            | Strict                                |
| --------------------------- | ------------------------ | ------------------------------------- |
| **Length**            | ~400+ lines              | ~120 lines                            |
| **Focus**             | Full context             | Constraints only                      |
| **Architecture**      | Yes                      | No                                    |
| **Tech Stack**        | Detailed                 | Minimal                               |
| **SOP/Workflow**      | Yes                      | No                                    |
| **Few-Shot Examples** | Yes                      | No                                    |
| **Token Cost**        | Higher                   | Lower                                 |
| **Use Case**          | New projects/exploratory | Experienced developers/cost-sensitive |
