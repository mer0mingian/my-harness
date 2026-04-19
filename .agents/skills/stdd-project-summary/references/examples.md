# Project Summary Examples

## 1. Template
```markdown
# Project Summary: [Project Name]

## Vision & Goal
[One sentence summary of the primary purpose]

## Tech Stack
- **Backend**: [e.g., Python 3.13, FastAPI]
- **Frontend**: [e.g., Jinja2, Alpine.js]
- **Database**: [e.g., SQLite via SQLAlchemy]
- **Tooling**: [e.g., uv, ruff]

## Target Users
- [User Type 1]
- [User Type 2]

## Scale & Deployment
[Expected usage patterns and hosting environment]

## Core Constraints
- [Constraint 1]
- [Constraint 2]
```

## 2. Example: STA2E Minimal VTT
```markdown
# Project Summary: STA2E Minimal VTT

## Vision & Goal
A web-based Virtual Tabletop (VTT) designed to digitize the starship combat experience for Star Trek Adventures 2nd Edition sessions.

## Tech Stack
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Jinja2 Templates + Bootstrap + Alpine.js
- **Database**: SQLAlchemy 2.0 with aiosqlite
- **Tooling**: uv for dependency management, ruff for linting

## Target Users
- Game Masters (GMs) running starship combat.
- Players participating via their own devices.

## Scale & Deployment
- Designed for local or private server hosting.
- Handles small groups (1 GM, 4-6 Players).

## Core Constraints
- Surgical Changes: Minimal impact on upstream open-source compatibility.
- STA 2e Rules: Strict adherence to 2d20 mechanics.
```
